"""Tests for G-CLAIM / Q-ENFORCE-02 acceptance claim language gate."""
from __future__ import annotations

from scripts.ci.check_acceptance_claim_language import _scan_text


def test_claim_without_layer_fails():
    v = _scan_text("t", "This book is a bestseller and shippable.")
    assert v
    assert any("Q-ENFORCE-02" in x or "G-CLAIM" in x for x in v)


def test_claim_with_layer_passes():
    v = _scan_text(
        "t",
        "Not a bestseller register claim — this cell is structurally clear (Layer 1).",
    )
    assert v == []


def test_catalog_register_without_layer3_fails():
    v = _scan_text("t", "We will improve catalog register via composer tweaks.")
    assert v
    assert any("flagship lever" in x for x in v)


def test_catalog_register_with_ontgp_passes():
    v = _scan_text(
        "t",
        "Improve catalog register only after Layer 3 ONTGP on flagship_line_edit cells.",
    )
    assert v == []


def test_allowlist_skips():
    v = _scan_text(
        "t",
        "CI-ALLOWLIST: claim-language-ok\nThis is a bestseller discussion of doctrine.",
    )
    assert v == []
