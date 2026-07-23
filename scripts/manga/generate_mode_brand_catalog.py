#!/usr/bin/env python3
"""Generate manga series plans for an active teacher or music brand.

Teacher brands normally enter through the strategic 37-brand planners. Music
brands live in their own registry, so this command gives them the same 15-genre
catalog surface without contaminating the frozen canonical brand list.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from phoenix_v4.manga.mode.catalog import active_music_brands, apply_brand_mode
from scripts.manga.run_m7_wave_a import (
    emit_series_plan_yaml,
    load_routing,
    validate_plan,
    load_schema,
)
from scripts.manga.generate_catalog_plan_from_strategic import VALID_GENRES, VALID_LOCALES


def build_mode_catalog(
    *, brand_id: str, locale: str, repo_root: Path = REPO
) -> list[dict]:
    music = active_music_brands(repo_root)
    if brand_id not in music:
        raise ValueError(f"{brand_id!r} is not an active music brand")
    routing = load_routing()
    return [
        apply_brand_mode(emit_series_plan_yaml(
            brand_id=brand_id,
            teacher_id=None,
            musician_id=music[brand_id],
            locale=locale,
            genre=genre,
            series_slug="series01",
            routing=routing,
        ), repo_root=repo_root)
        for genre in VALID_GENRES
    ]


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--brand", required=True)
    p.add_argument("--locale", required=True, choices=VALID_LOCALES)
    p.add_argument("--out-root", type=Path, default=REPO / "config/source_of_truth/manga_series_plans")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args(argv)
    plans = build_mode_catalog(brand_id=args.brand, locale=args.locale)
    schema = load_schema()
    for plan in plans:
        errors = validate_plan(plan, schema)
        if errors:
            raise SystemExit(f"{plan['series_id']}: {errors[0]}")
        if args.dry_run:
            print(f"[dry-run] {plan['series_id']} mode={plan['mode']}")
            continue
        out = args.out_root / args.locale / f"{plan['series_id']}.yaml"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(yaml.safe_dump(plan, sort_keys=False, allow_unicode=True), encoding="utf-8")
        print(out.relative_to(REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
