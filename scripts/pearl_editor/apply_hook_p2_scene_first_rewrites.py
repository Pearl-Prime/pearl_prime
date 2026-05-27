#!/usr/bin/env python3
"""Apply HOOK v01 scene-first rewrites for P2 batch (ws_pearl_editor_hook_p2_rewrite_batch_20260527)."""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TSV = REPO / "artifacts/qa/HOOK_SCENE_FIRST_TAGGING_20260527.tsv"

V01_BLOCK_RE = re.compile(
    r"(## HOOK v01\n---\n\n---\n)([\s\S]*?)(\n---)",
    re.MULTILINE,
)
PLACEHOLDER_RE = re.compile(r"^\[Persona-specific hook for ")


def _split_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]


def replace_v01(atom_text: str, new_para1: str, *, move_old_to_para2: bool = True) -> str:
    m = V01_BLOCK_RE.search(atom_text)
    if not m:
        raise ValueError("No ## HOOK v01 block found")
    old_body = m.group(2).strip()
    old_paras = _split_paragraphs(old_body)
    parts = [new_para1.strip()]
    if move_old_to_para2 and old_paras:
        old_first = old_paras[0]
        if not PLACEHOLDER_RE.match(old_first) and old_first.strip() != new_para1.strip():
            parts.append(old_first)
        parts.extend(old_paras[1:])
    new_body = "\n\n".join(parts)
    return atom_text[: m.start(2)] + new_body + atom_text[m.end(2) :]


# P2: educators, gen_alpha_students, nyc_executives — MIXED / PHILOSOPHY_FIRST only
REWRITES: dict[str, str] = {
    "atoms/educators/anxiety/HOOK/CANONICAL.txt": (
        "Ms. Reyes is in the faculty lounge at 7:15 AM, coffee cooling, fingers pressed on the "
        "printed admin observation calendar — her chest is already tight three weeks before anyone "
        "walks into her classroom."
    ),
    "atoms/educators/burnout/HOOK/CANONICAL.txt": (
        "Elena is at her kitchen table on Sunday at 9 PM, lesson plan folder open, hands stopped "
        "above the page — she does not want to and she does not have anything left to give it."
    ),
    "atoms/educators/compassion_fatigue/HOOK/CANONICAL.txt": (
        "Mr. Holloway is alone in his classroom after the last bell, grading tray in his lap, "
        "shoulders heavy from the student who told him about home — his chest still carries it "
        "hours later."
    ),
    "atoms/educators/courage/HOOK/CANONICAL.txt": (
        "Ms. Reyes is standing outside the principal's office at 3:40 PM, hand raised to knock, "
        "palms damp — she already knows saying she's wrong will cost something and her body is "
        "doing it anyway."
    ),
    "atoms/educators/depression/HOOK/CANONICAL.txt": (
        "Naomi is in the hallway when the bell rings, feet moving toward her classroom on autopilot, "
        "chest heavy — she used to love this part of the day and now she is just standing up anyway."
    ),
    "atoms/educators/financial_anxiety/HOOK/CANONICAL.txt": (
        "Lena is at the kitchen table with her laptop open to the student loan portal, district "
        "salary-freeze email still on screen — her chest tightens on the math she already ran twice."
    ),
    "atoms/educators/financial_stress/HOOK/CANONICAL.txt": (
        "You're standing in the teacher supply aisle with a half-full cart, calculator app open on "
        "your phone, chest tight — you will buy the markers anyway because your students need them."
    ),
    "atoms/educators/grief/HOOK/CANONICAL.txt": (
        "Ms. Reyes is in the staff lounge between periods, eyes on the empty desk where a student "
        "used to sit — her chest feels hollow while the school bell schedules the next class."
    ),
    "atoms/educators/imposter_syndrome/HOOK/CANONICAL.txt": (
        "Dr. Patel is at the back of Elena's classroom during fourth period, arms folded, watching — "
        "Elena's throat closes even though she knows the content; her body does not believe she is "
        "allowed to know it."
    ),
    "atoms/educators/overthinking/HOOK/CANONICAL.txt": (
        "Maya is at her dining table three hours after school, dishes still in the sink, jaw tight — "
        "the moment one instruction did not land keeps replaying in her head at full volume."
    ),
    "atoms/educators/self_worth/HOOK/CANONICAL.txt": (
        "You're at your grading desk after school, red pen hovering over a stack of tests, chest "
        "tight — their score is about to become your worth again and you hate that you let it."
    ),
    "atoms/educators/sleep_anxiety/HOOK/CANONICAL.txt": (
        "Elena is in bed on Sunday at 10 PM, eyes open to the ceiling, shoulders braced — her body "
        "is already running Monday's attendance, the noon IEP, and the seat change she has not made yet."
    ),
    "atoms/educators/social_anxiety/HOOK/CANONICAL.txt": (
        "Mr. Holloway is at the front of the cafeteria-turned-auditorium on back-to-school night, "
        "forty parents staring up at him — his chest tightens the way it does for a room full of "
        "students, except these adults are judging the teacher, not the lesson."
    ),
    "atoms/educators/somatic_healing/HOOK/CANONICAL.txt": (
        "Elena sits on her couch on the last day of June, hands pressed into her lower back — nine "
        "months of standing, managing, and absorbing, and her body is presenting the bill."
    ),
    "atoms/gen_alpha_students/anxiety/HOOK/CANONICAL.txt": (
        "Jordan is at the bedroom desk on Tuesday night, practice test open, eraser worn down to a "
        "smear — chest already tight for an exam that is still a week away."
    ),
    "atoms/gen_alpha_students/boundaries/HOOK/CANONICAL.txt": (
        "Maya is on her bed with her phone lit, friend's text asking to copy the homework again — "
        "her stomach tightens because she already knows saying no will change something between them."
    ),
    "atoms/gen_alpha_students/burnout/HOOK/CANONICAL.txt": (
        "Leo is slumped at his desk after school, Chromebook open on three unfinished tabs, shoulders "
        "collapsed toward the keyboard — he has been running on empty since October and nobody named it."
    ),
    "atoms/gen_alpha_students/compassion_fatigue/HOOK/CANONICAL.txt": (
        "Jordan is lying on his bed at 8 PM, phone buzzing with another friend's crisis text — "
        "shoulders slumped because he is tired of being the person everyone tells everything to."
    ),
    "atoms/gen_alpha_students/depression/HOOK/CANONICAL.txt": (
        "Maya is under the covers at 6:45 AM when her alarm fires, chest compressed, eyes on the "
        "ceiling — she already dreads the hallway before her feet touch the floor."
    ),
    "atoms/gen_alpha_students/financial_stress/HOOK/CANONICAL.txt": (
        "Leo is in the cafeteria line hearing the group chat about the class trip, tray empty, stomach "
        "dropping — he is already drafting the lie about why he cannot go."
    ),
    "atoms/gen_alpha_students/imposter_syndrome/HOOK/CANONICAL.txt": (
        "Jordan is in the honors hallway between classes, eyes on the wall plaque, throat tight — "
        "part of him is still waiting for someone to say his seat in this program was a mistake."
    ),
    "atoms/gen_alpha_students/overthinking/HOOK/CANONICAL.txt": (
        "Maya is filming herself in the bathroom mirror at 9 PM, phone propped on the sink, jaw locked "
        "— she keeps re-recording the same fifteen seconds because the caption might reveal the wrong "
        "person."
    ),
    "atoms/gen_alpha_students/self_worth/HOOK/CANONICAL.txt": (
        "Leo is staring at the B on his phone screen in the hallway between third and fourth period, "
        "chest tight — his entire value collapsed in one grade before he reached homeroom."
    ),
    "atoms/gen_alpha_students/social_anxiety/HOOK/CANONICAL.txt": (
        "Maya is in bed at 11 PM, shoulders hunched over her phone, thumb scrolling — every post is "
        "another number telling her she is behind before tomorrow even starts."
    ),
    "atoms/gen_alpha_students/somatic_healing/HOOK/CANONICAL.txt": (
        "Leo is at his desk trying to roll his shoulders down, earbuds in, neck stiff — they have been "
        "held at his ears so long that straight started to feel wrong."
    ),
    "atoms/nyc_executives/anxiety/HOOK/CANONICAL.txt": (
        "Catherine is in the back seat of a town car at 11 PM, deal closed, phone dark in her lap — "
        "her chest is still braced as if the term sheet could still fall apart."
    ),
    "atoms/nyc_executives/burnout/HOOK/CANONICAL.txt": (
        "Catherine is alone at the fund-close dinner table on Friday night, champagne untouched, "
        "shoulders flat — her body did not register celebration, only the brief silence before the "
        "next mandate loads."
    ),
    "atoms/nyc_executives/compassion_fatigue/HOOK/CANONICAL.txt": (
        "Marcus is in his corner office at 6 PM, direct report crying on the couch across from him — "
        "his chest tightens because he is burned out too and still has to hold the room."
    ),
    "atoms/nyc_executives/courage/HOOK/CANONICAL.txt": (
        "Catherine is at the head of the board table, deal deck open, jaw set — she knows the numbers "
        "are wrong, the room disagrees, and her chest burns with the knowing she is about to voice."
    ),
    "atoms/nyc_executives/depression/HOOK/CANONICAL.txt": (
        "Marcus steps out of the town car at the gala, biggest deal of his career sealed hours ago, "
        "face flat in the camera flash — he arrived and felt nothing he was supposed to feel."
    ),
    "atoms/nyc_executives/financial_stress/HOOK/CANONICAL.txt": (
        "Catherine is in the elevator watching the market ticker on her phone, portfolio down two "
        "percent, chest contracted with it before the doors open on forty-three."
    ),
    "atoms/nyc_executives/grief/HOOK/CANONICAL.txt": (
        "Marcus is at his father's hospital bedside on Tuesday night, hand on the rail, Thursday's "
        "earnings call already on his watch — his chest knows which calendar entry the firm will treat "
        "as real."
    ),
    "atoms/nyc_executives/imposter_syndrome/HOOK/CANONICAL.txt": (
        "Catherine is at the board table under the plaque that says first woman to chair this committee, "
        "pen steady on her notes — her body spends every session scanning for the moment they decide "
        "it was a mistake."
    ),
    "atoms/nyc_executives/overthinking/HOOK/CANONICAL.txt": (
        "Catherine is in her car parked outside the office an hour after the meeting ended, hands on "
        "the wheel, replaying the VP's silence at slide four — a new interpretation every thirty seconds."
    ),
    "atoms/nyc_executives/self_worth/HOOK/CANONICAL.txt": (
        "Marcus is loosening his tie in an empty corner office at 8 PM, title on the door, chest hollow "
        "— the role used to feel like it meant something and now he knows it is a costume."
    ),
    "atoms/nyc_executives/sleep_anxiety/HOOK/CANONICAL.txt": (
        "Marcus is awake at 3 AM in the penthouse bedroom, eyes open to the ceiling, term sheet pages "
        "running in his head — not worry exactly, but a body that has not been told the deal is over."
    ),
    "atoms/nyc_executives/somatic_healing/HOOK/CANONICAL.txt": (
        "Catherine is on the massage table on Saturday afternoon, therapist's hands on her lower back — "
        "by Tuesday morning commute her body has reloaded the tension as if the appointment never happened."
    ),
}


def update_tagging_tsv() -> None:
    rows: list[dict[str, str]] = []
    with TSV.open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        fieldnames = reader.fieldnames or []
        for row in reader:
            if row["rewrite_priority"] == "P2" and row["atom_path"] in REWRITES:
                row["classification"] = "SCENE_FIRST"
                row["first_paragraph_excerpt"] = REWRITES[row["atom_path"]][:200]
            rows.append(row)
    with TSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def apply_atoms() -> None:
    for rel, para1 in REWRITES.items():
        path = REPO / rel
        text = path.read_text(encoding="utf-8")
        path.write_text(replace_v01(text, para1), encoding="utf-8")
        print(f"updated {rel}")


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--tsv-only":
        update_tagging_tsv()
        return 0
    apply_atoms()
    update_tagging_tsv()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
