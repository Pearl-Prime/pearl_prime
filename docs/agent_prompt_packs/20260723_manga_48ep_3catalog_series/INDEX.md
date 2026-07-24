# 48-Episode Manga Series, 3 Catalogs, Genre-Native Self-Help — Prompt Pack Index

Date: 2026-07-23
Owner: Pearl_PM (dispatcher) + Pearl_Writer/native-language writer subagents (lanes)
Mode: Prompt-pack execution, live authoring (not planning-only)

## Program goal

Author ONE 48-episode manga/webtoon series (4 arcs x 12 episodes, escalating
stakes) per canonical brand, per catalog, for **en_US, ja_JP, zh_TW** (109 live
cells of 111 possible; 2 excluded by a brand's `manga_locales` restriction).
Each series carries a genre-native embedded self-help topic (per brand DNA),
no teacher-mode, and a concrete "modern reader world" hook realized as genre
engine per `config/manga/modern_reader_story_doctrine.yaml`.

## Live truth anchor used when this pack was authored

`docs/PROGRAM_STATE.md` LAST VERIFIED @ `origin/main` `a08b8af17b4e7b37ac36be7d4c1c8f6049e5ee37`
(2026-07-22). Re-verify against a fresher SHA before dispatching (see
`00_MASTER_DISPATCH_PROMPT.md` "Live-truth reconciliation").

## Source request summary

Operator (`/piper` invocation, 2026-07-23): write 1 series x 48 manga
episodes per brand, one brand per catalog, for en_US/ja_JP/zh_TW (~37-40
brands), a genre per brand (repeat genres if brands > genres available), a
progressive series arc every 12 episodes, self-help embedded subtly (no
teacher mode), using research on best genre/TV/comic/series craft including
"reader's living experience" hooks (magic app / commuter-train-to-fantasy-
world), and max native-speaker subagents for the writing, sized per genre
avg length/duration research.

## Prompt count

6 files: 1 master dispatcher + 1 gating research lane + 3 catalog writer
lanes + 1 recurring QA/audit lane. Plus 2 generated data artifacts (the
assignment-matrix generator script + its TSV output) that the dispatcher and
writer lanes all read.

## Wave order

| Wave | Lane | Owner | Substrate | Output | Status |
|---|---|---|---|---|---|
| 0 | `00_MASTER_DISPATCH_PROMPT.md` live-truth + scope reconciliation | Pearl_PM | clean origin/main read | reconciled scope, re-verified matrix | prompt-ready |
| 0 | `01_RESEARCH_GAP_ZHTW_MODERN_READER_PROMPT.md` | Pearl_Research | after wave 0 | `zh_TW` entry in `modern_reader_story_doctrine.yaml`, signal `zhtw-modern-reader-doctrine-landed` | prompt-ready; GATES all zh_TW writing |
| 1 (smoke) | `02_WRITER_LANE_EN_US_PROMPT.md` smoke cell | native-voice Claude subagent | after wave 0 | 1 authored+gated en_US episode, signal `manga48-smoke-pass` | prompt-ready |
| 1 (smoke) | `03_WRITER_LANE_JA_JP_PROMPT.md` smoke cell | `translate-ja` agent | after wave 0 | 1 authored+gated ja_JP episode | prompt-ready |
| 1 (smoke) | `04_WRITER_LANE_ZH_TW_PROMPT.md` smoke cell | `translate-zh-tw` agent | after lane 01 signal | 1 authored+gated zh_TW episode | prompt-ready; gated |
| 1.5 (pilot) | each writer lane, full arc 1 (12 eps) on 1 cell per catalog | same agents | after each lane's smoke merges | 3 pilot series arc-1, operator look-packet gate (Router SS16) | prompt-ready |
| 2 (scale) | each writer lane, tier-batched waves (flagship -> core -> niche), arc-1-only | same agents | after pilot operator read | remaining ~106 cells' arc 1 | prompt-ready |
| 3 (QA per wave) | `05_QA_AUDIT_LANE_PROMPT.md` | Pearl_PM/QA posture | after each scale wave merges | re-run gates, look-packet, findings | prompt-ready |
| follow-on | arcs 2-4 for every cell | same agents | after every brand has arc 1 in every catalog | full 48-episode series per cell | not yet dispatched — a later pack |

## Lane dependencies

- Lane 01 (zh_TW research) blocks ALL zh_TW writing (lane 04) past its smoke
  cell exemption note; does not block en_US (lane 02) or ja_JP (lane 03).
- Lanes 02 and 03 have no cross-dependency and may run fully in parallel.
- Lane 05 (QA) depends on the wave it audits having merged PRs to check.
- Pilot stage (1.5) in each lane is an operator-read gate before that lane's
  scale stage (2) — do not skip.

## Owners and subsystem authority

`manga_pipeline` (Pearl_Dev, per `SUBSYSTEM_AUTHORITY_MAP.tsv`) owns the
render/gate CODE this program consumes but does not modify. The AUTHORING
itself is Tier-1 Claude Code prose generation per `CLAUDE.md`'s LLM Tier
Policy — dispatched as: general-purpose Claude subagents (en_US), the
`translate-ja` Claude Code agent repurposed for native authoring (ja_JP), the
`translate-zh-tw` Claude Code agent repurposed for native authoring (zh_TW).
Never a paid API, never unattended Qwen/Gemma for this authoring work.

## Substrate for every lane

Read from `origin/main` (or a fetched-current local clone); no worktree
required for the writer lanes (they only add new files under
`artifacts/manga/chapter_scripts/` and `artifacts/manga/arc_storyboards/`, not
touching the huge shared tree's LFS assets) — a plain feature branch off
`origin/main` is sufficient. If disk is under 20 GiB free, use the plumbing
pattern (temp index off `origin/main^{tree}`) per
`docs/PROMPT_ROUTER_OPERATING_MANUAL.md` SS10, not a fresh worktree.

## Expected branches, PRs, proof roots, outputs

- Branches: `agent/manga48-<catalog>-<wave-name>-20260723` per wave per
  catalog (e.g. `agent/manga48-en-us-smoke-20260723`).
- Proof roots: `artifacts/manga/chapter_scripts/<series_id>/ep_0XX.yaml`;
  `artifacts/manga/arc_storyboards/<series_id>/ep_0XX.arc_storyboard.yaml`;
  `artifacts/qa/manga_48ep_3catalog_look_packet_<catalog>_<wave>.md`.
- Handoffs: `artifacts/coordination/handoffs/manga48_<catalog>_<wave>_2026-07-23.md`.

## Hot-file conflict notes

`config/manga/modern_reader_story_doctrine.yaml` is touched by exactly ONE
lane (01, zh_TW addition) — serialize; no writer lane edits this file.
`artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` and `docs/PROGRAM_STATE.md`
are hot shared files per `docs/agent_brief.txt` SS1 — one actor at a time,
milestone updates only (smoke + each pilot + program completion), not every
wave.

## Required signal tokens

`zhtw-modern-reader-doctrine-landed`, `manga48-smoke-pass`,
`manga48-pilot-<catalog>-pass`, `manga48-wave-<n>-<catalog>`,
`manga48-qa-wave-<n>-<catalog>`. Full SHA required on every token.

## Cleanup and handoff requirements

Standard MERGED-or-BLOCKED landing contract per
`docs/PROMPT_ROUTER_OPERATING_MANUAL.md` SS9 in every lane prompt. No local
branches or worktrees left behind; remote branches deleted after squash-merge.

## Final audit lane

`05_QA_AUDIT_LANE_PROMPT.md`, run after every scale wave, plus one
program-level pass after the last wave listing every cell x arc completed,
every cell still outstanding, and citing every merged SHA.

## Related existing work (read, do not duplicate)

- `docs/agent_prompt_packs/20260715_world_14x37_books_manga_series_plan/` +
  `artifacts/planning/world_14x37_books_manga_20260715/` — the ratified
  14-market x 37-brand PLANNING pack this program's genre assignments are
  sourced from (see `00_MASTER_DISPATCH_PROMPT.md` "Cross-plan
  reconciliation"). That pack produces matrices/percentages; it does not
  author prose. This pack does.
- `docs/agent_prompt_packs/manga_arc_storyboard_planner.md` — the existing
  storyboard-then-script contract this program's writer lanes must follow
  (not a new process; reused as-is).
- `docs/agent_prompt_packs/20260718_manga_story_excellence_all_genres_qa/` —
  check before lane 05 runs; likely has reusable QA tooling/patterns.
- PR #94 (`agent/manga-m3-cultivation-craft-bible-20260723`, open as of
  2026-07-23) closes the last craft-bible gap (`cultivation_martial`) this
  program's genre assignments depend on for zh_TW/zh_CN cells — verify it has
  merged before authoring any `cultivation_martial`-genre cell; if still open,
  that cell is BLOCKED on this PR, not on this pack's own lanes.
