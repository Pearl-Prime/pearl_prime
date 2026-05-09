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

Structural variation axes (FEATURE-KNOB-CATALOG-VARIATION-V1-01 P0-1):
  Each row carries the canonical variation tuple consumed by
  ``phoenix_v4/planning/variation_selector.py`` so the catalog reflects
  what ``run_pipeline`` will actually execute:

    - ``angle_id``           — declared in ``config/angles/angle_registry.yaml`` (`angles:` keys)
    - ``motif_id``           — declared in ``config/source_of_truth/recurring_motif_bank.yaml``
    - ``book_structure_id``  — declared in ``config/source_of_truth/book_structure_archetypes.yaml``
    - ``journey_shape_id``   — declared in ``config/source_of_truth/journey_shapes.yaml``
    - ``variation_signature``— deterministic short SHA256 over the canonical tuple
                               (see ``phoenix_v4/planning/schema_v4.compute_variation_signature``)

  Selection is deterministic via the same SSOT-driven path as the runtime
  pipeline. ``angle_id`` resolves through ``catalog_planner_resolution.topic_angle_map``
  when declared (P0-2 SSOT); for topics not yet listed in the map, a deterministic
  SHA256 over (topic|persona) selects from the registry-declared angle keys so
  every row carries a registry-valid ``angle_id`` without mutating the
  registry (any new mapping requires AMENDMENT per cap entry).

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

# Active/inactive brand classifier consumer (PR #972 SSOT, mirrors PR #982 brand_admin pattern).
# Inactive brands are skipped with a single log line; spec: docs/specs/ACTIVE_BRAND_SSOT_V1_SPEC.md.
from scripts.catalog._active_brand_filter import is_brand_active

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

# Pearl Prime nominal chapter count for structural variation selection. The
# 12x10x5 lock (chapters x sections x variants) drives this; ``select_variation_knobs``
# uses the chapter count to gate journey_shape candidates by ``chapter_count_range``.
PEARL_PRIME_CHAPTER_COUNT = 12

# FEATURE-KNOB-CATALOG-VARIATION-V1-01 P0-1: deterministic seed shared with the
# runtime pipeline so each catalog row's variation signature matches what the
# Stage-2 selector will compute when ``run_pipeline`` consumes the same row.
VARIATION_SEED_PREFIX = "pearl_prime_catalog_v1"

# Locale → market_id in market_catalog_registry.yaml
LOCALE_TO_MARKET = {
    "en_US": "us",
    "ja_JP": "japan",
    "zh_TW": "taiwan",
    "zh_CN": "china",
}

# Pearl Prime catalog row column order — exact spec from dev brief.
# Columns 1–23 are positionally locked (downstream consumers may rely on
# positional access). Columns 24–28 are the structural variation axes added
# under FEATURE-KNOB-CATALOG-VARIATION-V1-01 P0-1 (appended, not interleaved,
# so positional readers of the original schema keep working).
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
    # P0-1 structural variation axes (appended, positionally locked here):
    "angle_id",
    "motif_id",
    "book_structure_id",
    "journey_shape_id",
    "variation_signature",
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
        # FEATURE-KNOB-CATALOG-VARIATION-V1-01 P0-1: variation axis registries.
        "angle_registry":    "config/angles/angle_registry.yaml",
        "motif_bank":        "config/source_of_truth/recurring_motif_bank.yaml",
        "book_structures":   "config/source_of_truth/book_structure_archetypes.yaml",
        "journey_shapes":    "config/source_of_truth/journey_shapes.yaml",
    }
    return {k: {"data": _load_yaml(v), "sha256": _sha256(v), "path": v}
            for k, v in sources.items()}


# ── Structural variation axes (P0-1) ────────────────────────────────────────
# Deterministic per-row selection of the 4 ratified axes
# (angle_id, motif_id, book_structure_id, journey_shape_id) plus a stable
# signature, using the same SSOT-driven path as the runtime pipeline.

def resolve_angle_id(angle_registry: dict, topic: str, persona: str,
                     brand: str, locale: str) -> tuple[str, str]:
    """
    Returns (angle_id, source_tag).

    1. Use ``catalog_planner_resolution.topic_angle_map`` (P0-2 SSOT) when the
       topic is mapped AND the resulting angle_id is declared under ``angles:``.
    2. Otherwise deterministically pick one of the registry-declared angle keys
       via SHA256 over (locale|brand|topic|persona). The cap entry's anti-drift
       rule forbids adding new mappings to the registry in this PR — any new
       topic→angle mapping requires AMENDMENT.

    Either path returns an angle_id that is a valid key under ``angles:`` so
    the value round-trips through ``CatalogPlanner._validate_catalog_angle_id``.
    """
    angles_root = (angle_registry.get("angles") or {})
    declared = sorted(angles_root.keys())
    if not declared:
        # Should never happen — registry is governance-locked. Fail loud.
        raise RuntimeError(
            "config/angles/angle_registry.yaml::angles is empty; cannot serialize angle_id"
        )

    res_block = (angle_registry.get("catalog_planner_resolution") or {})
    topic_map = (res_block.get("topic_angle_map") or {})
    mapped = topic_map.get(topic)
    if mapped and mapped in angles_root:
        return (str(mapped), "topic_angle_map")

    seed = f"{locale}|{brand}|{topic}|{persona}".encode("utf-8")
    idx = int(hashlib.sha256(seed).hexdigest(), 16) % len(declared)
    return (declared[idx], "deterministic_topic_persona_hash")


def select_variation_axes(angle_registry: dict, topic: str, persona: str,
                          brand: str, locale: str, teacher_id: str
                          ) -> tuple[dict, str]:
    """
    Returns ({angle_id, motif_id, book_structure_id, journey_shape_id, variation_signature},
             angle_source_tag).

    Uses ``phoenix_v4.planning.variation_selector.select_variation_knobs`` as
    the canonical SSOT-driven selector so each catalog row's variation tuple
    matches what ``run_pipeline`` will compute for the same (topic, persona,
    angle, seed). The stable signature is the existing
    ``compute_variation_signature`` (32-char hex SHA256 prefix over the
    canonical variation tuple).
    """
    # Late import: keep module importable in environments where phoenix_v4 is
    # not on the Python path (the generator already requires repo root on
    # sys.path via ``REPO_ROOT`` to resolve config/, but we add it explicitly
    # here so the import works regardless of caller cwd).
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from phoenix_v4.planning.variation_selector import select_variation_knobs  # type: ignore

    angle_id, source_tag = resolve_angle_id(
        angle_registry, topic, persona, brand, locale)

    # Per-row deterministic seed: stable across runs for identical inputs but
    # distinct across (locale, brand, teacher, topic, persona) combos so
    # adjacent rows don't collide on the same variation knob tuple.
    seed = (
        f"{VARIATION_SEED_PREFIX}|{locale}|{brand}|{teacher_id}|"
        f"{topic}|{persona}|{angle_id}"
    )

    knobs = select_variation_knobs(
        topic_id=topic,
        persona_id=persona,
        chapter_count=PEARL_PRIME_CHAPTER_COUNT,
        seed=seed,
        angle_id=angle_id,
        arc_id="",
        installment_number=None,
        wave_index=None,           # no anti-cluster across the whole catalog (audit P0-1 scope)
        config_root=None,          # use phoenix_v4 default config_root
        arc_tags=None,
        platform_id=None,          # platform_knob_tuning is P1, not P0-1
    )

    axes = {
        "angle_id": angle_id,
        "motif_id": knobs["motif_id"],
        "book_structure_id": knobs["book_structure_id"],
        "journey_shape_id": knobs["journey_shape_id"],
        "variation_signature": knobs["variation_signature"],
    }
    return (axes, source_tag)


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
                        locale: str, brand: str,
                        teacher_mode: str = "", runtime_format: str = "") -> tuple[str, str, str]:
    """
    Deterministic per-locale title + subtitle synthesis. No LLM fallback.
    Returns (title, subtitle, note).

    Two paths:

    en_US (B2, PR #790 architecture — unchanged):
        templates  = catalog_config.title_templates[topic]                 (5–6 per topic)
        base_title = templates[idx].title                                  (idx by SHA-256 seed)
        title      = "{voice_prefix} {base_title}".strip()
        subtitle   = "{base_subtitle} — {persona_signal}".strip()
        Selection deterministic by SHA256(locale|brand|topic|persona|teacher_mode|runtime_format).
        voice_prefix from brand_voice_modifiers[brand].voice_prefix.
        persona_signal from persona_subtitle_modifiers[persona].signal.

    ja_JP / zh_TW / zh_CN (B1, on top of #790):
        templates  = catalog_config.title_templates_{locale}              (5 formula templates)
        title_pat  = templates[idx].title    (placeholders: {voice_prefix} {topic})
        sub_pat    = templates[idx].subtitle_pattern
        title      = title_pat with {voice_prefix} ← brand_voice_modifiers[brand].voice_prefix_{locale}
                                  and {topic} ← topic_displays_{locale}[topic]
        subtitle   = sub_pat   with same interpolations + persona_signal_{locale} appended
                                  (joiner: " — " for en_US, " — " for non-en too — keeps Amazon-search compatibility)

    en_US output is byte-identical to PR #790's; the new path only fires for non-en.
    """
    # ── Resolve locale-specific keys ─────────────────────────────────
    is_en = (locale == "en_US")
    template_key = "title_templates" if is_en else f"title_templates_{locale}"
    voice_prefix_key = "voice_prefix" if is_en else f"voice_prefix_{locale}"
    signal_key = "signal" if is_en else f"signal_{locale}"

    # ── Pick template ────────────────────────────────────────────────
    if is_en:
        templates = (catalog_config.get(template_key) or {}).get(topic) or []
    else:
        templates = catalog_config.get(template_key) or []
    if not templates:
        return ("", "", "needs_title_synthesis_locale_native"
                if not is_en else "needs_title_synthesis")

    # B2 §6 salt: include teacher_mode + runtime_format. Same hash shape
    # for all locales so deterministic + reproducible.
    seed = f"{locale}|{brand}|{topic}|{persona}|{teacher_mode}|{runtime_format}".encode("utf-8")
    idx = int(hashlib.sha256(seed).hexdigest(), 16) % len(templates)
    tpl = templates[idx]
    title_pat = tpl.get("title", "") or ""
    sub_pat = tpl.get("subtitle_pattern", "") or ""

    # ── Topic display ────────────────────────────────────────────────
    if is_en:
        topic_disp = topic.replace("_", " ").title()
    else:
        topic_disp_map = catalog_config.get(f"topic_displays_{locale}") or {}
        topic_disp = topic_disp_map.get(topic) or topic.replace("_", " ").title()

    # ── Brand voice prefix (locale-aware) ────────────────────────────
    brand_mods = (catalog_config.get("brand_voice_modifiers") or {})
    voice_entry = brand_mods.get(brand) or brand_mods.get("_default") or {}
    voice_prefix = (voice_entry.get(voice_prefix_key) or "").strip()
    # Fallback: if a non-en row's brand has no locale-specific prefix
    # registered, leave it empty rather than leaking en_US into a CJK title.

    # ── Compose base title + subtitle ────────────────────────────────
    if is_en:
        # en_US (#790): "{voice_prefix} {base_title}" — preserved exactly.
        base_title = title_pat
        title = f"{voice_prefix} {base_title}".strip() if voice_prefix else base_title
        base_subtitle = sub_pat.replace("{topic}", topic_disp)
    else:
        # Non-en formula templates carry {voice_prefix} and {topic} placeholders.
        title = (title_pat
                 .replace("{voice_prefix}", voice_prefix)
                 .replace("{topic}", topic_disp))
        base_subtitle = (sub_pat
                         .replace("{voice_prefix}", voice_prefix)
                         .replace("{topic}", topic_disp))

    # ── Persona subtitle signal (locale-aware) ───────────────────────
    persona_mods = (catalog_config.get("persona_subtitle_modifiers") or {})
    persona_entry = persona_mods.get(persona) or persona_mods.get("_default") or {}
    persona_signal = (persona_entry.get(signal_key) or "").strip()
    if persona_signal and base_subtitle:
        subtitle = f"{base_subtitle} — {persona_signal}"
    else:
        subtitle = base_subtitle

    note = "" if (title and subtitle) else (
        "needs_title_synthesis" if is_en else "needs_title_synthesis_locale_native")
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
    angle_registry = inputs["angle_registry"]["data"] or {}
    topics = inputs["topics"]["data"].get("topics") or []
    personas = inputs["personas"]["data"].get("personas") or []
    # Restrict topics + personas to the active set declared in catalog_generation_config
    # (17 topics × 13 personas — same authority as ~800 high-confidence target).
    cfg_topics = catalog_config.get("topics") or topics
    cfg_personas = catalog_config.get("personas") or personas
    active_topics = [t for t in cfg_topics if t in set(topics)] or cfg_topics
    active_personas = [p for p in cfg_personas if p in set(personas)] or cfg_personas

    scores = inputs["scores"]["data"]
    # B2 (PR #790, supersedes #788): no flagship_set / dedup_phrases needed —
    # title composition uses brand_voice_modifiers + persona_subtitle_modifiers
    # baked into catalog_generation_config.yaml. See pick_title_subtitle().

    rows: list[dict] = []
    status_counts: dict[str, int] = {}

    for brand in brand_ids:
        if not is_brand_active(brand):
            print(f"[{locale}] skipped: inactive brand {brand}")
            continue
        bt = brand_teacher.get(brand)
        if not bt:
            # Not in any known brand registry — still emit a row tagged as blocked.
            for topic in active_topics:
                for persona in active_personas:
                    if is_killed(catalog_config, brand, topic, persona,
                                 locale, DEFAULT_RUNTIME_FORMAT):
                        continue
                    rows.append(_blocked_brand_row(
                        locale, market_id, brand, topic, persona, locale_names,
                        angle_registry))
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
                        catalog_config, locale_names, angle_registry,
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
                    catalog_config, locale_names, angle_registry,
                    readiness="ready",
                    blockers="",
                    notes=f"composite={comp:.2f}",
                ))
                status_counts["ready"] = status_counts.get("ready", 0) + 1

    return rows, status_counts


def _row(locale: str, market_id: str, brand: str, teacher_id: str,
         teacher_mode: bool, topic: str, persona: str, composite: float,
         catalog_config: dict, locale_names: dict[str, str],
         angle_registry: dict,
         readiness: str, blockers: str, notes: str) -> dict:
    title, subtitle, title_note = pick_title_subtitle(
        catalog_config, topic, persona, locale, brand,
        teacher_mode=("teacher" if teacher_mode else "voice"),
        runtime_format=DEFAULT_RUNTIME_FORMAT,
    )
    extra_notes = "; ".join(x for x in (notes, title_note) if x)
    if title_note and readiness == "ready":
        # Title synthesis missing is a soft block — surface it but keep readiness ready
        # only if other gates pass; mark notes.
        pass

    axes, angle_source = select_variation_axes(
        angle_registry, topic, persona, brand, locale, teacher_id)
    if angle_source != "topic_angle_map":
        extra_notes = "; ".join(
            x for x in (extra_notes, f"angle_source={angle_source}") if x)

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
        # P0-1 structural variation axes:
        "angle_id": axes["angle_id"],
        "motif_id": axes["motif_id"],
        "book_structure_id": axes["book_structure_id"],
        "journey_shape_id": axes["journey_shape_id"],
        "variation_signature": axes["variation_signature"],
    }


def _blocked_brand_row(locale: str, market_id: str, brand: str,
                       topic: str, persona: str,
                       locale_names: dict[str, str],
                       angle_registry: dict) -> dict:
    # Even teacher-blocked rows carry registry-valid variation axes so
    # downstream readers can plan around them. Use the empty-string teacher_id
    # as the seed component to keep determinism explicit.
    axes, _ = select_variation_axes(
        angle_registry, topic, persona, brand, locale, teacher_id="")
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
        # P0-1 structural variation axes:
        "angle_id": axes["angle_id"],
        "motif_id": axes["motif_id"],
        "book_structure_id": axes["book_structure_id"],
        "journey_shape_id": axes["journey_shape_id"],
        "variation_signature": axes["variation_signature"],
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
