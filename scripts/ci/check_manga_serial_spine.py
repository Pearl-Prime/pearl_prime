#!/usr/bin/env python3
"""Serial spine adoption gate — adopted series must have spine + continuity on disk.

Blocks silent omission of serial metadata once a series is listed in
config/manga/serial_spines/_adopted_series.yaml.

Run:
    PYTHONPATH=. python3 scripts/ci/check_manga_serial_spine.py
    PYTHONPATH=. python3 scripts/ci/check_manga_serial_spine.py --prove ep_002 \\
        --series heart_balance_shojo__en_US__romance_josei_drama__series01

Exit: 0 pass; 1 violation.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from phoenix_v4.manga.serial.spine_loader import (  # noqa: E402
    audit_adopted_series,
    build_episode_architect_input,
    default_repo_root,
    is_series_adopted,
)


class SerialSpineError(Exception):
    """Raised when adopted serial spine requirements fail."""


def assert_adopted_serial_spines(repo_root: Path | None = None) -> None:
    root = repo_root or default_repo_root()
    rows = audit_adopted_series(root)
    failures = [r for r in rows if r.get("status") != "PASS"]
    if failures:
        msg = "; ".join(
            f"{r['series_id']}: {r['failure_reasons']}" for r in failures
        )
        raise SerialSpineError(f"serial spine gate failed ({len(failures)}): {msg}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Manga serial spine adoption gate")
    parser.add_argument("--repo-root", type=Path, default=None)
    parser.add_argument(
        "--prove",
        metavar="EPISODE",
        help="Emit deterministic architect input JSON (e.g. ep_002)",
    )
    parser.add_argument("--series", type=str, default=None, help="series_id for --prove")
    args = parser.parse_args(argv)
    root = args.repo_root or default_repo_root()

    if args.prove:
        sid = args.series
        if not sid:
            print("--series required with --prove", file=sys.stderr)
            return 1
        if not is_series_adopted(sid, root):
            print(f"series not in adopted registry: {sid}", file=sys.stderr)
            return 1
        ep = args.prove.strip().lower().replace("-", "_")
        if ep.startswith("ep"):
            ch_num = int(ep.replace("ep_", "").replace("ep", ""))
        else:
            ch_num = int(ep)
        payload = build_episode_architect_input(sid, chapter_number=ch_num, repo_root=root)
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    try:
        assert_adopted_serial_spines(root)
    except SerialSpineError as e:
        print(f"BLOCK: {e}", file=sys.stderr)
        return 1
    print(f"PASS: {len(audit_adopted_series(root))} adopted serial spines valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
