"""Verify angle_registry.yaml v2: 91 angles + parent_universal inheritance + journey scaffolds.

Source spec: docs/specs/ANGLE_REGISTRY_SSOT_V2_SPEC.md
Catalog source: docs/plans/ANGLE_CATALOG_V2_2026-05-20.md
"""

from __future__ import annotations

import textwrap
from pathlib import Path
from typing import Any

import pytest

from phoenix_v4.planning.angle_resolver import (
    AngleChainDepthError,
    AngleCycleError,
    DeprecatedAngleError,
    MAX_CHAIN_DEPTH,
    load_angle_registry,
    load_canonical_topic_ids,
    resolve_angle_with_inheritance,
)

# Canonical sets used by the catalog v2 + spec.
VALID_FRAMING_MODES = {"debunk", "framework", "reveal", "leverage"}
VALID_ANALOGY_LENSES = {
    "fractal",
    "dimensional_revelation",
    "doorway",
    "machine_slowly_revealed",
    "mythic_recurrence",
    "progressive_compression",
    "book_is_the_angle",
}
CANONICAL_PHASE_ORDER = (
    "definition",
    "pattern_recognition",
    "identity_implications",
    "civilizational_spiritual",
    "transcendence_reintegration",
)
LEGACY_V1_ANGLES = {"WRONG_PROBLEM", "MAP_PROMISE", "HIDDEN_TRUTH", "ONE_LEVER"}
EXPECTED_TOTAL_NAMED = 91  # 20 universal + 71 topic-specific (legacy 4 excluded from this count)
EXPECTED_UNIVERSAL_COUNT = 20
EXPECTED_TOPIC_SPECIFIC_COUNT = 71


@pytest.fixture(scope="module")
def registry() -> dict[str, Any]:
    """Live SSOT registry (config/angles/angle_registry.yaml)."""
    reg = load_angle_registry()
    assert reg, "angle_registry.yaml failed to load"
    return reg


@pytest.fixture(scope="module")
def angles(registry: dict[str, Any]) -> dict[str, Any]:
    return registry.get("angles") or {}


def _is_universal(entry: dict) -> bool:
    """Universal = no parent_universal AND not deprecated."""
    return "parent_universal" not in entry and not entry.get("deprecated")


def _is_topic_specific(entry: dict) -> bool:
    return "parent_universal" in entry


def _is_deprecated(entry: dict) -> bool:
    return bool(entry.get("deprecated"))


# ─── Schema sanity ──────────────────────────────────────────────────────────


def test_schema_version_is_2(registry):
    assert registry.get("schema_version") == 2, "schema_version must be 2"


def test_authority_pointer_present(registry):
    assert registry.get("authority") == "docs/specs/ANGLE_REGISTRY_SSOT_V2_SPEC.md"


def test_total_named_angle_count_is_91(angles):
    """20 universal + 71 topic-specific = 91 named angles (excluding legacy-deprecated)."""
    universal_count = sum(1 for e in angles.values() if _is_universal(e))
    topic_count = sum(1 for e in angles.values() if _is_topic_specific(e))
    deprecated_count = sum(1 for e in angles.values() if _is_deprecated(e))
    assert universal_count == EXPECTED_UNIVERSAL_COUNT, f"expected 20 universal, got {universal_count}"
    assert topic_count == EXPECTED_TOPIC_SPECIFIC_COUNT, f"expected 71 topic-specific, got {topic_count}"
    assert (universal_count + topic_count) == EXPECTED_TOTAL_NAMED
    assert deprecated_count == 4, f"expected 4 legacy deprecated, got {deprecated_count}"


def test_all_91_angles_load_without_error(angles, registry):
    """Every non-deprecated angle resolves cleanly via the inheritance helper."""
    for aid, entry in angles.items():
        if _is_deprecated(entry):
            continue
        merged = resolve_angle_with_inheritance(aid, registry)
        assert merged, f"{aid} did not resolve"
        assert "_resolution_provenance" in merged


# ─── parent_universal validity ──────────────────────────────────────────────


def test_topic_specific_parent_universal_pointers_target_known_angles(angles):
    """parent_universal must point at an existing angle_id (universal OR another
    topic-specific — the catalog v2 has 2-level chains like
    LOYAL_ADAPTATION → PROTECTIVE_ALARM → USEFUL_SIGNAL).
    The 'final ancestor is a universal' invariant is checked separately."""
    for aid, entry in angles.items():
        if not _is_topic_specific(entry):
            continue
        parent = entry["parent_universal"]
        assert parent in angles, (
            f"{aid}.parent_universal={parent!r} is not declared anywhere in registry"
        )


def test_topic_specific_angles_resolve_to_a_valid_universal(angles, registry):
    """Walk the parent chain — final ancestor must be in the universal set."""
    universal_ids = {aid for aid, e in angles.items() if _is_universal(e)}
    for aid, entry in angles.items():
        if not _is_topic_specific(entry):
            continue
        merged = resolve_angle_with_inheritance(aid, registry)
        chain = merged["_resolution_provenance"]["parent_chain"]
        root_ancestor = chain[-1]  # chain is leaf → root
        assert root_ancestor in universal_ids, (
            f"{aid} parent chain {chain} ends at {root_ancestor} which is not a universal"
        )


# ─── Inheritance behavior ──────────────────────────────────────────────────


def test_leaf_inherits_structural_fields_from_parent(registry):
    """PROTECTIVE_ALARM picks up framing_mode=reveal from USEFUL_SIGNAL without restating it."""
    merged = resolve_angle_with_inheritance("PROTECTIVE_ALARM", registry)
    assert merged["framing_mode"] == "reveal", "framing_mode must inherit from USEFUL_SIGNAL"
    assert merged["arc_variant"] == "ARC_STANDARD_A_v6"
    assert merged["chapter_1_role_bias"] == "destabilization"
    assert merged["integration_reinforcement_type"] == "revelation"
    assert merged["parent_universal"] == "USEFUL_SIGNAL"
    # Display fields are leaf-defined.
    assert merged["display_name"] == "The Protective Alarm"
    assert merged["core_frame"].startswith("Anxiety as legitimate alarm")
    prov = merged["_resolution_provenance"]
    assert prov["chain_depth"] == 1
    assert "framing_mode" in prov["inherited_fields"]
    # 12-shape flagship (2026-07-07): PROTECTIVE_ALARM carries its own
    # journey.layer_progression (11 per-chapter callback levels), so journey
    # is a leaf override now; analogy_lens still deep-merges from the parent.
    assert "journey" in prov["leaf_overrides"]


def test_leaf_inherits_journey_block_from_parent(registry):
    """Topic-specific angle deep-merges journey: analogy_lens inherits from the
    universal while the leaf's 11-level flagship ladder overrides the 5-layer
    default (12-shape ladder extension 2026-07-07)."""
    merged = resolve_angle_with_inheritance("PROTECTIVE_ALARM", registry)
    journey = merged.get("journey")
    assert isinstance(journey, dict), "journey block must be present (merged)"
    assert journey.get("analogy_lens") == "progressive_compression"
    layers = journey.get("layer_progression") or []
    assert len(layers) == 11
    assert [row["chapter_range"] for row in layers] == [[c, c] for c in range(2, 13)]


def test_leaf_field_overrides_inherited_value(angles, registry):
    """If a leaf restates a structural field, the override wins; provenance records it."""
    # Synthesize an override test via a hand-built mini registry.
    mini = {
        "angles": {
            "PARENT": {
                "arc_variant": "ARC_PARENT",
                "framing_mode": "debunk",
                "chapter_1_role_bias": "destabilization",
                "integration_reinforcement_type": "revelation",
                "journey": {
                    "analogy_lens": "doorway",
                    "core_mantras": ["parent mantra"],
                    "layer_progression": [
                        {"layer": i, "phase": p, "chapter_range": [1, 2], "assertion": "TODO"}
                        for i, p in enumerate(CANONICAL_PHASE_ORDER, start=1)
                    ],
                },
            },
            "CHILD": {
                "parent_universal": "PARENT",
                "framing_mode": "reveal",  # override
                "display_name": "Child",
                "core_frame": "child core",
                "use_when": "child use",
            },
        }
    }
    merged = resolve_angle_with_inheritance("CHILD", mini)
    assert merged["framing_mode"] == "reveal", "leaf override must win"
    assert merged["arc_variant"] == "ARC_PARENT", "non-overridden field must inherit"
    prov = merged["_resolution_provenance"]
    assert "framing_mode" in prov["leaf_overrides"]
    # display_name is leaf-only and must not be reported as override.
    assert "display_name" not in prov["leaf_overrides"]


def test_missing_journey_field_falls_through_to_parent():
    """Leaf with no journey block inherits the entire parent journey block."""
    mini = {
        "angles": {
            "P": {
                "arc_variant": "ARC_P",
                "framing_mode": "reveal",
                "chapter_1_role_bias": "destabilization",
                "integration_reinforcement_type": "revelation",
                "journey": {
                    "analogy_lens": "fractal",
                    "core_mantras": ["P mantra"],
                    "layer_progression": [],
                },
            },
            "C": {
                "parent_universal": "P",
                "display_name": "Child",
                "core_frame": "x",
                "use_when": "x",
            },
        }
    }
    merged = resolve_angle_with_inheritance("C", mini)
    assert merged["journey"]["analogy_lens"] == "fractal"
    assert merged["journey"]["core_mantras"] == ["P mantra"]


def test_parent_chain_cycle_raises():
    mini = {
        "angles": {
            "A": {"parent_universal": "B", "display_name": "A", "core_frame": "x", "use_when": "x"},
            "B": {"parent_universal": "A", "display_name": "B", "core_frame": "x", "use_when": "x"},
        }
    }
    with pytest.raises(AngleCycleError):
        resolve_angle_with_inheritance("A", mini)


# ─── Deprecation contract ──────────────────────────────────────────────────


def test_all_4_legacy_angles_remain_in_registry(angles):
    for legacy in LEGACY_V1_ANGLES:
        assert legacy in angles, f"legacy v1 angle {legacy} must remain (soft-deprecated)"
        assert _is_deprecated(angles[legacy]), f"{legacy} must carry deprecated: true"


def test_deprecated_angles_carry_required_fields(angles):
    for aid, entry in angles.items():
        if not _is_deprecated(entry):
            continue
        assert "successor_angle_id" in entry, f"{aid} missing successor_angle_id"
        assert entry["successor_angle_id"] in angles, (
            f"{aid}.successor_angle_id={entry['successor_angle_id']!r} not in registry"
        )
        successor_entry = angles[entry["successor_angle_id"]]
        assert not _is_deprecated(successor_entry), (
            f"{aid} successor must be non-deprecated; "
            f"{entry['successor_angle_id']} is itself deprecated"
        )
        assert "deprecation_note" in entry, f"{aid} missing deprecation_note"


def test_deprecated_angle_raises_without_allow_legacy(registry):
    with pytest.raises(DeprecatedAngleError):
        resolve_angle_with_inheritance("WRONG_PROBLEM", registry, allow_legacy=False)


def test_deprecated_angle_resolves_with_allow_legacy(registry):
    merged = resolve_angle_with_inheritance("WRONG_PROBLEM", registry, allow_legacy=True)
    assert merged["framing_mode"] == "debunk"
    assert merged["_resolution_provenance"]["is_deprecated"] is True
    assert merged["_resolution_provenance"]["successor_angle_id"] == "SILENT_VERDICT"


def test_legacy_to_v2_migration_pointers_match_catalog(angles):
    """Catalog v2 §6 mapping: WRONG_PROBLEM→SILENT_VERDICT, MAP_PROMISE→BORROWED_COORDINATES,
    HIDDEN_TRUTH→USEFUL_SIGNAL, ONE_LEVER→ENGINE."""
    expected = {
        "WRONG_PROBLEM": "SILENT_VERDICT",
        "MAP_PROMISE": "BORROWED_COORDINATES",
        "HIDDEN_TRUTH": "USEFUL_SIGNAL",
        "ONE_LEVER": "ENGINE",
    }
    for legacy, successor in expected.items():
        assert angles[legacy]["successor_angle_id"] == successor


# ─── Universal-angle structural integrity ──────────────────────────────────


def test_each_universal_declares_valid_framing_mode(angles):
    for aid, entry in angles.items():
        if not _is_universal(entry):
            continue
        fm = entry.get("framing_mode")
        assert fm in VALID_FRAMING_MODES, (
            f"{aid}.framing_mode={fm!r} not in {VALID_FRAMING_MODES}"
        )


def test_each_universal_declares_analogy_lens_from_7(angles):
    for aid, entry in angles.items():
        if not _is_universal(entry):
            continue
        lens = entry.get("journey", {}).get("analogy_lens")
        assert lens in VALID_ANALOGY_LENSES, (
            f"{aid}.journey.analogy_lens={lens!r} not in 7-valid set {VALID_ANALOGY_LENSES}"
        )


def test_each_universal_has_5_layer_progression_in_canonical_phase_order(angles):
    for aid, entry in angles.items():
        if not _is_universal(entry):
            continue
        layers = entry.get("journey", {}).get("layer_progression") or []
        assert len(layers) == 5, f"{aid} layer_progression has {len(layers)} entries (expected 5)"
        phases = [layer.get("phase") for layer in layers]
        assert tuple(phases) == CANONICAL_PHASE_ORDER, (
            f"{aid} phase order {phases} != canonical {CANONICAL_PHASE_ORDER}"
        )
        nums = [layer.get("layer") for layer in layers]
        assert nums == [1, 2, 3, 4, 5], f"{aid} layer numbers {nums} != [1..5]"


def test_each_universal_has_named_object_by_topic_block(angles):
    """Universals declare per-topic named_object slots (null TODO until Pearl_Editor authors)."""
    for aid, entry in angles.items():
        if not _is_universal(entry):
            continue
        named = entry.get("journey", {}).get("named_object_by_topic")
        assert isinstance(named, dict), f"{aid} missing journey.named_object_by_topic"
        assert len(named) > 0, f"{aid} journey.named_object_by_topic is empty"


# ─── catalog_planner_resolution ────────────────────────────────────────────


def test_catalog_planner_resolution_version_is_2(registry):
    res = registry.get("catalog_planner_resolution") or {}
    assert res.get("version") == 2


def test_catalog_planner_topic_angle_map_targets_non_deprecated_angles(registry, angles):
    res = registry.get("catalog_planner_resolution") or {}
    tmap = res.get("topic_angle_map") or {}
    assert tmap, "topic_angle_map must not be empty"
    for topic_id, angle_id in tmap.items():
        assert angle_id in angles, f"topic_angle_map[{topic_id!r}]={angle_id!r} not declared"
        assert not _is_deprecated(angles[angle_id]), (
            f"topic_angle_map[{topic_id!r}] targets deprecated angle {angle_id!r}; "
            "point at the v2 successor instead"
        )


def test_catalog_planner_topic_angle_map_covers_expected_topics(registry):
    res = registry.get("catalog_planner_resolution") or {}
    tmap = res.get("topic_angle_map") or {}
    # Per catalog v2 §6 — operator-confirmed mappings.
    expected = {
        "anxiety": "PROTECTIVE_ALARM",
        "overthinking": "SILENT_VERDICT",
        "burnout": "INVISIBLE_COST",
        "imposter_syndrome": "IMPOSTERS_PERFORMANCE",
        "grief": "UNFINISHED_GOODBYE",
        "self_worth": "BORROWED_SELF",
        "shame": "INHERITED_SMALLNESS",
        "depression": "DOWNWARD_PULL",
        "relationship_anxiety": "FAMILIAR_WOUND",
        "social_anxiety": "NERVOUS_ARCHITECTURE",
        "sleep_anxiety": "NERVOUS_ARCHITECTURE",
        "boundaries": "UNSPOKEN_CONTRACT",
        "courage": "INVISIBLE_THRESHOLD",
        "financial_anxiety": "INHERITED_AMBITION",
        "compassion_fatigue": "UNNAMED_THIRST",
        "body_image": "WATCHED_BODY",
        "money": "SCARCITY_ECHO",
        "addiction": "USEFUL_NUMBNESS",
        "adhd": "MISFIRING_ENGINE",
        "divorce": "UNFINISHED_STORY",
    }
    for topic, want in expected.items():
        assert tmap.get(topic) == want, f"topic_angle_map[{topic}] expected {want}, got {tmap.get(topic)}"


# ─── Successor reverse pointers (forensics) ────────────────────────────────


def test_successor_of_pointers_match_legacy_successor_angle_id(angles):
    """If v2 angle declares successor_of: X, then legacy X.successor_angle_id should be this v2 angle."""
    for aid, entry in angles.items():
        successor_of = entry.get("successor_of")
        if not successor_of:
            continue
        assert successor_of in angles, f"{aid}.successor_of={successor_of!r} not in registry"
        legacy_entry = angles[successor_of]
        assert legacy_entry.get("deprecated"), (
            f"{aid}.successor_of points at non-deprecated {successor_of}"
        )
        assert legacy_entry.get("successor_angle_id") == aid, (
            f"{aid}.successor_of={successor_of!r} but {successor_of}.successor_angle_id="
            f"{legacy_entry.get('successor_angle_id')!r}"
        )

# ─── Inconsistency fixes (registry v2 PR #1245) ────────────────────────────


def test_loyal_adaptation_two_level_chain_depth_is_2(registry):
    """LOYAL_ADAPTATION → PROTECTIVE_ALARM → USEFUL_SIGNAL resolves with chain_depth=2."""
    merged = resolve_angle_with_inheritance("LOYAL_ADAPTATION", registry)
    prov = merged["_resolution_provenance"]
    assert prov["chain_depth"] == 2
    assert prov["parent_chain"] == ["LOYAL_ADAPTATION", "PROTECTIVE_ALARM", "USEFUL_SIGNAL"]
    assert merged["framing_mode"] == "reveal"


def test_parent_chain_exceeding_max_depth_raises(registry):
    """Chains longer than MAX_CHAIN_DEPTH raise AngleChainDepthError."""
    angles = registry.get("angles") or {}
    # Build a chain of depth MAX_CHAIN_DEPTH + 1
    depth = MAX_CHAIN_DEPTH + 1
    mini_angles = {}
    for i in range(depth + 1):
        aid = f"CHAIN_{i}"
        entry: dict = {"display_name": aid, "core_frame": "x", "use_when": "x"}
        if i > 0:
            entry["parent_universal"] = f"CHAIN_{i - 1}"
        else:
            entry.update({
                "arc_variant": "ARC_P",
                "framing_mode": "reveal",
                "chapter_1_role_bias": "destabilization",
                "integration_reinforcement_type": "revelation",
            })
        mini_angles[aid] = entry
    mini = {"angles": mini_angles}
    with pytest.raises(AngleChainDepthError):
        resolve_angle_with_inheritance(f"CHAIN_{depth}", mini)


def test_named_object_by_topic_keys_subset_of_canonical_topics(angles):
    """All named_object_by_topic keys must appear in canonical_topics.yaml."""
    canonical = load_canonical_topic_ids()
    for aid, entry in angles.items():
        if entry.get("deprecated") or "parent_universal" in entry:
            continue
        named = entry.get("journey", {}).get("named_object_by_topic") or {}
        extra = set(named.keys()) - canonical
        assert not extra, f"{aid} named_object_by_topic has non-canonical keys: {sorted(extra)}"


def test_layer_4_skipped_for_sleep_anxiety(registry):
    merged = resolve_angle_with_inheritance("USEFUL_SIGNAL", registry, topic_id="sleep_anxiety")
    layers = merged["journey"]["layer_progression"]
    layer_nums = [layer["layer"] for layer in layers]
    assert 4 not in layer_nums
    assert len(layers) == 4


def test_layer_4_included_for_anxiety_default(registry):
    merged = resolve_angle_with_inheritance("USEFUL_SIGNAL", registry, topic_id="anxiety")
    layers = merged["journey"]["layer_progression"]
    layer_nums = [layer["layer"] for layer in layers]
    assert 4 in layer_nums
    assert len(layers) == 5
