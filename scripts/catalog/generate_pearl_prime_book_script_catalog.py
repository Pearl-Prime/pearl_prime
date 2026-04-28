#!/usr/bin/env python3
"""
Pearl Prime Book Script Catalog Generator (wrapper)
====================================================

Emits per-locale Pearl Prime book script catalog CSVs for en_US, ja_JP,
zh_TW, zh_CN. This script is a thin wrapper around the existing catalog
loaders in scripts/catalog/generate_full_catalog.py — it does NOT mutate
that file. The Pearl Prime row schema is locked here; the upstream
generator's own row schema (covering ebook/manga/audiobook/podcast)
remains untouched.

Hard contract — this generator does NOT:
  - call any LLM (paid or free)
  - assemble, render, or generate manuscripts / chapters / sections
  - write manga catalog files (.yaml or .csv under artifacts/catalog/manga/)
  - mutate atom banks or registry topics

Each row stores the Pearl Prime structural lock:
  - section_plan_id        = pearl_prime_12x10x5
  - variant_pool_size      = 5
  - bestseller_overlay_ref = docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md
  - selection_strategy     = deterministic_by_seed
  - pipeline_route         = scripts/run_pipeline.py --pipeline-mode spine

High-confidence filter:
  Composite (teacher.topic_score + teacher.persona_score) / 2 >= 0.70.
  Rows with default-0.5 scoring on either dimension are emitted with
  readiness_status=blocked_score and blockers=needs_score (per dev brief).

Usage:
  python3 scripts/catalog/generate_pearl_prime_book_script_catalog.py \\
    --locales en_US,ja_JP,zh_TW,zh_CN \\
    --output-dir artifacts/catalog/pearl_prime_book_script_catalogs/
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml  # required; install via: pip install pyyaml

# ── Path resolution ─────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parents[2]
_MAIN_REPO = Path("/Users/ahjan/phoenix_omega")
if not (REPO_ROOT / "config" / "manga").exists() and (_MAIN_REPO / "config" / "manga").exists():
    CONFIG_ROOT = _MAIN_REPO
else:
    CONFIG_ROOT = REPO_ROOT

# ── Pearl Prime structural locks ────────────────────────────────────────────
SECTION_PLAN_ID = "pearl_prime_12x10x5"
VARIANT_POOL_SIZE = 5
BESTSELLER_OVERLAY_REF = "docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md"
SELECTION_STRATEGY = "deterministic_by_seed"
PIPELINE_ROUTE = "scripts/run_pipeline.py --pipeline-mode spine"
DEFAULT_RUNTIME_FORMAT = "standard_book"
DEFAULT_DURATION_BAND = "standard"  # 12ch x ~6kw/ch nominal
SCORE_THRESHOLD_STRONG = 0.70  # per teacher_topic_persona_scores.yaml score_bands

# Locale → market_id in market_catalog_registry.yaml
LOCALE_TO_MARKET = {
    "en_US": "us",
    "ja_JP": "japan",
    "zh_TW": "taiwan",
    "zh_CN": "china",
}

# Pearl Prime catalog row column order — exact spec from dev brief
COLUMNS = [
    "locale",
    "market",
    "brand",
    "brand_locale_name",
    "title",
    "subtitle",
    "topic",
    "persona",
    "teacher_id",
    "teacher_mode",
    "runtime_format",
    "duration_band",
    "section_plan_id",
    "variant_pool_size",
    "bestseller_overlay_ref",
    "selection_strategy",
    "pipeline_route",
    "readiness_status",
    "required_source_atoms",
    "required_registry_topic",
    "output_target_path",
    "notes",
    "blockers",
]


# ── Loaders ─────────────────────────────────────────────────────────────────
def _load_yaml(rel: str) -> Any:
    path = CONFIG_ROOT / rel
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _sha256(rel: str) -> str:
    path = CONFIG_ROOT / rel
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_all_inputs() -> dict:
    """Load every config file consumed by this generator."""
    sources = {
        "market_registry":   "config/catalog/market_catalog_registry.yaml",
        "catalog_config":    "config/catalog/catalog_generation_config.yaml",
        "topics":            "config/catalog_planning/canonical_topics.yaml",
        "personas":          "config/catalog_planning/canonical_personas.yaml",
        "scores":            "config/catalog_planning/teacher_topic_persona_scores.yaml",
        "teacher_archetypes": "config/catalog_planning/teacher_brand_archetypes.yaml",
        "matrix_zh":         "config/catalog_planning/brand_teacher_matrix_zh.yaml",
        "locale_brand_names": "config/catalog_planning/locale_brand_names.yaml",
        "format_registry":   "config/format_selection/format_registry.yaml",
        "canonical_genres":  "config/manga/canonical_genre_list.yaml",
    }
    return {k: {"data": _load_yaml(v), "sha256": _sha256(v), "path": v}
            for k, v in sources.items()}


# ── Brand → teacher resolution ──────────────────────────────────────────────
def build_brand_teacher_map(inputs: dict) -> dict[str, dict]:
    """
    Returns {brand_id: {"teacher_id": ..., "teacher_mode": bool}} for every brand
    referenced by any of the four target markets.
    """
    teacher_brand_archetypes = inputs["teacher_archetypes"]["data"].get(
        "teacher_brand_archetypes", []
    )
    matrix_zh = inputs["matrix_zh"]["data"].get("brands", {})

    out: dict[str, dict] = {}

    # 12 teacher-mode brands (one teacher each)
    for entry in teacher_brand_archetypes:
        out[entry["brand_id"]] = {
            "teacher_id": entry["teacher"],
            "teacher_mode": True,
        }

    # zh-specific standard brands (teacher_mode=False per owner decision Q2)
    for brand_id, cfg in matrix_zh.items():
        teachers = cfg.get("teachers", []) or ["ahjan"]
        out[brand_id] = {
            "teacher_id": teachers[0],
            "teacher_mode": False,
        }

    # Taiwan-only Adi Da teacher-mode brand
    out["bright_presence_tw"] = {
        "teacher_id": "adi_da",
        "teacher_mode": True,
    }

    return out


_LOCALE_TO_NAMES_KEY = {
    "en_US": "english_global",
    "ja_JP": "japan",
    "zh_TW": "taiwan",
    "zh_CN": "china",
}


def load_locale_brand_names(inputs: dict, locale: str) -> dict[str, str]:
    """Read locale-native brand names from teacher_brands + standard_brands sections."""
    data = inputs["locale_brand_names"]["data"] or {}
    key = _LOCALE_TO_NAMES_KEY.get(locale)
    if not key:
        return {}
    out: dict[str, str] = {}
    for section in ("teacher_brands", "standard_brands"):
        block = data.get(section) or {}
        if not isinstance(block, dict):
            continue
        for brand_id, names in block.items():
            if isinstance(names, dict) and key in names and isinstance(names[key], str):
                out[brand_id] = names[key]
    return out


# ── Scoring filter ──────────────────────────────────────────────────────────
def composite_score(scores: dict, teacher_id: str, topic: str, persona: str
                    ) -> tuple[float, bool, bool]:
    """
    Returns (composite, topic_explicit, persona_explicit).
    *_explicit = True only when the score is declared in the YAML, not the default.
    """
    teachers = scores.get("teachers", {})
    default = scores.get("default_score", 0.5)
    t = teachers.get(teacher_id, {})
    topic_scores = t.get("topic_scores", {}) or {}
    persona_scores = t.get("persona_scores", {}) or {}

    topic_explicit = topic in topic_scores
    persona_explicit = persona in persona_scores
    ts = topic_scores.get(topic, default)
    ps = persona_scores.get(persona, default)

    formula = scores.get("composite_formula", "average")
    if formula == "min":
        comp = min(ts, ps)
    else:  # average (default)
        comp = (ts + ps) / 2.0
    return (comp, topic_explicit, persona_explicit)


# ── Title / subtitle synthesis ──────────────────────────────────────────────
# Per dev brief: "If a title/subtitle cannot be synthesized from existing data,
# leave the field blank with notes: needs_title_synthesis — do NOT generate via API."
#
# config/catalog/catalog_generation_config.yaml::title_templates is English-only.
# Falling through to English templates for ja_JP/zh_TW/zh_CN produced
# 100% English titles in the non-English catalogs (validated in the first
# validation pass and recorded in validation_report.json). That is worse than
# blank — it misrepresents the catalog as locale-fit when it isn't.
#
# Synthesis is locale-gated: en_US uses templates; non-English locales leave
# title/subtitle blank with needs_title_synthesis until locale-native
# template files exist (e.g. config/catalog_planning/title_templates.ja_JP.yaml).
ENGLISH_TITLE_LOCALES = {"en_US"}


def pick_title_subtitle(catalog_config: dict, topic: str, persona: str,
                        locale: str, brand: str) -> tuple[str, str, str]:
    """
    Deterministic pick from English title_templates for English locales only.
    Non-English locales return blank with needs_title_synthesis (no LLM fallback).
    Returns (title, subtitle, note).
    """
    if locale not in ENGLISH_TITLE_LOCALES:
        return ("", "", "needs_title_synthesis_locale_native")
    templates = (catalog_config.get("title_templates") or {}).get(topic) or []
    if not templates:
        return ("", "", "needs_title_synthesis")
    seed = f"{locale}|{brand}|{topic}|{persona}".encode("utf-8")
    idx = int(hashlib.sha256(seed).hexdigest(), 16) % len(templates)
    tpl = templates[idx]
    title = tpl.get("title", "") or ""
    sub_pat = tpl.get("subtitle_pattern", "") or ""
    topic_disp = topic.replace("_", " ").title()
    subtitle = sub_pat.replace("{topic}", topic_disp)
    note = "" if (title and subtitle) else "needs_title_synthesis"
    return (title, subtitle, note)


# ── Kill-list filter ────────────────────────────────────────────────────────
def is_killed(catalog_config: dict, brand: str, topic: str, persona: str,
              locale: str, runtime_format: str) -> bool:
    kill = catalog_config.get("kill_list", {}) or {}
    for tp in kill.get("topic_persona_kills", []) or []:
        if tp.get("topic") == topic and tp.get("persona") == persona:
            return True
    for fl in kill.get("format_locale_kills", []) or []:
        if fl.get("format") == runtime_format and fl.get("locale") == locale:
            return True
    for bl in kill.get("brand_locale_kills", []) or []:
        if bl.get("brand") == brand and bl.get("locale") == locale:
            return True
    return False


# ── Atom / registry slot stubs ──────────────────────────────────────────────
# We do NOT touch atom banks here. We only emit the *expected* paths so the
# row clearly declares its dependencies. Atom existence is not validated at
# row-emit time; readiness_status reflects scoring only.
SECTION_TYPES_REPRESENTATIVE = ["scene", "depth", "teacher"]


def required_atoms_for(persona: str, topic: str) -> str:
    paths = [
        f"atoms/{persona}/anchored/{topic}/CANONICAL.txt",
    ] + [
        f"atoms/{persona}/{topic}/{st}/CANONICAL.txt"
        for st in SECTION_TYPES_REPRESENTATIVE
    ]
    return ";".join(paths)


def output_target_path(locale: str, brand: str, topic: str, persona: str,
                       teacher_id: str) -> str:
    return f"artifacts/books/{locale}/{brand}/{topic}_{persona}_{teacher_id}.json"


# ── Row builder ─────────────────────────────────────────────────────────────
def build_rows_for_locale(locale: str, inputs: dict,
                          brand_teacher: dict[str, dict],
                          locale_names: dict[str, str]) -> tuple[list[dict], dict]:
    """
    Returns (rows, status_breakdown) for this locale.
    status_breakdown: {readiness_status: count}.
    """
    market_id = LOCALE_TO_MARKET[locale]
    market = (inputs["market_registry"]["data"].get("markets") or {}).get(market_id) or {}
    brand_ids = market.get("brands") or []

    catalog_config = inputs["catalog_config"]["data"]
    topics = inputs["topics"]["data"].get("topics") or []
    personas = inputs["personas"]["data"].get("personas") or []
    # Restrict topics + personas to the active set declared in catalog_generation_config
    # (17 topics × 13 personas — same authority as ~800 high-confidence target).
    cfg_topics = catalog_config.get("topics") or topics
    cfg_personas = catalog_config.get("personas") or personas
    active_topics = [t for t in cfg_topics if t in set(topics)] or cfg_topics
    active_personas = [p for p in cfg_personas if p in set(personas)] or cfg_personas

    scores = inputs["scores"]["data"]

    rows: list[dict] = []
    status_counts: dict[str, int] = {}

    for brand in brand_ids:
        bt = brand_teacher.get(brand)
        if not bt:
            # Not in any known brand registry — still emit a row tagged as blocked.
            for topic in active_topics:
                for persona in active_personas:
                    if is_killed(catalog_config, brand, topic, persona,
                                 locale, DEFAULT_RUNTIME_FORMAT):
                        continue
                    rows.append(_blocked_brand_row(
                        locale, market_id, brand, topic, persona, locale_names))
                    status_counts["blocked_teacher"] = status_counts.get(
                        "blocked_teacher", 0) + 1
            continue

        teacher_id = bt["teacher_id"]
        teacher_mode = bt["teacher_mode"]

        for topic in active_topics:
            for persona in active_personas:
                if is_killed(catalog_config, brand, topic, persona,
                             locale, DEFAULT_RUNTIME_FORMAT):
                    continue

                comp, topic_explicit, persona_explicit = composite_score(
                    scores, teacher_id, topic, persona)

                # High-confidence filter:
                #   - If either dimension is missing scoring data (default 0.5),
                #     emit row with blocked_score / needs_score per owner Q4.
                #   - If both explicit but composite < strong threshold, drop.
                if not (topic_explicit and persona_explicit):
                    rows.append(_row(
                        locale, market_id, brand, teacher_id, teacher_mode,
                        topic, persona, comp,
                        catalog_config, locale_names,
                        readiness="blocked_score",
                        blockers="needs_score",
                        notes=(
                            f"composite={comp:.2f} "
                            f"(topic_explicit={topic_explicit}, "
                            f"persona_explicit={persona_explicit})"
                        ),
                    ))
                    status_counts["blocked_score"] = status_counts.get(
                        "blocked_score", 0) + 1
                    continue

                if comp < SCORE_THRESHOLD_STRONG:
                    # Below strong threshold and both dimensions explicit → not
                    # a high-confidence row. Filter out to keep catalog tight.
                    continue

                rows.append(_row(
                    locale, market_id, brand, teacher_id, teacher_mode,
                    topic, persona, comp,
                    catalog_config, locale_names,
                    readiness="ready",
                    blockers="",
                    notes=f"composite={comp:.2f}",
                ))
                status_counts["ready"] = status_counts.get("ready", 0) + 1

    return rows, status_counts


def _row(locale: str, market_id: str, brand: str, teacher_id: str,
         teacher_mode: bool, topic: str, persona: str, composite: float,
         catalog_config: dict, locale_names: dict[str, str],
         readiness: str, blockers: str, notes: str) -> dict:
    title, subtitle, title_note = pick_title_subtitle(
        catalog_config, topic, persona, locale, brand)
    extra_notes = "; ".join(x for x in (notes, title_note) if x)
    if title_note and readiness == "ready":
        # Title synthesis missing is a soft block — surface it but keep readiness ready
        # only if other gates pass; mark notes.
        pass

    return {
        "locale": locale,
        "market": market_id,
        "brand": brand,
        "brand_locale_name": locale_names.get(brand, ""),
        "title": title,
        "subtitle": subtitle,
        "topic": topic,
        "persona": persona,
        "teacher_id": teacher_id,
        "teacher_mode": "true" if teacher_mode else "false",
        "runtime_format": DEFAULT_RUNTIME_FORMAT,
        "duration_band": DEFAULT_DURATION_BAND,
        "section_plan_id": SECTION_PLAN_ID,
        "variant_pool_size": VARIANT_POOL_SIZE,
        "bestseller_overlay_ref": BESTSELLER_OVERLAY_REF,
        "selection_strategy": SELECTION_STRATEGY,
        "pipeline_route": PIPELINE_ROUTE,
        "readiness_status": readiness,
        "required_source_atoms": required_atoms_for(persona, topic),
        "required_registry_topic": f"registry/{topic}.yaml",
        "output_target_path": output_target_path(locale, brand, topic, persona, teacher_id),
        "notes": extra_notes,
        "blockers": blockers,
    }


def _blocked_brand_row(locale: str, market_id: str, brand: str,
                       topic: str, persona: str,
                       locale_names: dict[str, str]) -> dict:
    return {
        "locale": locale,
        "market": market_id,
        "brand": brand,
        "brand_locale_name": locale_names.get(brand, ""),
        "title": "",
        "subtitle": "",
        "topic": topic,
        "persona": persona,
        "teacher_id": "",
        "teacher_mode": "false",
        "runtime_format": DEFAULT_RUNTIME_FORMAT,
        "duration_band": DEFAULT_DURATION_BAND,
        "section_plan_id": SECTION_PLAN_ID,
        "variant_pool_size": VARIANT_POOL_SIZE,
        "bestseller_overlay_ref": BESTSELLER_OVERLAY_REF,
        "selection_strategy": SELECTION_STRATEGY,
        "pipeline_route": PIPELINE_ROUTE,
        "readiness_status": "blocked_teacher",
        "required_source_atoms": required_atoms_for(persona, topic),
        "required_registry_topic": f"registry/{topic}.yaml",
        "output_target_path": "",
        "notes": "no teacher mapping resolved for this brand",
        "blockers": "needs_teacher_mapping",
    }


# ── CSV writer ──────────────────────────────────────────────────────────────
def write_csv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


# ── Git short SHA for generator_version ─────────────────────────────────────
def git_short_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short=12", "HEAD"],
            cwd=str(REPO_ROOT), stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


# ── Main ────────────────────────────────────────────────────────────────────
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Pearl Prime book script catalog generator (wrapper)")
    parser.add_argument("--locales", default="en_US,ja_JP,zh_TW,zh_CN",
                        help="Comma-separated locales (primary tier first).")
    parser.add_argument("--output-dir", default="artifacts/catalog/pearl_prime_book_script_catalogs/",
                        help="Output directory for per-locale CSVs + summary JSON.")
    args = parser.parse_args()

    locales = [s.strip() for s in args.locales.split(",") if s.strip()]
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    inputs = load_all_inputs()
    brand_teacher = build_brand_teacher_map(inputs)

    summary = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generator_version": git_short_sha(),
        "totals": {},
        "preconditions": {
            "genre_reconciliation_completed": True,
            "pearl_prime_structure_locked": "12x10x5",
            "bestseller_overlay_ref": BESTSELLER_OVERLAY_REF,
        },
        "source_files": [
            {"path": v["path"], "sha256": v["sha256"]}
            for v in inputs.values()
        ],
    }

    for locale in locales:
        locale_names = load_locale_brand_names(inputs, locale)
        rows, breakdown = build_rows_for_locale(
            locale, inputs, brand_teacher, locale_names)
        out_csv = out_dir / f"{locale}_catalog.csv"
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

    summary_path = out_dir / "catalog_summary.json"
    with open(summary_path, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=False)
    print(f"[summary] {summary_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
