#!/usr/bin/env python3
"""Build the ebook catalog HTML dashboard — mirror of the manga catalog page.

The manga catalog renders one card per series with the protagonist's
character image. The book catalog renders one card per BOOK with the
book cover. Operator request 2026-05-03: same description + metadata
format, but with book covers instead of main-character portraits.

Approach: re-use the manga dashboard's HTML/CSS/JS pipeline (it's a
self-contained 770-line template that filters/searches/sorts by
fields). Map the book index's fields onto the manga schema so the
template doesn't have to change:

    book_id              → series_id
    book_title           → series_title
    book_register        → series_logline
    book_description     → series_description (synthesised below)
    book_cover_image_path→ main_character_image_path
    author               → main_character_name
    "ebook"              → main_character_role
    cover_kind           → visual_grammar  (template uses this for color-pill)
    publisher            → audience  (template displays it)

Then do a final find-and-replace on the rendered HTML to swap "Manga"
labels for "Book" labels. The page reads naturally as a book catalog
without template duplication.

Usage:
  python3 scripts/catalog_visibility/build_book_dashboard.py \
      --index artifacts/catalog_visibility/book_series_index.json \
      [--brand stillness_press] \
      [--locale en] \
      [--out artifacts/catalog_visibility/global_book_dashboard.html]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts.catalog_visibility.build_dashboard import (
    build_html, _filter_series, _resolve_brand,
)


# Label substitutions for the rendered HTML.
LABEL_SWAPS = [
    ("Manga catalog", "Book catalog"),
    ("Manga Catalog", "Book Catalog"),
    ("manga catalog", "book catalog"),
    ("manga series", "books"),
    ("Manga series", "Books"),
    (">Series<", ">Books<"),  # tab/header text
    ("Series:", "Books:"),
    ("series_title", "book_title"),
    ("Series title", "Book title"),
    ("Main character", "Author"),
    ("main_character", "author"),
    ("character image", "book cover"),
    ("Character image", "Book cover"),
    ("character portrait", "book cover"),
    ("triptych", "cover"),
    ("Triptych", "Cover"),
]


def _synthesise_description(book: dict[str, Any]) -> str:
    """Compose a book description from R6 identity fields + EPUB metadata."""
    parts: list[str] = []
    register = book.get("book_register")
    subtitle = book.get("book_subtitle")
    subject_note = book.get("book_subject_note")
    if subtitle:
        parts.append(f"**{subtitle}**")
    if register:
        parts.append(register.strip().rstrip(".") + ".")
    if subject_note:
        parts.append(subject_note.strip())
    return "\n\n".join(parts) if parts else ""


def _book_to_series_shape(book: dict[str, Any]) -> dict[str, Any]:
    """Map a book record into the manga schema fields the template renders."""
    return {
        # Core display fields (template renders these)
        "series_id": book.get("book_id"),
        "series_title": book.get("book_title"),
        "series_logline": book.get("book_register") or "",
        "series_description": _synthesise_description(book),
        "main_character_image_path": book.get("book_cover_image_path"),
        "main_character_name": book.get("author"),
        "main_character_role": "Author",
        # Filter / facet fields (template uses these to color-code, group, search)
        "brand_id": book.get("brand_id") or book.get("teacher"),
        "catalog_id": "ebook_us_core",
        "locale": book.get("locale") or "en",
        "market_demo": book.get("publisher") or "",
        "genre_family": book.get("topic") or "",
        "subgenre": book.get("subgenre") or book.get("topic") or "",
        "emotional_engine": book.get("book_register") or "",
        "serialization_engine": "ebook_single",
        "visual_grammar": book.get("cover_kind") or "",
        "reader_promise": book.get("book_register") or "",
        "positioning": book.get("brand_inspiration") or "",
        "audience": book.get("publisher") or "",
        "comp_titles": [],
        "marketing_angle": book.get("template_archetype") or "",
        "hook_lines": [],
        "launch_priority": book.get("launch_priority", "P1"),
        "status": book.get("status", "draft"),
        # Pass-through extras (preserved on the row but not displayed by default)
        "teacher": book.get("teacher"),
        "primary_lane": book.get("topic") or "",
        "cover_kind": book.get("cover_kind"),
        "epub_path": book.get("epub_path"),
        "brand_palette_primary": book.get("brand_palette_primary"),
        "author_signature_color": book.get("author_signature_color"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Build the ebook catalog dashboard.")
    ap.add_argument("--index", type=Path,
                    default=REPO_ROOT / "artifacts" / "catalog_visibility" / "book_series_index.json",
                    help="Path to book_series_index.json")
    ap.add_argument("--brand", type=str, default=None,
                    help="brand_id or teacher_id to filter (omit for all)")
    ap.add_argument("--locale", type=str, default="en")
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--title", type=str, default="",
                    help="HTML title override")
    args = ap.parse_args()

    data = json.loads(args.index.read_text(encoding="utf-8"))
    book_rows = list(data.get("books") or [])
    series_rows = [_book_to_series_shape(b) for b in book_rows]

    filtered = _filter_series(series_rows, brand_id=args.brand, locale=args.locale)

    if args.brand is not None:
        resolved = _resolve_brand(args.brand)
        title = args.title.strip() or f"Book catalog — {resolved} ({args.locale})"
        default_out = args.index.parent / f"{resolved}_{args.locale}_book_dashboard.html"
    else:
        title = args.title.strip() or f"Book catalog — all brands ({args.locale})"
        default_out = args.index.parent / f"global_book_dashboard.html"

    out_path: Path = args.out if args.out is not None else default_out
    html = build_html(series_slice=filtered, page_title=title)

    # Apply label swaps (longest-first to avoid partial matches)
    for src, dst in sorted(LABEL_SWAPS, key=lambda p: -len(p[0])):
        html = html.replace(src, dst)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    try:
        rel = out_path.resolve().relative_to(REPO_ROOT)
        print(f"wrote {rel} — {len(filtered)} books")
    except ValueError:
        print(f"wrote {out_path} — {len(filtered)} books")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
