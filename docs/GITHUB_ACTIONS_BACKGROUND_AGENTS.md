# GitHub Actions background agents

Operator reference for the six new workflows in `.github/workflows/` that
move long-running pipeline tasks off the laptop and into GitHub Actions.

## Workflows

| File | Trigger | Runner | Timeout | Purpose |
|---|---|---|---|---|
| `book-flagship-qa-ladder.yml` | `workflow_dispatch` | ubuntu-latest | 180m | Run the spine pipeline across all runtime formats at the flagship quality profile; upload reports as artifacts. |
| `single-book-smoke.yml` | `workflow_dispatch` | ubuntu-latest | 60m | One-off brand × topic × persona × format smoke test. |
| `weekly-book-rollout.yml` | `workflow_dispatch` + weekly Sun 06:00 UTC | ubuntu-latest | 720m | Matrix over brands × topics × formats; writes per-combination reports. |
| `manga-pipeline.yml` | `workflow_dispatch` | self-hosted `pearl-star-gpu` | 360m | Manga chapter render (ComfyUI + panel gen). Requires GPU. |
| `nightly-regression.yml` | `workflow_dispatch` + daily 03:00 UTC | ubuntu-latest | 180m | Full pytest + governance + readiness gate on `main`. |
| `pearl-star-health.yml` | `workflow_dispatch` + every 30m | ubuntu-latest | 10m | Heartbeat: checks `pearl-star-gpu` runner registration + status. |

## Trigger examples (gh CLI)

```bash
# Flagship QA ladder (default params — anxiety / gen_z_professionals / 7 formats)
gh workflow run book-flagship-qa-ladder.yml

# Flagship QA ladder with custom topic/persona/arc
gh workflow run book-flagship-qa-ladder.yml \
  -f topic=grief \
  -f persona=millennial_women_professionals \
  -f arc=millennial_women_professionals__grief__watcher__F006.yaml

# Single book smoke (fast sanity check)
gh workflow run single-book-smoke.yml \
  -f topic=anxiety -f persona=gen_z_professionals \
  -f arc=gen_z_professionals__anxiety__overwhelm__F006.yaml \
  -f runtime_format=standard_book -f quality_profile=draft

# Weekly rollout (multi-brand)
gh workflow run weekly-book-rollout.yml \
  -f brands="gen_z_professionals corporate_managers" \
  -f topics="anxiety grief" \
  -f formats="standard_book deep_book_4h"

# Manga pipeline (GPU required)
gh workflow run manga-pipeline.yml \
  -f brand=gen_z_professionals -f topic=anxiety \
  -f genre=shonen -f chapter_count=3

# Nightly regression (manual invocation)
gh workflow run nightly-regression.yml

# Health probe (manual ping)
gh workflow run pearl-star-health.yml
```

Results appear in the Actions tab, with GitHub Step Summary at the top of
each run. Artifacts are uploaded at the end of every run and retained for
30–90 days depending on workflow.

## Required GitHub secrets

Configure via **Settings → Secrets and variables → Actions → New repository secret**.

| Secret | Used by | Required for |
|---|---|---|
| `RUNCOMFY_TOKEN` | `manga-pipeline.yml` | ComfyUI API access |
| `CF_R2_ACCESS_KEY` | `manga-pipeline.yml` | Cloudflare R2 asset upload |
| `CF_R2_SECRET_KEY` | `manga-pipeline.yml` | Cloudflare R2 asset upload |
| `SENDGRID_API_KEY` | (future) failure notifications | Email alerts |
| `DASHSCOPE_API_KEY` | Qwen / Pearl Star flows | Atom translation / fill |
| `ELEVENLABS_API_KEY` | Audiobook / podcast flows | TTS generation |

`GITHUB_TOKEN` is provided automatically by Actions — no setup required.

## Self-hosted runner (`pearl-star-gpu`)

The `manga-pipeline.yml` workflow is pinned to `runs-on: [self-hosted, pearl-star-gpu]`
and requires a registered runner with that label to be online.

### Verify runner is registered

```bash
gh api /repos/Ahjan108/phoenix_omega_v4.8/actions/runners \
  --jq '.runners[] | select(.labels[].name=="pearl-star-gpu")'
```

If this returns nothing, the operator must register the runner on the Pearl Star
machine following the standard GitHub self-hosted runner setup:

1. **Settings → Actions → Runners → New self-hosted runner**
2. Select Linux x64
3. Run the install / configure / run commands GitHub provides
4. When prompted for labels, add: `pearl-star-gpu`
5. Start the runner as a service so it survives reboots:
   ```bash
   sudo ./svc.sh install
   sudo ./svc.sh start
   ```

### Health monitoring

`pearl-star-health.yml` fires every 30 minutes:
- If no runner with the `pearl-star-gpu` label is registered → warning only.
- If the runner is offline during 06:00–22:00 UTC operating hours → job fails.

The failure surfaces in the Actions tab as a red run; if the operator has
configured GitHub notifications for workflow failures, they will be notified
by email automatically (GitHub Settings → Notifications).

## Scoping

These workflows are additive. They do **not** replace:
- `core-tests.yml` (runs on every PR)
- `github-governance-check.yml` (ruleset required)
- Any existing pipeline workflow (`catalog-book-pipeline.yml`, `manga-image-gen.yml`, etc.)

Tasks that already have coverage (Core tests on PR, weekly catalog builds, etc.)
continue via their existing workflows. These six new workflows fill the gap
for operator-dispatched long-running tasks.
