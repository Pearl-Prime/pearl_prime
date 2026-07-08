#!/usr/bin/env python3
"""No-lost-functions gate — the machine form of §18 "old functions survive new features".

Authority: docs/agent_brief.txt §18 ("inventory=REDUCED is forbidden without operator
ratification ... caught by the dictionary-diff gate — a WIRED row may not silently become
orphan/removed/unwired"). This is that dictionary-diff gate.

WHAT IT DOES
    1. Regenerates the data dictionary at the PR HEAD (ddict.build_rows — the SAME
       builder check_data_dictionary.py uses, so the two never diverge).
    2. Reads the COMMITTED data dictionary at the baseline ref (default origin/main).
    3. Diffs: any path that was `WIRED` at baseline and is now REMOVED (absent from the
       HEAD build) or ORPHANED (HEAD status UNWIRED / KNOWN_UNWIRED) is a capability
       REGRESSION.
    4. FAILS (exit 1) on any regression UNLESS the PR carries an explicit
       `CAPABILITY-RETIREMENT-RATIFIED: <OPD ref>` tag (PR body / commit body) — a
       deliberate, operator-ratified retirement. New features never bury old functions.

WHY A SIBLING SCRIPT (NEW-ARTIFACT-JUSTIFIED)
    check_data_dictionary.py is a pure INTERNAL-consistency gate over the current tree
    (staleness, orphans, selector-blind banks, plan-stack bypass). This gate is a
    BASELINE-vs-HEAD diff: it must read another git ref (origin/main's committed
    dictionary) and reason about TRANSITIONS between two dictionary states. That is a
    fundamentally different operation (cross-ref diff, needs git). Folding it into the
    consistency gate would muddy a single-purpose script. The two share the builder;
    they do not share concerns. Registered in the SAME CI surfaces as its sibling
    (drift-detectors.yml + run_production_readiness_gates.py) so it is a required check.

FAIL-OPEN (never a false red): if the baseline dictionary cannot be read (ref missing,
first commit, shallow clone without the file) the gate PASSES with a stderr WARNING —
a diff gate with no baseline is a no-op, not a block.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drift_detector_git import repo_root_from_script  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.governance import build_data_dictionary as ddict  # noqa: E402

REPO_ROOT = repo_root_from_script(Path(__file__))
DICT_REL = ddict.OUT_REL
DEFAULT_BASELINE_REF = "origin/main"
RATIFY_TOKEN = "CAPABILITY-RETIREMENT-RATIFIED"

# A previously-WIRED path is "retired" if, at HEAD, it is absent or one of these statuses.
_RETIRED_STATUSES = {"UNWIRED", "KNOWN_UNWIRED"}


@dataclass
class Regression:
    path: str
    baseline_status: str
    head_status: str  # "REMOVED" when the path is gone at HEAD


def _git_show(ref_path: str, repo_root: Path) -> str | None:
    """`git show <ref>:<path>` → text, or None if it does not resolve (fail-open)."""
    try:
        r = subprocess.run(
            ["git", "show", ref_path],
            capture_output=True, text=True, cwd=str(repo_root),
        )
    except Exception:
        return None
    if r.returncode != 0:
        return None
    return r.stdout


def _parse_dict_text(text: str) -> dict[str, str]:
    """Parse DATA_DICTIONARY.tsv text → {path: status}."""
    out: dict[str, str] = {}
    if not text:
        return out
    lines = text.splitlines()
    if not lines:
        return out
    header = lines[0].split("\t")
    try:
        p_idx = header.index("path")
        s_idx = header.index("status")
    except ValueError:
        return out
    for line in lines[1:]:
        if not line.strip():
            continue
        cols = line.split("\t")
        if len(cols) <= max(p_idx, s_idx):
            continue
        out[cols[p_idx]] = cols[s_idx]
    return out


def _head_status_map(repo_root: Path) -> dict[str, str]:
    """Regenerate the dictionary at HEAD (fresh build) → {path: status}."""
    rows = ddict.build_rows(repo_root)
    # rows are (path, purpose, subsystem, owner, consumers, status)
    return {r[0]: r[5] for r in rows}


def _collect_ratify_text(repo_root: Path, baseline_ref: str) -> str:
    """Union of PR-body env + commit bodies on baseline..HEAD (mirrors the governance
    review's collect_override_text; a self-contained copy keeps this gate importless)."""
    chunks: list[str] = []
    for env_key in ("PR_BODY", "GITHUB_PR_BODY"):
        val = os.environ.get(env_key)
        if val:
            chunks.append(val)
    try:
        r = subprocess.run(
            ["git", "log", "--format=%B", f"{baseline_ref}..HEAD"],
            capture_output=True, text=True, cwd=str(repo_root),
        )
        if r.returncode == 0 and r.stdout.strip():
            chunks.append(r.stdout)
    except Exception:
        pass
    return "\n".join(chunks)


def _has_ratify_token(text: str) -> bool:
    """True if `CAPABILITY-RETIREMENT-RATIFIED: <non-empty reason>` appears."""
    if not text:
        return False
    pat = re.compile(rf"{re.escape(RATIFY_TOKEN)}\s*:\s*\S.*", re.MULTILINE)
    return bool(pat.search(text))


def find_regressions(repo_root: Path, baseline_ref: str) -> tuple[list[Regression], bool]:
    """Return (regressions, baseline_available). baseline_available=False → fail-open."""
    baseline_text = _git_show(f"{baseline_ref}:{DICT_REL}", repo_root)
    if baseline_text is None:
        return [], False
    baseline = _parse_dict_text(baseline_text)
    head = _head_status_map(repo_root)
    regs: list[Regression] = []
    for path, status in baseline.items():
        if status != "WIRED":
            continue
        if path not in head:
            regs.append(Regression(path, status, "REMOVED"))
        elif head[path] in _RETIRED_STATUSES:
            regs.append(Regression(path, status, head[path]))
    regs.sort(key=lambda r: r.path)
    return regs, True


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="No-lost-functions capability-regression gate (§18)")
    ap.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    ap.add_argument("--baseline-ref", default=DEFAULT_BASELINE_REF,
                    help="git ref whose committed data dictionary is the baseline (default origin/main)")
    args = ap.parse_args(argv)
    repo_root: Path = args.repo_root

    regs, baseline_available = find_regressions(repo_root, args.baseline_ref)

    if not baseline_available:
        print(f"CAPABILITY REGRESSION GATE: PASS (fail-open) — baseline "
              f"'{args.baseline_ref}:{DICT_REL}' not readable; diff gate is a no-op on this ref.",
              file=sys.stderr)
        return 0

    if not regs:
        print(f"CAPABILITY REGRESSION GATE: PASS — no previously-WIRED capability was "
              f"orphaned or removed vs {args.baseline_ref}.", file=sys.stderr)
        return 0

    ratified = _has_ratify_token(_collect_ratify_text(repo_root, args.baseline_ref))
    for r in regs:
        verb = "REMOVED" if r.head_status == "REMOVED" else f"orphaned (→ {r.head_status})"
        print(f"REGRESSION: {r.path} was WIRED at {args.baseline_ref} and is now {verb}",
              file=sys.stderr)

    if ratified:
        print(f"CAPABILITY REGRESSION GATE: PASS (ratified) — {len(regs)} retirement(s) "
              f"covered by an explicit {RATIFY_TOKEN} tag.", file=sys.stderr)
        return 0

    print(f"CAPABILITY REGRESSION GATE: {len(regs)} unratified capability regression(s) — "
          f"blocking. New features never bury old functions (§18). Either re-wire the "
          f"function(s), or — if the retirement is intentional and operator-ratified — add "
          f"'{RATIFY_TOKEN}: <OPD ref>' to the PR body / a commit body.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
