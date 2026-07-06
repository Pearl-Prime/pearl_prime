#!/usr/bin/env python3
"""CI: flagship 12-shape chapter shape — planner reconciliation + ch1 schedule gates."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

PLAN_PATH = (
    REPO_ROOT
    / "config/source_of_truth/twelve_shape_chapter_plans/gen_z_professionals_anxiety.yaml"
)
CH1_MANIFEST = (
    REPO_ROOT / "artifacts/qa/ch1_12shape_preview_v4_20260705/manifest.json"
)
REFINED_SLOTS = [
    "HOOK", "ANGLE_DEFINITION", "SCENE", "STORY", "PIVOT", "REFLECTION",
    "EXERCISE", "STORY", "STORY", "TAKEAWAY", "INTEGRATION", "THREAD",
]
_FORBIDDEN_CHARACTERS = ("Hana", "Min", "Yuki", "Jordan", "Marcus")
_EMBEDDED_PRACTICE = (
    r"Sit somewhere quiet for two minutes",
    r"Practice noticing the seam",
)


def _validate_planner() -> tuple[bool, str]:
    from phoenix_v4.planning.chapter_object_continuity import (
        assert_twelve_shape_plan,
        load_chapter_continuity_plan,
    )

    plan = load_chapter_continuity_plan("gen_z_professionals", "anxiety", REPO_ROOT)
    if not plan:
        return False, "twelve_shape plan missing"
    try:
        assert_twelve_shape_plan(plan)
    except AssertionError as exc:
        return False, str(exc)
    return True, f"12-ch plan reconciled ({PLAN_PATH.name})"


def _validate_manifest_gates() -> tuple[bool, str]:
    if not CH1_MANIFEST.exists():
        return False, "approved ch1 manifest missing"
    manifest = json.loads(CH1_MANIFEST.read_text(encoding="utf-8"))
    if not manifest.get("all_gates_pass"):
        bad = [g for g in manifest.get("continuity_gates", []) if not g.get("pass")]
        return False, f"manifest gates: {bad}"
    return True, "approved ch1 manifest gates PASS"


def assert_flagship_chapter_shape(
    chapter_text: str,
    *,
    schedule_slots: list[str] | None = None,
    character: str = "Priya",
) -> None:
    """Validate rendered ch1 prose + optional schedule slot list."""
    failures: list[str] = []
    if schedule_slots is not None and schedule_slots != REFINED_SLOTS:
        failures.append(f"slot sequence drift: {schedule_slots}")
    if not chapter_text.strip():
        failures.append("empty chapter")
    if character and not re.search(rf"\b{re.escape(character)}\b", chapter_text):
        failures.append(f"anchored character {character!r} missing")
    for forbidden in _FORBIDDEN_CHARACTERS:
        if forbidden != character and re.search(rf"\b{forbidden}\b", chapter_text):
            failures.append(f"character stacking: {forbidden}")
    for marker in _EMBEDDED_PRACTICE:
        if re.search(marker, chapter_text, re.I):
            failures.append(f"embedded practice in doctrine: {marker}")
    if "PROTECTIVE_ALARM" not in chapter_text and "protective alarm" not in chapter_text.lower():
        failures.append("off-angle: PROTECTIVE_ALARM missing")
    if failures:
        raise AssertionError("flagship chapter shape: " + "; ".join(failures))


def main() -> int:
    ok_plan, d_plan = _validate_planner()
    ok_manifest, d_manifest = _validate_manifest_gates()
    print(f"planner: {'PASS' if ok_plan else 'FAIL'} {d_plan}")
    print(f"ch1 manifest: {'PASS' if ok_manifest else 'FAIL'} {d_manifest}")
    return 0 if ok_plan and ok_manifest else 1


if __name__ == "__main__":
    sys.exit(main())
