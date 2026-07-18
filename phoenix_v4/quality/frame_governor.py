"""
Frame governance: somatic-first vs spiritual-first language balance.
Phrase-list detection (no LLM). v2 applies policy actions from frame_registry.yaml:
warn_only | soften_in_place | strip_sentence | hard_fail.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
FRAME_REGISTRY_PATH = REPO_ROOT / "config" / "source_of_truth" / "frame_registry.yaml"

ABSOLUTE_CLAIM_PATTERNS: tuple[str, ...] = (
    r"every\s+organ",
    r"disease\s+is",
    r"love\s+melts\s+all",
    r"\bkarma\b",
    r"frequency\s+of",
    r"vibration\s+of",
    r"soul\s+contract",
)
_ABSOLUTE_RES = tuple(re.compile(p, re.IGNORECASE) for p in ABSOLUTE_CLAIM_PATTERNS)

SPIRITUAL_LEXICON: tuple[str, ...] = (
    "soul contract",
    "past life",
    "karma",
    "chakra",
    "frequency",
    "vibration",
    "akashic",
    "ascension",
    "manifestation",
    "energy field",
    "aura",
    "divine timing",
    "cosmic",
    "sacred geometry",
    "light body",
)

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def _line_has_spiritual(line: str) -> bool:
    low = line.lower()
    return any(tok in low for tok in SPIRITUAL_LEXICON)


@dataclass
class FrameEnforcementContext:
    """Per-chapter runtime context for policy resolution."""

    chapter_index: int
    frame: str
    doctrine_chapter: bool = False
    allow_early_spiritual: bool = False
    emotional_job: str = ""


@dataclass
class FrameGovernanceResult:
    violations: list[dict[str, Any]] = field(default_factory=list)
    spiritual_density: float = 0.0
    frame_compliant: bool = True
    softened_sentences: list[dict[str, Any]] = field(default_factory=list)
    stripped_sentences: list[dict[str, Any]] = field(default_factory=list)
    hard_fail_reasons: list[str] = field(default_factory=list)


class FrameGovernanceHardFail(Exception):
    """Raised when a violation type is configured with hard_fail."""

    def __init__(self, reasons: list[str]) -> None:
        self.reasons = reasons
        super().__init__(reasons[0] if reasons else "frame governance hard fail")


def load_frame_registry(path: Optional[Path] = None) -> dict[str, Any]:
    p = path or FRAME_REGISTRY_PATH
    if not p.exists() or yaml is None:
        return {}
    try:
        return yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def _gv2(registry: dict[str, Any]) -> dict[str, Any]:
    return (registry or {}).get("governance_v2") or {}


def _resolve_action(
    violation_type: str,
    ctx: FrameEnforcementContext,
    registry: dict[str, Any],
) -> str:
    pol = (_gv2(registry).get("violation_policies") or {}).get(violation_type) or {}
    if violation_type == "spiritual_before_entry_chapter" and ctx.allow_early_spiritual:
        return str(pol.get("allow_early_spiritual_contract") or pol.get("default") or "warn_only")
    if ctx.doctrine_chapter and "doctrine_chapter" in pol:
        return str(pol["doctrine_chapter"])
    return str(pol.get("default") or "warn_only")


def _hard_fail_types(registry: dict[str, Any]) -> set[str]:
    raw = _gv2(registry).get("hard_fail_violation_types") or []
    return {str(x) for x in raw}


def _effective_density_max(ctx: FrameEnforcementContext, frame_registry: dict[str, Any]) -> float:
    frames = frame_registry.get("frames") or {}
    cfg = frames.get(ctx.frame) or frames.get("somatic_first") or {}
    base = float(cfg.get("spiritual_density_max") or 1.0)
    if ctx.doctrine_chapter:
        alt = cfg.get("doctrine_chapter_spiritual_density_max")
        if alt is not None:
            return max(base, float(alt))
    return base


def _compute_spiritual_density(text: str) -> tuple[float, int, int]:
    if not (text or "").strip():
        return 0.0, 0, 1
    lines = text.splitlines()
    total_words = max(len(text.split()), 1)
    spiritual_word_weight = 0
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        wc = len(stripped.split())
        if _line_has_spiritual(stripped):
            spiritual_word_weight += wc
    return min(1.0, spiritual_word_weight / float(total_words)), spiritual_word_weight, total_words


def _detect_violations(
    text: str,
    ctx: FrameEnforcementContext,
    frame_registry: dict[str, Any],
    *,
    for_compliance: bool,
) -> list[dict[str, Any]]:
    """Detect frame issues. When for_compliance, skip classes policy treats as allowed (doctrine / contract)."""
    violations: list[dict[str, Any]] = []
    if not (text or "").strip():
        return violations

    if ctx.frame == "spiritual_first":
        return violations

    frames = frame_registry.get("frames") or {}
    cfg = frames.get(ctx.frame) or frames.get("somatic_first") or {}
    spiritual_min = int(cfg.get("spiritual_entry_chapter_min") or 0)
    ban_absolutes = bool(cfg.get("absolute_claim_ban", False))
    density_max = _effective_density_max(ctx, frame_registry)

    lines = text.splitlines()
    for lineno, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped:
            continue

        if ban_absolutes and not ctx.doctrine_chapter:
            for rx in _ABSOLUTE_RES:
                if rx.search(stripped):
                    violations.append(
                        {
                            "type": "absolute_claim",
                            "pattern": rx.pattern,
                            "line": lineno,
                            "excerpt": stripped[:120],
                        }
                    )

        if _line_has_spiritual(stripped):
            if ctx.chapter_index < spiritual_min:
                if not ctx.doctrine_chapter and not ctx.allow_early_spiritual:
                    violations.append(
                        {
                            "type": "spiritual_before_entry_chapter",
                            "line": lineno,
                            "detail": f"spiritual lexicon before chapter_index >= {spiritual_min}",
                            "excerpt": stripped[:120],
                        }
                    )

    spiritual_density, _, _ = _compute_spiritual_density(text)
    if spiritual_density > density_max + 1e-6:
        violations.append(
            {
                "type": "spiritual_density",
                "detail": f"density {spiritual_density:.3f} > max {density_max:.3f}",
            }
        )

    if not for_compliance:
        return violations

    # Residual strict check: density still applies under effective cap; absolutes/spiritual-before already gated
    return violations


def frame_governance_check(
    text: str,
    frame: str,
    chapter_index: int,
    frame_registry: dict[str, Any],
    *,
    doctrine_chapter: bool = False,
    allow_early_spiritual: bool = False,
    emotional_job: str = "",
) -> FrameGovernanceResult:
    """
    Warn-only analysis on raw text (no mutation). Respects doctrine chapter and
    allow_early_spiritual for compliance-style evaluation.
    """
    ctx = FrameEnforcementContext(
        chapter_index=chapter_index,
        frame=frame,
        doctrine_chapter=doctrine_chapter,
        allow_early_spiritual=allow_early_spiritual,
        emotional_job=emotional_job,
    )
    if not frame_registry:
        return FrameGovernanceResult(frame_compliant=True)

    violations = _detect_violations(text, ctx, frame_registry, for_compliance=True)
    spiritual_density, _, _ = _compute_spiritual_density(text)
    return FrameGovernanceResult(
        violations=violations,
        spiritual_density=spiritual_density,
        frame_compliant=len(violations) == 0,
    )


def _split_sentences(fragment: str) -> list[str]:
    if not (fragment or "").strip():
        return []
    parts = [s.strip() for s in _SENTENCE_SPLIT.split(fragment.strip()) if s.strip()]
    return parts if parts else [fragment.strip()]


def _soften_with_lexicon(sentence: str, lex_map: dict[str, str]) -> tuple[str, list[str]]:
    out = sentence
    applied: list[str] = []
    low = out.lower()
    # Longer keys first to prefer multi-word replacements
    for key in sorted(lex_map.keys(), key=len, reverse=True):
        if key.lower() in low:
            repl = lex_map[key]
            out = re.sub(re.escape(key), repl, out, flags=re.IGNORECASE)
            low = out.lower()
            applied.append(key)
    return out, applied


def _soften_absolute_sentence(sentence: str, softeners: list[dict[str, Any]]) -> tuple[str, bool]:
    out = sentence
    changed = False
    for block in softeners:
        pat = block.get("pattern_regex")
        repl = block.get("replacement")
        if not pat or repl is None:
            continue
        try:
            nout, n = re.subn(pat, str(repl), out, flags=re.IGNORECASE)
        except re.error:
            continue
        if n:
            out = nout
            changed = True
    return out, changed


def apply_frame_enforcement(
    text: str,
    ctx: FrameEnforcementContext,
    frame_registry: dict[str, Any],
) -> tuple[str, FrameGovernanceResult]:
    """
    Apply v2 policies when governance_v2.enabled; otherwise return text unchanged
    and run frame_governance_check-equivalent telemetry on the original string.
    """
    if ctx.frame == "spiritual_first" or not (text or "").strip():
        return text, FrameGovernanceResult(frame_compliant=True)

    if not frame_registry:
        return text, FrameGovernanceResult(frame_compliant=True)

    gv2 = _gv2(frame_registry)
    if not gv2.get("enabled", False):
        chk = frame_governance_check(
            text,
            ctx.frame,
            ctx.chapter_index,
            frame_registry,
            doctrine_chapter=ctx.doctrine_chapter,
            allow_early_spiritual=ctx.allow_early_spiritual,
            emotional_job=ctx.emotional_job,
        )
        return text, chk

    hf_types = _hard_fail_types(frame_registry)
    absolute_softeners = list(gv2.get("absolute_softeners") or [])
    lex_map = {str(k): str(v) for k, v in (gv2.get("lexicon_softeners") or {}).items()}

    softened: list[dict[str, Any]] = []
    stripped: list[dict[str, Any]] = []
    hard_fail_reasons: list[str] = []
    warn_violations: list[dict[str, Any]] = []

    lines = text.splitlines(keepends=False)
    out_lines: list[str] = []

    frames = frame_registry.get("frames") or {}
    cfg = frames.get(ctx.frame) or frames.get("somatic_first") or {}
    spiritual_min = int(cfg.get("spiritual_entry_chapter_min") or 0)
    ban_absolutes = bool(cfg.get("absolute_claim_ban", False))

    for lineno, line in enumerate(lines, start=1):
        if not line.strip():
            out_lines.append(line)
            continue

        sentences = _split_sentences(line)
        new_sents: list[str] = []
        for sent in sentences:
            current = sent

            # --- absolute claims (first matching pattern wins) ---
            abs_rx = None
            if ban_absolutes:
                for rx in _ABSOLUTE_RES:
                    if rx.search(current):
                        abs_rx = rx
                        break
            if abs_rx is not None:
                action = _resolve_action("absolute_claim", ctx, frame_registry)
                if "absolute_claim" in hf_types and action == "hard_fail":
                    raise FrameGovernanceHardFail(
                        [
                            f"chapter {ctx.chapter_index + 1} line {lineno}: "
                            f"absolute_claim / {abs_rx.pattern}"
                        ]
                    )
                if action == "hard_fail":
                    raise FrameGovernanceHardFail(
                        [
                            f"chapter {ctx.chapter_index + 1} line {lineno}: "
                            f"absolute_claim policy=hard_fail"
                        ]
                    )
                if action == "warn_only":
                    warn_violations.append(
                        {
                            "type": "absolute_claim",
                            "pattern": abs_rx.pattern,
                            "line": lineno,
                            "excerpt": current[:120],
                        }
                    )
                    new_sents.append(current)
                    continue
                if action == "strip_sentence":
                    stripped.append(
                        {
                            "chapter_index": ctx.chapter_index,
                            "line": lineno,
                            "type": "absolute_claim",
                            "pattern": abs_rx.pattern,
                            "original": current[:240],
                        }
                    )
                    continue
                if action == "soften_in_place":
                    before = current
                    current, did = _soften_absolute_sentence(current, absolute_softeners)
                    if did:
                        softened.append(
                            {
                                "chapter_index": ctx.chapter_index,
                                "line": lineno,
                                "type": "absolute_claim",
                                "before": before[:240],
                                "after": current[:240],
                            }
                        )
                    else:
                        warn_violations.append(
                            {
                                "type": "absolute_claim",
                                "pattern": abs_rx.pattern,
                                "line": lineno,
                                "excerpt": current[:120],
                                "note": "soften_in_place had no matching softener; sentence kept",
                            }
                        )
                    new_sents.append(current)
                    continue

            # --- spiritual before entry chapter ---
            if (
                ctx.chapter_index < spiritual_min
                and _line_has_spiritual(current)
                and not ctx.doctrine_chapter
                and not ctx.allow_early_spiritual
            ):
                action = _resolve_action("spiritual_before_entry_chapter", ctx, frame_registry)
                if "spiritual_before_entry_chapter" in hf_types and action == "hard_fail":
                    raise FrameGovernanceHardFail(
                        [f"chapter {ctx.chapter_index + 1} line {lineno}: spiritual_before_entry_chapter"]
                    )
                if action == "hard_fail":
                    raise FrameGovernanceHardFail(
                        [f"chapter {ctx.chapter_index + 1} line {lineno}: spiritual_before_entry hard_fail"]
                    )
                if action == "warn_only":
                    warn_violations.append(
                        {
                            "type": "spiritual_before_entry_chapter",
                            "line": lineno,
                            "excerpt": current[:120],
                        }
                    )
                elif action == "strip_sentence":
                    stripped.append(
                        {
                            "chapter_index": ctx.chapter_index,
                            "line": lineno,
                            "type": "spiritual_before_entry_chapter",
                            "original": current[:240],
                        }
                    )
                    continue
                elif action == "soften_in_place":
                    before = current
                    current, keys = _soften_with_lexicon(current, lex_map)
                    if keys:
                        softened.append(
                            {
                                "chapter_index": ctx.chapter_index,
                                "line": lineno,
                                "type": "spiritual_before_entry_chapter",
                                "keys": keys,
                                "before": before[:240],
                                "after": current[:240],
                            }
                        )
                    else:
                        warn_violations.append(
                            {
                                "type": "spiritual_before_entry_chapter",
                                "line": lineno,
                                "excerpt": current[:120],
                                "note": "no lexicon_softeners matched; sentence kept",
                            }
                        )

            new_sents.append(current)

        rebuilt = " ".join(s for s in new_sents if s.strip())
        out_lines.append(rebuilt if rebuilt.strip() else "")

    out_text = "\n".join(out_lines)

    # spiritual_density: warn_only / hard_fail only (no automatic strip of density)
    density_max = _effective_density_max(ctx, frame_registry)
    spiritual_density, _, _ = _compute_spiritual_density(out_text)
    if spiritual_density > density_max + 1e-6:
        action = _resolve_action("spiritual_density", ctx, frame_registry)
        detail = f"density {spiritual_density:.3f} > max {density_max:.3f}"
        if action == "hard_fail" or "spiritual_density" in hf_types:
            raise FrameGovernanceHardFail(
                [f"chapter block {ctx.chapter_index + 1}: spiritual_density {detail}"]
            )
        if action == "warn_only":
            warn_violations.append({"type": "spiritual_density", "detail": detail})

    residual = _detect_violations(out_text, ctx, frame_registry, for_compliance=True)
    if _resolve_action("spiritual_density", ctx, frame_registry) == "warn_only":
        residual = [x for x in residual if x.get("type") != "spiritual_density"]
    frame_compliant = len(residual) == 0 and len(hard_fail_reasons) == 0

    return out_text, FrameGovernanceResult(
        violations=warn_violations + residual,
        spiritual_density=spiritual_density,
        frame_compliant=frame_compliant,
        softened_sentences=softened,
        stripped_sentences=stripped,
        hard_fail_reasons=hard_fail_reasons,
    )
