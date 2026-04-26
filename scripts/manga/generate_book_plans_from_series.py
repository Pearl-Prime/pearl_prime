#!/usr/bin/env python3
"""Generate v2 book_plan YAMLs from existing series_plan YAMLs.

Phase 1.5 catalog rebuild — sibling to generate_series_plans_from_catalog.py
(PR #642/#643). Reads each series_plan in config/source_of_truth/manga_series_plans/
and emits chapters_target book_plan YAMLs to
config/source_of_truth/manga_book_plans/<series_id>/<book_id>.yaml.

Each book_plan represents one shippable unit:
- color_vertical_webtoon → one episode (book_id = ep_001 .. ep_NN)
- bw_page_manga / color_page_manga → one chapter (book_id = chapter_01 .. chapter_NN)
- direct_self_help_illustrated → one essay (book_id = essay_01 .. essay_NN)

Inherits master_format, flatten_exports, target_platforms, locale, default_locale
from the parent series_plan. Per-book localized_titles are left empty for now —
populated later by the title-generation pass.

Usage:
    # Dry-run for all series
    python3 scripts/manga/generate_book_plans_from_series.py --dry-run

    # Sample one series per locale
    python3 scripts/manga/generate_book_plans_from_series.py --samples-only

    # Full generation
    python3 scripts/manga/generate_book_plans_from_series.py

    # One series only
    python3 scripts/manga/generate_book_plans_from_series.py \\
        --series-id stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying

Validates each book_plan against the schema. Exits non-zero on any failure.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable

REPO = Path(__file__).resolve().parents[2]
SERIES_ROOT = REPO / "config" / "source_of_truth" / "manga_series_plans"
BOOK_ROOT = REPO / "config" / "source_of_truth" / "manga_book_plans"
SAMPLE_ROOT = BOOK_ROOT / "_samples"
BOOK_SCHEMA = REPO / "schemas" / "manga" / "book_plan.schema.json"


# ─── helpers ────────────────────────────────────────────────────────────────


def _load_yaml(path: Path) -> dict[str, Any]:
    import yaml  # type: ignore

    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _book_id_prefix(master_format: str) -> str:
    return {
        "color_vertical_webtoon": "ep",
        "bw_page_manga": "chapter",
        "color_page_manga": "chapter",
        "direct_self_help_illustrated": "essay",
    }.get(master_format, "ep")


def _book_id(master_format: str, n: int) -> str:
    """ep_001 / chapter_01 / essay_01."""
    prefix = _book_id_prefix(master_format)
    if prefix == "ep":
        return f"{prefix}_{n:03d}"
    return f"{prefix}_{n:02d}"


def _page_target_count(master_format: str) -> int:
    """Default page/segment target per book per format."""
    return {
        "color_vertical_webtoon": 40,        # 30-50 panels per episode (webtoon convention)
        "bw_page_manga": 20,                  # 18-22 pages per chapter (yokoyomi convention)
        "color_page_manga": 20,
        "direct_self_help_illustrated": 8,    # short illustrated essay
    }.get(master_format, 20)


def _engine_for_topic(topic: str) -> str | None:
    """Map series topic → narrative engine when there's a clean fit.

    Engines drive content (NOT marketing) per series_plan schema.
    Falls back to None for topics without a canonical engine — those
    inherit nothing and the chapter-writer agent picks per book.
    """
    return {
        "anxiety": "false_alarm",
        "social_anxiety": "false_alarm",
        "sleep_anxiety": "spiral",
        "panic": "false_alarm",
        "burnout": "overwhelm",
        "overthinking": "spiral",
        "depression": "spiral",
        "shame": "shame",
        "comparison": "comparison",
        "imposter_syndrome": "comparison",
        "self_worth": "comparison",
        "grief": "grief",
        "compassion_fatigue": "overwhelm",
        "boundaries": "watcher",
        "courage": "watcher",
        "financial_anxiety": "spiral",
        "financial_stress": "overwhelm",
        "somatic_healing": "watcher",
    }.get(topic)


# ─── plan construction ────────────────────────────────────────────────────


def build_book_plan(series: dict[str, Any], n: int) -> dict[str, Any]:
    """Construct a v2 book_plan dict for episode/chapter/essay number n.

    Inherits master_format / flatten_exports / target_platforms / locale
    from the parent series_plan. Per-book overrides go in follow-up
    chapter-writer passes.
    """
    master_format = series.get("master_format") or series.get("format")
    book_id = _book_id(master_format, n)

    plan: dict[str, Any] = {
        "book_plan_schema": "2.0.0",
        "book_id": book_id,
        "series_id": series["series_id"],
        "format": master_format,
        "master_format": master_format,
        "flatten_exports": list(series.get("flatten_exports") or []),
        "panel_layout_template": series["panel_layout_template"],
        "target_platforms": list(series.get("target_platforms") or []),
        "title": f"{series.get('title', series['series_id'])} — {book_id}",
        "localized_titles": {series["locale"]: f"{series.get('title', series['series_id'])} — {book_id}"},
        "page_target_count": _page_target_count(master_format),
        "ai_disclosure_required": series.get("ai_disclosure_required", True),
    }

    engine = _engine_for_topic(series.get("topic", ""))
    if engine:
        plan["engine"] = engine

    return plan


# ─── validation ────────────────────────────────────────────────────────────


def validate_plan(plan: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    try:
        import jsonschema  # type: ignore
    except ImportError:
        return [f"missing required: {r}" for r in schema.get("required") or [] if r not in plan]
    v = jsonschema.Draft202012Validator(schema)
    return [
        f"{'.'.join(str(p) for p in err.absolute_path)}: {err.message}"
        for err in v.iter_errors(plan)
    ]


# ─── filesystem ────────────────────────────────────────────────────────────


def _write_book_plan(out_root: Path, series_id: str, plan: dict[str, Any]) -> Path:
    import yaml  # type: ignore

    series_dir = out_root / series_id
    series_dir.mkdir(parents=True, exist_ok=True)
    out_path = series_dir / f"{plan['book_id']}.yaml"
    out_path.write_text(
        "# Auto-generated by scripts/manga/generate_book_plans_from_series.py — do not hand-edit.\n"
        "# Inherited from: parent series_plan\n"
        "# Schema: schemas/manga/book_plan.schema.json (v2.0.0)\n\n"
        + yaml.safe_dump(plan, sort_keys=False, default_flow_style=False, allow_unicode=True),
        encoding="utf-8",
    )
    return out_path


def iter_series_plans(series_root: Path = SERIES_ROOT) -> Iterable[Path]:
    if not series_root.exists():
        return
    for locale_dir in sorted(series_root.iterdir()):
        if not locale_dir.is_dir() or locale_dir.name == "_samples":
            continue
        yield from sorted(locale_dir.glob("*.yaml"))


# ─── CLI ────────────────────────────────────────────────────────────────────


def _samples_filter(series_paths: Iterable[Path]) -> list[Path]:
    """Pick one series per locale — first alphabetically."""
    seen: set[str] = set()
    out: list[Path] = []
    for p in series_paths:
        locale = p.parent.name
        if locale in seen:
            continue
        seen.add(locale)
        out.append(p)
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--samples-only", action="store_true")
    p.add_argument("--series-id", help="Generate only this series' book_plans")
    p.add_argument("--locale", help="Restrict to this locale")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument(
        "--series-root",
        type=Path,
        default=SERIES_ROOT,
        help=f"Root directory of series_plan YAMLs (default: {SERIES_ROOT.relative_to(REPO)})",
    )
    p.add_argument(
        "--book-root",
        type=Path,
        default=BOOK_ROOT,
        help=f"Output root directory for book_plan YAMLs (default: {BOOK_ROOT.relative_to(REPO)})",
    )
    args = p.parse_args()

    series_paths = list(iter_series_plans(args.series_root))
    if not series_paths:
        print(f"No series_plans found under {args.series_root}")
        return 0

    if args.locale:
        series_paths = [p for p in series_paths if p.parent.name == args.locale]
    if args.series_id:
        series_paths = [p for p in series_paths if p.stem == args.series_id]

    if args.samples_only:
        series_paths = _samples_filter(series_paths)

    if not series_paths:
        print("No series match filters.")
        return 0

    schema = json.loads(BOOK_SCHEMA.read_text(encoding="utf-8"))
    out_root = SAMPLE_ROOT if args.samples_only else args.book_root

    written = 0
    failed: list[tuple[str, list[str]]] = []
    for series_path in series_paths:
        series = _load_yaml(series_path)
        chapters = int(series.get("chapters_target") or 0)
        if chapters <= 0:
            print(f"⚠️  {series_path.name}: no chapters_target — skipping")
            continue

        for n in range(1, chapters + 1):
            plan = build_book_plan(series, n)
            errors = validate_plan(plan, schema)
            if errors:
                failed.append((f"{series['series_id']}::{plan['book_id']}", errors))
                continue
            if args.dry_run:
                if n == 1:
                    print(f"[dry-run] {series['series_id']}: would write {chapters} book_plans "
                          f"({plan['book_id']} … {_book_id(series.get('master_format', 'color_vertical_webtoon'), chapters)})")
            else:
                _write_book_plan(out_root, series["series_id"], plan)
                written += 1

    if failed:
        print()
        print(f"❌ {len(failed)} book_plans failed schema validation:")
        for sid, errs in failed[:10]:
            print(f"   - {sid}")
            for e in errs[:3]:
                print(f"       {e}")
        return 1

    print()
    if args.dry_run:
        print(f"✓ dry-run complete — would generate book_plans for {len(series_paths)} series")
    else:
        print(f"✓ {written} book_plans written across {len(series_paths)} series")
    return 0


if __name__ == "__main__":
    sys.exit(main())
