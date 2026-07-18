#!/usr/bin/env python3
"""
Render assembly JSON → MP3 (TTS + FFmpeg mix + loudnorm + ID3).

See docs/PODCAST_PIPELINE_INTEGRATION_SPEC.md Gap 7b.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.music.select_and_edit import anti_spam_edit  # noqa: E402
from scripts.podcast._lib import cjk_locale, load_yaml  # noqa: E402

BANK_DIR = REPO_ROOT / "assets" / "music_bank"


def get_ffmpeg() -> str:
    return os.environ.get("FFMPEG_BIN", "ffmpeg")


def run_ff(cmd: list[str], *, dry_run: bool = False) -> bool:
    if dry_run:
        print(" ".join(cmd))
        return True
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr[-2000:] + "\n")
        return False
    return True


def _edge_tts(text: str, voice: str, out: Path, dry_run: bool) -> bool:
    if dry_run:
        print(f"edge-tts → {out}")
        return True
    out.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        [
            sys.executable,
            "-m",
            "edge_tts",
            "--text",
            text[:5000],
            "--voice",
            voice,
            "--write-media",
            str(out),
        ],
        capture_output=True,
        text=True,
        timeout=180,
    )
    return r.returncode == 0 and out.exists() and out.stat().st_size > 500


def _elevenlabs_tts(text: str, voice_id: str, model: str, out_mp3: Path, dry_run: bool) -> bool:
    key = (os.environ.get("ELEVENLABS_API_KEY") or "").strip()
    if not key:
        return False
    if dry_run:
        print(f"elevenlabs → {out_mp3}")
        return True
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    payload = json.dumps(
        {"text": text[:9000], "model_id": model},
    ).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"xi-api-key": key, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            out_mp3.parent.mkdir(parents=True, exist_ok=True)
            out_mp3.write_bytes(resp.read())
        return out_mp3.stat().st_size > 500
    except Exception as e:
        sys.stderr.write(f"ElevenLabs error: {e}\n")
        return False


def _cosyvoice_tts(text: str, speaker: str, out_path: Path, dry_run: bool) -> bool:
    base = (os.environ.get("COSYVOICE_URL") or "").strip().rstrip("/")
    if not base:
        return False
    if dry_run:
        print(f"cosyvoice → {out_path}")
        return True
    payload = json.dumps({"text": text[:5000], "speaker": speaker or "english_female"}).encode("utf-8")
    req = urllib.request.Request(
        f"{base}/api/v1/tts",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            data = resp.read()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(data)
        return out_path.stat().st_size > 500
    except Exception as e:
        sys.stderr.write(f"CosyVoice error: {e}\n")
        return False


def synth_speech(text: str, vc: dict[str, Any], out_wav: Path, dry_run: bool) -> bool:
    """Produce PCM WAV at project sample rate (44.1k mono)."""
    loc = vc.get("locale") or "en-US"
    provider = (vc.get("provider") or "edge_tts").lower()
    voice_id = vc.get("voice_id") or ""
    edge_fb = vc.get("edge_fallback") or "en-US-JennyNeural"
    model = vc.get("model") or "eleven_multilingual_v2"
    ref = vc.get("reference_id") or "english_female"

    if dry_run:
        print(f"TTS ({provider}) → {out_wav.name}")
        return True

    mid = out_wav.with_suffix(".mid.bin")
    chosen: Path | None = None
    if cjk_locale(loc) and provider == "cosyvoice2":
        p = mid.with_suffix(".cosy.wav")
        if _cosyvoice_tts(text, ref or voice_id or "english_female", p, dry_run=False):
            chosen = p
    if chosen is None and provider == "elevenlabs" and voice_id:
        p = mid.with_suffix(".el.mp3")
        if _elevenlabs_tts(text, voice_id, model, p, dry_run=False):
            chosen = p
    if chosen is None and provider == "edge_tts":
        p = mid.with_suffix(".edge.mp3")
        if _edge_tts(text, edge_fb, p, dry_run=False):
            chosen = p
    if chosen is None:
        p = mid.with_suffix(".edge.mp3")
        if _edge_tts(text, edge_fb, p, dry_run=False):
            chosen = p
    if chosen is None:
        return False

    cmd = [get_ffmpeg(), "-y", "-i", str(chosen), "-ar", "44100", "-ac", "1", str(out_wav)]
    ok = run_ff(cmd)
    chosen.unlink(missing_ok=True)
    return ok and out_wav.exists()


def probe_duration(path: Path) -> float:
    r = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=nokey=1:noprint_wrappers=1",
            str(path),
        ],
        capture_output=True,
        text=True,
    )
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def build_music_bed(
    cue: dict[str, Any] | None,
    episode_id: str,
    seg: str,
    target_s: float,
    out_wav: Path,
    dry_run: bool,
) -> bool:
    """Loop / extend music to target_s. Falls back to pink noise if no file."""
    if dry_run:
        print(f"music bed {target_s}s → {out_wav}")
        return True
    track = (cue or {}).get("track") or {}
    rel = track.get("file")
    src = BANK_DIR / rel if rel else None
    if not src or not src.is_file():
        # deterministic soft tone via lavfi
        return run_ff(
            [
                get_ffmpeg(),
                "-y",
                "-f",
                "lavfi",
                "-i",
                f"sine=frequency=220:sample_rate=44100:d={max(1.0, target_s)}",
                "-ac",
                "1",
                str(out_wav),
            ],
        )

    # Unique fingerprint per episode segment (anti-spam edit when possible)
    tmp_mp3 = out_wav.with_suffix(".bed.mp3")
    try:
        anti_spam_edit(src, tmp_mp3, f"{episode_id}:{seg}", target_s, ffmpeg_bin=get_ffmpeg())
    except Exception:
        shutil.copy(src, tmp_mp3)
    cmd = [
        get_ffmpeg(),
        "-y",
        "-stream_loop",
        "-1",
        "-i",
        str(tmp_mp3),
        "-t",
        str(max(1.0, target_s)),
        "-ar",
        "44100",
        "-ac",
        "1",
        str(out_wav),
    ]
    ok = run_ff(cmd)
    tmp_mp3.unlink(missing_ok=True)
    return ok


def mix_bed_voice(voice_wav: Path, music_wav: Path | None, target_s: float, out_wav: Path, dry_run: bool) -> bool:
    """Voice 0 dB ref; music ~-18 dB; amix. Pads voice to target_s."""
    if dry_run:
        print(f"mix → {out_wav}")
        return True
    dur_v = probe_duration(voice_wav)
    pad = max(0.0, target_s - dur_v)
    if not music_wav:
        return run_ff(
            [
                get_ffmpeg(),
                "-y",
                "-i",
                str(voice_wav),
                "-af",
                f"apad=whole_dur={target_s}",
                str(out_wav),
            ],
        )

    filt = (
        f"[1:a]volume=-18dB[m];"
        f"[0:a]apad=whole_dur={target_s}[v];"
        f"[m]apad=whole_dur={target_s}[m2];"
        f"[v][m2]amix=inputs=2:duration=longest[a]"
    )
    cmd = [
        get_ffmpeg(),
        "-y",
        "-i",
        str(voice_wav),
        "-i",
        str(music_wav),
        "-filter_complex",
        filt,
        "-map",
        "[a]",
        str(out_wav),
    ]
    if not run_ff(cmd):
        # Retry simpler mix
        return run_ff(
            [
                get_ffmpeg(),
                "-y",
                "-i",
                str(voice_wav),
                "-i",
                str(music_wav),
                "-filter_complex",
                f"[0:a]apad=whole_dur={target_s}[v];[1:a]volume=-18dB,apad=whole_dur={target_s}[m];"
                f"[v][m]amix=inputs=2:duration=longest[a]",
                "-map",
                "[a]",
                str(out_wav),
            ],
        )
    return True


def concat_wavs(paths: list[Path], out_wav: Path, dry_run: bool) -> bool:
    if dry_run:
        print(f"concat {len(paths)} → {out_wav}")
        return True
    lst = out_wav.parent / "concat_list.txt"
    lines = []
    for p in paths:
        safe = str(p.resolve()).replace("'", "'\\''")
        lines.append(f"file '{safe}'")
    lst.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return run_ff(
        [get_ffmpeg(), "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out_wav)],
    )


def _loudnorm_pass1(wav: Path, i: float, tp: float, lra: float = 11.0) -> dict[str, Any]:
    r = subprocess.run(
        [
            get_ffmpeg(),
            "-hide_banner",
            "-nostats",
            "-i",
            str(wav),
            "-af",
            f"loudnorm=I={i}:TP={tp}:LRA={lra}:print_format=json",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
    )
    err = r.stderr or ""
    jstart = err.rfind("{")
    jend = err.rfind("}") + 1
    if jstart < 0 or jend <= jstart:
        return {}
    return json.loads(err[jstart:jend])


def loudness_targets(fmt: str) -> tuple[float, float]:
    pf = load_yaml(REPO_ROOT / "config" / "podcast" / "podcast_format.yaml")
    fdef = (pf.get("formats") or {}).get(fmt) or {}
    audio = fdef.get("audio") or {}
    i = float(audio.get("loudness_target_lufs") or -16)
    tp_raw = audio.get("true_peak_dbtp") if audio.get("true_peak_dbtp") is not None else -1.0
    if isinstance(tp_raw, str):
        tp = float(tp_raw.replace("dBTP", "").replace("dBTp", "").strip())
    else:
        tp = float(tp_raw)
    return i, tp


def encode_mp3(
    wav: Path,
    mp3: Path,
    meta: dict[str, Any],
    fmt: str,
    dry_run: bool,
) -> bool:
    i, tp = loudness_targets(fmt)
    if dry_run:
        print(f"loudnorm I={i} → {mp3}")
        return True
    # libmp3lame + music beds: EBU integrated meters lower than loudnorm I on PCM.
    # Longer episodes need slightly more gain compensation in practice.
    dur_w = probe_duration(wav)
    bump = 6.2 if dur_w > 780.0 else 4.5
    i_enc = i + bump
    lra = 11.0
    m = _loudnorm_pass1(wav, i_enc, tp, lra)
    af = f"loudnorm=I={i_enc}:TP={tp}:LRA={lra}:print_format=summary"
    if m:
        af = (
            f"loudnorm=I={i_enc}:TP={tp}:LRA={lra}"
            f":measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
            f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true:print_format=summary"
        )
    title = meta.get("title") or "Episode"
    teacher = meta.get("teacher_name") or "Teacher"
    series = meta.get("series_title") or "Series"
    epn = str(meta.get("episode_number") or 1)
    cmd = [
        get_ffmpeg(),
        "-y",
        "-i",
        str(wav),
        "-af",
        af,
        "-ar",
        "44100",
        "-ac",
        "1",
        "-c:a",
        "libmp3lame",
        "-b:a",
        "128k",
        "-metadata",
        f"title={title}",
        "-metadata",
        f"artist={teacher}",
        "-metadata",
        f"album={series}",
        "-metadata",
        f"track={epn}",
        "-metadata",
        "genre=Education",
        "-metadata",
        "date=2026",
        str(mp3),
    ]
    return run_ff(cmd)


def id3_mutagen(mp3: Path, meta: dict[str, Any]) -> None:
    try:
        from mutagen.easyid3 import EasyID3  # type: ignore
        from mutagen.id3 import ID3  # type: ignore
    except ImportError:
        return
    try:
        audio = EasyID3(str(mp3))
    except Exception:
        audio = EasyID3()
        audio.save(str(mp3), v2_version=3)
        audio = EasyID3(str(mp3))
    audio["title"] = meta.get("title") or "Episode"
    audio["artist"] = meta.get("teacher_name") or "Teacher"
    audio["album"] = meta.get("series_title") or "Series"
    audio["tracknumber"] = str(meta.get("episode_number") or 1)
    audio["genre"] = "Education"
    audio["date"] = "2026"
    audio.save(v2_version=3)


def loudnorm_report(mp3: Path) -> dict[str, Any]:
    r = subprocess.run(
        [
            get_ffmpeg(),
            "-i",
            str(mp3),
            "-af",
            "loudnorm=print_format=json",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
    )
    err = r.stderr or ""
    m = re.search(r"\{[^{}]*\}", err, re.DOTALL)
    if not m:
        return {"raw": err[-800:]}
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return {"raw": m.group(0)[:400]}


def render(assembly_path: Path, output_mp3: Path, voice_provider: str, dry_run: bool) -> dict[str, Any]:
    data = json.loads(assembly_path.read_text(encoding="utf-8"))
    fmt = data.get("format") or "podcast_episode"
    episode_id = data.get("episode_id") or "episode"
    vc = dict(data.get("voice_config") or {})
    if voice_provider and voice_provider != "auto":
        vc["provider"] = voice_provider

    segments = data.get("segments") or []
    meta = {
        "title": (data.get("metadata") or {}).get("title"),
        "teacher_name": data.get("teacher_name"),
        "series_title": data.get("series_title"),
        "episode_number": data.get("episode_number"),
    }

    report: dict[str, Any] = {"episode_id": episode_id, "segments": [], "errors": []}
    mixed: list[Path] = []

    with tempfile.TemporaryDirectory(prefix="podcast_") as td:
        tdir = Path(td)
        for i, seg in enumerate(segments):
            sid = seg.get("segment_id") or f"seg{i}"
            text = (seg.get("text") or "").strip()
            target = float(seg.get("duration_target_s") or 120)
            cue = seg.get("music_cue")

            vwav = tdir / f"{i:03d}_{sid}_voice.wav"
            mwav = tdir / f"{i:03d}_{sid}_music.wav"
            out = tdir / f"{i:03d}_{sid}_mix.wav"

            if text:
                if not synth_speech(text, vc, vwav, dry_run):
                    report["errors"].append(f"TTS failed for {sid}")
                    continue
            else:
                # ambient-only segment
                run_ff(
                    [get_ffmpeg(), "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "0.5", str(vwav)],
                    dry_run=dry_run,
                )

            mus = None
            if cue and cue.get("track"):
                if build_music_bed(cue, episode_id, sid, target, mwav, dry_run):
                    mus = mwav

            if not mix_bed_voice(vwav, mus, target, out, dry_run):
                report["errors"].append(f"mix failed for {sid}")
                continue
            mixed.append(out)
            dur_s = 0.0 if dry_run else probe_duration(out)
            report["segments"].append({"segment_id": sid, "duration_s": dur_s})

        if not mixed:
            report["errors"].append("no segments rendered")
            return report

        full = tdir / "full.wav"
        if not concat_wavs(mixed, full, dry_run):
            report["errors"].append("concat failed")
            return report

        out_mp3 = output_mp3.resolve()
        out_mp3.parent.mkdir(parents=True, exist_ok=True)
        if not encode_mp3(full, out_mp3, meta, fmt, dry_run):
            report["errors"].append("mp3 encode failed")
            return report

        if dry_run:
            report["output_mp3"] = str(out_mp3)
            report["duration_s"] = 0.0
            report["file_size_bytes"] = 0
            report["loudness"] = {}
            return report

    id3_mutagen(output_mp3, meta)
    rep_path = output_mp3.with_suffix(".render_report.json")
    duration = probe_duration(output_mp3)
    ln = loudnorm_report(output_mp3)
    report["output_mp3"] = str(output_mp3)
    report["duration_s"] = duration
    report["file_size_bytes"] = output_mp3.stat().st_size if output_mp3.exists() else 0
    report["loudness"] = ln
    if not dry_run:
        rep_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description="Render podcast assembly to MP3")
    ap.add_argument("--assembly", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--voice-provider", default="auto")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--workspace", type=Path, default=None, help="Directory containing job.json (default: parent of --output)")
    ap.add_argument("--no-job-check", dest="no_job_check", action="store_true", help="Skip job.json enforcement (CI only)")
    args = ap.parse_args()
    if args.no_job_check:
        print("WARNING: --no-job-check: pipeline job enforcement disabled (CI/testing only).", file=sys.stderr)
    from scripts.pipeline.advance_stage import mark_complete, mark_failed
    from scripts.pipeline.check_job import require_stage

    ws = (args.workspace or args.output.parent).resolve()
    if not args.no_job_check:
        require_stage("render_audio", ws)

    report = render(args.assembly.resolve(), args.output.resolve(), args.voice_provider, args.dry_run)
    if report.get("errors"):
        for e in report["errors"]:
            print("ERROR:", e, file=sys.stderr)
        if not args.no_job_check:
            mark_failed(ws, "render_audio", error="render errors")
        return 1
    print(json.dumps(report, indent=2))
    if not args.no_job_check:
        mark_complete(ws, "render_audio", output=args.output.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
