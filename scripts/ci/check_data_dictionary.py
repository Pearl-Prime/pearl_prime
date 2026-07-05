#!/usr/bin/env python3
"""Drift detector: the enforced data dictionary (docs/DATA_DICTIONARY.tsv).

The undocumented-file / silent-orphan / unwired-knob kill. Prior sessions
shipped banks, knobs, and configs that existed but were reachable by no
selector, then reported the feature as working (the whole "memory is recall,
not enforcement" doctrine). This gate makes the data dictionary the SSOT and
FAILS on the drift classes below, so a silent orphan or an unwired spec-knob
cannot merge undocumented.

FAIL conditions (each a separate, named violation):
  1. STALE            docs/DATA_DICTIONARY.tsv differs from a fresh
                      build_data_dictionary.py run (someone added/removed a bank
                      or gate without regenerating — the dictionary is lying).
  2. UNWIRED-ORPHAN   a dictionary row with status=UNWIRED (a file reachable by
                      no non-test consumer) that is NOT declared KNOWN_UNWIRED.
                      Fix: wire it (add a consumer) or move it to KNOWN_UNWIRED
                      with a reason in build_data_dictionary.py.
  3. ATOM-UNREACHABLE an atom bank present on disk under a scanned atoms root
                      that no selector references (bank exists, selector-blind).
  4. BYPASS           a book-assembly entrypoint (scripts/run_pipeline.py or a
                      phoenix_v4 assembler) that does NOT reference BOTH
                      chapter_planner AND book_pass_gate — a path that assembles
                      a book while bypassing the plan/gate stack.

Cascade-block semantics: this gate is a hard blocker. A dependent NEXT-5 lane
that declares "done" while this is red is declaring done on an undocumented /
orphaned surface — the readiness runner (gate 27) treats a red here as a hard
failure so no dependent lane can green over it.

Allowlist: a same-or-preceding-line comment on an assembly invocation
  # CI-ALLOWLIST: data-dictionary-ok — <reason>
exempts that block from the BYPASS check (e.g. a smoke harness that legitimately
does not run the plan stack). Do NOT weaken the gate to pass a real bypass.

Run:
    PYTHONPATH=scripts/ci:. python3 scripts/ci/check_data_dictionary.py

Exit: 0 pass; 1 any violation.
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drift_detector_git import repo_root_from_script  # noqa: E402

# import the builder so the gate and the builder never diverge
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.governance import build_data_dictionary as ddict  # noqa: E402

REPO_ROOT = repo_root_from_script(Path(__file__))
DICT_REL = ddict.OUT_REL

# atom bank roots scanned for selector-reachability (bank exists but no selector)
ATOM_BANK_ROOTS = ("SOURCE_OF_TRUTH/atoms", "atoms")
# an assembler that emits a book must reference BOTH of these stacks
ASSEMBLY_ENTRYPOINTS = (
    "scripts/run_pipeline.py",
    "phoenix_v4/planning/assembly_compiler.py",
)
REQUIRED_PLAN_STACK = ("chapter_planner", "book_pass_gate")
BYPASS_ALLOWLIST = "CI-ALLOWLIST: data-dictionary-ok"


@dataclass
class Violation:
    kind: str
    detail: str


def _check_stale(repo_root: Path) -> list[Violation]:
    rows = ddict.build_rows(repo_root)
    fresh = ddict.render_tsv(rows)
    path = repo_root / DICT_REL
    current = path.read_text() if path.exists() else ""
    if current != fresh:
        return [Violation("STALE",
                          f"{DICT_REL} differs from a fresh build — run "
                          f"scripts/governance/build_data_dictionary.py and commit")]
    return []


def _parse_dict(repo_root: Path) -> list[dict[str, str]]:
    path = repo_root / DICT_REL
    if not path.exists():
        return []
    lines = path.read_text().splitlines()
    if not lines:
        return []
    header = lines[0].split("\t")
    out: list[dict[str, str]] = []
    for line in lines[1:]:
        if not line.strip():
            continue
        cols = line.split("\t")
        out.append(dict(zip(header, cols)))
    return out


def _check_orphans(rows: list[dict[str, str]]) -> list[Violation]:
    v: list[Violation] = []
    for r in rows:
        if r.get("status") == "UNWIRED":
            v.append(Violation("UNWIRED-ORPHAN",
                               f"{r.get('path')}: reachable by no non-test consumer and "
                               f"not declared KNOWN_UNWIRED — wire it or declare it"))
    return v


def _check_atom_reachability(repo_root: Path) -> list[Violation]:
    """Every atom bank dir under a scanned root must be referenced by some selector.

    'Selector' = the same non-test consumer blob the builder uses. A bank dir
    whose name/relpath appears nowhere in consumer code is selector-blind.
    """
    index = ddict.build_consumer_index(repo_root)
    v: list[Violation] = []
    for root in ATOM_BANK_ROOTS:
        base = repo_root / root
        if not base.is_dir():
            continue
        for bank in sorted(p for p in base.iterdir() if p.is_dir()):
            rel = str(bank.relative_to(repo_root))
            stem = bank.name.lower()
            if stem in index or rel.lower() in index:
                continue
            v.append(Violation("ATOM-UNREACHABLE",
                               f"{rel}: atom bank present but referenced by no selector "
                               f"(selector-blind)"))
    return v


def _block_is_allowlisted(lines: list[str], idx: int) -> bool:
    for j in range(max(0, idx - 2), idx + 1):
        if j < len(lines) and BYPASS_ALLOWLIST in lines[j]:
            return True
    return False


def _check_bypass(repo_root: Path) -> list[Violation]:
    """Book-assembly entrypoints must reference BOTH chapter_planner and book_pass_gate."""
    v: list[Violation] = []
    for rel in ASSEMBLY_ENTRYPOINTS:
        path = repo_root / rel
        if not path.is_file():
            continue
        try:
            text = path.read_text(errors="ignore")
        except OSError:
            continue
        if BYPASS_ALLOWLIST in text:
            continue
        low = text.lower()
        missing = [s for s in REQUIRED_PLAN_STACK if s not in low]
        if missing:
            v.append(Violation("BYPASS",
                               f"{rel}: book-assembly entrypoint does not reference "
                               f"{', '.join(missing)} — assembles while bypassing the "
                               f"plan/gate stack (add the reference or a "
                               f"# CI-ALLOWLIST: data-dictionary-ok comment with a reason)"))
    return v


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Enforced data-dictionary gate")
    ap.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = ap.parse_args(argv)
    repo_root: Path = args.repo_root

    violations: list[Violation] = []
    violations += _check_stale(repo_root)
    rows = _parse_dict(repo_root)
    violations += _check_orphans(rows)
    violations += _check_atom_reachability(repo_root)
    violations += _check_bypass(repo_root)

    if not violations:
        print(f"DATA DICTIONARY GATE: PASS ({len(rows)} documented entries; no orphans, "
              f"no selector-blind atom banks, no plan-stack bypass)", file=sys.stderr)
        return 0
    for v in violations:
        print(f"FAIL[{v.kind}]: {v.detail}", file=sys.stderr)
    print(f"DATA DICTIONARY GATE: {len(violations)} violation(s) — blocking",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
