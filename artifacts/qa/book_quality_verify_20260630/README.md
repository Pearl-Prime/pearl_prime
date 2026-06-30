# Assembled-Book Quality Verification — 2026-06-30

Durable evidence for the plan-scale sellability verification (Pearl_Research + Pearl_Editor).
GPU-free scoring; no Ollama invoked.

## Artifacts

| File | Purpose |
|------|---------|
| `DISCOVERY.md` | Book-set inventory, EI dimension mapping, prior art |
| `SCORECARD.tsv` / `SCORECARD.md` | Per-cell scores and leakage verdicts |
| `SELLABILITY_ROLLUP.md` | Operator rollup + recommended actions |
| `scores.json` / `scores_final.json` | Machine-readable score rows |

## pilot_10 stub cells — do-not-ship / superseded

Three `artifacts/pearl_prime/pilot_10/` renders from PR **#3605** leaked HOOK atom
square-bracket stubs (`[Persona-specific hook for …]`) yet passed the pre-fix
`delivery_contract_gate`. **Do not ship these cells.** Use `artifacts/wave_proof/`
rebuilds for the same persona×topic pairs (clean HOOK prose).

| Cell | Status | Superseded by |
|------|--------|---------------|
| `02_gen_z_professionals__burnout` | **do-not-ship** | `wave_proof/draft/burnout_grief__gen_z_professionals` (and siblings) |
| `04_corporate_managers__burnout` | **do-not-ship** | `wave_proof/draft/burnout_grief__corporate_managers` |
| `05_corporate_managers__financial_anxiety` | **do-not-ship** | wave_proof clean cell when assembled post-flip |

Gate hardening to block these stubs: delivery-gate stub-catch PR (pre-flip Jul 1).
