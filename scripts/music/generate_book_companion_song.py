#!/usr/bin/env python3
"""Build a MusicGen-style text prompt for a 60s companion track from a rendered book.

Runnable full-bandwidth MusicGen remains Colab-oriented (``musicgen_colab.py``) in this
repository. V1 ships **prompt + snippet extraction** so operators can paste into Colab or
Pearl Star without pulling ``audiocraft`` into CI.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))


def _extract_music_snippets(book_text: str, limit: int = 3) -> list[str]:
    chunks: list[str] = []
    for block in re.split(r"\n---\s+Music[^\n]*---\s*\n", book_text):
        block = block.strip()
        if not block:
            continue
        lines = [ln.strip() for ln in block.splitlines() if ln.strip() and not ln.startswith("---")]
        snippet = "\n".join(lines[:8]).strip()
        if len(snippet) > 40:
            chunks.append(snippet)
    chunks.sort(key=len, reverse=True)
    return chunks[:limit]


def build_musicgen_prompt(*, snippets: list[str], genre: str, theme: str, topic: str) -> str:
    joined = " | ".join(snippets) if snippets else "instrumental indie folk healing bed"
    return (
        f"{genre} instrumental, 60 seconds, warm, not busy, no vocals, "
        f"supporting readers working on {topic}, emotional color: {theme}. "
        f"Textual inspiration (not sung): {joined[:1200]}"
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Book companion song — prompt JSON (MusicGen deferred)")
    ap.add_argument("--book-output", required=True, type=Path, help="Path to rendered book.txt")
    ap.add_argument("--musician-id", required=True, help="Musician bank id")
    ap.add_argument("--out", required=True, type=Path, help="Output path (.json)")
    args = ap.parse_args()

    book_path: Path = args.book_output
    text = book_path.read_text(encoding="utf-8")
    snippets = _extract_music_snippets(text)

    try:
        import yaml  # type: ignore
    except ImportError:
        yaml = None  # type: ignore

    genre, theme, topic = "indie folk", "recovery", "anxiety"
    profile_path = REPO_ROOT / "SOURCE_OF_TRUTH" / "musician_banks" / args.musician_id / "profile.yaml"
    if yaml is not None and profile_path.exists():
        prof = yaml.safe_load(profile_path.read_text(encoding="utf-8")) or {}
        genre = str(prof.get("primary_genre") or genre)
        th = prof.get("themes") or []
        if isinstance(th, list) and th:
            theme = ", ".join(str(x) for x in th[:4])

    prompt = build_musicgen_prompt(snippets=snippets, genre=genre, theme=theme, topic=topic)
    out_path: Path = args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.suffix != ".json":
        out_path = out_path.with_suffix(".json")

    payload = {
        "musician_id": args.musician_id,
        "book_path": str(book_path),
        "snippets": snippets,
        "musicgen_prompt": prompt,
        "audio_status": "deferred",
        "defer_reason": "MusicGen entry point is Colab/Pearl-Star oriented; no local audiocraft gate in V1.",
    }
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote companion prompt artifact: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
