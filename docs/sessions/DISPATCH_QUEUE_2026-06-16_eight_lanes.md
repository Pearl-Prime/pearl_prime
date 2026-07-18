# Dispatch Queue — 8 Lanes (2026-06-16)

**Owner:** Pearl_PM (prompt-building router) · **Repo:** `Ahjan108/phoenix_omega_v4.8` · **`origin/main` = `9ec4a165f9`**
**Companion to:** `docs/sessions/SESSION_HANDOFF_2026-06-16_router_omnibus.md` (the omnibus references these prompts as "in the chat"; this file makes them durable).
**Status:** every load-bearing anchor below verified against `origin/main` this session. Paste each fenced block into its own fresh agent chat.

> **READ note for all lanes:** authority docs tagged **(wt-local)** exist only in the working tree, NOT on `origin/main` — read the working-tree copy, do not `git show origin/main:` them. Docs tagged **(main-only)** are the reverse. Everything else is on both.

---

## Dispatch map

| # | Lane | Agent | When |
|---|---|---|---|
| 1 | B — run_frame_judge | Pearl_Video | 🟢 now |
| 2 | C — manga seed | Pearl_Dev | 🟢 now |
| 3 | D — cap-ratify | Pearl_Architect | 🟢 now (sole hot-file writer) |
| 4 | Books Phase B | Pearl_Prime | 🟢 now (self-gates on the wave) |
| 5 | de-poison | Pearl_GitHub | 🟢 now (parallel-safe) |
| 6 | builder-ext | Pearl_Video | 🟢 now (1-line) |
| 7 | install | Pearl_Int | 🟡 GO on operator sudo + reboot ack |
| 8 | E — canonical builder | Pearl_Video | 🔶 hold until B merges |

Only shared file across 🟢 lanes is `ACTIVE_WORKSTREAMS.tsv` ws-row appends (conflict-trivial; 2nd PR rebases). B and builder-ext are both Pearl_Video but disjoint files → two separate sessions.

## Anchor verification ledger (this session)

- `origin/main` HEAD = `9ec4a165f9` (exact).
- de-poison delete-set = exactly 3 phantom gitlinks `_wt_beatmap`, `_wt_inj`, `_wt_r2_sai_ma`; `Qwen` + `Qwen-Agent` are LEGIT `.gitmodules` submodules (PROTECT). `.claude/worktrees` already untracked on main by PR #1577.
- builder-ext bug confirmed: Python `manga_name()` (`build_frame_selector_v2.py:57`) normalizes `.jpg→.png`; JS `renderPath()` (`:462`) does not.
- C seed sites confirmed: `render_v5_episode.py:727` (live index-jitter), `reference_sheet_generator.py:251` (per-character formula to reuse).
- E target `build_beat_driven.py` confirmed net-new (not on main); judge source `intelligent_v3_7_pipeline.py` is wt-local.
- install merge-gates clear: PR #1492 merged, cap `PEARL-STAR-JOB-QUEUE-V1-01` active; spec is main-only, handoff is wt-local.
- All other cited authority-doc paths exist on `origin/main`; the `video_best_method_20260616/*` docs + `BOOKS_SHIPPABILITY_DIAGNOSIS.md` are wt-local (tagged inline below).

---

## 1 — 🟢 B · `run_frame_judge.py` (Pearl_Video)

```
Pearl_Video — VIDEO B: lift the v3.7 AI-judge loop into a reusable run_frame_judge.py module (the W2 linchpin).
EMIT A STARTUP_RECEIPT FIRST (docs/SESSION_UNITY_PROTOCOL.md):
  AGENT:              Pearl_Video
  TASK:               generalize the v3.7 AI-judge (Qwen2.5-VL→Gemma3 re-render keep-best loop) into scripts/video/run_frame_judge.py — shared by the canonical video pipeline AND manga panel QA
  PROJECT_ID:         proj_state_convergence_20260328  (append a ws row to ACTIVE_WORKSTREAMS.tsv)
  SUBSYSTEM:          video_pipeline
  AUTHORITY_DOCS:     artifacts/video/video_best_method_20260616/PEARL_VIDEO_AI_JUDGE_GATE_V1_SPEC.md (wt-local) (the per-frame judge schema);
                      artifacts/video/video_best_method_20260616/VIDEO_TO_MANGA_CROSS_POLLINATION.md (wt-local) (W2 = this module; manga #1 consumes it);
                      docs/specs/PEARL_VIDEO_BEAT_DRIVEN_NARRATIVE_PIPELINE_V1_SPEC.md; docs/SESSION_UNITY_PROTOCOL.md
  READ_PATH_COMPLETE: <yes after reading the above>
  WRITE_SCOPE:        scripts/video/run_frame_judge.py (NEW) + tests/video/test_run_frame_judge.py (NEW)
  OUT_OF_SCOPE:       editing intelligent_v3_7_pipeline.py (read-only SOURCE); wiring into run_pipeline (that is lane E); the manga qa_panel_judge.py consumer (follow-on); paid API; any books composer/enrichment files
  BLOCKERS:           none
  READY_STATUS:       ready  (parallel-safe — disjoint from C/D and the Books Phase-B session)
THE WORK:
  • SOURCE OF TRUTH = the LOCAL-ONLY scripts/video/intelligent_v3_7_pipeline.py (it is NOT on origin/main — read the working-tree copy).
    Core loop ≈ L154-163 (judge call), L318-319 (model selection), L422-444 (re-judge / keep-best across attempts).
  • Models: Qwen2.5-VL-7B (judge) + Gemma3:27b (rewriter) + flux1-dev-fp8 (re-render) — ALL local Ollama/ComfyUI on Pearl Star
    (Tier-2, free). Seed = blake2b(beat_id), deterministic. NO paid API.
  • Extract into a reusable module + CLI: --frames-dir --beats <json> --threshold (default 80) --judge-model --rewriter-model
    --comfyui-url --checkpoint-out --max-retries. Emit per-frame JSON {id, score, missing[], wrong[], present[], suggested_fix}
    (schema lives in PEARL_VIDEO_AI_JUDGE_GATE_V1_SPEC.md).
  • Generalize so BOTH callers work: video (frame vs beat narration) AND manga (panel vs scene_description). This dual-use IS the point.
  • Unit-test with a STUBBED judge (mock the Ollama/ComfyUI calls) so CI is deterministic and needs no live box.
GUARDRAILS: net-new file → plumbing-commit off origin/main^{tree} (+GIT_LFS_SKIP_SMUDGE=1), no clobber possible. CI = source of
  truth. Only required check = "Verify governance"; Workers Builds red = ignore. Branch from origin/main. do-NOT-merge PR (review).
CLOSE: CLOSEOUT_RECEIPT — full SHA, the module's public API (so lane E + the manga consumer can bind to it), test results.
```

## 2 — 🟢 C · manga per-character seed propagation (Pearl_Dev)

```
Pearl_Dev — VIDEO C: propagate the per-character deterministic seed into manga panel renders (interim consistency before PuLID).
EMIT A STARTUP_RECEIPT FIRST:
  AGENT:              Pearl_Dev
  TASK:               replace index-jitter panel seeds with per-character seeds so a character renders consistently across panels (interim win; composes with deferred PuLID Phase C)
  PROJECT_ID:         proj_manga_first_ship_20260425  (append a ws row)
  SUBSYSTEM:          manga_pipeline
  AUTHORITY_DOCS:     artifacts/video/video_best_method_20260616/VIDEO_TO_MANGA_CROSS_POLLINATION.md (wt-local) (#2 = this — framed INTERIM, do NOT pre-empt PuLID);
                      specs/AI_MANGA_PIPELINE_SUMMARY.md; docs/MANGA_IMPLEMENTATION_OUTLINE.md;
                      docs/CHARACTER_INDIVIDUATION_PIPELINE_SPEC_2026-05-02.md; docs/SESSION_UNITY_PROTOCOL.md
  READ_PATH_COMPLETE: <yes>
  WRITE_SCOPE:        scripts/manga/render_v5_episode.py (the LIVE per-panel seed site, ~L727) + optionally scripts/manga/queue_panel_renders.py (~L279, sibling legacy path) + a focused test
  OUT_OF_SCOPE:       the constraint solver (do NOT rebuild — 14/14 AXIS-distinct already); PuLID / engine_router internals (deferred Phase C — COMPOSE, never replace); reference_sheet_generator.py (read-only seed-formula SOURCE); paid API; the video files (B/E)
  BLOCKERS:           none — INDEPENDENT, does NOT gate on B
  READY_STATUS:       ready  (parallel-safe)
THE WORK:
  • THE BUG: render_v5_episode.py ~L727  `seed = seed_base + (panel_index * 1009)` — index jitter → the SAME character drifts panel
    to panel, even though reference sheets ARE per-character seeded. (queue_panel_renders.py ~L279 `seed = args.seed_base + i` = same bug, legacy path.)
  • THE FORMULA TO REUSE (reference_sheet_generator.py ~L251): `DEFAULT_SEED_BASE(7777) + sum(ord(c) for c in <character_id>)`.
  • AUDIT FIRST (do not assume): does the panel payload (panel_prompts / continuity_state output) carry a per-panel character_id?
       → if YES: derive the seed from character_id when present; fall back to index jitter only when a panel has no character.
       → if the schema LACKS character_id: add it at the emission site (continuity_state_generator.py) — but verify the emit path before editing.
  • Fix the LIVE path (render_v5_episode.py is canonical per the router omnibus); fix or explicitly flag queue_panel_renders.py.
  • Add an opt-in flag (e.g. --seed-by-character). Deterministic, free, Tier-2. Compose with — do not replace — the deferred PuLID pathway.
GUARDRAILS + CLOSE: plumbing-commit off origin/main^{tree}; CI = source of truth; only "Verify governance" required; do-NOT-merge PR.
  CLOSEOUT_RECEIPT: full SHA, the audit finding (did panels carry character_id?), before/after seed for one repeated character.
```

## 3 — 🟢 D · cap-ratify `PEARL-VIDEO-BEAT-DRIVEN-V1-01` (Pearl_Architect, corrected 5-field map fix)

```
Pearl_Architect — VIDEO D: ratify cap PEARL-VIDEO-BEAT-DRIVEN-V1-01 + add the beat-driven spec to the video_pipeline authority row.
PR #1652 landed the beat-driven video method specs on main; now make the method AUTHORITATIVE. SERIAL hot-file lane — one writer on PEARL_ARCHITECT_STATE.md.
EMIT A STARTUP_RECEIPT FIRST:
  AGENT:              Pearl_Architect
  TASK:               ratify PEARL-VIDEO-BEAT-DRIVEN-V1-01 + add beat-driven + frame-selector specs to the video_pipeline SUBSYSTEM_AUTHORITY_MAP row
  PROJECT_ID:         proj_state_convergence_20260328  (video_pipeline governance)
  SUBSYSTEM:          video_pipeline
  AUTHORITY_DOCS:     docs/specs/PEARL_VIDEO_BEAT_DRIVEN_NARRATIVE_PIPELINE_V1_SPEC.md (on main via #1652);
                      docs/specs/PEARL_VIDEO_FRAME_SELECTOR_BEST_OF_V1_SPEC.md (on main via #1662);
                      artifacts/video/video_best_method_20260616/VIDEO_BEST_METHOD_CONSOLIDATION.md (wt-local) (has the draft cap text);
                      docs/PEARL_ARCHITECT_STATE.md; artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv; docs/GITHUB_GOVERNANCE.md; docs/SESSION_UNITY_PROTOCOL.md
  READ_PATH_COMPLETE: <yes>
  WRITE_SCOPE:        docs/PEARL_ARCHITECT_STATE.md (one cap entry, append-only) +
                      artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv (one IN-PLACE field-2 edit to the existing video_pipeline row)
  OUT_OF_SCOPE:       appending a 15-field row (that is ACTIVE_WORKSTREAMS.tsv's schema — the PRIOR ERROR this corrects); ANY code; the canonical refactor (E); editing the specs themselves (already on main); other cap entries / other subsystem rows
  BLOCKERS:           none
  READY_STATUS:       ready  (serial-safe — sole PEARL_ARCHITECT_STATE.md writer this wave; confirm no other cap-append is in flight before committing)
THE WORK:
  1. SERIAL-LANE CHECK FIRST: gh pr list --state open --search "PEARL_ARCHITECT_STATE" — if a cap-append PR is mid-merge, HOLD and
     surface (never two hot-file writers). Compute the next OPD-ID at write-time (max OPD-YYYYMMDD-NNN on origin/main +1; never hardcode).
  2. Append cap PEARL-VIDEO-BEAT-DRIVEN-V1-01 to PEARL_ARCHITECT_STATE.md, citing BOTH merged specs (#1652 beat-driven, #1662 frame-selector);
     ratify the canonical recipe (beat-author → master-prompt seed-locked render → AI-judge gate → best-of curate → assemble → publish-queue).
     IF governance requires explicit operator sign-off to move proposed→ratified, enter as status=proposed and ESCALATE (Pearl_Operator_Proxy) rather than self-ratifying.
  3. SUBSYSTEM_AUTHORITY_MAP.tsv is a **5-TAB-field** schema: subsystem_id · authority_doc · config_path · owner_agent · status.
     The `video_pipeline` row ALREADY EXISTS — field 2 (authority_doc) is currently `config/video/;scripts/video/README.md`.
     EDIT FIELD 2 IN PLACE: semicolon-append the two merged spec paths. Do NOT append a new row; do NOT touch fields 1/3/4/5; preserve tabs + LF + trailing newline.
GUARDRAILS: no paid API. Commit via the plumbing path (temp index off origin/main^{tree} + GIT_LFS_SKIP_SMUDGE=1) — sidesteps the
  hot-file lock/poison. only required check = "Verify governance"; Workers Builds red = ignore; --squash; gh pr list --search first.
CLOSE: CLOSEOUT_RECEIPT — cap SHA + OPD-ID used + the before/after of the authority-map field-2 string; NEXT_ACTION = canonical-builder refactor (E) can land under this cap.
```

## 4 — 🟢 Books Phase B · clear the diagnosed gates (Pearl_Prime)

```
Pearl_Prime — Books-Shippability PHASE B: clear the diagnosed production-gate fails to ONE clean production PASS.
You are Pearl_Prime (core_pipeline + pearl_prime). Phase A is DONE — the full diagnosis is written and it CORRECTED the
assumed frontier. Execute the Phase-B plan in the diagnosis (§4), fix the composer defects that block the production gate stack,
and re-render the proof book to a clean PASS — or honestly report which single blocker is a content/craft frontier, not code.
A sibling execution wave OWNS 5 review PRs that touch your hot files — coordinate, never race.
EMIT A STARTUP_RECEIPT FIRST (docs/SESSION_UNITY_PROTOCOL.md). Routing:
  AGENT:          Pearl_Prime
  TASK:           books-shippability Phase B — clear the diagnosed gate fails (scene_anchor · chapter_flow · book_pass/angle · book_quality) to a production PASS
  PROJECT_ID:     proj_pearl_prime_bestseller_rebase_20260425  (composer-frontier thread; append a ws row)
  SUBSYSTEM:      core_pipeline; pearl_prime
  AUTHORITY_DOCS: artifacts/qa/books_shippability_20260616/BOOKS_SHIPPABILITY_DIAGNOSIS.md (wt-local, the Phase-A deliverable) (THE Phase-B map — read §2/§3/§4 first);
                  docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md; docs/PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md;
                  specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md; docs/SESSION_UNITY_PROTOCOL.md
  WRITE_SCOPE:    phoenix_v4/rendering/chapter_composer.py (A1 chapter-direction re-stamping; C opening-chapter thesis; F12 wrapper miss) +
                  phoenix_v4/planning/{enrichment_select,angle_journey}.py (B angle-layer commission — ONLY if a code gap) +
                  config/quality/refrain_allowlist.yaml (A2 named-mechanism cap — ONLY if Architect/operator rules it legit vocab) +
                  artifacts/qa/books_shippability_20260616/**  (re-proof renders + updated closeout)
  OUT_OF_SCOPE:   de-poison (.claude/worktrees — runs ALONE, not here); paid API; WEAKENING any gate threshold (fix the OUTPUT, not the gate —
                  the only sanctioned cap is the A2 refrain_allowlist entry, and only if operator/Architect approves); re-breaking the atom-parse
                  baseline (#1590/#1623/#1630/#1635 — VERIFY it holds, do NOT re-repair); re-opening word_budget (reconciled, 21,227 PASS) or
                  chasing ei_v2 "0.53" (it is 0.64 PASS on main); F7 practice-density cap (escalate to Pearl_Architect — governance); F13 dwell
                  (report as the operator's known craft frontier, NOT a code fix); deciding/assembling devotion_path O-11 (operator call); the
                  orthogonal PRs' subject matter (#1656 brand-wizard, #1658 CJK localizer, #1660 HOOK content)
  READY_STATUS:   ready  (self-gating on the wave — see COORDINATE)
⚠ COORDINATE (parallelism contract — obey exactly):
  • The in-flight wave OWNS #1655 (short-refrain F1, book_renderer.py), #1659 (_SeenBodies, enrichment_select.py), #1656/#1658/#1660.
    Sibling-search each (gh pr list/view) BEFORE touching book_renderer.py or enrichment_select.py. Your Phase-B fixes are net-new and
    live mostly in chapter_composer.py (a DIFFERENT file) — but still BASE them on origin/main AFTER #1655/#1659 land. One merger per PR;
    rebase, never clobber. Per the diagnosis: NONE of the 5 wave PRs flip this book's verdict — they are hygiene, not the gate-clearer.
  • de-poison stays OUT (tree-rewrite, runs solo in its own session).
SEED FACTS (verified on main in Phase A — do not re-derive, do not chase the phantoms):
  • Anchor = origin/main (9ec4a165f9). The WORKING TREE IS DRIFTED (174 behind / 180 ahead) and gives FALSE F2 fails. Build + measure ONLY
    from a clean snapshot: `git archive origin/main | tar -x -C $SNAP` (zero working-tree mutation, zero worktree-poison) — the Phase-A method.
  • Proof tuple (reproduce proof_courage_MAIN's verdict first as your baseline): corporate_managers × courage × false_alarm, --teacher sai_ma,
    --pipeline-mode spine, --quality-profile production, F006 arc (config/source_of_truth/master_arcs/corporate_managers__courage__false_alarm__F006.yaml,
    NOT forced), --seed 1, --render-book --skip-audio --no-job-check. Deterministic, NO paid API. exit-1 on overshoot ≠ build-fail.
  • register_gate is NOT wired into spine on main (PR #1536 wires it) — run it standalone; its FAILs are 0 HARD_FAIL today.
THE WORK — diagnosis §4, ordered by leverage. Each fix: plumbing-commit off origin/main^{tree} (+GIT_LFS_SKIP_SMUDGE=1), render from a snapshot
of (origin/main + your patch), measure the gate delta, sibling-search, RULE-0, do-NOT-merge unless clean-class. NEVER weaken a gate.
  1. A1 — chapter-direction re-stamping (THE scene_anchor lever; clears the early-return blocker). In chapter_composer.py (the only
     bridge_transition_families consumer): the SAME chapter-direction substring is stamped into 5+ bridge/transition sentences per chapter
     ("seeing the pattern before defending it" 5×, "moving from understanding into one repeatable action" 5×, "naming the cost that keeps
     accumulating" 4× — book.txt L60/68/74/103/105). Fix: vary the direction phrasing across a chapter's transitions, OR cap to ≤2 literal-
     direction carriers, OR register the substring with bridge_memory so it isn't re-stamped. Re-render → confirm scene_anchor PASS.
  2. A2 — named-mechanism cap (book_quality phrase-density HOLD). "the organizational cost calculation" 61× / "the automatic response is"
     74× are the topic's central named mechanism (78 REFLECTION variants), not broken prose. DECIDE WITH ARCHITECT/OPERATOR: legit topic
     vocabulary → add a config/quality/refrain_allowlist.yaml per-phrase entry (the gate already supports this); defect → composer-side
     variation. Do NOT just raise book_wide_cap globally. Re-render → confirm book_quality HOLD clears.
  3. C — chapter_flow Ch1/Ch2. Ch1 MISSING_CLEAR_POINT (thesis_hits=0, score 85 — close); Ch2 WEAK_TRANSITIONS. Fix opening-chapter thesis
     synthesis (plant a detectable clear-point) + Ch2 transition density. Localized to the chapter_composer opening path.
  4. B — angle_journey 0% (likely the hardest; may be the honest content-frontier). angle_journey_coherence reports chapters_with_angle_slots=0
     (need ≥80%), observed_layers=[]. ROOT-CAUSE whether spine mode commissions angle_layer_by_chapter at all (vs registry-mode metadata
     evaluate_angle_journey_coherence expects), or whether it's the pilot's arc-vs-runtime-format mismatch. If a code gap → thread the angle
     layer into the beatmap/enrichment so ≥80% chapters carry angle slots. If a CONTENT gap (no false_alarm angle atoms) or arc-vs-format
     mismatch → REPORT as content-frontier, do NOT fake.
  5. Hygiene merges (parallel, do NOT block the gate work): if the wave hasn't — merge #1659 (re-proven F1 17→15, deterministic, clean-class
     after squash) and #1655 (after its <40-char bridge-bank audit). Verify orthogonal #1656/#1658/#1660 by RULE-0 (clean-class, no double-merge). None flip the verdict.
  6. D residue (only gates if #1536 wires register): F12 ch11 raw "The guru is the mirror…" bypassing teacher_wrapper = small localized
     composer/wrapper fix. F7 (over-prescription) → escalate to Pearl_Architect (per-chapter practice-density cap, governance). F13 (dwell/
     integration starvation, 6 ch) → REPORT as the operator's known craft frontier, NOT a code fix.
  7. GOAL: re-render the proof book → clean production PASS, OR an honest per-gate statement of which single blocker is content/craft-frontier
     (B angle-atoms? A2 vocabulary? F13 dwell?) rather than code. A partial PASS with one named frontier is a valid, truthful outcome.
  ALSO surface (don't decide): O-11 devotion topic-fit — ship the 99 workplace-topic plans under the spiritual brand vs author a spiritual
  catalog. F-COHERENCE is RESOLVED (courage renders as courage); this is PURELY product, gated in PR #1619. Route to operator / Pearl_Operator_Proxy in PARALLEL — it does NOT block this proof.
GUARDRAILS: no paid API; deterministic. Pipeline TESTS need --quality-profile=draft. CI = source of truth (build/measure from the origin/main
  snapshot, never the drifted tree). Only required check = "Verify governance"; Workers Builds red = ignore. Branch from origin/main; plumbing-commit.
STOP + escalate: any gate that is a months-long content/craft frontier (report, don't fake); if a fix would re-touch the atom-parse baseline
  (the #1590 regression trap — verify it holds, don't repair); A2 named-mechanism allowlist (Architect/operator); F7 cap (Architect); O-11 (operator).
CLOSE: CLOSEOUT_RECEIPT — per-gate before/after production verdict on the proof book (which gates now PASS, full SHAs); the A1/C/B/F12 fixes
  landed (do-NOT-merge PRs, SHAs) + which wave PRs you merged (coordinated); the honest content/craft-frontier statement for any unclearable gate;
  NEXT_ACTION (assembly re-dispatch once the book passes + the O-11 answer). Auto-open the re-rendered proof book + updated diagnosis in Finder.
```

## 5 — 🟢 de-poison · 3 residual `_wt_*` gitlinks (Pearl_GitHub)

```
Pearl_GitHub — DE-POISON (residual): remove the 3 stray phantom _wt_* gitlinks PR #1577 missed. This is NOT the mass-deletion it was framed as.
GROUNDED CORRECTION (verified live this session):
  • The big committed worktree poison was ALREADY removed by PR #1577 (d40ad927e3). On origin/main TODAY `.claude/worktrees` = 0 tracked paths.
  • The ENTIRE committed residual = 3 root-level phantom gitlinks with NO .gitmodules registration: _wt_beatmap, _wt_inj, _wt_r2_sai_ma.
    3 deletions / 57,700 files → sub-RULE-0; does NOT trip push_guard/governance.
  ⚠ DO NOT TOUCH `Qwen` and `Qwen-Agent`: LEGIT submodules registered in origin/main:.gitmodules (url github.com/Ahjan108/Qwen{,-Agent}.git).
    They appear as mode-160000 gitlinks but are intentional. Deleting a registered submodule is its own incident.
  • The ~110GB is purely LOCAL `.claude/worktrees/*` checkout disk (untracked on main) — a SEPARATE GC lane (below), not a main-tree commit.
EMIT A STARTUP_RECEIPT FIRST (docs/SESSION_UNITY_PROTOCOL.md):
  AGENT:          Pearl_GitHub
  TASK:           remove the 3 residual phantom _wt_* gitlinks from origin/main + harden gitignore; PROTECT Qwen/Qwen-Agent
  PROJECT_ID:     none; append a ws row under proj_state_convergence_20260328
  SUBSYSTEM:      repo-hygiene (Pearl_GitHub)
  AUTHORITY_DOCS: CLAUDE.md (Non-Negotiable Git Rules + RULE-0); origin/main:.gitmodules (the PROTECT-list); scripts/ops/worktree_cleanup_audit.sh + worktree_cleanup_daily.sh (LOCAL-disk reclaim); docs/AGENT_FILE_PERSISTENCE_PROTOCOL.md; docs/SESSION_UNITY_PROTOCOL.md
  READ_PATH_COMPLETE: <yes>
  WRITE_SCOPE:    a plumbing-commit off origin/main^{tree} dropping exactly 3 tree entries (_wt_beatmap, _wt_inj, _wt_r2_sai_ma) + (if missing) a .gitignore line covering `_wt_*/` and `.claude/worktrees/`; one ws-row append
  OUT_OF_SCOPE:   Qwen, Qwen-Agent (PROTECT — never delete); .claude/worktrees on main (already untracked by #1577); any non-gitlink file; the local ~110GB disk rm (SEPARATE cleanup-script lane); creating a worktree; the books/video/install lanes
  BLOCKERS:       none
  READY_STATUS:   ready — PARALLEL-SAFE (plumbing-commit touches neither working tree nor index → no index-lock contention → the old "fire alone/last" rule does NOT apply to this 3-gitlink removal)
THE WORK (committed-tree residual — tiny, clean):
  1. VERIFY scope live: `git ls-tree -r origin/main | grep '^160000'` → expect EXACTLY: Qwen, Qwen-Agent, _wt_beatmap, _wt_inj, _wt_r2_sai_ma.
     `git show origin/main:.gitmodules` → confirm ONLY Qwen + Qwen-Agent registered (the 3 _wt_* are NOT → phantom → removable). If the set differs → STOP + re-report.
  2. Build a plumbing-commit off origin/main^{tree} (GIT_LFS_SKIP_SMUDGE=1, NO worktree, NO index mutation): read the tree, drop the 3 _wt_*
     gitlink entries (`git update-index --force-remove` index-only is instant; `git rm --cached` STALLS on submodule status), write the tree, commit on a branch off origin/main.
  3. If .gitignore lacks coverage, add `_wt_*/` and `.claude/worktrees/` so this cannot re-poison (verify #1577's gitignore scope first).
  4. GATE before push: `git diff --stat origin/main <commit>` == EXACTLY 3 deletions (the 3 _wt_*), 0 other deletions, 0 mods beyond the optional
     .gitignore line; Qwen/Qwen-Agent/.gitmodules UNCHANGED. Anything else in the diff → STOP.
  5. do-NOT-merge PR; operator eyeballs it (any deletion PR gets a look). Only required check = "Verify governance".
SEPARATE LANE — LOCAL ~110GB disk reclaim (the only part wanting a quiet field; NOT a main-tree op):
  Reclaim via the SANCTIONED scripts, never a raw rm: `bash scripts/ops/worktree_cleanup_audit.sh` (read-only KEEP/SAFE/VERIFY classifier) →
  for SAFE-classified ONLY, `bash scripts/ops/worktree_cleanup_daily.sh` (archives each branch → origin FIRST, then removes; never --force).
  SAFE is often 0 (most worktrees are LOCAL_ONLY unpushed → push/archive before reclaim). Wants no concurrent git-writer. Independent of the 3-gitlink commit above.
GUARDRAILS: branch from origin/main; plumbing-commit only; never rm the legit submodules; never raw-rm worktree dirs (use the scripts).
STOP + escalate: gitlink set ≠ the expected 5; any diff entry beyond the 3 _wt_*; a worktree the audit flags VERIFY (may hold unpushed work).
CLOSE: CLOSEOUT_RECEIPT — full SHA of the 3-gitlink removal PR; the verified `git diff --stat` (exactly 3 deletions); confirmation Qwen/Qwen-Agent untouched; the disk-reclaim audit classification (KEEP/SAFE/VERIFY counts) + GB freed if the daily GC ran; NEXT_ACTION.
```

## 6 — 🟢 builder-ext · `.jpg→.png` source-fix (Pearl_Video)

```
Pearl_Video — BUILDER-EXT (low-urgency cleanup): fix build_frame_selector_v2.py's JS export so manga chosen_render is .png at the SOURCE.
The builder's Python manga_name() normalizes .jpg→.png, but the JS renderPath() does NOT — so a manga pick exports
chosen_render=manga_frames/manga_<x>.jpg, a path that never exists on disk. assemble_mixed.py (#1663) compensates downstream;
this makes the export honest at the source. ONE-LINE fix — could also be folded into the next time the builder is touched.
EMIT A STARTUP_RECEIPT FIRST (docs/SESSION_UNITY_PROTOCOL.md):
  AGENT:          Pearl_Video
  TASK:           normalize manga extension (.jpg/.jpeg→.png) in build_frame_selector_v2.py's JS renderPath() so chosen_render resolves to a real file
  PROJECT_ID:     proj_state_convergence_20260328  (video_pipeline; append a ws row)
  SUBSYSTEM:      video_pipeline
  AUTHORITY_DOCS: docs/specs/PEARL_VIDEO_FRAME_SELECTOR_BEST_OF_V1_SPEC.md (export-schema authority, merged #1662); docs/VIDEO_PIPELINE_SPEC.md; docs/SESSION_UNITY_PROTOCOL.md
  WRITE_SCOPE:    scripts/video/build_frame_selector_v2.py (the JS renderPath() one-liner; base the edit on origin/main — it is there via #1662) + optionally the spec note that manga chosen_render is always .png
  OUT_OF_SCOPE:   the ~2.7MB regenerated HTML (local artifact — never commit); re-rendering MP4s; REMOVING assemble_mixed.py's _normalize_manga_render() (KEEP it — already-downloaded exports still carry .jpg; the compensation stays belt-and-suspenders); paid API; books/install/de-poison lanes; creating a worktree
  READY_STATUS:   ready (parallel-safe; independent of every other lane)
THE WORK:
  • origin/main:scripts/video/build_frame_selector_v2.py line ~462: `return (st === 'manga') ? ('manga_frames/manga_' + fname) : ('frames/' + fname);`
    → normalize the manga branch only: `('manga_frames/manga_' + fname.replace(/\.jpe?g$/i, '.png'))`. Mirror the Python manga_name() (line ~57)
    and the assembler's _normalize_manga_render() (#1663) EXACTLY — same .jpg/.jpeg→.png, manga-only, regular path untouched.
    NOTE: this JS lives inside a Python format-template (doubled `{{ }}`), but the fix line has no braces → drop-in.
  • Regenerate the HTML locally and grep one manga export line to confirm chosen_render now ends in .png (do NOT commit the HTML).
GUARDRAILS: base the edit on `git show origin/main:...` (working tree is 174 behind); plumbing-commit off origin/main^{tree}; sibling-search
  "build_frame_selector_v2"; only required check = "Verify governance"; do-NOT-merge. KEEP the assembler's compensation (don't "clean it up").
CLOSE: CLOSEOUT_RECEIPT — the one-line renderPath() diff; a regenerated-export spot-check (a manga chosen_render now ends .png); confirmation the assembler's _normalize_manga_render() was left intact; SHA.
```

## 7 — 🟡 install · Pearl Star Job Queue V1 Phase A (Pearl_Int) — GO on operator sudo + reboot ack

```
Pearl_Int — INSTALL: Pearl Star Job Queue V1, Phase A (Postgres 17 + Procrastinate + ComfyUI-Persistent-Queue + 6 systemd + pscli/watchdog + flux_schnell worker + A1/A2/A3 smokes) on the Pearl Star host.
The merge-gates that blocked this on 2026-06-11 are now CLEAR (PR #1492 merged 2026-06-12; cap PEARL-STAR-JOB-QUEUE-V1-01 ACTIVE on
origin/main). Re-verify the pre-reqs LIVE, then execute Phase A. OPERATOR-COUPLED: it needs an interactive NOPASSWD-sudo grant on Pearl
Star and smoke A3 REBOOTS the box — request both before any destructive step.
EMIT A STARTUP_RECEIPT FIRST (docs/SESSION_UNITY_PROTOCOL.md). Routing:
  AGENT:          Pearl_Int
  TASK:           Pearl Star Job Queue V1 — Phase A install + A1/A2/A3 acceptance smokes on the Pearl Star host
  PROJECT_ID:     none (governed by cap PEARL-STAR-JOB-QUEUE-V1-01, ACTIVE on origin/main PEARL_ARCHITECT_STATE.md §~2704); append a ws row under proj_state_convergence_20260328
  SUBSYSTEM:      integrations (Pearl_Int).  NOTE: the proposed `pearl_star_capacity_and_queue` row is NOT yet in SUBSYSTEM_AUTHORITY_MAP.tsv — FLAG it as a gap; do NOT add it here (the Video-D session owns the map this wave — two writers = collision)
  AUTHORITY_DOCS: docs/specs/PEARL_STAR_JOB_QUEUE_V1_SPEC.md (main-only)  (§8 Phase A + §13 acceptance — READ FROM origin/main: `git show origin/main:docs/specs/PEARL_STAR_JOB_QUEUE_V1_SPEC.md`; the working tree is 174 behind and LACKS it);
                  docs/PEARL_STAR_JOB_QUEUE_V1_SESSION_HANDOFF_20260611.md (wt-local)  (§5 install plan — read the working-tree copy);
                  artifacts/research/pearl_star_capacity_and_queue_20260611/{SOFTWARE_INVENTORY,HARDWARE_INVENTORY,STALL_RECOVERY_RUNBOOK,JOB_SIZING_GUIDELINES}.md;
                  CLAUDE.md (Tier policy); docs/INTEGRATION_CREDENTIALS_REGISTRY.md (Pearl Star endpoints + Keychain eval); skills/pearl-int/SKILL.md; docs/SESSION_UNITY_PROTOCOL.md
  WRITE_SCOPE (repo, via plumbing-commit — NO worktree):
                  scripts/pearl_star/install/{01_postgres17,02_procrastinate,03_comfyui_persistent_queue,04_directories}.sh ·
                  the 5 systemd unit files · bin pscli + watchdog.py + monitor.py · flux_schnell_worker.py · smoke A1/A2/A3 ·
                  artifacts/qa/pearl_star_phase_a_install_evidence_20260611/** · docs/specs/PEARL_STAR_JOB_QUEUE_V1_SPEC.md §13 append (based on the origin/main copy) · one ws-row append
  HOST SCOPE (Pearl Star over SSH — NOT committed): Postgres 17 · Procrastinate venv+schema · ComfyUI-PQ node · pearl-star user+dirs · 6 systemd units enabled+active
  OUT_OF_SCOPE:   Phase B (llm/tts/orch workers + pipeline_registry wiring) · Phase C (Prometheus/Grafana) · Phase D (multi-node); paid API; committing Pearl Star host state; ADDING the pearl_star subsystem row to the authority map (flag → Architect); creating any worktree (worktree-poison + disk-constrained); the books/video lanes; de-poison
  BLOCKERS:       OPERATOR-COUPLED — (1) live NOPASSWD-sudo grant on Pearl Star; (2) explicit ack that smoke A3 REBOOTS Pearl Star. Idle-window marker EXPIRED 2026-06-12 → re-probe + re-reserve live.
  READY_STATUS:   ready (merge-gates CLEAR; pending operator sudo + reboot ack)
THE WORK:
  1. RE-RUN the 4-gate pre-req check (handoff §3.1) — do NOT trust this header; verify live:
       G1 PR #1492 MERGED  → `gh pr view 1492 --json state,mergedAt`  (expected MERGED 2026-06-12)
       G2 cap ACTIVE on origin/main → `git show origin/main:docs/PEARL_ARCHITECT_STATE.md | grep PEARL-STAR-JOB-QUEUE-V1-01`  (expected §~2704 ACTIVE)
       G2b subsystem row → confirm STILL MISSING on origin/main (note only; not a hard gate)
       G4 Pearl Star reachable+idle → `ssh pearl_star` live probe (uptime/load/GPU/VRAM) + WRITE a fresh idle-reservation marker (the 2026-06-11 one expired).
     If ANY hard gate (G1/G2/G4) FAILs → STOP + report which + what unblocks it.
  2. REQUEST operator sudo + reboot-ack BEFORE any destructive host step. If not granted → STOP (route via Pearl_Operator_Proxy if it's a decision, not a credential).
  3. Author the ~16 repo artifacts per spec §8 / handoff §5.1 (exact unit/script contents from the spec on origin/main). Tier-2 ONLY (Postgres/Procrastinate/ComfyUI/Ollama/CosyVoice2 — all local/free; audit_llm_callers must stay clean).
  4. Execute the host install over SSH (handoff §5.2): Postgres 17 (127.0.0.1:5432, schema pearl_star_queue) · Procrastinate venv /opt/pearl-star/venv + `procrastinate schema --apply` · ComfyUI-Persistent-Queue node + restart · pearl-star user + /opt|/var/log|/var/lib/pearl-star dirs · enable+start 6 systemd units.
  5. Run the 3 HARD smokes (handoff §5.3): A1 flux-schnell cover dispatch → COMPLETED <60s · A2 watchdog stall (FORCE_STALL=1 sleep 600) → STALL_WARN 2× → SIGKILL 3× → requeue succeeds · A3 REBOOT persistence (operator-confirmed `sudo systemctl reboot`; 5 queued jobs survive → resume+complete <10min post-boot · 0 dup · 0 loss).
  6. Capture the evidence bundle (handoff §5.5) + append spec §13 "Phase A Acceptance — PASS 2026-06-16" with verbatim A1/A2/A3 evidence. Verify the 6 acceptance criteria (spec §13 / handoff §5.4).
GUARDRAILS: Tier-2 only, no paid API, audit_llm_callers clean. NO worktree — plumbing-commit the repo artifacts off origin/main^{tree}
  (+GIT_LFS_SKIP_SMUDGE=1); base the spec §13 edit on `git show origin/main:...`, not the absent working-tree copy. Only required check =
  "Verify governance"; Workers Builds red = ignore. do-NOT-merge (operator reviews the evidence bundle before merge per handoff §10.1).
STOP + escalate: any hard pre-req gate fails; sudo/reboot not granted; Pearl Star unreachable/busy; a smoke FAILS (report the verdict, never fake a PASS); mid-install operator-tier decision → Pearl_Operator_Proxy.
CLOSE: CLOSEOUT_RECEIPT — repo-artifact PR full SHA; A1/A2/A3 verdicts (verbatim) + the 6 acceptance criteria; evidence-bundle path; the live re-probe result + new idle-marker; the still-missing subsystem-row flag (→ Architect); NEXT_ACTION (operator merges install PR after evidence review → Pearl_PM rollout tracker → Phase B). Auto-open the evidence bundle in Finder.
```

## 8 — 🔶 E · canonical builder (Pearl_Video) — HOLD until B lands

```
Pearl_Video — VIDEO E (GATED: dispatch ONLY after B's run_frame_judge.py is on origin/main): build the canonical builder that gets the
best videos into the publish path (today they die as local MP4s).
EMIT A STARTUP_RECEIPT FIRST (docs/SESSION_UNITY_PROTOCOL.md):
  AGENT:          Pearl_Video (+ Pearl_Dev hat for the run_pipeline wiring)
  TASK:           build_beat_driven.py (generalize the v3_* one-offs) + emit distribution_manifest.json + wire run_pipeline
  PROJECT_ID:     proj_state_convergence_20260328  (video_pipeline; append a ws row)
  SUBSYSTEM:      video_pipeline
  AUTHORITY_DOCS: artifacts/video/video_best_method_20260616/VIDEO_BEST_METHOD_CONSOLIDATION.md (wt-local) (the recipe + the flagged refactor);
                  docs/specs/PEARL_VIDEO_BEAT_DRIVEN_NARRATIVE_PIPELINE_V1_SPEC.md; docs/specs/PEARL_VIDEO_FRAME_SELECTOR_BEST_OF_V1_SPEC.md;
                  B's run_frame_judge module API (from B's CLOSEOUT_RECEIPT); docs/VIDEO_PIPELINE_SPEC.md; CLAUDE.md (Tier policy); docs/SESSION_UNITY_PROTOCOL.md
  READ_PATH_COMPLETE: <yes>
  WRITE_SCOPE:    scripts/video/build_beat_driven.py (NEW, generalized) + the distribution_manifest.json emit + run_pipeline wiring + tests
  OUT_OF_SCOPE:   re-deriving the judge (CONSUME B's run_frame_judge.py module); re-rendering MP4s / FLUX-Qwen invocation (paid/GPU);
                  retiring the v3_* one-offs in the same PR (deprecate, don't delete); the publish/upload side beyond emitting the manifest; paid API
  BLOCKERS:       B not yet merged → BASE this branch on origin/main + B's commit
  READY_STATUS:   GATED on B (do not dispatch until run_frame_judge.py is on origin/main)
THE WORK (per the consolidation report's flagged refactor):
  • GENERALIZE the v3_* / intelligent_v3_6/7 one-offs into ONE parameterized scripts/video/build_beat_driven.py:
    inputs (brand/script/beats) → master-prompt seed-locked render → run_frame_judge.py gate (B) → best-of curate → assemble → compat.
    Driven by config/video/ knobs (channel_registry, presets), not hardcoded per-version constants.
  • EMIT distribution_manifest.json into publish_queue/ — the KEY fix: build_daily_batch.py is a publish-queue SELECTOR that reads these
    manifests; the best videos never emitted one, so they never entered distribution. Match the existing manifest schema (read a real one).
  • WIRE into the canonical builder run_pipeline.py (the 11-stage) so beat-driven is the default path, not a side script.
  • Tests: the builder produces a valid distribution_manifest.json the selector accepts; mock renders/judge (no GPU in CI).
GUARDRAILS: no paid API; no live full render in CI. Branch from origin/main; plumbing-commit; sibling-search "build_beat_driven";
  only required check = "Verify governance"; do-NOT-merge (consequential pipeline change — operator confirms). Pearl Star may be offline →
  the builder must degrade gracefully (judge skips, render stubs) so structure is testable without GPU.
STOP + escalate if the generalization is larger than a clean single-PR core (then ship the build_beat_driven scaffold + manifest emit, and
  SPEC the run_pipeline wiring + v3_* retirement as a follow-on — don't half-wire the canonical builder).
CLOSE: CLOSEOUT_RECEIPT — build_beat_driven.py + a sample distribution_manifest.json it emitted + the run_pipeline wiring status (done vs spec'd)
  + the v3_* deprecation note + confirmation a best-video now enters the publish queue. SHA; do-NOT-merge.
```

---

## To finish 100%

1. Paste **1–6** into six fresh chats now (parallel-safe).
2. Fire **7 (install)** once the live NOPASSWD-sudo + smoke-A3-reboot ack is granted.
3. Hold **8 (E)** until **B** merges.
4. Operator-only, no prompt: **RunComfy cancel** (~Jun 24 money clock), review **#1580 / #1542 / #1619** + the devotion topic-fit call.
5. de-poison (lane 5) can be dispatched as its own chat OR executed inline by the router on "go".
