"""
Register gate — catches F1-F8 failure modes the existing structural gates miss.

Closes the loop between Layer 1 (machine gates pass) and Layer 3 (Pearl_Editor
ONTGP read). Per `docs/PEARL_PRIME_REGISTER_GATE_SPEC.md` and calibrated against
`artifacts/qa/ACCEPTANCE_VERDICT_2hr_ahjan_genz_anxiety_2026-05-18.md`.

Deterministic heuristics only (no model scoring; no LLM API calls — CLAUDE.md Tier policy).

F1: templated paragraph cosine-similarity ≥ 0.75 → WARN/FAIL
F2: broken slot-template fragments → HARD_FAIL (renderer artifact)
F3: per-teacher off-doctrine vocabulary → WARN-per-chapter, FAIL at 3+ distinct tokens
F4: verbatim closing-line repetition across chapters → WARN/FAIL
F5: named-character continuity discontinuity → WARN on per-chapter rotation
F6: pedagogical-cadence 4-gram repetition → WARN/FAIL
F7: over-prescribed practice density per chapter → WARN/FAIL
F8: citation grafting → deferred until anchor corpus lands (artifacts/reference/trade_pub_anchors/)

Verdicts:
  PASS         — 0 FAIL, 0 WARN
  ADVISORY     — 0 FAIL, ≤ 2 WARN
  WARN         — 0 FAIL, ≥ 3 WARN
  FAIL         — ≥ 1 FAIL
  HARD_FAIL    — any F2 violation (renderer artifact; never ship)
"""
from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

import yaml


# ─────────────────────────────────────────────────────────────────────────────
# Data classes
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class RegisterFinding:
    failure_id: str         # F1..F8
    severity: str           # WARN / FAIL / HARD_FAIL
    chapter: Optional[int]  # 1-indexed; None for book-level findings
    summary: str            # short human description
    evidence: dict          # detector-specific fields


@dataclass
class RegisterGateResult:
    verdict: str            # PASS / ADVISORY / WARN / FAIL / HARD_FAIL
    findings: list[RegisterFinding] = field(default_factory=list)
    book_metrics: dict = field(default_factory=dict)
    suggested_lanes: list[str] = field(default_factory=list)

    def to_json(self) -> dict:
        return {
            "verdict": self.verdict,
            "findings": [asdict(f) for f in self.findings],
            "book_metrics": self.book_metrics,
            "suggested_lanes": self.suggested_lanes,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

_CHAPTER_HEADER_RE = re.compile(r"^Chapter\s+(\d+)\s*$", re.MULTILINE)
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def _split_chapters(book_text: str) -> list[tuple[int, str]]:
    """Return list of (chapter_number, chapter_body_text) ordered by appearance."""
    matches = list(_CHAPTER_HEADER_RE.finditer(book_text))
    if not matches:
        return [(0, book_text)]
    chapters: list[tuple[int, str]] = []
    for i, m in enumerate(matches):
        ch_num = int(m.group(1))
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(book_text)
        body = book_text[start:end].strip()
        chapters.append((ch_num, body))
    return chapters


def _split_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def _split_sentences(text: str) -> list[str]:
    parts = _SENTENCE_SPLIT_RE.split(text.strip())
    return [p.strip() for p in parts if p.strip()]


def _word_set(text: str) -> set[str]:
    return set(re.findall(r"[A-Za-z']+", text.lower()))


def _cosine_jaccard(a: set[str], b: set[str]) -> float:
    """Jaccard similarity as a fast proxy for sentence-level cosine."""
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


# ─────────────────────────────────────────────────────────────────────────────
# F1 — Templated paragraph repetition
# ─────────────────────────────────────────────────────────────────────────────

F1_SIMILARITY_THRESHOLD = 0.55  # Jaccard proxy; calibrated lower than spec's 0.75 cosine
F1_MIN_PARA_SENTENCES = 3


def _detect_f1_templated_paragraphs(
    chapters: list[tuple[int, str]],
) -> list[RegisterFinding]:
    """
    Pairwise paragraph similarity within the book. Paragraphs of ≥3 sentences
    that share ≥F1_SIMILARITY_THRESHOLD Jaccard word-set overlap are flagged
    as a near-duplicate template instance.

    Cluster size 1 = no concern; 2 = WARN; 3+ = FAIL.
    """
    paragraphs: list[tuple[int, int, str]] = []  # (ch, para_idx, text)
    for ch_num, ch_text in chapters:
        for pi, para in enumerate(_split_paragraphs(ch_text)):
            sentences = _split_sentences(para)
            if len(sentences) < F1_MIN_PARA_SENTENCES:
                continue
            paragraphs.append((ch_num, pi, para))

    # Build word-sets once
    para_sets = [(loc, _word_set(p)) for loc, p in [((ch, pi), text) for ch, pi, text in paragraphs]]

    clusters: list[list[tuple[int, int]]] = []
    seen: set[int] = set()
    for i, (loc_i, set_i) in enumerate(para_sets):
        if i in seen:
            continue
        cluster: list[tuple[int, int]] = [loc_i]
        for j in range(i + 1, len(para_sets)):
            if j in seen:
                continue
            loc_j, set_j = para_sets[j]
            if _cosine_jaccard(set_i, set_j) >= F1_SIMILARITY_THRESHOLD:
                cluster.append(loc_j)
                seen.add(j)
        if len(cluster) >= 2:
            clusters.append(cluster)
            seen.add(i)

    findings = []
    for ci, cluster in enumerate(clusters):
        if len(cluster) == 2:
            severity = "WARN"
        else:
            severity = "FAIL"
        # Get text excerpt from first paragraph
        first_ch, first_pi = cluster[0]
        excerpt = ""
        for ch, pi, text in paragraphs:
            if ch == first_ch and pi == first_pi:
                excerpt = text[:120] + "..." if len(text) > 120 else text
                break
        findings.append(RegisterFinding(
            failure_id="F1",
            severity=severity,
            chapter=None,  # book-level
            summary=f"templated paragraph cluster size {len(cluster)} (chapters {sorted(set(c for c, _ in cluster))})",
            evidence={
                "cluster_id": f"f1_cluster_{ci:03d}",
                "instances": [{"chapter": c, "para_index": p} for c, p in cluster],
                "excerpt": excerpt,
            },
        ))
    return findings


# ─────────────────────────────────────────────────────────────────────────────
# F2 — Broken slot-template fragments (HARD_FAIL)
# ─────────────────────────────────────────────────────────────────────────────

F2_RULES = {
    "F2.A_colon_period_only": re.compile(r":\s+\.(\s|$)"),
    "F2.B_sentence_end_preposition": re.compile(
        r"\b(with|of|by|to|for|on|in|from|the|a)\.\s*$",
        re.IGNORECASE | re.MULTILINE,
    ),
    "F2.E_colon_no_content": re.compile(r":\s*\n\n"),
}

F2_LOWERCASE_SENTENCE_START_NOUNS = {
    "can", "mechanism", "attachment", "suffering", "the", "this", "that", "a",
    "and", "but", "love", "now", "through", "for example",
}


def _detect_f2_broken_fragments(chapters: list[tuple[int, str]]) -> list[RegisterFinding]:
    findings = []
    for ch_num, ch_text in chapters:
        # F2.A — ": ."
        for m in F2_RULES["F2.A_colon_period_only"].finditer(ch_text):
            findings.append(RegisterFinding(
                failure_id="F2",
                severity="HARD_FAIL",
                chapter=ch_num,
                summary='F2.A: colon-period-only slot artifact (e.g. "Ahjan\'s reading of this is precise: .")',
                evidence={"rule": "F2.A_colon_period_only", "offset": m.start(), "snippet": ch_text[max(0, m.start()-40):m.end()+10]},
            ))
        # F2.B — ends with preposition + period
        for m in F2_RULES["F2.B_sentence_end_preposition"].finditer(ch_text):
            findings.append(RegisterFinding(
                failure_id="F2",
                severity="HARD_FAIL",
                chapter=ch_num,
                summary='F2.B: sentence ends with dangling preposition (e.g. "In Ahjan\'s framework, the path begins with.")',
                evidence={"rule": "F2.B_sentence_end_preposition", "offset": m.start(), "snippet": ch_text[max(0, m.start()-40):m.end()+5]},
            ))
        # F2.C — sentence starts with lowercase known noun
        for sent in _split_sentences(ch_text):
            if not sent:
                continue
            first_word = sent.split()[0].lower().rstrip(",.:;")
            if first_word in F2_LOWERCASE_SENTENCE_START_NOUNS and sent[0].islower():
                findings.append(RegisterFinding(
                    failure_id="F2",
                    severity="HARD_FAIL",
                    chapter=ch_num,
                    summary=f'F2.C: sentence starts with lowercase noun "{first_word}" (template did not fill leading article)',
                    evidence={"rule": "F2.C_lowercase_noun_start", "sentence": sent[:120]},
                ))
        # F2.D — sub-4-word standalone paragraph (excluding chapter headers, list items)
        for para in _split_paragraphs(ch_text):
            wc = len(para.split())
            if 0 < wc < 4 and not para.startswith("#") and not para[0].isdigit():
                # Filter out genuine 1-line caption strips that ARE meant to be short.
                # Heuristic: a true 3-word slot artifact like "Ahjan's the practice" has no clear sentence shape.
                if not para.endswith((".", "?", "!")):
                    findings.append(RegisterFinding(
                        failure_id="F2",
                        severity="HARD_FAIL",
                        chapter=ch_num,
                        summary=f'F2.D: sub-4-word fragment "{para}" — likely slot-template artifact',
                        evidence={"rule": "F2.D_sub_4_word_paragraph", "text": para},
                    ))
        # F2.E — colon followed by paragraph break
        for m in F2_RULES["F2.E_colon_no_content"].finditer(ch_text):
            findings.append(RegisterFinding(
                failure_id="F2",
                severity="HARD_FAIL",
                chapter=ch_num,
                summary="F2.E: colon followed by paragraph break (slot content missing)",
                evidence={"rule": "F2.E_colon_no_content", "offset": m.start(), "snippet": ch_text[max(0, m.start()-30):m.end()+30]},
            ))
    return findings


# ─────────────────────────────────────────────────────────────────────────────
# F3 — Off-doctrine teacher-bank overrun
# ─────────────────────────────────────────────────────────────────────────────

# Per-teacher off-doctrine token classes (token-class set drawn from doctrine.yaml's
# tradition / forbidden_claims / prohibited_outcomes). For teachers without
# doctrine.yaml, use the universal class only.
TEACHER_FORBIDDEN_TOKENS: dict[str, list[str]] = {
    "ahjan": [
        # Other-tradition tokens that should not appear in an ahjan/Tantric book
        "krishna", "bhakti", "vedanta", "sufi", "naqshbandi", "brahman",
        # Prohibited per doctrine
        "theravada", "theravadan",
        # Generic-mystical phrases the audit caught
        "transmission of light", "enlightened ones", "martial arts",
        "structured pathways to light", "spiritual teacher",
    ],
    "joshin": [
        # Joshin = Shingon (Mikkyo) — NOT generic Zen
        "zen", "soto", "rinzai",
        # Other traditions
        "krishna", "bhakti", "vedanta", "sufi",
    ],
    "junko": [
        # Junko = receiver/hibakusha witness — NOT a "teacher" in the conventional sense
        # Don't flag heavily; her doctrine permits witness-register language
    ],
    "master_feung": [
        # Generic Asian wisdom that should NOT appear in Grand Painting / Chinese wisdom register
        "vedanta", "bhakti", "sufi", "naqshbandi",
    ],
    "maat": [
        # Maat = Naqshbandi Sufi — NOT generic mystical
        "krishna", "bhakti", "vedanta", "zen",
    ],
}

F3_WARN_TOKENS_PER_CHAPTER = 1
F3_FAIL_TOKENS_PER_CHAPTER = 3


def _detect_f3_off_doctrine(
    chapters: list[tuple[int, str]],
    teacher_id: str,
) -> list[RegisterFinding]:
    if teacher_id not in TEACHER_FORBIDDEN_TOKENS:
        # No doctrine token-class registered for this teacher; skip
        return []
    forbidden = TEACHER_FORBIDDEN_TOKENS[teacher_id]
    findings = []
    for ch_num, ch_text in chapters:
        ch_lower = ch_text.lower()
        hits: list[str] = []
        for tok in forbidden:
            if tok.lower() in ch_lower:
                hits.append(tok)
        distinct = sorted(set(hits))
        if len(distinct) >= F3_FAIL_TOKENS_PER_CHAPTER:
            severity = "FAIL"
        elif len(distinct) >= F3_WARN_TOKENS_PER_CHAPTER:
            severity = "WARN"
        else:
            continue
        findings.append(RegisterFinding(
            failure_id="F3",
            severity=severity,
            chapter=ch_num,
            summary=f"off-doctrine vocabulary for teacher='{teacher_id}': {distinct}",
            evidence={"teacher_id": teacher_id, "off_doctrine_tokens": distinct, "hit_count": len(hits)},
        ))
    return findings


# ─────────────────────────────────────────────────────────────────────────────
# F4 — Verbatim closing-line repetition
# ─────────────────────────────────────────────────────────────────────────────

def _detect_f4_closing_line_repeats(chapters: list[tuple[int, str]]) -> list[RegisterFinding]:
    closing_lines: list[tuple[int, str]] = []
    for ch_num, ch_text in chapters:
        sentences = _split_sentences(ch_text)
        if not sentences:
            continue
        # Last sentence; strip trailing punctuation for matching
        last = sentences[-1].strip()
        if len(last) < 20:
            # Too short to be meaningful for closing-line repetition
            continue
        closing_lines.append((ch_num, last))

    # Find duplicates
    line_counts: dict[str, list[int]] = {}
    for ch_num, line in closing_lines:
        line_counts.setdefault(line, []).append(ch_num)

    findings = []
    for line, chs in line_counts.items():
        if len(chs) < 2:
            continue
        severity = "WARN" if len(chs) == 2 else "FAIL"
        findings.append(RegisterFinding(
            failure_id="F4",
            severity=severity,
            chapter=None,
            summary=f"closing-line repeated verbatim in {len(chs)} chapters: {chs}",
            evidence={"chapters": chs, "closing_line": line[:160]},
        ))
    return findings


# ─────────────────────────────────────────────────────────────────────────────
# F5 — Named-character continuity
# ─────────────────────────────────────────────────────────────────────────────

# Naive proper-noun extraction (capitalized non-sentence-start words that aren't common nouns)
# Filter out chapter-header common words + plain English proper nouns that aren't characters
F5_NAME_BLOCKLIST = {
    "Slack", "Notion", "LinkedIn", "Discord", "Stanford", "Harvard", "Tuesday",
    "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "Monday",
    "January", "February", "March", "April", "May", "June", "July", "August",
    "September", "October", "November", "December", "I", "Chapter", "Ahjan",
    "Q3", "AM", "PM", "CEO", "HVAC", "HRV", "EI",
}


def _detect_f5_named_character_continuity(chapters: list[tuple[int, str]]) -> list[RegisterFinding]:
    # Per chapter: extract capitalized 1- or 2-word names not in blocklist
    chapter_chars: dict[int, set[str]] = {}
    for ch_num, ch_text in chapters:
        names: set[str] = set()
        # Match Capitalized + (optional " Capitalized")
        for m in re.finditer(r"\b([A-Z][a-z]{2,})(?:\s+([A-Z][a-z]{2,}))?\b", ch_text):
            first = m.group(1)
            if first in F5_NAME_BLOCKLIST:
                continue
            names.add(first)
        chapter_chars[ch_num] = names

    # Compute pairwise overlap
    all_chapters = sorted(chapter_chars.keys())
    if len(all_chapters) < 3:
        return []  # not enough chapters to assess continuity
    overlap_pairs = 0
    total_pairs = 0
    for i, ch_a in enumerate(all_chapters):
        for ch_b in all_chapters[i + 1:]:
            total_pairs += 1
            if chapter_chars[ch_a] & chapter_chars[ch_b]:
                overlap_pairs += 1
    overlap_ratio = overlap_pairs / total_pairs if total_pairs else 1.0

    if overlap_ratio >= 0.4:
        return []
    return [RegisterFinding(
        failure_id="F5",
        severity="WARN",
        chapter=None,
        summary=f"low named-character continuity across chapters (overlap_ratio={overlap_ratio:.2f})",
        evidence={
            "overlap_ratio": round(overlap_ratio, 2),
            "named_chars_per_chapter": {str(k): sorted(v) for k, v in chapter_chars.items()},
        },
    )]


# ─────────────────────────────────────────────────────────────────────────────
# F6 — Pedagogical-cadence 4-gram repetition
# ─────────────────────────────────────────────────────────────────────────────

def _detect_f6_cadence_repetition(chapters: list[tuple[int, str]]) -> list[RegisterFinding]:
    cadence_4grams: list[tuple[int, tuple[int, ...]]] = []
    for ch_num, ch_text in chapters:
        sents = _split_sentences(ch_text)
        lens = [len(s.split()) for s in sents]
        for i in range(len(lens) - 3):
            cadence_4grams.append((ch_num, tuple(lens[i:i + 4])))

    counter = Counter(g for _, g in cadence_4grams)
    repeats = {g: c for g, c in counter.items() if c >= 3}
    if not repeats:
        return []
    severity = "WARN" if len(repeats) <= 2 else "FAIL"
    return [RegisterFinding(
        failure_id="F6",
        severity=severity,
        chapter=None,
        summary=f"pedagogical-cadence 4-gram repeated 3+ times: {len(repeats)} distinct repeating cadences",
        evidence={"repeats": [{"cadence": list(k), "count": v} for k, v in repeats.items()]},
    )]


# ─────────────────────────────────────────────────────────────────────────────
# F7 — Over-prescribed practice density per chapter
# ─────────────────────────────────────────────────────────────────────────────

# Heuristic: a "prescribed-action paragraph" contains ≥1 second-person imperative
# verb AND ≥1 timing/step cue.
F7_IMPERATIVE_VERBS = {
    "breathe", "notice", "follow", "feel", "try", "write", "set", "place",
    "open", "close", "name", "watch", "begin", "start", "pause", "land",
    "remember", "let", "hold", "imagine", "drop", "rest", "press",
}
F7_TIMING_STEP_CUES = {
    "seconds", "minutes", "hours", "ninety", "sixty", "five", "ten",
    "step", "first", "second", "third", "1.", "2.", "3.",
    "cycle", "cycles", "repeat", "for", "before", "after",
}


def _is_prescribed_action(para: str) -> bool:
    words = re.findall(r"[A-Za-z]+", para.lower())
    has_imperative = any(w in F7_IMPERATIVE_VERBS for w in words)
    has_timing_or_step = any(c in para.lower() for c in F7_TIMING_STEP_CUES)
    return has_imperative and has_timing_or_step


def _detect_f7_practice_density(chapters: list[tuple[int, str]]) -> list[RegisterFinding]:
    findings = []
    for ch_num, ch_text in chapters:
        count = sum(1 for p in _split_paragraphs(ch_text) if _is_prescribed_action(p))
        if count >= 4:
            severity = "FAIL"
        elif count == 3:
            severity = "WARN"
        else:
            continue
        findings.append(RegisterFinding(
            failure_id="F7",
            severity=severity,
            chapter=ch_num,
            summary=f"over-prescribed practice density: {count} distinct prescribed-action paragraphs",
            evidence={"prescribed_action_count": count},
        ))
    return findings


# ─────────────────────────────────────────────────────────────────────────────
# Aggregate verdict
# ─────────────────────────────────────────────────────────────────────────────

def _aggregate_verdict(findings: list[RegisterFinding]) -> str:
    has_hard_fail = any(f.severity == "HARD_FAIL" for f in findings)
    if has_hard_fail:
        return "HARD_FAIL"
    has_fail = any(f.severity == "FAIL" for f in findings)
    if has_fail:
        return "FAIL"
    warn_count = sum(1 for f in findings if f.severity == "WARN")
    if warn_count == 0:
        return "PASS"
    if warn_count <= 2:
        return "ADVISORY"
    return "WARN"


def _route_suggested_lanes(findings: list[RegisterFinding]) -> list[str]:
    by_failure: dict[str, set[str]] = {}
    routing = {
        "F1": "Pearl_Editor + Pearl_Writer (atom diversification) OR Pearl_Dev (renderer paragraph-template dedupe extension)",
        "F2": "Pearl_Dev (renderer slot-fill validation; HARD-FAIL renderer artifact)",
        "F3": "Pearl_Dev (TEACHER-MODE-WRAPPER-SEMANTICS-01 impl: ws_teacher_wrapper_semantics_impl_20260517) + Pearl_Editor (teacher_bank atom doctrine audit)",
        "F4": "Pearl_Dev (closing-line uniqueness check in composer)",
        "F5": "Pearl_Architect (named-character roster strategy decision) + Pearl_Editor (story_atom roster updates)",
        "F6": "Pearl_Editor + Pearl_Writer (cadence variety in pedagogical-cadence atoms)",
        "F7": "Pearl_Architect (per-chapter practice-density cap) + Pearl_Editor (atom routing)",
    }
    seen: set[str] = set()
    lanes: list[str] = []
    for f in findings:
        lane = routing.get(f.failure_id)
        if lane and lane not in seen:
            lanes.append(lane)
            seen.add(lane)
    return lanes


# ─────────────────────────────────────────────────────────────────────────────
# Public entry point
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_register(
    book_text: str,
    *,
    teacher_id: str = "",
    persona_id: str = "",
    topic_id: str = "",
    quality_profile: str = "production",
) -> RegisterGateResult:
    """
    Score the rendered book against the F1-F7 detectors.

    F8 (citation grafting) is deferred until anchor corpus
    (artifacts/reference/trade_pub_anchors/) lands.

    Returns a RegisterGateResult with verdict + per-F findings + suggested
    remediation lanes.
    """
    chapters = _split_chapters(book_text)
    findings: list[RegisterFinding] = []
    findings += _detect_f1_templated_paragraphs(chapters)
    findings += _detect_f2_broken_fragments(chapters)
    if teacher_id:
        findings += _detect_f3_off_doctrine(chapters, teacher_id)
    findings += _detect_f4_closing_line_repeats(chapters)
    findings += _detect_f5_named_character_continuity(chapters)
    findings += _detect_f6_cadence_repetition(chapters)
    findings += _detect_f7_practice_density(chapters)

    verdict = _aggregate_verdict(findings)
    lanes = _route_suggested_lanes(findings)

    return RegisterGateResult(
        verdict=verdict,
        findings=findings,
        book_metrics={
            "chapter_count": len(chapters),
            "word_count": len(book_text.split()),
            "teacher_id": teacher_id,
            "persona_id": persona_id,
            "topic_id": topic_id,
            "quality_profile": quality_profile,
            "spec_version": "1.0.0",
            "f8_deferred": "anchor_corpus_required",
        },
        suggested_lanes=lanes,
    )


def evaluate_register_from_path(
    book_path: Path,
    *,
    teacher_id: str = "",
    persona_id: str = "",
    topic_id: str = "",
    quality_profile: str = "production",
    output_path: Optional[Path] = None,
) -> RegisterGateResult:
    """Convenience: read book.txt from disk, score, optionally write report JSON."""
    book_text = Path(book_path).read_text(encoding="utf-8")
    result = evaluate_register(
        book_text,
        teacher_id=teacher_id,
        persona_id=persona_id,
        topic_id=topic_id,
        quality_profile=quality_profile,
    )
    if output_path:
        Path(output_path).write_text(json.dumps(result.to_json(), indent=2), encoding="utf-8")
    return result


# ─────────────────────────────────────────────────────────────────────────────
# CLI for ad-hoc scoring (no LLM; deterministic)
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Score a Pearl Prime book.txt against the register gate (F1-F7).")
    parser.add_argument("--book", required=True, help="Path to book.txt")
    parser.add_argument("--teacher", default="", help="Teacher ID (e.g. ahjan); enables F3 doctrine check")
    parser.add_argument("--persona", default="", help="Persona ID (info only)")
    parser.add_argument("--topic", default="", help="Topic ID (info only)")
    parser.add_argument("--output", default=None, help="Optional output JSON path")
    args = parser.parse_args()

    result = evaluate_register_from_path(
        Path(args.book),
        teacher_id=args.teacher,
        persona_id=args.persona,
        topic_id=args.topic,
        output_path=Path(args.output) if args.output else None,
    )
    print(json.dumps({"verdict": result.verdict, "findings_count": len(result.findings)}, indent=2))
    for f in result.findings:
        ch = f"ch{f.chapter}" if f.chapter else "book"
        print(f"  [{f.severity:9s}] {f.failure_id} {ch}: {f.summary}")
    if result.suggested_lanes:
        print()
        print("Suggested remediation lanes:")
        for lane in result.suggested_lanes:
            print(f"  - {lane}")
