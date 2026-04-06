"""Manga-grade prompt compiler for FLUX image generation.

Builds structured prompt dicts with quality tokens, continuity tags,
provenance hashing, and QC-ready output. Replaces raw prompt string
building throughout the image generation scripts.

Rewritten from .pyc interface spec — see specs/MANGA_QC_AND_EBOOK_PIPELINE_SPEC.md §A.2.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]


REPO_ROOT = Path(__file__).resolve().parents[2]

# ── Token limits (FLUX CLIP encoder) ──
MAX_POSITIVE_TOKENS = 120
MAX_NEGATIVE_TOKENS = 60

# ── Quality tokens always prepended to positive ──
QUALITY_TOKENS = "masterpiece, best quality, highly detailed illustration"

# ── Shared negative tokens always included ──
SHARED_NEGATIVE_TOKENS = (
    "low quality, worst quality, blurry, watermark, text, signature, "
    "deformed, disfigured, bad anatomy, extra limbs"
)

# ── Task-specific style presets ──
TASK_STYLE_PRESETS: dict[str, dict[str, str]] = {
    "cover_art_base": {
        "suffix": "abstract book cover, atmospheric, portrait orientation",
        "extra_negative": "text, letters, face, person, realistic photo",
    },
    "video_bank_image": {
        "suffix": "cinematic composition, atmospheric, high detail",
        "extra_negative": "text, letters, UI elements",
    },
    "author_pic": {
        "suffix": "character portrait, professional illustration, manga-inspired",
        "extra_negative": "photo, realistic face, 3d render, multiple people",
    },
}

# ── Config paths ──
_AUTHOR_PIC_PROMPTS_PATH = REPO_ROOT / "config" / "authoring" / "author_pic_prompts.yaml"
_PROVIDER_ROUTING_PATH = REPO_ROOT / "config" / "image_generation" / "provider_routing.yaml"

_VERSION = "manga_qc_v1"


def _token_count(text: str) -> int:
    """Count CLIP-style tokens (split on spaces and commas)."""
    if not text or not text.strip():
        return 0
    tokens = [t.strip() for t in text.replace(",", " ").split() if t.strip()]
    return len(tokens)


def _sha256(data: str) -> str:
    """SHA-256 hex digest of a string."""
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _load_yaml_config(path: Path) -> dict[str, Any]:
    """Load a YAML config file. Returns empty dict if missing or yaml unavailable."""
    if yaml is None or not path.is_file():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _bio_to_subject(name: str, bio: str) -> str:
    """Extract visual character description from bio text using keyword matching."""
    bio_lower = bio.lower() if bio else ""

    if "coaching" in bio_lower or "coach" in bio_lower:
        subject = f"{name}, professional coaching presence"
    elif "clinical" in bio_lower or "therapist" in bio_lower:
        subject = f"{name}, clinical professional warmth"
    elif "meditation" in bio_lower or "spiritual" in bio_lower:
        subject = f"{name}, serene contemplative figure"
    elif "teacher" in bio_lower or "master" in bio_lower:
        subject = f"{name}, wise teacher figure"
    elif "healer" in bio_lower or "healing" in bio_lower:
        subject = f"{name}, gentle healing practitioner"
    elif "author" in bio_lower or "writer" in bio_lower:
        subject = f"{name}, creative literary figure"
    else:
        subject = f"{name}, professional portrait"

    return subject


def _extract_bio_keywords(bio: str) -> list[str]:
    """Extract searchable keywords from bio for continuity tags."""
    if not bio:
        return []
    keywords: list[str] = []
    search_terms = [
        "meditation", "coaching", "clinical", "spiritual", "healing",
        "therapy", "yoga", "mindfulness", "wellness", "energy",
        "consciousness", "transformation", "teacher", "master",
        "practitioner", "author", "researcher", "psychologist",
    ]
    bio_lower = bio.lower()
    for term in search_terms:
        if term in bio_lower:
            keywords.append(term)
    return keywords


def compile_image_prompt(
    task: str,
    subject: str,
    style_hint: str,
    palette_tokens: list[str],
    scene: str,
    extra_positive: str,
    extra_negative: str,
    author_id: str,
    bio_keywords: list[str],
) -> dict[str, Any]:
    """Build a structured prompt dict from manga-grade patterns.

    Returns dict with keys: positive, negative, continuity_tags, provenance, qc_results,
    guidance, seed.
    """
    preset = TASK_STYLE_PRESETS.get(task, {})

    # Build positive prompt
    parts_positive = [QUALITY_TOKENS]
    if subject:
        parts_positive.append(subject)
    if style_hint:
        parts_positive.append(style_hint)
    if palette_tokens:
        parts_positive.append(", ".join(palette_tokens))
    if scene:
        parts_positive.append(scene)
    if preset.get("suffix"):
        parts_positive.append(preset["suffix"])
    if extra_positive:
        parts_positive.append(extra_positive)

    positive = ", ".join(p for p in parts_positive if p)

    # Build negative prompt
    parts_negative = [SHARED_NEGATIVE_TOKENS]
    if preset.get("extra_negative"):
        parts_negative.append(preset["extra_negative"])
    if extra_negative:
        parts_negative.append(extra_negative)

    negative = ", ".join(p for p in parts_negative if p)

    # Continuity tags
    continuity_tags: list[str] = [f"task:{task}"]
    if author_id:
        continuity_tags.append(f"author:{author_id}")
    if style_hint:
        continuity_tags.append(f"style:{style_hint}")
    for kw in bio_keywords:
        continuity_tags.append(f"bio:{kw}")

    # Provenance
    prompt_hash = _sha256(positive + "|" + negative)
    provenance = {
        "prompt_hash": prompt_hash,
        "compiled_at": datetime.now(timezone.utc).isoformat(),
        "version": _VERSION,
        "task": task,
        "author_id": author_id,
    }

    # Token counts for QC
    positive_tokens = _token_count(positive)
    negative_tokens = _token_count(negative)

    return {
        "positive": positive,
        "negative": negative,
        "continuity_tags": continuity_tags,
        "provenance": provenance,
        "qc_results": [],
        "positive_token_count": positive_tokens,
        "negative_token_count": negative_tokens,
        "guidance": 7.5,
        "seed": 0,
    }


def compile_author_pic_prompt(
    author_id: str,
    bio: str,
    style_hint: str,
    display_name: str,
) -> dict[str, Any]:
    """Build a structured prompt for an author portrait.

    Loads per-author presets from config/authoring/author_pic_prompts.yaml
    and extracts visual character from bio text.
    """
    config = _load_yaml_config(_AUTHOR_PIC_PROMPTS_PATH)
    authors_config = config.get("authors", {})
    style_presets = config.get("style_presets", {})

    # Get author-specific preset
    author_entry = authors_config.get(author_id, {})
    preset_name = author_entry.get("style_preset", "contemplative_portrait")
    preset = style_presets.get(preset_name, {})

    # Build subject from bio
    subject = _bio_to_subject(display_name or author_id, bio)
    bio_keywords = _extract_bio_keywords(bio)

    # Merge preset into prompt
    extra_positive = preset.get("positive", "")
    quality_suffix = preset.get("quality_suffix", "")
    if quality_suffix:
        extra_positive = f"{extra_positive}, {quality_suffix}" if extra_positive else quality_suffix

    extra_negative = preset.get("negative_extra", "")
    preset_suffix = preset.get("suffix", "")

    compiled = compile_image_prompt(
        task="author_pic",
        subject=subject,
        style_hint=style_hint,
        palette_tokens=[],
        scene=preset_suffix,
        extra_positive=extra_positive,
        extra_negative=extra_negative,
        author_id=author_id,
        bio_keywords=bio_keywords,
    )

    # Add author-specific metadata
    compiled["author_id"] = author_id
    compiled["display_name"] = display_name
    compiled["bio_length"] = len(bio) if bio else 0

    return compiled


# ── Manga panel prompt helpers ──────────────────────────────────────


def compile_panel_prompt(panel: dict[str, Any]) -> dict[str, str]:
    """Compile a single manga panel dict into positive/negative prompt strings.

    Accepts a panel dict from a ``panel_prompts`` artifact (which uses
    ``prompt`` or ``visual_prompt`` for the main text) and returns a flat
    dict with ``panel_id``, ``positive``, and ``negative`` keys suitable for
    image-generation backends.
    """
    # Accept both field names
    visual = panel.get("prompt", "") or panel.get("visual_prompt", "")
    negative = panel.get("negative_prompt", "")
    composition = panel.get("composition_notes", "")
    tags = panel.get("continuity_tags", [])
    sdf = panel.get("sdf_conditioning", {})

    positive_parts: list[str] = []
    if visual:
        positive_parts.append(str(visual))
    if composition:
        if isinstance(composition, dict):
            positive_parts.append(str(composition.get("summary", "")))
        else:
            positive_parts.append(str(composition))
    for tag in tags:
        if isinstance(tag, str):
            positive_parts.append(tag)
    for k, v in (sdf.items() if isinstance(sdf, dict) else []):
        if isinstance(v, str):
            positive_parts.append(f"{k}: {v}")

    return {
        "panel_id": panel.get("panel_id", ""),
        "positive": ", ".join(p for p in positive_parts if p) if positive_parts else "",
        "negative": str(negative) if negative else "",
    }


def compile_all_panel_prompts(panel_prompts: dict[str, Any]) -> list[dict[str, str]]:
    """Compile all panels in a ``panel_prompts`` artifact.

    Returns a list of dicts, each with ``panel_id``, ``positive``, and
    ``negative`` keys.
    """
    return [compile_panel_prompt(p) for p in panel_prompts.get("panels", [])]
