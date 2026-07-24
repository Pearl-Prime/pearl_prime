"""Tests for the compiled per-genre craft checklists + GATE_CRAFT wiring (Lane 07).

Mutation-proofed: a checklist-conformant script PASSes the craft gate; a script
missing must-item evidence, or carrying a failure-mode signal, FAILs it. A gate
that stays green under those mutations would not be accepted.
"""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import pytest
import yaml

from phoenix_v4.manga.modern_reader_context import canonical_genre_ids
from phoenix_v4.manga.qc.gate_registry import load_gate_registry
from phoenix_v4.manga.story_quality import (
    check_genre_craft_checklist,
    evaluate_story_excellence,
)

REPO = Path(__file__).resolve().parents[2]
CRAFT = REPO / "config/manga/genre_craft_checklists.yaml"
MC = REPO / "config/manga/mc_endurance_checklists.yaml"
GATES = REPO / "config/manga/story_excellence_gates.yaml"
GATE_PY = REPO / "phoenix_v4/manga/story_quality/excellence_gate.py"
FIX = REPO / "tests/fixtures/manga/genre_craft"
EXCELLENCE_FIX = REPO / "tests/fixtures/manga/story_excellence"

GATE_CRAFT = "MANGA.STORY.GENRE_CRAFT_CHECKLIST"


def _load(p: Path) -> dict:
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


@pytest.fixture(scope="module")
def craft_cfg() -> dict:
    return _load(CRAFT)


@pytest.fixture(scope="module")
def mc_cfg() -> dict:
    return _load(MC)


# ── config integrity ──────────────────────────────────────────────────────

def test_craft_keyspace_is_subset_of_canonical(craft_cfg):
    canonical = set(canonical_genre_ids())
    genres = set((craft_cfg.get("genres") or {}).keys())
    assert genres, "no genre blocks authored yet"
    stray = genres - canonical
    assert not stray, f"craft genres not in canonical_genre_list: {sorted(stray)}"


def test_all_canonical_genres_have_a_craft_block(craft_cfg):
    """Scale acceptance: every canonical genre carries a compiled checklist."""
    canonical = set(canonical_genre_ids())
    genres = set((craft_cfg.get("genres") or {}).keys())
    missing = canonical - genres
    assert not missing, f"canonical genres missing a craft block: {sorted(missing)}"


def test_every_block_has_required_sections_and_valid_sources(craft_cfg, mc_cfg):
    mc_families = set((mc_cfg.get("families") or {}).keys())
    for gid, block in (craft_cfg.get("genres") or {}).items():
        assert isinstance(block, dict), gid
        # bible file must exist on disk (no dangling authority)
        bible = block.get("bible")
        assert bible, f"{gid}: missing bible"
        assert (REPO / bible).is_file(), f"{gid}: bible not found: {bible}"

        must = block.get("story_elements_must") or []
        assert must, f"{gid}: no story_elements_must"
        for it in must:
            assert it.get("item"), f"{gid}: must-item missing text"
            assert it.get("evidence_any"), f"{gid}: must-item missing evidence_any: {it.get('item')}"
            _assert_source_resolves(gid, it.get("source"))

        for it in block.get("story_elements_should") or []:
            _assert_source_resolves(gid, it.get("source"))

        fms = block.get("failure_modes") or []
        assert fms, f"{gid}: no failure_modes"
        for fm in fms:
            assert fm.get("signal_any"), f"{gid}: failure_mode missing signal_any: {fm.get('item')}"
            _assert_source_resolves(gid, fm.get("source"))

        for it in block.get("dialogue_rules") or []:
            _assert_source_resolves(gid, it.get("source"))
        for it in block.get("panel_grammar_items") or []:
            _assert_source_resolves(gid, it.get("source"))

        # mc_items reference must resolve by key (never restated)
        mc_ref = block.get("mc_items") or {}
        fam = mc_ref.get("family")
        assert fam in mc_families, f"{gid}: mc_items.family {fam!r} not an mc_endurance family"


def _assert_source_resolves(gid: str, source):
    assert source, f"{gid}: item missing source anchor"
    file_part = re.split(r"#", str(source), 1)[0]
    assert (REPO / file_part).is_file(), f"{gid}: source anchor file missing: {source}"


# ── wiring ────────────────────────────────────────────────────────────────

def test_mc_endurance_is_wired_not_unwired():
    mc = _load(MC)
    assert mc.get("status") != "unwired", "mc_endurance_checklists.yaml still status: unwired"
    # the wiring gate keys off the stem appearing in a non-test consumer
    assert "mc_endurance_checklists" in GATE_PY.read_text(encoding="utf-8")


def test_gate_registry_has_craft_gate():
    ids = {g.gate_id for g in load_gate_registry()}
    assert GATE_CRAFT in ids


def test_story_excellence_gates_references_craft_config():
    cfg = _load(GATES)
    gc = cfg.get("genre_craft") or {}
    assert gc.get("checklist_file") == "config/manga/genre_craft_checklists.yaml"
    assert gc.get("mc_endurance_file") == "config/manga/mc_endurance_checklists.yaml"
    assert 0.0 < float(gc.get("must_coverage_floor")) <= 1.0


# ── craft gate: PASS + mutation FAILs (mutation-proof) ────────────────────

def _smoke_script() -> dict:
    return json.loads(
        (FIX / "supernatural_everyday_pass" / "chapter_script_writer_handoff.json").read_text()
    )


def test_craft_gate_pass_on_conformant_script():
    g = check_genre_craft_checklist(_smoke_script(), genre="supernatural_everyday", repo_root=REPO)
    assert g["gate_id"] == GATE_CRAFT
    assert g["status"] == "PASS", g
    assert g["score"] == 100
    # mc_endurance items are surfaced (proves the by-key binding is live)
    assert any("mc_endurance" in (e.get("path") or "") for e in g["evidence"]), g["evidence"]


def test_craft_gate_blocks_when_must_item_evidence_removed():
    # Replace all panel text with bland content that carries none of the must-item
    # evidence tokens -> coverage drops below floor -> BLOCK.
    mutated = {
        "genre_id": "supernatural_everyday",
        "pages": [
            {"page_number": 1, "panels": [
                {"scene": "A person walks into a house.", "narration": "It was a normal day."},
                {"scene": "They chat about the weather.", "dialogue": [{"speaker": "a", "text": "Nice out today."}]},
            ]},
        ],
    }
    g = check_genre_craft_checklist(mutated, genre="supernatural_everyday", repo_root=REPO)
    assert g["status"] == "BLOCKED", g
    assert any(i["code"] == "genre_craft_must_items_uncovered" for i in g["issues"]), g["issues"]


def test_craft_gate_blocks_when_failure_mode_signal_present():
    mutated = _smoke_script()
    mutated["pages"][0]["panels"][0]["scene"] += (
        " Then a jump scare — the monster attack begins as the spirit's power level rises."
    )
    g = check_genre_craft_checklist(mutated, genre="supernatural_everyday", repo_root=REPO)
    assert g["status"] == "BLOCKED", g
    assert any(i["code"] == "genre_craft_failure_mode_present" for i in g["issues"]), g["issues"]


def test_craft_gate_noop_pass_for_ungoverned_genre():
    # A genre with no checklist block yet must be a no-op PASS (never a crash).
    g = check_genre_craft_checklist({"pages": []}, genre="not_a_real_genre", repo_root=REPO)
    assert g["status"] == "PASS", g


# ── end-to-end: craft gate integrated into evaluate_story_excellence ──────

def _existing_pass_pair(name: str):
    d = EXCELLENCE_FIX / "pass" / name
    story = json.loads((d / "story_architecture_handoff.json").read_text())
    script = json.loads((d / "chapter_script_writer_handoff.json").read_text())
    return story, script


@pytest.mark.parametrize("name,genre", [
    ("dark_fantasy_ja_jp_genz", "dark_fantasy"),
    ("healing_ja_jp_genz", "healing"),
])
def test_end_to_end_pass_fixture_still_passes_with_craft_gate(name, genre):
    """Regression: existing full-pipeline pass fixtures stay PASS once GATE_CRAFT
    is authored for their genre (calibration anchor)."""
    if genre not in (_load(CRAFT).get("genres") or {}):
        pytest.skip(f"{genre} craft block not authored yet")
    story, script = _existing_pass_pair(name)
    report = evaluate_story_excellence(
        story_handoff=story, writer_handoff=script, production=True, repo_root=REPO
    )
    craft = next(g for g in report["gates"] if g["gate_id"] == GATE_CRAFT)
    assert craft["status"] == "PASS", craft
    assert report["status"] == "PASS", report


def test_end_to_end_failure_mode_injection_blocks_full_report():
    """Inject a genre failure-mode phrase into a passing fixture -> full report BLOCKS
    with GATE_CRAFT among the failed gates (real-pipeline mutation proof)."""
    genre = "dark_fantasy"
    if genre not in (_load(CRAFT).get("genres") or {}):
        pytest.skip("dark_fantasy craft block not authored yet")
    story, script = _existing_pass_pair("dark_fantasy_ja_jp_genz")
    block = (_load(CRAFT).get("genres") or {})[genre]
    phrase = block["failure_modes"][0]["signal_any"][0]
    mutated = copy.deepcopy(script)
    # append the defect phrase into the first panel's action
    p0 = mutated["pages"][0]["panels"][0]
    p0["action"] = (p0.get("action") or "") + f" {phrase}."
    report = evaluate_story_excellence(
        story_handoff=story, writer_handoff=mutated, production=True, repo_root=REPO
    )
    failed = {g["gate_id"] for g in report["gates"] if g["status"] == "BLOCKED"}
    assert GATE_CRAFT in failed, failed
    assert report["status"] == "BLOCKED", report


# ── storyboard advisory sub-check (non-blocking) ──────────────────────────

def test_storyboard_advisory_flags_missing_panel_grammar():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "cmas", str(REPO / "scripts/ci/check_manga_arc_storyboard.py")
    )
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)

    bare = {
        "genre_id": "supernatural_mystery",  # alias -> supernatural_everyday
        "panels": [{"framing": "MS", "story_move": "she opens the door", "visual_proof": "door opens"}],
        "genre_cadence": [], "page_turn_promises": [],
    }
    notes = m.advisory_panel_grammar(bare, repo_root=REPO)
    assert notes, "expected advisory notes for a plan with no panel-grammar signals"

    conformant = {
        "genre_id": "supernatural_everyday",
        "panels": [
            {"framing": "threshold-shot", "story_move": "spirit_present at torii, fog",
             "visual_proof": "silence_flag true, wordless", "beat_role": "encounter_sign"},
            {"framing": "CU", "story_move": "ritual release", "visual_proof": "aftermath, silent",
             "beat_role": "aftermath"},
        ],
        "genre_cadence": ["investigation"], "page_turn_promises": [],
    }
    assert m.advisory_panel_grammar(conformant, repo_root=REPO) == []
