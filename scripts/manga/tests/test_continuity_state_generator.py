"""Tests for continuity_state_generator.py — Milestone C Step 1+.

Covers:
    - Beatsheet schema validation (pass + fail cases)
    - Inheritance engine (props_reset / restore stack, character_state inheritance)
    - Per-archetype dispatch (12 supported archetypes)
    - H1-H10 heuristic rules (pure-function correctness)
    - Emitter (YAML round-trip via safe_load)
    - OPD-144 tension_override behavior
    - End-to-end round-trip integration test on ep_001

Run from repo root:
    PYTHONPATH=. python3 -m pytest scripts/manga/tests/test_continuity_state_generator.py -v
    OR
    python3 scripts/manga/tests/test_continuity_state_generator.py
"""
from __future__ import annotations

import io
import sys
import unittest
from pathlib import Path
from textwrap import dedent
import tempfile

import yaml

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts" / "manga"))

import continuity_state_generator as gen  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
# Test fixtures
# ─────────────────────────────────────────────────────────────────────────────


def _write_temp_yaml(content: str) -> Path:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
    f.write(content)
    f.close()
    return Path(f.name)


MINIMAL_BEATSHEET = dedent("""
    schema_version: "1.0.0"
    beatsheet_type: episode
    series_id: stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying
    episode_id: ep_001
    stage_characters:
      - mira_aoki
    defaults:
      scene_id: bedroom_aoki
      temporal: dawn
      prop_state:
        phone: face_down
    beats:
      - beat_id: b01
        archetype: sparse_establishing_wide
        beat_type: spatial
        character:
          mira_aoki:
            on_frame: false
            role: implied_listener
""").strip()


# ─────────────────────────────────────────────────────────────────────────────
# Schema validation tests
# ─────────────────────────────────────────────────────────────────────────────


class TestBeatsheetValidation(unittest.TestCase):

    def test_minimal_beatsheet_loads(self):
        path = _write_temp_yaml(MINIMAL_BEATSHEET)
        doc = gen.load_beatsheet(path)
        self.assertEqual(doc["episode_id"], "ep_001")
        self.assertEqual(len(doc["beats"]), 1)

    def test_missing_required_field(self):
        bad = "schema_version: '1.0.0'\nbeatsheet_type: episode\n"
        path = _write_temp_yaml(bad)
        with self.assertRaises(gen.BeatsheetValidationError) as cm:
            gen.load_beatsheet(path)
        self.assertIn("series_id", str(cm.exception))

    def test_wrong_schema_version(self):
        bad = MINIMAL_BEATSHEET.replace('schema_version: "1.0.0"', 'schema_version: "9.9.9"')
        path = _write_temp_yaml(bad)
        with self.assertRaises(gen.BeatsheetValidationError) as cm:
            gen.load_beatsheet(path)
        self.assertIn("schema_version", str(cm.exception))

    def test_empty_stage_characters(self):
        bad = MINIMAL_BEATSHEET.replace(
            "stage_characters:\n  - mira_aoki",
            "stage_characters: []",
        )
        path = _write_temp_yaml(bad)
        with self.assertRaises(gen.BeatsheetValidationError):
            gen.load_beatsheet(path)

    def test_breath_phase_outside_chest_archetype(self):
        bad_beats = dedent("""
            beats:
              - beat_id: b01
                archetype: sparse_establishing_wide
                character:
                  mira_aoki:
                    breath_phase: quickening
        """).strip()
        bad = MINIMAL_BEATSHEET.replace(
            dedent("""
                beats:
                  - beat_id: b01
                    archetype: sparse_establishing_wide
                    beat_type: spatial
                    character:
                      mira_aoki:
                        on_frame: false
                        role: implied_listener
            """).strip(),
            bad_beats,
        )
        path = _write_temp_yaml(bad)
        with self.assertRaises(gen.BeatsheetValidationError) as cm:
            gen.load_beatsheet(path)
        self.assertIn("breath_phase", str(cm.exception).lower())

    def test_tension_override_enum(self):
        # Build beatsheet dict programmatically to avoid YAML indentation issues
        bs = yaml.safe_load(MINIMAL_BEATSHEET)
        bs["beats"][0]["tension_override"] = "rising"
        path = _write_temp_yaml(yaml.safe_dump(bs))
        doc = gen.load_beatsheet(path)
        self.assertEqual(doc["beats"][0]["tension_override"], "rising")

    def test_tension_override_invalid_value(self):
        bs = yaml.safe_load(MINIMAL_BEATSHEET)
        bs["beats"][0]["tension_override"] = "spiking"
        path = _write_temp_yaml(yaml.safe_dump(bs))
        with self.assertRaises(gen.BeatsheetValidationError):
            gen.load_beatsheet(path)

    def test_duplicate_beat_ids(self):
        bs = yaml.safe_load(MINIMAL_BEATSHEET)
        bs["beats"].append({"beat_id": "b01", "archetype": "tea_beat_close_up"})
        path = _write_temp_yaml(yaml.safe_dump(bs))
        with self.assertRaises(gen.BeatsheetValidationError) as cm:
            gen.load_beatsheet(path)
        self.assertIn("duplicate", str(cm.exception).lower())

    def test_character_id_not_in_stage(self):
        bad = MINIMAL_BEATSHEET.replace(
            "mira_aoki:\n        on_frame: false",
            "unknown_character:\n        on_frame: false",
        )
        path = _write_temp_yaml(bad)
        with self.assertRaises(gen.BeatsheetValidationError):
            gen.load_beatsheet(path)


# ─────────────────────────────────────────────────────────────────────────────
# Inheritance engine tests
# ─────────────────────────────────────────────────────────────────────────────


class TestInheritanceEngine(unittest.TestCase):

    def test_props_reset_and_restore_stack(self):
        state = gen.GeneratorState()
        state.prop_state = {"cup": "full", "phone": "face_down"}

        # Snapshot
        state.snapshot_props()
        state.prop_state = {"conference_table": "present"}
        self.assertEqual(state.prop_state, {"conference_table": "present"})

        # Restore
        state.restore_props()
        self.assertEqual(state.prop_state, {"cup": "full", "phone": "face_down"})

    def test_restore_without_snapshot_raises(self):
        state = gen.GeneratorState()
        with self.assertRaises(gen.GeneratorError):
            state.restore_props()


# ─────────────────────────────────────────────────────────────────────────────
# Heuristic rule tests
# ─────────────────────────────────────────────────────────────────────────────


class TestHeuristicRules(unittest.TestCase):

    def test_h1_light_rig_derivation(self):
        scene_inv = {
            "scenes": [
                {"scene_id": "kitchen_table_aoki",
                 "light_rigs": [
                     {"light_rig_id": "K01_dawn_window_warm"},
                     {"light_rig_id": "K02_morning_window_neutral"},
                 ]}
            ]
        }
        rig = gen.derive_light_rig("kitchen_table_aoki", "dawn", scene_inv, None)
        self.assertEqual(rig, "K01_dawn_window_warm")

        rig = gen.derive_light_rig("kitchen_table_aoki", "morning", scene_inv, None)
        self.assertEqual(rig, "K02_morning_window_neutral")

    def test_h1_single_rig_scene(self):
        """Flashback scenes typically have one rig; temporal is moot."""
        scene_inv = {
            "scenes": [
                {"scene_id": "conference_room_flashback",
                 "light_rigs": [{"light_rig_id": "K_flashback_cool_grey_blue"}]}
            ]
        }
        rig = gen.derive_light_rig("conference_room_flashback", "midday", scene_inv, None)
        self.assertEqual(rig, "K_flashback_cool_grey_blue")

    def test_h2_gaze_from_anchor(self):
        gaze = gen.derive_gaze(None, "cup", {"cup": "full"})
        self.assertEqual(gaze, "at_named_object_cup")

    def test_h2_gaze_override(self):
        gaze = gen.derive_gaze({"gaze": "eyes_closed"}, "cup", {"cup": "full"})
        self.assertEqual(gaze, "eyes_closed")

    def test_h2_gaze_anchor_not_in_props(self):
        gaze = gen.derive_gaze(None, "ghost_prop", {"cup": "full"})
        self.assertIsNone(gaze)

    def test_h3_tension_direction_rising(self):
        d = gen.derive_tension_direction(0.4, 0.3, None)
        self.assertEqual(d, "rising")

    def test_h3_tension_direction_easing(self):
        d = gen.derive_tension_direction(0.2, 0.3, None)
        self.assertEqual(d, "easing")

    def test_h3_tension_direction_steady(self):
        d = gen.derive_tension_direction(0.3, 0.3, None)
        self.assertEqual(d, "steady")

    def test_h3_tension_override_per_opd_144(self):
        # OPD-144: operator's tension_override takes precedence over literal H3
        d = gen.derive_tension_direction(0.4, 0.3, tension_override="steady")
        self.assertEqual(d, "steady")
        d = gen.derive_tension_direction(0.3, 0.3, tension_override="rising")
        self.assertEqual(d, "rising")

    def test_h4_magnitude_delta_literal(self):
        # Per OPD-143: literal arithmetic, no narrative semantics
        self.assertEqual(gen.derive_magnitude_delta(0.4, 0.3), 0.1)
        self.assertEqual(gen.derive_magnitude_delta(0.2, 0.3), -0.1)
        self.assertEqual(gen.derive_magnitude_delta(0.3, 0.3), 0.0)
        self.assertEqual(gen.derive_magnitude_delta(0.0, None), 0.0)

    def test_h5_on_frame_from_archetype(self):
        # face archetype → on_frame=True
        self.assertTrue(gen.derive_on_frame(None, "character_quiet_face"))
        # sparse_establishing → on_frame=False (subject_type=None, no state)
        self.assertFalse(gen.derive_on_frame(None, "sparse_establishing_wide"))
        # operator override
        self.assertTrue(gen.derive_on_frame({"on_frame": True}, "sparse_establishing_wide"))
        # pet_companion: human off-frame by default
        self.assertFalse(gen.derive_on_frame(None, "pet_companion_micro"))
        # sparse but op_has_state → True (op is putting character in frame)
        self.assertTrue(
            gen.derive_on_frame(None, "sparse_establishing_wide", op_has_state=True)
        )

    def test_h6_role_from_on_frame(self):
        self.assertEqual(gen.derive_role(True), "subject")
        self.assertEqual(gen.derive_role(False), "implied_listener")

    def test_h7_weather_anchor(self):
        self.assertTrue(gen.should_emit_weather_anchor(0))
        self.assertFalse(gen.should_emit_weather_anchor(1))
        self.assertFalse(gen.should_emit_weather_anchor(34))

    def test_h8_v41_boilerplate(self):
        # Face archetype + past activation onset → emit
        self.assertTrue(gen.should_emit_v41_boilerplate("character_quiet_face", 5))
        self.assertTrue(gen.should_emit_v41_boilerplate("character_face_micro_tension", 10))
        # Early-chapter face archetype → don't emit (per ep001_003 ground truth)
        self.assertFalse(gen.should_emit_v41_boilerplate("character_quiet_face", 2))
        # Non-face archetype → don't emit
        self.assertFalse(gen.should_emit_v41_boilerplate("tea_beat_close_up", 10))
        # pet_companion_micro is a special case per ep001_014
        self.assertTrue(gen.should_emit_v41_boilerplate("pet_companion_micro", 13))

    def test_h10_panel_id_and_inherits_from(self):
        self.assertEqual(gen.compute_panel_id("ep_001", 0), "ep001_001")
        self.assertEqual(gen.compute_panel_id("ep_001", 34), "ep001_035")
        self.assertIsNone(gen.compute_inherits_from("ep_001", 0))
        self.assertEqual(gen.compute_inherits_from("ep_001", 1), "ep001_001")


# ─────────────────────────────────────────────────────────────────────────────
# Archetype dispatch tests
# ─────────────────────────────────────────────────────────────────────────────


class TestArchetypeDispatch(unittest.TestCase):

    def test_supported_archetypes_have_subject_type_mapping(self):
        for arch in gen.SUPPORTED_ARCHETYPES:
            self.assertIn(arch, gen.ARCHETYPE_SUBJECT_TYPE,
                          f"archetype {arch} missing in ARCHETYPE_SUBJECT_TYPE")

    def test_declared_but_unimplemented_raises(self):
        """Per operator instruction, the 7 unused archetypes raise rather
        than silently emitting partial output."""
        bs = yaml.safe_load(MINIMAL_BEATSHEET)
        bs["beats"][0]["archetype"] = "morning_routine_sequence"
        # Validation doesn't raise (archetype is in declared-but-unimplemented set)
        # But build_panel does
        state = gen.GeneratorState()
        state.scene_id = "bedroom_aoki"
        state.temporal = "dawn"
        with self.assertRaises(gen.ArchetypeNotImplementedError):
            gen.build_panel(bs["beats"][0], 0, state, bs, {})

    def test_unknown_archetype_raises(self):
        bs = yaml.safe_load(MINIMAL_BEATSHEET)
        bs["beats"][0]["archetype"] = "made_up_archetype"
        state = gen.GeneratorState()
        with self.assertRaises(gen.ArchetypeNotImplementedError):
            gen.build_panel(bs["beats"][0], 0, state, bs, {})


# ─────────────────────────────────────────────────────────────────────────────
# Emitter (YAML round-trip)
# ─────────────────────────────────────────────────────────────────────────────


class TestEmitter(unittest.TestCase):

    def test_yaml_round_trip(self):
        panel = {
            "schema_version": "1.0.0",
            "panel_id": "ep001_001",
            "inherits_from": None,
            "beat_type": "spatial",
            "archetype": "sparse_establishing_wide",
            "scene_state": {
                "scene_id": "bedroom_aoki",
                "temporal": "dawn",
                "light_rig_id": "K01_dawn_window_warm",
            },
            "character_state": {},
            "prop_state": {"phone": "face_down"},
            "continuity_invariants": ["test"],
        }
        out_path = Path(tempfile.NamedTemporaryFile(suffix=".yaml", delete=False).name)
        gen.emit_panel_yaml(panel, out_path)
        loaded = yaml.safe_load(out_path.read_text())
        self.assertEqual(loaded["panel_id"], panel["panel_id"])
        self.assertEqual(loaded["scene_state"]["scene_id"], "bedroom_aoki")
        self.assertEqual(loaded["prop_state"]["phone"], "face_down")
        out_path.unlink()


# ─────────────────────────────────────────────────────────────────────────────
# End-to-end integration test on ep_001
# ─────────────────────────────────────────────────────────────────────────────


class TestEp001RoundTrip(unittest.TestCase):
    """The single most important test: run the generator on the real
    Step 0 beatsheet and confirm the round-trip diff against ground truth
    gives zero strict (EXACT/ENUM/NUMERIC/STRUCTURAL) divergences.

    This is the Milestone C exit-criteria gate.
    """

    def test_generate_35_panels_for_ep_001(self):
        beatsheet_path = (
            REPO / "artifacts" / "manga"
            / "stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying"
            / "continuity_state" / "ep_001"
            / "_extracted_beatsheet.yaml"
        )
        if not beatsheet_path.exists():
            self.skipTest("ep_001 beatsheet not present in this checkout")

        beatsheet = gen.load_beatsheet(beatsheet_path)
        configs = gen.load_config_inputs(beatsheet, REPO)
        panels = gen.generate_continuity_state(beatsheet, configs)
        self.assertEqual(len(panels), 35,
                         "ep_001 must produce exactly 35 panels (1:1 beat→panel)")

        panel_ids = [p["panel_id"] for p in panels]
        for i in range(35):
            self.assertEqual(panel_ids[i], f"ep001_{i + 1:03d}")

    def test_round_trip_passes_strict_diff(self):
        """Generate ep_001 + run diff harness in strict mode + assert pass."""
        sys.path.insert(0, str(REPO / "scripts" / "manga"))
        import diff_continuity_state as diff

        beatsheet_path = (
            REPO / "artifacts" / "manga"
            / "stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying"
            / "continuity_state" / "ep_001"
            / "_extracted_beatsheet.yaml"
        )
        if not beatsheet_path.exists():
            self.skipTest("ep_001 beatsheet not present in this checkout")

        # Generate to temp dir
        out_dir = Path(tempfile.mkdtemp(prefix="v51_step1_test_"))
        beatsheet = gen.load_beatsheet(beatsheet_path)
        configs = gen.load_config_inputs(beatsheet, REPO)
        panels = gen.generate_continuity_state(beatsheet, configs)
        for panel in panels:
            gen.emit_panel_yaml(panel, out_dir / f"{panel['panel_id']}.yaml")

        # Diff against ground truth
        gt_dir = (
            REPO / "artifacts" / "manga"
            / "stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying"
            / "continuity_state" / "ep_001"
        )
        gen_files = sorted(p for p in out_dir.glob("*.yaml"))
        gt_files = sorted(p for p in gt_dir.glob("ep001_*.yaml"))
        gen_by_stem = {p.stem: p for p in gen_files}
        gt_by_stem = {p.stem: p for p in gt_files}

        all_divergences = []
        for stem in sorted(set(gen_by_stem) & set(gt_by_stem)):
            all_divergences.extend(
                diff.diff_continuity_state(gen_by_stem[stem], gt_by_stem[stem])
            )

        strict_classes = {"EXACT", "ENUM", "NUMERIC", "STRUCTURAL"}
        strict = [
            d for d in all_divergences
            if d.class_ in strict_classes and not d.acceptable
        ]
        self.assertEqual(strict, [],
                         f"Expected zero strict divergences (only known-acceptable + "
                         f"COMMENTARY allowed); got {len(strict)} strict divergences:\n"
                         + "\n".join(
                             f"  [{d.class_}] {d.panel_id}.{d.field_path}: "
                             f"gen={d.generated_value!r} gt={d.ground_truth_value!r}"
                             for d in strict[:10]
                         ))


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    unittest.main(verbosity=2)
