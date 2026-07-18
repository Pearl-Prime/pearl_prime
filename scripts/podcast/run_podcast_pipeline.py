#!/usr/bin/env python3
"""Orchestrator: assemble → render → feed → optional R2 upload."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.podcast._lib import load_yaml  # noqa: E402
from scripts.podcast.render_podcast_audio import probe_duration  # noqa: E402


def run_cmd(cmd: list[str]) -> bool:
    r = subprocess.run(cmd, cwd=str(REPO_ROOT))
    return r.returncode == 0


def make_artwork(primary_hex: str, out_jpg: Path, dry_run: bool) -> None:
    """Minimal 3000×3000 JPEG placeholder from brand primary color."""
    if dry_run:
        print(f"artwork → {out_jpg}")
        return
    out_jpg.parent.mkdir(parents=True, exist_ok=True)
    color = primary_hex.lstrip("#")
    if len(color) != 6:
        color = "4A5568"
    subprocess.run(
        [
            os.environ.get("FFMPEG_BIN", "ffmpeg"),
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"color=c=0x{color}:s=3000x3000",
            "-frames:v",
            "1",
            "-q:v",
            "2",
            str(out_jpg),
        ],
        capture_output=True,
        check=False,
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Run full podcast pipeline")
    ap.add_argument("--brand-id", required=True)
    ap.add_argument("--locale", required=True)
    ap.add_argument("--week", required=True)
    ap.add_argument("--book-dir", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--formats", default="podcast_episode,podcast_short")
    ap.add_argument("--series-title", default="The Room Full of People")
    ap.add_argument("--series-slug", default="social_anxiety_arc")
    ap.add_argument("--base-url", default=os.environ.get("PODCAST_PUBLIC_BASE_URL", "https://cdn.example.com/podcast"))
    ap.add_argument("--skip-upload", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument(
        "--workspace",
        type=Path,
        default=None,
        help="Directory containing job.json (default: --output-dir)",
    )
    ap.add_argument(
        "--no-job-check",
        dest="no_job_check",
        action="store_true",
        help="Skip job.json enforcement for spawned stage scripts (CI only)",
    )
    args = ap.parse_args()

    book_dir = args.book_dir.resolve()
    out_root = args.output_dir.resolve()
    job_ws = str((args.workspace or out_root).resolve())
    podcast_dir = out_root / "podcast"
    podcast_dir.mkdir(parents=True, exist_ok=True)
    work = podcast_dir / "_work"
    work.mkdir(parents=True, exist_ok=True)

    wq = load_yaml(REPO_ROOT / "config" / "catalog" / "weekly_queue_config.yaml")
    _ = wq.get("podcast_weekly") or {}

    brand_colors = load_yaml(REPO_ROOT / "config" / "catalog_planning" / "brand_identity_system.yaml")
    tb = (brand_colors.get("teacher_brands") or {}).get(args.brand_id) or {}
    sid = (tb.get("brand_identity") or {}).get("primary_colors") or ["#4A5568"]
    primary = sid[0] if sid else "#4A5568"
    artwork_path = podcast_dir / "artwork.jpg"
    make_artwork(primary, artwork_path, args.dry_run)

    formats = [f.strip() for f in args.formats.split(",") if f.strip()]
    exe = sys.executable
    assemblies: list[Path] = []
    episode_metas: list[dict[str, Any]] = []

    for fmt in formats:
        asm_dir = work / fmt
        asm_dir.mkdir(parents=True, exist_ok=True)
        cmd_ass = [
            exe,
            str(REPO_ROOT / "scripts/podcast/assemble_podcast_episode.py"),
            "--book-dir",
            str(book_dir),
            "--brand-id",
            args.brand_id,
            "--locale",
            args.locale,
            "--format",
            fmt,
            "--week",
            args.week,
            "--series-title",
            args.series_title,
            "--series-slug",
            args.series_slug,
            "--output-dir",
            str(asm_dir),
            "--workspace",
            job_ws,
        ]
        if args.no_job_check:
            cmd_ass.append("--no-job-check")
        if args.dry_run:
            print(" ".join(cmd_ass))
            print("(render would run after assemble for %s)" % fmt)
            continue
        if not run_cmd(cmd_ass):
            return 1
        globs = list(asm_dir.glob("assembly_*.json"))
        if not globs:
            print("No assembly written", file=sys.stderr)
            return 1
        asm_path = globs[0]
        assemblies.append(asm_path)
        ad = json.loads(asm_path.read_text(encoding="utf-8"))
        ep_id = ad.get("episode_id") or fmt
        mp3_path = podcast_dir / f"{ep_id}.mp3"
        cmd_render = [
            exe,
            str(REPO_ROOT / "scripts/podcast/render_podcast_audio.py"),
            "--assembly",
            str(asm_path),
            "--output",
            str(mp3_path),
            "--voice-provider",
            "auto",
            "--workspace",
            job_ws,
        ]
        if args.no_job_check:
            cmd_render.append("--no-job-check")
        if not run_cmd(cmd_render):
            return 1

        if mp3_path.exists():
            ln = json.loads(
                (mp3_path.with_suffix(".render_report.json")).read_text(encoding="utf-8")
            ) if (mp3_path.with_suffix(".render_report.json")).exists() else {}
            pub = format_datetime(datetime.now(timezone.utc), usegmt=True)
            meta = {
                "episode_id": ep_id,
                "guid": ad.get("guid"),
                "locale": args.locale,
                "title": (ad.get("metadata") or {}).get("title") or ep_id,
                "description": (ad.get("metadata") or {}).get("description") or "",
                "pub_date_rfc2822": pub,
                "enclosure_url": f"{args.base_url.rstrip('/')}/{args.brand_id}/{args.series_slug}/{mp3_path.name}",
                "enclosure_length_bytes": mp3_path.stat().st_size,
                "duration_s": probe_duration(mp3_path) or ln.get("duration_s"),
                "episode_number": ad.get("episode_number") or 1,
                "season_number": ad.get("season_number") or 1,
                "explicit": (ad.get("metadata") or {}).get("explicit") or "no",
                "format": fmt,
            }
            meta_path = podcast_dir / f"{ep_id}.meta.json"
            meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            episode_metas.append(meta)

    ch_path = podcast_dir / "channel_assembly.json"
    ch = {
        "channel": {
            "title": args.series_title,
            "description": f"{args.series_title} — {args.brand_id}",
            "language": args.locale,
            "author": args.brand_id,
            "explicit": "no",
        }
    }
    if not args.dry_run:
        ch_path.write_text(json.dumps(ch, indent=2) + "\n", encoding="utf-8")

    cmd_feed = [
        exe,
        str(REPO_ROOT / "scripts/podcast/generate_podcast_feed.py"),
        "--episodes-dir",
        str(podcast_dir),
        "--brand-id",
        args.brand_id,
        "--series-id",
        args.series_slug,
        "--base-url",
        args.base_url,
        "--output",
        str(podcast_dir / "feed.xml"),
        "--workspace",
        job_ws,
    ]
    if args.no_job_check:
        cmd_feed.append("--no-job-check")
    if args.dry_run:
        print(" ".join(cmd_feed))
    elif not run_cmd(cmd_feed):
        return 1

    upload_status = "skipped"
    if not args.skip_upload and not args.dry_run:
        cmd_up = [
            exe,
            str(REPO_ROOT / "scripts/podcast/upload_podcast_to_r2.py"),
            "--source-dir",
            str(podcast_dir),
            "--brand-id",
            args.brand_id,
            "--series-id",
            args.series_slug,
            "--week",
            args.week,
            "--workspace",
            job_ws,
        ]
        if args.no_job_check:
            cmd_up.append("--no-job-check")
        upload_status = "ok" if run_cmd(cmd_up) else "failed"

    report = {
        "brand_id": args.brand_id,
        "locale": args.locale,
        "week": args.week,
        "formats": formats,
        "assemblies": [str(p) for p in assemblies],
        "episodes": episode_metas,
        "podcast_dir": str(podcast_dir),
        "upload": upload_status,
    }
    rep_file = podcast_dir / "pipeline_report.json"
    if not args.dry_run:
        rep_file.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
