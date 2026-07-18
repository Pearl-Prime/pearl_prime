#!/usr/bin/env python3
"""Populate text_by_locale / sfx_by_locale / narrator_caption_by_locale dicts
on a chapter_script (or v3 lettering_spec) by translating from the source
locale to all target locales.

Per PR #631 Decision 1: 50–99× cost reduction across 5 markets vs
re-render-per-locale. Schema (PR #644 lettering v3) supports this; this
script does the actual filling.

Usage:
    # Default backend (Qwen on Pearl Star Ollama — Tier 2, free, unattended)
    python3 scripts/manga/translate_chapter_script.py \\
        --in artifacts/manga/chapter_scripts/.../ep_001.yaml \\
        --target-locales ja_JP,zh_TW,zh_CN

    # Operator-present override (DeepSeek for zh, Google AI for ja)
    python3 scripts/manga/translate_chapter_script.py \\
        --in ... --backend-overrides ja_JP=google_ai,zh_TW=deepseek,zh_CN=deepseek

    # Mock mode (tests / dry-run)
    python3 scripts/manga/translate_chapter_script.py --in ... --backend mock

Idempotent: if a locale's text dict is already populated for a line, the
script skips it (use --force to re-translate). ko_KR uses 'placeholder'
backend by default (echoes en_US) until Naver connector ships in Phase 2.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from phoenix_v4.manga.translation.translators import (  # type: ignore
    BackendUnavailableError,
    TranslationError,
    available_backends,
    bulk_translate,
    translate,
)


def _load_yaml(path: Path) -> dict[str, Any]:
    import yaml  # type: ignore

    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _dump_yaml(path: Path, data: dict[str, Any]) -> None:
    import yaml  # type: ignore

    path.write_text(
        yaml.safe_dump(data, sort_keys=False, default_flow_style=False, allow_unicode=True),
        encoding="utf-8",
    )


# ─── translation strategy per field ───────────────────────────────────────


def _translate_dict_in_place(
    field: dict[str, Any],
    *,
    source_locale: str,
    target_locales: list[str],
    backend_for: dict[str, str],
    force: bool,
) -> int:
    """Populate `field` (a *_by_locale dict) for every target locale.

    Returns the count of new locale entries added.
    """
    if not isinstance(field, dict):
        return 0
    src_value = field.get(source_locale)
    if src_value is None:
        return 0

    added = 0
    for tl in target_locales:
        if tl == source_locale:
            continue
        if tl in field and not force:
            continue
        backend = backend_for.get(tl, "qwen_ollama")
        try:
            if isinstance(src_value, str):
                field[tl] = translate(src_value, target_locale=tl, backend=backend)
            elif isinstance(src_value, list):
                field[tl] = bulk_translate(
                    src_value, target_locale=tl, backend=backend
                )
            else:
                continue
            added += 1
        except (TranslationError, BackendUnavailableError) as e:
            sys.stderr.write(f"⚠️  {tl}: {e}\n")
    return added


def translate_chapter_script(
    spec: dict[str, Any],
    *,
    source_locale: str = "en_US",
    target_locales: list[str] | None = None,
    backend: str = "qwen_ollama",
    backend_overrides: dict[str, str] | None = None,
    force: bool = False,
) -> tuple[dict[str, Any], dict[str, int]]:
    """Translate every text_by_locale / sfx_by_locale / narrator_caption_by_locale
    in `spec` from `source_locale` to each `target_locale`.

    Returns (updated_spec, stats) — stats is { locale: entries_added }.

    Idempotent: skips locales that already have a value unless ``force=True``.
    """
    if target_locales is None:
        target_locales = ["ja_JP", "zh_TW", "zh_CN"]
    backend_overrides = dict(backend_overrides or {})

    # Default ko_KR → placeholder (Phase 2 connector)
    backend_for: dict[str, str] = {tl: backend for tl in target_locales}
    backend_for["ko_KR"] = backend_overrides.get("ko_KR", "placeholder")
    backend_for.update(backend_overrides)

    stats: dict[str, int] = {tl: 0 for tl in target_locales}

    pages = spec.get("pages") or spec.get("lettering_panels")
    if pages is None:
        # Some chapter scripts use top-level "lettering_panels" instead of nested pages.
        return spec, stats

    # Walk both shapes: pages[].panels[] AND lettering_panels[]
    panels: list[dict[str, Any]] = []
    if isinstance(pages, list) and pages and "panels" in pages[0]:
        for page in pages:
            panels.extend(page.get("panels") or [])
    else:
        panels = pages

    for panel in panels:
        # Per-line dialogue text + font_override
        for line in panel.get("dialogue_lines") or []:
            tbl = line.setdefault("text_by_locale", {})
            n = _translate_dict_in_place(
                tbl,
                source_locale=source_locale,
                target_locales=target_locales,
                backend_for=backend_for,
                force=force,
            )
            for tl in target_locales:
                if tl in tbl:
                    stats[tl] = stats.get(tl, 0) + (1 if n else 0)

        # Panel-level sfx_by_locale (list of strings)
        sbl = panel.get("sfx_by_locale")
        if isinstance(sbl, dict):
            _translate_dict_in_place(
                sbl,
                source_locale=source_locale,
                target_locales=target_locales,
                backend_for=backend_for,
                force=force,
            )

        # Panel-level narrator_caption_by_locale
        ncbl = panel.get("narrator_caption_by_locale")
        if isinstance(ncbl, dict):
            _translate_dict_in_place(
                ncbl,
                source_locale=source_locale,
                target_locales=target_locales,
                backend_for=backend_for,
                force=force,
            )

    # Update available_locales metadata
    available = set(spec.get("available_locales") or [source_locale])
    available.update(target_locales)
    spec["available_locales"] = sorted(available)

    return spec, stats


# ─── CLI ───────────────────────────────────────────────────────────────────


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="input_path", required=True)
    p.add_argument("--out", dest="output_path",
                   help="Output path (default: overwrite input)")
    p.add_argument("--source-locale", default="en_US")
    p.add_argument("--target-locales", default="ja_JP,zh_TW,zh_CN",
                   help="Comma-separated target locales (default: ja_JP,zh_TW,zh_CN)")
    p.add_argument("--backend", default="qwen_ollama",
                   choices=available_backends(),
                   help="Default backend (Tier 2 default = qwen_ollama)")
    p.add_argument("--backend-overrides", default="",
                   help="Per-locale backend overrides, e.g. ja_JP=google_ai,zh_TW=deepseek")
    p.add_argument("--force", action="store_true",
                   help="Re-translate locales that already have values")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    in_path = Path(args.input_path).resolve()
    if not in_path.exists():
        sys.stderr.write(f"❌ input not found: {in_path}\n")
        return 2
    out_path = Path(args.output_path).resolve() if args.output_path else in_path

    target_locales = [l.strip() for l in args.target_locales.split(",") if l.strip()]
    overrides: dict[str, str] = {}
    if args.backend_overrides:
        for pair in args.backend_overrides.split(","):
            if "=" not in pair:
                continue
            locale, backend = pair.split("=", 1)
            overrides[locale.strip()] = backend.strip()

    print(f"Input:    {in_path.relative_to(REPO) if in_path.is_relative_to(REPO) else in_path}")
    print(f"Source:   {args.source_locale}")
    print(f"Targets:  {target_locales}")
    print(f"Backend:  {args.backend}  overrides: {overrides or '(none)'}")
    print()

    spec = _load_yaml(in_path)
    spec, stats = translate_chapter_script(
        spec,
        source_locale=args.source_locale,
        target_locales=target_locales,
        backend=args.backend,
        backend_overrides=overrides,
        force=args.force,
    )

    if args.dry_run:
        print("[dry-run] not writing output")
    else:
        _dump_yaml(out_path, spec)
        print(f"✓ wrote {out_path.relative_to(REPO) if out_path.is_relative_to(REPO) else out_path}")
    print()
    print("Stats:")
    for tl in target_locales:
        print(f"  {tl}: {stats.get(tl, 0)} fields populated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
