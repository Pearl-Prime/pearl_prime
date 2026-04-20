"""Tests for MDLG-01 through MDLG-05 EI dialogue gates + story strategy loader."""

from __future__ import annotations

from typing import Any

import pytest

from phoenix_v4.quality.ei_v2.manga_dialogue_gates import (
    gate_dialogue_engagement,
    gate_somatic_precision,
    gate_word_economy,
    gate_dialogue_uniqueness,
    gate_dialogue_cohesion,
    run_manga_dialogue_gates,
)
from phoenix_v4.manga.story_strategy_loader import (
    load_story_strategy,
    select_layer_variants,
    list_available_genres,
    get_combinatorial_count,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _script(texts: list[str], emotional_job: str = "") -> dict:
    """Build a minimal chapter_script with a list of dialogue text strings."""
    return {
        "emotional_job": emotional_job,
        "pages": [
            {
                "page_number": 1,
                "panels": [
                    {"panel_id": f"p{i:02d}", "dialogue": [t]}
                    for i, t in enumerate(texts, 1)
                ],
            }
        ],
    }


def _lettering(dialogue_lines: list[dict[str, Any]]) -> dict:
    """Build a minimal lettering_spec_v2 from a flat list of dialogue_line dicts."""
    return {
        "schema_version": "2.0.0",
        "artifact_type": "lettering_spec",
        "lettering_panels": [
            {
                "panel_id": f"p{i:02d}",
                "silence_confirmed": False,
                "dialogue_lines": [dl],
                "sfx": [],
                "narrator_caption": None,
            }
            for i, dl in enumerate(dialogue_lines, 1)
        ],
    }


def _make_dl(text: str, emotion: str = "neutral", intensity: str = "normal",
             bubble_style: str = "round_normal", position_hint: str = "top_right",
             tail_style: str = "pointer") -> dict:
    return {
        "speaker": "hero",
        "text": text,
        "emotion": emotion,
        "intensity": intensity,
        "bubble_style": bubble_style,
        "position_hint": position_hint,
        "tail_style": tail_style,
        "font_override": None,
    }


# ---------------------------------------------------------------------------
# MDLG-01: Engagement
# ---------------------------------------------------------------------------

class TestGateEngagement:
    def test_question_gives_high_score(self):
        script = _script(["Why is this happening?"])
        lettering = _lettering([_make_dl("Why is this happening?")])
        result, issue = gate_dialogue_engagement(script, lettering, "shonen")
        assert result.score > 0.60
        assert result.status == "PASS"
        assert issue is None

    def test_summarising_text_lowers_score(self):
        script = _script(["As you know, the enemy is strong."])
        lettering = _lettering([_make_dl("As you know, the enemy is strong.")])
        result, issue = gate_dialogue_engagement(script, lettering, "shonen")
        assert result.score < 0.90  # penalised

    def test_empty_dialogue_passes(self):
        script = _script([])
        lettering = {"schema_version": "2.0.0", "artifact_type": "lettering_spec",
                     "lettering_panels": []}
        result, issue = gate_dialogue_engagement(script, lettering, "shonen")
        assert result.status == "PASS"
        assert result.score == 1.0
        assert issue is None

    def test_suspense_ellipsis_scores_well(self):
        script = _script(["I have to... I have to keep going..."])
        lettering = _lettering([_make_dl("I have to... I have to keep going...")])
        result, _ = gate_dialogue_engagement(script, lettering, "shonen")
        assert result.score >= 0.65


# ---------------------------------------------------------------------------
# MDLG-02: Somatic precision
# ---------------------------------------------------------------------------

class TestGateSomatic:
    def test_inactive_when_no_somatic_trigger(self):
        script = _script(["Good morning!"])
        lettering = _lettering([_make_dl("Good morning!", emotion="joy")])
        result, issue = gate_somatic_precision(script, lettering, "shonen")
        assert result.score == 1.0
        assert issue is None

    def test_active_with_fear_emotion(self):
        # fear triggers gate — text has no somatic words → low score
        script = _script(["This is scary!"])
        lettering = _lettering([_make_dl("This is scary!", emotion="fear")])
        result, issue = gate_somatic_precision(script, lettering, "shonen")
        assert result.score < 1.0  # activated

    def test_somatic_vocab_improves_score(self):
        # Use exact vocab items from shonen list: "fists", "blood", "adrenaline"
        script = _script(["My fists clench. Blood pounds. Adrenaline surges."])
        lettering = _lettering([
            _make_dl("My fists clench. Blood pounds. Adrenaline surges.",
                     emotion="determination", intensity="shouting")
        ])
        result, _ = gate_somatic_precision(script, lettering, "shonen")
        assert result.score >= 0.70  # 3 matches × 0.20 + 0.30 = 0.90

    def test_seinen_somatic_vocab(self):
        # Use exact seinen vocab: "hollow", "numbness", "cold"
        script = _script(["A hollow feeling. Cold numbness spreading."])
        lettering = _lettering([
            _make_dl("A hollow feeling. Cold numbness spreading.", emotion="grief")
        ])
        result, _ = gate_somatic_precision(script, lettering, "seinen")
        assert result.score >= 0.50  # 2+ matches × 0.20 + 0.30 = 0.70


# ---------------------------------------------------------------------------
# MDLG-03: Word economy
# ---------------------------------------------------------------------------

class TestGateWordEconomy:
    def test_short_bubble_passes(self):
        script = _script(["Let's go!"])
        lettering = _lettering([_make_dl("Let's go!")])
        result, issue = gate_word_economy(script, lettering, "shonen")
        assert result.status == "PASS"
        assert issue is None

    def test_over_block_ceiling_fails(self):
        # shonen block ceiling = 25 words
        long_text = " ".join(["word"] * 30)
        script = _script([long_text])
        lettering = _lettering([_make_dl(long_text)])
        result, issue = gate_word_economy(script, lettering, "shonen")
        assert result.status == "FAIL"
        assert result.score == 0.0
        assert issue is not None
        assert issue["severity"] == "BLOCKER"

    def test_seinen_allows_longer_bubbles(self):
        # seinen block ceiling = 70 words — 50 words should be fine
        text = " ".join(["word"] * 50)
        script = _script([text])
        lettering = _lettering([_make_dl(text)])
        result, _ = gate_word_economy(script, lettering, "seinen")
        assert result.status in ("PASS", "WARN")  # 50 < 70 ceiling

    def test_horror_tight_ceiling(self):
        # horror block ceiling = 20 words — 22 words blocks
        text = " ".join(["dread"] * 22)
        script = _script([text])
        lettering = _lettering([_make_dl(text)])
        result, issue = gate_word_economy(script, lettering, "horror")
        assert result.score == 0.0  # block
        assert issue is not None

    def test_empty_dialogue_passes(self):
        script = _script([])
        lettering = {"schema_version": "2.0.0", "artifact_type": "lettering_spec",
                     "lettering_panels": []}
        result, _ = gate_word_economy(script, lettering, "shonen")
        assert result.status == "PASS"


# ---------------------------------------------------------------------------
# MDLG-04: Uniqueness
# ---------------------------------------------------------------------------

class TestGateUniqueness:
    def test_no_history_passes(self):
        script = _script(["I won't give up!"])
        lettering = _lettering([_make_dl("I won't give up!")])
        result, issue = gate_dialogue_uniqueness(script, lettering, series_history=None)
        assert result.status == "PASS"
        assert issue is None

    def test_exact_repeat_blocks(self):
        text = "I won't give up!"
        script = _script([text])
        lettering = _lettering([_make_dl(text)])
        result, issue = gate_dialogue_uniqueness(script, lettering, series_history=[text])
        assert result.score == 0.0
        assert issue is not None
        assert issue["severity"] == "BLOCKER"

    def test_sufficiently_different_text_passes(self):
        script = _script(["The path forward is clear."])
        lettering = _lettering([_make_dl("The path forward is clear.")])
        history = ["The way back is lost.", "She stood alone.", "Rain fell."]
        result, issue = gate_dialogue_uniqueness(script, lettering, series_history=history)
        assert result.status in ("PASS", "WARN")
        # Should not block
        if issue:
            assert issue["severity"] != "BLOCKER"

    def test_case_insensitive_exact_match(self):
        script = _script(["I WON'T GIVE UP!"])
        lettering = _lettering([_make_dl("I WON'T GIVE UP!")])
        result, issue = gate_dialogue_uniqueness(
            script, lettering, series_history=["i won't give up!"]
        )
        assert result.score == 0.0


# ---------------------------------------------------------------------------
# MDLG-05: Cohesion
# ---------------------------------------------------------------------------

class TestGateCohesion:
    def test_no_emotional_job_passes(self):
        script = _script(["Let's go!"])
        lettering = _lettering([_make_dl("Let's go!")])
        result, issue = gate_dialogue_cohesion(script, lettering, chapter_contract=None)
        assert result.status == "PASS"

    def test_shame_engine_reinforced(self):
        # Use multiple shame patterns: "not good enough", "hiding", "worthless"
        script = _script(["I'm not good enough. I've been hiding. Worthless."], "shame")
        lettering = _lettering([_make_dl(
            "I'm not good enough. I've been hiding. Worthless.", emotion="shame")])
        result, _ = gate_dialogue_cohesion(
            script, lettering, chapter_contract={"emotional_job": "shame"}
        )
        # 3 matches × 0.15 + 0.35 = 0.80
        assert result.score >= 0.60

    def test_shame_engine_contradicted(self):
        script = _script(["I've got this! No problem at all."], "shame")
        lettering = _lettering([_make_dl("I've got this! No problem at all.")])
        result, issue = gate_dialogue_cohesion(
            script, lettering, chapter_contract={"emotional_job": "shame"}
        )
        # Forbidden patterns for shame: "confident", "i've got this", "no problem"
        assert result.score < 0.70

    def test_grief_engine_with_past_tense(self):
        # Use multiple grief patterns: "miss", "they were", "lost", "gone"
        script = _script(["I miss them. They were everything. Lost and gone."], "grief")
        lettering = _lettering([_make_dl(
            "I miss them. They were everything. Lost and gone.", emotion="grief")])
        result, _ = gate_dialogue_cohesion(
            script, lettering, chapter_contract={"emotional_job": "grief"}
        )
        # 4 matches × 0.15 + 0.35 = 0.95
        assert result.score >= 0.65


# ---------------------------------------------------------------------------
# run_manga_dialogue_gates — composite
# ---------------------------------------------------------------------------

class TestRunMangaDialogueGates:
    def test_returns_expected_structure(self):
        script = _script(["Are you ready? The battle begins now!"])
        lettering = _lettering([_make_dl("Are you ready? The battle begins now!",
                                          emotion="determination", intensity="excited")])
        report = run_manga_dialogue_gates(script, lettering, genre="shonen")
        assert "mdlg_score" in report
        assert "gates" in report
        assert "issues" in report
        assert "passed" in report
        gate_ids = {g["id"] for g in report["gates"]}
        assert "MDLG-COMPOSITE" in gate_ids
        assert len(report["gates"]) == 6  # 5 gates + composite

    def test_all_gates_present(self):
        script = _script(["Why won't you stop?"])
        lettering = _lettering([_make_dl("Why won't you stop?", emotion="fear")])
        report = run_manga_dialogue_gates(script, lettering, genre="shonen")
        gate_ids = {g["id"] for g in report["gates"]}
        assert "MDLG-01" in gate_ids
        assert "MDLG-02" in gate_ids
        assert "MDLG-03" in gate_ids
        assert "MDLG-04" in gate_ids
        assert "MDLG-05" in gate_ids

    def test_word_economy_block_fails_composite(self):
        long_text = " ".join(["word"] * 30)  # over shonen ceiling
        script = _script([long_text])
        lettering = _lettering([_make_dl(long_text)])
        report = run_manga_dialogue_gates(script, lettering, genre="shonen")
        assert report["passed"] is False
        assert any(i["severity"] == "BLOCKER" for i in report["issues"])

    def test_score_is_float_between_0_and_1(self):
        script = _script(["Let's fight!"])
        lettering = _lettering([_make_dl("Let's fight!", intensity="excited")])
        report = run_manga_dialogue_gates(script, lettering)
        assert 0.0 <= report["mdlg_score"] <= 1.0


# ---------------------------------------------------------------------------
# Story strategy loader
# ---------------------------------------------------------------------------

class TestStoryStrategyLoader:
    def test_list_available_genres_returns_at_least_three(self):
        genres = list_available_genres()
        assert len(genres) >= 3
        assert "shonen" in genres or "seinen" in genres or "shojo" in genres

    def test_load_shonen_strategy(self):
        result = load_story_strategy("shonen", series_id="test", arc_id="arc1")
        assert "strategy_id" in result
        assert "strategy" in result
        assert result["genre"] == "shonen"
        assert len(result["available_strategies"]) >= 5

    def test_load_shojo_strategy(self):
        result = load_story_strategy("shojo", series_id="test", arc_id="arc1")
        assert result["genre"] == "shojo"
        assert "strategy" in result

    def test_load_seinen_strategy(self):
        result = load_story_strategy("seinen", series_id="test", arc_id="arc1")
        assert result["genre"] == "seinen"

    def test_deterministic_selection(self):
        """Same inputs always produce same strategy."""
        r1 = load_story_strategy("shonen", series_id="my_series", arc_id="arc_001")
        r2 = load_story_strategy("shonen", series_id="my_series", arc_id="arc_001")
        assert r1["strategy_id"] == r2["strategy_id"]

    def test_different_seeds_may_produce_different_strategies(self):
        """Different series_id should produce different strategies across many tries."""
        selected = set()
        for i in range(20):
            r = load_story_strategy("shonen", series_id=f"series_{i}", arc_id="arc1")
            selected.add(r["strategy_id"])
        # Should pick more than 1 distinct strategy out of 20 tries
        assert len(selected) > 1

    def test_explicit_strategy_id_works(self):
        # Actual keys are strategy_01 … strategy_05 (WS3 agent used numeric keys)
        result = load_story_strategy(
            "shonen",
            strategy_id="strategy_01",
            series_id="test",
            arc_id="arc1",
        )
        assert result["strategy_id"] == "strategy_01"

    def test_missing_genre_returns_empty(self):
        result = load_story_strategy("nonexistent_genre_xyz")
        assert result == {}

    def test_invalid_strategy_id_raises(self):
        with pytest.raises(KeyError):
            load_story_strategy("shonen", strategy_id="invalid_strategy_xyz")

    def test_select_layer_variants_returns_5_layers(self):
        strategy_data = load_story_strategy("shonen", series_id="s", arc_id="a")
        if not strategy_data:
            pytest.skip("shonen strategies not available")
        layers = select_layer_variants(strategy_data, series_id="s", arc_id="a", genre="shonen")
        assert len(layers) == 5
        for i in range(1, 6):
            assert f"layer_{i}" in layers

    def test_layer_selection_is_deterministic(self):
        strategy_data = load_story_strategy("shonen", series_id="s", arc_id="a")
        if not strategy_data:
            pytest.skip("shonen strategies not available")
        l1 = select_layer_variants(strategy_data, series_id="s", arc_id="a", genre="shonen")
        l2 = select_layer_variants(strategy_data, series_id="s", arc_id="a", genre="shonen")
        assert l1 == l2

    def test_combinatorial_count_shonen(self):
        count = get_combinatorial_count("shonen")
        assert count > 200  # should be 1215 per spec

    def test_cjk_genre_name_normalised(self):
        """shōnen and shonen should map to same strategies."""
        r1 = load_story_strategy("shōnen", series_id="s", arc_id="a")
        r2 = load_story_strategy("shonen", series_id="s", arc_id="a")
        assert r1.get("genre") == r2.get("genre")
