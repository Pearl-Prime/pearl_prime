from __future__ import annotations

from pathlib import Path

from phoenix_v4.rendering import chapter_composer as cc


def _sample_thesis() -> str:
    return "The point is that the alarm fires before evidence."


def test_candidate_pools_differ_by_emotional_job() -> None:
    recognition = cc._collect_bridge_candidates(
        bridge_type="after_opening",
        emotional_job="recognition",
        chapter_position="early",
    )
    mechanism = cc._collect_bridge_candidates(
        bridge_type="after_opening",
        emotional_job="mechanism",
        chapter_position="early",
    )
    assert recognition and mechanism
    assert {c["text"] for c in recognition} != {c["text"] for c in mechanism}


def test_after_opening_recognition_avoids_mechanism_phrases() -> None:
    text = cc._bridge_after_opening(
        _sample_thesis(),
        emotional_job="recognition",
        chapter_index=0,
        total_chapters=12,
        bridge_memory=cc.BridgeMemory(),
    ).lower()
    assert "alarm has already chosen" not in text


def test_no_exact_bridge_phrase_reuse_in_12_chapters() -> None:
    memory = cc.BridgeMemory()
    seen: set[str] = set()
    jobs = ["recognition", "mechanism", "deepening", "reframe", "practice", "integration", "resolution"]
    for idx in range(12):
        text = cc._bridge_before_story(
            _sample_thesis(),
            reflection="You can feel it in the chest.",
            story="A normal morning became a threat story.",
            emotional_job=jobs[idx % len(jobs)],
            chapter_index=idx,
            total_chapters=12,
            bridge_memory=memory,
        )
        assert text not in seen
        seen.add(text)


def test_shape_not_overused_in_three_chapter_window() -> None:
    memory = cc.BridgeMemory()
    for idx in range(3):
        cc._bridge_before_exercise(
            _sample_thesis(),
            reflection="Body tightens before thought.",
            story="A message arrives and the jaw locks.",
            emotional_job="integration",
            chapter_index=idx,
            total_chapters=12,
            bridge_memory=memory,
        )
    shape_counts = {}
    for chapter in range(3):
        for shape, count in memory.shape_usage_by_chapter.get(chapter, {}).items():
            shape_counts[shape] = shape_counts.get(shape, 0) + count
    assert shape_counts
    assert max(shape_counts.values()) <= 2


def test_fallback_thread_returns_empty_for_final_chapter() -> None:
    assert (
        cc._fallback_thread(
            _sample_thesis(),
            chapter_index=11,
            total_chapters=12,
            emotional_job="resolution",
            bridge_memory=cc.BridgeMemory(),
        )
        == ""
    )


def test_fallback_thread_differs_early_vs_late() -> None:
    memory = cc.BridgeMemory()
    early = cc._fallback_thread(
        _sample_thesis(),
        chapter_index=1,
        total_chapters=12,
        emotional_job="recognition",
        bridge_memory=memory,
    )
    late = cc._fallback_thread(
        _sample_thesis(),
        chapter_index=10,
        total_chapters=12,
        emotional_job="recognition",
        bridge_memory=memory,
    )
    assert early != late


def test_bridge_memory_blocks_repeated_exact_phrase() -> None:
    memory = cc.BridgeMemory()
    first = cc._select_bridge_candidate(
        bridge_type="after_opening",
        emotional_job="recognition",
        chapter_index=0,
        total_chapters=12,
        bridge_memory=memory,
        context_text="alarm body pattern",
    )
    assert first is not None
    assert memory.phrase_used_book(first["text"])


def test_bridge_memory_limits_same_stem_density() -> None:
    memory = cc.BridgeMemory()
    memory.register(
        chapter_index=0,
        phrase="seed phrase",
        shape="direct_assertion",
        stems=["ask useful next question"],
        roots=["pattern"],
        family_key="after_opening|recognition",
    )
    blocked = {
        "text": "candidate",
        "shape": "question_turn",
        "stems": ["ask useful next question"],
        "roots": ["pattern"],
        "scene_bias": [],
        "position_bias": "any",
    }
    score = cc._score_bridge_candidate(
        blocked,
        chapter_index=1,
        total_chapters=12,
        bridge_memory=memory,
        bridge_family="after_opening|recognition",
        topic_keywords={"pattern"},
    )
    assert score <= -9999.0


def test_missing_yaml_graceful_fallback(monkeypatch) -> None:
    monkeypatch.setattr(cc, "_BRIDGE_TRANSITION_CACHE", None)
    monkeypatch.setattr(cc, "_BRIDGE_TRANSITION_PATH", Path("/tmp/no_bridge_config.yaml"))
    text = cc._bridge_after_opening(
        _sample_thesis(),
        opening="You freeze at send.",
        emotional_job="mechanism",
        chapter_index=1,
        total_chapters=12,
        bridge_memory=cc.BridgeMemory(),
    )
    assert text
    monkeypatch.setattr(cc, "_BRIDGE_TRANSITION_CACHE", None)


def test_backward_compat_emotional_job_empty() -> None:
    out = cc._bridge_before_story(
        _sample_thesis(),
        reflection="comparison makes everything smaller",
        story="she compared her inbox to everyone else",
        emotional_job="",
    ).lower()
    assert "outside" in out or "pattern" in out


def test_fallback_takeaway_varies_by_thesis() -> None:
    one = cc._fallback_takeaway("The point is that pausing breaks the loop.")
    two = cc._fallback_takeaway("The point is that naming the signal lowers panic.")
    assert one != two


def test_no_self_announcing_phrases_in_bridge_outputs() -> None:
    outputs = [
        cc._bridge_after_opening(_sample_thesis(), emotional_job="recognition", chapter_index=0, total_chapters=12, bridge_memory=cc.BridgeMemory()),
        cc._bridge_before_story(_sample_thesis(), reflection="x", story="y", emotional_job="mechanism", chapter_index=1, total_chapters=12, bridge_memory=cc.BridgeMemory()),
        cc._bridge_before_exercise(_sample_thesis(), reflection="x", story="y", emotional_job="practice", chapter_index=2, total_chapters=12, bridge_memory=cc.BridgeMemory()),
        cc._bridge_before_integration(_sample_thesis(), integration="z", emotional_job="integration", chapter_index=3, total_chapters=12, bridge_memory=cc.BridgeMemory()),
        cc._fallback_takeaway(_sample_thesis(), emotional_job="resolution", chapter_index=4, total_chapters=12, bridge_memory=cc.BridgeMemory()),
    ]
    for text in outputs:
        low = text.lower()
        assert "this chapter is about" not in low
        assert "the purpose of this section" not in low


def test_keyword_specific_legacy_bridges_still_fire_when_emotional_job_empty() -> None:
    comparison = cc._bridge_after_opening(
        "comparison",
        opening="comparison",
        emotional_job="",
    ).lower()
    assert "comparison does its quiet damage" in comparison or "turned it into a verdict" in comparison
    alarm = cc._bridge_after_opening(
        "alarm",
        opening="alarm",
        emotional_job="",
    ).lower()
    assert "alarm has already chosen" in alarm or "body is already behaving like the threat is real" in alarm


def test_compose_chapter_prose_still_returns_valid_output() -> None:
    slot_types = ["HOOK", "REFLECTION", "STORY", "EXERCISE", "INTEGRATION"]
    slot_proses = [
        "Your thumb hovers over send.",
        "The point is that anxiety predicts regret so loudly that it blocks action.",
        "She froze over a simple reply and called it strategy.",
        "Take one slow exhale and unclench your jaw.",
        "The room feels wider when the body stops arguing.",
    ]
    out = cc.compose_chapter_prose(
        slot_types,
        slot_proses,
        chapter_index=1,
        total_chapters=12,
        emotional_role="mechanism",
        bridge_memory=cc.BridgeMemory(),
    )
    assert isinstance(out, str) and len(out) > 80


# ─────────────────────────────────────────────────────────────────────────────
# DEFERRED-LANE bridge_bank (2026-06-15): the data-driven 'Ahead of you:' thread
# bank was starved (served 0x in the pilot books) because the shared book-level
# BridgeMemory was saturated with the synthetic "variant-N" disambiguator stem and
# the structural-root hard-cap, so every thread_fallback candidate scored -10_000
# and the selector fell through to the hardcoded literal pool.
# ─────────────────────────────────────────────────────────────────────────────


def test_synthetic_variant_stems_are_dropped_at_collection() -> None:
    # The bank carries a synthetic "variant-N" stem alongside each real semantic stem.
    # It must NOT survive into the candidate dict (otherwise it poisons shared memory).
    cands = cc._collect_bridge_candidates(
        bridge_type="thread_fallback",
        emotional_job="recognition",
        chapter_position="early",
    )
    assert cands, "thread_fallback recognition bank should have candidates"
    for c in cands:
        assert not any(
            cc._SYNTHETIC_VARIANT_STEM_RE.match(s) for s in c["stems"]
        ), f"synthetic variant stem leaked into {c['stems']!r}"
    # Real semantic stems are still present (dedup signal preserved).
    assert any(c["stems"] for c in cands), "real semantic stems must survive"


def test_synthetic_variant_stem_does_not_block_fresh_candidate() -> None:
    # Registering "variant-1" (as an earlier slot of any bridge type would) must NOT
    # veto a thread candidate that only shares that synthetic token.
    memory = cc.BridgeMemory()
    memory.register(
        chapter_index=0,
        phrase="some earlier bridge",
        shape="direct_assertion",
        stems=["variant-1"],  # synthetic token registered by an earlier slot
        roots=["recognition"],
        family_key="after_opening|recognition",
    )
    fresh = {
        "text": "Ahead of you: a genuinely fresh thread-forward sentence.",
        "shape": "question_turn",
        "stems": ["ask useful next question"],  # real stem, never used
        "roots": ["recognition"],
        "scene_bias": [],
        "position_bias": "any",
    }
    score = cc._score_bridge_candidate(
        fresh,
        chapter_index=1,
        total_chapters=12,
        bridge_memory=memory,
        bridge_family="thread_fallback|recognition",
        topic_keywords={"pattern"},
    )
    assert score > -9999.0, "fresh candidate must not be vetoed by a synthetic stem"


def test_data_driven_thread_bank_actually_serves_across_book() -> None:
    # Regression guard for the starvation: across a 12-chapter book sharing one
    # BridgeMemory (as a real render does), the data-driven 'Ahead of you:' bank
    # must serve at least a few chapters rather than falling 100% to the literal pool.
    memory = cc.BridgeMemory()
    roles = [
        "recognition", "destabilization", "reframe", "stabilization",
        "integration", "recognition", "mechanism", "reframe",
        "integration", "stabilization", "recognition", "integration",
    ]
    served = 0
    for ci in range(12):
        thread = cc._fallback_thread(
            "seeing the pattern before defending it",
            chapter_index=ci,
            total_chapters=12,
            emotional_job=roles[ci],
            bridge_memory=memory,
            book_seed="book-A",
            persona_id="p",
            topic_id="anxiety",
        )
        if thread.startswith("Ahead of you:"):
            served += 1
    assert served >= 2, f"data-driven thread bank served only {served}/12 (starved)"


def test_thread_bank_preserves_book_distinct_dedup() -> None:
    # #1589 guard: even with the bank serving, no exact thread phrase repeats within
    # a book, and two books (different seeds) diverge.
    def run(seed: str) -> list[str]:
        memory = cc.BridgeMemory()
        roles = [
            "recognition", "destabilization", "reframe", "stabilization",
            "integration", "recognition", "mechanism", "reframe",
            "integration", "stabilization", "recognition",
        ]
        out = []
        for ci in range(11):  # exclude final chapter (returns "")
            out.append(
                cc._fallback_thread(
                    "seeing the pattern before defending it",
                    chapter_index=ci,
                    total_chapters=12,
                    emotional_job=roles[ci],
                    bridge_memory=memory,
                    book_seed=seed,
                    persona_id="p",
                    topic_id="anxiety",
                )
            )
        return out

    a = run("book-A")
    b = run("book-B")
    # No exact repeat within a book (book-distinct dedup intact).
    assert len(set(a)) == len(a), "thread phrase repeated within a single book"
    # Determinism for a fixed seed.
    assert run("book-A") == a
    # Two different books diverge (cross-book divergence preserved).
    assert sum(1 for x, y in zip(a, b) if x == y) < len(a)
