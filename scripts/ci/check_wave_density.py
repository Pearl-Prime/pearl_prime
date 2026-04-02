#!/usr/bin/env python3
"""
Wave Density Gate — Production Version

FAIL wave if:
- >=30% share same arc_id
- >=40% identical band sequence
- >=50% identical slot signature
- >=60% identical exercise placement
- Experience layer caps exceeded (when experience fields present; §5.1 of EXPERIENCE_LAYER_ANTI_SPAM_SPEC)

No prose inspection.
Structural + experience layer.
Requires plans to have: arc_id, emotional_temperature_sequence, slot_sig, exercise_chapters (Stage 3 emitted).
Experience fields are optional (graceful degrade).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from typing import Any, Dict, List, Tuple


REQUIRED_KEYS = ("arc_id", "emotional_temperature_sequence", "slot_sig", "exercise_chapters")


def load_plan(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def mode_share(values: List[str]) -> Tuple[float, str]:
    if not values:
        return 0.0, ""
    c = Counter(values)
    val, count = c.most_common(1)[0]
    return count / len(values), val


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Wave density gate: FAIL if >=30%% same arc, >=40%% same band_seq, >=50%% same slot_sig, >=60%% same exercise placement, or experience layer caps exceeded"
    )
    ap.add_argument("--plans-dir", required=True, help="Directory containing compiled plan JSON files (Stage 3 output with arc_id, emotional_temperature_sequence, slot_sig, exercise_chapters)")
    ap.add_argument("--network-mode", action="store_true", help="Run cross-brand network-level experience checks")
    ap.add_argument("--catalog-index", default="", help="Path to catalog similarity index.jsonl (for first-of-kind alerts)")
    args = ap.parse_args()

    plans: List[Dict[str, Any]] = []
    for fn in sorted(os.listdir(args.plans_dir)):
        if fn.endswith(".json"):
            path = os.path.join(args.plans_dir, fn)
            plan = load_plan(path)
            for k in REQUIRED_KEYS:
                if k not in plan:
                    print(f"WAVE DENSITY: Plan missing required key '{k}': {path}", file=sys.stderr)
                    return 1
            plans.append(plan)

    if len(plans) < 2:
        print("WAVE DENSITY: PASS (too few plans)")
        return 0

    arcs: List[str] = []
    bands: List[str] = []
    slots: List[str] = []
    exercises: List[str] = []

    for p in plans:
        arcs.append(str(p["arc_id"]))
        bands.append("-".join(map(str, p["emotional_temperature_sequence"])))
        slots.append(str(p["slot_sig"]))
        exercises.append(",".join(map(str, p["exercise_chapters"])))

    # V4.7 Angle Integration: fail if >=50% of plans share same angle_id (count only non-null angle_id)
    angle_ids: List[str] = [str(p.get("angle_id") or "").strip() for p in plans]
    angle_ids_non_null = [a for a in angle_ids if a]

    failures: List[str] = []

    arc_share, _ = mode_share(arcs)
    if arc_share >= 0.30:
        failures.append(f"arc_id density {arc_share:.0%} >= 30%")

    band_share, _ = mode_share(bands)
    if band_share >= 0.40:
        failures.append(f"band sequence density {band_share:.0%} >= 40%")

    slot_share, _ = mode_share(slots)
    if slot_share >= 0.50:
        failures.append(f"slot signature density {slot_share:.0%} >= 50%")

    ex_share, _ = mode_share(exercises)
    if ex_share >= 0.60:
        failures.append(f"exercise placement density {ex_share:.0%} >= 60%")

    # DEV SPEC 3: emotional role signature diversity
    role_sigs: List[str] = [str(p.get("emotional_role_sig") or "") for p in plans]
    if role_sigs:
        role_share, _ = mode_share(role_sigs)
        if role_share >= 0.40:
            failures.append(f"emotional_role_sig density {role_share:.0%} >= 40%")

    if len(angle_ids_non_null) >= 2:
        angle_share, _ = mode_share(angle_ids_non_null)
        if angle_share >= 0.50:
            failures.append(f"angle_id density {angle_share:.0%} >= 50% (count non-null only)")

    # DEV SPEC 2: compression structure diversity (only when plans use compression)
    compression_pos: List[str] = []
    compression_len: List[str] = []
    for p in plans:
        compression_pos.append(str(p.get("compression_pos_sig") or ""))
        compression_len.append(",".join(str(x) for x in (p.get("compression_len_vec") or [])))
    has_compression = any(compression_pos)
    if has_compression and compression_pos and compression_len:
        pos_share, _ = mode_share(compression_pos)
        len_share, _ = mode_share(compression_len)
        if pos_share >= 0.50 and len_share >= 0.50:
            failures.append(
                f"compression structure density: pos_sig {pos_share:.0%} and len_vec {len_share:.0%} both >= 50%"
            )

    # --- Experience layer checks (§5.1 of EXPERIENCE_LAYER_ANTI_SPAM_SPEC) ---
    exp_failures: List[str] = []
    exp_warnings: List[str] = []
    try:
        # Import from phoenix_v4 package (add repo root to path if needed)
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        if repo_root not in sys.path:
            sys.path.insert(0, repo_root)
        from phoenix_v4.qa.experience_wave_checks import (
            check_experience_wave,
            check_experience_metadata_consistency,
        )
        from pathlib import Path

        catalog_index = Path(args.catalog_index) if args.catalog_index else None
        exp_failures, exp_warnings = check_experience_wave(
            plans,
            allow_legacy_plans=True,
            network_mode=args.network_mode,
            catalog_index_path=catalog_index,
        )

        # Experience-metadata consistency (WARN only)
        consistency_warnings = check_experience_metadata_consistency(plans)
        exp_warnings.extend(consistency_warnings)

    except ImportError:
        # phoenix_v4 not importable (e.g. CI without full env); skip experience checks gracefully
        exp_warnings.append("EXP WAVE: phoenix_v4.qa.experience_wave_checks not importable; experience checks skipped")
    except Exception as e:
        exp_warnings.append(f"EXP WAVE: experience check error (non-blocking): {e}")

    failures.extend(exp_failures)

    if failures:
        print("WAVE DENSITY: FAIL")
        for f in failures:
            print(" -", f)
        if exp_warnings:
            print("WAVE DENSITY: WARNINGS")
            for w in exp_warnings:
                print(" -", w)
        return 2

    if exp_warnings:
        print("WAVE DENSITY: WARNINGS")
        for w in exp_warnings:
            print(" -", w)

    print("WAVE DENSITY: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
