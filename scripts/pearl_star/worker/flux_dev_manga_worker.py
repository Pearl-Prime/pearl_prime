"""Pearl Star Job Queue V1 — flux-dev H1=A manga panel worker.

One job = one manga panel (1080×1920, flux1-dev-fp8, 28 steps, cfg 3.5).
Spec: docs/specs/MANGA_PRODUCTION_OPERATIONAL_V1_SPEC.md §5; stall 120s/180s.
"""

from __future__ import annotations

import os
import shutil
import time
from pathlib import Path

import requests

from app import app
from flux_schnell_worker import COMFY_OUTPUT, COMFY_URL, _Heartbeat, _poll_history

WORKLOAD = "t2i_flux_dev_h1a"
STALL_WARN_S = 120.0
STALL_KILL_S = 180.0
EXPECTED_TOTAL_S = 50.0
DEFAULT_W, DEFAULT_H = 1080, 1920


def _flux_dev_h1a_graph(
    prompt: str, negative: str, width: int, height: int, seed: int
) -> dict:
    neg = (
        f"{negative}, text, words, letters, captions, watermark, signature, signs, "
        "writing, typography, text characters, font, lettering, logos, subtitles, calligraphy"
    )
    return {
        "1": {"class_type": "CheckpointLoaderSimple",
              "inputs": {"ckpt_name": "flux1-dev-fp8.safetensors"}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": neg, "clip": ["1", 1]}},
        "4": {"class_type": "EmptyLatentImage",
              "inputs": {"width": width, "height": height, "batch_size": 1}},
        "5": {"class_type": "KSampler",
              "inputs": {"seed": seed, "steps": 28, "cfg": 3.5,
                         "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": 1.0,
                         "model": ["1", 0], "positive": ["2", 0],
                         "negative": ["3", 0], "latent_image": ["4", 0]}},
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "SaveImage",
              "inputs": {"filename_prefix": "manga_panel", "images": ["6", 0]}},
    }


def _resolve_dest(
    dest_path: str, output_basename: str, panel_id: str
) -> Path:
    if dest_path:
        return Path(dest_path)
    out_root = Path(os.environ.get("PS_OUTPUT_DIR", "/var/lib/pearl-star/output"))
    name = output_basename or panel_id or "panel"
    return out_root / f"{name}.png"


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


@app.task(name="t2i_flux_dev_h1a", queue="t2i", retry=1)
def t2i_flux_dev_h1a(
    prompt: str,
    negative: str = "",
    width: int = DEFAULT_W,
    height: int = DEFAULT_H,
    seed: int = 42,
    panel_id: str = "",
    output_basename: str = "",
    dest_path: str = "",
) -> dict:
    """Render one H1=A manga panel; land PNG at dest_path when provided."""
    job_id = os.environ.get("PROCRASTINATE_JOB_ID", panel_id or f"panel-{int(time.time())}")
    hb = _Heartbeat(
        job_id,
        expected_total_s=EXPECTED_TOTAL_S,
        stall_warn_at_s=STALL_WARN_S,
        stall_kill_at_s=STALL_KILL_S,
    )
    hb.start()
    try:
        hb.set_phase("submitting")
        graph = _flux_dev_h1a_graph(prompt, negative, width, height, seed)
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
        hb.set_phase("done", prompt_id=prompt_id)
        return {
            "status": "COMPLETED",
            "prompt_id": prompt_id,
            "output": str(dst),
            "workload": WORKLOAD,
            "panel_id": panel_id,
        }
    finally:
        hb.stop()
