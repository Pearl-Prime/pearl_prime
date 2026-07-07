# Phrase-Density Close — 2026-07-08

**Route:** generalized teacher-wrapper rotation after `books-100pct=cc52495d51`

**Closeout token:** `books-phrase-cap=<SHA>` (set after commit)

## Root cause

Composite-doctrine slots stamp **generalized-mode `intro_wrapper` prefixes** from `config/catalog_planning/teacher_wrapper_templates.yaml` as standalone paragraphs (~once per chapter). With only four variants — two sharing `{TRADITION} teaches that…` and one fixed `I came across this teaching tradition…` — book-wide 4–6-gram counts exceeded the gate cap (12).

Source family: `phoenix_v4/rendering/teacher_wrapper.py` + composite path in `phoenix_v4/planning/enrichment_select.py` (`apply_wrapper` with `_GENERALIZED_WRAPPER_SENTINEL`).

## Fix (code + config, no gate weakening)

1. **`WrapperUsageMemory`** — book-wide least-used variant selection with 4–6-gram load scoring (mirrors `practice_library_loader` chapter rotation).
2. **Wired through enrichment** — all `apply_wrapper` calls in `enrichment_select.py` share one `_book_wrapper_memory` per book.
3. **Template diversification** — split the shared `teaches that` n-gram cluster; reword variants that embedded `in the contemplative tradition`; add three TRADITION_SHORT–first variants.

**Allowlist changes:** none (`refrain_allowlist.yaml` untouched).

## Before → after (`cohesion_proof_20260708/after` vs phrase-density re-render, seed 4242)

| Cell | Before band | Before violations | After band | After violations |
|------|-------------|-------------------|------------|------------------|
| burnout_overwhelm × corporate_managers | Hold | 3 (top: `the contemplative tradition teaches that` ×14) | **Pass** | **0** |
| burnout_grief × gen_z_professionals | Hold | 20 (top: teaches-that cluster ×14; came-across cluster ×13) | **Pass** | **0** |
| burnout_overwhelm × healthcare_rns | Pass | 0 | **Pass** | **0** |

## Named cadence refrains (regression check)

| Refrain | All three cells after |
|---------|----------------------|
| Peel back the obvious… | **0** |
| Rest at this stop… | **0** |

## SELLABLE_AS_IS

None — this lane cleared **book_quality** phrase-density only. Tier-1 cohesive-flow / flagship register bar unchanged.

## Artifacts

- `artifacts/qa/phrase_density_proof_20260708/PROOF_REPORT.json`
- `artifacts/qa/phrase_density_proof_20260708/*.txt` (post-fix renders)
- Render dirs (full gate bundle): `/tmp/phrase_cap_{corporate_managers,gen_z_professionals,healthcare_rns}/`

## Files changed

- `phoenix_v4/rendering/teacher_wrapper.py`
- `phoenix_v4/planning/enrichment_select.py`
- `config/catalog_planning/teacher_wrapper_templates.yaml`
- `tests/unit/rendering/test_teacher_wrapper_phrase_rotation.py`
- `scripts/qa/run_phrase_density_proof_20260708.py`
