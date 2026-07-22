from pathlib import Path

from scripts.ci import check_rap_compliance as rap


def test_local_binary_write_without_r2_or_pscli_warns(tmp_path: Path, monkeypatch) -> None:
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "bad_render.py").write_text(
        "from pathlib import Path\n"
        "Path('artifacts/qa/frame.png').write_bytes(b'png')\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(rap, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(rap, "_ARTIFACT_WRITE_SCAN_ROOTS", (scripts,))

    assert rap._scan_local_artifact_writes() == [
        "scripts/bad_render.py may write artifact binaries locally without r2_sync.py or pscli"
    ]


def test_local_binary_write_with_canonical_persistence_is_allowed(
    tmp_path: Path, monkeypatch
) -> None:
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "good_render.py").write_text(
        "from pathlib import Path\n"
        "Path('artifacts/qa/frame.png').write_bytes(b'png')\n"
        "# persisted by scripts/artifacts/r2_sync.py\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(rap, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(rap, "_ARTIFACT_WRITE_SCAN_ROOTS", (scripts,))

    assert rap._scan_local_artifact_writes() == []
