#!/usr/bin/env python3
"""
Validate that required check names in config/governance/required_checks.yaml
match real workflow/job check names emitted by GitHub Actions.
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG = REPO_ROOT / "config" / "governance" / "required_checks.yaml"
WORKFLOWS = REPO_ROOT / ".github" / "workflows"


def load_checks() -> tuple[list[str], list[str]]:
    required: list[str] = []
    optional: list[str] = []
    in_always = False
    in_optional = False
    for raw in CONFIG.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("always_required:"):
            in_always = True
            in_optional = False
            continue
        if line.startswith("path_filtered_optional:"):
            in_always = False
            in_optional = True
            continue
        if (in_always or in_optional) and not raw.startswith("  - "):
            if not raw.startswith(" "):
                break
        if (in_always or in_optional) and line.startswith("- "):
            name = line[2:].strip().strip('"')
            if name:
                if in_always:
                    required.append(name)
                elif in_optional:
                    optional.append(name)
    return required, optional


def collect_available_checks() -> set[str]:
    checks: set[str] = set()
    for wf in sorted(WORKFLOWS.glob("*.yml")):
        text = wf.read_text(encoding="utf-8")
        in_jobs = False
        for raw in text.splitlines():
            line = raw.rstrip("\n")
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if line.startswith("name:"):
                checks.add(line.split(":", 1)[1].strip().strip('"'))
                continue
            if line.startswith("jobs:"):
                in_jobs = True
                continue
            if in_jobs:
                if not line.startswith("  "):
                    in_jobs = False
                    continue
                if line.startswith("  ") and not line.startswith("    ") and stripped.endswith(":"):
                    checks.add(stripped[:-1])
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
