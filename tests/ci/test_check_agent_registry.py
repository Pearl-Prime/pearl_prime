"""Unit tests for scripts/ci/check_agent_registry.py (P0-1 validator).

Self-contained: every test writes its own temp registry/map fixtures and points the
validator's path-accepting entrypoints at them, so the tests are deterministic and do
not depend on the live repo state. A final test exercises the validator against the
REAL repo files and asserts only that it runs and returns a defined exit code.
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest

from scripts.ci import check_agent_registry as car


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------
MAP_HEADER = "subsystem_id\tauthority_doc\tconfig_path\towner_agent\tstatus\n"


def write_map(tmp_path: Path, rows: list[tuple[str, str, str]]) -> Path:
    """rows = [(subsystem_id, owner_agent, status), ...]."""
    p = tmp_path / "SUBSYSTEM_AUTHORITY_MAP.tsv"
    lines = [MAP_HEADER]
    for sid, owner, status in rows:
        lines.append(f"{sid}\tdocs/x.md\tconfig/x.yaml\t{owner}\t{status}\n")
    p.write_text("".join(lines), encoding="utf-8")
    return p


def write_registry(tmp_path: Path, body: str) -> Path:
    p = tmp_path / "agent_registry.yaml"
    p.write_text(textwrap.dedent(body), encoding="utf-8")
    return p


def _vios(findings):
    return [f for f in findings if f["severity"] == car.SEV_VIOLATION]


def _infos(findings):
    return [f for f in findings if f["severity"] == car.SEV_INFO]


# ---------------------------------------------------------------------------
# RULE 1 — coverage
# ---------------------------------------------------------------------------
def test_exactly_one_owner_passes(tmp_path):
    reg = write_registry(
        tmp_path,
        """
        schema_version: "1.0"
        agents:
          pearl_a:
            display_name: "Pearl_A"
            skill_path: null
            subsystems: [sub_one]
          pearl_b:
            display_name: "Pearl_B"
            skill_path: null
            subsystems: [sub_two]
        """,
    )
    mp = write_map(tmp_path, [("sub_one", "Pearl_A", "active"), ("sub_two", "Pearl_B", "active")])
    findings = car.validate(car.load_registry(reg), car.load_map_subsystems(mp)[0], reg)
    assert _vios(findings) == []


def test_orphan_subsystem_is_violation(tmp_path):
    reg = write_registry(
        tmp_path,
        """
        agents:
          pearl_a:
            skill_path: null
            subsystems: [sub_one]
        """,
    )
    # sub_two has a single (non-multi) owner and no agent claims it -> ORPHAN -> violation.
    mp = write_map(tmp_path, [("sub_one", "Pearl_A", "active"), ("sub_two", "Pearl_DevOps", "active")])
    findings = car.validate(car.load_registry(reg), car.load_map_subsystems(mp)[0], reg)
    vios = _vios(findings)
    assert len(vios) == 1
    assert vios[0]["subsystem_id"] == "sub_two"
    assert vios[0]["rule"] == "coverage"
    assert "ORPHAN" in vios[0]["message"]


def test_orphan_suppressed_when_map_owner_is_multi(tmp_path):
    """A '+'-joined owner_agent in the map declares shared ownership -> INFO, not violation."""
    reg = write_registry(
        tmp_path,
        """
        agents:
          pearl_a:
            skill_path: null
            subsystems: [sub_one]
        """,
    )
    mp = write_map(
        tmp_path,
        [
            ("sub_one", "Pearl_A", "active"),
            ("sub_shared", "Pearl_Int (operations) + Pearl_Architect (spec)", "proposed"),
        ],
    )
    findings = car.validate(car.load_registry(reg), car.load_map_subsystems(mp)[0], reg)
    assert _vios(findings) == []
    infos = [f for f in _infos(findings) if f["subsystem_id"] == "sub_shared"]
    assert len(infos) == 1


def test_orphan_suppressed_when_notes_document_shared(tmp_path):
    reg = write_registry(
        tmp_path,
        """
        agents:
          pearl_a:
            skill_path: null
            subsystems: [sub_one]
            notes: "sub_shared is shared across Pearl_A and Pearl_B; intentionally not in subsystems."
        """,
    )
    mp = write_map(tmp_path, [("sub_one", "Pearl_A", "active"), ("sub_shared", "Pearl_Solo", "active")])
    findings = car.validate(car.load_registry(reg), car.load_map_subsystems(mp)[0], reg)
    assert _vios(findings) == []
    assert any(f["subsystem_id"] == "sub_shared" for f in _infos(findings))


def test_over_claimed_undocumented_is_violation(tmp_path):
    reg = write_registry(
        tmp_path,
        """
        agents:
          pearl_a:
            skill_path: null
            subsystems: [sub_one]
          pearl_b:
            skill_path: null
            subsystems: [sub_one]
        """,
    )
    mp = write_map(tmp_path, [("sub_one", "Pearl_A", "active")])
    findings = car.validate(car.load_registry(reg), car.load_map_subsystems(mp)[0], reg)
    vios = _vios(findings)
    assert len(vios) == 1
    assert "OVER-CLAIMED" in vios[0]["message"]
    assert vios[0]["subsystem_id"] == "sub_one"


def test_registry_subsystem_not_in_map_is_info(tmp_path):
    reg = write_registry(
        tmp_path,
        """
        agents:
          pearl_a:
            skill_path: null
            subsystems: [sub_one, proposed_sub]
        """,
    )
    mp = write_map(tmp_path, [("sub_one", "Pearl_A", "active")])
    findings = car.validate(car.load_registry(reg), car.load_map_subsystems(mp)[0], reg)
    assert _vios(findings) == []
    assert any(f["subsystem_id"] == "proposed_sub" for f in _infos(findings))


# ---------------------------------------------------------------------------
# RULE 2 — skill_path null-or-exists
# ---------------------------------------------------------------------------
def test_skill_path_null_ok(tmp_path):
    reg = write_registry(
        tmp_path,
        """
        agents:
          pearl_a:
            skill_path: null
            subsystems: [sub_one]
        """,
    )
    mp = write_map(tmp_path, [("sub_one", "Pearl_A", "active")])
    findings = car.validate(car.load_registry(reg), car.load_map_subsystems(mp)[0], reg)
    assert [f for f in _vios(findings) if f["rule"] == "skill_path"] == []


def test_skill_path_missing_is_violation(tmp_path):
    reg = write_registry(
        tmp_path,
        """
        agents:
          pearl_a:
            skill_path: skills/does-not-exist/SKILL.md
            subsystems: [sub_one]
        """,
    )
    mp = write_map(tmp_path, [("sub_one", "Pearl_A", "active")])
    findings = car.validate(car.load_registry(reg), car.load_map_subsystems(mp)[0], reg)
    sp_vios = [f for f in _vios(findings) if f["rule"] == "skill_path"]
    assert len(sp_vios) == 1
    assert sp_vios[0]["agent"] == "pearl_a"


def test_skill_path_existing_ok(tmp_path):
    # Point at a file we know exists on disk relative to REPO_ROOT.
    existing_rel = "scripts/ci/check_agent_registry.py"
    assert (car.REPO_ROOT / existing_rel).exists(), "test precondition: validator file present in repo"
    reg = write_registry(
        tmp_path,
        f"""
        agents:
          pearl_a:
            skill_path: {existing_rel}
            subsystems: [sub_one]
        """,
    )
    mp = write_map(tmp_path, [("sub_one", "Pearl_A", "active")])
    findings = car.validate(car.load_registry(reg), car.load_map_subsystems(mp)[0], reg)
    assert [f for f in _vios(findings) if f["rule"] == "skill_path"] == []


# ---------------------------------------------------------------------------
# Loaders / error handling
# ---------------------------------------------------------------------------
def test_missing_registry_returns_load_error(tmp_path):
    err = car.load_registry(tmp_path / "nope.yaml")
    assert err.get("__load_error")


def test_missing_map_returns_error(tmp_path):
    rows, err = car.load_map_subsystems(tmp_path / "nope.tsv")
    assert rows == []
    assert err


def test_run_exit_codes_and_json(tmp_path, capsys):
    # Clean fixture -> exit 0.
    reg_ok = write_registry(
        tmp_path,
        """
        agents:
          pearl_a:
            skill_path: null
            subsystems: [sub_one]
        """,
    )
    mp_ok = write_map(tmp_path, [("sub_one", "Pearl_A", "active")])
    rc = car.run(reg_ok, mp_ok, as_json=True)
    out = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert out["ok"] is True
    assert out["counts"]["violations"] == 0

    # Orphan fixture -> exit 1, JSON ok=False.
    mp_bad = write_map(tmp_path, [("sub_one", "Pearl_A", "active"), ("orphan_sub", "Pearl_Solo", "active")])
    rc2 = car.run(reg_ok, mp_bad, as_json=True)
    out2 = json.loads(capsys.readouterr().out)
    assert rc2 == 1
    assert out2["ok"] is False
    assert out2["counts"]["violations"] >= 1


def test_load_error_exit_code_2(tmp_path, capsys):
    rc = car.run(tmp_path / "missing.yaml", tmp_path / "missing.tsv", as_json=True)
    out = json.loads(capsys.readouterr().out)
    assert rc == 2
    assert out["ok"] is False
    assert out["load_error"]


# ---------------------------------------------------------------------------
# Smoke test against the REAL repo files (does not assert pass/fail — state may drift)
# ---------------------------------------------------------------------------
def test_real_repo_runs_and_returns_defined_code(capsys):
    rc = car.run(car.DEFAULT_REGISTRY, car.DEFAULT_MAP, as_json=True)
    out = json.loads(capsys.readouterr().out)
    assert rc in (0, 1, 2)
    assert "ok" in out
    assert "findings" in out
