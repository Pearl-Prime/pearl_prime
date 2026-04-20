"""Locked pipeline stage_id strings."""

from __future__ import annotations

SERIES_VISUAL_IDENTITY = "series_visual_identity"
SERIES_GENRE = "series_genre"
SERIES_STORY_ARCHITECT = "series_story_architect"
TRANSMISSION_SPLIT = "transmission_split"
CHAPTER_WRITER = "chapter_writer"
CHAPTER_VISUAL = "chapter_visual"
CHAPTER_IMAGE_GEN = "chapter_image_gen"
CHAPTER_LETTERING = "chapter_lettering"
CHAPTER_BUBBLE_RENDER = "chapter_bubble_render"
CHAPTER_LAYOUT = "chapter_layout"
CHAPTER_QC = "chapter_qc"
SERIES_MEMORY_MERGE = "series_memory_merge"

# ITE (Implicit Therapeutic Engine) enrichment stages
ITE_BREATH = "ite_breath"
ITE_GUTTER = "ite_gutter"
ITE_COLOR_ARC = "ite_color_arc"
ITE_FRACTAL = "ite_fractal"
ITE_QC = "ite_qc"

ALL_STAGE_IDS: tuple[str, ...] = (
    SERIES_VISUAL_IDENTITY,
    SERIES_GENRE,
    SERIES_STORY_ARCHITECT,
    TRANSMISSION_SPLIT,
    CHAPTER_WRITER,
    CHAPTER_VISUAL,
    CHAPTER_IMAGE_GEN,
    CHAPTER_LETTERING,
    CHAPTER_BUBBLE_RENDER,
    CHAPTER_LAYOUT,
    ITE_BREATH,
    ITE_GUTTER,
    ITE_COLOR_ARC,
    ITE_FRACTAL,
    ITE_QC,
    CHAPTER_QC,
    SERIES_MEMORY_MERGE,
)
