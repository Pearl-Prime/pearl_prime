#!/usr/bin/env python3
"""
Build the operator QA packet — single Markdown report for review/approval
before launch. Pure read-only analysis against current main.

What it produces:
  docs/OPERATOR_QA_PACKET_2026-04-29.md — the master report

Sections:
  1. Top 50 launch candidates (full row detail)
  2. Top 10 per locale (en_US / ja_JP / zh_TW / zh_CN)
  3. Teacher showcase QA checklist (13 teachers × 6 asset types)
  4. Image / audio QA checklist (presence-by-teacher matrix)
  5. CTA replacement list (every #book-/#audio-/#guide- anchor → needs real URL)

No catalog mutation, no LLM, no asset generation.
"""

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LB_DIR = ROOT / "artifacts/catalog/launch_baseline"
SHOWCASE = ROOT / "brand-wizard-app/public/teacher_showcase.html"
ASSETS = ROOT / "brand-wizard-app/public/assets"
TEACHER_PICS = ROOT / "brand-wizard-app/public/teacher_pics"

OUT = ROOT / "docs" / "OPERATOR_QA_PACKET_2026-04-29.md"

LOCALES = ("en_US", "ja_JP", "zh_TW", "zh_CN")
TEACHERS = (
    "ahjan", "adi_da", "master_feung", "sai_ma", "ra", "junko", "miki",
    "master_wu", "pamela_fellows", "joshin", "maat", "omote", "master_sha",
)


def load_csv(path):
    if not path.exists():
        return []
    return list(csv.DictReader(open(path)))


def find_source_row_id(loc, brand, topic, persona, teacher):
    """Find the original CSV row index for this Pearl Prime entry (1-based, header=1)."""
    p = ROOT / f"artifacts/catalog/pearl_prime_book_script_catalogs/{loc}_catalog.csv"
    if not p.exists():
        return None, None
    with open(p) as fh:
        for i, r in enumerate(csv.DictReader(fh), start=2):  # row 1 is header
            if (r["brand"] == brand and r["topic"] == topic
                    and r["persona"] == persona and r["teacher_id"] == teacher):
                return i, p.relative_to(ROOT)
    return None, p.relative_to(ROOT)


def asset_present(rel_path):
    return (ROOT / rel_path).exists()


def collect_teacher_assets():
    """Per teacher: presence map for portrait, audiobook ch1, podcast, hook,
    video reel, youtube, manga covers, manga panels."""
    audiobook_dir = ASSETS / "audio" / "audiobook_chapters"
    hook_dir = ASSETS / "audio" / "showcase"
    podcast_dir = ASSETS / "audio" / "podcast"
    reels_dir = ASSETS / "video" / "teacher_reels"
    youtube_dir = ASSETS / "video" / "youtube"
    manga_covers = ASSETS / "manga_covers"
    manga_panels = ASSETS / "manga_panels"

    out = {}
    for t in TEACHERS:
        # Portrait
        portrait = TEACHER_PICS / f"{t}.png"
        # Audiobook ch1 — match {teacher}_*_ch1.mp3
        ch1 = (list(audiobook_dir.glob(f"{t}_*_ch1.mp3"))
               if audiobook_dir.exists() else [])
        # Hook MP3
        hook = (list(hook_dir.glob(f"{t}_*_hook.mp3"))
                if hook_dir.exists() else [])
        # Podcast 3min
        podcast = podcast_dir / f"{t}_podcast_3min.mp3"
        # Video reel — files vary: master_wu → wu_reel.mp4; others → {t}_reel.mp4
        reel_candidates = [
            reels_dir / f"{t}_reel.mp4",
            reels_dir / f"{t.replace('master_', '')}_reel.mp4",
        ]
        reel_path = next((p for p in reel_candidates if p.exists()), None)
        # YouTube
        yt = list(youtube_dir.glob(f"{t}*.mp4")) if youtube_dir.exists() else []
        # Manga cover
        mcover = (list(manga_covers.glob(f"{t}_cover_*.png"))
                  if manga_covers.exists() else [])
        # Manga panels — directory with page_*.png
        mpanels_dir = manga_panels / t
        mpanels = (list(mpanels_dir.glob("page_*.png"))
                   if mpanels_dir.exists() else [])

        out[t] = {
            "portrait": portrait if portrait.exists() else None,
            "audiobook_ch1": ch1[0] if ch1 else None,
            "hook_mp3": hook[0] if hook else None,
            "podcast_mp3": podcast if podcast.exists() else None,
            "reel_mp4": reel_path,
            "youtube_mp4": yt[0] if yt else None,
            "manga_cover": mcover[0] if mcover else None,
            "manga_panels_count": len(mpanels),
        }
    return out


def collect_cta_anchors():
    """Find every #book-/#audio-/#guide- anchor in teacher_showcase.html."""
    if not SHOWCASE.exists():
        return {}
    txt = open(SHOWCASE).read()
    anchors = set()
    for m in re.finditer(r'#(book|audio|guide|listen|free|read)-([a-z_]+)', txt):
        anchors.add((m.group(1), m.group(2)))
    return sorted(anchors)


def md_table(headers, rows):
    sep = "|" + "|".join("---" for _ in headers) + "|"
    head_row = "| " + " | ".join(headers) + " |"
    body = "\n".join("| " + " | ".join(str(c) for c in r) + " |" for r in rows)
    return head_row + "\n" + sep + ("\n" + body if body else "")


def build():
    top50 = load_csv(LB_DIR / "top_50_combined.csv")
    top10_combined = load_csv(LB_DIR / "top_10_per_locale_combined.csv")
    summary = json.load(open(LB_DIR / "launch_baseline_data.json"))
    assets = collect_teacher_assets()
    ctas = collect_cta_anchors()

    lines = []
    lines.append("# Operator QA Packet — Pearl Prime Catalog Launch Review")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append(f"**Branch state:** `origin/main` post-#796 (final launch report) + #792 (cluster analyzer)")
    lines.append("**Purpose:** show the operator what to approve. No catalog or generation changes.")
    lines.append("**Reproduction:** `python3 scripts/catalog/build_operator_qa_packet.py`")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## How to use this packet")
    lines.append("")
    lines.append("1. Skim §1 (Top 50) and §2 (Top 10 per locale) — pick 10–20 to launch first.")
    lines.append("2. Walk §3 (teacher showcase QA checklist) — mark each row approve / reject / fix.")
    lines.append("3. Walk §4 (image/audio asset matrix) — flag missing or low-quality assets.")
    lines.append("4. Fill §5 (CTA replacement list) — provide real storefront / freebie URLs to replace placeholders.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ───────── §1 — Top 50 ─────────
    lines.append("## §1 — Top 50 launch candidates")
    lines.append("")
    lines.append(f"Source: [`{(LB_DIR / 'top_50_combined.csv').relative_to(ROOT)}`]({(LB_DIR / 'top_50_combined.csv').relative_to(ROOT)})")
    lines.append("")
    lines.append("Each row links to its source catalog CSV with a row index "
                  "(`source_row` is 1-based; row 1 = CSV header, so row 2 = first data row).")
    lines.append("")
    headers50 = ["#", "Lane", "Locale", "Brand", "Topic/Genre", "Persona",
                 "Teacher", "Composite", "Title", "Subtitle", "Source row"]
    rows50 = []
    for i, r in enumerate(top50, start=1):
        if r["lane"] == "book_script":
            row_id, src = find_source_row_id(
                r["locale"], r["brand"], r["subject"],
                r.get("persona", ""), r.get("teacher", ""))
            src_link = f"[{r['locale']} #{row_id}]({src})" if row_id else "—"
        else:
            src_link = "manga (see manga catalog)"
        rows50.append([
            i, r["lane"], r["locale"], r["brand"], r["subject"],
            r.get("persona", "—"), r.get("teacher", "—"),
            f"{float(r['normalized_score']):.2f}",
            r.get("title", ""), (r.get("subtitle") or "")[:60].replace("|", "\\|"),
            src_link,
        ])
    lines.append(md_table(headers50, rows50))
    lines.append("")
    lines.append("---")
    lines.append("")

    # ───────── §2 — Top 10 per locale ─────────
    lines.append("## §2 — Top 10 per locale")
    lines.append("")
    by_loc = defaultdict(list)
    for r in top10_combined:
        by_loc[r["locale"]].append(r)
    for loc in LOCALES:
        rows = by_loc[loc][:10]
        lines.append(f"### §2.{LOCALES.index(loc) + 1} — {loc}")
        lines.append("")
        lines.append(f"Source: [`{(LB_DIR / f'top_10_book_scripts_{loc}.csv').relative_to(ROOT)}`]({(LB_DIR / f'top_10_book_scripts_{loc}.csv').relative_to(ROOT)})")
        lines.append("")
        headers = ["#", "Brand", "Topic", "Persona", "Teacher", "Composite",
                   "Title", "Source row"]
        body = []
        for i, r in enumerate(rows, start=1):
            row_id, src = find_source_row_id(
                loc, r["brand"], r["subject"],
                r.get("persona", ""), r.get("teacher", ""))
            src_link = f"[#{row_id}]({src})" if row_id else "—"
            body.append([
                i, r["brand"], r["subject"], r["persona"], r["teacher"],
                f"{float(r['normalized_score']):.2f}",
                r.get("title", ""),
                src_link,
            ])
        lines.append(md_table(headers, body))
        lines.append("")
    lines.append("---")
    lines.append("")

    # ───────── §3 — Teacher showcase QA checklist ─────────
    lines.append("## §3 — Teacher showcase QA checklist")
    lines.append("")
    lines.append(f"Source: [`{SHOWCASE.relative_to(ROOT)}`]({SHOWCASE.relative_to(ROOT)})")
    lines.append("")
    lines.append("13 teacher sections present. Walk each row, mark approve / reject / needs_fix.")
    lines.append("")
    qa_headers = ["Teacher", "Portrait", "Audiobook Ch1", "Showcase Hook",
                   "Podcast 3min", "Video Reel", "YouTube", "Manga Cover",
                   "Manga Panels", "Reviewer mark"]
    qa_body = []
    for t in TEACHERS:
        a = assets[t]
        def mk(p): return f"✅ `{p.relative_to(ROOT)}`" if p else "❌ MISSING"
        qa_body.append([
            f"`{t}`",
            mk(a["portrait"]),
            mk(a["audiobook_ch1"]),
            mk(a["hook_mp3"]),
            mk(a["podcast_mp3"]),
            mk(a["reel_mp4"]),
            mk(a["youtube_mp4"]),
            mk(a["manga_cover"]),
            f"✅ {a['manga_panels_count']} pages" if a["manga_panels_count"] else "❌ 0 pages",
            "[ ] approve  [ ] reject  [ ] needs_fix",
        ])
    lines.append(md_table(qa_headers, qa_body))
    lines.append("")

    # Aggregated gaps
    missing_yt = sum(1 for t in TEACHERS if not assets[t]["youtube_mp4"])
    missing_reel = sum(1 for t in TEACHERS if not assets[t]["reel_mp4"])
    lines.append("### §3.1 — Aggregate gaps")
    lines.append("")
    lines.append(f"- **YouTube videos:** {missing_yt} of 13 teachers missing — `assets/video/youtube/` dir absent on disk")
    lines.append(f"- **Video reels:** {missing_reel} of 13 teachers missing reels in `assets/video/teacher_reels/`")
    lines.append("- **Locale page variants:** only en_US fully wired today; ja_JP / zh_TW / zh_CN page versions are TBD downstream of this catalog")
    lines.append("")
    lines.append("### §3.2 — Manual QA pass instructions")
    lines.append("")
    lines.append("For each teacher row above:")
    lines.append("1. Open the page locally: `cd brand-wizard-app && npm run dev` (or open the HTML file directly).")
    lines.append("2. Scroll to `#{teacher_slug}` section.")
    lines.append("3. Click each format card's play/pause control; verify audio plays.")
    lines.append("4. Click each format card's cover; verify it opens / loads.")
    lines.append("5. Mark approve / reject / needs_fix in the table column.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ───────── §4 — Image/audio QA matrix ─────────
    lines.append("## §4 — Image / audio asset QA matrix")
    lines.append("")
    lines.append("Same data as §3 with explicit reviewer slots per asset (not per teacher). "
                 "Use this when doing a focused asset-by-asset pass.")
    lines.append("")
    asset_types = [
        ("Portrait", "portrait"),
        ("Audiobook Ch1", "audiobook_ch1"),
        ("Showcase Hook", "hook_mp3"),
        ("Podcast 3min", "podcast_mp3"),
        ("Video Reel", "reel_mp4"),
        ("YouTube", "youtube_mp4"),
        ("Manga Cover", "manga_cover"),
    ]
    for label, key in asset_types:
        lines.append(f"### §4.{[k for _, k in asset_types].index(key) + 1} — {label}")
        lines.append("")
        h = ["Teacher", "Path", "Reviewer mark"]
        b = []
        for t in TEACHERS:
            p = assets[t][key]
            path_md = f"`{p.relative_to(ROOT)}`" if p else "❌ **MISSING**"
            b.append([f"`{t}`", path_md,
                      "[ ] approve  [ ] reject  [ ] needs_fix"])
        lines.append(md_table(h, b))
        lines.append("")
    lines.append("---")
    lines.append("")

    # ───────── §5 — CTA replacement list ─────────
    lines.append("## §5 — CTA placeholder replacement list")
    lines.append("")
    lines.append("These anchors in [`teacher_showcase.html`](" +
                 str(SHOWCASE.relative_to(ROOT)) + ") are placeholders. "
                 "Operator: provide real URLs to replace each.")
    lines.append("")
    cta_h = ["Anchor", "Teacher", "Real URL (operator fills)", "Notes"]
    cta_b = []
    for kind, teacher in ctas:
        cta_b.append([f"`#{kind}-{teacher}`", f"`{teacher}`", "", ""])
    lines.append(md_table(cta_h, cta_b))
    lines.append("")
    lines.append(f"**Total CTA placeholders:** {len(ctas)}")
    lines.append("")

    # Categorize what each CTA kind should point at
    lines.append("### §5.1 — Suggested URL targets per CTA kind")
    lines.append("")
    lines.append("| CTA prefix | Suggested target | Notes |")
    lines.append("|---|---|---|")
    lines.append("| `#book-{teacher}` | Amazon KDP / Apple Books / storefront link to teacher's flagship book | If multiple titles per teacher, pick the highest-composite-score Pearl Prime entry from §1 |")
    lines.append("| `#audio-{teacher}` | Audible / Spotify / podcast platform URL | Or in-page anchor to the audio player block if no external URL yet |")
    lines.append("| `#guide-{teacher}` | (Not currently in HTML) — would point at `/free/{slug}` freebie | Operator to confirm whether this CTA kind is needed at all |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ───────── §6 — Snapshot summary ─────────
    lines.append("## §6 — Snapshot summary")
    lines.append("")
    totals = summary.get("totals", {})
    lines.append("**Catalog readiness (from `launch_baseline_data.json`):**")
    lines.append("")
    lines.append(f"- Pearl Prime listing-ready: {totals.get('pearl_prime_listing_ready', 0):,}")
    lines.append(f"- Pearl Prime blocked_score (zh_TW only): {totals.get('pearl_prime_blocked_score', 0):,}")
    lines.append(f"- Manga ready: {totals.get('manga_ready', 0):,}")
    lines.append(f"- Manga awaiting manual image QA: {totals.get('manga_image_qa_pending', 0):,}")
    lines.append("")
    lines.append("**Top 50 split:**")
    lines.append("")
    lane_split = summary.get("top_50_lane_split", {})
    locale_split = summary.get("top_50_locale_split", {})
    lines.append(f"- by lane: {lane_split}")
    lines.append(f"- by locale: {locale_split}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## §7 — Stop / next")
    lines.append("")
    lines.append("After reviewing this packet:")
    lines.append("- Pick the 10–20 launch set from §1 / §2.")
    lines.append("- Send back §3 / §4 with reviewer marks.")
    lines.append("- Send back §5 with real URLs.")
    lines.append("")
    lines.append("Catalog system is sealed. No further engineering required from this packet.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"  → wrote {OUT}")
    print(f"  total CTA placeholders: {len(ctas)}")
    print(f"  teachers missing reels:  {missing_reel}/13")
    print(f"  teachers missing youtube: {missing_yt}/13")


if __name__ == "__main__":
    build()
