# zh-CN Wave 1 — Shard 10 — Skip Report

Model: DashScope `qwen3.7-max` (Singapore intl endpoint), via
`scripts/localization/translation_quality/candidates/dashscope_qwen_client.py`.
Validated with `scripts/localization/translation_quality/structural_validator.py`
+ `script_contamination.py` (zh-CN watchlist).

Shard: 20 items assigned. 12 accepted. 8 blocked/skipped (all real,
byte-verified source defects — no gate weakened, no content invented).

## Blocked items (not fixable without inventing content or altering the shared validator)

1. **`atoms/educators/self_worth/watcher/CANONICAL.txt`** — source file does
   not exist in the repo at all. `item_id 6449a0141a19`... (shard row 6). The
   shard's atom list references a path with no corresponding English source;
   `atoms/educators/self_worth/` has no `watcher` shape directory (only
   `depression/watcher` exists). Cannot translate a file that isn't there.

2. **`atoms/educators/imposter_syndrome/shame/CANONICAL.txt`** — 10 of its
   header blocks (`RECOGNITION_v01/03/05`, `MECHANISM_PROOF_v02/04`,
   `TURNING_POINT_v01/03/05`, `EMBODIMENT_v02/04`) have bodies that are
   literally just the bare next-version label (e.g. the body of
   `## RECOGNITION v01` is the text `RECOGNITION v02`) — unauthored
   band-fill stub scaffolding, not real prose. Translating a bare label as
   if it were content would be inventing meaning that isn't in the source.
   Matches the known "atom authoring backlog for EN-source-corrupted atoms"
   class (see `docs/` commit `386bf02bef`).

3. **`atoms/educators/self_worth/REFLECTION/CANONICAL.txt`** — the English
   source itself contains duplicate header IDs: `REFLECTION v16`–`v25` are
   each defined twice in the same file (lines 152–286 and again 288–421).
   `structural_validator.py`'s duplicate-header check fires on any repeated
   header ID in the candidate; since the source already has the duplicates,
   no faithful translation can pass this check without renumbering the
   source (out of scope — would be altering source structure, not
   translating it).

4. **`atoms/educators/courage/REFLECTION/CANONICAL.txt`** — same defect as
   #3: `REFLECTION v16`–`v25` duplicated in the English source itself.

5. **`atoms/educators/depression/watcher/CANONICAL.txt`** — the English
   source repeats `RECOGNITION v01`–`v05` five times each (25 duplicate
   headers) by design (a padding/band-fill pattern). Same permanent
   duplicate-header-ID block as #3/#4.

6. **`atoms/educators/depression/shame/CANONICAL.txt`** — identical
   duplicate-header pattern to #5 (`RECOGNITION v01`–`v05` x5 each).

7. **`atoms/educators/courage/spiral/CANONICAL.txt`** — `TURNING_POINT v01`
   and `EMBODIMENT v01` bodies are two-line `CALLBACK_ID: .../CALLBACK_PHASE:
   ...` metadata markers, not prose (a callback-linkage scaffold, distinct
   from the protected frontmatter keys in `protected_terms.yaml`, which
   don't cover `CALLBACK_ID`/`CALLBACK_PHASE`). There is no translatable
   content in these two blocks; leaving them as-is (correct) always trips
   the validator's `untranslated_english` check since it requires CJK
   presence in every non-empty body.

8. **`atoms/educators/courage/shame/CANONICAL.txt`** — same
   `CALLBACK_ID`/`CALLBACK_PHASE`-only body defect as #7
   (`TURNING_POINT v01`, `EMBODIMENT v01`). One repair pass fixed the
   file's other defects (a dropped trailing `---` on `MECHANISM_PROOF v07`,
   a `身份`→`自我认同` glossary drift, a delimiter-count mismatch) but the
   two CALLBACK-only blocks remain unresolvable without inventing prose.

## Systematic tooling finding (repaired locally, no repeat API calls)

The DashScope client's raw output for larger files reliably dropped the
blank line between a block's closing `---` and the next `## SHAPE vNN`
header (`---## HEADER` glued onto one line), which cascaded into
`header_id_mismatch` / `missing_header_ids` / `delimiter_count_mismatch`
false failures purely from lost whitespace, not lost content. Also observed:
occasional dropped trailing `---` at end-of-file, and one case of an extra
inserted `---` pair. All three were repaired deterministically (regex
newline-insertion, source-vs-candidate trailing-delimiter parity check, and
one manual diff-based fix) with **zero additional DashScope calls** — see
`fix_glued_headers` / `fix_trailing_delimiter` in the shard's scratch driver
script. Also found and fixed one recurring glossary drift:
`身份` (avoid-listed per `glossary_core.yaml`) instead of the preferred
`自我认同` for "identity" — deterministic find/replace, no repeat call.
Consistent with sibling shard 04's cross-shard finding that
`structural_validator.py` does not enforce glossary `preferred` forms, only
`avoid` lists — spot-checked all 12 accepted files against
`glossary_core.yaml`/`glossary_project.yaml` preferred terms
(羞耻感/不堪重负/自我认同/etc.) after repair; no drift found in this
shard's accepted set.

## Accepted (12/20)

- atoms/educators/imposter_syndrome/THREAD
- atoms/educators/imposter_syndrome/HOOK
- atoms/educators/imposter_syndrome/STORY
- atoms/educators/imposter_syndrome/REFLECTION
- atoms/educators/self_worth/shame
- atoms/educators/self_worth/comparison
- atoms/educators/self_worth/SCENE
- atoms/educators/self_worth/HOOK
- atoms/educators/courage/SCENE
- atoms/educators/courage/HOOK
- atoms/educators/depression/overwhelm
- atoms/educators/depression/SCENE

## Call budget

42 real DashScope calls made this shard (per-call log:
`artifacts/qa/translation_quality_cost_log_2026-07-23.jsonl`), against a
45-call soft cap set by the dispatch brief. Estimated real spend: **$0.244
USD** (`qwen3.7-max`, per-call rate table in `dashscope_qwen_client.py`).
