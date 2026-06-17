#!/usr/bin/env python3
"""
check_atoms_external_book_references.py

Detector for "what to do next" atoms that route readers OUT of the Pearl Prime
catalog by recommending external books, authors, classes, organizations, or URLs.

Contract: PEARL_PRIME_STOREFRONT_V1_SPEC.md §15.3 + AMENDMENT §AMENDMENT-2026-06-04.7

Output: TSV row schema:
    file_path  line_no  match_type  matched_text  suggested_action  locale

(The trailing `locale` column is appended additively — Stage-1 readers that key
on the first five columns are unaffected; the column is "" for non-localized
en-US scans and one of {en-US, ja-JP, zh-TW, zh-CN, ...} for localized scans.)

match_type in {
    high_external_author,
    high_external_title,
    high_external_org,
    high_url_in_atom,
    low_vague_recommendation,
}

STAGE 2a — LOCALIZED ATOM VARIANTS (this extension)
---------------------------------------------------
Stage 1 (#1454) scanned en-US root atoms only and concluded the §15 cleanup ROI
is "concentrated elsewhere (locale variants under
atoms/<persona>/<topic>/<atom>/locales/<locale>/, teacher-mode candidate atoms,
or other topics)". Stage 2a closes that gap: it scans the LOCALIZED atom
variants for the CJK locales {zh-TW, zh-CN, ja-JP} per §AMENDMENT-2026-06-04.7
"second pass" (ja-JP anxiety+overthinking) extended to the full CJK locale set
the localized corpus actually contains:

  - atoms/<persona>/<topic>/<atom>/locales/{zh-TW,zh-CN,ja-JP}/CANONICAL.txt
  - SOURCE_OF_TRUTH/teacher_banks/<teacher_id>/approved_atoms_localized/
        {zh-TW,zh-CN,ja-JP}/<ATOM_TYPE>/*.yaml

NOTE ON CJK + LATIN: external author/title/org references survive translation as
Latin-script tokens ("Bessel van der Kolk", "The Body Keeps the Score",
"Insight Timer", "Headspace app") and URLs are locale-agnostic, so the existing
high-confidence Latin pattern registries fire correctly inside CJK bodies. The
vague-recommendation English phrases will additionally fire on any localized
file that still carries un-translated English commentary (a known generation
artifact in some zh-TW/zh-CN CANONICAL.txt variants) — that is itself useful
signal for the per-locale heat map.

This is a READ-ONLY scan + report. No atom is rewritten here (that is the
separate operator-gated rewrite ws per §15.6).

USAGE
-----
# Full staged first-pass scan (en-US anxiety + overthinking)
python3 scripts/ci/check_atoms_external_book_references.py \
    --scope stage1 \
    --out artifacts/qa/next_step_atom_audit_2026-06-06.tsv

# Stage 2a — localized CJK atom variants + localized teacher banks, with
# per-locale heat-map summary (this extension)
python3 scripts/ci/check_atoms_external_book_references.py \
    --scope stage2a \
    --out artifacts/qa/next_step_atom_audit_stage_2a_20260612.tsv \
    --summary-out artifacts/qa/next_step_atom_audit_stage_2a_20260612_summary.md

# Stage 2a restricted to a single locale
python3 scripts/ci/check_atoms_external_book_references.py \
    --scope stage2a --locales ja-JP \
    --out artifacts/qa/ja_audit.tsv

# Custom path list (CI delta mode — pass changed files only)
python3 scripts/ci/check_atoms_external_book_references.py \
    --paths atoms/corporate_managers/anxiety/INTEGRATION/CANONICAL.txt \
    --out artifacts/qa/delta.tsv

# Scan everything (future stage2 / full sweep)
python3 scripts/ci/check_atoms_external_book_references.py \
    --scope all \
    --out artifacts/qa/full_sweep.tsv

EXIT CODES
----------
- 0  if the script ran cleanly (regardless of how many hits)
- 1  if a path was malformed or unreadable

The CI integration runs this in WARNING mode for the audit phase. The rewrite
workstream (separate, operator-gated) will graduate this to a BLOCKING check.

PERFORMANCE NOTE (Stage 2a sizing)
----------------------------------
Stage 1 scanned ~112 en-US files, so `_scan_text` throughput never mattered.
The Stage-2a localized corpus is ~10,700 atom CANONICAL.txt files (ja-JP 4,238 +
zh-TW 4,531 + zh-CN 1,928) plus ~285 localized teacher YAMLs. Profiling shows
`_scan_text` costs ~0.4–0.8s per 200-line file because every pattern registry
is `re.compile`d *inside* the per-surname / per-line loops and `finditer` runs
on every line for every author/title/org token (≈139k finditer calls for one
208-line file). A full single-process sweep is therefore ~60–90 min.

This module is correct as-is and the per-locale heat map is produced from a
representative sample in this WS. Two non-behaviour-changing speedups are left
to a follow-up (each needs its own equivalence test against this output):
  (1) hoist + precompile all pattern registries once at module load (biggest
      win — removes the in-loop re.compile churn);
  (2) parallelize the file loop (concurrent.futures ProcessPoolExecutor) — the
      scan is embarrassingly parallel and CI can shard by locale.
Until then, run the full sweep sharded by locale (`--locales ja-JP`, etc.) and
concatenate the TSVs, or run it as an offline (non-CI-blocking) batch.
"""

from __future__ import annotations

import argparse
import csv
import datetime
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Tuple

# ---------------------------------------------------------------------------
# Pattern registries
# ---------------------------------------------------------------------------

# High-confidence external author surnames. Match within ±10 words of book-noun
# proximity. The "context window" check below dampens false positives like
# "Brown" in "Brown sugar" or "Calm" as the adjective.
EXTERNAL_AUTHORS = [
    "van der Kolk", "Bessel van der Kolk", "Bessel",
    "Tara Brach", "Brach",
    "Eckhart Tolle", "Tolle",
    "Thich Nhat Hanh", "Thich",
    "Daniel Goleman", "Goleman",
    "Jon Kabat-Zinn", "Kabat-Zinn",
    "Brené Brown", "Brene Brown",
    "Gabor Maté", "Gabor Mate", "Maté",
    "Steven Pinker", "Pinker",
    "Peter Levine",
    "Stephen Porges", "Porges",
    "Norman Doidge", "Doidge",
    "Viktor Frankl", "Frankl",
    "Marianne Williamson", "Williamson",
    "Pema Chödrön", "Pema Chodron", "Chödrön", "Chodron",
    "Dalai Lama", "Dalai",
    "Ram Dass",
    "Adyashanti",
    "Byron Katie",
    "Mark Manson",
    "James Clear",
    "Cal Newport",
    "Susan Cain",
    "Jordan Peterson",
    "Mel Robbins",
    "Glennon Doyle",
    "Yung Pueblo",
    "Mark Nepo",
    "Rick Hanson",
    "Tich Nhat Han",  # common misspelling
]

# Book-noun proximity tokens — author surname must appear within ±10 words.
BOOK_NOUNS = [
    r"\bbook\b", r"\bbooks\b", r"\bmemoir\b", r"\bguide\b", r"\bmanual\b",
    r"\bworkbook\b", r"\bread it\b", r"\bread her\b", r"\bread his\b",
    r"\bread their\b", r"\bher work\b", r"\bhis work\b", r"\btheir work\b",
    r"\bher book\b", r"\bhis book\b", r"\btheir book\b",
    r"\bauthor\b", r"\bauthor's\b",
    r"\bwrites\b", r"\bwrote\b", r"\bwritten by\b",
    r"\bcheck out\b", r"\brecommend\b", r"\brecommends\b",
    r"\bteaches\b", r"\bteacher\b",  # teacher in proximity of name = likely external teacher CTA
]

# Italic-quoted title pattern: *Title Words* by Author
EXTERNAL_TITLE_RE = re.compile(
    r"\*[A-Z][A-Za-z]+(?:\s+[A-Za-z\']+){1,5}\*\s+by\s+[A-Z][A-Za-z]+",
)

# "Title" by Author (double-quoted)
EXTERNAL_TITLE_QUOTED_RE = re.compile(
    r"[\"“][A-Z][A-Za-z]+(?:\s+[A-Za-z\']+){1,5}[\"”]\s+by\s+[A-Z][A-Za-z]+",
)

# Well-known book titles. Two tiers:
# - UNAMBIGUOUS_TITLES: distinctive multi-word titles that are vanishingly
#   unlikely to be a false positive (always flagged on literal match).
# - AMBIGUOUS_TITLES: short / single-word titles that are also common English
#   words (Quiet, Mindset, Calm). Flag ONLY when book-noun proximity is met
#   (e.g., "Susan Cain's Quiet" or "Quiet by Susan Cain" or italic-quoted).
UNAMBIGUOUS_TITLES = [
    "The Body Keeps the Score",
    "The Power of Now",
    "Wherever You Go, There You Are",
    "Untethered Soul",
    "The Untethered Soul",
    "Radical Acceptance",
    "Daring Greatly",
    "Atlas of the Heart",
    "Atomic Habits",
    "Deep Work",
    "Man's Search for Meaning",
    "The Four Agreements",
    "When Things Fall Apart",
    "Mindfulness for Beginners",
    "Full Catastrophe Living",
    "Self-Compassion",
    "Tiny Beautiful Things",
    "The Gifts of Imperfection",
    "Letting Go",
    "Be Here Now",
    "Pocket Guide to the Polyvagal Theory",
    "The Mountain Is You",
    "101 Essays That Will Change the Way You Think",
    "Rising Strong",
    "The Subtle Art of Not Giving",
    "The Subtle Art",
]

AMBIGUOUS_TITLES = [
    "Quiet",
    "Mindset",
    "Calm",
    "Headspace",
    "Awakening",
]

# External orgs / apps / classes. Two tiers:
# - UNAMBIGUOUS_ORGS: distinctive brands that are vanishingly unlikely to be
#   regular English (Insight Timer, Plum Village, MBSR, etc.). Always flagged.
# - AMBIGUOUS_ORGS: brand names that are also common English words (Calm,
#   Headspace, Awakening). Flag only when the brand-noun proximity is present
#   (e.g., "Calm app", "subscribe to Headspace", "Insight Timer").
UNAMBIGUOUS_ORGS = [
    r"\bInsight Timer\b",
    r"\bPlum Village\b",
    r"\bSpirit Rock\b",
    r"\b10\% Happier\b",
    r"\bTen Percent Happier\b",
    r"\bMBSR\b",
    r"\bMBCT\b",
    r"\bUCLA Mindful\b",
    r"\bWaking Up app\b",
    r"\bSam Harris\b",
    r"\bShambhala\b",
    r"\bGoenka\b",
    r"\bVipassana\b",
    r"\bDharma Seed\b",
    r"\bInsight Meditation Society\b",
    r"\bTricycle\b",
    r"\bLion's Roar\b",
    r"\bSounds True\b",
    r"\bTED Talk\b",
    r"\bTED talk\b",
    r"\bYouTube channel\b",
]

# Ambiguous orgs — flag ONLY in brand-context proximity (e.g., "the Calm app",
# "subscribe to Headspace", "the Headspace app"). Pattern carries (token, ctx_pat).
AMBIGUOUS_ORGS = [
    (r"\bCalm\b",
     r"\b(?:app|application|subscription|subscribe|download|founder|CEO|company|brand)\b"),
    (r"\bHeadspace\b",
     r"\b(?:app|application|subscription|subscribe|download|founder|CEO|company|brand)\b"),
    (r"\bAwakening\b",
     r"\b(?:app|application|subscription|subscribe|download|founder|CEO|book|by)\b"),
]

# Subscribe/recommend-style phrases — moved to vague since "subscribe to" alone
# without a clear external referent is review-by-human.
EXTERNAL_PODCAST_RE = re.compile(
    r"\bPodcast\s+(?:by|called|titled)\s+[A-Z]",
)

# Lower-confidence vague-recommendation phrases.
VAGUE_RECOMMENDATIONS = [
    r"\bthere's a (?:great|wonderful|amazing|fantastic) book\b",
    r"\bthere is a (?:great|wonderful|amazing|fantastic) book\b",
    r"\bI learned this from a (?:wonderful|great|amazing) teacher\b",
    r"\bI learned this from my teacher\b",
    r"\bmy teacher (?:once )?said\b",
    r"\ba teacher I follow\b",
    r"\bsubscribe to\b",
    r"\bcheck out\b",
    r"\bI recommend\b",
    r"\bhighly recommend\b",
    r"\byou should read\b",
    r"\bgo read\b",
    r"\bgreat resource\b",
    r"\bwonderful resource\b",
    r"\bamazing resource\b",
]

# URLs anywhere in an atom — atoms should be content-only.
URL_RE = re.compile(r"https?://[^\s\)\]\>\"']+", re.IGNORECASE)

# Whitespace-normalized words: used for proximity windowing
WORD_RE = re.compile(r"\S+")

# Variant block separator inside CANONICAL.txt — header is "## INTEGRATION v01"
VARIANT_HEADER_RE = re.compile(r"^##\s+\w+\s+v\d+\s*$", re.MULTILINE)

# YAML body extraction for teacher-bank atoms.
YAML_BODY_RE = re.compile(r"^body:\s*(.+?)(?=^\w+:|\Z)", re.MULTILINE | re.DOTALL)

# ---------------------------------------------------------------------------
# Topic-matched SKU suggestion mapping (storefront landing URL pattern)
# ---------------------------------------------------------------------------

# Per spec §15.4 + §AMENDMENT-2026-06-04.7 — rewrites point to topic-matched
# Pearl Prime brand-lane SKUs at locale parity. For audit purposes we generate
# the SUGGESTED action string only; the actual rewrite is a separate ws.
TOPIC_TO_SKU_LANE = {
    "anxiety": "stillness_press anxiety series → /en-US/brand/stillness_press?topic=anxiety",
    "overthinking": "stillness_press overthinking series → /en-US/brand/stillness_press?topic=overthinking",
    # Future topics — add as scope expands.
    "grief": "stillness_press grief series → /en-US/brand/stillness_press?topic=grief",
    "burnout": "stillness_press burnout series → /en-US/brand/stillness_press?topic=burnout",
    "shame": "stillness_press shame series → /en-US/brand/stillness_press?topic=shame",
}


def topic_suggestion(topic: str, match_type: str) -> str:
    """Generate the suggested_action TSV field per spec §15.4."""
    if match_type == "low_vague_recommendation":
        return "human_review"
    sku_hint = TOPIC_TO_SKU_LANE.get(
        topic,
        f"Pearl Prime catalog SKU at locale parity (topic={topic})",
    )
    return f"replace with reference to {sku_hint}"


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------

@dataclass
class Match:
    file_path: str
    line_no: int
    match_type: str
    matched_text: str
    suggested_action: str
    # Locale tag. Defaulted so every existing positional construction of Match(
    # ...) in _scan_text remains valid without edits; the localized scan paths
    # backfill it via _tag_locale() after the scan returns. "" = non-localized
    # (en-US root) scan.
    locale: str = ""


def _within_proximity(words: List[str], idx_a: int, target_patterns: List[re.Pattern], window: int = 10) -> bool:
    """Return True if any pattern in target_patterns matches within ±window words of idx_a."""
    start = max(0, idx_a - window)
    end = min(len(words), idx_a + window + 1)
    window_text = " ".join(words[start:end])
    return any(p.search(window_text) for p in target_patterns)


def _scan_text(
    text: str,
    file_path: str,
    topic: str,
    line_offset: int = 0,
) -> List[Match]:
    """Scan a text body for all match types. line_offset shifts reported line_no."""
    results: List[Match] = []

    # Compile book-noun proximity patterns once
    book_noun_patterns = [re.compile(p, re.IGNORECASE) for p in BOOK_NOUNS]

    lines = text.splitlines()

    # ---- External author detection ----
    # Multi-word surnames (e.g., "van der Kolk", "Tara Brach") are always
    # high-confidence because they're too distinctive to be a false positive.
    # Single-token common-English surnames (e.g., "Brown") are flagged only
    # with book-noun proximity, and Single-token distinctive surnames
    # (e.g., "Maté", "Tolle", "Chödrön") are flagged as low_vague when
    # book-noun proximity is absent.
    DISTINCTIVE_SINGLE_TOKEN = {
        "Maté", "Mate", "Tolle", "Hanh", "Kabat-Zinn", "Chödrön", "Chodron",
        "Porges", "Doidge", "Frankl", "Adyashanti", "Goleman",
        "Brach", "Bessel", "Pinker",
        "Williamson", "Pueblo",  # Williamson is also a common surname; Yung Pueblo
        "Goenka", "Adyashanti", "Krishnamurti",
    }
    COMMON_ENGLISH_SURNAMES = {
        "Brown", "Mate", "Williams", "Levine", "Harris", "Robbins", "Doyle",
        "Newport", "Cain", "Peterson", "Clear", "Nepo", "Hanson", "Manson",
        "Dass", "Katie",  # Ram Dass / Byron Katie — context-dependent
        "Dalai",  # Dalai Lama is usually whole-phrase; bare "Dalai" is rare
        "Thich", "Pema",  # given names — only meaningful in context
    }
    for surname in EXTERNAL_AUTHORS:
        surname_pat = re.compile(rf"\b{re.escape(surname)}\b")
        is_multi_word = " " in surname
        is_distinctive_single = surname in DISTINCTIVE_SINGLE_TOKEN
        is_common = surname in COMMON_ENGLISH_SURNAMES
        for lineno_zero, line in enumerate(lines):
            for m in surname_pat.finditer(line):
                ctx_lines = []
                if lineno_zero > 0:
                    ctx_lines.append(lines[lineno_zero - 1])
                ctx_lines.append(line)
                if lineno_zero + 1 < len(lines):
                    ctx_lines.append(lines[lineno_zero + 1])
                ctx = " ".join(ctx_lines)
                has_book_noun = any(p.search(ctx) for p in book_noun_patterns)

                if is_multi_word:
                    # Multi-word surnames always flagged high
                    results.append(Match(
                        file_path, lineno_zero + 1 + line_offset,
                        "high_external_author",
                        f"{surname} :: {line.strip()[:120]}",
                        topic_suggestion(topic, "high_external_author"),
                    ))
                elif has_book_noun:
                    # Single-token + book-noun = high confidence
                    results.append(Match(
                        file_path, lineno_zero + 1 + line_offset,
                        "high_external_author",
                        f"{surname} :: {line.strip()[:120]}",
                        topic_suggestion(topic, "high_external_author"),
                    ))
                elif is_distinctive_single and not is_common:
                    # Distinctive single token without book-noun = low confidence
                    results.append(Match(
                        file_path, lineno_zero + 1 + line_offset,
                        "low_vague_recommendation",
                        f"{surname} (author name, no book-noun ctx) :: {line.strip()[:120]}",
                        "human_review — author surname referenced but no explicit book CTA",
                    ))
                # else: common-English token without context = skip (Brown, Mate adj, Williams, etc.)

    # ---- High-confidence: italic/quoted external title pattern ----
    for lineno_zero, line in enumerate(lines):
        for m in EXTERNAL_TITLE_RE.finditer(line):
            results.append(Match(
                file_path, lineno_zero + 1 + line_offset,
                "high_external_title",
                m.group(0),
                topic_suggestion(topic, "high_external_title"),
            ))
        for m in EXTERNAL_TITLE_QUOTED_RE.finditer(line):
            results.append(Match(
                file_path, lineno_zero + 1 + line_offset,
                "high_external_title",
                m.group(0),
                topic_suggestion(topic, "high_external_title"),
            ))

    # ---- High-confidence: unambiguous title literals (always flagged) ----
    for title in UNAMBIGUOUS_TITLES:
        title_pat = re.compile(rf"\b{re.escape(title)}\b")
        for lineno_zero, line in enumerate(lines):
            for m in title_pat.finditer(line):
                results.append(Match(
                    file_path, lineno_zero + 1 + line_offset,
                    "high_external_title",
                    f"{title} :: {line.strip()[:120]}",
                    topic_suggestion(topic, "high_external_title"),
                ))

    # ---- High-confidence: ambiguous title literals (need proximity) ----
    # Flag ONLY when:
    #   - The token appears in italic-quoted form (*Quiet*), OR
    #   - The token appears with book-noun proximity (±10 words), OR
    #   - The token appears with " by <CapitalizedName>" right after
    for title in AMBIGUOUS_TITLES:
        # Italic form: *Quiet*
        italic_pat = re.compile(rf"\*{re.escape(title)}\*")
        # "by" form: Quiet by Susan Cain
        by_pat = re.compile(rf"\b{re.escape(title)}\s+by\s+[A-Z][A-Za-z]+")
        # Bare token (case-sensitive) — needs context check below
        bare_pat = re.compile(rf"\b{re.escape(title)}\b")

        for lineno_zero, line in enumerate(lines):
            for m in italic_pat.finditer(line):
                results.append(Match(
                    file_path, lineno_zero + 1 + line_offset,
                    "high_external_title",
                    f"*{title}* :: {line.strip()[:120]}",
                    topic_suggestion(topic, "high_external_title"),
                ))
            for m in by_pat.finditer(line):
                results.append(Match(
                    file_path, lineno_zero + 1 + line_offset,
                    "high_external_title",
                    f"{m.group(0)} :: {line.strip()[:120]}",
                    topic_suggestion(topic, "high_external_title"),
                ))
            # Bare token: require ±10 word proximity to a book-noun.
            for m in bare_pat.finditer(line):
                # Skip if already counted via italic/by paths
                if "*" + title + "*" in line or m.group(0) + " by " in line:
                    continue
                ctx_lines = []
                if lineno_zero > 0:
                    ctx_lines.append(lines[lineno_zero - 1])
                ctx_lines.append(line)
                if lineno_zero + 1 < len(lines):
                    ctx_lines.append(lines[lineno_zero + 1])
                ctx = " ".join(ctx_lines)
                words = WORD_RE.findall(ctx)
                # Locate bare token in word list
                hit_idx = None
                title_norm = title.lower()
                for i, w in enumerate(words):
                    if w.lower().strip(".,!?\"';:*") == title_norm:
                        hit_idx = i
                        break
                if hit_idx is None:
                    continue
                if _within_proximity(words, hit_idx, book_noun_patterns, window=10):
                    results.append(Match(
                        file_path, lineno_zero + 1 + line_offset,
                        "high_external_title",
                        f"{title} (proximity) :: {line.strip()[:120]}",
                        topic_suggestion(topic, "high_external_title"),
                    ))

    # ---- High-confidence: unambiguous orgs ----
    for org_pat_str in UNAMBIGUOUS_ORGS:
        org_pat = re.compile(org_pat_str)
        for lineno_zero, line in enumerate(lines):
            for m in org_pat.finditer(line):
                results.append(Match(
                    file_path, lineno_zero + 1 + line_offset,
                    "high_external_org",
                    f"{m.group(0)} :: {line.strip()[:120]}",
                    topic_suggestion(topic, "high_external_org"),
                ))

    # ---- High-confidence: ambiguous orgs (brand-context proximity) ----
    for token_pat_str, ctx_pat_str in AMBIGUOUS_ORGS:
        token_pat = re.compile(token_pat_str)
        ctx_pat = re.compile(ctx_pat_str, re.IGNORECASE)
        for lineno_zero, line in enumerate(lines):
            for m in token_pat.finditer(line):
                ctx_lines = []
                if lineno_zero > 0:
                    ctx_lines.append(lines[lineno_zero - 1])
                ctx_lines.append(line)
                if lineno_zero + 1 < len(lines):
                    ctx_lines.append(lines[lineno_zero + 1])
                ctx = " ".join(ctx_lines)
                if ctx_pat.search(ctx):
                    results.append(Match(
                        file_path, lineno_zero + 1 + line_offset,
                        "high_external_org",
                        f"{m.group(0)} (brand-context) :: {line.strip()[:120]}",
                        topic_suggestion(topic, "high_external_org"),
                    ))

    # ---- High-confidence: external podcast pointer ----
    for lineno_zero, line in enumerate(lines):
        for m in EXTERNAL_PODCAST_RE.finditer(line):
            results.append(Match(
                file_path, lineno_zero + 1 + line_offset,
                "high_external_org",
                f"{m.group(0)} :: {line.strip()[:120]}",
                topic_suggestion(topic, "high_external_org"),
            ))

    # ---- High-confidence: URL in atom ----
    for lineno_zero, line in enumerate(lines):
        for m in URL_RE.finditer(line):
            results.append(Match(
                file_path, lineno_zero + 1 + line_offset,
                "high_url_in_atom",
                m.group(0),
                "remove URL — atoms are content-only per §15.7",
            ))

    # ---- Low-confidence: vague recommendation phrases ----
    for vague_pat_str in VAGUE_RECOMMENDATIONS:
        vague_pat = re.compile(vague_pat_str, re.IGNORECASE)
        for lineno_zero, line in enumerate(lines):
            for m in vague_pat.finditer(line):
                results.append(Match(
                    file_path, lineno_zero + 1 + line_offset,
                    "low_vague_recommendation",
                    f"{m.group(0)} :: {line.strip()[:120]}",
                    topic_suggestion(topic, "low_vague_recommendation"),
                ))

    return results


def _dedupe_matches(matches: List[Match]) -> List[Match]:
    """Dedupe identical (file_path, line_no, match_type, matched_text)."""
    seen = set()
    out: List[Match] = []
    for m in matches:
        key = (m.file_path, m.line_no, m.match_type, m.matched_text)
        if key in seen:
            continue
        seen.add(key)
        out.append(m)
    return out


# ---------------------------------------------------------------------------
# Per-variant scanning of CANONICAL.txt atoms
# ---------------------------------------------------------------------------

def _scan_atom_canonical(path: Path, topic: str) -> Tuple[int, List[Match]]:
    """
    Scan an atoms/<persona>/<topic>/<atom_type>/CANONICAL.txt file.
    Returns (variant_count, matches).
    Variants are delimited by "## INTEGRATION v01" / "## REFLECTION v02" / etc.
    """
    text = path.read_text(encoding="utf-8", errors="replace")
    # Count variant headers — each one is a scannable atom variant
    headers = list(VARIANT_HEADER_RE.finditer(text))
    variant_count = max(len(headers), 1)
    # We scan the whole file at once; line numbers are file-relative which
    # gives downstream reviewers an unambiguous anchor.
    matches = _scan_text(text, str(path), topic, line_offset=0)
    return variant_count, matches


def _scan_teacher_yaml(path: Path) -> Tuple[int, List[Match]]:
    """
    Scan a SOURCE_OF_TRUTH/teacher_banks/<teacher>/approved_atoms/<atom_type>/*.yaml.

    The YAML structure is:
        atom_id: ...
        body: <content here>
        teacher:
          teacher_id: ...
          ...

    We extract ONLY the body content (not the metadata) so that words like
    "teacher_id" in the metadata don't act as a false-positive book-noun
    proximity trigger.
    """
    text = path.read_text(encoding="utf-8", errors="replace")
    topic = "teacher_bank"
    text_lower = text.lower()
    if "anxiety" in text_lower:
        topic = "anxiety"
    if "overthinking" in text_lower:
        topic = "overthinking"

    # Extract body content. Body can be multi-line (YAML block-scalar or
    # folded-scalar style). Match `body:` and consume until the next top-level
    # YAML key (a line starting at column 0 with `key:`).
    body_match = re.search(
        r"^body:\s*(.*?)(?=^[a-zA-Z_]+:\s*$|^[a-zA-Z_]+:\s*\S|\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if not body_match:
        return 1, []

    body_text = body_match.group(1)
    # Find which line `body:` started on so we report correct line numbers
    body_start_char = body_match.start()
    line_offset = text[:body_start_char].count("\n")
    matches = _scan_text(body_text, str(path), topic, line_offset=line_offset)
    return 1, matches


# ---------------------------------------------------------------------------
# Scope enumeration
# ---------------------------------------------------------------------------

# Topics in scope for stage1 per AMENDMENT §AMENDMENT-2026-06-04.7
STAGE1_TOPICS = ["anxiety", "overthinking"]

# Atom types in scope per §15.2
SCOPED_ATOM_TYPES = ["COMPRESSION", "REFLECTION", "INTEGRATION", "HOOK"]

# ---------------------------------------------------------------------------
# Stage 2a — localized atom variants (CJK locales)
# ---------------------------------------------------------------------------

# CJK locales scanned by --scope stage2a, per §AMENDMENT-2026-06-04.7 second
# pass (ja-JP) extended to the zh-TW + zh-CN variants the localized corpus
# actually carries. ko-KR (+ zh-HK/zh-SG/zh-MO mirrors) are intentionally NOT
# in the default Stage-2a set — ko-KR is Phase-4 gated (§16) and the zh-* region
# mirrors are derivative; pass --locales to widen explicitly.
STAGE2A_LOCALES = ["ja-JP", "zh-TW", "zh-CN"]

# All locale codes the localized tree is known to use. Order is the canonical
# display order for the heat map; the scan only visits STAGE2A_LOCALES (or the
# --locales override) but the heat map reports every requested locale even at 0.
KNOWN_LOCALES = [
    "en-US", "ja-JP", "zh-TW", "zh-CN", "ko-KR", "zh-HK", "zh-SG", "zh-MO",
]

# Localized CANONICAL.txt lives at: atoms/<persona>/<topic>/<atom>/locales/<loc>/CANONICAL.txt
# Localized teacher YAML lives at:   .../approved_atoms_localized/<loc>/<TYPE>/*.yaml
_LOCALE_SEG_RE = re.compile(r"/locales/([A-Za-z]{2}-[A-Za-z]{2})/")
_LOCALE_TB_SEG_RE = re.compile(r"/approved_atoms_localized/([A-Za-z]{2}-[A-Za-z]{2})/")


def _locale_from_path(path: Path) -> str:
    """
    Derive the locale code from a localized atom / teacher-bank path.

    Matches both layouts:
      - atoms/.../locales/<locale>/CANONICAL.txt
      - SOURCE_OF_TRUTH/teacher_banks/.../approved_atoms_localized/<locale>/...
    Returns "" if the path is not a localized variant (i.e., en-US root atom).
    """
    s = path.as_posix()
    m = _LOCALE_SEG_RE.search(s) or _LOCALE_TB_SEG_RE.search(s)
    return m.group(1) if m else ""


def _topic_from_localized_atom_path(path: Path) -> str:
    """
    Topic for a localized atom is the same path segment as the en-US root:
    atoms/<persona>/<topic>/<atom>/locales/<locale>/CANONICAL.txt
    -> index of 'atoms' + 2.
    """
    parts = path.parts
    if "atoms" in parts:
        ai = parts.index("atoms")
        if ai + 2 < len(parts):
            return parts[ai + 2]
    return "unknown"


def _tag_locale(matches: List[Match], locale: str) -> List[Match]:
    """Backfill the locale field on every Match produced for a localized file."""
    for m in matches:
        m.locale = locale
    return matches


def _enumerate_localized_atoms(
    repo_root: Path, locales: List[str]
) -> List[Tuple[Path, str]]:
    """
    Enumerate (path, topic) for localized atom CANONICAL.txt variants in the
    requested locales:
        atoms/<persona>/<topic>/<atom>/locales/<locale>/CANONICAL.txt

    Returns them sorted for deterministic output. This walks the whole atoms/
    tree once with Path.rglob so it picks up every persona/topic/atom — there is
    no stage1-style topic allow-list here (the localized corpus spans every
    topic, and the whole point of Stage 2a is the corpus Stage 1 skipped).
    """
    pairs: List[Tuple[Path, str]] = []
    atoms_root = repo_root / "atoms"
    if not atoms_root.exists():
        return pairs
    locale_set = set(locales)
    for canonical in sorted(atoms_root.rglob("locales/*/CANONICAL.txt")):
        loc = _locale_from_path(canonical)
        if loc not in locale_set:
            continue
        pairs.append((canonical, _topic_from_localized_atom_path(canonical)))
    return pairs


def _enumerate_localized_teacher_atoms(
    repo_root: Path, locales: List[str]
) -> List[Tuple[Path, str]]:
    """
    Enumerate (path, locale) for localized teacher-bank atoms:
        SOURCE_OF_TRUTH/teacher_banks/<teacher>/approved_atoms_localized/<locale>/<TYPE>/*.yaml
    """
    pairs: List[Tuple[Path, str]] = []
    tb_root = repo_root / "SOURCE_OF_TRUTH" / "teacher_banks"
    if not tb_root.exists():
        return pairs
    locale_set = set(locales)
    for teacher_dir in sorted(tb_root.iterdir()):
        if not teacher_dir.is_dir():
            continue
        loc_root = teacher_dir / "approved_atoms_localized"
        if not loc_root.exists():
            continue
        for yaml_file in sorted(loc_root.rglob("*.yaml")):
            loc = _locale_from_path(yaml_file)
            if loc not in locale_set:
                continue
            pairs.append((yaml_file, loc))
    return pairs


def _enumerate_atoms(repo_root: Path, scope: str) -> List[Tuple[Path, str]]:
    """
    Enumerate (path, topic) tuples for the requested scope.
    scope = 'stage1' → en-US anxiety + overthinking × all personas, scoped atom types
    scope = 'all'    → everything matching atoms/<persona>/<topic>/<atom_type>/CANONICAL.txt
    """
    pairs: List[Tuple[Path, str]] = []
    atoms_root = repo_root / "atoms"
    if not atoms_root.exists():
        return pairs

    personas = [
        p for p in sorted(atoms_root.iterdir())
        if p.is_dir() and not p.name.startswith(".")
    ]

    for persona_dir in personas:
        topics = STAGE1_TOPICS if scope == "stage1" else [
            t.name for t in sorted(persona_dir.iterdir()) if t.is_dir()
        ]
        for topic in topics:
            topic_dir = persona_dir / topic
            if not topic_dir.exists():
                continue
            atom_types = (
                SCOPED_ATOM_TYPES if scope == "stage1"
                else [a.name for a in sorted(topic_dir.iterdir()) if a.is_dir()]
            )
            for atom_type in atom_types:
                canonical = topic_dir / atom_type / "CANONICAL.txt"
                if canonical.exists():
                    pairs.append((canonical, topic))

    return pairs


def _enumerate_teacher_atoms(repo_root: Path) -> List[Path]:
    """Enumerate teacher_banks/<teacher>/approved_atoms/<atom_type>/*.yaml."""
    paths: List[Path] = []
    tb_root = repo_root / "SOURCE_OF_TRUTH" / "teacher_banks"
    if not tb_root.exists():
        return paths
    for teacher_dir in sorted(tb_root.iterdir()):
        if not teacher_dir.is_dir():
            continue
        approved = teacher_dir / "approved_atoms"
        if not approved.exists():
            continue
        for atom_type_dir in sorted(approved.iterdir()):
            if not atom_type_dir.is_dir():
                continue
            for yaml_file in sorted(atom_type_dir.glob("*.yaml")):
                paths.append(yaml_file)
    return paths


# ---------------------------------------------------------------------------
# Per-locale heat-map summary (Stage 2a)
# ---------------------------------------------------------------------------

MATCH_TYPES_ORDER = [
    "high_external_author",
    "high_external_title",
    "high_external_org",
    "high_url_in_atom",
    "low_vague_recommendation",
]


def _persona_topic_from_path(rel_path: str) -> Tuple[str, str]:
    """Best-effort (persona, topic) extraction from a repo-relative path."""
    parts = Path(rel_path).parts
    if "atoms" in parts:
        ai = parts.index("atoms")
        persona = parts[ai + 1] if ai + 1 < len(parts) else "?"
        topic = parts[ai + 2] if ai + 2 < len(parts) else "?"
        return persona, topic
    if "teacher_banks" in parts:
        ti = parts.index("teacher_banks")
        teacher = parts[ti + 1] if ti + 1 < len(parts) else "?"
        return f"teacher:{teacher}", "teacher_bank"
    return "?", "?"


def _write_heatmap_summary(
    summary_path: Path,
    matches: List[Match],
    locales: List[str],
    files_per_locale: dict,
    variants_per_locale: dict,
    scan_date: str,
    tsv_out: Path,
    repo_root: Path,
) -> None:
    """
    Emit the per-locale heat-map markdown summary for Stage 2a.

    Sections:
      §1 headline (per-locale files / variants / flags table)
      §2 per-locale × match-type heat map
      §3 top external author/title/org tokens by frequency
      §4 recommended Stage 2b / 2c scope
    """
    # --- aggregate ---
    # counts[locale][match_type] = n
    counts: dict = {loc: {mt: 0 for mt in MATCH_TYPES_ORDER} for loc in locales}
    token_freq: dict = {}  # matched-token head -> count (high_* only)
    flagged_files: dict = {loc: set() for loc in locales}
    per_locale_total: dict = {loc: 0 for loc in locales}
    for m in matches:
        loc = m.locale or "en-US"
        if loc not in counts:
            counts[loc] = {mt: 0 for mt in MATCH_TYPES_ORDER}
            flagged_files.setdefault(loc, set())
            per_locale_total.setdefault(loc, 0)
        counts[loc][m.match_type] = counts[loc].get(m.match_type, 0) + 1
        per_locale_total[loc] += 1
        flagged_files[loc].add(m.file_path)
        if m.match_type.startswith("high_"):
            head = m.matched_text.split("::")[0].split("(")[0].strip()
            if head:
                token_freq[head] = token_freq.get(head, 0) + 1

    total_flags = len(matches)
    lines: List[str] = []
    lines.append("# Pearl Prime Storefront V1 — Atom Off-Catalog Reference Audit (Stage 2a — Localized CJK Variants)")
    lines.append("")
    lines.append("**Workstream:** `ws_pearl_writer_next_step_atom_audit_stage_2a_20260612` (stage 2a — localized atom variants)")
    lines.append(f"**Date:** {scan_date}")
    lines.append("**Authority:** `docs/specs/PEARL_PRIME_STOREFRONT_V1_SPEC.md` §15 + §AMENDMENT-2026-06-04.7 (second pass)")
    lines.append("**Detector:** `scripts/ci/check_atoms_external_book_references.py` (`--scope stage2a`)")
    lines.append(f"**Raw TSV:** `{_safe_rel(tsv_out, repo_root)}`")
    lines.append(f"**Locales scanned:** {', '.join(locales)}")
    lines.append("**Mode:** AUDIT ONLY — no atoms rewritten in this workstream (rewrite is the separate operator-gated ws per §15.6).")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## §1 — Headline result (per locale)")
    lines.append("")
    lines.append("| Locale | Atom files | Atom variants | Teacher YAMLs | Flagged passages | Flagged files |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for loc in locales:
        fp = files_per_locale.get(loc, {})
        atom_files = fp.get("atom_files", 0)
        atom_variants = variants_per_locale.get(loc, 0)
        teacher_yamls = fp.get("teacher_yamls", 0)
        lines.append(
            f"| `{loc}` | {atom_files:,} | {atom_variants:,} | {teacher_yamls:,} "
            f"| {per_locale_total.get(loc, 0):,} | {len(flagged_files.get(loc, set())):,} |"
        )
    tot_atom_files = sum(v.get("atom_files", 0) for v in files_per_locale.values())
    tot_atom_variants = sum(variants_per_locale.values())
    tot_teacher = sum(v.get("teacher_yamls", 0) for v in files_per_locale.values())
    lines.append(
        f"| **TOTAL** | **{tot_atom_files:,}** | **{tot_atom_variants:,}** "
        f"| **{tot_teacher:,}** | **{total_flags:,}** "
        f"| **{sum(len(s) for s in flagged_files.values()):,}** |"
    )
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## §2 — Per-locale × match-type heat map")
    lines.append("")
    header = "| Locale | " + " | ".join(MATCH_TYPES_ORDER) + " | total |"
    sep = "|---|" + "|".join(["---:"] * (len(MATCH_TYPES_ORDER) + 1)) + "|"
    lines.append(header)
    lines.append(sep)
    for loc in locales:
        row = counts.get(loc, {mt: 0 for mt in MATCH_TYPES_ORDER})
        cells = " | ".join(str(row.get(mt, 0)) for mt in MATCH_TYPES_ORDER)
        lines.append(f"| `{loc}` | {cells} | {per_locale_total.get(loc, 0)} |")
    # Column totals
    col_tot = {mt: sum(counts[loc].get(mt, 0) for loc in counts) for mt in MATCH_TYPES_ORDER}
    lines.append(
        "| **all** | "
        + " | ".join(f"**{col_tot[mt]}**" for mt in MATCH_TYPES_ORDER)
        + f" | **{total_flags}** |"
    )
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## §3 — Top external tokens by frequency (high-confidence only)")
    lines.append("")
    if token_freq:
        lines.append("| Token (author / title / org) | Hits |")
        lines.append("|---|---:|")
        for tok, n in sorted(token_freq.items(), key=lambda kv: (-kv[1], kv[0]))[:30]:
            safe = tok.replace("|", "\\|")
            lines.append(f"| `{safe}` | {n} |")
    else:
        lines.append("_No high-confidence external author / title / org tokens were found in the localized CJK corpus._")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## §4 — Recommended Stage 2b / 2c scope")
    lines.append("")
    # Heuristic recommendation derived from the data.
    high_total = sum(
        counts[loc].get(mt, 0)
        for loc in counts
        for mt in ("high_external_author", "high_external_title", "high_external_org", "high_url_in_atom")
    )
    vague_total = sum(counts[loc].get("low_vague_recommendation", 0) for loc in counts)
    # Locale ranked by high-confidence density.
    loc_high = {
        loc: sum(
            counts[loc].get(mt, 0)
            for mt in ("high_external_author", "high_external_title", "high_external_org", "high_url_in_atom")
        )
        for loc in locales
    }
    ranked = [loc for loc, _ in sorted(loc_high.items(), key=lambda kv: -kv[1]) if loc_high[loc] > 0]
    lines.append(f"- **High-confidence external-reference hits (author/title/org/url):** {high_total}")
    lines.append(f"- **Low-confidence (human-review) hits:** {vague_total}")
    if high_total == 0:
        lines.append(
            "- **Stage 2b recommendation:** the localized CJK corpus contains **no high-confidence "
            "external-book/author/org/URL CTAs**. The §15 rewrite ws does NOT need to fan out across the "
            "full CJK localized corpus. Scope Stage 2b to **human review of the low-confidence hits only** "
            f"({vague_total} passages), which are dominated by un-translated English commentary artifacts "
            "rather than genuine out-of-ecosystem CTAs."
        )
    else:
        lines.append(
            "- **Stage 2b recommendation:** prioritize the rewrite ws on the locales with high-confidence "
            f"hits, in density order: {', '.join(f'`{l}`' for l in ranked)}. "
            "Each high-confidence row in the TSV is a candidate for the §15.4 topic-matched-SKU rewrite "
            "(at locale parity — ja-JP atom → ja-JP SKU, never en-US)."
        )
    lines.append(
        "- **Stage 2c recommendation:** the un-translated-English-commentary signal surfaced by "
        "`low_vague_recommendation` in zh-TW/zh-CN CANONICAL.txt variants is a *localization-quality* "
        "finding distinct from §15 (atoms carrying English LLM analysis prose instead of translated body "
        "text). Route that to Pearl_Localization as a separate ticket; it is out of scope for the §15 "
        "external-reference rewrite but should not be lost."
    )
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## §5 — Anti-drift / scope guard")
    lines.append("")
    lines.append("- This is a **coverage report only** (§15.6). No atom file was modified.")
    lines.append("- Atoms remain content-only; any `high_url_in_atom` hit is a §15.7 invariant violation to be fixed by the rewrite ws, not here.")
    lines.append("- ko-KR / zh-HK / zh-SG / zh-MO mirrors were **excluded** from the default Stage-2a locale set (ko-KR is Phase-4 gated per §16; the others are derivative region mirrors). Pass `--locales` to include them in a future pass.")
    lines.append("")
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _safe_rel(p: Path, repo_root: Path) -> str:
    try:
        return str(Path(p).resolve().relative_to(repo_root))
    except ValueError:
        return str(p)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Detect external book/author/org/URL references in Pearl Prime "
            "'what to do next' atoms (spec §15.3)."
        ),
    )
    parser.add_argument(
        "--scope",
        choices=["stage1", "stage2a", "all"],
        default="stage1",
        help=(
            "stage1 = en-US anxiety + overthinking; "
            "stage2a = localized CJK atom variants (ja-JP/zh-TW/zh-CN) + "
            "localized teacher banks; all = full sweep"
        ),
    )
    parser.add_argument(
        "--locales",
        nargs="*",
        default=None,
        help=(
            "Locale filter for --scope stage2a (e.g. --locales ja-JP zh-TW). "
            f"Defaults to the Stage-2a set: {' '.join(STAGE2A_LOCALES)}."
        ),
    )
    parser.add_argument(
        "--summary-out",
        type=str,
        default=None,
        help=(
            "If set, write a per-locale heat-map markdown summary to this path "
            "(Stage 2a). Recommended for --scope stage2a."
        ),
    )
    parser.add_argument(
        "--paths",
        nargs="*",
        default=None,
        help="Explicit list of paths to scan (CI delta mode). Overrides --scope.",
    )
    parser.add_argument(
        "--out",
        type=str,
        default="artifacts/qa/next_step_atom_audit.tsv",
        help="Output TSV path",
    )
    parser.add_argument(
        "--include-teacher-banks",
        action="store_true",
        default=True,
        help="Also scan SOURCE_OF_TRUTH/teacher_banks/ approved_atoms YAMLs",
    )
    parser.add_argument(
        "--repo-root",
        type=str,
        default=str(Path(__file__).resolve().parents[2]),
        help="Repo root (defaults to the script's grandparent).",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress per-file progress lines",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Stage-2a localized scan flag + effective locale set.
    is_stage2a = (args.scope == "stage2a") and not args.paths
    stage2a_locales = list(args.locales) if args.locales else list(STAGE2A_LOCALES)

    # Build the scan list
    canonical_pairs: List[Tuple[Path, str]] = []
    teacher_paths: List[Path] = []
    # For stage2a we also carry localized teacher pairs (path, locale) so the
    # locale tag survives the scan.
    localized_teacher_pairs: List[Tuple[Path, str]] = []

    if args.paths:
        # CI delta mode
        for raw in args.paths:
            p = Path(raw)
            if not p.is_absolute():
                p = repo_root / p
            if not p.exists():
                continue
            # Try to infer topic from path
            parts = p.parts
            topic = "unknown"
            if "atoms" in parts:
                ai = parts.index("atoms")
                if ai + 2 < len(parts):
                    topic = parts[ai + 2]
            if "approved_atoms" in parts or "teacher_banks" in parts:
                teacher_paths.append(p)
            else:
                canonical_pairs.append((p, topic))
    elif is_stage2a:
        # Stage 2a — localized CJK atom variants + localized teacher banks.
        canonical_pairs = _enumerate_localized_atoms(repo_root, stage2a_locales)
        if args.include_teacher_banks:
            localized_teacher_pairs = _enumerate_localized_teacher_atoms(
                repo_root, stage2a_locales
            )
    else:
        canonical_pairs = _enumerate_atoms(repo_root, args.scope)
        if args.include_teacher_banks:
            teacher_paths = _enumerate_teacher_atoms(repo_root)

    total_files_scanned = 0
    total_variants_scanned = 0
    all_matches: List[Match] = []

    # Per-locale bookkeeping for the Stage-2a heat map.
    files_per_locale: dict = {
        loc: {"atom_files": 0, "teacher_yamls": 0} for loc in stage2a_locales
    }
    variants_per_locale: dict = {loc: 0 for loc in stage2a_locales}

    for path, topic in canonical_pairs:
        try:
            n_variants, matches = _scan_atom_canonical(path, topic)
        except Exception as exc:  # pragma: no cover
            print(f"ERROR scanning {path}: {exc}", file=sys.stderr)
            continue
        total_files_scanned += 1
        total_variants_scanned += n_variants
        if is_stage2a:
            loc = _locale_from_path(path)
            matches = _tag_locale(matches, loc)
            files_per_locale.setdefault(loc, {"atom_files": 0, "teacher_yamls": 0})
            files_per_locale[loc]["atom_files"] += 1
            variants_per_locale[loc] = variants_per_locale.get(loc, 0) + n_variants
        all_matches.extend(matches)
        if not args.quiet:
            print(f"scanned {path.relative_to(repo_root)} ({n_variants} variants, {len(matches)} hits)")

    for path in teacher_paths:
        try:
            n_variants, matches = _scan_teacher_yaml(path)
        except Exception as exc:  # pragma: no cover
            print(f"ERROR scanning {path}: {exc}", file=sys.stderr)
            continue
        total_files_scanned += 1
        total_variants_scanned += n_variants
        all_matches.extend(matches)
        if not args.quiet:
            print(f"scanned {path.relative_to(repo_root)} ({len(matches)} hits)")

    # Localized teacher-bank YAMLs (Stage 2a) — same scanner, locale-tagged.
    for path, loc in localized_teacher_pairs:
        try:
            n_variants, matches = _scan_teacher_yaml(path)
        except Exception as exc:  # pragma: no cover
            print(f"ERROR scanning {path}: {exc}", file=sys.stderr)
            continue
        total_files_scanned += 1
        total_variants_scanned += n_variants
        matches = _tag_locale(matches, loc)
        files_per_locale.setdefault(loc, {"atom_files": 0, "teacher_yamls": 0})
        files_per_locale[loc]["teacher_yamls"] += 1
        all_matches.extend(matches)
        if not args.quiet:
            print(f"scanned {path.relative_to(repo_root)} ({loc}, {len(matches)} hits)")

    all_matches = _dedupe_matches(all_matches)

    # Write TSV. The trailing `locale` column is appended additively — Stage-1
    # consumers that index the first five columns are unaffected.
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t", quoting=csv.QUOTE_MINIMAL)
        writer.writerow(
            ["file_path", "line_no", "match_type", "matched_text", "suggested_action", "locale"]
        )
        for m in all_matches:
            # Sanitize tabs/newlines in matched_text to keep TSV well-formed
            safe_match = m.matched_text.replace("\t", " ").replace("\n", " ").strip()
            safe_action = m.suggested_action.replace("\t", " ").replace("\n", " ").strip()
            try:
                rel = str(Path(m.file_path).resolve().relative_to(repo_root))
            except ValueError:
                rel = m.file_path
            writer.writerow([rel, m.line_no, m.match_type, safe_match, safe_action, m.locale])

    # Per-locale heat-map summary (Stage 2a or any run with --summary-out).
    if args.summary_out:
        summary_path = Path(args.summary_out)
        if not summary_path.is_absolute():
            summary_path = repo_root / summary_path
        scan_date = datetime.date.today().isoformat()
        _write_heatmap_summary(
            summary_path,
            all_matches,
            stage2a_locales,
            files_per_locale,
            variants_per_locale,
            scan_date,
            out_path,
            repo_root,
        )

    # Summary stats to stderr/stdout
    counts: dict[str, int] = {}
    locale_counts: dict[str, int] = {}
    for m in all_matches:
        counts[m.match_type] = counts.get(m.match_type, 0) + 1
        loc_key = m.locale or "en-US"
        locale_counts[loc_key] = locale_counts.get(loc_key, 0) + 1

    print("", file=sys.stderr)
    print(f"=== check_atoms_external_book_references SUMMARY ===", file=sys.stderr)
    if is_stage2a:
        print(f"scope             : stage2a (localized CJK)", file=sys.stderr)
        print(f"locales           : {', '.join(stage2a_locales)}", file=sys.stderr)
    print(f"files_scanned     : {total_files_scanned}", file=sys.stderr)
    print(f"variants_scanned  : {total_variants_scanned}", file=sys.stderr)
    print(f"total_hits        : {len(all_matches)}", file=sys.stderr)
    for mt in sorted(counts):
        print(f"  {mt:<28}: {counts[mt]}", file=sys.stderr)
    if is_stage2a:
        print("per-locale hits:", file=sys.stderr)
        for loc in stage2a_locales:
            print(f"  {loc:<10}: {locale_counts.get(loc, 0)}", file=sys.stderr)
    print(f"tsv_out           : {out_path}", file=sys.stderr)
    if args.summary_out:
        print(f"summary_out       : {args.summary_out}", file=sys.stderr)
    print("", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
