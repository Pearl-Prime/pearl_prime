```text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_Dev for Phoenix Omega.

Repo: Ahjan108/phoenix_omega_v4.8
Start from a clean checkout of latest origin/main.

STARTUP_RECEIPT:
- AGENT=Pearl_Dev
- LANE=manga_wave2_items124_20260722
- EXECUTION_MODE=local_fallback (Item 2's live PNG smoke, if attempted,
  becomes pearl_star_remote via pscli — queue-first only, see RAP note below)
- BACKGROUND_SAFE=yes
- RUNTIME_HOST=local checkout (+ pearl_star queue for Item 2 live smoke only)
- PERSISTENCE_SURFACES=branch/PR/artifact
- RESUME_SURFACE=docs/specs/MANGA_DRAWING_TRADITION_WAVE2_REIMPLEMENTATION_SPEC_20260721.md

READ FIRST:
- docs/specs/MANGA_DRAWING_TRADITION_WAVE2_REIMPLEMENTATION_SPEC_20260721.md
  — this IS your task spec, read it in full, including the "Cross-cutting"
  and commit-discipline sections at the end.
- CLAUDE.md manga doctrine (six-layer taxonomy; CONFIG-EXISTS ≠ working;
  gate-PASS ≠ pro bar)
- docs/ROBUST_AGENT_PROTOCOL.md (RAP — queue-first pscli dispatch is
  mandatory before any Pearl Star GPU/LLM work; only relevant if you attempt
  Item 2's live smoke test)
- config/manga/drawing_tradition_per_genre.yaml (the 8 existing top_8_deep
  blocks are your template for Item 1)
- phoenix_v4/manga/genre_tradition.py (resolve_tradition_genre — confirm the
  spec's reading that it's already generic before assuming code changes)
- scripts/pearl_star/worker/qwen_manga_worker.py + reference workflow
  scripts/image_generation/comfyui_workflows/qwen_image_no_pulid_manga.json
  (Item 2)
- scripts/manga/run_chapter_production.py, run_chapter_visual.py,
  run_manga_chapter.py (Item 4 — the 3 hardcoded --style-id defaults)

LIVE STATE RECONCILIATION:
- `git fetch origin`; the spec's "current baseline (verified 2026-07-21)"
  lines are now a day-plus old — re-verify each with a fresh
  `ls`/`grep`/`git log -p` before writing any code, exactly as the spec
  itself instructs ("Re-verify again before you start if time has passed").
- Confirm Item 3 (bubbles) is genuinely closed: `git show aad5cf2152 --stat`
  and re-run `scripts/manga/tests/test_assemble_from_bank.py` yourself — do
  not take the spec's "DONE" label on faith, confirm it, then move on. Do
  not re-do Item 3's work.
- Multiple sibling sessions may be active in this shared working tree
  (confirmed active on 2026-07-21/22). Before any `git commit`, run
  `git status --short` and confirm every staged path is one you intended.

PRE-REQUISITE CHECKS:
- item3_status=CODE-WIRED (already true per aad5cf2152 — confirm, don't
  re-implement)
- If Item 3 is somehow NOT actually landed on origin/main when you check,
  STOP and report BLOCKED — that would mean the spec's own "DONE" claim is
  itself stale/wrong, which is a bigger signal than this lane can resolve
  alone.

DISCOVERY REPORT BEFORE ACTION:
- current origin/main SHA;
- fresh confirmation, per item, of the spec's "current baseline" claims
  (Item 1: which genres are `top_8_deep` vs `deferred_phase2` right now;
  Item 2: current step count in qwen_manga_worker.py vs the reference JSON;
  Item 4: confirm phoenix_v4/manga/style_resolution.py still does not
  exist, and the 3 CLI scripts still hardcode dark_psychological);
- any open PR touching these same files;
- proposed smallest safe batch per item.

PROVENANCE:
- research: none new (this is implementation of an already-specced item)
- documents: docs/specs/MANGA_DRAWING_TRADITION_WAVE2_REIMPLEMENTATION_SPEC_20260721.md
- builds_on: config/manga/drawing_tradition_per_genre.yaml (8 existing
  top_8_deep blocks), scripts/pearl_star/worker/ blob-gate/stall-timeout
  pattern, existing style/archetype config
- inventory: EXTENDS — 6 new genre blocks (Item 1), 1 modernized worker
  (Item 2), 1 new resolver module + 3 CLI default changes (Item 4). Nothing
  reduced.

MISSION:
Close the 3 genuinely-outstanding items from the Wave-2 reimplementation
spec — Item 1 (drawing-tradition backfill for 6 genres), Item 2 (Qwen
Pearl Star worker modernization), Item 4 (style-default removal) — to
CODE-WIRED with real tests, per the spec's acceptance criteria for each.
Item 3 is already done; confirm only.

DELIVERABLES:
- Item 1: 6 new genre blocks in
  config/manga/drawing_tradition_per_genre.yaml (mystery,
  supernatural_everyday, workplace, battle, sci_fi_cyberpunk, sports),
  full schema parity with the 8 existing top_8_deep blocks, status value
  resolved per the spec's own open question (confirm no code branches on
  the literal string "top_8_deep").
- Item 2: modernized worker (target file determined per spec step 2 —
  verify before assuming), matching the reference ComfyUI workflow's real
  step count/cfg, blob-gate + stall-timeout preserved, unit graph tests
  (no live GPU required to pass).
- Item 4: `phoenix_v4/manga/style_resolution.py` with the documented
  authority chain + `grounded_realism` fallback; 3 CLI scripts' `--style-id`
  default changed from `dark_psychological` to none, calling the resolver.
- Real tests for all 3 items (do not claim the prior report's fabricated
  "28 tests" count — write and count your own).
- `artifacts/qa/manga_wave2_items124_closeout_2026-07-22.md` — written only
  after each item is verified working, per CLAUDE.md's honest-acceptance
  rule; label each item's actual layer (CODE-WIRED at minimum; EXECUTED-REAL
  only if you produced a real render/output; do not claim PROVEN-AT-BAR).

SMALLEST SAFE BATCH:
- smoke: Item 4 first (smallest, no GPU, clearest acceptance test —
  healing-genre chapter resolves to cozy_iyashikei with no --style-id).
- pilot: Item 1 (6 genre YAML blocks — author 1, validate resolution, then
  the remaining 5).
- scale: Item 2 (largest surface, touches Pearl Star worker code) — only
  after Items 1 and 4 are landed and green, and only up to the unit-graph-
  test bar; do not attempt the live GPU smoke unless pearl_star + the Qwen
  model trio are confirmed on-box (queue-first via pscli per RAP if you do).

HANG PREVENTION:
- poll interval: 10 minutes for any test run over a minute
- no-progress rule: inspect logs after two unchanged polls
- hard stall rule: BLOCKED or reduce batch (ship whichever items are green,
  report the rest BLOCKED individually) after three unchanged polls
- max window: 4 hours

TESTS/PROOFS:
- new test files co-located near each module (tests/manga/ or matching
  existing convention — check where scripts/manga/tests/ already lives)
- `python3 -m pytest <new test paths> -q`
- proof root: artifacts/qa/manga_wave2_items124_closeout_2026-07-22.md

DO NOT:
- no gate weakening;
- no stale metrics or borrowed numbers from the discredited prior report;
- no fake proof — every claim needs a command you actually ran and its
  output;
- no local-only finish;
- no giant batch first (do not attempt all 3 items in one commit);
- do not claim a live GPU smoke test passed without an actual rendered PNG
  to point to;
- do not repeat the original failure: after every file write, verify it
  landed on disk (`ls`/`cat`/`git status`) before reporting an item done —
  this is the spec's own explicit instruction after the prior incident.

LANDING CONTRACT:
- MERGED: PR opened, required checks green, squash-merged, signal emitted.
  May land as 1 PR per item (recommended, given 3 independent items) or
  1 PR total if items are small enough for clean review — prefer per-item
  PRs unless combining materially reduces review risk.
- BLOCKED: exact blocker per item, evidence, pushed remote branch if
  useful, handoff written. Partial landing (e.g. Item 4 MERGED, Item 2
  BLOCKED) is an acceptable and expected outcome — report each item's
  status independently, do not let one blocked item mask two merged ones.

CLEANUP LEDGER REQUIRED:
- worktree:
- local branch:
- remote branch:
- scratch files:
- background jobs:
- held artifacts:

HANDOFF REQUIRED:
- artifacts/coordination/handoffs/manga_wave2_items124_2026-07-22.md

CLOSEOUT_RECEIPT:
- AGENT: Pearl_Dev
- LANE: manga_wave2_items124_20260722
- STATUS=MERGED|BLOCKED (report once per item if outcomes differ)
- BRANCH:
- PR:
- MERGE_SHA:
- SIGNAL:
- PROOF_ROOT:
- TESTS:
- CLEANUP:
- HANDOFF:
- NEXT_ACTION:
```
