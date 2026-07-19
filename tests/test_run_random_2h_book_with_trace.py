"""Unit tests for scripts/qa/run_random_2h_book_with_trace.py (no full render)."""

from __future__ import annotations

from pathlib import Path
from unittest import mock

import pytest

from scripts.qa.run_random_2h_book_with_trace import (
    RUNTIME_FORMAT,
    CellCandidate,
    build_pipeline_command,
    default_render_dir,
    ensure_atom_trace,
    list_candidates,
    main,
    pick_candidate,
    _parse_arc_path,
)


def _touch_canonical(repo: Path, persona: str, topic: str) -> None:
    bank = repo / "atoms" / persona / topic / "HOOK"
    bank.mkdir(parents=True)
    (bank / "CANONICAL.txt").write_text("## HOOK v01\n---\n---\nhi\n---\n", encoding="utf-8")


def _write_arc(repo: Path, persona: str, topic: str, engine: str, structural: str) -> Path:
    arcs = repo / "config" / "source_of_truth" / "master_arcs"
    arcs.mkdir(parents=True, exist_ok=True)
    path = arcs / f"{persona}__{topic}__{engine}__{structural}.yaml"
    path.write_text("persona_id: stub\n", encoding="utf-8")
    return path


def test_parse_arc_path() -> None:
    p = Path("corporate_managers__burnout__overwhelm__F006.yaml")
    assert _parse_arc_path(p) == ("corporate_managers", "burnout", "overwhelm", "F006")
    assert _parse_arc_path(Path("bad.yaml")) is None


def test_list_candidates_requires_atom_bank(tmp_path: Path) -> None:
    _write_arc(tmp_path, "p1", "t1", "overwhelm", "F006")
    _write_arc(tmp_path, "p2", "t2", "shame", "F006")
    _touch_canonical(tmp_path, "p2", "t2")
    cands = list_candidates(repo_root=tmp_path)
    assert len(cands) == 1
    assert cands[0].persona == "p2"
    assert cands[0].topic == "t2"


def test_list_candidates_one_per_persona_topic(tmp_path: Path) -> None:
    _write_arc(tmp_path, "p1", "t1", "comparison", "F006")
    _write_arc(tmp_path, "p1", "t1", "overwhelm", "F006")
    _touch_canonical(tmp_path, "p1", "t1")
    cands = list_candidates(repo_root=tmp_path)
    assert len(cands) == 1
    # sorted glob → comparison before overwhelm
    assert cands[0].engine == "comparison"


def test_pick_candidate_seeded(tmp_path: Path) -> None:
    for i in range(5):
        _write_arc(tmp_path, f"p{i}", f"t{i}", "overwhelm", "F006")
        _touch_canonical(tmp_path, f"p{i}", f"t{i}")
    cands = list_candidates(repo_root=tmp_path)
    a = pick_candidate(cands, seed=7)
    b = pick_candidate(cands, seed=7)
    c = pick_candidate(cands, seed=8)
    assert a == b
    assert a.key != c.key or len(cands) == 1


def test_build_pipeline_command_is_2h_chord(tmp_path: Path) -> None:
    arc = _write_arc(tmp_path, "gen_z_professionals", "anxiety", "spiral", "F006")
    cell = CellCandidate(
        persona="gen_z_professionals",
        topic="anxiety",
        engine="spiral",
        structural_format="F006",
        arc_path=arc,
    )
    render_dir = tmp_path / "out"
    cmd = build_pipeline_command(cell=cell, render_dir=render_dir, seed="99", repo_root=tmp_path)
    assert "--runtime-format" in cmd
    assert RUNTIME_FORMAT in cmd
    assert cmd[cmd.index("--runtime-format") + 1] == "extended_book_2h"
    assert "--pipeline-mode" in cmd and "spine" in cmd
    assert "--quality-profile" in cmd and "production" in cmd
    assert "--exercise-journeys" in cmd
    assert "--render-book" in cmd
    assert "--persona" in cmd and "gen_z_professionals" in cmd
    assert "--topic" in cmd and "anxiety" in cmd


def test_default_render_dir_name() -> None:
    cell = CellCandidate("corp", "burnout", "overwhelm", "F006", Path("/x.yaml"))
    d = default_render_dir(cell, seed=42, out_root=Path("/tmp/out"), day="20260719")
    assert d.name == "random_2h_20260719_corp__burnout__42"


def test_ensure_atom_trace_requires_artifacts(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        ensure_atom_trace(tmp_path)


def test_ensure_atom_trace_calls_writer(tmp_path: Path) -> None:
    (tmp_path / "section_packet_audit.json").write_text('{"slots":[]}', encoding="utf-8")
    (tmp_path / "book.txt").write_text("hi", encoding="utf-8")
    with mock.patch(
        "scripts.qa.render_atom_trace.write_atom_trace",
        return_value=tmp_path / "human_atom_trace.txt",
    ) as w:
        out = ensure_atom_trace(tmp_path, repo_root=tmp_path)
    assert out == tmp_path / "human_atom_trace.txt"
    w.assert_called_once()


def test_main_list_candidates(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _write_arc(tmp_path, "p1", "t1", "overwhelm", "F006")
    _touch_canonical(tmp_path, "p1", "t1")
    rc = main(["--list-candidates", "--repo-root", str(tmp_path)])
    assert rc == 0
    captured = capsys.readouterr().out
    assert "candidates=1" in captured
    assert "p1 × t1" in captured


def test_main_dry_run(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _write_arc(tmp_path, "p1", "t1", "overwhelm", "F006")
    _touch_canonical(tmp_path, "p1", "t1")
    out_root = tmp_path / "renders"
    rc = main(
        [
            "--dry-run",
            "--seed",
            "1",
            "--repo-root",
            str(tmp_path),
            "--out-root",
            str(out_root),
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out
    assert "DRY_RUN" in out
    assert "extended_book_2h" in out
    assert "p1" in out
