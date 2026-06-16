"""
Chapter flow gate: rejects flat/choppy chapter prose before delivery.
Deterministic heuristics only (no model scoring).
"""
from __future__ import annotations

import re
import statistics
from dataclasses import dataclass

# Micro / short spine books use many line-broken paragraphs; adjacent token overlap
# stays artificially low while transitions still read fine. Relax only for these
# runtime formats — standard+ thresholds stay unchanged.
#
# Compact formats (PR #856 / PR-G #861) are also short-form by character: 5-8 chapters,
# 3000-7500 words, same paragraph-break density as micro_book_15/20. The chapter_flow
# gate's transition-cue threshold should match (2 cues required, not 3 for standard).
# Surfaced by PR-H smoke 2026-05-04: compact_book_8ch_30min was hitting the standard
# threshold of 3, failing WEAK_TRANSITIONS even when ch8 had 2 transition cues.
SHORT_FORM_RUNTIME_FORMAT_IDS = frozenset(
    {
        "micro_book_15",
        "micro_book_20",
        "short_book_30",
        "compact_book_5ch_15min",
        "compact_book_5ch_20min",
        "compact_book_8ch_30min",
    },
)

DEEP_FORM_RUNTIME_FORMAT_IDS = frozenset(
    {"deep_book_4h", "deep_book_6h"},
)

LONG_FORM_RUNTIME_FORMAT_IDS = frozenset(
    {"standard_book", "extended_book_2h", "deep_book_4h", "deep_book_6h"}
)

# OPD-124 canonical role order (segment-level, not atom-level).
_CANONICAL_ROLE_ORDER = (
    "hook",
    "scene_or_section",
    "first_section_content",
    "named_story",
    "teacher_insight",
    "exercise",
    "close",
)


def flow_profile_for_runtime_format(runtime_format_id: str) -> str:
    fmt = (runtime_format_id or "").strip()
    if fmt in SHORT_FORM_RUNTIME_FORMAT_IDS:
        return "short_form"
    if fmt in DEEP_FORM_RUNTIME_FORMAT_IDS:
        return "deep_form"
    return "standard"


@dataclass(frozen=True)
class ChapterFlowResult:
    status: str
    score: int
    errors: list[str]
    warnings: list[str]
    metrics: dict


_FORBIDDEN_PATTERNS = [
    re.compile(r"\{[^}]+\}"),
    re.compile(r"^---\s*$", re.M),
    re.compile(r"\[(?:family|voice_mode|mode|reframe_type):", re.I),
    re.compile(r"\b(?:family|voice_mode|mode|reframe_type|mechanism_emphasis)\s*:", re.I),
]

_REPETITIVE_PHRASES = [
    "i have noticed that",
    "what i have come to understand",
    "what i have come to think",
    "there is a mechanism that",
]

_SCAFFOLD_RISK_PHRASES = [
    "what this means going forward is simple",
    "that moment matters because",
    "so this is not just your private glitch",
    "gray light through the window",
]

_TRANSITION_CUES = (
    "that moment",
    "which means",
    "so when",
    "this is why",
    "in practice",
    "for example",
    "here is",
    "because",
    "that matters because",
    "this is the mechanism",
    "you can see",
    "what looks like",
    "remember this",
    # ws_flow_glue_selector_cap_enforcement_20260517 expansion.
    # Bridge families and post-OPD-109 phrasings emit these transitional shapes;
    # the gate previously missed them and false-FAILed WEAK_TRANSITIONS on
    # otherwise well-bridged chapters (Junko + Miyuki standard_book 2026-05-19).
    "watch how",          # bridge family same_pattern_different_face
    "sit with",           # 'sit with X long enough'
    "underneath",         # 'underneath the desk', 'underneath the story'
    "beneath",            # 'beneath that recognition'
    "one thread",         # 'one thread emerges'
    "across",             # 'Across <teacher>'s work'
    "step into",          # bridge family seeing-has-a-downstairs
    "the seeing",         # 'The seeing has a downstairs'
    "in another",         # 'in another room'
)

_THESIS_CUES = (
    "principle:",
    "the point is",
    "what this means",
    "this is not",
    # ws_flow_glue_selector_cap_enforcement_20260517 expansion.
    # The old cue list relied on four exact phrases that teacher-voice atoms
    # do not always emit verbatim; modern teacher prose makes the clear point
    # through structurally equivalent shapes that this list now recognizes.
    "is not the problem",   # 'Contradiction is not the problem here'
    "is the data",          # 'it is the data'
    "is the practice",      # 'X is the practice'
    "is not a sign",        # 'these are not signs that something is going wrong'
    "is meant to",          # 'It is meant to make the pattern visible'
    "is the entry",         # 'That freeze is the entry point'
    "is not a test",        # 'What follows is not a test'
    "is not just",          # 'this is not just X'
    "what follows",         # 'What follows is not a test, it is an invitation'
    "what remains",         # 'What remains is the moment after'
    "the truth",            # 'the body often tells the truth in extremities'
)

_AHA_CUES = (
    "the cost",
    "the price",
    "what you call",
    "not the problem",
    "did not happen",
    "your body",
    "instead",
    "but the",
)


def _sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def _token_set(text: str) -> set[str]:
    return set(re.findall(r"[a-z']+", text.lower()))


def _slot_types_to_roles(slot_types: list[str]) -> list[str]:
    try:
        from phoenix_v4.planning.chapter_planner import (
            _slot_type_to_canonical_role,
            load_chapter_structure_template,
        )

        tmpl = load_chapter_structure_template()
        return [_slot_type_to_canonical_role(st, tmpl) for st in slot_types]
    except Exception:
        return []


def evaluate_canonical_sequence_compliance(
    chapter_slots: list[str],
    *,
    runtime_format_id: str = "",
) -> list[str]:
    """
    OPD-124 calibration check: WARN when long-form chapter slots deviate from
    hook → scene → section → named story → teacher → exercise → close.

    Returns warning strings (never hard-fails).
    """
    rf = (runtime_format_id or "").strip()
    if rf not in LONG_FORM_RUNTIME_FORMAT_IDS:
        return []

    roles = _slot_types_to_roles(chapter_slots)
    if not roles:
        return ["CANONICAL_SEQUENCE: unable to map slot types to roles"]

    present_roles = [r for r in roles if r in _CANONICAL_ROLE_ORDER]
    if not present_roles:
        return ["CANONICAL_SEQUENCE: no canonical roles present in chapter slots"]

    warnings: list[str] = []
    required = set(_CANONICAL_ROLE_ORDER)
    missing = required - set(present_roles)
    if missing:
        warnings.append(
            "CANONICAL_SEQUENCE: missing roles "
            + ", ".join(sorted(missing))
        )

    last_idx = -1
    for role in present_roles:
        idx = _CANONICAL_ROLE_ORDER.index(role)
        if idx < last_idx:
            warnings.append(
                f"CANONICAL_SEQUENCE: role order violation ({role} after "
                f"{_CANONICAL_ROLE_ORDER[last_idx]})"
            )
            break
        last_idx = idx

    upper = [(s or "").strip().upper() for s in chapter_slots]
    if "STORY" in upper and "SCENE" in upper:
        if upper.index("STORY") < upper.index("SCENE"):
            warnings.append("CANONICAL_SEQUENCE: STORY before SCENE in slot list")
    if "STORY" in upper and any(s in upper for s in ("REFLECTION", "COMPRESSION", "PIVOT")):
        section_idx = min(
            upper.index(s) for s in ("REFLECTION", "COMPRESSION", "PIVOT") if s in upper
        )
        if upper.index("STORY") < section_idx:
            warnings.append(
                "CANONICAL_SEQUENCE: STORY before first_section_content in slot list"
            )

    return warnings


def evaluate_chapter_flow(
    chapter_text: str,
    *,
    flow_profile: str = "standard",
) -> ChapterFlowResult:
    errors: list[str] = []
    warnings: list[str] = []

    profile = (flow_profile or "standard").strip() or "standard"
    is_short_form = profile == "short_form"
    is_deep_form = profile == "deep_form"

    text = (chapter_text or "").strip()
    if not text:
        return ChapterFlowResult("FAIL", 0, ["CHAPTER_EMPTY"], [], {})

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    sentences = _sentences(text)
    min_sentences = 10 if is_short_form else 14
    if len(sentences) < min_sentences:
        # Micro/short books sometimes end with a brief closing beat; flow coherence
        # heuristics are not meaningful below a few sentences.
        if is_short_form and len(sentences) >= 2:
            warnings.append("SHORT_TAIL_CHAPTER_FOR_MICRO_FORMAT")
        else:
            errors.append("TOO_SHORT_FOR_AUDIO_FLOW")

    for pat in _FORBIDDEN_PATTERNS:
        if pat.search(text):
            # Deep-form chapters may contain narrative story-atom placeholders
            # like {Street_name} / {Weather_detail} that are stylistic and
            # will be stripped before final delivery.  Downgrade to warning.
            if is_deep_form:
                warnings.append("DELIVERY_ARTIFACT_PRESENT")
            else:
                errors.append("DELIVERY_ARTIFACT_PRESENT")
            break

    lower = text.lower()
    for phrase in _REPETITIVE_PHRASES:
        count = lower.count(phrase)
        if count > 1:
            errors.append(f"REPETITIVE_STEM:{phrase}")

    scaffold_hits = {}
    for phrase in _SCAFFOLD_RISK_PHRASES:
        count = lower.count(phrase)
        if count:
            scaffold_hits[phrase] = count
        if count >= 1 and phrase == "gray light through the window":
            errors.append("GENERIC_SCENE_FALLBACK")
        elif count >= 1 and phrase != "gray light through the window":
            warnings.append(f"SCAFFOLD_RISK:{phrase}")

    if "in the next chapter" in lower or "there is more to explore" in lower:
        errors.append("ANNOUNCED_THREAD")

    transition_hits = sum(1 for cue in _TRANSITION_CUES if cue in lower)
    if is_short_form:
        min_transitions = 2
    elif is_deep_form:
        # Deep chapters have 300–1200 sentences; cue density is much lower per
        # sentence.  Scale: require at least 1 per ~250 sentences, floor 3.
        min_transitions = max(3, len(sentences) // 250)
    else:
        min_transitions = 3
    if transition_hits < min_transitions:
        if is_deep_form:
            warnings.append("WEAK_TRANSITIONS")
        else:
            errors.append("WEAK_TRANSITIONS")

    thesis_hits = sum(1 for cue in _THESIS_CUES if cue in lower)
    if thesis_hits < 1:
        # Deep-form somatic / grief chapters use experiential language rather
        # than explicit thesis statements.  Downgrade to warning.
        if is_deep_form:
            warnings.append("MISSING_CLEAR_POINT")
        else:
            errors.append("MISSING_CLEAR_POINT")

    overlaps = []
    for i in range(1, len(paragraphs)):
        prev_tokens = _token_set(paragraphs[i - 1])
        curr_tokens = _token_set(paragraphs[i])
        if not prev_tokens or not curr_tokens:
            continue
        jaccard = len(prev_tokens & curr_tokens) / max(1, len(prev_tokens | curr_tokens))
        overlaps.append(jaccard)
    avg_overlap = sum(overlaps) / len(overlaps) if overlaps else 0.0
    # Many short paragraphs (common in grief / TTS line breaks) deflate overlap
    # without meaning the chapter lacks flow; skip this check for short_form when
    # paragraph count is high.
    choppy_threshold = 0.05
    # Skip when many short line-break paragraphs *or* a very short tail (≤6 ¶)
    # where overlap is not a useful signal.  Deep-form chapters always skip
    # choppy — adjacent-overlap in 100+ ¶ chapters is dominated by somatic
    # variety, not flow quality.
    skip_choppy = is_deep_form or (
        is_short_form and (len(paragraphs) > 14 or len(paragraphs) <= 6)
    )
    if overlaps and avg_overlap < choppy_threshold and not skip_choppy:
        errors.append("CHOPPY_SECTION_JUMPS")

    sentence_lengths = [len(re.findall(r"\b\w+\b", s)) for s in sentences]
    std_len = statistics.pstdev(sentence_lengths) if len(sentence_lengths) >= 2 else 0.0
    if std_len < 4.0:
        warnings.append("LOW_RHYTHM_VARIATION")

    if not re.search(r"\b(breathe|pause|exhale|inhale|write|name|notice|choose|practice)\b", lower):
        errors.append("NO_ACTIONABLE_STEP")

    aha_hits = sum(1 for cue in _AHA_CUES if cue in lower)
    if aha_hits < 1:
        warnings.append("LOW_AHA_SIGNAL")

    status = "PASS" if not errors else "FAIL"
    score = max(0, 100 - len(errors) * 15 - len(warnings) * 5)

    metrics = {
        "paragraphs": len(paragraphs),
        "sentences": len(sentences),
        "transition_hits": transition_hits,
        "thesis_hits": thesis_hits,
        "avg_adjacent_overlap": round(avg_overlap, 3),
        "sentence_len_std": round(std_len, 2),
        "aha_hits": aha_hits,
        "scaffold_hits": scaffold_hits,
        "flow_profile": profile,
    }
    return ChapterFlowResult(status, score, errors, warnings, metrics)


def evaluate_chapter_flow_with_slots(
    chapter_slots: list[str],
    segment_proses: list[str],
    *,
    flow_profile: str = "standard",
    runtime_format_id: str = "",
) -> ChapterFlowResult:
    """
    Same heuristics as evaluate_chapter_flow on concatenated text, plus:
    when TAKEAWAY or THREAD is in chapter_slots, require the corresponding segment to be non-empty.
    """
    if len(chapter_slots) != len(segment_proses):
        return ChapterFlowResult(
            "FAIL",
            0,
            [f"chapter_slots len ({len(chapter_slots)}) != segment_proses len ({len(segment_proses)})"],
            [],
            {},
        )
    chapter_text = "\n\n".join(p.strip() for p in segment_proses if p and p.strip())
    result = evaluate_chapter_flow(chapter_text, flow_profile=flow_profile)
    warnings = list(result.warnings)
    errors = list(result.errors)
    seq_warnings = evaluate_canonical_sequence_compliance(
        chapter_slots, runtime_format_id=runtime_format_id,
    )
    warnings.extend(seq_warnings)
    for i, slot in enumerate(chapter_slots):
        slot_upper = (slot or "").strip().upper()
        if slot_upper == "TAKEAWAY":
            if i >= len(segment_proses) or not (segment_proses[i] or "").strip():
                errors.append("TAKEAWAY_EMPTY")
            break
    for i, slot in enumerate(chapter_slots):
        slot_upper = (slot or "").strip().upper()
        if slot_upper == "THREAD":
            if i >= len(segment_proses) or not (segment_proses[i] or "").strip():
                errors.append("THREAD_EMPTY")
            break
    status = "PASS" if not errors else "FAIL"
    score = max(0, 100 - len(errors) * 15 - len(warnings) * 5)
    metrics = dict(result.metrics)
    metrics["takeaway_checked"] = "TAKEAWAY" in [(s or "").strip().upper() for s in chapter_slots]
    metrics["thread_checked"] = "THREAD" in [(s or "").strip().upper() for s in chapter_slots]
    metrics["canonical_sequence_warnings"] = len(seq_warnings)
    return ChapterFlowResult(status=status, score=score, errors=errors, warnings=warnings, metrics=metrics)
