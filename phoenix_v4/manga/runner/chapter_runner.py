"""Resumable chapter DAG: transmission → writer → visual → images → lettering → layout → QC → memory."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from phoenix_v4.manga.chapter.visual_from_script import compile_panel_prompts_from_chapter_script
from phoenix_v4.manga.chapter.writer_stub import build_chapter_script_pair_from_handoff
from phoenix_v4.manga.image_backend import (
    ImageBackend,
    build_panel_images_manifest,
)
from phoenix_v4.manga.memory.series_memory_merge import (
    apply_series_memory_update,
    build_series_memory_snapshot,
    load_or_init_series_memory,
)
from phoenix_v4.manga.models import paths as manga_paths
from phoenix_v4.manga.models import stage_ids as sid
from phoenix_v4.manga.models.validation import validate_instance
from phoenix_v4.manga.qc.chapter_qc import build_revision_queue_for_chapter
from phoenix_v4.manga.runner.stage_manifest_io import (
    stage_is_passed,
    write_stage_manifest,
)

RUN_ORDER: tuple[str, ...] = (
    sid.TRANSMISSION_SPLIT,
    sid.CHAPTER_WRITER,
    sid.CHAPTER_VISUAL,
    sid.CHAPTER_IMAGE_GEN,
    sid.CHAPTER_LETTERING,
    sid.CHAPTER_LAYOUT,
    sid.CHAPTER_QC,
    sid.SERIES_MEMORY_MERGE,
)

_STAGE_NAMES: dict[str, str] = {
    sid.TRANSMISSION_SPLIT: "Verify story architecture handoff",
    sid.CHAPTER_WRITER: "Chapter script (writer handoff)",
    sid.CHAPTER_VISUAL: "Panel prompts",
    sid.CHAPTER_IMAGE_GEN: "Panel images manifest",
    sid.CHAPTER_LETTERING: "Lettering spec",
    sid.CHAPTER_LAYOUT: "Page composites",
    sid.CHAPTER_QC: "QC revision queue",
    sid.SERIES_MEMORY_MERGE: "Merge series memory",
}


def _slice_run_order(
    from_stage: str | None, to_stage: str | None
) -> tuple[str, ...]:
    seq = list(RUN_ORDER)
    if from_stage is not None:
        if from_stage not in seq:
            raise ValueError(f"Unknown --from-stage {from_stage!r}")
        seq = seq[seq.index(from_stage) :]
    if to_stage is not None:
        if to_stage not in RUN_ORDER:
            raise ValueError(f"Unknown --to-stage {to_stage!r}")
        idx = seq.index(to_stage) if to_stage in seq else -1
        if idx < 0:
            raise ValueError(f"--to-stage {to_stage!r} not in selected range")
        seq = seq[: idx + 1]
    return tuple(seq)


def _attempt(workspace: Path, stage_id: str) -> int:
    from phoenix_v4.manga.runner.stage_manifest_io import stage_manifest_path

    p = stage_manifest_path(workspace, stage_id)
    if not p.is_file():
        return 1
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        return int(d.get("attempt") or 0) + 1
    except (json.JSONDecodeError, TypeError, ValueError):
        return 1


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _stage_transmission(workspace: Path) -> None:
    p = workspace / manga_paths.STORY_ARCHITECTURE_HANDOFF
    if not p.is_file():
        raise FileNotFoundError(f"Missing {p}")
    validate_instance(_load_json(p), "story_architecture_handoff")


def _stage_writer(workspace: Path, chapter_number: int) -> None:
    cr = _load_json(workspace / manga_paths.CHAPTER_REQUEST)
    validate_instance(cr, "chapter_request")
    story = _load_json(workspace / manga_paths.STORY_ARCHITECTURE_HANDOFF)
    validate_instance(story, "story_architecture_handoff")
    writer, internal = build_chapter_script_pair_from_handoff(
        story,
        chapter_number=chapter_number,
        series_id=str(cr["series_id"]),
        chapter_id=str(cr["chapter_id"]),
    )
    validate_instance(writer, "chapter_script_writer_handoff")
    validate_instance(internal, "chapter_script_internal_record")
    (workspace / manga_paths.CHAPTER_SCRIPT_WRITER_HANDOFF).write_text(
        json.dumps(writer, indent=2) + "\n", encoding="utf-8"
    )
    (workspace / manga_paths.CHAPTER_SCRIPT_INTERNAL_RECORD).write_text(
        json.dumps(internal, indent=2) + "\n", encoding="utf-8"
    )


def _stage_visual(
    workspace: Path,
    *,
    config_hash: str,
    style_id: str,
    teacher_id: str,
) -> None:
    raw = _load_json(workspace / manga_paths.CHAPTER_SCRIPT_WRITER_HANDOFF)
    cr = _load_json(workspace / manga_paths.CHAPTER_REQUEST)
    doc = compile_panel_prompts_from_chapter_script(
        raw,
        series_id=str(cr.get("series_id") or raw.get("series_id") or ""),
        chapter_id=str(cr.get("chapter_id") or raw.get("chapter_id") or ""),
        config_hash=config_hash,
        style_id=style_id,
        teacher_id=teacher_id,
    )
    validate_instance(doc, "panel_prompts")
    (workspace / manga_paths.PANEL_PROMPTS).write_text(
        json.dumps(doc, indent=2) + "\n", encoding="utf-8"
    )


def _stage_image_gen(workspace: Path, backend: ImageBackend) -> None:
    pp = _load_json(workspace / manga_paths.PANEL_PROMPTS)
    validate_instance(pp, "panel_prompts")
    gen = backend.generate(pp)
    manifest = build_panel_images_manifest(pp, gen)
    validate_instance(manifest, "panel_images_manifest")
    (workspace / manga_paths.PANEL_IMAGES_MANIFEST).write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


def _stage_lettering(workspace: Path) -> None:
    from phoenix_v4.manga.chapter.lettering_from_script import (
        build_lettering_spec_from_chapter_script,
    )

    raw = _load_json(workspace / manga_paths.CHAPTER_SCRIPT_WRITER_HANDOFF)
    letter = build_lettering_spec_from_chapter_script(raw)
    validate_instance(letter, "lettering_spec")
    (workspace / manga_paths.LETTERING_SPEC).write_text(
        json.dumps(letter, indent=2) + "\n", encoding="utf-8"
    )


def _stage_layout(workspace: Path) -> None:
    from phoenix_v4.manga.chapter.page_compose import compose_final_page_pngs

    script = _load_json(workspace / manga_paths.CHAPTER_SCRIPT_WRITER_HANDOFF)
    manifest = _load_json(workspace / manga_paths.PANEL_IMAGES_MANIFEST)
    out = workspace / manga_paths.FINAL_PAGE_COMPOSITE_DIR
    compose_final_page_pngs(script, manifest, out)


def _stage_qc(workspace: Path) -> None:
    rq = build_revision_queue_for_chapter(workspace)
    (workspace / manga_paths.REVISION_QUEUE).write_text(
        json.dumps(rq, indent=2) + "\n", encoding="utf-8"
    )
    if rq.get("chapter_clearance") != "pass":
        raise RuntimeError(
            "chapter_clearance is hold: "
            + "; ".join(
                str(x.get("description") or x.get("issue_code"))
                for x in rq.get("issues") or []
            )
        )


def _stage_memory(workspace: Path) -> None:
    cr = _load_json(workspace / manga_paths.CHAPTER_REQUEST)
    validate_instance(cr, "chapter_request")
    mem_path = workspace / manga_paths.SERIES_MEMORY
    memory = load_or_init_series_memory(mem_path)
    validate_instance(memory, "series_memory")
    update: dict[str, Any] = {
        "schema_version": "1.0.0",
        "artifact_type": "series_memory_update",
        "patches": [
            {
                "op": "append_fact",
                "fact": {
                    "kind": "chapter_pipeline_completed",
                    "series_id": cr["series_id"],
                    "chapter_id": cr["chapter_id"],
                    "arc_id": cr.get("arc_id"),
                },
            }
        ],
    }
    validate_instance(update, "series_memory_update")
    (workspace / manga_paths.SERIES_MEMORY_UPDATE).write_text(
        json.dumps(update, indent=2) + "\n", encoding="utf-8"
    )
    merged = apply_series_memory_update(memory, update)
    validate_instance(merged, "series_memory")
    mem_path.parent.mkdir(parents=True, exist_ok=True)
    mem_path.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")
    snap = build_series_memory_snapshot(merged)
    validate_instance(snap, "series_memory_snapshot")
    (workspace / manga_paths.SERIES_MEMORY_SNAPSHOT).write_text(
        json.dumps(snap, indent=2) + "\n", encoding="utf-8"
    )


def run_chapter_dag(
    workspace: Path,
    *,
    image_backend: ImageBackend,
    from_stage: str | None = None,
    to_stage: str | None = None,
    chapter_number: int = 1,
    config_hash: str = "",
    style_id: str = "dark_psychological",
    teacher_id: str = "ahjan",
) -> list[str]:
    """Execute DAG stages (skipping those already ``passed``). Returns stages executed."""
    ws = Path(workspace).resolve()
    order = _slice_run_order(from_stage, to_stage)
    ran: list[str] = []

    dispatch: dict[str, Callable[[], None]] = {
        sid.TRANSMISSION_SPLIT: lambda: _stage_transmission(ws),
        sid.CHAPTER_WRITER: lambda: _stage_writer(ws, chapter_number),
        sid.CHAPTER_VISUAL: lambda: _stage_visual(
            ws,
            config_hash=config_hash,
            style_id=style_id,
            teacher_id=teacher_id,
        ),
        sid.CHAPTER_IMAGE_GEN: lambda: _stage_image_gen(ws, image_backend),
        sid.CHAPTER_LETTERING: lambda: _stage_lettering(ws),
        sid.CHAPTER_LAYOUT: lambda: _stage_layout(ws),
        sid.CHAPTER_QC: lambda: _stage_qc(ws),
        sid.SERIES_MEMORY_MERGE: lambda: _stage_memory(ws),
    }

    for st in order:
        if stage_is_passed(ws, st):
            continue
        fn = dispatch[st]
        att = _attempt(ws, st)
        try:
            fn()
            write_stage_manifest(
                ws,
                st,
                stage_name=_STAGE_NAMES.get(st, st),
                status="passed",
                attempt=att,
                outputs={"workspace": str(ws)},
            )
            ran.append(st)
        except Exception as e:
            write_stage_manifest(
                ws,
                st,
                stage_name=_STAGE_NAMES.get(st, st),
                status="failed",
                attempt=att,
                error_summary=str(e)[:2000],
            )
            raise

    return ran
