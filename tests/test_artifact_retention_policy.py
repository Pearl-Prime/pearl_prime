from __future__ import annotations

from pathlib import Path

from scripts.ci.check_artifact_retention import (
    build_retention_manifest,
    classify_path,
    validate_retention_manifest,
)


def test_retention_policy_classifies_without_delete(tmp_path):
    policy = {
        "rules": [
            {
                "artifact_class": "REGENERABLE_RENDER",
                "owner": "Pearl_DevOps",
                "patterns": ["artifacts/manga/**"],
                "keep_duration": "until_manifest_verified",
                "durable_archive_required": True,
                "r2_pointer_required": True,
                "local_prune_eligible": True,
                "operator_approval_required_for_deletion": True,
                "restore_procedure": "pull-on-demand",
            }
        ]
    }

    rule = classify_path("artifacts/manga/example.png", policy)

    assert rule["artifact_class"] == "REGENERABLE_RENDER"
    assert rule["operator_approval_required_for_deletion"] is True


def test_retention_manifest_is_dry_run_only(tmp_path):
    root = tmp_path
    artifact = root / "artifacts" / "manga" / "one.bin"
    artifact.parent.mkdir(parents=True)
    artifact.write_bytes(b"x" * 11)
    policy = root / "policy.yaml"
    policy.write_text(
        """
rules:
  - artifact_class: REGENERABLE_RENDER
    owner: Pearl_DevOps
    patterns: ["artifacts/manga/**"]
    keep_duration: until_manifest_verified
    durable_archive_required: true
    r2_pointer_required: true
    local_prune_eligible: true
    operator_approval_required_for_deletion: true
    restore_procedure: pull-on-demand
""",
        encoding="utf-8",
    )

    manifest = build_retention_manifest(repo_root=root, policy_path=policy, roots=["artifacts"], max_families=5)

    assert manifest["files_deleted"] == 0
    assert manifest["real_offloads"] == 0
    assert not validate_retention_manifest(manifest)
