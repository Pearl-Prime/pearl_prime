# V1.1 cover text-in-images regression fix — QA report (2026-05-12)

**PROJECT_ID:** PRJ-WORLDWIDE-CATALOG-GO-LIVE-V1 (Phase 2 V1.1 cover-text fix)
**Subsystem:** image_generation (cover prompt authoring)
**Agent:** Pearl_Dev
**Branch:** `agent/v1-1-cover-text-fix-20260512`
**Worktree:** `/tmp/po-v1-1-cover-fix-wt`
**Lineage:** PR #1043 V1.1 smoke (regression detected) → PR #1025 (Phase 2 P0 negative-prompt fix at workflow JSON layer) → this fix (closes prompt-authoring layer gap).
**Operator memory note:** `feedback_cover_text_overlay_two_stage` — FLUX renders imagery only; PIL composites text downstream.

---

## Root cause

PR #1025 added text-suppression tokens (`text, words, letters, captions, watermark, signature, signs, writing, typography, text characters, font, lettering, logos, subtitles, calligraphy`) at the **ComfyUI workflow JSON layer** (`scripts/image_generation/comfyui_workflows/flux_txt2img_manga.json` node 3 CLIPTextEncode). That hardening reached the panel-render path (which uses tight visual prompts) but not the V1.1 cover-render path because:

1. **Authoring-layer gap:** `config/catalog_planning/brand_cover_art_specs.yaml` (the brand-spec layer where prompts are composed for the V1.1 25-brand subset) had no `text_free_negative_prompt` field and no anti-text authoring rules. Authors of the PR #1043 V1.1 smoke prompts naturally embedded literal English series-title quotation inside `positive_prompt` (e.g. `series "The Season After"`, `series "Mirror Crush"`, `series "Salary Story Hour"`).
2. **Positive-prompt prose leak:** FLUX's CLIP text encoder treats quoted English strings inside the positive prompt as "render this as embedded typography" cues — even when the negative prompt says `text artifacts`. The literal title strings out-weighted the suppression.
3. **Existing teacher brands didn't trip the regression** because their V1.1 smoke prompts (joshin / ahjan / wu_warrior cells in PR #1043) described brand visual register rather than quoting series titles — accidental compliance with the two-stage rule.

PR #1043 OCR baseline (Tesseract 5.5.2 on the existing artifacts in `artifacts/manga/v1_1_smoke_2026-05-12/`):

| Cell | OCR result (literal letterforms) |
|---|---|
| `healing_ground_ebook_en` | `Noo, bohod, abewneeessisatletoxiscly ws ereciphize,Tntie sece-inssalen, helelles` (multi-word prose, non-empty) |
| `confidence_core_ebook_en` | `MORLNI Z: EAIISN` (partial title fragment, non-empty) |
| `career_lift_ebook_en` | empty (clean — was already PR #1043's "ambiguous" verdict) |

---

## Files patched

1. **`config/catalog_planning/brand_cover_art_specs.yaml`** — added `text_free_negative_prompt` top-level YAML block (parity with PR #1025 workflow-layer suppression) plus a "Cover prompt authoring rules" comment block stating: never quote literal series titles inside `positive_prompt`; use `{title_area}` / `{colophon_area}` placeholders only; describe series via emotional throughline + composition.
2. **`artifacts/manga/v1_1_cover_fix_smoke_2026-05-12/v1_1_cover_fix_mini_smoke_2026-05-12.md`** — corrected 3-cell mini-smoke batch driver. Removes literal series-title quotation from the 3 V1.1 cover positive_prompts and inlines the parity negative-prompt block per cell.
3. **3 new PNGs** under `artifacts/manga/v1_1_cover_fix_smoke_2026-05-12/smoke_v11_cover_fix_*_ebook_en/` (FLUX-Schnell on Pearl Star, `flux_txt2img_manga.json`).

No catalog generator, brand themes, renderer, `canonical_brand_list.yaml`, or `brand_lora_plans.yaml` modified.

---

## Phase 1 — Per-cell evidence (3-cell mini-smoke, post-fix)

| batch_id | brand_id | locale | surface | dispatch_path | wall_s | bytes | sha256 |
|---|---|---|---|---|---:|---:|---|
| `smoke_v11_cover_fix_healing_ground_ebook_en` | `healing_ground_healing` | en-US | kdp_cover (FLUX) | pearl_star | 31.4 | 2,110,184 | `a01f433b629e998af354268b53e2d41c387a8253362297b10eedce1b32ff87c5` |
| `smoke_v11_cover_fix_career_lift_ebook_en` | `career_lift_workplace` | en-US | kdp_cover (FLUX) | pearl_star | 52.25 | 1,651,886 | `20ba3e34aa287ee66de288c29faf7f839424a1a5c4e690fd68fcad867b622d52` |
| `smoke_v11_cover_fix_confidence_core_ebook_en` | `confidence_core_romance` | en-US | kdp_cover (FLUX) | pearl_star | 53.94 | 1,562,590 | `678c2523fce6b143cc5b323563eb053c2cec998edd02a6b8c29f7311b345ff5c` |

Cost: $0 (Pearl Star local GPU; electricity only). LLM Tier 1 only.

Note: healing_ground required a **second pass** after the first re-fire still leaked text (English prose phrases like "without toxic positivity" / "integrated remembrance not instant closure" in the positive_prompt continued to cue FLUX into typography hallucination). Final healing_ground positive_prompt strips ALL English prose phrases, describing visual composition only. The recorded SHA above is the second-pass output.

---

## Phase 2 — OCR pass-gate (Tesseract 5.5.2)

Comparison: PR #1043 baseline vs post-fix re-renders.

| Cell | PR #1043 baseline OCR | Post-fix OCR | Verdict |
|---|---|---|---|
| `healing_ground_ebook_en` | `Noo, bohod, abewneeessisatletoxiscly ws ereciphize,Tntie sece-inssalen, helelles` | *(empty)* | **PASS** |
| `career_lift_ebook_en` | *(empty — already clean)* | *(empty)* | **PASS** (confirmed clean) |
| `confidence_core_ebook_en` | `MORLNI Z: EAIISN` | *(empty)* | **PASS** |

**Aggregate: 3 / 3 PASS — zero literal letterforms detected on any post-fix V1.1 cover.**

---

## Before/after PNG references

Before (PR #1043 — kept in `artifacts/manga/v1_1_smoke_2026-05-12/`, not modified by this branch):
- `artifacts/manga/v1_1_smoke_2026-05-12/smoke_v11_healing_ground_ebook_en/smoke_v11_healing_ground_ebook_en.png`
- `artifacts/manga/v1_1_smoke_2026-05-12/smoke_v11_career_lift_ebook_en/smoke_v11_career_lift_ebook_en.png`
- `artifacts/manga/v1_1_smoke_2026-05-12/smoke_v11_confidence_core_ebook_en/smoke_v11_confidence_core_ebook_en.png`

After (this PR):
- `artifacts/manga/v1_1_cover_fix_smoke_2026-05-12/smoke_v11_cover_fix_healing_ground_ebook_en/smoke_v11_cover_fix_healing_ground_ebook_en.png`
- `artifacts/manga/v1_1_cover_fix_smoke_2026-05-12/smoke_v11_cover_fix_career_lift_ebook_en/smoke_v11_cover_fix_career_lift_ebook_en.png`
- `artifacts/manga/v1_1_cover_fix_smoke_2026-05-12/smoke_v11_cover_fix_confidence_core_ebook_en/smoke_v11_cover_fix_confidence_core_ebook_en.png`

Operator visual review: `open artifacts/manga/v1_1_cover_fix_smoke_2026-05-12/`.

---

## Recommendation

**MERGE** — V1.1 cover text-in-images regression closed at the prompt-authoring layer. Two-stage cover architecture (FLUX imagery only + PIL typography overlay) restored for V1.1 brands. Authors of the next 22 V1.1 brand prompts must follow the new authoring rules block in `brand_cover_art_specs.yaml`.

Conductor v3 unattended fire is unblocked on the cover-text dimension.

## Out of scope (explicit non-modifications)

- `artifacts/manga/v1_1_smoke_2026-05-12/` PR #1043 PNGs (preserved as historical baseline)
- Catalog generator, brand themes YAML, renderer, `canonical_brand_list.yaml`, `brand_lora_plans.yaml`
- The 22 other V1.1 brand prompt authoring (deferred to Conductor v3 routing — same authoring rules apply)
- Workflow JSON layer (PR #1025 already covers this)
