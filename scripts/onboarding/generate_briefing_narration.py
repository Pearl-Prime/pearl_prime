#!/usr/bin/env python3
"""
Generate brand briefing narration: cumulative VoiceProfile, SSML export, ElevenLabs MP3 (male + female).
Authority: specs/BRAND_ADMIN_ONBOARDING_TTS_SPEC.md

Usage:
  PYTHONPATH=. python3 scripts/onboarding/generate_briefing_narration.py [--dry-run]
Requires PyYAML for config. API key from ELEVENLABS_API_KEY; voice ids from env or YAML.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
import xml.sax.saxutils as saxutils
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CONFIG_YAML = ROOT / "config" / "onboarding" / "tts" / "ahjan_elevenlabs.yaml"
FIXTURE_JSON = ROOT / "config" / "onboarding" / "tts" / "briefing_narration_fixture.json"
OUT_DIR = ROOT / "artifacts" / "onboarding_audio"
PUBLIC_AUDIO = ROOT / "brand-wizard-app" / "public" / "onboarding" / "audio"


def _load_repo_dotenv() -> None:
    """Load ROOT/.env into os.environ (does not override existing vars)."""
    path = ROOT / ".env"
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip("'").strip('"')
        if key and key not in os.environ:
            os.environ[key] = val


@dataclass
class VoiceProfile:
    stability: float = 0.45
    similarity_boost: float = 0.72
    style: float = 0.12
    use_speaker_boost: bool = True
    prosody_rate_percent: float = 100.0
    prosody_pitch_percent: float = 100.0
    break_after_ms: float = 400.0

    def clamp(self, clamps: dict[str, Any]) -> None:
        for key, (lo, hi) in clamps.items():
            if not hasattr(self, key):
                continue
            v = getattr(self, key)
            if isinstance(v, bool):
                continue
            setattr(self, key, max(lo, min(hi, float(v))))


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml  # type: ignore
    except ImportError as e:
        raise SystemExit("PyYAML is required: pip install pyyaml") from e
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _resolve_voice_id(cfg: dict[str, Any], gender: str) -> str:
    voices = cfg.get("voices") or {}
    key = "male_id" if gender == "male" else "female_id"
    env_key = voices.get(f"{gender}_id_env") or f"ELEVENLABS_VOICE_ID_{gender.upper()}"
    from_env = os.environ.get(str(env_key), "").strip()
    if from_env:
        return from_env
    inline = str(voices.get(key) or "").strip()
    if inline:
        return inline
    return ""


def _apply_mapping_delta(profile: VoiceProfile, delta: dict[str, Any]) -> None:
    for k, v in delta.items():
        if not hasattr(profile, k):
            continue
        cur = getattr(profile, k)
        if isinstance(cur, bool) and isinstance(v, bool):
            setattr(profile, k, v)
        elif isinstance(cur, bool):
            continue
        else:
            setattr(profile, k, float(cur) + float(v))


def _apply_slider_deltas(
    profile: VoiceProfile,
    sliders: dict[str, Any],
    slider_cfg: dict[str, Any],
) -> None:
    center = 50.0
    for sid, raw in sliders.items():
        block = slider_cfg.get(sid)
        if not isinstance(block, dict):
            continue
        try:
            val = float(raw)
        except (TypeError, ValueError):
            continue
        dev = val - center
        for key, mult in block.items():
            if not key.endswith("_per_unit"):
                continue
            base = key[: -len("_per_unit")]
            if not hasattr(profile, base):
                continue
            cur = getattr(profile, base)
            if isinstance(cur, bool):
                continue
            setattr(profile, base, float(cur) + float(dev) * float(mult))


def _voice_settings_for_api(profile: VoiceProfile) -> dict[str, Any]:
    return {
        "stability": round(profile.stability, 4),
        "similarity_boost": round(profile.similarity_boost, 4),
        "style": round(profile.style, 4),
        "use_speaker_boost": bool(profile.use_speaker_boost),
    }


def _build_ssml_segment(text: str, profile: VoiceProfile) -> str:
    esc = saxutils.escape(text.strip())
    rate = profile.prosody_rate_percent - 100.0
    pitch = profile.prosody_pitch_percent - 100.0
    rate_s = f"{rate:+.1f}%"
    pitch_s = f"{pitch:+.1f}%"
    br = int(max(0, profile.break_after_ms))
    return (
        f'<prosody rate="{rate_s}" pitch="{pitch_s}">{esc}</prosody>'
        f'<break time="{br}ms"/>'
    )


def _plain_segment(text: str, break_ms: int) -> str:
    return text.strip() + ("\n\n" if break_ms else "")


def _concat_mp3_ffmpeg(part_paths: list[Path], out_path: Path) -> bool:
    if not part_paths or not shutil.which("ffmpeg"):
        return False
    lst = out_path.parent / "_ffmpeg_concat_list.txt"
    lines = [f"file '{p.resolve()}'" for p in part_paths]
    lst.write_text("\n".join(lines), encoding="utf-8")
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(lst),
                "-c",
                "copy",
                str(out_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def _say_segment_to_mp3_macos(*, text: str, out_mp3: Path, voice: str) -> None:
    """Offline demo: macOS `say` + ffmpeg → MP3 (no ElevenLabs)."""
    if not shutil.which("say"):
        raise RuntimeError("macOS `say` not found; use ElevenLabs or run on macOS.")
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg required for offline demo MP3 encoding.")
    aiff = out_mp3.with_suffix(".aiff")
    subprocess.run(["say", "-v", voice, "-o", str(aiff), text], check=True)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(aiff),
            "-codec:a",
            "libmp3lame",
            "-qscale:a",
            "4",
            str(out_mp3),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    aiff.unlink(missing_ok=True)


def _publish_to_public_audio() -> None:
    """Copy merged briefing MP3s to brand-wizard-app/public/onboarding/audio/ for Pages."""
    PUBLIC_AUDIO.mkdir(parents=True, exist_ok=True)
    for name in ("briefing_ahjan_male.mp3", "briefing_ahjan_female.mp3"):
        src = OUT_DIR / name
        if not src.is_file():
            continue
        dest = PUBLIC_AUDIO / name
        shutil.copy2(src, dest)
        print(f"Published {dest}")


def synthesize_elevenlabs(
    *,
    api_key: str,
    voice_id: str,
    text: str,
    model_id: str,
    voice_settings: dict[str, Any],
) -> bytes:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    body = json.dumps(
        {
            "text": text,
            "model_id": model_id,
            "voice_settings": voice_settings,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"ElevenLabs HTTP {e.code}: {err}") from e


def run(*, dry_run: bool, offline_demo: bool, publish_public: bool) -> int:
    cfg = _load_yaml(CONFIG_YAML)
    fixture = json.loads(FIXTURE_JSON.read_text(encoding="utf-8"))
    steps = fixture.get("steps")
    if not isinstance(steps, list) or not steps:
        print("Fixture missing steps[]", file=sys.stderr)
        return 1

    base = cfg.get("base_profile") or {}
    clamps = cfg.get("clamps") or {}
    slider_deltas = cfg.get("slider_deltas") or {}
    cat_delta = cfg.get("category_baseline_delta") or {}
    model_id = str(cfg.get("elevenlabs_model_id") or "eleven_multilingual_v2")

    profile = VoiceProfile(
        stability=float(base.get("stability", 0.45)),
        similarity_boost=float(base.get("similarity_boost", 0.72)),
        style=float(base.get("style", 0.12)),
        use_speaker_boost=bool(base.get("use_speaker_boost", True)),
        prosody_rate_percent=float(base.get("prosody_rate_percent", 100.0)),
        prosody_pitch_percent=float(base.get("prosody_pitch_percent", 100.0)),
        break_after_ms=float(base.get("break_after_ms", 400.0)),
    )

    ssml_parts: list[str] = ['<?xml version="1.0" encoding="UTF-8"?>', "<speak>"]
    segment_profiles: list[dict[str, Any]] = []
    # Per-step narration + VoiceProfile after cumulative deltas (for SSML + per-segment TTS).
    tts_segments: list[tuple[str, VoiceProfile]] = []

    for step in steps:
        if not isinstance(step, dict):
            continue
        cat = str(step.get("category") or "")
        if cat in cat_delta and isinstance(cat_delta[cat], dict):
            _apply_mapping_delta(profile, cat_delta[cat])
        step_delta = step.get("delta")
        if isinstance(step_delta, dict):
            _apply_mapping_delta(profile, step_delta)
        sliders = step.get("sliders")
        if isinstance(sliders, dict):
            _apply_slider_deltas(profile, sliders, slider_deltas)
        profile.clamp(clamps)

        text = str(step.get("narration_text") or "").strip()
        if not text:
            continue
        ssml_parts.append(_build_ssml_segment(text, profile))
        segment_profiles.append({"step_id": step.get("id"), "profile": asdict(profile)})
        # Snapshot profile after this step for ElevenLabs voice_settings on this segment only.
        tts_segments.append(
            (text, VoiceProfile(**asdict(profile))),
        )

    ssml_parts.append("</speak>")
    full_ssml = "".join(ssml_parts)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "briefing_ssml.xml").write_text(full_ssml, encoding="utf-8")
    (OUT_DIR / "briefing_segment_profiles.json").write_text(
        json.dumps(segment_profiles, indent=2),
        encoding="utf-8",
    )
    (OUT_DIR / "briefing_voice_profile.json").write_text(
        json.dumps(asdict(profile), indent=2),
        encoding="utf-8",
    )
    print(f"Wrote {OUT_DIR / 'briefing_ssml.xml'}")
    print(f"Wrote {OUT_DIR / 'briefing_voice_profile.json'} (final cumulative profile)")

    if dry_run:
        print("Dry-run: skipping audio synthesis.")
        return 0

    api_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    use_eleven = bool(api_key) and not offline_demo

    if offline_demo:
        print("Offline demo: using macOS `say` + ffmpeg (not ElevenLabs).", file=sys.stderr)
    elif not api_key:
        print(
            "ELEVENLABS_API_KEY not set; only SSML/profile written. "
            "Set key + voice ids, or pass --offline-demo on macOS.",
            file=sys.stderr,
        )
        return 0

    male_id = _resolve_voice_id(cfg, "male")
    female_id = _resolve_voice_id(cfg, "female")
    if use_eleven and (not male_id or not female_id):
        print(
            "Set ELEVENLABS_VOICE_ID_MALE and ELEVENLABS_VOICE_ID_FEMALE (or voices.male_id/female_id in YAML).",
            file=sys.stderr,
        )
        return 1

    seg_dir = OUT_DIR / "segments"
    seg_dir.mkdir(parents=True, exist_ok=True)

    # Offline: built-in macOS voices (Ahjan-aligned timbre is ElevenLabs-only).
    offline_voices = (cfg.get("offline_demo_voices") or {})
    say_male = str(offline_voices.get("say_male") or "Daniel")
    say_female = str(offline_voices.get("say_female") or "Samantha")

    def render_gender_eleven(voice_id: str, prefix: str) -> None:
        part_paths: list[Path] = []
        for i, (raw_text, prof) in enumerate(tts_segments, start=1):
            vs = _voice_settings_for_api(prof)
            inner = _build_ssml_segment(raw_text, prof)
            chunk = f'<?xml version="1.0" encoding="UTF-8"?><speak>{inner}</speak>'
            part = seg_dir / f"{prefix}_{i:02d}.mp3"
            try:
                audio = synthesize_elevenlabs(
                    api_key=api_key,
                    voice_id=voice_id,
                    text=chunk,
                    model_id=model_id,
                    voice_settings=vs,
                )
            except RuntimeError:
                audio = synthesize_elevenlabs(
                    api_key=api_key,
                    voice_id=voice_id,
                    text=_plain_segment(raw_text, int(prof.break_after_ms)),
                    model_id=model_id,
                    voice_settings=vs,
                )
            part.write_bytes(audio)
            part_paths.append(part)
        out_full = OUT_DIR / f"briefing_{prefix}.mp3"
        if _concat_mp3_ffmpeg(part_paths, out_full):
            print(f"Wrote {out_full} ({len(part_paths)} segments via ffmpeg)")
        else:
            print(
                f"Wrote {len(part_paths)} segment files under {seg_dir}/ ({prefix}_NN.mp3). "
                f"Install ffmpeg and re-run to emit {out_full.name}, or concat manually.",
                file=sys.stderr,
            )

    def render_gender_say(say_voice: str, prefix: str) -> None:
        part_paths: list[Path] = []
        for i, (raw_text, _prof) in enumerate(tts_segments, start=1):
            part = seg_dir / f"{prefix}_{i:02d}.mp3"
            _say_segment_to_mp3_macos(text=raw_text, out_mp3=part, voice=say_voice)
            part_paths.append(part)
        out_full = OUT_DIR / f"briefing_{prefix}.mp3"
        if _concat_mp3_ffmpeg(part_paths, out_full):
            print(f"Wrote {out_full} ({len(part_paths)} segments via ffmpeg, offline demo)")
        else:
            print(f"ffmpeg concat failed for {prefix}; segments in {seg_dir}/", file=sys.stderr)

    if use_eleven:
        render_gender_eleven(male_id, "ahjan_male")
        render_gender_eleven(female_id, "ahjan_female")
    else:
        render_gender_say(say_male, "ahjan_male")
        render_gender_say(say_female, "ahjan_female")

    if publish_public:
        _publish_to_public_audio()

    return 0


def main() -> int:
    _load_repo_dotenv()
    ap = argparse.ArgumentParser(description="Brand briefing TTS (Ahjan / ElevenLabs)")
    ap.add_argument("--dry-run", action="store_true", help="SSML + JSON only, no API calls")
    ap.add_argument(
        "--offline-demo",
        action="store_true",
        help="macOS only: synthesize with `say`+ffmpeg instead of ElevenLabs (demo timbre).",
    )
    ap.add_argument(
        "--publish-public",
        action="store_true",
        help="After synthesis, copy merged MP3s to brand-wizard-app/public/onboarding/audio/",
    )
    args = ap.parse_args()
    if args.dry_run and args.offline_demo:
        print("Use only one of --dry-run or --offline-demo.", file=sys.stderr)
        return 1
    return run(
        dry_run=bool(args.dry_run),
        offline_demo=bool(args.offline_demo),
        publish_public=bool(args.publish_public),
    )


if __name__ == "__main__":
    raise SystemExit(main())
