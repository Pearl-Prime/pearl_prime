#!/usr/bin/env python3
"""
Flagship EXERCISE diversity gate (twelve-shape continuity plans).

Root cause this closes (2026-07-07 Layer-4 read): the gen_z_professionals x
anxiety plan assigned ch2-12's exercise_id as med_009, then med_015 through
med_024 — SEQUENTIAL ids from the SINGLE meditations_34 library, out of 311
exercises across 9 libraries. Nobody matched exercise to chapter; an author
just walked one file's id counter. That is the registry dup-fill anti-pattern
(fill by index, ignore purpose) recurring at the exercise layer — it produced
several contemplative/Buddhist-coded picks (Loving Kindness, Emptiness
Contemplation, Forgiveness Practice) in a secular gen-Z workplace book, one
of which (ch7's "Loving Kindness Expanding") tripped the secular-content
filter and silently lost two of its five composed layers with no gate
catching it (see check_flagship_exercise_five_layer.py).

This gate rejects a plan whose ch2+ exercise_ids either:
  1. all resolve to a single practice_library exercise_type ("all-one-library"), or
  2. contain a run of 3+ consecutive chapters whose ids are the same library's
     sequential index N, N+1, N+2, ... ("sequential-run"), or
  3. draw from fewer than MIN_LIBRARIES distinct exercise_type buckets across
     the whole plan.

Usage:
  python3 scripts/ci/check_flagship_exercise_diversity.py \\
      --plan config/source_of_truth/twelve_shape_chapter_plans/gen_z_professionals_anxiety.yaml
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

DEFAULT_PLAN = (
    REPO_ROOT
    / "config/source_of_truth/twelve_shape_chapter_plans/gen_z_professionals_anxiety.yaml"
)
MIN_LIBRARIES = 5
SEQUENTIAL_RUN_THRESHOLD = 3

# Trailing digits at the end of an id (e.g. "med_015" -> 15, "sens_008" -> 8).
# ab_tady ids (e.g. "cyclic_sighing") have no numeric suffix and never
# participate in the sequential-run check — only numbered-pool ids can walk
# an index sequentially.
_TRAILING_NUM_RE = re.compile(r"(\d+)$")


def _exercise_type_index(repo_root: Path) -> dict[str, str]:
    """id -> exercise_type, built from the same loader the pipeline uses."""
    from phoenix_v4.exercises.practice_library_loader import load_practice_library

    index: dict[str, str] = {}
    for ex_type, items in load_practice_library().items():
        for item in items:
            eid = item.get("id")
            if eid:
                index[str(eid)] = ex_type
    return index


def check(plan_path: Path) -> list[str]:
    import yaml

    plan = yaml.safe_load(plan_path.read_text(encoding="utf-8")) or {}
    chapters = plan.get("chapters") or []
    ex_type_of = _exercise_type_index(REPO_ROOT)

    # ch1 is golden-locked and exempt (content_only by design — see
    # check_flagship_contract.py). Diversity applies to the ch2+ picks.
    picks: list[tuple[int, str, str]] = []  # (chapter, exercise_id, exercise_type)
    for entry in chapters:
        ch_num = int(entry.get("chapter") or 0)
        eid = str(entry.get("exercise_id") or "").strip()
        if not ch_num or not eid or ch_num == 1:
            continue
        etype = ex_type_of.get(eid, "UNKNOWN")
        picks.append((ch_num, eid, etype))
    picks.sort()

    failures: list[str] = []

    distinct_types = {t for _, _, t in picks if t != "UNKNOWN"}
    if len(distinct_types) < MIN_LIBRARIES:
        failures.append(
            f"all-one-library: only {len(distinct_types)} distinct exercise_type(s) "
            f"across ch2+ ({sorted(distinct_types)}) — need >= {MIN_LIBRARIES}. "
            f"picks: {[(c, e) for c, e, _ in picks]}"
        )

    # Sequential-run: 3+ consecutive chapters whose ids are the SAME
    # exercise_type with strictly incrementing numeric suffixes.
    run_len = 1
    for i in range(1, len(picks)):
        _prev_ch, prev_id, prev_type = picks[i - 1]
        _ch, eid, etype = picks[i]
        prev_m = _TRAILING_NUM_RE.search(prev_id)
        cur_m = _TRAILING_NUM_RE.search(eid)
        same_sequential = (
            etype == prev_type
            and prev_m is not None
            and cur_m is not None
            and int(cur_m.group(1)) == int(prev_m.group(1)) + 1
        )
        if same_sequential:
            run_len += 1
        else:
            run_len = 1
        if run_len >= SEQUENTIAL_RUN_THRESHOLD:
            start_ch = picks[i - run_len + 1][0]
            failures.append(
                f"sequential-run: chapters {start_ch}-{_ch} all draw consecutive "
                f"{etype} ids ({picks[i - run_len + 1][1]} .. {eid}) — "
                f"pick by chapter mechanism, not by walking the id counter"
            )
            run_len = 1  # report each run once, then keep scanning

    unknown = [(c, e) for c, e, t in picks if t == "UNKNOWN"]
    if unknown:
        failures.append(f"unresolvable exercise_id(s) (not in any loaded library): {unknown}")

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    args = parser.parse_args()

    failures = check(args.plan)
    if failures:
        print("❌ FLAGSHIP EXERCISE DIVERSITY GATE — FAILED", file=sys.stderr)
        for f in failures:
            print(f"   ✗ {f}", file=sys.stderr)
        return 1
    print("✅ FLAGSHIP EXERCISE DIVERSITY GATE — ch2+ picks span >= "
          f"{MIN_LIBRARIES} libraries, no sequential-run pattern")
    return 0


if __name__ == "__main__":
    sys.exit(main())
