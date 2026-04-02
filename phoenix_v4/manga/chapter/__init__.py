"""Chapter-stage manga modules."""

from phoenix_v4.manga.chapter.chapter_production import produce_chapter_assets
from phoenix_v4.manga.chapter.lettering_from_script import (
    build_lettering_spec_from_chapter_script,
)
from phoenix_v4.manga.chapter.page_compose import compose_final_page_pngs
from phoenix_v4.manga.chapter.writer import write_chapter_script_pair
from phoenix_v4.manga.chapter.visual_from_script import (
    compile_panel_prompts_from_chapter_script,
    iter_panels_from_chapter_script,
)
from phoenix_v4.manga.chapter.writer_stub import build_chapter_script_pair_from_handoff

__all__ = [
    "build_chapter_script_pair_from_handoff",
    "build_lettering_spec_from_chapter_script",
    "compose_final_page_pngs",
    "compile_panel_prompts_from_chapter_script",
    "iter_panels_from_chapter_script",
    "produce_chapter_assets",
    "write_chapter_script_pair",
]
