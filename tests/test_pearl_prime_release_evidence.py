from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parent.parent / "scripts" / "ci" / "write_pearl_prime_release_evidence.py"
SPEC = importlib.util.spec_from_file_location("write_pearl_prime_release_evidence", MODULE_PATH)
evidence = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(evidence)


def test_release_bundle_requires_release_evidence(tmp_path, monkeypatch):
    repo = tmp_path
    (repo / "config" / "governance").mkdir(parents=True)
    (repo / "config" / "governance" / "required_checks.yaml").write_text(
        "required_checks:\n"
        "  - Core tests\n"
        "non_blocking_checks:\n"
        "  - \"Workers Builds: pearl-prime\"\n",
        encoding="utf-8",
    )
    (repo / "artifacts" / "release").mkdir(parents=True)
    (repo / "artifacts" / "canary_plans").mkdir(parents=True)
    (repo / "artifacts" / "systems_test").mkdir(parents=True)
    (repo / "artifacts" / "release" / "rollback_smoke_evidence.json").write_text("{}", encoding="utf-8")
    (repo / "artifacts" / "release" / "latest_systems_test_report.json").write_text("{}", encoding="utf-8")
    (repo / "artifacts" / "canary_plans" / "canary_summary.json").write_text("{}", encoding="utf-8")

    monkeypatch.setattr(evidence, "REPO_ROOT", repo)

    bundle = evidence.build_bundle("release")
    assert bundle["ready"] is True
    assert bundle["missing_required_evidence"] == []
    assert "Core tests" in bundle["required_checks"]
    assert "Workers Builds: pearl-prime" in bundle["non_blocking_checks"]
    paths = {row["id"]: row["path"] for row in bundle["evidence"]}
    assert paths["latest_systems_test_report"] == "artifacts/release/latest_systems_test_report.json"


def test_release_bundle_reports_missing_required_evidence(tmp_path, monkeypatch):
    repo = tmp_path
    (repo / "config" / "governance").mkdir(parents=True)
    (repo / "config" / "governance" / "required_checks.yaml").write_text(
        "required_checks:\n"
        "  - Release gates\n",
        encoding="utf-8",
    )
    (repo / "artifacts" / "release").mkdir(parents=True)

    monkeypatch.setattr(evidence, "REPO_ROOT", repo)

    bundle = evidence.build_bundle("release")
    assert bundle["ready"] is False
    missing = set(bundle["missing_required_evidence"])
    assert "artifacts/release/rollback_smoke_evidence.json" in missing
    assert "artifacts/canary_plans/canary_summary.json" in missing


def test_main_writes_json_bundle(tmp_path, monkeypatch):
    repo = tmp_path
    (repo / "config" / "governance").mkdir(parents=True)
    (repo / "config" / "governance" / "required_checks.yaml").write_text("required_checks: []\n", encoding="utf-8")
    (repo / "artifacts" / "release").mkdir(parents=True)

    monkeypatch.setattr(evidence, "REPO_ROOT", repo)

    out = repo / "artifacts" / "release" / "bundle.json"
    argv = sys.argv
    try:
        sys.argv = [
            "write_pearl_prime_release_evidence.py",
            "--profile",
            "pr",
            "--out",
            str(out.relative_to(repo)),
        ]
        assert evidence.main() == 0
    finally:
        sys.argv = argv

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["pipeline"] == "pearl-prime"
    assert data["profile"] == "pr"
