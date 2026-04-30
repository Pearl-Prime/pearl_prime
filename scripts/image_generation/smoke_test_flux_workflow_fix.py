#!/usr/bin/env python3
"""Smoke test for the FLUX workflow schnell→dev fix (PR #807).

Renders 4 genre prompts against BOTH the old (schnell) and new (flux1-dev)
KSampler configs, then writes a side-by-side comparison artifact at
artifacts/qa/flux_workflow_fix_smoke_<date>.md.

Genres covered (per master execution brief P0.3 acceptance criteria):
  - mecha            (failure genre — chronic drift)
  - dark_fantasy     (failure genre — chronic drift)
  - fantasy_adventure (failure genre — chronic drift)
  - healing          (control — should be stable in both configs)

Usage:
  # Dry run — print plan + cost estimate, render nothing:
  python3 scripts/image_generation/smoke_test_flux_workflow_fix.py --dry-run

  # Real render (requires RUNCOMFY_API_KEY in env or Keychain):
  python3 scripts/image_generation/smoke_test_flux_workflow_fix.py --run

  # Render only one config (for partial validation):
  python3 scripts/image_generation/smoke_test_flux_workflow_fix.py --run --config new
  python3 scripts/image_generation/smoke_test_flux_workflow_fix.py --run --config old

Outputs:
  artifacts/qa/flux_workflow_fix_smoke_<date>/
    mecha_old.png mecha_new.png
    dark_fantasy_old.png dark_fantasy_new.png
    fantasy_adventure_old.png fantasy_adventure_new.png
    healing_old.png healing_new.png
  artifacts/qa/flux_workflow_fix_smoke_<date>.md  (side-by-side artifact)

Cost: ~$0.03/image × 4 genres × 2 configs = ~$0.24 per full run.

Limitations (read before running):
  1. Without cookbook prompts (PR #802) merged, prompts are ad-hoc placeholders.
     A future re-run after #802 lands will use the cookbook's per-genre prompts.
  2. The submit_workflow function POSTs the full workflow JSON, which means
     local edits to the template DO take effect — but the deployment's
     installed checkpoint set must include both flux1-schnell-fp8 AND
     flux1-dev-fp8 for the side-by-side to work. If only one is installed,
     run with --config new (or old) and skip the comparison.
  3. Drift is qualitative; this artifact captures *images*, not pass/fail
     scores. Operator visual sign-off is the gate.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))


# Placeholder prompts — replace with cookbook prompts once PR #802 lands.
# These are intentionally generic-but-failure-prone for the 3 drift genres,
# and a stable healing scene for the control.
PROMPTS = {
    "mecha": (
        "manga cover, mecha pilot in cockpit, holographic readouts, kinetic motion, "
        "screentone shading, dynamic perspective, dramatic lighting, ink line consistency, "
        "professional manga art, 1024x1024"
    ),
    "dark_fantasy": (
        "manga cover, dark fantasy warrior in moonlit ruins, swirling mist, gothic detail, "
        "high contrast ink, atmospheric shadow, screentone gradient, dramatic composition, "
        "professional manga art, 1024x1024"
    ),
    "fantasy_adventure": (
        "manga cover, young hero on cliff edge facing ancient dragon, sweeping landscape, "
        "dynamic ink line, vivid screentone, hopeful expression, adventure tone, "
        "professional manga art, 1024x1024"
    ),
    "healing": (  # control — should render cleanly in both old and new configs
        "manga cover, gentle healer in forest clearing, dappled sunlight, soft watercolor wash, "
        "warm palette, contemplative expression, ink line consistency, slice-of-life tone, "
        "professional manga art, 1024x1024"
    ),
}

NEGATIVE_PROMPT = (
    "low quality, blurry, distorted anatomy, extra limbs, watermark, signature, "
    "text overlay, photorealistic, 3d render, western comic style"
)

OLD_CONFIG = {
    "ckpt_name": "flux1-schnell-fp8.safetensors",
    "steps": 24,
    "cfg": 4.0,
    "sampler_name": "euler",
    "scheduler": "normal",
}

NEW_CONFIG = {
    "ckpt_name": "flux1-dev-fp8.safetensors",
    "steps": 28,
    "cfg": 3.5,
    "sampler_name": "dpmpp_2m",
    "scheduler": "karras",
}


def build_workflow(positive: str, negative: str, cfg: dict) -> dict:
    """Build a minimal txt2img workflow with the given KSampler config."""
    return {
        "_meta": {"name": "flux_workflow_fix_smoke_test", "version": "1.0.0"},
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": cfg["ckpt_name"]},
        },
        "2": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": positive, "clip": ["1", 1]},
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": negative, "clip": ["1", 1]},
        },
        "4": {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": 1024, "height": 1024, "batch_size": 1},
        },
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "seed": 42,
                "steps": cfg["steps"],
                "cfg": cfg["cfg"],
                "sampler_name": cfg["sampler_name"],
                "scheduler": cfg["scheduler"],
                "denoise": 1.0,
                "model": ["1", 0],
                "positive": ["2", 0],
                "negative": ["3", 0],
                "latent_image": ["4", 0],
            },
        },
        "6": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["5", 0], "vae": ["1", 2]},
        },
        "7": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": "smoke_flux_fix", "images": ["6", 0]},
        },
    }


def render_one(api_key: str, deployment_id: str, workflow: dict, label: str) -> dict:
    """Submit one workflow + return a result dict."""
    from scripts.image_generation.runcomfy_batch import (
        submit_workflow,
        poll_run,
        extract_image_url,
        download_image,
    )
    print(f"[{label}] submitting…", flush=True)
    run_id = submit_workflow(api_key, deployment_id, workflow)
    print(f"[{label}] run_id={run_id}; polling…", flush=True)
    result = poll_run(api_key, deployment_id, run_id, timeout=300)
    image_url = extract_image_url(result)
    return {"label": label, "run_id": run_id, "image_url": image_url, "raw": result}


def write_artifact(out_dir: Path, results: list[dict], dry_run: bool) -> Path:
    """Write the side-by-side comparison artifact."""
    artifact_path = REPO_ROOT / "artifacts" / "qa" / f"flux_workflow_fix_smoke_{date.today().isoformat()}.md"
    lines: list[str] = [
        "# FLUX workflow schnell→dev smoke test",
        "",
        f"**Date:** {date.today().isoformat()}",
        "**PR:** #807 (FLUX schnell-mismatch fix) + #809 (LoRA base_model sweep)",
        "**Acceptance criterion source:** master execution brief P0.3 — "
        "\"side-by-side comparison committed to artifacts/qa/flux_workflow_fix_smoke_2026-04-30.md "
        "showing before/after for each genre\"",
        "",
        "## Configs compared",
        "",
        "| | OLD (schnell-mismatch) | NEW (Option A) |",
        "|-|-|-|",
        f"| ckpt | `{OLD_CONFIG['ckpt_name']}` | `{NEW_CONFIG['ckpt_name']}` |",
        f"| steps | {OLD_CONFIG['steps']} | {NEW_CONFIG['steps']} |",
        f"| cfg | {OLD_CONFIG['cfg']} | {NEW_CONFIG['cfg']} |",
        f"| sampler | {OLD_CONFIG['sampler_name']} | {NEW_CONFIG['sampler_name']} |",
        f"| scheduler | {OLD_CONFIG['scheduler']} | {NEW_CONFIG['scheduler']} |",
        "",
    ]
    if dry_run:
        lines += [
            "## Status: DRY RUN — no images rendered",
            "",
            "This artifact was generated in dry-run mode. To produce the real",
            "side-by-side comparison, re-run with `--run` after confirming",
            "RunComfy credentials are loaded.",
            "",
            "Cost estimate for full run: ~$0.24 (4 genres × 2 configs × ~$0.03/img).",
            "",
        ]
    lines += ["## Genre results", ""]
    for r in results:
        lines += [
            f"### {r['label']}",
            "",
            f"- run_id: `{r.get('run_id', 'n/a')}`",
            f"- image: `{r.get('image_path', r.get('image_url', 'n/a'))}`",
            "",
        ]
    if not dry_run:
        lines += [
            "## Operator sign-off",
            "",
            "Drift is qualitative. Operator inspects each old-vs-new pair and confirms:",
            "- [ ] mecha — drift reduced in NEW config",
            "- [ ] dark_fantasy — drift reduced in NEW config",
            "- [ ] fantasy_adventure — drift reduced in NEW config",
            "- [ ] healing (control) — quality stable or improved in NEW config",
            "",
            "If 3 of 3 failure genres improve and control holds, PR #807 + #809 are GREEN.",
            "If any failure genre still drifts on NEW config → escalate to Phase 2",
            "(LoRA + cookbook prompts in PR #802).",
            "",
        ]
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text("\n".join(lines), encoding="utf-8")
    return artifact_path


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dry-run", action="store_true", default=True, help="Print plan + write empty artifact (default)")
    p.add_argument("--run", dest="dry_run", action="store_false", help="Actually render via RunComfy")
    p.add_argument("--config", choices=["both", "old", "new"], default="both")
    p.add_argument("--genres", default=",".join(PROMPTS.keys()), help="Comma-separated subset of genres")
    p.add_argument("--deployment-id", default=os.environ.get(
        "RUNCOMFY_DEPLOYMENT_ID", "677edba8-ace0-4b2b-bad2-8e94b9959065"))
    args = p.parse_args()

    genres = [g.strip() for g in args.genres.split(",") if g.strip() in PROMPTS]
    configs_to_run = (
        [("old", OLD_CONFIG), ("new", NEW_CONFIG)] if args.config == "both"
        else [("old", OLD_CONFIG)] if args.config == "old"
        else [("new", NEW_CONFIG)]
    )

    print(f"Smoke test: {len(genres)} genres × {len(configs_to_run)} configs = {len(genres) * len(configs_to_run)} renders")
    print(f"Genres: {genres}")
    print(f"Configs: {[c[0] for c in configs_to_run]}")
    print(f"Deployment: {args.deployment_id}")
    print(f"Cost estimate: ~${len(genres) * len(configs_to_run) * 0.03:.2f}")
    print()

    out_dir = REPO_ROOT / "artifacts" / "qa" / f"flux_workflow_fix_smoke_{date.today().isoformat()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    results: list[dict] = []
    if args.dry_run:
        print("DRY RUN — no API calls made.")
        for g in genres:
            for label, cfg in configs_to_run:
                wf = build_workflow(PROMPTS[g], NEGATIVE_PROMPT, cfg)
                results.append({"label": f"{g}_{label}", "image_url": "(dry-run)", "raw": None})
                print(f"  would render: {g}_{label}  ckpt={cfg['ckpt_name']} steps={cfg['steps']} cfg={cfg['cfg']}")
    else:
        api_key = os.environ.get("RUNCOMFY_API_KEY", "").strip()
        if not api_key:
            print("ERROR: RUNCOMFY_API_KEY not set. Run: eval \"$(python3 scripts/ci/load_integration_env_from_keychain.py)\"", file=sys.stderr)
            return 1
        from scripts.image_generation.runcomfy_batch import download_image, extract_image_url
        for g in genres:
            for label, cfg in configs_to_run:
                tag = f"{g}_{label}"
                wf = build_workflow(PROMPTS[g], NEGATIVE_PROMPT, cfg)
                try:
                    r = render_one(api_key, args.deployment_id, wf, tag)
                    img_url = r.get("image_url")
                    if img_url:
                        out_path = out_dir / f"{tag}.png"
                        download_image(img_url, out_path)
                        r["image_path"] = str(out_path.relative_to(REPO_ROOT))
                    results.append(r)
                except Exception as e:  # noqa: BLE001
                    print(f"[{tag}] FAILED: {e}", file=sys.stderr)
                    results.append({"label": tag, "error": str(e)})
                time.sleep(1)

    artifact_path = write_artifact(out_dir, results, dry_run=args.dry_run)
    print()
    print(f"Artifact: {artifact_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
