# Pearl Prime Storefront V1 — Phase A coordination tracker

**Cap entry:** `PEARL-PRIME-STOREFRONT-V1-01` + `PEARL-PRIME-STOREFRONT-V1-01-AMENDMENT-2026-06-04` (`docs/PEARL_ARCHITECT_STATE.md`)
**Project ID:** `PRJ-PEARL-PRIME-STOREFRONT-V1` (`artifacts/coordination/ACTIVE_PROJECTS.tsv` — status `active`)
**Subsystem:** `storefront` (`artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv` — status `active`)
**Owner:** Pearl_PM
**Specification:** `docs/specs/PEARL_PRIME_STOREFRONT_V1_SPEC.md` (+ §AMENDMENT-2026-06-04)
**Parent PRs (merged on `origin/main`):**
- PR [#1433](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1433) — spec + cap entry + 5 coordination rows (SHA `69e9855f72471603f320f1b96ae72e899a3e8778`)
- PR [#1446](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1446) — AMENDMENT-2026-06-04 with 16 Q-PRP-* operator answers (SHA `eb9c4ab841e49f0fa5e72b4497505f1325837c7d`)

**Iteration 1:** 2026-06-06 (Phase A entry — initial tracker authoring)
**Cadence:** weekly minimum while ws's are active; daily once entering pre-launch QA (per spec §16 + Pearl_PM coordination deliverable #1)

---

## §1 — Workstream status table (5 ws's)

5-ws set per AMENDMENT-2026-06-04 §3:

| # | workstream_id | status | owner | scope summary | parallel batch |
|---|---|---|---|---|---|
| 1 | `ws_pearl_prime_storefront_v1_framework_research_20260603` | **completed** | Pearl_Architect | Web-research matrix (PRIMARY = Snipcart free tier per AMENDMENT §2.1). Evidence merged in spec §3 + §22 + AMENDMENT §2.1. | meta-track (closed) |
| 2 | `ws_pearl_prime_storefront_v1_ui_mockups_20260603` | **runnable** (in-flight 2026-06-06) | Pearl_Dev | 12 HTML mockups under `brand-wizard-app/public/storefront_mockups/`, en-US + ja-JP variants, hybrid Buy-Now + cart UX, guest-checkout flow, Snipcart drop-in surfaces mocked. | A — parallel with #3 |
| 3 | `ws_pearl_prime_storefront_v1_cloudflare_wiring_20260603` | **runnable** (in-flight 2026-06-06) | Pearl_Int | CF Pages + Workers + D1 + R2 + KV under account `b80152c319f941e6e92f928e2617a3d5` + Snipcart account + webhook routes; deploy workflow `.github/workflows/pearl-prime-storefront-deploy.yml`. Lands `config/storefront/sku_url_map.yaml` generator (gates ws #5). | A — parallel with #2 |
| 4 | `ws_pearl_writer_next_step_atom_audit_20260603` | **runnable** (in-flight 2026-06-06) | Pearl_Writer | Stage 1 audit (en-US `anxiety` + `overthinking` × all personas) — coverage report only (not rewrite). Authors `scripts/ci/check_atoms_external_book_references.py` per spec §15.3 + outputs `artifacts/qa/next_step_atom_audit_<date>.tsv` + summary. Phase A scope ratchet (ja-JP atoms) lands in Stage 2 follow-up ws. | B — parallel with #5 |
| 5 | `ws_freebie_cta_redirect_unification_20260603` | **runnable** (in-flight 2026-06-06) | Pearl_Marketing + Pearl_Dev | HARD CTA cutover across 7 surfaces × {en-US, ja-JP} per AMENDMENT §2.3. Authors `scripts/ci/check_external_buy_links.py` CI guard. `config/funnel/store_url_tracker.yaml` DELETED on launch day; `config/storefront/sku_url_map.yaml` becomes sole SKU URL registry. | B — parallel with #4 |

**Sibling agent worktrees (per operator session 2026-06-06):**

| # | Worktree | Branch |
|---|---|---|
| 2 | `/private/tmp/wt-pp-mockups-20260606` | `agent/pearl-dev-storefront-v1-ui-mockups-20260606` |
| 3 | `/private/tmp/wt-pp-int-cf-snipcart-20260606` | `agent/pearl-int-storefront-v1-cf-snipcart-wiring-20260606` |
| 4 | `/private/tmp/wt-pp-writer-audit-20260606` | `agent/pearl-writer-storefront-v1-atom-audit-stage1-20260606` |
| 5 | `/private/tmp/wt-pp-marketing-cta-20260606` | `agent/pearl-marketing-storefront-v1-cta-hard-cutover-20260606` |

Tracker iteration owner worktree: `/private/tmp/wt-pp-pm-coord-20260606` on branch `agent/pearl-pm-storefront-v1-phase-a-coordination-20260606`.

---

## §2 — Sequencing diagram (Phase A)

Text-based DAG of merge dependencies. `==>` is hard merge-gate; `~~>` is soft dependency (preferred sequencing only). All four runnable ws's start parallel; the operator-review + CI gates serialize them at the launch line.

```
                 META-TRACK (already closed on main)
                 |
  framework_research (#1) — COMPLETED via spec §3 + §22 + AMENDMENT §2.1
                 |
                 v
   +-------------+----------------+-----------------+---------------------+
   |                              |                 |                     |
   | BATCH A (infra + UX)         |                 | BATCH B (content + CTA cutover)
   |                              |                 |                     |
   v                              v                 v                     v
 mockups (#2)              cf+snipcart (#3)   atom audit (#4)        cta cutover (#5)
 [Pearl_Dev]               [Pearl_Int]        [Pearl_Writer]         [Pearl_Marketing+Pearl_Dev]
   |                              |                 |                     |
   |                              |  lands          |                     |  reads
   |                              |  config/storefront/sku_url_map.yaml   |  config/storefront/sku_url_map.yaml
   |                              +======= GATES ===========================+
   |                              |                                       |
   |  operator-review APPROVED    |                                       |
   |  gates frontend-code ws      |                                       |
   |  (next phase — out of A's 5) |                                       |
   |                              v                                       v
   |                       infra ALIVE on               CI guard          CI gate
   |                       pearl-prime-storefront       check_atoms_*     check_external_*
   |                       .pages.dev                   GREEN             GREEN
   |                              |                       |                  |
   v                              v                       v                  v
   +========== CONVERGENCE: Phase A launch-readiness gate ===========+
                                  |
                                  v
                 +--- pre-launch CI gates (5; see §4) ---+
                                  |
                                  v
                 +--- 6 smoke combinations (see §3) ----+
                                  |
                                  v
                          Phase A LAUNCH milestone
                                  |
                                  v
                          Phase B kickoff coord entry
                          (+ zh-TW + zh-CN + music + bundles)
```

**Notes on sequencing:**

- **Batch A (mockups + CF/Snipcart wiring) runs strictly parallel.** Pearl_Dev's mockup operator-approval gates Pearl_Dev's FRONTEND CODE lane (a separate, future ws — NOT in this Phase A 5-ws set per spec §16 phase-table revision + AMENDMENT §3). The mockup PR landing does not gate Pearl_Int's infra PR landing.
- **Batch B (atom audit + CTA cutover) runs parallel but ws #5 (CTA cutover) has a soft dependency on ws #3's `sku_url_map.yaml` generator** for the per-CTA replacement loop. Per the AMENDMENT §3 statement of departure: "ws_pearl_int_cloudflare_wiring landing canonical sku_url_map.yaml is prerequisite for this ws's per-CTA replacement". Sequencing recommendation: ws #5 begins sweep authoring + CI guard scaffold in parallel; per-CTA URL replacement loop blocks until ws #3 PR merges.
- **Atom audit ws #4 has no hard dependency on any other ws.** It can complete and merge independently. Its output (audit coverage report) gates a SEPARATE downstream ws (`ws_pearl_writer_next_step_atom_rewrite_<future-date>`) that is NOT in the Phase A 5-ws set.
- **Operator review is required after each ws's PR is opened.** No ws merges into `main` without operator sign-off per `feedback_validation_before_scaling` memory + AMENDMENT §3 implementation-ownership notes.

---

## §3 — 6 smoke-combo readiness matrix (HARD launch gate)

Per spec §AMENDMENT-2026-06-04.2.4 (Q-PRP-ROLLOUT-01 Full Phase 1+2 at launch): Phase A launch requires **6 smoke combinations green** before milestone declared.

| Combo | Locale | Product type | Smoke definition (per router prompt §"PHASE A LAUNCH GATE") | Status (Iter 1 @ 2026-06-06) |
|---|---|---|---|---|
| 1 | **en-US** | book | ≥1 real purchase + ≥1 real review + ≥1 successful download | not-started |
| 2 | **en-US** | audiobook | ≥1 real purchase + ≥1 real review + ≥1 stream-play + ≥1 MP3 download | not-started |
| 3 | **en-US** | manga | ≥1 real purchase + ≥1 real review + ≥1 WEBTOON read + ≥1 PDF download | not-started |
| 4 | **ja-JP** | book | ≥1 real purchase + ≥1 real review + ≥1 successful download (JPY currency) | not-started |
| 5 | **ja-JP** | audiobook | ≥1 real purchase + ≥1 real review + ≥1 stream-play + ≥1 MP3 download (ja-JP narrator voice) | not-started |
| 6 | **ja-JP** | manga | ≥1 real purchase + ≥1 real review + ≥1 WEBTOON read + ≥1 PDF download (ja-JP locale) | not-started |

**Status legend:** `not-started` → `in-progress` (some prerequisites met) → `pre-launch-ready` (all prerequisites met; awaiting e2e smoke execution) → `smoked-green` (smoke executed and passed; combo cleared for launch).

**Demotion clause (operator-decision-gated per AMENDMENT §2.4):** If ja-JP smoke combos 4-6 fail close to launch, Phase A demotes to en-US-only Phase A (combos 1-3 only); ja-JP slips to Phase A.1. **NOT auto-fallback** — operator must explicitly invoke. Log to `artifacts/coordination/operator_decisions_log.tsv` when invoked. This decision is in Pearl_Operator_Proxy's envelope per `docs/PEARL_OPERATOR_PROXY_SPEC.md`.

**Per-combo prerequisites (rolled up):**

| Combo | Needs (rolled up from the 4 runnable ws's) |
|---|---|
| 1 (en-US book) | ws#2 mockup approved → frontend code ws → ws#3 CF infra alive → ws#5 CTA cutover en-US complete → en-US book SKUs ingested → ≥1 EPUB in R2 → Snipcart test buy → review form submission → signed-URL download verification |
| 2 (en-US audiobook) | combo #1 prerequisites + audiobook M4B/MP3 in R2 + in-browser HLS streaming player working (per spec §12.1) + signed-URL MP3 download |
| 3 (en-US manga) | combo #1 prerequisites + manga page tiles + PDF in R2 + WEBTOON in-browser reader working (per spec §13.4) + signed-URL PDF download |
| 4 (ja-JP book) | combo #1 prerequisites + ja-JP locale routing + ja-JP catalog projection + JPY currency display + ja-JP body font chain (DM Sans → Noto Sans JP) + Snipcart JPY support |
| 5 (ja-JP audiobook) | combo #2 + combo #4 prerequisites + ja-JP narrator infra (already operational per `ws_voice_pipeline_activation_20260409`; storefront consumes) |
| 6 (ja-JP manga) | combo #3 + combo #4 prerequisites + ja-JP manga assets (already operational per Manga V2; storefront consumes) |

---

## §4 — Pre-launch CI gate matrix (5 gates — must all be GREEN)

Per router prompt §"Pre-launch CI gates" + spec §AMENDMENT-2026-06-04 §3:

| # | Gate | Owning ws | Definition | Status (Iter 1) |
|---|---|---|---|---|
| 1 | `scripts/ci/check_external_buy_links.py` | ws #5 (CTA cutover) | Zero violations across all 7 surface categories in both locales (Q-PRP-CTA-UNIFY-01 HARD cutover). Surfaces: `funnel/`, marketing surfaces, `brand-wizard-app/public/free/`, `somatic_exercise_freebee_apps/`, email YAMLs, social-CTA registries, ja-JP equivalents. | **PENDING** (script not yet authored) |
| 2 | `scripts/ci/check_atoms_external_book_references.py` | ws #4 (atom audit) | Atom rewrites complete for en-US + ja-JP `anxiety` + `overthinking` (Phase A audit + rewrite cycle). Note: ws #4 is AUDIT only; the rewrite ws is gated on operator approval of Q-PRP-WRITER-AUDIT-01 scope (start narrow vs full sweep). | **PENDING** (script not yet authored) |
| 3 | `.github/workflows/pearl-prime-storefront-deploy.yml` | ws #3 (CF wiring) | Deploys cleanly to `pearl-prime-storefront.pages.dev`. wrangler-action@v3 with CLOUDFLARE_API_TOKEN + CLOUDFLARE_ACCOUNT_ID repo secrets under account `b80152c319f941e6e92f928e2617a3d5`. | **PENDING** (workflow not yet authored) |
| 4 | Snipcart account live + webhook secret rotated within 90 days | ws #3 (CF wiring) | `SNIPCART_WEBHOOK_SECRET` provisioned in CF Workers env. Webhook route `/api/webhook/snipcart` operational. Per-tx settlement to Stripe verified. | **PENDING** (Snipcart account not yet provisioned) |
| 5 | D1 schemas applied; reviews + orders + library tables operational | ws #3 (CF wiring) | D1 migrations applied per spec §7.2 (sku), §10.3 (order, order_item — Snipcart-mirror), §11.2 (review). en-US + ja-JP locale partitions seeded. | **PENDING** (migrations not yet authored) |

**Additional gate (router prompt):**

- R2 bucket populated with cover assets + sample previews + paid asset files for ≥6 SKUs (one per combo). Tracked under ws #3 + downstream content-ingest ws.

**Gate-clearance rule:** Phase A launch milestone may NOT be declared unless gates 1-5 are GREEN AND 6 smoke combinations (§3) reach `smoked-green` AND operator declares launch.

---

## §5 — Per-ws gate table (what each ws's PR landing unblocks)

| ws # | When PR merges, this clears the way for: |
|---|---|
| 1 (framework_research) | Already cleared via merged parent PRs #1433 + #1446. No further action. |
| 2 (mockups) | Operator review of mockups gates Pearl_Dev's **frontend code lane** (a SEPARATE, future ws — NOT in Phase A's 5-ws set per spec §16 phase-table revision). Mockup PR landing does not block ws #3, #4, or #5. |
| 3 (CF + Snipcart wiring) | (a) Unblocks ws #5's per-CTA URL replacement loop (provides canonical `config/storefront/sku_url_map.yaml`). (b) Clears CI gates 3, 4, 5 in §4. (c) Unblocks Phase A content ingest (catalog projector + R2 asset population). |
| 4 (atom audit Stage 1) | (a) Clears half of CI gate 2 in §4 (audit-coverage half; rewrite cycle clears the other half). (b) Operator review of the audit report gates the SEPARATE Stage 2 rewrite ws + Phase A scope ratchet to ja-JP atoms (per AMENDMENT §3 statement). |
| 5 (CTA cutover) | (a) Clears CI gate 1 in §4. (b) Removes legacy `config/funnel/store_url_tracker.yaml` (DELETED at launch day; successor = `config/storefront/sku_url_map.yaml`). (c) Establishes HARD-cutover end-state across all 7 surfaces × {en-US, ja-JP}. |

---

## §6 — Operator decision log

Canonical operator-decision log: [`artifacts/coordination/operator_decisions_log.tsv`](./operator_decisions_log.tsv) (TSV; append-only).

**Q-PRP-* answers (16 decisions, 4 departures, 1 super-set):** Captured authoritatively in the cap-AMENDMENT itself at `docs/PEARL_ARCHITECT_STATE.md` §`PEARL-PRIME-STOREFRONT-V1-01 — AMENDMENT — 2026-06-04` and in spec §AMENDMENT-2026-06-04 §1. Not duplicated as OPD-* rows; the AMENDMENT cap entry is the source of truth for the Q-PRP-* decisions.

**Future Phase A decisions** (e.g., ja-JP smoke demotion invocation, atom-rewrite Stage 2 scope ratchet, Snipcart per-locale pricing FX) will be logged as OPD-* rows in `operator_decisions_log.tsv` with citations to this tracker iteration + the relevant cap entry / spec section.

**Pearl_Operator_Proxy in-envelope items** (per `docs/PEARL_OPERATOR_PROXY_SPEC.md`): Pearl_PM may decide and log without escalation for: tracker iteration cadence shifts, sibling-ws sequencing fine-tuning, smoke-combo prerequisites refinement. Out-of-envelope items (e.g., adding a 6th ws to Phase A, demoting smoke combos, mutating SKU pricing) escalate to operator.

---

## §7 — Phase A → Phase B gate conditions

Per spec §AMENDMENT-2026-06-04.2.4 (renamed phases):

- ~~Phase 1~~ → **Phase A (launch)** — en-US + ja-JP × book + audiobook + manga + auto catalog + reviews + Snipcart
- ~~Phase 2~~ → folded into Phase A
- ~~Phase 3~~ → **Phase B** — + zh-TW + zh-CN + music + series bundles + recommender personalization
- ~~Phase 4~~ → **Phase C** — + ko-KR (gated on `distribution_status` clearance per `docs/CJK_CATALOG_PLAN.md`)

**Phase A → Phase B gate** (this tracker iteration anticipates; not yet active):

| Condition | Status |
|---|---|
| All 6 smoke combinations `smoked-green` (or 3 en-US combos `smoked-green` + ja-JP demoted to Phase A.1 per operator decision) | not-started |
| All 5 pre-launch CI gates GREEN | not-started |
| Phase A launch milestone declared by operator | not-started |
| Pearl_PM authors **Phase B kickoff** coordination entry (separate tracker `artifacts/coordination/storefront_v1_phase_b_tracker.md`) | not-started |

When the gate is cleared, Pearl_PM opens Phase B coordination per router prompt §"Phase A → Phase B gate".

---

## §8 — Cadence + iteration plan

**Cadence:** weekly minimum while Phase A ws's are active; daily once entering pre-launch QA (per spec §16 implicit cadence + Pearl_PM coordination deliverable #1).

**Per-iteration deliverables (PR scope):**

- Tracker delta: which ws statuses changed (`runnable → in_progress → completed`); which smoke combos newly ready; which CI gates newly green.
- Blockers surfaced this iteration + operator decisions logged.
- NEXT_ACTION: which ws agent is on the critical path next.

**Anti-bundling:** Per spec §"GOLDEN BRANCH + PR" guidance — each tracker update is a small PR; do NOT bundle weeks of changes into one mega-PR. PR title pattern: `coord(storefront): Phase A tracker update — <date>`.

**Status-flip protocol per spec coordination deliverable #4:**

- Flip ws status `runnable → in_progress` when ws agent commits the STARTUP_RECEIPT.
- Flip ws status `in_progress → completed` when the agent's CLOSEOUT_RECEIPT shows the merge SHA.
- Update `evidence_paths` in `ACTIVE_WORKSTREAMS.tsv` with the merge SHA + PR URL.
- Update `last_updated` to the current date.

These TSV-row mutations happen in **subsequent** tracker iterations (not this initial-authoring iteration) — the 5 runnable rows already reflect AMENDMENT-2026-06-04 status and operator strongly prefers no concurrent TSV writes while sibling ws agents are in flight.

---

## §9 — Iteration 1 (2026-06-06) — initial authoring scope

**This iteration:**

- Authors initial Phase A tracker (this file).
- Anticipates 4 sibling-agent PRs landing in operator-review queue from concurrent sessions (mockups, CF wiring, atom audit stage 1, CTA cutover).
- Does **not** mutate `ACTIVE_WORKSTREAMS.tsv` or `SUBSYSTEM_AUTHORITY_MAP.tsv` (already in post-AMENDMENT state per operator session 2026-06-04).
- Does **not** mutate `ACTIVE_PROJECTS.tsv` `current_truth_paths` field this iteration — sibling-session concurrent-write risk per operator guidance; deferred to iteration 2 once sibling PRs land.
- Does **not** log Q-PRP-* answers as OPD-* rows — they are canonical in the AMENDMENT cap entry; future Phase A operator decisions will be OPD-logged.

**Sibling-PR collision check (2026-06-06):** `gh pr list --search "Phase A tracker" --state all` → no existing tracker PR. Safe to proceed.

**NEXT_ACTION (carried into the PR closeout):** Pearl_Int's CF + Snipcart wiring ws (#3) is on the critical path next — it gates ws #5's per-CTA replacement loop (provides `config/storefront/sku_url_map.yaml`) AND clears CI gates 3, 4, 5 (three of five pre-launch gates). Pearl_Dev's mockup ws (#2) runs parallel but only gates a future ws (frontend code lane) outside the Phase A 5-ws set; it does not block any other Phase A ws. Pearl_Writer's atom audit ws (#4) is fully independent. Pearl_Marketing's CTA cutover ws (#5) is soft-blocked on ws #3 for the per-CTA replacement loop but can begin sweep authoring + CI guard scaffold in parallel.
