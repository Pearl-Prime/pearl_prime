"""Unit tests for PR changed-files resolution (gh pr diff vs gh pr view fallback)."""

from __future__ import annotations

import json
import subprocess
from unittest.mock import patch

import pytest

from scripts.ci import pr_governance_review as gov


def _completed(
    returncode: int,
    stdout: str = "",
    stderr: str = "",
) -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(
        args=[],
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )


def test_get_changed_files_uses_diff_when_name_status_present(capsys):
    diff_out = "M\tscripts/ci/example.py\nA\tdocs/foo.md\n"
    view_json = {"files": [{"path": "ignored.py", "changeType": "ADDED"}]}

    def fake_run(cmd, **kwargs):
        if cmd[:3] == ["gh", "pr", "diff"] and cmd[3:] == ["99", "--name-status"]:
            return _completed(0, diff_out)
        if cmd[:4] == ["gh", "pr", "view", "99"] and "--json" in cmd:
            return _completed(0, json.dumps(view_json))
        pytest.fail(f"unexpected cmd: {cmd!r}")

    with patch.object(gov.subprocess, "run", side_effect=fake_run):
        files = gov.get_changed_files("99")

    assert files == [
        {"status": "M", "path": "scripts/ci/example.py"},
        {"status": "A", "path": "docs/foo.md"},
    ]
    err = capsys.readouterr().err
    assert "changed_files_source=gh_pr_diff_name_status" in err
    assert "gh_pr_view" not in err


def test_get_changed_files_falls_back_when_diff_nonzero(capsys):
    view_payload = {
        "files": [
            {"path": "a.py", "changeType": "MODIFIED"},
            {"path": "b.yaml", "changeType": "ADDED"},
        ]
    }

    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        if cmd[:3] == ["gh", "pr", "diff"]:
            return _completed(1, "", "unknown flag: --name-status")
        if cmd[:4] == ["gh", "pr", "view", "100"] and "--json" in cmd:
            return _completed(0, json.dumps(view_payload))
        pytest.fail(f"unexpected cmd: {cmd!r}")

    with patch.object(gov.subprocess, "run", side_effect=fake_run):
        files = gov.get_changed_files("100")

    assert len(calls) == 2
    assert files == [
        {"status": "M", "path": "a.py"},
        {"status": "A", "path": "b.yaml"},
    ]
    err = capsys.readouterr().err
    assert "changed_files_source=gh_pr_view_json_files" in err
    assert "gh_pr_diff_rc=1" in err


def test_get_changed_files_falls_back_when_diff_stdout_empty(capsys):
    view_payload = {
        "files": [
            {"path": "x.md", "changeType": "REMOVED"},
        ]
    }

    def fake_run(cmd, **kwargs):
        if cmd[:3] == ["gh", "pr", "diff"]:
            return _completed(0, "   \n")
        if cmd[:4] == ["gh", "pr", "view", "101"] and "--json" in cmd:
            return _completed(0, json.dumps(view_payload))
        pytest.fail(f"unexpected cmd: {cmd!r}")

    with patch.object(gov.subprocess, "run", side_effect=fake_run):
        files = gov.get_changed_files("101")

    assert files == [{"status": "D", "path": "x.md"}]
    err = capsys.readouterr().err
    assert "changed_files_source=gh_pr_view_json_files" in err
    assert "empty_or_failed_diff" in err


def test_get_changed_files_fallback_when_diff_unparseable(capsys):
    view_payload = {"files": [{"path": "ok.py", "changeType": "ADDED"}]}

    def fake_run(cmd, **kwargs):
        if cmd[:3] == ["gh", "pr", "diff"]:
            return _completed(0, "not-a-name-status-line\n")
        if cmd[:4] == ["gh", "pr", "view", "102"] and "--json" in cmd:
            return _completed(0, json.dumps(view_payload))
        pytest.fail(f"unexpected cmd: {cmd!r}")

    with patch.object(gov.subprocess, "run", side_effect=fake_run):
        files = gov.get_changed_files("102")

    assert files == [{"status": "A", "path": "ok.py"}]
    err = capsys.readouterr().err
    assert "gh_pr_view_json_files" in err
    assert "gh_pr_diff_unparseable" in err
