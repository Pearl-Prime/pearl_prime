#!/usr/bin/env python3
"""Track manga chapter_script YAML rows that need native-speaker QA per locale.

The canonical tracker is a UTF-8 TSV under artifacts/qa/ (see
docs/runbooks/JA_JP_NATIVE_REVIEW_PROCESS.md).

Schema columns (tab-separated, header row required):
  series_id          — Writer handoff series_id field
  chapter_id         — e.g. ep_001
  brand_label        — Human label for PM (e.g. Brand-2, stillness_press)
  yaml_locale        — Locale key inside YAML dicts (e.g. ja_JP)
  tier               — Translation lane (e.g. V1_inline, V2_human_polish)
  source_status      — Machine/stub hint (tier1_inline_shipped | stub_placeholder | empty_pending)
  queue_status       — pending_native_review | in_review | native_signed_off | blocked
  script_relpath     — Repo-relative path to ep_*.yaml
  open_date          — YYYY-MM-DD
  target_surface     — e.g. WEBTOON_Japan, internal_QA
  notes              — Free text

Usage:
  python3 scripts/localization/queue_native_review.py list --tsv artifacts/qa/native_review_queue_2026-05-07.tsv
  python3 scripts/localization/queue_native_review.py add --tsv ... --series-id S --chapter-id ep_001 ...
  python3 scripts/localization/queue_native_review.py set-status --tsv ... --series-id S --chapter-id ep_001 \\
      --locale ja_JP --status native_signed_off
  python3 scripts/localization/queue_native_review.py summary --tsv ...
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]

REQUIRED_COLUMNS: tuple[str, ...] = (
    "series_id",
    "chapter_id",
    "brand_label",
    "yaml_locale",
    "tier",
    "source_status",
    "queue_status",
    "script_relpath",
    "open_date",
    "target_surface",
    "notes",
)


def default_queue_path() -> Path:
    return REPO_ROOT / "artifacts" / "qa" / "native_review_queue_2026-05-07.tsv"


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines:
        raise SystemExit(f"Empty queue file: {path}")
    rows: list[dict[str, str]] = []
    reader = csv.DictReader(lines, delimiter="\t")
    if reader.fieldnames is None:
        raise SystemExit(f"Missing header row: {path}")
    header = [h.strip() for h in reader.fieldnames if h]
    missing = [c for c in REQUIRED_COLUMNS if c not in header]
    if missing:
        raise SystemExit(f"Queue file missing columns {missing}: {path}")
    for row in reader:
        norm = {k: (row.get(k) or "").strip() for k in REQUIRED_COLUMNS}
        rows.append(norm)
    return list(REQUIRED_COLUMNS), rows


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    out_lines = []
    out_lines.append("\t".join(REQUIRED_COLUMNS))
    for r in rows:
        out_lines.append("\t".join(r.get(c, "") for c in REQUIRED_COLUMNS))
    path.write_text("\n".join(out_lines) + "\n", encoding="utf-8")


def find_row(rows: list[dict[str, str]], series_id: str, chapter_id: str, yaml_locale: str) -> int | None:
    for i, row in enumerate(rows):
        if (
            row["series_id"] == series_id
            and row["chapter_id"] == chapter_id
            and row["yaml_locale"] == yaml_locale
        ):
            return i
    return None


def cmd_list(path: Path) -> int:
    _, rows = read_rows(path)
    for row in rows:
        print("{queue_status}: {brand_label} {chapter_id} [{yaml_locale}] -> {script_relpath}".format(**row))
    return 0


def cmd_summary(path: Path) -> int:
    _, rows = read_rows(path)
    counts: dict[str, int] = {}
    for row in rows:
        st = row.get("queue_status") or "(empty)"
        counts[st] = counts.get(st, 0) + 1
    for k in sorted(counts.keys()):
        print(f"{k}\t{counts[k]}")
    return 0


def cmd_add(
    path: Path,
    *,
    series_id: str,
    chapter_id: str,
    brand_label: str,
    locale: str,
    tier: str,
    source_status: str,
    queue_status: str,
    script_relpath: str,
    open_date: str,
    target_surface: str,
    notes: str,
) -> int:
    if path.exists():
        _, rows = read_rows(path)
    else:
        rows = []
    if find_row(rows, series_id, chapter_id, locale) is not None:
        print(
            "Row already exists for series_id/chapter/locale — use set-status or edit TSV.",
            file=sys.stderr,
        )
        return 1
    rows.append(
        {
            "series_id": series_id,
            "chapter_id": chapter_id,
            "brand_label": brand_label,
            "yaml_locale": locale,
            "tier": tier,
            "source_status": source_status,
            "queue_status": queue_status,
            "script_relpath": script_relpath,
            "open_date": open_date,
            "target_surface": target_surface,
            "notes": notes.replace("\t", " "),
        }
    )
    write_rows(path, rows)
    return 0


def cmd_set_status(
    path: Path,
    *,
    series_id: str,
    chapter_id: str,
    locale: str,
    status: str,
    notes_append: str | None,
) -> int:
    _, rows = read_rows(path)
    idx = find_row(rows, series_id, chapter_id, locale)
    if idx is None:
        print("No matching row.", file=sys.stderr)
        return 1
    rows[idx]["queue_status"] = status
    if notes_append:
        prev = rows[idx]["notes"].strip()
        suffix = notes_append.strip().replace("\t", " ")
        rows[idx]["notes"] = (prev + " | " + suffix).strip(" |") if prev else suffix
    write_rows(path, rows)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument(
        "--tsv",
        type=Path,
        default=default_queue_path(),
        help=f"Tracker TSV (default: {default_queue_path().relative_to(REPO_ROOT)})",
    )

    subs = p.add_subparsers(dest="cmd", required=True)

    subs.add_parser("list", help="Print one line per queued item")
    subs.add_parser("summary", help="Count rows by queue_status")

    pa = subs.add_parser("add", help="Append a row (fails if key exists)")
    pa.add_argument("--series-id", required=True)
    pa.add_argument("--chapter-id", required=True)
    pa.add_argument("--brand-label", required=True)
    pa.add_argument("--locale", required=True, help="YAML key e.g. ja_JP")
    pa.add_argument("--tier", required=True)
    pa.add_argument("--source-status", required=True)
    pa.add_argument("--queue-status", default="pending_native_review")
    pa.add_argument("--script-relpath", required=True)
    pa.add_argument("--open-date", required=True)
    pa.add_argument("--target-surface", required=True)
    pa.add_argument("--notes", default="")

    ps = subs.add_parser("set-status", help="Update queue_status (+ optional notes append)")
    ps.add_argument("--series-id", required=True)
    ps.add_argument("--chapter-id", required=True)
    ps.add_argument("--locale", required=True)
    ps.add_argument("--status", required=True)
    ps.add_argument("--notes-append")

    return p


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    args = build_parser().parse_args(argv)

    path: Path = args.tsv
    path = Path(path)
    if not path.is_absolute():
        path = (REPO_ROOT / path).resolve()

    cmd: str = args.cmd

    if cmd == "list":
        if not path.exists():
            print(f"Missing {path}", file=sys.stderr)
            return 2
        return cmd_list(path)
    if cmd == "summary":
        if not path.exists():
            print(f"Missing {path}", file=sys.stderr)
            return 2
        return cmd_summary(path)
    if cmd == "add":
        return cmd_add(
            path,
            series_id=args.series_id,
            chapter_id=args.chapter_id,
            brand_label=args.brand_label,
            locale=args.locale,
            tier=args.tier,
            source_status=args.source_status,
            queue_status=args.queue_status,
            script_relpath=args.script_relpath,
            open_date=args.open_date,
            target_surface=args.target_surface,
            notes=args.notes,
        )
    if cmd == "set-status":
        if not path.exists():
            print(f"Missing {path}", file=sys.stderr)
            return 2
        return cmd_set_status(
            path,
            series_id=args.series_id,
            chapter_id=args.chapter_id,
            locale=args.locale,
            status=args.status,
            notes_append=args.notes_append,
        )

    raise AssertionError(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
