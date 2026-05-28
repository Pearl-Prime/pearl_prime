# Phoenix Omega — Systems State (2026-05-27)

**Author:** Pearl_PM (autonomous multi-agent session closeout)
**main HEAD at authoring:** `823baf35d`
**Scope:** State after the brand-admin-v2 + HOOK-SCENE-FIRST-01 autonomous session, and the launch plan for worldwide catalog fan-out.

---

## 1. WHAT THIS SESSION ACCOMPLISHED

18 PRs merged to `main` (zero paid-API spend; all content fell back to free/local tiers).

### Brand-Admin-V2 (operator-visible weekly-work dashboard)
| Layer | PRs | Result |
|---|---|---|
| Phase 1 P0 (infra) | #1296 #1305 #1326 #1334 #1337 #1340 | Live 3-axis brand index + v2 dashboard + per-platform download (OPD-145 split-at-build) + planned-volumes backfill (37 brands × 3 axes) |
| Phase 2 P0 (real content MVP) | #1344 #1346 #1347 #1348 #1349 #1351 | stillness_press × 2026-W22 shipped end-to-end on **all 4 axes** + weekly cron |
| Cron output | #1350 | First auto-generated weekly package PR (merged) |

**Operator-visible result:** `brand-wizard-app/public/brand_admin_v2.html` → stillness_press → 2026-W22 → 6 platform download cards (KDP, WEBTOON, Spotify, Apple Podcasts, Audible, Google Play) all live.

### HOOK-SCENE-FIRST-01 (authoring quality gate)
| PRs | Result |
|---|---|
| #1327 #1328 | F11 register-gate detector + brief addendum + 212-atom tagging |
| #1336 #1342 #1341 | **178 atoms rewritten scene-first** (41 P0 + 100 P1 + 37 P2) — corpus pass complete |

### Other
| PRs | Result |
|---|---|
| #1331 | OPD-154: panel descriptions authoritative over writer-notes |
| #1333 | ep_002 V5.1 pose library extension (mira + dr_morimoto) |
| #1332 | CI baseline recovery V1 PARTIAL closeout |

### Hidden bugs caught + fixed (beyond original scope)
1. `build_admin_packets.py:141` — missing `mkdir(parents=True)` before per-platform zip (PR #1326 regression → #1334)
2. `build_platform_zips_for_brand` — only wrote manifest+README, dropped deliverable files (→ #1344)
3. `weekly_package_writer.yml` — heredoc broke YAML indentation; workflow silently failed 0s since PR #1251 (→ #1348)
4. `test_register_gate.py` — corpus calibration drift after P0 rewrites (→ #1336)

### Stale PRs closed as superseded
#1297, #1292, #1330

---

## 2. CURRENT SYSTEM STATE

### What is LIVE and validated
- **Brand-admin-v2 dashboard** — 37-brand picker, real planned volumes, per-platform downloads, weekly cron (Monday 9am UTC, opens auto-PR for operator review).
- **4-axis packaging pipeline** — book (EPUB) / manga (KDP PDF + WEBTOON PNG) / podcast (MP3) / audiobook (M4B) → per-platform ZIPs via `scripts/brand/build_admin_packets.py`. **Proven end-to-end for 1 brand × 1 week.**
- **HOOK authoring gate** — F11 detector live (WARN mode); 178-atom corpus is scene-first.

### Tier routing (per CLAUDE.md LLM policy)
- **English prose** (en_US books, manga scripts) → Pearl_Writer = Claude subagents (Tier 1, operator-present).
- **CJK6 prose** (ja_JP, zh_TW, zh_CN) → Qwen on Pearl Star (Tier 2, free, unattended).
- **English batch / scheduled** → Gemma on Pearl Star (Tier 2).
- **Images** → Pearl Star primary ($0); RunComfy fallback ($10/mo cap, ~$9.86 headroom).
- **Audio TTS** → ElevenLabs (⚠️ Keychain key 401 — rotate) OR free Edge TTS / local CosyVoice2.

### Catalog planning state (artifacts/catalog/)
- `PHOENIX_OMEGA_MASTER_CATALOG_PLAN.md` — 13 teachers × 13 locales × 29 topics; 980+ manga series; 13,104 audiobook titles; ~933K projected panel images.
- `high_confidence_catalog_v1.tsv` — **801 rows** (the $-maker tier: brand×topic×persona×format×locale).
- `full_catalog.csv` — **8,287 titles** across 309 brand/lane pairs.
- `catalog_gap_report.md` — drift: short 135 brand/lane instances; 166 rows missing series-plan + cover-art mappings; legacy teacher-brand names not migrated to 12×37.
- `config/manga/manga_brand_series_plan.yaml` — 35 of 37 brands have manga series plans.

### The honest scale reality
"All books + manga + podcast scripts for 37 brands × 4 locales" = **thousands of titles + ~933K manga panel images**. This is unambiguously a **Tier 2 unattended batch program** (Gemma/Qwen on Pearl Star), measured in days–weeks of compute — NOT a Claude-Code-in-chat task. Per CLAUDE.md, Claude Code is for review-before-ship prose; the bulk catalog generation runs on Pearl Star.

---

## 3. WORLDWIDE CATALOG FAN-OUT PROGRAM (3 layers, gated)

Per the "validation before scaling" principle: do NOT blind-fan-out to 37×4. Gate on plan-complete + brand-1-deep-validated first.

### LAYER 1 — PLAN (close the gaps) [achievable now, autonomous]
Make the catalog plan complete + drift-free for 37 brands × 4 launch locales (en_US, ja_JP, zh_TW, zh_CN).
- Close the 135 missing brand/lane instances.
- Map series-plans + cover-art-specs for the 166 unmapped rows.
- Migrate legacy teacher-brand names → 12×37 naming.
- Output: per-brand × per-locale series + book + podcast plans (SSOT).
- **Owner:** Pearl_PM + Pearl_Research. **Tier:** planning/data (cheap).
- **Gate:** plan validator green → unlocks Layer 2 + 3.

### LAYER 2 — VALIDATE (brand-1 deep) [heavy, dispatch now, runs long]
Fully build **stillness_press** in **en_US + ja_JP**: all books (text written), all manga series + titles, all podcast scripts, all image-bank images, assembled into pics + books.
- Proves the full per-brand pipeline at depth before scaling to 36 more.
- **Owner:** Pearl_Writer (en prose) + Qwen (ja prose) + Pearl_Author (manga) + Pearl Star (images).
- **Tier:** Tier 1 for en review-quality prose; Tier 2 for ja + images.
- **Gate:** brand-1 ships to operator review → validates the fan-out template.

### LAYER 3 — FAN OUT (36 brands × 4 locales) [Tier 2 batch, gated]
Batch-generate the remaining 36 brands × 4 locales per the Layer 1 plan, using the Layer 2 template.
- **Owner:** Pearl_Conductor v3 (unattended) on Pearl Star (Gemma en / Qwen CJK / Pearl Star images).
- **Tier:** Tier 2 unattended, scheduled. ~days–weeks wall-clock.
- **Gate:** ONLY after Layer 1 plan-complete AND Layer 2 brand-1 operator-approved. Do NOT spawn before both gates pass.

---

## 4. OPEN OPERATOR ACTION ITEMS

1. **ELEVENLABS_API_KEY** — Keychain key returns 401. Rotate: `security add-generic-password -s ELEVENLABS_API_KEY -a $USER -w <new_key>`. (Non-blocking; audio fell back to Edge TTS / CosyVoice2.)
2. **F11 WARN → HARD_FAIL** — corpus is now scene-first; HOOK-SCENE-FIRST-01 Open Question Q1 is unblocked. Authorize Pearl_Architect escalation ws.
3. **Layer 3 fan-out authorization** — needs explicit operator go after Layers 1+2 validate. This is the big Pearl Star compute spend (free but multi-day).
4. **RunComfy budget** — $9.86/$10 monthly headroom. If manga images for brand-1-deep exceed Pearl Star capacity and spill to RunComfy, may hit cap.

---

*Generated by Pearl_PM autonomous session closeout. Authority: docs/SESSION_UNITY_PROTOCOL.md + docs/PEARL_ARCHITECT_STATE.md (WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01).*
