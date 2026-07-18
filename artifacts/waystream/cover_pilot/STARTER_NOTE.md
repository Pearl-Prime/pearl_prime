# Waystream Cover Pilot — Starter Note (pick up here)

**Status (2026-06-20):** the per-author **FLUX image-pool** cover look is PROVEN and
operator-approved. The next session implements the **full varied template system**
(operator spec in §3). Everything below is on disk in this folder + Pearl Star is live.

---

## §1 What's in this folder (resume from these)

| File | What |
|---|---|
| `compose_cover.py` | The pilot compositor — **ONE** template (full-bleed FLUX image + dark scrim + Georgia serif title + italic subtitle + topic symbol + `BOOK N · SERIES` band + `AUTHOR · WAYSTREAM SANCTUARY` byline). Extend this into a LIBRARY. |
| `gen_pools.py` | The Pearl Star **FLUX-schnell pool generator** (PROVEN). Reuses `scripts/publish/render_imagery_for_template.submit_to_comfyui`. |
| `pilot_contact_sheet.png` | The approved look — Lena Frost (3 anxiety) vs Theo Castellan (3 boundaries). |
| `sample_flux_pool_image.png` | A raw schnell pool image (navy/cream dawn horizon). |
| `../author_pools/lena_frost/` (8) | Pilot pool — navy→cream dawn-horizon vibe, sky-blue accent. |
| `../author_pools/theo_castellan/` (8) | Pilot pool — charcoal/amber arch vibe, terracotta accent. |

## §2 Proven FLUX recipe (Pearl Star, no cloud)

```python
import os; os.environ["COMFYUI_URL"]="http://100.92.68.74:8188"   # Pearl Star ComfyUI, HTTP 200
from scripts.publish.render_imagery_for_template import submit_to_comfyui, ImageryPlan
plan = ImageryPlan(book_id="x", full_book_id="x", genre="abstract", width=1024, height=1280,
    aspect=0.8, positive_prompt="<author vibe>, no text, no people", negative_prompt="text, words, people, frame",
    output_path=Path(...), type_dominant=False)
img_bytes = submit_to_comfyui(plan, comfyui_url=os.environ["COMFYUI_URL"], config="schnell", seed=<i>)
```
- **`config="schnell"` ONLY** — `flux1-schnell-fp8.safetensors` is on Pearl Star + license-clean. **flux1-dev is BANNED.**
- ~45s/image. 20 authors × ~15 ≈ 300 images ≈ ~3–4 hrs unattended.
- Vary `seed` per pool image; vary the prompt per author (their signature vibe).

## §3 Operator spec — the redesign to build (implement ALL)

1. **Layout template LIBRARY (variation across 37 brands):** full-bleed image (pilot) · center-image-SMALL (inset over gradient/solid) · center-image-LARGE · gradient-only (the old #1760 style) · framed/bordered · title-in-a-box · top/bottom color bands. Each brand gets its OWN template family + font pairing + palette (brands must NOT share fonts/look — a brand is its own publishing house).
2. **Per-author template WITHIN a brand (the big one):** each author gets a DISTINCT variant — picture size, frame vs none, title/subtitle box vs open, gradient vs full-bleed, symbol style/placement, type treatment. 800 books across ~12–20 authors must read as that many distinct author lines, not one template. Deterministic per `author_id`.
3. **Intelligent per-topic SYMBOL vocabulary:** analyze ALL ~15 topics; design a motif system per topic from primitives (lines, dots, arcs, slashes) in VARIED combinations.
   - **HIGH CONTRAST mandatory** — the pilot's light-blue mark blended into the background and was nearly invisible. Fix: strong contrast (light-on-dark / dark-on-light / saturated accent).
   - **VARIATION:** pattern of N elements (1,4,5,7…); symbol COUNT can track book number (bk1=1, bk2=2…); different arrangements per book. Across 800 books: NO repeated pattern — generative + topic-coherent + unique.
4. **KEEP (operator confirmed happy):** the per-author FLUX pool, the `BOOK N · SERIES` band, brand fonts, and the title structure — full title `"The Alarm Is Lying: <engine-angle suffix>"` + subtitle `"A Real Talk Guide to <keyword> for <persona>"`. Do NOT change title/subtitle logic.
5. **Mix it up** — frames, boxes, picture sizes, gradients — so it never reads as one template.

## §4 Read first (ground every choice — do NOT reinvent)

- `artifacts/research/cover_quality_and_differentiation_framework_2026-05-03.md` — the 4-layer brand→author→series→book system + §0 craft ("logo not illustration", thumbnail focal clarity, 2–3 colors).
- `artifacts/research/cover_design_intelligence_gap_2026-05-04.md`, `kdp_bestseller_cover_analysis_2026-05-02.md`, `bestseller_titles_seo_covers_research.md` (Series Cover System §642).
- `config/publishing/cover_identity_system.yaml` — machine contract (§1 brand / §2 author / §3 series / §4 book). Waystream is NOT yet a brand card here — add it.
- `scripts/publish/render_kdp_cover.py` + `abstract_cover_art.py` — current renderer; the #1760 gradient+symbol path = keep as ONE template option.
- Catalog: `artifacts/waystream/waystream_800book_catalog_plan.csv` (800 books). Authors: `config/author_registry.yaml` (brand_id `way_stream_sanctuary`, 20 pens). Memory: `project_waystream_catalog_v2`.

## §5 Constraints

- GPU = Pearl Star ComfyUI only, FLUX **schnell** (no cloud, flux1-dev BANNED). Composite = deterministic PIL.
- Plumbing-commit config/code off `origin/main`. Covers are artifacts — render locally, `open` a contact sheet (don't commit ~800 PNGs).
- **Verify by EYEBALL** (contact sheets); the operator judges the look. Don't claim a look you haven't viewed.

## §6 Acceptance

A contact sheet across multiple authors × topics × books where: (a) each author has a visibly distinct template + vibe, (b) each topic has a distinct high-contrast symbol vocabulary, (c) no two books share a pattern, (d) series name + book number on every cover, (e) it reads as a real multi-author, multi-brand publishing house — not one template fill.
