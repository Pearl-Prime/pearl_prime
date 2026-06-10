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
**Iteration 2:** 2026-06-09 (7-PR merge cascade landed on `origin/main` + AMENDMENT-2026-06-04.2 ratified via seed + 16 OPDs logged)
**Cadence:** weekly minimum while ws's are active; daily once entering pre-launch QA (per spec §16 + Pearl_PM coordination deliverable #1) — **ITER 2 RAMP: cadence cuts over weekly → DAILY** until Phase 3a Wave 1 (corp_mgrs × anxiety persona-keyed atom backfill) lands per OPD-20260606-003 (b).

---

# ITER 2 — 2026-06-09 — 7-PR merge cascade + AMENDMENT-2026-06-04.2 ratified via seed + 16 OPDs logged

> **Read order:** iter 2 sections §A-§L below SUPERSEDE iter 1 sections §1 (workstream table), §3 (smoke matrix), §4 (CI gate matrix), §5 (per-ws gate table), §9 (NEXT_ACTION). Iter 1 sections preserved verbatim below the iter 2 block as audit trail; §2 sequencing diagram + §6 operator decision log pointer + §7 Phase A→B gate + §8 cadence remain in force from iter 1 unmodified.

## §A — Iter 2 banner + cadence change

**State of `origin/main` at iter 2 fire (2026-06-09 23:00 UTC):**

- 7 of 8 Phase-A program PRs (including 2 cross-program cap-entry PRs) MERGED.
- All 16 operator decisions (`OPD-20260606-001` through `OPD-20260606-016`) LOGGED in `artifacts/coordination/operator_decisions_log.tsv` (PR #1480, SHA `11843f9f8`).
- Iter-2 seed `artifacts/coordination/storefront_v1_phase_a_tracker_iter_2_seed.md` PRE-STAGED on main (PR #1480 same commit). This iter-2 doc consumes the seed verbatim into §J + §K + §L below.
- 6 child-ws dispatch prompts pre-staged at `artifacts/coordination/pearl_prime_one_path_child_ws_dispatch_prompts.md` (PR #1480 same commit) — READY-TO-FIRE for Phase 1 mechanical + Phase 2 runtime + Phase 3a persona backfill + Phase 3b signature_phrases + Phase 4 craft gates + Pearl_PM sequencing meta-ws.
- ONE-PATH lockdown V1 spec live at `docs/specs/PEARL_PRIME_ONE_PATH_LOCKDOWN_V1_SPEC.md` (PR #1479, SHA `febd1fb95`) — 18-dimension canonical path + runtime fail-fast enforcement contract + 18-row hard-deletion manifest.
- Pearl_Architect cap entry `PEARL-PRIME-ONE-PATH-V1-01` appended to `docs/PEARL_ARCHITECT_STATE.md` (PR #1479 same commit) — operator-answered defaults make the cap-entry de-facto ACTIVE pending a separate status-flip PR (out of this iter's scope).

**Cadence flip (rationale):** with the 7-PR cascade landed, Phase A enters pre-launch QA window (per iter-1 §8 trigger condition). Cadence cuts from weekly minimum to **DAILY tracker iteration** until Phase 3a Wave 1 (corp_mgrs × anxiety persona-keyed atom backfill) lands and the first Q-PRP-STOREFRONT-CONTENT-GATE-01 SKU-join check fires automatically. Daily cadence reverts to weekly once first persona×topic combo crosses the §J.1 mechanical contract.

**This iter's PM scope:** tracker-only single-file update (this file). NO child-ws spawns this iter (Phase 1 mechanical + Phase 3a Wave 1 + ja-JP freebie + Stage 2a localized audit are being dispatched in parallel sibling sessions per the child-ws dispatch prompts on disk). NO TSV row mutations (ACTIVE_WORKSTREAMS / SUBSYSTEM_AUTHORITY_MAP / ACTIVE_PROJECTS) this iter — deferred to iter 3 once sibling dispatches commit their STARTUP_RECEIPTs. NO Q-PRP-* or Q-OP-* operator-decision authorship this iter — all 16 answered in the OPD log already.

---

## §B — AMENDMENT-2026-06-04.2 surfacings (S1 / S2 / S3 ratified via seed)

The AMENDMENT-2026-06-04.2 parallel-dispatch surfacings (originally 3 open items in PR #1455's spec amendment) are now resolved via the iter-2 seed cross-link. Verbatim seed text on disk: [`artifacts/coordination/storefront_v1_phase_a_tracker_iter_2_seed.md`](./storefront_v1_phase_a_tracker_iter_2_seed.md) §J + §K + §L.

| Surfacing | Disposition | Source |
|---|---|---|
| **S1 — Pearl_Writer atom-audit cascade revision** (Stage 1 en-US `anxiety` + `overthinking` coverage report is insufficient; needs Stage 2a localized-first to support Q-PRP-STOREFRONT-CONTENT-GATE-01 mechanical contract in ja-JP + zh-TW launch scope) | **RESOLVED → (a) Stage 2a localized-first ws spawned.** New ws `ws_pearl_writer_next_step_atom_audit_stage_2a_localized_20260606` dispatched parallel to this PM iter per OPD-20260606-003 persona-staging logic + Pearl_Architect's 9-file evidence in PR #1455 §B. | PR #1455 §B (S1); iter-2 seed §K row "Pearl_Writer spawns Stage 2a localized"; OPD-20260606-003 |
| **S2 — ja-JP freebie launch-blocker** (15 ja-JP freebie pages absent under `brand-wizard-app/public/free/` ja-JP mirror; Pearl_Marketing's en-US HARD-cutover PR #1453 doesn't author the ja-JP funnel; without ja-JP freebies, the storefront cannot accept ja-JP smoke combos 4-6) | **RESOLVED → (a) new ws spawned.** `ws_pearl_marketing_ja_jp_freebie_pages_authoring_20260606` dispatched parallel to this PM iter per OPD-20260606-015 launch-gate clause (ja-JP freebie pages are a hard launch-readiness criterion per §L below). | PR #1455 §B (S2); iter-2 seed §K row "Pearl_Marketing spawns ja-JP freebies"; OPD-20260606-015 |
| **S3 — `sku_url_map.yaml` ratification** (PR #1453 hand-curated `config/storefront/sku_url_map.yaml` is 17,688 rows under the OLD top-5-locale × all-personas assumption; OPD-20260606-004 (b) demotes to top-3 locales + OPD-20260606-015 SCOPE-GATED launch demotes to 1 persona × 1 topic at launch; the 17,688 hand-curated rows are retained as the catalog UPPER BOUND, with the live live-catalog subset gated mechanically by Q-PRP-STOREFRONT-CONTENT-GATE-01 per persona×topic) | **RESOLVED → (a) projector matches hand-curated schema; mechanical Q-PRP-STOREFRONT-CONTENT-GATE-01 contract is the live-vs-bounded subset gate.** No PR #1453 revert; the 17,688-row YAML stands as the upper bound. Pearl_PM automation appends live SKU rows mechanically per §J.1. | PR #1455 §B (S3); iter-2 seed §J.1 mechanical contract + §J.2 launch scope; OPD-20260606-015 + OPD-20260606-016 |

---

## §C — 6-PR merge cascade → 7 of 8 MERGED (UPDATE)

Iter-1 §C from the dispatch-prompt (originally "6 open PRs in operator-review queue") is REPLACED. Live `origin/main` state as of 2026-06-09 23:00 UTC:

| # | PR | Title (truncated) | Owner | Merge SHA on main | Status |
|---|---|---|---|---|---|
| 0 | [#1479](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1479) | spec(pearl_prime): ONE-PATH lockdown V1 [v2 clean recovery; replaces closed #1473] | Pearl_Architect | `febd1fb95` | **MERGED** |
| 0' | [#1480](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1480) | coord(pearl_prime+storefront): log 16 OPDs + iter-2 PM tracker seed + 6 child ws dispatch prompts [v2 clean recovery; replaces closed #1478] | Pearl_Architect | `11843f9f8` | **MERGED** |
| 1 | [#1448](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1448) | coord(storefront): Phase A tracker — iter 1 (initial authoring) | Pearl_PM | `da691d6c4` | **MERGED** |
| 2 | [#1454](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1454) | audit(atoms): stage 1 en-US anxiety + overthinking off-catalog reference audit | Pearl_Writer | `db52b0293` | **MERGED** |
| 3 | [#1450](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1450) | infra(storefront): CF Pages + D1 + R2 + KV + Snipcart wiring scaffold | Pearl_Int | `5a481c1e2` | **MERGED** |
| 4 | [#1452](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1452) | feat(storefront-mockups): 12 components × en-US/ja-JP variants | Pearl_Dev | `4c4ac5e0c` | **MERGED** |
| 5 | [#1453](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1453) | feat(storefront): HARD CTA cutover sweep + CI guard (incl. 17,688-row `sku_url_map.yaml`) | Pearl_Marketing | `2aa09807b` | **MERGED** |
| 6 | [#1455](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1455) | spec(storefront-v1): AMENDMENT-2026-06-04.2 | Pearl_Architect | n/a | **OPEN** — merge conflict with #1479/#1480 (cap-entry overlap; operator-side rebase or v2 re-author pending) |

**Cascade observation:** the merge order observed (`#1479 cap-entry` → `#1480 OPDs+seed+prompts` → `#1448 PM iter 1` → `#1454 Writer audit` → `#1450 Int CF` → `#1452 Dev mockups` → `#1453 Marketing CTA`) closely matches the recommended order in iter-1 §C (Q-PRP-MERGE-ORDER-01 = (a)), with the two cap-entry PRs (#1479 + #1480) inserted before the storefront-program cascade per OPD-20260606-001 META acceptance (cap-entries land first to unblock Pearl_PM dispatch). **#1455 status is not blocking iter-2** — the AMENDMENT-2026-06-04.2 substance was pre-ratified through the OPDs (which were authored against the AMENDMENT proposal text), so the surfacings are resolved per §B even with the PR itself unmerged.

**Note on this PR vs sibling PR #1457:** stale sibling PR #1457 (open since 2026-06-06, single file, +391/-0) was authored against the iter-1 + 6-open-PR state with 4 Q-PRP-AMEND-* PENDING. The seed + 16 OPDs supersede its content. THIS iter-2 PR (v2 final-20260609) supersedes #1457; operator may close #1457 at convenience.

---

## §D — Q-PRP-AMEND-* 4-decision matrix → 4 of 4 ANSWERED (UPDATE)

Iter-1 §D from the dispatch-prompt listed 4 Q-PRP-AMEND-* PENDING. All 4 are now ANSWERED via OPDs:

| Q-ID | Iter-1 §D recommended default | Iter-2 resolved answer | Source OPD | Surfacing closure |
|---|---|---|---|---|
| Q-PRP-WRITER-AUDIT-STAGE-02 | (a) Stage 2a localized-first | **(a) Stage 2a localized-first** — Pearl_Writer Stage 2a ws dispatched | OPD-20260606-003 (b) persona-staging extends to localized-atom staging; PR #1455 §B (S1) 9-file evidence | §B / S1 RESOLVED |
| Q-PRP-JA-JP-FREEBIE-GAP-01 | (a) spawn new ws | **(a) spawn new ws** — `ws_pearl_marketing_ja_jp_freebie_pages_authoring_20260606` dispatched | OPD-20260606-015 SCOPE-GATED launch + ja-JP-in-launch-scope clause | §B / S2 RESOLVED |
| Q-PRP-SKU-MAP-PROJECTOR-01 | (a) projector matches hand-curated schema | **(a) projector matches** — mechanical SKU-join contract IS the live-vs-bounded projector | OPD-20260606-016 NEW Q-PRP definition + answer | §B / S3 RESOLVED + §J.1 codified |
| Q-PRP-MERGE-ORDER-01 | (a) #1448 → #1454 → #1450 → #1452 → #1453 | **(a) — observed cascade matches** (with #1479 + #1480 cap-entries inserted ahead per OPD-001 META) | OPD-20260606-001 META + OPD-20260606-011 single-PR-per-ws-atomic | §C cascade complete |

**Newly tracked Q-PRP for iter 2 (cross-program, ratified):** `Q-PRP-STOREFRONT-CONTENT-GATE-01` — see §J.1 below.

---

## §E — Workstream status (iter 2; supersedes iter 1 §1 + §5)

Status reflects post-merge state on `origin/main`. The 5 ws's from iter-1 §1 status-flip per their merged PRs; AMENDMENT-2026-06-04.2 adds 2 new ws's (the ones dispatched parallel to this iter); plus the 6 ONE-PATH child ws's referenced for cross-program coordination.

### E.1 — Storefront-program ws's (the original 5 + 2 new from AMENDMENT.2)

| # | workstream_id | iter-1 status | iter-2 status | Owner | Evidence |
|---|---|---|---|---|---|
| 1 | `ws_pearl_prime_storefront_v1_framework_research_20260603` | completed | completed (unchanged) | Pearl_Architect | spec §3 + §22 + AMENDMENT §2.1 |
| 2 | `ws_pearl_prime_storefront_v1_ui_mockups_20260603` | runnable (in-flight) | **completed** | Pearl_Dev | PR #1452 SHA `4c4ac5e0c` |
| 3 | `ws_pearl_prime_storefront_v1_cloudflare_wiring_20260603` | runnable (in-flight) | **completed** | Pearl_Int | PR #1450 SHA `5a481c1e2` |
| 4 | `ws_pearl_writer_next_step_atom_audit_20260603` | runnable (in-flight) | **completed (Stage 1)** | Pearl_Writer | PR #1454 SHA `db52b0293` |
| 5 | `ws_freebie_cta_redirect_unification_20260603` | runnable (in-flight) | **completed** | Pearl_Marketing + Pearl_Dev | PR #1453 SHA `2aa09807b` |
| 6 (NEW) | `ws_pearl_writer_next_step_atom_audit_stage_2a_localized_20260606` | n/a | **runnable (dispatched parallel to this iter)** | Pearl_Writer | per Q-PRP-WRITER-AUDIT-STAGE-02 = (a); PR #1455 §B (S1) 9-file evidence |
| 7 (NEW) | `ws_pearl_marketing_ja_jp_freebie_pages_authoring_20260606` | n/a | **runnable (dispatched parallel to this iter)** | Pearl_Marketing | per OPD-20260606-015 launch gate + Q-PRP-JA-JP-FREEBIE-GAP-01 = (a) |

**TSV mutations DEFERRED to iter 3** per CLAUDE.md `feedback_sibling_session_collision` memory pattern — sibling sessions are mid-flight; concurrent ACTIVE_WORKSTREAMS.tsv writes risk merge collision. Iter 3 will flip rows 2-5 to `completed` + add rows 6-7 once sibling STARTUP_RECEIPTs commit.

### E.2 — Pearl Prime ONE-PATH cross-program ws's (referenced for §J coordination contract)

These ws's belong to the Pearl Prime ebook-assembly program (cap-entry `PEARL-PRIME-ONE-PATH-V1-01`) but are tracked here for cross-program intersection per §J:

| # | workstream_id | Phase | Owner | iter-2 status | Dispatch prompt location |
|---|---|---|---|---|---|
| ONE-PATH-1 | `ws_pearl_dev_one_path_phase_1_mechanical_sweeps_20260606` | Phase 1 (3 sub-PRs: L03 + L05 + L11) | Pearl_Dev | **dispatched parallel to this iter** | `artifacts/coordination/pearl_prime_one_path_child_ws_dispatch_prompts.md` Prompt 1 |
| ONE-PATH-2 | `ws_pearl_dev_one_path_phase_2_runtime_gates_20260606` | Phase 2 (7 sub-PRs: D8 + D4 + D6 + D10 + D11 + D12 + D13/D14/D15/D17) | Pearl_Dev | blocked on Phase 1 merge | same Prompt 2 |
| ONE-PATH-3a | `ws_pearl_editor_one_path_phase_3a_persona_atom_backfill_20260606` | Phase 3a Wave 1 (corp_mgrs × anxiety first per OPD-003) | Pearl_Editor + Pearl_Writer | **dispatched parallel to this iter (Wave 1)** | same Prompt 3 |
| ONE-PATH-3b | `ws_pearl_writer_one_path_phase_3b_signature_phrases_20260606` | Phase 3b (parallel with 3a) | Pearl_Writer | dispatched parallel | same Prompt 4 |
| ONE-PATH-4 | `ws_pearl_editor_one_path_phase_4_craft_gate_activation_20260606` | Phase 4 (gates on Phase 3a+3b completion) | Pearl_Editor | blocked on Phase 3 | same Prompt 5 |
| ONE-PATH-PM | `ws_pearl_pm_one_path_lockdown_sequencing_tracker_20260606` | meta-coord (weekly) | Pearl_PM | runnable | same Prompt 6 |

**Cross-program trigger:** ONE-PATH-3a Wave 1 (corp_mgrs × anxiety) completion is the upstream event that fires the first automated SKU-join check per §J.1 mechanical contract.

---

## §F — Phase A pre-launch CI gate matrix (iter 2 update; adds Q-PRP-STOREFRONT-CONTENT-GATE-01 as gating)

Iter-1 §4 listed 5 pre-launch CI gates. Iter-1 §F (dispatch-prompt §F) added a 6th gate (ja-JP freebie ws merged). Iter-2 adds a 7th gate per OPD-016:

| # | Gate | Owning ws | iter-2 status | Definition |
|---|---|---|---|---|
| 1 | `scripts/ci/check_external_buy_links.py` | ws #5 (CTA cutover) | **GREEN** (script authored + zero violations across 7 surface categories × {en-US, ja-JP}) | PR #1453 SHA `2aa09807b` |
| 2 | `scripts/ci/check_atoms_external_book_references.py` | ws #4 (atom audit) | **PARTIAL — Stage 1 GREEN; Stage 2a in flight** | PR #1454 authored script; Stage 2a ws (E.1 row 6) extends to localized atoms |
| 3 | `.github/workflows/pearl-prime-storefront-deploy.yml` | ws #3 (CF wiring) | **AUTHORED — scaffold landed; first deploy pending Snipcart provisioning** | PR #1450 SHA `5a481c1e2` |
| 4 | Snipcart account live + webhook secret rotated within 90 days | ws #3 (CF wiring) | **PENDING** (8 operator-action-required slots per #1450 PR body; awaits operator) | per PR #1450 operator-action list |
| 5 | D1 schemas applied; reviews + orders + library tables operational | ws #3 (CF wiring) | **AUTHORED — migrations landed in PR #1450; not yet applied to live D1 instance** | PR #1450 scaffold |
| 6 | ja-JP freebie pages authored (15 pages mirror en-US `brand-wizard-app/public/free/`) | ws_pearl_marketing_ja_jp_freebie_pages_authoring_20260606 (E.1 row 7) | **IN FLIGHT** (dispatched parallel to this iter) | per OPD-20260606-015 launch gate |
| 7 (NEW) | **Q-PRP-STOREFRONT-CONTENT-GATE-01 mechanical SKU-join criterion fires GREEN for at least the en-US `gen_z_professionals × anxiety` launch-SKU subset** (≥7 SKUs across 7 formats) | Pearl_PM automation hook (post Phase 3a Wave 1 merge) | **NOT-STARTED** — gated on ONE-PATH Phase 3a Wave 1 + ONE-PATH Phase 1 mechanical sweeps + ONE-PATH Phase 2 runtime gates landing | per OPD-20260606-016; codified in §J.1 below |

**Gate-clearance rule (updated):** Phase A launch milestone may NOT be declared unless gates 1-7 are GREEN AND the 6 smoke combinations (§G) reach `smoked-green` for at least combo 1 (en-US book) AND operator declares launch (per OPD-20260606-015 SCOPE-GATED launch). ja-JP and zh-TW smoke combos additionally require ja-JP / zh-TW persona-keyed atom coverage per §J.1; if either locale's atom coverage misses the gate, scope demotes to en-US-only launch per §L.

---

## §G — 6 smoke-combo readiness matrix (iter 2 update)

Per spec §AMENDMENT-2026-06-04.2.4 + OPD-20260606-015 SCOPE-GATED launch:

| Combo | Locale | Product type | iter-1 status | iter-2 status | Gated on |
|---|---|---|---|---|---|
| 1 | **en-US** | book | not-started | **not-started** (target: pre-launch-ready) | Phase 3a Wave 1 (corp_mgrs × anxiety) atom backfill + Q-PRP-STOREFRONT-CONTENT-GATE-01 fires + Snipcart provisioned + D1 applied. **Combo 1 is the launch-gating combo per OPD-015 Option B.** |
| 2 | en-US | audiobook | not-started | not-started | combo 1 + HLS streaming player working + signed-URL MP3 download |
| 3 | en-US | manga | not-started | not-started | combo 1 + manga PDF in R2 + WEBTOON reader |
| 4 | **ja-JP** | book | not-started | not-started | combo 1 + ja-JP locale routing + ja-JP catalog projection + JPY currency + ja-JP persona-keyed atom coverage (per §J.1) + ja-JP freebie pages (gate 6) |
| 5 | ja-JP | audiobook | not-started | not-started | combo 2 + combo 4 prerequisites + ja-JP narrator infra (already operational) |
| 6 | ja-JP | manga | not-started | not-started | combo 3 + combo 4 prerequisites + ja-JP manga assets (already operational) |

**Critical-path observation:** ALL 6 combos remain `not-started` because the upstream gate — ONE-PATH Phase 3a Wave 1 (corp_mgrs × anxiety persona-keyed atom backfill) — has NOT landed. Per OPD-20260606-003 (b) staged persona backfill, corp_mgrs is the FIRST persona; per OPD-20260606-015 SCOPE-GATED launch, the launch-day SKU subset is `gen_z_professionals × anxiety` (one persona × one topic, the gold-reference combo). Once Phase 3a Wave 1 lands AND the §J.1 mechanical SKU-join check fires GREEN for `gen_z_professionals × anxiety`, combo 1 moves to `pre-launch-ready`.

**Note on persona scope vs gold-reference combo:** OPD-20260606-013 pins `gen_z_professionals × anxiety × spiral × F006 × ahjan × production × --exercise-journeys × --pipeline-mode spine` as the canonical gold-reference SHA (combo for combo 1 launch). OPD-20260606-003 (b) staged persona backfill order starts with **corp_mgrs** (highest-revenue assignment) — NOT `gen_z_professionals`. The reconciliation: Phase 3a Wave 1 backfills BOTH `gen_z_professionals` AND `corp_mgrs` × `anxiety` in parallel; `gen_z_professionals × anxiety` is the launch-gating combo per OPD-015 (gold-ref baseline) while `corp_mgrs × anxiety` is the catalog-expansion-precedent combo per OPD-003 (revenue tier).

---

## §H — Critical path (iter 2; supersedes iter 1 §9 NEXT_ACTION)

**Current bottleneck (iter 2 fire):** ONE-PATH Phase 1 mechanical sweeps (L03 + L05 + L11) — these clear the structural debt that Phase 2 runtime gates depend on, and Phase 2 runtime gates are the precondition for Phase 3a content backfill being safe. Without Phase 1, the Phase 3a per-persona backfill cannot be trusted to produce gold-ref-equivalent output, so the §J.1 mechanical SKU-join check would fire RED rather than GREEN.

**Active parallel sessions (dispatched parallel to this PM iter):**

1. **Pearl_Dev** — ONE-PATH Phase 1 mechanical sweeps (Prompt 1; 3 sub-PRs for L03 SCENE→STORY label sweep, L05 RUNTIME_TEMPLATES.chapter_count deletion, L11 placeholder-leakage post-compose strip). **CURRENT BOTTLENECK ON CRITICAL PATH.**
2. **Pearl_Editor + Pearl_Writer** — ONE-PATH Phase 3a Wave 1 (`gen_z_professionals + corp_mgrs × anxiety` persona-keyed atom backfill to all 16 required slot-type dirs per D8 PersonaAtomCoverageError contract). Cannot land cleanly until Phase 1 + Phase 2 land (or runs in parallel and rebases).
3. **Pearl_Marketing** — `ws_pearl_marketing_ja_jp_freebie_pages_authoring_20260606` (15 ja-JP freebie pages mirror en-US `brand-wizard-app/public/free/`).
4. **Pearl_Writer** — `ws_pearl_writer_next_step_atom_audit_stage_2a_localized_20260606` (9 localized atom files per Pearl_Architect's PR #1455 §B evidence).

**Recommended merge sequencing (iter 2 → iter 3):**

```
Phase 1 mechanical PRs (L03 → L05 → L11)
    |
    v
Phase 2 runtime gate PRs (D8 → D4 → D6 → D10 → D11 → D12 → D13/D14/D15/D17)
    |
    v
Phase 3a Wave 1 PR (gen_z_professionals + corp_mgrs × anxiety atom backfill)
                |                                       Parallel: 3b signature_phrases + ja-JP freebies + Stage 2a localized audit
                v
Q-PRP-STOREFRONT-CONTENT-GATE-01 fires for gen_z_professionals × anxiety
    |
    v
First storefront SKU rows appended to sku_url_map.yaml (mechanical)
    |
    v
Combo 1 (en-US book) → pre-launch-ready
    |
    v
Snipcart operator-action slots cleared + D1 migrations applied
    |
    v
Combo 1 → smoked-green
    |
    v
Phase A launch milestone declared (per OPD-015 Option B SCOPE-GATED)
    |
    v
Catalog expands automatically per §J.1 as Phase 3a Wave 2+ per-persona PRs land
```

**Iter 2 NEXT_ACTION (Pearl_PM iter 3):** fire on first trigger — any of:
- (a) ONE-PATH Phase 1 mechanical PR merges (status flips PM iter 3 to track Phase 2 readiness),
- (b) Pearl_Writer Stage 2a localized audit PR merges,
- (c) Pearl_Marketing ja-JP freebie PR merges,
- (d) PR #1455 AMENDMENT-2026-06-04.2 rebased + merged (closes the open cap-entry overlap),
- (e) 24-hour no-motion (daily cadence per §A).

---

## §I — Iter-3 trigger conditions

Iter 3 fires on FIRST of:
1. Any PR in §C row 6 (#1455) status change (merged / closed / re-authored).
2. Any ONE-PATH Phase 1 mechanical PR merging on `origin/main`.
3. Any Phase 3a Wave 1 per-persona atom-backfill PR merging.
4. Pearl_Writer Stage 2a localized audit PR merging.
5. Pearl_Marketing ja-JP freebie pages PR merging.
6. Snipcart operator-action slots cleared (gate 4 in §F).
7. D1 migrations applied to live instance (gate 5 in §F).
8. First Q-PRP-STOREFRONT-CONTENT-GATE-01 SKU-join check fires GREEN (gate 7 in §F).
9. 24-hour no-motion (daily cadence per §A).
10. Operator decision logged in `operator_decisions_log.tsv` referencing PEARL-PRIME-STOREFRONT-V1-01 or PEARL-PRIME-ONE-PATH-V1-01.

---

## §J — Cross-program intersection (iter 2 NEW; verbatim from seed §J)

> Section §J below is incorporated **verbatim** from the iter-2 seed at `artifacts/coordination/storefront_v1_phase_a_tracker_iter_2_seed.md` §J. The seed is the historical pre-staged record (authored by Pearl_Architect 2026-06-06, pre-OPDs); this section lifts it into the live tracker as the iter-2 ratified contract.

The Pearl Prime ebook-assembly program (PR #1479 ONE-PATH lockdown — cap-entry `PEARL-PRIME-ONE-PATH-V1-01`) and the Storefront-V1 e-commerce program (PRs #1448-1454 cascade — cap-entry `PEARL-PRIME-STOREFRONT-V1-01`) intersect at exactly two contracts. Iter 2 ratifies both:

### §J.1 — Q-PRP-STOREFRONT-CONTENT-GATE-01 mechanical SKU-join criterion (NEW; ratified per OPD-20260606-016)

**Definition (operator-ratified per OPD-20260606-016):**
> A SKU joins the storefront catalog when its **persona×topic** has all 16 persona-keyed atom dirs (HOOK / STORY / SCENE / REFLECTION / EXERCISE / COMPRESSION / PIVOT / PERMISSION / PERMISSION_GRANT / TAKEAWAY / THREAD / INTEGRATION / TEACHER_DOCTRINE / TEACHER_DOCTRINE_INTRO / ANGLE_DEFINITION / ANGLE_CALLBACK) AND a smoke `book.txt` lands within **±10% of gold-reference word count envelope** for the runtime format.

**Mechanics:**
- Catalog growth = **mechanical consequence of Phase 3a landing per persona×topic.**
- **No operator approval per-SKU.** Pearl_PM dispatches catalog-expansion automation once Phase 3a's per-persona PR lands.
- The gold-reference word-count envelope per runtime format (from `artifacts/pearl_prime/gold_reference_ladder_2026-05-30/`):
  - `micro_book_15`: 6548 wc ±10% = [5893, 7203]
  - `micro_book_20`: 8338 wc ±10% = [7504, 9172]
  - `short_book_30`: 10538 wc ±10% = [9484, 11592]
  - `standard_book`: 19986 wc ±10% = [17987, 21985]
  - `extended_book_2h`: 27102 wc ±10% = [24392, 29812]
  - `deep_book_4h`: 39693 wc ±10% = [35724, 43662]
  - `deep_book_6h`: 56210 wc ±10% = [50589, 61831]

**Implementation hook (post Phase 3a per-persona PR merge; Pearl_PM automation):**
1. CI smoke runs all 7 runtime formats for the newly-backfilled persona × {anxiety, burnout, overthinking, ...whichever topics it has full atom coverage for}.
2. For each smoke that lands within ±10% of gold-ref envelope AND exits 0 (under production profile lockdown), append a SKU row to `config/storefront/sku_url_map.yaml` (or successor projector output).
3. Cloudflare deploy workflow picks up the new SKU; storefront catalog grows.

### §J.2 — Storefront-V1 launch scope (OPD-20260606-015 ratified)

**Launch-day SKU subset (Option B SCOPE-GATED):**
- `gen_z_professionals × anxiety × ahjan × {micro_15, micro_20, short_30, standard_book, extended_2h, deep_4h, deep_6h}` × {en-US, ja-JP, zh-TW}
- = 7 formats × 3 locales × 1 persona × 1 topic = **21 launch-day SKUs**
- (Per Q-PRP-STOREFRONT-CONTENT-GATE-01: ja-JP and zh-TW must have BOTH `gen_z_professionals × anxiety` persona-keyed atoms in their locale AND smoke pass the wc envelope; if either locale fails, scope further reduces to en-US-only = 7 SKUs.)

**Catalog growth path (post-launch):**
- Phase 3a backfill order per OPD-20260606-003 (b): corp_mgrs → working_parents → first_responders → healthcare_rns → gen_x_sandwich → tech_finance_burnout → millennial_women_professionals → gen_alpha_students → gen_z_student → nyc_executives → educators → midlife_women (the last blocked on arc-authoring per `ws_midlife_women_arc_authoring_20260427`).
- Each persona × topic combo that lands Phase 3a + passes the §J.1 criterion = +7 formats × 3 locales = +21 SKUs (or less if some topics aren't covered).
- Theoretical full-catalog (per OPD-20260606-004 (b) top-3 demote): 12 personas × ~15 topics × 7 formats × 3 locales ≈ 3,780 SKUs (vs. the 17,688 in #1453's hand-curated `sku_url_map.yaml` which assumed top-5 locales × all personas including ungated).

### §J.3 — Cross-program coordination contract

| Pearl Prime side | Storefront side | Trigger |
|---|---|---|
| Phase 3a per-persona PR lands + smoke passes §J.1 | Pearl_PM automation appends to `sku_url_map.yaml` + redeploy | Mechanical (no operator) |
| Phase 2 runtime gates land | Storefront catalog adoption is safe (no silent lesser-config) | Mechanical (no operator) |
| Phase 4 craft gates land | Storefront catalog adoption hits §13 rubric not just structural-assembly | Mechanical (no operator) |
| ONE-PATH `ws_pearl_pm_one_path_lockdown_sequencing_tracker_20260606` status update | Storefront-V1 Phase A tracker iter N+1 fires | Pearl_PM cron weekly (DAILY per §A iter-2 ramp) |

---

## §K — Updated merge cascade (iter 2 NEW; reflects post-merge state; verbatim from seed §K with status overlay)

> Section §K below incorporates the seed §K cascade-plan **with iter-2 post-merge status overlay added**. Seed §K originally projected the cascade pre-merge; iter 2 confirms the cascade executed.

| Step | PR | Owner | Iter-2 status |
|---|---|---|---|
| 0 | **#1479 ONE-PATH lockdown V1 spec** (was projected as "#1473 cap-entry" in seed; v2 clean recovery replacement) | Pearl_Architect | **MERGED** (`febd1fb95`) |
| 0' | **#1480 16 OPDs + iter-2 seed + 6 child ws prompts** (v2 clean recovery; was "#1478" in seed projection) | Pearl_Architect | **MERGED** (`11843f9f8`) |
| 1 | **#1455 AMENDMENT-2026-06-04.2** | Pearl_Architect | **OPEN — merge conflict** (substance already ratified via OPDs; PR-level merge pending operator-side rebase or v2 re-author) |
| 2 | #1448 PM tracker iter 1 | Pearl_PM | **MERGED** (`da691d6c4`) |
| 3 | #1454 Pearl_Writer audit Stage 1 | Pearl_Writer | **MERGED** (`db52b0293`) |
| 4 | #1450 Pearl_Int CF + Snipcart | Pearl_Int | **MERGED** (`5a481c1e2`) |
| 5 | #1452 Pearl_Dev mockups | Pearl_Dev | **MERGED** (`4c4ac5e0c`) |
| 6 | #1453 Pearl_Marketing CTA cutover | Pearl_Marketing | **MERGED** (`2aa09807b`) — `sku_url_map.yaml` 17,688 rows retained as catalog upper-bound; Q-PRP-STOREFRONT-CONTENT-GATE-01 mechanics gate which subset is actually live |

**Post-merge cascade (now in flight, parallel to this PM iter):**
- Pearl_PM dispatches the 6 child ws's per PR #1479 spec §7 phase order (Phase 1 mechanical → Phase 2 runtime → Phase 3a + 3b parallel → Phase 4 craft).
- Pearl_Marketing spawns `ws_pearl_marketing_ja_jp_freebie_pages_authoring_20260606` per OPD-20260606-015 launch gate (15 ja-JP freebie pages mirror en-US `brand-wizard-app/public/free/`).
- Pearl_Writer spawns `ws_pearl_writer_next_step_atom_audit_stage_2a_localized_20260606` per Q-PRP-WRITER-AUDIT-STAGE-02 = (a) (9 localized atom files identified in Pearl_Architect's S1 evidence in PR #1455).

---

## §L — Phase A launch readiness gate (iter 2 UPDATE; verbatim from seed §L)

> Section §L below is incorporated **verbatim from seed §L** as the iter-2 launch-readiness gate definition.

Original iter-1 §4 gate matrix unchanged; iter-2 §F supersedes with 7-gate matrix; iter-2 §L adds these launch-decision criteria:

| Gate | Source | iter-2 status |
|---|---|---|
| Pearl Prime ONE-PATH lockdown cap-entry merged (was projected as #1473; landed as #1479) | seed §L | **GREEN** (`febd1fb95`) |
| Storefront AMENDMENT-2026-06-04.2 cap-entry merged (#1455) | seed §L | **AMBER** — PR open with conflict; substance ratified via OPDs |
| 5 child storefront PRs cascade merged (#1448 → #1454 → #1450 → #1452 → #1453) | iter-1 §C / seed §K | **GREEN** (all 5 merged per §C) |
| `ws_pearl_marketing_ja_jp_freebie_pages_authoring_20260606` lands | AMENDMENT-2026-06-04.2 §B | **PENDING** (dispatched parallel to this iter) |
| Pearl Prime `gen_z_professionals × anxiety` launch-SKU subset passes Q-PRP-STOREFRONT-CONTENT-GATE-01 criterion (≥7 SKUs en-US confirmed; ja-JP + zh-TW SKUs added if pass) | §J.2 | **NOT-STARTED — gating launch declaration** |
| Pearl Prime Phase 3a per-persona backfill ws's begin landing (corp_mgrs first per OPD-003) | ONE-PATH §7 Phase 3a | **PENDING** (Wave 1 dispatched parallel; post-launch gates catalog expansion) |

**Phase A launch declaration criterion** (operator-tier):
- All 5 storefront-program child PRs merged ✓ (§C rows 1-5 + the cap-entry PRs #1479 + #1480; #1455 cap-entry pending but substance ratified)
- ja-JP freebie pages ws merged (pending)
- At least the 7-SKU en-US `gen_z_professionals × anxiety` subset passes §J.1 + appears in `sku_url_map.yaml` live (pending Phase 3a Wave 1 + Q-PRP-STOREFRONT-CONTENT-GATE-01 mechanical fire)
- Operator declares Phase A live; catalog expands automatically per §J.1 from there

---

*End of iter 2 block. Iter 1 sections preserved verbatim below as audit trail.*

---

# ITER 1 — 2026-06-06 — initial tracker authoring (preserved as audit trail)

> Iter 1 sections §1 / §3 / §4 / §5 / §9 are SUPERSEDED by iter 2 §E / §G / §F / §E.1 / §H respectively. Iter 1 §2 / §6 / §7 / §8 remain in force unmodified. Preserved verbatim for audit trail.

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
