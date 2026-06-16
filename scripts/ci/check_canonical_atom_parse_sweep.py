#!/usr/bin/env python3
"""CI parse-sweep guard for atoms/**/CANONICAL.txt — catches atom-header over-match regressions.

WHY THIS EXISTS
---------------
PR #1590 (SHA 0d1cf1520) ran a DEFECT-7 header repair that OVER-MATCHED: its repair
regex ``^(TOKEN)\\s+v\\d+\\s*$`` whose next non-empty line is ``---`` also fired on
legitimate *body-text* lines that happened to read like a header token (e.g. a block
whose body is the literal string ``RECOGNITION v02`` immediately followed by the
block's closing ``---``). The script prepended ``## `` to those body lines, promoting
them into phantom ``## RECOGNITION v02`` headers with an EMPTY metadata block. The real
``phoenix_v4.planning.assembly_compiler._parse_canonical_txt`` validator then rejected
those files ("missing path line in metadata") and raised ``ValueError``. Because
``check_tuple_viability._load_story_atoms_for_engine`` swallows that ValueError and
returns ``[]``, every affected engine pool collapsed to **NO_STORY_POOL** — tuples
could not render, live on main, gating Pearl_Prime assembly. 1,215 CANONICAL.txt files
that parsed CLEANLY at #1590's parent began failing.

WHAT THIS GUARD DOES
--------------------
It runs the REAL strict parser (``assembly_compiler._parse_canonical_txt``, the one whose
failure produces NO_STORY_POOL) over EVERY ``atoms/**/CANONICAL.txt`` and FAILS when:

  (A) a file fails the strict parser and is NOT in the checked-in baseline allowlist
      (``check_canonical_atom_parse_sweep_baseline.txt``) — i.e. a NEW parse regression
      relative to the documented, pre-existing DEFECT-7 / empty-HOOK-metadata debt; OR

  (B) a file exhibits the #1590 OVER-MATCH SIGNATURE — a ``## <LABEL> vNN`` header whose
      metadata block (the text between its two ``---`` delimiters) is empty/whitespace or
      itself embeds another ``## <LABEL> vNN`` header line — and is NOT in the baseline.
      This is the structural fingerprint of a body line wrongly promoted to a header; it
      is caught regardless of whether the strict parser happens to raise, so a future
      over-match cannot hide.

The baseline allowlist pins the 8,218 pre-existing strict-parse failures that exist
independently of #1590 (HOOK banks with intentionally-empty metadata + broader,
out-of-scope DEFECT-7 corruption that this restore did not touch). The guard is GREEN on
the post-restore tree and goes RED the instant a clean atom file regresses.

USAGE
-----
    python3 scripts/ci/check_canonical_atom_parse_sweep.py            # sweep + verdict
    python3 scripts/ci/check_canonical_atom_parse_sweep.py --json     # machine-readable
    python3 scripts/ci/check_canonical_atom_parse_sweep.py --update-baseline
        # regenerate the baseline from the CURRENT tree (use ONLY after an INTENTIONAL,
        # reviewed change to the pre-existing failure set — never to paper over a regression).

Exit code 0 = clean (no new failures, no new over-match signatures); 1 = regression.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ATOMS_ROOT = REPO_ROOT / "atoms"
BASELINE_PATH = Path(__file__).resolve().parent / "check_canonical_atom_parse_sweep_baseline.txt"

# ``## <LABEL> vNN`` header line (a bare token + version, nothing else on the line).
_HEADER_LINE_RE = re.compile(r"^##\s+([A-Z_]+)\s+v(\d+)\s*$")

# A full ``## <LABEL> vNN`` block: header, then the metadata block delimited by ``---``.
# group(3) is the captured metadata text (what the real validator inspects for ``path:``).
_BLOCK_RE = re.compile(
    r"^##\s+([A-Z_]+)\s+v(\d+)\s*\n---\s*\n([\s\S]*?)\n---",
    re.MULTILINE,
)


def _import_strict_parser():
    """Import the REAL strict parser whose failure drives NO_STORY_POOL.

    Imported lazily so ``--update-baseline`` and ``--help`` work even if the
    heavyweight planning package import chain is unavailable in a minimal env.
    """
    sys.path.insert(0, str(REPO_ROOT))
    from phoenix_v4.planning.assembly_compiler import _parse_canonical_txt  # noqa: WPS433

    return _parse_canonical_txt


def iter_canonical_files() -> list[Path]:
    """All ``atoms/**/CANONICAL.txt`` (includes ``locales/<locale>/CANONICAL.txt``)."""
    return sorted(ATOMS_ROOT.rglob("CANONICAL.txt"))


def overmatch_signature_hits(text: str) -> int:
    """Count ``## <LABEL> vNN`` blocks whose metadata block is empty/whitespace OR
    embeds another ``## <LABEL> vNN`` header line.

    This is the structural fingerprint left by PR #1590's over-match: a body line that
    read like a header token was promoted to ``## TOKEN vNN`` and slammed up against the
    prior block's closing ``---``, so its "metadata" is either blank or the *next* real
    header. A correctly-authored block always carries a ``path:`` (STORY engines) or real
    ``mode:``/scene metadata between its delimiters, never another ``## `` header.
    """
    hits = 0
    for m in _BLOCK_RE.finditer(text):
        meta = m.group(3)
        if not meta.strip():
            hits += 1
            continue
        if any(_HEADER_LINE_RE.match(line.strip()) for line in meta.splitlines()):
            hits += 1
    return hits


def load_baseline() -> set[str]:
    if not BASELINE_PATH.exists():
        return set()
    return {
        line.strip()
        for line in BASELINE_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def sweep() -> dict:
    """Run the strict parser + signature scan over every CANONICAL.txt. Returns a report."""
    parse = _import_strict_parser()
    baseline = load_baseline()
    files = iter_canonical_files()

    parse_fail: list[str] = []
    signature_fail: list[str] = []
    for f in files:
        rel = str(f.relative_to(REPO_ROOT))
        try:
            parse(f)
        except Exception:  # noqa: BLE001 — the real parser raises ValueError on bad data
            parse_fail.append(rel)
        try:
            if overmatch_signature_hits(f.read_text(encoding="utf-8")) > 0:
                signature_fail.append(rel)
        except OSError:
            parse_fail.append(rel)

    new_parse_fail = sorted(set(parse_fail) - baseline)
    new_signature_fail = sorted(set(signature_fail) - baseline)
    return {
        "total_files": len(files),
        "baseline_size": len(baseline),
        "parse_fail_total": len(parse_fail),
        "signature_fail_total": len(signature_fail),
        "new_parse_failures": new_parse_fail,
        "new_overmatch_signatures": new_signature_fail,
        "ok": not new_parse_fail and not new_signature_fail,
    }


def update_baseline() -> int:
    """Regenerate the baseline allowlist from the CURRENT tree state."""
    parse = _import_strict_parser()
    fails: list[str] = []
    for f in iter_canonical_files():
        try:
            parse(f)
        except Exception:  # noqa: BLE001
            fails.append(str(f.relative_to(REPO_ROOT)))
    fails = sorted(fails)
    header = (
        "# Baseline allowlist for scripts/ci/check_canonical_atom_parse_sweep.py\n"
        "# Pre-existing atoms/**/CANONICAL.txt files that FAIL the strict\n"
        "# assembly_compiler._parse_canonical_txt validator independently of any single PR\n"
        "# (intentionally-empty HOOK metadata + broader pre-existing DEFECT-7 corruption).\n"
        "# A file NOT in this list that fails the strict parser is a NEW regression and\n"
        "# blocks CI. Regenerate ONLY after an intentional, reviewed change via\n"
        "#   python3 scripts/ci/check_canonical_atom_parse_sweep.py --update-baseline\n"
    )
    BASELINE_PATH.write_text(header + "\n".join(fails) + "\n", encoding="utf-8")
    print(f"[parse-sweep] baseline updated: {len(fails)} entries -> {BASELINE_PATH.name}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true", help="Emit the report as JSON.")
    ap.add_argument(
        "--update-baseline",
        action="store_true",
        help="Regenerate the baseline allowlist from the current tree (reviewed use only).",
    )
    args = ap.parse_args(argv)

    if args.update_baseline:
        return update_baseline()

    report = sweep()
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"[parse-sweep] CANONICAL.txt files scanned : {report['total_files']}")
        print(f"[parse-sweep] baseline (pre-existing fails): {report['baseline_size']}")
        print(f"[parse-sweep] strict-parse failures total  : {report['parse_fail_total']}")
        print(f"[parse-sweep] over-match signatures total  : {report['signature_fail_total']}")
        print(f"[parse-sweep] NEW parse failures           : {len(report['new_parse_failures'])}")
        print(f"[parse-sweep] NEW over-match signatures     : {len(report['new_overmatch_signatures'])}")
        if not report["ok"]:
            print("\n[parse-sweep] FAIL — atom-header parse regression detected.")
            for f in report["new_parse_failures"][:50]:
                print(f"    NEW PARSE FAIL: {f}")
            for f in report["new_overmatch_signatures"][:50]:
                print(f"    NEW OVER-MATCH: {f}")
            print(
                "\nThis is the PR #1590 failure class: a clean CANONICAL.txt was mangled into\n"
                "metadata-less '## <LABEL> vNN' headers. Restore the body text; do NOT add the\n"
                "file to the baseline to silence this."
            )
        else:
            print("\n[parse-sweep] OK — no new atom-header parse regressions.")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
