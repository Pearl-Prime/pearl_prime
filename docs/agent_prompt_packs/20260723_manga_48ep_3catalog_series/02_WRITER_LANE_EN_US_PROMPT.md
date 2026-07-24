# 02 — Writer lane: en_US catalog (37 cells)

Paste into a fresh session per wave (re-paste for each new wave; do not run all
37 cells in one unbounded turn). Part of the pack at
`docs/agent_prompt_packs/20260723_manga_48ep_3catalog_series/` — read
`00_MASTER_DISPATCH_PROMPT.md` in full first; this file only adds the en_US-
specific detail and does not repeat the shared contract.

## EXECUTE

Turn ends on: this wave's cells all MERGED-or-BLOCKED, signal emitted, CLOSEOUT
filed. Not on "PR open." Not on "draft written."

## STARTUP_RECEIPT

```
AGENT:              Pearl_Writer (native-voice Claude subagent fan-out)
TASK:               en_US 48-episode manga series authoring, arc-1-first ramp
PROJECT_ID:         proj_manga_catalog_reconciliation_20260426
SUBSYSTEM:          manga_pipeline (authoring only; no render/pipeline code)
AUTHORITY_DOCS:     00_MASTER_DISPATCH_PROMPT.md (full shared contract);
                    ASSIGNMENT_MATRIX.tsv; docs/research/manga_craft/ bibles;
                    manga_arc_storyboard_planner.md; MANGA_STORY_EXCELLENCE_REALIZATION_GATE_SPEC.md
READ_PATH_COMPLETE: <confirm yes -- read 00_MASTER_DISPATCH_PROMPT.md in full first>
WRITE_SCOPE:        artifacts/manga/chapter_scripts/<series_id>/ep_0XX.yaml;
                    artifacts/manga/arc_storyboards/<series_id>/ep_0XX.arc_storyboard.yaml
                    for en_US cells only
OUT_OF_SCOPE:       ja_JP/zh_TW cells; any render/gate code; the two source
                    genre-allocation SSOT files (read only)
PROVENANCE:         inherits 00_MASTER_DISPATCH_PROMPT.md's PROVENANCE block
BLOCKERS:           none for en_US (unlike zh_TW, no doctrine gap)
READY_STATUS:       ready
```

## Scope this lane covers

All 37 en_US rows in `ASSIGNMENT_MATRIX.tsv` (`awk -F'\t' '$1=="en_US"'` on the
committed matrix — 3 flagship, 16 core, 18 niche; 0 excluded). Read the matrix
row for each cell you take: it gives `genre_id`, `craft_bible` path,
`arc_shape_hint`, and `status` (REUSE_EXISTING vs NEW_SERIES) with the existing
`existing_series_id` to author into when REUSE_EXISTING.

## Native-voice authoring

English-native prose — dispatch general-purpose Claude subagents per brand (or
per small brand batch within a wave) using the Agent tool. Each subagent's
prompt must include: the brand's `primary_topic`/`secondary_topics` (from
`config/manga/canonical_brand_list.yaml`, cited in the matrix), the assigned
`genre_id`'s craft bible (read SS1-SS9 before writing a single panel — SS7 is
the 48-episode/volume arc shape, SS8 is the required panel-field schema, SS9 is
three canonical voice openings to calibrate register), the en_US
`modern_reader_context` block from `config/manga/modern_reader_story_doctrine.yaml`,
and the gold PASS fixture
`tests/fixtures/manga/story_excellence/pass/battle_en_us_genalpha/chapter_script_writer_handoff.json`
(or `pass/school_fr_fr_genalpha/` as a second reference for craft-bible-to-
panel translation, adapted register).

## Smoke cell (do this one first, alone, before any other en_US cell)

`stillness_press` (flagship, REUSE_EXISTING,
`artifacts/manga/chapter_scripts/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/`).
This directory's existing `ep_001.yaml` FAILS `check_manga_story_authored.py`
today (verified 2026-07-23: `artifact_type` is unset — it is a listing, not a
story). Rewrite `ep_001.yaml` in place as a full `chapter_script_writer_handoff`
(psychological_horror genre per the matrix — the anxiety-as-horror-shell
technique from `docs/CJK_CATALOG_PLAN.md` SS1 applied to en_US), arc-1 opener,
>= the panel floor, modern_reader_context populated, no teacher named (a real
`ahjan`-authored en_US flagship book already exists and is PROVEN-AT-BAR in the
BOOK pipeline — this is a SEPARATE manga vessel-character story; the author
pen-name `ahjan` in the directory name is a byline convention only, it must
NEVER appear as a character or named teacher inside panel text). Gate-check it,
open a PR, get it green, merge, emit `manga48-smoke-pass=<SHA>`, then continue.

## Per-cell exit criteria

Same as the master prompt's "Deliverable shape per cell" section. Self-check
against ALL of the `tests/fixtures/manga/story_excellence/block/` fixture
names before calling a cell done — each is a named failure mode your episode
must not reproduce (mention_only_phone_train, dark_fantasy_portal_no_cost,
generic_healing_something_shifted, sports_stats_no_body_team,
social_issue_poster_no_relationship, romance_no_dyad, missing_modern_reader_context,
china_system_allegory, france_flat_us_school, japan_tourist_default).

## Wave sizing

Batch by tier: wave A = 3 flagship (after smoke); wave B = 16 core (split into
~2 sub-waves of 8 if PR file count runs high); wave C = 18 niche (split
similarly). Arc-1-only (12 episodes) per cell in these waves; arcs 2-4 are a
follow-on program per the master prompt's ramp ordering.

## Landing + signals

Per master prompt. `manga48-wave-<n>-en_US=<full-SHA>` per wave PR.

## CLOSEOUT_RECEIPT

List every cell completed this wave with its series_id and merged SHA. List
any cell you skipped and why (already-authored per live-truth recheck,
blocked, deferred to next wave).
