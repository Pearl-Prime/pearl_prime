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
- V1.1 (2026-05-11): merges full **planned** catalog from the worldwide
  allocation TSV + V1.1 series themes YAML. Rendered books carry
  ``status="rendered"``; planned-but-unrendered books carry
  ``status="planned"`` and have ``book_cover_image_path=None``.

Sources:

- ``scripts/release/build_epub.py:TEACHER_BOOKS`` — title / subtitle /
  author / publisher / topic / locale per book (legacy rendered set)
- ``config/publishing/cover_identity_system.yaml`` — brand_id, register,
  subject, micro_palette_shift, cover_kind, series
- ``config/publishing/bestseller_templates.yaml`` — palette + archetype
- ``artifacts/pipeline_examples/<teacher>/cover_<book_id>_FINAL.png`` or
  fallback ``cover_<book_id>_v3_imagery.png`` for the cover tile path
- ``artifacts/qa/worldwide_catalog_37_brand_allocation_plan_2026-05-11.tsv``
  — V1.1 allocation: brand_id × locale × surface × series_count (ebook rows only)
- ``artifacts/marketing/v1_1_25_brand_series_themes_2026-05-11.yaml`` —
  V1.1 per-brand×locale series concepts (title, arc_shape, throughline)

Output: ``artifacts/catalog_visibility/book_series_index.json``.
"""
from __future__ import annotations

import csv
import json
import re
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

# V1.1 planned-catalog inputs
ALLOCATION_TSV = (
    REPO_ROOT / "artifacts" / "qa"
    / "worldwide_catalog_37_brand_allocation_plan_2026-05-11.tsv"
)
SERIES_THEMES_YAML = (
    REPO_ROOT / "artifacts" / "marketing"
    / "v1_1_25_brand_series_themes_2026-05-11.yaml"
)
CANONICAL_BRANDS_YAML = REPO_ROOT / "config" / "manga" / "canonical_brand_list.yaml"
BRAND_REGISTRY_YAML = REPO_ROOT / "config" / "brand_registry.yaml"


_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _slug(s: str) -> str:
    return _SLUG_RE.sub("_", s.lower()).strip("_") or "x"


def _safe_repo_relative(p: Path) -> str:
    """Return ``p`` relative to REPO_ROOT if possible, else absolute string."""
    try:
        return str(p.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(p)


def _load_allocation_rows(path: Path) -> list[dict[str, str]]:
    """Read the V1.1 worldwide allocation TSV. Returns [] if missing."""
    if not path.is_file():
        return []
    with path.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        return [dict(r) for r in reader]


def _load_series_themes(path: Path) -> dict[str, Any]:
    """Read the V1.1 series themes YAML. Returns {} if missing."""
    if not path.is_file():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data if isinstance(data, dict) else {}


def _load_brand_locale_map() -> dict[str, str]:
    """Map brand_id → declared locale from brand_registry (if present)."""
    if not BRAND_REGISTRY_YAML.is_file():
        return {}
    data = yaml.safe_load(BRAND_REGISTRY_YAML.read_text(encoding="utf-8")) or {}
    brands = data.get("brands") or {}
    out: dict[str, str] = {}
    for bid, meta in brands.items():
        if isinstance(meta, dict) and meta.get("locale"):
            out[str(bid)] = str(meta["locale"])
    return out


def _brand_default_priority(brand_id: str, allocation_rows: list[dict[str, str]]) -> str | None:
    for row in allocation_rows:
        if row.get("brand_id") == brand_id and row.get("priority_phase"):
            return row["priority_phase"]
    return None


def _load_v1_1_planned_books(
    *,
    allocation_path: Path = ALLOCATION_TSV,
    themes_path: Path = SERIES_THEMES_YAML,
) -> list[dict[str, Any]]:
    """Enumerate one row per planned ebook series per (brand, locale).

    Joins allocation TSV (ebook surface only) with V1.1 series themes by
    (brand_id, locale). When themes are missing for a (brand, locale) pair,
    falls back to synthetic ``"<Brand> Series N"`` titles so the planned
    cell is still visible in the dashboard.
    """
    alloc_rows = _load_allocation_rows(allocation_path)
    themes_doc = _load_series_themes(themes_path)
    brand_themes = themes_doc.get("brands") if isinstance(themes_doc, dict) else None
    brand_themes = brand_themes if isinstance(brand_themes, dict) else {}

    brand_locale_registry = _load_brand_locale_map()
    rows_out: list[dict[str, Any]] = []

    for row in alloc_rows:
        if row.get("surface") != "ebook":
            continue
        brand_id = row.get("brand_id") or ""
        locale = row.get("locale") or ""
        if not brand_id or not locale:
            continue
        try:
            series_count = int(row.get("series_count") or 0)
        except ValueError:
            series_count = 0
        try:
            episodes_per_series = int(row.get("episode_per_series_count") or 0)
        except ValueError:
            episodes_per_series = 0
        priority_phase = row.get("priority_phase") or None

        brand_block = brand_themes.get(brand_id) or {}
        series_by_locale = (brand_block.get("series") or {}) if isinstance(brand_block, dict) else {}
        themes_for_locale = series_by_locale.get(locale) or []
        themes_for_locale = themes_for_locale if isinstance(themes_for_locale, list) else []

        # Emit exactly series_count rows per allocation cell. If themes run out, synthesise.
        for idx in range(series_count):
            if idx < len(themes_for_locale):
                t = themes_for_locale[idx] or {}
                title = str(t.get("series_title") or f"{brand_id} series {idx + 1}")
                logline = t.get("arc_shape")
                description = t.get("emotional_throughline")
                surface_priority = t.get("surface_priority")
            else:
                title = f"{brand_id.replace('_', ' ').title()} — Series {idx + 1}"
                logline = None
                description = None
                surface_priority = None

            book_id = f"{brand_id}__{locale}__{idx + 1:02d}"
            rows_out.append({
                "book_id": book_id,
                "brand_id": brand_id,
                "locale": locale,
                "lang": locale,
                "author_id": None,
                "author": None,
                "publisher": None,
                "teacher": None,
                "book_title": title,
                "book_subtitle": logline,
                "book_description": description,
                "topic": (brand_block.get("topic_anchor")
                          if isinstance(brand_block, dict) else None),
                "genre_family": None,
                "subgenre": None,
                "book_register": surface_priority,
                "book_subject": None,
                "book_subject_note": None,
                "micro_palette_shift": None,
                "series": None,
                "brand_palette_primary": None,
                "brand_palette_secondary": None,
                "brand_palette_brand": None,
                "brand_inspiration": None,
                "author_signature_color": None,
                "cover_kind": "planned_placeholder",
                "template_archetype": None,
                "book_cover_image_path": None,
                "book_cover_status": "planned",
                "epub_path": None,
                "format": "ebook",
                "launch_priority": "P1",
                "status": "planned",
                "priority_phase": priority_phase,
                "surface": "ebook",
                "series_count": series_count,
                "episode_per_series_count": episodes_per_series,
                "series_index": idx + 1,
                "registry_locale": brand_locale_registry.get(brand_id),
                "plan_source_path": _safe_repo_relative(allocation_path),
            })

    return rows_out


def _load_v1_2_planned_books(
    repo_root: Path = REPO_ROOT,
) -> list[dict[str, Any]]:
    """Enumerate one row per V1.2 series concept.

    V1.2 themes are richer than V1.1: each series has a fully-authored
    persona_archetype, magical_register, serial_engine, portal_mechanic,
    long_arc_spine, opening_5_volume_arc, etc. Files live at
    ``artifacts/marketing/v1_2_themes_<locale>_cluster_<x>.yaml`` (20 total =
    4 locales × 5 clusters). Each emits ~25 series.

    Output row shape matches V1.1 planned rows for dashboard compatibility,
    with V1.2 metadata added so the card can show register/engine chips.
    Status = "planned"; source_version = "v1.2".
    """
    glob_pattern = "artifacts/marketing/v1_2_themes_*_cluster_*.yaml"
    rows_out: list[dict[str, Any]] = []
    for path in sorted(repo_root.glob(glob_pattern)):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        cluster_id = data.get("cluster")
        locale_default = data.get("locale")
        for series in data.get("series", []) or []:
            series_id = str(series.get("series_id") or "").strip()
            brand_id = str(series.get("brand_id") or "").strip()
            locale = str(series.get("locale") or locale_default or "").strip()
            if not series_id or not brand_id or not locale:
                continue
            book_id = series_id  # already deterministic <brand>__<locale>__<slug>
            rows_out.append({
                "book_id": book_id,
                "brand_id": brand_id,
                "locale": locale,
                "lang": locale,
                "author_id": None,
                "author": None,
                "publisher": None,
                "teacher": None,
                "book_title": series.get("series_title") or f"{brand_id} series",
                "book_subtitle": series.get("series_logline"),
                "book_description": series.get("series_description"),
                "topic": None,
                "genre_family": series.get("genre_family"),
                "subgenre": None,
                "book_register": series.get("reading_platform_fit"),
                "book_subject": None,
                "book_subject_note": None,
                "micro_palette_shift": None,
                "series": None,
                "brand_palette_primary": None,
                "brand_palette_secondary": None,
                "brand_palette_brand": None,
                "brand_inspiration": None,
                "author_signature_color": None,
                "cover_kind": "planned_placeholder",
                "template_archetype": None,
                "book_cover_image_path": None,
                "book_cover_status": "planned",
                "epub_path": None,
                "format": "ebook",
                "launch_priority": "P1",
                "status": "planned",
                "priority_phase": None,
                "surface": "ebook",
                "series_count": None,
                "episode_per_series_count": None,
                "series_index": None,
                "registry_locale": None,
                "plan_source_path": str(path.relative_to(repo_root)),
                # V1.2-specific metadata (pass-through for dashboard card chips):
                "source_version": "v1.2",
                "cluster_id": cluster_id,
                "persona_archetype": series.get("persona_archetype"),
                "daily_life_anchor": series.get("daily_life_anchor"),
                "portal_mechanic": series.get("portal_mechanic"),
                "episodic_frame_per_volume": series.get("episodic_frame_per_volume"),
                "magical_register": series.get("magical_register"),
                "serial_engine": series.get("serial_engine"),
                "long_arc_spine": series.get("long_arc_spine"),
                "volume_runway_target": series.get("volume_runway_target"),
                "reading_platform_fit": series.get("reading_platform_fit"),
                "opening_5_volume_arc": series.get("opening_5_volume_arc"),
                "comp_titles": series.get("comp_titles"),
                "reader_promise": series.get("reader_promise"),
                "marketing_angle": series.get("marketing_angle"),
                "emotional_engine": series.get("emotional_engine"),
                "audience": series.get("audience"),
            })
    return rows_out


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
            "status": "rendered",
            "priority_phase": "V1.0_matrix_confirmed",
            "surface": "ebook",
        }
        rows.append(row)

    # V1.1 — merge planned-but-unrendered ebook rows from worldwide allocation TSV.
    planned_rows = _load_v1_1_planned_books()
    rendered_ids = {str(r.get("book_id")) for r in rows}
    merged: list[dict[str, Any]] = list(rows)
    for p in planned_rows:
        if str(p.get("book_id")) in rendered_ids:
            # Rendered row already exists with this id; keep rendered metadata.
            continue
        merged.append(p)

    # V1.2 — merge richer planned rows from the 20 cluster YAML files.
    # Each V1.2 series has portal_mechanic / magical_register / serial_engine
    # / persona_archetype metadata that the dashboard card surfaces.
    v1_2_rows = _load_v1_2_planned_books()
    existing_ids = {str(r.get("book_id")) for r in merged}
    for v in v1_2_rows:
        if str(v.get("book_id")) in existing_ids:
            # Already covered by rendered or V1.1 planned; do not duplicate.
            continue
        merged.append(v)
        existing_ids.add(str(v.get("book_id")))

    out = {
        "schema_version": 2,
        "books": merged,
        "stats": {
            "total_books": len(merged),
            "rendered_books": sum(1 for r in merged if r.get("status") == "rendered"),
            "planned_books": sum(1 for r in merged if r.get("status") == "planned"),
            "covers_present": sum(1 for r in merged if r.get("book_cover_image_path")),
            "covers_missing": sum(1 for r in merged if not r.get("book_cover_image_path")),
            "type_only": sum(1 for r in merged if r.get("cover_kind") == "type_only"),
            "image_full_bleed": sum(1 for r in merged if r.get("cover_kind") == "image_full_bleed"),
            "image_dominant": sum(1 for r in merged if r.get("cover_kind") == "image_dominant"),
        },
    }
    return out


def main() -> int:
    index = build_book_series_index()
    INDEX_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    INDEX_OUTPUT.write_text(json.dumps(index, indent=2, ensure_ascii=False))
    s = index["stats"]
    print(f"wrote {_safe_repo_relative(INDEX_OUTPUT)}: "
          f"{s['total_books']} books "
          f"({s.get('rendered_books', 0)} rendered + "
          f"{s.get('planned_books', 0)} planned) · "
          f"{s['covers_present']} with covers · "
          f"{s['covers_missing']} missing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
