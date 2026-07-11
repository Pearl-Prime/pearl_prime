# pt-BR Translation Taxonomy Repair — Handoff (2026-07-11)

**To:** owner lane `ws_cjk_atom_translation_qwen25_20260420` (and its non-CJK
follow-on, `NON_CJK_WAVE1_TRANSLATION_CLOSEOUT_2026-07-10`)
**From:** narrow infra-repair lane (this PR)
**Scope:** taxonomy/dispatch fix only — **no translation content added.**

## What changed

`pt-BR` was ratified as the 14th canonical locale in
`config/localization/locale_registry.yaml` (Q-MANGA-01, OPD-20260704-005,
2026-07-04), but three dispatch/reporting scripts were never updated to include
it in their non-CJK locale bucket:

1. `scripts/localization/run_translation_loop.py` — `EUROPEAN_LOCALES` tuple
   was `(es-US, es-ES, fr-FR, de-DE, it-IT, hu-HU)`, missing `pt-BR`. Fixed:
   added `pt-BR` to the tuple. `--european-locales` now dispatches 7 locales
   instead of 6.
2. `scripts/translate_atoms_all_locales_cloud.py` — had **no** non-CJK bucket
   at all (`CJK6_LOCALES` only). Added an `EUROPEAN_LOCALES` tuple mirroring
   `run_translation_loop.py` exactly, plus a `--european-locales` CLI flag and
   additive/dedup locale-resolution logic (same pattern as the loop script).
3. `scripts/ci/report_translation_coverage.py` — bestseller coverage section
   was hardcoded to `CJK6_LOCALES` only; it could not measure `pt-BR` (or any
   European locale) coverage. Added `EUROPEAN_LOCALES` + a parallel
   `by_european_locale` report section and text-output block.

Why it was missed originally: `pt-BR` was added to the locale registry as a
**cap amendment** (14th locale, after the original 13-locale/6-CJK+6-European
design was already coded into these three scripts' hand-rolled tuples). The
registry update did not fan out to the hardcoded tuples in the dispatch/report
scripts — a pure taxonomy-propagation gap, not a data or translation gap.

Verified against `config/localization/locale_registry.yaml`'s `locale_groups`
section before fixing: the registry's `european` group (5 locales, no
`es-US`/`pt-BR`) and `latam` group (`es-US`, `pt-BR`) do **not** match the
scripts' existing `EUROPEAN_LOCALES` bucket (which is really "all non-CJK,
non-baseline locales" — 6 before this fix, 7 after). Rather than force a
mismatched registry group onto these scripts, `pt-BR` was added directly to
the existing hand-rolled tuple, since that exactly reproduces
`locale_groups.all_locales` minus `en-US` (baseline) minus the CJK6 — i.e. it
is the correct, already-implied bucket.

## What did NOT change

- No atom translation content — this is a taxonomy/dispatch fix only.
- `.github/workflows/translate-atoms-qwen-matrix.yml`,
  `generate-and-translate-atoms.yml`, `translate-bestseller-atoms.yml` — left
  disabled, untouched. They are correctly and truthfully disabled (no
  pearl-star self-hosted runner registered; ubuntu-latest cannot reach the
  Tailscale-only Ollama endpoint). This repair does not change that substrate
  truth — `--european-locales`/`pt-BR` dispatch through these scripts still
  requires either a Tier-1 Claude Code session or a working Tier-2
  Ollama/Qwen endpoint reachable from wherever the script actually runs.
- `scripts/ci/report_translation_coverage.py`'s teacher-bank corpus
  (`SOURCE_OF_TRUTH/teacher_banks/**/approved_atoms/*.yaml`, ~2,490 files) is
  still not counted by this script — it only ever covered `atoms/` (~5,181
  files), for both CJK and now European/pt-BR. That gap is pre-existing and
  symmetric across all locales already measured by this tool; not introduced
  or fixed by this repair.

## The real gap that remains: translation coverage, not tooling

Per `artifacts/qa/NON_CJK_WAVE1_TRANSLATION_CLOSEOUT_2026-07-10.md` (live,
verified 2026-07-10): of **7,671** non-CJK-translatable EN source files
(`atoms/` bestseller atoms + `SOURCE_OF_TRUTH/teacher_banks` approved atoms
combined), **pt-BR coverage was 8/7,671** (`midlife_women` × `anxiety`, 8 of 9
atom types, pilot slice only). `es-US` was also 8/7,671. All other European
locales (`es-ES`, `fr-FR`, `de-DE`, `it-IT`, `hu-HU`) were 0/7,671.

This taxonomy fix does not move that number — it only means `pt-BR` is now
correctly *selectable* through `--all-locales`/`--european-locales` bucket
flags in both dispatch scripts, and correctly *measured* by the coverage
report. The 7,663-file pt-BR residual is real, unclosed translation work for
the owner lane, not an infra blocker. Per `CLAUDE.md`'s LLM Tier Policy, bulk
non-CJK translation content must go through Tier 1 (Claude Code,
operator-present) unless/until a Tier-2 local Ollama non-CJK pipeline exists
(it does not today).

## Suggested next step for the owner lane

Re-run `python3 scripts/ci/report_translation_coverage.py --locales pt-BR`
(now reports `by_european_locale.pt-BR` correctly) to confirm the current
residual before planning the next authored translation slice.
