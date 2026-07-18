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

  (C) an ENGLISH BASE STORY pool (atoms/<persona>/<topic>/<story_engine>/CANONICAL.txt,
      engine in STORY_ENGINES) carries the over-match signature -- checked INDEPENDENTLY
      of the baseline (report key story_pool_overmatch). A STORY pool is exactly what
      check_tuple_viability loads, so an over-match there IS NO_STORY_POOL and can never
      be a baseline-able "pre-existing" state. (C) is the invariant whose absence let
      #1623 ship the burnout/overwhelm residual; it bounds what (A)/(B)'s baseline can hide.

  (D) a block's PROSE BODY (not its metadata) is the bare, unauthored next-header label --
      e.g. the body under ``## RECOGNITION v01`` is literally the string ``RECOGNITION v02``,
      no ``##`` prefix -- and is NOT in the separate stub baseline
      (``check_canonical_atom_parse_sweep_stub_baseline.txt``). This is the UN-PROMOTED
      sibling of the #1590 over-match: DEFECT-7's repair never touched these, so the label
      just sat as prose instead of ever becoming a phantom header. These blocks have
      well-formed metadata and parse CLEANLY through the strict parser (checks A/B never see
      them) and are also invisible to
      ``phoenix_v4.rendering.prose_resolver._is_stub_body`` (which only recognizes
      bracket/pipeline placeholder stubs, not bare-header-text ones) -- so unlike (A)/(B),
      an un-caught (D) instance does not fail a build; it silently ships garbage one-line
      "prose" in the selectable rendering pool. Found 2026-07-10 while fixing
      atoms/gen_z_professionals/overthinking/{false_alarm,watcher}/CANONICAL.txt (see
      artifacts/qa/OVERTHINKING_STUB_CONTENT_FIX_2026-07-10.md); repo-wide sweep at that time
      found 883 files / 7,769 variants carrying this shape, baselined below.

The baseline allowlist pins the 8,218 pre-existing strict-parse failures that exist
independently of #1590 (HOOK banks with intentionally-empty metadata + broader,
out-of-scope DEFECT-7 corruption that this restore did not touch). The guard is GREEN on
the post-restore tree and goes RED the instant a clean atom file regresses. The stub
baseline is a SEPARATE file/list (883 entries as of 2026-07-10) tracking the (D) debt
independently, so the two categories of pre-existing debt stay independently reviewable.

USAGE
-----
    python3 scripts/ci/check_canonical_atom_parse_sweep.py                  # sweep + verdict
    python3 scripts/ci/check_canonical_atom_parse_sweep.py --json           # machine-readable
    python3 scripts/ci/check_canonical_atom_parse_sweep.py --update-baseline
        # regenerate the (A)/(B) baseline from the CURRENT tree (use ONLY after an
        # INTENTIONAL, reviewed change to the pre-existing failure set — never to paper
        # over a regression).
    python3 scripts/ci/check_canonical_atom_parse_sweep.py --update-stub-baseline
        # regenerate the (D) stub baseline from the CURRENT tree (same rule: only after an
        # intentional, reviewed content fix — e.g. after authoring real prose for a
        # previously-stubbed file, to drop it out of the baseline).

Exit code 0 = clean (no new failures, no new over-match signatures, no new stub content); 1 = regression.
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
STUB_BASELINE_PATH = (
    Path(__file__).resolve().parent / "check_canonical_atom_parse_sweep_stub_baseline.txt"
)

# ``## <LABEL> vNN`` header line (a bare token + version, nothing else on the line).
_HEADER_LINE_RE = re.compile(r"^##\s+([A-Z_]+)\s+v(\d+)\s*$")

# A full ``## <LABEL> vNN`` block: header, then the metadata block delimited by ``---``.
# group(3) is the captured metadata text (what the real validator inspects for ``path:``).
_BLOCK_RE = re.compile(
    r"^##\s+([A-Z_]+)\s+v(\d+)\s*\n---\s*\n([\s\S]*?)\n---",
    re.MULTILINE,
)

# Same block, but capturing the PROSE body (between the metadata's closing ``---`` and the
# block's own closing ``---``) instead of the metadata — matches the shape
# ``phoenix_v4.rendering.prose_resolver._parse_canonical_with_prose`` uses at render time,
# since check (D) targets exactly what that renderer would select, not what the strict
# metadata-only parser validates.
_PROSE_BLOCK_RE = re.compile(
    r"^##\s+([A-Z_]+)\s+v(\d+)\s*\n---\s*\n[\s\S]*?\n---\s*\n([\s\S]*?)(?=\n---|\Z)",
    re.MULTILINE,
)

# A prose body that is EXACTLY a bare ``LABEL vNN`` token, nothing else — the un-promoted
# DEFECT-7 shape. Full-string match (post-strip) so real prose that merely mentions a
# role/version in passing, or terse-but-real "band-fill" prose like "Crisis. Breakthrough.",
# never false-positives (see tests).
_STUB_PROSE_RE = re.compile(r"^[A-Z_]+\s+v\d+$")

# STORY engine pools (``atoms/<persona>/<topic>/<engine>/CANONICAL.txt``) are exactly what
# ``check_tuple_viability._load_story_atoms_for_engine`` loads; an over-match here IS the
# NO_STORY_POOL failure mode. It is therefore checked INDEPENDENTLY of the baseline — a STORY
# pool can never be silenced by adding it to the allowlist. This is the invariant whose
# absence let #1623 ship a residual: a clean STORY pool (corporate_managers/burnout/overwhelm)
# was over-matched yet merged because the only blocking check is "Verify governance".
STORY_ENGINES = frozenset(
    {"false_alarm", "overwhelm", "shame", "spiral", "watcher", "grief", "comparison"}
)


def is_english_story_pool(path: Path) -> bool:
    """True only for ``atoms/<persona>/<topic>/<story_engine>/CANONICAL.txt`` (the English base
    STORY pool). Locale variants (``.../locales/<loc>/CANONICAL.txt``) are excluded: their
    pre-existing CJK breakage is a separate voice/infra-gated backlog, not this guard's job."""
    try:
        rel = path.relative_to(ATOMS_ROOT).parts
    except ValueError:
        return False
    return len(rel) == 4 and rel[2] in STORY_ENGINES and rel[-1] == "CANONICAL.txt"


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


def stub_prose_signature_hits(text: str) -> int:
    """Count blocks whose PROSE body (not metadata) is the bare, unauthored next-header
    label. See check (D) in the module docstring. Structurally distinct from
    ``overmatch_signature_hits``: those blocks fail or nearly-fail the strict parser
    (empty or header-embedding metadata); these blocks have well-formed metadata and parse
    CLEANLY — the defect lives entirely in the prose body, which the strict parser never
    inspects.
    """
    hits = 0
    for m in _PROSE_BLOCK_RE.finditer(text):
        prose = m.group(3).strip()
        if _STUB_PROSE_RE.match(prose):
            hits += 1
    return hits


def _en_source_rel(rel: str) -> str | None:
    """Map atoms/.../locales/<loc>/CANONICAL.txt → atoms/.../CANONICAL.txt."""
    parts = Path(rel).parts
    if "locales" not in parts:
        return None
    idx = parts.index("locales")
    return str(Path(*parts[:idx]) / "CANONICAL.txt")


def is_baseline_parse_fail(rel: str, baseline: set[str]) -> bool:
    """True when strict-parse failure is pre-existing (self or inherited from en source)."""
    if rel in baseline:
        return True
    en = _en_source_rel(rel)
    return bool(en and en in baseline)


def load_baseline() -> set[str]:
    if not BASELINE_PATH.exists():
        return set()
    return {
        line.strip()
        for line in BASELINE_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def load_stub_baseline() -> set[str]:
    if not STUB_BASELINE_PATH.exists():
        return set()
    return {
        line.strip()
        for line in STUB_BASELINE_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def sweep() -> dict:
    """Run the strict parser + signature scan over every CANONICAL.txt. Returns a report."""
    parse = _import_strict_parser()
    baseline = load_baseline()
    stub_baseline = load_stub_baseline()
    files = iter_canonical_files()

    parse_fail: list[str] = []
    signature_fail: list[str] = []
    story_overmatch: list[str] = []
    stub_fail: list[str] = []
    for f in files:
        rel = str(f.relative_to(REPO_ROOT))
        try:
            parse(f)
        except Exception:  # noqa: BLE001 — the real parser raises ValueError on bad data
            parse_fail.append(rel)
        try:
            text = f.read_text(encoding="utf-8")
        except OSError:
            parse_fail.append(rel)
            continue
        if overmatch_signature_hits(text) > 0:
            signature_fail.append(rel)
            if is_english_story_pool(f):
                story_overmatch.append(rel)
        if stub_prose_signature_hits(text) > 0:
            stub_fail.append(rel)

    new_parse_fail = sorted(r for r in set(parse_fail) if not is_baseline_parse_fail(r, baseline))
    new_signature_fail = sorted(set(signature_fail) - baseline)
    # STORY-pool over-match is NOT reduced by the baseline — it is always a NO_STORY_POOL regression.
    story_overmatch = sorted(set(story_overmatch))
    new_stub_fail = sorted(set(stub_fail) - stub_baseline)
    return {
        "total_files": len(files),
        "baseline_size": len(baseline),
        "stub_baseline_size": len(stub_baseline),
        "parse_fail_total": len(parse_fail),
        "signature_fail_total": len(signature_fail),
        "stub_fail_total": len(stub_fail),
        "new_parse_failures": new_parse_fail,
        "new_overmatch_signatures": new_signature_fail,
        "story_pool_overmatch": story_overmatch,
        "new_stub_failures": new_stub_fail,
        "ok": (
            not new_parse_fail
            and not new_signature_fail
            and not story_overmatch
            and not new_stub_fail
        ),
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


def update_stub_baseline() -> int:
    """Regenerate the (D) stub-content baseline allowlist from the CURRENT tree state."""
    stubs: list[str] = []
    for f in iter_canonical_files():
        try:
            text = f.read_text(encoding="utf-8")
        except OSError:
            continue
        if stub_prose_signature_hits(text) > 0:
            stubs.append(str(f.relative_to(REPO_ROOT)))
    stubs = sorted(stubs)
    header = (
        "# Stub-content baseline allowlist for scripts/ci/check_canonical_atom_parse_sweep.py\n"
        "# Pre-existing atoms/**/CANONICAL.txt files carrying check (D): a block whose PROSE\n"
        "# body is the bare, unauthored next-header label (e.g. body 'RECOGNITION v02' under\n"
        "# header '## RECOGNITION v01'). See artifacts/qa/OVERTHINKING_STUB_CONTENT_FIX_2026-07-10.md\n"
        "# for the discovery and fix pattern. A file NOT in this list that carries this shape\n"
        "# is a NEW regression and blocks CI. Regenerate ONLY after an intentional, reviewed\n"
        "# content fix (authoring real prose for a stubbed variant) via\n"
        "#   python3 scripts/ci/check_canonical_atom_parse_sweep.py --update-stub-baseline\n"
    )
    STUB_BASELINE_PATH.write_text(header + "\n".join(stubs) + "\n", encoding="utf-8")
    print(f"[parse-sweep] stub baseline updated: {len(stubs)} entries -> {STUB_BASELINE_PATH.name}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true", help="Emit the report as JSON.")
    ap.add_argument(
        "--update-baseline",
        action="store_true",
        help="Regenerate the (A)/(B) baseline allowlist from the current tree (reviewed use only).",
    )
    ap.add_argument(
        "--update-stub-baseline",
        action="store_true",
        help="Regenerate the (D) stub-content baseline allowlist from the current tree (reviewed use only).",
    )
    args = ap.parse_args(argv)

    if args.update_baseline:
        return update_baseline()
    if args.update_stub_baseline:
        return update_stub_baseline()

    report = sweep()
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"[parse-sweep] CANONICAL.txt files scanned : {report['total_files']}")
        print(f"[parse-sweep] baseline (pre-existing fails): {report['baseline_size']}")
        print(f"[parse-sweep] stub baseline (pre-existing) : {report['stub_baseline_size']}")
        print(f"[parse-sweep] strict-parse failures total  : {report['parse_fail_total']}")
        print(f"[parse-sweep] over-match signatures total  : {report['signature_fail_total']}")
        print(f"[parse-sweep] stub-content signatures total: {report['stub_fail_total']}")
        print(f"[parse-sweep] NEW parse failures           : {len(report['new_parse_failures'])}")
        print(f"[parse-sweep] NEW over-match signatures     : {len(report['new_overmatch_signatures'])}")
        print(f"[parse-sweep] STORY-pool over-match (never OK): {len(report['story_pool_overmatch'])}")
        print(f"[parse-sweep] NEW stub-content signatures   : {len(report['new_stub_failures'])}")
        if not report["ok"]:
            print("\n[parse-sweep] FAIL — atom-header parse regression detected.")
            for f in report["new_parse_failures"][:50]:
                print(f"    NEW PARSE FAIL: {f}")
            for f in report["new_overmatch_signatures"][:50]:
                print(f"    NEW OVER-MATCH: {f}")
            for f in report["story_pool_overmatch"][:50]:
                print(f"    STORY-POOL OVER-MATCH (restore, never baseline): {f}")
            for f in report["new_stub_failures"][:50]:
                print(f"    NEW STUB CONTENT: {f}")
            print(
                "\nThis is the PR #1590 failure class: a clean CANONICAL.txt was mangled into\n"
                "metadata-less '## <LABEL> vNN' headers. Restore the body text; do NOT add the\n"
                "file to the baseline to silence this.\n"
                "\n"
                "NEW STUB CONTENT means a block's prose body is a bare, unauthored next-header\n"
                "label (check D). Author real prose for that variant; do NOT add the file to the\n"
                "stub baseline to silence this."
            )
        else:
            print("\n[parse-sweep] OK — no new atom-header parse regressions.")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
