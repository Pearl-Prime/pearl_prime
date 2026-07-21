# Seam notes — corporate_managers × burnout × overwhelm

## Fixed: leaked batch-generation metadata in STORY atoms (7 entries, v24–v30)

File: `atoms/corporate_managers/burnout/STORY/CANONICAL.txt`

All 7 entries shared one defect signature: a bolted-on trailing sentence of the shape
`In the <detail>, <Name> names the burnout pattern as an lived scene without turning
it into a verdict. Wave2-<NNN> keeps this body cell-specific.` — this is internal
generation/QA bookkeeping text that leaked into production prose, with a grammar
error (`as an lived scene`) baked in on every instance, plus upstream noun-swap
corruption in several bodies (`opened the stakeholders`, `the scanning wasn't shared`,
`the alarm without threat`, `standing in the direct reports`) that no longer parses as
English.

Fix method: rewrote each atom's body to a clean, grammatical, single-register
character-study paragraph, preserving the named character, `MECHANISM_DEPTH` /
`IDENTITY_STAGE` / `COST_TYPE` / `COST_INTENSITY` metadata, and the corporate-manager
scene grounding (1:1 calendar block, headcount spreadsheet, escalation ticket, OKR
review deck, open-plan desk, skip-level note, hiring-loop debrief) — no composer/topology
touched, no metadata schema changed, pure prose-level seam repair.

Example (v24, before → after):

> Before: "Nolan notices the shift. Marcus told himself the scanning was just how it
> worked. Everyone nearby seemed to carry it. But that Tuesday, when the stakeholders
> landed and his hands went cold before he'd read the first line, he understood: the
> scanning wasn't shared. It was his. It had always been his. In the 1:1 calendar
> block, Nolan names the burnout pattern as an lived scene without turning it into a
> verdict. Wave2-001 keeps this body cell-specific."

> After: "Nolan notices the shift, watching himself do it from a small distance. He
> used to tell himself the vigilance was just how the job worked — everyone on his
> level stayed on alert, so it didn't count as a problem. But that Tuesday, in the
> middle of a routine 1:1, his hands went cold before the calendar even loaded the next
> meeting, and he understood: the vigilance wasn't shared. It had never been shared.
> It was his, and it had been running since before this role even started."

## Documented, not fixed: catalog-wide scope of the same defect

`grep -rl "Wave2-\|as an lived scene" atoms/` returns hundreds of files across nearly
every persona/topic bank in the catalog (e.g. `working_parents/*`, `nyc_executives/*`,
`millennial_women_professionals/*`, and more) — this is a systemic batch-authoring
defect, not scoped to burnout or to these 3 cells. Fixing it catalog-wide is out of
this lane's write scope (`atoms/**` edits are restricted to the 3 designated cells) and
out of its time budget. Recommend a dedicated future bank-hygiene lane, same pattern as
Lane 02's C4 recommendation.

## Documented, not fixed: duplicate-atom cross-chapter selection

The `STORY v19` ("Louisa") atom in this same bank is selected twice in the sampled
manuscript (Ch2 and Ch12, verbatim). The atom text itself is clean; the defect is in
*which chapter selects which atom* — a depth/enrichment selection behavior, not a
bank-content defect. Fixing selection logic is composer-adjacent and banned for this
lane. Flagged for the owning lane (Pearl_Dev, per the ONTGP routing table in
`docs/PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md`: "Turn FAIL → beat structure in
chapter_script or enrichment (Pearl_Dev + Pearl_Architect)").
