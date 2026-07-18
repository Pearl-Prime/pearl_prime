"""Tests for config/manga/genre_prompt_cookbook_v2.yaml.

The cookbook is structured DATA, so the tests pin its shape and enforce
the FLUX negation rule from PR #802 section 8: the positive token blocks
must NOT contain ``no X`` / ``without X`` patterns. Negations live in the
``universal_negative`` slot only.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
COOKBOOK_PATH = REPO_ROOT / "config" / "manga" / "genre_prompt_cookbook_v2.yaml"

EXPECTED_GENRES = {
    "anxiety",
    "sleep_anxiety",
    "grief",
    "boundaries",
    "self_worth",
    "overthinking",
    "imposter_syndrome",
    "burnout",
    "courage",
}

REQUIRED_KEYS = {
    "archetype",
    "palette",
    "composition",
    "subject_prompt",
    "style_modifiers",
    "lock_in_tokens",
    "revisit_after_r1",
}

# Forbidden patterns inside positive prompt token blocks (subject_prompt,
# style_modifiers). Per PR #802 section 8, FLUX embeds "no text" close to
# "text", so any "no X" / "without X" in the positive is actively harmful.
NEGATION_PATTERNS = [
    re.compile(r"\bno\s+\w", re.IGNORECASE),       # "no text", "no letters"
    re.compile(r"\bwithout\s+\w", re.IGNORECASE),  # "without text"
    re.compile(r"\bno-\w", re.IGNORECASE),         # "no-text"
    re.compile(r"<no\b", re.IGNORECASE),           # "<no something>"
]


@pytest.fixture(scope="module")
def cookbook() -> dict:
    with COOKBOOK_PATH.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def test_yaml_parses(cookbook):
    assert isinstance(cookbook, dict)


def test_schema_version_is_2(cookbook):
    assert cookbook.get("schema_version") >= 2


def test_all_expected_genres_present(cookbook):
    genres = cookbook.get("genres") or {}
    actual = set(genres.keys())
    missing = EXPECTED_GENRES - actual
    assert not missing, f"missing genres: {sorted(missing)}"


def test_every_genre_has_required_keys(cookbook):
    genres = cookbook.get("genres") or {}
    for genre_name, block in genres.items():
        actual_keys = set(block.keys())
        missing = REQUIRED_KEYS - actual_keys
        assert not missing, (
            f"genre {genre_name!r} missing required keys: {sorted(missing)}"
        )
        # lock_in_tokens must be a 2-3 element list
        lock_in = block["lock_in_tokens"]
        assert isinstance(lock_in, list), (
            f"{genre_name}.lock_in_tokens must be a list, got {type(lock_in)!r}"
        )
        assert 2 <= len(lock_in) <= 3, (
            f"{genre_name}.lock_in_tokens must have 2-3 entries, got {len(lock_in)}"
        )


def test_no_negations_in_positive_prompt_blocks(cookbook):
    """Per PR #802 section 8 — no 'no X' / 'without X' in positive prompts."""
    genres = cookbook.get("genres") or {}
    offenses: list[str] = []
    for genre_name, block in genres.items():
        for field in ("subject_prompt", "style_modifiers"):
            text = block.get(field) or ""
            for pat in NEGATION_PATTERNS:
                match = pat.search(text)
                if match:
                    offenses.append(
                        f"{genre_name}.{field}: matched {pat.pattern!r} "
                        f"at {match.group(0)!r}"
                    )
    assert not offenses, (
        "negation tokens found in positive prompt blocks "
        "(violates PR #802 section 8 rule):\n  " + "\n  ".join(offenses)
    )


def test_universal_negative_nonempty_and_contains_core_tokens(cookbook):
    universal_negative = (cookbook.get("universal_negative") or "").lower()
    assert universal_negative.strip(), "universal_negative must be non-empty"
    for required in ("text", "watermark", "blurry"):
        assert required in universal_negative, (
            f"universal_negative must contain {required!r}"
        )


def test_universal_register_nonempty(cookbook):
    register = (cookbook.get("universal_register") or "").strip()
    assert register, "universal_register must be non-empty"
    # Must contain portrait + KDP cues — these are what makes it 'universal'
    assert "portrait" in register.lower()
    assert "1600x2560" in register or "1600 x 2560" in register


def test_book_genre_map_covers_inventory(cookbook):
    """All 13 books from the cover regen plan must map to a known genre."""
    expected_books = {
        "ahjan_anxiety",
        "joshin_anxiety",
        "pamela_fellows_anxiety",
        "omote_sleep_anxiety",
        "master_sha_grief",
        "sai_ma_grief",
        "maat_boundaries",
        "adi_da_self_worth",
        "miyuki_overthinking",  # per OPD-111 — was junko_overthinking
        "miki_imposter_syndrome",
        "ra_imposter_syndrome",
        "master_feung_burnout",
        "master_wu_courage",
    }
    book_map = cookbook.get("book_genre_map") or {}
    actual = set(book_map.keys())
    missing = expected_books - actual
    assert not missing, f"book_genre_map missing books: {sorted(missing)}"
    # Every mapped genre must exist in genres
    genres = set((cookbook.get("genres") or {}).keys())
    for book, genre in book_map.items():
        assert genre in genres, (
            f"book {book!r} maps to unknown genre {genre!r}"
        )


def test_compose_positive_has_no_negations():
    """End-to-end: composed positive prompt for every book must be clean."""
    import sys

    sys.path.insert(0, str(REPO_ROOT / "scripts" / "manga"))
    from cookbook_v2_compose_prompt import compose_positive, load_cookbook

    cookbook = load_cookbook()
    book_map = cookbook.get("book_genre_map") or {}
    offenses: list[str] = []
    for book in book_map:
        composed = compose_positive(book)
        for pat in NEGATION_PATTERNS:
            match = pat.search(composed)
            if match:
                offenses.append(
                    f"book {book}: composed prompt matched "
                    f"{pat.pattern!r} at {match.group(0)!r}"
                )
    assert not offenses, "composed positive prompts contain negations:\n  " + "\n  ".join(
        offenses
    )


def test_compose_helper_runs_for_all_books():
    import sys

    sys.path.insert(0, str(REPO_ROOT / "scripts" / "manga"))
    from cookbook_v2_compose_prompt import (
        compose_negative,
        compose_positive,
        load_cookbook,
    )

    cookbook = load_cookbook()
    book_map = cookbook.get("book_genre_map") or {}
    assert book_map, "book_genre_map must not be empty"
    for book in book_map:
        positive = compose_positive(book)
        assert positive, f"empty positive prompt for {book!r}"
        # Sanity: composed prompt should be reasonably long
        assert len(positive) > 80, (
            f"composed prompt for {book!r} is suspiciously short: {len(positive)} chars"
        )

    negative = compose_negative()
    assert negative, "compose_negative() must return a non-empty string"
    assert "text" in negative.lower()
