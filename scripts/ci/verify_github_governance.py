#!/usr/bin/env python3
"""
Verify GitHub governance: ruleset targets main only, required checks match policy,
PR-only merge, no bypass scripts, no token files. Reads config from
config/governance/required_checks.yaml.

Modes:
  --mode local   Repo-only checks (no API). Always runnable in CI.
  --mode api     Ruleset + required checks via API. Needs GITHUB_TOKEN with ruleset read.
  --strict       In api mode, exit 1 if token missing (default: exit 0 with warning).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "config" / "governance" / "required_checks.yaml"
SCRIPTS_CI = REPO_ROOT / "scripts" / "ci"
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"
FORBIDDEN_FILES = (".github_token", "github_access_token.rtf")
# Script-level bypass indicators only. Do not match bare API field names like
# bypass_actors (legitimate in ruleset readers, e.g. check_branch_protection_ruleset.py).
FORBIDDEN_BYPASS_SCRIPT_PATTERNS = (
    re.compile(r'enforcement\s*:\s*["\']disabled["\']', re.I),
    re.compile(r'["\']bypass_mode["\']\s*:\s*["\']always["\']', re.I),
    re.compile(r'\bbypass_mode\s*=\s*["\']always["\']', re.I),
)


def text_has_forbidden_bypass_logic(text: str) -> bool:
    """True if *text* looks like code that weakens rulesets (not API field reads)."""
    return any(p.search(text) for p in FORBIDDEN_BYPASS_SCRIPT_PATTERNS)


def load_config() -> dict:
    if not CONFIG_PATH.is_file():
        return {}
    data = {
        "version": 2,
        "required_checks": [],
        "always_required": ["Core tests"],
        "path_filtered_optional": [],
        "non_blocking_checks": [],
        "forbidden_legacy_checks": [],
        "allowed_required_integrations": [],
    }
    try:
        with open(CONFIG_PATH) as f:
            section: str | None = None
            for line in f:
                s = line.strip()
                if not s or s.startswith("#"):
                    continue
                if s.startswith("required_checks:"):
                    section = "required_checks"
                    continue
                if s.startswith("always_required:"):
                    section = "always_required"
                    continue
                if s.startswith("path_filtered_optional:"):
                    section = "path_filtered_optional"
                    continue
                if s.startswith("non_blocking_checks:"):
                    section = "non_blocking_checks"
                    continue
                if s.startswith("forbidden_legacy_checks:"):
                    section = "forbidden_legacy_checks"
                    continue
                if s.startswith("allowed_required_integrations:"):
                    section = "allowed_required_integrations"
                    continue
                if section and s.startswith("- "):
                    value = s[2:].strip(' "\t')
                    if section == "allowed_required_integrations":
                        data.setdefault(section, []).append(int(value))
                    else:
                        data.setdefault(section, []).append(value)
    except Exception:
        pass
    for key, value in list(data.items()):
        if isinstance(value, list):
            data[key] = list(dict.fromkeys(value))
    return data


def parse_yaml_name(line: str) -> str | None:
    match = re.match(r"^\s*name:\s*(.+?)\s*$", line)
    if not match:
        return None
    return match.group(1).strip().strip('"').strip("'")


def collect_workflow_check_names() -> set[str]:
    checks: set[str] = set()
    for wf in sorted(WORKFLOWS_DIR.glob("*.yml")):
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


def check_policy_files_present() -> bool:
    ok = True
    if not CONFIG_PATH.is_file():
        print(f"  FAIL: Missing {CONFIG_PATH}")
        ok = False
    else:
        print(f"  PASS: {CONFIG_PATH} present")
    gov_doc = REPO_ROOT / "docs" / "GITHUB_GOVERNANCE.md"
    if not gov_doc.is_file():
        print(f"  FAIL: Missing {gov_doc}")
        ok = False
    else:
        print(f"  PASS: {gov_doc} present")
    return ok


def check_no_bypass_scripts() -> bool:
    ok = True
    if not SCRIPTS_CI.is_dir():
        return True
    for f in SCRIPTS_CI.glob("*.py"):
        if f.name == "verify_github_governance.py":
            continue
        if "bypass" in f.name.lower() and "no_bypass" not in f.name.lower():
            print(f"  FAIL: Bypass script not allowed: {f.name}")
            ok = False
        else:
            try:
                text = f.read_text()
                if text_has_forbidden_bypass_logic(text):
                    print(f"  FAIL: Bypass logic in {f.name}")
                    ok = False
            except Exception:
                pass
    if ok:
        print("  PASS: No bypass scripts or logic")
    return ok


def check_no_token_files() -> bool:
    ok = True
    for name in FORBIDDEN_FILES:
        p = REPO_ROOT / name
        if p.is_file():
            print(f"  FAIL: Token file must be removed: {name}")
            ok = False
    for p in REPO_ROOT.glob("*.rtf"):
        if "token" in p.name.lower() or "github" in p.name.lower():
            print(f"  FAIL: Token file must be removed: {p.name}")
            ok = False
    if ok:
        print("  PASS: No token files in repo")
    return ok


def run_local() -> bool:
    print("[local] Policy files present")
    a = check_policy_files_present()
    print("[local] No bypass scripts")
    b = check_no_bypass_scripts()
    print("[local] No token files")
    c = check_no_token_files()
    print("[local] Required checks match workflow-emitted names")
    d = check_required_names_exist()
    return a and b and c and d


def check_required_names_exist() -> bool:
    config = load_config()
    required = config.get("required_checks") or []
    available = collect_workflow_check_names()
    ok = True
    for check in required:
        if check in available:
            print(f"  PASS: required check emitted by workflow/job name: {check}")
        else:
            print(f"  FAIL: required check not emitted by workflows: {check}")
            ok = False
    return ok


def api_get(token: str, path: str) -> dict | list:
    url = f"https://api.github.com/repos/Ahjan108/phoenix_omega_v4.8{path}"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())


def ruleset_targets_main(detail: dict) -> bool:
    cond = detail.get("conditions", {}) or {}
    ref = cond.get("ref_name", {}) or {}
    include = ref.get("include") or []
    if not include:
        return True
    return set(include).issubset({"refs/heads/main", "~DEFAULT_BRANCH"})


def normalize_contexts(detail: dict) -> list[dict]:
    for rule in detail.get("rules") or []:
        if isinstance(rule, dict) and rule.get("type") == "required_status_checks":
            params = rule.get("parameters") or {}
            return list(params.get("required_status_checks") or [])
    return []


def run_api(strict: bool) -> bool:
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not token:
        try:
            out = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, timeout=5)
            if out.returncode == 0 and out.stdout:
                token = out.stdout.strip()
        except Exception:
            pass
    if not token:
        msg = "Skipping API checks (no GITHUB_TOKEN). Use --mode local only or set GITHUB_TOKEN."
        if strict:
            print(f"  FAIL: {msg}", file=sys.stderr)
            return False
        print(f"  WARN: {msg}")
        return True
    config = load_config()
    required = config.get("required_checks") or []
    always = config.get("always_required") or ["Core tests"]
    non_blocking = set(config.get("non_blocking_checks") or [])
    forbidden_legacy = set(config.get("forbidden_legacy_checks") or [])
    allowed_integrations = set(config.get("allowed_required_integrations") or [])
    available = collect_workflow_check_names()
    ok = True
    try:
        rulesets = api_get(token, "/rulesets")
        if not isinstance(rulesets, list):
            rulesets = [rulesets]
        active_main_rulesets: list[dict] = []
        for rs in rulesets:
            # List endpoint can be partial; fetch detail by id for reliable rule checks.
            rs_id = rs.get("id")
            detail = rs
            if rs_id is not None:
                try:
                    full = api_get(token, f"/rulesets/{rs_id}")
                    if isinstance(full, dict):
                        detail = full
                except Exception:
                    # Fall back to list payload if detail fetch is unavailable.
                    pass

            name = detail.get("name", rs.get("name", "?"))
            if ruleset_targets_main(detail):
                print(f"  PASS: Ruleset {name} targets main only")
                if detail.get("enforcement") == "active":
                    active_main_rulesets.append(detail)
            else:
                cond = detail.get("conditions", {}) or {}
                ref = cond.get("ref_name", {}) or {}
                include = ref.get("include") or []
                print(f"  FAIL: Ruleset {name} does not target main only: {include}")
                ok = False
            rules = detail.get("rules") or []
            has_pr = any(isinstance(r, dict) and r.get("type") == "pull_request" for r in rules)
            if has_pr:
                print(f"  PASS: Ruleset {name} requires PR before merge")
            else:
                print(f"  FAIL: Ruleset {name} must require PR before merge")
                ok = False
        if not active_main_rulesets:
            print("  FAIL: No active ruleset applies to main")
            ok = False
        expected = set(required)
        unique_sets: dict[tuple[str, ...], list[str]] = {}
        for detail in active_main_rulesets:
            name = detail.get("name", "?")
            contexts = normalize_contexts(detail)
            context_names = [ctx.get("context", "").strip() for ctx in contexts if ctx.get("context")]
            context_set = set(context_names)
            unique_sets.setdefault(tuple(sorted(context_set)), []).append(name)

            if context_set == expected:
                print(f"  PASS: Ruleset {name} requires canonical contexts")
            else:
                print(
                    f"  FAIL: Ruleset {name} required contexts {sorted(context_set)} "
                    f"do not match canonical {sorted(expected)}"
                )
                ok = False

            for context in context_names:
                if context in forbidden_legacy:
                    print(f"  FAIL: Ruleset {name} still requires forbidden legacy context: {context}")
                    ok = False
                if context in non_blocking:
                    print(f"  FAIL: Ruleset {name} requires non-blocking context: {context}")
                    ok = False
                if context not in available:
                    print(f"  FAIL: Ruleset {name} requires context not emitted by workflows: {context}")
                    ok = False

            for item in contexts:
                integration_id = item.get("integration_id")
                if integration_id is None:
                    continue
                if allowed_integrations and integration_id not in allowed_integrations:
                    print(
                        f"  FAIL: Ruleset {name} requires context {item.get('context')} "
                        f"from unexpected integration_id={integration_id}"
                    )
                    ok = False

        if len(unique_sets) == 1:
            only_set = next(iter(unique_sets))
            owners = next(iter(unique_sets.values()))
            print(
                f"  PASS: Active main rulesets share one required-check set: "
                f"{list(only_set)} across {', '.join(owners)}"
            )
        else:
            print("  FAIL: Active main rulesets have conflicting required-check sets:")
            for contexts, names in unique_sets.items():
                print(f"    {names}: {list(contexts)}")
            ok = False
    except urllib.error.HTTPError as e:
        print(f"  WARN: Could not read rulesets ({e.code}). Run with token that has ruleset read.")
        if strict:
            ok = False
    except Exception as e:
        print(f"  WARN: API error: {e}")
        if strict:
            ok = False
    print("  INFO: Canonical required checks:", required)
    print("  INFO: Always-required checks:", always)
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify GitHub governance")
    ap.add_argument("--mode", choices=("local", "api", "all"), default="all", help="local=repo-only, api=API checks, all=both")
    ap.add_argument("--strict", action="store_true", help="In api mode, fail if token missing")
    args = ap.parse_args()
    ok = True
    if args.mode in ("local", "all"):
        ok = run_local() and ok
    if args.mode in ("api", "all"):
        ok = run_api(args.strict) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
