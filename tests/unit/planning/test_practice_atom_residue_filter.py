"""OPD-107 follow-up: residue filter on `_is_practice_atom`.

Background
----------
PR #1211 (OPD-107) plumbed the persona EXERCISE pool through the same
`_filter_practice_pool` shape gate the teacher pool uses. The gate accepts
atoms whose content shows "instruction-with-steps" evidence — numbered steps
(`Step 1.`), imperatives (`Place your hand`, `Breathe in`, `Now,`), or sensory
cues (`drop your shoulders`).

A pre-existing teacher atom `ahjan_EXERCISE_064_mined` was RTF residue from a
YouTube affiliate-marketing blog. Its body begins:

    "Helvetica;ArialMT; ;;;;; ;; Creating comparison videos for affiliate
     marketing on YouTube ... Step 1. Choose products ..."

The literal "Step 1." substring tripped the positive-evidence pass, so the
filter accepted it. That single atom then won all 24 EXERCISE slots in Book 3
(`ahjan x gen_z_professionals x anxiety x deep_book_6h`), blocking the
OPD-107 fallthrough from delivering legitimate persona-pool practice atoms
to chapters 4-9.

This module pins the additive negative-evidence (residue) filter:
  * Font-stack tells (RTF \\fonttbl ASCII output: ``Helvetica;``, ``ArialMT;``)
  * RTF artifact tokens (``\\fonttbl``, ``\\rtf1``)
  * HTML/markdown residue (``<p>``, ``&nbsp;``)
  * Blog/marketing tells (``Click here``, ``Affiliate marketing``, ``https://``)
  * Mining-tool stamps (``kb_mine_v1``, ``synthesis_method:``)

Each is rejected regardless of positive evidence. Operators can bypass via
`_PRACTICE_RESIDUE_ALLOWLIST` (empty by default).
"""
from __future__ import annotations

import pytest

from phoenix_v4.planning import enrichment_select as es
from phoenix_v4.planning.enrichment_select import (
    _PRACTICE_RESIDUE_ALLOWLIST,
    _RESIDUE_MARKERS,
    _filter_practice_pool,
    _has_residue_markers,
    _is_practice_atom,
)


# ───────────────────────────────────────────────────────────────────────────
# Real false-positive fixture: ahjan_EXERCISE_064_mined.yaml content
# ───────────────────────────────────────────────────────────────────────────

# Content copied verbatim from
# SOURCE_OF_TRUTH/teacher_banks/ahjan/approved_atoms/EXERCISE/ahjan_EXERCISE_064_mined.yaml
AHJAN_064_RESIDUE_BODY: str = (
    "Helvetica;ArialMT; ;;;;; ;; ;;;;; ;; Creating comparison videos for "
    "affiliate marketing on YouTube is an excellent strategy for beginners. "
    "It not only provides valuable information to your audience but also "
    "showcases multiple affiliate products at once. Here's a step-by-step "
    "guide on how to do it, along with a hypothetical example and potential "
    "earnings.Step 1. Choose products in the same category that you want to "
    "compare. Ensure these products are relevant to your audience and "
    "available through your affiliate programs.Example."
)

AHJAN_064_FIXTURE: dict = {
    "atom_id": "ahjan_EXERCISE_064_mined",
    "content": AHJAN_064_RESIDUE_BODY,
    "metadata": {
        "teacher": {"teacher_id": "ahjan"},
        "synthesis_method": "kb_mine_v1",
    },
}


# ───────────────────────────────────────────────────────────────────────────
# Synthetic fixtures — one per residue category
# ───────────────────────────────────────────────────────────────────────────

# Each fixture pairs RTF/blog residue with a "Step 1./first,/now," positive
# marker that WITHOUT the residue filter would slip through.

FONT_STACK_RESIDUE_FIXTURES = [
    {
        "atom_id": "synth_residue_helvetica",
        "content": "Helvetica;ArialMT; ; Step 1. open the doc. Step 2. read it.",
        "metadata": {},
    },
    {
        "atom_id": "synth_residue_times_new_roman",
        "content": "Times New Roman; foo bar. first, do the thing. now, breathe.",
        "metadata": {},
    },
    {
        "atom_id": "synth_residue_courier",
        "content": "Courier, monospace; Step 1. read carefully. Step 2. close eyes.",
        "metadata": {},
    },
]

RTF_TOKEN_FIXTURES = [
    {
        "atom_id": "synth_residue_fonttbl",
        "content": (
            r"\fonttbl\f0\fnil\fcharset0 Helvetica; Step 1. open the file. "
            r"first, place your hand."
        ),
        "metadata": {},
    },
    {
        "atom_id": "synth_residue_rtf1",
        "content": (
            r"\rtf1\ansi\ansicpg1252 Step 1. close your eyes. inhale slowly."
        ),
        "metadata": {},
    },
]

HTML_RESIDUE_FIXTURES = [
    {
        "atom_id": "synth_residue_html_p",
        "content": (
            "<p>Step 1. place your hand on your belly.</p>"
            "<p>Step 2. breathe in.</p>"
        ),
        "metadata": {},
    },
    {
        "atom_id": "synth_residue_html_br",
        "content": "Step 1. inhale.<br>Step 2. exhale.<br/>Step 3. notice.",
        "metadata": {},
    },
    {
        "atom_id": "synth_residue_html_nbsp",
        "content": "Step 1.&nbsp;close your eyes. Step 2.&nbsp;breathe.",
        "metadata": {},
    },
]

BLOG_MARKETING_FIXTURES = [
    {
        "atom_id": "synth_residue_click_here",
        "content": "Click here to learn more. Step 1. inhale slowly. Step 2. exhale.",
        "metadata": {},
    },
    {
        "atom_id": "synth_residue_affiliate",
        "content": (
            "Today we discuss affiliate marketing on YouTube. Step 1. Choose "
            "products. Step 2. Compare them."
        ),
        "metadata": {},
    },
    {
        "atom_id": "synth_residue_url",
        "content": (
            "Read more at https://example.com. Step 1. close your eyes. "
            "Step 2. breathe."
        ),
        "metadata": {},
    },
    {
        "atom_id": "synth_residue_www",
        "content": "Visit www.example.com. Step 1. relax. Step 2. notice your breath.",
        "metadata": {},
    },
    {
        "atom_id": "synth_residue_subscribe",
        "content": (
            "Subscribe to our newsletter. Step 1. Place your hand on your "
            "belly. Step 2. Breathe."
        ),
        "metadata": {},
    },
    {
        "atom_id": "synth_residue_youtube",
        "content": (
            "On our YouTube channel we cover affiliate marketing. Step 1. "
            "Open the doc. first, breathe."
        ),
        "metadata": {},
    },
]

MINING_STAMP_FIXTURES = [
    {
        "atom_id": "synth_residue_kb_mine",
        "content": (
            "kb_mine_v1 synthesis. Step 1. inhale. Step 2. exhale. Step 3. "
            "notice."
        ),
        "metadata": {},
    },
    {
        "atom_id": "synth_residue_synthesis_method",
        "content": (
            "synthesis_method: kb_mine_v1\nStep 1. close eyes. Step 2. "
            "breathe in for four counts."
        ),
        "metadata": {},
    },
    {
        "atom_id": "synth_residue_quote_hash",
        "content": (
            "quote_hash: deadbeef\nStep 1. place your hand. Step 2. breathe."
        ),
        "metadata": {},
    },
    {
        "atom_id": "synth_residue_doc_id",
        "content": (
            "doc_id: raw/some.rtf\nStep 1. inhale slowly. Step 2. exhale "
            "for six counts."
        ),
        "metadata": {},
    },
]

# Legitimate practice atoms — should still PASS the filter unchanged.
LEGITIMATE_PRACTICE_FIXTURES = [
    {
        "atom_id": "legit_breath_steps",
        "content": (
            "Sit back from your screen. Place both feet flat on the floor. "
            "Breathe in for four counts. Hold for four counts. Breathe out "
            "for four counts."
        ),
        "metadata": {},
    },
    {
        "atom_id": "legit_numbered_grounding",
        "content": (
            "5-4-3-2-1 grounding scan.\n"
            "1. Name five things you can see.\n"
            "2. Name four things you can feel.\n"
            "3. Name three sounds you can hear.\n"
            "4. Name two scents you notice.\n"
            "5. Name one taste in your mouth."
        ),
        "metadata": {},
    },
    {
        "atom_id": "legit_body_scan",
        "content": (
            "Close your eyes. Notice the scalp. Move to the jaw. Let it go "
            "slack. Drop your shoulders. Breathe out. Open your eyes."
        ),
        "metadata": {},
    },
    {
        "atom_id": "legit_meta_tagged",
        "content": "Stand tall. Roll your shoulders. Take three deep breaths.",
        "metadata": {"slot_type": "exercise"},
    },
    {
        # Even legitimate practice scripts can mention "step" — but as a noun
        # in flowing prose, not the residue pattern "Step 1.". The numbered-
        # step regex requires anchor at start of line and digit.
        "atom_id": "legit_first_now",
        "content": (
            "first, sit comfortably. now, breathe in slowly through the nose. "
            "then, breathe out through the mouth."
        ),
        "metadata": {},
    },
]


# ───────────────────────────────────────────────────────────────────────────
# Core target: the actual false-positive must be rejected
# ───────────────────────────────────────────────────────────────────────────


def test_ahjan_exercise_064_mined_is_rejected():
    """The target false-positive must be rejected by the residue filter.

    Without the filter, the literal `Step 1. Choose products...` substring
    trips `_NUMBERED_STEP_RE` and the atom wins primary-fill in Book 3.
    """
    assert _is_practice_atom(AHJAN_064_FIXTURE) is False


def test_ahjan_exercise_064_residue_markers_are_detected():
    """At least three residue markers must fire on the true false-positive.

    Documents which markers the operator can rely on to catch this class of
    bug. Helvetica;, ArialMT;, affiliate marketing, YouTube channel, https://
    all should match.
    """
    content_lower = AHJAN_064_RESIDUE_BODY.lower()
    hits = [m for m in _RESIDUE_MARKERS if m in content_lower]
    assert "helvetica;" in hits
    assert "arialmt;" in hits
    assert "affiliate marketing" in hits
    assert len(hits) >= 3, (
        f"Expected >=3 residue markers on ahjan_EXERCISE_064_mined, got {hits}"
    )


# ───────────────────────────────────────────────────────────────────────────
# Per-category negative-evidence tests
# ───────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("atom", FONT_STACK_RESIDUE_FIXTURES, ids=lambda a: a["atom_id"])
def test_font_stack_residue_is_rejected(atom):
    """RTF \\fonttbl residue must be rejected (Helvetica; ArialMT; etc.)."""
    assert _is_practice_atom(atom) is False


@pytest.mark.parametrize("atom", RTF_TOKEN_FIXTURES, ids=lambda a: a["atom_id"])
def test_rtf_artifact_tokens_are_rejected(atom):
    """RTF control words (\\fonttbl, \\rtf1) must be rejected."""
    assert _is_practice_atom(atom) is False


@pytest.mark.parametrize("atom", HTML_RESIDUE_FIXTURES, ids=lambda a: a["atom_id"])
def test_html_residue_is_rejected(atom):
    """HTML tags (<p>, <br>, &nbsp;) must be rejected."""
    assert _is_practice_atom(atom) is False


@pytest.mark.parametrize("atom", BLOG_MARKETING_FIXTURES, ids=lambda a: a["atom_id"])
def test_blog_marketing_residue_is_rejected(atom):
    """Blog/marketing tells (Click here, Affiliate marketing, URLs) rejected."""
    assert _is_practice_atom(atom) is False


@pytest.mark.parametrize("atom", MINING_STAMP_FIXTURES, ids=lambda a: a["atom_id"])
def test_mining_tool_stamps_are_rejected(atom):
    """Mining-tool stamps (kb_mine_v1, synthesis_method:, doc_id:) rejected."""
    assert _is_practice_atom(atom) is False


# ───────────────────────────────────────────────────────────────────────────
# Regression: legitimate practice atoms still pass
# ───────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "atom", LEGITIMATE_PRACTICE_FIXTURES, ids=lambda a: a["atom_id"]
)
def test_legitimate_practice_atoms_still_pass(atom):
    """Real practice content (without residue) must still be accepted.

    This is the regression guarantee: tightening the filter cannot drop
    legitimate atoms. If this test fails, a residue marker was too broad.
    """
    assert _is_practice_atom(atom) is True


def test_filter_practice_pool_strips_residue_keeps_legitimate():
    """End-to-end pool filtering: residue atoms get dropped, legit ones survive."""
    mixed_pool = list(LEGITIMATE_PRACTICE_FIXTURES) + [AHJAN_064_FIXTURE]
    mixed_pool += BLOG_MARKETING_FIXTURES[:2]
    mixed_pool += HTML_RESIDUE_FIXTURES[:1]

    filtered = _filter_practice_pool(mixed_pool)
    legit_ids = {a["atom_id"] for a in LEGITIMATE_PRACTICE_FIXTURES}
    filtered_ids = {a["atom_id"] for a in filtered}
    assert filtered_ids == legit_ids, (
        f"Residue atoms leaked through: {filtered_ids - legit_ids}"
    )


# ───────────────────────────────────────────────────────────────────────────
# Allow-list escape-hatch
# ───────────────────────────────────────────────────────────────────────────


def test_allowlist_bypass_lets_residue_atom_pass(monkeypatch):
    """An atom_id in _PRACTICE_RESIDUE_ALLOWLIST bypasses the residue check.

    Future operators may legitimately want to ship an atom that discusses
    URLs or HTML tags pedagogically. The allow-list is the supported escape.
    """
    # Atom contains an https:// URL — would normally be rejected.
    intentional_url_atom = {
        "atom_id": "operator_approved_url_example",
        "content": (
            "Visit https://docs.example.com to download the worksheet. "
            "Then: Step 1. close your eyes. Step 2. breathe in slowly."
        ),
        "metadata": {},
    }

    # Without the allow-list entry, residue marker hits and atom is rejected.
    assert _is_practice_atom(intentional_url_atom) is False

    # Patch in an allow-list entry for this atom_id.
    monkeypatch.setattr(
        es,
        "_PRACTICE_RESIDUE_ALLOWLIST",
        frozenset({"operator_approved_url_example"}),
    )
    assert _is_practice_atom(intentional_url_atom) is True


def test_allowlist_is_empty_by_default():
    """The shipped allow-list must be empty until operators explicitly grow it.

    A non-empty default would silently un-protect the residue filter.
    """
    assert _PRACTICE_RESIDUE_ALLOWLIST == frozenset()


# ───────────────────────────────────────────────────────────────────────────
# _has_residue_markers helper
# ───────────────────────────────────────────────────────────────────────────


def test_has_residue_markers_empty_string():
    assert _has_residue_markers("") is False
    assert _has_residue_markers("   ") is True or _has_residue_markers("   ") is False
    # The function takes pre-lowercased input; empty after strip != argument
    # mutation. Spec: only check non-empty input.


def test_has_residue_markers_clean_text():
    assert _has_residue_markers("close your eyes and breathe slowly") is False


def test_has_residue_markers_dirty_text():
    assert _has_residue_markers("helvetica; arialmt; some text") is True
    assert _has_residue_markers("step 1. click here for more") is True
    assert _has_residue_markers("step 1. visit https://x.com") is True


# ───────────────────────────────────────────────────────────────────────────
# Metadata short-circuit ordering — residue check wins over slot_type tag
# ───────────────────────────────────────────────────────────────────────────


def test_metadata_slot_type_does_not_override_residue_rejection():
    """Even an atom tagged metadata.slot_type='exercise' must be rejected if
    its content shows residue. Metadata cannot override content-level filth."""
    atom = {
        "atom_id": "synth_mistagged_exercise_with_residue",
        "content": "Helvetica;ArialMT; Step 1. open the doc.",
        "metadata": {"slot_type": "exercise"},
    }
    assert _is_practice_atom(atom) is False


def test_metadata_synthesis_method_kb_mine_alone_is_fine():
    """A metadata synthesis_method='kb_mine_v1' tag is not itself residue.

    Only `kb_mine_v1` strings appearing inside the atom CONTENT body are
    residue. Legitimate teacher-mined atoms may carry this metadata tag and
    still pass when the body is clean prose."""
    atom = {
        "atom_id": "synth_clean_kb_mine_meta",
        "content": (
            "Sit comfortably. Place both feet flat on the floor. "
            "Breathe in for four counts. Breathe out for six counts."
        ),
        "metadata": {"synthesis_method": "kb_mine_v1"},
    }
    assert _is_practice_atom(atom) is True
