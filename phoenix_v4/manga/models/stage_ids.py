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
CHAPTER_LAYOUT = "chapter_layout"
CHAPTER_QC = "chapter_qc"

ALL_STAGE_IDS: tuple[str, ...] = (
    SERIES_VISUAL_IDENTITY,
    SERIES_GENRE,
    SERIES_STORY_ARCHITECT,
    TRANSMISSION_SPLIT,
    CHAPTER_WRITER,
    CHAPTER_VISUAL,
    CHAPTER_IMAGE_GEN,
    CHAPTER_LETTERING,
    CHAPTER_LAYOUT,
    CHAPTER_QC,
)
