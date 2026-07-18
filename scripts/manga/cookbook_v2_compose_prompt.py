#!/usr/bin/env python3
"""Compose final FLUX positive (and optional negative) prompt for a book.

Loads ``config/manga/genre_prompt_cookbook_v2.yaml`` and renders the
positive prompt for a given book id by combining its genre's
``subject_prompt`` + ``style_modifiers`` + the universal layout register +
the genre's ``lock_in_tokens``.

The positive prompt is composed from PURELY positive tokens. ALL negations
(``no text``, ``no watermark``, etc) live in ``universal_negative`` and are
emitted only via ``--negative`` or :func:`compose_negative`. This is the
core fix in cookbook v2 vs the prior fragment-based prompts — see PR #802
section 8 for the FLUX-specific negation rule.

Library API
-----------
- :func:`compose_positive(book_id, cookbook_path=None) -> str`
- :func:`compose_negative(cookbook_path=None) -> str`
- :func:`load_cookbook(path) -> dict`

CLI
---
::

    python3 scripts/manga/cookbook_v2_compose_prompt.py --book ahjan_anxiety
    python3 scripts/manga/cookbook_v2_compose_prompt.py --book maat_boundaries --negative
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_COOKBOOK = REPO_ROOT / "config" / "manga" / "genre_prompt_cookbook_v2.yaml"


def load_cookbook(path: Path | str | None = None) -> dict[str, Any]:
    """Load the cookbook YAML and return the parsed dict."""
    cookbook_path = Path(path) if path else DEFAULT_COOKBOOK
    with cookbook_path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"cookbook root must be a mapping, got {type(data)!r}")
    return data


def _normalize(text: str) -> str:
    """Collapse internal whitespace to single spaces and strip."""
    return re.sub(r"\s+", " ", text).strip()


def _resolve_block(book_id: str, cookbook: dict[str, Any]) -> dict[str, Any]:
    """Merge per-book override (if any) over the genre block."""
    book_genre_map = cookbook.get("book_genre_map") or {}
    if book_id not in book_genre_map:
        raise KeyError(
            f"book_id {book_id!r} not in book_genre_map; known books: "
            f"{sorted(book_genre_map.keys())}"
        )
    genre = book_genre_map[book_id]

    genres = cookbook.get("genres") or {}
    if genre not in genres:
        raise KeyError(
            f"genre {genre!r} for book {book_id!r} missing from genres section"
        )

    block = dict(genres[genre])

    overrides = (cookbook.get("book_overrides") or {}).get(book_id) or {}
    if "subject_prompt_override" in overrides:
        block["subject_prompt"] = overrides["subject_prompt_override"]
    if "style_modifiers_override" in overrides:
        block["style_modifiers"] = overrides["style_modifiers_override"]
    if "lock_in_tokens_override" in overrides:
        block["lock_in_tokens"] = overrides["lock_in_tokens_override"]
    return block


def compose_positive(book_id: str, cookbook_path: Path | str | None = None) -> str:
    """Return the composed positive prompt for ``book_id``.

    Order: subject_prompt -> style_modifiers -> universal_register ->
    lock_in_tokens. Pure positive tokens only — no "no X" / "without X"
    fragments are ever introduced here.
    """
    cookbook = load_cookbook(cookbook_path)
    block = _resolve_block(book_id, cookbook)

    universal_register = cookbook.get("universal_register", "")

    parts: list[str] = []
    for key in ("subject_prompt", "style_modifiers"):
        val = block.get(key)
        if val:
            parts.append(_normalize(val))
    if universal_register:
        parts.append(_normalize(universal_register))

    lock_in = block.get("lock_in_tokens") or []
    if lock_in:
        parts.append(", ".join(_normalize(t) for t in lock_in))

    return ", ".join(p for p in parts if p)


def compose_negative(cookbook_path: Path | str | None = None) -> str:
    """Return the universal negative prompt string."""
    cookbook = load_cookbook(cookbook_path)
    return _normalize(cookbook.get("universal_negative", ""))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compose FLUX positive/negative prompts from cookbook v2",
    )
    parser.add_argument(
        "--book",
        required=True,
        help="book id (key under book_genre_map in the cookbook)",
    )
    parser.add_argument(
        "--negative",
        action="store_true",
        help="also print the universal negative prompt after the positive",
    )
    parser.add_argument(
        "--cookbook",
        default=None,
        help="path to cookbook YAML (default: config/manga/genre_prompt_cookbook_v2.yaml)",
    )
    args = parser.parse_args(argv)

    try:
        positive = compose_positive(args.book, args.cookbook)
    except (KeyError, FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print("POSITIVE:")
    print(positive)
    if args.negative:
        print()
        print("NEGATIVE:")
        print(compose_negative(args.cookbook))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
