#!/usr/bin/env python3
"""
Complete ch1 preview v4: v3 atom cleanup (exercise de-glue, pivot≠integration, one practice).

Usage:
  PYTHONPATH=. python3 scripts/qa/assemble_ch1_12shape_preview_v4.py
"""
from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

PERSONA = "gen_z_professionals"
TOPIC = "anxiety"
ENGINE = "overwhelm"
ANGLE_ID = "PROTECTIVE_ALARM"
CHARACTER = "Priya"
OBJECT = "after_send_reply_anxiety"
SEED = "ch1_12shape_preview_v4:gen_z_professionals:anxiety:20260705"
OUT_DIR = REPO_ROOT / "artifacts" / "qa" / "ch1_12shape_preview_v4_20260705"
V3_PATH = REPO_ROOT / "artifacts" / "qa" / "ch1_12shape_preview_v3_20260705/complete_ch1.txt"

REFINED_SLOTS = [
    "HOOK",
    "ANGLE_DEFINITION",
    "SCENE",
    "STORY",
    "PIVOT",
    "REFLECTION",
    "EXERCISE",
    "STORY",
    "STORY",
    "TAKEAWAY",
    "INTEGRATION",
    "THREAD",
]
_STORY_ARC = ("recognition", "mechanism_proof", "turning_point")

CH1_DOCTRINE_ID = "COMPOSITE_DOCTRINE v03"
EXERCISE_ID = "med_007"

ATOM_PICKS = {
    "HOOK": ("HOOK v89", "atoms/gen_z_professionals/anxiety/HOOK/CANONICAL.txt"),
    "SCENE": ("SCENE v83", "atoms/gen_z_professionals/anxiety/SCENE/CANONICAL.txt"),
    "PIVOT": ("PIVOT v50", "atoms/gen_z_professionals/anxiety/PIVOT/CANONICAL.txt"),
    "TAKEAWAY": ("TAKEAWAY v19", "atoms/gen_z_professionals/anxiety/TAKEAWAY/CANONICAL.txt"),
    "INTEGRATION": ("INTEGRATION v26", "atoms/gen_z_professionals/anxiety/INTEGRATION/CANONICAL.txt"),
    "THREAD": ("THREAD v13", "atoms/gen_z_professionals/anxiety/THREAD/CANONICAL.txt"),
}

STORY_PICKS = {
    "recognition": ("overwhelm/recognition/micro/v03.txt", "story_plan:HARDSHIP:story_0:recognition:overwhelm:v03"),
    "mechanism_proof": ("overwhelm/mechanism_proof/micro/v05.txt", "story_plan:HARDSHIP:story_0:mechanism_proof:overwhelm:v05"),
    "turning_point": ("overwhelm/turning_point/micro/v08.txt", "story_plan:HARDSHIP:story_0:turning_point:overwhelm:v08"),
}

_EXERCISE_GLUE = (
    r"Now we're going to do a practice",
    r"You do not need to believe that",
    r"Just try it",
    r"This is Noting Practice",
    r"Now, I want you to notice something",
    r"Whatever happened — or did not happen — is exactly right",
)

_PIVOT_INTEGRATION_SHARED = (
    r"third night",
    r"one counter",
    r"chest will object",
    r"phone face.?down",
    r"put the phone",
    r"11pm slack",
)

_EMBEDDED_PRACTICE_MARKERS = (
    r"Sit somewhere quiet for two minutes",
    r"Practice noticing the seam",
    r"Find the gap\.",
)

_TEACHER_TRADITION_RE = re.compile(
    r"(?i)(?:contemplative tradition teaches|rooted in the contemplative tradition)"
)


@dataclass
class BeatRecord:
    slot: str
    atom_id: str
    bank: str
    prose: str
    slot_index: int = 0
    story_arc: str = ""
    notes: str = ""


@dataclass
class ChapterPreview:
    beats: list[BeatRecord] = field(default_factory=list)
    character: str = CHARACTER
    anxiety_object: str = OBJECT


@dataclass
class GateResult:
    name: str
    passed: bool
    detail: str


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip() if path.exists() else ""


def _atom_by_id(canonical_path: Path, atom_id: str) -> str:
    from phoenix_v4.planning.registry_resolver import _parse_canonical_txt

    slot = canonical_path.parent.name
    for atom in _parse_canonical_txt(canonical_path, slot_type=slot):
        if str(atom.get("atom_id") or "").strip() == atom_id:
            return str(atom.get("content") or "").strip()
    return ""


def _load_angle_definition() -> tuple[str, str, str]:
    from phoenix_v4.planning.enrichment_select import _try_angle_definition

    hit = _try_angle_definition(
        persona_id=PERSONA,
        topic_id=TOPIC,
        angle_id=ANGLE_ID,
        repo_root=REPO_ROOT,
        fallback_warnings=[],
    )
    if hit:
        body, _src, sid = hit
        bank = f"atoms/{PERSONA}/{TOPIC}/ANGLE_DEFINITION/PROTECTIVE_ALARM/CANONICAL.txt"
        return sid, body.strip(), bank
    return "EMPTY", "[BANK EMPTY — author gap]", ""


def _load_story(arc: str) -> tuple[str, str, str]:
    rel, sid = STORY_PICKS[arc]
    path = REPO_ROOT / "story_atoms" / PERSONA / "anchored" / TOPIC / rel
    return sid, _read(path), f"story_atoms/{PERSONA}/anchored/{TOPIC}/{rel}"


def _load_doctrine() -> tuple[str, str, str]:
    path = REPO_ROOT / "SOURCE_OF_TRUTH/composite_doctrine/anxiety/REFLECTION/CANONICAL.txt"
    body = _atom_by_id(path, CH1_DOCTRINE_ID)
    return CH1_DOCTRINE_ID, body, str(path.relative_to(REPO_ROOT))


def _load_exercise_med007() -> tuple[str, str, str]:
    from phoenix_v4.exercises.practice_library_loader import (
        compose_exercise,
        load_component_templates,
        load_practice_library,
    )

    library = load_practice_library()
    all_ex = [e for exercises in library.values() for e in exercises]
    exercise = next((e for e in all_ex if e.get("id") == EXERCISE_ID), None)
    if not exercise:
        return "EMPTY", "[BANK EMPTY — author gap]", ""
    composed = compose_exercise(
        exercise, 0, SEED, load_component_templates(), content_only=True
    )
    return (
        EXERCISE_ID,
        composed.strip(),
        "SOURCE_OF_TRUTH/practice_library/inbox/meditations_library_34_PRODUCTION_READY.json",
    )


def assemble_v4() -> ChapterPreview:
    preview = ChapterPreview()
    story_i = 0

    for i, slot in enumerate(REFINED_SLOTS):
        aid, body, bank, note = "", "", "", ""
        arc = ""

        if slot == "HOOK":
            aid, bank = ATOM_PICKS["HOOK"]
            body = _atom_by_id(REPO_ROOT / bank, aid)
        elif slot == "ANGLE_DEFINITION":
            aid, body, bank = _load_angle_definition()
            note = "PROTECTIVE_ALARM persona slice; seeds Sunday→Monday"
        elif slot == "SCENE":
            aid, bank = ATOM_PICKS["SCENE"]
            body = _atom_by_id(REPO_ROOT / bank, aid)
            note = f"character={CHARACTER}; pre-send setup"
        elif slot == "STORY":
            arc = _STORY_ARC[story_i]
            story_i += 1
            aid, body, bank = _load_story(arc)
            note = f"character={CHARACTER}; arc={arc}"
        elif slot == "REFLECTION":
            aid, body, bank = _load_doctrine()
            note = "v03 sensation-vs-story — reflection only, no embedded practice"
        elif slot == "EXERCISE":
            aid, body, bank = _load_exercise_med007()
            note = "med_007 content_only — bridge + description, no assembly glue"
        elif slot == "PIVOT":
            aid, bank = ATOM_PICKS["PIVOT"]
            body = _atom_by_id(REPO_ROOT / bank, aid)
            note = "principle-only; INTEGRATION owns concrete 11pm rep"
        elif slot in ("TAKEAWAY", "INTEGRATION", "THREAD"):
            aid, bank = ATOM_PICKS[slot]
            body = _atom_by_id(REPO_ROOT / bank, aid)

        preview.beats.append(
            BeatRecord(
                slot=slot,
                atom_id=aid,
                bank=bank,
                prose=body or "[BANK EMPTY — author gap]",
                slot_index=i,
                story_arc=arc,
                notes=note,
            )
        )

    return preview


def _reader_prose(preview: ChapterPreview) -> str:
    parts = [
        b.prose.strip()
        for b in preview.beats
        if b.prose and "[BANK EMPTY" not in b.prose
    ]
    return "\n\n".join(parts) + "\n"


def _format_annotated(preview: ChapterPreview) -> str:
    lines = [
        "Chapter 1 — promise_engine v4 (atom cleanup)",
        f"Cell: {PERSONA} × {TOPIC} | Character: {CHARACTER} | Object: {OBJECT}",
        f"Fixes: exercise de-glue | pivot≠integration | one practice (v03)",
        "",
        "=" * 72,
        "",
    ]
    for beat in preview.beats:
        label = f"{beat.slot}({beat.story_arc})" if beat.story_arc else beat.slot
        lines.extend([
            f"[SLOT: {label} — atom {beat.atom_id} from {beat.bank}]",
            f"  ({beat.notes})" if beat.notes else "",
            "",
            beat.prose,
            "",
            "-" * 72,
            "",
        ])
    return "\n".join(line for line in lines if line is not None).rstrip() + "\n"


def run_gates(preview: ChapterPreview) -> list[GateResult]:
    full = _reader_prose(preview)
    results: list[GateResult] = []

    glue = [p for p in _EXERCISE_GLUE if re.search(p, full, re.I)]
    results.append(
        GateResult(
            "NO EXERCISE GLUE",
            not glue,
            f"glue phrases found={glue or 'none'}",
        )
    )

    pivot = next((b for b in preview.beats if b.slot == "PIVOT"), None)
    integration = next((b for b in preview.beats if b.slot == "INTEGRATION"), None)
    shared: list[str] = []
    if pivot and integration:
        shared = [
            p
            for p in _PIVOT_INTEGRATION_SHARED
            if re.search(p, pivot.prose, re.I) and re.search(p, integration.prose, re.I)
        ]
        sim = SequenceMatcher(None, pivot.prose.lower(), integration.prose.lower()).ratio()
    else:
        sim = 0.0
    results.append(
        GateResult(
            "PIVOT ≠ INTEGRATION",
            not shared and sim < 0.35,
            f"shared phrases={shared or 'none'}; similarity={sim:.2f}",
        )
    )

    reflection = next((b for b in preview.beats if b.slot == "REFLECTION"), None)
    embedded = [
        p for p in _EMBEDDED_PRACTICE_MARKERS
        if reflection and re.search(p, reflection.prose, re.I)
    ]
    exercise = next((b for b in preview.beats if b.slot == "EXERCISE"), None)
    has_exercise = exercise and "note them" in exercise.prose.lower()
    results.append(
        GateResult(
            "ONE PRACTICE",
            not embedded and bool(has_exercise),
            f"doctrine embedded practice={embedded or 'none'}; EXERCISE slot present={bool(has_exercise)}",
        )
    )

    gaps = [b.slot for b in preview.beats if b.atom_id == "EMPTY" or "[BANK EMPTY" in b.prose]
    results.append(
        GateResult("NO PLACEHOLDERS", not gaps, f"empty slots={gaps or 'none'}")
    )

    priya = bool(re.search(rf"\b{CHARACTER}\b", full))
    forbidden = [n for n in ("Hana", "Min") if re.search(rf"\b{n}\b", full)]
    results.append(
        GateResult(
            "ONE CHARACTER",
            priya and not forbidden,
            f"Priya={priya}; forbidden={forbidden or 'none'}",
        )
    )

    has_v03 = "small space between the sensation and the story" in full.lower()
    results.append(
        GateResult("ONE DOCTRINE", has_v03, f"sensation-vs-story present={has_v03}")
    )

    return results


def _manifest(preview: ChapterPreview, gates: list[GateResult]) -> dict[str, Any]:
    return {
        "version": "v4",
        "v4_fixes": {
            "exercise_glue": "med_007 content_only render; glue from compose_exercise + intro components (bank-wide follow-up)",
            "pivot_integration": "PIVOT v50 rewritten principle-only; INTEGRATION v26 keeps concrete 11pm rep",
            "one_practice": "COMPOSITE_DOCTRINE v03_pure (no embedded practice); EXERCISE med_007 only",
        },
        "beats": [
            {
                "slot": b.slot,
                "atom_id": b.atom_id,
                "bank": b.bank,
                "word_count": len(b.prose.split()),
                "notes": b.notes,
            }
            for b in preview.beats
        ],
        "continuity_gates": [
            {"test": g.name, "pass": g.passed, "detail": g.detail} for g in gates
        ],
        "all_gates_pass": all(g.passed for g in gates),
    }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    preview = assemble_v4()
    gates = run_gates(preview)

    complete_path = OUT_DIR / "complete_ch1.txt"
    complete_path.write_text(_reader_prose(preview), encoding="utf-8")
    (OUT_DIR / "annotated_ch1.txt").write_text(_format_annotated(preview), encoding="utf-8")
    (OUT_DIR / "manifest.json").write_text(
        json.dumps(_manifest(preview, gates), indent=2), encoding="utf-8"
    )

    rubric = ["# Ch1 continuity rubric — v4", "", "| Test | Pass | Detail |", "|------|------|--------|"]
    for g in gates:
        rubric.append(f"| {g.name} | {'PASS' if g.passed else '**FAIL**'} | {g.detail} |")
    rubric.append("")
    rubric.append(
        f"**Overall:** {'ALL PASS' if all(g.passed for g in gates) else 'BLOCKED'}"
    )
    (OUT_DIR / "continuity_rubric.md").write_text("\n".join(rubric) + "\n", encoding="utf-8")

    print(f"Wrote {complete_path}")
    for g in gates:
        print(f"  [{'PASS' if g.passed else 'FAIL'}] {g.name}: {g.detail}")

    if not all(g.passed for g in gates):
        return 1

    subprocess.run(["open", str(complete_path)], check=False)
    if V3_PATH.exists():
        subprocess.run(["open", str(V3_PATH)], check=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
