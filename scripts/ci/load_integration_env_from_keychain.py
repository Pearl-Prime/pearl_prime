#!/usr/bin/env python3
"""Emit shell `export VAR=...` lines for integration env vars found in macOS Keychain.

Uses the same env-var name list as ``check_integration_env.py``
(``scripts/ci/integration_env_registry.py``).

Typical use from repo root (zsh/bash):

    eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"

Only variables that exist in Keychain are emitted; missing accounts are skipped.
Use ``--verbose`` to print skip notices to stderr.

Keychain: generic password, service ``-s`` default ``phoenix-omega``, account ``-a`` = env var name.
"""

from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path

_CI_DIR = Path(__file__).resolve().parent
if str(_CI_DIR) not in sys.path:
    sys.path.insert(0, str(_CI_DIR))

from integration_env_registry import REGISTRY  # noqa: E402


def keychain_get(*, service: str, account: str) -> str | None:
    r = subprocess.run(
        ["security", "find-generic-password", "-s", service, "-a", account, "-w"],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        return None
    v = (r.stdout or "").strip()
    return v if v else None


def main() -> int:
    p = argparse.ArgumentParser(description="Load tracked env vars from macOS Keychain (stdout = shell exports).")
    p.add_argument(
        "--service",
        default="phoenix-omega",
        help="Keychain service name (-s), default phoenix-omega",
    )
    p.add_argument("--list", action="store_true", help="Print tracked env var names only (one per line)")
    p.add_argument("--count", action="store_true", help="Print number of unique tracked env var names")
    p.add_argument("--verbose", "-v", action="store_true", help="Stderr: note Keychain misses")
    args = p.parse_args()

    names = sorted({row[1] for row in REGISTRY})
    if args.count:
        print(len(names))
        return 0
    if args.list:
        for n in names:
            print(n)
        return 0

    for name in names:
        val = keychain_get(service=args.service, account=name)
        if val is not None:
            print(f"export {name}={shlex.quote(val)}")
        elif args.verbose:
            print(f"# skip: no Keychain item for {name} (service={args.service})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
