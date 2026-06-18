#!/usr/bin/env python3
"""Tier-1 authored chapter script PAIR for devotion_en_01 · ch_1 (Open Vessel Press).

Genre register (LOCKED): HEALING / IYASHIKEI / devotional-emotional-drama —
grief tended, compassion returned, courage as inner work. NOT battle.

REAL prose authored by Tier-1 Claude (Pearl_Prime, operator-present) — NOT the
deterministic stub, NOT a paid API. Renders the merged iyashikei story engine's
"First Light" beats (the visiting-presence / hardness-softened-by-witnessing arc;
hook family loss_echo) into a chapter that clears the BLOCKING bestseller gate
(phoenix_v4/manga/qc/bestseller_gate.py) under the devotion_path healing profile:

  * substance: >= 6 panels / >= 2 pages, no stub markers, no verbatim repeats,
    unique-ratio >= 0.5, final panel lands a loss_echo hook
  * healing register: NO emotional labeling, NO cliffhanger, NO threat language
  * craft gates (promoted to BLOCKER): hook=loss_echo, silent_panel_ratio≈0.40
    (±0.15), words-per-page≈32 (±30% → 22–42), restraint (show > tell, josei),
    yearning (no premature resolution)

Output: chapter_script_authored.json — the {chapter_script_writer_handoff,
chapter_script_internal_record} pair the runner installs via ReplayLLMClient
(_install_authored_script) when writer_mode='claude'.

Cast (config/source_of_truth/manga_profiles/series/devotion_en_0{1,2}.yaml):
  Amara  — Amara Okafor, hospice care-nurse; efficient with people, distant from
           them; the chapter receives her into a deeper baseline (the engine's
           "Asa": sets out the second cup, then remembers).
  Sai Ma — the elder teacher-guide; the visiting devotional presence who lets the
           silence sit and does not fix (the engine's "Ren").

  PYTHONPATH=. python3 scripts/manga/author_devotion_en_01_ch1.py \
      --workspace artifacts/manga/devotion_en_01_run
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

# Each panel: action (renderer direction, also counts as SHOW), camera, mood,
# and optional dialogue/caption. caption is reader-facing (counts toward WPP and
# restraint exposition — kept observational, never emotional labeling). Silence
# panels carry no reader-facing text (panel_type 'silent'); they are ~40% of
# panels for the iyashikei breath. Moods move calm→neutral→tense→hopeful so the
# chapter lands an emotional turn without ever naming a feeling.
PAGES = [
    # P1 — weather hook + locate Amara mid-habit (beats 0–1)
    {"page_number": 1, "page_type": "splash", "panels": [
        {"camera": "establishing-wide", "mood": "calm",
         "action": "Dawn over the hospice garden. Mist on the wet gravel; the cicadas already gone for the season. No people yet — just the world, breathing.",
         "caption": "First cold of the year. The eaves dripping where the rain had been."},
        {"camera": "medium", "mood": "neutral",
         "action": "Amara moves down the ward corridor mid-habit — squaring a blanket, refilling a jug, sweeping the threshold. Her hands move before the mind wakes; we learn who she is by what they do."},
    ]},
    # P2 — the small wrongness: the second cup (beat 2)
    {"page_number": 2, "page_type": "standard", "panels": [
        {"camera": "insert", "mood": "neutral",
         "action": "Close on the tea tray in the break room: Amara sets out two cups from old habit. Her hand stops over the second one.",
         "caption": "Two cups. The way it had always been done, long after there was only one to drink."},
        {"camera": "close-up", "mood": "tense",
         "action": "She remembers, and puts the second cup back on the shelf. The empty place on the tray keeps the shape of someone.",
         "caption": "She put it back on the shelf. The tray kept the shape of where it used to stand."},
        {"camera": "environmental-insert", "mood": "calm", "panel_type": "silent",
         "action": "A sparrow lands on the sill, considers the glass, and is gone. The tray sits with its one cup."},
    ]},
    # P3 — the disruption arrives like weather: the bedside, Sai Ma (beats 3)
    {"page_number": 3, "page_type": "standard", "panels": [
        {"camera": "over-shoulder", "mood": "tense",
         "action": "Room seven. A man keeps vigil at his wife's bedside, both his hands around hers, the monitor switched off. An elder, Sai Ma, sits unmoving in the far corner, sandalwood beads at her wrist.",
         "caption": "The kind of quiet that has already happened."},
        {"camera": "close-up", "mood": "tense",
         "action": "Amara's old instinct surfaces — assess, offer a line of comfort, set the next task moving. Her mouth opens.",
         "dialogue": [{"character": "Amara", "text": "Is there someone I can call for you? Anyone at all?"}]},
        {"camera": "medium", "mood": "dark",
         "action": "The man does not look up from his wife's face. He answers from somewhere far down, without heat, asking for nothing.",
         "dialogue": [{"character": "Tomas", "text": "No one to call. I only don't want to let go of her hand yet."}]},
    ]},
    # P4 — the armor of usefulness fails; Sai Ma lets the silence sit (beat 4)
    {"page_number": 4, "page_type": "standard", "panels": [
        {"camera": "close-up", "mood": "dark", "panel_type": "silent",
         "action": "The line runs out in Amara's throat. Nothing here to refill or square off. Her hand hovers, useless, near the chart at her hip."},
        {"camera": "medium", "mood": "neutral",
         "action": "From the corner, Sai Ma turns one bead slowly between thumb and finger and tips her head toward the empty chair on the near side of the bed. She does not rise to fix anything.",
         "dialogue": [{"character": "Sai Ma", "text": "You don't have to mend it. Sitting is also a thing two hands can do."}]},
    ]},
    # P5 — they do the ordinary thing together (beat 5)
    {"page_number": 5, "page_type": "standard", "panels": [
        {"camera": "close-up", "mood": "tense",
         "action": "Amara, low, the nearest she comes to honesty — she grips the chart, then sets it down on the windowsill, the first thing all morning she puts down unfinished.",
         "dialogue": [{"character": "Amara", "text": "And if sitting is all I can do?"}]},
        {"camera": "medium", "mood": "neutral",
         "action": "Sai Ma only smiles and pours water from the bedside jug into a paper cup, sliding it across to Tomas. An ordinary task; the being-beside is the point.",
         "dialogue": [{"character": "Sai Ma", "text": "Then we sit, and we keep the water near. That is the whole of it."}]},
        {"camera": "wide", "mood": "calm", "panel_type": "silent",
         "action": "Amara lowers herself into the empty chair. Three people and the morning light. The grief in the room loosens its grip a quarter-turn."},
    ]},
    # P6 — a wordless stretch: she stops performing okayness (beat 6)
    {"page_number": 6, "page_type": "silent", "panels": [
        {"camera": "environmental-insert", "mood": "calm", "panel_type": "silent",
         "action": "Wind in the eaves. Steam off the paper cup. A leaf on the sill deciding which way to fall."},
        {"camera": "close-up", "mood": "calm", "panel_type": "silent",
         "action": "Amara's shoulders come down from where they have lived for years. She stops performing okayness and simply is, beside another person and the weather."},
        {"camera": "wide", "mood": "calm", "panel_type": "silent",
         "action": "The three of them in the climbing light, no one speaking, the dust turning slowly between them."},
    ]},
    # P7 — Amara says one true thing; Sai Ma does not fix it (beat 7)
    {"page_number": 7, "page_type": "standard", "panels": [
        {"camera": "close-up", "mood": "neutral",
         "action": "Amara looks at her own steady hands — the hands so good at doing — and says one small true thing, halting, the size that fits in a single breath.",
         "dialogue": [{"character": "Amara", "text": "I keep setting out the second cup. Every morning. Then I remember."}]},
        {"camera": "medium", "mood": "hopeful",
         "action": "Sai Ma does not reach to fix it. She tells one bead, and nods, holding the space open for the small confession to simply exist.",
         "dialogue": [{"character": "Sai Ma", "text": "The hand remembers who it loved. Let it. That is not a thing to correct."}]},
    ]},
    # P8 — Sai Ma leaves like weather; something settles (beat 8)
    {"page_number": 8, "page_type": "standard", "panels": [
        {"camera": "medium", "mood": "hopeful",
         "action": "Later. Sai Ma gathers her shawl and leaves the way weather leaves, without ceremony — a hand briefly on Amara's shoulder at the door. Tomas has fallen asleep in the chair, his wife's hand still in his.",
         "dialogue": [{"character": "Sai Ma", "text": "You stayed. He was not alone for it. Neither were you."}]},
        {"camera": "wide", "mood": "calm",
         "action": "Amara alone in the doorway of room seven. The light on the wall has changed. Nothing is resolved. Something has settled.",
         "caption": "The light on the wall had moved. Nothing was fixed. Something, all the same, had settled."},
    ]},
    # P9 — return to baseline one degree deeper; loss_echo close (beat 9)
    {"page_number": 9, "page_type": "standard", "panels": [
        {"camera": "medium", "mood": "hopeful",
         "action": "Next dawn. The break room. Amara reaches for the tray and sets out one cup — on purpose this time, not from forgetting — and rests her palm a moment on the shelf where the second used to stand.",
         "caption": "One cup, set down on purpose. The second place still there, just quieter now."},
        {"camera": "environmental-insert", "mood": "calm", "panel_type": "silent",
         "action": "Final panel: on the bare branch outside the glass, a single white plum blossom has opened. Amara, small in frame, noticing it for the first time though she has passed it all winter. The season turns a degree. The reader exhales."},
    ]},
]


def _pid(page_no: int, idx: int) -> str:
    return f"p_{page_no}_{idx}"


def _panel(page_no: int, idx: int, p: dict, *, internal: bool) -> dict:
    out: dict = {
        "panel_id": _pid(page_no, idx),
        "action": p["action"],
        "camera": p["camera"],
        "mood": p["mood"],
        "dialogue": p.get("dialogue", []),
    }
    if p.get("caption"):
        out["caption"] = p["caption"]
    if p.get("panel_type"):
        out["panel_type"] = p["panel_type"]
    if internal:
        out["is_carrier_beat"] = bool(p.get("caption") or p.get("panel_type") == "silent")
    return out


def _pages(internal: bool) -> list[dict]:
    return [
        {"page_number": pg["page_number"], "page_type": pg["page_type"],
         "panels": [_panel(pg["page_number"], i, p, internal=internal) for i, p in enumerate(pg["panels"])]}
        for pg in PAGES
    ]


def build_pair() -> dict:
    """Return the {writer_handoff, internal_record} pair the ReplayLLMClient reads."""
    common = {"series_id": "devotion_en_01", "chapter_id": "ch_1", "chapter_end_hook": "loss_echo"}
    return {
        "chapter_script_writer_handoff": {
            "schema_version": "1.0.0",
            "artifact_type": "chapter_script_writer_handoff",
            **common,
            "pages": _pages(internal=False),
        },
        "chapter_script_internal_record": {
            "schema_version": "1.0.0",
            "artifact_type": "chapter_script_internal_record",
            "script_provenance": "claude_tier1",
            **common,
            "pages": _pages(internal=True),
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Author devotion_en_01 ch_1 (Tier-1 iyashikei pair).")
    ap.add_argument("--workspace", type=Path, required=True)
    args = ap.parse_args()
    ws = args.workspace.resolve()
    ws.mkdir(parents=True, exist_ok=True)

    pair = build_pair()
    out = ws / "chapter_script_authored.json"
    out.write_text(json.dumps(pair, indent=2) + "\n", encoding="utf-8")

    wh = pair["chapter_script_writer_handoff"]
    n_pages = len(wh["pages"])
    n_panels = sum(len(p["panels"]) for p in wh["pages"])
    n_silent = sum(1 for p in wh["pages"] for pn in p["panels"] if pn.get("panel_type") == "silent")
    print(f"Wrote {out} — {n_pages} pages, {n_panels} panels, {n_silent} silent ({n_silent/n_panels:.0%})")

    # Self-report against the real gate (profile-resolved).
    from phoenix_v4.manga.qc.bestseller_gate import evaluate_bestseller_gate
    from phoenix_v4.manga.runner.chapter_runner import _resolve_manga_profile

    prof = _resolve_manga_profile(ws, brand_id="devotion_path", genre_id="healing")
    verdict = evaluate_bestseller_gate(wh, prof)
    print(f"Bestseller gate verdict: {verdict['clearance']} (profile={'resolved' if prof else 'none'})")
    for b in verdict.get("blockers", []):
        print(f"  [BLOCKER] {b.get('gate_id')}: {str(b.get('description'))[:110]}")
    return 0 if verdict["clearance"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
