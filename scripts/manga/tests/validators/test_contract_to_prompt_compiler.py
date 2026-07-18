"""Tests for contract_to_prompt_compiler.py — Phase B.1 step 1.5.

Per docs/specs/MANGA_LAYER_RENDER_CONTRACT_SPEC.md §5.9 (v0.5.1 additive-safe).

Validates:
  1. Smoke: compiler runs clean on a representative L2 input
  2. Determinism: same input -> same cache_key across runs (golden snapshot)
  3. Required-slot-missing is fatal
  4. Optional-slot-missing uses default
  5. Unknown-slot-in-template is fatal
  6. Provided-but-unreferenced slot is WARN, not fatal (additive-safe)
  7. Dotted-key substitution works (safe_zone.margin.top resolves correctly)
  8. §5.5 spec example reproduces the literal "17%" and "15%" values
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[4]
COMPILER = REPO / "scripts" / "manga" / "contract_to_prompt_compiler.py"
TEMPLATE_DIR = REPO / "config" / "manga" / "prompt_templates"

sys.path.insert(0, str(REPO / "scripts" / "manga"))
import contract_to_prompt_compiler as ctpc  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
# fixtures
# ─────────────────────────────────────────────────────────────────────────────


def _full_l2_inputs() -> dict:
    """A complete, valid L2 contract input for Mira Aoki in iyashikei healing CU."""
    return {
        "character": {
            "render_prompt_base": (
                "Front-facing portrait of Mira Aoki — early 30s East-Asian-coded woman "
                "with soft round face, medium almond eyes, long brown hair side-left "
                "parted, cream knit sweater with warm cardigan, jade pendant"
            ),
            "negative_prompt_base": (
                "shojo sparkle, plastic skin, uncanny valley, bow mouth, extra-large eyes"
            ),
            "wardrobe_override": "",
        },
        "continuity": {
            "pose_clause": "seated upright at kitchen table, both hands wrapping ceramic cup",
            "gaze_clause": "looking down at cup",
            "hand_state_clause": "both hands wrapping cup, fingers relaxed not gripped",
            "emotional_clause": "anxious diminishing — mid-regulation",
            "expression_dial": "0.3",
            "breath_phase_clause": "exhale settling",
        },
        "safe_zone": {
            "framing_clause": "close-up: face and shoulders",
            "subject_zone_pct_str": "65% x 80%",
            "margin": {
                "top": 15,
                "bottom": 5,
                "left": 17.5,
                "right": 17.5,
            },
            "shoulder_margin_clause": (
                "both shoulders fully inside the frame with at least 17% empty space "
                "on left and right of body, forehead with at least 15% empty space above hairline"
            ),
        },
        "archetype": {
            "scene_context_clause": "soft warm-cream kitchen interior with wooden table edge visible",
            "attached_props_clause": "subject holding a warm ceramic cup",
            "background_blur_clause": "soft-focus background, shallow depth of field, subject in sharp foreground",
        },
        "light_rig": {
            "prompt_clause": (
                "warm dawn light from camera-left, soft window-diffused, "
                "gentle warm bounce on shadow side, slight atmospheric haze, "
                "high-key exposure"
            ),
        },
        "style_state": {
            "line_weight_clause": (
                "soft pen-and-ink linework, variable line weight, warm uneven hand-inked"
            ),
            "wash_softness_clause": "soft watercolor wash with gentle 2-4px edge bleed",
            "tonal_density_clause": "low tonal density, breathable negative space",
            "shading_aggression_clause": (
                "gentle shading, low contrast, value range 180-240 on light skin"
            ),
        },
        "genre": {
            "forbidden_grammar_clause": (
                "no speed lines, no dutch angles, no exaggerated reactions, "
                "no sweatdrops, no concentration lines"
            ),
        },
        "resolution": {
            "width": 1080,
            "height": 1920,
        },
    }


def _full_l0_inputs() -> dict:
    """A complete, valid L0 contract input for an iyashikei kitchen-dawn scene."""
    return {
        "scene": {
            "description": (
                "a kitchen at dawn, warm cream and sage palette, soft window light, "
                "wooden table, houseplant on windowsill, no people, no kettle, no cup"
            ),
            "subject_bbox_region_clause": "upper-right third",
            "scene_specific_composition_clause": (
                "houseplant on windowsill lower-left, dappled tree-leaf shadow on wall"
            ),
            "forbidden_objects_clause": "kettle, cup, phone, book, named objects",
            "atmospheric_clause": "gentle dust motes catching morning light",
            "palette_clause": "warm cream + sage accent palette, low saturation",
        },
        "light_rig": {
            "prompt_clause": (
                "warm dawn light from camera-left, soft window-diffused, slight haze"
            ),
        },
        "style_state": {
            "line_weight_clause": "soft pen-and-ink, variable line weight",
            "wash_softness_clause": "soft watercolor wash",
            "tonal_density_clause": "low tonal density, breathable negative space",
            "shading_aggression_clause": "gentle shading",
        },
        "genre": {
            "drawing_tradition_clause": (
                "iyashikei watercolor register, painterly continuity, Yokohama "
                "Kaidashi Kiko aesthetic"
            ),
            "forbidden_grammar_clause": (
                "no speed lines, no dutch angles, no exaggerated reactions"
            ),
        },
        "resolution": {
            "width": 1080,
            "height": 1920,
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# 1. Smoke
# ─────────────────────────────────────────────────────────────────────────────


def test_l2_compile_smoke():
    bundle = ctpc.compile_prompt("L2", _full_l2_inputs())
    assert bundle.positive
    assert bundle.negative
    assert bundle.cache_key
    assert len(bundle.cache_key) == 64  # sha256 hex


def test_l0_compile_smoke():
    bundle = ctpc.compile_prompt("L0", _full_l0_inputs())
    assert bundle.positive
    assert bundle.negative
    assert bundle.cache_key


# ─────────────────────────────────────────────────────────────────────────────
# 2. Determinism (golden snapshot)
# ─────────────────────────────────────────────────────────────────────────────


def test_l2_compile_deterministic():
    inputs = _full_l2_inputs()
    b1 = ctpc.compile_prompt("L2", inputs)
    b2 = ctpc.compile_prompt("L2", inputs)
    assert b1.cache_key == b2.cache_key
    assert b1.positive == b2.positive
    assert b1.negative == b2.negative


def test_l0_compile_deterministic():
    inputs = _full_l0_inputs()
    b1 = ctpc.compile_prompt("L0", inputs)
    b2 = ctpc.compile_prompt("L0", inputs)
    assert b1.cache_key == b2.cache_key


# ─────────────────────────────────────────────────────────────────────────────
# 3. Missing required slot is fatal
# ─────────────────────────────────────────────────────────────────────────────


def test_missing_required_slot_is_fatal():
    inputs = _full_l2_inputs()
    del inputs["character"]["render_prompt_base"]
    with pytest.raises(ctpc.CompilerError) as exc:
        ctpc.compile_prompt("L2", inputs)
    assert "missing required slot" in str(exc.value)
    assert "character.render_prompt_base" in str(exc.value)


def test_missing_required_nested_slot_is_fatal():
    inputs = _full_l2_inputs()
    del inputs["safe_zone"]["margin"]["top"]
    with pytest.raises(ctpc.CompilerError) as exc:
        ctpc.compile_prompt("L2", inputs)
    assert "missing required slot" in str(exc.value)
    assert "safe_zone.margin.top" in str(exc.value)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Missing optional slot uses default
# ─────────────────────────────────────────────────────────────────────────────


def test_missing_optional_slot_uses_default():
    inputs = _full_l2_inputs()
    del inputs["character"]["wardrobe_override"]   # optional, default ""
    del inputs["continuity"]["breath_phase_clause"]  # optional, default ""
    bundle = ctpc.compile_prompt("L2", inputs)
    # Should not raise; defaults substituted.
    assert bundle.positive


def test_missing_optional_l0_slot_uses_default():
    inputs = _full_l0_inputs()
    del inputs["scene"]["atmospheric_clause"]
    del inputs["scene"]["palette_clause"]
    bundle = ctpc.compile_prompt("L0", inputs)
    assert bundle.positive


# ─────────────────────────────────────────────────────────────────────────────
# 5. Unknown slot in template is fatal
# ─────────────────────────────────────────────────────────────────────────────


def test_unknown_slot_in_template_is_fatal(tmp_path: Path):
    """Hand-build a malformed template dir; compiler must reject."""
    td = tmp_path / "templates"
    td.mkdir()
    # Copy real registry, write a bad template
    (td / "slot_registry.yaml").write_text(
        (TEMPLATE_DIR / "slot_registry.yaml").read_text()
    )
    (td / "L2.positive.template.txt").write_text(
        "Subject: {character.render_prompt_base}\nBOGUS: {nonexistent.slot}\n"
    )
    (td / "L2.negative.template.txt").write_text("")
    with pytest.raises(ctpc.CompilerError) as exc:
        ctpc.compile_prompt("L2", _full_l2_inputs(), template_dir=td)
    assert "unknown slot reference" in str(exc.value) or "unknown slot references" in str(exc.value)
    assert "nonexistent.slot" in str(exc.value)


# ─────────────────────────────────────────────────────────────────────────────
# 6. Provided-but-unreferenced slot is WARN (additive-safe)
# ─────────────────────────────────────────────────────────────────────────────


def test_extra_provided_slot_warns_not_fails():
    inputs = _full_l2_inputs()
    inputs["future_axis"] = {"new_slot": "experimental value"}
    bundle = ctpc.compile_prompt("L2", inputs)
    # Should not raise.
    assert bundle.positive
    # Should warn (logged).
    assert any("provided slots not referenced" in w for w in bundle.warnings)


# ─────────────────────────────────────────────────────────────────────────────
# 7. Dotted-key substitution
# ─────────────────────────────────────────────────────────────────────────────


def test_dotted_key_margin_top_substitutes():
    inputs = _full_l2_inputs()
    inputs["safe_zone"]["margin"]["top"] = 999
    bundle = ctpc.compile_prompt("L2", inputs)
    assert "top 999%" in bundle.positive


def test_all_four_margin_axes_substitute():
    inputs = _full_l2_inputs()
    inputs["safe_zone"]["margin"] = {"top": 11, "bottom": 22, "left": 33, "right": 44}
    bundle = ctpc.compile_prompt("L2", inputs)
    assert "top 11%" in bundle.positive
    assert "bottom 22%" in bundle.positive
    assert "left 33%" in bundle.positive
    assert "right 44%" in bundle.positive


# ─────────────────────────────────────────────────────────────────────────────
# 8. §5.5 spec example — the literal 17% / 15% trace
# ─────────────────────────────────────────────────────────────────────────────


def test_spec_5_5_example_literal_values():
    """Per spec §5.5, healing CU character_face_only renders shoulders with
    17% side margin and 15% forehead margin. Confirm the compiler preserves
    those literal values through to the output prompt."""
    inputs = _full_l2_inputs()
    inputs["safe_zone"]["margin"] = {
        "top": 15, "bottom": 5, "left": 17.5, "right": 17.5
    }
    inputs["safe_zone"]["shoulder_margin_clause"] = (
        "both shoulders fully inside the frame with at least 17% empty space "
        "on left and right of body, forehead with at least 15% empty space "
        "above hairline"
    )
    bundle = ctpc.compile_prompt("L2", inputs)
    # The clause appears verbatim.
    assert "at least 17%" in bundle.positive
    assert "at least 15%" in bundle.positive
    # The dotted margin values render as percentages.
    assert "top 15%" in bundle.positive
    assert "bottom 5%" in bundle.positive
    assert "left 17.5%" in bundle.positive
    assert "right 17.5%" in bundle.positive


# ─────────────────────────────────────────────────────────────────────────────
# 9. CLI smoke (end-to-end via subprocess)
# ─────────────────────────────────────────────────────────────────────────────


def test_cli_runs_with_yaml_inputs(tmp_path: Path):
    inputs_path = tmp_path / "inputs.yaml"
    inputs_path.write_text(yaml.safe_dump(_full_l2_inputs()))
    r = subprocess.run(
        [sys.executable, str(COMPILER), "--layer-type", "L2", "--contract-inputs", str(inputs_path)],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, f"stderr={r.stderr}"
    assert "=== POSITIVE ===" in r.stdout
    assert "=== NEGATIVE ===" in r.stdout
    assert "cache_key=" in r.stdout


def test_cli_missing_required_slot_exits_2(tmp_path: Path):
    bad = _full_l2_inputs()
    del bad["character"]["render_prompt_base"]
    inputs_path = tmp_path / "inputs.yaml"
    inputs_path.write_text(yaml.safe_dump(bad))
    r = subprocess.run(
        [sys.executable, str(COMPILER), "--layer-type", "L2", "--contract-inputs", str(inputs_path)],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 2
    assert "missing required slot" in r.stderr
