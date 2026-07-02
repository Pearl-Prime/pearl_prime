"""Tests for register-output craft strengthen passes."""

from phoenix_v4.rendering.register_output_strengthen import (
    break_pedagogical_cadence_repetition,
    cap_prescribed_action_density,
    dedupe_register_f1_paragraphs,
    ensure_book_terminal_integrity,
    ensure_dwell_beats,
    ensure_unique_chapter_closings,
    ensure_word_count_floor,
    repair_f13_dwell_contract,
    spine_deprescribe_inject_enabled,
    verify_f7_exercise_preservation,
    _DEPRESCRIBE_ALTERNATIVES,
)
from phoenix_v4.quality.register_gate import (
    _detect_f4_closing_line_repeats,
    _detect_f13_dwell_starvation,
    _detect_f6_cadence_repetition,
    _detect_f1_templated_paragraphs,
    _f13_is_insight,
    _is_prescribed_action,
    _split_chapters,
)


def test_ensure_book_terminal_integrity_truncates_mid_sentence():
    prose = "Chapter 1\n\nFirst paragraph ends well.\n\nThis breath practice starts"
    fixed = ensure_book_terminal_integrity(prose)
    assert fixed.endswith(".")
    assert "starts" not in fixed.split()[-3:]


def test_ensure_dwell_beats_is_noop():
    body = (
        "The mechanism is simple. Which means the body moves first. "
        "The cost is already on the table."
    )
    chapter = f"Chapter 2\n\n{body}"
    out = ensure_dwell_beats(chapter, seed="test")
    assert out == chapter


def test_ensure_word_count_floor_is_noop():
    """
    G1 (render-hardening 2026-07-02): the word-floor padder is disabled (#4566). It must
    NOT append standalone one-line filler to hit a floor — an under-length book is a
    thin-pool signal, surfaced by run_pipeline, never papered over. Even asked to reach a
    floor far above the input, the padder returns the prose byte-for-byte unchanged.
    """
    body = (
        "She knows the shape of the exhaustion well enough to describe it from the inside. "
        "The red-eye lands at six-fifteen. She buys a coffee that costs seven dollars."
    )
    chapter = f"Chapter 1\n\n{body}"
    before_words = len(chapter.split())
    out = ensure_word_count_floor(chapter, floor=before_words + 5000, seed="floor")
    assert out == chapter, "floor padder must be a no-op (no filler appended)"
    assert len(out.split()) == before_words, "no words may be added to reach the floor"


def test_break_pedagogical_cadence_clears_f6():
    # Four identical cadence windows (8,10,12,9 word sentences ×3) trip F6.
    sent_a = "one two three four five six seven eight."
    sent_b = "one two three four five six seven eight nine ten."
    sent_c = "one two three four five six seven eight nine ten eleven twelve."
    sent_d = "one two three four five six seven eight nine."
    block = " ".join([sent_a, sent_b, sent_c, sent_d])
    chapter = f"Chapter 1\n\n{block}\n\n{block}\n\n{block}"
    assert _detect_f6_cadence_repetition(_split_chapters(chapter))
    fixed = break_pedagogical_cadence_repetition(chapter, seed="test")
    assert not _detect_f6_cadence_repetition(_split_chapters(fixed))


def test_cap_prescribed_action_density():
    paras = []
    for i in range(5):
        paras.append(f"Notice your breath for five seconds. Step {i + 1}. Hold.")
    body = "\n\n".join(paras)
    chapter = f"Chapter 1\n\n{body}"
    out = cap_prescribed_action_density(chapter, max_per_chapter=2)
    ch_text = out.split("Chapter 1", 1)[1]
    count = sum(1 for p in ch_text.split("\n\n") if _is_prescribed_action(p))
    assert count <= 2


def test_cap_prescribed_action_density_no_deprescribe_inject_when_disabled():
    """G1-residual: surplus prescribed-action paras are dropped, not replaced with filler."""
    paras = []
    for i in range(5):
        paras.append(f"Notice your breath for five seconds. Step {i + 1}. Hold.")
    body = "\n\n".join(paras)
    chapter = f"Chapter 1\n\n{body}"
    out = cap_prescribed_action_density(
        chapter, max_per_chapter=2, inject_deprescribe_alternative=False
    )
    ch_text = out.split("Chapter 1", 1)[1]
    for alt in _DEPRESCRIBE_ALTERNATIVES:
        assert alt not in ch_text
    count = sum(1 for p in ch_text.split("\n\n") if _is_prescribed_action(p))
    assert count <= 2


def test_destack_adjacent_inject_paragraphs():
    from phoenix_v4.rendering.register_output_strengthen import (
        destack_adjacent_inject_paragraphs,
    )

    bridge = "The mechanism behind this pattern is small and stubborn."
    dep = "An ordinary pace is a sustainable pace."
    body = f"{bridge}\n\n{dep}\n\nSome longer narrative paragraph that should remain."
    chapter = f"Chapter 1\n\n{body}"
    out = destack_adjacent_inject_paragraphs(chapter)
    assert bridge in out
    assert dep not in out
    assert "Some longer narrative paragraph" in out


def test_spine_deprescribe_inject_disabled_by_default(monkeypatch):
    monkeypatch.delenv("PHOENIX_SPINE_DEPRESCRIBE", raising=False)
    assert not spine_deprescribe_inject_enabled()
    monkeypatch.setenv("PHOENIX_SPINE_DEPRESCRIBE", "1")
    assert spine_deprescribe_inject_enabled()


def test_fold_bridge_forward_into_next_narrative_paragraph():
    """G1-residual Phase-2: a standalone bridge one-liner is woven into the
    paragraph it introduces, not left as a free-standing beat."""
    from phoenix_v4.rendering.register_output_strengthen import (
        fold_standalone_inject_paragraphs,
    )

    bridge = "The mechanism behind this pattern is small and stubborn."
    atom = (
        "You are not less than you were; you are measuring an empty tank "
        "against a full one, and the gauge has simply not caught up yet."
    )
    chapter = f"Chapter 1\n\n{bridge}\n\n{atom}"
    out = fold_standalone_inject_paragraphs(chapter)
    # bridge no longer stands alone; it is prefixed onto the atom paragraph
    assert f"{bridge} {atom}" in out
    assert f"{bridge}\n\n{atom}" not in out


def test_fold_collapses_consecutive_injects_and_practice_intro():
    from phoenix_v4.rendering.register_output_strengthen import (
        fold_standalone_inject_paragraphs,
        _DEPRESCRIBE_ALTERNATIVES,
    )

    bridge = "The mechanism behind this pattern is small and stubborn."
    dep = _DEPRESCRIBE_ALTERNATIVES[0]
    practice = "Now we're going to do a breath practice."
    atom = (
        "The comparison engine runs on incomplete data and treats every "
        "decision like a permanent threat to your standing and your worth."
    )
    chapter = f"Chapter 1\n\n{bridge}\n\n{dep}\n\n{practice}\n\n{atom}"
    out = fold_standalone_inject_paragraphs(chapter)
    body = out.split("Chapter 1", 1)[1]
    # no inject line survives as its own paragraph
    for line in (bridge, dep, practice):
        assert f"\n\n{line}\n\n" not in body
        assert not body.strip().startswith(line + "\n\n")
    # exactly one narrative paragraph remains (injects collapsed into it)
    paras = [p for p in body.split("\n\n") if p.strip()]
    assert len(paras) == 1
    assert atom in paras[0]


def test_fold_marks_bare_section_heading():
    from phoenix_v4.rendering.register_output_strengthen import (
        fold_standalone_inject_paragraphs,
    )

    heading = "This Is Not Tiredness"
    atom = (
        "You closed the laptop and the closing did not register as relief, "
        "because the depletion is not about the hours you worked today."
    )
    chapter = f"Chapter 1\n\n{heading}\n\n{atom}"
    out = fold_standalone_inject_paragraphs(chapter)
    assert f"## {heading}" in out
    # a real sentence (ends in punctuation) is never mis-marked as a heading
    assert "## You closed" not in out


def test_fold_disabled_by_env(monkeypatch):
    from phoenix_v4.rendering.register_output_strengthen import (
        fold_standalone_inject_paragraphs,
        inject_fold_enabled,
    )

    monkeypatch.setenv("PHOENIX_INJECT_FOLD", "0")
    assert not inject_fold_enabled()
    bridge = "The mechanism behind this pattern is small and stubborn."
    atom = "A longer narrative paragraph that clearly should remain in place unchanged here."
    chapter = f"Chapter 1\n\n{bridge}\n\n{atom}"
    assert fold_standalone_inject_paragraphs(chapter) == chapter


def test_deprescribe_alternatives_are_f7_safe():
    assert _DEPRESCRIBE_ALTERNATIVES
    for line in _DEPRESCRIBE_ALTERNATIVES:
        assert not _is_prescribed_action(line), line
        assert not _f13_is_insight(line), line


def test_repair_f13_dwell_contract_is_noop():
    body = (
        "The mechanism is simple. Which means the body moves first. "
        "The cost is already on the table."
    )
    chapter = f"Chapter 3\n\n{body}"
    out = repair_f13_dwell_contract(chapter, seed="test")
    assert out == chapter


def test_verify_f7_exercise_preservation_zero_contract():
    chapter = "Chapter 1\n\nNotice your breath for five seconds. Step one."
    gov = {
        "exercise_slots_dropped": [
            {"chapter": 1, "contract_max_exercises": 0},
        ]
    }
    violations = verify_f7_exercise_preservation(chapter, governance_report=gov)
    assert violations
    assert any("contract_max_exercises=0" in v for v in violations)


def test_verify_f7_exercise_preservation_stripped_exercise():
    chapter = "Chapter 2\n\nPlain narrative without prescribed steps."
    gov = {
        "exercise_slots_dropped": [
            {"chapter": 2, "contract_max_exercises": 1},
        ]
    }
    violations = verify_f7_exercise_preservation(chapter, governance_report=gov)
    assert any("below contract_max_exercises" in v for v in violations)


def test_dedupe_register_f1_paragraphs():
    para = (
        "One two three four five six. "
        "Seven eight nine ten eleven twelve. "
        "Thirteen fourteen fifteen sixteen."
    )
    ch1 = f"Chapter 1\n\n{para}\n\nTail sentence here."
    ch2 = f"Chapter 2\n\n{para}\n\nDifferent tail."
    book = f"{ch1}\n\n{ch2}"
    assert _detect_f1_templated_paragraphs(_split_chapters(book))
    out, notes = dedupe_register_f1_paragraphs(book)
    assert not _detect_f1_templated_paragraphs(_split_chapters(out))
    assert notes


def test_ensure_unique_chapter_closings():
    line = "Of course the alarm kept running — the system was doing its job."
    book = (
        f"Chapter 1\n\nBody one.\n\n{line}\n\n"
        f"Chapter 2\n\nBody two.\n\n{line}"
    )
    assert _detect_f4_closing_line_repeats(_split_chapters(book))
    out = ensure_unique_chapter_closings(book, seed="test")
    assert not _detect_f4_closing_line_repeats(_split_chapters(out))
