"""Reference character sheet generator — V2 manga pipeline Phase B.6.

For each named teacher with a filled `character_design` YAML, generate one
canonical reference sheet PNG (front_neutral pose, 12-axis vocabulary tokens,
brand-tradition register). The sheet feeds Phase B.7's reference-image input
pathway (PuLID-FaceNet conditioning) at panel render time.

Pipeline:
    1. Load character_design YAML (validated by Phase A constraint solver).
    2. Engine router selects base + workflow per brand demographic + genre.
    3. Build reference-sheet prompt: prompt_builder positive tokens + a
       "front_neutral pose, character reference sheet, plain background"
       qualifier; negative tokens carry the universal forbidden tokens.
    4. Submit to Pearl Star ComfyUI via the existing queue_panel_renders.py
       wire (single panel, sampler per engine_router; no reference image
       at this stage — the OUTPUT is the reference image).
    5. Write PNG to artifacts/manga/image_bank/<brand>/reference_sheets/
       <character_id>/<character_id>_reference_sheet.png
    6. Write provenance.json with engine + seed + prompt hash + character_
       design YAML hash + ip_adapter_weight target.

Gated on: character_design YAML existing for the teacher AND Pearl Star's
PuLID nodes installed (Phase B's Pearl_Int install ws). If either gate
fails, the generator skips with a documented status row.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_COMFY_URL = os.environ.get("COMFYUI_URL", "http://192.168.1.112:8188")
DEFAULT_REFERENCE_DIR = REPO_ROOT / "artifacts" / "manga" / "image_bank"
DEFAULT_SEED_BASE = 7777

POLL_INTERVAL_SEC = 2.0
POLL_TIMEOUT_SEC = 300.0


@dataclass
class GenerationResult:
    teacher_id: str
    brand_id: str
    success: bool
    out_path: str | None
    provenance_path: str | None
    engine: str
    reasoning: str
    skipped: bool = False
    skip_reason: str = ""


# ── Helpers (lazy imports for prompt_builder + engine_router to keep this
# module unit-testable without yaml on the import path).

def _build_reference_prompt(
    character_design: dict,
    *,
    primary_genre: str | None,
    secondary_genre: str | None,
    base_model: str,
    width: int,
    height: int,
):
    """Build a positive + negative prompt for a canonical reference sheet.
    Reuses Phase A.2 prompt_builder for character + genre tokens; appends
    the reference-sheet qualifier."""
    from scripts.manga.character_individuation.prompt_builder import (
        build_prompt, load_builder_config,
    )

    cfg = load_builder_config(base_model=base_model, width=width, height=height)

    # The "scene_description" for a reference sheet is the canonical pose.
    scene = (
        "Character reference sheet, front-facing neutral pose, "
        "plain neutral background, full body, soft frontal lighting"
    )
    built = build_prompt(
        panel_id=f"reference_sheet_{character_design.get('series_id', 'unknown')}",
        scene_description=scene,
        character_design=character_design,
        primary_genre=primary_genre,
        secondary_genre=secondary_genre,
        builder_config=cfg,
    )
    return built


def _select_engine_for(character_design: dict):
    from scripts.manga.character_individuation.engine_router import select_engine

    return select_engine(
        brand_id=character_design.get("brand_id"),
        genre=character_design.get("genre_family"),
        market_demo=character_design.get("market_demo"),
        color_mode="bw",
        use_reference=False,  # generating the reference; no reference input
    )


# ── ComfyUI submission (mirrors queue_panel_renders.py pattern) ──────────────

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


def _strip_meta(workflow: dict) -> dict:
    return {k: v for k, v in workflow.items() if k != "_meta"}


def _inject_prompts_into_workflow(
    workflow: dict, *, positive: str, negative: str, seed: int,
) -> dict:
    """Replace {{positive_prompt}} / {{negative_prompt}} / seeds in the
    template. Mirrors scripts/image_generation/manga_teacher_batch._build_workflow."""
    out = json.loads(json.dumps(workflow))  # deep copy
    for node in out.values():
        if not isinstance(node, dict):
            continue
        inputs = node.get("inputs") or {}
        text = inputs.get("text")
        if isinstance(text, str):
            if "{{positive_prompt}}" in text:
                inputs["text"] = positive
            elif "{{negative_prompt}}" in text:
                inputs["text"] = negative
        if "seed" in inputs:
            inputs["seed"] = seed
        if "noise_seed" in inputs:
            inputs["noise_seed"] = seed
    return out


def _submit_to_comfy(
    comfy_url: str, workflow: dict, out_path: Path,
) -> tuple[bool, str]:
    submit = _post_json(f"{comfy_url}/prompt", {"prompt": workflow})
    prompt_id = submit.get("prompt_id")
    if not prompt_id:
        return False, "ComfyUI returned no prompt_id"
    deadline = time.time() + POLL_TIMEOUT_SEC
    while time.time() < deadline:
        time.sleep(POLL_INTERVAL_SEC)
        try:
            history = _get_json(f"{comfy_url}/history/{prompt_id}")
        except urllib.error.URLError:
            continue
        if prompt_id not in history:
            continue
        outputs = history[prompt_id].get("outputs") or {}
        for node_outputs in outputs.values():
            images = node_outputs.get("images") or []
            if not images:
                continue
            img = images[0]
            view_url = (
                f"{comfy_url}/view?filename={img['filename']}"
                f"&subfolder={img.get('subfolder', '')}&type={img.get('type', 'output')}"
            )
            data = _get_bytes(view_url)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(data)
            return True, f"wrote {out_path.name} ({len(data):,} bytes)"
    return False, f"poll timeout after {POLL_TIMEOUT_SEC}s"


# ── Public API ───────────────────────────────────────────────────────────────

def generate_reference_sheet(
    character_design_path: str | Path,
    *,
    teacher_id: str,
    brand_id: str | None = None,
    output_root: Path | None = None,
    comfy_url: str = DEFAULT_COMFY_URL,
    seed: int | None = None,
    dry_run: bool = False,
) -> GenerationResult:
    """Generate one canonical reference sheet for a teacher.

    Returns a GenerationResult; on dry_run, the workflow is built but not
    submitted to ComfyUI (used by tests + plan-only operator runs).
    """
    cd_path = Path(character_design_path)
    if not cd_path.is_file():
        return GenerationResult(
            teacher_id=teacher_id, brand_id=brand_id or "?",
            success=False, out_path=None, provenance_path=None,
            engine="?", reasoning="character_design YAML not found",
            skipped=True,
            skip_reason=f"character_design YAML not found: {cd_path}",
        )

    series_yaml = yaml.safe_load(cd_path.read_text()) or {}
    cd = series_yaml.get("character_design") or series_yaml
    if "axes" not in cd:
        return GenerationResult(
            teacher_id=teacher_id, brand_id=brand_id or "?",
            success=False, out_path=None, provenance_path=None,
            engine="?", reasoning="no axes in character_design block",
            skipped=True, skip_reason="character_design YAML has no axes",
        )

    # Forward top-level fields onto cd if not already present
    for fwd in ("market_demo", "genre_family", "secondary_genre", "brand_id", "series_id"):
        if fwd in series_yaml and fwd not in cd:
            cd[fwd] = series_yaml[fwd]
    brand_id = brand_id or cd.get("brand_id") or "unknown_brand"
    cd["brand_id"] = brand_id

    selection = _select_engine_for(cd)
    sampler = selection.sampler

    built_prompt = _build_reference_prompt(
        cd,
        primary_genre=cd.get("genre_family"),
        secondary_genre=cd.get("secondary_genre"),
        base_model=selection.engine,
        width=sampler["width"],
        height=sampler["height"],
    )

    seed_value = seed if seed is not None else DEFAULT_SEED_BASE + sum(ord(c) for c in teacher_id)

    out_root = output_root or DEFAULT_REFERENCE_DIR
    out_dir = Path(out_root) / brand_id / "reference_sheets" / teacher_id
    out_path = out_dir / f"{teacher_id}_reference_sheet.png"
    provenance_path = out_dir / "provenance.json"

    cd_yaml_text = cd_path.read_text()
    provenance = {
        "teacher_id": teacher_id,
        "brand_id": brand_id,
        "engine": selection.engine,
        "workflow_path": str(selection.workflow_path),
        "sampler": dict(sampler),
        "seed": seed_value,
        "positive_prompt": built_prompt.positive,
        "negative_prompt": built_prompt.negative,
        "character_design_path": str(cd_path),
        "character_design_sha256": hashlib.sha256(cd_yaml_text.encode("utf-8")).hexdigest(),
        "engine_router_reasoning": selection.reasoning,
        "ip_adapter_weight_target": 0.85,
        "phase": "V2-B6-reference-sheet",
        "render_target": f"{sampler['width']}x{sampler['height']}",
        "schema_version": "1.0",
    }

    if dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)
        provenance_path.write_text(json.dumps(provenance, indent=2, ensure_ascii=False))
        return GenerationResult(
            teacher_id=teacher_id, brand_id=brand_id,
            success=True, out_path=str(out_path),
            provenance_path=str(provenance_path),
            engine=selection.engine, reasoning="dry-run; provenance written, no ComfyUI submit",
        )

    workflow_path = selection.workflow_path
    if not workflow_path.is_file():
        return GenerationResult(
            teacher_id=teacher_id, brand_id=brand_id,
            success=False, out_path=None, provenance_path=None,
            engine=selection.engine,
            reasoning=f"workflow template not found: {workflow_path}",
            skipped=True, skip_reason="workflow template missing",
        )
    template = json.loads(workflow_path.read_text())
    workflow = _inject_prompts_into_workflow(
        template, positive=built_prompt.positive,
        negative=built_prompt.negative, seed=seed_value,
    )
    workflow = _strip_meta(workflow)

    try:
        ok, msg = _submit_to_comfy(comfy_url, workflow, out_path)
    except urllib.error.URLError as e:
        return GenerationResult(
            teacher_id=teacher_id, brand_id=brand_id,
            success=False, out_path=None, provenance_path=None,
            engine=selection.engine,
            reasoning=f"ComfyUI submit failed: {e}",
            skipped=True, skip_reason="ComfyUI unreachable",
        )

    if ok:
        out_dir.mkdir(parents=True, exist_ok=True)
        provenance_path.write_text(json.dumps(provenance, indent=2, ensure_ascii=False))
    return GenerationResult(
        teacher_id=teacher_id, brand_id=brand_id,
        success=ok, out_path=str(out_path) if ok else None,
        provenance_path=str(provenance_path) if ok else None,
        engine=selection.engine, reasoning=msg,
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--character-design", required=True,
                    help="Path to series YAML carrying the character_design block")
    ap.add_argument("--teacher-id", required=True)
    ap.add_argument("--brand-id", default=None)
    ap.add_argument("--comfy-url", default=DEFAULT_COMFY_URL)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    res = generate_reference_sheet(
        args.character_design,
        teacher_id=args.teacher_id,
        brand_id=args.brand_id,
        comfy_url=args.comfy_url,
        seed=args.seed,
        dry_run=args.dry_run,
    )
    print(json.dumps(asdict(res), indent=2))
    return 0 if res.success else 2


if __name__ == "__main__":
    raise SystemExit(main())
