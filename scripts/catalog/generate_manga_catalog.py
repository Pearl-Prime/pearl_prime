#!/usr/bin/env python3
"""
Manga Catalog Generator (Pearl Prime locales)
=============================================

Materializes the brand × genre allocation matrix in
config/manga/brand_genre_allocation.yaml into per-locale manga catalog
CSVs. Catalog/queue artifacts only — no panel generation, no LoRA
training, no ComfyUI calls, no book assembly, no LLM calls.

Series count per (brand, genre) cell:
    series_count = max(1, round(allocation_pct / 10))

Schema (23 columns, planned in
docs/MANGA_CATALOG_PLAN_EN_US_JA_JP_ZH_TW_ZH_CN_2026-04-28.md §5):
  locale, market, brand, brand_locale_name, series_id, series_title,
  genre, is_tentpole, genre_allocation_pct, series_format,
  chapters_per_volume, cadence_weeks, visual_grammar, emotional_engine,
  serialization_engine, pacing_profile_ref, lora_plan_ref,
  character_pipeline_ref, pipeline_route, readiness_status,
  output_target_path, notes, blockers

Title policy: locale-native title synthesis is out of scope. Per the
established Pearl Prime catalog rule, series_title is left blank with
notes=needs_title_synthesis_locale_native (no LLM fallback).

Usage:
  python3 scripts/catalog/generate_manga_catalog.py \\
    --locales en_US,ja_JP \\
    --output-dir artifacts/catalog/manga/
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

# ── Path resolution ─────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parents[2]
_MAIN_REPO = Path("/Users/ahjan/phoenix_omega")
if not (REPO_ROOT / "config" / "manga").exists() and (_MAIN_REPO / "config" / "manga").exists():
    CONFIG_ROOT = _MAIN_REPO
else:
    CONFIG_ROOT = REPO_ROOT

# ── Constants ───────────────────────────────────────────────────────────────
MANGA_PIPELINE_ROUTE = (
    "MANGA_PIPELINE_TBD — see docs/MANGA_CATALOG_PLAN_EN_US_JA_JP_ZH_TW_ZH_CN_2026-04-28.md §7"
)

LOCALE_TO_MARKET = {"en_US": "us", "ja_JP": "japan", "zh_TW": "taiwan", "zh_CN": "china"}

LOCALE_TO_NAMES_KEY = {
    "en_US": "english_global",
    "ja_JP": "japan",
    "zh_TW": "taiwan",
    "zh_CN": "china",
}

# Cadence map: chapters_per_series_per_month → cadence_weeks (rough integer)
def cadence_weeks(chapters_per_month: float) -> int:
    if chapters_per_month <= 0:
        return 8
    weeks_per_chapter = 4.0 / chapters_per_month
    return max(1, round(weeks_per_chapter))

# Default series_format per locale + per-cell fallback
def series_format(locale: str, allocation_pct: int, is_tentpole: bool) -> str:
    """
    Locale-biased format selection per plan §4:
      ja_JP — print_manga for tentpole/heavy allocations (tankōbon route),
              web_manga for medium, webtoon_vertical for tertiary.
      en_US — web_manga for tentpole/heavy (KDP graphic novel EPUB),
              webtoon_vertical for the rest (WEBTOON Canvas).
      zh_TW — webtoon-vertical primary (LINE Webtoon TW), web_manga for
              tentpole + heavy allocations (BookWalker TW collected volumes).
      zh_CN — text-track baseline (manga lane is 0% mix today per
              catalog_generation_config.yaml), but design intent is
              web_manga primary if/when local-entity access lands.
    """
    if locale == "ja_JP":
        if is_tentpole or allocation_pct >= 25:
            return "print_manga"
        if allocation_pct >= 8:
            return "web_manga"
        return "webtoon_vertical"
    if locale == "zh_TW":
        if is_tentpole or allocation_pct >= 25:
            return "web_manga"
        return "webtoon_vertical"
    if locale == "zh_CN":
        if is_tentpole or allocation_pct >= 25:
            return "web_manga"
        if allocation_pct >= 10:
            return "web_manga"
        return "webtoon_vertical"
    # en_US
    if is_tentpole or allocation_pct >= 25:
        return "web_manga"
    return "webtoon_vertical"

COLUMNS = [
    "locale", "market", "brand", "brand_locale_name", "series_id", "series_title",
    "genre", "is_tentpole", "genre_allocation_pct", "series_format",
    "chapters_per_volume", "cadence_weeks", "visual_grammar", "emotional_engine",
    "serialization_engine", "pacing_profile_ref", "lora_plan_ref",
    "character_pipeline_ref", "pipeline_route", "readiness_status",
    "output_target_path", "notes", "blockers",
]


# ── Loaders ─────────────────────────────────────────────────────────────────
def _load(rel: str) -> Any:
    with open(CONFIG_ROOT / rel, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _sha256(rel: str) -> str:
    h = hashlib.sha256()
    with open(CONFIG_ROOT / rel, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_inputs() -> dict:
    sources = {
        "allocation":         "config/manga/brand_genre_allocation.yaml",
        "canonical_genres":   "config/manga/canonical_genre_list.yaml",
        "manga_taxonomy":     "config/manga/manga_taxonomy.yaml",
        "manga_pacing":       "config/manga/manga_pacing_by_genre.yaml",
        "brand_series_plan":  "config/manga/manga_brand_series_plan.yaml",
        "brand_lora_plans":   "config/manga/brand_lora_plans.yaml",
        "teacher_archetypes": "config/catalog_planning/teacher_brand_archetypes.yaml",
        "locale_brand_names": "config/catalog_planning/locale_brand_names.yaml",
    }
    return {k: {"data": _load(v), "sha256": _sha256(v), "path": v}
            for k, v in sources.items()}


# ── Indexes ────────────────────────────────────────────────────────────────
def index_genres(canonical: dict) -> dict[str, dict]:
    return {g["id"]: g for g in canonical.get("genres", [])}


def index_taxonomy_families(taxonomy: dict) -> dict[str, dict]:
    return {f["id"]: f for f in taxonomy.get("genre_families", [])}


def index_taxonomy_subgenres(taxonomy: dict) -> dict[str, dict]:
    return {s["id"]: s for s in taxonomy.get("subgenres", [])}


def index_pacing(pacing: dict) -> set[str]:
    return set((pacing.get("genre_pacing") or {}).keys())


def index_brand_teacher(archetypes: dict, allocation: dict) -> dict[str, dict]:
    """
    Returns {brand_id: {teacher_id, teacher_mode}} covering both:
      - the 12 global teacher brands (from teacher_brand_archetypes.yaml)
      - the 13 zh-specific brands (from allocation::zh_specific_brand_teacher)
    """
    out: dict[str, dict] = {
        e["brand_id"]: {"teacher_id": e["teacher"], "teacher_mode": True}
        for e in archetypes.get("teacher_brand_archetypes", [])
    }
    zh_map = allocation.get("zh_specific_brand_teacher") or {}
    for brand_id, info in zh_map.items():
        out[brand_id] = {
            "teacher_id": info.get("teacher", "ahjan"),
            "teacher_mode": bool(info.get("teacher_mode", False)),
        }
    return out


def locale_names_for(locale_brand_names: dict, locale: str) -> dict[str, str]:
    key = LOCALE_TO_NAMES_KEY.get(locale)
    out: dict[str, str] = {}
    if not key:
        return out
    for section in ("teacher_brands", "standard_brands"):
        block = locale_brand_names.get(section) or {}
        for brand_id, names in block.items():
            if isinstance(names, dict) and isinstance(names.get(key), str):
                out[brand_id] = names[key]
    return out


# ── Genre attribute resolution ─────────────────────────────────────────────
def resolve_genre_attrs(genre_id: str,
                        genre_index: dict[str, dict],
                        family_index: dict[str, dict],
                        subgenre_index: dict[str, dict],
                        pacing_keys: set[str],
                        taxonomy_fallback: dict[str, dict]) -> dict:
    """
    Resolve visual_grammar / emotional_engine / serialization_engine /
    pacing_profile_ref for a canonical genre id by walking taxonomy first,
    then canonical_genre_list.yaml::taxonomy_fallback for residual gaps.
    """
    g = genre_index.get(genre_id) or {}
    pacing_proxy = g.get("pacing_proxy")

    # Pacing key resolution: prefer direct match, then proxy, then null.
    if genre_id in pacing_keys:
        pacing_ref = f"genre_pacing.{genre_id}"
    elif pacing_proxy and pacing_proxy in pacing_keys:
        pacing_ref = f"genre_pacing.{pacing_proxy}"
    else:
        pacing_ref = ""  # unmapped → blocked_pacing

    # Engines + visual grammar from taxonomy genre_families (preferred)
    fam = family_index.get(genre_id) or {}
    if not fam:
        sub = subgenre_index.get(genre_id) or {}
        parent = sub.get("genre_family") or sub.get("parent_genre")
        if parent:
            fam = family_index.get(parent) or {}

    visual_grammars = fam.get("default_visual_grammars") or fam.get("visual_grammars") or []
    emotional_engines = fam.get("default_emotional_engines") or fam.get("emotional_engines") or []
    serialization_engines = (fam.get("default_serialization_engines")
                             or fam.get("serialization_engines") or [])

    # Fallback: backfill missing dimensions from canonical_genre_list.yaml
    fb = taxonomy_fallback.get(genre_id) or {}
    if not visual_grammars:
        visual_grammars = fb.get("default_visual_grammars") or []
    if not emotional_engines:
        emotional_engines = fb.get("default_emotional_engines") or []
    if not serialization_engines:
        serialization_engines = fb.get("default_serialization_engines") or []

    return {
        "visual_grammar": "|".join(visual_grammars),
        "emotional_engine": "|".join(emotional_engines),
        "serialization_engine": "|".join(serialization_engines),
        "pacing_profile_ref": pacing_ref,
    }


# ── Brand cadence resolution ───────────────────────────────────────────────
def brand_cadence(brand_series_plan: dict, brand: str) -> tuple[int, int]:
    """Returns (chapters_per_volume, cadence_weeks)."""
    bp = (brand_series_plan.get("brands") or {}).get(brand) or {}
    cpm = bp.get("chapters_per_series_per_month")
    if cpm is None:
        defaults = brand_series_plan.get("global_defaults") or {}
        cpm = defaults.get("chapters_per_series_per_month", 2)
    chapters_per_vol = bp.get("max_chapters_before_volume", 10)
    return chapters_per_vol, cadence_weeks(cpm)


def _strip_locale_suffix(brand: str) -> str:
    for suf in ("_tw", "_cn", "_hk", "_sg"):
        if brand.endswith(suf):
            return brand[: -len(suf)]
    return brand


# zh lattice + Taiwan-only marketing slugs → keys under brand_style_loras
# (trained teacher / standard styles). See docs/brand_admin/zh_*_distribution_guide.md.
_CATALOG_BRAND_STYLE_CANON: dict[str, str] = {
    "sleep_repair": "sleep_restoration",
    "panic_first_aid": "stabilizer",
    "gen_z_grounding": "digital_ground",
    "grief_companion": "body_memory",
    "inner_security": "relational_calm",
    "bright_presence": "stillness_press",
}


def _resolve_brand_style_key(style_loras: dict, brand: str) -> tuple[str, str]:
    """
    Returns (style_yaml_key, provenance_suffix) for brand_style_loras.
    provenance_suffix is empty when the row uses a direct YAML key match.
    """
    if brand in style_loras:
        return brand, ""
    base = _strip_locale_suffix(brand)
    if base in style_loras:
        if base != brand:
            return base, "shared via locale-suffix strip"
        return base, ""
    canon = _CATALOG_BRAND_STYLE_CANON.get(base)
    if canon and canon in style_loras:
        return canon, f"catalog style map {base!r}→{canon!r}"
    return "", ""


def lora_refs(lora_plans: dict, brand: str, teacher: str | None) -> tuple[str, str]:
    """
    Returns (lora_plan_ref, character_pipeline_ref).

    Brand style resolution:
      1. Try brand_id directly (covers the 12 global teacher brands).
      2. Try stripping locale suffix (_tw, _cn, _hk, _sg) and matching base
         brand (e.g. stabilizer_tw → stabilizer); when matched, mark in the
         ref so downstream knows it's a shared style.
      3. Try catalog marketing-base → trained style key map (zh lattice +
         bright_presence_tw base), per V1.1 Q4 blocked_lora-first cleanup.
      4. Otherwise blank → flagged as blocked_lora.

    Character resolution: teacher_id direct lookup; blank if missing.
    """
    style_loras = (lora_plans.get("brand_style_loras") or {})
    char_loras = (lora_plans.get("character_loras") or {})

    sk, prov = _resolve_brand_style_key(style_loras, brand)
    if sk:
        lora_ref = (
            f"brand_lora_plans.brand_style_loras.{sk} ({prov})"
            if prov
            else f"brand_lora_plans.brand_style_loras.{sk}"
        )
    else:
        lora_ref = ""

    if teacher and teacher in char_loras:
        char_ref = f"brand_lora_plans.character_loras.{teacher}"
    else:
        char_ref = ""

    return lora_ref, char_ref


# ── Row builder ────────────────────────────────────────────────────────────
def series_count_for(allocation_pct: int) -> int:
    return max(1, round(allocation_pct / 10))


def build_rows_for_locale(locale: str, inputs: dict) -> tuple[list[dict], dict]:
    market_id = LOCALE_TO_MARKET[locale]
    alloc = (inputs["allocation"]["data"]
             .get("allocations") or {}).get(locale) or {}
    tentpole_map = (inputs["allocation"]["data"]
                    .get("brand_tentpole") or {})
    divergence_policy = (inputs["allocation"]["data"]
                         .get("tentpole_divergence_policy") or {})

    genre_index = index_genres(inputs["canonical_genres"]["data"])
    family_index = index_taxonomy_families(inputs["manga_taxonomy"]["data"])
    subgenre_index = index_taxonomy_subgenres(inputs["manga_taxonomy"]["data"])
    pacing_keys = index_pacing(inputs["manga_pacing"]["data"])
    taxonomy_fallback = (inputs["canonical_genres"]["data"]
                         .get("taxonomy_fallback") or {})
    brand_teacher = index_brand_teacher(
        inputs["teacher_archetypes"]["data"],
        inputs["allocation"]["data"])
    locale_names = locale_names_for(inputs["locale_brand_names"]["data"], locale)

    rows: list[dict] = []
    breakdown: dict[str, int] = {}

    for brand, cells in alloc.items():
        bt = brand_teacher.get(brand, {})
        teacher = bt.get("teacher_id", "")
        teacher_mode = bool(bt.get("teacher_mode", True))
        brand_locale_name = locale_names.get(brand, "")
        chapters_per_vol, cadence_wk = brand_cadence(
            inputs["brand_series_plan"]["data"], brand)
        lora_ref, char_ref = lora_refs(
            inputs["brand_lora_plans"]["data"], brand, teacher)
        tentpole_genre = tentpole_map.get(brand, "")

        for genre, pct in cells.items():
            attrs = resolve_genre_attrs(
                genre, genre_index, family_index, subgenre_index, pacing_keys,
                taxonomy_fallback)
            n_series = series_count_for(pct)
            is_tentpole = (genre == tentpole_genre)

            blockers: list[str] = []
            if not lora_ref:
                blockers.append("needs_lora_plan")
            if not char_ref:
                blockers.append("needs_character_lora")
            if not attrs["pacing_profile_ref"]:
                blockers.append("needs_pacing_contract")
            if not (attrs["visual_grammar"] and attrs["emotional_engine"]):
                blockers.append("needs_taxonomy_engines")

            readiness = "ready" if not blockers else (
                "blocked_lora" if "needs_lora_plan" in blockers
                else "blocked_character_lora" if "needs_character_lora" in blockers
                else "blocked_pacing" if "needs_pacing_contract" in blockers
                else "blocked_archetype"
            )

            notes_parts: list[str] = [f"allocation_pct={pct}", f"series_count={n_series}"]
            if is_tentpole:
                notes_parts.append("tentpole_match")
            elif tentpole_genre and pct == max(cells.values()):
                # This row is the matrix Primary but doesn't match the tentpole.
                # Check the divergence policy: if the (brand, locale) is registered
                # as `coexist`, the divergence is intentional and we emit a
                # different (non-blocking) tag.
                policy_decision = (divergence_policy.get(brand, {})
                                   .get(locale, {})
                                   .get("decision"))
                if policy_decision == "coexist":
                    notes_parts.append(
                        f"intentional_portfolio_divergence:matrix_primary={genre},tentpole={tentpole_genre}"
                    )
                else:
                    notes_parts.append(
                        f"tentpole_mismatch:matrix_primary={genre},tentpole={tentpole_genre}"
                    )
            notes_parts.append("needs_title_synthesis_locale_native")

            for idx in range(1, n_series + 1):
                series_id = f"{brand}_{genre}_{idx:02d}"
                fmt = series_format(locale, pct, is_tentpole)
                row = {
                    "locale": locale,
                    "market": market_id,
                    "brand": brand,
                    "brand_locale_name": brand_locale_name,
                    "series_id": series_id,
                    "series_title": "",  # locale-native synthesis is a separate task
                    "genre": genre,
                    "is_tentpole": "true" if is_tentpole else "false",
                    "genre_allocation_pct": pct,
                    "series_format": fmt,
                    "chapters_per_volume": chapters_per_vol,
                    "cadence_weeks": cadence_wk,
                    "visual_grammar": attrs["visual_grammar"],
                    "emotional_engine": attrs["emotional_engine"],
                    "serialization_engine": attrs["serialization_engine"],
                    "pacing_profile_ref": attrs["pacing_profile_ref"],
                    "lora_plan_ref": lora_ref,
                    "character_pipeline_ref": char_ref,
                    "pipeline_route": MANGA_PIPELINE_ROUTE,
                    "readiness_status": readiness,
                    "output_target_path": f"artifacts/manga/{locale}/{brand}/{series_id}/",
                    "notes": "; ".join(notes_parts),
                    "blockers": ";".join(blockers),
                }
                rows.append(row)
                breakdown[readiness] = breakdown.get(readiness, 0) + 1

    return rows, breakdown


# ── CSV writer ─────────────────────────────────────────────────────────────
def write_csv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def git_short_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short=12", "HEAD"],
            cwd=str(REPO_ROOT), stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


# ── Main ───────────────────────────────────────────────────────────────────
def main() -> int:
    parser = argparse.ArgumentParser(description="Manga catalog generator (en_US + ja_JP)")
    parser.add_argument("--locales", default="en_US,ja_JP",
                        help="Comma-separated locales.")
    parser.add_argument("--output-dir", default="artifacts/catalog/manga/",
                        help="Output directory.")
    args = parser.parse_args()

    locales = [s.strip() for s in args.locales.split(",") if s.strip()]
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    inputs = load_inputs()

    summary = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generator_version": git_short_sha(),
        "totals": {},
        "preconditions": {
            "allocation_matrix_authority": "config/manga/brand_genre_allocation.yaml",
            "genre_reconciliation_completed": True,
            "reconciliation_strategy": "option_C_coexist (mono-genre = tentpole, matrix = portfolio)",
            "zh_tw_zh_cn_lora": (
                "V1.1 Q4: zh marketing-base slugs resolve to trained brand_style_loras keys; "
                "adi_da character_loras entry gates bright_presence_tw"
            ),
        },
        "scope_excluded": [
            "ComfyUI image generation",
            "panel composition / page layout rendering",
            "LoRA training",
            "book / volume assembly",
            "any LLM call",
        ],
        "source_files": [
            {"path": v["path"], "sha256": v["sha256"]}
            for v in inputs.values()
        ],
    }

    for locale in locales:
        rows, breakdown = build_rows_for_locale(locale, inputs)
        out_csv = out_dir / f"{locale}_manga_catalog.csv"
        write_csv(rows, out_csv)

        ready = breakdown.get("ready", 0)
        blocked = sum(v for k, v in breakdown.items() if k != "ready")
        summary["totals"][locale] = {
            "rows": len(rows),
            "ready": ready,
            "blocked": blocked,
            "by_status": dict(sorted(breakdown.items())),
        }
        print(f"[{locale}] rows={len(rows)} ready={ready} blocked={blocked} → {out_csv}")

    summary_path = out_dir / "manga_catalog_summary.json"
    with open(summary_path, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=False)
    print(f"[summary] {summary_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
