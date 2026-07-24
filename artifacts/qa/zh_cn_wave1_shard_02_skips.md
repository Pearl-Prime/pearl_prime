# zh-CN Wave 1 — Shard 02 Skip Report

Shard file: `wave1_shard_02.jsonl` (20 atoms assigned)

## Summary

- Attempted: 20
- Translated & accepted: 15
- Skipped (EN-source corrupted, blocker reported per instructions): 4
- Skipped (out of shard scope by mistake — see note): 1

## Skipped atoms — EN-source structurally corrupted

The following English `CANONICAL.txt` source files contain a stub-index
corruption pattern in their early `RECOGNITION`/`MECHANISM_PROOF`/
`TURNING_POINT`/`EMBODIMENT` v01–v05/v22 blocks: the block's frontmatter is
followed immediately by the **next block's bare header name as plain text**
(no `##` prefix, no body prose) instead of authored English content, e.g.:

```
## RECOGNITION v01
---
path: ...
BAND: 2
...
---
RECOGNITION v02
---

## RECOGNITION v03
...
```

This is not a translation problem — there is no English content to translate
for these blocks. Per the shard brief ("If the English source is malformed,
report the blocker rather than inventing missing meaning"), these atoms were
NOT translated and NOT hand-patched. They should route to EN-source authoring
remediation (matches the existing backlog referenced in
`docs/`/commit 386bf02bef "atom authoring backlog for EN-source-corrupted
atoms (650 rows)").

| item_id | source_path | reason |
|---|---|---|
| 5a54653003ea | atoms/working_parents/compassion_fatigue/watcher/CANONICAL.txt | RECOGNITION v01-05, MECHANISM_PROOF v01-05, TURNING_POINT v01-05, EMBODIMENT v01-05 are bare-header stubs (no authored body) |
| 3eca3fd3a60f | atoms/working_parents/compassion_fatigue/overwhelm/CANONICAL.txt | same stub-index corruption pattern as watcher above |
| 245eb4cb7e80 | atoms/working_parents/compassion_fatigue/grief/CANONICAL.txt | same stub-index corruption pattern |
| e52c1398462e | atoms/gen_alpha_students/compassion_fatigue/spiral/CANONICAL.txt | RECOGNITION v02/v04, MECHANISM_PROOF v01/v03/v05, TURNING_POINT v02/v04, EMBODIMENT v01/v03/v05 are bare-header stubs |

Verified clean (same shape family, same persona/topic) as a control check:
`working_parents/compassion_fatigue/spiral`, `working_parents/compassion_fatigue/false_alarm`,
`gen_alpha_students/compassion_fatigue/watcher`, `gen_alpha_students/compassion_fatigue/overwhelm`,
and `gen_alpha_students/compassion_fatigue/grief` all have fully authored English
prose throughout — only the four files above are corrupted. Corruption is
file-specific, not engine-name-specific.

## Accepted atoms (15) — DashScope qwen3.7-max, structural + script-contamination validated

All 15 passed `structural_validator.py` and `script_contamination.py`
(zh-CN watchlist) with 0 open findings after one round of terminology repair
(see below). No repair-state escalation to `targeted_repair_2` /
`fresh_regeneration` / `quarantine` was needed for any of the 15 — all
resolved at the "initial candidate + manual terminology/script fix" stage.

| item_id | locale path |
|---|---|
| c62c8f727037 | atoms/gen_x_sandwich/compassion_fatigue/HOOK/locales/zh-CN/CANONICAL.txt |
| 2138ec5da380 | atoms/gen_x_sandwich/compassion_fatigue/STORY/locales/zh-CN/CANONICAL.txt |
| c3809a261e3d | atoms/gen_x_sandwich/compassion_fatigue/REFLECTION/locales/zh-CN/CANONICAL.txt |
| daecaef1fa6c | atoms/gen_x_sandwich/compassion_fatigue/TAKEAWAY/locales/zh-CN/CANONICAL.txt |
| 6a297499f0e7 | atoms/working_parents/compassion_fatigue/INTEGRATION/locales/zh-CN/CANONICAL.txt |
| 2e70a6603fdd | atoms/working_parents/compassion_fatigue/spiral/locales/zh-CN/CANONICAL.txt |
| bdb174ac59e5 | atoms/working_parents/compassion_fatigue/false_alarm/locales/zh-CN/CANONICAL.txt |
| 32ae47c584d9 | atoms/working_parents/compassion_fatigue/shame/locales/zh-CN/CANONICAL.txt |
| f3d0cf12d918 | atoms/working_parents/compassion_fatigue/COMPRESSION/locales/zh-CN/CANONICAL.txt |
| 4c1057772a38 | atoms/working_parents/compassion_fatigue/comparison/locales/zh-CN/CANONICAL.txt |
| efada165b997 | atoms/working_parents/compassion_fatigue/REFLECTION/locales/zh-CN/CANONICAL.txt |
| e395f4c392f2 | atoms/gen_alpha_students/compassion_fatigue/PIVOT/locales/zh-CN/CANONICAL.txt |
| ef9af739e310 | atoms/gen_alpha_students/compassion_fatigue/watcher/locales/zh-CN/CANONICAL.txt |
| ecd621693078 | atoms/gen_alpha_students/compassion_fatigue/INTEGRATION/locales/zh-CN/CANONICAL.txt |
| 7bcfb2b10262 | atoms/gen_alpha_students/compassion_fatigue/overwhelm/locales/zh-CN/CANONICAL.txt |
| 83ea7ca46be5 | atoms/gen_alpha_students/compassion_fatigue/grief/locales/zh-CN/CANONICAL.txt |

## Post-generation manual repair applied (cross-shard finding)

A cross-shard finding (shard 04 / PR #101) reported that `structural_validator.py`
only enforces `glossary_core.yaml`/`glossary_project.yaml` **avoid**-lists,
not **preferred/locked** forms, so DashScope drifted to colloquial synonyms
for the locked critical_recurring term "compassion fatigue" on a meaningful
fraction of files. This shard's outputs were audited against
`analysis/zh_cn/glossary_project.yaml` and repaired accordingly before
acceptance:

- `同情疲劳` / `同情心疲劳` / `共情疲劳` → locked `共情耗竭` ("compassion fatigue")
  — found in 11 of the 15 accepted files, all fixed.
- `共情枯竭` / `共情储备耗尽` → locked `共情耗尽` ("empathy tank empty" motif)
  — found in 2 files, fixed.
- `超出承受极限的关怀` / `只付出而无补充的状态/感觉` → locked `关心超出了承受范围` /
  `只出不进的付出` ("caring past capacity" / "giving without refill" motifs,
  gen_x_sandwich/STORY only) — fixed.
- `身份` (bare, self-concept sense — glossary_core.yaml avoid-list item,
  preferred `自我认同`) — found across 9 files (mostly compound `身份认同`),
  contextually rewritten to `自我认同`/`自我认同代价` etc. rather than a naive
  blanket substitution, to keep sentences grammatical.
- Traditional-script leakage (`裡` instead of Simplified `里`) — found in 2
  `INTEGRATION` files, fixed.
- One missing closing `---` delimiter (structural, not terminology) —
  `gen_alpha_students/compassion_fatigue/grief` `MECHANISM_PROOF_v07` was
  truncated at end-of-file by the client's max-token completion; delimiter
  restored.

All fixes were verified by re-running `structural_validator.py` and
`script_contamination.py` — all 15 files show 0 open findings after repair.

## DashScope spend

See `artifacts/qa/translation_quality_cost_log_<date>.jsonl` cost log
entries for this run (qwen3.7-max, 15 calls, one per full atom file —
no retries needed at the DashScope-call level; all repair was manual
terminology/script post-processing, not additional model calls).
