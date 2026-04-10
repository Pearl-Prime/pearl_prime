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


def get_weekly_plan(brand_id: str, lane: str, week_id: str, year: int = 2026) -> Optional[dict]:
    """
    Read the projected weekly production plan for a brand/lane/week from the
    rolling 12-month projection system (artifacts/projections/).

    Returns the 'planned' dict {format: quantity} for the given week,
    or None if no projection file exists (caller falls back to flat config mix).

    Example return:
        {"series_books": 5, "standalone_books": 4, "micro_books": 2,
         "manga_chapters": 2, "podcast_episodes": 1, "format_variations": 1}
    """
    projection_path = REPO_ROOT / "artifacts" / "projections" / f"{brand_id}_{lane}_{year}.json"
    if not projection_path.exists():
        return None
    try:
        with open(projection_path, "r", encoding="utf-8") as fh:
            projection = json.load(fh)
        for w in projection.get("weeks", []):
            if w.get("week") == week_id:
                return w.get("planned")
    except Exception:
        pass
    return None


def _lane_id_to_projection_lane(lane_id: str) -> str:
    """
    Map legacy lane_id values (e.g. 'en_US', 'ja_JP') to projection lane keys
    (e.g. 'english_global', 'japan') used in annual_projection_targets.yaml.
    """
    _mapping = {
        "en_US": "english_global",
        "en_GB": "english_global",
        "en_AU": "english_global",
        "de_DE": "dach",
        "de_AT": "dach",
        "de_CH": "dach",
        "fr_FR": "france",
        "es_ES": "spain",
        "es_MX": "latam",
        "es_CO": "latam",
        "es_AR": "latam",
        "pt_BR": "brazil",
        "ja_JP": "japan",
        "ko_KR": "korea",
        "zh_TW": "taiwan",
        "zh_HK": "taiwan",
        "zh_CN": "china",
        "hu_HU": "hungary",
        "it_IT": "italy",
        # Projection lane keys pass through unchanged
        "english_global": "english_global",
        "dach": "dach",
        "france": "france",
        "spain": "spain",
        "italy": "italy",
        "latam": "latam",
        "brazil": "brazil",
        "japan": "japan",
        "korea": "korea",
        "taiwan": "taiwan",
        "china": "china",
        "hungary": "hungary",
    }
    return _mapping.get(lane_id, lane_id)


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
    "adhd_focus": "ADHD & Focus", "anxiety": "Anxiety", "boundaries": "Boundaries",
    "burnout": "Burnout", "compassion_fatigue": "Compassion Fatigue", "courage": "Courage",
    "depression": "Depression", "financial_anxiety": "Financial Anxiety",
    "financial_stress": "Financial Stress", "grief": "Grief",
    "imposter_syndrome": "Imposter Syndrome", "mindfulness": "Mindfulness",
    "overthinking": "Overthinking", "self_worth": "Self-Worth",
    "sleep_anxiety": "Sleep Anxiety", "social_anxiety": "Social Anxiety",
    "somatic_healing": "Somatic Healing",
}

PERSONA_DISPLAY = {
    "corporate_managers": "Professionals", "millennial_women_professionals": "Women",
    "tech_finance_burnout": "High Performers", "gen_z_professionals": "Young Professionals",
    "gen_z_student": "College Students", "healthcare_rns": "Nurses and Caregivers",
    "first_responders": "First Responders", "educators": "Educators",
    "working_parents": "Working Parents", "entrepreneurs": "Entrepreneurs",
    "gen_x_sandwich": "Midlife Adults", "gen_alpha_students": "Students",
    "nyc_executives": "Executives",
}

# Persona subtitle strategy (from persona_in_titles_strategy_research.md):
# 70% persona-subtitle, 20% situation-subtitle, 10% generic
# Per-market: JP/KR prefer universal titles; US/DE/FR respond to persona targeting
PERSONA_SUBTITLE_MODE = {
    # "always" = append "for {persona}" if not already in subtitle
    # "never" = never add persona to subtitle (keep generic)
    # "situation" = use situation phrase instead of persona label
    "healthcare_rns": "always",        # "for Nurses and Caregivers" — high specificity
    "first_responders": "always",      # "for First Responders" — high specificity
    "educators": "always",             # "for Educators" — high specificity
    "working_parents": "always",       # "for Working Parents" — clear audience
    "corporate_managers": "situation",  # "for Busy Professionals" — broader
    "entrepreneurs": "situation",       # "for People Who Can't Stop" — aspirational
    "millennial_women_professionals": "situation",  # "for Women Who Do Too Much"
    "tech_finance_burnout": "situation",  # "for High Performers"
    "gen_z_professionals": "situation",   # "for Your Twenties"
    "gen_z_student": "always",           # "for College Students"
    "gen_alpha_students": "always",       # "for Students"
    "gen_x_sandwich": "situation",        # "for the Sandwich Generation"
    "nyc_executives": "situation",        # "for Leaders Under Pressure"
}

# Situation phrases (used when mode = "situation")
PERSONA_SITUATION = {
    "corporate_managers": "for Busy Professionals",
    "entrepreneurs": "for People Who Can't Stop",
    "millennial_women_professionals": "for Women Who Do Too Much",
    "tech_finance_burnout": "for High Performers",
    "gen_z_professionals": "for Your Twenties",
    "gen_x_sandwich": "for the Sandwich Generation",
    "nyc_executives": "for Leaders Under Pressure",
}

# Lanes where persona targeting is suppressed (prefer universal titles)
PERSONA_SUPPRESS_LANES = {"ja_JP", "ko_KR"}

# Runtime format word counts and pricing
RUNTIME_FORMATS = {
    # Text ebook formats
    "micro_book_15":   {"words": 2750, "price": 0.99,  "structural": ["F015", "F003"], "type": "ebook"},
    "micro_book_20":   {"words": 3500, "price": 0.99,  "structural": ["F015", "F003"], "type": "ebook"},
    "short_book_30":   {"words": 5000, "price": 2.99,  "structural": ["F003", "F006", "F007", "F011"], "type": "ebook"},
    "standard_book":   {"words": 10000, "price": 3.99, "structural": ["F006", "F007", "F010", "F011", "F014"], "type": "ebook"},
    "extended_book_2h": {"words": 20000, "price": 9.99, "structural": ["F004", "F009", "F010", "F014"], "type": "ebook"},
    "deep_book_4h":    {"words": 40000, "price": 17.99, "structural": ["F004", "F009", "F013"], "type": "ebook"},
    "deep_book_6h":    {"words": 55000, "price": 24.99, "structural": ["F013"], "type": "ebook"},
    # Manga/webtoon formats (JP-primary)
    "manga_episode":   {"panels": 12, "price": 0.00,  "structural": ["MF01"], "type": "manga"},  # free webtoon episode
    "manga_volume":    {"panels": 40, "price": 4.99,  "structural": ["MF02"], "type": "manga"},  # tankōbon collected volume
    "manga_micro":     {"panels": 5,  "price": 0.00,  "structural": ["MF03"], "type": "manga"},  # short episode (LINE Manga)
}

# Micro formats for the "strong_micros" slot
MICRO_RUNTIMES = ["micro_book_15", "micro_book_20"]
# Standard formats for standalones
STANDALONE_RUNTIMES = ["short_book_30", "standard_book"]
# For format variations
ALL_RUNTIMES = list(RUNTIME_FORMATS.keys())
# Manga formats for JP lane
MANGA_RUNTIMES = ["manga_episode", "manga_volume", "manga_micro"]
MANGA_STANDALONE_RUNTIMES = ["manga_volume"]
MANGA_MICRO_RUNTIMES = ["manga_episode", "manga_micro"]

# Manga-specific series names (iyashikei therapeutic manga)
MANGA_SERIES_NAMES = {
    "anxiety": ["The Quiet Signal", "Breath Between Panels"],
    "burnout": ["Ashes to Still", "The Empty Desk"],
    "sleep_anxiety": ["The 2 AM Scroll", "Moonlit Breath"],
    "imposter_syndrome": ["The Wrong Room", "Mirror Image"],
    "overthinking": ["The Loop", "Thought Spiral"],
    "self_worth": ["Enough", "The Cracked Mirror"],
    "boundaries": ["The Line", "No with Grace"],
    "grief": ["The Empty Chair", "Still Water"],
    "depression": ["Grey Morning", "The Slow Return"],
    "social_anxiety": ["The Doorway", "Invisible Wall"],
    "courage": ["The First Step", "Brave Enough"],
    "somatic_healing": ["Body Map", "The Tension Backpack"],
    "mindfulness": ["Present Tense", "The Pause"],
    "adhd_focus": ["Scattered", "The Focus Thief"],
    "compassion_fatigue": ["Empty Cup", "The Last Drop"],
    "financial_anxiety": ["The Number", "Broke and Breathing"],
    "financial_stress": ["Paycheck to Paycheck", "The Budget Spiral"],
}

# Manga title templates (for graphic novel EPUBs and webtoon series)
MANGA_TITLE_TEMPLATES = {
    "anxiety": [
        {"title": "Quiet Signal", "subtitle_pattern": "A Therapeutic Manga About {topic} and the Nervous System"},
        {"title": "The Alarm in Her Chest", "subtitle_pattern": "An Iyashikei Manga for {topic} Recovery"},
        {"title": "Breathe Between Panels", "subtitle_pattern": "A Healing Manga About Living with {topic}"},
    ],
    "burnout": [
        {"title": "The Empty Desk", "subtitle_pattern": "A Therapeutic Manga About {topic} and Recovery"},
        {"title": "Ashes to Still", "subtitle_pattern": "An Iyashikei Manga for {topic} Healing"},
        {"title": "Running on Empty", "subtitle_pattern": "A Healing Manga About {topic} and Rest"},
    ],
    "sleep_anxiety": [
        {"title": "The 2 AM Scroll", "subtitle_pattern": "A Therapeutic Manga About {topic} and Rest"},
        {"title": "Moonlit Breath", "subtitle_pattern": "An Iyashikei Manga for {topic} Recovery"},
        {"title": "Dark Room, Still Mind", "subtitle_pattern": "A Healing Manga About {topic}"},
    ],
    "imposter_syndrome": [
        {"title": "The Wrong Room", "subtitle_pattern": "A Therapeutic Manga About {topic}"},
        {"title": "Mirror Image", "subtitle_pattern": "An Iyashikei Manga for {topic} Recovery"},
        {"title": "Who Let Me In", "subtitle_pattern": "A Healing Manga About {topic} and Belonging"},
    ],
    "overthinking": [
        {"title": "The Loop", "subtitle_pattern": "A Therapeutic Manga About {topic} and Mental Spirals"},
        {"title": "Thought Spiral", "subtitle_pattern": "An Iyashikei Manga for {topic} Recovery"},
        {"title": "The Reply Draft", "subtitle_pattern": "A Healing Manga About {topic}"},
    ],
    "self_worth": [
        {"title": "The Cracked Mirror", "subtitle_pattern": "A Therapeutic Manga About {topic}"},
        {"title": "Enough", "subtitle_pattern": "An Iyashikei Manga for Rebuilding {topic}"},
        {"title": "Kintsugi Heart", "subtitle_pattern": "A Healing Manga About {topic} and Gold"},
    ],
    "boundaries": [
        {"title": "The Line", "subtitle_pattern": "A Therapeutic Manga About Setting {topic}"},
        {"title": "No with Grace", "subtitle_pattern": "An Iyashikei Manga for {topic}"},
        {"title": "The Open Door", "subtitle_pattern": "A Healing Manga About {topic} and Peace"},
    ],
    "grief": [
        {"title": "The Empty Chair", "subtitle_pattern": "A Therapeutic Manga About {topic} and Loss"},
        {"title": "Still Water", "subtitle_pattern": "An Iyashikei Manga for {topic} Recovery"},
        {"title": "Phantom Warmth", "subtitle_pattern": "A Healing Manga About Living with {topic}"},
    ],
    "depression": [
        {"title": "Grey Morning", "subtitle_pattern": "A Therapeutic Manga About {topic}"},
        {"title": "The Slow Return", "subtitle_pattern": "An Iyashikei Manga for {topic} Recovery"},
        {"title": "Color Comes Back", "subtitle_pattern": "A Healing Manga About {topic} and Hope"},
    ],
    "courage": [
        {"title": "The First Step", "subtitle_pattern": "A Therapeutic Manga About {topic}"},
        {"title": "Brave Enough", "subtitle_pattern": "An Iyashikei Manga for Finding {topic}"},
        {"title": "The Raised Hand", "subtitle_pattern": "A Healing Manga About {topic} and Voice"},
    ],
    "mindfulness": [
        {"title": "Present Tense", "subtitle_pattern": "A Therapeutic Manga About {topic}"},
        {"title": "The Pause", "subtitle_pattern": "An Iyashikei Manga for {topic} Practice"},
        {"title": "Here Not There", "subtitle_pattern": "A Healing Manga About {topic} and Presence"},
    ],
    "adhd_focus": [
        {"title": "Scattered", "subtitle_pattern": "A Therapeutic Manga About {topic}"},
        {"title": "The Focus Thief", "subtitle_pattern": "An Iyashikei Manga for {topic} Recovery"},
        {"title": "Brain on Fire", "subtitle_pattern": "A Healing Manga About Living with {topic}"},
    ],
    "somatic_healing": [
        {"title": "Body Map", "subtitle_pattern": "A Therapeutic Manga About {topic}"},
        {"title": "The Tension Backpack", "subtitle_pattern": "An Iyashikei Manga for {topic}"},
        {"title": "Unlock", "subtitle_pattern": "A Healing Manga About {topic} and the Nervous System"},
    ],
    "social_anxiety": [
        {"title": "The Doorway", "subtitle_pattern": "A Therapeutic Manga About {topic}"},
        {"title": "Invisible Wall", "subtitle_pattern": "An Iyashikei Manga for {topic} Recovery"},
        {"title": "Show Up", "subtitle_pattern": "A Healing Manga About {topic} and Connection"},
    ],
}

SERIES_NAMES = {
    "adhd_focus": ["The Focus Reset Series", "Wired Different Collection"],
    "anxiety": ["The Steady Ground Collection", "Calm Signal Series"],
    "burnout": ["The Recovery Road Series", "Ashes to Energy Collection"],
    "sleep_anxiety": ["The Midnight Reset Series", "Quiet Night Collection", "Sleep and Body Collection"],
    "imposter_syndrome": ["The Belonging Series", "Own Your Seat Collection"],
    "social_anxiety": ["The Brave Room Series", "Show Up Collection"],
    "self_worth": ["The Enough Series", "Mirror Work Collection"],
    "boundaries": ["The Sacred Line Series", "No with Grace Collection"],
    "grief": ["The After Collection", "Still Standing Series", "The Long Goodbye Series", "The Unnamed Loss Collection"],
    "mindfulness": ["The Present Moment Series", "Stillness Practice Collection"],
    "overthinking": ["The Quiet Mind Series", "Loop Breaker Collection"],
    "somatic_healing": ["The Body Knows Series", "Nervous System Reset Collection"],
    "depression": ["The Slow Return Series", "Light Ahead Collection"],
    "courage": ["The Bold Step Series", "Brave Enough Collection"],
    "compassion_fatigue": ["The Healer's Rest Series", "Empty Well Collection"],
    "financial_anxiety": ["The Money Peace Series", "Worth Beyond Balance Collection"],
    "financial_stress": ["The Paycheck Reset Series", "Financial Ground Collection"],
}

SERIES_BOOK_SUBTITLES = {
    "adhd_focus": [
        "Understanding Your ADHD Brain and How It Works",
        "Focus Strategies That Work with Your Wiring",
        "ADHD and Overwhelm: Calming the Input Flood",
        "Executive Function Recovery for Daily Life",
        "The Dopamine Connection: Why Motivation Disappears",
        "ADHD Time Blindness and How to Navigate It",
        "Hyperfocus and Burnout: Managing the Extremes",
        "ADHD in Relationships and Social Life",
        "Building Routines That Survive the ADHD Brain",
        "Long-Term ADHD Management Without Shame",
    ],
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
        "Understanding Paycheck-to-Paycheck Stress",
        "The Body Under Financial Pressure",
        "Financial Stress and Sleep Disruption",
        "Building a Stability Plan on a Tight Budget",
        "Somatic Tools for Money Pressure",
        "Financial Stress in Families and Relationships",
        "From Survival Mode to Financial Ground",
        "Making Decisions Under Financial Pressure",
        "Financial Recovery After Job Loss or Crisis",
        "Building Long-Term Financial Resilience",
    ],
    "mindfulness": [
        "What Mindfulness Actually Is (Not What You Think)",
        "Your First Meditation: A No-Pressure Guide",
        "Mindfulness for Anxiety and Racing Thoughts",
        "The Body Scan: Listening to What You Carry",
        "Mindfulness in Daily Life: Not Just Cushion Time",
        "When Meditation Feels Impossible: Common Blocks",
        "Mindful Breathing for Stress and Overwhelm",
        "Presence Practice for Overthinkers",
        "Mindfulness and Sleep: Winding Down the Mind",
        "A Lifelong Mindfulness Practice: Beyond the Basics",
    ],
}

# Title templates per topic (from catalog_generation_config.yaml + search research)
TITLE_TEMPLATES = {
    "adhd_focus": [
        {"title": "The Focus Thief", "subtitle_pattern": "Understanding {topic} and Reclaiming Your Attention"},
        {"title": "Scattered but Whole", "subtitle_pattern": "A Neurodivergent Guide to {topic} and Self-Acceptance"},
        {"title": "Brain on Fire", "subtitle_pattern": "Managing {topic} Overwhelm and Sensory Overload"},
        {"title": "Not Lazy, Wired Different", "subtitle_pattern": "An {topic} Guide for Adults Who Were Never Diagnosed"},
        {"title": "The Dopamine Debt", "subtitle_pattern": "How {topic} Hijacks Motivation and How to Get It Back"},
        {"title": "When Focus Fights Back", "subtitle_pattern": "A Somatic Approach to {topic} and Executive Function"},
        {"title": "Attention Is Not a Choice", "subtitle_pattern": "An {topic} Recovery Guide for {persona}"},
        {"title": "The ADHD Reset", "subtitle_pattern": "Daily Strategies for {topic} and Neurodivergent Burnout"},
        {"title": "Hyperfocus Hangover", "subtitle_pattern": "Managing the Extremes of {topic}"},
        {"title": "Wired for Chaos", "subtitle_pattern": "How to Build Structure with an {topic} Brain"},
    ],
    "anxiety": [
        {"title": "The Alarm Is Lying", "subtitle_pattern": "A Nervous System Guide to {topic} Recovery for {persona}"},
        {"title": "Safe Enough", "subtitle_pattern": "How to Calm {topic} and Reclaim Your Nervous System"},
        {"title": "The Emergency That Never Comes", "subtitle_pattern": "Breaking Free from High-Functioning {topic}"},
        {"title": "Wired for Worry", "subtitle_pattern": "Understanding Your {topic} Response and How to Rewire It"},
        {"title": "The Calm After", "subtitle_pattern": "A Body-Based Guide to {topic} Recovery"},
        {"title": "False Alarm", "subtitle_pattern": "When Your Nervous System Lies About Danger"},
        {"title": "Steady Ground", "subtitle_pattern": "Finding Calm in the Middle of {topic}"},
        {"title": "The Panic You Survived", "subtitle_pattern": "How to Stop {topic} from Running Your Life"},
        {"title": "Breath Before the Storm", "subtitle_pattern": "Somatic Tools for {topic} and Overwhelm"},
        {"title": "Quiet Enough", "subtitle_pattern": "A {topic} Recovery Guide for Overthinkers"},
    ],
    "burnout": [
        {"title": "Running on Fumes", "subtitle_pattern": "A Recovery Guide for {topic} and Work Exhaustion"},
        {"title": "The Collapse You Earned", "subtitle_pattern": "{topic} Recovery for People Who Can't Stop"},
        {"title": "Before You Break", "subtitle_pattern": "Escaping {topic} and Rebuilding Your Energy"},
        {"title": "Empty Battery", "subtitle_pattern": "A Nervous System Reset for {topic} and Exhaustion"},
        {"title": "The Rest You Owe Yourself", "subtitle_pattern": "Recovering from {topic} Without Guilt"},
        {"title": "Ashes to Energy", "subtitle_pattern": "Rebuilding After {topic} and Total Depletion"},
        {"title": "The Wall", "subtitle_pattern": "What Happens When {topic} Catches Up"},
        {"title": "Hustle Hangover", "subtitle_pattern": "A Recovery Plan for {topic} and Overwork"},
        {"title": "Not Lazy, Depleted", "subtitle_pattern": "Understanding {topic} and Reclaiming Your Life"},
        {"title": "The Slow Return", "subtitle_pattern": "How to Come Back from {topic} Without Burning Again"},
    ],
    "sleep_anxiety": [
        {"title": "The 3 AM Mind", "subtitle_pattern": "A Guide to Overcoming Insomnia and {topic}"},
        {"title": "Permission to Rest", "subtitle_pattern": "How to Calm Racing Thoughts and Finally Sleep"},
        {"title": "The Quiet Hour", "subtitle_pattern": "Reclaiming Sleep from {topic} and Overthinking"},
        {"title": "Dark Room, Loud Brain", "subtitle_pattern": "A Somatic Guide to Beating {topic}"},
        {"title": "Sleep Is Not a Reward", "subtitle_pattern": "How to Break the {topic} Cycle"},
        {"title": "The Pillow Wars", "subtitle_pattern": "Winning the Battle Against {topic} and Insomnia"},
        {"title": "Drift", "subtitle_pattern": "A Body-Based Approach to Overcoming {topic}"},
        {"title": "Lights Out, Mind On", "subtitle_pattern": "A Practical Guide to Silencing {topic}"},
        {"title": "The Night Shift", "subtitle_pattern": "How Your Body Keeps You Awake and How to Stop It"},
        {"title": "Tired of Being Tired", "subtitle_pattern": "{topic} Recovery for Exhausted Minds"},
    ],
    "imposter_syndrome": [
        {"title": "You're Not a Fraud", "subtitle_pattern": "Overcoming {topic} and Owning Your Worth"},
        {"title": "The Proof Was Always You", "subtitle_pattern": "An {topic} Recovery Guide for {persona}"},
        {"title": "Belonging at the Table", "subtitle_pattern": "Silencing {topic} and Claiming Your Place"},
        {"title": "The Mask You Wore", "subtitle_pattern": "How {topic} Kept You Small and How to Break Free"},
        {"title": "Earned, Not Faked", "subtitle_pattern": "Overcoming {topic} and Owning Your Success"},
        {"title": "Who Let Me In", "subtitle_pattern": "A Guide to Dismantling {topic} from the Inside"},
        {"title": "The Competence Gap", "subtitle_pattern": "Why {topic} Lies About What You Know"},
        {"title": "Own Your Seat", "subtitle_pattern": "How to Silence {topic} and Show Up Fully"},
        {"title": "The Credential Trap", "subtitle_pattern": "When No Amount of Proof Defeats {topic}"},
        {"title": "Enough Already", "subtitle_pattern": "A Nervous System Approach to {topic} Recovery"},
    ],
    "social_anxiety": [
        {"title": "The Room Isn't Watching", "subtitle_pattern": "A {topic} Recovery Guide for Quiet People"},
        {"title": "Brave Enough to Show Up", "subtitle_pattern": "Overcoming {topic} and Building Real Connection"},
        {"title": "The Script Nobody Gave You", "subtitle_pattern": "How to Navigate {topic} with Confidence"},
        {"title": "Small Talk Survival", "subtitle_pattern": "A Practical Guide to Overcoming {topic}"},
        {"title": "Visible Without Fear", "subtitle_pattern": "How to Stop {topic} from Shrinking Your Life"},
        {"title": "The First Word", "subtitle_pattern": "Breaking Through {topic} One Conversation at a Time"},
        {"title": "Wallflower to Bloom", "subtitle_pattern": "A Body-Based Approach to {topic} Recovery"},
        {"title": "The Exit Plan You Don't Need", "subtitle_pattern": "Overcoming {topic} and Staying Present"},
        {"title": "Nervous and Going Anyway", "subtitle_pattern": "A Guide to Living with {topic}"},
        {"title": "The Eyes on You", "subtitle_pattern": "What {topic} Gets Wrong About Being Seen"},
    ],
    "self_worth": [
        {"title": "You Were Always Enough", "subtitle_pattern": "Rebuilding Self-Esteem and Reclaiming Your Worth"},
        {"title": "The Mirror Lied", "subtitle_pattern": "A Self-Love Guide to Healing Low Self-Esteem"},
        {"title": "Worthy Without Proof", "subtitle_pattern": "How to Build Unshakable {topic} and Confidence"},
        {"title": "The Measuring Stops Here", "subtitle_pattern": "Breaking Free from the {topic} Deficit"},
        {"title": "Not for Sale", "subtitle_pattern": "Reclaiming Your {topic} from Performance Culture"},
        {"title": "Inherent", "subtitle_pattern": "A Guide to {topic} That Doesn't Depend on Achievement"},
        {"title": "The Comparison Cure", "subtitle_pattern": "How to Stop Measuring and Start Living"},
        {"title": "Unearned and Deserved", "subtitle_pattern": "A Radical Approach to {topic} Recovery"},
        {"title": "Before the Grade", "subtitle_pattern": "Rediscovering {topic} Beyond Performance"},
        {"title": "Already Whole", "subtitle_pattern": "A Somatic Guide to Rebuilding {topic}"},
    ],
    "boundaries": [
        {"title": "The No That Saved Me", "subtitle_pattern": "A Practical Guide to Setting {topic} and Finding Peace"},
        {"title": "Stop Pouring from an Empty Cup", "subtitle_pattern": "{topic} for People Pleasers and Overgivers"},
        {"title": "The Line You Draw", "subtitle_pattern": "How to Set {topic} Without Guilt or Fear"},
        {"title": "Sacred Limits", "subtitle_pattern": "A Guide to {topic} That Protect Without Isolating"},
        {"title": "Not Your Emergency", "subtitle_pattern": "How to Set {topic} When Everyone Needs Something"},
        {"title": "The Fence You Build", "subtitle_pattern": "A Body-Based Guide to Healthy {topic}"},
        {"title": "Guard Your Peace", "subtitle_pattern": "Setting {topic} in Relationships, Work, and Life"},
        {"title": "Kind and Clear", "subtitle_pattern": "How to Say No Without Being the Villain"},
        {"title": "The Open Door Problem", "subtitle_pattern": "Why {topic} Feel Impossible and How to Start"},
        {"title": "Protect What Matters", "subtitle_pattern": "A {topic} Guide for People Who Give Too Much"},
    ],
    "grief": [
        {"title": "The Weight of Gone", "subtitle_pattern": "A Gentle Guide to {topic}, Loss, and Healing"},
        {"title": "Still Here Without You", "subtitle_pattern": "Finding Your Way Through {topic} and Heartbreak"},
        {"title": "The Shape of Missing", "subtitle_pattern": "A {topic} Recovery Companion for the Worst Days"},
        {"title": "Grief Has No Schedule", "subtitle_pattern": "A Guide to Healing Loss on Your Own Timeline"},
        {"title": "The Empty Chair", "subtitle_pattern": "Learning to Live with {topic} and Absence"},
        {"title": "Love After Loss", "subtitle_pattern": "How to Carry {topic} Without Being Crushed by It"},
        {"title": "The Wave That Comes", "subtitle_pattern": "Understanding {topic} and Finding Solid Ground"},
        {"title": "Not Getting Over It", "subtitle_pattern": "A {topic} Guide for People Tired of Being Told to Move On"},
        {"title": "Phantom Presence", "subtitle_pattern": "Living with {topic} and the People We Still Feel"},
        {"title": "After the Funeral", "subtitle_pattern": "What Nobody Tells You About Long-Term {topic}"},
    ],
    "overthinking": [
        {"title": "The Loop Breaker", "subtitle_pattern": "How to Stop {topic} and Quiet Your Racing Mind"},
        {"title": "Your Brain Is Not the Boss", "subtitle_pattern": "A Guide to Overcoming {topic} and Mental Spirals"},
        {"title": "Thought Traffic", "subtitle_pattern": "Breaking Free from {topic}, Worry, and Analysis Paralysis"},
        {"title": "The Replay Button", "subtitle_pattern": "How to Stop {topic} from Hijacking Your Day"},
        {"title": "Analysis Paralysis", "subtitle_pattern": "A Practical Guide to Escaping {topic}"},
        {"title": "The Mind Won't Quit", "subtitle_pattern": "Somatic Tools for {topic} and Rumination"},
        {"title": "One Thought Too Many", "subtitle_pattern": "How to Break the {topic} Cycle"},
        {"title": "Decision Made", "subtitle_pattern": "How to Move Past {topic} and Into Action"},
        {"title": "The Draft You Never Send", "subtitle_pattern": "Overcoming {topic} in Communication and Life"},
        {"title": "Quieter Than Yesterday", "subtitle_pattern": "A Week-by-Week Guide to Reducing {topic}"},
    ],
    "somatic_healing": [
        {"title": "The Body Remembers the Way Out", "subtitle_pattern": "{topic} and Nervous System Recovery"},
        {"title": "Unlock the Freeze", "subtitle_pattern": "A Somatic Guide to Nervous System Reset and Trauma Release"},
        {"title": "Held by the Body", "subtitle_pattern": "A {topic} Guide for Stress, Trauma, and Anxiety"},
        {"title": "Your Nervous System Is Talking", "subtitle_pattern": "How to Listen and Heal with {topic}"},
        {"title": "The Tension You Carry", "subtitle_pattern": "A {topic} Guide for Chronic Stress and Pain"},
        {"title": "Reset", "subtitle_pattern": "Vagus Nerve Exercises and {topic} for Daily Calm"},
        {"title": "Thaw", "subtitle_pattern": "Coming Back to Life After Freeze, Shutdown, and Numbness"},
        {"title": "Body First", "subtitle_pattern": "Why {topic} Works When Talk Therapy Alone Doesn't"},
        {"title": "The Shake Off", "subtitle_pattern": "A {topic} Guide to Releasing Stored Stress"},
        {"title": "Wired for Safety", "subtitle_pattern": "How Your Nervous System Heals Through {topic}"},
    ],
    "depression": [
        {"title": "The Light You Forgot", "subtitle_pattern": "A Gentle Guide to Healing {topic} and Finding Hope"},
        {"title": "Still Breathing", "subtitle_pattern": "{topic} Recovery for People Running on Empty"},
        {"title": "Color Returns", "subtitle_pattern": "How to Move Through {topic} One Day at a Time"},
        {"title": "The Flat Morning", "subtitle_pattern": "A Guide to Getting Up When {topic} Holds You Down"},
        {"title": "Numb and Navigating", "subtitle_pattern": "Living with High-Functioning {topic}"},
        {"title": "The Grey Season", "subtitle_pattern": "A Somatic Approach to {topic} Recovery"},
        {"title": "Small Movements", "subtitle_pattern": "How Tiny Steps Break Through {topic}"},
        {"title": "Not Fine", "subtitle_pattern": "A Guide to {topic} for People Who Keep Saying They're Okay"},
        {"title": "Below the Surface", "subtitle_pattern": "Understanding {topic} and the Body's Role in Healing"},
        {"title": "The First Good Day", "subtitle_pattern": "What {topic} Recovery Actually Looks Like"},
    ],
    "courage": [
        {"title": "The Fear That Built You", "subtitle_pattern": "Finding {topic} When Everything Feels Uncertain"},
        {"title": "Jump Scared", "subtitle_pattern": "A Guide to Building {topic} and Facing the Unknown"},
        {"title": "Bold Enough", "subtitle_pattern": "How to Find {topic} in Anxious Times"},
        {"title": "The Raised Hand", "subtitle_pattern": "A Guide to {topic} for People Who Stay Silent"},
        {"title": "Scared and Starting", "subtitle_pattern": "How to Act with {topic} Before You Feel Ready"},
        {"title": "The Other Side of Fear", "subtitle_pattern": "What Happens When You Choose {topic}"},
        {"title": "Brave Is a Verb", "subtitle_pattern": "A Daily Practice Guide for Building {topic}"},
        {"title": "The Leap Year", "subtitle_pattern": "Finding {topic} in Uncertain Times"},
        {"title": "Voice Unlocked", "subtitle_pattern": "How to Speak Up When {topic} Feels Impossible"},
        {"title": "Trembling and Going", "subtitle_pattern": "A Somatic Guide to Everyday {topic}"},
    ],
    "compassion_fatigue": [
        {"title": "Caring Until There's Nothing Left", "subtitle_pattern": "A {topic} Recovery Guide for Helpers"},
        {"title": "The Empty Well", "subtitle_pattern": "Healing {topic} and Emotional Exhaustion"},
        {"title": "Who Heals the Healer", "subtitle_pattern": "{topic} Recovery for {persona}"},
        {"title": "Empathy Overdraft", "subtitle_pattern": "When {topic} Drains Everything You Have"},
        {"title": "The Helper's Burnout", "subtitle_pattern": "A Somatic Guide to {topic} Recovery"},
        {"title": "Boundaries for Caregivers", "subtitle_pattern": "How to Give Without Losing Yourself to {topic}"},
        {"title": "Refill First", "subtitle_pattern": "A {topic} Recovery Plan for Nurses, Teachers, and Helpers"},
        {"title": "The Cost of Caring", "subtitle_pattern": "Understanding {topic} and What to Do About It"},
        {"title": "Numb to Need", "subtitle_pattern": "When {topic} Turns Empathy Into Exhaustion"},
        {"title": "Your Turn to Heal", "subtitle_pattern": "A {topic} Guide for People Who Put Everyone First"},
    ],
    "financial_anxiety": [
        {"title": "The Money Knot", "subtitle_pattern": "Untangling {topic} and Building Financial Peace"},
        {"title": "Broke and Breathing", "subtitle_pattern": "A Somatic Guide to {topic} Recovery"},
        {"title": "Worth More Than Your Balance", "subtitle_pattern": "Healing {topic} and Money Shame"},
        {"title": "The Number You Avoid", "subtitle_pattern": "How to Face {topic} Without Spiraling"},
        {"title": "Debt and Breath", "subtitle_pattern": "A Nervous System Approach to {topic}"},
        {"title": "Rich in Everything but Calm", "subtitle_pattern": "Understanding {topic} and Finding Peace"},
        {"title": "Money on the Mind", "subtitle_pattern": "Breaking the {topic} Thought Loop"},
        {"title": "The Safety Net", "subtitle_pattern": "How to Build Financial Security Despite {topic}"},
        {"title": "Not About the Numbers", "subtitle_pattern": "A Somatic Guide to Healing {topic}"},
        {"title": "Scarcity Thinking", "subtitle_pattern": "How {topic} Hijacks Your Decisions"},
    ],
    "financial_stress": [
        {"title": "The Money Knot", "subtitle_pattern": "Untangling {topic} and Building Financial Peace"},
        {"title": "Broke and Breathing", "subtitle_pattern": "A Somatic Guide to {topic} Recovery"},
        {"title": "Worth More Than Your Balance", "subtitle_pattern": "Healing {topic} and Money Shame"},
        {"title": "Paycheck to Paycheck", "subtitle_pattern": "A Calm Guide to Surviving {topic}"},
        {"title": "The Budget Spiral", "subtitle_pattern": "How {topic} Controls Your Life and How to Take It Back"},
        {"title": "Earning Enough, Feeling Broke", "subtitle_pattern": "Understanding Hidden {topic}"},
        {"title": "Money and Meaning", "subtitle_pattern": "A Guide to {topic} Recovery for {persona}"},
        {"title": "The Cost of Living", "subtitle_pattern": "How to Navigate {topic} with Less Panic"},
        {"title": "Financial Calm", "subtitle_pattern": "A Nervous System Guide to Managing {topic}"},
        {"title": "Beyond the Balance", "subtitle_pattern": "Healing Your Relationship with Money and {topic}"},
    ],
    "mindfulness": [
        {"title": "The Breath You Forgot", "subtitle_pattern": "A Beginner's Guide to {topic} and Present-Moment Awareness"},
        {"title": "Present Tense", "subtitle_pattern": "How {topic} Calms Anxiety and Quiets the Mind"},
        {"title": "Here Not There", "subtitle_pattern": "A {topic} Guide for Overthinkers and Worriers"},
        {"title": "The Stillness Practice", "subtitle_pattern": "Daily {topic} Exercises for Stress and Calm"},
        {"title": "Quiet Thunder", "subtitle_pattern": "{topic} and Meditation for People Who Can't Sit Still"},
        {"title": "One Breath at a Time", "subtitle_pattern": "A Simple {topic} Practice for {persona}"},
        {"title": "The Attention Anchor", "subtitle_pattern": "How {topic} Trains Your Brain to Stay Present"},
        {"title": "Grounded", "subtitle_pattern": "A {topic} Guide for Anxiety, Stress, and Overwhelm"},
        {"title": "Mind Full to Mindful", "subtitle_pattern": "The Shift from Overthinking to {topic}"},
        {"title": "The Art of Noticing", "subtitle_pattern": "A {topic} Workbook for Daily Presence"},
    ],
}

KEYWORD_TEMPLATES = {
    "adhd_focus": ["adhd self help", "adhd focus book", "neurodivergent guide", "adhd adults", "dopamine regulation", "adhd burnout", "executive function", "adhd and anxiety", "adhd women book", "neurodivergent burnout"],
    "anxiety": ["anxiety relief", "nervous system regulation", "calm anxiety naturally", "anxiety recovery", "high functioning anxiety", "anxiety workbook adults", "somatic anxiety", "how to stop anxiety", "anxiety and stress relief", "panic attack help"],
    "burnout": ["burnout recovery", "work exhaustion healing", "nervous system reset", "burnout book professionals", "hustle culture recovery", "stress management", "burnout prevention", "exhaustion recovery", "work life balance", "chronic stress"],
    "sleep_anxiety": ["insomnia self help", "racing thoughts night", "sleep anxiety relief", "cant sleep book", "3am anxiety", "calm mind sleep", "bedtime anxiety", "how to fall asleep", "sleep hygiene", "nighttime anxiety"],
    "imposter_syndrome": ["imposter syndrome book", "feeling like fraud", "self doubt recovery", "imposter syndrome women", "imposter syndrome work", "confidence building", "worthy enough", "not good enough", "self doubt at work", "feeling inadequate"],
    "social_anxiety": ["social anxiety recovery", "overcoming shyness", "introvert anxiety", "social confidence", "making friends adult", "phone anxiety", "social skills", "how to talk to people", "fear of judgment", "social anxiety workbook"],
    "self_worth": ["self esteem books", "self worth healing", "self love guide", "confidence building", "feeling worthless recovery", "enough self help", "body neutrality", "how to love yourself", "not good enough", "inner critic healing"],
    "boundaries": ["setting boundaries book", "how say no", "people pleasing recovery", "boundaries without guilt", "codependency healing", "toxic relationship boundaries", "healthy boundaries", "how to say no book", "stop people pleasing", "boundaries in relationships"],
    "grief": ["grief recovery book", "coping with loss", "grief healing guide", "losing loved one", "grief companion", "complicated grief", "bereavement self help", "how to grieve", "grief and loss", "moving on after death"],
    "overthinking": ["stop overthinking book", "racing thoughts relief", "quiet mind guide", "analysis paralysis", "worry less book", "mental spirals", "rumination recovery", "how to stop overthinking", "anxious thoughts", "quiet your mind"],
    "somatic_healing": ["nervous system regulation book", "somatic exercises", "vagus nerve healing", "body trauma release", "polyvagal theory guide", "somatic therapy self help", "freeze response", "nervous system reset", "body keeps the score", "trauma release exercises"],
    "depression": ["depression recovery book", "feeling numb healing", "low energy guide", "depression self help", "finding hope again", "functioning depression", "mood healing", "high functioning depression", "emotional numbness", "feeling empty"],
    "courage": ["courage building book", "facing fear guide", "brave living", "fear of change", "bold decisions", "risk taking self help", "courage practice", "afraid to speak up", "fear of failure", "overcoming fear"],
    "compassion_fatigue": ["compassion fatigue recovery", "caregiver burnout book", "empathy exhaustion", "nurse self care", "helper burnout", "vicarious trauma", "moral injury healing", "empathy overload", "caregiver stress", "helping profession burnout"],
    "financial_anxiety": ["money anxiety book", "financial stress relief", "money shame healing", "financial anxiety guide", "broke and scared", "money mindset", "financial therapy", "money worries", "financial stress and anxiety", "debt stress"],
    "mindfulness": ["mindfulness book", "meditation for beginners", "how to meditate", "present moment awareness", "calm mind", "mindfulness workbook", "daily meditation guide", "mindfulness and anxiety", "being present", "mindfulness exercises"],
    "financial_stress": ["financial stress book", "money worry relief", "financial wellness guide", "money anxiety recovery", "financial peace", "money shame healing", "financial self help", "paycheck to paycheck stress", "money problems help", "financial wellness"],
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
                   content_type: str, series_book_num: int = 0,
                   lane_id: str = "en_US") -> tuple[str, str]:
    """Generate a title + subtitle pair with persona targeting.

    Persona targeting strategy (from research):
    - 70% of titles include persona/situation in subtitle
    - JP/KR lanes suppress persona targeting (prefer universal)
    - "always" mode: append "for {Persona}" if not in subtitle
    - "situation" mode: append aspirational phrase instead of persona label
    - "never" mode: no persona reference
    """
    topic_display = TOPIC_DISPLAY.get(topic_id, topic_id.replace("_", " ").title())
    persona_display = PERSONA_DISPLAY.get(persona_id, persona_id.replace("_", " ").title())

    if content_type == "series" and topic_id in SERIES_BOOK_SUBTITLES:
        subtitles = SERIES_BOOK_SUBTITLES[topic_id]
        idx = series_book_num % len(subtitles)
        series_list = SERIES_NAMES.get(topic_id, [f"The {topic_display} Series"])
        series_name = series_list[0]
        title = f"{series_name}: Book {series_book_num + 1}"
        subtitle = subtitles[idx]
        # Add persona to series subtitles too (unless JP/KR)
        subtitle = _apply_persona_suffix(subtitle, persona_id, persona_display, lane_id)
        return title, subtitle

    # Standalone / micro / variation: use title templates
    templates = TITLE_TEMPLATES.get(topic_id, [
        {"title": f"The {topic_display} Reset", "subtitle_pattern": "A Guide to {topic} Recovery"},
    ])
    seed_int = int(seed[:8], 16)
    template = templates[seed_int % len(templates)]

    title = template["title"]
    subtitle = template["subtitle_pattern"].format(
        topic=topic_display,
        persona=persona_display,
    )

    # Apply persona targeting if not already in subtitle
    subtitle = _apply_persona_suffix(subtitle, persona_id, persona_display, lane_id)

    return title, subtitle


def _apply_persona_suffix(subtitle: str, persona_id: str, persona_display: str,
                           lane_id: str) -> str:
    """Append persona targeting to subtitle based on strategy config.

    Skips if:
    - Subtitle already contains persona reference
    - Lane is in PERSONA_SUPPRESS_LANES (JP/KR prefer universal)
    - Mode is "never" for this persona
    - Adding would exceed 120 chars (Amazon subtitle limit)
    """
    # Check if persona already referenced
    if persona_display.lower() in subtitle.lower() or f"for {persona_display}" in subtitle:
        return subtitle

    # Suppress for JP/KR markets (prefer universal titles)
    if lane_id in PERSONA_SUPPRESS_LANES:
        return subtitle

    mode = PERSONA_SUBTITLE_MODE.get(persona_id, "situation")

    if mode == "never":
        return subtitle

    if mode == "always":
        persona_phrase = f"for {persona_display}"
    elif mode == "situation":
        persona_phrase = PERSONA_SITUATION.get(persona_id, f"for {persona_display}")
    else:
        return subtitle

    # Avoid double "for" — if subtitle already has a generic audience "for X" phrase,
    # replace it with the persona phrase. Only replace known generic patterns.
    import re
    _GENERIC_FOR = re.compile(
        r" for (People Pleasers and Overgivers|Quiet People|Helpers|"
        r"People Running on Empty|People Tired of Being Told to Move On|"
        r"People Who Give Too Much|Overthinkers and Worriers|"
        r"Adults Who Were Never Diagnosed|People Who Can't Sit Still)$"
    )
    match = _GENERIC_FOR.search(subtitle)
    if match:
        new_subtitle = subtitle[:match.start()] + " " + persona_phrase
    elif " for " not in subtitle:
        # No existing "for" — safe to append
        new_subtitle = subtitle + " " + persona_phrase
    else:
        # Has a "for" but it's content-specific (e.g., "for the Worst Days") — append
        new_subtitle = subtitle + " " + persona_phrase
        # But check for double "for" and skip if it reads badly
        if new_subtitle.count(" for ") > 1:
            return subtitle  # skip — better generic than awkward double

    # Check length (optimal <120 chars for Amazon)
    if len(new_subtitle) > 120:
        return subtitle

    return new_subtitle


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
    lane_id = brand.get("lane_id", "en_US")
    projection_lane = _lane_id_to_projection_lane(lane_id)

    # --- PROJECTION SYSTEM: read per-brand 52-week plan if available ---
    projection_plan = get_weekly_plan(brand_id, projection_lane, week_id)
    if projection_plan:
        # Map projection format keys → queue slot counts
        # Projection formats: series_books, standalone_books, micro_books,
        #   manga_chapters, podcast_episodes, format_variations, video_audiobooks
        n_series = projection_plan.get("series_books", 2) + projection_plan.get("manga_chapters", 0)
        n_strong_standalone = projection_plan.get("standalone_books", 5)
        n_strong_micro = projection_plan.get("micro_books", 3)
        n_viable_standalone = max(0, target - n_series - n_strong_standalone - n_strong_micro
                                  - projection_plan.get("format_variations", 2)
                                  - projection_plan.get("podcast_episodes", 0))
        n_format_var = projection_plan.get("format_variations", 2)
        # Recalculate target from projection (may differ from flat 15)
        target = sum(projection_plan.values())
    else:
        # Fallback: use flat config mix (original behavior preserved)
        lane_mix = queue_cfg.get("lane_weekly_mix", {}).get(lane_id)
        if lane_mix:
            # JP manga-primary mix
            n_series = lane_mix.get("manga_series_installments", 3) + lane_mix.get("ebook_series_installments", 1)
            n_strong_standalone = lane_mix.get("manga_standalone", 3) + lane_mix.get("ebook_standalone", 3)
            n_strong_micro = lane_mix.get("manga_micro", 2) + lane_mix.get("ebook_micro", 1)
            n_viable_standalone = 0  # all slots used by manga+ebook split
            n_format_var = lane_mix.get("format_variations", 2)
        else:
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

    # Track usage counts for diversity enforcement
    _engine_counts: dict[str, int] = {}
    _topic_counts: dict[str, int] = {}

    def _pick_config(configs: list[dict], runtime_filter: Optional[list[str]] = None) -> Optional[dict]:
        """Pick a config with engine AND topic diversity.

        Enforces:
        - Engine rotation: prefers least-used engine
        - Topic cap: no topic exceeds ceil(15 / n_brand_topics) + 2
        - Combined sort: (topic_count, engine_count) ensures both diversify
        """
        filtered = [c for c in configs if not runtime_filter or c["runtime_format_id"] in runtime_filter]
        if not filtered:
            return None

        # Calculate per-topic cap
        brand_topics_in_configs = set(c["topic_id"] for c in filtered)
        n_topics = max(len(brand_topics_in_configs), 1)
        topic_cap = (15 // n_topics) + 2

        # Sort by: (topic_count, engine_count) — diversifies BOTH simultaneously
        def sort_key(cfg):
            tc = _topic_counts.get(cfg["topic_id"], 0)
            ec = _engine_counts.get(cfg["engine"], 0)
            return (tc, ec)

        candidates = sorted(filtered, key=sort_key)

        # Pick first candidate under topic cap
        for cfg in candidates:
            tc = _topic_counts.get(cfg["topic_id"], 0)
            if tc >= topic_cap:
                continue
            _topic_counts[cfg["topic_id"]] = tc + 1
            _engine_counts[cfg["engine"]] = _engine_counts.get(cfg["engine"], 0) + 1
            return cfg

        # All topics at cap — pick least-used engine regardless
        for cfg in candidates:
            tc = _topic_counts.get(cfg["topic_id"], 0)
            _topic_counts[cfg["topic_id"]] = tc + 1
            _engine_counts[cfg["engine"]] = _engine_counts.get(cfg["engine"], 0) + 1
            return cfg

        # Fallback
        seed_int = int(make_seed(brand_id, week_id, len(queue))[:8], 16)
        cfg = filtered[seed_int % len(filtered)]
        _topic_counts[cfg["topic_id"]] = _topic_counts.get(cfg["topic_id"], 0) + 1
        _engine_counts[cfg["engine"]] = _engine_counts.get(cfg["engine"], 0) + 1
        return cfg

    def _build_item(cfg: dict, content_type: str, seed: str,
                    series_id: Optional[str] = None,
                    series_book_num: int = 0) -> dict:
        rt_info = RUNTIME_FORMATS.get(cfg["runtime_format_id"], {})
        price = rt_info.get("price", 3.99)
        if content_type == "series" and series_book_num == 0:
            price = 0.00  # Book 1 is permafree (KDP price-match via free on Google Play/Kobo)

        # Pass lane_id for persona targeting (JP/KR suppress persona in subtitles)
        _lane = brand.get("lane_id", "en_US") if isinstance(brand, dict) else "en_US"
        title, subtitle = generate_title(
            cfg["topic_id"], cfg["persona_id"], cfg["engine"],
            cfg["runtime_format_id"], seed, len(queue),
            content_type, series_book_num, lane_id=_lane,
        )

        # Differentiate keywords by content_type to prevent cannibalization
        base_kw = KEYWORD_TEMPLATES.get(cfg["topic_id"], [])
        content_type_suffix = {
            "micro": "quick guide",
            "standalone": "workbook",
            "series": "step by step",
            "format_variation": "comprehensive guide",
        }
        suffix = content_type_suffix.get(content_type, "")
        # Use first 6 base keywords + 1 content-type keyword (7 total for Amazon max)
        keywords = base_kw[:6] + [f"{cfg['topic_id'].replace('_', ' ')} {suffix}".strip()] if suffix else base_kw[:7]

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
    # Strategy: 1 continuation + 1 new series starter per week.
    # The new series produces a permafree Book 1 ($0.00) every week.
    # The continuation advances an existing series.
    brand_topics = list(brand.get("primary_topics", []))
    week_num = int(week_id.split("-W")[-1]) if "-W" in week_id else 1
    for i in range(n_series):
        if not brand_topics:
            break

        if i == 0:
            # Slot 0: CONTINUATION — advance existing series
            topic = brand_topics[0]
            book_num = (week_num - 1) % 10  # cycles through 10-book series
        else:
            # Slot 1: NEW SERIES STARTER — permafree Book 1 ($0.00)
            # Rotate through topics each week so different series launch
            topic = brand_topics[(week_num + i) % len(brand_topics)]
            book_num = 0  # always Book 1 = permafree

        series_name_list = SERIES_NAMES.get(topic, [f"The {TOPIC_DISPLAY.get(topic, topic)} Series"])
        series_idx = (week_num + i) % len(series_name_list) if i > 0 else 0
        series_id = f"SER-{brand_id}-{topic}-{series_name_list[series_idx].replace(' ', '_').lower()}"

        # Pick a config for series — rotate engine by week + series index
        brand_personas = brand.get("primary_personas", [])
        persona = brand_personas[(week_num + i) % len(brand_personas)] if brand_personas else "corporate_managers"
        engine = ENGINES[(week_num + i) % len(ENGINES)]  # rotate engine by week

        series_cfg = {
            "topic_id": topic,
            "persona_id": persona,
            "engine": engine,
            "format_id": "F006",
            "runtime_format_id": "standard_book",
        }

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
