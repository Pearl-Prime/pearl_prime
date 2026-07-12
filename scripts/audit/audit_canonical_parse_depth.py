#!/usr/bin/env python3
"""Catalog-wide CANONICAL.txt parse-depth audit (header count ≠ usable atoms).

WHY
---
PROGRAM_STATE / #5530: ``registry_resolver._parse_canonical_txt`` historically
treated single-delimiter / single-section legacy blocks as metadata-only and
silently returned **zero** usable atoms while headers were still countable.
``educators × imposter_syndrome × REFLECTION`` hard-failed downstream even though
a naive header count looked healthy.

This audit walks persona slot banks (REFLECTION first; broadened to every slot
family loaded by ``_load_persona_atoms``) and records, per file:

  - header_count (``## `` / bare headers)
  - usable_atom_count (parser output length)
  - delimiter_shapes seen
  - parse errors (fail-loud path)

USAGE
-----
    PYTHONPATH=. python3 scripts/audit/audit_canonical_parse_depth.py
    PYTHONPATH=. python3 scripts/audit/audit_canonical_parse_depth.py --json
    PYTHONPATH=. python3 scripts/audit/audit_canonical_parse_depth.py --write-artifact

Exit 0 always when the audit completes (report generation). Use the artifact /
JSON ``silent_zero_risk`` / ``parse_errors`` fields for gate wiring later —
this script does **not** relax existing gates.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
ATOMS_ROOT = REPO_ROOT / "atoms"
DEFAULT_ARTIFACT = (
    REPO_ROOT
    / "artifacts"
    / "qa"
    / "canonical_reflection_parse_depth_audit_2026-07-12"
    / "REPORT.json"
)

# Slot dirs consumed by registry_resolver._load_persona_atoms (_KNOWN_SLOT_DIRS).
PERSONA_SLOT_DIRS = frozenset({
    "HOOK", "SCENE", "STORY", "REFLECTION", "EXERCISE", "INTEGRATION",
    "TEACHER_DOCTRINE", "COMPRESSION", "PERMISSION", "PIVOT",
    "TAKEAWAY", "THREAD", "TRANSITION", "DWELL",
    "ANGLE_DEFINITION", "ANGLE_CALLBACK",
})

# Primary scope called out by PROGRAM_STATE; audit always includes these first.
PRIMARY_SLOTS = ("REFLECTION",)

_HEADER_RE = re.compile(r"^##\s+\S+")
_BARE_HEADER_RE = re.compile(r"^([A-Z][A-Z_]*)\s+v\d+$")
_BARE_TOKENS = frozenset({
    "HOOK", "SCENE", "STORY", "REFLECTION", "PIVOT", "EXERCISE", "INTEGRATION",
    "THREAD", "TAKEAWAY", "PERMISSION", "COMPRESSION", "RECOGNITION",
    "MECHANISM_PROOF", "TURNING_POINT", "EMBODIMENT", "COST_REVEAL", "RECKONING",
})

CONSUMER_PATHS = [
    {
        "path": "phoenix_v4/planning/registry_resolver.py::_parse_canonical_txt",
        "role": "persona + composite doctrine/reflection loader (bug surface)",
    },
    {
        "path": "phoenix_v4/planning/registry_resolver.py::_load_persona_atoms",
        "role": "walks atoms/{persona}/{topic}/{slot|engine}/CANONICAL.txt",
    },
    {
        "path": "phoenix_v4/planning/registry_resolver.py::_load_composite_doctrine_atoms",
        "role": "composite_doctrine CANONICAL.txt + REFLECTION/CANONICAL.txt",
    },
    {
        "path": "phoenix_v4/quality/composite_doctrine_secular_lint.py",
        "role": "imports registry_resolver._parse_canonical_txt",
    },
    {
        "path": "scripts/qa/assemble_ch1_12shape_preview_v4.py",
        "role": "imports registry_resolver._parse_canonical_txt",
    },
    {
        "path": "phoenix_v4/planning/assembly_compiler.py::_parse_canonical_txt",
        "role": "strict STORY metadata parser (separate contract; path/band)",
    },
    {
        "path": "phoenix_v4/quality/base.py::parse_canonical_blocks",
        "role": "quality lint two-delimiter block parser",
    },
    {
        "path": "phoenix_v4/rendering/prose_resolver.py::_parse_canonical_with_prose",
        "role": "render-time STORY prose map",
    },
    {
        "path": "scripts/localization/run_translation_loop.py::parse_canonical",
        "role": "translation loop variant splitter",
    },
    {
        "path": "scripts/ci/check_canonical_atom_parse_sweep.py",
        "role": "CI sweep via assembly_compiler strict parser (STORY over-match)",
    },
]


def _count_headers(text: str) -> int:
    n = 0
    lines = text.splitlines()
    for i, line in enumerate(lines):
        s = line.strip()
        if _HEADER_RE.match(s):
            n += 1
            continue
        if _BARE_HEADER_RE.match(s):
            tok = _BARE_HEADER_RE.match(s).group(1)  # type: ignore[union-attr]
            if tok in _BARE_TOKENS:
                nxt = ""
                for j in range(i + 1, len(lines)):
                    if lines[j].strip():
                        nxt = lines[j].strip()
                        break
                if nxt == "---":
                    n += 1
    return n


def _iter_git_canonical(slots: Iterable[str]) -> list[tuple[str, str]]:
    """List (path, blob_oid) for atoms/**/<SLOT>/CANONICAL.txt from HEAD."""
    out = subprocess.check_output(
        ["git", "ls-tree", "-r", "HEAD"],
        cwd=REPO_ROOT,
        text=True,
    )
    slot_set = {s.upper() for s in slots}
    rows: list[tuple[str, str]] = []
    for line in out.splitlines():
        # <mode> <type> <oid>\t<path>
        try:
            meta, path = line.split("\t", 1)
        except ValueError:
            continue
        parts_meta = meta.split()
        if len(parts_meta) < 3 or parts_meta[1] != "blob":
            continue
        oid = parts_meta[2]
        if not path.startswith("atoms/") or not path.endswith("/CANONICAL.txt"):
            continue
        parts = Path(path).parts
        # atoms/persona/topic/SLOT/CANONICAL.txt
        # atoms/persona/topic/SLOT/locales/loc/CANONICAL.txt
        if len(parts) >= 5 and parts[3].upper() in slot_set:
            rows.append((path, oid))
        elif (
            len(parts) >= 7
            and parts[3].upper() in slot_set
            and parts[4] == "locales"
        ):
            rows.append((path, oid))
    return sorted(rows, key=lambda x: x[0])


def _batch_read_blobs(path_oids: list[tuple[str, str]]) -> dict[str, str]:
    """Read many blobs via ``git cat-file --batch`` (fast path when atoms absent on disk)."""
    if not path_oids:
        return {}
    texts: dict[str, str] = {}
    missing: list[tuple[str, str]] = []
    for rel, oid in path_oids:
        disk = REPO_ROOT / rel
        if disk.exists():
            texts[rel] = disk.read_text(encoding="utf-8")
        else:
            missing.append((rel, oid))
    if not missing:
        return texts

    # Interleave request/response to avoid stdout pipe deadlock on large batches.
    proc = subprocess.Popen(
        ["git", "cat-file", "--batch"],
        cwd=REPO_ROOT,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    assert proc.stdin is not None and proc.stdout is not None
    try:
        for rel, oid in missing:
            proc.stdin.write(f"{oid}\n".encode("utf-8"))
            proc.stdin.flush()
            header = proc.stdout.readline().decode("utf-8", errors="replace")
            if not header or " missing" in header:
                texts[rel] = ""
                continue
            try:
                size = int(header.strip().split()[-1])
            except (IndexError, ValueError):
                texts[rel] = ""
                continue
            data = proc.stdout.read(size)
            proc.stdout.read(1)  # trailing newline after blob
            texts[rel] = data.decode("utf-8", errors="replace")
    finally:
        try:
            proc.stdin.close()
        except Exception:
            pass
        proc.wait(timeout=60)
    return texts


def _slot_from_rel(rel: str) -> str:
    parts = Path(rel).parts
    if len(parts) >= 4:
        return parts[3].upper()
    return ""


def audit_file(rel: str, text: str, parse) -> dict[str, Any]:
    row: dict[str, Any] = {
        "path": rel,
        "slot": _slot_from_rel(rel),
        "header_count": 0,
        "usable_atom_count": 0,
        "delimiter_shapes": [],
        "silent_zero_risk": False,
        "parse_error": None,
    }
    if text is None:
        row["parse_error"] = "read_failed: missing blob"
        return row

    row["header_count"] = _count_headers(text)
    try:
        atoms = parse(Path(rel), slot_type=row["slot"] or None, text=text)
    except Exception as exc:  # noqa: BLE001 — surface fail-loud path
        row["parse_error"] = f"{type(exc).__name__}: {exc}"
        # Headers with a hard parse error are the loud path — not silent.
        row["silent_zero_risk"] = False
        return row

    row["usable_atom_count"] = len(atoms)
    shapes = [a.get("delimiter_shape") for a in atoms if isinstance(a, dict)]
    row["delimiter_shapes"] = sorted({s for s in shapes if s})
    # Pre-fix failure mode: headers present, zero usable, no exception.
    row["silent_zero_risk"] = row["header_count"] > 0 and row["usable_atom_count"] == 0
    return row


def run_audit(
    *,
    slots: Optional[list[str]] = None,
    include_all_persona_slots: bool = True,
) -> dict[str, Any]:
    sys.path.insert(0, str(REPO_ROOT))
    from phoenix_v4.planning.registry_resolver import (  # noqa: WPS433
        CanonicalParseError,
        _parse_canonical_txt,
    )

    primary = list(PRIMARY_SLOTS)
    if slots:
        chosen = [s.upper() for s in slots]
    elif include_all_persona_slots:
        chosen = sorted(PERSONA_SLOT_DIRS)
    else:
        chosen = primary

    # Always ensure REFLECTION is included.
    if "REFLECTION" not in chosen:
        chosen = ["REFLECTION", *chosen]

    path_oids = _iter_git_canonical(chosen)
    texts = _batch_read_blobs(path_oids)
    rows = [
        audit_file(rel, texts.get(rel, ""), _parse_canonical_txt)
        for rel, _oid in path_oids
    ]

    silent = [r for r in rows if r.get("silent_zero_risk")]
    errors = [r for r in rows if r.get("parse_error")]
    header_gt_usable = [
        r for r in rows
        if r["header_count"] > r["usable_atom_count"] and not r.get("parse_error")
    ]
    by_slot: dict[str, dict[str, int]] = {}
    shape_counter: Counter[str] = Counter()
    for r in rows:
        slot = r["slot"] or "?"
        bucket = by_slot.setdefault(
            slot,
            {"files": 0, "headers": 0, "usable": 0, "errors": 0, "silent_zero": 0},
        )
        bucket["files"] += 1
        bucket["headers"] += int(r["header_count"])
        bucket["usable"] += int(r["usable_atom_count"])
        if r.get("parse_error"):
            bucket["errors"] += 1
        if r.get("silent_zero_risk"):
            bucket["silent_zero"] += 1
        for s in r.get("delimiter_shapes") or []:
            shape_counter[s] += 1

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "parser": "phoenix_v4.planning.registry_resolver._parse_canonical_txt",
        "canonical_parse_error_type": CanonicalParseError.__name__,
        "slots_scanned": chosen,
        "primary_slots": list(PRIMARY_SLOTS),
        "consumer_paths": CONSUMER_PATHS,
        "totals": {
            "files": len(rows),
            "headers": sum(r["header_count"] for r in rows),
            "usable_atoms": sum(r["usable_atom_count"] for r in rows),
            "parse_errors": len(errors),
            "silent_zero_risk": len(silent),
            "header_gt_usable_ok_files": len(header_gt_usable),
        },
        "delimiter_shape_counts": dict(shape_counter),
        "by_slot": by_slot,
        "silent_zero_files": [r["path"] for r in silent],
        "parse_error_files": [
            {"path": r["path"], "error": r["parse_error"]} for r in errors[:200]
        ],
        "sample_rows": rows[:50],
        "all_rows": rows,
        "acceptance": {
            "silent_zero_impossible_when_parser_raises": True,
            "note": (
                "Post-fix parser raises CanonicalParseError on header-present "
                "empty-prose blocks; silent_zero_risk must be 0 for scanned files."
            ),
        },
    }


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true", help="Print full JSON report")
    ap.add_argument(
        "--write-artifact",
        action="store_true",
        help=f"Write report to {DEFAULT_ARTIFACT}",
    )
    ap.add_argument(
        "--artifact-path",
        type=Path,
        default=DEFAULT_ARTIFACT,
        help="Artifact output path",
    )
    ap.add_argument(
        "--slots",
        nargs="*",
        default=None,
        help="Slot names to scan (default: all persona slot dirs + REFLECTION)",
    )
    ap.add_argument(
        "--reflection-only",
        action="store_true",
        help="Scan only atoms/**/REFLECTION/CANONICAL.txt",
    )
    args = ap.parse_args(argv)

    report = run_audit(
        slots=(["REFLECTION"] if args.reflection_only else args.slots),
        include_all_persona_slots=not args.reflection_only and args.slots is None,
    )

    # Compact summary view omits all_rows unless --json / artifact.
    summary = {k: v for k, v in report.items() if k != "all_rows"}
    summary["parse_error_files"] = report["parse_error_files"][:20]

    if args.write_artifact:
        path: Path = args.artifact_path
        out_dir = path.parent
        out_dir.mkdir(parents=True, exist_ok=True)

        # Repo-compliant artifacts only (no multi-MB all_rows blob).
        # Full rows remain available in-memory / via --json for local use.
        summary = {k: v for k, v in report.items() if k != "all_rows"}
        pe = list(summary.pop("parse_error_files", []) or [])
        summary["parse_error_files_count"] = len(pe)
        summary["parse_error_files_sample"] = pe[:50]
        summary_path = out_dir / "SUMMARY.json"
        summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

        jsonl_path = out_dir / "PARSE_ERRORS.jsonl"
        with jsonl_path.open("w", encoding="utf-8") as fh:
            for row in pe:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")

        # Legacy REPORT.json path: write SUMMARY payload only if caller asked for
        # REPORT.json — never dump all_rows into the repo.
        if path.name.upper() == "REPORT.JSON":
            # Do not create REPORT.json (blob-policy / size). Prefer SUMMARY.json.
            if path.exists():
                path.unlink()
        else:
            path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

        md_path = out_dir / "REPORT.md"
        totals = report["totals"]
        md = [
            "# CANONICAL parse-depth audit",
            "",
            f"Generated: `{report['generated_at']}`",
            f"Parser: `{report['parser']}`",
            "",
            "## Totals",
            "",
            f"- files: **{totals['files']}**",
            f"- headers: **{totals['headers']}**",
            f"- usable atoms: **{totals['usable_atoms']}**",
            f"- parse errors (loud): **{totals['parse_errors']}**",
            f"- silent zero-atom risk: **{totals['silent_zero_risk']}**",
            "",
            "## Delimiter shapes",
            "",
        ]
        for shape, n in sorted(report["delimiter_shape_counts"].items()):
            md.append(f"- `{shape}`: {n}")
        md.extend(["", "## Consumers audited", ""])
        for c in CONSUMER_PATHS:
            md.append(f"- `{c['path']}` — {c['role']}")
        md.extend(["", "## By slot", ""])
        for slot, b in sorted(report["by_slot"].items()):
            md.append(
                f"- **{slot}**: files={b['files']} headers={b['headers']} "
                f"usable={b['usable']} errors={b['errors']} silent_zero={b['silent_zero']}"
            )
        md.extend([
            "",
            "## Acceptance",
            "",
            report["acceptance"]["note"],
            "",
            f"silent_zero_files: {report['silent_zero_files'][:20]}",
            "",
            "## Artifacts",
            "",
            "- `SUMMARY.json` — totals / by_slot / acceptance (repo-compliant)",
            "- `PARSE_ERRORS.jsonl` — one JSON object per failing file",
            "- Full per-file rows regenerable locally; not committed (blob policy).",
            "",
        ])
        md_path.write_text("\n".join(md) + "\n", encoding="utf-8")
        print(f"[parse-depth] wrote {summary_path}")
        print(f"[parse-depth] wrote {jsonl_path}")
        print(f"[parse-depth] wrote {md_path}")

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        t = report["totals"]
        print(f"[parse-depth] files={t['files']} headers={t['headers']} "
              f"usable={t['usable_atoms']} errors={t['parse_errors']} "
              f"silent_zero={t['silent_zero_risk']}")
        print(f"[parse-depth] shapes={report['delimiter_shape_counts']}")
        if t["silent_zero_risk"]:
            print("[parse-depth] FAIL silent zero-atom drops still possible:")
            for p in report["silent_zero_files"][:20]:
                print(f"    {p}")
            return 1
        print("[parse-depth] OK — no silent header→zero-atom drops in scanned set")
    return 1 if report["totals"]["silent_zero_risk"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
