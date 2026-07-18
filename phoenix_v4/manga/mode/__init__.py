"""Manga mode-wrapper system — teacher-mode XOR music-mode (additive / opt-in).

A manga series is the work of ONE archetype — a teacher (doctrine) or a musician
(sound) — never both. The mode is baked into the genre via a native vessel
(config/manga/manga_mode_vessels.yaml) at a 3-beat skeleton. See
artifacts/manga/pilots/MANGA_MODE_WRAPPER_DESIGN.md.

This package is standalone and side-effect-free: importing or calling it changes
NO existing pipeline behavior. Integration into story_architect / chapter_writer
is a separate, opt-in step (only active when a series sets `mode`).
"""
from __future__ import annotations

from .validator import MODES, ModeError, assert_mode_xor, resolve_mode
from .vessels import VesselError, load_all_vessels, load_vessel

__all__ = [
    "MODES",
    "ModeError",
    "assert_mode_xor",
    "resolve_mode",
    "VesselError",
    "load_all_vessels",
    "load_vessel",
]
