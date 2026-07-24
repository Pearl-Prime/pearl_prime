# 01 — Research lane: zh_TW modern-reader-world market profile (GATES zh_TW writing)

Paste into a fresh session (Pearl_Research posture; use the `deep-research` skill
for the web-research portion, then a direct edit for the config addition). Part
of the pack at `docs/agent_prompt_packs/20260723_manga_48ep_3catalog_series/`
(see `00_MASTER_DISPATCH_PROMPT.md` for full program context).

## EXECUTE

This is a short, single-wave lane. Do not stop after producing findings prose —
the deliverable is a merged config addition, not a report.

## STARTUP_RECEIPT

```
AGENT:              Pearl_Research
TASK:               zh_TW modern-reader-world market profile (gates zh_TW manga writing)
PROJECT_ID:         proj_manga_catalog_reconciliation_20260426
SUBSYSTEM:          manga_pipeline (config/manga/ authoring, not render code)
AUTHORITY_DOCS:     docs/research/manga_craft/story_quality_gap_audit_modern_reader_worlds.md;
                    config/manga/modern_reader_story_doctrine.yaml;
                    research/2026-03-30_asian-persona-topic-market-fit.md
READ_PATH_COMPLETE: <confirm yes>
WRITE_SCOPE:        config/manga/modern_reader_story_doctrine.yaml (ADD zh_TW block only)
OUT_OF_SCOPE:       the 4 existing market profiles; any chapter_script file
PROVENANCE:         see PROVENANCE block below
BLOCKERS:           none known
READY_STATUS:       ready
```

## Why this lane exists

`config/manga/modern_reader_story_doctrine.yaml` (landed 2026-07-18, see
`docs/research/manga_craft/story_quality_gap_audit_modern_reader_worlds.md`)
defines concrete "genre engine collides with a modern reader-world object"
mechanics (the operator's "magic app / commuter train to a fantasy world"
instinct) for exactly four markets: `en_US`, `ja_JP`, `zh_CN`, `fr_FR`. It has
**no `zh_TW` entry**. Per Router Operating Principle SS18 ("research: NONE ->
STOP, route a Pearl_Research lane first; nothing is built on an unresearched
premise"), no zh_TW episode may be authored against a zh_CN-borrowed profile
without either (a) this lane landing a real zh_TW profile, or (b) an explicit
operator OPD accepting the zh_CN profile as an interim stand-in for the pilot
cell only.

## Mission

1. Research zh_TW (Taiwan) Gen Z / Gen Alpha reader-world touchpoints, parallel
   in depth to the existing 4 market profiles. Reuse what already exists first:
   `research/2026-03-30_asian-persona-topic-market-fit.md` SS1 (zh-TW section,
   already cited in `config/manga/locale_genre_allocations.yaml`'s zh_TW genre
   rows — read it before running new web searches) and
   `docs/CJK_CATALOG_PLAN.md` TW-specific rows (hybrid/BD literary-influence
   note). Only run NEW web research (`deep-research` skill or `WebSearch`) for
   what those two sources do not already cover: concrete Taiwan-specific daily
   objects/rituals analogous to the ja_JP profile's train-platform/conbini/
   cram-school/LINE-chat list — e.g. MRT commute + EasyCard tap, night-market
   ritual, bubble-tea-app ordering, Readmoo/comic-app reading habits, cram
   school (buxiban) culture, LINE (or Taiwan-common chat app) group norms,
   convenience-store (7-Eleven/FamilyMart Taiwan) rituals distinct from Japan's,
   university dorm/commute patterns. Cite every claim with a source, per this
   repo's research convention (see `docs/MANGA_SERIES_PORTFOLIO_RESEARCH.md`'s
   footer for the citation format to match).
2. Author a `zh_TW` entry in `config/manga/modern_reader_story_doctrine.yaml`
   matching the existing schema exactly (see the `ja_JP` entry as the closest
   structural analog — same fields: market surface rule, market touchpoints,
   market guardrails, audience story rule/touchpoints, genre relevance rule).
   Do not invent a new schema shape; extend the existing one (Router SS9 reuse-
   before-authoring).
3. Add >= 8-10 catalysts under this profile analogous to the existing ~50
   catalysts (grep the file for `catalyst:` blocks to see the pattern), one or
   two per primary genre in zh_TW's allocation (`config/manga/locale_genre_allocations.yaml`
   zh_TW section: psychological_horror, romance_josei_drama, workplace_drama,
   iyashikei, supernatural_mystery, dark_fantasy, cultivation_martial, isekai,
   psychological_thriller, historical_period, school_coming_of_age).
4. Regression-test: `phoenix_v4/manga/modern_reader_context.py` is the
   loader/validator for this file — run its existing test suite
   (`grep -rl modern_reader_context tests/ | xargs -I{} pytest {}`) to confirm
   the new zh_TW block parses and validates cleanly.

## PROVENANCE

```
research:   research/2026-03-30_asian-persona-topic-market-fit.md SS1 zh-TW;
            docs/CJK_CATALOG_PLAN.md TW rows; NEW web research for the gap
            named above (cite sources)
documents:  docs/research/manga_craft/story_quality_gap_audit_modern_reader_worlds.md
builds_on:  config/manga/modern_reader_story_doctrine.yaml (ADD zh_TW entry,
            same schema as en_US/ja_JP/zh_CN/fr_FR — do not restructure the file)
inventory:  EXTENDS. The 4 existing market profiles are untouched.
```

## Landing + signal

MERGED (small config-only PR, CI green, squash-merged) or BLOCKED with the
specific gap named. Signal: `zhtw-modern-reader-doctrine-landed=<full-SHA>`.
This signal is the gate check `04_WRITER_LANE_ZH_TW_PROMPT.md` verifies before
authoring any zh_TW episode.

## CLOSEOUT_RECEIPT

Standard template. NEXT_ACTION should point back to
`04_WRITER_LANE_ZH_TW_PROMPT.md` with the merged SHA filled into its gate
check.
