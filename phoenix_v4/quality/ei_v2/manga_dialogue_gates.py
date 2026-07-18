"""EI V2 manga dialogue gates — MDLG-01 through MDLG-05.

These gates run as part of the ITE QC pipeline (after T-20) and score
per-chapter dialogue against five quality dimensions specific to the visual
medium of manga.

Gates
-----
MDLG-01  Engagement Hook     — dialogue creates forward momentum
MDLG-02  Somatic Precision   — body-experience grounding (conditional)
MDLG-03  Word Economy        — per-genre words-per-bubble ceilings
MDLG-04  Uniqueness          — series-wide de-duplication
MDLG-05  Cohesion            — matches chapter emotional_job (EI engine)

Each gate returns a ``GateResult`` (same dataclass used by prose gates in
``dimension_gates.py``) and an issue dict suitable for appending to
``build_revision_queue_for_chapter``'s issues list.

Thresholds
----------
Gate        PASS    WARN    BLOCK
MDLG-01    ≥0.65  0.45-   <0.45
MDLG-02    ≥0.70  0.50-   <0.50 (only when activated by somatic emotion)
MDLG-03    ≥0.70  0.50-   hard block if any bubble exceeds ceiling
MDLG-04    ≥0.75  0.60-   <0.60 or exact match
MDLG-05    ≥0.70  0.50-   <0.40

Overall chapter dialogue score = weighted average (weights sum to 1.0;
MDLG-02 weight redistributed to MDLG-01 when inactive).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import Any, Mapping, Sequence

from phoenix_v4.quality.ei_v2.dimension_gates import GateResult

# ---------------------------------------------------------------------------
# Genre word-per-bubble ceilings (from spec)
# ---------------------------------------------------------------------------

# (typical_max, hard_block_ceiling)
_GENRE_WORD_CEILINGS: dict[str, tuple[int, int]] = {
    "shonen": (20, 25),
    "shōnen": (20, 25),
    "shojo": (35, 45),
    "shōjo": (35, 45),
    "seinen": (55, 70),  # internal monologue can be long
    "josei": (35, 45),
    "kodomomuke": (18, 22),
    "isekai": (28, 35),
    "horror": (15, 20),
    "sports": (20, 26),
    "slice_of_life": (30, 38),
    "sl": (30, 38),
    "bl_gl": (32, 42),
    "mecha": (28, 35),
}
_DEFAULT_CEILINGS = (28, 35)

# ---------------------------------------------------------------------------
# EI engine → reinforcing / forbidden dialogue patterns
# ---------------------------------------------------------------------------

_ENGINE_REINFORCING_PATTERNS: dict[str, list[str]] = {
    "shame": [
        "not good enough", "can't do", "shouldn't have", "my fault",
        "embarrassing", "how could i", "worthless", "pathetic",
        "nobody wants", "hiding", "afraid they'll find out",
    ],
    "overwhelm": [
        "too much", "can't keep up", "everything at once", "where do i",
        "falling apart", "drowning", "i can't", "i don't know where",
        "nothing makes sense",
    ],
    "grief": [
        "miss", "used to", "they were", "never again", "lost", "gone",
        "before they", "back when", "can't forget", "still remember",
    ],
    "false_alarm": [
        "i was sure", "i thought", "mistaken", "it wasn't", "relief",
        "wait that's not", "never happened", "overreacted",
    ],
    "spiral": [
        "again", "always", "every time", "never stops", "same thing",
        "over and over", "why do i keep", "can't escape",
    ],
    "watcher": [
        "they", "from here", "watching", "standing back", "outside",
        "apart from", "separate", "none of this concerns",
    ],
    "comparison": [
        "better than me", "worse than", "more than i", "what's the point",
        "can't compare", "behind everyone", "ahead of me",
    ],
}

_ENGINE_FORBIDDEN_PATTERNS: dict[str, list[str]] = {
    "shame": ["proud", "confident", "i've got this", "no problem", "easy"],
    "overwhelm": ["everything is fine", "under control", "ready for anything"],
    "grief": ["let's go", "time to move", "excited", "can't wait", "future looks"],
    "false_alarm": ["real danger", "it's actually", "as expected"],
    "spiral": ["breaking the cycle", "finally free", "solved it"],
    "watcher": ["i feel", "my heart", "i want", "for me"],
    "comparison": ["unique", "my own path", "doesn't matter what others"],
}

# Somatic trigger emotions — MDLG-02 only activates for these
_SOMATIC_TRIGGER_EMOTIONS = frozenset({
    "fear", "grief", "determination_peak", "love_confession",
    "horror_encounter", "despair", "overwhelm", "panic",
    "determination",  # peak version identified by intensity
})

# Somatic vocabulary per genre
_SOMATIC_VOCAB: dict[str, list[str]] = {
    "shonen": ["fists", "clenching", "blood", "legs giving", "adrenaline", "heart pounding",
               "muscles burning", "breath ragged", "knees shaking", "chest tight"],
    "shojo": ["heart pounding", "face flushing", "stomach tightening", "tears blurring",
              "throat closing", "chest aching", "fingers trembling", "cheeks burning"],
    "seinen": ["numbness", "hollow", "weight", "sweat", "cold", "heavy",
               "chest empty", "can't feel", "numb to", "deadened"],
    "horror": ["cold creeping", "nausea", "skin crawling", "ears ringing",
               "shaking", "bile rising", "body won't move", "frozen"],
    "sports": ["lungs burning", "muscles screaming", "tunnel vision",
               "world going silent", "pain fading", "legs gone"],
}
_DEFAULT_SOMATIC = ["heart", "breath", "stomach", "hands shaking", "throat", "chest",
                    "body", "trembling", "cold sweat", "pulse"]

# Engagement hook indicators
_HOOK_PATTERNS = [
    r"\?",               # questions (reader keeps turning)
    r"\.{3}",            # trailing ellipsis (suspense)
    r"\b(but|yet|however|unless|except|until|if only)\b",  # conditional pivot
    r"\b(wait|stop|no|impossible|how|why)\b",              # shock/denial
    r"\b(you|we|i) (won't|can't|don't|never|always)\b",   # declaration
]

_SUMMARISING_PATTERNS = [
    r"\b(as you know|as we discussed|in summary|therefore|thus|we have)\b",
    r"\b(the reason is|this means that|the point is)\b",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _all_dialogue_texts(chapter_script: Mapping[str, Any]) -> list[str]:
    """Return flat list of all dialogue text strings from chapter_script."""
    texts: list[str] = []
    for page in chapter_script.get("pages") or []:
        for panel in page.get("panels") or []:
            dlg = panel.get("dialogue")
            if isinstance(dlg, list):
                for item in dlg:
                    if isinstance(item, str) and item.strip():
                        texts.append(item.strip())
                    elif isinstance(item, dict):
                        t = str(item.get("text") or "").strip()
                        if t:
                            texts.append(t)
    return texts


def _lettering_lines(lettering_spec: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Return all dialogue_line dicts from lettering_spec_v2."""
    lines: list[dict[str, Any]] = []
    for row in lettering_spec.get("lettering_panels") or []:
        for dl in row.get("dialogue_lines") or []:
            if isinstance(dl, dict):
                lines.append(dl)
    return lines


def _word_count(text: str) -> int:
    return len(text.split())


def _normalise_genre(raw: str) -> str:
    return raw.lower().replace("-", "_").replace(" ", "_").replace("ō", "o").replace("ū", "u")


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _make_issue(
    gate_id: str,
    score: float,
    threshold_block: float,
    threshold_warn: float,
    description: str,
) -> dict[str, Any] | None:
    """Return a revision_queue issue dict if gate failed, else None."""
    if score < threshold_block:
        return {
            "issue_code": f"{gate_id}_BLOCK",
            "gate_id": gate_id,
            "severity": "BLOCKER",
            "stage_owner": "chapter_lettering",
            "description": description,
        }
    if score < threshold_warn:
        return {
            "issue_code": f"{gate_id}_WARN",
            "gate_id": gate_id,
            "severity": "WARN",
            "stage_owner": "chapter_lettering",
            "description": description,
        }
    return None


# ---------------------------------------------------------------------------
# Gate implementations
# ---------------------------------------------------------------------------

def gate_dialogue_engagement(
    chapter_script: Mapping[str, Any],
    lettering_spec: Mapping[str, Any],
    genre: str,
) -> tuple[GateResult, dict[str, Any] | None]:
    """MDLG-01: Does dialogue create forward momentum?

    Scores based on presence of question marks, ellipsis, conditional pivots,
    shock/denial words, and declarations versus summarising/closing patterns.
    """
    texts = _all_dialogue_texts(chapter_script)
    if not texts:
        # No dialogue → gate not applicable → neutral pass
        result = GateResult("MDLG-01", "PASS", 1.0, [], [])
        return result, None

    full_text = " ".join(texts).lower()
    n = len(texts)

    hook_matches = sum(
        1 for pat in _HOOK_PATTERNS
        if re.search(pat, full_text, re.IGNORECASE)
    )
    close_matches = sum(
        1 for pat in _SUMMARISING_PATTERNS
        if re.search(pat, full_text, re.IGNORECASE)
    )

    # Score: hooks help, closing patterns hurt
    raw = (hook_matches / max(1, len(_HOOK_PATTERNS))) - 0.2 * (close_matches / max(1, len(_SUMMARISING_PATTERNS)))
    score = max(0.0, min(1.0, 0.4 + raw * 0.6))

    # Bonus: final-panel check — last dialogue text should contain a hook
    if texts:
        last = texts[-1].lower()
        if any(re.search(p, last, re.IGNORECASE) for p in _HOOK_PATTERNS):
            score = min(1.0, score + 0.15)

    issues: list[str] = []
    if close_matches:
        issues.append(f"Summarising patterns found ({close_matches}): weakens hook")
    if hook_matches == 0:
        issues.append("No engagement hook patterns detected in dialogue")

    status = "PASS" if score >= 0.65 else ("WARN" if score >= 0.45 else "FAIL")
    result = GateResult("MDLG-01", status, score, issues,
                        ["Add a question, ellipsis, or stakes declaration to create forward pull"]
                        if status != "PASS" else [])
    issue = _make_issue("MDLG-01", score, 0.45, 0.65,
                        f"Engagement score {score:.2f}: dialogue lacks forward momentum")
    return result, issue


def gate_somatic_precision(
    chapter_script: Mapping[str, Any],
    lettering_spec: Mapping[str, Any],
    genre: str,
) -> tuple[GateResult, dict[str, Any] | None]:
    """MDLG-02: Does dialogue reference physical experience when appropriate?

    Gate activates only for panels containing somatic-trigger emotions
    (fear, grief, determination_peak, love_confession, horror_encounter).
    Returns neutral PASS when no trigger emotion found.
    """
    lines = _lettering_lines(lettering_spec)
    if not lines:
        result = GateResult("MDLG-02", "PASS", 1.0, [], [])
        return result, None

    # Check if any somatic-trigger emotion present
    triggered = any(
        str(dl.get("emotion") or "").lower() in _SOMATIC_TRIGGER_EMOTIONS
        or (str(dl.get("emotion") or "").lower() == "determination"
            and str(dl.get("intensity") or "").lower() in ("shouting", "screaming"))
        for dl in lines
    )
    if not triggered:
        result = GateResult("MDLG-02", "PASS", 1.0, [], [])
        return result, None

    # Gate is active — check for somatic vocabulary
    g = _normalise_genre(genre)
    vocab = _SOMATIC_VOCAB.get(g, _DEFAULT_SOMATIC)
    all_text = " ".join(str(dl.get("text") or "") for dl in lines).lower()

    matches = sum(1 for v in vocab if v in all_text)
    # Each match contributes 0.20 beyond the 0.30 base; 4+ matches = 1.0
    score = min(1.0, 0.30 + matches * 0.20)

    issues: list[str] = []
    if matches == 0:
        issues.append(
            f"Somatic trigger emotion detected but no body-experience vocabulary in dialogue. "
            f"Genre '{genre}' somatic vocabulary: {vocab[:4]}"
        )

    status = "PASS" if score >= 0.70 else ("WARN" if score >= 0.50 else "FAIL")
    result = GateResult("MDLG-02", status, score, issues,
                        [f"Add body-sensation language for genre '{genre}'"] if issues else [])
    issue = _make_issue("MDLG-02", score, 0.50, 0.70,
                        f"Somatic precision {score:.2f}: emotional scene lacks physical grounding")
    return result, issue


def gate_word_economy(
    chapter_script: Mapping[str, Any],
    lettering_spec: Mapping[str, Any],
    genre: str,
) -> tuple[GateResult, dict[str, Any] | None]:
    """MDLG-03: Are word-per-bubble counts within genre ceilings?

    Hard BLOCK if any single bubble exceeds the genre block ceiling.
    WARN if bubbles exceed the typical_max threshold.
    """
    lines = _lettering_lines(lettering_spec)
    if not lines:
        result = GateResult("MDLG-03", "PASS", 1.0, [], [])
        return result, None

    g = _normalise_genre(genre)
    typical_max, block_ceiling = _GENRE_WORD_CEILINGS.get(g, _DEFAULT_CEILINGS)

    over_block: list[tuple[str, int]] = []
    over_typical: list[tuple[str, int]] = []

    for dl in lines:
        text = str(dl.get("text") or "")
        wc = _word_count(text)
        if wc > block_ceiling:
            over_block.append((text[:40], wc))
        elif wc > typical_max:
            over_typical.append((text[:40], wc))

    if over_block:
        score = 0.0
        issues = [f"Bubble exceeds BLOCK ceiling ({block_ceiling} words for {genre}): "
                  f"'{t}'... ({wc} words)" for t, wc in over_block[:3]]
        result = GateResult("MDLG-03", "FAIL", score, issues,
                            [f"Split bubble text to under {typical_max} words for genre '{genre}'"])
        issue: dict[str, Any] | None = {
            "issue_code": "MDLG-03_BLOCK",
            "gate_id": "MDLG-03",
            "severity": "BLOCKER",
            "stage_owner": "chapter_lettering",
            "description": issues[0],
        }
        return result, issue

    if over_typical:
        score = 0.55
        issues = [f"{len(over_typical)} bubble(s) over typical_max ({typical_max}): "
                  f"'{over_typical[0][0]}'... ({over_typical[0][1]} words)"]
        result = GateResult("MDLG-03", "WARN", score, issues,
                            [f"Reduce bubble length to ≤{typical_max} words for genre '{genre}'"])
        issue = _make_issue("MDLG-03", score, 0.0, 0.70,
                            f"Word economy warn: {len(over_typical)} long bubble(s)")
        return result, issue

    score = 1.0
    result = GateResult("MDLG-03", "PASS", score, [], [])
    return result, None


def gate_dialogue_uniqueness(
    chapter_script: Mapping[str, Any],
    lettering_spec: Mapping[str, Any],
    series_history: Sequence[str] | None = None,
) -> tuple[GateResult, dict[str, Any] | None]:
    """MDLG-04: Are dialogue lines sufficiently varied from series history?

    Compares current chapter lines against ``series_history`` (list of
    previously used dialogue strings from series memory).
    Returns PASS when series_history is empty or None (first chapter).
    """
    lines = _lettering_lines(lettering_spec)
    if not lines:
        result = GateResult("MDLG-04", "PASS", 1.0, [], [])
        return result, None

    current_texts = [str(dl.get("text") or "") for dl in lines if dl.get("text")]
    if not current_texts:
        result = GateResult("MDLG-04", "PASS", 1.0, [], [])
        return result, None

    history = list(series_history or [])
    if not history:
        result = GateResult("MDLG-04", "PASS", 1.0, [], [])
        return result, None

    # Check for near-duplicates
    exact_matches: list[str] = []
    near_matches: list[tuple[str, float]] = []

    for ct in current_texts:
        ct_lower = ct.lower().strip()
        for ht in history:
            ht_lower = ht.lower().strip()
            if ct_lower == ht_lower:
                exact_matches.append(ct[:50])
                break
            sim = _similarity(ct, ht)
            if sim > 0.85:
                near_matches.append((ct[:50], round(sim, 2)))
                break

    if exact_matches:
        score = 0.0
        issues = [f"Exact repeat of previously used line: '{exact_matches[0]}'"]
        result = GateResult("MDLG-04", "FAIL", score, issues,
                            ["Replace exact-repeat dialogue with a fresh variant"])
        issue: dict[str, Any] | None = {
            "issue_code": "MDLG-04_BLOCK",
            "gate_id": "MDLG-04",
            "severity": "BLOCKER",
            "stage_owner": "chapter_lettering",
            "description": issues[0],
        }
        return result, issue

    n_total = len(current_texts)
    n_near = len(near_matches)
    score = max(0.0, 1.0 - (n_near / max(1, n_total)) * 0.5)

    issues: list[str] = []
    if near_matches:
        issues.append(f"{n_near}/{n_total} lines have high similarity (>0.85) to series history")

    status = "PASS" if score >= 0.75 else ("WARN" if score >= 0.60 else "FAIL")
    result = GateResult("MDLG-04", status, score, issues,
                        ["Vary dialogue phrasing — avoid repetition from earlier chapters"]
                        if issues else [])
    issue = _make_issue("MDLG-04", score, 0.60, 0.75,
                        f"Uniqueness {score:.2f}: {n_near} near-duplicate line(s)")
    return result, issue


def gate_dialogue_cohesion(
    chapter_script: Mapping[str, Any],
    lettering_spec: Mapping[str, Any],
    chapter_contract: Mapping[str, Any] | None = None,
) -> tuple[GateResult, dict[str, Any] | None]:
    """MDLG-05: Does dialogue reinforce the chapter's emotional_job (EI engine)?

    Maps ``chapter_contract.emotional_job`` → expected dialogue patterns.
    Returns neutral PASS when no emotional_job is specified.
    """
    lines = _lettering_lines(lettering_spec)
    if not lines:
        result = GateResult("MDLG-05", "PASS", 1.0, [], [])
        return result, None

    ej = str((chapter_contract or {}).get("emotional_job") or "").lower().strip()
    if not ej:
        # Check chapter_script directly as fallback
        ej = str(chapter_script.get("emotional_job") or "").lower().strip()
    if not ej:
        result = GateResult("MDLG-05", "PASS", 1.0, [], [])
        return result, None

    engine = ej.replace("-", "_").replace(" ", "_")
    reinforcing = _ENGINE_REINFORCING_PATTERNS.get(engine, [])
    forbidden = _ENGINE_FORBIDDEN_PATTERNS.get(engine, [])

    all_text = " ".join(str(dl.get("text") or "") for dl in lines).lower()

    reinforcing_hits = sum(1 for p in reinforcing if p in all_text)
    forbidden_hits = sum(1 for p in forbidden if p in all_text)

    n_reinforce = len(reinforcing)
    n_forbid = len(forbidden)

    # Each reinforcing hit contributes 0.15 beyond base 0.35; 5+ = 1.0
    # Each forbidden hit subtracts 0.15
    score = max(0.0, min(1.0, 0.35 + reinforcing_hits * 0.15 - forbidden_hits * 0.15))

    issues: list[str] = []
    if forbidden_hits > 0:
        issues.append(
            f"Dialogue contradicts emotional_job '{engine}': "
            f"{forbidden_hits} forbidden pattern(s) found"
        )
    if reinforcing_hits == 0:
        issues.append(
            f"Dialogue does not reinforce emotional_job '{engine}': "
            f"expected patterns like {reinforcing[:3]}"
        )

    status = "PASS" if score >= 0.70 else ("WARN" if score >= 0.50 else "FAIL")
    result = GateResult("MDLG-05", status, score, issues,
                        [f"Align dialogue with '{engine}' EI engine patterns"] if issues else [])
    issue = _make_issue("MDLG-05", score, 0.40, 0.70,
                        f"Cohesion {score:.2f} for engine '{engine}': dialogue misaligned")
    return result, issue


# ---------------------------------------------------------------------------
# Composite scoring
# ---------------------------------------------------------------------------

_BASE_WEIGHTS = {
    "MDLG-01": 0.25,
    "MDLG-02": 0.15,  # redistributed when inactive
    "MDLG-03": 0.30,
    "MDLG-04": 0.15,
    "MDLG-05": 0.15,
}

_GENRE_WEIGHT_OVERRIDES: dict[str, dict[str, float]] = {
    "shonen": {"MDLG-01": 0.35, "MDLG-02": 0.10},
    "shōnen": {"MDLG-01": 0.35, "MDLG-02": 0.10},
    "seinen": {"MDLG-02": 0.25, "MDLG-01": 0.15},
    "horror": {"MDLG-03": 0.40, "MDLG-01": 0.20},
    "shojo": {"MDLG-05": 0.25, "MDLG-01": 0.15},
    "shōjo": {"MDLG-05": 0.25, "MDLG-01": 0.15},
}


def run_manga_dialogue_gates(
    chapter_script: Mapping[str, Any],
    lettering_spec: Mapping[str, Any],
    genre: str = "shonen",
    chapter_contract: Mapping[str, Any] | None = None,
    series_history: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Run all MDLG gates and return a composite report.

    Returns a dict compatible with the ``ite_qc_report`` gates list format:
    ``{"gates": [...], "mdlg_score": float, "passed": bool, "issues": [...]}``

    Parameters
    ----------
    chapter_script
        Chapter script writer handoff.
    lettering_spec
        lettering_spec v2 artifact.
    genre
        Genre string (normalised internally).
    chapter_contract
        Dict with ``emotional_job`` key (optional).
    series_history
        Previously used dialogue strings from series memory (optional).
    """
    r01, i01 = gate_dialogue_engagement(chapter_script, lettering_spec, genre)
    r02, i02 = gate_somatic_precision(chapter_script, lettering_spec, genre)
    r03, i03 = gate_word_economy(chapter_script, lettering_spec, genre)
    r04, i04 = gate_dialogue_uniqueness(chapter_script, lettering_spec, series_history)
    r05, i05 = gate_dialogue_cohesion(chapter_script, lettering_spec, chapter_contract)

    # Determine if MDLG-02 was active
    mdlg02_active = r02.score < 1.0 or bool(r02.issues)  # active when it scored below 1.0 or had issues

    # Build weights (genre overrides + redistribute inactive MDLG-02)
    g = _normalise_genre(genre)
    weights = dict(_BASE_WEIGHTS)
    overrides = _GENRE_WEIGHT_OVERRIDES.get(g, {})
    for k, v in overrides.items():
        weights[k] = v
    # Normalise
    total_w = sum(weights.values())
    weights = {k: v / total_w for k, v in weights.items()}

    if not mdlg02_active:
        # Redistribute MDLG-02 weight to MDLG-01
        w2 = weights.pop("MDLG-02")
        weights["MDLG-01"] = weights.get("MDLG-01", 0) + w2
        total_w = sum(weights.values())
        weights = {k: v / total_w for k, v in weights.items()}

    # Score map
    scores = {
        "MDLG-01": r01.score,
        "MDLG-02": r02.score if mdlg02_active else None,
        "MDLG-03": r03.score,
        "MDLG-04": r04.score,
        "MDLG-05": r05.score,
    }

    weighted_sum = sum(
        (scores[k] or 0.0) * weights.get(k, 0)
        for k in weights
    )

    gate_entries = [
        {"id": "MDLG-01", "level": "BLOCKER", "passed": r01.status != "FAIL",
         "score": round(r01.score, 3), "detail": r01.issues[0] if r01.issues else "ok"},
        {"id": "MDLG-02", "level": "BLOCKER", "passed": r02.status != "FAIL",
         "score": round(r02.score, 3), "detail": r02.issues[0] if r02.issues else "ok",
         "active": mdlg02_active},
        {"id": "MDLG-03", "level": "BLOCKER", "passed": r03.status != "FAIL",
         "score": round(r03.score, 3), "detail": r03.issues[0] if r03.issues else "ok"},
        {"id": "MDLG-04", "level": "BLOCKER", "passed": r04.status != "FAIL",
         "score": round(r04.score, 3), "detail": r04.issues[0] if r04.issues else "ok"},
        {"id": "MDLG-05", "level": "BLOCKER", "passed": r05.status != "FAIL",
         "score": round(r05.score, 3), "detail": r05.issues[0] if r05.issues else "ok"},
    ]

    issues = [i for i in [i01, i02, i03, i04, i05] if i is not None]
    blockers = [x for x in issues if x.get("severity") == "BLOCKER"]

    gate_entries.append({
        "id": "MDLG-COMPOSITE",
        "level": "INFO",
        "passed": len(blockers) == 0,
        "score": round(weighted_sum, 3),
        "detail": f"mdlg_score={round(weighted_sum, 3)}",
    })

    return {
        "mdlg_score": round(weighted_sum, 3),
        "passed": len(blockers) == 0,
        "gates": gate_entries,
        "issues": issues,
        "weights": {k: round(v, 3) for k, v in weights.items()},
        "genre": genre,
    }
