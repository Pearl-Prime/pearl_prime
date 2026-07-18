"""
Knob Apply Stage Contract — function signatures and dataclasses only.

Authority: docs/KNOB_APPLY_STAGE_CONTRACT.md
Implementation of apply_knobs() is a separate workstream.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union


# --- Spine input (SpineSelect output) ---


@dataclass
class SpineSourceMeta:
    path: str
    content_sha256: Optional[str] = None


@dataclass
class SequencingRules:
    must_come_before: List[str] = field(default_factory=list)
    cannot_come_too_early: List[str] = field(default_factory=list)
    saved_for_late_book: List[str] = field(default_factory=list)


@dataclass
class IntensityProfileLabeled:
    style: str = "labeled_list"
    by_chapter: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class IntensityProfileNumeric:
    style: str = "numeric_12"
    levels: List[Union[int, float]] = field(default_factory=list)


@dataclass
class ToneAndPacing:
    intensity_profile: Optional[Union[IntensityProfileLabeled, IntensityProfileNumeric, Dict[str, Any]]] = None
    trust_curve: Optional[str] = None
    action_timing: Optional[str] = None
    mechanism_timing: Optional[str] = None
    permission_timing: Optional[str] = None


@dataclass
class SelectedChapter:
    """One chapter from the selected spine (immutable fields for KnobApply)."""

    number: int
    role: str
    working_title: str
    thesis: str
    emotional_job: str
    practical_job: str
    what_changes: str
    required_sections: List[str]
    forbidden_moves: List[str]
    recommended_enrichments: List[str]
    claim_someone_could_argue: Optional[str] = None
    why_this_chapter_exists: Optional[str] = None
    what_comes_next: Optional[str] = None


@dataclass
class SelectedSpine:
    """Input from SpineSelect stage — see docs/KNOB_APPLY_STAGE_CONTRACT.md §2."""

    schema_version: int
    stage: str
    family_id: str
    family_name: str
    topic: str
    adjacent_topics: List[str]
    primary_mechanism: str
    allowed_engines: List[str]
    forbidden_engines: List[str]
    reader_starting_state: str
    reader_ending_state: str
    what_makes_this_family_different: str
    chapters: List[SelectedChapter]
    sequencing_rules: SequencingRules
    tone_and_pacing: ToneAndPacing
    source: Optional[SpineSourceMeta] = None


# --- Knob profile (resolver output from topic_knob_profiles.yaml) ---


@dataclass
class DangerousCombination:
    knobs: List[str]
    chapter_range: str
    reason: str


@dataclass
class PlatformConflictRule:
    platform: List[str]
    conflict: str
    resolution: str


@dataclass
class KnobState:
    """
    Resolved or partial knob tuple. Field names match topic_knob_profiles.yaml
    (story_density, exercise_density, mechanism_depth, …).
    None means “not specified at this overlay level.”
    """

    story_density: Optional[str] = None
    exercise_density: Optional[str] = None
    mechanism_depth: Optional[str] = None
    reflection_depth: Optional[str] = None
    pacing_profile: Optional[str] = None
    emotional_temperature: Optional[str] = None
    practical_vs_contemplative: Optional[str] = None
    teacher_presence: Optional[str] = None
    spirituality_level: Optional[str] = None
    compression: Optional[str] = None
    narrative_structure: Optional[str] = None
    runtime_target: Optional[str] = None


@dataclass
class KnobProfile:
    """Input from topic_knob_profiles.yaml resolver — contract §3."""

    schema_version: int
    topic: str
    source: str
    primary_mechanism: str
    allowed_engines: List[str]
    forbidden_engines: List[str]
    knob_defaults: KnobState
    hard_floors: KnobState
    hard_ceilings: KnobState
    phase_overrides: Dict[str, KnobState]
    dangerous_combinations: List[DangerousCombination]
    platform_conflicts: List[PlatformConflictRule] = field(default_factory=list)
    research_citations: List[Dict[str, Any]] = field(default_factory=list)
    requires_human_decision: List[Dict[str, Any]] = field(default_factory=list)
    persona_overrides: KnobState = field(default_factory=KnobState)
    platform_overrides: KnobState = field(default_factory=KnobState)


# --- KnobApply output ---


@dataclass
class ShapedChapter(SelectedChapter):
    """Spine chapter plus KnobApply-derived shaping — contract §4."""

    shaped_section_weights: Dict[str, float] = field(default_factory=dict)
    knob_state: KnobState = field(default_factory=KnobState)
    emotional_temperature: str = ""
    pacing_profile: str = ""
    target_word_count: int = 0
    phase: str = ""  # early_book | mid_book | late_book
    compression_allowed: bool = False
    enrichment_priority: List[str] = field(default_factory=list)


@dataclass
class KnobAudit:
    knobs_applied: Dict[str, Any] = field(default_factory=dict)
    sequencing_constraints_applied: List[Dict[str, Any]] = field(default_factory=list)
    floors_enforced: List[Dict[str, Any]] = field(default_factory=list)
    ceilings_enforced: List[Dict[str, Any]] = field(default_factory=list)
    dangerous_combos_checked: List[Dict[str, Any]] = field(default_factory=list)
    platform_conflicts_resolved: List[Dict[str, Any]] = field(default_factory=list)
    persona_adjustments_dropped: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ShapedSpine:
    """Output of KnobApply — contract §4."""

    schema_version: int
    stage: str
    topic: str
    family_id: str
    runtime_format: str
    structural_format: Optional[str]
    chapters: List[ShapedChapter]
    knob_audit: KnobAudit
    selected_spine_sha256: Optional[str] = None


def apply_knobs(
    spine: SelectedSpine,
    knob_profile: KnobProfile,
    runtime_format: str,
    persona_id: Optional[str] = None,
    platform_id: Optional[str] = None,
) -> ShapedSpine:
    """
    Apply knob profile to a selected spine, producing a shaped spine.

    Conflict resolution priority (high → low):
      1. Spine sequencing_rules + forbidden_moves + required_sections
      2. Knob hard_floors / hard_ceilings
      3. Knob phase_overrides (per chapter phase)
      4. Runtime + platform constraints / platform_overrides
      5. Persona persona_overrides

    Baseline seed: knob_defaults (see docs/KNOB_APPLY_STAGE_CONTRACT.md §5).

    Returns ShapedSpine with per-chapter section weights + knob_audit.
    """
    raise NotImplementedError("Contract only — implementation in separate PR")
