# Session Handoff — 2026-05-04

**Operator:** Ahjan108
**Worktree:** `/Users/ahjan/phoenix_omega/.claude/worktrees/zealous-colden-df9890/`
**Branches active in this session:**
- `agent/pearl-news-layout-restore-20260503` (PR #850)
- `agent/pearl-news-five-layout-system-20260504` (PR #853)
- `agent/cover-d1-immediate-fixes-20260504` (PR #855)
- `agent/cover-pr4-category-anchor-20260504` (PR #857)

**Context tier:** Tier 1 — operator-present, no paid LLM calls (CI enforces).

---

## TL;DR

Two workstreams shipped, four open PRs, three more PRs sequenced. **Next agent / future me** can resume by reading this doc top-to-bottom; everything to make a decision is here, with file paths and SHAs.

| Workstream | Status | What's pending |
|---|---|---|
| Pearl News three-layout restore | **Done** — 2 PRs open, awaiting operator merge | Visual sign-off on rendered article variants once merged |
| Cover-design intelligence rebuild (5-phase plan) | **Phase 1 done** — 2 PRs open, BLOCKER fixes amended, both reviewer-approved | PR-5 (Phase 2+3), PR-6 (Phase 4), PR-7 (Phase 5) — gated on PR-3/PR-4 merge |

**4 open PRs**, all CI-running, all locally green. Both cover PRs went through a peer-review pass (2 parallel review agents); PR #857 had 2 BLOCKERs (now fixed); PR #855 was approved as-is.

---

## Workstream 1 — Pearl News three-layout restore (`COMPLETE`)

### Problem (operator's diagnosis)

> "Three different UI templates with sidebar on right OR left OR bottom. Currently it's stuck in the bottom variant with collapsed real estate. It used to work — look in git history. Don't reinvent it."

### Phase 1 archaeology — what we found

Documented in [`artifacts/audit/pearl_news_layout_archaeology_2026-05-03.md`](../artifacts/audit/pearl_news_layout_archaeology_2026-05-03.md) (167L). Headline:

- The current `origin/main` Pearl News article assembler (`pearl_news/pipeline/assemble_v52.py`) supported **3 layouts** — `default | scroll_story | dock`.
- A **5-layout** version existed on the unmerged branch `origin/agent/fix-pearl-news-deterministic-slots`, adding `editorial` (wider canvas + right sidebar) and `wide` (full-width content + sidebar cards as a horizontal **bottom strip**).
- That branch was **PR #587** — open since 2026-04-23, blocked by `Core tests` + `Workers Builds: pearl-prime` CI failures, ~10 days stale.
- The PR title (`fix(pearl_news): wire deterministic teacher slots into v52 render`) did NOT advertise the layout work, plausibly explaining the ">10 mis-fixes" pattern the operator described.

This was **failure-mode #2** from the brief: "the fix has been mis-attempted in a sibling worktree…surface the branch + recommend either (a) merging that worktree's branch, or (b) cherry-picking the relevant commits."

### Strategy chosen + executed

Strategy A — cherry-pick. PR #587 closed as superseded. Two new PRs:

| PR | What | Stat |
|---|---|---|
| [#850](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/850) | cherry-pick `f4d9418c8b` (slot/teacher fix) | +30/-1, 1 file |
| [#853](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/853) | cherry-pick `d6ead3af7a` (five-layout system) + `--layout` CLI plumbing in `run_article_pipeline.py` + `run_pearl_news_teacher_batch.py` + pytest cases for `wide`/`editorial`/unknown values + mobile-fallback markup for `dock` + lang-aware strip header for `wide` + governing spec | +539, 16 files |

`docs/PEARL_NEWS_LAYOUT_SYSTEM_2026-05-04.md` is the governing spec (linked in `docs/DOCS_INDEX.md`); has an anti-regression checklist that future Pearl News PRs must respect.

### Visual QA evidence

10 screenshots at `artifacts/qa/pearl_news_layout_screenshots_2026-05-03/` covering all 5 variants × {desktop 1440×900, mobile 375×812}. QA agent's measured DOM evidence verified:

| variant | desktop | mobile | computed evidence |
|---|---|---|---|
| `default` (right) | ✅ | ✅ | grid `1fr 360px`, max 1100px |
| `dock` (left) | ✅ | ✅ | grid `280px 732px`, sticky `top: 24px` |
| `wide` (**bottom**) | ✅ | ✅ | block layout, body 900px, sidebar `flex-direction: row`, "PRACTICE & ENGAGE" label visible |
| `editorial` (wider right) | ✅ | ✅ | grid `780px 280px`, max 1280px |
| `scroll_story` (no sidebar) | ✅ | ✅ | block, max 720px, sidebar `display: none` |

**Known caveats** (deferred to follow-up):
- Sample article used legacy 6-slot shape; `scroll_story` rendered with 0 inline interstitials and `dock` TOC anchors point to non-existent section IDs. Re-QA against a 14-slot article before authorizing the publisher to use the new variants.
- `dock` mobile lacks fallback HTML for the practice/CTA cards (CSS hides the rail; markup not emitted).

### What's pending on this workstream

1. **Operator merges #850, then #853.** They're stacked — #853 builds on #850's API.
2. **Configure publisher to set `meta["layout"]`** per-article. Code-review agents on PR #853 flagged that without this wiring, all production WP articles still fall through to `default` and the 5 variants are unreachable in prod.

---

## Workstream 2 — Cover-design intelligence rebuild (5-phase plan)

### Problem (operator's diagnosis)

> "You're not doing it right. Covers should look clear, understandable, not basic but with a REASON for being. Use deeper research. Get it right."

Two failing covers surfaced as ground truth:
- `artifacts/pipeline_examples/maat/cover_maat_boundaries.png` — title rendered as "No That Saved Me" (gibberish); royal navy + Greek key border + feather quill (ancient-mythology aesthetic on a *boundaries self-help* book). Wrong shelf signaling end-to-end.
- `artifacts/pipeline_examples/manga_covers/joshin_cover_anxiety.png` — beautiful sumi-e art print with **no title visible**. Looks like meditation art, not "I have anxiety, what helps?" buyer-facing book.

### Deep research output

[`artifacts/research/cover_design_intelligence_gap_2026-05-04.md`](../artifacts/research/cover_design_intelligence_gap_2026-05-04.md) (472L). Hard verdict:

> R6's 4-layer framework (brand × author × series × book) is structurally orthogonal to the layer a *reader* uses to recognize a cover — readers use **category** (Amazon sub-shelf). No category-anchor exists upstream of brand, so brand identity drifts into pretty-but-wrong covers (Truth Compass = Riverhead-typography luxury → shipped Greek-key + feather-quill on a *boundaries* self-help book).
>
> R6's quality gates run *after* FLUX, catching cheap defects (color count) but missing the expensive ones (wrong category, wrong promise, wrong audience). Pre-render contracts are needed.

Sources cited: Reedsy, Derek Murphy, Stuart Bache (The Creative Penn), BookBub Insights, KDPEasy, Self-Publishing Advice. URLs in the doc's §C.

### 5-phase plan (operator authorized "do all")

| # | Phase | Size | Status | Prereq |
|---|---|---|---|---|
| 1 | Category-anchor module + pre-render reader test | medium (~400-600 LOC) | **Done** as PR-3 (#855 D1) + PR-4 (#857 Phase 1) | Operator pre-curates the rest of the comp-shelf YAML (~198 cells, see below) |
| 2 | Title syntactic-fitter + title/subtitle category-keyword validator | small (~150-250 LOC) | Pending — PR-5 | PR-4 merged |
| 3 | FLUX prompt builder consumes category vocabulary | medium (~300-500 LOC) | Pending — PR-5 (bundled with Phase 2) | PR-4 merged |
| 4 | Manual-gate operationalization (operator click-to-pass + audit log) | small (~100-200 LOC) | Pending — PR-6 | none |
| 5 | Production tells (custom kerning) + golden-reference regression set | medium (~350 LOC + ~50 reference covers) | Pending — PR-7 | All earlier |

### Phase 1 — what shipped (PR #855 + PR #857)

#### PR #855 — D1 immediate fixes ([branch](https://github.com/Ahjan108/phoenix_omega_v4.8/tree/agent/cover-d1-immediate-fixes-20260504), head SHA `783386bf66`)

Two day-scoped bug fixes that don't require any architectural work:

**D1a — Maat title gibberish.** `_wrap_to_width` in `scripts/publish/render_kdp_cover.py` was syntax-naive; greedy whitespace wrap orphaned articles/conjunctions at line ends. Fix: orphan-prevention pass (article / preposition / conjunction / `no`/`not` / demonstratives never end a line). `_fit_font_to_box` runs two-pass: prefer orphan-free at smaller font sizes; fallback accepts orphans if geometry can't satisfy. ASCII-dominant only; CJK skipped.

**D1b — Joshin no-title cover.** `phoenix_v4/manga/covers/cover_assembler.py::overlay_typography_front` swallowed the title-render exception and continued to logo + save. Result: title-less covers got published. Fix: fail-closed on empty / whitespace `title_text` and missing `typography_config`. Title-render exceptions propagate.

**Tests.** [`tests/test_cover_d1_immediate_fixes.py`](../tests/test_cover_d1_immediate_fixes.py) — 9 tests, all green. Existing `tests/test_publish_render_kdp_cover.py` 25/25 still pass.

**Reviewer verdict:** **APPROVE, no BLOCKERs.** Three IMPORTANT items, all deferred to PR-5 scope:
- `_render_title_text:190-191` has dead-code `if tc is None: return image` (now unreachable).
- `_fit_font_to_box` fallback path doesn't prefer orphan-free (intentional per docstring).
- Manga `_render_title_text` has no wrapping at all (out of scope for D1, planned for PR-7).

**Backward-compat call-out:** any existing KDP cover that previously rendered with a trailing-article orphan at initial font size will now render with a smaller font and orphan-free wrap. Reviewer recommends spot-checking 2–3 already-shipped "The X of Y" or "A Guide to Z" titles.

#### PR #857 — Phase 1: category-anchor + comp-shelf + pre-render gate ([branch](https://github.com/Ahjan108/phoenix_omega_v4.8/tree/agent/cover-pr4-category-anchor-20260504), head SHA `4d6b95ac3d`)

The architectural fix. Adds the rung-0 layer that R6's brand-author-series-book identity system was missing.

**Files:**

| Role | Path | LOC |
|---|---|---|
| Comp-shelf YAML (the data) | [`config/publishing/cover_comp_shelf.yaml`](../config/publishing/cover_comp_shelf.yaml) | 361L |
| Resolver / `CategoryAnchor` dataclass | [`scripts/publish/category_anchor.py`](../scripts/publish/category_anchor.py) | 336L (post-amendment) |
| Pre-render gate (CLI + library) | [`scripts/publish/cover_pre_render_gate.py`](../scripts/publish/cover_pre_render_gate.py) | 278L |
| Tests | [`tests/test_cover_category_anchor.py`](../tests/test_cover_category_anchor.py) | 303L → 426L |
| Governing spec | [`docs/COVER_CATEGORY_ANCHOR_SPEC.md`](./COVER_CATEGORY_ANCHOR_SPEC.md) | 161L (post-amendment) |
| Tagged in | [`docs/DOCS_INDEX.md`](./DOCS_INDEX.md) | +1L |

**Pre-render gate** runs BEFORE FLUX. Four gates:
- G1 `category_anchor_resolves` — block if `--fail-on-missing-cell`
- G2 `comp_shelf_confidence_present` — warn
- G3 `category_keyword_in_title_or_subtitle` — **BLOCK**
- G4 `flux_subject_no_blocked_motifs` — **BLOCK** (substring-match against blocklist)

Exit codes: 0 = pass / pass-through, 2 = blocked, 1 = unresolved.

**Seed cells (2 of ~200 needed):**
- `boundaries__en` (`high` confidence, 5 verified comp covers — Cloud/Townsend, Tawwab x2, McKeown, Braiker; dates verified)
- `anxiety__en__manga` (`provisional`, 4 verified comps + 1 placeholder)

**Reviewer verdict (initial):** FIX-FIRST. Two BLOCKERs:

1. **`is_blocked_motif` over-blocked via bidirectional substring match.** With the boundaries blocklist entry `"any single human figure as focal element"`, candidates like `"figure"`, `"single"`, `"element"`, `"focal"`, `"border"` all became falsely blocked. **Fixed in commit `4d6b95ac3d`** — one-directional containment only. Pinned by `test_is_blocked_motif_unidirectional_no_overblocking`.

2. **`title_carries_category_keyword` collapsed slash-form keywords to a literal phrase.** YAML keyword `"yes / no"` became `\byes no\b` (literal phrase) instead of OR-ing the alternatives. **Fixed in commit `4d6b95ac3d`** — strip parentheticals, split on `/`, try each branch with word-boundary regex. Pinned by 3 new regression tests.

Plus IMPORTANT cleanups (also in `4d6b95ac3d`):
- Spec doc anti-regression checklist tagged `[testable]` vs `[policy]`.
- Two new deferred items captured: cell-key separator collision check (PR-5), `subtitle_scope: "neither"` allowlist for canonical comp titles like *Daring Greatly* (PR-5).
- Exit-code documentation honestly notes argparse's exit-2 inheritance.

**Tests:** 24 → 29 (+5 regression tests). All green. PR comment posted summarizing the BLOCKER fixes.

### What's pending — operator data work (the binding prerequisite)

The seed YAML ships 2 cells. **Full coverage = ~200 cells:** ~13 brands × ~15 topics × ~3 locales (en / ja / zh-cn). Each cell needs 5 verified comp covers.

This is **operator data work**, not engineering. ~15 min/cell × 200 ≈ **50h of operator time** across the catalog timeline. Live Amazon scraping is OUT of scope.

Add cells via small data-only PRs that append to `shelves:` in the YAML. Renderer warns-but-passes on missing cells under default `cover_anchor_resolution.fallback_policy: warn_and_pass_through`; flip to `fail_closed` once coverage hits >80%.

**Recommended curation order:**
1. The 2 failing-cover rescue cells — shipped in PR #857.
2. Pearl Prime's eight active topics × three locales (~24 cells).
3. Manga-format cells (~30 cells).
4. The long tail (catalog 800-config foothold).

### What's pending on this workstream — engineering work

**PR-5 (Phase 2 + 3, medium ~500-700 LOC):**
- Wire pre-render gate into `scripts/publish/render_imagery_for_template.py` + `phoenix_v4/manga/covers/cover_generator.py`.
- Add YAML title-validator that runs at config-load time (refuses to load if any book's title fails the keyword check for its declared topic).
- Build a FLUX prompt builder that sources subjects from `visual_motif_pool` instead of hardcoded strings.
- Address PR #855 IMPORTANT items: remove dead `_render_title_text:190-191` branch; comment on `_fit_font_to_box` fallback semantics.
- Add the deferred items from PR #857 spec doc: cell-key separator validator; `subtitle_scope: "neither"` allowlist.

**PR-6 (Phase 4, small ~100-200 LOC):**
- Operationalize manual gates: CLI wrapper around `cover_quality_gates.py` + `cover_pre_render_gate.py` that records pass/fail to an audit log, gates publish.

**PR-7 (Phase 5, medium ~500 LOC + ~50 reference covers):**
- Production-tells layer (per-font kerning tables, key-word punch styling).
- Golden-reference regression set so silent regressions get caught.
- Manga `_render_title_text` wrapping (carry-over from PR #855 IMPORTANT).

---

## All open PRs (4 in flight)

| # | Branch | Workstream | Status | CI | Locally-green |
|---|---|---|---|---|---|
| [#850](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/850) | `agent/pearl-news-layout-restore-20260503` | Pearl News slot/teacher | open | running | yes |
| [#853](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/853) | `agent/pearl-news-five-layout-system-20260504` | Pearl News 5-layout system | open | running | yes |
| [#855](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/855) | `agent/cover-d1-immediate-fixes-20260504` | Cover D1 fixes | open, **APPROVE** | running | 9/9 D1 + 25/25 existing |
| [#857](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/857) | `agent/cover-pr4-category-anchor-20260504` | Cover Phase 1 | open, BLOCKERs **fixed**, ready for re-review | running | 29/29 |

PR #587 (the original Pearl News stranded fix) was closed as superseded earlier.

---

## Decisions still needing operator input

### Pearl News
- **D-PN-1.** Once #850 + #853 merge, **configure publisher to set `meta["layout"]`** per-article. Without this, the 5 variants ship as code but are unreachable in prod (every article falls through to `default`). This is publisher-configuration work, not engineering.
- **D-PN-2.** Re-QA against a 14-slot article before authorizing the new variants for production. The visual QA used a legacy 6-slot sample, so `scroll_story`'s inline interstitials and `dock`'s TOC anchors couldn't be verified.

### Cover system
- **D-CV-1.** Merge order: I recommend #855 first (smaller, isolated bug fixes, APPROVE), then #857 second (larger, Phase 1 architecture, BLOCKER-fixed). PR-5 stacks on #857.
- **D-CV-2.** Comp-shelf YAML curation cadence — operator picks. Options:
  - Curate as I go, blocking PR-5 until ~24 production-active cells are filled.
  - Ship PR-5 with code-only and curate cells in parallel data PRs (recommended; avoids serialization).
- **D-CV-3.** Should `cover_anchor_resolution.fallback_policy` flip to `fail_closed` at any specific cell-coverage threshold? Recommend >80% of catalog footprint, which is operator data work.
- **D-CV-4.** Architectural decision — when a canonical comp title lacks the topic keyword in title or subtitle (e.g. *Daring Greatly* on the boundaries shelf), do we add an `exempt_titles` allowlist, or extend `category_keyword_required_in` with a `"neither"` scope value? Either works; pick before PR-5 ships the validator.

---

## Risks + caveats

### Documented in PRs
- **PR #855 backward-compat**: existing covers with trailing-article titles will re-render at smaller font sizes after merge. Spot-check 2–3 shipped titles before authorizing fleet-wide regen.
- **PR #857 confidence levels**: `boundaries__en` is `high` (5 verified comps); `anxiety__en__manga` is `provisional` (1 placeholder comp explicitly marked TBD). Operator should upgrade `anxiety__en__manga` to `high` before flipping `fallback_policy: fail_closed`.

### Surfaced in reviews, deferred
- **CategoryAnchor mutability gap**: dict fields are NOT deep-frozen. Callers can mutate `anchor.visual_motif_pool["type_dominant"]["weight"] = 0.99` and corrupt other consumers. Documented in spec; PR-5+ should consider `MappingProxyType` if real-world mutations occur.
- **Manga title wrapping**: `_render_title_text` in `cover_assembler.py` has NO wrapping logic. Long manga titles will silently overflow the title box. Fix planned for PR-7.

### Known edge cases not yet pinned
- Leading-punctuation titles (`'"The Book of No"'`).
- Em-dash titles (`"The Book — A Practical Guide"`).
- Pure-CJK single-char titles (`"心"`).

These don't crash today; tests for them would lock in correctness. Add in PR-5.

---

## Files to read in order (for next agent / future me)

1. **This doc** — `docs/SESSION_HANDOFF_2026_05_04.md`.
2. **CLAUDE.md** — repo-level rules (LLM tier policy, push-guard requirements, PR governance).
3. **`artifacts/research/cover_design_intelligence_gap_2026-05-04.md`** — the deep-research diagnosis. Q1-Q5 cover the design-intent ladder, per-cover defect lists, where defects originate in the pipeline, methodology gaps, and the 5-phase plan. **This is the brain dump.**
4. **`docs/COVER_CATEGORY_ANCHOR_SPEC.md`** — the governing spec for cover Phase 1. Schema, resolver contract, gate contract, anti-regression checklist with `[testable]`/`[policy]` tags.
5. **`config/publishing/cover_comp_shelf.yaml`** — the data layer. The 2 seed cells are reference templates for adding the next ~198.
6. **`scripts/publish/category_anchor.py`** + **`scripts/publish/cover_pre_render_gate.py`** — the working code.
7. **`docs/PEARL_NEWS_LAYOUT_SYSTEM_2026-05-04.md`** — Pearl News governing spec for the 5-layout system (PR #853).
8. **`artifacts/audit/pearl_news_layout_archaeology_2026-05-03.md`** — the archaeology that drove PR #850 + PR #853.

For PRs:
- `gh pr view 850` / `gh pr view 853` / `gh pr view 855` / `gh pr view 857` for current state.

---

## Resume signal — what to do next

**If operator has merged #855 + #857:**
1. Branch from fresh `origin/main`: `git checkout -b agent/cover-pr5-renderers-flux-builder-<DATE> origin/main`.
2. Read `docs/COVER_CATEGORY_ANCHOR_SPEC.md` and `artifacts/research/cover_design_intelligence_gap_2026-05-04.md` Q5 PHASE 2 + PHASE 3.
3. Wire `cover_pre_render_gate.run_gates()` into `render_imagery_for_template.py:<find the FLUX-call site>` and `phoenix_v4/manga/covers/cover_generator.py:<find the FLUX-call site>` — gate must run BEFORE FLUX spend.
4. Build the FLUX prompt builder that consumes `anchor.visual_motif_pool` (weighted random selection) and applies `anchor.filter_motifs()` to drop blocklist hits.
5. Add YAML title-validator that runs at config-load time on `cover_identity_system.yaml::books.*.title` — refuses to load if any book's title fails `anchor.title_carries_category_keyword()` for its declared `(topic, locale)`.
6. Address PR #855 IMPORTANT items (`_render_title_text:190-191` dead branch; `_fit_font_to_box` fallback comment).
7. Address PR #857 deferred items (cell-key separator collision validator; `subtitle_scope: "neither"` allowlist OR `exempt_titles` field — depends on D-CV-4).
8. Tests: pin every code path with at least one regression test that ties back to the operator's failing-cover ground truth (Maat, Joshin) AND extends to a third synthetic case to prove the contract isn't over-fit.
9. Push, open PR-5, run preflight + push-guard, monitor governance gate.

**If operator has NOT merged #855 + #857:**
- Don't stack PR-5 on the unmerged branches. Per memory note "Validation before scaling": pivot to validation work instead — re-QA the 14-slot article path for Pearl News (D-PN-2), or curate the next batch of comp-shelf cells (D-CV-2). Both unblock downstream work without rebase risk.

**If operator changed direction entirely:**
- Re-read the most recent operator messages in this session's transcript.
- The 5-phase plan is a hypothesis; operator can override at any point. The research doc Q5 phases are ranked by leverage but not by sequencing dependency for phases 4 and 5 (they could be done in parallel with the others).

---

## Session-level constraints respected

- ✅ No paid LLM API calls (CI's `llm-policy-enforcement.yml` enforces; verified via `python3 scripts/ci/audit_llm_callers.py`).
- ✅ No `--admin` merges.
- ✅ Every PR branched from `origin/main` (not from another feature branch); push-guard + preflight clean.
- ✅ Every PR has CLOSEOUT-able receipt material (full SHAs, file lists, line counts, governance gate status).
- ✅ Pearl News and Cover work kept on separate branches; no cross-contamination.
- ✅ One PR closed as superseded (#587), with clear reasoning in the PR comment + this handoff.
- ✅ All review BLOCKERs fixed before requesting human re-review (#857).

---

*Generated 2026-05-04 by Claude Opus 4.7 (1M context). For questions about any decision in this doc, see the linked artifacts; for questions about future direction, ask the operator.*
