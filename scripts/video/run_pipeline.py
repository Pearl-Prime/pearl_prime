#!/usr/bin/env python3
"""
Run the full video pipeline for a plan: preparer → shot → assets → timeline → caption →
VCE stages 12–14 → QC → optional render → platform adapter → multilang → provenance → metadata → analytics.
Uses fixtures or artifacts; writes to artifacts/video/ by default.
Usage:
  python scripts/video/run_pipeline.py --plan-id plan-therapeutic-001 [--format short] [--platforms youtube,tiktok] [--languages en,zh-CN]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
from scripts.video._config import load_yaml as _load_video_yaml  # noqa: E402


def run(cmd: list[str], cwd: Path) -> bool:
    r = subprocess.run(cmd, cwd=cwd)
    return r.returncode == 0


def _format_to_aspect(format_key: str) -> str:
    data = _load_video_yaml("config/video/format_specs.yaml")
    fmt = (data.get("formats") or {}).get(format_key, {})
    return str(fmt.get("aspect", "16:9"))


def main() -> int:
    ap = argparse.ArgumentParser(description="Run full video pipeline for a plan (VCE extended)")
    ap.add_argument("--plan-id", default="plan-therapeutic-001", help="Plan ID (used for naming)")
    ap.add_argument("--fixtures-dir", default=None, help="Dir with render_manifest.json")
    ap.add_argument("--render-manifest", default=None, help="Direct path to render_manifest.json or .html file")
    ap.add_argument("--out-dir", default=None, help="Output dir (default: artifacts/video/<plan_id>)")
    ap.add_argument("--video-id", default=None, help="Video ID (default: video-<plan_id>)")
    ap.add_argument("--force", action="store_true", help="Overwrite existing artifacts at every stage")
    ap.add_argument("--assets-dir", default=None, help="Assets directory for render")
    ap.add_argument("--skip-render", action="store_true", default=False, help="Skip the FFmpeg render stage (default: render runs)")
    ap.add_argument("--no-skip-render", action="store_true", help="Deprecated no-op: render now runs by default; kept for backward compat")
    ap.add_argument("--format", default="short", help="VCE format: short|mid|long|motion_comic|lofi|exercise")
    ap.add_argument("--platforms", default="youtube,tiktok", help="Comma-separated targets for platform adapter")
    ap.add_argument("--languages", default="en", help="Comma-separated locales for multilang stage")
    ap.add_argument("--quality", default="standard", choices=("draft", "standard", "high"), help="FFmpeg CRF/preset when rendering")
    ap.add_argument("--channel-id", default="ch_001", help="Channel for soundtrack / QC stub")
    ap.add_argument("--title", default="When anxiety shows up", help="Stub/final title for distribution")
    ap.add_argument("--description", default="A short on noticing anxiety without fighting it.", help="Description")
    ap.add_argument("--tags", default="anxiety,mindfulness,therapeutic", help="Comma-separated tags")
    ap.add_argument("--voice", action="store_true", help="Generate voice narration via free/local TTS (CosyVoice2 CJK / Edge-TTS EN; never ElevenLabs)")
    ap.add_argument("--music", action="store_true", help="Also run voice synthesis (music bed itself comes from --music-bank, the free bank)")
    ap.add_argument("--music-bank", action="store_true", help="Select music from free music bank (recommended)")
    ap.add_argument("--auto-generate", action="store_true", help="Auto-generate missing image assets via RunComfy")
    ap.add_argument("--upload", action="store_true", help="Run Stage 18 Upload/Publish after pipeline (dry-run by default)")
    ap.add_argument("--upload-live", action="store_true", help="Upload for real (requires --upload)")
    ap.add_argument(
        "--no-job-check",
        dest="no_job_check",
        action="store_true",
        help="Skip job.json enforcement on stage scripts (CI/testing only)",
    )
    args = ap.parse_args()

    skip_render = args.skip_render and not args.no_skip_render
    if args.no_job_check:
        print(
            "WARNING: --no-job-check: pipeline job enforcement disabled (CI/testing only).",
            file=sys.stderr,
        )

    fixtures = Path(args.fixtures_dir or str(REPO_ROOT / "fixtures" / "video_pipeline"))
    out_root = Path(args.out_dir or str(REPO_ROOT / "artifacts" / "video" / args.plan_id))
    video_id = args.video_id or f"video-{args.plan_id}"
    out_root.mkdir(parents=True, exist_ok=True)

    if args.render_manifest:
        manifest_path = Path(args.render_manifest)
    else:
        manifest_alt = fixtures / f"render_manifest_{args.plan_id}.json"
        if manifest_alt.exists():
            manifest_path = manifest_alt
        else:
            manifest_path = fixtures / "render_manifest.json"
    if not manifest_path.exists():
        print(f"Error: render manifest not found: {manifest_path}", file=sys.stderr)
        return 1

    scripts = REPO_ROOT / "scripts" / "video"
    py = sys.executable
    force_flag = ["--force"] if args.force else []
    job_flag = ["--no-job-check"] if args.no_job_check else []

    aspect = _format_to_aspect(args.format)
    if aspect == "9:16":
        aspect_arg = "9:16"
    elif aspect == "16:9":
        aspect_arg = "16:9"
    else:
        aspect_arg = "16:9"

    steps = [
        ([py, str(scripts / "prepare_script_segments.py"), str(manifest_path), "-o", str(out_root / "script_segments.json")] + force_flag, "Script Preparer"),
        ([py, str(scripts / "run_shot_planner.py"), str(out_root / "script_segments.json"), "-o", str(out_root / "shot_plan.json")] + force_flag, "Shot Planner"),
        ([py, str(scripts / "run_asset_resolver.py"), str(out_root / "shot_plan.json"), "-o", str(out_root / "resolved_assets.json")]
         + (["--auto-generate", "--auto-generate-dir", str(out_root / "generated_assets")] if args.auto_generate else [])
         + force_flag, "Asset Resolver"),
        ([py, str(scripts / "run_timeline_builder.py"), str(out_root / "shot_plan.json"), str(out_root / "resolved_assets.json"),
          "-o", str(out_root / "timeline.json"), "--aspect", aspect_arg] + force_flag, "Timeline Builder"),
        ([py, str(scripts / "run_caption_adapter.py"), str(out_root / "timeline.json"), str(out_root / "script_segments.json"),
          "-o", str(out_root / "captions.json")] + force_flag, "Caption Adapter"),
        ([py, str(scripts / "run_layer_compositor.py"), str(out_root / "resolved_assets.json"), str(out_root / "shot_plan.json"),
          "-o", str(out_root / "composited_layers.json"), "--format", args.format] + force_flag, "Layer Compositor"),
        ([py, str(scripts / "run_animation_engine.py"), str(out_root / "composited_layers.json"), str(out_root / "shot_plan.json"),
          str(out_root / "timeline.json"), "-o", str(out_root / "animation_plan.json"), "--format", args.format] + force_flag, "Animation Engine"),
        ([py, str(scripts / "run_soundtrack_engine.py"), str(out_root / "timeline.json"), str(out_root / "shot_plan.json"),
          str(out_root / "script_segments.json"), "-o", str(out_root / "soundtrack_plan.json"), "--channel-id", args.channel_id] + force_flag, "Soundtrack Engine"),
    ]
    for cmd, name in steps:
        if not run(cmd + job_flag, REPO_ROOT):
            print(f"Failed: {name}", file=sys.stderr)
            return 1
        print(f"OK: {name}")

    # ── Music bank selection — free, no API cost ──
    soundtrack_audio_path = out_root / "soundtrack_plan.json"  # default (no audio)
    if args.music_bank:
        try:
            from scripts.music.select_and_edit import select_track, anti_spam_edit
            soundtrack = json.loads((out_root / "soundtrack_plan.json").read_text(encoding="utf-8"))
            duration = float(soundtrack.get("duration_s", 60))
            track = select_track(topic="anxiety", mood="calm")
            if track:
                music_out = out_root / "audio" / "music_bank_track.mp3"
                music_out.parent.mkdir(parents=True, exist_ok=True)
                bank_src = REPO_ROOT / "assets" / "music_bank" / track["file"]
                if bank_src.is_file():
                    anti_spam_edit(bank_src, music_out, video_id, duration, ffmpeg_bin="ffmpeg")
                    soundtrack["music_path"] = str(music_out)
                    write_path = out_root / "audio" / "soundtrack_plan_with_audio.json"
                    write_path.write_text(json.dumps(soundtrack, indent=2), encoding="utf-8")
                    soundtrack_audio_path = write_path
                    print(f"OK: Music Bank (track: {track['id']}, edited for {video_id})")
                else:
                    print(f"Warning: music bank track not found: {bank_src}", file=sys.stderr)
            else:
                print("Warning: no matching track in music bank", file=sys.stderr)
        except Exception as e:
            print(f"Warning: music bank failed ({e})", file=sys.stderr)

    # ── Voice synthesis (free/local TTS: CosyVoice2 CJK / Edge-TTS EN) — opt-in via --voice ──
    if args.voice or args.music:
        # Derive a routing locale from the first --languages entry (bare "en" -> "en-US").
        first_lang = (args.languages.split(",")[0] or "en").strip()
        voice_locale = "en-US" if first_lang.lower() in ("en", "en-us") else first_lang
        voice_cmd = [
            py, str(scripts / "run_voice_synthesis.py"),
            str(out_root / "soundtrack_plan.json"),
            "-o", str(out_root / "audio"),
            "--locale", voice_locale,
        ]
        if args.music:
            voice_cmd.append("--music")
        if args.force:
            voice_cmd.append("--force")
        if not run(voice_cmd, REPO_ROOT):
            print("Failed: Voice Synthesis", file=sys.stderr)
            return 1
        print("OK: Voice Synthesis")
        # Use the updated plan with audio paths
        audio_plan = out_root / "audio" / "soundtrack_plan_with_audio.json"
        if audio_plan.exists():
            soundtrack_audio_path = audio_plan

    timeline = json.loads((out_root / "timeline.json").read_text(encoding="utf-8"))
    duration_s = timeline.get("duration_s", 0)
    primary_asset_ids = [c.get("asset_id") for c in timeline.get("clips", []) if c.get("asset_id")]
    tags_list = [t.strip() for t in args.tags.split(",") if t.strip()]

    try:
        ss0 = json.loads((out_root / "script_segments.json").read_text(encoding="utf-8"))
        content_type = ss0.get("content_type", "therapeutic")
    except Exception:
        content_type = "therapeutic"

    stub_path = out_root / "distribution_stub.json"
    stub_path.write_text(json.dumps({
        "video_id": video_id,
        "plan_id": args.plan_id,
        "title": args.title,
        "description": args.description,
        "tags": tags_list,
        "primary_asset_ids": primary_asset_ids,
        "channel_id": args.channel_id,
        "hook_type": "light_reveal",
        "music_mood": "calm",
        "ite_score": 0.65,
    }, indent=2), encoding="utf-8")

    qc_cmd = [
        py, str(scripts / "run_qc.py"),
        str(out_root / "shot_plan.json"),
        str(out_root / "resolved_assets.json"),
        str(out_root / "timeline.json"),
        "-o", str(out_root / "qc_summary.json"),
        "--composited-layers", str(out_root / "composited_layers.json"),
        "--animation-plan", str(out_root / "animation_plan.json"),
        "--soundtrack-plan", str(out_root / "soundtrack_plan.json"),
        "--captions", str(out_root / "captions.json"),
        "--distribution-manifest", str(stub_path),
        "--qc-mode", "plan",
        "--vce-format", args.format,
        "--platforms", args.platforms,
        "--content-type", content_type,
    ]
    ct = content_type

    if not run(qc_cmd + job_flag, REPO_ROOT):
        print("Failed: QC", file=sys.stderr)
        return 1
    print("OK: QC")

    if not skip_render:
        render_cmd = [
            py, str(scripts / "run_render.py"),
            str(out_root / "timeline.json"),
            "-o", str(out_root),
            "--video-id", video_id,
            "--captions", str(out_root / "captions.json"),
            "--shot-plan", str(out_root / "shot_plan.json"),
            "--composited-layers", str(out_root / "composited_layers.json"),
            "--animation-plan", str(out_root / "animation_plan.json"),
        ]
        if args.assets_dir:
            render_cmd.extend(["--assets-dir", str(args.assets_dir)])
        else:
            render_cmd.append("--placeholder")
        render_cmd.extend(["--quality", args.quality])
        if soundtrack_audio_path.exists():
            render_cmd.extend(["--soundtrack-plan", str(soundtrack_audio_path)])
        if not run(render_cmd + job_flag, REPO_ROOT):
            print("Failed: Render", file=sys.stderr)
            return 1
        print("OK: Render")

        qc_pub = [
            py, str(scripts / "run_qc.py"),
            str(out_root / "shot_plan.json"),
            str(out_root / "resolved_assets.json"),
            str(out_root / "timeline.json"),
            "-o", str(out_root / "qc_summary_publish.json"),
            "--composited-layers", str(out_root / "composited_layers.json"),
            "--animation-plan", str(out_root / "animation_plan.json"),
            "--soundtrack-plan", str(out_root / "soundtrack_plan.json"),
            "--captions", str(out_root / "captions.json"),
            "--distribution-manifest", str(stub_path),
            "--qc-mode", "publish",
            "--vce-format", args.format,
            "--platforms", args.platforms,
            "--content-type", ct,
        ]
        if not run(qc_pub + job_flag, REPO_ROOT):
            print("Failed: QC (publish mode)", file=sys.stderr)
            return 1
        print("OK: QC (publish mode)")

    if not run([
        py, str(scripts / "run_platform_adapter.py"),
        str(out_root / "timeline.json"),
        str(stub_path),
        str(out_root / "animation_plan.json"),
        "-o", str(out_root / "platform_variants.json"),
        "--platforms", args.platforms,
    ] + force_flag + job_flag, REPO_ROOT):
        print("Failed: Platform Adapter", file=sys.stderr)
        return 1
    print("OK: Platform Adapter")

    if not run([
        py, str(scripts / "run_multilang_renderer.py"),
        str(out_root / "soundtrack_plan.json"),
        str(out_root / "platform_variants.json"),
        str(out_root / "captions.json"),
        "-o", str(out_root / "multilang_plan.json"),
        "--languages", args.languages,
    ] + force_flag + job_flag, REPO_ROOT):
        print("Failed: Multi-Language Renderer", file=sys.stderr)
        return 1
    print("OK: Multi-Language Renderer")

    provenance_path = f"artifacts/video/provenance/{video_id}.json"
    prov_out = REPO_ROOT / "artifacts" / "video" / "provenance"
    prov_out.mkdir(parents=True, exist_ok=True)

    prov_cmd = [
        py, str(scripts / "write_provenance.py"),
        "--video-id", video_id, "--plan-id", args.plan_id,
        "--shot-plan", str(out_root / "shot_plan.json"),
        "--resolved", str(out_root / "resolved_assets.json"),
        "--timeline", str(out_root / "timeline.json"),
        "-o", str(prov_out / f"{video_id}.json"),
        "--duration-s", str(duration_s),
        "--hook-type", "light_reveal", "--environment", "forest_path", "--motion-type", "slow_zoom",
        "--music-mood", "calm", "--caption-pattern", "question_hook", "--style-version", "v1",
    ] + force_flag
    if not run(prov_cmd, REPO_ROOT):
        print("Failed: Provenance Writer", file=sys.stderr)
        return 1
    print("OK: Provenance Writer")

    meta_cmd = [
        py, str(scripts / "write_metadata.py"),
        "--video-id", video_id, "--plan-id", args.plan_id,
        "--shot-plan", str(out_root / "shot_plan.json"),
        "--title", args.title,
        "--description", args.description,
        "--provenance-path", provenance_path, "--batch-id", "batch-2026-03-04-001",
        "-o", str(out_root / "distribution_manifest.json"),
        "--tags", args.tags,
        "--primary-asset-ids", ",".join(primary_asset_ids),
        "--hook-type", "light_reveal", "--environment", "forest_path", "--motion-type", "slow_zoom",
        "--music-mood", "calm", "--caption-pattern", "question_hook", "--style-version", "v1",
    ] + force_flag
    if not run(meta_cmd, REPO_ROOT):
        print("Failed: Metadata Writer", file=sys.stderr)
        return 1
    print("OK: Metadata Writer")

    if not run([
        py, str(scripts / "run_analytics_ingestor.py"),
        str(out_root / "distribution_manifest.json"),
        "-o", str(out_root / "analytics_feedback.json"),
    ] + force_flag, REPO_ROOT):
        print("Failed: Analytics Ingestor", file=sys.stderr)
        return 1
    print("OK: Analytics Ingestor")

    # Stage 18 — Upload/Publish (dry-run by default; --upload to enable)
    if getattr(args, "upload", False):
        upload_cmd = [
            py, str(scripts / "run_upload.py"),
            str(out_root / "platform_variants.json"),
            "--channel-id", args.channel_id,
            "--video-dir", str(out_root),
            "-o", str(out_root / "upload_results.json"),
        ]
        if args.platforms:
            upload_cmd.extend(["--platforms", args.platforms])
        if not getattr(args, "upload_live", False):
            pass  # dry-run is the default
        else:
            upload_cmd.append("--no-dry-run")
        upload_cmd.extend(job_flag)
        if not run(upload_cmd, REPO_ROOT):
            print("Failed: Upload/Publish", file=sys.stderr)
            return 1
        print("OK: Upload/Publish")

    print(f"Pipeline complete. Outputs in {out_root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
