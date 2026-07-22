EXECUTE. This lane is the payoff of Lanes 02 (glossary) and 03 (rewrite list) — do not
run it until both exist, and do not re-derive either from scratch if they're already
sitting on disk.

You are Pearl_Localization, dispatching the actual `translate-zh-tw` repair work now
that (a) the corpus-derived glossary exists (`analysis/glossary_core.yaml` +
`analysis/glossary_project.yaml` + `analysis/style_guide_zh_tw.yaml` from Lane 02
Phase 1–2) and (b) the reconciled rewrite list exists
(`artifacts/qa/zh_tw_rewrite_list_<date>.tsv` from Lane 03) telling you exactly which
files are `TRUE_CONTAMINATION` or `WRONG_REGISTER_CLEAN_SCRIPT` and therefore actually
need rewriting — not the inflated 33% raw-sweep number and not the possibly-too-low
3.8% conservative number.

## Pre-flight

1. `git fetch origin`; confirm Lane 02's `analysis/` outputs and Lane 03's
   `artifacts/qa/zh_tw_rewrite_list_*.tsv` exist and are current (check dates — if
   `origin/main` has moved significantly since either was generated, some flagged
   files may have already been fixed by an unrelated PR; spot-check a handful before
   trusting the list wholesale).
2. Filter the rewrite list to `verdict == TRUE_CONTAMINATION` or
   `verdict == WRONG_REGISTER_CLEAN_SCRIPT`. Do NOT dispatch repairs for
   `AMBIGUOUS_VARIANT` or `CLEAN` rows — that would be rewriting files that don't
   actually need it.
3. Load the glossary and style guide into context before dispatching any subagent
   batch — every `translate-zh-tw` call in this lane should be instructed to apply
   `analysis/glossary_core.yaml` terms consistently, not re-invent terminology
   per-file (that inconsistency is itself part of what makes translated corpora read
   as low-quality).

## Task

Batch the confirmed-bad file list (likely low hundreds, not thousands — this repo's
own conservative estimate was ~195 files) into `translate-zh-tw` subagent dispatches
via the `Agent` tool, smallest-safe-batch per this repo's own translation-wave
precedent (`ws_translation_wave_cjk_primary_20260712` used small batches after GPU/
throughput problems on the Qwen path — this lane is Tier-1 Claude only, no GPU
constraint, but keep batches reviewable, e.g. 10-20 files per dispatch). Each dispatch
must:
- Instruct the subagent to use the new glossary for any term it covers, and to flag
  (not silently invent) any recurring term it encounters that ISN'T in the glossary
  yet — feed those back into `analysis/glossary_project.yaml` as you go, so the
  glossary gets more complete as repair proceeds, not just at the one-time Lane 02
  pass.
- Re-run this repo's zh-TW Simplified-contamination gate (the CI check landed via PR
  #49, `check_zh_tw_simplified_contamination.py`, or `scripts/ci/` equivalent — find
  its live location, it may have moved) against each repaired file before counting it
  done.
- NOT touch any file outside the confirmed rewrite list, even if it looks suspicious
  during review — flag those separately rather than silently expanding scope.

## Landing

Standard branch/PR/governance flow, batched (don't try to land all repairs in one
giant PR — follow this repo's PR-size governance; split into reviewable chunks if the
confirmed list is large). Watch CI to terminal state per batch.

## CLOSEOUT_RECEIPT (required, exact)

Files repaired count vs. total confirmed-bad count (may be a partial pass — say so
honestly if you don't finish the whole list in one session, and leave a clear resume
marker). New glossary terms discovered and added during repair (count + where).
Contamination-gate pass/fail per repaired file. Signal token:
`ZHTW_REWRITE_DISPATCHED_<files repaired>_<files remaining>`.
