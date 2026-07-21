"""Regression tests for zh-TW resolver locale-threading.

Ensures non-persona resolver loaders read the localized CANONICAL.txt that
already exists on disk when locale='zh-TW', while leaving en-US byte-identical.
See docs/ZHTW_RESOLVER_LOCALE_THREADING_SPEC.md.
"""
from phoenix_v4.planning.registry_resolver import _load_composite_doctrine_atoms


def _cjk(s: str) -> int:
    return sum(1 for c in s if "一" <= c <= "鿿")


def _joined(atoms: dict) -> str:
    return " ".join(
        b["content"] for pool in atoms.values() for b in pool if isinstance(b, dict)
    )


def test_composite_doctrine_localizes_zhtw():
    """zh-TW doctrine reads the on-disk localized CANONICAL.txt (Chinese)."""
    zh = _joined(_load_composite_doctrine_atoms("anxiety", locale="zh-TW"))
    assert _cjk(zh) > 500, "expected substantial Chinese content for zh-TW doctrine"


def test_composite_doctrine_en_us_unchanged():
    """en-US (and default) stays English — no behaviour change."""
    en = _joined(_load_composite_doctrine_atoms("anxiety", locale="en-US"))
    default = _joined(_load_composite_doctrine_atoms("anxiety"))
    assert _cjk(en) == 0, "en-US doctrine must contain no CJK"
    assert en == default, "explicit en-US must equal locale-less default"


def test_composite_doctrine_missing_locale_falls_back():
    """A locale with no localized file falls back to English, never crashes."""
    fr = _joined(_load_composite_doctrine_atoms("anxiety", locale="fr-FR"))
    en = _joined(_load_composite_doctrine_atoms("anxiety", locale="en-US"))
    # No fr-FR doctrine on disk for this topic -> English fallback (honest).
    assert fr == en


# --------------------------------------------------------------------------- #
# story_plan loader (build_story_schedule -> _load_all_atoms)
# --------------------------------------------------------------------------- #
from pathlib import Path

from phoenix_v4.planning.story_planner import _load_all_atoms

_PERSONA, _TOPIC = "gen_z_professionals", "anxiety"


def _story_meta(atoms):
    return [(a.variant, a.arc_position, a.character, a.word_count) for a in atoms]


def test_story_selection_metadata_locale_independent():
    """Character/variant/word_count derive from English -> selection is
    deterministic regardless of locale (rendered text may differ)."""
    root = Path(".")
    en = _load_all_atoms(_PERSONA, _TOPIC, root, locale="en-US")
    zh = _load_all_atoms(_PERSONA, _TOPIC, root, locale="zh-TW")
    assert len(en) == len(zh) and len(en) > 0
    assert _story_meta(en) == _story_meta(zh)


def test_story_en_us_no_cjk():
    """en-US story text is unchanged (no CJK)."""
    root = Path(".")
    en = _load_all_atoms(_PERSONA, _TOPIC, root, locale="en-US")
    assert sum(_cjk(a.text) for a in en) == 0


def test_story_zhtw_renders_localized_subset():
    """zh-TW renders Chinese for every story variant that has a localized
    sibling on disk (partial subset -> honest English fallback for the rest)."""
    root = Path(".")
    zh = _load_all_atoms(_PERSONA, _TOPIC, root, locale="zh-TW")
    localized = sum(1 for a in zh if _cjk(a.text) > 20)
    assert localized > 0, "expected some zh-TW story variants to render Chinese"


# --------------------------------------------------------------------------- #
# angle_atom loaders (_try_angle_definition / _try_angle_callback)
# --------------------------------------------------------------------------- #
from phoenix_v4.planning.enrichment_select import (
    _try_angle_callback,
    _try_angle_definition,
)

_ANGLE = "PROTECTIVE_ALARM"


def test_angle_definition_localizes_zhtw_and_en_us_unchanged():
    root, w = Path("."), []
    en = _try_angle_definition(
        persona_id=_PERSONA, topic_id=_TOPIC, angle_id=_ANGLE,
        repo_root=root, fallback_warnings=w, locale="en-US",
    )
    zh = _try_angle_definition(
        persona_id=_PERSONA, topic_id=_TOPIC, angle_id=_ANGLE,
        repo_root=root, fallback_warnings=w, locale="zh-TW",
    )
    assert en[1] == "angle_atom" and _cjk(en[0]) == 0
    assert zh[1] == "angle_atom" and _cjk(zh[0]) > 20


def test_angle_callback_localizes_zhtw_and_en_us_unchanged():
    root, w = Path("."), []
    en = _try_angle_callback(
        persona_id=_PERSONA, topic_id=_TOPIC, angle_id=_ANGLE, layer=3,
        repo_root=root, fallback_warnings=w, locale="en-US",
    )
    zh = _try_angle_callback(
        persona_id=_PERSONA, topic_id=_TOPIC, angle_id=_ANGLE, layer=3,
        repo_root=root, fallback_warnings=w, locale="zh-TW",
    )
    assert en[1] == "angle_atom" and _cjk(en[0]) == 0
    assert zh[1] == "angle_atom" and _cjk(zh[0]) > 20


# --------------------------------------------------------------------------- #
# practice_library loader (locale-aware inbox + locale-keyed cache)
# --------------------------------------------------------------------------- #
from phoenix_v4.exercises.practice_library_loader import (
    get_exercise_for_chapter,
    load_practice_library,
)


def _lib_text(lib):
    return " ".join(
        str(it.get("text", "")) for pool in lib.values() for it in pool
    )


def test_practice_library_cache_is_locale_isolated():
    """en-US and zh-TW must not share a cache entry."""
    en = load_practice_library(locale="en-US")
    zh = load_practice_library(locale="zh-TW")
    assert _cjk(_lib_text(en)) == 0
    assert _cjk(_lib_text(zh)) > 0


def test_practice_exercise_composes_localized():
    """End-to-end composed exercise: en-US no CJK, zh-TW contains Chinese."""
    kw = dict(topic_id=_TOPIC, persona_id=_PERSONA, seed="flagship_phase2_layer6")
    en = get_exercise_for_chapter(chapter_index=2, locale="en-US", **kw)
    zh = get_exercise_for_chapter(chapter_index=2, locale="zh-TW", **kw)
    assert en and _cjk(en) == 0
    assert zh and _cjk(zh) > 20
