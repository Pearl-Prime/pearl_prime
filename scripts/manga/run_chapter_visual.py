#!/usr/bin/env python3
"""Compile chapter_script (writer handoff) JSON into panel_prompts + optional panel_images_manifest.

  PYTHONPATH=. python3 scripts/manga/run_chapter_visual.py chapter_script.json \\
    -o panel_prompts.json [--manifest-out manifest.json] [--backend noop|replay] [--replay-map paths.json] \\
    [--arc-storyboard artifacts/manga/arc_storyboards/<series>/<ep>.arc_storyboard.yaml] \\
    [--assembly-hints-out assembly_layer_hints.json]

With --arc-storyboard the storyboard is the page/panel authority
(MANGA_ARC_STORYBOARD_CONTRACT.md §"Storyboard consumption"): panel count,
ordering, and prompt scaffolds come from the board; the script supplies
dialogue; count divergences are WARN rows (storyboard wins — OPD-154).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.manga.chapter.visual_from_script import (
    build_assembly_layer_hints,
    compile_panel_prompts_from_chapter_script,
)
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
    ap.add_argument(
        "--arc-storyboard",
        type=Path,
        help="Path to an arc_storyboard_plan (YAML or JSON). When set, the "
        "storyboard drives panel count/ordering/prompt scaffolds; the script "
        "supplies dialogue (MANGA_ARC_STORYBOARD_CONTRACT.md).",
    )
    ap.add_argument(
        "--assembly-hints-out",
        type=Path,
        help="Write assembly_layer_hints JSON derived from the storyboard's "
        "layer_picks (requires --arc-storyboard). Missing bank assets become "
        "flagged INTERIM placeholder rows + demand-gap rows, never dropped.",
    )
    args = ap.parse_args()

    path = args.chapter_script
    if not path.exists():
        print(f"Error: not found: {path}", file=sys.stderr)
        return 1
    if args.assembly_hints_out and not args.arc_storyboard:
        print("--assembly-hints-out requires --arc-storyboard", file=sys.stderr)
        return 1

    arc_storyboard = None
    if args.arc_storyboard:
        if not args.arc_storyboard.exists():
            print(f"Error: not found: {args.arc_storyboard}", file=sys.stderr)
            return 1
        sb_text = args.arc_storyboard.read_text(encoding="utf-8")
        if args.arc_storyboard.suffix.lower() in (".yaml", ".yml"):
            import yaml

            arc_storyboard = yaml.safe_load(sb_text)
        else:
            arc_storyboard = json.loads(sb_text)

    raw_text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in (".yaml", ".yml"):
        import yaml

        raw = yaml.safe_load(raw_text)
    else:
        raw = json.loads(raw_text)
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
    arc_ref = None
    if args.arc_storyboard:
        try:
            arc_ref = str(args.arc_storyboard.resolve().relative_to(REPO_ROOT))
        except ValueError:
            arc_ref = str(args.arc_storyboard)
    doc = compile_panel_prompts_from_chapter_script(
        raw,
        series_id=raw.get("series_id"),
        chapter_id=raw.get("chapter_id"),
        config_hash=snap,
        style_id=resolved_style_id,
        teacher_id=args.teacher_id,
        arc_storyboard=arc_storyboard,
        arc_storyboard_ref=arc_ref,
    )
    write_atomically(args.out, doc)
    print(f"Wrote {len(doc['panels'])} panel prompts to {args.out}")
    for row in doc.get("storyboard_divergences") or []:
        print(
            f"WARN storyboard divergence [{row.get('type')}] "
            f"{row.get('panel_id') or row.get('page_id')} — {row.get('resolution')}",
            file=sys.stderr,
        )

    if args.assembly_hints_out:
        hints = build_assembly_layer_hints(
            arc_storyboard,
            repo_root=REPO_ROOT,
            series_id=raw.get("series_id"),
            arc_storyboard_ref=arc_ref,
        )
        write_atomically(args.assembly_hints_out, hints)
        stats = hints["gaps"]["stats"]
        if not hints["bank_contract_present"]:
            print(
                "WARN: no bank contract for this series "
                "(artifacts/manga/<series>/bank_contracts/) — hints emitted anyway",
                file=sys.stderr,
            )
        print(
            f"Wrote assembly layer hints ({stats['panels_with_picks']} panels with picks, "
            f"{stats['layers_real']} REAL / {stats['layers_interim']} INTERIM layers, "
            f"{stats['layers_gap']} demand gaps) to {args.assembly_hints_out}"
        )

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
