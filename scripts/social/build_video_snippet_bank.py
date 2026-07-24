#!/usr/bin/env python3
"""CODE-WIRED builder for the Social Video Snippet Bank — Lane 03.

Reuses the 3 already-wired video-family renderers as the render engines
(REUSE-FIRST — this file does not implement a 4th video engine):

  - scripts/social/render_broll_montage_shorts.py   (family: broll_montage)
  - scripts/social/render_kinetic_type_shorts.py    (family: kinetic_type)
  - scripts/social/render_object_metaphor_shorts.py (family: object_metaphor)

Each renderer's own top-level functions are imported and called directly
(Ken Burns zoompan crop, progressive crop-window clip, libass kinetic type)
re-parameterized by (family, topic_native_family, beat_role, k_index, aspect)
instead of each renderer's own hardcoded 3-item pilot storyboard.

Authority: docs/specs/SOCIAL_VIDEO_SNIPPET_BANK_SPEC_2026-07-19.md
Sizing table: config/social/media_bank_sizing_20260719.yaml

Writes artifacts/social_media_video_bank_2026-07-19/MANIFEST.tsv.

Stub-guard (hard rule): any rendered file with bytes < STUB_GUARD_BYTES is
forced to render_status=stub in the manifest, regardless of what the render
step returned. There is no code path that writes render_status=ok for a
stub-sized file.
"""
from __future__ import annotations

import os as _os
def _mb_ffmpeg_preset() -> str:
    return _os.environ.get("MEDIA_BANK_FFMPEG_PRESET", "medium")

import argparse
import fcntl
import hashlib
import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import yaml

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.social import render_broll_montage_shorts as broll_mod  # noqa: E402
from scripts.social import render_kinetic_type_shorts as kinetic_mod  # noqa: E402
from scripts.social import render_object_metaphor_shorts as objmeta_mod  # noqa: E402
from scripts.social.semantic_asset_selector import select_from_topic_pool  # noqa: E402

FFMPEG = "/opt/homebrew/bin/ffmpeg"
FFPROBE = "/opt/homebrew/bin/ffprobe"

SIZING_YAML = REPO / "config/social/media_bank_sizing_20260719.yaml"
SPEC_DOC = REPO / "docs/specs/SOCIAL_VIDEO_SNIPPET_BANK_SPEC_2026-07-19.md"
STOCK_BASE = (
    REPO
    / "artifacts/stock_image_bank/way_stream_sanctuary/mental_health_editorial_100x"
    / "downloads/pexels"
)
# Licensed Storyblocks HD only — never a shared pool under stock_image_bank (EULA §B).
STORYBLOCKS_LICENSED_BASE = REPO / "artifacts/storyblocks_licensed"
# Set by main() from --stock-provider; render helpers read this.
STOCK_PROVIDER = "auto"

OUT_ROOT = REPO / "artifacts/social_media_video_bank_2026-07-19"
PILOTS_DIR = OUT_ROOT / "pilots"
WORK_ROOT = OUT_ROOT / "_work"
MANIFEST_PATH = OUT_ROOT / "MANIFEST.tsv"

WIDTH, HEIGHT, FPS = 1080, 1920, 30
STUB_GUARD_BYTES = 50_000
DURATION_TOLERANCE_S = 0.6

FAMILIES = ("broll_montage", "kinetic_type", "object_metaphor")

BEAT_ROLE_DURATIONS = {
    "hook": 3.0,
    "beat": 5.0,
    "value": 8.0,
    "endcard": 2.0,
}

# Lane 02 §5.1 pilot priority topics (native families with existing stock overlap).
PILOT_PRIORITY_TOPICS = [
    "anxiety",
    "boundaries",
    "burnout",
    "depression",
    "grief",
    "overthinking",
]

# scripts/social/render_kinetic_type_shorts.py role -> (BG_SPEC/TEXT_COLOR key, reveal grammar)
KINETIC_ROLE_MAP = {
    "hook": "hook",
    "beat": "recognition",
    "value": "mechanism",
    "endcard": "payoff",
}
KINETIC_PLACEHOLDER_TEXT = {
    "beat": "you're not imagining it",
    "value": "here's what's happening",
    "endcard": "there's a way through",
    # "hook" text is the topic label itself, computed per-call (§4.2 of the spec)
}

OBJECT_METAPHOR_CROP_SPEC = {
    "hook": {"height_frac": 1.00, "zoom_to": 1.03},
    "beat": {"height_frac": 0.55, "zoom_to": 1.05},
    "value": {"height_frac": 0.32, "zoom_to": 1.06},
    "endcard": {"height_frac": 0.60, "zoom_to": 1.02},
}
DEFAULT_SUBJECT_CENTER = (0.50, 0.45)

MOOD_FREQS = {
    "tense_anxious": (220.00, 261.63, 329.63),
    "heavy_low": (110.00, 130.81, 164.81),
    "grounding_somatic": (196.00, 246.94, 293.66),
    "empowering_courage": (261.63, 329.63, 392.00),
}

ASPECT_BUCKETS = {
    "VERTICAL_9_16": {"label": "9x16", "crop": None},
    "SQUARE_1_1": {"label": "1x1", "crop": {"w": 1080, "h": 1080}},
    "PORTRAIT_4_5": {"label": "4x5", "crop": {"w": 1080, "h": 1350}},
    "LANDSCAPE_WIDE": {"label": "16x9", "crop": {"w": 1080, "h": 608}, "scale": (1920, 1080)},
}

MANIFEST_COLUMNS = [
    "asset_id",
    "family",
    "topic_native_family",
    "beat_role",
    "k_index",
    "seed",
    "aspect_bucket",
    "width",
    "height",
    "fps",
    "duration_s_target",
    "duration_s_actual",
    "video_codec",
    "audio_codec",
    "has_audio",
    "bytes",
    "sha256_16",
    "mood_register",
    "source_stock_ref",
    "content_provenance",
    "license_status",
    "production_ready",
    "review_status",
    "render_status",
    "r2_key_planned",
    "r2_uploaded",
    "local_path",
    "generated_by",
    "generated_at",
    "keyword_score",
    "match_quality",
    "match_rationale",
]


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stderr.write(f"CMD FAILED: {' '.join(cmd)}\n{proc.stderr[-4000:]}\n")
        raise SystemExit(proc.returncode)
    return proc


def load_sizing() -> dict[str, Any]:
    return yaml.safe_load(SIZING_YAML.read_text(encoding="utf-8"))


def mood_register_for_topic(sizing: dict[str, Any], topic: str) -> str:
    clusters = sizing["audio_bank"]["mood_registers"]["clusters"]
    for register, topics in clusters.items():
        if topic in topics:
            return register
    raise SystemExit(f"topic {topic!r} not found in any mood_register cluster in {SIZING_YAML}")


def derive_seed(family: str, topic: str, beat_role: str, k_index: int) -> int:
    key = f"{family}|{topic}|{beat_role}|{k_index}"
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


# Native-family topics without a 1:1 pexels folder map onto nearest covered folders.
STOCK_TOPIC_ALIASES: dict[str, list[str]] = {
    "compassion_fatigue": ["burnout", "trauma"],
    "courage": ["hope"],
    "financial_anxiety": ["anxiety"],
    "financial_stress": ["anxiety", "anger"],
    "imposter_syndrome": ["self_worth"],
    "sleep_anxiety": ["anxiety"],
    "social_anxiety": ["loneliness"],
    "somatic_healing": ["healing"],
}


def _licensed_storyblocks_stills(topic: str) -> list[Path]:
    """Still plates from fill_social_bank BANK_INDEX, then work-unit dir heuristics."""
    pool: list[Path] = []
    seen: set[Path] = set()

    try:
        from scripts.storyblocks.fill_social_bank import plates_for_topic  # noqa: PLC0415

        for p in plates_for_topic(topic, media_type="image"):
            if p not in seen and p.is_file():
                seen.add(p)
                pool.append(p)
    except Exception:  # noqa: BLE001 — index optional
        pass

    folder_names = set(STOCK_TOPIC_ALIASES.get(topic, [topic]) + [topic])
    if not STORYBLOCKS_LICENSED_BASE.is_dir():
        return pool
    for wu_dir in sorted(STORYBLOCKS_LICENSED_BASE.iterdir()):
        if not wu_dir.is_dir():
            continue
        name = wu_dir.name.lower()
        if not any(f.replace("_", "") in name.replace("_", "") or f in name for f in folder_names):
            # Accept exact work-unit dirs like social_broll:anxiety (colon→safe)
            if not any(f in name for f in folder_names):
                continue
        # Still plates only — Ken Burns / object-metaphor renderers expect images.
        # Licensed .mp4/.mov stay in the work-unit bank for direct-clip consumers.
        for pattern in ("*.jpeg", "*.jpg", "*.png", "*.webp"):
            for p in sorted(wu_dir.glob(pattern)):
                if p not in seen:
                    seen.add(p)
                    pool.append(p)
    return pool


def stock_pool(topic: str, *, provider: str = "auto") -> list[Path]:
    """Return still/video plates for topic.

    provider:
      - pexels: legacy editorial 100x stills only
      - storyblocks: licensed work-unit bank only (confirm_selection path)
      - auto: storyblocks licensed first, then pexels fill
    """
    folder_names = STOCK_TOPIC_ALIASES.get(topic, [topic])
    pool: list[Path] = []
    seen: set[Path] = set()
    provider = (provider or "auto").lower()

    def _add(paths: list[Path]) -> None:
        for p in paths:
            if p in seen:
                continue
            seen.add(p)
            pool.append(p)

    if provider in {"storyblocks", "auto"}:
        _add(_licensed_storyblocks_stills(topic))

    if provider in {"pexels", "auto"}:
        for folder in folder_names:
            topic_dir = STOCK_BASE / folder
            if not topic_dir.is_dir():
                continue
            _add(sorted(topic_dir.glob("*.jpeg")) + sorted(topic_dir.glob("*.jpg")))

    if not pool:
        raise SystemExit(
            f"No stock plates for topic={topic!r} provider={provider!r} "
            f"(tried folders={folder_names} under {STOCK_BASE} and {STORYBLOCKS_LICENSED_BASE}). "
            "For Storyblocks: python3 scripts/storyblocks/fill_social_bank.py "
            "--topics <topic> --media image. See docs/STORYBLOCKS_SOCIAL_BANK.md."
        )
    return pool



_DEFAULT_BEAT_CAPTIONS = {
    ("anxiety", "hook"): "anxious phone racing thoughts in a crowded commute",
    ("anxiety", "beat"): "tense worried hands clutching chest near traffic crowd",
    ("anxiety", "value"): "one breath with phone down at a quiet desk",
    ("anxiety", "endcard"): "calm pause after naming the anxious signal",
    ("social_anxiety", "hook"): "nervous in a crowded room full of people avoiding eye contact",
    ("social_anxiety", "beat"): "shy awkward pause in a hallway elevator public space",
    ("social_anxiety", "value"): "one small step out of the waiting room crowd",
    ("social_anxiety", "endcard"): "you can leave the crowded room without apology",
    ("burnout", "hook"): "exhausted at a laptop desk late night coffee drained",
    ("burnout", "beat"): "tired head in hands at office laptop overworked",
    ("burnout", "value"): "step away from the cluttered desk and empty coffee cup",
    ("burnout", "endcard"): "rest is part of the work not a failure",
    ("boundaries", "hook"): "assertive pause at a doorway before a hard conversation",
    ("boundaries", "beat"): "serious discussion meeting room colleagues listening",
    ("boundaries", "value"): "a clear no at the meeting doorway calendar boundary",
    ("boundaries", "endcard"): "your boundary can stay kind and firm",
    ("depression", "hook"): "lonely quiet rain on the window empty room",
    ("depression", "beat"): "withdrawn morning by the window bed grey light",
    ("depression", "value"): "one small move from the bed toward the window light",
    ("depression", "endcard"): "slow mornings still count as progress",
    ("grief", "hook"): "quiet sadness empty chair candle remembrance",
    ("grief", "beat"): "mourning with a photo frame and empty chair at the table",
    ("grief", "value"): "a candle and fallen leaves marking remembrance",
    ("grief", "endcard"): "grief can sit beside you without rushing",
    ("overthinking", "hook"): "restless night thoughts spiral clock notebook",
    ("overthinking", "beat"): "sticky notes maze of decisions phone screen worry",
    ("overthinking", "value"): "one notebook line instead of another spiral",
    ("overthinking", "endcard"): "you do not have to solve the maze tonight",
}


def default_caption_for(topic: str, beat_role: str) -> str:
    if (topic, beat_role) in _DEFAULT_BEAT_CAPTIONS:
        return _DEFAULT_BEAT_CAPTIONS[(topic, beat_role)]
    return f"{topic.replace('_', ' ')} {beat_role} everyday adult indoor"


def pick_stock_image(topic: str, beat_role: str, seed: int, pool: list[Path], caption: str | None = None) -> dict[str, Any]:
    """CTQC keyword pick — never silent seed-modulo pool indexing."""
    result = select_from_topic_pool(
        topic,
        pool,
        caption=caption or default_caption_for(topic, beat_role),
        beat_role=beat_role,
        seed=seed,
    )
    return {
        "path": result.path,
        "keyword_score": result.keyword_score,
        "match_quality": result.match_quality,
        "match_rationale": result.match_rationale,
    }


def assert_broll_stock_licensed(img: Path, *, work_unit_id: str | None = None) -> None:
    """EULA §A: Storyblocks preview/unlicensed paths cannot enter social b-roll render.

    Legacy Pexels/Pixabay plates under stock_image_bank pass through. Storyblocks
    assets require a license download record (scripts/storyblocks/consumer_guard.py).
    """
    from scripts.storyblocks.consumer_guard import (  # noqa: PLC0415
        UnlicensedStoryblocksAssetError,
        assert_storyblocks_licensed_for_consumer,
    )

    asset = {
        "path": str(img),
        "source_stock_ref": str(img),
        "source_provider": "storyblocks" if "storyblocks" in str(img).lower() else "pexels",
        "work_unit_id": work_unit_id,
        "storyblocks_stock_id": img.stem if "storyblocks" in str(img).lower() else "",
    }
    try:
        assert_storyblocks_licensed_for_consumer(asset, work_unit_id=work_unit_id)
    except UnlicensedStoryblocksAssetError as exc:
        raise SystemExit(f"b-roll stock blocked (Storyblocks EULA §A): {exc}") from exc


def ffprobe_summary(path: Path) -> dict[str, Any]:
    proc = run(
        [
            FFPROBE,
            "-v",
            "error",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            str(path),
        ]
    )
    data = json.loads(proc.stdout)
    streams = data.get("streams", [])
    fmt = data.get("format", {})
    v = next((s for s in streams if s.get("codec_type") == "video"), {})
    a = next((s for s in streams if s.get("codec_type") == "audio"), None)
    return {
        "duration_s": float(fmt.get("duration", 0.0)),
        "width": v.get("width"),
        "height": v.get("height"),
        "video_codec": v.get("codec_name"),
        "audio_codec": (a or {}).get("codec_name"),
        "has_audio": a is not None,
        "bytes": path.stat().st_size,
    }


def sha256_16(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()[:16]


def apply_stub_guard(bytes_: int, decode_ok: bool, duration_ok: bool) -> str:
    """Hard rule: bytes < STUB_GUARD_BYTES can never be 'ok'. See spec §6.4."""
    if bytes_ < STUB_GUARD_BYTES:
        return "stub"
    if not decode_ok or not duration_ok:
        return "fail"
    return "ok"


def build_snippet_bed(
    out_path: Path,
    duration_s: float,
    mood_register: str,
    *,
    licensed_audio: Path | None = None,
) -> Path:
    """Build an audio bed for the snippet.

    Prefer a licensed Storyblocks track when ``licensed_audio`` is provided and
    exists; otherwise fall back to the deterministic synthetic sine bed
    (spec §3.3). The sine fallback MUST remain — keys may be absent and other
    lanes still depend on rendering without Storyblocks credentials.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fade_out_start = max(duration_s - 1.0, 0.0)
    fade_out_dur = min(1.0, duration_s * 0.3)

    if licensed_audio is not None and Path(licensed_audio).is_file():
        # Use -af (not filter_complex) for single-input audio filters.
        af = (
            f"atrim=0:{duration_s:.3f},asetpts=PTS-STARTPTS,"
            "volume=0.12,"
            f"afade=t=in:st=0:d=0.3,afade=t=out:st={fade_out_start:.2f}:d={fade_out_dur:.2f}"
        )
        run(
            [
                FFMPEG,
                "-y",
                "-i",
                str(licensed_audio),
                "-af",
                af,
                str(out_path),
            ]
        )
        return out_path

    freqs = MOOD_FREQS[mood_register]
    inputs: list[str] = []
    for f in freqs:
        inputs += ["-f", "lavfi", "-i", f"sine=frequency={f}:duration={duration_s}"]
    filt = (
        "[0][1][2]amix=inputs=3:weights=1 1 1,"
        "lowpass=f=1200,volume=0.08,"
        f"afade=t=in:st=0:d=0.3,afade=t=out:st={fade_out_start:.2f}:d={fade_out_dur:.2f}"
    )
    run([FFMPEG, "-y", *inputs, "-filter_complex", filt, str(out_path)])
    return out_path


def render_broll_snippet(topic: str, beat_role: str, k_index: int, seed: int, out_path: Path) -> dict[str, Any]:
    pool = stock_pool(topic, provider=STOCK_PROVIDER)
    pick = pick_stock_image(topic, beat_role, seed, pool)
    img = pick["path"]
    assert_broll_stock_licensed(img, work_unit_id=f"social_broll:{topic}")
    motion = ["push", "pan", "static"][seed % 3]
    duration_s = BEAT_ROLE_DURATIONS[beat_role]
    silent = out_path.with_suffix(".silent.mp4")
    broll_mod.render_beat_clip(img, k_index, duration_s, motion, silent)
    return {
        "silent_video": silent,
        "source_stock_ref": str(img.relative_to(REPO)),
        "motion": motion,
        "keyword_score": pick["keyword_score"],
        "match_quality": pick["match_quality"],
        "match_rationale": pick["match_rationale"],
    }


def render_object_metaphor_snippet(
    topic: str, beat_role: str, k_index: int, seed: int, out_path: Path
) -> dict[str, Any]:
    pool = stock_pool(topic, provider=STOCK_PROVIDER)
    pick = pick_stock_image(topic, beat_role, seed, pool)
    img = pick["path"]
    assert_broll_stock_licensed(img, work_unit_id=f"social_broll:{topic}")
    src_w, src_h = objmeta_mod.image_dims(img)
    spec = OBJECT_METAPHOR_CROP_SPEC[beat_role]
    jitter_x = ((seed // 7) % 21 - 10) / 200.0
    jitter_y = ((seed // 13) % 21 - 10) / 200.0
    cx = min(max(DEFAULT_SUBJECT_CENTER[0] + jitter_x, 0.15), 0.85)
    cy = min(max(DEFAULT_SUBJECT_CENTER[1] + jitter_y, 0.15), 0.85)
    crop = objmeta_mod.compute_crop_window(src_w, src_h, cx, cy, spec["height_frac"])
    duration_s = BEAT_ROLE_DURATIONS[beat_role]
    silent = out_path.with_suffix(".silent.mp4")
    objmeta_mod.render_beat_clip(img, crop, spec["zoom_to"], duration_s, [], beat_role, silent)
    return {
        "silent_video": silent,
        "source_stock_ref": str(img.relative_to(REPO)),
        "crop_px": crop,
        "subject_center_frac": {"x": round(cx, 4), "y": round(cy, 4)},
        "keyword_score": pick["keyword_score"],
        "match_quality": pick["match_quality"],
        "match_rationale": pick["match_rationale"],
    }


def render_kinetic_type_snippet(topic: str, beat_role: str, seed: int, out_path: Path) -> dict[str, Any]:
    renderer_role = KINETIC_ROLE_MAP[beat_role]
    duration_s = BEAT_ROLE_DURATIONS[beat_role]
    text = KINETIC_PLACEHOLDER_TEXT.get(beat_role, topic.upper())
    if beat_role == "hook":
        text = topic.upper()

    ass_path = out_path.with_suffix(".ass")
    lines, _reveals = kinetic_mod.build_beat_lines(renderer_role, text, 0.0, duration_s)
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {WIDTH}
PlayResY: {HEIGHT}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{kinetic_mod.FONT_NAME},96,&H00F3EEE3,&H00F3EEE3,&H001A1A1A,&H00000000,0,0,0,0,100,100,0,0,1,3,0,5,80,80,80,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ass_path.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")

    silent = out_path.with_suffix(".silent.mp4")
    bg_source = kinetic_mod.lavfi_source(renderer_role, duration_s)
    ass_escaped = str(ass_path).replace("\\", "\\\\").replace(":", "\\:")
    filt = f"[0:v]ass='{ass_escaped}'[outv]"
    fast = _os.environ.get("MEDIA_BANK_FAST_MOTION", "").strip().lower() in {"1", "true", "yes", "2"}
    if fast:
        # Solid-color 1-frame + stream-loop (no libass). Kinetic is already INTERIM;
        # ASS under load averages >100 stalls for minutes per cell.
        one = out_path.with_suffix(".1frame.mp4")
        run(
            [
                FFMPEG,
                "-y",
                "-f",
                "lavfi",
                "-i",
                f"color=c=0xF3EEE3:s={WIDTH}x{HEIGHT}:d=0.04:r=30",
                "-frames:v",
                "1",
                "-c:v",
                "libx264",
                "-preset",
                "ultrafast",
                "-tune",
                "stillimage",
                "-crf",
                "28",
                "-pix_fmt",
                "yuv420p",
                "-an",
                str(one),
            ]
        )
        run(
            [
                FFMPEG,
                "-y",
                "-stream_loop",
                "-1",
                "-i",
                str(one),
                "-t",
                str(duration_s),
                "-c:v",
                "copy",
                "-an",
                str(silent),
            ]
        )
        one.unlink(missing_ok=True)
    else:
        run(
            [
                FFMPEG,
                "-y",
                "-f",
                "lavfi",
                "-i",
                bg_source,
                "-filter_complex",
                filt,
                "-map",
                "[outv]",
                "-r",
                str(FPS),
                "-t",
                str(duration_s),
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
                str(silent),
            ]
        )
    return {
        "silent_video": silent,
        "source_stock_ref": None,
        "placeholder_text": text,
        "renderer_role_mapping": renderer_role,
    }


def mux_with_bed(
    silent_video: Path,
    mood_register: str,
    duration_s: float,
    work_dir: Path,
    out_path: Path,
    *,
    work_unit_id: str | None = None,
) -> None:
    """Mux silent video with licensed Storyblocks audio bed when available, else sine fallback."""
    licensed: Path | None = None
    try:
        from scripts.storyblocks.mood_audio import resolve_licensed_audio_bed

        licensed = resolve_licensed_audio_bed(mood_register, work_unit_id)
    except Exception:
        licensed = None
    bed = build_snippet_bed(
        work_dir / "bed.wav",
        duration_s,
        mood_register,
        licensed_audio=licensed,
    )
    kinetic_mod.mux(silent_video, bed, out_path)


def export_aspect_variant(master_path: Path, bucket: str, out_path: Path) -> None:
    """Deterministic safe-crop derivation from the 9:16 master (spec §5)."""
    spec = ASPECT_BUCKETS[bucket]
    crop = spec["crop"]
    if crop is None:
        raise ValueError("VERTICAL_9_16 is native; nothing to export")
    cw, ch = crop["w"], crop["h"]
    cx = (WIDTH - cw) // 2
    cy = (HEIGHT - ch) // 2
    vf = f"crop={cw}:{ch}:{cx}:{cy}"
    if spec.get("scale"):
        sw, sh = spec["scale"]
        vf += f",scale={sw}:{sh}"
    cmd = [
        FFMPEG,
        "-y",
        "-i",
        str(master_path),
        "-vf",
        vf,
        "-c:v",
        "libx264",
        "-preset",
        _mb_ffmpeg_preset(),
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "copy",
        "-movflags",
        "+faststart",
        str(out_path),
    ]
    run(cmd)


@dataclass
class Cell:
    family: str
    topic: str
    beat_role: str
    k_index: int
    aspect_bucket: str = "VERTICAL_9_16"


@dataclass
class Receipt:
    row: dict[str, Any] = field(default_factory=dict)


def render_cell(cell: Cell) -> Receipt:
    seed = derive_seed(cell.family, cell.topic, cell.beat_role, cell.k_index)
    duration_s = BEAT_ROLE_DURATIONS[cell.beat_role]
    asset_id = f"{cell.family}__{cell.topic}__{cell.beat_role}__k{cell.k_index:02d}__{cell.aspect_bucket}"

    PILOTS_DIR.mkdir(parents=True, exist_ok=True)
    work_dir = WORK_ROOT / asset_id
    work_dir.mkdir(parents=True, exist_ok=True)
    final_path = PILOTS_DIR / f"{asset_id}.mp4"

    mood_register = mood_register_for_topic(SIZING, cell.topic)

    content_provenance = "REAL"
    source_stock_ref = None
    extra: dict[str, Any] = {}

    if cell.family == "broll_montage":
        info = render_broll_snippet(cell.topic, cell.beat_role, cell.k_index, seed, work_dir / "clip")
        source_stock_ref = info["source_stock_ref"]
        extra["motion"] = info["motion"]
    elif cell.family == "object_metaphor":
        info = render_object_metaphor_snippet(cell.topic, cell.beat_role, cell.k_index, seed, work_dir / "clip")
        source_stock_ref = info["source_stock_ref"]
        extra["crop_px"] = info["crop_px"]
        extra["subject_center_frac"] = info["subject_center_frac"]
    elif cell.family == "kinetic_type":
        info = render_kinetic_type_snippet(cell.topic, cell.beat_role, seed, work_dir / "clip")
        content_provenance = "INTERIM"
        extra["placeholder_text"] = info["placeholder_text"]
    else:
        raise SystemExit(f"unknown family {cell.family!r}")

    mux_with_bed(
        info["silent_video"],
        mood_register,
        duration_s,
        work_dir,
        final_path,
        work_unit_id=f"social_broll:{cell.topic}",
    )

    summary = ffprobe_summary(final_path)
    decode_ok = summary["video_codec"] is not None
    duration_ok = abs(summary["duration_s"] - duration_s) <= DURATION_TOLERANCE_S
    status = apply_stub_guard(summary["bytes"], decode_ok, duration_ok)

    r2_label = ASPECT_BUCKETS[cell.aspect_bucket]["label"]
    r2_key = f"social-media-bank/v1/video/{cell.topic}/{cell.family}/{r2_label}/{asset_id}.mp4"

    row = {
        "asset_id": asset_id,
        "family": cell.family,
        "topic_native_family": cell.topic,
        "beat_role": cell.beat_role,
        "k_index": cell.k_index,
        "seed": seed,
        "aspect_bucket": cell.aspect_bucket,
        "width": summary["width"],
        "height": summary["height"],
        "fps": FPS,
        "duration_s_target": duration_s,
        "duration_s_actual": round(summary["duration_s"], 3),
        "video_codec": summary["video_codec"],
        "audio_codec": summary["audio_codec"],
        "has_audio": summary["has_audio"],
        "bytes": summary["bytes"],
        "sha256_16": sha256_16(final_path),
        "mood_register": mood_register,
        "source_stock_ref": source_stock_ref or "",
        "content_provenance": content_provenance,
        "license_status": "unverified_inherited_100x_pexels" if source_stock_ref else "n/a_no_photography",
        "production_ready": False,
        "review_status": "unreviewed",
        "render_status": status,
        "r2_key_planned": r2_key,
        "r2_uploaded": "pending",
        "local_path": str(final_path.relative_to(REPO)),
        "generated_by": "scripts/social/build_video_snippet_bank.py",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "keyword_score": info.get("keyword_score", ""),
        "match_quality": info.get("match_quality", ""),
        "match_rationale": info.get("match_rationale", ""),
    }
    row.update({f"_extra_{k}": v for k, v in extra.items()})
    return Receipt(row=row)


def load_manifest_rows() -> dict[str, dict[str, Any]]:
    if not MANIFEST_PATH.exists():
        return {}
    rows: dict[str, dict[str, Any]] = {}
    with MANIFEST_PATH.open(encoding="utf-8") as f:
        header = f.readline().rstrip("\n").split("\t")
        for line in f:
            if not line.strip():
                continue
            values = line.rstrip("\n").split("\t")
            row = dict(zip(header, values))
            rows[row["asset_id"]] = row
    return rows


def write_manifest(rows: dict[str, dict[str, Any]]) -> None:
    """Atomic merge-write so parallel --families workers do not clobber each other."""
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    lock_path = OUT_ROOT / "MANIFEST.lock"
    with lock_path.open("a+", encoding="utf-8") as lock_fh:
        fcntl.flock(lock_fh.fileno(), fcntl.LOCK_EX)
        try:
            merged = load_manifest_rows()
            merged.update(rows)
            tmp = MANIFEST_PATH.with_suffix(".tsv.tmp")
            with tmp.open("w", encoding="utf-8") as f:
                f.write("\t".join(MANIFEST_COLUMNS) + "\n")
                for asset_id in sorted(merged):
                    row = merged[asset_id]
                    f.write("\t".join(str(row.get(c, "")) for c in MANIFEST_COLUMNS) + "\n")
            tmp.replace(MANIFEST_PATH)
            rows.clear()
            rows.update(merged)
        finally:
            fcntl.flock(lock_fh.fileno(), fcntl.LOCK_UN)


def adopt_existing_master(cell: Cell) -> Optional[Receipt]:
    """If a prior run left a valid master on disk but not in the manifest, adopt it."""
    asset_id = f"{cell.family}__{cell.topic}__{cell.beat_role}__k{cell.k_index:02d}__VERTICAL_9_16"
    final_path = PILOTS_DIR / f"{asset_id}.mp4"
    if not final_path.exists() or final_path.stat().st_size < STUB_GUARD_BYTES:
        return None
    duration_s = BEAT_ROLE_DURATIONS[cell.beat_role]
    summary = ffprobe_summary(final_path)
    decode_ok = summary["video_codec"] is not None
    duration_ok = abs(summary["duration_s"] - duration_s) <= DURATION_TOLERANCE_S
    status = apply_stub_guard(summary["bytes"], decode_ok, duration_ok)
    if status != "ok":
        return None
    seed = derive_seed(cell.family, cell.topic, cell.beat_role, cell.k_index)
    mood_register = mood_register_for_topic(SIZING, cell.topic)
    r2_label = ASPECT_BUCKETS["VERTICAL_9_16"]["label"]
    row = {
        "asset_id": asset_id,
        "family": cell.family,
        "topic_native_family": cell.topic,
        "beat_role": cell.beat_role,
        "k_index": cell.k_index,
        "seed": seed,
        "aspect_bucket": "VERTICAL_9_16",
        "width": summary["width"],
        "height": summary["height"],
        "fps": FPS,
        "duration_s_target": duration_s,
        "duration_s_actual": round(summary["duration_s"], 3),
        "video_codec": summary["video_codec"],
        "audio_codec": summary["audio_codec"],
        "has_audio": summary["has_audio"],
        "bytes": summary["bytes"],
        "sha256_16": sha256_16(final_path),
        "mood_register": mood_register,
        "source_stock_ref": "",
        "content_provenance": "INTERIM" if cell.family == "kinetic_type" else "REAL",
        "license_status": "n/a_no_photography" if cell.family == "kinetic_type" else "unverified_inherited_100x_pexels",
        "production_ready": False,
        "review_status": "unreviewed",
        "render_status": status,
        "r2_key_planned": f"social-media-bank/v1/video/{cell.topic}/{cell.family}/{r2_label}/{asset_id}.mp4",
        "r2_uploaded": "pending",
        "local_path": str(final_path.relative_to(REPO)),
        "generated_by": "scripts/social/build_video_snippet_bank.py",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    return Receipt(row=row)


_UNRESOLVED_UPLOAD_STATES = {"pending", "not_attempted", "blocked_no_creds"}


def maybe_upload_r2(rows: dict[str, dict[str, Any]], attempt: bool) -> None:
    if not attempt:
        for row in rows.values():
            if row.get("r2_uploaded") in _UNRESOLVED_UPLOAD_STATES:
                row["r2_uploaded"] = "not_attempted"
        return
    import os

    missing = [
        n
        for n in ("CLOUDFLARE_ACCOUNT_ID", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY")
        if not os.environ.get(n)
    ]
    if missing:
        print(f"BLOCKER: R2 upload skipped, missing env: {missing}", file=sys.stderr)
        for row in rows.values():
            if row.get("r2_uploaded") in _UNRESOLVED_UPLOAD_STATES:
                row["r2_uploaded"] = "blocked_no_creds"
        return

    from scripts.artifacts.r2_push_helper import _r2_client, _bucket_name, _content_type  # type: ignore

    client = _r2_client()
    bucket = _bucket_name()
    for row in rows.values():
        if row.get("r2_uploaded") not in _UNRESOLVED_UPLOAD_STATES:
            continue
        local_path = REPO / row["local_path"]
        if row["render_status"] != "ok" or not local_path.exists():
            row["r2_uploaded"] = "skipped_not_ok"
            continue
        key = row["r2_key_planned"]
        with local_path.open("rb") as fh:
            client.put_object(
                Bucket=bucket,
                Key=key,
                Body=fh,
                ContentType=_content_type(local_path),
                Metadata={"sha256_16": row["sha256_16"]},
            )
        row["r2_uploaded"] = "uploaded"
        print(f"uploaded -> s3://{bucket}/{key}")


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--phase", choices=["pilot", "v1_en_us", "v1_all_markets"], default="pilot")
    ap.add_argument("--families", default=",".join(FAMILIES))
    ap.add_argument("--topics", default="")
    ap.add_argument("--roles", default="beat")
    ap.add_argument("--k-limit", type=int, default=1, help="cap k_index loop (default: 1 slot, k_index=0)")
    ap.add_argument(
        "--aspects",
        default="VERTICAL_9_16",
        help="comma list; non-native buckets are derived by crop-export from the VERTICAL_9_16 master",
    )
    ap.add_argument("--r2-upload", action="store_true", help="best-effort R2 push; no-op if creds missing")
    ap.add_argument("--limit", type=int, default=0, help="safety cap on total cells rendered this invocation (0=no cap)")
    ap.add_argument(
        "--skip-existing",
        action="store_true",
        help="skip cells whose VERTICAL_9_16 master already has render_status=ok in the manifest",
    )
    ap.add_argument(
        "--checkpoint-every",
        type=int,
        default=10,
        help="rewrite MANIFEST.tsv every N newly rendered masters (default 10)",
    )
    ap.add_argument(
        "--stock-provider",
        choices=["auto", "pexels", "storyblocks"],
        default="auto",
        help="auto=licensed Storyblocks work-unit bank then Pexels fill; "
        "storyblocks=licensed HD only (confirm_selection path)",
    )
    return ap


def main() -> int:
    global STOCK_PROVIDER
    args = build_parser().parse_args()
    STOCK_PROVIDER = args.stock_provider
    families = [f.strip() for f in args.families.split(",") if f.strip()]
    roles = [r.strip() for r in args.roles.split(",") if r.strip()]
    aspects = [a.strip() for a in args.aspects.split(",") if a.strip()]

    # Auto k from sizing table when caller left the pilot default (1) on a scale phase.
    k_limit = args.k_limit
    if args.phase in {"v1_en_us", "v1_all_markets"} and args.k_limit == 1:
        for row in (SIZING.get("video_bank") or {}).get("rows") or []:
            if row.get("phase") == args.phase and row.get("k"):
                k_limit = int(row["k"])
                print(f"auto k-limit from sizing phase={args.phase}: {k_limit}")
                break

    if args.topics:
        topics = [t.strip() for t in args.topics.split(",") if t.strip()]
    elif args.phase == "pilot":
        topics = PILOT_PRIORITY_TOPICS
    else:
        topics = list(SIZING["dimensions"]["topics_native_family"]["families"])

    for f in families:
        if f not in FAMILIES:
            raise SystemExit(f"unknown family {f!r}, must be one of {FAMILIES}")
    for r in roles:
        if r not in BEAT_ROLE_DURATIONS:
            raise SystemExit(f"unknown beat_role {r!r}, must be one of {list(BEAT_ROLE_DURATIONS)}")
    for a in aspects:
        if a not in ASPECT_BUCKETS:
            raise SystemExit(f"unknown aspect bucket {a!r}, must be one of {list(ASPECT_BUCKETS)}")

    cells = [
        Cell(family=family, topic=topic, beat_role=role, k_index=k_index)
        for family in families
        for topic in topics
        for role in roles
        for k_index in range(min(k_limit, 12))
    ]
    if args.limit:
        cells = cells[: args.limit]

    rows = load_manifest_rows()
    rendered_new = 0
    skipped = 0
    for idx, cell in enumerate(cells, 1):
        master_id = f"{cell.family}__{cell.topic}__{cell.beat_role}__k{cell.k_index:02d}__VERTICAL_9_16"
        if args.skip_existing and rows.get(master_id, {}).get("render_status") == "ok":
            skipped += 1
            print(f"[{idx}/{len(cells)}] SKIP existing {master_id}")
            continue
        if args.skip_existing:
            adopted = adopt_existing_master(cell)
            if adopted is not None:
                rows[adopted.row["asset_id"]] = adopted.row
                skipped += 1
                print(f"[{idx}/{len(cells)}] ADOPT disk {master_id} bytes={adopted.row['bytes']}")
                # Persist adopts immediately so a killed worker does not lose disk recovery.
                if args.checkpoint_every and skipped % max(args.checkpoint_every, 1) == 0:
                    write_manifest(rows)
                continue
        print(f"[{idx}/{len(cells)}] === rendering {cell.family}/{cell.topic}/{cell.beat_role}/k{cell.k_index:02d} (native VERTICAL_9_16) ===")
        try:
            receipt = render_cell(cell)
        except SystemExit as exc:
            # Soft-fail one cell so a missing stock folder cannot kill the whole family worker.
            asset_id = f"{cell.family}__{cell.topic}__{cell.beat_role}__k{cell.k_index:02d}__VERTICAL_9_16"
            fail_row = {
                "asset_id": asset_id,
                "family": cell.family,
                "topic_native_family": cell.topic,
                "beat_role": cell.beat_role,
                "k_index": cell.k_index,
                "seed": derive_seed(cell.family, cell.topic, cell.beat_role, cell.k_index),
                "aspect_bucket": "VERTICAL_9_16",
                "width": WIDTH,
                "height": HEIGHT,
                "fps": FPS,
                "duration_s_target": BEAT_ROLE_DURATIONS[cell.beat_role],
                "duration_s_actual": 0,
                "video_codec": "",
                "audio_codec": "",
                "has_audio": False,
                "bytes": 0,
                "sha256_16": "",
                "mood_register": "",
                "source_stock_ref": "",
                "content_provenance": "REAL",
                "license_status": "n/a",
                "production_ready": False,
                "review_status": "unreviewed",
                "render_status": "fail",
                "r2_key_planned": f"social-media-bank/v1/video/{cell.topic}/{cell.family}/9x16/{asset_id}.mp4",
                "r2_uploaded": "pending",
                "local_path": "",
                "generated_by": "scripts/social/build_video_snippet_bank.py",
                "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
            rows[asset_id] = fail_row
            rendered_new += 1
            print(f"FAIL soft {asset_id}: {exc}", flush=True)
            if args.checkpoint_every and rendered_new % args.checkpoint_every == 0:
                write_manifest(rows)
            continue
        rows[receipt.row["asset_id"]] = receipt.row
        rendered_new += 1
        print(json.dumps({k: v for k, v in receipt.row.items() if not k.startswith("_extra_")}, indent=2, default=str))

        master_path = REPO / receipt.row["local_path"]
        for bucket in aspects:
            if bucket == "VERTICAL_9_16" or receipt.row["render_status"] != "ok":
                continue
            derived_asset_id = f"{cell.family}__{cell.topic}__{cell.beat_role}__k{cell.k_index:02d}__{bucket}"
            derived_path = PILOTS_DIR / f"{derived_asset_id}.mp4"
            print(f"    -> deriving {bucket} crop-export from master")
            export_aspect_variant(master_path, bucket, derived_path)
            d_summary = ffprobe_summary(derived_path)
            d_status = apply_stub_guard(
                d_summary["bytes"],
                d_summary["video_codec"] is not None,
                abs(d_summary["duration_s"] - BEAT_ROLE_DURATIONS[cell.beat_role]) <= DURATION_TOLERANCE_S,
            )
            d_label = ASPECT_BUCKETS[bucket]["label"]
            d_row = dict(receipt.row)
            d_row.update(
                {
                    "asset_id": derived_asset_id,
                    "aspect_bucket": bucket,
                    "width": d_summary["width"],
                    "height": d_summary["height"],
                    "duration_s_actual": round(d_summary["duration_s"], 3),
                    "bytes": d_summary["bytes"],
                    "sha256_16": sha256_16(derived_path),
                    "render_status": d_status,
                    "r2_key_planned": f"social-media-bank/v1/video/{cell.topic}/{cell.family}/{d_label}/{derived_asset_id}.mp4",
                    "r2_uploaded": "pending",
                    "local_path": str(derived_path.relative_to(REPO)),
                }
            )
            rows[derived_asset_id] = d_row

        if args.checkpoint_every and rendered_new % args.checkpoint_every == 0:
            write_manifest(rows)
            print(f"    checkpoint: wrote manifest ({len(rows)} rows, {rendered_new} new this run)")

    maybe_upload_r2(rows, attempt=args.r2_upload)
    write_manifest(rows)
    print(f"skip_existing={skipped} newly_rendered={rendered_new}")

    ok = [r for r in rows.values() if r["render_status"] == "ok"]
    stub = [r for r in rows.values() if r["render_status"] == "stub"]
    failed = [r for r in rows.values() if r["render_status"] == "fail"]
    print("\n=== SUMMARY ===")
    print(f"manifest: {MANIFEST_PATH.relative_to(REPO)}")
    print(f"ok={len(ok)} stub={len(stub)} fail={len(failed)} total_rows={len(rows)}")
    if failed:
        print(f"FAIL: {len(failed)} row(s) failed render/decode gates", file=sys.stderr)
        return 1
    return 0


SIZING = load_sizing()

if __name__ == "__main__":
    raise SystemExit(main())
