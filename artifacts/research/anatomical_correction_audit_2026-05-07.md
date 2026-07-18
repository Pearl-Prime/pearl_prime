# Anatomical correction — community LoRA + tooling audit (Pearl\_Research)

**Session type:** Research-only — closes **P0-3** from operator audit dated 2026-05-07 (hand-correction / anatomy stack was missing from prior 2026-04-29 fork-and-build audits).

**Audience:** Pearl\_Engineering (Phase D implementation workstream).

**Companion artifact:** Tiered roster in `config/manga/anatomical_correction_loras.yaml` (machine-readable mirror of findings below).

---

## 1. Executive summary

Commercial-safe manga generation still depends on three parallel layers: **(A)** prompt + base-model priors, **(B)** **negative embeddings / negative-placement LoRAs** that penalize anatomical failures, **(C)** **optional inpaint/detection post** (ADetailer-style) and occasional **commercial-vetted restoration** stacks.

The community surface is fragmented: aliases like **“BadHands v3”** and **“flux-hand-fix”** do **not** map to single stable Civitai slugs anymore; operators should treat those names as **families** and pin **exact `modelVersionId` + file hashes** before production.

Until each asset’s Civitai **commercial-permissions panel** is clicked through, Phoenix policy treats all community-derived weights as **🟡** — even when upstream codebases are OSS-clean.

---

## 2. License tier legend (Phoenix “commercial-clean”)

Aligned with `artifacts/research/community_lora_roster_2026-04-29.yaml`:

| Marker | Meaning |
| --- | --- |
| 🟢 | Asset path is **commercial-clean without extra contracts**: OSS license permits commercial use *and* (for LoRA/embeddings) Civitai / Hugging Face flags + **base-model** redistribution terms are verified as permitting shipped product revenue. |
| 🟡 | **Conditional / ambiguous**: requires per-asset Civitai flag verification, base-model caveat (e.g. Illustrious, Pony), **FLUX-derived** community adapters pending BFL + host terms, **AGPL** toolchain compliance review, etc. Do **not** recommend as canonical until cleared. |
| 🔴 | **Blocked for Phoenix default commercial**: NC-only license, **third-party celebrity/IP** training surfaced on page, prohibited commercial face-swap checkpoints without enterprise license, **Pony** base output restrictions, etc. |

**Hard stop:** If license verification stays ambiguous after page review, tier stays **🟡** — **do not** promote to canonical integration.

---

## 3. Canonical hand-fix assets (embedding + LyCORIS/LoRA)

### 3.1 “BadHands v3” / Bad Hands family (negative prompt)

**Finding:** Public search and Civitai listings today emphasize **Bad-Hands-5** (`/models/116230`) and related embeddings; a distinct page titled **“BadHands v3”** was **not** reliably resolved in this research pass. Many tutorials file-name older embeddings `badhandv3` — treat as **deprecated alias**.

**Operational mapping**

- **Bad-Hands-5** (embedding) — Civitai `116230` — **🟡** (Civitai commercial flags + training data unknowns).
- **bad\_pictures v3.0** (embedding, SD1.5-biased) — Civitai `23178` — **🟡** (general quality + “bad hands” suppression; confirm XL compatibility if misused cross-arch).

**Integration note:** Embeddings load in the **negative prompt** with their **trigger token**; verify CLIP skip + base model family (SD1.5 vs SDXL) before stacking.

### 3.2 `negative_hand` / `negative_hand-neg`

- **negative\_hand Negative Embedding** — Civitai `56519` — triggers include **`negative_hand`** / community references to **`negative_hand-neg`** — **🟡**.
- **Negative Hands** (SDXL embedding) — Civitai `583583` — trigger **`NEGATIVE_HANDS`**, author notes clip skip `2` — **🟡**.

### 3.3 “EasyNegative\_Hand”

**Finding:** No stable Civitai slug uniquely titled **EasyNegative\_Hand** surfaced in targeted search.

**Operational mapping**

- Likely confusion between **EasyNegative** (`7808`, ubiquitous SD1.5 negative embed, **🟡**) stacked with **`negative_hand`** or **Negative Hands XL**.
- **Recommendation:** Do **not** treat “EasyNegative\_Hand” as a verified third artifact until a maintainer supplies a pinned URL + version id.

### 3.4 `hand_v1.0` (explicit version handle)

Map the operator token to a **concrete** SDXL LoRA with a “v1.0” version label, e.g. **Better hands – SDXL v1.0** — Civitai `1584999` — **🟡** (page flags + data).

*(Other hand finetunes exist — “Hand Fine Tuning SDXL”, “ClearHandsXL”, “Hands SDXL beta” — all **🟡** pending the same diligence.)*

### 3.5 BadHands-style **negative LyCORIS** (SDXL)

- **BadHands SDXL (negative LyCORIS/LoKr)** — Civitai `128969` — author pattern: invoke from **negative prompt** with **positive weight** — **🟡** (nonstandard UI; easy to mis-wire in ComfyUI).

### 3.6 Detail Tweaker XL (general detail; helps hands incidentally)

- **Detail Tweaker XL** — Civitai `122359` (author `w4r10ck`) — continuous strength roughly **−3…+3** — **🟡** (commercial FAQ exists on mirrors; Phoenix must read live Civitai permissions).

### 3.7 “flux-hand-fix” (FLUX)

**Finding:** No widely indexed Civitai model uses the **exact slug** `flux-hand-fix`. The community uses nearby names:

| Candidate | Role | Tier |
| --- | --- | --- |
| **Hand Detail FLUX & XL** v3.0-FLUX — Civitai `260852` | Positive “detailed hands” bias — **primary FLUX LoRA candidate** | 🟡 |
| **\[FLUX\] Detailed Hands** — Civitai `891074` | Alternate FLUX hand LoRA | 🟡 |
| **Flux Fix Hands (fp8 4steps)** — Civitai `626333` | **Workflow** (detector + quick repair) | 🟡 |
| **Hand & Feets Fix** — Civitai `2064475` | Workflow bundle | 🟡 |

**FLUX.1 dev / schnell base license:** Black Forest Labs terms apply to outputs and redistribution. Any **Phase D** integration must include **BFL + host** review in addition to Civitai creator flags.

---

## 4. Civitai hand-correction — by base model family

| Family | Representative assets | Phoenix stance |
| --- | --- | --- |
| **SDXL** (incl. Animagine 4.0) | Negative Hands XL, BadHands SDXL LyCORIS, Better hands / ClearHandsXL class | Primary engineering target — **🟡** until each file is flag-verified. |
| **Pony Diffusion XL** | Many “anime hand” LoRAs are Pony-tagged (e.g. eye/hand bundles) | **🔴** for default commercial on Pony base (matches prior Phoenix roster: Pony commercial restrictions). |
| **FLUX** | Hand Detail FLUX & XL, Detailed Hands, repair workflows | **🟡** — dual gate: Civitai + BFL. |
| **Qwen-Image** | Sparse dedicated “hand-only” LoRAs in English search | Prefer **base model + prompt + light regional inpaint**; only add community LoRAs with **🟢/🟡** verification (see YAML). |

---

## 5. Face-detail and eye-detail LoRAs (SDXL-ish)

These **shift identity and lighting**; use **lower weight** and **later** in the LoRA stack than broad style LoRAs.

| Asset (illustrative) | Civitai (path id) | Notes | Tier |
| --- | --- | --- | --- |
| **SDXL/PDXL Tuning Face Detailer** | `234556` | Expression + face micro-detail; anime weight guidance on page | 🟡 |
| **Face light up / 前面ライトアップ** | `962998` | Frontal face lighting bias | 🟡 |
| **Perfect Eyes XL** | `118427` | `perfecteyes` + palette tags; strong DL count | 🟡 |
| **Ultimate Anime Style Enhancer SDXL** | `1616854` | Includes `EyesHD` class tags | 🟡 |
| **Enchanting Eyes (Detailed Eyes)** | `974076` | **Illustrious** base — **Illustrious commercial terms** gate | 🟡 |
| **beautiful detailed eyes** | `5693` | SD1.5-leaning legacy | 🟡 |

**Pony-tagged eye LoRAs** (e.g. `290239`) — assume **🔴** for Phoenix commercial on Pony; cross-test on SDXL only if license + arch transfer is explicitly validated.

---

## 6. Non-LoRA post-processing (face / hands)

| Tool | License / commercial note | Tier | Guidance |
| --- | --- | --- | --- |
| **ADetailer** ([`Bing-su/adetailer`](https://github.com/Bing-su/adetailer)) | **AGPL-3.0** | 🟡 | Fine for internal pipelines if Phoenix complies with AGPL (network/SaaS obligations). Legal should sign off before customer-facing managed inference. |
| **GFPGAN** ([`TencentARC/GFPGAN`](https://github.com/TencentARC/GFPGAN)) | **Apache-2.0** | 🟢 | Code license clean; **weights** still subject to model-card terms — default **🟢** for code path, **verify weight bundle**. |
| **CodeFormer** ([`sczhou/CodeFormer`](https://github.com/sczhou/CodeFormer)) | **S-Lab License 1.0** — **NC** | 🔴 | Do **not** ship in commercial restoration stack without written permission. |
| **inswapper-512** (InsightFace family) | README / policy: **contact InsightFace for commercial** on inswapper series | 🟡 / 🔴 | Treat as **🔴 default** for “commercial-clean without contract.” If enterprise license obtained, re-tier to **🟢** with contract id in audit trail. |

**Pearl operator ask (“inswapper-512 commercial-clean check”):** **Not** clean by default — **enterprise license track** or **exclude** from automated face-replace nodes.

---

## 7. Per-base-model integration guidance (Phase D prep)

### 7.1 Animagine XL 4.0 (SDXL)

**Goal:** Fix hands **without** washing manga line register.

Recommended **stack pattern** (strengths are starting points — Phase D tunes on held-out manga panels):

1. **Genre / register LoRAs** (existing Phoenix stack) — e.g. lineart/halftone helpers from prior roster — **0.55–0.85**.
2. **Detail Tweaker XL** — small positive increment (**~0.25–0.7**) **only if** print legibility needs micro-contrast — watch for brittle finger geometry.
3. **Hand correction**

   - *Preferred low-risk*: **Negative Hands XL** embedding in **negative** prompt (confirm clip skip parity with Animagine defaults).
   - *Stronger anatomical penalty*: **BadHands SDXL LyCORIS** authored for **negative stack** placement — obey author weight polarity.
   - *Positive finetune last resort*: **Better hands SDXL-class** LoRA at **≤0.6** — validate against multi-panel continuity.

**Layer order (ComfyUI / ai-toolkit mental model):** **Style → anatomy/detail correction → tiny face/eye helpers** — never place a heavy face LoRA ahead of anatomy correction or hands will deform to satisfy face loss.

### 7.2 Qwen-Image

**Hypothesis validated by JP/CN discourse:** Qwen-Image already carries **strong structural priors** on hands vs SDXL era.

**Recommendation:** Phase D starts with **prompting + regional img2img/inpaint** using the base checkpoint; **avoid** stacking unvetted SDXL embeddings. Add Qwen-native or explicitly Qwen-trained detail LoRAs **only** after **🟢/🟡** gating per file.

### 7.3 FLUX.1 schnell

**Canonical substitute** for operator term **“flux-hand-fix”:**

- **Primary:** **Hand Detail FLUX & XL** (`260852`, FLUX branch) — author trigger **`detailed hands`** (per page metadata in community mirror).
- **Secondary:** **\[FLUX\] Detailed Hands** (`891074`).
- **Workflow fallback:** **Flux Fix Hands** (`626333`) when batch QC shows systematic hand box failures.

**Caveat:** Schnell vs dev **step/noise** schedules change effective LoRA strength — Phase D must regression-test **Panel A/B** on schnell-only paths.

---

## 8. Phase D implementation plan (separate workstream)

1. **Inventory freeze** — Import `config/manga/anatomical_correction_loras.yaml` into the same release-control process as `community_lora_roster`.
2. **Perm-gate script** — Extend `scripts/ci` or internal checklist so every linked Civitai id records the **six commercial toggles** + screenshot hash (operator policy).
3. **Comfy regression harness** — Fixed seeds, three poses (open palm, pointing, holding prop), two aspect ratios, B&W + color manga nodes.
4. **Tier promotion** — Only **🟢** (or **🟡** cleared to **🟢** with written note) enter default **Pearl Star** unattended pipelines; **🟡** stays operator-gated.
5. **Legal pass** — AGPL (ADetailer) network use; BFL FLUX bundle; InsightFace exclusions.
6. **Documentation** — Update `docs/COMFYUI_FLUX_MANGA_PROMPTING_RESEARCH_*.md` cross-links once weights are pinned.

---

## 9. Top-3 hand-fix candidates (if scope must shrink)

When forced to defer breadth (per **hard stop**):

1. **Hand Detail FLUX & XL** (`260852`) — FLUX lane.
2. **Negative Hands XL** (`583583`) — SDXL negative embed lane.
3. **BadHands SDXL LyCORIS** (`128969`) — SDXL negative-stack LyCORIS lane.

All three remain **🟡** until page-level commercial verification completes.

---

## 10. Sources & method

- Web search snapshots (Civitai, GitHub README/LICENSE) dated **2026-05-07**.
- Phoenix prior artifacts: `artifacts/research/community_lora_roster_2026-04-29.yaml` (schema + tier semantics).

**Closing statement:** This document is **research authority** only; it **does not** download, bundle, or enable any checkpoint in CI.
