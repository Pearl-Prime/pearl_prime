# zh-CN Wave 1 Shard 05 — Skip Report

Shard file: `wave1_shard_05.jsonl` (20 atoms, gen_z_student/compassion_fatigue +
nyc_executives/compassion_fatigue). Translated via DashScope Qwen3.7-max
(Singapore intl endpoint), validated with
`scripts/localization/translation_quality/structural_validator.py` +
`script_contamination.py` (zh-CN watchlist).

17/20 atoms accepted. 3 skipped:

## 1. `atoms/gen_z_student/compassion_fatigue/comparison/CANONICAL.txt`
- item_id: `974be28425d9`
- reason: **source_missing** — this English source path does not exist on
  `origin/main` (`git show origin/main:atoms/gen_z_student/compassion_fatigue/
  comparison/CANONICAL.txt` → "exists on disk, but not in origin/main"). The
  shard worklist references a path that was never landed as a real atom.
  Blocker for atom authoring, not translation — reporting per instructions
  rather than inventing content.

## 2. `atoms/nyc_executives/compassion_fatigue/HOOK/CANONICAL.txt`
- item_id: `bf3cf11d173f`
- reason: validation failed after one repair attempt —
  `script_contamination` on block `HOOK_v20`: candidate used the
  Hong-Kong-register term "的士" (forbidden per
  `analysis/zh_cn/regional_usage_watchlist.yaml`; Mainland preferred term is
  "出租车"). The repair pass did not remove it. Skipped per protocol rather
  than hand-patching.

## 3. `atoms/nyc_executives/compassion_fatigue/REFLECTION/CANONICAL.txt`
- item_id: `37bec4433762`
- reason: validation failed after one repair attempt — structural drift in
  the back half of a long (30-variant) file: duplicate header IDs
  (`REFLECTION_v16`..`v25` repeated), delimiter-count mismatches
  (source=3 vs candidate=2 on v16–v25; source=1 vs candidate=2 on several
  earlier odd-numbered variants), and `untranslated_english` on several
  blocks. This looks like the model losing track of block boundaries on a
  long multi-variant source rather than a glossary/register issue — repair
  attempt did not resolve it. Skipped per protocol rather than hand-patching.

## DashScope spend (this shard)

- Total calls across both process runs: 12 (initial run, crashed on a
  transient network error mid-repair) + 16 (resume run) = 28 calls.
- Total estimated cost: ~$0.054 (run 1, before crash) + ~$0.125 (resume run)
  = **~$0.179 USD** (qwen3.7-max estimated per-1K-token rate).
- Well under the ~45-call soft cap for this shard.
