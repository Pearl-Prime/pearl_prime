#!/usr/bin/env python3
"""
Phoenix Omega Full Catalog Generator
=====================================
Reads brand registry, archetype registry, format registry, and research data
to produce catalog entries on the 12×37 planning grid (12 lanes × 37 brands per
`config/catalog_planning/teacher_brand_lane_assignments.yaml`), using registry rows
when present and planning-driven fallbacks when a locale row is still pending.

Usage:
    python scripts/catalog/generate_full_catalog.py --all-lanes --output artifacts/catalog/full_catalog.csv
    python scripts/catalog/generate_full_catalog.py --lane en_US --output artifacts/catalog/en_us_catalog.csv
    python scripts/catalog/generate_full_catalog.py --brand stabilizer_en_us --output artifacts/catalog/stabilizer_catalog.csv
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import random
import sys
from pathlib import Path
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
# In a git worktree the config files may live in the main checkout.
# Detect and use the main repo root as fallback for reading configs.
_MAIN_REPO = Path("/Users/ahjan/phoenix_omega")
if not (REPO_ROOT / "config" / "brand_management").exists() and (_MAIN_REPO / "config" / "brand_management").exists():
    _CONFIG_ROOT = _MAIN_REPO
else:
    _CONFIG_ROOT = REPO_ROOT

# Try to load YAML; fall back to a minimal parser if PyYAML is unavailable.
try:
    import yaml
except ImportError:
    yaml = None


def _load_yaml(path: Path) -> Any:
    """Load a YAML file, falling back to JSON-based stub if PyYAML missing."""
    if yaml is not None:
        with open(path, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh)
    # Minimal fallback: only works for simple YAML; for complex files we
    # require PyYAML.  Print a helpful error.
    raise ImportError(
        f"PyYAML is required to load {path.name}. Install with: pip install pyyaml"
    )


# ---------------------------------------------------------------------------
# Registry loaders
# ---------------------------------------------------------------------------
def load_brand_registry() -> dict:
    return _load_yaml(_CONFIG_ROOT / "config/brand_management/global_brand_registry.yaml")


def load_teacher_brand_map() -> dict:
    return _load_yaml(_CONFIG_ROOT / "config/brand_management/teacher_brand_map.yaml")


def load_archetype_registry() -> dict:
    return _load_yaml(
        _CONFIG_ROOT / "config/catalog_planning/brand_archetype_registry.yaml"
    )


def load_format_registry() -> dict:
    return _load_yaml(_CONFIG_ROOT / "config/format_selection/format_registry.yaml")


def load_catalog_config() -> dict:
    # Catalog config is always in the working tree (we just created it)
    for root in [REPO_ROOT, _CONFIG_ROOT]:
        p = root / "config/catalog/catalog_generation_config.yaml"
        if p.exists():
            return _load_yaml(p)
    raise FileNotFoundError("catalog_generation_config.yaml not found")


def load_teacher_profiles() -> dict:
    """Load pen_name_teacher_profiles_full.json, indexed by teacher_id."""
    path = _CONFIG_ROOT / "config/authoring/pen_name_teacher_profiles_full.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text())
    return {t["teacher_id"]: t for t in data} if isinstance(data, list) else {}


def load_description_templates() -> dict:
    path = _CONFIG_ROOT / "config/catalog_planning/description_templates.yaml"
    return _load_yaml(path) if path.exists() else {}


def load_teacher_brand_archetypes() -> dict:
    return _load_yaml(_CONFIG_ROOT / "config/catalog_planning/teacher_brand_archetypes.yaml")


def load_teacher_brand_lane_assignments() -> dict:
    return _load_yaml(_CONFIG_ROOT / "config/catalog_planning/teacher_brand_lane_assignments.yaml")


# 12 global lanes — regional blocks are nested under `english_global` in the YAML.
NESTED_PLANNING_LANES = frozenset(
    {
        "dach",
        "france",
        "spain",
        "italy",
        "latam",
        "brazil",
        "japan",
        "korea",
        "taiwan",
        "china",
        "hungary",
    }
)

# Registry keys use lowercase locale tokens (e.g. inner_light_press_de_de).
PLANNING_LANE_TO_LOCALE_TOKEN: dict[str, str] = {
    "english_global": "en_us",
    "dach": "de_de",
    "france": "fr_fr",
    "spain": "es_es",
    "italy": "it_it",
    "latam": "es_us",
    "brazil": "pt_br",
    "japan": "ja_jp",
    "korea": "ko_kr",
    "taiwan": "zh_tw",
    "china": "zh_cn",
    "hungary": "hu_hu",
}

# Catalog CSV lane_id / locale routing (matches global_brand_registry lane_id).
PLANNING_LANE_TO_CATALOG_LANE_ID: dict[str, str] = {
    "english_global": "en_US",
    "dach": "de_DE",
    "france": "fr_FR",
    "spain": "es_ES",
    "italy": "it_IT",
    "latam": "es_US",
    "brazil": "pt_BR",
    "japan": "ja_JP",
    "korea": "ko_KR",
    "taiwan": "zh_TW",
    "china": "zh_CN",
    "hungary": "hu_HU",
}


def _lane_instance_suffix(planning_lane: str, summary: dict) -> str:
    """Suffix on planning teacher brand_instance_id (e.g. _de, _latam)."""
    return str(summary.get("lane_suffixes", {}).get(planning_lane) or "")


def build_planning_teacher_to_legacy_archetype() -> dict[str, str]:
    """Map planning teacher brand_id (e.g. stillness_press) → teacher_brand_map key (e.g. inner_light_press)."""
    arch = load_teacher_brand_archetypes()
    tmap = load_teacher_brand_map()
    brands = tmap.get("teacher_brands", {})
    out: dict[str, str] = {}
    for entry in arch.get("teacher_brand_archetypes", []):
        pid = entry.get("brand_id")
        tid = entry.get("teacher")
        if not pid or not tid:
            continue
        legacy: str | None = None
        for key, row in brands.items():
            if row.get("teacher_id") == tid:
                legacy = key
                break
        if legacy:
            out[str(pid)] = legacy
    return out


def iter_teacher_planning_rows(assignments: dict) -> list[tuple[str, str, str]]:
    """Yield (planning_lane, brand_instance_id, teacher_id) from lane assignments."""
    root = assignments.get("english_global")
    if not isinstance(root, dict):
        return []
    rows: list[tuple[str, str, str]] = []
    for key, info in root.items():
        if key in NESTED_PLANNING_LANES:
            continue
        if isinstance(info, dict) and info.get("teacher"):
            rows.append(("english_global", str(key), str(info["teacher"])))
    for lane in sorted(NESTED_PLANNING_LANES):
        block = root.get(lane)
        if not isinstance(block, dict):
            continue
        for bid, info in block.items():
            if isinstance(info, dict) and info.get("teacher"):
                rows.append((lane, str(bid), str(info["teacher"])))
    return rows


def _teacher_planning_archetype_index() -> dict[str, dict]:
    data = load_teacher_brand_archetypes()
    return {
        str(e["brand_id"]): e
        for e in data.get("teacher_brand_archetypes", [])
        if e.get("brand_id")
    }


def _synthetic_teacher_planning_row(
    instance_id: str,
    teacher_id: str,
    planning_lane: str,
    planning_base: str,
    tarch: dict,
) -> dict:
    lane_id = PLANNING_LANE_TO_CATALOG_LANE_ID[planning_lane]
    gtm = tarch.get("gtm_identity") or {}
    persona_raw = str(gtm.get("persona", ""))
    persona = ARCH_GTM_PERSONA_TO_CATALOG.get(persona_raw, "corporate_managers")
    return {
        "brand_id": instance_id,
        "brand_archetype_id": planning_base,
        "lane_id": lane_id,
        "teacher_id": teacher_id,
        "teacher_mode": True,
        "tradition": str(tarch.get("tradition", "")),
        "brand_focus": str(gtm.get("functional_job", "")),
        "primary_topics": _topics_from_archetype_keywords(tarch),
        "primary_personas": [persona],
    }


def _resolve_teacher_brand_row(
    planning_lane: str,
    instance_id: str,
    teacher_id: str,
    planning_to_legacy: dict[str, str],
    summary: dict,
    all_brands: dict,
    teacher_rows: dict,
    tarch_by_planning: dict[str, dict],
) -> tuple[str, dict] | None:
    sfx = _lane_instance_suffix(planning_lane, summary)
    base = instance_id[: -len(sfx)] if sfx and instance_id.endswith(sfx) else instance_id
    legacy = planning_to_legacy.get(base)
    loc_tok = PLANNING_LANE_TO_LOCALE_TOKEN.get(planning_lane)
    if not loc_tok:
        return None
    if legacy:
        reg_id = f"{legacy}_{loc_tok}"
        bd = all_brands.get(reg_id)
        if bd:
            return instance_id, dict(bd)
        trow = teacher_rows.get(legacy)
        if trow:
            lane_id = PLANNING_LANE_TO_CATALOG_LANE_ID[planning_lane]
            return instance_id, {
                "brand_id": instance_id,
                "brand_archetype_id": legacy,
                "lane_id": lane_id,
                "teacher_id": teacher_id,
                "teacher_mode": True,
                "tradition": str(trow.get("tradition", "")),
                "brand_focus": str(trow.get("brand_focus", "")),
                "primary_topics": list(trow.get("primary_topics", [])),
                "primary_personas": list(trow.get("primary_personas", [])),
            }
    tarch = tarch_by_planning.get(base)
    if tarch:
        return instance_id, _synthetic_teacher_planning_row(
            instance_id, teacher_id, planning_lane, base, tarch
        )
    return None


ARCH_GTM_PERSONA_TO_CATALOG: dict[str, str] = {
    "trauma_sensitive_meditator": "millennial_women_professionals",
    "overthinking_knowledge_worker": "corporate_managers",
    "simplicity_seeker": "gen_x_sandwich",
    "high_functioning_perfectionist": "corporate_managers",
    "energy_depleted_professional": "working_parents",
    "doomscrolling_gen_z": "gen_z_professionals",
    "shadow_work_seeker": "millennial_women_professionals",
    "shame_carrying_people_pleaser": "millennial_women_professionals",
    "high_stakes_performer": "first_responders",
    "chronic_insomnia_sufferer": "gen_x_sandwich",
    "unprocessed_grief_carrier": "working_parents",
    "burnout_survivor_rebuilding": "entrepreneurs",
    "love_exhausted_caregiver": "healthcare_rns",
    "burned_out_professional": "corporate_managers",
    "high_efficiency_achiever": "tech_finance_burnout",
    "insomniac_creative": "millennial_women_professionals",
    "mid_career_stalled": "corporate_managers",
    "neurodivergent_young_adult": "gen_z_professionals",
    "longevity_seeker": "gen_x_sandwich",
    "artistic_student": "gen_alpha_students",
    "overwhelmed_parent": "working_parents",
    "corporate_leader": "nyc_executives",
    "trauma_recovery_adult": "healthcare_rns",
    "spiritually_curious": "millennial_women_professionals",
    "startup_founder": "entrepreneurs",
    "women_35_plus": "millennial_women_professionals",
    "young_male_growth": "gen_z_professionals",
    "gen_z_student": "gen_z_student",
    "chronic_stress_worker": "corporate_managers",
    "biohacker": "entrepreneurs",
    "socially_anxious": "gen_z_professionals",
    "couples_repair": "working_parents",
    "early_riser": "corporate_managers",
    "digital_overwhelm": "tech_finance_burnout",
    "competitive_sales": "nyc_executives",
    "therapy_newcomer": "millennial_women_professionals",
    "45_plus_reinventor": "gen_x_sandwich",
}


def _topics_from_archetype_keywords(arch: dict) -> list[str]:
    clusters = (arch.get("discovery_contract") or {}).get("keyword_clusters") or {}
    blob = " ".join(
        [str(x) for x in clusters.get("primary", []) + clusters.get("secondary", [])]
    ).lower()
    out: list[str] = []
    rules = [
        ("anxiety", "anxiety"),
        ("sleep", "sleep_anxiety"),
        ("insomnia", "sleep_anxiety"),
        ("burnout", "burnout"),
        ("trauma", "somatic_healing"),
        ("grief", "grief"),
        ("worth", "self_worth"),
        ("confidence", "self_worth"),
        ("imposter", "imposter_syndrome"),
        ("boundary", "boundaries"),
        ("focus", "overthinking"),
        ("courage", "courage"),
        ("depression", "depression"),
        ("relationship", "boundaries"),
        ("longevity", "somatic_healing"),
        ("healthspan", "burnout"),
        ("student", "anxiety"),
        ("performance", "imposter_syndrome"),
    ]
    for needle, topic in rules:
        if needle in blob and topic not in out:
            out.append(topic)
    if not out:
        out = ["anxiety", "burnout", "self_worth", "overthinking"]
    return out[:5]


def _archetype_index() -> dict[str, dict]:
    data = load_archetype_registry()
    return {
        str(a["brand_id"]): a
        for a in data.get("brand_archetypes", [])
        if a.get("brand_id")
    }


def _synthetic_standard_brand_row(base: str, planning_lane: str, arch: dict) -> dict:
    loc_tok = PLANNING_LANE_TO_LOCALE_TOKEN[planning_lane]
    reg_id = f"{base}_{loc_tok}"
    lane_id = PLANNING_LANE_TO_CATALOG_LANE_ID[planning_lane]
    gtm = arch.get("gtm_identity") or {}
    persona_raw = str(gtm.get("persona", ""))
    persona = ARCH_GTM_PERSONA_TO_CATALOG.get(persona_raw, "corporate_managers")
    return {
        "brand_id": reg_id,
        "brand_archetype_id": base,
        "lane_id": lane_id,
        "teacher_id": "",
        "teacher_mode": False,
        "tradition": "",
        "brand_focus": str(gtm.get("functional_job", "")),
        "primary_topics": _topics_from_archetype_keywords(arch),
        "primary_personas": [persona],
    }


def _iter_standard_brand_targets(summary: dict, all_brands: dict) -> list[tuple[str, dict]]:
    bases = summary.get("standard_mode_brands", {}).get("base_names", [])
    lanes = ["english_global"] + sorted(NESTED_PLANNING_LANES)
    arch_by_id = _archetype_index()
    out: list[tuple[str, dict]] = []
    for planning_lane in lanes:
        loc_tok = PLANNING_LANE_TO_LOCALE_TOKEN.get(planning_lane)
        if not loc_tok:
            continue
        for base in bases:
            reg_id = f"{base}_{loc_tok}"
            bd = all_brands.get(reg_id)
            if bd:
                out.append((str(bd.get("brand_id", reg_id)), dict(bd)))
                continue
            arch = arch_by_id.get(base)
            if not arch:
                continue
            syn = _synthetic_standard_brand_row(base, planning_lane, arch)
            out.append((syn["brand_id"], syn))
    return out


def build_12x37_brand_targets(all_brands: dict) -> list[tuple[str, dict]]:
    """Planned 12 lanes × 37 brands: teacher IDs from planning YAML, rows from registry (or teacher map fallback)."""
    assignments = load_teacher_brand_lane_assignments()
    summary = assignments.get("summary") or {}
    planning_to_legacy = build_planning_teacher_to_legacy_archetype()
    teacher_rows = load_teacher_brand_map().get("teacher_brands", {})
    tarch_by_planning = _teacher_planning_archetype_index()
    targets: list[tuple[str, dict]] = []
    seen: set[tuple[str, str]] = set()
    for planning_lane, instance_id, tid in iter_teacher_planning_rows(assignments):
        pair = _resolve_teacher_brand_row(
            planning_lane,
            instance_id,
            tid,
            planning_to_legacy,
            summary,
            all_brands,
            teacher_rows,
            tarch_by_planning,
        )
        if not pair:
            continue
        bid, data = pair
        key = (bid, data.get("lane_id", ""))
        if key in seen:
            continue
        seen.add(key)
        targets.append((bid, data))
    for bid, data in _iter_standard_brand_targets(summary, all_brands):
        key = (bid, data.get("lane_id", ""))
        if key in seen:
            continue
        seen.add(key)
        targets.append((bid, data))
    return targets


# ---------------------------------------------------------------------------
# Deterministic catalog_id
# ---------------------------------------------------------------------------
def make_catalog_id(brand_id: str, topic: str, persona: str, fmt: str, pos: int = 0) -> str:
    """SHA-256-based deterministic ID (first 12 hex chars)."""
    seed = f"{brand_id}|{topic}|{persona}|{fmt}|{pos}"
    return "CAT-" + hashlib.sha256(seed.encode()).hexdigest()[:12].upper()


# ---------------------------------------------------------------------------
# Title generation
# ---------------------------------------------------------------------------
TOPIC_DISPLAY = {
    "anxiety": "Anxiety",
    "boundaries": "Boundaries",
    "burnout": "Burnout",
    "compassion_fatigue": "Compassion Fatigue",
    "courage": "Courage",
    "depression": "Depression",
    "financial_anxiety": "Financial Anxiety",
    "financial_stress": "Financial Stress",
    "grief": "Grief",
    "imposter_syndrome": "Imposter Syndrome",
    "overthinking": "Overthinking",
    "self_worth": "Self-Worth",
    "sleep_anxiety": "Sleep Anxiety",
    "social_anxiety": "Social Anxiety",
    "somatic_healing": "Somatic Healing",
}

PERSONA_DISPLAY = {
    "corporate_managers": "Professionals",
    "millennial_women_professionals": "Women",
    "tech_finance_burnout": "High Performers",
    "gen_z_professionals": "Young Professionals",
    "healthcare_rns": "Nurses and Caregivers",
    "first_responders": "First Responders",
    "educators": "Educators",
    "working_parents": "Working Parents",
    "entrepreneurs": "Entrepreneurs",
    "gen_x_sandwich": "Midlife Adults",
    "gen_alpha_students": "Students",
    "nyc_executives": "Executives",
}

# Series names by topic -- creative, non-keyword-stuffed
SERIES_NAMES = {
    "anxiety": ["The Steady Ground Collection", "Calm Signal Series"],
    "burnout": ["The Recovery Road Series", "Ashes to Energy Collection"],
    "sleep_anxiety": ["The Midnight Reset Series", "Quiet Night Collection"],
    "imposter_syndrome": ["The Belonging Series", "Own Your Seat Collection"],
    "social_anxiety": ["The Brave Room Series", "Show Up Collection"],
    "self_worth": ["The Enough Series", "Mirror Work Collection"],
    "boundaries": ["The Sacred Line Series", "No with Grace Collection"],
    "grief": ["The After Collection", "Still Standing Series"],
    "overthinking": ["The Quiet Mind Series", "Loop Breaker Collection"],
    "somatic_healing": ["The Body Knows Series", "Nervous System Reset Collection"],
    "depression": ["The Color Returns Series", "Light Ahead Collection"],
    "courage": ["The Bold Step Series", "Fear to Fire Collection"],
    "compassion_fatigue": ["The Healer's Rest Series", "Empty Well Collection"],
    "financial_anxiety": ["The Money Peace Series", "Worth Beyond Balance Collection"],
    "financial_stress": ["The Money Peace Series", "Worth Beyond Balance Collection"],
}

# Per-series book subtitle templates (keyword-rich, SEO-carrying)
SERIES_BOOK_SUBTITLES = {
    "anxiety": [
        "Understanding Your Nervous System and Anxiety Triggers",
        "Somatic Exercises for Anxiety Relief",
        "Calming High-Functioning Anxiety at Work",
        "Breaking the Anxiety Spiral with Body-Based Tools",
        "Anxiety Recovery Through Breath and Movement",
        "Rewiring Anxious Thought Patterns",
        "Building an Anxiety-Proof Morning Routine",
        "From Hypervigilance to Grounded Calm",
        "Anxiety and Sleep: Reclaiming Rest",
        "Long-Term Anxiety Recovery and Nervous System Resilience",
    ],
    "burnout": [
        "Recognizing Burnout Before the Crash",
        "Nervous System Recovery from Work Exhaustion",
        "Setting Boundaries to Prevent Burnout",
        "Burnout Recovery for High Achievers",
        "Somatic Healing After Prolonged Stress",
        "Rebuilding Energy and Motivation After Burnout",
        "Burnout and Identity: Who Am I Without Hustle",
        "The Role of Rest in Burnout Recovery",
        "Burnout-Proof Habits for Sustainable Work",
        "From Burnout to Balance: A New Way Forward",
    ],
    "sleep_anxiety": [
        "Why Your Mind Races at Night",
        "Somatic Techniques for Falling Asleep",
        "Breaking the 3 AM Anxiety Cycle",
        "Racing Thoughts and How to Calm Them",
        "Building a Sleep-Friendly Nervous System",
        "Insomnia Recovery Without Medication",
        "The Body's Role in Sleep Anxiety",
        "Evening Routines for Better Sleep",
        "Overcoming the Fear of Sleeplessness",
        "Long-Term Sleep Recovery and Rest Resilience",
    ],
    "imposter_syndrome": [
        "Understanding the Roots of Imposter Syndrome",
        "Imposter Syndrome at Work: A Recovery Guide",
        "The Nervous System Behind Self-Doubt",
        "Imposter Syndrome for Women in Leadership",
        "From Fraud Feelings to Authentic Confidence",
        "Imposter Syndrome and Perfectionism",
        "Owning Your Achievements Without Apology",
        "Imposter Syndrome in Creative Careers",
        "Building Worth That Doesn't Need Proof",
        "From Imposter to Belonging: The Full Journey",
    ],
    "social_anxiety": [
        "Understanding Social Anxiety and Your Nervous System",
        "Small Talk Without the Panic",
        "Social Anxiety Recovery for Introverts",
        "The Body's Response to Social Situations",
        "Building Social Confidence Step by Step",
        "Phone Anxiety and Digital Social Stress",
        "From Avoidance to Connection",
        "Social Anxiety in the Workplace",
        "Making Friends as an Adult with Social Anxiety",
        "Long-Term Social Confidence and Belonging",
    ],
    "self_worth": [
        "Where Low Self-Esteem Comes From",
        "Somatic Practices for Self-Worth Recovery",
        "Healing the Inner Critic",
        "Self-Worth Beyond Achievement",
        "Body Image and Self-Esteem Healing",
        "Building Confidence from the Inside Out",
        "Self-Worth in Relationships",
        "From People-Pleasing to Self-Respect",
        "The Practice of Self-Compassion",
        "Unshakable Worth: Living Beyond Approval",
    ],
    "boundaries": [
        "Why Boundaries Feel So Hard",
        "The Nervous System Behind People-Pleasing",
        "Setting Boundaries at Work Without Guilt",
        "Boundaries in Family Relationships",
        "The Somatic Experience of Saying No",
        "Boundaries with Difficult People",
        "Boundaries and Self-Worth",
        "Digital Boundaries and Screen-Time Limits",
        "Maintaining Boundaries Under Pressure",
        "The Freedom on the Other Side of No",
    ],
    "grief": [
        "The First Days of Grief",
        "Grief and Your Nervous System",
        "When Grief Won't Follow the Stages",
        "Grief After Sudden Loss",
        "The Body's Way of Grieving",
        "Grief and Guilt: Letting Go of What-Ifs",
        "Grief Anniversaries and Triggers",
        "Finding Meaning After Loss",
        "Grief in the Workplace",
        "Living with Loss: Long-Term Grief Integration",
    ],
    "overthinking": [
        "Why Your Brain Won't Stop",
        "The Nervous System Behind Rumination",
        "Breaking the Overthinking Loop",
        "Overthinking at Night: A Sleep-Ready Mind",
        "Decision Fatigue and Analysis Paralysis",
        "Somatic Tools for Quieting the Mind",
        "Overthinking in Relationships",
        "From Worry to Presence",
        "The Perfectionism-Overthinking Connection",
        "A Quiet Mind: Long-Term Recovery from Overthinking",
    ],
    "somatic_healing": [
        "Your Nervous System Explained",
        "Vagus Nerve Exercises for Daily Calm",
        "Releasing Trauma Stored in the Body",
        "The Polyvagal Approach to Safety",
        "Somatic Healing for Anxiety and Stress",
        "Body-Based Recovery from Burnout",
        "Freeze Response and How to Thaw",
        "Somatic Healing for Sleep and Rest",
        "The Body's Wisdom in Emotional Healing",
        "Building a Resilient Nervous System for Life",
    ],
    "depression": [
        "Understanding Low Energy and Emotional Numbness",
        "The Nervous System in Depression Recovery",
        "Somatic Practices for Lifting Mood",
        "High-Functioning Depression: Hidden Struggles",
        "Motivation Recovery After Depression",
        "Depression and Sleep: Breaking the Cycle",
        "Rebuilding Daily Routines After Depression",
        "Depression in Relationships",
        "Body-Based Hope: Somatic Depression Recovery",
        "The Long Road Back to Color",
    ],
    "courage": [
        "Understanding the Fear Response",
        "The Nervous System Behind Courage",
        "Courage in Career Transitions",
        "From Paralysis to Bold Action",
        "Somatic Courage: Bravery in the Body",
        "Courage After Failure",
        "Speaking Up: Courage in Relationships",
        "Fear of the Unknown",
        "Building Courage as a Daily Practice",
        "The Courage to Be Yourself",
    ],
    "compassion_fatigue": [
        "Recognizing Compassion Fatigue Early",
        "The Nervous System of Caregivers",
        "Compassion Fatigue Recovery for Nurses",
        "Empathy Without Exhaustion",
        "Boundaries for Helpers and Healers",
        "Somatic Recovery from Emotional Labor",
        "Moral Injury in Healthcare",
        "Rebuilding Empathy After Burnout",
        "Self-Care That Actually Works for Caregivers",
        "Sustainable Caring: Long-Term Compassion Resilience",
    ],
    "financial_anxiety": [
        "Understanding Money Anxiety and Its Roots",
        "The Nervous System Response to Financial Stress",
        "Breaking the Money Shame Cycle",
        "Financial Anxiety for Young Professionals",
        "Somatic Tools for Money Worry Relief",
        "Budgeting Without the Panic",
        "Money and Relationships",
        "Financial Anxiety and Sleep",
        "Building Financial Confidence",
        "From Money Fear to Financial Peace",
    ],
    "financial_stress": [
        "Understanding Financial Stress in Your Body",
        "The Nervous System Response to Money Pressure",
        "Breaking the Financial Shame Cycle",
        "Financial Stress for Working Families",
        "Somatic Tools for Money Pressure Relief",
        "Practical Calm for Financial Uncertainty",
        "Money Stress and Relationships",
        "Financial Stress and Sleep Recovery",
        "Building Financial Resilience",
        "From Money Pressure to Financial Wellness",
    ],
}


def pick_title_and_subtitle(
    config: dict,
    topic: str,
    persona: str,
    content_type: str,
    series_idx: int = 0,
    book_pos: int = 0,
    seed_str: str = "",
) -> tuple[str, str]:
    """
    Select a title/subtitle pair from templates, deterministically seeded.
    For series books, the subtitle carries per-book SEO keywords.
    """
    rng = random.Random(seed_str)
    templates = config.get("title_templates", {}).get(topic, [])
    if not templates:
        # Fallback generic
        templates = [
            {"title": f"The Path Forward", "subtitle_pattern": f"A Guide to {{topic}} Recovery and Healing"}
        ]

    topic_display = TOPIC_DISPLAY.get(topic, topic.replace("_", " ").title())
    persona_display = PERSONA_DISPLAY.get(persona, persona.replace("_", " ").title())

    if content_type == "series_book" and book_pos > 0:
        # Series books after Book 1 get unique per-book subtitles
        subs = SERIES_BOOK_SUBTITLES.get(topic, [])
        idx = min(book_pos - 1, len(subs) - 1) if subs else 0
        subtitle = subs[idx] if subs else f"{topic_display} Recovery: Part {book_pos}"
        # Series Book 1 gets the template title; later books get "Book N" in series
        tpl = rng.choice(templates)
        title = tpl["title"]
        return title, subtitle

    # Standalone / micro / deep / series Book 1
    tpl = rng.choice(templates)
    title = tpl["title"]
    subtitle = tpl["subtitle_pattern"].replace("{topic}", topic_display)

    # For persona-specific standalone, add audience to subtitle
    if content_type == "standalone" and persona not in ("corporate_managers",):
        subtitle = subtitle.rstrip(".") + f" for {persona_display}"

    return title, subtitle


def make_description(
    topic: str, persona: str, content_type: str,
    catalog_id: str = "",
    brand_data: dict | None = None,
    teacher_data: dict | None = None,
    desc_templates: dict | None = None,
    runtime_format: str = "",
    companion_type: str = "",
) -> str:
    """Generate a unique 3-4 sentence platform description using 4-layer composition."""
    brand_data = brand_data or {}
    teacher_data = teacher_data or {}
    desc_templates = desc_templates or {}

    topic_d = TOPIC_DISPLAY.get(topic, topic.replace("_", " ").title())
    persona_d = PERSONA_DISPLAY.get(persona, persona.replace("_", " ").title())
    h = hash(catalog_id) if catalog_id else 0

    # Layer 1: Brand voice (5 sentence structures, rotated)
    _openers = [
        "From {b}, rooted in {t}.",
        "{b} brings a {t}-grounded approach.",
        "Published by {b}, drawing on {t}.",
        "Published by {b}, informed by {t}.",
        "{b} presents a {t}-based path.",
    ]
    brand_name = brand_data.get("display_name", "")
    tradition = brand_data.get("tradition", "")
    brand_focus = brand_data.get("brand_focus", "")
    trad_short = tradition.split("/")[0].strip().lower() if tradition and "/" in tradition else (tradition.strip().lower() if tradition else "somatic healing")
    if brand_name:
        layer1 = _openers[abs(h) % len(_openers)].format(b=brand_name, t=trad_short)
        if brand_focus and abs(h >> 3) % 2 == 0:
            layer1 += f" {brand_focus.rstrip('.')}."
    else:
        layer1 = ""

    # Layer 2: Teacher method (5 intro variants × 5 method variants)
    _t_intros = [
        "Guided by {n}, {p}.",
        "Written through the teachings of {n}, {p}.",
        "{n} brings {p} to this work.",
        "Drawing on the practice of {n}, {p}.",
        "Informed by {n}'s approach — {p}.",
    ]
    _m_intros = [
        "This {c} applies {m}.",
        "Built on {m}.",
        "Uses {m} to guide each chapter.",
        "Grounded in {m}.",
        "Structured around {m}.",
    ]
    ei = teacher_data.get("ei_profile", {})
    teacher_name = teacher_data.get("display_name", "")
    layer2 = ""
    tradition_phrase = ei.get("tradition_phrase", "")
    ei_one_liner = ei.get("ei_one_liner", "")
    reader_benefit = ei.get("reader_benefit_phrase", "")
    if teacher_name and tradition_phrase:
        layer2 = _t_intros[abs(h >> 4) % len(_t_intros)].format(n=teacher_name, p=tradition_phrase)
    if ei_one_liner:
        ct_display = content_type.replace("_", " ")
        layer2 += " " + _m_intros[abs(h >> 6) % len(_m_intros)].format(c=ct_display, m=ei_one_liner)
    elif reader_benefit:
        layer2 += f" {reader_benefit.rstrip('.')}."

    # Layer 3: Topic hook (5 per topic, rotated by different hash bits)
    hooks = desc_templates.get("topic_hooks", {}).get(topic, [])
    if hooks:
        layer3 = hooks[abs(h >> 8) % len(hooks)]
    else:
        layer3 = f"A practical exploration of {topic_d.lower()} through body-based and evidence-based approaches."

    # Layer 4: Format + Persona + Companion
    rt_descs = desc_templates.get("runtime_descriptions", {})
    p_descs = desc_templates.get("persona_descriptions", {})
    c_notes = desc_templates.get("companion_notes", {})
    rt = rt_descs.get(runtime_format, f"A guide")
    pd = p_descs.get(persona, persona_d.lower())
    cn = c_notes.get(companion_type, "")
    layer4 = f"{rt} for {pd}."
    if cn:
        layer4 += f" {cn}"

    parts = [p for p in [layer1, layer2, layer3, layer4] if p.strip()]
    return " ".join(parts).strip()


def make_cover_brief(
    archetype_data: dict, cover_templates: dict
) -> str:
    """Build a cover brief string from archetype cover_art_identity."""
    cai = archetype_data.get("cover_art_identity", {})
    style = (cai.get("style_pool") or ["minimalist_gradient"])[0]
    palette = ", ".join(cai.get("color_palette", ["muted_blue", "warm_sand"]))
    template = cover_templates.get(style, cover_templates.get("minimalist_gradient", ""))
    return template.replace("{palette}", palette)


def get_keywords(config: dict, topic: str) -> str:
    """Return 7 backend keywords as semicolon-separated string."""
    kws = config.get("keyword_templates", {}).get(topic, [])
    return "; ".join(kws[:7])


# ---------------------------------------------------------------------------
# Pricing
# ---------------------------------------------------------------------------
def compute_price(
    archetype_data: dict,
    content_type: str,
    locale: str,
    config: dict,
    is_series_book1: bool = False,
) -> float:
    pp = archetype_data.get("pricing_posture", {})
    locale_adj = config.get("locale_pricing", {}).get(locale, {})
    multiplier = locale_adj.get("multiplier", 1.0)

    if is_series_book1:
        return 0.99 * multiplier

    if content_type == "micro_book":
        base = pp.get("micro_sessions", [3.99, 5.99])
        price = base[0]
    elif content_type == "deep_book":
        base = pp.get("deep_dives", [17.99, 24.99])
        price = base[1]
    elif content_type == "series_book":
        price = 4.99
    else:  # standalone
        base = pp.get("micro_sessions", [3.99, 5.99])
        price = (base[0] + base[1]) / 2

    adjusted = round(price * multiplier, 2)
    # Apply locale caps
    max_std = locale_adj.get("max_standard", 999)
    min_micro = locale_adj.get("min_micro", 0.50)
    if adjusted > max_std:
        adjusted = max_std
    if adjusted < min_micro:
        adjusted = min_micro
    return round(adjusted, 2)


# ---------------------------------------------------------------------------
# Format assignment
# ---------------------------------------------------------------------------
CONTENT_TYPE_FORMAT_MAP = {
    "micro_book": ("F015", "micro_book_15"),
    "standalone": ("F006", "standard_book"),
    "series_book": ("F003", "short_book_30"),
    "deep_book": ("F004", "deep_book_4h"),
}

RUNTIME_WORD_RANGES = {
    "micro_book_15": (2500, 3000),
    "micro_book_20": (3000, 4000),
    "short_book_30": (4500, 5500),
    "standard_book": (9000, 11000),
    "extended_book_2h": (18000, 22000),
    "deep_book_4h": (36000, 44000),
    "deep_book_6h": (52000, 58000),
}

RUNTIME_CHAPTER_DEFAULTS = {
    "micro_book_15": 5,
    "micro_book_20": 5,
    "short_book_30": 7,
    "standard_book": 12,
    "extended_book_2h": 15,
    "deep_book_4h": 20,
    "deep_book_6h": 24,
}


def select_format(content_type: str, topic: str) -> tuple[str, str]:
    """Pick structural + runtime format IDs based on content type and topic."""
    defaults = CONTENT_TYPE_FORMAT_MAP.get(content_type, ("F006", "standard_book"))

    # Adjust based on topic affinity
    if content_type == "standalone":
        if topic == "somatic_healing":
            return ("F006", "standard_book")
        if topic == "sleep_anxiety":
            return ("F003", "short_book_30")
        if topic in ("imposter_syndrome", "self_worth"):
            return ("F007", "standard_book")
        if topic == "boundaries":
            return ("F007", "standard_book")
    if content_type == "deep_book":
        if topic == "somatic_healing":
            return ("F004", "deep_book_4h")
        if topic == "grief":
            return ("F009", "deep_book_4h")
    return defaults


# ---------------------------------------------------------------------------
# Companion / freebie
# ---------------------------------------------------------------------------
def get_companion(content_type: str, topic: str) -> tuple[str, str]:
    """Return companion_type and freebie_slug."""
    if content_type == "micro_book":
        return ("none", "")
    if topic in ("somatic_healing", "anxiety", "sleep_anxiety", "burnout"):
        slug = f"workbook-{topic.replace('_', '-')}"
        return ("workbook", slug)
    if topic in ("imposter_syndrome", "self_worth", "social_anxiety"):
        slug = f"assessment-{topic.replace('_', '-')}"
        return ("practice_guide", slug)
    return ("none", "")


# ---------------------------------------------------------------------------
# Kill-list checks
# ---------------------------------------------------------------------------
def is_killed(config: dict, brand_id: str, topic: str, persona: str, locale: str, runtime_fmt: str) -> bool:
    kills = config.get("kill_list", {})
    for tp in kills.get("topic_persona_kills", []):
        if tp["topic"] == topic and tp["persona"] == persona:
            return True
    for fl in kills.get("format_locale_kills", []):
        if fl["format"] == runtime_fmt and fl["locale"] == locale:
            return True
    archetype_id = brand_id.rsplit("_", 2)[0] if "_" in brand_id else brand_id
    for bl in kills.get("brand_locale_kills", []):
        if bl["brand"] == archetype_id and bl["locale"] == locale:
            return True
    return False


# ---------------------------------------------------------------------------
# Main catalog generation
# ---------------------------------------------------------------------------
def generate_catalog(
    lane_filter: str | None = None,
    brand_filter: str | None = None,
) -> list[dict]:
    """Generate the full catalog (12×37 planning grid), returning list of entry dicts."""

    brand_reg = load_brand_registry()
    teacher_map = load_teacher_brand_map()
    archetype_reg = load_archetype_registry()
    config = load_catalog_config()
    teacher_profiles = load_teacher_profiles()
    desc_templates = load_description_templates()
    market_weights = desc_templates.get("market_topic_weights", {})

    # Index archetype data by brand_id
    archetype_index: dict[str, dict] = {}
    for arch in archetype_reg.get("brand_archetypes", []):
        archetype_index[arch["brand_id"]] = arch

    cover_templates = config.get("cover_brief_templates", {})
    content_mix = config.get("content_mix", {})

    all_brands = brand_reg.get("brands", {})
    entries: list[dict] = []
    seen_ids: set[str] = set()

    brand_targets = build_12x37_brand_targets(all_brands)

    for brand_id, brand_data in brand_targets:
        lane_id = brand_data.get("lane_id", "")
        locale = lane_id

        # Filters
        if lane_filter and lane_id != lane_filter:
            continue
        if brand_filter and brand_id != brand_filter:
            continue

        archetype_id = brand_data.get("brand_archetype_id", "")
        arch = archetype_index.get(archetype_id, {})
        teacher_id = brand_data.get("teacher_id", "")
        teacher_mode = brand_data.get("teacher_mode", False)

        # P2: Fill empty teacher_id from best-fit teacher profiles
        # Brand registry uses locale-suffixed IDs (adhd_forge_en_us) but teacher
        # profiles use base IDs (adhd_forge). Strip locale suffix for matching.
        if not teacher_id and teacher_profiles:
            base_brand = "_".join(brand_id.split("_")[:-2]) if brand_id.count("_") >= 2 else brand_id
            best_score = -1
            for tid, tprof in teacher_profiles.items():
                if tprof.get("brand_id") == brand_id or tprof.get("brand_id") == base_brand:
                    teacher_id = tid
                    break
                ts = tprof.get("topic_scores", {})
                avg = sum(ts.get(t, 0) for t in brand_data.get("primary_topics", [])) / max(len(brand_data.get("primary_topics", [])), 1)
                if avg > best_score:
                    best_score = avg
                    teacher_id = tid

        topics = brand_data.get("primary_topics", [])
        personas = brand_data.get("primary_personas", [])

        if not topics or not personas:
            continue

        # Every brand in every lane gets full catalog — production cost is near-zero.
        # No artificial tier limits. 24 brands × all topics × series + standalones + micros.
        # The 800 high-confidence configs are tagged WAVE_1 (ship first).
        # Everything else is WAVE_2 (ship alongside, track performance).
        # KILL rule: zero sales after 90 days → deprioritize.
        locale_config = config.get("locales", {}).get(lane_id, {})
        tier = locale_config.get("tier", "secondary")
        max_topic_combos = len(topics)  # ALL topics for this brand
        include_series = True
        series_length = 7 if tier == "primary" else 4

        # --- Generate content per topic x persona ---
        brand_entries: list[dict] = []
        combo_count = 0

        for topic in topics:
            if combo_count >= max_topic_combos:
                break
            # Use primary persona for this brand (archetype-defined)
            persona = personas[0] if personas else "corporate_managers"
            combo_count += 1

            # --- Series (if lane supports it) ---
            if include_series:
                series_names_list = SERIES_NAMES.get(topic, [f"The {TOPIC_DISPLAY.get(topic, topic).title()} Series"])
                rng = random.Random(f"{brand_id}|{topic}|{persona}")
                series_name = rng.choice(series_names_list)
                series_id = f"SER-{hashlib.sha256(f'{brand_id}|{series_name}'.encode()).hexdigest()[:8].upper()}"

                fmt_id, runtime_id = select_format("series_book", topic)
                if not is_killed(config, brand_id, topic, persona, locale, runtime_id):
                    # Series Book 1 (Wave 1 at $0.99)
                    cat_id = make_catalog_id(brand_id, topic, persona, "series_1", 1)
                    if cat_id not in seen_ids:
                        seen_ids.add(cat_id)
                        title, subtitle = pick_title_and_subtitle(
                            config, topic, persona, "series_book", 0, 0, seed_str=cat_id
                        )
                        word_range = RUNTIME_WORD_RANGES.get(runtime_id, (4500, 5500))
                        chapters = RUNTIME_CHAPTER_DEFAULTS.get(runtime_id, 7)
                        companion_type, freebie_slug = get_companion("series_book", topic)
                        brand_entries.append({
                            "catalog_id": cat_id,
                            "brand_id": brand_id,
                            "lane_id": lane_id,
                            "teacher_id": teacher_id,
                            "topic_id": topic,
                            "persona_id": persona,
                            "format_id": fmt_id,
                            "runtime_format_id": runtime_id,
                            "content_type": "series_book",
                            "series_id": series_id,
                            "series_position": 1,
                            "title": f"{series_name}: {title}",
                            "subtitle": subtitle,
                            "price_usd": compute_price(arch, "series_book", locale, config, is_series_book1=True),
                            "keywords": get_keywords(config, topic),
                            "description": make_description(
                                topic, persona, "series_book",
                                catalog_id=cat_id,
                                brand_data=brand_data,
                                teacher_data=teacher_profiles.get(teacher_id, {}),
                                desc_templates=desc_templates,
                                runtime_format=runtime_id,
                                companion_type=companion_type,
                            ),
                            "cover_brief": make_cover_brief(arch, cover_templates),
                            "companion_type": companion_type,
                            "freebie_slug": freebie_slug,
                            "estimated_word_count": f"{word_range[0]}-{word_range[1]}",
                            "estimated_chapters": chapters,
                            "priority": "WAVE_1",
                            "market_viability": "STRONG",
                        })

                        # Series Books 2-N (Wave 2)
                        for pos in range(2, series_length + 1):
                            cat_id_n = make_catalog_id(brand_id, topic, persona, f"series_{pos}", pos)
                            if cat_id_n in seen_ids:
                                continue
                            seen_ids.add(cat_id_n)
                            _, sub_n = pick_title_and_subtitle(
                                config, topic, persona, "series_book", 0, pos, seed_str=cat_id_n
                            )
                            # P3: Subtitle diversity — add angle variation for pos > 1
                            topic_d = TOPIC_DISPLAY.get(topic, topic.replace("_", " ").title())
                            angle_variants = [
                                f"Deeper Practices for {topic_d}",
                                f"Advanced {topic_d} Recovery Strategies",
                                f"Next Steps in {topic_d} Healing",
                                f"Building on {topic_d} Foundations",
                                f"Sustained {topic_d} Resilience",
                            ]
                            angle_rng = random.Random(f"{cat_id_n}|angle")
                            angle_suffix = angle_rng.choice(angle_variants)
                            if sub_n and not any(v in sub_n for v in angle_variants):
                                sub_n = f"{sub_n} — {angle_suffix}"
                            brand_entries.append({
                                "catalog_id": cat_id_n,
                                "brand_id": brand_id,
                                "lane_id": lane_id,
                                "teacher_id": teacher_id,
                                "topic_id": topic,
                                "persona_id": persona,
                                "format_id": fmt_id,
                                "runtime_format_id": runtime_id,
                                "content_type": "series_book",
                                "series_id": series_id,
                                "series_position": pos,
                                "title": f"{series_name}: Book {pos}",
                                "subtitle": sub_n,
                                "price_usd": compute_price(arch, "series_book", locale, config),
                                "keywords": get_keywords(config, topic),
                                "description": make_description(
                                    topic, persona, "series_book",
                                    catalog_id=cat_id_n,
                                    brand_data=brand_data,
                                    teacher_data=teacher_profiles.get(teacher_id, {}),
                                    desc_templates=desc_templates,
                                    runtime_format=runtime_id,
                                    companion_type=companion_type,
                                ),
                                "cover_brief": make_cover_brief(arch, cover_templates),
                                "companion_type": companion_type,
                                "freebie_slug": freebie_slug,
                                "estimated_word_count": f"{word_range[0]}-{word_range[1]}",
                                "estimated_chapters": chapters,
                                "priority": "WAVE_2",
                                "market_viability": "STRONG",
                            })

            # --- Micro book (Wave 1 cold start) ---
            micro_fmt, micro_runtime = select_format("micro_book", topic)
            if not is_killed(config, brand_id, topic, persona, locale, micro_runtime):
                cat_micro = make_catalog_id(brand_id, topic, persona, "micro", 0)
                if cat_micro not in seen_ids:
                    seen_ids.add(cat_micro)
                    t_micro, s_micro = pick_title_and_subtitle(
                        config, topic, persona, "micro_book", seed_str=cat_micro
                    )
                    micro_word = RUNTIME_WORD_RANGES.get(micro_runtime, (2500, 3000))
                    micro_ch = RUNTIME_CHAPTER_DEFAULTS.get(micro_runtime, 5)
                    brand_entries.append({
                        "catalog_id": cat_micro,
                        "brand_id": brand_id,
                        "lane_id": lane_id,
                        "teacher_id": teacher_id,
                        "topic_id": topic,
                        "persona_id": persona,
                        "format_id": micro_fmt,
                        "runtime_format_id": micro_runtime,
                        "content_type": "micro_book",
                        "series_id": "",
                        "series_position": 0,
                        "title": t_micro,
                        "subtitle": s_micro,
                        "price_usd": compute_price(arch, "micro_book", locale, config),
                        "keywords": get_keywords(config, topic),
                        "description": make_description(
                            topic, persona, "micro_book",
                            catalog_id=cat_micro,
                            brand_data=brand_data,
                            teacher_data=teacher_profiles.get(teacher_id, {}),
                            desc_templates=desc_templates,
                            runtime_format=micro_runtime,
                            companion_type="none",
                        ),
                        "cover_brief": make_cover_brief(arch, cover_templates),
                        "companion_type": "none",
                        "freebie_slug": "",
                        "estimated_word_count": f"{micro_word[0]}-{micro_word[1]}",
                        "estimated_chapters": micro_ch,
                        "priority": "WAVE_1",
                        "market_viability": "STRONG",
                    })

            # --- Standalone (Wave 2) ---
            if tier != "tertiary":
                sa_fmt, sa_runtime = select_format("standalone", topic)
                if not is_killed(config, brand_id, topic, persona, locale, sa_runtime):
                    cat_sa = make_catalog_id(brand_id, topic, persona, "standalone", 0)
                    if cat_sa not in seen_ids:
                        seen_ids.add(cat_sa)
                        t_sa, s_sa = pick_title_and_subtitle(
                            config, topic, persona, "standalone", seed_str=cat_sa
                        )
                        sa_word = RUNTIME_WORD_RANGES.get(sa_runtime, (9000, 11000))
                        sa_ch = RUNTIME_CHAPTER_DEFAULTS.get(sa_runtime, 12)
                        c_type, c_slug = get_companion("standalone", topic)
                        brand_entries.append({
                            "catalog_id": cat_sa,
                            "brand_id": brand_id,
                            "lane_id": lane_id,
                            "teacher_id": teacher_id,
                            "topic_id": topic,
                            "persona_id": persona,
                            "format_id": sa_fmt,
                            "runtime_format_id": sa_runtime,
                            "content_type": "standalone",
                            "series_id": "",
                            "series_position": 0,
                            "title": t_sa,
                            "subtitle": s_sa,
                            "price_usd": compute_price(arch, "standalone", locale, config),
                            "keywords": get_keywords(config, topic),
                            "description": make_description(
                                topic, persona, "standalone",
                                catalog_id=cat_sa,
                                brand_data=brand_data,
                                teacher_data=teacher_profiles.get(teacher_id, {}),
                                desc_templates=desc_templates,
                                runtime_format=sa_runtime,
                                companion_type=c_type,
                            ),
                            "cover_brief": make_cover_brief(arch, cover_templates),
                            "companion_type": c_type,
                            "freebie_slug": c_slug,
                            "estimated_word_count": f"{sa_word[0]}-{sa_word[1]}",
                            "estimated_chapters": sa_ch,
                            "priority": "WAVE_2",
                            "market_viability": "STRONG" if tier == "primary" else "VIABLE",
                        })

        entries.extend(brand_entries)

    return entries


def generate_summary(entries: list[dict]) -> list[dict]:
    """Produce per-brand summary rows."""
    from collections import defaultdict

    brand_lane: dict[tuple, dict] = {}
    for e in entries:
        key = (e["brand_id"], e["lane_id"])
        if key not in brand_lane:
            brand_lane[key] = {
                "brand_id": e["brand_id"],
                "lane_id": e["lane_id"],
                "total_titles": 0,
                "series_count": 0,
                "standalone_count": 0,
                "micro_count": 0,
                "deep_count": 0,
                "wave_1_count": 0,
                "wave_2_count": 0,
                "wave_3_count": 0,
            }
        row = brand_lane[key]
        row["total_titles"] += 1
        ct = e["content_type"]
        if ct == "series_book":
            row["series_count"] += 1
        elif ct == "standalone":
            row["standalone_count"] += 1
        elif ct == "micro_book":
            row["micro_count"] += 1
        elif ct == "deep_book":
            row["deep_count"] += 1
        p = e["priority"]
        if p == "WAVE_1":
            row["wave_1_count"] += 1
        elif p == "WAVE_2":
            row["wave_2_count"] += 1
        elif p == "WAVE_3":
            row["wave_3_count"] += 1

    return sorted(brand_lane.values(), key=lambda r: (r["lane_id"], r["brand_id"]))


# ---------------------------------------------------------------------------
# CSV writer
# ---------------------------------------------------------------------------
CATALOG_FIELDS = [
    "catalog_id", "brand_id", "lane_id", "teacher_id", "topic_id",
    "persona_id", "format_id", "runtime_format_id", "content_type",
    "series_id", "series_position", "title", "subtitle", "price_usd",
    "keywords", "description", "cover_brief", "companion_type",
    "freebie_slug", "estimated_word_count", "estimated_chapters",
    "priority", "market_viability",
]

SUMMARY_FIELDS = [
    "brand_id", "lane_id", "total_titles", "series_count",
    "standalone_count", "micro_count", "deep_count",
    "wave_1_count", "wave_2_count", "wave_3_count",
]


def write_csv(rows: list[dict], path: Path, fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Wrote {len(rows)} rows -> {path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Phoenix Omega Catalog Generator")
    parser.add_argument("--all-lanes", action="store_true", help="Generate for all lanes")
    parser.add_argument("--lane", type=str, default=None, help="Generate for one lane (e.g. en_US)")
    parser.add_argument("--brand", type=str, default=None, help="Generate for one brand (e.g. stabilizer_en_us)")
    parser.add_argument("--output", type=str, default="artifacts/catalog/full_catalog.csv",
                        help="Output CSV path (relative to repo root)")
    parser.add_argument("--summary", type=str, default=None,
                        help="Summary CSV path (default: <output_dir>/catalog_summary.csv)")
    args = parser.parse_args()

    if not args.all_lanes and not args.lane and not args.brand:
        print("Specify --all-lanes, --lane <lane_id>, or --brand <brand_id>")
        sys.exit(1)

    lane_filter = args.lane
    brand_filter = args.brand

    print("Phoenix Omega Catalog Generator")
    print("=" * 50)
    if args.all_lanes:
        print("Mode: All lanes")
    elif lane_filter:
        print(f"Mode: Lane filter = {lane_filter}")
    elif brand_filter:
        print(f"Mode: Brand filter = {brand_filter}")

    print("\nLoading registries...")
    entries = generate_catalog(lane_filter=lane_filter, brand_filter=brand_filter)

    print(f"\nGenerated {len(entries)} catalog entries")

    # Stats
    by_type = {}
    by_wave = {}
    by_lane = {}
    for e in entries:
        by_type[e["content_type"]] = by_type.get(e["content_type"], 0) + 1
        by_wave[e["priority"]] = by_wave.get(e["priority"], 0) + 1
        by_lane[e["lane_id"]] = by_lane.get(e["lane_id"], 0) + 1

    print("\nBy content type:")
    for k, v in sorted(by_type.items()):
        print(f"  {k}: {v}")

    print("\nBy wave:")
    for k, v in sorted(by_wave.items()):
        print(f"  {k}: {v}")

    print("\nBy lane (top 5):")
    for k, v in sorted(by_lane.items(), key=lambda x: -x[1])[:5]:
        print(f"  {k}: {v}")

    # Write catalog CSV
    out_path = REPO_ROOT / args.output
    write_csv(entries, out_path, CATALOG_FIELDS)

    # Write summary CSV
    summary = generate_summary(entries)
    summary_path = args.summary
    if not summary_path:
        summary_path = out_path.parent / "catalog_summary.csv"
    else:
        summary_path = REPO_ROOT / summary_path
    write_csv(summary, Path(summary_path), SUMMARY_FIELDS)

    print(f"\nDone. Total catalog entries: {len(entries)}")


if __name__ == "__main__":
    main()
