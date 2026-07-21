"""Tests for compile_safe_zones.py — Phase B.1 step 1 deterministic gate.

Per docs/specs/MANGA_LAYER_RENDER_CONTRACT_SPEC.md §13.2.

Validates:
  1. Smoke: compiler runs clean on canonical inputs
  2. Determinism: same input -> same hash across runs (golden snapshot)
  3. Precedence: spec §5.7 compiled-view spot rows are reproduced exactly
  4. Schema: missing required field is fatal (exit 2)
  5. Schema: wrong type is fatal
  6. Schema: unknown framing reference is fatal
  7. Cycle: subject<->subject loop is fatal
  8. Genre scope: framing_override only fires when subject's framing matches
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[4]
COMPILER = REPO / "scripts" / "manga" / "compile_safe_zones.py"
INPUT_DIR = REPO / "config" / "manga" / "safe_zones"
DEFAULT_OUTPUT = REPO / "config" / "manga" / "compiled" / "safe_zones.yaml"


# ─────────────────────────────────────────────────────────────────────────────
# helpers
# ─────────────────────────────────────────────────────────────────────────────


def run_compiler(input_dir: Path | None = None, output: Path | None = None):
    cmd = [sys.executable, str(COMPILER)]
    if input_dir is not None:
        cmd += ["--input-dir", str(input_dir)]
    if output is not None:
        cmd += ["--output", str(output)]
    return subprocess.run(cmd, capture_output=True, text=True)


def copy_canonical_inputs(dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for f in INPUT_DIR.glob("*.yaml"):
        (dst / f.name).write_text(f.read_text())


def sha256_text(p: Path) -> str:
    return hashlib.sha256(p.read_text().encode("utf-8")).hexdigest()


# ─────────────────────────────────────────────────────────────────────────────
# 1. Smoke
# ─────────────────────────────────────────────────────────────────────────────


def test_compiler_smoke():
    r = run_compiler()
    assert r.returncode == 0, f"compiler failed: stderr={r.stderr!r}, stdout={r.stdout!r}"
    assert DEFAULT_OUTPUT.is_file()


# ─────────────────────────────────────────────────────────────────────────────
# 2. Determinism — golden snapshot
# ─────────────────────────────────────────────────────────────────────────────


def test_compiler_output_deterministic(tmp_path: Path):
    out1 = tmp_path / "out1.yaml"
    out2 = tmp_path / "out2.yaml"
    r1 = run_compiler(output=out1)
    r2 = run_compiler(output=out2)
    assert r1.returncode == 0
    assert r2.returncode == 0
    h1 = sha256_text(out1)
    h2 = sha256_text(out2)
    assert h1 == h2, f"non-deterministic: {h1} vs {h2}"


# ─────────────────────────────────────────────────────────────────────────────
# 3. Precedence — spec §5.7 compiled-view rows reproduce exactly
# ─────────────────────────────────────────────────────────────────────────────


def _load_compiled() -> dict:
    r = run_compiler()
    assert r.returncode == 0, r.stderr
    return yaml.safe_load(DEFAULT_OUTPUT.read_text())["compiled"]


@pytest.mark.parametrize(
    "row_key,expected_margin,expected_zone",
    [
        # (subject × framing × genre, margin {T,B,L,R}, subject_zone_pct)
        # — from spec §5.7 compiled-view table
        (
            "subject=character_face_only|framing=CU|genre=healing",
            {"top": 15, "bottom": 5, "left": 17.5, "right": 17.5},
            [65, 80],
        ),
        (
            "subject=character_face_only|framing=CU|genre=psychological_horror",
            {"top": 15, "bottom": 0, "left": 17.5, "right": 17.5},
            [65, 80],
        ),
        (
            "subject=character_face_only|framing=CU|genre=comedy",
            {"top": 18, "bottom": 5, "left": 17.5, "right": 17.5},
            [65, 80],
        ),
        (
            "subject=character_full_figure|framing=MS|genre=healing",
            {"top": 5, "bottom": 5, "left": 25, "right": 25},
            [50, 90],
        ),
        (
            "subject=character_ELS_in_L0|framing=LS|genre=healing",
            {"top": 10, "bottom": 10, "left": 10, "right": 10},
            [22, 20],
        ),
        (
            "subject=character_full_figure|framing=MS|genre=fantasy_adventure",
            {"top": 5, "bottom": 5, "left": 25, "right": 25},
            [55, 90],  # fantasy_adventure widens MS zone
        ),
        (
            "subject=object_macro|framing=ECU|genre=healing",
            {"top": 10, "bottom": 10, "left": 12.5, "right": 12.5},
            [75, 80],
        ),
        (
            "subject=object_macro|framing=ECU|genre=mecha",
            {"top": 8, "bottom": 8, "left": 8, "right": 8},
            [75, 80],
        ),
        (
            "subject=character_hand_only|framing=ECU|genre=healing",
            {"top": 17.5, "bottom": 17.5, "left": 17.5, "right": 17.5},
            [65, 65],
        ),
    ],
)
def test_precedence_compiled_rows_match_spec(row_key, expected_margin, expected_zone):
    rows = _load_compiled()
    assert row_key in rows, f"missing row {row_key!r}"
    row = rows[row_key]
    assert row["margin"] == expected_margin, (
        f"{row_key}: margin {row['margin']} != expected {expected_margin}"
    )
    assert row["subject_zone_pct"] == expected_zone, (
        f"{row_key}: zone {row['subject_zone_pct']} != expected {expected_zone}"
    )


def test_archetype_exception_row():
    rows = _load_compiled()
    key = "archetype_exception=window_light_threshold"
    assert key in rows
    row = rows[key]
    # silhouette_back overrides + healing genre + archetype override
    assert row["margin"] == {"top": 10, "bottom": 10, "left": 10, "right": 10}
    assert row["subject_must_not_touch_edge"] is False
    assert row["placement_pinned"] == [5, 30, 45, 95]


def test_genre_healing_adds_negative_space_rule():
    rows = _load_compiled()
    row = rows["subject=character_face_only|framing=CU|genre=healing"]
    assert "composite_rule" in row
    assert row["composite_rule"]["negative_space_min_pct"] == 40


def test_genre_dark_fantasy_adds_dramatic_bleed_flag():
    rows = _load_compiled()
    row = rows["subject=character_face_only|framing=CU|genre=dark_fantasy"]
    assert "archetype_flag" in row
    assert row["archetype_flag"]["dramatic_bleed_allowed"] is True


def test_base_contract_fields_propagate_to_every_row():
    rows = _load_compiled()
    for key, row in rows.items():
        if key.startswith("archetype_exception="):
            continue  # archetype exceptions may override base fields
        # base fields must appear unless explicitly overridden upstream
        assert row.get("backdrop") == "pure_white", f"{key}: backdrop should be pure_white"
        assert row.get("alpha_bimodal") is True, f"{key}: alpha_bimodal should be true"
        assert row.get("feather_px") == 0, f"{key}: feather_px should be 0"
        assert row.get("backdrop_corner_tolerance") == 5, f"{key}: corner tol should be 5"
        assert row.get("subject_must_not_touch_edge") is True, (
            f"{key}: subject_must_not_touch_edge should be true"
        )


# ─────────────────────────────────────────────────────────────────────────────
# 4. Schema: missing required field is fatal
# ─────────────────────────────────────────────────────────────────────────────


def test_missing_schema_version_is_fatal(tmp_path: Path):
    inp = tmp_path / "inp"
    copy_canonical_inputs(inp)
    # Strip schema_version from base_contract
    bad = yaml.safe_load((inp / "base_contract.yaml").read_text())
    del bad["schema_version"]
    (inp / "base_contract.yaml").write_text(yaml.safe_dump(bad))
    r = run_compiler(input_dir=inp)
    assert r.returncode == 2, f"expected exit 2, got {r.returncode}; stderr={r.stderr}"
    assert "missing required keys" in r.stderr


def test_missing_type_is_fatal(tmp_path: Path):
    inp = tmp_path / "inp"
    copy_canonical_inputs(inp)
    bad = yaml.safe_load((inp / "framing_contract.yaml").read_text())
    del bad["type"]
    (inp / "framing_contract.yaml").write_text(yaml.safe_dump(bad))
    r = run_compiler(input_dir=inp)
    assert r.returncode == 2
    assert "missing required keys" in r.stderr


# ─────────────────────────────────────────────────────────────────────────────
# 5. Schema: wrong type is fatal
# ─────────────────────────────────────────────────────────────────────────────


def test_wrong_type_is_fatal(tmp_path: Path):
    inp = tmp_path / "inp"
    copy_canonical_inputs(inp)
    bad = yaml.safe_load((inp / "base_contract.yaml").read_text())
    bad["type"] = "not_base_contract"
    (inp / "base_contract.yaml").write_text(yaml.safe_dump(bad))
    r = run_compiler(input_dir=inp)
    assert r.returncode == 2
    assert "type must be" in r.stderr


# ─────────────────────────────────────────────────────────────────────────────
# 6. Schema: unknown reference is fatal
# ─────────────────────────────────────────────────────────────────────────────


def test_unknown_framing_reference_is_fatal(tmp_path: Path):
    inp = tmp_path / "inp"
    copy_canonical_inputs(inp)
    bad = yaml.safe_load((inp / "subject_contract.yaml").read_text())
    bad["contracts"]["broken_subject"] = {"inherits_from": "framing.DOES_NOT_EXIST"}
    (inp / "subject_contract.yaml").write_text(yaml.safe_dump(bad))
    r = run_compiler(input_dir=inp)
    assert r.returncode == 2
    assert "unknown framing_contract" in r.stderr


def test_unknown_archetype_base_subject_is_fatal(tmp_path: Path):
    inp = tmp_path / "inp"
    copy_canonical_inputs(inp)
    bad = yaml.safe_load((inp / "archetype_exception.yaml").read_text())
    bad["exceptions"]["broken_arch"] = {
        "base": "subject_contract.DOES_NOT_EXIST",
        "overrides": {},
    }
    (inp / "archetype_exception.yaml").write_text(yaml.safe_dump(bad))
    r = run_compiler(input_dir=inp)
    assert r.returncode == 2
    assert "unknown subject_contract" in r.stderr


# ─────────────────────────────────────────────────────────────────────────────
# 7. Cycle detection
# ─────────────────────────────────────────────────────────────────────────────


def test_subject_cycle_is_fatal(tmp_path: Path):
    inp = tmp_path / "inp"
    copy_canonical_inputs(inp)
    bad = yaml.safe_load((inp / "subject_contract.yaml").read_text())
    bad["contracts"]["loop_a"] = {"inherits_from": "subject.loop_b"}
    bad["contracts"]["loop_b"] = {"inherits_from": "subject.loop_a"}
    (inp / "subject_contract.yaml").write_text(yaml.safe_dump(bad))
    r = run_compiler(input_dir=inp)
    assert r.returncode == 2
    assert "CycleError" in r.stderr or "cycle in subject_contract" in r.stderr


# ─────────────────────────────────────────────────────────────────────────────
# 8. Genre scope: framing_override is correctly scope-targeted
# ─────────────────────────────────────────────────────────────────────────────


def test_dark_fantasy_cu_override_only_fires_for_CU_inheritors():
    """dark_fantasy.framing_overrides.CU should affect character_face_only (CU)
    but NOT character_full_figure (MS)."""
    rows = _load_compiled()
    cu_row = rows["subject=character_face_only|framing=CU|genre=dark_fantasy"]
    ms_row = rows["subject=character_full_figure|framing=MS|genre=dark_fantasy"]
    # CU row: dark_fantasy lowers margin
    assert cu_row["margin"]["top"] == 7, f"CU dark_fantasy top should be 7, got {cu_row['margin']['top']}"
    # MS row: dark_fantasy should NOT touch margin (no MS override in dark_fantasy)
    assert ms_row["margin"]["top"] == 5, f"MS dark_fantasy top should stay base 5, got {ms_row['margin']['top']}"


def test_mecha_object_macro_subject_override_only_fires_for_object_macro():
    """mecha.subject_overrides.object_macro should affect object_macro
    but NOT character_full_figure."""
    rows = _load_compiled()
    obj_row = rows["subject=object_macro|framing=ECU|genre=mecha"]
    char_row = rows["subject=character_full_figure|framing=MS|genre=mecha"]
    # object_macro mecha: subject_override sets margins to 8
    assert obj_row["margin"] == {"top": 8, "bottom": 8, "left": 8, "right": 8}
    # character_full_figure mecha: no subject_override applies
    assert char_row["margin"] == {"top": 5, "bottom": 5, "left": 25, "right": 25}
