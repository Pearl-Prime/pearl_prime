#!/usr/bin/env python3
"""V5 / Qwen-Image-Layered feasibility test.

Standalone smoke test that:
  1. Submits qwen_image_layered_decompose.json to Pearl Star ComfyUI with a known
     manga-style prompt.
  2. Polls /history until the prompt finishes.
  3. Collects ALL output images (one per decomposed layer — Qwen-Image-Layered
     emits N=layers RGBA layers; default 2 = subject + background).
  4. Reports timing + VRAM used + per-layer file sizes.

Purpose: clear the V5 feasibility gate documented in
  artifacts/research/manga_layer_compositing_research_2026-05-20.md §9.2
  (RTX 5070 Ti 16 GB unknown vs. fp8mixed's 24 GB claim).

If this passes → Qwen-Image-Layered is operationally feasible on Pearl Star;
proceed to build the V5 episode orchestrator + integrate ep_001 once V4 PR #1239
merges. If it OOMs → fall back to fp8_e4m3fn UNETLoader weight_dtype, or escalate.

This is a Tier 1 (operator-present) smoke test. No batch scaling.

Usage:
    python3 scripts/manga/v5_qwen_layered_feasibility.py \\
        --output-dir artifacts/manga/v5_feasibility/

Environment:
    COMFYUI_URL  — defaults to http://192.168.1.112:8188 (Pearl Star)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]

WORKFLOW_PATH = (
    REPO_ROOT
    / "scripts/image_generation/comfyui_workflows/qwen_image_layered_decompose.json"
)
DEFAULT_COMFY_URL = os.environ.get("COMFYUI_URL", "http://192.168.1.112:8188")
POLL_INTERVAL_SEC = 5.0
POLL_TIMEOUT_SEC = 600.0  # 10 min — first run loads ~20 GB diffusion model into VRAM

# Smoke prompt: archetype-shaped panel prompt similar to V4 L0+L2 combined,
# but written as ONE coherent scene (which is the V5 architectural point —
# Qwen renders the whole panel together, then decomposes).
SMOKE_POSITIVE = (
    "A young Japanese woman with shoulder-length straight black hair, calm "
    "neutral expression, seated at a small wooden kitchen table at dawn. "
    "Soft warm golden light from a window on the left. White ceramic mug "
    "in front of her on the table. A small succulent in a clay pot on the "
    "windowsill behind. Painterly manga illustration, soft shading, "
    "iyashikei (healing genre) atmosphere, peaceful and slightly melancholy. "
    "Medium close-up framing, shoulders to head visible, subject centered "
    "with breathing room above. Clean line art, gentle wash."
)
SMOKE_NEGATIVE = (
    "lowres, blurry, distorted face, deformed hands, extra fingers, "
    "anatomical errors, asymmetric eyes, harsh shadow, photorealistic"
)


def _post_json(url: str, payload: dict) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _get_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _get_bytes(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=120) as resp:
        return resp.read()


def _gpu_status(comfy_url: str) -> dict[str, Any]:
    """Read /system_stats from ComfyUI; returns vram_total / vram_free in bytes."""
    try:
        stats = _get_json(f"{comfy_url}/system_stats")
    except Exception as e:
        return {"error": str(e)}
    devices = stats.get("devices") or []
    if not devices:
        return {"error": "no devices reported"}
    d = devices[0]
    return {
        "name": d.get("name", "?"),
        "vram_total_gb": round(d.get("vram_total", 0) / 1024**3, 2),
        "vram_free_gb": round(d.get("vram_free", 0) / 1024**3, 2),
        "torch_vram_total_gb": round(d.get("torch_vram_total", 0) / 1024**3, 2),
    }


def _build_workflow(template: dict, positive: str, negative: str, seed: int) -> dict:
    """Substitute {{positive_prompt}} / {{negative_prompt}} placeholders + seed.

    Mirrors scripts/image_generation/manga_teacher_batch.py:_build_workflow contract
    but inlined to keep the feasibility test self-contained (no V4-branch deps).
    """
    wf: dict = json.loads(json.dumps(template))  # deep copy
    for node_id, node in wf.items():
        if not isinstance(node, dict):
            continue
        inputs = node.get("inputs", {})
        if not isinstance(inputs, dict):
            continue
        for k, v in list(inputs.items()):
            if not isinstance(v, str):
                continue
            if "{{positive_prompt}}" in v:
                inputs[k] = v.replace("{{positive_prompt}}", positive)
            if "{{negative_prompt}}" in v:
                inputs[k] = v.replace("{{negative_prompt}}", negative)
        # Inject seed into KSampler
        if node.get("class_type") == "KSampler" and "seed" in inputs:
            inputs["seed"] = seed
    # ComfyUI /prompt rejects nodes without class_type; strip the _meta sidecar.
    wf = {k: v for k, v in wf.items() if k != "_meta"}
    return wf


def run_feasibility(comfy_url: str, output_dir: Path, seed: int) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)

    if not WORKFLOW_PATH.is_file():
        print(f"ERROR: workflow not at {WORKFLOW_PATH}", file=sys.stderr)
        return 1
    template = json.loads(WORKFLOW_PATH.read_text())

    print("=== V5 / Qwen-Image-Layered feasibility test ===")
    print(f"ComfyUI: {comfy_url}")
    print(f"Workflow: {WORKFLOW_PATH.relative_to(REPO_ROOT)}")
    print(f"Output: {output_dir}")
    print()
    print("--- GPU baseline (pre-submit) ---")
    print(json.dumps(_gpu_status(comfy_url), indent=2))

    wf = _build_workflow(template, SMOKE_POSITIVE, SMOKE_NEGATIVE, seed)

    print("\n--- Submitting workflow ---")
    t0 = time.time()
    try:
        submit_resp = _post_json(f"{comfy_url}/prompt", {"prompt": wf})
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"ERROR: submit returned HTTP {e.code}", file=sys.stderr)
        print(body, file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: submit failed: {e}", file=sys.stderr)
        return 1
    prompt_id = submit_resp.get("prompt_id")
    if not prompt_id:
        print(f"ERROR: no prompt_id in submit response: {submit_resp}", file=sys.stderr)
        return 1
    print(f"prompt_id = {prompt_id}")

    print("\n--- Polling /history (interval={:.0f}s, timeout={:.0f}s) ---".format(
        POLL_INTERVAL_SEC, POLL_TIMEOUT_SEC))
    deadline = time.time() + POLL_TIMEOUT_SEC
    while time.time() < deadline:
        time.sleep(POLL_INTERVAL_SEC)
        try:
            history = _get_json(f"{comfy_url}/history/{prompt_id}")
        except urllib.error.URLError:
            continue
        if prompt_id not in history:
            elapsed = time.time() - t0
            gpu = _gpu_status(comfy_url)
            print(f"  [{elapsed:6.1f}s] queued/running … "
                  f"vram_free={gpu.get('vram_free_gb', '?')} GB")
            continue
        outputs = history[prompt_id].get("outputs", {})
        elapsed = time.time() - t0
        print(f"\n--- Done in {elapsed:.1f}s ---")
        gpu_after = _gpu_status(comfy_url)
        print(f"GPU peak (post-render): {gpu_after}")

        # Collect ALL output images — V5 expects N layers, not 1
        all_images = []
        for node_id, node_outputs in outputs.items():
            images = node_outputs.get("images", []) or []
            for img in images:
                all_images.append((node_id, img))

        if not all_images:
            print("ERROR: prompt finished but no images in outputs", file=sys.stderr)
            print(json.dumps(outputs, indent=2)[:1000], file=sys.stderr)
            return 1

        print(f"\n--- Collected {len(all_images)} output image(s) ---")
        layer_paths = []
        for idx, (node_id, img) in enumerate(all_images):
            view_url = (
                f"{comfy_url}/view?filename={img['filename']}"
                f"&subfolder={img.get('subfolder', '')}&type={img.get('type', 'output')}"
            )
            try:
                png_bytes = _get_bytes(view_url)
            except Exception as e:
                print(f"  layer_{idx:02d}: download FAILED — {e}", file=sys.stderr)
                continue
            out = output_dir / f"feasibility_layer_{idx:02d}.png"
            out.write_bytes(png_bytes)
            layer_paths.append(out)
            print(f"  layer_{idx:02d} → {out.name} ({len(png_bytes):,} bytes, "
                  f"src_node={node_id}, src_name={img['filename']})")

        # Telemetry sidecar
        sidecar = output_dir / "feasibility_telemetry.json"
        telemetry = {
            "prompt_id": prompt_id,
            "elapsed_sec": round(elapsed, 1),
            "n_layers": len(layer_paths),
            "gpu_after": gpu_after,
            "workflow": str(WORKFLOW_PATH.relative_to(REPO_ROOT)),
            "positive_prompt": SMOKE_POSITIVE,
            "negative_prompt": SMOKE_NEGATIVE,
            "seed": seed,
            "layer_paths": [str(p.relative_to(REPO_ROOT)) for p in layer_paths],
        }
        sidecar.write_text(json.dumps(telemetry, indent=2))
        print(f"\nTelemetry: {sidecar.relative_to(REPO_ROOT)}")

        print("\n=== PASS ===")
        print(f"  Layers produced: {len(layer_paths)}")
        print(f"  Elapsed: {elapsed:.1f}s")
        print(f"  VRAM free post-render: {gpu_after.get('vram_free_gb', '?')} GB")
        return 0

    print(f"\nERROR: poll timeout after {POLL_TIMEOUT_SEC:.0f}s", file=sys.stderr)
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", default="artifacts/manga/v5_feasibility",
                    help="Where to save the layer PNGs + telemetry")
    ap.add_argument("--comfy-url", default=DEFAULT_COMFY_URL,
                    help=f"ComfyUI URL (default: {DEFAULT_COMFY_URL})")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    return run_feasibility(args.comfy_url, Path(args.output_dir).resolve(), args.seed)


if __name__ == "__main__":
    sys.exit(main())
