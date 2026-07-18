from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parent.parent / "scripts" / "ci" / "write_workflow_run_manifest.py"
SPEC = importlib.util.spec_from_file_location("write_workflow_run_manifest", MODULE_PATH)
manifest = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(manifest)


def test_main_writes_manifest_with_run_metadata(tmp_path, monkeypatch):
    repo = tmp_path
    (repo / "artifacts").mkdir(parents=True)
    artifact = repo / "artifacts" / "demo.json"
    artifact.write_text("{}", encoding="utf-8")

    monkeypatch.setenv("GITHUB_REPOSITORY", "Ahjan108/phoenix_omega_v4.8")
    monkeypatch.setenv("GITHUB_RUN_ID", "12345")
    monkeypatch.setenv("GITHUB_RUN_ATTEMPT", "2")
    monkeypatch.setenv("GITHUB_RUN_NUMBER", "7")
    monkeypatch.setenv("GITHUB_REF", "refs/heads/main")
    monkeypatch.setenv("GITHUB_SHA", "deadbeef")
    monkeypatch.setenv("GITHUB_EVENT_NAME", "push")
    monkeypatch.setenv("GITHUB_SERVER_URL", "https://github.com")
    monkeypatch.setattr(manifest, "REPO_ROOT", repo)

    out = repo / "artifacts" / "release" / "workflow_run_manifest.json"
    argv = sys.argv
    try:
        sys.argv = [
            "write_workflow_run_manifest.py",
            "--workflow-name",
            "Release gates",
            "--workflow-file",
            ".github/workflows/release-gates.yml",
            "--out",
            str(out.relative_to(repo)),
            "--artifact",
            str(artifact.relative_to(repo)),
        ]
        assert manifest.main() == 0
    finally:
        sys.argv = argv

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["workflow_name"] == "Release gates"
    assert data["workflow_file"] == ".github/workflows/release-gates.yml"
    assert data["run_url"] == "https://github.com/Ahjan108/phoenix_omega_v4.8/actions/runs/12345"
    assert data["artifacts"][0]["path"] == "artifacts/demo.json"
    assert data["artifacts"][0]["exists"] is True
