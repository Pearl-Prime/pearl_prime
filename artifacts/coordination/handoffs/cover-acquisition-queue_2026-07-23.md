# Handoff: cover-acquisition-queue (Lane 02, 2026-07-23)

**Status:** MERGED (queue + tooling only — no imagery acquired).
**Prereq landed:** Lane 01 PR #144, `1967795c756b56904b59f2ec9bdcad48f750c446` (bank_image_picker.py,
verify_cover_topic_imagery.py, storyblocks_cover_topic_map.yaml).

## What landed in this lane

- `scripts/publish/analyze_storyblocks_reuse.py` — read-only reuse-vs-new-search analyzer.
- `artifacts/coordination/cover_acquisition_queue.tsv` — 17 rows, one per canonical cover topic.
- `tests/test_analyze_storyblocks_reuse.py` — 12 passing tests.
- Two new rows in `artifacts/coordination/CANONICAL_ARTIFACTS_REGISTRY.tsv`.
- `artifacts/qa/cover_acquisition_queue_20260723/SUMMARY.md` + `analyze_output.json`.

Result: only `grief` (stock_id `350614976`, still image, positive cue `candle`)
resolves to `reuse_confirm`. All other 16 topics are `new_search` — including
5 of the 6 nominated "reuse candidate" topics (anxiety, boundaries, burnout,
depression, overthinking), because their social-bank hits either lack a
genuine descriptive cue or only match on an ineligible video record.

## NEXT ACTION requiring live credentials (not this session's job)

Three things must happen, in order, before any cover image can actually ship,
and all three require an operator/live-credential session:

1. **Storyblocks API confirm/download for the grief reuse candidate**
   (stock_id `350614976`) — under a **brand-new book-cover work unit**, not
   the existing `social_media_bank_storyblocks_20260720` work unit. EULA
   Section B forbids a shared HD pool across work units, so this is a fresh
   download even though the same stock item was already licensed once for
   social use.
2. **11 new Storyblocks searches** for the net-new topics (adhd_focus,
   compassion_fatigue, courage, financial_anxiety, financial_stress,
   imposter_syndrome, mindfulness, self_worth, sleep_anxiety, social_anxiety,
   somatic_healing) — none have any existing candidate anywhere in the repo.
3. **Human topic-verification for all 17 topics** before any record can ever
   carry `metadata.topic_verified: true`. This lane cannot and did not
   fabricate that step for any topic, including grief.

Only after (1)+(3) for grief and (2)+(3) for the other 16 can
`scripts/ci/verify_cover_topic_imagery.py` start passing, topic by topic.

## Resume commands

```bash
git fetch origin
python3 scripts/publish/analyze_storyblocks_reuse.py --json   # re-run the analysis fresh
cat artifacts/coordination/cover_acquisition_queue.tsv          # current queue state
pytest tests/test_analyze_storyblocks_reuse.py -x
```

When live Storyblocks credentials exist, use the existing
`scripts/storyblocks/fill_social_bank.py` pattern (see
`docs/STORYBLOCKS_SOCIAL_BANK.md`) but target a new cover work unit and write
through `scripts/storyblocks/license_store.py` with `surface="cover"` +
`metadata.topic_verified` set only after a human confirms the image, then
re-run `python3 scripts/ci/verify_cover_topic_imagery.py`.
