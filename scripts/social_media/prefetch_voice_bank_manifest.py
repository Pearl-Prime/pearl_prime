#!/usr/bin/env python3
"""Bulk-download all status=ok voice-bank MP3s from R2 into the local mp3 tree.

Does not call CosyVoice. Fail-closed rows (status≠ok) are skipped.
"""
from __future__ import annotations

import argparse
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from scripts.social_media.voice_bank_lookup import (  # noqa: E402
    DEFAULT_MANIFEST,
    VoiceBankError,
    load_index,
)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    for env in ("R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY"):
        if not (os.environ.get(env) or "").strip():
            print(f"MISSING {env} — load Keychain first", file=sys.stderr)
            return 2

    bank = load_index(args.manifest, allow_r2_download=True)
    rows = []
    for aid, row in bank._by_id.items():
        if (row.get("status") or "") != "ok":
            continue
        rows.append(row)
    if args.limit:
        rows = rows[: args.limit]
    print(f"prefetch target ok_rows={len(rows)} workers={args.workers}", flush=True)

    ok = skip = fail = 0

    def one(row: dict) -> tuple[str, str]:
        local = bank.local_path_for_row(row)
        if local.is_file() and local.stat().st_size >= 10_000:
            return "skip", row.get("atom_id") or ""
        try:
            bank.ensure_local_mp3(row)
            return "ok", row.get("atom_id") or ""
        except Exception as e:  # noqa: BLE001
            return "fail", f"{row.get('atom_id')}: {type(e).__name__}: {e}"

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as ex:
        futs = [ex.submit(one, r) for r in rows]
        for i, fut in enumerate(as_completed(futs), 1):
            status, detail = fut.result()
            if status == "ok":
                ok += 1
            elif status == "skip":
                skip += 1
            else:
                fail += 1
                print(f"FAIL {detail}", flush=True)
            if i % 50 == 0 or i == len(futs):
                print(
                    f"progress {i}/{len(futs)} downloaded={ok} already={skip} fail={fail}",
                    flush=True,
                )

    print(f"DONE downloaded={ok} already={skip} fail={fail}", flush=True)
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
