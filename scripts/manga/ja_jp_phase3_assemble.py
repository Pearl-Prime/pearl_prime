#!/usr/bin/env python3
"""Phase 3 — assemble per-series manga book deliverables for ja_JP.

For each series that has completed renders + bubbles, this builds:

  1. ``cover/<series>_cover_v1_raw.png``  (FLUX/Animagine render of main character)
  2. ``cover/<series>_cover_v1_final.png`` (PIL title overlay per the two-stage rule)
  3. ``<series>_ep_NNN_webtoon_scroll.png`` (one tall PNG = the reader's continuous scroll)
  4. ``<series>_ep_NNN_book.pdf`` (cover + title + 12-panel bound book)
  5. ``r2:phoenix-omega-artifacts/manga/ja_jp_books/<series>/*`` (synced)

Idempotent + resumable: skips a series whose
``BOOK_COMPLETE_<series>.flag`` sentinel exists.

Runs AFTER Phase 2 bulk. Discovers series with completed panel renders
(panels_dir non-empty AND chapter_script.yaml present).

Usage:
    python3 scripts/manga/ja_jp_phase3_assemble.py [--series SERIES_ID]
                                                   [--skip-r2]
                                                   [--cover-via-comfyui]
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import yaml  # type: ignore
from PIL import Image, ImageDraw, ImageFont  # type: ignore

REPO_ROOT = Path(__file__).resolve().parents[2]
SENTINEL_DIR = REPO_ROOT / "artifacts" / "manga" / "sentinels"
CHAPTER_SCRIPTS_DIR = REPO_ROOT / "artifacts" / "manga" / "chapter_scripts"
PANELS_OUT_DIR = REPO_ROOT / "artifacts" / "manga" / "panels"
BUBBLED_OUT_DIR = REPO_ROOT / "artifacts" / "manga" / "bubbled"
BOOKS_OUT_DIR = REPO_ROOT / "artifacts" / "manga" / "books"
COVERS_OUT_DIR = REPO_ROOT / "artifacts" / "manga" / "covers"

QUEUE_RENDER = REPO_ROOT / "scripts" / "manga" / "queue_panel_renders.py"

# Gutter map for webtoon scroll (matches webtoon_compose.py)
GUTTER_PX = {
    None: 200,
    "micro": 40,
    "spatial": 200,
    "standard": 800,
    "long_drop": 2200,
    "miyazaki_ma": 2800,
}

WEBTOON_WIDTH = 800
TARGET_W, TARGET_H = 1200, 1920  # PDF page dimensions


def log(msg: str) -> None:
    print(f"[assemble {time.strftime('%H:%M:%S')}] {msg}", flush=True)


def load_font(size: int, *names: str) -> ImageFont.ImageFont:
    for name in names:
        for prefix in ("/Library/Fonts/", "/System/Library/Fonts/", "/System/Library/Fonts/Supplemental/",
                       "/usr/share/fonts/", "/usr/share/fonts/truetype/dejavu/",
                       "/usr/share/fonts/opentype/noto/", "/usr/share/fonts/truetype/noto/"):
            for ext in (".ttf", ".ttc", ".otf"):
                p = Path(prefix + name + ext)
                if p.exists():
                    try:
                        return ImageFont.truetype(str(p), size)
                    except Exception:
                        pass
    return ImageFont.load_default()


def discover_series() -> list[str]:
    """All series under chapter_scripts/ that have at least one rendered panel."""
    found: list[str] = []
    for series_dir in sorted(CHAPTER_SCRIPTS_DIR.glob("stillness_press__*__en_US__*")):
        panels_root = PANELS_OUT_DIR / series_dir.name
        if not panels_root.exists():
            continue
        # any chapter has at least 1 png?
        if any(panels_root.glob("ep_*/*.png")):
            found.append(series_dir.name)
    return found


def render_cover(series_id: str, chapter_yaml: Path, *, comfy_url: str, workflow_path: Path | None = None) -> Path | None:
    """Dispatch a single cover render to ComfyUI (Pearl Star)."""
    cs = yaml.safe_load(chapter_yaml.read_text())
    mains = cs.get("main_characters") or []
    if not mains:
        log(f"  cover: no main_characters in {chapter_yaml.name}; skipping cover render")
        return None
    main = mains[0]
    palette = cs.get("scene_palette") or {}
    palette_words = " · ".join(str(v) for v in palette.values() if v)
    style_hint = {
        "psychological_horror": "psychological horror manga, claustrophobic, cold blue light, deep shadows, anime linework",
        "mecha": "industrial mecha manga, seinen, harsh sodium hangar light, scale contrast, anime linework",
        "iyashikei": "iyashikei manga, gentle linework, soft watercolor, contemplative mood, anime linework",
    }
    # Guess the genre from the chapter_script
    # series_id pattern: brand__teacher__locale__topic__series
    parts = series_id.split("__")
    topic = parts[3] if len(parts) > 3 else ""
    genre_map = {
        "overthinking": "psychological_horror",
        "grief": "mecha",
        "anxiety": "iyashikei",
    }
    genre = genre_map.get(topic, "iyashikei")
    style = style_hint.get(genre, style_hint["iyashikei"])

    cover_prompt = (
        f"{palette_words}, Portrait of {main.get('name', 'main character')}, "
        f"{main.get('visual_anchor', '')}, {style}, "
        f"composition: 2/3 figure portrait, looking thoughtfully off-frame, no text, "
        f"no caption, no signature, no border, no title, no watermark"
    )

    cover_prompts_path = Path("/tmp/cover_prompts.json")
    cover_prompts_path.write_text(json.dumps({
        "schema_version": "1.0.0",
        "artifact_type": "panel_prompts",
        "panels": [{
            "panel_id": f"cover_{series_id}",
            "prompt": cover_prompt,
            "negative_prompt": "extra fingers, extra limbs, malformed hands, distorted face, watermark, signature, text, lettering, title, words, blurry, low resolution, jpeg artifacts, bad anatomy",
            "beat_type": None,
            "silence_confirmed": True,
            "composition_notes": {"summary": f"COVER — {main.get('name', 'main')}"}
        }],
    }, indent=2))

    out_dir = COVERS_OUT_DIR / series_id
    out_dir.mkdir(parents=True, exist_ok=True)

    wf = workflow_path or (REPO_ROOT / "scripts" / "image_generation" / "comfyui_workflows" / "animagine_xl_txt2img_manga_no_pulid.json")
    cmd = [
        sys.executable, str(QUEUE_RENDER),
        "--panel-prompts", str(cover_prompts_path),
        "--output-dir", str(out_dir),
        "--workflow-path", str(wf),
        "--comfy-url", comfy_url,
        "--skip-existing",
    ]
    log(f"  cover render → {wf.name}")
    rc = subprocess.run(cmd, env={**os.environ, "QUEUE_POLL_TIMEOUT_SEC": "900"}).returncode
    if rc != 0:
        log(f"  cover render FAILED rc={rc}")
        return None
    pngs = list(out_dir.glob(f"cover_{series_id}.png"))
    return pngs[0] if pngs else None


def composite_cover(raw_cover: Path, series_id: str, chapter_script: dict, out_path: Path) -> Path:
    """PIL title overlay per the two-stage cover rule (FLUX renders imagery only)."""
    cover = Image.open(raw_cover).convert("RGB")
    # Resize to TARGET_W × TARGET_H
    src_w, src_h = cover.size
    src_ratio, tgt_ratio = src_w / src_h, TARGET_W / TARGET_H
    if abs(src_ratio - tgt_ratio) > 0.01:
        if src_ratio > tgt_ratio:
            new_h = int(src_w / tgt_ratio)
            canvas = Image.new("RGB", (src_w, new_h), color=(20, 22, 28))
            canvas.paste(cover, (0, (new_h - src_h) // 2))
            cover = canvas
        else:
            new_w = int(src_h * tgt_ratio)
            canvas = Image.new("RGB", (new_w, src_h), color=(20, 22, 28))
            canvas.paste(cover, ((new_w - src_w) // 2, 0))
            cover = canvas
    cover = cover.resize((TARGET_W, TARGET_H), Image.LANCZOS)

    # Vignette
    overlay = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for y in range(0, 600):
        od.rectangle([(0, y), (TARGET_W, y + 1)], fill=(8, 8, 12, int(140 * (1 - y / 600))))
    for y in range(TARGET_H - 500, TARGET_H):
        od.rectangle([(0, y), (TARGET_W, y + 1)], fill=(8, 8, 12, int(160 * ((y - (TARGET_H - 500)) / 500))))
    cover = Image.alpha_composite(cover.convert("RGBA"), overlay).convert("RGB")

    # Titles
    title_en = chapter_script.get("title", "")
    # Get series-level title (strip "Episode 1: ...")
    series_title = title_en.split(" — ")[0] if " — " in title_en else title_en
    author = chapter_script.get("manga_author", "")

    font_title = load_font(110, "Avenir", "Helvetica", "DejaVuSans-Bold")
    font_sub = load_font(46, "Avenir", "Helvetica", "DejaVuSans")
    font_byline = load_font(38, "Avenir-Light", "Avenir", "Helvetica", "DejaVuSans")

    draw = ImageDraw.Draw(cover)
    draw.text((TARGET_W // 2, 180), series_title, font=font_title, fill=(248, 244, 234), anchor="mm",
              stroke_width=2, stroke_fill=(0, 0, 0))
    draw.text((TARGET_W // 2, 330), chapter_script.get("chapter_id", ""), font=font_sub, fill=(220, 220, 200), anchor="mm")
    draw.text((TARGET_W // 2, TARGET_H - 200), author, font=font_byline, fill=(248, 244, 234), anchor="mm")
    draw.text((TARGET_W // 2, TARGET_H - 140), "stillness_press", font=font_byline, fill=(220, 220, 200), anchor="mm")

    cover.save(out_path, "PNG", optimize=True)
    return out_path


def build_scroll(series_id: str, chapter_id: str) -> Path | None:
    """One tall PNG = the reader's whole-episode scroll."""
    panels_dir = PANELS_OUT_DIR / series_id / chapter_id
    pngs = sorted(panels_dir.glob("*.png"))
    if not pngs:
        return None
    # Prefer bubbled if they exist
    bubbled_dir = BUBBLED_OUT_DIR / series_id / chapter_id / "ja_JP"
    bubbled_pngs = sorted(bubbled_dir.glob("*_bubbled.png")) if bubbled_dir.exists() else []
    source_pngs = bubbled_pngs if bubbled_pngs else pngs

    chapter_yaml = CHAPTER_SCRIPTS_DIR / series_id / f"{chapter_id}.yaml"
    cs = yaml.safe_load(chapter_yaml.read_text())

    def beat_type_for(pid: str) -> str | None:
        for page in cs.get("pages", []) or []:
            for p in page.get("panels", []) or []:
                if p.get("panel_id") == pid or p.get("panel_id") == pid.replace("_bubbled", ""):
                    return p.get("beat_type")
        return None

    resized = []
    for png in source_pngs:
        im = Image.open(png).convert("RGB")
        new_h = int(im.size[1] * WEBTOON_WIDTH / im.size[0])
        resized.append((png.stem.replace("_bubbled", ""), im.resize((WEBTOON_WIDTH, new_h), Image.LANCZOS)))

    gutters = [0] + [GUTTER_PX.get(beat_type_for(sid), 200) for sid, _ in resized[1:]]
    total_h = sum(im.size[1] for _, im in resized) + sum(gutters)
    canvas = Image.new("RGB", (WEBTOON_WIDTH, total_h), color=(255, 255, 255))
    y = 0
    for (sid, im), g in zip(resized, gutters):
        y += g
        canvas.paste(im, (0, y))
        y += im.size[1]

    out = BOOKS_OUT_DIR / series_id / f"{series_id}_{chapter_id}_webtoon_scroll.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out, "PNG", optimize=False)
    log(f"  scroll: {out.name} ({out.stat().st_size / 1e6:.1f} MB, {total_h} px tall)")
    return out


def build_pdf(series_id: str, chapter_id: str, cover_path: Path | None, chapter_script: dict, out_path: Path) -> Path:
    """Bound PDF: cover + title page + 12-panel book + back."""
    pages: list[Image.Image] = []

    if cover_path and cover_path.exists():
        pages.append(Image.open(cover_path).convert("RGB"))

    font_title = load_font(90, "Avenir", "Helvetica", "DejaVuSans-Bold")
    font_sub = load_font(40, "Avenir", "Helvetica", "DejaVuSans")
    font_byline = load_font(30, "Avenir", "Helvetica", "DejaVuSans")

    # Title page
    tp = Image.new("RGB", (TARGET_W, TARGET_H), color=(248, 244, 240))
    d = ImageDraw.Draw(tp)
    series_title = chapter_script.get("title", "").split(" — ")[0]
    d.text((TARGET_W // 2, 700), series_title, font=font_title, fill=(40, 50, 50), anchor="mm")
    d.text((TARGET_W // 2, 900), chapter_script.get("chapter_id", ""), font=font_sub, fill=(120, 90, 60), anchor="mm")
    d.text((TARGET_W // 2, 1100), f"Author: {chapter_script.get('manga_author', '')}", font=font_sub, fill=(60, 60, 60), anchor="mm")
    d.text((TARGET_W // 2, 1200), f"Brand: stillness_press", font=font_byline, fill=(120, 120, 120), anchor="mm")
    d.text((TARGET_W // 2, 1300), f"Locale: ja_JP", font=font_byline, fill=(120, 120, 120), anchor="mm")
    d.text((TARGET_W // 2, 1600), "© 2026 SpiritualTech Systems", font=font_byline, fill=(160, 160, 160), anchor="mm")
    d.text((TARGET_W // 2, 1660), "AI-assisted: Animagine XL 4.0 (RAIL++-M); script + composition human-authored", font=font_byline, fill=(160, 160, 160), anchor="mm")
    pages.append(tp)

    # Panels — prefer bubbled
    panels_dir = PANELS_OUT_DIR / series_id / chapter_id
    bubbled_dir = BUBBLED_OUT_DIR / series_id / chapter_id / "ja_JP"
    bubbled = sorted(bubbled_dir.glob("*_bubbled.png")) if bubbled_dir.exists() else []
    raw = sorted(panels_dir.glob("*.png"))
    panel_pngs = bubbled if bubbled else raw

    for p in panel_pngs:
        im = Image.open(p).convert("RGB")
        aspect = im.size[0] / im.size[1]
        if aspect > TARGET_W / TARGET_H:
            new_w = TARGET_W
            new_h = int(TARGET_W / aspect)
        else:
            new_h = TARGET_H
            new_w = int(TARGET_H * aspect)
        im_resized = im.resize((new_w, new_h), Image.LANCZOS)
        canvas = Image.new("RGB", (TARGET_W, TARGET_H), color=(255, 255, 255))
        canvas.paste(im_resized, ((TARGET_W - new_w) // 2, (TARGET_H - new_h) // 2))
        pages.append(canvas)

    # Back page
    back = Image.new("RGB", (TARGET_W, TARGET_H), color=(248, 244, 240))
    d = ImageDraw.Draw(back)
    d.text((TARGET_W // 2, 800), f"more from {chapter_script.get('manga_author', 'this author')}", font=font_sub, fill=(80, 80, 80), anchor="mm")
    d.text((TARGET_W // 2, 1100), "stillness_press", font=font_byline, fill=(120, 120, 120), anchor="mm")
    pages.append(back)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    pages[0].save(out_path, "PDF", resolution=200, save_all=True, append_images=pages[1:])
    log(f"  pdf: {out_path.name} ({out_path.stat().st_size / 1e6:.2f} MB, {len(pages)} pages)")
    return out_path


def r2_sync(series_id: str, files: list[Path]) -> None:
    bucket = os.environ.get("R2_BUCKET", "phoenix-omega-artifacts")
    rclone = shutil.which("rclone") or os.path.expanduser("~/.local/bin/rclone")
    if not Path(rclone).exists():
        log(f"  rclone not found at {rclone}; skipping R2 sync")
        return
    for f in files:
        if not f.exists():
            continue
        dest = f"r2:{bucket}/manga/ja_jp_books/{series_id}/{f.name}"
        rc = subprocess.run([rclone, "copyto", str(f), dest], capture_output=True, timeout=300).returncode
        if rc == 0:
            log(f"  R2 ↑ {f.name}")
        else:
            log(f"  R2 FAIL: {f.name}")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--series", help="series_id (default: all)")
    p.add_argument("--skip-r2", action="store_true")
    p.add_argument("--comfy-url", default=os.environ.get("COMFYUI_URL", "http://localhost:8188"))
    p.add_argument("--cover-workflow", default=os.environ.get("MANGA_WORKFLOW_PATH"))
    args = p.parse_args()

    SENTINEL_DIR.mkdir(parents=True, exist_ok=True)
    BOOKS_OUT_DIR.mkdir(parents=True, exist_ok=True)
    COVERS_OUT_DIR.mkdir(parents=True, exist_ok=True)

    series_list = [args.series] if args.series else discover_series()
    log(f"Phase 3: assembling {len(series_list)} series")

    for series_id in series_list:
        sentinel = SENTINEL_DIR / f"BOOK_COMPLETE_{series_id}.flag"
        if sentinel.exists():
            log(f"[skip] {series_id} (BOOK_COMPLETE flag)")
            continue

        log(f"=== assemble: {series_id} ===")

        series_dir = CHAPTER_SCRIPTS_DIR / series_id
        chapters = sorted(c.stem for c in series_dir.glob("ep_*.yaml"))
        if not chapters:
            log(f"  no chapters; skipping")
            continue

        ep1_yaml = series_dir / f"{chapters[0]}.yaml"
        cs = yaml.safe_load(ep1_yaml.read_text())

        # Cover render
        cover_workflow_path = Path(args.cover_workflow) if args.cover_workflow else None
        raw_cover = render_cover(series_id, ep1_yaml, comfy_url=args.comfy_url, workflow_path=cover_workflow_path)
        cover_path = None
        if raw_cover:
            cover_path = COVERS_OUT_DIR / series_id / f"{series_id}_cover_v1_final.png"
            composite_cover(raw_cover, series_id, cs, cover_path)
            log(f"  composed cover: {cover_path.name} ({cover_path.stat().st_size / 1024:.0f} KB)")

        produced: list[Path] = []
        if cover_path and cover_path.exists():
            produced.append(cover_path)

        # Per chapter: scroll + PDF
        for chapter_id in chapters:
            scroll = build_scroll(series_id, chapter_id)
            if scroll:
                produced.append(scroll)

            pdf_out = BOOKS_OUT_DIR / series_id / f"{series_id}_{chapter_id}_book.pdf"
            try:
                build_pdf(series_id, chapter_id, cover_path, cs, pdf_out)
                produced.append(pdf_out)
            except Exception as e:
                log(f"  pdf FAILED: {e}")

        if not args.skip_r2 and produced:
            r2_sync(series_id, produced)

        sentinel.write_text(
            f"BOOK_COMPLETE @ {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n"
            f"series={series_id}\n"
            f"chapters={chapters}\n"
            f"files_produced={[str(f.name) for f in produced]}\n"
        )
        log(f"  ✓ {series_id}: {len(produced)} files in books/{series_id}/")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
