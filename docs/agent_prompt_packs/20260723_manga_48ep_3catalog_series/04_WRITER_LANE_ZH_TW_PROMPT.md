# 04 — Writer lane: zh_TW catalog (36 cells) — GATED

Paste into a fresh session per wave, AFTER `01_RESEARCH_GAP_ZHTW_MODERN_READER_PROMPT.md`
has landed. Part of the pack at
`docs/agent_prompt_packs/20260723_manga_48ep_3catalog_series/` — read
`00_MASTER_DISPATCH_PROMPT.md` in full first.

## STARTUP_RECEIPT

```
AGENT:              translate-zh-tw (repurposed as native-Traditional-Chinese
                    AUTHORING voice)
TASK:               zh_TW 48-episode manga series authoring, arc-1-first ramp
PROJECT_ID:         proj_manga_catalog_reconciliation_20260426
SUBSYSTEM:          manga_pipeline (authoring only)
AUTHORITY_DOCS:     00_MASTER_DISPATCH_PROMPT.md; 01_RESEARCH_GAP_ZHTW_MODERN_READER_PROMPT.md
                    (its landed output); ASSIGNMENT_MATRIX.tsv;
                    docs/research/manga_craft/ bibles; manga_arc_storyboard_planner.md
READ_PATH_COMPLETE: <confirm yes -- read 00_MASTER_DISPATCH_PROMPT.md AND
                    confirm lane 01's signal exists before proceeding>
WRITE_SCOPE:        artifacts/manga/chapter_scripts/<series_id>/ep_0XX.yaml;
                    artifacts/manga/arc_storyboards/<series_id>/ep_0XX.arc_storyboard.yaml
                    for zh_TW cells only; config/authoring/manga_authors/ (ADD
                    3-5 new zh_TW pen-name profiles only, per Q-MANGA48-ZHTW-AUTHORS-01)
OUT_OF_SCOPE:       en_US/ja_JP cells; config/manga/modern_reader_story_doctrine.yaml
                    (lane 01's scope, not this lane's)
PROVENANCE:         inherits 00_MASTER_DISPATCH_PROMPT.md's PROVENANCE block;
                    additionally builds_on lane 01's landed zh_TW doctrine entry
BLOCKERS:           GATED on lane 01's signal (see gate check below) and on the
                    thin zh_TW author pool (see Q-MANGA48-ZHTW-AUTHORS-01)
READY_STATUS:       blocked until lane 01 signal confirmed
```

## PRE-REQUISITE GATE CHECK (verify before doing anything else)

```
grep -q "^  zh_TW:" config/manga/modern_reader_story_doctrine.yaml
```
If this fails (no `zh_TW` market profile), STOP. Do not proceed on a
zh_CN-borrowed profile without an explicit operator OPD accepting that as an
interim stand-in for the smoke/pilot cell only — log the OPD, do not silently
substitute. Confirm the lane-01 signal `zhtw-modern-reader-doctrine-landed=<SHA>`
exists on a durable surface (merged PR) before treating this gate as passed.

## EXECUTE

Turn ends on: this wave's cells all MERGED-or-BLOCKED, signal emitted, CLOSEOUT
filed.

## Scope this lane covers

36 zh_TW rows in `ASSIGNMENT_MATRIX.tsv` PLUS `bright_presence_tw_seinen`
(zh_TW-exclusive per its `manga_locales` restriction — 37 cells total for this
catalog, one more than en_US/ja_JP). Only 1 row is REUSE_EXISTING
(`solar_return_isekai__zh_TW__isekai__series01` — verify live whether this
directory has any real episode file at all; it may be an empty scaffold).
35-36 are NEW_SERIES: this catalog has essentially zero existing series
identity to build on, and only 2 native pen-name author profiles
(`config/authoring/manga_authors/lin_yuxi_zh_tw_002.yaml`,
`shen_yejing_zh_tw_001.yaml`) versus 255 for ja_JP. This is the heaviest-lift
catalog in the program — budget accordingly and do not expect en_US/ja_JP wave
sizing to carry over 1:1.

## Author-pool gap (Q-MANGA48-ZHTW-AUTHORS-01, default: resolve inline)

Before wave A, author 3-5 additional zh_TW pen-name profiles in
`config/authoring/manga_authors/` (same schema as the existing 2 — check
`config/authoring/manga_authors/schema.yaml` if present, else mirror
`lin_yuxi_zh_tw_002.yaml`'s field shape), so 37 NEW_SERIES cells are not all
forced onto 2 bylines. This is a small, mechanical addition — do it as part of
wave A rather than escalating to the operator, unless the existing schema
requires information only the operator can supply (e.g. a licensing/
legal constraint on pen-name authorship you don't already see documented).

## Native-voice authoring

Dispatch the `translate-zh-tw` Claude Code agent (Traditional Chinese Taiwan
localization agent) as the native-authoring voice, same instruction as the
ja_JP lane: this is original authoring in Traditional Chinese, not translation
of an English draft. Use the newly-landed zh_TW `modern_reader_context`
profile from lane 01 (MRT commute / EasyCard / night-market / bubble-tea-app /
Readmoo-or-local-comic-app / buxiban cram-school / Taiwan convenience-store
ritual — whatever lane 01 actually landed; re-read the file, do not assume
this list is final). Genre register skews TW-literary per
`docs/CJK_CATALOG_PLAN.md` SS2 (atmospheric palette, French-BD-adjacent
influence) — do not default to a zh_CN or ja_JP voice pasted over Traditional
Chinese script; the market guardrails in lane 01's output should say so
explicitly.

## Smoke cell (do first, alone)

Pick the highest-tier NEW_SERIES cell (a flagship or core brand — check
`ASSIGNMENT_MATRIX.tsv` for the first `tier=flagship` or `tier=core` zh_TW row;
as of this pack's generation all 3 flagship brands and most core brands are
NEW_SERIES for zh_TW). Create the series directory following the naming
convention `{brand_id}__{author_pen_name}__zh_TW__{primary_topic}__{title_slug}`
(matching the en_US/ja_JP convention exactly), author ep_001 as the arc-1
opener, gate-check, PR, CI green, merge, emit
`manga48-pilot-zh_TW-pass=<SHA>`.

## Per-cell exit criteria

Same as master prompt + block-fixture self-check
(`china_system_allegory` and `france_flat_us_school` are adjacent failure
modes worth re-reading even though neither is zh_TW-named — the underlying
lesson, "don't flatten a CJK-market story into a Western or PRC-generic
register," applies directly).

## Wave sizing

Smaller waves than en_US/ja_JP given the thin author pool and zero existing
scaffolding — recommend 5-6 cells per wave rather than 8-10.

## Landing + signals

Per master prompt. `manga48-wave-<n>-zh_TW=<full-SHA>` per wave PR.

## CLOSEOUT_RECEIPT

List every cell completed this wave with its new series_id, the author
profile used (noting which of the newly-authored zh_TW pen names it used),
and merged SHA.
