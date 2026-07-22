# 00 — MASTER DISPATCH: 48-Episode Manga Series, 3 Catalogs, Genre-Native Self-Help

Paste this into a fresh Pearl_PM chat. It is the lead prompt of a pack under
`docs/agent_prompt_packs/20260723_manga_48ep_3catalog_series/`. Companion files in
this pack (read before dispatching child lanes):
- `ASSIGNMENT_MATRIX.tsv` — pre-computed brand x catalog -> genre assignment (111
  rows: 53 REUSE_EXISTING, 56 NEW_SERIES, 2 EXCLUDED). Regenerate with
  `generate_series_assignment_matrix.py` if canonical_brand_list.yaml or
  locale_genre_allocations.yaml change before this lands.
- `01_RESEARCH_GAP_ZHTW_MODERN_READER_PROMPT.md` — MUST complete before any zh_TW
  writer lane opens (research=NONE gate, see PROVENANCE below).
- `02_WRITER_LANE_EN_US_PROMPT.md`, `03_WRITER_LANE_JA_JP_PROMPT.md`,
  `04_WRITER_LANE_ZH_TW_PROMPT.md` — per-catalog writer fan-out prompts.

---

## EXECUTE

Do not summarize this prompt back to the operator. Do not produce a plan-only
response and stop. Do not stop after opening one PR "for review" — the turn
contract ends only on a named signal (below) or one concrete BLOCKER with
evidence. This is a multi-wave PROGRAM, not a single-turn deliverable — the
turn contract applies per wave, not to the whole 48-episode x ~109-cell scope
at once. Ramp: smoke (1 cell, full loop, gates green) -> pilot (3 cells, one
per catalog) -> scale (remaining cells in PR-size-capped waves). Never claim
"all 48 episodes for all brands are written" without a per-cell CLOSEOUT and a
merged SHA — partial waves are the honest default here.

## STARTUP_RECEIPT (emit before doing anything)

```
AGENT:              Pearl_PM
TASK:               48-episode / 4-arc manga series, genre-native embedded
                     self-help, 1 series per brand per catalog, en_US/ja_JP/zh_TW
PROJECT_ID:         proj_manga_catalog_reconciliation_20260426 (extend; do not
                     fork a parallel catalog-planning project)
SUBSYSTEM:          manga_pipeline (owner Pearl_Dev per SUBSYSTEM_AUTHORITY_MAP.tsv)
                     -- writing/authoring itself is Tier-1 Claude Code prose
                     generation per CLAUDE.md LLM Tier Policy, not Pearl_Dev code
AUTHORITY_DOCS:     docs/agent_brief.txt; docs/PROGRAM_STATE.md; CLAUDE.md
                     (Manga Vision-Conformance Doctrine + LLM Tier Policy);
                     specs/MANGA_CATALOG_RECONCILIATION_SPEC.md;
                     docs/GENRE_PORTFOLIO_PLAN.md; docs/CJK_CATALOG_PLAN.md;
                     docs/US_CATALOG_PLAN.md; docs/MANGA_SERIES_PORTFOLIO_RESEARCH.md;
                     docs/research/manga_craft/index.md (+ the 20 per-genre bibles);
                     docs/research/manga_craft/story_quality_gap_audit_modern_reader_worlds.md
READ_PATH_COMPLETE: <confirm yes after reading all of the above + this pack>
WRITE_SCOPE:        artifacts/manga/chapter_scripts/<series_id>/ep_0XX.yaml (new +
                     rewritten stub files); config/manga/modern_reader_story_doctrine.yaml
                     (zh_TW market profile ADD only, lane 01); this pack's own
                     status notes
OUT_OF_SCOPE:       phoenix_v4/manga/* render/pipeline code (image rendering,
                     bubble rendering, assemble_from_bank.py); config/manga/gate_registry.yaml;
                     canonical_brand_list.yaml / locale_genre_allocations.yaml (READ
                     only — this program consumes them, does not edit them);
                     any book-pipeline (Pearl_Prime) file
PROVENANCE:
  research:   docs/MANGA_SERIES_PORTFOLIO_RESEARCH.md (industry cadence/portfolio
              benchmarks); docs/research/manga_craft/*.md (20 genre craft bibles,
              48-volume arc shapes); docs/research/manga_craft/story_quality_gap_audit_modern_reader_worlds.md
              (modern-reader-world hook doctrine: phones/trains/apps/group chats
              MUST become the genre engine, never decoration — this is the
              "magic app / commuter train" mechanic the operator asked for,
              already researched and CI-gated); research/2026-03-30_*-persona-topic-market-fit.md
              (cited per-locale in locale_genre_allocations.yaml). GAP: zh_TW has
              NO modern-reader-context market profile in
              config/manga/modern_reader_story_doctrine.yaml (only en_US/ja_JP/
              zh_CN/fr_FR exist) -- STOP and run 01_RESEARCH_GAP_ZHTW_MODERN_READER_PROMPT.md
              before any zh_TW episode is authored. Do not proceed on zh_TW
              writing with a zh_CN-borrowed profile without that lane's ratified output.
  documents:  docs/GENRE_PORTFOLIO_PLAN.md; docs/CJK_CATALOG_PLAN.md;
              docs/US_CATALOG_PLAN.md; specs/MANGA_CATALOG_RECONCILIATION_SPEC.md;
              docs/specs/MANGA_100PCT_PRODUCTION_ROADMAP_2026-07-03.md;
              CLAUDE.md Manga Vision-Conformance Doctrine (six-layer taxonomy +
              3 CI-enforced drift classes)
  builds_on:  artifacts/planning/world_14x37_books_manga_20260715/manga_genre_allocation_14x37.tsv
              (AUTHORITATIVE per-brand genre DNA, ratified per specs/MANGA_BRAND_DNA_ANTI_SPAM_SPEC.md
              -- this program's ASSIGNMENT_MATRIX.tsv sources its genre_id column from
              here, not from a fresh heuristic; see "Cross-plan reconciliation" below);
              config/manga/canonical_brand_list.yaml (37-brand Path X canon);
              config/manga/locale_genre_allocations.yaml (per-locale genre-share cross-
              check only); config/manga/modern_reader_story_doctrine.yaml;
              docs/agent_prompt_packs/manga_arc_storyboard_planner.md (mandatory
              storyboard-then-script sequence -- schemas/manga/arc_storyboard_plan.schema.json,
              scripts/ci/check_manga_arc_storyboard.py); docs/specs/MANGA_STORY_EXCELLENCE_REALIZATION_GATE_SPEC.md
              (governs scripts/manga/validate_story_excellence.py, the authority behind
              the story_excellence pass/block fixture corpus); schemas/manga/chapter_script_writer_handoff.schema.json;
              scripts/ci/check_manga_story_authored.py (entry gate); existing
              artifacts/manga/chapter_scripts/ series identities (53 cells -- REUSE, do
              not rename or fork a second series for the same brand+locale)
  inventory:  EXTENDS ONLY. Every existing chapter_scripts/ directory, author
              profile (config/authoring/manga_authors/), and craft bible stays
              exactly as-is. This program never deletes or renames an existing
              series identity; a REUSE_EXISTING row means "author into this
              listing," not "replace it."
BLOCKERS:           zh_TW modern-reader doctrine gap (see PROVENANCE.research);
                    zh_TW native pen-name author pool is thin (2 profiles in
                    config/authoring/manga_authors/: lin_yuxi_zh_tw_002,
                    shen_yejing_zh_tw_001) vs 255 ja_JP profiles -- flag as
                    Q-MANGA48-ZHTW-AUTHORS-01 (default: reuse the 2 existing +
                    author 3-5 more zh_TW pen names in the same lane before
                    scaling zh_TW past the pilot cell)
READY_STATUS:       ready (smoke wave); blocked on 01 for zh_TW past smoke
```

## Live-truth reconciliation (Router SS11 — re-verify, do not trust this prompt's numbers)

Before dispatching any writer lane:
1. `git fetch origin` and re-read `docs/PROGRAM_STATE.md`'s manga section for a
   fresher "LAST VERIFIED" SHA than `a08b8af17` (2026-07-22, cited when this pack
   was authored). If it moved, re-read the manga status block before proceeding.
2. Re-run `python3 docs/agent_prompt_packs/20260723_manga_48ep_3catalog_series/generate_series_assignment_matrix.py`
   and diff against the committed `ASSIGNMENT_MATRIX.tsv` in this pack. If any
   row's `status` changed from `NEW_SERIES` to something else (i.e. someone
   authored that cell since), that is SUCCESS — stand down that cell, do not
   re-author, report the delta in your CLOSEOUT.
3. For every cell you are about to write into, re-run
   `PYTHONPATH=. python3 scripts/ci/check_manga_story_authored.py --chapter-script <path>/ep_001.yaml`
   yourself first — if it already PASSES, that cell is done; skip it.
4. `gh pr list --search "manga" --state open` and the sibling-PR search
   (docs/agent_brief.txt SS1) before opening any new PR — another session may
   already be mid-flight on an overlapping brand or locale.
5. **Check PR #94 and PR #102 merge state before the storyboard/validate
   steps** (verified OPEN, not merged, as of 2026-07-23 — re-check live):
   PR #94 lands the `cultivation_martial` craft bible (a dependency for any
   `cultivation_martial`-genre cell). PR #102 fixes two real bugs in the
   pipeline this pack's writer lanes depend on: (a)
   `phoenix_v4/manga/prompts/chapter_writer_prompt.txt` was missing the
   instruction to preserve `modern_reader_context` — now fixed; (b)
   `config/manga/story_excellence_gates.yaml`'s `strategy_bank_by_genre` had
   10 keys (`essay`, `food`, `family`, `procedural`, `comedy`, `school`,
   `memoir`, `social_issue`, `graphic_medicine`, `battle_internal`) pointing
   at strategy-bank files that don't exist — remapped to real files
   (`iyashikei_strategies.yaml`, `shojo_strategies.yaml`,
   `psychological_thriller_strategies.yaml`, `historical_period_strategies.yaml`,
   `shonen_strategies.yaml`, `seinen_strategies.yaml`,
   `workplace_drama_strategies.yaml`). If PR #102 has not merged when a writer
   lane runs `validate_story_excellence.py`, that gate may fail for reasons
   that have nothing to do with the episode's writing quality — do not
   mis-diagnose a PR-#102-shaped failure as a craft problem in the story.
6. **Genre-vocabulary mismatch — resolve before trusting a direct key lookup.**
   `story_excellence_gates.yaml`'s `strategy_bank_by_genre` keys use the
   OLDER `config/manga/manga_taxonomy.yaml` genre-family vocabulary (`battle`,
   `romance`, `workplace`, `healing`, `mystery`, `horror`, `sports`, `school`,
   `cultivation`, etc.) — NOT the `genre_id` vocabulary
   `ASSIGNMENT_MATRIX.tsv` uses (sourced from `locale_genre_allocations.yaml` /
   the 14x37 DNA file: `workplace_drama`, `iyashikei`, `cultivation_martial`,
   `school_coming_of_age`, `psychological_horror`, `action_battle`, etc.).
   These are DIFFERENT strings that appear to correspond semantically
   (`workplace`~`workplace_drama`, `cultivation`~`cultivation_martial`,
   `school`~`school_coming_of_age`) but a same-string key lookup will NOT
   resolve. Do not assume the mapping — before running
   `validate_story_excellence.py` / `plan_genre_scene_coverage.py` for a
   cell, find and use whatever resolution function the actual code path
   calls (grep `strategy_bank_by_genre` usage in `phoenix_v4/manga/` and
   check `config/manga/canonical_genre_list.yaml`'s `alias_of` field first —
   it is the closest existing reconciliation artifact, though its stated
   scope is taxonomy-vs-pacing reconciliation, not this locale-allocation
   vocabulary specifically). If no resolver exists for a given genre_id,
   that is a real gap — file it as a blocker for that cell rather than
   guessing a key.

## Cross-plan reconciliation (read before dispatching any writer lane)

An existing, already-executed planning pack (`docs/agent_prompt_packs/20260715_world_14x37_books_manga_series_plan/`,
artifacts at `artifacts/planning/world_14x37_books_manga_20260715/`) already
ratified a full 14-market x 37-brand manga portfolio TARGET: per brand, 16
(flagship) / 9 (core) / 5 (niche) series, **each 24 episodes**, with a
brand-level genre-weight DNA (`manga_genre_allocation_14x37.tsv`) marked
`production_status: planned_not_proven` — planning coverage, not authored
prose. This program does NOT duplicate that planning work; it is a narrower,
concrete AUTHORING slice on top of it:

- **Genre choice:** `ASSIGNMENT_MATRIX.tsv`'s `genre_id` is sourced from that
  file's top-weighted genre per brand (`genre_source=14x37_dna` for 109/109
  live cells) — reuse, not a fresh pick. `locale_mix_check` cross-references
  `locale_genre_allocations.yaml`'s per-market demand mix: 96 cells read `OK`
  (the brand's DNA genre is also a demanded genre in that market); 13 read
  `FLAG_NOT_IN_LOCALE_MIX` — these two SSOTs encode different things
  (brand-level identity DNA vs market-level reader demand) and can
  legitimately disagree. For flagged cells, default to the brand DNA genre
  (it is the more brand-identity-authoritative, anti-spam-audited source) but
  note the flag in that cell's CLOSEOUT rather than silently resolving it.
- **Episode count:** the 14x37 plan's per-series target is 24 episodes; the
  operator's instruction THIS session is explicit and more recent: 48
  episodes with a 4-arc-of-12 structure. Treat this as an explicit operator
  override for the FIRST/flagship series of each brand's eventual portfolio,
  not a silent divergence — log it as `Q-MANGA48-EPCOUNT-01` (default: 48
  episodes as instructed; this series counts toward that brand's series_target
  count as roughly "2 series' worth" of episode budget until Pearl_Architect
  reconciles `episodes_per_series_target` for flagship series specifically).
  Do not average down to 24 without an explicit operator walk-back.
- Do not re-run lanes 01-09 of the 20260715 pack; this program starts from
  their output.

## Mission

Write ONE 48-episode manga/webtoon series per brand, per catalog, for the
en_US, ja_JP, and zh_TW catalogs (37 brands x 3 catalogs, minus 2 cells where
`bright_presence_tw_seinen` is contractually zh_TW-exclusive per
`config/manga/canonical_brand_list.yaml` manga_locales = 109 series total).
Every series carries:

- **A 4-arc structure, one arc per 12 episodes** (episodes 1-12, 13-24, 25-36,
  37-48), each arc escalating stakes and moving the series toward "more
  interesting" territory per the operator's brief — i.e. arc 1 is NOT the same
  shape repeated four times; arc 4 must feel like a materially bigger story
  than arc 1 (world widens, stakes personalize, relationships deepen, the
  self-help topic's mastery deepens). Use the per-genre `arc_shape_hint` column
  in `ASSIGNMENT_MATRIX.tsv` (sourced from each craft bible's SS7 48-volume
  shape) as the starting shape — adapt, do not invent from nothing, and do not
  force a stakes-escalation shape onto lanes whose bible says otherwise
  (iyashikei, josei_adult_memoir, kodomomuke are seasonal/diaristic by design;
  respect that register rather than bolting on false stakes).
- **A genre-native self-help topic embedded as subtext, never as teacher-mode.**
  The brand's `primary_topic` (+ secondary_topics) from `ASSIGNMENT_MATRIX.tsv`
  is the wellness anchor. It must surface through vessel characters, genre
  mechanics, and consequence — never as an explicit lesson, never with a named
  real-world teacher (Ahjan / Sai Ma / Adi Da) appearing in panel text.
  `scripts/ci/check_manga_story_authored.py` hard-blocks any panel naming a
  brand teacher; this is not optional guidance, it is a CI gate.
- **A concrete "modern reader world" hook realized as genre engine, not
  decoration** — the operator's "magic app / commuter train to a fantasy
  world" instinct is already a first-class, researched, CI-adjacent doctrine:
  `config/manga/modern_reader_story_doctrine.yaml` + the gold-standard PASS
  fixture at `tests/fixtures/manga/story_excellence/pass/healing_ja_jp_genz/chapter_script_writer_handoff.json`
  (a lost train commute + a saved conbini receipt become the grief-vessel, not
  set dressing). Do NOT write a "mention-only" version of this — see the block
  fixtures at `tests/fixtures/manga/story_excellence/block/mention_only_phone_train/`
  and `.../dark_fantasy_portal_no_cost/` for the exact failure mode the QC gate
  rejects (portal/app appears with zero cost or consequence).
- **Genre-appropriate pacing** per `config/manga/manga_pacing_by_genre.yaml`
  (words/page, silent-panel ratio, reaction-shot frequency by genre family) for
  print-register lanes, and vertical-scroll conventions (one long "page" of
  15-35 panels per episode is normal) for webtoon-format lanes
  (`webtoon_vertical_romance`, `webtoon_vertical_drama`, `digital_ground`'s
  manhwa register). If a genre's avg length/duration is not covered by that
  file or the craft bible, that is a real research gap — route a short
  Pearl_Research lane for that one genre rather than guessing (Router SS18: no
  code/content on an unresearched premise).

## Deliverable shape per cell (per brand x catalog)

**Mandatory sequence per episode (do not skip the storyboard step and jump
straight to dialogue — this is an existing, reused contract, not new
process):** per `docs/agent_prompt_packs/manga_arc_storyboard_planner.md`,
(1) read the genre craft bible + `config/manga/genre_scene_templates/<genre>.yaml`
+ `config/source_of_truth/manga_story_strategies/<genre>_strategies.yaml` +
`config/manga/main_character_interaction_grammar.yaml`; (2) plan an
`arc_storyboard.yaml` (logline, stakes_now/stakes_end, page-turn promises,
panel board with `story_move`/`visual_proof`/`information_delta`) at
`artifacts/manga/arc_storyboards/<series_id>/<episode_id>.arc_storyboard.yaml`
and gate it with
`PYTHONPATH=scripts/ci:. python3 scripts/ci/check_manga_arc_storyboard.py --arc-plan <path>`;
(3) only then author the `chapter_script_writer_handoff` labeling moves already
visible on the board, setting `arc_storyboard_ref` to the plan path; (4) run
`PYTHONPATH=. python3 scripts/manga/validate_story_excellence.py --help`
first to confirm current flags (verified 2026-07-23: it requires BOTH
`--story-handoff <path>` — the story/series-level object, not the per-episode
file — AND `--chapter-script <path>`; `--production` for the strict gate,
`--json` for machine-readable output) — this is the
`docs/specs/MANGA_STORY_EXCELLENCE_REALIZATION_GATE_SPEC.md` gate, the
authority behind the pass/block fixtures cited throughout this pack — and
`PYTHONPATH=. python3 scripts/manga/plan_genre_scene_coverage.py --genre <genre> --story <path>`.
Writing dialogue before the storyboard board exists is a named anti-pattern in
that doc ("words paper over empty pictures") — treat it as a hard rule.

Each `chapter_script_writer_handoff` episode file
(`artifacts/manga/chapter_scripts/<series_id>/ep_0XX.yaml`) must:
- set `artifact_type: chapter_script_writer_handoff` (existing stub files in
  REUSE_EXISTING cells currently do NOT — that is exactly why they fail the
  gate; fix this field as part of authoring, do not create a second file);
- carry >= 6 real authored panels (the entry floor `_MIN_PANELS`; genre pacing
  tables above typically demand far more per episode — treat 6 as the CI floor,
  not the craft target);
- carry NO stub markers (`{brace}`, TODO/TBD/FIXME/XXX/HOOK/PLACEHOLDER/LOREM
  IPSUM/CHAPTER_END_HOOK — `scripts/ci/check_manga_story_authored.py` greps
  for these verbatim);
- carry a `modern_reader_context` block matching the target locale's market
  profile (see PROVENANCE.research gap above for zh_TW);
- never name a brand teacher in panel text.

Run the gate yourself before calling a cell done:
```
PYTHONPATH=. python3 scripts/ci/check_manga_story_authored.py --chapter-script artifacts/manga/chapter_scripts/<series_id>/ep_0XX.yaml
```
This is the ENTRY gate only (plan-vs-story). Also self-check each episode
against the `story_excellence` block-fixture failure modes (mention-only
props, no-cost portals, generic "something shifted" healing, poster-not-
relationship social issues, stats-only sports scenes with no body/team stakes)
before marking a cell complete — these are the actual craft bar, not just the
CI floor.

## Fan-out plan (native-speaker subagents, Tier-1 Claude Code per CLAUDE.md)

Per CLAUDE.md's LLM Tier Policy, ALL prose generation here — including ja_JP
and zh_TW — is Tier 1 (Claude Code, human-reviewed), never a paid API and
never unattended Qwen/Gemma. "Native speaker subagent" means: dispatch the
Claude Code `translate-ja` agent for ja_JP and `translate-zh-tw` agent for
zh_TW as the native-language AUTHORING voice (not merely translating an
English draft — brief them explicitly to author original Japanese / Traditional
Chinese panel text, matching the market_surface_rule in each locale's
modern_reader_context). For en_US, dispatch general-purpose Claude subagents
directly (no translation agent needed).

Open each catalog's dedicated writer-lane prompt as its own child session (one
per catalog is the minimum viable split; further split by brand-tier batch
inside that lane if concurrency requires it — never more than ~10-15 cells'
worth of new files in one PR per push-guard/governance file caps):
1. `02_WRITER_LANE_EN_US_PROMPT.md` — 37 cells (3 flagship + 16 core + 18 niche,
   0 excluded).
2. `03_WRITER_LANE_JA_JP_PROMPT.md` — 36 cells (bright_presence_tw_seinen
   excluded).
3. `01_RESEARCH_GAP_ZHTW_MODERN_READER_PROMPT.md` THEN
   `04_WRITER_LANE_ZH_TW_PROMPT.md` — 36 cells, gated on 01's signal.

## Ramp (mandatory — do not skip stages)

1. **Smoke (1 cell):** pick `en_US / stillness_press` (flagship, REUSE_EXISTING,
   already has a partial episode at
   `artifacts/manga/chapter_scripts/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/`).
   Author ep_001 fully (arc 1 opener), pass `check_manga_story_authored.py`,
   self-check against story_excellence failure modes, open a PR, get CI green,
   merge. This proves the whole loop (schema, gate, PR, CI) before scaling.
2. **Pilot (3 cells, one per catalog):** the smoke cell's full 12-episode arc 1
   + one ja_JP cell (`ja_JP / cognitive_clarity`, REUSE_EXISTING) full arc 1 +
   one zh_TW cell (after lane 01 lands) full arc 1. Merge each as its own PR.
   This is the operator's first look-packet — do NOT scale past this without
   an operator read on voice/quality (Router SS16: a read-approval on the genre
   voice, once per catalog, then frozen as the quality bar the rest of the
   wave defends).
3. **Scale (remaining ~106 cells):** batch by tier (flagship first, then core,
   then niche) and by catalog, arc-1-only (12 episodes) per cell per wave, PRs
   capped at a sane file count (~10-15 series' worth of new/changed episode
   files each). Arcs 2-4 for each series are explicitly a FOLLOW-ON wave after
   every brand has at least an authored arc 1 in every catalog — do not go
   deep (arcs 2-4) on a few brands before every brand has arc 1, unless the
   operator overrides this ordering.

## Landing contract (every wave, no exceptions)

MERGED (PR opened, required checks green incl. Drift detectors' story-authored
gates, squash-merged, signal emitted) or BLOCKED (one concrete blocker + work
pushed to a remote branch, never left local-only). Cleanup ledger every wave.
Update `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` under
`proj_manga_catalog_reconciliation_20260426` with a new row for this program
(e.g. `ws_manga_48ep_3catalog_writing_20260723`), and update
`docs/PROGRAM_STATE.md`'s manga section on the smoke + each pilot merge
(milestone merges only — do not spam it every wave).

## Signal tokens

- `manga48-smoke-pass=<full-SHA>` — smoke cell merged + gate green.
- `manga48-pilot-<catalog>-pass=<full-SHA>` — each catalog's pilot cell merged.
- `manga48-wave-<n>-<catalog>=<full-SHA>` — each scale wave's merge SHA.

## CLOSEOUT_RECEIPT (emit at the end of every wave)

Use the standard template (docs/SESSION_UNITY_PROTOCOL.md). Label every claim
on the six-layer manga taxonomy (CLAUDE.md Manga Vision-Conformance Doctrine
SS1) — an authored, gate-passing episode is CODE-WIRED/EXECUTED-REAL at best;
it is not PROVEN-AT-BAR until an operator blind-read approves the voice per
catalog (Router SS16). Never say "48 books written" without naming exactly
which cells, which arcs, and citing the merged SHA per cell.

## Do not

- Do not invent a new brand, genre, or catalog outside the 37 x 3 canon without
  an explicit operator ratification (this is Path X canon, frozen).
- Do not delete, rename, or fork a duplicate of any REUSE_EXISTING series
  identity — author into the existing directory/id.
- Do not write zh_TW episodes before lane 01 lands (or an explicit operator
  override accepting the zh_CN-borrowed doctrine as an interim stand-in,
  logged as an OPD).
- Do not touch `phoenix_v4/manga/*` rendering code, `config/manga/gate_registry.yaml`,
  or the two source-of-truth config files this program only reads.
- Do not claim "system working" or "bestseller" for any cell on gate-PASS alone
  (CLAUDE.md doctrine — gate-PASS != done).
