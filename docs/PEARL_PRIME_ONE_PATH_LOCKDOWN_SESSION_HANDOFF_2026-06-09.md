# Pearl Prime ONE-PATH Lockdown — Session Handoff (2026-06-09)

**Session window:** 2026-06-06 → 2026-06-09 (Pearl_Prime → Pearl_Architect → Pearl_PM dispatch).
**Author of this handoff:** Pearl_Architect (the session orchestrator).
**Purpose:** single document covering the full session arc, what landed on main, what's in flight, what's broken, what the next session restarts on. Read this first when resuming.

---

## §1 — TL;DR

- **Pearl Prime ONE-PATH lockdown V1 is law on main.** 20-dimension canonical path defined; 18-row deletion manifest enumerated; runtime fail-fast contract specified; 6 child ws's queued.
- **Storefront-V1 infrastructure is live on main.** CF Pages + D1 + R2 + KV + Snipcart wiring scaffold + 12 UI mockups + 17,688-row sku_url_map.yaml + atom-audit Stage 1 detector + CI guard.
- **16 operator decisions logged** at `artifacts/coordination/operator_decisions_log.tsv` (OPD-20260606-001 through -016).
- **Cross-program SKU-join contract ratified** (Q-PRP-STOREFRONT-CONTENT-GATE-01): mechanical SKU expansion as Phase 3a per-persona atom backfill lands, no operator approval per-SKU.
- **8 PRs merged**, 4 PRs cleanly closed (broken with 57k staged deletions OR superseded), 4 agents dispatched + re-dispatched for Phase 1 mechanical / Phase 3a Wave 1 / ja-JP freebie / Stage 2a localized audit.
- **Phase A launch ETA: ~2 weeks.** ~21 launch-day SKUs (gen_z_professionals × anxiety × 7 formats × 3 locales); catalog grows automatically as Wave 1 (corp_mgrs + working_parents + first_responders) lands.

---

## §2 — Mission arc (chronological)

| Step | Mission | Outcome |
|---|---|---|
| 1 | **Pearl_Prime status + outline + 20-format smoke** (operator's original ask) | `artifacts/qa/pearl_prime_status_2026-06-06.md` (44 KB) + 13 book.txt outputs at `/tmp/pearl_prime_status_assembly_2026-06-06/` + `AGGREGATED_RESULTS.tsv`. Standard_book overshot 20K ceiling (20929 wc vs ceiling 20000). Only deep_book_4h passed production-profile gates clean. |
| 2 | **7-axis full audit** (operator follow-up) | 6 parallel general-purpose subagents + 1 Pearl_Architect synthesis = `artifacts/qa/pearl_prime_audit_2026-06-06.md` (26 KB). Per-axis findings at `/tmp/pearl_prime_audit_2026-06-06/agent{1..6}_*.md`. Identified: registry-source layer tapered (chapters 02-12 have 7-9 sections not 10); 85% of master arcs declare `chapter_count: 20` not 12; 12 of 14 personas missing persona-keyed atom dirs; no de-DE/fr-FR atoms (breaks CATALOG-800-PER-BRAND-01 math); audiobook wpm broken for sub-2h formats. |
| 3 | **Regression diagnosis (gen_z gold-ref vs corp_mgrs smoke)** | `artifacts/qa/pearl_prime_why_smoke_was_worse_2026-06-06.md` (14 KB). Root cause: `atoms/gen_z_professionals/anxiety/TEACHER_DOCTRINE/CANONICAL.txt:9` contains the "Slack at 9:47pm / footstep on street" carry_line; corp_mgrs equivalent does NOT exist → fallback to generic `teacher_banks/ahjan/doctrine/` produces voice fragmentation. Also: corp_mgrs F006 spiral arc has `chapter_count: 20` compressed into 12 spine → repetition cascade. |
| 4 | **CRAFT_DEPTH_OVERLAY proposal** (predecessor to ONE-PATH) | `docs/PEARL_PRIME_CRAFT_DEPTH_OVERLAY_PROPOSAL_2026-06-06.md` (18 KB) — 6 new gates G1-G6 + 5 writer contracts C1-C5. **Later SUPERSEDED-BY PEARL-PRIME-ONE-PATH-V1-01** (its G1-G6 + C1-C5 fold into D12-D20 as mandatory). |
| 5 | **PEARL_PRIME ONE-PATH lockdown V1 (the master spec)** | `docs/specs/PEARL_PRIME_ONE_PATH_LOCKDOWN_V1_SPEC.md` (426 lines) + cap entry `PEARL-PRIME-ONE-PATH-V1-01` in `docs/PEARL_ARCHITECT_STATE.md` + 18-row deletion manifest at `artifacts/qa/pearl_prime_one_path_deletion_manifest_20260606.tsv` + 6 child ws rows in `ACTIVE_WORKSTREAMS.tsv`. Originally PR #1473 — **closed broken** (57k staged deletions from `--no-checkout` worktree pattern) — replaced by clean **PR #1479** (commit `febd1fb95`, merged). |
| 6 | **Operator decisions** | Operator accepted all 13 lockdown defaults + chose Option B scope-gated launch + defined new Q-PRP-STOREFRONT-CONTENT-GATE-01 mechanical SKU-join criterion. 16 decisions logged. Originally PR #1478 — **closed broken** — replaced by clean **PR #1480** (commit `11843f9f8`, merged). |
| 7 | **Storefront-V1 5-PR cascade** (authored by parallel sibling sessions on 2026-06-06; merged this session) | #1448 PM tracker iter 1 (`da691d6c4`), #1454 Pearl_Writer atom audit Stage 1 (`db52b0293`), #1450 Pearl_Int CF + Snipcart (`5a481c1e2`), #1452 Pearl_Dev 12 mockups (`4c4ac5e0c`), #1453 Pearl_Marketing CTA cutover + 17,688-row sku_url_map (`2aa09807b`). |
| 8 | **PR #1455 Storefront AMENDMENT-2026-06-04.2** | Merge conflict with newly-landed main. Auto-rebase failed. **Closed as superseded** — its S1/S2/S3 surfacings + ja-JP freebie ws + Stage 2a localized audit ws are absorbed via the iter-2 tracker (#1481) + the 4 dispatched agents that will add ws rows organically. |
| 9 | **Pearl_PM Phase A tracker iter 2** | PR #1481 (commit `c1506b171`, merged). Incorporates seed §J cross-program intersection + §K post-merge cascade overlay + §L Phase A launch readiness gate + 16 OPD decision table. 318 lines added; iter-1 content preserved verbatim. |
| 10 | **4-agent dispatch** (Phase 1 + Phase 3a Wave 1 + ja-JP freebie + Stage 2a localized) | First dispatch stalled (system index.lock contention); second dispatch in flight. Each prompt cites the now-merged main artifacts + bans the `--no-checkout` worktree pattern. |

---

## §3 — What's on main (8 commits merged this session)

In merge order:

| Commit | PR | Owner | Description |
|---|---|---|---|
| `febd1fb95` | #1479 | Pearl_Architect (me) | ONE-PATH lockdown V1 spec + cap entry + 18-row deletion manifest + 6 child ws rows |
| `11843f9f8` | #1480 | Pearl_Architect (me) | 16 OPD operator decisions + iter-2 PM tracker seed + 6 child ws dispatch prompts |
| `da691d6c4` | #1448 | Pearl_PM (sibling session) | Phase A tracker iter 1 (initial authoring) |
| `db52b0293` | #1454 | Pearl_Writer (sibling) | Atom audit Stage 1 — en-US `anxiety` + `overthinking` detector |
| `5a481c1e2` | #1450 | Pearl_Int (sibling) | CF Pages + D1 + R2 + KV + Snipcart scaffold |
| `4c4ac5e0c` | #1452 | Pearl_Dev (sibling) | 12 UI mockups (en-US + ja-JP) + storefront.css + demo JSON |
| `2aa09807b` | #1453 | Pearl_Marketing (sibling) | HARD CTA cutover + 17,688-row `sku_url_map.yaml` + CI guard |
| `c1506b171` | #1481 | Pearl_PM (re-dispatched by me) | Phase A tracker iter 2 (incorporates seed §J/§K/§L) |

Verify on main: `git log --oneline origin/main | head -10`.

---

## §4 — What's closed (not on main; with reason)

| PR | Reason | Replaced by |
|---|---|---|
| #1473 | Broken — `--no-checkout` worktree caused 57,060 unintended file deletions to be staged. CLAUDE.md non-negotiable rule 0 forbids merging >50-file deletions. Halted before merge. | #1479 (clean re-author) |
| #1478 | Same staging bug. | #1480 (clean re-author) |
| #1457 | Stale sibling iter-2 tracker from 2026-06-06; superseded by #1481. | #1481 |
| #1455 | Merge conflict with newly-landed main; auto-rebase failed; content effectively absorbed by #1481 §J + dispatched agent ws-row additions. | #1481 + dispatched agent PRs |

---

## §5 — In flight (4 agents dispatched + re-dispatched)

All four agents include the **explicit `--no-checkout` ban** + sparse-checkout pattern as recovery from the PR #1473/#1478 staging bug.

| Agent | Owner | Expected PR(s) |
|---|---|---|
| Phase 1 mechanical sweeps | Pearl_Dev | 3 PRs: L03 SCENE→STORY label sweep + L05 vestigial `RUNTIME_TEMPLATES.chapter_count` delete + L11/D16 placeholder leakage strip + assert |
| Phase 3a Wave 1 — `corporate_managers × anxiety` persona-keyed atom backfill | Pearl_Editor + Pearl_Writer | 1 PR: 16 slot-type dirs (TEACHER_DOCTRINE / PERMISSION_GRANT / TEACHER_DOCTRINE_INTRO / ANGLE_DEFINITION / ANGLE_CALLBACK) modeled on gen_z gold-ref + smoke verification per Q-PRP-STOREFRONT-CONTENT-GATE-01 |
| ja-JP freebie landing pages × 15 | Pearl_Marketing | 1 PR: `brand-wizard-app/public/free_ja/<slug>/index.html` mirroring en-US + ja-JP email sequences + ja-JP social CTAs |
| Stage 2a localized atom audit | Pearl_Writer | 1 PR: detector extension (`scripts/ci/check_atoms_external_book_references.py --locale-scope localized`) + zh-TW + zh-CN + ja-JP sweep + `artifacts/qa/next_step_atom_audit_stage_2a_2026-06-09.tsv` + remediation routing summary |

Re-dispatched 2026-06-10 in clean shell state (first dispatch stalled on index.lock contention). 5-6 PRs incoming.

---

## §6 — 16 operator decisions logged

Full text at `artifacts/coordination/operator_decisions_log.tsv` rows OPD-20260606-001 through -016. Summary:

| OPD-id | Axis | Answer |
|---|---|---|
| 001 | META | Accept all 13 ONE-PATH recommended defaults |
| 002 | Q-OP-L01-ARC-STRATEGY-01 | (a) auto-compress 20-arc → 12 via spine-subset |
| 003 | Q-OP-L09-PERSONA-FLOOR-01 | (b) staged: corporate_managers + working_parents + first_responders FIRST |
| 004 | Q-OP-L10-LOCALE-SCOPE-01 | (b) demote CATALOG-800 to top-3 (en-US + ja-JP + zh-TW) |
| 005 | Q-OP-VOICE-BRAID-01 | (b) slot-zoned voice braid |
| 006 | Q-OP-CHAPTER-REPETITION-THRESHOLD-01 | (a) T=0.85; sentence-transformers all-MiniLM-L6-v2 local |
| 007 | Q-OP-METAPHOR-CAP-N-01 | (a) N=5 per chapter |
| 008 | Q-OP-SIGNATURE-PHRASES-COUNT-01 | (a) 5 phrases/book whitelist |
| 009 | Q-OP-DRAFT-PROFILE-SMOKE-01 | (a) --smoke flag exempt operator-attended runs |
| 010 | Q-OP-RUNTIME-FAIL-MESSAGE-LANGUAGE-01 | (c) both layers per §12 template |
| 011 | Q-OP-MIGRATION-CADENCE-01 | (a) single-PR-per-ws atomic |
| 012 | Q-OP-MOVE-4-VERDICT-RECOMPUTE-01 | (a) YES before Phase 1 dispatches |
| 013 | Q-OP-GOLD-REFERENCE-SHA-PIN-01 | (a) pin gold-ref SHA to MEMORY.md |
| 014 | Q-OP-CRAFT-DEPTH-OVERLAY-PROPOSAL-DISPOSITION-01 | (a) mark frontmatter SUPERSEDED-BY |
| 015 | STOREFRONT_LAUNCH_GATE | **Option B SCOPE-GATED** launch (~21 launch-day SKUs) |
| 016 | Q-PRP-STOREFRONT-CONTENT-GATE-01 (NEW) | Mechanical SKU-join criterion |

---

## §7 — Cross-program contract (Pearl_Prime ONE-PATH ↔ Storefront-V1)

**Q-PRP-STOREFRONT-CONTENT-GATE-01 (OPD-20260606-016 verbatim):**

> A SKU joins the storefront catalog when its **persona × topic** has all 16 persona-keyed atom dirs (HOOK / STORY / SCENE / REFLECTION / EXERCISE / COMPRESSION / PIVOT / PERMISSION / PERMISSION_GRANT / TAKEAWAY / THREAD / INTEGRATION / TEACHER_DOCTRINE / TEACHER_DOCTRINE_INTRO / ANGLE_DEFINITION / ANGLE_CALLBACK) AND a smoke `book.txt` lands within **±10% of gold-reference word count envelope** for the runtime format.

**Gold-ref word count envelopes** (from `artifacts/pearl_prime/gold_reference_ladder_2026-05-30/`):

| Runtime format | wc | ±10% envelope |
|---|---:|---|
| micro_book_15 | 6548 | [5893, 7203] |
| micro_book_20 | 8338 | [7504, 9172] |
| short_book_30 | 10538 | [9484, 11592] |
| standard_book | 19986 | [17987, 21985] |
| extended_book_2h | 27102 | [24392, 29812] |
| deep_book_4h | 39693 | [35724, 43662] |
| deep_book_6h | 56210 | [50589, 61831] |

**Implementation hook (post Phase 3a per-persona PR merge):**

1. CI smoke runs all 7 runtime formats for the newly-backfilled persona × {anxiety, burnout, overthinking, …}.
2. For each smoke that lands within ±10% envelope AND exits 0 under production profile, append SKU row to `config/storefront/sku_url_map.yaml`.
3. Cloudflare deploy workflow picks up the new SKU; storefront catalog grows.

**Catalog growth = mechanical consequence of Phase 3a landing.** No operator approval per-SKU.

---

## §8 — Phase A launch math

**Launch-day SKU subset (Option B SCOPE-GATED per OPD-20260606-015):**

- `gen_z_professionals × anxiety × ahjan × {micro_15, micro_20, short_30, standard_book, extended_2h, deep_4h, deep_6h}` × {en-US, ja-JP, zh-TW}
- = **7 formats × 3 locales = 21 launch-day SKUs**
- (If ja-JP or zh-TW smoke fails the ±10% envelope, scope reduces to en-US-only = 7 SKUs.)

**Catalog growth path:**

- Phase 3a backfill order per OPD-20260606-003 (b):
  - **Wave 1** (in flight): corporate_managers → working_parents → first_responders
  - **Wave 2**: healthcare_rns → gen_x_sandwich → tech_finance_burnout → millennial_women_professionals
  - **Wave 3**: gen_alpha_students → gen_z_student → nyc_executives → educators → midlife_women (last blocked on `ws_midlife_women_arc_authoring_20260427`)
- Each persona × topic combo that lands Phase 3a + passes the §7 criterion = +21 SKUs (or less if some topics aren't covered).
- Theoretical full-catalog at top-3 locale demote: 12 personas × ~15 topics × 7 formats × 3 locales ≈ **3,780 SKUs**.

**ETA:**
- Pearl_Dev Phase 1 mechanical sweeps (3 PRs): ~1 week
- Pearl_Marketing ja-JP freebie pages (15): ~1 week
- Pearl_Editor Phase 3a Wave 1 corp_mgrs × anxiety atom backfill + smoke: ~1-2 weeks
- → **Phase A launch ready ~2 weeks** with the ~21 + Wave 1 partial expansion.

---

## §9 — Open issues + restart points

### 9.1 — Operator action queue

1. **Review the 5-6 incoming PRs** from dispatched agents as they land. Recommend merge order:
   - Phase 1 mechanical sweeps (3 PRs) — review + merge first (smallest surface, mechanical)
   - Stage 2a localized atom audit — review + merge second (audit-only; opens Pearl_Editor remediation ws)
   - Phase 3a Wave 1 corp_mgrs × anxiety — review + merge third (largest surface; verify smoke results)
   - ja-JP freebie pages — review + merge fourth (preview at `/free_ja/<slug>/`)
2. **Pin gold-reference SHA + branch** to `~/.claude/projects/-Users-ahjan-phoenix-omega/memory/MEMORY.md` per OPD-20260606-013 (a). The ref is: `agent/gold-reference-7tier-redirect-20260530` + combo `gen_z_professionals × anxiety × spiral × F006 × ahjan × production × --exercise-journeys × --pipeline-mode spine`.
3. **Mark CRAFT_DEPTH_OVERLAY proposal frontmatter SUPERSEDED-BY** per OPD-20260606-014 (a). File: `docs/PEARL_PRIME_CRAFT_DEPTH_OVERLAY_PROPOSAL_2026-06-06.md`.
4. **Move 4 verdict recompute** per OPD-20260606-012 (a) — recompute under production+§13 rubric BEFORE Phase 1 mechanical sweeps dispatch their first PR. Pearl_Architect ws to author.
5. **Operator-action slots in `storefront_resource_ids.md`** (from PR #1450 scaffold) — 8 slots need real values (Cloudflare account ID, Stripe API keys, Snipcart account credentials, etc.). Fill before storefront goes live.
6. **R2 bucket population** (≥6 SKU assets, one per smoke combo) — operator R2 work; gated on #1450 merge + asset authoring.

### 9.2 — Ws status flips Pearl_PM should execute as part of meta-ws

- `ws_auto_plan_ssot_refactor_20260505` → **completed** (Audit Agent A3 confirmed refactor SHIPPED; `FORMAT_CHAPTER_COUNTS` removed; `get_format_chapter_count()` reads registry)
- `ws_register_gate_f11_hook_abstract_detector_20260523` → **scope-amend** to elevate F11 WARN→BLOCK per spec §2 D10
- `ws_exercise_strict_canonical_production_20260506` → **cross-link** to spec §2 D7
- `ws_pearl_prime_storefront_v1_framework_research_20260603` → **completed** (per PR #1481 §E)
- `ws_pearl_prime_storefront_v1_ui_mockups_20260603` → **completed** (post #1452 merge)
- `ws_pearl_prime_storefront_v1_cloudflare_wiring_20260603` → **in_progress** (scaffold landed; projector + application code = follow-ons)
- `ws_pearl_writer_next_step_atom_audit_20260603` → **completed Stage 1** (PR #1454 landed); Stage 2 ws to be opened by dispatched Pearl_Writer Stage 2a PR
- `ws_freebie_cta_redirect_unification_20260603` → **in_progress** (sweep + CI guard landed; projector reconciliation deferred)

### 9.3 — Workstreams to spawn after dispatched PRs land

- After Pearl_Dev Phase 1 PR 1.a merges → trigger **Phase 2 D8 PersonaAtomCoverageError ws** (depends on at least Wave 1 partial completion)
- After Phase 3a Wave 1 corp_mgrs × anxiety merges → trigger **next Wave 1 PR** (working_parents × anxiety) + sku_url_map.yaml automation
- After Pearl_Writer Stage 2a localized PR merges → trigger **Pearl_Editor off-catalog remediation ws** (`ws_pearl_editor_off_catalog_remediation_stage_2a_20260609`)
- After ja-JP freebie pages merge → mark Phase A launch precondition cleared per PR #1481 §L

### 9.4 — Phase 2 (runtime gates) — pending Phase 1 land

8 PRs per `artifacts/coordination/pearl_prime_one_path_child_ws_dispatch_prompts.md` "Prompt 2":
- 2.a D8 PersonaAtomCoverageError (waits for ≥3 personas Phase 3a complete to avoid breaking every existing combo)
- 2.b D4 VariantFloorError
- 2.c D1 ArcChapterCountError + auto-compress
- 2.d D7 EXERCISE strict-canonical promote
- 2.e D6 CatalogProfileError
- 2.f D10 F11 elevation
- 2.g D11 AudiobookWpmOutOfBandError + format_registry recalibration follow-up
- 2.h D18 `--pipeline-mode` default flip mirror sites (per `COHESIVE-FLOW-PATH-DEFAULT-SPINE-01`)

### 9.5 — Phase 4 (craft gates) — pending Phase 3a + 3b partial completion

8 PRs per dispatch prompts:
- 4.a D12 VoiceOutOfZoneError
- 4.b D13 CharacterIllustrationOnlyError
- 4.c D14 PronounContinuityError
- 4.d D15 SignalAmplificationMissingError
- 4.e D17 + D19 DecorativeMetaphorInflationError + signature_phrases whitelist
- 4.f D18 ChapterProgressionLoopError (sentence-transformers local)
- 4.g D20 GenericBuddhistDriftError
- 4.h Final cascade integration in scripts/run_pipeline.py

### 9.6 — Phase 3b (registry section backfill) — parallel to Phase 3a

Rolling per-topic PRs at `registry/<topic>.yaml`. 15 topics × ~33 sections short × ≥3 variants = ~1,350 net new variants. Topic order: anxiety + burnout + overthinking first (highest-traffic per Move 4).

---

## §10 — Restart points (resume next session here)

A future Pearl_Architect or Pearl_PM session restarting from cold opens these files in order:

1. **This handoff doc** — `docs/PEARL_PRIME_ONE_PATH_LOCKDOWN_SESSION_HANDOFF_2026-06-09.md`.
2. **Cap entry** — `docs/PEARL_ARCHITECT_STATE.md` → `PEARL-PRIME-ONE-PATH-V1-01` block (search for that ID).
3. **The master spec** — `docs/specs/PEARL_PRIME_ONE_PATH_LOCKDOWN_V1_SPEC.md` — §2 20-dimension table + §5 enforcement architecture + §7 migration sequence + §10 Q-OP-* (all answered via OPDs) + §12 failure-message template.
4. **Deletion manifest** — `artifacts/qa/pearl_prime_one_path_deletion_manifest_20260606.tsv` — 18 rows L01-L18.
5. **Operator decisions** — `artifacts/coordination/operator_decisions_log.tsv` rows OPD-20260606-001 through -016.
6. **Iter-2 tracker** — `artifacts/coordination/storefront_v1_phase_a_tracker.md` (now has iter-2 banner + §J cross-program intersection at top).
7. **Iter-2 seed** (historical reference) — `artifacts/coordination/storefront_v1_phase_a_tracker_iter_2_seed.md`.
8. **Child ws dispatch prompts** — `artifacts/coordination/pearl_prime_one_path_child_ws_dispatch_prompts.md` (6 prompts; copy-paste-able into Agent dispatches).
9. **6 child ws rows** — `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` (filter for `one_path` substring).
10. **Audit synthesis** — `artifacts/qa/pearl_prime_audit_2026-06-06.md` (the diagnostic ground truth).
11. **Regression note** — `artifacts/qa/pearl_prime_why_smoke_was_worse_2026-06-06.md` (the gen_z vs corp_mgrs causal trace).
12. **Status snapshot** — `artifacts/qa/pearl_prime_status_2026-06-06.md` (the original mission deliverable; §11 outline + §12 20-format smoke results).
13. **Gold-reference ladder** — `artifacts/pearl_prime/gold_reference_ladder_2026-05-30/deep_book_4h/book.txt` (the canonical truth; what good output looks like).

---

## §11 — Key file paths (single-place reference)

| Purpose | Path |
|---|---|
| Master spec | `docs/specs/PEARL_PRIME_ONE_PATH_LOCKDOWN_V1_SPEC.md` |
| Cap entry | `docs/PEARL_ARCHITECT_STATE.md` → `PEARL-PRIME-ONE-PATH-V1-01` |
| Deletion manifest | `artifacts/qa/pearl_prime_one_path_deletion_manifest_20260606.tsv` |
| Operator decisions log | `artifacts/coordination/operator_decisions_log.tsv` |
| Iter-2 tracker | `artifacts/coordination/storefront_v1_phase_a_tracker.md` |
| Iter-2 seed (historical) | `artifacts/coordination/storefront_v1_phase_a_tracker_iter_2_seed.md` |
| Child ws dispatch prompts | `artifacts/coordination/pearl_prime_one_path_child_ws_dispatch_prompts.md` |
| ws rows | `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` (filter `one_path`) |
| Audit synthesis | `artifacts/qa/pearl_prime_audit_2026-06-06.md` |
| Per-axis audit reports | `/tmp/pearl_prime_audit_2026-06-06/agent{1..6}_*.md` (ephemeral; mirrored in audit synthesis) |
| Status snapshot + 20-format smoke | `artifacts/qa/pearl_prime_status_2026-06-06.md` |
| Status assembly outputs | `/tmp/pearl_prime_status_assembly_2026-06-06/<format>/{book.txt, quality_summary.json, ...}` (ephemeral) |
| Regression note | `artifacts/qa/pearl_prime_why_smoke_was_worse_2026-06-06.md` |
| CRAFT_DEPTH_OVERLAY proposal (predecessor; SUPERSEDED) | `docs/PEARL_PRIME_CRAFT_DEPTH_OVERLAY_PROPOSAL_2026-06-06.md` |
| Gold-reference ladder | `artifacts/pearl_prime/gold_reference_ladder_2026-05-30/` |
| Gold-ref TEACHER_DOCTRINE atom (the load-bearing one) | `atoms/gen_z_professionals/anxiety/TEACHER_DOCTRINE/CANONICAL.txt:9` |

---

## §12 — Lessons learned (the worktree `--no-checkout` staging bug)

**Symptom:** PRs #1473 + #1478 each had `changedFiles: 57060` and `+517 / -8,033,402` instead of the intended ~500 lines added.

**Root cause:** the `--no-checkout` worktree pattern leaves the index populated with origin/main's tree but the working directory empty. When you `git add` your intended files, the staged-deletions of all the un-checked-out files from the worktree creation are ALSO in the index (apparently from an earlier `git status -A`-equivalent operation). The commit then includes both your intended changes + 57,060 file deletions.

**Detection:** `gh api /repos/.../pulls/<N>/files?per_page=100 --jq '[group_by(.status) | .[] | {status: .[0].status, count: length}]'` — any `removed` count anywhere near 50 should halt the merge per CLAUDE.md non-negotiable rule 0.

**Recovery:** close the broken PR + re-create on a CLEAN branch from origin/main with explicit checkout (full or sparse). Files recoverable from git history via `git show <broken-commit-SHA>:<path>`. No data lost.

**Prevention:** the 4 dispatched child agent prompts each include:

```
# CORRECT: full checkout OR sparse-checkout
git worktree add /private/tmp/wt-... -b <branch> origin/main
# OR
git worktree add --no-checkout /private/tmp/wt-... origin/main && \
  cd /private/tmp/wt-... && \
  git sparse-checkout init --no-cone && \
  git sparse-checkout set <only-paths-you-need> && \
  git checkout

# WRONG: do NOT use --no-checkout WITHOUT sparse-checkout
# It causes 57k staged-deletion bug.
```

Plus a pre-commit verification: `git diff --cached --stat | head -10` to confirm only intended files appear.

The lesson lands in the Pearl Prime / Pearl Architect / Pearl Dev memory bank as a load-bearing operational rule.

---

## §13 — Anti-drift check

- This handoff doc does NOT replace any cap entry or spec. It's a session log + reference index.
- All claims trace to a file on main (commit SHAs cited where relevant) or to a logged OPD.
- Authority order preserved: V4.5 Writer Spec → PHOENIX_ARC_FIRST_CANONICAL_SPEC → PEARL_PRIME_BOOK_SYSTEM_CANONICAL → PEARL_PRIME_ONE_PATH_LOCKDOWN_V1_SPEC → this handoff.
- Q-OP-* are all answered via OPDs in the log; no live operator-tier decisions in this doc.
- The 4 dispatched agents are NOT being re-spawned by this doc — they run independently and will PR back.

---

## §14 — Closing receipt

**STARTUP date:** 2026-06-06.
**HANDOFF date:** 2026-06-09 (this doc).
**Total PRs touched this session:** 12 (8 merged + 4 closed).
**Total operator decisions logged:** 16.
**Total dispatched agents:** 5 (1 returned successfully = #1481 PM iter-2; 4 re-dispatched, in flight).
**Total `--no-checkout` staging bugs caught + recovered:** 2.
**Status of Pearl Prime ONE-PATH lockdown V1:** **LIVE on main.** Pearl Prime cannot ship a lesser configuration silently once Phase 2 runtime gates land per the 6 child ws dispatch.

Next session resume from §10 above.

---

*Companion docs:*
- `docs/specs/PEARL_PRIME_ONE_PATH_LOCKDOWN_V1_SPEC.md` (the spec this handoff documents)
- `docs/PEARL_ARCHITECT_STATE.md` `PEARL-PRIME-ONE-PATH-V1-01` (the cap entry)
- `docs/PEARL_PRIME_CRAFT_DEPTH_OVERLAY_PROPOSAL_2026-06-06.md` (SUPERSEDED predecessor)
- `docs/PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md` (the V4 book system canonical contract)
- `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` (the bestseller overlay this lockdown promotes from advisory → mandatory)
