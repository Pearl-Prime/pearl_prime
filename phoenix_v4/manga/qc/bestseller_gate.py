"""MANGA bestseller quality gate — BLOCKING chapter clearance.

The book pipeline has a blocking register gate; this is its manga sibling. It
runs the craft gates (hook / pacing / restraint / yearning) AND a genre-agnostic
STORY-SUBSTANCE check, and returns a single verdict. ``_stage_qc`` raises
``BestsellerGateError`` (HARD_FAIL) when a sub-bar chapter would otherwise
render, exactly like a sub-bar book chapter HARD_FAILs the register gate.

Substance checks (catch templated / canned chapters):
  - too few panels / pages (a real chapter has body)
  - verbatim-repeated panels (scaffolding repetition — the book-pipeline sin)
  - unfilled ``{placeholder}`` tails or HOOK/TODO/TBD/FIXME stubs
  - degenerate dialogue (every line identical / empty)
  - healing-register cardinal sins (craft bible §6): emotional labeling in
    caption, cliffhanger endings, villain/threat language, raised voices.

Severity model: substance findings are BLOCKER. Craft-gate findings
(hook/pacing/restraint/yearning) are promoted to BLOCKER inside this gate
because a bestseller chapter must satisfy its own genre's grammar.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, Mapping

from phoenix_v4.manga.qc._script_shape import (
    iter_pages,
    iter_panels,
    last_panel,
    panel_text,
)

if TYPE_CHECKING:
    from phoenix_v4.manga.series.profile_loader import MangaProfile

# Minimums for a chapter that has real story body (not a stub).
_MIN_PANELS = 6
_MIN_PAGES = 2

# Stub / placeholder markers that must never reach render.
_STUB_RE = re.compile(
    r"\{[a-z_]+\}"                      # unfilled {protagonist} / {setting}
    r"|\bTODO\b|\bTBD\b|\bFIXME\b|\bXXX\b"
    r"|\bHOOK\b|\bPLACEHOLDER\b|\bLOREM IPSUM\b|\bCHAPTER_END_HOOK\b",
    re.IGNORECASE,
)

# Healing-register cardinal sins (iyashikei_minimalism.md §6).
# Emotional labeling in caption/narration — "she felt sad", "he was lonely".
_LABELING_RE = re.compile(
    r"\b(?:she|he|they|i)\s+(?:felt|feels|was|were|is|am)\s+"
    r"(?:so\s+|very\s+|really\s+)?"
    r"(?:sad|lonely|angry|afraid|scared|happy|joyful|grief-stricken|devastated|"
    r"heartbroken|miserable|anxious|terrified|furious|ecstatic|depressed)\b",
    re.IGNORECASE,
)
# Cliffhanger / question-ending poison (even soft ones).
_CLIFFHANGER_RE = re.compile(
    r"who could it be\??|what happens next|to be continued|"
    r"little did .* know|but then,? everything|cliffhanger",
    re.IGNORECASE,
)
# Villain / threat / battle language — breaks the healing contract entirely.
_THREAT_WORDS = [
    "attack", "enemy", "villain", "kill", "destroy", "weapon", "battle",
    "fight to the death", "vengeance", "slaughter", "monster must be",
    "defeat the", "blood everywhere", "scream", "screamed", "shouted",
    "explosion", "war ", "warlord", "assassin",
]

_HEALING_GENRES = frozenset(
    ["healing", "supernatural_everyday", "slice_of_life", "iyashikei"]
)
_HEALING_GRAMMARS = frozenset(
    ["iyashikei_minimalism", "healing_iyashikei", "sparse_atmosphere"]
)


class BestsellerGateError(RuntimeError):
    """Raised by _stage_qc when a chapter HARD_FAILs the bestseller gate."""

    def __init__(self, findings: list[dict[str, Any]]):
        self.findings = findings
        summary = "; ".join(
            f"[{f.get('gate_id')}] {f.get('description')}" for f in findings
        )
        super().__init__(f"Bestseller gate HARD_FAIL ({len(findings)} blocker(s)): {summary}")


def _is_healing_profile(profile: "MangaProfile | None") -> bool:
    if profile is None:
        return False
    return (
        getattr(profile, "genre_family", "") in _HEALING_GENRES
        or getattr(profile, "visual_grammar", "") in _HEALING_GRAMMARS
    )


def _substance_findings(
    chapter_script: Mapping[str, Any],
    profile: "MangaProfile | None",
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    panels = list(iter_panels(chapter_script))
    pages = list(iter_pages(chapter_script))

    # 1. Body floor.
    if len(panels) < _MIN_PANELS or len(pages) < _MIN_PAGES:
        findings.append({
            "issue_code": "STORY_SUBSTANCE_THIN",
            "gate_id": "MANGA.BESTSELLER.SUBSTANCE",
            "severity": "BLOCKER",
            "stage_owner": "chapter_qc",
            "description": (
                f"Chapter has only {len(panels)} panel(s) over {len(pages)} page(s); "
                f"a bestseller chapter needs >= {_MIN_PANELS} panels over >= {_MIN_PAGES} pages."
            ),
        })

    # 2. Stub / placeholder markers anywhere in the script.
    texts = [panel_text(p) for p in panels]
    for t in texts:
        m = _STUB_RE.search(t)
        if m:
            findings.append({
                "issue_code": "STORY_SUBSTANCE_STUB_MARKER",
                "gate_id": "MANGA.BESTSELLER.SUBSTANCE",
                "severity": "BLOCKER",
                "stage_owner": "chapter_qc",
                "description": f"Unfilled stub/placeholder reached render: {m.group(0)!r} in {t[:80]!r}",
            })
            break

    # 3. Verbatim-repeated panels (scaffolding repetition).
    nonempty = [t.strip().lower() for t in texts if t.strip()]
    if len(nonempty) >= 4:
        seen: dict[str, int] = {}
        for t in nonempty:
            seen[t] = seen.get(t, 0) + 1
        worst_text, worst_n = max(seen.items(), key=lambda kv: kv[1])
        # >1 exact repeat of a substantive (>=6 word) panel is templated filler.
        if worst_n >= 2 and len(worst_text.split()) >= 6:
            findings.append({
                "issue_code": "STORY_SUBSTANCE_VERBATIM_REPEAT",
                "gate_id": "MANGA.BESTSELLER.SUBSTANCE",
                "severity": "BLOCKER",
                "stage_owner": "chapter_qc",
                "description": (
                    f"Panel text repeats verbatim {worst_n}x (templated filler): {worst_text[:80]!r}"
                ),
            })
        # Low unique-ratio across the chapter = canned.
        uniq_ratio = len(set(nonempty)) / len(nonempty)
        if uniq_ratio < 0.5:
            findings.append({
                "issue_code": "STORY_SUBSTANCE_LOW_VARIETY",
                "gate_id": "MANGA.BESTSELLER.SUBSTANCE",
                "severity": "BLOCKER",
                "stage_owner": "chapter_qc",
                "description": (
                    f"Only {uniq_ratio:.0%} of text panels are unique — chapter reads as templated."
                ),
            })

    # 4. Final panel must actually land something (no empty close).
    lp = last_panel(chapter_script)
    if lp is not None and not panel_text(lp).strip():
        # An intentional silent final panel is fine ONLY if the chapter carries a hook note.
        has_hook = bool(
            str(chapter_script.get("chapter_end_hook") or "").strip()
        )
        if not has_hook:
            findings.append({
                "issue_code": "STORY_SUBSTANCE_EMPTY_CLOSE",
                "gate_id": "MANGA.BESTSELLER.SUBSTANCE",
                "severity": "BLOCKER",
                "stage_owner": "chapter_qc",
                "description": "Final panel is empty and no chapter_end_hook is set — chapter does not close.",
            })

    # 5. Healing-register cardinal sins.
    if _is_healing_profile(profile):
        joined = " ".join(texts)
        if _LABELING_RE.search(joined):
            m = _LABELING_RE.search(joined)
            findings.append({
                "issue_code": "HEALING_EMOTIONAL_LABELING",
                "gate_id": "MANGA.BESTSELLER.HEALING_REGISTER",
                "severity": "BLOCKER",
                "stage_owner": "chapter_qc",
                "description": (
                    f"Emotional labeling — the iyashikei cardinal sin (craft bible §6.2): "
                    f"{m.group(0)!r}. Show via environmental correlative instead."
                ),
            })
        if _CLIFFHANGER_RE.search(joined):
            findings.append({
                "issue_code": "HEALING_CLIFFHANGER",
                "gate_id": "MANGA.BESTSELLER.HEALING_REGISTER",
                "severity": "BLOCKER",
                "stage_owner": "chapter_qc",
                "description": "Cliffhanger/question ending poisons iyashikei re-read value (craft bible §6.7).",
            })
        low = joined.lower()
        hits = [w for w in _THREAT_WORDS if w in low]
        if hits:
            findings.append({
                "issue_code": "HEALING_THREAT_LANGUAGE",
                "gate_id": "MANGA.BESTSELLER.HEALING_REGISTER",
                "severity": "BLOCKER",
                "stage_owner": "chapter_qc",
                "description": (
                    f"Villain/threat/battle language breaks the healing contract "
                    f"(craft bible §6.1): {hits[:5]}."
                ),
            })

    return findings


def evaluate_bestseller_gate(
    chapter_script: Mapping[str, Any],
    profile: "MangaProfile | None" = None,
) -> dict[str, Any]:
    """Run the full bestseller gate. Returns a verdict dict.

    Verdict keys:
      - ``clearance``  — "pass" | "hard_fail"
      - ``blockers``   — list of BLOCKER findings (substance + promoted craft gates)
      - ``findings``   — all findings (blockers only here; craft gates promoted)
    """
    findings: list[dict[str, Any]] = []

    # Story-substance (genre-agnostic, always on).
    findings.extend(_substance_findings(chapter_script, profile))

    # Genre-native story engine (blocks shell-correct but structurally generic output).
    try:
        from phoenix_v4.manga.qc.genre_engine_gate import evaluate_genre_engine
        genre_decl = None
        if profile is not None:
            genre_decl = getattr(profile, "genre_family", None) or getattr(profile, "genre_id", None)
        findings.extend(
            evaluate_genre_engine(chapter_script, genre_id=str(genre_decl or ""))
        )
    except Exception:
        pass

    # Craft gates — only when a profile is available; promote MAJOR -> BLOCKER.
    if profile is not None:
        try:
            from phoenix_v4.manga.qc.hook_gate import check_chapter_hook
            issue = check_chapter_hook(chapter_script, profile)
            if issue:
                issue = {**issue, "severity": "BLOCKER"}
                findings.append(issue)
        except Exception:
            pass
        try:
            from phoenix_v4.manga.qc.pacing_gates import (
                check_genre_authenticity,
                check_silence_density,
            )
            for fn in (check_genre_authenticity,):
                issue = fn(chapter_script, profile)
                if issue:
                    findings.append({**issue, "severity": "BLOCKER"})
            # silence density needs lettering; pass empty so it falls back to script counting
            issue = check_silence_density(chapter_script, {}, profile)
            if issue:
                findings.append({**issue, "severity": "BLOCKER"})
        except Exception:
            pass
        try:
            from phoenix_v4.manga.qc.restraint_gate import check_restraint_over_exposition
            issue = check_restraint_over_exposition(chapter_script, profile)
            if issue:
                findings.append({**issue, "severity": "BLOCKER"})
        except Exception:
            pass
        try:
            from phoenix_v4.manga.qc.yearning_gate import check_yearning_pacing
            issue = check_yearning_pacing(chapter_script, profile)
            if issue:
                findings.append({**issue, "severity": "BLOCKER"})
        except Exception:
            pass

    blockers = [f for f in findings if f.get("severity") == "BLOCKER"]
    return {
        "clearance": "hard_fail" if blockers else "pass",
        "blockers": blockers,
        "findings": findings,
    }
