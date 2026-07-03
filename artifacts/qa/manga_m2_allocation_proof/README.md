# M2 Allocation Proof

Exit proof for Roadmap M2 (R1 allocation chain).

| Artifact | Role |
|---|---|
| `catalog_plan_BEFORE_global_matrix.md` | Generator run with `--no-allocations` (identical mix every locale) |
| `catalog_plan_AFTER_allocation_derived.md` | Generator run consuming `config/manga/locale_genre_allocations.yaml` |
| `GENRE_DISTRIBUTION_DIFF.md` | Before/after genre-mix comparison (the verifiable proof) |
| `C1_C2_STANDDOWN_VS_PR2795.md` | Item-3 stand-down vs open PR #2795 |

**Not committed:** mass-regenerated per-locale series plans (M7 Wave A).

Reproduce:

```bash
PYTHONPATH=. python3 scripts/manga/generate_catalog_plan_from_strategic.py \
  --no-allocations -o artifacts/qa/manga_m2_allocation_proof/catalog_plan_BEFORE_global_matrix.md
PYTHONPATH=. python3 scripts/manga/generate_catalog_plan_from_strategic.py \
  -o artifacts/qa/manga_m2_allocation_proof/catalog_plan_AFTER_allocation_derived.md
```
