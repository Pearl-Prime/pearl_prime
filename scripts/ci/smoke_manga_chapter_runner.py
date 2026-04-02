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

        replay = ws / "_replay"
        replay.mkdir()
        (replay / "p_1_0.png").write_bytes(_MIN_PNG)
        (replay / "p_1_1.png").write_bytes(_MIN_PNG)
        (replay / "map.json").write_text(
            json.dumps({"p_1_0": "p_1_0.png", "p_1_1": "p_1_1.png"}),
            encoding="utf-8",
        )

        cli = REPO / "scripts" / "manga" / "run_manga_chapter.py"
        env = {**os.environ, "PYTHONPATH": str(REPO)}
        r = subprocess.run(
            [
                sys.executable,
                str(cli),
                "--workspace",
                str(ws),
                "--backend",
                "replay",
                "--replay-map",
                str(replay / "map.json"),
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
