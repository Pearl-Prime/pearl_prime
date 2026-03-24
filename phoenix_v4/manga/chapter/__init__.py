"""Chapter-stage manga modules."""

from phoenix_v4.manga.chapter.writer import write_chapter_script_pair
from phoenix_v4.manga.chapter.visual_from_script import (
    compile_panel_prompts_from_chapter_script,
    iter_panels_from_chapter_script,
)
from phoenix_v4.manga.chapter.writer_stub import build_chapter_script_pair_from_handoff

__all__ = [
    "build_chapter_script_pair_from_handoff",
    "write_chapter_script_pair",
    "compile_panel_prompts_from_chapter_script",
    "iter_panels_from_chapter_script",
]
