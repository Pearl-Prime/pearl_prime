"""Regression tests — content_uniqueness truth-source alignment."""
from __future__ import annotations

from pathlib import Path

import pytest

from phoenix_v4.quality.content_uniqueness_truth import (
    DEFAULT_SELLABILITY_UNIQUENESS_TRUTH_SOURCE,
    TRUTH_SOURCE_LEGACY_REGISTRY,
    TRUTH_SOURCE_SHIPPED_SPINE,
    assert_report_truth_source,
    compare_truth_sources,
    enrich_catalog_book_result,
    score_from_registry,
    score_from_shipped_book,
)

REPO = Path(__file__).resolve().parents[1]

BURNOUT_BOOKS = [
    REPO / "artifacts/wave_proof/draft/burnout_overwhelm__corporate_managers/book.txt",
    REPO / "artifacts/wave_proof/draft/burnout_watcher__corporate_managers/book.txt",
    REPO / "artifacts/wave_proof/draft/burnout_grief__corporate_managers/book.txt",
]


@pytest.mark.parametrize("book_path", BURNOUT_BOOKS, ids=[p.parent.name for p in BURNOUT_BOOKS])
def test_shipped_spine_burnout_proof_cells_do_not_fail_trigram_uniqueness(book_path: Path) -> None:
    if not book_path.exists():
        pytest.skip(f"missing proof artifact {book_path}")
    result = score_from_shipped_book(book_path, topic_id="burnout", persona_id="corporate_managers")
    assert result.truth_source == TRUTH_SOURCE_SHIPPED_SPINE
    assert result.content_uniqueness >= 0.99


def test_legacy_registry_burnout_scores_lower_than_shipped() -> None:
    legacy = score_from_registry("burnout")
    assert legacy is not None
    assert legacy.truth_source == TRUTH_SOURCE_LEGACY_REGISTRY
    assert legacy.warning
    book = BURNOUT_BOOKS[0]
    if not book.exists():
        pytest.skip("missing proof book")
    shipped = score_from_shipped_book(book, topic_id="burnout")
    assert shipped.content_uniqueness > legacy.content_uniqueness


def test_legacy_registry_cannot_masquerade_as_sellability_truth() -> None:
    with pytest.raises(ValueError, match="sellability_truth"):
        assert_report_truth_source(
            {
                "truth_source": TRUTH_SOURCE_LEGACY_REGISTRY,
                "warning": "legacy only",
                "sellability_truth": True,
            }
        )


def test_missing_truth_source_rejected() -> None:
    with pytest.raises(ValueError, match="truth_source"):
        assert_report_truth_source({"content_uniqueness": 0.5})


def test_catalog_deep_enrichment_labels_registry() -> None:
    row = enrich_catalog_book_result(
        {"book_id": "p__burnout", "dimensions": {"content_uniqueness": 0.0}},
        "burnout",
    )
    assert row["truth_source"] == TRUTH_SOURCE_LEGACY_REGISTRY
    assert row["sellability_truth"] is False
    assert row["warning"]


def test_compare_truth_sources_diverges_for_burnout() -> None:
    book = BURNOUT_BOOKS[0]
    if not book.exists():
        pytest.skip("missing proof book")
    cmp = compare_truth_sources(book, "burnout", persona_id="corporate_managers")
    assert cmp["default_sellability_truth_source"] == DEFAULT_SELLABILITY_UNIQUENESS_TRUTH_SOURCE
    assert cmp["measurement_path_divergence"] is True
    assert cmp["shipped_spine_book"]["content_uniqueness"] >= 0.99
    assert cmp["legacy_registry_artifact"]["content_uniqueness"] < cmp["shipped_spine_book"]["content_uniqueness"]
