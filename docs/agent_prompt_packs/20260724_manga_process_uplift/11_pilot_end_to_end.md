# EXECUTE — Lane 11 — Pilot: one series through the full new loop

**AGENT:** Pearl_Writer + Pearl_Editor (Tier-1 Claude) · **SUBSYSTEM:** manga_pipeline · **WAVE:** 3

## GATE CHECK
Proceed when BOTH `manga-series-master-plan-contract-merged=<sha>` AND
`manga-genre-checklists-wired=<sha>` exist. Check (don't require) `manga-skills-registered`,
`manga-bank-demand-rollup-merged`, `manga-storyboard-consumed` — use whichever landed; note in
the closeout which parts of the loop ran on merged tooling vs contract-manual fallback.

## EXECUTION CONTRACT (binding, in-band)
- EXECUTE end-to-end; terminal = signal token or ONE BLOCKER (evidence + pushed work +
  NEXT_ACTION). STARTUP_RECEIPT / CLOSEOUT_RECEIPT bracket the work.
- Re-verify premises live; DISCOVERY REPORT first (including: does the chosen series already
  have a master plan from Lane 06's golden example? If yes, EXTEND it — do not re-author).
- Substrate: plumbing for artifacts; run validators from the full checkout (sparse-cone parity
  is a known false-FAIL source — repo memory).
- Landing: MERGED (checks read + named) or BLOCKED. Cleanup ledger + handoff
  `artifacts/coordination/handoffs/manga_process_uplift_lane11_2026-07-24.md`.
- PROVENANCE: research=(all four Wave-1 outputs); documents=master-plan contract + excellence
  gate spec + storyboard contract; builds_on=Lane 06 golden master plan, existing
  chapter_scripts + arc storyboards for the series; inventory=EXTENDS.

## READ FIRST
Lane 06's golden master plan + its series' existing artifacts (chapter_scripts, arc_storyboards,
bank_contracts, image_bank state), `skills/manga-story-writer/SKILL.md` + `skills/manga-editor/
SKILL.md` + `skills/manga-storyboarder/SKILL.md` (if landed — else the contract specs directly),
`config/manga/genre_craft_checklists.yaml`, `scripts/manga/validate_story_excellence.py`,
`scripts/ci/check_manga_story_authored.py`, `scripts/manga/assemble_from_bank.py`.

## MISSION — prove the operator's full loop on ONE series, honestly labeled
Series: the Lane 06 golden-example series (default `stillness_press…the_alarm_is_lying` unless
Lane 06 chose otherwise — follow its choice).

1. **Master-plan editor pass:** Pearl_Editor reviews the 100-ep master plan per the §Editor pass
   checklist flow (genre contract, cadence conformance, MC endurance, mode-arc coherence) →
   review artifact committed → REVISE loop until APPROVE.
2. **Arc episode-planning pass:** for the CURRENT arc (wherever the series' authored episodes
   end), fill/refresh the per-episode plan rows (logline, genre-pleasure beat, self_help_topic
   beat, hook position) per the master-plan contract; editor verifies per-episode checks.
3. **Write 2 NEW episodes** (the next two unauthored) through the full chain: writer skill flow →
   `chapter_script_writer_handoff` YAMLs → excellence gate ≥85 + story-authored gate PASS →
   editor per-item checklist read → APPROVE (iterate; record every REVISE round — the iteration
   trace is evidence the process works, not failure).
4. **Storyboard both episodes** via the storyboarder flow (arc_storyboard schema-valid, CI check
   PASS, layer picks from the bank contract, gap rows emitted).
5. **Bank demand delta:** run the Lane 09 rollup if merged (else hand-derive the delta table for
   the 2 episodes) — commit the rollup/delta artifact.
6. **Assemble one episode** with `assemble_from_bank.py` from whatever REAL layers exist +
   INTERIM stand-ins for gaps (labeled; INTERIM is never final art) — composition grammar +
   genre bubbles (v2) on; commit `_provenance.json` evidence. NO GPU rendering; missing layers
   stay INTERIM (rendering is an M5 lane, RAP queue-first, out of scope here).
7. **Verdict doc:** `artifacts/qa/manga_process_uplift_pilot_2026-07-24/SUMMARY.md` — what the
   loop caught (checklist items that forced revisions = the payoff evidence), tool gaps, timing
   per stage, and the honest layer: scripts = **authored candidate**; loop = **system working**
   AT MOST if every gate ran green end-to-end; explicitly NOT PROVEN-AT-BAR (blind-10 unjudged).
   These 2 episodes are prime blind-10 candidates — say so for the M6 lane.

## OPERATOR VISIBILITY
Last step: `open artifacts/qa/manga_process_uplift_pilot_2026-07-24/` (auto-open for review —
house rule). The operator read is invited, not claimed.

## WRITE SCOPE
The series' master plan (revision), episode-plan rows, 2 new `chapter_scripts/` episodes, 2 arc
storyboards, review artifacts, demand delta, one assembled episode dir (INTERIM-labeled), pilot
SUMMARY, handoff. **OUT OF SCOPE:** other series, GPU renders, gate/config/code edits (file
issues to dispatcher instead), PROGRAM_STATE.

## DO NOT
- Never report bestseller/shippable/done without the acceptance layer named (G-CLAIM applies).
- Never restitch old images as proof — fresh assembly output only, INTERIM-labeled.
- Teacher never named in panel text (hard gate).

## SIGNAL
`manga-process-pilot-system-working=<full merge SHA>` (emit ONLY if the full loop ran with all
gates green; otherwise `manga-process-pilot-authored-candidate=<sha>` + gap list).
