"""MANGA.CHAPTER.HOOK gate — chapter-end hook type check."""
from __future__ import annotations

from typing import Any, Mapping

from phoenix_v4.manga.series.profile_loader import MangaProfile

# Keywords that signal each hook family in the chapter script's final beat.
_HOOK_SIGNALS: dict[str, list[str]] = {
    "revelation": ["revealed", "realizes", "truth", "discovers", "secret", "exposed"],
    "interruption": ["interrupted", "cut off", "suddenly", "before she could", "before he could", "bursts"],
    "betrayal": ["betray", "lied", "deceived", "never trusted", "was using"],
    "vow": ["swears", "vows", "promises", "will never", "pledges", "oath"],
    "arrival": ["arrives", "appears", "shows up", "standing there", "at the door", "walks in"],
    "almost_confession": ["almost", "nearly said", "stopped", "couldn't", "bit her lip", "looked away", "words caught"],
    "confession_almost_happened": ["almost", "nearly said", "stopped", "couldn't", "bit her lip", "looked away", "words caught"],
    "new_rival": ["rival", "challenger", "new face", "unknown fighter", "who are you"],
    "hidden_truth_glimpse": ["glimpse", "flash", "for just a moment", "briefly", "half-seen"],
    "ominous_image": ["shadow", "symbol", "mark", "omen", "strange", "wrong", "unsettling"],
    "emotional_rupture": ["breaks down", "cries", "shatters", "can't hold", "tears", "voice breaks"],
    "ambiguous_line": ["what did you mean", "?", "—", "or did she", "or did he", "or was it"],
    "what_did_that_mean": ["what did you mean", "what did that mean", "?", "—", "or did she", "or did he"],
    "impossible_task": ["impossible", "can't be done", "no one has ever", "you'll never"],
    # Therapeutic / essay hook families
    "loss_echo": ["still", "remembered", "miss", "absence", "without", "gone", "used to", "echo"],
    "small_wonder": ["noticed", "first time", "ordinary", "simple", "small", "just", "quietly", "always been"],
}


def check_chapter_hook(
    chapter_script: Mapping[str, Any],
    profile: MangaProfile,
) -> dict[str, Any] | None:
    """Return an issue dict if the chapter-end hook doesn't match the profile, else None."""
    chapters = chapter_script.get("chapters") or []
    if not chapters:
        return None
    last_chapter = chapters[-1] if isinstance(chapters[-1], dict) else {}
    pages = last_chapter.get("pages") or []
    if not pages:
        return None
    last_page = pages[-1] if isinstance(pages[-1], dict) else {}
    panels = last_page.get("panels") or []
    if not panels:
        return None
    last_panel = panels[-1] if isinstance(panels[-1], dict) else {}

    # Collect text from last panel + any final narration
    check_text = " ".join([
        str(last_panel.get("narration") or ""),
        str(last_panel.get("caption") or ""),
        " ".join(str(d) for d in (last_panel.get("dialogue") or [])),
        str(last_page.get("chapter_end_note") or ""),
    ]).lower()

    hook_family = profile.chapter_hook_family
    signals = _HOOK_SIGNALS.get(hook_family, [])

    if not check_text.strip():
        return None  # can't check — no text

    matched = any(sig in check_text for sig in signals)
    if matched:
        return None  # gate passes

    return {
        "issue_code": "CHAPTER_HOOK_MISMATCH",
        "gate_id": "MANGA.CHAPTER.HOOK",
        "severity": "MAJOR",
        "stage_owner": "chapter_qc",
        "description": (
            f"Chapter end does not signal hook family '{hook_family}'. "
            f"Expected signals: {signals[:4]}. "
            f"Actual final text (truncated): {check_text[:120]!r}"
        ),
    }
