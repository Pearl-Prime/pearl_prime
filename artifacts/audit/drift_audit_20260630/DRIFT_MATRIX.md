# Plan-vs-Practice Drift Audit

**Date:** 2026-06-30  
**Agent:** Pearl_PM + Pearl_Architect (read-only coordination audit)  
**Ground truth:** `origin/main` @ `509ddd719e` · open PRs via `gh` · OPDs in `artifacts/coordination/operator_decisions_log.tsv`  
**SSOT entry:** `docs/PROGRAM_STATE.md` (LAST VERIFIED 2026-06-25 — noted where superseded by newer merges)

---

## DISCOVERY REPORT

### Plan-of-record sources

| Source | Role in ledger |
|--------|----------------|
| `docs/PROGRAM_STATE.md` | SSOT priorities, listing≠EPUB glossary, track status |
| `docs/PEARL_ARCHITECT_STATE.md` | Cap registry (ratified vs proposed), architect routing |
| `docs/specs/WORLDWIDE_CATALOG_GO_LIVE_V1_PROGRAM_SPEC.md` + `artifacts/qa/go_live_readiness_audit_2026-05-08.md` | P0/P1/P2 surface priority (Q1–Q5 ratified 2026-05-08) |
| `docs/sessions/SESSION_HANDOFF_2026-06-29_worldwide_catalog_books_cjk_manga.md` | Current lane map + Jul 1 resume sequence |
| `artifacts/coordination/ACTIVE_PROJECTS.tsv` | 17 projects by status |
| `artifacts/research/bestseller_pattern_fit_20260611/OUR_SYSTEM_VS_PATTERNS_GAP.md` | Research conclusion: assembler/quality is the lever, not more catalog rows |
| `artifacts/research/platform_optimization/anti_spam_platform_comparison.md` | Research conclusion: velocity + engagement gates matter at publish, not pre-assembly listing volume |
| OPD-20260627-001, OPD-20260629-001/002/003 | Latest steering (worldwide model, arc method, quality lane, GPU priority) |

### Actual-activity window

- **Merged on `origin/main`:** 2026-06-15 → 2026-06-30 (filtered for substantive vs skeleton churn)
- **Open PRs:** 694 total (`gh pr list --state open`, 2026-06-30)
- **Recently merged sample:** last 30 merged PRs (dominated by Western skeleton batches Jun 27–28)
- **OPDs:** rows 153–154 in `operator_decisions_log.tsv` (+ session handoff for OPD-001/003 context)

### Lanes scored

1. Catalog listings vs real EPUBs (Production-Gate spine)  
2. Lever A — arc-gen / buildability (educators/nyc thin cells)  
3. Composer / register frontier (OPD-20260629-002)  
4. CJK translation + GPU priority (OPD-20260629-003)  
5. Manga (titled/pilot vs render-thin / dispatch bug)  
6. Western localization (skeleton fan-out)  
7. Storefront / EPUB attach  
8. Proposed-program backlog (music v2, sangha, song-kit, teacher-manga-video, agent-system-v2, duration-derivation)

### Evidence method per verdict

- **Planned intent:** cite doc section or cap id  
- **Actual activity:** cite PR#, SHA, or OPD id  
- **Verdict:** compare intent priority order vs where merge/PR volume actually went  
- **Skeleton PRs:** counted separately — never equated to shipped books  

---

## 1. PLAN-OF-RECORD LEDGER

Priority order reconstructed from SSOT + session handoff (Jun 29 supersedes May worldwide phase plan for *execution sequencing*):

| Priority | Planned work | Research / plan conclusion | Source |
|---------|--------------|---------------------------|--------|
| **P0** | Turn ~1,519 listings + ~32k plannable en_US plans into **real, gate-passing EPUBs**; assembly → R2, not git | Bottleneck is **assembly + quality**, not catalog row count; 1 EPUB proves path | `PROGRAM_STATE.md` Production-Gate; `OUR_SYSTEM_VS_PATTERNS_GAP.md` §0 |
| **P0** | Close buildability blockers: flip campaign → pilot → assembly; thin-persona engine-keyed pools | +462 arc-seeded cells still **NOT spine-buildable** (NO_STORY_POOL) | `PROGRAM_STATE.md` ⚠ thin-persona caveat; session handoff §2 |
| **P1** | Pearl Prime quality lane: register/composer fixes before mass assembly | F2/F4/F6 renderer artifacts, not atom mass-reformat | OPD-20260629-002; research craft-failure root cause |
| **P1** | CJK atom translation (GPU) before manga renders | 89% held-back parse-fail class; ko/zh gaps | Session handoff §5; OPD-20260629-003 |
| **P2** | Western localization: localize en_US (OPD-20260627-001), **after** flip makes cells buildable | Translated editions ≠ spam; inherit en atoms via flip | OPD-20260627-001; session handoff §6 |
| **P2** | Manga: queue-unblock + curated ~6,200 renders, **post-CJK** | Render-thin (0.13% panels); dispatch bug not throughput | Session handoff §7; OPD-20260629-003 |
| **Deferred** | Storefront Phase A smoke (5 locales × 4 product types) | Consumer surface blocked on real assets | `PEARL-PRIME-STOREFRONT-V1-01`; `PROGRAM_STATE.md` Storefront |
| **Backlog** | Proposed programs: music v2, sangha, song-kit, teacher-manga-video, agent-system-v2 | Spec-only until operator Q-gates close | `ACTIVE_PROJECTS.tsv` status=proposed |

**Research conclusions baked into plans:**

- **Bestseller research (2026-06-11):** Arc metadata exists; **assembler selection** is the gap — fixes belong in pipeline/quality, not listing expansion.  
- **Anti-spam research:** Platform risk is **velocity + similarity at publish**, not pre-ship YAML count — supports localization model but **does not** prioritize skeleton batches over first EPUB wave.  
- **Go-live audit (2026-05-08):** Surface 1 (catalog) was RED; operator ratified P0 = catalog + active brands + marketing SSOT — but Jun 29 handoff reframes **within-catalog** priority as flip→assemble→EPUB.

---

## 2. ACTUAL-ACTIVITY LEDGER

Substantive merges (2026-06-20 → 2026-06-30), excluding skeleton batch noise:

| Activity | Evidence | Aligns with plan? |
|----------|----------|-------------------|
| en_US arc gap closed (178 arcs + 5 motifs) | PR **#3009** `451f91bca0` · OPD-20260629-001 | ✅ Buildability prerequisite |
| Pearl Prime quality 34%→83% (F4/F6/F2.D) | PRs **#3043, #3055, #3060, #3067, #3077** · OPD-20260629-002 | ✅ Pre-assembly quality bar |
| CJK translator prose-only fix | PR **#3046** `04f710760c` | ✅ CJK lane |
| CJK atomic land + 308 atoms | PR **#3091** `6633530a6c` | ✅ CJK lane |
| Flip campaign + hu_HU topic-fit | PR **#3088** `105b59ddab` · OPD-20260627-001 | ✅ Lane A spine |
| Manga queue-unblock (stage-only) | PR **#3071** `53f36e8a81` · OPD-20260629-003 | ✅ Staged correctly post-CJK |
| GPU priority OPD logged | PR **#3070** | ✅ Steering |
| Cloud EPUB assembly campaign infra | PR **#2306** `9a7a0bd942` (Jun window) | ✅ Assembly path |
| First Waystream EPUB | PR **#1923** `4e6320b19c` (prior) | ✅ Proof point — still **1 catalog EPUB** |
| GHL EPUB attach | PR **#1947** `89a11d5387` | ⚠️ Merged; `PROGRAM_STATE.md` (2026-06-25) still says not attached — **SSOT lag** |
| Content gaps (mindfulness/adhd/self_worth) | PR **#3123** OPEN (awaiting Jul 1) | ✅ Quality/content frontier |
| Lean-CI path filter | PR **#3166** OPEN (do-not-merge until Jul 1) | ✅ Unblocks flip without $200/day burn |
| Arc-gen pilot (educators) | PR **#3199** OPEN (references OPD-004 not yet in OPD log) | ✅ Lever A — in flight |
| Plan-scale QA pilot | PR **#3605** OPEN + `artifacts/qa/plan_scale_qa_pilot_20260630/` | ⚠️ QA evidence — aligned if pre-assembly |

**Volume activity (dominant):**

| Activity | Evidence | Note |
|----------|----------|------|
| Western skeleton PR fan-out | **694 open PRs**; sample of 500 → **493 skeleton PRs** (es_US 151, it_IT 105, pt_BR 104, hu_HU 98, de_DE 34) | Listing metadata only |
| Recent merges Jun 27–28 | #3072–#3103+ mostly `feat(catalog): *_skeletons batch *` | Triggered **$0 Actions budget hard-stop** (session handoff §0, §8) |
| Flip pilot (warrior_calm) | PRs #3197–#3227 OPEN; pilot **queued, zero fanout fired** | **Blocked** by CI budget, not by plan rejection |
| fr_FR / de_DE / es_ES skeleton history | Dozens of merges in `git log` since Jun 15 | Pre-dates Jun 27 stall but same pattern |

**Project registry motion:**

- **Active:** 9 projects (`ACTIVE_PROJECTS.tsv`)  
- **Proposed (no execution):** 5 — `proj_teacher_manga_30s_video_v1`, `PRJ-MUSIC-MODE-FREEBIE-FUNNEL-V1`, `PRJ-MUSIC-MODE-V2-PRODUCTION-LAUNCH`, `PRJ-SANGHA-KARMA-YOGA-V1`, `PRJ-MUSIC-ONBOARDING-SONG-KIT-V1`  
- **Phase-1-complete / wired / completed:** music brand integration, dual-path image render, CI baseline recovery  

---

## 3. DRIFT MATRIX

| Lane | Planned intent (+ source) | Actual activity (+ evidence) | Verdict | Severity | Note |
|------|---------------------------|-------------------------------|---------|----------|------|
| **Listings → real EPUBs** | P0: flip → assemble → R2 EPUBs; **1 EPUB** today is proof not scale (`PROGRAM_STATE.md` Production-Gate; handoff §2) | Flip infra **merged** (#3088); pilot **stalled** (CI budget); assembly campaign exists (#2306) but **no mass EPUB output**; 694 open PRs mostly skeletons | **DRIFTING** | **HIGH** | Right infrastructure, wrong bandwidth allocation — skeleton volume blocked the pilot |
| **Lever A arc-gen / buildability** | Engine-keyed STORY pools for educators/nyc; binding governance (`PROGRAM_STATE.md` ⚠) | Arc seeding done (+462); 4-cell rebuild still HARD-FAIL; PR **#3199** arc-gen pilot open | **STALLED** | **HIGH** | Planned and partially attempted; thin cells still block scale |
| **Composer / register (OPD-002)** | Code-layer F2/F4/F6 fixes; drop atom mass-reformat | **Complete** on main (#3043–#3067); 24/29 matrix; #3123 content gaps staged | **ON-POINT** | — | Strongest alignment in the audit window |
| **CJK translation + GPU** | CJK owns GPU first; queue not direct Ollama (OPD-003) | #3046/#3091 merged; GPU wave running per handoff; #3127/#3147 staged | **ON-POINT** | — | Operator re-prioritization **consistent** with forensic audit |
| **Manga** | Titled + pilot; renders post-CJK; ~6,200 curated units | 1,345 series plans; 295 panels (0.13%); #3071 merged stage-only; deploy held | **STALLED** (planned deferral) | **MED** | Stall is **intentional** post-OPD-003, but render frontier unchanged for months |
| **Western localization** | Localize don't regenerate; fr 40/40, es 38/40, etc.; flip makes buildable (OPD-001, handoff §6) | Mass skeleton PR fan-out (493+ open); Jun 27–28 merge storm → CI exhaustion | **DRIFTING** | **HIGH** | Model-aligned but **priority-inverted** vs EPUB spine; burned CI budget |
| **Storefront / EPUB attach** | GHL auto-promotes on attach; storefront Phase A needs real assets | #1947 attach merged; SSOT still says unattached; Pearl Prime Storefront **active** but pre-launch | **STALLED** | **MED** | Attach may have landed; consumer storefront still blocked on asset depth |
| **Proposed programs backlog** | Execute after core spine (implicit in cap registry + session handoff) | 5 proposed projects accumulating Q-gates; music v2 deck/spec Jun 11; sangha Jun 9; **zero merges** on these lanes | **STALLED** (good) / **UNPLANNED risk** | **LOW–MED** | Not executing (good) but **spec surface area growing** faster than spine completes |

---

## 4. LEAD HYPOTHESES

### H1: More listings/skeletons while gap is listings → EPUBs

**Evidence:**

- SSOT: **~1,519 listings**, **1 assembled EPUB** (`PROGRAM_STATE.md` glossary + Production-Gate).  
- Open PR sample: **493/500** are `feat(catalog): *_skeletons` across es_US, it_IT, pt_BR, hu_HU, de_DE.  
- Jun 27–28 skeleton merge storm correlates with **Actions $0 budget stop** (handoff §0).  
- Flip pilot (the planned bridge to buildable books) **did not run**; warrior_calm PRs sit open (#3197–#3227).  
- Session handoff Jul 1 sequence puts **#3166 lean-CI → #3123 → flip pilot → assembly** — skeleton fan-out is **not** step 1.

**Verdict: PROVEN (with nuance).**  
Skeleton expansion is **policy-aligned** with OPD-20260627-001 (localize worldwide) but **priority-inverted** relative to the Jun 29 execution spine. Volume ≠ alignment: the lane is busy but drifting from the stated P0 gap (EPUBs).

### H2: Proposed programs proliferating faster than core spine completes

**Evidence:**

- **5 proposed** vs **9 active** projects; proposed entries dated May 8 – Jun 12 (music v2, sangha, song-kit, teacher-manga-video, music freebie funnel).  
- Each carries **8–25 operator Q-gates** unresolved.  
- Core spine: still **1 EPUB** at production scale; flip not executed; Lever A thin cells open.  
- Cap registry: 22+ status-tagged entries in `PEARL_ARCHITECT_STATE.md`; new caps (dwell-beat, song-kit) added Jun 12 while assembly blocked.

**Verdict: PROVEN.**  
Proposals are **not shipping** (no drift via execution) but **accumulating faster** than Production-Gate reaches "done." Spec debt is real drift risk.

### H3: Recent OPDs vs research-stated bottleneck

**Evidence:**

- Research (`OUR_SYSTEM_VS_PATTERNS_GAP.md`): bottleneck = **assembler/quality**, not catalog rows.  
- OPD-20260629-002: fixed composer/register → **83% QA pass** — **matches research**.  
- OPD-20260629-003: GPU→CJK — **matches** CJK forensic audit (translation broken, not manga throughput).  
- OPD-20260627-001: worldwide localize — **matches** anti-spam research.  
- **Mismatch:** skeleton fan-out execution **before** flip/assembly contradicts research lever (ship quality EPUBs first) and Jun 29 handoff ordering — not the OPD text itself, but **dispatch practice**.

**Verdict: PARTIAL.**  
Steering decisions are research-consistent; **execution mix** (493 skeleton PRs vs 0 flip pilot runs) is not.

---

## 5. NET VERDICT

**We are DRIFTING on the highest-priority spine** (listings → real EPUBs), while **staying on-point** on pre-assembly quality (OPD-002) and CJK recovery (OPD-003). The drift is not random busyness: it is a **priority inversion** where Western skeleton catalog expansion consumed GitHub Actions budget and blocked the flip→assemble lane that the Jun 29 handoff explicitly placed first on Jul 1.

### Top 3 highest-severity drift items

1. **Skeleton fan-out blocked the EPUB spine (HIGH).**  
   - *Evidence:* 694 open PRs (~71% skeletons); CI budget hard-stop; warrior_calm flip pilot queued with zero fanout.  
   - *Plan source:* `PROGRAM_STATE.md` Production-Gate ("next = engine-keyed pools + assembly"); session handoff §2 + §12 Jul 1 sequence.

2. **Listing volume mistaken for progress (HIGH).**  
   - *Evidence:* Recent merge log dominated by `*_skeletons batch *`; still **1 catalog EPUB** at scale.  
   - *Plan source:* `PROGRAM_STATE.md` glossary (listing ≠ EPUB); research `OUR_SYSTEM_VS_PATTERNS_GAP.md` §0.

3. **Lever A thin-persona buildability still open while catalog expands (HIGH).**  
   - *Evidence:* educators/nyc cells HARD-FAIL tuple-viability; #3199 pilot open; +462 arcs not spine-buildable.  
   - *Plan source:* `PROGRAM_STATE.md` ⚠ thin-persona caveat; handoff §2.

---

## 6. REALIGNMENT RECOMMENDATIONS (ranked, no execution)

| Rank | Action | Rationale |
|------|--------|-----------|
| 1 | **Merge #3166 first on Jul 1**, then run warrior_calm flip pilot before any new skeleton merges | Restores planned Lane A; stops ~83% CI burn (handoff §8) |
| 2 | **Freeze Western skeleton fan-out** until flip pilot clean + first assembly batch to R2 | Prevents repeat of Jun 27–28 budget exhaustion |
| 3 | **Execute Jul 1 staged spine PRs** (#3123, #3127, #3147) before resuming locale catalog batches | Content/CJK fixes directly raise assembly pass rate |
| 4 | **Complete Lever A** (#3199 arc-gen pilot → engine-keyed pools) before educators/nyc flip waves | SSOT explicit blocker for +462 cells |
| 5 | **Truth-up `PROGRAM_STATE.md`** for EPUB attach (#1947) and post-OPD-002 quality status | SSOT lag erodes audit trust |
| 6 | **Hold proposed programs** (music v2, sangha, song-kit, teacher-video) — no new cap entries until flip pilot passes | Reduces spec debt (H2) |
| 7 | **Deploy manga queue-unblock post-CJK** per OPD-003 — do not pull GPU forward | Already ratified; avoid re-opening |
| 8 | **Re-run 29-cell QA matrix** post-merge (handoff §12 step 8) before dispatching more remediation prompts | Confirms whether QA/lanes you are authoring are still the binding frontier |

### Operator-tier questions

**Q-DRIFT-01 — Skeleton freeze scope** — **RESOLVED 2026-06-30 (OPD-20260630-001): HARD FREEZE**
- **Choice:** (A) Full freeze on `feat(catalog): *_skeletons` until first R2 assembly batch, vs (B) Allow skeleton merges at ≤N/week with lean-CI only.  
- **Impact:** A unblocks flip fastest; B preserves slow Western locale progress.  
- **Recommendation:** **A** for Jul–Aug; resume skeletons split across months per handoff §8.  
- **Why:** CI free tier ≈ 2,000 min/mo; 170 flip PRs alone ≈ 2,380 min without lean-CI.  
- **Ratified default:** **A** — enforced in CI via `config/governance/skeleton_freeze.yaml` + `scripts/ci/pr_governance_review.py`.

**Q-DRIFT-02 — PROGRAM_STATE EPUB attach claim** — **RESOLVED 2026-06-30 (OPD-20260630-002): SSOT WINS, #1947 verifiable**
- **Choice:** (A) `#1947` attach satisfies "attached to GHL feed" SSOT row, vs (B) attach incomplete until storefront consumer path live.  
- **Recommendation:** **A** for GHL row; keep storefront row **stalled** until Phase A smoke.  
- **Why:** `#1947` merged `89a11d5387`; SSOT verified 2026-06-25 predates it.  
- **Ratified default:** **A** — `docs/PROGRAM_STATE.md` GHL + Storefront rows reconciled (GHL attach done; storefront Phase A still blocked).

**Q-DRIFT-03 — Plan-scale QA pilot (#3605) dispatch** — **RESOLVED 2026-06-30 (OPD-20260630-003): FINISH SWEEP, HOLD QA**
- **Choice:** (A) Run now as pre-assembly evidence, vs (B) Defer until post-flip-pilot stable checkout.  
- **Recommendation:** **B** — pilot harness is on-plan but secondary to flip/assembly; running during CI stall adds churn without merge path.  
- **Why:** Aligns remediation spend with H1 finding.  
- **Ratified default:** **B** — let running 1000-plan sweep complete; no new QA scaffolding until post-flip stable tree (#3605 merge-on-green only).

---

## 7. CLOSEOUT_RECEIPT

| Field | Value |
|-------|-------|
| **AGENT/TASK/STATUS** | Pearl_PM + Pearl_Architect / Plan-vs-Practice Drift Audit / **COMPLETE (read-only)** |
| **NET VERDICT** | **DRIFTING** on EPUB spine + localization volume; **ON-POINT** on quality lane + CJK steering |
| **Top drift** | (1) skeleton fan-out blocked flip pilot (2) listing volume ≠ EPUB progress (3) Lever A still open |
| **H1** | **PROVEN** (priority inversion) |
| **H2** | **PROVEN** (spec accumulation > spine completion) |
| **H3** | **PARTIAL** (OPDs match research; dispatch mix does not) |
| **Matrix summary** | 2 ON-POINT · 2 DRIFTING · 3 STALLED · 0 UNPLANNED execution |
| **Q-DRIFT** | Q-DRIFT-01/02/03 **RESOLVED 2026-06-30** (OPD-20260630-001/002/003) |
| **Evidence dir** | `artifacts/audit/drift_audit_20260630/` |
| **Commit** | None (read-only audit) |
