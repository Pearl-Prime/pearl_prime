# Pearl News Sidebar — Version History

**Last updated:** 2026-06-04
**Authored by:** Pearl_News (Phoenix Omega) — session `agent/pearl-news-sidebar-restore-20260603`
**Authority:** This document is the chronological record of every sidebar version that has ever shipped (in `pearl_news/pipeline/` and adjacent paths). The canonical-SHA verdict at §16 governs what the parity gate (`scripts/ci/check_pearl_news_sidebar_parity.py`) enforces.
**Companion docs:** [`PEARL_NEWS_SIDEBAR_FUNCTION_INVENTORY.md`](./PEARL_NEWS_SIDEBAR_FUNCTION_INVENTORY.md) (F-ID definitions), [`PEARL_NEWS_LAYOUT_SYSTEM_2026-05-04.md`](./PEARL_NEWS_LAYOUT_SYSTEM_2026-05-04.md) (PR #853 governing spec), [`PEARL_NEWS_WRITER_SPEC.md`](./PEARL_NEWS_WRITER_SPEC.md) §S (Sidebar Restoration Protocol).

---

## 0. Why this doc exists

Per memory `project_known_good_anchors.md` (Pearl News sidebar entry): _"Operator has reported sidebar variants broken ~25 times across sessions. Every fresh-fix attempt failed. The fix has always been git-restore from PR #853, never re-authoring."_

This document is the append-only ledger that prevents the next session from having to rebuild the SHA archeology from scratch. Every row has:

- **SHA + date + PR#**
- **Files touched**
- **Functions added / removed** (cross-ref to F-IDs in A2)
- **Verdict** (BEST / GOOD / BROKEN / SUPERSEDED / DEPRECATED)
- **Verdict-evidence** (operator quote OR observable behavioral difference)

The §16 final table names the single canonical SHA (or SHA chain) that the parity gate restores against.

---

## 1. Lineage at a glance

```
PR #505  (505-byline/sidebar regression museum)        Apr 2026  — earliest in-history sidebar work captured here
   ↓
PR #559  (restore v5.2 sidebar + teacher-per-article)  Apr 2026  — first MERGED operator restore via git-first rule
   ↓
PR #592  (v5.4 interactive sidebar)                    Apr 2026  — CLOSED (superseded); 732ccfd56 secondary anchor
   ↓
PR #850  (slot/teacher fix PR-1 of 2)                  May 2026  — wire slot+teacher into v52
   ↓
PR #853  (five-layout sidebar + governing spec)        2026-05-04 — CANONICAL ⭐  SHA 8070e81fd
   ↓
PR #1105 (kill wpautop phantom <p> grid theft)         2026-05-13 — companion fix; SHA b64caf846
   ↓
[branch-only] 6e7dc9277  (operator restore PR #853 → v2)       2026-05-19  — NOT MERGED
[branch-only] 45733349a  (mini-app launcher cta-card)          2026-05-19  — NOT MERGED
[branch-only] 78f115fe3  (interactive poll + take + IIFE)      2026-05-19  — NOT MERGED, but produces live 3724
[branch-only] d0075d31d  (WP must-use plugin /signal)          2026-05-19  — NOT MERGED, but plugin DEPLOYED LIVE
[branch-only] 3daa86d56  (gen_z_reactions atom schema)         2026-05-19  — NOT MERGED
```

The four 2026-05-19 commits live on `agent/pearl-news-section-order-fix` (worktree `elastic-kepler-2caa6a`). They were never put into a PR. The operator's "Pearl Star working copy" refers to this branch.

---

## 2. PR #505 — `d148285be` — fix(pearl_news): 1-topic × 1-teacher × 1-article + byline/sidebar + regression museum

| Field | Value |
|---|---|
| **Date** | 2026-04-19 |
| **PR** | [#505](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/505) (MERGED) |
| **Branch** | `agent/pearl-news-one-per-teacher-fix-20260419` |
| **Files** | `pearl_news/pipeline/assemble_v52.py`; tests; regression museum |
| **Functions added** | (early) F1 exercise card scaffold; F2 cta-card scaffold; F3 SDG card |
| **Functions removed** | none |
| **Verdict** | **SUPERSEDED** by PR #853 |
| **Evidence** | Memory `project_known_good_anchors.md` lists `d148285be` as a secondary restore anchor — meaning it had a working sidebar but PR #853 superseded its layout system. |

## 3. PR #559 — `87fc9befe` — fix(pearl_news): restore v5.2 sidebar + teacher-per-article

| Field | Value |
|---|---|
| **Date** | 2026-04-21 |
| **PR** | [#559](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/559) (MERGED) |
| **Files** | `pearl_news/pipeline/assemble_v52.py`; tests |
| **Functions** | restored F1–F3 after a drift |
| **Verdict** | **SUPERSEDED** by PR #853 |
| **Evidence** | This was the FIRST operator-invoked git-first restore documented in the codebase. Memory secondary anchor. |

## 4. PR #592 — `732ccfd56` — feat(pearl-news + manga): v5.4 interactive sidebar

| Field | Value |
|---|---|
| **Date** | 2026-04-23 |
| **PR** | [#592](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/592) (**CLOSED**, not merged) |
| **Files** | `pearl_news/pipeline/assemble_v52.py` + manga lead-pick artifacts |
| **Functions added** | (early version of) F4 poll + F5 take |
| **Verdict** | **SUPERSEDED** by 78f115fe3 (which authored the modern interactive layer from scratch — memory note: _"this never existed in this repo (no votePoll/pollOption/submitTake across --all refs)"_, meaning #592's interactive layer was discarded). |
| **Evidence** | PR #592 was closed in favor of splitting into PR #850 + PR #853 (per #853 body: _"Why split from PR #587"_). The 13-manga-lead-picks salvaged to PR #713; the sidebar interactive code was NOT salvaged. |

## 5. PR #850 — `d6ead3af7` — fix(pearl_news): wire deterministic teacher slots into v52 render (PR-1 of 2)

| Field | Value |
|---|---|
| **Date** | 2026-05-03 |
| **PR** | [#850](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/850) (MERGED) |
| **Files** | `pearl_news/pipeline/assemble_v52.py` (+30 / -1) |
| **Functions** | Teacher slot wiring — prerequisite for PR #853 |
| **Verdict** | **GOOD** (still load-bearing in current main; PR #853 builds on it). |
| **Evidence** | PR #853 body explicitly calls out PR #850 as companion: _"PR-1 (#850), 1 file, +30/-1"_. |

## 6. ⭐ PR #853 — `8070e81fd` — feat(pearl_news): five-layout sidebar system + `--layout` CLI + governing spec (PR-2 of 2)

| Field | Value |
|---|---|
| **Date** | 2026-05-04 (merged 15:26:18 UTC) |
| **PR** | [#853](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/853) (MERGED) |
| **Files (17)** | `pearl_news/pipeline/assemble_v52.py` (+143/-8); `run_article_pipeline.py` (+13); `scripts/run_pearl_news_teacher_batch.py` (+15/-2); `tests/test_pearl_news_sidebar_v52.py` (+127); `docs/PEARL_NEWS_LAYOUT_SYSTEM_2026-05-04.md` (+161); 10 layout screenshot PNGs |
| **Functions added** | F1 exercise timer (5-card density); F2 cta-card slot; F3 SDG card; layout system with 5 variants (default/dock/wide/editorial/scroll_story); lang attribute; CSS_DOCK mobile breakpoint |
| **Functions removed** | none |
| **Verdict** | **BEST — CANONICAL ANCHOR** ⭐ |
| **Evidence** | (1) Memory `project_known_good_anchors.md` Pearl_News section explicitly names `8070e81fd` as the canonical SHA. (2) PR #853 ships the governing spec `docs/PEARL_NEWS_LAYOUT_SYSTEM_2026-05-04.md` ("the gate against the 11th regression"). (3) Every subsequent operator restore (6e7dc9277) cites PR #853 by SHA. (4) `tests/test_pearl_news_sidebar_v52.py` (15/15 passing) is the anti-regression harness. |

## 7. PR #1105 — `b64caf846` — fix(pearl_news): kill WordPress wpautop phantom `<p>` that steals the sidebar grid cell

| Field | Value |
|---|---|
| **Date** | 2026-05-13 |
| **PR** | [#1105](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1105) (MERGED) |
| **Files** | `pearl_news/pipeline/assemble_v52.py` (+6 lines) |
| **Functions** | Defensive fix — WP wpautop was injecting phantom `<p>` tags that broke `.article-container { display: grid; grid-template-columns: 1fr 360px; }` and the sidebar fell into the main column. |
| **Verdict** | **GOOD — load-bearing companion to PR #853** |
| **Evidence** | Required for visible sidebar rendering; without it, post-WP HTML breaks the grid. Listed in user brief gotchas. |

## 8. PRs #1106 / #1107 / #1108 / #1109 — slot HTML hygiene (2026-05-13/14)

| PR | Subject | Effect on sidebar |
|----|---------|--------|
| #1106 | remove mock-up pillar nav + authority block | no direct sidebar change; removed top-of-article chrome |
| #1107 | strip HTML leaks from slot output | indirect — cleans LLM output that was occasionally leaking into sidebar h3s |
| #1108 | also strip slot-prompt scaffolding (SLOT:, ## LEDE) | indirect |
| #1109 | strip inline HOOK:/BIG_PICTURE: prefixes + anti-echo postscript | indirect |

**Verdict for all four:** GOOD — defensive hygiene, no functional change to sidebar. None drift-relevant.

## 9. PR #1119 — `agent/pearl-news-stop-legacy-filler-20260516` — emergency stop on missing atoms

**Date:** 2026-05-15. **Verdict:** GOOD; quality-gate addition; no sidebar markup change.

## 10. PR #1124 + #1126 + #1128 — foundation / pack / localization (2026-05-15/16)

**Verdict:** GOOD; teacher pack + locale work; no sidebar markup change.

## 11. PR #1175 — `master_wu x 5 cells` (2026-05-17)

**Verdict:** GOOD; per-teacher per-slot atom expansion; no sidebar markup change.

## 12. ⚠️ BRANCH-ONLY commit `6e7dc9277` — fix(pearl_news): restore PR #853 sidebar structure for v2 (operator git-first restore)

| Field | Value |
|---|---|
| **Date** | 2026-05-19 11:01:41 -10:00 |
| **Branch** | `agent/pearl-news-section-order-fix` (NOT MERGED) |
| **Files** | `pearl_news/pipeline/assemble_v52.py` (+308 / -? lines; brings file from ~1750 → 2058) |
| **Functions restored** | F1 exercise timer (full, with toggleExercise + step dots) + F2 cta-card slot — both had been silently replaced by a single static "v2-practice-card" in an earlier branch commit. |
| **Verdict** | **GOOD — operator-anchored** |
| **Evidence** | Commit body: _"Operator 2026-05-19: 'the nav is not working right. it used to work great. look in git history for best stuff.' Per memory drift-recovery rule (git first, not fresh-fix), checked the known-good anchors registry → PR #853 / SHA 8070e81fd"._ This is the canonical operator-invoked restore that's the basis for the entire feedback memory `feedback_drift_recovery_git_first.md`. |

## 13. ⚠️ BRANCH-ONLY commit `45733349a` — feat(pearl_news): v2 — mini-app launcher + SDG bullets + disclaimer relocate + long-form Gen Z atoms + teacher-view rewrite

| Field | Value |
|---|---|
| **Date** | 2026-05-19 10:46:24 -10:00 |
| **Branch** | `agent/pearl-news-section-order-fix` (NOT MERGED) |
| **Files** | `pearl_news/pipeline/assemble_v52.py` (+1); new file `pearl_news/config/reaction_to_app.yaml` |
| **Functions added/refined** | F2 cta-card → mini-app launcher (gated on `practice_app_slug`); F3 SDG card grows to 3-bullet detail |
| **Verdict** | **GOOD** (operator approved the mini-app launcher in QA pass 2026-05-19). |
| **Evidence** | Commit body details operator QA pass with 4 specific asks all addressed. |

## 14. ⚠️ BRANCH-ONLY commit `78f115fe3` — feat(pearl_news): interactive Hot Take Poll + Editorial Take submission + EI v2 ingest stub

| Field | Value |
|---|---|
| **Date** | 2026-05-19 11:40:04 -10:00 |
| **Branch** | `agent/pearl-news-section-order-fix` (NOT MERGED) |
| **Files** | `pearl_news/pipeline/assemble_v52.py` (+~118 lines); new file `pearl_news/pipeline/reader_signal_ingest.py` |
| **Functions added** | F4 Hot Take Poll (clickable `<button class="pn-poll-option">` with data-pn-value, localStorage tally, animated `.pn-poll-bar`); F5 Editorial Input (textarea + `<button class="pn-take-submit">`); INFRA `pnReaderSignal` IIFE (POST to `/wp-json/pearl-news/v1/signal` with mailto fallback) |
| **Verdict** | **GOOD — operator-requested, function-bearing** |
| **Evidence** | Commit body: _"Operator request 2026-05-19: 'there was a poll + take submission that fed info to ei v2 and helped select next articles' — confirmed via git history that this never existed in this repo (no votePoll/pollOption/submitTake/reader_signal/poll_response across --all refs). Built it."_ — This is the ONE place these functions exist in code. PR #592's earlier interactive layer was discarded; this is the canonical implementation. |

## 15. ⚠️ BRANCH-ONLY commit `d0075d31d` — feat(pearl_news): WP must-use plugin for `/wp-json/pearl-news/v1/signal` (Phase 2)

| Field | Value |
|---|---|
| **Date** | 2026-05-19 12:16:48 -10:00 |
| **Branch** | `agent/pearl-news-section-order-fix` (NOT MERGED — but DEPLOYED LIVE on `pearlnewsuna.org`) |
| **Files** | new files `pearl_news/wp_plugin/pearl-news-signal.php` (~280 LOC) + `pearl_news/wp_plugin/README.md` |
| **Functions added** | INFRA POST `/wp-json/pearl-news/v1/signal` + GET `/wp-json/pearl-news/v1/signal/aggregate/{article_id}`. Rate-limit (20/min, 500/day per hashed IP). Honeypot fields. SHA-256 IP anonymization. Appends to `wp-content/uploads/pearl-news-signals/YYYY-MM-DD.jsonl`. |
| **Verdict** | **GOOD (repo-side) — but DRIFTED vs. deployed** |
| **Evidence** | Live probe (2026-06-04): `GET /wp-json/pearl-news/v1` returns 10 endpoints (`/signal`, `/poll`, `/editorial`, `/advocate`, `/freebie`, `/feedback`, plus 4 GET variants). Repo plugin implements only 2 (`/signal` POST + `/signal/aggregate` GET). The other 8 endpoints are deployed but **source nowhere in the repo or any worktree**. See `Q-PNS-PLUGIN-DRIFT-01` in §17. Operator (this session) approved accepting the lag for this PR; full plugin source pull deferred to a follow-up workstream. |

## 16. VERDICT TABLE — canonical SHA chain for the parity gate

The parity gate (`scripts/ci/check_pearl_news_sidebar_parity.py`) restores against this composite chain. Each row is necessary; no single SHA is sufficient.

| Order | SHA | PR | On `origin/main`? | Files | Role |
|-------|-----|----|--------------------|------|------|
| 1 | `8070e81fd` | #853 | ✅ | assemble_v52.py +143 | **Structural baseline.** 5-layout system, exercise/cta/SDG card scaffolding, governing spec. |
| 2 | `b64caf846` | #1105 | ✅ | assemble_v52.py +6 | wpautop grid-cell fix — required for post-WP visible sidebar. |
| 3 | `6e7dc9277` | — | ❌ branch-only | assemble_v52.py +308 | Operator restore of PR #853's 5-card density into v2 templates. |
| 4 | `45733349a` | — | ❌ branch-only | assemble_v52.py +1 + new yaml | mini-app launcher cta-card variant + 3-bullet SDG; new `reaction_to_app.yaml`. |
| 5 | `78f115fe3` | — | ❌ branch-only | assemble_v52.py +~118 + new py | Interactive F4 poll + F5 take + `pnReaderSignal` IIFE; new `reader_signal_ingest.py`. |
| 6 | `d0075d31d` | — | ❌ branch-only (DEPLOYED) | new php + README | WP must-use plugin serving `/signal` endpoint. |

**Selected restore source for `pearl_news/pipeline/assemble_v52.py`:** `78f115fe3` — it is the LATEST branch-only commit that touches `assemble_v52.py`, so its on-disk file content already contains rows 3+4+5 stacked. Restore command:

```bash
git checkout 78f115fe3 -- pearl_news/pipeline/assemble_v52.py
git checkout 78f115fe3 -- pearl_news/pipeline/reader_signal_ingest.py
git checkout d0075d31d -- pearl_news/wp_plugin/
git checkout 45733349a -- pearl_news/config/reaction_to_app.yaml
git checkout 3daa86d56 -- pearl_news/atoms/gen_z_reactions/
```

This restores 6 of the canonical chain's `assemble_v52.py` deltas (8070+b64ca+6e7dc+45733+78f11 — d0075 didn't touch the file) and the 4 new files. The wpautop fix b64caf846 is already in main HEAD (since current main inherits PR #1105). The 78f115fe3 file content also inherits b64caf846 since 78f115fe3's branch was built on top of a main that included #1105.

---

## 17. Open operator questions

| ID | Status | Summary |
|----|--------|---------|
| `Q-PNS-CANONICAL-01` | **Refined → composite** | Canonical is the chain of 6 SHAs in §16. The "single canonical SHA" form of the question has no clean answer; the parity gate enforces the composite. |
| `Q-PNS-CANONICAL-01-RESTORE-MECHANISM` | **Answered: git-checkout** (operator confirmed 2026-06-04) | Use `git checkout <sha> -- <path>` per file. NOT cherry-pick. Avoids commit-history coupling to v2-template work. |
| `Q-PNS-HERO-01` | **Open** | Operator flagged hero-pic in wrong place in prior session. Canonical placement matches post 3724. After C1 restore, render a sample article + diff against 3724's hero position; if mismatch, surface in PR body and let operator decide. |
| `Q-PNS-POLL-BACKEND-01` | **Answered** | `/wp-json/pearl-news/v1/signal` (live + healthy, POST test returned `{"ok":true,"signal_id":"..."}` at 2026-06-04 16:42 UTC). |
| `Q-PNS-EDITORIAL-INPUT-01` | **Answered** | Same endpoint as poll, `kind: take` payload variant. Same plugin file. |
| `Q-PNS-DEPRECATION-01` | **Refined** | Prior chat's deprecation proposal targeted `assemble_v52.py` — that's WRONG. assemble_v52.py contains the canonical sidebar; do NOT deprecate. See `artifacts/pearl_news/audit/DEPRECATION_PROPOSAL.md` for the corrected list (legacy patch scripts only). |
| `Q-PNS-CI-BLOCKING-01` | **Answered (Recommended default)** | D1 BLOCKS publish on parity-fail. CI workflow steps must run D1 BEFORE the publish step; exit non-zero ⇒ publish skipped. |
| `Q-PNS-LIVE-TEST-POST-01` | **Open** | Operator to pick a disposable slug (suggested: `pn-sidebar-parity-probe-20260606`). Live-test post acceptance #4 will create it. |
| `Q-PNS-PLUGIN-DRIFT-01` (NEW) | **Answered: accept lag** (operator confirmed 2026-06-04) | Deployed plugin has 8 endpoints not in repo. This PR restores `/signal` only. Follow-up workstream proposal: either pull live PHP source (requires WP server SSH or admin-side export) or document the endpoint set + author the additional routes. NOT for this PR. |

---

## 18. Drift-recovery quick-reference

When operator says _"the sidebar is broken"_ in a future session:

1. **Read this doc + `PEARL_NEWS_SIDEBAR_FUNCTION_INVENTORY.md`** (NOT git history from scratch).
2. **Run** `python3 scripts/ci/check_pearl_news_sidebar_parity.py` to see which F-IDs are missing.
3. **For each missing F-ID:** look up the source SHA in §16, run `git checkout <sha> -- <path>`.
4. **Re-run the gate.** If it still fails, the canonical snapshot itself may be stale — refresh per §S of `PEARL_NEWS_WRITER_SPEC.md`.
5. **NEVER re-author sidebar markup, CSS, or JS.** Every regression in this domain (per memory: ~25 of them) has been a re-author attempt that made things worse. Git checkout is the rule.

---

**End of document. Append-only.**
