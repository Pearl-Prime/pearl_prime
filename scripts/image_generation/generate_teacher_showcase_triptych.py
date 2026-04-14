#!/usr/bin/env python3
"""Generate 3 manga images per showcase teacher (portrait, scene, symbolic) via local ComfyUI FLUX."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required — pip install pyyaml", file=sys.stderr)
    sys.exit(1)

from scripts.image_generation.manga_teacher_batch import _build_workflow
from scripts.image_generation.runcomfy_batch import load_workflow

PROMPTS_PATH = REPO_ROOT / "config" / "manga" / "teacher_character_prompts.yaml"
BRAND_PATH = REPO_ROOT / "config" / "catalog_planning" / "brand_identity_system.yaml"
WORKFLOW_PATH = REPO_ROOT / "scripts" / "image_generation" / "comfyui_workflows" / "flux_txt2img_manga.json"
OUTPUT_DIR = REPO_ROOT / "brand-wizard-app" / "public" / "assets" / "manga_covers"
DEFAULT_COMFY_URL = os.environ.get("COMFYUI_URL", "http://192.168.1.112:8188")

SHOWCASE_TEACHER_IDS: list[str] = [
    "ahjan", "adi_da", "master_feung", "sai_ma", "ra", "junko", "miki",
    "master_wu", "pamela_fellows", "joshin", "maat", "omote", "master_sha",
]
# Legacy output files may use older keys; map yaml teacher id -> filename prefix if they differ.
YAML_KEY_TO_FILE_PREFIX: dict[str, str] = {}
IMAGE_KINDS: tuple[str, ...] = ("portrait", "scene", "symbolic")
ARCHETYPE_FLUX: dict[str, tuple[int, float]] = {
    "cozy_iyashikei": (20, 3.5),
    "dark_psychological": (25, 4.0),
    "interactive_branching": (24, 4.0),
    "webtoon_vertical_romance": (22, 4.0),
    "power_progression": (24, 4.2),
    "hyper_clean_cinematic": (24, 4.2),
}
MIN_OUTPUT_BYTES = 100 * 1024
TXT2IMG_STYLE_PREFIX = (
    "masterpiece manga illustration, high detail, clean professional linework, cohesive color palette, "
    "single clear focal subject, no text, no watermark, no logo"
)
TYPE_INSTRUCTIONS: dict[str, str] = {
    "portrait": (
        "CHARACTER PORTRAIT — close-up or medium shot, facing viewer or three-quarter view, "
        "emphasis on face, eyes, expression, and quiet presence."
    ),
    "scene": (
        "TEACHING SCENE — wider cinematic shot, environmental storytelling, teacher in context of their practice."
    ),
    "symbolic": (
        "SYMBOLIC BRAND ESSENCE — stylized semi-abstract manga, metaphorical, not another head-and-shoulders portrait."
    ),
}
TRIPTYCH_BRIEF: dict[str, dict[str, str]] = {
    "ahjan": {
        "portrait": "Calm eyes, soft golden light, temple garden bokeh.",
        "scene": "Seated meditation in a sunlit courtyard, morning mist rising.",
        "symbolic": "Golden light from clasped hands, lotus shadow, gentle iyashikei wash.",
    },
    "adi_da": {
        "portrait": "Piercing compassionate gaze, dramatic top-light, gold rim light.",
        "scene": "Stone throne-like outcrop in shadow, radiant beam through darkness.",
        "symbolic": "Eyes reflecting star field, golden sacred geometry overlay, high contrast.",
    },
    "pamela_fellows": {
        "portrait": "Compassionate smile, warm therapy-room light, plants.",
        "scene": "Two people in sunlit room, hands visible, safe connection.",
        "symbolic": "Heart-center glow, overlapping hands watercolor.",
    },
    "master_wu": {
        "portrait": "Ancient amused eyes, Taoist master, water reflection hints.",
        "scene": "Waterfall mist, qigong stillness, flowing robes.",
        "symbolic": "Mountain and water in ink, qi as brushstroke trails.",
    },
    "miki": {
        "portrait": "Kind eyes, forest light, leaves in hair.",
        "scene": "Mossy forest, fireflies, cyan dusk accents.",
        "symbolic": "Forest canopy; figure woven into tree pattern.",
    },
    "junko": {
        "portrait": "Sharp eyes, dry smile, extreme negative space.",
        "scene": "Empty wall, one tea cup, long morning shadow.",
        "symbolic": "Large enso; figure from brushstroke gap.",
    },
    "master_sha": {
        "portrait": "Compassionate eyes, violet gold particles, lotus hints.",
        "scene": "Candlelit hall, mandala on floor, student silhouettes.",
        "symbolic": "Lotus and light rays, mandala lace background.",
    },
    "ra": {
        "portrait": "Vast eyes, star reflection, minimal detail.",
        "scene": "Cliff at night, ember sparks, infinite sky.",
        "symbolic": "Eye with galaxy; form dissolving.",
    },
    "sai_ma": {
        "portrait": "Warm eyes, rose-gold aura, soft fabrics.",
        "scene": "Lotus pond sunset, gold motes.",
        "symbolic": "Hands releasing light, drifting lotus petals.",
    },
    "omote": {
        "portrait": "Noh duality: half mask, half raw face, pine.",
        "scene": "Stage diptych: formal fabric vs raw body.",
        "symbolic": "Mask becoming real face, terracotta tension.",
    },
    "master_feung": {
        "portrait": "Ancient patience, qigong hands, bamboo ink wash.",
        "scene": "Mountain temple dawn, subtle qi streams.",
        "symbolic": "Bamboo; qi as ink strokes, earth and gold.",
    },
    "maat": {
        "portrait": "Regal presence, lapis gold, desert light.",
        "scene": "Temple columns, hieroglyph hints, golden hour.",
        "symbolic": "Feather and scales, bold Egyptian geometry.",
    },
    "joshin": {
        "portrait": "Clear seeing eyes, single stone or cup, Zen space.",
        "scene": "Inquiry across low table, candle light.",
        "symbolic": "Enso fragment, warm sliver of light on ink.",
    },
}
_DIMS: dict[str, tuple[int, int]] = {
    "portrait": (800, 1000),
    "scene": (1200, 800),
    "symbolic": (800, 800),
}


def _yaml_key_for_file_prefix(file_prefix: str, yaml_teachers: dict[str, Any]) -> str | None:
    if file_prefix in yaml_teachers:
        return file_prefix
    for yk in yaml_teachers:
        if YAML_KEY_TO_FILE_PREFIX.get(yk) == file_prefix:
            return yk
    return None


def _load_brand_colors() -> dict[str, tuple[list[str], str]]:
    raw = yaml.safe_load(BRAND_PATH.read_text(encoding="utf-8"))
    out: dict[str, tuple[list[str], str]] = {}
    for _slug, block in (raw.get("teacher_brands") or {}).items():
        tid = block.get("teacher")
        bi = (block.get("brand_identity") or {})
        prim = bi.get("primary_colors") or []
        acc = bi.get("accent_color") or "#888888"
        if tid and isinstance(prim, list) and len(prim) >= 2:
            out[str(tid)] = ([str(prim[0]), str(prim[1])], str(acc))
    sg = (raw.get("standard_brands") or {}).get("spiritual_ground") or {}
    sgbi = sg.get("brand_identity") or {}
    sg_prim = sgbi.get("primary_colors") or []
    if len(sg_prim) >= 2:
        out["adi_da"] = ([str(sg_prim[0]), str(sg_prim[1])], str(sgbi.get("accent_color", "#A78BFA")))
    return out


def _color_prompt_line(tid: str, brands: dict[str, tuple[list[str], str]]) -> str:
    (p1, p2), acc = brands.get(tid, (["#333333", "#CCCCCC"], "#888888"))
    return (
        f"Strict brand palette: primary {p1} and {p2}, accent {acc}; "
        f"dominate clothing, light, and atmosphere."
    )


def _seed_for(tid: str, kind: str) -> int:
    h = hashlib.sha256(f"{tid}:{kind}:teacher_triptych_v1".encode()).digest()
    return int.from_bytes(h[:4], "big") % (2**31 - 1) or 1


def _flux_params(archetype: str) -> tuple[int, float]:
    return ARCHETYPE_FLUX.get(archetype, (24, 4.0))


def _apply_txt2img_geometry(workflow: dict[str, Any], w: int, h: int, seed: int, steps: int, cfg: float) -> None:
    if "4" in workflow:
        workflow["4"]["inputs"]["width"] = int(w)
        workflow["4"]["inputs"]["height"] = int(h)
    if "5" in workflow:
        workflow["5"]["inputs"]["seed"] = int(seed)
        workflow["5"]["inputs"]["steps"] = int(steps)
        workflow["5"]["inputs"]["cfg"] = float(cfg)
        workflow["5"]["inputs"]["denoise"] = 1.0
        workflow["5"]["inputs"]["sampler_name"] = "euler"
        workflow["5"]["inputs"]["scheduler"] = "normal"


def _strip_meta(wf: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in wf.items() if k != "_meta"}


def queue_prompt(comfy_url: str, workflow: dict[str, Any]) -> str:
    url = comfy_url.rstrip("/")
    data = json.dumps({"prompt": workflow}).encode("utf-8")
    req = urllib.request.Request(
        f"{url}/prompt", data=data, headers={"Content-Type": "application/json"}, method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        body = json.loads(resp.read().decode())
    err = body.get("error")
    if err:
        raise RuntimeError(json.dumps(err, indent=2))
    pid = body.get("prompt_id")
    if not pid:
        raise RuntimeError(f"No prompt_id: {body}")
    return str(pid)


def download_result(comfy_url: str, prompt_id: str, timeout_s: float = 600.0) -> bytes:
    url = comfy_url.rstrip("/")
    deadline = time.monotonic() + timeout_s
    last_err = None
    while time.monotonic() < deadline:
        time.sleep(2.0)
        try:
            with urllib.request.urlopen(urllib.request.Request(f"{url}/history/{prompt_id}"), timeout=60) as hresp:
                history = json.loads(hresp.read().decode())
        except urllib.error.URLError:
            continue
        if prompt_id not in history:
            continue
        entry = history[prompt_id]
        st = entry.get("status", {})
        if st.get("completed") is False and st.get("status_str") == "error":
            raise RuntimeError(json.dumps(entry, indent=2)[:4000])
        outputs = entry.get("outputs") or {}
        for node_out in outputs.values():
            if not isinstance(node_out, dict):
                continue
            images = node_out.get("images") or []
            if images:
                img = images[0]
                params = urllib.parse.urlencode({
                    "filename": img["filename"],
                    "subfolder": img.get("subfolder", ""),
                    "type": img.get("type", "output"),
                })
                with urllib.request.urlopen(f"{url}/view?{params}", timeout=120) as iresp:
                    return iresp.read()
        for node_out in outputs.values():
            if isinstance(node_out, dict) and "exception_message" in node_out:
                last_err = node_out.get("exception_message")
        if last_err:
            break
    raise RuntimeError(f"Timeout prompt_id={prompt_id!r} err={last_err!r}")


def _build_positive(
    tid: str, yaml_teachers: dict[str, Any], brands: dict[str, tuple[list[str], str]], kind: str
) -> str:
    yk = _yaml_key_for_file_prefix(tid, yaml_teachers) or tid
    tdef = yaml_teachers.get(yk) or {}
    core = (tdef.get("positive") or "").strip().replace("\n", " ")
    brief = TRIPTYCH_BRIEF.get(tid, {}).get(kind, "")
    return " ".join(
        p for p in (
            TXT2IMG_STYLE_PREFIX,
            TYPE_INSTRUCTIONS[kind],
            brief,
            _color_prompt_line(tid, brands),
            core,
        ) if p
    )


def _build_negative(yaml_teachers: dict[str, Any], tid: str, shared_negative: str) -> str:
    yk = _yaml_key_for_file_prefix(tid, yaml_teachers) or tid
    tdef = yaml_teachers.get(yk) or {}
    own = (tdef.get("negative") or "").strip().replace("\n", " ")
    return ", ".join(x for x in (shared_negative, own) if x)


def main() -> int:
    parser = argparse.ArgumentParser(description="Teacher showcase triptych via ComfyUI FLUX.")
    parser.add_argument("--teacher", default=None)
    parser.add_argument("--type", choices=list(IMAGE_KINDS), default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--comfy-url", default=DEFAULT_COMFY_URL)
    parser.add_argument("--checkpoint", default=None)
    args = parser.parse_args()

    data = yaml.safe_load(PROMPTS_PATH.read_text(encoding="utf-8"))
    yaml_teachers: dict[str, Any] = dict(data.get("teachers") or {})
    shared_negative = (data.get("shared_negative") or "").strip()
    brands = _load_brand_colors()
    template = load_workflow(WORKFLOW_PATH)

    teachers = list(SHOWCASE_TEACHER_IDS)
    if args.teacher:
        if args.teacher not in teachers:
            print(f"ERROR: unknown teacher {args.teacher!r}", file=sys.stderr)
            return 2
        teachers = [args.teacher]

    kinds = list(IMAGE_KINDS) if args.type is None else [args.type]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ok = failed = 0

    for tid in teachers:
        yk = _yaml_key_for_file_prefix(tid, yaml_teachers)
        if yk is None:
            print(f"SKIP {tid}: no YAML entry", file=sys.stderr)
            failed += len(kinds)
            continue
        tdef = yaml_teachers.get(yk) or {}
        arch = str(tdef.get("style_archetype") or "dark_psychological")
        steps, cfg = _flux_params(arch)

        for kind in kinds:
            w, h = _DIMS[kind]
            pos = _build_positive(tid, yaml_teachers, brands, kind)
            neg = _build_negative(yaml_teachers, tid, shared_negative)
            seed = _seed_for(tid, kind)
            out_path = OUTPUT_DIR / f"{tid}_{kind}.png"

            if args.dry_run:
                print(f"[DRY-RUN] {tid}/{kind} {w}x{h} seed={seed}")
                ok += 1
                continue

            wf = _build_workflow(template, positive_prompt=pos, negative_prompt=neg, input_image_b64=None, seed=seed)
            _apply_txt2img_geometry(wf, w, h, seed, steps, cfg)
            if args.checkpoint and "1" in wf:
                wf["1"]["inputs"]["ckpt_name"] = args.checkpoint

            try:
                print(f"{tid} {kind} → queue …", flush=True)
                pid = queue_prompt(args.comfy_url, _strip_meta(wf))
                raw = download_result(args.comfy_url, pid)
            except Exception as exc:
                print(f"  FAIL: {exc}", file=sys.stderr)
                failed += 1
                continue

            out_path.write_bytes(raw)
            sz = out_path.stat().st_size
            if sz < MIN_OUTPUT_BYTES:
                print(f"  WARN small file {sz}", file=sys.stderr)
                failed += 1
                continue
            print(f"  OK {out_path.name} ({sz:,} bytes)")
            ok += 1

    print(f"Done: {ok} ok, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
