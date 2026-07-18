#!/usr/bin/env python3
"""Freeze an approved full-book render as golden snapshot #2 (operator ratification required).

Writes CANONICAL_FLAGSHIP_BOOK.txt + updates CANONICAL_FLAGSHIP_BOOK_METADATA.json.
Run only after operator read approval; PR must carry GOLDEN-UPDATE-RATIFIED: <OPD>.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BOOK_OUT = REPO_ROOT / "artifacts/qa/snapshots/CANONICAL_FLAGSHIP_BOOK.txt"
META_OUT = REPO_ROOT / "artifacts/qa/snapshots/CANONICAL_FLAGSHIP_BOOK_METADATA.json"
CHAPTER_SPLIT = __import__("re").compile(r"^Chapter\s+(\d+)\b", __import__("re").M)


def _chapter_shas(book_text: str) -> dict[str, str]:
    import re

    matches = list(CHAPTER_SPLIT.finditer(book_text))
    out: dict[str, str] = {}
    for i, m in enumerate(matches):
        ch = m.group(1)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(book_text)
        body = book_text[start:end].strip()
        out[f"ch{ch}"] = hashlib.sha256(body.encode("utf-8")).hexdigest()
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render-dir", type=Path, required=True)
    parser.add_argument("--seed", default="flagship_phase2_layer6")
    parser.add_argument("--ratify-opd", required=True, help="OPD ref for GOLDEN-UPDATE-RATIFIED")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    book_path = args.render_dir / "book.txt"
    if not book_path.exists():
        print(f"FAIL: {book_path} missing", file=sys.stderr)
        return 2

    book_text = book_path.read_text(encoding="utf-8")
    normalized = book_text.rstrip() + "\n"
    book_bytes = normalized.encode("utf-8")
    sha = hashlib.sha256(book_bytes).hexdigest()

    meta = json.loads(META_OUT.read_text(encoding="utf-8"))
    meta.update({
        "status": "ratified",
        "ratified_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "seed": args.seed,
        "content_sha256": sha,
        "word_count": len(normalized.split()),
        "byte_count": len(book_bytes),
        "chapter_content_sha256": _chapter_shas(normalized),
        "ratify_opd": args.ratify_opd,
    })

    if args.dry_run:
        print(f"would write {BOOK_OUT.name} ({len(book_bytes):,} bytes, sha256={sha[:16]}…)")
        return 0

    BOOK_OUT.write_text(normalized, encoding="utf-8")
    META_OUT.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"frozen full-book golden: {BOOK_OUT}")
    print(f"sha256: {sha}")
    print(f"ratify with GOLDEN-UPDATE-RATIFIED: {args.ratify_opd}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
