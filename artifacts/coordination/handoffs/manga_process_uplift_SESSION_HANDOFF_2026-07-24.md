# SESSION HANDOFF — Manga Process Uplift Program (2026-07-24)

**Owner role:** dispatcher for the manga **still/story/production** uplift program.
**Plan of record:** `docs/agent_prompt_packs/20260724_manga_process_uplift/` (MERGED, PR #313).
**Live anchor at handoff:** `origin/main` = `b4c1a255dc3eccae5abff594c3064f57ddadd42b`
(NOTE: main moves every few minutes — scheduled pt_BR batches + sibling programs. Re-fetch and
re-derive every SHA/PR state below before acting; each is a CLAIM.)

**How to resume in one line:** verify the 3 in-flight lanes (§3) landed; then dispatch Lane 08 →
Lane 11 → Lane 12 in that gated order (§4), each from its lane prompt file with a live-delta note.

---

## 0. What this program is (for a cold start)

Put enforced process around manga: research-verified genre/duration/cadence → 100-episode Series
Master Plan → checklist-gated writing → editor QA → storyboard → image-bank demand → assembly.
12 signal-gated lanes + a Pearl_PM dispatcher. Everything EXTENDS existing canonical machinery;
nothing is greenfield. Read `docs/agent_prompt_packs/20260724_manga_process_uplift/INDEX.md`
first — it has the operator-idea disposition table and the full lane map.

**Acceptance honesty:** nothing in this program claims PROVEN-AT-BAR. That stays gated on blind-10
judged scorecards (roadmap M6), which this program feeds but does not satisfy. Research =
RESEARCHED; contracts/gates = SPECCED/CODE-WIRED; the pilot (Lane 11) reaches **system working**
at most.

---

## 1. Operator rulings — RATIFIED, binding (logged OPD-20260724-MPU-01..04, PR #316)

- **Q-MPU-01 = flagship-first.** en_US wave-1 series get full 100-ep master plans (eps 1–48
  detailed, 49–100 outline); CJK cells stay on the 48-ep cadence until wave 2.
- **Q-MPU-02 = PR #295 REWORK, never merge.** DONE: Lane 05 absorbed its 10 bibles (#323), Lane 06
  absorbed its 20 arc plans (#331), **#295 CLOSED as superseded 2026-07-24T06:34** (branch never
  touched). Do not reopen or re-merge #295.
- **Q-MPU-03 = BOTH US-illustrated frames.** Book-format contract (primary, evidenced) AND
  serialized-episode variant; routed by series_plan `format`/`master_format`. Spec'd in Lane 06's
  contract §US-illustrated.
- **Q-MPU-04 = one skill per role** (editor/writer/storyboarder), genre-parameterized via
  checklist files — NOT 25 per-genre agents.

---

## 2. Scope boundaries (do NOT cross — other sessions own these)

- **R2 / LFS offload** → separate agent (operator handoff). Open PR #336 (`r2-program-reconcile`)
  is theirs. Keep `check_render_progress_bytes.py`'s R2/LFS byte-verification fallback INTACT;
  don't move manga assets or touch R2 config.
- **Manga VIDEO pose-bank** → separate Piper session (operator ruling: "leave video to the other
  session"). Pack `docs/agent_prompt_packs/20260724_manga_video_pose_bank/` (MERGED, PR #335);
  open PR #339 is its coord registration. It is DOWNSTREAM of this program (consumes Lane 09
  `series_demand_rollup`, serializes its pilot ingest against this program's Lane 11). **Your only
  duty toward it:** hold serial ownership of hot files (PROGRAM_STATE / ACTIVE_WORKSTREAMS / OPD),
  second-lander-re-roots on collision; do NOT dispatch any video lane. When you dispatch Lane 11,
  warn it a video bank-ingest may serialize against the same stillness/mira_aoki artifacts.

---

## 3. IN FLIGHT at handoff — VERIFY FIRST, resume if not landed

Three lane agents were mid-authoring with NO PR yet at the sweep (main tip `b4c1a255dc`). They may
self-complete to MERGED/BLOCKED after this handoff, or may have parked. **Verify each before doing
anything** (`gh pr list --search "<slug>" --state all`; check the signal token on main):

| Lane | What | Gate (satisfied) | Signal to look for | If NOT landed → resume |
|---|---|---|---|---|
| **07 genre checklists** | compile bibles + 289 MC items → `genre_craft_checklists.yaml`, wire into `story_excellence_gates.yaml` + `excellence_gate.py`, flip `mc_endurance_checklists.yaml` to wired; mutation-tested | craft-bibles-complete `82ef3957` + mc-endurance `11c12e5345` | `manga-genre-checklists-wired=<sha>` | re-dispatch from `07_genre_checklists_wired.md` |
| **09 bank demand rollup** | `--series-rollup` on `generate_bank_contracts_from_script.py` → `series_demand_rollup.yaml` + schema + one real rollup on the Lane 06 golden series | master-plan `1cbb40adf0` | `manga-bank-demand-rollup-merged=<sha>` | re-dispatch from `09_bank_demand_rollup.md` |
| **schema-fix** (repo health) | repair `test_manga_schemas.py::…[arc_storyboard_plan]` KeyError from #319 (breaks Core tests on main) | — | (no token; check Core tests first-failure moves past arc_storyboard) | re-dispatch: fix the parametrized minimal-instance builder for the arc_storyboard schema, don't skip/xfail |

**Monitor-parking gotcha (bit ≥3 lanes today):** a subagent that arms a background poller/Monitor
and says "standing by"/"waiting on pollers" is PERMANENTLY stalled — it cannot self-wake. Drive it
with `SendMessage`: instruct synchronous foreground polling only, drive to MERGED/BLOCKED. Bake
"synchronous polling only; never arm a watcher and end your turn" into every dispatch note.

---

## 4. QUEUED — not yet dispatched (the remaining work to finish the program)

Dispatch in this gated order, one lane per background agent, full lane prompt VERBATIM + a
live-delta note:

- **Lane 08 — manga skills** (`08_manga_skills.md`). Gate: `manga-genre-checklists-wired`.
  Creates `skills/manga-story-writer`, `skills/manga-editor`, `skills/manga-storyboarder` (thin
  bindings to the canonical gates/checklists; absorbs `manga_arc_storyboard_planner.md` with a
  superseded-pointer). Signal `manga-skills-registered`.
- **Lane 11 — end-to-end pilot** (`11_pilot_end_to_end.md`). Gate: master-plan `1cbb40adf0` (✅) +
  `manga-genre-checklists-wired`. Runs ONE series (stillness_press flagship — Lane 06's golden
  `artifacts/manga/series_master_plans/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying.master_plan.yaml`)
  through the full loop: master-plan editor pass → arc episode pass → write 2 new episodes (gate
  ≥85 + story-authored + editor checklist) → storyboard both → bank delta → assemble one episode
  (INTERIM-labeled, offline, no GPU) → `artifacts/qa/manga_process_uplift_pilot_2026-07-24/SUMMARY.md`
  → `open` it for operator. **This produces the operator read packet — the next real touchpoint.**
  Signal `manga-process-pilot-system-working` (or `…-authored-candidate` + gap list). **Warn it:
  video bank-ingest (sibling program) may serialize against the same stillness/mira_aoki artifacts.**
- **Lane 12 — final audit + SSOT** (`12_final_audit_ssot.md`). Gate: all prior terminal. Byte-
  verifies every lane, lands the debts in §5, rewrites the PROGRAM_STATE manga row with honest
  acceptance layers, false-premise sweep, enforcement-promotion check. Signal
  `manga-process-uplift-audited`.

---

## 5. DEBTS / FOLLOW-UPS to fold into Lane 12 (or file as small lanes)

Collected from lane closeouts — none blocking, all must be closed for an honest "done":

1. **PROGRAM_STATE R3 correction still owed.** Lane 01 corrected the vision-audit `.md` only.
   `docs/PROGRAM_STATE.md` manga row + `artifacts/qa/manga_vision_conformance_20260722.tsv` still
   carry the false "vessels unwired (R3=25%)" premise — vessels are CODE-WIRED since #4616
   (`story_architect.apply_mode_vessel`). Correct at the source (dated, don't rewrite history).
2. **Canonical registry rows owed:** `manga_series_master_plan_contract` / `_schema` / `_gate`
   (Lane 06 requested via dispatcher). `mc_endurance_checklists` already landed (PR#325). Add
   whatever Lane 09/07/08 create.
3. **Untracked authority files needing a landing owner** (referenced but only on the shared
   checkout, NOT origin/main): `docs/research/manga_craft/main_character_interaction_grammar_by_genre.md`,
   `comedy_gag.md`, `story_quality_gap_audit_modern_reader_worlds.md`;
   `config/manga/genre_scene_templates/mecha.yaml` (gate 47 required-story-function check no-ops
   until it lands); `tests/manga/test_arc_storyboard_gate.py` (gate #319 merged testless).
4. **Dual gate-46 numbering collision** in `run_production_readiness_gates.py` (pre-existing, left
   untouched by every lane per instruction). New gates landed at 47 (#319) and 48 (#331).
5. **6 grandfathered legacy `bubble_render` callers** in `KNOWN_LEGACY_CALLERS`
   (`check_no_legacy_bubble_render.py`, ratchet) → migrate to v2, shrink to zero.
6. **`chapter_runner.py` arc_storyboard passthrough** — Lane 10 wired consumption into
   `visual_from_script`/`assemble_from_bank` but the runner still only requires the plan
   pre-visual; passing `arc_storyboard=` through the runner is the named next step.
7. **Release gates chronic red** = gate 27 (`wave_proof/.../enrichment_audit.json` missing
   `research_fit` key) — main-side, unrelated to this program; worth a dedicated small lane.
8. **`agent/bestseller-atom-flow-lanes-20260721` retirement** — its bubble commit `aad5cf2152` is
   now redundant with main (landed as #318). CAUTION: the shared checkout is PARKED on this branch
   — do not delete it out from under an active checkout; coordinate.

---

## 6. MERGED LEDGER (this program, 2026-07-24 — full SHAs)

| Item | PR | Merge SHA | Signal |
|---|---|---|---|
| Pack (plan of record + rulings) | #313 | `802955aeea845149cd430b806f0a305f24c16018` | — |
| Coordination (ws rows + OPD-MPU-01..04) | #316 | `88573e234536f28162b215656ed4255e95084774` | — |
| Lane 01 bubble-v2 wiring | #318 | `2208b2b37ab1589f3041129934b8d6eea352406e` | `manga-stranded-landed` |
| Lane 01 storyboard gate #47 + R3 correction | #319 | `0644674cdf9184ea6a1f11a772942878768944f9` | — |
| Lane 01 handoff | #321 | `d4fec15c5920162d5d2ed218d11d2e3807c269f8` | — |
| Lane 02 US illustrated formats | #320 | `2a7a1b89a02cb1605df42058d031da4dbde01dba` | `us-illustrated-format-research-merged` |
| Lane 03 arc cadence | #322 | `9446b3e74efc0607d77e5fddce21cf8213aa7f5f` | `manga-arc-cadence-research-merged` |
| Lane 04 MC endurance + market refresh | #325 | `11c12e5345bff9586d91a50f9c90e92dfe54e27e` | `manga-mc-endurance-research-merged` |
| Lane 05 craft bibles + #295 absorb | #323 | `82ef39572e2751a7bed210d509a394b5d598f0ad` | `manga-craft-bibles-complete` |
| Lane 06 Series Master Plan contract | #331 | `1cbb40adf0094081adc38da6188041a3dc9f9fca` | `manga-series-master-plan-contract-merged` |
| Lane 10 storyboard consumption wiring | #330 | `007a69d19758d98326a0a7c2b851e0a1e9ae3cfb` | `manga-storyboard-consumed` |
| Repo-health: DATA_DICTIONARY regen (cleared Drift-detectors main red) | #326 | `7885fb6f78b34040377d95d9e6a47da0565be669` | — |
| Repo-health: land dangling US-illustrated authority doc | #328 | `bb8ef82ed317eeb6b7f600834d909427d49bdcfa` | — |
| PR #295 | — | CLOSED (superseded) | — |

**10 of 12 lanes merged + 2 repo-health fixes + #295 closed. Zero blocked.** Remaining: Lanes 07,
09 (in flight §3), 08, 11, 12 (queued §4).

---

## 7. DISPATCH MECHANICS the next session MUST use (proven all day)

- **Substrate:** shared checkout `/Users/ahjan/phoenix_omega` is DIRTY and PARKED on
  `agent/bestseller-atom-flow-lanes-20260721`. NEVER switch branches; NEVER commit from HEAD. Use
  the **plumbing pattern**: temp index off `origin/main^{tree}`, `git hash-object -w` +
  `update-index`, staged-diff gate (`git diff --cached --numstat origin/main` — verify exact file
  list + **0 unintended deletions** before commit), `commit-tree` with parent=fresh origin/main,
  push to a new `agent/...` branch. No full worktrees (262k files, LFS smudge).
- **zsh `${VAR}:path` gotcha:** ALWAYS brace `${VAR}:path` in `git show`/refspecs — the bare
  `$VAR:path` triggers the zsh `:a` modifier and silently corrupts the ref (nearly gutted a
  coordination TSV this session; caught by the staged-diff gate).
- **Required checks = `parse-sweep` + `Verify governance` ONLY.** Merge on those two green; name
  every check's status (never "all checks pass"). Chronic main reds, each verified diff-independent:
  **Core tests** (chronically slow + the arc_storyboard schema break, fix in §3); **Release gates**
  (gate 27, §5.7). **Drift detectors is now GREEN** (fixed by #326) — if a new script/gate makes it
  stale again, regenerate `DATA_DICTIONARY.tsv` via `scripts/governance/build_data_dictionary.py`
  in the same PR (correct fix, not a weakening).
- **Strict up-to-date ruleset:** main moves fast; merges bounce with "head branch is not up to
  date." Re-root via plumbing onto fresh origin/main + `--force-with-lease` + tight SYNCHRONOUS
  retry loop. Auto-merge is DISABLED repo-wide (`--auto` rejected).
- **Rule 0:** `gh pr diff <n> --stat | tail -1` before any merge; >50 deletions = STOP, ask owner.
- **`bash scripts/git/pre_merge_check.sh <n>`** before merge; `health_check.sh` may hang on the
  busy shared checkout — timebox and report honestly, never claim it passed if it didn't return.

---

## 8. NEXT_ACTION (cold-start resumable)

1. `git fetch origin main`; re-derive all state above.
2. Verify §3 lanes: search PRs + signals for checklists / bank-rollup / schema-fix. Merge any that
   are open+green; re-dispatch any that parked or died (from their lane prompt, synchronous-poll
   note included).
3. Once `manga-genre-checklists-wired` exists: dispatch **Lane 08** (skills), then **Lane 11**
   (pilot — the operator read packet). Both gates for Lane 11 are then met.
4. After Lane 11: dispatch **Lane 12** (final audit) — it lands the §5 debts, rewrites the
   PROGRAM_STATE manga row, and emits `manga-process-uplift-audited`.
5. Keep serial ownership of hot coordination files; second-lander-re-roots vs the sibling video
   (#335/#339) and R2 (#336) programs.

**The pilot's `SUMMARY.md` + assembled sample episode is the operator's next review touchpoint —
`open` it when Lane 11 completes.**
