#!/usr/bin/env python3
"""Enqueue mecha + psychological_thriller M5 bank REAL layers on Pearl Star.

Reads bank_contracts/*.yaml for slots 03–04 (6 layers each: 2 L0 scenes,
2 L2 poses, 2 L3 objects). RAP queue-first via ``enqueue_panel_job``.

Prompt doctrine (2026-07-08 triage): never enqueue the ultra-thin bank-contract
one-liners alone. Enrich from authored ``panel_prompts`` / scene anchors so
Flux cannot collapse "hangar" / "cockpit" into abstract noise. Queue COMPLETED
+ bytes ≥50KB is NOT a usability proof — callers must run
``bank_layer_blob_gate`` after land.

Usage:
    PYTHONPATH=. python3 scripts/manga/enqueue_crossgenre_real_layers.py --dry-run
    PYTHONPATH=. python3 scripts/manga/enqueue_crossgenre_real_layers.py --series mecha
    PYTHONPATH=. python3 scripts/manga/enqueue_crossgenre_real_layers.py --series thriller
    PYTHONPATH=. python3 scripts/manga/enqueue_crossgenre_real_layers.py
    PYTHONPATH=. python3 scripts/manga/enqueue_crossgenre_real_layers.py --layer-id hangar_pre_dawn --force
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from scripts.manga.prompt_authority import build_authority_prompt_block
from scripts.manga.render_request_ledger import (
    build_request_spec,
    fetch_queue_status_map,
    record_enqueue,
    reconcile_requests,
    request_ids_needing_enqueue,
    upsert_requests,
)

REPO = Path(__file__).resolve().parents[2]
MANGA = REPO / "artifacts" / "manga"
PANEL_PROMPTS = MANGA / "panel_prompts"
MIN_REAL_BYTES = 50_000
MECHA_CLEAN_LAYER_IDS = {
    "hangar_pre_dawn",
    "cockpit_interior",
    "seated_cockpit",
    "threshold_stand",
    "glove_pad",
    "telemetry_panel",
}

# Layer-id → keywords used to pick the richest matching panel_prompt excerpt.
LAYER_PROMPT_ANCHORS: dict[str, tuple[str, ...]] = {
    "hangar_pre_dawn": (
        "hangar bay",
        "empty hangar",
        "hangar",
        "cathedral-scale industrial",
        "pre-dawn",
    ),
    "cockpit_interior": (
        "cockpit interior",
        "empty cockpit",
        "cockpit seat",
        "instrument panel",
    ),
    "seated_cockpit": (
        "seated pilot",
        "single pilot",
        "pure white backdrop",
    ),
    "threshold_stand": (
        "standing pilot",
        "single pilot",
        "pure white backdrop",
    ),
    "glove_pad": (
        "oatmeal-colored hand-knit glove pad",
        "oatmeal glove pad",
        "knit glove",
    ),
    "telemetry_panel": (
        "telemetry",
        "isolated telemetry",
        "subsystem latency",
    ),
    "office_after_hours": (
        "office after hours",
        "dual monitors",
        "empty chairs",
        "after hours",
        "fluorescent",
    ),
    "archive_corridor": (
        "archive corridor",
        "file labels",
        "corridor",
        "filing",
    ),
    "at_desk_tense": (
        "at a desk",
        "shoulders high",
        "laptop",
        "tired eyes",
    ),
    "reading_shoulders": (
        "shoulders",
        "colleague",
        "reads",
    ),
    "clicking_pen": (
        "pen",
        "clicked",
    ),
    "risk_model_printout": (
        "print",
        "risk model",
        "prediction",
    ),
}

# Explicit scene anchors injected even when panel_prompts miss — prevent abstract collapse.
SCENE_CONTENT_ANCHORS: dict[str, str] = {
    "hangar_pre_dawn": (
        "Wide establishing shot of Hangar Bay 3 at 04:12 before dawn, cathedral-scale "
        "industrial hangar interior with visible steel catwalks, gantry cranes, floor "
        "markings, docking clamps, and EMPTY repair gantries with no robot parked in frame; "
        "overhead floods OFF; only standby work-lights cast long hard shadows across the floor; "
        "cool pre-dawn slate-blue ambient fill; NO characters and NO mecha subject in frame; clear "
        "architectural perspective vanishing lines, readable hangar architecture, manga panel"
    ),
    "cockpit_interior": (
        "Empty mecha cockpit interior support plate: sealed canopy, empty flight harness "
        "straps, dual control yokes/joysticks, amber HUD glass reflecting a single warm "
        "cockpit-amber filament lamp, slate-grey instrument panels with brass meridian-line inlays, "
        "readable switches and telemetry strip LEDs, tight interior perspective, "
        "NO pilot, NO person, NO glove prop, NO foreground character; seinen mecha manga cockpit"
    ),
    "seated_cockpit": (
        "Single pilot seated pose cutout, charcoal flightsuit, short black hair pinned at nape, "
        "jaw set, hands held as if near controls, oatmeal glove pad on left palm, pure white "
        "backdrop alpha cutout plate, NO chair, NO cockpit, NO console, NO background"
    ),
    "threshold_stand": (
        "Single pilot standing full-body cutout, charcoal flightsuit, oatmeal glove pad visible, "
        "tense shoulders, pure white backdrop alpha cutout plate, NO cockpit threshold, "
        "NO machine, NO hangar, NO environment"
    ),
    "glove_pad": (
        "Hand-knit oatmeal cream glove pad alone, soft yarn texture visible, rendered LARGE "
        "centered on pure white backdrop, product-plate clarity"
    ),
    "telemetry_panel": (
        "Isolated telemetry strip object with amber LED indicators and dark slate bezel, "
        "readable hardware detail, LARGE centered on pure white backdrop, NO cockpit scene"
    ),
    "office_after_hours": (
        "Dim corporate office after hours: dual glowing monitors, empty swivel chairs, "
        "fluorescent ceiling panels half-off, cool blue shadows, cubicle desks, "
        "readable room geometry, psychological thriller manga establishing plate"
    ),
    "archive_corridor": (
        "Long archive corridor lined with labeled filing cabinets, cool fluorescent "
        "perspective corridor vanishing point, psychological thriller manga"
    ),
}

SERIES = {
    "mecha": {
        "series_id": "warrior_calm_cultivation__master_wu__en_US__burnout__the_chassis_is_listening",
        "panel_prompts_series_id": (
            "warrior_calm_cultivation__master_wu__en_US__burnout__the_chassis_is_listening"
        ),
        "genre_id": "mecha",
        "market_demo": "seinen",
        "visual_grammar": "kinetic_action",
        "genre_style": (
            "seinen mecha manga, Patlabor / 86 / Bokurano tonal reference (NOT Gundam-action), "
            "matte slate chassis, amber telemetry glow, brass meridian-line tracery, "
            "pen-and-ink linework, clear readable forms, hard edges, architectural perspective"
        ),
        "negative": (
            "text, watermark, chibi, comedy, bright saturated colors, abstract noise, "
            "formless blob, pure gradient, empty soft field, no objects, gaussian blur mess, "
            "Gundam-style action pose, plastic gloss"
        ),
    },
    "thriller": {
        "series_id": "cognitive_clarity__en_US__psychological_thriller__series01",
        "panel_prompts_series_id": (
            "cognitive_clarity__ahjan__en_US__overthinking__the_loop_is_not_thinking"
        ),
        "genre_id": "psychological_thriller",
        "market_demo": "seinen",
        "visual_grammar": "dread_contrast",
        "genre_style": (
            "psychological thriller manga register, fluorescent constriction, paranoia, "
            "cool shadows, false relief discipline, pen-and-ink linework, readable interior geometry"
        ),
        "negative": (
            "text, watermark, comedy, warm cozy lighting, chibi, abstract noise, "
            "formless blob, pure gradient, empty soft field"
        ),
    },
}


@dataclass(frozen=True)
class LayerJob:
    layer_id: str
    layer_class: str
    out_path: Path
    prompt: str
    negative: str
    width: int
    height: int


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _merge_negative(*parts: str) -> str:
    seen: set[str] = set()
    out: list[str] = []
    for part in parts:
        for chunk in str(part or "").split(","):
            text = chunk.strip()
            if not text:
                continue
            key = text.lower()
            if key in seen:
                continue
            seen.add(key)
            out.append(text)
    return ", ".join(out)


def _load_panel_prompt_texts(series_key: str) -> list[str]:
    cfg = SERIES[series_key]
    sid = cfg.get("panel_prompts_series_id") or cfg["series_id"]
    path = PANEL_PROMPTS / sid / "ep_001.panel_prompts.json"
    if not path.is_file():
        return []
    doc = json.loads(path.read_text(encoding="utf-8"))
    panels = doc.get("panels") or doc.get("prompts") or []
    texts: list[str] = []
    for panel in panels:
        if not isinstance(panel, dict):
            continue
        prompt = str(panel.get("prompt") or "").strip()
        if prompt:
            texts.append(prompt)
        notes = panel.get("composition_notes") or {}
        if isinstance(notes, dict):
            excerpt = str(notes.get("scene_excerpt") or "").strip()
            if excerpt:
                texts.append(excerpt)
    return texts


def _best_panel_excerpt(layer_id: str, panel_texts: list[str], *, max_chars: int = 900) -> str:
    anchors = LAYER_PROMPT_ANCHORS.get(layer_id) or (layer_id.replace("_", " "),)
    best = ""
    best_score = -1
    for text in panel_texts:
        low = text.lower()
        score = sum(1 for a in anchors if a.lower() in low)
        if score > best_score or (score == best_score and len(text) > len(best)):
            best_score = score
            best = text
    if best_score <= 0:
        return ""
    # Prefer the concrete scene sentence: drop the long character-bible tail if present.
    cut = re.split(r",\s*consistent character:", best, maxsplit=1)[0]
    cut = cut.strip().rstrip(",")
    if len(cut) > max_chars:
        cut = cut[: max_chars - 1].rsplit(" ", 1)[0] + "…"
    return cut


def _compose_prompt(
    *,
    layer_id: str,
    layer_class: str,
    contract_description: str,
    style: str,
    panel_texts: list[str],
) -> str:
    parts: list[str] = []
    anchor = SCENE_CONTENT_ANCHORS.get(layer_id, "").strip()
    if anchor:
        parts.append(anchor)
    excerpt = "" if layer_id in MECHA_CLEAN_LAYER_IDS else _best_panel_excerpt(layer_id, panel_texts)
    if excerpt and excerpt.lower() not in (anchor.lower() if anchor else ""):
        parts.append(excerpt)
    # Contract description is a last-resort crumb — never the sole content.
    desc = "" if layer_id in MECHA_CLEAN_LAYER_IDS else (contract_description or "").strip()
    if desc and all(desc.lower() not in p.lower() for p in parts):
        parts.append(desc)
    if layer_class == "L0":
        parts.append(
            "STRUCTURAL L0 contract: empty environment/support plate only, "
            "no pilot, no person, no character, no foreground subject, no hero mecha subject, "
            "support surfaces clearly visible for later compositing"
        )
        parts.append("full-bleed scene plate filling frame, no letterboxing")
    elif layer_class == "L2":
        parts.append(
            "STRUCTURAL L2 contract: exactly one alpha-separable subject cutout, "
            "pilot OR mecha only, pure white backdrop, no cockpit, no hangar, "
            "no environment, no console, no background objects, clean silhouette readable"
        )
    elif layer_class == "L3":
        parts.append(
            "STRUCTURAL L3 contract: one isolated object or telemetry prop only, "
            "large centered pure white backdrop, no people, no pilot, no environment"
        )
    parts.append(style)
    prompt = ", ".join(p for p in parts if p)
    if len(prompt) < 180:
        raise ValueError(
            f"prompt under-specified for {layer_id} ({len(prompt)} chars) — "
            "refusing to enqueue thin bank-contract crumbs that collapse to blobs"
        )
    return prompt


def build_jobs(
    series_key: str,
    *,
    task: str = "t2i_qwen_image",
    layer_ids: set[str] | None = None,
) -> list[LayerJob]:
    cfg = SERIES[series_key]
    series_id = cfg["series_id"]
    root = MANGA / series_id
    contracts = root / "bank_contracts"
    style, authority_negative, _ = build_authority_prompt_block(
        genre_id=str(cfg.get("genre_id") or ""),
        task=task,
        market_demo=str(cfg.get("market_demo") or ""),
        visual_grammar=str(cfg.get("visual_grammar") or ""),
        extra_style=str(cfg.get("genre_style") or ""),
    )
    negative = _merge_negative(authority_negative, str(cfg["negative"]))
    panel_texts = _load_panel_prompt_texts(series_key)
    jobs: list[LayerJob] = []

    scene_doc = _load_yaml(contracts / "scene_inventory.yaml")
    for scene in scene_doc.get("scenes") or []:
        sid = scene["scene_id"]
        if layer_ids is not None and sid not in layer_ids:
            continue
        w, h = scene.get("render_resolution") or [1080, 1920]
        jobs.append(
            LayerJob(
                layer_id=sid,
                layer_class="L0",
                out_path=root / "image_bank" / "L0" / f"{sid}.png",
                prompt=_compose_prompt(
                    layer_id=sid,
                    layer_class="L0",
                    contract_description=str(scene.get("description") or ""),
                    style=style,
                    panel_texts=panel_texts,
                ),
                negative=negative + ", people, person, pilot, character, foreground subject, hero mecha subject",
                width=int(w),
                height=int(h),
            )
        )

    pose_doc = _load_yaml(contracts / "character_pose_inventory.yaml")
    for pose in pose_doc.get("poses") or []:
        pid = pose["pose_id"]
        if layer_ids is not None and pid not in layer_ids:
            continue
        w, h = pose.get("render_resolution") or [1080, 1920]
        jobs.append(
            LayerJob(
                layer_id=pid,
                layer_class="L2",
                out_path=root / "image_bank" / "L2" / f"{pid}.png",
                prompt=_compose_prompt(
                    layer_id=pid,
                    layer_class="L2",
                    contract_description=str(pose.get("description") or ""),
                    style=style,
                    panel_texts=panel_texts,
                ),
                negative=negative + (
                    ", busy background, cockpit interior, hangar, environment, room, "
                    "scenery, console background, multiple subjects, extra people"
                ),
                width=int(w),
                height=int(h),
            )
        )

    obj_doc = _load_yaml(contracts / "object_inventory.yaml")
    for obj in obj_doc.get("objects") or []:
        oid = obj["object_id"]
        if layer_ids is not None and oid not in layer_ids:
            continue
        w, h = obj.get("render_resolution") or [1080, 1920]
        jobs.append(
            LayerJob(
                layer_id=oid,
                layer_class="L3",
                out_path=root / "image_bank" / "L3" / f"{oid}.png",
                prompt=_compose_prompt(
                    layer_id=oid,
                    layer_class="L3",
                    contract_description=str(obj.get("description") or ""),
                    style=style,
                    panel_texts=panel_texts,
                ),
                negative=negative + ", people, person, hands, pilot, character, background, environment, scene",
                width=int(w),
                height=int(h),
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


def _existing_is_usable(path: Path) -> bool:
    """Skip only if local PNG exists, is large, AND passes blob gate."""
    if not path.is_file() or path.stat().st_size < MIN_REAL_BYTES:
        return False
    try:
        from scripts.manga.bank_layer_blob_gate import is_blob_png

        return not is_blob_png(path)
    except Exception as exc:  # pragma: no cover - defensive
        print(f"  WARN blob-gate unavailable for {path}: {exc}", file=sys.stderr)
        return False


def enqueue_jobs(
    jobs: list[LayerJob],
    *,
    campaign_id: str,
    series_key: str,
    series_id: str,
    task: str,
    ssh_host: str,
    dry_run: bool,
    skip_existing: bool,
) -> list[dict[str, Any]]:
    from scripts.manga.pearl_star_t2i_enqueue import enqueue_panel_job

    results: list[dict[str, Any]] = []
    specs = [
        build_request_spec(
            campaign_id=campaign_id,
            series_key=series_key,
            series_id=series_id,
            layer_id=job.layer_id,
            layer_class=job.layer_class,
            out_path=job.out_path,
            prompt=job.prompt,
            negative=job.negative,
            width=job.width,
            height=job.height,
            task=task,
        )
        for job in jobs
    ]
    doc, _ = upsert_requests(specs)
    status_map: dict[int, str] = {}
    try:
        prior_job_ids = [
            int(doc["requests"][spec["request_id"]]["latest_job_id"])
            for spec in specs
            if doc["requests"][spec["request_id"]].get("latest_job_id") is not None
        ]
        if prior_job_ids:
            status_map = fetch_queue_status_map(prior_job_ids, ssh_host=ssh_host)
    except Exception as exc:
        print(f"  WARN queue status reconcile failed: {exc}", file=sys.stderr)
    reconcile_requests(queue_status_map=status_map)
    allowed_ids = request_ids_needing_enqueue()

    for job in jobs:
        rel = job.out_path.relative_to(REPO)
        job.out_path.parent.mkdir(parents=True, exist_ok=True)
        request_id = f"{series_key}:{job.layer_class}:{job.layer_id}"
        if not dry_run and request_id not in allowed_ids and skip_existing:
            print(f"  SKIP {job.layer_id} (ledger says already usable/queued)", file=sys.stderr)
            continue
        if not dry_run and skip_existing and _existing_is_usable(job.out_path):
            print(f"  SKIP {job.layer_id} ({rel}, usable REAL)", file=sys.stderr)
            continue
        if dry_run:
            print(
                json.dumps(
                    {
                        "layer_id": job.layer_id,
                        "layer_class": job.layer_class,
                        "out_path": str(rel),
                        "task": task,
                        "prompt_chars": len(job.prompt),
                        "prompt_preview": job.prompt[:220],
                    }
                )
            )
            continue
        # Never leave a prior blob counted as REAL while the new job is in flight.
        if job.out_path.is_file():
            fail_dir = job.out_path.parent / "_BLOB_FAIL"
            fail_dir.mkdir(parents=True, exist_ok=True)
            quarantined = fail_dir / f"{job.out_path.stem}__pre_rerender{job.out_path.suffix}"
            job.out_path.replace(quarantined)
            print(f"  QUARANTINE {rel} -> {quarantined.relative_to(REPO)}", file=sys.stderr)
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
            "prompt_chars": len(job.prompt),
            "request_id": request_id,
        }
        results.append(row)
        record_enqueue(
            request_id,
            job_id=int(row["job_id"]),
            via=str(row["via"]),
            task=task,
        )
        print(f"  QUEUE {job.layer_id} job_id={row['job_id']} via={row['via']}", file=sys.stderr)
    return results


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--series", choices=["mecha", "thriller", "both"], default="both")
    ap.add_argument(
        "--layer-id",
        action="append",
        default=[],
        help="Limit to specific layer_id(s); repeatable (e.g. hangar_pre_dawn)",
    )
    ap.add_argument(
        "--task",
        default="t2i_qwen_image",
        choices=["t2i_flux_dev_h1a", "t2i_qwen_image", "t2i_flux_schnell"],
    )
    ap.add_argument("--ssh-host", default="")
    ap.add_argument("--no-preflight", action="store_true")
    args = ap.parse_args(argv)

    import os

    ssh_host = args.ssh_host or os.environ.get("PS_QUEUE_SSH_HOST", "pearl_star")
    keys = ["mecha", "thriller"] if args.series == "both" else [args.series]
    layer_ids = set(args.layer_id) if args.layer_id else None

    if not args.dry_run and not args.no_preflight:
        preflight_pscli(ssh_host)

    all_results: dict[str, list[dict[str, Any]]] = {}
    for key in keys:
        jobs = build_jobs(key, task=args.task, layer_ids=layer_ids)
        print(f"{key}: {len(jobs)} bank layers", file=sys.stderr)
        all_results[key] = enqueue_jobs(
            jobs,
            campaign_id="crossgenre_real_layers_wave1",
            series_key=key,
            series_id=SERIES[key]["series_id"],
            task=args.task,
            ssh_host=ssh_host,
            dry_run=args.dry_run,
            skip_existing=not args.force,
        )

    if not args.dry_run:
        print(json.dumps({"enqueued": all_results}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
