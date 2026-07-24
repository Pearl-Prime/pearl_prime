# zh-CN Wave 1 — Shard 00 Skip Report

Shard file: `wave1_shard_00.jsonl` (20 atoms). 9 translated and accepted; 11 skipped.
All skips are due to malformed/absent English source, not translation quality —
per program instruction "if the English source is malformed, report the blocker
rather than inventing missing meaning."

## Skipped: malformed EN source — missing `## SHAPE vNN` header prefix on
even-numbered versions (content silently swallowed into the preceding block)

These files use a `RECOGNITION`/`MECHANISM_PROOF` convention where odd versions
(v01, v03, v05...) carry only a one-line `path:` label (not prose) and even
versions (v02, v04...) are missing their `##` header prefix entirely, so the
structural parser folds the bare "RECOGNITION v02" text and delimiter into the
prior block's body instead of recognizing it as a separate entry. There is no
real prose to translate for the even-numbered entries, and inventing content
for them would violate the "don't invent missing meaning" rule.

- `atoms/first_responders/compassion_fatigue/watcher/CANONICAL.txt` (item 1a194ef2bfcd)
- `atoms/first_responders/compassion_fatigue/overwhelm/CANONICAL.txt` (item 885322a63003)
- `atoms/first_responders/compassion_fatigue/spiral/CANONICAL.txt` (item 90ff1b48662a)
- `atoms/first_responders/compassion_fatigue/grief/CANONICAL.txt` (item 8b805106131a)
- `atoms/first_responders/compassion_fatigue/false_alarm/CANONICAL.txt` (item a3a97b108224)
- `atoms/first_responders/compassion_fatigue/shame/CANONICAL.txt` (item 9221a366b355)
- `atoms/first_responders/compassion_fatigue/comparison/CANONICAL.txt` (item 934f27538e81)

## Skipped: malformed EN source — duplicate header IDs

`structural_validator.py`'s `duplicate_header_ids` check fires on the
candidate's header list regardless of translation quality, because the
**English source itself** repeats a header ID. A byte-faithful translation of
either file will always fail structural validation; this is not a repair-able
translation defect.

- `atoms/first_responders/compassion_fatigue/INTEGRATION/CANONICAL.txt`
  (item dd264c0b1b87) — `INTEGRATION_v05` (and `v06`, `v07`) appear twice,
  once as a bare metadata pointer, once as a full authored reframe with its
  own frontmatter — an authoring merge artifact, not a translatable pair.
- `atoms/gen_z_professionals/compassion_fatigue/COMPRESSION/CANONICAL.txt`
  (item fa1055f29a03) — `COMPRESSION_v04` appears twice.

## Skipped: source_path does not exist on `origin/main`

Both files exist only as **untracked, uncommitted** local files in a sibling
worktree (`?? ` in `git status`, confirmed via
`git log -- <path>` returning empty and
`git show origin/main:<path>` erroring "exists on disk, but not in
'origin/main'"). The golden-branch pattern requires branching from
`origin/main`; there is no canonical committed EN source at this path to
translate from a clean branch. Flagging for the atom-authoring/backlog owner
rather than translating from an unreviewed, non-canonical local draft.

- `atoms/midlife_women/compassion_fatigue/GRIEF/CANONICAL.txt` (item ee1cfa5e68a2)
- `atoms/midlife_women/compassion_fatigue/false_alarm/CANONICAL.txt` (item db91f5f17a12)

## Accepted (9)

- `atoms/first_responders/compassion_fatigue/EXERCISE/CANONICAL.txt` (item 41f081f74f4e)
- `atoms/first_responders/compassion_fatigue/COMPRESSION/CANONICAL.txt` (item 0500175ba18c)
- `atoms/first_responders/compassion_fatigue/HOOK/CANONICAL.txt` (item 148c7b015ef0)
- `atoms/first_responders/compassion_fatigue/REFLECTION/CANONICAL.txt` (item 3d8ac1ec1fae)
- `atoms/first_responders/compassion_fatigue/SCENE/CANONICAL.txt` (item 619a3dca0465)
- `atoms/first_responders/compassion_fatigue/STORY/CANONICAL.txt` (item 1c4b616ddd7a)
- `atoms/first_responders/compassion_fatigue/TAKEAWAY/CANONICAL.txt` (item 3680492bbfd1)
- `atoms/midlife_women/compassion_fatigue/PIVOT/CANONICAL.txt` (item 68be9e6e59cc)
- `atoms/midlife_women/compassion_fatigue/INTEGRATION/CANONICAL.txt` (item c6f4ae56f22c)

All 9 translated via `scripts/localization/translation_quality/candidates/dashscope_qwen_client.py`
(`qwen3.7-max`, DashScope Singapore intl endpoint), one repair pass applied by
hand to 3 of the 9 (glossary-lock consistency for the `compassion fatigue` /
`empathy tank empty` / `giving without refill` critical_recurring motifs per
`analysis/zh_cn/glossary_project.yaml`, plus one delimiter-count fix), then
re-validated. All 9 pass `structural_validator.py --locale zh-CN` and
`script_contamination.py --locale zh-CN` clean.

Total DashScope calls this shard: 9 (one per accepted atom; no repair calls —
the 3 repairs were done by hand-editing the candidate text, not by re-calling
DashScope, to stay well under the ~45-call budget).
