#!/usr/bin/env python3
"""Memory-consolidation cadence pre-flight (P0-6, AGENT_SYSTEM_IMPROVEMENT_V2_SPEC).

READ-ONLY freshness snapshot of the Claude Code auto-memory directory. This does
NOT consolidate anything — consolidation is done by the packaged `consolidate-memory`
skill inside an operator-present Claude Code session (Tier-1). This script only
surfaces *what* should be reviewed and *how stale* it is, so the operator can decide
whether this month's cadence pass is worth running and which entries to scrutinise.

Why a separate, dependency-free script:
  * The cadence runbook (docs/MEMORY_CONSOLIDATION_CADENCE_RUNBOOK.md) and the
    scheduled reminder workflow (.github/workflows/memory-consolidation-reminder.yml)
    both want a cheap, side-effect-free "is the memory stale?" read.
  * It must run with the stock interpreter (no pip installs, no repo PYTHONPATH),
    because the operator runs it ad hoc and CI may run it on a clean runner.

Tier policy: pure stdlib, NO LLM call of any kind (paid or local). The actual
reflective merge is the operator's `consolidate-memory` skill, not this script.

Usage:
    python3 scripts/memory/memory_cadence_preflight.py
    python3 scripts/memory/memory_cadence_preflight.py --memory-dir /path/to/memory
    python3 scripts/memory/memory_cadence_preflight.py --json
    python3 scripts/memory/memory_cadence_preflight.py --stale-days 45

Exit code is always 0 in normal operation (this is a report, not a gate). It exits
non-zero only on an unexpected internal error, never on "memory looks stale".
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

# The canonical Claude Code auto-memory layout: a per-project `memory/` dir whose
# index is MEMORY.md and whose body is a set of sibling `*.md` topic files. This is
# the same structure the packaged `consolidate-memory` skill operates over.
INDEX_FILENAME = "MEMORY.md"

# Default staleness threshold. Entries (topic files) untouched for longer than this
# are flagged as "review candidates" — the most likely place a wrong lesson has
# ossified. Tunable via --stale-days; the cadence ships monthly so 45d ~= "older
# than one full cadence cycle and then some".
DEFAULT_STALE_DAYS = 45


def default_memory_dir() -> Path:
    """Best-effort resolution of the auto-memory dir for the current project.

    Order of precedence:
      1. $CLAUDE_MEMORY_DIR (explicit override, used by the runbook / CI).
      2. ~/.claude/projects/<slug>/memory for a project slug derived from CWD.
      3. The first ~/.claude/projects/*/memory that actually contains MEMORY.md.

    Returns a Path even if it does not exist; the caller validates existence so it
    can print a friendly message rather than throwing.
    """
    env = os.environ.get("CLAUDE_MEMORY_DIR")
    if env:
        return Path(env).expanduser()

    projects = Path.home() / ".claude" / "projects"

    # 2. Derive the slug Claude Code uses: the absolute CWD with os.sep -> '-'.
    #    e.g. /Users/ahjan/phoenix_omega -> -Users-ahjan-phoenix-omega
    cwd = Path.cwd().resolve()
    slug = str(cwd).replace(os.sep, "-")
    candidate = projects / slug / "memory"
    if (candidate / INDEX_FILENAME).is_file():
        return candidate

    # 3. Fall back to any project that has a MEMORY.md index.
    if projects.is_dir():
        for child in sorted(projects.iterdir()):
            mem = child / "memory"
            if (mem / INDEX_FILENAME).is_file():
                return mem

    # Nothing found — return the derived candidate so the message is actionable.
    return candidate


def _age_days(path: Path, now: float) -> float:
    return (now - path.stat().st_mtime) / 86400.0


def scan(memory_dir: Path, stale_days: float) -> dict:
    """Build a freshness report for the memory dir. Read-only."""
    now = time.time()
    index = memory_dir / INDEX_FILENAME

    report: dict = {
        "memory_dir": str(memory_dir),
        "exists": memory_dir.is_dir(),
        "index_present": index.is_file(),
        "stale_days_threshold": stale_days,
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
        "topic_file_count": 0,
        "index_age_days": None,
        "index_referenced_count": None,
        "topic_files": [],          # every *.md except the index
        "stale_candidates": [],     # topic files older than the threshold
        "unindexed_files": [],      # *.md on disk not linked from MEMORY.md
    }

    if not memory_dir.is_dir():
        return report

    if index.is_file():
        report["index_age_days"] = round(_age_days(index, now), 1)
        try:
            index_text = index.read_text(encoding="utf-8", errors="replace")
        except OSError:
            index_text = ""
        # Count markdown links in the index — a proxy for "entries the index claims
        # to track". A drift between this and the on-disk file count is exactly the
        # kind of staleness the cadence exists to catch.
        report["index_referenced_count"] = index_text.count("](")
    else:
        index_text = ""

    topic_files = sorted(
        p for p in memory_dir.glob("*.md") if p.name != INDEX_FILENAME
    )
    report["topic_file_count"] = len(topic_files)

    for p in topic_files:
        age = round(_age_days(p, now), 1)
        entry = {"name": p.name, "age_days": age}
        report["topic_files"].append(entry)
        if age > stale_days:
            report["stale_candidates"].append(entry)
        # Heuristic: is this file linked from the index at all?
        if index_text and p.name not in index_text:
            report["unindexed_files"].append(p.name)

    # Sort stale candidates oldest-first so the operator triages the most-ossified
    # entries before the rest.
    report["stale_candidates"].sort(key=lambda e: e["age_days"], reverse=True)
    return report


def render_human(report: dict) -> str:
    lines: list[str] = []
    lines.append("# Memory-consolidation cadence — pre-flight snapshot")
    lines.append("")
    lines.append(f"- memory dir: `{report['memory_dir']}`")
    if not report["exists"]:
        lines.append("- **status: NOT FOUND** — nothing to consolidate here.")
        lines.append(
            "  Set $CLAUDE_MEMORY_DIR or run from the project whose memory you "
            "want to review."
        )
        return "\n".join(lines)
    lines.append(f"- index present (`{INDEX_FILENAME}`): {report['index_present']}")
    if report["index_age_days"] is not None:
        lines.append(f"- index last modified: {report['index_age_days']} days ago")
    if report["index_referenced_count"] is not None:
        lines.append(
            f"- index links: {report['index_referenced_count']}  |  "
            f"topic files on disk: {report['topic_file_count']}"
        )
    else:
        lines.append(f"- topic files on disk: {report['topic_file_count']}")
    lines.append(
        f"- staleness threshold: > {report['stale_days_threshold']} days"
    )
    lines.append("")

    stale = report["stale_candidates"]
    lines.append(f"## Stale review candidates ({len(stale)})")
    if stale:
        lines.append("")
        lines.append("Oldest first — review these for wrong/ossified lessons:")
        lines.append("")
        for e in stale:
            lines.append(f"- `{e['name']}` — {e['age_days']} days old")
    else:
        lines.append("")
        lines.append("_None over threshold — memory is reasonably fresh._")
    lines.append("")

    unindexed = report["unindexed_files"]
    if unindexed:
        lines.append(f"## Files not linked from {INDEX_FILENAME} ({len(unindexed)})")
        lines.append("")
        lines.append("Possible index drift — confirm these are intentional:")
        lines.append("")
        for name in unindexed:
            lines.append(f"- `{name}`")
        lines.append("")

    lines.append("---")
    lines.append(
        "Next: run the `consolidate-memory` skill in a Claude Code session to "
        "challenge/merge these. See "
        "`docs/MEMORY_CONSOLIDATION_CADENCE_RUNBOOK.md`."
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--memory-dir",
        default=None,
        help="Path to the Claude Code memory dir (default: auto-resolve).",
    )
    ap.add_argument(
        "--stale-days",
        type=float,
        default=DEFAULT_STALE_DAYS,
        help=f"Flag topic files older than N days (default {DEFAULT_STALE_DAYS}).",
    )
    ap.add_argument(
        "--json",
        action="store_true",
        help="Emit the raw report as JSON instead of human-readable text.",
    )
    args = ap.parse_args(argv)

    memory_dir = (
        Path(args.memory_dir).expanduser()
        if args.memory_dir
        else default_memory_dir()
    )

    report = scan(memory_dir, args.stale_days)

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(render_human(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
