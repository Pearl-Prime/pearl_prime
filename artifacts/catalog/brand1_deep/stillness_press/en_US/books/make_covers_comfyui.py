#!/usr/bin/env python3
"""Generate stillness_press KDP covers with REAL ComfyUI iyashikei imagery.

Two-stage cover rule (COVER-TEXT-OVERLAY / COVER-REGISTRY-01):
  Stage 1 (FLUX on Pearl Star): renders iyashikei imagery only — NO title,
      NO author, NO subtitle in the prompt (FLUX hallucinates embedded
      typography otherwise — see brand_cover_art_specs.yaml authoring rules).
  Stage 2 (PIL): composites the title / subtitle / author / publisher text
      over the rendered imagery, in the stillness_press palette.

This SUPERSEDES make_covers.py (which produced a PIL gradient because Pearl
Star was unreachable in the prior session). The text-compositing layer is
identical to make_covers.py; only the background is now a real render.

Backend: ComfyUI on Pearl Star via COMFYUI_URL (load Keychain env first:
  eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)").
Workflow: flux1-schnell-fp8 txt2img (4-step). $0 (Pearl Star primary).

Storage note: brand1_deep cover PNGs ship as RAW git blobs (see .gitattributes
lines 84-87: `artifacts/catalog/brand1_deep/**/*.png -filter` — LFS budget is
exhausted), so they MUST stay under the no-binary-blobs.yml 1 MB cap. Stage 2
quantizes the final composite to land under --max-bytes (default 950 KB) while
keeping the soft watercolor palette intact.

Usage:
  eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
  python3 make_covers_comfyui.py            # render all 4
  python3 make_covers_comfyui.py --slug anxiety_gen_z_professionals
  python3 make_covers_comfyui.py --imagery-only   # stage 1 only (debug)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1600, 2560  # KDP storefront portrait (5:8)

# iyashikei palette (mirrors make_covers.py / panel_prompts.json visual grammar)
CREAM = (244, 237, 224)
DAWN_GOLD = (232, 213, 178)
SAGE = (150, 165, 142)
TERRACOTTA = (196, 144, 116)
JADE = (96, 138, 120)
INK = (58, 54, 48)
SOFT_INK = (96, 90, 80)

SERIF = "/System/Library/Fonts/Supplemental/Georgia.ttf"
SERIF_BOLD = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
SERIF_ITALIC = "/System/Library/Fonts/Supplemental/Georgia Italic.ttf"

# Stage-1 FLUX imagery prompts — TEXT-FREE. Each describes the emotional
# throughline / palette / composition WITHOUT quoting any title.
# Composition leaves the upper ~55% calmer (the typography slot).
BASE_NEG = (
    "text, letters, words, watermark, signature, typography, logo, caption, "
    "title text, embedded title, lettering, calligraphy, signage, subtitles, "
    "font glyphs, latin alphabet, writing, characters, harsh shadows, "
    "neon, 3d render, photorealistic, deformed hands, extra fingers, frame, border"
)
STYLE = (
    "seinen iyashikei manga illustration, soft ink linework, warm earth-toned "
    "watercolor wash, slate-and-gold palette, soft natural light, paper texture "
    "grain, generous negative space, Studio Ghibli meets Yokohama Kaidashi Kiko, "
    "contemplative stillness, no people in upper third"
)

BOOKS = [
    {
        "slug": "anxiety_gen_z_professionals",
        "title": "The Room Is Safe",
        "subtitle": "A Body-First Guide to Anxiety for People Who Can't Switch Off",
        # imagery: a safe, quiet interior — a still room, warm low light
        "imagery": (
            "a quiet sunlit room seen from within, a single low window with soft "
            "morning light pooling on a wooden floor, a floor cushion, a small "
            "plant, calm safe enclosed space, lower-half focus, "
        ),
    },
    {
        "slug": "sleep_anxiety_midlife_women",
        "title": "The Hour That Won't Let Go",
        "subtitle": "A Somatic Guide to the 3 A.M. Mind for Women Tired of Being Tired",
        "imagery": (
            "a dim bedroom at deep night lit only by one warm lamp in the corner, "
            "an empty made bed, soft amber glow against indigo dark, profound quiet, "
            "the long hour before dawn, lower-half focus, "
        ),
    },
    {
        "slug": "overthinking_millennial_women_professionals",
        "title": "The Fourth Draft of a Text Message",
        "subtitle": "A Contemplative Guide to Quieting the Mind That Won't Stop Rehearsing",
        "imagery": (
            "still water surface settling after ripples, faint concentric rings "
            "fading to a perfect calm mirror reflecting a pale dawn sky, reeds at "
            "the edge, the mind growing quiet, lower-half focus, "
        ),
    },
    {
        "slug": "anxiety_tech_finance_burnout",
        "title": "The Dashboard in Your Chest",
        "subtitle": "A Body-First Guide to Anxiety for High-Output People Running on Empty",
        "imagery": (
            "a single candle flame in soft darkness, warmth spreading outward into "
            "a gentle golden glow, the body's quiet center, rest after overdrive, "
            "muted slate background warming to gold, lower-half focus, "
        ),
    },
]


# ── Stage 1: ComfyUI FLUX render ────────────────────────────────────────────

def _comfy_url() -> str:
    url = os.environ.get("COMFYUI_URL", "").rstrip("/")
    if not url:
        sys.exit("COMFYUI_URL not set — run: eval \"$(python3 scripts/ci/"
                 "load_integration_env_from_keychain.py)\"")
    return url


def _seed(slug: str) -> int:
    return int(hashlib.sha256(("cover_" + slug).encode()).hexdigest(), 16) % (2**32)


def render_imagery(slug: str, positive: str, out_png: Path, *,
                   width: int = 1024, height: int = 1664, timeout: float = 300.0) -> Path:
    """Render text-free iyashikei imagery via Pearl Star FLUX (schnell). Returns path."""
    base = _comfy_url()
    seed = _seed(slug)
    wf = {
        "1": {"class_type": "CheckpointLoaderSimple",
              "inputs": {"ckpt_name": "flux1-schnell-fp8.safetensors"}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": positive, "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": BASE_NEG, "clip": ["1", 1]}},
        "4": {"class_type": "EmptyLatentImage",
              "inputs": {"width": width, "height": height, "batch_size": 1}},
        "5": {"class_type": "KSampler",
              "inputs": {"seed": seed, "steps": 4, "cfg": 1.0, "sampler_name": "euler",
                         "scheduler": "simple", "denoise": 1.0, "model": ["1", 0],
                         "positive": ["2", 0], "negative": ["3", 0], "latent_image": ["4", 0]}},
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "SaveImage",
              "inputs": {"filename_prefix": f"cover_{slug}", "images": ["6", 0]}},
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
        raise TimeoutError(f"no output for {slug} after {timeout}s")
    url = (base + f"/view?filename={out['filename']}"
           f"&subfolder={out.get('subfolder', '')}&type={out.get('type', 'output')}")
    data = urllib.request.urlopen(url, timeout=60).read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"{slug}: not a valid PNG")
    out_png.parent.mkdir(parents=True, exist_ok=True)
    out_png.write_bytes(data)
    print(f"  [stage1] {slug}: rendered {len(data)} bytes (seed={seed}, {time.time()-t0:.1f}s)")
    return out_png


# ── Stage 2: PIL typography composite ────────────────────────────────────────

def wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _save_under_cap(img: Image.Image, out_path: Path, max_bytes: int) -> int:
    """Save PNG, quantizing palette down until it fits under max_bytes.

    brand1_deep covers are raw git blobs (not LFS) so must stay < 1 MB cap.
    Soft watercolor imagery quantizes cleanly; we step the palette down only
    as far as needed to fit.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # First try full-color optimized.
    img.save(out_path, "PNG", optimize=True)
    if out_path.stat().st_size <= max_bytes:
        return out_path.stat().st_size
    rgb = img.convert("RGB")
    for colors in (256, 192, 128, 96, 64, 48, 32):
        q = rgb.quantize(colors=colors, method=Image.MEDIANCUT, dither=Image.FLOYDSTEINBERG)
        q.save(out_path, "PNG", optimize=True)
        if out_path.stat().st_size <= max_bytes:
            return out_path.stat().st_size
    return out_path.stat().st_size  # smallest we got


def composite_cover(imagery_png: Path, title: str, subtitle: str, author: str,
                    publisher: str, out_path: Path, *, max_bytes: int = 950_000) -> Path:
    """Composite stillness_press typography over rendered imagery (stage 2)."""
    img = Image.open(imagery_png).convert("RGB").resize((W, H), Image.LANCZOS)

    # Warm the top into a readable typography field: blend a soft cream→gold
    # gradient over the upper region so title text reads at thumbnail scale,
    # while letting the rendered imagery show through the lower half.
    overlay = Image.new("RGB", (W, H), CREAM)
    grad = Image.new("L", (1, H), 0)
    gpx = grad.load()
    for y in range(H):
        t = y / (H - 1)
        # opaque-ish cream at top (0.0..0.80), fading to fully transparent by 62%
        a = max(0.0, 0.82 * (1.0 - min(t / 0.62, 1.0)))
        gpx[0, y] = int(a * 255)
    mask = grad.resize((W, H))
    img = Image.composite(overlay, img, mask)

    d = ImageDraw.Draw(img)

    # jade through-line rule (manga visual through-line motif)
    d.line([(W // 2 - 90, 360), (W // 2 + 90, 360)], fill=JADE, width=6)

    margin = 150
    max_w = W - 2 * margin

    # Title
    title_font = ImageFont.truetype(SERIF_BOLD, 132)
    title_lines = wrap(d, title.upper(), title_font, max_w)
    if len(title_lines) > 3:
        title_font = ImageFont.truetype(SERIF_BOLD, 104)
        title_lines = wrap(d, title.upper(), title_font, max_w)
    y = 470
    for ln in title_lines:
        lw = d.textlength(ln, font=title_font)
        # soft drop for legibility over imagery
        d.text(((W - lw) / 2 + 3, y + 3), ln, font=title_font, fill=(244, 237, 224))
        d.text(((W - lw) / 2, y), ln, font=title_font, fill=INK)
        y += title_font.size + 22

    # Subtitle
    y += 50
    sub_font = ImageFont.truetype(SERIF_ITALIC, 52)
    for ln in wrap(d, subtitle, sub_font, max_w - 60):
        lw = d.textlength(ln, font=sub_font)
        d.text(((W - lw) / 2, y), ln, font=sub_font, fill=TERRACOTTA)
        y += sub_font.size + 16

    # Author (lower third) — sits over imagery, add subtle plate
    auth_font = ImageFont.truetype(SERIF, 70)
    aw = d.textlength(author, font=auth_font)
    plate = Image.new("RGBA", (int(aw) + 80, 110), (244, 237, 224, 150))
    plate = plate.filter(ImageFilter.GaussianBlur(8))
    img.paste(Image.new("RGB", plate.size, CREAM),
              (int((W - aw) / 2 - 40), 2105), plate)
    d = ImageDraw.Draw(img)
    d.text(((W - aw) / 2, 2120), author, font=auth_font, fill=INK)

    # Publisher (footer)
    pub_font = ImageFont.truetype(SERIF, 40)
    pw = d.textlength(publisher.upper(), font=pub_font)
    d.text(((W - pw) / 2, 2360), publisher.upper(), font=pub_font, fill=SOFT_INK)

    final_bytes = _save_under_cap(img, out_path, max_bytes)
    img.info["_final_bytes"] = final_bytes  # noqa: (informational)
    return out_path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", help="render only this slug")
    ap.add_argument("--imagery-only", action="store_true", help="stage 1 only")
    ap.add_argument("--author", default="Ahjan")
    ap.add_argument("--publisher", default="Stillness Press")
    ap.add_argument("--max-bytes", type=int, default=950_000,
                    help="cap final cover size (raw-blob no-binary-blobs 1 MB limit)")
    ap.add_argument("--force", action="store_true", help="re-render imagery even if cached")
    args = ap.parse_args()

    out_dir = Path(__file__).parent / "covers"
    imagery_dir = Path(__file__).parent / "covers" / "_imagery"
    books = [b for b in BOOKS if (not args.slug or b["slug"] == args.slug)]

    done = 0
    for b in books:
        slug = b["slug"]
        positive = b["imagery"] + STYLE
        img_png = imagery_dir / f"imagery_{slug}.png"
        if img_png.is_file() and img_png.stat().st_size > 10_000 and not args.force:
            print(f"  [stage1] {slug}: imagery cached -> {img_png.name}")
        else:
            render_imagery(slug, positive, img_png)
        if args.imagery_only:
            done += 1
            continue
        out = composite_cover(img_png, b["title"], b["subtitle"],
                              args.author, args.publisher,
                              out_dir / f"cover_{slug}.png", max_bytes=args.max_bytes)
        sz = out.stat().st_size
        flag = "OK" if sz <= args.max_bytes else "OVER-CAP"
        print(f"  [stage2] cover -> {out} ({sz} bytes, {sz/1e6:.2f} MB) [{flag}]")
        done += 1
    print(f"{done} cover(s) processed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
