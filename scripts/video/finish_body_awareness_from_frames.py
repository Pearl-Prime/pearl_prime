#!/usr/bin/env python3
"""
Finish TikTok body-awareness MP4 from frames (no audio). Optional ComfyUI frame gen.

Uses teacher_plans/{teacher}.json for shot order, motion, and reuse_frame_from.

Example:
  python3 scripts/video/finish_body_awareness_from_frames.py --teacher ahjan
  python3 scripts/video/finish_body_awareness_from_frames.py --teacher joshin --generate-frames
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
from scripts.video.flux_client import load_yaml  # noqa: E402

ARTIFACTS = REPO_ROOT / "artifacts" / "video" / "tiktok_body_awareness"
WORKFLOW_PATH = REPO_ROOT / "scripts" / "image_generation" / "comfyui_workflows" / "flux_video_bank.json"

CLIP_SEC = 6.0
FPS = 30
OUT_W, OUT_H = 720, 1280

STANDARD_NEGATIVE = (
    "gritty urban dread, harsh neon panic, cold sterile realism, aggressive darkness, "
    "cartoon, anime, low quality, blurry, watermark, text overlay, stock photo feel"
)


def build_full_negative() -> str:
    cfg = load_yaml("config/video/prompt_constraints.yaml")
    parts = list(cfg.get("shared_negatives") or [])[:8]
    extra = ", ".join(parts)
    if extra:
        return f"{STANDARD_NEGATIVE}, {extra}"
    return STANDARD_NEGATIVE


def comfyui_generate_image(
    comfy_url: str,
    *,
    positive: str,
    negative: str,
    width: int,
    height: int,
    seed: int,
    filename_prefix: str,
    timeout_s: float = 600.0,
) -> bytes:
    workflow = json.loads(WORKFLOW_PATH.read_text(encoding="utf-8"))
    workflow = {k: v for k, v in workflow.items() if k != "_meta"}
    if "5" in workflow:
        workflow["5"]["inputs"]["width"] = int(width)
        workflow["5"]["inputs"]["height"] = int(height)
    if "6" in workflow:
        workflow["6"]["inputs"]["text"] = positive
    if "7" in workflow:
        workflow["7"]["inputs"]["text"] = negative if negative.strip() else " "
    if "25" in workflow:
        workflow["25"]["inputs"]["noise_seed"] = seed
    elif "3" in workflow:
        workflow["3"]["inputs"]["seed"] = seed
    if "9" in workflow:
        workflow["9"]["inputs"]["filename_prefix"] = filename_prefix

    url = comfy_url.rstrip("/")
    payload = json.dumps({"prompt": workflow}).encode("utf-8")
    req = urllib.request.Request(
        f"{url}/prompt", data=payload, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        prompt_id = json.loads(resp.read().decode())["prompt_id"]

    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        time.sleep(2.5)
        try:
            with urllib.request.urlopen(urllib.request.Request(f"{url}/history/{prompt_id}"), timeout=60) as hresp:
                history = json.loads(hresp.read().decode())
        except urllib.error.URLError:
            continue
        if prompt_id not in history:
            continue
        entry = history[prompt_id]
        st = entry.get("status", {})
        if st.get("completed") is False and st.get("status_str") == "error":
            raise RuntimeError(json.dumps(entry, indent=2)[:4000])
        outputs = entry.get("outputs") or {}
        for node_out in outputs.values():
            if not isinstance(node_out, dict):
                continue
            for img in node_out.get("images") or []:
                params = urllib.parse.urlencode(
                    {
                        "filename": img["filename"],
                        "subfolder": img.get("subfolder", ""),
                        "type": img.get("type", "output"),
                    }
                )
                with urllib.request.urlopen(f"{url}/view?{params}", timeout=120) as iresp:
                    return iresp.read()
        for node_out in outputs.values():
            if isinstance(node_out, dict) and node_out.get("exception_message"):
                raise RuntimeError(str(node_out.get("exception_message")))
    raise RuntimeError(f"ComfyUI timeout prompt_id={prompt_id!r}")


def run_ffmpeg(args: list[str], *, label: str) -> None:
    p = subprocess.run(args, capture_output=True, text=True)
    if p.returncode != 0:
        sys.stderr.write(f"ffmpeg failed ({label}): {p.stderr}\n")
        raise RuntimeError(f"ffmpeg {label} failed")


def motion_clip(motion: str, src_png: Path, dst_mp4: Path) -> None:
    d = int(CLIP_SEC * FPS)
    common_end = ["-t", str(CLIP_SEC), "-r", str(FPS), "-pix_fmt", "yuv420p", "-c:v", "libx264", "-preset", "medium"]

    if motion == "static_hold":
        cmd = [
            "ffmpeg", "-y", "-loop", "1", "-i", str(src_png),
            "-vf", f"scale={OUT_W}:{OUT_H}:flags=lanczos", *common_end, str(dst_mp4),
        ]
        run_ffmpeg(cmd, label="static_hold")
        return

    if motion == "fade_transition":
        vf = f"scale={OUT_W}:{OUT_H}:flags=lanczos,fade=t=in:st=0:d=0.5:color=black"
        cmd = ["ffmpeg", "-y", "-loop", "1", "-i", str(src_png), "-vf", vf, *common_end, str(dst_mp4)]
        run_ffmpeg(cmd, label="fade_transition")
        return

    if motion == "slow_zoom_in":
        zexpr = "min(zoom+0.0012,1.28)"
        vf = (
            f"scale=8000:-1,zoompan=z='{zexpr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={d}:s={OUT_W}x{OUT_H}:fps={FPS}"
        )
        cmd = ["ffmpeg", "-y", "-loop", "1", "-i", str(src_png), "-vf", vf, *common_end, str(dst_mp4)]
        run_ffmpeg(cmd, label="slow_zoom_in")
        return

    if motion == "micro_zoom":
        zexpr = "min(zoom+0.0006,1.12)"
        vf = (
            f"scale=6000:-1,zoompan=z='{zexpr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={d}:s={OUT_W}x{OUT_H}:fps={FPS}"
        )
        cmd = ["ffmpeg", "-y", "-loop", "1", "-i", str(src_png), "-vf", vf, *common_end, str(dst_mp4)]
        run_ffmpeg(cmd, label="micro_zoom")
        return

    if motion == "slow_motion":
        zexpr = "min(zoom+0.0007,1.18)"
        vf = (
            f"scale=7000:-1,zoompan=z='{zexpr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={d}:s={OUT_W}x{OUT_H}:fps={FPS},"
            f"vignette=PI/5"
        )
        cmd = ["ffmpeg", "-y", "-loop", "1", "-i", str(src_png), "-vf", vf, *common_end, str(dst_mp4)]
        run_ffmpeg(cmd, label="slow_motion")
        return

    if motion == "fluid_motion":
        zexpr = "min(zoom+0.0009,1.22)"
        xexpr = "iw/2-(iw/zoom/2)+on*0.15"
        yexpr = "ih/2-(ih/zoom/2)+on*0.08"
        vf = f"scale=7500:-1,zoompan=z='{zexpr}':x='{xexpr}':y='{yexpr}':d={d}:s={OUT_W}x{OUT_H}:fps={FPS}"
        cmd = ["ffmpeg", "-y", "-loop", "1", "-i", str(src_png), "-vf", vf, *common_end, str(dst_mp4)]
        run_ffmpeg(cmd, label="fluid_motion")
        return

    if motion == "slow_pan":
        xexpr = f"50+on*({OUT_W*0.35}/{d})"
        vf = (
            f"scale=5200:-1,zoompan=z=1.12:x='{xexpr}':y='ih/2-(ih/zoom/2)':d={d}:s={OUT_W}x{OUT_H}:fps={FPS}"
        )
        cmd = ["ffmpeg", "-y", "-loop", "1", "-i", str(src_png), "-vf", vf, *common_end, str(dst_mp4)]
        run_ffmpeg(cmd, label="slow_pan")
        return

    if motion == "quick_jump_cuts":
        sc = "scale=1600:2844:flags=lanczos"
        filt = (
            f"[0:v]{sc},split=3[a][b][c];"
            f"[a]crop=720:1280:80:200,trim=duration=2,setpts=PTS-STARTPTS[v0];"
            f"[b]crop=720:1280:520:640,trim=duration=2,setpts=PTS-STARTPTS[v1];"
            f"[c]crop=720:1280:300:900,trim=duration=2,setpts=PTS-STARTPTS[v2];"
            f"[v0][v1][v2]concat=n=3:v=1:a=0,trim=duration={CLIP_SEC},setpts=PTS-STARTPTS[outv]"
        )
        cmd = [
            "ffmpeg", "-y", "-loop", "1", "-i", str(src_png), "-filter_complex", filt,
            "-map", "[outv]", *common_end, str(dst_mp4),
        ]
        run_ffmpeg(cmd, label="quick_jump_cuts")
        return

    if motion == "cut_sequence":
        filt = (
            f"[0:v]scale=2000:-1,split=3[a][b][c];"
            f"[a]crop=720:1280:200:120,trim=duration=2,setpts=PTS-STARTPTS[v0];"
            f"[b]crop=720:1280:640:300,trim=duration=2,setpts=PTS-STARTPTS[v1];"
            f"[c]crop=720:1280:400:500,trim=duration=2,setpts=PTS-STARTPTS[v2];"
            f"[v0][v1][v2]concat=n=3:v=1:a=0,trim=duration={CLIP_SEC},setpts=PTS-STARTPTS[outv]"
        )
        cmd = [
            "ffmpeg", "-y", "-loop", "1", "-i", str(src_png), "-filter_complex", filt,
            "-map", "[outv]", *common_end, str(dst_mp4),
        ]
        run_ffmpeg(cmd, label="cut_sequence")
        return

    if motion == "match_cut_loop":
        motion_clip("static_hold", src_png, dst_mp4)
        return

    motion_clip("static_hold", src_png, dst_mp4)


def concat_clips(clips: list[Path], out_mp4: Path) -> None:
    lst = out_mp4.parent / "concat_list.txt"
    lst.write_text("\n".join(f"file '{c.resolve()}'" for c in clips) + "\n", encoding="utf-8")
    run_ffmpeg(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out_mp4)],
        label="concat",
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--teacher", default="ahjan")
    ap.add_argument("--skip-existing-clips", action="store_true", help="reuse clips/*.mp4 if already present")
    ap.add_argument("--generate-frames", action="store_true", help="call ComfyUI for any missing PNGs (non-reuse shots)")
    ap.add_argument(
        "--comfy-url",
        default=os.environ.get("COMFYUI_URL", "http://192.168.1.112:8188").strip(),
    )
    args = ap.parse_args()

    if not shutil.which("ffmpeg"):
        print("ffmpeg required", file=sys.stderr)
        return 1

    plan_path = ARTIFACTS / "teacher_plans" / f"{args.teacher}.json"
    if not plan_path.is_file():
        print(f"Missing plan {plan_path}", file=sys.stderr)
        return 1
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    teacher_id = plan.get("teacher_id", args.teacher)
    shots: list[dict] = plan.get("shots") or []
    if len(shots) != 10:
        print(f"Expected 10 shots, got {len(shots)}", file=sys.stderr)
        return 1

    out_dir = ARTIFACTS / teacher_id
    frames_dir = out_dir / "frames"
    clips_dir = out_dir / "clips"
    work_dir = out_dir / "_work"
    frames_dir.mkdir(parents=True, exist_ok=True)
    clips_dir.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(parents=True, exist_ok=True)

    neg = build_full_negative()
    comfy_url = (args.comfy_url or "").strip()

    for i, shot in enumerate(shots):
        sid = str(shot["shot_id"])
        if shot.get("reuse_frame_from"):
            continue
        dst = frames_dir / f"{sid}.png"
        if dst.is_file():
            continue
        if not args.generate_frames:
            print(f"Missing frame {dst}; re-run with --generate-frames (ComfyUI).", file=sys.stderr)
            return 1
        if not comfy_url:
            print("Set COMFYUI_URL or pass --comfy-url", file=sys.stderr)
            return 1
        if not WORKFLOW_PATH.is_file():
            print(f"Missing workflow {WORKFLOW_PATH}", file=sys.stderr)
            return 1
        prompt = str(shot.get("prompt", "")).strip()
        if not prompt or prompt.startswith("(reuses"):
            print(f"Shot {sid} missing prompt", file=sys.stderr)
            return 1
        style = str(plan.get("style", "")).strip()
        positive = f"{prompt}. Style continuity: {style}. Vertical 9:16 composition, 720 by 1280 intent."
        seed = 910_000 + i * 17_359
        prefix = f"tiktok_body_{teacher_id}_{sid}"
        print(f"[ComfyUI] {sid} …", flush=True)
        img = comfyui_generate_image(
            comfy_url,
            positive=positive,
            negative=neg,
            width=OUT_W,
            height=OUT_H,
            seed=seed,
            filename_prefix=prefix,
        )
        dst.write_bytes(img)
        print(f"     saved {dst} ({len(img):,} bytes)")

    for shot in shots:
        sid = str(shot["shot_id"])
        reuse = shot.get("reuse_frame_from")
        if not reuse:
            continue
        dst = frames_dir / f"{sid}.png"
        src = frames_dir / f"{str(reuse)}.png"
        if not src.is_file():
            print(f"Missing reuse source frame {src}", file=sys.stderr)
            return 1
        shutil.copy2(src, dst)
        print(f"reuse frame {reuse} → {sid}")

    frame_paths: dict[str, Path] = {str(s["shot_id"]): frames_dir / f"{str(s['shot_id'])}.png" for s in shots}
    for sid, pth in frame_paths.items():
        if not pth.is_file():
            print(f"Missing frame {pth}", file=sys.stderr)
            return 1

    clips: list[Path] = []
    for shot in shots:
        sid = str(shot["shot_id"])
        motion = str(shot.get("motion", "static_hold"))
        src_png = frame_paths[sid]
        clip_p = clips_dir / f"{sid}.mp4"
        if args.skip_existing_clips and clip_p.is_file():
            print(f"skip clip {clip_p.name}")
            clips.append(clip_p)
            continue
        print(f"motion {sid} ({motion}) …", flush=True)
        motion_clip(motion, src_png, clip_p)
        clips.append(clip_p)

    raw_video = work_dir / "video_noaudio.mp4"
    concat_clips(clips, raw_video)
    final_mp4 = out_dir / "final_tiktok.mp4"
    shutil.copy2(raw_video, final_mp4)
    print(f"Wrote {final_mp4} (video only, no audio)")

    p = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=width,height",
         "-of", "default=noprint_wrappers=1", str(final_mp4)],
        capture_output=True, text=True,
    )
    print("--- ffprobe ---")
    print(p.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
