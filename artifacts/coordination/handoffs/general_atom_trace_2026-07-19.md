# Handoff — General atom trace tool (2026-07-19)

```
CLOSEOUT_RECEIPT
AGENT=Pearl_Dev_general_atom_trace
TOOL=scripts/qa/render_atom_trace.py
FORMAT_MATCHES_CH1_HARNESS=yes — spot-checked HOOK / ANGLE_DEFINITION / STORY on flagship
RUNS_ON=artifacts/qa/proprime_accent_flagship_proof_2026-07-11 (gen_z×anxiety, 120/121 resolved) + artifacts/qa/pearl_prime_next_micro_wave_20260716/corporate_managers__boundaries__false_alarm__F006 (110/122 resolved) — zero hardcoding
WIRED_INTO_PIPELINE=yes: --render-book auto-emits human_atom_trace.txt (WARN-on-error, does not fail render)
TESTS=4 (tests/test_render_atom_trace.py)
USAGE=PYTHONPATH=. python3 scripts/qa/render_atom_trace.py <render_dir>
ACCEPTANCE_LAYER=system working (proven on real render dirs)
LANDED=offline/general-atom-trace-20260719@6ce6002405cb63fcac2861df7cef39eb90c9973e
CLEANUP_COMPLETE=yes
HANDOFF=artifacts/coordination/handoffs/general_atom_trace_2026-07-19.md
SIGNAL=general-atom-trace=6ce6002405cb63fcac2861df7cef39eb90c9973e
NEXT_ACTION=operator runs it on any book's render dir to QA atoms (name→source→text); replay on github-suspension-lifted
```

## What shipped

- `scripts/qa/render_atom_trace.py` — post-render tool; reads `section_packet_audit.json` + `book.txt` (+ `plan.json` for persona/topic); writes `human_atom_trace.txt`.
- Format reuses Ch1/Ch2 human atom trace field labels (What this surface does / Source / Atom / Status / First rendered sentence / Previous beat / Cohesion/read note). Unresolvable sources emit `<unresolved:…>` — never fabricated.
- Optional pipeline wire in `scripts/run_pipeline.py` immediately after SPA write (always attempt, WARN on error).
- Proof: `artifacts/qa/general_atom_trace_20260719/`.
- Pytest: `tests/test_render_atom_trace.py`.

## CLEANUP LEDGER

| Item | Status |
|------|--------|
| Temp GIT_INDEX_FILE `/tmp/gat_idx*` | removed after land |
| `/tmp/po_clean` scratch (sparse origin/main extracts) | removed after land |
| No `git add -A` | honored — explicit paths only |
| Working-tree dirty codex branch | untouched as build base; land is off `origin/main` |
| Generated traces under existing render dirs | left local; proof copies under `artifacts/qa/general_atom_trace_20260719/` |

## GitHub

Account suspended (403). Landed offline only. Replay push/PR when suspension lifts.
