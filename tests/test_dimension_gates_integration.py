"""Verify all 5 EI V2 dimension gates produce non-stub scores (ACT-009 / BSG-005)."""
from phoenix_v4.quality.ei_v2.dimension_gates import (
    gate_cohesion,
    gate_engagement,
    gate_listen_experience,
    gate_somatic_precision,
    gate_uniqueness,
)

GOOD_TEXT = """
The pattern you have been living with has a name. It is not a character flaw
and it is not a life sentence. It is a strategy your nervous system developed
when you needed it most. The problem is not that you have it. The problem is
that you still run it in situations where it costs more than it protects.
Your body knows this strategy as well as your mind does. The tightening in
your chest before a difficult conversation. The hypervigilance at a family
dinner. The way you cannot stop scanning the room even when you are safe.
What the research calls a conditioned threat response. Your amygdala learned
that certain signals meant danger even when the original danger is long gone.
The system that kept you safe has outlived its usefulness. What changes this
is giving your nervous system new evidence repeatedly in real situations.
""".strip()

SHORT_BAD = "The."

# Prior chapter text for cohesion gate (needs chapter_index >= 1 to evaluate)
PRIOR_TEXT = "This is a prior chapter about completely unrelated administrative topics."

# Adapters: each gate has its own required signature
# We provide minimal kwargs to get meaningful (non-trivial) evaluation
GATES = [
    # uniqueness: needs other_texts + chapter_index; empty others -> always 1.0
    # Use chapter_index=1 with a different other_text to get real evaluation
    (gate_uniqueness, "uniqueness",
     {"other_texts": [PRIOR_TEXT], "chapter_index": 1},
     {"other_texts": [SHORT_BAD], "chapter_index": 1}),
    # cohesion: chapter_index=1 + a prior to compare against
    (gate_cohesion, "cohesion",
     {"other_texts": [PRIOR_TEXT], "chapter_index": 1},
     {"other_texts": [PRIOR_TEXT], "chapter_index": 1}),
    # engagement: needs chapter_index
    (gate_engagement, "engagement",
     {"chapter_index": 0},
     {"chapter_index": 0}),
    # somatic_precision: no extra args
    (gate_somatic_precision, "somatic_precision", {}, {}),
    # listen_experience: no extra args
    (gate_listen_experience, "listen_experience", {}, {}),
]


def test_all_gates_return_valid_scores():
    for fn, name, good_kwargs, _ in GATES:
        r = fn(GOOD_TEXT, **good_kwargs)
        assert hasattr(r, "score"), f"{name}: missing score"
        assert 0.0 <= r.score <= 1.0, f"{name}: score {r.score} out of range"
        assert hasattr(r, "status"), f"{name}: missing status"
        assert r.status in ("PASS", "WARN", "FAIL"), f"{name}: bad status {r.status}"
        assert hasattr(r, "dimension"), f"{name}: missing dimension attribute"
        print(f"{name}: score={r.score:.3f} status={r.status}")


def test_no_gate_is_constant_stub():
    """No gate should return 1.0 for BOTH good and bad input — that would be a stub."""
    for fn, name, good_kwargs, bad_kwargs in GATES:
        r_good = fn(GOOD_TEXT, **good_kwargs)
        r_bad = fn(SHORT_BAD, **bad_kwargs)
        is_constant_stub = r_good.score == 1.0 and r_bad.score == 1.0
        assert not is_constant_stub, (
            f"{name} is a constant-1.0 stub: "
            f"good={r_good.score:.3f} bad={r_bad.score:.3f}"
        )


def test_engagement_differentiates_long_from_short():
    r_good = gate_engagement(GOOD_TEXT, chapter_index=0)
    r_bad = gate_engagement(SHORT_BAD, chapter_index=0)
    assert r_good.score > r_bad.score, (
        f"engagement should score good text higher: good={r_good.score:.3f} bad={r_bad.score:.3f}"
    )


def test_somatic_precision_detects_body_words():
    r_good = gate_somatic_precision(GOOD_TEXT)  # contains chest, breath, jaw etc.
    r_bad = gate_somatic_precision("Administrative procedures require documentation review processes.")
    assert r_good.score > r_bad.score, (
        f"somatic_precision should score body-word-rich text higher: "
        f"good={r_good.score:.3f} bad={r_bad.score:.3f}"
    )


def test_listen_experience_varied_beats_monotone():
    monotone = ("This is a sentence. " * 15).strip()
    r_varied = gate_listen_experience(GOOD_TEXT)
    r_mono = gate_listen_experience(monotone)
    assert r_varied.score >= r_mono.score, (
        f"varied text {r_varied.score:.3f} should score >= monotone {r_mono.score:.3f}"
    )


def test_cohesion_chapter_zero_always_passes():
    """Chapter 0 has no prior — cohesion should not penalize it."""
    r = gate_cohesion(GOOD_TEXT, other_texts=[], chapter_index=0)
    assert r.status == "PASS", f"chapter 0 cohesion should PASS, got {r.status}"
    assert r.score == 1.0, f"chapter 0 cohesion score should be 1.0, got {r.score}"


def test_cohesion_unrelated_prior_fails():
    """Cohesion should fail when current chapter shares nothing with prior."""
    prior = "Cats prefer warm windowsills during afternoon naps beside the garden wall."
    unrelated = (
        "Administrative tax regulations require documentation from all departments each year. "
        "Compliance officers review submissions carefully before approving revised filings only. "
        "Organizations must retain detailed records throughout the statutory period without exception."
    )
    r = gate_cohesion(unrelated, other_texts=[prior], chapter_index=1,
                      cohesion_cfg={"min_cross_chapter_refs": 1,
                                    "pass_threshold": 0.40, "warn_threshold": 0.25})
    assert r.status == "FAIL", f"unrelated chapters should fail cohesion, got {r.status} {r.score}"


def test_uniqueness_duplicate_fails():
    """Uniqueness should fail when current text heavily duplicates another chapter."""
    long_dup = (
        "That morning, Sarah opened her laptop at the kitchen table with careful attention. "
        "Her jaw was tight and her shoulders carried the weight of unfinished decisions. "
        "But then she noticed something shifting in how she breathed before the meeting started. "
        "What comes next might surprise anyone listening to this story unfold slowly across hours. "
        "Her shoulders eased slightly when she named the fear aloud in the quiet room alone."
    )
    r = gate_uniqueness(long_dup, other_texts=[long_dup], chapter_index=1)
    assert r.status == "FAIL", (
        f"high-overlap text should fail uniqueness, got {r.status} score={r.score:.3f}"
    )


def test_all_gates_present_in_phase3_run():
    """run_chapter_dimension_gates at phase=3 must include all 5 gates."""
    from phoenix_v4.quality.ei_v2.dimension_gates import run_chapter_dimension_gates

    report = run_chapter_dimension_gates(
        GOOD_TEXT,
        [],
        chapter_index=0,
        dimension_gates_cfg={
            "fail_mode": "warn",
            "dimension_gate_phase": 3,
            "blocked_dimensions": [],
        },
    )
    dimensions_present = {g.dimension for g in report.gates}
    for expected in ("uniqueness", "engagement", "somatic_precision", "cohesion", "listen_experience"):
        assert expected in dimensions_present, f"Gate '{expected}' missing from phase-3 run"
