from __future__ import annotations

import json
from pathlib import Path

from scripts.ci import run_canary_100_books


def test_canary_uses_no_update_freebie_index(monkeypatch, tmp_path: Path) -> None:
    recorded_cmds: list[list[str]] = []
    monkeypatch.setattr("sys.argv", ["run_canary_100_books.py"])
    monkeypatch.setattr(run_canary_100_books, "REPO_ROOT", tmp_path)

    monkeypatch.setattr(
        run_canary_100_books,
        "_sample_arcs",
        lambda n, seed=42, allowed_formats=None: [
            (tmp_path / "demo__topic__engine__F006.yaml", "first_responders", "grief", "F006"),
        ],
    )

    class Result:
        returncode = 0
        stderr = ""

    def fake_run(cmd, **kwargs):
        recorded_cmds.append(cmd)
        out_index = cmd.index("--out") + 1
        Path(cmd[out_index]).write_text("{}", encoding="utf-8")
        return Result()

    monkeypatch.setattr(run_canary_100_books.subprocess, "run", fake_run)

    exit_code = run_canary_100_books.main()

    assert exit_code == 0
    assert recorded_cmds
    assert "--no-job-check" in recorded_cmds[0]
    assert "--no-generate-freebies" in recorded_cmds[0]
    assert "--no-update-freebie-index" in recorded_cmds[0]


def test_canary_uses_analyzer_driven_selection(monkeypatch, tmp_path: Path) -> None:
    recorded_cmds: list[list[str]] = []
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_canary_100_books.py",
            "--analysis",
            str(tmp_path / "analysis.json"),
            "--combo-mode",
            "best-worst",
            "--combo-limit",
            "1",
        ],
    )
    monkeypatch.setattr(run_canary_100_books, "REPO_ROOT", tmp_path)

    (tmp_path / "analysis.json").write_text(
        json.dumps(
            {
                "best_combos": [{"format_id": "BESTFMT"}],
                "worst_combos": [{"format_id": "WORSTFMT"}],
            }
        ),
        encoding="utf-8",
    )

    def sample_arcs(n, seed=42, allowed_formats=None):
        assert allowed_formats == ["BESTFMT", "WORSTFMT"]
        return [
            (tmp_path / "demo__topic__engine__BESTFMT.yaml", "first_responders", "grief", "BESTFMT"),
        ]

    monkeypatch.setattr(run_canary_100_books, "_sample_arcs", sample_arcs)

    class Result:
        returncode = 0
        stderr = ""

    def fake_run(cmd, **kwargs):
        recorded_cmds.append(cmd)
        out_index = cmd.index("--out") + 1
        Path(cmd[out_index]).write_text("{}", encoding="utf-8")
        return Result()

    monkeypatch.setattr(run_canary_100_books.subprocess, "run", fake_run)

    exit_code = run_canary_100_books.main()

    assert exit_code == 0
    assert recorded_cmds
    assert recorded_cmds[0][recorded_cmds[0].index("--arc") + 1].endswith("BESTFMT.yaml")


def test_canary_falls_back_when_analysis_formats_match_no_arcs(monkeypatch, tmp_path: Path, capsys) -> None:
    recorded_allowed_formats: list[list[str] | None] = []
    recorded_cmds: list[list[str]] = []
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_canary_100_books.py",
            "--analysis",
            str(tmp_path / "analysis.json"),
            "--combo-mode",
            "best-worst",
            "--combo-limit",
            "1",
        ],
    )
    monkeypatch.setattr(run_canary_100_books, "REPO_ROOT", tmp_path)

    (tmp_path / "analysis.json").write_text(
        json.dumps(
            {
                "best_combos": [{"format_id": "standard_book"}],
                "worst_combos": [{"format_id": "extended_book_2h"}],
            }
        ),
        encoding="utf-8",
    )

    def sample_arcs(n, seed=42, allowed_formats=None):
        recorded_allowed_formats.append(allowed_formats)
        if allowed_formats:
            return []
        return [
            (tmp_path / "demo__topic__engine__F006.yaml", "first_responders", "grief", "F006"),
        ]

    monkeypatch.setattr(run_canary_100_books, "_sample_arcs", sample_arcs)

    class Result:
        returncode = 0
        stderr = ""

    def fake_run(cmd, **kwargs):
        recorded_cmds.append(cmd)
        out_index = cmd.index("--out") + 1
        Path(cmd[out_index]).write_text("{}", encoding="utf-8")
        return Result()

    monkeypatch.setattr(run_canary_100_books.subprocess, "run", fake_run)

    exit_code = run_canary_100_books.main()

    assert exit_code == 0
    assert recorded_allowed_formats == [["standard_book", "extended_book_2h"], None]
    assert recorded_cmds
    assert "falling back to unfiltered arc sample" in capsys.readouterr().err
