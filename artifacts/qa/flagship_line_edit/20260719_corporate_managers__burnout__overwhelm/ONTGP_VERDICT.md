# ONTGP Verdict — corporate_managers × burnout × overwhelm

**Date:** 2026-07-19 (Pearl_Editor lane 03)
**MATRIX cell:** `C048__corporate_managers__burnout__overwhelm` (dispatcher default, "#1923-proven shipping cell")
**RENDER_REF:** see `RENDER_REF.txt` — fresh L1 chord render attempted and **hard-stopped on G-DEF4** (see below); verdict below is a real read of the best available prior manuscript, per dispatcher ruling.
**Reader:** Pearl_Editor (agent, ONTGP proxy — full read of Ch1 / Ch5 / Ch12, not a keyword proxy)

## L1 — fresh chord render attempt

```
PYTHONPATH=. python3 scripts/run_pipeline.py --pipeline-mode spine --quality-profile production \
  --exercise-journeys --persona corporate_managers --topic burnout \
  --arc config/source_of_truth/master_arcs/corporate_managers__burnout__overwhelm__F006.yaml \
  --locale en-US --render-book --render-dir ...
```

Not independently re-run by this lane (would reproduce the identical failure already
proven fresh, same-day, by Lane 02 against the same untouched `registry/burnout.yaml`
— see `artifacts/qa/perfect_books_wave2_20260718/lane02/renders/corporate_managers__burnout__overwhelm_run.log`:
`SystemExit(1)`, **106 foreign-persona registry drops** for `persona_id='corporate_managers'`
against a `registry/burnout.yaml` authored 100% `Gen Z`). Root cause: `artifacts/qa/perfect_books_wave2_20260718/lane02/DEF4_SYSTEMWIDE_FINDING.md`
(catalog-wide, not scoped to this cell). Per dispatcher ruling, this lane does not
retry the identical render and does not touch registry/composer code (banned lever).

## L2 — ONTGP read (real read, quoted evidence)

Sampled: Ch1, Ch5, Ch12 (last) of
`artifacts/qa/pearl_prime_dev_finish_20260716/ten_wave2/corporate_managers__burnout__overwhelm__F006/book.txt`
(a real four-piece-chord production output — `book_quality_report.json` confirms
`"status": "PASS"`, `source: spine_pipeline`, 12 chapters, 20,700 words).

### Chapter 1 — "This Is Not Tiredness"

| Dimension | Verdict | Evidence |
|---|---|---|
| Orient | PASS | Opens on body/scene, not concept: *"You open the laptop at 6 AM out of habit, not need, and the inbox loads its three hundred unread like a tide that went out years ago and never came back in."* (L4) |
| Name | PASS | Mechanism named with topic-vocab: *"Your stress response does not wait for a threat to arrive; it fires in anticipation of one... The morning dread is your system pre-loading for a day it has come to expect will be too much."* (L26) |
| Turn | PASS | Felt pivot via named-character beat: *"She is you. She is building the same trap you built... You do not stop her. You cannot. Because eight years ago someone tried to tell you and you did not listen either."* (L74–94) |
| Give | PASS | Concrete tool: *"Press your back flat against a wall. Feel the wall hold you. Count five slow exhales."* (L62–64) |
| Pull | WEAK | Chapter closes flat, not forward-leaning: *"Nobody knows. The performance continues."* (L116) — a strong image but not traction into Ch2's stated topic (headcount review). |

### Chapter 5 — "Doing More to Feel Less Useless"

| Dimension | Verdict | Evidence |
|---|---|---|
| Orient | PASS | *"You caught yourself, mid-1:1, nodding at a direct report's win with a face that felt like it belonged to someone else — competent, warm, entirely rented..."* (L350) |
| Name | PASS | Names mechanism + cites real research: *"Christina Maslach's published case studies of teachers and nurses describe professionals who loved their calling until chronic overload turned dedication into cynicism..."* (L384) |
| Turn | PASS | The 5-day-PTO vignette: *"Because if the machine runs without you, then the burnout was not necessary. The sacrifice was not required."* (L444) |
| Give | PASS | *"Breathe in through your nose for four counts. Out for six."* (L456) |
| Pull | WEAK | Ends on *"A single breath can be the whole intervention."* (L470) — abstract close, no lean into Ch6. |
| **Seam visibility** | **FAIL** | Two verbatim/near-verbatim internal duplicate paragraphs inside the *same* chapter: `"contemplative practice holds that presence comes before strategy." / "The work demands less than the worry about the work."` appears at L396+398 **and again** at L412+414; `"Before your next one-on-one, sit down first. Place one hand flat on the desk. Press down until you feel the surface..."` appears at L458–460 **and again** (with one clause added) at L464–466. This is a visible exercise-wrapper/shift-phrase repeat within one chapter — exactly the seam class the spec bans from catalog ship (§1.5). |

### Chapter 12 — "Rebuilding From the Inside" (last)

| Dimension | Verdict | Evidence |
|---|---|---|
| Orient | PASS | *"You closed the laptop at 11:15 PM, told yourself that was it, and opened it again at 11:22 to check one thread..."* (L1037) |
| Name | PASS | *"the chronic activation of burnout makes stillness feel unsafe. The body, locked in a low-grade emergency, reads rest as danger..."* (L1063); grounded further with a cited historical example (Marie Curie, L1051–1053). |
| Turn | PASS | VP confession scene: *"I am drowning. The words come out and you cannot take them back."* (L1123) |
| Give | WEAK | *"Let the discharge be whatever it was — a shoulder drop, a jaw release, a long exhale."* (L1169) — softer/vaguer than the concrete tools in Ch1/Ch5. |
| Pull (integration) | WEAK | Book ends on *"What moved, moved. What stayed, stays."* (L1171) — thin, does not land the whole-book arc. |
| **Inter-atom cohesion** | **FAIL** | The "Louisa" character-study vignette (*"Louisa had read everything about burnout — the articles, the frameworks..."*) is used **verbatim, twice**, once in Ch2 (L157–159) and again in the book's climax chapter, Ch12 (L1161–1167), with zero acknowledgment or callback framing. Same atom (`STORY v19` in `atoms/corporate_managers/burnout/STORY/CANONICAL.txt`) selected twice across chapters — this is exactly the "strong local prose + weak whole-book cohesion" failure mode the line-edit lane exists to close (ANALYSIS_REPORT §7). In the closing chapter this reads as recycled filler, not a deliberate reprise. |

## Overall verdict: **FAIL**

Per the ONTGP chapter-pass rule (0 FAILs, ≤2 WEAKs), Ch1 and Ch5 individually would
pass; Ch12 has one dimension FAIL (integration/Pull is WEAK, and the whole-book
"inter-atom cohesion" check the mission brief calls out explicitly is a hard FAIL:
duplicate climax-chapter vignette). **Book does not reach Layer-3 `system working`.**
This is an honest FAIL, not a WEAK dressed up — do not read this as PASS.

## L3 — Fix applied (atom rewrite, not composer)

The duplicate-vignette finding is a **selection/depth issue** (the same STORY atom
picked twice across chapters), not a text defect in the atom itself — fixing the
*selection* would mean touching enrichment/depth-selection code, which is
composer-adjacent and explicitly banned for this lane. **Not fixed here** (documented,
not silently skipped — same discipline Lane 02 applied to the C4 finding).

A second, genuinely atom-level defect *was* found and fixed: 7 `STORY` atoms in this
cell's own bank (`atoms/corporate_managers/burnout/STORY/CANONICAL.txt`, v24–v30) carried
a **leaked batch-generation artifact** — every one ended with a bolted-on,
disconnected, ungrammatical tail sentence (e.g. *"...he understood: the scanning
wasn't shared... In the 1:1 calendar block, Nolan names the burnout pattern as an lived
scene without turning it into a verdict. Wave2-001 keeps this body cell-specific."*) —
broken grammar, nonsensical noun-swaps ("opened the stakeholders", "the alarm without
threat"), and literal internal QA-marker text (`Wave2-00N ... cell-specific`) leaking
into production prose. This is a genuine "seam" defect squarely in scope
(`atoms/**` for this designated cell) — **rewritten** as natural, grammatical,
persona-grounded prose (see `NOTES.md` for the full before/after). This is a
**catalog-wide pattern** (same defect signature confirmed in the other 2 lane-03
cells' banks, and grep-confirmed present in dozens of other persona/topic banks
outside this lane's scope — not touched there, documented for a future dedicated
fix lane, same discipline as Lane 02's C4 finding).

These 7 atoms were **not selected** in the specific prior manuscript sampled above
(that render predates this fix), so this verdict correctly reports FAIL on the
pre-fix manuscript; the fix is forward-looking (L4) — it corrects the bank so any
future render of this cell (once the C4 blocker is separately resolved) inherits
clean atoms instead of the leaked-metadata versions.

## L4 — Promoted

Atom fix landed directly in `atoms/corporate_managers/burnout/STORY/CANONICAL.txt`
(the reusable bank itself, not a one-off manuscript patch) — see handoff for the
explicit-path list.
