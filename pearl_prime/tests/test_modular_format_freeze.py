import pytest

from pearl_prime.modular_format_freeze import (
    BLOCKED_LEGACY_RUNTIMES,
    FREEZE_CONFIG_PATH,
    apply_output_format_to_plan,
    load_freeze_settings,
    reject_legacy_format,
)


def test_freeze_config_loads():
    settings = load_freeze_settings(FREEZE_CONFIG_PATH)
    assert settings.enabled is True
    assert "five_min_practice" in settings.formats
    assert "protocol_library" in settings.formats


def test_apply_output_format_to_plan_rewrites_slot_shape():
    settings = load_freeze_settings(FREEZE_CONFIG_PATH)
    base = {
        "format_structural_id": "F006",
        "format_runtime_id": "standard_book",
        "chapter_count": 12,
        "slot_definitions": [["HOOK", "SCENE", "STORY", "REFLECTION", "EXERCISE", "INTEGRATION"]] * 12,
    }
    out = apply_output_format_to_plan(
        base,
        output_format_id="myth_vs_mechanism",
        chapter_count=8,
        settings=settings,
    )
    assert out["format_structural_id"] == "MOD_myth_vs_mechanism"
    assert out["format_runtime_id"] == "short_book_30"
    assert out["chapter_count"] == 8
    assert len(out["slot_definitions"]) == 8
    assert out["slot_definitions"][0] == ["HOOK", "SCENE", "STORY", "PIVOT", "REFLECTION", "EXERCISE", "TAKEAWAY", "INTEGRATION", "THREAD"]
    assert out["output_format_id"] == "myth_vs_mechanism"


def test_legacy_runtimes_blocked():
    """V4 freeze MUST block all legacy long-form formats (1hr+)."""
    settings = load_freeze_settings(FREEZE_CONFIG_PATH)
    assert settings.enabled, "V4 freeze must be enabled"
    for rt in BLOCKED_LEGACY_RUNTIMES:
        with pytest.raises(ValueError, match="BLOCKED"):
            reject_legacy_format(rt, settings)


def test_v4_formats_not_blocked():
    """V4 modular short formats must NOT be blocked."""
    settings = load_freeze_settings(FREEZE_CONFIG_PATH)
    for fmt_id in settings.formats:
        rt = settings.formats[fmt_id].get("runtime_format_id", "")
        reject_legacy_format(rt, settings)  # should not raise


def test_blocked_runtimes_are_complete():
    """Ensure all known legacy long-form runtimes are in the blocklist."""
    expected = {"standard_book", "extended_book_2h", "deep_book_4h", "deep_book_6h"}
    assert BLOCKED_LEGACY_RUNTIMES == expected
