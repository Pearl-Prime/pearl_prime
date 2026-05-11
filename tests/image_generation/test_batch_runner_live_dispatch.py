"""Unit tests for activation routing and live-dispatch wiring (no real SSH/API)."""

from __future__ import annotations

from pathlib import Path
import pytest

from scripts.image_generation import batch_runner


def _state(
    *,
    flux_schnell_present: bool = True,
    animagine_xl_present: bool = True,
    qwen_unified_ckpt_present: bool = False,
    qwen_transformer_shard_count: int = 9,
    probe_stdout: str = "",
) -> batch_runner.PearlStarModelState:
    return batch_runner.PearlStarModelState(
        flux_schnell_present=flux_schnell_present,
        animagine_xl_present=animagine_xl_present,
        qwen_unified_ckpt_present=qwen_unified_ckpt_present,
        qwen_transformer_shard_count=qwen_transformer_shard_count,
        probe_stdout=probe_stdout,
    )


def test_resolve_dispatch_flux_pearl() -> None:
    b = {"dispatch_path": "auto", "workflow_template": "flux_txt2img_manga.json"}
    assert batch_runner.resolve_dispatch_path(b, _state()) == "pearl_star"


def test_resolve_dispatch_flux_runcomfy_when_missing() -> None:
    b = {"dispatch_path": "auto", "workflow_template": "flux_txt2img_manga.json"}
    assert batch_runner.resolve_dispatch_path(b, _state(flux_schnell_present=False)) == "runcomfy"


def test_resolve_dispatch_animagine_pearl_when_ckpt() -> None:
    b = {"dispatch_path": "auto", "workflow_template": "animagine_xl_txt2img_manga.json"}
    assert batch_runner.resolve_dispatch_path(b, _state()) == "pearl_star"


def test_resolve_dispatch_animagine_runcomfy_when_missing() -> None:
    b = {"dispatch_path": "auto", "workflow_template": "animagine_xl_txt2img_manga.json"}
    assert batch_runner.resolve_dispatch_path(b, _state(animagine_xl_present=False)) == "runcomfy"


def test_resolve_dispatch_qwen_pearl_only_with_unified_ckpt() -> None:
    b = {"dispatch_path": "auto", "workflow_template": "qwen_image_txt2img_manga.json"}
    assert batch_runner.resolve_dispatch_path(b, _state(qwen_unified_ckpt_present=True)) == "pearl_star"
    assert batch_runner.resolve_dispatch_path(b, _state(qwen_unified_ckpt_present=False)) == "runcomfy"


def test_resolve_dispatch_explicit_run_comfy_alias() -> None:
    b = {"dispatch_path": "run_comfy", "workflow_template": "flux_txt2img_manga.json"}
    assert batch_runner.resolve_dispatch_path(b, None) == "runcomfy"


def test_resolve_auto_none_state_routes_runcomfy() -> None:
    b = {"dispatch_path": "auto", "workflow_template": "flux_txt2img_manga.json"}
    assert batch_runner.resolve_dispatch_path(b, None) == "runcomfy"


def test_run_live_activation_happy_path_pearl(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    out = tmp_path / "smoke"
    batches = [
        {
            "batch_id": "smoke_a",
            "locale": "en-US",
            "dispatch_path": "pearl_star",
            "sequence": 1,
            "workflow_template": "flux_txt2img_manga.json",
            "positive_prompt": "test panel",
            "negative_prompt": "blur",
        },
    ]

    def fake_dispatch(batch: dict, *, dry_run: bool, **kwargs: object) -> dict:
        assert dry_run is False
        assert kwargs.get("ssh_host") == "testhost"
        assert kwargs.get("activation_output_dir") == out
        return {"dispatch_path": "pearl_star", "status": "succeeded", "dry_run": False}

    monkeypatch.setattr(batch_runner, "ensure_pearl_comfyui", lambda ssh_host: None)
    monkeypatch.setattr(batch_runner, "probe_pearl_star_models", lambda ssh_host: _state())
    monkeypatch.setattr(batch_runner, "dispatch", fake_dispatch)
    monkeypatch.setattr(batch_runner, "runcomfy_cost_check", lambda **k: {"cooldown": False, "spend_to_date_usd": 0.0})

    res = batch_runner.run_live_activation(
        batches,
        output_root=out,
        ssh_host="testhost",
        skip_comfy_ping=True,
    )
    # Last element is the fault_tolerance_summary row (RUN_LIVE_ACTIVATION_FAULT_TOLERANCE_V1).
    cells = [r for r in res if not r.get("fault_tolerance_summary")]
    assert len(cells) == 1
    assert cells[0]["status"] == "succeeded"


def test_run_live_activation_skips_runcomfy_on_cost_cap(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    out = tmp_path / "smoke"
    batches = [
        {
            "batch_id": "cap_r",
            "locale": "en-US",
            "dispatch_path": "runcomfy",
            "sequence": 1,
            "workflow_template": "flux_txt2img_manga.json",
            "positive_prompt": "x",
        },
    ]
    monkeypatch.setattr(batch_runner, "ensure_pearl_comfyui", lambda ssh_host: None)
    monkeypatch.setattr(batch_runner, "probe_pearl_star_models", lambda ssh_host: _state())
    monkeypatch.setattr(
        batch_runner,
        "runcomfy_cost_check",
        lambda **k: {"cooldown": True, "spend_to_date_usd": 10.0},
    )
    res = batch_runner.run_live_activation(
        batches,
        output_root=out,
        skip_comfy_ping=True,
    )
    cells = [r for r in res if not r.get("fault_tolerance_summary")]
    assert cells[0].get("skipped") is True
    assert cells[0].get("reason") == "runcomfy_cost_cooldown"


def test_run_live_activation_routing_animagine_to_pearl(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    out = tmp_path / "smoke"
    batches = [
        {
            "batch_id": "route_anim",
            "locale": "ja-JP",
            "dispatch_path": "auto",
            "sequence": 1,
            "workflow_template": "animagine_xl_txt2img_manga.json",
            "positive_prompt": "1girl, school uniform",
            "negative_prompt": "lowres",
            "reference_image": "example.png",
        },
    ]
    captured: dict[str, object] = {}

    def fake_dispatch(batch: dict, *, dry_run: bool, **kwargs: object) -> dict:
        captured["path"] = batch["dispatch_path"]
        return {"dispatch_path": batch["dispatch_path"], "status": "succeeded", "dry_run": False}

    monkeypatch.setattr(batch_runner, "ensure_pearl_comfyui", lambda ssh_host: None)
    monkeypatch.setattr(batch_runner, "probe_pearl_star_models", lambda ssh_host: _state(animagine_xl_present=True))
    monkeypatch.setattr(batch_runner, "dispatch", fake_dispatch)
    monkeypatch.setattr(batch_runner, "runcomfy_cost_check", lambda **k: {"cooldown": False, "spend_to_date_usd": 0.0})

    batch_runner.run_live_activation(batches, output_root=out, skip_comfy_ping=True)
    assert captured["path"] == "pearl_star"
