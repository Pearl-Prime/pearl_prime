# Phoenix Omega — Consolidated Roadmap to 100%

**Date:** 2026-06-12 · **Companion to:** `SYSTEM_STATUS_AUDIT.md` · **Base:** origin/main @ `99ee0ba40`
**Framing:** "100%" = a content type produces **catalog-scale, ship-quality output, unattended, across the 37-brand canon + active CJK locales.** Today every type is at 0–3% of that.

---

## A. System critical path — what unblocks the most

The single highest-leverage observation: **the pipelines are ~80% built; the missing 20% is last-mile wiring + 3 shared upstream unblocks.** Spend here first, in this order:

1. **Fix `scene_anchor_density` (87% pre-render block).** This one gate rejects 174/200 books before render. It gates the **entire book catalog → which gates audiobooks (need book text) → which gates CJK books**. Single biggest upstream unblock. *No ws opened — needs root-cause investigation (Pearl_Dev).*
2. **Wire the books craft-gate stack** (`register_gate` → `ship_readiness_aggregator` → flip pipeline default to `spine`). Turns "renders" into "ships at trade-pub register." *3 PROPOSED ws's, ~3–4 dev-days total.*
3. **Provision ONE CosyVoice2 endpoint (`COSYVOICE_URL`).** Unblocks **CJK production across podcast + audiobook + video simultaneously** (shared dependency). *Pearl_Int infra, ~1 day.*
4. **Teacher-bank overlay backfill** (QUOTE + TEACHER_DOCTRINE for 15 teachers). Fixes the **F3 off-doctrine defect** → unblocks trade-pub-grade teacher-mode books for all brands. *Large editorial lane (Pearl_Editor + Pearl_Writer).*
5. **Last-mile wiring sweep** across podcast/video/audiobook/manga (one PR each — details below). Converts "1-brand MVP" into "37-brand cron."

> Note: **CJK is NOT on the critical path as an atom problem** — ja-JP/zh-TW atoms are ~85%. CJK is unblocked by items 3 (voice), 4 (teacher localization), and the manga LoRA fix — i.e. data/infra, not authoring.

---

## B. Per-subsystem roadmap

### B.1 BOOKS / Pearl Prime — from ~0% trade-pub-shippable → 100%

| Pri | Step | Open ws | Effort |
|---|---|---|---|
| **P0** | Root-cause + fix `scene_anchor_density` (87% catalog blocked pre-render) | *none — open one* | M (1–2 wk investigation) |
| **P0** | Wire `register_gate.py` (F1–F7,F11 already built) into `run_pipeline.py` | `ws_register_gate_implementation_20260518` | S (1–2 d) |
| **P0** | Build `ship_readiness_aggregator.py` (unified ship verdict) | `ws_ship_readiness_aggregator_20260518` | S (1–2 d) |
| **P0** | Flip `--pipeline-mode` default `registry`→`spine` | `ws_pipeline_mode_default_flip_to_spine_20260518` | XS (0.5 d) |
| **P1** | Backfill teacher-bank QUOTE + TEACHER_DOCTRINE for 15 teachers (F3 fix) | `ws_teacher_wrapper_semantics_impl_20260517` + editorial | L (editorial, per-teacher) |
| **P1** | Duration-label derivation spec + `format_registry.yaml` schema + CI guard (**char-aware for CJK**) | *none — open one* | M (1 spec + 1 dev day) |
| **P1** | Author anchor corpus → enables F8 + Layer-3 calibration | `ws_pearl_prime_acceptance_verdict_calibration_20260518` (step C) | S (operator picks 5–10 paras) |
| **P2** | Spec + build dwell-beat / integration-pacing craft gate (operator's #1 concern) | post-#1509 review (Architect spec queued) | M–L |
| **P2** | Ratify + build voice-zone C2 gate (Option B) | awaiting operator ratification | M |
| **P2** | Release gates → green on main | `ws_ci_recovery_release_gates` | M |
| **P3** | Localize persona-keyed atoms gap (zh-CN 27%→, ko-KR/zh-HK/zh-SG) + teacher banks for CJK | `ws_pearl_localization_atom_100pct_*` (worktree, unmerged) | L |
| **P3** | Close 29 empty en-US cells (midlife_women 15 + master_arcs; educators 7; nyc_executives 7) | `ws_atom_gap_fill_20260410`, `ws_midlife_women_arc_authoring_20260427` | M |

**Honest effort to "100%":** trade-pub-grade **en-US** = **weeks** (gate wiring ~1 wk + scene_anchor_density ~1–2 wk + teacher-bank editorial = the long pole). Full 37-brand + CJK catalog = **months**.

### B.2 PODCASTS — from 2.7% (1/37) → 100%

| Pri | Step | Open ws | Effort |
|---|---|---|---|
| **P0** | Loop `run_podcast_pipeline.py` across all 37 brands in `weekly_package_writer.yml` (today: hardcoded to stillness_press) | *none — open under Pearl_Prime* | S (~2 d) |
| **P0** | Provision + test CosyVoice2 endpoint (unblocks CJK) | Pearl_Int infra | S (~1 d) |
| **P0** | Prove R2 upload end-to-end (one live run, no `--skip-upload`) | Pearl_Int | XS (0.5 d) |
| **P1** | Fix cron schedule (10:00→9:00 UTC) + brand-loop | Pearl_GitHub | XS |
| **P1** | Validate per-brand/locale TTS voices at episode length (Edge-TTS $0 vs ElevenLabs) | Pearl_Prime | S |
| **P2** | Brand-admin podcast API + UI | Pearl_Int | M |

**Effort to 100%:** en-US 37-brand ≈ **1–2 weeks**; CJK adds the endpoint + per-locale voice validation.

### B.3 MANGA — from 1 episode (V4) → 37-brand V2 catalog

| Pri | Step | Open ws | Effort |
|---|---|---|---|
| **P0** | Publish ep_001 en-US (commit `queue_panel_renders.py`, register R2 secrets, bubble + webtoon compose + WEBTOON Canvas push) | `ws_post_pr478_manga_activation_20260418` | S (~1 d) |
| **P0** | ep_002 V5.1 dispatch (pose-library extension) | `ws_ep002_v51_pose_library_extension_20260527` | XS (0.5 d) |
| **P1** | V5 Qwen-Image-Layered production run (fixes V4 2/35 placement flaw) → then V2 Phase A | `MANGA-LAYERED-PIPELINE-V2-01` (Phase A, PROPOSED) | L (3–5 d dev + operator-go) |
| **P1** | Unblock CJK manga: align brand_style_loras + protagonist refs (zh_TW/zh_CN `blocked_lora`→`blocked_score`) | `ws_zh_manga_blocked_lora_followup_20260511` | S–M |
| **P1** | Extend catalog generator 12→37 brands + author 25 missing brand themes | `ws_catalog_generator_extend_to_37_brands_20260511` + `ws_catalog_generator_v1_1_25_brand_authoring_20260511` | M |
| **P2** | 37-brand schema atomic migration (delete 132 series + 716 book stale YAMLs — **>50-file deletion → operator approval required**) | `ws_manga_phase_2x_1_schema_atomic` | M (operator-gated) |
| **P2** | Pearl_Conductor v3 full-queue (37×4×2, unattended ~5–10 d wall, Pearl Star + RunComfy <$10) | `ws_pearl_conductor_v3_full_queue_activation_20260511` | L (compute-bound) |
| **P3** | LINE Manga Indies connector (ja-JP distribution) | *none — referenced as pending* | TBD |

**Effort to 100%:** ep_001 publish = **~1 day**; V2 layered production = **~4–5 weeks Pearl_Dev + ~$50 RunPod + ~3 hr operator review** (per cap); full 37-brand catalog = **months** (Conductor + schema migration).

### B.4 AUDIOBOOKS — from 0.3% (1/312) → 100%

| Pri | Step | Open ws | Effort |
|---|---|---|---|
| **P0** | Run the comparator-loop staging proof (the sole §12 blocker) | *none — open one* | S (~1 d) |
| **P0** | Acquire + stage locale-native CJK reference corpora (JVS ja / CSS10·THCHS zh / KSS ko) — replaces 40 Libri stand-ins (**JVS licensing gate**) | *none — open one* | M (1–2 wk, licensing) |
| **P1** | Flip en-US routing CosyVoice2-first (align to $0 MVP; resolve ElevenLabs-first inconsistency) | TTS migration spec (deferred lane) | XS (config PR) |
| **P1** | Author ja-JP + ko-KR golden regression sets (8 each) | *none — open one* | S (~2 d) |
| **P1** | Run comparator loop across 312 books × active locales (Pearl Star compute) | *none — open one* | L (1–2 wk compute) |
| **P2** | Package M4Bs for all 37 brands (extend #1346 pattern) | brand-admin-v2 extension | M |
| **P2** | Activate the 480 narrator clone slots (after native corpora land) + per-assignment ECAPA | post-corpora | M |

**Effort to 100%:** en-US catalog ≈ **weeks** (staging + comparator compute); CJK-quality adds **1–2 wk** corpora licensing/encode.

### B.5 VIDEO — from 0 canonical videos → productionized

| Pri | Step | Open ws | Effort |
|---|---|---|---|
| **P0** | Write `run_voice_synthesis.py` (EN Piper/ElevenLabs + CJK CosyVoice2) — unblocks `--voice` | *none — open one* | S (2–3 d) |
| **P0** | Fix upload CI interface (`--brand-suffix` vs `--channel-id/--batch`) | Pearl_GitHub | XS (1 hr patch) |
| **P1** | Add video-generate cron + flip `--skip-render` default | *none — open one* | S (~1 d) |
| **P1** | Wire platform credentials (stillness_press, cognitive_clarity) in CI secrets | Pearl_Int | XS |
| **P2** | Brand-Admin-V2 **video axis** (the missing 5th axis) | `ws_video_brand_admin_axis` (new) | M (~1 wk) |
| **P2** | Replace bespoke macOS `say` CJK path with canonical CosyVoice2 | extends voice-synth | S |
| **P3** | Teacher×Manga 30s pilot render (gated on operator Q1–Q4) | `proj_teacher_manga_30s_video_v1` | S (post-gate) |

**Effort to 100%:** productionize (real canonical MP4 + unattended publish) ≈ **2–3 weeks**; full catalog cadence (41–61 videos/book) = **months** and depends on manga renders existing.

---

## C. Sequencing (what to do in which wave)

- **Wave 1 (days, highest leverage):** flip pipeline-mode default; wire register_gate + ship_readiness; fix video upload-CI + write run_voice_synthesis.py; loop podcast cron across 37 brands; publish manga ep_001; provision CosyVoice2 endpoint; run audiobook staging proof. → turns 5 one-off MVPs into **37-brand-capable** pipelines for the cheap-to-fix types.
- **Wave 2 (weeks):** root-cause `scene_anchor_density`; teacher-bank overlay backfill; duration-derivation fix (char-aware); CJK voice corpora; ep_002 + V5 layered run; comparator-loop catalog run.
- **Wave 3 (months, operator-gated):** V2 manga layered production (Phase A–E); Pearl_Conductor v3 full-queue; 37-brand schema migration; dwell-beat + voice-zone craft gates; EU-locale expansion (currently 0%, mostly P5/deferred).

## D. Honest "where 100% is hard" callouts

- **Books at trade-pub register is the real frontier** — machine gates pass, human Layer-3 read fails. This needs the register-gate wiring **plus** teacher-bank editorial **plus** the dwell-beat/voice-zone gates that aren't built. Months, not weeks, for the full catalog.
- **Manga V2 is genuinely large** — 4–5 weeks dev + compute + operator review, and the V4→V5 architectural pivot means the multi-model ambition is still pre-production.
- **CJK production is cheap to start** (atoms are ~85% for ja-JP/zh-TW) **but quality CJK voice needs licensed native corpora** — a procurement lane, not a code lane.
- **Don't chase the 62,409-variant aspirational grid** — 72% is operator-deferred P5. Closing the **29 en-US cells + teacher-bank overlay + CJK voice** is the real "to-100%," not 26,618 authoring hours.
