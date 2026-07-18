# Phoenix Omega Claude Translation Agents

This directory defines Claude Code agents for Phoenix Omega localization work.
The intent is to make translation execution repeatable instead of paste-only:
the orchestrator builds the live locale gap, dispatches locale-native child
agents, and verifies that atom headers and coverage actually close.

## Agents

- `translate-orchestrator`: plans and coordinates translation waves.
- `translate-ja`: Japanese, `ja-JP`.
- `translate-ko`: Korean, `ko-KR`.
- `translate-zh-tw`: Traditional Chinese for Taiwan, `zh-TW`.
- `translate-zh-hk`: Traditional Chinese for Hong Kong, `zh-HK`.
- `translate-zh-sg`: Simplified Chinese for Singapore, `zh-SG`.
- `translate-zh-cn`: Simplified Chinese for Mainland China, `zh-CN`.
- `translate-it`: Italian, `it-IT`.
- `translate-fr`: French, `fr-FR`.
- `translate-de`: German, `de-DE`.
- `translate-es-la`: Latin American / US Spanish, `es-US`.
- `translate-es-es`: Spain Spanish, `es-ES`.
- `translate-hu`: Hungarian, `hu-HU`.
- `translate-pt-br`: Brazilian Portuguese, `pt-BR`.

## Required Operating Pattern

1. Run the orchestrator from a clean branch or isolated worktree.
2. Build a live worklist with `scripts/localization/build_14_locale_worklist.py`.
3. Dispatch locale agents only against their own locale path:
   `atoms/**/locales/<locale>/CANONICAL.txt`.
4. Use `.claude/skills/translation-qa/SKILL.md` as the QA contract.
5. Re-run the live worklist after every batch.
6. Do not report a locale complete unless its missing and partial counts are zero.

## Safety Rules

- Never weaken validation gates to make coverage look better.
- Never silently route through paid/cloud providers unless explicitly authorized.
- Never count a header-present but empty/English fallback block as translated.
- Preserve canonical atom header IDs exactly.
- Keep generated audit artifacts out of commits unless the repository gate expects
  them.

