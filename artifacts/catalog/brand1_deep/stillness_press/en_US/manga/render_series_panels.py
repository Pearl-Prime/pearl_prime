#!/usr/bin/env python3
"""Render stillness_press manga series 2 / 3 panels via Pearl Star ComfyUI.

Series 1 (What the Body Holds) was rendered via the V4 layered pipeline (needs
per-panel continuity_state YAMLs). Series 2 (The Night Before You Sleep) and 3
(Hands, Shoulders, Breath) ship as render-ready markdown panel scripts only.

This parses each script's `**Pn** — visual description.` lines, builds an
iyashikei FLUX prompt per panel (text-free imagery — lettering is composited
downstream), and renders each panel as a 1080x1920 WEBTOON-vertical PNG on
Pearl Star (flux1-schnell-fp8, 4-step). $0 (Pearl Star primary).

Per MANGA panel rule: NO dialogue/caption text in the render prompt (FLUX
hallucinates embedded text); the lettering layer is applied separately.

Usage:
  eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
  python3 render_series_panels.py --series 2
  python3 render_series_panels.py --series 3 --limit 10
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[7] if len(
    Path(__file__).resolve().parents) > 7 else Path.cwd()

SCRIPTS_DIR = Path(__file__).parent / "scripts"

SERIES = {
    "2": {
        "script": "series2_the_night_before_you_sleep_ep001.md",
        "out_subdir": "stillness_press_sleep_vol1/ep_001",
        "character_lock": (
            "Yuki — early 30s East-Asian woman, soft features, dark chin-length bob, "
            "oversized cream cardigan, tired gentle face"
        ),
        "palette": (
            "warm cream and amber lamplight against soft indigo night, very low "
            "contrast, 4 percent black fill"
        ),
    },
    "3": {
        "script": "series3_hands_shoulders_breath_ep001.md",
        "out_subdir": "stillness_press_somatic_vol1/ep_001",
        "character_lock": (
            "Mei — 28 East-Asian woman, short practical hair, glasses, layered "
            "neutral clothing, thoughtful guarded face softening over time"
        ),
        "palette": (
            "warm neutral daylight, sage and cream and soft wood tones, gentle "
            "afternoon light, 6 percent black fill"
        ),
    },
}

STYLE = (
    "seinen iyashikei manga panel, soft ink linework, light line weight, warm "
    "earth-toned watercolor wash, minimal screentone, generous negative space, "
    "Yokohama Kaidashi Kiko aesthetic, painterly continuity, contemplative stillness"
)
NEG = (
    "text, words, letters, captions, speech bubbles, watermark, signature, "
    "typography, lettering, calligraphy, font, subtitles, "
    "speed lines, dutch angle, exaggerated reaction, sweatdrops, concentration "
    "lines, chibi, neon, harsh shadows, 3d render, photorealistic, deformed "
    "hands, extra fingers, extra limbs, frame border"
)

# Panel line: "**P12** — *SILENT.* Close: her hand drifts ..."
PANEL_RE = re.compile(r"^\*\*P(\d+)\*\*\s*[—-]\s*(.+)$")


def parse_panels(script_path: Path) -> list[tuple[str, str]]:
    """Return [(panel_id, visual_description), ...] from a render-ready script.

    Strips the leading *SILENT.* / *TYPOGRAPHIC ONLY* directive and any inline
    bold directives; keeps the visual prose. Skips pure typographic cards.
    """
    panels: list[tuple[str, str]] = []
    for raw in script_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        m = PANEL_RE.match(line)
        if not m:
            continue
        num = int(m.group(1))
        desc = m.group(2).strip()
        # Drop a leading italic directive like *SILENT.* or *TYPOGRAPHIC ONLY*
        directive = ""
        dm = re.match(r"^\*([^*]+)\*\s*(.*)$", desc)
        if dm:
            directive = dm.group(1).strip().upper()
            desc = dm.group(2).strip()
        # Skip pure episode/typographic cards — no imagery to render
        if "TYPOGRAPHIC" in directive:
            continue
        # Strip any remaining markdown emphasis / POV labels noise
        desc = desc.replace("**", "").replace("*", "")
        if not desc:
            desc = "a quiet still moment, generous negative space"
        panels.append((f"ep001_{num:03d}", desc))
    return panels


def _comfy_url() -> str:
    url = os.environ.get("COMFYUI_URL", "").rstrip("/")
    if not url:
        sys.exit('COMFYUI_URL not set — run: eval "$(python3 scripts/ci/'
                 'load_integration_env_from_keychain.py)"')
    return url


def render_panel(panel_id: str, prompt: str, out_png: Path, *,
                 timeout: float = 300.0) -> Path:
    base = _comfy_url()
    seed = int(hashlib.sha256(panel_id.encode()).hexdigest(), 16) % (2**32)
    wf = {
        "1": {"class_type": "CheckpointLoaderSimple",
              "inputs": {"ckpt_name": "flux1-schnell-fp8.safetensors"}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["1", 1]}},
        "4": {"class_type": "EmptyLatentImage",
              "inputs": {"width": 1080, "height": 1920, "batch_size": 1}},
        "5": {"class_type": "KSampler",
              "inputs": {"seed": seed, "steps": 4, "cfg": 1.0, "sampler_name": "euler",
                         "scheduler": "simple", "denoise": 1.0, "model": ["1", 0],
                         "positive": ["2", 0], "negative": ["3", 0], "latent_image": ["4", 0]}},
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "SaveImage",
              "inputs": {"filename_prefix": panel_id, "images": ["6", 0]}},
    }
    req = urllib.request.Request(
        base + "/prompt", data=json.dumps({"prompt": wf}).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    pid = json.loads(urllib.request.urlopen(req, timeout=60).read())["prompt_id"]
    t0 = time.time()
    out = None
    while time.time() - t0 < timeout:
        h = json.loads(urllib.request.urlopen(base + f"/history/{pid}", timeout=30).read())
        if pid in h and h[pid].get("outputs"):
            for _nid, no in h[pid]["outputs"].items():
                if no.get("images"):
                    out = no["images"][0]
                    break
            if out:
                break
        time.sleep(2)
    if not out:
        raise TimeoutError(f"no output for {panel_id} after {timeout}s")
    url = (base + f"/view?filename={out['filename']}"
           f"&subfolder={out.get('subfolder', '')}&type={out.get('type', 'output')}")
    data = urllib.request.urlopen(url, timeout=60).read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"{panel_id}: invalid PNG")
    out_png.parent.mkdir(parents=True, exist_ok=True)
    out_png.write_bytes(data)
    return out_png


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--series", required=True, choices=list(SERIES.keys()))
    ap.add_argument("--limit", type=int, help="cap number of panels (smoke)")
    ap.add_argument("--out-root", type=Path,
                    default=Path(__file__).parent.parent.parent.parent.parent
                    / "manga" / "rendered",
                    help="output root for rendered panels")
    ap.add_argument("--resume", action="store_true", default=True)
    args = ap.parse_args()

    cfg = SERIES[args.series]
    script_path = SCRIPTS_DIR / cfg["script"]
    panels = parse_panels(script_path)
    if args.limit:
        panels = panels[:args.limit]

    out_dir = (Path(__file__).parent / "rendered" / cfg["out_subdir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    progress = out_dir / "RENDER_PROGRESS.tsv"
    if not progress.is_file():
        progress.write_text("panel_id\tstatus\tbytes\tseconds\n", encoding="utf-8")

    print(f"=== Series {args.series}: {len(panels)} panels -> {out_dir} ===")
    done = fail = skip = 0
    t_all = time.time()
    for panel_id, desc in panels:
        out_png = out_dir / f"{panel_id}.png"
        if args.resume and out_png.is_file() and out_png.stat().st_size > 10_000:
            print(f"  [skip] {panel_id} (cached)")
            skip += 1
            continue
        prompt = (f"{desc}. Character: {cfg['character_lock']}. {cfg['palette']}. {STYLE}")
        # FLUX/CLIP truncates ~77 tokens of *weighting* but accepts long prose; trim very long
        prompt = prompt[:900]
        t0 = time.time()
        try:
            render_panel(panel_id, prompt, out_png)
            sz = out_png.stat().st_size
            dt = time.time() - t0
            with progress.open("a", encoding="utf-8") as f:
                f.write(f"{panel_id}\tok\t{sz}\t{dt:.1f}\n")
            print(f"  [ok]   {panel_id}  {sz} bytes  {dt:.1f}s")
            done += 1
        except Exception as e:
            with progress.open("a", encoding="utf-8") as f:
                f.write(f"{panel_id}\tfail\t0\t0\n")
            print(f"  [FAIL] {panel_id}: {e}")
            fail += 1
    print(f"\nSeries {args.series} done: {done} rendered, {skip} cached, {fail} failed "
          f"({time.time()-t_all:.0f}s total)")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
