#!/usr/bin/env python3
"""Direct Qwen-Image ComfyUI render helper (operator-present; Pearl Star GPU)."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

DEFAULT_COMFY_URL = os.environ.get("COMFYUI_URL", "http://100.92.68.74:8188")
POLL_INTERVAL_S = 3.0
POLL_TIMEOUT_S = float(os.environ.get("QUEUE_POLL_TIMEOUT_SEC", "900"))

_NEG_SUFFIX = (
    "text, words, letters, captions, watermark, signature, signs, writing, "
    "typography, text characters, font, lettering, logos, subtitles, calligraphy"
)


def qwen_image_txt2img_graph(
    prompt: str, negative: str, width: int, height: int, seed: int
) -> dict:
    """Qwen-Image txt2img without PuLID (bank layers / env plates)."""
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
                "steps": 24,
                "cfg": 4.0,
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


def _post_json(url: str, payload: dict, timeout: int = 30) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _get_json(url: str, timeout: int = 30) -> dict:
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _get_bytes(url: str, timeout: int = 120) -> bytes:
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return resp.read()


def render_qwen_panel_png(
    *,
    prompt: str,
    negative: str,
    width: int,
    height: int,
    seed: int,
    out_path: Path,
    comfy_url: str | None = None,
) -> dict[str, Any]:
    """Submit one Qwen panel to ComfyUI; write PNG bytes to *out_path*."""
    base = (comfy_url or DEFAULT_COMFY_URL).rstrip("/")
    graph = qwen_image_txt2img_graph(prompt, negative, width, height, seed)
    pr = _post_json(f"{base}/prompt", {"prompt": graph})
    if pr.get("error"):
        raise RuntimeError(f"ComfyUI error: {pr['error']}")
    prompt_id = str(pr.get("prompt_id") or "")
    if not prompt_id:
        raise RuntimeError(f"no prompt_id: {pr}")

    deadline = time.time() + POLL_TIMEOUT_S
    filename = None
    while time.time() < deadline:
        try:
            hist = _get_json(f"{base}/history/{prompt_id}")
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                time.sleep(POLL_INTERVAL_S)
                continue
            raise
        entry = hist.get(prompt_id) or {}
        if entry.get("status", {}).get("completed"):
            for node_out in entry.get("outputs", {}).values():
                for img in node_out.get("images", []) or []:
                    filename = img.get("filename")
                    if filename:
                        break
                if filename:
                    break
            break
        time.sleep(POLL_INTERVAL_S)

    if not filename:
        raise RuntimeError(f"timeout waiting for ComfyUI prompt_id={prompt_id}")

    sub = urllib.parse.urlencode({"filename": filename, "type": "output"})
    data = _get_bytes(f"{base}/view?{sub}")
    if len(data) < 10_000:
        raise RuntimeError(f"ComfyUI returned tiny payload ({len(data)} bytes)")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(data)
    return {"prompt_id": prompt_id, "filename": filename, "bytes": len(data)}
