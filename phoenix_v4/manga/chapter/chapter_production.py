"""Chapter production: prompts → manifest → lettering → optional page PNGs."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

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
) -> dict[str, Any]:
    """Run visual + image backend + lettering; optionally write composite page PNGs.

    All JSON artifacts are validated before return.
    """
    sid = series_id if series_id is not None else chapter_script.get("series_id")
    cid = chapter_id if chapter_id is not None else chapter_script.get("chapter_id")

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

    lettering = build_lettering_spec_from_chapter_script(
        chapter_script, schema_version=schema_version
    )
    validate_instance(lettering, "lettering_spec")

    page_paths: list[Path] | None = None
    if final_pages_out is not None:
        page_paths = compose_final_page_pngs(
            chapter_script, manifest, Path(final_pages_out)
        )

    out: dict[str, Any] = {
        "panel_prompts": panel_prompts,
        "panel_images_manifest": manifest,
        "lettering_spec": lettering,
    }
    if page_paths is not None:
        out["final_page_paths"] = page_paths
    return out
