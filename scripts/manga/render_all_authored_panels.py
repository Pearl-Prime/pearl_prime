#!/usr/bin/env python3
"""Render every authored panel_prompts.json via Pearl Star queue (or direct ComfyUI).

Discovers ``artifacts/manga/panel_prompts/<series>/ep_*.panel_prompts.json`` and
invokes ``queue_panel_renders.py`` per episode. Resumable via ``--skip-existing``.

Scope reality (2026-06-24): only series with Pearl_Author-authored panel_prompts
can render. The canonical 37-brand list is in
``config/manga/canonical_brand_list.yaml``; most brands lack chapter_scripts +
panel_prompts until content is authored.

Usage:
    python3 scripts/manga/render_all_authored_panels.py --dry-run
    python3 scripts/manga/render_all_authored_panels.py --via-queue
    python3 scripts/manga/render_all_authored_panels.py --brand stillness_press --via-queue
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PANEL_PROMPTS_DIR = REPO_ROOT / "artifacts" / "manga" / "panel_prompts"
PANELS_OUT_DIR = REPO_ROOT / "artifacts" / "manga" / "panels"
PROGRESS_DIR = REPO_ROOT / "artifacts" / "manga"
SENTINEL_DIR = REPO_ROOT / "artifacts" / "manga" / "sentinels"
QUEUE_RENDER = REPO_ROOT / "scripts" / "manga" / "queue_panel_renders.py"
_DEFAULT_H1A = REPO_ROOT / "scripts" / "image_generation" / "comfyui_workflows" / "flux_txt2img_manga.json"
H1A_WORKFLOW = Path(os.environ["MANGA_WORKFLOW_PATH"]) if os.environ.get("MANGA_WORKFLOW_PATH") else _DEFAULT_H1A
DEFAULT_COMFY_URL = os.environ.get("PS_COMFY_URL") or os.environ.get("COMFYUI_URL") or "http://127.0.0.1:8188"

sys.path.insert(0, str(REPO_ROOT))
from scripts.manga.manga_series_plan_ssot import canonical_brand_ids  # noqa: E402


def log(msg: str) -> None:
    print(f"[bulk {time.strftime('%H:%M:%S')}] {msg}", flush=True)


def discover_episodes(*, brand: str | None) -> list[tuple[str, str, Path]]:
    """Return (series_id, chapter_id, panel_prompts_path) sorted."""
    out: list[tuple[str, str, Path]] = []
    for pp in sorted(PANEL_PROMPTS_DIR.rglob("*.panel_prompts.json")):
        series_id = pp.parent.name
        if brand and not series_id.startswith(f"{brand}__"):
            continue
        chapter_id = pp.name.replace(".panel_prompts.json", "")
        out.append((series_id, chapter_id, pp))
    return out


def count_panels(pp: Path) -> int:
    data = json.loads(pp.read_text())
    return len(data.get("prompts") or data.get("panels") or [])


def count_rendered(series_id: str, chapter_id: str) -> int:
    out = PANELS_OUT_DIR / series_id / chapter_id
    if not out.is_dir():
        return 0
    return sum(1 for p in out.glob("*.png") if p.stat().st_size > 1024)


def render_episode(series_id: str, chapter_id: str, pp: Path, *, via_queue: bool, dry_run: bool) -> int:
    out_dir = PANELS_OUT_DIR / series_id / chapter_id
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        str(QUEUE_RENDER),
        "--panel-prompts",
        str(pp),
        "--output-dir",
        str(out_dir),
        "--workflow-path",
        str(H1A_WORKFLOW),
        "--skip-existing",
    ]
    if via_queue:
        cmd.append("--via-queue")
    else:
        cmd.extend(["--comfy-url", DEFAULT_COMFY_URL])
    log(f"  cmd: {' '.join(cmd[1:])}")
    if dry_run:
        return 0
    return subprocess.run(cmd, cwd=REPO_ROOT).returncode


def brand_gap_report() -> None:
    canon = canonical_brand_ids()
    authored = sorted({p.parent.name.split("__")[0] for p in PANEL_PROMPTS_DIR.rglob("*.panel_prompts.json")})
    missing = [b for b in canon if b not in authored]
    log(f"canonical brands: {len(canon)} | with panel_prompts: {len(authored)} | missing content: {len(missing)}")
    if missing:
        log(f"  no panel_prompts yet: {', '.join(missing[:8])}{'...' if len(missing) > 8 else ''}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--brand", help="Filter to one brand_id prefix (e.g. stillness_press)")
    ap.add_argument("--via-queue", action="store_true", help="Pearl Star Procrastinate queue (recommended on-box)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max-retries", type=int, default=2)
    ap.add_argument("--report-only", action="store_true", help="Print inventory and 37-brand gap; do not render")
    args = ap.parse_args()

    SENTINEL_DIR.mkdir(parents=True, exist_ok=True)
    episodes = discover_episodes(brand=args.brand)
    if not episodes:
        log("No panel_prompts found.")
        brand_gap_report()
        return 1

    total_need = sum(count_panels(pp) for _, _, pp in episodes)
    total_have = sum(count_rendered(s, c) for s, c, _ in episodes)
    log(f"episodes: {len(episodes)} | panels: {total_have}/{total_need} already rendered")
    brand_gap_report()
    if args.report_only:
        for series_id, chapter_id, pp in episodes:
            n = count_panels(pp)
            have = count_rendered(series_id, chapter_id)
            log(f"  {series_id}/{chapter_id}: {have}/{n}")
        return 0

    progress_path = PROGRESS_DIR / f"bulk_render_progress_authored_{time.strftime('%Y-%m-%d', time.gmtime())}.tsv"
    new_file = not progress_path.exists()
    fail = 0

    for series_id, chapter_id, pp in episodes:
        sentinel = SENTINEL_DIR / f"authored_render_{series_id}__{chapter_id}.ok"
        n = count_panels(pp)
        have = count_rendered(series_id, chapter_id)
        if have >= n and n > 0:
            log(f"[skip] {series_id}/{chapter_id} complete ({have}/{n})")
            continue
        if sentinel.exists() and have >= n:
            log(f"[skip] {series_id}/{chapter_id} (sentinel)")
            continue

        log(f"=== {series_id}/{chapter_id} ({have}/{n} panels) ===")
        rc = 1
        for attempt in range(args.max_retries):
            if attempt:
                backoff = (2 ** attempt) * 15
                log(f"  retry {attempt + 1}/{args.max_retries} after {backoff}s")
                time.sleep(backoff)
            rc = render_episode(series_id, chapter_id, pp, via_queue=args.via_queue, dry_run=args.dry_run)
            if rc == 0:
                break
        have_after = count_rendered(series_id, chapter_id)
        status = "ok" if rc == 0 and have_after >= n else "partial" if have_after > have else "failed"
        with progress_path.open("a") as f:
            if new_file:
                f.write("ts\tseries_id\tchapter_id\tstatus\thave\ttotal\n")
                new_file = False
            f.write(
                f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\t{series_id}\t{chapter_id}\t{status}\t{have_after}\t{n}\n"
            )
        if status != "ok":
            fail += 1
            log(f"  {status.upper()} {chapter_id} ({have_after}/{n})")
        else:
            sentinel.write_text(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} panels={have_after}\n")
            log(f"  OK {chapter_id} ({have_after}/{n})")

    if fail:
        log(f"done with {fail} episode failure(s)")
        return 1
    log("all authored episodes complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
