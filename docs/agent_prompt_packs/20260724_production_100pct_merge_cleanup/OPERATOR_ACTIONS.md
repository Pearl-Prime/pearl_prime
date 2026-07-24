# Operator Actions — things only you can do (2026-07-24)

These are gated on you (credentials, billing, brand/taste). No agent lane will attempt them.
Each has a "then say" — the phrase that unblocks the waiting lane.

## A. Rotate leaked R2/Cloudflare credentials — SECURITY, overdue since 07-21
Five secrets were pasted in plaintext into a session transcript on 2026-07-21
(see `artifacts/coordination/handoffs/session_cleanup_r2_manga_spec_handoff_2026-07-21.md`).
Rotation was deferred and is still pending.
1. Cloudflare dashboard → R2 → API tokens → roll the token(s).
2. Update macOS Keychain entries (names per `scripts/ci/integration_env_registry.py`).
3. Verify: `eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"` then a small R2 list op.
**Then say:** "R2 creds rotated" (no lane blocked, but closes the security loose end).

## B. Add `CLOUDFLARE_API_TOKEN` GitHub Actions secret — blocks all brand-wizard deploys
Every brand-wizard Pages deploy has failed since 2026-07-22T17:25Z.
GitHub → Pearl-Prime/pearl_prime → Settings → Secrets and variables → Actions →
New repository secret → `CLOUDFLARE_API_TOKEN` (a token with Pages write).
**Then say:** "CF token set" → Lane 05 re-runs the deploy and verifies live.

## C. Clear the Alibaba DashScope billing arrearage — blocks free CJK6 TTS
Account-wide block (financial action). Console: Singapore region only —
`https://modelstudio.console.alibabacloud.com/ap-southeast-1#/api-key`.
**Then say:** "DashScope unblocked" → TTS lane extends the EN voice bank to CJK6.

## D. Approve branch protection on main — one word, biggest safety win
main currently has ZERO protection (live-confirmed 404). Lane 02 prepares the
exact ruleset per `docs/BRANCH_PROTECTION_REQUIREMENTS.md` (required checks:
Core tests, Release gates, EI V2 gates, Change impact, Drift detectors) and
shows you the command before applying.
**Then say:** "apply branch protection" → Lane 02 applies + verifies.

## E. Quality reads (brand/taste — the real 100%-content gates)
1. **Manga pilot read:** 3 cells / 37 episodes are real on main. Read one episode
   per cell (paths in `SESSION_HANDOFF_20260723_manga_dispatch.md`). Scale work
   and PRs #243/#245 stay HELD until your read.
   **Then say:** "manga pilot approved" (or name fixes).
2. **zh-TW smoke book read:** Lane 06 produces the first complete zh-TW Waystream
   book. Wave 1 (10 books) stays HELD until your read.
   **Then say:** "zh-TW smoke approved" (or name fixes).
