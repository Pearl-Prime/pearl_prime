# Q5 — Top Production Cliffs (ranked by ROI × blast radius)

**Date:** 2026-04-29

**Method.** Each cliff has: severity, blast_radius (how many subsystems it gates), effort_to_fix (operator-hours / engineer-days), ROI tier (S = system-unblocking; A = subsystem-unblocking; B = quality), and phase tag (Phase 0–6 of the pathway). Sorted by chronological-shipping order (Phase 0 first), then by ROI within phase. Reference cliffs surfaced in [`q4_*`](.) [`q6_spec_drift.md`](./q6_spec_drift.md) [`q8_ci_health.md`](./q8_ci_health.md) [`q10_repo_cruft.md`](./q10_repo_cruft.md).

## Phase 0 — Foundation & safety (must precede all else)

### C1. main branch ruleset is permissive [P0 — S, Phase 0]
- **Evidence:** `gh api repos/.../rulesets/13451138` (live ruleset "Protect main") requires only `Verify governance` as status check. `BRANCH_PROTECTION_REQUIREMENTS.md` and `PEARL_PRIME_RELEASE_CONTRACT.md` name 4 different required checks (`Core tests`, `Release gates`, `EI V2 gates`, `Change impact`). Required reviewer count = 0. Bypass actor = RepositoryRole, `bypass_mode: always`.
- **Why it bites:** PR #245 class incidents (mass deletion) currently rely on a single `pr-governance-review.yml` workflow as a brittle backstop. Deletion-blocker bypassable by any repo-role-5 user.
- **Effort:** 30 min (gh api PATCH to update ruleset rules; smoke a guard PR).
- **Risk if skipped:** Production-grade incidents. Already had one (#245).

### C2. 5 workflows reference banned `secrets.CLAUDE_API_KEY` [P0 — A, Phase 0]
- **Evidence:** Per `q8_ci_health.md` §Banned-secret drift. Specific files: `manga-quality-forensic-analysis.yml`, `manga-series-pitch.yml`, plus 3 others (full list in q8). CLAUDE.md tier policy bans Anthropic API in repo code.
- **Effort:** 1 hour to remove or replace.
- **Risk if skipped:** LLM tier policy enforcement is theatrical; pipeline could exfil to paid Anthropic API.

### C3. `change-impact.yml` 0/30 pass rate [P0 — A, Phase 0]
- **Evidence:** q8 §B. PR-triggered, gates_main flag set, broken. If branch protection is restored to require this check, every PR blocks.
- **Effort:** 2 hours (debug the workflow's failure).
- **Risk if skipped:** can't restore branch protection to spec.

### C4. INTEGRATION_CREDENTIALS_REGISTRY missing 3 APIs [P1 — B, Phase 0]
- **Evidence:** q6 spec drift. Missing DeepSeek, Google AI Studio (Gemini), Cloudflare R2 (`R2_*`) — all referenced in `scripts/ci/integration_env_registry.py` but undocumented.
- **Effort:** 30 min doc-only PR.
- **Risk if skipped:** new operator can't load env; "single canonical reference" claim is false.

### C5. `pearl-star-health.yml` 0/30 pass rate, cron */30 [P1 — B, Phase 0]
- **Evidence:** q8 §A. ~672 false alerts/fortnight.
- **Effort:** 1 hour (fix or disable).
- **Risk if skipped:** alert noise hides real signals.

### C6. EI V2 still advisory; promotion gate not exercised [P1 — A, Phase 0]
- **Evidence:** `ei-v2-gates.yml:5` says V2 advisory. `artifacts/ei_v2/learned_params.json` (292 B) ≈ `learned_params_seed.json` (290 B). 18 modules + 21 tests not load-bearing.
- **Effort:** 1 engineer-day to land first promotion gate run + flip a flag.
- **Risk if skipped:** quality safety net is decorative.

## Phase 1 — Catalog → storefront (the revenue floor)

### C7. No EPUB packager exists [S, Phase 1]
- **Evidence:** `scripts/publish/` contains `kdp_comics_upload.py` and `webtoon_canvas_upload.py` (manga). No `build_epub.py`, no `book_packager.py`, no equivalent. Authored chapter prose in `artifacts/audiobook_samples/_prose/` has no path to package.
- **Effort:** 2-3 engineer-days (epub-builder lib + cover/metadata/TOC + validation against KDP spec).
- **Why it's the BIGGEST cliff:** the entire content factory has no terminal output. 2,584 atoms + 14 teachers + 270+ master arcs cannot become 1 sellable book.

### C8. No KDP submission pipeline [S, Phase 1]
- **Evidence:** No automation against KDP API or kdspy. Operator-manual submission only.
- **Effort:** 3-5 engineer-days for first KDP-comics submission automation; 5-10 for full books (KDP requires manual review queue interaction).
- **Risk if skipped:** packaging is moot if you can't submit.

### C9. No Apple Books, no LINE Manga submission [A, Phase 1]
- **Effort:** 2-3 engineer-days each.
- **Risk if skipped:** locale-ship paths blocked.

### C10. PHOENIX_OMEGA_MASTER_CATALOG_PLAN.md does not exist [B, Phase 1]
- **Evidence:** `ls docs/PHOENIX_OMEGA_MASTER_CATALOG_PLAN.md` → No such file. The audit anchor list (CLAUDE.md doesn't reference it, but the brief did).
- **Effort:** 1 day to write the doc that scopes catalog → storefront.
- **Risk if skipped:** Phase 1 has no canonical plan.

## Phase 2 — Pearl Prime book pipeline

### C11. `--pipeline-mode spine` is canonical but code defaults to `registry` [P0 — S, Phase 2]
- **Evidence:** q6 §B.2. Canonical spec (PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md:15-23) says spine MUST be the path. `scripts/run_pipeline.py:1438-1444` default = "registry" (legacy).
- **Effort:** 30 min (flip default + add --pipeline-mode-legacy override) + smoke regression.
- **Why it's load-bearing:** every silent caller is using legacy. Drift-debt accrues every day.

### C12. Pearl Prime sentinel acceptance evidence absent [A, Phase 2]
- **Evidence:** `docs/PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md:99` defines sentinel acceptance tuple. `ls artifacts/sentinel/` returns empty.
- **Effort:** 1 engineer-day to wire + run.
- **Risk if skipped:** the spec's Definition of Done is unverifiable.

### C13. Audiobook full-book TTS path never exercised [A, Phase 2]
- **Evidence:** 13 `*_ch1.mp3` in `artifacts/audiobook_samples/`, no multi-chapter, no full-book. `audiobook-regression.yml:3` says "Full regression (requires LM Studio) runs on manual dispatch only".
- **Effort:** 2 engineer-days (multi-chapter concat + chapter-marker MP4/M4B + cover).
- **Phase tag:** Phase 2 — gates audiobook ship.

### C14. Video pipeline outputs only test renders [A, Phase 2]
- **Evidence:** `artifacts/video/` has only test renders + image_banks + provenance.
- **Effort:** 2-3 engineer-days for first end-to-end book→video.

## Phase 3 — Manga pipeline

### C15. 35 panel prompts, 0 chapter-bound renders [S, Phase 3]
- **Evidence:** `artifacts/manga/panel_prompts/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/ep_001.panel_prompts.json` has 35 prompts. `artifacts/manga/episodes/` empty. Pipeline ratio 35:0.
- **Effort:** Operator GATE-OP-1 (R2 secrets) + GATE-OP-2 (Pearl Star marker) + 1 GPU run (~2 hours wall time on Pearl Star).
- **Phase tag:** Phase 3 entry gate. **Single highest-ROI manga action.**

### C16. PR #802 drift autopsy: schnell-fp8 misconfig + en_US locale suppression [A, Phase 3]
- **Evidence:** PR #802 §0-§2: `flux1-schnell-fp8.safetensors` running steps=24/cfg=4.0 (anti-pattern; schnell is 4-step distilled). `no text, no typography` smuggled into POSITIVE prompt → hallucinated kanji. en_US locale-hint suppresses manga prior.
- **Effort:** ½ engineer-day to reconfigure FLUX prompts + steps/cfg.
- **Why it's load-bearing:** the 840 image_bank PNGs prove "we can render at volume" but PR #802 proves "what we render is off-brand." Fix unlocks brand-on render quality.

### C17. LoRA training VRAM blocked [A, Phase 3]
- **Evidence:** PR #623 (open, CONFLICTING) — Pearl Star RTX 5070 Ti 16 GB; FLUX-schnell-fp8 takes 10.6 GB; OOM. 3 exit options: GPU upgrade ≥24GB / cloud $600-1500 / IP-Adapter. No decision.
- **Effort:** Decision is the work. Implementation 2-4 engineer-days regardless.
- **Why it's load-bearing:** 12 of 37 brand LoRAs have plan entries; 0 have trained weights. Brand-on character consistency is impossible without LoRA OR IP-Adapter.

### C18. 132 stale series_plans + 716 stale book_plans deletion not landed [B, Phase 3]
- **Evidence:** Per q6 / proj_manga_catalog_reconciliation_20260426 §OQ-4 atomic deletion. Code accepts post-cutover `VALID_GENRES` while YAMLs remain pre-cutover.
- **Effort:** 1 day for atomic PR (delete YAMLs + bump VALID_GENRES coherently).

## Phase 4 — Surfaces & ops

### C19. Marketing has 1 funnel of ~26 expected [A, Phase 4]
- **Evidence:** `funnel/burnout_reset/` is the only funnel. `platform_marketing/` doesn't exist.
- **Effort:** 1 engineer-week per funnel × 25 = unrealistic without templating; 3 engineer-days for funnel-builder template + 1 day per funnel after.

### C20. brand_admin has 0 tests, dashboard is doc-only [B, Phase 4]
- **Evidence:** q9 test reality: `find tests/ -name '*brand_admin*'` = 0. `docs/PIPELINE_DASHBOARD_INDEX.md` is markdown, not interactive.
- **Effort:** 5 engineer-days for interactive dashboard + 2 days for brand_admin test harness.

### C21. Pearl News daily cron pass rate 57% [B, Phase 4]
- **Evidence:** q8 §B. 16/28 pass.
- **Effort:** 1 day debug.
- **Note:** the *site* is live; the *cron* is flaky.

### C22. Storefront_distribution has no spec doc [B, Phase 4]
- **Evidence:** No authority doc; not in SUBSYSTEM_AUTHORITY_MAP; partial code in scripts/publish/.
- **Effort:** 1 day to write spec → opens C8/C9 for execution.

## Phase 5 — Multi-locale + podcast

### C23. Translation: zh_CN ~2,200 atoms pending [S for zh_CN ship, Phase 5]
- **Evidence:** `proj_manga_first_ship_20260425` blockers. zh_TW 92.1%, ja_JP 89.3% with ~366 remaining, zh_CN ~2,200 pending.
- **Effort:** 1 engineer-week of Qwen-batch authoring + validation (no operator-attended LLM cost on Pearl Star).

### C24. Podcast pipeline at 1 pilot, no episode published [A, Phase 5]
- **Evidence:** q4 book cluster. `artifacts/podcast_pilot/pilot_report.md` only. `config/integrations/podcast_credentials.yaml` and `pearl_news/research/podcast/` don't exist (referenced by authority map).
- **Effort:** 3-5 engineer-days (RSS feed, Anchor/Spotify submit, episode pipeline).

## Phase 6 — Full automation

### C25. Recommendations subsystem at 15% — `backlog` per authority map [B, Phase 6]
- Defer until Phase 5 ship cadence is real.

## Cross-cutting cliffs

### C26. 25 of 42 open PRs are CONFLICTING; 11 are >14d old [B — process, all phases]
- **Evidence:** q2 + q10. Sweep needed.
- **Effort:** 4 operator-hours.

### C27. 128 squash-merged remote branches lingering on origin [B — process, all phases]
- **Evidence:** q10 §B. 174 of 216 remote branches have no open PR.
- **Effort:** 30 min bulk delete (after `git log origin/<b> ^origin/main` confirmation).

### C28. 14 BROKEN + 13 DEAD CI workflows [B — process, all phases]
- **Evidence:** q8. 27 of 75 (36%) workflows are broken or dead.
- **Effort:** 1 engineer-week at 5/day for triage.

### C29. brand_admin has 0 tests [A — testing, Phase 4]
- **Evidence:** `find tests/ -name '*brand_admin*'` = 0. Per q4 ops, brand_admin is 55% with ratified DASH-02 path.
- **Effort:** 2 engineer-days first test harness.

### C30. Test cliffs in revenue-adjacent code [B, all phases]
- **Evidence:** marketing 5 tests, freebie 5, recommend 5, pearl_prime 5, audiobook 3, podcast 2, brand_admin 0. Pearl_news 15, manga 52, ei_v2 21.
- **Pattern:** revenue-producing surfaces are under-tested.

## Headline summary

**Top 5 cliffs by ROI × blast-radius:**

1. **C7 — No EPUB packager exists** (S, Phase 1, 2-3 engineer-days). Single biggest unlock. Without it, the entire book content factory is sterile.
2. **C15 — 35 panel prompts, 0 chapter-bound renders** (S, Phase 3, ~2 hours operator + GPU). Operator-side, fast, unblocks the manga pipeline first ship.
3. **C1 — main branch ruleset permissive** (S, Phase 0, 30 min). Cheap fix, prevents recurrence of mass-deletion incidents.
4. **C8 — No KDP submission pipeline** (S, Phase 1, 3-5 engineer-days). Pairs with C7 for revenue-floor unlock.
5. **C11 — `registry` is silent default instead of `spine`** (S, Phase 2, 30 min). Drift-debt that compounds daily.

Of those: **C1, C11, C15** are sub-day fixes. They should land within the next 48 hours.
