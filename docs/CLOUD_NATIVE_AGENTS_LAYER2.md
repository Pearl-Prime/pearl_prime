# Cloud-Native Agents Layer 2 — Cloudflare R2 for binary artifacts

**Status:** Layer 2 active (this PR).
**Predecessor:** [Layer 1](./CLOUD_NATIVE_AGENTS.md) (PR #633, merged).
**Successor:** Layer 3 — Pearl Star → R2 push integration.

## Why

After Layer 1 the operator's laptop stops growing `.claude/worktrees/`
(agent work moved to Codespaces). But the repo itself can still grow if
agents commit rendered books, character portraits, or QA-run epubs. Each
manga book at FLUX-schnell quality is ~50 MB; 132 series × ~10 books ×
50 MB = 66 GB, which would blow up `.git` and break Codespaces' 15 GB
free-tier disk.

Layer 2 moves those binary artifacts to **Cloudflare R2** (10 GB free,
$0 egress) and keeps only **manifests** (YAML pointers + sha256) in the
repo.

## What ships in this PR

| File | Purpose |
|---|---|
| `config/artifacts/r2_buckets.yaml` | Single source of truth for bucket name, namespaces, key conventions, lifecycle rules |
| `schemas/artifacts/manifest.schema.json` | JSON Schema for artifact manifests (Draft 2020-12) |
| `scripts/artifacts/r2_sync.py` | `push` / `pull` / `verify` / `ls` CLI; uses boto3 against R2's S3-compatible endpoint |
| `scripts/artifacts/setup_r2.sh` | Idempotent bucket-creation + CORS + lifecycle apply (run once from Codespace) |
| `.github/workflows/no-binary-blobs.yml` | CI guard: rejects PRs adding binary files >1 MB to the repo (with allowlist for small fixtures + doc images) |

## Bucket layout

One bucket: `phoenix-omega-artifacts`. Five namespaces under prefix:

```
manga/rendered_books/{series_id}/{book_id}/{asset}
manga/portraits/{character_id}/{variant}.png
qa_runs/{date}/{run_id}/{book_id}/{asset}        # rotated 30d
brand/{brand_id}/{asset_type}/{filename}
tmp/{session_id}/{filename}                      # auto-purged 24h
```

Free-tier sizing target: ~6.5 GB sustained, 3.5 GB headroom inside the
10 GB cap.

## Auth model

R2 supports two auth modes; Phoenix Omega uses **mode 2** because it
works identically on Codespaces, GitHub Actions, and Pearl Star without
needing the node CLI on every host.

| Mode | Used by | Creds |
|---|---|---|
| Cloudflare API token (account-level) | `wrangler` (setup_r2.sh only) | `CLOUDFLARE_API_TOKEN` |
| R2 access keys (S3-compatible) | `r2_sync.py` + boto3 | `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY` |

## How the operator sets this up (one-time, ~5 minutes)

### 1. Create R2 access keys

Go to https://dash.cloudflare.com → **R2** → **Manage R2 API Tokens** →
**Create API Token**:

- Permission: **Object Read & Write**
- Bucket scope: **Apply to specific bucket** → enter `phoenix-omega-artifacts`
  (the bucket doesn't exist yet — that's fine; you can scope ahead)
- TTL: leave unset (perpetual; rotate annually via Pearl_INT)

Copy the **Access Key ID** + **Secret Access Key** immediately — Cloudflare
shows the secret only once.

### 2. Add to Codespaces secrets

Go to https://github.com/settings/codespaces → **New secret**:

| Name | Value |
|---|---|
| `CLOUDFLARE_ACCOUNT_ID` | the account ID from the dash URL |
| `CLOUDFLARE_API_TOKEN` | a Workers + R2 token (separate from access keys above) |
| `R2_ACCESS_KEY_ID` | from step 1 |
| `R2_SECRET_ACCESS_KEY` | from step 1 |

Make all four available to **this repository** (not all-repos unless you
want them everywhere). Codespaces injects them as env vars on next session.

### 3. Run the setup script (from a Codespace)

```bash
bash scripts/artifacts/setup_r2.sh
```

Idempotent. Creates the bucket if missing, applies CORS for direct upload
from Codespaces (`*.github.dev`), applies the lifecycle rules from the
config (`qa_runs/` 30d expire, `tmp/` 1d expire). Safe to re-run.

### 4. Smoke test

```bash
# List (should be empty initially)
python scripts/artifacts/r2_sync.py ls --namespace tmp --head 5

# Push
mkdir -p /tmp/r2-smoke && echo "hello $(date)" > /tmp/r2-smoke/test.txt
python scripts/artifacts/r2_sync.py push \
  --namespace tmp \
  --src /tmp/r2-smoke/ \
  --run-id smoke-$(date +%s)

# Pull (should be cache-hit on the manifest just written)
python scripts/artifacts/r2_sync.py pull \
  --manifest artifacts/manifests/tmp/...yaml
```

## Daily usage

### Pushing artifacts

```bash
python scripts/artifacts/r2_sync.py push \
  --namespace manga_rendered_books \
  --src out/rendered/anxiety_series/ep_001/ \
  --series-id stillness_press__anxiety \
  --book-id ep_001 \
  --manifest artifacts/manifests/manga_rendered_books/anxiety_series/ep_001.yaml
```

`r2_sync.py` walks the source dir, hashes each file, uploads to R2, and
writes a manifest YAML conforming to `manifest.schema.json`. The manifest
is what you commit to the repo.

### Pulling for downstream work (e.g. uploader, dashboard render)

```bash
python scripts/artifacts/r2_sync.py pull \
  --manifest artifacts/manifests/manga_rendered_books/anxiety_series/ep_001.yaml
```

Pulls into `artifacts/r2_cache/<manifest_id>/` (gitignored). Skips files
whose local sha256 already matches the manifest — re-running is fast.

### Verifying

```bash
python scripts/artifacts/r2_sync.py verify \
  --manifest artifacts/manifests/.../ep_001.yaml
```

Confirms every artifact in the manifest exists in R2 with matching size.
Used by CI before catalog publishing runs.

## What CI enforces

`.github/workflows/no-binary-blobs.yml` runs on every PR to `main`:

- Lists files **added** in the PR (not modifications)
- Skips allowlisted paths: `tests/fixtures/`, `docs/img/`, `skills/*/img/`
- For non-allowlisted files >1 MB: heuristic binary detection (NUL byte in
  first 8 KB, or known binary extension)
- If any oversized binary added → CI fails with the exact `r2_sync.py push`
  command needed to fix it

## Out of scope here (Layer 3)

- **Pearl Star → R2 push.** The render pipeline at `scripts/manga/render_*.py`
  needs a post-step that calls `r2_sync.py push` after each book renders.
  That's Layer 3 — also adds the `~/.phoenix_omega_pearl_star` marker so
  `assert_remote.py` accepts the rig.
- **Existing artifacts migration.** If you have rendered books already on
  the laptop (e.g. from the draft-profile QA run in
  `restore-first-100-qa-wrapper-20260425`), Pearl_INT can write a
  one-shot migration script after this PR lands.

## Free-tier budget tracking

R2 free tier:

| Metric | Free | Phoenix Omega target |
|---|---|---|
| Storage | 10 GB | ≤ 6.5 GB |
| Class A ops (writes, lists) | 1M/mo | ≤ 100k/mo |
| Class B ops (reads, heads) | 10M/mo | ≤ 500k/mo |
| Egress | $0 | $0 (R2 doesn't charge egress) |

A daily nightly catalog regen at 132 series × 10 panels = 1320 writes/day
= ~40k writes/mo. Comfortably inside free tier.

## Security

- R2 access keys are **bucket-scoped** to `phoenix-omega-artifacts` only.
  A leaked key cannot read other Cloudflare resources.
- Bucket is **private** by default (no public listing). Use signed URLs
  for one-off public sharing (`r2_sync.py sign-url --key ... --ttl 3600`
  — to be added in Layer 3).
- `r2_sync.py` calls `assert_remote()` and refuses to run on a local
  laptop unless `PHOENIX_OMEGA_REMOTE=local-override` (Layer 1 chokepoint).

## Related

- `CLAUDE.md` § API Keys & Credentials
- `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` § Cloudflare
- `docs/CLOUD_NATIVE_AGENTS.md` (Layer 1)
- `skills/pearl-int/SKILL.md` (integration ownership)
