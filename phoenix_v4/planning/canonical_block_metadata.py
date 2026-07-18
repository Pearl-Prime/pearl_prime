"""Parse optional metadata blobs between ``---`` fences in CANONICAL.txt blocks."""
from __future__ import annotations

import json
import re
from typing import Any

_LISTISH = re.compile(r"^\s*\[.*\]\s*$", re.DOTALL)


def _coerce_scalar(raw: str) -> Any:
    s = raw.strip()
    if not s:
        return ""
    low = s.lower()
    if low in ("true", "false"):
        return low == "true"
    if low in ("null", "none"):
        return None
    if s.isdigit():
        return int(s)
    if _LISTISH.match(s):
        try:
            return json.loads(s)
        except json.JSONDecodeError:
            inner = s.strip()[1:-1].strip()
            if not inner:
                return []
            return [p.strip().strip("'\"") for p in inner.split(",") if p.strip()]
    if "," in s and ":" not in s.split(",")[0]:
        parts = [p.strip() for p in s.split(",") if p.strip()]
        if len(parts) > 1:
            return parts
    return s


def parse_canonical_metadata_block(blob: str) -> dict[str, Any]:
    """
    Line-oriented ``Key: value`` headers from a canonical block metadata section.

    Keys are normalized to lowercase snake_case. Values that look like JSON arrays
    or comma-separated lists become Python lists.
    """
    out: dict[str, Any] = {}
    for raw in (blob or "").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, rest = line.partition(":")
        nk = key.strip().lower().replace(" ", "_").replace("-", "_")
        if not nk:
            continue
        val = _coerce_scalar(rest)
        if nk == "id" and val is not None:
            out["id"] = str(val).strip()
        else:
            out[nk] = val
    return out
