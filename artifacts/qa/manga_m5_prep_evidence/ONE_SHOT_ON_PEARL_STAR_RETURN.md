# One-shot when Pearl Star returns

```bash
# 1. Confirm queue RUNNING (RAP)
pscli status   # or ssh … pscli status

# 2. Enqueue REAL layers (LOW priority, CJK preempts)
bash artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/assembled/m5_prep_stillness_REAL_INTERIM_proof/../demo_alarm_metaphor_6p/RESUME_COMMANDS.sh
# (or per-series RESUME under assembled/m5_prep_wiring_proof_INTERIM/)

# 3. After REAL assets land, re-assemble with provenance: REAL
PYTHONPATH=. python3 scripts/manga/assemble_from_bank.py \
  --manifest artifacts/manga/<series>/assembly_manifests/<real>.yaml \
  --out-dir artifacts/manga/<series>/assembled/<real>/ --strip --bubbles
```

Budget: OPD-20260704-007 — ~2–4 GPU-h LOW-priority pilot total.
