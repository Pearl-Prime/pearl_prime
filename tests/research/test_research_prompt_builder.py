from __future__ import annotations

import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "research"))

from research_prompt_builder import (  # noqa: E402
    ResearchPromptInputs,
    build_prompt_package,
    score_prompt_quality,
    write_prompt_package,
)
from run_research import require_prompt_package_or_legacy_ack  # noqa: E402


def test_china_brief_preserves_wrapped_decision_and_routes_to_qwen() -> None:
    inputs = ResearchPromptInputs(
        prompt_id="pain_points",
        title="China self-help audio discovery prompt repair",
        issue_description="China research was too Western and missed local discovery surfaces.",
        transcript="""Failing output symptom:
- no Simplified Chinese source plan
- no comparison of Ximalaya vs Douyin vs Xiaohongshu
- generic TikTok advice

Decision needed:
Should China research be routed to Qwen / QuinChat first, and what should
it ask so Phoenix Omega can decide whether to create China-specific
metadata, consumer-language, and funnel configs?

Unknowns:
- what local-language terms Chinese consumers use for burnout and sleep anxiety
- what platform/compliance constraints affect claims and title wording

Exclude:
- US-only Spotify advice
- generic TikTok marketing tips
""",
        markets=["China"],
        locales=["zh-CN"],
        platforms=["Xiaohongshu", "Douyin", "Bilibili", "Ximalaya"],
    )

    package = build_prompt_package(inputs)
    brief = package["brief"]
    decision_text = " ".join(brief["decision_to_make"])

    assert package["recommended_prompt_key"] == "qwen_china"
    assert package["routing"]["provider_id"] == "qwen_china"
    assert "what should it ask so Phoenix Omega" in decision_text
    assert "metadata, consumer-language, and funnel configs" in decision_text
    assert "no Simplified Chinese source plan" in brief["what_is_broken"]

    prompt = package["prompts"]["qwen_china"]
    assert "Prioritize Simplified Chinese sources" in prompt
    assert "Compare China-native evidence against global/English-language assumptions" in prompt
    assert score_prompt_quality(prompt)["score"] == score_prompt_quality(prompt)["max_score"]


def test_japan_brief_routes_to_rakuten_with_japan_native_source_rules() -> None:
    inputs = ResearchPromptInputs(
        prompt_id="platform",
        title="Japan LINE and Rakuten funnel prompt repair",
        issue_description="Japan funnel research mixed US email logic into the LINE lane.",
        transcript="""Failing output:
- no Japanese-language source requirement
- no LINE Official Account / LIFF / rich menu evidence
- no Rakuten Kobo vs Amazon JP vs Audible Japan comparison

Decision:
Should the Japan lane use Rakuten Chat AI / Japan-native deep research
before Phoenix changes config/funnel/line_jp/oa_brand_registry.yaml and
downstream metadata rules?

Missing evidence:
- current LINE OA read/click behavior
- Japanese self-help/audiobook discovery terms
- what not to import from US email funnels

Do not include generic global advice. Surface contradictions and open risks.
""",
        markets=["Japan"],
        locales=["ja-JP"],
        platforms=["LINE", "Rakuten Kobo", "Audible Japan", "Amazon JP"],
    )

    package = build_prompt_package(inputs)
    prompt = package["prompts"]["rakuten_japan"]

    assert package["recommended_prompt_key"] == "rakuten_japan"
    assert package["routing"]["provider_id"] == "rakuten_japan"
    assert "Japanese-language primary sources" in prompt
    assert "Compare Japan-native evidence against imported US/global assumptions" in prompt
    assert "config/funnel/line_jp/oa_brand_registry.yaml" in prompt
    assert score_prompt_quality(prompt)["score"] == score_prompt_quality(prompt)["max_score"]


def test_global_package_emits_all_prompt_variants_and_writes_artifacts(tmp_path: Path) -> None:
    inputs = ResearchPromptInputs(
        prompt_id="semantic_trend",
        title="Global social media pipeline research prompt repair",
        issue_description=(
            "Phoenix Omega needs a global prompt to decide how to build a reusable "
            "book-to-social pipeline across YouTube Shorts, Instagram, TikTok, Pinterest, and email."
        ),
        transcript="""What is broken:
- no decision framework for which platforms get which content shapes
- no evidence-backed cadence or asset-sizing recommendations
- no comparison between educational clips, quote cards, carousel posts, and email reuse

Decision needed:
What should Phoenix Omega automate first: extraction, captions, image
generation, video assembly, scheduling, or analytics feedback?

Unknowns:
- what current platform mechanics matter in 2026
- which formats lead to owned-list capture instead of vanity engagement
- what should be excluded from automation because it needs human review
""",
        markets=["Global"],
        locales=["en-US"],
        platforms=["YouTube Shorts", "Instagram", "TikTok", "Pinterest", "Email"],
        source_preferences=["official platform docs", "credible creator economy reports"],
        exclusions=["single-platform hacks", "generic content marketing advice"],
    )

    package = build_prompt_package(inputs)
    paths = write_prompt_package(package, tmp_path, "global-social-media-pipeline")

    assert package["recommended_prompt_key"] == "gemini"
    assert set(package["prompts"]) == {"master", "gemini", "qwen_china", "rakuten_japan"}
    assert score_prompt_quality(package["prompts"]["gemini"])["score"] == score_prompt_quality(
        package["prompts"]["gemini"]
    )["max_score"]
    assert paths["brief"].exists()
    assert paths["routing"].exists()
    assert paths["prompt_master"].exists()
    assert paths["prompt_gemini"].exists()
    assert paths["prompt_qwen_china"].exists()
    assert paths["prompt_rakuten_japan"].exists()
    assert paths["index"].exists()


def test_explicit_japan_hints_override_noisy_china_transcript_mentions() -> None:
    inputs = ResearchPromptInputs(
        prompt_id="platform",
        title="Japan explicit route with noisy China transcript",
        issue_description="Decide Japan LINE funnel changes for Phoenix Omega.",
        transcript=(
            "The pasted session mentions China, Xiaohongshu, Douyin, Bilibili, "
            "Ximalaya, and Qwen as examples to avoid copying."
        ),
        markets=["Japan"],
        locales=["ja-JP"],
        platforms=["LINE", "Rakuten Kobo"],
    )

    package = build_prompt_package(inputs)

    assert package["recommended_prompt_key"] == "rakuten_japan"
    assert package["routing"]["provider_id"] == "rakuten_japan"
    assert not any(signal.startswith("keywords:china") for signal in package["routing"]["signals"])


def test_explicit_global_hints_override_noisy_regional_mentions() -> None:
    inputs = ResearchPromptInputs(
        prompt_id="semantic_trend",
        title="Global route with noisy regional examples",
        issue_description="Decide a global Phoenix Omega social pipeline implementation.",
        transcript=(
            "Compare previous China Xiaohongshu and Japan LINE notes only as cautionary examples; "
            "this actual research is global and must not route regionally."
        ),
        markets=["Global"],
        locales=["en-US"],
        platforms=["YouTube Shorts", "Instagram", "TikTok"],
    )

    package = build_prompt_package(inputs)

    assert package["recommended_prompt_key"] == "gemini"
    assert package["routing"]["provider_id"] == "gemini_global"
    assert package["routing"]["signals"] == ["locales:en-US", "markets:Global"]


def test_route_signals_do_not_count_locale_alias_substrings() -> None:
    inputs = ResearchPromptInputs(
        prompt_id="pain_points",
        title="China locale alias check",
        issue_description="China route should explain only real structured hints.",
        transcript="Use China-native sources.",
        markets=["China"],
        locales=["zh-CN"],
        platforms=["Xiaohongshu"],
    )

    package = build_prompt_package(inputs)

    assert "locales:zh-CN" in package["routing"]["signals"]
    assert "locales:cn" not in package["routing"]["signals"]


def test_direct_research_execution_requires_prompt_package_or_legacy_ack() -> None:
    with pytest.raises(RuntimeError, match="direct Pearl_Research execution is blocked"):
        require_prompt_package_or_legacy_ack(
            prepare_deep_research_prompt=False,
            allow_legacy_direct_run=False,
        )

    require_prompt_package_or_legacy_ack(
        prepare_deep_research_prompt=True,
        allow_legacy_direct_run=False,
    )
    require_prompt_package_or_legacy_ack(
        prepare_deep_research_prompt=False,
        allow_legacy_direct_run=True,
    )
