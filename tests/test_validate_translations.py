#!/usr/bin/env python3
"""Tests for scripts/validate_translations.py."""
from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from scripts.validate_translations import (
    check_glossary,
    check_golden_segments,
    check_thresholds,
    discover_translated_files,
    fuzzy_match,
    glossary_coverage,
    run_validation,
)


# ── Fixtures ───────────────────────────────────────────────────────────────

@pytest.fixture
def tmp_atoms(tmp_path):
    """Create a minimal atoms tree with one translated file."""
    locale = "ja-JP"
    atom_dir = tmp_path / "atoms" / "educators" / "anxiety" / "PIVOT"
    atom_dir.mkdir(parents=True)
    (atom_dir / "CANONICAL.txt").write_text("English source text", encoding="utf-8")

    locale_dir = atom_dir / "locales" / locale
    locale_dir.mkdir(parents=True)
    (locale_dir / "CANONICAL.txt").write_text(
        "不安リセット は正しい翻訳です。\n落ち着きの技法 も含まれています。",
        encoding="utf-8",
    )
    return tmp_path / "atoms"


@pytest.fixture
def glossary_terms():
    return [
        {
            "id": "anxiety_reset",
            "en_US": "Anxiety Reset",
            "ja-JP": "不安リセット",
            "ja-JP_forbidden": ["アンキシエティリセット"],
        },
        {
            "id": "calm_technique",
            "en_US": "Calming Technique",
            "ja-JP": "落ち着きの技法",
            "ja-JP_forbidden": ["カーミングテクニック"],
        },
    ]


@pytest.fixture
def golden_segments():
    return [
        {
            "id": "golden_1",
            "en_US": "Your nervous system fires an alarm.",
            "ja-JP": "あなたの神経系が警報を発します。",
        },
    ]


# ── Glossary: correct translation → pass ──────────────────────────────────

class TestGlossaryCheck:
    def test_preferred_term_present_passes(self, glossary_terms):
        text = "不安リセット は効果的な方法です。"
        results = check_glossary(text, glossary_terms, "ja-JP")
        anxiety_result = next(r for r in results if r["term_id"] == "anxiety_reset")
        assert anxiety_result["passed"] is True

    def test_forbidden_alternative_fails(self, glossary_terms):
        text = "アンキシエティリセット を試してみましょう。"
        results = check_glossary(text, glossary_terms, "ja-JP")
        anxiety_result = next(r for r in results if r["term_id"] == "anxiety_reset")
        assert anxiety_result["passed"] is False
        assert anxiety_result["found"] == "アンキシエティリセット"

    def test_missing_preferred_does_not_hard_fail(self, glossary_terms):
        text = "この文章には用語が含まれていません。"
        results = check_glossary(text, glossary_terms, "ja-JP")
        # No forbidden terms → all pass (absence doesn't fail, just lowers coverage)
        assert all(r["passed"] for r in results)

    def test_no_terms_for_locale_returns_empty(self):
        terms = [{"id": "t1", "en_US": "Test", "ko-KR": "테스트"}]
        results = check_glossary("Some text", terms, "ja-JP")
        assert results == []

    def test_coverage_full(self, glossary_terms):
        text = "不安リセット と 落ち着きの技法 の両方が含まれます。"
        results = check_glossary(text, glossary_terms, "ja-JP")
        cov = glossary_coverage(results, text)
        assert cov == 1.0

    def test_coverage_partial(self, glossary_terms):
        text = "不安リセット だけが含まれます。"
        results = check_glossary(text, glossary_terms, "ja-JP")
        cov = glossary_coverage(results, text)
        assert cov == 0.5

    def test_coverage_zero(self, glossary_terms):
        text = "何も含まれていない。"
        results = check_glossary(text, glossary_terms, "ja-JP")
        cov = glossary_coverage(results, text)
        assert cov == 0.0

    def test_coverage_no_terms(self):
        cov = glossary_coverage([], "anything")
        assert cov == 1.0


# ── Golden regression ─────────────────────────────────────────────────────

class TestGoldenRegression:
    def test_exact_match_passes(self, tmp_path, golden_segments):
        fp = tmp_path / "translated.txt"
        fp.write_text("あなたの神経系が警報を発します。", encoding="utf-8")
        results = check_golden_segments([fp], golden_segments, "ja-JP")
        assert len(results) == 1
        assert results[0]["passed"] is True
        assert results[0]["similarity"] == 1.0

    def test_close_match_passes(self, tmp_path, golden_segments):
        fp = tmp_path / "translated.txt"
        # Minor variation (extra space, slightly different phrasing)
        fp.write_text("あなたの神経系が 警報を発します。", encoding="utf-8")
        results = check_golden_segments([fp], golden_segments, "ja-JP", fuzzy_threshold=0.80)
        assert len(results) == 1
        assert results[0]["passed"] is True

    def test_major_deviation_fails(self, tmp_path, golden_segments):
        fp = tmp_path / "translated.txt"
        fp.write_text("完全に異なるテキストです。", encoding="utf-8")
        results = check_golden_segments([fp], golden_segments, "ja-JP")
        assert len(results) == 1
        assert results[0]["passed"] is False

    def test_empty_corpus_fails(self, tmp_path, golden_segments):
        fp = tmp_path / "translated.txt"
        fp.write_text("", encoding="utf-8")
        results = check_golden_segments([fp], golden_segments, "ja-JP")
        assert len(results) == 1
        assert results[0]["passed"] is False

    def test_no_segments_returns_empty(self, tmp_path):
        fp = tmp_path / "translated.txt"
        fp.write_text("Some text", encoding="utf-8")
        results = check_golden_segments([fp], [], "ja-JP")
        assert results == []

    def test_segment_without_locale_skipped(self, tmp_path):
        fp = tmp_path / "translated.txt"
        fp.write_text("Some text", encoding="utf-8")
        segments = [{"id": "g1", "en_US": "Test", "ko-KR": "테스트"}]
        results = check_golden_segments([fp], segments, "ja-JP")
        assert results == []


# ── Fuzzy match ───────────────────────────────────────────────────────────

class TestFuzzyMatch:
    def test_identical_strings(self):
        passed, ratio = fuzzy_match("hello world", "hello world")
        assert passed is True
        assert ratio == 1.0

    def test_empty_expected(self):
        passed, ratio = fuzzy_match("anything", "")
        assert passed is True

    def test_below_threshold(self):
        passed, ratio = fuzzy_match("completely different", "not even close at all")
        assert passed is False


# ── Threshold check ───────────────────────────────────────────────────────

class TestThresholdCheck:
    def test_all_pass(self):
        thresholds = {
            "min_glossary_coverage": 0.8,
            "min_golden_regression_pass": 0.9,
            "min_segment_count_per_locale": 1,
        }
        result = check_thresholds(0.95, 1.0, 5, thresholds)
        assert result["all_passed"] is True
        assert result["glossary_coverage"]["passed"] is True
        assert result["golden_regression_pass"]["passed"] is True
        assert result["segment_count"]["passed"] is True

    def test_glossary_below_threshold(self):
        thresholds = {
            "min_glossary_coverage": 0.8,
            "min_golden_regression_pass": 0.9,
            "min_segment_count_per_locale": 0,
        }
        result = check_thresholds(0.5, 1.0, 5, thresholds)
        assert result["all_passed"] is False
        assert result["glossary_coverage"]["passed"] is False

    def test_golden_below_threshold(self):
        thresholds = {
            "min_glossary_coverage": 0.0,
            "min_golden_regression_pass": 0.9,
            "min_segment_count_per_locale": 0,
        }
        result = check_thresholds(1.0, 0.5, 5, thresholds)
        assert result["all_passed"] is False
        assert result["golden_regression_pass"]["passed"] is False

    def test_segment_count_below_threshold(self):
        thresholds = {
            "min_glossary_coverage": 0.0,
            "min_golden_regression_pass": 1.0,
            "min_segment_count_per_locale": 10,
        }
        result = check_thresholds(1.0, 1.0, 3, thresholds)
        assert result["all_passed"] is False
        assert result["segment_count"]["passed"] is False

    def test_default_thresholds(self):
        result = check_thresholds(0.0, 1.0, 0, {})
        # defaults: min_glossary=0.0, min_golden=1.0, min_segments=0
        assert result["all_passed"] is True


# ── Discovery ─────────────────────────────────────────────────────────────

class TestDiscovery:
    def test_finds_translated_files(self, tmp_atoms):
        files = discover_translated_files(tmp_atoms, "ja-JP")
        assert len(files) == 1
        assert files[0].name == "CANONICAL.txt"
        assert "ja-JP" in str(files[0])

    def test_no_files_for_missing_locale(self, tmp_atoms):
        files = discover_translated_files(tmp_atoms, "ko-KR")
        assert files == []


# ── Empty locale (no translations) ────────────────────────────────────────

class TestEmptyLocale:
    def test_no_translations_reports_error(self, tmp_path):
        atoms_dir = tmp_path / "atoms"
        atoms_dir.mkdir()
        # Create a minimal quality contracts dir
        qc_dir = tmp_path / "config" / "localization" / "quality_contracts"
        qc_dir.mkdir(parents=True)
        (qc_dir / "glossary.yaml").write_text("schema_version: '1.0'\nterms: []", encoding="utf-8")
        (qc_dir / "golden_translation_regression.yaml").write_text(
            "schema_version: '1.0'\nsegments: []", encoding="utf-8"
        )
        (qc_dir / "release_thresholds.yaml").write_text(
            "schema_version: '1.0'\nthresholds:\n  min_glossary_coverage: 0.0\n"
            "  min_golden_regression_pass: 1.0\n  min_segment_count_per_locale: 0",
            encoding="utf-8",
        )

        report = run_validation(
            locale="ja-JP",
            atoms_dir=atoms_dir,
            repo_root=tmp_path,
        )
        assert report["file_count"] == 0
        assert "error" in report
        assert "No translated" in report["error"]

    def test_empty_locale_with_min_segment_threshold_fails(self, tmp_path):
        atoms_dir = tmp_path / "atoms"
        atoms_dir.mkdir()
        qc_dir = tmp_path / "config" / "localization" / "quality_contracts"
        qc_dir.mkdir(parents=True)
        (qc_dir / "glossary.yaml").write_text("schema_version: '1.0'\nterms: []", encoding="utf-8")
        (qc_dir / "golden_translation_regression.yaml").write_text(
            "schema_version: '1.0'\nsegments: []", encoding="utf-8"
        )
        (qc_dir / "release_thresholds.yaml").write_text(
            "schema_version: '1.0'\nthresholds:\n  min_glossary_coverage: 0.0\n"
            "  min_golden_regression_pass: 1.0\n  min_segment_count_per_locale: 5",
            encoding="utf-8",
        )

        report = run_validation(
            locale="ja-JP",
            atoms_dir=atoms_dir,
            repo_root=tmp_path,
        )
        assert report["overall_passed"] is False


# ── Integration: run_validation ───────────────────────────────────────────

class TestRunValidation:
    def test_full_run_with_translations(self, tmp_atoms, tmp_path):
        # Set up quality contracts
        qc_dir = tmp_path / "config" / "localization" / "quality_contracts"
        qc_dir.mkdir(parents=True)
        (qc_dir / "glossary.yaml").write_text("schema_version: '1.0'\nterms: []", encoding="utf-8")
        (qc_dir / "golden_translation_regression.yaml").write_text(
            "schema_version: '1.0'\nsegments: []", encoding="utf-8"
        )
        (qc_dir / "release_thresholds.yaml").write_text(
            "schema_version: '1.0'\nthresholds:\n  min_glossary_coverage: 0.0\n"
            "  min_golden_regression_pass: 1.0\n  min_segment_count_per_locale: 0",
            encoding="utf-8",
        )

        # tmp_atoms is under tmp_path/atoms, repo_root should be tmp_path
        # but tmp_atoms fixture uses its own tmp_path, so we need to copy
        report = run_validation(
            locale="ja-JP",
            atoms_dir=tmp_atoms,
            repo_root=tmp_path,
        )
        assert report["file_count"] == 1
        assert report["overall_passed"] is True
        assert "per_file" in report
