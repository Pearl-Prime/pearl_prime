# LANE 2 — Spec + Plan: Full Manga Image Bank, 1 Series/Brand × 5 Locales (Free Infra Only)

## EXECUTE

Deliverable is a **spec + phased plan document**, landed as a docs-only PR.
You are not rendering the bank in this lane — Lane 1's smoke test is the only
GPU dispatch this pack authorizes. Do not stop at "here are some options" —
produce one committed, decision-complete plan the operator can approve as-is
or redline. Require Lane 1's report before starting; if it isn't available,
run Lane 1 yourself first.

## Read first (governing specs — cite these, do not invent a parallel plan)

1. `docs/specs/MANGA_100PCT_PRODUCTION_ROADMAP_2026-07-03.md` §5 (Milestone
   M5) — this task IS M5, extended in locale scope. Read the R6 law it states:
   only build a bank for a series that already has a gate-passing story.
2. `docs/specs/MANGA_V5_LAYERED_ARCHITECTURE.md` — current render approach
   (one Qwen-Image-Layered dispatch/panel → N+1 RGBA outputs). Read its
   v1.0.1 amendment (the one real run: `stillness_en_01 ep_001`, 35/35, 10.76GB
   peak VRAM, 3h39m).
3. `docs/specs/MANGA_LAYER_RENDER_CONTRACT_SPEC.md` — L0–L4 layer semantics,
   z-order, provenance rules that `assemble_from_bank.py` enforces.
4. `scripts/manga/assemble_from_bank.py` + `schemas/manga/assembly_manifest.schema.json`
   — the canonical assembler. Your plan must produce banks in the shape this
   already-working tool consumes; do not propose a new assembler.
5. `docs/ROBUST_AGENT_PROTOCOL.md` — GPU dispatch discipline (RAP,
   queue-first, one-image-per-job) applies to every render step your plan
   proposes.
6. `config/manga/brand_lora_plans.yaml` and
   `docs/PEARL_ARCHITECT_STATE.md` (grep `MANGA-LAYERED-PIPELINE-V2-01`) —
   current LoRA/PuLID plan and phase status (Phase B base-models/PuLID and
   Phase C register/genre LoRAs are both `status: proposed`, not executed).
7. `artifacts/qa/MANGA_VISION_CONFORMANCE_AUDIT_2026-07-03.md` — the honest
   baseline. Confirm it's still accurate before citing it (it's 3 weeks old
   relative to other docs you'll read).
8. Brand scope: grep `docs/PEARL_ARCHITECT_STATE.md` for
   "MANGA-CATALOG-RECONCILIATION" / the 37-canonical-brand freeze (Path X).
   Confirm the current brand count and list — do not assume 37 without
   re-checking, brand freezes get amended.
9. Locale scope: `config/localization/locale_registry.yaml` (confirms
   en_US/ja_JP/zh_TW/zh_CN/fr_FR are all real, existing locale codes) and
   `docs/agent_prompt_packs/20260723_manga_48ep_3catalog_series/ASSIGNMENT_MATRIX.tsv`
   (the freshest brand×genre×locale scope def — currently en_US/ja_JP/zh_TW
   only; fr_FR and zh_CN are outside its scope and need their own resolution).

## Known contradiction to resolve (do not silently pick one side)

`docs/PROGRAM_STATE.md` (2026-07-22) states the fr_FR manga allocation-chain
gap is "closed" with "fr_FR real plans" existing. `artifacts/qa/MANGA_VISION_CONFORMANCE_AUDIT_2026-07-03.md`
(3 weeks earlier) states fr_FR's manga track is entirely absent from the
registry. These cannot both be current. Before your plan assumes fr_FR has
zero or nonzero manga series plans, run a live check:

```
find docs/research -iname "*fr_fr*manga*" -o -iname "*manga*fr_fr*" 2>/dev/null
grep -ril "fr_FR" artifacts/manga/series_plans/ 2>/dev/null | head -20
```

Report which claim is true as of today, with the file paths you checked, and
build the plan on the verified state — not on either doc's say-so.

## What the spec + plan must cover

### A. Scope definition (the plan's first job — this is genuinely undefined today)

- Exact brand list for "1 series per brand to start" (confirmed count from
  the freeze doc, not assumed 37).
- Per brand: does a gate-passing (register_gate PASS, `check_manga_story_authored.py`
  PASS) authored series already exist for each of the 5 target locales? Build
  a real table (brand × locale → {gate-passing story exists | listing-only
  stub | absent}) by querying `artifacts/manga/chapter_scripts/` and
  `artifacts/manga/series_plans/`, not by assuming. R6 law forbids building a
  bank ahead of an authored, gate-passing story — flag every brand×locale cell
  that fails this as **blocked on authoring**, not as an image-bank task.
- zh_CN specifically: confirm current count of `blocked_lora` rows
  (`ws_zh_manga_blocked_lora_followup_20260511` in
  `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`) and whether those brands
  should be excluded from the "to start" wave or held for a LoRA-readiness
  follow-up.

### B. Technical approach (grounded in what's already real, not invented)

- Reconcile V4 (L0–L4 contract) vs V5 (per-panel Qwen-Image decompose) — state
  which one your plan actually dispatches through and why, citing the one
  real run's numbers (10.76GB VRAM, 3h39m/episode) as your budget baseline.
- State explicitly: **panel art is locale-agnostic; only bubble/lettering is
  locale-specific** (post-assembly pass via `bubble_render_v2`,
  `config/manga/genre_bubble_styles.yaml`). This means the 5-locale
  requirement multiplies the (cheap, CPU-side) lettering pass, not the (GPU,
  expensive) render pass — spell out the resulting real GPU-hour estimate for
  "1 series/brand × 1 render + 5 locales of lettering" vs the naive "×5
  everything" misreading, so the operator sees the actual cost difference.
- Model roster, free-only, cite each: `flux1-schnell-fp8` (base,
  Apache-2.0), Qwen-Image (V5 layered decompose), PuLID (face-lock, Phase B —
  state its actual install status from Lane 1's report), Animagine XL (where
  genre calls for it per `MANGA_DRAWING_TRADITION_WAVE2_REIMPLEMENTATION_SPEC_20260721.md`
  — note that spec's own history: a prior session falsely claimed it complete
  when nothing existed on disk; re-verify current state, don't inherit that
  claim), ToonOut/BiRefNet (cutout, MIT license, CPU-fallback on this GPU).
  LoRA training: state plainly that zero brand LoRAs are trained anywhere
  today (`brand_lora_plans.yaml` is 100% `status: planned`) and that PuLID-only
  face-lock is the realistic near-term path unless the operator wants to
  fund/schedule LoRA training as a separate prerequisite workstream.
- RAP compliance: every render step is one queue job, one image; no bundled
  batch dispatch; polling with stall thresholds per
  `docs/ROBUST_AGENT_PROTOCOL.md`.

### C. Ramp (smoke → pilot → scale — do not propose jumping to scale)

- **Smoke**: Lane 1's single test image (already done by the time this lane
  runs) — cite its result, don't re-propose it.
- **Pilot**: one series (`stillness_press` — it already has the only
  non-INTERIM partial bank/render on record, per the 2026-07-03 audit and
  this session's own ep_011/ep_012 authoring) rendered for all 5 target
  locales' lettering pass on top of one real render. This proves the
  render-once/letter-five-times model end-to-end before committing to any
  other brand.
- **Scale**: the remaining brand×locale cells that passed the R6
  authored-story gate in §A, sequenced by whichever locale currently has the
  most real authored coverage first (do not sequence by locale alphabetically
  or by operator-request order — sequence by what's actually buildable
  today, and say so).
- For each phase, state a real GPU-hour estimate derived from the pilot's
  measured wall-clock (not the 3-week-old 40-GPU-h/series planning number
  alone) once the pilot completes.

### D. What this plan explicitly does NOT authorize

- No LoRA training (separate decision/workstream — flag as a prerequisite
  question for the operator, don't fold it in silently).
- No story authoring for brand×locale cells that fail the R6 gate (route
  those to the existing manga-authoring dispatch lane instead of implying
  the image-bank plan covers them).
- No RunComfy or any paid image path, regardless of GPU-hour pressure.
- No claim of PROVEN-AT-BAR quality — that requires a blind-judge pass that
  doesn't exist yet (R7 = 5% per the audit); the plan should note this as a
  known future gate, not solve it here.

## Landing

- Write the plan to `docs/specs/MANGA_IMAGE_BANK_5LOCALE_PLAN_<YYYYMMDD>.md`
  (use today's actual date).
- Append a new row to `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` for
  this workstream (confirmed no existing row covers it).
- Branch fresh off a re-fetched `origin/main` (per master prompt's dirty-tree
  guidance — build via git plumbing if the working tree carries unrelated
  changes from other sessions, which is common in this repo).
- Run the mandatory preflight, commit, push, open a PR (do not merge).
  Report the exact PR number/URL and full commit SHA in your
  CLOSEOUT_RECEIPT, plus the signal token `<signal>=<full-SHA>`.
