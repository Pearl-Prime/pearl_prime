"""Regression tests for the V1.2 panel-hang poll-budget fix.

Locks behaviour added 2026-05-13:
- Default poll budget is 600s (was 300s, below the measured ~292s cold-start
  P95 — see AMENDMENT-2026-05-13 in
  ``docs/specs/CONDUCTOR_V3_DISPATCH_BRIDGE_V1_SPEC.md``).
- ``RUNCOMFY_POLL_MAX_WAIT_S`` env var overrides default, clamped to
  ``[300, 1800]``.
- ``poll_wait_s`` and ``poll_budget_s`` appear in successful dispatch result.
- Poll-timeout raises a clear error (no more silent hang at the cell-guard
  ceiling).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.image_generation.dispatchers import runcomfy_dispatcher as dispatcher


def test_default_poll_budget_is_600s(monkeypatch: pytest.MonkeyPatch) -> None:
    """Default must clear the measured ~292s RunComfy cold-start P95."""
    monkeypatch.delenv("RUNCOMFY_POLL_MAX_WAIT_S", raising=False)
    assert dispatcher._poll_max_wait_s() == 600


def test_env_override_respected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RUNCOMFY_POLL_MAX_WAIT_S", "900")
    assert dispatcher._poll_max_wait_s() == 900


def test_env_override_clamped_low(monkeypatch: pytest.MonkeyPatch) -> None:
    """Floor at 300 — anything tighter would re-introduce the hang."""
    monkeypatch.setenv("RUNCOMFY_POLL_MAX_WAIT_S", "60")
    assert dispatcher._poll_max_wait_s() == 300


def test_env_override_clamped_high(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ceiling at 1800 — RunComfy serverless hard-timeout is 30 min."""
    monkeypatch.setenv("RUNCOMFY_POLL_MAX_WAIT_S", "999999")
    assert dispatcher._poll_max_wait_s() == 1800


def test_env_override_invalid_value_falls_back(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RUNCOMFY_POLL_MAX_WAIT_S", "not-an-int")
    assert dispatcher._poll_max_wait_s() == 600


def test_dispatch_surfaces_poll_wait_and_budget(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Successful live dispatch must include ``poll_wait_s`` + ``poll_budget_s``.

    Both fields are required by the V1.2 fan-out observability layer so the
    operator can tune the upstream per-cell guard against measured behaviour
    rather than guesses.
    """
    # Make a tiny valid PNG fixture (>= 10_000 bytes) for _validate_png.
    png_path = tmp_path / "out" / "smoke" / "smoke.png"
    png_path.parent.mkdir(parents=True, exist_ok=True)
    png_header = b"\x89PNG\r\n\x1a\n" + b"\x00" * 10_010
    png_path.write_bytes(png_header)

    # Make submit/poll/result all return canned values; no HTTP.
    monkeypatch.setenv("RUNCOMFY_POLL_MAX_WAIT_S", "450")
    monkeypatch.setattr(
        dispatcher,
        "_runcomfy_api_key",
        lambda: "fake-token-for-test",  # nosec — test fixture, never logged
    )
    monkeypatch.setattr(
        dispatcher._rc,
        "dispatch_workflow",
        lambda *a, **kw: {"dry_run": True, "workflow_path": str(a[0])},
    )
    monkeypatch.setattr(
        dispatcher._bill,
        "poll_billing",
        lambda dry_run: {"cumulative_month_spend_usd": 0.42},
    )
    monkeypatch.setattr(
        dispatcher,
        "submit_inference",
        lambda **kw: {
            "request_id": "req-fake-1",
            "status_url": "https://api.runcomfy.net/prod/v2/x/status",
            "result_url": "https://api.runcomfy.net/prod/v2/x/result",
        },
    )
    monkeypatch.setattr(
        dispatcher,
        "poll_request",
        lambda api_key, url, max_wait: {"status": "completed"},
    )
    monkeypatch.setattr(
        dispatcher,
        "get_result",
        lambda api_key, url: {
            "outputs": {"9": {"images": [{"url": "https://cdn.example/x.png"}]}}
        },
    )
    monkeypatch.setattr(
        dispatcher,
        "extract_image_url",
        lambda final: "https://cdn.example/x.png",
    )
    monkeypatch.setattr(
        dispatcher,
        "download_image",
        lambda url, dest: dest.write_bytes(png_path.read_bytes()),
    )
    monkeypatch.setattr(
        dispatcher._ledger,
        "record_dispatch",
        lambda **kw: type(
            "L",
            (),
            {
                "est_usd": 0.01,
                "cumulative_month_usd": 0.43,
                "source": "estimated",
                "rate_per_second_usd": 0.0003,
            },
        )(),
    )

    batch = {
        "batch_id": "smoke-fixture",
        "positive_prompt": "vertical webtoon panel",
        "seed": 42,
        "runcomfy_workflow": "qwen_image_txt2img_manga",
    }
    result = dispatcher.dispatch(
        batch, dry_run=False, activation_output_dir=tmp_path / "out"
    )
    assert result["status"] == "succeeded"
    assert "poll_wait_s" in result
    assert "poll_budget_s" in result
    assert result["poll_budget_s"] == 450


def test_dispatch_poll_timeout_raises_clear_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """When poll budget elapses without a terminal status, we must raise
    a diagnostic error rather than silently returning an empty result. The
    error string must mention ``RUNCOMFY_POLL_MAX_WAIT_S`` so operators have
    a direct lever."""
    monkeypatch.setattr(
        dispatcher,
        "_runcomfy_api_key",
        lambda: "fake-token-for-test",
    )
    monkeypatch.setattr(
        dispatcher._rc,
        "dispatch_workflow",
        lambda *a, **kw: {"dry_run": True},
    )
    monkeypatch.setattr(
        dispatcher._bill,
        "poll_billing",
        lambda dry_run: {"cumulative_month_spend_usd": 0.0},
    )
    monkeypatch.setattr(
        dispatcher,
        "submit_inference",
        lambda **kw: {
            "request_id": "req-fake-2",
            "status_url": "https://api.runcomfy.net/prod/v2/y/status",
            "result_url": "https://api.runcomfy.net/prod/v2/y/result",
        },
    )
    monkeypatch.setattr(
        dispatcher,
        "poll_request",
        lambda api_key, url, max_wait: {"status": "timeout"},
    )

    batch = {"batch_id": "smoke-timeout", "positive_prompt": "x", "seed": 1}
    with pytest.raises(RuntimeError, match="RUNCOMFY_POLL_MAX_WAIT_S"):
        dispatcher.dispatch(
            batch, dry_run=False, activation_output_dir=tmp_path / "out"
        )
