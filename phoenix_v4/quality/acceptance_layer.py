#!/usr/bin/env python3
"""Book acceptance-layer stamp — mechanizes
``docs/PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md`` so a book can never be
reported as ``bestseller_register`` / ``system_working`` / "shippable" off a
``register_gate``/gate-PASS alone.

Lane 04 (``docs/agent_prompt_packs/20260721_bestseller_atom_flow/04_book_acceptance_layer_stamp.md``)
of the 2026-07-21 bestseller-atom-flow prompt pack. Depends on Lane 01
(``scripts/ci/check_book_story_authored.py``) for the ``research_fit_bound``
signal and the ``book_acceptance_stamp.json`` file convention this module
extends additively (never removes fields Lane 01 wrote).

Source request this whole pack traces back to (see pack INDEX.md): operator
audit of seed 43001 (``millennial_women_professionals x courage``) — a
book that gate-PASSed with ``research_fit: {}``, no story_schedule, no
character through-line, no book_idea/motif payoff, ONTGP 0.52/Give
0.38/Pull 0.32, ``mechanism_called=0``; operator: "you always forget what I
told you last audit." CLAUDE.md's "Meta-rule: memory is recall, not
enforcement" names the fix directly: a mechanism, not another memory note.
This module is that mechanism.

STATUS LANGUAGE (verbatim from the scorecard's "Status language" table,
``docs/PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md`` lines 23-33) — five
rungs, lowest to highest. This module only ever *advances* a book layer by
layer; it never skips a rung and never invents a layer name:

  path_broken          -- pipeline halted before producing book.txt
  path_works            -- book.txt exists, but Layer 1 hard gates did not all
                           PASS (scorecard line 56)
  structurally_clear    -- Layer 1 (scorecard lines 41-58)
  authored_candidate    -- Layer 1 + real research_fit binding + a named
                           mechanism call (scorecard lines 60-75, Lane 04 spec)
  system_working        -- Layer 1+2 + a LOGGED Pearl_Editor ONTGP sample read
                           (scorecard lines 77-99)
  bestseller_register   -- Layer 4 blind-10 system benchmark verdict, surfaced
                           only when one already exists elsewhere (scorecard
                           lines 101-117); THIS MODULE NEVER COMPUTES THIS
                           ITSELF.

NUMERIC FLOORS -- copied verbatim from the scorecard, do not invent new ones:

  - ``docs/PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md:50`` (Layer 1 hard
    gate table): "``bestseller_craft`` | ... | ``quality_summary.
    bestseller_craft.overall_score >= 0.55`` | PASS required under
    ``--quality-profile production``" -> ``BESTSELLER_CRAFT_SCORE_FLOOR``.
  - ``...:58`` (Layer 1 "Research-fit binding cap" paragraph, added by Lane 01
    2026-07-21): a book with unbound ``research_fit`` "is capped at Layer 1
    (`structurally clear` / `acceptance_layer: structurally_clear_only`)
    regardless of other Layer 1 gates passing ... must not be reported as
    `authored candidate`, `system working`, or `bestseller register` until a
    real story_atoms bank binds." -> the research-fit ceiling below.
  - ``...:90`` (Layer 3 ONTGP rubric): "Chapter passes ONTGP if: 0 FAILs
    across all 5 dimensions AND <= 2 WEAKs." / "...:91 Book passes Layer 3
    if: all sampled chapters pass ONTGP." -> ``ONTGP_MAX_FAILS_PER_CHAPTER``,
    ``ONTGP_MAX_WEAKS_PER_CHAPTER``.
  - ``...:113`` (Layer 4 system-level benchmark): "System-level PASS: >= 7 of
    10 books say `felt assembled = yes` AND >= 6 of 10 say
    `shelf-next-to-trade-pub = yes`." -> ``LAYER4_MIN_FELT_ASSEMBLED_YES``,
    ``LAYER4_MIN_SHELF_YES``, ``LAYER4_TOTAL_BOOKS``. Read-only in this
    module -- never computed, only surfaced if already recorded.

The scorecard does NOT define any single numeric "ONTGP composite" score
field anywhere in the document (ONTGP is a per-dimension PASS/WEAK/FAIL
rubric, not a 0-1 score). The 2026-07-21 Lane 04 prompt pack text mentions
capping Layer 1 "if ONTGP composite < some documented floor from the
scorecard" -- the only numeric craft-quality floor the scorecard actually
documents for Layer 1 is the ``bestseller_craft`` gate's ``overall_score >=
0.55``. This module applies that floor and does NOT invent a separate
"ONTGP composite" number that the scorecard never defines. The real ONTGP
PASS/WEAK/FAIL rubric IS applied, verbatim, to gate Layer 3 (see
``_ontgp_chapter_passes`` below), which is where the scorecard actually uses
it.

NEVER-AUTO-ASSIGN GUARANTEE:
  - ``system_working`` (Layer 3) is returned ONLY when the caller passes an
    explicit ``ontgp_sample_review`` record (a human/Pearl_Editor artifact).
    ``ontgp_sample_review=None`` (the default) means "no review logged yet"
    and the result can never exceed ``authored_candidate``.
  - ``bestseller_register`` (Layer 4) is returned ONLY when the caller passes
    an explicit ``blind10_result`` record that itself already carries a
    PASS verdict per the scorecard's Layer 4 thresholds. This module
    contains no code path that can produce ``bestseller_register`` from
    gate/craft/research_fit signals alone -- see
    ``test_no_gate_only_combination_reaches_layer3_or_4`` in
    ``tests/test_acceptance_layer.py`` for the exhaustive proof.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional

# --- Status language rungs (scorecard lines 23-33) --------------------------
PATH_BROKEN = "path_broken"
PATH_WORKS = "path_works"
STRUCTURALLY_CLEAR = "structurally_clear"
AUTHORED_CANDIDATE = "authored_candidate"
SYSTEM_WORKING = "system_working"
BESTSELLER_REGISTER = "bestseller_register"

_RUNG_ORDER = (
    PATH_BROKEN,
    PATH_WORKS,
    STRUCTURALLY_CLEAR,
    AUTHORED_CANDIDATE,
    SYSTEM_WORKING,
    BESTSELLER_REGISTER,
)

# --- Numeric floors, copied verbatim from the scorecard (see module docstring
#     for the exact line citation of each) -----------------------------------
BESTSELLER_CRAFT_SCORE_FLOOR = 0.55  # scorecard line 50
ONTGP_MAX_FAILS_PER_CHAPTER = 0      # scorecard line 90
ONTGP_MAX_WEAKS_PER_CHAPTER = 2      # scorecard line 90
LAYER4_TOTAL_BOOKS = 10              # scorecard line 113
LAYER4_MIN_FELT_ASSEMBLED_YES = 7    # scorecard line 113
LAYER4_MIN_SHELF_YES = 6             # scorecard line 113

_ONTGP_DIMENSIONS = ("orient", "name", "turn", "give", "pull")

# The scorecard names this exact string for the research-fit ceiling
# (line 58): "acceptance_layer: structurally_clear_only". Lane 01's
# check_book_story_authored.py already writes this literal string into
# book_acceptance_stamp.json for unbound books; kept identical here so the
# two lanes never disagree on the cap's name. Distinct from the plain
# `structurally_clear` rung name used elsewhere in this taxonomy — this
# value specifically flags "capped here, not merely resting here".
RESEARCH_FIT_CEILING_LABEL = "structurally_clear_only"


@dataclass(frozen=True)
class AcceptanceLayerResult:
    """Deterministic acceptance-layer verdict for one rendered book.

    ``layer3_pass`` / ``layer4_pass`` are ``Optional[bool]``: ``None`` means
    "no review/benchmark logged" (pending), NOT "failed". This is the
    never-auto-assign contract from the module docstring.
    """

    acceptance_layer: str
    reasons: tuple[str, ...]
    layer1_pass: bool
    layer2_pass: bool
    layer3_pass: Optional[bool]
    layer4_pass: Optional[bool]
    research_fit_bound: Optional[bool]
    inputs: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "acceptance_layer": self.acceptance_layer,
            "reasons": list(self.reasons),
            "layer1_pass": self.layer1_pass,
            "layer2_pass": self.layer2_pass,
            "layer3_pass": self.layer3_pass,
            "layer4_pass": self.layer4_pass,
            "research_fit_bound": self.research_fit_bound,
        }


def _ontgp_chapter_passes(dims: Mapping[str, str]) -> bool:
    """Scorecard line 90, verbatim: "Chapter passes ONTGP if: 0 FAILs across
    all 5 dimensions AND <= 2 WEAKs."."""
    values = [str(dims.get(d, "")).strip().upper() for d in _ONTGP_DIMENSIONS]
    fails = sum(1 for v in values if v == "FAIL")
    weaks = sum(1 for v in values if v == "WEAK")
    return fails <= ONTGP_MAX_FAILS_PER_CHAPTER and weaks <= ONTGP_MAX_WEAKS_PER_CHAPTER


def _ontgp_sample_passes(review: Mapping[str, Any]) -> tuple[bool, str]:
    """Scorecard line 91: "Book passes Layer 3 if: all sampled chapters pass
    ONTGP.". ``review`` shape: {"chapters": {"<n>": {"orient": "PASS", ...}}}.
    An empty/malformed review can never pass (fails closed, never auto-true).
    """
    chapters = review.get("chapters")
    if not isinstance(chapters, Mapping) or not chapters:
        return False, "ontgp_sample_review has no sampled chapters recorded"
    failing = [
        str(name)
        for name, dims in chapters.items()
        if not isinstance(dims, Mapping) or not _ontgp_chapter_passes(dims)
    ]
    if failing:
        return False, f"ONTGP sample FAILed on chapter(s): {', '.join(sorted(failing))}"
    return True, ""


def _layer4_passes(result: Mapping[str, Any]) -> tuple[bool, str]:
    """Scorecard line 113, verbatim: "System-level PASS: >= 7 of 10 books say
    `felt assembled = yes` AND >= 6 of 10 say `shelf-next-to-trade-pub =
    yes`.". This function only ever READS an already-computed blind-10
    verdict; it is never called to *produce* one from gate data.
    """
    verdict = str(result.get("verdict") or "").strip().upper()
    if verdict == "PASS":
        return True, "blind10_result verdict=PASS (operator-recorded)"
    if verdict:
        return False, f"blind10_result verdict={verdict!r} (not PASS)"
    felt = result.get("felt_assembled_yes_count")
    shelf = result.get("shelf_next_to_trade_pub_yes_count")
    total = result.get("total_books", LAYER4_TOTAL_BOOKS)
    if isinstance(felt, int) and isinstance(shelf, int) and total == LAYER4_TOTAL_BOOKS:
        passed = felt >= LAYER4_MIN_FELT_ASSEMBLED_YES and shelf >= LAYER4_MIN_SHELF_YES
        return passed, (
            f"felt_assembled_yes={felt}/{total} (floor {LAYER4_MIN_FELT_ASSEMBLED_YES}), "
            f"shelf_yes={shelf}/{total} (floor {LAYER4_MIN_SHELF_YES})"
        )
    return False, "blind10_result present but missing verdict/counts — treated as not-yet-PASS"


def compute_acceptance_layer(
    *,
    book_txt_exists: bool = True,
    layer1_gate_statuses: Optional[Mapping[str, str]] = None,
    bestseller_craft_score: Optional[float] = None,
    research_fit_bound: Optional[bool] = None,
    research_fit_unbound_reason: Optional[str] = None,
    book_idea_or_motif_present: bool = False,
    mechanism_called: Optional[int] = None,
    ontgp_sample_review: Optional[Mapping[str, Any]] = None,
    blind10_result: Optional[Mapping[str, Any]] = None,
) -> AcceptanceLayerResult:
    """Compute the deterministic acceptance layer for one book.

    Every keyword is optional and defaults to the *safest* (lowest-layer)
    value: a caller that supplies nothing gets ``path_works`` at best, never
    a higher layer by omission. This mirrors the module's never-auto-assign
    doctrine down to the parameter defaults themselves.

    Parameters
    ----------
    book_txt_exists:
        Whether the render actually produced ``book.txt`` (scorecard line
        56: ``path works`` vs ``path broken``).
    layer1_gate_statuses:
        Mapping of Layer-1 hard-gate name -> status string (``"PASS"`` /
        ``"FAIL"`` / ``"WARN"`` / ``"SKIPPED"``). Only gates the caller
        actually ran should be included; an empty/None mapping is treated as
        "no Layer 1 gate evidence" (fails closed -> not structurally_clear).
        Scorecard Layer 1 table (lines 45-53): chapter_flow, book_quality_gate,
        scene_anti_genericity, bestseller_craft, ei_v2, transformation_arc,
        book_pass. Pass whichever subset a given caller has computed; this
        function does not silently assume a missing gate PASSed.
    bestseller_craft_score:
        The ``quality_summary.bestseller_craft.overall_score`` value.
        Enforces the scorecard's explicit ``>= 0.55`` numeric floor (line 50)
        even if the caller's own status string for that gate says PASS under
        a looser local threshold.
    research_fit_bound:
        Output of Lane 01's ``classify_research_fit()``
        (``scripts/ci/check_book_story_authored.py``). ``None``/``False``
        both cap the result at ``structurally_clear`` per scorecard line 58.
    book_idea_or_motif_present:
        Whether a REAL (non-generic-fallback) book_idea/motif payoff was
        recorded for this book — distinct from ``research_fit_bound`` in the
        Lane 04 spec, even though today's only wired signal for this
        (``research_fit.motif_ledger`` non-empty) is derived from the same
        underlying research_fit payload.
    mechanism_called:
        Count of named-mechanism invocations actually recorded for this
        book. No such field is wired into ``enrichment_audit.json`` /
        ``quality_summary.json`` anywhere in this repo today (verified by
        grep, 2026-07-21) — ``None`` (the default) means "not tracked yet"
        and is treated as "not > 0", i.e. it caps the result at
        ``structurally_clear`` rather than inventing a fake positive count.
    ontgp_sample_review:
        A logged Pearl_Editor (or human) ONTGP sample-read record, or
        ``None`` if no such review has been logged. Never auto-populated.
    blind10_result:
        A logged Layer-4 blind-10 operator benchmark record, or ``None``.
        Never auto-populated; never computed from any other input here.
    """
    reasons: list[str] = []
    inputs = {
        "book_txt_exists": book_txt_exists,
        "layer1_gate_statuses": dict(layer1_gate_statuses or {}),
        "bestseller_craft_score": bestseller_craft_score,
        "research_fit_bound": research_fit_bound,
        "book_idea_or_motif_present": book_idea_or_motif_present,
        "mechanism_called": mechanism_called,
        "ontgp_sample_review_present": ontgp_sample_review is not None,
        "blind10_result_present": blind10_result is not None,
    }

    if not book_txt_exists:
        return AcceptanceLayerResult(
            acceptance_layer=PATH_BROKEN,
            reasons=("pipeline did not produce book.txt (scorecard: 'path broken')",),
            layer1_pass=False,
            layer2_pass=False,
            layer3_pass=None,
            layer4_pass=None,
            research_fit_bound=research_fit_bound,
            inputs=inputs,
        )

    gates = dict(layer1_gate_statuses or {})
    if not gates:
        reasons.append("no Layer 1 gate evidence supplied — cannot certify structurally_clear")
        layer1_pass = False
    else:
        failing_gates = sorted(name for name, status in gates.items() if str(status).upper() != "PASS")
        layer1_pass = not failing_gates
        if failing_gates:
            reasons.append(f"Layer 1 gate(s) not PASS: {', '.join(failing_gates)}")

    if bestseller_craft_score is not None and bestseller_craft_score < BESTSELLER_CRAFT_SCORE_FLOOR:
        layer1_pass = False
        reasons.append(
            f"bestseller_craft overall_score {bestseller_craft_score:.4f} < floor "
            f"{BESTSELLER_CRAFT_SCORE_FLOOR} (scorecard line 50, Layer 1 hard gate)"
        )

    if not layer1_pass:
        return AcceptanceLayerResult(
            acceptance_layer=PATH_WORKS,
            reasons=tuple(reasons) or ("Layer 1 not certified clean",),
            layer1_pass=False,
            layer2_pass=False,
            layer3_pass=None,
            layer4_pass=None,
            research_fit_bound=research_fit_bound,
            inputs=inputs,
        )

    # Layer 1 hard gates PASS. Apply the research-fit ceiling (scorecard
    # line 58) before considering Layer 2+.
    research_fit_ok = bool(research_fit_bound)
    if not research_fit_ok:
        reasons.append(
            "research_fit unbound"
            + (f" ({research_fit_unbound_reason})" if research_fit_unbound_reason else "")
            + " — capped at Layer 1 per scorecard line 58 "
            f"(acceptance_layer={RESEARCH_FIT_CEILING_LABEL!r}), regardless of other "
            "Layer 1 gates passing"
        )
        return AcceptanceLayerResult(
            acceptance_layer=STRUCTURALLY_CLEAR,
            reasons=tuple(reasons),
            layer1_pass=True,
            layer2_pass=False,
            layer3_pass=None,
            layer4_pass=None,
            research_fit_bound=research_fit_bound,
            inputs=inputs,
        )

    if not book_idea_or_motif_present:
        reasons.append("no book_idea/motif payoff recorded — capped at structurally_clear")
        return AcceptanceLayerResult(
            acceptance_layer=STRUCTURALLY_CLEAR,
            reasons=tuple(reasons),
            layer1_pass=True,
            layer2_pass=False,
            layer3_pass=None,
            layer4_pass=None,
            research_fit_bound=research_fit_bound,
            inputs=inputs,
        )

    mechanism_ok = bool(mechanism_called and mechanism_called > 0)
    if not mechanism_ok:
        reasons.append(
            f"mechanism_called={mechanism_called!r} (not > 0, or not tracked) — "
            "capped at structurally_clear"
        )
        return AcceptanceLayerResult(
            acceptance_layer=STRUCTURALLY_CLEAR,
            reasons=tuple(reasons),
            layer1_pass=True,
            layer2_pass=False,
            layer3_pass=None,
            layer4_pass=None,
            research_fit_bound=research_fit_bound,
            inputs=inputs,
        )

    # Layer 2 (authored_candidate) reached: Layer 1 + real research_fit
    # binding + book_idea/motif + a named mechanism actually called.
    reasons.append(
        "authored_candidate: Layer 1 clean, research_fit bound, book_idea/motif "
        "present, mechanism_called > 0"
    )
    layer2_pass = True

    # Layer 3 (system_working) — NEVER auto-assigned. Only advances if a
    # logged ONTGP sample review already exists.
    if ontgp_sample_review is None:
        reasons.append(
            "pending Pearl_Editor ONTGP sample read (Layer 3) — not auto-assumed; "
            "acceptance_layer stays authored_candidate until logged"
        )
        return AcceptanceLayerResult(
            acceptance_layer=AUTHORED_CANDIDATE,
            reasons=tuple(reasons),
            layer1_pass=True,
            layer2_pass=layer2_pass,
            layer3_pass=None,
            layer4_pass=None,
            research_fit_bound=research_fit_bound,
            inputs=inputs,
        )

    layer3_pass, layer3_reason = _ontgp_sample_passes(ontgp_sample_review)
    if layer3_reason:
        reasons.append(layer3_reason)
    if not layer3_pass:
        return AcceptanceLayerResult(
            acceptance_layer=AUTHORED_CANDIDATE,
            reasons=tuple(reasons),
            layer1_pass=True,
            layer2_pass=layer2_pass,
            layer3_pass=False,
            layer4_pass=None,
            research_fit_bound=research_fit_bound,
            inputs=inputs,
        )

    reasons.append("system_working: logged ONTGP sample read passed all sampled chapters")

    # Layer 4 (bestseller_register) — NEVER computed here. Only surfaced if
    # an explicit, already-PASSing blind10_result is handed in.
    if blind10_result is None:
        reasons.append(
            "no blind10_result recorded — acceptance_layer stays system_working "
            "(bestseller_register is a system-level, not single-book, verdict and "
            "is never auto-assigned by this module)"
        )
        return AcceptanceLayerResult(
            acceptance_layer=SYSTEM_WORKING,
            reasons=tuple(reasons),
            layer1_pass=True,
            layer2_pass=layer2_pass,
            layer3_pass=True,
            layer4_pass=None,
            research_fit_bound=research_fit_bound,
            inputs=inputs,
        )

    layer4_pass, layer4_reason = _layer4_passes(blind10_result)
    if layer4_reason:
        reasons.append(layer4_reason)
    if not layer4_pass:
        return AcceptanceLayerResult(
            acceptance_layer=SYSTEM_WORKING,
            reasons=tuple(reasons),
            layer1_pass=True,
            layer2_pass=layer2_pass,
            layer3_pass=True,
            layer4_pass=False,
            research_fit_bound=research_fit_bound,
            inputs=inputs,
        )

    reasons.append("bestseller_register: surfaced from an existing operator-recorded blind10 PASS")
    return AcceptanceLayerResult(
        acceptance_layer=BESTSELLER_REGISTER,
        reasons=tuple(reasons),
        layer1_pass=True,
        layer2_pass=layer2_pass,
        layer3_pass=True,
        layer4_pass=True,
        research_fit_bound=research_fit_bound,
        inputs=inputs,
    )


def rung_index(acceptance_layer: str) -> int:
    """Ordinal position of a layer name in the status-language ladder,
    lowest first. Useful for "did this book advance" comparisons."""
    try:
        return _RUNG_ORDER.index(acceptance_layer)
    except ValueError:
        return -1
