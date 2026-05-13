"""Locale-aware persona atom loading regression tests (LOCALE-PROP-FIX-2026).

Asserts the standard (non-teacher) spine/registry pipeline reads atoms from
``atoms/<persona>/<topic>/<slot>/locales/<locale>/CANONICAL.txt`` when a
non-en-US locale is requested, with English fallback when the locale variant
is missing. Pre-fix, ``_load_persona_atoms`` ignored the locale entirely and
non-en-US runs produced 100% English books even when locale CANONICAL.txt
files existed under ``atoms/.../locales/<locale>/``.
"""
from __future__ import annotations

from pathlib import Path

import pytest

import phoenix_v4.planning.registry_resolver as rr


CANONICAL_EN = """## STORY v01
---
band: 3
---
This is the English body that must NOT appear for ja-JP runs when a
locale-specific variant exists for the same atom directory.
---
"""

CANONICAL_JP = """## STORY v01
---
band: 3
---
これは日本語の本文です。ロケールが ja-JP のときは英語の代わりにこれが
読み込まれる必要があります。
---
"""


def _seed_persona_topic(
    tmp_atoms_root: Path,
    persona: str,
    topic: str,
    slot: str,
    en_body: str,
    locale_bodies: dict[str, str] | None = None,
) -> None:
    slot_dir = tmp_atoms_root / persona / topic / slot
    slot_dir.mkdir(parents=True, exist_ok=True)
    (slot_dir / "CANONICAL.txt").write_text(en_body, encoding="utf-8")
    for locale, body in (locale_bodies or {}).items():
        locale_dir = slot_dir / "locales" / locale
        locale_dir.mkdir(parents=True, exist_ok=True)
        (locale_dir / "CANONICAL.txt").write_text(body, encoding="utf-8")


@pytest.fixture
def isolated_atoms_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Repoint registry_resolver.ATOMS_ROOT at a tmp dir for the duration of the test."""
    monkeypatch.setattr(rr, "ATOMS_ROOT", tmp_path)
    return tmp_path


def test_locale_path_helper_prefers_locale_file_when_present(
    isolated_atoms_root: Path,
) -> None:
    """Direct unit test for `_locale_canonical_path`."""
    slot_dir = isolated_atoms_root / "p" / "t" / "STORY"
    slot_dir.mkdir(parents=True)
    base = slot_dir / "CANONICAL.txt"
    base.write_text("en", encoding="utf-8")
    locale = slot_dir / "locales" / "ja-JP" / "CANONICAL.txt"
    locale.parent.mkdir(parents=True)
    locale.write_text("ja", encoding="utf-8")

    # Locale-specific file selected when present.
    assert rr._locale_canonical_path(slot_dir, "ja-JP") == locale
    # en-US is treated as base (no locale subdir lookup, even if it existed).
    assert rr._locale_canonical_path(slot_dir, "en-US") == base
    # None / empty defaults to base.
    assert rr._locale_canonical_path(slot_dir, None) == base


def test_locale_path_helper_falls_back_when_locale_file_missing(
    isolated_atoms_root: Path,
) -> None:
    """Missing locale file → English fallback."""
    slot_dir = isolated_atoms_root / "p" / "t" / "STORY"
    slot_dir.mkdir(parents=True)
    base = slot_dir / "CANONICAL.txt"
    base.write_text("en", encoding="utf-8")
    # No locales/ subdir exists.
    assert rr._locale_canonical_path(slot_dir, "ja-JP") == base


def test_load_persona_atoms_returns_locale_content_for_non_en_us(
    isolated_atoms_root: Path,
) -> None:
    """
    The core bug fix: when locale='ja-JP' AND the locale CANONICAL.txt exists,
    _load_persona_atoms must return Japanese prose, NOT the English fallback.
    """
    _seed_persona_topic(
        isolated_atoms_root,
        persona="gen_z_professionals",
        topic="anxiety",
        slot="STORY",
        en_body=CANONICAL_EN,
        locale_bodies={"ja-JP": CANONICAL_JP},
    )

    atoms = rr._load_persona_atoms(
        "gen_z_professionals", "anxiety", locale="ja-JP"
    )
    assert "STORY" in atoms, "STORY pool should be present"
    bodies = [a["content"] for a in atoms["STORY"]]
    assert bodies, "STORY pool must have at least one atom"
    joined = "\n\n".join(bodies)
    # Must contain Japanese characters
    assert any("぀" <= ch <= "ヿ" or "一" <= ch <= "鿿" for ch in joined), (
        f"Expected CJK chars from ja-JP CANONICAL.txt, got: {joined[:200]!r}"
    )
    # Must NOT contain the English-only marker phrase
    assert "must NOT appear" not in joined, (
        "English fallback leaked into ja-JP atom pool — locale propagation broken."
    )


def test_load_persona_atoms_default_locale_returns_english(
    isolated_atoms_root: Path,
) -> None:
    """Regression-safe: default (locale=None) and locale='en-US' both return base English."""
    _seed_persona_topic(
        isolated_atoms_root,
        persona="gen_z_professionals",
        topic="anxiety",
        slot="STORY",
        en_body=CANONICAL_EN,
        locale_bodies={"ja-JP": CANONICAL_JP},
    )

    for loc in (None, "en-US"):
        atoms = rr._load_persona_atoms(
            "gen_z_professionals", "anxiety", locale=loc
        )
        joined = "\n\n".join(a["content"] for a in atoms.get("STORY", []))
        assert "must NOT appear" in joined, (
            f"locale={loc!r} should hit the base English file; "
            f"got: {joined[:200]!r}"
        )
        # No CJK should bleed in for the default path.
        assert not any(
            "぀" <= ch <= "ヿ" or "一" <= ch <= "鿿"
            for ch in joined
        ), f"locale={loc!r} unexpectedly produced CJK content"


def test_load_persona_atoms_locale_falls_back_when_locale_file_missing(
    isolated_atoms_root: Path,
) -> None:
    """ja-JP requested but only base English file exists → English used silently."""
    _seed_persona_topic(
        isolated_atoms_root,
        persona="gen_z_professionals",
        topic="anxiety",
        slot="STORY",
        en_body=CANONICAL_EN,
        locale_bodies=None,
    )

    atoms = rr._load_persona_atoms(
        "gen_z_professionals", "anxiety", locale="ja-JP"
    )
    joined = "\n\n".join(a["content"] for a in atoms.get("STORY", []))
    assert "must NOT appear" in joined
    assert not any(
        "぀" <= ch <= "ヿ" or "一" <= ch <= "鿿" for ch in joined
    )


def test_load_persona_atoms_skips_locales_subdir_as_slot_type(
    isolated_atoms_root: Path,
) -> None:
    """The 'locales' directory itself must not be misread as a slot type or engine."""
    _seed_persona_topic(
        isolated_atoms_root,
        persona="gen_z_professionals",
        topic="anxiety",
        slot="STORY",
        en_body=CANONICAL_EN,
        locale_bodies={"ja-JP": CANONICAL_JP},
    )
    # Also seed a sibling locales/ dir at the topic root (mimics
    # atoms/persona/topic/locales/ if anyone ever creates one).
    sibling = isolated_atoms_root / "gen_z_professionals" / "anxiety" / "locales"
    sibling.mkdir(parents=True, exist_ok=True)
    (sibling / "CANONICAL.txt").write_text("noise that must not load", encoding="utf-8")

    atoms = rr._load_persona_atoms(
        "gen_z_professionals", "anxiety", locale="ja-JP"
    )
    # 'LOCALES' must not appear as a slot type.
    assert "LOCALES" not in atoms
    joined = "\n\n".join(a["content"] for a in atoms.get("STORY", []))
    assert "noise that must not load" not in joined
