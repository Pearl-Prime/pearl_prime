#!/usr/bin/env python3
"""Repair corrupted block headers in atoms/*/*/*/CANONICAL.txt (DEFECT 7, content lane).

CONTEXT
-------
546/3,521 primary ``atoms/*/*/*/CANONICAL.txt`` banks (full-tree 1,619/16,292)
ship MALFORMED block headers: every even-numbered block lost its ``## `` prefix.
``phoenix_v4/planning/registry_resolver.py::_parse_canonical_txt`` historically
treated only ``## ``-prefixed lines as block headers, so a bare ``INTEGRATION v06``
line is absorbed into the PRIOR atom's body and leaks verbatim into reader prose
as a standalone line — driving the register-gate F2 HARD_FAIL on 9/9 pilot books
(spec: COMPOSER_FRONTIER_FIX_SPEC_20260614.md, DEFECT 7, the single most
universal blocker).

This is the CONTENT lane (the unblocker, no source-code change): repair the
source files by prepending ``## `` to every malformed block header. A companion
COMPOSER-GUARD lane hardens the parser as a fail-closed backstop; the two are
complementary — this script fixes the data at rest, the guard catches any
un-repaired file at runtime.

REPAIR RULE (copied VERBATIM from the fix-spec, DEFECT 7 "Fix" lane (1))
-----------------------------------------------------------------------
Prepend ``## `` to every line matching::

    ^(HOOK|SCENE|STORY|REFLECTION|PIVOT|EXERCISE|INTEGRATION|THREAD|TAKEAWAY|PERMISSION|COMPRESSION|RECOGNITION|MECHANISM_PROOF|TURNING_POINT|EMBODIMENT|COST_REVEAL|RECKONING)\s+v\d+\s*$

whose **next non-empty line is** ``---``.

Two guards make this safe and idempotent:
  * a line already starting with ``## `` is NEVER touched (no double-prefix);
  * the next-non-empty-line==``---`` guard ensures a grammatical mid-atom phrase
    (which is never followed by a lone ``---``) is never mistaken for a header.

EXCLUSION
---------
``atoms/gen_z_professionals/financial_anxiety/EXERCISE/CANONICAL.txt`` is owned by
a separate lane (the EXERCISE-bank authoring lane) and is skipped here.

USAGE
-----
    python3 scripts/fix/repair_atom_canonical_headers.py --dry-run
    python3 scripts/fix/repair_atom_canonical_headers.py --apply

``--dry-run`` (the default) prints the count of files + lines that would change
and emits no writes. ``--apply`` rewrites the affected files in place and writes
the full list of repaired paths to
``artifacts/pearl_prime/fix_wave_rebuild_20260614/laneD_repaired_files.txt``.

By default the script scans the FULL tree (``atoms/**/CANONICAL.txt``), which
includes ``locales/<locale>/CANONICAL.txt`` variants — these carry the same
structural ``<TOKEN> vNN`` header corruption (the header token is English/
structural even in localized atoms) and feed the same parser, so they leak the
same raw labels into CJK prose and must be repaired too. Pass ``--primary-only``
to restrict to the 3-level primary banks.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Repo root = two levels up from scripts/fix/.
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ATOMS_ROOT = REPO_ROOT / "atoms"

# Owned by a separate lane (EXERCISE-bank authoring) — never touch here.
EXCLUDE_PATH = (
    ATOMS_ROOT
    / "gen_z_professionals"
    / "financial_anxiety"
    / "EXERCISE"
    / "CANONICAL.txt"
).resolve()

REPAIRED_LIST_PATH = (
    REPO_ROOT
    / "artifacts"
    / "pearl_prime"
    / "fix_wave_rebuild_20260614"
    / "laneD_repaired_files.txt"
)

# --- EXACT header-token alternation + regex, copied VERBATIM from the fix-spec
#     (COMPOSER_FRONTIER_FIX_SPEC_20260614.md, DEFECT 7, Fix lane (1)). ---
_HEADER_TOKENS = (
    "HOOK|SCENE|STORY|REFLECTION|PIVOT|EXERCISE|INTEGRATION|THREAD|TAKEAWAY|"
    "PERMISSION|COMPRESSION|RECOGNITION|MECHANISM_PROOF|TURNING_POINT|"
    "EMBODIMENT|COST_REVEAL|RECKONING"
)
HEADER_RE = re.compile(rf"^({_HEADER_TOKENS})\s+v\d+\s*$")


def _next_nonempty(lines: list[str], idx: int) -> str:
    """Return the next non-empty line after ``idx``, stripped (``""`` if none)."""
    for j in range(idx + 1, len(lines)):
        if lines[j].strip():
            return lines[j].strip()
    return ""


def repair_text(text: str) -> tuple[str, int]:
    """Return (repaired_text, num_lines_fixed) for one CANONICAL.txt body.

    Splitlines/join preserves the original line content exactly except for the
    ``## `` prefix prepended to each malformed header. The trailing-newline of
    the source is preserved.
    """
    # Preserve a trailing newline if the source had one.
    had_trailing_nl = text.endswith("\n")
    lines = text.splitlines()
    out: list[str] = []
    fixed = 0
    for i, line in enumerate(lines):
        # Never double-prefix an already-correct header.
        if line.startswith("## "):
            out.append(line)
            continue
        stripped = line.strip()
        if HEADER_RE.match(stripped) and _next_nonempty(lines, i) == "---":
            # Prepend the canonical "## " marker to the (stripped) header token.
            out.append(f"## {stripped}")
            fixed += 1
        else:
            out.append(line)
    repaired = "\n".join(out)
    if had_trailing_nl:
        repaired += "\n"
    return repaired, fixed


def iter_target_files(primary_only: bool) -> list[Path]:
    if primary_only:
        files = sorted(ATOMS_ROOT.glob("*/*/*/CANONICAL.txt"))
    else:
        files = sorted(ATOMS_ROOT.rglob("CANONICAL.txt"))
    return [f for f in files if f.resolve() != EXCLUDE_PATH]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would change without writing (default).",
    )
    mode.add_argument(
        "--apply",
        action="store_true",
        help="Rewrite affected files in place and emit the repaired-file list.",
    )
    parser.add_argument(
        "--primary-only",
        action="store_true",
        help="Restrict to the 3-level primary banks (atoms/*/*/*/CANONICAL.txt).",
    )
    args = parser.parse_args(argv)

    apply = bool(args.apply)  # default (neither flag) => dry-run
    files = iter_target_files(args.primary_only)

    changed_files: list[Path] = []
    total_lines = 0
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:  # pragma: no cover - defensive
            print(f"  SKIP (unreadable): {path} ({exc})", file=sys.stderr)
            continue
        repaired, fixed = repair_text(text)
        if fixed == 0:
            continue
        changed_files.append(path)
        total_lines += fixed
        if apply:
            path.write_text(repaired, encoding="utf-8")

    scope = "primary (3-level)" if args.primary_only else "full tree"
    mode_label = "APPLIED" if apply else "DRY-RUN"
    print(f"[repair_atom_canonical_headers] mode={mode_label} scope={scope}")
    print(f"  files scanned: {len(files)}")
    print(f"  files {'repaired' if apply else 'that would change'}: {len(changed_files)}")
    print(f"  header lines {'fixed' if apply else 'that would change'}: {total_lines}")

    if apply:
        REPAIRED_LIST_PATH.parent.mkdir(parents=True, exist_ok=True)
        rel_paths = sorted(
            str(p.relative_to(REPO_ROOT)) for p in changed_files
        )
        REPAIRED_LIST_PATH.write_text(
            "\n".join(rel_paths) + ("\n" if rel_paths else ""),
            encoding="utf-8",
        )
        print(f"  repaired-file list -> {REPAIRED_LIST_PATH.relative_to(REPO_ROOT)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
