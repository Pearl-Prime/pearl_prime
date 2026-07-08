"""CI gate smoke for accent plan assignment."""
from scripts.ci.check_accent_plan_assignment import CANONICAL_CASES, audit_case


def test_canonical_accent_plan_assignment_passes():
    result = audit_case(CANONICAL_CASES[0])
    assert result["pass"], result.get("errors")
