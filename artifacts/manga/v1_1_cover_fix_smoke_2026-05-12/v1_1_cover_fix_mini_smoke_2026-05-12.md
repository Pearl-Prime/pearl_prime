# V1.1 cover text-regression fix — 3-cell mini-smoke (2026-05-12)

**PROJECT_ID:** PRJ-WORLDWIDE-CATALOG-GO-LIVE-V1 (Phase 2 V1.1 cover-text fix)
**Subsystem:** image_generation (cover prompt authoring)
**Agent:** Pearl_Dev
**Branch:** `agent/v1-1-cover-text-fix-20260512`
**Lineage:** PR #1043 smoke (regression detected) → PR #1025 (Phase 2 P0 negative-prompt fix, didn't reach V1.1 prompt-authoring layer) → this fix.
**Operator memory note:** `feedback_cover_text_overlay_two_stage` — FLUX renders imagery only; PIL composites text downstream.

---

## Two fixes applied

### Fix A — Negative-prompt parity (defense-in-depth)
Added top-level `text_free_negative_prompt` block to
`config/catalog_planning/brand_cover_art_specs.yaml` carrying the same text-suppression
tokens already added at the workflow JSON layer in PR #1025. This makes the rule
explicit at the brand-spec layer where authors compose new prompts.

### Fix B — Strip literal series-title quotation from V1.1 cover positive_prompts
The 3 V1.1 cover prompts in PR #1043's smoke MD quoted English series titles
inline (`series "The Season After"`, `series "Mirror Crush"`, `series "Salary Story Hour"`).
FLUX rendered those quoted strings as embedded typography — exactly what the
two-stage architecture forbids. Below batches replace literal title quotation
with **emotional-throughline + composition** description only. Title content moves
to the downstream PIL typography overlay stage (per cover_identity_system.yaml).

---

## Machine-readable batches (consumed by `scripts/image_generation/batch_runner.py::load_plan`)

```batch
batch_id: smoke_v11_cover_fix_healing_ground_ebook_en
brand_id: healing_ground_healing
series_id: the_season_after
locale: en-US
dispatch_path: auto
workflow_template: flux_txt2img_manga.json
asset_type: kdp_cover
positive_prompt: josei healing ebook cover illustration, single bare branch with one new green leaf against muted dawn sky, soft watercolor wash, vertical 1080x1920, generous upper negative space, palette muted ochre and slate grey, contemplative atmosphere, minimal composition
negative_prompt: text, letters, words, watermark, signature, typography, logo, caption, title text, embedded title, lettering, calligraphy, signage, captions, subtitles, font glyphs, latin alphabet typography, blurry, oversaturated, religious iconography, busy background, melodrama, horror cues, photorealistic faces
sequence: 1
```

```batch
batch_id: smoke_v11_cover_fix_career_lift_ebook_en
brand_id: career_lift_workplace
series_id: salary_story_hour
locale: en-US
dispatch_path: auto
workflow_template: flux_txt2img_manga.json
asset_type: kdp_cover
positive_prompt: josei workplace ebook cover, peer-disclosure cohort scene, professional josei figure mid-conversation across small cafe table, notebook open showing only abstract numeric ledger marks (no letters), competence-and-boundaries register without girlboss caricature, palette warm beige and ink, vertical 1080x1920, generous upper negative space for typography
negative_prompt: text, letters, words, watermark, signature, typography, logo, caption, title text, embedded title, lettering, calligraphy, signage, captions, subtitles, font glyphs, latin alphabet typography, blurry, oversaturated, corporate stock-photo cliche, photorealistic faces, busy background, sexualized framing
sequence: 2
```

```batch
batch_id: smoke_v11_cover_fix_confidence_core_ebook_en
brand_id: confidence_core_romance
series_id: mirror_crush
locale: en-US
dispatch_path: auto
workflow_template: flux_txt2img_manga.json
asset_type: kdp_cover
positive_prompt: shojo romance ebook cover, single shojo protagonist looking softly at her reflection in a hallway window with crush silhouette out of focus behind, blush-lighting palette warm rose and cream, consent-forward romance register, vertical 1080x1920, generous upper negative space for typography, no coercion or possessive cues
negative_prompt: text, letters, words, watermark, signature, typography, logo, caption, title text, embedded title, lettering, calligraphy, signage, captions, subtitles, font glyphs, latin alphabet typography, blurry, oversaturated, sexualized minors, photorealistic faces, busy background, possessive iconography, jealousy cues
sequence: 3
```

---

## Diff vs PR #1043 smoke prompts (per cell)

| Cell | What changed |
|---|---|
| `healing_ground_ebook_en` | Removed `series "The Season After"` literal quotation. Replaced with descriptive `four-season grief arc, ... integrated remembrance not instant closure`. Negative prompt expanded with PR #1025-parity text-suppression block. |
| `career_lift_ebook_en` | Removed `series "Salary Story Hour"` literal quotation. Replaced with descriptive `peer-disclosure cohort scene`. Notebook content now `abstract numeric ledger marks (no letters)` to suppress text-rendering temptation that produced "AMIE" fragment. Negative prompt expanded. |
| `confidence_core_ebook_en` | Removed `series "Mirror Crush"` literal quotation AND removed `(self-image arc, crush as mirror for self-trust not completion fantasy)` parenthetical English prose. Negative prompt expanded. |

---

## Execution status

This branch contains the **deterministic source-of-truth fix** (corrected prompts +
brand-spec authoring rules + parity negative-prompt block). Actual FLUX render
firing on Pearl Star requires SSH access from the operator workstation; the
re-fire and OCR pass-gate are documented in the QA artifact at
`artifacts/qa/v1_1_cover_text_fix_2026-05-12.md`.

The string-level deterministic gate (literal series-title strings absent from
all 3 V1.1 cover positive_prompts) is verified in the same QA artifact.
