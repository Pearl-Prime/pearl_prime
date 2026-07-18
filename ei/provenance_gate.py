"""
ei.provenance_gate — P0.4 PROVENANCE + DOCTRINE GATE (advisory).

Converged item:
  #1517 P0.4 "Provenance + doctrine gate v0 — compile forbidden_claims /
             prohibited_outcomes / prohibited_terms into rule checks"
  #1516   "provenance checked INSIDE the feasibility test" (folds into P0.2's Φ floor)

Two jobs:
  1. PROVENANCE-BY-CONSTRUCTION: every atom must carry a real teacher_id that
     maps to a known doctrine. An atom with no provenance is a hard violation
     (integrity guarantee #1).
  2. DOCTRINE FIDELITY: each teacher's doctrine declares forbidden_claims,
     prohibited_outcomes, prohibited_terms. We compile these into matchable
     rules and flag any atom/sequence text that trips a teacher's OWN
     prohibitions, OR that mixes one teacher's atoms with another teacher's
     forbidden framing (cross-contamination).

This is a free, deterministic, rule-based gate (no LLM, no paid API). It does
NOT modify production lint; it is a standalone advisory checker and the basis
for the Φ feasibility test in ei.fitness.

Design note — guarantee #4 (fidelity-as-floor): violations are BINARY (a claim
is forbidden or it isn't); the gate returns pass/fail + the offending rule, not
a soft score. ei.fitness consumes pass/fail as the hard feasibility floor.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from . import config as C
from . import corpus as corp


@dataclass
class Rule:
    teacher_id: str
    kind: str                # forbidden_claim | prohibited_outcome | prohibited_term
    source_text: str         # the doctrine line
    terms: list[str]         # extracted matchable terms (lowercased)


@dataclass
class Violation:
    atom_id: str
    teacher_id: str          # whose atom
    rule_teacher: str        # whose rule was tripped
    kind: str
    rule_text: str
    matched_terms: list[str]
    snippet: str
    cross_teacher: bool      # True if rule_teacher != atom's teacher


# ---------------------------------------------------------------------------
# compile doctrine prohibitions into rules
# ---------------------------------------------------------------------------
# Only true function words are stopped. Content words that carry the forbidden
# FRAMING (abstract / intellectual / system / separation / contemplative / ...)
# are KEPT — they are the whole point of a forbidden_claim rule.
_TERM_STOP = set("""the a an and or of to in on for with as is are was that this it its their your
you not no nor without into onto from than then""".split())


def _extract_terms(line: str, min_len: int = 4, max_terms: int = 6) -> list[str]:
    """Pull the distinctive content words from a doctrine prohibition line."""
    words = re.findall(r"[A-Za-z][A-Za-z\-]+", line.lower())
    seen = []
    for w in words:
        if len(w) >= min_len and w not in _TERM_STOP and w not in seen:
            seen.append(w)
    return seen[:max_terms]


def compile_rules(teacher_ids: list[str] | None = None) -> list[Rule]:
    rules: list[Rule] = []
    for tid in (teacher_ids or C.all_teacher_ids()):
        doc = corp.load_doctrine(tid)
        if not doc:
            continue
        for kind, items in (
            ("forbidden_claim", doc.forbidden_claims),
            ("prohibited_outcome", doc.prohibited_outcomes),
            ("prohibited_term", doc.prohibited_terms),
        ):
            for line in items:
                terms = _extract_terms(line)
                if terms:
                    rules.append(Rule(teacher_id=tid, kind=kind, source_text=line, terms=terms))
    return rules


# ---------------------------------------------------------------------------
# provenance check
# ---------------------------------------------------------------------------
def check_provenance(atoms) -> list[str]:
    """Return atom_ids that lack a valid teacher provenance (hard violations)."""
    known = set(C.all_teacher_ids())
    bad = []
    for a in atoms:
        if not a.teacher_id or a.teacher_id not in known:
            bad.append(a.atom_id)
    return bad


# ---------------------------------------------------------------------------
# doctrine-fidelity check over a text / atom set
# ---------------------------------------------------------------------------
_NEGATION = re.compile(r"\b(not|never|no|isn't|aren't|without|opposite of|rather than|instead of)\b")


def _rule_trips(text_l: str, rule: Rule, min_hits: int = 2, window: int = 14) -> list[str]:
    """
    A rule trips if a strong fraction of its distinctive terms co-occur WITHIN A
    TIGHT WINDOW (forbidden *framing*, not just shared vocabulary), AND the span
    is not explicitly negated.

    KNOWN LIMITATION (honest, surfaced in EI_P0_RESULTS.md): this is lexical, not
    semantic. It cannot distinguish "X is the problem" from "X is NOT the
    problem"; the negation guard catches the obvious flips, but true stance
    detection is a P1 need (an embedding/NLI gate). The P0 gate is a coarse,
    deterministic, free first-pass — provenance is exact; framing is approximate.
    """
    toks = re.findall(r"[a-z][a-z\-']+", text_l)
    pos = {}
    for i, w in enumerate(toks):
        pos.setdefault(w, []).append(i)
    present = [t for t in rule.terms if t in pos]
    # require a strong fraction of the rule's terms (>=3, or all if fewer)
    need = max(min_hits, min(3, len(rule.terms)))
    if len(present) < need:
        return []
    # proximity: the present terms must fit inside a window of `window` tokens
    idxs = sorted(min(pos[t]) for t in present)
    tight = []
    for t in present:
        # is this term near the cluster median?
        pass
    span = idxs[-1] - idxs[0]
    if span > window * max(1, len(present) - 1):
        return []
    # negation guard: if the window around the cluster contains an explicit
    # negation, do NOT trip (the atom likely refutes the forbidden framing).
    lo = max(0, idxs[0] - 4)
    hi = min(len(toks), idxs[-1] + 4)
    window_text = " ".join(toks[lo:hi])
    if _NEGATION.search(window_text):
        return []
    return present


def check_atom_against_rules(atom, rules: list[Rule], *, cross_teacher: bool = True,
                             min_hits: int = 2) -> list[Violation]:
    text_l = atom.text.lower()
    out: list[Violation] = []
    for rule in rules:
        is_cross = rule.teacher_id != atom.teacher_id
        if is_cross and not cross_teacher:
            continue
        hits = _rule_trips(text_l, rule, min_hits=min_hits)
        if hits:
            out.append(Violation(
                atom_id=atom.atom_id,
                teacher_id=atom.teacher_id,
                rule_teacher=rule.teacher_id,
                kind=rule.kind,
                rule_text=rule.source_text,
                matched_terms=hits,
                snippet=atom.text[:160],
                cross_teacher=is_cross,
            ))
    return out


@dataclass
class GateReport:
    n_atoms: int
    n_rules: int
    provenance_violations: list[str]
    own_doctrine_violations: list[Violation]      # atom trips its OWN teacher's rule
    cross_teacher_violations: list[Violation]      # atom trips ANOTHER teacher's rule
    feasible: bool                                  # own-doctrine clean (the hard floor)

    def summary(self) -> dict:
        return {
            "n_atoms": self.n_atoms,
            "n_rules": self.n_rules,
            "provenance_violations": len(self.provenance_violations),
            "own_doctrine_violations": len(self.own_doctrine_violations),
            "cross_teacher_violations": len(self.cross_teacher_violations),
            "feasible_provenance_and_own_doctrine": self.feasible,
        }


def run_gate(atoms=None, *, min_hits: int = 2) -> GateReport:
    """
    The advisory gate over the whole corpus (or a supplied atom set).

    feasible == (no provenance violations) AND (no atom trips its OWN doctrine).
    Cross-teacher trips are reported separately: they flag where ONE teacher's
    language would violate ANOTHER's doctrine — the exact contamination the
    "no homogenization" guarantee guards against when atoms are mixed.
    """
    if atoms is None:
        atoms = corp.load_atoms()
    rules = compile_rules()

    prov_bad = check_provenance(atoms)

    own: list[Violation] = []
    cross: list[Violation] = []
    for a in atoms:
        for v in check_atom_against_rules(a, rules, cross_teacher=True, min_hits=min_hits):
            (own if not v.cross_teacher else cross).append(v)

    feasible = (len(prov_bad) == 0) and (len(own) == 0)
    return GateReport(
        n_atoms=len(atoms),
        n_rules=len(rules),
        provenance_violations=prov_bad,
        own_doctrine_violations=own,
        cross_teacher_violations=cross,
        feasible=feasible,
    )


def is_sequence_feasible(atoms, *, min_hits: int = 2) -> tuple[bool, list[Violation]]:
    """
    The hook ei.fitness uses for the Φ hard floor: a candidate atom-sequence is
    feasible iff it has full provenance AND no atom violates its own doctrine.
    Returns (feasible, own_doctrine_violations).
    """
    rules = compile_rules(teacher_ids=sorted({a.teacher_id for a in atoms}))
    if check_provenance(atoms):
        return False, []
    own = []
    for a in atoms:
        own += [v for v in check_atom_against_rules(a, rules, cross_teacher=False, min_hits=min_hits)]
    return (len(own) == 0), own


# ---------------------------------------------------------------------------
# negative-control: a synthetic atom that SHOULD trip a known rule (for the test)
# ---------------------------------------------------------------------------
def forbidden_test_case():
    """
    Build a synthetic atom that deliberately trips ahjan's forbidden_claim
    "Buddhism as abstract intellectual system" — proves the gate BLOCKS a known
    forbidden claim (the #1517 P0 exit criterion).
    """
    from .corpus import Atom

    return Atom(
        atom_id="SYNTHETIC_FORBIDDEN_001",
        teacher_id="ahjan",
        atom_type="TEACHER_DOCTRINE",
        band="universal",
        body=("Buddhism is best understood as an abstract intellectual system, "
              "a purely intellectual abstract framework separated from the material world."),
    )
