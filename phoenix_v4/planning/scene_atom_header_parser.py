"""OPD-114 Phase B: optional SCENE atom header metadata (archetype, depth_level)."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Optional

_ARCHETYPE_DEPTH_RE = re.compile(
    r"\[archetype:\s*([^,\]]+)\s*,\s*depth_level:\s*(\d+)\s*\]",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class SceneAtom:
    atom_id: str
    content: str
    archetype: Optional[str] = None
    depth_level: int = 1


@dataclass(frozen=True)
class SceneAtomHeader:
    atom_id: str
    archetype: Optional[str]
    depth_level: int


def parse_scene_atom_header(header_line: str) -> SceneAtomHeader:
    """Parse ``## SCENE v01`` or ``## SCENE v01 [archetype: x, depth_level: N]``."""
    raw = (header_line or "").strip()
    if raw.startswith("## "):
        raw = raw[3:].strip()
    archetype: Optional[str] = None
    depth_level = 1
    match = _ARCHETYPE_DEPTH_RE.search(raw)
    atom_id = raw
    if match:
        archetype = (match.group(1) or "").strip() or None
        depth_level = max(1, int(match.group(2)))
        atom_id = _ARCHETYPE_DEPTH_RE.sub("", raw).strip()
    return SceneAtomHeader(atom_id=atom_id, archetype=archetype, depth_level=depth_level)


def scene_atom_from_dict(atom: dict[str, Any]) -> SceneAtom:
    meta = dict(atom.get("metadata") or {})
    archetype = meta.get("archetype")
    depth_raw = meta.get("depth_level", 1)
    try:
        depth_level = max(1, int(depth_raw))
    except (TypeError, ValueError):
        depth_level = 1
    arch: Optional[str]
    if archetype is None or str(archetype).strip() == "":
        arch = None
    else:
        arch = str(archetype).strip()
    return SceneAtom(
        atom_id=str(atom.get("atom_id") or ""),
        content=str(atom.get("content") or "").strip(),
        archetype=arch,
        depth_level=depth_level,
    )


def attach_scene_metadata(atom: dict[str, Any], header_line: str) -> dict[str, Any]:
    """Merge parsed header fields into atom metadata (SCENE CANONICAL blocks)."""
    parsed = parse_scene_atom_header(header_line)
    meta = dict(atom.get("metadata") or {})
    meta.setdefault("archetype", parsed.archetype)
    meta.setdefault("depth_level", parsed.depth_level)
    out = dict(atom)
    out["metadata"] = meta
    out["atom_id"] = parsed.atom_id or out.get("atom_id") or ""
    return out
