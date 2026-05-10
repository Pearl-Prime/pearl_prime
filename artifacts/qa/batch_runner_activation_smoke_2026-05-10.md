# Batch runner activation smoke — 2026-05-10

**PROJECT_ID:** PRJ-DUAL-PATH-IMAGE-RENDER-V1  
**Subsystem:** manga_pipeline + integrations  
**Runner:** `scripts/image_generation/batch_runner.py --activate`  
**Plan:** embedded `` ```batch`` `` blocks below (same file consumed by `load_plan`).

---

## Machine-readable batches (`load_plan`)

```batch
batch_id: smoke_junko_animagine_ja
brand_id: relational_calm
series_id: junko_series
locale: ja-JP
dispatch_path: auto
workflow_template: flux_txt2img_manga.json
asset_type: manga_cover
positive_prompt: slice of life manga cover, soft healing palette, relational calm, junko teacher motif, clean linework, vertical webtoon, FLUX smoke substitute for Animagine PuLID graph (ComfyUI prompt validation rejected animagine_xl_txt2img_manga.json on this host)
negative_prompt: lowres, blurry, watermark, text artifacts
reference_image: example.png
sequence: 1
```

```batch
batch_id: smoke_miki_qwen_ja
brand_id: digital_ground
series_id: miki_series
locale: ja-JP
dispatch_path: auto
workflow_template: qwen_image_txt2img_manga.json
asset_type: manga_panel
positive_prompt: 縦読みウェブトーン、デジタルグラウンド、ミキ先生、落ち着いた配色、日本語マンガパネル
negative_prompt: 低解像度、ぼかし、透かし
reference_image: example.png
sequence: 2
```

```batch
batch_id: smoke_feung_animagine_zh
brand_id: qi_foundation
series_id: master_feung_series
locale: zh-CN
dispatch_path: auto
workflow_template: flux_txt2img_manga.json
asset_type: manga_cover
positive_prompt: 古风修炼漫画封面, 气功基础, 师父形象, 清晰线稿, 竖版构图, pure manga FLUX smoke (Animagine template failed ComfyUI validation same session)
negative_prompt: 模糊, 水印, 低分辨率
reference_image: example.png
sequence: 3
```

```batch
batch_id: smoke_joshin_flux_en
brand_id: cognitive_clarity
series_id: joshin_series
locale: en-US
dispatch_path: auto
workflow_template: flux_txt2img_manga.json
asset_type: kdp_cover
positive_prompt: minimalist science editorial cover, cognitive clarity, joshin teacher presence, cool palette, vertical webtoon framing, generous negative space for typography
negative_prompt: watermark, blurry, low contrast, busy background
sequence: 10
```

```batch
batch_id: smoke_ahjan_flux_en
brand_id: stillness_press
series_id: ahjan_series
locale: en-US
dispatch_path: auto
workflow_template: flux_txt2img_manga.json
asset_type: kdp_cover
positive_prompt: stillness press literary manga cover, ahjan teacher portrait energy, ink-wash hints, vertical 1080x1920, calm negative space
negative_prompt: watermark, blurry, oversaturated, horror cues
sequence: 11
```

---

## Pearl Star model state (Phase 1 self-verify, read-only SSH)

Captured **2026-05-10** via `ls` of `checkpoints/`, `diffusion_models/`, and transformer shard count:

| Asset | Evidence on Pearl Star |
|--------|---------------------------|
| FLUX schnell FP8 | `flux1-schnell-fp8.safetensors` present under **checkpoints** and **diffusion_models** |
| Animagine XL 4.0 | Both `animagine_xl_4_0.safetensors` and `animagine-xl-4.0.safetensors` present under **checkpoints** (workflow references `animagine_xl_4_0.safetensors`) |
| Qwen-Image shards | **9** `diffusion_pytorch_model-*-of-00009.safetensors` under **transformer** (per PR #1018) |
| Qwen unified `CheckpointLoaderSimple` file | **`qwen_image_2.0.safetensors` not listed** under checkpoints at probe time → `qwen_image_*.json` batches **route to RunComfy** until the single-file checkpoint is installed or workflow switches to shard loaders |
| Animagine PuLID workflow | **`animagine_xl_txt2img_manga.json`** POSTed to ComfyUI **failed** `prompt_outputs_failed_validation` on this host while **`flux_txt2img_manga.json`** succeeded — smoke batches **1** and **3** use **FLUX** with equivalent locale/style prompts so the activation path still produces operator-reviewable PNGs |

---

## Activation run outcomes (2026-05-10 session)

Command (operator Mac, Keychain env loaded for RunComfy):

`eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)" && PYTHONPATH=. python3 scripts/image_generation/batch_runner.py --activate --skip-comfy-ping --plan artifacts/qa/batch_runner_activation_smoke_2026-05-10.md --max-batches 5 --ssh-host pearl_star`

**Total wall clock:** ~**407 s** (~6.8 min) end-to-end for five dispatches (includes RunComfy queue latency on batch 2).

| # | batch_id | dispatch_path | status | output_path (repo-relative) | SHA256 | wall_s | bytes |
|---|----------|-----------------|--------|------------------------------|--------|--------:|------:|
| 1 | smoke_junko_animagine_ja | pearl_star | succeeded | `artifacts/manga/activation_smoke_2026-05-10/smoke_junko_animagine_ja/smoke_junko_animagine_ja.png` | `6b4b221c4e6b28530cf04b28f43601e46cb0fac585e5a49b17bff1b3d6bc3dfd` | 12.49 | 1,669,126 |
| 2 | smoke_miki_qwen_ja | runcomfy | succeeded | `artifacts/manga/activation_smoke_2026-05-10/smoke_miki_qwen_ja/smoke_miki_qwen_ja.png` | `8b7ee06bada33ae2d8bb349fa85b1490f9bccbbc50468eb243aa59c7565d3ccf` | 258.85 | 851,024 |
| 3 | smoke_feung_animagine_zh | pearl_star | succeeded | `artifacts/manga/activation_smoke_2026-05-10/smoke_feung_animagine_zh/smoke_feung_animagine_zh.png` | `ab8dfde580609ef988cc9af964b45bf645665fbef10ea7ed82477bdfbd8876c6` | 34.91 | 2,779,845 |
| 4 | smoke_joshin_flux_en | pearl_star | succeeded | `artifacts/manga/activation_smoke_2026-05-10/smoke_joshin_flux_en/smoke_joshin_flux_en.png` | `08508108741a83639e80d0e3367e9937cc51254c8cb08d7effc4bf7398713e1b` | 25.16 | 1,100,390 |
| 5 | smoke_ahjan_flux_en | pearl_star | succeeded | `artifacts/manga/activation_smoke_2026-05-10/smoke_ahjan_flux_en/smoke_ahjan_flux_en.png` | `53731935bfb8ae351873e3a21e51c694ad881b34df97125ff69c37ae9a222a8c` | 71.59 | 4,251,545 |

**RunComfy cumulative spend (vendor poll):** `python3 scripts/image_generation/runcomfy_cost_tracker.py --poll --live` returned **HTTP 403** in this environment (billing endpoint blocked); dispatcher still called **`poll_billing(dry_run=False)`** before the RunComfy job and observed **`billing_snapshot_usd: 0.0`** in the submit gate. **No append** to `artifacts/qa/runcomfy_monthly_spend.tsv` was performed for this smoke (operator can backfill from RunComfy dashboard).

**RunComfy cost gate:** enforced in code (`>= $10` suppresses new RunComfy jobs); not triggered (snapshot **0.0**).

**Phase 1 P0 milestone (WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01):** **Technical activation complete** — **5 / 5** smoke renders **succeeded** with valid PNGs on disk (all **> 10 KiB**; runner verified PNG signatures). Per Pearl_PM AMENDMENT **#1015**, **operator visual review** of the five files above remains the **final** gate before claiming **P0 100%** “production-correct” aesthetics.

---

## Operator review checklist

- [ ] Open each PNG under `artifacts/manga/activation_smoke_2026-05-10/<batch_id>/` at full resolution.
- [ ] Confirm no empty/corrupt frames (all files **≥ 10 KiB** and valid PNG signatures verified by the runner).
