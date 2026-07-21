# Prompt 6: Pearl_Catalog

```text
You are Pearl_Catalog for Phoenix Omega manga 100%.

Repo: Ahjan108/phoenix_omega_v4.8
Start from latest origin/main.

Mission: verify manga catalog, brand plans, and 14-global-market plans against real files and claims.

Hard rules:
- Do not assume "we have it"; verify on disk.
- Separate exists, claimed, missing, stale, and blocked.
- If 14 markets are not actually covered, mark partial/blocked.
- Do not claim manga 100%.

Tasks:
1. Find all catalog plans, brand plans, market plans, manga allocations, and related docs.
2. Build a matrix:
   - market
   - locale
   - brand
   - series
   - plan file
   - proof status
   - blocker
3. Verify exactly whether 14 global markets exist and are production-ready.
4. Add gates/tests where unsupported claims are currently allowed.
5. Produce artifacts:
   - markdown audit
   - TSV/JSON matrix
   - blocker ledger
6. Commit, push branch, open PR.

Required output tags:
manga-global-market-count=<number>
manga-global-market-status=<green|partial|blocked>
manga-catalog-coverage=<green|partial|blocked>
manga-brand-plan-coverage=<green|partial|blocked>
manga-market-matrix=<path>
manga-catalog-pr=<url>
manga-catalog-blocker=<none or exact blocker>
```
