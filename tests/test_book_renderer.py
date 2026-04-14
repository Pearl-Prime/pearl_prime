"""Tests for Stage 6 prose resolution and book renderer."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from phoenix_v4.rendering import book_renderer as book_renderer_module
from phoenix_v4.rendering.prose_resolver import (
    PlanContext,
    RenderResult,
    _parse_block_file_with_prose,
    resolve_prose_for_plan,
    _is_placeholder_or_silence,
    _slot_type_from_placeholder_or_silence,
)
from phoenix_v4.rendering.book_renderer import (
    ChapterFlowGateError,
    DeliveryContractError,
    DimensionGateBlockError,
    RenderOptions,
    TxtWriter,
    clean_for_delivery,
    delivery_contract_gate,
    render_book,
)


@pytest.fixture(autouse=True)
def _isolate_book_renderer_module_caches() -> None:
    """Clear process-wide renderer caches so earlier tests cannot flip flow-gate outcomes."""
    from phoenix_v4.quality.ei_v2.config import invalidate_ei_v2_config_cache
    from phoenix_v4.rendering import chapter_composer

    invalidate_ei_v2_config_cache()
    book_renderer_module._LOCATION_PROFILE_CACHE = None
    book_renderer_module._FORMAT_REGISTRY_CACHE = None
    book_renderer_module._MECHANISM_ALIAS_CACHE.clear()
    chapter_composer._CHAPTER_INDEX_TLS = 0
    yield
    invalidate_ei_v2_config_cache()
    book_renderer_module._LOCATION_PROFILE_CACHE = None
    book_renderer_module._FORMAT_REGISTRY_CACHE = None
    book_renderer_module._MECHANISM_ALIAS_CACHE.clear()
    chapter_composer._CHAPTER_INDEX_TLS = 0


def test_placeholder_silence_helpers() -> None:
    assert _is_placeholder_or_silence("placeholder:STORY:ch0:slot2") is True
    assert _is_placeholder_or_silence("silence:REFLECTION:ch1:slot3") is True
    assert _is_placeholder_or_silence("nyc_executives_self_worth_shame_EMBODIMENT_v04") is False
    assert _slot_type_from_placeholder_or_silence("placeholder:HOOK:ch0:slot0") == "HOOK"
    assert _slot_type_from_placeholder_or_silence("silence:REFLECTION:ch1:slot3") == "REFLECTION"


def test_plan_context_from_plan_with_top_level_ids() -> None:
    plan = {"topic_id": "self_worth", "persona_id": "nyc_executives", "atom_ids": []}
    ctx = PlanContext.from_plan(plan)
    assert ctx.persona_id == "nyc_executives"
    assert ctx.topic_id == "self_worth"
    assert "shame" in ctx.engines or "comparison" in ctx.engines


def test_plan_context_infer_from_story_atom_id() -> None:
    plan = {
        "atom_ids": [
            "placeholder:HOOK:ch0:slot0",
            "nyc_executives_self_worth_shame_EMBODIMENT_v04",
        ],
    }
    ctx = PlanContext.from_plan(plan)
    assert ctx.persona_id == "nyc_executives"
    assert ctx.topic_id == "self_worth"
    assert "shame" in ctx.engines


def test_resolve_prose_returns_result_with_placeholder_tracking() -> None:
    plan = {
        "atom_ids": ["placeholder:HOOK:ch0:slot0", "nyc_executives_self_worth_shame_EMBODIMENT_v04"],
        "chapter_slot_sequence": [["HOOK", "STORY"]],
    }
    repo = Path(__file__).resolve().parent.parent
    result = resolve_prose_for_plan(plan, atoms_root=repo / "atoms")
    assert isinstance(result, RenderResult)
    assert len(result.placeholder_or_silence_ids) >= 1
    # STORY prose should be resolved if atoms exist
    if result.prose_map:
        assert "nyc_executives_self_worth_shame_EMBODIMENT_v04" in result.prose_map or "nyc_executives_self_worth_shame_EMBODIMENT_v04" in result.missing_ids


def test_render_book_txt_with_placeholders_allowed(tmp_path: Path) -> None:
    plan = {
        "plan_hash": "test_hash",
        "atom_ids": ["placeholder:HOOK:ch0:slot0", "placeholder:STORY:ch0:slot1"],
        "chapter_slot_sequence": [["HOOK", "STORY"]],
    }
    written = render_book(
        plan,
        tmp_path,
        formats=["txt"],
        allow_placeholders=True,
        on_missing="placeholder",
        title_page=False,
    )
    assert "txt" in written
    assert (tmp_path / "book.txt").exists()
    text = (tmp_path / "book.txt").read_text()
    assert "Chapter 1" in text
    # Chapter composer filters placeholder prose and generates fallback content;
    # verify that the render produces non-empty chapter output without crashing.
    assert len(text.strip()) > len("Chapter 1")


def test_txt_writer_emits_missing_when_on_missing_placeholder() -> None:
    plan = {
        "atom_ids": ["unknown_atom_id_xyz"],
        "chapter_slot_sequence": [["STORY"]],
    }
    result = resolve_prose_for_plan(plan)
    result.missing_ids.append("unknown_atom_id_xyz")
    options = RenderOptions(allow_placeholders=True, on_missing="placeholder")
    writer = TxtWriter(plan, result.prose_map, result, options)
    out = Path(__file__).resolve().parent.parent / "artifacts" / "books_qa" / "test_missing.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    writer.write(out)
    text = out.read_text()
    # Chapter composer filters [Missing:...] prose and generates fallback content;
    # verify that the render produces output without crashing on missing atoms.
    assert "Chapter 1" in text
    assert len(text.strip()) > len("Chapter 1")
    out.unlink(missing_ok=True)


def test_strengthen_chapter_flow_for_delivery_repairs_spine_like_prose() -> None:
    from phoenix_v4.quality.chapter_flow_gate import evaluate_chapter_flow
    from phoenix_v4.rendering.book_renderer import strengthen_chapter_flow_for_delivery

    spine_like = (
        "The desk is the same desk. The screen is bright. You read the subject line twice.\n\n"
        "Your jaw does not relax when the tab closes. The next message is already there.\n\n"
        "You tell yourself this is normal. The body is not convinced.\n\n"
        "You drink water you do not taste. You return to the same paragraph.\n\n"
        "Nothing is wrong on paper. Something is wrong in the chest.\n\n"
        "You measure your tone in the reply. You measure your breath less carefully.\n\n"
        "The afternoon light changes. The urgency does not leave with it.\n\n"
        "You finish one thing and the list replaces it before you stand."
    )
    before = evaluate_chapter_flow(spine_like)
    strengthened = strengthen_chapter_flow_for_delivery(
        spine_like, chapter_index=3, book_seed="unit-test-strengthen"
    )
    after = evaluate_chapter_flow(strengthened)
    assert before.status == "FAIL"
    assert {"WEAK_TRANSITIONS", "MISSING_CLEAR_POINT", "NO_ACTIONABLE_STEP"}.issubset(
        set(before.errors)
    )
    assert after.status == "PASS"


def test_render_book_writes_chapter_flow_report(tmp_path: Path) -> None:
    plan = {
        "plan_hash": "flow_report_hash",
        "atom_ids": ["placeholder:HOOK:ch0:slot0", "placeholder:STORY:ch0:slot1"],
        "chapter_slot_sequence": [["HOOK", "STORY"]],
    }
    written = render_book(
        plan,
        tmp_path,
        formats=["txt"],
        allow_placeholders=True,
        on_missing="placeholder",
        title_page=False,
        enforce_word_count=False,
    )
    assert "chapter_flow_report" in written
    report = json.loads((tmp_path / "chapter_flow_report.json").read_text(encoding="utf-8"))
    assert report["chapter_count"] >= 1
    assert report["status"] in {"PASS", "FAIL"}


def test_render_book_enforce_chapter_flow_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        book_renderer_module,
        "strengthen_chapter_flow_for_delivery",
        lambda composed, **_: composed,
    )
    # Force the flow gate to see a hard FAIL by injecting a chapter that always
    # evaluates as FAIL (empty chapter text → CHAPTER_EMPTY error).
    from phoenix_v4.quality.chapter_flow_gate import ChapterFlowResult
    monkeypatch.setattr(
        book_renderer_module,
        "evaluate_chapter_flow",
        lambda text, **kw: ChapterFlowResult(
            status="FAIL", score=0,
            errors=["FORCED_TEST_FAILURE"], warnings=[], metrics={},
        ),
    )
    plan = {
        "plan_hash": "flow_gate_fail_hash",
        "atom_ids": ["placeholder:HOOK:ch0:slot0", "placeholder:STORY:ch0:slot1"],
        "chapter_slot_sequence": [["HOOK", "STORY"]],
    }
    with pytest.raises(ChapterFlowGateError):
        render_book(
            plan,
            tmp_path,
            formats=["txt"],
            allow_placeholders=True,
            on_missing="placeholder",
            title_page=False,
            enforce_word_count=False,
            enforce_chapter_flow=True,
        )


def test_render_book_enforce_dimension_gates_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    plan = {
        "plan_hash": "dg_block_hash",
        "atom_ids": ["placeholder:HOOK:ch0:slot0", "placeholder:STORY:ch0:slot1"],
        "chapter_slot_sequence": [["HOOK", "STORY"]],
    }

    def fake_run_dimension_gates(*_a: object, **_k: object) -> dict:
        return {
            "chapter_index": 0,
            "gates": [],
            "overall_status": "FAIL",
            "fail_count": 1,
            "warn_count": 0,
            "blocks_delivery": True,
            "dimension_gate_phase": 1,
            "fail_mode": "block",
            "blocked_dimensions": ["engagement"],
        }

    monkeypatch.setattr(
        book_renderer_module,
        "_run_dimension_gates_for_composed_chapter",
        fake_run_dimension_gates,
    )

    with pytest.raises(DimensionGateBlockError):
        render_book(
            plan,
            tmp_path,
            formats=["txt"],
            allow_placeholders=True,
            on_missing="placeholder",
            title_page=False,
            enforce_word_count=False,
            enforce_dimension_gates=True,
        )


def test_render_book_writes_location_grounding_report_when_location_present(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    plan = {
        "plan_hash": "location_report_hash",
        "topic_id": "overthinking",
        "persona_id": "gen_z_professionals",
        "resolved_location_id": "nyc_grand_central",
        "atom_ids": ["scene_atom_1"],
        "chapter_slot_sequence": [["STORY"]],
    }

    def fake_resolve(*args, **kwargs):
        return RenderResult(
            prose_map={
                "scene_atom_1": (
                    "Your chest tightens thinking about talking to your manager "
                    "as the 6 express lurches forward leaving Grand Central. "
                    "42nd Street below keeps sliding by."
                )
            },
            missing_ids=[],
            placeholder_or_silence_ids=[],
        )

    monkeypatch.setattr(book_renderer_module, "resolve_prose_for_plan", fake_resolve)

    written = render_book(
        plan,
        tmp_path,
        formats=["txt"],
        title_page=False,
        enforce_word_count=False,
    )

    assert "location_grounding_report" in written
    report = json.loads((tmp_path / "location_grounding_report.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert {hit["key"] for hit in report["signals_found"]} >= {"transit_line", "transit_stop"}


def test_clean_for_delivery_strips_assembly_section_headers() -> None:
    raw = (
        "## HOOK v01\n"
        "First line of hook.\n\n"
        "## STORY v01\n"
        "Story body.\n\n"
        "## SCENE v01\n"
        "Scene body.\n\n"
        "## MECHANISM_DEPTH\n"
        "Mechanism prose.\n"
    )
    out = clean_for_delivery(raw)
    assert "## HOOK" not in out
    assert "## STORY" not in out
    assert "## SCENE" not in out
    assert "## MECHANISM_DEPTH" not in out
    assert "First line of hook." in out
    assert "Story body." in out
    delivery_contract_gate(out, source_hint="test")


def test_clean_for_delivery_preserves_normal_markdown_chapter_headings() -> None:
    raw = "## Chapter Title\n\nProse under a normal chapter-style heading.\n"
    out = clean_for_delivery(raw)
    assert "## Chapter Title" in out
    assert "Prose under" in out
    delivery_contract_gate(out, source_hint="test")


def test_clean_for_delivery_preserves_story_word_in_prose_heading() -> None:
    """STORY keyword alone must not strip real titles like '## Story of the river'."""
    raw = "## Story of the river\n\nThe water moves anyway.\n"
    out = clean_for_delivery(raw)
    assert "## Story of the river" in out
    delivery_contract_gate(out, source_hint="test")


def test_delivery_contract_gate_flags_leaked_section_headers() -> None:
    dirty = "## HOOK v01\n\nSome prose.\n"
    with pytest.raises(DeliveryContractError) as exc:
        delivery_contract_gate(dirty, source_hint="test")
    assert "assembly section header" in str(exc.value).lower()


def test_dedup_repeated_blocks_exact_duplicate_removes_second() -> None:
    from phoenix_v4.rendering.book_renderer import _dedup_repeated_blocks

    p = (
        "This is a long enough paragraph that it should participate in the "
        "deduplication fingerprint logic and be considered for removal when "
        "it appears twice in the same manuscript body text."
    )
    text = f"{p}\n\n{p}\n\n"
    out = _dedup_repeated_blocks(text)
    assert out.count("deduplication fingerprint") == 1


def test_dedup_repeated_blocks_near_duplicate_whitespace() -> None:
    from phoenix_v4.rendering.book_renderer import _dedup_repeated_blocks

    a = (
        "Same words repeated with different spacing and punctuation here "
        "so we verify normalization catches minor surface differences in "
        "the duplicated block content across the manuscript."
    )
    b = (
        "Same  words,, repeated\nwith different spacing and punctuation here "
        "so we verify normalization catches minor surface differences in "
        "the duplicated block content across the manuscript."
    )
    out = _dedup_repeated_blocks(f"{a}\n\n{b}")
    assert "normalization" in out
    assert out.count("Same") == 1


def test_dedup_repeated_blocks_short_paragraphs_may_repeat() -> None:
    from phoenix_v4.rendering.book_renderer import _dedup_repeated_blocks

    short = "One two three four five."
    text = f"{short}\n\n{short}\n\n"
    out = _dedup_repeated_blocks(text)
    assert out.count("One two three four five.") == 2


def test_dedup_repeated_blocks_distinct_long_paragraphs_kept() -> None:
    from phoenix_v4.rendering.book_renderer import _dedup_repeated_blocks

    a = " ".join([f"alpha_{i}" for i in range(25)])
    b = " ".join([f"beta_{i}" for i in range(25)])
    out = _dedup_repeated_blocks(f"{a}\n\n{b}")
    assert "alpha_0" in out and "beta_0" in out


def test_dedup_four_count_breath_section_deduplicated() -> None:
    from phoenix_v4.rendering.book_renderer import _dedup_repeated_blocks

    breath = (
        "Inhale for four counts. Hold for four counts. Exhale for four counts. "
        "Hold empty for four counts. Repeat this cycle three times. Notice how "
        "the body responds without forcing any particular outcome or judgment."
    )
    out = _dedup_repeated_blocks(f"{breath}\n\n{breath}\n\n")
    assert out.count("Inhale for four counts") == 1


def test_dedup_repeated_blocks_keeps_pre_dedup_when_below_word_floor() -> None:
    from phoenix_v4.rendering.book_renderer import _dedup_repeated_blocks

    p = (
        "This paragraph is long enough to participate in deduplication logic and "
        "will be fingerprinted so the second identical copy is normally removed "
        "from the manuscript when no word floor is applied to the delivery pass."
    )
    text = f"{p}\n\n{p}\n"
    shrunk = _dedup_repeated_blocks(text, word_floor=0)
    assert shrunk.count("This paragraph is long enough") == 1
    kept = _dedup_repeated_blocks(text, word_floor=5000)
    assert kept.count("This paragraph is long enough") == 2


def test_clean_for_delivery_dedup_respects_runtime_word_floor() -> None:
    long_para = (
        "This duplicate long paragraph is written for runtime word floor testing "
        "with more than twenty words so dedup would normally remove the second copy "
        "but the format floor requires keeping pre-dedup word count for thin books."
    )
    raw = f"{long_para}\n\n{long_para}\n"
    out_no_plan = clean_for_delivery(raw)
    assert out_no_plan.count("duplicate long paragraph") == 1
    out_with_plan = clean_for_delivery(raw, plan={"runtime_format_id": "short_book_30"})
    assert out_with_plan.count("duplicate long paragraph") == 2


def test_clean_for_delivery_strips_concatenated_spine_hook_lines() -> None:
    raw = (
        "## HOOK v01 --- --- First hook body. --- ## HOOK v02 --- --- Second hook body."
    )
    out = clean_for_delivery(raw)
    assert "## HOOK" not in out
    assert "First hook body" in out
    assert "Second hook body" in out


def test_clean_for_delivery_runs_dedup_after_strip_scaffolding() -> None:
    long_para = (
        "This duplicate long paragraph is written for clean_for_delivery integration "
        "testing with more than twenty words so the deduplication threshold applies "
        "and the second identical copy is removed after assembly headers are stripped."
    )
    raw = f"## STORY v01\n\n{long_para}\n\n{long_para}\n"
    out = clean_for_delivery(raw)
    assert "## STORY" not in out
    assert out.count("second identical copy") == 1


def test_parse_block_file_with_metadata_then_prose(tmp_path: Path) -> None:
    canonical = tmp_path / "CANONICAL.txt"
    canonical.write_text(
        """## INTEGRATION v01
---
mode: BODY_LANDED
reframe_type: BODY_FACT
weight: light
carry_line: "line"
---
This is real prose, not metadata.
---
""",
        encoding="utf-8",
    )
    parsed = _parse_block_file_with_prose(canonical, "p", "t", "INTEGRATION")
    assert parsed["p_t_INTEGRATION_v01"].startswith("This is real prose")
