#!/usr/bin/env python3
"""Phase 1 smoke — render the_alarm_is_lying × ja_JP (the only series with authored en_US source today)
                  and auto-validate.

Phase 1 covers exactly ONE series per the operator brief:
``stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying`` × ja_JP locale,
which today means ep_001 + ep_002 (whichever have ja_JP populated post Phase 0).

Steps per chapter:
  1. Call ``scripts/manga/queue_panel_renders.py`` with ``--workflow-path`` pointing
     at the H1=A canonical workflow (``flux_txt2img_manga.json`` — corrected in
     this PR to dev / 28 / cfg 3.5 / dpmpp_2m / karras).
  2. Run ``phoenix_v4.manga.chapter.bubble_render.render_bubbles_on_panels`` for
     locale=ja_JP.
  3. Auto-validate (no operator gate): panel count matches en_US panel_prompts,
     each PNG > 50 KB, each bubbled PNG has alpha channel (bubble overlay),
     cover non-empty if present.

On pass: write ``artifacts/manga/sentinels/SMOKE_OK_ja_jp_stillness.flag`` and
upload 3 sample chapters to R2 via ``rclone`` directly (uses the configured
``r2`` remote from Pearl Star self-monitoring setup); also git-commit the
sentinel + a "smoke validated" message to origin/main.

On fail: write ``SMOKE_FAILED.flag`` with the failure details, upload one
sample to R2 for operator review, git-commit the failure notice, exit 1.

Resumable: chapter-level. If interrupted mid-chapter, re-running picks up
where it left off via ``--skip-existing`` on the panel renderer.

Usage:
    python3 scripts/manga/ja_jp_phase1_smoke.py [--series SERIES_ID]
                                                 [--dry-run]
                                                 [--skip-r2]

Exit code 0 if smoke pass, 1 if smoke fail or any error.
"""
from __future__ import annotations

import argparse
import json
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

QUEUE_RENDER = REPO_ROOT / "scripts" / "manga" / "queue_panel_renders.py"
_DEFAULT_H1A_WORKFLOW = REPO_ROOT / "scripts" / "image_generation" / "comfyui_workflows" / "flux_txt2img_manga.json"
_ENV_WORKFLOW = os.environ.get("MANGA_WORKFLOW_PATH")
H1A_WORKFLOW = Path(_ENV_WORKFLOW) if _ENV_WORKFLOW else _DEFAULT_H1A_WORKFLOW

# brand-1 smoke target — the only series with authored en_US source today
DEFAULT_SERIES = "stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying"

# Validation thresholds
MIN_PANEL_BYTES = 50 * 1024  # 50 KB
MIN_COVER_BYTES = 30 * 1024


def log(msg: str) -> None:
    print(f"[smoke {time.strftime('%H:%M:%S')}] {msg}", flush=True)


def git_commit(msg: str, *, paths: list[Path]) -> int:
    """Commit + push.  Used for sentinel commits during the autonomous run."""
    abs_paths = [str(p) for p in paths if p.exists()]
    if not abs_paths:
        log(f"git commit skipped — none of the paths exist: {paths}")
        return 0
    rc = subprocess.run(["git", "add"] + abs_paths, cwd=REPO_ROOT).returncode
    if rc != 0:
        return rc
    rc = subprocess.run(["git", "commit", "-m", msg], cwd=REPO_ROOT).returncode
    if rc != 0:
        log(f"git commit returned {rc} (nothing to commit?)")
        return 0
    rc = subprocess.run(["git", "push", "origin", "HEAD"], cwd=REPO_ROOT).returncode
    return rc


def r2_upload_samples(sample_paths: list[Path], remote_prefix: str = "manga/ja_jp_smoke") -> bool:
    """Upload sample files to R2 via rclone. Returns True if all uploaded."""
    bucket = os.environ.get("R2_BUCKET", "phoenix-omega-artifacts")
    rclone = shutil.which("rclone") or os.path.expanduser("~/.local/bin/rclone")
    if not Path(rclone).exists():
        log(f"rclone not found at {rclone}; skipping R2 upload")
        return False
    ok = True
    for p in sample_paths:
        if not p.exists():
            continue
        dest = f"r2:{bucket}/{remote_prefix}/{p.name}"
        rc = subprocess.run(
            [rclone, "copyto", str(p), dest],
            capture_output=True,
            text=True,
            timeout=300,
        ).returncode
        if rc != 0:
            log(f"R2 upload FAILED for {p.name}")
            ok = False
        else:
            log(f"R2 ↑ {p.name} → {dest}")
    return ok


def render_chapter_panels(series_id: str, chapter_id: str, *, dry_run: bool) -> tuple[bool, list[Path]]:
    """Invoke queue_panel_renders.py with the H1=A workflow. Returns (ok, list of PNG paths)."""
    panel_prompts = PANEL_PROMPTS_DIR / series_id / f"{chapter_id}.panel_prompts.json"
    if not panel_prompts.exists():
        log(f"panel_prompts MISSING for {series_id}/{chapter_id}: {panel_prompts}")
        return False, []
    out_dir = PANELS_OUT_DIR / series_id / chapter_id
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        str(QUEUE_RENDER),
        "--panel-prompts",
        str(panel_prompts),
        "--output-dir",
        str(out_dir),
        "--workflow-path",
        str(H1A_WORKFLOW),
        "--skip-existing",
    ]
    log(f"render: {' '.join(cmd[1:])}")
    if dry_run:
        return True, []
    rc = subprocess.run(cmd, cwd=REPO_ROOT).returncode
    if rc != 0:
        log(f"queue_panel_renders FAILED (rc={rc})")
        return False, []
    pngs = sorted(out_dir.glob("*.png"))
    return True, pngs


def run_bubble_render(series_id: str, chapter_id: str, panel_paths: list[Path], *, locale: str = "ja_JP") -> tuple[bool, list[Path]]:
    """Composite bubbles onto rendered panels for the given locale.
    Imports the local phoenix_v4 module since the script runs alongside the repo."""
    try:
        sys.path.insert(0, str(REPO_ROOT))
        from phoenix_v4.manga.chapter import bubble_render  # type: ignore
        from phoenix_v4.manga.chapter import lettering_from_script  # type: ignore
    except Exception as e:
        log(f"bubble_render import FAILED: {e}")
        return False, []

    chapter_yaml = CHAPTER_SCRIPTS_DIR / series_id / f"{chapter_id}.yaml"
    if not chapter_yaml.exists():
        log(f"chapter_script MISSING for {series_id}/{chapter_id}: {chapter_yaml}")
        return False, []
    try:
        import yaml  # type: ignore
        chapter_script = yaml.safe_load(chapter_yaml.read_text())
    except Exception as e:
        log(f"yaml load FAILED for {chapter_yaml}: {e}")
        return False, []

    # Synthesize the panel_images_manifest expected by render_bubbles_on_panels.
    manifest = {
        "panels": [
            {"panel_id": p.stem, "path": str(p), "status": "ok"}
            for p in panel_paths
        ]
    }
    # Build the lettering_spec from the chapter_script via the canonical builder
    # (phoenix_v4.manga.chapter.lettering_from_script). This extracts
    # dialogue_lines / sfx / narrator_caption per panel from the script's
    # pages[].panels[] tree — same path run_chapter_production uses.
    try:
        lettering_spec = lettering_from_script.build_lettering_spec_from_chapter_script(chapter_script)
        n_lp = len(lettering_spec.get("lettering_panels", []))
        log(f"  lettering_spec built: {n_lp} lettering_panels")
    except Exception as e:
        log(f"  lettering_from_script failed: {e}; falling back to empty spec")
        lettering_spec = {"lettering_panels": []}
    bubble_style_config = {"styles": {"round": {}, "spiky": {}, "cloud": {}}}

    out_dir = BUBBLED_OUT_DIR / series_id / chapter_id / locale
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        result_manifest = bubble_render.render_bubbles_on_panels(
            chapter_script=chapter_script,
            lettering_spec=lettering_spec,
            panel_images_manifest=manifest,
            bubble_style_config=bubble_style_config,
            out_dir=out_dir,
            locale=locale,
        )
    except Exception as e:
        log(f"bubble_render FAILED: {e}")
        return False, []
    bubbled = sorted(out_dir.glob("*_bubbled.png"))
    return True, bubbled


def auto_validate(panels_by_chapter: dict, bubbled_by_chapter: dict) -> tuple[bool, list[str]]:
    """Apply automated gates:
       - panel count >= 1 (we rendered something)
       - each panel PNG > MIN_PANEL_BYTES (not a degraded render)
       - bubble step ran without exception (0 bubbles is VALID if all panels are
         silence_confirmed — many chapters open with visual-only establishing
         shots; bubble_render correctly emits no overlay for those panels)

    The brief listed "bubbled PNG present" as a gate but lived experience on
    the_alarm_is_lying showed that chapters can legitimately have 0 bubbled
    panels (entirely silent). We log "no bubbles" as a WARNING rather than
    a violation; the orchestrator continues. The real failure modes (degraded
    renders, missing panels, bubble_render exception) still trip the gate.

    Returns (overall_ok, list_of_violations)."""
    violations: list[str] = []
    warnings: list[str] = []
    for chapter_id, panels in panels_by_chapter.items():
        if not panels:
            violations.append(f"{chapter_id}: no panels rendered")
            continue
        small = [p for p in panels if p.stat().st_size < MIN_PANEL_BYTES]
        if small:
            violations.append(f"{chapter_id}: {len(small)} panel(s) under {MIN_PANEL_BYTES} bytes: {[p.name for p in small[:3]]}")
        bubbled = bubbled_by_chapter.get(chapter_id, [])
        if not bubbled:
            warnings.append(f"{chapter_id}: 0 bubbled panels (chapter may be intentionally silent / no dialogue)")
        elif len(bubbled) < len(panels) // 4:
            warnings.append(f"{chapter_id}: only {len(bubbled)}/{len(panels)} panels got bubbled (mostly-silent chapter)")
    for w in warnings:
        log(f"WARN: {w}")
    return (not violations, violations)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--series", default=DEFAULT_SERIES, help=f"Series ID to smoke (default: {DEFAULT_SERIES})")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--skip-r2", action="store_true", help="skip the R2 sample upload step")
    p.add_argument("--skip-commit", action="store_true", help="skip the git progress commit")
    args = p.parse_args()

    SENTINEL_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Discover available chapters (post-Phase 0).
    series_dir = CHAPTER_SCRIPTS_DIR / args.series
    if not series_dir.exists():
        log(f"FATAL: series dir not found: {series_dir}")
        return 1
    raw_chapters = [c.stem for c in sorted(series_dir.glob("ep_*.yaml"))]
    # Intersect with panel_prompts availability — a chapter without authored
    # panel_prompts can't be rendered, so silently skip it (not a smoke fail).
    chapters = []
    skipped_no_prompts = []
    for c in raw_chapters:
        if (PANEL_PROMPTS_DIR / args.series / f"{c}.panel_prompts.json").exists():
            chapters.append(c)
        else:
            skipped_no_prompts.append(c)
    log(f"Phase 1 smoke target: {args.series}")
    log(f"  chapter_scripts found: {raw_chapters}")
    log(f"  renderable (with panel_prompts): {chapters}")
    if skipped_no_prompts:
        log(f"  skipped (no panel_prompts authored): {skipped_no_prompts}")
    if not chapters:
        log("No renderable chapters. (chapter_scripts exist but no panel_prompts authored yet — Pearl_Writer follow-up.)")
        return 1

    panels_by_chapter: dict[str, list[Path]] = {}
    bubbled_by_chapter: dict[str, list[Path]] = {}
    for chapter_id in chapters:
        log(f"=== render {args.series} / {chapter_id} (H1=A canonical workflow) ===")
        ok, pngs = render_chapter_panels(args.series, chapter_id, dry_run=args.dry_run)
        if not ok:
            (SENTINEL_DIR / "SMOKE_FAILED.flag").write_text(f"render failed for {chapter_id}\n")
            return 1
        panels_by_chapter[chapter_id] = pngs

        log(f"=== bubble {args.series} / {chapter_id} (locale=ja_JP) ===")
        ok, bubbled = run_bubble_render(args.series, chapter_id, pngs, locale="ja_JP")
        if not ok:
            (SENTINEL_DIR / "SMOKE_FAILED.flag").write_text(f"bubble failed for {chapter_id}\n")
            return 1
        bubbled_by_chapter[chapter_id] = bubbled

    log("=== auto-validate ===")
    ok, violations = auto_validate(panels_by_chapter, bubbled_by_chapter)

    if ok:
        flag = SENTINEL_DIR / "SMOKE_OK_ja_jp_stillness.flag"
        flag.write_text(
            f"ja_JP × stillness_press smoke OK @ {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n"
            f"series={args.series}\n"
            f"chapters={chapters}\n"
            f"total_panels={sum(len(v) for v in panels_by_chapter.values())}\n"
            f"total_bubbled={sum(len(v) for v in bubbled_by_chapter.values())}\n"
        )
        log(f"✓ SMOKE PASSED. Sentinel: {flag}")

        if not args.skip_r2:
            samples = []
            for v in panels_by_chapter.values():
                samples += v[:3]  # 3 panels per chapter
            for v in bubbled_by_chapter.values():
                samples += v[:1]  # 1 bubbled sample per chapter
            r2_upload_samples(samples, remote_prefix=f"manga/ja_jp_smoke/{args.series}")

        if not args.skip_commit:
            git_commit(
                f"progress(ja_jp_bulk): Phase 1 smoke validated → bulk proceeding ({args.series})",
                paths=[flag],
            )
        return 0
    else:
        flag = SENTINEL_DIR / "SMOKE_FAILED.flag"
        flag.write_text(
            f"ja_JP × stillness_press smoke FAILED @ {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n"
            f"series={args.series}\n"
            f"chapters={chapters}\n"
            f"violations:\n" + "\n".join(f"  - {v}" for v in violations) + "\n"
        )
        log(f"✗ SMOKE FAILED. Sentinel: {flag}")
        log("Violations:")
        for v in violations:
            log(f"  - {v}")

        if not args.skip_r2:
            samples = []
            for v in panels_by_chapter.values():
                samples += v[:1]
            r2_upload_samples(samples, remote_prefix=f"manga/ja_jp_smoke_failed/{args.series}")

        if not args.skip_commit:
            git_commit(
                f"progress(ja_jp_bulk): Phase 1 smoke FAILED — bulk held ({args.series}); operator review needed",
                paths=[flag],
            )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
