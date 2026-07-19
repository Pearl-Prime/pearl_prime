# Handoff — Storyblocks EULA Compliance (2026-07-19)

**Signal:** `BLOCKED:no access to 48social Django backend repo + GitHub Ahjan108 suspended`  
**Owner:** Pearl_Int  
**Branch:** `agent/storyblocks-eula-compliance-20260719`  
**Base:** `origin/main` @ `9e9b9e606791590337cd7d0f2fb425def2e6f760`

---

## DISCOVERY REPORT

### 1. Backend repo locate

| Probe | Result |
|-------|--------|
| Sibling checkouts under `/Users/ahjan` | No `*48social*` / `*/brands/services/storyblocks` checkout |
| Spotlight / `manage.py` near social | None matching 48social |
| Pearl Star (`pearl_star:~/git`, home tree) | Only `phoenix_omega_offline.git` + phoenix_omega; **no** 48social Django |
| GitHub via `gh` / HTTPS / SSH as `Ahjan108` | **Account suspended** (HTTP 403); token in keyring invalid; cannot search or clone |
| phoenix_omega references | Spec paths only (`docs/storyblocks-integration.md`); Metricool prompt confirms separate 48social Django repo exists but gives no clone URL |

**Required access (operator):** clone URL + push credentials for the **48 Social Django product backend** that contains:

- `backend/apps/brands/services/storyblocks/`
- `backend/apps/brands/views.py`
- `backend/apps/campaigns/` (`CampaignAssetDownload`)
- `backend/apps/pipelines/services/`

**Do not invent** that implementation inside phoenix_omega.

### 2. Spec vs contract reconciliation

Landed in this packet:

- `docs/STORYBLOCKS_EULA_COMPLIANCE.md` — clause→guard map + implementation sketches
- `docs/storyblocks-integration.md` — EULA-reconciled (user_id per brand, MAU meter, render guard, rate limits, AI wall, release marks, Q-SB-04 N/A)
- `docs/Storyblocks API Agreement - 48 Social.pdf` — signed SSOT (was untracked; now committed)

Key disagreements fixed in the design surface (were in the pre-reconcile spec):

1. views.py `request.user.id` vs AssetSelectionService `brand_id`
2. No MAU meter / no download-vs-search distinction
3. No proactive rate limiter
4. No license-on-download render guard
5. “Watermarked preview” wording vs agreement’s watermark-free previews (still unlicensed)

### 3. Inventory (live vs spec-only)

| Component | Status in this environment |
|-----------|----------------------------|
| `StoryblocksAPIService` / `AssetSelectionService` / `CampaignAssetDownload` | **Spec-only** here — code not present in phoenix_omega; cannot verify live vs stub without backend repo |
| Confirm-first / per-campaign GCS / delete-on-campaign-delete | Preserved in design (inventory=EXTENDS; do not drop) |
| Render guard / MAU ledger / rate limiter / views.py brand id | **Design only** until backend PR |

### 4. MAU calendar basis

**UTC calendar month** (`YYYY-MM`). Rationale: §4.3(a) says “calendar month”; monthly invoices → UTC is the unambiguous default (Q-SB-03). Flag if Storyblocks billing uses another anchor.

---

## What changed (this branch)

| Path | Change |
|------|--------|
| `docs/STORYBLOCKS_EULA_COMPLIANCE.md` | **Added** — mechanism map R1–R3 + extras |
| `docs/storyblocks-integration.md` | **Added + reconciled** to signed agreement |
| `docs/Storyblocks API Agreement - 48 Social.pdf` | **Added** (855314 bytes < 1MB blob gate) |
| `artifacts/coordination/operator_decisions_log.tsv` | **OPD-SB-01..04** defaults |
| `artifacts/coordination/handoffs/storyblocks_eula_compliance_2026-07-19.md` | This handoff |

---

## Verified

- PDF Doc Ref **EUYIG-SF8TR-9LD23-TJ3AK**, effective **2026-02-24 → 2027-02-23**, Payment Schedule free tier **104 MAUs**, fee **$4.40/MAU**, MAU = Download query user_ids, rate limits 600/120.
- No Django Storyblocks implementation reachable to unit-test.
- GitHub PR/merge to `Ahjan108/phoenix_omega_v4.8` **blocked** by account suspension.
- Durable push target attempted: `pearlstar_offline` (`pearl_star:~/git/phoenix_omega_offline.git`).

---

## Tests run

None on product backend (repo absent). Design-only packet — no phoenix_omega runtime Storyblocks code to test.

---

## Blockers

1. **Primary:** No access to 48social Django backend repo (path/URL unknown; not checked out; not on Pearl Star).
2. **Secondary:** GitHub identity `Ahjan108` suspended — cannot open/merge GitHub PR for phoenix_omega either until re-auth / unsuspend.

---

## NEXT_ACTION

1. Operator: restore GitHub access for `Ahjan108` **or** provide alternate push remote with PR capability.
2. Operator: provide 48social backend clone URL + credentials (or local path).
3. Pearl_Int resume: implement R1–R3 + extras per `docs/STORYBLOCKS_EULA_COMPLIANCE.md` on that repo; merge; emit `storyblocks-eula-compliance=<full-SHA>`.

---

## CLEANUP LEDGER

| Item | Status |
|------|--------|
| Worktree `/Users/ahjan/phoenix_omega_wt_storyblocks_eula_20260719` | Aborted/removed (full checkout too slow); branch built via temp-index commit |
| Scratch `/tmp/sb_eula.txt` | Ephemeral pdftotext — OK to leave or delete |
| Debug instrumentation | None |
| Branch `agent/storyblocks-eula-compliance-20260719` | HOLD until GitHub unsuspend or operator merges from pearlstar_offline |
