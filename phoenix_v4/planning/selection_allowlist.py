"""Book-level allowlists for atom metadata (topic, persona, frame, doctrine quarantine)."""
from __future__ import annotations

from typing import Any


def atom_passes_book_governance(
    metadata: Any,
    *,
    topic_id: str,
    persona_id: str,
    book_frame: str = "somatic_first",
) -> bool:
    """
    Return False when atom metadata explicitly excludes this book context.

    Empty or missing filters mean no restriction. ``doctrine_quarantine`` atoms are
    excluded unless the book uses ``spiritual_first`` frame governance.
    """
    if not isinstance(metadata, dict):
        return True
    tid = (topic_id or "").strip()
    pid = (persona_id or "").strip()
    frame = (book_frame or "somatic_first").strip()

    tf = metadata.get("topic_filter")
    if isinstance(tf, (list, tuple)) and tf and tid and tid not in tf:
        return False
    pf = metadata.get("persona_filter")
    if isinstance(pf, (list, tuple)) and pf and pid and pid not in pf:
        return False
    ff = metadata.get("frame_filter") or metadata.get("allowed_frames")
    if isinstance(ff, (list, tuple)) and ff and frame and frame not in ff:
        return False

    if bool(metadata.get("doctrine_quarantine")) and frame != "spiritual_first":
        return False
    return True
