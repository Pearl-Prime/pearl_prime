from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "scripts" / "manga"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from manga_100pct_cloud_dispatch import dispatch

SHA = "a" * 40


def _config(path: Path):
    data = {
        "program_id": "test",
        "repository": "owner/repo",
        "branch": "agent/test",
        "mission": "Test mission",
        "foundation": {"pr_number": 5597, "expected_head_sha": SHA},
        "absolute_rules": ["Do not invent evidence."],
        "agents": {
            "Pearl_ArtPipeline": {
                "maps_to_lanes": ["A"],
                "goal": "proof",
                "tasks": ["run proof"],
                "output_tags": ["proof"],
            }
        },
        "final_auditor": {"name": "Pearl_Auditor", "config": "audit.yaml", "tasks": ["audit"]},
    }
    path.write_text(yaml.safe_dump(data), encoding="utf-8")


def _receipt(path: Path, *, merged: bool):
    path.write_text(
        json.dumps(
            {
                "repository": "owner/repo",
                "pr_number": 5597,
                "head_sha": SHA,
                "merge_sha": "b" * 40 if merged else None,
                "merged": merged,
                "required_checks_pass": True,
                "dispatch_allowed": merged,
            }
        ),
        encoding="utf-8",
    )


def test_dispatch_is_blocked_until_foundation_is_merged(tmp_path: Path):
    config = tmp_path / "config.yaml"
    receipt = tmp_path / "receipt.json"
    output = tmp_path / "packet"
    _config(config)
    _receipt(receipt, merged=False)
    manifest = dispatch(config, receipt, output)
    assert manifest["dispatch_allowed"] is False
    assert (output / "BLOCKED.md").is_file()
    assert not (output / "00_Pearl_PM.md").exists()


def test_dispatch_renders_prompts_after_green_receipt(tmp_path: Path):
    config = tmp_path / "config.yaml"
    receipt = tmp_path / "receipt.json"
    output = tmp_path / "packet"
    _config(config)
    _receipt(receipt, merged=True)
    manifest = dispatch(config, receipt, output)
    assert manifest["dispatch_allowed"] is True
    assert manifest["prompts"] == ["00_Pearl_PM.md", "01_Pearl_ArtPipeline.md", "02_Pearl_Auditor.md"]
    assert "Foundation merge SHA" in (output / "00_Pearl_PM.md").read_text(encoding="utf-8")
