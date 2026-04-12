"""Unit tests for pearl_news.pipeline.slot_expansion_engine."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_engine_produces_same_html_as_claude_path() -> None:
    from pearl_news.pipeline.slot_expansion_engine import expand_item_slots

    class _Dummy:
        model_id = "dummy"

        def complete_chat(self, *args, **kwargs):  # noqa: ANN002, ANN003
            return None

    prompts_root = REPO_ROOT / "pearl_news" / "prompts"
    item: dict = {
        "id": "t1",
        "template_id": "hard_news_spiritual_response",
        "language": "en",
        "topic": "climate",
        "primary_sdg": "13",
        "sdg_labels": {"13": "Climate Action"},
        "url": "https://example.com/a",
        "title": "Title",
        "summary": "Summary text for youth.",
        "_teacher_resolved": {
            "display_name": "Test Teacher",
            "tradition": "test tradition",
            "teacher_id": "__no_pack_teacher__",
            "atoms": ["atom one", "atom two", "atom three"],
        },
    }
    expand_item_slots(
        item,
        backend=_Dummy(),
        config={"max_tokens": 500},
        prompts_root=prompts_root,
        repo_root=REPO_ROOT,
        language="en",
        max_retries=0,
        simulate=True,
        provider_cfg={},
    )
    c = item["content"]
    assert "<h1>" in c
    assert "Source:" in c
    assert "<p>" in c
    assert item.get("_expansion_engine") == "slot_expansion"
    assert item.get("_v52_slots")


def test_engine_loads_locale_prompt_over_english(tmp_path: Path) -> None:
    from pearl_news.pipeline.slot_expansion_engine import load_slot_prompt

    root = tmp_path / "prompts"
    ja = root / "slot_by_slot" / "hard_news_spiritual_response" / "locales" / "ja"
    ja.mkdir(parents=True)
    (ja / "news_peg.txt").write_text("JA_PROMPT_UNIQUE", encoding="utf-8")
    (root / "slot_by_slot" / "hard_news_spiritual_response" / "news_peg.txt").write_text(
        "EN_PROMPT", encoding="utf-8"
    )
    assert load_slot_prompt(root, "hard_news_spiritual_response", "news_peg", "ja") == "JA_PROMPT_UNIQUE"


def test_engine_falls_back_to_english_prompt(tmp_path: Path) -> None:
    from pearl_news.pipeline.slot_expansion_engine import load_slot_prompt

    root = tmp_path / "prompts"
    p = root / "slot_by_slot" / "hard_news_spiritual_response" / "news_peg.txt"
    p.parent.mkdir(parents=True)
    p.write_text("EN_ONLY", encoding="utf-8")
    assert load_slot_prompt(root, "hard_news_spiritual_response", "news_peg", "ja") == "EN_ONLY"


def test_deterministic_pack_with_locale_overlay(tmp_path: Path) -> None:
    from pearl_news.pipeline.deterministic_teacher_topic import load_teacher_topic_pack

    packs = tmp_path / "pearl_news" / "teacher_topic_packs"
    base = packs / "teachers" / "t1" / "climate.yaml"
    base.parent.mkdir(parents=True)
    base.write_text("active: true\nhook_personal:\n  options: []\n", encoding="utf-8")
    loc = packs / "locales" / "ja" / "teachers" / "t1" / "climate.yaml"
    loc.parent.mkdir(parents=True)
    loc.write_text("overlay_line: ja-value\n", encoding="utf-8")
    merged = load_teacher_topic_pack(tmp_path, "t1", "climate", language="ja")
    assert merged is not None
    assert merged.get("overlay_line") == "ja-value"
    assert merged.get("active") is True


def test_deterministic_pack_without_overlay_returns_english(tmp_path: Path) -> None:
    from pearl_news.pipeline.deterministic_teacher_topic import load_teacher_topic_pack

    packs = tmp_path / "pearl_news" / "teacher_topic_packs"
    base = packs / "teachers" / "t1" / "climate.yaml"
    base.parent.mkdir(parents=True)
    base.write_text("active: true\nx: 1\n", encoding="utf-8")
    merged = load_teacher_topic_pack(tmp_path, "t1", "climate", language="ja")
    assert merged is not None
    assert merged.get("x") == 1


def test_locale_overlay_merges_options_by_id(tmp_path: Path) -> None:
    from pearl_news.pipeline.deterministic_teacher_topic import load_teacher_topic_pack

    packs = tmp_path / "pearl_news" / "teacher_topic_packs"
    base = packs / "teachers" / "t1" / "climate.yaml"
    base.parent.mkdir(parents=True)
    base.write_text(
        "active: true\n"
        "hook_personal:\n"
        "  options:\n"
        "  - id: a1\n"
        "    line: English one\n"
        "    meta: keep\n"
        "  - id: a2\n"
        "    line: English two\n",
        encoding="utf-8",
    )
    loc = packs / "locales" / "ja" / "teachers" / "t1" / "climate.yaml"
    loc.parent.mkdir(parents=True)
    loc.write_text(
        "hook_personal:\n"
        "  options:\n"
        "  - id: a1\n"
        "    line: 日本語\n",
        encoding="utf-8",
    )
    merged = load_teacher_topic_pack(tmp_path, "t1", "climate", language="ja")
    assert merged is not None
    opts = (merged.get("hook_personal") or {}).get("options") or []
    by_id = {o["id"]: o for o in opts if isinstance(o, dict) and "id" in o}
    assert by_id["a1"]["line"] == "日本語"
    assert by_id["a1"]["meta"] == "keep"
    assert by_id["a2"]["line"] == "English two"


def test_resolve_expansion_system_prompt_ja_zh_from_cjk_provider(tmp_path: Path) -> None:
    from pearl_news.pipeline.slot_expansion_engine import resolve_expansion_system_prompt

    root = tmp_path / "prompts"
    root.mkdir(parents=True)
    (root / "expansion_system_cjk.txt").write_text("GENERIC_CJK", encoding="utf-8")
    (root / "expansion_system_ja.txt").write_text("JA_SPECIAL", encoding="utf-8")
    (root / "expansion_system_zh_cn.txt").write_text("ZH_SPECIAL", encoding="utf-8")

    prov = {"system_prompt": "expansion_system_cjk.txt"}
    assert (
        resolve_expansion_system_prompt(root, language="ja", provider_cfg=prov, config={}).strip()
        == "JA_SPECIAL"
    )
    assert (
        resolve_expansion_system_prompt(root, language="zh-cn", provider_cfg=prov, config={}).strip()
        == "ZH_SPECIAL"
    )
    assert (
        resolve_expansion_system_prompt(root, language="zh-tw", provider_cfg=prov, config={}).strip()
        == "ZH_SPECIAL"
    )
    assert (
        resolve_expansion_system_prompt(root, language="ko", provider_cfg=prov, config={}).strip()
        == "GENERIC_CJK"
    )


@pytest.mark.skipif(
    not __import__("importlib").util.find_spec("openai"),
    reason="openai package not installed",
)
def test_openai_backend_strips_fences() -> None:
    from pearl_news.pipeline.slot_expansion_engine import OpenAICompatibleBackend

    backend = OpenAICompatibleBackend(
        {
            "base_url": "http://localhost:1/v1",
            "api_key": "x",
            "model": "qwen2.5:14b",
            "timeout": 5,
            "disable_thinking": True,
        }
    )
    fake_msg = MagicMock()
    fake_msg.content = "```html\n<p>Hello</p>\n```"
    fake_choice = MagicMock()
    fake_choice.message = fake_msg
    fake_resp = MagicMock()
    fake_resp.choices = [fake_choice]

    with patch("openai.OpenAI") as m_client:
        inst = m_client.return_value
        inst.chat.completions.create.return_value = fake_resp
        out = backend.complete_chat("sys", "user", max_tokens=100, temperature=0.5)
    assert out == "<p>Hello</p>"


def test_cjk_source_line_localization() -> None:
    from pearl_news.pipeline.slot_expansion_engine import localize_source_line_html

    html = '<p><em>Source: <a href="https://u.test">https://u.test</a></em></p>'
    assert "出典" in localize_source_line_html(html, "ja")
    assert "来源" in localize_source_line_html(html, "zh-cn")
    assert "Source:" in localize_source_line_html(html, "en")


def test_thin_output_retry() -> None:
    from pearl_news.pipeline.slot_expansion_engine import expand_item_slots

    long_html = (
        "<h1>Youth Climate Action and City Schools</h1>\n\n"
        + "\n\n".join(
            f"<p>Paragraph {i} with 67% students and SDG 13 climate action detail.</p>" for i in range(12)
        )
        + '\n\n<p><em>Source: <a href="https://example.com">https://example.com</a></em></p>'
    )

    class _Counting:
        model_id = "c"
        calls = 0

        def complete_chat(self, system, user, **kwargs):  # noqa: ANN002, ANN003
            _Counting.calls += 1
            if isinstance(user, str) and "too short" in user:
                return long_html
            return "Brief."

    prompts_root = REPO_ROOT / "pearl_news" / "prompts"
    item: dict = {
        "id": "thin1",
        "template_id": "hard_news_spiritual_response",
        "language": "en",
        "topic": "climate",
        "primary_sdg": "13",
        "sdg_labels": {"13": "Climate Action"},
        "url": "https://example.com",
        "title": "T",
        "summary": "S",
        "_teacher_resolved": {
            "display_name": "Teacher",
            "tradition": "tradition",
            "teacher_id": "__no_pack_teacher__",
            "atoms": ["a", "b", "c"],
        },
    }
    _Counting.calls = 0
    expand_item_slots(
        item,
        backend=_Counting(),
        config={"max_tokens": 500},
        prompts_root=prompts_root,
        repo_root=REPO_ROOT,
        language="en",
        max_retries=0,
        simulate=False,
        provider_cfg={"min_output_chars": {"en": 8000, "default": 8000}, "thin_output_retry": True},
    )
    assert _Counting.calls >= 15
    assert "SDG" in item["content"] or "sdg" in item["content"].lower()
