"""Manga QC (revision queue, gate registry)."""

from phoenix_v4.manga.qc.chapter_qc import build_revision_queue_for_chapter
from phoenix_v4.manga.qc.gate_registry import GateSpec, load_gate_registry

__all__ = [
    "GateSpec",
    "build_revision_queue_for_chapter",
    "load_gate_registry",
]
