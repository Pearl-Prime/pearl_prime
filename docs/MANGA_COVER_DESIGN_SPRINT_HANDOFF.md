# Manga Cover Design System — Sprint Handoff

**Sprint type:** Research + Design + Scaffold (no implementation)
**Branch:** `agent/manga-cover-design-research-20260418`
**PR:** [#497](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/497)
**Commits:** 3 (`0e14c4f224` → `07568aab6d` → `21764bc9c0`)
**Total:** 21 new files, 20,484 lines
**Status:** All validation clean. PR open, awaiting operator review.

---

## What Was Built

A complete knowledge base and programmatic design system for generating
manga book covers across 12 global markets. Ten parallel workstreams ran
simultaneously. No cover generation implementation — this sprint is
research + spec + scaffold only.

---

## File Map

### Research Documents

| File | Lines | What's inside |
|------|-------|---------------|
| `artifacts/research/manga_cover_design/01_japan_by_genre.md` | 1,831 | 11 genres × ASCII layout diagrams, hex color palettes, typography pairings, 5–8 character poses each, background treatment rules, Vol.1 vs later-volume conventions, anti-patterns for FLUX negative prompts. Deep Junji Ito sub-section. |
| `artifacts/research/manga_cover_design/02_japan_publisher_house_styles.md` | 855 | 7 publishers (Shūeisha, Kodansha, Shogakukan, Kadokawa, Square Enix, Hakusensha, Enterbrain). For each: logo/imprint badge, spine color-coding, title typography, back cover layout, inner jacket convention, paper stock, sub-imprint identities. Jump Comics stamp system. Tankōbon production specs with spine width formula. |
| `artifacts/research/manga_cover_design/03_global_markets.md` | 1,377 | 11 non-Japan markets across 4 tiers. Per market: trim sizes (mm), typography conventions, color tendencies, spine/back cover/barcode conventions, digital storefronts, localization patterns. Attack on Titan cross-market case study tracing 8 markets. Master localization checklist. Publisher ecosystem maps. |
| `artifacts/research/manga_cover_design/04_typography_system.md` | 1,851 | 7 scripts (JP, EN/Latin, Traditional Chinese, Simplified Chinese, Korean, Arabic, Thai). Fude/mincho/gothic/maru-gothic/logotype categories. Tategumi Pillow code. Furigana size ratios. Volume number conventions by publisher. 46+ font recommendations, all OFL-verified. 10 typographic pairing recipes. FLUX prompt text-reservation formulations. |
| `artifacts/research/manga_cover_design/09_bestseller_cover_analysis.md` | 1,993 | 30+ bestselling series across JP (Oricon 2024–25), US (ICv2), France (GfK). Composition type distribution, 6 color clusters, title placement data, thumbnail optimization rules. 25 ranked design rules. Anti-pattern hall of fame (8 cases where violating the rules succeeded). Spine-mural frequency analysis. |

### Implementation Specs

| File | Lines | What's inside |
|------|-------|---------------|
| `specs/manga_cover_flux_workflows.md` | 1,908 | Full FLUX prompt templates for all 11 genres (positive + negative + params). Layout-directive vocabulary for composition control. ControlNet (OpenPose/Depth/Canny) integration with strength calibration tables. IP-Adapter for series visual continuity. 16GB VRAM budget analysis for Pearl Star — every node combination. Two-pass workflow recommendation. Pillow compositing code (gradient overlay, title stroke, volume badge, logo, spine strip extraction, mural composition). Negative prompt library per genre + per-market regulatory addendums. |
| `specs/manga_cover_uniqueness_engine.md` | 1,345 | 4-layer selection architecture (Brand → Series → Volume → Market). SHA-256 deterministic seed with per-layer offsets to prevent cross-layer correlation. Anti-repetition guardrails: protagonist run ≤3, no consecutive pose repeat, temperature run ≤2, mood beat arc validation. Minimum bank sizes per layer for 50-volume series. Full Stillness Press Vol.1–5 selection trace (JP and US market divergence). |
| `specs/manga_cover_full_assembly.md` | 956 | Front/spine/back/jacket flap dimensions for all 12 markets. Spine width formula (page count × paper thickness). Wrap canvas geometry formulas (bleed, safe area, assembly order). Back cover zone layout with word-count targets per market. Barcode placement by market (Brazil upper-right exception noted). JP spine mural design workflow. Production handoff checklist. |
| `specs/manga_cover_regulatory_compliance.md` | 928 | 13 jurisdictions. France Loi 1949 orange warning band (Pantone 151C, min 15mm, exact placement). Germany BzKJ indexing triggers. Australia RC abort logic (pipeline must halt, not just rate). Brazil CLASSIND circle badge with mandatory R$ price. Canada s.163.1 hard prohibition. 14-content-type compliance matrix across all markets. Per-market badge specs (shape, CMYK, text, dimensions). |
| `specs/manga_cover_pipeline_integration.md` | 1,271 | DAG position: after final panel render, before PDF/CBZ/EPUB packaging. Full input/output schema. Complete function signatures with docstrings for `generate_front_cover()`, `generate_back_cover()`, `generate_spine()`, `assemble_full_wrap()`, `render_digital_cover()`. CLI flags for `run_manga_pipeline.py` and `weekly_manga_rollout.py`. GitHub Actions workflow spec for `manga-cover-generate.yml` (pearl-star-gpu runner). Dependency checklist: what must exist before first cover can generate. |

### Config & Schema Files

| File | Lines | What's inside |
|------|-------|---------------|
| `config/source_of_truth/manga_cover_layers/schema.yaml` | 1,067 | Master schema for all 4 selection layers. Machine-readable field type definitions. All 12 market configurations (trim/bleed/safe-area/rating-system/barcode-position). Anti-repetition rule parameters. Seed computation offsets. Bank size minimums. |
| `config/source_of_truth/manga_cover_layers/brand_signatures/stillness_press.yaml` | 463 | **Fully-worked reference example.** 6-color palette with rationale notes. Composition family: `environmental`. Mood register: `restrained`. Typography family: Klee One / M PLUS 1 / Lato. 22-item taboo element list with contextual exceptions. Enso logo lockup. Series defaults (character occupies ≤30% frame). Cover evolution principle: "walking through a year." Matte-only production notes. 6 cited reference series. |
| `config/source_of_truth/manga_cover_layers/brand_signatures/stub_template.yaml` | 330 | Operator fill-in template for new brands. Every required field present with inline instructions. Pre-commit validation note: reject any file still containing the literal string `"TODO"`. |
| `fonts/manga_covers/FONT_REGISTRY.yaml` | 828 | 56 fonts across 13 subcategories. Extends `fonts/manga/FONT_REGISTRY.yaml`. All OFL-1.1 or equivalent commercial-use-clean. Every entry: id, name, source, URL, license, weights, scripts, use_cases, pillow_compatible, flux_rendering, notes. 11 genre pairings block. |

### ComfyUI Workflows

| File | Nodes | What's inside |
|------|-------|---------------|
| `config/comfyui_workflows/manga_covers/iyashikei_cover.json` | 9 | UNETLoader (fp8), DualCLIPLoader (T5+CLIP-L), VAELoader, CLIPTextEncodeFlux (full iyashikei positive + negative prompt embedded), EmptyLatentImage (1024×1600), KSampler (dpmpp_2m/karras, CFG 6.0, steps 38), VAEDecode, SaveImage. Runnable on Pearl Star as-is. |
| `config/comfyui_workflows/manga_covers/shonen_cover.json` | 12 | Same core chain + ControlNetLoader, LoadImage (pose map input), ControlNetApplyAdvanced (OpenPose, strength 0.65). Runtime bypass note for when no character sheet exists. euler_ancestral sampler, CFG 7.0, steps 35. |

### Python Scaffold Modules (`phoenix_v4/manga/covers/`)

All modules pass `py_compile`. Stubs only — no implementation.

| Module | Lines | What's inside |
|--------|-------|---------------|
| `__init__.py` | 181 | Architecture docstring. Data flow description. Full public API and exception class re-exports. |
| `cover_selector.py` | 716 | `LayeredCoverSelector` class. `select_cover_params()`. `_compute_seed()` via SHA-256. `_select_layer()` deterministic RNG. YAML loading with caches. Prompt builder. ControlNet config builder. Genre registries (generation params, base prompts, negative prompts, market addendums). `CoverParams`, `TrimSize`, `ControlNetConfig`, `TypographyConfig` dataclasses. |
| `cover_generator.py` | 893 | `CoverGenerator` class. `generate_front_cover()`, `generate_back_cover()`. `_call_flux_api()` (RunComfy API stub). `_poll_until_complete()`. `_download_image()`. `_load_comfyui_workflow()`. `_patch_workflow()`. `_single_pass_generate()`, `_two_pass_generate()`. `_upscale()` (Real-ESRGAN with PIL Lanczos fallback). `validate_cover_set()`, `list_generated_covers()`, `get_spine_width_mm()`. All exception classes. |
| `cover_assembler.py` | 654 | `CoverAssembler` class. `overlay_typography_front()`. `apply_title_zone_gradient()`. `_render_title_text()`. `_render_volume_badge()` (circle/rectangle/star styles). `_composite_publisher_logo()`. `assemble_full_wrap()`. `generate_spine()`. `extract_spine_strip()`. `compose_spine_mural()`. `render_digital_cover()`. `_apply_market_adaptations()`. |
| `market_adapters.py` | 722 | `MarketAdapter` ABC. 12 concrete subclasses (JP, US, FR, DE, IT, BR, MX, TW, CN, KR, ES, AU). `get_trim_size()`, `get_typography_config()`, `get_market_adapter()`, `list_market_specs()`. DE and CN adapters override `apply_regulatory_constraints()`. |

---

## What Covers Each Genre

| Genre | Research (WS1) | FLUX Prompts (WS5) | Font Pairing (WS4) | Bestseller Analysis (WS9) |
|-------|---------------|--------------------|--------------------|--------------------------|
| Shōnen | ✅ | ✅ | ✅ | ✅ One Piece, MHA, Demon Slayer, JJK |
| Shōjo | ✅ | ✅ | ✅ | ✅ Fruits Basket, Sailor Moon |
| Seinen | ✅ | ✅ | ✅ | ✅ Vinland Saga, Berserk, Monster |
| Josei | ✅ | ✅ | ✅ | — |
| Kodomomuke | ✅ | ✅ | ✅ | — |
| Isekai | ✅ | ✅ | ✅ | — |
| Horror | ✅ + Ito deep | ✅ | ✅ | ✅ Chainsaw Man (dark adjacent) |
| Sports | ✅ | ✅ | ✅ | ✅ Blue Lock |
| Iyashikei | ✅ | ✅ + full ComfyUI JSON | ✅ | ✅ Dungeon Meshi, Frieren |
| BL/GL | ✅ | ✅ | ✅ | — |
| Mecha | ✅ | ✅ | ✅ | — |

---

## What Covers Each Market

| Market | Trim (mm) | Rating System | Barcode Position | Researched |
|--------|-----------|--------------|-----------------|-----------|
| JP | 112×175 | Publisher self | Lower-right | ✅ Deep |
| US | 139.7×215.9 | Publisher self (Viz T/T+/OT/M) | Lower-right | ✅ |
| FR | 148×210 | Loi 1949 | Lower-right | ✅ |
| DE | 148×210 | BzKJ indexing | Lower-right | ✅ |
| IT | 148×210 | AGCOM/self | Lower-right | ✅ |
| ES | 148×210 | Self | Lower-right | ✅ |
| BR | 150×210 | CLASSIND | **Upper-right** | ✅ |
| MX | 139.7×215.9 | Self | Lower-right | ✅ |
| TW | 128×182 | 普/護/輔/限 + shrinkwrap | Lower-right | ✅ |
| CN | 128×182 | NPPA review | Lower-right | ✅ |
| KR | 128×182 | Youth Protection Act | Lower-right | ✅ |
| AU | 139.7×215.9 | ACB (RC = abort) | Lower-right | ✅ |

---

## What's NOT in This Sprint

These are explicitly deferred to the implementation sprint:

- `cover_generator.py` actual FLUX call logic (stubs exist, RunComfy endpoint not wired)
- `cover_assembler.py` actual PIL compositing (stubs exist)
- `market_adapters.py` actual constraint enforcement (stubs exist)
- `.github/workflows/manga-cover-generate.yml` (specced in `manga_cover_pipeline_integration.md`, not committed — no pearl-star-gpu runner configured yet)
- Brand signatures for brands 2–12 (stub_template.yaml is ready; fill per brand when prioritized)
- Series signatures (created per-series by operator, not pre-populated)
- Volume variation banks (generated at series-launch time, not this sprint)

---

## Blockers Before First Real Cover

Three things must exist before `cover_generator.py` can produce output:

1. **✅ Stillness Press brand signature** — done in this sprint (`brand_signatures/stillness_press.yaml`)
2. **⬜ Series identity YAML** — operator creates for first test series using `stub_template.yaml` as starting point; save to `config/source_of_truth/manga_cover_layers/series_signatures/{series_id}.yaml`
3. **⬜ Character sheet PNG** — protagonist character sheet at `image_bank/{series_id}/characters/{character_id}_sheet.png` (prior forensic analysis Workstream 5 — check status)

Once (2) and (3) exist, the implementation sprint can begin.

---

## Next Sprint Scope (Implementation)

**Goal:** Generate first real Stillness Press Vol.1 cover.

**Tasks:**
1. Implement `cover_generator.py` — wire `_call_flux_api()` to RunComfy endpoint using existing `RUNCOMFY_API_KEY` from Keychain
2. Implement `cover_assembler.py` — wire `_render_title_text()` via Pillow using font from FONT_REGISTRY.yaml (Klee One for Stillness Press)
3. Implement `market_adapters.py` JP adapter — trim 112×175, spine formula, no rating badge
4. Add `--generate-cover` flag to `scripts/run_manga_pipeline.py`
5. Create `manga-cover-generate.yml` GitHub Actions workflow (pearl-star-gpu runner)
6. Create series identity YAML for first test series
7. Run end-to-end: `generate_front_cover(series_id, volume=1, market="JP")` → inspect output
8. Iterate on FLUX prompt template until cover meets brand spec

**Estimated sprint size:** Medium (implement against specs that already exist; no new design decisions needed)

---

## Key Design Decisions Encoded in Specs

These were settled during this sprint and should not be re-litigated:

| Decision | Where |
|----------|-------|
| Deterministic seed: `sha256(brand:series:volume:market)[:8]` | `specs/manga_cover_uniqueness_engine.md` §3 |
| VRAM constraint: IP-Adapter OR ControlNet per pass, not both simultaneously | `specs/manga_cover_flux_workflows.md` §3 |
| Stillness Press: character ≤30% frame, environment leads | `config/source_of_truth/manga_cover_layers/brand_signatures/stillness_press.yaml` |
| Brazil barcode = upper-right (not lower-right like all other markets) | `specs/manga_cover_full_assembly.md` + `specs/manga_cover_regulatory_compliance.md` |
| Australia RC = pipeline abort, not rating badge | `specs/manga_cover_regulatory_compliance.md` §AU |
| ComfyUI workflows: FLUX fp8 UNETLoader (not checkpoint loader) | Both workflow JSONs |
| Font for Stillness Press title: Klee One (OFL, weight 400 only) | `fonts/manga_covers/FONT_REGISTRY.yaml` + `brand_signatures/stillness_press.yaml` |
| Series cover evolution: "walking through a year" seasonal arc | `brand_signatures/stillness_press.yaml` |

---

## Validation Status

```
yaml.safe_load:  schema.yaml ✅  stillness_press.yaml ✅  stub_template.yaml ✅  FONT_REGISTRY.yaml ✅
json.tool:       iyashikei_cover.json ✅  shonen_cover.json ✅
py_compile:      __init__.py ✅  cover_selector.py ✅  cover_generator.py ✅  cover_assembler.py ✅  market_adapters.py ✅
push_guard:      ✅
preflight_push:  ✅
```

---

*Generated by Pearl_Research — Claude Code session, 2026-04-18*
*PR #497 | Branch: agent/manga-cover-design-research-20260418 | HEAD: 21764bc9c0*
