#!/usr/bin/env python3
"""Operator-facing bulk status dashboard for the ja_JP × stillness_press run.

Reads:
  - ``artifacts/manga/sentinels/*.flag`` and ``*.ok``
  - ``artifacts/manga/bulk_render_progress_ja_jp_*.tsv`` (most recent)
  - recent ``git log`` matching ``progress(ja_jp_bulk):``

Writes a single-file self-contained HTML at:
  ``artifacts/manga/bulk_dashboard_ja_jp.html``

Then syncs the HTML to R2 (via ``rclone copyto``) so the operator can open the
URL from any device. Returns the public R2 URL template on stdout.

Designed to run hourly via cron or on-demand from the orchestrator. Idempotent
and side-effect-free besides the HTML write + R2 upload.

Usage:
    python3 scripts/manga/bulk_status_dashboard.py [--no-upload]
"""
from __future__ import annotations

import argparse
import html
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SENTINEL_DIR = REPO_ROOT / "artifacts" / "manga" / "sentinels"
PROGRESS_DIR = REPO_ROOT / "artifacts" / "manga"
DASHBOARD_PATH = PROGRESS_DIR / "bulk_dashboard_ja_jp.html"


def gather_sentinels() -> list[tuple[str, str]]:
    if not SENTINEL_DIR.exists():
        return []
    rows = []
    for s in sorted(SENTINEL_DIR.iterdir()):
        if s.is_file():
            try:
                content = s.read_text()[:1500]
            except Exception:
                content = "(unreadable)"
            rows.append((s.name, content))
    return rows


def latest_progress_tsv() -> Path | None:
    candidates = sorted(PROGRESS_DIR.glob("bulk_render_progress_ja_jp_*.tsv"))
    return candidates[-1] if candidates else None


def gather_progress_rows() -> list[dict]:
    path = latest_progress_tsv()
    if not path:
        return []
    rows: list[dict] = []
    try:
        lines = path.read_text().splitlines()
    except Exception:
        return []
    if not lines:
        return []
    headers = lines[0].split("\t")
    for line in lines[1:]:
        parts = line.split("\t")
        rows.append(dict(zip(headers, parts)))
    return rows


def gather_recent_commits(limit: int = 30) -> list[str]:
    try:
        r = subprocess.run(
            ["git", "log", "--oneline", "--no-decorate", f"-{limit}", "--grep=progress(ja_jp_bulk):"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=20,
        )
        if r.returncode != 0:
            return []
        return r.stdout.strip().splitlines()
    except Exception:
        return []


def render_html() -> str:
    now = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    sentinels = gather_sentinels()
    progress = gather_progress_rows()
    commits = gather_recent_commits()

    smoke_ok = any(name == "SMOKE_OK_ja_jp_stillness.flag" for name, _ in sentinels)
    smoke_failed = any(name == "SMOKE_FAILED.flag" for name, _ in sentinels)
    bulk_complete = any(name == "BULK_COMPLETE_ja_jp_stillness.flag" for name, _ in sentinels)

    if smoke_failed:
        banner_state = ("FAILED — operator review needed", "#7a0000")
    elif bulk_complete:
        banner_state = ("BULK COMPLETE", "#0a5a00")
    elif smoke_ok:
        banner_state = ("BULK RUNNING (Phase 2)", "#0a4a8a")
    else:
        banner_state = ("PHASE 0/1 IN PROGRESS", "#7a5a00")

    rows_html = ""
    if progress:
        rows_html = '<table style="width:100%;border-collapse:collapse"><tr style="background:#222"><th style="text-align:left;padding:6px">ts</th><th style="text-align:left;padding:6px">series_id</th><th style="text-align:left;padding:6px">chapter_id</th><th style="text-align:left;padding:6px">status</th><th style="text-align:right;padding:6px">n_panels</th></tr>'
        for row in progress[-100:]:
            rows_html += "<tr style='border-top:1px solid #333'>"
            for k in ("ts", "series_id", "chapter_id", "status", "n_panels"):
                v = html.escape(row.get(k, "—"))
                style = "padding:6px"
                if k == "status":
                    if "fail" in v.lower():
                        style += ";color:#ff8080"
                    elif v == "ok":
                        style += ";color:#80ff80"
                rows_html += f'<td style="{style}">{v}</td>'
            rows_html += "</tr>"
        rows_html += "</table>"
    else:
        rows_html = '<p style="color:#888">No progress.tsv rows yet.</p>'

    commits_html = "<ol>" + "".join(f"<li><code>{html.escape(c)}</code></li>" for c in commits[:30]) + "</ol>" if commits else '<p style="color:#888">No progress commits yet.</p>'

    sentinels_html = ""
    for name, content in sentinels:
        sentinels_html += f"<details style='margin-bottom:6px'><summary style='cursor:pointer'><code>{html.escape(name)}</code></summary><pre style='background:#111;padding:8px;border-radius:4px;color:#ccc;overflow:auto'>{html.escape(content)}</pre></details>"
    if not sentinels_html:
        sentinels_html = '<p style="color:#888">No sentinel files yet.</p>'

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>ja_JP × stillness_press bulk dashboard</title>
<style>
body {{font-family: -apple-system, BlinkMacSystemFont, sans-serif; background:#0a0a0a; color:#eee; margin:0; padding:20px; max-width: 1200px; margin: 0 auto}}
h1, h2 {{margin: 16px 0 12px 0}}
.banner {{padding: 24px; border-radius: 12px; background: {banner_state[1]}; color: white; font-size: 24px; font-weight: 600; margin-bottom: 20px}}
.meta {{color:#888; font-size: 12px; margin-bottom: 18px}}
section {{background:#161616; padding:18px; border-radius:8px; margin-bottom:16px}}
table {{font-size:13px}}
code {{background:#222; padding:2px 5px; border-radius:3px; font-size:12px}}
</style></head>
<body>
<h1>ja_JP × stillness_press — Pearl Star autonomous bulk render</h1>
<div class="meta">Generated {now} · refreshed hourly by <code>scripts/manga/bulk_status_dashboard.py</code></div>
<div class="banner">{html.escape(banner_state[0])}</div>

<section>
  <h2>Sentinels</h2>
  {sentinels_html}
</section>

<section>
  <h2>Recent progress (last 100 rows)</h2>
  {rows_html}
</section>

<section>
  <h2>Recent <code>progress(ja_jp_bulk):</code> commits</h2>
  {commits_html}
</section>

<section style="font-size:13px; color:#888">
  <h2>Operator commands</h2>
  <p>Monitor live: <code>ssh pearl_star "tail -100 ~/phoenix_omega/artifacts/manga/bulk_logs/ja_jp_full_*.log"</code></p>
  <p>Abort: <code>ssh pearl_star "pkill -f orchestrate_ja_jp_stillness_full_render"</code></p>
  <p>Resume after abort: <code>ssh pearl_star</code>, then re-run the 3-command start sequence (orchestrator skips completed work via sentinels).</p>
  <p>Runbook: <code>docs/runbooks/JA_JP_STILLNESS_PEARL_STAR_BULK_RUNBOOK.md</code></p>
</section>

</body></html>
"""


def upload_to_r2() -> str | None:
    bucket = os.environ.get("R2_BUCKET", "phoenix-omega-artifacts")
    rclone = shutil.which("rclone") or os.path.expanduser("~/.local/bin/rclone")
    if not Path(rclone).exists():
        return None
    dest = f"r2:{bucket}/manga/bulk_dashboard_ja_jp.html"
    rc = subprocess.run(
        [rclone, "copyto", "--header-upload", "Content-Type: text/html; charset=utf-8", str(DASHBOARD_PATH), dest],
        capture_output=True, text=True, timeout=120,
    )
    if rc.returncode == 0:
        return dest
    return None


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--no-upload", action="store_true")
    args = p.parse_args()

    DASHBOARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    DASHBOARD_PATH.write_text(render_html())
    print(f"wrote: {DASHBOARD_PATH}", flush=True)

    if args.no_upload:
        return 0
    dest = upload_to_r2()
    if dest:
        print(f"uploaded: {dest}", flush=True)
        # Public URL template — operator's R2 bucket public binding determines the actual prefix.
        # If a public binding is set (custom domain or r2.dev), the dashboard lives at:
        #   https://<public-binding>/manga/bulk_dashboard_ja_jp.html
        bucket = os.environ.get("R2_BUCKET", "phoenix-omega-artifacts")
        print(f"public URL (if bucket has public binding): https://<r2-public-url>/manga/bulk_dashboard_ja_jp.html (bucket={bucket})", flush=True)
    else:
        print("R2 upload skipped or failed; local copy only.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
