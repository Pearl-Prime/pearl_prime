"""Tests for scripts/image_generation/prompt_compiler.py — see MANGA_QC_AND_EBOOK_PIPELINE_SPEC §A.3.6."""

from __future__ import annotations

import pytest

from scripts.image_generation.image_qc import validate_prompt
from scripts.image_generation.prompt_compiler import (
    MAX_NEGATIVE_TOKENS,
    MAX_POSITIVE_TOKENS,
    QUALITY_TOKENS,
    SHARED_NEGATIVE_TOKENS,
    TASK_STYLE_PRESETS,
    _extract_bio_keywords,
    _sha256,
    _token_count,
    compile_author_pic_prompt,
    compile_image_prompt,
)


def test_token_count_simple() -> None:
    assert _token_count("one two three") == 3


def test_token_count_with_commas() -> None:
    assert _token_count("a, b, c") == 3


def test_token_count_empty() -> None:
    assert _token_count("") == 0
    assert _token_count("   ") == 0


def test_sha256_deterministic() -> None:
    assert _sha256("hello") == _sha256("hello")


def test_sha256_different_inputs() -> None:
    assert _sha256("a") != _sha256("b")


def test_compile_basic_structure() -> None:
    c = compile_image_prompt(
        task="cover_art_base",
        subject="test subject",
        style_hint="calm",
        palette_tokens=["slate"],
        scene="scene",
        extra_positive="",
        extra_negative="",
        author_id="x",
        bio_keywords=["meditation"],
    )
    assert "positive" in c and "negative" in c
    assert "continuity_tags" in c and "provenance" in c
    assert c.get("qc_results") == []


def test_compile_includes_quality_tokens() -> None:
    c = compile_image_prompt(
        task="video_bank_image",
        subject="s",
        style_hint="h",
        palette_tokens=[],
        scene="",
        extra_positive="",
        extra_negative="",
        author_id="",
        bio_keywords=[],
    )
    assert "masterpiece" in c["positive"].lower()
    assert "best quality" in c["positive"].lower()


def test_compile_includes_negative_tokens() -> None:
    c = compile_image_prompt(
        task="cover_art_base",
        subject="subj",
        style_hint="st",
        palette_tokens=[],
        scene="sc",
        extra_positive="",
        extra_negative="",
        author_id="a",
        bio_keywords=[],
    )
    for part in ("low quality", "blurry"):
        assert part in c["negative"].lower()


def test_compile_style_hint() -> None:
    c = compile_image_prompt(
        task="cover_art_base",
        subject="sub",
        style_hint="ethereal blue",
        palette_tokens=[],
        scene="",
        extra_positive="",
        extra_negative="",
        author_id="",
        bio_keywords=[],
    )
    assert "ethereal blue" in c["positive"]


def test_compile_palette_tokens() -> None:
    c = compile_image_prompt(
        task="cover_art_base",
        subject="sub",
        style_hint="st",
        palette_tokens=["#abc", "mist"],
        scene="",
        extra_positive="",
        extra_negative="",
        author_id="",
        bio_keywords=[],
    )
    assert "#abc" in c["positive"] and "mist" in c["positive"]


def test_compile_scene() -> None:
    c = compile_image_prompt(
        task="cover_art_base",
        subject="sub",
        style_hint="st",
        palette_tokens=[],
        scene="sunset over water",
        extra_positive="",
        extra_negative="",
        author_id="",
        bio_keywords=[],
    )
    assert "sunset over water" in c["positive"]


def test_all_task_presets_exist() -> None:
    for key in ("cover_art_base", "video_bank_image", "author_pic"):
        assert key in TASK_STYLE_PRESETS


def test_author_pic_preset_applied() -> None:
    bio = "x" * 60 + " meditation coaching"
    c = compile_author_pic_prompt("ahjan", bio, "warm light", "Ahjan")
    assert "ahjan" in c.get("author_id", "") or c.get("author_id") == "ahjan"
    assert "meditation" in " ".join(c.get("continuity_tags", []))


def test_qc_passes_valid_prompt() -> None:
    c = compile_image_prompt(
        task="cover_art_base",
        subject="abstract book cover background, calm mood",
        style_hint="contemplative",
        palette_tokens=[],
        scene="soft light",
        extra_positive="",
        extra_negative="",
        author_id="ahjan",
        bio_keywords=[],
    )
    r = validate_prompt(c)
    assert r["status"] in ("passed", "passed_with_warnings")


def test_qc_blocks_empty_subject() -> None:
    bad = {
        "positive": "masterpiece, best quality",
        "negative": SHARED_NEGATIVE_TOKENS,
        "provenance": {"prompt_hash": _sha256("x")},
        "positive_token_count": 4,
        "negative_token_count": _token_count(SHARED_NEGATIVE_TOKENS),
    }
    r = validate_prompt(bad)
    assert r["status"] == "failed"
    assert "IMAGE.PROMPT.STRUCTURE" in r["blockers"]


def test_continuity_tags_task() -> None:
    c = compile_image_prompt(
        task="cover_art_base",
        subject="s",
        style_hint="",
        palette_tokens=[],
        scene="",
        extra_positive="",
        extra_negative="",
        author_id="",
        bio_keywords=[],
    )
    assert any(t.startswith("task:cover_art_base") for t in c["continuity_tags"])


def test_continuity_tags_author() -> None:
    c = compile_image_prompt(
        task="video_bank_image",
        subject="s",
        style_hint="",
        palette_tokens=[],
        scene="",
        extra_positive="",
        extra_negative="",
        author_id="kai",
        bio_keywords=[],
    )
    assert "author:kai" in c["continuity_tags"]


def test_continuity_tags_style() -> None:
    c = compile_image_prompt(
        task="cover_art_base",
        subject="sub",
        style_hint="muted",
        palette_tokens=[],
        scene="",
        extra_positive="",
        extra_negative="",
        author_id="",
        bio_keywords=[],
    )
    assert "style:muted" in c["continuity_tags"]


def test_continuity_tags_bio_keywords() -> None:
    c = compile_image_prompt(
        task="author_pic",
        subject="s",
        style_hint="",
        palette_tokens=[],
        scene="",
        extra_positive="",
        extra_negative="",
        author_id="a",
        bio_keywords=["yoga"],
    )
    assert "bio:yoga" in c["continuity_tags"]


def test_provenance_structure() -> None:
    c = compile_image_prompt(
        task="cover_art_base",
        subject="sub",
        style_hint="st",
        palette_tokens=[],
        scene="sc",
        extra_positive="",
        extra_negative="",
        author_id="id",
        bio_keywords=[],
    )
    p = c["provenance"]
    assert "prompt_hash" in p and "compiled_at" in p and p.get("version")


def test_provenance_hash_changes_with_prompt() -> None:
    a = compile_image_prompt(
        task="cover_art_base",
        subject="one",
        style_hint="s",
        palette_tokens=[],
        scene="",
        extra_positive="",
        extra_negative="",
        author_id="",
        bio_keywords=[],
    )
    b = compile_image_prompt(
        task="cover_art_base",
        subject="two",
        style_hint="s",
        palette_tokens=[],
        scene="",
        extra_positive="",
        extra_negative="",
        author_id="",
        bio_keywords=[],
    )
    assert a["provenance"]["prompt_hash"] != b["provenance"]["prompt_hash"]


def test_author_pic_prompt_basic() -> None:
    c = compile_author_pic_prompt(
        "ahjan",
        "y" * 55 + " meditation",
        "soft",
        "Ahjan",
    )
    assert c["positive"] and c["negative"]
    assert c.get("bio_length", 0) >= 50


def test_author_pic_prompt_bio_keywords() -> None:
    bio = "z" * 40 + " wellness and mindfulness practice daily"
    kws = _extract_bio_keywords(bio)
    assert "wellness" in kws or "mindfulness" in kws


def test_token_budget_constants() -> None:
    assert MAX_POSITIVE_TOKENS >= 80
    assert MAX_NEGATIVE_TOKENS >= 40
    assert MAX_POSITIVE_TOKENS <= 200
