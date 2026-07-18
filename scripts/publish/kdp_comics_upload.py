#!/usr/bin/env python3
"""KDP Comics & Graphic Novels package builder.

Amazon KDP requires manual upload via the KDP Dashboard web UI — there is
no public KDP upload API. This script produces an upload-ready package
that a human (or browser-automation later) can paste into the KDP form.

Output package (per book):
  <out_dir>/
    interior.pdf                  — Print-ready interior PDF (KDP fixed-layout)
    interior.epub                 — Reflowable EPUB for ebook listing
    cover_<trim>.jpg              — Cover image at KDP-required dimensions
    metadata.json                 — Title, subtitle, description, BISAC, keywords,
                                    pricing, AI disclosure, author bio
    upload_checklist.md           — Step-by-step manual paste guide
    ai_disclosure.txt             — Required AI disclosure text per ai_policy_blockers.yaml
    README.md                     — Package summary

Reads:
  config/publishing/ai_policy_blockers.yaml  (via _policy_loader)
  config/source_of_truth/book_plans_en_us/<book_id>.yaml  (book metadata)
  artifacts/pearl_prime_en_us/sample_books/<book_id>.txt  (rendered prose)
  assets/manga_catalog/<brand>/<series>/main_character.png  (cover base)

Refuses to build a package if KDP policy status changes to BLOCKED.

Usage:
    python3 scripts/publish/kdp_comics_upload.py \\
      --book-id stillness_press__ahjan__gen_z_professionals__anxiety__false_alarm \\
      --out artifacts/upload_packages/kdp/

This is a PACKAGE BUILDER, not a network uploader. KDP web-UI submission
is a separate manual step performed by the operator using the produced
package.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Make the repo root importable so _policy_loader resolves
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from scripts.publish._policy_loader import (  # noqa: E402
    PolicyError,
    assert_target_allowed,
    disclosure_text,
)


PLATFORM_ID = "amazon_kdp_comics"
KDP_TRIM_SIZES = {
    "graphic_novel_5x8": (5.0, 8.0),
    "graphic_novel_5_25x8": (5.25, 8.0),
    "graphic_novel_6x9": (6.0, 9.0),
    "manga_5_06x7_81": (5.06, 7.81),  # JP B6 closest KDP equivalent
}
KDP_MAX_KEYWORDS = 7
KDP_MAX_BISAC = 3


def _load_book_plan(book_id: str) -> dict[str, Any]:
    import yaml

    p = REPO / "config" / "source_of_truth" / "book_plans_en_us" / f"{book_id}.yaml"
    if not p.exists():
        raise FileNotFoundError(f"Book plan not found: {p}")
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def _build_metadata_json(book_plan: dict[str, Any], pol: dict[str, Any]) -> dict[str, Any]:
    """Map book_plan fields → KDP submission metadata schema."""
    desc_block = book_plan.get("description") or {}
    keywords = (book_plan.get("keywords") or {}).get("primary", []) or []
    bisac = book_plan.get("bisac_codes") or []
    target_price = book_plan.get("target_price") or {}

    return {
        "platform": "amazon_kdp_comics",
        "platform_status": pol["status"],
        "book_id": book_plan.get("book_id"),
        "title": book_plan.get("title"),
        "subtitle": book_plan.get("subtitle"),
        "author_pen_name": (book_plan.get("author_positioning") or {}).get("teacher", ""),
        "language": "en_US",
        "description_short": (desc_block.get("short_blurb") or "").strip(),
        "description_long": (desc_block.get("long_description") or "").strip(),
        "categories": {
            # KDP allows max 3 BISAC codes per format
            "bisac_primary": bisac[:KDP_MAX_BISAC],
        },
        "keywords": {
            # KDP allows max 7 keywords
            "kdp": keywords[:KDP_MAX_KEYWORDS],
        },
        "pricing": {
            "ebook_usd": target_price.get("ebook_usd"),
            "paperback_usd": target_price.get("paperback_usd"),
            "kdp_select_enrolled": True,  # 70% royalty path
            "royalty_tier": "70%",
        },
        "ai_disclosure": {
            "required": pol["disclosure_required"],
            "text": disclosure_text(PLATFORM_ID),
            "kdp_field": "publication_information.contains_ai_content",
            "value": "Yes — text and images both AI-assisted",
        },
        "trim_size_recommended": "graphic_novel_6x9",  # KDP standard for manga
        "interior": {
            "format": "fixed_layout_pdf",
            "color": "bw",  # default — set color: yes for color page manga
            "page_size_inches": [6.0, 9.0],
            "bleed": "include_bleed",
        },
        "cover": {
            "format": "jpg",
            "min_resolution_px": [2560, 4096],
            "color_space": "RGB",
        },
        "comp_titles": book_plan.get("comp_titles") or [],
        "main_character": {
            "name": book_plan.get("main_character_name"),
            "lora_id": book_plan.get("main_character_lora_id"),
        },
        "manuscript_word_count": book_plan.get("target_word_range"),
    }


def _build_checklist_md(book_plan: dict[str, Any], pol: dict[str, Any]) -> str:
    return f"""# KDP Upload Checklist — {book_plan.get('title','(untitled)')}

**Book ID:** {book_plan.get('book_id','')}
**Platform status:** {pol['status']}
**AI disclosure required:** {pol['disclosure_required']}

## Step 1 — KDP Bookshelf
1. Log in to https://kdp.amazon.com → Bookshelf → Create New Title → Kindle eBook
2. Paste **Title** + **Subtitle** from `metadata.json`
3. Author: paste **author_pen_name** from `metadata.json`
4. Description: paste `description_long` (HTML allowed for `<i>` `<b>`)

## Step 2 — Categories + Keywords
5. BISAC categories (max 3): paste `categories.bisac_primary`
6. Keywords (max 7): paste `keywords.kdp` one per slot

## Step 3 — Content
7. Upload `interior.epub` (reflowable) OR `interior.pdf` (fixed-layout — recommended for manga)
8. Upload `cover_graphic_novel_6x9.jpg` to Cover slot

## Step 4 — AI disclosure (REQUIRED — non-skippable as of 2024)
9. Publication Information → "Does your book contain AI-generated content?" → **Yes**
10. Paste `ai_disclosure.text` from `metadata.json` into the "Describe how AI was used" field

## Step 5 — Pricing
11. KDP Select enrollment: **YES** (gives 70% royalty + KU bonus)
12. Marketplaces: Worldwide
13. eBook list price: ${book_plan.get('target_price',{}).get('ebook_usd', '?')}
14. Royalty tier: 70%

## Step 6 — Save & Publish
15. Save as Draft → review preview
16. Submit for Publication

## Verify after publish
- [ ] Title appears in Amazon search within 24-72h
- [ ] Categories show correctly
- [ ] AI disclosure visible on product page (Amazon adds "Created with AI" tag automatically)
- [ ] KENP page count populated within 7d if KU-enrolled

## Source
Per `config/publishing/ai_policy_blockers.yaml` → `amazon_kdp_comics`:
{pol['rationale'] or 'AI permitted with disclosure. 70% royalty at $2.99-9.99.'}

Source citation: {pol['source']}
"""


def build_package(book_id: str, out_dir: Path) -> dict[str, Any]:
    # Step 1: consult policy. Raise PolicyError if KDP becomes BLOCKED.
    pol = assert_target_allowed(PLATFORM_ID)

    # Step 2: load book plan
    book_plan = _load_book_plan(book_id)

    # Step 3: assemble package
    pkg_dir = out_dir / book_id
    pkg_dir.mkdir(parents=True, exist_ok=True)

    metadata = _build_metadata_json(book_plan, pol)
    (pkg_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    (pkg_dir / "ai_disclosure.txt").write_text(
        disclosure_text(PLATFORM_ID), encoding="utf-8"
    )

    (pkg_dir / "upload_checklist.md").write_text(
        _build_checklist_md(book_plan, pol), encoding="utf-8"
    )

    # README summarizing the package
    readme = (
        f"# KDP Comics package — {book_plan.get('title', book_id)}\n\n"
        f"Built: {book_id}\n"
        f"Platform: {PLATFORM_ID} (status={pol['status']})\n\n"
        f"## Files in this package\n"
        f"- metadata.json — paste-ready KDP form fields\n"
        f"- upload_checklist.md — step-by-step manual upload guide\n"
        f"- ai_disclosure.txt — required AI disclosure text\n"
        f"- (TODO) interior.pdf / interior.epub — produced by manga assembly pipeline\n"
        f"- (TODO) cover_*.jpg — produced by cover generation pipeline\n\n"
        f"## Status\n"
        f"This package is a planning shell. Interior + cover production pipeline\n"
        f"connects in a follow-up PR. Until then, upload_checklist.md gives the\n"
        f"operator the manual steps + metadata.json gives the form-paste fields.\n"
    )
    (pkg_dir / "README.md").write_text(readme, encoding="utf-8")

    return {
        "package_dir": str(pkg_dir),
        "files_written": ["metadata.json", "ai_disclosure.txt", "upload_checklist.md", "README.md"],
        "policy_status": pol["status"],
        "disclosure_required": pol["disclosure_required"],
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--book-id", required=True, help="book_id from book_plans_en_us/")
    p.add_argument("--out", default="artifacts/upload_packages/kdp/", help="Output dir")
    args = p.parse_args()

    try:
        result = build_package(args.book_id, REPO / args.out)
    except PolicyError as e:
        print(f"❌ POLICY: {e}", file=sys.stderr)
        return 1
    except FileNotFoundError as e:
        print(f"❌ MISSING: {e}", file=sys.stderr)
        return 2

    print(f"✓ Package built at {result['package_dir']}")
    print(f"  Status: {result['policy_status']}")
    print(f"  Disclosure required: {result['disclosure_required']}")
    print(f"  Files: {', '.join(result['files_written'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
