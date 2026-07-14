# INDEX — Social Media Content Pipeline (self-help book topics)

## Program goal

Build an **in-repo, deterministic social-media content pipeline** that turns rendered
Pearl Prime / Waystream self-help books into native, platform-adapted posts across
**Instagram, Facebook, LinkedIn, Pinterest, TikTok, YouTube Shorts, Instagram Reels**
(Threads / Bluesky config-ready, X deferred per operator). The pipeline covers:

- **Static** content (carousels, LinkedIn PDFs, Pins, FB/text posts) — implements the
  existing `docs/specs/STATIC_SOCIAL_BOOK_CONTENT_ENGINE_2026-07-13.md` spec **in code**
  (today it is SPECCED-only; zero code implements it).
- **Imagery** — Pearl Star (FLUX, RAP queue-first) + book-cover sourcing + PIL text
  overlay (two-stage), and a **Canva-template** variant lane for deterministic
  high-variety renders ("change colors / swap elements → many unique posts").
- **Video** — Instagram Reels / YouTube Shorts / TikTok / Pinterest video via **Pearl
  Animator** (Remotion). Pearl Animator is Tier-1 operator-present, lives OUTSIDE this
  repo, and is NOT a cloud-scale batch renderer — the in-repo deliverable is the
  scene templates + a `social_video_manifest.json` contract; render pilots are
  operator-run.
- **Captions + media validation + scheduling** — the operator's expert brief
  (`PLATFORM_RULES` + platform spec tables) becomes `config/social/platform_rules.yaml`
  + `config/social/platform_specs.yaml`, a media validator, and a **Metricool**
  `/v2/scheduler/posts` payload builder.
- **QA gates** — the STATIC_SOCIAL QA gates + ethics/safety gate, wired into CI and
  mutation-tested.

**Scope guard (READ THIS):** this pack builds the **engine** and proves it on **one
book, small batch**. It does **NOT** generate "thousands of posts," and it does **NOT**
auto-publish anything. Scaling to a full brand / thousands is a **separate follow-up
dispatch**, gated on the operator's look-approval of the visual output (Q-SOCIAL-03).

## Live origin/main anchor used by router

- **Router-verified live `origin/main`:** `08a370aa711ec61dc2869050b7ee8e0418cb3bd3` (2026-07-14).
- **PROGRAM_STATE.md SSOT stamp:** `d8532d2d43874051b90201bda8b07eab5c1ce817` (2026-07-11 —
  behind live; lanes reconcile against live `origin/main`, never the stamp or the working tree).
- **Sibling branch in flight (collision hazard):** `codex/ghl-evergreen-waystream` is
  actively editing `docs/48_SOCIAL_GHL_BRAND_ADMIN_SPEC.md` and `docs/ghl/*`. **No lane in
  this pack may edit those files.** Reference them read-only.

## Source request summary

Operator (2026-07-14, Opus): make social posts on self-help book topics for IG / FB /
LinkedIn (+ video Reels / Shorts / TikTok via Pearl Animator, + Pinterest and other good
platforms; skip X for now); use Pearl Star for imagery, sourcing from book covers where
sufficient; use **Canva templates** for deterministic high-variety posts; follow the
attached expert brief (platform specs + `PLATFORM_RULES` caption rules) and the deep
research file `docs/research_social_media.txt`; **make it a pipeline in the repo.**

## Prompt count

**10 prompts** = `00_MASTER_DISPATCH_PROMPT.md` (Pearl_PM dispatcher) + **9 lane prompts**
(`01`–`09`). Plus this `INDEX.md` = **11 files total** in the pack.

## Provenance chain (Router v4 §18)

```
research  → docs/research_social_media.txt (deep research, ~2k+ lines)
            docs/book_deep_research.txt
            operator expert brief (platform specs + PLATFORM_RULES) — captured in L0 as config
documents → docs/specs/STATIC_SOCIAL_BOOK_CONTENT_ENGINE_2026-07-13.md (static authority; SPECCED)
            docs/48_SOCIAL_GHL_BRAND_ADMIN_SPEC.md (ops model; READ-ONLY — sibling branch)
            + NEW docs/specs/SOCIAL_MEDIA_PIPELINE_MASTER_SPEC.md (L0 authors — unifies static+image+video+canva+metricool)
code      → phoenix_v4/social/** + scripts/social/run_social_pipeline.py + config/social/** (this pack builds)
```

## Wave order

| Wave | Lanes | Gate to start |
| --- | --- | --- |
| **0 — Foundation** | L0 (architecture spec + schemas + package skeleton + registry/authority/workstream seeding + platform config stubs) | none — starts first, alone |
| **1 — Implementation** | L1, L2, L3, L4, L5 (parallel) | `social-arch-merged=<sha>` exists |
| **1.5 — Operator look gate** | (human) review L3/L4 pilot renders + L5 pilot video | L3+L4 pilots rendered; emits `social-look-approved=<sha/thread>` |
| **2 — Orchestration** | L6 (end-to-end pipeline runner + weekly-package wiring) | `social-extractor-merged` AND `social-captions-metricool-merged` |
| **3 — QA gates** | L7 (QA + ethics gates → CI, mutation-tested) | `social-orchestrator-merged` |
| **4 — Audit** | L8 (final production audit + acceptance-layer labelling + operator packet) | all lane signals present |

**Visual-lane scale is gated:** L3/L4 land their CODE + pilot renders in Wave 1, but
**scaling render volume** (and any move toward a full-book/brand batch) does not proceed
until `social-look-approved` exists (Wave 1.5). L8 must NOT label the visual system
PROVEN without that signal.

## Lanes — owner / substrate / dependency / output signal

| Lane | Owner | Substrate (primary files) | Depends on | Output signal / CLOSEOUT token |
| --- | --- | --- | --- | --- |
| **L0** arch + scaffold | Pearl_Architect | `docs/specs/SOCIAL_MEDIA_PIPELINE_MASTER_SPEC.md`, `schemas/social/*.json`, `phoenix_v4/social/__init__.py`, `config/social/` (stubs), coordination TSVs | — | `social-arch-merged=<sha>` · `CLOSEOUT_RECEIPT::social-L0-arch` |
| **L1** book→social extractor + static copy | Pearl_Marketing | `phoenix_v4/social/extractor.py`, `phoenix_v4/social/static_generator.py`, `config/social/static_content_config.yaml` | L0 | `social-extractor-merged=<sha>` · `CLOSEOUT_RECEIPT::social-L1-extractor` |
| **L2** captions + media validator + Metricool payload | Pearl_Int | `phoenix_v4/social/caption_adapter.py`, `phoenix_v4/social/media_validator.py`, `phoenix_v4/social/metricool_payload.py`, `config/social/platform_specs.yaml`, `config/social/platform_rules.yaml` | L0 | `social-captions-metricool-merged=<sha>` · `CLOSEOUT_RECEIPT::social-L2-captions` |
| **L3** image lane (Pearl Star + covers + PIL) | Pearl_Int | `phoenix_v4/social/image_render.py`, `config/social/image_render_config.yaml` (reuses `artifacts/waystream/cover_pilot/compose_cover.py`, `phoenix_v4/manga/covers/`) | L0 | `social-image-lane-merged=<sha>` · `CLOSEOUT_RECEIPT::social-L3-image` |
| **L4** Canva template lane | Pearl_Int | `phoenix_v4/social/canva_render.py`, `config/social/canva_templates.yaml` | L0 | `social-canva-lane-merged=<sha>` **or** `social-canva-lane-blocked=<reason>` · `CLOSEOUT_RECEIPT::social-L4-canva` |
| **L5** video lane (Pearl Animator wiring) | Pearl_Video | `phoenix_v4/social/video_manifest.py`, `docs/specs/SOCIAL_VIDEO_ANIMATOR_WIRING_SPEC.md`, scene templates in `~/<brand>_video` (local) | L0 | `social-video-lane-merged=<sha>` · `CLOSEOUT_RECEIPT::social-L5-video` |
| **L6** pipeline orchestrator + weekly wiring | Pearl_Dev | `scripts/social/run_social_pipeline.py` (wires into `scripts/build_weekly_brand_package.py`) | L1, L2 | `social-orchestrator-merged=<sha>` · `CLOSEOUT_RECEIPT::social-L6-orchestrator` |
| **L7** QA + ethics gates → CI | Pearl_Research | `phoenix_v4/social/gates/`, `scripts/ci/check_social_*.py`, `tests/test_social_*.py` | L6 | `social-qa-gates-merged=<sha>` · `CLOSEOUT_RECEIPT::social-L7-gates` |
| **L8** final production audit | Pearl_PM | `artifacts/qa/social_pipeline_audit_2026-07-14.md`, PROGRAM_STATE update | all | `social-pipeline-audit-complete=<sha>` · `CLOSEOUT_RECEIPT::social-L8-audit` |

## Canonical data contracts (defined by L0; every lane builds against these seams)

- `schemas/social/static_social_plan.schema.json` — from STATIC_SOCIAL spec "Output Manifest".
- `schemas/social/social_media_asset.schema.json` — one asset (platform, format, source_trace, hook, slides/caption, cta, visual_direction, media_refs, safety_verdict).
- `schemas/social/social_media_manifest.schema.json` — per-book package (list of assets + provenance).
- `schemas/social/metricool_payload.schema.json` — `/v2/scheduler/posts` payload (providers, publicationDate, text, firstCommentText, media, mediaAltText, per-platform *Data blocks).

**The schema files are the seam.** L1 emits `static_social_plan.json`/manifest; L2/L3/L4/L5
consume the manifest and produce captions/payloads/media; they build against the L0 schema +
fixtures, **not** against each other's code — so Wave-1 lanes are truly parallel.

## Hot-file conflict notes (Router v4 §25)

- **Coordination TSVs** (`CANONICAL_ARTIFACTS_REGISTRY.tsv`, `SUBSYSTEM_AUTHORITY_MAP.tsv`,
  `ACTIVE_WORKSTREAMS.tsv`): **only L0 seeds them**, and **only the Pearl_PM dispatcher
  updates workstream statuses thereafter** (serial writer — these are hot governance files).
  Wave-1 lanes do NOT edit these TSVs.
- **`phoenix_v4/social/__init__.py`**: created by L0 in Wave 0 so Wave-1 lanes never race on it.
- **`config/social/` dir**: shared dir, **disjoint filenames** per lane (L1 `static_content_config.yaml`;
  L2 `platform_specs.yaml`+`platform_rules.yaml`; L3 `image_render_config.yaml`; L4 `canva_templates.yaml`).
  No two lanes write the same file. L0 lands the dir with a README stating file ownership.
- **`config/funnel/social_cta_config.yaml`** (EXISTS): consumed read-only by L1/L2; **not recreated**.
- **`docs/48_SOCIAL_GHL_BRAND_ADMIN_SPEC.md` + `docs/ghl/*`**: read-only for ALL lanes
  (active sibling branch `codex/ghl-evergreen-waystream`).
- **`docs/specs/STATIC_SOCIAL_BOOK_CONTENT_ENGINE_2026-07-13.md`**: L0 may add a single
  cross-ref line pointing to the new master spec; L1 implements it but does not rewrite it.

## Required output tags (every lane closeout must emit)

- Its `social-*-merged=<full-sha>` (or `-blocked=<reason>`) signal on a durable surface.
- `CLOSEOUT_RECEIPT::social-L<N>-<slug>` grep token.
- Acceptance-layer label (Router v4 §16): `SPECCED` / `CODE-WIRED` / `EXECUTED-REAL` /
  `PROVEN-AT-BAR`. **`register_gate`/CI PASS is at most CODE-WIRED, never "done."**
- Handoff: `artifacts/coordination/handoffs/social-L<N>-<slug>_2026-07-14.md`.
- Heartbeat if the lane runs >15 min: `artifacts/coordination/heartbeats/social-L<N>_2026-07-14.md`.

## Open operator questions (recommend defaults; dispatcher batches; do NOT decide unilaterally)

- **Q-SOCIAL-01 — Scheduler:** Metricool vs GHL-native. **Default:** build the Metricool
  `/v2/scheduler/posts` payload (per expert brief) as primary; document GHL-native as an
  interchangeable alternative behind the same manifest. (L2)
- **Q-SOCIAL-02 — Static image renderer of record:** Pearl Star/PIL vs Canva. **Default:**
  dual-track — Pearl Star + book-cover-sourced + PIL as the **CI-safe, credential-free
  default** (L3); Canva as the **high-variety enhancement** lane that degrades to BLOCKED if
  the Canva Connect credential/MCP is absent in the run environment (L4). Neither is deleted.
- **Q-SOCIAL-03 — First-proof scale:** 1 book vs 1 brand vs "thousands." **Default:** ONE
  book end-to-end (recommend the PROVEN-AT-BAR flagship `gen_z_professionals × anxiety`),
  then operator look-approval, then a **separate** 1-brand scale dispatch. **This pack does
  not attempt thousands.**
- **Q-SOCIAL-04 — First-proof platforms:** **Default:** static = IG carousel + LinkedIn PDF +
  Pinterest Pin + FB post; video = IG Reels + YT Shorts + TikTok (1 pilot each). Threads/
  Bluesky config-ready, not rendered; X deferred per operator.
- **Q-SOCIAL-05 — Auto-publish:** **Default OFF for the entire pack.** The pipeline emits
  scheduled-draft payloads only; nothing is posted. Publishing is a later operator decision.

## Final audit / release gate

L8 (Pearl_PM) runs the production audit on the one-book proof: verifies the chain
extractor→captions→media→manifest→Metricool-payload produces a **schedulable, safe,
on-spec** package; confirms QA gates are RED-on-violation (mutation-tested); confirms no
lane claimed "done" on gate-PASS alone; confirms `social-look-approved` exists before
labelling the visual system beyond CODE-WIRED; updates PROGRAM_STATE; `open`s the sample
assets for the operator's Layer-4 look-read.

## Cleanup + handoff requirements (all lanes)

Every lane ends **MERGED or BLOCKED** (no third state), same turn, with:
- cleanup ledger — worktrees removed/HOLD-declared, local+remote branches deleted after
  merge, scratch files removed or in the PR, background jobs (Pearl Star queue ids)
  stopped or declared;
- a handoff `.md` under `artifacts/coordination/handoffs/`;
- a heartbeat under `artifacts/coordination/heartbeats/` if it ran >15 min.

## Status

| Lane | Status |
| --- | --- |
| L0–L8 | **AUTHORED — not yet dispatched.** Pack is durable local docs (uncommitted). |
