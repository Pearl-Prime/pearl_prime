#!/usr/bin/env python3
"""Classify doc-like files for canonicality status.

Produces artifacts/inventory/full_repo_doc_status_matrix_<DATE>.csv. One row
per .md/.txt/.docx/.rst/.adoc file. Uses full enumeration via git ls-files;
narrow filename patterns are banned (see specs/FULL_REPO_RECONCILIATION_EXECUTION_SPEC.md §2).

Usage:
    python3 scripts/audit/classify_doc_status.py [--out PATH] [--dry-run]

Tier 1; no LLM calls.
"""
from __future__ import annotations

import argparse
import csv
import datetime as _dt
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

DOC_PATTERNS = ("*.md", "*.txt", "*.docx", "*.rst", "*.adoc", "README", "AGENTS.md")

# Path-pattern fast classifier (covers ~94% of repo). Order matters.
FAST_RULES: list[tuple[str, str, str, str]] = [
    # (path-prefix, classification, subsystem, note)
    # GAP-G8 (PR-12 2026-04-27): specs/*.md were mis-classified as "unknown"
    # by an earlier audit pass; specs/ are subsystem authority docs by definition.
    ("specs/",                      "canonical",          "unknown",        "subsystem authority spec (subsystem inferred from filename)"),
    ("atoms/",                      "generated_artifact", "atoms",          "atom registry entry"),
    ("template_expand2/",           "fixture",            "teacher_mode",   "template expansion fixture"),
    ("brand-wizard-app/",           "current_support",    "brand_admin",    "brand wizard internal asset"),
    ("SOURCE_OF_TRUTH/teacher_banks/", "fixture",         "teacher_mode",   "teacher bank source"),
    ("SOURCE_OF_TRUTH/story_atoms/",   "fixture",         "core_pipeline",  "story atom source"),
    ("image_bank/",                 "fixture",            "brand_admin",    "image bank metadata"),
    # GAP-G9 (PR-12 2026-04-27): repo_coordination was an overweight catch-all
    # (116 of 154 canonicals). Sub-bucketed by audience: pm/architect/github/
    # session-protocol files belong to repo_coordination; subsystem-specific
    # coord docs route via SUBSYSTEM_HINTS instead.
    ("artifacts/coordination/",     "current_support",    "repo_coordination", "coordination registry"),
    ("artifacts/inventory/",        "current_support",    "repo_coordination", "audit inventory"),
    ("artifacts/",                  "generated_artifact", "unknown",        "build/audit artifact"),
    ("tests/",                      "test",               "unknown",        "test fixture"),
    ("archive/",                    "archived",           "unknown",        ""),
    ("salvage/",                    "archived",           "unknown",        ""),
    ("old_chat_specs/",             "archived",           "unknown",        ""),
    (".claude/worktrees/",          "fixture",            "unknown",        "ephemeral worktree artifact"),
]

SUBSYSTEM_HINTS: list[tuple[re.Pattern, str]] = [
    # Order matters: more-specific patterns first.
    (re.compile(r"(?i)pearl[_-]?prime|bestseller|story_atoms"), "pearl_prime"),
    (re.compile(r"(?i)pearl[_-]?news|news_writer"),            "pearl_news"),
    (re.compile(r"(?i)manga|catalog_reconciliation|webtoon"),   "manga_pipeline"),
    (re.compile(r"(?i)audiobook"),                              "audiobook_pipeline"),
    (re.compile(r"(?i)podcast"),                                "podcast_pipeline"),
    (re.compile(r"(?i)teacher|engine|writer_overlay"),          "teacher_mode"),
    (re.compile(r"(?i)brand[_-]?(wizard|admin|registry)"),      "brand_admin"),
    (re.compile(r"(?i)dashboard"),                              "dashboard"),
    (re.compile(r"(?i)integration|env_registry|secrets|credential"), "integrations"),
    (re.compile(r"(?i)video|render|flux"),                      "video_pipeline"),
    (re.compile(r"(?i)\btts\b|voice_routing|speech"),           "video_pipeline"),
    (re.compile(r"(?i)translation|locale|i18n|cjk"),            "translation"),
    (re.compile(r"(?i)marketing|funnel|freebee|conversion|ltv"), "marketing"),
    (re.compile(r"(?i)trend_feed|reddit_feed"),                 "trend_feeds"),
    (re.compile(r"(?i)quality_gate|ei_v2|effortful_imag"),      "ei_v2"),
    # GAP-G9 sub-buckets for what was previously catch-all repo_coordination
    (re.compile(r"(?i)github_govern|branch_protect|pr_review|pearl_github"), "pearl_devops"),
    (re.compile(r"(?i)pearl_pm|active_workstreams|active_projects|session_unity"), "repo_coordination"),
    (re.compile(r"(?i)pearl_architect|subsystem_authority|architecture_health"), "repo_coordination"),
    (re.compile(r"(?i)session_handoff|closeout_receipt|startup_receipt"), "repo_coordination"),
]

CANONICAL_SIGNALS = re.compile(
    r"\b(canonical|sole authority|single source of truth|authority doc)\b",
    re.IGNORECASE,
)
SUPERSEDED_SIGNALS = re.compile(
    r"\b(superseded|retired|deprecated|do not use|replaced by)\b",
    re.IGNORECASE,
)


def run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, cwd=REPO_ROOT, text=True)


def list_doc_files() -> list[str]:
    out = run(["git", "ls-files"] + list(DOC_PATTERNS))
    return [p for p in out.splitlines() if p]


def fast_classify(path: str) -> tuple[str, str, str] | None:
    for prefix, cls_, subsys, note in FAST_RULES:
        if path.startswith(prefix):
            return cls_, subsys, note
    return None


def infer_subsystem(path: str) -> str:
    for pat, sub in SUBSYSTEM_HINTS:
        if pat.search(path):
            return sub
    return "unknown"


def slow_classify(repo: Path, path: str) -> tuple[str, str, str]:
    """Used for the ~6% of paths that don't hit the fast rules."""
    full = repo / path
    head = ""
    line_count = 0
    if full.exists() and full.is_file():
        try:
            with full.open(errors="ignore") as f:
                lines = f.readlines()
                head = "".join(lines[:50])
                line_count = len(lines)
        except OSError:
            pass

    title = ""
    if path.endswith(".md") or path.endswith(".rst"):
        for line in head.splitlines():
            line = line.strip()
            if line.startswith("#"):
                title = line.lstrip("# ").strip()
                break
    if not title and head:
        title = head.splitlines()[0].strip()
    title = title[:80]

    if SUPERSEDED_SIGNALS.search(head):
        cls_ = "superseded"
    elif CANONICAL_SIGNALS.search(head) or path.startswith("specs/") or path.startswith("docs/"):
        cls_ = "canonical"
    elif path.lower().endswith("readme.md") or path.endswith("README"):
        cls_ = "README"
    elif line_count == 0:
        cls_ = "deletion_candidate"
    else:
        cls_ = "unknown"

    return cls_, title, str(line_count)


def last_commit_date(path: str) -> str:
    """Single-file fallback (use build_last_commit_date_map for bulk)."""
    try:
        out = run(["git", "log", "-n", "1", "--format=%ad", "--date=short", "--", path])
        return out.strip()
    except subprocess.CalledProcessError:
        return ""


def build_last_commit_date_map() -> dict[str, str]:
    """Bulk path → last-commit-date map via single git log invocation.

    PR-19 (2026-04-27) perf fix: prior per-file `git log -n 1` × 19,696 files
    was dominating runtime (script died around 1,684 rows). One pass over the
    full history is O(commit-count), not O(file-count). Mirrors the pattern
    in build_full_repo_inventory.py.
    """
    out = run([
        "git", "log", "--all", "--no-renames",
        "--pretty=format:COMMIT|%ad", "--date=short", "--name-only",
    ])
    last: dict[str, str] = {}
    cur_date = ""
    for line in out.splitlines():
        if line.startswith("COMMIT|"):
            cur_date = line.split("|", 1)[1]
        elif line.strip() and cur_date and line not in last:
            last[line] = cur_date
    return last


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    today = _dt.date.today().isoformat()
    default = REPO_ROOT / f"artifacts/inventory/full_repo_doc_status_matrix_{today}.csv"
    out_path = Path(args.out) if args.out else default
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        print(f"[dry-run] would write {out_path}", file=sys.stderr)
        return 0

    paths = list_doc_files()
    print(f"enumerated {len(paths):,} doc-like files", file=sys.stderr)

    print("building bulk last-commit-date map (single git log invocation)...", file=sys.stderr)
    date_map = build_last_commit_date_map()
    print(f"date map covers {len(date_map):,} paths", file=sys.stderr)

    with out_path.open("w") as g:
        w = csv.writer(g, delimiter="\t", quoting=csv.QUOTE_MINIMAL)
        w.writerow([
            "path", "top_level_area", "subsystem", "title_or_h1", "line_count",
            "last_commit_date", "classification", "references_in", "references_out",
            "conflict_with", "notes",
        ])
        for path in paths:
            tla = path.split("/", 1)[0] if "/" in path else "(root)"
            fast = fast_classify(path)
            if fast:
                cls_, subsys, note = fast
                title = path.rsplit("/", 1)[-1]
                lc = "-1"
                date_ = date_map.get(path, "")
                w.writerow([path, tla, subsys, title, lc, date_, cls_, "-1", "-1", "", note])
            else:
                cls_, title, lc = slow_classify(REPO_ROOT, path)
                subsys = infer_subsystem(path)
                date_ = date_map.get(path, "")
                w.writerow([path, tla, subsys, title, lc, date_, cls_, "0", "0", "", ""])

    print(f"wrote {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
