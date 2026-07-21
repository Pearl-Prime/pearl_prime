# Teacher onboarding full-reqs 100% — 2026-07-20

updated=2026-07-20T23:51:38Z

## Signals

| Signal | SHA / status |
|--------|----------------|
| `teacher-onboarding-flag-selector-landed` | `f0faac8d2e` (+ FlagLocaleGate vitest green this session) |
| `teacher-onboarding-i18n-14-of-14-landed` | `c2a7b9e372` / fix `4f4750327c` (131 keys × 14; CJK empty body_prefix allowed) |
| `teacher-owned-brand-generator-landed` | this tip (engine + registry + pytest 7/7) |
| `hybrid-brand-onboarding-routing-landed` | this tip (409 offer + `/accept-hybrid` + CF + wizard UI) |
| Storyblocks social bank seed | EXECUTED-REAL — 3 video + 3 image under `artifacts/storyblocks_licensed/social_media_bank_storyblocks_20260720/` |
| GitHub push/PR | **BLOCKED** — account suspended (403) |

## Proofs

- `PYTHONPATH=. python3 -m pytest tests/brand_generation/ -q` → **7 passed**
- `npm test -- --run FlagLocaleGate` → **4 passed**
- `node brand-wizard-app/scripts/check_teacher_onboarding_locales.mjs` → 14 OK (empty `success.body_prefix` allowlisted)
- `node brand-wizard-app/scripts/check_teacher_onboarding_flag_gate.mjs` → OK

## Phase C contract

- 409 `teacher_claimed` trigger unchanged; body adds `offer.mode=generalized_hybrid` + `available_archetypes`
- Accept is lazy: `POST /api/v1/onboarding/accept-hybrid` (FastAPI) and CF `functions/api/onboarding/accept-hybrid.js`
- Cap 40 hybrids per teacher/lane; `hybrid_already_exists` / `hybrid_cap_reached` are 409s
- Cloudflare `/teacher_onboarding` draft backend has **no** exclusivity ledger — hybrid 409 path is brand-wizard FastAPI/CF onboarding submit

## Q-TRANS / Q-BRAND defaults applied

- Q-TRANS-01: UI JSON standalone (key-parity script only)
- Q-TRANS-02: teacher doctrine atoms out of scope
- Q-BRAND-GEN-01: additive `teacher_originated_brands.yaml` (not 40×14)
- Q-BRAND-GEN-03: lazy hybrid generation

## Next

```
git fetch origin && gh api user
# when live:
git push -u origin agent/teacher-onboarding-lang-and-hybrid-brands-20260720
gh pr list --search "teacher onboarding" --state all
```
