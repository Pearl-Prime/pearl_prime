#!/usr/bin/env python3
"""Distribution pipeline: EPUB3 / print PDF / CBZ / webtoon from composed pages."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from phoenix_v4.manga.distribution.config_io import list_page_pngs  # noqa: E402
from phoenix_v4.manga.models.validation import repo_root  # noqa: E402
from phoenix_v4.manga.series.profile_loader import load_series_profile  # noqa: E402
from scripts.manga.build_cbz import build_cbz  # noqa: E402
from scripts.manga.build_epub3 import build_epub3  # noqa: E402
from scripts.manga.build_print_pdf import build_print_pdf  # noqa: E402
from scripts.manga.generate_upload_checklist import generate_upload_checklist  # noqa: E402
from scripts.manga.reformat_webtoon import reformat_webtoon  # noqa: E402

_FORMAT_ALIASES = {
    "epub": "epub3",
    "pdf": "print_pdf",
    "print": "print_pdf",
}


def _default_formats(profile: dict) -> list[str]:
    targets = profile.get("adaptation_targets") or []
    formats: list[str] = []
    if "print" in targets:
        formats.extend(["epub3", "print_pdf", "cbz"])
    if "webtoon" in targets:
        formats.append("webtoon")
    return formats or ["epub3", "cbz"]


def _normalize_formats(raw: str, profile: dict) -> list[str]:
    if not raw.strip():
        return _default_formats(profile)
    out: list[str] = []
    for part in raw.split(","):
        fmt = _FORMAT_ALIASES.get(part.strip().lower(), part.strip().lower())
        if fmt and fmt not in out:
            out.append(fmt)
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build distribution formats from page_###.png + series profile"
    )
    parser.add_argument("--title-id", required=True)
    parser.add_argument("--page-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument(
        "--formats",
        default="",
        help="Comma list: epub3,print_pdf,cbz,webtoon (default from adaptation_targets)",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--distribution-locale", default="")
    args = parser.parse_args(argv)

    root = repo_root()
    profile = load_series_profile(args.title_id, root)
    pages = list_page_pngs(args.page_dir)
    title_id = str(profile.get("title_id") or args.title_id)
    out_dir = args.out_dir or (root / "artifacts" / "manga_distribution" / title_id)
    formats = _normalize_formats(args.formats, profile)

    if args.dry_run:
        print(
            f"Dry run: title_id={title_id} pages={len(pages)} "
            f"formats={','.join(formats)} out_dir={out_dir}"
        )
        return 0

    out_dir.mkdir(parents=True, exist_ok=True)
    built: dict[str, Path] = {}

    if "epub3" in formats:
        epub_path = out_dir / f"{title_id}.epub"
        build_epub3(profile=profile, pages=pages, out_path=epub_path, repo_root=root)
        built["epub3"] = epub_path
        print(f"epub3: {epub_path}")

    if "print_pdf" in formats:
        pdf_path = out_dir / f"{title_id}_print.pdf"
        build_print_pdf(profile=profile, pages=pages, out_path=pdf_path, repo_root=root)
        built["print_pdf"] = pdf_path
        print(f"print_pdf: {pdf_path}")

    if "cbz" in formats:
        cbz_path = out_dir / f"{title_id}.cbz"
        build_cbz(profile=profile, pages=pages, out_path=cbz_path)
        built["cbz"] = cbz_path
        print(f"cbz: {cbz_path}")

    if "webtoon" in formats:
        try:
            wt_dir = reformat_webtoon(
                profile=profile,
                pages=pages,
                out_dir=out_dir,
                repo_root=root,
                distribution_locale=args.distribution_locale or None,
            )
            built["webtoon"] = wt_dir
            print(f"webtoon: {wt_dir}")
        except ValueError as exc:
            print(f"webtoon skipped: {exc}", file=sys.stderr)

    if built:
        checklist = out_dir / f"{title_id}_upload_checklist.md"
        generate_upload_checklist(
            profile=profile,
            built_formats=built,
            out_path=checklist,
            repo_root_path=root,
        )
        print(f"checklist: {checklist}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
