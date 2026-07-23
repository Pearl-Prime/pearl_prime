"""Tests for scripts/publish/analyze_storyblocks_reuse.py (Lane 02: cover-acquisition-queue).

These tests guard the three things that matter for this lane:
1. A genuine reuse candidate (grief / stock_id 350614976, a still image whose
   title contains the positive cue "candle") is actually surfaced from the
   real, committed social-bank metadata.
2. The script never promotes a social_broll-surface record to surface: cover
   and never sets topic_verified: true — it can only recommend, never write.
3. All 17 canonical topics from the topic map appear in the output; none are
   silently dropped, whether or not they have a plausible candidate.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
import yaml

from scripts.publish.analyze_storyblocks_reuse import (
    DEFAULT_SOCIAL_BANK_INDEX,
    DEFAULT_TOPIC_MAP,
    NEW_SEARCH_ONLY_TOPICS,
    REUSE_NOMINATED_TOPICS,
    analyze,
    build_queue_rows,
    load_social_bank_assets,
    load_topic_map,
    score_social_bank_candidate,
    write_queue_tsv,
)


def _canonical_topics() -> set[str]:
    return set(load_topic_map(DEFAULT_TOPIC_MAP)["topics"].keys())


def test_real_social_bank_and_topic_map_are_present():
    # Sanity: this lane's whole analysis depends on these two committed files
    # actually existing and being non-trivial. If either goes missing the
    # rest of these tests would pass vacuously, which would be worse than a
    # loud failure here.
    assert DEFAULT_TOPIC_MAP.is_file()
    assert DEFAULT_SOCIAL_BANK_INDEX.is_file()
    assert len(_canonical_topics()) == 17


def test_grief_reuse_candidate_identified_from_real_social_bank_metadata():
    """A genuine reuse candidate is correctly identified from existing
    social-bank metadata: grief/350614976 is a still image whose title
    ("...small candle burning...") contains the topic's positive cue
    "candle" and no excluded cue, so it must be flagged plausible."""
    result = analyze()
    grief = result["topics"]["grief"]
    assert grief["action"] == "reuse_confirm"
    plausible_ids = {c["stock_id"] for c in grief["social_bank_candidates_plausible"]}
    assert "350614976" in plausible_ids


def test_video_hit_is_never_counted_as_a_cover_candidate():
    """grief/353483009 is a video whose title also contains "candle" — a
    plausible topical hit by text alone — but book covers require a still
    image, so it must never appear as a countable candidate."""
    result = analyze()
    grief = result["topics"]["grief"]
    plausible_ids = {c["stock_id"] for c in grief["social_bank_candidates_plausible"]}
    assert "353483009" not in plausible_ids
    all_ids = {c["stock_id"]: c for c in grief["social_bank_candidates_all"]}
    assert all_ids["353483009"]["plausible"] is False
    assert all_ids["353483009"]["media_type_ok"] is False


def test_tag_only_match_without_descriptive_cue_is_not_plausible():
    """A record merely tagged with a topic (asset["topic"] == topic) but with
    no genuine descriptive (title) evidence must not be promoted to
    plausible — mirrors bank_image_picker.validate_candidate()'s exclusion of
    metadata.keywords/topic_keys from the positive-cue haystack."""
    topic_map = load_topic_map(DEFAULT_TOPIC_MAP)
    asset = {
        "topic": "anxiety",
        "media_type": "image",
        "stock_id": "999999999",
        "title": "A completely unrelated photo of a bicycle",
    }
    scored = score_social_bank_candidate(asset, "anxiety", topic_map)
    assert scored["plausible"] is False
    assert "descriptive metadata (title) has no topic-positive cue" in scored["reasons"]


def test_excluded_cue_disqualifies_even_with_positive_cue_present():
    topic_map = load_topic_map(DEFAULT_TOPIC_MAP)
    asset = {
        "topic": "anxiety",
        "media_type": "image",
        "stock_id": "999999998",
        "title": "A calm scene interrupted by sudden horror",
    }
    scored = score_social_bank_candidate(asset, "anxiety", topic_map)
    assert scored["plausible"] is False
    assert scored["excluded_hits"] == ["horror"]


def test_social_broll_record_is_never_auto_promoted_to_cover_surface():
    """The core guardrail of this lane: scoring a social-bank record can only
    ever produce a recommendation, never a write. Every scored candidate must
    still self-report as unverified social_broll, and running the full
    analysis + queue-row build must not mutate the source bank file at all."""
    before = DEFAULT_SOCIAL_BANK_INDEX.read_bytes()
    before_hash = hashlib.sha256(before).hexdigest()

    result = analyze()
    rows = build_queue_rows(result)

    after_hash = hashlib.sha256(DEFAULT_SOCIAL_BANK_INDEX.read_bytes()).hexdigest()
    assert before_hash == after_hash, "analyze()/build_queue_rows() must never touch the source bank file"

    for topic_info in result["topics"].values():
        for candidate in topic_info["social_bank_candidates_all"]:
            assert candidate["surface_today"] == "social_broll"
            assert candidate["topic_verified_today"] is False

    # No queue row is ever allowed to assert a promotion already happened;
    # every row must still name credentials + human review as the blocker,
    # and reuse rows must say "re-download ... after human review", never
    # "relabel" (which would imply mutating the existing record in place).
    for row in rows:
        assert row["blocked_on"] == "live Storyblocks API credentials + human topic-verification"
        if row["action"] == "reuse_confirm":
            assert "re-download" in row["required_next_step"]
            assert "after human review" in row["required_next_step"]
            assert "relabel" not in row["required_next_step"]


def test_all_17_canonical_topics_present_no_topic_dropped():
    result = analyze()
    canonical = _canonical_topics()
    assert set(result["topics"].keys()) == canonical
    assert len(canonical) == 17

    rows = build_queue_rows(result)
    row_topics = {row["topic_key"] for row in rows}
    assert row_topics == canonical
    assert len(rows) == 17

    # Every row has a well-formed action and never fabricates a candidate for
    # a new_search row.
    for row in rows:
        assert row["action"] in ("reuse_confirm", "new_search")
        if row["action"] == "new_search":
            assert row["candidate_stock_ids"] == ""


def test_new_search_only_topics_have_zero_social_bank_candidates():
    result = analyze()
    for topic in NEW_SEARCH_ONLY_TOPICS:
        info = result["topics"][topic]
        assert info["social_bank_candidates_total"] == 0
        assert info["action"] == "new_search"


def test_reuse_nominated_topics_are_a_subset_of_canonical_topics():
    assert set(REUSE_NOMINATED_TOPICS) <= _canonical_topics()
    assert set(NEW_SEARCH_ONLY_TOPICS) <= _canonical_topics()
    assert set(REUSE_NOMINATED_TOPICS) | set(NEW_SEARCH_ONLY_TOPICS) == _canonical_topics()


def test_nominated_reuse_topic_can_still_resolve_to_new_search_honestly():
    """Nomination is not the same as a confirmed candidate. Several of the
    six nominated topics (anxiety, boundaries, burnout, depression,
    overthinking) have social-bank rows tagged with the topic, but none of
    those rows carry a genuine descriptive cue on a still image — so this
    lane must honestly report new_search for them rather than assuming the
    nomination was correct."""
    result = analyze()
    honestly_new_search = [
        t
        for t in REUSE_NOMINATED_TOPICS
        if result["topics"][t]["action"] == "new_search"
    ]
    # At least one nominated topic must have been downgraded by real data,
    # proving this is a live computation and not a hardcoded pass-through.
    assert honestly_new_search, "expected at least one nominated topic to honestly resolve to new_search"


def test_write_queue_tsv_round_trips(tmp_path):
    result = analyze()
    rows = build_queue_rows(result)
    out = write_queue_tsv(rows, tmp_path / "queue.tsv")
    text = out.read_text(encoding="utf-8")
    lines = text.strip("\n").split("\n")
    assert lines[0].split("\t") == [
        "topic_key",
        "action",
        "candidate_stock_ids",
        "source_bank_ref",
        "required_next_step",
        "blocked_on",
    ]
    assert len(lines) == 18  # header + 17 topics


def test_load_social_bank_assets_missing_path_returns_empty(tmp_path):
    assert load_social_bank_assets(tmp_path / "does_not_exist.json") == []
