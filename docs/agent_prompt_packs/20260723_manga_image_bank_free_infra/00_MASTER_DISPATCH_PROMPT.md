# MASTER DISPATCH — Manga Image Bank on Free Infra (1 series/brand × 5 locales)

Paste this whole file into the lead agent chat. It runs two lanes **in sequence**
(lane 2 depends on lane 1's verified findings) — do not skip straight to lane 2.

## Why this pack exists

The operator asked for: (1) verification that the free/local image-gen stack
actually works, and (2) a spec + plan (not a build) for the full manga image
bank — one series per brand, rendered for `en_US` (us_eng), `ja_JP` (japan),
`zh_TW` (taiwan), `zh_CN` (china), `fr_FR` (france) — using only free
infrastructure (Pearl Star / ComfyUI / open-weight models), never paid image
APIs, staying inside whatever "free limits" exist.

This is **Milestone M5** of the already-ratified
`docs/specs/MANGA_100PCT_PRODUCTION_ROADMAP_2026-07-03.md` (§5, "R5 banks +
assembly at scale, GPU begins") — extended from its native en_US/ja_JP/zh_TW
scope to 5 locales. It is not a new parallel system: it must build on
`scripts/manga/assemble_from_bank.py` (canonical, do not fork), the V4/V5
layer-render specs, and RAP queue-first GPU dispatch. Neither of these lanes
authors manga story content, trains anything, or spends real GPU-hours beyond
one smoke-test image — that is explicitly out of scope until the operator
reads the plan produced by Lane 2 and green-lights a pilot.

## EXECUTE

Do not stop at "plan the plan," "read the docs and summarize," or "here's what
I'd do." Run Lane 1 to completion (verified PASS/FAIL, not "should work"), then
run Lane 2 using Lane 1's actual findings. Land Lane 2's output as a
docs-only PR. Do not merge it yourself — open it and report the PR number.

## Lanes

1. `01_VERIFY_FREE_MODEL_INFRA_PROMPT.md` — smoke-test Pearl Star/ComfyUI,
   confirm `flux1-schnell-fp8` is the resident checkpoint (never
   `flux1-dev`, which is license-banned for commercial use), confirm RAP
   queue-first single-image dispatch produces a real PNG, confirm PuLID/LoRA
   node install state, confirm zero paid-path (RunComfy) usage.
2. `02_IMAGE_BANK_SPEC_AND_PLAN_PROMPT.md` — using Lane 1's verified findings,
   author the spec + smoke→pilot→scale plan for the 37-brand × 5-locale image
   bank. Deliverable is a **document**, not rendered images.

## Non-negotiables carried into both lanes

- **RAP queue-first only** (`docs/ROBUST_AGENT_PROTOCOL.md`): never call
  ComfyUI directly via Bash for >10s work. Use `pscli enqueue` /
  `pscli inspect` / `pscli status`. One image per queue job — never bundle.
- **Reuse-first**: `assemble_from_bank.py`, `render_v5_episode.py`, `pscli` are
  canonical (`artifacts/coordination/CANONICAL_ARTIFACTS_REGISTRY.tsv`). Edit
  or extend; do not fork.
- **Free-only, no exceptions**: RunComfy is decommissioned by operator order
  2026-06-13 (`docs/INTEGRATION_CREDENTIALS_REGISTRY.md:77`). Do not re-enable
  it, do not call any paid image API, regardless of what any stale doc implies.
- **Layer-honest reporting**: label every status claim with the six-layer
  taxonomy (`ABSENT → RESEARCHED → SPECCED → CONFIG-EXISTS → CODE-WIRED →
  EXECUTED-REAL → PROVEN-AT-BAR`) per CLAUDE.md's manga doctrine. A rendered
  PNG that exists is EXECUTED-REAL, not "done"; nothing manga-wide is
  PROVEN-AT-BAR today (no blind-judge pass has ever run) — do not claim it.
- **Live-truth over memory**: several facts below are dated and one is
  self-contradictory (see Lane 2 §"known contradiction to resolve"). Re-verify
  against current `origin/main` before building the plan on it.

## STARTUP_RECEIPT (both lanes, before touching anything)

```
git branch --show-current
git status --short
git fetch origin
git rev-list --left-right --count origin/main...HEAD
PYTHONPATH=. python3 scripts/git/push_guard.py
scripts/ci/preflight_push.sh
bash scripts/git/health_check.sh
PYTHONPATH=. python3 scripts/ci/check_rap_compliance.py
```

If the working tree is dirty with unrelated state (this repo's shared
directory often carries other sessions' uncommitted files — confirmed true as
of 2026-07-23), branch fresh off `origin/main` and build your changes via git
plumbing (temp index off `origin/main^{tree}`) rather than `git add -A`.

## CLOSEOUT_RECEIPT (required, both lanes)

Full commit SHA, PR URL or "LANDED-OFFLINE" reason, exact file list touched,
signal token `<signal>=<full-SHA>`, and — for Lane 2 specifically — a new row
appended to `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` for this
workstream (none exists yet; confirmed by research this session).
