"""Manga video pose-bank supply tooling (V-Bank V1).

Authority: docs/specs/MANGA_VIDEO_POSE_BANK_SUPPLY_SPEC.md
Implements demand→capture compile, cloud wan2.7 capture burn (import-only
DashScope client), frame extract, INTERIM pose cutouts, ordered gate chain.

This package MUST NOT contain DashScope native async headers or aigc
service path literals — import ``scripts.social.dashscope_free_media`` only.
"""

from __future__ import annotations

__all__ = [
    "ALLOWED_CLOUD_ENGINES",
    "STUB_GUARD_BYTES",
    "SCHEMA_VERSION",
]

SCHEMA_VERSION = "1.0.0"
ALLOWED_CLOUD_ENGINES = frozenset({"wan2.7-t2v", "wan2.7-i2v"})
STUB_GUARD_BYTES = 50_000
