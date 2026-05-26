"""Tests for continuity_state_generator.py — Milestone C Step 1+.

Covers:
    - Beatsheet schema validation (pass + fail cases)
    - Inheritance engine (props_reset / restore stack, character_state inheritance)
    - Per-archetype dispatch (12 supported archetypes)
    - H1-H10 heuristic rules (pure-function correctness)
    - Emitter (YAML round-trip via safe_load)
    - OPD-146 tension_override behavior
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
        # OPD-146: operator's tension_override takes precedence over literal H3
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
# OPD-147 / OPD-148 — multi-character extension + new archetype dispatch
# ─────────────────────────────────────────────────────────────────────────────


# Two-character beatsheet fixture used by the new tests below. Keeps Mira as
# stage_characters[0] (protagonist contract); Dr. Morimoto is the secondary.
MULTI_CHAR_BEATSHEET_BASE = dedent("""
    schema_version: "1.0.0"
    beatsheet_type: episode
    series_id: stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying
    episode_id: ep_002
    stage_characters:
      - mira_aoki
      - dr_morimoto
    defaults:
      scene_id: office_meeting_room
      temporal: morning
      light_rig_id: K02_morning_window_neutral
      prop_state:
        laptop_meeting: open_between_them
    beats:
      - beat_id: b01
        archetype: character_face_micro_tension
        beat_type: micro
        character:
          mira_aoki:
            on_frame: true
            pose_id: face_close_seated_speaking
            expression_dial: 0.6
            emotional: anxious
            gaze: at_named_character_dr_morimoto
            hand_state: relaxed_open
          dr_morimoto:
            on_frame: false
            role: implied_listener
      - beat_id: b02
        archetype: secondary_character_face_close
        subject_actor: dr_morimoto
        beat_type: micro
        character:
          mira_aoki:
            on_frame: false
            role: implied_listener
          dr_morimoto:
            on_frame: true
            role: subject
            pose_id: face_close_seated_calm
            expression_dial: 0.2
            emotional: calm
            gaze: at_named_character_mira_aoki
            hand_state: relaxed_open
        shared_attention_anchor: dr_morimoto
      - beat_id: b03
        archetype: character_face_micro_tension
        beat_type: micro
        character:
          mira_aoki:
            on_frame: true
            pose_id: face_close_seated_speaking
            expression_dial: 0.5
            emotional: anxious_diminishing
            gaze: at_named_character_dr_morimoto
            hand_state: relaxed_open
          dr_morimoto:
            on_frame: false
            role: implied_listener
        tension_override: easing
      - beat_id: b04
        archetype: typographic_caption_card
        caption_style: mid_episode_strip
        caption_text: "It's not danger. It's just steam."
        beat_type: micro
        character:
          mira_aoki: null
          dr_morimoto: null
""").strip()


class TestSecondaryCharacterFaceCloseDispatch(unittest.TestCase):
    """OPD-147: secondary_character_face_close DEFINE.

    Verifies the new archetype dispatches correctly under the multi-character
    extension: subject_actor binds the on-frame character, the protagonist is
    off-frame, character_state contains only the subject_actor, v41 boilerplate
    fires.
    """

    def setUp(self):
        path = _write_temp_yaml(MULTI_CHAR_BEATSHEET_BASE)
        self.beatsheet = gen.load_beatsheet(path)
        self.panels = gen.generate_continuity_state(self.beatsheet, {})

    def test_secondary_character_face_close_dispatch_dr_morimoto(self):
        """b02: beat with archetype=secondary_character_face_close +
        subject_actor=dr_morimoto produces correct on-frame state for
        Dr. Morimoto and off-frame state for Mira."""
        b02_panel = self.panels[1]
        self.assertEqual(b02_panel["archetype"], "secondary_character_face_close")
        self.assertEqual(b02_panel["subject_actor"], "dr_morimoto")

        # Dr. Morimoto: on-frame subject; character_state present
        cs_morimoto = b02_panel["character_state"].get("dr_morimoto")
        self.assertIsNotNone(cs_morimoto,
                             "dr_morimoto must have character_state when he's the subject_actor")
        self.assertEqual(cs_morimoto["pose_id"], "face_close_seated_calm")
        self.assertEqual(cs_morimoto["expression_dial"], 0.2)
        self.assertEqual(cs_morimoto["emotional"], "calm")

        # Mira: off-frame; no character_state entry (suppressed via POV)
        self.assertNotIn("mira_aoki", b02_panel["character_state"],
                         "Mira's character_state must be suppressed under "
                         "secondary_character_face_close POV")

        # Active entities: Dr. Morimoto on_frame=true, Mira on_frame=false
        active = {e["id"]: e for e in b02_panel["relational_field"]["active_entities"]}
        self.assertTrue(active["dr_morimoto"]["on_frame"])
        self.assertEqual(active["dr_morimoto"]["role"], "subject")
        self.assertFalse(active["mira_aoki"]["on_frame"])
        self.assertEqual(active["mira_aoki"]["role"], "implied_listener")

        # H8: v41_per_axis_edge_resolved fires (face-only archetype past activation onset)
        # Note: beat_index 1 (b02) is < 5, so v41 doesn't fire here. Verify the
        # archetype IS in V41_FACE_ARCHETYPES even though this specific beat
        # doesn't emit (matches V1 ep001_003 behavior).
        self.assertIn("secondary_character_face_close", gen.V41_FACE_ARCHETYPES)

    def test_secondary_character_face_close_missing_subject_actor_raises(self):
        """Without subject_actor, schema validation raises."""
        # Build via dict mutation to avoid indentation-fragile string replace.
        bs = yaml.safe_load(MULTI_CHAR_BEATSHEET_BASE)
        del bs["beats"][1]["subject_actor"]
        path = _write_temp_yaml(yaml.safe_dump(bs))
        with self.assertRaises(gen.BeatsheetValidationError) as cm:
            gen.load_beatsheet(path)
        self.assertIn("subject_actor", str(cm.exception).lower())

    def test_secondary_character_face_close_invalid_subject_actor_raises(self):
        """subject_actor not in stage_characters raises."""
        bs = yaml.safe_load(MULTI_CHAR_BEATSHEET_BASE)
        bs["beats"][1]["subject_actor"] = "ghost_character"
        path = _write_temp_yaml(yaml.safe_dump(bs))
        with self.assertRaises(gen.BeatsheetValidationError):
            gen.load_beatsheet(path)


class TestTypographicCaptionCardDispatch(unittest.TestCase):
    """OPD-148: typographic_caption_card DEFINE (META cluster).

    Verifies the new META archetype: empty character_state for ALL stage
    characters, caption_text + caption_style preserved, render_directive
    emitted, scene_state.light_rig_id suppressed, both characters off_frame.
    """

    def setUp(self):
        path = _write_temp_yaml(MULTI_CHAR_BEATSHEET_BASE)
        self.beatsheet = gen.load_beatsheet(path)
        self.panels = gen.generate_continuity_state(self.beatsheet, {})

    def test_typographic_caption_card_dispatch(self):
        """b04: typographic_caption_card emits caption_text + caption_style +
        render_directive; character_state is empty for all stage characters;
        active_entities show on_frame=false for both."""
        b04_panel = self.panels[3]
        self.assertEqual(b04_panel["archetype"], "typographic_caption_card")

        # META fields preserved
        self.assertEqual(b04_panel["caption_style"], "mid_episode_strip")
        self.assertEqual(b04_panel["caption_text"], "It's not danger. It's just steam.")
        self.assertEqual(b04_panel["render_directive"], "typographic_only")

        # character_state: all stage_characters suppressed
        self.assertEqual(b04_panel["character_state"], {},
                         "typographic_caption_card must suppress all character_state")

        # active_entities: every entity off_frame
        for entity in b04_panel["relational_field"]["active_entities"]:
            self.assertFalse(entity["on_frame"],
                             f"{entity['id']} must be on_frame=false for "
                             f"typographic_caption_card META archetype")
            self.assertEqual(entity["role"], "implied_listener")

        # scene_state.light_rig_id dropped (no L0 lighting under META)
        self.assertNotIn("light_rig_id", b04_panel["scene_state"],
                         "typographic_caption_card must drop light_rig_id "
                         "(rendered via lettering pipeline, not L0/L1/L2/L3)")

    def test_typographic_caption_card_missing_caption_style_raises(self):
        bs = yaml.safe_load(MULTI_CHAR_BEATSHEET_BASE)
        del bs["beats"][3]["caption_style"]
        path = _write_temp_yaml(yaml.safe_dump(bs))
        with self.assertRaises(gen.BeatsheetValidationError):
            gen.load_beatsheet(path)

    def test_typographic_caption_card_invalid_caption_style_raises(self):
        bs = yaml.safe_load(MULTI_CHAR_BEATSHEET_BASE)
        bs["beats"][3]["caption_style"] = "bogus_style"
        path = _write_temp_yaml(yaml.safe_dump(bs))
        with self.assertRaises(gen.BeatsheetValidationError):
            gen.load_beatsheet(path)


class TestMultiCharacterInheritance(unittest.TestCase):
    """OPD-147 multi-character generator extension.

    Verifies per-character inheritance: when beat N is Dr. Morimoto-focused,
    Mira's state (and dial cache) inherits from beat N-1 so that beat N+1
    (back to Mira) reads the correct prev_dial. Mira's pose at beat N-1 must
    not get clobbered by archetype-default re-application when the protagonist
    is implicitly off-stage.
    """

    def setUp(self):
        path = _write_temp_yaml(MULTI_CHAR_BEATSHEET_BASE)
        self.beatsheet = gen.load_beatsheet(path)
        self.panels = gen.generate_continuity_state(self.beatsheet, {})

    def test_multi_character_inheritance(self):
        """Mira's dial chain inherits across the Dr. Morimoto-focused b02:
        b01 sets Mira dial=0.6; b02 has Mira implied off-frame (no character
        state); b03 sets Mira dial=0.5 — generator must compute
        magnitude_delta = 0.5 - 0.6 = -0.1, NOT 0.0 (which would mean Mira's
        cache was reset to None on b02)."""
        b03_panel = self.panels[2]
        tension = b03_panel["relational_field"]["emotional_tension_vector"]
        # The protagonist's dial inheritance chain continues across b02
        # (where Mira is implied off-frame for the secondary character CU).
        self.assertAlmostEqual(
            tension["magnitude_delta_from_prev"], -0.1, places=3,
            msg="Multi-character inheritance: Mira's dial cache must "
                "persist across b02 (subject_actor=dr_morimoto POV)"
        )
        # direction: operator override "easing"
        self.assertEqual(tension["direction"], "easing")

    def test_secondary_subject_actor_does_not_force_protagonist_character_state(self):
        """When subject_actor is set, the protagonist character_state is
        SUPPRESSED (not just on_frame=false). Verifies b02's character_state
        contains only dr_morimoto, not mira_aoki even with stale inheritance."""
        b02_panel = self.panels[1]
        self.assertNotIn("mira_aoki", b02_panel["character_state"])
        self.assertIn("dr_morimoto", b02_panel["character_state"])

    def test_protagonist_remains_stage_characters_index_0(self):
        """The multi-character extension preserves stage_characters[0] as the
        protagonist (tension vector source). Verify order is stable in
        active_entities across all beats."""
        for panel in self.panels:
            entities = panel["relational_field"]["active_entities"]
            self.assertEqual(entities[0]["id"], "mira_aoki",
                             f"protagonist must remain stage_characters[0] "
                             f"on panel {panel['panel_id']}")


class TestEp001RoundTripStillPassesAfterMultiCharExtension(unittest.TestCase):
    """The regression gate. ep_001 is the V1 single-character episode whose
    35 ground-truth YAMLs must still round-trip byte-clean (zero strict
    EXACT/ENUM/NUMERIC/STRUCTURAL divergences) after the multi-character
    extension lands. Without this test, multi-character refactors could
    silently regress single-char inheritance.

    This test is a deliberate duplicate of TestEp001RoundTrip.test_round_trip_passes_strict_diff
    but lives in this class so the regression gate is unambiguously named in
    the new-archetype + multi-char workstream.

    Per docs/PEARL_ARCHITECT_BRIEF_EP002_CANDIDATE_ARCHETYPES.md acceptance
    criterion #2 (this PR's regression gate).
    """

    def test_ep_001_round_trip_still_passes_after_multi_char_extension(self):
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

        out_dir = Path(tempfile.mkdtemp(prefix="v51_step2_ep_001_regression_"))
        beatsheet = gen.load_beatsheet(beatsheet_path)
        configs = gen.load_config_inputs(beatsheet, REPO)
        panels = gen.generate_continuity_state(beatsheet, configs)
        for panel in panels:
            gen.emit_panel_yaml(panel, out_dir / f"{panel['panel_id']}.yaml")

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
                         "MULTI-CHARACTER REGRESSION: ep_001 single-char "
                         "round-trip must remain byte-clean after extension. "
                         "Got {} strict divergences:\n{}".format(
                             len(strict),
                             "\n".join(
                                 "  [{}] {}.{}: gen={!r} gt={!r}".format(
                                     d.class_, d.panel_id, d.field_path,
                                     d.generated_value, d.ground_truth_value,
                                 )
                                 for d in strict[:10]
                             ),
                         ))


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    unittest.main(verbosity=2)
