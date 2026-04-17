#!/usr/bin/env python3
"""Scan repository sources for banned paid-LLM API usage."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".claude",
    ".cursor",
    "fonts",
    "image_bank",
    "artifacts",
    ".mypy_cache",
    "dist",
    "build",
}
SKIP_PREFIXES = (".claude/",)


def _should_skip(path: Path) -> bool:
    rel = path.relative_to(REPO_ROOT)
    parts = rel.parts
    if any(p in SKIP_DIRS for p in parts):
        return True
    s = str(rel).replace("\\", "/")
    return any(s.startswith(p) for p in SKIP_PREFIXES)


def _iter_files(roots: list[Path]) -> list[Path]:
    out: list[Path] = []
    for root in roots:
        if root.is_file():
            if root.suffix in {".py", ".yaml", ".yml"}:
                out.append(root)
            continue
        if not root.is_dir():
            continue
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            if p.suffix not in {".py", ".yaml", ".yml"}:
                continue
            if _should_skip(p):
                continue
            out.append(p)
    return sorted(set(out))


def _path_exempt(rel_posix: str, exempt_paths: list[str]) -> bool:
    for ex in exempt_paths or []:
        exn = ex.replace("\\", "/").rstrip("/")
        if exn and (rel_posix == exn or rel_posix.startswith(exn + "/")):
            return True
    return False


def _line_allowed(line: str, subs: list[str] | None) -> bool:
    if not subs:
        return False
    low = line.lower()
    return any(s.lower() in low for s in subs)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--banned-patterns-file", type=Path, required=True)
    ap.add_argument("--allowed-patterns-file", type=Path, default=None)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--roots", nargs="*", help="Limit scan to these roots (repo-relative or absolute)")
    ap.add_argument("--fail-on-violation", action="store_true")
    args = ap.parse_args()

    banned_cfg = yaml.safe_load(args.banned_patterns_file.read_text(encoding="utf-8")) or {}
    global_exempt = list(banned_cfg.get("global_exempt_prefixes") or [])
    rules = banned_cfg.get("banned_patterns") or {}
    rule_items = list(rules.items()) if isinstance(rules, dict) else []

    roots: list[Path] = []
    if args.roots:
        for r in args.roots:
            p = Path(r)
            if not p.is_absolute():
                p = REPO_ROOT / p
            roots.append(p.resolve())
    else:
        roots.append(REPO_ROOT)

    files = _iter_files(roots)
    violations: list[dict[str, object]] = []

    for rule_name, spec in rule_items:
        if not isinstance(spec, dict):
            continue
        pattern = spec.get("regex") or ""
        reason = spec.get("reason") or ""
        exempt_paths = list(spec.get("exempt_paths") or [])
        line_allow = list(spec.get("line_allow_substrings") or [])
        try:
            rx = re.compile(pattern, re.MULTILINE | re.DOTALL)
        except re.error as e:
            print(f"Invalid regex for {rule_name}: {e}", file=sys.stderr)
            return 2

        for path in files:
            rel = path.relative_to(REPO_ROOT).as_posix()
            if _path_exempt(rel, global_exempt) or _path_exempt(rel, exempt_paths):
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for m in rx.finditer(text):
                start = m.start()
                line_no = text.count("\n", 0, start) + 1
                line_start = text.rfind("\n", 0, start) + 1
                line_end = text.find("\n", start)
                if line_end < 0:
                    line_end = len(text)
                line = text[line_start:line_end]
                if line_allow and _line_allowed(line, line_allow):
                    continue
                snippet = m.group(0).strip().replace("\n", " ")[:200]
                violations.append(
                    {
                        "rule": rule_name,
                        "path": rel,
                        "line": line_no,
                        "snippet": snippet,
                        "reason": reason,
                    }
                )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# LLM callers audit",
        "",
        f"- Violations: **{len(violations)}**",
        f"- Files scanned: **{len(files)}**",
        "",
    ]
    for v in violations:
        lines.append(f"## `{v['path']}`:{v['line']} — `{v['rule']}`")
        lines.append("")
        lines.append(f"- Reason: {v['reason']}")
        lines.append(f"- Snippet: `{v['snippet']}`")
        lines.append("")
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    summary_path = args.output.parent / "llm_audit_summary.json"
    summary_path.write_text(
        json.dumps({"violation_count": len(violations), "violations": violations}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"violation_count": len(violations)}, indent=2))
    if args.fail_on_violation and violations:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
