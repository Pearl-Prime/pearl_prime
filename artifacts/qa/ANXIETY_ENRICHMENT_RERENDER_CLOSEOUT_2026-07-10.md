# Anxiety Enrichment Contract-v1 Closeout — 2026-07-10

**Agent:** Pearl_Dev  
**Project:** `proj_pearl_prime_bestseller_rebase_20260425`  
**Subsystem:** pearl_prime; core_pipeline  
**Acceptance layer:** **CODE-WIRED + EXECUTED-REAL** (contract-v1 composite proof; not Layer-4 blind register)

---

## Discovery reconciliation (live)

| Check | Live truth |
|---|---|
| `origin/main` SHA | `4067366556fedfd99913fbd3806d78af53d32b5a` |
| PR #5490 / #5492 overlap | **`scripts/run_pipeline.py` only** |
| Anxiety banks | **18 RQ + 18 TS** entries, YAML parse OK |
| Contract-v1 bundle | **regenerated in-turn** at `artifacts/rendered/cli_demo_trace_run_composite_contract_v1/` |
| Stash recovered | `stash@{1}` message `anxiety-contract-v1-wip` informed parity-safe legacy planner split; not blindly applied |
| Default flagship parity | **BYTE-IDENTICAL** (`sha256=88fcff84…`, seed `flagship_phase2_layer6`) |

### PR #5490 disposition (`run_pipeline.py` overlap)

**Survivor: PR #5492.** Minimum #5490 hunks **absorbed** into #5492:

- `--pipeline-mode` default **`spine`** (already present)
- `_guard_legacy_registry_mode()` + `--allow-legacy-registry` (absorbed in-turn)

**#5490 partially superseded** for `run_pipeline.py` ownership. Remaining independent value on #5490 (docs index, debug-script moves, `test_spine_pipeline_integration` help assertions) is **out of lane scope** and may stay open without competing on the shared file.

---

## CLOSEOUT_RECEIPT

| Field | Value |
|---|---|
| **commit SHA** | _see post-push git log_ |
| **branch** | `agent/anxiety-enrichment-contract-v1-20260710` |
| **PR URL** | https://github.com/Ahjan108/phoenix_omega_v4.8/pull/5492 |
| **merge SHA** | _pending squash-merge_ |
| **stash used** | `stash@{1}: anxiety-contract-v1-wip` (reference only; legacy planner parity path already on branch) |
| **proof bundle** | **regenerated** (not reused from stale disk claims) |

### Files changed (lane scope)

- `phoenix_v4/planning/accent_planner.py` — contract-v1 opt-in planner + legacy parity path
- `scripts/run_pipeline.py` — contract-v1 isolation, book_idea/motif, underfill gate, registry guard (#5490 minimum)
- `phoenix_v4/qa/assembly_trace.py` — assembly trace writer
- `tests/planning/test_accent_planner.py` — anxiety pilot tests
- `SOURCE_OF_TRUTH/accent_banks/reflection_questions/anxiety/entries.yaml`
- `SOURCE_OF_TRUTH/accent_banks/troubleshooting/anxiety/entries.yaml`
- `artifacts/qa/ANXIETY_ENRICHMENT_RERENDER_CLOSEOUT_2026-07-10.md`
- `artifacts/rendered/cli_demo_trace_run_composite_contract_v1/*`

### Tests run

```bash
PYTHONPATH=. python3 -m pytest tests/planning/test_accent_planner.py -q
# 7 passed

PYTHONPATH=. python3 scripts/ci/check_flagship_book_parity.py --snapshot all \
  --ch1-from-file /tmp/flagship_parity_test/book.txt \
  --full-from-file /tmp/flagship_parity_test/book.txt
# BYTE-IDENTICAL ch1 + full book
```

### Render commands

**Contract-v1 proof (composite path, explicit opt-in via render-dir suffix):**

```bash
PYTHONPATH=. python3 scripts/run_pipeline.py \
  --topic anxiety \
  --persona gen_z_professionals \
  --arc config/source_of_truth/master_arcs/gen_z_professionals__anxiety__overwhelm__F006.yaml \
  --pipeline-mode spine \
  --runtime-format extended_book_2h \
  --quality-profile production \
  --exercise-journeys \
  --no-job-check \
  --render-book \
  --render-dir artifacts/rendered/cli_demo_trace_run_composite_contract_v1 \
  --seed cli_demo_trace_run_composite_contract_v1
```

**Default flagship parity (contract-v1 OFF):**

```bash
PYTHONPATH=. python3 scripts/run_pipeline.py \
  --topic anxiety --persona gen_z_professionals \
  --arc config/source_of_truth/master_arcs/gen_z_professionals__anxiety__overwhelm__F006.yaml \
  --pipeline-mode spine --runtime-format extended_book_2h \
  --quality-profile production --exercise-journeys --no-job-check \
  --render-book --render-dir /tmp/flagship_parity_test --seed flagship_phase2_layer6
```

### Proof signals

| Signal | Value |
|---|---|
| `REFLECTION_QUESTION` landed | **3** (`rq_anxiety_gen_z_professionals_02` ch3, `_15` ch11, `_10` ch12) |
| `TROUBLESHOOTING` landed | **1** (`ts_anxiety_gen_z_professionals_07` ch3) |
| supported underfill (RQ/TS) | **0** |
| provenance (RQ/TS) | **authored_bank** |
| `book_idea` | `prediction-as-evidence swap` |
| `book_motif` | `The Alarm (chest and phone)` |
| `contract_id` | `cli_demo_trace_run_composite_contract_v1` |
| default flagship parity | **BYTE-IDENTICAL** |

### Visible in `book.txt` + trace

- RQ: `When the chest tightens before the meeting starts, what prediction are you treating as evidence?`
- TS: `When the practice wobbles, this is what to do next. When this happens in a meeting…`
- `assembly_trace.md`: RQ/TS rows with `authored_bank` supply
- `supported_underfilled_budget_by_class: {}`

---

## Cleanup ledger

- [x] Survivor PR #5492; #5490 `run_pipeline.py` overlap resolved via minimum absorb + explicit supersede note
- [x] Contract-v1 proof regenerated; default flagship parity verified byte-identical
- [x] No parallel enrichment engine; no cross-persona bank borrowing
- [ ] Squash-merge pending CI green

---

## Required signals

```
anxiety-enrichment-contract-v1=<merge-sha-after-push>
anxiety-enrichment-contract-v1-render=/Users/ahjan/phoenix_omega/artifacts/rendered/cli_demo_trace_run_composite_contract_v1
anxiety-enrichment-contract-v1-rq-landed=3
anxiety-enrichment-contract-v1-ts-landed=1
anxiety-enrichment-contract-v1-underfill=0
anxiety-enrichment-contract-v1-default-parity=byte-identical
anxiety-enrichment-contract-v1-pr-survivor=5492
anxiety-enrichment-contract-v1-pr-superseded=5490-partial-run_pipeline-only
anxiety-enrichment-contract-v1-blocker=none
```
