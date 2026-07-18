#!/usr/bin/env python3
"""Generate story-engine proof artifacts for 3 exemplar governed genres."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "artifacts" / "qa" / "story_engine_proof"

EXEMPLARS = [
    ("psychological_horror", "anxiety", "horror_thriller_lane"),
    ("workplace_drama", "burnout", "romance_workplace_lane"),
    ("action_battle", "courage", "battle_sports_lane"),
]


def main() -> int:
    sys.path.insert(0, str(REPO))
    from phoenix_v4.manga.series.story_architect import build_story_architecture_internal
    from phoenix_v4.manga.story_engine_loader import (
        engine_spec,
        validate_engine_blob,
        _blob_from_chapters,
    )

    OUT.mkdir(parents=True, exist_ok=True)
    summary: list[dict] = []

    for genre, topic, lane in EXEMPLARS:
        internal = build_story_architecture_internal(
            series_id=f"proof_{lane}__{topic}",
            arc_id="arc_001",
            genre_id=genre,
            topic=topic,
        )
        ch1_beats = [
            {"beat_index": b.get("beat_index"), "beat_text": b.get("beat_text")}
            for b in internal["chapters"][0]["plot_beats"]
        ]
        blob = _blob_from_chapters(internal["chapters"])
        violations = validate_engine_blob(blob, genre)
        spec = engine_spec(genre) or {}

        artifact = {
            "lane": lane,
            "genre": genre,
            "topic": topic,
            "story_engine_genre": internal.get("story_engine_genre"),
            "transmission_note": internal["transmission_audit"]["note"],
            "core_engine": spec.get("core_engine"),
            "chapter_1_beats": ch1_beats,
            "engine_validation": "PASS" if not violations else violations,
        }
        out_path = OUT / f"{lane}__{genre}__architect.json"
        out_path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n")
        summary.append({
            "lane": lane,
            "genre": genre,
            "artifact": str(out_path.relative_to(REPO)),
            "beats": len(ch1_beats),
            "validation": artifact["engine_validation"],
        })

    (OUT / "PROOF_SUMMARY.json").write_text(
        json.dumps({"exemplars": summary}, indent=2) + "\n"
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
