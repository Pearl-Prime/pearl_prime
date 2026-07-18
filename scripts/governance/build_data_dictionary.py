#!/usr/bin/env python3
"""Build the enforced repo data dictionary — docs/DATA_DICTIONARY.tsv.

The data dictionary is the SSOT map of "what every significant file/bank IS,
which subsystem owns it, who consumes it, and whether it is wired". It is the
substrate the enforcement gate (scripts/ci/check_data_dictionary.py) reads: a
file that is not in the dictionary, or is documented but reachable by nothing,
is a drift signal.

This builder walks the FULL repo (not just docs/): the seed roots below are the
high-value surfaces where silent orphans and unwired knobs actually hurt —
atom banks, source-of-truth banks, the code that consumes them, config, and CI.
It classifies each entry by directory-derived subsystem, resolves a coarse
consumer set by string-reachability (same idiom as check_manga_wiring.py — a
"consumer" is a non-test .py under scripts/ or phoenix_v4/ whose text references
the entry's stem/relpath), and emits a stable, sorted TSV.

Columns (tab-separated):
    path       repo-relative path (a file, or a bank directory)
    purpose    one-line human purpose (heuristic from location + name)
    subsystem  coarse subsystem bucket (doctrine_bank / exercise_bank / atoms /
               composer / planning / ci / config / workflow / docs / script)
    owner      owning agent/role (heuristic; edit in place when known)
    consumers  ";"-joined non-test consumer relpaths (or "-" if none found)
    status     WIRED | KNOWN_UNWIRED | UNWIRED | REFERENCE

Deterministic: same tree in → same TSV out (stable sort, no timestamps in body).

Run:
    PYTHONPATH=. python3 scripts/governance/build_data_dictionary.py
    PYTHONPATH=. python3 scripts/governance/build_data_dictionary.py --check
        (exit 1 if docs/DATA_DICTIONARY.tsv is stale vs a fresh build)

Exit: 0 wrote (or up-to-date under --check); 1 stale under --check; 2 usage.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]

OUT_REL = "docs/DATA_DICTIONARY.tsv"
HEADER = ("path", "purpose", "subsystem", "owner", "consumers", "status")

# Non-test consumer code roots (mirrors check_manga_wiring.py idiom).
CONSUMER_ROOTS = ("scripts", "phoenix_v4")

# ---------------------------------------------------------------------------
# Seed KNOWN_UNWIRED — banks/bodies that exist on origin/main but are consumed
# by no production selector yet. Each key is a repo-relative path (a bank dir or
# a file); value is the reason. These are the honest "declared-unwired" entries
# the gate expects. To wire one: add a real consumer, then move it out of here.
#
# Per mission seed (2026-07-06):
#   - the composite-doctrine REFLECTION banks (secular doctrine, only anxiety is
#     block-populated today; the rest are structural placeholders)
#   - the 11 exercises_v4/approved bodies (five-layer library is the wired one;
#     these flat approved bodies are the OLD lane — see memory: exercise five-layer rule)
# ---------------------------------------------------------------------------
KNOWN_UNWIRED: dict[str, str] = {}

_DOCTRINE_ROOT = "SOURCE_OF_TRUTH/composite_doctrine"
_EXERCISE_ROOT = "SOURCE_OF_TRUTH/exercises_v4/approved"

# doctrine banks: one KNOWN_UNWIRED entry per <topic>/REFLECTION bank dir.
_DOCTRINE_UNWIRED_REASON = (
    "composite-doctrine REFLECTION bank — secular doctrine placeholder; only "
    "anxiety is block-populated + composer-reachable today (memory: composite "
    "doctrine banks empty). Wire = shared secular section_06 per topic."
)
_EXERCISE_UNWIRED_REASON = (
    "exercises_v4/approved flat body — OLD lane; the WIRED library is the "
    "five-layer library_34 (memory: exercise five-layer rule). Do not 'wire the 11'."
)

# Knobs/paths recorded as WIRED (override string-reachability, positive assert).
# doctrine_rotation landed on main in commit 61e156e7ace5787de51f586f276041f2413f3ddb
# (squash-merge of PR #4672; one doctrine per chapter).
KNOWN_WIRED: dict[str, str] = {
    "config/source_of_truth/doctrine_rotation.yaml":
        "doctrine rotation knob — WIRED 61e156e7ace5787de51f586f276041f2413f3ddb "
        "(enrichment_select + doctrine_rotation.py consume it: one doctrine/chapter, no repeats).",
    "phoenix_v4/planning/doctrine_rotation.py":
        "doctrine rotation engine — WIRED 61e156e7ace5787de51f586f276041f2413f3ddb.",
}


def _is_test_path(p: Path) -> bool:
    parts = {seg.lower() for seg in p.parts}
    return "tests" in parts or p.name.startswith("test_")


def build_consumer_index(repo_root: Path) -> str:
    """One lowercased blob of all non-test consumer .py text (string-reachability)."""
    blobs: list[str] = []
    for root in CONSUMER_ROOTS:
        base = repo_root / root
        if not base.is_dir():
            continue
        for py in base.rglob("*.py"):
            if _is_test_path(py):
                continue
            try:
                blobs.append(py.read_text(errors="ignore"))
            except OSError:
                continue
    return "\n".join(blobs).lower()


def _consumers_for(stem_or_rel: str, repo_root: Path) -> list[str]:
    """Non-test consumer relpaths whose text references the token. Bounded scan."""
    token = stem_or_rel.lower()
    hits: list[str] = []
    for root in CONSUMER_ROOTS:
        base = repo_root / root
        if not base.is_dir():
            continue
        for py in base.rglob("*.py"):
            if _is_test_path(py):
                continue
            try:
                if token in py.read_text(errors="ignore").lower():
                    hits.append(str(py.relative_to(repo_root)))
            except OSError:
                continue
    return sorted(hits)


def _subsystem_for(rel: str) -> str:
    if rel.startswith(_DOCTRINE_ROOT):
        return "doctrine_bank"
    if rel.startswith(_EXERCISE_ROOT):
        return "exercise_bank"
    if rel.startswith("SOURCE_OF_TRUTH/atoms") or "/atoms/" in rel:
        return "atoms"
    if rel.startswith("phoenix_v4/rendering") or "composer" in rel:
        return "composer"
    if rel.startswith("phoenix_v4/planning") or rel.startswith("phoenix_v4/qa"):
        return "planning"
    if rel.startswith("scripts/ci"):
        return "ci"
    if rel.startswith(".github/workflows"):
        return "workflow"
    if rel.startswith("config"):
        return "config"
    if rel.startswith("docs"):
        return "docs"
    if rel.startswith("scripts"):
        return "script"
    return "other"


def _purpose_for(rel: str, subsystem: str) -> str:
    name = Path(rel).name
    if subsystem == "doctrine_bank":
        topic = rel.split("/")[2] if len(rel.split("/")) > 2 else name
        return f"composite-doctrine REFLECTION bank ({topic})"
    if subsystem == "exercise_bank":
        return f"approved five-layer-lane exercise body ({name})"
    if subsystem == "ci":
        return f"CI drift/readiness gate ({name})"
    if subsystem == "workflow":
        return f"GitHub Actions workflow ({name})"
    return f"{subsystem} entry ({name})"


def _owner_for(subsystem: str) -> str:
    return {
        "doctrine_bank": "Pearl_Editor",
        "exercise_bank": "Pearl_Editor",
        "atoms": "Pearl_Writer",
        "composer": "Pearl_Prime",
        "planning": "Pearl_Prime",
        "ci": "Pearl_GitHub",
        "workflow": "Pearl_GitHub",
        "config": "Pearl_Architect",
        "docs": "Pearl_PM",
        "script": "Pearl_Dev",
    }.get(subsystem, "Pearl_PM")


def _doctrine_bank_dirs(repo_root: Path) -> list[str]:
    base = repo_root / _DOCTRINE_ROOT
    if not base.is_dir():
        return []
    out: list[str] = []
    for topic in sorted(base.iterdir()):
        if not topic.is_dir():
            continue
        refl = topic / "REFLECTION"
        if refl.is_dir():
            out.append(str(refl.relative_to(repo_root)))
    return out


def _exercise_bodies(repo_root: Path) -> list[str]:
    base = repo_root / _EXERCISE_ROOT
    if not base.is_dir():
        return []
    return sorted(str(p.relative_to(repo_root)) for p in base.glob("*.yaml"))


def _ci_gates(repo_root: Path) -> list[str]:
    base = repo_root / "scripts" / "ci"
    if not base.is_dir():
        return []
    return sorted(str(p.relative_to(repo_root)) for p in base.glob("check_*.py"))


def _workflows(repo_root: Path) -> list[str]:
    base = repo_root / ".github" / "workflows"
    if not base.is_dir():
        return []
    return sorted(str(p.relative_to(repo_root)) for p in base.glob("*.yml"))


def build_rows(repo_root: Path) -> list[tuple[str, str, str, str, str, str]]:
    rows: list[tuple[str, ...]] = []

    # 1. doctrine banks (KNOWN_UNWIRED seed)
    for rel in _doctrine_bank_dirs(repo_root):
        KNOWN_UNWIRED.setdefault(rel, _DOCTRINE_UNWIRED_REASON)

    # 2. exercise bodies (KNOWN_UNWIRED seed)
    for rel in _exercise_bodies(repo_root):
        KNOWN_UNWIRED.setdefault(rel, _EXERCISE_UNWIRED_REASON)

    entries: list[str] = []
    entries += _doctrine_bank_dirs(repo_root)
    entries += _exercise_bodies(repo_root)
    entries += _ci_gates(repo_root)
    entries += _workflows(repo_root)
    entries += [rel for rel in KNOWN_WIRED if (repo_root / rel).exists()]

    seen: set[str] = set()
    for rel in entries:
        if rel in seen:
            continue
        seen.add(rel)
        subsystem = _subsystem_for(rel)
        purpose = _purpose_for(rel, subsystem)
        owner = _owner_for(subsystem)

        stem = Path(rel).stem
        if rel in KNOWN_WIRED:
            status = "WIRED"
            consumers = ";".join(_consumers_for(stem, repo_root)) or "self"
        elif rel in KNOWN_UNWIRED:
            status = "KNOWN_UNWIRED"
            consumers = "-"
        elif subsystem in ("ci", "workflow"):
            # gates/workflows are infra; they are "wired" by the workflow that runs them
            status = "WIRED"
            consumers = ".github/workflows"
        else:
            found = _consumers_for(stem, repo_root)
            if found:
                status = "WIRED"
                consumers = ";".join(found)
            else:
                status = "UNWIRED"
                consumers = "-"
        rows.append((rel, purpose, subsystem, owner, consumers, status))

    rows.sort(key=lambda r: (r[2], r[0]))
    return rows  # type: ignore[return-value]


def render_tsv(rows: list[tuple[str, str, str, str, str, str]]) -> str:
    lines = ["\t".join(HEADER)]
    for row in rows:
        lines.append("\t".join(row))
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Build the enforced repo data dictionary.")
    ap.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    ap.add_argument("--out", default=OUT_REL, help=f"output relpath (default {OUT_REL})")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if the on-disk dictionary differs from a fresh build")
    args = ap.parse_args(argv)
    repo_root: Path = args.repo_root

    rows = build_rows(repo_root)
    fresh = render_tsv(rows)
    out_path = repo_root / args.out

    if args.check:
        current = out_path.read_text() if out_path.exists() else ""
        if current == fresh:
            print(f"DATA DICTIONARY: up-to-date ({len(rows)} entries)", file=sys.stderr)
            return 0
        print(f"DATA DICTIONARY: STALE — rebuild with "
              f"scripts/governance/build_data_dictionary.py", file=sys.stderr)
        return 1

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(fresh)
    n_unwired = sum(1 for r in rows if r[5] == "KNOWN_UNWIRED")
    n_wired = sum(1 for r in rows if r[5] == "WIRED")
    n_orphan = sum(1 for r in rows if r[5] == "UNWIRED")
    print(f"DATA DICTIONARY: wrote {args.out} — {len(rows)} entries "
          f"({n_wired} wired, {n_unwired} known-unwired, {n_orphan} orphan)",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
