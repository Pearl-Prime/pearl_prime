# Lane 07 Handoff — Genre checklists: machine-readable + wired into gates (2026-07-24)

**Lane:** 07 of manga process uplift pack
(`docs/agent_prompt_packs/20260724_manga_process_uplift/07_genre_checklists_wired.md`)
**Agent:** Pearl_Dev + Pearl_Editor · **Branch:** `agent/manga-genre-checklists-wired-20260724`
**Signal (on merge):** `manga-genre-checklists-wired=<merge SHA>`

## Gate check (both satisfied on fresh origin/main)

- `manga-craft-bibles-complete=82ef39572e2751a7bed210d509a394b5d598f0ad` (Lane 05, PR #323) — ancestor of origin/main ✓
- `manga-mc-endurance-research-merged=11c12e5345bff9586d91a50f9c90e92dfe54e27e` (Lane 04, PR #325) — **is** origin/main HEAD ✓

## Delivered

| Artifact | State |
|---|---|
| `config/manga/genre_craft_checklists.yaml` | **NEW** — all 25 canonical genres. Per genre: `story_elements_must`/`should` (bible §1/§3/§6, `evidence_any` tokens), `dialogue_rules` (§4), `panel_grammar_items` (§2/§8, `storyboard_signal_any`), `failure_modes` (§6, `signal_any`), and `mc_items` that **reference** `mc_endurance_checklists.yaml` by key (family + lists — never restated). |
| `phoenix_v4/manga/story_quality/excellence_gate.py` | Extended: `GATE_CRAFT` (`MANGA.STORY.GENRE_CRAFT_CHECKLIST`) via `_check_genre_craft` — hard-blocking, **unweighted** (like RESEARCH/ARCHITECT/ALIAS; never lowers threshold 85). Public `check_genre_craft_checklist()`. |
| `config/manga/mc_endurance_checklists.yaml` | `status: unwired` → **wired** (this module is its real consumer via the by-key `mc_items` reference). |
| `config/manga/story_excellence_gates.yaml` | `genre_craft:` config block (checklist_file, mc_endurance_file, enforce, `must_coverage_floor: 0.5`). |
| `config/manga/gate_registry.yaml` | `MANGA.STORY.GENRE_CRAFT_CHECKLIST` row (BLOCKER). |
| `scripts/ci/check_manga_arc_storyboard.py` | `advisory_panel_grammar()` sub-check (non-blocking; `panel_grammar_items.storyboard_signal_any`; alias-resolves genre id via canonical_genre_list). |
| `docs/specs/MANGA_STORY_EXCELLENCE_REALIZATION_GATE_SPEC.md` | §"Editor pass" (two-stage QA sharing one checklist source + review-artifact schema; **Lane 08 binds here**) + `GATE_CRAFT` gate-id doc. |
| `tests/manga/test_genre_craft_checklists.py` + `tests/fixtures/manga/genre_craft/supernatural_everyday_pass/` | NEW — mutation-proofed. |
| Registry row | `genre_craft_checklists` in `CANONICAL_ARTIFACTS_REGISTRY.tsv`; `mc_endurance_checklists` note updated to WIRED. |

## How the enforcement works (deepens the existing system — no parallel checker)

`_check_genre_craft` runs inside `evaluate_story_excellence` as a 10th gate. It **hard-blocks** on
two mutation-provable conditions:
1. any `failure_modes.signal_any` phrase present on the page (defect present);
2. fewer than `must_coverage_floor` (0.5) of `story_elements_must` items have on-page evidence.

Per the MC-endurance study's binding constraints (Lane 04 handoff):
- **`endurance_mechanics` are NEVER hard-gated** — the 100+-episode signature; completion-first
  genres legitimately lack them.
- **per-family failure cadence is a genre signature, not a global gate** — no universal "MC fails
  every N chapters" rule was created.
- referenced MC items are surfaced for the **Editor pass** + gate report, resolved by key.

## Mutation proof (tests)

- conformant supernatural script → `GATE_CRAFT` PASS;
- strip must-item evidence → BLOCK (`genre_craft_must_items_uncovered`);
- inject a `failure_modes.signal_any` phrase → BLOCK (`genre_craft_failure_mode_present`);
- end-to-end: an existing dark_fantasy pass fixture + injected failure phrase → full report BLOCKED
  with `GATE_CRAFT` in the failed set.

## Verification (in the sparse-cone worktree, from a true green baseline)

- `tests/manga/test_story_excellence_gate.py` — **21/21** (the 6 existing pass fixtures still PASS
  end-to-end now that GATE_CRAFT enforces their genres → calibration confirmed, no regression).
- `tests/manga/test_genre_craft_checklists.py` — **14/14** (config integrity, source-anchor
  resolution for all 25 blocks, mc_items resolve by key, wiring, mutation-proof, storyboard advisory).
- `check_manga_wiring.py` — PASS (50 wired / 8 declared-unwired; mc_endurance flipped to wired,
  genre_craft new+wired).
- `check_manga_arc_storyboard.py` — PASS; `advisory_panel_grammar` verified directly
  (alias `supernatural_mystery`→`supernatural_everyday`; bare plan → advisories, conformant → none).
- Four-way key-space aligned: `genre_craft_checklists` == `canonical_genre_list` ==
  `mc_endurance_checklists.families` == `story_excellence_gates.genre_core_evidence` (all 25).

## Known limitation (honest)

`tests/manga/test_storyboard_consumption.py`: 13/13 logic tests pass; **3 "golden" tests fail with
`FileNotFoundError`** because their fixtures live under `artifacts/manga/chapter_scripts/` which is
outside this session's sparse cone (widening the cone into `artifacts/manga` times out on the busy
shared checkout). These are **sparse-cone artifacts, not code regressions** — my edit to
`check_manga_arc_storyboard.py` only adds `advisory_panel_grammar` + two non-blocking `print` calls
and cannot cause a FileNotFoundError. CI (full checkout) will run them normally.

## For Lane 08 (manga-editor skill)

Bind to `docs/specs/MANGA_STORY_EXCELLENCE_REALIZATION_GATE_SPEC.md` §"Editor pass": load the genre's
block from `genre_craft_checklists.yaml`, resolve the `mc_items` reference against
`mc_endurance_checklists.yaml`, and emit the `manga_chapter_editor_review` artifact (per-item verdict
lines). Do not fork a second checklist source for the human read.

## Untracked-authority note (Lane 04 follow-up)

No checklist item cites the three untracked docs
(`main_character_interaction_grammar_by_genre.md`, `comedy_gag.md`,
`story_quality_gap_audit_modern_reader_worlds.md`). Every `source:` anchor points at an on-main bible
under `docs/research/manga_craft/` (verified by the test suite). No untracked file was landed.

## Cleanup ledger

- Sparse-cone worktree `…/scratchpad/wt-genre-craft` on branch
  `agent/manga-genre-checklists-wired-20260724` — remove after merge.
- One recovered poison event: an interrupted `git sparse-checkout add artifacts/manga/*` (timed out
  materializing) left 70,328 phantom `D` entries for `config/source_of_truth/book_plans_*`
  (cone-excluded scratch). Recovered instantly with `git sparse-checkout reapply`; no committed work
  affected; explicit `git add <file>` used for every commit.
- No branch switches; shared checkout on `agent/bestseller-atom-flow-lanes-20260721` untouched.
- `docs/research/manga_craft/index.md` — re-read immediately before edit (identical to origin/main,
  no drift), one Lane 07 pointer bullet **appended** after Lane 04's cross-cutting entry (LAST in the
  05→04→07 chain); grep-verified single `genre_craft` mention afterward.

## NEXT_ACTION

Land the PR (required checks: parse-sweep + Verify governance). On merge, emit
`manga-genre-checklists-wired=<merge SHA>`. Lane 08 consumes §"Editor pass".
