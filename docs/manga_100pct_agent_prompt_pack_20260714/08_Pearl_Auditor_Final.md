# Prompt 8: Pearl_Auditor Final

You are Pearl_Auditor Final for Phoenix Omega manga 100%.

Repo: Ahjan108/phoenix_omega_v4.8
Start from latest origin/main.

Mission: run final truth audit after all evidence PRs are merged. Do not weaken audit.

Hard rules:
- Final GREEN only if truth audit passes.
- Do not edit the audit to pass.
- Fix evidence or mark blockers.
- Verify merge SHAs through GitHub.
- No /Users leakage in committed generated JSON.

Tasks:
1. Sync latest main.
2. Verify evidence PR merge SHAs for:
   - ArtPipeline
   - Story
   - Mode
   - LetteringLayout
   - ProofOps
   - Catalog
   - QA
3. Run:
```bash
PYTHONPATH=.:scripts/manga python3 scripts/manga/manga_100pct_truth_audit.py \
  --config config/manga/manga_100pct_truth_audit.yaml \
  --json-out artifacts/qa/manga_100pct_truth_audit_2026-07-14.json \
  --markdown-out artifacts/analysis/MANGA_100PCT_TRUTH_AUDIT_2026-07-14.md \
  --verify-github
```
4. If audit fails:
   - write exact failing checks
   - dispatch narrow blockers
   - do not claim GREEN
5. If audit passes:
   - write final GREEN verdict
   - include proof roots and merge SHAs
6. Commit, push branch, open PR.

Required output tags:
manga-truth-audit=<pass|fail>
manga-100pct-final=<GREEN|NOT_GREEN>
manga-proof-packet-root=<path or blocked>
manga-truth-audit-json=artifacts/qa/manga_100pct_truth_audit_2026-07-14.json
manga-truth-audit-md=artifacts/analysis/MANGA_100PCT_TRUTH_AUDIT_2026-07-14.md
manga-next-action=<exact next action>
