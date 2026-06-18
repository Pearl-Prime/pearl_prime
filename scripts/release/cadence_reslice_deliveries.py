#!/usr/bin/env python3
"""Re-slice an over-stuffed weekly_packages platform folder into a cadenced, cap-legal ramp.

WHY THIS EXISTS
---------------
A brand's rendered books can land all in ONE week folder (e.g. all 80 Devotion /
Open Vessel Press EPUBs dumped into
artifacts/weekly_packages/devotion_path/2026-W25/amazon_kdp/). The delivery feed
builder (scripts/onboarding/gen_brand_deliveries.py) then mirrors that single
week verbatim, so the Brand Director dashboard shows ~80 books for one week —
which violates the per-platform-per-week caps in
config/release_velocity/safe_velocity.yaml and the new-brand ramp in
config/release_velocity/velocity_ramp.yaml.

This script enforces the SSOT cadence: it reads the platform cap_max from
safe_velocity.yaml (via the same resolution generate_weekly_schedule.py uses),
builds a monotonic new-imprint ramp (1-2/wk early -> grow -> hold at cap_max)
onto CONSECUTIVE ISO weeks starting at the current/given week, and physically
moves the files into per-week folders. Every week's count is hard-capped at
cap_max; the script FAILS if it ever would exceed it.

It is deterministic: files are slotted in sorted (topic/persona) order, so the
same input always produces the same per-week layout.

CADENCE SOURCE
--------------
- Cap:   config/release_velocity/safe_velocity.yaml  (lane platform -> trust tier -> per_week[max])
- Lanes: config/release_velocity/lanes.yaml          (en -> google_play_books; etc.)
- Ramp:  config/release_velocity/velocity_ramp.yaml  (phase_1 "1-2/wk early -> ~5-10/wk by day 90")

Usage:
  # EN lane (Google Play new_imprint cap = 20/wk), Devotion amazon_kdp folder:
  python3 scripts/release/cadence_reslice_deliveries.py \
      --brand-dir artifacts/weekly_packages/devotion_path \
      --from-week 2026-W25 --platform amazon_kdp --lane en

  # Dry-run (print the plan, move nothing):
  python3 scripts/release/cadence_reslice_deliveries.py ... --dry-run
"""
from __future__ import annotations

import argparse
import shutil
import sys
from datetime import date, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_SAFE_VELOCITY = REPO_ROOT / "config" / "release_velocity" / "safe_velocity.yaml"
CONFIG_LANES = REPO_ROOT / "config" / "release_velocity" / "lanes.yaml"

# Same content set the delivery feed publishes (gen_brand_deliveries.CONTENT_EXT).
CONTENT_EXT = {".epub", ".pdf", ".mp3", ".m4b", ".png", ".cue", ".md"}


def _load_yaml(p: Path) -> dict:
    if not p.exists():
        return {}
    try:
        import yaml
        return yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def lane_platforms(lane: str | None) -> list[str] | None:
    """Resolve a lane name to its platform list (config/release_velocity/lanes.yaml)."""
    if not lane:
        return None
    cfg = _load_yaml(CONFIG_LANES)
    lane_cfg = (cfg.get("lanes") or {}).get(lane) or {}
    return lane_cfg.get("platforms") or None


def resolve_cap_max(lane: str | None) -> int:
    """Effective per-week cap_max = min over the lane's platforms of new-tier per_week[max].

    Mirrors generate_weekly_schedule.py._get_platform_caps so the cadence here and
    the scheduler agree. Default (no lane) uses safe_velocity's global validation list.
    """
    safe = _load_yaml(CONFIG_SAFE_VELOCITY)
    platforms = lane_platforms(lane) or (
        safe.get("platforms_for_schedule_validation")
        or ["google_play_books", "findaway_voices", "ximalaya"]
    )
    trust_tier = safe.get("default_trust_tier_for_scheduling") or "new_imprint"
    tier_keys = (safe.get("trust_tier_platform_key") or {}).get(trust_tier, {}).copy()
    tier_keys.setdefault("google_play_books", "new_imprint")
    tier_keys.setdefault("findaway_voices", "new_account")
    tier_keys.setdefault("ximalaya", "verified_account")

    cap = None
    for plat in platforms:
        key = tier_keys.get(plat)
        if not key:
            continue
        per_week = ((safe.get(plat) or {}).get(key) or {}).get("per_week") or [0, 999999]
        cmax = int(per_week[1])
        cap = cmax if cap is None else min(cap, cmax)
    if cap is None:
        raise SystemExit(f"Could not resolve a per-week cap for lane={lane!r}; check safe_velocity.yaml")
    return cap


def ramp_counts(total: int, cap_max: int) -> list[int]:
    """Monotonic new-imprint ramp covering `total` items, every week <= cap_max.

    Honors velocity_ramp.yaml phase_1: "1-2/wk early -> ~5-10/wk by day 90 (~13 wks)",
    then climb to cap_max and hold until the backlog drains. Deterministic.
    """
    if total <= 0:
        return []
    # Slow new-imprint start, then build toward cap_max. Clamp each step to cap_max.
    ladder = [2, 2, 3, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16, 18, 20]
    counts: list[int] = []
    remaining = total
    for step in ladder:
        if remaining <= 0:
            break
        c = min(step, cap_max, remaining)
        counts.append(c)
        remaining -= c
    while remaining > 0:  # drain any tail at cap_max
        c = min(cap_max, remaining)
        counts.append(c)
        remaining -= c
    assert sum(counts) == total, (sum(counts), total)
    assert all(c <= cap_max for c in counts), counts
    return counts


def iso_week_label(d: date) -> str:
    iso = d.isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


def monday_of_iso_week(label: str) -> date:
    """'2026-W25' -> Monday date of that ISO week."""
    year_s, wk_s = label.split("-W")
    return date.fromisocalendar(int(year_s), int(wk_s), 1)


def collect_content_files(folder: Path) -> list[Path]:
    """Sorted real content files in `folder` (deterministic slot order)."""
    if not folder.is_dir():
        return []
    files = [
        f for f in folder.iterdir()
        if f.is_file()
        and f.suffix.lower() in CONTENT_EXT
        and f.name != "README.txt"
    ]
    return sorted(files, key=lambda p: p.name)


def plan_reslice(files: list[Path], from_week: str, cap_max: int) -> list[tuple[str, list[Path]]]:
    """Return [(iso_week_label, [files...]), ...] on consecutive ISO weeks from `from_week`."""
    counts = ramp_counts(len(files), cap_max)
    start_monday = monday_of_iso_week(from_week)
    plan: list[tuple[str, list[Path]]] = []
    idx = 0
    for i, c in enumerate(counts):
        wk = iso_week_label(start_monday + timedelta(days=7 * i))
        plan.append((wk, files[idx:idx + c]))
        idx += c
    return plan


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--brand-dir", type=Path, required=True,
                    help="artifacts/weekly_packages/<brand> directory")
    ap.add_argument("--from-week", required=True, help="ISO week the files currently sit in, e.g. 2026-W25")
    ap.add_argument("--platform", default="amazon_kdp", help="platform subfolder (default amazon_kdp)")
    ap.add_argument("--lane", default="en", help="release lane for cap resolution (default en)")
    ap.add_argument("--dry-run", action="store_true", help="print the plan, move nothing")
    args = ap.parse_args()

    brand_dir = args.brand_dir if args.brand_dir.is_absolute() else REPO_ROOT / args.brand_dir
    src_folder = brand_dir / args.from_week / args.platform
    if not src_folder.is_dir():
        print(f"ERROR: source folder not found: {src_folder}", file=sys.stderr)
        return 1

    cap_max = resolve_cap_max(args.lane)
    files = collect_content_files(src_folder)
    if not files:
        print(f"No content files in {src_folder}; nothing to re-slice.")
        return 0

    plan = plan_reslice(files, args.from_week, cap_max)

    print(f"lane={args.lane}  cap_max={cap_max}/wk  files={len(files)}  weeks={len(plan)}")
    for wk, wk_files in plan:
        flag = "  <-- OVER CAP" if len(wk_files) > cap_max else ""
        print(f"  {wk}: {len(wk_files):>2} {args.platform}{flag}")
        if len(wk_files) > cap_max:
            print("ERROR: a week exceeds cap_max; aborting (this should be impossible).", file=sys.stderr)
            return 1

    if args.dry_run:
        print("(dry-run) no files moved.")
        return 0

    moved = 0
    for wk, wk_files in plan:
        if wk == args.from_week:
            continue  # files already in the from-week folder stay put
        dest_dir = brand_dir / wk / args.platform
        dest_dir.mkdir(parents=True, exist_ok=True)
        for f in wk_files:
            dest = dest_dir / f.name
            if dest.resolve() == f.resolve():
                continue
            shutil.move(str(f), str(dest))
            moved += 1

    # Verify the from-week folder now holds exactly the week-1 count.
    remaining = collect_content_files(src_folder)
    wk1_count = len(plan[0][1]) if plan else 0
    print(f"moved {moved} files; {args.from_week} now holds {len(remaining)} (expected {wk1_count}).")
    if len(remaining) != wk1_count:
        print("WARN: from-week residual count does not match plan; inspect manually.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
