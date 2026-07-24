#!/usr/bin/env python3
"""Render STYLE A — kinetic typography on bold plates — for 3 faceless pilots.

Fast kinetic type on bold solid/gradient plates. Punchy word-group reveals,
hard cuts between beats, brief settled hold on payoff. Not photo Ken Burns —
this is the saturated kinetic family (competitive wellness Reel, not a
slideshow).

Pipeline (per pilot):
  1. background.mp4  — concat of solid/gradient color plates (hard cuts),
     one plate per beat, generated via ffmpeg lavfi `color`/`gradients`
     source filters. A single-frame accent "color snap" flash is drawn on
     top of the first ~80ms for the hook pattern-interrupt.
  2. captions.ass     — libass kinetic type: cumulative word-group builds
     with a scale-punch-in (`\\t` transform) + quick fade, hard-swapped
     between reveal steps, holding on the final step of each beat.
  3. typed_silent.mp4 — background + `ass=` filter burned in, no audio.
  4. audio mix (wav)  — soft ambient bed (full length) + synthesized SFX:
     soft hit on hook, three ticks on the mechanism label build, one click
     on the practice reveal, and a resolve chime on payoff. All synthesized
     with ffmpeg lavfi sources (sine/anoisesrc) — no paid APIs.
  5. final/<id>.mp4   — typed_silent + audio mux, AAC, 1080x1920.

Authority: docs/PEARL_ANIMATOR_FACELESS_SHORTS_SPEC_2026-07-18.md
Captions/topics reused verbatim from
artifacts/qa/social_visual_rebuild_publishable_quality_20260718/
  lane05_pearl_animator_rebuild/shortform_publishable_storyboards.json
Beat timing is this look's own beat map (see BEAT_TIMES), not the source
storyboard's durations — kinetic type paces faster than the b-roll cut.

Does not live-publish. Does not claim beautiful/shippable — labels
"system working" pending operator look, per LOOK_VARIANT.md.
"""
from __future__ import annotations

import os as _os
def _mb_ffmpeg_preset() -> str:
    return _os.environ.get("MEDIA_BANK_FFMPEG_PRESET", "medium")

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
STORYBOARDS = (
    REPO
    / "artifacts/qa/social_visual_rebuild_publishable_quality_20260718"
    / "lane05_pearl_animator_rebuild/shortform_publishable_storyboards.json"
)
OUT_ROOT = (
    REPO
    / "artifacts/qa/social_finish_20260718/lane03_research_complete"
    / "variants/kinetic_type"
)
WIDTH, HEIGHT, FPS = 1080, 1920, 30

# Pearl calm-but-punchy palette — deliberately not purple-AI, not cream+terracotta.
CHARCOAL = "1C1B19"
CREAM = "F3EEE3"
ACCENT = "2F6F5E"  # deep teal-emerald

BEAT_TIMES = [(0.0, 1.5), (1.5, 6.0), (6.0, 13.0), (13.0, 20.0), (20.0, 25.0)]
ROLE_ORDER = ["hook", "recognition", "mechanism", "practice", "payoff"]
TOTAL_DURATION_S = BEAT_TIMES[-1][1]

BG_SPEC = {
    "hook": {"kind": "solid", "colors": [CHARCOAL]},
    "recognition": {"kind": "solid", "colors": [CREAM]},
    "mechanism": {"kind": "gradient", "colors": [CHARCOAL, ACCENT]},
    "practice": {"kind": "solid", "colors": [ACCENT]},
    "payoff": {"kind": "solid", "colors": [CHARCOAL]},
}
TEXT_COLOR = {
    "hook": CREAM,
    "recognition": CHARCOAL,
    "mechanism": CREAM,
    "practice": CREAM,
    "payoff": CREAM,
}
FONT_NAME = "Arial Black"


def _ffmpeg() -> str:
    for candidate in (Path("/opt/homebrew/bin/ffmpeg"), Path("/usr/local/bin/ffmpeg")):
        if candidate.is_file():
            return str(candidate)
    return "ffmpeg"


def _ffprobe() -> str:
    for candidate in (Path("/opt/homebrew/bin/ffprobe"), Path("/usr/local/bin/ffprobe")):
        if candidate.is_file():
            return str(candidate)
    return "ffprobe"


def _run(cmd: list[str], label: str) -> None:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"{label} failed:\ncmd={' '.join(cmd)}\n{proc.stderr[-3000:]}")


def hex_to_ass_bgr(hex_rgb: str) -> str:
    """RRGGBB -> ASS &H00BBGGRR& (opaque)."""
    r, g, b = hex_rgb[0:2], hex_rgb[2:4], hex_rgb[4:6]
    return f"&H00{b}{g}{r}&".upper().replace("&H00", "&H00", 1)


def ass_time(t: float) -> str:
    if t < 0:
        t = 0.0
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h:d}:{m:02d}:{s:05.2f}"


def wrap2(text: str, max_chars: int = 18) -> str:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if len(trial) <= max_chars or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    if len(lines) > 2:
        lines = [lines[0], " ".join(lines[1:])]
    return "\\N".join(lines)


def split_into_n(text: str, n: int) -> list[str]:
    words = text.split()
    n = max(1, min(n, len(words)))
    k, m = divmod(len(words), n)
    groups, idx = [], 0
    for i in range(n):
        size = k + (1 if i < m else 0)
        groups.append(" ".join(words[idx : idx + size]))
        idx += size
    return [g for g in groups if g]


def word_groups(text: str, group_size: int) -> list[str]:
    words = text.split()
    return [" ".join(words[i : i + group_size]) for i in range(0, len(words), group_size)]


def font_size_for(final_text: str, role: str) -> int:
    length = len(final_text)
    base = 120 if role == "hook" else 96
    if length > 34:
        base -= 20
    elif length > 22:
        base -= 8
    return base


def build_beat_lines(
    role: str, text: str, start: float, end: float
) -> tuple[list[str], list[float]]:
    """Return (ASS Dialogue lines, absolute reveal timestamps) for one beat."""
    color = hex_to_ass_bgr(TEXT_COLOR[role])
    fsize = font_size_for(text, role)
    x, y = WIDTH // 2, 900
    dur = end - start
    lines: list[str] = []
    reveal_times: list[float] = []

    if role == "hook":
        group_size = 3 if len(text.split()) > 6 else 2
        groups = word_groups(text.upper(), group_size)
        cumulative = [" ".join(groups[: i + 1]) for i in range(len(groups))]
    elif role == "mechanism":
        groups = split_into_n(text, 3)
        cumulative = [" ".join(groups[: i + 1]) for i in range(len(groups))]
    elif role == "practice":
        groups = word_groups(text, 1)
        cumulative = [" ".join(groups[: i + 1]) for i in range(len(groups))]
    else:
        cumulative = [text]

    n = len(cumulative)
    gap = min(0.30, max(0.16, (dur * 0.55) / max(n, 1)))
    for i, step_text in enumerate(cumulative):
        step_start = start + i * gap
        step_end = end if i == n - 1 else start + (i + 1) * gap
        reveal_times.append(step_start)
        display = wrap2(step_text, max_chars=16 if role == "hook" else 20)
        is_last = i == n - 1
        fade = "\\fad(50,110)" if is_last else "\\fad(40,0)"
        override = (
            f"{{\\an5\\pos({x},{y})\\c{color}\\fscx132\\fscy132"
            f"\\t(0,140,\\fscx100\\fscy100){fade}}}"
        )
        lines.append(
            f"Dialogue: 0,{ass_time(step_start)},{ass_time(step_end)},"
            f"Default,,0,0,0,,{override}{display}"
        )

    if role == "payoff":
        accent = hex_to_ass_bgr(ACCENT)
        bar_y = y + fsize // 2 + 46
        bar = (
            f"{{\\an5\\pos({x},{bar_y})\\c{accent}\\fad(50,110)\\p1}}"
            "m -120 0 l 120 0 l 120 6 l -120 6{\\p0}"
        )
        lines.append(
            f"Dialogue: 0,{ass_time(start)},{ass_time(end)},Default,,0,0,0,,{bar}"
        )

    # apply per-line fontsize by rewriting the style reference size in override
    lines = [ln.replace("\\fscx132\\fscy132", f"\\fs{fsize}\\fscx132\\fscy132") for ln in lines]
    return lines, reveal_times


def build_ass(beats: list[dict], out_path: Path) -> dict:
    """Write the ASS file; return SFX cue times (seconds, absolute)."""
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {WIDTH}
PlayResY: {HEIGHT}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{FONT_NAME},96,&H00F3EEE3,&H00F3EEE3,&H001A1A1A,&H00000000,0,0,0,0,100,100,0,0,1,3,0,5,80,80,80,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    all_lines: list[str] = []
    cues = {"hook_hit_s": 0.0, "mechanism_ticks_s": [], "practice_click_s": 0.0, "payoff_chime_s": 0.0}
    for beat in beats:
        role = beat["role"]
        lines, reveals = build_beat_lines(role, beat["text"], beat["start"], beat["end"])
        all_lines.extend(lines)
        if role == "hook":
            cues["hook_hit_s"] = beat["start"]
        elif role == "mechanism":
            cues["mechanism_ticks_s"] = reveals
        elif role == "practice":
            cues["practice_click_s"] = reveals[0] if reveals else beat["start"]
        elif role == "payoff":
            cues["payoff_chime_s"] = beat["start"]
    out_path.write_text(header + "\n".join(all_lines) + "\n", encoding="utf-8")
    return cues


def lavfi_source(role: str, dur: float) -> str:
    spec = BG_SPEC[role]
    if spec["kind"] == "solid":
        c = spec["colors"][0]
        return f"color=c=0x{c}:s={WIDTH}x{HEIGHT}:d={dur}:r={FPS}"
    c0, c1 = spec["colors"]
    return (
        f"gradients=s={WIDTH}x{HEIGHT}:d={dur}:r={FPS}:c0=0x{c0}:c1=0x{c1}:"
        f"x0=0:y0=0:x1=0:y1={HEIGHT}:type=linear:speed=0"
    )


def build_typed_silent(beats: list[dict], ass_path: Path, out_path: Path) -> None:
    inputs: list[str] = []
    for beat in beats:
        dur = beat["end"] - beat["start"]
        inputs += ["-f", "lavfi", "-i", lavfi_source(beat["role"], dur)]
    n = len(beats)
    concat_in = "".join(f"[{i}:v]" for i in range(n))
    ass_escaped = str(ass_path).replace("\\", "\\\\").replace(":", "\\:")
    filter_complex = (
        f"{concat_in}concat=n={n}:v=1:a=0[bg];"
        f"[bg]drawbox=x=0:y=0:w={WIDTH}:h={HEIGHT}:color=0x{ACCENT}@1.0:t=fill:"
        f"enable='lte(t,0.08)'[bgf];"
        f"[bgf]ass='{ass_escaped}'[outv]"
    )
    cmd = [
        _ffmpeg(),
        "-y",
        *inputs,
        "-filter_complex",
        filter_complex,
        "-map",
        "[outv]",
        "-r",
        str(FPS),
        "-t",
        str(TOTAL_DURATION_S),
        "-c:v",
        "libx264",
        "-preset",
        _mb_ffmpeg_preset(),
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(out_path),
    ]
    _run(cmd, "typed silent render")


def synth_wav(path: Path, filter_str: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [_ffmpeg(), "-y", "-f", "lavfi", "-i", filter_str, "-ac", "2", "-ar", "44100", str(path)]
    _run(cmd, f"synth {path.name}")
    return path


def make_bed(path: Path, duration_s: float) -> Path:
    return synth_wav(
        path,
        (
            f"anoisesrc=color=brown:amplitude=0.014:duration={duration_s}"
            f"[n];sine=frequency=196:duration={duration_s}:sample_rate=44100[s];"
            "[s]volume=0.028,afade=t=in:st=0:d=1.2,afade=t=out:st="
            f"{duration_s - 2.2}:d=2.2[sf];[n]lowpass=f=700,volume=0.34[nf];"
            f"[nf][sf]amix=inputs=2:duration=first:dropout_transition=0,"
            f"afade=t=in:st=0:d=0.6,afade=t=out:st={duration_s - 2.0}:d=2.0"
        ),
    )


def make_hit(path: Path) -> Path:
    return synth_wav(
        path,
        "sine=frequency=150:duration=0.22:sample_rate=44100,"
        "afade=t=in:st=0:d=0.004,afade=t=out:st=0.02:d=0.19:curve=exp,volume=0.9",
    )


def make_tick(path: Path) -> Path:
    return synth_wav(
        path,
        "sine=frequency=2400:duration=0.05:sample_rate=44100,"
        "afade=t=in:st=0:d=0.002,afade=t=out:st=0.008:d=0.04:curve=exp,volume=0.55",
    )


def make_click(path: Path) -> Path:
    return synth_wav(
        path,
        "sine=frequency=620:duration=0.1:sample_rate=44100,"
        "afade=t=in:st=0:d=0.002,afade=t=out:st=0.02:d=0.08:curve=exp,volume=0.6",
    )


def make_chime(path: Path) -> Path:
    return synth_wav(
        path,
        "sine=frequency=440:duration=1.3:sample_rate=44100[a];"
        "sine=frequency=659.25:duration=1.1:sample_rate=44100[b];"
        "[a]afade=t=out:st=0.25:d=1.0:curve=exp,volume=0.5[af];"
        "[b]adelay=70|70,afade=t=out:st=0.3:d=0.9:curve=exp,volume=0.42[bf];"
        "[af][bf]amix=inputs=2:duration=longest,aecho=0.5:0.3:60:0.15",
    )


def build_master_audio(cues: dict, work_dir: Path, out_path: Path) -> Path:
    bed = make_bed(work_dir / "bed.wav", TOTAL_DURATION_S)
    hit = make_hit(work_dir / "hit.wav")
    tick = make_tick(work_dir / "tick.wav")
    click = make_click(work_dir / "click.wav")
    chime = make_chime(work_dir / "chime.wav")

    ticks_ms = [int(round(t * 1000)) for t in cues["mechanism_ticks_s"]]
    while len(ticks_ms) < 3:
        ticks_ms.append(ticks_ms[-1] if ticks_ms else 6000)
    hit_ms = int(round(cues["hook_hit_s"] * 1000))
    click_ms = int(round(cues["practice_click_s"] * 1000))
    chime_ms = int(round(cues["payoff_chime_s"] * 1000))

    filter_complex = (
        f"[1]adelay={hit_ms}|{hit_ms}[hitd];"
        f"[2]asplit=3[t0][t1][t2];"
        f"[t0]adelay={ticks_ms[0]}|{ticks_ms[0]}[tick0];"
        f"[t1]adelay={ticks_ms[1]}|{ticks_ms[1]}[tick1];"
        f"[t2]adelay={ticks_ms[2]}|{ticks_ms[2]}[tick2];"
        f"[3]adelay={click_ms}|{click_ms}[clickd];"
        f"[4]adelay={chime_ms}|{chime_ms}[chimed];"
        "[0][hitd][tick0][tick1][tick2][clickd][chimed]"
        "amix=inputs=7:duration=first:dropout_transition=0,alimiter=limit=0.95"
    )
    cmd = [
        _ffmpeg(),
        "-y",
        "-i",
        str(bed),
        "-i",
        str(hit),
        "-i",
        str(tick),
        "-i",
        str(click),
        "-i",
        str(chime),
        "-filter_complex",
        filter_complex,
        "-t",
        str(TOTAL_DURATION_S),
        "-ac",
        "2",
        "-ar",
        "44100",
        str(out_path),
    ]
    _run(cmd, "master audio mix")
    return out_path


def mux(video: Path, audio: Path, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        _ffmpeg(),
        "-y",
        "-i",
        str(video),
        "-i",
        str(audio),
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-shortest",
        "-movflags",
        "+faststart",
        str(out_path),
    ]
    _run(cmd, "mux")


def validate_mp4(path: Path) -> dict:
    probe = subprocess.run(
        [
            _ffprobe(),
            "-v",
            "error",
            "-show_entries",
            "stream=codec_type,codec_name,width,height,duration",
            "-of",
            "json",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(probe.stdout)
    streams = data.get("streams") or []
    video = next((s for s in streams if s.get("codec_type") == "video"), {})
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
    decode = subprocess.run(
        [_ffmpeg(), "-v", "error", "-i", str(path), "-f", "null", "-"],
        capture_output=True,
        text=True,
    )
    dur = float(video.get("duration") or 0)
    return {
        "path": str(path.relative_to(REPO)) if path.is_relative_to(REPO) else str(path),
        "width": video.get("width"),
        "height": video.get("height"),
        "duration_s": round(dur, 2),
        "has_audio": audio is not None,
        "audio_codec": (audio or {}).get("codec_name"),
        "full_decode_ok": decode.returncode == 0 and not decode.stderr.strip(),
        "duration_gate": 21.0 <= dur <= 27.5,
        "platform_contract": video.get("width") == WIDTH and video.get("height") == HEIGHT,
    }


def resolve_beats(item: dict) -> list[dict]:
    beats = []
    for role, (start, end), src in zip(ROLE_ORDER, BEAT_TIMES, item["beats"]):
        assert src["role"] == role, f"role order mismatch: {src['role']} != {role}"
        beats.append({"role": role, "text": src["caption"].strip(), "start": start, "end": end})
    return beats


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="", help="comma-separated example_ids; default=all")
    ap.add_argument("--out", type=Path, default=OUT_ROOT)
    args = ap.parse_args()

    items = json.loads(STORYBOARDS.read_text(encoding="utf-8"))
    wanted = {"tt_anxiety_faceless", "tt_burnout_faceless", "yt_overthinking_faceless"}
    items = [i for i in items if i["example_id"] in wanted]
    only = {x.strip() for x in args.only.split(",") if x.strip()}
    if only:
        items = [i for i in items if i["example_id"] in only]

    work_root = args.out / "_work"
    final_dir = args.out / "final"
    final_dir.mkdir(parents=True, exist_ok=True)

    receipts = []
    for item in items:
        example_id = item["example_id"]
        print(f"== {example_id} ==")
        beats = resolve_beats(item)
        wd = work_root / example_id
        wd.mkdir(parents=True, exist_ok=True)

        ass_path = wd / "captions.ass"
        cues = build_ass(beats, ass_path)

        silent = wd / "typed_silent.mp4"
        build_typed_silent(beats, ass_path, silent)

        audio = wd / "master_audio.wav"
        build_master_audio(cues, wd, audio)

        final = final_dir / f"{example_id}.mp4"
        mux(silent, audio, final)

        receipt = validate_mp4(final)
        receipt.update(
            {
                "example_id": example_id,
                "topic": item.get("topic"),
                "persona": item.get("persona"),
                "platform": item.get("platform"),
                "beat_count": len(beats),
                "render_mode": "kinetic_type_ass_plates",
                "look_variant": "A_kinetic_type",
                "viewer_captions_only": True,
                "faceless": True,
                "acceptance_layer": "system working — kinetic-type cut pending operator look",
            }
        )
        receipts.append(receipt)
        print(json.dumps(receipt, indent=2))

    (args.out / "validation_receipts.jsonl").write_text(
        "\n".join(json.dumps(r, sort_keys=True) for r in receipts) + "\n",
        encoding="utf-8",
    )
    failed = [
        r
        for r in receipts
        if not (r["full_decode_ok"] and r["duration_gate"] and r["platform_contract"] and r["has_audio"])
    ]
    if failed:
        print(f"FAIL: {len(failed)} receipts failed gates", file=sys.stderr)
        return 1
    print(f"OK: {len(receipts)} kinetic-type MP4s -> {final_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
