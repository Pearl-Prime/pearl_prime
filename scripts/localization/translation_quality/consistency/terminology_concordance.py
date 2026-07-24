#!/usr/bin/env python3
"""Terminology-concordance builder.

Finds every occurrence of every glossary term (from
analysis/<locale_dir>/glossary_core.yaml + glossary_project.yaml) across
the translated corpus, for Claude to scan for drift. Deterministic
extraction only -- this module does not judge whether a variant rendering
is a drift problem or a legitimate context-sensitive choice (glossary_project
already documents which terms are context-sensitive via
`preferred_by_context`).

Usage:
    python3 scripts/localization/translation_quality/consistency/terminology_concordance.py \\
        --locale zh-CN --atoms-root atoms --out artifacts/qa/concordance_zh_cn.json
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))

LOCALE_ANALYSIS_DIRS = {
    "zh-CN": "zh_cn",
    "zh-TW": "zh_tw",
    "zh-HK": "zh_hk",
    "zh-SG": "zh_sg",
    "ja-JP": "ja_jp",
    "ko-KR": "ko_kr",
}


def _locale_dirname(locale: str) -> str:
    return locale.replace("-", "_").lower()


def load_glossary_terms(locale: str) -> dict[str, list[str]]:
    """Return {source_term: [all known rendering variants]} across
    glossary_core.yaml + glossary_project.yaml, so the concordance can
    match any of them (not just the single `preferred` rendering)."""
    d = LOCALE_ANALYSIS_DIRS.get(locale, _locale_dirname(locale))
    adir = REPO_ROOT / "analysis" / d
    out: dict[str, list[str]] = defaultdict(list)

    core = adir / "glossary_core.yaml"
    if core.is_file():
        data = yaml.safe_load(core.read_text(encoding="utf-8")) or {}
        for term in data.get("terms") or []:
            source = term.get("source", "")
            variants = [term.get("preferred")] + list(term.get("context_alt") or [])
            out[source].extend(v for v in variants if v)

    project = adir / "glossary_project.yaml"
    if project.is_file():
        data = yaml.safe_load(project.read_text(encoding="utf-8")) or {}
        for term in data.get("terms") or []:
            source = term.get("source", "")
            by_context = term.get("preferred_by_context") or {}
            out[source].extend(v for v in by_context.values() if v)

    return {k: sorted(set(v)) for k, v in out.items()}


def find_localized_files(atoms_root: Path, locale: str) -> list[Path]:
    return sorted(atoms_root.rglob(f"locales/{locale}/CANONICAL.txt"))


def build_concordance(atoms_root: Path, locale: str) -> dict[str, Any]:
    terms = load_glossary_terms(locale)
    files = find_localized_files(atoms_root, locale)

    # concordance[source_term][rendering] -> list of file paths using it
    concordance: dict[str, dict[str, list[str]]] = {src: defaultdict(list) for src in terms}

    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        rel = str(path.relative_to(REPO_ROOT))
        for source, variants in terms.items():
            for variant in variants:
                if variant and variant in text:
                    concordance[source][variant].append(rel)

    out: dict[str, Any] = {}
    for source, by_variant in concordance.items():
        if not by_variant:
            continue
        out[source] = {
            "variants_found": {v: len(paths) for v, paths in by_variant.items()},
            "distinct_renderings": len(by_variant),
            "files_by_variant": {v: paths for v, paths in by_variant.items()},
        }
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--locale", required=True)
    ap.add_argument("--atoms-root", type=Path, default=REPO_ROOT / "atoms")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)

    concordance = build_concordance(args.atoms_root, args.locale)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(concordance, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    multi_rendering = {k: v for k, v in concordance.items() if v["distinct_renderings"] > 1}
    print(f"Wrote {args.out}: {len(concordance)} terms found, {len(multi_rendering)} with >1 distinct rendering")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
