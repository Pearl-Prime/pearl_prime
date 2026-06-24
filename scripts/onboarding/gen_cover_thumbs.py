#!/usr/bin/env python3
"""Dashboard JPEG thumbs from full-res covers (gitignored under assets/covers/).

Full KDP covers (~3 MB PNG) cannot ship on Cloudflare Pages: assets/covers/ is
gitignored and LFS budget is exhausted. This script writes small JPEG thumbs
(<200 KB each) to brand-wizard-app/public/assets/cover_thumbs/{brand}/ so the
handoff dashboard can display real cover art after a normal Pages deploy.

Run after rendering covers locally:
  python3 scripts/onboarding/gen_cover_thumbs.py --brand devotion_path
  python3 scripts/onboarding/gen_brand_catalogs.py --brand devotion_path
"""
from __future__ import annotations

import argparse
import io
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parents[2]
COVERS = REPO / "brand-wizard-app" / "public" / "assets" / "covers"
ARTIFACT_COVERS = REPO / "artifacts" / "covers"
THUMBS = REPO / "brand-wizard-app" / "public" / "assets" / "cover_thumbs"

MAX_WIDTH = 420
JPEG_QUALITY = 82
MAX_BYTES = 250_000


def _source_png(brand: str, book_id: str) -> Path | None:
    name = f"{book_id}.png"
    for root in (COVERS / brand, ARTIFACT_COVERS / brand / "all", ARTIFACT_COVERS / brand):
        p = root / name
        if p.is_file():
            return p
    return None


def _encode_jpeg(img: Image.Image, quality: int) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()


def render_thumb(src: Path, out: Path) -> int:
    img = Image.open(src).convert("RGB")
    w, h = img.size
    if w > MAX_WIDTH:
        nh = int(h * MAX_WIDTH / w)
        img = img.resize((MAX_WIDTH, nh), Image.Resampling.LANCZOS)
    quality = JPEG_QUALITY
    data = _encode_jpeg(img, quality)
    while len(data) > MAX_BYTES and quality > 50:
        quality -= 5
        data = _encode_jpeg(img, quality)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    return len(data)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--brand", required=True, help="brand prefix (e.g. devotion_path)")
    ap.add_argument("--book-id", default=None, help="single book_id stem (default: all PNGs found)")
    args = ap.parse_args()
    brand = args.brand.strip()
    out_dir = THUMBS / brand
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.book_id:
        ids = [args.book_id.strip()]
    else:
        seen: set[str] = set()
        for root in (COVERS / brand, ARTIFACT_COVERS / brand / "all", ARTIFACT_COVERS / brand):
            if root.is_dir():
                for p in root.glob("*.png"):
                    seen.add(p.stem)
        ids = sorted(seen)

    ok, missing = 0, []
    for book_id in ids:
        src = _source_png(brand, book_id)
        if not src:
            missing.append(book_id)
            continue
        nbytes = render_thumb(src, out_dir / f"{book_id}.jpg")
        print(f"  {book_id}.jpg  ({nbytes // 1024} KB)  <- {src.relative_to(REPO)}")
        ok += 1

    if missing:
        print(f"MISSING source PNG ({len(missing)}): {missing[:5]}{'...' if len(missing) > 5 else ''}")
    print(f"wrote {ok} thumbs -> {out_dir.relative_to(REPO)}")
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
