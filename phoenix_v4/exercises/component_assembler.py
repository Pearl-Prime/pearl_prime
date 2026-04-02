"""
Exercise component assembler: selects and joins exercise components
based on assembly context and YAML-driven rules.

Integration point: chapter_composer.py calls assemble_exercise_for_chapter()
to get the fully composed exercise text (bridge + intro + description + aha + integration)
with only the appropriate components at the right depth.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Optional

try:
    import yaml
except ImportError:
    yaml = None

from phoenix_v4.exercises.models import (
    AssemblyContext,
    ComponentMode,
    ComponentSelection,
    ComponentVariants,
    EmotionalState,
    ExerciseComponents,
)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RULES_PATH = REPO_ROOT / "config" / "practice" / "assembly_components.yaml"
BRIDGE_TEMPLATES_PATH = REPO_ROOT / "SOURCE_OF_TRUTH" / "exercises_v4" / "bridge_templates.yaml"
INTRO_TEMPLATES_PATH = REPO_ROOT / "SOURCE_OF_TRUTH" / "exercises_v4" / "intro_templates.yaml"
AHA_STANDARD_PATH = REPO_ROOT / "SOURCE_OF_TRUTH" / "exercises_v4" / "aha_noticing_phoenix_standard.yaml"
INTEGRATION_STANDARD_PATH = REPO_ROOT / "SOURCE_OF_TRUTH" / "exercises_v4" / "integration_phoenix_standard.yaml"


def _load_yaml(p: Path) -> Any:
    if not p.exists() or yaml is None:
        return {}
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]


def _derive_lean(full_text: str, max_sentences: int = 2) -> str:
    """Derive lean variant: first N sentences of full text."""
    sents = _sentences(full_text)
    if not sents:
        return full_text
    return " ".join(sents[:max_sentences])


# ---------------------------------------------------------------------------
# Rule loading and matching
# ---------------------------------------------------------------------------

def load_assembly_rules(path: Optional[Path] = None) -> list[dict]:
    """Load ordered rules from assembly_components.yaml."""
    data = _load_yaml(path or RULES_PATH)
    return data.get("rules") or []


def _match_rule(rule: dict, ctx: AssemblyContext) -> bool:
    """Check if a single rule's match block matches the context."""
    match_block = rule.get("match") or {}
    if not match_block:
        return True  # empty match = default/catch-all

    for key, value in match_block.items():
        if key == "first_encounter":
            if ctx.first_encounter != value:
                return False
        elif key == "emotional_state":
            if ctx.emotional_state.value != value:
                return False
        elif key == "is_session_close":
            if ctx.is_session_close != value:
                return False
        elif key == "repeat_count_gte":
            if ctx.repeat_count < value:
                return False
        elif key == "repeat_count_lte":
            if ctx.repeat_count > value:
                return False
    return True


def select_components(
    ctx: AssemblyContext,
    rules: Optional[list[dict]] = None,
) -> ComponentSelection:
    """Evaluate context against ordered rules, return first match."""
    if rules is None:
        rules = load_assembly_rules()

    for rule in rules:
        if _match_rule(rule, ctx):
            comps = rule.get("components") or {}
            return ComponentSelection(
                bridge=ComponentMode(comps.get("bridge", "lean")),
                intro=ComponentMode(comps.get("intro", "full")),
                description=ComponentMode(comps.get("description", "full")),
                aha=ComponentMode(comps.get("aha", "full")),
                integration=ComponentMode(comps.get("integration", "full")),
                bridge_tone=rule.get("bridge_tone", ""),
                rule_name=rule.get("name", "unknown"),
            )

    # Absolute fallback if no rules match (should not happen with default rule)
    return ComponentSelection(rule_name="hardcoded_fallback")


# ---------------------------------------------------------------------------
# Template loading
# ---------------------------------------------------------------------------

_bridge_cache: dict[str, dict] = {}
_intro_cache: dict[str, dict] = {}
_aha_cache: dict[str, str] = {}
_integration_cache: dict[str, str] = {}


def _load_bridge_templates(path: Optional[Path] = None) -> dict[str, dict]:
    if not _bridge_cache:
        data = _load_yaml(path or BRIDGE_TEMPLATES_PATH)
        for key, val in (data.get("templates") or {}).items():
            _bridge_cache[key] = val
    return _bridge_cache


def _load_intro_templates(path: Optional[Path] = None) -> dict[str, dict]:
    if not _intro_cache:
        data = _load_yaml(path or INTRO_TEMPLATES_PATH)
        for key, val in (data.get("templates") or {}).items():
            _intro_cache[key] = val
    return _intro_cache


def _load_aha_standards(path: Optional[Path] = None) -> dict[str, str]:
    if not _aha_cache:
        data = _load_yaml(path or AHA_STANDARD_PATH)
        if isinstance(data, dict):
            for key, val in data.items():
                if isinstance(val, str):
                    _aha_cache[key] = val
    return _aha_cache


def _load_integration_standards(path: Optional[Path] = None) -> dict[str, str]:
    if not _integration_cache:
        data = _load_yaml(path or INTEGRATION_STANDARD_PATH)
        if isinstance(data, dict):
            for key, val in data.items():
                if isinstance(val, str):
                    _integration_cache[key] = val
    return _integration_cache


# ---------------------------------------------------------------------------
# Component resolution
# ---------------------------------------------------------------------------

def resolve_exercise_components(
    exercise_id: str,
    exercise_type: str = "",
    description_text: str = "",
    aha_text: str = "",
    integration_text: str = "",
) -> ExerciseComponents:
    """
    Build ExerciseComponents from available sources.

    Priority:
    1. Explicit text passed in (from atoms, practice library, or ab_tady_37 components)
    2. Templates (bridge, intro) keyed by exercise_type
    3. Standards (aha, integration) keyed by exercise_id
    """
    bridge_templates = _load_bridge_templates()
    intro_templates = _load_intro_templates()
    aha_standards = _load_aha_standards()
    integration_standards = _load_integration_standards()

    # Bridge from templates
    bt = bridge_templates.get(exercise_type) or bridge_templates.get("_default") or {}
    bridge = ComponentVariants(
        full=bt.get("full", ""),
        lean=bt.get("lean", ""),
        gentle=bt.get("gentle", ""),
    )

    # Intro from templates
    it = intro_templates.get(exercise_type) or intro_templates.get("_default") or {}
    intro = ComponentVariants(
        full=it.get("full", ""),
        lean=it.get("lean", ""),
    )

    # Description from passed text
    description = ComponentVariants(
        full=description_text,
        lean=_derive_lean(description_text, max_sentences=3) if description_text else "",
    )

    # AHA: prefer passed text, fallback to standard
    aha_full = aha_text or aha_standards.get(exercise_id, "")
    aha = ComponentVariants(
        full=aha_full,
        lean=_derive_lean(aha_full) if aha_full else "",
    )

    # Integration: prefer passed text, fallback to standard
    int_full = integration_text or integration_standards.get(exercise_id, "")
    integration = ComponentVariants(
        full=int_full,
        lean=_derive_lean(int_full) if int_full else "",
    )

    return ExerciseComponents(
        exercise_id=exercise_id,
        exercise_type=exercise_type,
        bridge=bridge,
        intro=intro,
        description=description,
        aha=aha,
        integration=integration,
    )


def resolve_from_ab_tady_components(exercise_data: dict) -> ExerciseComponents:
    """Build ExerciseComponents from an ab_tady_37 JSON entry with components field."""
    comps = exercise_data.get("components") or {}
    exercise_id = exercise_data.get("id", "")
    exercise_type = exercise_data.get("exercise_type", "")

    def _variants(key: str) -> ComponentVariants:
        c = comps.get(key) or {}
        if isinstance(c, str):
            return ComponentVariants(full=c, lean=_derive_lean(c))
        return ComponentVariants(
            full=c.get("full", ""),
            lean=c.get("lean", "") or _derive_lean(c.get("full", "")),
            gentle=c.get("gentle", ""),
        )

    return ExerciseComponents(
        exercise_id=exercise_id,
        exercise_type=exercise_type,
        bridge=_variants("bridge"),
        intro=_variants("intro"),
        description=_variants("description"),
        aha=_variants("aha"),
        integration=_variants("integration"),
    )


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------

def _get_text(variants: ComponentVariants, mode: ComponentMode, tone: str = "") -> str:
    """Select the right text variant based on mode and tone."""
    if mode == ComponentMode.SKIP:
        return ""
    if mode == ComponentMode.LEAN:
        return variants.lean or _derive_lean(variants.full)
    # FULL mode
    if tone == "gentle" and variants.gentle:
        return variants.gentle
    return variants.full


def assemble_exercise(
    components: ExerciseComponents,
    selection: ComponentSelection,
) -> str:
    """
    Join selected exercise components into final prose.

    Returns the composed text with paragraph breaks between components.
    Components set to SKIP are omitted entirely.
    """
    parts: list[str] = []

    bridge_text = _get_text(components.bridge, selection.bridge, selection.bridge_tone)
    if bridge_text:
        parts.append(bridge_text)

    intro_text = _get_text(components.intro, selection.intro)
    if intro_text:
        parts.append(intro_text)

    desc_text = _get_text(components.description, selection.description)
    if desc_text:
        parts.append(desc_text)

    aha_text = _get_text(components.aha, selection.aha)
    if aha_text:
        parts.append(aha_text)

    int_text = _get_text(components.integration, selection.integration)
    if int_text:
        parts.append(int_text)

    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# High-level entry point for chapter_composer
# ---------------------------------------------------------------------------

def assemble_exercise_for_chapter(
    exercise_id: str,
    exercise_type: str,
    description_text: str,
    ctx: AssemblyContext,
    aha_text: str = "",
    integration_text: str = "",
    ab_tady_data: Optional[dict] = None,
    rules: Optional[list[dict]] = None,
) -> str:
    """
    Full pipeline: resolve components → select modes → assemble text.

    Called by chapter_composer.py when exercise_context is provided.
    Returns the complete exercise block (bridge through integration).
    """
    if ab_tady_data and ab_tady_data.get("components"):
        components = resolve_from_ab_tady_components(ab_tady_data)
    else:
        components = resolve_exercise_components(
            exercise_id=exercise_id,
            exercise_type=exercise_type,
            description_text=description_text,
            aha_text=aha_text,
            integration_text=integration_text,
        )

    selection = select_components(ctx, rules)
    return assemble_exercise(components, selection)
