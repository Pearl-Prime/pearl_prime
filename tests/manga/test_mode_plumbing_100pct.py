from __future__ import annotations

import sys
import types
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "scripts" / "manga"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import verify_manga_mode_plumbing as verifier


def test_mode_verifier_requires_internal_and_handoff_vessels(monkeypatch):
    emit_module = types.ModuleType("phoenix_v4.manga.series.emit")

    def emit_series_setup(*, mode=None, **kwargs):
        return mode

    def build_series_artifact_bundle(*, mode=None, **kwargs):
        return {
            "story_architecture_internal": {
                "mode": mode,
                "mode_vessel": {"id": f"{mode}-vessel"},
                "mode_vessel_beats": [{"beat_id": "v1"}],
            },
            "story_architecture_handoff": {
                "mode": mode,
                "mode_vessel": {"id": f"{mode}-vessel"},
                "mode_vessel_beats": [{"beat_id": "v1"}],
            },
        }

    emit_module.emit_series_setup = emit_series_setup
    emit_module.build_series_artifact_bundle = build_series_artifact_bundle

    run_module = types.ModuleType("scripts.run_manga_pipeline")

    def run_one_book(*, mode=None, **kwargs):
        return mode

    run_module.run_one_book = run_one_book

    monkeypatch.setitem(sys.modules, "phoenix_v4.manga.series.emit", emit_module)
    monkeypatch.setitem(sys.modules, "scripts.run_manga_pipeline", run_module)
    report = verifier.verify_mode("teacher")
    assert report["passed"] is True
    assert report["emit-mode-plumbing"] == "green"
