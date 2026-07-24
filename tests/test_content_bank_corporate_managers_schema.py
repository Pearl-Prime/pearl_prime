"""Regression test for Finding B.2 — anxiety_corporate_managers_scene_recognition_bank.yaml
schema backfill.

Prior to this fix, the bank shipped in a pre-schema-hardening format (only
variant_id/collision_family/body) and was silently skipped by the per-file
fail-safe loader added in PR #59, meaning the corporate_managers persona never
received this bank's content-bank enrichment. This test proves the bank now
validates cleanly against REQUIRED_VARIANT_KEYS and is actually loaded into the
registry (not silently dropped).
"""
from __future__ import annotations

from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")

from phoenix_v4.content_banks.loader import (
    REQUIRED_VARIANT_KEYS,
    ContentBankSchemaError,
    _validate_variant,
    load_content_bank_registry,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
BANK_PATH = REPO_ROOT / "config" / "content_banks" / "anxiety_corporate_managers_scene_recognition_bank.yaml"
BANK_STEM = "anxiety_corporate_managers_scene_recognition_bank"


def _load_variants():
    with open(BANK_PATH, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return data["variants"]


def test_bank_file_exists():
    assert BANK_PATH.exists(), "anxiety_corporate_managers_scene_recognition_bank.yaml must exist"


def test_all_variants_have_required_keys():
    variants = _load_variants()
    assert len(variants) == 40, "backfill must preserve all 40 authored variants"
    for rec in variants:
        missing = REQUIRED_VARIANT_KEYS - set(rec.keys())
        assert not missing, f"{rec.get('variant_id')} missing keys: {sorted(missing)}"


def test_all_variants_pass_loader_validation():
    variants = _load_variants()
    for rec in variants:
        # Raises ContentBankSchemaError on any schema violation — must not raise.
        _validate_variant(rec, source=str(BANK_PATH))


def test_variant_ids_unique_and_stable():
    variants = _load_variants()
    ids = [v["variant_id"] for v in variants]
    assert len(ids) == len(set(ids)), "variant_id values must be unique"
    assert ids[0] == "acmr_001" and ids[-1] == "acmr_040"


def test_signature_phrases_are_verbatim_substrings_of_body():
    variants = _load_variants()
    for rec in variants:
        body_norm = " ".join(rec["body"].split()).lower()
        for phrase in rec["signature_phrases"]:
            phrase_norm = " ".join(phrase.split()).lower()
            assert phrase_norm in body_norm, (
                f"{rec['variant_id']}: signature_phrase {phrase!r} not found in body"
            )


def test_bank_is_actually_loaded_into_registry():
    """The registry-level proof: this bank must appear in the loaded registry,
    not be silently skipped by the per-file fail-safe (PR #59)."""
    registry = load_content_bank_registry(banks_dir=REPO_ROOT / "config" / "content_banks")
    assert BANK_STEM in registry.banks, (
        f"{BANK_STEM} was skipped by the registry loader — schema backfill did not take"
    )
    assert len(registry.banks[BANK_STEM]) == 40


def test_bank_reachable_via_persona_and_topic_allowlists():
    variants = _load_variants()
    for rec in variants:
        assert rec["persona_allowlist"] == ["corporate_managers"]
        assert rec["topic_allowlist"] == ["anxiety"]
