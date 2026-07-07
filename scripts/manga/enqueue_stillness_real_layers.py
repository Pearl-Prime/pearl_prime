#!/usr/bin/env python3
"""Enqueue stillness pilot L1/L3/L4 REAL bank layers on Pearl Star (M5 / #3075).

Bounded LOW-priority batch (~6 images): wall alarm (L1), kettle + cup×3 (L3),
steam (L4).  RAP queue-first via ``enqueue_panel_job`` — never ComfyUI direct.

After renders land on Pearl Star, fetch PNGs into the repo image_bank and
re-assemble ``demo_alarm_metaphor_6p`` at 0 INTERIM (see operator memo).

Tier 1 operator-present. No paid LLM APIs.

Usage:
    # Preflight + print jobs (no dispatch):
    PYTHONPATH=. python3 scripts/manga/enqueue_stillness_real_layers.py --dry-run

    # Enqueue missing layers (skip files already ≥50KB locally):
    PYTHONPATH=. python3 scripts/manga/enqueue_stillness_real_layers.py

    # Force re-enqueue all six:
    PYTHONPATH=. python3 scripts/manga/enqueue_stillness_real_layers.py --force

    # Custom SSH host (default: pearl_star / PS_QUEUE_SSH_HOST):
    PYTHONPATH=. python3 scripts/manga/enqueue_stillness_real_layers.py --ssh-host ahjan108@100.92.68.74
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[2]
SERIES = "stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying"
BANK = REPO / "artifacts" / "manga" / SERIES / "image_bank"
INVENTORY = REPO / "config/source_of_truth/manga_profiles/series/stillness_en_01.object_inventory.yaml"
MIN_REAL_BYTES = 50_000


@dataclass(frozen=True)
class LayerJob:
    layer_id: str
    layer_class: str
    out_path: Path
    prompt: str
    negative: str
    width: int
    height: int


def _load_inventory() -> dict[str, Any]:
    return yaml.safe_load(INVENTORY.read_text(encoding="utf-8"))


def _object(inv: dict[str, Any], object_id: str) -> dict[str, Any]:
    for obj in inv.get("objects") or []:
        if obj.get("object_id") == object_id:
            return obj
    raise KeyError(f"object_id {object_id!r} not in {INVENTORY}")


def build_jobs() -> list[LayerJob]:
    inv = _load_inventory()
    jobs: list[LayerJob] = []
    style = "soft pen-and-ink linework, watercolor wash, iyashikei register"

    kettle = _object(inv, "kettle")
    kettle_prompt = (
        "Matte ceramic kettle, warm cream glaze, simple handle, curved spout, "
        + kettle["prompt_template_extras"]["on_burner_boiling"]
        + ", rendered LARGE filling 80% of frame, pure white backdrop, "
        + style
    )
    jobs.append(
        LayerJob(
            layer_id="kettle_on_burner_boiling",
            layer_class="L3",
            out_path=BANK / "L3" / "kettle_on_burner_boiling.png",
            prompt=kettle_prompt,
            negative="people, person, hands, text, watermark, busy background",
            width=1080,
            height=1920,
        )
    )

    cup = _object(inv, "cup")
    for state in ("empty", "half", "full"):
        cup_prompt = (
            cup["description"]
            + ", "
            + cup["prompt_template_extras"][state]
            + ", rendered LARGE filling 80% of frame, pure white backdrop, "
            + style
        )
        jobs.append(
            LayerJob(
                layer_id=f"cup_{state}",
                layer_class="L3",
                out_path=BANK / "L3" / f"cup_{state}.png",
                prompt=cup_prompt,
                negative="people, person, hands, text, watermark",
                width=1080,
                height=1920,
            )
        )

    jobs.append(
        LayerJob(
            layer_id="wall_alarm_green_idle",
            layer_class="L1",
            out_path=BANK / "L1" / "wall_alarm_green_idle.png",
            prompt=(
                "Round wall-mounted smoke alarm, soft green LED ring idle state, "
                "matte white shell, rendered LARGE centered, pure white backdrop, "
                "soft pen-and-ink linework, iyashikei watercolor register"
            ),
            negative="people, text, watermark, wall, ceiling, background detail",
            width=1080,
            height=1080,
        )
    )

    jobs.append(
        LayerJob(
            layer_id="steam_wisp_rising",
            layer_class="L4",
            out_path=BANK / "L4" / "steam_wisp_rising.png",
            prompt=(
                "Single rising steam plume, soft white wisps curling upward, "
                "gentle undulation, pure black backdrop, no objects, no people"
            ),
            negative="kettle, cup, text, color, background",
            width=1080,
            height=1920,
        )
    )
    return jobs


def preflight_pscli(ssh_host: str) -> None:
    remote = (
        "set -a; . /etc/pearl-star/queue.env 2>/dev/null; "
        f". {REPO}/.pearl_star_queue.env 2>/dev/null; set +a; "
        f"{REPO}/scripts/pearl_star/bin/pscli status"
    )
    proc = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", ssh_host, remote],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"pscli preflight failed on {ssh_host}: "
            f"{proc.stderr.strip() or proc.stdout.strip()}"
        )
    print(proc.stdout.strip(), file=sys.stderr)


def enqueue_jobs(
    jobs: list[LayerJob],
    *,
    task: str,
    ssh_host: str,
    dry_run: bool,
    skip_existing: bool,
) -> list[dict[str, Any]]:
    from scripts.manga.pearl_star_t2i_enqueue import enqueue_panel_job

    results: list[dict[str, Any]] = []
    for job in jobs:
        rel = job.out_path.relative_to(REPO)
        if not dry_run and skip_existing and job.out_path.is_file() and job.out_path.stat().st_size >= MIN_REAL_BYTES:
            print(f"  SKIP {job.layer_id} ({rel}, already REAL)", file=sys.stderr)
            continue
        if dry_run:
            print(
                json.dumps(
                    {
                        "layer_id": job.layer_id,
                        "layer_class": job.layer_class,
                        "out_path": str(rel),
                        "task": task,
                        "width": job.width,
                        "height": job.height,
                    }
                )
            )
            continue
        res = enqueue_panel_job(
            task=task,  # type: ignore[arg-type]
            prompt=job.prompt,
            negative=job.negative,
            width=job.width,
            height=job.height,
            panel_id=job.layer_id,
            out_path=rel,
            ssh_host=ssh_host,
        )
        row = {
            "layer_id": job.layer_id,
            "layer_class": job.layer_class,
            "out_path": str(rel),
            "job_id": res.get("job_id"),
            "via": res.get("via"),
        }
        results.append(row)
        print(f"  QUEUE {job.layer_id} job_id={row['job_id']} via={row['via']}", file=sys.stderr)
    return results


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true", help="list jobs only; no pscli/enqueue")
    ap.add_argument("--force", action="store_true", help="enqueue even when local REAL file exists")
    ap.add_argument("--task", default="t2i_flux_dev_h1a",
                    choices=["t2i_flux_dev_h1a", "t2i_qwen_image", "t2i_flux_schnell"])
    ap.add_argument("--ssh-host", default="", help="Pearl Star SSH host (default: pearl_star)")
    ap.add_argument("--no-preflight", action="store_true", help="skip pscli status check")
    args = ap.parse_args(argv)

    import os

    ssh_host = args.ssh_host or os.environ.get("PS_QUEUE_SSH_HOST", "pearl_star")
    jobs = build_jobs()
    print(f"stillness L1/L3/L4 batch: {len(jobs)} jobs", file=sys.stderr)

    if not args.dry_run and not args.no_preflight:
        preflight_pscli(ssh_host)

    results = enqueue_jobs(
        jobs,
        task=args.task,
        ssh_host=ssh_host,
        dry_run=args.dry_run,
        skip_existing=not args.force,
    )

    if not args.dry_run and results:
        print(json.dumps({"enqueued": len(results), "jobs": results}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
