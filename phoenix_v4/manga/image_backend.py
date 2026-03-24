"""Image generation backends: noop (pending) and fixture replay for CI."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from collections.abc import Mapping
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ImageBackend(Protocol):
    """Generate or stub panel images from a panel_prompts artifact."""

    def generate(self, panel_prompts: Mapping[str, Any]) -> list[dict[str, Any]]:
        """Return one result dict per panel (panel_id, status, path?, dimensions, hash?)."""
        ...


class NoopImageBackend:
    """No files written — every panel stays ``pending`` (layout/QC wiring later)."""

    def generate(self, panel_prompts: Mapping[str, Any]) -> list[dict[str, Any]]:
        return [
            {
                "panel_id": p["panel_id"],
                "status": "pending",
                "path": None,
                "width": 0,
                "height": 0,
            }
            for p in panel_prompts.get("panels") or []
        ]


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


class FixtureReplayImageBackend:
    """Map panel_id → image path; emits ok + dimensions + sha256 when file exists."""

    def __init__(self, mapping: dict[str, Path]) -> None:
        self._mapping = {k: Path(v).resolve() for k, v in mapping.items()}

    @classmethod
    def from_json_file(cls, path: Path) -> FixtureReplayImageBackend:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("Replay mapping must be a JSON object of panel_id -> path")
        base = path.parent.resolve()
        out: dict[str, Path] = {}
        for pid, rel in data.items():
            p = Path(rel)
            out[str(pid)] = (base / p).resolve() if not p.is_absolute() else p
        return cls(out)

    def generate(self, panel_prompts: Mapping[str, Any]) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for p in panel_prompts.get("panels") or []:
            pid = str(p["panel_id"])
            file_path = self._mapping.get(pid)
            if file_path is None or not file_path.is_file():
                results.append(
                    {
                        "panel_id": pid,
                        "status": "pending",
                        "path": None,
                        "width": 0,
                        "height": 0,
                    }
                )
                continue
            # Minimal dimensions: skip PIL; use 1x1 for unknown or read PNG header if needed
            width, height = _png_dimensions_if_simple(file_path)
            results.append(
                {
                    "panel_id": pid,
                    "status": "ok",
                    "path": str(file_path),
                    "width": width,
                    "height": height,
                    "content_sha256": _sha256_file(file_path),
                }
            )
        return results


def _png_dimensions_if_simple(path: Path) -> tuple[int, int]:
    """Read width/height from PNG IHDR without Pillow."""
    data = path.read_bytes()
    if len(data) >= 24 and data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR":
        w = int.from_bytes(data[16:20], "big")
        h = int.from_bytes(data[20:24], "big")
        return w, h
    return 512, 512


def build_panel_images_manifest(
    panel_prompts: Mapping[str, Any],
    generation_results: list[dict[str, Any]],
    *,
    schema_version: str = "1.0.0",
) -> dict[str, Any]:
    """Merge panel_prompts with backend results into panel_images_manifest artifact."""
    by_id = {str(r["panel_id"]): r for r in generation_results}
    panels: list[dict[str, Any]] = []
    for p in panel_prompts.get("panels") or []:
        pid = str(p["panel_id"])
        r = by_id.get(pid, {})
        status = str(r.get("status", "pending"))
        entry: dict[str, Any] = {"panel_id": pid, "status": status}
        path = r.get("path")
        if path:
            entry["path"] = path
        w = int(r.get("width") or 0)
        h = int(r.get("height") or 0)
        if status == "ok" and w > 0 and h > 0:
            entry["width"] = w
            entry["height"] = h
        sha = r.get("content_sha256")
        if sha:
            entry["content_sha256"] = sha
        panels.append(entry)
    return {
        "schema_version": schema_version,
        "artifact_type": "panel_images_manifest",
        "panels": panels,
    }
