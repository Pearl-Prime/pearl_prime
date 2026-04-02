"""Map ``revision_queue`` issues → resume stage; clear stage manifests for auto-revision."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from phoenix_v4.manga.models import paths as manga_paths
from phoenix_v4.manga.models import stage_ids as sid
from phoenix_v4.manga.runner.dag_order import RUN_ORDER
from phoenix_v4.manga.runner.stage_manifest_io import stage_manifest_path

# revision_queue.issue.stage_owner strings from chapter_qc / gates
STAGE_OWNER_TO_STAGE_ID: dict[str, str] = {
    "transmission_split": sid.TRANSMISSION_SPLIT,
    "chapter_writer": sid.CHAPTER_WRITER,
    "chapter_visual": sid.CHAPTER_VISUAL,
    "chapter_image_gen": sid.CHAPTER_IMAGE_GEN,
    "chapter_lettering": sid.CHAPTER_LETTERING,
    "chapter_layout": sid.CHAPTER_LAYOUT,
    "chapter_qc": sid.CHAPTER_QC,
}


def revision_resume_stage_from_queue(revision_queue: Mapping[str, Any]) -> str | None:
    """Earliest pipeline stage that may fix listed issues (min index in ``RUN_ORDER``)."""
    issues = revision_queue.get("issues") or []
    stage_ids: list[str] = []
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        owner = issue.get("stage_owner")
        if isinstance(owner, str) and owner in STAGE_OWNER_TO_STAGE_ID:
            stage_ids.append(STAGE_OWNER_TO_STAGE_ID[owner])
    if not stage_ids:
        return None
    return min(stage_ids, key=lambda x: RUN_ORDER.index(x))


def clear_stage_manifests_from(workspace: Path, from_stage_id: str) -> list[Path]:
    """Remove ``stages/<stage_id>/stage_manifest.json`` for ``from_stage_id`` and all later stages."""
    if from_stage_id not in RUN_ORDER:
        raise ValueError(f"Unknown stage {from_stage_id!r}")
    idx = RUN_ORDER.index(from_stage_id)
    removed: list[Path] = []
    for st in RUN_ORDER[idx:]:
        p = stage_manifest_path(workspace, st)
        if p.is_file():
            p.unlink()
            removed.append(p)
    return removed


def load_revision_queue(workspace: Path) -> dict[str, Any] | None:
    p = Path(workspace) / manga_paths.REVISION_QUEUE
    if not p.is_file():
        return None
    return json.loads(p.read_text(encoding="utf-8"))
