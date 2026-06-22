"""Per-batch fault tolerance tests for ``run_live_activation``.

Covers RUN_LIVE_ACTIVATION_FAULT_TOLERANCE_V1:

  * success on first try
  * transient-then-success (one retry)
  * retries-exhausted (logged to sidecar, run continues)
  * non-retryable (fail-fast for the cell, run continues)
  * cap-exhausted (RunComfy cooldown skip + non-retryable cap message)

All tests stub SSH/probe/cost; no real network or subprocess.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from scripts.image_generation import batch_runner


def _state() -> batch_runner.PearlStarModelState:
    return batch_runner.PearlStarModelState(
        flux_schnell_present=True,
        flux_dev_present=True,
        animagine_xl_present=True,
        qwen_unified_ckpt_present=False,
        qwen_transformer_shard_count=9,
        probe_stdout="",
    )


def _stub_environment(monkeypatch: pytest.MonkeyPatch, *, cooldown: bool = False) -> None:
    monkeypatch.setattr(batch_runner, "ensure_pearl_comfyui", lambda ssh_host: None)
    monkeypatch.setattr(batch_runner, "probe_pearl_star_models", lambda ssh_host: _state())
    monkeypatch.setattr(
        batch_runner,
        "runcomfy_cost_check",
        lambda **k: {"cooldown": cooldown, "spend_to_date_usd": 10.0 if cooldown else 0.0},
    )


def _batch(batch_id: str, *, dispatch_path: str = "pearl_star") -> dict[str, Any]:
    return {
        "batch_id": batch_id,
        "locale": "en-US",
        "dispatch_path": dispatch_path,
        "sequence": 1,
        "workflow_template": "flux_txt2img_manga.json",
        "positive_prompt": "ft test panel",
    }


# ---------------------------------------------------------------------------
# Classifier unit tests
# ---------------------------------------------------------------------------


def test_classify_no_image_url_is_transient() -> None:
    policy = batch_runner.FaultTolerancePolicy()
    exc = RuntimeError("No image URL in RunComfy result keys=['status']")
    assert batch_runner._classify_exception(exc, policy) == "transient"


def test_classify_http_502_is_transient() -> None:
    policy = batch_runner.FaultTolerancePolicy()
    assert batch_runner._classify_exception(RuntimeError("HTTP 502 Bad Gateway"), policy) == "transient"
    assert batch_runner._classify_exception(RuntimeError("HTTP 503"), policy) == "transient"
    assert batch_runner._classify_exception(RuntimeError("HTTP 504 timeout"), policy) == "transient"


def test_classify_timeout_is_transient() -> None:
    policy = batch_runner.FaultTolerancePolicy()
    assert batch_runner._classify_exception(TimeoutError("Read timed out"), policy) == "transient"


def test_classify_auth_is_non_retryable() -> None:
    policy = batch_runner.FaultTolerancePolicy()
    assert batch_runner._classify_exception(RuntimeError("HTTP 401 Unauthorized"), policy) == "non_retryable"
    assert batch_runner._classify_exception(RuntimeError("HTTP 403 Forbidden"), policy) == "non_retryable"


def test_classify_cap_exhausted_is_non_retryable() -> None:
    policy = batch_runner.FaultTolerancePolicy()
    msg = "RunComfy cumulative_month_spend_usd >= $10; job not submitted."
    assert batch_runner._classify_exception(RuntimeError(msg), policy) == "non_retryable"


def test_classify_invalid_workflow_is_non_retryable() -> None:
    policy = batch_runner.FaultTolerancePolicy()
    exc = ValueError("invalid workflow JSON: missing key 'positive_prompt'")
    assert batch_runner._classify_exception(exc, policy) == "non_retryable"


def test_classify_unknown_error_defaults_to_unknown() -> None:
    policy = batch_runner.FaultTolerancePolicy()
    assert batch_runner._classify_exception(RuntimeError("disk full"), policy) == "unknown"


def test_non_retryable_wins_over_transient_when_both_match() -> None:
    policy = batch_runner.FaultTolerancePolicy()
    # Auth failure where the message also mentions "timeout" — must stay non_retryable.
    exc = RuntimeError("HTTP 401 unauthorized after timeout on auth probe")
    assert batch_runner._classify_exception(exc, policy) == "non_retryable"


# ---------------------------------------------------------------------------
# run_live_activation integration tests
# ---------------------------------------------------------------------------


def test_success_first_try(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _stub_environment(monkeypatch)
    out = tmp_path / "out"

    def fake_dispatch(batch: dict, *, dry_run: bool, **_: Any) -> dict[str, Any]:
        return {"dispatch_path": "pearl_star", "status": "succeeded", "dry_run": False}

    monkeypatch.setattr(batch_runner, "dispatch", fake_dispatch)

    res = batch_runner.run_live_activation(
        [_batch("ok_1")],
        output_root=out,
        skip_comfy_ping=True,
        sleep_fn=lambda _s: None,
        run_id="run_success",
    )
    cells = [r for r in res if not r.get("fault_tolerance_summary")]
    summary = next(r for r in res if r.get("fault_tolerance_summary"))
    assert len(cells) == 1
    assert cells[0]["status"] == "succeeded"
    assert cells[0]["attempts"] == 1
    assert summary["succeeded"] == 1
    assert summary["retried"] == 0
    assert summary["failed"] == 0
    assert summary["failed_cells_sidecar"] is None


def test_transient_then_success(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _stub_environment(monkeypatch)
    out = tmp_path / "out"
    calls = {"n": 0}

    def fake_dispatch(batch: dict, *, dry_run: bool, **_: Any) -> dict[str, Any]:
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("No image URL in RunComfy result keys=['status']")
        return {"dispatch_path": "pearl_star", "status": "succeeded", "dry_run": False}

    sleeps: list[float] = []
    monkeypatch.setattr(batch_runner, "dispatch", fake_dispatch)

    res = batch_runner.run_live_activation(
        [_batch("flaky_1")],
        output_root=out,
        skip_comfy_ping=True,
        sleep_fn=sleeps.append,
        run_id="run_flaky",
    )
    cells = [r for r in res if not r.get("fault_tolerance_summary")]
    summary = next(r for r in res if r.get("fault_tolerance_summary"))
    assert calls["n"] == 2
    assert cells[0]["status"] == "succeeded"
    assert cells[0]["attempts"] == 2
    assert summary["succeeded"] == 1
    assert summary["retried"] == 1
    assert summary["failed"] == 0
    # First-attempt backoff comes from policy default (30s).
    assert sleeps == [30.0]


def test_retries_exhausted_logs_sidecar_and_continues(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _stub_environment(monkeypatch)
    out = tmp_path / "out"
    out.mkdir(parents=True, exist_ok=True)
    calls = {"n": 0}

    def fake_dispatch(batch: dict, *, dry_run: bool, **_: Any) -> dict[str, Any]:
        calls["n"] += 1
        if batch["batch_id"] == "always_fail":
            raise RuntimeError("HTTP 503 Service Unavailable")
        return {"dispatch_path": "pearl_star", "status": "succeeded", "dry_run": False}

    monkeypatch.setattr(batch_runner, "dispatch", fake_dispatch)

    res = batch_runner.run_live_activation(
        [_batch("always_fail"), _batch("good_after")],
        output_root=out,
        skip_comfy_ping=True,
        sleep_fn=lambda _s: None,
        run_id="run_exhaust",
    )
    cells = [r for r in res if not r.get("fault_tolerance_summary")]
    summary = next(r for r in res if r.get("fault_tolerance_summary"))
    failed = [c for c in cells if c.get("failed")]
    succeeded = [c for c in cells if c.get("status") == "succeeded"]

    # 1 initial + 2 retries = 3 attempts on the failing cell, then continue to next.
    assert calls["n"] == 3 + 1
    assert len(failed) == 1
    assert failed[0]["classification"] == "retries_exhausted"
    assert failed[0]["attempts"] == 3
    assert len(succeeded) == 1
    assert summary["failed"] == 1
    assert summary["succeeded"] == 1

    sidecar = out / "run_exhaust_failed_cells.tsv"
    assert sidecar.is_file(), "expected sidecar TSV to be written"
    text = sidecar.read_text(encoding="utf-8")
    assert "always_fail" in text
    assert "retries_exhausted" in text


def test_non_retryable_fails_fast(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _stub_environment(monkeypatch)
    out = tmp_path / "out"
    out.mkdir(parents=True, exist_ok=True)
    calls = {"n": 0}

    def fake_dispatch(batch: dict, *, dry_run: bool, **_: Any) -> dict[str, Any]:
        calls["n"] += 1
        if batch["batch_id"] == "auth_fail":
            raise RuntimeError("HTTP 401 Unauthorized")
        return {"dispatch_path": "pearl_star", "status": "succeeded", "dry_run": False}

    monkeypatch.setattr(batch_runner, "dispatch", fake_dispatch)

    res = batch_runner.run_live_activation(
        [_batch("auth_fail"), _batch("after")],
        output_root=out,
        skip_comfy_ping=True,
        sleep_fn=lambda _s: None,
        run_id="run_auth",
    )
    cells = [r for r in res if not r.get("fault_tolerance_summary")]
    summary = next(r for r in res if r.get("fault_tolerance_summary"))
    failed = [c for c in cells if c.get("failed")]

    # No retries on non-retryable: just 1 call for auth_fail + 1 for after.
    assert calls["n"] == 2
    assert len(failed) == 1
    assert failed[0]["classification"] == "non_retryable"
    assert failed[0]["attempts"] == 1
    assert summary["failed"] == 1
    assert summary["succeeded"] == 1

    sidecar = out / "run_auth_failed_cells.tsv"
    assert sidecar.is_file()
    assert "non_retryable" in sidecar.read_text(encoding="utf-8")


def test_cap_exhausted_skip_then_runtime_message_non_retryable(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Two complementary cap behaviors:

    1. RunComfy cooldown TSV/billing flips ``cost_check`` → batch is skipped
       up-front (existing behavior; never hits dispatch_with_retries).
    2. If a dispatcher itself raises a cap message (e.g. RunComfy returns
       'cumulative_month_spend_usd >= $10'), the wrapper classifies it as
       non_retryable and writes a sidecar row.
    """
    _stub_environment(monkeypatch, cooldown=True)
    out = tmp_path / "out"

    def fake_dispatch(*_a: Any, **_kw: Any) -> dict[str, Any]:  # pragma: no cover
        raise AssertionError("dispatch must not run when cost cooldown active")

    monkeypatch.setattr(batch_runner, "dispatch", fake_dispatch)

    res = batch_runner.run_live_activation(
        [_batch("cap_skip", dispatch_path="runcomfy")],
        output_root=out,
        skip_comfy_ping=True,
        sleep_fn=lambda _s: None,
        run_id="run_cap_skip",
    )
    cells = [r for r in res if not r.get("fault_tolerance_summary")]
    assert cells[0].get("skipped") is True
    assert cells[0].get("reason") == "runcomfy_cost_cooldown"

    # Now exercise dispatcher-raised cap message.
    _stub_environment(monkeypatch, cooldown=False)
    out2 = tmp_path / "out2"
    out2.mkdir(parents=True, exist_ok=True)

    def cap_dispatch(*_a: Any, **_kw: Any) -> dict[str, Any]:
        raise RuntimeError(
            "RunComfy cumulative_month_spend_usd >= $10; job not submitted."
        )

    monkeypatch.setattr(batch_runner, "dispatch", cap_dispatch)

    res2 = batch_runner.run_live_activation(
        [_batch("cap_raise", dispatch_path="runcomfy")],
        output_root=out2,
        skip_comfy_ping=True,
        sleep_fn=lambda _s: None,
        run_id="run_cap_raise",
    )
    cells2 = [r for r in res2 if not r.get("fault_tolerance_summary")]
    failed = [c for c in cells2 if c.get("failed")]
    assert len(failed) == 1
    assert failed[0]["classification"] == "non_retryable"
    assert failed[0]["attempts"] == 1
    sidecar = out2 / "run_cap_raise_failed_cells.tsv"
    assert sidecar.is_file()


def test_unknown_error_treated_as_non_retryable(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Surprise exceptions fail-fast and land in the sidecar (no infinite retry)."""
    _stub_environment(monkeypatch)
    out = tmp_path / "out"
    out.mkdir(parents=True, exist_ok=True)
    calls = {"n": 0}

    def fake_dispatch(*_a: Any, **_kw: Any) -> dict[str, Any]:
        calls["n"] += 1
        raise RuntimeError("disk full")

    monkeypatch.setattr(batch_runner, "dispatch", fake_dispatch)

    res = batch_runner.run_live_activation(
        [_batch("surprise")],
        output_root=out,
        skip_comfy_ping=True,
        sleep_fn=lambda _s: None,
        run_id="run_unknown",
    )
    cells = [r for r in res if not r.get("fault_tolerance_summary")]
    assert calls["n"] == 1
    assert cells[0]["classification"] == "unknown"


def test_keyboard_interrupt_propagates(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _stub_environment(monkeypatch)
    out = tmp_path / "out"

    def fake_dispatch(*_a: Any, **_kw: Any) -> dict[str, Any]:
        raise KeyboardInterrupt()

    monkeypatch.setattr(batch_runner, "dispatch", fake_dispatch)

    with pytest.raises(KeyboardInterrupt):
        batch_runner.run_live_activation(
            [_batch("ki")],
            output_root=out,
            skip_comfy_ping=True,
            sleep_fn=lambda _s: None,
            run_id="run_ki",
        )


def test_custom_policy_extra_transient(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Caller can extend the transient list without forking the module."""
    _stub_environment(monkeypatch)
    out = tmp_path / "out"
    calls = {"n": 0}

    def fake_dispatch(batch: dict, *, dry_run: bool, **_: Any) -> dict[str, Any]:
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("custom thing failed")
        return {"dispatch_path": "pearl_star", "status": "succeeded", "dry_run": False}

    monkeypatch.setattr(batch_runner, "dispatch", fake_dispatch)

    policy = batch_runner.FaultTolerancePolicy(
        max_retries=1,
        backoff_schedule_s=(0.0,),
        extra_transient=("custom thing",),
    )
    res = batch_runner.run_live_activation(
        [_batch("custom_flake")],
        output_root=out,
        skip_comfy_ping=True,
        sleep_fn=lambda _s: None,
        run_id="run_custom",
        fault_tolerance=policy,
    )
    cells = [r for r in res if not r.get("fault_tolerance_summary")]
    assert cells[0]["status"] == "succeeded"
    assert cells[0]["attempts"] == 2
    assert calls["n"] == 2
