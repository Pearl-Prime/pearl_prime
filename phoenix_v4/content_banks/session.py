from __future__ import annotations

from collections import defaultdict, deque
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Deque, Dict, List, Optional, Set


@dataclass
class ContentBankSession:
    """Tracks collision families and reuse limits across a single book render."""

    used_scene_anchor_ids: Set[str] = field(default_factory=set)
    flow_glue_variant_counts: Dict[int, Dict[str, int]] = field(default_factory=dict)
    flow_glue_family_order: Dict[int, Deque[str]] = field(default_factory=dict)
    doctrine_events: List[dict[str, Any]] = field(default_factory=list)

    def flow_counts_for_chapter(self, chapter_index: int) -> Dict[str, int]:
        return self.flow_glue_variant_counts.setdefault(chapter_index, defaultdict(int))

    def flow_recent_families(self, chapter_index: int) -> Deque[str]:
        return self.flow_glue_family_order.setdefault(chapter_index, deque(maxlen=3))

    def record_flow_glue(self, chapter_index: int, variant_id: str, collision_family: str) -> None:
        self.flow_counts_for_chapter(chapter_index)[variant_id] += 1
        if collision_family:
            self.flow_recent_families(chapter_index).append(collision_family)

    def flow_glue_ok(self, chapter_index: int, variant_id: str, collision_family: str) -> bool:
        if self.flow_counts_for_chapter(chapter_index)[variant_id] >= 2:
            return False
        recent = self.flow_recent_families(chapter_index)
        if len(recent) >= 1 and collision_family and collision_family == recent[-1]:
            return False
        return True

    def scene_anchor_ok(self, variant_id: str) -> bool:
        return variant_id not in self.used_scene_anchor_ids

    def record_scene_anchor(self, variant_id: str) -> None:
        self.used_scene_anchor_ids.add(variant_id)


def get_or_create_bank_session(plan: Optional[dict]) -> Optional[ContentBankSession]:
    if not plan:
        return None
    key = "__content_bank_session"
    existing = plan.get(key)
    if isinstance(existing, ContentBankSession):
        return existing
    sess = ContentBankSession()
    plan[key] = sess
    return sess


def variant_logger_from_plan(plan: Optional[dict]) -> Optional[Any]:
    if not plan:
        return None
    raw = plan.get("content_variant_log_path")
    if not raw:
        return None
    from phoenix_v4.content_banks.variant_log import VariantSelectionLogger

    return VariantSelectionLogger(Path(str(raw)))
