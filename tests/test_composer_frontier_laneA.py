"""Lane A regression tests for the composer-frontier fix wave.

Covers two defects, both fixed inside phoenix_v4/rendering/chapter_composer.py:

  DEFECT 1 (cross_book_transitions): inter-chapter thread-forward bridges were
  emitted byte-identically across books (same thesis -> same constant) and
  repeated up to 10x within a single book, because (1) the data-driven bridge
  bank was gated behind `if job:` using arc-role vocab the planner never matched
  to _EMOTIONAL_JOBS, and (2) the hardcoded literal fallback was book-agnostic.

  DEFECT 5 (hook_placeholders): the placeholder detector only matched
  "[Placeholder|Missing|Silence: ...]" and let "[Persona-specific hook for
  <persona> x <topic>]" stubs (and TODO/TKTK/TBD/DRAFT forms) render as chapter
  openings.

Spec: artifacts/analysis/pearl_prime_priorities/COMPOSER_FRONTIER_FIX_SPEC_20260614.md
"""
from __future__ import annotations

import itertools
from collections import Counter

from phoenix_v4.rendering import chapter_composer as cc


# A realistic 12-chapter emotional-role sequence using the planner's actual arc
# vocab (arc_loader.ALLOWED_EMOTIONAL_ROLES = recognition / destabilization /
# reframe / stabilization / integration). destabilization + stabilization are
# precisely the roles that fell through the old `if job:` gate.
_REALISTIC_ROLES = [
    "recognition",
    "recognition",
    "destabilization",
    "destabilization",
    "reframe",
    "reframe",
    "reframe",
    "reframe",
    "stabilization",
    "integration",
    "integration",
    "integration",
]
_THESIS = "the alarm fires before the facts arrive and the body braces for a prediction"
_PERSONAS = [
    "gen_alpha_students",
    "corporate_managers",
    "educators",
    "gen_z_professionals",
    "nyc_executives",
    "gen_x_sandwich",
]
_TOPICS = ["anxiety", "burnout", "boundaries", "financial_anxiety"]


def _render_book_bridges(
    *,
    seed: str,
    persona: str,
    topic: str,
    thesis: str = _THESIS,
    roles: list[str] | None = None,
) -> list[str]:
    """Render the thread-forward bridge for every non-final chapter of one book."""
    roles = roles if roles is not None else _REALISTIC_ROLES
    total = len(roles)
    bridge_memory = cc.BridgeMemory()
    out: list[str] = []
    for ch, role in enumerate(roles):
        cc._CHAPTER_INDEX_TLS = ch
        bridge = cc._fallback_thread(
            thesis,
            ch,
            total,
            emotional_job=role,
            bridge_memory=bridge_memory,
            book_seed=seed,
            persona_id=persona,
            topic_id=topic,
        )
        if bridge:
            out.append(bridge)
    return out


# ---------------------------------------------------------------------------
# DEFECT 1 (a): no chapter-bridge repeats >1x within a single book.
# ---------------------------------------------------------------------------

def test_no_bridge_repeats_within_a_single_book() -> None:
    bridges = _render_book_bridges(
        seed="book_seed_1", persona="gen_alpha_students", topic="anxiety"
    )
    assert bridges, "expected at least one inter-chapter bridge"
    counts = Counter(bridges)
    offenders = {b: n for b, n in counts.items() if n > 1}
    assert not offenders, f"bridges repeated >1x within one book: {offenders}"


def test_no_bridge_repeats_across_many_realistic_books() -> None:
    # The 10x-within-a-book scaffolding signature must be gone for every
    # persona/topic, not just one.
    for persona, topic in itertools.product(_PERSONAS, _TOPICS):
        bridges = _render_book_bridges(
            seed=f"seed_{persona}_{topic}", persona=persona, topic=topic
        )
        counts = Counter(bridges)
        max_repeat = max(counts.values()) if counts else 0
        assert max_repeat <= 1, (
            f"{persona} x {topic}: a bridge repeated {max_repeat}x within the book"
        )


# ---------------------------------------------------------------------------
# DEFECT 1 (b): two books with different persona/topic but the same thesis
# produce different bridges (the byte-identical cross-book signature is gone).
# ---------------------------------------------------------------------------

def test_two_books_same_thesis_different_persona_topic_diverge() -> None:
    book_a = _render_book_bridges(
        seed="seed_a", persona="gen_alpha_students", topic="anxiety"
    )
    book_b = _render_book_bridges(
        seed="seed_b", persona="corporate_managers", topic="burnout"
    )
    assert book_a and book_b
    assert book_a != book_b, (
        "two books with the same thesis but different persona/topic produced "
        "byte-identical bridge sequences"
    )


def test_full_book_bridge_sequences_are_distinct_across_population() -> None:
    # Population-level guarantee: no two (persona x topic) books collapse to the
    # same full bridge sequence. This is the strong form of the cross-book
    # byte-identical defect.
    sequences = [
        tuple(
            _render_book_bridges(
                seed=f"seed_{persona}_{topic}", persona=persona, topic=topic
            )
        )
        for persona, topic in itertools.product(_PERSONAS, _TOPICS)
    ]
    assert len(set(sequences)) == len(sequences), (
        "distinct persona/topic books produced identical full bridge sequences"
    )


def test_literal_fallback_no_longer_byte_identical_across_books() -> None:
    # The old code returned ONE constant per thesis keyword regardless of book,
    # so the same chapter index across every book emitted a byte-identical line.
    # With job forced empty (the literal-fallback path), the same thesis+chapter
    # across many books must now span multiple distinct strings.
    cc._CHAPTER_INDEX_TLS = 3
    picks = set()
    for persona, topic in itertools.product(_PERSONAS, _TOPICS):
        picks.add(
            cc._fallback_thread(
                _THESIS,
                3,
                12,
                emotional_job="",  # force the literal fallback path
                bridge_memory=cc.BridgeMemory(),
                book_seed=f"seed_{persona}_{topic}",
                persona_id=persona,
                topic_id=topic,
            )
        )
    assert len(picks) > 1, (
        "literal fallback is still book-agnostic: same thesis+chapter yields a "
        "single byte-identical string across all books"
    )


# ---------------------------------------------------------------------------
# DEFECT 1 (root): arc-role vocab now reaches the data-driven bridge bank.
# ---------------------------------------------------------------------------

def test_arc_roles_resolve_to_bridge_bank_jobs() -> None:
    # recognition/reframe/integration already overlap _EMOTIONAL_JOBS; the
    # gap was destabilization/stabilization (and legacy synonyms).
    assert cc._resolve_emotional_job("destabilization") == "mechanism"
    assert cc._resolve_emotional_job("stabilization") == "resolution"
    assert cc._resolve_emotional_job("landing") == "resolution"
    assert cc._resolve_emotional_job("opening") == "recognition"
    # Pass-through for vocab already in the bank.
    assert cc._resolve_emotional_job("recognition") == "recognition"
    assert cc._resolve_emotional_job("reframe") == "reframe"
    assert cc._resolve_emotional_job("integration") == "integration"
    # Unmappable / empty -> '' (skip the bank, use the literal fallback).
    assert cc._resolve_emotional_job("") == ""
    assert cc._resolve_emotional_job("not_a_role") == ""


def test_destabilization_role_fires_the_data_driven_bank() -> None:
    # Proof the bank is actually reached: its entries are all prefixed
    # "Ahead of you:" (config/rendering/bridge_transition_families.yaml).
    bridge = cc._fallback_thread(
        "the alarm keeps firing before the facts arrive",
        2,
        12,
        emotional_job="destabilization",
        bridge_memory=cc.BridgeMemory(),
    )
    assert bridge.startswith("Ahead of you"), (
        f"data-driven bank was not reached for arc role 'destabilization': {bridge!r}"
    )


# ---------------------------------------------------------------------------
# DEFECT 5: the broadened placeholder detector flags the new stub forms.
# ---------------------------------------------------------------------------

def test_placeholder_detector_flags_new_stub_forms() -> None:
    stub_forms = [
        "[Persona-specific hook for gen_z_professionals × burnout]",
        "[Persona-specific hook for corporate_managers × financial_anxiety]",
        "[persona-specific hook for educators × anxiety]",  # lowercase
        "[Hook for gen_z_professionals × burnout]",
        "[TODO: write the chapter opening]",
        "[TKTK]",
        "[TBD]",
        "[DRAFT hook for X]",
        # original narrow forms must still match
        "[Placeholder: missing hook]",
        "[Missing: scene]",
        "[Silence: no atom]",
    ]
    for stub in stub_forms:
        assert cc._is_placeholder_text(stub), f"failed to flag stub: {stub!r}"


def test_placeholder_detector_does_not_false_positive_on_real_prose() -> None:
    real_prose = [
        "What remains is the moment after the alarm fires, when your body still "
        "wants to obey a prediction.",
        # contains the words 'hook for' but is real prose, not a bracketed stub
        "This is a genuine hook for the reader to hold onto.",
        "Start with the pressure under the sternum. That is the part still bracing.",
        "",
        "   ",
    ]
    for text in real_prose:
        assert not cc._is_placeholder_text(text), f"false positive on: {text!r}"


def test_placeholder_stub_is_suppressed_as_chapter_opening() -> None:
    # End-to-end: a HOOK slot carrying the stub must NOT become the chapter
    # opening line. compose_chapter_prose routes HOOK through _is_placeholder_text.
    stub = "[Persona-specific hook for gen_z_professionals × burnout]"
    prose = cc.compose_chapter_prose(
        slot_types=["HOOK", "REFLECTION"],
        slot_proses=[
            stub,
            "The alarm fires before the facts arrive. The body braces anyway.",
        ],
        chapter_index=0,
        total_chapters=12,
        topic_id="burnout",
        persona_id="gen_z_professionals",
        emotional_role="recognition",
        arc_thesis="the alarm fires before the facts arrive",
    )
    assert stub not in prose, (
        "placeholder HOOK stub leaked into composed chapter prose"
    )
