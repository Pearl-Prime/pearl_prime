# zh-CN Wave 1 — Shard 04 skip report

Shard file: `wave1_shard_04.jsonl` (20 atoms, persona `gen_alpha_students`, topic `compassion_fatigue`).

Result: **0 skipped / 20 accepted.**

All 20 atoms translated via DashScope Qwen (`qwen3.7-max`, Singapore intl
endpoint) and passed `structural_validator.py` (headers, delimiters,
placeholders, script-contamination, numbers, protected terms) on the
first attempt — no repair-loop invocations were needed.

One manual correction applied post-validation (not caught by the
automated validator, since it only checks glossary `avoid`-lists, not
locked `preferred` terms): 6 of the 20 files rendered "compassion fatigue"
as 同情疲劳 (a valid secondary/colloquial form per
`analysis/zh_cn/glossary_core.yaml`) instead of the
`analysis/zh_cn/glossary_project.yaml`-locked critical_recurring term
共情耗竭. Since this whole shard is the `compassion_fatigue` topic family,
consistency was corrected to 共情耗竭 across all files, then re-validated
(still 0 failures).

No DashScope call-cap concerns: 20 calls total (1 per atom, 0 repairs
needed) against a 45-call budget for this shard.
