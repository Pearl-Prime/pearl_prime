#!/usr/bin/env python3
"""Book-level "listing-as-story" advisory gate — mirrors
`check_manga_story_authored.py` for prose books.

Ground truth (2026-07-21 audit, `docs/agent_prompt_packs/20260721_bestseller_atom_flow/INDEX.md`):
seed 43001 (`millennial_women_professionals x courage`) gate-PASSed with
`research_fit: {}` — no story_schedule, no character through-line, no
book_idea/motif payoff, ONTGP 0.52/Give 0.38/Pull 0.32, mechanism_called=0.
CLAUDE.md's Manga Vision-Conformance Doctrine already named this drift class
("listing-as-story") and CI-enforced it for manga via
`check_manga_story_authored.py`; no book-level equivalent existed before this
file. This is that equivalent, for the render dispatch's research_fit binding
rather than manga's chapter_script.

Detection: read a completed book's `enrichment_audit.json`. "Bound" means
`research_fit` resolved to an active, structured mode (`research_fit_v1` /
`twelve_shape_continuity`) with real spine/motif content — i.e.
`build_story_schedule()` (`phoenix_v4/planning/story_planner.py`) actually
found and used a `story_atoms` bank for this persona/topic. Anything else —
`mode == "skipped"` with a `skip_reason` containing `"no_story_atoms"` (the
exact substring stamped by `story_planner.py`, re-verified 2026-07-21 against
`tests/test_bestseller_atom_pipeline_honesty_20260720.py`), or the bare
`research_fit: {}` with no mode/skip_reason at all (the `legacy_planner` path
every real book render checked in this repo's proof roots today goes through,
since `research_fit` stamping is not yet wired into `scripts/run_pipeline.py`
on this branch — see the Lane 01 handoff for the full discovery note) — is
UNBOUND.

ADVISORY vs --strict (a threshold decision — operator-tier, NOT made by this
change):
  Default (advisory): an unbound book WARNs (loud stderr message) and is
  stamped in a companion `book_acceptance_stamp.json` written next to its
  `enrichment_audit.json`: `{"research_fit_bound": false, "acceptance_layer":
  "structurally_clear_only"}`. The book still renders; it just can never be
  reported as more than Layer 1 (`structurally clear`,
  `docs/PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md`) downstream, however
  many other gates pass. Exit code is always 0 in this mode UNLESS a target
  path is literally missing/unreadable (that is a real error, not a binding
  judgment, and always exits 1).
  `--strict` flips this to a hard render-block: exit 1 if ANY target is
  unbound. This is the documented hard-block option named in the Lane 01
  prompt pack (`docs/agent_prompt_packs/20260721_bestseller_atom_flow/01_ci_gate_research_fit_and_story_authored.md`);
  it ships OFF by default because turning it on changes which books can
  render at all — an operator-tier call the INDEX.md Evidence Requirements
  section explicitly reserves. It is drafted here, not enabled.

Two roles, one file (mirrors check_manga_story_authored.py):
  - `classify_research_fit(audit)` / `evaluate_book_target(path)` — import
    into the render dispatch or Lane 04's acceptance-layer stamping as the
    binding-check primitive.
  - CLI — one or more completed-book directories (`--book-dir`), explicit
    audit files (`--audit`), or a PR scan of changed enrichment_audit.json
    files (`--base`); book render outputs are untracked/gitignored in this
    repo today so `--book-dir` against a fresh or proof-root render is the
    primary real-world mode, not the git-diff scan.

Run:
    # advisory (default) — one or more completed books:
    PYTHONPATH=. python3 scripts/ci/check_book_story_authored.py \\
        --book-dir artifacts/qa/<run>/<cell>
    # hard-block variant (documented, NOT the default):
    PYTHONPATH=. python3 scripts/ci/check_book_story_authored.py \\
        --book-dir artifacts/qa/<run>/<cell> --strict

Exit: 0 in advisory mode (unless a target is missing/unreadable — always 1
then, in either mode); in --strict mode, 1 if any readable target is unbound.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo root for phoenix_v4 import
sys.path.insert(0, str(Path(__file__).resolve().parent))       # scripts/ci for drift_detector_git
from drift_detector_git import changed_paths, repo_root_from_script  # noqa: E402

REPO_ROOT = repo_root_from_script(Path(__file__))
AUDIT_FILENAME = "enrichment_audit.json"
STAMP_FILENAME = "book_acceptance_stamp.json"

# Active, structured research_fit modes — kept in sync with
# phoenix_v4/planning/story_planner.py (build_story_schedule) and
# scripts/ci/check_research_fit_honesty.py's own mode check. If you add a new
# mode there, add it here too (a test asserts these lists agree in intent).
_BOUND_MODES = frozenset({"research_fit_v1", "twelve_shape_continuity"})
_UNBOUND_ACCEPTANCE_LAYER = "structurally_clear_only"


class BookAuditUnreadableError(Exception):
    """Raised when a book-dir/audit target cannot be located or parsed."""


def _load_audit(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise BookAuditUnreadableError(
            f"{path}: {AUDIT_FILENAME} does not contain a JSON object"
        )
    return data


def classify_research_fit(audit: dict[str, Any]) -> tuple[bool, str]:
    """Return (research_fit_bound, reason). reason is '' when bound.

    Mirrors the honesty checks in check_research_fit_honesty.py's check_audit
    but answers a different question: not "is this audit internally
    consistent" but "did this book actually bind to a story_atoms bank".
    """
    rf = audit.get("research_fit")
    rf = rf if isinstance(rf, dict) else {}
    top_skip = str(audit.get("research_fit_skip_reason") or "").strip()
    rf_skip = str(rf.get("skip_reason") or "").strip()
    mode = str(rf.get("mode") or "").strip()
    skip_reason = rf_skip or top_skip

    if mode in _BOUND_MODES and (
        rf.get("spine_pins") or rf.get("book_phases") or rf.get("motif_ledger")
    ):
        return True, ""

    if skip_reason:
        return False, skip_reason
    if mode == "skipped":
        return False, "research_fit.mode=skipped with no skip_reason"
    if not rf:
        return False, (
            "research_fit is empty ({}) with no mode/skip_reason set — "
            "legacy_planner path, equivalent to no_story_atoms: book rendered "
            "with no character through-line bound to a story_atoms bank"
        )
    return False, f"research_fit.mode={mode!r} present but missing spine/motif structure"


def resolve_audit_path(target: Path) -> Path:
    return target / AUDIT_FILENAME if target.is_dir() else target


def stamp_book_acceptance(audit_path: Path, *, bound: bool, reason: str) -> dict[str, Any]:
    """Merge the research_fit binding finding into book_acceptance_stamp.json
    next to the audit file, so Lane 04 (acceptance-layer stamp) has one place
    to read the cap from without re-deriving it. Returns the written stamp."""
    stamp_path = audit_path.parent / STAMP_FILENAME
    stamp: dict[str, Any] = {}
    if stamp_path.is_file():
        try:
            existing = json.loads(stamp_path.read_text(encoding="utf-8"))
            if isinstance(existing, dict):
                stamp = existing
        except (json.JSONDecodeError, OSError):
            stamp = {}
    stamp["research_fit_bound"] = bound
    if bound:
        stamp.pop("acceptance_layer", None)
        stamp.pop("research_fit_unbound_reason", None)
    else:
        stamp["acceptance_layer"] = _UNBOUND_ACCEPTANCE_LAYER
        stamp["research_fit_unbound_reason"] = reason
    stamp_path.write_text(json.dumps(stamp, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return stamp


def evaluate_book_target(
    target: Path, *, write_stamp: bool = True
) -> tuple[bool, str, dict[str, Any]]:
    """Return (bound, reason, stamp_written). Raises BookAuditUnreadableError
    if the target has no readable enrichment_audit.json."""
    audit_path = resolve_audit_path(target)
    if not audit_path.is_file():
        raise BookAuditUnreadableError(f"no {AUDIT_FILENAME} at {audit_path}")
    audit = _load_audit(audit_path)
    bound, reason = classify_research_fit(audit)
    stamp = stamp_book_acceptance(audit_path, bound=bound, reason=reason) if write_stamp else {}
    return bound, reason, stamp


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "--book-dir", nargs="+", default=None, type=Path,
        help="one or more completed-book render directories",
    )
    ap.add_argument(
        "--audit", nargs="+", default=None, type=Path,
        help="one or more explicit enrichment_audit.json files",
    )
    ap.add_argument("--base", default=None, help="git base ref (scan changed enrichment_audit.json)")
    ap.add_argument("--head", default="HEAD")
    ap.add_argument("--paths", nargs="*", default=None, help="explicit repo-relative paths (tests)")
    ap.add_argument(
        "--strict", action="store_true",
        help="hard-block: exit 1 if any target is research_fit-unbound "
             "(documented option, OFF by default — operator-tier threshold)",
    )
    ap.add_argument(
        "--no-stamp", action="store_true",
        help="do not write book_acceptance_stamp.json (report only)",
    )
    ap.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = ap.parse_args(argv)

    targets: list[Path] = []
    if args.book_dir:
        targets.extend(args.book_dir)
    if args.audit:
        targets.extend(args.audit)
    if args.paths is not None:
        targets.extend(args.repo_root / p for p in args.paths)
    elif args.base:
        targets.extend(
            args.repo_root / p
            for p in changed_paths(args.base, args.head, args.repo_root)
            if p.endswith(AUDIT_FILENAME)
        )

    if not targets:
        # Empty --base/--paths scan is a clean pass (same contract as
        # check_manga_story_authored.py: "PASS (0 changed script(s))").
        # Only a bare invocation with no mode flags is a usage error.
        if args.base or args.paths is not None:
            print(
                "BOOK-STORY-AUTHORED: PASS (0 changed enrichment_audit.json)",
                file=sys.stderr,
            )
            return 0
        print("No book targets given (--book-dir/--audit/--base)", file=sys.stderr)
        return 2

    hard_errors: list[str] = []
    unbound: list[tuple[Path, str]] = []
    bound_count = 0
    seen: set[Path] = set()
    for t in targets:
        if t in seen:
            continue
        seen.add(t)
        try:
            is_bound, reason, _stamp = evaluate_book_target(t, write_stamp=not args.no_stamp)
        except (BookAuditUnreadableError, json.JSONDecodeError, OSError) as e:
            hard_errors.append(str(e))
            continue
        if is_bound:
            bound_count += 1
        else:
            unbound.append((t, reason))

    for e in hard_errors:
        print(f"ERROR: {e}", file=sys.stderr)

    for t, reason in unbound:
        print(
            f"WARN: research_fit UNBOUND at {t} — {reason}; acceptance_layer "
            f"capped at {_UNBOUND_ACCEPTANCE_LAYER!r} (advisory — book still "
            f"renders; rerun with --strict to hard-block)",
            file=sys.stderr,
        )

    if hard_errors:
        print(f"BOOK-STORY-AUTHORED: {len(hard_errors)} unreadable target(s)", file=sys.stderr)
        return 1

    if unbound and args.strict:
        print(f"BOOK-STORY-AUTHORED: {len(unbound)} unbound (STRICT — blocking)", file=sys.stderr)
        return 1

    total = bound_count + len(unbound)
    status = "PASS" if not unbound else "WARN"
    print(
        f"BOOK-STORY-AUTHORED: {status} ({bound_count} bound, {len(unbound)} unbound "
        f"of {total} — advisory only unless --strict)",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
