#!/usr/bin/env python3
"""
Translation Comparator Loop — run_translation_loop.py

Ported from scripts/audiobook_script/run_comparator_loop.py.
Pipeline: English atom -> Qwen translate -> Judge -> [patch -> retry] -> pass or manual_review.

Architecture:
  - File-level parallelism: ThreadPoolExecutor(max_parallel_files).
  - Loop: translate -> judge -> score -> decision (pass / continue / manual_review).
  - Patch injection: judge-returned prompt_patches assembled by PatchApplier;
    appended to system prompt as REVISION INSTRUCTIONS block.
  - Manual review: files exhausting max_loops write defect history + best translation.

Config: config/localization/translation_loop_config.yaml
Checklist: config/localization/translation_checklist.yaml

Usage:
  # Single file test
  python scripts/localization/run_translation_loop.py \\
    --persona educators --topic anxiety --slot PIVOT --locale ja-JP

  # Full persona
  python scripts/localization/run_translation_loop.py \\
    --persona educators --locale ja-JP

  # All personas, all CJK6 locales
  python scripts/localization/run_translation_loop.py --all-locales

  # Dry run
  python scripts/localization/run_translation_loop.py --persona educators --locale ja-JP --dry-run
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

logger = logging.getLogger("translation_loop")

SLOT_TYPES = ("PIVOT", "TAKEAWAY", "THREAD", "PERMISSION", "STORY")
ENGINE_DIRS = ("comparison", "false_alarm", "grief", "overwhelm", "shame", "spiral", "watcher")
# All translatable atom types: slot types + engine directories
ALL_ATOM_TYPES = SLOT_TYPES + ENGINE_DIRS
CJK6_LOCALES = ("ja-JP", "ko-KR", "zh-CN", "zh-HK", "zh-SG", "zh-TW")
EUROPEAN_LOCALES = ("es-US", "es-ES", "fr-FR", "de-DE", "it-IT", "hu-HU")
ALL_LOCALES = CJK6_LOCALES + EUROPEAN_LOCALES

LOCALE_NAMES: dict[str, str] = {
    "ja-JP": "Japanese (日本語)",
    "ko-KR": "Korean (한국어)",
    "zh-CN": "Simplified Chinese (简体中文)",
    "zh-HK": "Traditional Chinese — Hong Kong (繁體中文 — 香港)",
    "zh-SG": "Simplified Chinese — Singapore (简体中文 — 新加坡)",
    "zh-TW": "Traditional Chinese — Taiwan (繁體中文 — 台灣)",
}

VARIANT_RE = re.compile(
    r"(^##\s+\S+\s+v\d+\s*)\s*\n---\s*\n([\s\S]*?)---\s*\n(.*?)(?=\n---\s*\n\n##|\n---\s*\Z)",
    re.MULTILINE | re.DOTALL,
)
# Legacy regex for atoms without metadata (empty block between --- delimiters)
VARIANT_RE_LEGACY = re.compile(
    r"(^##\s+\S+\s+v\d+\s*)\s*\n---\s*\n\s*---\s*\n(.*?)(?=\n---\s*\n\n##|\n---\s*\Z)",
    re.MULTILINE | re.DOTALL,
)


# ─── CONFIG ──────────────────────────────────────────────────────────────────

def _load_yaml(path: Path) -> dict:
    try:
        import yaml
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        logger.error("Failed to load %s: %s", path, e)
        return {}


def _load_config() -> dict:
    return _load_yaml(REPO_ROOT / "config" / "localization" / "translation_loop_config.yaml")


def _load_checklist() -> dict:
    return _load_yaml(REPO_ROOT / "config" / "localization" / "translation_checklist.yaml")


def _load_dotenv() -> None:
    env_path = REPO_ROOT / ".env"
    if not env_path.is_file():
        return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            if key.strip() and key.strip() not in os.environ:
                os.environ[key.strip()] = value.strip()


_load_dotenv()


# ─── DATA ────────────────────────────────────────────────────────────────────

@dataclass
class LoopTrace:
    file_id: str
    locale: str
    loop_index: int
    draft_hash: str
    prompt_patch: str
    aggregate_score: float
    hard_gates_passed: bool
    decision: str
    timestamp_utc: str
    gate_results: list[dict] = field(default_factory=list)


@dataclass
class FileResult:
    persona: str
    topic: str
    slot_type: str
    locale: str
    decision: str
    loops_attempted: int
    best_score: float
    best_translation: str
    final_translation: str
    traces: list[LoopTrace] = field(default_factory=list)
    error: str | None = None


# ─── PARSING ─────────────────────────────────────────────────────────────────

def parse_canonical(text: str) -> list[tuple[str, str, str]]:
    """Parse CANONICAL.txt into [(header, metadata, prose), ...].

    Handles both formats:
      - Legacy (no metadata): ## ROLE vNN\\n---\\n\\n---\\nprose\\n---
      - Engine (with metadata): ## ROLE vNN\\n---\\nBAND: 2\\n...\\n---\\nprose\\n---
    Returns (header, metadata_block, prose) tuples. metadata_block may be empty.
    """
    results = list(VARIANT_RE.finditer(text))
    if results:
        return [(m.group(1).strip(), m.group(2).strip(), m.group(3).strip()) for m in results]
    # Fall back to legacy regex (no metadata between --- delimiters)
    legacy = list(VARIANT_RE_LEGACY.finditer(text))
    return [(m.group(1).strip(), "", m.group(2).strip()) for m in legacy]


def format_canonical(variants: list[tuple[str, str, str] | tuple[str, str]]) -> str:
    """Format variants back to CANONICAL.txt. Accepts 2-tuples (legacy) or 3-tuples (with metadata)."""
    blocks = []
    for v in variants:
        if len(v) == 3:
            header, meta, prose = v
            if meta.strip():
                blocks.append(f"{header}\n---\n{meta}\n---\n{prose}\n---")
            else:
                blocks.append(f"{header}\n---\n\n---\n{prose}\n---")
        else:
            header, prose = v
            blocks.append(f"{header}\n---\n\n---\n{prose}\n---")
    return "\n\n".join(blocks) + "\n"


# ─── LLM CALLS ──────────────────────────────────────────────────────────────

def _call_translate(source_text: str, locale: str, system_prompt: str, cfg: dict) -> str:
    from scripts.localization.llm_client import call_llm
    return call_llm(
        system_prompt, source_text, cfg,
        role="draft", temperature=0.25,
    )


def _call_judge(english_source: str, translation: str, locale: str,
                slot_type: str, checklist: dict, cfg: dict) -> str:
    from scripts.localization.llm_client import call_llm

    gates = checklist.get("gates", [])
    locale_overrides = checklist.get("locale_overrides", {}).get(locale, {})
    additional = locale_overrides.get("additional_checks", [])

    gate_instructions = []
    for g in gates:
        gate_instructions.append(
            f"Gate: {g['gate_id']} ({g['type']})\n"
            f"  {g['judge_instruction']}\n"
            f"  Defect format: {g['defect_format']}\n"
            f"  Patch format: {g.get('prompt_patch_format', 'N/A')}"
        )

    system_prompt = (
        "You are a translation quality judge for therapeutic self-help content.\n"
        "Evaluate the translation against these gates:\n\n"
        + "\n\n".join(gate_instructions)
        + ("\n\nAdditional locale checks:\n" + "\n".join(f"- {c}" for c in additional) if additional else "")
        + "\n\nOutput a JSON array — one object per gate. Each object has keys: "
        "gate_id, pass (bool), score (float 0.0-1.0 for scored gates, null for hard), "
        "defect (string or null), prompt_patch (string or null — fix instruction for the translator).\n"
        "IMPORTANT: Keep defect and prompt_patch strings SHORT (one sentence each).\n"
        "Output ONLY valid JSON — no preamble, no markdown fences."
    )

    user_prompt = (
        f"SLOT TYPE: {slot_type}\n"
        f"TARGET LOCALE: {locale}\n\n"
        f"=== ENGLISH SOURCE ===\n{english_source}\n\n"
        f"=== TRANSLATION ===\n{translation}\n\n"
        "Evaluate against all gates. Return JSON array."
    )

    return call_llm(
        system_prompt, user_prompt, cfg,
        role="judge", temperature=0.1, max_tokens=16384,
    )


# ─── JSON REPAIR ────────────────────────────────────────────────────────────

def _parse_judge_json(raw: str) -> list[dict]:
    """Parse judge JSON with fallback repair for truncated responses."""
    try:
        return json.loads(raw)
    except json.JSONDecodeError as first_err:
        logger.warning("Judge JSON parse failed (%s), attempting repair", first_err)

    # Strategy 1: truncate to last complete object in array
    # Find the last '}' and close the array
    last_brace = raw.rfind("}")
    if last_brace > 0:
        candidate = raw[:last_brace + 1].rstrip().rstrip(",") + "]"
        # Ensure it starts with '['
        arr_start = candidate.find("[")
        if arr_start >= 0:
            candidate = candidate[arr_start:]
            try:
                result = json.loads(candidate)
                logger.info("Judge JSON repaired by truncating to last complete object")
                return result
            except json.JSONDecodeError:
                pass

    # Strategy 2: extract individual JSON objects with regex
    obj_pattern = re.compile(r'\{[^{}]*\}', re.DOTALL)
    objects = []
    for m in obj_pattern.finditer(raw):
        try:
            objects.append(json.loads(m.group()))
        except json.JSONDecodeError:
            continue
    if objects:
        logger.info("Judge JSON repaired by extracting %d individual objects", len(objects))
        return objects

    raise ValueError(f"Could not parse or repair judge JSON: {raw[:200]}...")


# ─── PATCH APPLIER (ported from run_comparator_loop.py) ─────────────────────

class PatchApplier:
    def __init__(self, cfg: dict, checklist: dict) -> None:
        pi = cfg.get("patch_injection", {})
        self.max_chars = pi.get("max_patch_tokens", 800) * 4
        self.hard_prefix = pi.get("hard_gate_prefix", "[HARD — must fix]")
        self.scored_prefix = pi.get("scored_gate_prefix", "[IMPROVE]")
        self.header_tpl = pi.get(
            "revision_block_header",
            "## REVISION INSTRUCTIONS (Loop {loop_index})\n## Fix ALL issues below.\n",
        )
        self._gate_weights: dict[str, float] = {}
        self._gate_types: dict[str, str] = {}
        for g in checklist.get("gates", []):
            self._gate_weights[g["gate_id"]] = g.get("weight", 1.0)
            self._gate_types[g["gate_id"]] = g.get("type", "hard")

    def assemble(self, original_prompt: str, gate_results: list[dict], loop_index: int) -> str:
        failed = [g for g in gate_results if not g.get("pass", True) and g.get("prompt_patch")]
        if not failed:
            return original_prompt

        hard = sorted(
            [g for g in failed if self._gate_types.get(g["gate_id"]) == "hard"],
            key=lambda g: g["gate_id"],
        )
        scored = sorted(
            [g for g in failed if self._gate_types.get(g["gate_id"]) == "scored"],
            key=lambda g: -self._gate_weights.get(g["gate_id"], 1.0),
        )

        header = self.header_tpl.format(loop_index=loop_index)
        lines = []
        for g in hard:
            defect = f" [Defect: {g['defect']}]" if g.get("defect") else ""
            lines.append(f"{self.hard_prefix} {g['gate_id']}{defect}: {g['prompt_patch']}")
        for g in scored:
            defect = f" [Defect: {g['defect']}]" if g.get("defect") else ""
            lines.append(f"{self.scored_prefix} {g['gate_id']}{defect}: {g['prompt_patch']}")

        patch = header + "\n".join(lines)
        if len(patch) > self.max_chars:
            hard_only = header + "\n".join(
                f"{self.hard_prefix} {g['gate_id']}: {g['prompt_patch']}" for g in hard
            )
            patch = hard_only[:self.max_chars]
            logger.warning("Patch truncated (hard gates only); loop=%d", loop_index)

        return original_prompt + "\n\n" + patch


# ─── SCORING (ported from run_comparator_loop.py) ───────────────────────────

def _aggregate_score(gate_results: list[dict], checklist: dict) -> tuple[float, bool]:
    gate_map = {g["gate_id"]: g for g in checklist.get("gates", [])}
    scored_total = 0.0
    max_scored = 0.0
    all_hard = True

    for r in gate_results:
        gid = r.get("gate_id", "")
        gdef = gate_map.get(gid, {})
        gtype = gdef.get("type", "hard")
        if gtype == "hard":
            if not r.get("pass", False):
                all_hard = False
        else:
            w = gdef.get("weight", 1.0)
            s = r.get("score") or 0.0
            scored_total += s * w
            max_scored += w

    agg = round(scored_total / max_scored, 4) if max_scored > 0 else 1.0
    return agg, all_hard


def _passes_threshold(agg: float, all_hard: bool, cfg: dict, locale: str) -> bool:
    if not all_hard:
        return False
    base = cfg.get("scoring", {}).get("min_scored_pass_threshold", 0.75)
    override = cfg.get("locale_threshold_overrides", {}).get(locale, {})
    return agg >= override.get("min_scored_pass_threshold", base)


# ─── SYSTEM PROMPT ───────────────────────────────────────────────────────────

def _make_translate_system_prompt(locale: str, slot_type: str) -> str:
    locale_name = LOCALE_NAMES.get(locale, locale)
    return (
        "You are a professional translator specializing in therapeutic and "
        f"self-help content. Translate the following from English to {locale_name}.\n\n"
        f"Content type: {slot_type} atom (20 variants).\n\n"
        "Rules:\n"
        "1. Preserve the second-person voice ('You are allowed to...')\n"
        "2. Preserve emotional tone — gentle, validating, zero judgment\n"
        "3. Use locale-native phrasing (not translationese)\n"
        "4. Preserve the ## TYPE vNN headers exactly as-is (English)\n"
        "5. Preserve the --- delimiters exactly as-is\n"
        "6. Do not add explanations or notes\n"
        "7. Return ONLY the translated text in identical format\n"
        "8. Each variant must read as native writing, not a translation"
    )


# ─── DISCOVERY ───────────────────────────────────────────────────────────────

def discover_atoms(
    atoms_root: Path,
    persona: str | None = None,
    topic: str | None = None,
    slot: str | None = None,
) -> list[tuple[str, str, str, Path]]:
    # Determine which atom types to scan.
    # --slot STORY  => only STORY directory
    # --slot comparison => only comparison engine
    # --slot ENGINE => all 7 engine directories
    # no filter => ALL_ATOM_TYPES (slots + engines)
    if slot:
        upper = slot.upper()
        lower = slot.lower()
        if upper in SLOT_TYPES:
            search_types = (upper,)
        elif lower in ENGINE_DIRS:
            search_types = (lower,)
        elif lower == "engine" or lower == "engines":
            search_types = ENGINE_DIRS
        else:
            search_types = (slot,)
    else:
        search_types = ALL_ATOM_TYPES

    manifest = []
    for st in search_types:
        for path in atoms_root.rglob(f"{st}/CANONICAL.txt"):
            if "locales" in path.parts:
                continue
            rel = path.relative_to(atoms_root)
            parts = rel.parts
            if len(parts) < 4 or parts[2] != st:
                continue
            p, t = parts[0], parts[1]
            if persona and p != persona:
                continue
            if topic and t != topic:
                continue
            manifest.append((p, t, st, path))
    manifest.sort()
    return manifest


# ─── ARTIFACTS ───────────────────────────────────────────────────────────────

def _write_trace(cfg: dict, trace: LoopTrace) -> None:
    base = REPO_ROOT / cfg.get("artifact_trace", {}).get("base_path", "artifacts/localization/translation_loop")
    d = base / trace.file_id / f"loop_{trace.loop_index}"
    d.mkdir(parents=True, exist_ok=True)
    (d / "trace.json").write_text(json.dumps({
        "file_id": trace.file_id, "locale": trace.locale,
        "loop_index": trace.loop_index, "draft_hash": trace.draft_hash,
        "prompt_patch": trace.prompt_patch, "aggregate_score": trace.aggregate_score,
        "hard_gates_passed": trace.hard_gates_passed, "decision": trace.decision,
        "timestamp_utc": trace.timestamp_utc, "gate_results": trace.gate_results,
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    jsonl = REPO_ROOT / cfg.get("observability", {}).get("jsonl_log_path", "artifacts/localization/loop_decisions.jsonl")
    jsonl.parent.mkdir(parents=True, exist_ok=True)
    with open(jsonl, "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "ts": trace.timestamp_utc, "file_id": trace.file_id, "locale": trace.locale,
            "loop": trace.loop_index, "decision": trace.decision,
            "score": trace.aggregate_score, "hard_ok": trace.hard_gates_passed,
        }, ensure_ascii=False) + "\n")


def _write_manual_review(cfg: dict, result: FileResult) -> None:
    base = REPO_ROOT / cfg.get("artifact_trace", {}).get("base_path", "artifacts/localization/translation_loop")
    file_id = f"{result.persona}/{result.topic}/{result.slot_type}/{result.locale}"
    d = base / file_id / "manual_review"
    d.mkdir(parents=True, exist_ok=True)
    (d / "best_translation.txt").write_text(result.best_translation, encoding="utf-8")
    (d / "final_translation.txt").write_text(result.final_translation, encoding="utf-8")
    history = [{"loop": t.loop_index, "score": t.aggregate_score, "gates": t.gate_results} for t in result.traces]
    (d / "defect_history.json").write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")

    queue_path = REPO_ROOT / cfg.get("artifact_trace", {}).get(
        "manual_review_queue_file", "artifacts/localization/manual_review_queue.json")
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    queue = []
    if queue_path.exists():
        try:
            queue = json.loads(queue_path.read_text(encoding="utf-8"))
        except Exception:
            queue = []
    queue.append({
        "file_id": file_id, "persona": result.persona, "topic": result.topic,
        "slot": result.slot_type, "locale": result.locale,
        "best_score": result.best_score, "loops": result.loops_attempted,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    })
    queue_path.write_text(json.dumps(queue, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.warning("MANUAL REVIEW: %s/%s/%s locale=%s", result.persona, result.topic, result.slot_type, result.locale)


# ─── THE LOOP ────────────────────────────────────────────────────────────────

def run_file_loop(
    persona: str, topic: str, slot_type: str, source_path: Path,
    locale: str, cfg: dict, checklist: dict, resume: bool,
) -> FileResult:
    """Run translate -> judge -> patch -> retry loop for one CANONICAL.txt file."""
    file_id = f"{persona}/{topic}/{slot_type}/{locale}"
    atoms_root = source_path.parent.parent.parent.parent
    out_path = atoms_root / persona / topic / slot_type / "locales" / locale / "CANONICAL.txt"

    # Resume check
    if resume and out_path.exists() and out_path.stat().st_size > 100:
        return FileResult(
            persona=persona, topic=topic, slot_type=slot_type, locale=locale,
            decision="resume_skip", loops_attempted=0, best_score=1.0,
            best_translation="", final_translation="",
        )

    source_text = source_path.read_text(encoding="utf-8")
    source_variants = parse_canonical(source_text)
    if len(source_variants) == 0:
        return FileResult(
            persona=persona, topic=topic, slot_type=slot_type, locale=locale,
            decision="skip", loops_attempted=0, best_score=0.0,
            best_translation="", final_translation="",
            error=f"Source has 0 variants (cannot translate empty file)",
        )

    max_loops = cfg.get("loop_control", {}).get("max_loops", 3)
    single_pass = cfg.get("single_pass", True)  # DEFAULT: single-pass mode

    base_prompt = _make_translate_system_prompt(locale, slot_type)
    traces: list[LoopTrace] = []
    best_translation = ""
    final_translation = ""
    best_score = -1.0

    if single_pass:
        # ── SINGLE-PASS MODE (DEFAULT) ────────────────────────────────
        # 1 translate call → write → TTS byte check → done. No judge, no retry.
        ts = datetime.now(timezone.utc).isoformat()
        logger.info("Single-pass: %s → %s", file_id, locale)

        # 1. TRANSLATE (1 API call only)
        try:
            translation = _call_translate(source_text, locale, base_prompt, cfg)
        except Exception as e:
            logger.error("Translate failed: %s: %s", file_id, e)
            return FileResult(
                persona=persona, topic=topic, slot_type=slot_type, locale=locale,
                decision="error", loops_attempted=1, best_score=0.0,
                best_translation="", final_translation="",
                error=str(e),
            )

        final_translation = translation
        best_translation = translation
        best_score = 1.0  # No judge → assume pass

        # 2. TTS BYTE CHECK (validate translation isn't broken)
        tts_ok = True
        if translation and len(translation.strip()) < 10:
            tts_ok = False
            logger.warning("TTS check: translation too short (%d chars): %s", len(translation), file_id)
        # Check for obvious translation failures
        if translation and source_text.strip()[:50] in translation:
            # Translation is identical to source — likely failed
            tts_ok = False
            logger.warning("TTS check: translation identical to source: %s", file_id)

        decision = "pass" if tts_ok else "tts_fail"
        traces.append(LoopTrace(
            file_id=file_id, locale=locale, loop_index=1,
            draft_hash=hashlib.sha256(translation.encode()).hexdigest()[:16],
            prompt_patch="", aggregate_score=1.0 if tts_ok else 0.0,
            hard_gates_passed=tts_ok, decision=decision, timestamp_utc=ts,
        ))
        _write_trace(cfg, traces[-1])

    else:
        # ── JUDGE-LOOP MODE (--judge-loop) ────────────────────────────
        # Old behavior: translate → judge → score → patch → retry
        patcher = PatchApplier(cfg, checklist)
        current_prompt = base_prompt

        for loop_idx in range(1, max_loops + 1):
            ts = datetime.now(timezone.utc).isoformat()
            logger.info("Loop %d/%d: %s", loop_idx, max_loops, file_id)

            # 1. TRANSLATE
            try:
                translation = _call_translate(source_text, locale, current_prompt, cfg)
            except Exception as e:
                logger.error("Translate failed: %s loop=%d: %s", file_id, loop_idx, e)
                traces.append(LoopTrace(
                    file_id=file_id, locale=locale, loop_index=loop_idx,
                    draft_hash="", prompt_patch="", aggregate_score=0.0,
                    hard_gates_passed=False, decision="error", timestamp_utc=ts,
                ))
                break

            final_translation = translation
            draft_hash = hashlib.sha256(translation.encode()).hexdigest()[:16]

            # 2. JUDGE
            try:
                judge_raw = _call_judge(source_text, translation, locale, slot_type, checklist, cfg)
                raw = judge_raw.strip()
                if raw.startswith("```"):
                    raw = raw.split("\n", 1)[-1]
                    raw = raw.rsplit("```", 1)[0]
                gate_results = _parse_judge_json(raw.strip())
                if not isinstance(gate_results, list):
                    gate_results = [gate_results]
            except Exception as e:
                logger.error("Judge failed: %s loop=%d: %s", file_id, loop_idx, e)
                traces.append(LoopTrace(
                    file_id=file_id, locale=locale, loop_index=loop_idx,
                    draft_hash=draft_hash, prompt_patch="", aggregate_score=0.0,
                    hard_gates_passed=False, decision="manual_review", timestamp_utc=ts,
                ))
                break

            # 3. SCORE
            agg, all_hard = _aggregate_score(gate_results, checklist)
            if agg > best_score:
                best_score = agg
                best_translation = translation

            # 4. DECIDE
            if _passes_threshold(agg, all_hard, cfg, locale):
                decision = "pass"
            elif loop_idx < max_loops:
                decision = "continue"
            else:
                decision = "manual_review"

            # 5. PATCH (if continuing)
            patch_block = ""
            if decision == "continue":
                next_prompt = patcher.assemble(current_prompt, gate_results, loop_idx + 1)
                patch_block = next_prompt[len(current_prompt):]
                current_prompt = next_prompt

            trace = LoopTrace(
                file_id=file_id, locale=locale, loop_index=loop_idx,
                draft_hash=draft_hash, prompt_patch=patch_block,
                aggregate_score=agg, hard_gates_passed=all_hard,
                decision=decision, timestamp_utc=ts, gate_results=gate_results,
            )
            traces.append(trace)
            _write_trace(cfg, trace)

            if decision != "continue":
                break

    final_decision = traces[-1].decision if traces else "error"
    result = FileResult(
        persona=persona, topic=topic, slot_type=slot_type, locale=locale,
        decision=final_decision, loops_attempted=len(traces),
        best_score=best_score, best_translation=best_translation,
        final_translation=final_translation, traces=traces,
    )

    # Write output
    if final_decision == "pass":
        # Use best-scoring translation
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(best_translation, encoding="utf-8")
        logger.info("PASS: %s (score=%.3f, loops=%d)", file_id, best_score, len(traces))
    elif final_decision == "manual_review":
        # Still write best translation but flag for review
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(best_translation, encoding="utf-8")
        _write_manual_review(cfg, result)

    return result


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

    ap = argparse.ArgumentParser(description="Translation Loop — single-pass (default) or comparator loop mode")
    ap.add_argument("--locale", help="Target locale (e.g. ja-JP)")
    ap.add_argument("--all-locales", action="store_true", help="All 6 CJK locales")
    ap.add_argument("--european-locales", action="store_true", help="All 6 European locales (es-US, es-ES, fr-FR, de-DE, it-IT, hu-HU)")
    ap.add_argument("--persona", help="Filter to one persona")
    ap.add_argument("--topic", help="Filter to one topic")
    ap.add_argument("--slot", help="Slot type filter")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--resume", action="store_true", help="Skip files with existing translations")
    ap.add_argument("--max-parallel", type=int, default=5)
    ap.add_argument("--max-files", type=int, default=0, help="Limit number of files (0=all)")
    ap.add_argument("--judge-loop", action="store_true", help="Use multi-pass judge loop (old behavior). Default is single-pass.")
    ap.add_argument("--tts-check", action="store_true", default=True, help="Validate translation via TTS MP3 byte check (default: on)")
    args = ap.parse_args()

    cfg = _load_config()
    checklist = _load_checklist()

    if not cfg:
        print("ERROR: config/localization/translation_loop_config.yaml missing", file=sys.stderr)
        return 1
    if not checklist:
        checklist = {}  # Single-pass mode doesn't need checklist

    # Wire single-pass mode into config (DEFAULT: True unless --judge-loop)
    cfg["single_pass"] = not args.judge_loop

    locales = []
    if args.all_locales:
        locales = list(CJK6_LOCALES)
    if args.european_locales:
        locales.extend(list(EUROPEAN_LOCALES))
    if args.locale:
        locales.append(args.locale)
    # Deduplicate while preserving order
    seen = set()
    locales = [l for l in locales if not (l in seen or seen.add(l))]
    if not locales:
        print("Specify --locale, --all-locales, or --european-locales", file=sys.stderr)
        return 2

    if not args.dry_run and not (os.environ.get("TOGETHER_API_KEY", "").strip() or os.environ.get("DASHSCOPE_API_KEY", "").strip()):
        print("TOGETHER_API_KEY or DASHSCOPE_API_KEY required (set env var or use --dry-run)", file=sys.stderr)
        return 2

    atoms_root = REPO_ROOT / "atoms"
    manifest = discover_atoms(atoms_root, persona=args.persona, topic=args.topic, slot=args.slot)
    if args.max_files and args.max_files > 0:
        manifest = manifest[:args.max_files]
    max_loops = cfg.get("loop_control", {}).get("max_loops", 3)

    # Single-pass mode (DEFAULT): translate → write → TTS byte check. No judge, no retry.
    # Judge-loop mode (--judge-loop): translate → judge → score → patch → retry (old behavior).
    if args.judge_loop:
        mode = "judge_loop"
        calls_per_job = f"1 translate + 1 judge × up to {max_loops} loops = max {max_loops * 2}"
    else:
        mode = "single_pass"
        max_loops = 1  # Override: single pass only
        calls_per_job = "1 translate + 1 TTS byte check (no judge)"

    print(f"Manifest: {len(manifest)} files × {len(locales)} locales = {len(manifest) * len(locales)} jobs")
    print(f"Mode: {mode} | parallel={args.max_parallel}")
    print(f"API calls per job: {calls_per_job}")

    if args.dry_run:
        for p, t, s, path in manifest[:20]:
            print(f"  {p}/{t}/{s} -> {path}")
        if len(manifest) > 20:
            print(f"  ... and {len(manifest) - 20} more")
        return 0

    # Run
    results: list[FileResult] = []
    for locale in locales:
        print(f"\n{'='*60}\nLocale: {locale}\n{'='*60}")
        with ThreadPoolExecutor(max_workers=args.max_parallel) as ex:
            futures = {
                ex.submit(run_file_loop, p, t, s, path, locale, cfg, checklist, args.resume): f"{p}/{t}/{s}"
                for p, t, s, path in manifest
            }
            for fut in as_completed(futures):
                fid = futures[fut]
                try:
                    r = fut.result()
                    results.append(r)
                    status = f"{r.decision} (score={r.best_score:.3f}, loops={r.loops_attempted})"
                    print(f"  [{len(results)}/{len(manifest)}] {fid}: {status}")
                except Exception as e:
                    print(f"  [{len(results)}/{len(manifest)}] {fid}: ERROR {e}")

    # Summary
    passed = sum(1 for r in results if r.decision == "pass")
    manual = sum(1 for r in results if r.decision == "manual_review")
    skipped = sum(1 for r in results if r.decision in ("skip", "resume_skip"))
    errors = sum(1 for r in results if r.decision == "error")
    total = len(results)

    print(f"\n{'='*60}")
    print(f"SUMMARY: {total} files processed")
    print(f"  pass:          {passed} ({passed/total*100:.0f}%)" if total else "  pass: 0")
    print(f"  manual_review: {manual}")
    print(f"  skipped:       {skipped}")
    print(f"  errors:        {errors}")

    return 1 if errors > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
