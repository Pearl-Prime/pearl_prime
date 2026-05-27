"""
Tests for phoenix_v4.quality.register_gate.

Per spec §7 — regression tests for each F1-F7 detector + the calibration
assertion that the gate MUST fail the 2026-05-18 verdict book.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from phoenix_v4.quality.register_gate import (
    _f11_first_paragraph_warns,
    _parse_hook_variation_first_paragraphs,
    evaluate_register,
    evaluate_register_from_path,
    load_hook_atoms_from_paths,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


# ─────────────────────────────────────────────────────────────────────────────
# F1 — templated paragraph repetition
# ─────────────────────────────────────────────────────────────────────────────

def test_f1_warns_on_2_near_duplicate_paragraphs():
    """
    Two paragraphs with high word-set Jaccard overlap should produce F1 WARN.

    Note: the F1 detector uses word-set Jaccard as a proxy for paragraph
    similarity. Two paragraphs about anxiety with DIFFERENT mechanism vocab
    (e.g. "identity anxiety" vs "allostatic load") may share <55% word
    content even though they share template structure — those are flagged
    by the real-book calibration test instead. This unit test verifies that
    near-verbatim repeats DO get flagged.
    """
    para = (
        "The mechanism is hypervigilance as trained response. This is what happens "
        "in the body of the professional when the performance review activates the "
        "system built for survival but now runs in the workplace context. Your thumb "
        "scrolling. Your survival hardware is responding to real inputs. The data "
        "is correct. The output makes sense for the data."
    )
    body = (
        f"Chapter 1\n\n{para}\n\nA different paragraph about coffee and the morning.\n\n"
        f"Chapter 2\n\n{para} The body is the messenger.\n"
    )
    result = evaluate_register(body)
    f1 = [f for f in result.findings if f.failure_id == "F1"]
    assert len(f1) >= 1, "expected at least one F1 finding for the duplicated paragraph template"
    # Cluster size 2 = WARN per spec
    assert any(f.severity == "WARN" for f in f1)


def test_f1_fails_on_3_plus_template_instances():
    """Three+ near-duplicates of the same paragraph template should produce F1 FAIL."""
    template = (
        "The mechanism is {MECH}. This is what happens in the body of the professional "
        "when the unclear career path activates the system that was built for survival "
        "but now runs in the context of the workplace. Your restless legs under the desk. "
        "The vigilance loop is intact. The pressure is genuine. The body is staying in calibration with the pressure."
    )
    body = "Chapter 1\n\n" + template.format(MECH="identity anxiety") + "\n\n"
    body += "Chapter 2\n\n" + template.format(MECH="allostatic load") + "\n\n"
    body += "Chapter 3\n\n" + template.format(MECH="anticipatory anxiety") + "\n\n"
    result = evaluate_register(body)
    f1_fail = [f for f in result.findings if f.failure_id == "F1" and f.severity == "FAIL"]
    assert len(f1_fail) >= 1, "expected at least one F1 FAIL for 3+ instances of the same template"


# ─────────────────────────────────────────────────────────────────────────────
# F2 — broken slot fragments (HARD_FAIL)
# ─────────────────────────────────────────────────────────────────────────────

def test_f2a_hard_fails_on_colon_period_artifact():
    """': .' empty-slot artifact must HARD_FAIL the book."""
    body = "Chapter 1\n\nAhjan's reading of this is precise: .\n\nMore content here.\n"
    result = evaluate_register(body)
    assert result.verdict == "HARD_FAIL"
    assert any(f.failure_id == "F2" and "F2.A" in f.summary for f in result.findings)


def test_f2b_hard_fails_on_dangling_preposition():
    """Paragraph ending with preposition + period must HARD_FAIL."""
    body = "Chapter 1\n\nIn Ahjan's framework, the path begins with.\n\nMore content.\n"
    result = evaluate_register(body)
    assert result.verdict == "HARD_FAIL"
    assert any(f.failure_id == "F2" and "F2.B" in f.summary for f in result.findings)


def test_f2c_hard_fails_on_lowercase_noun_sentence_start():
    """Sentence starting with lowercase noun must HARD_FAIL."""
    body = "Chapter 1\n\nThe pipeline ran. mechanism running continuously is written into your biology.\n"
    result = evaluate_register(body)
    assert result.verdict == "HARD_FAIL"
    assert any(f.failure_id == "F2" and "F2.C" in f.summary for f in result.findings)


def test_f2d_hard_fails_on_sub_4_word_fragment():
    """A 3-word standalone fragment like 'Ahjan's the practice' must HARD_FAIL."""
    body = "Chapter 1\n\nAhjan's the practice\n\nThe next real paragraph here.\n"
    result = evaluate_register(body)
    assert result.verdict == "HARD_FAIL"
    assert any(f.failure_id == "F2" and "F2.D" in f.summary for f in result.findings)


# ─────────────────────────────────────────────────────────────────────────────
# F3 — off-doctrine teacher-bank overrun
# ─────────────────────────────────────────────────────────────────────────────

def test_f3_fails_on_3_plus_off_doctrine_tokens_in_chapter_for_ahjan():
    """ahjan (Tantric Buddhist) book with Krishna + Bhakti + transmission of light = FAIL."""
    body = (
        "Chapter 1\n\n"
        "This direct transmission of light from teacher to student is sacred.\n"
        "Krishna teaches focus through work.\n"
        "Bhakti yoga underscores self-love and balanced relationships.\n"
    )
    result = evaluate_register(body, teacher_id="ahjan")
    f3_fail = [f for f in result.findings if f.failure_id == "F3" and f.severity == "FAIL"]
    assert len(f3_fail) >= 1


def test_f3_no_fire_without_teacher_id():
    """Without teacher_id, F3 is skipped entirely (defaults can't be evaluated)."""
    body = "Chapter 1\n\nKrishna teaches Bhakti yoga. Transmission of light.\n"
    result = evaluate_register(body, teacher_id="")
    f3 = [f for f in result.findings if f.failure_id == "F3"]
    assert len(f3) == 0


# ─────────────────────────────────────────────────────────────────────────────
# F4 — closing-line repetition
# ─────────────────────────────────────────────────────────────────────────────

def test_f4_warns_when_2_chapters_share_closing():
    closing = "What remains is the moment after the alarm fires, when your body still wants to obey a prediction."
    body = (
        f"Chapter 1\n\nSome opening.\nMore content here for length.\nFinal beat. {closing}\n\n"
        f"Chapter 2\n\nDifferent opening.\nDifferent middle.\nDifferent closing beat. {closing}\n"
    )
    result = evaluate_register(body)
    f4 = [f for f in result.findings if f.failure_id == "F4"]
    assert len(f4) == 1
    assert f4[0].severity == "WARN"


def test_f4_fails_when_3_plus_chapters_share_closing():
    closing = "What remains is the moment after the alarm fires, when your body still wants to obey a prediction."
    body = ""
    for i in range(1, 4):
        body += f"Chapter {i}\n\nUnique opening for chapter {i}. Middle filler. {closing}\n\n"
    result = evaluate_register(body)
    f4 = [f for f in result.findings if f.failure_id == "F4"]
    assert any(f.severity == "FAIL" for f in f4)


# ─────────────────────────────────────────────────────────────────────────────
# F6 — pedagogical-cadence 4-gram repetition
# ─────────────────────────────────────────────────────────────────────────────

def test_f6_fails_when_cadence_4gram_repeats_3_plus_times():
    """Same 4-gram sentence-length sequence appearing in 3+ paragraphs across chapters."""
    # Build sentences with fixed word counts that produce identical 4-grams
    # word counts [6, 6, 11, 8] (the audit's known cadence)
    s1 = "The variables are real and concrete."  # 6 words
    s2 = "The stakes are genuine and present."  # 6 words
    s3 = "The uncertainty is not manufactured by your anxiety alone here."  # 11 words
    s4 = "It is manufactured by the surrounding conditions."  # 8 words
    paragraph = " ".join([s1, s2, s3, s4])
    body = ""
    for i in range(1, 5):  # 4 chapters with identical cadence
        body += f"Chapter {i}\n\n{paragraph}\n\n"
    result = evaluate_register(body)
    f6 = [f for f in result.findings if f.failure_id == "F6"]
    assert len(f6) >= 1


# ─────────────────────────────────────────────────────────────────────────────
# F7 — over-prescribed practice density
# ─────────────────────────────────────────────────────────────────────────────

def test_f7_fails_when_chapter_has_4_plus_distinct_practices():
    body = (
        "Chapter 1\n\n"
        "Try this for ninety seconds: notice where your attention is scanning.\n\n"
        "Breathe in through your nose for four counts. Hold for two seconds. Out for six.\n\n"
        "Notice a thought that repeats itself in your mind. Follow it back step by step.\n\n"
        "Write the prediction your mind is treating like a fact for the next five minutes.\n\n"
    )
    result = evaluate_register(body)
    f7 = [f for f in result.findings if f.failure_id == "F7" and f.severity == "FAIL"]
    assert len(f7) >= 1


# ─────────────────────────────────────────────────────────────────────────────
# Verdict aggregation
# ─────────────────────────────────────────────────────────────────────────────

def test_clean_book_passes():
    body = (
        "Chapter 1\n\nA clean opening paragraph with embodied prose. The body knows. The chest tightens once. The breath returns.\n\n"
        "Another paragraph with a different texture entirely. Eyes open. Hands on the desk. The morning continues.\n\n"
        "Chapter 2\n\nA different opening. New scene, new character. The light comes in through different windows.\n\n"
        "Different details. Different beat. Different closing line for this chapter that is wholly its own.\n\n"
        "Chapter 3\n\nMore variety. The third chapter takes a third angle. Specific somatic detail throughout.\n\n"
        "Yet another distinct closing that does not mirror the prior chapters at all whatsoever.\n"
    )
    result = evaluate_register(body)
    # Note: without active F1-F7 triggers, should be PASS or ADVISORY
    assert result.verdict in {"PASS", "ADVISORY"}, f"clean book got verdict={result.verdict} with findings={result.findings}"


def test_hard_fail_short_circuits():
    """Any F2 violation produces HARD_FAIL regardless of other findings."""
    body = "Chapter 1\n\nClean clean clean. But this colon: .\n"
    result = evaluate_register(body)
    assert result.verdict == "HARD_FAIL"


# ─────────────────────────────────────────────────────────────────────────────
# Calibration assertion — the gate MUST FAIL the 2026-05-18 verdict book
# ─────────────────────────────────────────────────────────────────────────────

CALIBRATION_BOOK = (
    REPO_ROOT
    / "artifacts"
    / "pearl_prime"
    / "extended_book_2h"
    / "ahjan_gen_z_professionals_anxiety_en_US_20260518T131809Z_round5"
    / "book.txt"
)


# ─────────────────────────────────────────────────────────────────────────────
# F11 — HOOK atom first-paragraph abstract opening (HOOK-SCENE-FIRST-01)
# ─────────────────────────────────────────────────────────────────────────────

SCENE_FIRST_HOOK_V01 = (
    "Diane woke at 3:14am with her heart already ahead of her, cataloging everything "
    "that could go wrong before she'd opened her eyes."
)

PHILOSOPHY_FIRST_HOOK_V01 = (
    "Your worth is your business. Your business is your worth. So every decision "
    "becomes a referendum on your value as a human."
)

MIKI_SCENE_FIRST = (
    "Somewhere right now, a person is sitting in a bathroom stall at their new job, "
    "pressing their phone against their thigh so nobody hears the screen light up, "
    "breathing through their mouth because their nose is too congested from the silent "
    "crying they did in the car on the way here."
)

OMOTE_PHILOSOPHY_FIRST = (
    "Nightfall strips the surface away. This happens automatically, without consent "
    "and without ceremony. The lights go off."
)

MIXED_HOOK_ATOM = """## HOOK v01
---

---
Awareness is the first casualty of a busy mind. The thoughts arrive before the body does.
---

## HOOK v02
---

---
She sat in the kitchen at 5am, hands wrapped around a cold mug, listening to the refrigerator hum.
---
"""


def test_f11_scene_first_paragraph_passes():
    warns, _meta = _f11_first_paragraph_warns(SCENE_FIRST_HOOK_V01)
    assert warns is False


def test_f11_philosophy_first_paragraph_warns():
    warns, meta = _f11_first_paragraph_warns(PHILOSOPHY_FIRST_HOOK_V01)
    assert warns is True
    assert meta.get("abstract_opening") is True


def test_f11_miki_reference_scene_first_passes():
    warns, _meta = _f11_first_paragraph_warns(MIKI_SCENE_FIRST)
    assert warns is False


def test_f11_omote_reference_philosophy_first_warns():
    warns, meta = _f11_first_paragraph_warns(OMOTE_PHILOSOPHY_FIRST)
    assert warns is True
    assert meta.get("abstract_opening") is True


def test_f11_mixed_atom_warns_on_v01_only():
    variations = _parse_hook_variation_first_paragraphs(MIXED_HOOK_ATOM)
    assert variations[0][0] == "v01"
    warns_v01, _ = _f11_first_paragraph_warns(variations[0][1])
    warns_v02, _ = _f11_first_paragraph_warns(variations[1][1])
    assert warns_v01 is True
    assert warns_v02 is False


def test_f11_register_gate_integration_five_atom_sample():
    """Full register run with 5 HOOK atoms from HOOK-SCENE-FIRST-01 empirical sample."""
    atom_fixtures = [
        ("atoms/midlife_women/anxiety/HOOK/CANONICAL.txt", SCENE_FIRST_HOOK_V01),
        (
            "atoms/entrepreneurs/anxiety/HOOK/CANONICAL.txt",
            "Your chest tightens when the client goes silent. The invoice sits unpaid and the email sits unopened.",
        ),
        (
            "atoms/midlife_women/imposter_syndrome/HOOK/CANONICAL.txt",
            "She has twenty-two years of experience and a graduate degree and she still lowers her voice slightly when she speaks in the Monday meeting.",
        ),
        (
            "atoms/midlife_women/sleep_anxiety/HOOK/CANONICAL.txt",
            "She wakes at 3:17am and the night sweats have already passed and now it's the thoughts.",
        ),
        ("atoms/entrepreneurs/overthinking/HOOK/CANONICAL.txt", PHILOSOPHY_FIRST_HOOK_V01),
    ]
    hook_atoms = []
    for path, first_para in atom_fixtures:
        hook_atoms.append((
            path,
            f"## HOOK v01\n---\n\n---\n{first_para}\n---\n",
        ))
    body = "Chapter 1\n\nMinimal rendered book body for F11 integration.\n"
    result = evaluate_register(body, hook_atoms=hook_atoms)
    f11 = [f for f in result.findings if f.failure_id == "F11"]
    assert len(f11) == 1
    assert f11[0].severity == "WARN"
    assert "overthinking" in f11[0].evidence["atom_path"]
    assert "Your worth" in f11[0].evidence["evidence_snippet"]


HOOK_ATOM_PATHS = [
    REPO_ROOT / "atoms/midlife_women/anxiety/HOOK/CANONICAL.txt",
    REPO_ROOT / "atoms/entrepreneurs/anxiety/HOOK/CANONICAL.txt",
    REPO_ROOT / "atoms/midlife_women/imposter_syndrome/HOOK/CANONICAL.txt",
    REPO_ROOT / "atoms/midlife_women/sleep_anxiety/HOOK/CANONICAL.txt",
    REPO_ROOT / "atoms/entrepreneurs/overthinking/HOOK/CANONICAL.txt",
]


@pytest.mark.skipif(
    not all(p.exists() for p in HOOK_ATOM_PATHS),
    reason="HOOK atom corpus not checked out in this worktree",
)
def test_f11_integration_on_disk_hook_corpus_sample():
    # NOTE (HOOK-SCENE-FIRST-01 P0+P1 rewrites, 2026-05-27):
    # Pearl_Editor rewrote 41 P0 HOOK atoms in PR #1336 and 100 P1 atoms in this PR
    # (including entrepreneurs/overthinking) to scene-first. All 5 atoms in HOOK_ATOM_PATHS
    # now open scene-first so F11 correctly returns 0 findings. The synthetic
    # test_f11_integration_full_loop above still exercises the detector on a known-bad fixture.
    hook_atoms = load_hook_atoms_from_paths(HOOK_ATOM_PATHS)
    result = evaluate_register("Chapter 1\n\nRendered hook chapter placeholder.\n", hook_atoms=hook_atoms)
    f11 = [f for f in result.findings if f.failure_id == "F11"]
    assert len(f11) == 0, (
        f"Expected 0 F11 WARN findings on P0+P1 corpus sample (all 5 rewritten scene-first); "
        f"got {len(f11)}: {[f.evidence.get('atom_path') for f in f11]}"
    )


@pytest.mark.skipif(not CALIBRATION_BOOK.exists(), reason="calibration book not on disk in this worktree")
def test_calibration_book_must_fail():
    """
    Per spec §7: applying the gate to the 2026-05-18 verdict book must
    produce a FAIL or HARD_FAIL verdict. If it passes, thresholds are too lenient.
    """
    result = evaluate_register_from_path(
        CALIBRATION_BOOK,
        teacher_id="ahjan",
        persona_id="gen_z_professionals",
        topic_id="anxiety",
    )
    assert result.verdict in {"FAIL", "HARD_FAIL"}, (
        f"calibration book got verdict={result.verdict} — register gate thresholds "
        f"are too lenient. Findings: {len(result.findings)}"
    )
    # Specifically, the audit identified F1, F2, F3, F4 as definite failures
    failure_ids = {f.failure_id for f in result.findings}
    for fid in {"F1", "F2", "F3", "F4"}:
        assert fid in failure_ids, f"expected {fid} finding on calibration book; got {failure_ids}"
