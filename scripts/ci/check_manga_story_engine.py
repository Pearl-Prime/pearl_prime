#!/usr/bin/env python3
"""Governed story-engine audit — batch scan chapter scripts + architect probes.

Runtime enforcement lives in bestseller_gate; this gate catches generic spines
across a corpus before render/QC dispatch.

Run:
    PYTHONPATH=. python3 scripts/ci/check_manga_story_engine.py
    PYTHONPATH=. python3 scripts/ci/check_manga_story_engine.py --audit-all-authored
    PYTHONPATH=. python3 scripts/ci/check_manga_story_engine.py --architect-probe
    PYTHONPATH=scripts/ci:. python3 scripts/ci/check_manga_story_engine.py \\
        --base origin/main --head HEAD

Exit: 0 conformant; 1 violation (named reason).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from drift_detector_git import changed_paths, repo_root_from_script  # noqa: E402

from phoenix_v4.manga.qc.story_engine_audit import (  # noqa: E402
    audit_architect_governed_genres,
    audit_chapter_script_corpus,
    audit_chapter_script_engine,
    merge_audit_rows,
    write_audit_tsv,
)

REPO_ROOT = repo_root_from_script(Path(__file__))
DEFAULT_AUDIT_REPORT = (
    REPO_ROOT / "artifacts" / "qa" / "manga_story_engine_audit" / "STORY_ENGINE_MISMATCH.tsv"
)
CHAPTER_SCRIPT_MARKERS = (
    "artifacts/manga/chapter_scripts/",
    "artifacts/manga/pilots/",
)


class StoryEngineAuditError(Exception):
    """Raised when a governed script fails story-engine validation."""


def assert_story_engine(path: Path, *, repo_root: Path = REPO_ROOT) -> None:
    row = audit_chapter_script_engine(path, repo_root=repo_root)
    if row["status"] == "FAIL":
        raise StoryEngineAuditError(f"{path}: {row['failure_reasons']}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Governed story-engine batch audit")
    ap.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    ap.add_argument("--chapter-script", type=Path, default=None)
    ap.add_argument("--base", default=None)
    ap.add_argument("--head", default="HEAD")
    ap.add_argument("--paths", nargs="*", default=None)
    ap.add_argument(
        "--audit-all-authored",
        action="store_true",
        help="scan chapter_scripts + pilots for governed genres",
    )
    ap.add_argument(
        "--architect-probe",
        action="store_true",
        help="probe architect output for every governed genre with strategy bank",
    )
    ap.add_argument(
        "--report-out",
        type=Path,
        default=DEFAULT_AUDIT_REPORT,
        help="audit TSV destination",
    )
    ap.add_argument(
        "--series-id",
        action="append",
        default=[],
        help="audit explicit series_id script trees",
    )
    args = ap.parse_args(argv)

    if not (
        args.chapter_script
        or args.audit_all_authored
        or args.architect_probe
        or args.series_id
        or args.paths is not None
        or args.base
    ):
        args.architect_probe = True

    if args.chapter_script:
        try:
            assert_story_engine(args.chapter_script, repo_root=args.repo_root)
            print(f"STORY-ENGINE: PASS ({args.chapter_script})", file=sys.stderr)
            return 0
        except StoryEngineAuditError as e:
            print(f"STORY-ENGINE BLOCKED: {e}", file=sys.stderr)
            return 1

    rows: list[dict[str, str]] = []
    if args.audit_all_authored or args.architect_probe:
        if args.audit_all_authored:
            rows.extend(
                audit_chapter_script_corpus(
                    args.repo_root,
                    series_ids=args.series_id or None,
                )
            )
        if args.architect_probe:
            rows.extend(audit_architect_governed_genres(args.repo_root))
        rows = merge_audit_rows(rows)
        write_audit_tsv(rows, args.report_out)
        fails = [r for r in rows if r["status"] == "FAIL"]
        print(
            f"STORY-ENGINE AUDIT: {len(rows)} row(s); "
            f"{len(fails)} FAIL → {args.report_out}",
            file=sys.stderr,
        )
        for r in fails:
            print(f"  FAIL {r['script_path']}: {r['failure_reasons']}", file=sys.stderr)
        return 1 if fails else 0

    if args.series_id:
        rows = audit_chapter_script_corpus(
            args.repo_root, series_ids=args.series_id, only_governed=True,
        )
        fails = [r for r in rows if r["status"] == "FAIL"]
        if not fails:
            print(f"STORY-ENGINE: PASS ({len(rows)} script(s))", file=sys.stderr)
            return 0
        for r in fails:
            print(f"FAIL {r['script_path']}: {r['failure_reasons']}", file=sys.stderr)
        return 1

    if args.paths is not None:
        targets = list(args.paths)
    elif args.base:
        targets = [
            p for p in changed_paths(args.base, args.head, args.repo_root)
            if p.endswith(".yaml")
            and any(p.startswith(m) for m in CHAPTER_SCRIPT_MARKERS)
        ]
    else:
        targets = []

    failures: list[str] = []
    for rel in sorted(set(targets)):
        try:
            assert_story_engine(args.repo_root / rel, repo_root=args.repo_root)
        except StoryEngineAuditError as e:
            failures.append(str(e))
    if not failures:
        if targets:
            print(f"STORY-ENGINE: PASS ({len(targets)} changed script(s))", file=sys.stderr)
        else:
            print("STORY-ENGINE: PASS (no changed scripts; use --audit-all-authored)", file=sys.stderr)
        return 0
    for f in failures:
        print(f"FAIL: {f}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
