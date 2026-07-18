"""Ordered chapter pipeline stages (single source for runner + revision policy)."""

from __future__ import annotations

from phoenix_v4.manga.models import stage_ids as sid

# Format IDs must match keys in config/manga/format_adaptation_grammars.yaml
_FORMAT_COMPOSITOR_MAP: dict[str, str] = {
    "print": "PrintCompositor",
    "webtoon": "WebtoonCompositor",
    "motion_comic": "MotionComicCompositor",
    "vertical_short_teaser": "VerticalTeaserCompositor",
}


def get_compositor_for_format(format_id: str) -> str:
    """Return compositor class name for the given format_id.

    Raises ValueError for unknown formats so callers fail loudly
    rather than silently using the wrong compositor.
    """
    try:
        return _FORMAT_COMPOSITOR_MAP[format_id]
    except KeyError:
        known = sorted(_FORMAT_COMPOSITOR_MAP)
        raise ValueError(
            f"Unknown format_id {format_id!r}. Known: {known}"
        ) from None

RUN_ORDER: tuple[str, ...] = (
    sid.TRANSMISSION_SPLIT,
    sid.CHAPTER_WRITER,
    sid.CHAPTER_VISUAL,
    sid.CHAPTER_IMAGE_GEN,
    sid.CHAPTER_LETTERING,
    sid.CHAPTER_BUBBLE_RENDER,
    sid.CHAPTER_LAYOUT,
    sid.ITE_BREATH,
    sid.ITE_GUTTER,
    sid.ITE_COLOR_ARC,
    sid.ITE_FRACTAL,
    sid.ITE_QC,
    sid.CHAPTER_QC,
    sid.SERIES_MEMORY_MERGE,
)

STAGE_NAMES: dict[str, str] = {
    sid.TRANSMISSION_SPLIT: "Verify story architecture handoff",
    sid.CHAPTER_WRITER: "Chapter script (writer handoff)",
    sid.CHAPTER_VISUAL: "Panel prompts",
    sid.CHAPTER_IMAGE_GEN: "Panel images manifest",
    sid.CHAPTER_LETTERING: "Lettering spec",
    sid.CHAPTER_BUBBLE_RENDER: "Speech bubble render",
    sid.CHAPTER_LAYOUT: "Page composites",
    sid.ITE_BREATH: "ITE breath annotation",
    sid.ITE_GUTTER: "ITE gutter therapy",
    sid.ITE_COLOR_ARC: "ITE color arc",
    sid.ITE_FRACTAL: "ITE fractal compliance",
    sid.ITE_QC: "ITE QC gates (T-01..T-20)",
    sid.CHAPTER_QC: "QC revision queue",
    sid.SERIES_MEMORY_MERGE: "Merge series memory",
}
