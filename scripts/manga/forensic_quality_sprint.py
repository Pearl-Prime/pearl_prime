#!/usr/bin/env python3
"""Stub forensic manga quality pack (artifacts/analysis/*.md)."""
from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT = REPO_ROOT / "artifacts" / "analysis"


def main() -> int:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    key = (os.environ.get("CLAUDE_API_KEY") or "").strip()
    note = "LLM key present (optional forensic LLM).\n" if key else "No CLAUDE_API_KEY — stubs only.\n"
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "manga_forensic_teardown.md").write_text(f"# Forensic teardown\n\n{note}{ts}\n", encoding="utf-8")
    (OUT / "MANGA_QUALITY_GAP_PLAN.md").write_text(
        "\n".join(
            [
                "# Manga quality gap plan",
                "",
                f"_Generated {ts}_",
                "",
                "## Executive summary",
                "",
                "1. Close image_bank gaps (manga-image-bank-build).",
                "2. Verify pearl-star-gpu + Ollama Gemma/Qwen.",
                "3. Enforce local LLM routing (llm-callers-audit).",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print("Wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
