# Manga V2 — Phase B–E Launch Plan (Operator One-Pager)

**Cap:** `MANGA-LAYERED-PIPELINE-V2-01` (ACTIVE / ratified) · **Author:** Pearl_Architect · **Date:** 2026-06-12

## Summary & The One Decision

Phase A of Manga V2 (constraint solver + deterministic prompt builder + facenet QA + per-character 12-axis YAMLs) is **built and lands this session** — it delivers ~70% catalog character distinctness from the prompt stack alone, with **no per-character LoRAs and $0 / fully local** cost. Phases **B–E are the only paid compute anywhere in manga**: ~$50 total RunPod, run sequentially over several days, to take face consistency from ~70% → ~90% and re-render a small reference set for a side-by-side quality call. This plan exists so spend stays **operator-authorized, never automatic**.

> **Code is already merged** — the Phase A/B *implementation* (constraint solver, deterministic prompt builder, facenet QA harness, PuLID nodes + engine-router) landed via **#925 / #926 / #928**. The ~$50 authorizes the **compute run** (RunPod GPU + LoRA training), **not** development. As of 2026-06-12 the per-character `character_design` data is also filled and 14/14 solver-distinct (see the Phase-A instances PR).

> **DECISION ASKED OF OPERATOR:** Authorize up to **$50 RunPod** to run Phases B→E (sequential), starting once Phase A is on `main` **and** the Pearl Star ComfyUI endpoint is back online. One go/no-go. (Final V2 promote/archive is a *separate* decision at the Phase-E gate.)

> **PRECONDITION (currently FAILING):** All B–E renders require the **Pearl Star ComfyUI endpoint `http://192.168.1.112:8188` ONLINE**. It is **DOWN right now** — bring it up before authorizing, or B cannot start.

## Phase Table

| Phase | Produces | Est. cost | Wall-time | Entry gate | Exit gate |
|---|---|---|---|---|---|
| **B — Face-lock** | PuLID-FLUX-FaceNet face-lock from **1 canonical reference sheet per named character** → ~90% face consistency | ~$20 RunPod GPU | ~1 day | Phase A merged to `main` **+** operator authorizes spend **+** Pearl Star online | Face cosine **≥ 0.55** on facenet QA harness across named cast |
| **C — Style + lettering LoRAs** | Register/genre LoRAs for **12–14 named recurring cast** (`config/manga/brand_lora_plans.yaml`) + lettering. **Reconcile against V5 lettering-v2 (PR #945) — do NOT duplicate lettering.** | ~$20 RunPod (LoRA training) | ~1–2 days | Phase B exit gate passed | LoRA outputs pass facenet QA: **cosine ≥ 0.55, characters distinct** |
| **D — Anatomy/hands** | Anatomy + hands correction pass over B/C outputs | ~$5 RunPod | ~0.5 day | Phase C exit gate passed | No gross anatomy/hand defects on QA sample |
| **E — V1→V2 re-render** | Re-render `stillness_press` ep_001 + ep_002 (+ one `cognitive_clarity` ep) **with side-by-side visual comparison** | ~$5 RunPod | ~0.5 day | Phase D exit gate passed | **OPERATOR VISUAL REVIEW → V2 promote-or-archive decision** |

## RunPod Budget — Line Items (~$50, NOT-TO-EXCEED $50)

| Item | Phase | Est. |
|---|---|---|
| Base model pull + PuLID-FLUX-FaceNet face-lock run | B | ~$20 |
| Register/genre LoRA training (12–14 named cast) + lettering reconcile | C | ~$20 |
| Anatomy/hands correction pass | D | ~$5 |
| V1→V2 re-render (3 episodes) for side-by-side | E | ~$5 |
| **TOTAL** | B–E | **~$50** |

> **NOT-TO-EXCEED: $50.** If projected spend crosses $50 at any phase boundary, **halt and re-confirm with operator** before continuing. No phase auto-advances past this ceiling.

## Trigger Chain (B starts only when ALL true)

```
[ Phase A merged to main ]  AND  [ Operator authorizes ≤$50 spend ]  AND  [ Pearl Star http://192.168.1.112:8188 ONLINE ]
        │
        └──> B (face-lock) ──pass cosine≥0.55──> C (LoRAs + lettering reconcile) ──pass QA──> D (anatomy/hands) ──pass──> E (re-render) ──> OPERATOR VISUAL REVIEW
```

Each arrow is a hard gate: a phase **does not start** until the prior phase's exit gate is green. No step fires while Pearl Star is offline.

## Phase-E Promote-or-Archive Criteria

V2 is **promoted** (replaces V5.1 as the manga render path) only if the side-by-side review shows V2 is **bestseller-grade and beats V5.1** on:

- **Face consistency** — same character reads as the same person across panels/episodes (target ~90%, up from V5.1).
- **Cast distinctness** — named cast members are visually distinguishable (facenet cosine ≥ 0.55, distinct).
- **Anatomy/hands** — no worse than V5.1; visible defects reduced.
- **Lettering** — at parity with V5 lettering-v2 (PR #945), not a regression.
- **No new artifacts** — V2 introduces no quality regression vs V5.1 on the reviewed episodes.

If V2 does **not** clearly beat V5.1 on the above → **archive V2 outputs, keep V5.1 as the production path.** The ~$50 buys the *decision*, not an automatic switch.

## One-Click for the Operator — Go / No-Go Checklist

Tick all before authorizing spend:

- [ ] **Phase A is merged to `main`** (prompt stack delivering ~70% distinctness, $0/local).
- [ ] **Pearl Star ComfyUI `http://192.168.1.112:8188` is ONLINE** (currently DOWN — fix first).
- [ ] **Canonical reference sheets exist** — 1 per named character for PuLID face-lock (Phase B input).
- [ ] **`config/manga/brand_lora_plans.yaml` cast list confirmed** — 12–14 named recurring characters for Phase C.
- [ ] **PR #945 (V5 lettering-v2) acknowledged** — Phase C reconciles, does not duplicate lettering.
- [ ] **Budget understood:** ~$50 total RunPod, **not-to-exceed $50**, sequential, multi-day.
- [ ] **Phase-E review is a separate sign-off** — promote-or-archive is decided after seeing side-by-sides, not now.

> **GO** = all boxes ticked → authorize ≤$50, B begins.
> **NO-GO** = any box unchecked (esp. Pearl Star DOWN or Phase A not on `main`) → do **not** authorize; resolve the gap first.
