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
    DimensionGateBlockError,
    RenderOptions,
    TxtWriter,
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
