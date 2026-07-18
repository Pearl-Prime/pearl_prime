"""Tests for the canonical Pearl Star dispatch helper (scripts/pearl_star/dispatch.py).

All subprocess calls are mocked — no SSH, no queue, no GPU is touched. We verify
that dispatch_gpu_job validates inputs, resolves task names, and ships the
correct payload to defer_panel_job_cli.py via the local or SSH path.
"""

from __future__ import annotations

import json
import subprocess

import pytest

from scripts.pearl_star import dispatch
from scripts.pearl_star.dispatch import DispatchError, dispatch_gpu_job


def _fake_completed(stdout: str, returncode: int = 0, stderr: str = ""):
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


def test_local_dispatch_ships_expected_payload(monkeypatch):
    captured = {}

    def fake_run(cmd, *args, **kwargs):
        captured["cmd"] = cmd
        return _fake_completed(json.dumps({"job_id": 7, "task": "t2i_flux_dev_h1a"}))

    monkeypatch.setenv("PS_QUEUE_DSN", "postgresql://x@127.0.0.1/q")
    monkeypatch.setattr(dispatch.subprocess, "run", fake_run)

    out = dispatch_gpu_job("t2i", {"prompt": "hi", "seed": 1}, task="t2i_flux_dev_h1a")

    assert out["job_id"] == 7
    assert out["via"] == "local"
    cmd = captured["cmd"]
    assert cmd[0] == "python3"
    assert "defer_panel_job_cli.py" in cmd[1]
    assert cmd[2:4] == ["--task", "t2i_flux_dev_h1a"]
    payload = json.loads(cmd[5])
    assert payload["prompt"] == "hi"
    assert payload["seed"] == 1
    # priority must NOT be injected — on-box workers reject unknown kwargs
    assert "priority" not in payload


def test_ssh_dispatch_when_no_dsn(monkeypatch):
    captured = {}

    def fake_run(cmd, *args, **kwargs):
        captured["cmd"] = cmd
        return _fake_completed(json.dumps({"job_id": 9, "task": "t2i_flux_schnell"}))

    monkeypatch.delenv("PS_QUEUE_DSN", raising=False)
    monkeypatch.setattr(dispatch.subprocess, "run", fake_run)

    out = dispatch_gpu_job("t2i", {"prompt": "x"}, task="t2i_flux_schnell", ssh_host="pearl_star")

    assert out["via"] == "ssh:pearl_star"
    cmd = captured["cmd"]
    assert cmd[0] == "ssh"
    assert "pearl_star" in cmd
    # remote command embeds the defer CLI + task
    remote = cmd[-1]
    assert "defer_panel_job_cli.py" in remote
    assert "t2i_flux_schnell" in remote


def test_priority_arg_accepted_but_not_injected(monkeypatch):
    """priority= is validated but not shipped as a task kwarg (workers reject it)."""
    captured = {}

    def fake_run(cmd, *args, **kwargs):
        captured["cmd"] = cmd
        return _fake_completed(json.dumps({"job_id": 1, "task": "t2i_flux_dev_h1a"}))

    monkeypatch.setenv("PS_QUEUE_DSN", "postgresql://x@127.0.0.1/q")
    monkeypatch.setattr(dispatch.subprocess, "run", fake_run)

    dispatch_gpu_job("t2i", {"prompt": "p"}, task="t2i_flux_dev_h1a", priority=8)
    payload = json.loads(captured["cmd"][5])
    assert payload["prompt"] == "p"
    assert "priority" not in payload


def test_unknown_job_class_rejected():
    with pytest.raises(ValueError, match="unknown job_class"):
        dispatch_gpu_job("gpu", {"prompt": "x"})


def test_unknown_task_rejected():
    with pytest.raises(ValueError, match="unknown task"):
        dispatch_gpu_job("t2i", {"prompt": "x"}, task="t2i_nonexistent")


def test_task_class_mismatch_rejected():
    with pytest.raises(ValueError, match="belongs to job_class"):
        # t2i_flux_dev_h1a is a t2i task, not llm
        dispatch_gpu_job("llm", {"prompt": "x"}, task="t2i_flux_dev_h1a")


def test_ambiguous_t2i_requires_explicit_task(monkeypatch):
    # t2i has 3 registered tasks → must pass task=...
    monkeypatch.setenv("PS_QUEUE_DSN", "postgresql://x@127.0.0.1/q")
    with pytest.raises(ValueError, match="pass task"):
        dispatch_gpu_job("t2i", {"prompt": "x"})


def test_priority_out_of_range_rejected():
    with pytest.raises(ValueError, match="priority"):
        dispatch_gpu_job("t2i", {"prompt": "x"}, task="t2i_flux_dev_h1a", priority=99)


def test_payload_must_be_dict():
    with pytest.raises(TypeError):
        dispatch_gpu_job("t2i", ["not", "a", "dict"], task="t2i_flux_dev_h1a")  # type: ignore[arg-type]


def test_nonzero_returncode_raises(monkeypatch):
    monkeypatch.setenv("PS_QUEUE_DSN", "postgresql://x@127.0.0.1/q")
    monkeypatch.setattr(
        dispatch.subprocess, "run",
        lambda *a, **k: _fake_completed("", returncode=1, stderr="defer boom"),
    )
    with pytest.raises(DispatchError, match="defer boom"):
        dispatch_gpu_job("t2i", {"prompt": "x"}, task="t2i_flux_dev_h1a")


def test_empty_output_raises(monkeypatch):
    monkeypatch.setenv("PS_QUEUE_DSN", "postgresql://x@127.0.0.1/q")
    monkeypatch.setattr(
        dispatch.subprocess, "run", lambda *a, **k: _fake_completed("   \n")
    )
    with pytest.raises(DispatchError, match="no output"):
        dispatch_gpu_job("t2i", {"prompt": "x"}, task="t2i_flux_dev_h1a")
