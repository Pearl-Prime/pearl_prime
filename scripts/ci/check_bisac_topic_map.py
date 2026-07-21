#!/usr/bin/env python3
"""Validate the anxiety-family topic-to-BISAC floor.

RN-5 refresh: the generators already map anxiety-family topics to
``SEL036000``. This checker guards that mapping without rewriting catalog files.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable

import yaml

from scripts.catalog import flip_authoring_skeletons, gen_plan_skeletons

EXPECTED_TOPIC_BISAC = {
    "anxiety": ["SEL036000", "SEL024000", "SEL031000"],
    "sleep_anxiety": ["SEL036000", "SEL024000", "SEL031000"],
    "social_anxiety": ["SEL036000", "SEL024000", "SEL031000"],
    "financial_anxiety": ["SEL036000", "SEL024000", "SEL031000"],
    "overthinking": ["SEL036000", "SEL024000", "SEL031000"],
}


def _validate_sequence(topic: str, codes: Iterable[str], source: str) -> list[str]:
    got = list(codes or [])
    expected = EXPECTED_TOPIC_BISAC[topic]
    if got[: len(expected)] != expected:
        return [
            f"{source}: topic={topic} expected leading BISAC {expected}, got {got}"
        ]
    return []


def _validate_lead(topic: str, codes: Iterable[str], source: str) -> list[str]:
    got = list(codes or [])
    expected = EXPECTED_TOPIC_BISAC[topic][0]
    if not got or got[0] != expected:
        return [f"{source}: topic={topic} expected lead BISAC {expected}, got {got}"]
    return []


def validate_generator_maps() -> list[str]:
    errors: list[str] = []
    for topic in EXPECTED_TOPIC_BISAC:
        errors.extend(
            _validate_sequence(
                topic,
                gen_plan_skeletons.topic_bisac(topic),
                "scripts/catalog/gen_plan_skeletons.py",
            )
        )
        errors.extend(
            _validate_sequence(
                topic,
                flip_authoring_skeletons._topic_bisac(topic),
                "scripts/catalog/flip_authoring_skeletons.py",
            )
        )
    return errors


def validate_sample_plan(path: Path) -> list[str]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    topic = str(data.get("topic") or "")
    if not topic and data.get("book_id"):
        parts = str(data["book_id"]).split("__")
        if len(parts) >= 4:
            topic = parts[3]
    if topic not in EXPECTED_TOPIC_BISAC:
        return []
    return _validate_lead(topic, data.get("bisac_codes") or [], str(path))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sample-plan",
        action="append",
        type=Path,
        default=[],
        help="Existing book_plan YAML to validate in addition to generator maps.",
    )
    args = parser.parse_args()

    errors = validate_generator_maps()
    for sample in args.sample_plan:
        if not sample.exists():
            errors.append(f"{sample}: sample plan missing")
            continue
        errors.extend(validate_sample_plan(sample))

    if errors:
        print("BISAC topic map check FAILED")
        for err in errors:
            print(f"  {err}")
        return 1

    print("BISAC topic map check PASSED")
    print(f"  topics_checked={len(EXPECTED_TOPIC_BISAC)}")
    print(f"  sample_plans_checked={len(args.sample_plan)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
