# Handoff — zh-TW/CJK Translation Quality Program (Lane 02, Phase 1-2)

**Date:** 2026-07-22
**Agent:** Pearl_Translator_Coordinator
**Branch:** `agent/zh-tw-glossary-build-20260722`
**Lane:** `docs/agent_prompt_packs/20260721_zh_tw_translation_quality_program/02_claude_corpus_analysis_and_evaluation_sequence.md`

## Phase reached: 2 (of 4). STOPPED at mandatory checkpoint per lane instructions.

## What was done

**Phase 1 — corpus analysis.** Full production atom corpus mapped: 5,213 `CANONICAL.txt`
files (72,962 prose variants) across 14 personas / ~230 topics under `atoms/`. Production-scope
subset (12 atom types per `report_translation_coverage.py`'s own definition) = 3,755 files —
this number cross-validates exactly against `docs/PROGRAM_STATE.md`'s and the 2026-07-15 gap
audit's independently-computed production-scope count, confirming item-granularity (one row per
`persona/topic/slot_type` CANONICAL.txt file) matches the repo's own coverage-scope logic.

Read real prose (not headers/metadata) across ~660 sampled variants, weighted toward
`tech_finance_burnout`, `corporate_managers`, `working_parents` (defect-concentrated pools per
the contamination audit) plus a breadth sample across the other 11 personas.

**Real finding surfaced (not previously documented at this granularity):** a shared sentence-
skeleton template is reused across 53-172 items per skeleton (`analysis/duplicate_clusters.json`)
in the PIVOT/STORY/TAKEAWAY family. Some topic-specific fills are genuine coined metaphors
("depletion dressed as dedication", "golden handcuffs"); others are broken/ungrammatical
placeholder-style fills ("the loss didn't ask permission", "the mourning has no schedule") that
read as unfilled template artifacts even in the English source. This corroborates
`PROGRAM_STATE.md`'s known Q1 atom-cohesion finding at a new, specific, machine-verifiable level
(exact skeleton strings + exact affected item_ids). Flagged in `style_guide_zh_tw.yaml`
(`template_artifact_handling`) with an explicit translation rule: translate intended meaning, do
not force literal awkward renderings, and flag the item back to the atom-cohesion lane.

**Phase 2 — glossary/style guide.** Populated `glossary_core.yaml`, `glossary_project.yaml`,
`style_guide_zh_tw.yaml`, `protected_terms.yaml`, `regional_usage_watchlist.yaml`,
`concept_map.json` from the real sampled reading. Cross-checked every Simplified/Traditional
boundary call against `artifacts/qa/zh_tw_translation_gap_audit_2026-07-15.md` §6 (Big5 + s2t
dual-check calibration for 台/吃/游/群/床 etc.) and `artifacts/qa/zhtw_simplified_sweep_20260715/
summary.json`'s top confirmed-Simplified pairs (托/这/个/为/无/发/经/过). Reader address confirmed
as 你 (default) by actually reading the second-person voice pattern across the sample, not
assumed. Two open questions flagged explicitly for operator sign-off (do not resolve silently):
(1) named recurring characters (Marcus, Elena, James, Priya, Devon) — keep Latin script or
transliterate, book-wide consistency decision; (2) `template_artifact_handling` rule itself
should be confirmed as the right policy before Phase 4 production dispatch.

## Deliverables (all under `analysis/`, all non-empty)

| File | Lines/rows |
|---|---|
| `corpus_manifest.jsonl` | 5,217 |
| `glossary_core.yaml` | ~230 lines |
| `glossary_project.yaml` | ~140 lines |
| `style_guide_zh_tw.yaml` | ~180 lines |
| `concept_map.json` | 8 concepts |
| `protected_terms.yaml` | ~65 lines |
| `regional_usage_watchlist.yaml` | ~50 lines |
| `duplicate_clusters.json` | 6 clusters, 53-172 members each |
| `risk_map.jsonl` | 5,217 (low 6 / medium 765 / high 2,900 / critical_recurring 1,546) |
| `calibration_set.jsonl` | 251 (stratified, oversampled high/critical, weighted toward defect pools) |
| `structural_signatures.jsonl` | 14 slot-type structural contracts with real word/sentence-count stats |

Self spot-check (Phase 1 TESTS/PROOFS requirement): pulled 5 `high` + 5 `low` risk_map items,
re-read actual bodies, all 10 classifications held up. Also confirmed the 4 `low`-tier auxiliary
catalog docs (`INDEX.md`, `GENERATION_SUMMARY.txt`, `SAMPLE_PREVIEW.txt`,
`REFLECTION_MANIFEST.md`) genuinely exist on `origin/main` under `atoms/`.

## Known limitations (honest, not swept under the rug)

- Corpus reading was a deliberate weighted SAMPLE (~1,000 variants read directly out of 72,962
  total), not exhaustive — appropriate for glossary/style-guide authoring, not a claim that every
  atom was read.
- `risk_map.jsonl` has a genuine near-absence of "low" tier content at the atom-body level (only
  6 of 5,217 items) — this corpus is deliberately 100% literary/therapeutic prose, not UI
  strings/metadata, so almost nothing is structurally low-risk. This is a real finding about the
  corpus shape, not a classification bug (verified by re-reading TRANSITION-slot content, which
  looked candidate-low but reads as full narrative prose on inspection).
- Two files (`gen_z_professionals/anxiety/ANGLE_DEFINITION/{ENGINE,PROTECTIVE_ALARM}`) don't fit
  either observed header convention (`## SLOT vNN` or `--- variant: vNN`) — treated as low-risk
  planning text based on content inspection, variant_count recorded as best-effort.
- `healthcare_rns/sleep_anxiety/shame` (and likely other `healthcare_rns` cells, not exhaustively
  checked) use a third, "condensed" combined-atom format (`## RECOGNITION through EMBODIMENT
  COMBINED`) not covered by `structural_signatures.jsonl`'s per-slot breakdown — flagging for
  whoever runs Lane 01's structural validator against this locale next; not fixed here, out of
  this lane's scope.
- Named-character transliteration and template-artifact handling are explicitly left as OPEN
  questions for the operator, not silently decided.

## Infra state observed this session (context for whoever resumes)

- Lane 01's harness (`scripts/localization/translation_quality/`) does **not** exist yet on
  `origin/main` as of this session — consistent with the prompt pack's stated wave order (Lane 01
  and Lane 02 Phase 1-2 run in parallel, no dependency). Phase 3 cannot start until it lands.
- `agent/zh-tw-audit-reconcile-glossary-rewrite-20260722` exists as a remote branch but had not
  produced `artifacts/qa/zh_tw_rewrite_list_*.tsv` on `origin/main` as of this session — proceeded
  without it per the lane's own fallback instruction.
- `agent/zh-tw-corpus-analysis-glossary-20260722` exists as an empty/unstarted local branch
  (identical to `origin/main`, zero diff) — appears to be an unused duplicate dispatch of this
  same lane, not active competing work. Not touched by this session.
- **Filesystem note for future sessions:** `git worktree add` and even `git status` inside a
  freshly-checked-out worktree were extremely slow to the point of stalling (many concurrent
  agent worktrees on this machine saturating disk I/O — consistent with the
  `project_worktree_disk_constraint` memory note). This session worked around it entirely via git
  plumbing (`GIT_INDEX_FILE` + `read-tree`/`hash-object`/`write-tree`/`commit-tree` against
  `origin/main`'s tree, reading corpus content via `git cat-file --batch` instead of a working-tree
  checkout) rather than waiting on the stalled checkout. Two now-orphaned worktree/branch
  artifacts from the stalled attempts
  (`agent/zh-tw-glossary-build2-20260722` branch + its worktree at `/tmp/zh-tw-glossary-build2`,
  and a possible lingering `/tmp/zh-tw-glossary-build` remnant) should be pruned by whoever next
  runs `git worktree prune` / `git branch -D` on this machine — left in place here rather than
  risking a destructive cleanup mid-session on a shared, I/O-contended filesystem.

## NEXT_ACTION

Awaiting operator glossary/style-guide sign-off (report below). Once confirmed:
- Phase 3 (blind calibration) requires Lane 01's candidate clients + calibration harness to land
  first, plus Lane 00's governance exception + DashScope arrearage clearance if DashScope
  candidates are wanted for the round (Ollama + Google can run without either).
- If the operator wants named-character transliteration resolved before Phase 3, that ruling
  should be appended to `analysis/glossary_project.yaml`'s `named_recurring_characters` block.
