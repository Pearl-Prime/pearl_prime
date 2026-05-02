#!/usr/bin/env python3
"""Stage 1 of the template-based KDP cover pipeline — FLUX renders the
imagery patch at the genre's imagery_zone aspect ratio.

This is paired with ``scripts/publish/render_kdp_cover.py`` (Stage 2),
which composites the FLUX patch into the canvas at the template's
pixel coordinates.

The two-stage flow keeps responsibilities clean:
  Stage 1 (this script): imagery only, at the imagery_zone aspect.
  Stage 2 (renderer):    layout + type composite, 1600x2560 final.

Behavior:
  * Loads ``config/publishing/bestseller_templates.yaml`` (R4 contract)
    and ``config/manga/genre_prompt_cookbook_v2.yaml`` (R5-rewritten
    aspect-aware prompts).
  * For each requested book, looks up its genre via book_genre_map.
  * SKIPS type-dominant genres (boundaries, self_worth, imposter_syndrome)
    — those have ``imagery_zone == null`` and are flat-color rendered by
    Stage 2.
  * For image-bearing genres: computes the FLUX width×height matching
    the imagery_zone aspect at ~1.0 megapixel, rounded to multiples of
    64 (FLUX VAE constraint).
  * Composes the positive prompt = subject_prompt + universal_register +
    lock_in_tokens. Negative = universal_negative.
  * Submits to ComfyUI at ``$COMFYUI_URL/prompt``. Saves output to
    ``artifacts/pipeline_examples/<teacher_id>/cover_<teacher_id>_v3_imagery.png``.

Safety:
  * Real renders require ``--i-have-confirmed-pearl-star`` (PR #826
    pattern). Without it, only --dry-run is allowed.
  * No paid LLM/image API calls.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TEMPLATES_PATH = REPO_ROOT / "config" / "publishing" / "bestseller_templates.yaml"
DEFAULT_COOKBOOK_PATH = REPO_ROOT / "config" / "manga" / "genre_prompt_cookbook_v2.yaml"
DEFAULT_IDENTITY_PATH = REPO_ROOT / "config" / "publishing" / "cover_identity_system.yaml"
DEFAULT_WORKFLOW_PATH = REPO_ROOT / "scripts" / "image_generation" / "comfyui_workflows" / "flux_txt2img_manga.json"

CKPT_BY_CONFIG = {
    "dev": "flux1-dev-fp8.safetensors",
    "schnell": "flux1-schnell-fp8.safetensors",
}

CANVAS_W = 1600
CANVAS_H = 2560

logger = logging.getLogger("render_imagery_for_template")


# ─── DATA ─────────────────────────────────────────────────────────────


@dataclass
class ImageryPlan:
    book_id: str             # bare TEACHER_BOOKS id (e.g. "maat")
    full_book_id: str        # book_genre_map key (e.g. "maat_boundaries")
    genre: str
    width: int
    height: int
    aspect: float
    positive_prompt: str
    negative_prompt: str
    output_path: Path
    type_dominant: bool


# ─── CONFIG LOADING ───────────────────────────────────────────────────


def load_templates(path: Path | None = None) -> dict[str, Any]:
    p = path or DEFAULT_TEMPLATES_PATH
    return yaml.safe_load(p.read_text())


def load_cookbook(path: Path | None = None) -> dict[str, Any]:
    p = path or DEFAULT_COOKBOOK_PATH
    return yaml.safe_load(p.read_text())


def load_identity(path: Path | None = None) -> dict[str, Any] | None:
    """Load cover_identity_system.yaml if present (R6 contract). Returns
    None if absent so the imagery pipeline keeps working."""
    p = path or DEFAULT_IDENTITY_PATH
    if not p.exists():
        return None
    return yaml.safe_load(p.read_text())


def _identity_book_record(identity_cfg: dict[str, Any] | None,
                          identity_book_id: str) -> dict[str, Any] | None:
    if not identity_cfg:
        return None
    return (identity_cfg.get("books") or {}).get(identity_book_id)


def _bare_to_identity_id(bare_id: str) -> str:
    """Map bare TEACHER_BOOKS id (e.g. 'sai_ma') to identity-system key
    ('sai_maa'). Most ids match; handful diverge."""
    overrides = {
        "sai_ma": "sai_maa",
    }
    return overrides.get(bare_id, bare_id)


# ─── ASPECT / SIZE ────────────────────────────────────────────────────


def imagery_aspect_for_genre(template: dict[str, Any]) -> float | None:
    """Compute (zone width / zone height) on the 1600x2560 canvas.
    Returns None for type-dominant genres (no imagery_zone)."""
    iz = template.get("imagery_zone")
    if iz is None:
        return None
    x_pct = iz["x_pct"]
    y_pct = iz["y_pct"]
    w = (x_pct[1] - x_pct[0]) / 100.0 * CANVAS_W
    h = (y_pct[1] - y_pct[0]) / 100.0 * CANVAS_H
    return w / h


def flux_dimensions(aspect: float, target_megapixels: float = 1.0) -> tuple[int, int]:
    """Compute FLUX width×height matching the given aspect at the target
    megapixel count. Both dimensions are rounded to the nearest multiple
    of 64 (FLUX VAE requirement).

    aspect = width / height
    """
    target_pixels = target_megapixels * 1_000_000
    # w * h = target_pixels; w/h = aspect → h = sqrt(target/aspect)
    import math
    h = math.sqrt(target_pixels / aspect)
    w = h * aspect

    def _round_64(v: float) -> int:
        return max(64, int(round(v / 64.0)) * 64)

    return _round_64(w), _round_64(h)


# ─── PROMPT COMPOSITION ───────────────────────────────────────────────


def compose_positive_prompt(cookbook: dict[str, Any], genre: str) -> str:
    """Stitch subject_prompt + universal_register + lock_in_tokens into
    a single positive-only prompt string (per cookbook v2 contract)."""
    genre_block = cookbook["genres"][genre]
    subject = genre_block.get("subject_prompt")
    if subject is None:
        raise ValueError(
            f"Genre '{genre}' is FLUX-bypassed (subject_prompt is null) — "
            "this script must skip it."
        )
    register = cookbook.get("universal_register", "").strip()
    lock_in = genre_block.get("lock_in_tokens") or []
    parts = [subject.strip()]
    if register:
        parts.append(register)
    if lock_in:
        parts.append(", ".join(lock_in))
    return ". ".join(p.rstrip(". ") for p in parts) + "."


def compose_negative_prompt(cookbook: dict[str, Any]) -> str:
    return (cookbook.get("universal_negative") or "").strip()


# ─── BOOK PLANNING ────────────────────────────────────────────────────


def _iter_book_genre_map(templates_cfg: dict[str, Any],
                         cookbook_cfg: dict[str, Any]) -> dict[str, str]:
    """Merged book_genre_map (templates wins on conflict)."""
    merged: dict[str, str] = {}
    merged.update(cookbook_cfg.get("book_genre_map") or {})
    merged.update(templates_cfg.get("book_genre_map") or {})
    return merged


def _strip_genre_suffix(full_id: str, genre: str) -> str:
    """maat_boundaries + boundaries -> maat."""
    suffix = f"_{genre}"
    if full_id.endswith(suffix):
        return full_id[: -len(suffix)]
    return full_id


def plan_for_book(
    full_book_id: str,
    templates_cfg: dict[str, Any] | None = None,
    cookbook_cfg: dict[str, Any] | None = None,
    identity_cfg: dict[str, Any] | None = None,
) -> ImageryPlan:
    """Build an ImageryPlan for a book_genre_map id (e.g.
    'maat_boundaries').

    R7: When ``identity_cfg`` (or the default identity YAML on disk)
    contains an entry for the book, use the identity-system composer
    for the prompt and respect ``cover_kind: type_only``.
    """
    templates_cfg = templates_cfg or load_templates()
    cookbook_cfg = cookbook_cfg or load_cookbook()
    if identity_cfg is None:
        identity_cfg = load_identity()
    bgm = _iter_book_genre_map(templates_cfg, cookbook_cfg)
    if full_book_id not in bgm:
        raise ValueError(
            f"Unknown book_id '{full_book_id}'. Known: {sorted(bgm.keys())}"
        )
    genre = bgm[full_book_id]
    template = templates_cfg["templates"][genre]
    bare_id = _strip_genre_suffix(full_book_id, genre)
    identity_id = _bare_to_identity_id(bare_id)
    out_path = (
        REPO_ROOT / "artifacts" / "pipeline_examples"
        / bare_id / f"cover_{bare_id}_v3_imagery.png"
    )

    identity_book = _identity_book_record(identity_cfg, identity_id)
    # R7: identity says type_only → skip FLUX even if R4 template has zone.
    if identity_book and identity_book.get("cover_kind") == "type_only":
        return ImageryPlan(
            book_id=bare_id, full_book_id=full_book_id, genre=genre,
            width=0, height=0, aspect=0.0,
            positive_prompt="", negative_prompt="",
            output_path=out_path, type_dominant=True,
        )

    aspect = imagery_aspect_for_genre(template)
    if aspect is None:
        return ImageryPlan(
            book_id=bare_id, full_book_id=full_book_id, genre=genre,
            width=0, height=0, aspect=0.0,
            positive_prompt="", negative_prompt="",
            output_path=out_path, type_dominant=True,
        )

    w, h = flux_dimensions(aspect)
    if identity_book:
        # Use identity composer when book has an identity entry.
        try:
            from scripts.publish.identity_compose_prompt import (
                compose_identity_positive,
                compose_identity_negative,
            )
            positive = compose_identity_positive(identity_id)
            negative = compose_identity_negative()
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "identity composer failed for %s: %s — falling back to cookbook",
                identity_id, exc,
            )
            positive = compose_positive_prompt(cookbook_cfg, genre)
            negative = compose_negative_prompt(cookbook_cfg)
    else:
        positive = compose_positive_prompt(cookbook_cfg, genre)
        negative = compose_negative_prompt(cookbook_cfg)
    return ImageryPlan(
        book_id=bare_id, full_book_id=full_book_id, genre=genre,
        width=w, height=h, aspect=round(aspect, 3),
        positive_prompt=positive, negative_prompt=negative,
        output_path=out_path, type_dominant=False,
    )


def plan_for_batch(
    templates_cfg: dict[str, Any] | None = None,
    cookbook_cfg: dict[str, Any] | None = None,
) -> list[ImageryPlan]:
    templates_cfg = templates_cfg or load_templates()
    cookbook_cfg = cookbook_cfg or load_cookbook()
    bgm = _iter_book_genre_map(templates_cfg, cookbook_cfg)
    return [
        plan_for_book(full_id, templates_cfg, cookbook_cfg)
        for full_id in sorted(bgm.keys())
    ]


# ─── COMFYUI SUBMISSION ───────────────────────────────────────────────


def submit_to_comfyui(
    plan: ImageryPlan,
    *,
    comfyui_url: str,
    config: str = "dev",
    workflow_path: Path | None = None,
    seed: int = 837_204,
) -> bytes:
    """Submit a single plan to ComfyUI; return image bytes.

    config: "dev" → 28 steps cfg 3.5; "schnell" → 4 steps cfg 1.0.
    """
    import time
    import urllib.parse
    import urllib.request

    wf_path = workflow_path or DEFAULT_WORKFLOW_PATH
    workflow = json.loads(wf_path.read_text())
    workflow = {k: v for k, v in workflow.items() if k != "_meta"}

    # Generic node-id heuristic: width/height live on a node with those keys;
    # positive/negative texts live on CLIPTextEncode-style nodes.
    for _, node in workflow.items():
        inputs = node.get("inputs", {})
        if "width" in inputs and "height" in inputs:
            inputs["width"] = plan.width
            inputs["height"] = plan.height
        if "noise_seed" in inputs:
            inputs["noise_seed"] = seed
        elif "seed" in inputs:
            inputs["seed"] = seed

    # Walk nodes; the workflow JSON pattern in this repo uses two
    # CLIPTextEncode nodes with {{positive_prompt}} / {{negative_prompt}}
    # placeholders. R7: detect slots by placeholder string instead of
    # hard-coded node IDs (the manga workflow uses 2/3, not 6/7).
    placeholder_filled = False
    for _, node in workflow.items():
        inputs = node.get("inputs", {})
        text = inputs.get("text")
        if not isinstance(text, str):
            continue
        if "{{positive_prompt}}" in text:
            inputs["text"] = plan.positive_prompt
            placeholder_filled = True
        elif "{{negative_prompt}}" in text:
            inputs["text"] = plan.negative_prompt or " "
            placeholder_filled = True
    # Legacy fallback: prior pipelines used node ids 6 (pos) / 7 (neg).
    if not placeholder_filled:
        if "6" in workflow and "inputs" in workflow["6"]:
            workflow["6"]["inputs"]["text"] = plan.positive_prompt
        if "7" in workflow and "inputs" in workflow["7"]:
            workflow["7"]["inputs"]["text"] = plan.negative_prompt or " "

    # Steps + cfg + sampler + scheduler + ckpt per config tier.
    # FIX (R7): swap ckpt_name based on config so --config schnell actually
    # loads the schnell ckpt instead of silently running schnell timings
    # against the dev ckpt.
    if config == "schnell":
        steps, cfg = 4, 1.0
        sampler, scheduler = "euler", "simple"
    else:
        steps, cfg = 28, 3.5
        sampler, scheduler = "dpmpp_2m", "karras"
    target_ckpt = CKPT_BY_CONFIG.get(config, CKPT_BY_CONFIG["dev"])
    for _, node in workflow.items():
        inputs = node.get("inputs", {})
        if "steps" in inputs:
            inputs["steps"] = steps
        if "cfg" in inputs:
            inputs["cfg"] = cfg
        if "sampler_name" in inputs:
            inputs["sampler_name"] = sampler
        if "scheduler" in inputs:
            inputs["scheduler"] = scheduler
        if "ckpt_name" in inputs:
            inputs["ckpt_name"] = target_ckpt

    url = comfyui_url.rstrip("/")
    payload = json.dumps({"prompt": workflow}).encode("utf-8")
    req = urllib.request.Request(
        f"{url}/prompt", data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        prompt_id = json.loads(resp.read())["prompt_id"]

    deadline = time.monotonic() + 300
    while time.monotonic() < deadline:
        time.sleep(3)
        hreq = urllib.request.Request(f"{url}/history/{prompt_id}")
        with urllib.request.urlopen(hreq, timeout=15) as hresp:
            history = json.loads(hresp.read())
        if prompt_id in history:
            for node_out in history[prompt_id].get("outputs", {}).values():
                images = node_out.get("images", [])
                if images:
                    img = images[0]
                    params = urllib.parse.urlencode({
                        "filename": img["filename"],
                        "subfolder": img.get("subfolder", ""),
                        "type": img.get("type", "output"),
                    })
                    with urllib.request.urlopen(
                        f"{url}/view?{params}", timeout=60
                    ) as iresp:
                        return iresp.read()
    raise RuntimeError(f"ComfyUI prompt {prompt_id} timed out")


# ─── EXECUTION ────────────────────────────────────────────────────────


def execute_plan(
    plan: ImageryPlan,
    *,
    config: str = "dev",
    dry_run: bool = False,
) -> dict[str, Any]:
    if plan.type_dominant:
        return {
            "book_id": plan.book_id, "full_book_id": plan.full_book_id,
            "genre": plan.genre, "status": "skipped_type_dominant",
        }
    if dry_run:
        return {
            "book_id": plan.book_id, "full_book_id": plan.full_book_id,
            "genre": plan.genre, "status": "planned",
            "width": plan.width, "height": plan.height,
            "aspect": plan.aspect,
            "output_path": str(plan.output_path),
        }

    comfyui_url = os.environ.get("COMFYUI_URL", "").strip()
    if not comfyui_url:
        raise RuntimeError(
            "COMFYUI_URL is not set. Run on Pearl Star or set the env var."
        )
    plan.output_path.parent.mkdir(parents=True, exist_ok=True)
    image_bytes = submit_to_comfyui(plan, comfyui_url=comfyui_url, config=config)
    plan.output_path.write_bytes(image_bytes)
    return {
        "book_id": plan.book_id, "full_book_id": plan.full_book_id,
        "genre": plan.genre, "status": "ok",
        "width": plan.width, "height": plan.height,
        "aspect": plan.aspect,
        "output_path": str(plan.output_path),
    }


# ─── CLI ──────────────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render imagery patches for KDP covers at template aspect ratios."
    )
    parser.add_argument("--book", type=str, default=None,
                        help="book_id key from book_genre_map (e.g. ahjan_anxiety).")
    parser.add_argument("--batch", action="store_true",
                        help="Render all books in book_genre_map.")
    parser.add_argument("--config", choices=["dev", "schnell"], default="dev")
    parser.add_argument("--dry-run", action="store_true",
                        help="List planned renders without calling ComfyUI.")
    parser.add_argument(
        "--i-have-confirmed-pearl-star", action="store_true",
        help="Required for non-dry-run execution. Confirms operator has "
             "verified Pearl Star is reachable at $COMFYUI_URL.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    args = build_parser().parse_args(argv)

    templates_cfg = load_templates()
    cookbook_cfg = load_cookbook()

    plans: list[ImageryPlan]
    if args.batch:
        plans = plan_for_batch(templates_cfg, cookbook_cfg)
    elif args.book:
        plans = [plan_for_book(args.book, templates_cfg, cookbook_cfg)]
    else:
        print("error: --book or --batch required", file=sys.stderr)
        return 2

    if not args.dry_run and not args.i_have_confirmed_pearl_star:
        print("error: real ComfyUI submission requires "
              "--i-have-confirmed-pearl-star (or use --dry-run)",
              file=sys.stderr)
        return 2

    results: list[dict[str, Any]] = []
    for plan in plans:
        try:
            result = execute_plan(plan, config=args.config, dry_run=args.dry_run)
        except Exception as exc:  # noqa: BLE001
            result = {
                "book_id": plan.book_id, "full_book_id": plan.full_book_id,
                "genre": plan.genre, "status": "error", "error": str(exc),
            }
        results.append(result)
        print(json.dumps(result))

    fail = [r for r in results if r["status"] in ("error",)]
    return 0 if not fail else 1


if __name__ == "__main__":
    sys.exit(main())
