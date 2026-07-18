#!/usr/bin/env python3
"""Shared fail-closed helpers for Phoenix Omega manga 100% lanes.

These helpers deliberately distinguish:
- planned
- emitted
- rendered
- human approved

No helper promotes a missing proof to green.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Iterable, Mapping

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

ALLOWED_LANE_STATUSES = {"green", "partial", "blocked", "not-started"}
FINAL_GREEN = "GREEN"
FINAL_NOT_GREEN = "NOT_GREEN"
REQUIRED_TRACE_IDS = (
    "series_id",
    "episode_id",
    "chapter_id",
    "panel_id",
    "beat_id",
    "doctrine_id",
    "layer_role",
    "support_zone_id",
)

_TAG_RE = re.compile(r"(?m)^\s*[-*]?\s*([a-z0-9][a-z0-9_-]*)=([^\n`]+?)\s*$")


class Manga100PctError(RuntimeError):
    """Fail-closed error for the manga 100% integration program."""


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise Manga100PctError(f"could not read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise Manga100PctError(f"expected JSON object: {path}")
    return value


def read_yaml(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise Manga100PctError("PyYAML is required")
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as exc:  # noqa: BLE001
        raise Manga100PctError(f"could not read YAML {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise Manga100PctError(f"expected YAML object: {path}")
    return value


def write_json(path: Path, value: Mapping[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(dict(value), indent=2, ensure_ascii=False, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    return path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def repo_rel(path: Path, repo_root: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve()))
    except ValueError:
        return str(path.resolve())


def assert_no_user_home_strings(paths: Iterable[Path]) -> list[str]:
    failures: list[str] = []
    for path in paths:
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".json", ".yaml", ".yml", ".md", ".tsv", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if "/Users/" in text:
            failures.append(str(path))
    return failures


def extract_tags(text: str) -> dict[str, str]:
    return {key: value.strip() for key, value in _TAG_RE.findall(text)}


def read_closeout_tags(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    return extract_tags(path.read_text(encoding="utf-8", errors="replace"))


def require_keys(row: Mapping[str, Any], keys: Iterable[str], *, label: str) -> list[str]:
    return [f"{label}: missing {key}" for key in keys if row.get(key) in (None, "")]


def bool_env(name: str) -> bool:
    return str(os.environ.get(name, "")).strip().lower() in {"1", "true", "yes", "on"}
