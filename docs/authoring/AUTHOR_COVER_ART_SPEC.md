# AUTHOR COVER ART SPEC

## Version 1.0.0

---

## Purpose

Every author gets a **signature visual style** for all their audiobook covers.
The system is model-first: 4 intentionally different prompts per author produce
4 base images via an external image model. Python handles rendering: resize,
text overlay, contrast validation, and dual-format export. No effects pipeline.

---

## Architecture

```
One-time (per author):
  setup_author_cover_identity.py → cover_art_blueprint.yaml
  compose_prompts.py             → 4 prompt strings
  Author runs image model        → 4 base images saved to base/

Per book:
  generate_cover.py              → select slot by hash
                                 → resize 2400×2400
                                 → overlay title + author
                                 → contrast check (WCAG AA)
                                 → export PNG + JPEG (≤2MB)

QC:
  cover_qc.py                   → pHash collision guard
                                 → manifest update
```

---

## 1. Blueprint Schema

File: `assets/authors/{author_id}/cover_art/cover_art_blueprint.yaml`

### Required fields

| Field | Type | Description |
|---|---|---|
| `author_id` | string | Must match author_registry |
| `brand_id` | string | Must exist in brand_archetype_registry |
| `cover_pipeline_version` | string | Semver; tracks code version for reproducibility |
| `prompt_fills` | object | Author's visual signature fills (see below) |
| `base_images` | object | Filenames for 4 slots + `images_ready` boolean |
| `typography` | object | Font config + slot text zone overrides |
| `compliance_metadata` | object | Audit trail (see below) |

### prompt_fills (required keys)

| Key | Used in | Example |
|---|---|---|
| `object_metaphor` | slot_1 | "single lotus flower floating on still dark water" |
| `viewpoint` | slot_1 | "overhead view" |
| `environment_scene` | slot_2 | "mountain temple path at dawn with soft mist" |
| `lighting_mood` | slot_2, slot_4 | "golden hour soft diffused light" |
| `texture_type` | slot_3 | "flowing ink wash" |
| `organic_shape` | slot_3 | "organic curves" |
| `motion_word` | slot_3 | "breath" |
| `mood_word` | slot_3 | "meditative" |
| `human_element` | slot_4 | "silhouette of person meditating, back to viewer" |
| `setting_hint` | slot_4 | "overlooking misty valley" |
| `emotion_word` | slot_4 | "peace" |
| `color_desc` | all | "soft gold and deep indigo" |
| `color_palette_id` | all | "warm_gold_indigo" |
| `style_keyword` | all | "editorial photography" |

### compliance_metadata (required keys)

| Key | Type | Description |
|---|---|---|
| `source_prompts` | list | Composed prompts (written by compose_prompts.py --save) |
| `image_model` | string | e.g. "midjourney-v6.1", "dall-e-3", "flux-1.1-pro" |
| `image_model_version` | string | Specific version string |
| `generation_date` | date | ISO date when base images were generated |
| `human_reviewed` | boolean | Set true after visual QA |
| `license_status` | string | "ai_generated_original" |

---

## 2. Prompt Templates

File: `config/cover_art/prompt_templates.yaml`

### 4 Slots

| Slot | Name | Composition | Default text zone |
|---|---|---|---|
| 1 | symbolic | Single central metaphor, clean background | upper_third |
| 2 | environmental | Landscape/atmosphere evoking transformation | upper_third |
| 3 | abstract | Textures, gradients, organic shapes | center |
| 4 | human | Silhouette/gesture, warmth/connection | upper_quarter |

### Mandatory rules

- Every composed prompt MUST end with `mandatory_suffix` (no text/letters/words).
- Every composed prompt MUST include `format_suffix` (square 1:1, high resolution).
- Unfilled template placeholders trigger a WARNING in compose_prompts.py.

### Color palettes

Defined in `prompt_templates.yaml` under `color_palettes`. Each palette provides:
- `color_desc` — natural language for prompt insertion
- `hex_primary`, `hex_secondary` — brand colors
- `text_color_light`, `text_color_dark` — contrast-safe text options

---

## 3. Text Zones

Slot-aware safe zones prevent title from overlapping key visual elements.

| Zone name | Top % | Bottom % | Use case |
|---|---|---|---|
| `upper_quarter` | 2% | 25% | Human/silhouette (avoid face) |
| `upper_third` | 2% | 33% | Symbolic/environmental (sky/negative space) |
| `center` | 20% | 80% | Abstract (no focal point) |
| `lower_third` | 67% | 95% | Reserved for future use |

Blueprint can override per-slot via `typography.slot_text_zone_overrides`.

---

## 4. Contrast Validation

Before export, `generate_cover.py` samples the average luminance of the text zone
region and picks light or dark text color from the palette.

- **Target**: WCAG AA 4.5:1 contrast ratio
- **Method**: Sample center 80% width of the text zone; compute relative luminance;
  test both `text_color_light` and `text_color_dark` from palette
- **Behavior**: If neither color passes 4.5:1, picks the better one and prints WARNING.
  Cover still exports (some images may have complex backgrounds where no solid color
  achieves 4.5:1 everywhere).

---

## 5. Deterministic Slot Selection

```
slot_index = SHA256(author_id + ":" + book_id) % 4
```

- Same `(author_id, book_id)` always produces the same cover
- Different books by same author cycle through different slots
- `--force-slot` CLI flag allows manual override

---

## 6. Export

| Format | Purpose | Spec |
|---|---|---|
| PNG | Archival, Google Play upload | Full quality, optimize=True |
| JPEG | Voices by INaudio upload | ≤2MB; quality steps from 92→75 by 3 |

Output path: `artifacts/covers/{author_id}/{author_id}_{book_id}_cover_2400x2400.{ext}`

### JPEG quality stepping

Start at quality 92. Check file size. If >2MB, step down by 3.
Floor at quality 75. If still >2MB at 75, export anyway with warning.

---

## 7. pHash Collision Guard

| Check | Threshold | Action |
|---|---|---|
| Same brand | Hamming distance ≥ 12 | FAIL if < 12 |
| Same author | Hamming distance ≥ 8 | WARN if < 8 |

Uses simplified average-hash (16×16 grayscale). For production at scale,
upgrade to `imagehash` library's DCT-based pHash.

### Inline check (generate_cover.py)

When `--brand` is passed, generator checks pHash against manifest before export.
If collision detected, bumps to next slot: `(slot + 1) % 4`.
If all 4 slots collide, fails with "author needs new base images".

### Manifest (cover_qc.py)

Brand-level manifest: `artifacts/covers/{brand_id}_cover_manifest.yaml`

Records per cover: `phash`, `slot`, `path`, `author_id`, `book_id`,
`generated` timestamp, `pipeline_version`.

---

## 8. Platform Requirements

### Google Play Books (audiobooks)
- **Cover**: 2400×2400 recommended (minimum 1024)
- **Format**: JPEG or PNG
- **Aspect ratio**: 1:1 (square)
- **Content**: Title and author on cover recommended
- **Restrictions**: No 3D mockups, no letterboxing

### Voices by INaudio (formerly Findaway Voices)
- **Cover**: 2400×2400 recommended
- **Format**: JPEG preferred (≤2MB for upload speed)
- **Content**: Title and author on cover
- **QA**: Visual inspection; rejects "auto-generated" or template-stamped look
- **Note**: Accepts ElevenLabs AI-narrated content for wide distribution
- **Distribution**: Spotify, Audible, Apple Books, 35+ retailers

### Ximalaya / Himalaya (Phase 2)
- **Cover**: Square; discovery UI weights cover heavily in category browsing
- **Audience**: Chinese urban professionals, 25-39, high spending power
- **Typography conventions**: Bolder, larger title text than Western self-help;
  often banner-backed text treatment for legibility
- **Locale variant**: CJK font mapping, horizontal/vertical text, safe zone
  adjustments, text_treatment (floating / banner_backed / pill_container)

---

## 9. CLI Reference

### setup_author_cover_identity.py
```
python setup_author_cover_identity.py --author <id> --brand <brand_id> [--palette <palette_id>]
```
Creates directory structure and blueprint stub.

### compose_prompts.py
```
python compose_prompts.py --author <id>          # print 4 prompts
python compose_prompts.py --author <id> --save   # save to blueprint
python compose_prompts.py --author <id> --json   # JSON output
```
Composes 4 prompt strings from templates + blueprint fills.

### generate_cover.py
```
python generate_cover.py --author <id> --book-id <id> --title "Title" --author-name "Name"
python generate_cover.py --author <id> --book-id <id> --title "Title" --author-name "Name" --subtitle "Subtitle"
python generate_cover.py --author <id> --book-id <id> --title "Title" --author-name "Name" --force-slot 2
python generate_cover.py --author <id> --book-id <id> --title "Title" --author-name "Name" --out ./custom/
```

### cover_qc.py
```
python cover_qc.py --check <path> --brand <brand_id>
python cover_qc.py --check <path> --brand <brand_id> --register --author <id> --book-id <id> --slot <name>
python cover_qc.py --audit --brand <brand_id>
```

---

## 10. Implementation Phases

### Phase 1 (store-ready)
1. Blueprint schema + directory layout
2. Prompt templates with 4 slots + color palettes
3. `setup_author_cover_identity.py`
4. `compose_prompts.py`
5. `generate_cover.py` (resize + text overlay + contrast + PNG/JPEG)
6. `cover_qc.py` (pHash + manifest)

### Phase 2 (scale + international)
1. Locale variants (CJK typography, vertical text, safe zones)
2. Brand-level cover manifest index
3. Publish bundle integration with export pipeline
4. Optional: light tint/adjustment from brand palette
5. Optional: batch generation CLI

---

## 11. Uniqueness and Spam Protection

| Layer | Mechanism |
|---|---|
| Brand | style_pool enforced unique by CI (no two brands share) |
| Author | Unique 4 base images + unique prompt_fills per author |
| Book | Deterministic slot selection from book_id hash |
| QC | pHash Hamming ≥ 12 within brand; warn within author |
| Audit | Cover manifest indexes all generated covers for dedup |

---

## Appendix: Onboarding Workflow

```
1. Add author to config/author_registry.yaml
2. Run: python setup_author_cover_identity.py --author <id> --brand <brand_id> --palette <palette>
3. Edit blueprint: fill in prompt_fills with author's visual signature
4. Run: python compose_prompts.py --author <id> --save
5. Paste 4 prompts into image model (Midjourney / DALL-E / Flux)
6. Save 4 outputs to assets/authors/<id>/cover_art/base/
7. Set images_ready: true in blueprint
8. Set compliance_metadata: image_model, generation_date
9. Per book: python generate_cover.py --author <id> --book-id <id> --title "..." --author-name "..."
10. QC: python cover_qc.py --check <path> --brand <brand_id> --register ...
```
