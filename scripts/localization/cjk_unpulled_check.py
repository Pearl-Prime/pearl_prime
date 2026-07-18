#!/usr/bin/env python3
"""Loud check: Pearl Star locale atom ceiling vs origin/main.

Surfaces stranded inventory (on PS but not on origin) so translation runs
cannot silently complete without landing.

Usage:
  python3 scripts/localization/cjk_unpulled_check.py
  python3 scripts/localization/cjk_unpulled_check.py --locale ja_JP --json
  python3 scripts/localization/cjk_unpulled_check.py --strict   # exit 1 if any stranded
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

LOCALE_TO_PATH = {
    "ja_JP": "ja-JP",
    "zh_TW": "zh-TW",
    "zh_CN": "zh-CN",
    "ko_KR": "ko-KR",
    "zh_HK": "zh-HK",
    "zh_SG": "zh-SG",
}

SSH_HOST = "pearl_star"
PS_REPO = "~/phoenix_omega"


def _origin_paths(locale_key: str) -> set[str]:
    hyp = LOCALE_TO_PATH[locale_key]
    needle = f"/locales/{hyp}/CANONICAL.txt"
    out = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", "origin/main"],
        cwd=REPO_ROOT,
        text=True,
    )
    return {line.strip() for line in out.splitlines() if needle in line}


def _pearl_star_paths(locale_key: str) -> set[str]:
    hyp = LOCALE_TO_PATH[locale_key]
    remote = (
        f"cd {PS_REPO} && find atoms -path '*/locales/{hyp}/CANONICAL.txt' "
        "-type f 2>/dev/null | sort"
    )
    proc = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", SSH_HOST, remote],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"ssh pearl_star failed: {proc.stderr.strip()}")
    return {line.strip() for line in proc.stdout.splitlines() if line.strip()}


def _en_base_count() -> int:
    out = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", "origin/main"],
        cwd=REPO_ROOT,
        text=True,
    )
    n = 0
    for line in out.splitlines():
        if line.endswith("/CANONICAL.txt") and "/locales/" not in line:
            n += 1
    return n


def check_locale(locale_key: str, *, exclude_paths: set[str] | None = None) -> dict:
    origin = _origin_paths(locale_key)
    ps = _pearl_star_paths(locale_key)
    exclude = exclude_paths or set()
    stranded = sorted(ps - origin - exclude)
    return {
        "locale": locale_key,
        "origin_count": len(origin),
        "pearl_star_count": len(ps),
        "stranded_count": len(stranded),
        "stranded_paths": stranded,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--locale", choices=sorted(LOCALE_TO_PATH), help="Single locale")
    ap.add_argument("--exclude-file", help="Repo-relative paths to exclude (e.g. backlog)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true", help="Exit 1 when any stranded > 0")
    ap.add_argument("--write-stranded", help="Write stranded repo-relative paths to file")
    args = ap.parse_args(argv)

    exclude: set[str] = set()
    if args.exclude_file:
        pf = Path(args.exclude_file)
        for line in pf.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                exclude.add(line)

    locales = [args.locale] if args.locale else list(LOCALE_TO_PATH.keys())
    en_base = _en_base_count()
    rows = [check_locale(loc, exclude_paths=exclude) for loc in locales]

    if args.write_stranded and len(locales) == 1:
        Path(args.write_stranded).write_text(
            "\n".join(rows[0]["stranded_paths"]) + ("\n" if rows[0]["stranded_paths"] else ""),
            encoding="utf-8",
        )

    if args.json:
        print(json.dumps({"en_us_base": en_base, "locales": rows}, indent=2))
    else:
        print(f"CJK unpulled check — en_US base on origin: {en_base}")
        print(f"{'Locale':<8} {'Origin':>8} {'PS':>8} {'Stranded':>10} {'% origin':>10}")
        any_stranded = False
        for r in rows:
            pct = 100.0 * r["origin_count"] / en_base if en_base else 0.0
            print(
                f"{r['locale']:<8} {r['origin_count']:>8} {r['pearl_star_count']:>8} "
                f"{r['stranded_count']:>10} {pct:>9.1f}%"
            )
            if r["stranded_count"]:
                any_stranded = True
                print(f"  ⚠ {r['stranded_count']} atoms on Pearl Star not on origin/main")
        if any_stranded:
            print("\nACTION: run cjk_translate_and_land.sh pull-stranded — do not treat translation as done.")
        else:
            print("\nOK — no stranded locale atoms detected.")

    total_stranded = sum(r["stranded_count"] for r in rows)
    if args.strict and total_stranded > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
