"""Resumable chapter DAG: transmission → writer → visual → images → lettering → layout → QC → memory."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)

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
from phoenix_v4.manga.ite_pipeline import (
    annotate_gutter_therapy,
    annotate_panel_breath,
    build_color_arc,
    load_ite_merged_config,
    run_fractal_check,
    run_ite_qc,
)
from phoenix_v4.manga.models import paths as manga_paths
from phoenix_v4.manga.models import stage_ids as sid
from phoenix_v4.manga.models.validation import validate_instance
from phoenix_v4.manga.qc.chapter_qc import build_revision_queue_for_chapter
from phoenix_v4.manga.runner.dag_order import RUN_ORDER, STAGE_NAMES
from phoenix_v4.manga.runner.stage_manifest_io import (
    stage_is_passed,
    write_stage_manifest,
)


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
    sdf_stub: bool,
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
    if sdf_stub:
        from phoenix_v4.manga.sdf.stub import attach_sdf_stub_conditioning

        doc = attach_sdf_stub_conditioning(doc)
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
    _run_ite_artifacts(workspace, manifest)


def _run_ite_artifacts(workspace: Path, manifest: dict[str, Any]) -> None:
    """Implicit Therapeutic Engine: breath → color arc → gutter → fractal → QC (debug/ite)."""
    ite_cfg = load_ite_merged_config()
    script_path = workspace / manga_paths.CHAPTER_SCRIPT_WRITER_HANDOFF
    if not script_path.is_file():
        return
    script = _load_json(script_path)
    ite_dir = workspace / manga_paths.DEBUG_DIR / "ite"
    ite_dir.mkdir(parents=True, exist_ok=True)

    breath = annotate_panel_breath(script, cfg=ite_cfg)
    (ite_dir / "chapter_breath.json").write_text(
        json.dumps(breath, indent=2) + "\n", encoding="utf-8"
    )

    paths_map: dict[str, Path] = {}
    for p in manifest.get("panels") or []:
        pid = str(p.get("panel_id") or "")
        raw = p.get("path")
        if not pid or not raw:
            continue
        path = Path(str(raw))
        if not path.is_absolute():
            path = (workspace / path).resolve()
        if path.is_file():
            paths_map[pid] = path

    color = build_color_arc(breath, paths_map or None, cfg=ite_cfg)
    (ite_dir / "color_arc.json").write_text(json.dumps(color, indent=2) + "\n", encoding="utf-8")

    gutter = annotate_gutter_therapy(breath, cfg=ite_cfg)
    (ite_dir / "chapter_gutter.json").write_text(json.dumps(gutter, indent=2) + "\n", encoding="utf-8")

    fractal = run_fractal_check(paths_map, gutter, cfg=ite_cfg)
    (ite_dir / "fractal_report.json").write_text(json.dumps(fractal, indent=2) + "\n", encoding="utf-8")

    qc_report = run_ite_qc(
        chapter_enriched=gutter,
        color_arc=color,
        fractal_report=fractal,
        breath_doc=breath,
        cfg=ite_cfg,
    )
    (ite_dir / "ite_qc_report.json").write_text(json.dumps(qc_report, indent=2) + "\n", encoding="utf-8")


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


def _stage_bubble_render(workspace: Path) -> None:
    from phoenix_v4.manga.chapter.bubble_render import render_bubbles_on_panels

    script = _load_json(workspace / manga_paths.CHAPTER_SCRIPT_WRITER_HANDOFF)
    lettering = _load_json(workspace / manga_paths.LETTERING_SPEC)
    manifest = _load_json(workspace / manga_paths.PANEL_IMAGES_MANIFEST)
    out_dir = workspace / manga_paths.BUBBLED_PANELS_DIR
    updated = render_bubbles_on_panels(
        chapter_script=script,
        lettering_spec=lettering,
        panel_images_manifest=manifest,
        bubble_style_config=None,
        out_dir=out_dir,
    )
    (workspace / manga_paths.PANEL_IMAGES_MANIFEST).write_text(
        json.dumps(updated, indent=2) + "\n", encoding="utf-8"
    )


def _stage_layout(
    workspace: Path,
    *,
    brand_id: str | None = None,
    genre_id: str | None = None,
) -> None:
    from phoenix_v4.manga.chapter.page_compose import compose_final_page_pngs

    script = _load_json(workspace / manga_paths.CHAPTER_SCRIPT_WRITER_HANDOFF)
    manifest = _load_json(workspace / manga_paths.PANEL_IMAGES_MANIFEST)
    # Skip page composition if no panels have ok status (e.g. noop/dry_run backend)
    ok_panels = [p for p in (manifest.get("panels") or []) if p.get("status") == "ok"]
    if not ok_panels:
        out = workspace / manga_paths.FINAL_PAGE_COMPOSITE_DIR
        out.mkdir(parents=True, exist_ok=True)
        logger.info("No ok panels in manifest — skipping page composition (noop/dry_run mode)")
        return
    # Resolve genre + reading direction for the frame engine. Explicit params
    # win; otherwise read chapter_request.json (genre_family / reading_direction).
    genre = genre_id
    reading_direction: str | None = None
    cr_path = workspace / manga_paths.CHAPTER_REQUEST
    if cr_path.is_file():
        try:
            cr = json.loads(cr_path.read_text(encoding="utf-8"))
            genre = genre or (str(cr.get("genre_family") or "") or None)
            reading_direction = str(cr.get("reading_direction") or "") or None
        except Exception:
            pass
    out = workspace / manga_paths.FINAL_PAGE_COMPOSITE_DIR
    compose_final_page_pngs(
        script, manifest, out, genre=genre, reading_direction=reading_direction
    )


def _ite_dir(workspace: Path) -> Path:
    d = workspace / manga_paths.DEBUG_DIR / "ite"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _stage_ite_breath(workspace: Path) -> None:
    """ITE breath annotation: enrich chapter with breath_phase on panels."""
    ite_cfg = load_ite_merged_config()
    script_path = workspace / manga_paths.CHAPTER_SCRIPT_WRITER_HANDOFF
    if not script_path.is_file():
        return
    script = _load_json(script_path)
    breath = annotate_panel_breath(script, cfg=ite_cfg)
    (_ite_dir(workspace) / "chapter_breath.json").write_text(
        json.dumps(breath, indent=2) + "\n", encoding="utf-8"
    )


def _stage_ite_gutter(workspace: Path) -> None:
    """ITE gutter therapy: assign gutter_class per panel."""
    ite_cfg = load_ite_merged_config()
    breath_path = _ite_dir(workspace) / "chapter_breath.json"
    if not breath_path.is_file():
        # Fall back to chapter script if breath not yet run
        script_path = workspace / manga_paths.CHAPTER_SCRIPT_WRITER_HANDOFF
        if not script_path.is_file():
            return
        breath = _load_json(script_path)
    else:
        breath = _load_json(breath_path)
    gutter = annotate_gutter_therapy(breath, cfg=ite_cfg)
    (_ite_dir(workspace) / "chapter_gutter.json").write_text(
        json.dumps(gutter, indent=2) + "\n", encoding="utf-8"
    )


def _stage_ite_color_arc(workspace: Path) -> None:
    """ITE color arc: per-panel color temperature targets."""
    ite_cfg = load_ite_merged_config()
    breath_path = _ite_dir(workspace) / "chapter_breath.json"
    if not breath_path.is_file():
        return
    breath = _load_json(breath_path)
    manifest_path = workspace / manga_paths.PANEL_IMAGES_MANIFEST
    paths_map: dict[str, Path] = {}
    if manifest_path.is_file():
        manifest = _load_json(manifest_path)
        for p in manifest.get("panels") or []:
            pid = str(p.get("panel_id") or "")
            raw = p.get("path")
            if not pid or not raw:
                continue
            path = Path(str(raw))
            if not path.is_absolute():
                path = (workspace / path).resolve()
            if path.is_file():
                paths_map[pid] = path
    color = build_color_arc(breath, paths_map or None, cfg=ite_cfg)
    (_ite_dir(workspace) / "color_arc.json").write_text(
        json.dumps(color, indent=2) + "\n", encoding="utf-8"
    )


def _stage_ite_fractal(workspace: Path) -> None:
    """ITE fractal compliance check."""
    ite_cfg = load_ite_merged_config()
    gutter_path = _ite_dir(workspace) / "chapter_gutter.json"
    if not gutter_path.is_file():
        return
    gutter = _load_json(gutter_path)
    manifest_path = workspace / manga_paths.PANEL_IMAGES_MANIFEST
    paths_map: dict[str, Path] = {}
    if manifest_path.is_file():
        manifest = _load_json(manifest_path)
        for p in manifest.get("panels") or []:
            pid = str(p.get("panel_id") or "")
            raw = p.get("path")
            if not pid or not raw:
                continue
            path = Path(str(raw))
            if not path.is_absolute():
                path = (workspace / path).resolve()
            if path.is_file():
                paths_map[pid] = path
    fractal = run_fractal_check(paths_map, gutter, cfg=ite_cfg)
    (_ite_dir(workspace) / "fractal_report.json").write_text(
        json.dumps(fractal, indent=2) + "\n", encoding="utf-8"
    )


def _stage_ite_qc(workspace: Path) -> None:
    """ITE QC: run all T-01..T-20 gates."""
    ite_cfg = load_ite_merged_config()
    ite_d = _ite_dir(workspace)
    gutter_path = ite_d / "chapter_gutter.json"
    if not gutter_path.is_file():
        return
    gutter = _load_json(gutter_path)
    breath_path = ite_d / "chapter_breath.json"
    breath = _load_json(breath_path) if breath_path.is_file() else None
    color_path = ite_d / "color_arc.json"
    color = _load_json(color_path) if color_path.is_file() else None
    fractal_path = ite_d / "fractal_report.json"
    fractal = _load_json(fractal_path) if fractal_path.is_file() else None
    qc_report = run_ite_qc(
        chapter_enriched=gutter,
        color_arc=color,
        fractal_report=fractal,
        breath_doc=breath,
        cfg=ite_cfg,
    )
    (ite_d / "ite_qc_report.json").write_text(
        json.dumps(qc_report, indent=2) + "\n", encoding="utf-8"
    )


def _resolve_manga_profile(
    workspace: Path,
    *,
    brand_id: str | None = None,
    genre_id: str | None = None,
) -> "MangaProfile | None":
    """Try to load a MangaProfile for this chapter. Returns None if unavailable (all profile gates skip)."""
    try:
        from phoenix_v4.manga.series.profile_loader import (
            MangaProfile,
            find_profile_for_brand_genre,
            find_profile_for_series,
        )

        # Priority 1: explicit brand_id + genre_id params (caller-supplied)
        if brand_id and genre_id:
            p = find_profile_for_brand_genre(brand_id, genre_id)
            if p is not None:
                return p

        # Priority 2: brand_id + genre_id in chapter_request.json
        cr_path = workspace / manga_paths.CHAPTER_REQUEST
        if cr_path.is_file():
            try:
                cr = json.loads(cr_path.read_text(encoding="utf-8"))
                cr_brand = str(cr.get("brand_id") or "")
                cr_genre = str(cr.get("genre_family") or "")
                if cr_brand and cr_genre:
                    p = find_profile_for_brand_genre(cr_brand, cr_genre)
                    if p is not None:
                        return p

                # Priority 3: series_id lookup (exact title_id match in profiles dir)
                series_id = str(cr.get("series_id") or "")
                if series_id:
                    p = find_profile_for_series(series_id)
                    if p is not None:
                        return p
            except Exception:
                pass

        return None
    except Exception:
        return None


def _stage_qc(workspace: Path, *, brand_id: str | None = None, genre_id: str | None = None) -> None:
    manga_profile = _resolve_manga_profile(workspace, brand_id=brand_id, genre_id=genre_id)
    rq = build_revision_queue_for_chapter(workspace, manga_profile=manga_profile)
    (workspace / manga_paths.REVISION_QUEUE).write_text(
        json.dumps(rq, indent=2) + "\n", encoding="utf-8"
    )
    if rq.get("chapter_clearance") != "pass":
        detail = "; ".join(
            str(x.get("description") or x.get("issue_code"))
            for x in rq.get("issues") or []
        )
        logger.warning("chapter_clearance is hold: %s", detail)


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
    sdf_stub: bool = True,
    brand_id: str | None = None,
    genre_id: str | None = None,
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
            sdf_stub=sdf_stub,
        ),
        sid.CHAPTER_IMAGE_GEN: lambda: _stage_image_gen(ws, image_backend),
        sid.CHAPTER_LETTERING: lambda: _stage_lettering(ws),
        sid.CHAPTER_BUBBLE_RENDER: lambda: _stage_bubble_render(ws),
        sid.CHAPTER_LAYOUT: lambda: _stage_layout(ws, brand_id=brand_id, genre_id=genre_id),
        sid.ITE_BREATH: lambda: _stage_ite_breath(ws),
        sid.ITE_GUTTER: lambda: _stage_ite_gutter(ws),
        sid.ITE_COLOR_ARC: lambda: _stage_ite_color_arc(ws),
        sid.ITE_FRACTAL: lambda: _stage_ite_fractal(ws),
        sid.ITE_QC: lambda: _stage_ite_qc(ws),
        sid.CHAPTER_QC: lambda: _stage_qc(ws, brand_id=brand_id, genre_id=genre_id),
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
                stage_name=STAGE_NAMES.get(st, st),
                status="passed",
                attempt=att,
                outputs={"workspace": str(ws)},
            )
            ran.append(st)
        except Exception as e:
            write_stage_manifest(
                ws,
                st,
                stage_name=STAGE_NAMES.get(st, st),
                status="failed",
                attempt=att,
                error_summary=str(e)[:2000],
            )
            raise

    return ran


def run_chapter_dag_with_auto_revision(
    workspace: Path,
    *,
    image_backend: ImageBackend,
    max_revision_rounds: int = 3,
    from_stage: str | None = None,
    to_stage: str | None = None,
    chapter_number: int = 1,
    config_hash: str = "",
    style_id: str = "dark_psychological",
    teacher_id: str = "ahjan",
    sdf_stub: bool = True,
    brand_id: str | None = None,
    genre_id: str | None = None,
) -> tuple[list[str], int]:
    """On QC hold, clear manifests from earliest implicated stage and re-run (bounded).

    Returns ``(stages_run_cumulative, rounds_used)``.
    """
    from phoenix_v4.manga.runner.revision_policy import (
        clear_stage_manifests_from,
        load_revision_queue,
        revision_resume_stage_from_queue,
    )

    ws = Path(workspace).resolve()
    all_ran: list[str] = []
    cur_from = from_stage
    cur_to = to_stage
    for round_idx in range(max_revision_rounds):
        try:
            ran = run_chapter_dag(
                ws,
                image_backend=image_backend,
                from_stage=cur_from,
                to_stage=cur_to,
                chapter_number=chapter_number,
                config_hash=config_hash,
                style_id=style_id,
                teacher_id=teacher_id,
                sdf_stub=sdf_stub,
                brand_id=brand_id,
                genre_id=genre_id,
            )
            all_ran.extend(ran)
            return all_ran, round_idx + 1
        except RuntimeError as e:
            rq = load_revision_queue(ws)
            if rq is None or rq.get("chapter_clearance") == "pass":
                raise
            resume = revision_resume_stage_from_queue(rq)
            if resume is None:
                raise RuntimeError(
                    "QC hold but no resumable stage_owner in issues"
                ) from e
            if round_idx >= max_revision_rounds - 1:
                raise RuntimeError(
                    f"auto-revision exhausted after {max_revision_rounds} attempt(s): {e}"
                ) from e
            clear_stage_manifests_from(ws, resume)
            cur_from = None
            cur_to = None
    raise RuntimeError("auto-revision loop fell through")
