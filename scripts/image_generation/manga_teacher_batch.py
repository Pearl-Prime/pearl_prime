#!/usr/bin/env python3
"""Manga teacher character art generator — batch RunComfy IP-Adapter + img2img.

Takes real teacher photos and converts them to manga-style character art using
two approaches (IP-Adapter face-preserving + standard img2img), then outputs
a comparison sheet.

Usage:
    # Dry run — show what would be submitted:
    python scripts/image_generation/manga_teacher_batch.py --dry-run

    # Run single teacher:
    python scripts/image_generation/manga_teacher_batch.py --teacher ahjan

    # Run all teachers with photos:
    python scripts/image_generation/manga_teacher_batch.py

    # Run only IP-Adapter approach:
    python scripts/image_generation/manga_teacher_batch.py --approach ip_adapter

    # Run only img2img approach:
    python scripts/image_generation/manga_teacher_batch.py --approach img2img

    # Custom seeds for variation:
    python scripts/image_generation/manga_teacher_batch.py --seeds 42,123,456,789

Requires:
    RUNCOMFY_API_KEY env var (or macOS Keychain: phoenix-omega / RUNCOMFY_API_KEY)
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required — pip install pyyaml", file=sys.stderr)
    sys.exit(1)

from scripts.image_generation.runcomfy_batch import (
    submit_workflow,
    poll_run,
    extract_image_url,
    download_image,
    load_workflow,
)

# ── Paths ──
PROMPTS_PATH = REPO_ROOT / "config" / "manga" / "teacher_character_prompts.yaml"
PHOTOS_DIR = REPO_ROOT / "assets" / "manga" / "teacher_reference_photos"
OUTPUT_DIR = REPO_ROOT / "artifacts" / "manga" / "teacher_character_art"
WORKFLOW_IP_ADAPTER = REPO_ROOT / "scripts" / "image_generation" / "comfyui_workflows" / "flux_ip_adapter_manga.json"
WORKFLOW_IMG2IMG = REPO_ROOT / "scripts" / "image_generation" / "comfyui_workflows" / "flux_img2img_manga.json"

# ── RunComfy API ──
RUNCOMFY_API_BASE = "https://api.runcomfy.net/prod/v1"
# IP-Adapter requires a deployment with IP-Adapter nodes installed.
# Set via env or default to the standard FLUX deployment (may need updating).
DEFAULT_DEPLOYMENT_IP_ADAPTER = os.environ.get(
    "RUNCOMFY_IPADAPTER_DEPLOYMENT_ID",
    "677edba8-ace0-4b2b-bad2-8e94b9959065",
)
DEFAULT_DEPLOYMENT_IMG2IMG = os.environ.get(
    "RUNCOMFY_IMG2IMG_DEPLOYMENT_ID",
    "677edba8-ace0-4b2b-bad2-8e94b9959065",
)


def _get_api_key() -> str:
    """Load RunComfy API key from env or macOS Keychain."""
    key = os.environ.get("RUNCOMFY_API_KEY", "").strip()
    if key:
        return key
    # Try macOS Keychain
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-s", "phoenix-omega", "-a", "RUNCOMFY_API_KEY", "-w"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    print("ERROR: RUNCOMFY_API_KEY not found in env or Keychain.", file=sys.stderr)
    sys.exit(1)


def _load_prompts() -> dict[str, Any]:
    """Load teacher character prompts config."""
    with PROMPTS_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _find_photo(teacher_id: str) -> Path | None:
    """Find a reference photo for a teacher. Checks common extensions."""
    for ext in ("jpg", "jpeg", "png", "webp"):
        path = PHOTOS_DIR / f"{teacher_id}.{ext}"
        if path.is_file():
            return path
    return None


def _image_to_base64(path: Path) -> str:
    """Read image file and return base64 string."""
    return base64.b64encode(path.read_bytes()).decode("ascii")


def _build_workflow(
    workflow_template: dict[str, Any],
    *,
    positive_prompt: str,
    negative_prompt: str,
    input_image_b64: str | None = None,
    seed: int = 42,
) -> dict[str, Any]:
    """Build a workflow with prompt and image substitutions."""
    workflow = json.loads(json.dumps(workflow_template))  # deep copy

    # Find and replace prompt placeholders
    for node_id, node in workflow.items():
        if node_id == "_meta":
            continue
        inputs = node.get("inputs", {})

        # Replace text prompts
        if isinstance(inputs.get("text"), str):
            if "{{positive_prompt}}" in inputs["text"]:
                inputs["text"] = positive_prompt
            elif "{{negative_prompt}}" in inputs["text"]:
                inputs["text"] = inputs["text"].replace("{{negative_prompt}}", negative_prompt)

        # Replace input image
        if isinstance(inputs.get("image"), str) and "{{input_image}}" in inputs["image"]:
            if input_image_b64:
                inputs["image"] = input_image_b64

        # Replace seed
        if "seed" in inputs:
            inputs["seed"] = seed
        if "noise_seed" in inputs:
            inputs["noise_seed"] = seed

    return workflow


def _run_single(
    *,
    api_key: str,
    teacher_id: str,
    approach: str,
    positive_prompt: str,
    negative_prompt: str,
    photo_path: Path,
    seed: int,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Run a single generation job. Returns result dict."""
    # Select workflow and deployment
    if approach == "ip_adapter":
        workflow_path = WORKFLOW_IP_ADAPTER
        deployment_id = DEFAULT_DEPLOYMENT_IP_ADAPTER
    else:
        workflow_path = WORKFLOW_IMG2IMG
        deployment_id = DEFAULT_DEPLOYMENT_IMG2IMG

    # Load workflow template
    workflow_template = load_workflow(workflow_path)

    # Build workflow with substitutions
    image_b64 = _image_to_base64(photo_path)
    workflow = _build_workflow(
        workflow_template,
        positive_prompt=positive_prompt,
        negative_prompt=negative_prompt,
        input_image_b64=image_b64,
        seed=seed,
    )

    # Output path
    output_subdir = OUTPUT_DIR / teacher_id / approach
    output_subdir.mkdir(parents=True, exist_ok=True)
    output_file = output_subdir / f"seed_{seed}.png"

    result = {
        "teacher_id": teacher_id,
        "approach": approach,
        "seed": seed,
        "photo": str(photo_path),
        "output": str(output_file),
        "status": "pending",
    }

    if dry_run:
        print(f"  [DRY RUN] {teacher_id} / {approach} / seed={seed}")
        print(f"    Photo: {photo_path}")
        print(f"    Output: {output_file}")
        print(f"    Prompt: {positive_prompt[:80]}...")
        result["status"] = "dry_run"
        return result

    # Submit to RunComfy
    print(f"  Submitting {teacher_id} / {approach} / seed={seed}...")
    try:
        run_id = submit_workflow(api_key, deployment_id, workflow)
        print(f"    Run ID: {run_id}")

        # Poll for completion
        completed = poll_run(api_key, deployment_id, run_id, max_wait=600.0)
        image_url = extract_image_url(completed)

        if image_url:
            download_image(image_url, output_file)
            print(f"    Downloaded: {output_file}")
            result["status"] = "completed"
            result["image_url"] = image_url
        else:
            print(f"    WARNING: No image URL in result for {teacher_id}/{approach}")
            result["status"] = "no_image"
            result["raw_result"] = completed

    except Exception as e:
        print(f"    ERROR: {e}")
        result["status"] = "error"
        result["error"] = str(e)

    return result


def run_batch(
    *,
    teachers: list[str] | None = None,
    approaches: list[str] | None = None,
    seeds: list[int] | None = None,
    dry_run: bool = False,
) -> list[dict[str, Any]]:
    """Run the full batch for specified teachers and approaches."""
    if approaches is None:
        approaches = ["ip_adapter", "img2img"]
    if seeds is None:
        seeds = [42, 123, 456]  # 3 variations per approach

    api_key = _get_api_key()
    config = _load_prompts()
    shared_prefix = config.get("shared_prefix", "")
    shared_negative = config.get("shared_negative", "")
    teacher_configs = config.get("teachers", {})

    # Filter to requested teachers or all with photos
    if teachers:
        teacher_ids = [t for t in teachers if t in teacher_configs]
    else:
        teacher_ids = list(teacher_configs.keys())

    results: list[dict[str, Any]] = []
    total_jobs = 0
    skipped = 0

    print(f"\n{'='*60}")
    print(f"MANGA TEACHER CHARACTER ART BATCH")
    print(f"{'='*60}")
    print(f"Teachers:   {len(teacher_ids)}")
    print(f"Approaches: {approaches}")
    print(f"Seeds:      {seeds}")
    print(f"Total jobs: {len(teacher_ids) * len(approaches) * len(seeds)}")
    print(f"Dry run:    {dry_run}")
    print(f"{'='*60}\n")

    for teacher_id in teacher_ids:
        tc = teacher_configs[teacher_id]
        photo = _find_photo(teacher_id)

        if photo is None:
            print(f"[SKIP] {teacher_id} — no photo found in {PHOTOS_DIR}/")
            skipped += 1
            continue

        print(f"\n[{teacher_id}] ({tc.get('display_name', teacher_id)})")
        print(f"  Photo: {photo}")
        print(f"  Style: {tc.get('style_archetype', 'unknown')}")

        # Build full prompts
        positive = f"{shared_prefix}, {tc['positive']}"
        negative = f"{tc['negative']}, {shared_negative}"

        for approach in approaches:
            for seed in seeds:
                result = _run_single(
                    api_key=api_key,
                    teacher_id=teacher_id,
                    approach=approach,
                    positive_prompt=positive,
                    negative_prompt=negative,
                    photo_path=photo,
                    seed=seed,
                    dry_run=dry_run,
                )
                results.append(result)
                total_jobs += 1

                # Small delay between submissions to avoid rate limiting
                if not dry_run and result["status"] != "error":
                    time.sleep(2)

    # Write results manifest
    manifest_path = OUTPUT_DIR / "batch_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"BATCH COMPLETE")
    print(f"{'='*60}")
    print(f"Total jobs:    {total_jobs}")
    print(f"Skipped:       {skipped} (no photo)")
    print(f"Completed:     {sum(1 for r in results if r['status'] == 'completed')}")
    print(f"Errors:        {sum(1 for r in results if r['status'] == 'error')}")
    print(f"Manifest:      {manifest_path}")
    print(f"Output dir:    {OUTPUT_DIR}/")
    print()

    return results


def generate_comparison_html(results: list[dict[str, Any]]) -> Path:
    """Generate an HTML comparison sheet from batch results."""
    config = _load_prompts()
    teacher_configs = config.get("teachers", {})

    # Group results by teacher
    by_teacher: dict[str, list[dict[str, Any]]] = {}
    for r in results:
        tid = r["teacher_id"]
        if tid not in by_teacher:
            by_teacher[tid] = []
        by_teacher[tid].append(r)

    html_parts = [
        "<!DOCTYPE html>",
        "<html><head>",
        "<meta charset='utf-8'>",
        "<title>Manga Teacher Character Art — Comparison</title>",
        "<style>",
        "  body { font-family: -apple-system, sans-serif; background: #1a1a2e; color: #eee; padding: 2rem; }",
        "  h1 { text-align: center; color: #e94560; }",
        "  .teacher { margin: 2rem 0; padding: 1.5rem; background: #16213e; border-radius: 12px; }",
        "  .teacher h2 { color: #0f3460; background: #e94560; display: inline-block; padding: 0.3rem 1rem; border-radius: 6px; }",
        "  .teacher-meta { color: #888; margin: 0.5rem 0 1rem; }",
        "  .grid { display: flex; flex-wrap: wrap; gap: 1rem; }",
        "  .card { background: #0f3460; border-radius: 8px; padding: 0.8rem; text-align: center; width: 220px; }",
        "  .card img { width: 200px; height: 267px; object-fit: cover; border-radius: 6px; }",
        "  .card .label { font-size: 0.8rem; color: #aaa; margin-top: 0.4rem; }",
        "  .card .approach { font-weight: bold; color: #e94560; }",
        "  .ref-photo { border: 3px solid #e94560; }",
        "  .pick-btn { margin-top: 0.5rem; padding: 0.3rem 0.8rem; background: #e94560; color: white; border: none; border-radius: 4px; cursor: pointer; }",
        "  .pick-btn:hover { background: #c73e50; }",
        "</style>",
        "</head><body>",
        "<h1>Manga Teacher Character Art — Side-by-Side Comparison</h1>",
        f"<p style='text-align:center;color:#888'>Generated {time.strftime('%Y-%m-%d %H:%M')} — {len(results)} images across {len(by_teacher)} teachers</p>",
    ]

    for teacher_id in teacher_configs:
        if teacher_id not in by_teacher:
            continue
        tc = teacher_configs[teacher_id]
        teacher_results = by_teacher[teacher_id]

        photo = _find_photo(teacher_id)
        photo_rel = f"../../assets/manga/teacher_reference_photos/{photo.name}" if photo else ""

        html_parts.append(f"<div class='teacher'>")
        html_parts.append(f"  <h2>{tc.get('display_name', teacher_id)}</h2>")
        html_parts.append(f"  <div class='teacher-meta'>Style: {tc.get('style_archetype', '?')} | "
                          f"IP weight: {tc.get('ip_adapter_weight', '?')} | "
                          f"Denoise: {tc.get('img2img_denoise', '?')}</div>")
        html_parts.append(f"  <div class='grid'>")

        # Reference photo
        if photo:
            html_parts.append(f"    <div class='card'>")
            html_parts.append(f"      <img src='{photo_rel}' class='ref-photo' alt='Reference photo'>")
            html_parts.append(f"      <div class='label'>REFERENCE PHOTO</div>")
            html_parts.append(f"    </div>")

        # Generated images
        for r in sorted(teacher_results, key=lambda x: (x["approach"], x["seed"])):
            if r["status"] not in ("completed", "dry_run"):
                continue
            img_path = Path(r["output"])
            img_rel = f"{teacher_id}/{r['approach']}/seed_{r['seed']}.png"
            approach_label = "IP-Adapter" if r["approach"] == "ip_adapter" else "img2img"
            html_parts.append(f"    <div class='card'>")
            html_parts.append(f"      <img src='{img_rel}' alt='{teacher_id} {approach_label}'>")
            html_parts.append(f"      <div class='approach'>{approach_label}</div>")
            html_parts.append(f"      <div class='label'>seed: {r['seed']}</div>")
            html_parts.append(f"      <button class='pick-btn' onclick=\"this.textContent='PICKED'\">Pick this</button>")
            html_parts.append(f"    </div>")

        html_parts.append(f"  </div>")
        html_parts.append(f"</div>")

    html_parts.extend(["</body></html>"])

    output_path = OUTPUT_DIR / "comparison.html"
    output_path.write_text("\n".join(html_parts), encoding="utf-8")
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate manga character art for Phoenix Omega teachers")
    parser.add_argument("--teacher", type=str, help="Single teacher ID to process")
    parser.add_argument("--approach", type=str, choices=["ip_adapter", "img2img", "both"], default="both",
                        help="Which approach to run (default: both)")
    parser.add_argument("--seeds", type=str, default="42,123,456",
                        help="Comma-separated seeds for variations (default: 42,123,456)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be submitted without running")
    parser.add_argument("--no-comparison", action="store_true", help="Skip generating comparison HTML")
    args = parser.parse_args()

    teachers = [args.teacher] if args.teacher else None
    approaches = ["ip_adapter", "img2img"] if args.approach == "both" else [args.approach]
    seeds = [int(s.strip()) for s in args.seeds.split(",")]

    results = run_batch(
        teachers=teachers,
        approaches=approaches,
        seeds=seeds,
        dry_run=args.dry_run,
    )

    if not args.no_comparison and results:
        comparison_path = generate_comparison_html(results)
        print(f"Comparison sheet: {comparison_path}")
        print(f"Open: file://{comparison_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
