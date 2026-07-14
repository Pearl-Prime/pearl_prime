# Anxiety Flagship Enhancement Pilot Packet

**Date:** 2026-07-13
**Status:** Pilot authoring packet — illustrative, not a template to copy verbatim
**Authority:** [ENHANCEMENT_CONTRACT_V2_WORKING_PRIORS_2026-07-13.md](../ENHANCEMENT_CONTRACT_V2_WORKING_PRIORS_2026-07-13.md) §7 (`anxiety_flagship_hybrid` preset), [specs/ACCENT_BEATS_SYSTEM_SPEC.md](../../specs/ACCENT_BEATS_SYSTEM_SPEC.md) §14
**Profile:** `anxiety_flagship_hybrid` — `practical_credible` base + `intimate_voice` modifiers, 12-chapter trade self-help book

## Purpose

This packet is the reference shape for planning a new anxiety-profile book. It shows, chapter by chapter, where each of the four layers does its work — not just where `optional_accents` go. It is not a formula to reproduce chapter-for-chapter in every book; individual chapters should keep the dominant-archetype variety described in the authority doc §8 (`recognition_chapter`, `mechanism_chapter`, `reframe_chapter`, `practice_chapter`, `resistance_chapter`, `integration_chapter`).

## How to read this table

- **Dominant job** — the chapter archetype driving this chapter (authority doc §8). Not every chapter needs to run all four phases (arrival/discovery/action/integration) — the archetype tells you which phase(s) to lean into.
- **Proof / embodiment** — `EXTERNAL_STORY` (with function tag), `AUTHOR_DISCLOSURE`, or `CITED_EVIDENCE` placed in this chapter. Not sparse; planned per the book-level minimums in the authority doc §7.1.
- **Optional accent** — the one `optional_accents` element (if any) placed in this chapter. Most chapters carry none; per the global slot budget (spec §4.2a), at least 4 of 12 chapters must be accent-free.
- **Callback** — a `CALLBACK_PLANT` or `CALLBACK_RETURN` in this chapter, with `return_function` where applicable.
- **Analogy / metaphor** — where a `major_explanatory_analogy` or `developed_or_recurring_metaphor` does real explanatory work.

## Chapter-by-chapter plan

| Ch | Dominant job (archetype) | Proof / embodiment | Optional accent | Callback | Analogy / metaphor |
|----|---------------------------|---------------------|------------------|----------|----------------------|
| 1 | `recognition_chapter` — dense `VALIDATION_NORMALIZATION`, name the loop | `AUTHOR_DISCLOSURE` (`credibility` function) — author names their own version of the loop | — (bare) | **PLANT** `image_id: caged-bird` — the loop as a bird pacing a cage it doesn't know is open | Introduce the cage/bird image as the book's central explanatory metaphor for the anxiety loop |
| 2 | `mechanism_chapter` — how the nervous system generates the loop | `CITED_EVIDENCE` (mechanism-supporting stat, early-to-middle placement, after the reader has been met) | `REFLECTION_QUESTION` — `after_REFLECTION` | — | Body-alarm analogy: nervous system as a smoke detector that can't tell toast from fire |
| 3 | `recognition_chapter` — a second, different-context version of the loop | `EXTERNAL_STORY` — function `recognition` | — (bare) | — | — |
| 4 | `practice_chapter` — first real exercise | — | `ENCOURAGEMENT` — `after_EXERCISE` | — | — |
| 5 | `mechanism_chapter` — re-explain the mechanism in a new situation (work/relational) | `CITED_EVIDENCE` #2 | — (bare) | — | Re-use the smoke-detector image in a new context (deepen, not repeat) |
| 6 | `reframe_chapter` — the loop as adaptation, not defect | `EXTERNAL_STORY` — function `mechanism_proof` | `AUTHOR_COMMENTARY` — `after_REFLECTION`, orientation function | — | — |
| 7 | `resistance_chapter` — what gets in the way of practicing | `AUTHOR_DISCLOSURE` (`failure_model` function) — author's own attempt that didn't work at first | — (bare) | **RETURN** `caged-bird` → `reinterpret`: "from trapped nervous system to protective adaptation" | — |
| 8 | `practice_chapter` — harder exercise, real stakes | — | `ENCOURAGEMENT` — after a difficult realization | — | — |
| 9 | `recognition_chapter` — a story that shows the cost of *not* practicing | `EXTERNAL_STORY` — function `cautionary` | — (bare) | — | — |
| 10 | `mechanism_chapter` — troubleshooting the practice in real life | `TROUBLESHOOTING` (`chapter_engine`, after `INTEGRATION`) | — (bare) | — | — |
| 11 | `integration_chapter` — the practice under everyday pressure | `EXTERNAL_STORY` — function `possibility` (someone who kept going) | `QUOTE` — closer, `before_THREAD` | **RETURN** `caged-bird` → `transfer`: the reader's own version of the open door | — |
| 12 | `integration_chapter` — closing, forward-carrying | `AUTHOR_DISCLOSURE` (`turning_point` function) — where this practice landed for the author | `WISDOM_ESSENCE` — `before_THREAD`, secular register (book's only use; hard cap 1) | **RETURN** `caged-bird` → `close`: the image as the book's last image | — |

## Budget check against the authority doc

- **`optional_accents` used:** `REFLECTION_QUESTION` ×1, `ENCOURAGEMENT` ×2, `AUTHOR_COMMENTARY` ×1, `QUOTE` ×1, `WISDOM_ESSENCE` ×1 = 6 total across 6 chapters — inside `target_total_accents: 7-9` (hard max 10) and `target_accent_chapters: 5-7` (hard max 8). Six chapters (1, 3, 5, 7, 9, 10) are accent-free, clearing the `accent_free_chapters_minimum: 4`.
- **`proof_and_embodiment` used:** `CITED_EVIDENCE` ×2 (target 1, hard max 2 — at cap), `EXTERNAL_STORY` ×4 (target 2, hard max 3 — **over target**; trim to 3 in build, keeping `recognition`/`mechanism_proof`/`cautionary` and dropping one), `AUTHOR_DISCLOSURE` ×3 (target 1, hard max 2 — **over cap**; trim to 2, keep `credibility` early and one late-book function).
- **`chapter_engine_expectations`:** `TROUBLESHOOTING` ×1 (target 2 — add one more, e.g. chapter 8 or 10, after a second hard exercise).
- **`cohesion_and_craft`:** one callback thread with 3 returns (`reinterpret`, `transfer`, `close`) plus a recurring metaphor (smoke-detector) — inside the `callback_or_motif_returns: 5-8` target once the second callback thread (the smoke-detector re-uses) is counted; add 1-2 more small returns in build if the count reads thin.

**Read this packet as a first draft against the budget, not a finished plan** — the over/under notes above are intentional: they show how to check a chapter-by-chapter draft against the profile's minimums and maxima before locking a plan, not a claim that this exact table is gate-clean. Trim `EXTERNAL_STORY` and `AUTHOR_DISCLOSURE` to the counts above before this plan ships.

## What this packet is not

- Not a claim that any of this prose exists yet — this is planning shape, not authored content.
- Not a replacement for the per-book `story_metadata` / `evidence_metadata` / `callback` YAML blocks required by [specs/ACCENT_BEATS_SYSTEM_SPEC.md](../../specs/ACCENT_BEATS_SYSTEM_SPEC.md) §2.5 and §2.6 — every proof/embodiment and cohesion element listed above still needs its full metadata block when authored.
- Not empirically validated dosage — per the authority doc §15, these are research-informed working priors, not a benchmarked count.
