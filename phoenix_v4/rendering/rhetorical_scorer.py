"""
Scored candidate selection for rhetorical variants.

Replaces _pick_variant() hash-seeded selection with penalty/reward scoring
across memory state. Each subsystem selector calls score_and_select()
with its candidate pool and context.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from phoenix_v4.rendering.rhetorical_memory import RhetoricalMemory, UsageRecord


@dataclass
class ScoringContext:
    """Everything the scorer needs from the caller."""

    layer: str
    sublayer: str
    chapter_index: int
    emotional_job: str
    topic_id: str
    memory: RhetoricalMemory
    book_seed: str = ""


@dataclass
class CandidateVariant:
    """A single variant to be scored. Tags come from the YAML."""

    variant_id: str
    text: str
    shape: str = ""
    register: str = ""
    movement: str = ""
    instruction_tone: str = ""
    cadence: str = ""
    abstraction_level: str = ""
    root_family: str = ""
    emotional_jobs: list[str] = field(default_factory=list)

    @property
    def stem(self) -> str:
        """First 6 words, lowercased."""
        words = self.text.strip().split()[:6]
        return " ".join(w.lower() for w in words)


EMOTIONAL_JOB_BONUS = 3
RECENCY_PENALTIES = {1: -5, 2: -3, 3: -1}
CROSS_LAYER_ECHO_PENALTY = -2
BUDGET_OVER_PENALTY = -4
BUDGET_THRESHOLD = 0.30
STEM_VETO_SCORE = float("-inf")


def score_candidate(candidate: CandidateVariant, ctx: ScoringContext) -> float:
    """Score a single candidate against current memory state."""
    score = 0.0

    if ctx.emotional_job and ctx.emotional_job in candidate.emotional_jobs:
        score += EMOTIONAL_JOB_BONUS

    if ctx.memory.stem_used_recently(
        ctx.layer, ctx.sublayer, candidate.stem, ctx.chapter_index
    ):
        return STEM_VETO_SCORE

    recent = ctx.memory.recent_at_layer(
        ctx.layer, ctx.sublayer, ctx.chapter_index, window=3
    )
    for rec in recent:
        chapters_ago = ctx.chapter_index - rec.chapter_index
        if chapters_ago in RECENCY_PENALTIES and rec.shape == candidate.shape:
            score += RECENCY_PENALTIES[chapters_ago]

    if candidate.root_family:
        same_ch = ctx.memory.same_chapter_other_layers(ctx.chapter_index, ctx.layer)
        if any(r.root_family == candidate.root_family for r in same_ch):
            score += CROSS_LAYER_ECHO_PENALTY

    for dim_name in ("shape", "register", "movement"):
        val = getattr(candidate, dim_name, "")
        if val and ctx.memory.dimension_ratio(dim_name, val) > BUDGET_THRESHOLD:
            score += BUDGET_OVER_PENALTY

    return score


def score_and_select(
    candidates: list[CandidateVariant],
    ctx: ScoringContext,
) -> tuple[CandidateVariant, UsageRecord]:
    """
    Score all candidates, pick the best, record in memory, return both
    the chosen candidate and the usage record.

    Tiebreak: original pool order (first candidate wins ties).
    """
    if not candidates:
        raise ValueError("Empty candidate pool — cannot select")

    scored = [(score_candidate(c, ctx), i, c) for i, c in enumerate(candidates)]
    scored.sort(key=lambda t: (-t[0], t[1]))
    _, _, best = scored[0]

    record = UsageRecord(
        chapter_index=ctx.chapter_index,
        layer=ctx.layer,
        sublayer=ctx.sublayer,
        variant_id=best.variant_id,
        shape=best.shape,
        register=best.register,
        movement=best.movement,
        instruction_tone=best.instruction_tone,
        cadence=best.cadence,
        abstraction_level=best.abstraction_level,
        root_family=best.root_family,
        stem=best.stem,
    )
    ctx.memory.record(record)
    return best, record


def check_chapter_budget(
    memory: RhetoricalMemory,
    threshold: float = BUDGET_THRESHOLD,
) -> dict[str, list[str]]:
    """
    Return any dimension values that have exceeded the budget threshold.
    Useful for QA reports. Returns {dim_name: [over_budget_values]}.
    """
    warnings: dict[str, list[str]] = {}
    for dim_name in (
        "shape",
        "register",
        "movement",
        "instruction_tone",
        "cadence",
        "abstraction_level",
    ):
        over = []
        with memory._lock:
            for val, count in memory._dimension_counts[dim_name].items():
                if memory._total_selections > 0:
                    ratio = count / memory._total_selections
                    if ratio > threshold:
                        over.append(f"{val} ({ratio:.0%})")
        if over:
            warnings[dim_name] = over
    return warnings

