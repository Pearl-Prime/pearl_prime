# Handoff — Storyblocks EULA Compliance (2026-07-19)

**Signal:** `BLOCKED:no writable access to 48social Django backend (+ Ahjan108 GitHub suspended)`  
**Owner:** Pearl_Int  
**Branch:** `agent/storyblocks-eula-compliance-20260719`  
**Base:** `origin/main` @ `9e9b9e606791590337cd7d0f2fb425def2e6f760`  
**Design tip (durable):** `3701e0524d2d39d62250fcafb1b65e5e00b8c684`  
**Prior tip:** `54c25e605413ef2a39b72751a62a5cbdd1b465ec`  
**Durable remote:** `pearlstar_offline` → `pearl_star:~/git/phoenix_omega_offline.git`  
**GitHub PR (phoenix_omega):** blocked — Ahjan108 suspended (re-verified 2026-07-19T10:08Z)
---

## CONTINUE re-verify (2026-07-19 ~18:08 UTC+8) — NEW evidence

| Probe | Result (this turn) |
|-------|---------------------|
| `gh auth status` / `gh api user` | **Still suspended** — keyring token invalid; HTTP 403 “Sorry. Your account was suspended” |
| `git ls-remote origin` / SSH github.com | **403 suspended** (cannot open phoenix_omega PR) |
| `pearlstar_offline` branch tip | **Confirmed** then advanced to `3701e0524d2d39d62250fcafb1b65e5e00b8c684` (this CONTINUE harden) |
| Design files on tip | Present: `docs/STORYBLOCKS_EULA_COMPLIANCE.md`, reconciled `docs/storyblocks-integration.md`, signed PDF, this handoff |
| Local siblings / Spotlight | No `manage.py`, no `*/brands/services/storyblocks`, no `*48social*` product checkout (only briefing audio filenames) |
| Pearl Star `~/git` | Still **only** `phoenix_omega_offline.git` — no 48social clone |
| `~/.zsh_history` | Only `git clone …/phoenix_omega_v4.8.git` — **never** a 48social backend clone on this machine |
| `PROGRAM_STATE` / `INTEGRATION_CREDENTIALS_REGISTRY` / `integration_env_registry.py` | **No** STORYBLOCKS_* vars; **no** backend clone URL |
| Public GitHub user [`48social`](https://github.com/48social) | **EXISTS** (id `219904317`) but **0 public repos**, 0 public events, 0 orgs |
| Name guesses `48social/{backend,api,app,…}` | All **404** without auth (private or different host) |
| Web search for public 48social Django + Storyblocks | No official product backend found |

**Concrete blocker (single line):** Operator must provide a **writable clone of the private 48 Social Django backend** (and restore GitHub push for merge/PR); environment has design-only access via pearlstar_offline.

---

## DISCOVERY REPORT (unchanged conclusions)

### Backend target (when access lands)

Paths from design spec (implement **there**, not in phoenix_omega):

- `backend/apps/brands/services/storyblocks/`
- `backend/apps/brands/views.py` (StockSearchView — fix per-brand `user_id`)
- `backend/apps/brands/services/asset_selection_service.py`
- `backend/apps/campaigns/` (`CampaignAssetDownload` + new MAU ledger)
- `backend/apps/pipelines/services/` (R1 render guard)

### Spec packet already on branch

- `docs/STORYBLOCKS_EULA_COMPLIANCE.md` — R1/R2/R3 + rate limit + AI wall + attribution
- `docs/storyblocks-integration.md` — EULA-reconciled
- `docs/Storyblocks API Agreement - 48 Social.pdf` — Doc Ref EUYIG-SF8TR-9LD23-TJ3AK
- Decisions: `OPD-SB-01`…`OPD-SB-04` (hard block 105th; per-brand id; UTC month; STOCK_PROVIDER exclusive)

### MAU month basis

**UTC calendar month** (`YYYY-MM`) — Q-SB-03 default.

---

## ACCESS_REQUIRED (operator checklist)

Paste answers into chat or a local path; agent cannot discover these.

1. **Backend clone URL** (likely private under `https://github.com/48social/<repo>` or another host):  
   `______________________________`
2. **Auth that can clone + push that repo** (PAT / SSH key / Codespace with access):  
   `______________________________`
3. **Default branch name** (usually `main`):  
   `______________________________`
4. **GitHub for phoenix_omega design PR** (optional once backend merges): unsuspend `Ahjan108` **or** `gh auth login` with a write-capable identity.

---

## Exact NEXT commands (operator → agent)

### A. Unblock GitHub on this Mac (phoenix_omega PR)

```bash
gh auth logout -h github.com -u Ahjan108
gh auth login -h github.com   # identity with push on Ahjan108/phoenix_omega_v4.8
cd /Users/ahjan/phoenix_omega
git fetch origin
# publish design branch from pearlstar if origin lacks it:
git push -u origin agent/storyblocks-eula-compliance-20260719
gh pr create --base main --head agent/storyblocks-eula-compliance-20260719 \
  --title "docs(storyblocks): EULA compliance design + reconciled integration spec" \
  --body "Design-only. Backend implementation follows in 48social Django repo. See docs/STORYBLOCKS_EULA_COMPLIANCE.md + handoff artifacts/coordination/handoffs/storyblocks_eula_compliance_2026-07-19.md"
```

### B. Fetch design tip from Pearl Star (any machine with `pearl_star` SSH)

```bash
git fetch pearlstar_offline agent/storyblocks-eula-compliance-20260719
git log -1 --oneline pearlstar_offline/agent/storyblocks-eula-compliance-20260719
# expect: 3701e0524d2d39d62250fcafb1b65e5e00b8c684 (or newer tip on same branch)
```

### C. Resume EXECUTE once backend URL is known (paste into new Pearl_Int turn)

```bash
# REPLACE URL — do not invent
export SB_BACKEND_URL='git@github.com:48social/<PRIVATE_REPO>.git'   # or https://...
export SB_BACKEND_DIR="$HOME/48social_backend"
git clone "$SB_BACKEND_URL" "$SB_BACKEND_DIR"
cd "$SB_BACKEND_DIR"
git fetch origin && git checkout -b agent/storyblocks-eula-compliance-20260719 origin/main

# Then implement per phoenix_omega docs (copy from pearlstar tip or local):
#   docs/STORYBLOCKS_EULA_COMPLIANCE.md  (R1 render guard, R2 per-brand user_id,
#   R3 MAU meter hard 104, rate limiter 600/120, AI wall, attribution, release marks)
# Required tests: MAU 104/105 boundary, search excluded, brand id stability,
#   render-guard, rate-limiter. Preserve confirm-first / no HD pre-cache.
# Merge PR → emit: storyblocks-eula-compliance=<full-SHA>
```

### D. Verify still blocked (smoke)

```bash
gh api user -q .login                                 # must NOT be 403
test -d "$HOME/48social_backend/backend/apps/brands/services/storyblocks" && echo BACKEND_OK
```

---

## What changed (design branch — already pushed)

| Path | Change |
|------|--------|
| `docs/STORYBLOCKS_EULA_COMPLIANCE.md` | Clause→guard map R1–R3 + extras |
| `docs/storyblocks-integration.md` | EULA-reconciled |
| `docs/Storyblocks API Agreement - 48 Social.pdf` | Signed SSOT (<1MB) |
| `artifacts/coordination/operator_decisions_log.tsv` | OPD-SB-01..04 |
| `artifacts/coordination/handoffs/storyblocks_eula_compliance_2026-07-19.md` | This handoff (+ CONTINUE re-verify) |
---

## Tests run

None on product backend (repo still absent). Design packet only.

---

## CLEANUP LEDGER

| Item | Status |
|------|--------|
| Full worktree checkout attempt | Aborted earlier; branch via temp-index |
| `/tmp/48repos.json` `/tmp/48ev.json` | Ephemeral CONTINUE probes — safe to delete |
| Branch `agent/storyblocks-eula-compliance-20260719` | **HOLD** on `pearlstar_offline` @ `3701e0524d…` |
| Inventing Django Storyblocks code in phoenix_omega | **Forbidden** — not done |

---

## NEXT_ACTION

1. Operator fills **ACCESS_REQUIRED** #1–#2 (backend URL + credentials).  
2. Optionally run **A** to unsuspend/login and open phoenix_omega design PR.  
3. Pearl_Int runs **C** → MERGED → `storyblocks-eula-compliance=<full-SHA>`.
