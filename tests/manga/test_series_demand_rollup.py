"""Tests for the series image-bank demand rollup (uplift Lane 09).

Covers:
  * golden fixture series -> rollup shape (L0/L2/L3, coverage, identity lock)
  * schema validation of the produced rollup
  * outline-episode authoring-gap surfacing (backdrop/object/cast the 100-ep plan
    implies but the bank contract does not cover) -> confidence:outline
  * mutation: an outline arc referencing a NEW pose-less cast/backdrop surfaces a
    fresh authoring_gap row that the control run does not have
  * Lane 10 panels_with_gaps aggregation (gap_asset_counts) — reused, not reinvented
  * byte-real coverage: only >= MIN_BYTES files count as present
  * chapter-script stub mode unchanged (regression)
  * the real Lane 06 golden master plan validates against the schema
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema
import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts" / "manga"))

import generate_bank_contracts_from_script as gen  # noqa: E402

SCHEMA = json.loads((REPO / "schemas" / "manga" / "series_demand_rollup.schema.json").read_text())


def _big_png(path: Path, size: int = 60_000) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\0" * (size - 8))


def _build_fixture(root: Path, *, outline_premise: str, with_gap_file: bool = True) -> Path:
    sid = "test_series"
    brand = "test_brand"
    series_dir = root / "artifacts" / "manga" / sid
    bank = series_dir / "bank_contracts"
    bank.mkdir(parents=True, exist_ok=True)

    # bank contracts (the authored "required universe")
    (bank / "scene_inventory.yaml").write_text(yaml.safe_dump({
        "series_id": sid,
        "scenes": [{
            "scene_id": "kitchen_test",
            "light_rigs": [{"light_rig_id": "K01"}, {"light_rig_id": "K02"}],
        }],
    }))
    (bank / "object_inventory.yaml").write_text(yaml.safe_dump({
        "series_id": sid,
        "objects": [{
            "object_id": "kettle",
            "layer_class": "L3",
            "state_variants_required": ["off_burner", "on_burner"],
        }],
    }))
    (bank / "character_pose_inventory.yaml").write_text(yaml.safe_dump({
        "series_id": sid,
        "characters": {
            "hero_test": {"poses": [{"pose_id": "pose_a"}, {"pose_id": "pose_b"}]},
        },
    }))

    # image_bank: one pose byte-real + a reference sheet; kettle absent.
    _big_png(series_dir / "image_bank" / "L2" / "hero_test" / "pose_a.png")
    _big_png(series_dir / "image_bank" / "L2" / "hero_test" / "hero_test_reference_sheet.png")
    # a below-floor file must NOT count as present
    stub = series_dir / "image_bank" / "L2" / "hero_test" / "pose_b.png"
    stub.parent.mkdir(parents=True, exist_ok=True)
    stub.write_bytes(b"tiny")

    # Lane 10 gap file (panels_with_gaps format)
    if with_gap_file:
        man = series_dir / "assembly_manifests"
        man.mkdir(parents=True, exist_ok=True)
        (man / "ep_001_bank_gaps.json").write_text(json.dumps({
            "series_id": sid, "episode_id": "ep_001",
            "panels_with_gaps": [{"panel_id": "p1", "gaps": ["L2:missing_pose", "L3:kettle_missing"]}],
            "stats": {"panels_total": 1},
        }))

    # flagship config (so _flagship_lora_plan reads a real tier + rows)
    cfg = root / "config" / "manga"
    cfg.mkdir(parents=True, exist_ok=True)
    (cfg / "canonical_brand_list.yaml").write_text(yaml.safe_dump({
        "brands": {brand: {"tier": "flagship"}},
    }))
    (cfg / "brand_lora_plans.yaml").write_text(yaml.safe_dump({
        "brand_style_loras": {brand: {"trigger_word": "style_tb", "status": "planned"}},
        "protagonist_loras": [
            {"series_id": "other_jp_01", "brand_id": brand, "locale": "ja_JP",
             "trigger_word": "hana_tb_jp", "character_name": "Hana", "status": "defined"},
        ],
    }))

    plan = {
        "schema_version": "1.0.0",
        "artifact_type": "series_master_plan",
        "series_id": sid, "brand_id": brand, "locale": "en_US",
        "episode_horizon": 4,
        "arcs": [
            {
                "arc_id": "arc1", "episode_start": 1, "episode_end": 2,
                "detail_level": "detailed", "arc_premise": "The kitchen practice.",
                "arc_promise": "A quiet start.", "self_help_topic": "anxiety",
                "mc_change_vector": {"from_state": "tense", "to_state": "settled"},
                "episodes": [
                    {"episode": 1,
                     "logline": "A morning in the kitchen with the kettle, watched by Yara.",
                     "genre_pleasure_beat": "kettle steam", "self_help_topic_beat": "noticing",
                     "hook": {"promise": "will it settle"}},
                    {"episode": 2,
                     "logline": "The kitchen kettle boils again on a calm afternoon.",
                     "genre_pleasure_beat": "calm", "self_help_topic_beat": "breath",
                     "hook": {"promise": "again"}},
                ],
            },
            {
                "arc_id": "arc2", "episode_start": 3, "episode_end": 4,
                "detail_level": "outline", "arc_premise": outline_premise,
                "arc_promise": "The loop continues.", "self_help_topic": "grief",
                "mc_change_vector": {"from_state": "alone", "to_state": "accompanied"},
            },
        ],
    }
    mp = root / "artifacts" / "manga" / "series_master_plans" / "test.master_plan.yaml"
    mp.parent.mkdir(parents=True, exist_ok=True)
    mp.write_text(yaml.safe_dump(plan))
    return mp


ROOFTOP_PREMISE = "A rooftop scene lit by a candle, watched by Devon each evening."


@pytest.fixture
def rollup(tmp_path: Path) -> dict:
    mp = _build_fixture(tmp_path, outline_premise=ROOFTOP_PREMISE)
    return gen.series_demand_rollup(mp, repo_root=tmp_path)


def _by_id(rows, key, val):
    return next((r for r in rows if r.get(key) == val), None)


def test_schema_validates(rollup):
    jsonschema.Draft202012Validator(SCHEMA).validate(rollup)
    assert rollup["acceptance_layer"] == "structurally_clear"
    assert rollup["episode_horizon"] == 4
    assert rollup["detailed_window_end"] == 2


def test_l0_backdrop_from_contract(rollup):
    row = _by_id(rollup["demand"]["l0_backdrops"], "scene_id", "kitchen_test")
    assert row is not None
    assert row["source"] == "bank_contract"
    assert row["render_demand"] == 2  # two light rigs
    assert row["present_byte_real"] == 0
    assert row["coverage_gap"] == 2
    # kitchen appears in a DETAILED episode -> authored confidence
    assert row["confidence"] == "authored"
    assert row["episodes_touching"]["count"] >= 1


def test_l0_outline_authoring_gap_surfaces(rollup):
    # rooftop is only in the OUTLINE arc and not in the contract -> authoring gap
    row = _by_id(rollup["demand"]["l0_backdrops"], "scene_id", "candidate__rooftop")
    assert row is not None
    assert row["source"] == "master_plan_outline"
    assert row["authoring_gap"] is True
    assert row["confidence"] == "outline"


def test_l3_object_coverage_and_candidate(rollup):
    kettle = _by_id(rollup["demand"]["l3_objects"], "object_id", "kettle")
    assert kettle is not None
    assert kettle["render_demand"] == 2
    assert kettle["present_byte_real"] == 0  # kettle.png absent
    # candle only in outline arc -> authoring-gap object row
    candle = _by_id(rollup["demand"]["l3_objects"], "object_id", "candidate__candle")
    assert candle is not None
    assert candle["authoring_gap"] is True
    assert candle["confidence"] == "outline"


def test_l2_pose_byte_real_coverage(rollup):
    hero = _by_id(rollup["demand"]["l2_character_poses"], "character_id", "hero_test")
    assert hero is not None
    assert hero["in_bank_contract"] is True
    assert hero["pose_render_demand"] == 2
    # only pose_a is >= floor; the 4-byte pose_b stub must NOT count
    assert hero["present_byte_real"] == 1
    assert hero["coverage_gap"] == 1
    assert hero["identity_lock"]["reference_sheet_present"] is True


def test_l2_outline_cast_authoring_gap(rollup):
    ids = {r["character_id"] for r in rollup["demand"]["l2_character_poses"]}
    # Yara (detailed) and Devon (outline) are proper names picked up mid-sentence
    assert "devon" in ids
    assert "yara" in ids
    devon = _by_id(rollup["demand"]["l2_character_poses"], "character_id", "devon")
    assert devon["in_bank_contract"] is False
    assert devon["authoring_gap"] is True
    assert devon["confidence"] == "outline"


def test_identity_lock_and_flagship(rollup):
    il = rollup["identity_lock_plan"]
    assert set(il["pulid_reference_sheets"]["required_for"]) >= {"hero_test", "devon", "yara"}
    assert il["pulid_reference_sheets"]["present"] == ["hero_test"]
    fl = il["flagship_lora"]
    assert fl["brand_on_flagship_list"] is True
    assert fl["brand_tier"] == "flagship"
    # one series-level authoring gap naming the protagonist candidate
    assert len(fl["authoring_gaps"]) == 1
    assert "hero_test" in fl["authoring_gaps"][0]


def test_gap_file_aggregation_reuses_lane10_format(rollup):
    gr = rollup["storyboard_gap_rollup"]
    assert gr["episodes_with_gap_files"] == ["ep_001"]
    assert gr["total_panels_with_gaps"] == 1
    assert gr["gap_asset_counts"] == {"L2:missing_pose": 1, "L3:kettle_missing": 1}


def test_coverage_summary_totals(rollup):
    cs = rollup["coverage_summary"]
    # present = 1 pose (pose_a) only
    assert cs["present_byte_real_total"] == 1
    assert cs["required_render_demand_total"] == cs["present_byte_real_total"] + cs["coverage_gap_total"]
    assert cs["byte_floor"] == 50_000


def test_render_queue_estimate(rollup):
    rq = rollup["render_queue_estimate"]
    assert rq["total_assets_to_render"] == sum(v["to_render"] for v in rq["by_class"].values())
    assert rq["gpu_cost_usd_est"] >= 0
    assert "per-asset" in rq["method"]


def test_mutation_new_outline_reference_adds_gap_row(tmp_path: Path):
    """A control plan whose outline arc references nothing new vs a mutated plan
    that references a new backdrop+cast: the mutation surfaces fresh authoring
    gaps the control does not have (the 'unknown reference -> FAIL row' guarantee)."""
    control_mp = _build_fixture(tmp_path / "ctl", outline_premise="A quiet continuation of the same kitchen.")
    control = gen.series_demand_rollup(control_mp, repo_root=tmp_path / "ctl")
    ctl_scene_ids = {r["scene_id"] for r in control["demand"]["l0_backdrops"]}
    ctl_cast = {r["character_id"] for r in control["demand"]["l2_character_poses"]}

    mut_mp = _build_fixture(tmp_path / "mut", outline_premise="A subway platform, watched by Priya at dusk.")
    mut = gen.series_demand_rollup(mut_mp, repo_root=tmp_path / "mut")
    mut_scene_ids = {r["scene_id"] for r in mut["demand"]["l0_backdrops"]}
    mut_cast = {r["character_id"] for r in mut["demand"]["l2_character_poses"]}

    # the unknown backdrop and the unknown cast member surface only in the mutation
    assert "candidate__subway" in mut_scene_ids and "candidate__subway" not in ctl_scene_ids
    assert "priya" in mut_cast and "priya" not in ctl_cast


def test_chapter_stub_mode_unchanged(tmp_path: Path, monkeypatch):
    """The original --chapter-script stub path still writes 3 inventory files
    with the pre-existing shape (inventory EXTENDS, never regresses)."""
    monkeypatch.setattr(gen, "REPO", tmp_path)
    script = tmp_path / "ep_001.yaml"
    script.write_text(yaml.safe_dump({
        "series_id": "stub_series", "brand_id": "stub_brand", "genre": "iyashikei",
        "pages": [{"panels": [
            {"scene": "A quiet kitchen table with a cup and a hand resting", "dialogue_lines": ["hi"]},
            {"scene": "A phone on the bedside table lights up with a notification"},
        ]}],
    }))
    written = gen.generate_chapter_stub(script)
    names = {p.name for p in written}
    assert names == {"scene_inventory.yaml", "object_inventory.yaml", "character_pose_inventory.yaml"}
    doc = yaml.safe_load((tmp_path / "artifacts" / "manga" / "stub_series"
                          / "bank_contracts" / "scene_inventory.yaml").read_text())
    assert doc["m5_prep"] is True
    assert doc["scenes"][0]["status"] == "specced_awaiting_gpu"


def test_real_golden_master_plan_rollup(tmp_path: Path):
    """The real Lane 06 golden master plan (on origin/main) rolls up and validates."""
    mp = REPO / ("artifacts/manga/series_master_plans/"
                 "stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying.master_plan.yaml")
    if not mp.is_file():
        pytest.skip("golden master plan not present in this checkout")
    doc = gen.series_demand_rollup(mp, repo_root=REPO)
    jsonschema.Draft202012Validator(SCHEMA).validate(doc)
    assert doc["series_id"] == "stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying"
    assert doc["episode_horizon"] == 100
    assert doc["identity_lock_plan"]["flagship_lora"]["brand_on_flagship_list"] is True
    ids = {r["character_id"] for r in doc["demand"]["l2_character_poses"]}
    assert {"mira_aoki", "dr_morimoto"} <= ids
