# ONTGP Verdict — healthcare_rns × burnout × overwhelm

**Date:** 2026-07-19 (Pearl_Editor lane 03)
**Reader:** Pearl_Editor (agent, ONTGP proxy — full read of Ch1, Ch5, Ch12)

## L1 — fresh chord render attempt (this lane, live)

```
PYTHONPATH=. python3 scripts/run_pipeline.py --pipeline-mode spine --quality-profile production \
  --exercise-journeys --persona healthcare_rns --topic burnout \
  --arc config/source_of_truth/master_arcs/healthcare_rns__burnout__overwhelm__F006.yaml \
  --locale en-US --render-book --render-dir artifacts/qa/perfect_books_wave2_20260718/lane03/renders/healthcare_rns__burnout__overwhelm
```

**Result: `SystemExit(1)`, EXIT_CODE=1, 106 foreign-persona registry drops**
(`persona_id='healthcare_rns'`, `section_persona='Gen Z'`) — confirms Lane 02's
inferred-but-not-independently-rendered prediction for this exact cell, live, this
run. Full log:
`artifacts/qa/perfect_books_wave2_20260718/lane03/renders/healthcare_rns__burnout__overwhelm_run.log`.
No `book.txt` written. Falling through to the best available prior manuscript per
dispatcher ruling.

## L2 — ONTGP read (real read, quoted evidence)

Sampled: Ch1, Ch5, Ch12 (last) of
`artifacts/wave_proof/draft/burnout_overwhelm__healthcare_rns/book.txt` — the exact
persona×topic×engine match by path name, and by far the strongest prose of the 3
cells' available manuscripts.

### Chapter 1 — "This Is Not Tiredness"

| Dimension | Verdict | Evidence |
|---|---|---|
| Orient | WEAK | Opens on direct emotional address, not body/scene: *"I want to say the sentence I think you have been holding. The nursing I was trained for does not exist in the job I am doing."* (L4) — strong voice, but the first concrete scene anchor (Maria in the break room) does not land until L22, past the ~120-word Orient window. |
| Name | PASS | *"The mechanism is called inadequate recovery—the state where the intensity of the work exceeds the recovery capacity available to the person doing it."* (L17) — precise, topic-specific mechanism naming, not generic stress language. |
| Turn | PASS | *"Maria is in the break room at 3 AM, sandwich untouched, eyes on the clock — she has four hours left on the stretch and her chest feels like she is watching herself from the hallway."* (L22) into the IV-pump/call-light scene (L26) — a real felt pivot from abstraction into embodied nursing detail. |
| Give | PASS | Implicit throughout via the "mechanism" framing rather than a discrete exercise block in the sampled excerpt — reads as WEAK-adjacent but the chapter's closing frame (naming the working-memory-budget mechanism, L36) functions as a cognitive tool the reader can hold. |
| Pull | PASS | Ends mid-shift with unresolved tension ("hour nine" of a demanding assignment, L30, and the working-memory mechanism explanation immediately after) — genuine traction into what the book promises to unpack next. |

### Chapter 5 — "Doing More to Feel Less Useless"

| Dimension | Verdict | Evidence |
|---|---|---|
| Orient | PASS | *"I've noticed that I'm becoming less human to my patients. I'm more efficient. More task-focused. Less able to sit with someone's fear or pain."* (L344) — first-person, embodied, immediate. |
| Name | PASS | *"The mechanism is called medical avoidance by medical professionals—this strange thing where knowing what's wrong becomes a substitute for actually addressing it."* (L348); reinforced with a second named mechanism later in the same chapter (*"Overfunctioning is not a personality type or a work ethic. It is a specific coping mechanism..."*, L387). |
| Turn | PASS | Tyler's dream-code vignette: *"His body is in constant readiness. The shift has ended but the shift has never ended."* (L353) — a strong, specific, nursing-grounded pivot. |
| Give | PASS | *"Press your feet into the floor. Feel the pressure through your soles... Press harder for three seconds. Release."* (L359) — concrete, embodied, repeatable practice. |
| Pull | **FAIL** | Chapter cuts off mid-sentence: *"The next chapter begins where insight usually thins out: inside the moment you have to choose again. An alarm this loud usually has something quieter underneath it. The signal makes more sense once the context is"* (L426, **text truncates here** — no period, no continuation). This is a hard rendering defect, not a stylistic weakness. |
| **Seam visibility** | **FAIL** | A near-identical seam paragraph repeats twice in this one chapter: *"So when the body tightens, do not solve the whole pattern here. Work with the place that braced first. / Start with the pressure under the sternum. That is the part still bracing."* appears at L389–391 and again, word-for-word, at L415–417. |

### Chapter 12 — "Rebuilding From the Inside" (last)

| Dimension | Verdict | Evidence |
|---|---|---|
| Orient | PASS | *"There's a specific mechanism at play when you can name every pathology except the one you're living."* (L994) — direct, embodied, sets up the chapter's real subject immediately. |
| Name | PASS | Names the mechanism explicitly (*"The mechanism here is called reframing, and I'm very good at it."*, L994) and grounds it physiologically (*"Sustained stress activates the sympathetic nervous system, which floods my bloodstream with cortisol and adrenaline..."*, L999). |
| Turn | PASS | Aisha crying in the supply closet then giving "the best handoff of the shift" (L1021) is a strong, specific, embodied turn appropriate to a closing chapter. |
| Give | PASS | Full micro-shake / breath-practice sequence (L1041–1055) — one of the most concrete, well-explained practices across all 3 sampled chapters of any of the 3 cells. |
| Pull (integration) | PASS | *"Recovery from burnout is not a return to a previous state... What is being built is something different: a self that has a sustainable relationship with its own capacity, built on worth that doesn't require depletion as proof."* (L1035, restated L1064) — a genuine thesis-level integration statement for a closing chapter. |
| **Seam visibility** | **FAIL** | The exact same broken ambient-detail phrase found in Ch5's sibling family recurs, now visibly garbled: *"The glass holds a softened outline at the frame holds steady. is a clock concept — you know it changed because the windows got dark."* (L1009) — grammatically broken (missing subject before "is a clock concept"); and *"A passing shadow at the sill holds steady moves through the room. through the room window."* (L1013) duplicates, near-verbatim, the identical broken phrase already seen twice in Ch5 of the tech_finance_burnout cell's manuscript (different persona, same shared template bug — see that cell's `NOTES.md`). |

## Overall verdict: **FAIL (closest of the 3 cells to PASS)**

Ch1 and Ch12 are strong — Ch12 in particular has 0 FAIL/0 WEAK across the 5 core
ONTGP dimensions and would PASS outright on its own. **What blocks a book-level PASS
is Ch5's hard defects**: a mid-sentence truncation (Pull=FAIL, a genuine rendering
bug, not a craft weakness) and a duplicated seam paragraph, plus the same broken
ambient-detail template recurring in Ch12. This is real, honest progress — the
closest of the 3 designated cells to `system working` — but it is not there yet. Do
not round WEAK-adjacent findings up to PASS.

## L3 — Fix applied / documented

- **Fixed (in scope):** this cell's own `STORY` bank
  (`atoms/healthcare_rns/burnout/STORY/CANONICAL.txt`) carried the same leaked-batch-
  generation-metadata defect as the other 2 cells (7 entries, v24–v30) — rewritten;
  see `NOTES.md`.
- **Not fixed (out of scope, catalog-wide shared renderer config):** the broken
  `window_reference` / light-detail ambient template family in
  `config/rendering/environment_fallback_families.yaml`, and the Ch5 mid-sentence
  truncation bug (likely a section-join/depth-enrichment boundary bug, not a content
  atom) — both documented with full evidence in `NOTES.md` and in the
  tech_finance_burnout cell's notes (shared root cause). Recommended as a dedicated
  Pearl_Dev-owned fix lane.

## L4 — Promoted

Atom fix landed directly in `atoms/healthcare_rns/burnout/STORY/CANONICAL.txt`.
