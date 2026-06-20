"""Deterministic per-brand / per-author cover assignment.

Generalizes config/publishing/waystream_cover_system.yaml (one brand, hand-authored
author cards) to ALL brands. Design law (operator spec, STARTER_NOTE §3):
  * each BRAND reads as its own publishing house (distinct font DNA + palette base)
  * each AUTHOR within a brand gets a distinct (family x serif x sans x palette x
    title_case) so a 12-20 author brand reads as that many lines, not one template
  * assignment is PURELY a function of (brand_id, author_id) -> stable + call-order
    independent, so pools.py and render_brand.py always agree on an author's family.

No GPU here. FLUX pools (pools.py) are MARKET-AGNOSTIC: generated once per
(brand, author), reused across all 14 locales (only the composited text changes).
"""
from __future__ import annotations
import hashlib

# Fonts validated against macOS + scripts/publish/waystream_covers/fonts.py
SERIFS = ["Georgia", "Hoefler Text", "Charter", "Iowan Old Style", "Baskerville",
          "Didot", "Athelas", "Cochin", "Bodoni 72", "Superclarendon", "Palatino", "Times New Roman"]
SANS = ["Avenir Next", "Gill Sans", "Futura", "Helvetica Neue", "Trebuchet MS", "Verdana", "Arial", "Optima"]
FAMILIES = ["full_bleed", "inset_card", "panel_bands", "title_block",
            "gradient_solo", "framed", "duotone_split", "stripe_minimal"]
IMAGE_FAMILIES = {"full_bleed", "inset_card", "panel_bands", "title_block"}
CASES = ["sentence", "title", "small_caps"]

# Palette bank: deep (dark) / field (warm paper, never #fff) / accent (signal).
PALETTES = [
    ("#0E1B33", "#F3EFE5", "#6FA8D6"), ("#11324A", "#F4F1E8", "#E8A23D"),
    ("#1B2A4A", "#EFEADD", "#DE5B45"), ("#14303A", "#F2EEE3", "#4FB0A2"),
    ("#233A5E", "#F6F2E9", "#C9A24A"), ("#2A2440", "#F1ECE0", "#C98AB0"),
    ("#103040", "#EFEADD", "#46A6CB"), ("#2E2233", "#F3EEE2", "#E0913C"),
    ("#2A211B", "#F1E9DC", "#C8703B"), ("#2E2A22", "#F3ECDD", "#B98A3E"),
    ("#3A2A2A", "#F4ECDD", "#D98F4E"), ("#26303A", "#EFEADD", "#C76B57"),
    ("#1F2A2A", "#F1ECE0", "#C9A24A"), ("#322A3A", "#F2ECE0", "#B98AA8"),
    ("#3A3024", "#F4EEDF", "#D89B45"), ("#232A24", "#F0ECDE", "#B79A48"),
]

# Topic -> motif glyph (symbols.py MOTIF_FN has 15 primitives; map all registry
# topics onto the nearest-semantic glyph; extend with new glyphs later).
TOPIC_MOTIF = {
    "anxiety": "breath", "sleep_anxiety": "crescent", "sleep": "crescent", "sleep_restoration": "crescent",
    "social_anxiety": "link", "overthinking": "loop", "grief": "drop", "boundaries": "divider",
    "burnout": "ember", "compassion_fatigue": "wane", "depression": "lowline", "financial_anxiety": "bars",
    "financial_stress": "jagged", "imposter_syndrome": "offset", "self_worth": "ring", "somatic_healing": "stem",
    "courage": "rise", "mindfulness": "breath", "adhd_focus": "loop", "focus": "rise", "confidence": "ring",
    "relationships": "link", "relationship_clarity": "link", "resilience": "rise", "stress": "jagged",
    "trauma": "drop", "creativity": "rise", "longevity": "ring", "performance": "rise", "clarity": "breath",
    "purpose": "rise", "presence": "breath", "devotion": "stem", "meaning": "ring",
}
DEFAULT_MOTIF = "ring"


def _h(s: str) -> int:
    return int(hashlib.sha1(s.encode()).hexdigest()[:8], 16)


def topic_motif(topic: str) -> str:
    return TOPIC_MOTIF.get((topic or "").lower(), DEFAULT_MOTIF)


def display_name(author_id: str) -> str:
    return " ".join(p.capitalize() for p in str(author_id).replace("-", "_").split("_"))


def assign_author(brand_id: str, author_id: str) -> dict:
    """Stable distinct cover card for (brand, author) — no positional state."""
    bh = _h(brand_id)
    ah = _h(f"{brand_id}/{author_id}")
    deep, field, accent = PALETTES[ah % len(PALETTES)]
    return {
        "display": display_name(author_id),
        "family": FAMILIES[ah % len(FAMILIES)],
        "serif": SERIFS[(bh // 7 + ah // 11) % len(SERIFS)],
        "sans": SANS[(bh // 13 + ah // 17) % len(SANS)],
        "deep": deep, "field": field, "accent": accent,
        "title_case": CASES[ah % len(CASES)],
    }


def assign_brand(brand_id: str, author_ids) -> dict:
    return {aid: assign_author(brand_id, aid) for aid in author_ids}
