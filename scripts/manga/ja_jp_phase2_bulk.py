#!/usr/bin/env python3
"""Phase 2 bulk — render remaining ja_JP series (post Phase 1 auto-validation).

Auto-discovers en_US chapter scripts under
``artifacts/manga/chapter_scripts/stillness_press__*__en_US__*/`` (minus the
Phase 1 smoke series) and renders panels + bubbles per chapter, sequentially
per series (one series at a time keeps VRAM headroom for any co-tenant work
on Pearl Star — e.g., ``ws_teacher_manga_triptych_20260410``).

Gated on Phase 1 sentinel ``SMOKE_OK_ja_jp_stillness.flag``. Refuses to start
if ``SMOKE_FAILED.flag`` exists or ``SMOKE_OK`` doesn't.

Per-chapter loop:
  1. queue_panel_renders.py (H1=A workflow, --skip-existing)
  2. bubble_render for locale=ja_JP
  3. Daily progress TSV append at
     ``artifacts/manga/bulk_render_progress_ja_jp_<date>.tsv``
  4. R2 upload of finished chapter via rclone copyto (skip if --skip-r2)

Resumable: per-panel via --skip-existing inside queue_panel_renders.py; per-chapter
via sentinel ``artifacts/manga/sentinels/ja_jp_phase2_<series>__<chapter>.ok``.

Today (2026-06-02) the only authored en_US source is ``the_alarm_is_lying``
which Phase 1 already covers, so Phase 2 has zero work to do — and that is
correct. It exits 0 with "nothing-to-render" rather than failing. When more
en_US chapters get authored, re-running the orchestrator picks them up.

Usage:
    python3 scripts/manga/ja_jp_phase2_bulk.py [--include-phase1-series]
                                                [--dry-run]
                                                [--skip-r2]
                                                [--skip-commit]
                                                [--max-retries N]
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SENTINEL_DIR = REPO_ROOT / "artifacts" / "manga" / "sentinels"
LOG_DIR = REPO_ROOT / "artifacts" / "manga" / "bulk_logs"
CHAPTER_SCRIPTS_DIR = REPO_ROOT / "artifacts" / "manga" / "chapter_scripts"
PANEL_PROMPTS_DIR = REPO_ROOT / "artifacts" / "manga" / "panel_prompts"
PANELS_OUT_DIR = REPO_ROOT / "artifacts" / "manga" / "panels"
BUBBLED_OUT_DIR = REPO_ROOT / "artifacts" / "manga" / "bubbled"
PROGRESS_DIR = REPO_ROOT / "artifacts" / "manga"

QUEUE_RENDER = REPO_ROOT / "scripts" / "manga" / "queue_panel_renders.py"
H1A_WORKFLOW = REPO_ROOT / "scripts" / "image_generation" / "comfyui_workflows" / "flux_txt2img_manga.json"

PHASE1_SERIES = "stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying"


def log(msg: str) -> None:
    print(f"[bulk {time.strftime('%H:%M:%S')}] {msg}", flush=True)


def smoke_gate() -> bool:
    if (SENTINEL_DIR / "SMOKE_FAILED.flag").exists():
        log("BLOCKED: SMOKE_FAILED.flag exists. Resolve Phase 1 first.")
        return False
    if not (SENTINEL_DIR / "SMOKE_OK_ja_jp_stillness.flag").exists():
        log("BLOCKED: SMOKE_OK_ja_jp_stillness.flag missing. Run Phase 1 first.")
        return False
    return True


def discover_series(*, include_phase1: bool, brand: str = "stillness_press") -> list[Path]:
    pattern = f"{brand}__*__en_US__*"
    series = [d for d in sorted(CHAPTER_SCRIPTS_DIR.glob(pattern)) if d.is_dir()]
    if not include_phase1:
        series = [s for s in series if s.name != PHASE1_SERIES]
    return series


def render_chapter(series_id: str, chapter_id: str, *, dry_run: bool, max_retries: int) -> bool:
    panel_prompts = PANEL_PROMPTS_DIR / series_id / f"{chapter_id}.panel_prompts.json"
    if not panel_prompts.exists():
        log(f"  no panel_prompts; skipping {series_id}/{chapter_id}")
        return False
    out_dir = PANELS_OUT_DIR / series_id / chapter_id
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable, str(QUEUE_RENDER),
        "--panel-prompts", str(panel_prompts),
        "--output-dir", str(out_dir),
        "--workflow-path", str(H1A_WORKFLOW),
        "--skip-existing",
    ]
    for attempt in range(max_retries):
        log(f"  render attempt {attempt + 1}/{max_retries}: {chapter_id}")
        if dry_run:
            return True
        rc = subprocess.run(cmd, cwd=REPO_ROOT).returncode
        if rc == 0:
            return True
        log(f"  render rc={rc}; backoff {(2 ** attempt) * 10}s")
        time.sleep((2 ** attempt) * 10)
    return False


def bubble_chapter(series_id: str, chapter_id: str, *, locale: str = "ja_JP") -> bool:
    """Bubble overlay; same import path as Phase 1."""
    try:
        sys.path.insert(0, str(REPO_ROOT))
        from phoenix_v4.manga.chapter import bubble_render  # type: ignore
        from phoenix_v4.manga.chapter import lettering_from_script  # type: ignore
        import yaml  # type: ignore
    except Exception as e:
        log(f"  bubble import failed: {e}")
        return False
    chapter_yaml = CHAPTER_SCRIPTS_DIR / series_id / f"{chapter_id}.yaml"
    if not chapter_yaml.exists():
        return False
    panels_dir = PANELS_OUT_DIR / series_id / chapter_id
    pngs = sorted(panels_dir.glob("*.png"))
    if not pngs:
        return False
    manifest = {"panels": [{"panel_id": p.stem, "path": str(p), "status": "ok"} for p in pngs]}
    try:
        chapter_script = yaml.safe_load(chapter_yaml.read_text())
    except Exception as e:
        log(f"  yaml load failed: {e}")
        return False
    # Build lettering_spec from the chapter_script via canonical builder.
    try:
        lettering_spec = lettering_from_script.build_lettering_spec_from_chapter_script(chapter_script)
    except Exception as e:
        log(f"  lettering_from_script failed: {e}; falling back to empty spec")
        lettering_spec = {"lettering_panels": []}
    bubble_style_config = {"styles": {"round": {}, "spiky": {}, "cloud": {}}}
    out_dir = BUBBLED_OUT_DIR / series_id / chapter_id / locale
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        bubble_render.render_bubbles_on_panels(
            chapter_script=chapter_script,
            lettering_spec=lettering_spec,
            panel_images_manifest=manifest,
            bubble_style_config=bubble_style_config,
            out_dir=out_dir,
            locale=locale,
        )
    except Exception as e:
        log(f"  bubble_render failed: {e}")
        return False
    return True


def r2_upload_chapter(series_id: str, chapter_id: str) -> bool:
    bucket = os.environ.get("R2_BUCKET", "phoenix-omega-artifacts")
    rclone = shutil.which("rclone") or os.path.expanduser("~/.local/bin/rclone")
    if not Path(rclone).exists():
        return False
    src = BUBBLED_OUT_DIR / series_id / chapter_id / "ja_JP"
    if not src.exists():
        return False
    dest = f"r2:{bucket}/manga/ja_jp_bulk/{series_id}/{chapter_id}/"
    rc = subprocess.run([rclone, "copy", str(src), dest], capture_output=True, timeout=1800).returncode
    return rc == 0


def append_progress(progress_path: Path, *, series_id: str, chapter_id: str, status: str, n_panels: int) -> None:
    new = not progress_path.exists()
    with progress_path.open("a") as f:
        if new:
            f.write("ts\tseries_id\tchapter_id\tstatus\tn_panels\n")
        f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\t{series_id}\t{chapter_id}\t{status}\t{n_panels}\n")


def git_commit_progress(progress_path: Path) -> None:
    subprocess.run(["git", "add", str(progress_path)], cwd=REPO_ROOT)
    rc = subprocess.run(
        ["git", "commit", "-m", f"progress(ja_jp_bulk): tsv update {time.strftime('%Y-%m-%d', time.gmtime())}"],
        cwd=REPO_ROOT,
    ).returncode
    if rc == 0:
        subprocess.run(["git", "push", "origin", "HEAD"], cwd=REPO_ROOT)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--include-phase1-series", action="store_true", help="include the_alarm_is_lying (default: skip — Phase 1 already did it)")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--skip-r2", action="store_true")
    p.add_argument("--skip-commit", action="store_true")
    p.add_argument("--max-retries", type=int, default=3)
    args = p.parse_args()

    SENTINEL_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    if not smoke_gate():
        return 1

    series_list = discover_series(include_phase1=args.include_phase1_series)
    log(f"Phase 2 bulk: discovered {len(series_list)} series to render (excluding Phase 1: {not args.include_phase1_series})")
    if not series_list:
        log("Nothing to render. (Expected if only the_alarm_is_lying is authored — Phase 1 already covered it.)")
        log("Phase 2 NO-OP: writing complete-flag.")
        (SENTINEL_DIR / "BULK_COMPLETE_ja_jp_stillness.flag").write_text(
            f"Phase 2 bulk complete (no additional series) @ {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n"
        )
        return 0

    progress_path = PROGRESS_DIR / f"bulk_render_progress_ja_jp_{time.strftime('%Y-%m-%d', time.gmtime())}.tsv"
    last_commit_day = ""

    for series_dir in series_list:
        series_id = series_dir.name
        raw_chapters = sorted(c.stem for c in series_dir.glob("ep_*.yaml"))
        # Skip chapters lacking panel_prompts (Pearl_Writer hasn't authored prompts yet).
        chapters = [c for c in raw_chapters
                    if (PANEL_PROMPTS_DIR / series_id / f"{c}.panel_prompts.json").exists()]
        skipped = [c for c in raw_chapters if c not in chapters]
        log(f"=== series: {series_id} ({len(chapters)} renderable / {len(raw_chapters)} chapter_scripts) ===")
        if skipped:
            log(f"  skipped (no panel_prompts authored): {skipped}")
        for chapter_id in chapters:
            sentinel = SENTINEL_DIR / f"ja_jp_phase2_{series_id}__{chapter_id}.ok"
            if sentinel.exists():
                log(f"  [skip] {chapter_id} (sentinel)")
                continue
            ok = render_chapter(series_id, chapter_id, dry_run=args.dry_run, max_retries=args.max_retries)
            if not ok:
                append_progress(progress_path, series_id=series_id, chapter_id=chapter_id, status="render_failed", n_panels=0)
                log(f"  render FAILED for {chapter_id}; continuing")
                continue
            ok = bubble_chapter(series_id, chapter_id, locale="ja_JP")
            if not ok:
                append_progress(progress_path, series_id=series_id, chapter_id=chapter_id, status="bubble_failed", n_panels=0)
                log(f"  bubble FAILED for {chapter_id}; continuing")
                continue
            n = len(list((PANELS_OUT_DIR / series_id / chapter_id).glob("*.png")))
            if not args.skip_r2:
                r2_upload_chapter(series_id, chapter_id)
            sentinel.write_text(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} panels={n}\n")
            append_progress(progress_path, series_id=series_id, chapter_id=chapter_id, status="ok", n_panels=n)
            log(f"  ✓ {chapter_id} ({n} panels)")

            today = time.strftime("%Y-%m-%d", time.gmtime())
            if not args.skip_commit and today != last_commit_day:
                git_commit_progress(progress_path)
                last_commit_day = today

    (SENTINEL_DIR / "BULK_COMPLETE_ja_jp_stillness.flag").write_text(
        f"Phase 2 bulk done @ {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n"
    )
    if not args.skip_commit:
        git_commit_progress(progress_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
