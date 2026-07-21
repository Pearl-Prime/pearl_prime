"""Tests for the music-brand diversity gate (G1-G8).

Per lane 04's TESTS/PROOFS + mutation-test requirement (Router Operating
Principles §14): every HARD_FAIL gate (G1-G5) gets both a passing fixture and a
deliberately-broken fixture that must trip the gate, proving it actually catches
violations rather than staying green under a broken input.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.qa import music_brand_diversity_lib as lib  # noqa: E402
from scripts.ci import check_music_brand_diversity as gate  # noqa: E402


# ---------------------------------------------------------------------------------
# G1 — per-slot-pool variant reuse (HARD_FAIL)
# ---------------------------------------------------------------------------------
def test_g1_limit_formula():
    assert lib.g1_variant_reuse_limit(0) == 5
    assert lib.g1_variant_reuse_limit(3) == 5
    assert lib.g1_variant_reuse_limit(25) == 5
    assert lib.g1_variant_reuse_limit(26) == 6  # ceil(26/5) == 6 > 5


def test_g1_passing_fixture_no_reuse():
    usages = ["Body one", "Body two", "Body three"]
    metric = lib.compute_variant_reuse(usages)
    assert metric["violation"] is False
    assert metric["max_reuse"] == 1


def test_g1_deliberately_duplicated_fixture_fails():
    """Mutation-test fixture: 3-atom synthetic pool where 6 usages are copy-pasted
    duplicates of the same body, i.e. an explicit copy-paste anti-pattern."""
    usages = ["Same body text."] * 6 + ["Unique body two"]
    metric = lib.compute_variant_reuse(usages)
    assert metric["violation"] is True
    assert metric["max_reuse"] == 6
    assert metric["limit"] == 5


def test_g1_normalizes_whitespace_and_case_for_reuse_detection():
    usages = ["Hello   World", "hello world", "HELLO WORLD", "HELLO WORLD", "HELLO WORLD", "HELLO WORLD"]
    metric = lib.compute_variant_reuse(usages)
    assert metric["max_reuse"] == 6
    assert metric["violation"] is True


def test_g1_empty_pool_no_violation():
    metric = lib.compute_variant_reuse([])
    assert metric["violation"] is False
    assert metric["n"] == 0


# ---------------------------------------------------------------------------------
# G2 — topic concentration <= 30% (HARD_FAIL)
# ---------------------------------------------------------------------------------
def _books(n_by_field: dict[str, list[str]]) -> list[dict]:
    """Build N book dicts from per-field value lists (all lists must be equal length)."""
    lengths = {len(v) for v in n_by_field.values()}
    assert len(lengths) == 1
    n = lengths.pop()
    return [{k: v[i] for k, v in n_by_field.items()} for i in range(n)]


def test_g2_topic_concentration_passes_when_balanced():
    books = _books({"topic": ["anxiety", "grief", "burnout", "boundaries"]})
    result = lib.g2_topic_concentration(books)
    assert result["violation"] is False
    assert result["fraction"] == pytest.approx(0.25)


def test_g2_topic_concentration_fails_when_concentrated():
    """Deliberately-broken fixture: 8/10 books share one topic (80% > 30% limit)."""
    books = _books({"topic": ["anxiety"] * 8 + ["grief", "burnout"]})
    result = lib.g2_topic_concentration(books)
    assert result["violation"] is True
    assert result["fraction"] == pytest.approx(0.8)


# ---------------------------------------------------------------------------------
# G3 — persona concentration <= 30% (HARD_FAIL)
# ---------------------------------------------------------------------------------
def test_g3_persona_concentration_passes_when_balanced():
    books = _books({"persona": ["nurses", "teachers", "managers", "founders"]})
    assert lib.g3_persona_concentration(books)["violation"] is False


def test_g3_persona_concentration_fails_when_concentrated():
    books = _books({"persona": ["nurses"] * 7 + ["teachers", "managers", "founders"]})
    result = lib.g3_persona_concentration(books)
    assert result["violation"] is True
    assert result["fraction"] == pytest.approx(0.7)


# ---------------------------------------------------------------------------------
# G4 — format concentration <= 50% (HARD_FAIL)
# ---------------------------------------------------------------------------------
def test_g4_format_concentration_passes_at_exactly_half():
    books = _books({"format": ["ebook", "ebook", "audio", "print"]})
    result = lib.g4_format_concentration(books)
    assert result["fraction"] == pytest.approx(0.5)
    assert result["violation"] is False  # <= 50% is the limit, not strictly less


def test_g4_format_concentration_fails_when_over_half():
    books = _books({"format": ["ebook"] * 6 + ["audio", "print", "audio", "print"]})
    result = lib.g4_format_concentration(books)
    assert result["violation"] is True
    assert result["fraction"] == pytest.approx(0.6)


# ---------------------------------------------------------------------------------
# G5 — locale concentration, per-platform tunable (HARD_FAIL)
# ---------------------------------------------------------------------------------
def test_g5_locale_concentration_kdp_us_passes_at_70pct():
    books = _books({"locale": ["en_US"] * 7 + ["en_GB", "en_AU", "en_CA"]})
    result = lib.g5_locale_concentration(books, platform="kdp_us")
    assert result["limit"] == pytest.approx(0.70)
    assert result["violation"] is False


def test_g5_locale_concentration_kdp_us_fails_above_70pct():
    books = _books({"locale": ["en_US"] * 8 + ["en_GB", "en_AU"]})
    result = lib.g5_locale_concentration(books, platform="kdp_us")
    assert result["violation"] is True


def test_g5_locale_concentration_kdp_jp_uses_stricter_threshold():
    books = _books({"locale": ["ja_JP"] * 6 + ["en_US"] * 4})
    result_us = lib.g5_locale_concentration(books, platform="kdp_us")
    result_jp = lib.g5_locale_concentration(books, platform="kdp_jp")
    assert result_us["limit"] == pytest.approx(0.70)
    assert result_jp["limit"] == pytest.approx(0.50)
    # Same 60% concentration: passes KDP US (<=70%) but fails KDP JP (<=50%).
    assert result_us["violation"] is False
    assert result_jp["violation"] is True


def test_g5_locale_concentration_unknown_platform_uses_default():
    result = lib.g5_locale_concentration([], platform="some_new_store")
    assert result["limit"] == pytest.approx(lib.G5_LOCALE_DEFAULT_MAX)


# ---------------------------------------------------------------------------------
# G6 — title fuzzy-similarity clustering <= ceil(N/20) (WARN)
# ---------------------------------------------------------------------------------
def test_g6_distinct_titles_no_clusters():
    titles = ["Calm Before the Storm", "Rise After Rain", "Anchor in the Dark"]
    result = lib.g6_title_clusters(titles)
    assert result["cluster_count"] == 0
    assert result["violation"] is False


def test_g6_near_duplicate_titles_cluster_and_can_violate():
    titles = ["The Anxious Mind Reset"] * 21 + [f"Distinct Title {i}" for i in range(20)]
    result = lib.g6_title_clusters(titles)
    assert result["cluster_count"] >= 1
    # n = 41, limit = ceil(41/20) = 3; one 21-member cluster alone doesn't exceed the
    # cluster-COUNT limit, so assert on the metric shape and a lower-limit scenario below.
    assert result["limit"] == 3


def test_g6_multiple_duplicate_clusters_exceed_limit():
    titles = (
        ["Title Alpha"] * 2
        + ["Title Beta"] * 2
        + ["Title Gamma"] * 2
        + ["Title Delta"] * 2
        + [f"Unique {i}" for i in range(12)]
    )
    # n = 20, limit = ceil(20/20) = 1; 4 duplicate clusters > 1 -> violation.
    result = lib.g6_title_clusters(titles)
    assert result["n"] == 20
    assert result["limit"] == 1
    assert result["cluster_count"] == 4
    assert result["violation"] is True


# ---------------------------------------------------------------------------------
# G7 — author-bio reuse <= 60% (WARN)
# ---------------------------------------------------------------------------------
def test_g7_author_bio_reuse_passes_under_60pct():
    bios = ["Bio A"] * 3 + ["Bio B"] * 2 + ["Bio C"]
    result = lib.g7_author_bio_reuse(bios)
    assert result["violation"] is False


def test_g7_author_bio_reuse_fails_over_60pct():
    bios = ["Same canned bio."] * 7 + ["Bio B", "Bio C", "Bio D"]
    result = lib.g7_author_bio_reuse(bios)
    assert result["violation"] is True
    assert result["fraction"] == pytest.approx(0.7)


# ---------------------------------------------------------------------------------
# G8 — slot-atom rotation Gini <= 0.4 (WARN)
# ---------------------------------------------------------------------------------
def test_g8_perfectly_even_rotation_gini_zero():
    result = lib.g8_rotation_gini([5, 5, 5, 5])
    assert result["gini"] == pytest.approx(0.0)
    assert result["violation"] is False


def test_g8_uneven_rotation_gini_violates():
    result = lib.g8_rotation_gini([0, 0, 0, 40])
    assert result["gini"] > lib.G8_GINI_MAX
    assert result["violation"] is True


def test_gini_coefficient_known_values():
    assert lib.gini_coefficient([1, 1, 1, 1]) == pytest.approx(0.0)
    assert lib.gini_coefficient([]) == pytest.approx(0.0)
    assert lib.gini_coefficient([0, 0, 0]) == pytest.approx(0.0)


# ---------------------------------------------------------------------------------
# CLI script: evaluate_kit() entry point + Phase-A degraded mode
# ---------------------------------------------------------------------------------
def test_evaluate_kit_is_the_probed_entry_point_name():
    assert callable(gate.evaluate_kit)


def test_evaluate_kit_phase_a_degraded_mode_with_no_catalog_books():
    payload = {
        "brand_id": "ahjan_music",
        "musician_id": "ahjan",
        "quality_profile": "production",
        "pools": {
            "LYRIC_OPENING": [
                {"atom_id": "a1", "variants": [{"body": "One"}, {"body": "Two"}, {"body": "Three"}]},
            ],
        },
        "books": [],
    }
    verdict = gate.evaluate_kit(payload)
    assert verdict["phase"] == "phase_a_degraded"
    assert verdict["gates"]["G1"]["status"] == "pass"
    for gate_id in ("G2", "G3", "G4", "G5", "G6", "G7", "G8"):
        assert verdict["gates"][gate_id]["status"] == "skipped"
    assert verdict["overall"] == "PASS"


def test_evaluate_kit_g1_hard_fail_under_production_profile():
    """Deliberately-broken fixture: a pool where 6 variant bodies are exact
    copy-paste duplicates must HARD_FAIL under --quality-profile production."""
    dup_variants = [{"body": "Copy pasted line."} for _ in range(6)]
    payload = {
        "brand_id": "ahjan_music",
        "musician_id": "ahjan",
        "quality_profile": "production",
        "pools": {"LYRIC_OPENING": [{"atom_id": "a1", "variants": dup_variants}]},
        "books": [],
    }
    verdict = gate.evaluate_kit(payload)
    assert verdict["gates"]["G1"]["status"] == "fail"
    assert "G1" in verdict["hard_failures"]
    assert verdict["overall"] == "HARD_FAIL"


def test_evaluate_kit_g1_fail_is_warn_not_hard_fail_under_draft_profile():
    """DO NOT list says G1-G5 are ratified HARD_FAIL under production; this proves
    the gate does NOT silently soften them by never failing draft either — draft
    still surfaces the violation, just non-blocking (WARN, not HARD_FAIL)."""
    dup_variants = [{"body": "Copy pasted line."} for _ in range(6)]
    payload = {
        "brand_id": "ahjan_music",
        "musician_id": "ahjan",
        "quality_profile": "draft",
        "pools": {"LYRIC_OPENING": [{"atom_id": "a1", "variants": dup_variants}]},
        "books": [],
    }
    verdict = gate.evaluate_kit(payload)
    assert verdict["gates"]["G1"]["status"] == "fail"
    assert verdict["overall"] == "WARN"


def test_evaluate_kit_full_mode_hard_fails_g2_when_topic_concentrated():
    books = [{"topic": "anxiety", "persona": "p", "format": "ebook", "locale": "en_US",
              "title": f"Title {i}", "author_bio": f"Bio {i}"} for i in range(45)]
    books += [{"topic": "grief", "persona": "p2", "format": "print", "locale": "en_GB",
               "title": f"Other {i}", "author_bio": f"Bio2 {i}"} for i in range(5)]
    payload = {
        "brand_id": "ahjan_music",
        "musician_id": "ahjan",
        "quality_profile": "production",
        "pools": {},
        "books": books,
    }
    verdict = gate.evaluate_kit(payload)
    assert verdict["phase"] == "full"
    assert verdict["gates"]["G2"]["status"] == "fail"
    assert verdict["overall"] == "HARD_FAIL"


# ---------------------------------------------------------------------------------
# CLI script: disk loaders against a synthetic bank directory
# ---------------------------------------------------------------------------------
def test_load_pool_atoms_reads_approved_and_draft_atoms(tmp_path: Path):
    bank_dir = tmp_path / "some_handle"
    approved = bank_dir / "approved_atoms" / "LYRIC_OPENING"
    draft = bank_dir / "draft_atoms" / "LYRIC_OPENING"
    approved.mkdir(parents=True)
    draft.mkdir(parents=True)
    (approved / "lo_01.yaml").write_text(
        yaml.safe_dump({"atom_id": "h_LYRIC_OPENING_01", "variants": [{"body": "Approved body"}]}),
        encoding="utf-8",
    )
    (draft / "lo_02.yaml").write_text(
        yaml.safe_dump({"atom_id": "h_LYRIC_OPENING_02", "variants": [{"body": "Draft body"}]}),
        encoding="utf-8",
    )
    atoms = gate.load_pool_atoms(bank_dir, "LYRIC_OPENING")
    ids = {a["atom_id"] for a in atoms}
    assert ids == {"h_LYRIC_OPENING_01", "h_LYRIC_OPENING_02"}


def test_resolve_musician_handle_raises_for_unknown_brand(tmp_path: Path):
    registry_path = tmp_path / "registry.yaml"
    registry_path.write_text(
        yaml.safe_dump({"music_brands": [{"brand_id": "known_music", "musician_handle": "known"}]}),
        encoding="utf-8",
    )
    with pytest.raises(gate.BrandNotFoundError):
        gate.resolve_musician_handle("unknown_music", registry_path=registry_path)
    assert gate.resolve_musician_handle("known_music", registry_path=registry_path) == "known"


# ---------------------------------------------------------------------------------
# Live-data smoke: the real ahjan_music bank on disk (Phase-A degraded mode)
# ---------------------------------------------------------------------------------
_LIVE_BANK_DIR = REPO_ROOT / "SOURCE_OF_TRUTH/musician_banks/ahjan"


@pytest.mark.skipif(not _LIVE_BANK_DIR.is_dir(), reason="ahjan musician bank not present in this checkout")
def test_live_ahjan_music_brand_passes_phase_a_gate():
    payload = gate.build_payload("ahjan_music", "production")
    assert payload["pools"], "expected at least one slot pool for ahjan_music"
    verdict = gate.evaluate_kit(payload)
    assert verdict["phase"] == "phase_a_degraded"
    assert verdict["overall"] in {"PASS", "WARN"}
    assert verdict["gates"]["G1"]["status"] in {"pass", "fail"}
