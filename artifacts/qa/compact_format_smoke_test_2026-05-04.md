# Compact Format & Atom Backfill Smoke Test — 2026-05-04

Branch: `agent/pearl-writer-compact-formats-genz-anxiety-20260504`
Operator: present (Tier 1)

## What this PR ships (content only)

| Deliverable | Status | Lines | Notes |
|---|---|---:|---|
| `docs/COMPACT_BOOK_FORMAT_SPECS_2026-05-04.md` | NEW | 460 | Spec doc — 3 compact runtime formats (5ch/15min, 5ch/20min, 8ch/30min). Wiring deferred to follow-up engineering PR. |
| `docs/TEACHER_DOCTRINE_ATOM_CONVENTION_2026-05-04.md` | NEW | 141 | Establishes `atoms/<persona>/<topic>/TEACHER_DOCTRINE/CANONICAL.txt` convention. Wiring deferred. |
| `atoms/gen_z_professionals/anxiety/TEACHER_DOCTRINE/CANONICAL.txt` | NEW | 56 | 5 variants × 5 distinct mechanisms |
| `atoms/gen_z_professionals/burnout/TEACHER_DOCTRINE/CANONICAL.txt` | NEW | 56 | 5 variants × 5 distinct mechanisms |
| `atoms/gen_z_professionals/imposter_syndrome/TEACHER_DOCTRINE/CANONICAL.txt` | NEW | 60 | 5 variants × 5 distinct mechanisms |
| `atoms/gen_z_professionals/sleep_anxiety/TEACHER_DOCTRINE/CANONICAL.txt` | NEW | 60 | 5 variants × 5 distinct mechanisms |
| `atoms/gen_z_professionals/financial_anxiety/TEACHER_DOCTRINE/CANONICAL.txt` | NEW | 60 | 5 variants × 5 distinct mechanisms |
| `atoms/gen_z_professionals/anxiety/HOOK/CANONICAL.txt` | UPDATE | 386 → 662 | +25 thesis-line variants (v56–v80) for chapter_target 1/3/8/11/12 |
| `atoms/gen_z_professionals/anxiety/PIVOT/CANONICAL.txt` | UPDATE | 234 → 305 | +10 transition variants (v34–v43) for chapter_target 2/12 |
| `atoms/gen_z_professionals/anxiety/INTEGRATION/CANONICAL.txt` | UPDATE | 252 → 338 | +5 closer actionable-step variants (v26–v30) for chapter_target 12 |

Total: 25 new TEACHER_DOCTRINE atom blocks + 40 new chapter-flow atom blocks + 2 new docs + 1 smoke-test summary (this file).

## Failure-class diagnosis (evidence-grounded)

Source: `/tmp/pearl_prime_runs/{micro_book_15, micro_book_20_draft, short_book_30_draft, standard_book, extended_book_2h, deep_book_4h, deep_book_6h}/`

| Failure class | Affected formats | Evidence |
|---|---|---|
| `EnrichmentGapError: TEACHER_DOCTRINE chapter=2 slot_index=5` | standard_book, extended_book_2h, deep_book_4h, deep_book_6h | stderr.log on each (no rendered book.txt produced) |
| Word band overrun | micro_book_15 (+43.4%), micro_book_20 (+42.5%), short_book_30 (+15.6%) | `book_pass_report.json:word_budget=FAIL` |
| chapter_flow MISSING_CLEAR_POINT | 4 chapters in micro_book_20 | `chapter_flow_report.json` |
| chapter_flow WEAK_TRANSITIONS | 1+ chapters | `chapter_flow_report.json` |

## Validator results (post-PR)

```
$ PYTHONPATH=. python3 scripts/registry/validate_variant_coverage.py \
    --strict --persona gen_z_professionals \
    --topic anxiety --topic burnout --topic imposter_syndrome \
    --topic sleep_anxiety --topic financial_anxiety
variant-coverage: registry passed=1350 gaps=0; atoms passed=55 gaps=0;
total_gaps=0; min_variants=3; mode=strict
```

`atoms passed=55` reflects the new TEACHER_DOCTRINE blocks visible to the validator. **0 gaps** for the 5 backfilled topics.

## Smoke test: spine pipeline mode

Command:
```
PYTHONPATH=. python3 scripts/run_pipeline.py \
  --arc config/source_of_truth/master_arcs/gen_z_professionals__anxiety__overwhelm__F006.yaml \
  --topic anxiety --persona gen_z_professionals \
  --workspace /tmp/smoke_spine_2026-05-04 \
  --pipeline-mode spine --quality-profile production \
  --render-book --render-dir /tmp/smoke_spine_2026-05-04 \
  --out /tmp/smoke_spine_2026-05-04/plan.json --seed 20260504 --no-job-check
```

Result:
- ✅ Pipeline progressed past `chapter=2 slot_index=5` (the TEACHER_DOCTRINE slot that previously raised `EnrichmentGapError` on standard_book / extended_book_2h / deep_book_*). No EnrichmentGapError fired.
- ⚠️ Pipeline halted at scene_anchor_density gate (`Scene anchor density cap: FAIL — repeated >3-word phrases exceed cap 2`). This is unrelated to the atoms shipped in this PR; it's a separate pre-existing gate condition.
- chapter_flow / book_pass / bestseller_craft gates not reached because of the upstream halt.

## What this smoke test does and does not prove

**Proves:**
- TEACHER_DOCTRINE atoms exist on disk in the convention path and pass variant-coverage validation.
- Pipeline does not raise the originally-diagnosed `EnrichmentGapError: TEACHER_DOCTRINE` on the gen_z_professionals × anxiety triple under at least one master arc.
- HOOK / PIVOT / INTEGRATION backfill compiles cleanly (no syntax error or schema-rejection at registry resolution).

**Does NOT prove (deferred to follow-up engineering PR per K7=C):**
- TEACHER_DOCTRINE atoms are loaded from the new persona-source path. The original gap may close because of a different code path (registry fallback, master-arc routing differences) rather than because the new atoms are loadable. Confirming this requires either: (a) reproducing the original failure on a `__grief__F006` arc that hits chapter_2 slot_index_5 unambiguously, or (b) extending `phoenix_v4/planning/enrichment_select.py` persona-source lookup to read `atoms/<persona>/<topic>/TEACHER_DOCTRINE/CANONICAL.txt` and observing it succeed.
- Compact runtime formats render. The `compact_book_5ch_*` and `compact_book_8ch_30min` formats are spec-only in this PR; their wiring lives in the follow-up engineering PR scope (extend `_max_extra_chunks_for_format`, beatmap word targets, `book_quality_gate.yaml` runtime_policies, plus the format declaration itself).
- chapter_flow gate pass/fail counts shift. The gate was not reached in the smoke run; full validation requires the scene_anchor_density gate to also pass on the smoke arc, which is out of scope for this PR.

## Follow-up engineering PR scope

Deferred per operator decision K7=C:

1. `phoenix_v4/planning/enrichment_select.py` — extend persona-source lookup to read `atoms/<persona>/<topic>/TEACHER_DOCTRINE/CANONICAL.txt` when the resolver's persona path is taken. Map `mode: SECULAR_BRIDGE` to persona-source eligibility.
2. `phoenix_v4/planning/enrichment_select.py::_max_extra_chunks_for_format` — add `compact_book_5ch_15min`, `compact_book_5ch_20min`, `compact_book_8ch_30min` runtime keys with appropriate per-section budgets.
3. `phoenix_v4/planning/beatmap_compile.py` — extend `TEACHER_DOCTRINE` word target to be runtime-aware (460 → ~80–120 for compact runtimes).
4. `config/format_selection/format_registry.yaml` (or new `runtime_formats.yaml`) — declare the 3 compact format YAML blocks per the spec doc.
5. `config/quality/book_quality_gate.yaml::runtime_policies` — add entries for the 3 compact runtimes.
6. Optional: investigate Batch 2 memorable-line polish on chapters that show TAKEAWAY warnings post-wiring.

## Validation receipts

- `git status` clean before push (only the 11 staged files + this summary)
- `scripts/registry/validate_variant_coverage.py --strict` shows 0 gaps for backfilled topics
- No production code edits in this PR (per brief constraint)
- No paid LLM API calls (Pearl_Writer = Claude Code subagents)
- Branch from `origin/main`, push-guard + preflight to be run pre-push
