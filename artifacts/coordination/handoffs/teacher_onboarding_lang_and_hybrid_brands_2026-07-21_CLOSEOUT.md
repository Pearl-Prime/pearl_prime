# CLOSEOUT_RECEIPT — Teacher onboarding lang switcher + hybrid brands

```
CLOSEOUT_RECEIPT
AGENT:          Cursor (dev) — resume/finish after interrupt; worktree lane
TASK:           Teacher onboarding language switcher + teacher-owned/hybrid brand generation
COMMIT_SHA:     A=b9db18709508e72965b2a0ba9dfc5aa76fa6076d
                B=55923199611675e4121f8952dd80bdfce634dd86
                C=c825129940a4fae1a970b5acd5e8541aa37187b0
                handoff-pin=00cf971a93c28e80a0afe4b3db5453415f279981
                proof-fix=<this commit>
BRANCH:         agent/teacher-onboarding-lang-and-hybrid-brands-20260721
WORKTREE:       /Users/ahjan/phoenix_omega/.worktrees/teacher-ob-20260721
FILES_WRITTEN:  (phases A–C already on branch; this closeout adds corrected Phase C A/B proof + handoff/CLOSEOUT)
FILES_READ:     EXECUTE prompt; prior finish-agent closeout; handoff 2026-07-21;
                teacher_brand_generator.py; brand_onboarding.py; FlagLocaleGate.*;
                predecessor name_occurrence_report.json (hybrid_brand_onboarding_20260720)
PROVENANCE:     Extends ancestral f0faac8d2e flag gate + 14-locale i18n; net-new
                phoenix_v4/brand_generation + teacher_originated_brands.yaml;
                409 teacher_claimed offer + accept-hybrid (FastAPI + CF)
STATUS:         A=completed (MERGED local) ; B=completed (MERGED local) ; C=completed (MERGED local)
                proof gap closed this session: name_occurrence A/B was seed-divergence only —
                replaced with reader-facing named-vs-hybrid occurrence report (pass=true);
                sparse worktree expanded so pytest can read SOURCE_OF_TRUTH/teacher_banks
HANDOFF_TO:     Pearl_GitHub / next Claude session (git landing)
NEXT_ACTION:    push agent/teacher-onboarding-lang-and-hybrid-brands-20260721 ;
                run push-guard + preflight + pr_governance_review.py ; open PR
SIGNALS:        teacher-onboarding-flag-selector-landed=b9db18709508e72965b2a0ba9dfc5aa76fa6076d ;
                teacher-owned-brand-generator-landed=55923199611675e4121f8952dd80bdfce634dd86 ;
                hybrid-brand-onboarding-routing-landed=c825129940a4fae1a970b5acd5e8541aa37187b0
```

## Verification this session

| Check | Result |
|-------|--------|
| `pytest tests/brand_generation/` | **7 passed** (after sparse-checkout add of teacher_banks + marketing/authoring) |
| `check_teacher_onboarding_locales.mjs` | 14×131 OK |
| `check_teacher_onboarding_flag_gate.mjs` | OK |
| Vitest `FlagLocaleGate` | **4 passed** |
| Phase C A/B `name_occurrence_report.json` | **pass=true** (named name total=8, hybrid=0, doctrine markers>0) |

## Applied defaults (unchanged)

- Q-BRAND-GEN-01 → separate `teacher_originated_brands.yaml`
- Q-BRAND-GEN-02 → deterministic seeded, no LLM
- Q-BRAND-GEN-03 → lazy hybrid on accept only
- Q-LANG-01 → Screen 3 link on `pearl_prime_entry.html`

## Explicit non-actions

- Did **not** touch `.github/workflows/brand-admin-onboarding-pages.yml`
- Did **not** push
- Did **not** commit bestseller-lane work on `agent/bestseller-atom-flow-lanes-20260721`
- Did **not** `git add -A` (node_modules left untracked)
