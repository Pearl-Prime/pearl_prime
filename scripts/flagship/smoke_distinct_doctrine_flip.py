#!/usr/bin/env python3
"""Smoke-test 12-distinct doctrine flip on a scratch plan copy (no commit).

Proves: apply script works, v01–v15 resolve, 12 distinct, ch1 v03, no DoctrineRotationError,
CH1 golden parity unchanged after restore.
"""
from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PLAN_PATH = (
    REPO_ROOT
    / "config/source_of_truth/twelve_shape_chapter_plans/gen_z_professionals_anxiety.yaml"
)
SEQUENCE_PATH = (
    REPO_ROOT
    / "config/source_of_truth/twelve_shape_chapter_plans"
    / "gen_z_professionals_anxiety_distinct_doctrine_sequence.yaml"
)
APPLY_SCRIPT = REPO_ROOT / "scripts/flagship/apply_distinct_doctrine_to_plan.py"
PARITY_SCRIPT = REPO_ROOT / "scripts/ci/check_flagship_book_parity.py"
PIPELINE = REPO_ROOT / "scripts/run_pipeline.py"


def _run(cmd: list[str], *, cwd: Path | None = None, timeout: int = 600) -> subprocess.CompletedProcess:
    env = {**dict(__import__("os").environ), "PYTHONPATH": str(REPO_ROOT)}
    return subprocess.run(
        cmd, cwd=str(cwd or REPO_ROOT), env=env, capture_output=True, text=True, timeout=timeout,
    )


def _doctrine_ids_from_plan(path: Path) -> dict[int, str]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    out: dict[int, str] = {}
    for ch in data.get("chapters") or []:
        if isinstance(ch, dict):
            out[int(ch["chapter"])] = str(ch.get("doctrine_id") or "").strip()
    return out


def _doctrine_ids_from_enriched() -> list[str]:
    from phoenix_v4.planning.beatmap_compile import (
        compile_beatmap,
        load_format_spec,
        load_topic_engines,
    )
    from phoenix_v4.planning.enrichment_select import EnrichmentRequest, select_enrichment
    from phoenix_v4.planning.knob_apply import apply_knobs, load_knob_profile, load_spine
    from phoenix_v4.planning.doctrine_rotation import normalize_doctrine_id

    topic, persona = "anxiety", "gen_z_professionals"
    fmt = "extended_book_2h"
    spine = load_spine(topic, REPO_ROOT, runtime_format=fmt)
    shaped = apply_knobs(
        spine, load_knob_profile(topic, REPO_ROOT), runtime_format=fmt,
        persona_id=persona, repo_root=REPO_ROOT,
    )
    bm = compile_beatmap(
        shaped, load_topic_engines(topic, REPO_ROOT),
        load_format_spec(fmt, REPO_ROOT), REPO_ROOT,
    )
    book = select_enrichment(
        EnrichmentRequest(
            beatmap=bm,
            teacher_id=None,
            persona_id=persona,
            topic_id=topic,
            seed="distinct_doctrine_smoke",
            publishable_book=False,
            spine_context={"book_frame": "somatic_first"},
        ),
        repo_root=REPO_ROOT,
    )
    picked: list[str] = []
    for ch in book.chapters:
        for slot in ch.slots:
            if slot.slot_type == "REFLECTION" and "composite_doctrine" in slot.source:
                picked.append(normalize_doctrine_id(slot.source_id or ""))
                break
    return picked


def main() -> int:
    failures: list[str] = []
    print("=== doctrine flip smoke (scratch plan, no commit) ===\n")

    # 1. Parity baseline
    print("[1/5] CH1 parity baseline (production plan)...")
    r = _run([sys.executable, str(PARITY_SCRIPT)])
    if r.returncode != 0:
        failures.append("CH1 parity baseline failed before flip")
        print(r.stdout, r.stderr)
    else:
        print(r.stdout.strip())

    backup = PLAN_PATH.read_text(encoding="utf-8")
    before_ids = _doctrine_ids_from_plan(PLAN_PATH)

    with tempfile.TemporaryDirectory(prefix="doctrine_smoke_") as tmp:
        scratch = Path(tmp) / "plan_distinct.yaml"
        shutil.copy2(PLAN_PATH, scratch)

        # 2. Apply flip to scratch
        print("\n[2/5] apply_distinct_doctrine_to_plan.py on scratch copy...")
        r = _run([
            sys.executable, str(APPLY_SCRIPT),
            "--plan", str(scratch),
            "--sequence", str(SEQUENCE_PATH),
        ])
        if r.returncode != 0:
            failures.append(f"apply script failed: {r.stderr}")
        else:
            print(r.stdout.strip())

        flipped = _doctrine_ids_from_plan(scratch)
        seq_data = yaml.safe_load(SEQUENCE_PATH.read_text(encoding="utf-8"))
        expected = {int(k): v for k, v in (seq_data.get("doctrine_by_chapter") or {}).items()}

        if flipped.get(1) != "COMPOSITE_DOCTRINE v03":
            failures.append(f"ch1 doctrine drift in scratch: {flipped.get(1)}")
        if flipped != expected:
            failures.append(f"scratch plan doctrine mismatch: {flipped} != {expected}")
        if len(set(flipped.values())) != 12:
            failures.append(f"expected 12 distinct doctrines, got {len(set(flipped.values()))}")

        nums = [int(re.search(r"v(\d+)", d).group(1)) for d in flipped.values() if re.search(r"v(\d+)", d)]
        if any(n > 15 for n in nums):
            failures.append(f"phantom doctrine num > 15: {nums}")

        # 3. Swap plan temporarily
        print("\n[3/5] enrichment smoke (distinct plan, ch1–12 doctrine resolution)...")
        PLAN_PATH.write_text(scratch.read_text(encoding="utf-8"), encoding="utf-8")
        try:
            try:
                picked = _doctrine_ids_from_enriched()
            except Exception as exc:
                exc_name = type(exc).__name__
                if "DoctrineRotation" in exc_name:
                    failures.append(f"DoctrineRotationError: {exc}")
                else:
                    failures.append(f"enrichment failed: {exc_name}: {exc}")
                picked = []

            if picked:
                print(f"   picked per chapter ({len(picked)}): {picked}")
                if len(picked) < 12:
                    failures.append(f"only {len(picked)} chapters got doctrine")
                if len(set(picked)) != len(set(expected.values())):
                    failures.append("picked doctrines not 12 distinct")
                if picked[0] != "COMPOSITE_DOCTRINE v03":
                    failures.append(f"ch1 enriched picks {picked[0]}, expected v03")
                for n in picked:
                    m = re.search(r"v(\d+)", n)
                    if m and int(m.group(1)) > 15:
                        failures.append(f"phantom in enrichment: {n}")

            # 4. Draft pipeline build (rotation smoke, not mass)
            print("\n[4/5] draft pipeline build (extended_book_2h)...")
            render_dir = Path(tmp) / "render"
            render_dir.mkdir()
            r = _run([
                sys.executable, str(PIPELINE),
                "--topic", "anxiety",
                "--persona", "gen_z_professionals",
                "--arc", "config/source_of_truth/master_arcs/gen_z_professionals__anxiety__overwhelm__F006.yaml",
                "--pipeline-mode", "spine",
                "--runtime-format", "extended_book_2h",
                "--quality-profile", "draft",
                "--exercise-journeys",
                "--no-job-check",
                "--skip-quality-gates",
                "--render-book",
                "--render-dir", str(render_dir),
                "--seed", "distinct_doctrine_smoke",
            ], timeout=600)
            book_path = render_dir / "book.txt"
            if not book_path.exists():
                failures.append("draft build did not emit book.txt")
                print(r.stderr[-2000:] if r.stderr else "no stderr")
            else:
                book = book_path.read_text(encoding="utf-8")
                wc = len(book.split())
                print(f"   book.txt emitted ({wc:,} words)")
                if "[BANK EMPTY" in book and "REFLECTION" in book:
                    pass  # ch9-12 unwired — expected
        finally:
            PLAN_PATH.write_text(backup, encoding="utf-8")

    # 5. Parity after restore
    print("\n[5/5] CH1 parity after plan restore...")
    r = _run([sys.executable, str(PARITY_SCRIPT)])
    if r.returncode != 0:
        failures.append("CH1 parity failed after restore")
        print(r.stderr)
    else:
        print(r.stdout.strip())

    if before_ids == _doctrine_ids_from_plan(PLAN_PATH):
        print("\n   committed plan unchanged (cap-at-5 cycle intact)")
    else:
        failures.append("production plan file mutated after smoke")

    print("\n=== SMOKE RESULT ===")
    if failures:
        for f in failures:
            print(f"  FAIL: {f}")
        return 1
    print("  PASS: distinct-12 flip mechanism verified on scratch plan")
    print("  - apply script OK")
    print("  - 12 distinct v01–v15, ch1 v03")
    print("  - enrichment resolves without DoctrineRotationError")
    print("  - CH1 parity green; production plan restored")
    return 0


if __name__ == "__main__":
    sys.exit(main())
