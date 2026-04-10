"""Resolve job workspace for video stage CLIs."""
from __future__ import annotations

from pathlib import Path


def resolve_video_workspace(
    args: object,
    *,
    out_attr: str = "out",
) -> Path:
    """Prefer explicit --workspace; else directory containing primary output path."""
    w = getattr(args, "workspace", None)
    if w:
        return Path(w).resolve()
    op = getattr(args, out_attr, None)
    if op:
        p = Path(op).resolve()
        return p.parent if p.suffix.lower() in (".json", ".mp4", ".md", ".txt") else p
    cwd = Path.cwd()
    if (cwd / "job.json").exists():
        return cwd
    return cwd
