"""Lane G — register-gate composer-guard backstop (DEFECT 7, lane 2).

Fail-closed backstop complementing the content-repair lane: even when an atom
bank ships a MALFORMED block header (missing its "## " prefix), the renderer must
never let a raw atom-id label ("INTEGRATION v06", "RECOGNITION v04") reach reader
prose, and the parser must still split the un-repaired atom into separate blocks.

Covers all three guard sites:
  1. registry_resolver._parse_canonical_txt recognizes BARE block headers.
  2. book_renderer scrubbers strip bare atom-id lines (no "##" required).
  3. delivery_contract_gate fail-closes on a leaked bare atom-id label.

See artifacts/analysis/pearl_prime_priorities/COMPOSER_FRONTIER_FIX_SPEC_20260614.md
"""
from __future__ import annotations

import pytest

from phoenix_v4.planning.registry_resolver import _parse_canonical_txt
from phoenix_v4.rendering.book_renderer import (
    DeliveryContractError,
    _scrub_inline_leaked_slot_markers,
    clean_for_delivery,
    delivery_contract_gate,
)


# ---------------------------------------------------------------------------
# Site 1 — registry_resolver._parse_canonical_txt: bare-header recognition
# ---------------------------------------------------------------------------

def test_malformed_bare_header_parses_into_separate_blocks(tmp_path) -> None:
    """A second block whose "## " prefix is missing must NOT be absorbed.

    Without the guard, the bare "INTEGRATION v06" header is treated as body text
    and the two atoms merge into one block (and the label leaks into prose). With
    the guard it parses into two distinct blocks.
    """
    canonical = tmp_path / "CANONICAL.txt"
    canonical.write_text(
        "## INTEGRATION v05\n"
        "---\n"
        "family: F4\n"
        "---\n"
        "First integration body about staying with the pattern.\n"
        "\n"
        "INTEGRATION v06\n"  # <-- malformed: no "## " prefix
        "---\n"
        "family: F4\n"
        "---\n"
        "Second integration body about choosing again.\n",
        encoding="utf-8",
    )

    blocks = _parse_canonical_txt(canonical, slot_type="INTEGRATION")

    assert len(blocks) == 2, f"expected 2 separate blocks, got {len(blocks)}"
    assert blocks[0]["atom_id"] == "INTEGRATION v05"
    assert blocks[1]["atom_id"] == "INTEGRATION v06"
    # The raw atom-id label must never appear inside the prior block's body.
    assert "INTEGRATION v06" not in blocks[0]["content"]
    assert "First integration body" in blocks[0]["content"]
    assert "Second integration body" in blocks[1]["content"]


def test_well_formed_headers_still_parse_unchanged(tmp_path) -> None:
    """Regression guard: the normal "## " path is unaffected by the new branch."""
    canonical = tmp_path / "CANONICAL.txt"
    canonical.write_text(
        "## HOOK v01\n"
        "---\n"
        "---\n"
        "Body one.\n"
        "## HOOK v02\n"
        "---\n"
        "---\n"
        "Body two.\n",
        encoding="utf-8",
    )
    blocks = _parse_canonical_txt(canonical, slot_type="HOOK")
    assert [b["atom_id"] for b in blocks] == ["HOOK v01", "HOOK v02"]
    assert blocks[0]["content"] == "Body one."
    assert blocks[1]["content"] == "Body two."


def test_grammatical_line_not_misread_as_bare_header(tmp_path) -> None:
    """A bare-looking token NOT followed by '---' stays in the body (no false split).

    Guards against the bare-header branch eating a legitimate mid-atom line.
    """
    canonical = tmp_path / "CANONICAL.txt"
    canonical.write_text(
        "## STORY v01\n"
        "---\n"
        "---\n"
        "The body mentions a step labeled STEP v1 in passing prose.\n"
        "It continues normally on the next line.\n",
        encoding="utf-8",
    )
    blocks = _parse_canonical_txt(canonical, slot_type="STORY")
    assert len(blocks) == 1
    assert "STEP v1 in passing prose" in blocks[0]["content"]


# ---------------------------------------------------------------------------
# Site 2 — book_renderer scrubbers: bare atom-id line scrubbed (no "##")
# ---------------------------------------------------------------------------

def test_scrub_bare_atom_id_line_returns_empty() -> None:
    """The line-level scrubber must not early-return on a bare (no-'##') label."""
    assert _scrub_inline_leaked_slot_markers("INTEGRATION v06") == ""
    assert _scrub_inline_leaked_slot_markers("RECOGNITION v04") == ""


def test_scrub_keeps_ordinary_prose() -> None:
    """Ordinary prose (and prose containing lowercase 'v6') is untouched."""
    line = "Start with the pressure under the sternum."
    assert _scrub_inline_leaked_slot_markers(line) == line
    line2 = "She drove a v8 down the avenue."
    assert _scrub_inline_leaked_slot_markers(line2) == line2


def test_clean_for_delivery_strips_bare_atom_id_label() -> None:
    """A synthetic chapter containing a bare 'INTEGRATION v06' line is scrubbed."""
    raw = (
        "Chapter 1\n\n"
        "Real opening prose for the chapter.\n\n"
        "INTEGRATION v06\n\n"
        "More real prose after the leaked label.\n"
    )
    out = clean_for_delivery(raw)
    assert "INTEGRATION v06" not in out
    assert "Real opening prose for the chapter." in out
    assert "More real prose after the leaked label." in out
    # And the cleaned output passes the gate (the leak is gone).
    delivery_contract_gate(out, source_hint="test")


# ---------------------------------------------------------------------------
# Site 3 — delivery_contract_gate: fail-closed on a leaked bare atom-id label
# ---------------------------------------------------------------------------

def test_delivery_contract_gate_raises_on_bare_atom_id_label() -> None:
    """If a bare atom-id label survives into final prose, the build must hard-fail."""
    dirty = "Some prose.\nINTEGRATION v06\nMore prose.\n"
    with pytest.raises(DeliveryContractError) as exc:
        delivery_contract_gate(dirty, source_hint="test")
    assert "bare atom-id label" in str(exc.value).lower()


def test_delivery_contract_gate_passes_clean_prose() -> None:
    """Clean prose with no leaked labels must not raise."""
    clean = (
        "Chapter 1\n\n"
        "This is ordinary reader prose with no scaffolding.\n\n"
        "It mentions resilience but never an atom-id label.\n"
    )
    delivery_contract_gate(clean, source_hint="test")
