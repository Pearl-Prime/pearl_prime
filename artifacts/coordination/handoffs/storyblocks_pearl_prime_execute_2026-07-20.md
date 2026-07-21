# Handoff — Storyblocks Pearl Prime EXECUTE (2026-07-20)

**Signal:** `storyblocks-pearl-prime=6a1120982d601ac19f2286a323557bb6dae5439a`  
**Layer:** CODE-WIRED + unit tests (**system working**); live EXECUTED-REAL **not** claimed (no keys)  
**Branch:** `agent/storyblocks-pearl-prime-20260720`  
**Base:** `agent/storyblocks-pearl-prime-rescope-20260719` @ `05c69d740a`  
**Durable remote:** `pearlstar_offline` @ `6a1120982d` (origin GitHub 403 suspended — PR/merge BLOCKED)

---

## Defaults applied (operator said “go on”)

| ID | Decision |
|----|----------|
| Q-SB-PP-01 | Surface = **social b-roll** |
| Q-SB-PP-02 | Identity = **per locale brand** |
| Q-SB-PP-03 | Legal = proceed under 48 Social agreement as design assumption; **operator-must-confirm**; no live API without keys |
| Q-SB-01/03 | HARD BLOCK 105th MAU; UTC month; downloads-only |

Logged in `artifacts/coordination/operator_decisions_log.tsv` as `OPD-SB-PP-01`…`OPD-SB-03`.

---

## What landed

| Path | Role |
|------|------|
| `scripts/storyblocks/` | API client (HMAC), rate limiter, MAU ledger, license store, confirm_download, consumer_guard |
| `scripts/social/build_video_snippet_bank.py` | B-roll consumer guard for Storyblocks |
| `tests/storyblocks/test_mau_and_license_guards.py` | Unit tests (mocked HTTP) |
| `scripts/ci/integration_env_registry.py` | `STORYBLOCKS_*` tracked |
| `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` §8d | Human credential docs |

**Not done:** live Storyblocks download (keys absent); covers surface; PR/merge to GitHub if account suspended.

---

## How to load keys (when available)

```bash
# Stage in Keychain service phoenix-omega:
#   STORYBLOCKS_PUBLIC_KEY, STORYBLOCKS_PRIVATE_KEY
eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
python3 -c "from scripts.storyblocks.api_client import StoryblocksAPIClient; StoryblocksAPIClient()"
```

Without keys, client raises `StoryblocksConfigError` (fail-closed).

---

## NEXT_ACTION (operator)

1. Confirm Q-SB-PP-03 legal (Pearl Prime under 48 Social agreement)  
2. Stage Storyblocks API keys in Keychain  
3. Optional: live smoke confirm_selection for one social_broll work unit  
4. Unsuspend GitHub / open PR if merge signal required on origin
