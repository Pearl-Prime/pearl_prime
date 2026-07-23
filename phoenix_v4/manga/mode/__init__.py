"""Manga mode-wrapper system — teacher-mode XOR music-mode (additive / opt-in).

A manga series is the work of ONE archetype — a teacher (doctrine) or a musician
(sound) — never both. The mode is baked into the genre via a native vessel
(config/manga/manga_mode_vessels.yaml) at a 3-beat skeleton. See
artifacts/manga/pilots/MANGA_MODE_WRAPPER_DESIGN.md.

Importing remains side-effect-free. Catalog and production integration is active
when a series resolves to a teacher or active music brand; legacy rows with no
identity remain unchanged.
"""
from __future__ import annotations

from .validator import MODES, ModeError, assert_mode_xor, resolve_mode
from .vessels import VesselError, load_all_vessels, load_vessel
from .catalog import (
    ModeSourceError,
    active_music_brands,
    apply_brand_mode,
    build_mode_source_packet,
)

__all__ = [
    "MODES",
    "ModeError",
    "assert_mode_xor",
    "resolve_mode",
    "VesselError",
    "load_all_vessels",
    "load_vessel",
    "ModeSourceError",
    "active_music_brands",
    "apply_brand_mode",
    "build_mode_source_packet",
]
