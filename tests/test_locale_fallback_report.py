"""Tests for the locale-fallback honesty gate (phoenix_v4.rendering.locale_fallback_report).

Proves the core contract:
  * a missing localized BODY-prose atom FAILS in production (report flags it and
    yields a specific blocker), and RENDERS-WITH-LABEL in draft;
  * citations / proper nouns / source titles classified as allowed-English do NOT
    trip the gate;
  * Latin-script target locales are undetectable-by-script and never fail here.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from phoenix_v4.rendering.locale_fallback_report import (
    build_locale_fallback_report,
    classify_slot,
    production_blockers,
    write_locale_fallback_report,
)


# --- Minimal EnrichedBook-like fakes (duck-typed) ---------------------------
@dataclass
class _Slot:
    slot_type: str
    content: str
    source: str = "story_plan"
    source_id: str = "src"
    atom_id: str = "atom"


@dataclass
class _Chapter:
    number: int
    slots: list = field(default_factory=list)


@dataclass
class _Book:
    chapters: list = field(default_factory=list)


# A localized (zh-TW) HOOK and an English-fallback STORY, plus a citation-only slot.
_ZH_HOOK = "野心仍在。只是它的代價比過去高昂。你很擅長你的工作，但那已經不再讓人覺得足夠。"
_EN_STORY = (
    "Alex is twenty-four and working at a tech startup as a junior developer. "
    "The job is exciting and pays better than her last one, but it takes everything."
)
_CITATION_ONLY = "[Barrett, 2017]"
_TITLE_ONLY = '“How Emotions Are Made” (Barrett, 2017)'


def _make_book() -> _Book:
    return _Book(chapters=[
        _Chapter(1, [
            _Slot("HOOK", _ZH_HOOK, source="persona_atom", source_id="HOOK v26", atom_id="HOOK v26"),
            _Slot("STORY", _EN_STORY, source="story_plan",
                  source_id="story_plan:twelve_shape:ch1:story_1:recognition:overwhelm:v03"),
            _Slot("REFLECTION", _CITATION_ONLY, source="composite_doctrine", source_id="COMPOSITE_DOCTRINE v03"),
        ]),
    ])


def test_missing_localized_body_prose_fails_in_production():
    book = _make_book()
    report = build_locale_fallback_report(book, "zh-TW", "production")
    assert report["applicable"] is True
    assert report["production_would_fail"] is True
    fb = report["english_fallbacks"]
    # Exactly the English STORY is flagged; the zh HOOK and the citation are not.
    assert len(fb) == 1
    assert fb[0]["slot_type"] == "STORY"
    assert fb[0]["chapter"] == 1
    blockers = production_blockers(report)
    assert len(blockers) == 1
    # Blocker names the atom, the slot and the chapter specifically.
    assert "ch1" in blockers[0] and "STORY" in blockers[0]
    assert "story_plan:twelve_shape:ch1:story_1:recognition:overwhelm:v03" in blockers[0]


def test_same_book_renders_with_label_in_draft():
    book = _make_book()
    report = build_locale_fallback_report(book, "zh-TW", "draft")
    # Draft still detects + labels the fallback, but does NOT demand a failure.
    assert report["applicable"] is True
    assert report["production_would_fail"] is False
    assert len(report["english_fallbacks"]) == 1
    assert report["english_fallbacks"][0]["slot_type"] == "STORY"


def test_localized_slot_not_flagged():
    c = classify_slot("HOOK", _ZH_HOOK, "zh-TW")
    assert c["classification"] == "localized"


def test_citation_only_is_allowed_english():
    c = classify_slot("REFLECTION", _CITATION_ONLY, "zh-TW")
    assert c["classification"] == "allowed_english"


def test_quoted_title_is_allowed_english():
    # Latin letters live in the proper-noun/title tokens; residue is below the floor.
    c = classify_slot("REFLECTION", _TITLE_ONLY, "zh-TW")
    assert c["classification"] == "allowed_english"


def test_english_body_prose_is_fallback():
    c = classify_slot("STORY", _EN_STORY, "zh-TW")
    assert c["classification"] == "english_fallback"


def test_embedded_citation_in_localized_prose_stays_localized():
    mixed = _ZH_HOOK + " (Barrett, 2017) " + _ZH_HOOK
    c = classify_slot("REFLECTION", mixed, "zh-TW")
    assert c["classification"] == "localized"


def test_latin_script_locale_is_undetectable_and_never_fails():
    book = _make_book()  # contains English STORY
    report = build_locale_fallback_report(book, "de-DE", "production")
    assert report["applicable"] is False
    assert report["production_would_fail"] is False
    assert report["english_fallbacks"] == []
    # Body-prose slots are classified undetectable, not fallback.
    c = classify_slot("STORY", _EN_STORY, "de-DE")
    assert c["classification"] == "undetectable_by_script"


def test_en_us_and_non_body_slots_not_flagged():
    assert classify_slot("STORY", _EN_STORY, "en-US")["classification"] == "undetectable_by_script"
    assert classify_slot("ANGLE_METADATA", _EN_STORY, "zh-TW")["classification"] == "not_body_prose"


def test_write_report_creates_artifact(tmp_path: Path):
    book = _make_book()
    report, path = write_locale_fallback_report(book, "zh-TW", "production", tmp_path)
    assert path.exists()
    on_disk = json.loads(path.read_text(encoding="utf-8"))
    assert on_disk["stage"] == "locale_fallback_report"
    assert on_disk["locale"] == "zh-TW"
    assert on_disk["production_would_fail"] is True
    assert on_disk["summary"]["english_fallback"] == 1
    assert on_disk["summary"]["localized"] == 1
    assert on_disk["summary"]["allowed_english"] == 1
