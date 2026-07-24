# EXECUTE — Pearl_Int: DashScope (Qwen/Alibaba Model Studio) Free-Tier for Video + Image + TTS

**EXECUTE. Do not stop at "I'll look into it" or a plan.** The turn ends only when you emit
`dashscope-free-media-report=<report-path-or-sha>` with a filled capability+quota table, OR one concrete
BLOCKER with evidence. This is a **read/investigate** lane — you produce a report + a probe result, not new
pipeline code. **You do NOT enter, print, or commit any API key** (operator-tier / enforcement-gated).

`BACKGROUND_SAFE=yes` · `PERSISTENCE_SURFACES=<report, probe log, offline branch>` ·
`RESUME_SURFACE=artifacts/research/dashscope_free_media_2026-07-19/REPORT.md`

## The operator's question (answer these, concretely)
1. Translation free credits look exhausted — **confirm** whether the DashScope account's free text/translation
   quota is actually spent (and what that means for other model families — is free credit shared or per-model?).
2. Can we do **video, image, and TTS** on the same account for **free**? For each: is there a free tier, **how
   much** (calls / tokens / seconds / images), **expiry**, and **rate limits**?
3. Which specific **model IDs** back each (video / image / TTS) on the **Singapore/international** Model Studio,
   and are they reachable with the current key?

## STARTUP_RECEIPT (emit before acting)
1. `git branch --show-current` · `git status --short` · `pwd` (must be `/Users/ahjan/phoenix_omega`).
2. `git fetch origin` → **EXPECTED 403 (account suspended).** Record `github=BLOCKED-403`; land OFFLINE; do not wait.
3. Read: `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` §Qwen/DashScope, `CLAUDE.md` (Critical URLs + **LLM Tier / BANNED paid-API policy**), `scripts/ci/integration_env_registry.py` (env-var names).
4. **Critical (from CLAUDE.md — do not guess/Google):** the console is **SINGAPORE only** —
   `https://modelstudio.console.alibabacloud.com/ap-southeast-1#/api-key`. **Beijing is WRONG.** Base URL is the
   `ap-southeast-1` (intl) DashScope endpoint, not the China endpoint. Quotas differ by region — report the **Singapore/intl** numbers, not China-console numbers.

## PROVENANCE
```
research:   NONE-NEEDED (capability investigation of an existing account/integration)
documents:  docs/INTEGRATION_CREDENTIALS_REGISTRY.md ; CLAUDE.md (URLs + tier policy)
builds_on:  DASHSCOPE_API_KEY/BASE_URL/MODEL (Keychain) ; existing caller scripts/translate_atoms_all_locales_cloud.py
inventory:  UNCHANGED (read/probe only) ; no existing DashScope *media* pricing doc → this report is NEW-ARTIFACT-JUSTIFIED
```

## MISSION — three evidence sources, reconciled
1. **Docs (authoritative pricing):** pull the **international (Singapore) Model Studio** free-tier terms for the
   three media families and record exact numbers + expiry + rate limits:
   - **Video:** Tongyi Wanxiang / **Wan** text-to-video & image-to-video model IDs (e.g. `wan2.x-t2v-*`, `wanx-*`).
   - **Image:** Tongyi Wanxiang image gen (`wanx-v1` / `wan2.x-t2i-*` family).
   - **TTS:** DashScope speech synthesis — **CosyVoice** + **Sambert** model families.
   Cite each figure with its source URL. Where intl-vs-China or new-user-vs-standing-account differs, say which applies to THIS account.
2. **Live account probe (EXECUTED-REAL, key never printed):** load the key from Keychain
   (`eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"` — verify by EXIT CODE, never `--verbose`,
   which leaks secrets), then hit the DashScope **models-list / metadata** endpoint (and, only if a documented
   free trial covers it, ONE minimal generation per family) to confirm which video/image/TTS models the key can
   actually reach. Record HTTP status + model availability; redact the key in all logs.
3. **Live balance (OPERATOR-GATED):** the remaining free-credit **balance / usage** is read from the Singapore
   console billing/usage page, which needs operator login (a credential/console action you do NOT perform). Put a
   crisp **OPERATOR ACTION** block in the report: exact page path + what to read off it, so the operator confirms
   the actual remaining balance in one look.

## POLICY GUARDRAILS (do not trip the enforcement gate)
- CLAUDE.md **BANS paid DashScope-cloud usage in repo code** (`llm-policy-enforcement.yml`). This lane is
  investigation + a capability doc for **operator-present, free-tier** media use — it does **not** wire paid
  media APIs into scheduled pipelines. Do NOT add a `DASHSCOPE_API_KEY` read to any workflow/pipeline; do NOT
  commit a key. If the report recommends a media capability, flag it as **operator-present / free-tier only** and
  note that productionizing it needs an explicit policy decision (`audit_llm_callers.py` must stay green).

## DELIVERABLES
- `artifacts/research/dashscope_free_media_2026-07-19/REPORT.md` — a filled table:
  `family | model_id(s) | free? | free amount | unit | expiry | rate limit | key-reachable(probe) | source URL`
  for **video / image / TTS**, plus the translation-quota finding, the shared-vs-per-model answer, and the
  OPERATOR ACTION block for live balance. Lead with a one-line **direct answer**: "Yes/No free, how much, per family."
- `artifacts/research/dashscope_free_media_2026-07-19/probe.log` — redacted probe transcript (status codes, model availability).
- Handoff `artifacts/coordination/handoffs/dashscope_free_media_2026-07-19.md`.

## DO NOT
- Do NOT print/commit/echo the API key or any secret; no `--verbose` on the Keychain loader (leaks). Redact in logs.
- Do NOT query the Beijing/China console or report China quotas as if they apply — Singapore/intl only.
- Do NOT wire DashScope into any workflow/pipeline or run a large paid batch — a free probe is 1 tiny call max per family, only if a documented free trial covers it.
- Do NOT claim a family is "free" without a cited source figure AND the key-reachable probe result.

## LANDING CONTRACT (github=BLOCKED-403 → OFFLINE)
Commit report + redacted probe log + handoff to local branch `agent/dashscope-free-media-20260719` via the
plumbing pattern (temp index off `origin/main^{tree}`, `GIT_LFS_SKIP_SMUDGE=1`, explicit `git add` paths,
gate `git diff --cached --stat origin/main` = exactly those files, **key confirmed absent from the diff**); record SHA; do not push.
Cleanup ledger: probe processes done, no secret in any tracked/scratch file, temp env unset.

## CLOSEOUT_RECEIPT (exact)
```
dashscope-free-media-report=<report-path-or-sha>
answer: video=<free?+amount> image=<free?+amount> tts=<free?+amount> translation-quota=<spent?/shared-or-per-model>
region=Singapore/ap-southeast-1  key-reachable: video=<y/n> image=<y/n> tts=<y/n> (probe HTTP codes in log)
github=BLOCKED-403 (landed offline: agent/dashscope-free-media-20260719 @ <sha>)
report=artifacts/research/dashscope_free_media_2026-07-19/REPORT.md  handoff=<path>
operator-action=<console billing page path to read live balance>  key-committed=NO  cleanup-complete=yes
acceptance-layer: EXECUTED-REAL (docs cited + live key probe); live BALANCE = OPERATOR-READ pending
```
