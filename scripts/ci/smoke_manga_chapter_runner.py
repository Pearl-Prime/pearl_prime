#!/usr/bin/env python3
"""CI smoke: minimal workspace + ``scripts/manga/run_manga_chapter.py`` (replay, full DAG).

Exit 0 only if the CLI completes and revision_queue clears.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

# Minimal 1x1 RGBA PNG (same as manga tests)
_MIN_PNG = bytes(
    [
        0x89,
        0x50,
        0x4E,
        0x47,
        0x0D,
        0x0A,
        0x1A,
        0x0A,
        0x00,
        0x00,
        0x00,
        0x0D,
        0x49,
        0x48,
        0x44,
        0x52,
        0x00,
        0x00,
        0x00,
        0x01,
        0x00,
        0x00,
        0x00,
        0x01,
        0x08,
        0x06,
        0x00,
        0x00,
        0x00,
        0x1F,
        0x15,
        0xC4,
        0x89,
        0x00,
        0x00,
        0x00,
        0x0A,
        0x49,
        0x44,
        0x41,
        0x54,
        0x78,
        0x9C,
        0x63,
        0x00,
        0x01,
        0x00,
        0x00,
        0x05,
        0x00,
        0x01,
        0x0D,
        0x0A,
        0x2D,
        0xB4,
        0x00,
        0x00,
        0x00,
        0x00,
        0x49,
        0x45,
        0x4E,
        0x44,
        0xAE,
        0x42,
        0x60,
        0x82,
    ]
)


def main() -> int:
    sys.path.insert(0, str(REPO))
    from phoenix_v4.manga.series.emit import emit_series_setup

    with tempfile.TemporaryDirectory(prefix="manga_chapter_smoke_") as td:
        ws = Path(td)
        emit_series_setup(
            ws,
            series_id="ci_smoke_series",
            arc_id="ci_smoke_arc",
            genre_id="ci_smoke_genre",
        )
        cr = {
            "schema_version": "1.0.0",
            "artifact_type": "chapter_request",
            "series_id": "ci_smoke_series",
            "chapter_id": "ci_smoke_chapter",
            "arc_id": "ci_smoke_arc",
        }
        (ws / "chapter_request.json").write_text(
            json.dumps(cr, indent=2) + "\n", encoding="utf-8"
        )

        cli = REPO / "scripts" / "manga" / "run_manga_chapter.py"
        env = {**os.environ, "PYTHONPATH": str(REPO)}
        r0 = subprocess.run(
            [
                sys.executable,
                str(cli),
                "--workspace",
                str(ws),
                "--backend",
                "noop",
                "--to-stage",
                "chapter_visual",
            ],
            cwd=str(REPO),
            env=env,
        )
        if r0.returncode != 0:
            print("smoke: noop chapter_visual failed", file=sys.stderr)
            return r0.returncode

        pp_path = ws / "panel_prompts.json"
        if not pp_path.is_file():
            print("smoke: panel_prompts.json not produced", file=sys.stderr)
            return 1
        panel_prompts = json.loads(pp_path.read_text(encoding="utf-8"))
        # MANGA.BESTSELLER.GENRE_ENGINE reads declared genre from the chapter script.
        from phoenix_v4.manga.models import paths as manga_paths

        script_path = ws / manga_paths.CHAPTER_SCRIPT_WRITER_HANDOFF
        script = json.loads(script_path.read_text(encoding="utf-8"))
        script["genre_id"] = "ci_smoke_genre"
        script_path.write_text(json.dumps(script, indent=2) + "\n", encoding="utf-8")

        replay = ws / "_replay"
        replay.mkdir()
        mapping: dict[str, str] = {}
        for panel in panel_prompts.get("panels") or []:
            pid = str(panel.get("panel_id") or "")
            if not pid:
                continue
            fname = f"{pid}.png"
            (replay / fname).write_bytes(_MIN_PNG)
            mapping[pid] = fname
        mmap = replay / "map.json"
        mmap.write_text(json.dumps(mapping), encoding="utf-8")

        r = subprocess.run(
            [
                sys.executable,
                str(cli),
                "--workspace",
                str(ws),
                "--backend",
                "replay",
                "--replay-map",
                str(mmap),
                "--from-stage",
                "chapter_image_gen",
            ],
            cwd=str(REPO),
            env=env,
        )
        if r.returncode != 0:
            print("smoke: run_manga_chapter.py failed", file=sys.stderr)
            return r.returncode

        rq = json.loads((ws / "revision_queue.json").read_text(encoding="utf-8"))
        if rq.get("chapter_clearance") != "pass":
            print("smoke: revision_queue not pass:", rq, file=sys.stderr)
            return 1

    print("smoke_manga_chapter_runner: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
