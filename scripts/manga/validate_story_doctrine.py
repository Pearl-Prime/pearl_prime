#!/usr/bin/env python3
"""Validate manga story architecture against the manga-native doctrine contract."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping

import yaml

REPO = Path(__file__).resolve().parents[2]
DEFAULT_CONTRACT = REPO / "config" / "manga" / "story_doctrine_contract.yaml"


class StoryDoctrineError(RuntimeError):
    pass


def _beats(chapter: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = chapter.get("plot_beats") or chapter.get("beats") or []
    return [dict(row) for row in rows if isinstance(row, Mapping)]


def validate_story(
    story: Mapping[str, Any],
    *,
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    genre = (
        story.get("genre_engine")
        or story.get("genre_id")
        or story.get("genre_family")
        or (story.get("genre_blueprint") or {}).get("genre_id")
    )
    if (contract.get("episode") or {}).get("require_genre_engine") and not genre:
        failures.append({"rule": "STORY-GENRE-001", "message": "missing genre engine"})

    chapters = story.get("chapters") or []
    if len(chapters) < int((contract.get("episode") or {}).get("min_chapters", 1)):
        failures.append({"rule": "STORY-ARC-001", "message": "no chapters"})

    carriers: list[tuple[int, str]] = []
    visual_embed_beats = 0
    prohibited = [
        str(value).lower()
        for value in (contract.get("anti_lecture") or {}).get("prohibited_phrases", [])
    ]
    accepted_carriers = set(
        str(value)
        for value in (contract.get("craft_carriers") or {}).get("accepted", [])
    )

    for chapter_index, chapter_raw in enumerate(chapters, start=1):
        chapter = dict(chapter_raw)
        chapter_beats = _beats(chapter)
        if not chapter.get("chapter_end_hook"):
            failures.append({
                "rule": "STORY-HOOK-002",
                "chapter": chapter_index,
                "message": "missing chapter closing hook",
            })
        if not chapter_beats:
            failures.append({
                "rule": "STORY-BEAT-001",
                "chapter": chapter_index,
                "message": "chapter has no beats",
            })
            continue

        first = chapter_beats[0]
        if not (
            first.get("hook")
            or first.get("story_function") in {"hook", "opening_hook"}
            or str(first.get("beat_text") or "").strip()
        ):
            failures.append({
                "rule": "STORY-HOOK-001",
                "chapter": chapter_index,
                "message": "opening beat has no hook/content",
            })

        chapter_has_delta = False
        consecutive_exposition = 0
        for beat_index, beat in enumerate(chapter_beats):
            text = str(beat.get("beat_text") or beat.get("text") or "")
            low = text.lower()
            for phrase in prohibited:
                if phrase in low:
                    failures.append({
                        "rule": "STORY-LECTURE-001",
                        "chapter": chapter_index,
                        "beat": beat_index,
                        "message": f"prohibited lecture phrase: {phrase}",
                    })
            function = str(beat.get("story_function") or "")
            if function in {"exposition", "instruction", "lecture"}:
                consecutive_exposition += 1
            else:
                consecutive_exposition = 0
            max_exposition = int(
                (contract.get("chapter") or {}).get("max_consecutive_exposition_beats", 1)
            )
            if consecutive_exposition > max_exposition:
                failures.append({
                    "rule": "STORY-LECTURE-002",
                    "chapter": chapter_index,
                    "beat": beat_index,
                    "message": "too many consecutive exposition beats",
                })

            carrier = str(
                beat.get("craft_carrier")
                or beat.get("embed_carrier")
                or beat.get("metaphor_type")
                or ""
            )
            tags = {str(v) for v in (beat.get("tags") or [])}
            matched = ({carrier} | tags) & accepted_carriers
            for value in matched:
                carriers.append((chapter_index, value))
            if beat.get("doctrine_id") not in (None, "", "none") or beat.get("is_carrier_beat"):
                visual_embed_beats += 1
            if beat.get("emotional_delta") or beat.get("choice_delta"):
                chapter_has_delta = True

        if (contract.get("chapter") or {}).get("require_emotional_delta") and not chapter_has_delta:
            warnings.append({
                "rule": "STORY-EMOTION-001",
                "chapter": chapter_index,
                "message": "no explicit emotional_delta/choice_delta metadata",
            })

    min_embed = int((contract.get("episode") or {}).get("min_visual_embed_beats", 1))
    if visual_embed_beats < min_embed:
        failures.append({
            "rule": "STORY-EMBED-001",
            "message": f"visual embed beats {visual_embed_beats} < {min_embed}",
        })

    min_carriers = int((contract.get("episode") or {}).get("min_craft_carriers", 1))
    if len(carriers) < min_carriers:
        failures.append({
            "rule": "STORY-CRAFT-001",
            "message": "no explicit metaphor/analogy/parable or approved visual carrier",
        })

    mode = str(story.get("mode") or "").strip()
    if mode:
        supported = set((contract.get("mode") or {}).get("supported") or [])
        if mode not in supported:
            failures.append({"rule": "STORY-MODE-001", "message": f"unsupported mode {mode}"})
        if (contract.get("mode") or {}).get("require_vessel_when_declared") and not story.get("mode_vessel"):
            failures.append({"rule": "STORY-MODE-002", "message": "mode declared without mode_vessel"})

    return {
        "contract_id": contract.get("contract_id"),
        "passed": not failures,
        "genre_engine": genre,
        "chapter_count": len(chapters),
        "visual_embed_beat_count": visual_embed_beats,
        "craft_carriers": [{"chapter": ch, "carrier": carrier} for ch, carrier in carriers],
        "failures": failures,
        "warnings": warnings,
        "overall-manga-green": "NOT_PROVEN",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--story", required=True, type=Path)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    story = json.loads(args.story.read_text(encoding="utf-8"))
    contract = yaml.safe_load(args.contract.read_text(encoding="utf-8")) or {}
    report = validate_story(story, contract=contract)
    text = json.dumps(report, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if report["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
