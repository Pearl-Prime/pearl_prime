#!/usr/bin/env python3
"""Build exact 14-language (en-US baseline + 13 translated locales) coverage worklists."""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any

TRANSLATED_LOCALES = (
    "ja-JP", "zh-TW", "zh-CN", "zh-HK", "zh-SG", "ko-KR",
    "es-US", "pt-BR", "es-ES", "fr-FR", "de-DE", "it-IT", "hu-HU",
)
HEADER_RE = re.compile(r"(?m)^##\s+([A-Z][A-Z0-9_]*)\s+v(\d+)\s*$")
PLACEHOLDER_RE = re.compile(
    r"\[[^\]]*(?:placeholder|persona-specific|content for|todo|tbd)[^\]]*\]",
    re.IGNORECASE,
)
ENGLISH_SENTENCE_RE = re.compile(
    r"\b(?:the|this|that|you|your|when|because|what|with|from)\b",
    re.IGNORECASE,
)


def _headers(path: Path) -> list[str]:
    if not path.is_file():
        return []
    return [f"{m.group(1)}_v{m.group(2)}" for m in HEADER_RE.finditer(path.read_text(encoding="utf-8"))]


def _prose_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def build(repo: Path) -> dict[str, Any]:
    atoms = repo / "atoms"
    base_files = [
        path for path in atoms.rglob("CANONICAL.txt")
        if "locales" not in path.relative_to(atoms).parts
    ]
    rows = []
    locale_totals = {
        locale: {"base_files": 0, "complete_files": 0, "missing_files": 0, "partial_files": 0}
        for locale in TRANSLATED_LOCALES
    }
    for base in sorted(base_files):
        base_headers = _headers(base)
        if not base_headers:
            continue
        rel = base.relative_to(repo)
        for locale in TRANSLATED_LOCALES:
            localized = base.parent / "locales" / locale / "CANONICAL.txt"
            local_headers = _headers(localized)
            missing_headers = sorted(set(base_headers) - set(local_headers))
            duplicate_headers = sorted({
                value for value in local_headers if local_headers.count(value) > 1
            })
            text = _prose_text(localized)
            placeholders = PLACEHOLDER_RE.findall(text)
            # This is a warning signal, not proof of untranslated prose.
            english_fallback_signal = bool(
                localized.is_file()
                and locale not in {"es-US", "es-ES", "pt-BR", "fr-FR", "de-DE", "it-IT"}
                and len(ENGLISH_SENTENCE_RE.findall(text)) >= 8
            )
            if not localized.is_file():
                status = "MISSING"
            elif missing_headers or duplicate_headers or placeholders:
                status = "PARTIAL"
            else:
                status = "COMPLETE"
            locale_totals[locale]["base_files"] += 1
            locale_totals[locale][
                "complete_files" if status == "COMPLETE"
                else "missing_files" if status == "MISSING"
                else "partial_files"
            ] += 1
            if status != "COMPLETE" or english_fallback_signal:
                rows.append({
                    "locale": locale,
                    "base_file": str(rel),
                    "localized_file": str(localized.relative_to(repo)),
                    "status": status,
                    "base_atom_count": len(base_headers),
                    "localized_atom_count": len(local_headers),
                    "missing_atom_ids": missing_headers,
                    "duplicate_atom_ids": duplicate_headers,
                    "placeholder_count": len(placeholders),
                    "english_fallback_signal": english_fallback_signal,
                    "slot_family": base.parent.name,
                    "persona": base.relative_to(atoms).parts[0],
                    "topic": base.relative_to(atoms).parts[1],
                })
    for locale, totals in locale_totals.items():
        denominator = max(1, totals["base_files"])
        totals["coverage_pct"] = round(100.0 * totals["complete_files"] / denominator, 2)
    return {
        "schema_version": "1.0.0",
        "language_count_including_en_US_baseline": 14,
        "translated_locale_count": len(TRANSLATED_LOCALES),
        "translated_locales": list(TRANSLATED_LOCALES),
        "locale_totals": locale_totals,
        "incomplete_rows": rows,
        "all_translated_locales_complete": all(
            totals["coverage_pct"] == 100.0 for totals in locale_totals.values()
        ),
        "truth": (
            "Coverage compares localized CANONICAL block IDs to the en-US base. "
            "English-fallback signal requires native review before claiming completion."
        ),
    }


def write_outputs(repo: Path, out: Path, payload: dict[str, Any]) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / "coverage_report.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    rows = payload["incomplete_rows"]
    fields = [
        "locale", "persona", "topic", "slot_family", "status",
        "base_file", "localized_file", "base_atom_count", "localized_atom_count",
        "missing_atom_ids", "duplicate_atom_ids", "placeholder_count",
        "english_fallback_signal",
    ]
    with (out / "missing_file_inventory.tsv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        for row in rows:
            copy = dict(row)
            copy["missing_atom_ids"] = ",".join(copy["missing_atom_ids"])
            copy["duplicate_atom_ids"] = ",".join(copy["duplicate_atom_ids"])
            writer.writerow({key: copy.get(key, "") for key in fields})
    shards = {}
    for locale in TRANSLATED_LOCALES:
        locale_rows = [row for row in rows if row["locale"] == locale]
        shards[locale] = {
            "locale": locale,
            "rows": locale_rows,
            "instructions": [
                "Preserve headers and metadata.",
                "Translate prose only.",
                "Use native regional register.",
                "Do not copy Chinese variants across zh-TW/zh-CN/zh-HK/zh-SG.",
                "Run parser validation after every batch.",
            ],
        }
        (out / f"shard_{locale}.json").write_text(
            json.dumps(shards[locale], ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    lines = ["# 14-Language Coverage", "", "| Locale | Coverage | Missing | Partial |", "|---|---:|---:|---:|"]
    for locale, totals in payload["locale_totals"].items():
        lines.append(
            f"| {locale} | {totals['coverage_pct']:.2f}% | "
            f"{totals['missing_files']} | {totals['partial_files']} |"
        )
    (out / "coverage_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("artifacts/qa/localization_14_coverage_20260714"),
    )
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    out = args.out if args.out.is_absolute() else repo / args.out
    payload = build(repo)
    write_outputs(repo, out, payload)
    print(json.dumps({
        "artifact_root": str(out),
        "all_complete": payload["all_translated_locales_complete"],
        "locale_totals": payload["locale_totals"],
    }, ensure_ascii=False, indent=2))
    return 0 if payload["all_translated_locales_complete"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
