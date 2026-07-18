"""
ei.reader_council — P0.3 READER COUNCIL ADVISORY GATE (psychology pillar). Advisory.

Converged item:
  #1517 P0.3 "Reader Council v0 — 3-4 persona-agents on gemma3:27b +
             Outlines-constrained ReaderResponse; run as an ADVISORY QA gate."
  #1516      psychology / validation pillar.

THE DIRECT ANSWER TO RCG-013 (cited):
  RCG-013 says personas are "segments without validation source." A weight in a
  config is not a reader. Here each canonical persona becomes a GENERATIVE AGENT
  that READS a real gold-ref book and returns a structured felt-response GROUNDED
  IN A REAL PSYCHOLOGICAL FRAMEWORK — CBT (cognitive appraisal), IFS (parts /
  protectors), SDT (autonomy / competence / relatedness). Grounding the response
  in a named framework is the validation source RCG-013 asks for: the reader's
  reaction is anchored to established psychology, not asserted.

FREE/LOCAL ONLY:
  Ollama gemma3:27b on Pearl Star (serial GPU), native format=json for structured
  output (the free stand-in for Outlines/XGrammar). No paid API. Temperature 0 +
  fixed seed for reproducibility.

INTEGRITY:
  Advisory only — a sibling to the G1-G6 craft gates, NOT a fitness driver yet
  (that is P1). The council NEVER speaks AS a teacher; it speaks AS a reader
  reacting to the book.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path

from . import config as C
from . import corpus as corp
from . import ollama_client as oc


# ---------------------------------------------------------------------------
# persona cards — grounded in CBT / IFS / SDT (the RCG-013 validation source)
# ---------------------------------------------------------------------------
# Each card pairs a canonical persona id with a transparent psychological frame.
# These frames are the CITED grounding; the agent reads through this lens.
PERSONA_FRAMES = {
    "tech_finance_burnout": {
        "label": "Tech/finance professional, burned out",
        "cbt": "catastrophizes about falling behind; core belief 'my worth = my output'.",
        "ifs": "a fierce manager part drives overwork to protect an exhausted exile.",
        "sdt": "autonomy starved (calendar owns them); competence over-identified; relatedness thin.",
        "reads_for": "permission to rest without earning it; not one more optimization.",
    },
    "working_parents": {
        "label": "Working parent, depleted",
        "cbt": "guilt loops ('never enough for anyone'); all-or-nothing about self-care.",
        "ifs": "a caretaker part overrides every personal need; resentment exile underneath.",
        "sdt": "relatedness high but self-directed autonomy near zero.",
        "reads_for": "small, real practices that fit a life with no spare time.",
    },
    "millennial_women_professionals": {
        "label": "Millennial woman professional, high-functioning anxiety",
        "cbt": "mind-reading + fortune-telling about judgement; perfectionistic standards.",
        "ifs": "an inner critic part polices performance; a tender part wants to be seen.",
        "sdt": "competence strong, autonomy contested, relatedness curated/performative.",
        "reads_for": "language that names the felt experience precisely, not generic advice.",
    },
    "first_responders": {
        "label": "First responder, chronic activation",
        "cbt": "hypervigilance reads as realism; suppresses appraisal of own distress.",
        "ifs": "a protector part stays armored; vulnerability is dangerous.",
        "sdt": "competence central to identity; relatedness guarded; autonomy externally constrained.",
        "reads_for": "respect for their reality; nothing that feels soft or naive.",
    },
}

DEFAULT_COUNCIL = ["tech_finance_burnout", "working_parents",
                   "millennial_women_professionals", "first_responders"]


# ---------------------------------------------------------------------------
# structured response
# ---------------------------------------------------------------------------
@dataclass
class ReaderResponse:
    persona: str
    framework_lens: str
    landed: list                  # what resonated (what worked)
    did_not_land: list            # what missed / felt generic / off
    disengaged_at: str            # where they would put the book down
    felt_shift: str               # the emotional shift, if any
    autonomy_competence_relatedness: dict   # SDT read
    resonance_0_10: float         # advisory engagement signal
    would_finish: bool
    raw: dict = field(default_factory=dict)


_SCHEMA_HINT = """Return ONLY a JSON object with EXACTLY these keys:
{
  "landed": [ "short phrase", ... ],
  "did_not_land": [ "short phrase", ... ],
  "disengaged_at": "where in the book you would stop reading, or 'finished'",
  "felt_shift": "the emotional shift you felt, or 'none'",
  "sdt": {"autonomy": "...", "competence": "...", "relatedness": "..."},
  "resonance_0_10": <number 0-10>,
  "would_finish": <true|false>
}"""


def _build_prompt(persona_id: str, frame: dict, book_excerpt: str) -> tuple[str, str]:
    system = (
        f"You are a READER, not a critic and not a teacher. You are {frame['label']}. "
        f"React only as this person would. Ground your reaction in how this person's "
        f"psychology works:\n"
        f"- Cognitive (CBT): {frame['cbt']}\n"
        f"- Parts (IFS): {frame['ifs']}\n"
        f"- Needs (SDT): {frame['sdt']}\n"
        f"You are reading a self-help / contemplative book. You read for: {frame['reads_for']}\n"
        f"Be honest about what bored you or felt generic. Never pretend to be the author."
    )
    prompt = (
        f"Here is the book (excerpt):\n\n\"\"\"\n{book_excerpt}\n\"\"\"\n\n"
        f"As this reader, give your honest felt-response.\n{_SCHEMA_HINT}"
    )
    return system, prompt


def read_book(persona_id: str, book_text: str, *, model: str | None = None,
              max_chars: int = 9000, seed: int = 42) -> ReaderResponse | None:
    frame = PERSONA_FRAMES.get(persona_id)
    if not frame:
        return None
    excerpt = book_text[:max_chars]
    system, prompt = _build_prompt(persona_id, frame, excerpt)
    obj = oc.generate_json(prompt, model=model, seed=seed, system=system)
    if not obj:
        return None

    def _aslist(x):
        if isinstance(x, list):
            return [str(i) for i in x]
        if x is None:
            return []
        return [str(x)]

    try:
        res = float(obj.get("resonance_0_10", 5))
    except Exception:
        res = 5.0
    sdt = obj.get("sdt") or {}
    if not isinstance(sdt, dict):
        sdt = {"note": str(sdt)}

    return ReaderResponse(
        persona=persona_id,
        framework_lens="CBT (appraisal) + IFS (parts) + SDT (autonomy/competence/relatedness)",
        landed=_aslist(obj.get("landed")),
        did_not_land=_aslist(obj.get("did_not_land")),
        disengaged_at=str(obj.get("disengaged_at", "")),
        felt_shift=str(obj.get("felt_shift", "")),
        autonomy_competence_relatedness=sdt,
        resonance_0_10=res,
        would_finish=bool(obj.get("would_finish", False)),
        raw=obj,
    )


@dataclass
class CouncilReport:
    book: str
    model: str
    n_personas: int
    responses: list
    mean_resonance: float
    finish_rate: float
    advisory_note: str


def convene(book_path: Path, personas: list[str] | None = None,
            model: str | None = None) -> CouncilReport:
    personas = personas or DEFAULT_COUNCIL
    model = model or C.OLLAMA["council_model"]
    text = corp.load_gold_ref(book_path)
    responses = []
    for pid in personas:
        r = read_book(pid, text, model=model)
        if r:
            responses.append(r)
    res_vals = [r.resonance_0_10 for r in responses] or [0.0]
    finish = [1 for r in responses if r.would_finish]
    return CouncilReport(
        book=Path(book_path).name,
        model=model,
        n_personas=len(responses),
        responses=responses,
        mean_resonance=round(sum(res_vals) / len(res_vals), 2),
        finish_rate=round(len(finish) / max(len(responses), 1), 2),
        advisory_note=("ADVISORY ONLY — sibling to G1-G6 craft gates, NOT a fitness "
                       "driver (that is P1). Grounded in CBT/IFS/SDT per RCG-013."),
    )


def report_to_dict(rep: CouncilReport) -> dict:
    return {
        "book": rep.book, "model": rep.model, "n_personas": rep.n_personas,
        "mean_resonance": rep.mean_resonance, "finish_rate": rep.finish_rate,
        "advisory_note": rep.advisory_note,
        "responses": [asdict(r) for r in rep.responses],
    }
