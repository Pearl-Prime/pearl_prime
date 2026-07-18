#!/usr/bin/env python3
"""check_external_buy_links.py — HARD CTA cutover CI guard.

Per `docs/specs/PEARL_PRIME_STOREFRONT_V1_SPEC.md` §14.5 +
§AMENDMENT-2026-06-04.3 §14:

    Phase A launch is gated on **zero** external paid-content CTA matches
    across the seven sweep-surface categories in both en-US and ja-JP.

    External paid-content CTA URL patterns:
        amazon.com/dp        amazon.co.jp/dp     amazon.de/dp
        play.google.com/store/books
        play.google.com/store/audiobooks
        audible.com/pd       audible.co.jp/pd    audible.de/pd
        books.apple.com
        kobo.com/ebook       kobo.com/audiobook
        webtoons.com         webtoon.com         comic.naver.com
        honto.jp             cmoa.jp             bookwalker.jp
        spotify.com/track    spotify.com/album   (only when CTA = "buy", not "listen")
        amzn.to              geni.us             (affiliate shorteners)

This guard is the operational enforcement of the HARD cutover. Any new content
that re-introduces an external paid CTA fails CI and blocks merge.

Allow-list:
    `config/storefront/external_link_allowlist.yaml` (operator-curated)
    permits legitimate non-CTA external links (e.g., brand-bio discovery
    links, documentation source citations, DB schema column-value examples).

Exit codes:
    0 — no violations OR --fail-on-violation absent and violations present
    1 — violations present AND --fail-on-violation set

Output:
    TSV at `artifacts/qa/external_buy_links_violations_<YYYY-MM-DD>.tsv`
    Columns: file_path<TAB>line_no<TAB>matched_url<TAB>suggested_storefront_url

Usage:
    python3 scripts/ci/check_external_buy_links.py --fail-on-violation
    python3 scripts/ci/check_external_buy_links.py --warn-only          # informational
"""

from __future__ import annotations

import argparse
import datetime
import os
import pathlib
import re
import sys
from typing import Iterable

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

# ─────────────────────────────────────────────────────────────────────────────
# Sweep surface categories (§14.2 + §AMENDMENT-2026-06-04.3 §14)
# ─────────────────────────────────────────────────────────────────────────────
SWEEP_SURFACES: list[str] = [
    "funnel/",
    "brand-wizard-app/public/free/",
    "brand-wizard-app/public/free_ja/",  # ja-JP equivalent (may not yet exist)
    "somatic_exercise_freebee_apps/",
    "config/marketing/",
    "docs/marketing/",
    "scripts/marketing/",
    "marketing_deep_research/",
    "config/funnel/email_templates/",
    "config/funnel/line_jp/",
    "pearl_news/articles/",
    "pearl_news/article_templates/",
    "pearl_news/atoms/",
]

# File-extension filter: only scan content-bearing surfaces.
SCAN_EXTENSIONS: set[str] = {
    ".html", ".htm", ".md", ".yaml", ".yml",
    ".json", ".txt", ".py", ".jinja", ".jinja2",
    ".tsv", ".csv",
}

# ─────────────────────────────────────────────────────────────────────────────
# Paid-content CTA detection patterns (regex — case-insensitive).
# Tuned to match the URL host + an indicative buy-CTA path.
# ─────────────────────────────────────────────────────────────────────────────
PAID_CTA_PATTERNS: list[tuple[str, str]] = [
    # (pattern, "suggested replacement hint")
    (r"https?://(?:www\.)?amazon\.com/dp/", "https://pearlprime.shop/en-US/book/<brand>/<inner_key>"),
    (r"https?://(?:www\.)?amazon\.co\.jp/dp/", "https://pearlprime.shop/ja-JP/book/<brand>/<inner_key>"),
    (r"https?://(?:www\.)?amazon\.de/dp/", "https://pearlprime.shop/<locale>/book/<brand>/<inner_key>"),
    (r"https?://(?:www\.)?amazon\.co\.uk/dp/", "https://pearlprime.shop/<locale>/book/<brand>/<inner_key>"),
    (r"https?://(?:www\.)?amazon\.fr/dp/", "https://pearlprime.shop/<locale>/book/<brand>/<inner_key>"),
    (r"https?://(?:www\.)?amazon\.com\.br/dp/", "https://pearlprime.shop/<locale>/book/<brand>/<inner_key>"),
    (r"https?://(?:www\.)?amazon\.com\.au/dp/", "https://pearlprime.shop/<locale>/book/<brand>/<inner_key>"),
    (r"https?://(?:www\.)?amazon\.com\.mx/dp/", "https://pearlprime.shop/<locale>/book/<brand>/<inner_key>"),
    (r"https?://(?:www\.)?amazon\.es/dp/", "https://pearlprime.shop/<locale>/book/<brand>/<inner_key>"),
    (r"https?://(?:www\.)?play\.google\.com/store/books", "https://pearlprime.shop/<locale>/book/<brand>/<inner_key>"),
    (r"https?://(?:www\.)?play\.google\.com/store/audiobooks", "https://pearlprime.shop/<locale>/audiobook/<brand>/<inner_key>"),
    (r"https?://(?:www\.)?audible\.com/pd/", "https://pearlprime.shop/en-US/audiobook/<brand>/<inner_key>"),
    (r"https?://(?:www\.)?audible\.co\.jp/pd/", "https://pearlprime.shop/ja-JP/audiobook/<brand>/<inner_key>"),
    (r"https?://(?:www\.)?audible\.de/pd/", "https://pearlprime.shop/<locale>/audiobook/<brand>/<inner_key>"),
    (r"https?://(?:www\.)?audible\.co\.uk/pd/", "https://pearlprime.shop/<locale>/audiobook/<brand>/<inner_key>"),
    (r"https?://(?:www\.)?books\.apple\.com/", "https://pearlprime.shop/<locale>/book/<brand>/<inner_key>"),
    (r"https?://(?:www\.)?kobo\.com/(?:[a-z\-]+/)?ebook/", "https://pearlprime.shop/<locale>/book/<brand>/<inner_key>"),
    (r"https?://(?:www\.)?kobo\.com/(?:[a-z\-]+/)?audiobook/", "https://pearlprime.shop/<locale>/audiobook/<brand>/<inner_key>"),
    (r"https?://(?:www\.)?webtoons\.com/", "https://pearlprime.shop/<locale>/manga/<brand>/<series_id>"),
    (r"https?://(?:www\.)?webtoon\.com/", "https://pearlprime.shop/<locale>/manga/<brand>/<series_id>"),
    (r"https?://(?:www\.)?comic\.naver\.com/", "https://pearlprime.shop/<locale>/manga/<brand>/<series_id>"),
    (r"https?://(?:www\.)?honto\.jp/", "https://pearlprime.shop/ja-JP/book/<brand>/<inner_key>"),
    (r"https?://(?:www\.)?cmoa\.jp/", "https://pearlprime.shop/ja-JP/manga/<brand>/<series_id>"),
    (r"https?://(?:www\.)?bookwalker\.jp/", "https://pearlprime.shop/ja-JP/<product_type>/<brand>/<inner_key>"),
    # Affiliate shorteners
    (r"https?://amzn\.to/", "https://pearlprime.shop/<locale>/<product_type>/<brand>/<inner_key>"),
    (r"https?://geni\.us/", "https://pearlprime.shop/<locale>/<product_type>/<brand>/<inner_key>"),
]

# Spotify is a special case: "listen on Spotify Podcasts" is allowed on
# brand-bio discovery surfaces (§14.4); only the "buy this track/album" CTA
# unifies. Detect ONLY in proximity to a "buy" verb.
SPOTIFY_BUY_CONTEXT = re.compile(
    r"(?i)(?:buy|purchase)\b[^\n]{0,40}spotify\.com/(?:track|album)/"
)


COMPILED_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(p, re.IGNORECASE), hint) for p, hint in PAID_CTA_PATTERNS
]


# ─────────────────────────────────────────────────────────────────────────────
# Allow-list
# ─────────────────────────────────────────────────────────────────────────────
ALLOWLIST_PATH = REPO_ROOT / "config" / "storefront" / "external_link_allowlist.yaml"


def _load_allowlist() -> list[dict]:
    if not ALLOWLIST_PATH.exists():
        return []
    if yaml is None:
        print("WARN: PyYAML not installed; allowlist disabled.", file=sys.stderr)
        return []
    with open(ALLOWLIST_PATH) as f:
        doc = yaml.safe_load(f) or {}
    entries = doc.get("allowlist") or []
    if not isinstance(entries, list):
        return []
    return [e for e in entries if isinstance(e, dict)]


def _allowlisted(file_rel: str, line_no: int, matched_url: str, allowlist: list[dict]) -> bool:
    for entry in allowlist:
        fp = entry.get("file_path")
        ln = entry.get("line_no")
        mu = entry.get("matched_url")
        if fp and fp != file_rel:
            continue
        if ln is not None and ln != line_no:
            continue
        if mu and mu not in matched_url:
            continue
        return True
    return False


# ─────────────────────────────────────────────────────────────────────────────
# Walk + scan
# ─────────────────────────────────────────────────────────────────────────────
def _iter_files(surfaces: Iterable[str]) -> Iterable[pathlib.Path]:
    for surface in surfaces:
        root = REPO_ROOT / surface
        if not root.exists():
            continue
        if root.is_file():
            yield root
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            # Skip dotfiles + node_modules + python cache
            dirnames[:] = [d for d in dirnames if not d.startswith(".") and d not in {"node_modules", "__pycache__"}]
            for name in filenames:
                path = pathlib.Path(dirpath) / name
                if path.suffix.lower() in SCAN_EXTENSIONS:
                    yield path


def _scan_file(path: pathlib.Path, allowlist: list[dict]) -> list[tuple[str, int, str, str]]:
    """Return list of (file_rel, line_no, matched_url, suggested_url)."""
    violations: list[tuple[str, int, str, str]] = []
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line_no, line in enumerate(f, start=1):
                for rx, hint in COMPILED_PATTERNS:
                    for m in rx.finditer(line):
                        matched = m.group(0)
                        file_rel = str(path.relative_to(REPO_ROOT))
                        if _allowlisted(file_rel, line_no, matched, allowlist):
                            continue
                        violations.append((file_rel, line_no, matched, hint))
                # Spotify buy context (only flagged when verb proximity)
                for m in SPOTIFY_BUY_CONTEXT.finditer(line):
                    matched = m.group(0)
                    file_rel = str(path.relative_to(REPO_ROOT))
                    if _allowlisted(file_rel, line_no, matched, allowlist):
                        continue
                    violations.append((file_rel, line_no, matched, "https://pearlprime.shop/<locale>/music/<brand>/<inner_key>"))
    except (OSError, UnicodeDecodeError):
        pass
    return violations


# ─────────────────────────────────────────────────────────────────────────────
# main
# ─────────────────────────────────────────────────────────────────────────────
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fail-on-violation",
        action="store_true",
        help="Exit 1 if any violation found (HARD-cutover gate).",
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="Always exit 0; report violations to stdout only.",
    )
    parser.add_argument(
        "--tsv-out",
        default=None,
        help="Override default TSV output path (default: artifacts/qa/external_buy_links_violations_<date>.tsv).",
    )
    parser.add_argument(
        "--surfaces",
        nargs="*",
        default=None,
        help="Override default sweep surfaces (for testing).",
    )
    args = parser.parse_args()

    surfaces = args.surfaces or SWEEP_SURFACES
    allowlist = _load_allowlist()

    all_violations: list[tuple[str, int, str, str]] = []
    for path in _iter_files(surfaces):
        all_violations.extend(_scan_file(path, allowlist))

    # Output TSV
    today = datetime.date.today().isoformat()
    tsv_path = (
        REPO_ROOT / args.tsv_out
        if args.tsv_out
        else REPO_ROOT / "artifacts" / "qa" / f"external_buy_links_violations_{today}.tsv"
    )
    tsv_path.parent.mkdir(parents=True, exist_ok=True)
    with open(tsv_path, "w") as f:
        f.write("file_path\tline_no\tmatched_url\tsuggested_storefront_url\n")
        for row in all_violations:
            f.write("\t".join(str(x) for x in row) + "\n")

    n = len(all_violations)
    if n == 0:
        print(f"OK: zero external paid-CTA violations across {len(surfaces)} sweep surfaces.")
        print(f"     TSV: {tsv_path.relative_to(REPO_ROOT)}")
        return 0

    print(f"FAIL: {n} external paid-CTA violations found.", file=sys.stderr)
    print(f"      TSV: {tsv_path.relative_to(REPO_ROOT)}", file=sys.stderr)
    for row in all_violations[:25]:
        print(f"  {row[0]}:{row[1]}  {row[2]}", file=sys.stderr)
    if n > 25:
        print(f"  ... ({n - 25} more — see TSV)", file=sys.stderr)

    if args.warn_only:
        return 0
    if args.fail_on_violation:
        return 1
    # Default behavior when neither flag set: warn-only.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
