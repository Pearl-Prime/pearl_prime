"""
Regression Museum runner. Loads the YAML config, dispatches each failure_class
to its detector, and returns a structured result.

Usage:
    from phoenix_v4.quality.regression_museum import run_museum_gates
    result = run_museum_gates(book, persona="gen_z_professionals")
    if result["blocked"]:
        sys.exit(1)
"""

import yaml
import inspect
from pathlib import Path
from typing import Optional

from phoenix_v4.quality.regression_museum import detectors as _det_module
from phoenix_v4.quality.regression_museum.detectors import Violation

_DEFAULT_CONFIG = Path(__file__).parent.parent.parent.parent / "config" / "governance" / "regression_museum.yaml"


def run_museum_gates(
    book: dict,
    persona: str = "",
    config_path: Optional[Path] = None,
) -> dict:
    """
    Returns:
        {
            "violations": list[Violation],
            "blocked": bool,
            "warned": bool,
            "summary": str,
            "by_class": dict[str, list[Violation]],
        }
    """
    config_path = config_path or _DEFAULT_CONFIG
    config = yaml.safe_load(config_path.read_text())
    failure_classes = config.get("failure_classes", {})

    all_violations: list[Violation] = []
    by_class: dict[str, list[Violation]] = {}

    for class_name, spec in failure_classes.items():
        fn_name = f"detect_{class_name}"
        fn = getattr(_det_module, fn_name, None)
        if fn is None:
            continue

        # Build kwargs the detector accepts
        sig = inspect.signature(fn)
        kwargs: dict = {}
        if "persona" in sig.parameters:
            kwargs["persona"] = persona
        if "config" in sig.parameters:
            kwargs["config"] = spec
        # Pass scalar spec fields that match detector params
        for key, val in spec.items():
            if key in sig.parameters and key not in ("persona", "config"):
                kwargs[key] = val

        violations = fn(book, **kwargs)
        by_class[class_name] = violations
        all_violations.extend(violations)

    blocked = any(v.severity == "block" for v in all_violations)
    warned = any(v.severity in ("warn", "warn_then_block") for v in all_violations)
    n_block = sum(1 for v in all_violations if v.severity == "block")
    n_warn = len(all_violations) - n_block

    return {
        "violations": all_violations,
        "blocked": blocked,
        "warned": warned,
        "by_class": by_class,
        "summary": (
            f"{len(all_violations)} violation(s): {n_block} blocking, {n_warn} warnings"
            if all_violations
            else "All museum gates passed. No violations."
        ),
    }
