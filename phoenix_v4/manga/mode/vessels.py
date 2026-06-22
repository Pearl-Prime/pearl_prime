"""Loader for the manga mode-wrapper vessel config (config/manga/manga_mode_vessels.yaml).

Given a (genre, mode) it returns the genre-native vessel + its 3-beat skeleton, used
when a series sets `mode` to bake teacher doctrine or musician sound into the story.
Pure read; no pipeline coupling.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import yaml

from .validator import MODES, ModeError  # noqa: F401  (re-exported convenience)

_REPO_ROOT = Path(__file__).resolve().parents[3]
_MAIN_REPO = Path("/Users/ahjan/phoenix_omega")
_CONFIG_REL = "config/manga/manga_mode_vessels.yaml"


class VesselError(KeyError):
    """Raised when a (genre, mode) vessel is not found in the config."""


def _config_path(repo_root: Optional[Path] = None) -> Path:
    if repo_root is not None:
        return repo_root / _CONFIG_REL
    here = _REPO_ROOT / _CONFIG_REL
    if here.exists():
        return here
    return _MAIN_REPO / _CONFIG_REL


def load_all_vessels(repo_root: Optional[Path] = None) -> dict[str, Any]:
    path = _config_path(repo_root)
    with open(path, "r", encoding="utf-8") as fh:
        doc = yaml.safe_load(fh) or {}
    return doc.get("genres", {})


def load_vessel(genre: str, mode: str, repo_root: Optional[Path] = None) -> dict[str, Any]:
    """Return the vessel dict {vessel, vessel_desc, beats:{...}} for (genre, mode)."""
    if mode not in MODES:
        raise ModeError(f"mode must be one of {MODES}, got {mode!r}")
    genres = load_all_vessels(repo_root)
    g = genres.get(genre)
    if g is None:
        raise VesselError(f"no vessels configured for genre {genre!r}")
    v = g.get(mode)
    if v is None:
        raise VesselError(f"no {mode}-mode vessel configured for genre {genre!r}")
    return v
