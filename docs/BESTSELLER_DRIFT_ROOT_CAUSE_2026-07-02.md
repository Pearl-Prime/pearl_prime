# Bestseller Quality Drift — Root-Cause Retrospective

**Date:** 2026-07-02  
**Owner:** Pearl_Architect  
**Base:** `origin/main` @ `b72722b738` (post #4566 `bcc31520eb`, #4583 `20401d38c2`)  
**Authority:** Canonical answer to *why* "bestseller" quality repeatedly drifted across sessions — books reported as passing/bestseller while reading as stitched one-liners.

---

## Executive summary

The drift was **not** missing atoms, a broken composer, or insufficient gate count. It was a **category error**: Layer-1 `register_gate` PASS was read as Layer-4 **bestseller register**, while a **default-path injector regression** (`365fd19cc3`) stitched books out of one-line dwell-beat filler (~35% beat-line share) that no HARD gate caught until F14 landed in #4583. Sessions kept "tuning the composer for catalog scale" when hand-seamed atoms already read as bestseller — the real lever is a **flagship line-edit lane**, not more composer scaffolding.

**Structural block (first time):** #4566 disabled the injectors; #4583 added F14 HARD_FAIL beat-line ceiling. A filler-stitched book can no longer pass the gate.

---

## DISCOVERY — register-PASS / bestseller claims vs actual prose

| Date / source | Claim | What the prose actually was | Gap |
|---|---|---|---|
| 2026-06-22 `artifacts/qa/waystream_render_bottleneck_snapshot_20260622.md` | "Register gate non-PASS in rendered dirs: **0**"; sample `corporate_managers__anxiety__comparison` → "register PASS" | 61 `book.txt` on disk; 45/66 dirs used **debug** `quality_profile` (gates skipped). Production sample passed regex gate — not human cohesion read. | Machine PASS on subset; debug renders excluded from gate semantics |
| 2026-06-22 `365fd19cc3` closeout | "Waystream pilot production-gate composer defects (F6/F7/F13)" shipped as fix | Introduced `register_output_strengthen.py` with `_DWELL_BEAT_POOL`, `_CADENCE_MICRO_BREAKERS`, word-floor padding on **default spine path** | Filler to game F6/F7/F13 metrics — root regression |
| 2026-06-24 `docs/sessions/SESSION_HANDOFF_2026-06-24_advisory_router_session.md` | "**register PASS / BUILD_EXIT=0**" for Theo Castellan EPUB | No Layer-3 ONTGP read; no acceptance-layer name | `register PASS` ≠ `system working` |
| 2026-06-30 `artifacts/qa/plan_scale_qa_pilot_20260630/FREE_TIER1_READS.json` | "Paragraph prose is **bestseller-adjacent**" + "Several cells **PASS register_gate**" | Same cells: "**fortune-cookie fragment flood**", disconnected bridge atoms recur across chapters/topics | register PASS + human cohesion-weak |
| 2026-06-30 `artifacts/qa/plan_scale_qa_pilot_20260630/README.md` | "12/13 assembled cells: plan-cohesion PASS → **register PASS/WARN**" | Human read: "plan-cohesion + register PASS together still **UNDER-predict** reader-felt cohesion" | Proxy validity break documented, not enforced |
| 2026-06-30 `artifacts/qa/book_quality_verify_20260630/SCORECARD.md` | Way Stream Sanctuary = "**canonical register-PASS**" → **SELLABLE_AS_IS** | Only 1 cell at composite 0.76; wave_proof spine books all **Cohesive flow CONCERN** (Tier-1 override) | register-PASS reference ≠ catalog-scale bestseller |
| 2026-07-01 PR #4486 / `waystream_800_build_ledger.tsv` (branch) | Assembly lane reports **58 assembled** cells; sessions summarized as "~57 register-PASS" | Ledger tracks `epub_assembled=YES`, not acceptance layer; pre-#4583 renders could PASS gate at ~35% beat-lines | Layer-1 count read as campaign-ready |
| 2026-05-18 `docs/PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md` | Explicitly names failure mode: "Agents optimize for **gate PASS** and think the work is done" | Doc existed; **not in CLAUDE.md**; not CI-enforced | Knowledge-only — did not bind behavior |
| 2026-07-02 `docs/PEARL_PRIME_BEATLINE_CEILING_CALIBRATION_2026-07-02.md` | Stitched render **198/565 = 35.0%** beat-lines → F14 HARD_FAIL; hand-seam FINAL **5/181 = 2.8%** → PASS | Proves injector-class prose is measurable and blockable | Evidence that closed the gate hole |

---

## 1. THE DRIFT MECHANISM (dated evidence + commit SHAs)

### (a) `register_gate` was F2-only HARD → regex PASS ≠ bestseller

**Evidence:** `phoenix_v4/quality/register_gate.py` module header (pre-#4583): only F2 (broken slot fragments) was HARD_FAIL. F1, F6, F7, F13 were WARN/FAIL advisory. A book of disconnected one-line beats could PASS if F2 was clean.

**Scorecard:** `docs/PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md` lines 14–17, 125–147 — machine gates prove `structurally clear` at Layer 1; **cannot** prove `bestseller register` (Layer 4).

**Fix:** #4583 `20401d38c2` — F14 beat-line-share HARD_FAIL at 25% cutoff.

### (b) `365fd19cc3` injected filler onto DEFAULT path to game metrics

**Commit:** `365fd19cc358595c7162e7fb448f5442b22f7eb1` (2026-06-22)

**What it added:**
- New `phoenix_v4/rendering/register_output_strengthen.py` (457 lines)
<!-- CI-ALLOWLIST: legacy-registry-ok — prose reference to run_pipeline.py, not an executed build invocation -->
- Wired into `scripts/run_pipeline.py` spine path via `strengthen_register_craft_output`
- `_DWELL_BEAT_POOL` (one-line beats: "Pause.", "Your shoulders drop a half inch.", …)
- `_CADENCE_MICRO_BREAKERS` ("One breath.", "Notice that.", …)
- Word-floor padding to hit minimum word counts

**Why:** Waystream pilot needed to clear F6 (cadence repetition), F7 (prescribed-action density), F13 (dwell-beat starvation), and word-count floors — **without** authoring cohesive multi-sentence atoms. The strengthener patched metrics post-render.

**Measured harm:** #4583 calibration — stitched EPUB class **35.0%** beat-line share vs hand-seam baseline **2.8%**.

### (c) No HARD gate caught filler + good chord was opt-in → recurred every render

**Recurrence:** `artifacts/qa/waystream_render_bottleneck_snapshot_20260622.md` — MANUSCRIPT_PASS_INVENTORY shows `strengthen_register_craft_output` + repair loop (F7×8, F13×5, floor×2) on **every** spine render. Injector ran on each build until #4566.

**Chord gap:** Canonical invocation requires `--pipeline-mode spine --quality-profile production --exercise-journeys`. Default CLI `--pipeline-mode` remained `registry`. G3 (#4583) added CI **warn-only** chord assert — chord-less catalog builds could still ship.

**Fixes:**
- #4566 `bcc31520eb` — dwell-beat + word-floor injectors **disabled**; F2.D bare-slot HARD gate
- #4583 `20401d38c2` — G1 spine padder off; G2 F14 ceiling; G3 chord CI assert (warn)
- **This lane** — G3 flipped WARN → BLOCK

### (d) Sessions lost work to churn; re-derived the same shortcut

**Evidence:**
- `docs/sessions/SESSION_HANDOFF_2026-06-18_devotion_manga_video.md` — parallel `bestseller_gate.py` copy on diverged branch; main canonical different
- Agent transcript `67ad63a1` — unpushed composer-lane worktrees (`wt-register-flip`, `wt-composer-deferred`) archived after near-loss
- Cohesion chunk prompts (2026-06-30) — success criteria = "register PASS maintained" (metric gaming, not cohesion read)

**Control that would have stopped it:** Promote lessons to CI/CLAUDE.md at merge time; archive-push branches before worktree removal.

### (e) Mis-framing: "tune the composer for catalog register"

**Evidence:** `artifacts/qa/plan_scale_qa_pilot_20260630/FREE_TIER1_READS.json` — "Paragraph-level prose is genuinely strong … **bestseller-adjacent**" but "assembled-book weakness is **COHESION between atoms**". Same atoms hand-seamed already read well; gap is inter-atom stitching and flagship line-edit, not composer topology.

**Anti-pattern:** Any session whose closeout says "improve register_gate / composer for catalog scale" without naming acceptance layer is repeating the drift.

---

## 2. WHY IT KEPT RECURRING — session table

| Session / artifact | What re-introduced or masked drift | Control that would have stopped it |
|---|---|---|
| 2026-06-22 Waystream pilot (`365fd19cc3`) | Shipped dwell-beat injector as "production-gate fix" | F14-class HARD ceiling before merge; ban post-render one-line injection on default path |
| 2026-06-22 bottleneck snapshot | Reported "register non-PASS: 0" across 61 books | Require acceptance-layer language; separate debug vs production gate results |
| 2026-06-24 advisory router handoff | "register PASS" reported as success | Scorecard status language in closeout template |
| 2026-06-30 plan-scale QA | Documented register≠human gap but closeout still used register PASS | Escalate FREE_TIER1_READS gap to HARD gate (→ F14) |
| 2026-06-30 cohesion chunks | Success = "register PASS maintained" | Name Layer 3 ONTGP or cohesion read, not gate alone |
| 2026-07-01 Waystream 800 assembly (#4486) | "~57 register-PASS" summarized as structurally clear | Ledger column for acceptance layer; F14 on all production renders |
| Recurring composer sessions | "Tune register_gate / composer" instead of line-edit lane | CLAUDE.md doctrine: composer ≠ flagship-register lever |
| Cursor / subagent sessions | No access to ~/.claude memory | CLAUDE.md + CI enforcement (memory is recall, not binding) |

---

## 3. PREVENTION — in place vs still missing

### IN PLACE (verified on `origin/main` @ `b72722b738`)

| Control | SHA / PR | What it enforces |
|---|---|---|
| Injector disabled | #4566 `bcc31520eb` | Dwell-beat + word-floor padding no-op on default path |
| F2.D bare-slot HARD | #4566 `bcc31520eb` | Unresolved `{SLOT}` fragments block ship |
| F14 beat-line HARD ceiling | #4583 `20401d38c2` | >25% one-line beats → HARD_FAIL |
| G1 spine padder off | #4583 `20401d38c2` | Under-length surfaced, not padded |
| Acceptance scorecard | `docs/PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md` | Names gate-PASS ≠ bestseller; 4-layer status language |
| G3 chord detector (was warn) | #4583 `20401d38c2` | Detects incomplete chord in PR-touched production invocations |

### STILL MISSING (before this lane)

| Gap | Smallest durable control | Status after this lane |
|---|---|---|
| G3 chord warn-only | Flip `drift-detectors.yml` WARN → BLOCK | **LANDED** (this PR) |
| Doctrine not in CLAUDE.md | 3-point anti-drift section | **LANDED** (this PR) |
| Four-piece chord not global default | CI BLOCK on changed invocations; global CLI flip = operator escalation (Q-ENFORCE-01) | CI only — intentional |
| No CI on closeout claims | Grep session/PR bodies for "bestseller"/"register-PASS" without acceptance layer | **PROPOSED** (Q-ENFORCE-02) — cheap regex, defer |
| Flagship line-edit lane | Standing process for 1–3 flagship cells/quarter; ONTGP Layer 3 read | **PROPOSED** — process, not code |
| Churn / orphan work | Archive-push all agent branches before worktree removal | **Existing** runbook; reinforce in handoffs |

### Proposed controls (not landed here)

**Q-ENFORCE-02 — closeout-claim grep (propose-only):**
```bash
# Fail if closeout claims bestseller/register-PASS without an acceptance-layer term
rg -i 'bestseller|register.?pass' CLOSEOUT.md \
  && ! rg -i 'structurally clear|authored candidate|system working|bestseller register|Layer [1-4]' CLOSEOUT.md
```

**Flagship line-edit lane:** For each brand's canonical cell (e.g. `way_stream_sanctuary × corporate_managers × burnout`), run Layer 3 ONTGP on Ch1/Ch5/Ch11 after every render-hardening change. Composer changes do not substitute.

---

## 4. THE ONE-PAGE RULE — anti-drift checklist

Every Pearl Prime / bestseller session MUST follow this. If all items pass, this specific drift cannot recur.

### Before you touch code

- [ ] Read `docs/PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md` and `docs/BESTSELLER_DRIFT_ROOT_CAUSE_2026-07-02.md`
- [ ] State the **acceptance layer** you are targeting (structurally clear / authored candidate / system working / bestseller register)
- [ ] Confirm task is NOT "tune composer for catalog register" unless Layer 3 read proved composer is the bottleneck

### Render / build

- [ ] Production renders use the **four-piece chord**: `--pipeline-mode spine --quality-profile production --exercise-journeys`
- [ ] No post-render one-line injectors on default path (injectors disabled #4566; F14 catches regression #4583)
- [ ] Under-length books → surface `spine_word_floor_signals`, do not pad

### Report / closeout

- [ ] **NEVER** say "bestseller" or "shippable" on `register_gate` PASS alone
- [ ] Name the acceptance layer every time
- [ ] If claiming cohesion, cite human read (Layer 3) or F14 beat-line share, not gate PASS count
- [ ] "register-PASS" is Layer 1 at best → say **structurally clear**, not bestseller

### Promote lessons (meta-rule)

- [ ] Every hard-won quality lesson → **CI hard gate**, **can't-bypass default**, or **CLAUDE.md rule** — not memory alone

---

## Cross-references

- Beat-line calibration: `docs/PEARL_PRIME_BEATLINE_CEILING_CALIBRATION_2026-07-02.md`
- Acceptance stack: `docs/PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md`
- F14 fixtures: `tests/fixtures/register_gate_f14/`
- Chord detector: `scripts/ci/check_canonical_pipeline_path.py`
- Injector regression: `365fd19cc3` → disabled `bcc31520eb` → ceiling `20401d38c2`

## Change log

- 2026-07-02: Initial authoritative root-cause doc + prevention checklist (Pearl_Architect retrospective).
