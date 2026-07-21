#!/usr/bin/env python3
"""Build Pearl_Research briefs and provider-specific deep-research prompts.

This module is intentionally offline and deterministic. It does not perform
research and does not call an LLM. Its job is to turn messy operator context
into a structured intermediate artifact, then compile high-quality prompts for
the downstream research engines.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - surfaced as a clean runtime error.
    yaml = None  # type: ignore[assignment]


REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTING_CONFIG_PATH = REPO_ROOT / "config" / "research" / "deep_research_prompt_routing.yaml"
PROMPT_META_ROOT = REPO_ROOT / "research" / "prompts" / "meta"

TEMPLATE_PATHS = {
    "master": PROMPT_META_ROOT / "deep_research_master_prompt.md",
    "gemini": PROMPT_META_ROOT / "deep_research_gemini_prompt.md",
    "qwen_china": PROMPT_META_ROOT / "deep_research_qwen_china_prompt.md",
    "rakuten_japan": PROMPT_META_ROOT / "deep_research_rakuten_japan_prompt.md",
}

BRIEF_FIELD_ORDER = [
    "what_is_broken",
    "decision_to_make",
    "unknowns",
    "missing_evidence",
    "exact_questions",
    "hypotheses_to_test",
    "constraints",
    "good_output_should_include",
    "explicit_exclusions",
]

SECTION_HEADING_ALIASES = {
    "what_is_broken": [
        "what is broken",
        "what broke",
        "problem",
        "problems",
        "this is the problem",
        "failure symptom",
        "failure symptoms",
        "failing output",
        "failing outputs",
        "failing output symptom",
        "current failure symptoms",
        "symptoms",
    ],
    "decision_to_make": [
        "decision",
        "decision needed",
        "decision to make",
        "operator decision",
        "operator question",
        "real question",
        "recommendation needed",
    ],
    "unknowns": [
        "unknown",
        "unknowns",
        "open questions",
        "open question",
        "unclear",
        "needs validation",
    ],
    "missing_evidence": [
        "missing evidence",
        "evidence missing",
        "evidence gaps",
        "missing proof",
        "source gaps",
        "provenance gaps",
    ],
    "exact_questions": [
        "exact questions",
        "questions",
        "questions to answer",
        "specific questions",
        "specific questions to answer",
    ],
    "constraints": [
        "constraints",
        "requirements",
        "implementation requirements",
        "rules",
        "must preserve",
    ],
    "good_output_should_include": [
        "good output",
        "good output should include",
        "deliverable format",
        "required output",
        "output should include",
    ],
    "explicit_exclusions": [
        "exclude",
        "exclusions",
        "do not include",
        "do not",
        "avoid",
        "must not include",
    ],
    "source_rules": [
        "sources",
        "source rules",
        "source preferences",
        "preferred sources",
        "acceptable sources",
        "evidence standards",
    ],
}

PROMPT_QUALITY_PATTERNS = {
    "exact_research_objective": [r"exact research objective|research objective|objective"],
    "system_business_context": [r"phoenix omega context|business and system context|system context"],
    "failure_symptoms": [r"failure symptoms|current failure|what is broken|broken"],
    "hypotheses_to_test": [r"hypotheses? to test|disconfirming evidence"],
    "specific_questions": [r"specific questions|exact questions|questions .* answer"],
    "required_comparisons": [r"required comparisons|compare|comparison"],
    "decision_output": [r"decision to make|recommended action|decision-oriented"],
    "evidence_standards": [r"evidence standards|evidence requirements|source rules"],
    "source_quality_rules": [r"primary sources|official docs|source-quality|weak evidence"],
    "no_generic_advice": [r"do not give generic|generic advice"],
    "contradictions_uncertainty": [r"contradictions?|ambiguities|uncertainty|tradeoffs?"],
    "phoenix_implications": [r"implementation implications for phoenix omega"],
    "provenance_sources": [r"provenance|sources"],
}


@dataclass
class ResearchPromptInputs:
    """Raw inputs accepted by the prompt-generation layer."""

    transcript: str = ""
    issue_description: str = ""
    failing_outputs: list[str] = field(default_factory=list)
    relevant_files: dict[str, str] = field(default_factory=dict)
    repo_context: str = ""
    prompt_id: str = ""
    title: str = ""
    markets: list[str] = field(default_factory=list)
    locales: list[str] = field(default_factory=list)
    platforms: list[str] = field(default_factory=list)
    source_preferences: list[str] = field(default_factory=list)
    exclusions: list[str] = field(default_factory=list)


def _require_yaml() -> Any:
    if yaml is None:
        raise RuntimeError("PyYAML is required for Pearl_Research prompt generation.")
    return yaml


def load_routing_config(path: Path = ROUTING_CONFIG_PATH) -> dict[str, Any]:
    loader = _require_yaml()
    with open(path, "r", encoding="utf-8") as f:
        return loader.safe_load(f) or {}


def _unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        value = " ".join(str(item).strip().split())
        if not value:
            continue
        key = value.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(value)
    return out


def _term_matches(term: str, lower_text: str) -> bool:
    lowered = term.lower().strip()
    if not lowered:
        return False
    if re.fullmatch(r"[a-z0-9_.-]+", lowered):
        boundary_chars = r"a-z0-9_.-" if len(lowered) <= 2 else r"a-z0-9"
        pattern = r"(?<![" + boundary_chars + r"])" + re.escape(lowered) + r"(?![" + boundary_chars + r"])"
        return re.search(pattern, lower_text) is not None
    return lowered in lower_text


def _normalize_heading(value: str) -> str:
    value = re.sub(r"[`*_#>-]+", " ", value.strip().lower())
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def _section_key_for_label(label: str) -> str | None:
    normalized = _normalize_heading(label)
    if not normalized:
        return None
    for key, aliases in SECTION_HEADING_ALIASES.items():
        for alias in aliases:
            if normalized == _normalize_heading(alias):
                return key
    return None


def _strip_list_marker(line: str) -> tuple[str, bool]:
    match = re.match(r"^\s*(?:[-*+]|\d+[.)])\s+(.*)$", line)
    if not match:
        return line.strip(), False
    return match.group(1).strip(), True


def _section_key_and_remainder(line: str) -> tuple[str | None, str]:
    line, _ = _strip_list_marker(line)
    clean = line.strip().strip("# ").strip()
    if not clean:
        return None, ""

    if ":" in clean:
        prefix, remainder = clean.split(":", 1)
        key = _section_key_for_label(prefix)
        if key:
            return key, remainder.strip()

    return _section_key_for_label(clean), ""


def slugify(value: str, default: str = "research-brief") -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:80] or default


def compact_text(text: str, max_chars: int = 6000) -> str:
    text = text.strip()
    if len(text) <= max_chars:
        return text
    head = text[: max_chars // 2].rstrip()
    tail = text[-(max_chars // 2) :].lstrip()
    return f"{head}\n\n[... middle truncated by prompt builder ...]\n\n{tail}"


def _all_input_text(inputs: ResearchPromptInputs) -> str:
    pieces = [
        inputs.issue_description,
        inputs.transcript,
        "\n\n".join(inputs.failing_outputs),
        inputs.repo_context,
        "\n\n".join(inputs.relevant_files.values()),
        " ".join(inputs.markets + inputs.locales + inputs.platforms),
    ]
    return "\n\n".join(p for p in pieces if p.strip())


def _context_items(text: str, *, include_headings: bool = False) -> list[str]:
    """Return cleaned transcript items while preserving wrapped bullet/prose lines."""
    items: list[str] = []
    current = ""
    current_is_heading = False

    def flush() -> None:
        nonlocal current, current_is_heading
        value = " ".join(current.split()).strip()
        if value and (include_headings or _section_key_and_remainder(value)[0] is None):
            items.append(value)
        current = ""
        current_is_heading = False

    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped:
            flush()
            continue

        stripped = stripped.lstrip("> ").strip()
        line, is_list_item = _strip_list_marker(stripped)
        section_key, _ = _section_key_and_remainder(line)
        is_heading = section_key is not None
        previous_looks_wrapped = bool(current) and not re.search(r"[.!?;:)\"']$", current)
        indented_continuation = bool(raw[: len(raw) - len(raw.lstrip())]) and not is_list_item
        should_continue = (
            bool(current)
            and not current_is_heading
            and not is_heading
            and not is_list_item
            and (previous_looks_wrapped or indented_continuation)
        )

        if should_continue:
            current = f"{current.rstrip()} {line.strip()}"
            continue

        flush()
        current = line.strip()
        current_is_heading = is_heading and not _section_key_and_remainder(line)[1]

    flush()
    return items


def _candidate_lines(text: str) -> list[str]:
    lines: list[str] = []
    for line in _context_items(text):
        if not line:
            continue
        if len(line) > 280:
            chunks = re.split(r"(?<=[.!?])\s+", line)
            lines.extend(chunk.strip() for chunk in chunks if chunk.strip())
        else:
            lines.append(line)
    return lines


def _extract_section_items(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {key: [] for key in SECTION_HEADING_ALIASES}
    current_key: str | None = None
    current_item = ""

    def flush_item() -> None:
        nonlocal current_item
        value = " ".join(current_item.split()).strip()
        if current_key and value:
            sections[current_key].append(value)
        current_item = ""

    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped:
            flush_item()
            current_key = None
            continue

        stripped = stripped.lstrip("> ").strip()
        line, is_list_item = _strip_list_marker(stripped)
        key, remainder = _section_key_and_remainder(line)
        if key:
            flush_item()
            current_key = key
            if remainder:
                current_item = remainder
            continue

        if current_key:
            previous_looks_wrapped = bool(current_item) and not re.search(r"[.!?;:)\"']$", current_item)
            indented_continuation = bool(raw[: len(raw) - len(raw.lstrip())]) and not is_list_item
            if current_item and not is_list_item and (previous_looks_wrapped or indented_continuation):
                current_item = f"{current_item.rstrip()} {line.strip()}"
            else:
                flush_item()
                current_item = line.strip()

    flush_item()

    return {key: _unique(values) for key, values in sections.items() if values}


def _select_lines(text: str, keywords: list[str], max_items: int = 8) -> list[str]:
    selected: list[str] = []
    lowered_keywords = [k.lower() for k in keywords]
    for line in _candidate_lines(text):
        lower = line.lower()
        if any(keyword in lower for keyword in lowered_keywords):
            selected.append(line)
        if len(selected) >= max_items:
            break
    return _unique(selected)


def _question_lines(text: str, max_items: int = 8) -> list[str]:
    questions = [line for line in _candidate_lines(text) if "?" in line]
    return _unique(questions[:max_items])


def _format_list(items: list[str], fallback: str) -> str:
    values = _unique(items)
    if not values:
        return f"- {fallback}"
    return "\n".join(f"- {item}" for item in values)


def _format_sources(source_rules: dict[str, list[str]]) -> str:
    parts: list[str] = []
    labels = [
        ("Preferred sources", "preferred_sources"),
        ("Acceptable sources", "acceptable_sources"),
        ("Weak sources", "weak_sources"),
        ("Source languages", "source_languages"),
    ]
    for label, key in labels:
        values = source_rules.get(key, [])
        if values:
            parts.append(f"{label}:\n" + "\n".join(f"- {item}" for item in values))
    return "\n\n".join(parts) if parts else "- Use cited primary and high-authority secondary sources."


def _format_markets(markets_locales_platforms: dict[str, list[str]]) -> str:
    sections = [
        ("Markets", markets_locales_platforms.get("markets", []), "No explicit market detected."),
        ("Locales", markets_locales_platforms.get("locales", []), "No explicit locale detected."),
        ("Platforms", markets_locales_platforms.get("platforms", []), "No explicit platform detected."),
    ]
    return "\n\n".join(f"{label}:\n{_format_list(values, fallback)}" for label, values, fallback in sections)


def _default_source_rules(
    provider: dict[str, Any],
    source_preferences: list[str],
) -> dict[str, list[str]]:
    provider_languages = provider.get("source_language_priority") or []
    return {
        "preferred_sources": _unique(
            source_preferences
            + [
                "official platform documentation and policy pages",
                "primary market data, filings, or regulator publications",
                "credible industry reports and trade press",
                "academic or practitioner research with transparent methods",
            ]
        ),
        "acceptable_sources": [
            "credible news analysis with named sources",
            "platform-native examples when clearly labeled as examples",
            "expert commentary only when triangulated against stronger sources",
        ],
        "weak_sources": [
            "unsourced trend roundups",
            "affiliate SEO posts",
            "single-anecdote social media claims",
            "AI-generated summaries without source URLs",
        ],
        "source_languages": _unique(provider_languages or ["English-language sources"]),
    }


def _detect_values_from_routes(
    text: str,
    explicit_markets: list[str],
    explicit_locales: list[str],
    explicit_platforms: list[str],
    config: dict[str, Any],
) -> dict[str, list[str]]:
    lower = text.lower()
    markets = list(explicit_markets)
    locales = list(explicit_locales)
    platforms = list(explicit_platforms)
    for route in config.get("routes", []):
        match = route.get("match", {})
        if not explicit_markets:
            for market in match.get("markets", []):
                if _term_matches(market, lower):
                    markets.append(market)
        if not explicit_locales:
            for locale in match.get("locales", []):
                if _term_matches(locale, lower):
                    locales.append(locale)
        if not explicit_platforms:
            for platform in match.get("platforms", []):
                if _term_matches(platform, lower):
                    platforms.append(platform)
    return {
        "markets": _unique(markets),
        "locales": _unique(locales),
        "platforms": _unique(platforms),
    }


def _structured_route_signals(route: dict[str, Any], mlp: dict[str, list[str]]) -> list[str]:
    """Match inspectable routing signals from structured market/locale/platform hints."""
    match = route.get("match", {})
    signals: list[str] = []
    locale_values = {value.lower().strip() for value in mlp.get("locales", [])}
    market_text = " ".join(mlp.get("markets", [])).lower()
    platform_text = " ".join(mlp.get("platforms", [])).lower()

    for locale in match.get("locales", []):
        if str(locale).lower().strip() in locale_values:
            signals.append(f"locales:{locale}")
    for market in match.get("markets", []):
        if _term_matches(str(market), market_text):
            signals.append(f"markets:{market}")
    for platform in match.get("platforms", []):
        if _term_matches(str(platform), platform_text):
            signals.append(f"platforms:{platform}")
    return _unique(signals)


def _text_route_signals(route: dict[str, Any], haystack: str) -> list[str]:
    match = route.get("match", {})
    signals: list[str] = []
    for key in ("locales", "markets", "keywords", "platforms"):
        for term in match.get(key, []):
            if _term_matches(str(term), haystack):
                signals.append(f"{key}:{term}")
    return _unique(signals)


def _default_routing_result(config: dict[str, Any], signal: str) -> dict[str, Any]:
    providers = config.get("providers", {})
    provider_id = config.get("default_provider", "gemini_global")
    provider = providers.get(provider_id, {})
    return {
        "route_id": "default",
        "provider_id": provider_id,
        "provider": provider,
        "prompt_key": provider.get("prompt_key", "gemini"),
        "signals": [signal],
        "score": 0,
    }


def _explicit_routing_hints_present(brief: dict[str, Any]) -> bool:
    controls = brief.get("routing_controls", {})
    explicit_keys = ("explicit_markets", "explicit_locales", "explicit_platforms")
    return any(controls.get(key) for key in explicit_keys)


def choose_research_provider(
    brief: dict[str, Any],
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Choose the recommended provider from explicit routing config."""
    config = config or load_routing_config()
    providers = config.get("providers", {})
    mlp = brief.get("markets_locales_platforms", {})

    best_structured_route: dict[str, Any] | None = None
    best_structured_score = -1
    best_structured_signals: list[str] = []
    for route in config.get("routes", []):
        signals = _structured_route_signals(route, mlp)
        score = len(signals) * 100 + int(route.get("priority", 0))
        if signals and score > best_structured_score:
            best_structured_route = route
            best_structured_score = score
            best_structured_signals = signals

    if best_structured_route is not None:
        provider_id = best_structured_route.get("provider")
        provider = providers.get(provider_id, {})
        return {
            "route_id": best_structured_route.get("id", ""),
            "provider_id": provider_id,
            "provider": provider,
            "prompt_key": provider.get("prompt_key", "gemini"),
            "signals": best_structured_signals,
            "score": best_structured_score,
        }

    if _explicit_routing_hints_present(brief):
        return _default_routing_result(
            config,
            "default:explicit routing hints did not match China or Japan; ignoring noisy transcript-only regional terms",
        )

    haystack_parts: list[str] = []
    for key in ("title", "input_summary", "issue_description", *BRIEF_FIELD_ORDER):
        value = brief.get(key)
        if isinstance(value, list):
            haystack_parts.extend(value)
        elif value:
            haystack_parts.append(str(value))
    for key in ("markets", "locales", "platforms"):
        haystack_parts.extend(mlp.get(key, []))
    haystack = " ".join(haystack_parts).lower()

    best_route: dict[str, Any] | None = None
    best_score = -1
    best_signals: list[str] = []
    for route in config.get("routes", []):
        signals = _text_route_signals(route, haystack)
        score = len(signals) * 10 + int(route.get("priority", 0))
        if signals and score > best_score:
            best_route = route
            best_score = score
            best_signals = signals

    if best_route is None:
        return _default_routing_result(config, "default:no explicit China or Japan routing signal")

    provider_id = best_route.get("provider")
    provider = providers.get(provider_id, {})
    return {
        "route_id": best_route.get("id", ""),
        "provider_id": provider_id,
        "provider": provider,
        "prompt_key": provider.get("prompt_key", "gemini"),
        "signals": _unique(best_signals),
        "score": best_score,
    }


def build_research_brief(
    inputs: ResearchPromptInputs,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a structured research brief from messy context."""
    config = config or load_routing_config()
    all_text = _all_input_text(inputs)
    section_items = _extract_section_items(all_text)
    brief_hash = hashlib.sha1(all_text.encode("utf-8", errors="ignore")).hexdigest()[:10]
    if inputs.title:
        title = inputs.title
    elif inputs.issue_description:
        title = inputs.issue_description.splitlines()[0][:120]
    else:
        title = ""
    if not title:
        title = f"Pearl_Research prompt brief for {inputs.prompt_id or 'ad hoc research'}"

    detected = _detect_values_from_routes(
        all_text,
        inputs.markets,
        inputs.locales,
        inputs.platforms,
        config,
    )

    broken = section_items.get("what_is_broken") or _select_lines(
        all_text,
        ["broken", "failing", "fails", "failure", "wrong", "weak", "messy", "generic", "not the best", "regression"],
    )
    decisions = section_items.get("decision_to_make") or _select_lines(
        all_text,
        ["decision", "decide", "choose", "route", "should we", "recommend", "tradeoff", "which"],
    )
    unknowns = section_items.get("unknowns") or _select_lines(
        all_text,
        ["unknown", "unclear", "not sure", "verify", "validate", "figure out", "find out", "gap"],
    )
    missing = section_items.get("missing_evidence") or _select_lines(
        all_text,
        ["missing", "evidence", "source", "citation", "proof", "data", "benchmark", "provenance"],
    )
    constraints = section_items.get("constraints") or _select_lines(
        all_text,
        ["must", "do not", "don't", "never", "constraint", "preserve", "avoid", "exclude"],
        max_items=6,
    )
    exclusions = _unique(
        inputs.exclusions
        + section_items.get("explicit_exclusions", [])
        + _select_lines(all_text, ["do not", "exclude", "avoid", "never"], max_items=6)
    )
    questions = _unique(section_items.get("exact_questions", []) + _question_lines(all_text))
    if not questions:
        questions = [
            "What evidence explains the failure symptoms and which decision should Phoenix Omega make next?",
            "Which market, locale, or platform constraints materially change the recommendation?",
            "What implementation implications should Phoenix Omega account for before changing the system?",
        ]

    if not broken and inputs.issue_description:
        broken = [inputs.issue_description]
    if not decisions:
        decisions = ["Decide what Phoenix Omega should change, preserve, or route differently based on the evidence."]
    if not unknowns:
        unknowns = ["Which claims are true, current, market-specific, and supported by reliable sources."]
    if not missing:
        missing = ["Current source-backed evidence, contradictions across sources, and platform or locale-specific proof."]

    provider_preview = choose_research_provider(
        {
            "what_is_broken": broken,
            "decision_to_make": decisions,
            "unknowns": unknowns,
            "missing_evidence": missing,
            "exact_questions": questions,
            "constraints": constraints,
            "markets_locales_platforms": detected,
        },
        config,
    )
    provider = provider_preview["provider"]

    regional_text = " ".join(detected.get("markets", []) + detected.get("locales", [])).lower()
    regional_hypotheses: list[str] = []
    if "china" in regional_text or "zh-cn" in regional_text:
        regional_hypotheses.append("Chinese-language sources may materially change the China recommendation.")
    if "japan" in regional_text or "ja-jp" in regional_text:
        regional_hypotheses.append("Japanese-language sources may materially change the Japan recommendation.")
    hypotheses = _unique(
        [
            f"The current failure may be caused by: {item}"
            for item in (broken[:3] or ["insufficiently specific research prompts"])
        ]
        + [
            "Provider-native prompts may produce stronger evidence than a single generic prompt.",
            "The right answer may require preserving existing Phoenix Omega behavior while upgrading prompt quality before execution.",
        ]
        + regional_hypotheses
    )

    relevant_files = []
    for path, content in inputs.relevant_files.items():
        relevant_files.append(
            {
                "path": path,
                "excerpt": compact_text(content, max_chars=1200),
            }
        )

    source_rules = _default_source_rules(
        provider,
        inputs.source_preferences + section_items.get("source_rules", []),
    )

    brief = {
        "schema_version": "1.0",
        "brief_id": f"research-brief-{brief_hash}",
        "title": title,
        "created_at_utc": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "input_summary": compact_text(inputs.issue_description or all_text, max_chars=900),
        "issue_description": inputs.issue_description or "No separate issue description provided; see transcript/context.",
        "what_is_broken": broken,
        "decision_to_make": decisions,
        "unknowns": unknowns,
        "missing_evidence": missing,
        "exact_questions": questions,
        "hypotheses_to_test": hypotheses,
        "constraints": constraints or ["Preserve existing Phoenix Omega behavior unless evidence supports a change."],
        "markets_locales_platforms": detected,
        "routing_controls": {
            "explicit_markets": _unique(inputs.markets),
            "explicit_locales": _unique(inputs.locales),
            "explicit_platforms": _unique(inputs.platforms),
            "hint_precedence": (
                "Explicit market, locale, and platform hints override transcript-only "
                "regional mentions during provider selection."
            ),
        },
        "good_output_should_include": _unique(
            [
                "executive summary",
                "direct answer to the operator's real question",
                "evidence-backed findings",
                "contradictions and ambiguities",
                "recommended action",
                "implementation implications for Phoenix Omega",
                "open risks",
                "provenance and sources",
            ]
            + section_items.get("good_output_should_include", [])
        ),
        "source_rules": source_rules,
        "explicit_exclusions": exclusions or ["Generic advice that does not answer the Phoenix Omega decision."],
        "phoenix_omega_context": {
            "affected_subsystems": _unique([inputs.prompt_id, "Pearl_Research", "research prompts", "provider routing"]),
            "relevant_files": relevant_files,
            "implementation_constraints": _unique(
                [
                    "Extend existing Pearl_Research flow rather than creating a disconnected toy flow.",
                    "Keep routing explicit and inspectable.",
                    "Do not perform downstream research in the prompt-generation stage.",
                ]
                + constraints[:4]
            ),
        },
        "routing_preview": {
            "likely_provider": provider.get("display_name", provider_preview["provider_id"]),
            "routing_signals": provider_preview["signals"],
        },
        "raw_context_excerpt": compact_text(all_text, max_chars=5000),
    }
    return brief


def _brief_prompt_title(brief: dict[str, Any], suffix: str = "") -> str:
    base = brief.get("title") or "Pearl_Research Deep Research Prompt"
    return f"{base}{suffix}"


def _required_comparisons(brief: dict[str, Any]) -> list[str]:
    mlp = brief.get("markets_locales_platforms", {})
    comparisons = [
        "Compare strong evidence vs weak or anecdotal evidence.",
        "Compare current Phoenix Omega behavior vs the evidence-backed target behavior.",
    ]
    markets = mlp.get("markets", [])
    platforms = mlp.get("platforms", [])
    if len(markets) > 1:
        comparisons.append("Compare the named markets separately before synthesizing.")
    if len(platforms) > 1:
        comparisons.append("Compare platform-specific requirements and user behavior.")
    if markets and any(m.lower() == "china" or "mainland" in m.lower() for m in markets):
        comparisons.append("Compare China-native evidence against global/English-language assumptions.")
    if markets and any(m.lower() == "japan" for m in markets):
        comparisons.append("Compare Japan-native evidence against imported US/global assumptions.")
    return comparisons


def render_prompt(template_path: Path, brief: dict[str, Any], routing: dict[str, Any]) -> str:
    template = template_path.read_text(encoding="utf-8")
    mlp = brief.get("markets_locales_platforms", {})
    constraints_and_exclusions = _unique(
        list(brief.get("constraints", [])) + list(brief.get("explicit_exclusions", []))
    )
    mapping = {
        "PROMPT_TITLE": _brief_prompt_title(brief),
        "RESEARCH_OBJECTIVE": brief.get("issue_description", ""),
        "SYSTEM_CONTEXT": _format_list(
            brief.get("phoenix_omega_context", {}).get("implementation_constraints", [])
            + [
                "Recommended provider: "
                + routing.get("provider", {}).get("display_name", routing.get("provider_id", "")),
                "Routing signals: " + ", ".join(routing.get("signals", [])),
            ],
            "Phoenix Omega context was not specified.",
        ),
        "PROVIDER_STYLE_NOTES": _format_list(
            routing.get("provider", {}).get("style_notes", []),
            "Use the selected provider's strengths, but keep the report evidence-backed and decision-oriented.",
        ),
        "FAILURE_SYMPTOMS": _format_list(brief.get("what_is_broken", []), "No failure symptoms were extracted."),
        "DECISION_TO_MAKE": _format_list(brief.get("decision_to_make", []), "No decision was extracted."),
        "UNKNOWNS_AND_GAPS": _format_list(
            list(brief.get("unknowns", [])) + list(brief.get("missing_evidence", [])),
            "No evidence gaps were extracted.",
        ),
        "HYPOTHESES_TO_TEST": _format_list(brief.get("hypotheses_to_test", []), "No hypotheses were extracted."),
        "EXACT_QUESTIONS": _format_list(brief.get("exact_questions", []), "No exact questions were extracted."),
        "REQUIRED_COMPARISONS": _format_list(_required_comparisons(brief), "Compare alternatives where evidence supports it."),
        "MARKETS_LOCALES_PLATFORMS": _format_markets(mlp),
        "CONSTRAINTS_AND_EXCLUSIONS": _format_list(
            constraints_and_exclusions,
            "Avoid generic advice and keep the answer tied to Phoenix Omega.",
        ),
        "SOURCE_RULES": _format_sources(brief.get("source_rules", {})),
        "RAW_CONTEXT_EXCERPT": brief.get("raw_context_excerpt", ""),
    }
    rendered = template
    for key, value in mapping.items():
        rendered = rendered.replace("{{" + key + "}}", str(value))
    return rendered.rstrip() + "\n"


def compile_research_prompts(
    brief: dict[str, Any],
    routing: dict[str, Any] | None = None,
    config: dict[str, Any] | None = None,
) -> dict[str, str]:
    config = config or load_routing_config()
    routing = routing or choose_research_provider(brief, config)
    return {
        key: render_prompt(path, brief, routing)
        for key, path in TEMPLATE_PATHS.items()
    }


def build_prompt_package(
    inputs: ResearchPromptInputs,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    config = config or load_routing_config()
    brief = build_research_brief(inputs, config)
    routing = choose_research_provider(brief, config)
    brief["routing_preview"] = {
        "likely_provider": routing.get("provider", {}).get("display_name", routing.get("provider_id", "")),
        "routing_signals": routing.get("signals", []),
    }
    prompts = compile_research_prompts(brief, routing, config)
    return {
        "brief": brief,
        "routing": {
            "route_id": routing.get("route_id"),
            "provider_id": routing.get("provider_id"),
            "provider_display_name": routing.get("provider", {}).get("display_name"),
            "prompt_key": routing.get("prompt_key"),
            "signals": routing.get("signals", []),
            "score": routing.get("score"),
        },
        "prompts": prompts,
        "recommended_prompt_key": routing.get("prompt_key", "gemini"),
    }


def write_prompt_package(package: dict[str, Any], out_dir: Path, stem: str | None = None) -> dict[str, Path]:
    loader = _require_yaml()
    out_dir.mkdir(parents=True, exist_ok=True)
    brief = package["brief"]
    stem = slugify(stem or brief.get("title", "") or brief.get("brief_id", "research-brief"))
    paths: dict[str, Path] = {}

    brief_path = out_dir / f"{stem}_research_brief.yaml"
    brief_path.write_text(
        loader.safe_dump(brief, sort_keys=False, allow_unicode=True, width=1000),
        encoding="utf-8",
    )
    paths["brief"] = brief_path

    routing_path = out_dir / f"{stem}_routing.yaml"
    routing_path.write_text(
        loader.safe_dump(package["routing"], sort_keys=False, allow_unicode=True, width=1000),
        encoding="utf-8",
    )
    paths["routing"] = routing_path

    for key, prompt in package["prompts"].items():
        path = out_dir / f"{stem}_{key}_prompt.md"
        path.write_text(prompt, encoding="utf-8")
        paths[f"prompt_{key}"] = path

    index_path = out_dir / f"{stem}_INDEX.md"
    recommended = package.get("recommended_prompt_key", "gemini")
    lines = [
        f"# Pearl_Research Prompt Package: {brief.get('title', stem)}",
        "",
        f"Recommended provider: {package['routing'].get('provider_display_name')}",
        f"Recommended prompt: `{recommended}`",
        "",
        "## Files",
        "",
    ]
    for label, path in paths.items():
        lines.append(f"- `{label}`: `{path.name}`")
    lines.extend(
        [
            "",
            "## Usage",
            "",
            "Paste the recommended provider prompt into the downstream research engine.",
            "Do not treat this package as completed research; it is the pre-research prompt-generation artifact.",
        ]
    )
    index_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    paths["index"] = index_path
    return paths


def score_prompt_quality(prompt: str) -> dict[str, Any]:
    text = prompt.lower()
    checks: dict[str, bool] = {}
    for name, patterns in PROMPT_QUALITY_PATTERNS.items():
        checks[name] = any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)
    return {
        "score": sum(1 for passed in checks.values() if passed),
        "max_score": len(checks),
        "checks": checks,
    }
