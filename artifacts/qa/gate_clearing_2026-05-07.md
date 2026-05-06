# Gate Clearing — Pearl_Int 2026-05-07

Brand-2 manga ship (`proj_manga_first_ship_20260425`) had two operator-only
gates blocking Pearl_Dev stages D–H. Both are now cleared. Pearl_Dev may
resume the runbook at stage D.

## Outcomes

| Gate | Status | Notes |
|---|---|---|
| GATE-OP-1 (R2 secrets) | **CLEARED** | 4 R2 names + replacement Cloudflare token + R2_ENDPOINT in Keychain at `service=phoenix-omega`. Live R2 connection verified via boto3 put/get/delete. |
| GATE-OP-2 (Pearl Star SSH) | **CLEARED** | `ssh pearl_star` reaches host; key + config + known_hosts all pre-existing; marker `~/.phoenix_omega_pearl_star` already installed Apr 25. |
| GATE-LOC (ja-JP atom coverage) | passable, unchanged | 89.3% — above 85% degrade threshold, ship can proceed. |
| GATE-DEV (queue_panel_renders.py) | resolved | Script committed at `scripts/manga/queue_panel_renders.py` (9402 bytes). |

## GATE-OP-1 detail

### Token rotation

The leaked Cloudflare API token (prefix `cfut_Ab1…`) that appeared in chat
on 2026-05-07 was revoked by operator at
`https://dash.cloudflare.com/profile/api-tokens`. A replacement Workers AI
token (prefix `cfut_OrcMgi…`, IP-filtered to operator's home address, valid
through 2026-11-01) was generated and staged at `docs/cloudflare_api.txt`
(gitignored).

### R2 credentials staged

Operator generated bucket-scoped R2 S3-compatible credentials at
`Cloudflare Dashboard → R2 → Manage R2 API Tokens`:

- `R2_ACCESS_KEY_ID` (32 hex)
- `R2_SECRET_ACCESS_KEY` (64 hex)
- bucket `phoenix-omega-artifacts` (existing, default storage class
  Standard, public access disabled, EU jurisdiction)
- S3 endpoint host `<32-char hex>.r2.cloudflarestorage.com` (EU
  jurisdiction; differs from `CLOUDFLARE_ACCOUNT_ID`)

### Keychain load (no values logged)

Pearl_Int read `docs/cloudflare_api.txt` and added each value to macOS
Keychain at `service=phoenix-omega, account=<NAME>`:

| Name | Length | Status |
|---|---|---|
| `CLOUDFLARE_ACCOUNT_ID` | 32 | OK |
| `CLOUDFLARE_API_TOKEN` | 53 | OK (overwrote leaked) |
| `R2_ACCOUNT_ID` | 32 | OK |
| `R2_ACCESS_KEY_ID` | 32 | OK |
| `R2_SECRET_ACCESS_KEY` | 64 | OK |
| `R2_BUCKET` | 23 | OK |
| `R2_ENDPOINT` | 65 | OK |

Verification: `eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"`
exports all 6 registered names. The unregistered `R2_ENDPOINT` is fetched
directly via `security find-generic-password` until the small registry
update in this PR ships.

### R2 live connection smoke test

`boto3` with `R2_ENDPOINT` (EU jurisdiction host) + bucket-scoped
credentials performed:

- `list_objects_v2` on `phoenix-omega-artifacts` → 0 objects (empty
  bucket, expected)
- `put_object` `.phoenix_omega_smoketest_2026-05-07` → success
- `delete_object` same key → success

`list_buckets` returns `AccessDenied` because the token is bucket-scoped
(by design — least privilege).

### EU jurisdiction nuance + r2_sync.py fix

The operator's bucket lives in the EU jurisdiction; its S3 endpoint host
hash (`626d6eb8…`) differs from `CLOUDFLARE_ACCOUNT_ID` (`b80152c3…`).
`scripts/artifacts/r2_sync.py` previously hard-coded
`https://{account_id}.r2.cloudflarestorage.com` — which would fail for EU
buckets.

Fix in this PR: `r2_sync.py` reads `R2_ENDPOINT` and falls back to the
default-jurisdiction format when unset. Default-jurisdiction buckets keep
working unchanged; EU buckets now work too.

`R2_ENDPOINT` added to `scripts/ci/integration_env_registry.py` so it
exports through the canonical Keychain loader alongside the rest.

## GATE-OP-2 detail

Pre-existing state on operator's Mac:

- `~/.ssh/id_ed25519_pearl_star` (private key, perms 600, dated Apr 8)
- `~/.ssh/id_ed25519_pearl_star.pub` (public key)
- `~/.ssh/config`:
  ```
  Host pearl_star
    HostName 100.92.68.74
    User ahjan108
    AddressFamily inet
    IdentityFile ~/.ssh/id_ed25519_pearl_star
    ServerAliveInterval 60
    ServerAliveCountMax 3
  ```
- `~/.ssh/known_hosts`: entries for both `pearlstar.local` and
  `pearlstar.tail7fd910.ts.net`

Earlier `Permission denied (publickey,password)` in this session was
caused by attempting `ssh pearlstar.tail7fd910.ts.net` (full Tailscale
hostname), which doesn't match the `Host pearl_star` alias and so didn't
pick up the IdentityFile. Using the alias resolves cleanly.

### Connection test

```
$ ssh pearl_star 'echo OK $(hostname); uname -a; nvidia-smi --query-gpu=memory.free,name --format=csv,noheader'
OK pearlstar
Linux pearlstar 6.17.0-22-generic #22~24.04.1-Ubuntu SMP PREEMPT_DYNAMIC Thu Mar 26 15:25:54 UTC 2 x86_64 x86_64 x86_64 GNU/Linux
3156 MiB, NVIDIA GeForce RTX 5070 Ti
```

### Marker file

```
$ ssh pearl_star 'ls -la ~/.phoenix_omega_pearl_star'
-rw------- 1 ahjan108 ahjan108 168 Apr 25 11:14 /home/ahjan108/.phoenix_omega_pearl_star
```

Marker installed during prior session; `assert_remote.py` will accept the
host. The runbook's casual reference to `~/manga_marker` was a name typo;
canonical filename is `~/.phoenix_omega_pearl_star` per
`scripts/agent/install_pearl_star_marker.sh`.

## Followups for Pearl_Dev

1. **GPU contention.** RTX 5070 Ti reports only ~3 GiB free of 16 GiB
   total. Likely the `ws_teacher_manga_triptych_20260410` workstream is
   occupying VRAM. Stage D (FLUX render) needs to either coordinate with
   the triptych owner before queuing or wait for the rig to drain. The
   runbook's "≥40 GB free" expectation came from a different GPU
   assumption — for the 5070 Ti the practical guidance is "wait until
   ≥10 GB free for FLUX-schnell-fp8".

2. **r2_sync.py endpoint patch lands in this PR.** Pearl_Dev's stage G
   call to `r2_sync.py push` will now resolve the EU endpoint correctly
   without further code change.

3. **Chat-transcript exposure.** Three values transited the
   conversation transcript during this session:
   a. The original leaked token `cfut_Ab1…` — already revoked.
   b. `CLOUDFLARE_ACCOUNT_ID` value — not authentication material; left as is.
   c. The replacement `CLOUDFLARE_API_TOKEN` value `cfut_OrcMgi…`,
      via Pearl_Int's Read of `docs/cloudflare_api.txt`. This is the
      canonical staging-file pattern (per CLAUDE.md ElevenLabs
      precedent), so the file itself is the intended source — but if
      the chat transcript leaves operator-controlled storage, conservative
      hygiene says rotate this token too. Operator decides; deferred.

## Pearl_Int learning capture

Skill reference added at
`skills/pearl-int/references/credential_staging_files.md` documenting:

- Canonical gitignored credential staging file paths
- Cloudflare R2 token result-page format
- Correct Keychain scheme (`-s phoenix-omega -a <NAME>`, NOT the inverse)
- Parse + load command pattern with no value echoing
- EU jurisdiction endpoint nuance
- Token rotation triggers

Future Pearl_Int sessions can apply the same pattern to other staging
files (`docs/11.txt`, `cloudflare_workers_ai.txt`, etc.) without
re-deriving.

## Pearl_Dev resume signal

> **GATES CLEARED. Resume manga brand-2 stages D–H per the brand-2
> handoff at
> `artifacts/manga/chapter_scripts/cognitive_clarity__ahjan__en_US__overthinking__the_loop_is_not_thinking/HANDOFF.md`
> (or successor location). GPU is contended (3 GiB free) — check before
> queuing FLUX renders. R2 endpoint override is in env (`R2_ENDPOINT`)
> and consumed automatically by `r2_sync.py` after this PR merges.**
