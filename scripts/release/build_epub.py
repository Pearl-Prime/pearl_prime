#!/usr/bin/env python3
"""
EPUB Book Packager — build_epub.py

Takes rendered book text files and produces KDP-ready EPUB 3 packages
with cover images, metadata, and multi-chapter structure.

Usage:
    # Build EPUB from a book text file
    python scripts/release/build_epub.py \
        --input artifacts/pipeline_examples/ahjan/book_ahjan_anxiety_15min.txt \
        --title "The Alarm Is Lying" \
        --subtitle "A Nervous System Guide to Anxiety Recovery" \
        --author "Ahjan" \
        --publisher "Inner Light Press" \
        --cover artifacts/pipeline_examples/ahjan/cover_ahjan_anxiety.png \
        --output artifacts/epub/ahjan_anxiety.epub

    # Build all 13 teacher books
    python scripts/release/build_epub.py --batch

    # Dry run (show what would be built)
    python scripts/release/build_epub.py --batch --dry-run
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# KDP ideal embedded / storefront portrait (height × width per Amazon Help G200645690)
_EBOOK_COVER_W = 1600
_EBOOK_COVER_H = 2560

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

logger = logging.getLogger("epub_builder")

try:
    from ebooklib import epub
except ImportError:
    print("Error: ebooklib required. Install: pip install ebooklib", file=sys.stderr)
    sys.exit(1)


# ─── BOOK MANIFEST ────────────────────────────────────────────────────

TEACHER_BOOKS = [
    {"id": "ahjan", "author": "Ahjan", "publisher": "Inner Light Press",
     "title": "The Alarm Is Lying", "subtitle": "A Nervous System Guide to Anxiety Recovery",
     "topic": "anxiety", "lang": "en"},
    {"id": "adi_da", "author": "Adi Da", "publisher": "Awakening Press",
     "title": "You Were Always Enough", "subtitle": "Rebuilding Self-Esteem and Reclaiming Your Worth",
     "topic": "self_worth", "lang": "en"},
    {"id": "joshin", "author": "Joshin", "publisher": "Still Forest",
     "title": "Quiet Enough", "subtitle": "A Zen Guide to Calming Anxiety and Finding Presence",
     "topic": "anxiety", "lang": "en"},
    {"id": "miyuki", "author": "Miyuki", "publisher": "Zen Clarity",  # per OPD-111 — Loop Breaker is contemplative
     "title": "The Loop Breaker", "subtitle": "How to Stop Overthinking and Quiet Your Racing Mind",
     "topic": "overthinking", "lang": "en"},
    {"id": "maat", "author": "Ma'at", "publisher": "Truth Compass",
     "title": "The No That Saved Me", "subtitle": "A Practical Guide to Setting Boundaries and Finding Peace",
     "topic": "boundaries", "lang": "en"},
    {"id": "master_feung", "author": "Master Feung", "publisher": "Vitality Path",
     "title": "After Burnout", "subtitle": "A Taoist Guide to Energy Recovery",
     "topic": "burnout", "lang": "zh-CN"},
    {"id": "master_sha", "author": "Master Sha", "publisher": "Soul Repair",
     "title": "The Weight of Gone", "subtitle": "A Gentle Guide to Grief, Loss, and Healing",
     "topic": "grief", "lang": "en"},
    {"id": "master_wu", "author": "Master Wu", "publisher": "Mountain Gate Press",
     "title": "The Way of Courage", "subtitle": "Shaolin Wisdom for Facing Fear",
     "topic": "courage", "lang": "zh-TW"},
    {"id": "miki", "author": "Miki", "publisher": "Gen Spark",
     "title": "Who Let Me In", "subtitle": "A Guide to Dismantling Imposter Syndrome from the Inside",
     "topic": "imposter_syndrome", "lang": "en"},
    {"id": "omote", "author": "Omote", "publisher": "Gentle Wave",
     "title": "Dark Room, Loud Brain", "subtitle": "A Somatic Guide to Beating Sleep Anxiety",
     "topic": "sleep_anxiety", "lang": "en"},
    {"id": "pamela_fellows", "author": "Pamela Fellows", "publisher": "Body Wisdom",
     "title": "Wired for Worry", "subtitle": "Understanding Your Anxiety Response and How to Rewire It",
     "topic": "anxiety", "lang": "en"},
    {"id": "ra", "author": "Ra", "publisher": "Cosmic Edge",
     "title": "The Proof Was Always You", "subtitle": "Overcoming Imposter Syndrome and Owning Your Worth",
     "topic": "imposter_syndrome", "lang": "en"},
    {"id": "sai_ma", "author": "Sai Maa", "publisher": "Healing Ground Press",
     "title": "Still Here Without You", "subtitle": "Finding Your Way Through Grief and Heartbreak",
     "topic": "grief", "lang": "en"},
]


# ─── CHAPTER PARSER ───────────────────────────────────────────────────

def parse_book_text(text: str) -> list[dict[str, str]]:
    """Parse a book text file into chapters.

    Detects chapter boundaries by looking for:
    - Lines starting with "CHAPTER" or "第" (Chinese)
    - Lines starting with "A NOTE ON THE TEACHINGS" or "教"
    - Lines starting with "WHERE TO GO DEEPER" or "深入"
    - All-caps section headers
    """
    lines = text.split("\n")
    chapters: list[dict[str, str]] = []
    current_title = ""
    current_body: list[str] = []

    chapter_re = re.compile(
        r"^(CHAPTER \d+|Chapter \d+|第[一二三四五六七八九十\d]+章|"
        r"A NOTE ON THE TEACHINGS|教[导導]缘起|"
        r"WHERE TO GO DEEPER|深入修[行炼練]|"
        r"[A-Z][A-Z\s:—\-]{8,}$)",
        re.MULTILINE,
    )

    for line in lines:
        stripped = line.strip()
        if chapter_re.match(stripped) and len(stripped) < 100:
            # Save previous chapter
            if current_title or current_body:
                chapters.append({
                    "title": current_title or "Introduction",
                    "body": "\n".join(current_body).strip(),
                })
            current_title = stripped
            current_body = []
        else:
            current_body.append(line)

    # Save last chapter
    if current_title or current_body:
        chapters.append({
            "title": current_title or "Content",
            "body": "\n".join(current_body).strip(),
        })

    return chapters


# ─── EPUB BUILDER ─────────────────────────────────────────────────────

CSS_STYLE = """
body {
    font-family: Georgia, 'Times New Roman', serif;
    line-height: 1.8;
    margin: 2em;
    color: #2a2a2a;
}
h1, h2 {
    font-family: 'Palatino Linotype', Palatino, serif;
    color: #1a1a1a;
    margin-top: 2em;
    margin-bottom: 0.5em;
}
h1 { font-size: 1.6em; text-align: center; }
h2 { font-size: 1.3em; border-bottom: 1px solid #ddd; padding-bottom: 0.3em; }
p { margin-bottom: 1em; text-indent: 0; }
.pre-intro { font-style: italic; color: #555; }
.exercise { background: #f9f6f0; padding: 1em; border-left: 3px solid #b45309; margin: 1em 0; }
.permission { font-weight: bold; color: #8b4513; }
.publisher { text-align: center; font-size: 0.9em; color: #888; margin-top: 3em; }
.ai-disclosure {
    font-size: 0.8em; color: #999; text-align: center;
    margin-top: 2em; padding: 1em; border-top: 1px solid #eee;
}
"""


def prepare_embedded_ebook_cover(cover_path: Path, *, raw: bool = False) -> tuple[bytes, str]:
    """Bytes + media-type for EPUB cover item.

    When Pillow is available and ``raw`` is False, image is letterboxed to
    :data:`_EBOOK_COVER_W` × :data:`_EBOOK_COVER_H` (1.6:1) so square or odd
    storefront crops do not produce non-portrait EPUB embeds that fail common
    distributor guidance. Output is always PNG for a single predictable spine item.
    """
    ext = cover_path.suffix.lower()
    src_type = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}.get(ext, "image/png")
    raw_bytes = cover_path.read_bytes()
    if raw:
        return raw_bytes, src_type
    try:
        from PIL import Image
    except ImportError:
        logger.warning(
            "Pillow not installed; embedding %s without resize. Install Pillow for KDP-portrait-normalization.",
            cover_path,
        )
        return raw_bytes, src_type

    img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
    w, h = img.size
    tw, th = _EBOOK_COVER_W, _EBOOK_COVER_H
    if abs(w - tw) <= 2 and abs(h - th) <= 2:
        out = img
    else:
        scale = min(tw / w, th / h)
        nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
        resized = img.resize((nw, nh), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (tw, th), (245, 245, 245))
        x0 = (tw - nw) // 2
        y0 = (th - nh) // 2
        canvas.paste(resized, (x0, y0))
        out = canvas
        logger.info(
            "Normalized EPUB cover %s from %d×%d → %d×%d (portrait embed).",
            cover_path,
            w,
            h,
            tw,
            th,
        )
    buf = io.BytesIO()
    out.save(buf, format="PNG", optimize=True)
    return buf.getvalue(), "image/png"


def text_to_html(text: str) -> str:
    """Convert plain text to simple HTML paragraphs."""
    paragraphs = text.split("\n\n")
    html_parts = []
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        # Escape HTML entities
        para = para.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        # Preserve single newlines as <br>
        para = para.replace("\n", "<br/>\n")
        html_parts.append(f"<p>{para}</p>")
    return "\n".join(html_parts)


def build_epub(
    *,
    input_path: Path,
    title: str,
    subtitle: str,
    author: str,
    publisher: str,
    language: str = "en",
    cover_path: Path | None = None,
    output_path: Path,
    topic: str = "",
    raw_cover: bool = False,
    description: str = "",
    disclosure: str = "",
) -> Path:
    """Build a KDP-ready EPUB 3 from a book text file."""
    text = input_path.read_text(encoding="utf-8")
    chapters = parse_book_text(text)

    if not chapters:
        raise ValueError(f"No chapters found in {input_path}")

    book = epub.EpubBook()

    # ── Metadata ──
    uid = hashlib.sha256(f"{author}|{title}|{topic}".encode()).hexdigest()[:16]
    book.set_identifier(f"phoenix-omega-{uid}")
    book.set_title(f"{title}: {subtitle}")
    book.set_language(language)
    book.add_author(author)

    book.add_metadata("DC", "publisher", publisher)
    desc = description.strip() or (
        f"{subtitle}. A therapeutic book by {author}, published by {publisher}. "
        f"Part of the Phoenix Omega series."
    )
    book.add_metadata("DC", "description", desc)
    book.add_metadata("DC", "subject", topic.replace("_", " ").title())
    book.add_metadata("DC", "date", datetime.now(timezone.utc).strftime("%Y-%m-%d"))

    ei_disclosure = disclosure.strip() or (
        "This book was created with AI assistance as part of the Phoenix Omega "
        "therapeutic content system. All content has been reviewed and curated "
        "by human editors. This work is intended for informational purposes "
        "and is not a substitute for professional mental health care."
    )
    book.add_metadata("DC", "rights", ei_disclosure)

    # ── Cover (embedded; storefront upload still uses separate file in distributor UI / our PNG exports) ──
    if cover_path and cover_path.exists():
        cover_data, _media_type = prepare_embedded_ebook_cover(cover_path, raw=raw_cover)
        book.set_cover("cover.png", cover_data, create_page=True)

    # ── Stylesheet ──
    style = epub.EpubItem(
        uid="style",
        file_name="style/default.css",
        media_type="text/css",
        content=CSS_STYLE.encode("utf-8"),
    )
    book.add_item(style)

    # ── Title page ──
    title_html = f"""
    <html><head><link rel="stylesheet" href="style/default.css"/></head>
    <body>
    <h1>{title}</h1>
    <p style="text-align:center; font-size:1.1em; color:#555;">{subtitle}</p>
    <p style="text-align:center; margin-top:2em;">By {author}</p>
    <p class="publisher">{publisher}</p>
    <p class="ai-disclosure">
        {ei_disclosure}
    </p>
    </body></html>
    """
    title_page = epub.EpubHtml(title="Title Page", file_name="title.xhtml", lang=language)
    title_page.content = title_html.encode("utf-8")
    title_page.add_item(style)
    book.add_item(title_page)

    # ── Chapters ──
    epub_chapters = [title_page]
    toc_entries = []

    for i, ch in enumerate(chapters):
        ch_title = ch["title"]
        ch_body = text_to_html(ch["body"])

        ch_html = f"""
        <html><head><link rel="stylesheet" href="style/default.css"/></head>
        <body>
        <h2>{ch_title}</h2>
        {ch_body}
        </body></html>
        """

        ch_item = epub.EpubHtml(
            title=ch_title,
            file_name=f"chapter_{i+1:02d}.xhtml",
            lang=language,
        )
        ch_item.content = ch_html.encode("utf-8")
        ch_item.add_item(style)
        book.add_item(ch_item)
        epub_chapters.append(ch_item)
        toc_entries.append(ch_item)

    # ── Navigation ──
    book.toc = toc_entries
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ["nav"] + epub_chapters

    # ── Write ──
    output_path.parent.mkdir(parents=True, exist_ok=True)
    epub.write_epub(str(output_path), book, {})
    logger.info("Built: %s (%d chapters, %d bytes)", output_path, len(chapters), output_path.stat().st_size)

    return output_path


# ─── BATCH MODE ───────────────────────────────────────────────────────

def build_all(dry_run: bool = False, raw_cover: bool = False) -> list[dict[str, Any]]:
    """Build EPUBs for all 13 teacher books."""
    examples_dir = REPO_ROOT / "artifacts" / "pipeline_examples"
    epub_dir = REPO_ROOT / "artifacts" / "epub"
    results: list[dict[str, Any]] = []

    for book in TEACHER_BOOKS:
        tid = book["id"]
        topic = book["topic"]
        input_path = examples_dir / tid / f"book_{tid}_{topic}_15min.txt"
        cover_path = examples_dir / tid / f"cover_{tid}_{topic}.png"
        output_path = epub_dir / f"{tid}_{topic}.epub"

        if not input_path.exists():
            logger.warning("Missing: %s", input_path)
            results.append({"id": tid, "status": "missing_input", "path": str(input_path)})
            continue

        if dry_run:
            has_cover = cover_path.exists()
            print(f"  [{tid}] {book['title']} → {output_path.name} (cover: {'yes' if has_cover else 'NO'})")
            results.append({"id": tid, "status": "dry_run", "has_cover": has_cover})
            continue

        try:
            path = build_epub(
                input_path=input_path,
                title=book["title"],
                subtitle=book["subtitle"],
                author=book["author"],
                publisher=book["publisher"],
                language=book["lang"],
                cover_path=cover_path if cover_path.exists() else None,
                output_path=output_path,
                topic=topic,
                raw_cover=raw_cover,
            )
            size = path.stat().st_size
            print(f"  ✓ [{tid}] {book['title']} → {path.name} ({size:,} bytes)")
            results.append({"id": tid, "status": "ok", "path": str(path), "size": size})
        except Exception as e:
            logger.error("Failed: %s — %s", tid, e)
            print(f"  ✗ [{tid}] {book['title']} — {e}")
            results.append({"id": tid, "status": "error", "error": str(e)})

    return results


# ─── CLI ──────────────────────────────────────────────────────────────

def main():
    logging.basicConfig(level=logging.INFO, format="%(name)s %(levelname)s %(message)s")

    parser = argparse.ArgumentParser(description="Build KDP-ready EPUBs from book texts")
    parser.add_argument("--input", type=Path, help="Input book text file")
    parser.add_argument("--title", help="Book title")
    parser.add_argument("--subtitle", default="", help="Book subtitle")
    parser.add_argument("--author", help="Author name")
    parser.add_argument("--publisher", default="Phoenix Omega", help="Publisher name")
    parser.add_argument("--cover", type=Path, help="Cover image path")
    parser.add_argument("--output", type=Path, help="Output EPUB path")
    parser.add_argument("--language", default="en", help="Language code")
    parser.add_argument("--topic", default="", help="Topic for metadata")
    parser.add_argument("--batch", action="store_true", help="Build all 13 teacher books")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be built")
    parser.add_argument(
        "--raw-cover",
        action="store_true",
        help="Embed the source cover file as-is (skip 1600×2560 letterbox normalization)",
    )
    parser.add_argument("--description", default="", help="DC description metadata")
    parser.add_argument("--disclosure", default="", help="Title-page EI disclosure (not AI boilerplate)")

    args = parser.parse_args()

    if args.batch:
        print(f"=== EPUB BATCH BUILD — {len(TEACHER_BOOKS)} BOOKS ===\n")
        results = build_all(dry_run=args.dry_run, raw_cover=args.raw_cover)
        ok = sum(1 for r in results if r["status"] == "ok")
        print(f"\n{'DRY-RUN: ' if args.dry_run else ''}{ok}/{len(results)} built")
        return

    if not args.input:
        parser.error("--input or --batch required")

    build_epub(
        input_path=args.input,
        title=args.title or "Untitled",
        subtitle=args.subtitle,
        author=args.author or "Unknown",
        publisher=args.publisher,
        language=args.language,
        cover_path=args.cover,
        output_path=args.output or Path(f"{args.input.stem}.epub"),
        topic=args.topic,
        raw_cover=args.raw_cover,
        description=args.description,
        disclosure=args.disclosure,
    )


if __name__ == "__main__":
    main()
