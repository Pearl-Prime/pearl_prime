#!/usr/bin/env python3
"""
Generate all 4 KDP-spec cover formats for all 13 teacher brands.

Pass 1: ComfyUI FLUX generates abstract background (NO text in prompt)
Pass 2: Python/PIL overlays professional typography

Formats:
  ebook     → 1600×2560  KDP ebook portrait
  audiobook → 3200×3200  Audible/Spotify square (AUDIOBOOK badge)
  podcast   → 3000×3000  Apple/Spotify podcast (PODCAST badge, distinct layout)
  social    → 1080×1080  Instagram/TikTok thumb

Output: brand-wizard-app/public/assets/covers/kdp/{teacher_id}_{format}.png

Usage:
  python3 scripts/image_generation/generate_kdp_all_formats.py --mode comfyui
  python3 scripts/image_generation/generate_kdp_all_formats.py --mode gradient
  python3 scripts/image_generation/generate_kdp_all_formats.py --mode gradient --teacher ahjan
  python3 scripts/image_generation/generate_kdp_all_formats.py --dry-run
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

# ── Dimensions ──────────────────────────────────────────────────────────────
FORMATS = {
    "ebook":     (1600, 2560),
    "audiobook": (3200, 3200),
    "podcast":   (3000, 3000),
    "social":    (1080, 1080),
}

# ComfyUI generation size (upscaled by PIL afterwards — background is abstract)
COMFYUI_SIZES = {
    "ebook":     (576, 1024),   # portrait ~5:8
    "audiobook": (1024, 1024),  # square
    "podcast":   (1024, 1024),  # square
    "social":    (1024, 1024),  # square
}

# ── Typography layout (fraction of final canvas) ─────────────────────────────
LAYOUTS = {
    "ebook": {
        "title_y":      0.12,
        "title_max_w":  0.85,
        "title_size":   0.065,
        "sub_y":        0.52,
        "sub_size":     0.028,
        "author_y":     0.80,
        "author_size":  0.025,
        "colophon_y":   0.92,
        "colophon_size":0.018,
        "badge_text":   None,
    },
    "audiobook": {
        "title_y":      0.20,
        "title_max_w":  0.80,
        "title_size":   0.075,
        "sub_y":        0.55,
        "sub_size":     0.032,
        "author_y":     0.78,
        "author_size":  0.028,
        "colophon_y":   0.90,
        "colophon_size":0.020,
        "badge_text":   "AUDIOBOOK",
    },
    "podcast": {
        # Distinct layout: series name at top, title in middle, teacher at bottom
        "series_y":     0.06,
        "series_size":  0.032,
        "title_y":      0.28,
        "title_max_w":  0.82,
        "title_size":   0.080,
        "sub_y":        0.60,
        "sub_size":     0.030,
        "author_y":     0.78,
        "author_size":  0.028,
        "colophon_y":   0.90,
        "colophon_size":0.020,
        "badge_text":   "PODCAST",
    },
    "social": {
        "title_y":      0.12,
        "title_max_w":  0.85,
        "title_size":   0.095,
        "sub_y":        0.58,
        "sub_size":     0.042,
        "author_y":     0.80,
        "author_size":  0.038,
        "colophon_y":   0.92,
        "colophon_size":0.028,
        "badge_text":   None,
    },
}

# ── Teacher book data (corrected to match manifest.json) ────────────────────
# Key = brand_id, matches brand_identity_system.yaml
TEACHER_BOOKS = {
    "stillness_press": {
        "teacher_id":   "ahjan",
        "title":        "The Alarm You Learned to Ignore",
        "subtitle":     "Recognizing what your body already knows about anxiety",
        "series":       "Stillness Press Podcast",
        "author":       "Lena Thorne",
        "topic":        "anxiety",
        "locale":       "en-US",
        "flux_prompt":  (
            "abstract watercolor wash, warm slate and cloud white, soft golden light, "
            "organic flowing forms, contemplative negative space, minimal, atmospheric"
        ),
    },
    "cognitive_clarity": {
        "teacher_id":   "joshin",
        "title":        "The Seeing Mind",
        "subtitle":     "When clarity arrives before the answer does",
        "series":       "Clear Seeing Books Podcast",
        "author":       "Ada Park",
        "topic":        "anxiety",
        "locale":       "en-US",
        "flux_prompt":  (
            "abstract bold monochrome, near-black with pure white, rice paper grain texture, "
            "Zen minimal, single brushstroke element, vast negative space"
        ),
    },
    "somatic_wisdom": {
        "teacher_id":   "pamela_fellows",
        "title":        "The Body Knows First",
        "subtitle":     "A polyvagal guide to burnout recovery",
        "series":       "Felt Sense Publishing Podcast",
        "author":       "Pamela Fellows",
        "topic":        "burnout",
        "locale":       "en-US",
        "flux_prompt":  (
            "abstract warm cream linen texture, espresso brown gradient, dusty rose accent, "
            "soft anatomical line detail, clinical warmth, embodied intelligence"
        ),
    },
    "qi_foundation": {
        "teacher_id":   "master_feung",
        "title":        "Root and Breath",
        "subtitle":     "Qi cultivation for the overwhelmed system",
        "series":       "Root & Meridian Press Podcast",
        "author":       "Master Feung",
        "topic":        "burnout",
        "locale":       "zh-CN",
        "flux_prompt":  (
            "abstract Chinese ink wash painting, earth brown and warm sand tones, "
            "flowing water patterns, dynamic brush strokes, mountain mist, powerful grounded"
        ),
    },
    "digital_ground": {
        "teacher_id":   "miki",
        "title":        "Scroll Stop",
        "subtitle":     "Digital-age calm for the always-on generation",
        "series":       "Present Tense Books Podcast",
        "author":       "Miki",
        "topic":        "social_anxiety",
        "locale":       "ja-JP",
        "flux_prompt":  (
            "abstract midnight blue with ice blue gradient, single cyan glow element, "
            "pixel grain subtle texture, nocturnal, screen-glow aesthetic, digital native calm"
        ),
    },
    "heart_balance": {
        "teacher_id":   "maat",
        "title":        "Scales of Ma'at",
        "subtitle":     "Shadow work as self-worth recalibration",
        "series":       "Feather & Scale Press Podcast",
        "author":       "Maat",
        "topic":        "self_worth",
        "locale":       "en-US",
        "flux_prompt":  (
            "abstract deep indigo and papyrus gold, sacred geometry patterns, "
            "feather and scale motif, ceremonial, ancient Egyptian cosmic weight, amber glow"
        ),
    },
    "relational_calm": {
        "teacher_id":   "junko",
        "title":        "The Empty Cup",
        "subtitle":     "Radical acceptance in relationships",
        "series":       "Bare Form Books Podcast",
        "author":       "Junko",
        "topic":        "overthinking",
        "locale":       "ja-JP",
        "flux_prompt":  (
            "abstract minimal Japanese aesthetic, near-white with single stone grey brushstroke, "
            "maximum negative space, wabi-sabi, imperfect circle trace, warm white"
        ),
    },
    "warrior_calm": {
        "teacher_id":   "master_wu",
        "title":        "Iron Gate",
        "subtitle":     "Martial composure under pressure",
        "series":       "Iron Gate Press Podcast",
        "author":       "Master Wu",
        "topic":        "courage",
        "locale":       "zh-CN",
        "flux_prompt":  (
            "abstract charcoal and gunmetal tones, sharp geometric forms, single crimson element, "
            "compressed power, martial discipline, contained intensity, brushed metal texture"
        ),
    },
    "sleep_restoration": {
        "teacher_id":   "master_sha",
        "title":        "Night Architecture",
        "subtitle":     "Building sleep from the inside",
        "series":       "Night Architecture Books Podcast",
        "author":       "Master Sha",
        "topic":        "sleep_anxiety",
        "locale":       "zh-CN",
        "flux_prompt":  (
            "abstract near-black to deep indigo gradient, soft violet moon arch element, "
            "velvet grain texture, nocturnal architectural, restful depth, star-field subtle"
        ),
    },
    "body_memory": {
        "teacher_id":   "omote",
        "title":        "Held Ground",
        "subtitle":     "Letting the body process what the mind cannot",
        "series":       "Held Ground Press Podcast",
        "author":       "Omote",
        "topic":        "sleep_anxiety",
        "locale":       "ko-KR",
        "flux_prompt":  (
            "abstract warm charcoal and clay tones, terracotta accent, earthen seasonal texture, "
            "grounded body impression, hand pressing ground, seasonal healing"
        ),
    },
    "solar_return": {
        "teacher_id":   "ra",
        "title":        "Ember and Ash",
        "subtitle":     "Burnout as initiation, not failure",
        "series":       "Ember & Ash Publishing Podcast",
        "author":       "Ra",
        "topic":        "imposter_syndrome",
        "locale":       "en-US",
        "flux_prompt":  (
            "abstract soot black to ash white gradient bottom to top, single ember orange spark, "
            "charcoal grain texture, post-fire clarity, phoenix energy, stark renewal"
        ),
    },
    "devotion_path": {
        "teacher_id":   "sai_ma",
        "title":        "Open Vessel",
        "subtitle":     "Devotion as a self-worth practice",
        "series":       "Open Vessel Press Podcast",
        "author":       "Sai Ma",
        "topic":        "grief",
        "locale":       "zh-CN",
        "flux_prompt":  (
            "abstract lotus white to deep purple gradient, blush pink accent, silk weave texture, "
            "devotional warmth, feminine grace, lotus petal motif, receiving energy"
        ),
    },
    "awakening_press": {
        "teacher_id":   "adi_da",
        "title":        "The Fire That Sees",
        "subtitle":     "Radical self-inquiry for the devoted seeker",
        "series":       "Awakening Press Podcast",
        "author":       "Adi Da",
        "topic":        "self_worth",
        "locale":       "en-US",
        "flux_prompt":  (
            "abstract dark canvas deep indigo and old gold, dramatic light ray breaking through "
            "darkness, high contrast, sharp geometric forms, intense piercing illumination"
        ),
        "colors_override": ["#4A1A2A", "#1A0A10"],
        "accent_override":  "#FF6B35",
        "display_name_override": "Awakening Press",
    },
}

# ── Helpers ──────────────────────────────────────────────────────────────────

def _hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

def _luminance(rgb: tuple[int, int, int]) -> float:
    return (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255.0

def _load_font(size: int, bold: bool = False):
    from PIL import ImageFont
    candidates = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFCompact.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()

def _wrap_text(text: str, font, max_w: int, draw) -> list[str]:
    words = text.split()
    lines, cur = [], ""
    for word in words:
        test = f"{cur} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > max_w and cur:
            lines.append(cur)
            cur = word
        else:
            cur = test
    if cur:
        lines.append(cur)
    return lines or [text]

def _load_brand_identity(brand_id: str) -> dict[str, Any]:
    try:
        import yaml
    except ImportError:
        return {}
    p = REPO_ROOT / "config" / "catalog_planning" / "brand_identity_system.yaml"
    data = yaml.safe_load(p.read_text()) or {} if p.exists() else {}
    brand = (
        (data.get("teacher_brands") or {}).get(brand_id) or
        (data.get("standard_brands") or {}).get(brand_id) or
        {}
    )
    bi = brand.get("brand_identity", {})
    return {
        "display_name": brand.get("display_name", brand_id.replace("_", " ").title()),
        "primary_colors": bi.get("primary_colors", ["#1A1A1A", "#F5F5F5"]),
        "accent_color":   bi.get("accent_color", "#D4A574"),
    }


# ── Background generators ─────────────────────────────────────────────────────

def _gradient_bg(w: int, h: int, colors: list[str]) -> "Image":
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)
    c1 = _hex_to_rgb(colors[0])
    c2 = _hex_to_rgb(colors[1]) if len(colors) > 1 else c1
    for y in range(h):
        t = y / h
        draw.line([(0, y), (w, y)], fill=tuple(int(c1[i] * (1 - t) + c2[i] * t) for i in range(3)))
    return img

def _comfyui_bg(
    comfyui_url: str,
    prompt: str,
    seed: int,
    fmt: str,
    w: int, h: int,
) -> "Image":
    """Generate background via ComfyUI FLUX, resize to (w, h)."""
    from PIL import Image
    wf_path = REPO_ROOT / "scripts" / "image_generation" / "comfyui_workflows" / "flux_video_bank.json"
    workflow = json.loads(wf_path.read_text())
    # ComfyUI treats every top-level key as a node; strip metadata
    workflow.pop("_meta", None)

    negative = (
        "text, letters, words, typography, title, author, watermark, "
        "face, person, hand, fingers, realistic photo, busy, cluttered, border, frame"
    )
    full_prompt = f"{prompt}\n\nAvoid: {negative}"

    if "6" in workflow:
        workflow["6"]["inputs"]["text"] = full_prompt
    if "25" in workflow:
        workflow["25"]["inputs"]["noise_seed"] = seed
    elif "3" in workflow:
        workflow["3"]["inputs"]["seed"] = seed

    # Set generation dimensions (ComfyUI node "5" = EmptyLatentImage)
    gen_w, gen_h = COMFYUI_SIZES[fmt]
    if "5" in workflow:
        workflow["5"]["inputs"]["width"]  = gen_w
        workflow["5"]["inputs"]["height"] = gen_h

    url = comfyui_url.rstrip("/")
    payload = json.dumps({"prompt": workflow}).encode()
    req = urllib.request.Request(
        f"{url}/prompt", data=payload, headers={"Content-Type": "application/json"}
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
            outputs = history[prompt_id].get("outputs", {})
            for node_out in outputs.values():
                images = node_out.get("images", [])
                if images:
                    img_meta = images[0]
                    params = urllib.parse.urlencode({
                        "filename": img_meta["filename"],
                        "subfolder": img_meta.get("subfolder", ""),
                        "type": img_meta.get("type", "output"),
                    })
                    with urllib.request.urlopen(f"{url}/view?{params}", timeout=60) as iresp:
                        raw = iresp.read()
                    img = Image.open(io.BytesIO(raw)).convert("RGB")
                    return img.resize((w, h), Image.LANCZOS)
    raise RuntimeError(f"ComfyUI timed out for prompt {prompt_id}")


# ── Typography overlay ────────────────────────────────────────────────────────

def _draw_badge(draw, text: str, x: int, y: int, accent_rgb: tuple, text_color: tuple, size: int) -> None:
    """Draw a pill-shaped badge (e.g., AUDIOBOOK, PODCAST)."""
    font = _load_font(size, bold=True)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y = int(size * 0.5), int(size * 0.25)
    rx0, ry0 = x - pad_x, y - pad_y
    rx1, ry1 = x + tw + pad_x, y + th + pad_y
    draw.rounded_rectangle([rx0, ry0, rx1, ry1], radius=int(size * 0.3), fill=accent_rgb)
    bright = tuple(min(255, c + 80) for c in accent_rgb)
    draw.text((x, y), text, fill=bright, font=font)

def _overlay_typography(
    img: "Image",
    book: dict[str, Any],
    brand_info: dict[str, Any],
    fmt: str,
) -> "Image":
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    w, h = img.size
    layout = LAYOUTS[fmt]

    # Detect text color from background center
    center = img.getpixel((w // 2, h // 3))
    if isinstance(center, int):
        center = (center, center, center)
    bg_lum = _luminance(center[:3])
    text_color = (255, 255, 255) if bg_lum < 0.5 else (20, 20, 20)
    accent_rgb = _hex_to_rgb(brand_info["accent_color"])
    max_w = int(w * layout["title_max_w"])

    def draw_centered(text: str, font, y: int, color: tuple) -> int:
        lines = _wrap_text(text, font, max_w, draw)
        lh = int(font.size * 1.25)
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            lw = bbox[2] - bbox[0]
            draw.text(((w - lw) // 2, y), line, fill=color, font=font)
            y += lh
        return y

    # ── PODCAST format has unique layout ──────────────────────────────────────
    if fmt == "podcast":
        # Dark overlay strip at top for readability
        from PIL import Image
        overlay = Image.new("RGBA", (w, int(h * 0.22)), (0, 0, 0, 160))
        img.paste(Image.new("RGB", overlay.size, (0, 0, 0)), (0, 0), overlay)

        # Series name (smaller, at top)
        ser_size = max(20, int(h * layout["series_size"]))
        ser_font = _load_font(ser_size, bold=False)
        draw.text.__self__  # re-get draw after paste
        draw = ImageDraw.Draw(img)
        series_text = book.get("series", f"A {brand_info['display_name']} Podcast")
        bbox = draw.textbbox((0, 0), series_text, font=ser_font)
        sw = bbox[2] - bbox[0]
        ser_y = int(h * layout["series_y"])
        draw.text(((w - sw) // 2, ser_y), series_text, fill=(220, 220, 220), font=ser_font)

        # Thin accent line under series name
        line_y = ser_y + ser_size + int(h * 0.018)
        bw = int(w * 0.3)
        bx = (w - bw) // 2
        draw.rectangle([(bx, line_y), (bx + bw, line_y + 3)], fill=accent_rgb)

        # Title (oversized, centered)
        title_size = max(32, int(h * layout["title_size"]))
        title_font = _load_font(title_size, bold=True)
        title_y = int(h * layout["title_y"])
        end_y = draw_centered(book["title"].upper(), title_font, title_y, text_color)

        # Subtitle
        sub_size = max(18, int(h * layout["sub_size"]))
        sub_font = _load_font(sub_size, bold=False)
        sub_y = int(h * layout["sub_y"])
        muted = tuple(max(0, min(255, c + (40 if bg_lum < 0.5 else -40))) for c in text_color)
        draw_centered(book["subtitle"], sub_font, sub_y, muted)

        # Author
        auth_size = max(16, int(h * layout["author_size"]))
        auth_font = _load_font(auth_size, bold=False)
        auth_y = int(h * layout["author_y"])
        auth_bbox = draw.textbbox((0, 0), book["author"], font=auth_font)
        aw = auth_bbox[2] - auth_bbox[0]
        draw.text(((w - aw) // 2, auth_y), book["author"], fill=accent_rgb, font=auth_font)

        # PODCAST badge — top-right corner
        badge_size = max(14, int(h * 0.022))
        badge_x = int(w * 0.62)
        badge_y = int(h * 0.045)
        _draw_badge(draw, "🎙 PODCAST", badge_x, badge_y, accent_rgb, text_color, badge_size)

        # Colophon
        col_size = max(12, int(h * layout["colophon_size"]))
        col_font = _load_font(col_size, bold=False)
        col_y = int(h * layout["colophon_y"])
        col_text = brand_info["display_name"]
        col_bbox = draw.textbbox((0, 0), col_text, font=col_font)
        cw = col_bbox[2] - col_bbox[0]
        muted2 = tuple(max(0, min(255, c + (60 if bg_lum < 0.5 else -60))) for c in text_color)
        draw.text(((w - cw) // 2, col_y), col_text, fill=muted2, font=col_font)

        return img

    # ── Standard formats (ebook, audiobook, social) ────────────────────────────
    title_size = max(24, int(h * layout["title_size"]))
    title_font = _load_font(title_size, bold=True)
    title_y = int(h * layout["title_y"])
    end_y = draw_centered(book["title"].upper(), title_font, title_y, text_color)

    # Accent bar
    bar_y = end_y + int(h * 0.015)
    bw = int(w * 0.2)
    bx = (w - bw) // 2
    draw.rectangle([(bx, bar_y), (bx + bw, bar_y + 4)], fill=accent_rgb)

    # Subtitle
    if book.get("subtitle"):
        sub_size = max(16, int(h * layout["sub_size"]))
        sub_font = _load_font(sub_size, bold=False)
        sub_y = int(h * layout["sub_y"])
        muted = tuple(max(0, min(255, c + (40 if bg_lum < 0.5 else -40))) for c in text_color)
        draw_centered(book["subtitle"], sub_font, sub_y, muted)

    # Author
    auth_size = max(14, int(h * layout["author_size"]))
    auth_font = _load_font(auth_size, bold=False)
    auth_y = int(h * layout["author_y"])
    auth_bbox = draw.textbbox((0, 0), book["author"], font=auth_font)
    aw = auth_bbox[2] - auth_bbox[0]
    draw.text(((w - aw) // 2, auth_y), book["author"], fill=accent_rgb, font=auth_font)

    # Badge (AUDIOBOOK)
    if layout.get("badge_text"):
        badge_size = max(14, int(h * 0.018))
        badge_x = int(w * 0.04)
        badge_y = int(h * 0.04)
        _draw_badge(draw, layout["badge_text"], badge_x, badge_y, accent_rgb, text_color, badge_size)

    # Colophon
    if brand_info.get("display_name"):
        col_size = max(12, int(h * layout["colophon_size"]))
        col_font = _load_font(col_size, bold=False)
        col_y = int(h * layout["colophon_y"])
        col_text = brand_info["display_name"]
        col_bbox = draw.textbbox((0, 0), col_text, font=col_font)
        cw = col_bbox[2] - col_bbox[0]
        muted2 = tuple(max(0, min(255, c + (60 if bg_lum < 0.5 else -60))) for c in text_color)
        draw.text(((w - cw) // 2, col_y), col_text, fill=muted2, font=col_font)

    return img


# ── Main generation loop ─────────────────────────────────────────────────────

def generate_all(
    mode: str = "gradient",
    teacher_filter: str | None = None,
    fmt_filter: str | None = None,
    dry_run: bool = False,
) -> list[dict]:
    from PIL import Image

    out_dir = REPO_ROOT / "brand-wizard-app" / "public" / "assets" / "covers" / "kdp"
    out_dir.mkdir(parents=True, exist_ok=True)

    comfyui_url = os.environ.get("COMFYUI_URL", "http://192.168.1.112:8188").strip()

    results = []
    brands = list(TEACHER_BOOKS.keys())
    if teacher_filter:
        brands = [b for b in brands if TEACHER_BOOKS[b]["teacher_id"] == teacher_filter]

    fmts = list(FORMATS.keys())
    if fmt_filter:
        fmts = [f for f in fmts if f == fmt_filter]

    total = len(brands) * len(fmts)
    print(f"KDP Cover Generator — {len(brands)} teachers × {len(fmts)} formats = {total} covers")
    print(f"Mode: {mode}  Output: {out_dir}/\n")

    for brand_id in brands:
        book = TEACHER_BOOKS[brand_id]
        teacher_id = book["teacher_id"]
        brand_info = _load_brand_identity(brand_id)
        # Apply overrides
        if book.get("colors_override"):
            brand_info["primary_colors"] = book["colors_override"]
        if book.get("accent_override"):
            brand_info["accent_color"] = book["accent_override"]
        if book.get("display_name_override"):
            brand_info["display_name"] = book["display_name_override"]

        seed = int(hashlib.md5(brand_id.encode()).hexdigest()[:8], 16) % (2 ** 31)

        print(f"  [{brand_id}] {book['title']} ({teacher_id})")

        for fmt in fmts:
            dest = out_dir / f"{teacher_id}_{fmt}.png"
            w, h = FORMATS[fmt]

            if dry_run:
                print(f"    [DRY-RUN] {fmt:12s} → {dest.name}")
                results.append({"teacher": teacher_id, "format": fmt, "status": "dry_run"})
                continue

            # Pass 1: background
            if mode == "comfyui":
                try:
                    bg = _comfyui_bg(comfyui_url, book["flux_prompt"], seed + list(FORMATS.keys()).index(fmt), fmt, w, h)
                    print(f"    [comfyui] {fmt:12s} → background generated")
                except Exception as e:
                    print(f"    [WARN] ComfyUI failed ({e}), using gradient")
                    bg = _gradient_bg(w, h, brand_info["primary_colors"])
            else:
                bg = _gradient_bg(w, h, brand_info["primary_colors"])

            # Pass 2: typography overlay
            cover = _overlay_typography(bg, book, brand_info, fmt)
            cover.save(str(dest), "PNG", optimize=True)
            sz = dest.stat().st_size
            print(f"    [ok]      {fmt:12s} → {dest.name} ({sz:,} B)")
            results.append({"teacher": teacher_id, "format": fmt, "path": str(dest), "status": "ok"})

    ok = sum(1 for r in results if r["status"] == "ok")
    print(f"\n{'='*55}")
    print(f"Generated: {ok}/{total} covers")
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate all 4 KDP cover formats for all 13 teachers")
    ap.add_argument("--mode", choices=["gradient", "comfyui"], default="gradient")
    ap.add_argument("--teacher", default=None, help="Generate single teacher by teacher_id")
    ap.add_argument("--format", choices=list(FORMATS.keys()), default=None, help="Single format only")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    results = generate_all(
        mode=args.mode,
        teacher_filter=args.teacher,
        fmt_filter=args.format,
        dry_run=args.dry_run,
    )
    ok = sum(1 for r in results if r["status"] == "ok")
    return 0 if ok == sum(1 for r in results) or args.dry_run else 1


if __name__ == "__main__":
    raise SystemExit(main())
