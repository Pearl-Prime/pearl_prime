#!/usr/bin/env python3
"""Continuity-state generator — Milestone C Step 1+ (per OPD-140).

Reads an operator-authored beatsheet (per docs/specs/MANGA_BEATSHEET_SCHEMA.yaml)
and emits N per-panel continuity_state YAMLs (per docs/specs/MANGA_CONTINUITY_STATE_SPEC.md).

This module is PURE-PYTHON + DETERMINISTIC. No LLM, no embeddings, no external APIs.
Per CLAUDE.md tier policy: continuity_state generation is heuristic + deterministic,
NOT generative; LLMs would compromise round-trip reproducibility.

Pipeline (per design notes §4.2):

    beatsheet.yaml + (series_profile, scene_inventory, style_state, panel_template,
                       light_rig_library, character_pose_inventory)
       ↓
    [1] Parse + validate beatsheet schema
    [2] Compute header fields
    [3] For each beat:
        [3a] Initialize state from inheritance (defaults if beat 1; else prev panel)
        [3b] Apply beat scene / character / props overrides
        [3c] Run archetype dispatch (§3 of design notes)
        [3d] Run heuristic rules H1-H10 (§2 of design notes)
        [3e] Emit auto-commentary continuity_invariants
        [3f] Compute panel_id + inherits_from
        [3g] Write panel YAML

CLI:
    python3 scripts/manga/continuity_state_generator.py \\
        --beatsheet artifacts/.../ep_001/_extracted_beatsheet.yaml \\
        --output-dir /tmp/v51_step1_roundtrip/ep_001

Encoded operator decisions (from artifacts/coordination/operator_decisions_log.tsv):
    OPD-142 (OPEN-1, ep001_016 on_frame contradiction):
        Generator emits on_frame=false when character_state is empty for the beat.
        Reconciles relational_field with character_state.
    OPD-143 (OPEN-2, ep001_017 dial citation):
        Generator computes magnitude_delta arithmetically from inheritance chain.
        Comment field is operator prose; generator never reads it.
    OPD-144 (OPEN-3, tension_vector.direction):
        Generator default = literal H3 (numerical delta sign mapped to enum).
        Operator override via beat.tension_override (enum: rising|steady|easing|reversing).
"""
from __future__ import annotations

import argparse
import copy
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import yaml


# ─────────────────────────────────────────────────────────────────────────────
# Exceptions
# ─────────────────────────────────────────────────────────────────────────────


class BeatsheetValidationError(ValueError):
    """Beatsheet failed schema validation. Includes field path on failure."""


class ArchetypeNotImplementedError(NotImplementedError):
    """Beat uses an archetype not in the V1 dispatch table. Per design notes §3
    coverage gap: only the 12 archetypes exercised by ep_001 are supported in V1.
    Operator instruction (2026-05-24): do not pre-build dispatch for the 7
    unused iyashikei archetypes; let ep_002+ surface what they need.
    """


class GeneratorError(RuntimeError):
    """Pipeline-level failure — bubble up with context."""


# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────


SCHEMA_VERSION = "1.0.0"
CHARACTER_DESIGN_HASH_PENDING = "axes_only_PENDING_compute"

# V4 spec §6.3.A invariant 1: scene jumps + temporal jumps allowed on these beat_types
SCENE_JUMP_BEAT_TYPES = {"standard", "long_drop", "miyazaki_ma"}

# V4 spec §6.3.A invariant 6
EXPRESSION_DIAL_BOUNDS = {
    "micro": 0.3,
    "spatial": 0.5,
}

# Temporal cycle (per config/manga/continuity/temporal_cycle.yaml)
DEFAULT_TEMPORAL_CYCLE = ["dawn", "morning", "midday", "afternoon", "evening", "night"]

# V4.1 face-archetype boilerplate string (verbatim from ground truth ep001_006)
V41_FACE_BOILERPLATE = (
    "V4.1 (2026-05-20): per-axis subject_must_not_touch_edge contract shipped (spec "
    "§15.A.7); face-only archetype edge_touch + bleed gates now PASS on bottom+right "
    "axes. subject_safe_zone may still report overflow on top+left guarded axes — that "
    "is a render-precision concern (Mira centering + top hair clearance), not a contract "
    "failure; resolved by render-time prompt refinement on a per-panel basis."
)

# Archetypes that emit the v41_per_axis_edge_resolved + boilerplate (H8).
# secondary_character_face_close joins per OPD-147 — same CU face framing as
# character_quiet_face, identical per-axis subject_must_not_touch_edge contract.
V41_FACE_ARCHETYPES = {
    "character_quiet_face",
    "character_face_micro_tension",
    "secondary_character_face_close",
}

# Per design notes §3 — the 14 archetypes supported in V1 + extension:
#   - 12 from ep_001 (Milestone C Step 1)
#   - +2 from ep_002 (OPD-147 secondary_character_face_close,
#     OPD-148 typographic_caption_card, this PR — joint with multi-character
#     generator extension).
SUPPORTED_ARCHETYPES = {
    "sparse_establishing_wide",
    "tea_beat_close_up",
    "character_quiet_face",
    "chest_breath_micro",
    "character_face_micro_tension",
    "hand_table_micro",
    "dappled_light_hand",
    "pet_companion_micro",
    "seasonal_anchor_object",
    "kettle_steam_macro",
    "long_drop_decompression",
    "pendulation_pair_visual_rhyme",
    # OPD-147 + OPD-148 (2026-05-26) — joint with multi-character extension:
    "secondary_character_face_close",
    "typographic_caption_card",
}

# Archetypes that REQUIRE the beat to declare `subject_actor: <character_id>`
# binding the on-frame character to a specific entry in stage_characters.
# Per OPD-147: secondary_character_face_close is the first parametrized
# archetype; future multi-character archetypes (e.g. shared_meal_table_medium
# when promoted from declared-but-unimplemented) will join this set.
ARCHETYPES_REQUIRING_SUBJECT_ACTOR = {
    "secondary_character_face_close",
}

# Archetypes that suppress ALL stage_characters (META cluster: typographic
# caption cards, future title cards, etc.). For these, the generator emits
# empty character_state for every stage_character and on_frame=false for every
# active_entity. Per OPD-148.
META_ARCHETYPES_SUPPRESSING_ALL_CHARACTERS = {
    "typographic_caption_card",
}

# typographic_caption_card requires `caption_style` parametrized field.
# Validated at load_beatsheet time.
_LEGAL_CAPTION_STYLES = {"mid_episode_strip", "end_episode_card"}

# Per design notes §3 — declared but explicitly out of scope for V1.
# ep_002 surfaces three of these (walking_in_thought_medium, miyazaki_ma_pause,
# window_light_threshold); per design notes §3 "Don't pre-build dispatch for
# them; let the next episodes' beatsheets reveal what they need" — ep_002
# has now done so, so they're promoted to SUPPORTED_ARCHETYPES (with minimal
# dispatch using iyashikei.yaml's existing archetype rows + subject_type from
# scene_context.yaml). The remaining four stay declared-but-unimplemented
# until ep_003+ beatsheets surface their need.
DECLARED_BUT_UNIMPLEMENTED_ARCHETYPES = {
    "morning_routine_sequence",
    "food_preparation_overhead",
    "shared_meal_table_medium",
    "phone_notification_macro",
}

# ep_002-surfaced archetypes (Milestone B Step 2 minimal dispatch). These
# are NOT part of OPD-147/OPD-148 (those are the two new candidates); they
# were already declared in iyashikei.yaml but not dispatched. ep_002's
# beatsheet references them, so we add minimal dispatch here so the
# generator's dry-run flows through. The dispatch is "plain" — no special
# parametrized fields, just standard pose_id + hand_state defaults from
# the existing iyashikei.yaml composition_tokens.
_EP_002_DECLARED_ARCHETYPES_PROMOTED = {
    "walking_in_thought_medium",
    "miyazaki_ma_pause",
    "window_light_threshold",
}
SUPPORTED_ARCHETYPES |= _EP_002_DECLARED_ARCHETYPES_PROMOTED

# Per-archetype default pose_id (from design notes §3 table). When the
# operator doesn't author a pose_id, fall back to this. Where the archetype
# has multiple defaults (e.g. sparse_establishing_wide), operator MUST author.
ARCHETYPE_DEFAULT_POSE_ID = {
    "tea_beat_close_up": "hands_wrapping_cup",
    "character_quiet_face": "front_portrait_seated_calm",
    "chest_breath_micro": "chest_breath_micro",
    "character_face_micro_tension": "front_portrait_seated_tense",
    "hand_table_micro": "hand_only_table",
    "dappled_light_hand": "hand_only_table",
    "pet_companion_micro": "front_portrait_seated_calm",  # off-frame seated
    "seasonal_anchor_object": "front_portrait_seated_calm",  # off-frame
    "kettle_steam_macro": "front_portrait_seated_calm",  # off-frame
    "long_drop_decompression": "full_figure_standing_at_window",
    # OPD-147: default pose for the on-frame subject_actor of
    # secondary_character_face_close. Applies to the subject_actor character
    # ONLY (not to the protagonist, who is off-frame for this archetype).
    "secondary_character_face_close": "face_close_seated_calm",
    # ep_002-surfaced — minimal defaults; ep_002 beatsheet authors specific
    # pose_ids per beat (full_figure_walking_*, full_figure_climbing_stairs,
    # etc.). These defaults are fallback only.
    "walking_in_thought_medium": "full_figure_walking_three_quarter",
    "miyazaki_ma_pause": "full_figure_seated_tiny",  # the rare visible-but-small case
    "window_light_threshold": "full_figure_threshold_door",
    # sparse_establishing_wide: no single default; operator picks
    # pendulation_pair_visual_rhyme: inherits from partner
    # typographic_caption_card: META — no character_state, no pose_id
}

# Per-archetype default hand_state (when operator hasn't overridden).
# Used for FRESH appearance only (no prev character state).
ARCHETYPE_DEFAULT_HAND_STATE = {
    "tea_beat_close_up": "wrapping_cup",
    "character_quiet_face": "relaxed_open",
    "chest_breath_micro": "tucked_self_soothing",
    "character_face_micro_tension": "tucked_self_soothing",
    "hand_table_micro": "relaxed_open",
    "dappled_light_hand": "wrapping_cup",
    "pet_companion_micro": "relaxed_open",
    "long_drop_decompression": "relaxed_open",
    "sparse_establishing_wide": "relaxed_open",
    # OPD-147: applies to subject_actor — secondary character is calm-
    # professional baseline; hands relaxed in lap or on table.
    "secondary_character_face_close": "relaxed_open",
    # ep_002-surfaced: walking + threshold archetypes default to relaxed-open
    # hands; the body is doing the work, not the hands.
    "walking_in_thought_medium": "relaxed_open",
    "miyazaki_ma_pause": "relaxed_open",
    "window_light_threshold": "relaxed_open",
}

# Archetypes where hand_state is PRESCRIPTIVE: the archetype semantically
# requires a specific hand pose. When the archetype changes TO one of these
# and operator didn't override, apply the default. Other archetypes'
# hand_state inherits from prev.
#
# Two categories:
#   - "active" hand archetypes (specific hand action): tea_beat_close_up (cup),
#     chest_breath_micro (self-soothing), dappled_light_hand (cup).
#   - "calm-reset" wide framings where the character is in resting posture:
#     sparse_establishing_wide, long_drop_decompression, pet_companion_micro,
#     seasonal_anchor_object, kettle_steam_macro. These reset hand to
#     relaxed_open (the operator's "character at ease" default).
HAND_PRESCRIPTIVE_ARCHETYPES = {
    "tea_beat_close_up",
    "chest_breath_micro",
    "dappled_light_hand",
    "sparse_establishing_wide",
    "long_drop_decompression",
    "pet_companion_micro",
    "seasonal_anchor_object",
    "kettle_steam_macro",
}

# Per-archetype subject_type → drives H5 on_frame default
# (parallel of config/manga/panel_templates/iyashikei.scene_context.yaml subject_type)
ARCHETYPE_SUBJECT_TYPE = {
    "sparse_establishing_wide": None,
    "tea_beat_close_up": "character_hands_only",
    "character_quiet_face": "character_face_only",
    "chest_breath_micro": "character_chest_partial",
    "character_face_micro_tension": "character_face_only",
    "hand_table_micro": "character_hand_only",
    "dappled_light_hand": "character_hand_only",
    "pet_companion_micro": "character_pet_only",  # null human implied
    "seasonal_anchor_object": None,
    "kettle_steam_macro": None,
    "long_drop_decompression": None,
    "pendulation_pair_visual_rhyme": None,
    # OPD-147: subject is the (parametrized) subject_actor — the protagonist
    # is off-frame by default. Per-character on_frame derivation lives in
    # derive_on_frame_for_character() (multi-character extension).
    "secondary_character_face_close": "character_face_only",
    # OPD-148: META — no character on-frame, no L2 cutout, no rendering
    # via the L0/L1/L2/L3 stack.
    "typographic_caption_card": None,
    # ep_002-surfaced — minimal dispatch (subject_type values match
    # iyashikei.scene_context.yaml entries). Per design notes §3 promote-
    # when-surfaced policy.
    "walking_in_thought_medium": "character_full_figure_walking",
    "miyazaki_ma_pause": None,  # character_ELS_in_L0 — figure baked into L0, no separate on-frame L2 subject
    "window_light_threshold": "character_silhouette_back",
}

# Archetypes where the human character is implied off-frame BY DEFAULT
# even though there's no explicit operator override.
# Per design notes §3: pet_companion_micro has subject_type=character_pet_only,
# meaning the human is implied off-frame. Operator must explicitly set
# on_frame=true to put the human in frame.
ARCHETYPES_DEFAULTING_HUMAN_OFF_FRAME = {"pet_companion_micro"}


# ─────────────────────────────────────────────────────────────────────────────
# Beatsheet parser + schema validator
# ─────────────────────────────────────────────────────────────────────────────


_BEATSHEET_REQUIRED_FIELDS = (
    "schema_version", "beatsheet_type", "series_id", "episode_id",
    "stage_characters", "beats",
)
_BEAT_REQUIRED_FIELDS = ("beat_id", "archetype")
_LEGAL_BEAT_TYPES = {"micro", "spatial", "standard", "long_drop", "miyazaki_ma"}
_LEGAL_TENSION_OVERRIDES = {"rising", "steady", "easing", "reversing"}
_LEGAL_BREATH_PHASES = {"quickening", "holding", "inhale", "exhale", "exhale_settling", "deep_steady"}


def load_beatsheet(path: Path) -> dict:
    """Load + manually-validate beatsheet YAML.

    Validation is intentionally light-touch (no jsonschema dep): just enough
    to catch malformed beatsheets before they propagate through inheritance.

    Returns the validated beatsheet dict.

    Raises BeatsheetValidationError on schema violation with field path.
    """
    if not path.exists():
        raise BeatsheetValidationError(f"beatsheet not found: {path}")

    try:
        doc = yaml.safe_load(path.read_text())
    except yaml.YAMLError as e:
        raise BeatsheetValidationError(f"beatsheet YAML parse error: {e}") from e

    if not isinstance(doc, dict):
        raise BeatsheetValidationError(
            f"beatsheet root must be a mapping; got {type(doc).__name__}"
        )

    for field_name in _BEATSHEET_REQUIRED_FIELDS:
        if field_name not in doc:
            raise BeatsheetValidationError(f"missing required top-level field: {field_name!r}")

    if doc.get("schema_version") != SCHEMA_VERSION:
        raise BeatsheetValidationError(
            f"schema_version mismatch: expected {SCHEMA_VERSION!r}, "
            f"got {doc.get('schema_version')!r}"
        )

    if doc.get("beatsheet_type") != "episode":
        raise BeatsheetValidationError(
            f"only beatsheet_type='episode' supported in V1; got {doc.get('beatsheet_type')!r}"
        )

    stage = doc.get("stage_characters")
    if not isinstance(stage, list) or not stage:
        raise BeatsheetValidationError(
            "stage_characters must be a non-empty list of character_ids"
        )

    beats = doc.get("beats")
    if not isinstance(beats, list) or not beats:
        raise BeatsheetValidationError("beats must be a non-empty list")

    seen_beat_ids = set()
    for idx, beat in enumerate(beats):
        path_str = f"beats[{idx}]"
        if not isinstance(beat, dict):
            raise BeatsheetValidationError(f"{path_str}: beat must be a mapping")
        for field_name in _BEAT_REQUIRED_FIELDS:
            if field_name not in beat:
                raise BeatsheetValidationError(
                    f"{path_str}: missing required field {field_name!r}"
                )
        beat_id = beat["beat_id"]
        if not isinstance(beat_id, str) or not beat_id.startswith("b"):
            raise BeatsheetValidationError(
                f"{path_str}: beat_id must be a string starting with 'b'; got {beat_id!r}"
            )
        if beat_id in seen_beat_ids:
            raise BeatsheetValidationError(f"{path_str}: duplicate beat_id {beat_id!r}")
        seen_beat_ids.add(beat_id)

        # beat_type enum check (if present)
        bt = beat.get("beat_type")
        if bt is not None and bt not in _LEGAL_BEAT_TYPES:
            raise BeatsheetValidationError(
                f"{path_str}.beat_type: {bt!r} not in {sorted(_LEGAL_BEAT_TYPES)}"
            )

        # tension_override enum check (OPD-144)
        to = beat.get("tension_override")
        if to is not None and to not in _LEGAL_TENSION_OVERRIDES:
            raise BeatsheetValidationError(
                f"{path_str}.tension_override: {to!r} not in {sorted(_LEGAL_TENSION_OVERRIDES)}"
            )

        # archetype must be either supported OR declared-but-unimplemented
        arch = beat["archetype"]
        if arch not in SUPPORTED_ARCHETYPES and arch not in DECLARED_BUT_UNIMPLEMENTED_ARCHETYPES:
            # Allow unknown archetypes through schema-validation (generator may
            # error later at dispatch); useful for new genre rollouts where the
            # validator should not block authoring before dispatch lands.
            pass

        # OPD-147: archetypes requiring subject_actor MUST declare it, and
        # the value MUST be a character_id present in stage_characters.
        if arch in ARCHETYPES_REQUIRING_SUBJECT_ACTOR:
            sa = beat.get("subject_actor")
            if sa is None:
                raise BeatsheetValidationError(
                    f"{path_str}: archetype {arch!r} requires beat.subject_actor "
                    f"(character_id of the on-frame focal character)"
                )
            if sa not in stage:
                raise BeatsheetValidationError(
                    f"{path_str}.subject_actor: {sa!r} not in stage_characters {stage}"
                )

        # OPD-148: typographic_caption_card requires caption_style + caption_text.
        if arch == "typographic_caption_card":
            cs = beat.get("caption_style")
            if cs is None:
                raise BeatsheetValidationError(
                    f"{path_str}: archetype typographic_caption_card requires "
                    f"beat.caption_style (one of {sorted(_LEGAL_CAPTION_STYLES)})"
                )
            if cs not in _LEGAL_CAPTION_STYLES:
                raise BeatsheetValidationError(
                    f"{path_str}.caption_style: {cs!r} not in {sorted(_LEGAL_CAPTION_STYLES)}"
                )
            ct = beat.get("caption_text")
            if ct is None or not isinstance(ct, str) or not ct.strip():
                raise BeatsheetValidationError(
                    f"{path_str}: archetype typographic_caption_card requires "
                    f"beat.caption_text (non-empty string)"
                )

        # per-character validation
        char_block = beat.get("character") or {}
        if not isinstance(char_block, dict):
            raise BeatsheetValidationError(
                f"{path_str}.character: must be a mapping (or omit)"
            )
        for cid, cstate in char_block.items():
            if cid not in stage:
                raise BeatsheetValidationError(
                    f"{path_str}.character.{cid}: character_id not in stage_characters"
                )
            if cstate is None:
                continue  # explicit null suppression — fine
            if not isinstance(cstate, dict):
                raise BeatsheetValidationError(
                    f"{path_str}.character.{cid}: must be a mapping or null"
                )
            # breath_phase only valid on chest_breath_micro
            bp = cstate.get("breath_phase")
            if bp is not None:
                if arch != "chest_breath_micro":
                    raise BeatsheetValidationError(
                        f"{path_str}.character.{cid}.breath_phase: only valid on "
                        f"archetype=chest_breath_micro; got archetype={arch!r}"
                    )
                if bp not in _LEGAL_BREATH_PHASES:
                    raise BeatsheetValidationError(
                        f"{path_str}.character.{cid}.breath_phase: {bp!r} not in "
                        f"{sorted(_LEGAL_BREATH_PHASES)}"
                    )

    return doc


# ─────────────────────────────────────────────────────────────────────────────
# H1-H10 heuristic rules (per design notes §2)
# ─────────────────────────────────────────────────────────────────────────────


def derive_light_rig(
    scene_id: str,
    temporal: str,
    scene_inventory: dict | None,
    light_rig_library: dict | None,
) -> str | None:
    """H1: light_rig_id = first(scene_inventory[scene_id].light_rigs intersect
    temporal-compatible rigs in light_rig_library).

    For V1, the temporal compatibility is encoded by NAMING convention in
    light_rig_id (K01_dawn_..., K02_morning_...). When the scene has only
    one rig (e.g. flashback), that rig wins regardless of temporal.

    Returns None when no scene_inventory supplied (operator override required).
    Raises GeneratorError if no compatible rig found.
    """
    if scene_inventory is None:
        return None

    # Find the scene entry
    scenes = scene_inventory.get("scenes", []) or []
    scene_entry = next((s for s in scenes if s.get("scene_id") == scene_id), None)
    if scene_entry is None:
        # New scene declared inline in beatsheet (e.g. conference_room_flashback
        # before backfill). Caller is expected to pin light_rig_id explicitly.
        return None

    rigs = [
        (r.get("light_rig_id") if isinstance(r, dict) else r)
        for r in (scene_entry.get("light_rigs") or [])
    ]
    rigs = [r for r in rigs if r]
    if not rigs:
        raise GeneratorError(
            f"scene {scene_id!r} declares no light_rigs in scene_inventory"
        )

    # When scene_inventory carries multiple rigs, pick the one whose name
    # encodes the temporal (K01_dawn -> dawn). Falls back to first available
    # rig if no match. Heuristic per design notes §2 H1.
    matching = [r for r in rigs if f"_{temporal}_" in r or f"_{temporal}" in r]
    if matching:
        return matching[0]
    if len(rigs) == 1:
        # Single-rig scene (e.g. flashback) — temporal is moot
        return rigs[0]
    # No naming-based match; fail loudly so operator pins explicitly
    raise GeneratorError(
        f"no light_rig matches temporal={temporal!r} in scene_inventory[{scene_id!r}].light_rigs "
        f"({rigs}); set scene.light_rig_id explicitly in the beat"
    )


def derive_gaze(
    beat_character_block: dict | None,
    shared_attention_anchor: str | None,
    prop_state: dict,
) -> str | None:
    """H2: derive gaze from shared_attention_anchor.

    Order of precedence:
        1. Explicit operator override (beat_character_block['gaze'])
        2. shared_attention_anchor → at_named_object_<anchor> (if anchor in prop_state)
        3. None — caller fills from inherited / archetype default / error
    """
    if beat_character_block and "gaze" in beat_character_block:
        return beat_character_block["gaze"]
    if shared_attention_anchor and shared_attention_anchor in (prop_state or {}):
        return f"at_named_object_{shared_attention_anchor}"
    return None


def derive_tension_direction(
    current_dial: float | None,
    prev_dial: float | None,
    tension_override: str | None,
) -> str:
    """H3 + OPD-144: emotional_tension_vector.direction.

    Default (literal): numerical delta sign → enum.
        delta > 0 → 'rising'
        delta < 0 → 'easing'   (V4 ground truth uses 'diminishing' as well;
                                 OPD-144 normalized to 'easing' but legacy
                                 ground truth has neither — only 'rising' and
                                 'steady'. Documenting this distinction is
                                 deliberate; the diff harness treats this as a
                                 known-acceptable divergence pending the broader
                                 enum reconciliation in Phase B.2.)
        delta == 0 → 'steady'

    OPD-144 override: if tension_override is set, return that verbatim.
    """
    if tension_override is not None:
        return tension_override
    if current_dial is None or prev_dial is None:
        return "steady"
    delta = round(current_dial - prev_dial, 3)
    if delta > 0:
        return "rising"
    if delta < 0:
        return "easing"
    return "steady"


def derive_magnitude_delta(
    current_dial: float | None,
    prev_dial: float | None,
) -> float:
    """H4: magnitude_delta_from_prev = literal expression_dial arithmetic.

    Per OPD-143: generator always uses literal arithmetic on the inheritance
    chain. Operator comment fields are NOT consulted.
    """
    if current_dial is None or prev_dial is None:
        return 0.0
    return round(current_dial - prev_dial, 3)


def derive_on_frame(
    beat_character_block: dict | None,
    archetype: str,
    op_has_state: bool = False,
) -> bool:
    """H5: on_frame from archetype.subject_type, with operator override.

    Precedence:
        1. Explicit operator override (beat_character_block['on_frame'])
        2. False when archetype defaults human off-frame (e.g. pet_companion_micro)
        3. True when archetype.subject_type is non-null
        4. True when operator authored real state fields, EVEN IF
           archetype.subject_type is null (operator is putting character in frame)
        5. False when archetype.subject_type is null AND no state authored
           (sparse_establishing_wide etc.)
    """
    if beat_character_block and "on_frame" in beat_character_block:
        return bool(beat_character_block["on_frame"])
    if archetype in ARCHETYPES_DEFAULTING_HUMAN_OFF_FRAME:
        return False
    subject_type = ARCHETYPE_SUBJECT_TYPE.get(archetype)
    if subject_type is not None:
        return True
    # subject_type is None — character in frame ONLY if operator authored state
    return op_has_state


def derive_role(on_frame: bool) -> str:
    """H6: role from on_frame. 100% consistent across all 35 ground-truth panels."""
    return "subject" if on_frame else "implied_listener"


def should_emit_weather_anchor(beat_index: int) -> bool:
    """H7: emit weather_anchor only on beat 1 (per ep_001 evidence).

    Future: also emit on scene_id transitions where new scene's
    scene_inventory declares a weather_anchor; ep_001 has no such case.
    """
    return beat_index == 0


def should_emit_v41_boilerplate(
    archetype: str,
    beat_index: int,
    prev_had_v41: bool = False,
) -> bool:
    """H8: emit v41_per_axis_edge_resolved boilerplate.

    Per ground-truth evidence in ep_001:
        emits on panels: 006, 011, 014, 015, 023, 026, 028, 031.
        Does NOT emit on: 003 (character_quiet_face), 005 (chest_breath_micro),
            007-009, 012, 013, 017 (chest_breath_micro), 020/021 (chest_breath_micro),
            024 (sparse), 025 (seasonal), 027 (kettle), 029 (long_drop),
            030, 032 (sparse), 033 (pendulation), 034 (sparse), 035 (episode card).

    The emerging rule: v41 boilerplate emits on face-only archetypes
    (character_quiet_face, character_face_micro_tension) starting at beat 6
    (ep001_006), where the V4.1 contract was first relevant for the
    activation onset peak. The pet_companion_micro at ep001_014 also carries
    v41 (operator authored — character implied off-frame, but the boilerplate
    accompanies the dial-bounce documentation).

    V1 implementation: face-only archetypes starting at panel_index >= 5
    (ep001_006), plus pet_companion_micro as a one-off rule.
    """
    if beat_index < 5:
        return False
    if archetype in V41_FACE_ARCHETYPES:
        return True
    # pet_companion_micro carries v41 per ep001_014 ground truth evidence
    if archetype == "pet_companion_micro":
        return True
    return False


def resolve_active_character(
    beat: dict,
    stage_characters: list,
) -> str:
    """Determine which character_id is the FOCAL on-frame subject for this beat.

    Multi-character extension (OPD-147, this PR). Order of precedence:
        1. If beat declares `subject_actor: <character_id>`, use it (validated
           at load_beatsheet time to be present in stage_characters).
        2. Else fall back to `stage_characters[0]` (the protagonist).

    Pure-Python helper, no side effects. Single-character path (ep_001) always
    resolves to stage_characters[0] because no beat has subject_actor, so the
    behavior is identical to V1.

    Per docs/PEARL_ARCHITECT_BRIEF_EP002_CANDIDATE_ARCHETYPES.md §4.1.
    """
    subject_actor = beat.get("subject_actor")
    if subject_actor is not None and subject_actor in stage_characters:
        return subject_actor
    return stage_characters[0]


def derive_on_frame_for_character(
    cid: str,
    beat: dict,
    beat_character_block: dict | None,
    archetype: str,
    stage_characters: list,
    op_has_state: bool = False,
) -> bool:
    """Multi-character on_frame derivation (OPD-147 extension of H5).

    Augments derive_on_frame() with multi-character semantics:
        - For META_ARCHETYPES_SUPPRESSING_ALL_CHARACTERS (typographic_caption_card):
          every character is off_frame regardless of subject_type or operator.
        - For ARCHETYPES_REQUIRING_SUBJECT_ACTOR (secondary_character_face_close):
          the subject_actor is on_frame, every OTHER character is off_frame
          (POV-from-protagonist composition).
        - For all other archetypes, falls back to the V1 single-char derive_on_frame
          rule, which treats every stage_character as the focal subject. This
          matches ep_001's behavior exactly (one stage_character, applies the
          archetype's subject_type).

    Explicit operator override (beat_character_block['on_frame']) always wins.
    """
    # 1. Explicit operator override (highest priority).
    if beat_character_block and "on_frame" in beat_character_block:
        return bool(beat_character_block["on_frame"])

    # 2. META archetypes (OPD-148): no character on-frame ever.
    if archetype in META_ARCHETYPES_SUPPRESSING_ALL_CHARACTERS:
        return False

    # 3. subject_actor archetypes (OPD-147): only the named actor is on-frame.
    if archetype in ARCHETYPES_REQUIRING_SUBJECT_ACTOR:
        subject_actor = beat.get("subject_actor")
        return cid == subject_actor

    # 4. Default V1 single-char path — preserved verbatim for backwards compat.
    return derive_on_frame(beat_character_block, archetype, op_has_state=op_has_state)


def compute_panel_id(episode_id: str, beat_index: int) -> str:
    """H10 helper: panel_id from episode_id + 1-based zero-padded index."""
    # ep_001 → ep001_NNN
    ep_compact = episode_id.replace("_", "")
    return f"{ep_compact}_{beat_index + 1:03d}"


def compute_inherits_from(episode_id: str, beat_index: int) -> str | None:
    """H10: inherits_from = null on beat 1; else previous panel_id."""
    if beat_index == 0:
        return None
    return compute_panel_id(episode_id, beat_index - 1)


# ─────────────────────────────────────────────────────────────────────────────
# Inheritance engine
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class GeneratorState:
    """Cross-panel state carried through the generation loop."""

    # Sticky scene state (inherits across beats unless overridden)
    scene_id: str | None = None
    temporal: str | None = None
    light_rig_id: str | None = None

    # Sticky character state, per character_id
    character_state: dict = field(default_factory=dict)

    # Sticky prop state
    prop_state: dict = field(default_factory=dict)

    # Sticky relational fields
    shared_attention_anchor: str | None = None

    # Previous panel's archetype — drives "apply archetype defaults when
    # archetype changes" behavior.
    prev_archetype: str | None = None

    # Snapshot stack for props_reset / props_restore_from_scene_exit
    prop_snapshots: list = field(default_factory=list)

    def snapshot_props(self) -> None:
        self.prop_snapshots.append(copy.deepcopy(self.prop_state))

    def restore_props(self) -> None:
        if not self.prop_snapshots:
            raise GeneratorError(
                "props_restore_from_scene_exit called without prior props_reset snapshot"
            )
        self.prop_state = self.prop_snapshots.pop()


# ─────────────────────────────────────────────────────────────────────────────
# Per-beat panel-build
# ─────────────────────────────────────────────────────────────────────────────


def build_panel(
    beat: dict,
    beat_index: int,
    state: GeneratorState,
    beatsheet: dict,
    configs: dict,
) -> dict:
    """Build one panel from one beat. Mutates `state` in place.

    Returns a dict in canonical continuity_state shape (per
    docs/specs/MANGA_CONTINUITY_STATE_SPEC.md §1).
    """
    archetype = beat["archetype"]

    if (
        archetype not in SUPPORTED_ARCHETYPES
        and archetype in DECLARED_BUT_UNIMPLEMENTED_ARCHETYPES
    ):
        raise ArchetypeNotImplementedError(
            f"archetype {archetype!r} is declared in iyashikei.yaml but not "
            f"dispatched in V1 (no ep_001 evidence). Per operator instruction: "
            f"add dispatch when ep_002+ beatsheets surface need."
        )
    elif archetype not in SUPPORTED_ARCHETYPES:
        raise ArchetypeNotImplementedError(
            f"unknown archetype {archetype!r}; supported V1 archetypes: "
            f"{sorted(SUPPORTED_ARCHETYPES)}"
        )

    episode_id = beatsheet["episode_id"]
    stage_characters = beatsheet["stage_characters"]
    panel_id = compute_panel_id(episode_id, beat_index)
    inherits_from = compute_inherits_from(episode_id, beat_index)

    # ── Step 3a: scene overrides ──
    scene_block = beat.get("scene") or {}
    prev_scene_id = state.scene_id
    prev_temporal = state.temporal
    if "id" in scene_block:
        state.scene_id = scene_block["id"]
    if "temporal" in scene_block:
        state.temporal = scene_block["temporal"]
    # If operator pinned light_rig_id explicitly, use it; else derive (H1)
    if "light_rig_id" in scene_block:
        state.light_rig_id = scene_block["light_rig_id"]
    else:
        try:
            derived = derive_light_rig(
                state.scene_id,
                state.temporal,
                configs.get("scene_inventory"),
                configs.get("light_rig_library"),
            )
            if derived is not None:
                state.light_rig_id = derived
        except GeneratorError:
            # Defer; if no override exists this will surface in validator
            pass

    # ── Step 3b: prop overrides ──
    if beat.get("props_clear"):
        state.prop_state = {}
    elif beat.get("props_reset"):
        state.snapshot_props()
        state.prop_state = {}
        # Apply the beat's `props` block as the new prop_state
        for pid, pval in (beat.get("props") or {}).items():
            state.prop_state[pid] = pval
    elif beat.get("props_restore_from_scene_exit"):
        state.restore_props()
        # Apply this beat's additional props on top
        for pid, pval in (beat.get("props") or {}).items():
            state.prop_state[pid] = pval
    else:
        # Additive: append/transition
        for pid, pval in (beat.get("props") or {}).items():
            state.prop_state[pid] = pval

    # ── Step 3c: shared_attention_anchor ──
    # Anchor is mostly per-beat (B-cat). Sticky inheritance works in the
    # within-cluster cases (b14 inherits from b13). But anchor implicitly
    # clears on scene changes (b16) and on props_reset / props_clear.
    if "shared_attention_anchor" in beat:
        # Explicit operator authoring (including explicit null)
        state.shared_attention_anchor = beat["shared_attention_anchor"]
    elif beat.get("props_reset") or beat.get("props_clear") or (
        prev_scene_id is not None and state.scene_id != prev_scene_id
    ):
        # Scene change or prop reset → anchor is stale; clear
        state.shared_attention_anchor = None
    # else: inherit (already set on state from prev iteration)

    # ── Step 3d/e: per-character state ──
    # V1 ep_001 has a single stage_character (multi-character case is Phase 2).
    #
    # Per-character rules (refined from ground truth observation):
    #   1. If beat.character.<cid> is null (explicit suppression) → emit no
    #      character_state entry for cid. on_frame=false in relational_field.
    #   2. If operator authored real state fields (any of: pose_id,
    #      expression_dial, emotional, gaze, hand_state, breath_phase) → start
    #      from inherited cs (or empty dict), apply operator deltas, fill
    #      archetype defaults for unset fields, derive gaze if anchor changed.
    #   3. If operator ONLY authored relational fields (on_frame, role) and no
    #      state fields → inherit prev_cs as-is (no archetype default re-apply).
    #      If no prev_cs (or prev was empty) → emit no character_state entry.
    #   4. If operator authored nothing for cid → inherit prev_cs as-is.
    #
    # Archetype defaults are applied ONLY on the first beat the character
    # appears with real state. After that, fields stick via inheritance.
    char_block_per_beat = beat.get("character") or {}
    new_character_state: dict[str, Any] = {}
    suppressed_char_ids: set[str] = set()

    # Fields that count as "real character state" (versus relational)
    _STATE_FIELDS = {"pose_id", "expression_dial", "emotional", "gaze",
                     "gaze_direction", "hand_state", "breath_phase"}

    # OPD-148 META suppression: typographic_caption_card and similar
    # META cluster archetypes suppress all stage_characters globally —
    # the panel is purely typographic, no L2 cutout, no character_state.
    # This is checked BEFORE the per-character loop so it cleanly applies
    # even when operator authored explicit null for each character (e.g.
    # ep_002 b24).
    if archetype in META_ARCHETYPES_SUPPRESSING_ALL_CHARACTERS:
        suppressed_char_ids.update(stage_characters)
        # Skip the per-character state loop entirely; new_character_state
        # stays empty.
        state.character_state = new_character_state
    else:
        for cid in stage_characters:
            prev_cs = state.character_state.get(cid)
            beat_cs = char_block_per_beat.get(cid, ...)  # sentinel: missing

            if beat_cs is None:
                # Explicit null suppression
                suppressed_char_ids.add(cid)
                continue

            # Determine whether operator authored any state-fields for this cid
            op_has_state = (
                isinstance(beat_cs, dict)
                and any(k in beat_cs for k in _STATE_FIELDS)
            )
            op_authored_anything = isinstance(beat_cs, dict) and len(beat_cs) > 0

            # OPD-147 multi-character: for ARCHETYPES_REQUIRING_SUBJECT_ACTOR,
            # the protagonist is off-frame (POV-from-protagonist). If the
            # operator didn't author state for the protagonist, suppress them
            # (no character_state entry emitted) — matches ep_002 b17 / b22
            # where Mira is implied off-frame and only Dr. Morimoto carries
            # real state. The subject_actor character flows through the
            # normal path (cases below).
            if (
                archetype in ARCHETYPES_REQUIRING_SUBJECT_ACTOR
                and cid != beat.get("subject_actor")
                and not op_has_state
            ):
                suppressed_char_ids.add(cid)
                continue

            # Per OPD-142 / OPEN-1: ep001_016 has character_state={} despite the
            # operator setting on_frame=true (contradiction). The canonical
            # reading is "scene changed to flashback, character not in continuity
            # for new scene." Encode as: when SCENE CHANGED on this beat AND
            # archetype has null subject_type AND no state fields authored, suppress.
            archetype_has_no_subject = ARCHETYPE_SUBJECT_TYPE.get(archetype) is None
            scene_changed = (
                prev_scene_id is not None and state.scene_id != prev_scene_id
            )
            # Also suppress on episode-card archetype with props_clear: complete reset.
            is_episode_card = beat.get("props_clear", False) and archetype_has_no_subject
            if (
                (scene_changed and archetype_has_no_subject and not op_has_state)
                or is_episode_card
            ):
                suppressed_char_ids.add(cid)
                continue

            # Case 3 + 4: no state fields authored → strict inheritance
            if not op_has_state:
                if prev_cs is None or _is_empty_cs(prev_cs):
                    # No prev real state + no current state → no character_state entry
                    # (e.g. ep001_001 beat 1 with sparse_establishing_wide and
                    # operator authored only on_frame=false)
                    continue
                # Inherit prev_cs verbatim; apply pose_id archetype default if
                # archetype changed (per ep001_009 evidence). hand_state changes
                # only on transitions to hand-prescriptive archetypes.
                cs = copy.deepcopy(prev_cs)
                if archetype != "chest_breath_micro":
                    cs.pop("breath_phase", None)
                if (
                    state.prev_archetype is not None
                    and state.prev_archetype != archetype
                ):
                    default_pose = ARCHETYPE_DEFAULT_POSE_ID.get(archetype)
                    if default_pose:
                        cs["pose_id"] = default_pose
                    if archetype in HAND_PRESCRIPTIVE_ARCHETYPES:
                        default_hand = ARCHETYPE_DEFAULT_HAND_STATE.get(archetype)
                        if default_hand:
                            cs["hand_state"] = default_hand
                new_character_state[cid] = cs
                continue

            # Case 2: operator authored real state fields
            # Start from inherited cs (or empty if none)
            cs = copy.deepcopy(prev_cs) if (prev_cs and not _is_empty_cs(prev_cs)) else {}
            is_fresh_appearance = not cs  # no prev → archetype defaults will apply
            archetype_changed = (
                state.prev_archetype is not None
                and state.prev_archetype != archetype
            )

            # Apply operator deltas (excluding relational fields)
            for k, v in beat_cs.items():
                if k in ("on_frame", "role"):
                    continue  # propagate to relational_field instead
                if k == "gaze":
                    cs["gaze_direction"] = v
                else:
                    cs[k] = v

            # Always inject the design hash (A-cat, constant for V4 launch)
            cs["character_design_hash"] = CHARACTER_DESIGN_HASH_PENDING

            # Archetype defaults — semantics per ground-truth evidence:
            #   pose_id: applies on (a) fresh appearance, OR (b) archetype changed.
            #     Rationale: pose_id is the visual framing — when archetype
            #     changes, the framing changes too. Ground truth ep001_009 shows
            #     pose_id reverts to tea_beat default even though prev was
            #     dappled_light_hand with hand_only_table.
            #   hand_state: applies on (a) fresh appearance, OR (b) archetype
            #     changed AND the new archetype is hand-prescriptive
            #     (tea_beat_close_up, chest_breath_micro, dappled_light_hand —
            #     these have a semantically required hand pose). For other
            #     archetypes, hand_state inherits. Ground truth ep001_003
            #     inherits wrapping_cup from b02 even though character_quiet_face
            #     archetype's default would be relaxed_open.
            if is_fresh_appearance or archetype_changed:
                default_pose = ARCHETYPE_DEFAULT_POSE_ID.get(archetype)
                if default_pose and "pose_id" not in beat_cs:
                    cs["pose_id"] = default_pose
            if is_fresh_appearance or (
                archetype_changed and archetype in HAND_PRESCRIPTIVE_ARCHETYPES
            ):
                default_hand = ARCHETYPE_DEFAULT_HAND_STATE.get(archetype)
                if default_hand and "hand_state" not in beat_cs:
                    cs["hand_state"] = default_hand

            # D-cat: breath_phase ONLY for chest_breath_micro
            if archetype != "chest_breath_micro":
                cs.pop("breath_phase", None)

            # H2 gaze derivation: only when operator didn't author gaze AND
            # one of these conditions holds:
            #   (a) inherited gaze_direction was `at_named_object_X` AND
            #       X != current anchor (stale-anchor refresh)
            #   (b) anchor is a NEWLY-INTRODUCED prop on this beat
            #       (operator introducing prop = attentional shift)
            if "gaze" not in beat_cs:
                inherited_gaze = cs.get("gaze_direction")
                anchor = state.shared_attention_anchor
                if anchor and anchor in (state.prop_state or {}):
                    target_gaze = f"at_named_object_{anchor}"
                    prev_props_before_this_beat = state.__dict__.get("_prev_prop_state", {})
                    anchor_is_newly_introduced = anchor not in prev_props_before_this_beat

                    if isinstance(inherited_gaze, str) and inherited_gaze.startswith("at_named_object_"):
                        if inherited_gaze != target_gaze:
                            # (a) anchor changed; refresh
                            cs["gaze_direction"] = target_gaze
                    elif anchor_is_newly_introduced:
                        # (b) new prop introduced + set as anchor; derive
                        cs["gaze_direction"] = target_gaze

            new_character_state[cid] = cs

        state.character_state = new_character_state

    # ── Step 3f: assemble scene_state ──
    scene_state: dict[str, Any] = {}
    if state.scene_id is not None:
        scene_state["scene_id"] = state.scene_id
    if state.temporal is not None:
        scene_state["temporal"] = state.temporal
    if state.light_rig_id is not None:
        scene_state["light_rig_id"] = state.light_rig_id
    if should_emit_weather_anchor(beat_index):
        wa = (beatsheet.get("defaults") or {}).get("weather_anchor")
        if wa:
            scene_state["weather_anchor"] = wa

    # ── Step 3g: relational_field ──
    # Per-stage_character entry in active_entities (multi-character extension
    # per OPD-147). For single-character episodes (ep_001) the loop runs once
    # exactly as in V1 — behavior is byte-identical. For multi-character beats
    # (ep_002+) each stage_character gets its own active_entities entry with
    # its own on_frame state derived from archetype + subject_actor binding.
    active_entities = []
    for cid in stage_characters:
        beat_cs = char_block_per_beat.get(cid, ...)
        op_has_state_for_cid = (
            isinstance(beat_cs, dict)
            and any(k in beat_cs for k in _STATE_FIELDS)
        )
        explicit_on_frame = None
        if isinstance(beat_cs, dict) and "on_frame" in beat_cs:
            explicit_on_frame = bool(beat_cs["on_frame"])
        # Per OPD-142: when scene-changed suppression fires (ep001_016
        # flashback), reconcile on_frame=false even if operator says true.
        # For other suppression cases (episode card + META archetypes), also
        # force false.
        if cid in suppressed_char_ids:
            on_frame = False
        elif explicit_on_frame is not None:
            on_frame = explicit_on_frame
        else:
            # OPD-147 multi-character extension of H5: route through
            # derive_on_frame_for_character() which handles META archetypes
            # (typographic_caption_card) and subject_actor archetypes
            # (secondary_character_face_close) BEFORE falling back to V1
            # single-character derive_on_frame(). For ep_001 archetypes the
            # fall-through produces identical output to V1.
            on_frame = derive_on_frame_for_character(
                cid=cid,
                beat=beat,
                beat_character_block=beat_cs if isinstance(beat_cs, dict) else None,
                archetype=archetype,
                stage_characters=stage_characters,
                op_has_state=op_has_state_for_cid,
            )
        # role: H6
        if isinstance(beat_cs, dict) and "role" in beat_cs:
            role = beat_cs["role"]
        else:
            role = derive_role(on_frame)
        active_entities.append({"id": cid, "on_frame": on_frame, "role": role})

    # Compute tension vector vs prev panel.
    # The PROTAGONIST (stage_characters[0]) drives the panel's emotional
    # tension vector regardless of which character is on-frame. Rationale:
    # the iyashikei tension arc is the protagonist's interior journey; even
    # when a secondary character is on-frame (e.g. ep_002 b17 Dr. Morimoto
    # CU), the page's emotional reading is "where Mira is at right now."
    primary_cid = stage_characters[0]
    curr_cs = state.character_state.get(primary_cid)
    curr_dial = curr_cs.get("expression_dial") if curr_cs else None
    prev_dial = state.__dict__.setdefault("_prev_panel_dial", {}).get(primary_cid)
    magnitude_delta = derive_magnitude_delta(curr_dial, prev_dial)
    tension_override = beat.get("tension_override")
    direction = derive_tension_direction(curr_dial, prev_dial, tension_override)
    # Cache update for next iteration. Multi-character extension semantics:
    #   - When the protagonist HAS a current dial, update cache to that
    #     value (matches V1 single-char behavior).
    #   - When the protagonist has NO current dial AND was suppressed via
    #     OPD-142 scene-change (flashback) or props_clear (episode card),
    #     reset cache to None. Preserves V1 ep_001 round-trip: ep001_016
    #     scene-jump to flashback resets Mira's dial cache → ep001_017 has
    #     no prev_dial reference (matches ground-truth magnitude_delta=0.0).
    #   - When the protagonist has NO current dial for any OTHER reason
    #     (multi-character POV via secondary_character_face_close,
    #     seasonal_anchor_object with Mira implied off-frame, etc.):
    #     PRESERVE cache so the next protagonist-on-frame beat reads against
    #     the last known dial. This is the multi-character extension's key
    #     improvement: the protagonist's emotional inheritance chain
    #     continues across off-frame beats. Without this, ep_002 b19 (Mira
    #     dial=0.5 after b16 dial=0.6 through b17/b18 off-frame) would lose
    #     its -0.1 reference.
    archetype_has_no_subject = ARCHETYPE_SUBJECT_TYPE.get(archetype) is None
    scene_changed = (
        prev_scene_id is not None and state.scene_id != prev_scene_id
    )
    protagonist_reset_by_scene_change = (
        primary_cid in suppressed_char_ids
        and scene_changed
        and archetype_has_no_subject
    )
    protagonist_reset_by_episode_card = (
        beat.get("props_clear", False) and archetype_has_no_subject
    )
    if curr_dial is not None:
        state.__dict__["_prev_panel_dial"][primary_cid] = curr_dial
    elif protagonist_reset_by_scene_change or protagonist_reset_by_episode_card:
        # V1-equivalent path: reset cache to None (matches ep_001 b16/b35).
        state.__dict__["_prev_panel_dial"][primary_cid] = None
    # else: preserve cache (multi-character POV / object-only beats / META
    # archetype beats; protagonist's dial inheritance chain continues).

    relational_field: dict[str, Any] = {
        "active_entities": active_entities,
        "shared_attention_anchor": state.shared_attention_anchor,
    }
    # implied_partner_position: emit only on beats 1-2 per ground-truth
    # evidence (ep001_001 + ep001_002 carry it; rest omit). For multi-char
    # episodes this becomes a real position; V1 emits null for solo only on
    # opening pair.
    if beat_index < 2:
        relational_field["implied_partner_position"] = None
    relational_field["emotional_tension_vector"] = {
        "direction": direction,
        "magnitude_delta_from_prev": magnitude_delta,
    }

    # ── Step 3h: beat_type resolution ──
    # Operator may override; else null on beat 1 (no inheritance), else inherit
    # the archetype's default. ep_001 ground truth: beat 1 = "spatial" per
    # operator override; otherwise per beat.
    beat_type = beat.get("beat_type")
    if beat_type is None:
        # Fall back to archetype primary beat_type if known, else "micro"
        beat_type = _archetype_primary_beat_type(archetype)

    # ── Step 3i: continuity_invariants (H9) ──
    continuity_invariants = _emit_continuity_invariants(
        beat=beat,
        beat_index=beat_index,
        archetype=archetype,
        beat_type=beat_type,
        prev_scene_id=prev_scene_id,
        prev_temporal=prev_temporal,
        scene_state=scene_state,
        prop_state=state.prop_state,
        prev_prop_state=state.__dict__.setdefault("_prev_prop_state", {}),
        magnitude_delta=magnitude_delta,
        curr_dial=curr_dial,
        prev_dial=prev_dial,
    )
    # Stash for next beat's prop transitions
    state.__dict__["_prev_prop_state"] = copy.deepcopy(state.prop_state)

    # ── Step 3j: assemble panel dict ──
    panel: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "panel_id": panel_id,
        "inherits_from": inherits_from,
        "beat_type": beat_type,
        "archetype": archetype,
        "scene_state": scene_state,
        "character_state": _strip_empty_character_state(state.character_state),
        "prop_state": dict(state.prop_state),
        "continuity_invariants": continuity_invariants,
        "relational_field": relational_field,
    }

    # H8: v41_per_axis_edge_resolved on face-only archetypes (after activation onset)
    if should_emit_v41_boilerplate(archetype, beat_index):
        panel["v41_per_axis_edge_resolved"] = True
        # Append boilerplate to continuity_invariants if not already there
        if V41_FACE_BOILERPLATE not in continuity_invariants:
            continuity_invariants.append(V41_FACE_BOILERPLATE)

    # OPD-148: typographic_caption_card emits caption_text + caption_style +
    # render_directive=typographic_only, suppresses scene_state.light_rig_id
    # (no L0 light rig — the lettering pipeline renders the page directly).
    # character_state is already empty (META suppression upstream).
    if archetype == "typographic_caption_card":
        panel["caption_style"] = beat["caption_style"]
        panel["caption_text"] = beat["caption_text"]
        panel["render_directive"] = "typographic_only"
        # Drop light_rig_id from scene_state — caption-card has no L0 lighting.
        panel.get("scene_state", {}).pop("light_rig_id", None)

    # OPD-147: secondary_character_face_close emits subject_actor so downstream
    # prompt compiler / PuLID can bind the right reference sheet. The active
    # subject is the parametrized character, NOT stage_characters[0].
    if archetype in ARCHETYPES_REQUIRING_SUBJECT_ACTOR:
        panel["subject_actor"] = beat["subject_actor"]

    # Track archetype for next iteration's "apply archetype defaults?" check
    state.prev_archetype = archetype

    return panel


def _is_empty_cs(cs: dict | None) -> bool:
    """A character_state is 'empty' if it has no fields besides the design hash."""
    if not cs:
        return True
    keys = set(cs.keys()) - {"character_design_hash"}
    return not keys


def _strip_empty_character_state(character_state: dict) -> dict:
    """Strip out character_state entries that hold no real data."""
    return {cid: cs for cid, cs in character_state.items() if not _is_empty_cs(cs)}


def _archetype_primary_beat_type(archetype: str) -> str:
    """Archetype primary beat_type (per config/manga/panel_templates/iyashikei.yaml).

    Source-of-truth is the panel_template YAML, but for V1 we hard-code the
    12 supported archetypes to avoid YAML loading on the dispatch hot path.
    Operator override takes precedence; this is purely the fallback.
    """
    return {
        "sparse_establishing_wide": "spatial",
        "tea_beat_close_up": "micro",
        "character_quiet_face": "micro",
        "chest_breath_micro": "micro",
        "character_face_micro_tension": "micro",
        "hand_table_micro": "micro",
        "dappled_light_hand": "spatial",
        "pet_companion_micro": "micro",
        "seasonal_anchor_object": "spatial",
        "kettle_steam_macro": "spatial",
        "long_drop_decompression": "long_drop",
        "pendulation_pair_visual_rhyme": "micro",
        # OPD-147: secondary character CU is micro (per iyashikei.yaml primary).
        "secondary_character_face_close": "micro",
        # OPD-148: caption-card mid-episode strip is micro; end-episode card
        # is standard (operator overrides per beat).
        "typographic_caption_card": "micro",
        # ep_002-surfaced primaries from iyashikei.yaml.
        "walking_in_thought_medium": "spatial",
        "miyazaki_ma_pause": "miyazaki_ma",
        "window_light_threshold": "spatial",
    }.get(archetype, "micro")


def _emit_continuity_invariants(
    beat: dict,
    beat_index: int,
    archetype: str,
    beat_type: str,
    prev_scene_id: str | None,
    prev_temporal: str | None,
    scene_state: dict,
    prop_state: dict,
    prev_prop_state: dict,
    magnitude_delta: float,
    curr_dial: float | None,
    prev_dial: float | None,
) -> list[str]:
    """H9: auto-commentary + operator pass-throughs.

    The generator emits formatted strings for: scene transitions, prop
    introductions, prop state transitions, dial deltas on micro, light rig
    transitions, V4.1 face-archetype boilerplate. Operator `intent` and
    `notes` strings are appended after.

    Output order (deliberate, deterministic):
        1. Operator `intent` (passed verbatim from beatsheet)
        2. Auto-derived prop introductions / transitions
        3. Auto-derived scene / temporal transitions
        4. Auto-derived dial deltas
        5. Operator `notes` (passed verbatim from beatsheet)
    """
    invariants: list[str] = []

    # 1. Operator intent (passed through)
    if beat.get("intent"):
        invariants.append(beat["intent"])

    # 2. Prop introductions and transitions
    for pid, pval in prop_state.items():
        if pid not in prev_prop_state:
            invariants.append(
                f"{pid} introduced this panel; not in prev prop_state"
            )
        elif prev_prop_state[pid] != pval:
            invariants.append(
                f"{pid} transitions {prev_prop_state[pid]} -> {pval} (adjacent in enum)"
            )

    # 3. Scene transitions
    if beat_index > 0:
        curr_scene = scene_state.get("scene_id")
        if prev_scene_id is not None and curr_scene != prev_scene_id:
            allowed = beat_type in SCENE_JUMP_BEAT_TYPES
            verdict = "allowed" if allowed else "FORBIDDEN"
            invariants.append(
                f"scene jump {prev_scene_id} -> {curr_scene} on {beat_type} beat ({verdict})"
            )
        curr_temp = scene_state.get("temporal")
        if (
            prev_temporal is not None
            and curr_temp is not None
            and curr_temp != prev_temporal
        ):
            invariants.append(
                f"light_rig advances {prev_temporal} -> {curr_temp} (next-in-cycle)"
            )

    # 4. Dial deltas on micro
    if (
        beat_type == "micro"
        and curr_dial is not None
        and prev_dial is not None
        and magnitude_delta != 0.0
    ):
        sign = "+" if magnitude_delta > 0 else "-"
        invariants.append(
            f"dial {sign}{abs(magnitude_delta):.1f} from prev "
            f"({prev_dial} -> {curr_dial}) within micro bound 0.3"
        )

    # 5. Operator notes (passed through)
    if beat.get("notes"):
        invariants.append(beat["notes"])

    return invariants


# ─────────────────────────────────────────────────────────────────────────────
# Emitter
# ─────────────────────────────────────────────────────────────────────────────


def emit_panel_yaml(panel: dict, out_path: Path) -> None:
    """Write a panel dict as YAML to `out_path`.

    Uses safe_dump with default_flow_style=False to match ground-truth block
    style. Preserves field order via the dict's insertion order (Python 3.7+).
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    yaml_str = yaml.safe_dump(
        panel,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
        width=88,
    )
    out_path.write_text(yaml_str)


# ─────────────────────────────────────────────────────────────────────────────
# Top-level pipeline
# ─────────────────────────────────────────────────────────────────────────────


def load_config_inputs(beatsheet: dict, repo_root: Path) -> dict:
    """Load the runtime config files declared in the beatsheet header.

    Path resolution: relative to the repo root.
    Returns a dict with loaded YAML for each config source the generator needs.
    """
    def _load(rel_path: str | None) -> dict | None:
        if not rel_path:
            return None
        full = repo_root / rel_path
        if not full.is_file():
            return None
        try:
            return yaml.safe_load(full.read_text())
        except yaml.YAMLError:
            return None

    return {
        "series_profile": _load(beatsheet.get("series_profile_path")),
        "scene_inventory": _load(beatsheet.get("scene_inventory_path")),
        "style_state": _load(beatsheet.get("style_state_path")),
        "panel_template": _load(beatsheet.get("panel_template_path")),
        "light_rig_library": _load(beatsheet.get("light_rig_library")),
    }


def generate_continuity_state(
    beatsheet: dict,
    configs: dict,
) -> list[dict]:
    """Run the full pipeline. Returns a list of N panel dicts."""
    state = GeneratorState()
    # Apply defaults to seed state
    defaults = beatsheet.get("defaults") or {}
    if "scene_id" in defaults:
        state.scene_id = defaults["scene_id"]
    if "temporal" in defaults:
        state.temporal = defaults["temporal"]
    if "light_rig_id" in defaults:
        state.light_rig_id = defaults["light_rig_id"]
    if "prop_state" in defaults:
        state.prop_state = dict(defaults["prop_state"])

    # Pre-derive opening light_rig if not pinned
    if state.light_rig_id is None and state.scene_id and state.temporal:
        try:
            state.light_rig_id = derive_light_rig(
                state.scene_id, state.temporal,
                configs.get("scene_inventory"),
                configs.get("light_rig_library"),
            )
        except GeneratorError:
            pass

    panels = []
    for idx, beat in enumerate(beatsheet["beats"]):
        try:
            panel = build_panel(beat, idx, state, beatsheet, configs)
        except (BeatsheetValidationError, GeneratorError, ArchetypeNotImplementedError):
            raise
        except Exception as e:
            raise GeneratorError(
                f"beats[{idx}] (beat_id={beat.get('beat_id')!r}, archetype={beat.get('archetype')!r}): "
                f"unexpected error: {e}"
            ) from e
        panels.append(panel)

    return panels


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────


def _resolve_repo_root() -> Path:
    """Repo root is two levels up from this script (scripts/manga/foo.py)."""
    return Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Generate per-panel continuity_state YAMLs from a beatsheet.",
    )
    ap.add_argument("--beatsheet", type=Path, required=True,
                    help="Path to the beatsheet YAML (per MANGA_BEATSHEET_SCHEMA.yaml)")
    ap.add_argument("--output-dir", type=Path, required=True,
                    help="Output directory for per-panel YAMLs")
    ap.add_argument("--episode-id", type=str, default=None,
                    help="Override episode_id from beatsheet (rare)")
    ap.add_argument("--repo-root", type=Path, default=None,
                    help="Repo root for resolving config paths (default: derived from script location)")
    ap.add_argument("--dry-run", action="store_true",
                    help="Validate beatsheet + generate panels, but don't write to disk")
    ap.add_argument("--validate-only", action="store_true",
                    help="Validate beatsheet schema; skip generation")
    args = ap.parse_args(argv)

    repo_root = args.repo_root or _resolve_repo_root()

    try:
        beatsheet = load_beatsheet(args.beatsheet)
    except BeatsheetValidationError as e:
        print(f"BEATSHEET INVALID: {e}", file=sys.stderr)
        return 2

    if args.episode_id:
        beatsheet["episode_id"] = args.episode_id

    print(f"[generator] beatsheet loaded: {args.beatsheet}", file=sys.stderr)
    print(f"[generator]   episode_id={beatsheet['episode_id']}", file=sys.stderr)
    print(f"[generator]   beats={len(beatsheet['beats'])}", file=sys.stderr)
    print(f"[generator]   stage_characters={beatsheet['stage_characters']}", file=sys.stderr)

    if args.validate_only:
        print("[generator] schema validation OK; --validate-only set, exiting", file=sys.stderr)
        return 0

    configs = load_config_inputs(beatsheet, repo_root)
    missing = [k for k, v in configs.items() if v is None]
    if missing:
        print(f"[generator] WARNING: missing config files: {missing}", file=sys.stderr)

    try:
        panels = generate_continuity_state(beatsheet, configs)
    except (ArchetypeNotImplementedError, GeneratorError) as e:
        print(f"GENERATION FAILED: {e}", file=sys.stderr)
        return 3

    print(f"[generator] generated {len(panels)} panels", file=sys.stderr)

    if args.dry_run:
        print("[generator] --dry-run set; not writing to disk", file=sys.stderr)
        return 0

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for panel in panels:
        out_path = args.output_dir / f"{panel['panel_id']}.yaml"
        emit_panel_yaml(panel, out_path)

    print(f"[generator] wrote {len(panels)} YAMLs to {args.output_dir}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
