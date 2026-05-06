#!/usr/bin/env python3
"""Periodic check: verify branch protection ruleset 13451138 stays hardened.

Per the 2026-05-05 origin/main rewind incident
(artifacts/qa/origin_main_rewind_incident_2026-05-06.md), the ruleset
must enforce:
  - bypass_actors[].bypass_mode == "pull_request" (NOT "always")
  - non_fast_forward rule active
  - required_linear_history rule active

Run from CI on a daily cron, or manually:
    python3 scripts/ci/check_branch_protection_ruleset.py

Exits 0 if hardened; non-zero if drift detected (with reason).
"""
from __future__ import annotations

import json
import subprocess
import sys

REPO = "Ahjan108/phoenix_omega_v4.8"
RULESET_ID = "13451138"
REQUIRED_RULES = {"non_fast_forward", "required_linear_history", "pull_request"}
EXPECTED_BYPASS_MODE = "pull_request"


def main() -> int:
    try:
        out = subprocess.run(
            ["gh", "api", f"/repos/{REPO}/rulesets/{RULESET_ID}"],
            capture_output=True, text=True, check=True,
        )
    except subprocess.CalledProcessError as exc:
        print(f"FAIL: gh api error: {exc.stderr}", file=sys.stderr)
        return 2

    try:
        data = json.loads(out.stdout)
    except json.JSONDecodeError as exc:
        print(f"FAIL: invalid JSON from gh api: {exc}", file=sys.stderr)
        return 2

    failures = []

    # Check bypass mode on every actor
    for actor in data.get("bypass_actors", []):
        mode = actor.get("bypass_mode")
        if mode != EXPECTED_BYPASS_MODE:
            failures.append(
                f"bypass_actor {actor.get('actor_id')} (type={actor.get('actor_type')}) "
                f"has bypass_mode={mode!r}, expected {EXPECTED_BYPASS_MODE!r} "
                f"per 2026-05-06 hardening"
            )

    # Check required rules present
    rule_types = {r.get("type") for r in data.get("rules", [])}
    missing = REQUIRED_RULES - rule_types
    if missing:
        failures.append(f"missing required rule types: {sorted(missing)}")

    if failures:
        print("RULESET DRIFT DETECTED:")
        for f in failures:
            print(f"  - {f}")
        print(
            "\nRecover: in GitHub UI go to "
            f"https://github.com/{REPO}/settings/rules/{RULESET_ID} "
            "and restore the hardened configuration. See "
            "artifacts/qa/origin_main_rewind_incident_2026-05-06.md "
            "for the original incident context."
        )
        return 1

    print(
        f"OK: ruleset {RULESET_ID} is hardened "
        f"(bypass_mode={EXPECTED_BYPASS_MODE}, "
        f"all required rules active)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
