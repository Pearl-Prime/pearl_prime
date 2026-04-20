"""Chapter production: prompts → manifest → lettering → bubble render → page PNGs."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from phoenix_v4.manga.chapter.bubble_render import render_bubbles_on_panels
from phoenix_v4.manga.chapter.lettering_from_script import (
    build_lettering_spec_from_chapter_script,
)
from phoenix_v4.manga.chapter.page_compose import compose_final_page_pngs
from phoenix_v4.manga.chapter.visual_from_script import (
    compile_panel_prompts_from_chapter_script,
)
from phoenix_v4.manga.image_backend import ImageBackend, build_panel_images_manifest
from phoenix_v4.manga.models.validation import validate_instance


def produce_chapter_assets(
    chapter_script: Mapping[str, Any],
    *,
    image_backend: ImageBackend,
    schema_version: str = "1.0.0",
    series_id: str | None = None,
    chapter_id: str | None = None,
    config_hash: str = "",
    style_id: str = "dark_psychological",
    teacher_id: str = "ahjan",
    final_pages_out: Path | None = None,
    bubble_render_out: Path | None = None,
    bubble_style_config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run visual + image backend + lettering + optional bubble render + page composites.

    Pipeline stages executed in order:
      1. ``compile_panel_prompts_from_chapter_script``  (CHAPTER_VISUAL)
      2. ``image_backend.generate``                      (CHAPTER_IMAGE_GEN)
      3. ``build_lettering_spec_from_chapter_script``    (CHAPTER_LETTERING)
      4. ``render_bubbles_on_panels``                    (CHAPTER_BUBBLE_RENDER — optional)
      5. ``compose_final_page_pngs``                     (CHAPTER_LAYOUT — optional)

    Stage 4 (bubble render) runs when ``bubble_render_out`` is provided **and**
    the chapter contains at least one panel with dialogue / SFX / captions.
    It is silently skipped for all-silent chapters.

    Stage 5 (page compose) always receives the updated manifest from stage 4 when
    stage 4 ran, preserving the pipeline's non-destructive contract.

    All JSON artifacts are validated against the manga JSON schemas before return.

    Parameters
    ----------
    chapter_script
        The chapter_script writer handoff dict.
    image_backend
        Backend used to generate panel images (ImageBackend or stub).
    schema_version
        Artifact schema version string (default "1.0.0" for legacy callers;
        lettering uses "2.0.0" when the v2 schema is requested — controlled
        by passing "2.0.0" explicitly).
    series_id / chapter_id / config_hash / style_id / teacher_id
        Forwarded to ``compile_panel_prompts_from_chapter_script``.
    final_pages_out
        If provided, write ``page_NNN.png`` composites to this directory.
    bubble_render_out
        If provided, run CHAPTER_BUBBLE_RENDER and write bubbled panel PNGs
        to this directory.  If None, bubble stage is skipped.
    bubble_style_config
        Optional genre-level style overrides for the bubble renderer.
    """
    sid = series_id if series_id is not None else chapter_script.get("series_id")
    cid = chapter_id if chapter_id is not None else chapter_script.get("chapter_id")

    # ── Stage 1 + 2: visual prompts + image generation ────────────
    panel_prompts = compile_panel_prompts_from_chapter_script(
        chapter_script,
        schema_version=schema_version,
        series_id=sid if isinstance(sid, str) else None,
        chapter_id=cid if isinstance(cid, str) else None,
        config_hash=config_hash,
        style_id=style_id,
        teacher_id=teacher_id,
    )
    validate_instance(panel_prompts, "panel_prompts")

    gen = image_backend.generate(panel_prompts)
    manifest = build_panel_images_manifest(
        panel_prompts, gen, schema_version=schema_version
    )
    validate_instance(manifest, "panel_images_manifest")

    # ── Stage 3: lettering spec (v2 when bubble_render_out requested) ──
    lettering_sv = "2.0.0" if bubble_render_out is not None else schema_version
    lettering = build_lettering_spec_from_chapter_script(
        chapter_script, schema_version=lettering_sv
    )
    validate_instance(lettering, "lettering_spec")

    # ── Stage 4: bubble render (CHAPTER_BUBBLE_RENDER) ────────────
    manifest_for_layout = manifest
    bubble_render_applied = False

    if bubble_render_out is not None:
        # Check if there are any non-silent panels to process
        has_dialogue = any(
            not row.get("silence_confirmed", True)
            for row in lettering.get("lettering_panels") or []
        )
        if has_dialogue:
            manifest_for_layout = render_bubbles_on_panels(
                chapter_script=chapter_script,
                lettering_spec=lettering,
                panel_images_manifest=manifest,
                bubble_style_config=bubble_style_config,
                out_dir=Path(bubble_render_out),
            )
            bubble_render_applied = True

    # ── Stage 5: page composites (CHAPTER_LAYOUT) ─────────────────
    page_paths: list[Path] | None = None
    if final_pages_out is not None:
        page_paths = compose_final_page_pngs(
            chapter_script, manifest_for_layout, Path(final_pages_out)
        )

    out: dict[str, Any] = {
        "panel_prompts": panel_prompts,
        "panel_images_manifest": manifest,
        "lettering_spec": lettering,
    }
    if bubble_render_applied:
        out["panel_images_manifest_bubbled"] = manifest_for_layout
    if page_paths is not None:
        out["final_page_paths"] = page_paths
    return out
