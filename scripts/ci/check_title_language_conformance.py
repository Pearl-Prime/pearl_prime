#!/usr/bin/env python3
"""CI gate: title/subtitle LANGUAGE-conformance for non-English catalogs.

Thin CI wrapper around scripts/localization/check_title_language_conformance.py
(the detector itself; see that module's docstring for detection strategy —
english_copy_through, ascii_only_in_cjk_locale, wrong_script Traditional-vs-
Simplified via opencc + Big5/GB2312 codec-encodability, script_mismatch_ja/ko).
This gate exists because a correct detector that isn't wired into CI is not
an enforced mechanism (docs/BESTSELLER_DRIFT_ROOT_CAUSE... meta-rule: memory
is recall, not enforcement) -- it's just tribal knowledge that the tool exists.

Modes (mirrors scripts/ci/check_native_check.py):
  --bootstrap-mode   report totals, exit 0 regardless (transition; current
                      real debt as of 2026-07-23 is ~141k files across
                      pt_BR/zh_CN/zh_HK/zh_SG/zh_TW -- not a same-day fix)
  --production-only  fail if any hard-reason non-conformant file exists
                      (ship gate; CI default when not bootstrap)
  --locales          restrict to a subset (default: all 13 non-English)

Run:
  PYTHONPATH=. python3 scripts/ci/check_title_language_conformance.py --bootstrap-mode
  PYTHONPATH=. python3 scripts/ci/check_title_language_conformance.py --production-only --locales ja_JP ko_KR

Exit: 0 pass; 1 fail (production-only mode with non-conformant files found).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts.localization.check_title_language_conformance import (  # noqa: E402
    ALL_TARGET_LOCALES,
    build_en_reference,
    scan_book_surface,
    scan_manga_and_illustrated,
    _manga_plan_paths,
    _is_illustrated,
)
from scripts.catalog.locale_paths import plan_dirs  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bootstrap-mode", action="store_true", help="Report only, always exit 0")
    ap.add_argument(
        "--production-only",
        action="store_true",
        help="Fail if any hard-reason non-conformant file exists (default when --bootstrap-mode absent)",
    )
    ap.add_argument("--locales", nargs="*", default=None, help="Subset of locales; default = all 13 non-English")
    args = ap.parse_args(argv)

    bootstrap_mode = args.bootstrap_mode
    production_only = args.production_only or not bootstrap_mode

    target_locales = sorted(_norm(l) for l in args.locales) if args.locales else sorted(ALL_TARGET_LOCALES)

    en_book_dir, _ = plan_dirs(REPO_ROOT, "en_US")
    en_illust_paths = [p for p in _manga_plan_paths("en_US") if _is_illustrated(p)]
    en_manga_paths = [p for p in _manga_plan_paths("en_US") if not _is_illustrated(p)]
    en_titles, en_subtitles = build_en_reference(en_book_dir, en_illust_paths, en_manga_paths)

    total_non_conformant = 0
    total_checked = 0
    per_locale = []
    for locale in target_locales:
        book_title_rep, book_sub_rep = scan_book_surface(locale, en_titles, en_subtitles)
        illust_rep, manga_rep = scan_manga_and_illustrated(locale, en_titles)
        locale_non_conf = (
            book_title_rep.non_conformant_files
            + book_sub_rep.non_conformant_files
            + illust_rep.non_conformant_files
            + manga_rep.non_conformant_files
        )
        locale_checked = book_title_rep.files_checked + illust_rep.files_checked + manga_rep.files_checked
        total_non_conformant += locale_non_conf
        total_checked += locale_checked
        per_locale.append((locale, locale_non_conf, locale_checked))

    print(f"[title-language-conformance] mode={'bootstrap' if bootstrap_mode else 'production-only'}")
    for locale, non_conf, checked in per_locale:
        if non_conf:
            print(f"  {locale}: {non_conf} non-conformant / {checked} checked")
    print(f"  TOTAL: {total_non_conformant} non-conformant / {total_checked} checked "
          f"across {len(target_locales)} locale(s)")

    if total_non_conformant == 0:
        print("PASS: all checked locales conformant.")
        return 0

    if bootstrap_mode:
        print(f"WARN (bootstrap): {total_non_conformant} non-conformant files exist; "
              "not blocking while rollout is in progress (see project_title_metadata_english_copy_through memory).")
        return 0

    print(f"FAIL: {total_non_conformant} non-conformant title/subtitle files "
          "(run with --bootstrap-mode to report-only during active rollout).")
    return 1


def _norm(raw: str) -> str:
    return raw.replace("-", "_")


if __name__ == "__main__":
    sys.exit(main())
