#!/usr/bin/env python3
"""Pearl Practice — Transform exercise atoms into guided therapeutic audio.

Parses exercise atoms, adds pause markup + pointer phrases, generates
ElevenLabs TTS per section, applies post-production (slow, EQ, reverb),
mixes with ambient music, outputs final therapeutic practice MP3.

Usage:
    python3 scripts/pearl_practice/run_practice.py \
        --persona healthcare_rns --topic grief --variant 1 \
        -o ~/Desktop/grief_practice_v01.mp3 \
        [--ambient] [--binaural]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

try:
    import yaml
    import requests
except ImportError as e:
    print(f"Missing dependency: {e}", file=sys.stderr)
    sys.exit(1)


# ── Config loaders ──────────────────────────────────────────────────

def _load_yaml(rel: str) -> dict:
    p = REPO_ROOT / rel
    if not p.is_file():
        return {}
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def _load_pacing(topic: str) -> dict:
    cfg = _load_yaml("config/pearl_practice/pacing_profiles.yaml")
    profiles = cfg.get("profiles", {})
    return profiles.get(topic, profiles.get("default", {}))


def _load_pointers() -> dict:
    return _load_yaml("config/pearl_practice/pointer_phrases.yaml")


def _load_emotional_keywords() -> list[str]:
    cfg = _load_yaml("config/pearl_practice/pacing_profiles.yaml")
    return cfg.get("emotional_keywords", [])


# ── Step 1: Parse atom ──────────────────────────────────────────────

def parse_exercise(persona: str, topic: str, variant: int) -> dict:
    """Parse one exercise variant from CANONICAL.txt."""
    path = REPO_ROOT / "atoms" / persona / topic / "EXERCISE" / "CANONICAL.txt"
    if not path.is_file():
        raise FileNotFoundError(f"Exercise not found: {path}")

    text = path.read_text(encoding="utf-8")
    # Split by ## EXERCISE vXX markers
    blocks = re.split(r"## EXERCISE v\d+\s*\n-+\s*\n\s*-+\s*\n", text)
    blocks = [b.strip().strip("-").strip() for b in blocks if b.strip().strip("-").strip()]

    if variant < 1 or variant > len(blocks):
        raise ValueError(f"Variant {variant} not found (have {len(blocks)})")

    raw = blocks[variant - 1].strip()
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", raw) if s.strip()]

    # Auto-detect exercise type
    text_lower = raw.lower()
    if any(w in text_lower for w in ["breathe", "breath", "inhale", "exhale"]):
        ex_type = "breathing"
    elif any(w in text_lower for w in ["feet", "floor", "ground", "pressure", "solid"]):
        ex_type = "grounding"
    elif any(w in text_lower for w in ["body", "chest", "hands", "tension", "sensation"]):
        ex_type = "body_awareness"
    elif any(w in text_lower for w in ["grief", "cry", "tears", "loss", "pain"]):
        ex_type = "emotional_processing"
    else:
        ex_type = "general"

    word_count = len(raw.split())
    return {
        "persona": persona,
        "topic": topic,
        "variant": variant,
        "raw_text": raw,
        "sentences": sentences,
        "word_count": word_count,
        "exercise_type": ex_type,
        "duration_estimate_s": round(word_count / 80 * 60, 1),
    }


# ── Step 2: Generate marked-up script ───────────────────────────────

def _is_emotional(sentence: str, keywords: list[str]) -> bool:
    s = sentence.lower()
    return any(kw in s for kw in keywords)


def _pick_pointer(category: str, pointers: dict, seed: int) -> str:
    phrases = pointers.get(category, pointers.get("processing", ["Take a moment."]))
    return phrases[seed % len(phrases)]


def generate_markup(parsed: dict) -> dict:
    """Add opening, pointers, pauses, and closing to exercise."""
    topic = parsed["topic"]
    pacing = _load_pacing(topic)
    pointers = _load_pointers()
    emo_keywords = _load_emotional_keywords()

    sections: list[dict] = []
    seed = int(hashlib.sha256(f"{parsed['persona']}:{topic}:{parsed['variant']}".encode()).hexdigest()[:8], 16)

    # Opening
    opener = _pick_pointer("opening", pointers, seed)
    sections.append({"type": "opening", "role": "pointer", "text": opener, "pause_after_s": pacing.get("opening_pause_s", 6)})
    sections.append({"type": "setup", "role": "pointer", "text": "Take a slow breath in. And let it go.", "pause_after_s": pacing.get("opening_pause_s", 6)})

    # Instructions with pauses and pointers
    pointer_freq = pacing.get("pointer_every_n_sentences", 4)
    topic_pointers = pointers.get(f"{topic}_specific", pointers.get("processing", []))

    # Run intonation planner on all sentences
    from scripts.pearl_practice.intonation_planner import plan_exercise_intonation
    intonation_plan = plan_exercise_intonation(parsed["sentences"], topic)

    for i, (sentence, into) in enumerate(zip(parsed["sentences"], intonation_plan)):
        emotional = _is_emotional(sentence, emo_keywords)
        pause = pacing.get("processing_pause_s", 8) if emotional else pacing.get("standard_pause_s", 4)
        # Use the intonation-rewritten text instead of raw
        sections.append({"type": "instruction", "role": "guide", "text": into["rewritten"], "pause_after_s": pause})

        # Insert pointer phrase every N sentences
        if (i + 1) % pointer_freq == 0 and i < len(parsed["sentences"]) - 1:
            ptr = _pick_pointer(f"{topic}_specific" if topic_pointers else "processing", pointers, seed + i)
            sections.append({"type": "pointer", "role": "pointer", "text": ptr, "pause_after_s": pacing.get("micro_pause_s", 2)})

    # Closing
    closer = _pick_pointer("completion", pointers, seed + 100)
    sections.append({"type": "close", "role": "pointer", "text": closer, "pause_after_s": pacing.get("closing_pause_s", 4)})
    closer2 = _pick_pointer("completion", pointers, seed + 101)
    if closer2 != closer:
        sections.append({"type": "close", "role": "pointer", "text": closer2, "pause_after_s": 3})

    # Calculate totals
    total_silence = sum(s["pause_after_s"] for s in sections)
    est_speech = sum(len(s["text"].split()) / 80 * 60 for s in sections)

    return {
        "persona": parsed["persona"],
        "topic": parsed["topic"],
        "variant": parsed["variant"],
        "exercise_type": parsed["exercise_type"],
        "sections": sections,
        "total_speech_estimate_s": round(est_speech, 1),
        "total_silence_s": round(total_silence, 1),
        "total_duration_estimate_s": round(est_speech + total_silence, 1),
        "speech_ratio": round(est_speech / max(1, est_speech + total_silence), 2),
        "pacing_profile": topic,
    }


# ── Step 3: Voice synthesis (ElevenLabs) ────────────────────────────

def _elevenlabs_tts(text: str, voice_id: str, api_key: str, settings: dict) -> bytes:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": settings.get("stability", 0.88),
            "similarity_boost": settings.get("similarity", 0.70),
            "style": settings.get("style", 0.05),
            "use_speaker_boost": False,
            "speed": settings.get("speed", 0.75),
        },
    }
    for attempt in range(3):
        try:
            resp = requests.post(url, json=data, headers={"xi-api-key": api_key, "Content-Type": "application/json"}, timeout=30)
            if resp.status_code == 200:
                return resp.content
            if resp.status_code == 429 or resp.status_code >= 500:
                time.sleep(2 * (attempt + 1))
                continue
            raise RuntimeError(f"ElevenLabs {resp.status_code}: {resp.text[:200]}")
        except (ConnectionError, OSError):
            time.sleep(2 * (attempt + 1))
    raise RuntimeError("ElevenLabs TTS failed after 3 retries")


def synthesize_sections(script: dict, api_key: str, work_dir: Path) -> list[Path]:
    """Generate one MP3 per section via ElevenLabs."""
    pacing = _load_pacing(script["topic"])
    voice_id = pacing.get("voice_id", "pjcYQlDFKMbcOUp6F5GD")
    base_speed = pacing.get("speed", 0.75)

    clips_dir = work_dir / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)
    paths = []

    total = len(script["sections"])
    for i, section in enumerate(script["sections"]):
        clip = clips_dir / f"s_{i:03d}.mp3"

        if clip.exists() and clip.stat().st_size > 500:
            paths.append(clip)
            continue

        # Pointer phrases: slower, more stable
        is_pointer = section["role"] == "pointer"
        settings = {
            "stability": pacing.get("voice_stability", 0.88) + (0.05 if is_pointer else 0),
            "similarity": pacing.get("voice_similarity", 0.70),
            "style": 0.01 if is_pointer else pacing.get("voice_style", 0.05),
            "speed": max(0.7, base_speed * 0.92) if is_pointer else base_speed,
        }

        audio = _elevenlabs_tts(section["text"], voice_id, api_key, settings)
        clip.write_bytes(audio)
        print(f"  [{i+1}/{total}] {section['type']:12s} {len(audio)//1024:4d}KB | {section['text'][:50]}", flush=True)
        paths.append(clip)
        time.sleep(0.5)

    return paths


# ── Step 4: Post-production (FFmpeg) ────────────────────────────────

def _ffmpeg(*args, timeout=30):
    cmd = [os.environ.get("FFMPEG_BIN", "ffmpeg"), "-y"] + list(args)
    # Try common paths
    for ff in [cmd[0], "/opt/homebrew/bin/ffmpeg", "/usr/local/bin/ffmpeg", "ffmpeg"]:
        try:
            cmd[0] = ff
            return subprocess.run(cmd, capture_output=True, timeout=timeout, check=True)
        except FileNotFoundError:
            continue
    raise RuntimeError("ffmpeg not found")


def _generate_silence(duration_s: float, out_path: Path):
    """Generate a silent MP3 of given duration."""
    _ffmpeg(
        "-f", "lavfi", "-i", f"anullsrc=channel_layout=mono:sample_rate=44100",
        "-t", str(round(duration_s, 2)),
        "-c:a", "libmp3lame", "-b:a", "64k",
        str(out_path),
    )


def post_produce(clips: list[Path], script: dict, out_path: Path, *, include_ambient: bool = True):
    """Assemble clips with silences, apply EQ/reverb, mix with ambient."""
    work_dir = clips[0].parent.parent
    assembled_dir = work_dir / "assembled"
    assembled_dir.mkdir(exist_ok=True)

    # Build concat list: clip + silence + clip + silence + ...
    concat_parts: list[Path] = []
    for i, (clip, section) in enumerate(zip(clips, script["sections"])):
        concat_parts.append(clip)
        pause_s = section["pause_after_s"]
        if pause_s > 0.5:
            silence = assembled_dir / f"silence_{i:03d}.mp3"
            _generate_silence(pause_s, silence)
            concat_parts.append(silence)

    # Write concat list
    list_file = work_dir / "concat.txt"
    with open(list_file, "w") as f:
        for p in concat_parts:
            f.write(f"file '{p}'\n")

    # Concat all parts
    raw_concat = work_dir / "concat_raw.mp3"
    _ffmpeg("-f", "concat", "-safe", "0", "-i", str(list_file),
            "-c:a", "libmp3lame", "-b:a", "192k", str(raw_concat), timeout=60)

    # Apply warm EQ + gentle reverb + compression
    processed = work_dir / "processed.mp3"
    _ffmpeg(
        "-i", str(raw_concat),
        "-af", (
            "equalizer=f=300:t=q:w=1:g=3,"        # Warmth boost
            "equalizer=f=3500:t=q:w=1:g=-4,"       # Cut harshness
            "equalizer=f=8000:t=q:w=1:g=-2,"       # Gentle high roll-off
            "aecho=0.8:0.7:40:0.25,"               # Subtle reverb
            "compand=attacks=0.3:decays=0.8:"       # Gentle compression
            "points=-80/-80|-45/-45|-27/-25|-15/-12:soft-knee=6"
        ),
        "-c:a", "libmp3lame", "-b:a", "192k",
        str(processed),
        timeout=30,
    )

    if not include_ambient:
        # Just copy processed to output
        import shutil
        shutil.copy2(processed, out_path)
        return

    # Mix with ambient music from music bank
    amb_src = REPO_ROOT / "assets" / "music_bank" / "generated" / "amb_001.mp3"
    if not amb_src.is_file():
        import shutil
        shutil.copy2(processed, out_path)
        print("  Warning: no ambient track found, outputting voice-only", flush=True)
        return

    # Get voice duration
    r = subprocess.run(
        [os.environ.get("FFMPEG_BIN", "/opt/homebrew/bin/ffprobe"), "-v", "quiet",
         "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
         str(processed)],
        capture_output=True, text=True, timeout=10,
    )
    dur = float(r.stdout.strip()) if r.returncode == 0 else 180

    # Loop ambient to match voice duration, very low volume
    ambient_looped = work_dir / "ambient_loop.mp3"
    loop_count = max(1, int(dur / 30) + 1)
    _ffmpeg(
        "-stream_loop", str(loop_count),
        "-i", str(amb_src),
        "-af", "volume=0.10,afade=t=in:st=0:d=5,afade=t=out:st=" + str(max(0, dur - 5)) + ":d=5",
        "-t", str(round(dur + 2, 1)),
        "-c:a", "libmp3lame", "-b:a", "128k",
        str(ambient_looped),
        timeout=30,
    )

    # Final mix: voice + ambient
    out_path.parent.mkdir(parents=True, exist_ok=True)
    _ffmpeg(
        "-i", str(processed),
        "-i", str(ambient_looped),
        "-filter_complex", "[0:a]volume=1.0[v];[1:a]volume=0.12[a];[v][a]amix=inputs=2:duration=first[out]",
        "-map", "[out]",
        "-c:a", "libmp3lame", "-b:a", "192k",
        str(out_path),
        timeout=30,
    )


# ── Main CLI ────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description="Pearl Practice — Guided therapeutic audio from exercise atoms")
    ap.add_argument("--persona", required=True, help="Persona ID (e.g. healthcare_rns)")
    ap.add_argument("--topic", required=True, help="Topic ID (e.g. grief)")
    ap.add_argument("--variant", type=int, default=1, help="Exercise variant (1-3)")
    ap.add_argument("-o", "--output", required=True, type=Path, help="Output MP3 path")
    ap.add_argument("--ambient", action="store_true", default=True, help="Include ambient music (default: yes)")
    ap.add_argument("--no-ambient", action="store_true", help="Voice only, no ambient")
    ap.add_argument("--work-dir", type=Path, default=None, help="Working directory for intermediate files")
    args = ap.parse_args()

    api_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not api_key:
        print("Error: ELEVENLABS_API_KEY not set", file=sys.stderr)
        return 1

    include_ambient = args.ambient and not args.no_ambient

    # Step 1: Parse
    print(f"=== Pearl Practice: {args.persona} / {args.topic} / v{args.variant} ===", flush=True)
    parsed = parse_exercise(args.persona, args.topic, args.variant)
    print(f"  Parsed: {parsed['word_count']} words, {len(parsed['sentences'])} sentences, type={parsed['exercise_type']}", flush=True)

    # Step 2: Markup
    script = generate_markup(parsed)
    print(f"  Markup: {len(script['sections'])} sections, speech={script['speech_ratio']:.0%}, "
          f"est duration={script['total_duration_estimate_s']:.0f}s ({script['total_duration_estimate_s']/60:.1f}min)", flush=True)

    # Save script for inspection
    work_dir = args.work_dir or Path(f"/tmp/pearl_practice/{args.persona}_{args.topic}_v{args.variant}")
    work_dir.mkdir(parents=True, exist_ok=True)
    (work_dir / "script.json").write_text(json.dumps(script, indent=2), encoding="utf-8")

    # Step 3: Voice synthesis
    print(f"\n  Synthesizing {len(script['sections'])} sections via ElevenLabs...", flush=True)
    clips = synthesize_sections(script, api_key, work_dir)
    print(f"  Generated {len(clips)} audio clips", flush=True)

    # Step 4: Post-production
    print(f"\n  Post-production...", flush=True)
    post_produce(clips, script, args.output, include_ambient=include_ambient)

    # Report
    if args.output.is_file():
        size_kb = args.output.stat().st_size // 1024
        try:
            r = subprocess.run(
                ["/opt/homebrew/bin/ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", str(args.output)],
                capture_output=True, text=True, timeout=10,
            )
            dur = float(r.stdout.strip())
        except Exception:
            dur = 0
        print(f"\n  Output: {args.output} ({size_kb}KB, {dur:.1f}s / {dur/60:.1f}min)", flush=True)
        print(f"  Speech ratio: {script['speech_ratio']:.0%} speech / {1-script['speech_ratio']:.0%} silence", flush=True)
    else:
        print(f"\n  ERROR: output not created", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
