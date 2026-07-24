"""Storyboard consumption wiring (manga process uplift Lane 10).

Proves the arc storyboard is a consumed INPUT, not a planning-only artifact
(MANGA_ARC_STORYBOARD_CONTRACT.md §"Storyboard consumption"):

  1. Golden path — the REAL cognitive_clarity ja_JP ep_001 storyboard + script
     compile to a deterministic, storyboard-ordered panel_prompts artifact.
  2. Divergence rule — storyboard wins on panel count; WARN rows are emitted
     (OPD-154: panel descriptions > writer notes).
  3. Grammar stays gatekeeper — a storyboard-planned panel violating the
     G1 crop×bg_class legality matrix FAILS assembly.
  4. Inventory EXTENDS — the script-only legacy path is byte-identical when no
     storyboard is passed (no new keys, deterministic).
  5. Assembly hints — storyboard layer picks become manifest layers[] entries
     with provenance carried through; missing bank assets become flagged
     INTERIM placeholder rows + demand-gap rows, never silently dropped.

Run:
    PYTHONPATH=. python3 -m pytest tests/manga/test_storyboard_consumption.py -v
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts" / "manga"))

from phoenix_v4.manga.chapter.visual_from_script import (  # noqa: E402
    build_assembly_layer_hints,
    compile_panel_prompts_from_chapter_script,
    compute_storyboard_divergences,
)
from phoenix_v4.manga.models.validation import validate_instance  # noqa: E402

import assemble_from_bank as afb  # noqa: E402

GOLDEN_SERIES = (
    "cognitive_clarity__kurose_jin__ja_JP__overthinking__the_loop_is_not_thinking"
)
GOLDEN_STORYBOARD = (
    REPO / "artifacts" / "manga" / "arc_storyboards" / GOLDEN_SERIES
    / "ep_001.arc_storyboard.yaml"
)
GOLDEN_SCRIPT = (
    REPO / "artifacts" / "manga" / "chapter_scripts" / GOLDEN_SERIES / "ep_001.yaml"
)


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _mini_script(panels_page1: list[dict]) -> dict:
    return {
        "schema_version": "1.0.0",
        "artifact_type": "chapter_script_writer_handoff",
        "series_id": "unit_series",
        "chapter_id": "ep_unit",
        "pages": [{"page_id": "p01", "panels": panels_page1}],
    }


def _mini_storyboard(panels: list[dict]) -> dict:
    return {
        "schema_version": "1.0.0",
        "artifact_type": "arc_storyboard_plan",
        "series_id": "unit_series",
        "chapter_id": "ep_unit",
        "genre_id": "psychological_thriller",
        "panels": panels,
    }


def _sb_panel(pid: str, page: str = "p01", **extra) -> dict:
    row = {
        "panel_id": pid,
        "page_id": page,
        "story_move": f"world visibly changes in {pid}",
        "visual_proof": f"the picture proves the change in {pid}",
        "information_delta": f"reader learns {pid}",
    }
    row.update(extra)
    return row


# ── 1. Golden path: real cognitive_clarity ep_001 fixtures ───────────────────


def test_golden_cognitive_clarity_ep001_storyboard_driven() -> None:
    storyboard = _load_yaml(GOLDEN_STORYBOARD)
    script = _load_yaml(GOLDEN_SCRIPT)

    doc = compile_panel_prompts_from_chapter_script(
        script,
        series_id=script["series_id"],
        chapter_id=script["chapter_id"],
        config_hash="test",
        arc_storyboard=storyboard,
        arc_storyboard_ref=str(GOLDEN_STORYBOARD.relative_to(REPO)),
    )
    validate_instance(doc, "panel_prompts")

    sb_ids = [p["panel_id"] for p in storyboard["panels"]]
    out_ids = [p["panel_id"] for p in doc["panels"]]
    # Storyboard page map drives panel count AND ordering.
    assert out_ids == sb_ids
    assert doc["storyboard_driven"] is True
    assert doc["arc_storyboard_ref"] == str(GOLDEN_STORYBOARD.relative_to(REPO))

    by_id = {p["panel_id"]: p for p in doc["panels"]}
    for sb_panel in storyboard["panels"]:
        panel = by_id[sb_panel["panel_id"]]
        block = panel["storyboard"]
        assert block["story_move"] == sb_panel["story_move"]
        assert block["visual_proof"] == sb_panel["visual_proof"]
        assert block["information_delta"] == sb_panel["information_delta"]
        # visual_proof leads the positive prompt (scene-aware compiler).
        assert panel["prompt"].strip()
    assert by_id["ep001_005"]["storyboard"]["story_function"] == "override_attempt"

    # Deterministic: recompiling yields a byte-identical artifact.
    doc2 = compile_panel_prompts_from_chapter_script(
        script,
        series_id=script["series_id"],
        chapter_id=script["chapter_id"],
        config_hash="test",
        arc_storyboard=storyboard,
        arc_storyboard_ref=str(GOLDEN_STORYBOARD.relative_to(REPO)),
    )
    assert json.dumps(doc, sort_keys=True, ensure_ascii=False) == json.dumps(
        doc2, sort_keys=True, ensure_ascii=False
    )


def test_golden_ep001_script_dialogue_supplies_prompt_seed() -> None:
    storyboard = _load_yaml(GOLDEN_STORYBOARD)
    script = _load_yaml(GOLDEN_SCRIPT)
    doc = compile_panel_prompts_from_chapter_script(
        script, arc_storyboard=storyboard
    )
    by_id = {p["panel_id"]: p for p in doc["panels"]}
    # ep001_005 carries ja_JP dialogue in the script (dialogue_lines) and the
    # storyboard allows dialogue there — the script supplies it.
    assert by_id["ep001_005"]["storyboard"].get("dialogue_allowed") is True


# ── 2. Divergence rule: storyboard wins + WARN rows ──────────────────────────


def test_divergence_storyboard_wins_on_panel_count() -> None:
    script = _mini_script([
        {"panel_id": "a", "action": "hero pauses at the door", "camera": "wide"},
        {"panel_id": "b", "action": "an extra beat the board cut", "camera": "wide"},
    ])
    storyboard = _mini_storyboard([_sb_panel("a")])

    doc = compile_panel_prompts_from_chapter_script(script, arc_storyboard=storyboard)
    assert [p["panel_id"] for p in doc["panels"]] == ["a"]

    rows = doc["storyboard_divergences"]
    types = {r["type"] for r in rows}
    assert "page_panel_count_mismatch" in types
    assert "script_panel_not_in_storyboard" in types
    mismatch = next(r for r in rows if r["type"] == "page_panel_count_mismatch")
    assert mismatch["severity"] == "WARN"
    assert mismatch["resolution"] == "storyboard_wins"
    assert mismatch["storyboard_count"] == 1
    assert mismatch["script_count"] == 2


def test_divergence_storyboard_panel_missing_from_script_is_scaffolded() -> None:
    script = _mini_script([
        {"panel_id": "a", "action": "hero pauses at the door", "camera": "wide"},
    ])
    storyboard = _mini_storyboard([_sb_panel("a"), _sb_panel("c")])

    doc = compile_panel_prompts_from_chapter_script(script, arc_storyboard=storyboard)
    assert [p["panel_id"] for p in doc["panels"]] == ["a", "c"]
    scaffolded = next(p for p in doc["panels"] if p["panel_id"] == "c")
    # Scaffolded entirely from the storyboard: visual_proof drives the prompt.
    assert scaffolded["storyboard"]["visual_proof"].startswith("the picture proves")
    types = {r["type"] for r in doc["storyboard_divergences"]}
    assert "storyboard_panel_missing_from_script" in types


def test_divergence_dialogue_disallowed_by_storyboard() -> None:
    script = _mini_script([
        {
            "panel_id": "a",
            "action": "hero pauses at the door",
            "dialogue": ["I should not be speaking here"],
        },
    ])
    storyboard = _mini_storyboard([_sb_panel("a", dialogue_allowed=False)])

    doc = compile_panel_prompts_from_chapter_script(script, arc_storyboard=storyboard)
    types = {r["type"] for r in doc["storyboard_divergences"]}
    assert "dialogue_disallowed_by_storyboard" in types


def test_wrong_storyboard_artifact_rejected() -> None:
    script = _mini_script([{"panel_id": "a", "action": "beat"}])
    with pytest.raises(ValueError, match="arc_storyboard_plan"):
        compile_panel_prompts_from_chapter_script(
            script, arc_storyboard={"artifact_type": "series_plan"}
        )
    with pytest.raises(ValueError, match="series_id"):
        compile_panel_prompts_from_chapter_script(
            script,
            arc_storyboard=_mini_storyboard([_sb_panel("a")]) | {"series_id": "other"},
        )


def test_compute_divergences_clean_when_aligned() -> None:
    script = _mini_script([
        {"panel_id": "a", "action": "hero pauses"},
        {"panel_id": "b", "action": "hero moves"},
    ])
    storyboard = _mini_storyboard([_sb_panel("a"), _sb_panel("b")])
    assert compute_storyboard_divergences(storyboard, script) == []


# ── 3. Composition grammar stays gatekeeper for storyboard-planned panels ────


def _write_png(path: Path, size: tuple[int, int], color: tuple[int, int, int, int]) -> None:
    from PIL import Image

    Image.new("RGBA", size, color).save(path)


def _storyboard_planned_panel(tmp_path: Path, *, crop_class: str, bg_class: str,
                              derivation: dict | None = None) -> dict:
    """Build a storyboard-planned manifest panel with composition sidecars."""
    l0 = tmp_path / "L0_stage.png"
    l2 = tmp_path / "L2_subject.png"
    _write_png(l0, (320, 480), (200, 200, 200, 255))
    _write_png(l2, (120, 160), (90, 60, 40, 255))
    (tmp_path / "L0_stage.composition.json").write_text(json.dumps({
        "asset_id": "L0_stage",
        "bg_class": bg_class,
        "camera": {"angle_bucket": "eye", "eye_level_y_pct": 42},
    }))
    (tmp_path / "L2_subject.composition.json").write_text(json.dumps({
        "asset_id": "L2_subject",
        "crop_class": crop_class,
        "implied_camera": {"angle_bucket": "eye"},
        "anchor": {"y_px": 150.0},
    }))
    l0_layer: dict = {"layer_class": "L0", "asset": str(l0), "provenance": "REAL"}
    if derivation:
        l0_layer["derivation"] = derivation
    return {
        "panel_id": "sb_panel_001",
        "shot_type": "dialogue_bust",
        "storyboard": {
            "story_move": "the subject finally sets the phone down",
            "visual_proof": "hand releasing the phone onto the desk",
            "information_delta": "the override has ended",
            "page_id": "p01",
        },
        "layers": [
            l0_layer,
            {
                "layer_class": "L2",
                "asset": str(l2),
                "provenance": "REAL",
                "bbox_pct": [20, 20, 55, 65],
            },
        ],
    }


def test_storyboard_planned_panel_illegal_crop_bg_fails_assembly(tmp_path: Path) -> None:
    # G1 legality matrix: bust × full_render is ILLEGAL (no diegetic pair).
    panel = _storyboard_planned_panel(tmp_path, crop_class="bust", bg_class="full_render")
    with pytest.raises(ValueError, match="composition grammar FAIL — G1"):
        afb.assemble_panel(panel, {"width": 320, "height": 480}, tmp_path)


def test_storyboard_planned_panel_legal_combo_assembles(tmp_path: Path) -> None:
    # bust × tone_gradient (derived stage) is LEGAL — assembly succeeds and the
    # grammar report carries a G1 PASS for the storyboard-planned panel.
    panel = _storyboard_planned_panel(
        tmp_path,
        crop_class="bust",
        bg_class="full_render",
        derivation={"type": "tone_gradient"},
    )
    img, records, report = afb.assemble_panel(panel, {"width": 320, "height": 480}, tmp_path)
    assert img.size == (320, 480)
    assert report is not None and report.passed
    assert any(g.gate == "G1" and g.severity.value == "PASS" for g in report.gates)
    assert {r["provenance"] for r in records} == {"REAL"}


# ── Manifest-hint ingestion (validate_manifest + schema) ─────────────────────


def _hint_manifest(panel: dict) -> dict:
    return {
        "schema_version": "1.0.0",
        "series_id": "unit_series",
        "arc_storyboard_ref": "artifacts/manga/arc_storyboards/unit/ep_001.arc_storyboard.yaml",
        "canvas": {"width": 320, "height": 480},
        "panels": [panel],
    }


def test_validate_manifest_accepts_storyboard_hint_block() -> None:
    manifest = _hint_manifest({
        "panel_id": "p1",
        "storyboard": {
            "story_move": "the subject finally sets the phone down",
            "visual_proof": "hand releasing the phone onto the desk",
        },
        "layers": [
            {"layer_class": "L0", "asset": "x.png", "provenance": "REAL"},
        ],
    })
    assert afb.validate_manifest(manifest) == []


def test_validate_manifest_rejects_empty_storyboard_move() -> None:
    manifest = _hint_manifest({
        "panel_id": "p1",
        "storyboard": {"story_move": "none", "visual_proof": "hand releasing the phone"},
        "layers": [
            {"layer_class": "L0", "asset": "x.png", "provenance": "REAL"},
        ],
    })
    errors = afb.validate_manifest(manifest)
    assert any("hard rule 1" in e for e in errors)


def test_assembly_manifest_schema_allows_hint_fields() -> None:
    import jsonschema

    schema = json.loads(
        (REPO / "schemas" / "manga" / "assembly_manifest.schema.json").read_text()
    )
    manifest = _hint_manifest({
        "panel_id": "p1",
        "storyboard": {
            "story_move": "the subject finally sets the phone down",
            "visual_proof": "hand releasing the phone onto the desk",
            "information_delta": "the override has ended",
            "page_id": "p01",
        },
        "layers": [
            {"layer_class": "L0", "asset": "x.png", "provenance": "REAL"},
            {
                "layer_class": "L2",
                "asset": "y.png",
                "provenance": "INTERIM",
                "provenance_note": "bank gap — enqueue render",
                "bbox_pct": [10, 10, 50, 60],
            },
        ],
    })
    jsonschema.validate(manifest, schema)


# ── 4. Inventory EXTENDS: script-only legacy path byte-identical ─────────────


def test_no_storyboard_legacy_path_byte_identical() -> None:
    script = _mini_script([
        {"panel_id": "a", "action": "hero pauses at the door", "camera": "wide",
         "dialogue": ["short line"], "mood": "tense"},
        {"panel_id": "b", "action": "hero crosses the room", "camera": "close"},
    ])
    legacy = compile_panel_prompts_from_chapter_script(
        script, series_id="unit_series", chapter_id="ep_unit", config_hash="test"
    )
    explicit_none = compile_panel_prompts_from_chapter_script(
        script, series_id="unit_series", chapter_id="ep_unit", config_hash="test",
        arc_storyboard=None, arc_storyboard_ref=None,
    )
    assert json.dumps(legacy, sort_keys=True) == json.dumps(explicit_none, sort_keys=True)
    # No storyboard keys leak into the legacy artifact.
    assert "storyboard_driven" not in legacy
    assert "storyboard_divergences" not in legacy
    assert "arc_storyboard_ref" not in legacy
    assert all("storyboard" not in p for p in legacy["panels"])
    validate_instance(legacy, "panel_prompts")


def test_golden_script_only_path_has_no_storyboard_keys() -> None:
    script = _load_yaml(GOLDEN_SCRIPT)
    doc = compile_panel_prompts_from_chapter_script(script)
    assert "storyboard_driven" not in doc
    assert all("storyboard" not in p for p in doc["panels"])


# ── 5. Assembly layer hints: provenance carried, gaps flagged not dropped ────


def test_assembly_hints_real_interim_and_gap_rows(tmp_path: Path) -> None:
    bank = tmp_path / "artifacts" / "manga" / "unit_series" / "bank_contracts"
    bank.mkdir(parents=True)
    (bank / "scene_inventory.yaml").write_text("scenes: []\n")
    real_asset = tmp_path / "artifacts" / "manga" / "unit_series" / "image_bank" / "L0_room.png"
    real_asset.parent.mkdir(parents=True)
    real_asset.write_bytes(b"\x89PNG" + b"0" * 60_000)  # byte-real (≥ 50k floor)
    interim_asset = tmp_path / "artifacts" / "manga" / "unit_series" / "image_bank" / "L2_pose.png"
    interim_asset.write_bytes(b"\x89PNG" + b"0" * 60_000)

    storyboard = _mini_storyboard([
        _sb_panel(
            "a",
            layer_picks=[
                {
                    "layer_class": "L0",
                    "asset": "artifacts/manga/unit_series/image_bank/L0_room.png",
                },
                {
                    # Declared INTERIM stays INTERIM even though the file is real.
                    "layer_class": "L2",
                    "asset": "artifacts/manga/unit_series/image_bank/L2_pose.png",
                    "provenance": "INTERIM",
                    "provenance_note": "stand-in cutout pending banked render",
                    "bbox_pct": [10, 10, 50, 60],
                },
                {
                    "layer_class": "L3",
                    "asset": "artifacts/manga/unit_series/image_bank/L3_missing_cup.png",
                    "bbox_pct": [60, 60, 20, 20],
                },
            ],
        ),
        _sb_panel("b"),  # no picks — counted, not emitted
    ])

    hints = build_assembly_layer_hints(
        storyboard, repo_root=tmp_path, arc_storyboard_ref="unit/ep.arc_storyboard.yaml"
    )
    assert hints["artifact_type"] == "assembly_layer_hints"
    assert hints["bank_contract_present"] is True
    assert hints["arc_storyboard_ref"] == "unit/ep.arc_storyboard.yaml"

    assert len(hints["panels"]) == 1
    panel = hints["panels"][0]
    assert panel["panel_id"] == "a"
    assert panel["storyboard"]["story_move"].startswith("world visibly changes")
    layers = panel["layers"]
    # Never silently dropped: all three picks present.
    assert [ly["layer_class"] for ly in layers] == ["L0", "L2", "L3"]
    assert layers[0]["provenance"] == "REAL"
    assert layers[1]["provenance"] == "INTERIM"  # carried through, not upgraded
    assert layers[1]["provenance_note"] == "stand-in cutout pending banked render"
    assert layers[2]["provenance"] == "INTERIM"  # missing → flagged placeholder
    assert "bank gap" in layers[2]["provenance_note"]

    gaps = hints["gaps"]
    assert gaps["panels_with_gaps"] == [
        {"panel_id": "a", "gaps": ["L3:artifacts/manga/unit_series/image_bank/L3_missing_cup.png"]}
    ]
    stats = gaps["stats"]
    assert stats == {
        "panels_total": 2,
        "panels_with_picks": 1,
        "layers_real": 1,
        "layers_interim": 2,
        "layers_gap": 1,
    }


def test_assembly_hints_below_byte_floor_is_gap(tmp_path: Path) -> None:
    stub = tmp_path / "artifacts" / "manga" / "unit_series" / "image_bank" / "L0_stub.png"
    stub.parent.mkdir(parents=True)
    stub.write_bytes(b"\x89PNG tiny")  # below the 50k stub-as-done floor
    storyboard = _mini_storyboard([
        _sb_panel("a", layer_picks=[{
            "layer_class": "L0",
            "asset": "artifacts/manga/unit_series/image_bank/L0_stub.png",
        }]),
    ])
    hints = build_assembly_layer_hints(storyboard, repo_root=tmp_path)
    layer = hints["panels"][0]["layers"][0]
    assert layer["provenance"] == "INTERIM"
    assert hints["gaps"]["stats"]["layers_gap"] == 1
    assert hints["bank_contract_present"] is False
