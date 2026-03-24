"""Policy checks for writer-handoff transmission leakage."""

from __future__ import annotations

from typing import Any

FORBIDDEN_WRITER_HANDOFF_KEYS = frozenset(
    {
        "carrier_beat",
        "is_carrier_beat",
        "somatic_intention",
        "somatic_target",
        "hiding_place",
    }
)


def _walk(obj: Any, path: str) -> list[str]:
    violations: list[str] = []
    if isinstance(obj, dict):
        for key, val in obj.items():
            if key in FORBIDDEN_WRITER_HANDOFF_KEYS:
                violations.append(f"{path}.{key}" if path else key)
            violations.extend(_walk(val, f"{path}.{key}" if path else key))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            violations.extend(_walk(item, f"{path}[{i}]"))
    return violations


def assert_handoff_has_no_transmission_leakage(payload: dict[str, Any]) -> None:
    bad = _walk(payload, "")
    if bad:
        raise AssertionError("Transmission leakage in handoff: " + ", ".join(sorted(bad)))
