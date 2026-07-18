from __future__ import annotations

from phoenix_v4.rendering.rhetorical_memory import RhetoricalMemory, UsageRecord
from phoenix_v4.rendering.rhetorical_scorer import (
    BUDGET_THRESHOLD,
    STEM_VETO_SCORE,
    CandidateVariant,
    ScoringContext,
    check_chapter_budget,
    score_and_select,
    score_candidate,
)


def _record(chapter: int, layer: str, sublayer: str, stem: str, shape: str, root_family: str = "notice") -> UsageRecord:
    return UsageRecord(
        chapter_index=chapter,
        layer=layer,
        sublayer=sublayer,
        variant_id=f"{layer}-{chapter}",
        shape=shape,
        register="conversational",
        movement="inward",
        instruction_tone="gentle",
        cadence="medium_flowing",
        abstraction_level="mid_concept",
        root_family=root_family,
        stem=stem,
    )


def _ctx(memory: RhetoricalMemory, chapter: int = 2, emotional_job: str = "recognition") -> ScoringContext:
    return ScoringContext(
        layer="bridge",
        sublayer="after_opening",
        chapter_index=chapter,
        emotional_job=emotional_job,
        topic_id="anxiety",
        memory=memory,
    )


def _candidate(variant_id: str, text: str, **kwargs: object) -> CandidateVariant:
    base: dict[str, object] = {
        "variant_id": variant_id,
        "text": text,
        "shape": "declarative",
        "register": "conversational",
        "movement": "inward",
        "instruction_tone": "gentle",
        "cadence": "medium_flowing",
        "abstraction_level": "mid_concept",
        "root_family": "notice",
        "emotional_jobs": [],
    }
    base.update(kwargs)
    return CandidateVariant(**base)


def test_emotional_job_bonus() -> None:
    memory = RhetoricalMemory()
    ctx = _ctx(memory, chapter=1, emotional_job="recognition")
    matching = _candidate("a", "One line here", emotional_jobs=["recognition"])
    neutral = _candidate("b", "Another line here", emotional_jobs=[])
    assert score_candidate(matching, ctx) > score_candidate(neutral, ctx)


def test_stem_veto_recently_used() -> None:
    memory = RhetoricalMemory()
    memory.record(_record(1, "bridge", "after_opening", "one line here", "declarative"))
    ctx = _ctx(memory, chapter=2)
    vetoed = _candidate("a", "One line here")
    assert score_candidate(vetoed, ctx) == STEM_VETO_SCORE


def test_recency_penalty_same_shape_one_chapter_ago() -> None:
    memory = RhetoricalMemory()
    memory.record(_record(1, "bridge", "after_opening", "old stem", "declarative"))
    for i in range(2, 9):
        memory.record(_record(i, "bridge", "after_opening", f"other {i}", "interrogative"))
    ctx = _ctx(memory, chapter=2, emotional_job="")
    candidate = _candidate("a", "new words now", emotional_jobs=[], register="", movement="")
    assert score_candidate(candidate, ctx) == -5


def test_cross_layer_echo_penalty_same_chapter_other_layer() -> None:
    memory = RhetoricalMemory()
    memory.record(_record(2, "thesis", "frame", "thesis stem", "declarative", root_family="notice"))
    ctx = _ctx(memory, chapter=2, emotional_job="")
    candidate = _candidate(
        "a",
        "new words now",
        root_family="notice",
        emotional_jobs=[],
        shape="",
        register="",
        movement="",
    )
    assert score_candidate(candidate, ctx) == -2


def test_budget_penalty_over_threshold() -> None:
    memory = RhetoricalMemory()
    for i in range(4):
        memory.record(_record(i, "bridge", "after_opening", f"stem {i}", "declarative"))
    memory.record(_record(4, "bridge", "after_opening", "other stem", "interrogative"))
    assert memory.dimension_ratio("shape", "declarative") > BUDGET_THRESHOLD

    ctx = _ctx(memory, chapter=10, emotional_job="")
    candidate = _candidate(
        "a",
        "fresh words for scoring",
        shape="declarative",
        emotional_jobs=[],
        register="",
        movement="",
    )
    assert score_candidate(candidate, ctx) == -4


def test_tiebreak_first_candidate_wins() -> None:
    memory = RhetoricalMemory()
    ctx = _ctx(memory, chapter=3, emotional_job="")
    c1 = _candidate("a", "alpha text", emotional_jobs=[])
    c2 = _candidate("b", "beta text", emotional_jobs=[])
    best, _ = score_and_select([c1, c2], ctx)
    assert best.variant_id == "a"


def test_score_and_select_records_winner() -> None:
    memory = RhetoricalMemory()
    ctx = _ctx(memory, chapter=5, emotional_job="recognition")
    winner = _candidate("best", "gentle line here", emotional_jobs=["recognition"])
    other = _candidate("other", "different line now", emotional_jobs=[])
    chosen, rec = score_and_select([other, winner], ctx)

    assert chosen.variant_id == "best"
    assert rec.variant_id == "best"
    assert memory.total_selections == 1
    recent = memory.recent_at_layer("bridge", "after_opening", current_chapter=6, window=3)
    assert recent and recent[0].variant_id == "best"


def test_check_chapter_budget_reports_over_budget_dimensions() -> None:
    memory = RhetoricalMemory()
    for i in range(7):
        memory.record(_record(i, "bridge", "after_opening", f"stem {i}", "declarative"))
    for i in range(3):
        memory.record(
            UsageRecord(
                chapter_index=10 + i,
                layer="bridge",
                sublayer="after_opening",
                variant_id=f"other-{i}",
                shape="interrogative",
                register="conversational",
                movement="outward",
                instruction_tone="gentle",
                cadence="medium_flowing",
                abstraction_level="mid_concept",
                root_family="notice",
                stem=f"other stem {i}",
            )
        )
    warnings = check_chapter_budget(memory, threshold=0.6)
    assert "shape" in warnings
    assert any("declarative" in item for item in warnings["shape"])

