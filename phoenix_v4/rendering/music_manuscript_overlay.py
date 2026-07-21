"""Apply additive music overlay to a finished manuscript (spine or registry path)."""
from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from phoenix_v4.planning.music_overlay import plan_music_injection, summarize_injection_plan
from phoenix_v4.planning.story_planner import SCENE_SECTION_INDICES
from phoenix_v4.rendering.intro_conclusion_2p import render_music_conclusion_2p, render_music_intro_2p
from phoenix_v4.rendering.music_composer import build_substitutions, compose_atom_text, load_musician_profile

def _split_manuscript_chapters(prose: str) -> tuple[str, list[tuple[int, str]]]:
    """Return (preamble before Chapter 1, [(n, chapter_text_including_heading), ...])."""
    lines = prose.splitlines()
    first_ch1 = None
    for i, line in enumerate(lines):
        if re.match(r"^\s*Chapter\s+1\s*$", line.strip()):
            first_ch1 = i
            break
    if first_ch1 is None:
        return prose, []

    preamble = "\n".join(lines[:first_ch1]).strip()
    from_chapter_lines = lines[first_ch1:]
    chapters: list[tuple[int, str]] = []
    current_num: int | None = None
    current_buf: list[str] = []
    for line in from_chapter_lines:
        m = re.match(r"^\s*Chapter\s+(\d+)\s*$", line.strip())
        if m:
            if current_num is not None and current_buf:
                chapters.append((current_num, "\n".join(current_buf).strip()))
            current_num = int(m.group(1))
            current_buf = [line]
        elif current_num is not None:
            current_buf.append(line)
    if current_num is not None and current_buf:
        chapters.append((current_num, "\n".join(current_buf).strip()))
    return preamble, chapters


def _format_music_block(title: str, body: str, *, labeled: bool = False) -> str:
    body = body.strip()
    if not body:
        return ""
    if labeled:
        return f"\n\n--- {title} ---\n\n{body}".strip()
    return body


def _blocks_for_chapter(
    repo_root: Path,
    musician_id: str,
    music_mode: str,
    total_chapters: int,
    chapter_index: int,
    book_seed: str,
    persona_id: str,
    topic_id: str,
    substitutions: dict[str, str],
) -> dict[str, str]:
    """Build opening / mid / closing composite strings for one chapter."""
    points = plan_music_injection(chapter_count=total_chapters, music_mode=music_mode)
    by_pos: dict[str, list[str]] = defaultdict(list)
    for p in points:
        if p.chapter_index != chapter_index:
            continue
        txt = compose_atom_text(
            repo_root,
            musician_id,
            p.atom_pool_key,
            chapter_index=chapter_index,
            book_seed=book_seed,
            persona_id=persona_id,
            topic_id=topic_id,
            substitutions=substitutions,
        )
        by_pos[p.position].append(txt)

    def _join_section(position: str, label: str) -> str:
        parts = by_pos.get(position, [])
        if not parts:
            return ""
        merged = "\n\n".join(parts)
        return _format_music_block(label, merged)

    return {
        "opening": _join_section("opening", "Music — chapter opening"),
        "mid": _join_section("bestseller_beat", "Music — reflection beat"),
        "closing": _join_section("closing", "Music — chapter closing"),
    }


def _insert_mid_into_body(body: str, mid_block: str) -> str:
    """Insert ``mid_block`` into chapter body near bestseller beat (paragraph split)."""
    body = body.strip()
    if not mid_block or not body:
        return body
    paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    if len(paras) <= 1:
        return body + "\n\n" + mid_block.strip()

    # After fourth paragraph when possible (aligns loosely with SCENE section 5 placement).
    insert_after = min(3, max(0, len(paras) - 2))
    before = paras[: insert_after + 1]
    after = paras[insert_after + 1 :]
    return "\n\n".join(before) + "\n\n" + mid_block.strip() + "\n\n" + "\n\n".join(after)


def _insert_opening_after_native_start(body: str, opening_block: str) -> str:
    """Let the chapter establish its native voice before adding music prose."""
    body = body.strip()
    if not opening_block or not body:
        return body
    paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    if len(paras) <= 1:
        return body + "\n\n" + opening_block.strip()
    insert_after = min(1, len(paras) - 1)
    before = paras[: insert_after + 1]
    after = paras[insert_after + 1 :]
    return "\n\n".join(before) + "\n\n" + opening_block.strip() + "\n\n" + "\n\n".join(after)


def _patch_chapter_text(ch_text: str, blocks: dict[str, str]) -> str:
    lines = ch_text.splitlines()
    if not lines:
        return ch_text
    heading = lines[0]
    body = "\n".join(lines[1:]).strip()
    parts: list[str] = [heading]
    if body:
        if blocks.get("opening"):
            body = _insert_opening_after_native_start(body, blocks["opening"])
        body_m = _insert_mid_into_body(body, blocks.get("mid", "")) if blocks.get("mid") else body
        parts.append(body_m)
    if blocks.get("closing"):
        parts.append(blocks["closing"].strip())
    return "\n\n".join(p for p in parts if p).strip()


def apply_music_overlay_to_manuscript(
    prose: str,
    *,
    repo_root: Path,
    music_mode: str,
    musician_id: str,
    persona_id: str,
    topic_id: str,
    book_seed: str,
) -> tuple[str, dict[str, Any]]:
    """Return (new_prose, audit_dict). No-op if ``music_mode`` is ``none``."""
    if music_mode == "none" or not musician_id.strip():
        return prose, {"music_mode": "none", "applied": False}

    profile = load_musician_profile(repo_root, musician_id)
    substitutions = build_substitutions(profile, persona_id, topic_id)

    preamble, chapters = _split_manuscript_chapters(prose)
    if not chapters:
        return prose, {"applied": False, "reason": "no_chapter_1_heading_found"}

    intro = render_music_intro_2p(
        repo_root,
        musician_id,
        persona_id=persona_id,
        topic_id=topic_id,
        book_seed=book_seed,
    )
    outro = render_music_conclusion_2p(
        repo_root,
        musician_id,
        persona_id=persona_id,
        topic_id=topic_id,
        book_seed=book_seed,
    )

    rebuilt: list[str] = []
    if preamble:
        rebuilt.append(preamble)

    if intro:
        rebuilt.append(_format_music_block("A note from your reader", intro))

    n_ch = len(chapters)
    injection_points = plan_music_injection(chapter_count=n_ch, music_mode=music_mode)
    anchor_sec = (
        SCENE_SECTION_INDICES[1]
        if len(SCENE_SECTION_INDICES) > 1
        else (SCENE_SECTION_INDICES[0] if SCENE_SECTION_INDICES else None)
    )

    new_chapters: list[str] = []
    for ch_idx, (_num, ch_text) in enumerate(chapters):
        blocks = _blocks_for_chapter(
            repo_root,
            musician_id,
            music_mode,
            n_ch,
            ch_idx,
            book_seed,
            persona_id,
            topic_id,
            substitutions,
        )
        new_chapters.append(_patch_chapter_text(ch_text, blocks))

    rebuilt.append("\n\n".join(new_chapters))

    if outro:
        rebuilt.append(_format_music_block("Closing note", outro))

    new_prose = "\n\n".join(rebuilt).strip() + "\n"
    audit = {
        "applied": True,
        "music_mode": music_mode,
        "musician_id": musician_id,
        "musician_bank": f"SOURCE_OF_TRUTH/musician_banks/{musician_id}",
        "injection_summary": summarize_injection_plan(
            injection_points,
            anchor_section_index=anchor_sec,
        ),
        "profile_display_name": profile.get("display_name"),
    }
    return new_prose, audit
