# Cover Acquisition Queue — Discovery Summary (2026-07-23)

Lane 02 of the storyblocks-cover-wiring prompt pack (`cover-acquisition-queue`).
Builds on Lane 01's merged PR #144 (`1967795c756b56904b59f2ec9bdcad48f750c446`),
which landed `scripts/publish/bank_image_picker.py`,
`scripts/ci/verify_cover_topic_imagery.py`, and
`config/publishing/storyblocks_cover_topic_map.yaml` on `origin/main`.

## Correction of the source closeout's false provenance claim

An operator pasted a closeout claiming a "generated acquisition queue
containing every reusable stock ID, required action, and new-search topic"
for the 17 cover-image topics already existed. **This claim is false.** A
router independently verified this before this lane started:

- No such queue file exists anywhere in the repository, on any branch, or in
  git history at session start.
- The two commit SHAs the closeout cited (`053a6243ed`, `5c5177c627`) do not
  resolve to valid git objects in this repository (`git cat-file -t <sha>` ->
  `fatal: Not a valid object name`).
- This lane re-confirmed the same negative result independently: `git fetch
  origin` then a full repo search for `cover_acquisition_queue*` returned
  nothing prior to this lane's own work.

Everything below was authored from scratch in this lane. Nothing here reuses
or corroborates any number from the disputed closeout.

## Live-state reconciliation (fetched, not assumed)

- `origin/main` at lane start: `7a41843991493303a471cd39bde636cc838dd1d1`.
- `git merge-base --is-ancestor 1967795c756b56904b59f2ec9bdcad48f750c446
  origin/main` -> confirmed ancestor (Lane 01's PR #144 is landed).
- `artifacts/storyblocks/license_index.jsonl` (the cover-surface license
  index `bank_image_picker.pick_image` actually reads at render time):
  **does not exist** on `origin/main` — zero rows, confirmed empirically.
  This matches `docs/specs/STORYBLOCKS_COVER_ASSEMBLY_V1.md`'s own statement
  that "current committed inventory has no cover-surface license index."
- No path anywhere in the repo carries `surface: cover` or
  `topic_verified: true` for any Storyblocks record. Confirmed by inspecting
  the only committed Storyblocks bank metadata
  (`artifacts/storyblocks/social_media_bank_storyblocks_20260720/BANK_INDEX.json`,
  `MANIFEST.tsv`) — neither field exists in that schema at all; it predates
  the cover-surface contract entirely and is scoped to a social/video-snippet
  work unit (`social_media_bank_storyblocks_20260720`), i.e. `surface:
  social_broll` in spirit.
- The social bank's HD bytes live under the gitignored
  `artifacts/storyblocks_licensed/` prefix
  (`.gitignore`: "Storyblocks HD licensed downloads (local bank; never
  commit binaries)") and are **not present in this checkout** — only the
  metadata (`BANK_INDEX.json`, `MANIFEST.tsv`, 16 assets across 8 tags:
  anxiety, boundaries, burnout, depression, grief, hope, loneliness,
  overthinking) is committed. `hope` and `loneliness` are social-bank topic
  tags that are **not** among the 17 canonical cover topics in
  `config/publishing/storyblocks_cover_topic_map.yaml` / `config/catalog/
  catalog_generation_config.yaml` and were excluded from this analysis.

## Reuse-vs-new-search analysis (6 nominated + 11 net-new = 17)

For the six nominated reuse-candidate topics (anxiety, boundaries, burnout,
depression, grief, overthinking), this lane scored every social-bank record
tagged with that topic using the same heuristic as
`bank_image_picker.validate_candidate()` minus the `surface` /
`topic_verified` checks (those are exactly the two fields this lane cannot
fabricate), **plus** the `media_type == image` requirement (a book cover must
be a still image; a Storyblocks video record, however well it matches on
title text, is categorically not a usable cover candidate).

Honest result, run via `python3 scripts/publish/analyze_storyblocks_reuse.py`:

| Topic | Social-bank records tagged | Plausible image candidates | Action |
|---|---|---|---|
| anxiety | 3 (1 image, 2 video) | 0 — image title has no positive cue; the one positive-cue hit ("calm ocean waves") is on a video | new_search |
| boundaries | 2 (1 image, 1 video) | 0 | new_search |
| burnout | 1 (1 image) | 0 | new_search |
| depression | 2 (1 image, 1 video) | 0 | new_search |
| grief | 2 (1 image, 1 video) | 1 — image `350614976` ("...small candle burning...") hits positive cue `candle` | reuse_confirm |
| overthinking | 2 (1 image, 1 video) | 0 | new_search |

**Only `grief` yields a genuine reuse candidate.** The other five nominated
topics do have social-bank rows tagged with the right topic, but none carry
a genuine descriptive (title) match on a *still image* — several only match
on a video record, which is disqualified outright for cover use. This lane
does not paper over that: nomination as a "reuse candidate" is not the same
as having an actual candidate, and the queue reports the honest per-topic
result rather than assuming all six nominated topics reuse.

The 11 net-new topics (adhd_focus, compassion_fatigue, courage,
financial_anxiety, financial_stress, imposter_syndrome, mindfulness,
self_worth, sleep_anxiety, social_anxiety, somatic_healing) have, as
expected, zero social-bank records tagged with any of them — confirmed via
`social_bank_candidates_total == 0` for every one in the analysis output —
so all 11 are `new_search` with no candidates to list.

Full machine output: `artifacts/qa/cover_acquisition_queue_20260723/analyze_output.json`
(`python3 scripts/publish/analyze_storyblocks_reuse.py --json`).

## What this lane did NOT do

- **No live Storyblocks confirm/download happened.** No new HD bytes were
  fetched, no MAU ledger entry was created, no `CampaignAssetDownload` /
  `LicenseRecord` was written.
- **No `topic_verified: true` was ever written anywhere** — that would
  fabricate a human verification step that did not happen, which is the
  single most important rule of this lane.
- **No existing `social_broll`-surface record was relabeled.** The grief
  candidate (`350614976`) remains exactly what it was: a social-bank asset
  with no `surface` field and no verification. Reusing it for a cover
  requires a fresh Storyblocks confirm/download under a *new* book-cover
  work unit (EULA Section B — no shared HD pool across work units) plus a
  human looking at the actual image and confirming it represents `grief`
  before any `surface: cover` / `topic_verified: true` record can exist.
- **The cover render path remains blocked exactly as Lane 01 left it.**
  `scripts/ci/verify_cover_topic_imagery.py` still fails closed for all 17
  topics; this lane adds a triage queue for the next (credentialed, human)
  step, not any actual imagery.

## Deliverables

1. `scripts/publish/analyze_storyblocks_reuse.py` — read-only analyzer/recommender.
2. `artifacts/coordination/cover_acquisition_queue.tsv` — 17 rows (1 header + 17 topics).
3. `tests/test_analyze_storyblocks_reuse.py` — 12 tests, all passing.
4. `artifacts/coordination/CANONICAL_ARTIFACTS_REGISTRY.tsv` — two new rows
   (`cover_acquisition_queue`, `storyblocks_reuse_analyzer`) with
   `NEW-ARTIFACT-JUSTIFIED` rationale.
5. This file.

## Acceptance layer (honest)

**CODE-WIRED.** A queue and the tooling that produced it exist and are
tested against real, committed metadata. Zero cover images are licensed,
zero are human-verified, and the cover render path is still fail-closed for
all 17 topics. Do not report this as "acquisition done" or "images sourced."
