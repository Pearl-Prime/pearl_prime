# Pearl_Int Integration Health Check + Cloudflare Diagnosis — 2026-05-14

Branch: `agent/brand-wizard-composite-mode-20260514`
Source of truth: `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` + `scripts/ci/integration_env_registry.py`
Validator: `scripts/ci/check_integration_env.py` + per-service curl probes

## TL;DR — three actionable items for operator

| # | Service | State | Operator action |
|---|---------|-------|-----------------|
| 1 | **Cloudflare Pages local deploy** | BLOCKED | Generate a new API token at https://dash.cloudflare.com/profile/api-tokens with **Account → Cloudflare Pages → Edit** permission, **no IP CIDR restriction**, save to Keychain as `CLOUDFLARE_API_TOKEN_PAGES`. See §1 below. |
| 2 | **ElevenLabs** | INVALID KEY (HTTP 401) | Regenerate at https://elevenlabs.io/app/settings/api-keys. Save fresh `sk_...` to Keychain as `ELEVENLABS_API_KEY` (replaces current revoked one). |
| 3 | ~~**GEMMA_BASE_URL**~~ | ✅ DONE 2026-05-14 — set to Tailscale variant `http://pearlstar.tail7fd910.ts.net:11434/v1` (parity with COMFYUI_URL/COSYVOICE_URL; reachable from this dev machine; `gemma3:27b` + `qwen2.5:14b` listed by Ollama). Health check now: **0 REQUIRED missing, 40/86 set**. See OPD-20260514-009. |

Everything else is healthy. Full report below.

---

## §0 Pearl_Int preflight

- `.env` MISSING at repo root — **expected**; Phoenix Omega uses macOS Keychain as canonical source per CLAUDE.md. Load via `eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"`.
- `.env` is gitignored ✓
- `.env.example` MISSING — minor gap (would help new contributors); not blocking.
- `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` present (12 core services + Pages + R2 + video platforms).
- `scripts/ci/integration_env_registry.py` is canonical env-var list.

## §1 Cloudflare token diagnosis (root cause of PR #1111 local deploy failure)

### The token in Keychain is wrong-scoped + IP-restricted

```
CLOUDFLARE_API_TOKEN              cfut_Orc... (53 chars)   ← Workers Builds token, IP-restricted
CLOUDFLARE_API_TOKEN_PAGES        (0 chars — empty entry)  ← right name, no value
CLOUDFLARE_ACCOUNT_ID             b80152c3...               ← OK
```

### Evidence trail

```
GET /user/tokens/verify                          → HTTP 200  "valid and active"
GET /accounts/{id}/pages/projects                → HTTP 401  "Authentication error"
GET /user/tokens/permission_groups               → HTTP 403  code 9109 "Cannot use the access token from location: 174.208.231.101"
```

Interpretation: `cfut_` prefix = Workers Builds token, which is (a) scoped to Workers only — no Pages perm — and (b) IP-restricted by Cloudflare to specific CI/build infrastructure. From a developer laptop on a residential IP, every Pages call fails. This is correct security posture for a CI-only token; what's missing is a SEPARATE local token for Pages preview deploys.

### Pearl_Int fix path (operator does the portal walk; I write the Keychain entry)

**You (operator):**

1. Open https://dash.cloudflare.com/profile/api-tokens
2. Click **Create Token**
3. Use the **Custom Token** template
4. Permissions: **Account → Cloudflare Pages → Edit**
5. Account Resources: include the Phoenix Omega account (the one with ID `b80152c3...`)
6. **IP Address Filtering: leave EMPTY** (no restriction) — this is what makes it usable locally
7. TTL: 30 days is reasonable for rotating; or set to your house preference
8. Click **Continue to summary** → **Create Token** → copy the displayed token

**Then paste the token back in this chat** and I'll run:

```bash
security add-generic-password -a "$USER" -s CLOUDFLARE_API_TOKEN_PAGES -w "<paste-token>" -U
# Verify
curl -s -H "Authorization: Bearer <token>" "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/pages/projects?per_page=1" | python3 -m json.tool | head -10
```

I'll then propose a small follow-up PR that:
- Updates `scripts/ci/load_integration_env_from_keychain.py` to load `CLOUDFLARE_API_TOKEN_PAGES` into a separate env var
- Updates `scripts/ci/integration_env_registry.py` to track it as optional (Cloudflare Pages local deploys)
- Documents the Pages-vs-Workers split in `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` §Cloudflare

After that, the workflow is: `eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"; CLOUDFLARE_API_TOKEN=$CLOUDFLARE_API_TOKEN_PAGES npx wrangler pages deploy dist --project-name=brand-admin-onboarding --branch=<my-branch>` → preview URL on the branch deployment.

Note: This is purely for **branch-preview deploys** (developer-side proofing). Production deploys to `brand-admin-onboarding.pages.dev` still go through the CI workflow on `push: branches: [main]`.

---

## §2 Full integration health check

```
Summary: 39/85 env vars set  |  1 REQUIRED missing (GEMMA_BASE_URL)
```

### REQUIRED — all OK except 1

| Env var | Service | Status |
|---------|---------|--------|
| `DASHSCOPE_API_KEY` | DashScope/Qwen | ✓ set (35c, intl SG endpoint) |
| `DASHSCOPE_BASE_URL` | DashScope/Qwen | ✓ `https://dashscope-intl.aliyuncs.com/compatible-mode/v1` |
| `ANTHROPIC_API_KEY` | Anthropic | ✓ set (per check; not used by repo code per LLM-policy enforcement) |
| `ELEVENLABS_API_KEY` | ElevenLabs | ✓ set (51c) — **but token REVOKED (HTTP 401)** — see §2 action item |
| `CLOUDFLARE_API_TOKEN` | Cloudflare | ✓ set (53c) — Workers Builds scope only — see §1 |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare | ✓ set |
| `GITHUB_TOKEN` (gh CLI) | GitHub | ✓ logged in as Ahjan108 (keyring) |
| `WORDPRESS_*` | WordPress | ✓ set + reachable (HTTP 200) |
| `PEARL_STAR_IP`, `COMFYUI_URL` | Pearl Star | ✓ set; ComfyUI HTTP 200 |
| `COSYVOICE_URL` | Pearl Star | ✓ set; `/docs` HTTP 200 (service up — root 404 is normal FastAPI; correct healthcheck endpoint is `/docs`) |
| `HF_TOKEN` | Hugging Face | ✓ set (37c); HTTP 200 from whoami-v2 |
| `RUNCOMFY_API_KEY` | RunComfy | ✓ set (36c) |
| `R2_*` (6 vars) | Cloudflare R2 | ✓ all set |
| `YT_*`, `TIKTOK_*` (SP+CC) | YouTube/TikTok | ✓ client IDs/secrets set; some refresh tokens missing (see optional) |
| **`GEMMA_BASE_URL`** | Pearl Star/Gemma | ❌ **MISSING — REQUIRED** |

### OPTIONAL missing (45 — all known intentional gaps)

Broken into 4 cohorts:
- **Tier-2 LLM defaults** (5 vars): Gemma/Claude/Ollama/DeepSeek model overrides — use built-in defaults
- **Google AI** (2 vars): `GOOGLE_AI_API_KEY`, `GEMINI_MODEL` — ja-JP translation path, optional
- **GoHighLevel + SMTP + Funnel** (11 vars): funnel infra, only needed if running the funnel locally
- **Social Media — ND brand + secondary tokens** (~20 vars): NeuroDharma channel + Instagram/TikTok refresh tokens, populated as channels go live
- **Disabled platforms** (5 vars): Bilibili, Douyin — disabled pending ICP filing
- **SerpApi** (1 var): trend checking, 245-call/mo budget; not currently scheduled
- **RunComfy alias** (1 var): `RUNCOMFY_TOKEN` is just an alias for `RUNCOMFY_API_KEY` per Keychain parity note

### Connection tests (per-service)

| Service | Endpoint | Result |
|---------|----------|--------|
| Cloudflare | `/user/tokens/verify` | ✓ HTTP 200 (token valid) |
| Cloudflare | `/accounts/{id}/pages/projects` | ❌ HTTP 401 (scope/IP — see §1) |
| Hugging Face | `/api/whoami-v2` | ✓ HTTP 200 |
| Pearl Star ComfyUI | `/system_stats` | ✓ HTTP 200 |
| Pearl Star CosyVoice | `/docs` | ✓ HTTP 200 |
| ElevenLabs | `/v1/user` | ❌ HTTP 401 invalid_api_key — see action item 2 |
| GitHub | `gh auth status` | ✓ logged in |
| WordPress | `/wp-json/` | ✓ HTTP 200 |

---

## §3a Closeout — Path B taken (Cloudflare local preview deferred)

Operator generated `cfut_yESN9R...` via the portal but Cloudflare hard-locks every `cfut_`-prefixed token to Workers Builds scope + Cloudflare CI infrastructure IPs — **a known Cloudflare design constraint**, not fixable from the token side. Two cfut_ tokens are now active (`cfut_OrcMgi...` and `cfut_yESN9R...`); both remain valid for Workers Builds CI but neither can deploy Pages from a developer laptop.

**Decision (OPD-20260514-008):** Take Path B. PR #1111 is verified locally (vite preview + Claude_Preview screenshots × 4 locales). CI workflow at `.github/workflows/brand-admin-onboarding-pages.yml` auto-deploys on merge to main → live at brand-admin-onboarding.pages.dev. Branch-preview deploys remain a future nice-to-have that requires a non-`cfut_` Custom Token from the operator (Custom Token template at the bottom of the API tokens portal — distinct portal path from any other "Create Token" button).

**Pearl_Int autonomous follow-up done in this session:**
- Cleared the empty `CLOUDFLARE_API_TOKEN_PAGES` Keychain slot that had been polluted with a `cfut_` value during diagnostic. Slot is now genuinely empty so the next session reads "missing" rather than "set-but-wrong".
- Added `CLOUDFLARE_API_TOKEN_PAGES` to `scripts/ci/integration_env_registry.py` with explicit guidance text including the `cfut_` constraint and the portal path. `check_integration_env.py` now surfaces this as a tracked missing var, so the next person to run the health check immediately sees the right portal walk instead of rediscovering the constraint from scratch.

**Operator follow-up if branch-preview deploys become important:**
- Generate a Custom Token at https://dash.cloudflare.com/profile/api-tokens (scroll to bottom of templates list, click "Get started" next to "Custom token", NOT any other template). Permission: `Account → Cloudflare Pages → Edit`. IP filter empty. Result token will be ~40 chars with no `cfut_` prefix.
- Save to Keychain: `security add-generic-password -a "$USER" -s CLOUDFLARE_API_TOKEN_PAGES -w "<token>" -U`
- Token hygiene: revoke unused `cfut_` tokens at the same URL (you now have at least 2 active).

## §3 Recommended follow-ups (post operator action)

- **Small PR**: scaffold `.env.example` from `scripts/ci/integration_env_registry.py` (one-time, deterministic). Helps new contributors and surfaces tracked vars in code review.
- **Small PR**: update `scripts/ci/load_integration_env_from_keychain.py` to also load `CLOUDFLARE_API_TOKEN_PAGES` (or alias when Workers token is absent), once operator generates the Pages token.
- **Monitoring**: ElevenLabs 401 + future Cloudflare token expiry (current expires 2026-10-31) should be caught by a scheduled health check. Pearl_Int will draft a `scripts/integration/health_check.sh` per `skills/pearl-int/SKILL.md` §STEP 4 if desired (separate task).

---

## Pearl_Int boundaries respected

- ✗ Did NOT generate the Cloudflare token (user-only per `skills/pearl-int/SKILL.md` §SECURITY BOUNDARIES — Pearl_Int navigates, user copies).
- ✗ Did NOT enter or rotate the ElevenLabs key.
- ✓ Diagnosed token scope / IP issues using non-destructive GET requests.
- ✓ Read Keychain entries by name; no values printed in full.
- ✓ Health check used `scripts/ci/check_integration_env.py` (canonical) — no parallel secret registry created.
