#!/usr/bin/env python3
"""Compare SDK interfaces with the message gitlink pinned by an audited motion ref."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], stderr=subprocess.PIPE)


def exports(cmake):
    return set(re.findall(r'"((?:msg|srv|action)/[^"\n]+\.(?:msg|srv|action))"', cmake))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--motion', required=True, type=Path)
    parser.add_argument('--messages', type=Path, help='default: MOTION/crb_ros_msg')
    parser.add_argument('--ref', default='origin/main')
    args = parser.parse_args()
    baseline = json.loads((ROOT / 'runtime-contract.json').read_text())
    try:
        revision = git(args.motion, 'rev-parse', args.ref).decode().strip()
        if revision != baseline['motion_commit']:
            raise ValueError(f'{args.ref}={revision}: runtime source changed; re-audit before claiming compatibility')
        tree = git(args.motion, 'ls-tree', revision, 'crb_ros_msg').decode().split()
        message_revision = tree[2]
        if message_revision != baseline['messages_commit']:
            raise ValueError('Message gitlink differs from the audited baseline')
        messages = args.messages or args.motion / 'crb_ros_msg'
        upstream_exports = exports(git(messages, 'show', f'{message_revision}:CMakeLists.txt').decode())
        if upstream_exports != set(baseline['interfaces']):
            raise ValueError('Upstream exported interface set changed')
        sdk_exports = exports((ROOT / 'crb_ros_msg/CMakeLists.txt').read_text())
        if sdk_exports != upstream_exports | set(baseline['sdk_extensions']):
            raise ValueError('SDK exported interface set differs from baseline plus documented extensions')
        for name in sorted(upstream_exports):
            expected = git(messages, 'show', f'{message_revision}:{name}')
            actual = (ROOT / 'crb_ros_msg' / name).read_bytes()
            if actual != expected or hashlib.sha256(expected).hexdigest() != baseline['interfaces'][name]:
                raise ValueError(f'Interface mismatch: {name}')
        print(f'PASS: {len(upstream_exports)} interfaces match pinned runtime; {len(baseline["sdk_extensions"])} documented SDK extensions')
        print(f'hl_motion={revision}; crb_ros_msg={message_revision}')
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(f'FAIL: {exc}')
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
