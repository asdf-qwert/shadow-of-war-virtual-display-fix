#!/usr/bin/env python3
"""One-byte Shadow of War VRAM fix. Python 3.8+, Windows/Linux, no dependencies."""
import argparse
import hashlib
from pathlib import Path
import sys

ORIGINAL = 'ed0d95cabb033cd66aaa99d699374881846c3cb03ec345f1123d82d45e0bdaef'
PATCHED = 'a11034ff9eac3acd76f4ff0de622e2bade2d652f56e6b52c2d11a17b303a68f7'
OFFSET = 0x01cb42fa


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def get_state(data):
    digest = sha256(data)
    if digest == ORIGINAL:
        return 'Original'
    if digest == PATCHED:
        return 'Patched'
    raise ValueError('Unsupported EXE SHA-256: ' + digest)


def run_patch(exe):
    path = Path(exe)
    with path.open('r+b') as stream:
        original = stream.read()
        if get_state(original) == 'Patched':
            return 'Already patched.'
        backup = path.with_name(path.name + '.sow-vram-fix.original')
        try:
            with backup.open('xb') as saved:
                saved.write(original)
        except FileExistsError:
            pass
        if sha256(backup.read_bytes()) != ORIGINAL:
            raise ValueError('Backup differs from original; EXE was not changed.')
        try:
            stream.seek(OFFSET)
            if stream.write(b'\xe2') != 1:
                raise OSError('Incomplete write.')
            stream.flush()
            stream.seek(0)
            if sha256(stream.read()) != PATCHED:
                raise ValueError('Patched file verification failed.')
        except (OSError, ValueError):
            stream.seek(OFFSET)
            stream.write(original[OFFSET:OFFSET + 1])
            stream.flush()
            raise
    return 'Patched. Backup: ' + str(backup)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('exe', type=Path, help='Path to x64/ShadowOfWar.exe')
    args = parser.parse_args()
    try:
        print(run_patch(args.exe))
        return 0
    except (OSError, ValueError) as error:
        print('Error: ' + str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
