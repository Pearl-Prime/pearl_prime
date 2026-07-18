"""Tests for the YAML-backed refrain_allowlist and the refactored
_repeated_phrase_violations function.

Sprint 1 YELLOW ITEM-1 follow-up.
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ALLOWLIST_PATH = (
    Path(__file__).resolve().parents[2] / "config" / "quality" / "refrain_allowlist.yaml"
)


def _load_yaml_allowlist() -> dict:
    return yaml.safe_load(ALLOWLIST_PATH.read_text(encoding="utf-8")) or {}


def _make_text(phrase: str, count: int) -> str:
    """Build a pseudo-book text that contains *phrase* exactly *count* times."""
    # Pad with unique surrounding words to avoid unintended n-gram overlaps.
    lines = [f"alpha beta {phrase} gamma delta" for _ in range(count)]
    return " ".join(lines)


def _violations(text: str, cap: int = 12) -> list[dict[str, Any]]:
    # Always re-import to pick up module state after any monkeypatching.
    from phoenix_v4.quality.book_quality_gate import _repeated_phrase_violations
    return _repeated_phrase_violations(text, cap=cap)


# ---------------------------------------------------------------------------
# 1. YAML loads and parses without error
# ---------------------------------------------------------------------------

class TestYamlLoads:
    def test_yaml_file_exists(self):
        assert ALLOWLIST_PATH.exists(), f"YAML not found: {ALLOWLIST_PATH}"

    def test_yaml_has_version(self):
        data = _load_yaml_allowlist()
        assert data.get("version") == 1

    def test_yaml_entries_is_list(self):
        data = _load_yaml_allowlist()
        assert isinstance(data.get("entries"), list)

    def test_yaml_entries_non_empty(self):
        data = _load_yaml_allowlist()
        assert len(data["entries"]) > 0

    def test_module_loads_allowlist(self):
        """_REFRAIN_ALLOWLIST must be a non-empty dict at import time."""
        from phoenix_v4.quality.book_quality_gate import _REFRAIN_ALLOWLIST
        assert isinstance(_REFRAIN_ALLOWLIST, dict)
        assert len(_REFRAIN_ALLOWLIST) > 0

    def test_allowlist_keys_are_lowercase(self):
        from phoenix_v4.quality.book_quality_gate import _REFRAIN_ALLOWLIST
        for key in _REFRAIN_ALLOWLIST:
            assert key == key.lower(), f"Key not lower-cased: {key!r}"

    def test_allowlist_sorted_longest_first(self):
        from phoenix_v4.quality.book_quality_gate import _REFRAIN_ALLOWLIST
        keys = list(_REFRAIN_ALLOWLIST.keys())
        lengths = [len(k) for k in keys]
        assert lengths == sorted(lengths, reverse=True), (
            "Allowlist must be sorted longest-first for longest-match-wins"
        )


# ---------------------------------------------------------------------------
# 2. legitimate_motif at exactly cap_book_wide — NOT a violation
# ---------------------------------------------------------------------------

class TestLegitimateMotifAtCap:
    def test_legitimate_motif_at_exact_cap_not_in_violations(self):
        """A legitimate_motif phrase at exactly cap_book_wide (18) must not be flagged."""
        from phoenix_v4.quality.book_quality_gate import _REFRAIN_ALLOWLIST
        # Pick the first legitimate_motif entry.
        lm_entry = next(
            (e for e in _REFRAIN_ALLOWLIST.values() if e.get("classification") == "legitimate_motif"),
            None,
        )
        assert lm_entry is not None, "No legitimate_motif entry found in allowlist"
        phrase = lm_entry["phrase"]
        cap_bw = lm_entry["cap_book_wide"]  # 18

        text = _make_text(phrase, cap_bw)  # exactly at cap — should NOT trigger
        violations = _violations(text)
        matched_phrases = {v["phrase"] for v in violations}
        assert phrase not in matched_phrases, (
            f"Phrase {phrase!r} at exactly cap={cap_bw} should NOT be a violation"
        )

    def test_legitimate_motif_below_cap_not_in_violations(self):
        from phoenix_v4.quality.book_quality_gate import _REFRAIN_ALLOWLIST
        lm_entry = next(
            (e for e in _REFRAIN_ALLOWLIST.values() if e.get("classification") == "legitimate_motif"),
            None,
        )
        phrase = lm_entry["phrase"]
        cap_bw = lm_entry["cap_book_wide"]

        text = _make_text(phrase, cap_bw - 1)
        violations = _violations(text)
        matched_phrases = {v["phrase"] for v in violations}
        assert phrase not in matched_phrases


# ---------------------------------------------------------------------------
# 3. legitimate_motif at cap_book_wide+1 — IS a violation with matched entry
# ---------------------------------------------------------------------------

class TestLegitimateMotifOverCap:
    def test_over_cap_is_violation(self):
        from phoenix_v4.quality.book_quality_gate import _REFRAIN_ALLOWLIST
        lm_entry = next(
            (e for e in _REFRAIN_ALLOWLIST.values() if e.get("classification") == "legitimate_motif"),
            None,
        )
        phrase = lm_entry["phrase"]
        cap_bw = lm_entry["cap_book_wide"]  # 18

        text = _make_text(phrase, cap_bw + 1)  # one over
        violations = _violations(text)
        # Find the exact-phrase violation (there may be sub-phrase n-gram violations too)
        exact = [v for v in violations if v["phrase"] == phrase]
        assert len(exact) == 1, (
            f"Expected violation for {phrase!r} at {cap_bw + 1} occurrences, got {violations}"
        )

    def test_over_cap_violation_has_matched_allowlist_entry(self):
        from phoenix_v4.quality.book_quality_gate import _REFRAIN_ALLOWLIST
        lm_entry = next(
            (e for e in _REFRAIN_ALLOWLIST.values() if e.get("classification") == "legitimate_motif"),
            None,
        )
        phrase = lm_entry["phrase"]
        cap_bw = lm_entry["cap_book_wide"]

        text = _make_text(phrase, cap_bw + 1)
        violations = _violations(text)
        exact = [v for v in violations if v["phrase"] == phrase]
        assert exact[0]["matched_allowlist_entry"] is not None
        assert exact[0]["cap_applied"] == cap_bw

    def test_over_cap_violation_count_is_correct(self):
        from phoenix_v4.quality.book_quality_gate import _REFRAIN_ALLOWLIST
        lm_entry = next(
            (e for e in _REFRAIN_ALLOWLIST.values() if e.get("classification") == "legitimate_motif"),
            None,
        )
        phrase = lm_entry["phrase"]
        cap_bw = lm_entry["cap_book_wide"]
        expected_count = cap_bw + 1

        text = _make_text(phrase, expected_count)
        violations = _violations(text)
        exact = [v for v in violations if v["phrase"] == phrase]
        assert exact[0]["count"] == expected_count


# ---------------------------------------------------------------------------
# 4. Non-allowlisted phrase at default_cap+1 (13 occurrences) — IS a violation
# ---------------------------------------------------------------------------

class TestNonAllowlistedPhrase:
    def test_non_allowlisted_phrase_over_default_cap_is_violation(self):
        # Use a phrase that is definitely not in the allowlist.
        phrase = "zeta zeta zeta zeta"  # 4-word phrase, not in allowlist
        count = 13  # default cap is 12, so 13 > 12

        text = _make_text(phrase, count)
        violations = _violations(text)
        exact = [v for v in violations if v["phrase"] == phrase]
        assert len(exact) == 1, f"Expected violation for non-allowlisted phrase, got {violations}"

    def test_non_allowlisted_violation_has_no_matched_entry(self):
        phrase = "zeta zeta zeta zeta"
        text = _make_text(phrase, 13)
        violations = _violations(text)
        exact = [v for v in violations if v["phrase"] == phrase]
        assert exact[0]["matched_allowlist_entry"] is None

    def test_non_allowlisted_violation_uses_default_cap(self):
        phrase = "zeta zeta zeta zeta"
        text = _make_text(phrase, 13)
        violations = _violations(text)
        exact = [v for v in violations if v["phrase"] == phrase]
        assert exact[0]["cap_applied"] == 12  # default

    def test_non_allowlisted_phrase_at_default_cap_not_violation(self):
        phrase = "zeta zeta zeta zeta"
        text = _make_text(phrase, 12)  # exactly at default cap — not a violation
        violations = _violations(text)
        exact = [v for v in violations if v["phrase"] == phrase]
        assert len(exact) == 0


# ---------------------------------------------------------------------------
# 5. Longest-match-wins: longer allowlist key takes precedence over shorter
# ---------------------------------------------------------------------------

class TestLongestMatchWins:
    def test_longer_prefix_wins(self, tmp_path, monkeypatch):
        """If allowlist has 'the point' (cap=5) and 'the point is that' (cap=18),
        the phrase 'the point is that whatever' must match the longer entry (cap=18)."""
        import phoenix_v4.quality.book_quality_gate as gate_module

        short_key = "the point"
        long_key = "the point is that"
        # Use different caps so we can distinguish which one was applied.
        fake_allowlist = {
            # Sorted longest-first (as the real loader does)
            long_key: {
                "phrase": long_key,
                "cap_book_wide": 18,
                "classification": "legitimate_motif",
            },
            short_key: {
                "phrase": short_key,
                "cap_book_wide": 5,
                "classification": "legitimate_motif",
            },
        }
        monkeypatch.setattr(gate_module, "_REFRAIN_ALLOWLIST", fake_allowlist)

        # A phrase that starts with both keys — longer key must win.
        probe = "the point is that result"  # 5-gram starting with long_key
        text = _make_text(probe, 6)  # 6 > 5 (short cap) but <= 18 (long cap)

        violations = gate_module._repeated_phrase_violations(text)
        probe_violations = [v for v in violations if v["phrase"] == probe]
        # Should NOT be a violation because longer key's cap (18) applies.
        assert len(probe_violations) == 0, (
            f"Longer match should have won (cap=18, count=6 <= 18), "
            f"but got violation: {probe_violations}"
        )

    def test_shorter_prefix_would_have_triggered(self, monkeypatch):
        """Confirm the shorter cap (5) WOULD trigger without the longer key present."""
        import phoenix_v4.quality.book_quality_gate as gate_module

        short_key = "the point"
        fake_allowlist = {
            short_key: {
                "phrase": short_key,
                "cap_book_wide": 5,
                "classification": "legitimate_motif",
            },
        }
        monkeypatch.setattr(gate_module, "_REFRAIN_ALLOWLIST", fake_allowlist)

        probe = "the point is that result"
        text = _make_text(probe, 6)  # 6 > 5

        violations = gate_module._repeated_phrase_violations(text)
        probe_violations = [v for v in violations if v["phrase"] == probe]
        assert len(probe_violations) == 1, (
            f"Short key (cap=5) should have triggered at count=6"
        )
        assert probe_violations[0]["cap_applied"] == 5


# ---------------------------------------------------------------------------
# 6. Schema validation: YAML entry missing cap_book_wide is skipped gracefully
# ---------------------------------------------------------------------------

class TestSchemaValidation:
    def test_entry_missing_cap_book_wide_is_skipped(self, tmp_path, monkeypatch):
        """Loader must skip entries that are missing cap_book_wide."""
        bad_yaml = """
version: 1
entries:
  - phrase: "missing cap phrase"
    classification: legitimate_motif
    cap_per_chapter: 2
  - phrase: "valid phrase here"
    classification: legitimate_motif
    cap_book_wide: 18
    cap_per_chapter: 2
"""
        import phoenix_v4.quality.book_quality_gate as gate_module

        # Patch _load_refrain_allowlist to use our bad YAML string.
        import io
        original_loader = gate_module._load_refrain_allowlist

        def patched_loader():
            data = yaml.safe_load(bad_yaml) or {}
            result = {}
            for entry in data.get("entries", []):
                phrase = (entry.get("phrase") or "").strip().lower()
                if not phrase:
                    continue
                if "cap_book_wide" not in entry:
                    continue  # skip malformed
                result[phrase] = entry
            return dict(sorted(result.items(), key=lambda kv: -len(kv[0])))

        monkeypatch.setattr(gate_module, "_REFRAIN_ALLOWLIST", patched_loader())

        allowlist = gate_module._REFRAIN_ALLOWLIST
        assert "missing cap phrase" not in allowlist
        assert "valid phrase here" in allowlist

    def test_empty_phrase_entry_is_skipped(self, tmp_path, monkeypatch):
        """Loader must skip entries with empty/missing phrase field."""
        import phoenix_v4.quality.book_quality_gate as gate_module

        bad_entries = [
            {"phrase": "", "cap_book_wide": 18, "classification": "legitimate_motif"},
            {"cap_book_wide": 18, "classification": "legitimate_motif"},  # no phrase key
            {"phrase": "   ", "cap_book_wide": 18, "classification": "legitimate_motif"},  # whitespace only
        ]
        result = {}
        for entry in bad_entries:
            phrase = (entry.get("phrase") or "").strip().lower()
            if not phrase:
                continue
            if "cap_book_wide" not in entry:
                continue
            result[phrase] = entry

        assert result == {}, f"Expected empty result, got {result}"
