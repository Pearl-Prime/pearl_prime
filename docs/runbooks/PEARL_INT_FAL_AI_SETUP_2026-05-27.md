# Pearl_Int — fal.ai Setup Runbook

**Date:** 2026-05-27
**Owner:** Pearl_Int
**Trigger:** OPD-149 (2026-05-26) — operator approved Milestone H §7.1 fal.ai smoke test; blocked on credential setup
**Estimated operator time:** 10-15 minutes (one-time)
**Cost:** $0 to create account + key. Smoke test compute ≈ $1 (two-stage 1024×1024 panel pair).

---

## Why this matters

The V5.1 manga compute scoping (`docs/MANGA_V5_COMPUTE_SCALING_OPTIONS.md` §3.4) identifies fal.ai as the **lowest per-panel hosted cost option** for Qwen-Image-Layered ($0.08/panel two-stage vs RunComfy / Modal / Replicate alternatives). Before committing to fal.ai for the 800-series × 10-episode × 35-panel catalog rollout (~$22,400 at scale), the operator approved a **§7.1 smoke test**: render one ep_001 panel via fal.ai's `fal-ai/qwen-image-layered/lora` endpoint and compare side-by-side to the Pearl Star V5.1 baseline.

That smoke test is **the only empirical evidence that can move Milestone G forward**. Pearl_Int has staged everything needed except the credential itself, because Pearl_Int's security boundary prohibits creating third-party accounts on the operator's behalf.

---

## What you (operator) do

### Step 1 — Create a Phoenix fal.ai account

1. Open: https://fal.ai/login
2. Sign in with an email Phoenix controls (recommend the same Google account used for the Phoenix OmegaCloudflare workspace). fal.ai supports OAuth (Google, GitHub) and email/password.
3. On first sign-in, fal.ai applies the free signup credit automatically (sufficient for the smoke test).
4. Optional: under **Settings → Billing**, add a payment method if you intend to run the full ep_001 smoke test (~$1) plus any margin. Pure account creation does NOT require a card.

### Step 2 — Generate the API key

1. Navigate to: https://fal.ai/dashboard/keys
   - Direct route: top-right avatar → **Settings** → **API Keys** in the left sidebar.
2. Click **Add Key** (or "Create API Key").
3. Optional: give the key a label, e.g. `phoenix-omega-milestone-h-smoke`. Keys are not scope-limited at this level — there is one tier.
4. **Copy the key immediately.** fal.ai shows the full key value **once, at creation time**. After you close the modal, only the first/last few chars are visible.
5. Paste the value into chat for Pearl_Int — or skip the chat handoff and proceed directly to Step 3.

### Step 3 — Add the key to macOS Keychain

Phoenix's canonical credential storage is macOS Keychain under service name `phoenix-omega`. The same path every other integration uses:

```bash
# Replace <PASTE_KEY_HERE> with the value from Step 2.
# This is interactive — Keychain prompts for your macOS login password the first time.
security add-generic-password \
  -s phoenix-omega \
  -a FAL_KEY \
  -w "<PASTE_KEY_HERE>" \
  -U
```

The `-U` flag updates the entry if it already exists (safe to re-run).

To verify the entry exists (does NOT print the value):

```bash
security find-generic-password -s phoenix-omega -a FAL_KEY 2>&1 | head -1
# Expected: "keychain: ..." line, no error
```

To print the value (only run when you intentionally want it on stdout — be aware of shell history):

```bash
security find-generic-password -s phoenix-omega -a FAL_KEY -w
```

### Step 4 — Verify Phoenix's loader picks it up

From repo root:

```bash
cd /Users/ahjan/phoenix_omega
eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
[ -n "$FAL_KEY" ] && echo "FAL_KEY loaded: ${#FAL_KEY} chars" || echo "FAIL: FAL_KEY not loaded"
```

Expected output: `FAL_KEY loaded: N chars` (N ≈ 60-80 depending on fal.ai's current key format).

### Step 5 — Validate the key against fal.ai's API (auth-only, no compute spent)

This call hits fal.ai's queue-status endpoint with a sentinel request ID. Auth-success returns `404 not_found` JSON (the request ID doesn't exist, but the key authenticated). Auth-failure returns `401 unauthorized`.

```bash
curl -sS -o /tmp/fal_validate.json -w "HTTP:%{http_code}\n" \
  -H "Authorization: Key $FAL_KEY" \
  "https://queue.fal.run/fal-ai/qwen-image/requests/00000000-0000-0000-0000-000000000000/status"
cat /tmp/fal_validate.json
```

- **HTTP:404** + JSON like `{"detail": "Request not found"}` → key is valid. Proceed.
- **HTTP:401** + auth-error JSON → key was copied wrong. Repeat Step 2.
- **HTTP:000** or connection refused → network issue, not credential issue. Retry.

### Step 6 — Mark OPD-149 ready for execution

Add a follow-up line to `artifacts/coordination/operator_decisions_log.tsv` (or reply in chat) noting that the FAL_KEY is now provisioned. The next Pearl_Int / Pearl_Dev session that picks up Milestone H §7.1 will see the credential, run the smoke test, and pipe results back.

---

## What Pearl_Int has already staged for you

| File | Status | Purpose |
|------|--------|---------|
| `scripts/ci/integration_env_registry.py` | UPDATED | Adds `FAL_KEY` row so loader auto-exports it once it's in Keychain |
| `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` §12a | UPDATED | Single canonical doc entry for fal.ai (env var, validation, license, pricing) |
| `docs/runbooks/PEARL_INT_FAL_AI_SETUP_2026-05-27.md` | NEW (this file) | The step-by-step you're reading |
| `artifacts/coordination/operator_decisions_log.tsv` OPD-151 | — | Separate entry for the Cloudflare Workers Builds debt; not gated on fal.ai |

No production code references `FAL_KEY` yet — the smoke test dispatcher will land in a follow-up PR once the credential exists. This is intentional: Pearl_Int does NOT scaffold callers ahead of credentials per the discover-before-acting protocol.

---

## Failure modes + what to do

| Symptom | Diagnosis | Action |
|---------|-----------|--------|
| Step 5 returns 401 | Key was truncated on copy (fal.ai modal closed early) or wrong env var name in Keychain (must be exactly `FAL_KEY`, all caps) | Regenerate key via dashboard (Step 2), re-add to Keychain (Step 3) |
| Step 4 says "FAL_KEY not loaded" but Keychain has the entry | `service` name mismatch — must be `phoenix-omega` | `security delete-generic-password -s <wrong-service> -a FAL_KEY` then redo Step 3 |
| Step 5 returns 403 with billing error | Free-tier credit exhausted or account flagged | Add payment method under fal.ai → Settings → Billing |
| Step 5 hangs > 30s | fal.ai status page check: https://status.fal.ai/ | Retry after status is green |

---

## Security reminders

- **NEVER paste the FAL_KEY value into a committed file** (markdown, YAML, code). Keychain is the only home.
- The key is **not IP-locked** (unlike `cfut_` Cloudflare tokens). Treat it as full-permission — losing it = anyone can spend the Phoenix balance.
- If the key leaks, rotate immediately: fal.ai dashboard → API Keys → **Revoke** on the leaked key, generate a new one, redo Step 3.
- The `Keychain` entry is on **this Mac only**. CI runners (if any later) need the same key added to GitHub Actions Secrets — file a separate Pearl_Int request once the local smoke test passes.

---

## Cross-references

- OPD-149 — operator approval for the smoke test (blocker)
- `docs/MANGA_V5_COMPUTE_SCALING_OPTIONS.md` §3.4 + §7.1 — why fal.ai, what the smoke test measures
- `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` §12a — canonical credential entry
- `scripts/ci/integration_env_registry.py` — env var registration (`FAL_KEY` row)
- `artifacts/research/iyashikei_style_lora_scout_2026-05-21.md` Channel 1 — fal.ai commercial-clean status, LoRA loading interface confirmation
- Pearl_Int skill file: `skills/pearl-int/SKILL.md` — security boundaries (why Pearl_Int can't do this for you)
