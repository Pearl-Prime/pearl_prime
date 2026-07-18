# Phoenix Omega — GitHub Operations Entry

This branch is explicitly wired for **Pearl_GitHub**, the repo-native GitHub
operations agent.

## LLM Tier Policy (MANDATORY — read before touching any LLM code)

**Tier 1 — Claude Code (subscription, operator-present):**
- All refactors, features, analysis, research, prose generation (bestseller chapters, manga scripts)
- Any task where a human will review the output before it ships

**Tier 2 — Gemma (English) / Qwen (CJK6) on Pearl Star via Ollama (free, unattended):**
- Scheduled pipelines only: weekly manga rollout, nightly regression, Pearl News daily, brand digest
- Any pipeline step that fires when no operator is present

**BANNED — paid LLM APIs (enforced by `.github/workflows/llm-policy-enforcement.yml`):**
- `ANTHROPIC_API_KEY` / `CLAUDE_API_KEY` reads in repo code
- OpenAI cloud, Google AI, DashScope cloud, Together, Replicate, Perplexity, Cohere, Mistral paid
- Violations block PRs. Run `python3 scripts/ci/audit_llm_callers.py` before pushing.

## API Keys & Credentials — READ THIS FIRST

All credentials are documented in `docs/INTEGRATION_CREDENTIALS_REGISTRY.md`. Read it before touching any API.

**Critical URLs (DO NOT guess or Google these):**
- **Qwen/DashScope:** `https://modelstudio.console.alibabacloud.com/ap-southeast-1#/api-key` — **SINGAPORE ONLY. Beijing is WRONG.**
- **RunComfy:** `https://www.runcomfy.com/profile` → API Tokens
- **ElevenLabs:** Key is in `docs/11.txt` (gitignored) or Keychain

**Load all tracked integration env vars from macOS Keychain** (single source of truth: `scripts/ci/integration_env_registry.py`, same list as `scripts/ci/check_integration_env.py`):

```bash
eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
```

Diagnostics: `python3 scripts/ci/load_integration_env_from_keychain.py --count` (how many names are tracked), `--list` (names only), `--verbose` (stderr notes for missing Keychain items while still emitting exports on stdout).

## Read First

Read these files in order before doing any git or GitHub work:

1. `docs/PROGRAM_STATE.md`
2. `ps.txt`
3. `docs/PEARL_GITHUB_ONBOARDING.md`
4. `skills/pearl-github/SKILL.md`
5. `skills/pearl-github/references/git_system.md`
6. `skills/pearl-github/references/repo_memory.md`
7. `docs/GITHUB_OPERATIONS_FRAMEWORK.md`
8. `docs/GITHUB_GOVERNANCE.md`
9. `docs/BRANCH_PROTECTION_REQUIREMENTS.md`
10. `docs/GITHUB_GOVERNANCE_INCIDENT_RUNBOOK.md`
11. `docs/DOCS_INDEX.md`
12. `docs/AGENT_FILE_PERSISTENCE_PROTOCOL.md`

## Bestseller Quality Anti-Drift Doctrine (MANDATORY — Pearl_Prime sessions)

Read `docs/BESTSELLER_DRIFT_ROOT_CAUSE_2026-07-02.md` and
`docs/PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md` before any Pearl Prime
bestseller / catalog render work.

1. **gate-PASS ≠ bestseller** — NEVER report a book as bestseller or shippable on
   `register_gate` PASS alone. Name the acceptance layer every time: `structurally clear`
   (Layer 1) / `authored candidate` (Layer 2) / `system working` (Layer 3) /
   `bestseller register` (Layer 4 blind-10). `register_gate` PASS is at most
   `structurally clear`.

2. **Composer is NOT the flagship-register lever** — the same atoms hand-seamed already
   read as bestseller. Do NOT re-tune the composer for catalog-scale register; that
   instinct IS the drift. Flagship register = the **line-edit lane** (Layer 3 ONTGP on
   canonical flagship cells).

3. **Meta-rule: memory is recall, not enforcement** — every hard-won quality/drift lesson
   must be promoted to an enforced mechanism: a **CI hard gate** (e.g. F14 beat-line
   ceiling), a **can't-bypass default** (four-piece chord on production builds), or a
   **CLAUDE.md rule** — NOT left in memory or tribal docs alone.

Production bestseller builds MUST use the four-piece chord:
`--pipeline-mode spine --quality-profile production --exercise-journeys`.
CI blocks incomplete chords in changed production invocations (`check_canonical_pipeline_path.py`).
This gate is a **required status check** ("Drift detectors") — a chord-incomplete
production `run_pipeline.py` invocation in a changed file **cannot merge**. If your PR
touches a run_pipeline invocation that is legitimately NOT a bestseller build (a smoke
test, a `--quality-profile draft` queue, a QA harness, or a prose/docstring reference —
not an executed build), mark it with a same-or-preceding-line comment
`# CI-ALLOWLIST: legacy-registry-ok — <reason>` to exempt that block. Do NOT weaken the
gate to pass; fix real bestseller builds by adding the missing chord flags.

## Manga Vision-Conformance Doctrine (MANDATORY — Pearl manga sessions)

Read `artifacts/qa/MANGA_VISION_CONFORMANCE_AUDIT_2026-07-03.md` (the honest
baseline) and `docs/specs/MANGA_100PCT_PRODUCTION_ROADMAP_2026-07-03.md` (the
routed plan) before any manga certification, catalog, story, bank, or render
work.

1. **Six-layer acceptance taxonomy — label every manga status claim.** Never
   report a manga axis, series, or asset as "done", "working", "ready", or
   "shippable" without naming the layer it has actually reached:
   `ABSENT → RESEARCHED → SPECCED → CONFIG-EXISTS → CODE-WIRED → EXECUTED-REAL →
   PROVEN-AT-BAR`. A config that exists is CONFIG-EXISTS, not working. A gate
   PASS is not the pro bar. Only a byte-verified artifact is EXECUTED-REAL; only
   a blind-judged sample is PROVEN-AT-BAR (nothing is, today).

2. **Three drift classes are now CI-enforced — do not weaken the gates to pass.**
   These are wired into the **Drift detectors** required check and
   `scripts/run_production_readiness_gates.py` (gates 21–23):
   - **stub-as-done** → `check_render_progress_bytes.py`: a RENDER_PROGRESS.tsv
     row marked `ok/done` with `bytes < 50_000` (or a missing image under
     `--require-images`) **cannot merge**. Fix by rendering real panels, never by
     editing the byte column.
   - **listing-as-story** → `check_manga_story_authored.py`: a (series, episode)
     cannot enter the render queue without an authored `chapter_script_writer_handoff`
     that has ≥ 6 authored panels and no stub markers. A `series_plan` is a
     listing, not a story. Import `assert_story_authored()` at any new render
     dispatch site.
   - **unwired-config-as-working** → `check_manga_wiring.py`: a new
     `config/manga/*.yaml` with no non-test consumer must carry `status: unwired`
     or a `KNOWN_UNWIRED` entry with a reason. Do not add a config and report the
     feature as working — wire it or declare it unwired.

3. **Layered assembly, never single-shot pages.** Panels are assembled
   deterministically from banked layers via `scripts/manga/assemble_from_bank.py`
   (spec `MANGA_LAYER_RENDER_CONTRACT_SPEC.md` §4/§10, `MANGA_V5_LAYERED_ARCHITECTURE.md`
   §7). Every layer in a manifest carries `provenance: REAL|INTERIM`; an INTERIM
   layer is a labeled stand-in and is **never** presented as final art. Do not
   ship a text-to-image single-shot page as a "layered" panel.

## Pearl_GitHub Scope

Pearl_GitHub owns:

- branch creation
- commit hygiene
- push safety
- pull request readiness
- push-guard compliance
- CI workflow awareness
- branch protection awareness
- hourly repo health checks
- recovery from wrong-base branches, stuck cherry-picks, and blocked pushes
- file persistence enforcement (see `docs/AGENT_FILE_PERSISTENCE_PROTOCOL.md`)

## Non-Negotiable Git Rules

0. **NEVER merge a PR that deletes more than 50 files without explicit owner approval.** Before merging ANY PR, check the diff size: `gh pr diff <number> --stat | tail -1`. If it shows deletions > 50, STOP and ask the user. PR #245 deleted 20,006 files and cost hundreds of hours to recover.
1. Always branch from `origin/main`
2. Never branch from `codex/*` or another local branch for agent work
3. Never push without running push-guard and preflight
4. Never guess branch state; check first
5. Keep scope small enough for push-guard and PR review
6. Never report "done" without a commit SHA or full file dump in CLOSEOUT_RECEIPT

## Mandatory Preflight

Run before any branch, commit, push, PR, merge, or recovery action:

```bash
git branch --show-current
git status --short
git fetch origin
git rev-list --left-right --count origin/main...HEAD
PYTHONPATH=. python3 scripts/git/push_guard.py
scripts/ci/preflight_push.sh
bash scripts/git/health_check.sh
PYTHONPATH=. python3 scripts/ci/check_rap_compliance.py
```

**RAP (Robust Agent Protocol):** Before any Pearl Star GPU/LLM work (>10s), read
`docs/ROBUST_AGENT_PROTOCOL.md`. Queue-first dispatch via `pscli` is mandatory;
`check_rap_compliance.py` warns on direct ComfyUI/Ollama bypass patterns.

## Automated PR Governance (Pearl_PM + Pearl_Architect gate)

Every PR to main is automatically reviewed by the governance CI workflow.
It checks:
- **Mass deletion** — blocks PRs deleting >50 files
- **PR size** — warns on >200 files, blocks >500
- **Subsystem scope** — warns if PR touches >3 subsystems
- **Authority docs** — warns if subsystem authority docs are missing
- **Drift patterns** — warns on duplicate specs, root-level files, etc.
- **Workstream conflict** — warns if PR overlaps with active workstreams

The review posts a comment on the PR with a pass/warn/block verdict.
**PRs with BLOCKED status cannot be merged** (enforced by GitHub ruleset).
**Western skeleton batch freeze:** when `config/governance/skeleton_freeze.yaml` → `active: true`, `pr_governance_review.py` BLOCKs `feat(catalog): {locale} skeletons {brand} batch {N}` PRs (CJK locales excluded; title-only matcher — see marker doc).

### Manual pre-merge check (run locally before pushing)

```bash
bash scripts/git/pre_merge_check.sh <PR_NUMBER>
python3 scripts/ci/pr_governance_review.py
```

If either blocks, do NOT merge. Ask the owner.

## Golden Branch Pattern

```bash
git fetch origin
git checkout -b agent/<task-summary> origin/main
```

If push-guard blocks because the base branch was wrong:

```bash
git fetch origin
git checkout -b agent/<task-summary>-clean origin/main
git cherry-pick <commit>
git push -u origin agent/<task-summary>-clean
```

## Hourly Checklist

Run:

```bash
bash scripts/git/health_check.sh
```

Use it at session start, before every push, and hourly during active repo work.

## Known-good anchors (high-drift subsystems)

Append-only registry of last-known-good SHAs/PRs per high-drift subsystem. Start here, restore by `git checkout`, do not re-author. Mirror of `~/.claude/projects/-Users-ahjan-phoenix-omega/memory/project_known_good_anchors.md`.

### Pearl News sidebar (5-card system + interactive layer)

- **Canonical PR:** #853 (`8070e81fd`) — feat(pearl_news): five-layout sidebar system + --layout CLI + governing spec
- **Composite chain (6 SHAs):** see `docs/PEARL_NEWS_SIDEBAR_VERSION_HISTORY.md` §16
- **Function inventory (F1–F5 + INFRA):** `docs/PEARL_NEWS_SIDEBAR_FUNCTION_INVENTORY.md`
- **Canonical snapshot (gold master):** `artifacts/pearl_news/snapshots/CANONICAL_SIDEBAR.html`
- **Metadata + fingerprints:** `artifacts/pearl_news/snapshots/CANONICAL_SIDEBAR_METADATA.json`
- **CI parity gate:** `scripts/ci/check_pearl_news_sidebar_parity.py` (BLOCKS publish on drift; wired into `.github/workflows/pearl-news-daily.yml` + `scripts/run_production_readiness_gates.py` gate #19)
- **Regression test:** `tests/test_pearl_news_sidebar_parity.py`
- **Sidebar restoration protocol:** `docs/PEARL_NEWS_WRITER_SPEC.md` §S
- **Drift signal:** operator says "the sidebar is broken" / "you have text but no function" / "you keep dropping the sidebar" → DO NOT fresh-fix. Run the parity gate, read VERSION_HISTORY §16, restore by `git checkout <sha> -- <path>`.

## When In Doubt

- Read `skills/pearl-github/SKILL.md`
- Read `skills/pearl-github/references/repo_memory.md`
- Read `docs/GITHUB_OPERATIONS_FRAMEWORK.md`
- Read `docs/GITHUB_GOVERNANCE.md`
- For browser or Colab tasks, verify visible outputs before claiming completion; keystroke automation alone is not proof. See `docs/COLAB_AND_BROWSER_VERIFICATION_RUNBOOK.md`
- Stop and verify rather than improvising
