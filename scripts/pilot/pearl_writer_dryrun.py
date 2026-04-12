#!/usr/bin/env python3
"""
Pearl_Writer dry-run pilot.

Reads the anxiety/standard_book budget.json, constructs synthetic section packets
for each slot, and calls expand_section(dry_run=True) to report how many sections
WOULD be expanded and the estimated word delta — without calling the LLM.

Usage:
    python3 scripts/pilot/pearl_writer_dryrun.py
    python3 scripts/pilot/pearl_writer_dryrun.py --topic anxiety --format standard_book
    python3 scripts/pilot/pearl_writer_dryrun.py --budget path/to/budget.json --out dir/
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.rendering.pearl_writer_expand import expand_section, should_expand


def _load_budget(budget_path: Path) -> dict:
    with open(budget_path) as f:
        return json.load(f)


def _make_packet(slot: dict, chapter_idx: int, slot_idx: int) -> dict:
    """Build a minimal synthetic section packet from a budget slot."""
    actual = int(slot.get("actual_words") or 0)
    target = int(slot.get("target_words") or 450)
    text = " ".join(["word"] * actual) if actual > 0 else ""
    return {
        "text": text,
        "word_count": actual,
        "target_words": target,
        "sources_used": [str(slot.get("source") or "enrichment")],
        "warnings": [],
        "section_type": str(slot.get("type") or "UNKNOWN"),
        "chapter_index": chapter_idx,
        "section_index": slot_idx,
    }


def run_dryrun(budget: dict, topic: str, format_: str) -> dict:
    spine_context = {
        "topic": topic,
        "persona_id": "general_adult",
        "teacher_id": "phoenix_standard",
        "engine": format_,
        "format": format_,
        "seed": f"dryrun:{topic}:{format_}",
    }

    chapters = budget.get("chapters") or []
    rows: list = []
    total_sections = 0
    would_expand = 0
    total_word_delta = 0

    for ch in chapters:
        ch_idx = int(ch.get("chapter") or 0)
        slots = ch.get("slots") or []
        for s_idx, slot in enumerate(slots):
            packet = _make_packet(slot, ch_idx, s_idx)
            total_sections += 1

            req = {
                "packet": packet,
                "spine_context": spine_context,
                "teacher_voice": "(dry-run: no voice reference loaded)",
                "seed": (
                    f"dryrun:{topic}:{format_}:expand:{ch_idx}:{s_idx}:expansion_v1"
                ),
            }
            result = expand_section(req, dry_run=True)

            dr = result.get("dry_run_report")
            if dr and dr.get("would_expand"):
                would_expand += 1
                delta = int(dr.get("words_to_add") or 0)
                total_word_delta += delta
                rows.append(
                    {
                        "chapter": ch_idx,
                        "chapter_title": ch.get("working_title"),
                        "slot_index": s_idx,
                        "section_type": dr.get("section_type"),
                        "current_words": dr["current_words"],
                        "target_words": dr["target_words"],
                        "words_to_add": delta,
                        "expansion_budget": dr.get("expansion_budget"),
                    }
                )
            else:
                rows.append(
                    {
                        "chapter": ch_idx,
                        "chapter_title": ch.get("working_title"),
                        "slot_index": s_idx,
                        "section_type": packet["section_type"],
                        "current_words": packet["word_count"],
                        "target_words": packet["target_words"],
                        "words_to_add": 0,
                        "expansion_budget": 0,
                        "skipped": True,
                    }
                )

    return {
        "topic": topic,
        "format": format_,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_sections": total_sections,
            "would_expand": would_expand,
            "sections_filled_ratio": (
                f"{would_expand}/{total_sections}"
                f" ({100 * would_expand / total_sections:.1f}%)"
                if total_sections
                else "0/0"
            ),
            "estimated_word_delta": total_word_delta,
            "baseline_total_words": int(budget.get("total_words") or 0),
            "projected_total_words": int(budget.get("total_words") or 0) + total_word_delta,
        },
        "section_rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Pearl_Writer dry-run pilot")
    parser.add_argument("--topic", default="anxiety")
    parser.add_argument("--format", dest="format_", default="standard_book")
    parser.add_argument("--budget", default=None, help="Path to budget.json (optional override)")
    parser.add_argument(
        "--out",
        default=str(REPO_ROOT / "artifacts" / "pilots" / "pearl_writer_dryrun"),
    )
    args = parser.parse_args()

    if args.budget:
        budget_path = Path(args.budget)
    else:
        budget_path = (
            REPO_ROOT
            / "artifacts"
            / "pilots"
            / "duration_matrix"
            / args.topic
            / args.format_
            / "budget.json"
        )

    if not budget_path.exists():
        print(f"ERROR: budget not found at {budget_path}", file=sys.stderr)
        sys.exit(1)

    budget = _load_budget(budget_path)
    report = run_dryrun(budget, topic=args.topic, format_=args.format_)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"dryrun_{args.topic}_{args.format_}.json"
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)

    s = report["summary"]
    print(f"\nPearl_Writer Dry-Run Report — {args.topic}/{args.format_}")
    print(f"  Sections scanned:      {s['total_sections']}")
    print(f"  Would expand:          {s['sections_filled_ratio']}")
    print(f"  Estimated word delta:  +{s['estimated_word_delta']} words")
    print(f"  Baseline total words:  {s['baseline_total_words']}")
    print(f"  Projected total words: {s['projected_total_words']}")
    print(f"\nFull report: {out_path}")


if __name__ == "__main__":
    main()
