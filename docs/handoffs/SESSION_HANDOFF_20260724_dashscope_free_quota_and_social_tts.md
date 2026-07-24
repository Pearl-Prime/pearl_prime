# Session Handoff — 2026-07-24: Piper 100% pack, DashScope free-quota unlock, Social TTS plan

**Agent:** Piper (router) → Pearl_Int / Pearl_GitHub work
**Session date:** 2026-07-24
**Branch worked from:** `agent/bestseller-atom-flow-lanes-20260721` (dirty with unrelated prior sessions' work — all landings in this session used the plumbing-commit pattern off fresh `origin/main`, never this branch directly)
**HANDOFF_TO:** Pearl_Int (DashScope burn + TTS lanes) / Pearl_GitHub (PR #327 merge, security rotation escalation)

---

## 1. What was asked (chronological)

1. "Analyze yesterday's handoffs, document systems state, give me prompts to bring the repo to best 100% production, clean up old/bad stuff" → **Piper systems-state pack**.
2. "Why did manga stop at 37 episodes, I told it to do more" → found orphaned batch branches; explained the ramp-gate doctrine.
3. "Use Chrome, help me with DashScope billing block" → investigated the blocked `gmalone@oneteamtech.com` account.
4. "I gave pearl-int the key, we used it for zh-CN translations" (on a *different* account) → discovered `ahjansamvara@gmail.com`, a second healthy account with live free quota.
5. "I want to use the free DashScope stuff for one-time content-bank building — all DashScope until we exhaust free limits" → scoped a governance exception, found and landed pre-existing but never-committed DashScope free-media tooling, fixed a real bug in it, verified real content generation.
6. "Can we TTS all the social media stuff? English (2 cozy voices) + CJK" → discovery + a 5-lane TTS pack.
7. This handoff.

---

## 2. DONE this session (verified, not claimed)

### 2a. Piper systems-state pack — **PR #280, MERGED** (2026-07-24T02:46:13Z)
`docs/agent_prompt_packs/20260724_production_100pct_merge_cleanup/` — 7-lane pack (main-green, merge-queue drain, worktree/branch cleanup, SSOT reconciliation, brand-wizard regression, zh-TW Waystream wave-0, manga stranded-work landing) + `OPERATOR_ACTIONS.md` + plain-English `REPO_STATE_2026-07-24.txt`.
**STATUS: pack landed, lanes NOT yet dispatched.** This is the biggest open item — see §3.1.

### 2b. DashScope governance exception + real content burn — **PR #310, MERGED** (2026-07-24T06:52:06Z)
- Scoped a narrow, sunset-dated (2026-10-18) CLAUDE.md + CI exception for one-time free-quota image/video content-bank building — modeled on the existing PR #65 zh-CN-translation exception pattern. New CI rule `dashscope_free_media_rest_api` in `config/governance/banned_llm_patterns.yaml` (closes a real gap: the old rule only matched the native SDK shape, not this code's raw-HTTP calls — this code was silently unbanned before).
- Landed pre-existing, never-committed DashScope free-media tooling from a prior (2026-07-19) session: `scripts/social/dashscope_free_media.py`, `run_dashscope_free_media_burn.py`, `ingest_dashscope_free_media_bank.py`, `run_cjk6_free_tier_translate.sh`, tests, research artifacts.
- **Found and fixed a real bug** (follow-up commit on the same PR): `force_singapore_env()` was hardcoding `DASHSCOPE_NATIVE_BASE_URL` to the generic `dashscope-intl.aliyuncs.com` host, silently breaking image generation for workspace-scoped keys (`sk-ws-...`). Fixed to derive via `dfm.native_base()`'s own workspace-aware logic. 3 new regression tests, 13/13 passing.
- **Live-verified real content generation** on account `ahjansamvara@gmail.com`, key "new pearl prime" (API-key console ID 952604, stored in macOS Keychain as `DASHSCOPE_FREE_QUOTA_API_KEY`, service `phoenix-omega`):
  - `artifacts/social_media_dashscope_free_2026-07-20/video/wan27_t2v__anxiety__k00.mp4` — real 2.4MB MP4, valid ISO Media container.
  - `artifacts/social_media_dashscope_free_2026-07-20/stills/diagnostic_test_01.png` — real 995KB PNG, 720×1280.
  - These two files are **currently untracked/uncommitted** in the working tree — not yet landed to git (they're test artifacts; decide whether to commit as samples or leave local).
- **⚠️ CAUTION — Core tests / Drift detectors / Release gates now show FAILURE on PR #310's post-merge check status** (re-checked live at handoff time). Not diagnosed this session — could be pre-existing chronic main redness (repo-documented pattern) or something this PR introduced. **First job for next session: run `gh pr checks 310` / check main's current CI state and determine which.**

### 2c. Social-media TTS discovery + 5-lane pack — **PR #327, OPEN, not yet merged**
`docs/agent_prompt_packs/20260724_social_tts_en_plus_cjk6/` — Lane 1 (finish English voice bank on CosyVoice2, correct script), Lane 2 (CJK6 gotcha research), Lane 3 (CJK6 translation), Lane 4 (CJK6 voicing + CosyVoice2-vs-Qwen3-TTS A/B), + dispatcher + plain-English state doc.
Key discoveries baked into the pack (verified via 3 parallel research agents):
- English is **not actually voiced yet** — only 8 audition clips exist, no production bank.
- `generate_voice_bank.py` (the "obvious" script) **skips the text-prep/gotcha rules** — bug. Use `generate_voice_bank_onbox.py` instead.
- DashScope cloud TTS free quota (10k–110k chars) **cannot cover a bank** (~249k chars for English alone) — sampling/A-B tool only. Self-hosted CosyVoice2 (unlimited) is the real engine; self-hosted open-weights Qwen3-TTS is the A/B challenger.
- Free-TTS capability matrix for all 14 project locales: 7 premium-free (CosyVoice2: en/ja/ko/zh-CN/zh-TW/zh-HK/zh-SG), 6 good-free (Edge-TTS: de/fr/es-ES/es-US/it/pt-BR), 1 paid-recommended (ElevenLabs: hu).

---

## 3. OPEN — ranked by priority

### 3.1 Dispatch the Piper 100%-production pack lanes (HIGHEST — was never started)
PR #280 merged the *plan*, but none of its 7 lanes have been dispatched. Read `docs/agent_prompt_packs/20260724_production_100pct_merge_cleanup/00_MASTER_DISPATCH_PROMPT.md` and dispatch. **Re-verify everything first** — the pack's PR/branch numbers are 2026-07-24-morning snapshots and the repo has moved since (multiple PRs merged/opened in the hours after, e.g. #306–#309, #327).

### 3.2 Diagnose PR #310's post-merge CI failures
`Core tests`, `Drift detectors`, and `Release gates` show FAILURE on the merged PR's check list. Unknown if pre-existing/unrelated or caused by this change. Run `bash scripts/run_production_readiness_gates.py` or equivalent on current `origin/main` HEAD to isolate.

### 3.3 Merge PR #327 (social TTS pack)
Currently OPEN, `mergeable: UNKNOWN`. Live CI red on Core tests, Drift detectors, Release gates; verify green before merge, or dispatch Lane 1 directly from the local pack files (doesn't require the PR merged first — Lane 1 is self-contained).

### 3.4 Real security leak — still unrotated
`docs/CREDENTIAL_HUNT_DEV_SPEC.md:91` has a live-looking `DASHSCOPE_API_KEY` value (`sk-3404112742fa4bbc9250df92e4f7853f`) in plaintext, **publicly on `origin/main` since 2026-04-03**, confirmed still present at handoff time. This is the OLD routine-fallback key, separate from today's `DASHSCOPE_FREE_QUOTA_API_KEY`. **Operator action required**: rotate this key on Alibaba Cloud (whichever account owns it — not yet determined which). Doc cleanup alone doesn't fix it (git history retains it). Also duplicated across 4 stale worktrees (`.claude/worktrees/*`, `.worktrees/teacher-ob-20260721`) — those can be deleted once confirmed merged/dead (see PR #280's Lane 03 cleanup list).

### 3.5 The gmalone@oneteamtech.com stale "Account Overdue" flag — never resolved
Separate, unresolved thread from earlier in the session: `gmalone@oneteamtech.com`'s ModelStudio console shows "Account Overdue" / "Some Features Restricted" despite **$0 owed everywhere** (verified across July and April billing cycles) and valid payment methods on file. This looks like a stale platform-side flag, not real debt. We pivoted to using the healthy `ahjansamvara@gmail.com` account instead rather than resolving this — it's still broken and gmalone's DashScope access is still blocked. Not urgent (workaround exists) but worth an Alibaba support ticket if that account is needed later. See `OPERATOR_ACTIONS.md` (in the Piper 100pct pack) item A/D for related credential/billing items.

### 3.6 Run the actual DashScope free-quota burns
Governance is landed, the pipeline is proven real, but only 1 test video + 2 test images exist. Two burns are ready to execute (both are Piper-pack Lane work, see §2b/§2c):
- **Media content bank** (image/video for social/manga reference): `scripts/social/run_dashscope_free_media_burn.py --max-stills 100 --max-t2v-s 50 --max-i2v-s 50` (env setup in PR #310's body / this doc §4).
- **English voice bank**: `scripts/social_media/generate_voice_bank_onbox.py` per PR #327 Lane 1's exact invocation.
Both need `PHOENIX_DASHSCOPE_FREE_MEDIA_ALLOW=1` (or the TTS lane's equivalent operator-present gate) set by hand — never in CI/cron. Free quota expires **2026-10-18** — genuine time pressure to actually run these, not just plan them.

### 3.7 CJK6 TTS gotcha research + translation (PR #327 Lanes 2–4)
Not started. Six languages need per-language TTS text-prep rules + translation before voicing. See pack for the full spec. Hard rules: zh-HK must render Cantonese (`yue`), zh-TW translation is Claude-only (never Qwen — it emits Simplified).

---

## 4. Working environment notes (save future sessions the rediscovery)

**DashScope free-quota account:** `ahjansamvara@gmail.com`, Model Studio Singapore (`ap-southeast-1`), Default Workspace. API key "new pearl prime" already in Keychain as `DASHSCOPE_FREE_QUOTA_API_KEY` (service `phoenix-omega`). Workspace-specific endpoint (**required** — the generic `dashscope-intl.aliyuncs.com` host does not work for this workspace-scoped key, though the post-fix code now derives this automatically):
```
https://ws-tbjufzktkzczfmhj.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1
```

Standard invocation pattern going forward:
```bash
cd /Users/ahjan/phoenix_omega
eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
export PHOENIX_DASHSCOPE_FREE_MEDIA_ALLOW=1
export DASHSCOPE_BASE_URL="https://ws-tbjufzktkzczfmhj.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1"
# DASHSCOPE_NATIVE_BASE_URL no longer needs manual export (fixed in PR #310 follow-up)
```

**Browser session gotcha:** the claude-in-chrome extension shares ONE cookie jar across all tabs — logging into a different Alibaba Cloud account in any tab switches the session for every tab pointed at that origin. Don't assume "tab X = account Y" without re-checking; open a fresh tab and re-verify if account identity matters.

**Free quota expiry: 2026-10-18** (all DashScope free-tier allocations on the ahjansamvara account, Singapore region only). ~86 days from this session — real deadline for §3.6/§3.7.

---

## 5. What NOT to re-litigate

- Do not re-investigate "which DashScope account to use" — settled: `ahjansamvara@gmail.com` for free-quota one-time work, `gmalone@oneteamtech.com` unused/blocked (§3.5), a third routine-fallback `DASHSCOPE_API_KEY` exists for CI/Tier-2 paid-fallback use (unrelated, unrotated leak at §3.4).
- Do not redesign the DashScope governance exception — PR #310 already landed the narrow, sunset-dated, code-enforced version (`PHOENIX_DASHSCOPE_FREE_MEDIA_ALLOW=1`, dedicated key, 3 files only). Extend its `exempt_paths` list if new one-time scripts need it; don't loosen the pattern.
- Do not re-derive the free-TTS engine matrix — it's in `TTS_STATE_2026-07-24.txt` and PR #327's discovery agents' findings, saved to memory (`project_social_media_tts_state.md`).

---

## CLOSEOUT_RECEIPT

```
STATUS: partial (2 PRs merged (#280, #310), 1 open (#327); 2 of 3 major threads have zero lanes executed yet)
HANDOFF_TO: Pearl_Int (execute Piper pack lanes + TTS Lane 1) / Pearl_GitHub (diagnose #310 CI, merge #327)
prs_merged: #280 (2026-07-24T02:46:13Z), #310 (2026-07-24T06:52:06Z)
prs_open: #327 (mergeable: UNKNOWN; CI red on Core tests / Drift detectors / Release gates)
real_artifacts_verified: 1 video (2.4MB mp4), 2 images (995KB + earlier test png) — genuine bytes, not stubs
security_finding_unresolved: docs/CREDENTIAL_HUNT_DEV_SPEC.md:91 leaked key, public since 2026-04-03, needs operator rotation
top_priority_next_action: dispatch docs/agent_prompt_packs/20260724_production_100pct_merge_cleanup/00_MASTER_DISPATCH_PROMPT.md (re-verify live state first — nothing in it has been executed)
free_quota_deadline: 2026-10-18
acceptance_layer: EXECUTED-REAL (governance + pipeline + first real content) — CODE-WIRED (TTS pack, unexecuted) — nothing PROVEN-AT-BAR (no operator listen/look yet)
```
