"""Focused tests for clean_for_delivery scaffolding strip + delivery_contract_gate leaks."""

import pytest

from phoenix_v4.rendering.book_renderer import (
    DeliveryContractError,
    clean_for_delivery,
    delivery_contract_gate,
)


def test_strip_inline_hook_header_with_dashes() -> None:
    raw = "## HOOK v01 --- --- some text\n\nReal prose here.\n"
    out = clean_for_delivery(raw)
    assert "## HOOK" not in out
    assert "some text" not in out
    assert "Real prose here." in out
    delivery_contract_gate(out, source_hint="test")


def test_strip_story_uppercase_still_strips() -> None:
    raw = "## STORY v01\n\nBody.\n"
    out = clean_for_delivery(raw)
    assert "## STORY" not in out
    assert "Body." in out


def test_preserves_title_case_story_heading() -> None:
    raw = "## Story of my life\n\nKept.\n"
    out = clean_for_delivery(raw)
    assert "## Story of my life" in out
    assert "Kept." in out
    delivery_contract_gate(out, source_hint="test")


def test_strip_single_line_intro_dict() -> None:
    raw = "Before.\n\n{'intro': 'foo', 'body': 'bar'}\n\nAfter.\n"
    out = clean_for_delivery(raw)
    assert "{'intro'" not in out and '{"intro"' not in out
    assert "foo" not in out
    assert "Before." in out
    assert "After." in out
    delivery_contract_gate(out, source_hint="test")


def test_strip_multiline_intro_dict_preserves_prose() -> None:
    raw = (
        "Open paragraph.\n\n"
        '{"intro": "x",\n'
        ' "body": "y"}\n\n'
        "Close paragraph.\n"
    )
    out = clean_for_delivery(raw)
    assert "intro" not in out
    assert "Open paragraph." in out
    assert "Close paragraph." in out
    delivery_contract_gate(out, source_hint="test")


def test_delivery_contract_gate_inline_header_leak() -> None:
    dirty = "## HOOK v01 --- trailing\nOK\n"
    with pytest.raises(DeliveryContractError) as exc:
        delivery_contract_gate(dirty, source_hint="test")
    assert "slot heading" in str(exc.value).lower() or "assembly" in str(exc.value).lower()


def test_delivery_contract_gate_dict_literal_leak() -> None:
    dirty = "Text\n{'intro': 'bad'}\n"
    with pytest.raises(DeliveryContractError) as exc:
        delivery_contract_gate(dirty, source_hint="test")
    assert "intro-dict" in str(exc.value).lower()
