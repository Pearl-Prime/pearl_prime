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
    assert recorded_cmds[0][recorded_cmds[0].index("--quality-profile") + 1] == "draft"
    assert "--no-job-check" in recorded_cmds[0]
    assert "--no-generate-freebies" in recorded_cmds[0]
    assert "--no-update-freebie-index" in recorded_cmds[0]


def test_sample_arcs_filters_to_canary_ready_surfaces(monkeypatch, tmp_path: Path) -> None:
    arcs_dir = tmp_path / "config" / "source_of_truth" / "master_arcs"
    arcs_dir.mkdir(parents=True)
    monkeypatch.setattr(run_canary_100_books, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(run_canary_100_books, "ARCS_DIR", arcs_dir)

    (tmp_path / "config").mkdir(exist_ok=True)
    (tmp_path / "config" / "topic_engine_bindings.yaml").write_text(
        "grief:\n  allowed_engines: [watcher]\n",
        encoding="utf-8",
    )

    good_arc = arcs_dir / "first_responders__grief__watcher__F006.yaml"
    missing_slot_arc = arcs_dir / "educators__grief__watcher__F006.yaml"
    invalid_engine_arc = arcs_dir / "first_responders__grief__spiral__F006.yaml"
    for arc in (good_arc, missing_slot_arc, invalid_engine_arc):
        arc.write_text("{}", encoding="utf-8")

    ready_base = tmp_path / "atoms" / "first_responders" / "grief"
    for slot in run_canary_100_books.CANARY_REQUIRED_ATOM_SLOTS:
        slot_dir = ready_base / slot
        slot_dir.mkdir(parents=True, exist_ok=True)
        (slot_dir / "CANONICAL.txt").write_text("ready\n", encoding="utf-8")
    engine_dir = ready_base / "watcher"
    engine_dir.mkdir(parents=True)
    (engine_dir / "CANONICAL.txt").write_text("story\n", encoding="utf-8")

    missing_base = tmp_path / "atoms" / "educators" / "grief"
    for slot in set(run_canary_100_books.CANARY_REQUIRED_ATOM_SLOTS) - {"SCENE"}:
        slot_dir = missing_base / slot
        slot_dir.mkdir(parents=True, exist_ok=True)
        (slot_dir / "CANONICAL.txt").write_text("partial\n", encoding="utf-8")
    missing_engine_dir = missing_base / "watcher"
    missing_engine_dir.mkdir(parents=True)
    (missing_engine_dir / "CANONICAL.txt").write_text("story\n", encoding="utf-8")

    samples = run_canary_100_books._sample_arcs(10)

    assert [(p.name, persona, topic, format_id) for p, persona, topic, format_id in samples] == [
        ("first_responders__grief__watcher__F006.yaml", "first_responders", "grief", "F006")
    ]


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
