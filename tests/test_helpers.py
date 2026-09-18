import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('capture', ROOT / 'tools/capture-j6.py')
capture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capture)


class CaptureTests(unittest.TestCase):
    def test_arguments_are_explicit_and_cannot_inject_a_command(self):
        args = capture.parse_args(['--address', '02:00:00:00:00:06', '--output-dir', 'private/example'])
        self.assertEqual(args.address, '02:00:00:00:00:06')
        for value in ('x;touch /tmp/unwanted', 'event1', '02:00:00:00:00:06/24', '00:00:00:00:00:00'):
            with self.subTest(value=value), patch('sys.stderr'), self.assertRaises(SystemExit):
                capture.parse_args(['--address', value])

    def test_unrelated_keyboard_never_becomes_capture_target(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def device(index, name, address, ev, vendor='05ac'):
                path = root / f'event{index}/device'
                for file, value in {'name': name, 'uniq': address, 'id/bustype': '0005',
                                    'id/vendor': vendor, 'id/product': '0220', 'capabilities/ev': ev}.items():
                    dest = path / file
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_text(value)
            device(8, 'Yiser-J6', '02:00:00:00:00:06', 'b')
            device(9, 'Yiser-J6 Consumer Control', '02:00:00:00:00:06', '13')
            device(1, 'Main keyboard', '02:00:00:00:00:01', '120013')
            original_is_file = Path.is_file
            def is_file(path):
                return str(path) == '/etc/arch-release' or original_is_file(path)
            with patch.object(capture, 'SYS_INPUT', root), patch.object(capture, 'DEV_INPUT', root), \
                 patch.object(capture, 'REMOTE_ADDRESS', '02:00:00:00:00:06'), \
                 patch.object(Path, 'is_file', is_file), patch.object(capture.stat, 'S_ISCHR', return_value=True):
                found = capture.identify()
                self.assertEqual([x['node'] for x in found], [str(root/'event8'), str(root/'event9')])
                (root/'event8/device/id/vendor').write_text('1234')
                with self.assertRaisesRegex(RuntimeError, 'identity mismatch'):
                    capture.identify()

    def test_partial_composite_device_refused(self):
        with patch.object(capture, 'SYS_INPUT') as root, patch.object(Path, 'is_file', return_value=True), \
             patch.object(Path, 'exists', return_value=False):
            root.glob.return_value = []
            with self.assertRaisesRegex(RuntimeError, 'Both confirmed'):
                capture.identify()

    def test_cleanup_terminates_and_bounds_unresponsive_child(self):
        child = Mock()
        child.poll.return_value = None
        child.wait.side_effect = [subprocess.TimeoutExpired('evtest', 1), 0]
        capture.stop_children([child])
        child.terminate.assert_called_once()
        child.kill.assert_called_once()
        self.assertEqual(child.wait.call_count, 2)
        child.stdout.close.assert_called_once()

    def test_worker_interruption_releases_started_readers(self):
        nodes = [{'node': '/never-opened-a', 'role': 'touch'}, {'node': '/never-opened-b', 'role': 'consumer'}]
        child = Mock()
        child.poll.return_value = None
        with patch.object(capture.os, 'geteuid', return_value=0), \
             patch.object(capture, 'identify', return_value=nodes), \
             patch.object(capture.subprocess, 'Popen', return_value=child), \
             patch.object(capture.selectors, 'DefaultSelector') as factory, \
             patch.object(capture, 'stop_children') as cleanup, patch.object(capture.signal, 'signal'), \
             patch('builtins.print'):
            factory.return_value.select.side_effect = KeyboardInterrupt
            with self.assertRaises(KeyboardInterrupt):
                capture.worker()
            cleanup.assert_called_once_with([child, child])
            factory.return_value.close.assert_called_once()

    def test_profiles_have_bounded_distinct_cues(self):
        for profile, duration, count in [('', 30, 6), ('--other-mode', 40, 7), ('--restore-mode', 24, 3)]:
            capture.configure_profile(profile)
            self.assertEqual((capture.DURATION, len(capture.CUES)), (duration, count))
            self.assertLess(max(t for t, _ in capture.CUES), duration)
        capture.configure_profile('')


class RecoveryConfigTests(unittest.TestCase):
    def check(self, content):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory)/'client'
            file.write_text(content)
            return subprocess.run(['sh', str(ROOT/'recovery/recovery-sshctl.sh'), '--check-config', str(file)],
                                  capture_output=True, text=True, timeout=5)

    def test_private_single_addresses(self):
        for address in ('10.23.45.67', '172.16.4.8', '172.31.4.8', '192.168.42.9'):
            self.assertEqual(self.check(address+'\n').returncode, 0, address)

    def test_subnets_public_addresses_and_injection_rejected(self):
        for address in ('10.0.0.1/24', '8.8.8.8', '127.0.0.1', '172.32.0.1', '10.256.0.1',
                        '010.2.3.4', '10.2.3.4;id', '10.2.3.4\n10.2.3.5', '10.2.3.4 ', ''):
            self.assertNotEqual(self.check(address+'\n').returncode, 0, address)
        self.assertNotEqual(self.check('10.23.45.67').returncode, 0)

    def test_help_is_safe_on_development_host(self):
        result = subprocess.run(['sh', str(ROOT/'recovery/recovery-sshctl.sh'), '--help'],
                                capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 0)
        self.assertIn('--check-config', result.stdout)


class RecoveryLifecycleTests(unittest.TestCase):
    """Run copied controller against fake proc, firewall, server and signal functions."""
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.base = self.root/'recovery'
        self.base.mkdir()
        self.proc = self.root/'proc'
        self.proc.mkdir()
        self.bin = self.root/'bin'
        self.bin.mkdir()
        self.state = self.root/'rules.json'
        self.state.write_text('[]')
        self.pidfile = self.root/'pid'
        self.lock = self.root/'lock'
        self.signal_log = self.root/'signals'
        source = (ROOT/'recovery/recovery-sshctl.sh').read_text()
        source = source.replace('BASE=/mnt/us/kindle-remote-recovery', f'BASE={self.base}')
        source = source.replace('PIDFILE=/tmp/kindle_remote_recovery.pid', f'PIDFILE={self.pidfile}')
        source = source.replace('LOCK=/tmp/kindle_remote_recovery.lock', f'LOCK={self.lock}')
        source = source.replace('/proc/', str(self.proc)+'/')
        (self.base/'controller.sh').write_text(source)
        shutil.copyfile(ROOT/'recovery/config.sh', self.base/'config.sh')
        (self.base/'allowed_client_ipv4').write_text('10.23.45.67\n')
        (self.base/'settings/SSH').mkdir(parents=True)
        for name in ('authorized_keys', 'host_ed25519'):
            (self.base/'settings/SSH'/name).write_text('mock-only-not-a-key\n')
        (self.base/'dropbear').write_text('mock executable; never run\n')
        (self.base/'runtime.sha256').write_text('mock manifest; verifier stubbed\n')
        mock = '''#!/usr/bin/env python3
import json, os, sys, shutil
from pathlib import Path
kind=Path(sys.argv[0]).name; args=sys.argv[1:]; root=Path(os.environ['MOCK_ROOT'])
state=root/'rules.json'; rules=json.loads(state.read_text())
if kind=='id': print('0')
elif kind=='ifconfig': print('wlan0 inet addr:10.23.45.90 Bcast:10.23.45.255')
elif kind=='sleep': pass
elif kind=='sha256sum': sys.exit(0)
elif kind=='iptables':
 op=args[0]; rule=args[1:]
 if op=='-C': sys.exit(0 if rule in rules else 1)
 if op=='-I': rules.append(rule)
 elif op=='-D': rules.remove(rule)
 else: sys.exit(2)
 state.write_text(json.dumps(rules))
elif kind=='env':
 if os.environ.get('MOCK_START_FAIL'): sys.exit(1)
 pid='42424242'; (root/'pid').write_text(pid+'\\n'); p=root/'proc'/pid; p.mkdir()
 (p/'exe').symlink_to(root/'recovery/dropbear')
else: sys.exit(2)
'''
        for name in ('id', 'ifconfig', 'sleep', 'sha256sum', 'iptables', 'env'):
            f=self.bin/name; f.write_text(mock); f.chmod(0o755)
        # kill is a shell builtin: override it explicitly; never signal any real PID.
        self.driver = self.base/'driver.sh'
        self.driver.write_text(f'''#!/bin/sh
kill() {{
 printf '%s\\n' "$*" >> '{self.signal_log}'
 case "$1:$2" in '-TERM:42424242') rm '{self.proc}/42424242/exe'; rmdir '{self.proc}/42424242';; *) return 1;; esac
}}
. '{self.base}/controller.sh' "$@"
''')
        self.env = dict(os.environ, MOCK_ROOT=str(self.root), PATH=str(self.bin)+os.pathsep+os.environ['PATH'])

    def tearDown(self):
        self.temp.cleanup()

    def run_controller(self, action, **env):
        return subprocess.run(['sh', str(self.driver), action], env=dict(self.env, **env),
                              capture_output=True, text=True, timeout=8)

    def test_start_stop_preserves_unrelated_process_and_rules(self):
        unrelated=['INPUT', '-p', 'tcp', '--dport', '9999', '-j', 'ACCEPT']
        self.state.write_text(json.dumps([unrelated]))
        other=self.proc/'12345678'; other.mkdir(); (other/'exe').symlink_to('/unrelated/program')
        start=self.run_controller('start'); self.assertEqual(start.returncode, 0, start.stdout+start.stderr)
        rules=json.loads(self.state.read_text()); self.assertEqual(len(rules), 3)
        self.assertTrue(all('10.23.45.67' in r for r in rules if r != unrelated))
        repeat=self.run_controller('start'); self.assertEqual(repeat.returncode, 0)
        self.assertEqual(len(json.loads(self.state.read_text())), 3)
        stop=self.run_controller('stop'); self.assertEqual(stop.returncode, 0, stop.stdout+stop.stderr)
        self.assertEqual(json.loads(self.state.read_text()), [unrelated])
        self.assertTrue((other/'exe').is_symlink())
        self.assertEqual(self.signal_log.read_text().strip(), '-TERM 42424242')
        self.assertFalse(self.pidfile.exists()); self.assertFalse(self.lock.exists())

    def test_failed_start_removes_its_new_rules(self):
        result=self.run_controller('start', MOCK_START_FAIL='1')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(json.loads(self.state.read_text()), [])
        self.assertFalse(self.lock.exists())

    def test_invalid_config_creates_no_rules_or_process(self):
        (self.base/'allowed_client_ipv4').write_text('10.23.45.0/24\n')
        result=self.run_controller('start')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(json.loads(self.state.read_text()), [])
        self.assertFalse(self.pidfile.exists()); self.assertFalse(self.lock.exists())


if __name__ == '__main__':
    unittest.main()
