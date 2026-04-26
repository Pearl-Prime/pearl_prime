#!/usr/bin/env python3
"""Build an HTML thumbnail-grid review surface for rendered manga panels.

Scans a directory of rendered PNGs (from ComfyUI / RunComfy / Pearl Star),
groups by chapter + panel_id, and emits a single self-contained HTML file
the operator can open in any browser to spot-check the renders.

Use cases:
- After Pearl Star ComfyUI render run completes for ep_001, generate the grid
  to QA the 35 panels in one screen
- Side-by-side bubble-overlay diff for en_US vs ja_JP versions of the same
  panel (when --compare-locale is supplied)

Tier 1 (operator-present); no LLM calls.

Usage:
    python3 scripts/manga/build_thumbnail_review_grid.py \\
        --input-dir artifacts/manga/<series>/panels/ep_001/ \\
        --output-html artifacts/manga/<series>/review/ep_001_grid.html

    python3 scripts/manga/build_thumbnail_review_grid.py \\
        --input-dir artifacts/manga/<series>/panels/ep_001/ \\
        --compare-locale artifacts/manga/<series>/panels_ja_JP/ep_001/ \\
        --output-html artifacts/manga/<series>/review/ep_001_locale_compare.html

    python3 scripts/manga/build_thumbnail_review_grid.py --dry-run --input-dir <dir>
"""
from __future__ import annotations

import argparse
import html
import os
import re
import sys
from pathlib import Path


def _rel(target: Path, base: Path) -> str:
    """Return a relative path even when target is not a subpath of base."""
    return os.path.relpath(target, base)

REPO_ROOT = Path(__file__).resolve().parents[2]

PANEL_ID_RE = re.compile(r"(?:ep[_-]?(\d+)[_-]?)?(?:p(?:age)?[_-]?(\d+)[_-]?)?(\d+)?", re.IGNORECASE)


def collect_panels(input_dir: Path) -> list[Path]:
    """Sort panels by filename so ep_001_001.png precedes ep_001_002.png."""
    if not input_dir.is_dir():
        return []
    return sorted([p for p in input_dir.rglob("*.png") if p.is_file()])


def panel_label(p: Path) -> str:
    return p.stem.replace("_", " ")


def render_html(
    primary_panels: list[Path],
    compare_panels: list[Path] | None,
    title: str,
    base_dir: Path,
) -> str:
    """Build the HTML doc as a single self-contained string."""
    rows = []
    if compare_panels:
        # Side-by-side: assume same panel_id matches across locales
        compare_by_stem = {p.stem: p for p in compare_panels}
        for primary in primary_panels:
            cmp = compare_by_stem.get(primary.stem)
            cmp_cell = (
                f'<td><a href="{html.escape(str(_rel(cmp, base_dir)))}" target="_blank">'
                f'<img src="{html.escape(str(_rel(cmp, base_dir)))}" loading="lazy" '
                f'style="max-width:240px;max-height:340px"></a></td>'
                if cmp
                else '<td><em style="color:#888">missing</em></td>'
            )
            rows.append(
                f"<tr>"
                f'<td><strong>{html.escape(panel_label(primary))}</strong></td>'
                f'<td><a href="{html.escape(str(_rel(primary, base_dir)))}" target="_blank">'
                f'<img src="{html.escape(str(_rel(primary, base_dir)))}" loading="lazy" '
                f'style="max-width:240px;max-height:340px"></a></td>'
                f"{cmp_cell}"
                f"</tr>"
            )
        header_extra = "<th>compare</th>"
    else:
        for primary in primary_panels:
            rows.append(
                f"<tr>"
                f'<td><strong>{html.escape(panel_label(primary))}</strong></td>'
                f'<td><a href="{html.escape(str(_rel(primary, base_dir)))}" target="_blank">'
                f'<img src="{html.escape(str(_rel(primary, base_dir)))}" loading="lazy" '
                f'style="max-width:320px;max-height:480px"></a></td>'
                f"</tr>"
            )
        header_extra = ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{html.escape(title)}</title>
<style>
  body {{ font-family: -apple-system, system-ui, sans-serif; background: #0e0a06; color: #faf6f0; padding: 1rem; }}
  h1 {{ font-weight: 400; letter-spacing: 0.04em; margin-bottom: 0.25rem; }}
  .meta {{ color: rgba(250,246,240,.45); font-size: 0.8rem; margin-bottom: 1.5rem; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th, td {{ padding: 0.5rem; text-align: center; border-bottom: 1px solid rgba(250,246,240,.08); vertical-align: middle; }}
  th {{ text-transform: uppercase; letter-spacing: 0.1em; font-size: 0.7rem; color: rgba(250,246,240,.55); font-weight: 500; }}
  td:first-child {{ text-align: left; font-family: 'DM Mono', monospace; font-size: 0.75rem; color: rgba(250,246,240,.65); }}
  img {{ border: 1px solid rgba(250,246,240,.1); display: block; margin: 0 auto; }}
  a {{ display: block; }}
  .summary {{ margin-bottom: 1.5rem; padding: 0.75rem 1rem; background: rgba(250,246,240,.04); border-left: 3px solid #c0a878; }}
</style>
</head>
<body>
  <h1>{html.escape(title)}</h1>
  <div class="meta">{len(primary_panels)} panel(s) · review surface · click thumbnail for full size</div>
  <div class="summary">
    Spot-check tips: scan for color palette consistency · character continuity · panel composition flow ·
    bubble placement (in compare view) · text legibility at thumbnail scale = legible at print scale.
  </div>
  <table>
    <thead><tr><th>panel</th><th>render</th>{header_extra}</tr></thead>
    <tbody>
      {''.join(rows)}
    </tbody>
  </table>
</body>
</html>"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input-dir", required=True, help="Directory of rendered panel PNGs")
    ap.add_argument("--compare-locale", default=None, help="Optional second directory for side-by-side locale comparison")
    ap.add_argument("--output-html", default=None, help="Output HTML path (default: <input-dir>/review_grid.html)")
    ap.add_argument("--title", default=None, help="Page title (default: derived from input dir)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    input_dir = Path(args.input_dir).resolve()
    if not input_dir.is_dir():
        print(f"ERROR: --input-dir not a directory: {input_dir}", file=sys.stderr)
        return 1

    out_path = Path(args.output_html).resolve() if args.output_html else input_dir / "review_grid.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    title = args.title or f"Review · {input_dir.name}"

    primary = collect_panels(input_dir)
    compare = collect_panels(Path(args.compare_locale).resolve()) if args.compare_locale else None

    print(f"primary panels: {len(primary)}", file=sys.stderr)
    if compare is not None:
        print(f"compare panels: {len(compare)}", file=sys.stderr)

    if args.dry_run:
        print(f"[dry-run] would write {out_path}", file=sys.stderr)
        return 0

    base_dir = out_path.parent
    body = render_html(primary, compare, title, base_dir)
    out_path.write_text(body)
    print(f"wrote {out_path}", file=sys.stderr)
    print(f"\nOpen in browser:\n  open {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
