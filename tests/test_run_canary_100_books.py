from __future__ import annotations

from pathlib import Path

from scripts.ci import run_canary_100_books


def test_canary_uses_no_update_freebie_index(monkeypatch, tmp_path: Path) -> None:
    recorded_cmds: list[list[str]] = []
    monkeypatch.setattr("sys.argv", ["run_canary_100_books.py"])
    monkeypatch.setattr(run_canary_100_books, "REPO_ROOT", tmp_path)

    monkeypatch.setattr(
        run_canary_100_books,
        "_sample_arcs",
        lambda n, seed=42: [
            (tmp_path / "demo__topic__engine__F006.yaml", "first_responders", "grief"),
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
    assert "--no-generate-freebies" in recorded_cmds[0]
    assert "--no-update-freebie-index" in recorded_cmds[0]
