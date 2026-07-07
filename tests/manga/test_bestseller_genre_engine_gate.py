"""Bestseller gate genre-engine enforcement — blocks shell-correct generic spines."""
from __future__ import annotations

from phoenix_v4.manga.qc.bestseller_gate import evaluate_bestseller_gate
from phoenix_v4.manga.qc.genre_engine_gate import evaluate_genre_engine


def _panels(texts: list[str]) -> dict:
    return {
        "artifact_type": "chapter_script_writer_handoff",
        "series_id": "test__author__en_US__anxiety__slug",
        "genre": "psychological_horror",
        "pages": [{
            "panels": [
                {"panel_id": f"p{i}", "scene": t, "caption": t}
                for i, t in enumerate(texts)
            ],
        }],
    }


def _workplace_panels(texts: list[str]) -> dict:
    doc = _panels(texts)
    doc["genre"] = "workplace_drama"
    doc["series_id"] = "test__author__en_US__burnout__slug"
    return doc


def test_horror_generic_dawn_spine_blocked():
    generic = _panels([
        "Wide establishing shot of a quiet mountain village.",
        "Dawn light, stillness before the day. The world breathes.",
        "She exhale. The room holds the echo.",
        "Something has shifted in the familiar space.",
        "Neither acknowledges the gap between them.",
        "Final panel: Not resolved. Not healed. Awake.",
    ])
    findings = evaluate_genre_engine(generic, genre_id="psychological_horror")
    codes = {f["issue_code"] for f in findings}
    assert "GENRE_ENGINE_GENERIC_SPINE" in codes
    assert any(f["severity"] == "BLOCKER" for f in findings)


def test_horror_native_spine_passes_engine_gate():
    native = _panels([
        "Mira stands very still in the dark cabin; dread sits in her shoulders.",
        "A wrong angle in the mirror — presence sensed before it is named.",
        "She flinches at a sound that should be ordinary but isn't normal.",
        "Shadow pools at the door; she reads the dark without naming it.",
        "The room stays wrong; vigilance replaces false clarity.",
        "She closes the book on the fear — integration by staying.",
    ])
    engine_findings = evaluate_genre_engine(native, genre_id="psychological_horror")
    assert not any(f["severity"] == "BLOCKER" for f in engine_findings)


def test_workplace_without_institutional_pressure_blocked():
    generic = _workplace_panels([
        "Dawn light, stillness before the day over a quiet mountain village.",
        "Tea ritual at the garden. The world breathes.",
        "A small choice — turns left instead of right.",
        "Unexpected kindness from a stranger.",
        "The room holds the echo of healing renewal.",
        "Not resolved. Not healed. Awake.",
    ])
    findings = evaluate_genre_engine(generic, genre_id="workplace_drama")
    assert any(f["issue_code"] == "GENRE_ENGINE_GENERIC_SPINE" for f in findings)


def test_workplace_native_spine_passes_engine_gate():
    native = _workplace_panels([
        "Open-plan office: badge click at the security desk before dawn shift.",
        "Calendar blocks every hour — no white space on the dashboard.",
        "Conference room: role eating the person; email ping during the meeting.",
        "Night shift custodian names the cycle on the floor.",
        "Desk piled with deadline packets; competence friction with the manager.",
        "Sustainable pace named — institutional pressure made legible.",
    ])
    findings = evaluate_genre_engine(native, genre_id="workplace_drama")
    assert not any(f["severity"] == "BLOCKER" for f in findings)


def test_bestseller_gate_promotes_engine_blockers():
    generic = _workplace_panels([
        "Dawn light, stillness before the day.",
        "The world breathes in stillness.",
        "Something has shifted.",
        "Neither acknowledges the gap.",
        "The room holds the echo.",
        "Not resolved. Not healed. Awake.",
    ])
    verdict = evaluate_bestseller_gate(generic, profile=None)
    engine_blockers = [
        b for b in verdict["blockers"]
        if b.get("gate_id") == "MANGA.BESTSELLER.GENRE_ENGINE"
    ]
    assert verdict["clearance"] == "hard_fail"
    assert engine_blockers
