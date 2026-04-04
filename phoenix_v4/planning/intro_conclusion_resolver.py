"""
Intro/Conclusion Chapter Resolver — Format-Aware Hybrid Template Bank Selection.

Four content sources, one selector:
  A. YAML template banks (config/source_of_truth/intro_conclusion_banks.yaml)
  B. Plan-generated variable substitution ({topic_display}, {mechanism_alias}, etc.)
  C. Per-brand overrides (optional)
  D. Per-format overrides (optional, e.g. F005 rescue kit, F001 90-day)

Selection priority: brand → format → persona → default (deterministic hash).
Size variant: lean / short / full — selected by runtime_format_id.
Anti-spam: SHA256 signature → 12% cap per brand/quarter + duplicate gate.

Authority: Plan — Format-Aware Introduction & Conclusion Chapters.
"""
from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_SOT = REPO_ROOT / "config" / "source_of_truth"

_BANKS_CACHE: Optional[dict] = None

# ── Runtime → intro size mapping ────────────────────────────────────
# lean: 1-2 sentences (~30w), no title heading — for micro/pocket guides
# short: 1 paragraph (~80w), short title — for 30-min books
# full: 2-4 paragraphs (~150-400w), full title — for standard+ books

RUNTIME_TO_INTRO_SIZE: dict[str, str] = {
    "micro_book_15": "lean",
    "micro_book_20": "lean",
    "short_book_30": "short",
    "standard_book": "full",
    "extended_book_2h": "full",
    "deep_book_4h": "full",
    "deep_book_6h": "full",
}

# Title rules per size
_INTRO_TITLES: dict[str, str] = {
    "lean": "",                # micro books: no heading
    "short": "Before We Begin",
    "full": "Introduction",
}
_CONCLUSION_TITLES: dict[str, str] = {
    "lean": "",
    "short": "To Close",
    "full": "Conclusion",
}


def _load_banks(config_root: Optional[Path] = None) -> dict:
    global _BANKS_CACHE
    if _BANKS_CACHE is not None:
        return _BANKS_CACHE
    root = config_root or CONFIG_SOT
    path = root / "intro_conclusion_banks.yaml"
    if not path.exists() or yaml is None:
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    _BANKS_CACHE = data
    return data


def _selector_index(selector_key: str, available_count: int) -> int:
    """Deterministic selection — same algorithm as pre_intro_resolver and slot_resolver."""
    if available_count <= 0:
        return 0
    digest = hashlib.sha256(selector_key.encode("utf-8")).digest()
    n = int.from_bytes(digest[:16], "big")
    return n % available_count


def _compute_signature(text: str) -> str:
    """SHA256 first 16 chars of resolved content."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _select_template(
    section: str,
    topic_id: str,
    persona_id: str,
    seed: str,
    brand_id: Optional[str] = None,
    format_id: Optional[str] = None,
    retry_index: int = 0,
    config_root: Optional[Path] = None,
) -> Optional[dict]:
    """
    Select one template from banks.
    Priority: brand → format → persona → default.
    Returns raw template dict or None.
    """
    banks = _load_banks(config_root)
    section_banks = banks.get(section) or {}

    templates = None

    # 1. Brand override
    if brand_id:
        brand_banks = section_banks.get("brands") or {}
        brand_entry = brand_banks.get(brand_id) or {}
        templates = brand_entry.get("templates")

    # 2. Format-specific override (e.g. F005 rescue kit, F001 90-day)
    if not templates and format_id:
        format_banks = section_banks.get("formats") or {}
        format_entry = format_banks.get(format_id) or {}
        templates = format_entry.get("templates")

    # 3. Persona override
    if not templates:
        persona_banks = section_banks.get("personas") or {}
        persona_entry = persona_banks.get(persona_id) or {}
        templates = persona_entry.get("templates")

    # 4. Default fallback
    if not templates:
        default_entry = section_banks.get("default") or {}
        templates = default_entry.get("templates")

    if not templates:
        return None

    key_suffix = f"|retry{retry_index}" if retry_index > 0 else ""
    selector_key = f"{section}_chapter|{topic_id}|{persona_id}|{seed}{key_suffix}"
    idx = _selector_index(selector_key, len(templates))
    return templates[idx]


def _get_content_for_size(template: dict, size: str) -> str:
    """
    Extract content for the requested size variant.
    Templates may have: lean, short, full (new format) OR just content (legacy).
    Fallback chain: requested size → full → content.
    """
    if size in template and template[size]:
        return str(template[size])
    # Fallback to larger sizes
    if size == "lean":
        for fallback in ("short", "full", "content"):
            if fallback in template and template[fallback]:
                return str(template[fallback])
    elif size == "short":
        for fallback in ("full", "content"):
            if fallback in template and template[fallback]:
                return str(template[fallback])
    # Final fallback
    return str(template.get("content") or template.get("full") or "")


def _substitute_variables(
    text: str,
    topic_id: str,
    persona_id: str,
    mechanism_alias: Optional[str] = None,
    chapter_count: Optional[int] = None,
) -> str:
    """Replace template variables with plan-specific values."""
    topic_display = topic_id.replace("_", " ") if topic_id else "what you are carrying"
    persona_display = persona_id.replace("_", " ") if persona_id else "people like you"

    result = text
    result = result.replace("{topic_display}", topic_display)
    result = result.replace("{persona_display}", persona_display)
    if mechanism_alias:
        result = result.replace("{mechanism_alias}", mechanism_alias)
    else:
        result = result.replace("{mechanism_alias}", "the pattern underneath")
    if chapter_count is not None:
        result = result.replace("{chapter_count}", str(chapter_count))
    else:
        result = result.replace("{chapter_count}", "these")
    return result


def _resolve_size(runtime_format_id: Optional[str], format_id: Optional[str] = None, chapter_count: Optional[int] = None) -> str:
    """
    Map runtime format to intro size. Falls back to chapter_count heuristic when runtime unknown.
    - ≤5 chapters → lean (pocket guide / micro)
    - 6-8 chapters → short
    - 9+ chapters → full
    """
    if runtime_format_id and runtime_format_id in RUNTIME_TO_INTRO_SIZE:
        return RUNTIME_TO_INTRO_SIZE[runtime_format_id]
    # Heuristic: use chapter count when runtime format is unknown
    if chapter_count is not None:
        if chapter_count <= 5:
            return "lean"
        elif chapter_count <= 8:
            return "short"
        else:
            return "full"
    return "full"


def resolve_introduction_chapter(
    topic_id: str,
    persona_id: str,
    seed: str = "default_seed",
    brand_id: Optional[str] = None,
    format_id: Optional[str] = None,
    runtime_format_id: Optional[str] = None,
    mechanism_alias: Optional[str] = None,
    chapter_count: Optional[int] = None,
    retry_index: int = 0,
    config_root: Optional[Path] = None,
) -> dict[str, Any]:
    """
    Resolve introduction chapter from template banks + variable substitution.
    Format-aware: selects lean/short/full size based on runtime_format_id.

    Returns:
        {"title": str, "content": str, "signature": str, "template_id": str, "size": str}
    """
    size = _resolve_size(runtime_format_id, format_id=format_id, chapter_count=chapter_count)

    template = _select_template(
        "introduction", topic_id, persona_id, seed,
        brand_id=brand_id, format_id=format_id,
        retry_index=retry_index, config_root=config_root,
    )
    if not template:
        # Hard fallback by size
        fallbacks = {
            "lean": "This book is about {topic_display} — the version that lives in your body.",
            "short": (
                "This book is about {topic_display}. Not the version you read about online. "
                "The version that lives in your body. Each chapter gives you one scene, one insight, one practice."
            ),
            "full": (
                "This book is about {topic_display}. Each chapter offers a scene, "
                "a reflection, and a practice. There is nothing to fix. There is "
                "something to see."
            ),
        }
        content = _substitute_variables(
            fallbacks.get(size, fallbacks["full"]),
            topic_id, persona_id, mechanism_alias, chapter_count,
        )
        title = _INTRO_TITLES.get(size, "Introduction")
        return {
            "title": title,
            "content": content.strip(),
            "signature": _compute_signature(content),
            "template_id": "_fallback",
            "size": size,
        }

    raw_content = _get_content_for_size(template, size)
    content = _substitute_variables(
        raw_content, topic_id, persona_id, mechanism_alias, chapter_count,
    )
    # Title: use template title for full/short, suppress for lean
    if size == "lean":
        title = ""
    elif size == "short":
        title = template.get("title", _INTRO_TITLES["short"])
    else:
        title = template.get("title", "Introduction")

    return {
        "title": title,
        "content": content.strip(),
        "signature": _compute_signature(content),
        "template_id": template.get("id", "unknown"),
        "size": size,
    }


def resolve_conclusion_chapter(
    topic_id: str,
    persona_id: str,
    seed: str = "default_seed",
    brand_id: Optional[str] = None,
    format_id: Optional[str] = None,
    runtime_format_id: Optional[str] = None,
    mechanism_alias: Optional[str] = None,
    chapter_count: Optional[int] = None,
    retry_index: int = 0,
    config_root: Optional[Path] = None,
) -> dict[str, Any]:
    """
    Resolve conclusion chapter from template banks + variable substitution.
    Format-aware: selects lean/short/full size based on runtime_format_id.

    Returns:
        {"title": str, "content": str, "signature": str, "template_id": str, "size": str}
    """
    size = _resolve_size(runtime_format_id, format_id=format_id, chapter_count=chapter_count)

    template = _select_template(
        "conclusion", topic_id, persona_id, seed,
        brand_id=brand_id, format_id=format_id,
        retry_index=retry_index, config_root=config_root,
    )
    if not template:
        fallbacks = {
            "lean": "Take what landed. Leave what did not. The door stays open.",
            "short": (
                "The pattern has not disappeared. But you are no longer inside it "
                "without knowing. Take what landed. The door stays open."
            ),
            "full": (
                "You started this book carrying something. The pattern has not "
                "disappeared. But you are no longer inside it without knowing. "
                "Take what landed. Leave what did not. The door stays open."
            ),
        }
        content = _substitute_variables(
            fallbacks.get(size, fallbacks["full"]),
            topic_id, persona_id, mechanism_alias, chapter_count,
        )
        title = _CONCLUSION_TITLES.get(size, "Conclusion")
        return {
            "title": title,
            "content": content.strip(),
            "signature": _compute_signature(content),
            "template_id": "_fallback",
            "size": size,
        }

    raw_content = _get_content_for_size(template, size)
    content = _substitute_variables(
        raw_content, topic_id, persona_id, mechanism_alias, chapter_count,
    )
    if size == "lean":
        title = ""
    elif size == "short":
        title = template.get("title", _CONCLUSION_TITLES["short"])
    else:
        title = template.get("title", "Conclusion")

    return {
        "title": title,
        "content": content.strip(),
        "signature": _compute_signature(content),
        "template_id": template.get("id", "unknown"),
        "size": size,
    }
