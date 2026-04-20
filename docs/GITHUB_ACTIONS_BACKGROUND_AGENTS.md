# GitHub Actions background agents (manga lane)

Pearl Star workloads use a **self-hosted** runner labeled `pearl-star-gpu`. Register the runner against this repository (or the org) in GitHub → **Settings → Actions → Runners → New self-hosted runner**, then start `run.sh` on the Pearl Star host. Apply the labels `self-hosted` and `pearl-star-gpu` so workflows in `.github/workflows/manga-smoke-test.yml` and `weekly-manga-rollout.yml` can schedule.

Optional operator env on the runner: `$HOME/.config/pearl-star/operator.env` (sourced by workflows) for `COMFYUI_URL`, `PEARL_STAR_IP`, and local paths.

Related governance: see `docs/GITHUB_GOVERNANCE.md` and the **Verify governance** job (`github-governance-check.yml`). Do not bypass ruleset **Protect main** (required checks include **Core tests** and governance verifiers).

## Operator cheat sheet (`gh workflow run`)

```bash
gh workflow run manga-operator-setup-verify.yml

gh workflow run manga-smoke-test.yml \
  -f brand=stillness_press -f topic=anxiety -f genre=shojo \
  -f persona=gen_z_professionals -f chapter_count=12 -f backend=replay

gh workflow run manga-series-pitch.yml \
  -f brand=stillness_press -f topic=grief -f genre=seinen -f persona=gen_z_professionals

gh workflow run manga-character-sheet-build.yml \
  -f series_id=the_garden_at_tidecalm -f character_ids=hana,mother,neighbor

gh workflow run manga-quality-forensic-analysis.yml

gh workflow run weekly-manga-rollout.yml -f dry_run=true

gh workflow run manga-fonts-acquire.yml
```

Inspect runs:

```bash
gh run list --workflow=manga-smoke-test.yml
gh run view <id>
gh run download <id>
gh issue list --label operator-action-required
gh pr list --label agent-generated --state open
```

## Required secrets (names only)

| Secret | Used by |
| --- | --- |
| `GITHUB_TOKEN` | implicit |
| `CF_R2_ACCESS_KEY`, `CF_R2_SECRET_KEY` | weekly rollout, R2 uploads |
| `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_ACCOUNT_ID`, `R2_BUCKET` | weekly rollout (legacy S3-compatible vars) |
| `SENDGRID_API_KEY` | weekly digest / failure email |
| `CLAUDE_API_KEY` | forensic + series pitch (optional until wired) |
| `RUNCOMFY_TOKEN` | RunComfy / hybrid backends |
| `COMFYUI_URL` or `PEARL_STAR_IP` | Pearl Star health checks on GPU workflows |

Repository **Variables** (non-secret): e.g. `WEEKLY_ROLLOUT_OPERATOR_EMAIL`, `COMFYUI_URL` if preferred as variable.
