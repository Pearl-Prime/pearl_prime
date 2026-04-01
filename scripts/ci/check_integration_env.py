#!/usr/bin/env python3
"""Check which integration credentials are configured in the current shell.

Reads the canonical registry of env vars from
docs/INTEGRATION_CREDENTIALS_REGISTRY.md and reports set vs missing.

Usage:
    python3 scripts/ci/check_integration_env.py
    python3 scripts/ci/check_integration_env.py --json
"""

import os
import sys

# Canonical env var registry.
# Each entry: (service_name, env_var, required_bool, notes)
REGISTRY = [
    # --- LLM Providers ---
    ("Qwen / DashScope", "QWEN_API_KEY", True, "Primary LLM - DashScope API key"),
    ("Qwen / DashScope", "QWEN_BASE_URL", True, "DashScope endpoint URL"),
    ("Qwen / DashScope", "QWEN_MODEL", False, "Model override (default in scripts)"),
    ("Qwen / DashScope", "DASHSCOPE_API_KEY", False, "Alt env var for DashScope key"),
    ("Qwen / DashScope", "DASHSCOPE_BASE_URL", False, "Alt env var for DashScope URL"),
    ("Qwen / DashScope", "DASHSCOPE_MODEL", False, "Alt env var for DashScope model"),
    ("Anthropic", "ANTHROPIC_API_KEY", False, "Claude API key (optional fallback LLM)"),
    ("Anthropic", "CLAUDE_MODEL", False, "Claude model selection"),
    ("OpenAI", "OPENAI_API_KEY", False, "OpenAI API key (TTS + fallback LLM)"),
    ("Ollama", "OLLAMA_HOST", False, "Local Ollama endpoint"),
    ("Ollama", "OLLAMA_MODEL", False, "Local Ollama model"),

    # --- Media / TTS ---
    ("ElevenLabs", "ELEVENLABS_API_KEY", False, "TTS (guided audio, journal prompts)"),

    # --- Infrastructure ---
    ("Cloudflare", "CLOUDFLARE_ACCOUNT_ID", False, "Workers AI + Pages"),
    ("Cloudflare", "CLOUDFLARE_API_TOKEN", False, "Cloudflare API token"),
    ("Cloudflare", "CLOUDFLARE_AI_API_TOKEN", False, "Workers AI alt token"),
    ("GitHub", "GITHUB_TOKEN", False, "GitHub API (auto in Actions)"),

    # --- Publishing ---
    ("WordPress", "WORDPRESS_SITE_URL", False, "Pearl News publishing"),
    ("WordPress", "WORDPRESS_USERNAME", False, "WordPress user"),
    ("WordPress", "WORDPRESS_APP_PASSWORD", False, "WordPress app password"),

    # --- Funnel ---
    ("GoHighLevel", "GHL_API_KEY", False, "Funnel CRM"),
    ("GoHighLevel", "GHL_LOCATION_ID", False, "GHL location"),
    ("SMTP", "SMTP_HOST", False, "Funnel email host"),
    ("SMTP", "SMTP_PORT", False, "Funnel email port"),
    ("SMTP", "SMTP_USER", False, "Funnel email user"),
    ("SMTP", "SMTP_PASSWORD", False, "Funnel email password"),
    ("Funnel", "FROM_EMAIL", False, "Funnel sender email"),
    ("Funnel", "FROM_NAME", False, "Funnel sender name"),
    ("Funnel", "SECRET_KEY", False, "Flask session key"),
    ("Funnel", "BASE_URL", False, "Funnel base URL"),
    ("Google Analytics", "GA4_MEASUREMENT_ID", False, "Funnel analytics"),
]


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
    print("Messaging channels (Keychain): scripts/integrations/report_messaging_requirements_local.sh")

    return 1 if missing_required else 0


def print_json(results):
    import json
    print(json.dumps(results, indent=2))
    missing_required = [r for r in results if not r["set"] and r["required"]]
    return 1 if missing_required else 0


def main():
    results = check_env()
    if "--json" in sys.argv:
        return print_json(results)
    return print_report(results)


if __name__ == "__main__":
    sys.exit(main())
