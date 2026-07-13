from __future__ import annotations

from unittest.mock import MagicMock

from phoenix_v4.planning.pool_index import AtomEntry
from phoenix_v4.planning.slot_resolver import ResolverContext, resolve_slot
from phoenix_v4.quality.chapter_flow_gate import evaluate_chapter_flow, evaluate_chapter_flow_with_slots
from scripts.build_proof_chapter import build_chapter


def test_chapter_flow_gate_fails_on_artifacts_and_repetition() -> None:
    bad = """
I have noticed that this keeps happening.
I have noticed that this keeps happening.
---
[family: F4 voice_mode: guide mechanism_emphasis: automatic]
The room is quiet. {street_name} is below.
"""
    result = evaluate_chapter_flow(bad)
    assert result.status == "FAIL"
    assert "DELIVERY_ARTIFACT_PRESENT" in result.errors
    assert any(e.startswith("REPETITIVE_STEM:") for e in result.errors)


def test_proof_chapter_passes_flow_gate() -> None:
    chapter = build_chapter("test-seed-01")
    result = evaluate_chapter_flow(chapter)
    assert result.status == "PASS", result.errors
    assert result.score >= 80
    assert result.metrics["transition_hits"] >= 3
    assert result.metrics["thesis_hits"] >= 1


def test_zh_tw_flow_cues_are_recognized_without_english_crutches() -> None:
    chapter = """
這一章先把身體的警報放回正確的位置。
你可以注意胸口的緊縮，而不必立刻相信它。
重點是，焦慮不是人格缺陷，而是一套過度努力的保護系統。
這意味著，我們要練習的是辨認警報，而不是羞辱自己。
這就是為什麼第一個步驟不是逼自己冷靜，而是先命名正在發生的事。
換句話說，感覺可以很大，但它不需要替你做決定。
在實際操作中，你先停一下，讓腳掌碰到地面。
然後呼吸一次，把吐氣拉得比吸氣更長。
例如，當訊息跳出來時，你可以先說：這是警報。
因為身體正在預測危險，所以它會把小訊號放大。
你可以看見，代價不是一封訊息，而是整天都被掃描佔據。
請記住，你的身體不是問題；問題在於警報被迫工作太久。
接下來，選擇一個最小的行動，寫下一句真實的話。
從這裡開始，練習不是完美，而是一次又一次把自己帶回來。
"""
    result = evaluate_chapter_flow(chapter, locale="zh-TW")
    assert result.status == "PASS", result.errors
    assert result.metrics["locale_family"] == "zh"
    assert result.metrics["transition_hits"] >= 3
    assert result.metrics["thesis_hits"] >= 1
    assert result.metrics["action_hits"] >= 1


def test_chapter_flow_with_slots_requires_takeaway_and_thread_when_present() -> None:
    # When TAKEAWAY or THREAD slot is present but segment is empty, gate fails with TAKEAWAY_EMPTY / THREAD_EMPTY
    slots = ["HOOK", "SCENE", "REFLECTION", "EXERCISE", "TAKEAWAY", "INTEGRATION", "THREAD"]
    segment_proses = [
        "The room is quiet. That moment when you notice your breath.",
        "She sat by the window. The light changed.",
        "What this means is that the body holds the story.",
        "Pause. Notice. Breathe.",
        "",  # TAKEAWAY empty -> TAKEAWAY_EMPTY
        "So when you return to the day, you carry this.",
        "",  # THREAD empty -> THREAD_EMPTY
    ]
    result = evaluate_chapter_flow_with_slots(slots, segment_proses)
    assert result.status == "FAIL"
    assert "TAKEAWAY_EMPTY" in result.errors
    assert "THREAD_EMPTY" in result.errors
    # When both are non-empty, no slot-specific errors
    segment_proses[4] = "Your anxiety is a nervous system alarm, not a flaw."
    segment_proses[6] = "What happens when you take this into the next moment?"
    result2 = evaluate_chapter_flow_with_slots(slots, segment_proses)
    assert "TAKEAWAY_EMPTY" not in result2.errors
    assert "THREAD_EMPTY" not in result2.errors


def test_resolve_slot_thesis_bias_prefers_metadata_overlap(monkeypatch) -> None:
    """Thesis-aware ranking (1-based chapter keys): aligned metadata sorts before generic."""
    low = AtomEntry("atom_low", metadata={"keywords": "calm breathing pause"})
    high = AtomEntry("atom_high", metadata={"keywords": "spiral regret prediction anxiety"})
    mock_index = MagicMock()
    mock_index.get_pool.return_value = [low, high]

    ctx = ResolverContext(
        persona_id="p",
        topic_id="t",
        slot_definitions=[],
        used_atom_ids=set(),
        pool_index=mock_index,
        selector_key_prefix="test-thesis",
        chapter_thesis={1: "The spiral tightens when regret predicts every outcome before you choose."},
    )
    monkeypatch.setattr(
        "phoenix_v4.planning.slot_resolver._selector_index",
        lambda _key, n: 0,
    )
    result = resolve_slot("REFLECTION", 0, 0, ctx)
    assert result is not None
    assert result[0] == "atom_high"


def test_short_form_flow_profile_skips_choppy_when_many_paragraphs() -> None:
    """Short spine books break lines often; overlap stays low without being a real jump."""
    # Token regex is [a-z']+ only — digits would fracture tokens and repeat short stems.
    blobs = [
        " ".join([f"blob{chr(ord('a') + i)}{chr(ord('a') + j)}unit" for j in range(12)]) + "."
        for i in range(20)
    ]
    glue = (
        "Because the pattern returns, which means you can name it. "
        "In practice, for example, you slow one breath. "
        "What this means is simple: you are allowed to feel this. Notice one breath and choose to stay."
    )
    text = "\n\n".join(blobs) + "\n\n" + glue
    standard = evaluate_chapter_flow(text, flow_profile="standard")
    short_form = evaluate_chapter_flow(text, flow_profile="short_form")
    assert "CHOPPY_SECTION_JUMPS" in standard.errors
    assert "CHOPPY_SECTION_JUMPS" not in short_form.errors
    assert short_form.metrics.get("flow_profile") == "short_form"


def test_flow_profile_for_runtime_format_maps_short_formats() -> None:
    from phoenix_v4.quality.chapter_flow_gate import flow_profile_for_runtime_format

    assert flow_profile_for_runtime_format("micro_book_15") == "short_form"
    assert flow_profile_for_runtime_format("standard_book") == "standard"
    assert flow_profile_for_runtime_format("deep_book_4h") == "deep_form"
    assert flow_profile_for_runtime_format("deep_book_6h") == "deep_form"


def test_deep_form_downgrades_transitions_and_thesis_to_warnings() -> None:
    """Deep chapters with 300+ sentences should not hard-fail on transition/thesis density."""
    # Build a long chapter with minimal transition cues (mimics real grief deep_book_6h)
    filler = " ".join(["The body holds what the mind cannot name."] * 80)
    body = filler + "\n\n" + filler + "\n\nNotice one breath. Exhale."
    result_standard = evaluate_chapter_flow(body, flow_profile="standard")
    result_deep = evaluate_chapter_flow(body, flow_profile="deep_form")
    # Standard profile hard-fails on missing transitions and thesis
    assert "WEAK_TRANSITIONS" in result_standard.errors or "MISSING_CLEAR_POINT" in result_standard.errors
    # Deep profile downgrades to warnings
    assert "WEAK_TRANSITIONS" not in result_deep.errors
    assert "MISSING_CLEAR_POINT" not in result_deep.errors
    assert result_deep.status == "PASS" or all(
        e not in result_deep.errors for e in ["WEAK_TRANSITIONS", "MISSING_CLEAR_POINT"]
    )


def test_deep_form_downgrades_delivery_artifact_to_warning() -> None:
    """Deep-form {placeholder} patterns should be warnings, not errors."""
    text = (
        "The station is quiet. {Street_name} outside. {Weather_detail}. "
        + "That moment when the grief hits. " * 20
        + "Notice. Breathe. Pause. "
        + "Because the cost is real. Which means you carry it. "
        + "In practice the point is to stay with the feeling."
    )
    result_std = evaluate_chapter_flow(text, flow_profile="standard")
    result_deep = evaluate_chapter_flow(text, flow_profile="deep_form")
    assert "DELIVERY_ARTIFACT_PRESENT" in result_std.errors
    assert "DELIVERY_ARTIFACT_PRESENT" not in result_deep.errors
    assert "DELIVERY_ARTIFACT_PRESENT" in result_deep.warnings


def test_short_form_skips_choppy_for_5_paragraphs() -> None:
    """Somatic short_book_30 with 5 paragraphs should skip choppy check."""
    paras = [
        "First paragraph about the body. Unique content here about sensation.",
        "Completely different second paragraph about movement and gravity.",
        "Third paragraph explores rhythm and proprioception awareness.",
        "Fourth piece on thermal regulation and interoceptive signals.",
        "Fifth closing paragraph. Breathe. Notice. The point is integration.",
    ]
    text = "\n\n".join(paras)
    result = evaluate_chapter_flow(text, flow_profile="short_form")
    assert "CHOPPY_SECTION_JUMPS" not in result.errors


def test_chapter_flow_gate_flags_generic_overlay_scaffolding() -> None:
    bad = """
You sit at the desk. gray light through the window on the glass.

That moment matters because it reveals the pattern before you have language for it.

What this means going forward is simple.

In the next chapter, we look at what it costs when it runs unchecked.

Notice your breath. Exhale once. Write one line.
"""
    result = evaluate_chapter_flow(bad)
    assert result.status == "FAIL"
    assert "GENERIC_SCENE_FALLBACK" in result.errors
    assert "ANNOUNCED_THREAD" in result.errors
    assert any(w.startswith("SCAFFOLD_RISK:") for w in result.warnings)


def test_compact_runtime_formats_classified_short_form():
    """PR-H 2026-05-04: compact runtime formats must be short-form for transition cue threshold.

    Compact formats (5/5/8 chapters, 3000-7500 words) are short-form by character.
    Without this classification, they fall to the "standard" profile requiring 3
    transition cues per chapter, which is too strict for compact-pacing prose.
    PR-G smoke surfaced ch8 of compact_book_8ch_30min failing WEAK_TRANSITIONS at
    2 cue hits when standard threshold of 3 was applied.
    """
    from phoenix_v4.quality.chapter_flow_gate import (
        flow_profile_for_runtime_format,
        SHORT_FORM_RUNTIME_FORMAT_IDS,
    )
    for fmt in (
        "compact_book_5ch_15min",
        "compact_book_5ch_20min",
        "compact_book_8ch_30min",
    ):
        assert fmt in SHORT_FORM_RUNTIME_FORMAT_IDS, (
            f"compact format {fmt!r} must be in SHORT_FORM_RUNTIME_FORMAT_IDS"
        )
        assert flow_profile_for_runtime_format(fmt) == "short_form", (
            f"compact format {fmt!r} must classify as short_form"
        )


def test_existing_short_form_formats_still_short_form():
    """Regression: don't break existing short-form classification."""
    from phoenix_v4.quality.chapter_flow_gate import flow_profile_for_runtime_format
    for fmt in ("micro_book_15", "micro_book_20", "short_book_30"):
        assert flow_profile_for_runtime_format(fmt) == "short_form"


def test_standard_book_unchanged():
    """Regression: standard_book is still standard, not short_form."""
    from phoenix_v4.quality.chapter_flow_gate import flow_profile_for_runtime_format
    assert flow_profile_for_runtime_format("standard_book") == "standard"
    assert flow_profile_for_runtime_format("deep_book_4h") == "deep_form"
