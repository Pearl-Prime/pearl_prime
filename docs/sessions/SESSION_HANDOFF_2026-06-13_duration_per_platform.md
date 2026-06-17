# Session Handoff — Pearl_Research: Duration-Per-Platform Strategy

**Date:** 2026-06-13 · **Agent:** Pearl_Research (platform-duration strategy) · **Tier:** 1 (operator present) · **Repo:** Ahjan108/phoenix_omega_v4.8
**Result:** PR **#1574 MERGED** (`ff0383efd`) — tier→platform routing + cited platform profiles live on main. Operator approved all 4 decision items. Content-length + CJK routed onward.
**Companion artifacts:** `artifacts/research/duration_per_platform_20260613/` (PLAN, SOURCES, GAP_VERIFICATION, CONTENT_LENGTH_TARGETS, deck)
**Memory:** `project_duration_per_platform`

---

## 1. Mission

Read our existing duration research; deep-research what each publishing/streaming platform rewards by length; build the per-platform duration plan (the target length to WIN on each surface); verify our REAL render durations against it; close the gaps (config in-lane; content-length routed to the writing program, never faked).

## 2. Discovery — what already existed (the reframe)

The landscape was more built than the brief assumed. Discovery flipped the task from "greenfield a plan" to "cross-walk + validate + verify + route":

- **CDIS framework** — `specs/CONTENT_DURATION_INTELLIGENCE_DEV_SPEC.md` (2026-03-31, "43 source clusters"): §4 platform profiles, §5 persona budgets, §8 cadence, §9 panel counts, §10 book/audiobook duration. The governing spec.
- **`config/duration/platform_duration_profiles.yaml`** (CDIS §4 as config) and **`config/catalog_planning/platform_knob_tuning.yaml`** (platform→format-tier routing). **Both have ZERO Python consumers** — planning references, not yet wired (CDIS §14 Phase-2 wires them). Numbers were uncited inline and ~2.5 months stale.
- **The honest 7-tier ladder MERGED** — PR **#1550** (`8236c5e3c`) derives honest durations from `word_target` (`standard_book` audiobook 147min / word_range `[9000,22000]` / `fill_regime: cap`); PR **#1572** (`c6de0be93`) added `one_hour_book` (9000w=60min); PR **#1573** (`b1f705291`) added `docs/DURATION_DERIVATION_SPEC_CJK_ADDENDUM.md`. Honesty spine: advertised duration = REAL median render; thin renders HARD_FAIL the word_count_gate.

**The genuine gaps (this session's contribution):** (a) no tier→platform cross-walk; (b) no meets/misses verification of REAL renders vs platform norms; (c) uncited/stale profile numbers; (d) CJK char-based per-platform targets.

## 3. The honest 7-tier ladder (en-US baseline)

| Tier | word_target | audiobook @150wpm | print pp @250w/pg | maps from |
|---|--:|--:|--:|---|
| T1 Quick Reset | 3,500 | 23 min | 14 | micro_book_15, compact_5ch_15 |
| T2 Mini | 4,500 | 30 min | 18 | micro_book_20, compact_5ch_20 |
| T3 Short | 6,000 | 40 min | 24 | short_book_30, compact_8ch_30 |
| T4 One-Hour | 9,000 | 60 min | 36 | one_hour_book (#1572) |
| T5 Standard | 22,000 | 147 min (2.45h) | 88 | standard_book, extended_book_2h |
| T6 Long-Form | 30,000 | 200 min (3.3h) | 120 | deep_book_4h |
| T7 Complete | 52,000 | 347 min (5.8h) | 208 | deep_book_6h |

## 4. Research — 7 platform clusters, 50+ cited 2026 sources

Fanned out 7 parallel research agents (KDP, Audible/ACX, Apple+Google, Spotify, YouTube, WEBTOON/LINE/Piccoma, CJK). Full citations in `PLATFORM_DURATION_SOURCES.md`. Validated/corrected vs CDIS §4:

| Platform | Winning length | CDIS verdict |
|---|---|---|
| **KDP** ebook/KU | 150–230pp / 35–50k w; KU pays per KENP page READ × ~$0.0045 (rising) | VALIDATED; price band → $2.99–9.99 (not $4.99 floor) |
| **Audible/ACX** | 5–7 hr / 45–63k w; floor 3 hr; à-la-carte price TIERED by finished hours | VALIDATED; **consumption-pool royalty live 2026-05-26** (50/30%, completion-weighted); "under-3hr collections" CORRECTED (no official collection — shorts disadvantaged by credit economics) |
| **Apple + Google** | length-agnostic flat per-sale (length=price justification, not payout); free AI narration **English only** (self-help eligible) | VALIDATED; **CJK audio walled** (neither AI-narrates ja/ko/zh; Apple Asia ≈ Japan only) |
| **Spotify** | audiobook 4–6 hr bias (15hr/mo at NORMAL speed → runtime scarce); podcast **20–40 min** | audiobook VALIDATED; podcast 20–30 **CORRECTED → 20–40**; `monetization_threshold 1200s` mislabeled (podcast floor, not Spotify rule) |
| **YouTube** | long **8–15 min** (retention-gated ≥50%); Shorts **15–60s (max 180s)**; trailer 60–90s; 8-min mid-roll | long 10–20 CORRECTED → 10–15; Shorts max **60→180s** (since 2024-10-15); 8-min VALIDATED |
| **WEBTOON/LINE/Piccoma** | no official panel rule (~8–12 min read / ~40–55 panels healing); series 25–30 ep; JP = short chapters + deep backlog + daily | Canvas 20–30 = creator heuristic; Lezhin 70+ → ~60-panel + ≥30-ep; iyashikei 55–65 → 40–55 |
| **CJK** | char-based: ja 2.15×/300cpm (HARD); zh 1.6×/190cpm; ko 2.0×/350cpm; Korea = Millie summary + Welaaa full | ja anchored; **zh + ko UNVERIFIED — gate on measured render** |

**Cross-cutting:** Findaway Voices ceased 2025-08-01 → INaudio + Spotify-for-Authors (config note stale). Every read-through surface (KU, Audible-new, Spotify, Kobo) pays on COMPLETED length.

## 5. The three findings that drive the strategy

1. **Only T7 "Complete" (52k / 5.8h / 208pp) wins the flagship paid-book surfaces simultaneously** — full KDP (150–230pp) + Audible (5–7h) + Spotify (4–6h). T6 (30k) is an entry full-audiobook (Audible 3–5h). **T1–T5 are podcast / short-read / lead-magnet plays — structural losers as standalone audiobooks** (sub-3h Audible floor, bottom price tier, negligible consumption-pool weight).
2. **Our REAL renders win NONE of the flagship paid-book surfaces.** Thin catalog ≈ 5k words (≈33 min) — only home is a single podcast episode. Gold/depth-fill ≈ 22k (≈2.4h) — a podcast season + KDP short-read, but under Audible's 3-hr floor. No render reaches T7 today.
3. **The routing config was built on the OLD wrong label.** `platform_knob_tuning.yaml` routed `standard_book`/`extended_book_2h` (2.3–2.5h) to Audible while stating `ideal_runtime_hours: 5`. Authored pre-#1550 (when standard_book was mislabeled "55 min"); #1550 fixed the label but never reconciled this routing → it silently routed sub-3h books to a 5h surface.

## 6. Config changes — PR #1574 (MERGED `ff0383efd`, RULE-0 clean, 0 deletions)

- **`config/catalog_planning/platform_knob_tuning.yaml`** — routing fix: `audible`/`spotify`/`apple_books`/`google_play`/`kobo` re-routed `[standard_book, extended_book_2h]` → `[deep_book_6h, deep_book_4h]` (the only tiers reaching their stated ideals); spotify `ideal_runtime_hours: 3→4`; findaway note refreshed (INaudio); Apple English-only AI narration + Google 6-language narration flags added.
- **`config/duration/platform_duration_profiles.yaml`** — cited + corrected: youtube sweet 600–1200→480–900s; youtube_shorts hard_max 60→180s; spotify podcast 20→40min + monetization relabel; audible consumption-pool model + "under-3hr collections" correction; **new `ladder_tier_platform_fit` cross-walk block** (lines ~210–231, the missing SSOT) + `cjk_provisional` block (lines 234–237).

## 7. Operator decisions (Tier-1 sign-off, recorded on PR #1574)

1. **Tier→platform routing — APPROVED → merged.** Audible/Spotify/KDP-full get T7/T6; short tiers → podcast/short-read/Ximalaya.
2. **52k "Complete" flagship — GREENLIT** → routed to the writing program (`CONTENT_LENGTH_TARGETS_FOR_WRITING_PROGRAM.md`).
3. **Thin-render shortfall — GREENLIT** as a writing-program depth/fill task.
4. **CJK gated on a measured render** — ja proceed; zh/ko measured by the in-flight validation session.

## 8. Content-length routed to the writing program (real length, never padding)

The dominant gap is content-length, not config. Routed targets:
- **#1 priority: a real 52,000-word "Complete" (T7 / `deep_book_6h`) flagship** — the only thing that wins Audible + full KDP. Persona-modified: millennial/corporate 52–63k; gen_z/working 45k.
- Close the thin-render shortfall (catalog renders ~5k vs target) — depth/fill, ≥70% completion.
- **Never pad** — padding loses the read-through revenue that motivates the length.
- CJK: ja ≈52k (in band); zh wants HIGHER (~65–95k, Ximalaya episodic); Korea = full + summary editions.

## 9. CJK provisional state

ja-JP anchored (expansion 2.15 measured, narration 300 文字/分 hard-sourced [C8][C9]). **zh (1.6×/190cpm) + ko (2.0×/350cpm) UNVERIFIED** — gate all CJK durations on a measured render. Pearl Star: Ollama UP (text measurement OK), **CosyVoice2 DOWN** (audiobook TTS timing blocked). Korea is a two-market split: ship BOTH a Millie summary (15–30 min) and a Welaaa full edition.

## 10. Cross-session coordination (this was NOT a solo session)

A **separate in-flight sibling session (`822b2bad`)** owns the follow-on orchestration. This session deliberately did **not** duplicate it (firing it from here would stampede a disk-full system + collide on worktrees):

- **Disk:** 17 GB free / 96% full → #1 (Lane-3) and #2 (validation) carry a ≥20GB worktree precheck → blocked until GC frees space.
- **Sibling GC:** classified 41 registered worktrees by **PR-state** (squash-merge masks ancestry, so merged-ancestor is the wrong signal); 25 have MERGED/CLOSED PRs → safe to remove; none overlap the 52-dir poison-zone. Running.
- **#3 de-poison:** PREPARED + PARKED awaiting explicit **"de-poison go"** (RULE-0 >50-file deletion: `.claude/worktrees/**` = 55 origin/main-tracked paths). Pure plumbing, reversible.
- **#1 Lane-3 (label layer)** + **#2 duration validation** (measures zh/ko on Pearl Star = executes decision item 4): queued, fire on GC success.

## 11. The two coordination seams + exact spec handed to the sibling

1. **zh/ko measurement must update TWO sites + reconcile a discrepancy.** When #2 lands measured zh/ko expansion: update the `cjk_provisional` block in `config/duration/platform_duration_profiles.yaml` (lines 234–237) AND `docs/DURATION_DERIVATION_SPEC_CJK_ADDENDUM.md` §2 (lines 39–42). **Partial flip only:** `expansion_char_per_word` → MEASURED, but `narration_cpm`/minutes stay PROVISIONAL until CosyVoice2 times a render (text-only ≠ TTS-timed; §4 gate not satisfied). **Reconcile:** ko-KR `narration_cpm` is `350` in the config but `330` in the addendum — converge them.
2. **#3 de-poison must be parented on current main + diff-gated.** Verify `git rev-parse $DEP^` == `ff0383efd3479a3191f2d1162f0394016b6cb068`; and `git diff --stat ff0383efd $DEP` shows ONLY `.claude/worktrees/**` deletions + 1 `.gitignore` line — **zero `config/` or `artifacts/` lines** (else it was built off a pre-#1574 base and would revert this session's merged work → rebuild via plumbing off `ff0383efd^{tree}`).

## 12. Open items / NEXT_ACTIONS

| Owner | Action |
|---|---|
| Operator | Approve sibling's GC kill-list (25 dead worktrees → frees disk) · give "de-poison go" for #3 when ready |
| Sibling `822b2bad` | Run GC → fire #1 (Lane-3 label layer) + #2 (validation) → keep #3 parked |
| #2 validation | Prove the HARD_FAIL on a thin en render; null-`runtime_format_id` no-escape audit; measure zh/ko TEXT expansion → update BOTH sites per Seam 1 |
| #1 Lane-3 | Build the customer-facing duration-label generator (consume the registry; surface the honest number to listings/epub) — the last mile that makes #1550's honest durations actually visible |
| Writing program | Build the real 52k "Complete" flagship; close the thin-render shortfall (real length, ≥70% completion) |
| Deferred | When CosyVoice2 `:9880` is up, TIME a zh/ko render to finalize the CJK narration_cpm/minutes constants |

## 13. Artifact & commit index

- **PR #1574** (MERGED `ff0383efd`): `config/duration/platform_duration_profiles.yaml`, `config/catalog_planning/platform_knob_tuning.yaml`, + `artifacts/research/duration_per_platform_20260613/**`
- **Deliverables** `artifacts/research/duration_per_platform_20260613/`: `DURATION_PER_PLATFORM_PLAN.md`, `PLATFORM_DURATION_SOURCES.md` (50+ cited), `DURATION_GAP_VERIFICATION.md`, `CONTENT_LENGTH_TARGETS_FOR_WRITING_PROGRAM.md`, `DURATION_PER_PLATFORM_DECK.{pptx,pdf}`, `build_deck.py`
- **Authority:** `specs/CONTENT_DURATION_INTELLIGENCE_DEV_SPEC.md`, `docs/DURATION_DERIVATION_SPEC.md`, `docs/DURATION_DERIVATION_SPEC_CJK_ADDENDUM.md`
- **Lineage:** #1550 (`8236c5e3c`) → #1572 (`c6de0be93`) → #1573 (`b1f705291`) → #1574 (`ff0383efd`)
