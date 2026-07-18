#!/usr/bin/env python3
"""
One-shot forensic manga quality sprint (stubs + optional Claude calls).

Writes artifacts under artifacts/analysis/ for agent PR packaging.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT = REPO_ROOT / "artifacts" / "analysis"


def _stub(path: Path, title: str, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# {title}\n\n{body}\n", encoding="utf-8")


def main() -> int:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    key = (os.environ.get("CLAUDE_API_KEY") or os.environ.get("ANTHROPIC_API_KEY") or "").strip()
    llm_note = (
        "LLM key present: extend this stub with Anthropic batch calls per workstream.\n"
        if key
        else "No CLAUDE_API_KEY — operator stub only.\n"
    )
    _stub(
        OUT / "manga_forensic_teardown.md",
        "Manga forensic teardown",
        f"Generated {ts}.\n\n{llm_note}",
    )
    streams = [
        ("iyashikei_craft_study.md", "Iyashikei craft study"),
        ("studio_workflow_gap.md", "Studio workflow gap analysis"),
        ("series_identity_layer.md", "Series identity layer"),
        ("character_consistency.md", "Character consistency"),
        ("name_thumbnail_stage.md", "Name thumbnail stage"),
        ("visual_quality_gates.md", "Visual quality gates"),
    ]
    for fname, title in streams:
        _stub(OUT / fname, title, f"Generated {ts}.\n\n{llm_note}")
    gap = OUT / "MANGA_QUALITY_GAP_PLAN.md"
    gap.write_text(
        "\n".join(
            [
                "# Manga quality gap plan",
                "",
                f"_Generated {ts}_",
                "",
                "## Executive summary",
                "",
                "1. Install OFL fonts under `fonts/manga/ttf/` (see FONT_REGISTRY.yaml).",
                "2. Run `manga-smoke-test` on `pearl-star-gpu` with ComfyUI / RunComfy backends.",
                "3. Close forensic workstreams above; prioritize print-grade lettering + bubbles.",
                "4. Named series + character sheets: dispatch `manga-series-pitch` + `manga-character-sheet-build`.",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print("Wrote:", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
