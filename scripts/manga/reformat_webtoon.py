#!/usr/bin/env python3
"""Reformat composed pages into vertical webtoon strips."""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from PIL import Image

from phoenix_v4.manga.compositor.panel_detector import crop_strips, detect_panel_rows
from phoenix_v4.manga.distribution.config_io import grammar_for_format, load_format_grammars


def _require_webtoon_target(profile: dict[str, Any]) -> None:
    targets = profile.get("adaptation_targets") or []
    if "webtoon" not in targets:
        raise ValueError(
            f"title_id={profile.get('title_id')!r} has no webtoon in adaptation_targets"
        )


def _locale_flip(profile: dict[str, Any], distribution_locale: str | None) -> bool:
    locale = (distribution_locale or os.environ.get("PHOENIX_MANGA_LOCALE") or "").lower()
    if locale not in ("ko", "kr", "ko_kr"):
        return False
    brand_id = str(profile.get("brand_id") or "")
    from phoenix_v4.manga.distribution.config_io import load_brand_illustration_styles
    from phoenix_v4.manga.models.validation import repo_root

    styles = load_brand_illustration_styles(repo_root())
    locale_variants = ((styles.get(brand_id) or {}).get("locale_variants")) or {}
    return "kr" in locale_variants


def reformat_webtoon(
    *,
    profile: dict[str, Any],
    pages: list[Path],
    out_dir: Path,
    repo_root: Path,
    distribution_locale: str | None = None,
) -> Path:
    _require_webtoon_target(profile)
    formats = load_format_grammars(repo_root)
    webtoon = grammar_for_format(formats, "webtoon")
    dims = webtoon.get("page_dimensions") or {}
    strip_width = int(dims.get("width_px") or 800)
    pacing_overrides = webtoon.get("pacing_overrides") or {}
    silent_ratio = float((profile.get("pacing") or {}).get("silent_panel_ratio") or 0.15)
    multiplier = float(pacing_overrides.get("words_per_page_target_multiplier") or 1.0)
    adjusted_silent = min(1.0, silent_ratio * multiplier)

    title_id = str(profile.get("title_id") or "manga")
    out_dir = out_dir / f"{title_id}_webtoon"
    out_dir.mkdir(parents=True, exist_ok=True)
    flip = _locale_flip(profile, distribution_locale)

    strip_paths: list[Path] = []
    silent_panels = 0
    total_panels = 0

    for page_idx, page in enumerate(pages, start=1):
        rows = detect_panel_rows(page)
        strips = crop_strips(page, rows)
        for strip_idx, strip in enumerate(strips, start=1):
            total_panels += 1
            gray = strip.convert("L")
            hist = gray.histogram()
            dark = sum(hist[:64])
            total = sum(hist) or 1
            if dark / total < 0.08:
                silent_panels += 1

            w, h = strip.size
            scale = strip_width / max(1, w)
            new_h = max(1, int(h * scale))
            resized = strip.resize((strip_width, new_h), Image.Resampling.LANCZOS)
            if flip:
                resized = resized.transpose(Image.FLIP_LEFT_RIGHT)
            out_file = out_dir / f"strip_{page_idx:03d}_{strip_idx:02d}.png"
            resized.save(out_file)
            strip_paths.append(out_file)
            resized.close()
            strip.close()

    audit_path = out_dir / f"{title_id}_webtoon_audit.txt"
    observed = silent_panels / max(1, total_panels)
    audit_path.write_text(
        f"strip_width_px={strip_width}\n"
        f"total_panels={total_panels}\n"
        f"silent_panels={silent_panels}\n"
        f"observed_silent_ratio={observed:.3f}\n"
        f"profile_silent_ratio={silent_ratio:.3f}\n"
        f"adjusted_target={adjusted_silent:.3f}\n"
        f"locale_flip={flip}\n",
        encoding="utf-8",
    )
    return out_dir


def main(argv: list[str] | None = None) -> int:
    import argparse

    from phoenix_v4.manga.distribution.config_io import list_page_pngs
    from phoenix_v4.manga.models.validation import repo_root
    from phoenix_v4.manga.series.profile_loader import load_series_profile

    parser = argparse.ArgumentParser(description="Reformat pages to webtoon strips")
    parser.add_argument("--title-id", required=True)
    parser.add_argument("--page-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--distribution-locale", default="")
    args = parser.parse_args(argv)

    root = repo_root()
    try:
        profile = load_series_profile(args.title_id, root)
        pages = list_page_pngs(args.page_dir)
        reformat_webtoon(
            profile=profile,
            pages=pages,
            out_dir=args.out_dir,
            repo_root=root,
            distribution_locale=args.distribution_locale or None,
        )
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
