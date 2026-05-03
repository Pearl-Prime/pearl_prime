#!/usr/bin/env python3
"""Build the ebook catalog index — book equivalent of manga_series_index.json.

Mirrors the manga catalog's data shape so the dashboard generator can be
forked with minimal field swaps. The book-specific differences:

- ``main_character_*`` fields → ``book_cover_*``  (cover image is the
  catalog tile, like the main-character portrait was on the manga page)
- Adds ``book_id`` / ``book_title`` / ``book_subtitle`` / ``publisher``
- Adds ``cover_kind`` (image_full_bleed | image_dominant | type_only) so
  the dashboard can color-code by cover-render strategy
- Adds ``brand_palette`` (hex tuple) so cards can adopt the brand color

Sources:

- ``scripts/release/build_epub.py:TEACHER_BOOKS`` — title / subtitle /
  author / publisher / topic / locale per book
- ``config/publishing/cover_identity_system.yaml`` — brand_id, register,
  subject, micro_palette_shift, cover_kind, series
- ``config/publishing/bestseller_templates.yaml`` — palette + archetype
- ``artifacts/pipeline_examples/<teacher>/cover_<book_id>_FINAL.png`` or
  fallback ``cover_<book_id>_v3_imagery.png`` for the cover tile path

Output: ``artifacts/catalog_visibility/book_series_index.json``.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))


IDENTITY_YAML = REPO_ROOT / "config" / "publishing" / "cover_identity_system.yaml"
TEMPLATES_YAML = REPO_ROOT / "config" / "publishing" / "bestseller_templates.yaml"
COOKBOOK_YAML = REPO_ROOT / "config" / "manga" / "genre_prompt_cookbook_v2.yaml"
INDEX_OUTPUT = REPO_ROOT / "artifacts" / "catalog_visibility" / "book_series_index.json"


def _load_teacher_books() -> list[dict[str, Any]]:
    """Pull TEACHER_BOOKS from the build_epub module without running it."""
    from scripts.release.build_epub import TEACHER_BOOKS
    return list(TEACHER_BOOKS)


def _find_cover_path(teacher: str, book_id_full: str, book_id: str,
                     locale_subdir: str = "us") -> str | None:
    """Prefer the canonical published cover under artifacts/cover_renders/,
    fallback through pipeline_examples (intermediate render staging), else
    None. Returned path is repo-relative for the dashboard to embed."""
    candidates = [
        # Canonical published location
        f"artifacts/cover_renders/{locale_subdir}/{book_id_full}__FINAL.png",
        f"artifacts/cover_renders/{locale_subdir}/{book_id}__FINAL.png",
        # Per-teacher staging (intermediate)
        f"artifacts/pipeline_examples/{teacher}/cover_{book_id_full}_FINAL.png",
        f"artifacts/pipeline_examples/{teacher}/cover_{book_id}_FINAL.png",
        f"artifacts/pipeline_examples/{teacher}/cover_{book_id_full}_v3_imagery.png",
        f"artifacts/pipeline_examples/{teacher}/cover_{book_id}_v3_imagery.png",
        f"artifacts/pipeline_examples/{teacher}/cover_{book_id_full}.png",
    ]
    for p in candidates:
        if (REPO_ROOT / p).is_file():
            return p
    return None


def build_book_series_index() -> dict[str, Any]:
    teacher_books = _load_teacher_books()
    identity = yaml.safe_load(IDENTITY_YAML.read_text()) if IDENTITY_YAML.exists() else {}
    templates = yaml.safe_load(TEMPLATES_YAML.read_text()).get("templates", {}) if TEMPLATES_YAML.exists() else {}

    brands_block = identity.get("brands", {}) or {}
    authors_block = identity.get("authors", {}) or {}
    books_block = identity.get("books", {}) or {}

    rows: list[dict[str, Any]] = []
    for tb in teacher_books:
        teacher = tb["id"]
        topic = tb["topic"]
        book_id_full = f"{teacher}_{topic}"
        book_identity = books_block.get(teacher, {})
        author_id = book_identity.get("author_id") or teacher
        author_record = authors_block.get(author_id, {})
        brand_id = author_record.get("brand_id")
        brand_record = brands_block.get(brand_id, {}) if brand_id else {}
        template = templates.get(topic, {})
        palette = template.get("palette", {})
        primary = palette.get("primary", {}).get("hex") if palette else None
        secondary = palette.get("secondary", {}).get("hex") if palette else None

        cover_kind = book_identity.get("cover_kind")
        if cover_kind is None:
            # Default cover_kind: type-dominant if template says so, else image
            if template.get("type_dominant"):
                cover_kind = "type_only"
            elif template.get("imagery_zone") is None:
                cover_kind = "type_only"
            else:
                cover_kind = "image_dominant"

        cover_path = _find_cover_path(teacher, book_id_full, teacher)

        row = {
            "book_id": book_id_full,
            "teacher": teacher,
            "author_id": author_id,
            "brand_id": brand_id,
            "brand_inspiration": brand_record.get("inspiration"),
            "publisher": tb.get("publisher"),
            "book_title": tb.get("title"),
            "book_subtitle": tb.get("subtitle"),
            "author": tb.get("author"),
            "topic": topic,
            "genre_family": topic,            # 1:1 in self-help; preserved for parity with manga schema
            "subgenre": book_identity.get("series", {}).get("subgenre") if book_identity.get("series") else None,
            "locale": tb.get("lang") or "en",
            "lang": tb.get("lang") or "en",
            "book_register": book_identity.get("this_book_register"),
            "book_subject": book_identity.get("this_book_subject"),
            "book_subject_note": book_identity.get("this_book_subject_note"),
            "micro_palette_shift": book_identity.get("this_book_micro_palette_shift"),
            "series": book_identity.get("series"),
            "brand_palette_primary": primary,
            "brand_palette_secondary": secondary,
            "brand_palette_brand": (brand_record.get("palette") or {}).get("primary"),
            "author_signature_color": author_record.get("signature_color"),
            "cover_kind": cover_kind,
            "template_archetype": template.get("primary_archetype"),
            "book_cover_image_path": cover_path,
            "book_cover_status": "ok" if cover_path else "missing",
            "epub_path": f"artifacts/epub/{book_id_full}.epub" if (REPO_ROOT / f"artifacts/epub/{book_id_full}.epub").is_file() else None,
            "format": "ebook",
            "launch_priority": book_identity.get("launch_priority", "P1"),
            "status": "draft",
        }
        rows.append(row)

    out = {
        "schema_version": 1,
        "books": rows,
        "stats": {
            "total_books": len(rows),
            "covers_present": sum(1 for r in rows if r["book_cover_image_path"]),
            "covers_missing": sum(1 for r in rows if not r["book_cover_image_path"]),
            "type_only": sum(1 for r in rows if r["cover_kind"] == "type_only"),
            "image_full_bleed": sum(1 for r in rows if r["cover_kind"] == "image_full_bleed"),
            "image_dominant": sum(1 for r in rows if r["cover_kind"] == "image_dominant"),
        },
    }
    return out


def main() -> int:
    index = build_book_series_index()
    INDEX_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    INDEX_OUTPUT.write_text(json.dumps(index, indent=2, ensure_ascii=False))
    s = index["stats"]
    print(f"wrote {INDEX_OUTPUT.relative_to(REPO_ROOT)}: "
          f"{s['total_books']} books · {s['covers_present']} with covers · "
          f"{s['covers_missing']} missing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
