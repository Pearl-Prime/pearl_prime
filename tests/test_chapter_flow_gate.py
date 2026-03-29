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
