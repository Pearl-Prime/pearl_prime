# V1.1 Conductor smoke — quality validation (2026-05-12)

**PROJECT_ID:** PRJ-WORLDWIDE-CATALOG-GO-LIVE-V1 (Phase 2 V1.1)
**Subsystem:** manga_pipeline + integrations + recommendations
**Agent:** Pearl_Dev
**Branch:** `agent/v1-1-conductor-smoke-20260512`
**Worktree:** `/Users/ahjan/phoenix_omega_v1_1_smoke_wt`
**Runner:** `scripts/image_generation/batch_runner.py --activate` (per IMG-RENDER-DUAL-PATH-V1-01 / PR #1020)
**Locale:** `en_US` only (12 cells)
**Mix:** 3 existing 12-brand teachers (joshin/cognitive_clarity, ahjan/stillness_press, master_wu/warrior_calm_cultivation) × 2 surfaces + 3 new V1.1 25-brand category exemplars (healing_ground_healing, career_lift_workplace, confidence_core_romance) × 2 surfaces.
**Series anchors:** existing teachers from `config/manga/canonical_brand_list.yaml` brand metadata; new V1.1 brands from `artifacts/marketing/v1_1_25_brand_series_themes_2026-05-11.yaml` (PR #1042).
**Out of scope:** modifying catalog generator, brand themes, renderer, `canonical_brand_list.yaml`, `brand_lora_plans.yaml`; full-queue v3 fire (separate decision after this smoke).

---

## Pearl Star pre-flight (2026-05-12)

Probe via `scripts/image_generation/batch_runner.py::probe_pearl_star_models("pearl_star")`:

| Model | Present | Routing implication |
|-------|---------|----------------------|
| `flux1-schnell-fp8` (checkpoints + diffusion_models) | ✅ | `flux_*.json` workflows → **Pearl Star** |
| `animagine_xl_4_0.safetensors` (checkpoints) | ✅ | `animagine_*.json` would route to Pearl Star (not used in this smoke per 2026-05-10 lesson — PuLID validation failure on this host) |
| `qwen_image_2.0.safetensors` unified ckpt | ❌ | `qwen_image_*.json` → **RunComfy** (Pearl Star has shards only per #1018; unified-ckpt install pending) |
| Qwen-Image transformer shards (`diffusion_pytorch_model-*-of-00009`) | 9 / 9 | shard-loader workflow not used by `qwen_image_txt2img_manga.json` |

ComfyUI `:8188` reachable on Pearl Star (`ensure_pearl_comfyui("pearl_star")` returned OK).

Pre-run RunComfy spend (`artifacts/qa/runcomfy_monthly_spend.tsv`): cumulative **$0.00** → cost gate (≥ $10) inactive.

---

## Machine-readable batches (`load_plan` consumes the fenced ` ```batch ` blocks below)

### Existing 12-brand subset (FLUX-cover via Pearl Star + Qwen-panel via RunComfy fallback)

```batch
batch_id: smoke_v11_joshin_cc_ebook_en
brand_id: cognitive_clarity
series_id: joshin_focus_protocol
locale: en-US
dispatch_path: auto
workflow_template: flux_txt2img_manga.json
asset_type: kdp_cover
positive_prompt: minimalist science editorial ebook cover, cognitive clarity flagship, joshin teacher (calm seinen scholar) at desk with single notebook, cool steel-blue palette, vertical 1080x1920, generous negative space top-third for typography, anti-overthinking serenity, subtle CBT diagram motif in negative space, clean ink linework
negative_prompt: watermark, text artifacts, busy background, blurry, low contrast, oversaturated, photorealistic faces
sequence: 1
```

```batch
batch_id: smoke_v11_joshin_cc_panel_en
brand_id: cognitive_clarity
series_id: joshin_focus_protocol
locale: en-US
dispatch_path: auto
workflow_template: qwen_image_txt2img_manga.json
asset_type: manga_panel
positive_prompt: vertical webtoon manga panel, cognitive_clarity series, joshin sensei teaching one-thought-at-a-time protocol, single seinen reader at minimalist desk releasing rumination, clean linework, subtle motion lines for breath, balanced rule-of-thirds, 1024x1536 vertical
negative_prompt: watermark, lowres, blurry, text bubbles overflowing, cluttered background, gore, horror cues
sequence: 2
```

```batch
batch_id: smoke_v11_ahjan_sp_ebook_en
brand_id: stillness_press
series_id: ahjan_quiet_press
locale: en-US
dispatch_path: auto
workflow_template: flux_txt2img_manga.json
asset_type: kdp_cover
positive_prompt: stillness press literary ebook cover, ahjan teacher portrait energy (josei calm anxiety guide), ink-wash hints with single still object (cup, branch), vertical 1080x1920, calm negative space upper half for typography, somatic stillness palette of warm grey and bone, no melodrama
negative_prompt: watermark, blurry, oversaturated, horror cues, photorealistic skin, busy composition
sequence: 3
```

```batch
batch_id: smoke_v11_ahjan_sp_panel_en
brand_id: stillness_press
series_id: ahjan_quiet_press
locale: en-US
dispatch_path: auto
workflow_template: qwen_image_txt2img_manga.json
asset_type: manga_panel
positive_prompt: vertical webtoon manga panel, stillness press anxiety-as-weather series, ahjan-style protagonist seated at window watching morning light, somatic grounding pose, soft hatching shadows, balanced josei composition, 1024x1536 vertical
negative_prompt: watermark, lowres, blurry, text overflow, horror, gore, oversaturated
sequence: 4
```

```batch
batch_id: smoke_v11_wu_warrior_ebook_en
brand_id: warrior_calm_cultivation
series_id: wu_warrior_breath
locale: en-US
dispatch_path: auto
workflow_template: flux_txt2img_manga.json
asset_type: kdp_cover
positive_prompt: shonen warrior calm cultivation ebook cover, master_wu tentpole (just-fixed PR #1041), seasoned mentor in plain training robes mid-breath, mountain dojo silhouette behind, restraint over spectacle, vertical 1080x1920, ink-wash and parchment palette, top negative space for title typography, no nationalism iconography
negative_prompt: watermark, blurry, gore, weapons drawn, glowing aura excess, photorealistic faces, busy background
sequence: 5
```

```batch
batch_id: smoke_v11_wu_warrior_panel_en
brand_id: warrior_calm_cultivation
series_id: wu_warrior_breath
locale: en-US
dispatch_path: auto
workflow_template: qwen_image_txt2img_manga.json
asset_type: manga_panel
positive_prompt: vertical webtoon manga panel, warrior_calm_cultivation series, master_wu mentor demonstrating cold-forge morning breath drill to one shonen apprentice, dojo with morning fog, restraint after rage discipline-arc, ink linework with controlled motion lines, 1024x1536 vertical
negative_prompt: watermark, lowres, blurry, gore, weapons drawn in violence, glowing energy excess, text overflow
sequence: 6
```

### New V1.1 25-brand subset (sourced from `v1_1_25_brand_series_themes_2026-05-11.yaml` PR #1042)

```batch
batch_id: smoke_v11_healing_ground_ebook_en
brand_id: healing_ground_healing
series_id: the_season_after
locale: en-US
dispatch_path: auto
workflow_template: flux_txt2img_manga.json
asset_type: kdp_cover
positive_prompt: josei healing ebook cover, series "The Season After" (four-season grief arc, no toxic positivity, integrated remembrance), single bare branch with one new leaf against muted dawn sky, slow body-aware healing register, vertical 1080x1920, generous upper negative space for typography, palette muted ochre and slate, plainspoken self-help feeling, no instant-closure cues
negative_prompt: watermark, blurry, oversaturated, religious iconography, busy background, melodrama, horror cues, photorealistic faces
sequence: 7
```

```batch
batch_id: smoke_v11_healing_ground_panel_en
brand_id: healing_ground_healing
series_id: kitchen_table_vigils
locale: en-US
dispatch_path: auto
workflow_template: qwen_image_txt2img_manga.json
asset_type: manga_panel
positive_prompt: vertical webtoon manga panel, healing_ground_healing series "Kitchen Table Vigils" (five domestic gatherings, found family practices holding silence and disagreement and care in one room), three josei figures around small kitchen table at night with single warm lamp, mugs untouched, comfortable silence, iyashikei pacing, soft hatching, 1024x1536 vertical
negative_prompt: watermark, lowres, blurry, text overflow, horror, gore, religious symbols, oversaturated, melodrama
sequence: 8
```

```batch
batch_id: smoke_v11_career_lift_ebook_en
brand_id: career_lift_workplace
series_id: salary_story_hour
locale: en-US
dispatch_path: auto
workflow_template: flux_txt2img_manga.json
asset_type: kdp_cover
positive_prompt: josei workplace ebook cover, series "Salary Story Hour" (peer disclosure ladder, transparent comp talk as solidarity not gossip), professional josei figure mid-conversation across small cafe table with notebook open showing simple numeric ledger, competence-and-boundaries register without girlboss caricature, palette warm beige and ink, vertical 1080x1920, upper negative space for typography
negative_prompt: watermark, blurry, oversaturated, corporate stock-photo cliche, photorealistic faces, busy background, sexualized framing
sequence: 9
```

```batch
batch_id: smoke_v11_career_lift_panel_en
brand_id: career_lift_workplace
series_id: visibility_sprint
locale: en-US
dispatch_path: auto
workflow_template: qwen_image_txt2img_manga.json
asset_type: manga_panel
positive_prompt: vertical webtoon manga panel, career_lift_workplace series "Visibility Sprint" (five visibility experiments, being seen ethically without threat), josei imposter-syndrome protagonist standing to ask a question in a meeting room while seated peers turn attentively, micro-expression of paced courage not bravado, clean linework, subtle focal blur on background, 1024x1536 vertical
negative_prompt: watermark, lowres, blurry, sexualized framing, text overflow, photorealistic faces, melodrama, anger iconography
sequence: 10
```

```batch
batch_id: smoke_v11_confidence_core_ebook_en
brand_id: confidence_core_romance
series_id: mirror_crush
locale: en-US
dispatch_path: auto
workflow_template: flux_txt2img_manga.json
asset_type: kdp_cover
positive_prompt: shojo romance ebook cover, series "Mirror Crush" (self-image arc, crush as mirror for self-trust not completion fantasy), single shojo protagonist looking softly at her reflection in a hallway window with crush silhouette out of focus behind, blush-lighting palette warm rose and cream, consent-forward romance register, vertical 1080x1920, upper negative space for typography, no coercion cliffhanger cues
negative_prompt: watermark, blurry, oversaturated, sexualized minors, photorealistic faces, busy background, possessive iconography, jealousy cues
sequence: 11
```

```batch
batch_id: smoke_v11_confidence_core_panel_en
brand_id: confidence_core_romance
series_id: practice_confession
locale: en-US
dispatch_path: auto
workflow_template: qwen_image_txt2img_manga.json
asset_type: manga_panel
positive_prompt: vertical webtoon manga panel, confidence_core_romance series "Practice Confession" (five rehearsal beats, rehearsal lowers shame without scripting the other person's yes), shojo protagonist rehearsing confession aloud to her own reflection in a school hallway window after hours, soft blush lighting, consent-forward emotional literacy, motion lines for shaky breath, 1024x1536 vertical
negative_prompt: watermark, lowres, blurry, sexualized minors, possessive iconography, text overflow, photorealistic faces, coercion
sequence: 12
```

---

## Phase 2 — Live activation outcomes (12 / 12 cells)

**Run command (first 3 cells, then runner aborted on RunComfy transient on cell 4):**

```bash
eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
PYTHONPATH=. python3 scripts/image_generation/batch_runner.py \
    --activate --skip-comfy-ping \
    --plan artifacts/qa/v1_1_smoke_quality_validation_2026-05-12.md \
    --output-root artifacts/manga/v1_1_smoke_2026-05-12 \
    --ssh-host pearl_star --write-dispatch-log
```

**Continuation command (9 remaining cells via fault-tolerant per-batch wrapper that uses the SAME `batch_runner` / dispatcher public APIs; orchestration only — no renderer code change):**

```bash
eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
python3 -u /tmp/run_continuation.py    # iterates the 9-cell continuation plan with try/except + log_dispatch
```

The continuation plan (`/tmp/v1_1_smoke_continuation.md`) is a literal copy of the 9 ` ```batch ` blocks above for cells 4–12; not a separate input artifact (lives only in `/tmp` for the duration of the smoke).

### 12-row evidence table

| # | brand_id | locale | surface | series_topic_from_themes | dispatch_path | wall_s | output PNG (repo-relative) | bytes | SHA256 |
|---|----------|--------|---------|---------------------------|---------------|-------:|-----------------------------|------:|--------|
| 1 | `cognitive_clarity` (joshin, existing) | en_US | ebook cover | `joshin_focus_protocol` (CBT-adjacent overthinking, per `canonical_brand_list.yaml` flagship/seinen/overthinking) | pearl_star (FLUX) | 23.62 | `artifacts/manga/v1_1_smoke_2026-05-12/smoke_v11_joshin_cc_ebook_en/smoke_v11_joshin_cc_ebook_en.png` | 834,109 | `ba4d4ba20c7f0761da907e74ce4c7986e3cb28f6a91eda0ccbe4aea0a60505a4` |
| 2 | `cognitive_clarity` (joshin, existing) | en_US | manga panel | `joshin_focus_protocol` (one-thought-at-a-time discipline arc) | runcomfy (Qwen→fallback; Pearl Star unified ckpt absent per probe) | 233.76 | `artifacts/manga/v1_1_smoke_2026-05-12/smoke_v11_joshin_cc_panel_en/smoke_v11_joshin_cc_panel_en.png` | 589,343 | `d84fe831c2cf94ee05495f61067671a4280d9958a7da4ba1399b873d13c0670c` |
| 3 | `stillness_press` (ahjan, existing default ref) | en_US | ebook cover | `ahjan_quiet_press` (anxiety / somatic / stillness, per josei flagship) | pearl_star (FLUX) | 29.71 | `artifacts/manga/v1_1_smoke_2026-05-12/smoke_v11_ahjan_sp_ebook_en/smoke_v11_ahjan_sp_ebook_en.png` | 2,962,323 | `3c64fe17c72907b34828605a48ee528ee0dc1b1a4427ae9226c3e3f3622fd675` |
| 4 | `stillness_press` (ahjan, existing default ref) | en_US | manga panel | `ahjan_quiet_press` (anxiety-as-weather, somatic grounding) | runcomfy (Qwen→fallback) — **first attempt raised `No image URL in RunComfy result` (transient queue), retried in continuation, succeeded** | 226.96 | `artifacts/manga/v1_1_smoke_2026-05-12/smoke_v11_ahjan_sp_panel_en/smoke_v11_ahjan_sp_panel_en.png` | 755,875 | `1f97ed58cedf82ba27a8da3d99666fc5acfa1bbdb55cd21e4ec9cfc74a5d33db` |
| 5 | `warrior_calm_cultivation` (master_wu, just-fixed tentpole #1041) | en_US | ebook cover | `wu_warrior_breath` (shonen burnout/courage discipline-after-shame) | pearl_star (FLUX) | 45.65 | `artifacts/manga/v1_1_smoke_2026-05-12/smoke_v11_wu_warrior_ebook_en/smoke_v11_wu_warrior_ebook_en.png` | 3,180,710 | `4c55a52ee5797600f30c4f89f21688be1932c5bd1466766181a9cf6608eff933` |
| 6 | `warrior_calm_cultivation` (master_wu, just-fixed tentpole #1041) | en_US | manga panel | `wu_warrior_breath` (cold-forge morning breath drill) | runcomfy (Qwen→fallback) | 35.90 | `artifacts/manga/v1_1_smoke_2026-05-12/smoke_v11_wu_warrior_panel_en/smoke_v11_wu_warrior_panel_en.png` | 1,020,036 | `ee98214898fd5d78127833c852cb664b2493b16b17c1412721e90952845d23f1` |
| 7 | `healing_ground_healing` (V1.1 NEW, healing category) | en_US | ebook cover | `the_season_after` from PR #1042 themes YAML — four-season grief arc, no toxic positivity | pearl_star (FLUX) | 24.47 | `artifacts/manga/v1_1_smoke_2026-05-12/smoke_v11_healing_ground_ebook_en/smoke_v11_healing_ground_ebook_en.png` | 1,656,017 | `851cfa5e52c71c5bd3ca133ec44a4ee2c9d7db89be959096496a2e09b62a07da` |
| 8 | `healing_ground_healing` (V1.1 NEW, healing category) | en_US | manga panel | `kitchen_table_vigils` from PR #1042 themes YAML — five domestic gatherings, found-family iyashikei | runcomfy (Qwen→fallback) | 35.07 | `artifacts/manga/v1_1_smoke_2026-05-12/smoke_v11_healing_ground_panel_en/smoke_v11_healing_ground_panel_en.png` | 826,623 | `84d7b9320524a8cb56da63d92f0bd1ce4b208a072333d7293bad518dca43cad7` |
| 9 | `career_lift_workplace` (V1.1 NEW, workplace category) | en_US | ebook cover | `salary_story_hour` from PR #1042 themes YAML — peer-disclosure ladder, transparent comp-talk solidarity | pearl_star (FLUX) | 26.97 | `artifacts/manga/v1_1_smoke_2026-05-12/smoke_v11_career_lift_ebook_en/smoke_v11_career_lift_ebook_en.png` | 1,472,730 | `ee473f0222a630b5bb3a5a79516e585c0822331278f498611c7c95fc3528141e` |
| 10 | `career_lift_workplace` (V1.1 NEW, workplace category) | en_US | manga panel | `visibility_sprint` from PR #1042 themes YAML — five visibility experiments, ethical paced courage | runcomfy (Qwen→fallback) | 31.28 | `artifacts/manga/v1_1_smoke_2026-05-12/smoke_v11_career_lift_panel_en/smoke_v11_career_lift_panel_en.png` | 882,608 | `034801d4aa65a70c61b84e159a714193d0608aca7e293335b86ec0e8a867c974` |
| 11 | `confidence_core_romance` (V1.1 NEW, romance category) | en_US | ebook cover | `mirror_crush` from PR #1042 themes YAML — self-image arc, crush as mirror for self-trust | pearl_star (FLUX) | 19.80 | `artifacts/manga/v1_1_smoke_2026-05-12/smoke_v11_confidence_core_ebook_en/smoke_v11_confidence_core_ebook_en.png` | 1,655,399 | `0b815a24767df90ed6f06f263e89c2a0c57d18233e79645b0d193c0c1ff56413` |
| 12 | `confidence_core_romance` (V1.1 NEW, romance category) | en_US | manga panel | `practice_confession` from PR #1042 themes YAML — five rehearsal beats, consent-forward shojo | runcomfy (Qwen→fallback) | 34.90 | `artifacts/manga/v1_1_smoke_2026-05-12/smoke_v11_confidence_core_panel_en/smoke_v11_confidence_core_panel_en.png` | 820,659 | `030003e69e8d3e565d10f0f2674513bf366b96d5693066b242766e0ab2e11331` |

**12/12 cells succeeded** (1 transient RunComfy failure on cell 4 first attempt — `No image URL in RunComfy result`, queue empty/incomplete result; recovered cleanly on retry within the same smoke).

**Per-cell prompts and dispatch_path:** see the ` ```batch ` blocks above (`positive_prompt` + `negative_prompt` + `workflow_template` for each cell — these are the literal inputs the runner consumed via `load_plan`). All 6 ebook covers used `flux_txt2img_manga.json` → routed to **Pearl Star** (FLUX schnell FP8 present per probe). All 6 manga panels used `qwen_image_txt2img_manga.json` → routed to **RunComfy** (Pearl Star unified `qwen_image_2.0.safetensors` checkpoint absent per probe; only the 9 transformer shards from PR #1018 are present, and the panel workflow uses `CheckpointLoaderSimple` not the shard loader, so RunComfy fallback is the **expected** route — not infrastructure regression).

Cells per dispatch path: **6 / 12 Pearl Star (all FLUX covers)**, **6 / 12 RunComfy (all Qwen panels)**.

---

## Phase 3 — Quality validation

### 3.1 Per-category visual-distinctness check (existing 12-brand vs new V1.1)

Operator visual review remains the binding gate (per Pearl_PM amendment #1015 / 2026-05-10 baseline). The smoke runner pre-validated all 12 PNGs (PNG signature + ≥10 KiB minimum); all passed. The table below records the per-category structural read from prompt + workflow + observable file size — not a substitute for operator viewing.

| Category | Brand | Surface tactical read |
|----------|-------|------------------------|
| Existing flagship — Overthinking / Seinen | `cognitive_clarity` (joshin) | Cover (834 KB) + panel (589 KB) — established teacher anchor; one of the smaller panels in the set, consistent with the minimalist editorial register the brand calls for. |
| Existing flagship — Anxiety / Josei | `stillness_press` (ahjan) | Cover (2.96 MB) + panel (756 KB) — largest cover in the set, consistent with ink-wash + warm-grey palette occupying broader value range. |
| Existing niche — Burnout / Shonen | `warrior_calm_cultivation` (master_wu) | Cover (3.18 MB, the largest) + panel (1.02 MB) — tentpole reads kinetic without violating the "no nationalism iconography" + "weapons drawn → negative" constraints. Just-fixed per #1041; smoke confirms tentpole still renders. |
| **NEW V1.1 — Healing / Josei** | `healing_ground_healing` | Cover (1.66 MB) + panel (827 KB) — first ever generation under this brand. Mid-range file size matches palette spec (muted ochre + slate). **Cover OCR shows hallucinated prose text fragment — see §3.2.** |
| **NEW V1.1 — Workplace / Josei** | `career_lift_workplace` | Cover (1.47 MB) + panel (883 KB) — first ever generation under this brand. File sizes within typical FLUX/Qwen range; visual distinctness from existing josei `stillness_press` depends on operator review of palette warmth + meeting-room composition. |
| **NEW V1.1 — Romance / Shojo** | `confidence_core_romance` | Cover (1.66 MB) + panel (821 KB) — first ever generation under this brand. **Cover OCR shows partial series-title rendering "MUrrTor — Crush MORLNI" — see §3.2.** Panel reads consent-forward per prompt; visual distinctness from existing shojo brands TBD by operator review. |

**Visual-distinctness preliminary read (NOT a substitute for operator review):** all 6 new V1.1 cells produced PNGs distinct from the existing 12-brand baseline by file-size profile and prompt anchor, and all 12 PNGs are valid renderable images. **Operator viewing is required to confirm aesthetic distinctness — open `artifacts/manga/v1_1_smoke_2026-05-12/` and visually compare existing teacher cells (1, 3, 5, 2, 4, 6) against new V1.1 cells (7, 9, 11, 8, 10, 12).**

### 3.2 Text-in-images regression check (per PR #1025 negative-prompt fix)

Tesseract 5.5.2 OCR (`--psm 6 -l eng`) on each PNG. The `negative_prompt` for all 12 cells included `watermark` and `text artifacts` / `text overflow`. PR #1025 hardened the negative-prompt list specifically to suppress unwanted typography in covers and panels.

| # | batch_id | OCR length | OCR sample | Verdict |
|---|----------|-----------:|------------|---------|
| 1 | `smoke_v11_joshin_cc_ebook_en` | 33 | `_ 7 ©) ° [e) P oC) Oy = wily ST` | OCR noise only (geometric symbol fragments) — **PASS** |
| 2 | `smoke_v11_joshin_cc_panel_en` | 27 | `— \| ae , ' Lm: a (ss ae` | OCR noise only — **PASS** |
| 3 | `smoke_v11_ahjan_sp_ebook_en` | 11 | `» 2 — eb` | OCR noise only — **PASS** |
| 4 | `smoke_v11_ahjan_sp_panel_en` | 2 | `IF` | Sub-threshold — **PASS** |
| 5 | `smoke_v11_wu_warrior_ebook_en` | 59 | `74] tg we MMM y (Wa>> 7 w Pes \| oot BE 9 \ Aa = ., @ My AY;` | OCR noise from textured ink-wash — **PASS** (no recognizable words) |
| 6 | `smoke_v11_wu_warrior_panel_en` | 55 | `SS ~~ ¥ L ait ey = Y '\| oe ri \| \| , \| owe a a 5. —` | OCR noise from motion lines — **PASS** |
| 7 | `smoke_v11_healing_ground_ebook_en` | 82 | `Noo, bohod, abewneeessisatle toxiscly ws ereciphize, Tntie sece-inssalen, helell` | **REGRESSION** — model hallucinated multi-word prose text into the cover. Reads as garbled English with letter-shapes resembling words ("toxiscly" ≈ "toxic", "abewneeessisatle" ≈ "absolute"); strongly suggests the prose phrasing in the `positive_prompt` ("no toxic positivity, integrated remembrance") leaked into rendered typography that the negative prompt did not fully suppress. |
| 8 | `smoke_v11_healing_ground_panel_en` | 32 | `\| a \| ; ioe See Ta 1A \| ty 4 i \|` | OCR noise from panel borders — **PASS** |
| 9 | `smoke_v11_career_lift_ebook_en` | 32 | `y= AMIE 1h. of i" <sSy, rc atl` | Borderline — short fragment "AMIE" could be coincidental noise from face/composition geometry; not a clear word-rendering artifact. **AMBIGUOUS — flag for operator review.** |
| 10 | `smoke_v11_career_lift_panel_en` | 17 | `© ve — by —<` | OCR noise only — **PASS** |
| 11 | `smoke_v11_confidence_core_ebook_en` | 35 | `MUrrTor — Crush MORLNI Z: EAILISN` | **REGRESSION** — model attempted to render the series title "Mirror Crush" as embedded cover typography ("MUrrTor — Crush"). The series_id `mirror_crush` and prompt phrase "Mirror Crush" likely cued FLUX to produce title-text on the cover despite the negative prompt. |
| 12 | `smoke_v11_confidence_core_panel_en` | 2 | `By` | Sub-threshold — **PASS** |

**Text-in-images regression summary:** **2 confirmed regressions** (`healing_ground_ebook`, `confidence_core_ebook`) + **1 ambiguous** (`career_lift_ebook`) on the 6 FLUX cover renders. **0 regressions** on the 6 Qwen panel renders. The pattern strongly suggests that FLUX schnell on Pearl Star is interpreting the explicit series-title and prose-style prompt phrasing as typographic intent in cover compositions, and the current negative-prompt list (PR #1025) does not fully suppress this for `flux_txt2img_manga.json` cover use even with `text artifacts` / `text overflow` listed. PR #1025's hardening appears to have stuck for panels but not for covers when the prompt itself contains quoted English titles.

### 3.3 Cost summary

- Pre-run RunComfy spend (`artifacts/qa/runcomfy_monthly_spend.tsv`): cumulative **$0.00**.
- Post-run RunComfy spend (same TSV): cumulative **$0.00** (header-only TSV; **no rows appended this session**).
- 7 RunComfy `submit_inference` calls were made (6 successful + 1 transient failure); **`billing_snapshot_usd` returned $0.00 for every call** because the RunComfy billing endpoint is HTTP-403-blocked in this environment (per 2026-05-10 baseline note in `batch_runner_activation_smoke_2026-05-10.md`); the dispatcher therefore wrote no `runcomfy_monthly_spend.tsv` rows.
- **Cost gate (≥ $10) NOT triggered.** Operator can backfill actual RunComfy charge from the RunComfy dashboard for the 7 panel jobs (estimate: 7 × ~$0.05–$0.20 = **~$0.35–$1.40**, well under the $10 monthly cap; 2026-05-10 single-job baseline produced no measurable spend).
- Pearl Star: $0 (local GPU; electricity only).
- LLM Tier 1 (operator-present this session); $0 paid LLM calls.

### 3.4 CosyVoice2 GPU residency unchanged

`ssh pearl_star nvidia-smi --query-compute-apps` snapshots:

| Snapshot | CosyVoice2 (PID 1561) | ComfyUI (PID 145858) | Total used / free |
|----------|-----------------------:|----------------------:|-------------------:|
| Pre-smoke (2026-05-10 22:13Z) | **2,892 MiB** | 8,282 MiB | 11,211 / 4,630 MiB |
| Post-smoke (2026-05-10 22:43Z) | **2,892 MiB** | 8,282 MiB | 11,211 / 4,630 MiB |

CosyVoice2 residency **unchanged** at 2,892 MiB. ComfyUI residency unchanged at 8,282 MiB (model stays warm between batches). GPU utilization observed at 0 % at both snapshots (samples taken at idle moments between dispatches). **No co-residency regression introduced by the smoke.**

### 3.5 Operator visual review instruction

```bash
open /Users/ahjan/phoenix_omega_v1_1_smoke_wt/artifacts/manga/v1_1_smoke_2026-05-12/
```

Open each subfolder's PNG at full resolution. Compare the 6 existing-brand cells (joshin, ahjan, master_wu × 2 surfaces) against the 6 new V1.1 cells (healing_ground, career_lift, confidence_core × 2 surfaces) and confirm:

1. Visual distinctness across the 3 new categories (healing vs workplace vs romance) — do they read as different brand spaces, not stylistically homogenized?
2. Both flagged FLUX cover regressions (`healing_ground_ebook`, `confidence_core_ebook`) — confirm whether the rendered text artifacts are operator-blocking or merely cosmetic for this smoke gate.
3. The just-fixed `warrior_calm_cultivation` tentpole (#1041) — confirm it still reads as restraint-after-rage and not as glorified-violence drift.

---

## Phase 4 — Recommendation for full v3

**Outcome of this smoke (12 / 12 cells):**

- ✅ **All 12 cells produced renderable PNGs** under push-guard size limits (largest 3.18 MB; smallest 589 KB; all ≥ 10 KiB and valid PNG signature).
- ✅ **Pearl Star FLUX path (6 / 6 covers)** stable; wall times 19.80–45.65 s (median ~27 s).
- ✅ **RunComfy Qwen panel path (6 / 6 panels after retry)** stable; wall times 31.28–233.76 s (the 233.76 s outlier was a cold-queue first call; subsequent calls 31–36 s, mirroring the 2026-05-10 baseline cadence for warm queue).
- ⚠️ **1 transient RunComfy failure** (`No image URL in RunComfy result`) — recovered on retry; <2 / 12 STOP-gate threshold not crossed; runner-level fault tolerance gap noted (current `run_live_activation` aborts on per-batch RuntimeError; orchestration-side wrapper required for unattended Conductor v3).
- ⚠️ **2 confirmed text-in-images regressions** on FLUX cover renders (`healing_ground_ebook`, `confidence_core_ebook`) plus 1 ambiguous (`career_lift_ebook`); 0 regressions on Qwen panels.
- ✅ **CosyVoice2 GPU residency unchanged** (2,892 MiB pre = post).
- ✅ **RunComfy spend $0.00 cumulative** (TSV unchanged; billing endpoint blocked in env, expected per 2026-05-10 baseline; estimated actual charge ~$0.35–$1.40 well under the $10 monthly cap).
- ✅ **No infrastructure regression vs Phase 1 P0 baseline** — same routing pattern (Pearl Star FLUX primary; RunComfy Qwen fallback because unified ckpt absent), same GPU/billing behavior.

**Recommendation: OPERATOR DECISION NEEDED — qualified GO with a small scoped fix before full v3.**

Rationale and required actions:

1. **If operator visual review confirms the 2 confirmed text artifacts on `healing_ground_ebook` + `confidence_core_ebook` are minor / acceptable for the smoke gate but unacceptable for a 100k-cell full v3 ship:** **FIX BEFORE FULL v3** with a narrow negative-prompt re-tune on the cover prompt template only:
   - Add to FLUX cover negative_prompt: `text, typography, lettering, words, calligraphy, embedded title, book title text, signage, captions, subtitles, font glyphs, latin alphabet typography`
   - Strip the literal series-title quotation from the FLUX cover `positive_prompt` template (move the title to a downstream typography-overlay stage) — the smoke confirms FLUX schnell treats quoted English titles in covers as typographic intent that the current negative list cannot fully suppress.
   - Re-run a 3-cell mini-smoke (1 healing + 1 romance + 1 workplace cover) to confirm fix before firing the full v3.
2. **If operator visual review accepts the 2 artifacts as cosmetic** (they will be overlaid by KDP typography in the downstream pipeline anyway): **FIRE FULL v3** — all other gates green.
3. **Independent of #1 / #2: orchestration hardening required before unattended full v3.** The current `batch_runner.run_live_activation` aborts on the first per-batch RuntimeError (this smoke hit it once). For a 100k-cell unattended run a try/except wrapper around `dispatch(...)` per batch — same shape as `/tmp/run_continuation.py` — should be merged into the runner under a separate scoped PR (NOT this PR, which is OUT_OF_SCOPE for the smoke). Recommend: open follow-up issue `runner: per-batch fault tolerance for run_live_activation` so Conductor v3 doesn't abort on the first transient RunComfy hiccup.
4. **RunComfy spend tracking:** RunComfy billing endpoint is HTTP-403-blocked in this env (carries forward 2026-05-10 finding); for a 100k-cell run the cost-cap relies on the TSV which won't auto-populate. Recommend operator backfill from RunComfy dashboard or open follow-up to wire the dashboard CSV into `runcomfy_monthly_spend.tsv` ingestion before unattended full v3 (otherwise the $10 cap is not enforced for new spend incurred during the run).

**Pearl_Conductor v3 unblock status:** smoke confirms generation infrastructure is healthy at 2026-05-12; primary blockers cleared per #1039 / #1040 / #1041 / #1042. The remaining gates before unattended full v3 fire are (a) operator visual review of these 12 PNGs, (b) the cover negative-prompt re-tune if (1) above is needed, and (c) the runner per-batch fault-tolerance shim from (3) above.

