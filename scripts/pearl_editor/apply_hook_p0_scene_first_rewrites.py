#!/usr/bin/env python3
"""Apply HOOK v01 scene-first rewrites for P0 batch (ws_pearl_editor_hook_p0_rewrite_batch_20260527)."""
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


# scene-first v01 paragraph 1 only; prior v01 text becomes paragraph 2 when not a placeholder
REWRITES: dict[str, str] = {
    "atoms/corporate_managers/boundaries/HOOK/CANONICAL.txt": (
        "Marcus is sitting on the edge of his bed at 11:47 PM, phone warm in his palm, "
        "thumbs hovering over a Slack thread from his direct report — he already knows he "
        "will answer before he finishes reading."
    ),
    "atoms/corporate_managers/compassion_fatigue/HOOK/CANONICAL.txt": (
        "Elena closes her laptop in the home office at 9:15 PM, shoulders still braced from "
        "the 1:1 where her direct report cried about the divorce — she held space at work and "
        "now her chest has no room left for herself."
    ),
    "atoms/corporate_managers/depression/HOOK/CANONICAL.txt": (
        "James stands in his new corner office on Monday morning, hands flat on the desk, "
        "staring at the promotion email on the monitor — his chest feels hollow where pride "
        "was supposed to land."
    ),
    "atoms/entrepreneurs/boundaries/HOOK/CANONICAL.txt": (
        "You're standing at the kitchen counter at 10:06 PM, phone already lit with the "
        "client's text, thumb moving toward reply before you decide whether tonight counts "
        "as yours."
    ),
    "atoms/entrepreneurs/burnout/HOOK/CANONICAL.txt": (
        "Somewhere past midnight you're still at the laptop in the home office, shoulders "
        "locked toward your ears, refreshing the dashboard because stopping feels like "
        "letting the business die."
    ),
    "atoms/entrepreneurs/imposter_syndrome/HOOK/CANONICAL.txt": (
        "You're sitting in the investor debrief room after the term sheet signed, smiling on "
        "cue, palms damp against your notebook — waiting for someone to say the win was luck."
    ),
    "atoms/entrepreneurs/overthinking/HOOK/CANONICAL.txt": (
        "You're at the kitchen table at 2:11 AM, laptop open on a decision you already made, "
        "jaw tight — replaying the pitch deck slide not for strategy but for proof you are "
        "allowed to exist."
    ),
    "atoms/entrepreneurs/sleep_anxiety/HOOK/CANONICAL.txt": (
        "You're lying awake at 3:04 AM in bed, phone face-down on the nightstand buzzing with "
        "a vendor alert you cannot ignore, eyes open because the business is on-call in your "
        "nervous system."
    ),
    "atoms/entrepreneurs/social_anxiety/HOOK/CANONICAL.txt": (
        "You're in the lobby of the industry conference, badge printed, coffee cup warming your "
        "hands, rehearsing the opener in your throat before you walk into a room full of people "
        "you are supposed to network with."
    ),
    "atoms/first_responders/financial_stress/HOOK/CANONICAL.txt": (
        "Marcus is at the kitchen table after night shift, uniform still on, hunched over the "
        "insurance bill with a calculator — the pay on the stub has not moved in two years and "
        "his jaw is clenched before the math finishes."
    ),
    "atoms/first_responders/imposter_syndrome/HOOK/CANONICAL.txt": (
        "Sofia is at her daughter's school pickup line in plain clothes, waving to other parents, "
        "hands still steadier on a scene than in small talk — she has carried people out of wreckage "
        "and cannot find the same footing here."
    ),
    "atoms/gen_alpha_students/courage/HOOK/CANONICAL.txt": (
        "You're sitting in the cafeteria at lunch, tray untouched, chest tight while everyone laughs "
        "at someone across the table — your mouth is open a fraction, about to say the thing that "
        "could cost you."
    ),
    "atoms/gen_alpha_students/financial_anxiety/HOOK/CANONICAL.txt": (
        "Jordan is in the school hallway between classes, phone in hand, stomach dropping at the "
        "group chat about the trip — the family account balance is visible in the banking app and "
        "the number does not clear the deposit."
    ),
    "atoms/gen_alpha_students/grief/HOOK/CANONICAL.txt": (
        "You're on your bedroom floor at 6 PM, knees pulled in, hands pressed to the empty dog bed "
        "where they used to sleep — your chest is tight and nobody at school treated the loss like "
        "it counted."
    ),
    "atoms/gen_x_sandwich/burnout/HOOK/CANONICAL.txt": (
        "Patricia is in her mother's kitchen at 7 AM, one hand on the walker, the other scrolling "
        "her work email — she has not finished the grocery order for her kids and her shoulders are "
        "already at her ears before the day has started."
    ),
    "atoms/gen_z_professionals/anxiety/HOOK/CANONICAL.txt": (
        "You're in your apartment at 10 PM, laptop closed but chest still loud, replaying whether the "
        "standup comment landed wrong — you did everything they told you to do and your body has not "
        "gotten the memo."
    ),
    "atoms/gen_z_professionals/burnout/HOOK/CANONICAL.txt": (
        "Amari is still at the desk at 11:30 PM on a Thursday, Slack workspace glowing, shoulders "
        "braced — the sprint ended but her body is running another week inside the same posture."
    ),
    "atoms/gen_z_professionals/financial_anxiety/HOOK/CANONICAL.txt": (
        "You're at the kitchen counter on payday, banking app open, thumb frozen on the rent line — "
        "$2,100 due against a salary that never quite clears the math after groceries and the student "
        "loan."
    ),
    "atoms/gen_z_professionals/imposter_syndrome/HOOK/CANONICAL.txt": (
        "You're in the Zoom gallery on your third month, camera on, nodding while a director praises "
        "the deck — your throat is tight because part of you is still waiting for them to notice the "
        "file was a mistake."
    ),
    "atoms/gen_z_professionals/overthinking/HOOK/CANONICAL.txt": (
        "You're on the subway at 8 AM, headphones in, jaw locked, scrolling workplace threads about "
        "layoffs and ethics — you keep running the same contradiction between what you know and what "
        "you participate in."
    ),
    "atoms/gen_z_professionals/social_anxiety/HOOK/CANONICAL.txt": (
        "You're filming a story update in your bathroom mirror at 9 PM, filter on, caption half-written "
        "about your career anxiety — your shoulders are raised and you already know posting it will not "
        "make the feeling smaller."
    ),
    "atoms/gen_z_student/overthinking/HOOK/CANONICAL.txt": (
        "She typed \"sounds good\" and deleted it. Typed it again. Deleted it again. Her thumbs locked "
        "mid-air over the screen, pulse climbing into her jaw. Three dots appeared on his side. Vanished. "
        "The hallway crowd pushed past her standing still between second and third period."
    ),
    "atoms/healthcare_rns/compassion_fatigue/HOOK/CANONICAL.txt": (
        "You're in Room 412 at 2 AM, gloved hands steady on the rails, voice soft for the crying patient "
        "— your chest stays perfectly flat while the right words leave your mouth."
    ),
    "atoms/healthcare_rns/depression/HOOK/CANONICAL.txt": (
        "You're in the driver's seat of your car at 7 AM after night shift, hands on the wheel, world gray "
        "through the windshield — eight hours of sleep will not touch what sits behind your ribs."
    ),
    "atoms/healthcare_rns/financial_stress/HOOK/CANONICAL.txt": (
        "You're at the kitchen table in scrubs still damp from shift, calculator and pay stub spread out — "
        "your chest tightens on the rent-to-salary ratio that has not moved since you became an RN."
    ),
    "atoms/midlife_women/boundaries/HOOK/CANONICAL.txt": (
        "Diane is in the driver's seat at 7:52 AM, phone buzzing with her mother's eighth call this week, "
        "thumb hovering over answer — she has a 9 AM meeting and her shoulders are already braced for forty "
        "more minutes."
    ),
    "atoms/midlife_women/burnout/HOOK/CANONICAL.txt": (
        "Diane is at the kitchen table on Sunday night, planner open, pen still in her hand without moving — "
        "she scheduled her mother's cardiologist, her son's IEP, her mammogram, and the quarterly review in "
        "one week and called that normal."
    ),
    "atoms/midlife_women/overthinking/HOOK/CANONICAL.txt": (
        "Diane is awake at 4 AM in bed, eyes open to the ceiling, fingers worrying the edge of the blanket — "
        "she has been planning contingencies so long she cannot tell strategy from anxiety hunting for a "
        "container."
    ),
    "atoms/midlife_women/social_anxiety/HOOK/CANONICAL.txt": (
        "Diane sits in her car in the party parking lot for ten minutes, hands on the wheel, engine off — "
        "she used to work any room and now her throat closes before she opens the door."
    ),
    "atoms/millennial_women_professionals/boundaries/HOOK/CANONICAL.txt": (
        "You're in your manager's doorway at 4 PM, notebook against your chest, throat tightening as you say "
        "yes to the weekend ask — you already know the cost before the words finish leaving your mouth."
    ),
    "atoms/millennial_women_professionals/burnout/HOOK/CANONICAL.txt": (
        "You're at the dining table at 12:18 AM, laptop open, shoulders hunched toward the screen, typing "
        "another reply because nobody else will — you have told yourself this is what reliable looks like."
    ),
    "atoms/millennial_women_professionals/imposter_syndrome/HOOK/CANONICAL.txt": (
        "You're in the team Slack thread after the launch shipped, cursor blinking in the congratulations "
        "channel — you accomplished something real and your stomach is busy finding the sentence where luck "
        "explains it."
    ),
    "atoms/millennial_women_professionals/overthinking/HOOK/CANONICAL.txt": (
        "You're awake at 2:06 AM in bed, eyes shut, jaw clenched, replaying the 47 seconds in yesterday's "
        "meeting — maybe too direct, maybe not direct enough — in full detail on a loop your body cannot stop."
    ),
    "atoms/millennial_women_professionals/self_worth/HOOK/CANONICAL.txt": (
        "You're at your desk at 3 PM, hands frozen above the keyboard, panic rising because output stopped — "
        "you have built a life where you only feel real when something measurable is leaving your fingers."
    ),
    "atoms/millennial_women_professionals/sleep_anxiety/HOOK/CANONICAL.txt": (
        "You're lying in bed at 2 AM, body heavy, eyes open, thumbs pressed into the sheet while tomorrow's "
        "meeting runs in your head — you know rehearsing worst cases is not preparation and you do it anyway."
    ),
    "atoms/millennial_women_professionals/social_anxiety/HOOK/CANONICAL.txt": (
        "You're standing outside the conference room glass at 8:58 AM, badge in hand, chest tight — your body "
        "is already drafting every way you might say the wrong thing before you touch the door."
    ),
    "atoms/tech_finance_burnout/sleep_anxiety/HOOK/CANONICAL.txt": (
        "You're in bed at 1:47 AM, smartwatch glowing on the nightstand, lying on your back with eyes open — "
        "you've diagrammed the sleep failure seventeen times and understanding has not turned the protocol off."
    ),
    "atoms/tech_finance_burnout/somatic_healing/HOOK/CANONICAL.txt": (
        "You're at your standing desk on Tuesday morning, shoulders pinned near your ears, trying to roll them "
        "down — they rise again before the standup starts because straight has started to feel wrong."
    ),
    "atoms/working_parents/boundaries/HOOK/CANONICAL.txt": (
        "You're on the nursery floor at 8:30 PM, toddler climbing your back, work phone buzzing in your pocket "
        "— you answer before you decide because saying no does not feel available tonight."
    ),
    "atoms/working_parents/compassion_fatigue/HOOK/CANONICAL.txt": (
        "You're loading the dishwasher at 9 PM, back aching, still wearing the smile you gave your child at "
        "homework time — you gave to your partner and your mother and your boss today and your chest is empty."
    ),
    "atoms/working_parents/somatic_healing/HOOK/CANONICAL.txt": (
        "You're sitting on the edge of the bathtub after the kids are down, shoulders still at your ears, "
        "rolling your neck once — the tension has been there so long you forgot your body was making a choice."
    ),
}


def update_tagging_tsv() -> None:
    rows: list[dict[str, str]] = []
    with TSV.open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        fieldnames = reader.fieldnames or []
        for row in reader:
            if row["rewrite_priority"] == "P0" and row["atom_path"] in REWRITES:
                row["classification"] = "SCENE_FIRST"
                row["first_paragraph_excerpt"] = REWRITES[row["atom_path"]][:200]
            rows.append(row)
    with TSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def apply_atoms() -> None:
    skip_move = {"atoms/gen_z_student/overthinking/HOOK/CANONICAL.txt"}
    for rel, para1 in REWRITES.items():
        path = REPO / rel
        text = path.read_text(encoding="utf-8")
        path.write_text(
            replace_v01(text, para1, move_old_to_para2=rel not in skip_move),
            encoding="utf-8",
        )
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
