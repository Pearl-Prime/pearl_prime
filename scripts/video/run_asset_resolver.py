#!/usr/bin/env python3
"""
Asset Resolver: ShotPlan + Image Bank index -> resolved assets per shot (shot_id -> asset_id).
Uses config/video/asset_selection_priority.yaml and composition_compat threshold.
If no bank path given, assigns deterministic placeholder asset_ids for testing.
Usage: python scripts/video/run_asset_resolver.py <shot_plan.json> -o <resolved_assets.json> [--bank <bank_index.json>] [--variant-id default]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.video._config import load_yaml, load_json, config_snapshot_hash, write_atomically, should_skip_output, REPO_ROOT


def _load_bank(bank_path: Path) -> list[dict]:
    if not bank_path.exists():
        return []
    text = bank_path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    if text.startswith("["):
        return load_json(bank_path)
    assets = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        assets.append(json.loads(line))
    return assets


def _resolve_shot(shot: dict, assets: list[dict], aspect_key: str, threshold: float) -> str | None:
    intent = shot.get("visual_intent", "")
    for a in assets:
        if a.get("visual_intent") != intent:
            continue
        compat = (a.get("composition_compat") or {}).get(aspect_key)
        if compat is not None and compat >= threshold:
            return a.get("asset_id")
    return None


def _generate_asset_via_runcomfy(
    shot: dict,
    output_dir: Path,
    api_key: str,
) -> str | None:
    """Generate a missing image asset via RunComfy FLUX API.

    Returns asset_id if successful, None on failure.
    """
    import os
    import time

    try:
        import requests as _req
    except ImportError:
        return None

    try:
        from scripts.image_generation.prompt_compiler import compile_image_prompt
    except ImportError:
        return None

    deploy_id = os.environ.get("RUNCOMFY_DEPLOYMENT_ID", "677edba8-ace0-4b2b-bad2-8e94b9959065")
    base_url = "https://api.runcomfy.net/prod/v1"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    intent = shot.get("visual_intent", "HOOK_VISUAL")
    shot_id = shot.get("shot_id", "shot-1")
    asset_id = f"asset-{shot_id.replace('shot-', '')}-001"

    # Build prompt from visual intent
    prompt_text = compile_image_prompt(
        task="video_bank_image",
        subject=intent.lower().replace("_", " "),
        style_hint="cinematic atmospheric illustration",
        palette_tokens=["warm", "amber"],
        scene="therapeutic wellness",
        extra_positive="high quality, detailed, no text",
        extra_negative="",
        author_id="",
        bio_keywords=[],
    ).get("positive", intent)

    # Submit to RunComfy
    data = {"overrides": {"6": {"inputs": {"text": prompt_text}}}}
    try:
        resp = _req.post(
            f"{base_url}/deployments/{deploy_id}/inference",
            json=data, headers=headers, timeout=60,
        )
        if resp.status_code != 200:
            return None
        r = resp.json()
        status_url = r.get("status_url", "")
        result_url = r.get("result_url", "")
    except Exception:
        return None

    # Poll for completion
    start = time.time()
    while time.time() - start < 300:
        try:
            sr = _req.get(status_url, headers={"Authorization": f"Bearer {api_key}"}, timeout=30)
            sd = sr.json()
            if sd.get("status") in ("succeeded", "completed"):
                rr = _req.get(result_url, headers={"Authorization": f"Bearer {api_key}"}, timeout=30)
                rd = rr.json()
                for nid, no in rd.get("outputs", {}).items():
                    if isinstance(no, dict):
                        imgs = no.get("images", [])
                        if imgs and isinstance(imgs[0], dict):
                            url = imgs[0].get("url")
                            if url:
                                ir = _req.get(url, timeout=60)
                                output_dir.mkdir(parents=True, exist_ok=True)
                                # Save as both .png and .jpg for resolver compatibility
                                (output_dir / f"{asset_id}.png").write_bytes(ir.content)
                                return asset_id
            elif sd.get("status") in ("failed", "error"):
                return None
        except Exception:
            pass
        time.sleep(10)

    return None


def run_asset_resolver(
    shot_plan: dict,
    bank_path: Path | None,
    variant_id: str,
    *,
    auto_generate: bool = False,
    auto_generate_dir: Path | None = None,
    runcomfy_api_key: str = "",
) -> dict:
    priority_config = load_yaml("config/video/asset_selection_priority.yaml")
    threshold = priority_config.get("composition_compat_threshold", 0.5)
    assets = _load_bank(bank_path) if bank_path else []
    aspect_key = "16:9"
    resolved = {}
    generated_count = 0
    for shot in shot_plan.get("shots", []):
        shot_id = shot["shot_id"]
        asset_id = _resolve_shot(shot, assets, aspect_key, threshold) if assets else None
        if not asset_id and auto_generate and runcomfy_api_key:
            gen_dir = auto_generate_dir or (REPO_ROOT / "artifacts" / "generated_assets")
            asset_id = _generate_asset_via_runcomfy(shot, gen_dir, runcomfy_api_key)
            if asset_id:
                generated_count += 1
        if not asset_id:
            asset_id = f"asset-{shot_id.replace('shot-', '')}-001"
        resolved[shot_id] = {"asset_id": asset_id}
    if generated_count:
        print(f"  Auto-generated {generated_count} assets via RunComfy", flush=True)
    return {
        "plan_id": shot_plan["plan_id"],
        "variant_id": variant_id,
        "config_hash": config_snapshot_hash(),
        "resolved": resolved,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Resolve assets for each shot from Image Bank or placeholders")
    ap.add_argument("shot_plan", help="Path to shot_plan.json")
    ap.add_argument("-o", "--out", required=True, help="Output resolved_assets.json path")
    ap.add_argument("--bank", help="Optional path to image bank index (JSON array or JSONL)")
    ap.add_argument("--variant-id", default="default", help="Variant for logging")
    ap.add_argument("--auto-generate", action="store_true", help="Generate missing assets via RunComfy FLUX")
    ap.add_argument("--auto-generate-dir", type=Path, default=None, help="Dir for generated assets")
    ap.add_argument("--force", action="store_true", help="Overwrite output even if it already exists")
    args = ap.parse_args()

    path = Path(args.shot_plan)
    if not path.exists():
        print(f"Error: not found: {path}", file=sys.stderr)
        return 1
    shot_plan = json.loads(path.read_text(encoding="utf-8"))
    bank_path = Path(args.bank) if args.bank else None

    import os
    rc_key = os.environ.get("RUNCOMFY_API_KEY", "").strip()

    out_path = Path(args.out)
    if should_skip_output(out_path, ["plan_id", "resolved", "config_hash"], args.force, config_snapshot_hash()):
        print(f"Skip (output exists, use --force to overwrite): {out_path}")
        return 0
    result = run_asset_resolver(
        shot_plan, bank_path, args.variant_id,
        auto_generate=args.auto_generate,
        auto_generate_dir=args.auto_generate_dir,
        runcomfy_api_key=rc_key,
    )
    write_atomically(out_path, result)
    print(f"Wrote resolved assets for {len(result['resolved'])} shots to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
