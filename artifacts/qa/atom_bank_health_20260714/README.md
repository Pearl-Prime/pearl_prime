# Atom Bank Health Audit Outputs

Full repo-wide audit outputs are generated at runtime by:

```bash
PYTHONPATH=. python3 scripts/qa/audit_atom_bank_health.py \
  --out-dir artifacts/qa/atom_bank_health_20260714
```

The complete TSV/JSON/markdown scan outputs are intentionally not committed because they are large, regenerated artifacts and trip CI size guards. Keep the auditor implementation, tests, and closeout in Git; generate the full matrix locally or in CI artifacts when needed.
