# zh-CN Wave 1 Shard 03 — Skip Report

Branch: `agent/zh-cn-wave1-shard-03-20260723`
Shard file: `wave1_shard_03.jsonl` (20 atoms, persona `gen_alpha_students`, topic `compassion_fatigue`)

## Summary

- Attempted: 20
- Accepted: 19
- Skipped: 1

## Skipped atoms

### `atoms/gen_alpha_students/compassion_fatigue/REFLECTION/CANONICAL.txt` (item_id `69c0ea327adf`)

**Reason: malformed English source, not a translation defect.**

The English source file has genuinely duplicated header IDs — `## REFLECTION v16`
through `## REFLECTION v25` appear twice in the file (once around line 168-319 in a
`## HEADER\n---\n\n## HEADER\n---\nfamily:...` paired-header convention, and again
starting at line 322 in a different `## HEADER\n---\n\n---\ncontent\n---` single-block
convention), instead of the source continuing on to `v31`-`v40`. Confirmed via:

```
grep -n "^## REFLECTION" atoms/gen_alpha_students/compassion_fatigue/REFLECTION/CANONICAL.txt
```

which shows `v16`-`v25` twice and no `v31`-`v40` at all. DashScope faithfully mirrored
this duplication into the candidate translation (the structural validator correctly
flagged `duplicate_header_ids` for the same 10 IDs). Per CLAUDE.md's translation
guidance ("If the English source is malformed, report the blocker rather than
inventing missing meaning"), this atom is skipped rather than hand-authoring the
missing v31-v40 content or silently renumbering the duplicate blocks — that would be
inventing meaning not present in the English canonical source. This should be routed
to EN-source authoring/repair (see the `docs(qa): atom authoring backlog for
EN-source-corrupted atoms` doc on main) before a zh-CN translation can be produced.

## Accepted atoms with structural-validator known false positive (manually verified correct)

### `atoms/gen_alpha_students/compassion_fatigue/COMPRESSION/CANONICAL.txt` (item_id `76b2eb9de8a4`)

`structural_validator.py` flags every block as `untranslated_english` because the
atom's body is 100% non-prose identifier lines (`compression_family: C1` ... `C5`),
byte-identical between English source and candidate. Confirmed via `diff` that this
is intentional — there is no human-readable prose in this atom at all, so there is
nothing to translate; the identical-to-source output is the correct output. Accepted
manually, not via `repair_state.py` repair cycle (nothing to repair).

## Locked-term drift found and fixed before commit (cross-shard finding, per PR #101)

`structural_validator.py`'s glossary check only enforces `avoid`-lists, not
`preferred`/locked forms in `glossary_project.yaml`. A comprehensive manual grep
across all 19 accepted candidates before commit found DashScope had drifted off the
locked terms on a majority of files. All instances below were corrected in place
before writing to the `locales/zh-CN/` paths:

- **"compassion fatigue" → locked `共情耗竭`**: found `共情疲劳` (74 occurrences across
  8 files: `14ce672c528d`, `533afc48fc5f`, `5acfb008fc47`, `763e29be8390`,
  `7ded14b2ebe7`, `d253f8b34083`, `dd94ee3db5e7`, plus the skipped `69c0ea327adf`) and
  `同情疲劳`/`共情枯竭` (29 occurrences across `0010cb9c3ab8`, `048fd27ff85b`,
  `38c80150b8eb`, `50aaee94740b`, `8351acb79be4`, `eca5e14c6b3c`) — all corrected to
  `共情耗竭`.
- **"empathy tank empty" → locked `共情耗尽`**: found `共情油箱已空` / `共情油箱耗尽` /
  a full mistranslated sentence in `763e29be8390` — corrected to `共情耗尽`.
- **"caring past capacity" → locked `关心超出了承受范围` (metaphor_body) /
  `超负荷的关心` (compressed_form)**: found `关怀过载`, `关怀已超出负荷`/`超出负荷的
  关怀`, `关怀能力超出负荷`, `超出承受能力的关怀`/`过度的关怀` across
  `0010cb9c3ab8`, `533afc48fc5f`, `763e29be8390`, `8351acb79be4` — corrected to the
  locked compressed/metaphor forms by context (compressed for THREAD/PERMISSION/
  TAKEAWAY register, metaphor_body for STORY narrative prose).
- **"giving without refill" → locked `只出不进的付出` (metaphor_body) / `付出没有
  回补` (compressed_form)**: found `只付出而无补充`, `付出却得不到补充`, `只付出不
  补充`, `只付出而不补充`, `只出不进的消耗` across `0010cb9c3ab8`, `533afc48fc5f`,
  `763e29be8390`, `8351acb79be4` — corrected to the locked forms by context.
- **"identity" glossary avoid-list violation (`身份`)**: two distinct source senses
  found and disambiguated: (a) genuine self-concept "identity" (glossary_core.yaml
  preferred `自我认同`) in `false_alarm`, `comparison`, `THREAD`, `TAKEAWAY`,
  `spiral/PIVOT` — corrected to `自我认同`; (b) a persona-pool-specific scene-noun
  rotation ("at the identity" / "at the online persona" / "at the group chat" —
  three interchangeable social-context fillers in the English source, not
  self-concept identity at all) in `PERMISSION` and `STORY` — rendered as `这个
  社交圈` to avoid the flagged term while preserving the locational-social sense,
  distinct from `网络人设` (online persona) and `群聊` (group chat) already used for
  the other two fillers in the same files. This "identity" scene-noun-rotation motif
  is not yet documented in `glossary_project.yaml` and should be added there for
  future shards touching `gen_alpha_students/compassion_fatigue`.

After these fixes, an independent re-grep across all 19 accepted files for every
locked-term variant found zero remaining drift, and `script_contamination.py`
reported clean on all 19 files.
