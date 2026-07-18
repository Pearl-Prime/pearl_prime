#!/usr/bin/env python3
"""Identity-system prompt composer (R7).

Layered on top of ``cookbook_v2_compose_prompt.py``: where the cookbook
emits a generic per-genre subject + style register, this composer reads
``config/publishing/cover_identity_system.yaml`` (R6) and composes a
prompt that reflects the four-layer identity:

    book.this_book_subject (per-book unique focal scene)
    + book.this_book_register (per-book emotional micro-register)
    + brand.motif_pool[author.motif_focus] (motif lock-in)
    + brand.palette descriptor (palette lock-in)
    + cookbook.style_modifiers (per-genre styling layer)
    + cookbook.universal_register (KDP composition register)
    + identity lock-in tokens

Pure positive tokens only. Negatives stay in
``cookbook.universal_negative`` (re-exported via
:func:`compose_identity_negative` for convenience).

Library API
-----------
* :func:`compose_identity_positive(book_id) -> str`
* :func:`compose_identity_negative() -> str`
* :func:`load_identity_system(path=None) -> dict`
* :func:`book_is_type_only(book_id) -> bool`

CLI
---
``python3 scripts/publish/identity_compose_prompt.py --book ahjan``
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IDENTITY_PATH = REPO_ROOT / "config" / "publishing" / "cover_identity_system.yaml"
DEFAULT_COOKBOOK_PATH = REPO_ROOT / "config" / "manga" / "genre_prompt_cookbook_v2.yaml"


def load_identity_system(path: Path | str | None = None) -> dict[str, Any]:
    """Load and lightly validate the identity-system YAML."""
    p = Path(path) if path else DEFAULT_IDENTITY_PATH
    if not p.exists():
        raise FileNotFoundError(f"identity system YAML missing: {p}")
    with p.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"identity system root must be a mapping, got {type(data)!r}")
    for required in ("brands", "authors", "books"):
        if required not in data:
            raise ValueError(f"identity system YAML missing top-level '{required}'")
    return data


def _load_cookbook(path: Path | str | None = None) -> dict[str, Any]:
    p = Path(path) if path else DEFAULT_COOKBOOK_PATH
    with p.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return data or {}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _resolve_book(book_id: str, identity: dict[str, Any]) -> tuple[
    dict[str, Any], dict[str, Any], dict[str, Any]
]:
    """Return (book, author, brand) records for ``book_id``."""
    books = identity.get("books") or {}
    if book_id not in books:
        raise KeyError(
            f"book_id {book_id!r} not in identity system; known: "
            f"{sorted(books.keys())}"
        )
    book = books[book_id]
    author_id = book.get("author_id")
    authors = identity.get("authors") or {}
    if author_id not in authors:
        raise KeyError(
            f"author_id {author_id!r} (from book {book_id!r}) not in authors"
        )
    author = authors[author_id]
    brand_id = author.get("brand_id")
    brands = identity.get("brands") or {}
    if brand_id not in brands:
        raise KeyError(
            f"brand_id {brand_id!r} (from author {author_id!r}) not in brands"
        )
    brand = brands[brand_id]
    return book, author, brand


def book_is_type_only(book_id: str, identity_path: Path | str | None = None) -> bool:
    """True if the book is type-only (no FLUX imagery)."""
    identity = load_identity_system(identity_path)
    book, _, _ = _resolve_book(book_id, identity)
    return book.get("cover_kind") == "type_only"


def _palette_descriptor(brand: dict[str, Any]) -> str:
    pal = brand.get("palette") or {}
    bits: list[str] = []
    if pal.get("primary"):
        bits.append(f"dominant primary {pal['primary']}")
    if pal.get("secondary"):
        bits.append(f"warm secondary {pal['secondary']}")
    if pal.get("accent"):
        bits.append(f"single accent {pal['accent']}")
    if not bits:
        return ""
    return "constrained palette: " + ", ".join(bits)


def _motif_focus_descriptor(author: dict[str, Any], brand: dict[str, Any]) -> str:
    focus = author.get("motif_focus") or []
    pool = set(brand.get("motif_pool") or [])
    valid = [m for m in focus if m in pool]
    if not valid:
        return ""
    return "motif focus: " + ", ".join(m.replace("_", " ") for m in valid)


def _identity_lock_ins(book: dict[str, Any], author: dict[str, Any],
                       brand: dict[str, Any]) -> list[str]:
    locks: list[str] = []
    if brand.get("one_word_read"):
        locks.append(f"emotional read: {brand['one_word_read']}")
    if brand.get("finish"):
        locks.append(_normalize(brand["finish"]))
    if author.get("signature_color"):
        locks.append(
            f"author signature accent {author['signature_color']} present in scene"
        )
    if book.get("this_book_micro_palette_shift"):
        locks.append(_normalize(book["this_book_micro_palette_shift"]))
    return locks


def compose_identity_positive(
    book_id: str,
    identity_path: Path | str | None = None,
    cookbook_path: Path | str | None = None,
) -> str:
    """Compose the FLUX-positive prompt for ``book_id`` from the identity
    system. Raises ValueError if the book is type-only (caller should
    branch on :func:`book_is_type_only`).
    """
    identity = load_identity_system(identity_path)
    book, author, brand = _resolve_book(book_id, identity)
    if book.get("cover_kind") == "type_only":
        raise ValueError(
            f"book {book_id!r} is type_only; do not compose a FLUX prompt"
        )
    subject = book.get("this_book_subject")
    if not subject:
        raise ValueError(
            f"book {book_id!r} has no this_book_subject and is not type_only"
        )

    cookbook = _load_cookbook(cookbook_path)
    topic = book.get("topic") or ""
    genre_block = (cookbook.get("genres") or {}).get(topic, {})
    style_modifiers = genre_block.get("style_modifiers") or ""
    universal_register = cookbook.get("universal_register") or ""

    parts: list[str] = []
    parts.append(_normalize(subject))
    if book.get("this_book_register"):
        parts.append(f"register: {_normalize(book['this_book_register'])}")
    motif = _motif_focus_descriptor(author, brand)
    if motif:
        parts.append(motif)
    palette = _palette_descriptor(brand)
    if palette:
        parts.append(palette)
    if style_modifiers:
        parts.append(_normalize(style_modifiers))
    if universal_register:
        parts.append(_normalize(universal_register))
    locks = _identity_lock_ins(book, author, brand)
    if locks:
        parts.append(", ".join(locks))

    return ", ".join(p for p in parts if p)


def compose_identity_negative(cookbook_path: Path | str | None = None) -> str:
    cookbook = _load_cookbook(cookbook_path)
    return _normalize(cookbook.get("universal_negative") or "")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compose FLUX prompts from the cover identity system (R6/R7).",
    )
    parser.add_argument("--book", required=True,
                        help="book id (key under books: in cover_identity_system.yaml)")
    parser.add_argument("--negative", action="store_true",
                        help="also emit the universal negative")
    parser.add_argument("--identity", default=None)
    parser.add_argument("--cookbook", default=None)
    args = parser.parse_args(argv)

    try:
        if book_is_type_only(args.book, args.identity):
            print(f"# book {args.book!r} is type_only; FLUX is skipped.")
            return 0
        positive = compose_identity_positive(args.book, args.identity, args.cookbook)
    except (KeyError, FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print("POSITIVE:")
    print(positive)
    if args.negative:
        print()
        print("NEGATIVE:")
        print(compose_identity_negative(args.cookbook))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
