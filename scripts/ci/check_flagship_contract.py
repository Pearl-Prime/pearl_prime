#!/usr/bin/env python3
"""
Flagship CH1 executable contract CI gate (exemplar-independent structural checks).

Rebuilds CH1 via the canonical production invocation and asserts structural
requirements on schedule + prose. Complements check_flagship_book_parity.py.

Spawned by:
  - .github/workflows/drift-detectors.yml
  - scripts/run_production_readiness_gates.py (gate #29)
  - tests/product/test_flagship_contract.py (pytest wrapper)

Usage:
  python3 scripts/ci/check_flagship_contract.py
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PIPELINE_SCRIPT = REPO_ROOT / "scripts/run_pipeline.py"
APPROVED_MANIFEST = REPO_ROOT / "artifacts/qa/ch1_12shape_preview_v4_20260705/manifest.json"
SEED = "flagship_phase2_layer6"

REFINED_SLOTS = [
    "HOOK", "ANGLE_DEFINITION", "SCENE", "STORY", "PIVOT", "REFLECTION",
    "EXERCISE", "STORY", "STORY", "TAKEAWAY", "INTEGRATION", "THREAD",
]

_FORBIDDEN_CHARACTERS = ("Hana", "Min", "Yuki", "Jordan", "Marcus")
_EXERCISE_GLUE = (
    r"Now we're going to do a practice",
    r"You do not need to believe that",
    r"Just try it",
    r"This is Noting Practice",
    r"Now, I want you to notice something",
    r"Whatever happened — or did not happen — is exactly right",
)
_EMBEDDED_PRACTICE = (
    r"Sit somewhere quiet for two minutes",
    r"Practice noticing the seam",
    r"Find the gap\.",
)
_MED007_BRIDGE = "Do this one out loud. For the next thirty seconds, note whatever appears."
_MED007_BODY_SNIPPET = "gently note them. Thinking. Feeling. Hearing."
_BEAT_FINGERPRINTS = [
    ("HOOK", r"You sent it\. The confirmation appeared"),
    ("ANGLE_DEFINITION", r"protective alarm"),
    ("SCENE", r"Priya's bedroom is dark"),
    ("STORY_recognition", r"Priya submits the project update at 11:47pm"),
    ("PIVOT", r"The update goes out\. No reply comes"),
    ("REFLECTION", r"small space between the sensation and the story"),
    ("EXERCISE", _MED007_BRIDGE),
    ("STORY_mechanism", r"The same loop does not stay inside Slack"),
    ("STORY_turning", r"Priya's temperature is 102\.4"),
    ("TAKEAWAY", r"overthinking isn't you being thorough"),
    ("INTEGRATION", r"11pm Slack-off alarm"),
    ("THREAD", r"tomorrow arriving early"),
]


def extract_ch1_prose(book_text: str) -> str:
    m = re.search(r"Chapter 1\b.*?\n\n(.*?)(?=\n\nChapter 2\b|\Z)", book_text, re.S)
    body = m.group(1).strip() if m else book_text.strip()
    if body.startswith("##"):
        body = body.split("\n\n", 1)[-1].strip()
    return body


def run_flagship_build(render_dir: Path) -> tuple[str, list[str]]:
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
    schedule_path = render_dir / "selected_content_variants.json"
    if not book_path.exists():
        raise RuntimeError("contract build did not emit book.txt")
    ch1 = extract_ch1_prose(book_path.read_text(encoding="utf-8"))
    slots: list[str] = []
    if schedule_path.exists():
        data = json.loads(schedule_path.read_text(encoding="utf-8"))
        ch1_sched = next(c for c in data["chapters"] if c["number"] == 1)
        slots = [s["slot_type"] for s in ch1_sched["slots"]]
    return ch1, slots


def run_contract_checks(ch1_text: str, schedule_slots: list[str]) -> list[str]:
    failures: list[str] = []
    if schedule_slots != REFINED_SLOTS:
        failures.append(f"slot sequence drift: {schedule_slots}")
    cursor = 0
    for label, pattern in _BEAT_FINGERPRINTS:
        m = re.search(pattern, ch1_text[cursor:], re.I | re.S)
        if not m:
            failures.append(f"missing beat fingerprint {label!r}")
        else:
            cursor += m.start() + 1
    if not re.search(r"\bPriya\b", ch1_text):
        failures.append("anchored character Priya missing")
    for forbidden in _FORBIDDEN_CHARACTERS:
        if re.search(rf"\b{re.escape(forbidden)}\b", ch1_text):
            failures.append(f"character stacking: {forbidden}")
    if not re.search(r"protective alarm", ch1_text, re.I):
        failures.append("off-angle: PROTECTIVE_ALARM missing")
    if "small space between the sensation and the story" not in ch1_text.lower():
        failures.append("v03_pure doctrine marker missing")
    for marker in _EMBEDDED_PRACTICE:
        if re.search(marker, ch1_text, re.I):
            failures.append(f"embedded practice in doctrine: {marker}")
    if _MED007_BRIDGE not in ch1_text:
        failures.append("med_007 bridge missing")
    if _MED007_BODY_SNIPPET not in ch1_text:
        failures.append("med_007 body missing")
    if re.search(r"(?i)contemplative tradition teaches", ch1_text):
        failures.append("TEACHER_DOCTRINE preamble present")
    if "TEACHER_DOCTRINE" in ch1_text:
        failures.append("TEACHER_DOCTRINE token in prose")
    glue = [p for p in _EXERCISE_GLUE if re.search(p, ch1_text, re.I)]
    if glue:
        failures.append(f"composer bridge glue: {glue}")
    for para in [p.strip() for p in ch1_text.split("\n\n") if p.strip()]:
        if not re.search(r"[.!?\"')\]]$", para):
            failures.append(f"truncated paragraph end: {para[-80:]!r}")
            break
    if APPROVED_MANIFEST.exists():
        manifest = json.loads(APPROVED_MANIFEST.read_text(encoding="utf-8"))
        expected = [b["slot"] for b in manifest["beats"]]
        if schedule_slots != expected:
            failures.append(f"manifest slot mismatch: {schedule_slots}")
    return failures


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="flagship_contract_") as tmp:
        try:
            ch1_text, schedule_slots = run_flagship_build(Path(tmp))
        except RuntimeError as exc:
            print(f"FAIL: {exc}", file=sys.stderr)
            return 3
    failures = run_contract_checks(ch1_text, schedule_slots)
    if failures:
        print("❌ FLAGSHIP CH1 EXECUTABLE CONTRACT — FAILED", file=sys.stderr)
        for f in failures:
            print(f"   ✗ {f}", file=sys.stderr)
        return 1
    print("✅ FLAGSHIP CH1 EXECUTABLE CONTRACT — ALL CHECKS PASS")
    print(f"   seed:   {SEED}")
    print(f"   words:  {len(ch1_text.split())}")
    print(f"   slots:  {len(schedule_slots)}/12")
    return 0


if __name__ == "__main__":
    sys.exit(main())
