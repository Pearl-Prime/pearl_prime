#!/usr/bin/env python3
"""CI: flagship 12-shape chapter shape — planner reconciliation + book-wide render gates."""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

PLAN_PATH = (
    REPO_ROOT
    / "config/source_of_truth/twelve_shape_chapter_plans/gen_z_professionals_anxiety.yaml"
)
CH1_MANIFEST = (
    REPO_ROOT / "artifacts/qa/ch1_12shape_preview_v4_20260705/manifest.json"
)
PIPELINE_SCRIPT = REPO_ROOT / "scripts/run_pipeline.py"
SEED = "flagship_phase2_layer6"

REFINED_SLOTS = [
    "HOOK", "ANGLE_DEFINITION", "SCENE", "STORY", "PIVOT", "REFLECTION",
    "EXERCISE", "STORY", "STORY", "TAKEAWAY", "INTEGRATION", "THREAD",
]
_FORBIDDEN_CHARACTERS = (
    "Hana", "Min", "Yuki", "Jordan", "Marcus", "Suki", "Devon", "Leo", "Nia", "Alex", "Sam",
)
_PLACEHOLDER_PATTERNS = (
    r"\[Angle journey —",
    r"callback placeholder",
    r"Prior layer:\s*TODO",
    r"definition placeholder",
)
_THIN_EXERCISE_BRIDGE = re.compile(
    r"Just thirty seconds|Put the book down|Close the book for this",
    re.I,
)
_FIVE_LAYER_INTEGRATION = re.compile(r"before you move on", re.I)
_FIVE_LAYER_INTRO = re.compile(r"This is .+\.", re.I)
_FIVE_LAYER_AHA = re.compile(
    r"notice if your breathing changed|notice something|I want you to notice|Now,\s*notice",
    re.I,
)
_BANK_EMPTY = re.compile(r"\[BANK EMPTY:", re.I)
_CHAPTER_SPLIT = re.compile(r"^Chapter\s+(\d+)\b", re.I | re.M)


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


def split_book_chapters(book_text: str) -> dict[int, str]:
    """Return {chapter_number: prose_body} for a rendered book.txt."""
    matches = list(_CHAPTER_SPLIT.finditer(book_text))
    out: dict[int, str] = {}
    for i, m in enumerate(matches):
        ch_num = int(m.group(1))
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(book_text)
        body = book_text[start:end].strip()
        if body.startswith("##"):
            body = body.split("\n\n", 1)[-1].strip()
        out[ch_num] = body
    return out


def assert_flagship_chapter_shape(
    chapter_text: str,
    *,
    schedule_slots: list[str] | None = None,
    character: str = "Priya",
    chapter_number: int = 1,
    ship_grade: bool = False,
    require_five_layer_exercise: bool = True,
) -> None:
    """Validate rendered chapter prose + optional schedule slot list."""
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
    for pattern in _PLACEHOLDER_PATTERNS:
        if re.search(pattern, chapter_text, re.I):
            failures.append(f"placeholder/scaffolding leaked: {pattern}")
    if re.search(r"\bTODO\b", chapter_text):
        failures.append("TODO token in reader prose")
    if require_five_layer_exercise and chapter_number >= 2:
        has_full = bool(
            _FIVE_LAYER_INTEGRATION.search(chapter_text)
            and _FIVE_LAYER_INTRO.search(chapter_text)
            and _FIVE_LAYER_AHA.search(chapter_text)
        )
        has_bridge = bool(_THIN_EXERCISE_BRIDGE.search(chapter_text))
        if has_bridge and not has_full:
            failures.append("thin body-only exercise (content_only leak)")
        if not has_full:
            failures.append("missing full 5-layer exercise markers")
    if ship_grade and _BANK_EMPTY.search(chapter_text):
        failures.append("BANK EMPTY in ship-grade chapter")
    if chapter_number == 1:
        for marker in (
            r"Sit somewhere quiet for two minutes",
            r"Practice noticing the seam",
        ):
            if re.search(marker, chapter_text, re.I):
                failures.append(f"embedded practice in doctrine: {marker}")
        if "PROTECTIVE_ALARM" not in chapter_text and "protective alarm" not in chapter_text.lower():
            failures.append("off-angle: PROTECTIVE_ALARM missing")
    if failures:
        raise AssertionError(
            f"flagship chapter shape ch{chapter_number}: " + "; ".join(failures)
        )


def assert_flagship_book_shape(
    book_text: str,
    *,
    ship_grade_chapters: frozenset[int] | None = None,
) -> None:
    """Validate every chapter in a rendered flagship build."""
    chapters = split_book_chapters(book_text)
    if len(chapters) < 12:
        raise AssertionError(f"expected 12 chapters, got {len(chapters)}")
    ship = ship_grade_chapters or frozenset({1, 2, 3, 4})
    for ch_num in sorted(chapters):
        assert_flagship_chapter_shape(
            chapters[ch_num],
            chapter_number=ch_num,
            ship_grade=(ch_num in ship),
            require_five_layer_exercise=(ch_num >= 2),
        )


def _run_flagship_build(render_dir: Path) -> str:
    cmd = [
        sys.executable,
        str(PIPELINE_SCRIPT),
        "--topic", "anxiety",
        "--persona", "gen_z_professionals",
        "--arc", "config/source_of_truth/master_arcs/gen_z_professionals__anxiety__overwhelm__F006.yaml",
        "--pipeline-mode", "spine",
        "--runtime-format", "extended_book_2h",
        "--quality-profile", "production",
        "--exercise-journeys",
        "--no-job-check",
        "--render-book",
        "--render-dir", str(render_dir),
        "--seed", SEED,
    ]
    env = {**dict(__import__("os").environ), "PYTHONPATH": str(REPO_ROOT)}
    subprocess.run(cmd, cwd=str(REPO_ROOT), env=env, capture_output=True, text=True, timeout=600, check=False)
    book_path = render_dir / "book.txt"
    if not book_path.exists():
        raise RuntimeError("shape gate build did not emit book.txt")
    return book_path.read_text(encoding="utf-8")


def _validate_book_render() -> tuple[bool, str]:
    with tempfile.TemporaryDirectory(prefix="flagship_shape_") as tmp:
        try:
            book_text = _run_flagship_build(Path(tmp))
        except RuntimeError as exc:
            return False, str(exc)
        try:
            assert_flagship_book_shape(book_text, ship_grade_chapters=frozenset({1, 2, 3, 4}))
        except AssertionError as exc:
            return False, str(exc)
    return True, "book-wide shape gates PASS (ch1–12; ship-grade ch1–4)"


def main() -> int:
    ok_plan, d_plan = _validate_planner()
    ok_manifest, d_manifest = _validate_manifest_gates()
    ok_book, d_book = _validate_book_render()
    print(f"planner: {'PASS' if ok_plan else 'FAIL'} {d_plan}")
    print(f"ch1 manifest: {'PASS' if ok_manifest else 'FAIL'} {d_manifest}")
    print(f"book render: {'PASS' if ok_book else 'FAIL'} {d_book}")
    return 0 if ok_plan and ok_manifest and ok_book else 1


if __name__ == "__main__":
    sys.exit(main())
