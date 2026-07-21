# Teacher onboarding — lang switcher + hybrid brands — 2026-07-21

updated=2026-07-21T15:00:00Z
branch=`agent/teacher-onboarding-lang-and-hybrid-brands-20260721`
worktree=`/Users/ahjan/phoenix_omega/.worktrees/teacher-ob-20260721`
github=`AUTH RESTORED (Pearl-Prime) — local commits only; do not push until operator asks`

## Applied operator defaults (loud)

| Q | Default applied |
|---|---|
| Q-BRAND-GEN-01 | Separate `config/brand_management/teacher_originated_brands.yaml` (never mutates 40×14) |
| Q-BRAND-GEN-02 | Deterministic seeded composition; **no LLM at build** |
| Q-BRAND-GEN-03 | Lazy hybrid gen on explicit accept only |
| Q-LANG-01 | No invite mech found → link from `pearl_prime_entry.html` Screen 3 |

## Signals

| Signal | SHA |
|--------|-----|
| `teacher-onboarding-flag-selector-landed` | `b9db18709508e72965b2a0ba9dfc5aa76fa6076d` |
| `teacher-owned-brand-generator-landed` | `55923199611675e4121f8952dd80bdfce634dd86` |
| `hybrid-brand-onboarding-routing-landed` | `c825129940a4fae1a970b5acd5e8541aa37187b0` |

Ancestral Phase A engine (flag gate + 14 locales) also at `f0faac8d2ed1ea511107dbcf07d39735b92d47ba`.

## Proofs

- Flag gate static: `artifacts/qa/teacher_onboarding_flag_selector_20260721/flag_gate_static_proof.txt`
- Smoke/pilot HTML: `artifacts/qa/teacher_onboarding_flag_selector_20260721/flag_gate_{smoke_en-US,pilot_ja-JP,pilot_zh-TW}.html` (+ PNG)
- Brand generator pilot: `artifacts/qa/teacher_brand_generator_pilot_20260721/` (`smoke_named_brand.json`, `pilot_brands.json`, `differentiation.json`, `smoke_hybrid_brand.json`, `name_occurrence_report.json`)
- Phase C A/B (reader-facing imprint): `artifacts/qa/hybrid_brand_onboarding_20260721/name_occurrence_report.json` — named name total>0, hybrid name total=0, `attribution_mode=generalized`, doctrine markers>0, **pass=true**
- Pytest: `tests/brand_generation/` → **7 passed** (requires `SOURCE_OF_TRUTH/teacher_banks` + `config/authoring` + `config/marketing` present — sparse worktree must `git sparse-checkout add` those)
- Vitest FlagLocaleGate: **4 passed**
- Locale key parity: 131 keys × 14 locales

## Phase contracts preserved

- Teacher exclusivity **409** unchanged; offer body adds `mode=generalized_hybrid` + `available_archetypes`
- Accept lazy via `POST /api/v1/onboarding/accept-hybrid` + CF `functions/api/onboarding/accept-hybrid.js`
- Hybrid cap **40** per teacher/lane; docstring 40×14
- Identity Language select retained as **source-language data field** (distinct from display locale)

## Resume note (2026-07-21 finish agent)

Prior finish agent had already MERGED A/B/C locally. This resume closed one honest proof gap:
`name_occurrence_report.json` previously recorded seed-divergence only; it now matches the
predecessor A/B pattern (named imprint carries teacher name; hybrid imprint carries zero).

CLOSEOUT: `artifacts/coordination/handoffs/teacher_onboarding_lang_and_hybrid_brands_2026-07-21_CLOSEOUT.md`

## Next (landing session)

```bash
cd /Users/ahjan/phoenix_omega/.worktrees/teacher-ob-20260721
git fetch origin && gh api user
# then BRAND_WIZARD_GITHUB_RETURN_REPLAY for predecessor pack if still needed, then:
git push -u origin agent/teacher-onboarding-lang-and-hybrid-brands-20260721
# then push-guard + preflight + pr_governance_review.py + open PR
```

Do **not** stage `.github/workflows/brand-admin-onboarding-pages.yml` or bestseller-lane dirty files from the main checkout.
