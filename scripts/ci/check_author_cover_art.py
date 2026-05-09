#!/usr/bin/env python3
"""
CI gate: every launchable author has author cover art registry entry, existing PNG, valid style/palette.
Launchable = teachers in brand_teacher_matrix + author_ids in author_registry.
Authority: docs/authoring/AUTHOR_COVER_ART_SYSTEM.md
Run: PYTHONPATH=. python3 scripts/ci/check_author_cover_art.py [--repo-root PATH] [--gate-mode warn|fail]
Exit: 0 pass (or pass-with-warnings in warn mode for missing assets only), 1 fail.

Gate mode (Phase 2 Q2 relax-to-warn for missing cover_art_base files):
- Default: warn — registry-referenced PNG missing on disk => stderr ::warning::, exit 0.
- fail — legacy strict: any issue including missing file => FAIL, exit 1.
  Set COVER_ART_GATE_MODE=fail or pass --gate-mode fail. CLI overrides env.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# GitHub Actions workflow command — surfaces in PR / run UI
_GH_WARN_PREFIX = "::warning::"


def _load_yaml(p: Path) -> dict:
    if not p.exists() or yaml is None:
        return {}
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _launchable_author_ids(repo_root: Path) -> set[str]:
    """Teachers in brand_teacher_matrix + author_ids in author_registry."""
    ids: set[str] = set()
    # Teachers assigned to any brand
    matrix_path = repo_root / "config" / "catalog_planning" / "brand_teacher_matrix.yaml"
    matrix = _load_yaml(matrix_path)
    for brand_data in (matrix.get("brands") or {}).values():
        for tid in brand_data.get("teachers") or []:
            if isinstance(tid, str) and tid.strip():
                ids.add(tid.strip())
    # Pen-name authors
    author_reg_path = repo_root / "config" / "author_registry.yaml"
    author_reg = _load_yaml(author_reg_path)
    for aid in (author_reg.get("authors") or {}).keys():
        if isinstance(aid, str) and aid.strip():
            ids.add(aid.strip())
    return ids


def resolve_gate_mode(cli_gate_mode: str | None) -> str:
    """Return 'warn' or 'fail'. CLI --gate-mode wins over COVER_ART_GATE_MODE; default warn."""
    if cli_gate_mode is not None:
        return cli_gate_mode
    env = (os.environ.get("COVER_ART_GATE_MODE") or "").strip().lower()
    if env in ("warn", "fail"):
        return env
    return "warn"


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate launchable authors have cover art registry + PNG + style/palette")
    ap.add_argument("--repo-root", type=Path, default=REPO_ROOT, help="Repo root")
    ap.add_argument(
        "--gate-mode",
        choices=("warn", "fail"),
        default=None,
        help="warn=missing cover_art_base file is warning only (default). fail=strict legacy. Overrides COVER_ART_GATE_MODE.",
    )
    args = ap.parse_args()
    repo_root = args.repo_root
    gate_mode = resolve_gate_mode(args.gate_mode)

    registry_path = repo_root / "config" / "authoring" / "author_cover_art_registry.yaml"
    if not registry_path.exists():
        print("FAIL: author cover art registry missing:", registry_path, file=sys.stderr)
        return 1

    reg = _load_yaml(registry_path)
    authors_reg = reg.get("authors") or {}

    launchable = _launchable_author_ids(repo_root)
    if not launchable:
        print("PASS: no launchable authors (empty brand_teacher_matrix + author_registry); skip", file=sys.stderr)
        return 0

    # Hard failures: registry/schema compliance (unchanged across modes).
    hard_errors: list[str] = []
    # Missing on-disk asset only (Phase 2 relax-to-warn when gate_mode == warn).
    missing_file_errors: list[str] = []

    for aid in sorted(launchable):
        if aid not in authors_reg:
            hard_errors.append(f"{aid}: missing from author_cover_art_registry.yaml")
            continue
        entry = authors_reg[aid]
        base_path_str = entry.get("cover_art_base")
        if not base_path_str or not isinstance(base_path_str, str):
            hard_errors.append(f"{aid}: cover_art_base missing or invalid")
            continue
        full_path = (repo_root / base_path_str).resolve()
        if not full_path.exists():
            missing_file_errors.append(f"{aid}: cover_art_base file does not exist: {base_path_str}")
        style_hint = entry.get("style_hint")
        if not style_hint or not isinstance(style_hint, str) or not style_hint.strip():
            hard_errors.append(f"{aid}: style_hint missing or empty")
        palette_tokens = entry.get("palette_tokens")
        if not isinstance(palette_tokens, list) or len(palette_tokens) == 0:
            hard_errors.append(f"{aid}: palette_tokens missing or empty")

    for e in hard_errors:
        print("FAIL:", e, file=sys.stderr)

    if hard_errors:
        print(
            "Author cover art gate: hard validation failed (registry entry, cover_art_base path, style_hint, or palette_tokens).",
            file=sys.stderr,
        )
        return 1

    if missing_file_errors:
        if gate_mode == "fail":
            for e in missing_file_errors:
                print("FAIL:", e, file=sys.stderr)
            print(
                "Author cover art gate: every launchable author must have registry entry, existing PNG, style_hint, palette_tokens.",
                file=sys.stderr,
            )
            return 1
        for e in missing_file_errors:
            print(f"{_GH_WARN_PREFIX}author cover art (missing asset): {e}", file=sys.stderr)
        print(
            f"{_GH_WARN_PREFIX}Author cover art gate: missing cover_art_base file(s) for "
            f"{len(missing_file_errors)} launchable author(s); continuing under warn mode (Phase 2 Q2).",
            file=sys.stderr,
        )
        return 0

    print("PASS: all launchable authors have cover art registry entry, PNG, style_hint, palette_tokens.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
