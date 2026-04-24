# Session Handoff — 2026-04-24

**Session:** great-shannon-21dadc  
**Author:** Pearl_PM (Claude agent)  
**Audience:** next operator / next agent session  
**Purpose:** Single source of truth for where Phoenix Omega stands after this session — what shipped, what's running, what's open, and the correct CLIs for the next run.

---

## 1. Executive Summary

| Area | State | Next Action |
|------|-------|-------------|
| **Pearl Prime text pipeline** | Gates green (149/210 conformance pass) but **rendered content has quality defects** — persona voice leak, ch1 contract not enforced, template stamps not caught by dedup. | Use `run_pipeline.py --render-book` loop (NOT `run_canary_100_books.py` which is plan-only) for QA-able books. |
| **Wave-2 translations** | **100% closed** through commit `636c54f3` (6 P4 banks + 40 atom siblings across `zh_TW` + `ja_JP`). | None. |
| **Pearl Star (Ubuntu inference box)** | **All 3 services green** (SSH:22, Ollama:11434, ComfyUI:8188, CosyVoice:9880) via tailnet hostname `pearlstar.tail7fd910.ts.net`. Keychain updated off stale LAN IP. | None. |
| **Brand 1 image bank — stillness_press** | **840/840 PNGs** complete (15 topics × 4 intents × 7 styles × 2 ratios). On main. | None. |
| **Brand 2 image bank — cognitive_clarity** | **224 PNGs** across 4 topics (boundaries, burnout, imposter_syndrome, overthinking × 56 each). ComfyUI run complete. | Decide whether spec calls for more topics or this is done. |
| **Manga catalog plans** | **All 8 docs merged to `origin/main`** via PRs #413, #476, #497 + prior commits. | Build the code the plans describe (see §5). |
| **Manga book-production layer** | **1.4% of required panel count; 0.005% of required pixel area.** Writer is a stub, FLUX not connected, compositor is a filmstrip, lettering never renders. | Sprint 0 foundation fixes. |
| **Conformance sprint — gen_z_student** | POOL_TOO_SHALLOW (3<12) + BAND_DEFICIT (missing bands 1/4/5). Agent killed mid-task. | Deepen STORY pools — blocks 35 combos. |
| **Phase E (CI guard + hard-fail)** | Not started. | After gen_z_student pool fix. |

---

## 2. What Shipped This Session

### 2.1 Code / config merged through commit chain
- `f41855003` — arc schema fix
- `1e8f22331` — wordcount gate tuning
- `1e723efb6` — registry F3 diversity
- `3f3da0c76` — paragraph splitter
- `f4e4a1624` — tighter splitter
- `0ba2ebfd4` — 2nd REFLECTION slot
- `61e173760` — missing educator atom banks
- `636c54f3` — full wave-2 translation backlog (zh_TW + ja_JP)

### 2.2 Infrastructure changes
- **Keychain migration:** `PEARL_STAR_IP` replaced with tailnet hostname `pearlstar.tail7fd910.ts.net` (Tailscale MagicDNS → `100.92.68.74`). All three `phoenix-omega` keychain accounts updated (`PEARL_STAR_IP`, `QWEN_BASE_URL`, `COMFYUI_URL`). Connectivity verified.
- **ComfyUI brand 2 launch:** cognitive_clarity image bank fired (PID 65800); completed at 224 PNGs.

### 2.3 No new docs shipped this session until this handoff
All manga catalog/plan docs already on main (see §4).

---

## 3. Authoritative CLIs (do not conflate)

| Goal | Correct CLI | Notes |
|------|-------------|-------|
| **100 rendered 1hr books across personas × topics** | `scripts/run_pipeline.py --render-book --render-formats txt --render-dir artifacts/prime_100/<slug>/` in a loop over sampled arcs | THE production path. Renders prose. |
| **Plan-level canary (release evidence)** | `scripts/ci/run_canary_100_books.py` | **NOT for QA** — only produces plan JSONs. Does not render prose. Cannot catch persona leaks, ch1 contract violations, template stamps. |
| **Conformance gate sweep** | `scripts/conformance/full_sprint.py --combos all --variations N --parallel 4` | Fires gates 1–8 per combo. Used for 149/210 pass report. |
| **Release readiness** | `scripts/run_production_readiness_gates.py` | Sign-off gates. |
| **System test** | `scripts/ci/run_rigorous_system_test.py` | End-to-end. |
| **Rollback smoke** | `scripts/release/rollback_smoke.sh` | Release workflow: `.github/workflows/release-gates.yml`. |
| **Manga chapter (single)** | `scripts/manga/run_manga_chapter.py --workspace ... --backend replay --export-pdf` | Per-chapter. No volume orchestrator exists. |
| **Manga series setup** | `scripts/manga/run_series_setup.py --series-id ... --arc-id ... --genre-id ... --brand-id ... --topic ... --locale ...` | One-time per series. |

**Rule:** canary green ≠ book readable. Content defects are post-plan / render-time; canary never runs the renderer.

---

## 4. Manga Plans — All Merged to `origin/main`

| Doc | Path | Merged via |
|-----|------|-----------|
| Catalog plan (12 teachers × 26 brands × 10 genres × 15 topics) | `artifacts/manga/MANGA_CATALOG_PLAN.md` | `b1ae8ca54` + #413 |
| Full catalog plan (extended) | `artifacts/manga/MANGA_FULL_CATALOG_PLAN.md` | `b1ae8ca54` + #413 |
| Volume + assets handoff | `docs/MANGA_CATALOG_VOLUME_AND_ASSETS_HANDOFF_2026_04_17.md` | PR chain |
| Quality gap plan (6 sprints, ~200 dev-hrs) | `docs/MANGA_QUALITY_GAP_PLAN.md` | #476 |
| Implementation outline | `docs/MANGA_IMPLEMENTATION_OUTLINE.md` | on main |
| Production pipeline | `docs/MANGA_PRODUCTION_PIPELINE.md` | on main |
| Cover design sprint handoff | `docs/MANGA_COVER_DESIGN_SPRINT_HANDOFF.md` | #497 |
| GTM plan | `docs/MANGA_GTM_PLAN.md` | on main |

**Stillness Press scope per catalog:** 24 series, 1,970 titles. Example rows:
- SP-001 *The Alarm Is Lying* — iyashikei / anxiety / Hana Tidecalm / 80 vols
- SP-003 *The False Emergency* — shonen / anxiety / Blaze Stormhammer / 85
- SP-006 *The 3am Mind* — horror / sleep_anxiety / 80

**Plans are merged; code they describe is not yet built.**

---

## 5. Open Work (Prioritized)

### P0 — Pearl Prime text quality (BLOCKERS for 100-book run)
1. **Persona voice leak** — gen_z content ("Gen Z professionals across years", "first real job", "gig economy precarity") appears in midlife_women books. Wrong atom scoping. Previous fix agent was fired then stopped by user; nothing committed.
2. **Ch1 contract not enforced at render time** — mechanism language ("The mechanism I want to name is the alarm as accurate data") leaking into the recognition chapter. Contract says ch1 `max_exercises=0`, emotional_job=recognition, reader_promise "names the pain without exercises yet" — enforce in render gate.
3. **Template stamp dedup miss** — patterns like `"Your chest tight at the ping. / Your restless legs under the desk. / Your thumb scrolling. The nervous system is reading the environment correctly. The threat is real. The activation is proportional."` appear 3× in one book. 20-word dedup window misses stamp-with-fill patterns. Widen window or hash normalized stems.
4. **Loc-var fragments** — "morning sun cutting through the blinds on your jacket sleeve", "the the bus moves". `_fill_locale_tokens()` not catching all substitutions or producing malformed joins.

### P0 — Conformance
5. **Deepen `gen_z_student` STORY pools** — POOL_TOO_SHALLOW (3<12), BAND_DEFICIT (bands 1/4/5 missing). Blocks 35 combos from 149/210 → higher. Prior agent killed mid-task.
6. **Phase E CI guard + hard-fail + stale test patch** — gated behind #5.

### P1 — Manga (Sprint 0 from `MANGA_QUALITY_GAP_PLAN.md`)
7. Replace `phoenix_v4/manga/chapter/writer_stub.py` with real chapter writer (spec exists: `specs/MANGA_CHAPTER_WRITER_SPEC.md`).
8. Connect FLUX backend — currently all 80 panel images are identical 64×64 placeholders (same SHA-256 `46413733d3...`).
9. Fix chapter scoping — runs as `ch_10` not `ch_01`; chapters 2–9 are stub dirs.
10. Prefix panel IDs with chapter ID (currently all chapters share 12 images).
11. Wire pipeline output path → PDF builder input path (they're disconnected today).
12. Add gutter/border pass to `page_compose.py` (panels currently flush, bleed into each other).
13. Add idempotency guard to series memory writer (12 identical `chapter_pipeline_completed` entries).

### P1 — Catalog → Volume orchestrator
14. **Build `scripts/manga/run_catalog_manga_volume.py`** — reads a machine manifest (not markdown) derived from `MANGA_CATALOG_PLAN.md`. Per row: resolve series metadata → `run_series_setup.py` → loop `run_manga_chapter.py` 1..N → merge chapter PDFs into one volume artifact (PyMuPDF / pypdf / Pillow).
15. **Generate the manifest:** `config/manga/catalog_manifest.yaml` from `MANGA_CATALOG_PLAN.md` rows (one-off CI script; don't parse markdown at runtime).

### P2 — Manga sprints A–E
16. Sprint A: Series identity layer (~20 hrs) — `scripts/manga/series_identity_init.py` + schema.
17. Sprint B: Character + setting consistency (~60 hrs) — CHARACTER_SHEET_BUILD, IP-Adapter, CLIP ≥0.82 gate.
18. Sprint C: Name/thumbnail stage (~40 hrs) — irregular grids, wireframe PDF review before FLUX.
19. Sprint D: Lettering/bubble integration (~20 hrs) — in flight (spec `bubble_rendering_engine` 8d0285cedc).
20. Sprint E: Visual quality gates MQG-01..08 (~20 hrs) — depends on C.

### P3 — Housekeeping
21. `config/content_banks/loc_var_render.yaml` format error ("expected variants list or bank sections of variant records") — Pearl_Writer falls back to `global_flow_glue_bank`. Not blocking.
22. Recognition bank coverage — only `gen_z_professionals × anxiety` has a curated bank (40 variants). 14 other P1–P5 combos in `docs/RECOGNITION_BANK_SPEC.md` have no bank; fall back to generic HOOK atom pool.
23. `BookSlotTracker` not threaded through `scripts/run_pipeline.py` (only wired in the pilot script). Main pipeline doesn't get variety enforcement.
24. Teacher wrapper: `teacher_atom` has no voice framing/attribution wrapper before entering the stack.
25. Unresolved template slots: `{selected_mechanism}`, `{selected_signal}` in REFLECTION atoms across 10 persona×topic combos. No resolver code exists.
26. Ch7/Ch8 REFLECTION enrichment gaps — `[CONTENT GAP: REFLECTION for anxiety ch7/8]` warnings.
27. `atoms/` pool (~6,040 atoms) largely idle — current path only hits it as deep fallback in `_find_story_content()`.
28. Onboarding doc drift: `docs/MANGA_PIPELINE_ONBOARDING.md` §3 references `--image-backend fixture-replay`; live CLI uses `--backend replay --replay-map`.

---

## 6. Environment / Credentials

All integration env from macOS Keychain (single source of truth: `scripts/ci/integration_env_registry.py`):

```bash
eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
```

| Use | Variables |
|-----|-----------|
| Pearl Star (inference box) | `PEARL_STAR_IP=pearlstar.tail7fd910.ts.net`, `QWEN_BASE_URL`, `COMFYUI_URL`, `COSYVOICE_URL` |
| Local ComfyUI FLUX (bank bulk) | `COMFYUI_URL` |
| RunComfy cloud | `RUNCOMFY_API_KEY`, `RUNCOMFY_DEPLOYMENT_ID` |
| Cloudflare Workers AI FLUX | `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_AI_API_TOKEN` (preferred), or `CLOUDFLARE_API_TOKEN` with Workers AI scopes |
| Qwen/DashScope | **Singapore only:** `https://modelstudio.console.alibabacloud.com/ap-southeast-1#/api-key`. Beijing URL is wrong. |

**LLM tier policy (enforced by `.github/workflows/llm-policy-enforcement.yml`):**
- Tier 1 — Claude Code (subscription, operator-present): refactors, features, prose generation for reviewed output.
- Tier 2 — Gemma / Qwen on Pearl Star via Ollama: scheduled unattended pipelines only.
- **Banned:** `ANTHROPIC_API_KEY`, `CLAUDE_API_KEY`, OpenAI cloud, Google AI, DashScope cloud, Together, Replicate, Perplexity, Cohere, Mistral paid. Audit: `python3 scripts/ci/audit_llm_callers.py`.

---

## 7. Image Banks — Current State

| Brand | Teacher | Locale | Path | PNGs | Status |
|-------|---------|--------|------|------|--------|
| stillness_press | ahjan | en_US | `image_bank/stillness_press/` | 840 | Complete (15 topics × 4 intents × 7 styles × 2 ratios). Index: `image_bank/index.json`. |
| cognitive_clarity | joshin | en_US | `image_bank/cognitive_clarity/` | 224 | Complete for 4 topics (boundaries, burnout, imposter_syndrome, overthinking × 56 each). Verify spec. |

**Filename convention:** `{intent}_{style_slug}_{sNN}.png` and `{intent}_{style_slug}_{sNN}_landscape.png`  
**Intents:** environment_atmosphere, symbolic_metaphor, hook_visual, character_emotion  
**Styles:** soft_ghibli_s00 ... geometric_abstract_s06

**LFS:** Large bank pushes need `PUSH_GUARD_MAX_FILES=500-900` above default 300.

---

## 8. Critical Rules (from CLAUDE.md)

- **Never merge a PR that deletes >50 files without explicit owner approval.** PR #245 deleted 20,006 files and cost hundreds of hours to recover. Check `gh pr diff <N> --stat | tail -1` before every merge.
- Always branch from `origin/main`. Never from `codex/*` or another local branch for agent work.
- Never push without `push_guard.py` + `preflight_push.sh` + `health_check.sh`.
- Never report "done" without a commit SHA or full file dump in CLOSEOUT_RECEIPT.
- Governance CI reviews every PR to main — blocks mass deletions, >500 files, warns on >3 subsystems touched.

---

## 9. For the Next Operator — Start Here

**If continuing Pearl Prime text quality work:**
1. Fix persona voice leak (open item #1) — `phoenix_v4/planning/registry_resolver.py` `_PERSONA_OVERLAY_TYPES` scoping.
2. Enforce ch1 contract at render (open item #2) — gate against `config/source_of_truth/chapter_purpose_contracts.yaml` arcs.standard_book.jobs[0].
3. Widen template stamp dedup (open item #3).
4. Deepen gen_z_student STORY pools (open item #5).
5. Then fire: `scripts/run_pipeline.py --render-book` loop over 100 sampled arcs → QA one.

**If continuing manga work:**
1. Execute Sprint 0 from `docs/MANGA_QUALITY_GAP_PLAN.md` (items #7–13). These are mechanical wire-ups, not design.
2. Build catalog → volume orchestrator (items #14–15).
3. Then Sprints A → B → C → D → E.

**If doing anything else first — read these in order:**
1. `ps.txt`
2. `docs/PEARL_GITHUB_ONBOARDING.md`
3. `docs/PEARL_PRIME_RELEASE_CONTRACT.md`
4. `docs/MANGA_QUALITY_GAP_PLAN.md`
5. `docs/MANGA_CATALOG_VOLUME_AND_ASSETS_HANDOFF_2026_04_17.md`
6. This handoff

---

**End of handoff.**
