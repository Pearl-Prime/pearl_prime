"""E2E replay chapter DAG + gate registry + two-phase resume."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from phoenix_v4.manga.image_backend import FixtureReplayImageBackend, NoopImageBackend
from phoenix_v4.manga.models import stage_ids as sid
from phoenix_v4.manga.models.validation import validate_instance
from phoenix_v4.manga.qc.gate_registry import load_gate_registry
from phoenix_v4.manga.runner.chapter_runner import run_chapter_dag
from phoenix_v4.manga.runner.stage_manifest_io import stage_is_passed
from phoenix_v4.manga.series.emit import emit_series_setup

pytest.importorskip("PIL")

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


def test_gate_registry_yaml_loads() -> None:
    gates = load_gate_registry()
    ids = {g.gate_id for g in gates}
    assert "MANGA_GATE_IMAGES_ALL_OK" in ids
    assert "MANGA_GATE_STORY_HANDOFF" in ids


def test_series_memory_merge_append_fact() -> None:
    from phoenix_v4.manga.memory.series_memory_merge import apply_series_memory_update

    mem = {
        "schema_version": "1.0.0",
        "artifact_type": "series_memory",
        "facts": [{"a": 1}],
    }
    upd = {
        "schema_version": "1.0.0",
        "artifact_type": "series_memory_update",
        "patches": [{"op": "append_fact", "fact": {"b": 2}}],
    }
    validate_instance(upd, "series_memory_update")
    out = apply_series_memory_update(mem, upd)
    validate_instance(out, "series_memory")
    assert len(out["facts"]) == 2


def test_chapter_runner_two_phase_resume(tmp_path: Path) -> None:
    ws = tmp_path / "ws"
    emit_series_setup(
        ws,
        series_id="e2e_series",
        arc_id="e2e_arc",
        genre_id="e2e_genre",
    )
    cr = {
        "schema_version": "1.0.0",
        "artifact_type": "chapter_request",
        "series_id": "e2e_series",
        "chapter_id": "ch_e2e",
        "arc_id": "e2e_arc",
    }
    validate_instance(cr, "chapter_request")
    (ws / "chapter_request.json").write_text(
        json.dumps(cr, indent=2) + "\n", encoding="utf-8"
    )

    r1 = run_chapter_dag(
        ws,
        image_backend=NoopImageBackend(),
        to_stage=sid.CHAPTER_VISUAL,
        config_hash="e2e",
    )
    assert sid.CHAPTER_VISUAL in r1
    assert stage_is_passed(ws, sid.CHAPTER_VISUAL)
    assert not stage_is_passed(ws, sid.CHAPTER_IMAGE_GEN)

    replay_dir = tmp_path / "replay"
    replay_dir.mkdir()
    (replay_dir / "p_1_0.png").write_bytes(_MIN_PNG)
    (replay_dir / "p_1_1.png").write_bytes(_MIN_PNG)
    mmap = replay_dir / "map.json"
    mmap.write_text(
        json.dumps({"p_1_0": "p_1_0.png", "p_1_1": "p_1_1.png"}),
        encoding="utf-8",
    )
    backend = FixtureReplayImageBackend.from_json_file(mmap)

    r2 = run_chapter_dag(
        ws,
        image_backend=backend,
        from_stage=sid.CHAPTER_IMAGE_GEN,
        config_hash="e2e",
    )
    assert sid.CHAPTER_IMAGE_GEN in r2
    assert sid.SERIES_MEMORY_MERGE in r2
    assert stage_is_passed(ws, sid.CHAPTER_QC)
    assert stage_is_passed(ws, sid.SERIES_MEMORY_MERGE)

    rq = json.loads((ws / "revision_queue.json").read_text(encoding="utf-8"))
    assert rq["chapter_clearance"] == "pass"

    mem = json.loads((ws / "series" / "series_memory.json").read_text(encoding="utf-8"))
    validate_instance(mem, "series_memory")
    assert any(
        f.get("kind") == "chapter_pipeline_completed" for f in mem.get("facts") or []
    )

    r3 = run_chapter_dag(ws, image_backend=backend, config_hash="e2e")
    assert r3 == []
