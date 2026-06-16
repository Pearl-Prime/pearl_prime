#!/usr/bin/env python3
"""
Drift detector: production-context run_pipeline.py invocations must use --pipeline-mode spine.

Scans PR-touched files under scripts/**, .github/workflows/**, docs/** for
scripts/run_pipeline.py (not scripts/video/run_pipeline.py). Production context
is workflow files, book-output flags (--render-book, --quality-profile, --render-dir),
or docs shell examples.

Allowlist: preceding-line or same-line comment
  # CI-ALLOWLIST: legacy-registry-ok — <reason>

Run:
  PYTHONPATH=. python3 scripts/ci/check_canonical_pipeline_path.py \\
    --base origin/main --head HEAD --gate-mode warn

Exit: 0 pass or pass-with-warnings; 1 fail (when --gate-mode fail and violations).
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from drift_detector_git import changed_paths, repo_root_from_script

REPO_ROOT = repo_root_from_script(Path(__file__))
_GH_WARN_PREFIX = "::warning::"

SCAN_PREFIXES = ("scripts/", ".github/workflows/", "docs/")
DEV_PATH_PREFIXES = (
    "scripts/systems_test/",
    "scripts/canary/",
    "scripts/pilot/",
    "tests/",
)
PRODUCTION_MARKERS = ("--render-book", "--quality-profile", "--render-dir")
ALLOWLIST_MARKER = "CI-ALLOWLIST: legacy-registry-ok"
SPINE_MODE_RE = re.compile(r"--pipeline-mode(?:=|\s+)spine\b")
REGISTRY_MODE_RE = re.compile(r"--pipeline-mode(?:=|\s+)registry\b")


def line_has_canonical_run_pipeline(line: str) -> bool:
    if "run_pipeline.py" not in line.lower():
        return False
    return "video/run_pipeline.py" not in line.replace("\\", "/").lower()


@dataclass
class Violation:
    file: str
    line: int
    snippet: str
    reason: str


def resolve_gate_mode(cli: str | None) -> str:
    if cli is not None:
        return cli
    env = (os.environ.get("CANONICAL_PIPELINE_GATE_MODE") or "").strip().lower()
    if env in ("warn", "fail"):
        return env
    return "warn"


def in_scan_scope(path: str) -> bool:
    return any(path.startswith(p) for p in SCAN_PREFIXES)


def is_dev_path(path: str) -> bool:
    return any(path.startswith(p) for p in DEV_PATH_PREFIXES)


def is_allowlisted(lines: list[str], idx: int) -> bool:
    for j in range(max(0, idx - 2), idx + 1):
        if j < len(lines) and ALLOWLIST_MARKER in lines[j]:
            return True
    return False


def collect_invocation_block(lines: list[str], start: int) -> tuple[str, int, int]:
    """Return (block_text, start_line_1based, end_line_1based) for a run_pipeline invocation."""
    end = start
    depth = 0
    started = False
    for i in range(start, min(start + 40, len(lines))):
        line = lines[i]
        if not started:
            if "run_pipeline.py" not in line:
                continue
            started = True
            end = i
        else:
            end = i
        depth += line.count("(") + line.count("[") - line.count(")") - line.count("]")
        if started and depth <= 0 and i > start:
            break
        if started and line.rstrip().endswith("\\"):
            continue
        if started and depth <= 0:
            break
    block = "\n".join(lines[start : end + 1])
    return block, start + 1, end + 1


def is_production_context(path: str, block: str) -> bool:
    if path.startswith(".github/workflows/"):
        return True
    if is_dev_path(path):
        return False
    if any(marker in block for marker in PRODUCTION_MARKERS):
        return True
    if path.startswith("docs/"):
        return True
    return False


def has_spine_mode(block: str) -> bool:
    return bool(SPINE_MODE_RE.search(block))


def scan_file(repo_root: Path, rel_path: str) -> list[Violation]:
    path = repo_root / rel_path
    if not path.is_file():
        return []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    lines = text.splitlines()
    violations: list[Violation] = []
    for i, line in enumerate(lines):
        if not line_has_canonical_run_pipeline(line):
            continue
        if is_allowlisted(lines, i):
            continue
        block, start_line, _end_line = collect_invocation_block(lines, i)
        if not is_production_context(rel_path, block):
            continue
        if has_spine_mode(block):
            continue
        mode_hint = "registry (explicit)" if REGISTRY_MODE_RE.search(block) else "registry (default)"
        violations.append(
            Violation(
                file=rel_path,
                line=start_line,
                snippet=block.strip().replace("\n", " ")[:160],
                reason=f"missing --pipeline-mode spine; would use {mode_hint}",
            )
        )
    return violations


def emit_violations(violations: list[Violation], gate_mode: str) -> int:
    if not violations:
        print("CANONICAL PIPELINE PATH: PASS", file=sys.stderr)
        return 0
    for v in violations:
        msg = f"{v.file}:{v.line}: {v.reason} — {v.snippet}"
        if gate_mode == "warn":
            print(f"{_GH_WARN_PREFIX}{msg}", file=sys.stderr)
        else:
            print(f"FAIL: {msg}", file=sys.stderr)
    summary = f"CANONICAL PIPELINE PATH: {len(violations)} violation(s)"
    if gate_mode == "warn":
        print(f"{summary} (warn mode — exit 0)", file=sys.stderr)
        return 0
    print(f"{summary} — blocking", file=sys.stderr)
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Detect non-spine run_pipeline.py in production contexts")
    ap.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    ap.add_argument("--base", default=None, help="Git base ref for PR diff (e.g. origin/main)")
    ap.add_argument("--head", default="HEAD", help="Git head ref")
    ap.add_argument("--gate-mode", choices=("warn", "fail"), default=None)
    ap.add_argument(
        "--paths",
        nargs="*",
        default=None,
        help="Explicit paths to scan (bypasses git diff; for tests)",
    )
    args = ap.parse_args()
    gate_mode = resolve_gate_mode(args.gate_mode)
    repo_root = args.repo_root

    if args.paths:
        targets = [p for p in args.paths if in_scan_scope(p.replace("\\", "/"))]
    else:
        targets = [p for p in changed_paths(args.base, args.head, repo_root) if in_scan_scope(p)]

    violations: list[Violation] = []
    for rel in sorted(set(targets)):
        violations.extend(scan_file(repo_root, rel))
    return emit_violations(violations, gate_mode)


if __name__ == "__main__":
    sys.exit(main())
