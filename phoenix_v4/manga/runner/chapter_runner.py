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


def _resolve_writer_mode(workspace: Path) -> str:
    """Resolve the chapter writer mode: chapter_request > env > 'claude' (fail-closed default).

    Modes:
      - 'claude': Tier-1 Claude Chapter Writer — the PRODUCTION path. The
        operator-present Tier-1 author (Claude Code / Pearl_Writer) drops a validated
        chapter script pair at ``chapter_script_authored.json`` (or ``MANGA_AUTHORED_SCRIPT``);
        _stage_writer validates + installs it via the LLM-client writer. No paid API is
        called in-process. When mode is 'claude' and no authored pair exists, the stage
        FAILS LOUDLY rather than silently shipping canned stub dialogue.
      - 'stub': deterministic ``writer_stub`` — CI / replay smoke tests only.

    Production runs set ``writer_mode: claude`` in chapter_request.json (or
    ``MANGA_WRITER_MODE=claude``). The default is 'claude' so missing writer_mode
    fails closed instead of silently emitting canned writer_stub dialogue. Replay
    tests must set ``writer_mode: stub`` explicitly. Independent of mode, an authored
    script pair on disk always activates the Tier-1 path (see _stage_writer).
    """
    cr_path = workspace / manga_paths.CHAPTER_REQUEST
    if cr_path.is_file():
        try:
            cr = json.loads(cr_path.read_text(encoding="utf-8"))
            wm = str(cr.get("writer_mode") or "").strip()
            if wm:
                return wm
        except Exception:
            pass
    import os
    return os.environ.get("MANGA_WRITER_MODE", "claude").strip() or "claude"


def _authored_script_path(workspace: Path) -> Path | None:
    """Locate a Tier-1-authored chapter script pair, if present."""
    import os
    env_p = os.environ.get("MANGA_AUTHORED_SCRIPT")
    candidates = []
    if env_p:
        candidates.append(Path(env_p))
    candidates.append(workspace / "chapter_script_authored.json")
    for p in candidates:
        if p.is_file():
            return p
    return None


def _install_authored_script(workspace: Path, authored: Path, cr: dict) -> None:
    """Validate + normalize a Tier-1-authored chapter script pair via the LLM-client writer."""
    from phoenix_v4.manga.chapter.writer import write_chapter_script_pair
    from phoenix_v4.manga.llm.client import ReplayLLMClient

    story = _load_json(workspace / manga_paths.STORY_ARCHITECTURE_HANDOFF)
    validate_instance(story, "story_architecture_handoff")
    client = ReplayLLMClient.from_json_file(authored)
    writer, internal = write_chapter_script_pair(
        client,
        story,
        chapter_number=int(cr.get("chapter_number") or 1),
        series_id=str(cr["series_id"]),
        chapter_id=str(cr["chapter_id"]),
        prompt_version="tier1_claude_authored_v1",
    )
    (workspace / manga_paths.CHAPTER_SCRIPT_WRITER_HANDOFF).write_text(
        json.dumps(writer, indent=2) + "\n", encoding="utf-8"
    )
    (workspace / manga_paths.CHAPTER_SCRIPT_INTERNAL_RECORD).write_text(
        json.dumps(internal, indent=2) + "\n", encoding="utf-8"
    )


def _non_shipping_smoke(workspace: Path) -> bool:
    """True when the caller marked the workspace as non-shipping smoke/draft."""
    import os

    cr_path = workspace / manga_paths.CHAPTER_REQUEST
    if cr_path.is_file():
        try:
            cr = json.loads(cr_path.read_text(encoding="utf-8"))
            if cr.get("non_shipping") or cr.get("smoke_only"):
                return True
            if str(cr.get("quality_profile") or "").strip() == "draft":
                return True
        except Exception:
            pass
    if os.environ.get("MANGA_NON_SHIPPING", "").strip() in {"1", "true", "yes"}:
        return True
    if os.environ.get("MANGA_QUALITY_PROFILE", "").strip() == "draft":
        return True
    return False


def _run_story_excellence_gate(workspace: Path) -> dict[str, Any]:
    """Post-writer excellence realization gate. Always writes the report artifact."""
    from phoenix_v4.manga.story_quality.excellence_gate import evaluate_story_excellence

    story_p = workspace / manga_paths.STORY_ARCHITECTURE_HANDOFF
    writer_p = workspace / manga_paths.CHAPTER_SCRIPT_WRITER_HANDOFF
    internal_p = workspace / manga_paths.CHAPTER_SCRIPT_INTERNAL_RECORD
    story = _load_json(story_p) if story_p.is_file() else {}
    writer = _load_json(writer_p) if writer_p.is_file() else {}
    internal = _load_json(internal_p) if internal_p.is_file() else None
    mode = _resolve_writer_mode(workspace)
    non_shipping = _non_shipping_smoke(workspace)
    # Fail-closed scoring for production writer (claude). Stub is CI/smoke: still
    # evaluate + write report, but do not raise (may WARN/BLOCKED).
    production = mode != "stub"
    report = evaluate_story_excellence(
        story_handoff=story,
        writer_handoff=writer,
        internal_record=internal,
        production=production,
    )
    out = workspace / "story_excellence_realization_report.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    allow_non_pass = mode == "stub" or non_shipping
    if report.get("status") != "PASS" and not allow_non_pass:
        raise RuntimeError(
            "story excellence realization gate status="
            f"{report.get('status')!r} (production requires PASS); "
            f"see {out}"
        )
    if allow_non_pass and report.get("status") != "PASS":
        logger.warning(
            "story excellence gate %s in stub/non-shipping smoke — report written",
            report.get("status"),
        )
    return report


def _require_excellence_pass_for_visual(workspace: Path) -> None:
    """Refuse visual planning when a production workspace lacks a PASS report."""
    report_p = workspace / "story_excellence_realization_report.json"
    mode = _resolve_writer_mode(workspace)
    # Stub / explicit non-shipping smoke may proceed; production must have PASS.
    if mode == "stub" or _non_shipping_smoke(workspace):
        return
    if not report_p.is_file():
        raise RuntimeError(
            "story excellence realization report missing — run chapter writer stage "
            f"before visual (expected {report_p})"
        )
    try:
        report = json.loads(report_p.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"unreadable story excellence report: {exc}") from exc
    if report.get("status") != "PASS":
        raise RuntimeError(
            "production visual planning refused: story excellence status="
            f"{report.get('status')!r} (need PASS); see {report_p}"
        )


def _stage_writer(workspace: Path, chapter_number: int) -> None:
    cr = _load_json(workspace / manga_paths.CHAPTER_REQUEST)
    validate_instance(cr, "chapter_request")
    cr.setdefault("chapter_number", chapter_number)

    mode = _resolve_writer_mode(workspace)
    authored = _authored_script_path(workspace)

    # Tier-1 Claude path: if an operator-authored script pair is present, install it.
    if authored is not None:
        _install_authored_script(workspace, authored, cr)
        _run_story_excellence_gate(workspace)
        return

    if mode == "stub":
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
        _run_story_excellence_gate(workspace)
        return

    # Production 'claude' mode with no authored pair available: fail loudly rather
    # than silently shipping canned writer_stub dialogue as if it were Tier-1 prose.
    raise RuntimeError(
        "Chapter writer mode is 'claude' (Tier-1, production) but no authored chapter "
        "script pair was found. Have the Tier-1 Claude Chapter Writer (operator-present "
        "Claude Code / Pearl_Writer) author the chapter and drop the validated pair at "
        f"{workspace / 'chapter_script_authored.json'} (or set MANGA_AUTHORED_SCRIPT), "
        "or run with writer_mode='stub' (chapter_request.json) / MANGA_WRITER_MODE=stub "
        "for CI smoke tests. English manga authoring is Tier-1 Claude, never a paid API."
    )


def _stage_visual(
    workspace: Path,
    *,
    config_hash: str,
    style_id: str,
    teacher_id: str,
    sdf_stub: bool,
    brand_id: str | None = None,
    genre_id: str | None = None,
) -> None:
    _require_excellence_pass_for_visual(workspace)
    raw = _load_json(workspace / manga_paths.CHAPTER_SCRIPT_WRITER_HANDOFF)
    cr = _load_json(workspace / manga_paths.CHAPTER_REQUEST)
    # Resolve render-routing inputs: explicit caller params win, else chapter_request,
    # else the MangaProfile (brand-genre lane template). All optional — when none
    # resolve, compile_panel_prompts_from_chapter_script keeps the legacy backend path.
    r_brand = brand_id or (str(cr.get("brand_id")) if cr.get("brand_id") else None)
    r_genre = genre_id or (str(cr.get("genre_family")) if cr.get("genre_family") else None)
    r_market_demo = str(cr.get("market_demo")) if cr.get("market_demo") else None
    r_secondary = str(cr.get("secondary_genre")) if cr.get("secondary_genre") else None
    r_color_mode = str(cr.get("color_mode") or "bw")
    profile = _resolve_manga_profile(workspace, brand_id=r_brand, genre_id=r_genre)
    if profile is not None:
        r_genre = r_genre or getattr(profile, "genre_family", None)
        r_market_demo = r_market_demo or getattr(profile, "market_demo", None)
    doc = compile_panel_prompts_from_chapter_script(
        raw,
        series_id=str(cr.get("series_id") or raw.get("series_id") or ""),
        chapter_id=str(cr.get("chapter_id") or raw.get("chapter_id") or ""),
        config_hash=config_hash,
        style_id=style_id,
        teacher_id=teacher_id,
        brand_id=r_brand,
        genre_id=r_genre,
        secondary_genre=r_secondary,
        market_demo=r_market_demo,
        color_mode=r_color_mode,
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


def _resolve_chapter_genre(workspace: Path) -> str | None:
    """Best-effort genre register for this chapter (for bubble styling).

    Order: series/genre_blueprint.json `genre_id` -> chapter_request
    `genre_family`/`genre_id`. Returns None when no genre is known (renderer
    then uses neutral intensity-driven bubbles).
    """
    gb_path = workspace / manga_paths.GENRE_BLUEPRINT
    if gb_path.is_file():
        try:
            gid = str((_load_json(gb_path).get("genre_id") or "")).strip()
            if gid:
                return gid
        except Exception:
            pass
    cr_path = workspace / manga_paths.CHAPTER_REQUEST
    if cr_path.is_file():
        try:
            cr = _load_json(cr_path)
            gid = str((cr.get("genre_family") or cr.get("genre_id") or "")).strip()
            if gid:
                return gid
        except Exception:
            pass
    return None


def _stage_bubble_render(workspace: Path) -> None:
    # V2 renderer: SVG bubble hulls + CJK shaping + furigana + real mouth-target
    # tails + genre-specific bubble styling (shape/font/tail per genre).
    from phoenix_v4.manga.chapter.bubble_render_v2 import render_bubbles_on_panels_v2

    script = _load_json(workspace / manga_paths.CHAPTER_SCRIPT_WRITER_HANDOFF)
    lettering = _load_json(workspace / manga_paths.LETTERING_SPEC)
    manifest = _load_json(workspace / manga_paths.PANEL_IMAGES_MANIFEST)
    out_dir = workspace / manga_paths.BUBBLED_PANELS_DIR
    genre = _resolve_chapter_genre(workspace)
    bubble_style_config = {"genre": genre} if genre else None
    updated = render_bubbles_on_panels_v2(
        chapter_script=script,
        lettering_spec=lettering,
        panel_images_manifest=manifest,
        bubble_style_config=bubble_style_config,
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


def _resolve_quality_profile(
    workspace: Path, quality_profile: str | None
) -> str:
    """Resolve the effective quality profile: explicit arg > chapter_request > env > 'production'.

    'draft' disables the blocking bestseller gate (for CI / replay smoke tests);
    'production' (the default) HARD_FAILs sub-bar chapters before render.
    """
    if quality_profile:
        return quality_profile
    cr_path = workspace / manga_paths.CHAPTER_REQUEST
    if cr_path.is_file():
        try:
            cr = json.loads(cr_path.read_text(encoding="utf-8"))
            qp = str(cr.get("quality_profile") or "").strip()
            if qp:
                return qp
        except Exception:
            pass
    import os
    return os.environ.get("MANGA_QUALITY_PROFILE", "production").strip() or "production"


def _stage_qc(
    workspace: Path,
    *,
    brand_id: str | None = None,
    genre_id: str | None = None,
    quality_profile: str | None = None,
) -> None:
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

    # ── BLOCKING bestseller gate (manga sibling of the book register gate) ──
    # Reads the chapter script + profile, runs the craft + story-substance gates,
    # writes a verdict, and HARD_FAILs (raises) in the 'production' profile when a
    # sub-bar chapter would otherwise render. 'draft' downgrades to a warning.
    from phoenix_v4.manga.qc.bestseller_gate import (
        BestsellerGateError,
        evaluate_bestseller_gate,
    )

    effective_profile = _resolve_quality_profile(workspace, quality_profile)
    script_p = workspace / manga_paths.CHAPTER_SCRIPT_WRITER_HANDOFF
    chapter_script: dict[str, Any] = {}
    if script_p.is_file():
        try:
            chapter_script = json.loads(script_p.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.warning("bestseller gate: could not read chapter script: %s", exc)

    verdict = evaluate_bestseller_gate(chapter_script, manga_profile)
    (workspace / "bestseller_gate_verdict.json").write_text(
        json.dumps({"quality_profile": effective_profile, **verdict}, indent=2) + "\n",
        encoding="utf-8",
    )

    if verdict.get("clearance") == "hard_fail":
        blockers = verdict.get("blockers") or []
        if effective_profile == "draft":
            logger.warning(
                "bestseller gate would HARD_FAIL (%d blocker(s)) — downgraded in 'draft' profile",
                len(blockers),
            )
        else:
            raise BestsellerGateError(blockers)


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
    quality_profile: str | None = None,
) -> list[str]:
    """Execute DAG stages (skipping those already ``passed``). Returns stages executed.

    ``quality_profile`` ("production" default | "draft") controls the blocking
    bestseller gate in the QC stage. "draft" downgrades a sub-bar chapter to a
    warning (for CI / replay smoke tests); "production" HARD_FAILs it.
    """
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
            brand_id=brand_id,
            genre_id=genre_id,
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
        sid.CHAPTER_QC: lambda: _stage_qc(
            ws, brand_id=brand_id, genre_id=genre_id, quality_profile=quality_profile
        ),
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
