# Social media audit landing wave — 2026-07-23

**Status:** LANDED (3 PRs merged to `origin/main`). Two items remain open, both named below with
a concrete next step — read this doc before re-investigating either from scratch.

## How this started

Session began as a single narrow task: `scripts/integrations/metricool/post.py` raised
`ModuleNotFoundError` for `phoenix_v4.social.deterministic_social`, breaking the required "Core
tests" CI check on every PR. Investigation found the whole `phoenix_v4/social/` package existed
only as untracked local files — never committed anywhere in git history, despite already-landed
code (`scripts/integrations/metricool/__init__.py`'s docstring, `docs/PEARL_ARCHITECT_STATE.md`)
assuming it was real. Landing that one package uncovered a live sibling-PR collision (#53 vs #55)
and a wider social-media subsystem audit gap, which the operator then dispatched as a 3-lane
review (Pearl_GitHub / Pearl_Research / Pearl_PM). This doc is the closeout for all of it.

## What merged

1. **PR [#75](https://github.com/Pearl-Prime/pearl_prime/pull/75)** → `9bfb9867c0`
   `phoenix_v4/social/__init__.py`, `media_selector.py`, `config/social/platform_specs.yaml`,
   `words_bank.yaml`, `visual_registry.yaml`, `config/manga/main_character_interaction_grammar.yaml`,
   plus a `social_media` row in `SUBSYSTEM_AUTHORITY_MAP.tsv` and the stale
   `evergreen_social_atom_bank` registry row fix (`pending-PR` → real SHA). This fixed **two**
   confirmed `FileNotFoundError`s that were breaking `origin/main`'s own required Core-tests check
   for everyone, not just this PR — see "still open" below for the third one it uncovered.
2. **PR [#79](https://github.com/Pearl-Prime/pearl_prime/pull/79)** → `319161a236`
   `docs/specs/SOCIAL_MEDIA_100PCT_PRODUCTION_PLAN_2026-07-22.md` (six-layer acceptance taxonomy,
   10-item sequenced gap list, 3 `Q-SOCIAL-*` open questions), a new "Social Media Atom Bank"
   section in `docs/PROGRAM_STATE.md` (subsystem had zero row despite being active since
   2026-07-21), and a workstream row in `ACTIVE_WORKSTREAMS.tsv`.
3. **PR [#96](https://github.com/Pearl-Prime/pearl_prime/pull/96)** → `cf1512336e`
   Records operator approval of `Q-SOCIAL-VISUAL-LICENSE-APPROVAL-01` in
   `operator_decisions_log.tsv`. **Caveat logged in the row itself:** the underlying
   `artifacts/qa/deterministic_social_visual_gate_20260718/` TSVs and contact sheet were not
   present in this working tree, so `LIVE_PUBLISHING_AUTHORIZED` and the 405 render-row
   `production_ready` flags were **not** flipped by this PR — whoever holds those files needs to
   apply that flip using this OPD as authorization.

Research currency audit (Lane B, no PR needed — pure audit doc): `artifacts/qa/social_research_currency_audit_20260722/RESEARCH_CURRENCY_AUDIT.md`.
Key findings already folded into #79's plan doc: citations resolve (37/37 sampled) but 98.7% share
undifferentiated boilerplate refs; the "weekly" research refresh has run exactly once ever with
zero recurring mechanism; APAC native-review is backed by one operator chat-level assertion, not
per-row sign-off.

## Still open — do not re-diagnose from scratch, read this first

### 1. PRs #53 and #55 need owner reconciliation

Both predate #75 and independently tried to close the same missing-file gap; both got comments
pointing at #75 as the landed reconciliation point. Neither was merged or closed by this session
(no clear single owner to confirm with, and #53 in particular had accumulated unrelated bundled
content — manga/storyblocks-music/flagship-snapshot changes — from branch drift that shouldn't be
authored away blind). **Next step:** whoever owns those branches should rebase onto current
`origin/main` — the missing-file portion should disappear from both diffs entirely now that #75
is merged; only genuinely-unique content (e.g. #55's `book_engine_policy.py` work) should remain.

### 2. `tests/manga/test_story_excellence_gate.py::test_pass_fixtures[battle_en_us_genalpha]` fails on CI

This is the **next** thing blocking Core tests on `origin/main` after #75's two fixes. Confirmed
**deterministic**, not flaky (`gh run rerun --failed` reproduced identically). Strong evidence it
is **not** caused by #75's `config/manga/main_character_interaction_grammar.yaml` content:
- `_check_interaction`'s hard-fail logic for the `battle` genre doesn't consult that file's
  per-genre row (only a soft no-op `quality_gate_checks` check does).
- Manually traced the fixture's script text against the interaction-target keyword lists: both the
  `found_targets` check and the multi-speaker fallback should PASS.
- Calling `evaluate_story_excellence(...)` directly on the exact fixture, in an isolated Python
  process, returns `status=PASS, score=100`.
- `pytest tests/manga/ -m "not slow and not integration"` (561 passed) also didn't reproduce it.

Leading unconfirmed hypothesis: `phoenix_v4/manga/modern_reader_context.py` has a module-level
mutable `_CACHE` (`load_modern_reader_doctrine`, keyed only on whether `path is None`) that could
carry stale state across tests when the full ~900-test suite runs in one process — something no
isolated or partial run can reproduce. Checked `tests/manga/test_modern_reader_story_context.py`
(a plausible earlier-running culprit by alphabetical collection order) — **it isn't tracked on
`origin/main` at all**, so it can't be the cause on CI specifically; ruled out.

**Could not identify the actual triggering test.** This local working tree has pervasive drift
(multiple tracked files present locally in stale/truncated versions — `server/routes/brand_onboarding.py`,
`phoenix_v4/quality/register_gate.py`, `config/manga/gate_registry.yaml` all confirmed stale here
during this session) that makes a faithful full-suite-against-real-`origin/main` repro impossible
from this checkout. **Next step:** someone with a clean `origin/main` checkout should run
`pytest tests/ -m "not slow and not integration" -x` directly and bisect forward from there (e.g.
`git bisect` across which test immediately preceding it in collection order, when commented out,
makes it pass).

## Working-tree hygiene note (not this session's job, flagging for visibility)

This checkout (`/Users/ahjan/phoenix_omega`, currently on `agent/bestseller-atom-flow-lanes-20260721`)
has extensive drift from `origin/main`: dozens of untracked stray files/test modules from other
concurrent sessions, and — more concerning — several *tracked* files present locally in stale or
truncated versions relative to what's actually merged. All landings in this doc were built via
plumbing commits based fresh off `origin/main` (never this working tree's state) specifically to
route around that drift; anyone continuing work here should verify file content against
`git show origin/main:<path>` before trusting local disk, and expect `git worktree add` / full
checkouts to time out at this repo's ~287k-file scale (use the plumbing-commit pattern instead).

## CLOSEOUT_RECEIPT

```
AGENT: Pearl_GitHub (+ Pearl_Research, Pearl_PM sub-lanes)
SIGNAL: social-media-audit-landing-wave=MERGED (3 PRs: #75 9bfb9867c0, #79 319161a236, #96 cf1512336e)
OPEN_ITEMS: PR #53/#55 reconciliation (owner action needed); battle_en_us_genalpha CI gate (needs clean-checkout bisection)
ACCEPTANCE_LAYER: CODE-WIRED for the landed files; social_media subsystem overall remains far from PROVEN-AT-BAR per docs/specs/SOCIAL_MEDIA_100PCT_PRODUCTION_PLAN_2026-07-22.md
NEXT_ACTION: rebase/reconcile #53 and #55; bisect battle_en_us_genalpha from a clean origin/main checkout; action remaining Q-SOCIAL-STORYBLOCKS-VOLUME-01 / Q-SOCIAL-LIVE-SCHEDULING-NONGOAL-CONFIRM-01 whenever convenient
```
