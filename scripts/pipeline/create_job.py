#!/usr/bin/env python3
"""Create job.json for any Phoenix pipeline (see config/pipeline_registry.yaml)."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

from scripts.pipeline._job_io import (
    iso_now,
    job_file,
    load_registry,
    registry_path,
    stages_from_registry,
    write_job_atomic,
)
from scripts.pipeline._paths import REPO_ROOT


def _slug(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9_]+", "-", s.strip()).strip("-").lower()
    return s or "job"


def _load_voice_map() -> dict[str, Any]:
    try:
        import yaml
    except ImportError as e:
        raise SystemExit("PyYAML required: pip install pyyaml") from e
    p = REPO_ROOT / "config" / "tts" / "brand_narrator_voice_map.yaml"
    if not p.exists():
        return {}
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    return data if isinstance(data, dict) else {}


def resolve_voice_id(brand: str, locale: str, explicit: str | None) -> str:
    if explicit:
        return explicit
    loc_key = locale.replace("-", "_").lower()
    data = _load_voice_map()
    block = data.get(loc_key) or data.get("en_us") or {}
    if not isinstance(block, dict):
        return ""
    row = block.get(brand)
    if not isinstance(row, dict):
        return ""
    return str(row.get("elevenlabs_id") or row.get("cosyvoice2_id") or "")


def main() -> int:
    reg = load_registry()
    pipelines = reg.get("pipelines") or {}
    ap = argparse.ArgumentParser(description="Create pipeline job.json")
    ap.add_argument(
        "--pipeline",
        required=True,
        choices=sorted(pipelines.keys()) or ["video", "ebook", "manga", "podcast", "audiobook"],
    )
    ap.add_argument("--workspace", type=Path, required=True)
    ap.add_argument("--teacher", default=None)
    ap.add_argument("--topic", default=None)
    ap.add_argument("--brand", default=None)
    ap.add_argument("--locale", default="en-US")
    ap.add_argument("--format", default=None, help="Video format key (short|mid|long|...)")
    ap.add_argument("--persona", default=None)
    ap.add_argument("--arc", type=Path, default=None, help="Master arc YAML (ebook)")
    ap.add_argument("--genre", default=None, help="Manga genre / style archetype")
    ap.add_argument("--brand-id", dest="brand_id", default=None, help="Podcast brand id")
    ap.add_argument("--week", default=None, help="Podcast week id")
    ap.add_argument("--book-dir", type=Path, default=None)
    ap.add_argument("--voice-id", dest="voice_id", default=None)
    args = ap.parse_args()

    pipe_cfg = pipelines.get(args.pipeline)
    if not pipe_cfg:
        print(f"Unknown pipeline {args.pipeline!r}. Edit {registry_path()}", file=sys.stderr)
        return 1

    required = list(pipe_cfg.get("required_params") or [])
    params: dict[str, Any] = {}
    if args.teacher:
        params["teacher"] = args.teacher
    if args.topic:
        params["topic"] = args.topic
    if args.brand:
        params["brand"] = args.brand
    if args.locale:
        params["locale"] = args.locale
    if args.format:
        params["format"] = args.format
    if args.persona:
        params["persona"] = args.persona
    if args.arc:
        params["arc_path"] = str(args.arc.resolve())
    if args.genre:
        params["genre"] = args.genre
    if args.brand_id:
        params["brand_id"] = args.brand_id
    if args.week:
        params["week"] = args.week
    if args.book_dir:
        params["book_dir"] = str(args.book_dir.resolve())

    brand_for_voice = params.get("brand") or params.get("brand_id") or ""
    vid = resolve_voice_id(str(brand_for_voice), str(params.get("locale") or "en-US"), args.voice_id)
    if vid:
        params["voice_id"] = vid
    elif args.voice_id:
        params["voice_id"] = args.voice_id

    missing = [k for k in required if not params.get(k)]
    if missing:
        print(f"Missing required params for pipeline '{args.pipeline}': {', '.join(missing)}", file=sys.stderr)
        print("Required by registry:", ", ".join(required), file=sys.stderr)
        return 1

    if args.pipeline == "ebook" and not params.get("teacher"):
        params["teacher"] = "default_teacher"

    guide = str(pipe_cfg.get("guide") or "")
    stages = stages_from_registry(pipe_cfg)
    job_id = (
        f"job-{_slug(str(params.get('teacher') or 'na'))}-"
        f"{_slug(str(params.get('topic') or params.get('persona') or 'run'))}-"
        f"{args.pipeline}-{_slug(iso_now()[:10])}"
    )

    ws = args.workspace.resolve()
    ws.mkdir(parents=True, exist_ok=True)
    job = {
        "schema_version": 1,
        "job_id": job_id,
        "pipeline": args.pipeline,
        "created": iso_now(),
        "guide_path": guide,
        "guide_acknowledged": False,
        "workspace": str(ws),
        "params": params,
        "stages": [
            {"name": s["name"], "status": None, "output": None, "ts": None} for s in stages
        ],
    }
    if job_file(ws).exists():
        print(f"Refusing to overwrite existing {job_file(ws)}", file=sys.stderr)
        return 1
    write_job_atomic(ws, job)
    print(f"Job created: {job_id}")
    print(f"Workspace: {ws}")
    print(f"Guide: {REPO_ROOT / guide}")
    print("Next: acknowledge the guide, then run stages in order:")
    print(f"  PYTHONPATH=. python3 scripts/pipeline/acknowledge_guide.py --workspace {ws}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
