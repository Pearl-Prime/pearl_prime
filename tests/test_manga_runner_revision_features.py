"""Focused tests for manga runner revision/layout helpers."""

from __future__ import annotations

import json
from pathlib import Path

from phoenix_v4.manga.models import stage_ids as sid
from phoenix_v4.manga.models.validation import validate_instance
from phoenix_v4.manga.models.workspace_layout import resolve_chapter_workspace
from phoenix_v4.manga.runner.revision_policy import (
    clear_stage_manifests_from,
    revision_resume_stage_from_queue,
)
from phoenix_v4.manga.runner.stage_manifest_io import stage_manifest_path
from phoenix_v4.manga.sdf.stub import attach_sdf_stub_conditioning


def test_resolve_chapter_workspace_prefers_flat_layout(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    chapter_request = {
        "schema_version": "1.0.0",
        "artifact_type": "chapter_request",
        "series_id": "series_a",
        "chapter_id": "chapter_flat",
    }
    validate_instance(chapter_request, "chapter_request")
    (workspace / "chapter_request.json").write_text(
        json.dumps(chapter_request, indent=2) + "\n",
        encoding="utf-8",
    )

    resolved = resolve_chapter_workspace(workspace, chapter_id="chapter_nested")

    assert resolved == workspace.resolve()


def test_resolve_chapter_workspace_supports_nested_layout(tmp_path: Path) -> None:
    series_root = tmp_path / "series_root"
    nested = series_root / "chapters" / "chapter_001"
    nested.mkdir(parents=True)
    chapter_request = {
        "schema_version": "1.0.0",
        "artifact_type": "chapter_request",
        "series_id": "series_b",
        "chapter_id": "chapter_001",
    }
    validate_instance(chapter_request, "chapter_request")
    (nested / "chapter_request.json").write_text(
        json.dumps(chapter_request, indent=2) + "\n",
        encoding="utf-8",
    )

    resolved = resolve_chapter_workspace(series_root, chapter_id="chapter_001")

    assert resolved == nested.resolve()


def test_revision_resume_stage_picks_earliest_implicated_stage() -> None:
    revision_queue = {
        "chapter_clearance": "hold",
        "issues": [
            {"stage_owner": "chapter_layout"},
            {"stage_owner": "chapter_visual"},
            {"stage_owner": "chapter_qc"},
        ],
    }

    resume = revision_resume_stage_from_queue(revision_queue)

    assert resume == sid.CHAPTER_VISUAL


def test_clear_stage_manifests_from_removes_only_later_stages(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    for stage_id in (
        sid.TRANSMISSION_SPLIT,
        sid.CHAPTER_WRITER,
        sid.CHAPTER_VISUAL,
        sid.CHAPTER_IMAGE_GEN,
        sid.CHAPTER_QC,
    ):
        manifest = stage_manifest_path(workspace, stage_id)
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(
            json.dumps({"stage_id": stage_id, "status": "passed"}, indent=2) + "\n",
            encoding="utf-8",
        )

    removed = clear_stage_manifests_from(workspace, sid.CHAPTER_VISUAL)

    assert stage_manifest_path(workspace, sid.TRANSMISSION_SPLIT).is_file()
    assert stage_manifest_path(workspace, sid.CHAPTER_WRITER).is_file()
    assert not stage_manifest_path(workspace, sid.CHAPTER_VISUAL).exists()
    assert not stage_manifest_path(workspace, sid.CHAPTER_IMAGE_GEN).exists()
    assert not stage_manifest_path(workspace, sid.CHAPTER_QC).exists()
    assert [path.parent.name for path in removed] == [
        sid.CHAPTER_VISUAL,
        sid.CHAPTER_IMAGE_GEN,
        sid.CHAPTER_QC,
    ]


def test_attach_sdf_stub_conditioning_adds_panel_metadata() -> None:
    panel_prompts = {
        "schema_version": "1.0.0",
        "artifact_type": "panel_prompts",
        "panels": [
            {"panel_id": "p1", "prompt": "hero in rain", "mood": "tense"},
            {"panel_id": "p2", "prompt": "calm street", "mood": "quiet"},
        ],
    }

    enriched = attach_sdf_stub_conditioning(panel_prompts, map_kind="disabled")
    validate_instance(enriched, "panel_prompts")

    assert enriched["panels"][0]["sdf_conditioning"]["pose_mod"] == "dramatic"
    assert enriched["panels"][1]["sdf_conditioning"]["pose_mod"] == "neutral"
