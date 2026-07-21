from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "scripts" / "manga"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from manga_100pct_truth_audit import audit

SHA = "a" * 40


def _write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def _config(path: Path):
    data = {
        "foundation_receipt": "qa/foundation.json",
        "merge_registry": "qa/merges.json",
        "required_agents": ["Pearl_A"],
        "forbidden_json_values": ["/Users/"],
        "claim_files": ["analysis/verdict.md"],
        "requirements": {
            "proof": {
                "path": "qa/proof/manifest.json",
                "json_assertions": {"status": "green", "real": True},
                "required_globs": ["*.png"],
            }
        },
    }
    path.write_text(yaml.safe_dump(data), encoding="utf-8")


def test_audit_fails_closed_when_evidence_is_missing(tmp_path: Path):
    config = tmp_path / "config.yaml"
    _config(config)
    report = audit(tmp_path, config)
    assert report["manga-100pct-final"] == "NOT_GREEN"
    assert any("foundation receipt missing" in failure for failure in report["failures"])


def test_audit_turns_green_only_with_receipts_merges_and_real_proof(tmp_path: Path):
    config = tmp_path / "config.yaml"
    _config(config)
    _write_json(
        tmp_path / "qa/foundation.json",
        {
            "pr_number": 5597,
            "merged": True,
            "required_checks_pass": True,
            "dispatch_allowed": True,
            "merge_sha": SHA,
        },
    )
    _write_json(
        tmp_path / "qa/merges.json",
        {
            "foundation": {"pr_number": 5597, "merged": True, "merge_sha": SHA},
            "agents": {"Pearl_A": {"pr_number": 6000, "merged": True, "merge_sha": "b" * 40}},
        },
    )
    _write_json(tmp_path / "qa/proof/manifest.json", {"status": "green", "real": True})
    (tmp_path / "qa/proof/panel.png").write_bytes(b"not-a-real-png-but-a-real-file-for-contract-test")
    report = audit(tmp_path, config)
    assert report["manga-100pct-final"] == "GREEN"
    assert report["failures"] == []


def test_audit_rejects_local_user_paths_and_corrects_green_claim(tmp_path: Path):
    config = tmp_path / "config.yaml"
    _config(config)
    _write_json(
        tmp_path / "qa/foundation.json",
        {
            "pr_number": 5597,
            "merged": True,
            "required_checks_pass": True,
            "dispatch_allowed": True,
            "merge_sha": SHA,
        },
    )
    _write_json(
        tmp_path / "qa/merges.json",
        {
            "foundation": {"pr_number": 5597, "merged": True, "merge_sha": SHA},
            "agents": {"Pearl_A": {"pr_number": 6000, "merged": True, "merge_sha": "b" * 40}},
        },
    )
    _write_json(tmp_path / "qa/proof/manifest.json", {"status": "green", "real": True, "root": "/Users/me/proof"})
    (tmp_path / "qa/proof/panel.png").write_bytes(b"x")
    verdict = tmp_path / "analysis/verdict.md"
    verdict.parent.mkdir(parents=True)
    verdict.write_text("manga-100pct-final=GREEN\n", encoding="utf-8")
    report = audit(tmp_path, config)
    assert report["manga-100pct-final"] == "NOT_GREEN"
    assert report["false_claims_corrected"]
