#!/usr/bin/env python3
"""
Generate FLUX stills for every example_registry row using onboarding_proof_media_prompts.json,
then assemble silent MP4s via the Pearl Prime video stack (scripts/video/run_render.py + ffmpeg).

Credentials: Cloudflare Workers AI per docs/INTEGRATION_CREDENTIALS_REGISTRY.md § Cloudflare.
Check: python3 scripts/ci/check_integration_env.py

Outputs (default):
  artifacts/onboarding_proof_media/images/{id}.png
  artifacts/onboarding_proof_media/videos/{id}/{id}.mp4

Usage:
  python3 scripts/onboarding/run_onboarding_proof_flux_and_video.py --dry-run
  python3 scripts/onboarding/run_onboarding_proof_flux_and_video.py --limit 2
  python3 scripts/onboarding/run_onboarding_proof_flux_and_video.py --images-only
  python3 scripts/onboarding/run_onboarding_proof_flux_and_video.py --video-only
  python3 scripts/onboarding/run_onboarding_proof_flux_and_video.py --ids cmp_bp_founder_v1,gal_tool_breath_01
  python3 scripts/onboarding/run_onboarding_proof_flux_and_video.py --placeholder-images   # no Cloudflare; ffmpeg solid-color PNGs
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.video.flux_client import call_flux, load_credentials  # noqa: E402
from scripts.video._config import get_ffmpeg_bin  # noqa: E402

PROMPTS_PATH = REPO_ROOT / "config" / "onboarding" / "onboarding_proof_media_prompts.json"
DEFAULT_OUT = REPO_ROOT / "artifacts" / "onboarding_proof_media"


def _seed_for_id(registry_id: str) -> int:
    h = hashlib.sha256(registry_id.encode()).hexdigest()
    return int(h[:8], 16) % (2**31)


def _flux_wh(aspect: str) -> tuple[int, int]:
    a = (aspect or "9:16").strip()
    if a == "16:9":
        return 1024, 576
    return 576, 1024


def _timeline_resolution(aspect: str) -> tuple[int, int, str]:
    a = (aspect or "9:16").strip()
    if a == "16:9":
        return 1920, 1080, "16:9"
    return 1080, 1920, "9:16"


def _compose_positive(t2i: dict) -> str:
    return (
        f"{t2i['foreground'].strip()}\n\n{t2i['background'].strip()}\n\n{t2i['lighting'].strip()}"
    )


def _resolve_negative(doc: dict, key: str) -> str:
    shared = doc.get("shared_negatives") or {}
    neg = shared.get(key) if isinstance(shared.get(key), str) else ""
    if not neg.strip():
        neg = str(shared.get("book_cover_default", ""))
    return neg.strip()


def _write_shot_plan(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "shots": [
                    {
                        "shot_id": "shot-1",
                        "prompt_bundle": {"motion": "ken_burns"},
                    }
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def _write_placeholder_png(ffmpeg_exe: str, registry_id: str, aspect: str, out_path: Path) -> None:
    """Deterministic solid-color PNG via lavfi (no FLUX)."""
    w, h = _flux_wh(aspect)
    hsh = hashlib.sha256(registry_id.encode()).hexdigest()
    color = f"0x{hsh[:6]}"
    cmd = [
        ffmpeg_exe,
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"color=c={color}:s={w}x{h}:d=1",
        "-frames:v",
        "1",
        str(out_path),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise RuntimeError(r.stderr or "ffmpeg placeholder failed")


def _write_timeline(path: Path, registry_id: str, duration_s: float, aspect: str) -> None:
    w, h, ar = _timeline_resolution(aspect)
    doc = {
        "plan_id": registry_id,
        "fps": 24,
        "resolution": {"width": w, "height": h},
        "aspect_ratio": ar,
        "duration_s": float(duration_s),
        "thumbnail_frame_ref": {"shot_id": "shot-1", "frame_offset": 0},
        "audio_tracks": [],
        "clips": [
            {
                "shot_id": "shot-1",
                "asset_id": registry_id,
                "start_time_s": 0.0,
                "end_time_s": float(duration_s),
                "caption_ref": "",
            }
        ],
    }
    path.write_text(json.dumps(doc, indent=2), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="FLUX images + Pearl Prime ffmpeg render for onboarding proof rows",
    )
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Base output directory")
    ap.add_argument("--dry-run", action="store_true", help="Print plan only")
    ap.add_argument("--limit", type=int, default=None, help="Max rows to process")
    ap.add_argument("--ids", type=str, default=None, help="Comma-separated registry ids")
    ap.add_argument("--force-images", action="store_true", help="Overwrite existing PNGs")
    ap.add_argument("--images-only", action="store_true", help="Skip video assembly")
    ap.add_argument("--video-only", action="store_true", help="Skip FLUX; need existing PNGs")
    ap.add_argument(
        "--placeholder-images",
        action="store_true",
        help="Skip FLUX API; write deterministic solid-color PNGs via ffmpeg (for CI or no credentials)",
    )
    ap.add_argument(
        "--max-render-seconds",
        type=float,
        default=None,
        help="Cap clip duration for faster local runs (default: use prompts' duration_s)",
    )
    ap.add_argument("--quality", default="draft", choices=("draft", "standard", "high"))
    args = ap.parse_args()

    if not PROMPTS_PATH.is_file():
        print(f"Missing {PROMPTS_PATH}", file=sys.stderr)
        return 1

    doc = json.loads(PROMPTS_PATH.read_text(encoding="utf-8"))
    by_id = doc.get("by_id")
    if not isinstance(by_id, dict):
        print("onboarding_proof_media_prompts.json: invalid by_id", file=sys.stderr)
        return 1

    id_filter = None
    if args.ids:
        id_filter = {x.strip() for x in args.ids.split(",") if x.strip()}

    rows = sorted(by_id.keys())
    if id_filter is not None:
        rows = [r for r in rows if r in id_filter]
        missing = id_filter - set(rows)
        if missing:
            print(f"Unknown ids (no prompts): {sorted(missing)}", file=sys.stderr)
            return 1
    if args.limit:
        rows = rows[: args.limit]

    out_base = Path(args.out)
    img_dir = out_base / "images"
    vid_root = out_base / "videos"
    img_dir.mkdir(parents=True, exist_ok=True)
    vid_root.mkdir(parents=True, exist_ok=True)

    account_id, api_token = load_credentials()
    need_flux = not args.dry_run and not args.video_only and not args.placeholder_images
    if need_flux and (not account_id or not api_token):
        print(
            "Missing Cloudflare credentials. Set CLOUDFLARE_ACCOUNT_ID and "
            "CLOUDFLARE_API_TOKEN (see docs/INTEGRATION_CREDENTIALS_REGISTRY.md). "
            "Or use --placeholder-images, or --video-only if PNGs already exist.",
            file=sys.stderr,
        )
        return 1

    # Placeholder PNGs and/or ffmpeg render both need ffmpeg.
    need_ffmpeg = not args.dry_run and (args.placeholder_images or not args.images_only)
    ffmpeg_bin = get_ffmpeg_bin() if need_ffmpeg else ""
    if need_ffmpeg:
        try:
            r = subprocess.run([ffmpeg_bin, "-version"], capture_output=True, text=True, timeout=5)
            if r.returncode != 0:
                raise RuntimeError(r.stderr or "ffmpeg failed")
        except (OSError, subprocess.TimeoutExpired) as e:
            print(f"ffmpeg not usable ({ffmpeg_bin}): {e}", file=sys.stderr)
            return 1

    manifest: dict = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "image_source": "placeholder_ffmpeg" if args.placeholder_images else "cloudflare_flux",
        "rows": {},
    }

    if args.dry_run:
        print(f"Would process {len(rows)} rows → {out_base}")
        for rid in rows:
            entry = by_id[rid]
            vid = entry.get("video") or {}
            print(f"  {rid}  aspect={vid.get('aspect')}  duration_s={vid.get('duration_s')}")
        return 0

    py = sys.executable
    render_py = REPO_ROOT / "scripts" / "video" / "run_render.py"

    for rid in rows:
        entry = by_id[rid]
        t2i = entry.get("t2i")
        vid = entry.get("video") or {}
        if not isinstance(t2i, dict):
            print(f"Skip {rid}: bad t2i", file=sys.stderr)
            continue
        aspect = str(vid.get("aspect") or "9:16")
        duration_s = float(vid.get("duration_s") or 8)
        duration_s = max(1.0, min(duration_s, 120.0))
        if args.max_render_seconds is not None:
            duration_s = min(duration_s, max(0.5, float(args.max_render_seconds)))

        png_path = img_dir / f"{rid}.png"
        row_manifest: dict = {"image": str(png_path.relative_to(REPO_ROOT))}

        if not args.video_only:
            if png_path.exists() and not args.force_images:
                print(f"Skip image (exists): {png_path.name}")
            elif args.placeholder_images:
                print(f"Placeholder PNG {rid} ...")
                try:
                    _write_placeholder_png(ffmpeg_bin, rid, aspect, png_path)
                    row_manifest["image_source"] = "placeholder_ffmpeg"
                except Exception as e:
                    print(f"  placeholder failed {rid}: {e}", file=sys.stderr)
                    row_manifest["image_error"] = str(e)
                    manifest["rows"][rid] = row_manifest
                    continue
            else:
                pos = _compose_positive(t2i)
                neg_key = str(t2i.get("negative_key") or "book_cover_default")
                neg = _resolve_negative(doc, neg_key)
                fw, fh = _flux_wh(aspect)
                seed = _seed_for_id(rid)
                print(f"FLUX {rid} ({fw}x{fh}) seed={seed} ...")
                try:
                    blob = call_flux(
                        account_id=account_id,
                        api_token=api_token,
                        prompt=pos,
                        negative_prompt=neg,
                        width=fw,
                        height=fh,
                        seed=seed,
                    )
                    png_path.write_bytes(blob)
                    row_manifest["image_source"] = "cloudflare_flux"
                except Exception as e:
                    print(f"  FLUX failed {rid}: {e}", file=sys.stderr)
                    row_manifest["flux_error"] = str(e)
                    manifest["rows"][rid] = row_manifest
                    continue

        if args.images_only:
            manifest["rows"][rid] = row_manifest
            continue

        if not png_path.is_file():
            print(f"Skip video (no image): {rid}", file=sys.stderr)
            row_manifest["video_error"] = "missing_png"
            manifest["rows"][rid] = row_manifest
            continue

        vdir = vid_root / rid
        vdir.mkdir(parents=True, exist_ok=True)
        tl_path = vdir / "timeline.json"
        sp_path = vdir / "shot_plan.json"
        _write_timeline(tl_path, rid, duration_s, aspect)
        _write_shot_plan(sp_path)

        print(f"Render {rid} ({duration_s}s) ...")
        try:
            subprocess.run(
                [
                    py,
                    str(render_py),
                    str(tl_path),
                    "-o",
                    str(vdir),
                    "--assets-dir",
                    str(img_dir),
                    "--shot-plan",
                    str(sp_path),
                    "--video-id",
                    rid,
                    "--quality",
                    args.quality,
                ],
                cwd=REPO_ROOT,
                check=True,
            )
            mp4 = vdir / f"{rid}.mp4"
            row_manifest["video"] = str(mp4.relative_to(REPO_ROOT)) if mp4.is_file() else None
        except subprocess.CalledProcessError as e:
            print(f"  render failed {rid}: {e}", file=sys.stderr)
            row_manifest["video_error"] = str(e)

        manifest["rows"][rid] = row_manifest

    man_path = out_base / "manifest.json"
    man_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote {man_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
