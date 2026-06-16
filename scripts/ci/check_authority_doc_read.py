#!/usr/bin/env python3
"""
Drift detector: PRs touching governed subsystems should cite authority docs in PR body/commits.

Best-effort backstop — cannot verify a doc was read, only that the agent mentioned it.

Run:
  PYTHONPATH=. python3 scripts/ci/check_authority_doc_read.py \\
    --base origin/main --head HEAD \\
    --pr-body-file /path/to/body.txt \\
    --commit-messages-file /path/to/commits.txt

Exit: 0 always (warnings only).
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from drift_detector_git import changed_paths, repo_root_from_script

REPO_ROOT = repo_root_from_script(Path(__file__))
_GH_WARN_PREFIX = "::warning::"
MAP_PATH = REPO_ROOT / "artifacts" / "coordination" / "SUBSYSTEM_AUTHORITY_MAP.tsv"
ACTIVE_STATUSES = {"active"}


@dataclass
class SubsystemRule:
    subsystem_id: str
    authority_docs: list[str]
    config_prefixes: list[str]


@dataclass
class MissingCitation:
    subsystem_id: str
    authority_docs: list[str]
    touched_files: list[str]


def load_subsystem_rules(map_path: Path) -> list[SubsystemRule]:
    rules: list[SubsystemRule] = []
    with map_path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            status = (row.get("status") or "").strip()
            if status not in ACTIVE_STATUSES:
                continue
            docs = [d.strip() for d in (row.get("authority_doc") or "").split(";") if d.strip()]
            norm_prefixes: list[str] = []
            for p in (row.get("config_path") or "").split(";"):
                p = p.strip()
                if not p:
                    continue
                if p.endswith("/") or Path(p).suffix:
                    norm_prefixes.append(p)
                else:
                    norm_prefixes.append(p.rstrip("/") + "/")
            rules.append(
                SubsystemRule(
                    subsystem_id=(row.get("subsystem_id") or "").strip(),
                    authority_docs=docs,
                    config_prefixes=norm_prefixes,
                )
            )
    return rules


def file_matches_prefix(rel_path: str, prefix: str) -> bool:
    rel = rel_path.replace("\\", "/")
    if prefix.endswith("/"):
        return rel.startswith(prefix) or rel == prefix.rstrip("/")
    return rel == prefix or rel.startswith(prefix + "/")


def subsystems_for_file(rel_path: str, rules: list[SubsystemRule]) -> list[SubsystemRule]:
    matched: list[SubsystemRule] = []
    for rule in rules:
        if any(file_matches_prefix(rel_path, p) for p in rule.config_prefixes):
            matched.append(rule)
    return matched


def load_reference_text(
    pr_body_file: Path | None,
    commit_messages_file: Path | None,
    base: str | None,
    head: str,
    repo_root: Path,
) -> str:
    chunks: list[str] = []
    if pr_body_file and pr_body_file.is_file():
        chunks.append(pr_body_file.read_text(encoding="utf-8", errors="replace"))
    if commit_messages_file and commit_messages_file.is_file():
        chunks.append(commit_messages_file.read_text(encoding="utf-8", errors="replace"))

    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if event_path and Path(event_path).is_file():
        try:
            event = json.loads(Path(event_path).read_text(encoding="utf-8"))
            pr = event.get("pull_request") or {}
            if pr.get("body"):
                chunks.append(str(pr["body"]))
            if pr.get("title"):
                chunks.append(str(pr["title"]))
        except (json.JSONDecodeError, OSError):
            pass

    if base:
        proc = subprocess.run(
            ["git", "log", f"{base}..{head}", "--pretty=format:%s%n%b"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            chunks.append(proc.stdout)

    return "\n".join(chunks).lower()


def doc_is_referenced(doc: str, reference_text: str) -> bool:
    doc_norm = doc.replace("\\", "/").lower()
    if doc_norm in reference_text:
        return True
    basename = Path(doc_norm).name
    if basename and basename in reference_text:
        return True
    stem = Path(doc_norm).stem.replace("_", " ")
    if len(stem) >= 8 and stem in reference_text:
        return True
    return False


def subsystem_cited(rule: SubsystemRule, reference_text: str) -> bool:
    return any(doc_is_referenced(doc, reference_text) for doc in rule.authority_docs)


def analyze(
    repo_root: Path,
    base: str | None,
    head: str,
    reference_text: str,
    paths: list[str] | None = None,
) -> list[MissingCitation]:
    rules = load_subsystem_rules(repo_root / "artifacts" / "coordination" / "SUBSYSTEM_AUTHORITY_MAP.tsv")
    if paths is None:
        paths = changed_paths(base, head, repo_root)
    touched_by_subsystem: dict[str, tuple[SubsystemRule, list[str]]] = {}
    for rel in paths:
        rel = rel.replace("\\", "/")
        for rule in subsystems_for_file(rel, rules):
            if rule.subsystem_id not in touched_by_subsystem:
                touched_by_subsystem[rule.subsystem_id] = (rule, [])
            touched_by_subsystem[rule.subsystem_id][1].append(rel)

    missing: list[MissingCitation] = []
    for _sid, (rule, files) in sorted(touched_by_subsystem.items()):
        if subsystem_cited(rule, reference_text):
            continue
        missing.append(
            MissingCitation(
                subsystem_id=rule.subsystem_id,
                authority_docs=rule.authority_docs,
                touched_files=sorted(set(files)),
            )
        )
    return missing


def emit_warnings(missing: list[MissingCitation]) -> int:
    if not missing:
        print("AUTHORITY DOC READ: PASS", file=sys.stderr)
        return 0
    for m in missing:
        docs = "; ".join(m.authority_docs[:3])
        if len(m.authority_docs) > 3:
            docs += f" (+{len(m.authority_docs) - 3} more)"
        files = ", ".join(m.touched_files[:3])
        if len(m.touched_files) > 3:
            files += f" (+{len(m.touched_files) - 3} more)"
        msg = (
            f"subsystem {m.subsystem_id}: PR body/commits cite none of {docs} "
            f"(touched: {files})"
        )
        print(f"{_GH_WARN_PREFIX}{msg}", file=sys.stderr)
    print(f"AUTHORITY DOC READ: {len(missing)} warning(s) (non-blocking)", file=sys.stderr)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Warn when governed subsystem changes lack authority-doc citation")
    ap.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    ap.add_argument("--base", default=None)
    ap.add_argument("--head", default="HEAD")
    ap.add_argument("--pr-body-file", type=Path, default=None)
    ap.add_argument("--commit-messages-file", type=Path, default=None)
    ap.add_argument("--paths", nargs="*", default=None, help="Explicit changed paths (for tests)")
    ap.add_argument("--reference-text", default=None, help="Inline reference text (for tests)")
    args = ap.parse_args()

    if args.reference_text is not None:
        ref = args.reference_text.lower()
    else:
        ref = load_reference_text(
            args.pr_body_file,
            args.commit_messages_file,
            args.base,
            args.head,
            args.repo_root,
        )

    missing = analyze(args.repo_root, args.base, args.head, ref, paths=args.paths)
    return emit_warnings(missing)


if __name__ == "__main__":
    sys.exit(main())
