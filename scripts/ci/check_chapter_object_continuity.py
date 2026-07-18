#!/usr/bin/env python3
"""CI: 12-shape chapter object/character continuity gates."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _run_v4() -> tuple[bool, str]:
    script = REPO_ROOT / "scripts/qa/assemble_ch1_12shape_preview_v4.py"
    if not script.exists():
        return False, "v4 assembler missing"
    subprocess.run(
        [sys.executable, str(script)],
        cwd=str(REPO_ROOT),
        env={**dict(__import__("os").environ), "PYTHONPATH": str(REPO_ROOT)},
        check=False,
    )
    manifest = REPO_ROOT / "artifacts/qa/ch1_12shape_preview_v4_20260705/manifest.json"
    if not manifest.exists():
        return False, "v4 manifest missing"
    gates = json.loads(manifest.read_text())["continuity_gates"]
    bad = [g for g in gates if not g["pass"]]
    return (not bad, "all PASS" if not bad else str(bad))


def _run_filter() -> tuple[bool, str]:
    from phoenix_v4.planning.chapter_object_continuity import (
        ChapterContinuityContext,
        filter_connective_pool,
    )

    ctx = ChapterContinuityContext(2, "Jordan", "morning_calendar_spiral")
    pool = [
        {"atom_id": "HOOK v89", "metadata": {"object": "after_send_reply_anxiety"}},
        {"atom_id": "HOOK v99", "metadata": {"object": "morning_calendar_spiral"}},
    ]
    out = filter_connective_pool(pool, "HOOK", ctx)
    return (len(out) == 1 and out[0]["atom_id"] == "HOOK v99", str(out))


def assert_chapter_continuity_from_manifest(manifest_path: Path) -> None:
    from phoenix_v4.planning.chapter_object_continuity import (
        ChapterContinuityContext,
        ContinuityBeat,
        assert_chapter_continuity,
    )

    data = json.loads(manifest_path.read_text())
    beats = [ContinuityBeat(b["slot"], b.get("atom_id", ""), b.get("prose", "")) for b in data["beats"]]
    ctx = ChapterContinuityContext(
        1, "Priya", "after_send_reply_anxiety", exercise_id="med_007",
        expected_doctrine_snippet="small space between the sensation and the story",
    )
    assert_chapter_continuity(beats, ctx)


def main() -> int:
    ok1, d1 = _run_filter()
    ok2, d2 = _run_v4()
    print(f"filter: {'PASS' if ok1 else 'FAIL'} {d1}")
    print(f"v4 ch1: {'PASS' if ok2 else 'FAIL'} {d2}")
    return 0 if ok1 and ok2 else 1


if __name__ == "__main__":
    sys.exit(main())
