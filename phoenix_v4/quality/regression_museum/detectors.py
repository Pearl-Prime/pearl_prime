"""
Regression Museum — deterministic detectors. No LLM. No flaky state.
One function per failure_class in regression_museum.yaml.
Each returns list[Violation]. Each is fast (regex or hash).
"""

import re
import hashlib
import collections
from dataclasses import dataclass
from typing import Optional


@dataclass
class Violation:
    failure_class: str
    severity: str        # "block" | "warn"
    location: str        # e.g. "chapter_3:paragraph_7"
    evidence: str        # excerpt that tripped the gate
    description: str


# ── helpers ──────────────────────────────────────────────────────────────────

def _chapters(book: dict) -> list[dict]:
    return book.get("chapters", [])


def _chapter_text(ch: dict) -> str:
    return ch.get("text", ch.get("content", ""))


def _snippet(text: str, start: int, end: int, pad: int = 40) -> str:
    return text[max(0, start - pad): end + pad]


# ── detectors ─────────────────────────────────────────────────────────────────

def detect_template_dict_artifact(book: dict, **_) -> list[Violation]:
    pat = re.compile(r"\{['\"]?\w+['\"]?\s*:\s*['\"]")
    out = []
    for ch in _chapters(book):
        text = _chapter_text(ch)
        for m in pat.finditer(text):
            out.append(Violation(
                failure_class="template_dict_artifact",
                severity="block",
                location=f"chapter_{ch.get('index', '?')}:char_{m.start()}",
                evidence=_snippet(text, m.start(), m.end()),
                description="Python dict syntax leaked into rendered prose",
            ))
    return out


def detect_font_css_leak(book: dict, **_) -> list[Violation]:
    pat = re.compile(r"[A-Za-z]+;\s*;;")
    out = []
    for ch in _chapters(book):
        text = _chapter_text(ch)
        for m in pat.finditer(text):
            out.append(Violation(
                failure_class="font_css_leak",
                severity="block",
                location=f"chapter_{ch.get('index', '?')}:char_{m.start()}",
                evidence=_snippet(text, m.start(), m.end()),
                description="CSS/font directive leaked into prose",
            ))
    return out


def detect_doubled_word(book: dict, exceptions: Optional[list] = None, **_) -> list[Violation]:
    pat = re.compile(r"\b([A-Za-z]{2,})\s+\1\b", re.IGNORECASE)
    skip = {e.lower() for e in (exceptions or ["had had", "that that", "do do", "very very", "is is"])}
    out = []
    for ch in _chapters(book):
        text = _chapter_text(ch)
        for m in pat.finditer(text):
            if m.group(0).lower() in skip:
                continue
            out.append(Violation(
                failure_class="doubled_word",
                severity="block",
                location=f"chapter_{ch.get('index', '?')}:char_{m.start()}",
                evidence=_snippet(text, m.start(), m.end()),
                description=f"Accidental word repetition: '{m.group(0)}'",
            ))
    return out


def detect_cross_chapter_verbatim_duplication(book: dict, ngram_size: int = 50, **_) -> list[Violation]:
    ngram_to_chapters: dict[str, set] = collections.defaultdict(set)
    ngram_sample: dict[str, str] = {}
    for ch in _chapters(book):
        words = _chapter_text(ch).split()
        idx = ch.get("index", "?")
        for i in range(len(words) - ngram_size + 1):
            ngram = " ".join(words[i: i + ngram_size]).lower()
            h = hashlib.sha256(ngram.encode()).hexdigest()[:16]
            ngram_to_chapters[h].add(idx)
            if h not in ngram_sample:
                ngram_sample[h] = ngram
    out = []
    seen: set[str] = set()
    for h, chapters in ngram_to_chapters.items():
        if len(chapters) > 1:
            sample = ngram_sample[h]
            key = sample[:80]
            if key in seen:
                continue
            seen.add(key)
            out.append(Violation(
                failure_class="cross_chapter_verbatim_duplication",
                severity="block",
                location=f"chapters:{sorted(chapters)}",
                evidence=sample[:200] + ("..." if len(sample) > 200 else ""),
                description=f"50+ word block repeated across chapters {sorted(chapters)}",
            ))
    return out


def detect_verbatim_chapter_block_repeat(book: dict, **_) -> list[Violation]:
    return detect_cross_chapter_verbatim_duplication(book, ngram_size=200)


_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+|\n+")
_WORD_RE = re.compile(r"[a-z0-9']+")


def _normalize_sentence(sentence: str) -> tuple[str, int]:
    """Lower-case, strip punctuation/whitespace; return (normalized, word_count)."""
    words = _WORD_RE.findall(sentence.lower())
    return " ".join(words), len(words)


def detect_cross_chapter_sentence_repeat(
    book: dict, min_words: int = 6, max_chapters_per_sentence: int = 1, **_
) -> list[Violation]:
    """Flag any normalized sentence of >= min_words that appears in >= 2 chapters.

    Durable backstop for the cohesion repeats that slip past the 50-word block
    detector and past every register gate (audit lever 4): named comfort lines
    and engine theses are short (6-15 words) but recur verbatim across chapters.
    Sentence-granularity, normalized (case/punctuation/whitespace-insensitive),
    deterministic, no LLM.
    """
    sentence_to_chapters: dict[str, set] = collections.defaultdict(set)
    sentence_sample: dict[str, str] = {}
    for ch in _chapters(book):
        text = _chapter_text(ch)
        idx = ch.get("index", "?")
        for raw in _SENTENCE_SPLIT_RE.split(text):
            norm, wc = _normalize_sentence(raw)
            if wc < min_words:
                continue
            sentence_to_chapters[norm].add(idx)
            if norm not in sentence_sample:
                sentence_sample[norm] = raw.strip()
    out: list[Violation] = []
    for norm, chapters in sentence_to_chapters.items():
        if len(chapters) > max_chapters_per_sentence:
            sample = sentence_sample[norm]
            out.append(Violation(
                failure_class="cross_chapter_sentence_repeat",
                severity="block",
                location=f"chapters:{sorted(chapters)}",
                evidence=sample[:200] + ("..." if len(sample) > 200 else ""),
                description=(
                    f"{min_words}+ word sentence repeated across "
                    f"{len(chapters)} chapters {sorted(chapters)}"
                ),
            ))
    # Stable ordering for deterministic reports.
    out.sort(key=lambda v: v.location)
    return out


def detect_off_persona_vocabulary(book: dict, persona: str = "", config: Optional[dict] = None, **_) -> list[Violation]:
    if not config:
        return []
    per_persona = config.get("per_persona", {})
    blocked = per_persona.get(persona, {}).get("blocked_terms", [])
    out = []
    for ch in _chapters(book):
        text = _chapter_text(ch)
        for term in blocked:
            for m in re.finditer(re.escape(term), text, re.IGNORECASE):
                out.append(Violation(
                    failure_class="off_persona_vocabulary",
                    severity="block",
                    location=f"chapter_{ch.get('index', '?')}:char_{m.start()}",
                    evidence=_snippet(text, m.start(), m.end()),
                    description=f"Off-persona term '{term}' in '{persona}' book",
                ))
    return out


def detect_same_exercise_overuse(book: dict, max_chapters_per_atom: int = 2, **_) -> list[Violation]:
    atom_uses: collections.Counter = collections.Counter()
    atom_chapters: dict = collections.defaultdict(list)
    for ch in _chapters(book):
        idx = ch.get("index", "?")
        for atom_id in ch.get("exercise_atom_ids", []):
            atom_uses[atom_id] += 1
            atom_chapters[atom_id].append(idx)
    out = []
    for atom_id, count in atom_uses.items():
        if count > max_chapters_per_atom:
            out.append(Violation(
                failure_class="same_exercise_overuse",
                severity="block",
                location=f"chapters:{atom_chapters[atom_id]}",
                evidence=f"atom_id={atom_id} used {count} times",
                description=f"Exercise atom {atom_id} used in {count} chapters (max {max_chapters_per_atom})",
            ))
    return out


def detect_identical_opening_scene(book: dict, window_words: int = 100, **_) -> list[Violation]:
    opening_hashes: dict[str, int] = {}
    out = []
    for ch in _chapters(book):
        words = _chapter_text(ch).split()
        snippet = " ".join(words[:window_words]).lower()
        h = hashlib.sha256(snippet.encode()).hexdigest()[:16]
        if h in opening_hashes:
            out.append(Violation(
                failure_class="identical_opening_scene",
                severity="block",
                location=f"chapters:{[opening_hashes[h], ch.get('index', '?')]}",
                evidence=snippet[:200],
                description=f"Chapter opening (first {window_words} words) matches chapter {opening_hashes[h]}",
            ))
        else:
            opening_hashes[h] = ch.get("index", "?")
    return out


def detect_generic_reader_address(book: dict, pattern: str = "", max_occurrences_per_book: int = 2, **_) -> list[Violation]:
    if not pattern:
        pattern = r"^(Many people|We all|Everyone|Most of us) "
    pat = re.compile(pattern, re.MULTILINE | re.IGNORECASE)
    all_hits = []
    for ch in _chapters(book):
        text = _chapter_text(ch)
        for m in pat.finditer(text):
            all_hits.append((ch.get("index", "?"), m.start(), _snippet(text, m.start(), m.end())))
    out = []
    if len(all_hits) > max_occurrences_per_book:
        for idx, pos, ev in all_hits:
            out.append(Violation(
                failure_class="generic_reader_address",
                severity="warn",
                location=f"chapter_{idx}:char_{pos}",
                evidence=ev,
                description=f"Generic reader address ({len(all_hits)} total, max {max_occurrences_per_book})",
            ))
    return out


def detect_repeated_scene_anchor(book: dict, pattern: str = "", max_occurrences_per_book: int = 3, **_) -> list[Violation]:
    if not pattern:
        pattern = r"soft daylight along the sill"
    pat = re.compile(re.escape(pattern), re.IGNORECASE)
    hits = []
    for ch in _chapters(book):
        text = _chapter_text(ch)
        for m in pat.finditer(text):
            hits.append((ch.get("index", "?"), m.start(), _snippet(text, m.start(), m.end())))
    out = []
    if len(hits) > max_occurrences_per_book:
        for idx, pos, ev in hits:
            out.append(Violation(
                failure_class="repeated_scene_anchor",
                severity="block",
                location=f"chapter_{idx}:char_{pos}",
                evidence=ev,
                description=f"Scene anchor repeated {len(hits)}× in book (max {max_occurrences_per_book})",
            ))
    return out


def detect_doctrinal_exposition_inline(book: dict, doctrine_terms: Optional[list] = None, abstract_nouns: Optional[list] = None, **_) -> list[Violation]:
    if not doctrine_terms:
        doctrine_terms = ["dharma", "karma", "bhakti", "enlightenment", "self-realization"]
    if not abstract_nouns:
        abstract_nouns = ["enlightenment", "consciousness", "awakening", "divine"]
    doctrine_pat = re.compile("|".join(re.escape(t) for t in doctrine_terms), re.IGNORECASE)
    abstract_pat = re.compile("|".join(re.escape(t) for t in abstract_nouns), re.IGNORECASE)
    out = []
    for ch in _chapters(book):
        paragraphs = re.split(r"\n\s*\n", _chapter_text(ch))
        for i, para in enumerate(paragraphs):
            has_doctrine = doctrine_pat.search(para)
            has_abstract = abstract_pat.search(para)
            if has_doctrine and has_abstract and len(para) > 80:
                out.append(Violation(
                    failure_class="doctrinal_exposition_inline",
                    severity="warn",
                    location=f"chapter_{ch.get('index', '?')}:paragraph_{i}",
                    evidence=para[:200],
                    description="Doctrinal exposition paragraph disconnected from narrative",
                ))
    return out


def detect_mid_paragraph_format_break(book: dict, **_) -> list[Violation]:
    # Paragraph ending without terminal punctuation
    pat = re.compile(r"[a-z,]\s*\n\s*\n", re.MULTILINE)
    out = []
    for ch in _chapters(book):
        text = _chapter_text(ch)
        for m in pat.finditer(text):
            out.append(Violation(
                failure_class="mid_paragraph_format_break",
                severity="warn",
                location=f"chapter_{ch.get('index', '?')}:char_{m.start()}",
                evidence=_snippet(text, m.start(), m.end()),
                description="Paragraph ends without terminal punctuation",
            ))
    return out
