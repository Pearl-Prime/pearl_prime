# Cloud-Native Agents Layer 3 — Pearl Star push + render integration

**Status:** Layer 3 active (this PR).
**Predecessors:** [Layer 1](./CLOUD_NATIVE_AGENTS.md) (PR #633), [Layer 2](./CLOUD_NATIVE_AGENTS_LAYER2.md) (PR #635).
**Stack:** complete after this — laptop disk safe, repo disk safe, render-host pushes canonical.

## Why

After Layers 1 + 2, your laptop and repo are protected from growth. But
the FLUX renders still produce binary artifacts on Pearl Star's local
disk (~50 MB per book × 132 series × ~10 books = 66 GB). Without Layer 3
they sit there until someone manually moves them, and downstream consumers
(Codespaces uploaders, dashboard renderers) can't reach them.

Layer 3 closes the loop:

- **Pearl Star marker** → `assert_remote.py` accepts the rig as a remote.
- **Reusable Python push helper** → render scripts call one function and
  the output is in R2 with a manifest committed back.
- **Migration helper** → one-shot script for the existing 96 rendered
  books (the draft-profile QA run living in
  `restore-first-100-qa-wrapper-20260425`).
- **Signed-URL CLI** → time-limited public links to single artifacts for
  manual review (KDP submission, owner spot-checks).

## What ships in this PR

| File | Purpose |
|---|---|
| `scripts/agent/install_pearl_star_marker.sh` | Idempotent installer that creates `~/.phoenix_omega_pearl_star`. Refuses to run on a host that doesn't look like Pearl Star (no RTX 5070+, hostname mismatch) without `--force`. |
| `scripts/artifacts/r2_push_helper.py` | Reusable Python module. Four typed entry points (`push_book_render`, `push_character_portraits`, `push_qa_run`, `push_brand_asset`) plus `sign_url`. Plus a generic `push_directory`. |
| `scripts/artifacts/migrate_local_books_to_r2.py` | One-shot migration for the 96 books from the draft-profile QA run. Auto-discovers `<root>/<series_id>/<book_id>/` layout. Dry-run mode. |
| `docs/CLOUD_NATIVE_AGENTS_LAYER3.md` | This doc. |

## Pearl Star setup (one-time)

SSH to the rig and run the installer:

```bash
ssh pearlstar.tail7fd910.ts.net
cd /path/to/phoenix_omega
git pull origin main
bash scripts/agent/install_pearl_star_marker.sh
```

The installer:
1. Confirms the host has an RTX 5070+ via `nvidia-smi` or hostname matches `pearlstar*`.
2. Creates `~/.phoenix_omega_pearl_star` (chmod 600) with a created-at stamp.
3. Re-runs `assert_remote.py` to verify it now reports `pearl-star`.

If you're SSH'd into a host that *should* be Pearl Star but auto-detection
fails (e.g. nvidia-smi missing during driver install, custom hostname), pass
`--force`.

## Pearl Star runtime — credential loading

Once the marker is in place, render scripts on Pearl Star load R2
credentials from the existing macOS Keychain bridge (per `CLAUDE.md`):

```bash
eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
python3 scripts/manga/render_book.py ... # now has CLOUDFLARE_ACCOUNT_ID etc.
```

The integration env registry at `scripts/ci/integration_env_registry.py`
already lists `CLOUDFLARE_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`,
`R2_SECRET_ACCESS_KEY` — Pearl_INT manages them.

## How render scripts call the helper

**Before (today):** rendered files sit in a local out-dir.

```python
out_dir = Path(f"out/rendered/{series_id}/{book_id}")
render_pages(out_dir)
# … files just stay there
```

**After:** add one import + one call.

```python
from scripts.artifacts.r2_push_helper import push_book_render

out_dir = Path(f"out/rendered/{series_id}/{book_id}")
render_pages(out_dir)

manifest_path = push_book_render(
    out_dir=out_dir,
    series_id=series_id,
    book_id=book_id,
)
# manifest_path = artifacts/manifests/manga_rendered_books/<series_id>/<book_id>.yaml
# binary blobs are now in R2; commit the manifest.
```

The helper handles sha256, content-type, manifest schema validation, and
R2 upload. Failures raise `R2PushError` with actionable messages
(missing creds → URL to Cloudflare dash; bad manifest → schema error).

## Migrating existing renders

The `restore-first-100-qa-wrapper-20260425` worktree on the laptop has
96 rendered books. To move them to R2:

```bash
# From a Codespace (don't run on the laptop — disk is tight)
# First, copy or rsync the worktree contents into the Codespace, or
# work directly on Pearl Star where they may also live.

# Dry-run first to verify discovery:
python3 scripts/artifacts/migrate_local_books_to_r2.py \
  --root path/to/qa_books/ \
  --dry-run

# Then push for real:
python3 scripts/artifacts/migrate_local_books_to_r2.py \
  --root path/to/qa_books/

# Commit the generated manifests:
git add artifacts/manifests/manga_rendered_books/
git commit -m "feat(qa): migrate draft-profile 96-book run manifests to R2"
```

After migration the books exist in R2 under `manga/rendered_books/...`
with one manifest YAML per book in the repo.

## Signed URLs (manual review)

Need to hand a reviewer a single link to a rendered cover or QA epub?

```bash
python3 scripts/artifacts/r2_push_helper.py sign-url \
  --key manga/rendered_books/stillness_press__anxiety/ep_001/cover.png \
  --ttl 3600

# → https://<account>.r2.cloudflarestorage.com/...?X-Amz-Signature=...
```

Default TTL 1 hour; configurable via `--ttl` (max recommended 7 days).

## What this completes

After Layer 3 the cloud-native migration is done:

| Pain point | Solved by |
|---|---|
| Laptop fills up on `.claude/worktrees/` | Layer 1 (Codespaces) |
| Repo grows when binaries committed | Layer 2 (R2 + no-binary-blobs CI) |
| Pearl Star renders never reach R2 | Layer 3 (push helper) |
| Existing renders stuck on laptop | Layer 3 (migration script) |
| Reviewer needs link to one render | Layer 3 (sign-url) |

## Out of scope (future work)

- **Wiring the helper into specific render scripts.** This PR provides
  the helper; rewriting each render entry point to call it is a
  per-pipeline follow-up (manga renders, QA runs, podcast audio,
  videoboard). Each follow-up is a 5-line change.
- **Auto-rotating R2 access keys.** Pearl_INT handles this manually for
  now; an automated rotation workflow can come later.
- **Public-bucket fork.** If you decide to publish R2-hosted thumbnails
  publicly (e.g. for the brand microsite), that's a separate bucket
  with `public: true` — not the canonical artifacts bucket.

## Related

- `docs/CLOUD_NATIVE_AGENTS.md` — Layer 1
- `docs/CLOUD_NATIVE_AGENTS_LAYER2.md` — Layer 2
- `scripts/agent/assert_remote.py` — the chokepoint
- `scripts/artifacts/r2_sync.py` — CLI sibling of r2_push_helper.py
- `skills/pearl-int/SKILL.md` — credential ownership
- `CLAUDE.md` — LLM Tier Policy (this PR honors it; no LLM calls)
