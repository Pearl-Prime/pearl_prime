#!/usr/bin/env python3
"""Repair/retry state machine.

Tracks each item through: initial candidate -> targeted repair 1 ->
targeted repair 2 -> fresh regeneration -> quarantine. Pure bookkeeping
(which attempt number, what the prior defect list was, when to stop and
quarantine) -- the actual repair content is Claude's (Lane 02). State is
persisted to a JSON file so a multi-session run is resumable, mirroring
the resumability pattern of the contamination-rewrite pack's checklist
files (docs/agent_prompt_packs/20260720_cjk_contamination_rewrite/).

Usage:
    python3 scripts/localization/translation_quality/repair_state.py \\
        --state-file artifacts/qa/repair_state_zh_cn_20260722.json \\
        --item-id 3a4a36a707b7 --record-attempt initial_candidate \\
        --defects '["untranslated_english"]'

    python3 scripts/localization/translation_quality/repair_state.py \\
        --state-file artifacts/qa/repair_state_zh_cn_20260722.json \\
        --next-stage --item-id 3a4a36a707b7
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Stage order -- fixed, no skipping. quarantine is terminal.
STAGES: tuple[str, ...] = (
    "initial_candidate",
    "targeted_repair_1",
    "targeted_repair_2",
    "fresh_regeneration",
    "quarantine",
)


@dataclass
class Attempt:
    stage: str
    defects: list[str]
    recorded_at: str


@dataclass
class ItemRepairState:
    item_id: str
    current_stage: str = STAGES[0]
    attempts: list[Attempt] = field(default_factory=list)
    accepted: bool = False
    quarantined: bool = False

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        return d

    @staticmethod
    def from_dict(d: dict[str, Any]) -> "ItemRepairState":
        return ItemRepairState(
            item_id=d["item_id"],
            current_stage=d.get("current_stage", STAGES[0]),
            attempts=[Attempt(**a) for a in d.get("attempts", [])],
            accepted=d.get("accepted", False),
            quarantined=d.get("quarantined", False),
        )


class RepairStateStore:
    """Persisted map of item_id -> ItemRepairState."""

    def __init__(self, path: Path):
        self.path = path
        self._items: dict[str, ItemRepairState] = {}
        if path.is_file():
            raw = json.loads(path.read_text(encoding="utf-8"))
            for item_id, d in raw.get("items", {}).items():
                self._items[item_id] = ItemRepairState.from_dict(d)

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"items": {item_id: s.to_dict() for item_id, s in self._items.items()}}
        self.path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def get(self, item_id: str) -> ItemRepairState:
        if item_id not in self._items:
            self._items[item_id] = ItemRepairState(item_id=item_id)
        return self._items[item_id]

    def record_attempt(self, item_id: str, stage: str, defects: list[str]) -> ItemRepairState:
        if stage not in STAGES:
            raise ValueError(f"Unknown stage {stage!r}; must be one of {STAGES}")
        state = self.get(item_id)
        state.current_stage = stage
        state.attempts.append(
            Attempt(stage=stage, defects=defects, recorded_at=datetime.now(timezone.utc).isoformat())
        )
        if stage == "quarantine":
            state.quarantined = True
        return state

    def accept(self, item_id: str) -> ItemRepairState:
        state = self.get(item_id)
        state.accepted = True
        return state

    def advance_stage(self, item_id: str) -> str:
        """Move to the next stage in the fixed order. Returns the new stage.
        Once at quarantine, stays at quarantine (terminal)."""
        state = self.get(item_id)
        idx = STAGES.index(state.current_stage)
        next_idx = min(idx + 1, len(STAGES) - 1)
        state.current_stage = STAGES[next_idx]
        if state.current_stage == "quarantine":
            state.quarantined = True
        return state.current_stage

    def items_at_stage(self, stage: str) -> list[str]:
        return [item_id for item_id, s in self._items.items() if s.current_stage == stage and not s.accepted]

    def summary(self) -> dict[str, int]:
        counts = {stage: 0 for stage in STAGES}
        accepted = 0
        for s in self._items.values():
            if s.accepted:
                accepted += 1
            else:
                counts[s.current_stage] = counts.get(s.current_stage, 0) + 1
        counts["accepted"] = accepted
        return counts


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--state-file", type=Path, required=True)
    ap.add_argument("--item-id")
    ap.add_argument("--record-attempt", metavar="STAGE", choices=STAGES)
    ap.add_argument("--defects", default="[]", help="JSON list of defect strings")
    ap.add_argument("--next-stage", action="store_true", help="Advance item to the next stage")
    ap.add_argument("--accept", action="store_true", help="Mark item accepted")
    ap.add_argument("--summary", action="store_true", help="Print stage counts and exit")
    args = ap.parse_args(argv)

    store = RepairStateStore(args.state_file)

    if args.summary:
        print(json.dumps(store.summary(), indent=2))
        return 0

    if not args.item_id:
        ap.error("--item-id required unless --summary")

    if args.record_attempt:
        defects = json.loads(args.defects)
        store.record_attempt(args.item_id, args.record_attempt, defects)
    if args.next_stage:
        new_stage = store.advance_stage(args.item_id)
        print(f"{args.item_id} -> {new_stage}")
    if args.accept:
        store.accept(args.item_id)

    store.save()
    print(json.dumps(store.get(args.item_id).to_dict(), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
