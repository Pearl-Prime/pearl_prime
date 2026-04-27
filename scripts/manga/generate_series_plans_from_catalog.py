#!/usr/bin/env python3
"""Generate v2 series_plan YAMLs from MANGA_FULL_CATALOG_PLAN.md.

Catalog-rebuild Phase 1. Reads the markdown catalog plan, applies the
format-routing rules in config/manga/format_routing.yaml, and emits one
YAML per series under config/source_of_truth/manga_series_plans/<locale>/.

Each YAML conforms to schemas/manga/series_plan.schema.json v2 (PR #631):
- master_format + flatten_exports (webtoon as master, B&W as downstream)
- connector_lane (unified_canvas / line_manga_indies / naver_webtoon_kr / print_only / partner_required)
- localized_titles (placeholder for cross-market shipping)
- pending_partner_targets (PARTNER_ONLY platforms documented but unblocked)

Usage:
    # Dry run — print what would be generated, no files written
    python3 scripts/manga/generate_series_plans_from_catalog.py --dry-run

    # Generate samples only (one per locale × teacher)
    python3 scripts/manga/generate_series_plans_from_catalog.py --samples-only

    # Full generation
    python3 scripts/manga/generate_series_plans_from_catalog.py

    # Filter by teacher / locale
    python3 scripts/manga/generate_series_plans_from_catalog.py --teacher ahjan --locale en_US

Validates each emitted plan against the schema. Exits non-zero if any
plan fails validation.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any, Iterable

REPO = Path(__file__).resolve().parents[2]
CATALOG_PLAN = REPO / "artifacts" / "manga" / "MANGA_FULL_CATALOG_PLAN.md"
ROUTING_CFG = REPO / "config" / "manga" / "format_routing.yaml"
OUT_ROOT = REPO / "config" / "source_of_truth" / "manga_series_plans"
SAMPLE_ROOT = REPO / "config" / "source_of_truth" / "manga_series_plans" / "_samples"

VALID_LOCALES = (
    "en_US", "ja_JP", "ko_KR", "zh_TW", "zh_CN",
    "es_LA", "hu_HU", "zh_HK",
)
VALID_GENRES = (
    "iyashikei", "seinen", "shonen", "shojo", "horror",
    "cultivation", "manhwa", "webtoon_romance", "isekai", "josei_essay_manga",
    "dark_fantasy", "psychological_horror", "supernatural_mystery",
    "sci_fi_cyberpunk", "psychological_thriller", "romance_josei_drama",
    "workplace_drama", "action_battle", "sports_competition",
    "historical_period", "cultivation_martial", "school_coming_of_age",
    "mecha",
)


# ─── parsing helpers ────────────────────────────────────────────────────────


_RE_TEACHER_HEADING = re.compile(r"^## \d+\.\s+([A-Z_]+)\s*—", re.IGNORECASE)
_RE_LOCALE_HEADING = re.compile(r"^### (en_US|ja_JP|ko_KR|zh_TW|zh_CN|es_LA|hu_HU|zh_HK)\b")
# Strand sub-heading captures secondary catalog sections like
# "### Ahjan — forest simplicity strand (Stillness Press; ...)".
# When a strand heading appears under a teacher, subsequent rows are tagged
# with the strand slug so series_ids don't collide with the main section.
_RE_STRAND_HEADING = re.compile(
    r"^###\s+([A-Z][A-Za-z]+)\s*—\s*([^()\n]+?)\s*(?:\([^)]*\))?\s*$"
)
_RE_TABLE_ROW = re.compile(
    r"^\|\s*(\d+)\s*\|"           # row number
    r"\s*([^|]+?)\s*\|"            # title
    r"\s*([^|]+?)\s*\|"            # genre
    r"\s*([^|]+?)\s*\|"            # style
    r"\s*([^|]+?)\s*\|"            # manga_author
    r"\s*([^|]+?)\s*\|"            # topic
    r"\s*(\d+)\s*\|?"              # chapters
)


def _slugify(text: str) -> str:
    """Lowercase + non-alnum → underscore + collapse + strip underscores."""
    s = re.sub(r"[^a-zA-Z0-9]+", "_", text.lower())
    return s.strip("_")


def parse_catalog(path: Path) -> list[dict[str, Any]]:
    """Yield one row per catalog entry: teacher / locale / strand / title / genre / style / author / topic / chapters."""
    rows: list[dict[str, Any]] = []
    cur_teacher: str | None = None
    cur_locale: str | None = None
    cur_strand: str | None = None  # None = main section, otherwise slug

    for line in path.read_text(encoding="utf-8").splitlines():
        m = _RE_TEACHER_HEADING.match(line)
        if m:
            cur_teacher = m.group(1).lower()
            cur_locale = None
            cur_strand = None
            continue
        # Locale heading must be checked before strand heading because
        # `### en_US (24 series)` would also match strand pattern otherwise.
        m = _RE_LOCALE_HEADING.match(line)
        if m:
            cur_locale = m.group(1)
            continue
        # Strand heading like "### Ahjan — forest simplicity strand (...)".
        m = _RE_STRAND_HEADING.match(line)
        if m and cur_teacher and m.group(1).lower() == cur_teacher:
            cur_strand = _slugify(m.group(2))
            cur_locale = None  # locale resets per strand
            continue
        m = _RE_TABLE_ROW.match(line)
        if not m:
            continue
        if not cur_teacher or not cur_locale:
            continue

        idx, title, genre, style, author, topic, chapters = m.groups()
        genre = genre.strip()
        if genre not in VALID_GENRES:
            continue

        rows.append(
            {
                "teacher_id": cur_teacher,
                "locale": cur_locale,
                "strand": cur_strand,                  # None for main section
                "row_number": int(idx),
                "title": title.strip(),
                "genre": genre,
                "style": style.strip(),
                "manga_author": author.strip(),
                "topic": _slugify(topic),
                "chapters_target": int(chapters),
            }
        )
    return rows


# ─── routing ────────────────────────────────────────────────────────────────


def _load_yaml(path: Path) -> dict[str, Any]:
    import yaml  # type: ignore

    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def resolve_format(routing: dict[str, Any], locale: str, genre: str, style: str) -> str:
    """Return master_format for this row."""
    style_overrides = (routing.get("style_overrides") or {}).get(style) or {}
    forced = style_overrides.get("force_master")
    if forced:
        return forced
    locale_specific = style_overrides.get("locale_specific") or {}
    if locale in locale_specific:
        return locale_specific[locale]
    default = ((routing["defaults_by_locale_genre"].get(locale) or {}).get(genre) or {})
    return default.get("master") or "color_vertical_webtoon"


def resolve_flatten_exports(routing: dict[str, Any], locale: str, genre: str) -> list[str]:
    default = ((routing["defaults_by_locale_genre"].get(locale) or {}).get(genre) or {})
    return list(default.get("flatten") or [])


def resolve_target_platforms(routing: dict[str, Any], locale: str, master_format: str) -> list[str]:
    return list(
        ((routing["target_platforms_by_locale_format"].get(locale) or {}).get(master_format) or [])
    )


def resolve_pending_partner_targets(routing: dict[str, Any], locale: str) -> list[str]:
    return list(routing.get("pending_partner_targets_by_locale", {}).get(locale) or [])


def resolve_connector_lane(routing: dict[str, Any], locale: str, master_format: str) -> str:
    return ((routing["connector_lane_by_locale_format"].get(locale) or {}).get(master_format)
            or "print_only")


def resolve_panel_template(routing: dict[str, Any], master_format: str) -> str:
    return routing["panel_layout_template_by_format"][master_format]


# ─── plan construction ─────────────────────────────────────────────────────


def derive_brand_id(teacher_id: str) -> str:
    """Map teacher_id → brand_id. Default: 'stillness_press' for ahjan; per-teacher mapping below."""
    return {
        "ahjan": "stillness_press",
        "joshin": "zen_threshold",
        "junko": "harmony_circle",
        "maat": "scales_of_light",
        "master_feung": "rooted_breath",
        "master_sha": "longevity_arts",
        "master_wu": "calm_storm",
        "miki": "presence_lab",
        "omote": "seasonal_body",
        "pamela_fellows": "embodied_excellence",
        "ra": "solar_return",
        "sai_ma": "bhakti_flame",
    }.get(teacher_id, f"{teacher_id}_press")


def build_series_id(row: dict[str, Any]) -> str:
    """e.g. stillness_press__ahjan__en_US__anxiety__alarm_is_lying

    Falls back to ``row{N}`` when the title has no Latin chars (e.g. ja_JP / zh titles)
    so the series_id stays valid filename + ASCII.

    When the row is from a strand sub-section (e.g. "Ahjan — forest simplicity"),
    the strand slug is appended to keep series_ids unique across sections of the
    same teacher in the same locale.
    """
    brand = derive_brand_id(row["teacher_id"])
    title_slug = _slugify(row["title"])[:40]
    if not title_slug:
        title_slug = f"row{row['row_number']:02d}"
    sid = f"{brand}__{row['teacher_id']}__{row['locale']}__{row['topic']}__{title_slug}"
    if row.get("strand"):
        sid += f"__{row['strand']}"
    return sid


def build_plan(row: dict[str, Any], routing: dict[str, Any]) -> dict[str, Any]:
    locale = row["locale"]
    genre = row["genre"]
    style = row["style"]

    master_format = resolve_format(routing, locale, genre, style)
    flatten_exports = resolve_flatten_exports(routing, locale, genre)
    target_platforms = resolve_target_platforms(routing, locale, master_format)
    pending = resolve_pending_partner_targets(routing, locale)
    connector_lane = resolve_connector_lane(routing, locale, master_format)
    panel_template = resolve_panel_template(routing, master_format)

    series_id = build_series_id(row)

    plan: dict[str, Any] = {
        "series_plan_schema": "2.0.0",
        "series_id": series_id,
        "brand_id": derive_brand_id(row["teacher_id"]),
        "teacher_id": row["teacher_id"],
        "locale": locale,
        "default_locale": locale,
        "format": master_format,                    # v1 backward-compat
        "master_format": master_format,
        "flatten_exports": flatten_exports,
        "connector_lane": connector_lane,
        "panel_layout_template": panel_template,
        "target_platforms": target_platforms,
        "title": row["title"],
        "localized_titles": {locale: row["title"]},
        "genre": genre,
        "style": style,
        "topic": row["topic"],
        "manga_author": row["manga_author"],
        "chapters_target": row["chapters_target"],
        "ai_disclosure_required": True,             # all AI-rendered series declare
    }
    if pending:
        plan["pending_partner_targets"] = pending
    return plan


# ─── validation ────────────────────────────────────────────────────────────


def _load_schema() -> dict[str, Any]:
    import json

    schema_path = REPO / "schemas" / "manga" / "series_plan.schema.json"
    return json.loads(schema_path.read_text(encoding="utf-8"))


def validate_plan(plan: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    try:
        import jsonschema  # type: ignore
    except ImportError:
        # Soft validate
        return [f"missing required: {r}" for r in schema.get("required") or [] if r not in plan]
    v = jsonschema.Draft202012Validator(schema)
    return [
        f"{'.'.join(str(p) for p in err.absolute_path)}: {err.message}"
        for err in v.iter_errors(plan)
    ]


# ─── filesystem ────────────────────────────────────────────────────────────


def _write_plan(out_root: Path, plan: dict[str, Any]) -> Path:
    import yaml  # type: ignore

    locale_dir = out_root / plan["locale"]
    locale_dir.mkdir(parents=True, exist_ok=True)
    out_path = locale_dir / f"{plan['series_id']}.yaml"

    out_path.write_text(
        "# Auto-generated by scripts/manga/generate_series_plans_from_catalog.py — do not hand-edit.\n"
        + "# Source: artifacts/manga/MANGA_FULL_CATALOG_PLAN.md\n"
        + "# Routing: config/manga/format_routing.yaml\n"
        + "# Schema: schemas/manga/series_plan.schema.json (v2.0.0)\n\n"
        + yaml.safe_dump(plan, sort_keys=False, default_flow_style=False, allow_unicode=True),
        encoding="utf-8",
    )
    return out_path


# ─── CLI ────────────────────────────────────────────────────────────────────


def _filter(rows: Iterable[dict[str, Any]], teacher: str | None, locale: str | None) -> list[dict[str, Any]]:
    out = []
    for r in rows:
        if teacher and r["teacher_id"] != teacher:
            continue
        if locale and r["locale"] != locale:
            continue
        out.append(r)
    return out


def _samples(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Pick 1 row per (teacher, locale) — used for first-pass review."""
    seen: set[tuple[str, str]] = set()
    out: list[dict[str, Any]] = []
    for r in rows:
        key = (r["teacher_id"], r["locale"])
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--catalog", default=str(CATALOG_PLAN))
    p.add_argument("--routing", default=str(ROUTING_CFG))
    p.add_argument("--out-root", default=str(OUT_ROOT))
    p.add_argument("--sample-root", default=str(SAMPLE_ROOT))
    p.add_argument("--samples-only", action="store_true",
                   help="Generate one plan per (teacher, locale) under _samples/ for first-pass review")
    p.add_argument("--teacher")
    p.add_argument("--locale", choices=VALID_LOCALES)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    rows = parse_catalog(Path(args.catalog))
    print(f"Parsed {len(rows)} rows from {args.catalog}")

    rows = _filter(rows, args.teacher, args.locale)
    if args.samples_only:
        rows = _samples(rows)

    if not rows:
        print("No rows match filters.")
        return 0

    routing = _load_yaml(Path(args.routing))
    schema = _load_schema()

    out_root = Path(args.sample_root) if args.samples_only else Path(args.out_root)

    written = 0
    failed: list[tuple[str, list[str]]] = []
    for row in rows:
        plan = build_plan(row, routing)
        errors = validate_plan(plan, schema)
        if errors:
            failed.append((plan["series_id"], errors))
            continue
        if args.dry_run:
            print(f"[dry-run] {plan['locale']:6} {plan['master_format']:25} {plan['series_id']}")
        else:
            path = _write_plan(out_root, plan)
            written += 1
            print(f"✓ wrote {path.relative_to(REPO)}")

    if failed:
        print()
        print(f"❌ {len(failed)} plans failed schema validation:")
        for sid, errs in failed[:10]:
            print(f"   - {sid}")
            for e in errs[:3]:
                print(f"       {e}")
        return 1

    print()
    print(f"✓ {written} plans written ({len(rows)} candidates, 0 failures)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
