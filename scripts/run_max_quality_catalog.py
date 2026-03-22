#!/usr/bin/env python3
"""
Run the maximum viable CLI catalog for teacher-mode and/or regular mode, with:
- real run_pipeline CLI compilation
- Stage 6 prose render
- EI V2 comparison artifacts per book
- editorial scoring + rewrite recommendations after the batch

This is a QA-oriented runner, not a release-wave publisher.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("PyYAML is required for run_max_quality_catalog.py") from exc

REPO_ROOT = Path(__file__).resolve().parent.parent
ARCS_ROOT = REPO_ROOT / "config" / "source_of_truth" / "master_arcs"
TEACHER_REGISTRY = REPO_ROOT / "config" / "teachers" / "teacher_registry.yaml"
TEACHER_MATRIX = REPO_ROOT / "config" / "catalog_planning" / "teacher_persona_matrix.yaml"


@dataclass(frozen=True)
class Job:
    mode: str
    teacher_id: str | None
    persona_id: str
    topic_id: str
    engine_id: str
    format_id: str
    arc_path: Path

    @property
    def job_key(self) -> str:
        teacher_part = self.teacher_id or "default_teacher"
        return f"{self.mode}__{teacher_part}__{self.arc_path.stem}"


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _parse_arc(arc_path: Path) -> tuple[str, str, str, str] | None:
    parts = arc_path.stem.split("__")
    if len(parts) != 4:
        return None
    return parts[0], parts[1], parts[2], parts[3]


def build_teacher_jobs(teacher_filter: str | None = None) -> list[Job]:
    registry = (_load_yaml(TEACHER_REGISTRY).get("teachers") or {})
    matrix = (_load_yaml(TEACHER_MATRIX).get("teachers") or {})
    arcs = sorted(ARCS_ROOT.glob("*.yaml"))
    jobs: list[Job] = []

    for teacher_id, teacher_cfg in registry.items():
        if teacher_filter and teacher_id != teacher_filter:
            continue
        matrix_cfg = matrix.get(teacher_id, {})
        allowed_personas = set(matrix_cfg.get("allowed_personas") or [])
        disallowed_personas = set(matrix_cfg.get("disallowed_personas") or [])
        allowed_engines = set(matrix_cfg.get("allowed_engines") or teacher_cfg.get("allowed_engines") or [])

        for arc_path in arcs:
            parsed = _parse_arc(arc_path)
            if not parsed:
                continue
            persona_id, topic_id, engine_id, format_id = parsed
            if allowed_personas and persona_id not in allowed_personas:
                continue
            if persona_id in disallowed_personas:
                continue
            if allowed_engines and engine_id not in allowed_engines:
                continue
            jobs.append(
                Job(
                    mode="teacher_mode",
                    teacher_id=teacher_id,
                    persona_id=persona_id,
                    topic_id=topic_id,
                    engine_id=engine_id,
                    format_id=format_id,
                    arc_path=arc_path,
                )
            )
    return jobs


def build_regular_jobs() -> list[Job]:
    jobs: list[Job] = []
    for arc_path in sorted(ARCS_ROOT.glob("*.yaml")):
        parsed = _parse_arc(arc_path)
        if not parsed:
            continue
        persona_id, topic_id, engine_id, format_id = parsed
        jobs.append(
            Job(
                mode="regular_mode",
                teacher_id=None,
                persona_id=persona_id,
                topic_id=topic_id,
                engine_id=engine_id,
                format_id=format_id,
                arc_path=arc_path,
            )
        )
    return jobs


def _copy_if_exists(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def run_job(job: Job, root_dir: Path, skip_word_count_gate: bool) -> dict:
    teacher_part = job.teacher_id or "default_teacher"
    out_dir = root_dir / job.mode / teacher_part
    plan_path = out_dir / "plans" / f"{job.arc_path.stem}.plan.json"
    render_dir = out_dir / "rendered" / job.arc_path.stem
    ei_dir = out_dir / "ei_v2" / job.arc_path.stem
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    render_dir.mkdir(parents=True, exist_ok=True)

    if plan_path.exists():
        return {
            "job_key": job.job_key,
            "status": "skipped_existing",
            "plan_path": str(plan_path),
            "render_dir": str(render_dir),
            "teacher_id": job.teacher_id,
            "mode": job.mode,
            "persona_id": job.persona_id,
            "topic_id": job.topic_id,
            "engine_id": job.engine_id,
            "format_id": job.format_id,
        }

    cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "run_pipeline.py"),
        "--topic",
        job.topic_id,
        "--persona",
        job.persona_id,
        "--arc",
        str(job.arc_path),
        "--out",
        str(plan_path),
        "--render-book",
        "--render-dir",
        str(render_dir),
        "--no-generate-freebies",
        "--no-update-freebie-index",
        "--ei-v2-compare",
    ]
    if skip_word_count_gate:
        cmd.append("--skip-word-count-gate")
    if job.teacher_id:
        cmd.extend(["--teacher", job.teacher_id])

    proc = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )

    ei_root = REPO_ROOT / "artifacts" / "ei_v2"
    _copy_if_exists(ei_root / "ei_v1_v2_comparison.json", ei_dir / "ei_v1_v2_comparison.json")
    _copy_if_exists(ei_root / "ei_v1_v2_summary.txt", ei_dir / "ei_v1_v2_summary.txt")

    return {
        "job_key": job.job_key,
        "status": "ok" if proc.returncode == 0 else "failed",
        "returncode": proc.returncode,
        "plan_path": str(plan_path),
        "render_dir": str(render_dir),
        "teacher_id": job.teacher_id,
        "mode": job.mode,
        "persona_id": job.persona_id,
        "topic_id": job.topic_id,
        "engine_id": job.engine_id,
        "format_id": job.format_id,
        "stdout_tail": "\n".join(proc.stdout.splitlines()[-10:]),
        "stderr_tail": "\n".join(proc.stderr.splitlines()[-10:]),
    }


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def run_editorial_passes(root_dir: Path) -> None:
    editorial_dir = root_dir / "editorial"
    section_scores = editorial_dir / "section_scores.jsonl"
    rewrite_recs = editorial_dir / "rewrite_recs.jsonl"
    reader_fit = editorial_dir / "reader_fit_scores.jsonl"
    plans_index = editorial_dir / "plans_index.jsonl"

    plan_rows: list[dict] = []
    for plan_path in sorted(root_dir.glob("**/*.plan.json")):
        try:
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        plan_rows.append(
            {
                "book_id": plan.get("plan_id") or plan.get("plan_hash") or plan_path.stem,
                "plan_id": plan.get("plan_id") or plan.get("plan_hash") or plan_path.stem,
                "persona_id": plan.get("persona_id", ""),
                "topic_id": plan.get("topic_id", ""),
                "locale": plan.get("locale", "en-US"),
            }
        )
    _write_jsonl(plans_index, plan_rows)

    subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "ml_editorial" / "run_section_scoring.py"),
            "--plans-dir",
            str(root_dir),
            "--out",
            str(section_scores),
        ],
        cwd=REPO_ROOT,
        check=False,
    )
    subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "ml_editorial" / "run_rewrite_recs.py"),
            "--section-scores",
            str(section_scores),
            "--out",
            str(rewrite_recs),
        ],
        cwd=REPO_ROOT,
        check=False,
    )
    subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "ml_editorial" / "run_reader_fit.py"),
            "--index",
            str(plans_index),
            "--out",
            str(reader_fit),
        ],
        cwd=REPO_ROOT,
        check=False,
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Run max QA catalog with EI and editorial passes")
    ap.add_argument(
        "--mode",
        choices=["teacher", "regular", "both"],
        default="both",
        help="Which catalog to run",
    )
    ap.add_argument("--teacher-id", default=None, help="Limit teacher-mode jobs to one teacher")
    ap.add_argument(
        "--root-dir",
        type=Path,
        default=REPO_ROOT / "artifacts" / "max_quality_catalog",
        help="Output root directory",
    )
    ap.add_argument("--max-jobs", type=int, default=0, help="Optional cap for testing; 0 = all")
    ap.add_argument("--skip-word-count-gate", action="store_true", help="Pass through to run_pipeline")
    ap.add_argument("--list-only", action="store_true", help="Only print job counts")
    args = ap.parse_args()

    jobs: list[Job] = []
    if args.mode in ("teacher", "both"):
        jobs.extend(build_teacher_jobs(args.teacher_id))
    if args.mode in ("regular", "both"):
        jobs.extend(build_regular_jobs())
    if args.max_jobs > 0:
        jobs = jobs[: args.max_jobs]

    teacher_jobs = sum(1 for job in jobs if job.mode == "teacher_mode")
    regular_jobs = sum(1 for job in jobs if job.mode == "regular_mode")
    print(f"Teacher-mode jobs: {teacher_jobs}")
    print(f"Regular-mode jobs: {regular_jobs}")
    print(f"Total jobs: {len(jobs)}")
    if args.list_only:
        return 0

    results: list[dict] = []
    for index, job in enumerate(jobs, start=1):
        print(
            f"[{index}/{len(jobs)}] {job.mode} "
            f"{job.teacher_id or 'default_teacher'} {job.arc_path.stem}",
            flush=True,
        )
        result = run_job(job, args.root_dir, skip_word_count_gate=args.skip_word_count_gate)
        results.append(result)

    manifest_path = args.root_dir / "run_manifest.jsonl"
    _write_jsonl(manifest_path, results)
    run_editorial_passes(args.root_dir)

    ok = sum(1 for row in results if row["status"] == "ok")
    skipped = sum(1 for row in results if row["status"] == "skipped_existing")
    failed = sum(1 for row in results if row["status"] == "failed")
    summary = {
        "teacher_mode_jobs": teacher_jobs,
        "regular_mode_jobs": regular_jobs,
        "total_jobs": len(jobs),
        "ok": ok,
        "skipped_existing": skipped,
        "failed": failed,
    }
    (args.root_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
