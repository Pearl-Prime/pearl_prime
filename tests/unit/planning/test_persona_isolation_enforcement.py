"""
OPD-118 — persona-isolation enforcement tests for deep_book_6h selector.

Defect:
    `_merged_persona_atoms_deep_6h` (introduced PR #939 Sprint-1) merged
    HOOK/SCENE/STORY atoms from EVERY persona that shared the rendered topic.
    A `gen_z_professionals × anxiety` render was pulling HOOK content from
    `tech_finance_burnout/anxiety/HOOK/` (trading floor),
    `first_responders/anxiety/HOOK/` (fire station), and
    `corporate_managers/anxiety/HOOK/` (executive suite). The stitched prose
    read as scene-hopping across incompatible settings — this is the root
    cause of the operator's persistent "scene-scene-scene / all over the
    place" Book 3 complaint.

Fix (OPD-118): `_merged_persona_atoms_deep_6h` now loads atoms ONLY from
`atoms/{primary_persona}/{topic}/`. Empty target pool → planner WARNING,
NOT silent spill into siblings.

These tests cover:
    1. Cross-persona contamination is BLOCKED (the regression test).
    2. Cross-topic contamination is BLOCKED.
    3. Empty target pool returns {} with WARNING (no silent spill).
    4. Teacher-bank atoms still load (positive control — only persona-pool
       contamination is blocked).
    5. Practice-library atoms still load (positive control for EXERCISE backstop).
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List

import pytest

from phoenix_v4.planning import enrichment_select as es
from phoenix_v4.planning import registry_resolver as rr


# ---------------------------------------------------------------------------
# Fixtures — synthetic atoms directory layered as the real layout.
# ---------------------------------------------------------------------------


def _write_canonical(slot_dir: Path, atoms: List[Dict[str, str]]) -> None:
    """Write atoms to {slot_dir}/CANONICAL.txt in the parser-expected format."""
    slot_dir.mkdir(parents=True, exist_ok=True)
    body_lines: List[str] = []
    for atom in atoms:
        body_lines.append(f"## {atom['id']}")
        body_lines.append("---")
        body_lines.append("---")
        body_lines.append(atom["content"])
        body_lines.append("---")
        body_lines.append("")
    (slot_dir / "CANONICAL.txt").write_text("\n".join(body_lines), encoding="utf-8")


@pytest.fixture
def atoms_fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """
    Build a synthetic atoms/ tree with four personas × anxiety topic + a
    `compassion_fatigue` cross-topic decoy to cover (1)-(2).

    Personas:
      - gen_z_professionals: full HOOK/SCENE/STORY (target persona)
      - tech_finance_burnout: decoy HOOK content (cross-persona contamination test)
      - first_responders: decoy HOOK content
      - corporate_managers: decoy HOOK content + cross-topic compassion_fatigue
    """
    atoms_root = tmp_path / "atoms"
    monkeypatch.setattr(rr, "ATOMS_ROOT", atoms_root)

    # Target persona: gen_z_professionals × anxiety — clean atoms
    _write_canonical(
        atoms_root / "gen_z_professionals" / "anxiety" / "HOOK",
        [
            {"id": "HOOK v01", "content":
             "The deadline for the launch was yesterday. Your slack pings keep "
             "arriving while your coffee cools. This is the gen_z_professionals "
             "voice and you can feel the spiral start."},
            {"id": "HOOK v02", "content":
             "Open laptop at 11pm to finish the deck nobody asked for. The "
             "remote-work isolation rises like a tide and your jaw tightens "
             "with each new thread."},
            {"id": "HOOK v03", "content":
             "Standup meeting cameras-on at 9am and the imposter syndrome "
             "lights up before your manager has even said good morning."},
        ],
    )
    _write_canonical(
        atoms_root / "gen_z_professionals" / "anxiety" / "SCENE",
        [
            {"id": "SCENE v01", "content":
             "Open the doordash app and stare at the screen. You scroll past "
             "the same three places you always order from and the choice "
             "paralysis lands like a slow weight in your chest."},
            {"id": "SCENE v02", "content":
             "Sit in the wework phone booth and listen to your heartbeat in "
             "the silence. The gen_z professional vibe is unmistakable here."},
            {"id": "SCENE v03", "content":
             "Notice the unread messages stacking in your DMs. Each one is a "
             "small obligation and the social anxiety begins to climb."},
        ],
    )
    _write_canonical(
        atoms_root / "gen_z_professionals" / "anxiety" / "STORY",
        [
            {"id": "STORY v01", "content":
             "Maya, twenty-six, software developer, opened her laptop at "
             "eleven pm and felt the familiar squeeze of the next-day deadline "
             "begin to fold around her shoulders. Her room was quiet."},
            {"id": "STORY v02", "content":
             "Devon got the promotion he had been hustling for and the next "
             "morning his anxiety was worse, not better. The imposter voice "
             "in his head got louder once the title was real."},
            {"id": "STORY v03", "content":
             "Priya's slack notifications hit forty before lunch and she felt "
             "her shoulders climb up toward her ears like they always did "
             "when the urgency was performative."},
        ],
    )
    _write_canonical(
        atoms_root / "gen_z_professionals" / "anxiety" / "REFLECTION",
        [
            {"id": "REFLECTION v01", "content":
             "Anxiety in your twenties is often the body trying to keep you "
             "safe in a world where the rules keep changing. The threat is "
             "real to the nervous system even when nothing is actually wrong."},
            {"id": "REFLECTION v02", "content":
             "The way you were taught to grind through it as a young "
             "professional is exactly the strategy that keeps the loop going. "
             "Productivity culture sells the cure that creates the disease."},
            {"id": "REFLECTION v03", "content":
             "You were not built to be a perpetual machine of response and "
             "the somatic exhaustion you feel is information, not weakness."},
        ],
    )

    # CROSS-PERSONA DECOY: tech_finance_burnout × anxiety HOOK (must NEVER appear)
    _write_canonical(
        atoms_root / "tech_finance_burnout" / "anxiety" / "HOOK",
        [
            {"id": "HOOK v01", "content":
             "Jaw clenched on the commute home at 6pm. Your trading floor "
             "metrics for the quarter just slipped and you can feel the loss "
             "ratio climb behind your ribs."},
            {"id": "HOOK v02", "content":
             "The fund manager copied you on the email at four am again. Your "
             "client portfolio is short by twelve million and the markets open "
             "in ninety minutes."},
            {"id": "HOOK v03", "content":
             "Bloomberg terminal on, three monitors lit, and the spread is "
             "moving against you. You haven't blinked in two minutes."},
        ],
    )

    # CROSS-PERSONA DECOY: first_responders × anxiety HOOK
    _write_canonical(
        atoms_root / "first_responders" / "anxiety" / "HOOK",
        [
            {"id": "HOOK v01", "content":
             "A car backfires two blocks away and your hand goes to your duty "
             "belt before your brain catches up. Fire engine sirens still "
             "trigger the cortisol cascade three months after the call."},
            {"id": "HOOK v02", "content":
             "The firefighter you trained with last year is the same one who "
             "didn't come home. You haven't worked a shift since the funeral "
             "and your wife is asking when you'll go back."},
            {"id": "HOOK v03", "content":
             "First responder shift report at five am and you can feel the "
             "shake in your hands when you pick up the coffee mug."},
        ],
    )

    # CROSS-PERSONA DECOY: corporate_managers × anxiety HOOK
    _write_canonical(
        atoms_root / "corporate_managers" / "anxiety" / "HOOK",
        [
            {"id": "HOOK v01", "content":
             "The reorg announcement hits your inbox at 2 PM. You have three "
             "hours before your team asks for reassurance you can't promise. "
             "Your hands are cold before the meeting even starts."},
            {"id": "HOOK v02", "content":
             "You have a direct report waiting on the performance review you "
             "must give and the words won't come. The C-suite expects a "
             "decision by end of day."},
            {"id": "HOOK v03", "content":
             "Middle management at forty-eight and the equity vests in two "
             "more years. You haven't slept through the night since q2."},
        ],
    )

    # CROSS-TOPIC DECOY: corporate_managers × compassion_fatigue
    # (used in cross-topic isolation tests — must never appear in anxiety pulls)
    _write_canonical(
        atoms_root / "corporate_managers" / "compassion_fatigue" / "INTEGRATION",
        [
            {"id": "INTEGRATION v01", "content":
             "The middle management role chews through your reserves week by "
             "week until you can't tell whose grief is whose. The reorg "
             "announcement was the third one this year."},
            {"id": "INTEGRATION v02", "content":
             "Compassion fatigue is what happens when the witnessing exceeds "
             "the recovering. You haven't had a quiet morning in six months."},
        ],
    )

    return atoms_root


# ---------------------------------------------------------------------------
# Test 1: cross-PERSONA contamination is BLOCKED.
# ---------------------------------------------------------------------------


def test_no_cross_persona_atoms_in_merged_pool(atoms_fixture: Path) -> None:
    """
    Confirm that `_merged_persona_atoms_deep_6h(gen_z_professionals, anxiety)`
    returns ZERO atoms from `tech_finance_burnout`, `first_responders`, or
    `corporate_managers` — even though all four personas have HOOK/SCENE/STORY
    populated for the same `anxiety` topic.
    """
    merged = es._merged_persona_atoms_deep_6h(
        "gen_z_professionals", "anxiety", atoms_fixture, locale=None
    )

    # Collect every body in every slot of the returned pool.
    all_bodies: List[str] = []
    for slot_atoms in merged.values():
        for atom in slot_atoms:
            all_bodies.append(str(atom.get("content") or ""))
    joined = "\n".join(all_bodies)

    # tech_finance_burnout signature phrases
    assert "Jaw clenched on the commute home at 6pm" not in joined, (
        "OPD-118 regression: tech_finance_burnout HOOK content leaked into "
        "gen_z_professionals/anxiety pool"
    )
    assert "trading floor" not in joined
    assert "Bloomberg terminal" not in joined

    # first_responders signature phrases
    assert "A car backfires two blocks away" not in joined, (
        "OPD-118 regression: first_responders HOOK content leaked into "
        "gen_z_professionals/anxiety pool"
    )
    assert "firefighter" not in joined
    assert "First responder shift report" not in joined

    # corporate_managers signature phrases
    assert "The reorg announcement hits your inbox at 2 PM" not in joined, (
        "OPD-118 regression: corporate_managers HOOK content leaked into "
        "gen_z_professionals/anxiety pool"
    )
    assert "direct report waiting on the performance review" not in joined
    assert "Middle management at forty-eight" not in joined


# ---------------------------------------------------------------------------
# Test 2: cross-TOPIC contamination is BLOCKED.
# ---------------------------------------------------------------------------


def test_no_cross_topic_atoms_in_merged_pool(atoms_fixture: Path) -> None:
    """
    Confirm `_merged_persona_atoms_deep_6h(gen_z_professionals, anxiety)`
    returns ZERO atoms from `compassion_fatigue` (a different topic with
    overlapping persona but unrelated theme).
    """
    merged = es._merged_persona_atoms_deep_6h(
        "gen_z_professionals", "anxiety", atoms_fixture, locale=None
    )

    all_bodies = "\n".join(
        str(atom.get("content") or "")
        for slot_atoms in merged.values()
        for atom in slot_atoms
    )

    # compassion_fatigue signature phrases — even though the persona
    # corporate_managers shares the same content, it's a wrong-topic pull.
    assert "Compassion fatigue is what happens" not in all_bodies, (
        "OPD-118 regression: compassion_fatigue topic content leaked into "
        "anxiety pool via cross-topic match"
    )
    assert "middle management role chews through your reserves" not in all_bodies


# ---------------------------------------------------------------------------
# Test 3: empty target persona pool → empty dict + WARNING (no spill).
# ---------------------------------------------------------------------------


def test_empty_target_persona_returns_empty_with_warning(
    atoms_fixture: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """
    When the target persona has NO atoms for the topic, the selector must
    return {} (NOT cross-persona spillover) and emit a planner WARNING.

    `nonexistent_persona × anxiety` is the empty-pool case.
    """
    caplog.set_level(logging.WARNING, logger=es.logger.name)
    merged = es._merged_persona_atoms_deep_6h(
        "nonexistent_persona", "anxiety", atoms_fixture, locale=None
    )
    assert merged == {}, (
        "Empty target persona pool must return empty dict — pre-OPD-118 the "
        "selector spilled into sibling personas. Got: %r" % merged
    )
    # WARNING must have been logged.
    warning_messages = [
        rec.message for rec in caplog.records
        if rec.levelno >= logging.WARNING and "OPD-118" in rec.message
    ]
    assert warning_messages, (
        "Expected OPD-118 WARNING when target persona pool is empty; "
        "no warning logged"
    )


# ---------------------------------------------------------------------------
# Test 4: teacher-bank atoms still load (positive control).
# ---------------------------------------------------------------------------


def test_teacher_bank_atoms_still_load(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Positive control: confirm the OPD-118 fix only blocks persona-pool
    cross-contamination — it does NOT touch the teacher-bank load path.
    `_load_teacher_atoms(ahjan)` must still return the teacher's atoms.
    """
    # Build a synthetic teacher bank.
    tb_root = tmp_path / "SOURCE_OF_TRUTH" / "teacher_banks" / "ahjan_test"
    approved_dir = tb_root / "approved_atoms" / "HOOK"
    approved_dir.mkdir(parents=True)

    atom_yaml = approved_dir / "ahjan_hook_001.yaml"
    atom_yaml.write_text(
        "atom_id: ahjan_HOOK_001\n"
        "content: |\n"
        "  Teacher-bank atom content for the ahjan voice. This text would not\n"
        "  exist in any persona pool — it lives in the teacher bank.\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(rr, "TEACHER_BANKS_ROOT", tmp_path / "SOURCE_OF_TRUTH" / "teacher_banks")

    loaded = rr._load_teacher_atoms("ahjan_test")
    assert "HOOK" in loaded, (
        "Teacher bank HOOK pool not loaded — OPD-118 fix should not have "
        "touched the teacher load path"
    )
    assert len(loaded["HOOK"]) == 1
    assert "Teacher-bank atom content for the ahjan voice" in loaded["HOOK"][0]["content"]


# ---------------------------------------------------------------------------
# Test 5: practice library atoms still load (positive control, EXERCISE).
# ---------------------------------------------------------------------------


def test_practice_library_path_unaffected_by_isolation_fix() -> None:
    """
    Positive control: import path for practice_library_loader is unchanged
    by OPD-118 (the fix is scoped to `_merged_persona_atoms_deep_6h`).

    This test does not exercise the full pipeline — it confirms the
    function we leave alone is still importable and has not been moved.
    """
    from phoenix_v4.exercises.practice_library_loader import (
        get_exercise_for_chapter,
        load_practice_library,
    )
    assert callable(get_exercise_for_chapter)
    assert callable(load_practice_library)


# ---------------------------------------------------------------------------
# Test 6: positive control — target persona atoms ARE returned.
# ---------------------------------------------------------------------------


def test_target_persona_atoms_returned_intact(atoms_fixture: Path) -> None:
    """
    Positive control: the fix must STILL return the target persona's atoms
    (the bug is silent spillover, not a total kill-switch). Confirm the
    `gen_z_professionals/anxiety` HOOK/SCENE/STORY atoms come back.
    """
    merged = es._merged_persona_atoms_deep_6h(
        "gen_z_professionals", "anxiety", atoms_fixture, locale=None
    )
    assert set(merged.keys()) >= {"HOOK", "SCENE", "STORY"}, (
        f"Target persona slots missing from merged pool: {merged.keys()}"
    )
    for slot in ("HOOK", "SCENE", "STORY"):
        assert len(merged[slot]) >= 3, (
            f"{slot} pool too small: {len(merged[slot])} atoms (want >= 3 "
            "for SPEC-739-THRESHOLD-01)"
        )

    # And confirm one of the known gen_z body markers IS present.
    joined = "\n".join(
        str(atom.get("content") or "")
        for slot_atoms in merged.values()
        for atom in slot_atoms
    )
    assert "gen_z_professionals voice" in joined or "gen_z professional vibe" in joined
