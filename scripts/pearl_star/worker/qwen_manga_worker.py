"""Pearl Star Job Queue V1 — Qwen-Image manga panel worker.

Renders via ComfyUI split-file Qwen graph (no PuLID — bank L0/L2/L3 layers).
Spec: MANGA_GENRE_PROMPTING_SYSTEM_RESEARCH_2026-07-10; prompt-builder v3 Qwen-primary.

Wave-2 Item 2 (2026-07-22): step count and negative-prompt CJK-character
exclusion synced to the reference no-PuLID workflow
(scripts/image_generation/comfyui_workflows/qwen_image_no_pulid_manga.json —
KSampler steps=28, cfg=4.0) plus a byte-floor blob-gate on the landed PNG
(the render-progress-bytes doctrine in CLAUDE.md, applied at the worker level
so a corrupt/stub ComfyUI output fails the task instead of landing silently).
"""

from __future__ import annotations

import os
import shutil
import time
from pathlib import Path

import requests

from app import app
from flux_schnell_worker import COMFY_OUTPUT, COMFY_URL, _Heartbeat, _poll_history
from gpu_heavy_lock import gpu_heavy_lock

_PS_REPO = Path(os.environ.get("PS_PHOENIX_REPO", "/home/ahjan108/phoenix_omega"))
_MANGA_OUT = Path(os.environ.get("PS_MANGA_OUT_ROOT", "/var/lib/pearl-star/manga_out"))

WORKLOAD = "t2i_qwen_image"
STALL_WARN_S = 180.0
STALL_KILL_S = 600.0
EXPECTED_TOTAL_S = 120.0
DEFAULT_W, DEFAULT_H = 1080, 1920

# Blob-gate floor (bytes): a landed PNG smaller than this is treated as a
# corrupt/stub ComfyUI output, not a real panel render (CLAUDE.md manga
# doctrine: "stub-as-done" — a render marked ok/done with bytes < floor must
# not pass silently). Mirrors the CI-side check_render_progress_bytes.py floor.
MIN_PNG_BYTES = 50_000

# Steps/cfg synced to the reference no-PuLID workflow (Wave-2 Item 2,
# 2026-07-22): scripts/image_generation/comfyui_workflows/qwen_image_no_pulid_manga.json
# KSampler node "5" — steps=28, cfg=4.0 (was steps=24 here; 24 predates the
# reference JSON and undercounted denoising steps vs the shipped graph).
STEPS = 28
CFG = 4.0

_NEG_SUFFIX = (
    "text, words, letters, captions, watermark, signature, signs, writing, "
    "typography, font, lettering, logos, subtitles, calligraphy, "
    "chinese characters, japanese characters, kanji, hiragana, katakana, hangul"
)


def qwen_image_txt2img_graph(
    prompt: str, negative: str, width: int, height: int, seed: int
) -> dict:
    neg = f"{negative}, {_NEG_SUFFIX}" if negative.strip() else _NEG_SUFFIX
    return {
        "1": {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": "qwen_image_fp8_e4m3fn.safetensors",
                "weight_dtype": "fp8_e4m3fn",
            },
        },
        "8": {
            "class_type": "CLIPLoader",
            "inputs": {
                "clip_name": "qwen_2.5_vl_7b_fp8_scaled.safetensors",
                "type": "qwen_image",
            },
        },
        "9": {
            "class_type": "VAELoader",
            "inputs": {"vae_name": "split_files/vae/qwen_image_vae.safetensors"},
        },
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["8", 0]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": neg, "clip": ["8", 0]}},
        "4": {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": width, "height": height, "batch_size": 1},
        },
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": STEPS,
                "cfg": CFG,
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": 1.0,
                "model": ["1", 0],
                "positive": ["2", 0],
                "negative": ["3", 0],
                "latent_image": ["4", 0],
            },
        },
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["9", 0]}},
        "7": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": "manga_panel_qwen", "images": ["6", 0]},
        },
    }


def _resolve_dest(dest_path: str, output_basename: str, panel_id: str) -> Path:
    if dest_path:
        p = Path(dest_path)
        try:
            rel = p.resolve().relative_to(_PS_REPO.resolve())
            return (_MANGA_OUT / rel).resolve()
        except ValueError:
            return p
    out_root = Path(os.environ.get("PS_OUTPUT_DIR", "/var/lib/pearl-star/output"))
    name = output_basename or panel_id or "panel"
    return out_root / f"{name}.png"


def _assert_blob_gate(dst: Path) -> None:
    """Raise if the landed PNG is under MIN_PNG_BYTES (stub/corrupt output).

    Mirrors the CI-side "stub-as-done" gate (CLAUDE.md manga doctrine,
    scripts/ci/check_render_progress_bytes.py) at the worker level: a task
    that lands a near-empty file should fail loudly (Procrastinate retries
    once, per @app.task(retry=1)) rather than report COMPLETED silently.
    """
    try:
        size = dst.stat().st_size
    except FileNotFoundError as exc:
        raise RuntimeError(f"blob-gate: expected output missing at {dst}") from exc
    if size < MIN_PNG_BYTES:
        raise RuntimeError(
            f"blob-gate: {dst} is {size} bytes (< {MIN_PNG_BYTES} floor) — "
            "treating as a stub/corrupt render, not a real panel"
        )


def _land_png(filename: str, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    src = COMFY_OUTPUT / filename
    try:
        if src.is_file():
            shutil.copyfile(src, dst)
            return
    except PermissionError:
        pass
    v = requests.get(
        f"{COMFY_URL}/view",
        params={"filename": filename, "type": "output"},
        timeout=120,
    )
    v.raise_for_status()
    dst.write_bytes(v.content)


@app.task(name="t2i_qwen_image", queue="t2i", retry=1)
def t2i_qwen_image(
    prompt: str,
    negative: str = "",
    width: int = DEFAULT_W,
    height: int = DEFAULT_H,
    seed: int = 42,
    panel_id: str = "",
    output_basename: str = "",
    dest_path: str = "",
) -> dict:
    """Render one Qwen-Image manga panel; land PNG at dest_path when provided."""
    job_id = os.environ.get("PROCRASTINATE_JOB_ID", panel_id or f"panel-{int(time.time())}")
    hb = _Heartbeat(
        job_id,
        expected_total_s=EXPECTED_TOTAL_S,
        stall_warn_at_s=STALL_WARN_S,
        stall_kill_at_s=STALL_KILL_S,
    )
    hb.start()
    try:
        with gpu_heavy_lock(
            f"t2i:{panel_id or job_id}",
            worker_lane="manga",
            wait_s=float(os.environ.get("PS_GPU_HEAVY_WAIT_S", "600")),
        ):
            return _run_qwen_image(
                hb=hb,
                prompt=prompt,
                negative=negative,
                width=width,
                height=height,
                seed=seed,
                panel_id=panel_id,
                output_basename=output_basename,
                dest_path=dest_path,
                job_id=job_id,
            )
    finally:
        hb.stop()


def _run_qwen_image(
    *,
    hb: _Heartbeat,
    prompt: str,
    negative: str,
    width: int,
    height: int,
    seed: int,
    panel_id: str,
    output_basename: str,
    dest_path: str,
    job_id: str,
) -> dict:
    hb.set_phase("submitting")
    graph = qwen_image_txt2img_graph(prompt, negative, width, height, seed)
    r = requests.post(f"{COMFY_URL}/prompt", json={"prompt": graph}, timeout=30)
    r.raise_for_status()
    pr = r.json()
    if pr.get("error"):
        raise RuntimeError(f"ComfyUI /prompt error: {pr['error']}")
    prompt_id = str(pr.get("prompt_id") or "")
    if not prompt_id:
        raise RuntimeError(f"no prompt_id in ComfyUI response: {pr}")
    hb.set_phase("rendering", prompt_id=prompt_id)

    entry = _poll_history(prompt_id, max_wait_s=900.0, interval=2.0)
    filename = None
    for node_out in entry.get("outputs", {}).values():
        for img in node_out.get("images", []) or []:
            filename = img.get("filename")
            if filename:
                break
        if filename:
            break
    if not filename:
        raise RuntimeError(f"no SaveImage output for prompt_id={prompt_id}")

    hb.set_phase("copying_output", prompt_id=prompt_id)
    dst = _resolve_dest(dest_path, output_basename, panel_id)
    _land_png(filename, dst)
    _assert_blob_gate(dst)
    hb.set_phase("done", prompt_id=prompt_id)
    return {
        "status": "COMPLETED",
        "prompt_id": prompt_id,
        "output": str(dst),
        "workload": WORKLOAD,
        "panel_id": panel_id,
    }
