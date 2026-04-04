#!/usr/bin/env python3
"""Check which integration credentials are configured in the current shell.

Env var names are defined in ``integration_env_registry.py`` (single source of truth,
kept in sync with ``docs/INTEGRATION_CREDENTIALS_REGISTRY.md``).

Usage:
    python3 scripts/ci/check_integration_env.py
    python3 scripts/ci/check_integration_env.py --json
        # JSON: object with "summary", "items" (per-var rows), "env_vars_tracked"
"""

import os
import sys
from pathlib import Path

_CI_DIR = Path(__file__).resolve().parent
if str(_CI_DIR) not in sys.path:
    sys.path.insert(0, str(_CI_DIR))

from integration_env_registry import ENV_VARS_TRACKED_COUNT, REGISTRY  # noqa: E402


def check_env():
    results = []
    for service, var, required, notes in REGISTRY:
        value = os.environ.get(var)
        is_set = value is not None and value.strip() != ""
        results.append({
            "service": service,
            "env_var": var,
            "required": required,
            "set": is_set,
            "notes": notes,
        })
    return results


def print_report(results):
    set_vars = [r for r in results if r["set"]]
    missing_required = [r for r in results if not r["set"] and r["required"]]
    missing_optional = [r for r in results if not r["set"] and not r["required"]]

    print("=" * 60)
    print("Integration Credentials Check")
    print("=" * 60)
    print()

    if set_vars:
        print(f"SET ({len(set_vars)}):")
        for r in set_vars:
            tag = "REQUIRED" if r["required"] else "optional"
            print(f"  [ok]  {r['env_var']:30s}  {r['service']:20s}  ({tag})")
        print()

    if missing_required:
        print(f"MISSING REQUIRED ({len(missing_required)}):")
        for r in missing_required:
            print(f"  [!!]  {r['env_var']:30s}  {r['service']:20s}  {r['notes']}")
        print()

    if missing_optional:
        print(f"MISSING OPTIONAL ({len(missing_optional)}):")
        for r in missing_optional:
            print(f"  [--]  {r['env_var']:30s}  {r['service']:20s}  {r['notes']}")
        print()

    total = len(results)
    set_count = len(set_vars)
    print(f"Summary: {set_count}/{total} env vars set", end="")
    if missing_required:
        print(f"  |  {len(missing_required)} REQUIRED vars missing")
    else:
        print(f"  |  all required vars present")

    print()
    print("Registry: docs/INTEGRATION_CREDENTIALS_REGISTRY.md")
    print("Env var names: scripts/ci/integration_env_registry.py")
    print("Keychain load: eval \"$(python3 scripts/ci/load_integration_env_from_keychain.py)\"")
    print("Messaging channels (Keychain): scripts/integrations/report_messaging_requirements_local.sh")

    return 1 if missing_required else 0


def print_json(results):
    import json

    set_vars = [r for r in results if r["set"]]
    missing_required = [r for r in results if not r["set"] and r["required"]]
    payload = {
        "registry_doc": "docs/INTEGRATION_CREDENTIALS_REGISTRY.md",
        "env_vars_module": "scripts/ci/integration_env_registry.py",
        "env_vars_tracked": ENV_VARS_TRACKED_COUNT,
        "summary": {
            "total_rows": len(results),
            "set_count": len(set_vars),
            "missing_required_count": len(missing_required),
            "missing_required_env_vars": [r["env_var"] for r in missing_required],
        },
        "items": results,
    }
    print(json.dumps(payload, indent=2))
    return 1 if missing_required else 0


def main():
    results = check_env()
    if "--json" in sys.argv:
        return print_json(results)
    return print_report(results)


if __name__ == "__main__":
    sys.exit(main())
# CI trigger
