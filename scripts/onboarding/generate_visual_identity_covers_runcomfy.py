#!/usr/bin/env python3
"""Visual identity (PR B) — generate KDP-style cover candidates via RunComfy.

Uses the same ComfyUI serverless deployment as the video bank (see
``scripts/image_generation/runcomfy_batch.py``). Credentials:
``RUNCOMFY_API_KEY`` and optional ``RUNCOMFY_DEPLOYMENT_ID``
(``docs/INTEGRATION_CREDENTIALS_REGISTRY.md``, § RunComfy).

Prompts match ``specs/BRAND_ADMIN_ONBOARDING_IMAGE_PACK_V1_TRUST_LAYER_SPEC.md``
§ Batch 4 (vi_calm … vi_mysterious). Demo book metadata is fixed across all six
slots; only ``style_variant`` / prompt body changes.

Examples::

    python3 scripts/onboarding/generate_visual_identity_covers_runcomfy.py generate --candidates 3

    python3 scripts/onboarding/generate_visual_identity_covers_runcomfy.py promote \\
      --winners scripts/onboarding/vi_winners.example.json \\
      --generation-run run_2026_04_03_approved
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.image_generation.runcomfy_batch import (  # noqa: E402
    _DEFAULT_DEPLOYMENT_ID,
    _RUNCOMFY_API_BASE,
    download_image,
    get_result,
    poll_request,
    submit_inference,
)

CONFIG_REG = REPO_ROOT / "config" / "onboarding" / "example_registry.json"
PUBLIC_REG = REPO_ROOT / "brand-wizard-app" / "public" / "onboarding" / "example_registry.json"
PUBLIC_GEN = REPO_ROOT / "brand-wizard-app" / "public" / "onboarding" / "proof" / "generated"

# Fixed demo book (PR B contract) — only style_variant differs per slot.
COVER_TITLE = "The Spiral Stops Here"
COVER_SUBTITLE = "A Practical Path Back to Calm, Clarity, and Direction"
COVER_AUTHOR = "Phoenix Press"
TYPO_SUFFIX = (
    "Amazon KDP nonfiction book cover, 2:3 portrait trim feel, professional "
    "hierarchy. Legible title text: "
    f'"{COVER_TITLE}". Subtitle: "{COVER_SUBTITLE}". Author: "{COVER_AUTHOR}". '
    "Typography crisp and straight, not warped or misspelled. "
)

# Trust-layer spec § Batch 4 (visual identity) — style bodies only; TYPO_SUFFIX prepended.
_STYLE_BODIES: dict[str, str] = {
    "calm": (
        "A premium self-help book cover visual with a calm identity: serene, spacious, regulated, "
        "elegant, emotionally safe, soft but not dull. Minimal but not empty. Designed to feel like "
        "a real bestselling modern wellness or overthinking-recovery book cover. High readability "
        "of form, refined restraint, polished commercial product visual, premium publishing quality, "
        "clear focal hierarchy, visually believable, clean lighting, strong composition, modern "
        "editorial finish, realistic material treatment, production-ready, not abstract inspiration art."
    ),
    "dark": (
        "A premium self-help or transformational nonfiction book cover visual with a dark identity: "
        "moody, intelligent, deep, dramatic, controlled, emotionally serious. Should feel premium and "
        "sophisticated, not horror, not fantasy. Suitable for shadow work, burnout, deep transformation, "
        "or intense personal growth. Real cover feel, polished commercial product visual, premium "
        "publishing quality, clear focal hierarchy, visually believable, clean lighting, strong "
        "composition, modern editorial finish, realistic material treatment, production-ready, not "
        "abstract inspiration art."
    ),
    "earthy": (
        "A premium book cover visual with an earthy identity: grounded, natural, human, textured, warm, "
        "quietly restorative. Suitable for healing, embodiment, nervous system regulation, or wholesome "
        "transformation. Must feel like a real marketable cover, not rustic décor art. Polished "
        "commercial product visual, premium publishing quality, clear focal hierarchy, visually "
        "believable, clean lighting, strong composition, modern editorial finish, realistic material "
        "treatment, production-ready, not abstract inspiration art."
    ),
    "bold": (
        "A premium nonfiction or self-help book cover visual with a bold identity: assertive, high "
        "contrast, confident, decisive, immediately noticeable in a storefront thumbnail. Strong impact "
        "without becoming cheap or loud. Feels like a real commercial winner for confidence, "
        "discipline, leadership, or action-oriented transformation. Polished commercial product visual, "
        "premium publishing quality, clear focal hierarchy, visually believable, clean lighting, strong "
        "composition, modern editorial finish, realistic material treatment, production-ready, not "
        "abstract inspiration art."
    ),
    "premium": (
        "A premium luxury-positioned self-help or transformational book cover visual: elevated, "
        "expensive-feeling, refined, highly intentional, tasteful, sophisticated. Should signal "
        "authority, quality, and aspirational emotional transformation. Must look like a real top-tier "
        "publishing output. Polished commercial product visual, premium publishing quality, clear focal "
        "hierarchy, visually believable, clean lighting, strong composition, modern editorial finish, "
        "realistic material treatment, production-ready, not abstract inspiration art."
    ),
    "mysterious": (
        "A premium self-help or spiritual-transformation book cover visual with a mysterious identity: "
        "intriguing, subtle, magnetic, atmospheric, emotionally open-ended, contemplative but still "
        "commercial. Should create curiosity without confusion. Real cover-native composition, polished "
        "commercial product visual, premium publishing quality, clear focal hierarchy, visually "
        "believable, clean lighting, strong composition, modern editorial finish, realistic material "
        "treatment, production-ready, not abstract inspiration art."
    ),
}

VI_SLOTS: list[tuple[str, str]] = [
    ("pack_v1_vi_calm_v1", "calm"),
    ("pack_v1_vi_dark_v1", "dark"),
    ("pack_v1_vi_earthy_v1", "earthy"),
    ("pack_v1_vi_bold_v1", "bold"),
    ("pack_v1_vi_premium_v1", "premium"),
    ("pack_v1_vi_mysterious_v1", "mysterious"),
]


def _build_prompt(style_key: str) -> str:
    body = _STYLE_BODIES[style_key]
    return TYPO_SUFFIX + body


def _run_one_image(
    *,
    api_key: str,
    deployment_id: str,
    positive: str,
    seed: int,
    out_path: Path,
) -> dict[str, Any]:
    resp = submit_inference(
        api_key=api_key,
        deployment_id=deployment_id,
        positive_prompt=positive,
        seed=seed,
    )
    request_id = resp.get("request_id", "unknown")
    status_url = resp.get("status_url", "")
    result_url = resp.get("result_url", "")
    if not status_url:
        base = f"{_RUNCOMFY_API_BASE}/deployments/{deployment_id}/requests/{request_id}"
        status_url = f"{base}/status"
        result_url = f"{base}/result"

    poll_resp = poll_request(api_key, status_url)
    status = poll_resp.get("status", "unknown")
    if status not in ("succeeded", "completed"):
        return {"status": status, "error": poll_resp.get("error"), "request_id": request_id}

    result_resp = get_result(api_key, result_url)
    outputs = result_resp.get("outputs", {})
    output_url = None
    for _node_id, node_output in outputs.items():
        if isinstance(node_output, dict):
            images = node_output.get("images", [])
            if images:
                output_url = images[0].get("url")
                break
    if not output_url:
        return {"status": "completed_no_output", "raw_outputs": outputs, "request_id": request_id}

    out_path.parent.mkdir(parents=True, exist_ok=True)
    download_image(output_url, out_path)
    return {"status": "completed", "path": str(out_path), "request_id": request_id, "seed": seed}


def _try_optimize_png(path: Path) -> None:
    try:
        from PIL import Image  # type: ignore[import-untyped]
    except ImportError:
        return
    with Image.open(path) as im:
        im.save(path, format="PNG", optimize=True)


def cmd_generate(args: argparse.Namespace) -> int:
    api_key = args.api_key or os.environ.get("RUNCOMFY_API_KEY", "").strip()
    deployment_id = args.deployment_id or os.environ.get(
        "RUNCOMFY_DEPLOYMENT_ID", _DEFAULT_DEPLOYMENT_ID
    ).strip()
    if not api_key:
        print("Error: set RUNCOMFY_API_KEY or pass --api-key", file=sys.stderr)
        return 1

    run_dir = REPO_ROOT / args.output_root / args.run_id
    manifest: list[dict[str, Any]] = []
    seed_base = args.seed_base

    for slot_idx, (reg_id, style_key) in enumerate(VI_SLOTS):
        if args.slots and style_key not in args.slots and reg_id not in args.slots:
            continue
        prompt = _build_prompt(style_key)
        for c in range(args.candidates):
            seed = seed_base + slot_idx * 10_000 + c * 997
            fname = f"{reg_id}_c{c}_seed{seed}.png"
            out_path = run_dir / fname
            print(f"[{reg_id}] candidate {c + 1}/{args.candidates} seed={seed}")
            res = _run_one_image(
                api_key=api_key,
                deployment_id=deployment_id,
                positive=prompt,
                seed=seed,
                out_path=out_path,
            )
            if res.get("status") == "completed":
                _try_optimize_png(out_path)
                print(f"  -> {out_path} ({out_path.stat().st_size} bytes)")
            else:
                print(f"  !! {res}")
            manifest.append(
                {
                    "registry_id": reg_id,
                    "style_variant": style_key,
                    "candidate_index": c,
                    "seed": seed,
                    **res,
                }
            )
            if c < args.candidates - 1:
                time.sleep(args.sleep_s)

    manifest_path = run_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Manifest: {manifest_path}")
    failed = sum(1 for m in manifest if m.get("status") != "completed")
    return 0 if failed == 0 else 1


def cmd_promote(args: argparse.Namespace) -> int:
    winners_path = Path(args.winners)
    if not winners_path.is_file():
        print(f"Error: winners file not found: {winners_path}", file=sys.stderr)
        return 1
    mapping: dict[str, str] = json.loads(winners_path.read_text(encoding="utf-8"))
    PUBLIC_GEN.mkdir(parents=True, exist_ok=True)

    for reg_id, src in mapping.items():
        srcp = Path(src).expanduser()
        if not srcp.is_file():
            print(f"Error: missing file for {reg_id}: {srcp}", file=sys.stderr)
            return 1
        dest = PUBLIC_GEN / f"{reg_id}.png"
        shutil.copy2(srcp, dest)
        _try_optimize_png(dest)
        print(f"Promoted {reg_id} -> {dest}")

    if not args.skip_registry:
        for path in (CONFIG_REG, PUBLIC_REG):
            data = json.loads(path.read_text(encoding="utf-8"))
            for row in data:
                rid = row.get("id")
                if rid not in mapping:
                    continue
                row["status"] = "ready"
                row["asset_path"] = f"/onboarding/proof/generated/{rid}.png"
                row["platform_mix"] = ["amazon_kdp"]
                row["generation_run"] = args.generation_run
                row["model_id"] = args.model_id
                row["template_id"] = args.template_id
                row["qc_approved_by"] = args.qc_approved_by
                if args.seed_override:
                    row["seed"] = str(args.seed_override)
                row["source"] = "runcomfy_visual_identity_pipeline"
            path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print(f"Updated registry: {path}")

    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="PR B visual identity covers via RunComfy.")
    sub = p.add_subparsers(dest="command", required=True)

    g = sub.add_parser("generate", help="Generate candidate PNGs under artifacts/")
    g.add_argument("--api-key", default="", help="RunComfy API key (else RUNCOMFY_API_KEY)")
    g.add_argument("--deployment-id", default="", help="Else RUNCOMFY_DEPLOYMENT_ID or default")
    g.add_argument("--candidates", type=int, default=3, help="Candidates per slot (3–5 recommended)")
    g.add_argument("--seed-base", type=int, default=482_001)
    g.add_argument("--run-id", default="", help="Output folder name under output-root")
    g.add_argument(
        "--output-root",
        default="artifacts/onboarding_examples/visual_identity/runcomfy",
        help="Directory under repo root",
    )
    g.add_argument("--sleep-s", type=float, default=2.0, help="Pause between API calls")
    g.add_argument(
        "--slots",
        nargs="*",
        default=None,
        help="Optional filter: style keys (calm, dark, …) and/or registry ids",
    )
    g.set_defaults(func=cmd_generate)

    pr = sub.add_parser("promote", help="Copy winner PNGs into public onboarding + update registries")
    pr.add_argument(
        "--winners",
        required=True,
        help="JSON map registry_id -> absolute or relative path to winner PNG",
    )
    pr.add_argument("--generation-run", required=True, help="Traceability label, e.g. run_2026_04_03")
    pr.add_argument("--model-id", default="runcomfy_flux_deployment_default")
    pr.add_argument("--template-id", default="kdp_visual_identity_v1")
    pr.add_argument("--qc-approved-by", default="human")
    pr.add_argument("--seed-override", default="", help="Optional single seed string written to each row")
    pr.add_argument(
        "--skip-registry",
        action="store_true",
        help="Only copy files; do not edit example_registry.json",
    )
    pr.set_defaults(func=cmd_promote)

    args = p.parse_args()
    if args.command == "generate" and not args.run_id:
        args.run_id = time.strftime("run_%Y_%m_%d_%H%M%S")
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
