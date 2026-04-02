#!/usr/bin/env python3
"""
CDIS §13 — Duration QC gates (5 BLOCKER, 6 WARN, 2 INFO).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.duration._config import config_snapshot_hash, write_atomically  # noqa: E402


def run_qc(plan: dict, meta: dict, fail_mode_block: bool) -> dict:
    blockers: list[dict] = []
    warns: list[dict] = []
    infos: list[dict] = []

    fit = float(plan.get("duration_fit_score") or 0)
    fmt = plan.get("format") or meta.get("format") or ""
    unit = plan.get("registry_unit") or "seconds"
    val = float(plan.get("recommended_value") or 0)
    rsec = plan.get("recommended_duration_sec")
    micro = bool(plan.get("micro_dose_protocol"))
    intent = plan.get("intent") or meta.get("intent") or ""

    sec = float(rsec) if rsec is not None else (val if unit == "seconds" else val * 60 if unit == "minutes" else 0)

    # BLOCKER: zero duration
    if sec <= 0 and unit in ("seconds", "minutes") and not meta.get("page_count"):
        blockers.append({"id": "DURATION.ZERO", "level": "BLOCKER", "detail": "zero duration"})

    # BLOCKER: therapeutic min (stub: exercise video < 300s)
    if "video" in fmt and "exercise" in str(meta.get("subtype", "")).lower() and sec < 300:
        blockers.append({"id": "DURATION.EXERCISE_MINIMUM", "level": "BLOCKER", "detail": "exercise < 5 min"})

    if intent in ("therapeutic", "deep_engagement") and not micro and sec < 60 and "short" in fmt and meta.get("modality") == "breathing":
        blockers.append({"id": "DURATION.THERAPEUTIC_MINIMUM", "level": "BLOCKER", "detail": "below breathing floor"})

    # BLOCKER: platform max
    if not plan.get("platform_compliant", True):
        blockers.append({"id": "DURATION.PLATFORM_MAX", "level": "BLOCKER", "detail": "platform violation"})

    # BLOCKER: below platform min (if marked)
    if meta.get("below_platform_min"):
        blockers.append({"id": "DURATION.PLATFORM_MIN", "level": "BLOCKER", "detail": "below platform_min"})

    if fail_mode_block and fit < 0.45:
        blockers.append({"id": "DURATION.FIT_SCORE_FAIL", "level": "BLOCKER", "detail": f"fit={fit}"})

    # WARN
    if fit < 0.60:
        warns.append({"id": "DURATION.FIT_SCORE_LOW", "level": "WARN", "detail": str(fit)})
    if not plan.get("persona_budget_fit", True):
        warns.append({"id": "DURATION.PERSONA_BUDGET", "level": "WARN", "detail": "exceeds persona budget"})
    if meta.get("outside_sweet_spot"):
        warns.append({"id": "DURATION.PLATFORM_SWEET_SPOT", "level": "WARN"})
    if meta.get("breath_missing"):
        warns.append({"id": "DURATION.BREATH_MISSING", "level": "WARN"})
    if meta.get("chapter_mismatch"):
        warns.append({"id": "DURATION.CHAPTER_MISMATCH", "level": "WARN"})
    if micro and not meta.get("frequency_plan"):
        warns.append({"id": "DURATION.MICRO_DOSE_NO_FREQ", "level": "WARN"})
    if "stream" in fmt or "lofi" in str(meta.get("tags")):
        if sec < 1800:
            warns.append({"id": "DURATION.LOFI_MINIMUM", "level": "WARN", "detail": "stream < 30 min"})

    # INFO
    if meta.get("serialization_delta"):
        infos.append({"id": "DURATION.SERIALIZATION", "level": "INFO", "detail": meta["serialization_delta"]})
    infos.append({"id": "DURATION.AFTERGLOW", "level": "INFO", "detail": "residue 15-23 min stub"})

    passed = len([b for b in blockers if b.get("level") == "BLOCKER"]) == 0
    return {
        "passed": passed,
        "blockers": blockers,
        "warnings": warns,
        "infos": infos,
        "config_hash": config_snapshot_hash(),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="CDIS duration QC")
    ap.add_argument("duration_plan", help="duration_plan.json")
    ap.add_argument("--metadata", default=None, help="extra JSON metadata")
    ap.add_argument("--fail-mode-block", action="store_true", help="treat low fit as BLOCKER")
    ap.add_argument("-o", "--out", required=True)
    args = ap.parse_args()

    p = Path(args.duration_plan)
    if not p.exists():
        print(f"Error: not found {p}", file=sys.stderr)
        return 1
    plan = json.loads(p.read_text(encoding="utf-8"))
    meta = {}
    if args.metadata and Path(args.metadata).exists():
        meta = json.loads(Path(args.metadata).read_text(encoding="utf-8"))
    rep = run_qc(plan, meta, args.fail_mode_block)
    write_atomically(Path(args.out), rep)
    print(f"Wrote {args.out} passed={rep['passed']}")
    return 0 if rep["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
