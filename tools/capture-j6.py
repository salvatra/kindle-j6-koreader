#!/usr/bin/python3
"""One bounded Arch capture using installed evtest; no pairing or configuration writes.

Run as the normal user in a terminal. sudo authentication stays in that terminal.
The privileged worker only identifies this J6, starts two evtest readers, emits their
output and stops them. The unprivileged parent alone saves the transcript.
"""
import argparse
import re
import hashlib
import json
import os
from pathlib import Path
import selectors
import signal
import stat
import subprocess
import sys
import time

REMOTE_ADDRESS = None
SYS_INPUT = Path("/sys/class/input")
DEV_INPUT = Path("/dev/input")
EXPECTED = {"Yiser-J6": "touch", "Yiser-J6 Consumer Control": "consumer"}
DURATION = 30.0
CUES = [(4, "LEFT 1"), (8, "LEFT 2"), (12, "LEFT 3"),
        (16, "RIGHT 1"), (20, "RIGHT 2"), (24, "RIGHT 3")]
OTHER_MODE = False
RESTORE_MODE = False
STOP_SIGNALS = (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)


def configure_profile(profile):
    global OTHER_MODE, RESTORE_MODE, DURATION, CUES
    OTHER_MODE = profile == '--other-mode'
    RESTORE_MODE = profile == '--restore-mode'
    if RESTORE_MODE:
        DURATION = 24.0
        CUES = [(4, 'MODE SWITCH'), (14, 'LEFT 1'), (18, 'RIGHT 1')]
    elif OTHER_MODE:
        DURATION = 40.0
        CUES = [(4, 'MODE SWITCH'), (14, 'LEFT 1'), (18, 'LEFT 2'), (22, 'LEFT 3'),
                (26, 'RIGHT 1'), (30, 'RIGHT 2'), (34, 'RIGHT 3')]
    else:
        DURATION = 30.0
        CUES = [(4, 'LEFT 1'), (8, 'LEFT 2'), (12, 'LEFT 3'),
                (16, 'RIGHT 1'), (20, 'RIGHT 2'), (24, 'RIGHT 3')]


def ignore_stop_signals():
    # tty/sudo/timeout may deliver more than one stop signal. Finish cleanup once;
    # the independent timeout can still enforce its SIGKILL deadline if necessary.
    for sig in STOP_SIGNALS:
        signal.signal(sig, signal.SIG_IGN)


def identify():
    if not Path('/etc/arch-release').is_file() or Path('/mnt/us').exists():
        raise RuntimeError('This capture is for the confirmed Arch host only.')
    found = []
    for event in sorted(SYS_INPUT.glob('event*')):
        dev = event / 'device'
        try:
            name = (dev / 'name').read_text().strip()
            uniq = (dev / 'uniq').read_text().strip().lower()
        except OSError:
            continue
        identity = hashlib.sha256(uniq.encode()).hexdigest()
        if uniq != REMOTE_ADDRESS:
            continue
        if name not in EXPECTED:
            raise RuntimeError('An additional J6 interface appeared; re-inventory first.')
        def read(relative):
            return (dev / relative).read_text().strip().lower()
        if (read('id/bustype'), read('id/vendor'), read('id/product')) != ('0005', '05ac', '0220'):
            raise RuntimeError('J6 Bluetooth identity mismatch.')
        role = EXPECTED[name]
        ev_mask = int(read('capabilities/ev'), 16)
        if ev_mask != {'touch': 0x0b, 'consumer': 0x13}[role]:
            raise RuntimeError('J6 interface capabilities changed; re-inventory first.')
        node = DEV_INPUT / event.name
        info = node.stat()
        if not stat.S_ISCHR(info.st_mode):
            raise RuntimeError('Input path is not a character device.')
        found.append({'node': str(node), 'name': name, 'role': role,
                      'identity_sha256': identity, 'rdev': info.st_rdev,
                      'sysfs': str(dev.resolve())})
    if len(found) != 2 or {x['role'] for x in found} != {'touch', 'consumer'}:
        raise RuntimeError('Both confirmed J6 interfaces must be connected. No capture started.')
    return found


def stop_children(children):
    for child in children:
        if child.poll() is None:
            try:
                child.terminate()
            except ProcessLookupError:
                pass
    for child in children:
        try:
            child.wait(timeout=1)
        except subprocess.TimeoutExpired:
            child.kill()
            child.wait(timeout=1)
        if child.stdout is not None:
            child.stdout.close()


def worker():
    if os.geteuid() != 0:
        raise RuntimeError('Worker requires the terminal-authenticated sudo invocation.')
    nodes = identify()
    children, ready, pending = [], set(), {}
    mux = selectors.DefaultSelector()
    started = None
    last_check = 0.0
    cue_index = 0
    total_bytes = 0
    stopping = False
    def interrupted(signum, frame):
        nonlocal stopping
        if stopping:
            return
        stopping = True
        ignore_stop_signals()
        raise KeyboardInterrupt
    for sig in STOP_SIGNALS:
        signal.signal(sig, interrupted)
    try:
        mode = ('one manual toggle requested during capture; verify LED afterward'
                if OTHER_MODE else 'unchanged; not verified')
        if RESTORE_MODE:
            mode = 'one toggle back toward E03 requested; restoration requires trace comparison'
        print('META: ' + json.dumps({'utc': time.time(), 'mode': mode, 'nodes': nodes}), flush=True)
        for node in nodes:
            # Fixed tools; nodes are discovered from exact identity/capabilities, never CLI node paths.
            child = subprocess.Popen(
                ['/usr/bin/stdbuf', '-oL', '-eL', '/usr/bin/evtest', '--grab', node['node']],
                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            children.append(child)
            mux.register(child.stdout, selectors.EVENT_READ, node)
            pending[node['role']] = b''
        ready_deadline = time.monotonic() + 5
        while True:
            now = time.monotonic()
            if any(child.poll() is not None for child in children):
                raise RuntimeError('An evtest reader stopped early; do not retry automatically.')
            if now - last_check >= 1:
                if identify() != nodes:
                    raise RuntimeError('J6 disconnected or its input identity changed.')
                last_check = now
            if started is None:
                if len(ready) == 2:
                    if identify() != nodes:
                        raise RuntimeError('J6 changed during capture startup.')
                    # The first cue is four seconds later, allowing failures to be drained.
                    started = now
                    print(f'STATUS: Both J6 readers started. Wait for the {len(CUES)} prompts.', flush=True)
                elif now >= ready_deadline:
                    raise RuntimeError('Readers did not become ready within five seconds.')
            else:
                elapsed = now - started
                if elapsed >= DURATION:
                    break
                if cue_index < len(CUES) and elapsed >= CUES[cue_index][0]:
                    label = CUES[cue_index][1]
                    instruction = ('hold ONLY small lower-right Button 2 for 3 seconds, then release. '
                                   'Observe the blue LED; do not toggle again.'
                                   if label == 'MODE SWITCH' else
                                   'press once briefly, then release.')
                    print(f'CUE: +{elapsed:.3f}s UTC={time.time():.3f} — '
                          f'{label}: {instruction}', flush=True)
                    cue_index += 1
            for key, _ in mux.select(timeout=0.2):
                data = os.read(key.fileobj.fileno(), 16384)
                if not data:
                    raise RuntimeError('J6 reader closed unexpectedly.')
                total_bytes += len(data)
                if total_bytes > 8 * 1024 * 1024:
                    raise RuntimeError('Capture output limit reached.')
                role = key.data['role']
                pending[role] += data
                while b'\n' in pending[role]:
                    raw, pending[role] = pending[role].split(b'\n', 1)
                    line = raw.decode('utf-8', errors='replace')
                    elapsed = time.monotonic() - started if started is not None else -1
                    print(f'TRACE: +{elapsed:.3f}s [{role}] {line}', flush=True)
                    low = line.lower()
                    if any(word in low for word in ('permission denied', 'device or resource busy',
                                                   'no such device', 'grabbed by another',
                                                   'could not grab', 'failed to grab')):
                        raise RuntimeError('Input access/grab failed; no further button prompts.')
                    if 'Testing ...' in line:
                        ready.add(role)
        print('STATUS: Capture interval complete.', flush=True)
    finally:
        stopping = True
        ignore_stop_signals()
        stop_children(children)
        mux.close()
        print('STATUS: Both evtest processes stopped; temporary input grabs released.', flush=True)


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--address', required=True, help='Bluetooth address of YOUR paired J6')
    parser.add_argument('--output-dir', type=Path,
                        default=Path(__file__).resolve().parents[1] / 'private' / 'captures')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--other-mode', action='store_true', help='Experimental: cue one mode change')
    group.add_argument('--restore-mode', action='store_true', help='Experimental: cue one change back')
    parser.add_argument('--worker', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if not re.fullmatch(r'[0-9a-fA-F]{2}(?::[0-9a-fA-F]{2}){5}', args.address):
        parser.error('--address must be one colon-separated Bluetooth address')
    if args.address.lower() in ('00:00:00:00:00:00', 'ff:ff:ff:ff:ff:ff'):
        parser.error('A real device address is required')
    args.address = args.address.lower()
    return args


def main():
    global REMOTE_ADDRESS
    args = parse_args(sys.argv[1:])
    REMOTE_ADDRESS = args.address
    worker_requested = args.worker
    profile_args = ['--other-mode'] if args.other_mode else (['--restore-mode'] if args.restore_mode else [])
    configure_profile(profile_args[0] if profile_args else '')
    if worker_requested:
        worker()
        return 0
    if os.geteuid() == 0 or not sys.stdin.isatty():
        raise RuntimeError('Run as your normal user in your own Arch terminal, without sudo in front.')
    nodes = identify()
    for tool in ('/usr/bin/evtest', '/usr/bin/stdbuf', '/usr/bin/timeout', '/usr/bin/sudo', '/usr/bin/python3'):
        if not os.access(tool, os.X_OK):
            raise RuntimeError('Required installed tool missing: ' + tool)
    print('J6 identified: ' + ', '.join(x['role'] + ' ' + x['node'] for x in nodes))
    if OTHER_MODE or RESTORE_MODE:
        print('Do NOT switch mode yet. The first cue will request one mode switch.')
        print('Button 2 is the small lower-right button below the directional ring, NOT RIGHT.')
        if RESTORE_MODE:
            print('Use only immediately after a recorded alternate-mode run, without an intervening power-off or mode switch.')
    else:
        print('Keep its current mode. Use only brief LEFT/RIGHT presses when prompted.')
    print(f'Both J6 interfaces will be captured for {DURATION:.0f} seconds; Ctrl+C stops early.')
    print('If you miss a cue or press late, continue and report it afterward.')
    subprocess.run(['/usr/bin/sudo', '-v'], check=True)
    input('Have the remote in hand, then press Enter to begin: ')
    if identify() != nodes:
        raise RuntimeError('J6 changed while waiting; re-identify before trying again.')
    logs = args.output_dir.expanduser().resolve()
    logs.mkdir(mode=0o700, parents=True, exist_ok=True)
    experiment = 'E06' if RESTORE_MODE else ('E05' if OTHER_MODE else 'E03')
    filename = logs / (experiment + time.strftime('-j6-%Y%m%dT%H%M%SZ', time.gmtime()) + f'-{os.getpid()}.txt')
    command = ['/usr/bin/sudo', '-n', '/usr/bin/timeout', '--signal=TERM', '--kill-after=2s',
               f'{int(DURATION) + 10}s', '/usr/bin/python3', '-I',
               str(Path(__file__).resolve()), '--worker']
    command.extend(['--address', REMOTE_ADDRESS])
    command.extend(profile_args)
    fd = os.open(filename, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as transcript:
        transcript.write('COMMAND: ' + json.dumps(command) + '\n')
        transcript.flush()
        child = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, text=True, bufsize=1)
        try:
            for line in child.stdout:
                transcript.write(line)
                transcript.flush()
                if line.startswith(('CUE:', 'STATUS:', 'ERROR:')):
                    print(('\a' if line.startswith('CUE:') else '') + line, end='', flush=True)
            code = child.wait()
        except KeyboardInterrupt:
            ignore_stop_signals()
            if child.poll() is None:
                try:
                    child.send_signal(signal.SIGTERM)
                except ProcessLookupError:
                    pass
            print('\nStopping. Waiting for the bounded worker to release input...')
            # The independent privileged timeout still caps all worker descendants.
            for line in child.stdout:
                transcript.write(line)
            code = child.wait(timeout=int(DURATION) + 15)
        transcript.write(f'EXIT: {code}\n')
    print('Capture saved locally:', filename)
    if code:
        print('Capture stopped with an error/interruption. Review the log; do not repeat automatically.')
    else:
        if RESTORE_MODE:
            print('Done. Record whether you followed the switch and both presses; report any deviations.')
            print('Leave the mode unchanged. Compare the trace with the original-mode recording before calling it restored.')
        elif OTHER_MODE:
            print('Done. Record whether the blue LED stayed on after switching, and any missed presses.')
            print('Leave the mode as it is until this trace is reviewed; no automatic restoration was done.')
        else:
            print('Done. Record whether you followed all six prompts; no log upload is needed.')
    return code


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        ignore_stop_signals()
        print('ERROR: Capture interrupted.', flush=True)
        raise SystemExit(130)
    except Exception as error:
        print('ERROR: ' + str(error), flush=True)
        raise SystemExit(1)
