# Prompt Pack: zh-TW/CJK Translation Quality Program — 2026-07-21

## Program goal

Build the operator's approved final architecture: Qwen3.7 Max (DashScope) as
primary literary translator + Qwen-MT as translation-specialist candidate +
Claude Code as coordinator/adversarial evaluator + xCOMET/CometKiwi as an
independent QE signal + deterministic structural validators + optional
Google/Azure candidates for disagreement and hard cases. Whole-corpus
analysis first, locked glossary/style guide, blind calibration, risk-based
candidate counts, targeted repair, chapter/book consistency passes.

## Live origin/main anchor used by router

`cc65ce42f2af6d5633bcd604c1bd2125a4dac899` (2026-07-19) — **re-fetch and
re-verify at execution time.**

## Operator decision already made (do not re-litigate)

The operator explicitly chose **"get an explicit policy exception"** when
asked how to handle DashScope Qwen3.7 Max / Qwen-MT given `CLAUDE.md`'s
BANNED paid-LLM-API list names "DashScope cloud" explicitly. Lane 00 lands
that exact, narrowly-scoped exception. It is NOT a blanket unban — every
other DashScope/paid-API call site in the repo stays banned.

## Credentials confirmed present (Keychain, 2026-07-21)

`QWEN_BASE_URL` (local Ollama), `QWEN_API_KEY`, `DASHSCOPE_API_KEY`,
`TOGETHER_API_KEY` (not used by this program — leave untouched, its ban is
unchanged), `HF_TOKEN` (xCOMET/CometKiwi, non-commercial license —
calibration/internal-signal use only, never the ship gate),
`GOOGLE_TRANSLATE_API_KEY`.

## Why this needs Claude Code (interactive), not a script

The pasted plan describes "Claude Code as coordinator and adversarial
evaluator" running blind ranking across hundreds of calibration items.
`CLAUDE.md` also bans `ANTHROPIC_API_KEY`/`CLAUDE_API_KEY` reads in repo
code — so this cannot be a headless script calling the Anthropic API in a
loop. The compliant, and only available, shape is: Claude Code sessions
(operator-present, Tier 1) driving the existing `translate-zh-cn` /
`translate-ja` / `translate-zh-tw` (and siblings) subagents via the `Agent`
tool, batched. Lane 02 is written for that shape, not for a batch harness.

## Files

- `00_governance_exception_dashscope_scoped.md` — Claude Code. Lands the
  scoped `banned_llm_patterns.yaml` exemption + `CLAUDE.md` footnote. **Land
  first** — Lane 01's DashScope client work and Lane 02's Phase 3 calibration
  both depend on this existing; everything else in both lanes can start
  before or in parallel with it.
- `01_cursor_build_translation_quality_pipeline.md` — Cursor (or Claude Code
  run directly, it's mechanical). Builds the infrastructure: deterministic
  validator, candidate-client wrappers (local Ollama, DashScope Qwen3.7
  Max/Qwen-MT behind the Lane-00 exemption, Google Translate, optional
  Azure), COMET scoring integration, calibration harness, acceptance-gate
  engine, repair/retry state machine, consistency-pass tooling. This is
  scaffolding — it does not translate or evaluate anything itself.
- `02_claude_corpus_analysis_and_evaluation_sequence.md` — Claude Code
  (interactive, Tier 1). Runs Phase 1 corpus analysis, Phase 2 spec/glossary
  authoring, Phase 3 blind calibration judging, and drives the ongoing
  semantic/Taiwan/voice evaluator stack via the `translate-*` subagents. This
  is where the literary/semantic judgment lives — do not try to automate it
  away.
- `03_reconcile_contamination_audit_and_rewrite_list.md` — Pearl_QA. Added
  2026-07-22. Two existing 2026-07-15 audits
  (`artifacts/qa/zh_tw_translation_gap_audit_2026-07-15.md` and
  `artifacts/qa/zhtw_simplified_sweep_20260715/summary.json`) disagree by an
  order of magnitude on how much landed zh-TW content is actually
  contaminated (3.8% conservative vs. 33% raw mechanical sweep, the latter
  inflated by ambiguous Traditional variant-form pairs). Nobody reconciled
  them — this lane produces the one real, file-level "needs rewrite" list,
  which is a genuine prerequisite the operator asked for before any repair
  work: "get the audit done so that we actually know what we have to
  write."
- `04_dispatch_zh_tw_rewrite_using_new_glossary.md` — Pearl_Localization.
  Added 2026-07-22. Dispatches `translate-zh-tw` repair batches against
  Lane 03's confirmed rewrite list, using Lane 02's corpus-derived glossary
  for consistent terminology instead of ad hoc per-file word choices.

## Wave order / dependencies

- Lane 00: no dependencies. Land first, small and low-risk (adds one
  `exempt_paths` entry + one doc footnote, touches zero runtime behavior by
  itself — `PHOENIX_TRANSLATION_ALLOW_CLOUD` still gates actual calls). As
  of 2026-07-22 this has NOT landed, and DashScope's own account is
  separately blocked by an unpaid balance (`Arrearage` on every chat-
  completion call, verified live 2026-07-19) — Lane 01 and Lane 02 Phase 3
  cannot proceed until BOTH clear. This does not block Lanes 02 Phase 1–2,
  03, or 04 below — none of them touch DashScope.
- Lane 01 and Lane 02 Phase 1 (corpus analysis) can start immediately,
  concurrently with Lane 00 and with each other — no shared write targets
  (01 writes `scripts/localization/translation_quality/**`, 02 writes
  `analysis/**`).
- Lane 02 Phase 3 onward (calibration, which needs the DashScope client from
  Lane 01 AND the exemption from Lane 00) blocks on both.
- **Lane 03 has no dependencies — run it now.** It reads existing audit
  artifacts and the live repo; nothing else in this pack gates it.
- **Lane 04 depends on Lane 02 Phase 1–2 (glossary) AND Lane 03 (rewrite
  list) both being complete.** It does not depend on Lane 00/01/DashScope at
  all — it's Tier-1 Claude (`translate-zh-tw`) repair work, same as the
  2026-07-15 gap-closure lane that already proved this path works.

## Recommended immediate sequence (given DashScope is currently blocked)

Run Lane 03 and Lane 02 Phase 1–2 in parallel today — both are unblocked,
disjoint write targets, and together they produce exactly what's needed to
answer "what do we actually have to write" and "what terms should we use
when we write it." Then run Lane 04. Lanes 00/01/Phase-3-onward can proceed
separately whenever the operator clears the DashScope arrearage and the
governance exception lands — they extend the pipeline to multi-candidate
adversarial evaluation later; they are not required to get real, correct
zh-TW files landed now.

## Hot-file conflict notes

None between 01 and 02 — disjoint write targets. Lane 00 touches
`config/governance/banned_llm_patterns.yaml` and `CLAUDE.md`; no other lane
in this pack touches either. Lane 03 writes only `artifacts/qa/
zh_tw_rewrite_list_*`; Lane 04 writes `atoms/**/locales/zh-TW/**` plus
appends to Lane 02's `analysis/glossary_project.yaml` — sequence Lane 04
strictly after Lane 02 Phase 1–2 to avoid it inventing glossary entries
that then conflict with Lane 02's own pass.

## Cost discipline (per the operator's plan)

Cursor's client wrapper (Lane 01) must hard-cap DashScope calls per run and
log an estimated spend — this is the actual enforcement of "diversity
without multiplying cost across every item," not a promise in a doc,
matching this project's standing "memory is recall, not enforcement" rule.
