"""Tests for scripts/qa/render_atom_trace.py — general post-render human atom trace."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.qa.render_atom_trace import build_atom_trace, write_atom_trace

REPO = Path(__file__).resolve().parents[1]


def _write_fixture(tmp_path: Path) -> Path:
    """Minimal render dir: SPA + book + plan, plus a tiny persona CANONICAL bank."""
    render = tmp_path / "render"
    render.mkdir()
    atoms = tmp_path / "atoms" / "fixture_persona" / "fixture_topic" / "HOOK"
    atoms.mkdir(parents=True)
    (atoms / "CANONICAL.txt").write_text(
        "## HOOK v01\n---\n---\nAlpha hook sentence one. Alpha hook sentence two.\n---\n\n"
        "## HOOK v02\n---\n---\nBeta hook opens here. More beta text follows after.\n---\n",
        encoding="utf-8",
    )
    doctrine = tmp_path / "SOURCE_OF_TRUTH" / "composite_doctrine" / "fixture_topic"
    doctrine.mkdir(parents=True)
    (doctrine / "CANONICAL.txt").write_text(
        "## COMPOSITE_DOCTRINE v01\n---\n---\nDoctrine body begins. Second doctrine sentence.\n---\n",
        encoding="utf-8",
    )
    book = (
        "Chapter 1\n\n"
        "Alpha hook sentence one. Alpha hook sentence two.\n\n"
        "Doctrine body begins. Second doctrine sentence.\n\n"
        "Beta hook opens here. More beta text follows after.\n"
    )
    (render / "book.txt").write_text(book, encoding="utf-8")
    slots = [
        {
            "chapter": 1,
            "slot_index": 0,
            "slot_type": "HOOK",
            "source": "persona_atom",
            "source_id": "HOOK v01",
            "variant_id": "",
            "words": 7,
        },
        {
            "chapter": 1,
            "slot_index": 1,
            "slot_type": "TEACHER_DOCTRINE",
            "source": "composite_doctrine",
            "source_id": "COMPOSITE_DOCTRINE v01",
            "variant_id": "",
            "words": 6,
        },
        {
            "chapter": 1,
            "slot_index": 2,
            "slot_type": "HOOK",
            "source": "persona_atom",
            "source_id": "HOOK v02",
            "variant_id": "",
            "words": 8,
        },
        {
            "chapter": 1,
            "slot_index": 3,
            "slot_type": "PIVOT",
            "source": "persona_atom",
            "source_id": "PIVOT v99",
            "variant_id": "",
            "words": 3,
        },
    ]
    (render / "section_packet_audit.json").write_text(
        json.dumps({"slots": slots, "slot_count": len(slots)}, indent=2),
        encoding="utf-8",
    )
    (render / "plan.json").write_text(
        json.dumps(
            {
                "persona_id": "fixture_persona",
                "topic_id": "fixture_topic",
                "locale": "en-US",
            }
        ),
        encoding="utf-8",
    )
    return render


def test_render_atom_trace_format_and_mapping(tmp_path: Path) -> None:
    render = _write_fixture(tmp_path)
    body, summary = build_atom_trace(render, repo_root=tmp_path)

    assert summary["slot_count"] == 4
    assert summary["resolved_count"] == 3
    assert summary["unresolved_count"] == 1
    assert summary["persona_id"] == "fixture_persona"
    assert summary["topic_id"] == "fixture_topic"

    # Exact field labels from the Ch1/Ch2 human atom trace format
    assert "# Human Atom Trace" in body
    assert "[HOOK]" in body
    assert "What this surface does:" in body
    assert "Source: atoms/fixture_persona/fixture_topic/HOOK/CANONICAL.txt:" in body
    assert "Atom: HOOK / HOOK v01" in body
    assert "Status: resolved; fallback: none" in body
    assert "First rendered sentence: Alpha hook sentence one." in body
    assert "Previous beat: START; next beat: TEACHER_DOCTRINE" in body
    assert "Cohesion/read note:" in body

    assert "Atom: COMPOSITE_DOCTRINE / COMPOSITE_DOCTRINE v01" in body
    assert "First rendered sentence: Doctrine body begins." in body

    # Honest unresolved — never fabricate a bank path
    assert "Source: <unresolved:PIVOT v99>" in body
    assert "Status: unresolved; fallback: unresolved" in body


def test_write_atom_trace_default_path(tmp_path: Path) -> None:
    render = _write_fixture(tmp_path)
    dest = write_atom_trace(render, repo_root=tmp_path)
    assert dest == render / "human_atom_trace.txt"
    assert dest.exists()
    assert dest.with_suffix(".summary.json").exists()


@pytest.mark.parametrize(
    "render_rel",
    [
        "artifacts/qa/proprime_accent_flagship_proof_2026-07-11",
        "artifacts/qa/pearl_prime_next_micro_wave_20260716/corporate_managers__boundaries__false_alarm__F006",
    ],
)
def test_real_render_dirs_smoke(render_rel: str) -> None:
    render = REPO / render_rel
    if not (render / "section_packet_audit.json").exists() or not (render / "book.txt").exists():
        pytest.skip(f"render dir missing locally: {render_rel}")
    body, summary = build_atom_trace(render, repo_root=REPO)
    assert summary["slot_count"] > 10
    assert "[HOOK]" in body or "What this surface does:" in body
    assert "Source:" in body
    assert "First rendered sentence:" in body
    # Zero hardcoding: persona/topic come from plan.json / dirname, not tool constants
    assert summary["persona_id"]
    assert summary["topic_id"]
