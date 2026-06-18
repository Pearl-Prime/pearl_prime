#!/usr/bin/env python3
"""GPU iyashikei panel renderer for the Devotion manga — Pearl Star ComfyUI / FLUX.1-schnell.

Drop-in replacement for ``scripts/manga/render_devotion_panels_local.py`` (the
deterministic PIL stand-in). Same CLI, same outputs:

  * writes ``panel_images/<panel_id>.png`` for every compiled panel prompt, and
  * writes ``replay/map.json`` (panel_id -> ABSOLUTE png path) that the existing
    ``FixtureReplayImageBackend`` (``--backend replay``) feeds into the rest of
    the resumable manga DAG (chapter_image_gen -> ... -> chapter_qc).

The ONLY thing that swaps versus the PIL stand-in is where the pixels come from:
each panel's *already-compiled* prompt + negative_prompt (from the chapter_visual
stage, style_id=cozy_iyashikei, with the iyashikei art direction, drawing
traditions and individuation tags baked in) is submitted straight to the live
Pearl Star ComfyUI server, which renders it on the RTX GPU.

Backend / licence (locked decisions — docs/sessions/AUTONOMOUS_MANGA_RUN_2026-06-17.md
D3, CLAUDE.md tier policy):
  * Model = ``flux1-schnell-fp8.safetensors`` — FLUX.1-schnell, Apache-2.0,
    commercial-clean. NEVER flux1-dev (non-commercial). Hardcoded below.
  * Sampler envelope = steps=4, cfg=1.0, euler/simple — the only valid schnell
    envelope (faithful to scripts/pearl_star/worker/flux_schnell_worker.py and
    scripts/image_generation/comfyui_workflows/flux_txt2img_manga.json).
  * Tier 1 (operator-present); Pearl Star ComfyUI = free + local GPU; no paid
    LLM/image API of any kind.

Per-panel canvas size follows the authored camera family (same _DIMS map the PIL
stand-in used) so the downstream FRAME / webtoon composer sees the same panel
aspect ratios it was tuned against — wide establishing shots stay wide, close-ups
stay tall. All dims are multiples of 16 (FLUX requirement).

  COMFYUI_URL=http://100.92.68.74:8188 \
  PYTHONPATH=. python3 scripts/manga/render_devotion_panels_gpu.py \
      --workspace artifacts/manga/devotion_en_01_run \
      --out-subdir panel_images --replay-map replay/map.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

# ── Licence-safe model + schnell envelope (DO NOT change to flux1-dev) ───────
CKPT_NAME = "flux1-schnell-fp8.safetensors"  # FLUX.1-schnell, Apache-2.0
SCHNELL_STEPS = 4
SCHNELL_CFG = 1.0
SCHNELL_SAMPLER = "euler"
SCHNELL_SCHEDULER = "simple"

DEFAULT_COMFY_URL = os.environ.get("COMFYUI_URL", "http://100.92.68.74:8188")
DEFAULT_SEED_BASE = 42
POLL_INTERVAL_S = 2.0
POLL_TIMEOUT_S = 300.0      # 5 min / panel ceiling
PANEL_RETRIES = 2           # transient ComfyUI/network failures
MIN_PNG_BYTES = 10_000      # a real FLUX panel is hundreds of KB; smaller = error body

# Per-camera canvas (px) — identical to render_devotion_panels_local.py _DIMS so
# the layout/compose engines see unchanged aspect ratios. All multiples of 16.
_DIMS = {
    "establishing-wide": (1024, 576),
    "wide": (1024, 576),
    "medium": (768, 768),
    "over-shoulder": (768, 768),
    "close-up": (640, 720),
    "insert": (640, 640),
    "environmental-insert": (768, 560),
}
_DEFAULT_DIM = (768, 768)

# Appended to every panel negative so the ART carries NO text — bubbles/captions
# are composited later by the lettering/bubble stages (two-stage rule). Mirrors
# flux_txt2img_manga.json + flux_schnell_worker._flux_schnell_graph.
_NEG_TEXT_SUFFIX = (
    "text, words, letters, captions, watermark, signature, writing, "
    "typography, font, lettering, logos, subtitles, speech bubble"
)

# Camera family -> shot-type phrase that leads the composed prompt (FLUX weights
# leading tokens most). Mirrors the camera semantics the PIL stand-in encoded via
# its per-camera dims + figure scale.
_SHOT_PHRASE = {
    "establishing-wide": "wide establishing shot, full environment, scenery",
    "wide": "wide shot, full scene",
    "medium": "medium shot",
    "over-shoulder": "over-the-shoulder shot",
    "close-up": "close-up",
    "insert": "close insert detail",
    "environmental-insert": "environmental insert, scenery detail",
}
# Cameras the PIL stand-in renders as pure scenery (no figure). Force "no people"
# so FLUX paints the authored environment, not a default portrait.
_SCENERY_CAMERAS = {"environmental-insert"}
_SCENERY_NEG = "person, people, face, portrait, character, human figure, crowd"


def _clean_action(action: str, limit: int = 340) -> str:
    """Collapse whitespace + cap length of the authored scene direction."""
    a = " ".join(str(action or "").split()).strip()
    # Drop the production aside some beats carry so it does not become art.
    a = a.replace("Final panel:", "").strip()
    return a[:limit].rsplit(" ", 1)[0] if len(a) > limit else a


def _style_tail(compiled_prompt: str) -> str:
    """The compiled iyashikei art-direction tail, minus its generic camera noise.

    Keeps the style / drawing-tradition / individuation / ITE tokens the task
    points at, but strips the ``mixed: close-up, medium, wide`` aside so it does
    not fight the panel's actual shot-type phrase.
    """
    return compiled_prompt.replace("mixed: close-up, medium, wide, ", "").strip()


def _compose_positive(compiled_prompt: str, camera: str, action: str) -> str:
    """Scene (authored) leads; compiled iyashikei art-direction tails."""
    cam = str(camera or "").strip().lower()
    scene = _clean_action(action)
    shot = _SHOT_PHRASE.get(cam, "medium shot")
    lead = f"{scene}, {shot}" if scene else shot
    if cam in _SCENERY_CAMERAS:
        lead = f"{lead}, no people, empty of figures"
    return f"{lead} | {_style_tail(compiled_prompt)}"


def _compose_negative(panel_negative: str, camera: str) -> str:
    neg = (panel_negative or "").strip()
    if str(camera or "").strip().lower() in _SCENERY_CAMERAS:
        neg = f"{neg}, {_SCENERY_NEG}" if neg else _SCENERY_NEG
    return neg


def _flux_schnell_graph(prompt: str, negative: str, width: int, height: int, seed: int) -> dict:
    """ComfyUI API graph for flux1-schnell-fp8 (4 / 1.0 / euler / simple)."""
    neg = f"{negative.strip()}, {_NEG_TEXT_SUFFIX}" if negative.strip() else _NEG_TEXT_SUFFIX
    return {
        "1": {"class_type": "CheckpointLoaderSimple",
              "inputs": {"ckpt_name": CKPT_NAME}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": neg, "clip": ["1", 1]}},
        "4": {"class_type": "EmptyLatentImage",
              "inputs": {"width": width, "height": height, "batch_size": 1}},
        "5": {"class_type": "KSampler",
              "inputs": {"seed": seed, "steps": SCHNELL_STEPS, "cfg": SCHNELL_CFG,
                         "sampler_name": SCHNELL_SAMPLER, "scheduler": SCHNELL_SCHEDULER,
                         "denoise": 1.0, "model": ["1", 0], "positive": ["2", 0],
                         "negative": ["3", 0], "latent_image": ["4", 0]}},
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "SaveImage",
              "inputs": {"filename_prefix": "devotion_panel", "images": ["6", 0]}},
    }


def _post_json(url: str, payload: dict, timeout: int = 30) -> dict:
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _get_json(url: str, timeout: int = 30) -> dict:
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _get_bytes(url: str, timeout: int = 120) -> bytes:
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return resp.read()


def _camera_dims(camera: str) -> tuple[int, int]:
    return _DIMS.get(str(camera or "").strip().lower(), _DEFAULT_DIM)


def _render_one(comfy_url: str, panel: dict, camera: str, action: str, seed: int) -> bytes:
    """Submit one panel to ComfyUI, poll, return the PNG bytes. Raises on failure."""
    compiled = (panel.get("prompt") or panel.get("flux_prompt") or "").strip()
    if not compiled:
        raise ValueError(f"{panel.get('panel_id')}: empty compiled prompt")
    positive = _compose_positive(compiled, camera, action)
    negative = _compose_negative(panel.get("negative_prompt") or "", camera)
    w, h = _camera_dims(camera)
    graph = _flux_schnell_graph(positive, negative, w, h, seed)

    submit = _post_json(f"{comfy_url}/prompt", {"prompt": graph})
    if submit.get("error"):
        raise RuntimeError(f"ComfyUI /prompt error: {submit['error']}")
    prompt_id = submit.get("prompt_id")
    if not prompt_id:
        raise RuntimeError(f"ComfyUI returned no prompt_id: {submit}")

    deadline = time.time() + POLL_TIMEOUT_S
    while time.time() < deadline:
        time.sleep(POLL_INTERVAL_S)
        try:
            history = _get_json(f"{comfy_url}/history/{prompt_id}")
        except urllib.error.URLError:
            continue
        entry = history.get(prompt_id) if isinstance(history, dict) else None
        if not isinstance(entry, dict):
            continue
        for node_out in (entry.get("outputs") or {}).values():
            for img in node_out.get("images", []) or []:
                fn = img.get("filename")
                if not fn:
                    continue
                view = (f"{comfy_url}/view?" + urllib.parse.urlencode(
                    {"filename": fn, "subfolder": img.get("subfolder", ""),
                     "type": img.get("type", "output")}))
                png = _get_bytes(view)
                if len(png) < MIN_PNG_BYTES or png[:8] != b"\x89PNG\r\n\x1a\n":
                    raise RuntimeError(f"bad PNG for {panel.get('panel_id')} "
                                       f"({len(png)} bytes, sig={png[:8]!r})")
                return png
    raise TimeoutError(f"{panel.get('panel_id')}: poll timeout after {POLL_TIMEOUT_S:.0f}s")


def render_panel(comfy_url: str, panel: dict, camera: str, action: str, seed: int, out_path: Path) -> tuple[int, int]:
    """Render one panel with bounded retries; write PNG; return (w, h)."""
    last_err = ""
    for attempt in range(PANEL_RETRIES + 1):
        try:
            png = _render_one(comfy_url, panel, camera, action, seed)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(png)
            # width/height straight from the IHDR we just wrote
            w = int.from_bytes(png[16:20], "big")
            h = int.from_bytes(png[20:24], "big")
            return w, h
        except Exception as exc:  # noqa: BLE001 — retry transient ComfyUI/network errors
            last_err = str(exc)
            if attempt < PANEL_RETRIES:
                time.sleep(2.0 * (attempt + 1))
    raise RuntimeError(f"{panel.get('panel_id')}: failed after {PANEL_RETRIES + 1} attempts — {last_err}")


def _authored_panels(ws: Path) -> dict[str, tuple[str, str]]:
    """panel_id -> (camera, action), read from the writer handoff.

    The compiled panel_prompts.json prompt is a scene-AGNOSTIC iyashikei style
    block (identical across panels); the authored ``action`` is where each beat's
    scene lives. We compose the two — exactly the data split the PIL stand-in used.
    """
    script_path = ws / "chapter_script_writer_handoff.json"
    out: dict[str, tuple[str, str]] = {}
    if script_path.is_file():
        script = json.loads(script_path.read_text())
        for page in script.get("pages") or []:
            for panel in page.get("panels") or []:
                pid = str(panel.get("panel_id"))
                out[pid] = (str(panel.get("camera") or ""), str(panel.get("action") or ""))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Render Devotion iyashikei panels on Pearl Star GPU (FLUX.1-schnell).")
    ap.add_argument("--workspace", type=Path, required=True)
    ap.add_argument("--out-subdir", default="panel_images")
    ap.add_argument("--replay-map", default="replay/map.json",
                    help="relative path under workspace for the panel_id->png map")
    ap.add_argument("--comfy-url", default=DEFAULT_COMFY_URL,
                    help=f"ComfyUI base URL (default: {DEFAULT_COMFY_URL})")
    ap.add_argument("--seed-base", type=int, default=DEFAULT_SEED_BASE)
    ap.add_argument("--only-panel", default=None, help="render just this panel_id (smoke test)")
    ap.add_argument("--skip-existing", action="store_true",
                    help="skip panels whose PNG already exists (>%d bytes)" % MIN_PNG_BYTES)
    ap.add_argument("--dry-run", action="store_true",
                    help="validate prompts + dims; submit nothing to the GPU")
    args = ap.parse_args()

    ws = args.workspace.resolve()
    pp_path = ws / "panel_prompts.json"
    if not pp_path.is_file():
        print(f"missing panel_prompts.json in {ws}", file=sys.stderr)
        return 1

    pp = json.loads(pp_path.read_text())
    panels = pp.get("panels") or pp.get("prompts") or []
    if not panels:
        print(f"no panels in {pp_path}", file=sys.stderr)
        return 1
    authored = _authored_panels(ws)

    if args.only_panel:
        panels = [p for p in panels if str(p.get("panel_id")) == args.only_panel]
        if not panels:
            print(f"panel_id {args.only_panel!r} not found in {pp_path}", file=sys.stderr)
            return 1

    out_dir = ws / args.out_subdir
    comfy_url = args.comfy_url.rstrip("/")
    print(f"GPU render: {len(panels)} panel(s) · model={CKPT_NAME} · comfy={comfy_url}", file=sys.stderr)

    rel_map: dict[str, str] = {}
    ok = fail = skipped = 0
    for i, panel in enumerate(panels):
        pid = str(panel.get("panel_id"))
        camera, action = authored.get(pid, ("", ""))
        w, h = _camera_dims(camera)
        seed = args.seed_base + i
        out_path = out_dir / f"{pid}.png"
        rel_map[pid] = str(Path(args.out_subdir) / f"{pid}.png")

        if args.dry_run:
            scene = _clean_action(action)[:60]
            print(f"  [dry] {pid:8s} {camera or '-':18s} {w}x{h} seed={seed} scene='{scene}'", file=sys.stderr)
            continue
        if args.skip_existing and out_path.is_file() and out_path.stat().st_size > MIN_PNG_BYTES:
            print(f"  SKIP {pid} (exists)", file=sys.stderr)
            skipped += 1
            continue
        t0 = time.time()
        try:
            rw, rh = render_panel(comfy_url, panel, camera, action, seed, out_path)
            dt = time.time() - t0
            print(f"  OK   {pid:8s} {rw}x{rh} {out_path.stat().st_size // 1024}KB {dt:4.1f}s ({i + 1}/{len(panels)})", file=sys.stderr)
            ok += 1
        except Exception as exc:  # noqa: BLE001
            print(f"  FAIL {pid}: {exc}", file=sys.stderr)
            fail += 1

    if args.dry_run:
        print(f"dry-run: {len(panels)} panels validated", file=sys.stderr)
        return 0

    if fail:
        print(f"\n{fail} panel(s) failed — replay map NOT written (DAG would render stale/missing art)", file=sys.stderr)
        return 1

    # replay map: absolute panel paths (location-robust), matching the PIL stand-in.
    map_path = ws / args.replay_map
    map_path.parent.mkdir(parents=True, exist_ok=True)
    abs_map = {pid: str((ws / rel).resolve()) for pid, rel in rel_map.items()}
    if args.only_panel:
        # smoke test: don't clobber the full map with a single entry
        print(f"\nsmoke OK: {ok} panel · (replay map left intact for --only-panel)", file=sys.stderr)
        return 0
    map_path.write_text(json.dumps(abs_map, indent=2) + "\n", encoding="utf-8")
    print(f"\nrendered {ok} GPU panels -> {out_dir}", file=sys.stderr)
    print(f"wrote replay map -> {map_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
