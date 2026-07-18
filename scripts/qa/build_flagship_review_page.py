#!/usr/bin/env python3
"""Stage 4: emit reader / annotated / provenance HTML from a flagship render dir.

Usage:
  python3 scripts/qa/build_flagship_review_page.py \\
    --render-dir artifacts/qa/my_flagship_build/render \\
    --out artifacts/qa/my_flagship_build/review.html
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_CHAPTER_SPLIT = re.compile(r"^(Chapter\s+\d+.*)$", re.M)


def _split_chapters(book_text: str) -> list[tuple[str, str]]:
    parts = _CHAPTER_SPLIT.split(book_text.strip())
    if len(parts) < 3:
        return [("Book", book_text.strip())]
    out: list[tuple[str, str]] = []
    if parts[0].strip():
        out.append(("Front matter", parts[0].strip()))
    for i in range(1, len(parts), 2):
        title = parts[i].strip()
        body = parts[i + 1].strip() if i + 1 < len(parts) else ""
        out.append((title, body))
    return out


def _load_provenance(render_dir: Path) -> dict:
    prov: dict = {"render_dir": str(render_dir)}
    for name in (
        "quality_summary.json",
        "register_gate_report.json",
        "selected_content_variants.json",
        "section_packet_audit.json",
    ):
        p = render_dir / name
        if p.exists():
            try:
                prov[name] = json.loads(p.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                prov[name] = {"_error": "unparseable"}
    return prov


def _render_html(book_text: str, *, title: str, provenance: dict) -> str:
    chapters = _split_chapters(book_text)
    toc = []
    body_parts = []
    for i, (ch_title, ch_body) in enumerate(chapters):
        anchor = f"ch-{i}"
        toc.append(f'<li><a href="#{anchor}">{html.escape(ch_title)}</a></li>')
        paras = "".join(
            f"<p>{html.escape(p.strip())}</p>"
            for p in ch_body.split("\n\n")
            if p.strip()
        )
        body_parts.append(
            f'<section id="{anchor}" class="chapter">'
            f"<h2>{html.escape(ch_title)}</h2>{paras}</section>"
        )
    prov_json = html.escape(json.dumps(provenance, indent=2)[:12000])
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>{html.escape(title)}</title>
  <style>
    body {{ font-family: Georgia, serif; max-width: 42rem; margin: 2rem auto; line-height: 1.6; color: #1a1a1a; }}
    nav {{ background: #f6f6f6; padding: 1rem; border-radius: 6px; margin-bottom: 2rem; }}
    nav ul {{ margin: 0; padding-left: 1.2rem; }}
    .chapter {{ margin-bottom: 3rem; padding-bottom: 2rem; border-bottom: 1px solid #ddd; }}
    .provenance {{ font-family: ui-monospace, monospace; font-size: 0.75rem; background: #fafafa;
                   padding: 1rem; white-space: pre-wrap; border: 1px solid #eee; margin-top: 3rem; }}
    h1 {{ font-size: 1.4rem; }}
    h2 {{ font-size: 1.15rem; margin-top: 0; }}
  </style>
</head>
<body>
  <h1>{html.escape(title)}</h1>
  <p><em>Reader view — {len(book_text.split()):,} words · {len(chapters)} sections</em></p>
  <nav><strong>Contents</strong><ul>{"".join(toc)}</ul></nav>
  {"".join(body_parts)}
  <details><summary>Provenance (build dir artifacts)</summary>
    <div class="provenance">{prov_json}</div>
  </details>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--title", default="Flagship Review — gen_z × anxiety")
    args = parser.parse_args()

    book_path = args.render_dir / "book.txt"
    if not book_path.exists():
        print(f"FAIL: {book_path} missing", file=sys.stderr)
        return 2

    book_text = book_path.read_text(encoding="utf-8")
    provenance = _load_provenance(args.render_dir)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(_render_html(book_text, title=args.title, provenance=provenance), encoding="utf-8")
    print(f"wrote {args.out} ({len(book_text.split()):,} words)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
