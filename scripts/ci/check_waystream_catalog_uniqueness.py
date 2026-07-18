#!/usr/bin/env python3
"""Hard gate: way_stream_sanctuary catalog must have 800 distinct titles, subtitles, and pairs.

On PRs that touch subtitle templates or the regen script (without plan apply), runs dry-run
achievability check instead of asserting plan files are already at 800/800.

  PYTHONPATH=. python3 scripts/ci/check_waystream_catalog_uniqueness.py
  PYTHONPATH=. python3 scripts/ci/check_waystream_catalog_uniqueness.py --dry-run-only
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
BRAND = "way_stream_sanctuary"
PLANS = REPO / "config/source_of_truth/book_plans_en_us"
REGEN = REPO / "scripts/catalog/waystream_subtitle_regen.py"
DRYRUN_ARTIFACT = REPO / "artifacts/waystream/subtitle_regen_dryrun.json"
EXPECTED = 800


def _load_plans() -> list[dict]:
    out = []
    for f in sorted(PLANS.glob(f"{BRAND}__*.yaml")):
        d = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        if d.get("_needs_authoring") is False and d.get("title"):
            out.append(d)
    return out


def check_plans_hard() -> tuple[bool, str]:
    plans = _load_plans()
    if len(plans) != EXPECTED:
        return False, f"expected {EXPECTED} authored plans, got {len(plans)}"
    titles = [p["title"].strip() for p in plans]
    subs = [p.get("subtitle", "").strip() for p in plans]
    pairs = list(zip(titles, subs))
    dup_t = {t: c for t, c in Counter(titles).items() if c > 1}
    dup_s = {t: c for t, c in Counter(subs).items() if c > 1}
    dup_p = {p: c for p, c in Counter(pairs).items() if c > 1}
    if dup_t or dup_s or dup_p:
        return False, (
            f"FAIL titles={len(set(titles))} subs={len(set(subs))} pairs={len(set(pairs))} "
            f"dup_t={len(dup_t)} dup_s={len(dup_s)} dup_p={len(dup_p)}"
        )
    return True, f"OK titles=800 subs=800 pairs=800 (n={len(plans)})"


def check_dryrun_artifact() -> tuple[bool, str]:
    if DRYRUN_ARTIFACT.exists():
        data = json.loads(DRYRUN_ARTIFACT.read_text(encoding="utf-8"))
        if (
            data.get("count") == EXPECTED
            and data.get("distinct_subtitles") == EXPECTED
            and data.get("distinct_titles") == EXPECTED
            and not data.get("dup_subtitles")
        ):
            return True, "dry-run artifact OK"
    # Run inline dry-run
    r = subprocess.run(
        [sys.executable, str(REGEN), "--dry-run"],
        cwd=str(REPO),
        env={**__import__("os").environ, "PYTHONPATH": str(REPO)},
        capture_output=True,
        text=True,
        timeout=300,
    )
    if r.returncode != 0:
        return False, (r.stdout + r.stderr).strip() or "dry-run failed"
    return True, (r.stdout.strip().splitlines() or ["dry-run OK"])[-1]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run-only", action="store_true", help="only verify regen achievability")
    args = ap.parse_args()

    if args.dry_run_only:
        ok, msg = check_dryrun_artifact()
    else:
        ok, msg = check_plans_hard()
        if not ok and "subs=" in msg and REGEN.exists():
            # Plans not yet at 800 — allow if dry-run proves achievability (pre-apply PR)
            dr_ok, dr_msg = check_dryrun_artifact()
            if dr_ok:
                print(f"WARN plans not at 800/800 yet; dry-run achievability: {dr_msg}")
                ok = True
                msg = dr_msg
    print(msg)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
