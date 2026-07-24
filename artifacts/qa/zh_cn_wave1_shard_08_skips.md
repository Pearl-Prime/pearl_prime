# zh-CN Wave 1 — Shard 08 skip report

Branch: `agent/zh-cn-wave1-shard-08-20260723`
Shard file: `wave1_shard_08.jsonl` (20 atoms)

## Accepted (18/20)

All 18 pass `structural_validator.py` (modulo a known, pre-existing
false-positive class documented below) and `script_contamination.py`
(locale=zh-CN).

1. atoms/educators/compassion_fatigue/COMPRESSION/CANONICAL.txt
2. atoms/educators/compassion_fatigue/SCENE/CANONICAL.txt
3. atoms/educators/compassion_fatigue/HOOK/CANONICAL.txt
4. atoms/corporate_managers/compassion_fatigue/TAKEAWAY/CANONICAL.txt
5. atoms/corporate_managers/compassion_fatigue/SCENE/CANONICAL.txt
6. atoms/corporate_managers/compassion_fatigue/PERMISSION/CANONICAL.txt
7. atoms/corporate_managers/compassion_fatigue/THREAD/CANONICAL.txt
8. atoms/corporate_managers/compassion_fatigue/HOOK/CANONICAL.txt
9. atoms/corporate_managers/compassion_fatigue/STORY/CANONICAL.txt
10. atoms/corporate_managers/compassion_fatigue/REFLECTION/CANONICAL.txt
11. atoms/corporate_managers/people_pleasing/EXERCISE/CANONICAL.txt
12. atoms/corporate_managers/compassion_fatigue/PIVOT/CANONICAL.txt
13. atoms/corporate_managers/compassion_fatigue/watcher/CANONICAL.txt
14. atoms/corporate_managers/compassion_fatigue/overwhelm/CANONICAL.txt
15. atoms/corporate_managers/compassion_fatigue/spiral/CANONICAL.txt
16. atoms/corporate_managers/compassion_fatigue/grief/CANONICAL.txt
17. atoms/corporate_managers/compassion_fatigue/false_alarm/CANONICAL.txt
18. atoms/corporate_managers/compassion_fatigue/EXERCISE/CANONICAL.txt

### Post-translation glossary drift fixes (manual, no extra DashScope calls)

Cross-shard finding (from shard 04 / PR #101): `structural_validator.py` only
enforces glossary `avoid`-lists, not `glossary_project.yaml` *locked*
preferred forms — DashScope silently drifted "compassion fatigue" to the
colloquial `同情疲劳` / `共情疲劳` instead of the locked `共情耗竭` on several
files. Manually grepped every accepted file for this and other locked terms
and corrected drift by direct string substitution (re-validated after each
fix, no additional API calls):

- `corporate_managers/compassion_fatigue/REFLECTION`: 1 instance (`身份认同`→`自我认同`, glossary `avoid` catch) + confirmed no `同情疲劳`/`共情疲劳` drift after full-file grep.
- `corporate_managers/compassion_fatigue/STORY`: 6 instances of `同情疲劳`→`共情耗竭`.
- `corporate_managers/compassion_fatigue/REFLECTION`: 15 instances of `同情疲劳`→`共情耗竭`.
- `corporate_managers/compassion_fatigue/watcher`: 1 `身份`→`自我认同` glossary fix, 2 `共情疲劳`→`共情耗竭`, 1 stray untranslated English word (`distress`) rewritten in Chinese.
- `corporate_managers/compassion_fatigue/overwhelm`: 2 instances of `共情疲劳`→`共情耗竭`.
- `corporate_managers/compassion_fatigue/spiral`: 4 instances of `同情疲劳`→`共情耗竭`.
- `corporate_managers/compassion_fatigue/grief`: 5 instances of `共情疲劳`→`共情耗竭`.
- `corporate_managers/compassion_fatigue/false_alarm`: 8 instances of `同情疲劳`→`共情耗竭`, plus 2 stray untranslated English fragments (`spirals into`, `exhaustion`) rewritten in Chinese.
- `corporate_managers/compassion_fatigue/EXERCISE`, `TAKEAWAY`, `SCENE`, `PERMISSION`, `THREAD`, `HOOK`, `PIVOT`, `people_pleasing/EXERCISE`, `educators/*`: grepped, no drift found.

Also checked `观察者` (watcher-motif rendering) against sibling
`corporate_managers/{boundaries,imposter_syndrome}/watcher` zh-CN files
already landed on main — `观察者` is the existing persona-pool convention
there, so it was kept (not `监视者`) for pool consistency per
`glossary_core.yaml`'s "hold constant across a persona pool" instruction.

### Known pre-existing validator false-positive (not a translation defect)

`atoms/educators/compassion_fatigue/COMPRESSION`,
`atoms/corporate_managers/compassion_fatigue/{watcher,overwhelm,grief}`
report `structural_validator.py` `per_block_failures: untranslated_english`
on blocks that are **frontmatter-only by design** (e.g. `COMPRESSION`'s
`compression_family: C1` blocks have zero body text; several
`watcher`/`overwhelm`/`grief` `RECOGNITION`/`MECHANISM_PROOF`/
`TURNING_POINT`/`EMBODIMENT` blocks carry only a `path: <English string>`
frontmatter value, which is itself a protected field per
`protected_terms.yaml`). Verified this is a pre-existing corpus-wide
condition, not something introduced here:
- `atoms/midlife_women/courage/COMPRESSION` (already-landed zh-CN sibling)
  fails the identical check against its own English source.
- `atoms/corporate_managers/compassion_fatigue/watcher/locales/zh-TW/CANONICAL.txt`
  (already-landed zh-TW sibling) fails structurally against the same
  English source too (different failure signature, same root cause: the
  validator's per-block body-emptiness heuristic does not special-case
  frontmatter-only atom shapes).
`script_contamination.py` passes clean on every one of these files.

## Skipped — genuine malformed English source (2/20)

Per instructions: reporting the blocker rather than inventing missing
meaning. Both are pre-existing corruption in `main`, not introduced by this
shard, and both have the identical corruption pattern already present in the
already-landed zh-TW sibling (confirmed by running `structural_validator.py`
against the zh-TW candidate — it fails the same way).

1. **`atoms/educators/compassion_fatigue/REFLECTION/CANONICAL.txt`**
   Duplicate header IDs: `REFLECTION v16`–`v25` each appear twice in the
   English source (lines 152–285 as empty/stub headers with only
   `family`/`voice_mode` frontmatter and no body; lines 288–356 again with
   full body content but no frontmatter). Additionally versions
   v02/v04/v06/v08/v10/v12/v14/v26/v28/v30 have zero body content at all
   (header + delimiter, immediately followed by the next header).
   `structural_validator.py --source ... --candidate <zh-TW sibling> --locale zh-TW`
   reproduces `duplicate_header_ids` against the same source, confirming
   this predates this translation effort.

2. **`atoms/corporate_managers/compassion_fatigue/INTEGRATION/CANONICAL.txt`**
   Duplicate header IDs: `INTEGRATION v05` and `INTEGRATION v07` each appear
   twice in the English source (lines 21/38 and 30/58 respectively).
   `structural_validator.py` against the zh-TW sibling reproduces the same
   `duplicate_header_ids` failure.

Both should be routed to the EN-source-authoring backlog (see the 650-row
backlog referenced in commit `386bf02bef`) rather than hand-patched here.
