#!/usr/bin/env python3
"""
Phoenix Omega Weekly Production Queue
======================================
Generates 15 titles per brand per week, indefinitely.
Priority: STRONG configs first, then VIABLE.
Each "configuration" = topic x persona x engine x format.
Each config can produce MANY unique books via engine, format, and seed variation.

Usage:
    # Generate this week's queue for all brands in en_US
    python scripts/catalog/weekly_production_queue.py --lane en_US --week current

    # Generate for one brand
    python scripts/catalog/weekly_production_queue.py --brand stabilizer_en_us --week 2026-W15

    # Generate for all lanes
    python scripts/catalog/weekly_production_queue.py --all-lanes --week current

    # Dry run (show what would be produced)
    python scripts/catalog/weekly_production_queue.py --lane en_US --week current --dry-run

    # Execute pipeline for the queue (actually produce the books)
    python scripts/catalog/weekly_production_queue.py --lane en_US --week current --execute
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
_MAIN_REPO = Path("/Users/ahjan/phoenix_omega")
if not (REPO_ROOT / "config" / "brand_management").exists() and (_MAIN_REPO / "config" / "brand_management").exists():
    _CONFIG_ROOT = _MAIN_REPO
else:
    _CONFIG_ROOT = REPO_ROOT

try:
    import yaml
except ImportError:
    yaml = None


def _load_yaml(path: Path) -> Any:
    if yaml is not None:
        with open(path, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh)
    raise ImportError(f"PyYAML required to load {path.name}. pip install pyyaml")


# ---------------------------------------------------------------------------
# Registry loaders
# ---------------------------------------------------------------------------

def load_brand_registry() -> dict:
    return _load_yaml(_CONFIG_ROOT / "config/brand_management/global_brand_registry.yaml")


def load_weekly_queue_config() -> dict:
    for root in [REPO_ROOT, _CONFIG_ROOT]:
        p = root / "config/catalog/weekly_queue_config.yaml"
        if p.exists():
            return _load_yaml(p)
    raise FileNotFoundError("weekly_queue_config.yaml not found")


def load_catalog_config() -> dict:
    for root in [REPO_ROOT, _CONFIG_ROOT]:
        p = root / "config/catalog/catalog_generation_config.yaml"
        if p.exists():
            return _load_yaml(p)
    raise FileNotFoundError("catalog_generation_config.yaml not found")


# ---------------------------------------------------------------------------
# Constants from registries
# ---------------------------------------------------------------------------

ENGINES = ["spiral", "shame", "comparison", "false_alarm", "overwhelm", "grief", "watcher"]

TOPIC_DISPLAY = {
    "anxiety": "Anxiety", "boundaries": "Boundaries", "burnout": "Burnout",
    "compassion_fatigue": "Compassion Fatigue", "courage": "Courage",
    "depression": "Depression", "financial_anxiety": "Financial Anxiety",
    "financial_stress": "Financial Stress", "grief": "Grief",
    "imposter_syndrome": "Imposter Syndrome", "overthinking": "Overthinking",
    "self_worth": "Self-Worth", "sleep_anxiety": "Sleep Anxiety",
    "social_anxiety": "Social Anxiety", "somatic_healing": "Somatic Healing",
}

PERSONA_DISPLAY = {
    "corporate_managers": "Professionals", "millennial_women_professionals": "Women",
    "tech_finance_burnout": "High Performers", "gen_z_professionals": "Young Professionals",
    "healthcare_rns": "Nurses and Caregivers", "first_responders": "First Responders",
    "educators": "Educators", "working_parents": "Working Parents",
    "entrepreneurs": "Entrepreneurs", "gen_x_sandwich": "Midlife Adults",
    "gen_alpha_students": "Students", "nyc_executives": "Executives",
}

# Runtime format word counts and pricing
RUNTIME_FORMATS = {
    "micro_book_15":   {"words": 2750, "price": 0.99,  "structural": ["F015", "F003"]},
    "micro_book_20":   {"words": 3500, "price": 0.99,  "structural": ["F015", "F003"]},
    "short_book_30":   {"words": 5000, "price": 2.99,  "structural": ["F003", "F006", "F007", "F011"]},
    "standard_book":   {"words": 10000, "price": 3.99, "structural": ["F006", "F007", "F010", "F011", "F014"]},
    "extended_book_2h": {"words": 20000, "price": 9.99, "structural": ["F004", "F009", "F010", "F014"]},
    "deep_book_4h":    {"words": 40000, "price": 17.99, "structural": ["F004", "F009", "F013"]},
    "deep_book_6h":    {"words": 55000, "price": 24.99, "structural": ["F013"]},
}

# Micro formats for the "strong_micros" slot
MICRO_RUNTIMES = ["micro_book_15", "micro_book_20"]
# Standard formats for standalones
STANDALONE_RUNTIMES = ["short_book_30", "standard_book"]
# For format variations
ALL_RUNTIMES = list(RUNTIME_FORMATS.keys())

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
        "The Courage to Stay: Long-Term Resilience",
    ],
    "compassion_fatigue": [
        "When Caring Starts to Hurt",
        "The Nervous System of the Helper",
        "Compassion Fatigue vs. Burnout",
        "Empathy Without Exhaustion",
        "Somatic Recovery for Caregivers",
        "Moral Injury in Healthcare",
        "Setting Limits as a Healer",
        "Vicarious Trauma and How to Heal",
        "Rebuilding Empathy After Depletion",
        "Sustainable Compassion: A Lifelong Practice",
    ],
    "financial_anxiety": [
        "Understanding Money Anxiety",
        "The Nervous System of Financial Stress",
        "Money Shame and Where It Comes From",
        "Breaking the Scarcity Mindset",
        "Somatic Practices for Financial Calm",
        "Financial Anxiety in Relationships",
        "Building Financial Confidence Step by Step",
        "The Debt Spiral and Emotional Recovery",
        "Money Conversations Without Panic",
        "Long-Term Financial Peace and Nervous System Health",
    ],
    "financial_stress": [
        "Understanding Financial Stress Responses",
        "The Body's Reaction to Money Worries",
        "Financial Stress and Sleep",
        "Building a Financial Safety Net",
        "Somatic Tools for Money Anxiety",
        "Financial Stress in Families",
        "From Scarcity to Security",
        "Money Stress and Decision Making",
        "Financial Recovery After Crisis",
        "Building Financial Resilience for Life",
    ],
}

# Title templates per topic (from catalog_generation_config.yaml + search research)
TITLE_TEMPLATES = {
    "anxiety": [
        {"title": "The Alarm Is Lying", "subtitle_pattern": "A Nervous System Guide to {topic} Recovery for {persona}"},
        {"title": "Safe Enough", "subtitle_pattern": "How to Calm {topic} and Reclaim Your Nervous System"},
        {"title": "The Emergency That Never Comes", "subtitle_pattern": "Breaking Free from High-Functioning {topic}"},
    ],
    "burnout": [
        {"title": "Running on Fumes", "subtitle_pattern": "A Recovery Guide for {topic} and Work Exhaustion"},
        {"title": "The Collapse You Earned", "subtitle_pattern": "{topic} Recovery for People Who Can't Stop"},
        {"title": "Before You Break", "subtitle_pattern": "Escaping {topic} and Rebuilding Your Energy"},
    ],
    "sleep_anxiety": [
        {"title": "The 3 AM Mind", "subtitle_pattern": "A Guide to Overcoming Insomnia and {topic}"},
        {"title": "Permission to Rest", "subtitle_pattern": "How to Calm Racing Thoughts and Finally Sleep"},
        {"title": "The Quiet Hour", "subtitle_pattern": "Reclaiming Sleep from {topic} and Overthinking"},
    ],
    "imposter_syndrome": [
        {"title": "You're Not a Fraud", "subtitle_pattern": "Overcoming {topic} and Owning Your Worth"},
        {"title": "The Proof Was Always You", "subtitle_pattern": "An {topic} Recovery Guide for {persona}"},
        {"title": "Belonging at the Table", "subtitle_pattern": "Silencing {topic} and Claiming Your Place"},
    ],
    "social_anxiety": [
        {"title": "The Room Isn't Watching", "subtitle_pattern": "A {topic} Recovery Guide for Quiet People"},
        {"title": "Brave Enough to Show Up", "subtitle_pattern": "Overcoming {topic} and Building Real Connection"},
        {"title": "The Script Nobody Gave You", "subtitle_pattern": "How to Navigate {topic} with Confidence"},
    ],
    "self_worth": [
        {"title": "You Were Always Enough", "subtitle_pattern": "Rebuilding Self-Esteem and Reclaiming Your Worth"},
        {"title": "The Mirror Lied", "subtitle_pattern": "A Self-Love Guide to Healing Low Self-Esteem"},
        {"title": "Worthy Without Proof", "subtitle_pattern": "How to Build Unshakable {topic} and Confidence"},
    ],
    "boundaries": [
        {"title": "The No That Saved Me", "subtitle_pattern": "A Practical Guide to Setting {topic} and Finding Peace"},
        {"title": "Stop Pouring from an Empty Cup", "subtitle_pattern": "{topic} for People Pleasers and Overgivers"},
        {"title": "The Line You Draw", "subtitle_pattern": "How to Set {topic} Without Guilt or Fear"},
    ],
    "grief": [
        {"title": "The Weight of Gone", "subtitle_pattern": "A Gentle Guide to {topic}, Loss, and Healing"},
        {"title": "Still Here Without You", "subtitle_pattern": "Finding Your Way Through {topic} and Heartbreak"},
        {"title": "The Shape of Missing", "subtitle_pattern": "A {topic} Recovery Companion for the Worst Days"},
    ],
    "overthinking": [
        {"title": "The Loop Breaker", "subtitle_pattern": "How to Stop {topic} and Quiet Your Racing Mind"},
        {"title": "Your Brain Is Not the Boss", "subtitle_pattern": "A Guide to Overcoming {topic} and Mental Spirals"},
        {"title": "Thought Traffic", "subtitle_pattern": "Breaking Free from {topic}, Worry, and Analysis Paralysis"},
    ],
    "somatic_healing": [
        {"title": "The Body Remembers the Way Out", "subtitle_pattern": "{topic} and Nervous System Recovery"},
        {"title": "Unlock the Freeze", "subtitle_pattern": "A Somatic Guide to Nervous System Reset and Trauma Release"},
        {"title": "Held by the Body", "subtitle_pattern": "A {topic} Guide for Stress, Trauma, and Anxiety"},
    ],
    "depression": [
        {"title": "The Light You Forgot", "subtitle_pattern": "A Gentle Guide to Healing {topic} and Finding Hope"},
        {"title": "Still Breathing", "subtitle_pattern": "{topic} Recovery for People Running on Empty"},
        {"title": "Color Returns", "subtitle_pattern": "How to Move Through {topic} One Day at a Time"},
    ],
    "courage": [
        {"title": "The Fear That Built You", "subtitle_pattern": "Finding {topic} When Everything Feels Uncertain"},
        {"title": "Jump Scared", "subtitle_pattern": "A Guide to Building {topic} and Facing the Unknown"},
        {"title": "Bold Enough", "subtitle_pattern": "How to Find {topic} in Anxious Times"},
    ],
    "compassion_fatigue": [
        {"title": "Caring Until There's Nothing Left", "subtitle_pattern": "A {topic} Recovery Guide for Helpers"},
        {"title": "The Empty Well", "subtitle_pattern": "Healing {topic} and Emotional Exhaustion"},
        {"title": "Who Heals the Healer", "subtitle_pattern": "{topic} Recovery for {persona}"},
    ],
    "financial_anxiety": [
        {"title": "The Money Knot", "subtitle_pattern": "Untangling {topic} and Building Financial Peace"},
        {"title": "Broke and Breathing", "subtitle_pattern": "A Somatic Guide to {topic} Recovery"},
        {"title": "Worth More Than Your Balance", "subtitle_pattern": "Healing {topic} and Money Shame"},
    ],
    "financial_stress": [
        {"title": "The Money Knot", "subtitle_pattern": "Untangling {topic} and Building Financial Peace"},
        {"title": "Broke and Breathing", "subtitle_pattern": "A Somatic Guide to {topic} Recovery"},
        {"title": "Worth More Than Your Balance", "subtitle_pattern": "Healing {topic} and Money Shame"},
    ],
}

KEYWORD_TEMPLATES = {
    "anxiety": ["anxiety relief", "nervous system regulation", "calm anxiety naturally", "anxiety recovery", "high functioning anxiety", "anxiety workbook adults", "somatic anxiety"],
    "burnout": ["burnout recovery", "work exhaustion healing", "nervous system reset", "burnout book professionals", "hustle culture recovery", "stress management", "burnout prevention"],
    "sleep_anxiety": ["insomnia self help", "racing thoughts night", "sleep anxiety relief", "cant sleep book", "3am anxiety", "calm mind sleep", "bedtime anxiety"],
    "imposter_syndrome": ["imposter syndrome book", "feeling like fraud", "self doubt recovery", "imposter syndrome women", "imposter syndrome work", "confidence building", "worthy enough"],
    "social_anxiety": ["social anxiety recovery", "overcoming shyness", "introvert anxiety", "social confidence", "making friends adult", "phone anxiety", "social skills"],
    "self_worth": ["self esteem books", "self worth healing", "self love guide", "confidence building", "feeling worthless recovery", "enough self help", "body neutrality"],
    "boundaries": ["setting boundaries book", "how say no", "people pleasing recovery", "boundaries without guilt", "codependency healing", "toxic relationship boundaries", "healthy boundaries"],
    "grief": ["grief recovery book", "coping with loss", "grief healing guide", "losing loved one", "grief companion", "complicated grief", "bereavement self help"],
    "overthinking": ["stop overthinking book", "racing thoughts relief", "quiet mind guide", "analysis paralysis", "worry less book", "mental spirals", "rumination recovery"],
    "somatic_healing": ["nervous system regulation book", "somatic exercises", "vagus nerve healing", "body trauma release", "polyvagal theory guide", "somatic therapy self help", "freeze response"],
    "depression": ["depression recovery book", "feeling numb healing", "low energy guide", "depression self help", "finding hope again", "functioning depression", "mood healing"],
    "courage": ["courage building book", "facing fear guide", "brave living", "fear of change", "bold decisions", "risk taking self help", "courage practice"],
    "compassion_fatigue": ["compassion fatigue recovery", "caregiver burnout book", "empathy exhaustion", "nurse self care", "helper burnout", "vicarious trauma", "moral injury healing"],
    "financial_anxiety": ["money anxiety book", "financial stress relief", "money shame healing", "financial anxiety guide", "broke and scared", "money mindset", "financial therapy"],
    "financial_stress": ["financial stress book", "money worry relief", "financial wellness guide", "money anxiety recovery", "financial peace", "money shame healing", "financial self help"],
}


# ---------------------------------------------------------------------------
# Seed generation
# ---------------------------------------------------------------------------

def make_seed(brand_id: str, week_id: str, sequence: int) -> str:
    """Deterministic seed from brand + week + sequence."""
    raw = f"{brand_id}|{week_id}|{sequence}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def make_queue_id(brand_id: str, week_id: str, sequence: int) -> str:
    """Human-readable queue ID."""
    return f"WQ-{week_id}-{brand_id}-{sequence:03d}"


# ---------------------------------------------------------------------------
# Production history
# ---------------------------------------------------------------------------

def load_production_history(history_path: Path) -> set[str]:
    """Load set of previously produced seeds for deduplication."""
    produced_seeds: set[str] = set()
    if history_path.exists():
        with open(history_path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    produced_seeds.add(record.get("seed", ""))
                except json.JSONDecodeError:
                    continue
    return produced_seeds


def append_production_history(history_path: Path, records: list[dict]) -> None:
    """Append produced items to the history file."""
    history_path.parent.mkdir(parents=True, exist_ok=True)
    with open(history_path, "a", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# Configuration expansion
# ---------------------------------------------------------------------------

def get_brand_valid_configs(brand: dict, queue_cfg: dict) -> tuple[list[dict], list[dict]]:
    """
    For a brand, return (strong_configs, viable_configs).
    Each config is a dict with topic, persona, engine, format_id, runtime_format_id.
    """
    brand_topics = set(brand.get("primary_topics", []))
    brand_personas = set(brand.get("primary_personas", []))

    # Build kill set
    kill_tp = set()
    for k in queue_cfg.get("kill_list", {}).get("topic_persona_kills", []):
        kill_tp.add((k["topic"], k["persona"]))

    strong_clusters = queue_cfg.get("strong_clusters", [])
    viable_clusters = queue_cfg.get("viable_clusters", [])

    # Build strong topic-persona set for this brand
    strong_tp: set[tuple[str, str]] = set()
    for cluster in strong_clusters:
        topic = cluster["topic"]
        if topic not in brand_topics:
            continue
        for persona in cluster["personas"]:
            if persona not in brand_personas:
                continue
            if (topic, persona) in kill_tp:
                continue
            strong_tp.add((topic, persona))

    # Build viable topic-persona set for this brand
    viable_tp: set[tuple[str, str]] = set()
    for cluster in viable_clusters:
        topic = cluster["topic"]
        if topic not in brand_topics:
            continue
        for persona in cluster["personas"]:
            if persona not in brand_personas:
                continue
            if (topic, persona) in kill_tp:
                continue
            if (topic, persona) in strong_tp:
                continue  # already strong
            viable_tp.add((topic, persona))

    # Also add any brand topic x persona that is not in strong or viable but is valid
    for topic in brand_topics:
        for persona in brand_personas:
            if (topic, persona) in kill_tp:
                continue
            if (topic, persona) not in strong_tp and (topic, persona) not in viable_tp:
                viable_tp.add((topic, persona))

    def expand_configs(tp_set: set[tuple[str, str]]) -> list[dict]:
        configs = []
        for topic, persona in sorted(tp_set):
            for engine in ENGINES:
                for runtime_id, rt_info in RUNTIME_FORMATS.items():
                    for structural_id in rt_info["structural"]:
                        configs.append({
                            "topic_id": topic,
                            "persona_id": persona,
                            "engine": engine,
                            "format_id": structural_id,
                            "runtime_format_id": runtime_id,
                        })
        return configs

    return expand_configs(strong_tp), expand_configs(viable_tp)


# ---------------------------------------------------------------------------
# Title generation
# ---------------------------------------------------------------------------

def generate_title(topic_id: str, persona_id: str, engine: str,
                   runtime_format_id: str, seed: str, sequence: int,
                   content_type: str, series_book_num: int = 0) -> tuple[str, str]:
    """Generate a title + subtitle pair."""
    topic_display = TOPIC_DISPLAY.get(topic_id, topic_id.replace("_", " ").title())
    persona_display = PERSONA_DISPLAY.get(persona_id, persona_id.replace("_", " ").title())

    if content_type == "series" and topic_id in SERIES_BOOK_SUBTITLES:
        # Series: use series book subtitles
        subtitles = SERIES_BOOK_SUBTITLES[topic_id]
        idx = series_book_num % len(subtitles)
        series_list = SERIES_NAMES.get(topic_id, [f"The {topic_display} Series"])
        series_name = series_list[0]
        title = f"{series_name}: Book {series_book_num + 1}"
        subtitle = subtitles[idx]
        return title, subtitle

    # Standalone / micro / variation: use title templates
    templates = TITLE_TEMPLATES.get(topic_id, [
        {"title": f"The {topic_display} Reset", "subtitle_pattern": "A Guide to {topic} Recovery for {persona}"},
    ])
    # Deterministic selection based on seed
    seed_int = int(seed[:8], 16)
    template = templates[seed_int % len(templates)]

    title = template["title"]
    subtitle = template["subtitle_pattern"].format(
        topic=topic_display,
        persona=persona_display,
    )

    # For micro books, append format signal
    if runtime_format_id in MICRO_RUNTIMES:
        subtitle = subtitle.rstrip(".") + " — A Quick Guide"

    return title, subtitle


# ---------------------------------------------------------------------------
# Core queue generator
# ---------------------------------------------------------------------------

def generate_weekly_queue(brand_id: str, brand: dict, week_id: str,
                          queue_cfg: dict, catalog_cfg: dict,
                          produced_seeds: set[str]) -> list[dict]:
    """
    Generate 15 titles for one brand for one week.

    Priority order:
    1. STRONG configs not yet produced (highest confidence, ship first)
    2. STRONG configs with different engine/format variations
    3. VIABLE configs not yet produced
    4. VIABLE configs with variations
    5. New combos (fill remaining slots)

    Weekly mix:
    - 2 series installments
    - 5 STRONG-config standalones
    - 3 STRONG-config micro-books ($0.99)
    - 3 VIABLE-config standalones
    - 2 format variations
    """
    target = queue_cfg.get("titles_per_brand_per_week", 15)
    mix = queue_cfg.get("weekly_mix", {})
    n_series = mix.get("series_installments", 2)
    n_strong_standalone = mix.get("strong_standalones", 5)
    n_strong_micro = mix.get("strong_micros", 3)
    n_viable_standalone = mix.get("viable_standalones", 3)
    n_format_var = mix.get("format_variations", 2)

    strong_configs, viable_configs = get_brand_valid_configs(brand, queue_cfg)

    queue: list[dict] = []
    used_seeds: set[str] = set()
    seq = 0

    def _next_seed() -> str:
        nonlocal seq
        seq += 1
        s = make_seed(brand_id, week_id, seq)
        while s in produced_seeds or s in used_seeds:
            seq += 1
            s = make_seed(brand_id, week_id, seq)
        used_seeds.add(s)
        return s

    def _pick_config(configs: list[dict], runtime_filter: Optional[list[str]] = None) -> Optional[dict]:
        """Pick the first config whose seed hasn't been produced yet."""
        for cfg in configs:
            if runtime_filter and cfg["runtime_format_id"] not in runtime_filter:
                continue
            # Check if this exact config has been produced (by checking a synthetic seed)
            test_seed = hashlib.sha256(
                f"{brand_id}|{cfg['topic_id']}|{cfg['persona_id']}|{cfg['engine']}|{cfg['runtime_format_id']}".encode()
            ).hexdigest()[:16]
            if test_seed not in produced_seeds:
                return cfg
        # All configs produced at least once — return any with fresh week-seed
        if configs:
            seed_int = int(make_seed(brand_id, week_id, len(queue))[:8], 16)
            filtered = [c for c in configs if not runtime_filter or c["runtime_format_id"] in runtime_filter]
            if filtered:
                return filtered[seed_int % len(filtered)]
        return None

    def _build_item(cfg: dict, content_type: str, seed: str,
                    series_id: Optional[str] = None,
                    series_book_num: int = 0) -> dict:
        rt_info = RUNTIME_FORMATS.get(cfg["runtime_format_id"], {})
        price = rt_info.get("price", 3.99)
        if content_type == "series" and series_book_num == 0:
            price = 0.99  # Book 1 is always $0.99

        title, subtitle = generate_title(
            cfg["topic_id"], cfg["persona_id"], cfg["engine"],
            cfg["runtime_format_id"], seed, len(queue),
            content_type, series_book_num,
        )

        keywords = KEYWORD_TEMPLATES.get(cfg["topic_id"], [])

        return {
            "queue_id": make_queue_id(brand_id, week_id, len(queue) + 1),
            "brand_id": brand_id,
            "week_id": week_id,
            "sequence": len(queue) + 1,
            "topic_id": cfg["topic_id"],
            "persona_id": cfg["persona_id"],
            "engine": cfg["engine"],
            "format_id": cfg["format_id"],
            "runtime_format_id": cfg["runtime_format_id"],
            "content_type": content_type,
            "series_id": series_id,
            "series_book_num": series_book_num if content_type == "series" else None,
            "title": title,
            "subtitle": subtitle,
            "price_usd": price,
            "keywords": keywords[:7],
            "priority": "STRONG" if cfg in strong_configs or any(
                c["topic_id"] == cfg["topic_id"] and c["persona_id"] == cfg["persona_id"]
                for c in strong_configs
            ) else "VIABLE",
            "seed": seed,
            "estimated_word_count": rt_info.get("words", 10000),
            "arc_path": (
                f"config/source_of_truth/master_arcs/"
                f"{cfg['persona_id']}__{cfg['topic_id']}__{cfg['engine']}__{cfg['format_id']}.yaml"
            ),
        }

    # ── 1. Series installments (2) ──────────────────────────────────
    brand_topics = list(brand.get("primary_topics", []))
    for i in range(n_series):
        if not brand_topics:
            break
        topic = brand_topics[i % len(brand_topics)]
        # Determine which book in series based on week
        week_num = int(week_id.split("-W")[-1]) if "-W" in week_id else 1
        book_num = (week_num - 1) % 10  # 10-book series, cycles

        series_name_list = SERIES_NAMES.get(topic, [f"The {TOPIC_DISPLAY.get(topic, topic)} Series"])
        series_id = f"SER-{brand_id}-{topic}-{series_name_list[i % len(series_name_list)].replace(' ', '_').lower()}"

        # Pick a config for series (standard_book runtime preferred)
        series_cfg = None
        brand_personas = brand.get("primary_personas", [])
        for persona in brand_personas:
            for engine in ENGINES:
                candidate = {
                    "topic_id": topic,
                    "persona_id": persona,
                    "engine": engine,
                    "format_id": "F006",
                    "runtime_format_id": "standard_book",
                }
                series_cfg = candidate
                break
            if series_cfg:
                break

        if series_cfg:
            seed = _next_seed()
            item = _build_item(series_cfg, "series", seed, series_id, book_num)
            queue.append(item)

    # ── 2. STRONG standalones (5) ───────────────────────────────────
    for _ in range(n_strong_standalone):
        cfg = _pick_config(strong_configs, STANDALONE_RUNTIMES)
        if cfg is None:
            cfg = _pick_config(viable_configs, STANDALONE_RUNTIMES)
        if cfg is None:
            break
        seed = _next_seed()
        queue.append(_build_item(cfg, "standalone", seed))

    # ── 3. STRONG micro-books (3) ───────────────────────────────────
    for _ in range(n_strong_micro):
        cfg = _pick_config(strong_configs, MICRO_RUNTIMES)
        if cfg is None:
            cfg = _pick_config(viable_configs, MICRO_RUNTIMES)
        if cfg is None:
            break
        seed = _next_seed()
        queue.append(_build_item(cfg, "micro", seed))

    # ── 4. VIABLE standalones (3) ───────────────────────────────────
    for _ in range(n_viable_standalone):
        cfg = _pick_config(viable_configs, STANDALONE_RUNTIMES)
        if cfg is None:
            cfg = _pick_config(strong_configs, STANDALONE_RUNTIMES)
        if cfg is None:
            break
        seed = _next_seed()
        queue.append(_build_item(cfg, "standalone", seed))

    # ── 5. Format variations (2) ────────────────────────────────────
    for _ in range(n_format_var):
        # Pick from all configs with a different runtime than what we've queued
        used_runtimes = {q["runtime_format_id"] for q in queue}
        remaining_runtimes = [r for r in ALL_RUNTIMES if r not in used_runtimes]
        if not remaining_runtimes:
            remaining_runtimes = ALL_RUNTIMES
        all_configs = strong_configs + viable_configs
        cfg = _pick_config(all_configs, remaining_runtimes)
        if cfg is None:
            cfg = _pick_config(all_configs)
        if cfg is None:
            break
        seed = _next_seed()
        queue.append(_build_item(cfg, "format_variation", seed))

    return queue[:target]


# ---------------------------------------------------------------------------
# Capacity calculator
# ---------------------------------------------------------------------------

def print_capacity(brand_id: str, brand: dict, queue_cfg: dict) -> None:
    """Print capacity math for a brand."""
    strong_configs, viable_configs = get_brand_valid_configs(brand, queue_cfg)

    # Unique topic-persona pairs
    strong_tp = set()
    viable_tp = set()
    for c in strong_configs:
        strong_tp.add((c["topic_id"], c["persona_id"]))
    for c in viable_configs:
        viable_tp.add((c["topic_id"], c["persona_id"]))

    n_engines = len(ENGINES)
    n_formats = len(RUNTIME_FORMATS)
    titles_per_week = queue_cfg.get("titles_per_brand_per_week", 15)

    strong_base = len(strong_tp)
    viable_base = len(viable_tp)

    strong_with_engines = strong_base * n_engines
    viable_with_engines = viable_base * n_engines
    strong_with_formats = strong_with_engines * n_formats
    viable_with_formats = viable_with_engines * n_formats

    total_unique = strong_with_formats + viable_with_formats

    weeks_strong_base = strong_base / titles_per_week if titles_per_week else 0
    weeks_strong_engines = strong_with_engines / titles_per_week if titles_per_week else 0
    weeks_all_engines = (strong_with_engines + viable_with_engines) / titles_per_week if titles_per_week else 0
    weeks_all_formats = total_unique / titles_per_week if titles_per_week else 0

    print(f"\n  Brand: {brand_id}")
    print(f"    STRONG topic×persona pairs: {strong_base}")
    print(f"    VIABLE topic×persona pairs: {viable_base}")
    print(f"    At {titles_per_week}/week, STRONG base configs last: {weeks_strong_base:.1f} weeks")
    print(f"    With {n_engines} engines: STRONG expands to {strong_with_engines} unique books")
    print(f"    At {titles_per_week}/week: {weeks_strong_engines:.1f} weeks ({weeks_strong_engines / 52:.1f} years)")
    print(f"    All configs with engines: {strong_with_engines + viable_with_engines} unique books")
    print(f"    At {titles_per_week}/week: {weeks_all_engines:.1f} weeks ({weeks_all_engines / 52:.1f} years)")
    print(f"    With format variations: {total_unique} unique products")
    print(f"    At {titles_per_week}/week: {weeks_all_formats:.1f} weeks ({weeks_all_formats / 52:.1f} years)")
    print(f"    Conclusion: {brand_id} can produce {titles_per_week}/week for "
          f"{weeks_all_formats / 52:.0f}+ years without repeating.")


# ---------------------------------------------------------------------------
# Pipeline execution
# ---------------------------------------------------------------------------

def execute_pipeline(item: dict) -> None:
    """Run the pipeline for a single queue item."""
    out_dir = (
        REPO_ROOT / "artifacts" / "weekly_packages"
        / item["brand_id"] / item["week_id"]
    )
    books_dir = out_dir / "books"
    plans_dir = out_dir / "plans"
    books_dir.mkdir(parents=True, exist_ok=True)
    plans_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable, str(REPO_ROOT / "scripts" / "run_pipeline.py"),
        "--topic", item["topic_id"],
        "--persona", item["persona_id"],
        "--arc", item["arc_path"],
        "--quality-profile", "draft",
        "--render-book",
        "--render-dir", str(books_dir),
        "--out", str(plans_dir / f"{item['queue_id']}.json"),
    ]

    teacher_id = item.get("teacher_id", "")
    if teacher_id:
        cmd.extend(["--teacher", teacher_id])

    print(f"  [EXEC] {item['queue_id']}: {' '.join(cmd[:6])}...")
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=600)
        print(f"  [DONE] {item['queue_id']}")
    except FileNotFoundError:
        print(f"  [SKIP] run_pipeline.py not found — queue item saved but not executed")
    except subprocess.CalledProcessError as e:
        print(f"  [FAIL] {item['queue_id']}: {e.stderr[:200] if e.stderr else 'unknown error'}")
    except subprocess.TimeoutExpired:
        print(f"  [TIMEOUT] {item['queue_id']}")


# ---------------------------------------------------------------------------
# Week resolution
# ---------------------------------------------------------------------------

def resolve_week(week_arg: str) -> str:
    """Resolve 'current' to ISO week string, or validate format."""
    if week_arg == "current":
        now = datetime.now(timezone.utc)
        iso_year, iso_week, _ = now.isocalendar()
        return f"{iso_year}-W{iso_week:02d}"
    # Validate format YYYY-WNN
    if len(week_arg) == 8 and week_arg[4] == "-" and week_arg[5] == "W":
        return week_arg
    raise ValueError(f"Invalid week format: {week_arg}. Use 'current' or 'YYYY-WNN'.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Phoenix Omega Weekly Production Queue — 15 titles/brand/week, forever.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              python scripts/catalog/weekly_production_queue.py --lane en_US --week current
              python scripts/catalog/weekly_production_queue.py --brand stabilizer_en_us --week 2026-W15
              python scripts/catalog/weekly_production_queue.py --all-lanes --week current --dry-run
              python scripts/catalog/weekly_production_queue.py --lane en_US --week current --execute
        """),
    )
    parser.add_argument("--lane", type=str, help="Lane ID (e.g., en_US)")
    parser.add_argument("--brand", type=str, help="Single brand ID")
    parser.add_argument("--all-lanes", action="store_true", help="All lanes")
    parser.add_argument("--week", type=str, required=True, help="Week ID: 'current' or 'YYYY-WNN'")
    parser.add_argument("--dry-run", action="store_true", help="Show queue without writing")
    parser.add_argument("--execute", action="store_true", help="Run pipeline for each item")
    parser.add_argument("--capacity", action="store_true", help="Show capacity math per brand")
    parser.add_argument("--output", type=str, help="Output JSON file (default: stdout summary)")

    args = parser.parse_args()
    week_id = resolve_week(args.week)

    # Load registries
    brand_registry = load_brand_registry()
    queue_cfg = load_weekly_queue_config()
    catalog_cfg = load_catalog_config()

    brands_data = brand_registry.get("brands", {})

    # Filter brands
    if args.brand:
        if args.brand not in brands_data:
            print(f"ERROR: Brand '{args.brand}' not found in registry.", file=sys.stderr)
            sys.exit(1)
        selected = {args.brand: brands_data[args.brand]}
    elif args.lane:
        selected = {bid: b for bid, b in brands_data.items() if b.get("lane_id") == args.lane}
        if not selected:
            print(f"ERROR: No brands found for lane '{args.lane}'.", file=sys.stderr)
            sys.exit(1)
    elif args.all_lanes:
        selected = brands_data
    else:
        print("ERROR: Specify --brand, --lane, or --all-lanes.", file=sys.stderr)
        sys.exit(1)

    # Load production history
    history_path = REPO_ROOT / queue_cfg.get("duplication_prevention", {}).get(
        "history_file", "artifacts/catalog/production_history.jsonl"
    )
    produced_seeds = load_production_history(history_path)

    all_queues: list[dict] = []
    total_brands = len(selected)

    print(f"\n{'='*70}")
    print(f"  Phoenix Omega Weekly Production Queue")
    print(f"  Week: {week_id}  |  Brands: {total_brands}  |  Target: {queue_cfg.get('titles_per_brand_per_week', 15)}/brand")
    print(f"{'='*70}")

    for brand_id, brand in sorted(selected.items()):
        if args.capacity:
            print_capacity(brand_id, brand, queue_cfg)
            continue

        queue = generate_weekly_queue(brand_id, brand, week_id, queue_cfg, catalog_cfg, produced_seeds)
        all_queues.extend(queue)

        # Summary per brand
        strong_count = sum(1 for q in queue if q["priority"] == "STRONG")
        viable_count = sum(1 for q in queue if q["priority"] == "VIABLE")
        series_count = sum(1 for q in queue if q["content_type"] == "series")
        micro_count = sum(1 for q in queue if q["content_type"] == "micro")

        print(f"\n  {brand_id}: {len(queue)} titles")
        print(f"    STRONG: {strong_count}  VIABLE: {viable_count}  "
              f"Series: {series_count}  Micro: {micro_count}")

        for item in queue:
            ct = item["content_type"][:3].upper()
            pri = item["priority"][:1]
            rt = item["runtime_format_id"]
            print(f"    [{ct}|{pri}] {item['queue_id']}  "
                  f"{item['topic_id']:20s} {item['engine']:12s} {rt:18s} "
                  f"${item['price_usd']:.2f}  \"{item['title']}\"")

    if args.capacity:
        return

    print(f"\n{'='*70}")
    print(f"  Total: {len(all_queues)} titles across {total_brands} brands for {week_id}")
    print(f"{'='*70}")

    # Capacity summary for first brand
    if selected and not args.capacity:
        first_bid = next(iter(sorted(selected.keys())))
        print_capacity(first_bid, selected[first_bid], queue_cfg)

    # Write output
    if not args.dry_run:
        # Save queue JSON
        output_path = args.output or str(
            REPO_ROOT / "artifacts" / "catalog" / f"weekly_queue_{week_id}.json"
        )
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        with open(out_p, "w", encoding="utf-8") as fh:
            json.dump(all_queues, fh, indent=2, ensure_ascii=False)
        print(f"\n  Queue written to: {out_p}")

        # Append to production history
        history_records = []
        for item in all_queues:
            history_records.append({
                "queue_id": item["queue_id"],
                "brand_id": item["brand_id"],
                "week_id": item["week_id"],
                "topic_id": item["topic_id"],
                "persona_id": item["persona_id"],
                "engine": item["engine"],
                "format_id": item["format_id"],
                "runtime_format_id": item["runtime_format_id"],
                "seed": item["seed"],
                "produced_at": datetime.now(timezone.utc).isoformat(),
                "status": "queued",
            })
        append_production_history(history_path, history_records)
        print(f"  History appended to: {history_path}")
        print(f"  Total history records: {len(produced_seeds) + len(history_records)}")

    # Execute pipeline if requested
    if args.execute and not args.dry_run:
        print(f"\n  Executing pipeline for {len(all_queues)} items...")
        for item in all_queues:
            execute_pipeline(item)

    print()


if __name__ == "__main__":
    main()
