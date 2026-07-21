#!/usr/bin/env python3
"""Ensure required agent bootstrap docs are indexed in DOCS_INDEX.md."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from scripts.ci.check_docs_governance import LINK_RE, resolve_link

REQUIRED_LINE_RE = re.compile(r"^\s*-\s+([A-Za-z0-9_./-]+)")


def parse_required_docs(agent_brief: Path) -> list[str]:
    text = agent_brief.read_text(encoding="utf-8")
    required: list[str] = []
    in_block = False
    for line in text.splitlines():
        if line.strip() == "Before generating any prompt, read:":
            in_block = True
            continue
        if in_block and not line.strip():
            break
        if not in_block:
            continue
        match = REQUIRED_LINE_RE.match(line)
        if match:
            required.append(match.group(1).strip())
    if "docs/agent_brief.txt" not in required:
        required.insert(0, "docs/agent_brief.txt")
    return required


def indexed_paths(docs_index: Path, repo_root: Path) -> set[str]:
    docs_dir = docs_index.parent
    text = docs_index.read_text(encoding="utf-8")
    paths: set[str] = set()
    for match in LINK_RE.finditer(text):
        target = match.group(2).strip()
        resolved = resolve_link(docs_dir, target)
        if resolved is None:
            continue
        try:
            rel = resolved.resolve().relative_to(repo_root.resolve())
        except ValueError:
            continue
        paths.add(rel.as_posix())
    return paths


def check_required_docs_index(repo_root: Path) -> tuple[list[str], list[str]]:
    agent_brief = repo_root / "docs" / "agent_brief.txt"
    docs_index = repo_root / "docs" / "DOCS_INDEX.md"
    required = parse_required_docs(agent_brief)
    indexed = indexed_paths(docs_index, repo_root)
    missing: list[str] = []
    for rel in required:
        if not (repo_root / rel).exists():
            missing.append(f"{rel} (file missing)")
        elif rel not in indexed:
            missing.append(rel)
    return required, missing


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    required, missing = check_required_docs_index(args.repo_root)
    if missing:
        print("Required docs index check FAILED")
        print(f"  required_docs_scanned={len(required)}")
        for rel in missing:
            print(f"  missing_index_row={rel}")
        return 1
    print("Required docs index check PASSED")
    print(f"  required_docs_scanned={len(required)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
