# 03 — Writer lane: ja_JP catalog (36 cells)

Paste into a fresh session per wave. Part of the pack at
`docs/agent_prompt_packs/20260723_manga_48ep_3catalog_series/` — read
`00_MASTER_DISPATCH_PROMPT.md` in full first; this file only adds the ja_JP-
specific detail.

## EXECUTE

Turn ends on: this wave's cells all MERGED-or-BLOCKED, signal emitted, CLOSEOUT
filed.

## STARTUP_RECEIPT

```
AGENT:              translate-ja (repurposed as native-Japanese AUTHORING voice)
TASK:               ja_JP 48-episode manga series authoring, arc-1-first ramp
PROJECT_ID:         proj_manga_catalog_reconciliation_20260426
SUBSYSTEM:          manga_pipeline (authoring only)
AUTHORITY_DOCS:     00_MASTER_DISPATCH_PROMPT.md (full shared contract);
                    ASSIGNMENT_MATRIX.tsv; config/authoring/manga_authors/*_ja_jp.yaml;
                    docs/research/manga_craft/ bibles; manga_arc_storyboard_planner.md
READ_PATH_COMPLETE: <confirm yes -- read 00_MASTER_DISPATCH_PROMPT.md in full first>
WRITE_SCOPE:        artifacts/manga/chapter_scripts/<series_id>/ep_0XX.yaml;
                    artifacts/manga/arc_storyboards/<series_id>/ep_0XX.arc_storyboard.yaml
                    for ja_JP cells only
OUT_OF_SCOPE:       en_US/zh_TW cells; config/authoring/manga_authors/ profile
                    edits beyond assigning an existing profile to a new series
PROVENANCE:         inherits 00_MASTER_DISPATCH_PROMPT.md's PROVENANCE block
BLOCKERS:           none for ja_JP
READY_STATUS:       ready
```

## Scope this lane covers

36 ja_JP rows in `ASSIGNMENT_MATRIX.tsv` (`bright_presence_tw_seinen` excluded
— zh_TW-only per its `manga_locales` restriction). 16 of these are
REUSE_EXISTING (existing chapter_scripts directories already carry a ja_JP
pen-name author and title — reuse the identity, author the story); 20 are
NEW_SERIES (no existing directory; assign an author from the 255 existing
ja_JP profiles in `config/authoring/manga_authors/*_ja_jp.yaml` — do not invent
a 256th unless none of the existing profiles fit the brand's demographic/topic
after checking).

## Native-voice authoring — this is the one the operator explicitly asked for

Dispatch the `translate-ja` Claude Code agent (Tools: Read, Write, Edit,
MultiEdit, Grep, Glob, Bash) as the native-Japanese AUTHORING voice, per brand
or small batch. Brief it explicitly: **this is original authoring, not
translation of an English draft.** Its usual job is atom translation/QA
repair; here its job is to write native Japanese panel dialogue, narration,
and SFX directly from the brief (brand topic + genre bible + modern reader
context), the way a Japanese-market webtoon/manga writer would, not a
localization of someone else's English scene. Populate `dialogue_lines` /
`narrator_caption_by_locale` fields with `ja_JP` keys per the schema (see the
gold PASS fixture below). If the agent's default mode wants an English source
to translate, override that — instruct it to draft directly in Japanese.

Reference the gold PASS fixture at
`tests/fixtures/manga/story_excellence/pass/healing_ja_jp_genz/chapter_script_writer_handoff.json`
and `pass/dark_fantasy_ja_jp_genz/chapter_script_writer_handoff.json` — both
are ja_JP, both show the exact `modern_reader_context` + panel shape to match
(train platform / conbini / cram school / LINE-chat register; catalyst
realized as the story engine, not decoration).

## Smoke cell (do first, alone)

`cognitive_clarity` (flagship, REUSE_EXISTING,
`artifacts/manga/chapter_scripts/cognitive_clarity__kurose_jin__ja_JP__overthinking__the_loop_is_not_thinking/`,
psychological_thriller genre per the matrix). Rewrite its `ep_001.yaml` as a
full authored `chapter_script_writer_handoff` (this dir's current file also
fails the entry gate today — verify live before assuming). Gate-check, PR, CI
green, merge, then continue to the rest of the wave.

## Per-cell exit criteria

Same as master prompt + the en_US lane's block-fixture self-check list
(`japan_tourist_default` is the ja_JP-specific one to watch hardest — do not
default to samurai/tourist-Japan imagery for a modern-set genre story per the
market guardrail `avoid_tourist_japan` / `avoid_samurai_default_for_modern_scenes`
already encoded in `config/manga/modern_reader_story_doctrine.yaml`'s ja_JP
profile).

## Wave sizing

Same tier-batched approach as the en_US lane (flagship -> core -> niche,
arc-1-only per cell, follow-on wave for arcs 2-4).

## Landing + signals

Per master prompt. `manga48-wave-<n>-ja_JP=<full-SHA>` per wave PR.

## CLOSEOUT_RECEIPT

List every cell completed this wave with its series_id, the ja_JP author
profile used/assigned, and merged SHA.
