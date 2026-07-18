#!/usr/bin/env python3
"""Build a panel_prompts artifact from a v3 chapter_script_writer_handoff.

The output is FLUX-schnell-fp8 ready: each panel becomes one positive +
negative prompt pair, with style/palette/character lock-in baked in.
Pearl Star's ComfyUI queue consumes the resulting JSON.

Usage:
    # Single chapter
    python3 scripts/manga/build_panel_prompts.py \\
        --in artifacts/manga/chapter_scripts/.../ep_001.yaml \\
        --out artifacts/manga/panel_prompts/.../ep_001.panel_prompts.json

    # Default --out: derived from --in by replacing extension and dir
    python3 scripts/manga/build_panel_prompts.py --in path/to/ep_001.yaml
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from phoenix_v4.manga.chapter.visual_from_script_v3 import (  # type: ignore
    compile_v3_panel_prompts,
)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="input_path", required=True)
    p.add_argument("--out", dest="output_path",
                   help="Output JSON path (default: derive from --in)")
    p.add_argument("--style-id", help="Override style anchor (e.g. cozy_iyashikei)")
    args = p.parse_args()

    in_path = Path(args.input_path).resolve()
    if not in_path.exists():
        sys.stderr.write(f"❌ input not found: {in_path}\n")
        return 2

    if args.output_path:
        out_path = Path(args.output_path).resolve()
    else:
        # Default: artifacts/manga/panel_prompts/<series>/<chapter>.panel_prompts.json
        out_path = REPO / "artifacts" / "manga" / "panel_prompts"
        # Mirror the chapter_scripts directory structure
        try:
            relative = in_path.relative_to(REPO / "artifacts" / "manga" / "chapter_scripts")
            out_path = out_path / relative.with_suffix("")
            out_path = out_path.with_suffix(".panel_prompts.json")
        except ValueError:
            out_path = out_path / (in_path.stem + ".panel_prompts.json")

    out_path.parent.mkdir(parents=True, exist_ok=True)

    import yaml  # type: ignore

    chapter_script = yaml.safe_load(in_path.read_text(encoding="utf-8")) or {}
    style_overrides = {"style_id": args.style_id} if args.style_id else None
    artifact = compile_v3_panel_prompts(chapter_script, style_overrides=style_overrides)

    out_path.write_text(
        json.dumps(artifact, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"✓ wrote {out_path.relative_to(REPO) if out_path.is_relative_to(REPO) else out_path}")
    print(f"  panels: {artifact['total_panels']}")
    if artifact["panels"]:
        avg_len = sum(len(p["prompt"]) for p in artifact["panels"]) // len(artifact["panels"])
        max_len = max(len(p["prompt"]) for p in artifact["panels"])
        print(f"  prompt length: avg {avg_len} chars, max {max_len} chars")
    return 0


if __name__ == "__main__":
    sys.exit(main())
