# EXECUTE — Storyblocks integration: make it abide by the signed API License Agreement

**Owner:** Pearl_Int (backend integration)  ·  **Substrate:** the 48social product backend (Django) — NOT phoenix_omega code
**Turn contract:** EXECUTE. Do not stop at "analysis," "plan," "PR open," or "report back later."
The turn ends only when you emit `storyblocks-eula-compliance=<full-SHA>` on a durable surface
(merged PR in the backend repo) **or** one concrete BLOCKER with evidence + pushed branch +
resume surface. A status summary is not a deliverable.

---

## STARTUP_RECEIPT (fill before acting — every line below is a CLAIM you re-verify live)

- Spec (authoring surface): `docs/storyblocks-integration.md` (in phoenix_omega)
- Signed agreement (SSOT for legal terms): `docs/Storyblocks API Agreement - 48 Social.pdf` (9 pp, Doc Ref EUYIG-SF8TR-9LD23-TJ3AK, effective 2026-02-24 → 2027-02-23)
- Code target: Django backend `backend/apps/brands/services/storyblocks/…`, `backend/apps/campaigns/…`,
  `backend/apps/brands/views.py`, `backend/apps/pipelines/services/…`
- **This code is NOT in phoenix_omega.** phoenix_omega only holds the spec + PDF. You MUST locate the
  real backend repo first (DISCOVERY, below). If you cannot reach it, that is a BLOCKER, not a reason to
  invent a parallel implementation here.

---

## PROVENANCE (complete in your DISCOVERY REPORT before writing code)

```
research:   The signed Storyblocks API License Agreement (the PDF). This is the legal ground truth;
            docs/storyblocks-integration.md is the design that must be RECONCILED to it.
documents:  docs/storyblocks-integration.md (design spec) + the PDF (governing terms).
builds_on:  Existing StoryblocksAPIService / StoryblocksAssetService / AssetSelectionService /
            anonymize_user_id/anonymize_project_id / CampaignAssetDownload — EXTEND IN PLACE.
inventory:  EXTENDS existing search/confirm/download flow. inventory=REDUCED is forbidden —
            do not drop the confirm-first / per-campaign-download / GCS-cleanup design; it is
            already EULA-aligned. You are ADDING compliance guards, not rebuilding the flow.
```

---

## MISSION

Bring the Storyblocks integration into provable compliance with the signed agreement. Two operator
requirements are non-negotiable, and there is a **third, cost-critical fact from the contract** the
operator's summary did not state — honor all three:

### R1 — Download is the license-granting act (operator req 1 + EULA §A, §2.1)
The HD **download query** is what grants the license to use an asset. A watermark-free **preview grants
no license**. Therefore:
- Any Storyblocks asset that is actually **used in a rendered/shipped campaign MUST have gone through the
  download endpoint** (`get_download_urls` → HD fetched → stored per-campaign). Confirm the existing
  `confirm_selection()` path does this and is the ONLY path that feeds a real render.
- Add a guard: the render/publish path refuses a Storyblocks-sourced asset that has no
  `CampaignAssetDownload` record (i.e. never licensed). Preview URLs must never reach a final render.

### R2 — Distinct, stable, anonymized User IDs per brand (operator req 2 + §2.1(iv), §4.3)
- Every **search AND download** query carries an **anonymized** `user_id` (§2.1(iv) requires anonymized
  IDs on *both* query types). Keep `anonymize_user_id` (SHA-256).
- The `user_id` is keyed **per brand**, not per end-user — operator ruling. It must be **deterministic and
  stable across a calendar month** so one brand = exactly one identity.
- **Fix the current inconsistency:** the spec's `AssetSelectionService` hook keys on `brand_id`
  (`anonymize_user_id(self.brand_id)`) but the `StockSearchView` hook keys on `request.user.id`. These
  produce different identities for the same brand and would inflate MAU. Standardize **every** Storyblocks
  query to the per-brand anonymized ID. Resolve brand from the request/campaign context in views.py.

### R3 — MAU is counted from DOWNLOAD queries only; free tier = 104/month; do not exceed (§4.3(a) + Payment Schedule)
> §4.3(a): "MAU… is determined by the number of unique User IDs provided in the **Download** queries to
> Storyblocks API in a given calendar month." Payment Schedule: "Monthly Active User Fee to apply to
> monthly usage **beyond 104 MAUs**." Fee = $4.40/MAU beyond 104.
- **Search user IDs do NOT count toward MAU. Only distinct download user_ids per calendar month count.**
- Build a **MAU meter + hard cap**: a persistent monthly ledger of the distinct anonymized **download**
  user_ids seen in the current calendar month. Before issuing a download query for a brand whose id is
  **not already in this month's ledger**, check the count:
  - if adding it would make the monthly distinct count **> 104**, BLOCK the download (do not silently
    incur overage) and surface a clear error/telemetry event;
  - if the brand is already counted this month, allow unlimited further downloads (assets are
    unlimited per user — only the distinct-ID count is capped).
- The ledger resets per **calendar month** (UTC — confirm the billing month basis; note the assumption).
- Emit a metric/log when the month crosses 80 and 100 MAUs (early warning before the 104 wall).

---

## ADDITIONAL EULA GUARDS (in scope — the agreement requires these; do not skip)

- **Rate limits (§2.1/§2.2):** throttle client-side to **≤600 search/min and ≤120 download/min**. Keep the
  existing 429 backoff but add a proactive limiter so we never depend on their throttling.
- **No stockpiling / no standalone files / no scripted high-volume download (EULA §B):** the confirm-first,
  download-only-on-selection, per-campaign copy, delete-on-campaign-delete design already satisfies this —
  **preserve it**. Do not add any "pre-cache HD" / "shared HD pool" / bulk-prefetch path.
- **No AI/ML training on Stock Files or their metadata/keywords (EULA §B, preamble):** CLIP embeddings
  computed from thumbnails to *assist selection* are explicitly allowed ("…not… a restriction on your
  ability to use AI to assist in your selection"). But add a guardrail/comment ensuring Storyblocks
  thumbnails, embeddings, tags, or keywords are **never** exported into any model-training / fine-tuning
  dataset. Confirm no existing pipeline does this.
- **Attribution (§3.2):** ensure the source of Storyblocks content is attributable (stored
  `source_provider="storyblocks"` + surfaced where content sources are credited).
- **Content-mix disclaimers (§2.2):** legacy Pexels/Pixabay/Unsplash remain behind `STOCK_PROVIDER`.
  If both providers can appear together to an end user, ensure license-difference clarity; CC-licensed or
  unreleased content needs the conspicuous disclaimers ("Content not guaranteed for commercial use" /
  "Content not Model Released"). If providers are mutually exclusive per deploy, document that and note the
  disclaimer obligation is N/A — do not over-build.
- **Identifiable people/property (EULA):** surface the Storyblocks `model_released` / `property_released`
  marks in the asset metadata so downstream use can respect them.

---

## DISCOVERY REPORT (produce FIRST, before any edit)

1. **Locate the backend repo.** It is not in phoenix_omega. Find it (sibling checkout, another GitHub repo,
   or clone target). Report its path/URL and current default branch. If you cannot access it → **BLOCKER**:
   push the compliance design (spec delta + a `STORYBLOCKS_EULA_COMPLIANCE.md` mechanism doc) to a
   phoenix_omega branch, open the PR, and report the exact repo you need access to. Do not implement
   Storyblocks code inside phoenix_omega.
2. **Reconcile spec vs. contract.** List every place `docs/storyblocks-integration.md` disagrees with the
   PDF (at minimum: user_id keyed per-user in views.py vs. per-brand; no MAU meter; no download-vs-search
   MAU distinction; no rate limiter; no license-on-download render guard). Correct the spec in the same
   PR/handoff so the design and the law match.
3. **Inventory existing code** at the integration points (search hook, StockSearchView, confirm/download,
   render/publish path) and confirm which is live vs. spec-only.
4. State the calendar-month/timezone basis you will meter MAU on and why.

---

## OPEN OPERATOR QUESTIONS (recommend defaults; log to operator_decisions_log.tsv; do not block on them)

- **Q-SB-01 — 105th brand behavior.** Default: **HARD BLOCK** any new brand's *download* once the month's
  distinct download-ID count is at 104 (operator said "don't go over the free limit"). Alt: allow overage
  at $4.40/MAU with a loud alert. Recommend the hard block.
- **Q-SB-02 — user_id identity scope.** Default: **per brand** (operator ruling). Confirms all end-users of
  one brand share a single Storyblocks identity, so brand count — not user count — drives MAU.
- **Q-SB-03 — MAU month basis.** Default: **UTC calendar month**, matching a monthly invoice. Flag if
  Storyblocks bills on a different anchor.
- **Q-SB-04 — provider co-presence.** Default: assume `STOCK_PROVIDER` makes them mutually exclusive per
  deploy (no mixed disclaimer needed). If mixed presentation is real, implement §2.2 disclaimers.

---

## DELIVERABLES

1. Per-brand anonymized `user_id` on **all** search + download queries (views.py path fixed).
2. MAU meter + **hard 104 cap on distinct monthly download user_ids** (with 80/100 warnings), metering
   downloads only.
3. License-on-download render guard (R1): no `CampaignAssetDownload` record → asset cannot enter a render.
4. Proactive rate limiter (600 search/min, 120 download/min).
5. AI-training wall-off guard/comment; attribution surfaced; identifiable-people marks surfaced;
   content-mix disclaimer handling (or documented N/A).
6. Tests: MAU cap (104 boundary: 104 passes, 105th new brand blocks, repeat brand unlimited), search-does-
   not-count-toward-MAU, per-brand id stability across a month, render-guard rejects preview-only asset,
   rate-limiter throttle. Unit + integration.
7. Spec reconciled to the contract; a short `STORYBLOCKS_EULA_COMPLIANCE.md` mapping each guard → the
   clause it satisfies (§A, §B, §2.1, §2.2, §3.2, §4.3(a)).

## DO NOT

- Do not let a preview URL reach a final render (that asset is unlicensed).
- Do not count search queries toward MAU, and do not meter MAU per end-user — per brand, download-only.
- Do not add HD pre-caching / shared pools / bulk prefetch (stockpiling breach).
- Do not export Storyblocks assets/metadata into any AI-training set.
- Do not build Storyblocks code inside phoenix_omega. Do not weaken any test to pass.

## GOTCHAS

- The cost trap: keying `user_id` per end-user (as the current views.py hook does) would multiply MAUs and
  blow past 104 fast. Per-brand keying is both the operator ruling and the cost control.
- MAU counts **downloads**, not searches — a naive "count every user_id we send" over-meters. Meter only at
  the download call site.
- The ledger must be race-safe: two concurrent downloads for two new brands at count 103 must not both
  pass. Use a DB unique constraint / transaction on (month, user_id), then count.

## LANDING CONTRACT (exactly one end state, same turn)

- **MERGED** — PR opened in the backend repo, required checks green, squash-merged, emit
  `storyblocks-eula-compliance=<full-SHA>`; **or**
- **BLOCKED** — one concrete blocker (e.g. "no access to backend repo <name/url>"), work pushed to a remote
  branch (never local-only), compliance design landed as phoenix_omega docs, resume surface named.

CLEANUP LEDGER (required): branches/worktrees removed or declared HOLD; scratch files removed; no debug
instrumentation left in the staged diff. Handoff file:
`artifacts/coordination/handoffs/storyblocks_eula_compliance_2026-07-19.md` (what changed, what was
verified, exact tests run, PR/merge SHA, proof roots, blockers, next command).

## CLOSEOUT_RECEIPT

```
signal:        storyblocks-eula-compliance=<full-SHA>   (or BLOCKED:<one-line blocker>)
repo:          <backend repo path/url> @ <branch>
acceptance:    system working  (guards enforced + tests green) — NOT "bestseller/done"; name the layer
mau_cap:       104 distinct monthly DOWNLOAD user_ids, per-brand, hard block on 105th   [Q-SB-01=<default|override>]
r1_license:    render-guard rejects non-downloaded Storyblocks assets: PASS/FAIL
r2_userid:     per-brand anonymized id on search+download; views.py inconsistency fixed: PASS/FAIL
r3_meter:      downloads-only metering; search excluded; 80/100 warnings; boundary tests: PASS/FAIL
extras:        rate-limiter / AI-wall / attribution / disclaimers: <status each>
decisions:     Q-SB-01..04 → operator_decisions_log.tsv rows <ids>
handoff:       artifacts/coordination/handoffs/storyblocks_eula_compliance_2026-07-19.md
cleanup:       <ledger>
NEXT_ACTION:   <specific resume step, or "none — merged">
```
