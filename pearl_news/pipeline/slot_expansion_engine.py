"""
Shared slot-by-slot expansion engine for Pearl News (Claude + OpenAI-compatible / Qwen).

Single code path for HTML assembly, deterministic packs, slot prompts, and metadata.
"""
from __future__ import annotations

import logging
import os
import re
import time
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

try:
    import yaml
except ImportError:
    yaml = None

from pearl_news.pipeline.deterministic_teacher_topic import (
    build_commentary_deterministic_plan,
    build_explainer_deterministic_plan,
    build_hard_news_deterministic_plan,
    build_interfaith_deterministic_plan,
    build_unsay_deterministic_plan,
    build_youth_feature_deterministic_plan,
)
from pearl_news.pipeline.slot_expansion_constants import (
    OPTIONAL_V52_SLOTS,
    TEMPLATE_SLOTS,
    TEMPLATE_SLOTS_V52,
    V52_SLOT_MAP,
)

logger = logging.getLogger(__name__)


@runtime_checkable
class CompletionBackend(Protocol):
    def complete_chat(
        self,
        system: str,
        user: str,
        *,
        max_tokens: int = 2000,
        temperature: float = 0.6,
    ) -> str | None: ...


def _strip_fences(text: str) -> str:
    raw = (text or "").strip()
    if not raw.startswith("```"):
        return raw
    lines = raw.split("\n")
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()


def load_slot_prompt(
    prompts_root: Path,
    template_id: str,
    slot_name: str,
    language: str = "en",
) -> str | None:
    """Try locale file first, then English default."""
    lang = (language or "en").strip().lower()
    if lang and lang not in ("en", ""):
        locale_path = (
            prompts_root
            / "slot_by_slot"
            / template_id
            / "locales"
            / lang
            / f"{slot_name}.txt"
        )
        if locale_path.exists():
            return locale_path.read_text(encoding="utf-8").strip()
    default_path = prompts_root / "slot_by_slot" / template_id / f"{slot_name}.txt"
    if default_path.exists():
        return default_path.read_text(encoding="utf-8").strip()
    return None


def _load_legacy_docs_system_prompt(prompts_root: Path) -> str:
    docs_path = prompts_root.parent.parent / "docs" / "pearl_news_prompts" / "00_SYSTEM_PROMPT.md"
    if docs_path.exists():
        return docs_path.read_text(encoding="utf-8").strip()
    path = prompts_root / "expansion_system.txt"
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return (
        "You are an editor for Pearl News. Write publish-grade journalism for Gen Z readers. "
        "Output only the requested content, no preamble or explanation."
    )


def resolve_expansion_system_prompt(
    prompts_root: Path,
    *,
    language: str,
    provider_cfg: dict[str, Any],
    config: dict[str, Any],
) -> str:
    prov = provider_cfg or {}
    sp_rel = (prov.get("system_prompt") or "").strip()
    lang = (language or "en").lower()
    if sp_rel:
        rel_clean = sp_rel.lstrip("/")
        if rel_clean.startswith("prompts/"):
            rel_clean = rel_clean[len("prompts/") :]
        base_name = Path(rel_clean).name
        # Shared CJK file: specialize register per language (ja / Chinese locales).
        if base_name == "expansion_system_cjk.txt":
            if lang == "ja" or lang.startswith("ja-"):
                ja_path = prompts_root / "expansion_system_ja.txt"
                if ja_path.exists():
                    return ja_path.read_text(encoding="utf-8").strip()
            if lang.startswith("zh"):
                zh_path = prompts_root / "expansion_system_zh_cn.txt"
                if zh_path.exists():
                    return zh_path.read_text(encoding="utf-8").strip()
        sp_path = prompts_root / rel_clean
        if sp_path.exists():
            return sp_path.read_text(encoding="utf-8").strip()
    if lang in ("en", ""):
        enp = prompts_root / "expansion_system_en.txt"
        if enp.exists():
            return enp.read_text(encoding="utf-8").strip()
    cjkp = prompts_root / "expansion_system_cjk.txt"
    if cjkp.exists():
        return cjkp.read_text(encoding="utf-8").strip()
    return _load_legacy_docs_system_prompt(prompts_root)


def localize_source_line_html(html: str, language: str) -> str:
    """After assembly, localize Source label for CJK (validator accepts 出典/来源)."""
    lang = (language or "en").lower()
    if lang.startswith("ja"):
        return html.replace("Source:", "出典:").replace("source:", "出典:")
    if lang.startswith("zh"):
        return html.replace("Source:", "来源:").replace("source:", "来源:")
    return html


def _load_anthropic_api_key() -> str:
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if key:
        return key
    repo_root = Path(__file__).resolve().parents[2]
    rtf_path = repo_root / "claude_api_key.rtf"
    if rtf_path.exists():
        raw = rtf_path.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"sk-ant-[a-zA-Z0-9_-]{20,}", raw)
        if m:
            return m.group(0)
    return ""


class AnthropicBackend:
    """Anthropic Messages API — same retry/timeout behavior as legacy _call_claude."""

    def __init__(self, provider_cfg: dict[str, Any], *, config: dict[str, Any] | None = None) -> None:
        self._prov = provider_cfg or {}
        self._config = config or {}
        api_key_env = (self._prov.get("api_key_env") or "ANTHROPIC_API_KEY").strip()
        self._api_key = os.environ.get(api_key_env, "").strip() or _load_anthropic_api_key()
        model_env = (self._prov.get("model_env") or "CLAUDE_MODEL").strip()
        self._model = (
            os.environ.get(model_env, "").strip()
            or self._prov.get("model")
            or self._config.get("claude_model")
            or os.environ.get("CLAUDE_MODEL", "").strip()
            or "claude-sonnet-4-20250514"
        )
        self._timeout = float(self._prov.get("timeout") or self._config.get("timeout") or 90.0)

    @property
    def model_id(self) -> str:
        return self._model

    def has_api_key(self) -> bool:
        return bool(self._api_key)

    def complete_chat(
        self,
        system: str,
        user: str,
        *,
        max_tokens: int = 2000,
        temperature: float = 0.6,
    ) -> str | None:
        if not self._api_key:
            return None
        try:
            from anthropic import Anthropic
        except ImportError:
            logger.error("anthropic package not installed: pip install anthropic")
            return None

        client = Anthropic(api_key=self._api_key, timeout=self._timeout, max_retries=1)
        t0 = time.monotonic()
        for attempt in range(2):
            try:
                response = client.messages.create(
                    model=self._model,
                    max_tokens=max_tokens,
                    system=system,
                    messages=[{"role": "user", "content": user}],
                    temperature=temperature,
                    timeout=self._timeout,
                )
                text = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        text += block.text
                out = text.strip() if text.strip() else None
                logger.info(
                    "AnthropicBackend complete_chat model=%s duration_s=%.2f ok=%s",
                    self._model,
                    time.monotonic() - t0,
                    bool(out),
                )
                return out
            except Exception as e:
                message = str(e)
                if "rate_limit_error" in message or "429" in message:
                    if attempt == 0:
                        logger.warning("Claude API rate-limited; sleeping 65s before retry")
                        time.sleep(65)
                        continue
                logger.warning("Claude API call failed: %s", e)
                logger.info(
                    "AnthropicBackend complete_chat model=%s duration_s=%.2f ok=False",
                    self._model,
                    time.monotonic() - t0,
                )
                return None
        return None


class OpenAICompatibleBackend:
    """Together / DashScope / Ollama / LM Studio via OpenAI-compatible chat completions."""

    def __init__(self, merged_cfg: dict[str, Any]) -> None:
        self._cfg = dict(merged_cfg)
        self._base_url = (self._cfg.get("base_url") or "").strip()
        self._api_key = (self._cfg.get("api_key") or "lm-studio").strip()
        self._model = (self._cfg.get("model") or "qwen3-14b").strip()
        self._timeout = float(self._cfg.get("timeout") or 360)
        self._disable_thinking = self._cfg.get("disable_thinking", True)
        from pearl_news.pipeline.cjk_qwen_model import PEARL_STAR_CJK_MODEL, is_ollama_openai_base_url

        # Allow providers to pin a specific Ollama model (e.g. gemma_slots → gemma2:9b)
        # by setting disable_model_override: true in their provider config.
        if is_ollama_openai_base_url(self._base_url) and not self._cfg.get("disable_model_override"):
            self._model = PEARL_STAR_CJK_MODEL

    @property
    def model_id(self) -> str:
        return self._model

    def has_api_key(self) -> bool:
        return bool(self._base_url)

    def complete_chat(
        self,
        system: str,
        user: str,
        *,
        max_tokens: int = 2000,
        temperature: float = 0.6,
    ) -> str | None:
        if not self._base_url:
            logger.warning("OpenAICompatibleBackend: base_url not set")
            return None
        try:
            from openai import OpenAI
        except ImportError:
            logger.warning("openai package not installed; pip install openai")
            return None
        try:
            from httpx import Timeout as HttpxTimeout

            http_timeout = HttpxTimeout(self._timeout)
        except ImportError:
            http_timeout = self._timeout

        client = OpenAI(base_url=self._base_url, api_key=self._api_key, timeout=http_timeout)
        extra_body: dict[str, Any] = {}
        # enable_thinking=False is a DashScope/Qwen-specific param — do NOT send to Groq/xAI/Together
        _is_dashscope = "dashscope" in self._base_url or "aliyuncs" in self._base_url
        if self._disable_thinking and _is_dashscope:
            extra_body["enable_thinking"] = False
        t0 = time.monotonic()
        try:
            resp = client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                **({"extra_body": extra_body} if extra_body else {}),
            )
            choice = resp.choices[0] if resp.choices else None
            if not choice or not getattr(choice, "message", None):
                logger.info(
                    "OpenAICompatibleBackend model=%s duration_s=%.2f ok=False (no choice)",
                    self._model,
                    time.monotonic() - t0,
                )
                return None
            raw = _strip_fences((choice.message.content or "").strip())
            ok = bool(raw)
            logger.info(
                "OpenAICompatibleBackend model=%s duration_s=%.2f ok=%s",
                self._model,
                time.monotonic() - t0,
                ok,
            )
            return raw if ok else None
        except Exception as e:
            logger.warning("OpenAICompatibleBackend call failed: %s", e)
            logger.info(
                "OpenAICompatibleBackend model=%s duration_s=%.2f ok=False",
                self._model,
                time.monotonic() - t0,
            )
            return None


class _SafeDict(dict):
    def __missing__(self, key: str) -> str:
        return ""


def _render_prompt(template: str, context: dict[str, Any]) -> str:
    return template.format_map(_SafeDict({k: ("" if v is None else str(v)) for k, v in context.items()}))


_SLOT_FORMAT_PREFIXES: dict[str, tuple[str, ...]] = {
    "hook_personal": ("HEADER:", "HOOK:"),
    "hook_big_picture": ("HEADER:", "BIG_PICTURE:"),
    "news_peg": ("HEADER:", "PEG:"),
    "teacher_perspective": ("HEADER:",),
    "youth_somatic": ("HEADER:",),
    "teacher_witness": ("HEADER:",),
}


def _clean_slot_output(slot: str, text: str) -> str:
    cleaned = (text or "").strip()
    if not cleaned:
        return ""
    if cleaned.upper() == "READY":
        return ""

    prefixes = _SLOT_FORMAT_PREFIXES.get(slot)
    if not prefixes:
        return cleaned

    kept: list[str] = []
    for raw_line in cleaned.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if any(line.upper().startswith(prefix) for prefix in prefixes):
            for prefix in prefixes:
                if line.upper().startswith(prefix):
                    remainder = line[len(prefix) :].strip()
                    if prefix != "HEADER:" and remainder:
                        kept.append(remainder)
                    break
            continue
        kept.append(line)
    return "\n\n".join(part for part in kept if part).strip()


def _short_text(value: str | None, *, max_chars: int) -> str:
    text = (value or "").strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0].strip().rstrip(" ,.;:") + "..."


def _teacher_quotes_text(teacher: dict[str, Any] | None, *, max_items: int = 2, max_chars: int = 320) -> str:
    atoms = ((teacher or {}).get("atoms") or [])[:max_items]
    if not atoms:
        return "No teacher atom bundle available."
    return "\n".join(f"- {_short_text(str(atom), max_chars=max_chars)}" for atom in atoms)


def _teacher_framework_text(teacher: dict[str, Any] | None) -> str:
    if not teacher:
        return ""
    attribution = (teacher.get("attribution") or "").strip()
    if attribution:
        return attribution
    atoms = teacher.get("atoms") or []
    if atoms:
        return str(atoms[0]).strip()
    tradition = (teacher.get("tradition") or "").strip()
    if tradition:
        return f"{tradition} framework for naming, diagnosing, and responding to youth distress."
    return ""


def _extract_turnaround_stats(text: str) -> tuple[str, str]:
    numbers = re.findall(r"\b\d[\d,%.]*\b", text or "")
    if len(numbers) >= 2:
        return numbers[0], numbers[1]
    if len(numbers) == 1:
        return numbers[0], ""
    return "", ""


def _extract_reader_loop_sentence(text: str) -> str:
    for line in (text or "").splitlines():
        stripped = line.strip()
        if stripped.upper().startswith("LOOP_SEQUENCE:"):
            return stripped.split(":", 1)[1].strip().strip('"')
    return _short_text(text, max_chars=180)


def _teacher_prompt_meta(repo_root: Path, teacher: dict[str, Any] | None) -> dict[str, str]:
    teacher = teacher or {}
    teacher_id = str(teacher.get("teacher_id") or "").strip()
    role = "teacher"
    years = ""
    tradition_age = ""

    if not teacher_id or yaml is None:
        return {
            "teacher_role": role,
            "teacher_years": years,
            "tradition_age": tradition_age,
        }

    doctrine_path = repo_root / "SOURCE_OF_TRUTH" / "teacher_banks" / teacher_id / "doctrine" / "doctrine.yaml"
    if not doctrine_path.exists():
        return {
            "teacher_role": role,
            "teacher_years": years,
            "tradition_age": tradition_age,
        }

    try:
        doctrine = yaml.safe_load(doctrine_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {
            "teacher_role": role,
            "teacher_years": years,
            "tradition_age": tradition_age,
        }

    role_text = str(doctrine.get("role_definition") or "").strip()
    if role_text:
        role = _short_text(role_text, max_chars=80)

    text_pool = "\n".join(
        [
            role_text,
            "\n".join(str(x) for x in (doctrine.get("verified_ground") or [])),
        ]
    )
    years_match = re.search(r"\b(\d{1,3})\s+years?\b", text_pool, re.IGNORECASE)
    if years_match:
        years = years_match.group(1)
    age_match = re.search(
        r"\b(\d{1,4}(?:,\d{3})?)\s+years?\b", str(doctrine.get("tradition") or ""), re.IGNORECASE
    )
    if age_match:
        tradition_age = age_match.group(1)

    return {
        "teacher_role": role,
        "teacher_years": years,
        "tradition_age": tradition_age,
    }


def _slot_token_budget(slot: str) -> int:
    budgets = {
        "headline": 80,
        "news_summary": 300,
        "youth_impact": 350,
        "teacher_perspective": 600,
        "sdg_un_tie": 200,
        "forward_look": 250,
        "thesis": 300,
        "teaching_interpretation": 600,
        "civic_recommendation": 300,
        "sdg_reference": 200,
        "event_summary": 300,
        "leaders_present": 250,
        "themes_discussed": 500,
        "youth_commitments": 300,
        "sdg_alignment": 200,
        "next_steps": 250,
        "what_happened": 300,
        "historical_background": 350,
        "ethical_spiritual_dimension": 600,
        "youth_implications": 350,
        "sdg_policy_tie": 250,
        "future_outlook": 300,
        "youth_narrative": 350,
        "data_research": 350,
        "teacher_reflection": 500,
        "sdg_framework": 200,
        "solutions": 350,
        "headline_layer_1": 60,
        "headline_layer_2": 40,
        "hook_personal": 150,
        "hook_big_picture": 150,
        "news_peg": 200,
        "teacher_intro": 150,
        "youth_somatic": 200,
        "teacher_witness": 200,
        "body_data": 250,
        "turnaround": 200,
        "bridge": 150,
        "practice_announce": 200,
        "convergence": 200,
        "distinction": 200,
    }
    return budgets.get(slot, 400)


def _to_html_paragraph(text: str) -> str:
    t = text.strip()
    if not t:
        return ""
    if t.startswith("<"):
        return t
    return f"<p>{t}</p>"


def _simulate_slot(slot: str, ctx: dict[str, Any]) -> str:
    topic = ctx.get("topic", "global affairs")
    teacher_name = ctx.get("teacher_name", "Maat")
    teacher_tradition = ctx.get("teacher_tradition", "interfaith")
    sdg_number = ctx.get("sdg_number", "17")
    sdg_name = ctx.get("sdg_name", "Partnerships for the Goals")

    simulated = {
        "headline": f"Youth Voices Rise as {topic.replace('_', ' ').title()} Reshapes Global Priorities",
        "news_summary": (
            f"A new development in {topic.replace('_', ' ')} is drawing attention from policymakers worldwide. "
            f"The issue highlights systemic challenges that disproportionately affect young people aged 15-24."
        ),
        "youth_impact": (
            f"In New York City, 67% of surveyed high school students reported that {topic.replace('_', ' ')} "
            f"affects their daily routines, according to a 2024 district wellness survey."
        ),
        "teacher_perspective": (
            f"{teacher_name} teaches that awareness must precede action.\n\n"
            f"In practice, {teacher_name} recommends a three-step reflection exercise.\n\n"
            f"\"The work is not to fix everything,\" {teacher_name} emphasizes."
        ),
        "sdg_un_tie": (
            f"This story relates to SDG {sdg_number}: {sdg_name}. "
            f"Pearl News is an independent nonprofit and is not affiliated with the United Nations."
        ),
        "forward_look": (
            f"City education offices are expected to release updated program data within the coming quarter. "
            f"Pearl News will track those scheduled updates."
        ),
        "thesis": f"The intersection of {topic.replace('_', ' ')} and youth agency demands a clear framework.",
        "teaching_interpretation": f"{teacher_name} offers a lens for understanding structural challenges.",
        "civic_recommendation": f"Local school boards should integrate {topic.replace('_', ' ')} literacy into curricula.",
        "sdg_reference": f"SDG {sdg_number} ({sdg_name}). Pearl News is not affiliated with the United Nations.",
        "event_summary": f"Leaders addressed {topic.replace('_', ' ')} with commitments to youth programming.",
        "leaders_present": "Representatives from Buddhist, Christian, Islamic, and Hindu traditions joined educators.",
        "themes_discussed": f"Participants identified youth mental health support and literacy in schools.",
        "youth_commitments": "Youth delegates pledged peer mentorship programs in 12 cities by year-end.",
        "sdg_alignment": f"The commitments align with SDG {sdg_number}: {sdg_name}.",
        "next_steps": "The steering committee will reconvene in 90 days to assess progress.",
        "what_happened": f"A significant development in {topic.replace('_', ' ')} has prompted international responses.",
        "historical_background": f"This issue has roots in policy shifts dating to the early 2010s.",
        "ethical_spiritual_dimension": f"{teacher_name} frames this through the lens of interconnection.",
        "youth_implications": f"For students aged 15-24, practical effects include changes to school programming.",
        "sdg_policy_tie": f"SDG {sdg_number} ({sdg_name}) frames the policy dimension.",
        "future_outlook": f"The next 12 months will be critical as new program data becomes available.",
        "youth_narrative": f"Maya, 16, started a peer education group at her high school.",
        "data_research": f"Research shows youth-led initiatives have higher engagement rates.",
        "teacher_reflection": f"{teacher_name} sees in these youth efforts a living example of contemplative education.",
        "sdg_framework": f"SDG {sdg_number}: {sdg_name}. Pearl News is not affiliated with the United Nations.",
        "solutions": f"Three models are showing measurable results: peer mentorship networks.",
        "headline_layer_1": f"{topic.replace('_', ' ').title()} Is Reshaping Youth Life",
        "headline_layer_2": f"{teacher_name} reads the same shift through a civic-spiritual lens.",
        "hook_personal": "You read the update. You keep functioning. A quieter part of you knows the cost is rising.",
        "hook_big_picture": "A new global data point confirms what many young people already tracked in their own routines.",
        "news_peg": f"New reporting on {topic.replace('_', ' ')} is forcing institutions to name what young people carry.",
        "teacher_intro": f"{teacher_name}, a {teacher_tradition} teacher, has seen in practice spaces what this does.",
        "youth_somatic": 'You read the number. Your throat tightened.\nLOOP_SEQUENCE: "read the number. throat tightened."',
        "teacher_witness": f"{teacher_name} has seen this exact loop in young people this year.",
        "body_data": "The scale is public now, but the consequence still lands one person at a time.",
        "turnaround": "Young people are already building responses.\n\n184 initiatives. 23 countries.",
        "bridge": f"184 initiatives. 23 countries. {teacher_name}'s tradition has been developing capacity for generations.",
        "practice_announce": "The practice in the sidebar is designed for this exact pressure.",
        "convergence": "Both traditions emphasized listening before naming the shared wound.",
        "distinction": "They diverged on the primary lever: inner practice versus institutional reform.",
    }
    return simulated.get(slot, f"[Simulated content for {slot}]")


def _plain_text_len(html: str) -> int:
    text = re.sub(r"<[^>]+>", " ", html or "")
    return len(re.sub(r"\s+", " ", text).strip())


def _min_output_floor(language: str, config: dict[str, Any], provider_cfg: dict[str, Any]) -> int:
    floors = provider_cfg.get("min_output_chars") or config.get("min_output_chars") or {}
    if isinstance(floors, dict):
        lang = (language or "en").lower()
        return int(floors.get(lang) or floors.get("default") or floors.get("en") or 1200)
    return int(floors) if floors else 1200


def expand_item_slots(
    item: dict[str, Any],
    *,
    backend: CompletionBackend,
    config: dict[str, Any],
    prompts_root: Path,
    repo_root: Path,
    language: str = "en",
    max_retries: int = 1,
    simulate: bool = False,
    provider_cfg: dict[str, Any] | None = None,
    expansion_provider_label: str | None = None,
) -> dict[str, Any]:
    """
    Fill v5.2 slots, merge HTML, set _v52_slots and expansion metadata.
    Mutates item in place; returns the item for convenience.
    """
    prov = provider_cfg or {}
    lang = str(language or item.get("language") or "en").lower()
    article_id = item.get("id", "?")
    template_id = item.get("_v52_template_id") or item.get("template_id") or "hard_news_spiritual_response"
    slots_list = list(
        TEMPLATE_SLOTS_V52.get(template_id)
        or TEMPLATE_SLOTS.get(template_id, TEMPLATE_SLOTS["hard_news_spiritual_response"])
    )
    optional_slots = tuple(OPTIONAL_V52_SLOTS.get(template_id, ()))
    is_v52_template = template_id in TEMPLATE_SLOTS_V52

    api_key_ok = True
    if isinstance(backend, AnthropicBackend) and not simulate:
        api_key_ok = backend.has_api_key()
    elif isinstance(backend, OpenAICompatibleBackend) and not simulate:
        api_key_ok = backend.has_api_key()

    if not api_key_ok:
        logger.error("No API key for slot expansion (article %s)", article_id)
        item["_expansion_failed"] = True
        item["_expansion_error"] = "no_api_key"
        return item

    system_prompt = resolve_expansion_system_prompt(prompts_root, language=lang, provider_cfg=prov, config=config)
    temperature = float(
        prov.get("temperature") if prov.get("temperature") is not None else config.get("temperature") or 0.5
    )

    teacher = item.get("_teacher_resolved") or {}
    teacher_name = teacher.get("display_name") or "Forum Participant"
    teacher_tradition = teacher.get("tradition") or "interfaith"
    teacher_meta = _teacher_prompt_meta(repo_root, teacher)
    deterministic_plan = None
    if template_id == "hard_news_spiritual_response":
        deterministic_plan = build_hard_news_deterministic_plan(item, repo_root, language=lang)
    elif template_id == "commentary":
        deterministic_plan = build_commentary_deterministic_plan(item, repo_root, language=lang)
    elif template_id == "explainer_context":
        deterministic_plan = build_explainer_deterministic_plan(item, repo_root, language=lang)
    elif template_id == "interfaith_dialogue_report":
        deterministic_plan = build_interfaith_deterministic_plan(item, repo_root)
    elif template_id == "youth_feature":
        deterministic_plan = build_youth_feature_deterministic_plan(item, repo_root, language=lang)
    elif template_id == "unsay_dialogue":
        deterministic_plan = build_unsay_deterministic_plan(item, repo_root)
    if deterministic_plan:
        item["_deterministic_teacher_topic_pack"] = deterministic_plan.get("pack_path")
        item["_deterministic_beat_map"] = deterministic_plan.get("beat_map_id")
        item["_deterministic_article_plan"] = deterministic_plan.get("ordered_sections")

    ctx: dict[str, Any] = {
        "news_event": (
            f"Title: {_short_text(item.get('raw_title') or item.get('title') or '', max_chars=150)}\n"
            f"Summary: {_short_text(item.get('raw_summary') or item.get('summary') or '', max_chars=300)}\n"
            f"URL: {item.get('url')}\nDate: {item.get('pub_date')}"
        ),
        "news_event_topic": item.get("topic") or "global affairs",
        "topic": item.get("topic") or "global affairs",
        "youth_impact_summary": _short_text(item.get("summary") or item.get("raw_summary") or "", max_chars=200),
        "youth_impact": _short_text(item.get("summary") or item.get("raw_summary") or "", max_chars=250),
        "teacher_name": teacher_name,
        "teacher_tradition": teacher_tradition,
        "teacher_framework": _teacher_framework_text(teacher),
        "teacher_quotes_practices": _teacher_quotes_text(teacher),
        "teacher_role": teacher_meta["teacher_role"],
        "teacher_years": teacher_meta["teacher_years"],
        "tradition_age": teacher_meta["tradition_age"],
        "sdg_number": item.get("primary_sdg") or "17",
        "sdg_name": (item.get("sdg_labels") or {}).get(
            item.get("primary_sdg", "17"), "Partnerships for the Goals"
        ),
        "sdg_target": "",
        "un_agency_name": item.get("un_body") or "United Nations",
        "locale": lang,
        "news_topic": item.get("topic") or "global affairs",
        "gen_z_impact": _short_text(item.get("summary") or item.get("raw_summary") or "", max_chars=160),
        "reader_loop_sentence": "",
        "turnaround_stat_1": "",
        "turnaround_stat_2": "",
    }

    values: dict[str, str] = {}
    all_ok = True
    t0 = time.monotonic()

    if deterministic_plan:
        for slot, value in (deterministic_plan.get("slots") or {}).items():
            if value:
                values[slot] = value
                ctx[slot] = value
                if slot == "youth_somatic":
                    ctx["reader_loop_sentence"] = _extract_reader_loop_sentence(value)
                elif slot == "turnaround":
                    stat_1, stat_2 = _extract_turnaround_stats(value)
                    ctx["turnaround_stat_1"] = stat_1
                    ctx["turnaround_stat_2"] = stat_2

    def _fill_slot(slot: str) -> None:
        nonlocal all_ok
        if values.get(slot):
            return
        out = None
        if simulate:
            out = _simulate_slot(slot, ctx)
        else:
            slot_template = load_slot_prompt(prompts_root, template_id, slot, lang)
            if not slot_template:
                logger.warning("No prompt template for %s/%s — skipping", template_id, slot)
                values[slot] = ""
                return
            prompt = _render_prompt(slot_template, {**ctx, **values})
            slot_max = min(_slot_token_budget(slot), int(prov.get("max_tokens") or config.get("max_tokens") or 4096))
            attempts = max(0, int(max_retries)) + 1
            for _ in range(attempts):
                out = backend.complete_chat(
                    system_prompt,
                    prompt,
                    max_tokens=slot_max,
                    temperature=temperature,
                )
                if out:
                    break
        if out:
            out = _clean_slot_output(slot, out)
        if out:
            values[slot] = out
            ctx[slot] = out
            if slot == "youth_somatic":
                ctx["reader_loop_sentence"] = _extract_reader_loop_sentence(out)
            elif slot == "turnaround":
                stat_1, stat_2 = _extract_turnaround_stats(out)
                ctx["turnaround_stat_1"] = stat_1
                ctx["turnaround_stat_2"] = stat_2
            logger.debug("  slot %s: %d chars", slot, len(out))
        else:
            logger.warning("  slot %s: FAILED for article %s", slot, article_id)
            values[slot] = ""
            all_ok = False

    for slot in slots_list:
        _fill_slot(slot)

    elapsed = time.monotonic() - t0

    if not all_ok or not values.get(slots_list[0]):
        item["_expansion_failed"] = True
        item["_expansion_error"] = "slot_generation_incomplete"
        logger.warning("Article %s: expansion incomplete (%.1fs)", article_id, elapsed)
        return item

    for slot in optional_slots:
        if simulate:
            out = _simulate_slot(slot, ctx)
            if out:
                out = _clean_slot_output(slot, out)
            if out:
                values[slot] = out
                ctx[slot] = out
        else:
            slot_template = load_slot_prompt(prompts_root, template_id, slot, lang)
            if not slot_template:
                continue
            prompt = _render_prompt(slot_template, {**ctx, **values})
            slot_max = min(_slot_token_budget(slot), int(prov.get("max_tokens") or config.get("max_tokens") or 4096))
            attempts = max(0, int(max_retries)) + 1
            out = None
            for _ in range(attempts):
                out = backend.complete_chat(
                    system_prompt,
                    prompt,
                    max_tokens=slot_max,
                    temperature=temperature,
                )
                if out:
                    break
            if out:
                out = _clean_slot_output(slot, out)
            if out:
                values[slot] = out
                ctx[slot] = out

    if is_v52_template:
        headline = " ".join(
            part.strip().rstrip(".")
            for part in [values.get("headline_layer_1", ""), values.get("headline_layer_2", "")]
            if part and part.strip()
        ).strip() or values.get(slots_list[0], "")
    else:
        headline = values.get("headline") or values.get(slots_list[0], "")
    source_url = item.get("url") or ""
    body_parts = [f"<h1>{headline.strip()}</h1>"]
    content_slots = list(slots_list[1:]) + [slot for slot in optional_slots if slot in values]
    for slot in content_slots:
        text = values.get(slot, "")
        if text:
            body_parts.append(_to_html_paragraph(text))
    if source_url:
        body_parts.append(f'<p><em>Source: <a href="{source_url}">{source_url}</a></em></p>')

    merged = "\n\n".join([p for p in body_parts if p.strip()])
    if lang not in ("en", ""):
        merged = localize_source_line_html(merged, lang)

    thin_retry = bool(prov.get("thin_output_retry", config.get("thin_output_retry", True)))
    floor = _min_output_floor(lang, config, prov)
    if thin_retry and _plain_text_len(merged) < floor and not simulate:
        retry_user = (
            f"The article HTML below is too short (need roughly {floor} characters of readable text). "
            "Expand body paragraphs in place with concrete anchors; keep <h1>, paragraph structure, and the final "
            "source line. Do not remove facts. Output only the full HTML body.\n\n" + merged
        )
        retry_max = int(prov.get("max_tokens") or config.get("max_tokens") or 2048)
        expanded = backend.complete_chat(
            system_prompt,
            retry_user,
            max_tokens=retry_max,
            temperature=min(0.8, temperature + 0.1),
        )
        if expanded:
            expanded = _strip_fences(expanded.strip())
            if expanded and "<h1" in expanded.lower():
                merged = expanded
                if lang not in ("en", ""):
                    merged = localize_source_line_html(merged, lang)
                logger.warning(
                    "Article %s: thin output retry applied (len was below %s)",
                    article_id,
                    floor,
                )
            else:
                logger.warning("Article %s: thin output retry returned unusable HTML", article_id)
        else:
            logger.warning("Article %s: thin output retry failed", article_id)

    item["content"] = merged

    v52_slots: dict[str, str] = {}
    if is_v52_template:
        for slot in slots_list:
            if values.get(slot):
                v52_slots[slot] = values[slot]
        for slot in optional_slots:
            if values.get(slot):
                v52_slots[slot] = values[slot]
    else:
        v52_map = V52_SLOT_MAP.get(template_id, V52_SLOT_MAP["hard_news_spiritual_response"])
        for template_slot, v52_name in v52_map.items():
            if template_slot in values and values[template_slot]:
                v52_slots[v52_name] = values[template_slot]
    item["_v52_slots"] = v52_slots

    item["_expansion_retries"] = 0
    if expansion_provider_label:
        item["_expansion_provider"] = expansion_provider_label
    elif isinstance(backend, AnthropicBackend):
        item["_expansion_provider"] = "claude"
    else:
        item["_expansion_provider"] = "qwen"
    item["_expansion_engine"] = "slot_expansion"

    wc = len(item["content"].split())
    logger.info(
        "Article %s: slot engine wrote %d words across %d slots (%.1fs) provider=%s",
        article_id,
        wc,
        len([v for v in values.values() if v]),
        elapsed,
        item.get("_expansion_provider"),
    )
    return item
