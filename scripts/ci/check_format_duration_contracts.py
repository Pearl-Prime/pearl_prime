#!/usr/bin/env python3
"""CI gate: runtime formats must not advertise duration without an honest contract.

DURATION-DERIVATION-01 §8 — enforced by ws_stub_format_duration_backfill (2026-07-07).

BLOCK when any ``runtime_formats`` entry:
  * carries ``audiobook_minutes``, ``ebook_minutes``, or ``duration_minutes`` but lacks
    ``word_range`` + ``fill_regime`` (false advertising), OR
  * stored minutes disagree with ``phoenix_v4.ops.duration_derivation`` recomputation, OR
  * a Group A atom-native format lacks a full duration contract.

Exit 0 on PASS; 1 on BLOCK.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

from phoenix_v4.ops.duration_derivation import (  # noqa: E402
    GROUP_A_ATOM_NATIVE_FORMATS,
    can_advertise_duration,
    derive_format_minutes,
    has_honest_duration_contract,
    load_wpm_constants,
)


def _load_registry(path: Path) -> dict:
    if yaml is None:
        raise SystemExit("BLOCK: PyYAML required for check_format_duration_contracts.py")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def check_format_duration_contracts(registry: dict, scorecard: dict | None = None) -> list[str]:
    """Return a list of BLOCK reasons (empty = PASS)."""
    errors: list[str] = []
    runtime = (registry or {}).get("runtime_formats") or {}
    tts_wpm, ebook_wpm = load_wpm_constants(scorecard)

    for name, fmt in runtime.items():
        if not isinstance(fmt, dict):
            continue
        advertises = any(
            k in fmt for k in ("audiobook_minutes", "ebook_minutes", "duration_minutes")
        )
        has_range = bool(fmt.get("word_range"))
        if advertises and not has_honest_duration_contract(fmt):
            errors.append(
                f"{name}: advertises duration ({fmt.get('audiobook_minutes')!r} ab / "
                f"{fmt.get('duration_minutes')!r} legacy) but lacks honest contract "
                f"(word_range={fmt.get('word_range')!r}, fill_regime={fmt.get('fill_regime')!r})"
            )
            continue
        if not has_range:
            continue
        derived = derive_format_minutes(fmt, tts_wpm, ebook_wpm)
        if derived is None:
            errors.append(f"{name}: word_range present but derivation returned None")
            continue
        for field, key in (("audiobook_minutes", "audiobook_minutes"), ("ebook_minutes", "ebook_minutes")):
            if field in fmt and fmt[field] != derived[key]:
                errors.append(
                    f"{name}: stored {field}={fmt[field]} != derived {derived[key]}"
                )
        if "duration_minutes" in fmt and fmt["duration_minutes"] != derived["audiobook_minutes"]:
            errors.append(
                f"{name}: duration_minutes={fmt['duration_minutes']} != "
                f"derived audiobook_minutes {derived['audiobook_minutes']}"
            )
        if name in GROUP_A_ATOM_NATIVE_FORMATS and not can_advertise_duration(fmt, scorecard):
            errors.append(f"{name}: Group A atom-native format cannot advertise duration")

    missing_group_a = GROUP_A_ATOM_NATIVE_FORMATS - set(runtime.keys())
    for name in sorted(missing_group_a):
        errors.append(f"{name}: Group A format missing from runtime_formats")

    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Format duration contract gate (DURATION-DERIVATION-01 §8)")
    ap.add_argument(
        "--registry",
        type=Path,
        default=REPO_ROOT / "config" / "format_selection" / "format_registry.yaml",
    )
    ap.add_argument(
        "--scorecard",
        type=Path,
        default=REPO_ROOT / "config" / "duration_scorecard.yaml",
    )
    args = ap.parse_args()
    registry = _load_registry(args.registry)
    scorecard = _load_registry(args.scorecard) if args.scorecard.exists() else {}
    errors = check_format_duration_contracts(registry, scorecard)
    if errors:
        print("BLOCK: format duration contract violations:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print("PASS: all runtime formats with duration claims have honest contracts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
