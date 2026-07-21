#!/usr/bin/env python3
"""Dry-run render work discovery for PearlStar/Conductor-aligned queues."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.pearl_star.dispatch import KNOWN_TASKS  # noqa: E402

DEFAULT_OUT = REPO_ROOT / "artifacts" / "qa" / "session_mining_specs_do_all_20260718" / "spec3_gpu_dispatcher_dryrun"


@dataclass(frozen=True)
class RenderJob:
    job_id: str
    family: str
    source_path: str
    job_class: str
    task: str
    priority: int
    payload: dict[str, Any]
    output_path: str
    dry_run: bool = True
    live_queue_write: bool = False


def _load_yaml(path: Path) -> dict[str, Any]:
    if yaml is None or not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data if isinstance(data, dict) else {}


def _job_id(*parts: str) -> str:
    digest = hashlib.sha1("|".join(parts).encode()).hexdigest()[:14]
    return f"dryrun_{digest}"


def _manga_jobs(limit: int) -> list[RenderJob]:
    path = REPO_ROOT / "config" / "catalog_planning" / "brand_series_plans.yaml"
    data = _load_yaml(path)
    jobs: list[RenderJob] = []
    for brand_id, cfg in sorted((data.get("brands") or {}).items()):
        lanes = ((cfg or {}).get("heavy_lanes") or {})
        for series_key, series in sorted(lanes.items()):
            if not isinstance(series, dict):
                continue
            topic = str(series.get("topic") or (cfg or {}).get("primary_topic") or "anxiety")
            title = str(series.get("title") or series_key)
            jid = _job_id("manga", brand_id, series_key, title)
            jobs.append(
                RenderJob(
                    job_id=jid,
                    family="manga_serial_panel",
                    source_path="config/catalog_planning/brand_series_plans.yaml",
                    job_class="t2i",
                    task="t2i_qwen_image",
                    priority=6,
                    payload={
                        "brand_id": brand_id,
                        "series_key": series_key,
                        "topic": topic,
                        "prompt": f"Dry-run manga panel discovery for {brand_id} / {title}",
                    },
                    output_path=f"artifacts/manga/dry_run/{brand_id}/{series_key}/{jid}.png",
                )
            )
            if len(jobs) >= limit:
                return jobs
    return jobs


def _marketing_jobs(limit: int) -> list[RenderJob]:
    path = REPO_ROOT / "config" / "funnel" / "freebie_to_book_map.yaml"
    data = _load_yaml(path)
    jobs: list[RenderJob] = []
    for topic in sorted((data.get("topics") or {}).keys()):
        jid = _job_id("marketing", topic)
        jobs.append(
            RenderJob(
                job_id=jid,
                family="marketing_visual",
                source_path="config/funnel/freebie_to_book_map.yaml",
                job_class="t2i",
                task="t2i_flux_dev_h1a",
                priority=4,
                payload={
                    "topic": topic,
                    "prompt": f"Dry-run marketing visual discovery for {topic}",
                },
                output_path=f"artifacts/marketing_visuals/dry_run/{topic}/{jid}.png",
            )
        )
        if len(jobs) >= limit:
            return jobs
    return jobs


def build_discovery_plan(
    *,
    families: list[str] | None = None,
    limit_per_family: int = 3,
    github_substrate: str = "blocked",
) -> dict[str, Any]:
    families = families or ["manga", "marketing"]
    jobs: list[RenderJob] = []
    if "manga" in families:
        jobs.extend(_manga_jobs(limit_per_family))
    if "marketing" in families:
        jobs.extend(_marketing_jobs(limit_per_family))
    invalid = [job for job in jobs if KNOWN_TASKS.get(job.task) != job.job_class]
    return {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source_spec": "docs/specs/session_mining_batch_20260718/CATALOG_GPU_DISPATCHER_V1_SPEC.md",
        "dry_run": True,
        "github_substrate": github_substrate,
        "queue_credentials": "configured" if os.environ.get("PS_QUEUE_DSN") else "not_configured",
        "live_queue_writes": "none",
        "public_publishing": "none",
        "jobs": [asdict(job) for job in jobs],
        "validation_errors": [
            f"{job.job_id}: task {job.task} is not registered for {job.job_class}"
            for job in invalid
        ],
        "stats": {
            "families_discovered": len(set(job.family for job in jobs)),
            "dry_run_jobs": len(jobs),
        },
    }


def _markdown(plan: dict[str, Any]) -> str:
    lines = [
        "# Render Job Discovery Dry Run",
        "",
        f"Generated: {plan['generated_at']}",
        "Live queue writes: none",
        f"GitHub substrate: {plan['github_substrate']}",
        "",
        "| Job | Family | Task | Output |",
        "| --- | --- | --- | --- |",
    ]
    for job in plan["jobs"]:
        lines.append(f"| `{job['job_id']}` | {job['family']} | {job['task']} | `{job['output_path']}` |")
    return "\n".join(lines) + "\n"


def write_plan(plan: dict[str, Any], output_dir: Path) -> dict[str, Path]:
    if plan.get("validation_errors"):
        raise SystemExit("\n".join(plan["validation_errors"]))
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "render_job_discovery_dry_run.json"
    md_path = output_dir / "render_job_discovery_dry_run.md"
    json_path.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(plan), encoding="utf-8")
    return {"json": json_path, "markdown": md_path}


def main() -> int:
    parser = argparse.ArgumentParser(description="Dry-run render job discovery")
    parser.add_argument("--family", action="append", dest="families")
    parser.add_argument("--limit-per-family", type=int, default=3)
    parser.add_argument("--github-substrate", default="blocked")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    plan = build_discovery_plan(
        families=args.families,
        limit_per_family=args.limit_per_family,
        github_substrate=args.github_substrate,
    )
    paths = write_plan(plan, args.output_dir)
    print(f"Render job dry-run written: {paths['json']}")
    print("Families: {families_discovered} Jobs: {dry_run_jobs}".format(**plan["stats"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
