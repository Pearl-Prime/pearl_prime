#!/usr/bin/env python3
"""Fail-closed production checker for Enhancement Contract V2.1 proof."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping


def _mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def check_payload(payload: Mapping[str, Any], *, production: bool) -> list[str]:
    errors: list[str] = []
    if not production:
        return errors
    if str(payload.get("status") or "").upper() != "PASS":
        errors.append("enhancement_contract_status_not_pass")
    v21 = _mapping(payload.get("enhancement_contract_v21"))
    if not v21:
        errors.append("enhancement_contract_v21_missing")
        return errors
    integrity = _mapping(_mapping(payload.get("validation")).get("v21_integrity"))
    if str(integrity.get("status") or "").upper() != "PASS":
        errors.append("enhancement_contract_v21_integrity_not_pass")
    budget = _mapping(v21.get("optional_accent_budget"))
    actual = _mapping(budget.get("actual"))
    assigned = int(actual.get("assigned_total_optional_accents") or 0)
    hard_total = int(budget.get("hard_max_total_accents") or 0)
    chapters = int(actual.get("optional_accent_chapter_count") or 0)
    hard_chapters = int(budget.get("hard_max_accent_chapters") or 0)
    free = int(actual.get("accent_free_chapter_count") or 0)
    free_min = int(budget.get("accent_free_chapters_minimum") or 0)
    if assigned > hard_total:
        errors.append("hard_max_total_accents_exceeded")
    if chapters > hard_chapters:
        errors.append("hard_max_accent_chapters_exceeded")
    if free < free_min:
        errors.append("accent_free_chapters_minimum_not_met")
    max_per = int(budget.get("max_accents_per_chapter") or 0)
    for chapter, count in _mapping(actual.get("per_chapter_optional_counts")).items():
        if int(count) > max_per:
            errors.append(f"max_accents_per_chapter_exceeded:ch{chapter}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("payload", type=Path)
    parser.add_argument(
        "--quality-profile",
        choices=["production", "flagship", "draft", "debug"],
        default="production",
    )
    args = parser.parse_args()
    payload = json.loads(args.payload.read_text(encoding="utf-8"))
    errors = check_payload(
        payload,
        production=args.quality_profile in {"production", "flagship"},
    )
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors}, indent=2))
    return 0 if not errors else 3


if __name__ == "__main__":
    raise SystemExit(main())
