#!/usr/bin/env python3
"""Fetch, verify, test and cross-build locally. Never connects to a Kindle."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / '.cache'
BUILD = ROOT / 'build'
LOCK = json.loads((ROOT / 'provenance/sources.json').read_text())


def digest(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def fetch(record, name):
    CACHE.mkdir(exist_ok=True)
    dest = CACHE / name
    if dest.exists():
        if dest.is_symlink() or digest(dest) != record['sha256']:
            raise RuntimeError(f'Invalid cached file: {dest}; remove it explicitly to retry')
        return dest
    temp = dest.with_suffix(dest.suffix + '.partial')
    request = urllib.request.Request(record['url'], headers={'User-Agent': 'kindle-j6-koreader-reproducer'})
    try:
        with urllib.request.urlopen(request, timeout=30) as response, temp.open('xb') as output:
            size = 0
            while block := response.read(1024 * 1024):
                size += len(block)
                if size > 200 * 1024 * 1024:
                    raise RuntimeError('Download exceeds the bounded size')
                output.write(block)
        if digest(temp) != record['sha256']:
            raise RuntimeError(f'Checksum mismatch: {name}')
        temp.replace(dest)
    finally:
        temp.unlink(missing_ok=True)
    return dest


def unpack(archive, destination, toolchain=False):
    """Allow only directories/files below the archive root; never follow links."""
    with tarfile.open(archive) as tar:
        for member in tar:
            parts = Path(member.name).parts
            if not parts or Path(member.name).is_absolute() or '..' in parts:
                raise RuntimeError('Unsafe archive path')
            if toolchain:
                if len(parts) < 3 or not (parts[1] in ('rustc', 'cargo') or parts[1].startswith('rust-std-')):
                    continue
                rel = Path(*parts[2:])
                if rel.parts[0] not in ('bin', 'lib', 'libexec', 'share'):
                    continue
            else:
                if len(parts) < 2:
                    continue
                rel = Path(*parts[1:])
            if not (member.isfile() or member.isdir()):
                raise RuntimeError(f'Archive link/special file rejected: {member.name}')
            target = destination / rel
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with tar.extractfile(member) as source, target.open('wb') as out:
                    shutil.copyfileobj(source, out)
                target.chmod(member.mode & 0o755)


def run(args, *, cwd, env=None, expected=0, log=None):
    result = subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True, timeout=900)
    if log:
        (BUILD / log).write_text(result.stdout + result.stderr)
    if result.returncode != expected:
        print((result.stdout + result.stderr)[-10000:])
        raise RuntimeError(f'Command failed ({result.returncode}, expected {expected}): {args}')
    return result.stdout + result.stderr


def prepare():
    if platform.system() != 'Linux' or platform.machine() != 'x86_64':
        raise RuntimeError('Reproduction targets an x86_64 Linux development host')
    BUILD.mkdir(exist_ok=True)
    toolchain = BUILD / 'toolchain'
    # Fresh managed outputs: refuse symlinked folders before removing generated content.
    for name in ('toolchain', 'source', 'baseline'):
        path = BUILD / name
        if path.is_symlink():
            raise RuntimeError(f'Refusing symlink: {path}')
        if path.exists():
            shutil.rmtree(path)
    for record in LOCK['toolchain']:
        archive = fetch(record, record['url'].rsplit('/', 1)[-1])
        unpack(archive, toolchain, toolchain=True)
    source = BUILD / 'source'
    unpack(fetch(LOCK['source'], 'mapper-source.tar.gz'), source)
    patch = ROOT / LOCK['patch']['path']
    if digest(patch) != LOCK['patch']['sha256']:
        raise RuntimeError('Public patch hash mismatch')
    # Isolate git-apply paths from the outer companion repository, including in CI.
    run(['git', 'init', '--quiet'], cwd=source)
    run(['git', 'apply', '--check', str(patch)], cwd=source)
    run(['git', 'apply', str(patch)], cwd=source)
    shutil.copytree(source, BUILD / 'baseline')
    # Keep added tests/fixtures, but restore the original production classification.
    main = BUILD / 'baseline/src/main.rs'
    text = main.read_text()
    fixed = 'direct || multitouch || (configured && touch_button && absolute_xy)'
    if text.count(fixed) != 1:
        raise RuntimeError('Unexpected classification helper')
    main.write_text(text.replace(fixed, 'direct || multitouch'))
    return source, toolchain


def environment(toolchain):
    env = dict(os.environ)
    # Do not inherit host compiler/linker overrides or a different toolchain sysroot.
    for key in list(env):
        if key.startswith(('RUST', 'CARGO_TARGET_', 'CARGO_ENCODED_')):
            del env[key]
    env.update({
        'PATH': str(toolchain / 'bin') + os.pathsep + env.get('PATH', ''),
        'RUSTC': str(toolchain / 'bin/rustc'),
        'RUSTDOC': str(toolchain / 'bin/rustdoc'),
        'CARGO_HOME': str(CACHE / 'cargo'),
        'CARGO_TARGET_DIR': str(BUILD / 'target'),
        'BUILD_SHA': LOCK['build_id'],
        'CARGO_INCREMENTAL': '0',
    })
    linker = toolchain / 'lib/rustlib/x86_64-unknown-linux-gnu/bin/rust-lld'
    if not linker.is_file():
        raise RuntimeError('Bundled rust-lld missing')
    env['CARGO_TARGET_ARMV7_UNKNOWN_LINUX_MUSLEABIHF_LINKER'] = str(linker)
    return env


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tests-only', action='store_true', help='Skip only the ARM release build')
    args = parser.parse_args()
    for directory in (CACHE, BUILD):
        if directory.is_symlink():
            raise RuntimeError(f'Refusing symlink: {directory}')
    source, toolchain = prepare()
    env = environment(toolchain)
    cargo = str(toolchain / 'bin/cargo')
    baseline_env = dict(env, CARGO_TARGET_DIR=str(BUILD / 'target-baseline'))
    baseline = run([cargo, 'test', '--locked'], cwd=BUILD / 'baseline', env=baseline_env,
                   expected=101, log='baseline-tests.log')
    if '42 passed; 3 failed' not in baseline:
        raise RuntimeError('Baseline did not fail precisely the three expected regressions')
    tests = run([cargo, 'test', '--locked'], cwd=source, env=env, log='patched-tests.log')
    if '45 passed; 0 failed' not in tests:
        raise RuntimeError('Expected all 45 patched tests')
    report = {'base_commit': LOCK['source']['commit'], 'public_patch_sha256': LOCK['patch']['sha256'],
              'baseline': '42 passed; 3 failed (expected)', 'patched': '45 passed; 0 failed',
              'rustc': run([env['RUSTC'], '--version'], cwd=source).strip(),
              'cargo': run([cargo, '--version'], cwd=source).strip(),
              'build_id': LOCK['build_id'], 'hardware_access': 'none'}
    if not args.tests_only:
        run([cargo, 'build', '--locked', '--release', '--target', LOCK['target']],
            cwd=source, env=env, log='arm-build.log')
        binary = BUILD / 'target' / LOCK['target'] / 'release/kindle-button-mapper'
        elf = run(['readelf', '-h', '-A', '-l', '-d', str(binary)], cwd=source, log='arm-elf.txt')
        if not all(x in elf for x in ('ELF32', 'ARM', 'hard-float ABI', 'VFPv3-D16')):
            raise RuntimeError('Unexpected ARM ABI/CPU attributes')
        if 'INTERP' in elf or '(NEEDED)' in elf:
            raise RuntimeError('Expected a static executable without a loader')
        if LOCK['build_id'].encode() not in binary.read_bytes():
            raise RuntimeError('Expected embedded build identity is missing')
        report.update(binary_sha256=digest(binary), binary_bytes=binary.stat().st_size,
                      target=LOCK['target'], static=True,
                      equals_historical_binary=digest(binary) == LOCK['historical_installed_binary']['sha256'])
    (BUILD / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
