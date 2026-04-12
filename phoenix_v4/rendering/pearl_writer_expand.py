"""
Pearl_Writer — Thin-Section Expansion Runtime

Last-mile length and coherence pass: brings a thin stacked section up to delivery
length without breaking teacher atom voice or arc intent.

Contract: docs/PEARL_WRITER_EXPANSION_SPEC.md
Authority: specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md; specs/PHOENIX_V4_5_WRITER_SPEC.md
"""
from __future__ import annotations

import logging
import os
import re
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────────────

DEFAULT_THIN_THRESHOLD = 350          # spec §1: activate when wc < min(350, target-100)
DEFAULT_MAX_BUDGET = 400              # spec §2: cap expansion_budget at 400 words
DEFAULT_MODEL = "claude-sonnet-4-6"  # Pearl_Writer = Claude Sonnet 4.6
DEFAULT_TIMEOUT = 90.0


# ── Trigger check ─────────────────────────────────────────────────────────────

def should_expand(packet: dict) -> bool:
    """
    Return True when the section is thin enough to warrant Pearl_Writer expansion.

    Spec §1 trigger: word_count < min(350, target_words - 100)
    """
    wc = int(packet.get("word_count") or 0)
    target = int(packet.get("target_words") or 450)
    threshold = min(DEFAULT_THIN_THRESHOLD, target - 100)
    return wc < threshold


# ── Prompt builders ───────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """\
You are Pearl_Writer, a bounded prose-development layer in the Phoenix Omega spine pipeline.

Your sole job: expand a thin audiobook section to its word-count target while preserving the exact teacher voice, arc intent, and layer order already present.

Rules (non-negotiable):
1. Preserve existing sentences — do NOT rewrite or remove them. Add prose around them.
2. Maintain layer order: bridge → journey intro → legacy → enrichment → teacher atom → depth.
3. No new claims, concepts, or teaching assertions not already present in the section or provided teacher atoms.
4. Transitions and coherence glue only — max 15% of added words may be connective tissue.
5. Match the teacher's register, cultural framing, and second-person stance exactly.
6. No markdown, headers, bullets, or meta-commentary. Plain prose only.
7. Output ONLY the final expanded section text. Nothing else.
"""

def _build_user_prompt(
    *,
    existing_text: str,
    target_words: int,
    current_words: int,
    teacher_voice: Optional[Any],
    layer_preservation: Optional[List[str]],
    spine_context: dict,
    seed: str,
) -> str:
    ctx = spine_context or {}
    topic = ctx.get("topic") or ctx.get("topic_id") or "unknown"
    persona = ctx.get("persona_id") or "unknown"
    teacher = ctx.get("teacher_id") or "unknown"
    engine = ctx.get("engine") or "standard_book"
    format_ = ctx.get("format") or engine

    voice_block = ""
    if teacher_voice:
        if isinstance(teacher_voice, str):
            voice_block = teacher_voice[:2000]
        elif isinstance(teacher_voice, dict):
            voice_block = str(teacher_voice)[:2000]
        elif isinstance(teacher_voice, list):
            voice_block = "\n---\n".join(str(v)[:400] for v in teacher_voice[:5])

    layer_block = ""
    if layer_preservation:
        layer_block = "Layer order to preserve: " + ", ".join(layer_preservation)

    return f"""\
EXPANSION TASK
Seed: {seed}
Topic: {topic} | Persona: {persona} | Teacher: {teacher} | Format: {format_}

Current section word count: {current_words}
Target word count: {target_words}
Words to add: ~{target_words - current_words}

{layer_block}

TEACHER VOICE REFERENCE (match this register and style exactly):
{voice_block if voice_block else "(no voice reference provided — match the register in the existing section)"}

EXISTING SECTION (preserve every sentence; expand between and around them):
{existing_text}

Write the expanded section now. Hit {target_words} words. Output the full section — existing sentences included.
"""


# ── Layer map builder ─────────────────────────────────────────────────────────

def _build_layer_map(text: str, sources_used: List[str]) -> Dict[str, str]:
    """
    Rough paragraph → layer attribution. We can only heuristically attribute since
    the stacked text no longer carries explicit markers. Uses sources_used ordering.
    """
    paragraphs = [p.strip() for p in re.split(r"\n\n+", text) if p.strip()]
    layer_cycle = list(sources_used) if sources_used else ["expanded"]
    result: Dict[str, str] = {}
    for i, para in enumerate(paragraphs):
        label = layer_cycle[i] if i < len(layer_cycle) else "pearl_writer:expansion"
        key = f"para_{i+1}"
        result[key] = label
    return result


# ── Claude API call ───────────────────────────────────────────────────────────

def _call_claude_api(
    *,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int,
    model: str = DEFAULT_MODEL,
    timeout: float = DEFAULT_TIMEOUT,
    api_key: Optional[str] = None,
) -> Optional[str]:
    """
    Call Claude via the Anthropic SDK. Returns generated text or None on failure.
    Mirrors the pattern in pearl_news/pipeline/llm_expand_claude.py.
    """
    key = api_key or os.environ.get("ANTHROPIC_API_KEY") or ""
    if not key:
        logger.error("ANTHROPIC_API_KEY not set; cannot call Claude API")
        return None

    try:
        from anthropic import Anthropic
    except ImportError:
        logger.error("anthropic package not installed: pip install anthropic")
        return None

    client = Anthropic(api_key=key, timeout=timeout, max_retries=1)
    for attempt in range(2):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
                temperature=0.4,  # low temp for determinism + voice fidelity
            )
            text = "".join(
                block.text for block in response.content if hasattr(block, "text")
            )
            return text.strip() if text.strip() else None
        except Exception as exc:
            msg = str(exc)
            if ("rate_limit_error" in msg or "429" in msg) and attempt == 0:
                logger.warning("Claude API rate-limited; sleeping 65s before retry")
                time.sleep(65)
                continue
            logger.warning("Claude API call failed: %s", exc)
            return None
    return None


# ── Word count ────────────────────────────────────────────────────────────────

def _word_count(text: str) -> int:
    return len(text.split()) if text else 0


# ── Main expand entry point ───────────────────────────────────────────────────

def expand_section(
    request: dict,
    *,
    dry_run: bool = False,
    model: str = DEFAULT_MODEL,
    api_key: Optional[str] = None,
) -> dict:
    """
    Expand a thin section packet to its word-count target.

    Input fields (spec §2):
        packet            — full compose_section_packet return dict
        spine_context     — topic/persona/teacher/engine/format/plan context
        teacher_voice     — teacher atom voice envelope (str | dict | list)
        layer_preservation — ordered source labels from packet["sources_used"]
        expansion_budget  — max added words (default target - current, cap 400)
        seed              — deterministic seed string

    Returns dict with:
        text, word_count, sources_used_delta, layer_map, warnings,
        expanded (bool), dry_run (bool)

    In dry_run=True: returns report without calling the LLM.
    """
    packet: dict = request.get("packet") or {}
    spine_context: dict = request.get("spine_context") or {}
    teacher_voice = request.get("teacher_voice")
    layer_preservation: List[str] = request.get("layer_preservation") or list(
        packet.get("sources_used") or []
    )
    seed: str = str(request.get("seed") or "pearl_writer:expansion_v1")

    existing_text: str = packet.get("text") or ""
    current_words: int = int(packet.get("word_count") or _word_count(existing_text))
    target_words: int = int(
        request.get("target_words") or packet.get("target_words") or 450
    )
    max_budget: int = int(
        request.get("expansion_budget")
        if request.get("expansion_budget") is not None
        else min(target_words - current_words, DEFAULT_MAX_BUDGET)
    )
    max_budget = max(0, max_budget)

    warnings: List[str] = list(packet.get("warnings") or [])

    # ── Validate trigger ──────────────────────────────────────────────────────
    if not should_expand(packet):
        return {
            "text": existing_text,
            "word_count": current_words,
            "sources_used_delta": [],
            "layer_map": _build_layer_map(existing_text, layer_preservation),
            "warnings": warnings,
            "expanded": False,
            "dry_run": dry_run,
        }

    # ── Non-trigger guard: skip on bad data ───────────────────────────────────
    teacher_id = spine_context.get("teacher_id") or packet.get("teacher_id")
    if not teacher_id and not teacher_voice:
        warnings.append("pearl_writer:skipped — empty teacher_id and no voice context")
        return {
            "text": existing_text,
            "word_count": current_words,
            "sources_used_delta": [],
            "layer_map": _build_layer_map(existing_text, layer_preservation),
            "warnings": warnings,
            "expanded": False,
            "dry_run": dry_run,
        }

    # ── Dry-run report ────────────────────────────────────────────────────────
    if dry_run:
        return {
            "text": existing_text,
            "word_count": current_words,
            "sources_used_delta": [],
            "layer_map": _build_layer_map(existing_text, layer_preservation),
            "warnings": warnings,
            "expanded": False,
            "dry_run": True,
            "dry_run_report": {
                "would_expand": True,
                "current_words": current_words,
                "target_words": target_words,
                "words_to_add": min(target_words - current_words, max_budget),
                "expansion_budget": max_budget,
                "seed": seed,
                "teacher_id": teacher_id,
                "section_type": packet.get("section_type"),
                "chapter_index": packet.get("chapter_index"),
                "section_index": packet.get("section_index"),
            },
        }

    # ── Live expansion ────────────────────────────────────────────────────────
    # tokens ≈ words × 1.4; add headroom for the existing text
    max_tokens = min(4096, int((target_words + 200) * 1.5))

    user_prompt = _build_user_prompt(
        existing_text=existing_text,
        target_words=target_words,
        current_words=current_words,
        teacher_voice=teacher_voice,
        layer_preservation=layer_preservation,
        spine_context=spine_context,
        seed=seed,
    )

    raw_output = _call_claude_api(
        system_prompt=_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        max_tokens=max_tokens,
        model=model,
        api_key=api_key,
    )

    if not raw_output:
        warnings.append("pearl_writer:api_call_failed — falling back to pre-expansion packet")
        return {
            "text": existing_text,
            "word_count": current_words,
            "sources_used_delta": [],
            "layer_map": _build_layer_map(existing_text, layer_preservation),
            "warnings": warnings,
            "expanded": False,
            "dry_run": False,
        }

    expanded_wc = _word_count(raw_output)

    # ── Quality gate ──────────────────────────────────────────────────────────
    # Attempt chapter_flow_gate if available; fall back on failure (spec §5)
    gate_passed = True
    try:
        from phoenix_v4.quality.chapter_flow_gate import check_section  # type: ignore
        gate_result = check_section(raw_output, section_type=packet.get("section_type"))
        if not gate_result.get("pass", True):
            gate_passed = False
            warnings.append(
                f"pearl_writer:flow_gate_failed:{gate_result.get('reason','unknown')} — fallback to pre-expansion"
            )
    except ImportError:
        pass  # gate not available; proceed

    if not gate_passed:
        return {
            "text": existing_text,
            "word_count": current_words,
            "sources_used_delta": [],
            "layer_map": _build_layer_map(existing_text, layer_preservation),
            "warnings": warnings,
            "expanded": False,
            "dry_run": False,
        }

    return {
        "text": raw_output,
        "word_count": expanded_wc,
        "sources_used_delta": ["pearl_writer:expansion_v1"],
        "layer_map": _build_layer_map(raw_output, layer_preservation),
        "warnings": warnings,
        "expanded": True,
        "dry_run": False,
    }
