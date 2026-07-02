#!/usr/bin/env python3
"""
Drift detector: production-context run_pipeline.py invocations must pass the CANONICAL
FOUR-PIECE CHORD — --pipeline-mode spine --quality-profile production --exercise-journeys
(--render-book is the invocation trigger, not scored as a chord flag).

G3 (render-hardening 2026-07-02): bestseller / catalog builds only reach bestseller
register on the spine+production+exercise-journeys path. A build that renders a book but
omits any chord flag silently falls back to the fast registry path or a non-production
profile and ships choppy / gate-skipped output. This gate grep-asserts the chord at
every production invocation site.

Scans PR-touched files under scripts/**, .github/workflows/**, docs/** for
scripts/run_pipeline.py (not scripts/video/run_pipeline.py). Production context
is workflow files, book-output flags (--render-book, --quality-profile, --render-dir),
or docs shell examples.

Chord flags checked (each missing flag is a separate violation reason):
  --pipeline-mode spine        (REQUIRED — canonical bestseller path)
  --quality-profile production (REQUIRED — all gates run at production severity)
  --exercise-journeys          (REQUIRED — canonical production invocation)

Allowlist: preceding-line or same-line comment
  # CI-ALLOWLIST: legacy-registry-ok — <reason>   (skips ALL chord checks for that block)

Kill-switch: CANONICAL_PIPELINE_CHORD_FULL=0 reverts to spine-flag-only checking
(the pre-G3 behavior) for the whole run.

Run:
  PYTHONPATH=. python3 scripts/ci/check_canonical_pipeline_path.py \\
    --base origin/main --head HEAD --gate-mode fail

Exit: 0 pass; 1 fail when --gate-mode fail and violations (CI default since 2026-07-02).
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

# G3 — the canonical four-piece chord. --render-book is the invocation trigger, so it is
# a production marker (above) rather than a scored chord flag. Each of these three must
# appear in a production run_pipeline invocation block.
#
# --quality-profile: accept the literal `production` OR a variable value ($VAR / "$VAR" /
# {var} / ${{ ... }}) — production is the parameterized default and workflows legitimately
# thread it through an input. A wrapper that OMITS the flag entirely (default flagship/…)
# is still caught. A literal non-production value (draft/debug) is NOT accepted.
QUALITY_PROFILE_OK_RE = re.compile(
    r"--quality-profile(?:=|\s+)"
    r"(?:production\b|['\"]?[$][{(]|['\"]?[$]\w|['\"]?\{)"
)
EXERCISE_JOURNEYS_RE = re.compile(r"--exercise-journeys\b")
# (flag_regex, human name, missing-reason)
CHORD_CHECKS = (
    (SPINE_MODE_RE, "--pipeline-mode spine", "missing --pipeline-mode spine"),
    (
        QUALITY_PROFILE_OK_RE,
        "--quality-profile production",
        "missing --quality-profile production (or a variable resolving to it)",
    ),
    (EXERCISE_JOURNEYS_RE, "--exercise-journeys", "missing --exercise-journeys"),
)


def full_chord_enabled() -> bool:
    """G3 kill-switch: CANONICAL_PIPELINE_CHORD_FULL=0 reverts to spine-flag-only checks."""
    flag = (os.environ.get("CANONICAL_PIPELINE_CHORD_FULL") or "").strip().lower()
    return flag not in ("0", "false", "off", "no")


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
    """Return (block_text, start_line_1based, end_line_1based) for a run_pipeline invocation.

    Follows two continuation styles so the whole invocation (and its flags) is captured:
      - Python list/call: bracket depth > 0 keeps the block open.
      - Shell backslash: a line ending in `\\` continues onto the next line. This must be
        honored BEFORE the depth-based break, otherwise a bare `python … run_pipeline.py \`
        line (depth 0) would truncate the block at the next line and drop every flag on the
        continuation (e.g. `--pipeline-mode spine` two lines down). [G3 fix, 2026-07-02]
    """
    end = start
    depth = 0
    started = False
    prev_continues = False  # previous collected line ended with a shell backslash
    # Python-list invocations often open `cmd = [` on a line ABOVE the run_pipeline.py entry
    # (`sys.executable, str(REPO/"scripts/run_pipeline.py"),`). Detect that by looking a few
    # lines up for an unclosed `[` / `(`, so the trailing flag items are collected. [G3]
    list_open = False
    for j in range(max(0, start - 3), start):
        opens = lines[j].count("[") + lines[j].count("(")
        closes = lines[j].count("]") + lines[j].count(")")
        if opens > closes:
            list_open = True
    for i in range(start, min(start + 60, len(lines))):
        line = lines[i]
        if not started:
            if "run_pipeline.py" not in line:
                continue
            started = True
            end = i
        else:
            end = i
        depth += line.count("(") + line.count("[") - line.count(")") - line.count("]")
        this_continues = line.rstrip().endswith("\\")
        # Keep the block open while the previous line continued via `\` or brackets are open.
        if this_continues:
            prev_continues = True
            continue
        if prev_continues:
            prev_continues = False
            if depth <= 0 and not list_open:
                break
            continue
        # Python-list mode: keep collecting items until the list closes (a line whose net
        # bracket delta drops the accumulated depth to the point the list `]` is seen).
        if list_open:
            if "]" in line and depth < 0:
                break
            continue
        if started and depth <= 0 and i > start:
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


_PYLIST_SEP_RE = re.compile(r"[\"'],\s*[\"']")


def normalize_block_for_flags(block: str) -> str:
    """Collapse Python-list arg separators so `"--flag", "value"` reads as `--flag value`.

    Shell/workflow invocations write `--flag value` inline; Python orchestration wrappers
    split them into adjacent list items (`"--pipeline-mode", "spine",`). Normalizing lets one
    flag-regex set match BOTH syntaxes so batch_*.py wrappers are checked too. [G3]
    """
    collapsed = _PYLIST_SEP_RE.sub(" ", block)
    # strip any remaining surrounding quotes on bare tokens so `--exercise-journeys"` matches
    collapsed = collapsed.replace('",', " ").replace("',", " ")
    return collapsed


def has_spine_mode(block: str) -> bool:
    return bool(SPINE_MODE_RE.search(normalize_block_for_flags(block)))


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
        snippet = block.strip().replace("\n", " ")[:160]
        # Normalize once so Python-list (`"--flag", "val"`) and shell (`--flag val`) forms
        # both match the chord regexes.
        norm_block = normalize_block_for_flags(block)
        if full_chord_enabled():
            # G3: every chord flag must be present. Report each missing flag separately.
            missing_reasons: list[str] = []
            for flag_re, _name, reason in CHORD_CHECKS:
                if not flag_re.search(norm_block):
                    if flag_re is SPINE_MODE_RE and REGISTRY_MODE_RE.search(norm_block):
                        missing_reasons.append("missing --pipeline-mode spine (uses registry explicitly)")
                    else:
                        missing_reasons.append(reason)
            if not missing_reasons:
                continue
            violations.append(
                Violation(
                    file=rel_path,
                    line=start_line,
                    snippet=snippet,
                    reason="incomplete bestseller chord: " + "; ".join(missing_reasons),
                )
            )
        else:
            # Kill-switch path: pre-G3 spine-flag-only behavior.
            if has_spine_mode(block):
                continue
            mode_hint = "registry (explicit)" if REGISTRY_MODE_RE.search(block) else "registry (default)"
            violations.append(
                Violation(
                    file=rel_path,
                    line=start_line,
                    snippet=snippet,
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
