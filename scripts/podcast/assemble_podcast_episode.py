#!/usr/bin/env python3
"""
Assemble podcast episode plan: book artifacts + podcast_format.yaml → assembly JSON.

See docs/PODCAST_PIPELINE_INTEGRATION_SPEC.md Gap 7a.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.podcast._lib import (  # noqa: E402
    atoms_by_type,
    episode_id_for,
    format_structure,
    load_video_plan,
    load_yaml,
    norm_locale,
    resolve_voice_config,
    segment_music_profile,
    stable_guid,
)
from scripts.music.select_and_edit import select_track  # noqa: E402


ATOM_MAP = {
    "cold_open": "HOOK",
    "scene_setting": "SCENE",
    "teaching": "REFLECTION",
    "story": "STORY",
    "guided_practice": "EXERCISE",
    "integration": "INTEGRATION",
    "thread_forward": "THREAD",
}


def _midpoint(r: list) -> float:
    if not r or len(r) < 2:
        return 60.0
    return (float(r[0]) + float(r[1])) / 2.0


def _scale_durations(
    segments: list[dict[str, Any]], target_total: float
) -> None:
    mids = [float(s.get("duration_target_s") or 0) for s in segments]
    ssum = sum(mids) or 1.0
    factor = target_total / ssum
    for s in segments:
        s["duration_target_s"] = max(15.0, round(float(s["duration_target_s"]) * factor, 1))


def build_segments_for_format(
    fmt: str,
    atoms: dict[str, str],
    topic: str,
    brand_id: str,
    locale: str,
) -> list[dict[str, Any]]:
    spec = format_structure(fmt)
    segdefs = spec.get("segments") or []
    out: list[dict[str, Any]] = []

    if fmt == "podcast_short":
        text_hook = atoms.get("HOOK", "")[:1200]
        body = atoms.get("EXERCISE") or atoms.get("REFLECTION") or atoms.get("STORY", "")
        body = body[:8000]
        order = [
            ("cold_open", "HOOK", text_hook),
            ("theme_intro", None, ""),
            ("guided_practice", "EXERCISE", body),
            ("outro", None, ""),
        ]
        for seg_name, _atom, txt in order:
            if seg_name == "theme_intro":
                txt = "Episode breve. Práctica guiada."
            elif seg_name == "outro":
                txt = "Gracias por escuchar. Hasta la próxima."
            music_meta = None
            role, mood = segment_music_profile("guided_practice", topic)
            tr = select_track(topic=topic, mood=mood, brand=brand_id, energy="low")
            if tr:
                music_meta = {"track": tr, "role": role, "level_db": -18.0}
            dur = 45.0 if seg_name in ("cold_open", "theme_intro", "outro") else 150.0
            out.append(
                {
                    "segment_id": seg_name,
                    "source_atom": _atom or "NONE",
                    "text": txt,
                    "duration_target_s": dur,
                    "music_cue": music_meta,
                }
            )
        return out

    # podcast_episode, podcast_trailer, podcast_sleep
    for sd in segdefs:
        seg_name = sd.get("segment")
        src_atom = sd.get("source_atom")
        if seg_name in ("theme_intro", "outro", "sleep_intro"):
            series_hint = "Serie Phoenix Omega"
            if seg_name == "theme_intro":
                text = f"{series_hint}. Episodio de bienestar y regulación del sistema nervioso."
            elif seg_name == "sleep_intro":
                text = "Te damos la bienvenida. Deja que el cuerpo se afiance, sin prisa."
            else:
                text = (
                    "Gracias por acompañarnos. Suscríbete para el próximo episodio. "
                    "Este programa es educativo y no sustituye atención profesional."
                )
            music = sd.get("music")
            tr = None
            if music:
                tr = select_track(topic=topic, mood="calm", brand=brand_id, energy="low")
            out.append(
                {
                    "segment_id": seg_name,
                    "source_atom": "NONE",
                    "text": text,
                    "duration_target_s": _midpoint(sd.get("duration_range_s") or [15, 30]),
                    "music_cue": {"track": tr, "role": str(music), "level_db": -18.0} if tr else None,
                }
            )
            continue

        key = src_atom if isinstance(src_atom, str) else None
        if key and key != "null":
            key = key.upper()
        text = atoms.get(key or "", "") if key else ""

        if seg_name in ("sleep_soundscape_open", "sleep_fade") and not key:
            text = ""
        if seg_name == "sleep_fade" and not text:
            text = (
                "Inhala, suave. Exhala, más lento. El sonido continúa. "
                "No hace falta seguir las palabras."
            )

        if seg_name == "scene_setting" and not text:
            st = atoms.get("STORY", "")
            text = st[: min(800, len(st))]

        if not text and seg_name == "thread_forward":
            continue

        if not text and seg_name not in ("cold_open", "sleep_soundscape_open"):
            continue

        dr = _midpoint(sd.get("duration_range_s") or [60, 120])
        music_meta = None
        mspec = sd.get("music")
        if mspec:
            if "sleep" in str(seg_name):
                tr = select_track(topic=topic, mood="calm", brand=brand_id, energy="low")
                if tr:
                    music_meta = {"track": tr, "role": "sleep_ambient", "level_db": -20.0}
            else:
                role, mood = segment_music_profile(str(seg_name), topic)
                tr = select_track(topic=topic, mood=mood, brand=brand_id, energy="low")
                if tr:
                    music_meta = {"track": tr, "role": role, "level_db": -18.0}

        out.append(
            {
                "segment_id": seg_name,
                "source_atom": key or "NONE",
                "text": text,
                "duration_target_s": dr,
                "music_cue": music_meta,
            }
        )

    pf = load_yaml(REPO_ROOT / "config" / "podcast" / "podcast_format.yaml")
    fmt_def = (pf.get("formats") or {}).get(fmt) or {}
    dmin, dmax = fmt_def.get("duration_range_s") or [900, 1500]
    target = (float(dmin) + float(dmax)) / 2.0
    if fmt == "podcast_trailer":
        target = _midpoint(fmt_def.get("duration_range_s") or [180, 300])
    _scale_durations(out, target)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Assemble podcast episode JSON")
    ap.add_argument("--book-dir", type=Path, required=True)
    ap.add_argument("--brand-id", required=True)
    ap.add_argument("--locale", required=True)
    ap.add_argument("--format", dest="fmt", required=True)
    ap.add_argument("--week", default="2026-W15")
    ap.add_argument("--series-title", default="The Room Full of People")
    ap.add_argument("--series-slug", default="social_anxiety_arc")
    ap.add_argument("--episode-number", type=int, default=1)
    ap.add_argument("--season-number", type=int, default=1)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()

    book_dir = args.book_dir.resolve()
    plan = load_video_plan(book_dir)
    atoms = atoms_by_type(plan)
    teacher_id = plan.get("teacher_id") or "unknown"
    topic = plan.get("topic") or "anxiety"
    locale = norm_locale(args.locale)

    segments = build_segments_for_format(args.fmt, atoms, topic, args.brand_id, locale)
    voice_config = resolve_voice_config(teacher_id, args.brand_id, locale)

    ep_id = episode_id_for(teacher_id, topic, locale, args.week, args.fmt, args.series_slug)
    assembly = {
        "schema_version": 1,
        "episode_id": ep_id,
        "guid": stable_guid(ep_id),
        "brand_id": args.brand_id,
        "locale": locale,
        "week": args.week,
        "format": args.fmt,
        "teacher_id": teacher_id,
        "topic": topic,
        "series_title": args.series_title,
        "series_slug": args.series_slug,
        "episode_number": args.episode_number,
        "season_number": args.season_number,
        "teacher_name": plan.get("title", "Teacher"),
        "segments": segments,
        "voice_config": voice_config,
        "duration_targets": {s["segment_id"]: s["duration_target_s"] for s in segments},
        "metadata": {
            "title": f"{args.series_title} — {topic.replace('_', ' ').title()}",
            "description": plan.get("title") or args.series_title,
            "explicit": "no",
        },
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    out_path = args.output_dir / f"assembly_{ep_id}.json"
    out_path.write_text(json.dumps(assembly, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
