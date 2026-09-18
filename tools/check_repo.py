#!/usr/bin/env python3
"""Check the publication allowlist, local documentation links and source hygiene."""
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_MACS = {'02:00:00:00:00:06', '02:00:00:00:00:01',
                '00:00:00:00:00:00', 'ff:ff:ff:ff:ff:ff'}


def main():
    names = (ROOT / 'PUBLIC_FILES.txt').read_text().splitlines()
    if not names or names != sorted(set(names)):
        raise RuntimeError('PUBLIC_FILES.txt must be a sorted, unique, explicit allowlist')
    for name in names:
        path = Path(name)
        if path.is_absolute() or '..' in path.parts:
            raise RuntimeError('Allowlist paths must stay inside the repository')
        full = ROOT / path
        if any(p.is_symlink() for p in (full, *full.parents)):
            raise RuntimeError(f'Symlinked publication file: {name}')
        data = full.read_bytes()
        if len(data) > 200_000 or b'\0' in data:
            raise RuntimeError(f'Unexpected binary or large file: {name}')
        text = data.decode('utf-8')
        private_patterns = (
            r'-----BEGIN [A-Z ]*PRIVATE KEY-----',
            r'\bgh[pousr]_[A-Za-z0-9]{20,}',
            r'\bgithub_pat_[A-Za-z0-9_]{20,}',
            '/' + r'home/[^/\s]+/',
            '/' + r'Users/[^/\s]+/',
            r'\bssh-(?:ed25519|rsa)\s+AAAA[A-Za-z0-9+/]{30,}',
        )
        if any(re.search(pattern, text) for pattern in private_patterns):
            raise RuntimeError(f'Potential private content: {name}')
        macs = re.findall(r'(?i)\b(?:[0-9a-f]{2}:){5}[0-9a-f]{2}\b', text)
        if any(mac.lower() not in ALLOWED_MACS for mac in macs):
            raise RuntimeError(f'Non-example Bluetooth identity: {name}')
        if path.suffix == '.py':
            ast.parse(text, filename=name)
        elif path.suffix == '.sh':
            subprocess.run(['sh', '-n', str(full)], check=True, timeout=10)
        elif path.suffix == '.json':
            json.loads(text)
        elif path.suffix == '.md':
            for target in re.findall(r'\]\(([^\s)]+)\)', text):
                url = urlsplit(target)
                if url.scheme or target.startswith('#'):
                    continue
                resolved = (full.parent / unquote(url.path)).resolve()
                if not resolved.is_relative_to(ROOT) or not resolved.is_file():
                    raise RuntimeError(f'Broken local link in {name}: {target}')
                if resolved.relative_to(ROOT).as_posix() not in names:
                    raise RuntimeError(f'Link to unpublished file in {name}: {target}')

    pins = json.loads((ROOT / 'provenance/sources.json').read_text())
    patch = ROOT / pins['patch']['path']
    if hashlib.sha256(patch.read_bytes()).hexdigest() != pins['patch']['sha256']:
        raise RuntimeError('Public patch does not match its recorded hash')
    evidence = json.loads((ROOT / 'provenance/public-verification.json').read_text())
    if evidence['base_commit'] != pins['source']['commit'] or evidence['public_patch_sha256'] != pins['patch']['sha256']:
        raise RuntimeError('Verification snapshot refers to a different source/patch')

    # Check the index only when this directory is itself a Git repository. Never
    # traverse an unrelated parent repository or stage files automatically.
    if (ROOT / '.git').exists():
        tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
        tracked = set(filter(None, tracked))
        if tracked != set(names):
            raise RuntimeError(f'Index differs from allowlist; extra={sorted(tracked-set(names))}, missing={sorted(set(names)-tracked)}')
    print(f'PASS: {len(names)} allowlisted text files, source hashes, syntax and local links')
    print('This check supplements manual staged-content and history review; it is not a secrets guarantee.')


if __name__ == '__main__':
    main()
