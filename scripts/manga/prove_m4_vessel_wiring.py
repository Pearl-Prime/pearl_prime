#!/usr/bin/env python3
"""M4 exit proof: story_architect beats differ with vs without mode vessel."""
from __future__ import annotations

import json
from pathlib import Path

from phoenix_v4.manga.series.story_architect import build_story_architecture_internal
from phoenix_v4.manga.chapter.writer import build_chapter_writer_prompt

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "artifacts" / "qa" / "manga_m4_vessel_wiring_proof"


def _beat_texts(arch: dict) -> list[str]:
    texts: list[str] = []
    for ch in arch.get("chapters") or []:
        for b in ch.get("plot_beats") or []:
            texts.append(str(b.get("beat_text") or ""))
    return texts


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    series_id = "m4_proof__mecha__en_US"
    arc_id = "arc_proof"
    genre_id = "mecha"

    without = build_story_architecture_internal(
        series_id=series_id, arc_id=arc_id, genre_id=genre_id, topic="burnout",
    )
    with_vessel = build_story_architecture_internal(
        series_id=series_id, arc_id=arc_id, genre_id=genre_id, topic="burnout",
        mode="teacher",
    )

    (OUT / "beats_WITHOUT_vessel.json").write_text(
        json.dumps(without, indent=2) + "\n", encoding="utf-8",
    )
    (OUT / "beats_WITH_vessel.json").write_text(
        json.dumps(with_vessel, indent=2) + "\n", encoding="utf-8",
    )

    t0 = _beat_texts(without)
    t1 = _beat_texts(with_vessel)
    only_with = [t for t in t1 if t not in t0]
    only_without_count = len(t0)
    only_with_count = len(t1)

    # Writer prompt proof
    handoff = {
        "chapters": with_vessel["chapters"],
        "mode": "teacher",
        "genre_id": genre_id,
        "mode_vessel": with_vessel.get("mode_vessel"),
    }
    # story handoff shape for writer expects chapter_number on chapters
    for i, ch in enumerate(handoff["chapters"], 1):
        ch.setdefault("chapter_number", i)
    prompt_with = build_chapter_writer_prompt(
        handoff, chapter_number=1, series_id=series_id, chapter_id="ep_001",
        mode="teacher", genre_id=genre_id,
    )
    prompt_without = build_chapter_writer_prompt(
        {"chapters": without["chapters"]},
        chapter_number=1, series_id=series_id, chapter_id="ep_001",
    )
    (OUT / "writer_prompt_WITH_vessel.txt").write_text(prompt_with, encoding="utf-8")
    (OUT / "writer_prompt_WITHOUT_vessel.txt").write_text(prompt_without, encoding="utf-8")

    lines = [
        "# M4 Vessel Wiring Proof",
        "",
        f"- genre_id: `{genre_id}`",
        f"- mode: `teacher` (with) vs unset (without)",
        f"- beats without vessel: **{only_without_count}**",
        f"- beats with vessel: **{only_with_count}**",
        f"- vessel-only beat texts: **{len(only_with)}**",
        f"- mode_vessel present: **{bool(with_vessel.get('mode_vessel'))}**",
        f"- writer prompt contains 'Mode vessel': **{'Mode vessel' in prompt_with}**",
        f"- writer prompt (no mode) contains 'Mode vessel': **{'Mode vessel' in prompt_without}**",
        "",
        "## Vessel-injected beat samples",
        "",
    ]
    for t in only_with[:5]:
        lines.append(f"- {t[:200]}")
    lines.append("")
    differ = (
        only_with
        and with_vessel.get("mode_vessel")
        and "Mode vessel" in prompt_with
        and "Mode vessel" not in prompt_without
        and t0 != t1
    )
    lines.append(f"**BEHAVIORAL DIFF: {'PASS' if differ else 'FAIL'}**")
    report = "\n".join(lines) + "\n"
    (OUT / "BEAT_DIFF_REPORT.md").write_text(report, encoding="utf-8")
    print(report)
    return 0 if differ else 1


if __name__ == "__main__":
    raise SystemExit(main())
