"""THE GATE — loader hardening: prose_resolver drops unfilled atom-stub variants.

Root cause closed: phoenix_v4.rendering.prose_resolver._parse_block_file_with_prose
(and _parse_canonical_with_prose) parsed EVERY "## <SLOT> vNN" block into the
selectable variant pool with no placeholder filter, so a partially-authored atom
(real v01 + unfilled "[Persona-specific hook for …]" v02..vNN) leaked its stub
label into reader-facing prose. The registry path already filtered via
enrichment_select._REGISTRY_PLACEHOLDER_RE; the spine loader did not.

These tests prove:
  1. A mixed real+stub CANONICAL.txt yields ONLY the real variant(s) selectable.
  2. A required slot whose blocks are ALL stubs raises InsufficientVariantsError
     (author atoms upstream — never ship the stub).
  3. The shared stub detector (_is_stub_body) flags bracket / pipeline /
     ellipsis / bare-variable stubs while preserving legitimate bracketed prose
     (citations, [sic], [emphasis added]) and prose that merely mentions brackets.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from phoenix_v4.rendering.prose_resolver import (
    InsufficientVariantsError,
    _is_stub_body,
    _parse_block_file_with_prose,
    _parse_canonical_with_prose,
)


# --- block-file (non-STORY) format: header / empty-metadata / body fences ---
def _mixed_block_canonical() -> str:
    return """

## HOOK v01
---

---
You're at the kitchen table in scrubs still damp from shift, the pay stub and the rent bill spread out in front of you.
---

## HOOK v02
---

---
[Persona-specific hook for healthcare_rns × financial_anxiety]
---

## HOOK v03
---

---
[Persona-specific hook for healthcare_rns × financial_anxiety]
---
"""


def test_mixed_real_and_stub_only_real_selectable(tmp_path: Path) -> None:
    canonical = tmp_path / "CANONICAL.txt"
    canonical.write_text(_mixed_block_canonical(), encoding="utf-8")
    parsed = _parse_block_file_with_prose(
        canonical, "healthcare_rns", "financial_anxiety", "HOOK"
    )
    # Only the real v01 survives; the two bracket stubs are dropped.
    assert list(parsed.keys()) == ["healthcare_rns_financial_anxiety_HOOK_v01"]
    body = parsed["healthcare_rns_financial_anxiety_HOOK_v01"]
    assert body.startswith("You're at the kitchen table")
    # No fence leak, no bracket-stub token anywhere in the selectable pool.
    for v in parsed.values():
        assert "[" not in v
        assert not v.lstrip().startswith("---")


def test_required_slot_all_stubs_raises(tmp_path: Path) -> None:
    canonical = tmp_path / "CANONICAL.txt"
    canonical.write_text(
        """## HOOK v01
---

---
[Persona-specific hook for x × y]
---

## HOOK v02
---

---
[Persona-specific hook for x × y]
---
""",
        encoding="utf-8",
    )
    with pytest.raises(InsufficientVariantsError):
        _parse_block_file_with_prose(canonical, "x", "y", "HOOK", required=True)


def test_required_slot_with_one_real_does_not_raise(tmp_path: Path) -> None:
    canonical = tmp_path / "CANONICAL.txt"
    canonical.write_text(_mixed_block_canonical(), encoding="utf-8")
    parsed = _parse_block_file_with_prose(
        canonical, "healthcare_rns", "financial_anxiety", "HOOK", required=True
    )
    assert len(parsed) == 1  # one real variant → safe, no raise


def test_required_missing_file_returns_empty_no_raise(tmp_path: Path) -> None:
    # A non-existent file is "missing" (caller's concern), not an all-stub slot.
    parsed = _parse_block_file_with_prose(
        tmp_path / "nope.txt", "x", "y", "HOOK", required=True
    )
    assert parsed == {}


def test_existing_real_prose_block_still_parses(tmp_path: Path) -> None:
    # Regression: the metadata-then-prose block shape (test_book_renderer.py:484)
    # must still parse to the real body after stub filtering.
    canonical = tmp_path / "CANONICAL.txt"
    canonical.write_text(
        """## INTEGRATION v01
---
mode: BODY_LANDED
reframe_type: BODY_FACT
weight: light
carry_line: "line"
---
This is real prose, not metadata.
---
""",
        encoding="utf-8",
    )
    parsed = _parse_block_file_with_prose(canonical, "p", "t", "INTEGRATION")
    assert parsed["p_t_INTEGRATION_v01"].startswith("This is real prose")


def test_story_canonical_drops_stub_variants(tmp_path: Path) -> None:
    # STORY format: ## ROLE vNN --- metadata --- prose ---
    canonical = tmp_path / "CANONICAL.txt"
    canonical.write_text(
        """## RECOGNITION v01
---
beat: open
---
The comparison starts the moment the badge scanner beeps you onto the unit.
---

## RECOGNITION v02
---
beat: open
---
[Persona-specific hook for nyc_executives × self_worth]
---
""",
        encoding="utf-8",
    )
    parsed = _parse_canonical_with_prose(
        canonical, "nyc_executives", "self_worth", "comparison"
    )
    assert len(parsed) == 1
    only_body = next(iter(parsed.values()))
    assert "[" not in only_body
    assert only_body.startswith("The comparison starts")


@pytest.mark.parametrize(
    "body,is_stub",
    [
        ("[Persona-specific hook for healthcare_rns × financial_anxiety]", True),
        ("[Placeholder: HOOK]", True),
        ("[Missing: SCENE]", True),
        ("[...]", True),
        ("[…]", True),
        ("{street_name}", True),
        ("{{persona}}", True),
        ("%(topic)s", True),
        ("", True),
        ("   ", True),
        # Real prose / legitimate bracket forms must NOT be treated as stubs.
        ("You're at the kitchen table in scrubs still damp from shift.", False),
        ("[sic]", False),
        ("[emphasis added]", False),
        ("[12]", False),
        ("[Smith et al., 2020]", False),
        ("She noticed [emphasis added] the overdue notice.", False),
        ("The clinic on the corner was already closed.", False),
        # A {var} embedded in real prose is resolved downstream, NOT a stub here.
        ("You step off the train at {transit_stop} and the cold hits.", False),
    ],
)
def test_is_stub_body_classifier(body: str, is_stub: bool) -> None:
    assert _is_stub_body(body) is is_stub
