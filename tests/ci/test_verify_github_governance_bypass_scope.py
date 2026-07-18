"""Bypass-detection scope for verify_github_governance (Phase 1 CI recovery)."""

from __future__ import annotations

from scripts.ci.verify_github_governance import REPO_ROOT, text_has_forbidden_bypass_logic

# Mirrors legitimate ruleset API usage in scripts/ci/check_branch_protection_ruleset.py
LEGITIMATE_RULESET_READER = '''
    for actor in data.get("bypass_actors", []):
        mode = actor.get("bypass_mode")
        if mode != EXPECTED_BYPASS_MODE:
            failures.append(
                f"bypass_actor {actor.get('actor_id')} has bypass_mode={mode!r}, expected {EXPECTED_BYPASS_MODE!r}"
            )
'''


def test_api_field_bypass_actors_reference_is_not_flagged():
    assert not text_has_forbidden_bypass_logic(LEGITIMATE_RULESET_READER)


def test_check_branch_protection_ruleset_on_disk_passes():
    path = REPO_ROOT / "scripts" / "ci" / "check_branch_protection_ruleset.py"
    assert path.is_file()
    assert not text_has_forbidden_bypass_logic(path.read_text(encoding="utf-8"))


def test_json_bypass_mode_always_is_flagged():
    malicious = 'body = {"bypass_mode": "always", "actor_id": 1}'
    assert text_has_forbidden_bypass_logic(malicious)


def test_python_bypass_mode_always_assignment_is_flagged():
    # Adjacent assignment / kwarg forms, not legitimate actor.get("bypass_mode") reads.
    assert text_has_forbidden_bypass_logic('bypass_mode = "always"')
    assert text_has_forbidden_bypass_logic("patch = dict(bypass_mode='always')")


def test_enforcement_disabled_literal_is_flagged():
    assert text_has_forbidden_bypass_logic('rules: { enforcement: "disabled" }')
