# Manga Vision-Conformance Refresh — 2026-07-22

**Author:** Pearl_QA (`agent/manga-vision-reaudit-20260722`), single-session verification pass.
**Base:** `origin/main` at `1020acd874` (`feat(localization): scaffold translation-quality pipeline (zh-CN mirror prioritized) (#66)`, 2026-07-23 01:26:36 +0800).
**Supersedes:** `artifacts/qa/MANGA_VISION_CONFORMANCE_AUDIT_2026-07-03.md` (superseded-provenance; cited, not re-derived, for every axis this session did not independently re-verify).
**Acceptance layers used throughout (never conflated):**
`ABSENT → RESEARCHED → SPECCED → CONFIG-EXISTS → CODE-WIRED → EXECUTED-REAL → PROVEN-AT-BAR`

**Methodology delta from the 07-03 baseline (state this plainly):** the 07-03 audit ran a 41-agent
Workflow fan-out with a dedicated adversarial refutation pass. This refresh is a **single-session
git-plumbing verification pass** — `git show`/`git ls-tree`/`git cat-file` against `origin/main`
(never the working tree, which sits on a diverged local branch), plus one live pytest run for the
axis with the most load-bearing new claim (R5). It is **narrower and less adversarial** than the
07-03 method. Every number below either (a) carries a cited file path / byte count / test result
from this session, or (b) is marked **CARRIED FORWARD, NOT RE-VERIFIED** from the 07-03 baseline —
never presented as freshly confirmed.

---

## 0. Critical finding: the task brief's central claim is UNMERGED

The dispatch for this audit named commit `aad5cf2152` (`feat(manga): assemble_from_bank --bubbles
uses genre-aware bubble_render_v2`, dated 2026-07-22 02:21:51 +0800) as landed evidence that R5's
bubble-rendering lane is now genre-aware. **This commit is not an ancestor of `origin/main`.**

```
git merge-base --is-ancestor aad5cf2152 origin/main → exit 1 (NOT an ancestor)
git branch -r --contains aad5cf2152 → origin/agent/bestseller-atom-flow-lanes-20260721 (only)
gh pr list --search manga --state open → no PR references this branch/commit
```

The same is true of two other recent-looking commits observed in this shared working tree's `git
log` (`eca2842a18`, `386bf02bef`) — both are local/pushed-branch-only, not on `origin/main`, and have
no open PR. **This audit scores `origin/main` only**, per the doctrine's own render-truth rule ("the
only render truth that counts"). The unmerged commit is real, tested, and CODE-WIRED **on its own
branch** (verified: `PYTHONPATH=. python3 -m pytest scripts/manga/tests/test_assemble_from_bank.py -q`
→ `33 passed, 2 skipped`, matching the commit message's claim exactly) — but it does not move any
R-axis on main today, and is flagged here as a **ready-to-merge follow-on**, not counted in the table
below.

This is exactly the failure mode `docs/specs/MANGA_DRAWING_TRADITION_WAVE2_REIMPLEMENTATION_SPEC_20260721.md`
documents (claimed-done items absent on re-verification) — inverted: here the commit *is* real, but
citing it as "landed" without checking ancestry would have been the same class of error.

---

## 1. The 60-second table — R1–R8 conformance

| Axis | 07-03 % | 07-22 % | Verification this session | Highest proven layer |
|---|---|---|---|---|
| **R1** | 30% | **46%** | Verified: `config/manga/locale_genre_allocations.yaml` (833 lines) now exists on `origin/main`, self-declares consumer `scripts/manga/generate_catalog_plan_from_strategic.py`; `git grep` confirms 3 real consumers (`generate_catalog_plan_from_strategic.py`, `run_m7_wave_a.py`, `manga_m7_plan_coverage_grid.py`); `fr_FR` now has **390 real series-plan YAMLs** under `config/source_of_truth/manga_series_plans/fr_FR/` (was 0 at baseline) | CODE-WIRED + EXECUTED-REAL (allocation→plan chain proven for fr_FR) |
| **R2** | 45% | ~47% (CARRIED, light signal) | Chapter-script count grew from the baseline's cited 16 to **69** files under `artifacts/manga/chapter_scripts/` (`git ls-tree` count) — a real but unaudited-for-craft count; no fresh craft-grade re-screen run this session | EXECUTED-REAL (script count), craft grade NOT re-verified |
| **R3** | 25% | **25% — UNCHANGED, re-confirmed** | Verified: `git show origin/main:phoenix_v4/manga/story_architect.py \| grep vessel` returns **nothing** — the vessel loader is still not consumed by story generation, exactly as the 07-03 finding stated. New 07-22 landings (`bdd89b0644`, `a08b8af17b` — story-excellence realization gate, `modern_reader_context`) are a **different** quality-gate axis, not vessel wiring; not counted toward R3 | CONFIG-EXISTS (unchanged) |
| **R4** | 8% | 8% — **CARRIED FORWARD, NOT RE-VERIFIED** | No music×manga commits identified in the 07-03→07-22 commit range; not independently re-checked this session | CONFIG-EXISTS (carried) |
| **R5** | 34% | **37%** | Verified real: mecha `L2/threshold_stand.png` = LFS pointer `size 2801613` (2.8MB) on `origin/main` (git show blob → LFS pointer text). Verified UNMERGED: genre-aware `bubble_render_v2` wiring into `assemble_from_bank.py` exists only on `agent/bestseller-atom-flow-lanes-20260721`, not on main (§0). `bubble_render_v2.py` module itself **does** already exist on `origin/main` (landed via `fd96785f7b`, 07-13) — CONFIG-EXISTS/CODE-EXISTS as a standalone module, but its wiring into the bank-assembly entrypoint is the still-unmerged piece | EXECUTED-REAL (mecha L2/L3 REAL assets); wiring gap narrowed but not closed on main |
| **R6** | 40% | ~42% (CARRIED, light signal) | Same script-count growth as R2; sequencing doctrine violations not re-audited | EXECUTED-REAL (carried) |
| **R7** | 5% | **9%** | Verified: `artifacts/qa/manga_blind10_2026-07-08/` now holds a full protocol scaffold (`PROTOCOL.md`, `RUBRIC.md`, `COMPARATOR_REGISTRY.yaml`, `JUDGE_RECRUITMENT_BRIEF.md`, judge outreach drafts, a pre-screen script) — real files, real content, CODE-WIRED tooling (`scripts/qa/validate_manga_blind10_comparators.py`, `pre_screen/build_prescreen_items.py`). But `artifacts/qa/manga_blind10_2026-07-08/scorecards/` contains only `.gitkeep`; `manga_blind_read_bar_2026-07-14/` holds a `judge_scorecard_TEMPLATE.json` (template, not a filled scorecard). **Zero judged scorecards exist on main.** Still **zero** PROVEN-AT-BAR artifacts | SPECCED→partial CODE-WIRED (scaffold real; bar itself untouched) |
| **R8** | 35% | **39%** | Verified: fr_FR moved from 0 series plans (baseline table §7.2) to 390 real plan files + `artifacts/catalog/manga/ssot_rollup/fr_FR_manga_catalog_ssot.csv` (SSOT rollup, `run_m7_wave_a.py`-produced). Locale count with real plans: still 6 of 13 registry locales (en_US, ja_JP, ko_KR, zh_CN, zh_TW, fr_FR); 7 remain at zero (es_US, es_ES, de_DE, it_IT, hu_HU, zh_SG, zh_HK); pt_BR not yet in registry rollout | EXECUTED-REAL (fr_FR added to the executed-real locale set) |

Machine-readable: `artifacts/qa/manga_vision_conformance_20260722.tsv`

**One-sentence verdict:** the two real movements this session can prove are (1) the R1 allocation
chain — the baseline's single named blocking gap — is now CODE-WIRED and has produced a sixth
locale's worth of real series plans (fr_FR, 390 files), and (2) the R5/R7 gaps have real, tested,
CODE-WIRED scaffolding narrowing them (mecha REAL L2/L3 assets; a genre-aware bubble renderer that
exists on main as a module and is fully wired on an unmerged sibling branch; a real blind-10 protocol
scaffold) — but **R3's vessel-wiring gap is unchanged**, **R7's actual bar is untouched (zero judged
scorecards)**, and the single most-advertised claim in this dispatch (genre-aware bubble wiring) is
**not yet on `origin/main`**.

---

## 2. Render truth (byte-verified this session)

| Asset | Path | Verification | Verdict |
|---|---|---|---|
| Mecha L2 cutout | `artifacts/manga/warrior_calm_cultivation__master_wu__en_US__burnout__the_chassis_is_listening/image_bank/L2/threshold_stand.png` | `git show origin/main:<path>` → LFS pointer, `size 2801613` | EXECUTED-REAL (2.8MB, on main) |
| Mecha human-readability proof pages | `.../assembled/ep_001_human_readability_proof/ep001_*.png` (8 files) | Landed via `06a15f29eb` (07-09), confirmed present in `git ls-tree origin/main` | EXECUTED-REAL |
| fr_FR series plans | `config/source_of_truth/manga_series_plans/fr_FR/*.yaml` | `git ls-tree -r origin/main` count = 390 | EXECUTED-REAL |
| fr_FR SSOT rollup | `artifacts/catalog/manga/ssot_rollup/fr_FR_manga_catalog_ssot.csv` + `.summary.json` | present in `git ls-tree origin/main` | EXECUTED-REAL |
| `locale_genre_allocations.yaml` | `config/manga/locale_genre_allocations.yaml` | 833 lines, 3 confirmed code consumers via `git grep` | CODE-WIRED |
| Blind-10 judge scorecards | `artifacts/qa/manga_blind10_2026-07-08/scorecards/` | contains only `.gitkeep` | ABSENT (still) |
| Genre-aware bubble wiring in `assemble_from_bank.py` | `scripts/manga/assemble_from_bank.py` | on `origin/main` today: still calls legacy `phoenix_v4.manga.chapter.bubble_render.render_bubbles_onto_panel` (verified via `git show origin/main:scripts/manga/assemble_from_bank.py \| grep bubble`) | UNCHANGED on main (genre-aware version exists only on unmerged `agent/bestseller-atom-flow-lanes-20260721`, commit `aad5cf2152`) |

---

## 3. What moved, what didn't, and why (per axis)

- **R1 (30%→46%, verified):** The 07-03 baseline's single named blocking gap — "a per-locale genre
  allocation exists NOWHERE" — is resolved on main. `locale_genre_allocations.yaml` (833 lines,
  `status: active`, `milestone: M2`, landed via `#4613` on 2026-07-03 16:01 -0700, i.e. *after* the
  07-03 audit was authored at 07:53 that same morning) is real, cites the same research triad the
  baseline audit did, and is consumed by three scripts including `run_m7_wave_a.py`, which produced
  fr_FR's 390 real plan files — a full research→allocation→plan chain, executed, for at least one
  locale. Remaining gap: 7 of 13 registry locales still have zero plans regardless of the allocation
  config existing (allocation ≠ automatic rollout).
- **R2/R6 (light signal only):** Chapter-script count grew 16→69 by raw file count. This session did
  **not** re-run a craft-grade screen (the baseline's internal 5-script read, itself flagged
  internal-only). Treat the R2/R6 bump as a floor-only signal, not a craft-quality claim.
- **R3 (25%, re-confirmed unchanged):** Directly re-checked the baseline's exact claim — `git show
  origin/main:phoenix_v4/manga/story_architect.py | grep -i vessel` returns nothing. The vessel
  loader (`config/manga/manga_mode_vessels.yaml`) is still CONFIG-EXISTS, still unconsumed by story
  generation. The 07-22 "realization gate registry" landings (`#20`, `#54`) are a **quality-gate**
  axis (mention-only object detection, `modern_reader_context`) — a real, separate CODE-WIRED
  addition, but it does not touch vessel consumption and is not counted toward R3.
- **R4 (8%, not re-verified):** No music×manga-specific commits were identified in the 07-03→07-22
  commit range surveyed; carried forward without independent re-check.
- **R5 (34%→37%, mixed):** Two real, opposite-direction findings: (a) mecha L2/L3 REAL assets
  (byte-verified 2.8MB PNG) genuinely landed since 07-03 (`06a15f29eb`, `b7f8d04bd3`, 07-09) —
  incremental EXECUTED-REAL growth beyond the single stillness_press series; (b) the specific
  genre-aware bubble-render wiring this dispatch was told to verify is real, tested (33 passed / 2
  skipped, reproduced this session), but **lives only on an unmerged branch** — see §0. Net: modest
  real gain, not the gain the dispatch assumed.
- **R7 (5%→9%, scaffold-only):** The blind-10 protocol went from "PROPOSAL ONLY" (07-03) to a fully
  authored, CODE-WIRED scaffold: protocol doc, rubric, comparator registry (with a real Yen Press
  comparator acquisition per `d9c91550b4`), judge recruitment brief, outreach drafts, a pre-screen
  script. This is genuine progress on *infrastructure* for the bar. It is **zero** progress on the
  bar itself — the `scorecards/` directory is a `.gitkeep`, and no operator/judge has scored anything
  on main.
- **R8 (35%→39%, verified):** fr_FR joins the executed-real locale set (390 plans + SSOT rollup CSV),
  taking the grid from 5 to 6 of 13 registry locales with real plans. 7 locales remain untouched
  (es_US, es_ES, de_DE, it_IT, hu_HU, zh_SG, zh_HK); pt_BR still pending registry ratification per the
  baseline's Q-MANGA-01 default.

---

## 4. Open items carried forward unchanged

- No blind-judge scorecard exists anywhere on `origin/main` — R7's actual bar is untouched.
- Vessel (teacher/music apparatus) wiring into story generation remains CONFIG-EXISTS only (R3/R4).
- 7–8 of 13 registry locales still have zero series plans depending on axis (R1/R8).
- The CI drift gates named in the 07-03 roadmap (`check_render_progress_bytes.py`,
  `check_manga_story_authored.py`, `check_manga_wiring.py`) were **not re-verified this session** —
  their presence/absence on `origin/main` should be confirmed by the next re-audit before being cited
  either way.

## 5. Immediate next action for the operator

Merge or formally re-dispatch `agent/bestseller-atom-flow-lanes-20260721`'s genre-aware bubble-render
commit (`aad5cf2152`) — it is real, tested, and currently stranded off `origin/main` with no open PR.
Until it merges, `origin/main`'s bank-assembly lane keeps calling the legacy (non-genre-aware) bubble
renderer even though the genre-aware module has been sitting on main, unused by this entrypoint,
since 2026-07-13.

**Evidence root:** this session's git-plumbing commands (quoted inline above) + one live pytest run;
no new agent fan-out was run. Full prior fan-out evidence: `artifacts/qa/manga_vision_conformance_20260703.tsv`.
