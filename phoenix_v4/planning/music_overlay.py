"""Music-mode V1: additive injection plan (does not alter SOMATIC slot grid).

Returns ordered injection descriptors used by ``music_manuscript_overlay``.
Positions: chapter ``opening``, ``bestseller_beat`` (mid-chapter), ``closing``.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Sequence

from phoenix_v4.planning.story_planner import SCENE_SECTION_INDICES

MusicPosition = Literal["opening", "bestseller_beat", "closing"]


@dataclass(frozen=True)
class MusicInjectionPoint:
    chapter_index: int  # 0-based
    position: MusicPosition
    """Atom pool subdirectory under approved_atoms/ (e.g. LYRIC_OPENING)."""
    atom_pool_key: str


def plan_music_injection(
    *,
    chapter_count: int,
    music_mode: str,
) -> list[MusicInjectionPoint]:
    """Plan additive music slots for every body chapter.

    Mid-chapter placement follows ``music_manuscript_overlay`` paragraph heuristics;
    ``SCENE_SECTION_INDICES`` (sec 5) informs audits via ``bestseller_anchor_section_index``.
    """
    if music_mode not in ("with-lyrics", "no-lyrics"):
        return []
    points: list[MusicInjectionPoint] = []
    for ch in range(max(0, chapter_count)):
        if music_mode == "with-lyrics":
            points.extend(
                [
                    MusicInjectionPoint(ch, "opening", "LYRIC_OPENING"),
                    MusicInjectionPoint(ch, "opening", "MUSIC_REFLECTION_OPENING"),
                    MusicInjectionPoint(ch, "bestseller_beat", "LYRIC_BESTSELLER_BEAT"),
                    MusicInjectionPoint(ch, "bestseller_beat", "MUSIC_REFLECTION_BESTSELLER_BEAT"),
                    MusicInjectionPoint(ch, "closing", "LYRIC_CLOSING"),
                    MusicInjectionPoint(ch, "closing", "MUSIC_REFLECTION_CLOSING"),
                ]
            )
        else:
            points.extend(
                [
                    MusicInjectionPoint(ch, "opening", "MUSIC_REFLECTION_OPENING"),
                    MusicInjectionPoint(ch, "bestseller_beat", "MUSIC_REFLECTION_BESTSELLER_BEAT"),
                    MusicInjectionPoint(ch, "closing", "MUSIC_REFLECTION_CLOSING"),
                ]
            )
    return points


def summarize_injection_plan(points: Sequence[MusicInjectionPoint], *, anchor_section_index: int | None = None) -> dict:
    """Compact JSON-serializable summary for audits."""
    by_ch: dict[str, list[str]] = {}
    for p in points:
        key = f"chapter_{p.chapter_index + 1}"
        by_ch.setdefault(key, []).append(f"{p.position}:{p.atom_pool_key}")
    out: dict = {"injection_points": by_ch, "total": len(points)}
    if anchor_section_index is not None:
        out["bestseller_anchor_section_index"] = anchor_section_index
    return out
