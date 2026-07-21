# CLOSEOUT — Teacher onboarding i18n + Storyblocks bank fill — 2026-07-20

```
CLOSEOUT_RECEIPT
AGENT:          Cursor (Pearl_Localization + Storyblocks fill)
TASK:           Teacher onboarding UI string translation, 14 locales + Storyblocks social bank seed
COMMIT_SHA:     4f4750327cd91a172ede752b76470a2f3492b497 (i18n fix + Storyblocks receipt)
                + ledger follow-up on HEAD (see git log)
FILES_WRITTEN:  brand-wizard-app/src/locales/teacher_onboarding/{en-US,zh-CN,zh-TW,zh-HK,zh-SG,ja-JP,ko-KR,es-US,es-ES,fr-FR,de-DE,it-IT,hu-HU,pt-BR}.json
                artifacts/storyblocks/social_bank_fill_20260720.json
                artifacts/storyblocks_licensed/social_media_bank_storyblocks_20260720/* (local HD, gitignored)
                artifacts/coordination/handoffs/teacher_onboarding_translation_2026-07-20.md
PROVENANCE:     en-US baseline from Cursor Phase A; 13 locales via translate-* subagents (smoke ja-JP → pilot → scale); Storyblocks search→confirm_selection
STATUS:         completed (translations + local Storyblocks HD); push/PR BLOCKED (GitHub 403 suspended)
HANDOFF_TO:     Pearl_GitHub (push/PR when account restored)
NEXT_ACTION:    git fetch origin && gh api user; then push agent/teacher-onboarding-lang-and-hybrid-brands-20260720
SIGNAL:         teacher-onboarding-i18n-14-of-14-landed=4f4750327cd91a172ede752b76470a2f3492b497
```

## Counts
- UI strings: **131** leaf keys × **14** locales
- Storyblocks confirmed: **3 video + 3 image** → `artifacts/storyblocks_licensed/social_media_bank_storyblocks_20260720/`
- Face-risk note: image `351250623` (person in frame) — look_gate PENDING for faceless families

## GitHub
Account suspended (403) — offline land only; ledger `HOLD-offline-no-push`.
