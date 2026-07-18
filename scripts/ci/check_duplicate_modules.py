#!/usr/bin/env python3
"""
Drift detector: warn when a newly added .py file duplicates existing top-level API.

For each Added .py in the PR diff, extract top-level function/class signatures via AST
and search the rest of the repo for matching name + positional arg count (functions)
or class name (classes).

Run:
  PYTHONPATH=. python3 scripts/ci/check_duplicate_modules.py --base origin/main --head HEAD

Exit: 0 always (warnings only); emits ::warning:: for candidate duplicates.
"""
from __future__ import annotations

import argparse
import ast
import sys
from dataclasses import dataclass
from pathlib import Path

from drift_detector_git import added_paths, repo_root_from_script

REPO_ROOT = repo_root_from_script(Path(__file__))
_GH_WARN_PREFIX = "::warning::"

SKIP_DIR_NAMES = {".git", "__pycache__", ".venv", "node_modules", ".mypy_cache"}
SKIP_FILE_SUFFIXES = ("_test.py", "test_.py", "conftest.py")


@dataclass(frozen=True)
class Signature:
    kind: str  # "function" | "class"
    name: str
    arg_count: int | None  # None for classes


@dataclass
class DuplicateHit:
    new_file: str
    new_line: int
    signature: Signature
    existing_file: str
    existing_line: int


def should_skip_file(path: Path) -> bool:
    name = path.name
    if name == "__init__.py":
        return True
    if any(name.endswith(s) for s in SKIP_FILE_SUFFIXES):
        return True
    return False


def extract_signatures(source: str, filename: str = "<unknown>") -> list[tuple[Signature, int]]:
    try:
        tree = ast.parse(source, filename=filename)
    except SyntaxError:
        return []
    out: list[tuple[Signature, int]] = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            argc = len(node.args.args)
            if node.args.args and node.args.args[0].arg in ("self", "cls"):
                argc -= 1
            out.append((Signature("function", node.name, max(0, argc)), node.lineno))
        elif isinstance(node, ast.ClassDef):
            out.append((Signature("class", node.name, None), node.lineno))
    return out


def iter_py_files(repo_root: Path) -> list[Path]:
    files: list[Path] = []
    for path in repo_root.rglob("*.py"):
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        if should_skip_file(path):
            continue
        files.append(path)
    return files


def build_index(repo_root: Path, exclude: Path | None = None) -> dict[Signature, list[tuple[str, int]]]:
    index: dict[Signature, list[tuple[str, int]]] = {}
    for path in iter_py_files(repo_root):
        if exclude and path.resolve() == exclude.resolve():
            continue
        rel = path.relative_to(repo_root).as_posix()
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for sig, line in extract_signatures(text, rel):
            index.setdefault(sig, []).append((rel, line))
    return index


def find_duplicates(repo_root: Path, new_rel: str, index: dict[Signature, list[tuple[str, int]]]) -> list[DuplicateHit]:
    path = repo_root / new_rel
    if not path.is_file() or should_skip_file(path):
        return []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    hits: list[DuplicateHit] = []
    for sig, line in extract_signatures(text, new_rel):
        for existing_file, existing_line in index.get(sig, []):
            if existing_file == new_rel:
                continue
            hits.append(
                DuplicateHit(
                    new_file=new_rel,
                    new_line=line,
                    signature=sig,
                    existing_file=existing_file,
                    existing_line=existing_line,
                )
            )
    return hits


def emit_warnings(hits: list[DuplicateHit]) -> int:
    if not hits:
        print("DUPLICATE MODULES: PASS", file=sys.stderr)
        return 0
    for h in hits:
        if h.signature.kind == "function":
            sig_desc = f"function {h.signature.name}({h.signature.arg_count} args)"
        else:
            sig_desc = f"class {h.signature.name}"
        msg = (
            f"{h.new_file}:{h.new_line}: new {sig_desc} may duplicate "
            f"{h.existing_file}:{h.existing_line}"
        )
        print(f"{_GH_WARN_PREFIX}{msg}", file=sys.stderr)
    print(f"DUPLICATE MODULES: {len(hits)} warning(s) (non-blocking)", file=sys.stderr)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Warn on new .py files duplicating existing top-level API")
    ap.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    ap.add_argument("--base", default=None, help="Git base ref for PR diff")
    ap.add_argument("--head", default="HEAD")
    ap.add_argument(
        "--new-files",
        nargs="*",
        default=None,
        help="Explicit new .py paths (for tests; bypasses git diff)",
    )
    args = ap.parse_args()
    repo_root = args.repo_root

    if args.new_files:
        new_py = [p for p in args.new_files if p.endswith(".py")]
    else:
        new_py = [p for p in added_paths(args.base, args.head, repo_root) if p.endswith(".py")]

    if not new_py:
        print("DUPLICATE MODULES: PASS (no new .py files)", file=sys.stderr)
        return 0

    all_hits: list[DuplicateHit] = []
    for rel in sorted(set(new_py)):
        exclude = (repo_root / rel).resolve()
        index = build_index(repo_root, exclude=exclude)
        all_hits.extend(find_duplicates(repo_root, rel, index))

    return emit_warnings(all_hits)


if __name__ == "__main__":
    sys.exit(main())
