#!/usr/bin/env python3
"""One-panel mecha layered pilot using prompt-builder v3 + Qwen-primary dispatch.

Produces L0/L2/L3 + composite under artifacts/qa/manga_layered_visual_proof_*.
Tier 1 operator-present lane — ComfyUI on Pearl Star (RAP queue when worker live).
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import date
from pathlib import Path
from typing import Any

from PIL import Image

REPO = Path(__file__).resolve().parents[2]
SERIES = (
    "warrior_calm_cultivation__master_wu__en_US__burnout__the_chassis_is_listening"
)
DEFAULT_OUT = (
    REPO / "artifacts" / "qa" / f"manga_layered_visual_proof_{date.today().isoformat()}"
    / "mecha_master_wu_pilot"
)

LAYER_SPECS = (
    ("L0.png", "cockpit_interior", "L0"),
    ("L2.png", "seated_cockpit", "L2"),
    ("L3.png", "telemetry_panel", "L3"),
)


def _compose_layers(l0: Path, l2: Path, l3: Path, out: Path) -> None:
    """Minimal z-order composite: L0 → L3 → L2."""
    base = Image.open(l0).convert("RGBA")
    canvas = Image.new("RGBA", base.size, (255, 255, 255, 255))
    canvas.paste(base, (0, 0))
    for layer_path in (l3, l2):
        layer = Image.open(layer_path).convert("RGBA")
        layer = layer.resize(base.size, Image.Resampling.LANCZOS)
        canvas.alpha_composite(layer)
    canvas.convert("RGB").save(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--seed", type=int, default=4242)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--render-direct", action="store_true", help="ComfyUI Qwen render on Pearl Star")
    ap.add_argument("--comfy-url", default="")
    ap.add_argument("--ssh-host", default="")
    ap.add_argument("--no-enqueue", action="store_true")
    args = ap.parse_args(argv)

    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    from scripts.manga.enqueue_crossgenre_real_layers import (
        SCENE_CONTENT_ANCHORS,
        SERIES as ENQ_SERIES,
        build_jobs,
        enqueue_jobs,
        preflight_pscli,
    )
    from scripts.manga.prompt_authority import build_panel_prompt, resolve_panel_task

    mecha = ENQ_SERIES["mecha"]
    task = resolve_panel_task(None, genre_id="mecha")
    layer_ids = {"cockpit_interior", "seated_cockpit", "telemetry_panel"}

    layer_prompts: dict[str, tuple[str, str, dict[str, Any]]] = {}
    prompts_md: list[str] = ["# Mecha Master Wu Layered Pilot — prompt-builder v3", ""]
    metrics: dict[str, Any] = {"task": task, "seed": args.seed, "layers": {}}

    jobs = build_jobs("mecha", task=task, layer_ids=layer_ids)
    job_by_id = {j.layer_id: j for j in jobs}

    for dest_name, lid, layer_class in LAYER_SPECS:
        job = job_by_id[lid]
        anchor = SCENE_CONTENT_ANCHORS.get(lid, "")
        pos, neg, prov = build_panel_prompt(
            genre_id="mecha",
            subject=anchor,
            composition=f"{layer_class} bank layer, pure white backdrop where cutout",
            locale="en_US",
            market_demo=str(mecha.get("market_demo") or "seinen"),
            extra_style=str(mecha.get("genre_style") or ""),
            task=task,
        )
        layer_prompts[lid] = (pos, neg, prov)
        prompts_md.append(f"## {lid} ({layer_class})")
        prompts_md.append(f"**positive:** {pos}")
        prompts_md.append(f"**negative:** {neg}")
        prompts_md.append("")
        metrics["layers"][lid] = {
            "positive_chars": len(pos),
            "provenance": prov,
            "dest": dest_name,
        }

    (out_dir / "PROMPT.md").write_text("\n".join(prompts_md))

    if args.dry_run:
        print(json.dumps({"layers": list(layer_ids), "task": task}, indent=2))
        return 0

    if args.render_direct:
        from scripts.manga.bank_layer_blob_gate import assert_not_blob, judge_png
        from scripts.manga.comfyui_qwen_panel_render import render_qwen_panel_png

        comfy = args.comfy_url or __import__("os").environ.get(
            "COMFYUI_URL", "http://100.92.68.74:8188"
        )
        render_rows = []
        for dest_name, lid, _ in LAYER_SPECS:
            job = job_by_id[lid]
            pos, neg, _ = layer_prompts[lid]
            dest = out_dir / dest_name
            print(f"RENDER {lid} -> {dest.name} …", file=sys.stderr)
            row = render_qwen_panel_png(
                prompt=pos,
                negative=neg,
                width=job.width,
                height=job.height,
                seed=args.seed + hash(lid) % 1000,
                out_path=dest,
                comfy_url=comfy,
            )
            v = assert_not_blob(dest)
            row["blob_gate"] = v.to_dict()
            render_rows.append({"layer_id": lid, **row})
            print(f"  PASS blob_gate small_edge={v.metrics.small_edge:.2f}", file=sys.stderr)
        _compose_layers(
            out_dir / "L0.png",
            out_dir / "L2.png",
            out_dir / "L3.png",
            out_dir / "composite.png",
        )
        comp_v = judge_png(out_dir / "composite.png")
        metrics["render_direct"] = render_rows
        metrics["composite_blob_gate"] = comp_v.to_dict()
        (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
        print(f"assembled {out_dir / 'composite.png'}")
        return 0 if comp_v.ok else 4

    import os

    ssh_host = args.ssh_host or os.environ.get("PS_QUEUE_SSH_HOST", "pearl_star")
    if not args.no_enqueue:
        try:
            preflight_pscli(ssh_host)
        except RuntimeError as exc:
            print(f"BLOCKER preflight: {exc}", file=sys.stderr)
            return 2
        results = enqueue_jobs(
            jobs,
            campaign_id="manga_prompt_builder_v3_mecha_pilot",
            series_key="mecha",
            series_id=SERIES,
            task=task,
            ssh_host=ssh_host,
            dry_run=False,
            skip_existing=False,
        )
        metrics["enqueue"] = results
        (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
        print(json.dumps({"enqueued": results}, indent=2))
        return 0

    from scripts.manga.bank_layer_blob_gate import assert_not_blob
    from scripts.manga.mecha_clean_structural_layer import validate_mecha_layer_meta

    bank_root = REPO / "artifacts" / "manga" / SERIES / "image_bank"
    mapping = {
        "L0.png": (bank_root / "L0" / "cockpit_interior.png", "L0"),
        "L2.png": (bank_root / "L2" / "seated_cockpit.png", "L2"),
        "L3.png": (bank_root / "L3" / "telemetry_panel.png", "L3"),
    }
    gate_rows = []
    for dest, (src, layer_class) in mapping.items():
        if not src.is_file() or src.stat().st_size < 1000:
            print(f"BLOCKER missing bank layer {src}", file=sys.stderr)
            return 3
        sidecar = src.with_suffix(".composition.json")
        if not sidecar.is_file():
            print(f"BLOCKER missing reviewed mecha sidecar {sidecar}", file=sys.stderr)
            return 3
        try:
            validate_mecha_layer_meta(json.loads(sidecar.read_text()), layer_class=layer_class)
        except ValueError as exc:
            print(f"BLOCKER contaminated/uncertified mecha bank layer {src}: {exc}", file=sys.stderr)
            return 3
        v = assert_not_blob(src)
        gate_rows.append(v.to_dict())
        shutil.copy2(src, out_dir / dest)
    _compose_layers(
        out_dir / "L0.png",
        out_dir / "L2.png",
        out_dir / "L3.png",
        out_dir / "composite.png",
    )
    metrics["blob_gate"] = gate_rows
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
    print(f"assembled {out_dir / 'composite.png'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
