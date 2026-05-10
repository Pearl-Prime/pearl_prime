"""V1.1 Q4: zh_TW + zh_CN blocked_lora-first cleanup (PRJ-WORLDWIDE-CATALOG-GO-LIVE-V1).

Ensures catalog style resolution maps zh marketing-base slugs to trained
``brand_style_loras`` keys and that ``adi_da`` is registered for
``bright_presence_tw``. Does not assert on ``blocked_character_lora`` (separate
teacher-matrix keys such as ``qi_foundation_cultivation`` vs archetype slug).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "catalog" / "generate_manga_catalog.py"


def _load_generator():
    spec = importlib.util.spec_from_file_location("gmc_zh_lora", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["gmc_zh_lora"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def gmc():
    return _load_generator()


def test_zh_locales_have_zero_blocked_lora_rows(gmc):
    inputs = gmc.load_inputs()
    for locale in ("zh_TW", "zh_CN"):
        _rows, breakdown = gmc.build_rows_for_locale(locale, inputs)
        assert breakdown.get("blocked_lora", 0) == 0, (locale, breakdown)


def test_en_us_ja_jp_readiness_breakdown_unchanged(gmc):
    """Regression guard: LoRA resolution must not alter en/ja row statuses."""
    inputs = gmc.load_inputs()
    expected = {
        "en_US": {"ready": 155, "blocked_character_lora": 15},
        "ja_JP": {"ready": 153, "blocked_character_lora": 13},
    }
    for locale, want in expected.items():
        _rows, breakdown = gmc.build_rows_for_locale(locale, inputs)
        assert dict(sorted(breakdown.items())) == dict(sorted(want.items())), (
            locale,
            breakdown,
        )


def test_zh_marketing_bases_resolve_style_refs(gmc):
    plans = gmc.load_inputs()["brand_lora_plans"]["data"]
    cases = [
        ("sleep_repair_tw", "sleep_restoration"),
        ("panic_first_aid_cn", "stabilizer"),
        ("gen_z_grounding_tw", "digital_ground"),
        ("grief_companion_cn", "body_memory"),
        ("inner_security_tw", "relational_calm"),
    ]
    for brand, expected_key in cases:
        ref, char = gmc.lora_refs(plans, brand, "ahjan")
        assert expected_key in ref, (brand, ref)
        assert char, (brand, char)
    ref_b, char_b = gmc.lora_refs(plans, "bright_presence_tw", "adi_da")
    assert "stillness_press" in ref_b
    assert "adi_da" in char_b
