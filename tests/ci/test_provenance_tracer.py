"""Tests for the §18 provenance tracer (docs/agent_brief.txt §18).

Covers:
  - check_provenance()               — PR-time §18 block guard (pr_governance_review)
  - check_capability_regression      — the no-lost-functions dictionary-diff gate
  - _parse_provenance_block()        — the PROVENANCE-block parser

Mirrors the fixture style of test_pr_governance_guards.py.
"""
from __future__ import annotations

from scripts.ci import pr_governance_review as gov
from scripts.ci import check_capability_regression as reg


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------

def _files(*pairs):
    return [{"status": s, "path": p} for s, p in pairs]


# A minimal governed-subsystem map (config_path prefix → subsystem info), shaped like
# load_subsystem_map()'s output.
_SMAP = {
    "phoenix_v4/planning/": {"subsystem_id": "pearl_prime", "authority_docs": [], "owner_agent": "Pearl_Prime"},
    "docs/specs/": {"subsystem_id": "core_pipeline", "authority_docs": [], "owner_agent": "Pearl_Prime"},
}

_COMPLETE_BLOCK = (
    "feat(planning): new selector\n\n"
    "PROVENANCE:\n"
    "  research: artifacts/research/foo.md\n"
    "  documents: docs/PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md\n"
    "  builds_on: pearl_prime_story_planner\n"
    "  inventory: EXTENDS\n"
)


# ---------------------------------------------------------------------------
# _parse_provenance_block
# ---------------------------------------------------------------------------

def test_parse_block_all_fields():
    b = gov._parse_provenance_block(_COMPLETE_BLOCK)
    assert b["research"] == "artifacts/research/foo.md"
    assert b["documents"].startswith("docs/")
    assert b["builds_on"] == "pearl_prime_story_planner"
    assert b["inventory"] == "EXTENDS"


def test_parse_block_absent_returns_none():
    assert gov._parse_provenance_block("just a normal PR body, no block") is None
    assert gov._parse_provenance_block("") is None


def test_parse_block_docs_alias_and_bullets():
    b = gov._parse_provenance_block(
        "PROVENANCE:\n- research: NONE\n- docs: docs/x.md\n- builds_on: y\n- inventory: UNCHANGED\n"
    )
    assert b["research"] == "NONE"
    assert b["documents"] == "docs/x.md"  # 'docs:' aliases to 'documents'


# ---------------------------------------------------------------------------
# check_provenance
# ---------------------------------------------------------------------------

def test_provenance_noop_when_no_capability_files():
    res = gov.check_provenance(_files(("M", "phoenix_v4/planning/enrichment_select.py")),
                               _SMAP, "feat: x", "no block")
    assert res["status"] == "PASS"
    assert res["details"]["capability_files"] == 0


def test_provenance_missing_block_warns_report_phase():
    res = gov.check_provenance(_files(("A", "phoenix_v4/planning/new_engine.py")),
                               _SMAP, "feat(planning): new engine", "body without a block")
    # report phase → WARN (flips to BLOCK when PROVENANCE_MISSING_SEVERITY = 'BLOCK')
    assert res["status"] == gov.PROVENANCE_MISSING_SEVERITY
    assert "PROVENANCE" in res["message"]


def test_provenance_research_none_blocks():
    body = ("feat: x\n\nPROVENANCE:\n  research: NONE\n  documents: d\n"
            "  builds_on: b\n  inventory: EXTENDS\n")
    res = gov.check_provenance(_files(("A", "phoenix_v4/planning/new_engine.py")),
                               _SMAP, "feat: x", body)
    assert res["status"] == "BLOCKED"
    assert "Pearl_Research" in res["message"]


def test_provenance_complete_block_passes():
    res = gov.check_provenance(_files(("A", "phoenix_v4/planning/new_engine.py")),
                               _SMAP, "feat(planning): new selector", _COMPLETE_BLOCK)
    assert res["status"] == "PASS"


def test_provenance_bugfix_class_exempt_even_without_block():
    res = gov.check_provenance(_files(("A", "phoenix_v4/planning/new_engine.py")),
                               _SMAP, "fix(planning): null-guard", "no block at all")
    assert res["status"] == "PASS"
    assert res["details"]["class"] == "bugfix"


def test_provenance_bugfix_research_none_still_exempt():
    # DO-NOT: never block a bugfix-class PR on research.
    body = "fix: y\n\nPROVENANCE:\n  research: NONE\n"
    res = gov.check_provenance(_files(("A", "phoenix_v4/planning/new_engine.py")),
                               _SMAP, "fix: y", body)
    assert res["status"] == "PASS"


def test_provenance_ungoverned_new_file_is_noop():
    res = gov.check_provenance(_files(("A", "random/place/thing.py")),
                               _SMAP, "feat: x", "no block")
    assert res["status"] == "PASS"


def test_provenance_new_spec_doc_is_capability():
    res = gov.check_provenance(_files(("A", "docs/specs/NEW_THING_SPEC.md")),
                               _SMAP, "feat: spec", "no block")
    assert res["status"] == gov.PROVENANCE_MISSING_SEVERITY  # a new spec is a capability contract


def test_provenance_test_file_not_capability():
    res = gov.check_provenance(_files(("A", "phoenix_v4/planning/tests/test_new.py")),
                               _SMAP, "feat: x", "no block")
    assert res["status"] == "PASS"


def test_provenance_reduced_inventory_surfaces_regression_note():
    body = ("PROVENANCE:\n  research: artifacts/research/foo.md\n  documents: d\n"
            "  builds_on: b\n  inventory: REDUCED\n")
    res = gov.check_provenance(_files(("A", "phoenix_v4/planning/new_engine.py")),
                               _SMAP, "feat: x", body)
    assert res["status"] == "PASS"
    assert "check_capability_regression" in res["message"]


def test_provenance_negated_reduced_does_not_trip_note():
    # "no function REDUCED" / the §18 template's "never REDUCED" must NOT fire the note.
    body = ("PROVENANCE:\n  research: artifacts/research/foo.md\n  documents: d\n"
            "  builds_on: b\n  inventory: EXTENDS; UNCHANGED — no function REDUCED\n")
    res = gov.check_provenance(_files(("A", "phoenix_v4/planning/new_engine.py")),
                               _SMAP, "feat: x", body)
    assert res["status"] == "PASS"
    assert "will require CAPABILITY-RETIREMENT-RATIFIED" not in res["message"]


# ---------------------------------------------------------------------------
# check_capability_regression — pure logic
# ---------------------------------------------------------------------------

def test_parse_dict_text():
    text = "path\tpurpose\tsubsystem\towner\tconsumers\tstatus\na.py\tx\ts\to\tc\tWIRED\nb.py\ty\ts\to\tc\tUNWIRED\n"
    m = reg._parse_dict_text(text)
    assert m == {"a.py": "WIRED", "b.py": "UNWIRED"}


def test_parse_dict_text_empty():
    assert reg._parse_dict_text("") == {}
    assert reg._parse_dict_text("path\tstatus\n") == {}


def test_has_ratify_token_requires_reason():
    assert reg._has_ratify_token("CAPABILITY-RETIREMENT-RATIFIED: OPD-20260709-001 merged x into y")
    assert not reg._has_ratify_token("CAPABILITY-RETIREMENT-RATIFIED:")
    assert not reg._has_ratify_token("nothing here")
    assert not reg._has_ratify_token("")


def test_find_regressions_detects_removed_and_orphaned(monkeypatch, tmp_path):
    baseline = ("path\tpurpose\tsubsystem\towner\tconsumers\tstatus\n"
                "kept.py\t\t\t\t\tWIRED\n"
                "removed.py\t\t\t\t\tWIRED\n"
                "orphaned.py\t\t\t\t\tWIRED\n"
                "already_unwired.py\t\t\t\t\tUNWIRED\n")
    monkeypatch.setattr(reg, "_git_show", lambda ref_path, root: baseline)
    monkeypatch.setattr(reg, "_head_status_map", lambda root: {
        "kept.py": "WIRED",
        "orphaned.py": "KNOWN_UNWIRED",
        "already_unwired.py": "UNWIRED",
        # removed.py absent
    })
    regs, available = reg.find_regressions(tmp_path, "origin/main")
    assert available is True
    paths = {(r.path, r.head_status) for r in regs}
    assert ("removed.py", "REMOVED") in paths
    assert ("orphaned.py", "KNOWN_UNWIRED") in paths
    # kept.py (still WIRED) and already_unwired.py (was not WIRED) are NOT regressions
    assert not any(r.path == "kept.py" for r in regs)
    assert not any(r.path == "already_unwired.py" for r in regs)


def test_find_regressions_fail_open_when_baseline_unreadable(monkeypatch, tmp_path):
    monkeypatch.setattr(reg, "_git_show", lambda ref_path, root: None)
    regs, available = reg.find_regressions(tmp_path, "origin/main")
    assert regs == []
    assert available is False


def test_main_fail_open_returns_zero(monkeypatch, tmp_path):
    monkeypatch.setattr(reg, "_git_show", lambda ref_path, root: None)
    assert reg.main(["--repo-root", str(tmp_path), "--baseline-ref", "origin/main"]) == 0


def test_main_blocks_unratified_regression(monkeypatch, tmp_path):
    baseline = "path\tpurpose\tsubsystem\towner\tconsumers\tstatus\ngone.py\t\t\t\t\tWIRED\n"
    monkeypatch.setattr(reg, "_git_show", lambda ref_path, root: baseline)
    monkeypatch.setattr(reg, "_head_status_map", lambda root: {})  # gone.py removed
    monkeypatch.setattr(reg, "_collect_ratify_text", lambda root, ref: "")  # no tag
    assert reg.main(["--repo-root", str(tmp_path), "--baseline-ref", "origin/main"]) == 1


def test_main_passes_ratified_regression(monkeypatch, tmp_path):
    baseline = "path\tpurpose\tsubsystem\towner\tconsumers\tstatus\ngone.py\t\t\t\t\tWIRED\n"
    monkeypatch.setattr(reg, "_git_show", lambda ref_path, root: baseline)
    monkeypatch.setattr(reg, "_head_status_map", lambda root: {})
    monkeypatch.setattr(reg, "_collect_ratify_text", lambda root, ref:
                        "CAPABILITY-RETIREMENT-RATIFIED: OPD-20260709-001 folded into unified gate")
    assert reg.main(["--repo-root", str(tmp_path), "--baseline-ref", "origin/main"]) == 0
