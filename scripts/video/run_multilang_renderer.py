#!/usr/bin/env python3
"""
Stage 16 — Multi-Language Renderer: soundtrack_plan + platform_variants + captions -> multilang_plan.json.
VCE §9: per-locale TTS call specs, subtitle types, cultural flags (no API calls).
Usage: python scripts/video/run_multilang_renderer.py <soundtrack_plan.json> <platform_variants.json> <captions.json> -o multilang_plan.json [--languages en,zh-CN]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.video._config import config_snapshot_hash, load_json, load_yaml, should_skip_output, write_atomically


def run_multilang(
    soundtrack: dict,
    platforms_doc: dict,
    captions: dict,
    languages: list[str],
) -> dict:
    cfg = load_yaml("config/video/multilang_config.yaml")
    cultural = cfg.get("cultural_metaphor_flags") or {}
    instruments = cfg.get("locale_instruments") or {}
    fonts = cfg.get("font_by_script") or {}
    sub_by_plat = cfg.get("subtitle_types_by_platform") or {}

    plan_id = soundtrack.get("plan_id") or platforms_doc.get("plan_id")
    base_calls = soundtrack.get("elevenlabs_api_calls") or []

    locales = []
    for lang in languages:
        inst = instruments.get(lang) or instruments.get(lang.split("-")[0], instruments.get("en", []))
        loc = {
            "locale": lang,
            "cultural_metaphor_flags": cultural.get(lang, {}),
            "instrument_additions": inst,
            "subtitle_font_hint": fonts.get("latin") if lang == "en" else fonts.get("cjk", fonts.get("latin")),
            "tts_call_specs": [],
            "subtitle_artifacts": [],
        }
        for call in base_calls:
            loc["tts_call_specs"].append({
                **call,
                "params": {**(call.get("params") or {}), "language_code": lang, "voice_clone_hint": f"{soundtrack.get('channel_id','ch_001')}_{lang}"},
                "expected_output": {"path": f"artifacts/audio/{plan_id}/narration_{lang}_placeholder.mp3"},
            })
        for var in platforms_doc.get("variants") or []:
            plat = var.get("platform", "")
            for st in sub_by_plat.get(plat, ["srt"]):
                ext = "ass" if st in ("ass", "burnt_in") else "srt"
                loc["subtitle_artifacts"].append({
                    "platform": plat,
                    "type": st,
                    "path": f"artifacts/subs/{plan_id}/{lang}_{plat}.{ext}",
                })
        locales.append(loc)

    return {
        "plan_id": plan_id,
        "config_hash": config_snapshot_hash(),
        "languages": languages,
        "locales": locales,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="VCE Stage 16 — Multi-language plan")
    ap.add_argument("soundtrack_plan")
    ap.add_argument("platform_variants")
    ap.add_argument("captions")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--languages", default="en", help="Comma-separated BCP-47 style codes")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--workspace", type=str, default=None, help="Directory containing job.json (default: parent of --out)")
    ap.add_argument("--no-job-check", dest="no_job_check", action="store_true", help="Skip job.json enforcement (CI only)")
    args = ap.parse_args()
    if args.no_job_check:
        print("WARNING: --no-job-check: pipeline job enforcement disabled (CI/testing only).", file=sys.stderr)
    from scripts.pipeline._video_workspace import resolve_video_workspace
    from scripts.pipeline.advance_stage import mark_complete, mark_failed
    from scripts.pipeline.check_job import require_stage

    ws = resolve_video_workspace(args, out_attr="out")
    if not args.no_job_check:
        require_stage("multilang", ws)

    paths = [Path(args.soundtrack_plan), Path(args.platform_variants), Path(args.captions)]
    if not all(p.exists() for p in paths):
        if not args.no_job_check:
            mark_failed(ws, "multilang", error="input not found")
        print("Error: input not found", file=sys.stderr)
        return 1
    ss, pv, cap = load_json(paths[0]), load_json(paths[1]), load_json(paths[2])
    langs = [x.strip() for x in args.languages.split(",") if x.strip()]
    out = Path(args.out)
    h = config_snapshot_hash()
    if should_skip_output(out, ["plan_id", "locales", "config_hash"], args.force, h):
        print(f"Skip (exists): {out}")
        if not args.no_job_check:
            mark_complete(ws, "multilang", output=out.name)
        return 0
    doc = run_multilang(ss, pv, cap, langs)
    write_atomically(out, doc)
    print(f"Wrote multilang_plan for {len(langs)} languages to {out}")
    if not args.no_job_check:
        mark_complete(ws, "multilang", output=out.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
