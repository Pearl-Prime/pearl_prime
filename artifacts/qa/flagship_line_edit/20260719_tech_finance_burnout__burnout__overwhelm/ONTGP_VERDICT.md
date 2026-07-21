# ONTGP Verdict — tech_finance_burnout × burnout × overwhelm

**Date:** 2026-07-19 (Pearl_Editor lane 03)
**Reader:** Pearl_Editor (agent, ONTGP proxy — full read of Ch1, Ch5, Ch12)

## L1 — fresh chord render attempt (this lane, live)

```
PYTHONPATH=. python3 scripts/run_pipeline.py --pipeline-mode spine --quality-profile production \
  --exercise-journeys --persona tech_finance_burnout --topic burnout \
  --arc config/source_of_truth/master_arcs/tech_finance_burnout__burnout__overwhelm__F006.yaml \
  --locale en-US --render-book --render-dir artifacts/qa/perfect_books_wave2_20260718/lane03/renders/tech_finance_burnout__burnout__overwhelm
```

**Result: `SystemExit(1)`, EXIT_CODE=1, 106 foreign-persona registry drops**
(`persona_id='tech_finance_burnout'`, `section_persona='Gen Z'`) — confirms Lane 02's
catalog-wide G-DEF4 finding independently, live, this lane, this run. Full log:
`artifacts/qa/perfect_books_wave2_20260718/lane03/renders/tech_finance_burnout__burnout__overwhelm_run.log`.
No `book.txt` written (hard-stop precedes compose). Per dispatcher ruling, falling
through to the best available prior manuscript for the ONTGP read below; no retry, no
registry/composer edit (banned lever).

## L2 — ONTGP read (real read, quoted evidence)

Sampled: Ch1, Ch5, Ch12 (last) of `artifacts/pilots/frame_v2_specimen_somatic_burnout/book.txt`
— the **best available** book.txt for this exact persona×topic pairing found in the
repo (see `RENDER_REF.txt` for the search). **Important honesty note:** unlike the
corporate_managers cell's reference, this file has no `book_quality_report.json` /
`book_pass_report.json` proving a Layer-1 PASS chord run — it is a `pilots/frame_v2_specimen`
draft, and the read below shows why: it does not read as production-quality prose.

### Chapter 1 — "This Is Not Tiredness"

| Dimension | Verdict | Evidence |
|---|---|---|
| Orient | FAIL | Opens abstractly, not on scene: *"Burnout as a systems failure, which you understand intellectually and cannot seem to address operationally."* (L4) — a thesis statement, not a body/scene anchor, in the first sentence. |
| Name | WEAK | Mechanism gestured at ("systems failure," "cascading failures") but never actually named/explained the way corporate_managers Ch1 names the stress-response mechanism. |
| Turn | FAIL | No felt pivot — the chapter is a flat list of restated variations on the same idea (see seam evidence below) rather than a scene with a turn. |
| Give | WEAK | *"Take one situation that usually triggers you... pause for three breaths before responding."* (L18–21) — a tool exists, but it is templated instruction, not grounded in the chapter's own scene. |
| Pull | FAIL | Chapter ends mid-scene with no integration: *"The doors open. Cold air moves through. The doors close again in your phone."* (L25) — "in your phone" is a broken clause (a door does not close "in your phone"), and nothing pulls toward Ch2. |
| **Seam visibility** | **FAIL** | The literal phrase **"soft daylight along the sill"** is repeated verbatim as an ambient-detail filler across multiple, unrelated scenes in this single chapter (office at 8 PM, kitchen, train) — including once with no antecedent noun at all: *"The office on the street below at 8 PM. soft daylight along the sill."* (L12). A single 900-word run-on block of "---"-separated micro-sentences (L23) is also visible raw template scaffolding, not prose. |

### Chapter 5 — "Doing More to Feel Less Useless"

| Dimension | Verdict | Evidence |
|---|---|---|
| Orient | FAIL | *"The metrics all showed warning signs. You track everything—sleep, output, focus."* (L156) — abstract restatement of Ch1's opening claim, not a new scene. |
| Name | WEAK | Same gestural mechanism language as Ch1, no new depth. |
| Turn | WEAK | The named-character micro-vignettes (*"She sat in the sprint for the third time that week..."*, L189) have real narrative texture, but they are compressed into one undifferentiated "---"-joined paragraph rather than landing as a scene. |
| Give | PASS | *"Place your hands on the sides of your ribcage. Feel your ribs expand with each inhale..."* (L168) — a genuine, concrete practice. |
| Pull | FAIL | Ends on a raw, unrendered data structure: *"{'intro': "You've been doing inner work—reading, recognizing, feeling. ...* (L191) — a Python dict literal is printed directly into the book text. This is not a seam, it is a hard rendering defect. |
| **Seam visibility** | **FAIL** | *"On the the train home"* (L158, duplicated article — "the the"); *"soft daylight along the sill"* repeats again (L158); the same broken filler pattern from Ch1 recurs. |

### Chapter 12 — "Rebuilding From the Inside" (last)

| Dimension | Verdict | Evidence |
|---|---|---|
| Orient | FAIL | *"Burnout as a systems problem means you can't fix it with individual interventions."* (L463) — abstract thesis restatement for the third sampled chapter running, not a scene. |
| Name | FAIL | No new mechanism named; recycles the same "systems failure" framing verbatim from Ch1 and Ch5. |
| Turn | FAIL | No felt pivot found in the sampled text. |
| Give | WEAK | *"Sit quietly for five minutes. Do nothing. Fix nothing. Change nothing."* (L479) — a real instruction, but generic, not tied to anything specific this book established. |
| Pull (integration) | FAIL | Ends mid-instruction with no sense of the book closing: *"Breathe once, write what you notice, and name what it is costing you today."* (L484) — a fine sentence in isolation, but there is no whole-book landing. |
| **Seam visibility** | **FAIL** | *"Your apartment at 11 PM. soft daylight along the sill."* (L465) — **factually incoherent**: daylight at 11 PM. *"Your apartment on soft daylight along the sill."* (L477) — ungrammatical ("on soft daylight"). The exact same broken filler phrase, unfit for its context every single time, appears in all 3 sampled chapters. |

## Overall verdict: **FAIL**

This is the weakest of the 3 cells, honestly. It fails on nearly every dimension in
all 3 sampled chapters, plus a literal unrendered Python dict printed into chapter 5
and a factual/grammatical error (daylight at 11 PM) repeated across the book. This is
not a WEAK read padded into a FAIL for effect — it is a genuine, low-quality specimen
draft, not a flagship candidate as-is. **Do not treat this as `system working`.**

## L3 — Fix applied (atom rewrite, not composer; scoped to what's actually fixable)

The chapter-level defects above (raw dict literal, "soft daylight along the sill"
filler, "the the" typo) live in **renderer-level ambient-detail template config**
(`config/rendering/environment_fallback_families.yaml`) and enrichment-per-section
scaffolding — **not** in this cell's own `atoms/tech_finance_burnout/**` bank, and
they are **catalog-wide shared infrastructure**, not scoped to this cell alone (the
same broken family entries were confirmed feeding the healthcare_rns manuscript too —
see that cell's verdict). Editing shared renderer config is out of this lane's
`atoms/**`-scoped write scope and carries golden-drift risk (see `NOTES.md` for the
full analysis and why it was **not** touched here). **Documented, not fixed** —
recommended as a dedicated Pearl_Dev-owned fix, same discipline as Lane 02's C4 item.

What *was* fixed, in scope: this cell's own `STORY` bank
(`atoms/tech_finance_burnout/burnout/STORY/CANONICAL.txt`) carried the identical
leaked-batch-generation-metadata defect found in the corporate_managers cell (10
entries, v21–v30) — rewritten; see `NOTES.md`.

## L4 — Promoted

Atom fix landed directly in `atoms/tech_finance_burnout/burnout/STORY/CANONICAL.txt`.
