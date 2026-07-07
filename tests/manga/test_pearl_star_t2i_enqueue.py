"""Tests for manga Pearl Star enqueue helper (out_path → dest_path contract)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from scripts.manga import pearl_star_t2i_enqueue as pst2i


def test_out_path_maps_to_dest_path(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    def fake_dispatch(job_class: str, payload: dict, **kwargs: object) -> dict:
        captured["payload"] = payload
        return {"job_id": 42, "task": kwargs.get("task"), "via": "local"}

    monkeypatch.setattr(pst2i, "pearl_star_dest_path", lambda p: f"/var/lib/pearl-star/manga_out/{p.name}")
    monkeypatch.setattr(
        "scripts.pearl_star.dispatch.dispatch_gpu_job",
        fake_dispatch,
    )

    out = pst2i.enqueue_panel_job(
        task="t2i_flux_dev_h1a",
        prompt="kettle",
        out_path="artifacts/manga/series/image_bank/L3/kettle.png",
    )
    assert out["job_id"] == 42
    payload = captured["payload"]
    assert isinstance(payload, dict)
    assert payload["dest_path"] == "/var/lib/pearl-star/manga_out/kettle.png"


def test_explicit_dest_path_wins_over_out_path(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_dispatch(job_class: str, payload: dict, **kwargs: object) -> dict:
        captured["payload"] = payload
        return {"job_id": 1, "task": "t2i_flux_dev_h1a", "via": "local"}

    monkeypatch.setattr(pst2i, "pearl_star_dest_path", lambda p: "/should/not/use")
    monkeypatch.setattr(
        "scripts.pearl_star.dispatch.dispatch_gpu_job",
        fake_dispatch,
    )

    pst2i.enqueue_panel_job(
        task="t2i_flux_dev_h1a",
        prompt="x",
        dest_path="/explicit/dest.png",
        out_path="artifacts/ignored.png",
    )
    payload = captured["payload"]
    assert isinstance(payload, dict)
    assert payload["dest_path"] == "/explicit/dest.png"


def test_enqueue_stillness_build_jobs_count() -> None:
    from scripts.manga.enqueue_stillness_real_layers import build_jobs

    jobs = build_jobs()
    assert len(jobs) == 6
    classes = {j.layer_class for j in jobs}
    assert classes == {"L1", "L3", "L4"}
    assert sum(1 for j in jobs if j.layer_class == "L3") == 4


def test_enqueue_stillness_dry_run(capsys: pytest.CaptureFixture[str]) -> None:
    from scripts.manga.enqueue_stillness_real_layers import main

    assert main(["--dry-run", "--no-preflight"]) == 0
    out = capsys.readouterr().out.strip().splitlines()
    assert len(out) == 6
    first = json.loads(out[0])
    assert "layer_id" in first
    assert "out_path" in first
