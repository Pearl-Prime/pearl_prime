#!/usr/bin/env python3
"""
Validate that required check names in config/governance/required_checks.yaml
match real workflow/job check names emitted by GitHub Actions.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG = REPO_ROOT / "config" / "governance" / "required_checks.yaml"
WORKFLOWS = REPO_ROOT / ".github" / "workflows"


def load_checks() -> tuple[list[str], list[str]]:
    required: list[str] = []
    optional: list[str] = []
    in_required = False
    in_optional = False
    for raw in CONFIG.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("required_checks:"):
            in_required = True
            in_optional = False
            continue
        if line.startswith("path_filtered_optional:"):
            in_required = False
            in_optional = True
            continue
        if (in_required or in_optional) and not raw.startswith("  - "):
            if not raw.startswith(" "):
                break
        if (in_required or in_optional) and line.startswith("- "):
            name = line[2:].strip().strip('"')
            if name:
                if in_required:
                    required.append(name)
                elif in_optional:
                    optional.append(name)
    return required, optional


def parse_yaml_name(line: str) -> str | None:
    match = re.match(r"^\s*name:\s*(.+?)\s*$", line)
    if not match:
        return None
    return match.group(1).strip().strip('"').strip("'")


def collect_available_checks() -> set[str]:
    checks: set[str] = set()
    for wf in sorted(WORKFLOWS.glob("*.yml")):
        lines = wf.read_text(encoding="utf-8").splitlines()
        in_jobs = False
        current_job_indent: int | None = None
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if not in_jobs and line.startswith("name:"):
                workflow_name = parse_yaml_name(line)
                if workflow_name:
                    checks.add(workflow_name)
                continue
            if line.startswith("jobs:"):
                in_jobs = True
                continue
            if in_jobs:
                if not line.startswith("  "):
                    in_jobs = False
                    current_job_indent = None
                    continue
                indent = len(line) - len(line.lstrip(" "))
                if indent == 2 and stripped.endswith(":"):
                    current_job_indent = 2
                    continue
                if current_job_indent == 2 and indent == 4:
                    job_name = parse_yaml_name(line)
                    if job_name:
                        checks.add(job_name)
                        current_job_indent = None
    return checks


def main() -> int:
    try:
        required, optional = load_checks()
        available = collect_available_checks()
    except Exception as e:
        print(f"FAIL: unable to parse governance/workflow files: {e}")
        return 1

    missing = [c for c in required if c not in available]
    if missing:
        print("FAIL: required checks do not match any workflow/job names:")
        for m in missing:
            print(f"  - {m}")
        print("INFO: sample available names:")
        for n in sorted(list(available))[:40]:
            print(f"  * {n}")
        return 1

    missing_optional = [c for c in optional if c not in available]
    if missing_optional:
        print("WARN: optional path-filtered check names do not currently match workflow/job names:")
        for m in missing_optional:
            print(f"  - {m}")

    print(f"PASS: {len(required)} required checks matched workflow/job names")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
