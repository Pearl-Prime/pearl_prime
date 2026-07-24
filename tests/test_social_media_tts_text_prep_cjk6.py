"""CJK6 TTS text-prep rulesets (Lane 2, SOCIALTTS-L2, 2026-07-24).

Covers two things:
1. The `apply_text_prep` loader extension (locale-aware sentence-boundary
   punctuation) does NOT change English behavior — English must stay
   byte-identical to the pre-extension implementation.
2. Each of the six CJK rulesets loads, applies cleanly through the shared
   loader, and its headline rule fires correctly (colon->full-stop,
   terminal punctuation, and one representative homograph/trap rewrite per
   locale — including the zh-TW 和/與 compound guard and the zh-HK hard
   `cosyvoice2_language: yue` rule).

Authority: artifacts/research/social_media_tts_text_prep_cjk6_2026-07-24/REPORT.md
Acceptance layer: RESEARCHED + CONFIG-EXISTS — this test proves the rules
apply as authored; it does NOT prove correct pronunciation on real audio
(that's Lane 4's job, EXECUTED-REAL).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts" / "social_media"))

import tts_text_prep as ttp  # noqa: E402

CONFIG_DIR = REPO / "config" / "tts"

CJK6_FILES = {
    "ja_JP": CONFIG_DIR / "social_media_tts_text_prep_ja_JP.yaml",
    "ko_KR": CONFIG_DIR / "social_media_tts_text_prep_ko_KR.yaml",
    "zh_CN": CONFIG_DIR / "social_media_tts_text_prep_zh_CN.yaml",
    "zh_TW": CONFIG_DIR / "social_media_tts_text_prep_zh_TW.yaml",
    "zh_HK": CONFIG_DIR / "social_media_tts_text_prep_zh_HK.yaml",
    "zh_SG": CONFIG_DIR / "social_media_tts_text_prep_zh_SG.yaml",
}

EXPECTED_COSYVOICE2_LANGUAGE = {
    "ja_JP": "ja",
    "ko_KR": "ko",
    "zh_CN": "zh",
    "zh_TW": "zh",
    "zh_HK": "yue",   # hard rule: Cantonese, NEVER "zh"
    "zh_SG": "zh",
}


# ---------------------------------------------------------------------------
# 1. English regression — must stay byte-identical after the loader extension
# ---------------------------------------------------------------------------

def test_english_colon_and_pacing_unchanged():
    prep = ttp.load_prep()  # default: English config/tts/social_media_tts_text_prep.yaml
    out = ttp.apply_text_prep(
        "You can feel it after the third urgent chat ping: tight chest, and the urge to fix every silence.",
        prep,
    )
    assert out == (
        "You can feel it after the third urgent chat ping. "
        "Tight chest. And the urge to fix every silence."
    )


def test_english_default_terminal_punct_is_ascii_period():
    prep = ttp.load_prep()
    out = ttp.apply_text_prep("no terminal punctuation here", prep)
    assert out.endswith(".")
    assert not out.endswith("。")


def test_english_policy_has_no_cjk_overrides():
    prep = ttp.load_prep()
    policy = prep.get("policy") or {}
    # English config predates this extension and must not need these keys.
    assert "sentence_end_chars" not in policy
    assert "sentence_boundary_requires_space" not in policy


# ---------------------------------------------------------------------------
# 2. Every CJK6 file loads and applies through the shared loader
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tag,path", CJK6_FILES.items())
def test_cjk6_ruleset_loads_and_applies(tag, path):
    assert path.exists(), f"missing ruleset file for {tag}: {path}"
    prep = ttp.load_prep(path)
    assert prep.get("schema_version") == 2
    assert prep.get("cosyvoice2_language") == EXPECTED_COSYVOICE2_LANGUAGE[tag]
    # Must apply without raising on arbitrary mixed-script input.
    out = ttp.apply_text_prep("测试 test 123 テスト 하나둘셋", prep)
    assert isinstance(out, str) and out


def test_zh_hk_hard_pins_yue_never_zh():
    prep = ttp.load_prep(CJK6_FILES["zh_HK"])
    assert prep["cosyvoice2_language"] == "yue"
    assert prep["cosyvoice2_language"] != "zh"
    assert any("yue" in rule for rule in prep.get("hard_rules", []))


# ---------------------------------------------------------------------------
# 3. CJK terminal punctuation is locale-correct (。not .)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "tag",
    ["ja_JP", "zh_CN", "zh_TW", "zh_HK", "zh_SG"],
)
def test_cjk_fullwidth_terminal_punct_appended(tag):
    prep = ttp.load_prep(CJK6_FILES[tag])
    out = ttp.apply_text_prep("这是一句没有结尾标点的话", prep)
    assert out.endswith("。")
    assert not out.endswith(".")


def test_korean_uses_ascii_terminal_punct_like_english():
    # Korean punctuation is Latin-style (. ! ? ,) unlike ja/zh* — no override needed.
    prep = ttp.load_prep(CJK6_FILES["ko_KR"])
    out = ttp.apply_text_prep("이것은 마침표가 없는 문장입니다", prep)
    assert out.endswith(".")


# ---------------------------------------------------------------------------
# 4. Colon-to-full-stop fires, but clock times/ratios are digit-guarded
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tag", ["ja_JP", "zh_CN", "zh_TW", "zh_HK", "zh_SG"])
def test_colon_becomes_fullwidth_period_but_not_between_digits(tag):
    prep = ttp.load_prep(CJK6_FILES[tag])
    out = ttp.apply_text_prep("请注意：这是重点", prep)
    assert "：" not in out and ":" not in out
    assert "。" in out
    # Clock-time-shaped digit:digit must not be split.
    out2 = ttp.apply_text_prep("3:00", prep)
    assert "3:00" in out2 or "3：00" in out2


# ---------------------------------------------------------------------------
# 5. Representative homograph/trap rewrites per locale
# ---------------------------------------------------------------------------

def test_ja_ichinichi_zutsu_forces_duration_reading():
    prep = ttp.load_prep(CJK6_FILES["ja_JP"])
    out = ttp.apply_text_prep("一日ずつ進みましょう", prep)
    assert "いちにちずつ" in out
    assert "一日ずつ" not in out


def test_ko_native_counter_forces_native_numeral_for_hours():
    prep = ttp.load_prep(CJK6_FILES["ko_KR"])
    out = ttp.apply_text_prep("3시간 동안 쉬세요", prep)
    assert "세 시간" in out
    assert "3시간" not in out


def test_ko_sino_korean_minutes_left_untouched():
    # 분 (minutes) is Sino-Korean and must NOT be native-numeral-rewritten.
    prep = ttp.load_prep(CJK6_FILES["ko_KR"])
    out = ttp.apply_text_prep("3분만 기다리세요", prep)
    assert "3분" in out


def test_ko_counter_rule_fires_with_attached_particle_no_space():
    # Regression: Korean particles (의/를/만…) attach directly to the counter
    # with NO space ("3개의", not "3개 의"). An earlier draft of this rule
    # required a trailing \b after the counter, which never matches here
    # because Python's \b treats Hangul as a word character — so "개" and
    # the following "의" never form a boundary. Fixed by dropping the
    # trailing \b (the leading \b already protects multi-digit numbers).
    prep = ttp.load_prep(CJK6_FILES["ko_KR"])
    out = ttp.apply_text_prep("오늘 하루 3개의 작은 목표만 정해보세요", prep)
    assert "세 개의" in out
    assert "3개의" not in out


def test_ko_counter_rule_does_not_fire_inside_multidigit_number():
    # "23개" must not be misread as if it were "3개" (leading \b protects this).
    prep = ttp.load_prep(CJK6_FILES["ko_KR"])
    out = ttp.apply_text_prep("23개는 건드리면 안 됩니다", prep)
    assert "23개" in out
    assert "세 개" not in out


def test_zh_cn_kanhu_avoids_kan_kan_polyphone():
    prep = ttp.load_prep(CJK6_FILES["zh_CN"])
    out = ttp.apply_text_prep("感谢每一位看护人员", prep)
    assert "照护" in out
    assert "看护" not in out


def test_zh_tw_he_conjunction_becomes_yu_but_compounds_survive():
    prep = ttp.load_prep(CJK6_FILES["zh_TW"])
    out = ttp.apply_text_prep("身體和情緒需要一起照顧", prep)
    assert "身體與情緒" in out

    for protected in ["溫和", "和平", "和諧", "和解", "和好", "隨和", "附和"]:
        out_protected = ttp.apply_text_prep(f"這是{protected}的例子", prep)
        assert protected in out_protected, f"{protected} was incorrectly rewritten"


def test_zh_sg_shares_zh_cn_polyphone_fixes():
    prep = ttp.load_prep(CJK6_FILES["zh_SG"])
    out = ttp.apply_text_prep("感谢每一位看护人员", prep)
    assert "照护" in out


# ---------------------------------------------------------------------------
# 6. do_not_blind_replace guard lists exist and are non-empty (documentation
#    contract — the loader does not consume this key, but every ruleset must
#    carry one, mirroring the English precedent's false-positive guard).
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tag,path", CJK6_FILES.items())
def test_do_not_blind_replace_guard_present(tag, path):
    prep = ttp.load_prep(path)
    guard = prep.get("do_not_blind_replace")
    assert guard, f"{tag} ruleset is missing a do_not_blind_replace guard list"
