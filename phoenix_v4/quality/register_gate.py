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
F9-F10: reserved (unclaimed detector ID gaps)
F11: HOOK atom first-paragraph abstract opening (lacks scene-first person+situation+posture) → WARN
     Per HOOK-SCENE-FIRST-01 / OPD-144; V1 WARN-only (future ws may escalate to HARD_FAIL)
F12: un-wrapped voice-shift → FAIL on raw teacher/science register (bypassed the wrapper),
     WARN on a thin wrapper. Per OVERLAY_SPEC §13 "Stage-6 voice-shift lint" + cap
     BESTSELLER-FIT-PLAN-VOICE-DOCTRINE-V1-01. Shares the VoiceOutOfZoneError vocabulary
     with D12's voice_braid_gate (cross-zone bleed); F12 is the un-wrapped-shift sibling.
F13: dwell-beat / integration starvation → FAIL when 3+ consecutive named insights run
     with no dwell beat between them. Per OVERLAY_SPEC §7.3 dwell contract + §13 criterion #13.

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
    failure_id: str         # F1..F8, F11, F12, F13 (F9-F10 reserved)
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

# F2.C — sentence starts with a lowercase word that signals a DROPPED leading article
# (slot-template artifact, e.g. "mechanism running continuously is written into your
# biology." where "The mechanism …" was intended).
#
# DEFERRED-LANE register_verdict (2026-06-15): the prior set also listed function words
# — "the", "a", "this", "that", "and", "but", "now", "through", "for example". Those are
# NOT missing-article artifacts: an article ("the"/"a") cannot itself be missing an
# article, and conjunctions/adverbs legitimately open a lowercased continuation sentence
# (e.g. a clause that begins after an ellipsis lead-in, or a stylistic lowercase opener).
# Flagging them produced false-positive HARD_FAILs — e.g. the perfectly grammatical
# exercise-wrapper line "the breath cycle (as taught by Ahjan)" — that blocked the whole
# register verdict from reaching PASS even with leaked labels already at zero. The set is
# now restricted to genuine bare CONTENT nouns/modals where a leading article was clearly
# elided, which still catches the real artifact asserted by the F2.C regression test.
F2_LOWERCASE_SENTENCE_START_NOUNS = {
    "can", "mechanism", "attachment", "suffering", "love",
}

# ── F2.B grammatical stranded-preposition / phrasal-verb exclusion ────────────
# DEFERRED-LANE register_verdict (2026-06-15, composer-register-flip): F2.B flags
# any sentence ending in a preposition (with/of/by/to/for/on/in/from/the/a) because a
# *genuine* unfilled-slot artifact ("…the path begins with {SLOT}." → "…begins with.")
# ends that way. But English legitimately strands prepositions sentence-finally:
#   • phrasal-verb particles  — "Drop the urge to move on.", "Then move on."
#   • relative-clause stranding — "the room you are answering in.",
#                                 "the thing you're now running from.",
#                                 "a practice to work with."
#   • infinitive complements   — "what repeated overload teaches you to stop asking for."
#   • passive / predicate       — "You're cared for.", "before it was always on."
# All of these are authored content (within_slot_bridge_families.yaml,
# global_flow_glue_bank.yaml, chapter_composer authored lines, exercise intro templates),
# not renderer artifacts — yet the bare regex HARD_FAILed the whole register verdict on
# them. This is the same false-positive-removal class as #1596's F2.C function-word fix.
#
# Discriminator (deterministic, no LLM): a sentence-final preposition is a *legitimate
# stranded preposition* — NOT a dropped-slot artifact — when the clause carries a stranding
# licensor (a relative pronoun / infinitive "to" / wh-word / "you are|'re" / object pronoun)
# OR the (verb, preposition) ending is a recognized phrasal verb. The genuine slot artifact
# asserted by test_f2b ("the path begins with.") has NO such licensor and "begins" is not a
# phrasal verb, so it still HARD_FAILs.

# Phrasal verbs whose particle legitimately ends a sentence (verb token immediately before
# the final preposition). Kept deliberately small + high-confidence.
_F2B_PHRASAL_VERB_ENDINGS = frozenset({
    ("move", "on"), ("moves", "on"), ("moved", "on"), ("moving", "on"),
    ("carry", "on"), ("carries", "on"), ("carried", "on"), ("carrying", "on"),
    ("go", "on"), ("goes", "on"), ("went", "on"), ("going", "on"),
    ("hold", "on"), ("holds", "on"), ("held", "on"), ("holding", "on"),
    ("hang", "on"), ("press", "on"), ("read", "on"), ("come", "on"),
    ("give", "in"), ("gives", "in"), ("gave", "in"), ("giving", "in"),
    ("cared", "for"), ("care", "for"), ("cares", "for"), ("caring", "for"),
    ("provided", "for"), ("accounted", "for"),
    # 2026-06-17 (Blocker 3, F2 false-positive hardening): motion/arrival phrasal verbs whose
    # particle legitimately ends a sentence. QA sweep T1 false-HARD_FAILed on the authored SCENE
    # line "He hears the first bus pulling in." — "pulling in" is a phrasal verb (a bus pulls in),
    # not a dropped template slot. These are content lines from SCENE/HOOK atoms, never artifacts.
    ("pulling", "in"), ("pull", "in"), ("pulls", "in"), ("pulled", "in"),
    ("rolling", "in"), ("roll", "in"), ("rolls", "in"), ("rolled", "in"),
    ("coming", "in"), ("come", "in"), ("comes", "in"), ("came", "in"),
    ("drifting", "in"), ("drift", "in"), ("drifts", "in"), ("drifted", "in"),
    ("filtering", "in"), ("filter", "in"), ("filters", "in"), ("filtered", "in"),
    ("settling", "in"), ("settle", "in"), ("settles", "in"), ("settled", "in"),
    ("pulling", "up"), ("pulls", "up"), ("pulled", "up"),
    ("looking", "up"), ("looks", "up"), ("looked", "up"),
    ("breathing", "out"), ("breathe", "out"), ("breathes", "out"), ("breathed", "out"),
    ("letting", "go"), ("lets", "go"), ("let", "go"),
})

# Stranding licensors: their presence anywhere in the sentence indicates the final
# preposition is grammatically stranded (relative clause / infinitive / wh-clause /
# passive-with-subject), not a dropped template slot.
_F2B_STRANDING_LICENSOR_RE = re.compile(
    r"\b("
    r"to|"                                   # infinitive: "a practice to work with."
    r"that|which|who|whom|whose|where|"      # relative pronouns
    r"what|why|how|"                          # wh-clauses: "what is the relationship for."
    r"you|your|you're|they|them|their|"       # stranded subject/object: "you are answering in."
    r"i'm|we're|he's|she's|it's|i|we"
    r")\b",
    re.IGNORECASE,
)

# Copula-predicate ending: a sentence-final particle that is the PREDICATE of a
# linking verb is legitimate prose, not a dropped slot — "The awareness is already on.",
# "before it was always on.", "the system was on.", "you're cared for." (passive). The
# bare F2.B regex HARD_FAILed these because they end in on/for/in; none carries a relative/
# infinitive licensor, so the licensor test above misses them. Pattern: a copula
# (is/are/was/were/be/been/being/'s/'re/am) optionally followed by ONE adverb (already/
# always/still/just/now/...) then the final particle. This is the "predicate" case the
# F2.B block comment already names but the original discriminator did not cover. The
# genuine slot artifact "the path begins with." has a lexical verb ("begins"), not a
# copula, immediately before the particle → still HARD_FAILs.
_F2B_COPULA_PREDICATE_RE = re.compile(
    r"\b(is|are|was|were|be|been|being|am|'s|'re|isn't|aren't|wasn't|weren't)\b"
    r"(?:\s+(?:already|always|still|just|now|even|truly|fully|never|only|"
    r"finally|again|right|all|so|really|quietly|simply)){0,2}\s+"
    r"(on|in|for|out|over|through|up|down|off|around|about)\.\s*$",
    re.IGNORECASE,
)


# Lowercase function words that may legitimately appear mid-heading in Title Case
# (e.g. "Worth Without Output" — but small joiners like of/and/the are commonly lowercased).
_F2D_TITLE_LOWERCASE_JOINERS = frozenset({
    "a", "an", "the", "and", "or", "but", "of", "to", "in", "on", "for",
    "with", "as", "at", "by", "from", "into", "over", "under",
    # 2026-06-17 (Blocker 3, F2 false-positive hardening): "vs" / "v" is a legitimate lowercase
    # heading joiner. QA sweep X2 false-HARD_FAILed on the chapter working title
    # "Performing vs Connecting" because "vs" was not recognized, so the Title-Case heading
    # exemption (_is_titlecase_heading) rejected it. (Only the period-free forms are listed; the
    # heading validator's token regex rejects a trailing period regardless.) Genuine leaked
    # component labels ("INTEGRATION v06") carry a digit and still HARD_FAIL.
    "vs", "v",
})


def _is_titlecase_heading(para: str) -> bool:
    """True when `para` reads as a clean Title-Case chapter heading (every content word
    capitalized, alphabetic only, no digits/labels). Used to keep a chapter's working title
    from tripping F2.D, while genuine leaked slot labels ("INTEGRATION v06") still HARD_FAIL."""
    tokens = para.split()
    if not tokens:
        return False
    saw_content_word = False
    for i, tok in enumerate(tokens):
        # Allow a trailing terminal-free token only; headings carry no sentence punctuation.
        if not re.fullmatch(r"[A-Za-z][A-Za-z-]*", tok):
            return False  # digits, apostrophes, labels (e.g. "v06", "Ahjan's") → not a heading
        low = tok.lower()
        if tok[0].isupper():
            saw_content_word = True
            continue
        # A lowercase token is only acceptable as an interior joiner (never first word).
        if i == 0 or low not in _F2D_TITLE_LOWERCASE_JOINERS:
            return False
    return saw_content_word


def _f2b_is_legitimate_stranded_preposition(sentence: str) -> bool:
    """True when a sentence-final preposition is grammatically stranded (legitimate prose),
    rather than a dropped-slot template artifact. See block comment above."""
    s = sentence.strip()
    # Tokenize trailing words; drop the final period.
    words = re.findall(r"[A-Za-z']+", s.lower())
    if len(words) < 2:
        return False
    verb, prep = words[-2], words[-1]
    if (verb, prep) in _F2B_PHRASAL_VERB_ENDINGS:
        return True
    # Copula-predicate particle ("The awareness is already on.", "it was always on.",
    # "you're cared for.") — the particle is the predicate of a linking/passive verb, not a
    # dropped slot. Checked before the licensor test because these sentences carry no
    # relative/infinitive licensor.
    if _F2B_COPULA_PREDICATE_RE.search(s):
        return True
    # A genuine dropped-slot artifact is a short lead-in clause with no stranding licensor
    # ("the path begins with."). Real stranded prepositions sit inside a clause that names
    # the stranded element via a licensor token.
    if _F2B_STRANDING_LICENSOR_RE.search(s):
        return True
    return False


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
            # Recover the offending sentence (text from the prior sentence/line boundary up to
            # the matched period) so we can tell a dropped-slot artifact ("…begins with.")
            # from a grammatically stranded preposition ("…a practice to work with.").
            seg_start = max(
                ch_text.rfind("\n", 0, m.start()),
                max(ch_text.rfind(". ", 0, m.start()),
                    max(ch_text.rfind("? ", 0, m.start()), ch_text.rfind("! ", 0, m.start()))),
            )
            offending_sentence = ch_text[seg_start + 1 : m.end()].strip()
            if _f2b_is_legitimate_stranded_preposition(offending_sentence):
                continue
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
        _f2d_paras = _split_paragraphs(ch_text)
        for _pi, para in enumerate(_f2d_paras):
            wc = len(para.split())
            if 0 < wc < 4 and not para.startswith("#") and not para[0].isdigit():
                # Filter out genuine 1-line caption strips that ARE meant to be short.
                # Heuristic: a true 3-word slot artifact like "Ahjan's the practice" has no clear sentence shape.
                if not para.endswith((".", "?", "!")):
                    # DEFERRED-LANE register_verdict (2026-06-15): the FIRST paragraph of a
                    # chapter body is the chapter's working title (the renderer emits
                    # "Chapter N\n\n<Working Title>\n\n…"; _split_chapters has already stripped
                    # the "Chapter N" line, so the title is _f2d_paras[0]). A clean Title-Case
                    # heading ("Small Exposures", "Worth Without Output") is NOT a slot artifact.
                    # Genuine leaked labels still HARD_FAIL: a leaked component label
                    # ("INTEGRATION v06") carries a digit/lowercase token and never sits at
                    # index 0, and "Ahjan's the practice" is not Title-Case.
                    if _pi == 0 and _is_titlecase_heading(para):
                        continue
                    findings.append(RegisterFinding(
                        failure_id="F2",
                        severity="HARD_FAIL",
                        chapter=ch_num,
                        summary=f'F2.D: sub-4-word fragment "{para}" — likely slot-template artifact',
                        evidence={"rule": "F2.D_sub_4_word_paragraph", "text": para},
                    ))
        # F2.E — colon followed by paragraph break
        for m in F2_RULES["F2.E_colon_no_content"].finditer(ch_text):
            # DEFERRED-LANE register_verdict (2026-06-15): the rule's intent is "the slot AFTER
            # the colon rendered empty". A colon that introduces a numbered/bulleted list or a
            # following content paragraph across a blank line is legitimate authored structure
            # ("Try this for ninety seconds:\n\n1. Notice…", "The teaching is simple:\n\nCrank…"),
            # not a missing slot. Only fire when nothing substantive follows the colon+blank
            # (EOF, another blank, or a bare heading/label).
            _after = ch_text[m.end():].lstrip()
            if _after:
                _first_line = _after.split("\n", 1)[0].strip()
                # Real content follows: a list item, or a line with >=3 words. Either means the
                # post-colon slot was filled (just as its own paragraph) → not an F2.E artifact.
                _is_list_item = bool(re.match(r"^(\d+[.)]|[-*•])\s+\S", _first_line))
                if _is_list_item or len(_first_line.split()) >= 3:
                    continue
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
        # Junko = channeler / light-language transmitter (receiver of cosmic guidance)
        # per OPD-111. Forbidden tokens block Zen/contemplative/ganbaru drift that
        # would re-create the OPD-111 doctrine mismatch in atom generation.
        "zen", "zazen", "shikantaza", "satori", "kensho", "kenshō", "roshi",
        "ganbaru", "mono no aware", "kitchen table",
        "shingon", "ajikan", "kōbō", "kobo daishi",
        "yuki", "hana", "kenji",  # Miyuki's recurring characters
    ],
    "miyuki": [
        # Miyuki = Japanese contemplative (lay-secular, wabi-sabi, ganbaru) per OPD-111.
        # Forbidden tokens block channeling/cosmic drift (Junko's territory) and
        # explicit Zen lineage drift (Kenjin's territory) and Shingon (Joshin's).
        "channel", "channeling", "light language", "ライトランゲージ",
        "ascended master", "cosmic council", "transmission", "soul remembrance",
        "frequency upgrade", "lemuria", "atlantis", "age of air",
        "shingon", "ajikan", "kōbō", "kobo daishi", "mikkyo",
        "shikantaza",  # method-name; Kenjin Roshi owns Sōtō Zen
        "satori", "kenshō", "kensho", "dokusan",
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
# F11 — HOOK atom first-paragraph abstract opening (HOOK-SCENE-FIRST-01)
# ─────────────────────────────────────────────────────────────────────────────

F11_WINDOW_CHARS = 200

F11_PERSON_PRONOUN_RE = re.compile(
    r"\b(?:a person|she|he|they|you|your)\b",
    re.IGNORECASE,
)
F11_PERSON_ROLE_NOUN_RE = re.compile(
    r"\b(?:person|woman|man|mother|father|daughter|son|executive|engineer|"
    r"professional|colleague|client|vp|ceo|manager|employee|graduate|student)\b",
    re.IGNORECASE,
)
F11_NAMED_CHARACTER_RE = re.compile(
    r"^[A-Z][a-z]{2,}\s+(?:woke|sat|stood|walked|has|used|lies|keeps|doesn't|don't)\b",
)
F11_SETTING_NOUN_RE = re.compile(
    r"\b(?:bathroom|office|kitchen|car|bed|stall|meeting|job|room|desk|home|"
    r"highway|hospital|store|airport|elevator|hallway|classroom|restaurant|"
    r"bedroom|apartment|building|floor|chair|table|screen|phone|email|invoice|"
    r"account|bank|client|revenue|pitch|deal)\b",
    re.IGNORECASE,
)
F11_PRESENT_CONTINUOUS_RE = re.compile(
    r"\b(?:sitting|standing|pressing|breathing|holding|driving|waiting|lying|"
    r"sleeping|running|refreshing|scrolling|typing|checking|replaying|thinking|"
    r"crying|listening|watching|reading|writing|pitching)\b",
    re.IGNORECASE,
)
F11_BODY_POSTURE_RE = re.compile(
    r"\b(?:sitting|standing|pressing|breathing|holding|tightens|clenched|jaw|"
    r"shoulders|ribs|chest|throat|hands|heart|mouth|nose|eyes|gut|stomach|"
    r"sweat|trembling|shaking|frozen|slumped|hunched|curled|gripping|leaning)\b",
    re.IGNORECASE,
)
F11_ABSTRACT_OPENING_RE = re.compile(
    r"^\s*(?:"
    r"Nightfall|The mind|Awareness|Consciousness|Worth\b|Every decision|"
    r"The\s+(?:mind|body|soul|truth|worth|stakes|pivot|public|private)\b|"
    r"Your worth\b|Philosophy\b|Abstract\b"
    r")",
    re.IGNORECASE,
)
_HOOK_VARIATION_RE = re.compile(r"^##\s+HOOK\s+(v\d+)\s*$", re.MULTILINE)
_HOOK_BODY_RE = re.compile(
    r"---\s*\n+---\s*\n+([\s\S]*?)\n+---",
    re.MULTILINE,
)


def _parse_hook_variation_first_paragraphs(atom_text: str) -> list[tuple[str, str]]:
    """Return (variation_id, first_paragraph) for each ## HOOK block in a CANONICAL atom."""
    variations: list[tuple[str, str]] = []
    headers = list(_HOOK_VARIATION_RE.finditer(atom_text))
    if not headers:
        stripped = atom_text.strip()
        if stripped:
            first_para = _split_paragraphs(stripped)[0] if _split_paragraphs(stripped) else stripped
            variations.append(("inline", first_para))
        return variations

    for i, header in enumerate(headers):
        var_id = header.group(1)
        start = header.end()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(atom_text)
        block = atom_text[start:end]
        body_match = _HOOK_BODY_RE.search(block)
        if body_match:
            body = body_match.group(1).strip()
        else:
            body = block.strip()
        paragraphs = _split_paragraphs(body)
        if paragraphs:
            variations.append((var_id, paragraphs[0]))
    return variations


def _f11_scene_first_signals(first_paragraph: str) -> dict[str, bool]:
    """Heuristic scene-first signals in the first 200 chars (V1; refine after corpus tagging)."""
    window = first_paragraph[:F11_WINDOW_CHARS]

    concrete_person = bool(
        F11_NAMED_CHARACTER_RE.match(first_paragraph.strip())
        or re.search(r"\b(?:she|he|they)\b", window, re.IGNORECASE)
        or (
            F11_PERSON_PRONOUN_RE.search(window)
            and F11_PERSON_ROLE_NOUN_RE.search(window)
        )
    )
    concrete_situation = bool(
        F11_SETTING_NOUN_RE.search(window)
        or F11_PRESENT_CONTINUOUS_RE.search(window)
        or re.search(
            r"\b(?:\d{1,2}:\d{2}\s*(?:am|pm)?|monday|tuesday|wednesday|thursday|friday|"
            r"saturday|sunday|tonight|morning|midnight|3am|4am)\b",
            window,
            re.IGNORECASE,
        )
    )
    concrete_body_posture = bool(
        F11_BODY_POSTURE_RE.search(window)
        or re.search(
            r"\b(?:sweat|sweats|woke|wakes|awake|insomnia|exhaustion|tired|lowers her voice)\b",
            window,
            re.IGNORECASE,
        )
    )

    return {
        "concrete_person": concrete_person,
        "concrete_situation": concrete_situation,
        "concrete_body_posture": concrete_body_posture,
    }


def _f11_first_paragraph_warns(first_paragraph: str) -> tuple[bool, dict]:
    """
    True when the HOOK opening should surface F11 WARN.

    Fail when: (a) abstract-noun-phrase opening, or (b) zero of three scene-first signals.
    """
    para = first_paragraph.strip()
    if not para:
        return False, {"reason": "empty_paragraph"}

    signals = _f11_scene_first_signals(para)
    signal_count = sum(signals.values())
    abstract_opening = bool(F11_ABSTRACT_OPENING_RE.match(para))

    warns = abstract_opening or signal_count == 0
    return warns, {
        "signals": signals,
        "signal_count": signal_count,
        "abstract_opening": abstract_opening,
    }


def _detect_f11_hook_abstract_opening(
    hook_atoms: list[tuple[str, str]],
) -> list[RegisterFinding]:
    """
    Flag HOOK atom first paragraphs that open philosophy-first instead of scene-first.

    Each hook_atoms entry is (atom_path, atom_file_text). Only v01 is checked when
    check_all_variations=False (default integration path); set check_all_variations
    via evaluate_register(hook_atoms=..., f11_all_variations=True).
    """
    findings: list[RegisterFinding] = []
    for atom_path, atom_text in hook_atoms:
        variations = _parse_hook_variation_first_paragraphs(atom_text)
        if not variations:
            continue
        # V1: first variation only (production HOOK slot uses v01)
        var_id, first_para = variations[0]
        warns, meta = _f11_first_paragraph_warns(first_para)
        if not warns:
            continue
        signals = meta.get("signals", {})
        missing = [k for k, v in signals.items() if not v]
        findings.append(RegisterFinding(
            failure_id="F11",
            severity="WARN",
            chapter=None,
            summary=(
                f"HOOK {var_id} first paragraph lacks scene-first opening "
                f"({meta.get('signal_count', 0)}/3 signals; abstract_opening={meta.get('abstract_opening')})"
            ),
            evidence={
                "detector_id": "F11",
                "severity": "WARN",
                "atom_path": atom_path,
                "variation": var_id,
                "evidence_snippet": first_para[:F11_WINDOW_CHARS],
                "signals": signals,
                "missing_signals": missing,
                "abstract_opening": meta.get("abstract_opening", False),
                "cap": "HOOK-SCENE-FIRST-01",
            },
        ))
    return findings


def _detect_f11_hook_abstract_opening_all_variations(
    hook_atoms: list[tuple[str, str]],
) -> list[RegisterFinding]:
    """Like _detect_f11_hook_abstract_opening but checks every HOOK variation in each atom."""
    findings: list[RegisterFinding] = []
    for atom_path, atom_text in hook_atoms:
        for var_id, first_para in _parse_hook_variation_first_paragraphs(atom_text):
            warns, meta = _f11_first_paragraph_warns(first_para)
            if not warns:
                continue
            signals = meta.get("signals", {})
            findings.append(RegisterFinding(
                failure_id="F11",
                severity="WARN",
                chapter=None,
                summary=(
                    f"HOOK {var_id} first paragraph lacks scene-first opening "
                    f"({meta.get('signal_count', 0)}/3 signals)"
                ),
                evidence={
                    "detector_id": "F11",
                    "severity": "WARN",
                    "atom_path": atom_path,
                    "variation": var_id,
                    "evidence_snippet": first_para[:F11_WINDOW_CHARS],
                    "signals": signals,
                    "abstract_opening": meta.get("abstract_opening", False),
                    "cap": "HOOK-SCENE-FIRST-01",
                },
            ))
    return findings


def load_hook_atoms_from_paths(paths: list[Path]) -> list[tuple[str, str]]:
    """Read HOOK CANONICAL.txt paths into (relative_path, text) tuples for F11."""
    loaded: list[tuple[str, str]] = []
    for p in paths:
        path = Path(p)
        loaded.append((str(path), path.read_text(encoding="utf-8")))
    return loaded


# ─────────────────────────────────────────────────────────────────────────────
# F12 — Un-wrapped voice-shift lint (BESTSELLER-FIT-PLAN-VOICE-DOCTRINE-V1-01)
# ─────────────────────────────────────────────────────────────────────────────
#
# Per OVERLAY_SPEC §13 "Stage-6 voice-shift lint (F12)". D12's voice_braid_gate
# (VoiceOutOfZoneError) catches CROSS-ZONE voice bleed (coach voice inside a STORY
# slot). F12 — the register_gate-side sibling — catches UN-WRAPPED voice-shift:
# teacher-doctrine or science-citation register entered RAW, without having been
# routed through teacher_wrapper.py / science_wrapper resolution.
#
# Shared error vocabulary: F12 findings carry evidence["error_class"] =
# "VoiceOutOfZoneError" so F12 and D12 surface under ONE operator-facing
# vocabulary (the spec's explicit requirement). voice_braid_gate.py does not yet
# exist on origin/main, so F12 is the register_gate-side detector; when D12 lands
# it reuses — does NOT duplicate — this VoiceOutOfZoneError vocabulary.
#
# Deterministic heuristic only — NO LLM API (CLAUDE.md Tier policy).
#
# Severity:
#   FAIL — an un-wrapped voice-shift (teacher/science register entered raw, no
#          wrapper attribution present in the surrounding sentence window).
#   WARN — a thin wrapper (wrapper present but attribution is degenerate — a bare
#          generalized "According to <Named individual>" that should have been
#          routed through named mode, or a wrapper stem with no lift/payload).

# Raw-teacher tells: honorific + named individual speaking AS authority, the exact
# generalized-mode anti-patterns banned by teacher_wrapper_templates.yaml
# ("Master X says…", "I came across this teacher", "According to [named
# individual]…"). These are register entries that bypassed the wrapper.
F12_RAW_TEACHER_RE = re.compile(
    r"\b("
    r"Master\s+[A-Z][a-z]+(?:\s+(?:says|teaches|taught|said|tells|reminds|reminds us|teaches us))?"
    r"|(?:Sensei|Guru|Roshi|Rōshi|Lama|Swami|Sifu|Sef?u|Rinpoche|Sheikh|Shaykh)\s+[A-Z][a-z]+"
    r"|I\s+(?:came across|met|studied with|once met|found)\s+(?:this|a|an)\s+(?:teacher|master|guru|monk|sensei|roshi|lama)"
    r")\b",
    re.IGNORECASE,
)

# Raw-science tells: named scientist + proof/overclaim verb, or first-person
# "a study I read", or the "Scientists have definitively shown" overclaim — the
# exact generalized-mode anti-patterns banned by science_wrapper_templates.yaml.
F12_RAW_SCIENCE_RE = re.compile(
    r"\b("
    r"Dr\.?\s+[A-Z][a-z]+\s+(?:proved|proves|has proven|definitively|showed|shows|discovered|found|demonstrated)"
    r"|Professor\s+[A-Z][a-z]+\s+(?:proved|proves|showed|shows|discovered|demonstrated)"
    r"|(?:a|the|this)\s+study\s+I\s+(?:read|saw|came across|found|remember)"
    r"|Scientists\s+have\s+definitively\s+(?:shown|proven|proved|demonstrated)"
    r"|Science\s+has\s+(?:proven|proved|definitively)"
    r")\b",
    re.IGNORECASE,
)

# Wrapper-attribution markers — the signatures that teacher_wrapper.py /
# science_wrapper resolution leave in the prose (from teacher_wrapper_templates.yaml
# + science_wrapper_templates.yaml, named + generalized + composite modes). Their
# presence near a register-shift means the shift WAS wrapped (no FAIL).
F12_WRAPPER_ATTRIBUTION_RE = re.compile(
    r"("
    # teacher wrapper signatures (named + generalized)
    r"\bAccording to\b"
    r"|\bIn\s+[A-Z][a-z]+'s\s+(?:framework|reading|work)\b"
    r"|\bDrawing on\b"
    r"|\bAs\s+[A-Z][a-z]+\s+reminds us\b"
    r"|\b(?:the|The)\s+[A-Z][a-z]+\s+tradition\b"
    r"|\b(?:Tantric|Zen|Theravada|Theravadan|Taoist|Shingon|Sufi|Naqshbandi|"
    r"Mikkyo|bhakti|somatic|contemplative)\s+(?:tradition|teaching|lineage|practice|approach)\b"
    r"|\bA practice (?:from|as taught by|grounded in)\b"
    # science wrapper signatures (named + generalized + composite)
    r"|\bResearch in\b"
    r"|\bthe\s+[a-z]+\s+evidence\b"
    r"|\bAcross studies\b"
    r"|\bAcross disciplines\b"
    r"|\bWithin\s+[a-z]+,?\s+the data\b"
    r"|\bRooted in\b"
    r"|\bgrounded in\s+[A-Z][a-z]+'s\b"
    r"|\bDrawn from\b"
    r")",
    re.IGNORECASE,
)

# "Thin wrapper" signal: a generalized-mode "According to <Named Capitalized
# Person>" — the wrapper stem is present but it names an individual (named-mode
# content smuggled through a generalized stem), or a wrapper stem that resolved to
# a bare pattern with no payload after it. WARN, not FAIL.
F12_THIN_WRAPPER_RE = re.compile(
    r"\bAccording to\s+(?:Dr\.?\s+)?[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\s*[.,]",
)


F12_WINDOW_CHARS = 160  # attribution-proximity window around a register-shift marker.


def _f12_window_has_wrapper(window: str) -> bool:
    """True when wrapper-attribution vocabulary is present in the proximity window."""
    return bool(F12_WRAPPER_ATTRIBUTION_RE.search(window))


def _detect_f12_unwrapped_voice_shift(
    chapters: list[tuple[int, str]],
) -> list[RegisterFinding]:
    """
    Flag teacher / science register that shifted in RAW, bypassing the wrapper.

    Operates on chapter text with a character window (NOT a naive sentence split:
    the raw-science marker "Dr. X proved" itself contains a period, which a
    sentence splitter would break apart). For each raw-teacher / raw-science marker
    match, a ±F12_WINDOW_CHARS window is checked for wrapper-attribution vocab:
      - no wrapper in window  → F12 FAIL (un-wrapped shift)
      - wrapper in window     → F12 WARN (thin/degenerate wrapper; raw tell leaked
                                 through an otherwise-wrapped line)
    A generalized wrapper stem that names an individual ("According to Dr. X,")
    is independently flagged WARN (thin wrapper). Findings carry the shared
    VoiceOutOfZoneError vocabulary so F12 and D12 read the same to the operator.
    """
    findings: list[RegisterFinding] = []
    for ch_num, ch_text in chapters:
        flagged_spans: list[tuple[int, int]] = []  # de-dupe overlapping markers
        for register, rx in (("teacher", F12_RAW_TEACHER_RE), ("science", F12_RAW_SCIENCE_RE)):
            for m in rx.finditer(ch_text):
                span = (m.start(), m.end())
                if any(span[0] < e and s < span[1] for s, e in flagged_spans):
                    continue
                flagged_spans.append(span)
                marker = m.group(0)
                lo = max(0, m.start() - F12_WINDOW_CHARS)
                hi = min(len(ch_text), m.end() + F12_WINDOW_CHARS)
                window = ch_text[lo:hi]
                snippet = ch_text[max(0, m.start() - 30):m.end() + 30].strip()
                if _f12_window_has_wrapper(window):
                    findings.append(RegisterFinding(
                        failure_id="F12",
                        severity="WARN",
                        chapter=ch_num,
                        summary=(
                            f"thin wrapper — {register} register marker '{marker}' "
                            f"present alongside a wrapper stem (degenerate attribution)"
                        ),
                        evidence={
                            "error_class": "VoiceOutOfZoneError",
                            "kind": "thin_wrapper",
                            "register": register,
                            "marker": marker,
                            "snippet": snippet[:160],
                            "cap": "BESTSELLER-FIT-PLAN-VOICE-DOCTRINE-V1-01",
                        },
                    ))
                else:
                    findings.append(RegisterFinding(
                        failure_id="F12",
                        severity="FAIL",
                        chapter=ch_num,
                        summary=(
                            f"un-wrapped {register} voice-shift: '{marker}' entered raw "
                            f"(bypassed teacher_wrapper / science_wrapper resolution)"
                        ),
                        evidence={
                            "error_class": "VoiceOutOfZoneError",
                            "kind": "unwrapped_voice_shift",
                            "register": register,
                            "marker": marker,
                            "snippet": snippet[:160],
                            "cap": "BESTSELLER-FIT-PLAN-VOICE-DOCTRINE-V1-01",
                        },
                    ))
        # Thin-wrapper: a generalized stem that names an individual ("According to
        # Dr. X,") even when no raw register verb fired. WARN.
        for m in F12_THIN_WRAPPER_RE.finditer(ch_text):
            span = (m.start(), m.end())
            if any(span[0] < e and s < span[1] for s, e in flagged_spans):
                continue
            flagged_spans.append(span)
            findings.append(RegisterFinding(
                failure_id="F12",
                severity="WARN",
                chapter=ch_num,
                summary=(
                    "thin wrapper — generalized stem names an individual "
                    "(should route through named mode or drop the name)"
                ),
                evidence={
                    "error_class": "VoiceOutOfZoneError",
                    "kind": "thin_wrapper",
                    "register": "ambiguous",
                    "snippet": ch_text[max(0, m.start() - 20):m.end() + 30].strip()[:160],
                    "cap": "BESTSELLER-FIT-PLAN-VOICE-DOCTRINE-V1-01",
                },
            ))
    return findings


# ─────────────────────────────────────────────────────────────────────────────
# F13 — Dwell-beat / integration-starvation (OVERLAY_SPEC §7.3 + §13 criterion #13)
# ─────────────────────────────────────────────────────────────────────────────
#
# Per §7.3: after each NAMED INSIGHT (a sentence articulating a new pattern,
# mechanism, reframe, or cost — the Name/Turn moves of §4, any PIVOT/REFLECTION
# claim) the chapter must hold a DWELL BEAT before advancing. A dwell beat is
# exactly one of: a body/sensory landing, a held silence, or a single concrete
# consequence — and is ≤~40 words ("a held breath, not a passage").
#
# Criterion #13 FAIL (the "broken" band of the §13 rubric): three or more
# CONSECUTIVE insight sentences with no dwell beat between them — integration
# starvation. This detector wires that diagnostic in as register-gate finding F13,
# feeding the editor §13 rubric.
#
# Deterministic heuristic only — NO LLM API.

F13_DWELL_MAX_WORDS = 40  # §7.3: "A dwell beat longer than ~40 words ... breaks the contract."
F13_CONSECUTIVE_INSIGHT_FAIL = 3  # §13 criterion #13 "broken" band.

# Insight markers — a sentence that NAMES a new pattern / mechanism / reframe /
# cost. (Name and Turn moves of §4; PIVOT/REFLECTION claims.)
F13_INSIGHT_RE = re.compile(
    r"("
    r"\bthe mechanism is\b"
    r"|\bwhat(?:'s| is) (?:actually )?happening (?:here )?is\b"
    r"|\bwhich means\b"
    r"|\bthe (?:real|actual|deeper|hidden) (?:pattern|cost|mechanism|truth|problem|fear|work)\b"
    r"|\bthe pattern is\b"
    r"|\bthis is (?:what|why|how|the|not|a)\b"
    r"|\bis not\b.*\bbut\b"
    r"|\bwas never (?:about|the)\b"
    r"|\bthe truth is\b"
    r"|\bhere(?:'s| is) (?:the|what)\b"
    r"|\bturns out\b"
    r"|\bthe point is\b"
    r"|\bthe reframe\b"
    r"|\bnotice that\b"
    r"|\bthe cost (?:is|of)\b"
    r")",
    re.IGNORECASE,
)

# Body / postural landing vocabulary ("land it in the body").
F13_DWELL_BODY_RE = re.compile(
    r"\b(?:shoulders|jaw|chest|ribs|throat|breath|breathe|breathing|hands|heart|"
    r"belly|stomach|gut|spine|neck|skin|feet|chair|floor|lungs|pulse|muscles|"
    r"tightens|loosens|slumped|hunched|clenched|unclench|exhale|inhale|settle|"
    r"settles|warmth|weight)\b",
    re.IGNORECASE,
)

# Held-silence vocabulary ("hold the silence").
F13_DWELL_SILENCE_RE = re.compile(
    r"("
    r"\bread (?:that|this) again\b"
    r"|\bstop reading\b"
    r"|\bthe next (?:sentence|line|paragraph) can wait\b"
    r"|\b(?:sit|stay|rest|wait) (?:with|here|in) (?:that|this|it)\b"
    r"|\bfor (?:a|one) (?:moment|breath|beat)\b"
    r"|\blet (?:that|this|it) (?:land|sit|settle|register)\b"
    r"|\bdon't move on (?:yet|too fast)\b"
    r"|\bnothing (?:more|else) to (?:do|say) (?:here|right now)\b"
    r")",
    re.IGNORECASE,
)

# Single-concrete-consequence vocabulary ("name one concrete consequence").
F13_DWELL_CONSEQUENCE_RE = re.compile(
    r"("
    r"\bthe next time\b"
    r"|\bso (?:tonight|tomorrow|today|the next)\b"
    r"|\bthe choice is (?:already|now)\b"
    r"|\bwhich is why,? the next\b"
    r"|\band you get to\b"
    r"|\bthat is the (?:moment|cost|price)\b"
    r")",
    re.IGNORECASE,
)


def _f13_is_insight(sentence: str) -> bool:
    return bool(F13_INSIGHT_RE.search(sentence))


def _f13_is_dwell_beat(sentence: str) -> bool:
    """
    True when the sentence is a dwell beat: a body landing, a held silence, or a
    single concrete consequence — AND it is ≤~40 words ("a held breath, not a
    passage", §7.3). A long sentence, even if sensory, is not a dwell beat.
    """
    if len(sentence.split()) > F13_DWELL_MAX_WORDS:
        return False
    return bool(
        F13_DWELL_BODY_RE.search(sentence)
        or F13_DWELL_SILENCE_RE.search(sentence)
        or F13_DWELL_CONSEQUENCE_RE.search(sentence)
    )


def _detect_f13_dwell_starvation(
    chapters: list[tuple[int, str]],
) -> list[RegisterFinding]:
    """
    Detect integration starvation per §13 criterion #13: 3+ CONSECUTIVE named
    insight sentences with no dwell beat between them.

    Walks each chapter's sentences in order, tracking the current run of
    consecutive insight sentences. A dwell beat (or a long non-insight sentence
    that is itself not an insight) resets the run. When a run reaches
    F13_CONSECUTIVE_INSIGHT_FAIL, the chapter FAILS criterion #13.
    """
    findings: list[RegisterFinding] = []
    for ch_num, ch_text in chapters:
        sentences = _split_sentences(ch_text)
        run = 0               # current consecutive-insight run length
        worst_run = 0
        worst_run_sents: list[str] = []
        cur_run_sents: list[str] = []
        flagged = False
        for sent in sentences:
            if _f13_is_dwell_beat(sent):
                # A dwell beat breaks the run — the reader gets to stay.
                run = 0
                cur_run_sents = []
                continue
            if _f13_is_insight(sent):
                run += 1
                cur_run_sents.append(sent)
                if run > worst_run:
                    worst_run = run
                    worst_run_sents = list(cur_run_sents)
                if run >= F13_CONSECUTIVE_INSIGHT_FAIL and not flagged:
                    findings.append(RegisterFinding(
                        failure_id="F13",
                        severity="FAIL",
                        chapter=ch_num,
                        summary=(
                            f"integration starvation — {run}+ consecutive named "
                            f"insights with no dwell beat between them "
                            f"(criterion #13 broken band; §7.3 dwell contract)"
                        ),
                        evidence={
                            "criterion": 13,
                            "consecutive_insights": run,
                            "threshold": F13_CONSECUTIVE_INSIGHT_FAIL,
                            "run_excerpt": [s[:120] for s in cur_run_sents[:5]],
                            "spec_ref": "OVERLAY_SPEC §7.3 / §13 criterion #13",
                        },
                    ))
                    flagged = True
            else:
                # Neutral, non-insight, non-dwell sentence. It is not teaching, but
                # the spec's diagnostic is specifically about consecutive INSIGHT
                # sentences with no dwell BEAT between them — a neutral connective
                # is not a dwell beat, so it does not reset the run.
                continue
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
        "F11": "Pearl_Editor (HOOK/ANGLE_DEFINITION scene-first rewrite per HOOK-SCENE-FIRST-01)",
        "F12": "Pearl_Dev (route teacher/science register through teacher_wrapper / science_wrapper per BESTSELLER-FIT-PLAN-VOICE-DOCTRINE-V1-01) + Pearl_Editor (re-attribute the raw shift; shares D12 VoiceOutOfZoneError vocab)",
        "F13": "Pearl_Editor + Pearl_Writer (re-pace per §7.3 dwell contract — insert a dwell beat after each named insight; §13 criterion #13)",
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
    hook_atoms: Optional[list[tuple[str, str]]] = None,
    f11_all_variations: bool = False,
) -> RegisterGateResult:
    """
    Score the rendered book against the F1-F7 + F12 + F13 detectors
    (+ optional F11 on HOOK atoms).

    F8 (citation grafting) is deferred until anchor corpus
    (artifacts/reference/trade_pub_anchors/) lands.

    F12 (un-wrapped voice-shift, BESTSELLER-FIT-PLAN-VOICE-DOCTRINE-V1-01) and F13
    (dwell-beat / integration starvation, §7.3 + §13 criterion #13) are book-level
    deterministic detectors and always run on the chapter text.

    When hook_atoms is provided, each entry is (atom_path, CANONICAL.txt text) and
    F11 runs per HOOK-SCENE-FIRST-01 (WARN-only in V1).

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
    findings += _detect_f12_unwrapped_voice_shift(chapters)
    findings += _detect_f13_dwell_starvation(chapters)
    if hook_atoms:
        if f11_all_variations:
            findings += _detect_f11_hook_abstract_opening_all_variations(hook_atoms)
        else:
            findings += _detect_f11_hook_abstract_opening(hook_atoms)

    verdict = _aggregate_verdict(findings)
    lanes = _route_suggested_lanes(findings)

    book_metrics: dict = {
        "chapter_count": len(chapters),
        "word_count": len(book_text.split()),
        "teacher_id": teacher_id,
        "persona_id": persona_id,
        "topic_id": topic_id,
        "quality_profile": quality_profile,
        "spec_version": "1.0.0",
        "f8_deferred": "anchor_corpus_required",
    }
    if hook_atoms is not None:
        book_metrics["f11_hook_atoms_checked"] = len(hook_atoms)

    return RegisterGateResult(
        verdict=verdict,
        findings=findings,
        book_metrics=book_metrics,
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
    parser = argparse.ArgumentParser(description="Score a Pearl Prime book.txt against the register gate (F1-F7, F12, F13, optional F11).")
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
