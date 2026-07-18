#!/usr/bin/env python3
"""Bundle rendered book.txt + audits + optional companion audio into one deliverable folder."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    ap = argparse.ArgumentParser(description="Package book + music metadata for brand admin handoff")
    ap.add_argument("--render-dir", required=True, type=Path, help="Directory containing book.txt")
    ap.add_argument("--dest", required=True, type=Path, help="Output directory (created)")
    ap.add_argument("--musician-id", required=True)
    ap.add_argument("--companion-json", type=Path, default=None, help="Output from generate_book_companion_song.py")
    ap.add_argument("--companion-wav", type=Path, default=None)
    args = ap.parse_args()

    src: Path = args.render_dir
    dest: Path = args.dest
    dest.mkdir(parents=True, exist_ok=True)

    manifest: dict = {"musician_id": args.musician_id, "files": []}

    def _copy(p: Path, name: str | None = None) -> None:
        if not p.exists():
            return
        target = dest / (name or p.name)
        shutil.copy2(p, target)
        manifest["files"].append({"path": str(target.relative_to(dest)), "source": str(p)})

    _copy(src / "book.txt")
    for optional in ("section_packet_audit.json", "music_overlay_audit.json", "budget.json", "enrichment_audit.json"):
        _copy(src / optional)

    if args.companion_json and args.companion_json.exists():
        _copy(args.companion_json, "companion_song_prompt.json")
    if args.companion_wav and args.companion_wav.exists():
        _copy(args.companion_wav, "companion_song.wav")

    (dest / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Packaged deliverable: {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
