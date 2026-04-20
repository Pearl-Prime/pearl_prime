# Manga catalog, volume production, Stillness Press assets — handoff

**Date:** 2026-04-17  
**Audience:** Pearl_PM, Pearl_Architect, Pearl_GitHub, next implementer  
**Purpose:** Single place for “what exists,” “what was shipped,” “what is not wired,” and **next actions** for catalog-driven manga volumes and related tooling.

---

## 1. Executive summary

| Area | State |
|------|--------|
| **Stillness Press (US Brand 1) image bank** | **840 / 840** PNGs (15 topics × 4 intents × 7 styles × 2 ratios). Index: `image_bank/index.json`. Tooling: `scripts/manga/stillness_press_image_bank.py` (`audit` / `generate` / `index`). Audits under `artifacts/manga/stillness_press_image_bank_audit*.txt` and `stillness_press_image_bank_audit_FINAL.txt`. |
| **Manga chapter pipeline** | **One chapter per** `run_manga_chapter.py` invocation. Produces workspace artifacts + optional **`manga.pdf`** (Pillow merge of `final_page_composite/page_*.png`). **No** shipped “full volume from catalog SKU” orchestrator. |
| **Lettering / speech bubbles** | **Dialogue** lives in `chapter_script`; **lettering_spec** only records `silence_confirmed` per panel. **Layout** (`page_compose.compose_final_page_pngs`) tiles panel PNGs only — **no rendered text or balloons** on pages. |
| **“Catalog” (two meanings)** | (A) **Pearl Prime** `generate_full_catalog.py` / BookSpecs = **text books**, not manga PDF assembly. (B) **Manga portfolio** `artifacts/manga/MANGA_CATALOG_PLAN.md` (and `MANGA_FULL_CATALOG_PLAN.md`) = **series matrix** (e.g. SP-001 *The Alarm Is Lying*) — **planning docs**, not machine-imported into `run_series_setup.py` today. |
| **Cloudflare Workers AI FLUX** | `load_credentials(for_workers_ai_image=True)` prefers **`CLOUDFLARE_AI_API_TOKEN`**; `call_flux` retries alternate bearer on **401**. Doc: `docs/VIDEO_CLOUDFLARE_FLUX_CREDENTIALS.md`. |
| **ITE QC CLI** | `scripts/manga/ite_qc.py`: **`--workspace`** fills `debug/ite/*.json` paths, default `-o`, skips job gate if **`job.json`** missing under workspace (with NOTE to stderr). |

---

## 2. Inventory — authority & entrypoints

### 2.1 Specs and governance

| Asset | Path |
|-------|------|
| Manga pipeline summary | `specs/AI_MANGA_PIPELINE_SUMMARY.md` |
| Spec index | `specs/README.md` |
| Implementation map | `docs/MANGA_IMPLEMENTATION_OUTLINE.md` |
| Operator onboarding | `docs/MANGA_PIPELINE_ONBOARDING.md` |
| Brand / series pacing | `config/manga/manga_brand_series_plan.yaml` |
| Illustration styles | `config/manga/brand_illustration_styles.yaml` |
| Flux scenes / intents | `config/video/flux_bank_scenes.yaml` |
| Topic → band / palette | `config/video/brand_style_tokens.yaml` |
| Image bank asset schema | `schemas/video/image_bank_asset_v1.schema.json` |
| Manga JSON schemas | `schemas/manga/*.schema.json` |
| Gate registry | `config/manga/gate_registry.yaml` |

### 2.2 Runtime code (manga)

| Concern | Path |
|---------|------|
| Chapter DAG order + stages | `phoenix_v4/manga/runner/chapter_runner.py` |
| CLI: full chapter | `scripts/manga/run_manga_chapter.py` |
| CLI: series setup | `scripts/manga/run_series_setup.py` |
| Transmission split | `phoenix_v4/manga/transmission.py` |
| Series emit / replay | `phoenix_v4/manga/series/emit.py`, `phoenix_v4/manga/series/*.py` |
| Panel prompts | `phoenix_v4/manga/chapter/visual_from_script.py` |
| Lettering spec | `phoenix_v4/manga/chapter/lettering_from_script.py` |
| Page composite | `phoenix_v4/manga/chapter/page_compose.py` |
| Image backends | `phoenix_v4/manga/image_backend.py` |
| ITE gates | `phoenix_v4/manga/ite_pipeline.py`, `phoenix_v4/manga/qc/` |
| CLI: ITE QC | `scripts/manga/ite_qc.py` |

### 2.3 Stillness Press image bank

| Asset | Path |
|-------|------|
| Bank root | `image_bank/stillness_press/<topic>/` |
| Global index | `image_bank/index.json` |
| Audit (final full matrix) | `artifacts/manga/stillness_press_image_bank_audit_FINAL.txt` |
| Generator / audit CLI | `scripts/manga/stillness_press_image_bank.py` |
| RunComfy batch (video-bank naming `vb_*`) | `scripts/image_generation/runcomfy_batch.py` |
| Cloudflare bank build (flat legacy layout) | `scripts/video/run_flux_bank_build.py` |
| ComfyUI workflow | `scripts/image_generation/comfyui_workflows/flux_video_bank.json` |

**Filename convention (manga bank):**  
`{intent}_{style_slug}_{sNN}.png` and `{intent}_{style_slug}_{sNN}_landscape.png`  
with intents: `environment_atmosphere`, `symbolic_metaphor`, `hook_visual`, `character_emotion`; styles `soft_ghibli_s00` … `geometric_abstract_s06`.

### 2.4 Catalog layers (do not conflate)

| Layer | What it is | Primary scripts / artifacts |
|-------|------------|-----------------------------|
| **Pearl Prime book catalog** | Allocations + **BookSpec** JSON for **ebooks** / compile pipeline | `scripts/generate_full_catalog.py`, `scripts/list_english_catalog_titles.py`, `artifacts/full_catalog/README.md` |
| **Manga portfolio plan** | Human-readable **series × genre × topic × author** matrix | `artifacts/manga/MANGA_CATALOG_PLAN.md`, `artifacts/manga/MANGA_FULL_CATALOG_PLAN.md` |
| **Weekly / format queue** | Production shape hints (e.g. `manga_volume` panel counts) | `scripts/catalog/weekly_production_queue.py` (see `MANGA_RUNTIMES`) |

There is **no** single CLI: `MANGA_CATALOG_PLAN` row → N chapters → one PDF.

### 2.5 Tests (manga)

| Tests | Path |
|-------|------|
| Schemas, transmission, series, visual, production, runner E2E | `tests/test_manga_*.py`, `tests/manga/test_ite_qc.py` |
| Fixtures | `tests/fixtures/manga/**` |

### 2.6 Git / PR / governance (image bank slice)

- Large LFS pushes may require **`PUSH_GUARD_MAX_FILES`** above default **300** (e.g. **500–900**) when comparing a branch to `origin/main` with hundreds of PNGs.
- PR governance still applies: file-count and subsystem checks (`scripts/ci/pr_governance_review.py`).

---

## 3. What was demonstrated (QA manga PDF)

- **Workspace:** `artifacts/manga/stillness_press_qa_run/` (regeneratable; **not** guaranteed in git — **artifacts are often local**).
- **Series id (QA slug):** `sp_qa_iyashikei_001` from `run_series_setup.py` (not a marketing title from `MANGA_CATALOG_PLAN.md`).
- **Author persona (fixture path):** `Hana Tidecalm` / `stillness_press` / `iyashikei` / topic **anxiety** — see `series/manga_author_identity.json` in that workspace after setup.
- **PDF path:** `artifacts/manga/stillness_press_qa_run/manga.pdf` (after `run_manga_chapter.py … --export-pdf`). **Replay** backend mapped panels to **`image_bank/stillness_press/anxiety/*.png`** via `replay/map.json`.
- **Regenerate PDF (minimal):**

```bash
mkdir -p artifacts/manga/stillness_press_qa_run/replay
python3 scripts/manga/run_series_setup.py \
  --workspace artifacts/manga/stillness_press_qa_run \
  --series-id sp_qa_iyashikei_001 --arc-id arc_1 --genre-id iyashikei \
  --brand-id stillness_press --topic anxiety --locale en_US
# write replay/map.json panel_id → relative paths under repo (see prior QA map)
PYTHONPATH=. python3 scripts/manga/run_manga_chapter.py \
  --workspace artifacts/manga/stillness_press_qa_run \
  --backend replay --replay-map artifacts/manga/stillness_press_qa_run/replay/map.json \
  --teacher-id ahjan --chapter-number 1 --style-id cozy_iyashikei \
  --auto-revision --max-revision-rounds 2 --export-pdf
```

---

## 4. Gaps and recommended next work

### 4.1 Catalog → full “book” (volume)

**Gap:** No orchestrator maps **SP-001** (or any `MANGA_CATALOG_PLAN.md` row) to:

1. Resolved `series_id`, `brand_id`, `genre_id`, `topic`, `teacher_id`, display **series title**  
2. `run_series_setup.py` (or replay) once per series  
3. Loop **`run_manga_chapter.py`** for `chapter_number` 1…N with consistent workspace / nested chapter layout per `resolve_chapter_workspace`  
4. Merge chapter PDFs or page trees into **one volume artifact** (new step: PyMuPDF / pypdf / Pillow)

**Recommendation:** Add `scripts/manga/run_catalog_manga_volume.py` (or equivalent) reading a **small machine manifest** (YAML/JSON) generated from `MANGA_CATALOG_PLAN.md` rows — avoid parsing Markdown in production; generate manifest in CI or one-off script.

### 4.2 Lettering and bubbles

**Gap:** No raster or vector overlay of dialogue; `lettering_spec` is silence bookkeeping only.

**Recommendation:** New stage or post-process: bubble layout JSON + font + `PIL.ImageDraw` / SVG → composite on `final_page_composite` (spec + schema first).

### 4.3 Pearl Prime catalog vs manga

**Gap:** `generate_full_catalog.py` does not emit manga workspaces.

**Recommendation:** If “catalog” must mean **BookSpec**, define explicit **product bridge** spec: BookSpec fields → optional manga spin-off workspace (out of scope until specified).

### 4.4 `MANGA_PIPELINE_ONBOARDING.md` drift

Onboarding §3 references `--image-backend fixture-replay`; live CLI uses **`--backend replay`** and **`--replay-map`**. Next doc pass: align examples with `scripts/manga/run_manga_chapter.py --help`.

---

## 5. Environment and credentials (quick reference)

```bash
eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
```

| Use | Variables |
|-----|-----------|
| Local ComfyUI FLUX (primary for bank bulk) | `COMFYUI_URL` |
| RunComfy cloud | `RUNCOMFY_API_KEY`, optional `RUNCOMFY_DEPLOYMENT_ID` |
| Cloudflare Workers AI FLUX | `CLOUDFLARE_ACCOUNT_ID`, **`CLOUDFLARE_AI_API_TOKEN`** (preferred), or `CLOUDFLARE_API_TOKEN` with Workers AI scopes |

---

## 6. Handoff checklist for the next owner

- [ ] Confirm **PR** status for Stillness Press bank + tooling (branch `agent/stillness-press-image-bank-complete-20260416` if still open; merge per governance).
- [ ] Decide **source of truth** for “series title”: extend `run_series_setup.py` / schemas vs manifest file from `MANGA_CATALOG_PLAN.md`.
- [ ] Implement **volume orchestrator** (§4.1) or document manual N-chapter procedure until shipped.
- [ ] Fix **onboarding CLI examples** (§4.4).
- [ ] Optional: **lettering renderer** spec + implementation (§4.2).
- [ ] Re-run **`python3 scripts/manga/stillness_press_image_bank.py audit`** after any manual bank edits; **`index`** subcommand to refresh `image_bank/index.json`.

---

## 7. Related coordination artifacts

| Topic | Path (if present) |
|-------|---------------------|
| Earlier audit snapshots | `artifacts/manga/stillness_press_image_bank_audit.txt`, `stillness_press_image_bank_audit_AFTER.txt` |
| Full catalog artifact README | `artifacts/full_catalog/README.md` |

---

**End of handoff.** Update `docs/DOCS_INDEX.md` task row “AI Manga Dharma system” to link this file for catalog/volume/bank follow-up.
