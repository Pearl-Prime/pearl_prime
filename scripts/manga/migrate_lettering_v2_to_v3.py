#!/usr/bin/env python3
"""Migrate lettering_spec v2 specs → v3 in-place.

PR #631 Decision 1: lettering_spec v3 adds text_by_locale, sfx_by_locale,
narrator_caption_by_locale, font_override_by_locale. v2 specs work as-is
(backward-compat) but to ship multi-locale you need to add localized
text. This helper:

1. Bumps lettering_spec_version to "3.0.0"
2. Adds default_locale (defaults to "en_US")
3. Adds available_locales [<default_locale>] (more added by translation pipeline later)
4. Wraps existing text fields into text_by_locale[<default_locale>] dicts
5. Leaves the v2 fields in place for backward-compat with old readers

Idempotent: re-running on a v3 spec is a no-op.

Usage:
    # Single file
    python3 scripts/manga/migrate_lettering_v2_to_v3.py path/to/spec.yaml

    # Whole directory
    python3 scripts/manga/migrate_lettering_v2_to_v3.py --dir artifacts/manga/lettering/

    # Set default_locale (defaults to en_US)
    python3 scripts/manga/migrate_lettering_v2_to_v3.py --default-locale ja_JP path/to/spec.yaml

    # Dry run
    python3 scripts/manga/migrate_lettering_v2_to_v3.py --dry-run path/to/spec.yaml
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]


def _load(path: Path) -> dict[str, Any]:
    import yaml  # type: ignore
    import json

    text = path.read_text(encoding="utf-8")
    if path.suffix in (".yaml", ".yml"):
        return yaml.safe_load(text) or {}
    return json.loads(text)


def _dump(path: Path, data: dict[str, Any]) -> None:
    import yaml  # type: ignore
    import json

    if path.suffix in (".yaml", ".yml"):
        path.write_text(
            yaml.safe_dump(data, sort_keys=False, default_flow_style=False, allow_unicode=True),
            encoding="utf-8",
        )
    else:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def migrate_spec(spec: dict[str, Any], default_locale: str = "en_US") -> tuple[dict[str, Any], bool]:
    """Return (migrated_spec, changed). If already v3, returns (spec, False)."""
    current_version = spec.get("lettering_spec_version", "2.0.0")
    if current_version == "3.0.0":
        return spec, False

    out = dict(spec)
    out["lettering_spec_version"] = "3.0.0"
    out.setdefault("default_locale", default_locale)
    out.setdefault("available_locales", [default_locale])

    panels = list(out.get("lettering_panels") or [])
    for panel in panels:
        # dialogue lines
        for line in panel.get("dialogue_lines") or []:
            if "text" in line and "text_by_locale" not in line:
                line["text_by_locale"] = {default_locale: line["text"]}
            if "font_override" in line and "font_override_by_locale" not in line:
                line["font_override_by_locale"] = {default_locale: line["font_override"]}

        # SFX
        if "sfx" in panel and "sfx_by_locale" not in panel:
            panel["sfx_by_locale"] = {default_locale: list(panel.get("sfx") or [])}

        # Narrator caption
        if "narrator_caption" in panel and "narrator_caption_by_locale" not in panel:
            panel["narrator_caption_by_locale"] = {default_locale: panel.get("narrator_caption")}

        # Coverage
        if "estimated_bubble_coverage" in panel and "estimated_bubble_coverage_by_locale" not in panel:
            cov = panel.get("estimated_bubble_coverage")
            if cov is not None:
                panel["estimated_bubble_coverage_by_locale"] = {default_locale: cov}

    out["lettering_panels"] = panels
    return out, True


def _migrate_file(path: Path, default_locale: str, dry_run: bool) -> bool:
    """Returns True if file was migrated (or would be)."""
    try:
        spec = _load(path)
    except Exception as e:
        sys.stderr.write(f"❌ {path}: parse error — {e}\n")
        return False

    if spec.get("artifact_type") != "lettering_spec":
        return False

    migrated, changed = migrate_spec(spec, default_locale=default_locale)
    if not changed:
        print(f"✓ {path.relative_to(REPO) if path.is_relative_to(REPO) else path}: already v3")
        return False

    if dry_run:
        print(f"[dry-run] would migrate {path.relative_to(REPO) if path.is_relative_to(REPO) else path}")
    else:
        _dump(path, migrated)
        print(f"✓ migrated {path.relative_to(REPO) if path.is_relative_to(REPO) else path}")
    return True


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("paths", nargs="*", help="Files to migrate")
    p.add_argument("--dir", help="Directory to walk recursively")
    p.add_argument("--default-locale", default="en_US",
                   choices=["en_US", "ja_JP", "ko_KR", "zh_TW", "zh_CN"])
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    files: list[Path] = []
    if args.dir:
        root = Path(args.dir).resolve()
        for ext in ("*.yaml", "*.yml", "*.json"):
            files.extend(sorted(root.rglob(ext)))
    files.extend(Path(p).resolve() for p in args.paths)

    if not files:
        print("Nothing to migrate. Pass file paths or --dir <dir>.")
        return 0

    migrated_count = 0
    for path in files:
        if not path.exists() or not path.is_file():
            continue
        if _migrate_file(path, default_locale=args.default_locale, dry_run=args.dry_run):
            migrated_count += 1

    print()
    print(f"{'Would migrate' if args.dry_run else 'Migrated'}: {migrated_count} of {len(files)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
