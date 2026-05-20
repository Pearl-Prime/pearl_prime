"""
Exercise component assembler: selects and joins exercise components
based on assembly context and YAML-driven rules.

Integration point: chapter_composer.py calls assemble_exercise_for_chapter()
to get the fully composed exercise text (bridge + intro + description + aha + integration)
with only the appropriate components at the right depth.
"""
from __future__ import annotations

import hashlib
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
INTRODUCTION_TEMPLATES_PATH = REPO_ROOT / "SOURCE_OF_TRUTH" / "exercises_v4" / "introduction_templates.yaml"  # OPD-113
INTRO_TEMPLATES_PATH = REPO_ROOT / "SOURCE_OF_TRUTH" / "exercises_v4" / "intro_templates.yaml"
AHA_STANDARD_PATH = REPO_ROOT / "SOURCE_OF_TRUTH" / "exercises_v4" / "aha_noticing_phoenix_standard.yaml"
INTEGRATION_STANDARD_PATH = REPO_ROOT / "SOURCE_OF_TRUTH" / "exercises_v4" / "integration_phoenix_standard.yaml"

# Canonical exercise types (bridge/intro templates) — rotation fallback when type unknown.
EXERCISE_TYPES_ROTATION: tuple[str, ...] = (
    "00_breath_regulation",
    "01_grounding_orientation",
    "02_body_awareness_scan",
    "03_somatic_release_discharge",
    "04_nervous_system_downregulation",
    "05_nervous_system_upregulation",
    "06_vagal_stimulation_sound",
    "07_self_contact_touch",
    "08_emotional_processing_completion",
    "09_embodied_intention_direction",
    "10_integration_return_to_baseline",
)

# Pools of Phoenix-standard aha/integration keys (must exist in aha_noticing_phoenix_standard.yaml).
AHA_POOL_BY_EXERCISE_TYPE: dict[str, tuple[str, ...]] = {
    "00_breath_regulation": (
        "physiological_sigh",
        "cyclic_sighing",
        "extended_exhale_breathing",
        "coherent_breathing",
        "nasal_breathing_reset",
        "diaphragmatic_breathing",
        "four_seven_eight_breathing",
    ),
    "01_grounding_orientation": (
        "orienting_practice",
        "five_four_three_two_one_sensory_reset",
        "grounding_through_feet",
        "eye_softening",
        "slow_standing_transition",
    ),
    "02_body_awareness_scan": (
        "body_scan",
        "hand_temperature_awareness",
        "neck_lengthening",
        "shoulder_drop_reset",
    ),
    "03_somatic_release_discharge": (
        "micro_shake_release",
        "progressive_muscle_release",
        "shoulder_drop_reset",
        "jaw_release",
    ),
    "04_nervous_system_downregulation": (
        "extended_exhale_breathing",
        "physiological_sigh",
        "coherent_breathing",
        "nasal_breathing_reset",
    ),
    "05_nervous_system_upregulation": (
        "cold_water_reset",
        "wall_push_reset",
        "slow_standing_transition",
        "gentle_rocking",
    ),
    "06_vagal_stimulation_sound": (
        "coherent_breathing",
        "nasal_breathing_reset",
        "extended_exhale_breathing",
    ),
    "07_self_contact_touch": (
        "hand_temperature_awareness",
        "open_chest_expansion",
        "grounding_through_feet",
    ),
    "08_emotional_processing_completion": (
        "body_scan",
        "progressive_muscle_release",
        "cross_body_tapping",
        "gentle_rocking",
    ),
    "09_embodied_intention_direction": (
        "open_chest_expansion",
        "seated_forward_fold",
        "slow_standing_transition",
    ),
    "10_integration_return_to_baseline": (
        "slow_standing_transition",
        "gentle_rocking",
        "warmth_reset",
        "coherent_breathing",
    ),
}


def _stable_pool_index(seed: str, pool_size: int) -> int:
    if pool_size <= 0:
        return 0
    digest = hashlib.sha256(seed.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % pool_size


def infer_exercise_type(chapter_index: int, exercise_type: str) -> str:
    et = (exercise_type or "").strip()
    if et in AHA_POOL_BY_EXERCISE_TYPE:
        return et
    return EXERCISE_TYPES_ROTATION[chapter_index % len(EXERCISE_TYPES_ROTATION)]


def pick_phoenix_standard_key(
    chapter_index: int,
    exercise_type: str,
    resolution_seed: str,
) -> str:
    """Deterministic Phoenix-standard key for aha/integration YAML lookup."""
    eff = infer_exercise_type(chapter_index, exercise_type)
    pool = AHA_POOL_BY_EXERCISE_TYPE[eff]
    idx = _stable_pool_index(f"{resolution_seed}:phoenix_std:{eff}:ch{chapter_index}", len(pool))
    return pool[idx]


# practice_library_loader categories → exercises_v4 template key
_CATEGORY_TO_EXERCISE_TYPE: dict[str, str] = {
    "breath_regulation": "00_breath_regulation",
    "sensory_grounding": "01_grounding_orientation",
    "body_awareness": "02_body_awareness_scan",
    "meditations": "10_integration_return_to_baseline",
}


def phoenix_blocks_for_practice_category(
    category: str,
    chapter_index: int,
    seed: str,
) -> tuple[str, str]:
    """Return (aha_text, integration_text) from Phoenix standards for library-compose path."""
    ex_t = _CATEGORY_TO_EXERCISE_TYPE.get(category) or "00_breath_regulation"
    key = pick_phoenix_standard_key(chapter_index, ex_t, seed)
    aha_standards = _load_aha_standards()
    integration_standards = _load_integration_standards()
    aha = (
        aha_standards.get(key, "")
        or aha_standards.get("_default", "")
    ).strip()
    integration = (
        integration_standards.get(key, "")
        or integration_standards.get("_default", "")
    ).strip()
    return aha, integration


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
            # OPD-113: `introduction` defaults to mirror `intro` mode when not
            # set explicitly — so existing rules keep their behavior. Rules
            # that explicitly skip intro (quick_repeat, flow_state, session_close)
            # also skip the introduction cue, preserving their flow intent.
            introduction_mode = comps.get(
                "introduction", comps.get("intro", "full")
            )
            return ComponentSelection(
                bridge=ComponentMode(comps.get("bridge", "lean")),
                introduction=ComponentMode(introduction_mode),
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
_introduction_cache: dict[str, dict] = {}  # OPD-113
_intro_cache: dict[str, dict] = {}
_aha_cache: dict[str, str] = {}
_integration_cache: dict[str, str] = {}


def _load_bridge_templates(path: Optional[Path] = None) -> dict[str, dict]:
    if not _bridge_cache:
        data = _load_yaml(path or BRIDGE_TEMPLATES_PATH)
        for key, val in (data.get("templates") or {}).items():
            _bridge_cache[key] = val
    return _bridge_cache


def _load_introduction_templates(path: Optional[Path] = None) -> dict[str, dict]:
    """Load OPD-113 introduction templates ("Now we're going to do an exercise" cue).

    Backward-compatible: missing file or empty templates → empty cache → caller
    treats absence as SKIP and emits nothing for the introduction component.
    """
    if not _introduction_cache:
        data = _load_yaml(path or INTRODUCTION_TEMPLATES_PATH)
        for key, val in (data.get("templates") or {}).items():
            _introduction_cache[key] = val
    return _introduction_cache


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
    chapter_index: int = 0,
    resolution_seed: str = "",
) -> ExerciseComponents:
    """
    Build ExerciseComponents from available sources.

    Priority:
    1. Explicit text passed in (from atoms, practice library, or ab_tady_37 components)
    2. Templates (bridge, intro) keyed by exercise_type
    3. Standards (aha, integration) keyed by exercise_id
    """
    bridge_templates = _load_bridge_templates()
    introduction_templates = _load_introduction_templates()  # OPD-113
    intro_templates = _load_intro_templates()
    aha_standards = _load_aha_standards()
    integration_standards = _load_integration_standards()

    eff_type = infer_exercise_type(chapter_index, exercise_type)
    seed = resolution_seed or exercise_id or f"ch{chapter_index}"
    std_key = pick_phoenix_standard_key(chapter_index, exercise_type, seed)

    # Bridge from templates
    bt = bridge_templates.get(eff_type) or bridge_templates.get("_default") or {}
    bridge = ComponentVariants(
        full=bt.get("full", ""),
        lean=bt.get("lean", ""),
        gentle=bt.get("gentle", ""),
    )

    # Introduction from templates (OPD-113: explicit "Now we're going to do an
    # exercise" cue — operator's Part 1 of the 5-part structure)
    intr = introduction_templates.get(eff_type) or introduction_templates.get("_default") or {}
    introduction = ComponentVariants(
        full=intr.get("full", ""),
        lean=intr.get("lean", ""),
    )

    # Intro from templates (operator's Part 2 / "description" in operator-speak)
    it = intro_templates.get(eff_type) or intro_templates.get("_default") or {}
    intro = ComponentVariants(
        full=it.get("full", ""),
        lean=it.get("lean", ""),
    )

    # Description from passed text
    description = ComponentVariants(
        full=description_text,
        lean=_derive_lean(description_text, max_sentences=3) if description_text else "",
    )

    # AHA: explicit text, then YAML keyed by atom/technique id, then Phoenix standard pool
    aha_full = (
        aha_text
        or aha_standards.get(exercise_id, "")
        or aha_standards.get(std_key, "")
        or aha_standards.get("_default", "")
    )
    aha = ComponentVariants(
        full=aha_full,
        lean=_derive_lean(aha_full) if aha_full else "",
    )

    # Integration: same precedence; integration file may only define a subset of keys
    int_full = (
        integration_text
        or integration_standards.get(exercise_id, "")
        or integration_standards.get(std_key, "")
        or integration_standards.get("_default", "")
    )
    integration = ComponentVariants(
        full=int_full,
        lean=_derive_lean(int_full) if int_full else "",
    )

    return ExerciseComponents(
        exercise_id=exercise_id,
        exercise_type=eff_type,
        bridge=bridge,
        introduction=introduction,  # OPD-113
        intro=intro,
        description=description,
        aha=aha,
        integration=integration,
    )


def resolve_from_ab_tady_components(exercise_data: dict) -> ExerciseComponents:
    """Build ExerciseComponents from an ab_tady_37 JSON entry with components field.

    OPD-113: pulls introduction from the ab_tady data if present; otherwise
    falls back to the template-driven introduction by exercise_type so that
    the explicit "Now we're going to do an exercise" cue is always available.
    """
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

    # OPD-113: introduction — prefer ab_tady-provided field, else template fallback
    introduction = _variants("introduction")
    if not introduction.full and not introduction.lean:
        intr_templates = _load_introduction_templates()
        eff_type = infer_exercise_type(0, exercise_type)
        intr = intr_templates.get(eff_type) or intr_templates.get("_default") or {}
        introduction = ComponentVariants(
            full=intr.get("full", ""),
            lean=intr.get("lean", ""),
        )

    return ExerciseComponents(
        exercise_id=exercise_id,
        exercise_type=exercise_type,
        bridge=_variants("bridge"),
        introduction=introduction,  # OPD-113
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

    Order (OPD-113 operator's 5-part exercise structure):
      bridge (optional transition)
      → introduction  (Part 1: "Now we're going to do an exercise")
      → intro         (Part 2: description — "This is a X practice...")
      → description   (Part 3: guidance — the atom text itself)
      → aha           (Part 4: what happens / what to notice)
      → integration   (Part 5: how to carry it forward)

    Returns the composed text with paragraph breaks between components.
    Components set to SKIP are omitted entirely.
    """
    parts: list[str] = []

    bridge_text = _get_text(components.bridge, selection.bridge, selection.bridge_tone)
    if bridge_text:
        parts.append(bridge_text)

    # OPD-113: explicit "Now we're going to do an exercise" cue (Part 1)
    introduction_text = _get_text(components.introduction, selection.introduction)
    if introduction_text:
        parts.append(introduction_text)

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
            chapter_index=ctx.chapter_index,
            resolution_seed=exercise_id or description_text[:40],
        )

    selection = select_components(ctx, rules)
    return assemble_exercise(components, selection)
