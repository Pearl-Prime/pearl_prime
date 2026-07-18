"""
ei.felt_arc — P0.5 FELT-ARC STATE ESTIMATOR (valence + arousal). Advisory.

Converged item:
  #1517 P0.2 "Felt-Arc State Machine v0 — add an arousal axis (NRC-VAD) to the
             existing valence felt-arc; formalize somatic_healing_spine.yaml's
             intensity/trust/permission as an explicit state graph; ship
             somatic_state_fit as a new advisory scoring dimension."
  #1516   somatic delivery feeds the T (therapeutic) objective.

Cites the repo's own mandate:
  RCG-007 "nervous-system claims uncited"  -> we ground the arc in a transparent
          VAD lexicon, not an asserted physiology claim.
  RCG-022 "teacher-bank pedagogy uncited"  -> the somatic spine's chapter ROLES
          (recognition -> ... -> integration) are the pedagogy; we measure
          whether prose tracks that intended arc.

What it does (free/local, CPU, deterministic):
  1. Score any text's emotional trajectory on TWO axes — valence (pleasant<->
     unpleasant) and arousal (calm<->activated) — using a vendored, open-licensed
     VAD lexicon subset (NRC-VAD licensing is roadmap risk #4 -> we DO NOT ship
     NRC-VAD; we ship an open subset and FLAG it for licence review).
  2. Map the somatic_healing_spine's 12 chapter ROLES to an INTENDED arc
     (e.g. destabilization = lower valence + higher arousal; integration =
     higher valence + lower arousal).
  3. somatic_state_fit = how well a book's measured per-chapter arc tracks the
     intended arc. Advisory only.

The book must follow "observation before intervention" — the estimator checks
the arousal curve does NOT spike before the mechanism chapter (titration, not
catharsis), matching the spine's explicit non-negotiable.
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import yaml

from . import config as C

_VAD_PATH = Path(__file__).resolve().parent / "data" / "vad_lexicon.tsv"


# ---------------------------------------------------------------------------
# VAD lexicon (vendored open subset; valence & arousal in [0,1], 0.5 neutral)
# ---------------------------------------------------------------------------
class _Lexicon:
    _v: dict | None = None
    _a: dict | None = None

    @classmethod
    def load(cls):
        if cls._v is not None:
            return cls._v, cls._a
        v, a = {}, {}
        if _VAD_PATH.exists():
            with _VAD_PATH.open(encoding="utf-8") as fh:
                r = csv.DictReader(fh, delimiter="\t")
                for row in r:
                    w = row["word"].strip().lower()
                    try:
                        v[w] = float(row["valence"])
                        a[w] = float(row["arousal"])
                    except Exception:
                        continue
        cls._v, cls._a = v, a
        return v, a


_WORD_RE = re.compile(r"[a-z][a-z\-']+")


def score_text_vad(text: str) -> tuple[float, float, int]:
    """
    Return (valence, arousal, n_hits) for a span. Mean over in-lexicon tokens;
    falls back to neutral (0.5, 0.5) when no tokens match.
    """
    v_lex, a_lex = _Lexicon.load()
    toks = _WORD_RE.findall(text.lower())
    vs, ars = [], []
    for t in toks:
        if t in v_lex:
            vs.append(v_lex[t])
            ars.append(a_lex[t])
    if not vs:
        return 0.5, 0.5, 0
    return float(np.mean(vs)), float(np.mean(ars)), len(vs)


def arc_over_segments(segments: list[str], smooth: int | None = None) -> list[dict]:
    """Per-segment valence/arousal, lightly smoothed."""
    smooth = smooth if smooth is not None else C.FELT_ARC["smooth_window"]
    raw = [score_text_vad(s) for s in segments]
    vals = np.array([r[0] for r in raw])
    aros = np.array([r[1] for r in raw])
    hits = [r[2] for r in raw]

    def _smooth(x):
        if smooth <= 1 or len(x) < smooth:
            return x
        k = np.ones(smooth) / smooth
        return np.convolve(x, k, mode="same")

    sv, sa = _smooth(vals), _smooth(aros)
    return [
        {"segment": i, "valence": round(float(sv[i]), 4),
         "arousal": round(float(sa[i]), 4), "n_vad_hits": hits[i]}
        for i in range(len(segments))
    ]


# ---------------------------------------------------------------------------
# the INTENDED arc from the somatic spine's chapter roles
# ---------------------------------------------------------------------------
# Each role -> (target_valence, target_arousal) on [0,1]. Grounded in the spine's
# own narrative: destabilization/cost-exposure dip valence and raise arousal;
# integration resolves to higher valence + lower arousal (a settled nervous
# system). This is the felt-arc the pedagogy intends.
ROLE_TARGETS = {
    "recognition":            (0.45, 0.50),
    "somatic_legitimacy":     (0.50, 0.45),
    "mechanism":              (0.52, 0.42),  # observation skill: calm
    "hidden_belief":          (0.42, 0.55),
    "destabilization":        (0.35, 0.65),  # the dip (after mechanism, by design)
    "practical_interruption": (0.50, 0.45),  # titration brings arousal back down
    "cost_exposure":          (0.38, 0.58),
    "reframe":                (0.55, 0.45),
    "self_relation_shift":    (0.60, 0.40),
    "practice_under_pressure":(0.52, 0.50),
    "identity_fracture":      (0.50, 0.52),
    "integration":            (0.68, 0.35),  # settled, legible, calm
}


def load_somatic_arc(spine_path: Path | None = None) -> list[dict]:
    """Read the somatic spine's chapters -> ordered (number, role, intended VA)."""
    spine_path = spine_path or (C.CONFIG_DIR / "spines" / "somatic_healing_spine.yaml")
    data = yaml.safe_load(Path(spine_path).read_text(encoding="utf-8"))
    chapters = data.get("chapters", {})
    rows = []
    for key, ch in sorted(chapters.items(), key=lambda kv: kv[1].get("number", 0)):
        role = ch.get("role", "")
        tv, ta = ROLE_TARGETS.get(role, (0.5, 0.5))
        rows.append({
            "number": ch.get("number"),
            "role": role,
            "title": ch.get("working_title", ""),
            "intended_valence": tv,
            "intended_arousal": ta,
        })
    return rows


# ---------------------------------------------------------------------------
# somatic_state_fit : measured arc vs intended arc
# ---------------------------------------------------------------------------
@dataclass
class SomaticFitReport:
    n_chapters: int
    intended: list[dict]
    measured: list[dict]
    valence_rmse: float
    arousal_rmse: float
    somatic_state_fit: float           # 1 - normalized error, in [0,1]
    observation_before_intervention_ok: bool
    notes: list[str] = field(default_factory=list)


def somatic_state_fit(book_text: str, n_chapters: int | None = None,
                      spine_path: Path | None = None) -> SomaticFitReport:
    """
    Split a book into n_chapters equal segments, measure each segment's VA, and
    compare to the somatic spine's intended per-chapter arc.

    observation_before_intervention check: arousal must not exceed the
    destabilization target before the mechanism chapter (the spine's
    non-negotiable: learn to watch before working with).
    """
    intended = load_somatic_arc(spine_path)
    n = n_chapters or len(intended)
    intended = intended[:n]

    # segment the book into n parts
    words = book_text.split()
    if not words:
        seg_texts = [""] * n
    else:
        size = max(1, len(words) // n)
        seg_texts = [" ".join(words[i * size:(i + 1) * size]) for i in range(n)]
        # fold any remainder into the last segment
        if len(words) > n * size:
            seg_texts[-1] += " " + " ".join(words[n * size:])

    measured_arc = arc_over_segments(seg_texts)
    for i, m in enumerate(measured_arc):
        m["role"] = intended[i]["role"] if i < len(intended) else ""

    iv = np.array([c["intended_valence"] for c in intended])
    ia = np.array([c["intended_arousal"] for c in intended])
    mv = np.array([m["valence"] for m in measured_arc[:n]])
    ma = np.array([m["arousal"] for m in measured_arc[:n]])

    v_rmse = float(np.sqrt(np.mean((iv - mv) ** 2)))
    a_rmse = float(np.sqrt(np.mean((ia - ma) ** 2)))
    fit = float(max(0.0, 1.0 - (v_rmse + a_rmse) / 2.0))

    # observation-before-intervention: find mechanism chapter index
    notes = []
    mech_idx = next((i for i, c in enumerate(intended) if c["role"] == "mechanism"), None)
    obi_ok = True
    if mech_idx is not None and mech_idx > 0:
        destab_arousal = 0.65
        pre = ma[:mech_idx]
        if pre.size and float(pre.max()) >= destab_arousal:
            obi_ok = False
            notes.append(
                f"arousal peaks ({float(pre.max()):.2f}) before the mechanism chapter "
                f"(ch {mech_idx + 1}) — risks intervention-before-observation."
            )
        else:
            notes.append("arousal stays measured before the mechanism chapter (observation-first OK).")

    return SomaticFitReport(
        n_chapters=n,
        intended=intended,
        measured=measured_arc[:n],
        valence_rmse=round(v_rmse, 4),
        arousal_rmse=round(a_rmse, 4),
        somatic_state_fit=round(fit, 4),
        observation_before_intervention_ok=obi_ok,
        notes=notes,
    )
