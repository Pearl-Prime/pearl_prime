#!/usr/bin/env python3
"""build_beat_driven — ONE parameterized beat-driven video builder (canonical).

Generalizes the v3.1–v3.7 ``build_v3_N_yt_starseed.py`` / ``intelligent_v3_6/v3_7``
one-offs into a single, config-driven builder so the proven beat-driven method
becomes the default path instead of a fork-per-video side script.

Pipeline (the canonical recipe — VIDEO_BEST_METHOD_CONSOLIDATION.md §3):

    inputs (brand / beats / audio)
      → word-level forced alignment        (whisper, local/free; injectable)
      → snap beats to narrator delivery
      → master-prompt render, seed-locked   (flux1-dev via ComfyUI; Tier-2, injectable)
      → AI-judge gate, keep-best            (scripts/video/run_frame_judge.py — CONSUMED, not re-derived)
      → best-of curate                      (judge-kept frame per beat; operator best-of is the W4 selector)
      → assemble (silent + mix)             (ffmpeg; injectable)
      → compat re-encode                    (ffmpeg faststart; injectable)
      → emit distribution_manifest.json into publish_queue/   (the missing link that
        lets build_daily_batch.py SELECT the video → run_upload.py publishes it)

Every external/expensive seam — alignment, render, judge, assemble, compat — is an
injectable callable defaulting to the real (Tier-2 local) implementation, so unit
tests stub them and the whole structure is exercised in CI with no GPU, no live
Pearl Star box, and NO paid API (CLAUDE.md LLM tier policy).

The AI-judge step binds to the public API of ``scripts/video/run_frame_judge.py``
(lane B): :class:`run_frame_judge.JudgeItem`, :class:`~run_frame_judge.JudgeConfig`,
:func:`~run_frame_judge.run_frame_judge`, :func:`~run_frame_judge.seed_for`. The
judge/render/rewrite callables are passed straight through to that module.

Authority:
    docs/specs/PEARL_VIDEO_BEAT_DRIVEN_NARRATIVE_PIPELINE_V1_SPEC.md  (stage map, beat schema)
    docs/specs/PEARL_VIDEO_FRAME_SELECTOR_BEST_OF_V1_SPEC.md          (best-of / export schema)
    artifacts/video/video_best_method_20260616/VIDEO_BEST_METHOD_CONSOLIDATION.md  (W1/W3/W5 refactor)
    cap PEARL-VIDEO-BEAT-DRIVEN-V1-01 (ratify lane D)

Public API (what run_pipeline + tests bind to):
    BeatVideoConfig(...)                 # all knobs; no hardcoded per-version constants
    load_beats(beats_path) -> list[dict] # .py BEATS module | .json list/{"beats":[...]}
    BeatDrivenBuilder(config, *, align_fn, render_fn, judge_fn, rewrite_fn,
                      assemble_fn, compat_fn, write_manifest_fn)
        .build() -> BuildResult
    BuildResult(timed_beats, verdicts, frames_dir, silent_path, final_path,
                compat_path, manifest_path, manifest)
    emit_distribution_manifest(config, *, result_meta, out_path) -> Path
    main(argv) -> int                    # CLI
"""
from __future__ import annotations

import argparse
import dataclasses
import importlib.util
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional, Sequence

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts" / "video"))

# CONSUME lane B's reusable judge — do NOT re-derive it.
import run_frame_judge as rfj  # noqa: E402
from scripts.video._config import write_atomically, get_ffmpeg_bin  # noqa: E402

DEFAULT_PUBLISH_QUEUE = REPO_ROOT / "artifacts" / "video" / "publish_queue"
DEFAULT_FRAME_BASE = 4000  # spec frame-numbering: 4000+ = future beat-driven videos
DEFAULT_WIDTH, DEFAULT_HEIGHT = 1920, 1080


# ───────────────────────────── config ─────────────────────────────

@dataclasses.dataclass
class BeatVideoConfig:
    """All builder knobs. Driven by args / config/video, never hardcoded per version."""
    video_id: str
    beats_path: Path
    audio_path: Optional[Path] = None
    plan_id: Optional[str] = None
    brand_id: str = "stillness_press"
    channel_id: str = "ch_001"
    content_type: str = "narrative"
    title: str = ""
    description: str = ""
    tags: Sequence[str] = ()
    platforms: Sequence[str] = ("youtube",)
    format: str = "landscape_16_9"

    artifact_dir: Optional[Path] = None        # where frames / mp4 land
    frames_dir: Optional[Path] = None
    publish_queue_dir: Path = DEFAULT_PUBLISH_QUEUE
    frame_base: int = DEFAULT_FRAME_BASE
    width: int = DEFAULT_WIDTH
    height: int = DEFAULT_HEIGHT
    fps: int = 30

    # judge knobs (passed through to run_frame_judge.JudgeConfig)
    judge_threshold: int = rfj.DEFAULT_THRESHOLD
    judge_max_retries: int = rfj.DEFAULT_MAX_RETRIES
    judge_model: str = rfj.DEFAULT_JUDGE_MODEL
    rewriter_model: str = rfj.DEFAULT_REWRITER_MODEL
    ollama_url: Optional[str] = None
    comfyui_url: Optional[str] = None

    # behaviour flags (the no-GPU / structure-only seams)
    skip_render: bool = False     # don't call ComfyUI (frames must pre-exist / be stubbed)
    skip_judge: bool = False      # don't run the AI-judge gate
    skip_assemble: bool = False   # don't shell ffmpeg
    style_lock: str = rfj.DEFAULT_STYLE_LOCK
    negative_bank: str = rfj.DEFAULT_NEGATIVE_BANK
    batch_id: str = ""

    def __post_init__(self) -> None:
        self.beats_path = Path(self.beats_path)
        if self.audio_path is not None:
            self.audio_path = Path(self.audio_path)
        self.plan_id = self.plan_id or self.video_id
        self.title = self.title or self.video_id.replace("_", " ").replace("-", " ").title()
        self.tags = list(self.tags)
        self.platforms = list(self.platforms)
        if self.artifact_dir is None:
            self.artifact_dir = REPO_ROOT / "artifacts" / "video" / self.video_id
        else:
            self.artifact_dir = Path(self.artifact_dir)
        if self.frames_dir is None:
            self.frames_dir = self.artifact_dir / "frames"
        else:
            self.frames_dir = Path(self.frames_dir)
        self.publish_queue_dir = Path(self.publish_queue_dir)
        if not self.batch_id:
            self.batch_id = f"batch-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}-{self.video_id}"

    def judge_config(self) -> "rfj.JudgeConfig":
        return rfj.JudgeConfig(
            threshold=self.judge_threshold,
            max_retries=self.judge_max_retries,
            judge_model=self.judge_model,
            rewriter_model=self.rewriter_model,
            ollama_url=self.ollama_url,
            comfyui_url=self.comfyui_url,
            width=self.width,
            height=self.height,
            style_lock=self.style_lock,
            negative_bank=self.negative_bank,
        )


# ───────────────────────────── results ─────────────────────────────

@dataclasses.dataclass
class BuildResult:
    timed_beats: list
    verdicts: list
    frames_dir: Path
    silent_path: Optional[Path] = None
    final_path: Optional[Path] = None
    compat_path: Optional[Path] = None
    manifest_path: Optional[Path] = None
    manifest: Optional[dict] = None

    @property
    def kept_frames(self) -> list:
        """The best-of frame per beat (judge-kept image if judged, else the render path)."""
        return [v.kept_image for v in self.verdicts if v.kept_image]


# ───────────────────────── beat loading ─────────────────────────

def load_beats(beats_path: Path) -> list:
    """Load a BEATS list from a .py module (``BEATS`` attribute) or a JSON file.

    Beat schema (PEARL_VIDEO_BEAT_DRIVEN_NARRATIVE_PIPELINE_V1_SPEC §"Beat schema"):
        {id, text, decision: render_new|reuse_existing, prompt? , frame?}
    JSON may be a bare list or ``{"beats": [...]}``.
    """
    beats_path = Path(beats_path)
    if beats_path.suffix == ".py":
        spec = importlib.util.spec_from_file_location(beats_path.stem, beats_path)
        if spec is None or spec.loader is None:
            raise ValueError(f"cannot import beats module: {beats_path}")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        beats = getattr(mod, "BEATS", None)
        if beats is None:
            raise ValueError(f"{beats_path} has no BEATS attribute")
        return list(beats)
    data = json.loads(beats_path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "beats" in data:
        return list(data["beats"])
    if isinstance(data, list):
        return data
    raise ValueError(f"unrecognized beats JSON shape in {beats_path}")


# ───────────────────────── default seams (Tier-2 / local) ─────────────────────────

def default_align(config: BeatVideoConfig, beats: list) -> list:
    """Snap beats to narrator delivery via word-level alignment.

    Looks for ``<artifact_dir>/whisper_alignment.json`` (produced by
    scripts/video/whisper_word_align.py). If absent (no audio / CI), falls back
    to a uniform-cadence stamp so the structure is still buildable. Each beat is
    returned with ``start_s`` / ``end_s`` populated. Never calls a paid API.
    """
    align_path = config.artifact_dir / "whisper_alignment.json"
    if align_path.exists():
        try:
            from build_v3_2_yt_starseed import snap_with_pause_absorption  # type: ignore
            whisper = json.loads(align_path.read_text(encoding="utf-8"))
            return list(snap_with_pause_absorption(
                beats, whisper["words"], whisper["duration_seconds"]))
        except Exception as exc:  # noqa: BLE001 — degrade to uniform cadence
            print(f"[align] forced-alignment unavailable ({exc!r}); uniform cadence",
                  file=sys.stderr)
    return uniform_cadence(beats, per_beat_s=4.0)


def uniform_cadence(beats: list, *, per_beat_s: float = 4.0) -> list:
    """Deterministic fallback timing: each beat gets ``per_beat_s`` back-to-back."""
    out = []
    t = 0.0
    for b in beats:
        nb = dict(b)
        nb["start_s"] = round(t, 3)
        nb["end_s"] = round(t + per_beat_s, 3)
        out.append(nb)
        t += per_beat_s
    return out


def default_render(config: BeatVideoConfig):
    """Return a run_frame_judge-compatible ``render_fn`` or None.

    The judge's own ComfyUIRenderer is reused (it already speaks the flux-dev
    workflow + style-lock contract). None when rendering is disabled.
    """
    if config.skip_render or not config.comfyui_url:
        return None
    return rfj.ComfyUIRenderer(config.judge_config())


def default_assemble(config: BeatVideoConfig, result: BuildResult) -> BuildResult:
    """ffmpeg concat (absolute-start-sec, drift-free) → silent mp4 → mix audio.

    Mirrors assemble_v3_8.py's drift-free absolute-timestamp concat. Shells ffmpeg;
    skipped when ``skip_assemble`` (CI) — then silent_path/final_path stay None.
    """
    if config.skip_assemble:
        return result
    ffmpeg = get_ffmpeg_bin()
    art = config.artifact_dir
    art.mkdir(parents=True, exist_ok=True)
    concat = art / f"{config.video_id}_concat.txt"
    timeline = _timeline_from_beats(result.timed_beats, result.verdicts, config)
    if not timeline:
        print("[assemble] empty timeline; skipping ffmpeg", file=sys.stderr)
        return result
    _write_ffconcat(concat, timeline)

    silent = art / f"{config.video_id}_silent.mp4"
    subprocess.run([
        ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
        "-vf", f"scale={config.width}:{config.height}:force_original_aspect_ratio=decrease,"
               f"pad={config.width}:{config.height}:(ow-iw)/2:(oh-ih)/2,setsar=1,"
               f"fps={config.fps},format=yuv420p",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
        str(silent),
    ], check=True)
    result.silent_path = silent

    if config.audio_path and Path(config.audio_path).exists():
        final = art / f"{config.video_id}.mp4"
        subprocess.run([
            ffmpeg, "-y", "-i", str(silent), "-i", str(config.audio_path),
            "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac",
            "-b:a", "192k", "-shortest", str(final),
        ], check=True)
        result.final_path = final
    else:
        result.final_path = silent
    return result


def default_compat(config: BeatVideoConfig, result: BuildResult) -> BuildResult:
    """Capture the previously-tacit ``_compat`` re-encode (Consolidation W6/G4).

    Broad-playback re-encode: yuv420p + faststat. Skipped with ``skip_assemble``.
    """
    if config.skip_assemble or not result.final_path:
        return result
    ffmpeg = get_ffmpeg_bin()
    src = Path(result.final_path)
    compat = src.with_name(f"{src.stem}_compat.mp4")
    subprocess.run([
        ffmpeg, "-y", "-i", str(src),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.0",
        "-movflags", "+faststart", "-c:a", "aac", "-b:a", "192k", str(compat),
    ], check=True)
    result.compat_path = compat
    return result


def _timeline_from_beats(timed_beats: list, verdicts: list, config: BeatVideoConfig) -> list:
    """(abs_start_sec, frame_path) pairs from the best-of frame per beat."""
    kept_by_id = {v.id: v.kept_image for v in verdicts if v.kept_image}
    timeline = []
    for i, b in enumerate(timed_beats):
        bid = str(b.get("id", i))
        frame = kept_by_id.get(bid) or _beat_frame_path(b, i, config)
        if frame and Path(frame).exists():
            timeline.append((float(b.get("start_s", i * 4.0)), Path(frame)))
    timeline.sort(key=lambda x: x[0])
    return timeline


def _write_ffconcat(path: Path, timeline: list) -> None:
    end = timeline[-1][0] + 4.0
    lines = ["ffconcat version 1.0"]
    for i, (start, frame) in enumerate(timeline):
        nxt = timeline[i + 1][0] if i + 1 < len(timeline) else end
        dur = max(nxt - start, 0.001)
        lines.append(f"file '{frame}'")
        lines.append(f"duration {dur:.6f}")
    lines.append(f"file '{timeline[-1][1]}'")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _beat_frame_path(beat: dict, idx: int, config: BeatVideoConfig) -> Path:
    """Resolve a beat's frame path: explicit ``frame`` index, else frame_base+idx."""
    if "image" in beat:
        return Path(beat["image"])
    if beat.get("decision") == "reuse_existing" and "frame" in beat:
        return config.frames_dir / f"frame_{int(beat['frame']):04d}.png"
    return config.frames_dir / f"frame_{config.frame_base + idx:04d}.png"


# ───────────────────────────── the builder ─────────────────────────────

AlignFn = Callable[[BeatVideoConfig, list], list]
AssembleFn = Callable[[BeatVideoConfig, BuildResult], BuildResult]
WriteManifestFn = Callable[..., Path]


class BeatDrivenBuilder:
    """Orchestrates the canonical beat-driven build. Every seam is injectable."""

    def __init__(
        self,
        config: BeatVideoConfig,
        *,
        align_fn: Optional[AlignFn] = None,
        render_fn=None,
        judge_fn=None,
        rewrite_fn=None,
        assemble_fn: Optional[AssembleFn] = None,
        compat_fn: Optional[AssembleFn] = None,
        write_manifest_fn: Optional[WriteManifestFn] = None,
        progress: Optional[Callable[[str], None]] = None,
    ):
        self.config = config
        self.align_fn = align_fn or default_align
        self._render_fn = render_fn  # None => default_render decides at build()
        self._render_explicit = render_fn is not None
        self.judge_fn = judge_fn
        self.rewrite_fn = rewrite_fn
        self.assemble_fn = assemble_fn or default_assemble
        self.compat_fn = compat_fn or default_compat
        self.write_manifest_fn = write_manifest_fn or emit_distribution_manifest
        self.log = progress or (lambda m: print(f"[build_beat_driven] {m}", flush=True))

    def build(self) -> BuildResult:
        cfg = self.config
        cfg.frames_dir.mkdir(parents=True, exist_ok=True)

        beats = load_beats(cfg.beats_path)
        self.log(f"loaded {len(beats)} beats from {cfg.beats_path.name}")

        timed = self.align_fn(cfg, beats)
        self.log(f"aligned {len(timed)} beats")

        # Build judge items, seed-locked per beat (blake2b(beat_id) via run_frame_judge).
        items = self._judge_items(timed)

        render_fn = self._render_fn if self._render_explicit else default_render(cfg)
        if cfg.skip_judge:
            verdicts = self._stub_verdicts(items)
            self.log("judge gate skipped (skip_judge)")
        else:
            verdicts = rfj.run_frame_judge(
                items, cfg.judge_config(),
                judge_fn=self.judge_fn, rewrite_fn=self.rewrite_fn, render_fn=render_fn,
                progress=lambda m: self.log(f"  judge: {m}"),
            )
            passed = sum(1 for v in verdicts if v.passed(cfg.judge_threshold))
            self.log(f"AI-judge gate: {passed}/{len(verdicts)} passed "
                     f"(threshold {cfg.judge_threshold})")

        result = BuildResult(timed_beats=timed, verdicts=verdicts, frames_dir=cfg.frames_dir)
        result = self.assemble_fn(cfg, result)
        result = self.compat_fn(cfg, result)
        if result.final_path:
            self.log(f"assembled -> {result.final_path}")

        manifest_path = self.write_manifest_fn(
            cfg,
            result_meta=self._manifest_meta(result),
            out_path=cfg.publish_queue_dir / cfg.video_id / "distribution_manifest.json",
        )
        result.manifest_path = manifest_path
        result.manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
        self.log(f"emitted manifest -> {manifest_path} (now selectable by build_daily_batch.py)")
        return result

    # -- helpers --

    def _judge_items(self, timed: list) -> list:
        items = []
        for i, b in enumerate(timed):
            bid = str(b.get("id", i))
            image = _beat_frame_path(b, i, self.config)
            items.append(rfj.JudgeItem(
                id=bid,
                image=image,
                target_text=str(b.get("text", "")),
                prompt=str(b.get("prompt", "")),
                character_id=b.get("character_id"),
                metadata={"decision": b.get("decision"), "index": i},
            ))
        return items

    def _stub_verdicts(self, items: list) -> list:
        """When judging is skipped, keep each render as-is (best-of == the render)."""
        return [
            rfj.JudgeVerdict(
                id=it.id, score=self.config.judge_threshold, missing=[], wrong=[],
                present=[], suggested_fix="", attempts=0,
                kept_image=str(it.image), kept_prompt=it.prompt,
            )
            for it in items
        ]

    def _manifest_meta(self, result: BuildResult) -> dict:
        primary = [str(b.get("id", i)) for i, b in enumerate(result.timed_beats)]
        return {
            "primary_asset_ids": primary,
            "video_path": str(result.compat_path or result.final_path or ""),
            "n_beats": len(result.timed_beats),
        }


# ───────────────────── distribution manifest emit (W3) ─────────────────────

def emit_distribution_manifest(config: BeatVideoConfig, *, result_meta: dict,
                               out_path: Path) -> Path:
    """Write a publish-queue ``distribution_manifest.json`` (THE W3 missing link).

    Schema matches the canonical writer (``write_metadata.py``) PLUS the routing
    keys ``build_daily_batch.py::discover_queue_items`` reads (brand_id, channel_id,
    content_type, created_at, engagement_score). Once this lands in
    ``artifacts/video/publish_queue/<video_id>/``, the best video finally ENTERS the
    publish queue that build_daily_batch.py selects from → run_upload.py publishes.
    """
    out_path = Path(out_path)
    primary = list(result_meta.get("primary_asset_ids", []))
    provenance_path = f"artifacts/video/provenance/{config.video_id}.json"
    doc = {
        # canonical write_metadata.py fields
        "video_id": config.video_id,
        "plan_id": config.plan_id,
        "config_hash": "",
        "title": config.title,
        "description": config.description,
        "tags": list(config.tags),
        "video_provenance_path": provenance_path,
        "batch_id": config.batch_id,
        "format": config.format,
        "hook_type": "light_reveal",
        "environment": "sacred_narrative",
        "motion_type": "still_sequence",
        "music_mood": "transcendent",
        "caption_pattern": "narrative",
        "style_version": "beat_driven_v1",
        "primary_asset_ids": primary,
        # build_daily_batch.py::discover_queue_items routing/selection keys
        "brand_id": config.brand_id,
        "channel_id": config.channel_id,
        "content_type": config.content_type,
        "platforms": list(config.platforms),
        "engagement_score": 0.5,
        "created_at": datetime.now(timezone.utc).isoformat(),
        # beat-driven provenance
        "pipeline": "beat_driven_v1",
        "source_beats": str(config.beats_path),
        "video_path": result_meta.get("video_path", ""),
        "n_beats": result_meta.get("n_beats", len(primary)),
    }
    write_atomically(out_path, doc)
    return out_path


# ───────────────────────────── CLI ─────────────────────────────

def build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="build_beat_driven",
        description="Canonical beat-driven video builder (Tier-2 local; consumes run_frame_judge).",
    )
    ap.add_argument("--video-id", required=True, help="video / output id (also the queue dir)")
    ap.add_argument("--beats", type=Path, required=True,
                    help="beats source: a .py BEATS module or a beats JSON")
    ap.add_argument("--audio", type=Path, default=None, help="narration WAV/MP3 (for mix)")
    ap.add_argument("--plan-id", default=None)
    ap.add_argument("--brand-id", default="stillness_press")
    ap.add_argument("--channel-id", default="ch_001")
    ap.add_argument("--content-type", default="narrative")
    ap.add_argument("--title", default="")
    ap.add_argument("--description", default="")
    ap.add_argument("--tags", default="", help="comma-separated")
    ap.add_argument("--platforms", default="youtube", help="comma-separated")
    ap.add_argument("--format", default="landscape_16_9")
    ap.add_argument("--artifact-dir", type=Path, default=None)
    ap.add_argument("--frames-dir", type=Path, default=None)
    ap.add_argument("--publish-queue-dir", type=Path, default=DEFAULT_PUBLISH_QUEUE)
    ap.add_argument("--frame-base", type=int, default=DEFAULT_FRAME_BASE)
    # judge passthrough
    ap.add_argument("--threshold", type=int, default=rfj.DEFAULT_THRESHOLD)
    ap.add_argument("--max-retries", type=int, default=rfj.DEFAULT_MAX_RETRIES)
    ap.add_argument("--judge-model", default=rfj.DEFAULT_JUDGE_MODEL)
    ap.add_argument("--rewriter-model", default=rfj.DEFAULT_REWRITER_MODEL)
    ap.add_argument("--ollama-url", default=None)
    ap.add_argument("--comfyui-url", default=None,
                    help="ComfyUI base url; omit to skip rendering (frames must pre-exist)")
    # structure-only seams (CI / no-GPU)
    ap.add_argument("--skip-render", action="store_true",
                    help="never call ComfyUI (frames must already exist on disk)")
    ap.add_argument("--skip-judge", action="store_true",
                    help="skip the AI-judge gate (keep renders as-is)")
    ap.add_argument("--skip-assemble", action="store_true",
                    help="skip ffmpeg assemble/compat (manifest-only / CI)")
    ap.add_argument("--manifest-only", action="store_true",
                    help="shortcut for --skip-render --skip-judge --skip-assemble")
    return ap


def config_from_args(args) -> BeatVideoConfig:
    if args.manifest_only:
        args.skip_render = args.skip_judge = args.skip_assemble = True
    return BeatVideoConfig(
        video_id=args.video_id,
        beats_path=args.beats,
        audio_path=args.audio,
        plan_id=args.plan_id,
        brand_id=args.brand_id,
        channel_id=args.channel_id,
        content_type=args.content_type,
        title=args.title,
        description=args.description,
        tags=[t.strip() for t in args.tags.split(",") if t.strip()],
        platforms=[p.strip() for p in args.platforms.split(",") if p.strip()],
        format=args.format,
        artifact_dir=args.artifact_dir,
        frames_dir=args.frames_dir,
        publish_queue_dir=args.publish_queue_dir,
        frame_base=args.frame_base,
        judge_threshold=args.threshold,
        judge_max_retries=args.max_retries,
        judge_model=args.judge_model,
        rewriter_model=args.rewriter_model,
        ollama_url=args.ollama_url,
        comfyui_url=args.comfyui_url,
        skip_render=args.skip_render,
        skip_judge=args.skip_judge,
        skip_assemble=args.skip_assemble,
    )


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    config = config_from_args(args)
    print(f"[build_beat_driven] video={config.video_id} beats={config.beats_path.name} "
          f"render={'off' if config.skip_render else 'on'} "
          f"judge={'off' if config.skip_judge else 'on'} "
          f"assemble={'off' if config.skip_assemble else 'on'}", file=sys.stderr, flush=True)
    builder = BeatDrivenBuilder(
        config,
        progress=lambda m: print(f"[build_beat_driven] {m}", file=sys.stderr, flush=True),
    )
    result = builder.build()
    print(json.dumps({
        "video_id": config.video_id,
        "beats": len(result.timed_beats),
        "kept_frames": len(result.kept_frames),
        "silent": str(result.silent_path) if result.silent_path else None,
        "final": str(result.final_path) if result.final_path else None,
        "compat": str(result.compat_path) if result.compat_path else None,
        "manifest": str(result.manifest_path),
        "enters_publish_queue": True,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
