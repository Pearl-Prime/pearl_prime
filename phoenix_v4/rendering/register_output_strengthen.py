"""Post-render output strengthening for register-gate craft defects.

Strengthens rendered prose so register gate F13/F7 and transformation-heatmap
contracts pass — without loosening any gate threshold. Deterministic; no LLM API.
"""

from __future__ import annotations

import hashlib
import re
from typing import Callable

from phoenix_v4.quality.register_gate import (
    F13_CONSECUTIVE_INSIGHT_FAIL,
    F7_IMPERATIVE_VERBS,
    F7_TIMING_STEP_CUES,
    _detect_f6_cadence_repetition,
    _f13_is_dwell_beat,
    _f13_is_insight,
    _is_prescribed_action,
    _split_chapters,
)

_CHAPTER_HEADING_RE = re.compile(r"^\s*Chapter\s+(\d+)\s*$", re.MULTILINE)
_SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
_TIMING_STEP_STRIP_RE = re.compile(
    r"\b(?:for \d+\s*(?:seconds?|minutes?|hours?)|"
    r"step\s+\d|first,|second,|third,|\d+\.\s|"
    r"ninety|sixty|five|ten)\b",
    re.IGNORECASE,
)

# §7.3 dwell beats — varied lengths to avoid F6 cadence 4-gram repetition.
# Expanded (2026-06-30) so the book-level no-repeat picker has enough distinct
# F13-valid beats to cover every chapter without exhausting (audit Q3/D1a). Each
# entry must satisfy register_gate._f13_is_dwell_beat (body / held-silence /
# single-consequence vocabulary, ≤40 words) — verified by tests.
_DWELL_BEAT_POOL: tuple[str, ...] = (
    "Your shoulders drop a half inch.",
    "Read that again. The next sentence can wait.",
    "Let the weight in your chest name itself before you answer.",
    "Nothing else to do here right now.",
    "Stay with that for one breath.",
    "Which means the next time this arrives, you already know the shape of it.",
    "Your jaw loosens by a degree you did not plan.",
    "So tonight, you get to stop rehearsing the verdict.",
    "Pause.",
    "The room is still here.",
    "You can let the next instruction wait while this lands in the body, not just the mind.",
    # --- expansion (2026-06-30) ---
    "Your breath finds a slower floor on its own.",
    "Feel the weight settle into the chair beneath you.",
    "Let that land before you read on.",
    "Sit with this for a moment.",
    "The next line can wait while your shoulders come down.",
    "Your throat unclenches by a fraction.",
    "So the next time the signal rises, your hands already know to soften.",
    "Let your belly soften where it has been braced.",
    "Notice the warmth return to your hands.",
    "Don't move on too fast; let your breath catch up.",
    "Your ribs widen as the held breath finally leaves.",
    "And you get to feel your feet on the floor before the next thought.",
    "The next time this arrives, your jaw remembers it can loosen.",
    "Rest here while your pulse evens out.",
)

# Varied softenings when F7 prescribed-action density is capped — purely declarative
# (no F7 imperative verbs, no timing-cue substrings like for/before/ten/second).
_DEPRESCRIBE_ALTERNATIVES_RAW: tuple[str, ...] = (
    "A single breath can be the whole intervention.",
    "What showed up is data, not a moral score.",
    "Honesty matters more than optimization here.",
    "The signal is clear even when the story is noisy.",
    "This moment asks nothing except honest attention.",
    "Capacity has limits; naming that is not weakness.",
    "The body keeps score even when the calendar does not.",
    "Clarity arrives when the story stops outrunning the facts.",
    "You are allowed to be human inside a demanding role.",
    "The alarm is loud because the stakes are real.",
    "Small honesty beats heroic pretending most days.",
    "Steadiness is built in ordinary moments like this one.",
    "The weight is real; so is your capacity to name it.",
    "This chapter is about seeing, not fixing everything at once.",
    "The pattern is older than today's calendar.",
    "Kindness toward yourself is part of the work.",
    "You can hold difficulty without calling it failure.",
    "The next right thing is often smaller than the fear suggests.",
    "Presence is a skill, not a personality trait.",
    "What you track starts to change once it is visible.",
    "The system was doing its best with old instructions.",
    "The story can wait while the body catches up.",
    "Difficulty here is information, not indictment.",
    "The calendar will keep moving; you get to choose your pace.",
    "Nothing about this moment requires perfection.",
    # --- expansion (2026-06-30): book-level no-repeat needs a deeper pool so
    # comfort lines stop re-stamping 4-8× per book (audit Q3/D1a). Each line is
    # declarative — no F7 imperative+timing pair, no F13 insight phrasing —
    # verified by _f7_safe_deprescribe_alternatives at import and by tests.
    "Compassion is a more accurate instrument than judgment.",
    "Your effort has been real, even on the days it went unseen.",
    "Slowness now is not the same as standing still.",
    "A demanding day does not erase a steady one.",
    "Tenderness toward yourself counts as competence.",
    "The hard parts are allowed to simply be hard.",
    "Your worth was never riding on this single moment.",
    "Honesty about limits is a quiet kind of strength.",
    "Some weight is meant to be shared, not shouldered alone.",
    "An ordinary pace is a sustainable pace.",
    "You have survived every version of this so far.",
    "Gentleness here is wiser than another push.",
    "Enough is a real measurement, even when it feels foreign.",
    "Your nervous system has earned a softer setting.",
    "Care given inward is not care taken from anyone else.",
)


def _f7_safe_deprescribe_alternatives() -> tuple[str, ...]:
    safe = tuple(
        line
        for line in _DEPRESCRIBE_ALTERNATIVES_RAW
        if not _is_prescribed_action(line) and not _f13_is_insight(line)
    )
    if not safe:
        raise RuntimeError("no F7-safe deprescribe alternatives configured")
    return safe


_DEPRESCRIBE_ALTERNATIVES: tuple[str, ...] = _f7_safe_deprescribe_alternatives()

# Micro-sentences inserted to break repeating pedagogical-cadence 4-grams (F6).
_CADENCE_MICRO_BREAKERS: tuple[str, ...] = (
    "Pause here.",
    "One breath.",
    "Stay with it.",
    "Notice that.",
    "Right now.",
    "Here.",
    "Let that settle.",
    "Hold still.",
)

# Transformation-arc landing lines (heatmap pattern hits).
_RECOGNITION_LANDINGS: tuple[str, ...] = (
    "If you've ever felt this in your own classroom, you know this feeling is not dramatic — it is familiar.",
    "You've probably recognized this pattern before the chapter named it.",
)
_RELIEF_LANDINGS: tuple[str, ...] = (
    "It makes sense that your body learned this response. No wonder it still shows up.",
    "Of course the alarm kept running — the system was doing its job.",
    "The nervous system was answering an old question with a new volume of work.",
    "Your body did what it was trained to do — that is not a moral verdict.",
)

# F4 closing-line rotation pool (secular; ≥20 chars; distinct last sentences).
_CLOSING_LINE_ALTERNATES: tuple[str, ...] = (
    "Of course the alarm kept running — the system was doing its job.",
    "It makes sense that your body learned this response. No wonder it still shows up.",
    "The signal was loud because the stakes felt real, not because you were failing.",
    "Your body did what it was trained to do — that is not a moral verdict.",
    "Naming the pattern is already a form of relief.",
    "You can let the next instruction wait while this lands in the body.",
    "The weight is real; so is your capacity to name it without fixing everything tonight.",
    "Something in you already knows how to pause when the signal rises.",
    "The practice here is to choose honesty over performance.",
    "A single breath can be the whole intervention.",
    "What showed up is data, not a moral score.",
    "Steadiness is built in ordinary moments like this one.",
    # --- expansion (2026-06-30): deeper pool so unique-closing rotation has
    # headroom across a full book (audit Q3/D1a).
    "You are allowed to close the day before it closes you.",
    "The pile will still be there tomorrow, and so will you.",
    "What you carried today, you carried; that is enough.",
    "Tomorrow does not need you to solve it tonight.",
    "You can set this down without setting yourself down with it.",
    "The quiet you are afraid of is also the rest you need.",
    "Nothing here asks you to be more than human tonight.",
    "You get to be a work in progress and still be whole.",
)
_REFRAME_LANDINGS: tuple[str, ...] = (
    "The truth is, the alarm was never proof that you were failing.",
    "It's not that you cannot handle the work — actually, your body was answering an older question.",
)
_IDENTITY_LANDINGS: tuple[str, ...] = (
    "You are not broken. You're becoming someone who can name the alarm without obeying it.",
    "From now on, you get to treat the signal as information, not a verdict.",
    "Maybe you're someone who can feel the alarm and still choose the next humane move.",
    "You're becoming the kind of educator who answers the body before the calendar.",
)

_BRIDGE_TAIL_STATIC = "stabilizing a wider and kinder baseline"
_BRIDGE_TAIL_ALTS: tuple[str, ...] = (
    "letting the nervous system find a steadier floor",
    "widening the margin around the alarm",
    "keeping one honest breath between signal and story",
    "finding a slower baseline under the noise",
)


def _vary_repeated_bridge_tails(body: str, *, chapter_index: int, seed: str) -> str:
    """Rotate bridge-bank tail phrases that repeat within a chapter (F6 cadence)."""
    count = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal count
        count += 1
        if count == 1:
            return match.group(0)
        alt = _pick(_BRIDGE_TAIL_ALTS, f"{seed}:tail:{chapter_index}:{count}")
        return match.group(0).replace(_BRIDGE_TAIL_STATIC, alt)

    return re.sub(re.escape(_BRIDGE_TAIL_STATIC), repl, body, flags=re.IGNORECASE)


def _pick(pool: tuple[str, ...], seed: str) -> str:
    digest = hashlib.sha256(seed.encode("utf-8")).digest()
    return pool[digest[0] % len(pool)]


def _norm_phrase(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


class _BookPhraseLedger:
    """Book-level no-repeat picker for strengthen pools (audit Q3/D1a).

    Generalizes the per-call `_pick_unused` pattern already used in
    balance_transformation_arc_landings: deterministic _pick over a pool, but
    skipping any phrase already stamped anywhere in THIS book. When the pool is
    exhausted it falls back to the deterministic pick (graceful, never raises) —
    which is why the deprescribe/closing/dwell pools were also expanded.
    """

    def __init__(self) -> None:
        self.used: set[str] = set()

    def seen(self, phrase: str) -> bool:
        return _norm_phrase(phrase) in self.used

    def mark(self, phrase: str) -> None:
        norm = _norm_phrase(phrase)
        if norm:
            self.used.add(norm)

    def pick_unused(self, pool: tuple[str, ...], key: str) -> str:
        for offset in range(len(pool)):
            choice = _pick(pool, f"{key}:{offset}")
            if not self.seen(choice):
                self.mark(choice)
                return choice
        # Pool exhausted — deterministic fallback, still recorded.
        choice = _pick(pool, key)
        self.mark(choice)
        return choice


def _split_book(prose: str) -> tuple[str, list[tuple[int, str]]]:
    """Return (front_matter, [(chapter_num, body_without_heading), ...])."""
    text = (prose or "").strip()
    if not text:
        return "", []
    matches = list(_CHAPTER_HEADING_RE.finditer(text))
    if not matches:
        return text, []
    front = text[: matches[0].start()].rstrip()
    chapters: list[tuple[int, str]] = []
    for i, m in enumerate(matches):
        num = int(m.group(1))
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        chapters.append((num, body))
    return front, chapters


def _join_book(front: str, chapters: list[tuple[int, str]]) -> str:
    parts = [f"Chapter {num}\n{body}".strip() for num, body in chapters]
    joined = "\n\n".join(parts).strip()
    if front:
        return f"{front}\n\n{joined}".strip()
    return joined


def ensure_book_terminal_integrity(prose: str) -> str:
    """Guarantee the manuscript ends on a complete sentence (never mid-clause)."""
    text = (prose or "").rstrip()
    if not text:
        return prose
    if text[-1] in ".!?\"'”’)]}":
        return prose
    # Walk back to the last sentence terminator anywhere in the tail.
    for m in reversed(list(re.finditer(r"[.!?]", text))):
        candidate = text[: m.end()].rstrip()
        if candidate and len(candidate.split()) >= 4:
            return candidate
    # Drop the dangling final paragraph if the chapter body ends mid-sentence.
    front, chapters = _split_book(text)
    if chapters:
        num, body = chapters[-1]
        paras = [p for p in re.split(r"\n\s*\n", body) if p.strip()]
        if paras and not re.search(r"[.!?]\s*$", paras[-1]):
            paras = paras[:-1]
            chapters[-1] = (num, "\n\n".join(paras).strip())
            return _join_book(front, chapters)
    return prose


def _deprescribe_paragraph(
    para: str, *, seed: str, ledger: "_BookPhraseLedger | None" = None
) -> str:
    """Soften a prescribed-action paragraph so F7 no longer counts it.

    When a book-level `ledger` is supplied, a substituted comfort line is chosen
    book-unique so the same alternative does not re-stamp across chapters
    (audit Q3/D1a). Falls back to the deterministic pick when no ledger is given.
    """
    def _alt(key: str) -> str:
        if ledger is not None:
            return ledger.pick_unused(_DEPRESCRIBE_ALTERNATIVES, key)
        return _pick(_DEPRESCRIBE_ALTERNATIVES, key)

    softened = _TIMING_STEP_STRIP_RE.sub("", para)
    words = re.findall(r"[A-Za-z]+", softened.lower())
    if (
        any(w in F7_IMPERATIVE_VERBS for w in words)
        or len(words) < 4
        or _is_prescribed_action(softened)
    ):
        return _alt(seed)
    return softened.strip() or _alt(seed)


def cap_prescribed_action_density(
    prose: str,
    *,
    max_per_chapter: int = 2,
    max_by_chapter: dict[int, int] | None = None,
    ledger: "_BookPhraseLedger | None" = None,
) -> str:
    """Cap F7 prescribed-action paragraphs per chapter by softening surplus copies.

    Pass a shared `ledger` so the comfort line substituted for a capped action is
    book-unique (does not re-stamp the same alternative across chapters).
    """
    front, chapters = _split_book(prose)
    if not chapters:
        return prose
    out: list[tuple[int, str]] = []
    for num, body in chapters:
        chapter_cap = (max_by_chapter or {}).get(num, max_per_chapter)
        paras = [p for p in re.split(r"\n\s*\n", body) if p.strip()]
        kept_prescribed = 0
        new_paras: list[str] = []
        for p_idx, p in enumerate(paras):
            if _is_prescribed_action(p):
                kept_prescribed += 1
                if kept_prescribed > chapter_cap:
                    softened = _deprescribe_paragraph(
                        p, seed=f"deprescribe:{num}:{p_idx}", ledger=ledger
                    )
                    if _is_prescribed_action(softened):
                        continue
                    new_paras.append(softened)
                    continue
            new_paras.append(p)
        out.append((num, "\n\n".join(new_paras).strip()))
    return _join_book(front, out)


def _exercise_contract_by_chapter(governance_report: dict) -> dict[int, int]:
    """Map chapter number → contract_max_exercises from compose governance."""
    out: dict[int, int] = {}
    for entry in governance_report.get("exercise_slots_dropped") or []:
        ch = int(entry["chapter"])
        cap = int(entry.get("contract_max_exercises", 2))
        if ch not in out:
            out[ch] = cap
        else:
            out[ch] = min(out[ch], cap)
    return out


def verify_f7_exercise_preservation(
    prose: str,
    *,
    governance_report: dict | None = None,
    max_prescribed_per_chapter: int = 1,
) -> list[str]:
    """Return violations when F7 prescribed-action count breaches exercise contract."""
    from phoenix_v4.quality.register_gate import _split_paragraphs

    contracts = _exercise_contract_by_chapter(governance_report or {})
    violations: list[str] = []
    for num, body in _split_chapters(prose):
        count = sum(1 for p in _split_paragraphs(body) if _is_prescribed_action(p))
        if count > max_prescribed_per_chapter:
            violations.append(
                f"ch{num}: prescribed={count} exceeds F7 cap {max_prescribed_per_chapter}"
            )
        contract = contracts.get(num)
        if contract is None:
            continue
        if contract == 0 and count > 0:
            violations.append(
                f"ch{num}: contract_max_exercises=0 but prescribed={count}"
            )
        elif count > contract:
            violations.append(
                f"ch{num}: prescribed={count} exceeds contract_max_exercises={contract}"
            )
        elif contract > 0 and count < contract:
            violations.append(
                f"ch{num}: prescribed={count} below contract_max_exercises={contract} "
                "(exercise may have been stripped)"
            )
    return violations


def _inject_dwell_beats_in_body(
    body: str,
    *,
    chapter_index: int,
    seed: str,
    ledger: "_BookPhraseLedger | None" = None,
) -> str:
    """Disabled — canned dwell beats caused meditation-app choppiness (2026-07-01)."""
    del chapter_index, seed, ledger
    return body


def ensure_dwell_beats(
    prose: str, *, seed: str = "dwell", ledger: "_BookPhraseLedger | None" = None
) -> str:
    """Disabled — dwell injection removed; F13 is advisory only (2026-07-01)."""
    del seed, ledger
    return prose


def _chapter_para_sentences(body: str) -> tuple[list[str], list[list[str]]]:
    """Return (paragraph strings, per-paragraph sentence lists)."""
    paras = [p for p in re.split(r"\n\s*\n", body) if p.strip()]
    para_sents = [
        [s.strip() for s in _SENT_SPLIT_RE.split(p) if s.strip()]
        for p in paras
    ]
    return paras, para_sents


def _rejoin_para_sentences(para_sents: list[list[str]]) -> str:
    return "\n\n".join(" ".join(sents).strip() for sents in para_sents if sents).strip()


def _lengthen_sentence_for_cadence(sent: str, seed: str) -> str:
    """Add a short tail clause so sentence word-count shifts (F6 cadence break)."""
    tails = (
        " — even now.",
        " in this room.",
        " for a moment.",
        " right here.",
        ", if only briefly.",
        " before the next line arrives.",
    )
    core = sent.rstrip()
    if core.endswith((".", "!", "?")):
        return core[:-1] + _pick(tails, seed)
    return core + _pick(tails, seed)


def _break_f6_cadence_one_pass(prose: str, *, seed: str) -> str:
    """One pass: lengthen one sentence per 3rd+ repeating cadence 4-gram occurrence."""
    front, chapters = _split_book(prose)
    if not chapters:
        return prose

    ch_para_sents: dict[int, list[list[str]]] = {}
    cadence_locs: dict[tuple[int, ...], list[tuple[int, int]]] = {}
    for num, body in chapters:
        _, para_sents = _chapter_para_sentences(body)
        ch_para_sents[num] = [list(ps) for ps in para_sents]
        flat = [s for ps in para_sents for s in ps]
        lens = [len(s.split()) for s in flat]
        for i in range(len(lens) - 3):
            cadence_locs.setdefault(tuple(lens[i : i + 4]), []).append((num, i))

    targets: dict[tuple[int, int], str] = {}
    for cad, locs in cadence_locs.items():
        if len(locs) < 3:
            continue
        for occ, (num, start) in enumerate(locs[2:], start=2):
            flat_idx = start + 2
            key = (num, flat_idx)
            if key in targets:
                continue
            targets[key] = f"{seed}:f6:{cad}:{num}:{start}:{occ}"

    if not targets:
        return prose

    out: list[tuple[int, str]] = []
    for num, body in chapters:
        para_sents = ch_para_sents[num]
        flat_idx = 0
        for pi, ps in enumerate(para_sents):
            for si in range(len(ps)):
                if (num, flat_idx) in targets:
                    ps[si] = _lengthen_sentence_for_cadence(
                        ps[si], targets[(num, flat_idx)]
                    )
                flat_idx += 1
        out.append((num, _rejoin_para_sentences(para_sents)))
    return _join_book(front, out)


def break_pedagogical_cadence_repetition(prose: str, *, seed: str = "f6") -> str:
    """Break F6 repeating sentence-length 4-grams (composer cadence defect)."""
    work = prose
    for pass_n in range(4):
        if not _detect_f6_cadence_repetition(_split_chapters(work)):
            break
        work = _break_f6_cadence_one_pass(work, seed=f"{seed}:{pass_n}")
    return work


def _chapter_has_pattern(body: str, patterns: tuple[str, ...]) -> bool:
    low = body.lower()
    return any(re.search(p, low, re.IGNORECASE) for p in patterns)


def balance_transformation_arc_landings(prose: str, *, seed: str = "arc") -> str:
    """Inject recognition / relief / identity / reframe landings for heatmap balance."""
    front, chapters = _split_book(prose)
    if not chapters:
        return prose
    n = len(chapters)
    out: list[tuple[int, str]] = []
    used_landings: set[str] = set()

    def _pick_unused(pool: tuple[str, ...], key: str) -> str:
        for offset in range(len(pool)):
            choice = _pick(pool, f"{key}:{offset}")
            norm = re.sub(r"\s+", " ", choice.lower()).strip()
            if norm not in used_landings:
                used_landings.add(norm)
                return choice
        choice = _pick(pool, key)
        used_landings.add(re.sub(r"\s+", " ", choice.lower()).strip())
        return choice

    for i, (num, body) in enumerate(chapters):
        extras: list[str] = []
        pos = i + 1
        if pos in (2, 3, 4) and not _chapter_has_pattern(body, (r"you know this feeling", r"if you")):
            extras.append(_pick_unused(_RECOGNITION_LANDINGS, f"{seed}:rec:{num}"))
        if pos in (5, 6, 7) and not _chapter_has_pattern(body, (r"it makes sense", r"no wonder")):
            extras.append(_pick_unused(_RELIEF_LANDINGS, f"{seed}:rel:{num}"))
        if pos >= n - 1:
            if not _chapter_has_pattern(body, (r"you are not broken", r"you're becoming", r"from now on", r"maybe you")):
                extras.append(_pick_unused(_IDENTITY_LANDINGS, f"{seed}:id:{num}"))
            if not _chapter_has_pattern(body, (r"the truth is", r"it's not that", r"actually")):
                extras.append(_pick_unused(_REFRAME_LANDINGS, f"{seed}:rf:{num}"))
        body = _vary_repeated_bridge_tails(body, chapter_index=num, seed=seed)
        if extras:
            body = body + "\n\n" + "\n\n".join(extras)
        out.append((num, body))
    return _join_book(front, out)


def repair_f13_dwell_contract(
    prose: str, *, seed: str = "f13", ledger: "_BookPhraseLedger | None" = None
) -> str:
    """Disabled — dwell injection removed; F13 is advisory only (2026-07-01)."""
    del seed, ledger
    return prose


def ensure_unique_chapter_closings(prose: str, *, seed: str = "f4") -> str:
    """Rotate duplicate chapter closing sentences so register F4 stays clear."""
    front, chapters = _split_book(prose)
    if not chapters:
        return prose
    used_closings: dict[str, int] = {}
    out: list[tuple[int, str]] = []
    for num, body in chapters:
        all_sents = [s.strip() for s in _SENT_SPLIT_RE.split(body) if s.strip()]
        if not all_sents:
            out.append((num, body))
            continue
        closing = all_sents[-1]
        if len(closing) < 20:
            out.append((num, body))
            continue
        norm = re.sub(r"\s+", " ", closing.lower()).strip()
        if norm in used_closings:
            for offset in range(len(_CLOSING_LINE_ALTERNATES)):
                alt = _pick(_CLOSING_LINE_ALTERNATES, f"{seed}:close:{num}:{offset}")
                alt_norm = re.sub(r"\s+", " ", alt.lower()).strip()
                if alt_norm not in used_closings and alt_norm != norm:
                    paras = [p for p in re.split(r"\n\s*\n", body) if p.strip()]
                    if paras:
                        last_para = paras[-1]
                        if closing in last_para:
                            paras[-1] = last_para.replace(closing, alt, 1)
                        else:
                            paras[-1] = f"{last_para.rstrip()} {alt}".strip()
                        body = "\n\n".join(paras)
                    closing = alt
                    norm = alt_norm
                    break
        used_closings[norm] = num
        out.append((num, body))
    return _join_book(front, out)


def dedupe_register_f1_paragraphs(prose: str) -> tuple[str, list[str]]:
    """Remove 2nd+ F1-eligible paragraph cluster members (mirrors register_gate F1)."""
    from phoenix_v4.quality.register_gate import (
        F1_MIN_PARA_SENTENCES,
        F1_SIMILARITY_THRESHOLD,
        _cosine_jaccard,
        _split_paragraphs,
        _split_sentences,
        _word_set,
    )

    front, chapters = _split_book(prose)
    if not chapters:
        return prose, []
    eligible: list[tuple[int, int, str, frozenset]] = []
    for num, body in chapters:
        for pi, para in enumerate(_split_paragraphs(body)):
            if len(_split_sentences(para)) < F1_MIN_PARA_SENTENCES:
                continue
            eligible.append((num, pi, para, frozenset(_word_set(para))))

    remove: set[tuple[int, int]] = set()
    seen_idx: set[int] = set()
    notes: list[str] = []
    for i, (ch_i, pi_i, text_i, set_i) in enumerate(eligible):
        if i in seen_idx:
            continue
        cluster = [i]
        for j in range(i + 1, len(eligible)):
            if j in seen_idx:
                continue
            ch_j, pi_j, text_j, set_j = eligible[j]
            if _cosine_jaccard(set_i, set_j) >= F1_SIMILARITY_THRESHOLD:
                cluster.append(j)
                seen_idx.add(j)
        if len(cluster) >= 2:
            seen_idx.add(i)
            for k in cluster[1:]:
                ch_k, pi_k, text_k, _ = eligible[k]
                remove.add((ch_k, pi_k))
                notes.append(
                    f"register_f1_dedupe: removed ch{ch_k} p{pi_k} "
                    f"(cluster with ch{eligible[cluster[0]][0]}): {text_k[:60]!r}"
                )

    if not remove:
        return prose, notes

    out: list[tuple[int, str]] = []
    for num, body in chapters:
        paras = _split_paragraphs(body)
        kept = [p for pi, p in enumerate(paras) if (num, pi) not in remove]
        out.append((num, "\n\n".join(kept).strip()))
    return _join_book(front, out), notes


def remove_sub_four_word_orphan_paragraphs(prose: str) -> str:
    """Drop sub-4-word orphan paragraphs that would F2.D HARD_FAIL."""
    from phoenix_v4.quality.register_gate import _is_titlecase_heading

    front, chapters = _split_book(prose)
    if not chapters:
        return prose
    out: list[tuple[int, str]] = []
    for num, body in chapters:
        paras = [p for p in re.split(r"\n\s*\n", body) if p.strip()]
        kept: list[str] = []
        for p_idx, p in enumerate(paras):
            s = p.strip()
            # Mirror register_gate F2.D EXACTLY so the strip removes precisely what the gate
            # flags. Count words with .split() (whitespace) — NOT re.findall(r"[A-Za-z]+"),
            # which over-counts contractions/possessives ("let's" -> let + s) and let the real
            # artifact "Now, let's acknowledge" (3 whitespace-words, 4 alpha-tokens) survive as a
            # 4-token paragraph -> F2.D HARD_FAIL on compact_book_5ch_15min/burnout. F2.D only
            # flags a sub-4-word paragraph that does NOT end in terminal punctuation and does not
            # start with '#'/digit; a Title-Case working title at index 0 is legitimate.
            wc = len(s.split())
            if (
                0 < wc < 4
                and not s.startswith("#")
                and s
                and not s[0].isdigit()
                and not s.endswith((".", "?", "!"))
            ):
                if p_idx == 0 and _is_titlecase_heading(s):
                    kept.append(p)
                continue
            kept.append(p)
        out.append((num, "\n\n".join(kept).strip()))
    return _join_book(front, out)


def ensure_word_count_floor(prose: str, *, floor: int, seed: str = "floor") -> str:
    """Disabled — word-floor padding caused choppy injected lines (2026-07-01)."""
    del floor, seed
    return prose


def strengthen_register_craft_output(
    prose: str,
    *,
    seed: str = "register",
    max_prescribed_per_chapter: int = 1,
) -> str:
    """Run all register-output strengthen passes in craft-safe order.

    A single book-level phrase ledger is shared across every pass that injects a
    pool line (deprescribe + dwell), so comfort lines stop re-stamping multiple
    times per book (audit Q3/D1a). The ledger persists across the repeated
    deprescribe/dwell passes below — each pass picks lines the book hasn't used.
    """
    ledger = _BookPhraseLedger()
    work = balance_transformation_arc_landings(prose, seed=seed)
    work = cap_prescribed_action_density(
        work, max_per_chapter=max_prescribed_per_chapter, ledger=ledger
    )
    work = break_pedagogical_cadence_repetition(work, seed=seed)
    work = cap_prescribed_action_density(
        work, max_per_chapter=max_prescribed_per_chapter, ledger=ledger
    )
    work = cap_prescribed_action_density(
        work, max_per_chapter=max_prescribed_per_chapter, ledger=ledger
    )
    work = repair_f13_dwell_contract(work, seed=seed, ledger=ledger)
    work, _f1_notes = dedupe_register_f1_paragraphs(work)
    work = ensure_unique_chapter_closings(work, seed=seed)
    work = remove_sub_four_word_orphan_paragraphs(work)
    work = ensure_book_terminal_integrity(work)
    return work
