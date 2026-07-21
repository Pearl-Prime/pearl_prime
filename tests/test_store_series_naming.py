from __future__ import annotations

from pathlib import Path

import yaml

from phoenix_v4.naming.generator import (
    generate_store_series_candidates,
    is_generic_store_series_name,
)
from scripts.catalog.dry_run_store_series_names import build_dry_run


def test_store_series_candidates_require_operator_review_and_reject_generic():
    candidates = generate_store_series_candidates(
        brand_id="cognitive_clarity",
        topic_id="overthinking",
        persona_id="general_readers",
        seed="unit",
    )

    assert candidates
    assert not any(is_generic_store_series_name(c["series_title"], "overthinking") for c in candidates)
    assert all(c["operator_review_status"] == "required_before_storefront" for c in candidates)
    assert all(c["production_public_release_authorized"] is False for c in candidates)
    assert is_generic_store_series_name("Overthinking Series", "overthinking")


def test_store_series_dry_run_writes_no_catalog_files(tmp_path):
    plan = tmp_path / "brand_series_plans.yaml"
    plan.write_text(
        yaml.safe_dump(
            {
                "brands": {
                    "cognitive_clarity": {"primary_topic": "overthinking"},
                    "somatic_wisdom": {"primary_topic": "anxiety"},
                }
            }
        ),
        encoding="utf-8",
    )

    report = build_dry_run(plan_path=plan)

    assert report["catalog_files_written"] is False
    assert report["stats"]["brands"] == 2
    assert report["stats"]["series_names_generated"] >= 2
