# Teacher Onboarding UI String Translation — 14 Locales — 2026-07-20

## Summary

Translated the Teacher Onboarding page's UI strings into all 14 canonical locales. This is
the standalone Claude translation lane named in the companion Cursor dev prompt
(`docs/agent_prompt_packs/20260720_teacher_onboarding_lang_and_hybrid_brands/01_CURSOR_DEV_teacher_onboarding_and_hybrid_brands.md`).
Out of scope for atom/doctrine/book content translation (the separate 46.2M-word standing
program) — this task touched only the 14 JSON resource files under
`brand-wizard-app/src/locales/teacher_onboarding/`.

## Discovery

All 14 locale files already existed in the working tree (untracked, from the Cursor dev
lane's Phase A scaffolding), including `en-US.json` as the baseline (131 leaf keys, 7
sections matching the live component). The 13 non-English files were **placeholder stubs**:
English content copied verbatim, each carrying a `_meta.todo` field reading
`"TODO(i18n): awaiting <locale>.json — falling back to en-US baseline until Claude
translation lane lands"`. This task is that lane. Verified `en-US.json` against the live
`brand-wizard-app/src/components/teacher-onboarding/TeacherOnboarding.jsx` (1508 lines) —
baseline strings matched the component exactly; no drift found. The loader
(`brand-wizard-app/src/i18n-teacher-onboarding.jsx`) already wires all 14 locales via
dynamic `import()` and ignores a top-level `_meta` key, so no code changes were needed —
only the JSON content.

## String count

131 leaf keys per locale, across 12 sections (`gate`, `chrome`, `header`, `identity`,
`rights`, `teachings`, `stories`, `practices`, `voice`, `activate`, `success`, `draft`,
`validation`, `common`).

## Baseline authorship

`en-US.json` was **pre-existing from the Cursor dev lane** — not authored by this pass. It
was read and verified against the live component before use as the translation source.

## Agent routing

Dispatched via the Agent tool directly to the 13 locale-native subagents (no orchestrator),
smoke → pilot → scale ramp:
- **Smoke:** `translate-ja` (ja-JP) — verified key parity + spot-checked 5 strings before
  proceeding.
- **Pilot (4, parallel):** `translate-zh-tw`, `translate-ko`, `translate-de`, `translate-es-la`
  (zh-TW, ko-KR, de-DE, es-US) — spanning CJK, Latin-diacritic, dual-Spanish-market cases.
- **Scale (8, parallel):** `translate-zh-cn`, `translate-zh-hk`, `translate-zh-sg`,
  `translate-es-es`, `translate-fr`, `translate-it`, `translate-hu`, `translate-pt-br`.

## Per-locale acceptance-check results

All 13 non-English locales, verified programmatically after every write:
- Valid JSON: **PASS** (all 13)
- Key parity vs `en-US.json` baseline (byte-identical key set, no missing/extra/renamed): **PASS** (all 13)
- No stub/TODO markers, no `_meta` key: **PASS** (all 13)
- No leftover untranslated English (excluding proper nouns `Pearl Prime`/`Pearl_Int` and
  literal placeholder examples like `teacher@example.com`): **PASS** (all 13) — one defect
  caught and fixed: `zh-TW.json` `common.url_placeholder` reverted to the English stub text
  mid-run (cause unclear — no other session was found editing this branch; possibly a stray
  tool-side revert); corrected via direct Edit and re-verified.
- zh-TW/zh-HK genuinely Traditional (not Simplified leakage): spot-checked with a
  Simplified-only character marker list — **none found** in either file.
- zh-CN/zh-SG/zh-TW/zh-HK are 4 distinct files (not duplicates of each other): confirmed via
  content hash — all 4 hashes differ.

## Register / terminology decisions (in-envelope, per prompt's Q-TRANS guidance)

No existing glossary entries in `config/localization/quality_contracts/glossary.yaml` cover
onboarding-specific terms ("teacher", "doctrine", "brand", "market") — confirmed by grep
before dispatch. Each locale agent was instructed to pick one consistent term for
"teacher" and "doctrine/teachings" and use it throughout that file; register was set
per-locale (formal address: Sie/vous/Lei/usted/Ön, polite Japanese/Korean, standard
Mandarin/Cantonese written register). Two locales (ja-JP, ko-KR) made a deliberate,
flagged word-order adjustment: `success.body_prefix` left empty, full sentence moved into
`body_suffix`, because the live component renders `{body_prefix} {name} {body_suffix}` as
a fixed positional concatenation and literal SOV-order translation into that slot structure
read awkwardly — verified this still renders a natural, grammatical sentence in both
languages.

## Commit / branch

- **Branch:** `agent/teacher-onboarding-lang-and-hybrid-brands-20260720` (existing shared
  branch — GitHub still 403 account-suspended, re-verified live via `git fetch origin` +
  `gh api user` at execution time, consistent with `docs/PROGRAM_STATE.md`
  "2026-07-19 Brand wizard onboarding" section).
- **Commit SHA:** `c2a7b9e3724311b9c6e75d8c1ef3f79ea6a37dcb`
- **Files:** exactly the 14 locale JSON files, `+2254/-0`, no other paths touched — matched
  `git diff --cached --stat` before commit.
- **PR:** none opened — GitHub push/PR/merge blocked by account suspension. This is the
  **only** blocked step; the translation work itself is fully committed, not left
  uncommitted or parked.

## Known-good anchor pointer

None needed — new content, not a restoration.

## Remaining blockers

1. **GitHub 403 (account suspended)** — blocks push/PR/merge. Re-run `git fetch origin` +
   `gh api user`; once both succeed, push this branch and open a PR (search
   `gh pr list --search "teacher onboarding" --state all` first for a sibling PR from the
   Cursor dev lane touching the same new directory before opening a second one).
2. **Q-TRANS-01** (should this JSON class join the `quality_contracts` CI gate machinery) —
   left as an open operator question per the prompt's recommended default: standalone for
   now, named here as a real small follow-on (a key-parity CI check across the 14 files) if
   the operator wants ongoing drift protection against new English strings added later
   without matching translations.

## Cleanup ledger

- No worktree created (shared tree, existing branch).
- No local/remote branch to delete (this IS the working branch, left in place for the
  operator/Cursor lane's continued work per the companion prompt).
- No scratch files created outside the 14 JSON files + this handoff.
- One stray git index.lock encountered mid-session (likely a concurrent process on the
  shared tree) — resolved by waiting, not by force-removing the lock.

## Next exact command if not fully landed

```
git fetch origin && gh api user   # re-check GitHub access
# once live:
git push -u origin agent/teacher-onboarding-lang-and-hybrid-brands-20260720
gh pr list --search "teacher onboarding" --state all   # check for sibling PR first
gh pr create --title "feat(i18n): teacher onboarding UI strings, 14 locales" --body "..."
python3 scripts/ci/pr_governance_review.py
bash scripts/git/pre_merge_check.sh <PR_NUMBER>
```
