"""
Practice Library Loader — loads 272 production-ready exercises from inbox
and composes them using the 5-dimension component template system.

Each exercise is assembled at runtime:
  bridge[i] + intro_template(name, mechanism[j]) + description +
  aha_template(obs[k], perm[l]) + integration_template(takeaway[m], closing[n])

12 exercises per book, each picks unique indices to never repeat.

Integration: called by slot_resolver or registry_resolver when EXERCISE
slot needs content. Returns fully composed exercise text with aha + integration.
"""
from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
INBOX_ROOT = REPO_ROOT / "SOURCE_OF_TRUTH" / "practice_library" / "inbox"
COMPONENT_TEMPLATES_PATH = REPO_ROOT / "config" / "pearl_practice" / "component_templates.yaml"
EXERCISE_TEMPLATES_PATH = REPO_ROOT / "config" / "pearl_practice" / "exercise_templates.yaml"

# Cache
_LIBRARY_CACHE: Optional[dict[str, list[dict]]] = None
_TEMPLATES_CACHE: Optional[dict] = None


def _load_yaml(path: Path) -> Any:
    if not path.exists() or yaml is None:
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _deterministic_index(seed: str, pool_size: int) -> int:
    if pool_size <= 0:
        return 0
    digest = hashlib.sha256(seed.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % pool_size


def load_practice_library() -> dict[str, list[dict]]:
    """Load all production-ready exercises from inbox, indexed by exercise_type.

    Returns:
        Dict keyed by exercise_type (e.g., "body_awareness") -> list of exercise dicts.
        Each exercise dict has: id, name, text, exercise_type, components, duration_seconds, tags.
    """
    global _LIBRARY_CACHE
    if _LIBRARY_CACHE is not None:
        return _LIBRARY_CACHE

    library: dict[str, list[dict]] = {}

    if not INBOX_ROOT.exists():
        logger.warning("Practice library inbox not found: %s", INBOX_ROOT)
        return library

    for json_path in sorted(INBOX_ROOT.glob("*_PRODUCTION_READY.json")):
        try:
            with open(json_path, encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Failed to load %s: %s", json_path.name, e)
            continue

        # Handle both list and dict formats
        if isinstance(data, dict):
            items = data.get("exercises", data.get("items", []))
            content_type = data.get("content_type", json_path.stem.split("_library")[0])
        elif isinstance(data, list):
            items = data
            content_type = json_path.stem.split("_library")[0]
        else:
            continue

        for item in items:
            if not isinstance(item, dict):
                continue
            ex_type = item.get("exercise_type", content_type)
            if ex_type not in library:
                library[ex_type] = []
            library[ex_type].append(item)

    total = sum(len(v) for v in library.values())
    logger.info("Loaded practice library: %d exercises across %d types", total, len(library))
    _LIBRARY_CACHE = library
    return library


def load_component_templates() -> dict:
    """Load the 5-dimension component template config."""
    global _TEMPLATES_CACHE
    if _TEMPLATES_CACHE is not None:
        return _TEMPLATES_CACHE
    _TEMPLATES_CACHE = _load_yaml(COMPONENT_TEMPLATES_PATH)
    return _TEMPLATES_CACHE


def compose_exercise(
    exercise: dict,
    chapter_index: int,
    seed: str,
    templates: Optional[dict] = None,
) -> str:
    """Compose a full exercise with bridge + intro + description + aha + integration.

    Uses the 5-dimension component template system for maximum variation.

    Args:
        exercise: Exercise dict from practice library (must have 'text' and 'name')
        chapter_index: Chapter position (for deterministic rotation)
        seed: Book-level seed for deterministic selection
        templates: Component templates (loaded if not provided)

    Returns:
        Fully composed exercise text ready for rendering.
    """
    templates = templates or load_component_templates()

    name = exercise.get("name", "Exercise")
    description = exercise.get("text", "")
    ex_type = exercise.get("exercise_type", "body_awareness")
    components = exercise.get("components", {})

    # Use pre-composed components if available
    if isinstance(components, dict) and components.get("bridge"):
        # Components may be strings or dicts with full/lean variants
        def _get_text(comp):
            if isinstance(comp, str):
                return comp
            if isinstance(comp, dict):
                return comp.get("full", comp.get("text", str(comp)))
            return str(comp) if comp else ""
        bridge = _get_text(components["bridge"])
        intro = _get_text(components.get("intro", ""))
        aha = _get_text(components.get("aha", ""))
        integration = _get_text(components.get("integration", ""))
        return f"{bridge}\n\n{intro}\n\n{description}\n\n{aha}\n\n{integration}".strip()

    # Otherwise compose from templates
    h = f"{seed}:exercise:ch{chapter_index}"

    # 1. Bridge (rotate 1 per chapter, never repeat)
    bridges = templates.get("bridge", ["Try this before you move on."])
    bridge = bridges[chapter_index % len(bridges)]

    # 2. Intro = "This is {name}. {mechanism}."
    # Map exercise_type to template category
    type_map = {
        "00_breath_regulation": "breath_regulation",
        "01_grounding_orientation": "sensory_grounding",
        "02_body_awareness_scan": "body_awareness",
        "03_somatic_release_discharge": "body_awareness",
        "04_nervous_system_downregulation": "breath_regulation",
        "05_nervous_system_upregulation": "breath_regulation",
        "06_vagal_stimulation_sound": "breath_regulation",
        "07_self_contact_touch": "body_awareness",
        "08_emotional_processing_completion": "meditations",
        "09_embodied_intention_direction": "meditations",
        "10_integration_return_to_baseline": "meditations",
    }
    category = type_map.get(ex_type, ex_type)
    mechanisms = templates.get("intro_mechanism", {}).get(category, ["Your body already knows."])
    mechanism = mechanisms[_deterministic_index(h + ":mech", len(mechanisms))]
    intro = f"This is {name}. {mechanism}"

    # 3. Description (the exercise text itself)
    # Already in 'description'

    # 4. Aha = "Now, notice {observation}. {permission}."
    observations = templates.get("aha_observation", {}).get(category, ["what shifted"])
    permissions = templates.get("aha_permission", ["Whatever came up is valid."])
    obs = observations[_deterministic_index(h + ":obs", len(observations))]
    perm = permissions[_deterministic_index(h + ":perm", len(permissions))]
    aha = f"Now, notice {obs}. {perm}"

    # 5. Integration = "Before you move on, {takeaway}. {closing}."
    takeaways = templates.get("integration_takeaway", {}).get(category, ["carry this with you"])
    closings = templates.get("integration_closing", ["You can return to this anytime."])
    takeaway = takeaways[_deterministic_index(h + ":take", len(takeaways))]
    closing = closings[_deterministic_index(h + ":close", len(closings))] if closings else ""
    integration = f"Before you move on, {takeaway}. {closing}".strip()

    return f"{bridge}\n\n{intro}\n\n{description}\n\n{aha}\n\n{integration}".strip()


def get_exercise_for_chapter(
    chapter_index: int,
    topic_id: str,
    persona_id: str,
    seed: str,
    used_exercise_ids: Optional[set] = None,
) -> Optional[str]:
    """Get a fully composed exercise for a chapter position.

    Selects from the full 272-exercise library, avoiding repeats within a book.
    Returns composed text (bridge + intro + description + aha + integration)
    or None if no exercises available.
    """
    library = load_practice_library()
    templates = load_component_templates()
    used = used_exercise_ids or set()

    # Flatten all exercises into one pool
    all_exercises = []
    for ex_type, exercises in library.items():
        all_exercises.extend(exercises)

    if not all_exercises:
        return None

    # Filter out already used
    available = [e for e in all_exercises if e.get("id") not in used]
    if not available:
        available = all_exercises  # allow reuse if exhausted (272 > 12 chapters, shouldn't happen)

    # Select deterministically
    idx = _deterministic_index(f"{seed}:exercise_select:ch{chapter_index}", len(available))
    exercise = available[idx]

    # Track usage
    if used_exercise_ids is not None:
        used_exercise_ids.add(exercise.get("id", ""))

    return compose_exercise(exercise, chapter_index, seed, templates)
