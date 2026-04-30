#!/usr/bin/env python3
"""validate_epub.py — KDP-readiness + structural EPUB validator (D-1.2 follow-up).

Companion to scripts/release/build_epub.py. Inspects an EPUB file and
reports:

  STRUCTURE   — required EPUB 3 manifest items, spine, NAV, NCX
  METADATA    — title / language / uid / author present + lang in BCP47 form
  COVER       — image present, dimensions meet KDP minimums
  CHAPTERS    — at least 1 chapter, all spine refs resolve
  SIZE        — file size below KDP's 650MB cap
  WORDCOUNT   — total prose word count (informational; warn if < 5000)

Exit codes:
  0 — all checks PASS (or only WARN-level findings)
  1 — at least one ERROR-level finding (KDP would reject)
  2 — input error (bad path, unreadable EPUB)

Usage:
  python3 scripts/publish/validate_epub.py path/to/book.epub
  python3 scripts/publish/validate_epub.py --json path/to/book.epub
  python3 scripts/publish/validate_epub.py --batch artifacts/epub/

Optional epubcheck integration:
  Set EPUBCHECK_JAR=/path/to/epubcheck.jar to additionally run the official
  W3C/IDPF epubcheck. Without it, only Python-side structural checks run.

Path-of-truth note:
  The pathway doc (docs/PHOENIX_OMEGA_PATHWAY_TO_100_2026-04-29.md, D-1.2)
  refers to scripts/publish/build_epub.py — but the actual builder is at
  scripts/release/build_epub.py and predates this PR. This validator lives
  in scripts/publish/ to match the pathway doc's "publish" namespace; the
  builder may be moved or aliased in a follow-up PR.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]

try:
    from ebooklib import epub, ITEM_IMAGE, ITEM_DOCUMENT, ITEM_COVER, ITEM_NAVIGATION
except ImportError:
    print("ERROR: ebooklib required. Install: pip install ebooklib", file=sys.stderr)
    sys.exit(2)

try:
    from PIL import Image
    _HAS_PIL = True
except ImportError:
    _HAS_PIL = False

# KDP cover thresholds (Amazon Help G200645690).
# Hard minimum the validator enforces; ideal target is 1600×2560.
KDP_COVER_MIN_W = 1000
KDP_COVER_MIN_H = 1600
KDP_COVER_IDEAL_W = 1600
KDP_COVER_IDEAL_H = 2560
KDP_FILE_SIZE_MAX_MB = 650
KDP_WORDCOUNT_WARN_BELOW = 5000

SEVERITY_INFO = "INFO"
SEVERITY_WARN = "WARN"
SEVERITY_ERROR = "ERROR"

_BCP47_RE = re.compile(r"^[a-zA-Z]{2,3}(-[A-Za-z0-9]+)*$")


@dataclass
class Finding:
    section: str
    severity: str
    code: str
    message: str
    detail: dict[str, Any] = field(default_factory=dict)


@dataclass
class Report:
    path: str
    findings: list[Finding] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == SEVERITY_ERROR]

    @property
    def warns(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == SEVERITY_WARN]

    def add(self, section: str, severity: str, code: str, message: str, **detail: Any) -> None:
        self.findings.append(Finding(section, severity, code, message, detail))

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "metadata": self.metadata,
            "errors": [asdict(f) for f in self.errors],
            "warns": [asdict(f) for f in self.warns],
            "infos": [asdict(f) for f in self.findings if f.severity == SEVERITY_INFO],
        }


def _check_size(path: Path, report: Report) -> None:
    size_bytes = path.stat().st_size
    size_mb = size_bytes / (1024 * 1024)
    report.metadata["file_size_mb"] = round(size_mb, 2)
    if size_mb > KDP_FILE_SIZE_MAX_MB:
        report.add(
            "SIZE", SEVERITY_ERROR, "size_above_kdp_cap",
            f"EPUB is {size_mb:.1f} MB; KDP cap is {KDP_FILE_SIZE_MAX_MB} MB",
            file_size_mb=round(size_mb, 2), cap_mb=KDP_FILE_SIZE_MAX_MB,
        )


def _check_metadata(book: "epub.EpubBook", report: Report) -> None:
    title = book.title or ""
    lang = book.language or ""
    uid = book.uid or ""
    creators = book.get_metadata("DC", "creator")

    report.metadata["title"] = title
    report.metadata["language"] = lang
    report.metadata["uid"] = uid
    report.metadata["author_count"] = len(creators)

    if not title.strip():
        report.add("METADATA", SEVERITY_ERROR, "missing_title", "EPUB has no <dc:title>")
    if not lang.strip():
        report.add("METADATA", SEVERITY_ERROR, "missing_language", "EPUB has no <dc:language>")
    elif not _BCP47_RE.match(lang.strip()):
        report.add(
            "METADATA", SEVERITY_ERROR, "invalid_language",
            f"<dc:language> {lang!r} is not a BCP47 tag", language=lang,
        )
    if not uid.strip():
        report.add("METADATA", SEVERITY_ERROR, "missing_uid", "EPUB has no <dc:identifier>")
    if not creators:
        report.add("METADATA", SEVERITY_ERROR, "missing_author", "EPUB has no <dc:creator>")


def _check_structure(book: "epub.EpubBook", report: Report) -> None:
    items = list(book.get_items())
    report.metadata["item_count"] = len(items)

    has_nav = any(isinstance(i, epub.EpubNav) for i in items)
    has_ncx = any(isinstance(i, epub.EpubNcx) for i in items)
    if not has_nav:
        report.add("STRUCTURE", SEVERITY_ERROR, "missing_nav", "EPUB has no NAV document")
    if not has_ncx:
        # NCX is EPUB 2 legacy but most KDP-bound EPUBs include it for compatibility.
        report.add("STRUCTURE", SEVERITY_WARN, "missing_ncx", "EPUB has no NCX (EPUB 2 fallback)")

    spine_ids = [s[0] if isinstance(s, tuple) else s for s in book.spine]
    report.metadata["spine_length"] = len(spine_ids)
    if not spine_ids:
        report.add("STRUCTURE", SEVERITY_ERROR, "empty_spine", "EPUB spine is empty")

    item_id_set = {i.id for i in items if hasattr(i, "id")}
    for sid in spine_ids:
        if sid not in item_id_set:
            report.add(
                "STRUCTURE", SEVERITY_ERROR, "spine_ref_unresolved",
                f"Spine references id {sid!r} which is not in manifest",
                missing_id=sid,
            )


def _check_cover(book: "epub.EpubBook", report: Report) -> None:
    covers = [i for i in book.get_items() if isinstance(i, epub.EpubCover)]
    report.metadata["cover_count"] = len(covers)
    if not covers:
        report.add("COVER", SEVERITY_ERROR, "missing_cover", "EPUB has no cover image")
        return

    cover = covers[0]
    cover_bytes = cover.content or b""
    report.metadata["cover_filename"] = cover.file_name
    report.metadata["cover_bytes"] = len(cover_bytes)

    if not _HAS_PIL:
        report.add(
            "COVER", SEVERITY_INFO, "pil_unavailable",
            "Pillow not installed — skipping cover dimension check",
        )
        return

    try:
        with Image.open(_BytesReader(cover_bytes)) as img:
            w, h = img.size
    except Exception as exc:  # noqa: BLE001
        report.add(
            "COVER", SEVERITY_ERROR, "cover_unreadable",
            f"Cover image unreadable by Pillow: {exc}", error=str(exc),
        )
        return

    report.metadata["cover_width"] = w
    report.metadata["cover_height"] = h
    if w < KDP_COVER_MIN_W or h < KDP_COVER_MIN_H:
        report.add(
            "COVER", SEVERITY_ERROR, "cover_below_kdp_min",
            f"Cover {w}×{h} below KDP minimum {KDP_COVER_MIN_W}×{KDP_COVER_MIN_H}",
            width=w, height=h, min_w=KDP_COVER_MIN_W, min_h=KDP_COVER_MIN_H,
        )
    elif w < KDP_COVER_IDEAL_W or h < KDP_COVER_IDEAL_H:
        report.add(
            "COVER", SEVERITY_WARN, "cover_below_kdp_ideal",
            f"Cover {w}×{h} below KDP ideal {KDP_COVER_IDEAL_W}×{KDP_COVER_IDEAL_H}",
            width=w, height=h, ideal_w=KDP_COVER_IDEAL_W, ideal_h=KDP_COVER_IDEAL_H,
        )


def _is_cover_wrapper(item: "epub.EpubHtml") -> bool:
    """Heuristic: filter out the cover.xhtml wrapper that ebooklib's set_cover()
    auto-creates. The wrapper is an EpubHtml whose id is 'cover' or whose
    file_name starts with 'cover.' — neither is real chapter prose."""
    if (getattr(item, "id", "") or "").lower() == "cover":
        return True
    fn = (getattr(item, "file_name", "") or "").lower()
    return fn.startswith("cover.")


def _check_chapters(book: "epub.EpubBook", report: Report) -> None:
    docs = [
        i for i in book.get_items()
        if isinstance(i, epub.EpubHtml)
        and not isinstance(i, epub.EpubNav)
        and not _is_cover_wrapper(i)
    ]
    report.metadata["chapter_count"] = len(docs)

    if not docs:
        report.add("CHAPTERS", SEVERITY_ERROR, "no_chapter_documents", "EPUB has no chapter HTML documents")
        return

    word_count = 0
    for doc in docs:
        body = doc.content or b""
        text = re.sub(rb"<[^>]+>", b" ", body).decode("utf-8", errors="ignore")
        word_count += len(text.split())

    report.metadata["word_count"] = word_count
    if word_count < KDP_WORDCOUNT_WARN_BELOW:
        report.add(
            "WORDCOUNT", SEVERITY_WARN, "word_count_low",
            f"Total word count {word_count} is below the {KDP_WORDCOUNT_WARN_BELOW} warn threshold",
            word_count=word_count, threshold=KDP_WORDCOUNT_WARN_BELOW,
        )


def _check_epubcheck(path: Path, report: Report) -> None:
    """Optional: run W3C/IDPF epubcheck if EPUBCHECK_JAR is set."""
    jar = os.environ.get("EPUBCHECK_JAR", "").strip()
    if not jar:
        report.add(
            "EPUBCHECK", SEVERITY_INFO, "epubcheck_not_configured",
            "EPUBCHECK_JAR not set; skipping official epubcheck pass",
        )
        return
    if not Path(jar).is_file():
        report.add(
            "EPUBCHECK", SEVERITY_WARN, "epubcheck_jar_missing",
            f"EPUBCHECK_JAR points to {jar!r} but file is not present",
            jar=jar,
        )
        return
    try:
        result = subprocess.run(
            ["java", "-jar", jar, str(path), "--quiet"],
            capture_output=True, text=True, timeout=120,
        )
    except (subprocess.SubprocessError, FileNotFoundError) as exc:
        report.add(
            "EPUBCHECK", SEVERITY_WARN, "epubcheck_run_failed",
            f"epubcheck invocation failed: {exc}", error=str(exc),
        )
        return
    if result.returncode == 0:
        report.add("EPUBCHECK", SEVERITY_INFO, "epubcheck_pass", "epubcheck PASS")
    else:
        report.add(
            "EPUBCHECK", SEVERITY_ERROR, "epubcheck_fail",
            "epubcheck reported errors",
            stdout=result.stdout[:2000], stderr=result.stderr[:2000],
        )


class _BytesReader:
    """Minimal seekable file-like wrapper for raw bytes."""
    def __init__(self, data: bytes) -> None:
        import io
        self._buf = io.BytesIO(data)

    def read(self, *a: Any, **k: Any) -> bytes:
        return self._buf.read(*a, **k)

    def seek(self, *a: Any, **k: Any) -> int:
        return self._buf.seek(*a, **k)

    def tell(self) -> int:
        return self._buf.tell()

    def close(self) -> None:
        self._buf.close()


def validate_epub(path: Path) -> Report:
    report = Report(path=str(path))
    if not path.is_file():
        report.add("INPUT", SEVERITY_ERROR, "file_not_found", f"No file at {path}")
        return report
    if path.suffix.lower() != ".epub":
        report.add("INPUT", SEVERITY_WARN, "extension_not_epub", f"Extension {path.suffix!r} is not .epub")

    _check_size(path, report)
    try:
        book = epub.read_epub(str(path))
    except Exception as exc:  # noqa: BLE001
        report.add("INPUT", SEVERITY_ERROR, "epub_unreadable", f"ebooklib could not read EPUB: {exc}")
        return report

    _check_metadata(book, report)
    _check_structure(book, report)
    _check_cover(book, report)
    _check_chapters(book, report)
    _check_epubcheck(path, report)
    return report


def _print_human(report: Report) -> None:
    print(f"=== {report.path} ===")
    if report.metadata:
        print("metadata:")
        for k, v in report.metadata.items():
            print(f"  {k}: {v}")
    if report.errors:
        print(f"\n{len(report.errors)} ERROR(S):")
        for f in report.errors:
            print(f"  ❌ [{f.section}/{f.code}] {f.message}")
    if report.warns:
        print(f"\n{len(report.warns)} WARN(S):")
        for f in report.warns:
            print(f"  ⚠️  [{f.section}/{f.code}] {f.message}")
    if not report.errors and not report.warns:
        print("\n✅ all checks PASS")
    elif not report.errors:
        print(f"\n✅ no ERRORs ({len(report.warns)} WARN; KDP would accept)")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("path", help="Path to .epub file or directory (with --batch)")
    p.add_argument("--batch", action="store_true", help="Treat path as directory; validate every .epub in it")
    p.add_argument("--json", action="store_true", help="Emit JSON instead of human-readable output")
    args = p.parse_args(argv)

    target = Path(args.path)
    if args.batch:
        if not target.is_dir():
            print(f"ERROR: --batch requires a directory; got {target}", file=sys.stderr)
            return 2
        files = sorted(target.glob("*.epub"))
        if not files:
            print(f"ERROR: no .epub files in {target}", file=sys.stderr)
            return 2
        reports = [validate_epub(f) for f in files]
    else:
        reports = [validate_epub(target)]

    if args.json:
        print(json.dumps([r.to_dict() for r in reports], indent=2))
    else:
        for r in reports:
            _print_human(r)
            print()

    any_error = any(r.errors for r in reports)
    return 1 if any_error else 0


if __name__ == "__main__":
    sys.exit(main())
