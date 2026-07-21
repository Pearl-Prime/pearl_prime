# Teacher onboarding — lang switcher + hybrid brands — 2026-07-21

updated=2026-07-21T07:20:00Z
branch=`agent/teacher-onboarding-lang-and-hybrid-brands-20260721`
github=`BLOCKED — gh api user → 401 Requires authentication (offline landing)`

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
| `hybrid-brand-onboarding-routing-landed` | (Phase C commit — see CLOSEOUT) |

Ancestral Phase A engine (flag gate + 14 locales) also at `f0faac8d2ed1ea511107dbcf07d39735b92d47ba`.

## Proofs

- Flag gate static: `artifacts/qa/teacher_onboarding_flag_selector_20260721/flag_gate_static_proof.txt`
- Smoke/pilot HTML: `artifacts/qa/teacher_onboarding_flag_selector_20260721/flag_gate_{smoke_en-US,pilot_ja-JP,pilot_zh-TW}.html`
- Brand generator pilot: `artifacts/qa/teacher_brand_generator_pilot_20260721/` (`smoke_named_brand.json`, `pilot_brands.json`, `differentiation.json`, `smoke_hybrid_brand.json`, `name_occurrence_report.json`)
- Pytest: `tests/brand_generation/` → 7 passed
- Locale key parity: 131 keys × 14 locales

## Phase contracts preserved

- Teacher exclusivity **409** unchanged; offer body adds `mode=generalized_hybrid` + `available_archetypes`
- Accept lazy via `POST /api/v1/onboarding/accept-hybrid` + CF `functions/api/onboarding/accept-hybrid.js`
- Hybrid cap **40** per teacher/lane; docstring 40×14
- Identity Language select retained as **source-language data field** (distinct from display locale)

## Next (when GitHub auth restored)

```bash
git fetch origin && gh api user
# then BRAND_WIZARD_GITHUB_RETURN_REPLAY for predecessor pack, then:
git push -u origin agent/teacher-onboarding-lang-and-hybrid-brands-20260721
```
