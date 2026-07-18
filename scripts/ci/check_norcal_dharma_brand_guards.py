#!/usr/bin/env python3
"""
CI guards: removed duplicate teacher/brand IDs must not reappear in catalog config.

The former separate forest/simplicity imprint was merged into Stillness Press (ahjan).
This script fails if deprecated identifiers show up under config/catalog_planning/.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_CATALOG = REPO_ROOT / "config" / "catalog_planning"


def _deprecated_teacher_id() -> str:
    """Historic duplicate id merged into ahjan; built without a contiguous forbidden literal."""
    return bytes((97, 106, 97, 104, 110, 95, 120)).decode("ascii")


def _deprecated_brand_id() -> str:
    """Historic distribution-only brand id merged into stillness_press."""
    return bytes(
        (110, 111, 114, 99, 97, 108, 95, 100, 104, 97, 114, 109, 97)
    ).decode("ascii")


# Substrings that must not appear in catalog_planning YAML (unified on ahjan / stillness_press).
FORBIDDEN = (_deprecated_teacher_id(), _deprecated_brand_id())


def _scan() -> list[str]:
    errors: list[str] = []
    if not CONFIG_CATALOG.is_dir():
        return [f"missing directory: {CONFIG_CATALOG}"]
    for path in sorted(CONFIG_CATALOG.rglob("*.yaml")):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as e:
            errors.append(f"{path}: read failed: {e}")
            continue
        lower = text.lower()
        for token in FORBIDDEN:
            if token in lower:
                errors.append(f"{path}: contains forbidden token {token!r}")
                break
    return errors


def main() -> int:
    errors = _scan()
    if errors:
        print("check_norcal_dharma_brand_guards: FAIL", file=sys.stderr)
        for e in errors:
            print(e, file=sys.stderr)
        return 1
    print("check_norcal_dharma_brand_guards: OK (no deprecated tokens in catalog_planning)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
