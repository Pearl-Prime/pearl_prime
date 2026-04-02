"""
Exercise component data models for the composable exercise assembly system.

Exercises are decomposed into 5 components: BRIDGE, INTRO, DESCRIPTION, AHA, INTEGRATION.
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
    """All 5 component variants for a single exercise."""

    exercise_id: str = ""
    exercise_type: str = ""
    bridge: ComponentVariants = field(default_factory=ComponentVariants)
    intro: ComponentVariants = field(default_factory=ComponentVariants)
    description: ComponentVariants = field(default_factory=ComponentVariants)
    aha: ComponentVariants = field(default_factory=ComponentVariants)
    integration: ComponentVariants = field(default_factory=ComponentVariants)


@dataclass
class ComponentSelection:
    """Resolved selection: which mode for each component."""

    bridge: ComponentMode = ComponentMode.LEAN
    intro: ComponentMode = ComponentMode.FULL
    description: ComponentMode = ComponentMode.FULL
    aha: ComponentMode = ComponentMode.FULL
    integration: ComponentMode = ComponentMode.FULL
    bridge_tone: str = ""  # "gentle" when post-emotional
    rule_name: str = "default"
