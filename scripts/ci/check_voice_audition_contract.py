#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
LOCALE_EXTENSION_PATH = REPO_ROOT / "config" / "localization" / "brand_registry_locale_extension.yaml"
PENDING_ASSIGNMENTS_PATH = REPO_ROOT / "config" / "voice_auditions" / "pending_voice_assignments.yaml"


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _pending_by_brand(data: dict) -> dict[str, dict]:
    return {
        row["brand_id"]: row
        for row in data.get("pending_assignments", [])
        if isinstance(row, dict) and row.get("brand_id")
    }


def main() -> int:
    locale_data = _load_yaml(LOCALE_EXTENSION_PATH)
    pending_data = _load_yaml(PENDING_ASSIGNMENTS_PATH)
    pending = _pending_by_brand(pending_data)
    failures: list[str] = []

    brands = locale_data.get("brands", {})
    for brand_id, cfg in brands.items():
        voice_identity = cfg.get("voice_identity") or {}
        locale = cfg.get("locale")
        elevenlabs_voice_id = voice_identity.get("elevenlabs_voice_id")
        elevenlabs_preferred = bool(voice_identity.get("elevenlabs_preferred"))

        pending_row = pending.get(brand_id)

        if isinstance(elevenlabs_voice_id, str) and elevenlabs_voice_id.strip().upper() == "TBD":
            if not pending_row:
                failures.append(
                    f"{brand_id}: elevenlabs_voice_id is TBD but no pending assignment exists in "
                    f"{PENDING_ASSIGNMENTS_PATH.relative_to(REPO_ROOT)}"
                )
            elif pending_row.get("placeholder") != "TBD":
                failures.append(
                    f"{brand_id}: pending assignment must declare placeholder 'TBD' when config uses TBD"
                )

        if elevenlabs_preferred and not elevenlabs_voice_id:
            if not pending_row:
                failures.append(
                    f"{brand_id}: elevenlabs_preferred=true requires either elevenlabs_voice_id or a pending assignment"
                )

        if pending_row:
            if pending_row.get("locale") != locale:
                failures.append(
                    f"{brand_id}: pending assignment locale {pending_row.get('locale')} does not match {locale}"
                )
            if pending_row.get("status") != "pending_audition":
                failures.append(f"{brand_id}: unsupported pending assignment status {pending_row.get('status')!r}")
            fallback_voice_id = pending_row.get("fallback_voice_id")
            if fallback_voice_id and fallback_voice_id != voice_identity.get("google_voice"):
                failures.append(
                    f"{brand_id}: pending assignment fallback_voice_id {fallback_voice_id!r} does not match "
                    f"google_voice {voice_identity.get('google_voice')!r}"
                )
            if not elevenlabs_voice_id and not elevenlabs_preferred:
                failures.append(
                    f"{brand_id}: pending assignment present but brand is not marked elevenlabs_preferred and has no TBD voice"
                )

    pending_only = sorted(set(pending) - set(brands))
    for brand_id in pending_only:
        failures.append(f"{brand_id}: pending assignment references unknown brand_id")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1

    print(
        "Voice audition contract OK: "
        f"{len(pending)} pending assignment(s) validated against "
        f"{LOCALE_EXTENSION_PATH.relative_to(REPO_ROOT)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
