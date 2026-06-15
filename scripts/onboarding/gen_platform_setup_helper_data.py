#!/usr/bin/env python3
"""
Generate brand-wizard-app/public/platform_setup_helper_data.json from the SSOT configs.

Joins:
  - config/brand_management/platform_setup_helper.yaml      (helper data: steps, social copy,
                                                              secret model, markets, signup urls)
  - config/brand_management/platform_credential_fields.yaml (authoritative display_name,
                                                              dashboard_url, viewable cred `fields`)
on platform `id`. Cred fields are NOT duplicated in the helper config — they're pulled here.

The page (platform_setup_helper.html) fetches the emitted JSON. Re-run after editing either
config (e.g. after live-researching a platform's setup_steps). Output is deterministic
(no runtime timestamp) so the committed JSON only changes when the source content changes.

Usage:
    python3 scripts/onboarding/gen_platform_setup_helper_data.py [--check]

    --check  exit 1 if the on-disk JSON differs from freshly generated (CI / pre-commit).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.stderr.write("PyYAML required: pip install pyyaml\n")
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
HELPER_CFG = REPO_ROOT / "config" / "brand_management" / "platform_setup_helper.yaml"
CRED_CFG = REPO_ROOT / "config" / "brand_management" / "platform_credential_fields.yaml"
OUT_PATH = REPO_ROOT / "brand-wizard-app" / "public" / "platform_setup_helper_data.json"

# Display-name fallbacks for ids not present in platform_credential_fields.yaml.
DISPLAY_FALLBACK = {
    "inaudio_findaway": "Findaway Voices / INaudio",
    "facebook": "Facebook",
}


def _load(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing config: {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def build() -> dict:
    helper = _load(HELPER_CFG)
    cred = _load(CRED_CFG)
    cred_platforms = cred.get("platforms", {}) or {}

    out_platforms = []
    for p in helper.get("platforms", []) or []:
        pid = p["id"]
        cred_entry = cred_platforms.get(pid, {}) or {}
        display_name = cred_entry.get("display_name") or DISPLAY_FALLBACK.get(pid) or pid.replace("_", " ").title()
        # NOTE: we deliberately do NOT pull the cred-config `fields` (Publisher ID, Author Page
        # URL, Marketplace, Business Account ID, …). The helper asks the director for ONLY a
        # login + a write-only password per platform — nothing extra.
        out_platforms.append({
            "id": pid,
            "display_name": display_name,
            "category": p.get("category", "distribution"),
            "markets": p.get("markets", ["en"]),
            "signup_url": p.get("signup_url", ""),
            "dashboard_url": p.get("dashboard_url") or cred_entry.get("dashboard_url", ""),
            "account_note_en": p.get("account_note_en", ""),
            "account_note_ja": p.get("account_note_ja", ""),
            "secret": p.get("secret", {}),
            "social_copy": p.get("social_copy", {}),
            "real_info_gates_en": p.get("real_info_gates_en", []),
            "real_info_gates_ja": p.get("real_info_gates_ja", []),
            "steps_status": p.get("steps_status", "pending"),
            "setup_steps": p.get("setup_steps", {"en": [], "ja": []}),
        })

    return {
        "schema_version": helper.get("schema_version", "1.0"),
        "generated_from": [
            "config/brand_management/platform_setup_helper.yaml",
            "config/brand_management/platform_credential_fields.yaml",
        ],
        "markets": helper.get("markets", []),
        "ui": helper.get("ui", {}),
        "platforms": out_platforms,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="exit 1 if on-disk JSON is stale")
    args = ap.parse_args()

    data = build()
    rendered = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False) + "\n"

    if args.check:
        current = OUT_PATH.read_text(encoding="utf-8") if OUT_PATH.exists() else ""
        if current != rendered:
            sys.stderr.write(f"STALE: {OUT_PATH} differs from generated. Re-run without --check.\n")
            return 1
        print(f"OK: {OUT_PATH} is up to date.")
        return 0

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(rendered, encoding="utf-8")
    n = len(data["platforms"])
    pending = sum(1 for p in data["platforms"] if p["steps_status"] != "verified")
    print(f"Wrote {OUT_PATH} — {n} platforms ({pending} steps pending live research).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
