# Handoff — Storyblocks-for-Pearl-Prime Re-Scope (2026-07-19)

**Signal:** `storyblocks-pearl-prime-rescope=SPECCED` (SHA pending push)  
**Owner:** Pearl_Int / Pearl_Architect  
**Branch:** `agent/storyblocks-pearl-prime-rescope-20260719`  
**Base tip:** `agent/storyblocks-eula-compliance-20260719` @ `7fb88a449b9049a99b690f96e11cf4c68d812b23`  
**Durable remote:** `pearlstar_offline` (origin GitHub still 403 suspended for Ahjan108)  
**Authority doc:** `docs/STORYBLOCKS_PEARL_PRIME_RESCOPE.md`

---

## Operator clarification (why this handoff exists)

Prior turn assumed substrate = **48social Django** because:

1. Signed agreement Licensee = **48 Social**
2. Design paths = `backend/apps/brands/services/storyblocks/…`
3. MAU model = per-brand / per-campaign

Operator: *want Storyblocks in **Pearl Prime*** (phoenix_omega). That is a **different substrate**.

**48social GitHub is NOT required** unless Pearl Prime will call a remote 48social Storyblocks API (none exists in-repo today).

---

## Discovery snapshot

| Item | Result | Layer |
|------|--------|-------|
| Storyblocks client/code in phoenix_omega | Absent | ABSENT → re-scope SPECCED |
| Stock bank today | Pexels/Pixabay/Unsplash via `scripts/brand/build_stock_image_bank.py` | CODE-WIRED (legacy providers) |
| Social b-roll | Pexels plates under `artifacts/stock_image_bank/...` | EXECUTED-REAL for Pexels path only |
| Cover pipeline | five_layer / KDP cover scripts; no Storyblocks | CODE-WIRED without Storyblocks |
| `STORYBLOCKS_*` credentials registry / Keychain tracked | Missing | — |
| Prior EULA design packet | Present on design branch | SPECCED for 48social |

---

## Proposed Pearl Prime path (summary)

- **Bank:** preview metadata in stock bank; **licensed HD per work unit** (book cell / social campaign slug) — no shared HD pool  
- **Guards:** license-on-download, MAU 104 hard cap, rate limits, AI wall-off, attribution  
- **Default identity:** per **locale brand** (OPEN — operator confirm)  
- **Default first surface:** operator must pick (social b-roll vs covers recommended)  
- **100%:** EXECUTED-REAL on chosen surface + tests — not docs alone  

---

## NEXT_ACTION

Operator answers (gate):

1. Surface: `covers` | `social_broll` | `pearl_news` | other  
2. Identity scope: accept **per locale brand** or override  
3. Storyblocks API keys + confirm Pearl Prime covered under 48 Social agreement  

Then agent EXECUTE in phoenix_omega per `docs/STORYBLOCKS_PEARL_PRIME_RESCOPE.md` §4.

---

## Related artifacts

- `docs/STORYBLOCKS_PEARL_PRIME_RESCOPE.md` — this re-scope (SSOT for Pearl Prime)  
- `docs/STORYBLOCKS_EULA_COMPLIANCE.md` — clause map (retarget call sites)  
- `docs/STORYBLOCKS_DOWNLOAD_BANK_METADATA_CONTRACT.md` — pattern; GCS/campaign → work-unit bank  
- `docs/storyblocks-integration.md` — 48social historical design  
- Prior handoff (superseded blocker): `artifacts/coordination/handoffs/storyblocks_eula_compliance_2026-07-19.md`
