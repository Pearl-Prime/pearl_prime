"""
Book-level rhetorical memory for cross-layer anti-repetition.

Single instance per book render. All four subsystem selectors
(environment, bridge, thesis/mechanism, exercise wrapper) share one
RhetoricalMemory so cross-layer echo detection works.
"""

from __future__ import annotations

import threading
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class UsageRecord:
    """One selection event."""

    chapter_index: int
    layer: str
    sublayer: str
    variant_id: str
    shape: str
    register: str
    movement: str
    instruction_tone: str
    cadence: str
    abstraction_level: str
    root_family: str
    stem: str
    metadata: dict[str, str] = field(default_factory=dict)


class RhetoricalMemory:
    """
    Thread-safe, book-level memory of all rhetorical selections.
    Created once per book render; passed to every selector.
    """

    def __init__(self, total_chapters: int = 20):
        self._lock = threading.Lock()
        self.total_chapters = total_chapters
        self._records: list[UsageRecord] = []
        self._by_chapter: dict[int, list[UsageRecord]] = defaultdict(list)
        self._by_layer: dict[str, list[UsageRecord]] = defaultdict(list)
        self._dimension_counts: dict[str, dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        self._total_selections: int = 0
        self._dimension_caps: dict[str, float] = {
            "shape": 0.30,
            "register": 0.30,
            "movement": 0.30,
            "instruction_tone": 0.40,
            "cadence": 0.40,
            "abstraction_level": 0.40,
            "root_family": 0.40,
        }

    def record(self, rec: UsageRecord) -> None:
        """Record a selection. Thread-safe."""
        with self._lock:
            self._records.append(rec)
            self._by_chapter[rec.chapter_index].append(rec)
            self._by_layer[rec.layer].append(rec)
            for dim_name in (
                "shape",
                "register",
                "movement",
                "instruction_tone",
                "cadence",
                "abstraction_level",
                "root_family",
            ):
                val = getattr(rec, dim_name, "")
                if val:
                    self._dimension_counts[dim_name][val] += 1
            self._total_selections += 1

    def recent_at_layer(
        self,
        layer: str,
        sublayer: str,
        current_chapter: int,
        window: int = 3,
    ) -> list[UsageRecord]:
        """Return records at (layer, sublayer) within the last `window` chapters."""
        with self._lock:
            min_ch = max(0, current_chapter - window)
            return [
                r
                for r in self._by_layer.get(layer, [])
                if r.sublayer == sublayer and min_ch <= r.chapter_index < current_chapter
            ]

    def same_chapter_other_layers(
        self, chapter_index: int, exclude_layer: str
    ) -> list[UsageRecord]:
        """Return all records for the same chapter from OTHER layers."""
        with self._lock:
            return [
                r
                for r in self._by_chapter.get(chapter_index, [])
                if r.layer != exclude_layer
            ]

    def dimension_ratio(self, dim_name: str, dim_value: str) -> float:
        """Return ratio of selections using dim_value for dim_name."""
        with self._lock:
            if self._total_selections == 0:
                return 0.0
            return (
                self._dimension_counts[dim_name][dim_value] / self._total_selections
            )

    def stem_used_recently(
        self,
        layer: str,
        sublayer: str,
        stem: str,
        current_chapter: int,
        window: int = 3,
    ) -> bool:
        """Check if exact stem was used at (layer, sublayer) in last `window` chapters."""
        recent = self.recent_at_layer(layer, sublayer, current_chapter, window)
        return any(r.stem == stem for r in recent)

    def over_budget(self, dim_name: str, dim_value: str) -> bool:
        """Return True when the value exceeds its configured book cap."""
        threshold = self._dimension_caps.get(dim_name, 1.0)
        return self.dimension_ratio(dim_name, dim_value) > threshold

    @property
    def total_selections(self) -> int:
        with self._lock:
            return self._total_selections

