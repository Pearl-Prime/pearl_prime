"""
Fast smoke tests for scripts/catalog/build_catalog_analysis_bundle.py.

Does not run generate_catalog() or the full bundle (too slow for default CI).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.catalog import build_catalog_analysis_bundle as bundle


@pytest.mark.sanity
def test_build_catalog_analysis_bundle_imports():
    assert bundle.CATALOG_DIR.name == "catalog"
    assert bundle.DOCS_DIR.name == "produced"


@pytest.mark.sanity
def test_build_combo_dashboard_merges_duplicate_combos():
    rows = [
        {
            "lane_id": "en_US",
            "brand_id": "demo_brand",
            "teacher_id": "demo_teacher",
            "topic_id": "anxiety",
            "persona_id": "corporate_managers",
            "format_id": "F003",
            "runtime_format_id": "short_book_30",
            "content_type": "series_book",
            "priority": "WAVE_1",
            "catalog_id": "CAT-AAA",
            "title": "First Title",
        },
        {
            "lane_id": "en_US",
            "brand_id": "demo_brand",
            "teacher_id": "demo_teacher",
            "topic_id": "anxiety",
            "persona_id": "corporate_managers",
            "format_id": "F003",
            "runtime_format_id": "short_book_30",
            "content_type": "series_book",
            "priority": "WAVE_1",
            "catalog_id": "CAT-BBB",
            "title": "Second Title",
        },
    ]
    out = bundle.build_combo_dashboard(rows)
    assert len(out) == 1
    assert out[0]["title_count"] == 2
    assert out[0]["sample_catalog_id"] == "CAT-AAA"
