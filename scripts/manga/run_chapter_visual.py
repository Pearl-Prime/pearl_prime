#!/usr/bin/env python3
"""Compile chapter_script (writer handoff) JSON into panel_prompts + optional panel_images_manifest.

  PYTHONPATH=. python3 scripts/manga/run_chapter_visual.py chapter_script.json \\
    -o panel_prompts.json [--manifest-out manifest.json] [--backend noop|replay] [--replay-map paths.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.manga.chapter.visual_from_script import compile_panel_prompts_from_chapter_script
from phoenix_v4.manga.image_backend import (
    FixtureReplayImageBackend,
    NoopImageBackend,
    build_panel_images_manifest,
)
from phoenix_v4.manga.style_resolution import resolve_style_id
from scripts.manga._config import config_snapshot_hash, write_atomically


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Compile chapter_script writer handoff into panel_prompts (+ optional manifest)"
    )
    ap.add_argument("chapter_script", type=Path, help="Path to chapter_script_writer_handoff JSON")
    ap.add_argument("-o", "--out", required=True, type=Path, help="Output panel_prompts.json")
    ap.add_argument("--manifest-out", type=Path, help="Output panel_images_manifest.json")
    ap.add_argument(
        "--backend",
        choices=("noop", "replay"),
        default="noop",
        help="Image backend for manifest (default noop)",
    )
    ap.add_argument(
        "--replay-map",
        type=Path,
        help="JSON map panel_id -> relative image path (for --backend replay)",
    )
    ap.add_argument(
        "--style-id",
        default=None,
        help="Explicit style archetype id. Omit to resolve via the authority "
        "chain in phoenix_v4.manga.style_resolution (genre/teacher/format "
        "signal, falling back to grounded_realism).",
    )
    ap.add_argument("--teacher-id", default="ahjan")
    args = ap.parse_args()

    path = args.chapter_script
    if not path.exists():
        print(f"Error: not found: {path}", file=sys.stderr)
        return 1

    raw = json.loads(path.read_text(encoding="utf-8"))
    if raw.get("artifact_type") != "chapter_script_writer_handoff":
        print(
            "Warning: expected artifact_type chapter_script_writer_handoff",
            file=sys.stderr,
        )

    resolved_style_id, style_source = resolve_style_id(
        explicit_override=args.style_id,
        chapter_script=raw,
        teacher_id=args.teacher_id,
        genre_id=raw.get("genre") or raw.get("genre_id"),
    )
    print(f"style_id={resolved_style_id} (source={style_source})", file=sys.stderr)

    snap = config_snapshot_hash()
    doc = compile_panel_prompts_from_chapter_script(
        raw,
        series_id=raw.get("series_id"),
        chapter_id=raw.get("chapter_id"),
        config_hash=snap,
        style_id=resolved_style_id,
        teacher_id=args.teacher_id,
    )
    write_atomically(args.out, doc)
    print(f"Wrote {len(doc['panels'])} panel prompts to {args.out}")

    if args.manifest_out:
        if args.backend == "noop":
            backend = NoopImageBackend()
        else:
            if not args.replay_map or not args.replay_map.exists():
                print("--replay-map required for replay backend", file=sys.stderr)
                return 1
            backend = FixtureReplayImageBackend.from_json_file(args.replay_map)
        gen = backend.generate(doc)
        manifest = build_panel_images_manifest(doc, gen)
        write_atomically(args.manifest_out, manifest)
        print(f"Wrote manifest ({len(manifest['panels'])} panels) to {args.manifest_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
