#!/usr/bin/env python3
"""Build ja_JP EPUBs for the 4 stillness_press books from Qwen-translated text.

Wires the Qwen-translated `books/text/book_<slug>.ja.txt` files (produced by
translate_book_ja.py — Tier 2, Pearl Star) into scripts/release/build_epub.py
with `--language ja`, the ComfyUI-rendered covers, and Japanese titles.

The ja title is read from the FIRST non-empty line of the translated text
(translate_book_ja.py emits the translated book-title heading there).

Usage:
  python3 build_ja_epubs.py                 # build all available
  python3 build_ja_epubs.py --slug anxiety_gen_z_professionals
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _find_build_epub() -> Path:
    """Locate scripts/release/build_epub.py.

    Works from a git worktree (where parents[N] does not reach the real repo).
    Honors $PHOENIX_REPO; otherwise walks up from CWD and from this file.
    """
    env = os.environ.get("PHOENIX_REPO")
    cands = []
    if env:
        cands.append(Path(env) / "scripts" / "release" / "build_epub.py")
    for base in (Path.cwd(), HERE):
        p = base
        for _ in range(12):
            cands.append(p / "scripts" / "release" / "build_epub.py")
            p = p.parent
    for c in cands:
        if c.is_file():
            return c.resolve()
    sys.exit("could not locate scripts/release/build_epub.py — set $PHOENIX_REPO")


BUILD_EPUB = _find_build_epub()

# slug -> (en title fallback, en subtitle, topic)
BOOKS = {
    "anxiety_gen_z_professionals": (
        "The Room Is Safe",
        "A Body-First Guide to Anxiety for People Who Can't Switch Off", "anxiety"),
    "sleep_anxiety_midlife_women": (
        "The Hour That Won't Let Go",
        "A Somatic Guide to the 3 A.M. Mind for Women Tired of Being Tired", "sleep_anxiety"),
    "overthinking_millennial_women_professionals": (
        "The Fourth Draft of a Text Message",
        "A Contemplative Guide to Quieting the Mind That Won't Stop Rehearsing", "overthinking"),
    "anxiety_tech_finance_burnout": (
        "The Dashboard in Your Chest",
        "A Body-First Guide to Anxiety for High-Output People Running on Empty", "anxiety"),
}


def ja_title_from_text(ja_txt: Path, fallback: str) -> str:
    for line in ja_txt.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s:
            return s
    return fallback


def _epub_cover(slug: str) -> Path | None:
    """Make a downscaled, optimized cover for EPUB embedding.

    The full ComfyUI cover is ~0.8-0.9 MB; build_epub re-letterboxes it to
    1600x2560 PNG (~1.8 MB) which would push the EPUB over the no-binary-blobs
    1 MB cap (brand1_deep ships raw EPUB blobs). We embed a 800x1280 cover
    quantized under ~250 KB instead — fine for an e-ink/phone reader.
    """
    src = HERE.parent / "en_US" / "books" / "covers" / f"cover_{slug}.png"
    if not src.is_file():
        return None
    try:
        from PIL import Image
    except ImportError:
        return src
    tmp_dir = HERE / "books" / "epub" / "_covers"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    out = tmp_dir / f"cover_{slug}.epub.png"
    # KDP minimum is 1000x1600; use exactly that so the EPUB cover passes the
    # KDP floor while keeping the embedded PNG small enough to stay under the
    # 1 MB raw-blob cap (quantize the soft palette as needed).
    img = Image.open(src).convert("RGB").resize((1000, 1600), Image.LANCZOS)
    img.save(out, "PNG", optimize=True)
    cap = 600_000
    if out.stat().st_size > cap:
        for colors in (256, 192, 128, 96, 64, 48):
            q = img.quantize(colors=colors, method=Image.MEDIANCUT, dither=Image.FLOYDSTEINBERG)
            q.save(out, "PNG", optimize=True)
            if out.stat().st_size <= cap:
                break
    return out


def build_one(slug: str) -> bool:
    en_fallback, _subtitle, topic = BOOKS[slug]
    ja_txt = HERE / "books" / "text" / f"book_{slug}.ja.txt"
    if not ja_txt.is_file() or ja_txt.stat().st_size < 200:
        print(f"  [skip] {slug}: ja text not ready ({ja_txt})")
        return False
    cover = _epub_cover(slug)
    out_epub = HERE / "books" / "epub" / f"book_{slug}.ja.epub"
    out_epub.parent.mkdir(parents=True, exist_ok=True)
    ja_title = ja_title_from_text(ja_txt, en_fallback)
    cmd = [
        sys.executable, str(BUILD_EPUB),
        "--input", str(ja_txt),
        "--title", ja_title,
        "--author", "Ahjan",
        "--publisher", "Stillness Press",
        "--language", "ja",
        "--topic", topic,
        "--output", str(out_epub),
    ]
    if cover and cover.is_file():
        cmd += ["--cover", str(cover), "--raw-cover"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not out_epub.is_file():
        print(f"  [FAIL] {slug}: rc={r.returncode}\n{r.stderr[-600:]}")
        return False
    print(f"  [ok]   {slug}: {out_epub.name} ({out_epub.stat().st_size} bytes) title={ja_title!r}")
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", help="build only this slug")
    args = ap.parse_args()
    slugs = [args.slug] if args.slug else list(BOOKS)
    ok = sum(build_one(s) for s in slugs)
    print(f"{ok}/{len(slugs)} ja EPUB(s) built")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
