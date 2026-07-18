"""
Tests for INV-3: Language = teacher's assigned language.

Covers:
1. TEACHER_LANGUAGE map in run_daily_news_cycle.py matches teacher_language_map.yaml.
2. detect_pearl_news_language_mismatch() catches articles with wrong language.
3. Detector passes articles with correct language.
4. Group-voice articles (no teacher_id) are skipped by the language detector.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.quality.regression_museum.pearl_news_detectors import (
    TEACHER_LANGUAGE as DETECTOR_TEACHER_LANGUAGE,
    detect_pearl_news_language_mismatch,
)


def _import_cycle_module():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "run_daily_news_cycle",
        REPO_ROOT / "scripts" / "pearl_news" / "run_daily_news_cycle.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _write_article(tmp_path: Path, slug: str, teacher_id: str | None, language: str) -> Path:
    data = {
        "title": "Test Article",
        "content": (
            '<div class="pn-byline">By Teacher | Tradition | EN</div>'
            '<p>Body</p>'
            '<aside class="pn-sidebar"><section class="pn-sidebar-teacher"><h3>Teacher</h3></section></aside>'
        ),
        "teacher_id": teacher_id,
        "teacher_used": {"teacher_id": teacher_id, "display_name": "Teacher"},
        "sidebar": {"teacher_name": "Teacher"},
        "language": language,
        "topic": "climate",
        "article_type": "hard_news_spiritual_response",
    }
    path = tmp_path / f"article_{slug}.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


class TestTeacherLanguageMap:
    def setup_method(self):
        self.mod = _import_cycle_module()

    def test_cycle_module_language_map_matches_detector_map(self):
        cycle_map = self.mod.TEACHER_LANGUAGE
        for teacher_id, lang in DETECTOR_TEACHER_LANGUAGE.items():
            assert teacher_id in cycle_map, (
                f"Teacher '{teacher_id}' in detector map but missing from cycle module map"
            )
            assert cycle_map[teacher_id] == lang, (
                f"Language mismatch for '{teacher_id}': "
                f"cycle={cycle_map[teacher_id]!r}, detector={lang!r}"
            )

    def test_english_teachers_map_to_en(self):
        # 'ra' and 'pamela_fellows' removed per PR #1132 (Pearl_Prime-only).
        # 'master_sha' added to align with the cycle module's en-roster.
        english_teachers = ["ahjan", "sai_ma", "maat", "master_sha"]
        for t in english_teachers:
            assert DETECTOR_TEACHER_LANGUAGE[t] == "en", f"{t} should be 'en'"

    def test_japanese_teachers_map_to_ja(self):
        # 'omote' added to align with the cycle module's ja-roster.
        ja_teachers = ["junko", "miki", "joshin", "omote"]
        for t in ja_teachers:
            assert DETECTOR_TEACHER_LANGUAGE[t] == "ja", f"{t} should be 'ja'"

    def test_chinese_teachers_map_to_zh_cn(self):
        zh_teachers = ["master_feung", "master_wu"]
        for t in zh_teachers:
            assert DETECTOR_TEACHER_LANGUAGE[t] == "zh-cn", f"{t} should be 'zh-cn'"

    def test_yaml_config_exists_and_is_loadable(self):
        try:
            import yaml
        except ImportError:
            pytest.skip("pyyaml not installed")
        config_path = REPO_ROOT / "pearl_news" / "config" / "teacher_language_map.yaml"
        assert config_path.exists(), f"teacher_language_map.yaml not found at {config_path}"
        with open(config_path, encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
        teacher_langs = cfg.get("teacher_languages") or {}
        for teacher_id, lang in DETECTOR_TEACHER_LANGUAGE.items():
            if teacher_id in teacher_langs:
                assert teacher_langs[teacher_id] == lang, (
                    f"YAML teacher_language_map has '{teacher_langs[teacher_id]}' for '{teacher_id}' "
                    f"but detector map has '{lang}'"
                )


class TestLanguageMismatchDetector:
    def test_correct_language_passes(self, tmp_path):
        _write_article(tmp_path, "aaa", "ahjan", "en")
        violations = detect_pearl_news_language_mismatch(tmp_path)
        assert violations == []

    def test_wrong_language_for_english_teacher_fails(self, tmp_path):
        _write_article(tmp_path, "aaa", "ahjan", "zh-cn")
        violations = detect_pearl_news_language_mismatch(tmp_path)
        assert len(violations) == 1
        assert violations[0].failure_class == "pearl_news_language_mismatch"
        assert violations[0].severity == "block"
        assert "ahjan" in violations[0].evidence
        assert "zh-cn" in violations[0].evidence

    def test_wrong_language_for_cjk_teacher_fails(self, tmp_path):
        _write_article(tmp_path, "aaa", "master_wu", "en")
        violations = detect_pearl_news_language_mismatch(tmp_path)
        assert len(violations) == 1
        assert "master_wu" in violations[0].evidence

    def test_correct_ja_language_passes(self, tmp_path):
        _write_article(tmp_path, "aaa", "junko", "ja")
        violations = detect_pearl_news_language_mismatch(tmp_path)
        assert violations == []

    def test_group_voice_no_teacher_is_skipped(self, tmp_path):
        _write_article(tmp_path, "aaa", None, "en")
        violations = detect_pearl_news_language_mismatch(tmp_path)
        assert violations == [], "Articles with no teacher_id are skipped by language check"

    def test_unknown_teacher_id_is_skipped(self, tmp_path):
        _write_article(tmp_path, "aaa", "unknown_teacher_xyz", "en")
        violations = detect_pearl_news_language_mismatch(tmp_path)
        assert violations == [], "Unknown teacher IDs cannot be validated and are skipped"
