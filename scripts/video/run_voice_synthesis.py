#!/usr/bin/env python3
"""
Stage 14b — Voice Synthesis: soundtrack_plan.json -> per-segment narration audio (WAV).

REUSES the audiobook/podcast TTS path (free/local only). NEVER ElevenLabs as an
active code path. Concretely it wraps:
  - scripts/podcast/_lib.resolve_voice_config  (provider stack from locale_voice_routing)
  - scripts/podcast/render_podcast_audio.synth_speech  (CosyVoice2 / Edge-TTS -> 44.1k mono WAV)

Provider routing (forced free):
  - CJK locales (ja/ko/zh*): CosyVoice2 on Pearl Star (COSYVOICE_URL), Edge-TTS fallback.
  - EN / EU / LATAM locales: Edge-TTS (free Microsoft). Piper may be wired later via
    the same synth primitive; ElevenLabs is explicitly DISABLED here even if a key is set.

The video pipeline (scripts/video/run_pipeline.py) calls this with the soundtrack_plan
and an output dir; on success it reads back `<out_dir>/soundtrack_plan_with_audio.json`,
which is this script's primary product: the input plan with a real `audio_path` (and
measured `audio_duration_s`) stitched onto each narration segment.

Usage:
  python scripts/video/run_voice_synthesis.py <soundtrack_plan.json> -o <out_dir> \
      [--locale en-US] [--provider auto|edge_tts|cosyvoice2] [--music] [--force] [--dry-run] \
      [--voice-bank MANIFEST.tsv]

Exit 0 on success (or dry-run). Exit 1 if no segment could be synthesized.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

# REUSE the existing free/local TTS primitives — do NOT reimplement synthesis.
from scripts.podcast._lib import norm_locale, resolve_voice_config  # noqa: E402
from scripts.podcast.render_podcast_audio import (  # noqa: E402
    probe_duration,
    synth_speech,
)

# Providers that cost money / are paid-cloud. NEVER allowed as an active code path here.
_BANNED_PROVIDERS = {"elevenlabs", "openai"}
_DEFAULT_VOICE_BANK = (
    REPO_ROOT / "artifacts" / "social_media_voice_bank_2026-07-19" / "MANIFEST.tsv"
)


def _force_free_provider(vc: dict, override: str | None) -> dict:
    """Return a voice-config whose provider is guaranteed free/local.

    resolve_voice_config() returns provider=elevenlabs for EN primary markets. The video
    pipeline must run unattended (Tier 2) and free, so we down-route any banned provider
    to Edge-TTS (or honor an explicit --provider override). CJK stays on CosyVoice2.
    """
    vc = dict(vc)
    if override and override != "auto":
        vc["provider"] = override
        return vc
    if (vc.get("provider") or "").lower() in _BANNED_PROVIDERS:
        # Edge-TTS is the free fallback for every locale; synth_speech will use
        # vc["edge_fallback"] as the voice id.
        vc["provider"] = "edge_tts"
    return vc


def _segment_text(seg: dict) -> str:
    return (seg.get("speakable_text") or seg.get("text") or "").strip()


def _apply_voice_bank_hit(seg: dict, hit, out_dir: Path, force: bool) -> bool:
    """Attach bank MP3 + speakable_text. Returns True on success."""
    seg_id = str(seg.get("segment_id") or "seg")
    dest = out_dir / f"narration_{seg_id}_voice_bank{Path(hit.local_mp3).suffix}"
    if (not dest.exists() or force) and hit.local_mp3 is not None:
        shutil.copy2(hit.local_mp3, dest)
    if not dest.exists():
        return False
    seg["text"] = hit.speakable_text
    seg["speakable_text"] = hit.speakable_text
    seg["primary_atom_id"] = hit.atom_id
    seg["audio_path"] = str(dest.relative_to(REPO_ROOT)) if _under_repo(dest) else str(dest)
    try:
        seg["audio_duration_s"] = probe_duration(dest)
    except Exception:
        seg["audio_duration_s"] = None
    seg["audio_provider"] = "social_voice_bank"
    seg["audio_status"] = "ok"
    seg["voice_bank_r2_key"] = hit.r2_key
    seg["voice_id"] = hit.voice_id
    return True


def synthesize_plan(
    plan: dict,
    out_dir: Path,
    locale: str,
    provider_override: str | None,
    force: bool,
    dry_run: bool,
    voice_bank: Path | None = None,
    allow_live_fallback: bool = False,
    allow_r2_download: bool = False,
) -> tuple[dict, int, int]:
    """Synthesize every narration segment. Returns (plan_with_audio, n_ok, n_total)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    loc = norm_locale(locale)

    bank_index = None
    if voice_bank is not None:
        from scripts.social_media.voice_bank_lookup import load_index

        bank_index = load_index(voice_bank, allow_r2_download=allow_r2_download)

    # Resolve a free voice stack once for this plan's locale. teacher_id/brand_id are not
    # carried on soundtrack_plan, so use the channel as a stable cache key for narrator
    # assignment lookup (falls back cleanly to the locale default voice).
    channel_id = str(plan.get("channel_id") or "ch_001")
    vc = resolve_voice_config(teacher_id=channel_id, brand_id="", locale=loc)
    vc = _force_free_provider(vc, provider_override)

    segments = plan.get("narration_segments") or []
    n_ok = 0
    n_bank = 0
    n_fallback = 0
    n_miss = 0
    for seg in segments:
        seg_id = str(seg.get("segment_id") or f"seg-{segments.index(seg)+1}")
        atom_id = (seg.get("primary_atom_id") or "").strip()

        if bank_index is not None and atom_id and not atom_id.startswith("html-"):
            try:
                hit = bank_index.resolve(atom_id, require_audio=not dry_run)
            except Exception as e:  # VoiceBankError or missing file
                print(
                    f"WARNING: voice-bank miss for {atom_id}: {e}",
                    file=sys.stderr,
                )
                n_miss += 1
                if not allow_live_fallback:
                    seg["audio_path"] = None
                    seg["audio_provider"] = "social_voice_bank"
                    seg["audio_status"] = "bank_miss"
                    continue
                # fall through to live synth — do not silent-substitute wrong text
            else:
                seg["speakable_text"] = hit.speakable_text
                seg["text"] = hit.speakable_text
                if dry_run:
                    seg["audio_path"] = str(hit.local_mp3) if hit.local_mp3 else None
                    seg["audio_provider"] = "social_voice_bank"
                    seg["audio_status"] = "dry_run"
                    n_ok += 1
                    n_bank += 1
                    continue
                if _apply_voice_bank_hit(seg, hit, out_dir, force):
                    n_ok += 1
                    n_bank += 1
                    continue
                print(
                    f"WARNING: voice-bank copy failed for {atom_id}",
                    file=sys.stderr,
                )
                n_miss += 1
                if not allow_live_fallback:
                    seg["audio_path"] = None
                    seg["audio_provider"] = "social_voice_bank"
                    seg["audio_status"] = "bank_miss"
                    continue

        if bank_index is not None and not allow_live_fallback:
            # Bank-only mode: never silent-substitute live TTS for a different text.
            if not seg.get("audio_path"):
                seg["audio_path"] = None
                seg["audio_provider"] = "social_voice_bank"
                seg["audio_status"] = seg.get("audio_status") or "bank_only_no_hit"
            continue

        text = _segment_text(seg)
        if not text:
            seg["audio_path"] = None
            seg["audio_status"] = "empty_text"
            continue
        out_wav = out_dir / f"narration_{seg_id}.wav"
        if out_wav.exists() and not force and not dry_run:
            seg["audio_path"] = str(out_wav.relative_to(REPO_ROOT)) if _under_repo(out_wav) else str(out_wav)
            seg["audio_duration_s"] = probe_duration(out_wav)
            seg["audio_provider"] = vc.get("provider")
            seg["audio_status"] = "cached"
            n_ok += 1
            if bank_index is not None:
                n_fallback += 1
            continue
        ok = synth_speech(text, vc, out_wav, dry_run=dry_run)
        if dry_run:
            seg["audio_path"] = str(out_wav)
            seg["audio_provider"] = vc.get("provider")
            seg["audio_status"] = "dry_run"
            n_ok += 1
            if bank_index is not None:
                n_fallback += 1
            continue
        if ok and out_wav.exists():
            seg["audio_path"] = str(out_wav.relative_to(REPO_ROOT)) if _under_repo(out_wav) else str(out_wav)
            seg["audio_duration_s"] = probe_duration(out_wav)
            seg["audio_provider"] = vc.get("provider")
            seg["audio_status"] = "ok"
            n_ok += 1
            if bank_index is not None:
                n_fallback += 1
                print(
                    f"WARNING: live-synth fallback for segment {seg_id} "
                    f"(atom_id={atom_id or 'none'}) — captions must match synth text",
                    file=sys.stderr,
                )
        else:
            seg["audio_path"] = None
            seg["audio_provider"] = vc.get("provider")
            seg["audio_status"] = "failed"

    plan["voice_synthesis"] = {
        "locale": loc,
        "provider": ("social_voice_bank" if n_bank and not n_fallback else vc.get("provider")),
        "edge_fallback": vc.get("edge_fallback"),
        "segments_total": len(segments),
        "segments_synthesized": n_ok,
        "voice_bank_hits": n_bank,
        "voice_bank_misses": n_miss,
        "live_fallback_hits": n_fallback,
        "voice_bank_manifest": str(voice_bank) if voice_bank else None,
        "dry_run": bool(dry_run),
        "elevenlabs_used": False,
    }
    return plan, n_ok, len(segments)


def _under_repo(p: Path) -> bool:
    try:
        p.resolve().relative_to(REPO_ROOT)
        return True
    except ValueError:
        return False


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Stage 14b — Voice Synthesis (free/local TTS; wraps audiobook/podcast path)"
    )
    ap.add_argument("soundtrack_plan", help="Path to soundtrack_plan.json (from Stage 14)")
    ap.add_argument("-o", "--out-dir", required=True, help="Output dir for narration WAVs + plan_with_audio")
    ap.add_argument("--locale", default="en-US", help="Locale for voice routing (e.g. en-US, ja-JP, zh-TW)")
    ap.add_argument(
        "--provider",
        default="auto",
        choices=("auto", "edge_tts", "cosyvoice2"),
        help="Force a free provider; 'auto' uses locale routing (ElevenLabs is always down-routed to free).",
    )
    ap.add_argument("--music", action="store_true", help="Accepted for pipeline-flag parity; music bed is handled by the soundtrack/music-bank stage, not here.")
    ap.add_argument("--force", action="store_true", help="Re-synthesize even if a WAV already exists")
    ap.add_argument("--dry-run", action="store_true", help="Plan/log only; do not call TTS or write audio")
    ap.add_argument(
        "--voice-bank",
        nargs="?",
        const=str(_DEFAULT_VOICE_BANK),
        default=None,
        help=(
            "Prefer CosyVoice social MP3 bank (MANIFEST.tsv). "
            f"Optional path; bare flag defaults to {_DEFAULT_VOICE_BANK}"
        ),
    )
    ap.add_argument(
        "--allow-live-fallback",
        action="store_true",
        help="On bank miss, fall back to Edge-TTS/CosyVoice live synth (logged; never silent wrong text)",
    )
    ap.add_argument(
        "--allow-r2-download",
        action="store_true",
        help="If local bank MP3 missing, download from R2 (needs integration env)",
    )
    args = ap.parse_args()

    plan_path = Path(args.soundtrack_plan)
    if not plan_path.is_file():
        print(f"Error: soundtrack plan not found: {plan_path}", file=sys.stderr)
        return 1
    try:
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
    except Exception as e:  # pragma: no cover - defensive
        print(f"Error: could not parse {plan_path}: {e}", file=sys.stderr)
        return 1

    voice_bank = Path(args.voice_bank) if args.voice_bank else None
    # Pipeline passes --voice with --voice-bank → allow live fallback on miss
    allow_live = bool(args.allow_live_fallback)

    out_dir = Path(args.out_dir)
    plan, n_ok, n_total = synthesize_plan(
        plan=plan,
        out_dir=out_dir,
        locale=args.locale,
        provider_override=args.provider,
        force=args.force,
        dry_run=args.dry_run,
        voice_bank=voice_bank,
        allow_live_fallback=allow_live,
        allow_r2_download=bool(args.allow_r2_download),
    )

    # Primary product the video pipeline reads back.
    out_plan = out_dir / "soundtrack_plan_with_audio.json"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_plan.write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")
    vs = plan["voice_synthesis"]
    print(
        f"Voice synthesis: {n_ok}/{n_total} segments "
        f"(provider={vs['provider']}, bank_hits={vs.get('voice_bank_hits', 0)}, "
        f"misses={vs.get('voice_bank_misses', 0)}) -> {out_plan}"
    )

    if args.dry_run:
        return 0
    # Success if at least one non-empty segment produced audio, or there was nothing to do.
    nonempty = sum(1 for s in (plan.get("narration_segments") or []) if _segment_text(s))
    if nonempty == 0:
        return 0
    return 0 if n_ok > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
