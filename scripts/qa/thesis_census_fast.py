#!/usr/bin/env python3
"""Fast cross-cell thesis census via generate_book_plan (no full build_plan)."""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

TARGET_TOPICS = frozenset(
    {"burnout", "anxiety", "boundaries", "overthinking", "self_worth", "grief"}
)


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "").strip().lower())


def run_census(*, one_duration: bool = True) -> dict:
    import sys

    sys.path.insert(0, str(REPO))
    from phoenix_v4.planning.book_structure_plan import generate_book_plan
    from scripts.qa.plan_scale_qa_sweep import (
        _FULL_SPINE_CHAPTERS,
        effective_assembled_chapters,
        enumerate_cells,
    )

    seen: set[tuple[str, str]] = set()
    cells = []
    for c in enumerate_cells():
        if c["topic"] not in TARGET_TOPICS:
            continue
        key = (c["persona"], c["topic"])
        if one_duration and key in seen:
            continue
        seen.add(key)
        cells.append(c)

    thesis_to_cells: dict[str, set[str]] = defaultdict(set)
    thesis_to_topics: dict[str, set[str]] = defaultdict(set)

    for c in cells:
        eff = effective_assembled_chapters(c["duration"])
        plan = generate_book_plan(
            c["topic"], c["persona"], c["duration"], c["engine"], chapter_count=eff
        )
        cell = f"{c['persona']}×{c['topic']}"
        for ch in plan.chapters:
            t = getattr(ch, "chapter_thesis", None) or ""
            if not t:
                continue
            n = _norm(t)
            thesis_to_cells[n].add(cell)
            thesis_to_topics[n].add(c["topic"])

    cross = sorted(
        (
            {
                "thesis": t[:140],
                "cell_count": len(cs),
                "topic_count": len(thesis_to_topics[t]),
                "topics": sorted(thesis_to_topics[t]),
            }
            for t, cs in thesis_to_cells.items()
            if len(cs) >= 2
        ),
        key=lambda x: (-x["cell_count"], -x["topic_count"]),
    )
    multi_topic = [x for x in cross if x["topic_count"] >= 2]

    return {
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "mode": "generate_book_plan_only",
        "one_duration_per_persona_topic": one_duration,
        "cells_scored": len(cells),
        "unique_theses": len(thesis_to_cells),
        "cross_cell_repeated_count": len(cross),
        "multi_topic_repeated_count": len(multi_topic),
        "top_multi_topic_repeats": multi_topic[:20],
        "cross_cell_repeated_theses": cross[:30],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--all-durations", action="store_true")
    args = ap.parse_args()
    data = run_census(one_duration=not args.all_durations)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(
        f"multi_topic={data['multi_topic_repeated_count']} "
        f"cross_cell={data['cross_cell_repeated_count']} "
        f"unique={data['unique_theses']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
