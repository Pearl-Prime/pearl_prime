"""
Exercise component data models for the composable exercise assembly system.

Exercises are decomposed into these components, mapped to the operator's
5-part exercise structure (OPD-113):

  1. INTRODUCTION  — "Now we're going to do an exercise."  (introduction_templates.yaml)
  2. DESCRIPTION   — "This is a X practice..."             (intro_templates.yaml; called INTRO in code)
  3. GUIDANCE      — the atom text itself                  (passed as description_text → DESCRIPTION)
  4. AHA           — what happens / what to notice         (aha_noticing_phoenix_standard.yaml)
  5. INTEGRATION   — how to carry it forward               (integration_phoenix_standard.yaml)

In addition, an optional BRIDGE prefixes the introduction to soften the transition
from prior narrative content into the exercise.

Each component can be rendered in FULL, LEAN, or SKIP mode depending on assembly context.
"""
from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Optional


class ComponentMode(enum.Enum):
    FULL = "full"
    LEAN = "lean"
    SKIP = "skip"


class EmotionalState(enum.Enum):
    NEUTRAL = "neutral"
    HEAVY = "heavy"
    FLOW = "flow"
    CLOSE = "close"


@dataclass
class AssemblyContext:
    """Signals the assembler reads to decide which components to include."""

    first_encounter: bool = True
    emotional_state: EmotionalState = EmotionalState.NEUTRAL
    repeat_count: int = 0
    is_session_close: bool = False
    persona: str = ""
    exercise_id: str = ""
    chapter_index: int = 0
    topic: str = ""


@dataclass
class ComponentVariants:
    """Full and lean text for a single exercise component."""

    full: str = ""
    lean: str = ""
    gentle: str = ""  # bridge-only: softer tone for post-emotional content


@dataclass
class ExerciseComponents:
    """All component variants for a single exercise.

    OPD-113: `introduction` was added as the explicit "Now we're going to do an
    exercise" cue (operator's Part 1 of the 5-part exercise structure). It is
    backward-compatible — when its variants are empty, the assembler emits nothing.
    """

    exercise_id: str = ""
    exercise_type: str = ""
    bridge: ComponentVariants = field(default_factory=ComponentVariants)
    introduction: ComponentVariants = field(default_factory=ComponentVariants)  # OPD-113
    intro: ComponentVariants = field(default_factory=ComponentVariants)
    description: ComponentVariants = field(default_factory=ComponentVariants)
    aha: ComponentVariants = field(default_factory=ComponentVariants)
    integration: ComponentVariants = field(default_factory=ComponentVariants)


@dataclass
class ComponentSelection:
    """Resolved selection: which mode for each component."""

    bridge: ComponentMode = ComponentMode.LEAN
    introduction: ComponentMode = ComponentMode.FULL  # OPD-113: default to explicit cue
    intro: ComponentMode = ComponentMode.FULL
    description: ComponentMode = ComponentMode.FULL
    aha: ComponentMode = ComponentMode.FULL
    integration: ComponentMode = ComponentMode.FULL
    bridge_tone: str = ""  # "gentle" when post-emotional
    rule_name: str = "default"
