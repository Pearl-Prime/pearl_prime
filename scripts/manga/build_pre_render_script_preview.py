#!/usr/bin/env python3
"""Build a pre-render HTML editorial preview for a manga chapter.

Reads a chapter_script.yaml + panel_prompts.json pair and emits a single
self-contained HTML file showing all panels in order with:
  - panel_id + beat_type + silence flag
  - composition_notes
  - FLUX prompt (collapsed with toggle for full text)
  - dialogue / narration text from the chapter script
  - locale text snippets (en_US primary; other locales when populated)

Use this BEFORE running ComfyUI renders to spot-check that the script + prompts
match operator intent. Complements scripts/manga/build_thumbnail_review_grid.py
(which is the POST-render PNG verification surface).

Usage:
    python3 scripts/manga/build_pre_render_script_preview.py \\
        --chapter-script artifacts/manga/chapter_scripts/<series>/ep_001.yaml \\
        --panel-prompts artifacts/manga/panel_prompts/<series>/ep_001.panel_prompts.json \\
        --output-html artifacts/manga/preview/<series>_ep_001_script_preview.html

    python3 scripts/manga/build_pre_render_script_preview.py --dry-run \\
        --chapter-script <yaml> --panel-prompts <json>

Tier 1 (operator-present); no LLM calls. Pure stdlib + PyYAML.
"""
from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_yaml(path: Path) -> dict:
    try:
        import yaml
    except ImportError:
        print("ERROR: PyYAML required — pip install pyyaml", file=sys.stderr)
        sys.exit(1)
    return yaml.safe_load(path.read_text())


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def _esc(s: object) -> str:
    return html.escape(str(s) if s is not None else "")


def _panel_text_locales(script_panel: dict) -> dict[str, str]:
    """Extract text_by_locale from a chapter-script panel; tolerant of nested shapes."""
    out: dict[str, str] = {}
    tbl = script_panel.get("text_by_locale") or {}
    if isinstance(tbl, dict):
        for loc, payload in tbl.items():
            if isinstance(payload, str):
                out[loc] = payload
            elif isinstance(payload, dict):
                # join meaningful string fields
                bits = []
                for k in ("dialogue", "narration", "sfx", "caption", "text"):
                    v = payload.get(k)
                    if isinstance(v, str) and v.strip():
                        bits.append(f"[{k}] {v}")
                    elif isinstance(v, list):
                        for item in v:
                            if isinstance(item, str) and item.strip():
                                bits.append(f"[{k}] {item}")
                            elif isinstance(item, dict):
                                t = item.get("text") or item.get("line")
                                if t:
                                    bits.append(f"[{k}] {t}")
                if bits:
                    out[loc] = "\n".join(bits)
    return out


def render_html(
    script: dict,
    prompts: dict,
    title: str,
) -> str:
    # Chapter script may use flat `panels`, flat `beats`, or nested `pages[].panels`
    script_panels = script.get("panels") or script.get("beats") or []
    if not script_panels:
        for page in (script.get("pages") or []):
            for p in (page.get("panels") or []):
                # propagate page_id onto panel for cross-reference
                p = dict(p)
                p.setdefault("page_id", page.get("page_id"))
                script_panels.append(p)
    prompt_panels = prompts.get("panels", [])
    # zip by panel_id where possible
    prompts_by_id = {p.get("panel_id"): p for p in prompt_panels if p.get("panel_id")}

    series_id = script.get("series_id") or prompts.get("series_id") or "(unknown)"
    chapter_id = script.get("chapter_id") or prompts.get("chapter_id") or "(unknown)"
    teacher_id = script.get("teacher_id") or "(none)"
    brand_id = script.get("brand_id") or "(none)"
    engine = script.get("engine") or "(none)"
    chapter_title = script.get("title") or working_title_from(series_id)
    locale = script.get("locale") or "en_US"
    available_locales = script.get("available_locales") or [locale]

    rows = []
    for i, sp in enumerate(script_panels, 1):
        pid = sp.get("panel_id") or sp.get("id") or f"p{i:03d}"
        pp = prompts_by_id.get(pid, {})
        beat_type = pp.get("beat_type") or sp.get("beat_type") or "—"
        silence = "🔇 silent" if pp.get("silence_confirmed") or sp.get("silence_confirmed") else ""
        comp_notes = pp.get("composition_notes") or sp.get("composition_notes") or ""
        prompt = pp.get("prompt") or pp.get("flux_prompt") or ""
        neg = pp.get("negative_prompt", "")
        text_locales = _panel_text_locales(sp)

        locale_blocks = []
        for loc in available_locales:
            t = text_locales.get(loc, "").strip()
            if t:
                locale_blocks.append(
                    f'<details open><summary><strong>text · {_esc(loc)}</strong></summary>'
                    f'<pre style="white-space:pre-wrap">{_esc(t)}</pre></details>'
                )
            else:
                locale_blocks.append(
                    f'<details><summary>text · {_esc(loc)} <em style="color:#888">(empty)</em></summary></details>'
                )

        rows.append(f"""
<tr>
  <td class="pid">
    <strong>{_esc(pid)}</strong><br>
    <span class="beat">{_esc(beat_type)}</span> {_esc(silence)}
  </td>
  <td class="comp">
    <strong>composition</strong>
    <pre style="white-space:pre-wrap">{_esc(comp_notes) or '<em style="color:#888">(none)</em>'}</pre>
    <details><summary>FLUX prompt ({len(prompt)} chars)</summary>
      <pre style="white-space:pre-wrap;font-size:.7rem">{_esc(prompt)}</pre>
    </details>
    {f'<details><summary>negative ({len(neg)} chars)</summary><pre style="white-space:pre-wrap;font-size:.7rem">{_esc(neg)}</pre></details>' if neg else ''}
  </td>
  <td class="text">
    {''.join(locale_blocks) or '<em style="color:#888">(no text)</em>'}
  </td>
</tr>
""")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{_esc(title)}</title>
<style>
  body {{ font-family: -apple-system, system-ui, sans-serif; background: #0e0a06; color: #faf6f0; padding: 1rem; max-width: 1400px; margin: 0 auto; }}
  h1 {{ font-weight: 400; letter-spacing: 0.04em; margin-bottom: 0.25rem; }}
  .meta {{ color: rgba(250,246,240,.6); font-size: 0.8rem; margin-bottom: 0.5rem; }}
  .meta-table {{ font-family: 'DM Mono', monospace; font-size: 0.75rem; border-collapse: collapse; margin: 0.5rem 0 1.5rem 0; }}
  .meta-table td {{ padding: 0.15rem 0.5rem; border-bottom: 1px solid rgba(250,246,240,.05); }}
  .meta-table td:first-child {{ color: rgba(250,246,240,.45); text-transform: uppercase; }}
  .summary {{ margin-bottom: 1.5rem; padding: 0.75rem 1rem; background: rgba(250,246,240,.04); border-left: 3px solid #c0a878; font-size: 0.85rem; }}
  table.panels {{ border-collapse: collapse; width: 100%; }}
  table.panels th, table.panels td {{ padding: 0.75rem; border-bottom: 1px solid rgba(250,246,240,.08); vertical-align: top; }}
  table.panels th {{ text-transform: uppercase; letter-spacing: 0.1em; font-size: 0.7rem; color: rgba(250,246,240,.55); font-weight: 500; text-align: left; background: rgba(250,246,240,.03); }}
  td.pid {{ width: 120px; font-family: 'DM Mono', monospace; font-size: 0.78rem; }}
  td.pid .beat {{ color: rgba(250,246,240,.55); font-size: 0.7rem; text-transform: uppercase; }}
  td.comp {{ width: 50%; font-size: 0.85rem; }}
  td.text {{ width: 35%; font-size: 0.8rem; }}
  pre {{ margin: 0.25rem 0; color: rgba(250,246,240,.85); font-family: 'DM Mono', monospace; font-size: 0.75rem; background: rgba(250,246,240,.02); padding: 0.4rem; border-radius: 2px; }}
  details summary {{ cursor: pointer; color: rgba(250,246,240,.65); font-size: 0.75rem; padding: 0.2rem 0; }}
  details[open] summary {{ color: rgba(250,246,240,.85); }}
  strong {{ color: rgba(250,246,240,.95); }}
</style>
</head>
<body>
  <h1>{_esc(chapter_title)}</h1>
  <div class="meta">{_esc(series_id)} · {_esc(chapter_id)}</div>
  <table class="meta-table">
    <tr><td>brand_id</td><td>{_esc(brand_id)}</td></tr>
    <tr><td>teacher_id</td><td>{_esc(teacher_id)}</td></tr>
    <tr><td>engine</td><td>{_esc(engine)}</td></tr>
    <tr><td>locale (primary)</td><td>{_esc(locale)}</td></tr>
    <tr><td>available_locales</td><td>{_esc(', '.join(available_locales))}</td></tr>
    <tr><td>panels</td><td>{len(script_panels)}</td></tr>
    <tr><td>silent panels</td><td>{sum(1 for p in prompt_panels if p.get('silence_confirmed'))} ({sum(1 for p in prompt_panels if p.get('silence_confirmed'))*100//max(1,len(prompt_panels))}%)</td></tr>
  </table>
  <div class="summary">
    <strong>Pre-render editorial review.</strong> Walk panels in order; check beat-type pacing flow ·
    composition variety · prompt specificity · text/dialogue voice consistency · locale gaps.
    Use <code>scripts/manga/build_thumbnail_review_grid.py</code> POST-render against the rendered PNGs.
  </div>
  <table class="panels">
    <thead><tr><th>panel</th><th>composition + FLUX prompt</th><th>dialogue / text by locale</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
</body>
</html>"""


def working_title_from(series_id: str) -> str:
    return series_id.split("__")[-1].replace("_", " ").title() if series_id else "Manga preview"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--chapter-script", required=True, help="Path to chapter_script.yaml")
    ap.add_argument("--panel-prompts", required=True, help="Path to panel_prompts.json")
    ap.add_argument("--output-html", default=None, help="Output HTML path (default: <script_dir>/<chapter>_script_preview.html)")
    ap.add_argument("--title", default=None, help="Page title (default: derived from chapter title)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    script_path = Path(args.chapter_script).resolve()
    prompts_path = Path(args.panel_prompts).resolve()
    if not script_path.is_file():
        print(f"ERROR: --chapter-script not a file: {script_path}", file=sys.stderr)
        return 1
    if not prompts_path.is_file():
        print(f"ERROR: --panel-prompts not a file: {prompts_path}", file=sys.stderr)
        return 1

    script = _load_yaml(script_path)
    prompts = _load_json(prompts_path)

    if args.output_html:
        out_path = Path(args.output_html).resolve()
    else:
        out_path = script_path.with_name(f"{script_path.stem}_script_preview.html")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    title = args.title or f"{script.get('title') or working_title_from(script.get('series_id', ''))} — script preview"

    if args.dry_run:
        print(f"[dry-run] would write {out_path}", file=sys.stderr)
        return 0

    body = render_html(script, prompts, title)
    out_path.write_text(body)
    print(f"wrote {out_path}", file=sys.stderr)
    print(f"\nOpen in browser:\n  open {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
