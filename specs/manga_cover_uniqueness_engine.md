# Manga Cover Uniqueness Engine — Comprehensive Specification

**Spec ID:** MANGA-COVER-UNIQUENESS-v1.0  
**Status:** Canonical  
**Owner:** Pearl_Architect  
**Date:** 2026-04-18  
**Related specs:** `specs/manga_cover_full_assembly.md`, `config/source_of_truth/manga_cover_layers/schema.yaml`

---

## Table of Contents

1. Problem Statement
2. Four-Layer Architecture
3. Deterministic Hash Selection
4. Anti-Repetition Guardrails
5. Volume Variation Bank Sizes
6. Worked Example: Stillness Press Vol. 1–5
7. Implementation Notes
8. Validation Protocol
9. Edge Cases and Failure Modes
10. Extension Points

---

## 1. Problem Statement

### 1.1 The Same-ness Failure

Naive cover generation — feeding a prompt template like "manga cover for Volume N of Series X" into an image model — produces covers that converge toward a single aesthetic attractor. The reasons are structural:

**Prompt convergence.** A template like `"anime-style cover illustration, female protagonist, action pose, vibrant colors, Vol. {n}"` has only one free variable. The model's prior distribution collapses all volumes toward the same statistical center. Volumes 1 through 50 look like the same cover with different numeral typography.

**Model memorization.** Large image models trained on manga corpora have strong priors about what "manga cover" looks like. Without explicit counter-pressure, every generated cover regresses toward the aggregate training distribution — which is itself dominated by shonen action manga from the early 2000s (Naruto, Bleach, One Piece) due to their disproportionate online presence.

**Missing brand constraint.** Without a brand signature enforcing palette, typography family, and composition rules, the model cannot distinguish between "Stillness Press pastoral iyashikei Vol. 3" and "Apex Comics dark action Vol. 3." The brand's visual identity is undefined noise.

**Missing series coherence.** Without a series signature enforcing a recurring motif, a specific color accent, and a composition variant, consecutive volumes of the same series read as unrelated books. Readers cannot identify a series by browsing a shelf.

**Missing volume variation.** Without tracked anti-repetition rules, the pose, mood, and character focal choice for Volume 5 may be identical to Volume 4. When this happens at scale — 50 volumes across 100 series — the production output reads as machine-stamped rather than curated.

**Missing market intelligence.** A cover generated for the JP tankōbon market uses typography conventions, trim proportions, and rating placement that are wrong for the US trade paperback market. Without market adaptation, localized editions either look foreign or require full manual rework.

### 1.2 The Combinatorial Challenge

The Phoenix Omega system must produce unique, on-brand, commercially viable covers at the following scale:

```
12 brands
  × up to 100 series per brand
    × up to 50 volumes per series
      × 12 markets per volume
= up to 720,000 unique cover assets
```

These are not cosmetic variations. Each cover must satisfy four simultaneous constraints:

1. **On-brand:** Unmistakably from the publishing brand. A reader who has seen one Stillness Press cover should recognize another immediately.
2. **Series-coherent:** Clearly part of a series. The same recurring motif, color accent emphasis, and composition variant run through every volume. Spines form a visual mural across volumes (JP convention).
3. **Volume-distinct:** Volume 1 and Volume 30 of the same series must read as different books covering different story territory. Character focal, mood beat, setting, and background treatment must vary meaningfully.
4. **Market-appropriate:** Typography direction, title placement, rating badges, barcode position, and trim proportions are correct for the target market without manual intervention.

Achieving all four simultaneously, deterministically, at 720,000-asset scale, is the problem this engine solves.

### 1.3 Why Determinism Matters

Non-deterministic cover generation creates production chaos:

- A cover regenerated without saving the seed looks different from the approved version.
- QA cannot verify that "Vol. 3, JP" and "Vol. 3, US" share correct series-level consistency.
- Brand compliance audits cannot be automated.
- Recovery from corrupted assets requires full manual recreation.

The uniqueness engine uses deterministic hash-based seed selection so that any cover can be reconstructed from its four keys (brand_id, series_id, volume, market) without storing the full asset. The seed is the asset's identity.

### 1.4 Scope of This Spec

This spec covers:
- The four-layer architecture for cover parameter selection
- The hash function and seed derivation method
- Anti-repetition guardrails for consecutive volumes
- Minimum bank sizes for sustainable 50-volume series
- A fully worked example for Stillness Press, Volumes 1–5, JP and US markets

This spec does not cover:
- Image generation prompt construction (see `specs/VISUAL_AGENT_SPEC.md`)
- Cover assembly and print-ready output (see `specs/manga_cover_full_assembly.md`)
- Typography rendering and lettering (see `specs/LETTERING_AGENT_SPEC.md`)

---

## 2. Four-Layer Architecture

The uniqueness engine applies four sequential layers of constraint and selection to produce a complete cover brief. Layers are ordered from most immutable (brand) to most variable (market). Each layer narrows the solution space; it does not fully determine the output.

```
┌─────────────────────────────────────────────────────────┐
│  LAYER 1: Brand Signature                               │
│  Immutable. Set once. Never changes.                    │
│  Defines: palette, typography, composition, mood        │
├─────────────────────────────────────────────────────────┤
│  LAYER 2: Series Signature                              │
│  Immutable per series. Set at series creation.          │
│  Defines: accent color, recurring motif, variant        │
├─────────────────────────────────────────────────────────┤
│  LAYER 3: Volume Variation                              │
│  Unique per volume. Computed from seed.                 │
│  Defines: pose, character focal, setting, mood beat     │
├─────────────────────────────────────────────────────────┤
│  LAYER 4: Market Adaptation                             │
│  Per-market rules. Applied last. Non-destructive.       │
│  Defines: typography swap, trim, rating badge, barcode  │
└─────────────────────────────────────────────────────────┘
```

The output of these four layers is a **cover brief** — a structured document that fully specifies a cover without being an image. The image generation system consumes the cover brief.

### 2.1 Layer 1 — Brand Signature (Immutable Per Brand)

The brand signature defines the visual DNA of a publishing imprint. It is set once by a brand administrator and must never be changed without a formal brand audit process. Changes to a brand signature invalidate all existing series signatures and require a full series re-verification pass.

**Purpose:** Ensure that any cover from this brand is immediately recognizable as belonging to it, regardless of series or volume.

**Governed by:** `config/source_of_truth/manga_cover_layers/brand_signatures/{brand_id}.yaml`

#### 2.1.1 Required Fields

**`brand_id`** (string, slug format)
- Unique identifier for the brand. Lowercase, hyphenated.
- Example: `stillness-press`, `apex-comics`, `neon-frontier`
- Never changes after creation. Used as primary key in all seed computations.

**`display_name`** (string)
- Human-readable brand name as it appears in editorial contexts.
- Example: `"Stillness Press"`, `"Apex Comics"`

**`primary_palette`** (list of 5–8 color objects)
- The canonical color set for this brand. Every cover must draw exclusively from this palette plus any market-mandated additions (e.g., regulatory red for age ratings).
- Each color object has: `name`, `hex`, `role`, and optional `notes`.
- Roles: `background` | `primary` | `accent` | `secondary` | `dark` | `light`
- The palette must include at least one dark value (for title text) and one light value (for title-safe zones).
- Palette is defined in the brand signature and cannot be overridden at any lower layer. Series signatures may *emphasize* a palette color but cannot introduce colors outside the palette.

**`typography_family`** (object)
- Specifies the font cluster the brand uses. All covers from this brand use these fonts exclusively.
- Fields: `display_font_id`, `body_font_id`, `accent_font_id`
- Font IDs reference the shared font registry at `config/source_of_truth/fonts/`
- Market adaptations may substitute script-appropriate variants (e.g., a Japanese font replacing the Latin display font) but must preserve weight and proportion equivalence.

**`composition_family`** (enum)
- The structural composition approach that defines how elements are arranged on the cover.
- Values: `portrait` | `environmental` | `symbolic` | `action` | `ensemble`
- `portrait`: character fills most of the frame; face or figure is the subject
- `environmental`: setting dominates; character is present as a presence, not the focus
- `symbolic`: object, texture, or abstract element carries the cover; character may be absent
- `action`: dynamic pose and motion; energy lines acceptable
- `ensemble`: multiple characters; group arrangement is the design problem
- A brand commits to one composition family. Series signatures select a variant within that family.

**`mood_register`** (enum)
- The tonal baseline that all covers from this brand must maintain.
- Values: `restrained` | `energetic` | `melancholic` | `epic` | `playful` | `sinister`
- Mood register governs: color saturation ceiling, acceptable pose energy, whether speed lines or effects are permitted, whether dark backgrounds are permitted.
- Volume-level mood beats modulate within the register; they cannot escape it.

**`taboo_elements`** (list of strings)
- Visual elements that must never appear on any cover from this brand, regardless of series or volume.
- Examples: `speed_lines`, `dark_horror_imagery`, `military_or_weapon_imagery`, `isekai_status_windows`
- These are enforced as prompt-level negative constraints when the cover brief is rendered.
- Taboo elements override everything. No volume variation or market adaptation may reintroduce a taboo element.

**`logo_lockup`** (object)
- Specifies where and how the brand logo appears.
- Fields: `position`, `front_cover_position`, `spine_position`, `size_relative`, `color_variant`, `notes`
- `size_relative`: fraction of cover width. Typical range: 0.05–0.12
- Some brands (Stillness Press) do not place logo on the front cover. This is a valid and intentional choice encoded here.

#### 2.1.2 Optional Fields

**`series_defaults`** (object)
- Default values that series signatures inherit unless overridden.
- Allows brand-level tendencies (e.g., "all series default to environmental_midground composition") without requiring each series to re-specify.

**`cover_evolution_principle`** (string)
- A prose statement of the intended evolution arc across volumes in a series.
- Not machine-executed. Used as design guidance when constructing volume variation banks.
- Example: `"Across a series, covers should feel like walking through a year. Vol.1 spring. The character grows within the same world."`

**`production_notes`** (object)
- Physical production preferences: paper stock, lamination, spot UV, embossing.
- These are passed to print production but do not affect the digital cover brief.

**`example_references`** (list of objects)
- Real-world published manga that exemplify this brand's visual register.
- Each reference has: `title`, `publisher`, `notes`
- Used as training examples when onboarding new visual agents to this brand.

### 2.2 Layer 2 — Series Signature (Immutable Per Series)

The series signature defines the visual identity of a specific manga series within the constraints established by its brand. It is set at series creation and should not change mid-series. Mid-series changes to a series signature create visible discontinuity on shelf.

**Purpose:** Ensure that all volumes of a series read as a unified set. A reader who picks up Volume 8 should immediately recognize it as part of the same series as Volumes 1–7.

**Governed by:** `config/source_of_truth/manga_cover_layers/series_signatures/{series_id}.yaml`

#### 2.2.1 Required Fields

**`series_id`** (string, slug format)
- Unique identifier for this series. Globally unique across all brands.
- Convention: `{brand_id}--{series_slug}`. Example: `stillness-press--wandering-harvest`

**`brand_id`** (string)
- Foreign key to the brand signature. Must match an existing brand_id in `brand_signatures/`.

**`color_accent_index`** (integer)
- Index into the brand's `primary_palette` list identifying which palette color this series emphasizes.
- Every volume in this series will weight this color prominently in its palette distribution.
- A different series within the same brand may emphasize a different palette color, creating visual differentiation between series on the same shelf.

**`typography_weight`** (enum)
- `light` | `regular` | `bold`
- Applies within the brand's display font family. All volumes in this series use this weight for the series title.
- Different series within a brand may use different weights to distinguish their visual register (a light-weight series feels more delicate; a bold-weight series more assertive), as long as the brand's title_weight constraint permits variance.

**`composition_variant`** (string)
- A specific variant within the brand's `composition_family`.
- If brand uses `environmental`, valid variants might be: `environmental_foreground`, `environmental_midground`, `environmental_aerial`, `environmental_intimate`
- The variant is specified in the brand's composition variant bank in the brand signature YAML under `composition_variants`.
- All volumes in this series use the same composition variant. This creates series coherence: the reader unconsciously recognizes the spatial grammar of the series.

**`recurring_motif`** (object)
- A visual element that appears in every volume of this series.
- The motif may scale, transform, or move position slightly volume-to-volume, but must be recognizable as the same element.
- Fields: `name`, `description`, `placement_default`, `color_override`
- Examples: a specific flower species, a lantern shape, a kanji character rendered in ink, a specific bird silhouette, a particular cloud formation
- The recurring motif is the series' visual signature to the reader. It is what fans notice and discuss.

**`protagonist_design_ref`** (string, file path)
- Path to the canonical character sheet for the series protagonist.
- Used as a consistency reference when generating the protagonist in volume variations.
- Format: `assets/characters/{series_id}/protagonist.yaml` or an image path.

#### 2.2.2 Optional Fields

**`location_bank`** (list of location objects)
- The pool of settings from which volume variations draw their `setting_variant_index`.
- If not specified here, the system uses a generic setting bank for the genre.
- Series-specific location banks are strongly preferred — they create world coherence across volumes.
- Minimum 8 locations for a 50-volume series (see Section 5).

**`tone_arc`** (list of strings)
- The intended mood arc across the series, by volume range.
- Example: `["hopeful", "tense", "tense", "triumphant", "reflective", "hopeful"]`
- When present, the system uses this arc to constrain `mood_beat` selection in volume variations rather than pure hash-based selection.

**`secondary_characters`** (list)
- Characters eligible to appear as character focal choices in volume variations.
- Each character has: `name`, `design_ref`, `first_eligible_volume`, `last_eligible_volume`

### 2.3 Layer 3 — Volume Variation (Unique Per Volume)

The volume variation layer makes each cover distinct within the constraints established by Layers 1 and 2. All selections at this layer are derived deterministically from the volume's hash seed. Anti-repetition guardrails (Section 4) apply after the initial seed-based selection.

**Purpose:** Ensure that consecutive volumes of the same series are visually distinct, that the series feels dynamic and progressing, and that no two volumes within a series read as "the same cover."

**Governed by:** `config/source_of_truth/manga_cover_layers/volume_variations/{series_id}/vol_{volume_number:04d}.yaml`
(These files are generated by the engine; they are not manually authored.)

#### 2.3.1 Required Fields

**`series_id`** (string)
- Foreign key to the series signature.

**`volume_number`** (integer)
- The volume number. 1-indexed. Must be positive.

**`character_focal`** (enum)
- Who is on the cover.
- Values: `protagonist` | `antagonist` | `supporting_primary` | `supporting_secondary` | `ensemble` | `no_character`
- `no_character`: environment or symbolic object is the subject. Valid only for brands with `composition_family: environmental` or `symbolic`.
- Protagonist may not appear more than 3 consecutive volumes without a forced switch (see Section 4.1).

**`pose_variant_index`** (integer)
- Index into the genre's pose library for the character focal's character type.
- The pose library is organized by: `{genre}_{character_type}_poses.yaml`
- No same pose index in two consecutive volumes (see Section 4.2).

**`setting_variant_index`** (integer)
- Index into the series' location bank (from series signature) or generic genre location bank.
- Selects which setting/background environment appears on this cover.

**`color_temperature`** (enum)
- `warm` | `neutral` | `cool`
- Modulates the color palette distribution within the brand palette and series accent.
- Warm: more weight on warm tones (reds, oranges, yellows, warm greens)
- Cool: more weight on cool tones (blues, blue-greens, cool grays)
- Neutral: balanced distribution
- Alternates across consecutive volumes (see Section 4.3).

**`mood_beat`** (enum)
- `hopeful` | `tense` | `reflective` | `triumphant` | `ominous`
- The emotional tone the cover communicates. Constrains lighting direction, character expression, and palette saturation.
- `hopeful`: open composition, light from above or ahead, neutral-to-warm temperature, open expression
- `tense`: compressed composition, side lighting or dramatic shadows, cooler temperature, guarded expression
- `reflective`: distance and space, even or diffuse lighting, neutral temperature, contemplative expression or no character
- `triumphant`: expanded composition, high-key lighting, warm temperature, upward-facing pose
- `ominous`: reduced safe area, low-key lighting, cool-to-dark temperature, obscured or downward expression

**`background_treatment`** (enum)
- `blown_out` | `pattern` | `environment` | `solid_color` | `gradient`
- `blown_out`: highly saturated or overexposed background; character silhouetted or high-contrast. Not permitted for restrained or melancholic mood registers.
- `pattern`: repeating graphic element fills background. Must use palette colors only.
- `environment`: rendered scene background. Most common for environmental composition brands.
- `solid_color`: single flat color from brand palette. Often used for symbolic composition.
- `gradient`: two-color gradient within palette. Safe default; never violates brand constraints.

**`focal_element`** (enum)
- `character_dominant` | `setting_dominant` | `object_symbolic`
- Determines the visual hierarchy: what the viewer's eye should travel to first.
- `character_dominant`: character occupies 40–70% of the cover area
- `setting_dominant`: character occupies 10–30% of cover area; setting leads
- `object_symbolic`: a non-character object (weapon, flower, book, lantern) occupies the primary focal zone

#### 2.3.2 Derived Fields (Computed, Not Stored)

These fields are computed at brief-generation time from the required fields above and the series/brand signatures. They are included in the cover brief but not stored in the volume variation YAML.

**`effective_palette`**: Brand palette filtered and weighted by series accent and volume color temperature.

**`title_color`**: Selected from effective palette based on background treatment contrast requirements.

**`motif_position`**: Derived from setting_variant_index; varies slightly each volume to prevent motif rigidity.

**`lighting_direction`**: Derived from mood_beat. See mood_beat definitions above.

### 2.4 Layer 4 — Market Adaptation (Per-Market Rules)

Market adaptation applies localization rules to the cover brief produced by Layers 1–3. It does not change the core visual design; it adjusts presentation for regional conventions, regulatory requirements, and physical production standards.

**Purpose:** Ensure that localized editions of a volume are print-ready and compliant in their target market without requiring manual rework.

**Governed by:** `config/source_of_truth/manga_cover_layers/schema.yaml` (market section)

#### 2.4.1 Typography Swap

Each market requires typography in the appropriate script. The brand's Latin/Roman display font is replaced by a script-appropriate equivalent that preserves weight and proportion.

Mapping principles:
- The substitute font must match the `typography_weight` of the series signature.
- It must be in the brand's font family register or an approved script extension.
- Proportional spacing may differ; title placement zone heights must be recalculated.

Script mappings for Stillness Press (example):
- `ja`: Klee One → Klee One (native JP) / M PLUS 1 for body
- `zh-Hant`: Klee One → Noto Serif CJK TC
- `zh-Hans`: Klee One → Noto Serif CJK SC
- `ko`: Klee One → Noto Serif KR
- `en`: Klee One (unchanged)
- `fr`, `de`, `es`, `it`, `pt`: Klee One with locale-specific glyph coverage

#### 2.4.2 Title Placement Reflow

Title placement conventions vary by market:

| Market | Title Position Default | Reading Direction | Notes |
|--------|----------------------|-------------------|-------|
| JP | Upper-right vertical | Right-to-left | Series title vertical on right edge |
| JP (modern) | Upper area horizontal | Left-to-right | Contemporary convention |
| US | Upper-left horizontal | Left-to-right | |
| FR | Upper horizontal | Left-to-right | French subtitle (translated) below |
| DE | Upper horizontal | Left-to-right | Mandatory age rating adjacent |
| KR | Upper horizontal | Left-to-right | |
| CN | Upper-right vertical or horizontal | — | Publisher preference |
| TW | Upper-right area | Right-to-left | Following JP convention |

Title placement reflow must be computed within the front cover safe area for the target trim size. See `specs/manga_cover_full_assembly.md` for safe area dimensions.

#### 2.4.3 Rating Badge

Every market has a mandatory or conventional age rating system. The cover brief includes a `rating_badge` field specifying:
- `rating_value`: the age rating string (e.g., `"G"`, `"PG-13"`, `"16+"`, `"成年向"`)
- `badge_style`: `numeric_circle` | `letter_badge` | `text_box` | `icon`
- `placement`: where on the cover the badge goes
- `size_mm`: bounding box in millimeters

Rating systems by market:

| Market | System | Authority | Placement Convention |
|--------|--------|-----------|---------------------|
| JP | Publisher self-rating | Publisher | Back cover, varies |
| US | CBLDF / publisher self | Publisher | Front cover lower-right or back cover |
| FR | Loi du 16 juillet 1949 | Commission | Back cover, required |
| DE | Unterhaltungssoftware Selbstkontrolle / BPjM | BPjM | Back cover, prominently |
| IT | AGCOM self-regulation | Publisher | Back cover |
| BR | CLASSIND | Secretaria Nacional | Front and back cover, upper-right |
| MX | Publisher self-rating | Publisher | Back cover |
| TW | TGPC (Game Prohibited Committee — content rules apply) | TGPC | Back cover |
| CN | NPPA content regulation | NPPA | Back cover |
| KR | KMRB | Korea Media Rating Board | Back cover |
| ES | Publisher self-rating | Publisher | Back cover |
| AU | ACB (Australian Classification Board) | ACB | Back cover |

#### 2.4.4 Trim Size Adjustment

Each market has a standard trim size. The cover brief specifies all dimensions for the target trim. Bleed and safe area are computed from the trim size.

Trim sizes and their implications for cover composition:

| Market | Trim W×H (mm) | Aspect Ratio | Notes |
|--------|--------------|--------------|-------|
| JP Tankōbon | 112×175 | 0.640 | Tall, narrow. Portrait compositions work best. |
| JP Bunkoban | 105×148 | 0.709 | A6 format. Even narrower compositions. |
| US Trade 5×7.5 | 127×190.5 | 0.667 | Similar to JP tankōbon. |
| US Standard | 139.7×215.9 | 0.647 | Most common US manga size. |
| FR/DE/IT | 148×210 | 0.705 | A5 format. Slightly wider than US. |
| BR | 150×210 | 0.714 | Similar to A5. |
| MX | 139.7×215.9 | 0.647 | US sizing used. |
| TW | 112×175 | 0.640 | JP sizing used. |
| CN | 112×175 | 0.640 | JP sizing used. |
| KR | 112×175 | 0.640 | JP sizing used. |

Composition validation: A cover brief designed for one trim size must be validated for safe area compliance when adapted to a different trim size. The composition variant (from Layer 2) anchors the proportional layout; trim adaptation scales within it.

#### 2.4.5 Spine Convention

| Market | Convention | Description |
|--------|-----------|-------------|
| JP | Mural | Spines of consecutive volumes form a continuous image. Series name vertical top-to-bottom, vol. number at bottom. |
| US | Text-only | Series name horizontal or vertical, volume number, publisher logo. No mural. |
| FR | Integrated | Spine color matches cover dominant; small mural optional but not standard. |
| DE | Integrated | Same as FR. |
| Other | Text-only | Default unless market-specific convention overrides. |

The mural convention for JP spines has implications for cover brief generation: the spine background color and any spine artwork must be planned as a sequence across all volumes, not independently.

#### 2.4.6 Regulatory Marks

Some markets require additional mandatory marks beyond the age rating badge:

- **JP**: Imprint name in specified typography; no global regulatory mark required.
- **DE**: `Altersfreigabe` badge (BPjM) at specified size; `§131 StGB` notice if content restricted.
- **FR**: `Loi 49-956` notice; age classification mark; for 18+ content, required diagonal stripe on front cover.
- **BR**: CLASSIND rating icon (mandatory both front and back per Brazilian law).
- **AU**: ACB consumer advice text ("Contains mild themes") adjacent to rating badge.
- **CN**: Publishing license number (`书号`) on back cover; required.
- **KR**: KMRB approval number on back cover.

---

## 3. Deterministic Hash Selection

### 3.1 The Seed Function

Every cover has exactly one seed, derived deterministically from its four identity keys.

```python
import hashlib

def compute_cover_seed(
    brand_id: str,
    series_id: str,
    volume: int,
    market: str
) -> int:
    """
    Compute a 32-bit deterministic seed for a cover.
    
    Args:
        brand_id:  slug, e.g. "stillness-press"
        series_id: slug, e.g. "stillness-press--wandering-harvest"
        volume:    1-indexed integer
        market:    ISO market code, e.g. "JP", "US", "FR"
    
    Returns:
        32-bit unsigned integer seed
    """
    key = f"{brand_id}:{series_id}:{volume:04d}:{market}"
    h = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return int(h[:8], 16)  # first 8 hex digits = 32-bit seed
```

Properties of this seed function:
- **Deterministic:** Same inputs always produce the same seed.
- **Collision-resistant:** SHA-256 collision probability for 720,000 assets is negligible (~10^-65).
- **Independent:** Seeds for different volumes/markets are uncorrelated. Knowledge of Vol. 3's seed gives no information about Vol. 4's seed.
- **Compact:** The full seed is a 32-bit integer (max ~4.3 billion). Sufficient for all selection operations.
- **Auditable:** The seed can be recomputed from the cover's identity keys at any time for verification.

### 3.2 Layer-Offset Selection

Each layer uses the seed with a different offset to prevent cross-layer correlation. Without offsets, layers would systematically correlate: the brand that selects accent color index 3 would also tend to select pose index 3, mood beat index 3, etc.

```python
# Offset constants — one per selectable field
OFFSET_CHARACTER_FOCAL      = 0
OFFSET_POSE_VARIANT         = 1000
OFFSET_SETTING_VARIANT      = 2000
OFFSET_COLOR_TEMPERATURE    = 3000
OFFSET_MOOD_BEAT            = 4000
OFFSET_BACKGROUND_TREATMENT = 5000
OFFSET_FOCAL_ELEMENT        = 6000

def select_from_bank(bank: list, seed: int, offset: int = 0) -> any:
    """
    Select an item from a bank using the seed and an offset.
    
    The offset ensures that each field makes an independent selection
    from the seed's distribution, preventing cross-field correlation.
    
    Args:
        bank:   list of options to select from
        seed:   32-bit cover seed
        offset: field-specific constant offset
    
    Returns:
        Selected item from bank
    """
    return bank[(seed + offset) % len(bank)]
```

### 3.3 Selection Cascade

The full selection cascade for a volume variation:

```python
def compute_volume_variation(
    brand_sig: dict,
    series_sig: dict,
    volume: int,
    market: str
) -> dict:
    """
    Compute the complete volume variation for a cover.
    
    Returns a cover brief dict with all layer selections resolved.
    """
    seed = compute_cover_seed(
        brand_id=brand_sig["brand_id"],
        series_id=series_sig["series_id"],
        volume=volume,
        market=market
    )
    
    # Layer 1 values come from brand_sig directly (no selection needed)
    composition_family = brand_sig["composition_family"]
    mood_register      = brand_sig["mood_register"]
    palette            = brand_sig["primary_palette"]
    typography         = brand_sig["typography_family"]
    
    # Layer 2 values come from series_sig directly (no selection needed)
    accent_color    = palette[series_sig["color_accent_index"]]
    comp_variant    = series_sig["composition_variant"]
    recurring_motif = series_sig["recurring_motif"]
    
    # Layer 3 — hash-based selection from banks
    character_focal_bank     = build_character_focal_bank(series_sig)
    pose_bank                = load_pose_bank(series_sig["genre"], composition_family)
    setting_bank             = series_sig.get("location_bank") or load_genre_location_bank(series_sig["genre"])
    color_temperature_bank   = ["warm", "neutral", "cool"]
    mood_beat_bank           = ["hopeful", "tense", "reflective", "triumphant", "ominous"]
    background_treatment_bank = build_background_bank(brand_sig, composition_family)
    focal_element_bank       = ["character_dominant", "setting_dominant", "object_symbolic"]
    
    raw = {
        "character_focal":      select_from_bank(character_focal_bank,     seed, OFFSET_CHARACTER_FOCAL),
        "pose_variant_index":   select_from_bank(pose_bank,                seed, OFFSET_POSE_VARIANT),
        "setting_variant_index":select_from_bank(setting_bank,             seed, OFFSET_SETTING_VARIANT),
        "color_temperature":    select_from_bank(color_temperature_bank,   seed, OFFSET_COLOR_TEMPERATURE),
        "mood_beat":            select_from_bank(mood_beat_bank,           seed, OFFSET_MOOD_BEAT),
        "background_treatment": select_from_bank(background_treatment_bank,seed, OFFSET_BACKGROUND_TREATMENT),
        "focal_element":        select_from_bank(focal_element_bank,       seed, OFFSET_FOCAL_ELEMENT),
    }
    
    # Apply anti-repetition guardrails (Section 4)
    adjusted = apply_anti_repetition(raw, volume, series_sig)
    
    # Apply market adaptation (Layer 4)
    market_rules = load_market_rules(market)
    cover_brief  = apply_market_adaptation(adjusted, brand_sig, series_sig, market_rules)
    
    return cover_brief
```

### 3.4 Market-Level Seed Divergence

For most fields, the market does not affect Layer 3 selection. The same character focal, pose, setting, and mood beat appear in the JP and US editions of Volume 3. What differs is the presentation layer (typography, trim, badges).

However, for markets where the regulatory or aesthetic requirements are substantially different — for example, a cover element that is permissible in one market but taboo in another — the system may need to force an alternate selection. This is handled by the `market_override` mechanism:

```python
MARKET_OVERRIDES = {
    "CN": {
        # CN regulatory requirements may prohibit certain elements
        "forbidden_focal_elements": ["object_symbolic_weapon"],
        "forbidden_mood_beats": ["ominous"],  # may be flagged as "unhealthy content"
        "required_background_treatment_fallback": "gradient",
    },
    "DE": {
        # BPjM may require content modification
        "forbidden_focal_elements": ["object_symbolic_weapon"],
    }
}

def apply_market_overrides(raw: dict, market: str, seed: int) -> dict:
    """
    Apply market-specific forbidden element overrides.
    When a selection violates a market prohibition, re-select from
    the remaining valid options using the same seed + a market-specific
    secondary offset.
    """
    overrides = MARKET_OVERRIDES.get(market, {})
    result = dict(raw)
    
    if "forbidden_focal_elements" in overrides:
        if result["focal_element"] in overrides["forbidden_focal_elements"]:
            valid_bank = [e for e in FOCAL_ELEMENT_BANK
                         if e not in overrides["forbidden_focal_elements"]]
            result["focal_element"] = select_from_bank(valid_bank, seed, OFFSET_FOCAL_ELEMENT + 9999)
    
    return result
```

---

## 4. Anti-Repetition Guardrails

The hash-based selection system produces statistically distributed choices across volumes. However, statistical distribution does not guarantee perceptual variety. Two adjacent volumes may, by chance, share the same pose index, same mood beat, and same color temperature — producing covers that read as clones.

Anti-repetition guardrails are deterministic adjustments applied after hash selection and before brief finalization. They check the previous volume's variation record and enforce minimum-change rules.

### 4.1 Character Focal: Maximum Consecutive Runs

**Rule:** The protagonist may not appear as `character_focal` for more than 3 consecutive volumes without a forced switch to another focal type.

**Rationale:** Long protagonist runs reduce the perceived variety of covers. Readers who buy in sequence begin to feel all covers are "the same person in a different landscape." Supporting characters and ensemble covers break the visual monotony and communicate that the world is larger than the protagonist.

**Implementation:**

```python
MAX_PROTAGONIST_RUN = 3

def enforce_character_focal_run(
    selected_focal: str,
    volume: int,
    series_history: list[dict]
) -> str:
    """
    Check if protagonist has appeared for MAX_PROTAGONIST_RUN consecutive volumes.
    If so, force switch to next eligible focal type.
    
    Args:
        selected_focal:  hash-selected focal type for this volume
        volume:          current volume number
        series_history:  list of previous volume variation dicts, ordered by volume
    
    Returns:
        Adjusted character_focal string
    """
    if selected_focal != "protagonist":
        return selected_focal
    
    # Count consecutive protagonist run ending at previous volume
    run = 0
    for prev in reversed(series_history[: volume - 1]):
        if prev["character_focal"] == "protagonist":
            run += 1
        else:
            break
    
    if run >= MAX_PROTAGONIST_RUN:
        # Force a non-protagonist focal
        # Use seed with a secondary offset to select the alternative
        alternatives = ["antagonist", "supporting_primary", "supporting_secondary", "ensemble"]
        seed = compute_cover_seed(
            brand_id=series_history[0]["brand_id"],
            series_id=series_history[0]["series_id"],
            volume=volume,
            market=series_history[0]["market"]
        )
        return select_from_bank(alternatives, seed, OFFSET_CHARACTER_FOCAL + 100)
    
    return selected_focal
```

**Exception:** If a series has no named secondary characters and `no_character` is not permitted for the brand's composition family, the maximum protagonist run limit is extended to 5 volumes with a mandatory `ensemble` or `no_character` insertion at the extension point.

### 4.2 Pose Variant: No Same Pose in Consecutive Volumes

**Rule:** The pose_variant_index for Volume N must differ from Volume N-1's pose_variant_index.

**Rationale:** Repeated poses are the most immediately visible sign of mechanical generation. Even if the setting and mood differ, an identical pose across two consecutive covers registers to readers as "the same image."

**Implementation:**

```python
def enforce_pose_no_repeat(
    selected_pose_index: int,
    volume: int,
    series_history: list[dict],
    pose_bank_size: int
) -> int:
    """
    If selected pose index matches previous volume's pose index,
    increment by 1 (mod bank size).
    
    This is a single-step adjustment only. The adjusted pose is still
    deterministically derived from the seed + 1 increment.
    """
    if volume <= 1:
        return selected_pose_index
    
    prev_pose_index = series_history[volume - 2]["pose_variant_index"]
    
    if selected_pose_index == prev_pose_index:
        return (selected_pose_index + 1) % pose_bank_size
    
    return selected_pose_index
```

**Extended rule:** For volumes in the same arc (if series bible defines story arcs), no pose index may repeat within an arc, regardless of whether volumes are consecutive. This requires arc-aware enforcement which reads the story bible if available.

### 4.3 Color Temperature: Directed Alternation

**Rule:** Color temperature alternates in tendency across consecutive volumes. Two consecutive "warm" volumes are permitted if hash selection naturally produces them, but three consecutive identical temperatures are not.

**Rationale:** A series of consistently warm-toned covers loses the visual rhythm that makes a shelf display compelling. The eye expects variation.

**Implementation:**

```python
MAX_TEMPERATURE_RUN = 2

def enforce_color_temperature_alternation(
    selected_temp: str,
    volume: int,
    series_history: list[dict]
) -> str:
    """
    Prevent more than MAX_TEMPERATURE_RUN consecutive volumes
    with identical color temperature.
    
    On forced switch, select from the other two temperature options
    using a secondary seed offset.
    """
    if volume <= 1:
        return selected_temp
    
    run = 0
    for prev in reversed(series_history[: volume - 1]):
        if prev["color_temperature"] == selected_temp:
            run += 1
        else:
            break
    
    if run >= MAX_TEMPERATURE_RUN:
        alternatives = [t for t in ["warm", "neutral", "cool"] if t != selected_temp]
        seed = compute_cover_seed(
            brand_id=series_history[0]["brand_id"],
            series_id=series_history[0]["series_id"],
            volume=volume,
            market=series_history[0]["market"]
        )
        return select_from_bank(alternatives, seed, OFFSET_COLOR_TEMPERATURE + 100)
    
    return selected_temp
```

### 4.4 Mood Beat: Story Bible Validation

If the series signature includes a `tone_arc` field, the mood beat selection is validated against the intended story beat for this volume range.

**Implementation:**

```python
MOOD_BEAT_COMPATIBILITY = {
    # tone_arc value -> compatible mood_beats for cover
    "hopeful":    ["hopeful", "reflective"],
    "tense":      ["tense", "ominous", "reflective"],
    "triumphant": ["triumphant", "hopeful"],
    "dark":       ["ominous", "tense"],
    "resolution": ["reflective", "hopeful", "triumphant"],
}

def validate_mood_beat_against_story_arc(
    selected_mood: str,
    volume: int,
    series_sig: dict,
    seed: int
) -> str:
    """
    If series has a tone_arc, validate the selected mood beat is compatible.
    If not compatible, select the closest valid mood beat.
    """
    tone_arc = series_sig.get("tone_arc")
    if not tone_arc:
        return selected_mood
    
    # Determine which arc segment this volume falls in
    arc_index = (volume - 1) % len(tone_arc)
    intended_tone = tone_arc[arc_index]
    
    compatible = MOOD_BEAT_COMPATIBILITY.get(intended_tone, ["hopeful", "tense", "reflective", "triumphant", "ominous"])
    
    if selected_mood in compatible:
        return selected_mood
    
    # Select from compatible beats
    return select_from_bank(compatible, seed, OFFSET_MOOD_BEAT + 100)
```

### 4.5 Background Treatment: Register Compliance

**Rule:** Background treatments are validated against the brand's mood register. Some treatment types are incompatible with certain mood registers.

```python
REGISTER_TREATMENT_RESTRICTIONS = {
    "restrained": {
        "forbidden": ["blown_out"],
        "preferred": ["environment", "gradient", "solid_color"],
    },
    "energetic": {
        "forbidden": [],
        "preferred": ["blown_out", "pattern", "environment"],
    },
    "melancholic": {
        "forbidden": ["blown_out"],
        "preferred": ["environment", "gradient", "solid_color"],
    },
    "epic": {
        "forbidden": [],
        "preferred": ["environment", "blown_out", "gradient"],
    },
    "playful": {
        "forbidden": [],
        "preferred": ["pattern", "solid_color", "gradient"],
    },
    "sinister": {
        "forbidden": ["blown_out"],
        "preferred": ["solid_color", "gradient", "environment"],
    },
}
```

---

## 5. Volume Variation Bank Sizes

For a 50-volume series to feel non-repetitive, the variation banks used for Layer 3 selection must contain enough distinct options that hash-based selection distributes without creating visible cycles.

### 5.1 Minimum Bank Size Analysis

For a bank of size N, pure hash selection over 50 volumes produces each option approximately 50/N times. The perceptual threshold for "I've seen this before" varies by element type:

| Element | Perceptual Sensitivity | Recurrence Tolerance | Min Bank Size |
|---------|----------------------|---------------------|--------------|
| Pose variant | High — immediately visible | 1 recurrence per 10 volumes | 10 |
| Setting variant | Medium — requires attention | 1 recurrence per 6 volumes | 8 |
| Color temperature | Low — subliminal | 1 run per 3 volumes | 3 |
| Mood beat | Medium — affects reading experience | 1 recurrence per 10 volumes | 5 |
| Background treatment | Medium — structural feel | 1 recurrence per 8 volumes | 6 |
| Focal element | Low — perceived as emphasis | 1 recurrence per 5 volumes | 3 |
| Character focal | Medium — central identity | Run limit enforced separately | 4 |

### 5.2 Pose Variant Bank: Minimum 10

The pose library must contain at least 10 distinct poses per character type per composition family. Poses are defined along axes:

- **Vertical position:** standing / seated / crouching / lying / floating
- **Facing direction:** full front / three-quarter / profile / back / away
- **Arm position:** at side / raised / crossed / extended / reaching
- **Gaze direction:** direct camera / upward / downward / away / closed
- **Movement state:** static / weight shift / mid-motion / extreme motion

For iyashikei / restrained brands, extreme motion is prohibited by the mood register. The effective pose bank for Stillness Press is drawn from: static, weight shift, slow motion. Within those constraints, 10+ distinct poses are readily achievable.

Example pose bank for Stillness Press (environmental, restrained):
1. Standing in field, facing 3/4, gaze distant
2. Seated on rock, profile, gaze downward at water
3. Kneeling in garden, gaze at plant
4. Walking away, back to camera
5. Standing at window, profile, gaze through glass
6. Lying in grass, upward gaze
7. Sitting on step, direct camera gaze
8. Crouching to examine something on ground
9. Standing in rain, face upward
10. Two-figure seated, side by side (ensemble variant)
11. Standing at threshold (doorway/gate), profile
12. Walking toward camera, gaze slightly down

### 5.3 Setting Variant Bank: Minimum 8

The series location bank must contain at least 8 distinct settings. Settings are defined by:
- Primary biome/environment type
- Time of day
- Season
- Weather state
- Interior vs. exterior

For Stillness Press:
1. Rice paddy at dawn, summer
2. Mountain path, autumn, overcast
3. Seaside cliff, afternoon, clear
4. Rural farmhouse interior, winter morning
5. Village market, midday, spring
6. Forest clearing, dusk, misty
7. River bank, afternoon, cloudy
8. Train platform, evening, light rain
9. Rooftop garden, noon, summer
10. Temple steps, early morning, autumn

### 5.4 Mood Beat Bank: Minimum 5

The five mood beats already satisfy this minimum:
- hopeful
- tense
- reflective
- triumphant
- ominous

For brands with constrained mood registers (e.g., `restrained` or `melancholic`), `triumphant` and `ominous` may be rarely or never selected. In these cases, the effective bank shrinks. Guardrail: if effective mood bank (after register filtering) is fewer than 3 options, expand by adding `nuanced_{beat}` variants specific to the brand.

### 5.5 Background Treatment Bank: Minimum 6 Effective Options

Not all 6 background treatments are valid for all brands. The effective bank after register filtering must be at least 3 options. For Stillness Press (restrained), the effective bank is:
- environment (preferred)
- gradient
- solid_color
- pattern (occasional — must use natural patterns: leaf, wood grain, wave)

Note: `blown_out` is forbidden by `restrained` register. `pattern` requires careful brand-palette restriction.

### 5.6 Distribution Over 50 Volumes (Expected)

With a 10-pose bank over 50 volumes, after anti-repetition enforcement:
- Average pose appearances: 5 (each pose appears ~5 times)
- Consecutive-repeat violations before guardrail: ~5 (hash occasionally selects same as previous)
- After guardrail enforcement: 0 consecutive repeats

With an 8-setting bank over 50 volumes:
- Average setting appearances: 6.25 (each setting appears ~6 times)
- Settings feel like "returning to a familiar place" rather than repetition — this is desirable for iyashikei.

---

## 6. Worked Example: Stillness Press Vol. 1–5

### 6.1 Setup

**Brand:** Stillness Press  
**Brand ID:** `stillness-press`  
**Series:** Wandering Harvest (放浪する収穫)  
**Series ID:** `stillness-press--wandering-harvest`  
**Genre:** Iyashikei, rural slice-of-life  
**Composition family:** environmental  
**Mood register:** restrained

Series signature summary:
- `color_accent_index`: 2 (warm_clay, `#C4956A`)
- `typography_weight`: regular
- `composition_variant`: environmental_midground
- `recurring_motif`: single stalk of barley (right edge, lower-third)
- `protagonist_design_ref`: assets/characters/wandering-harvest/protagonist.yaml

Tone arc defined: `["hopeful", "reflective", "tense", "reflective", "triumphant"]`

### 6.2 Seed Computation

```python
# JP market seeds
seeds_jp = {
    vol: compute_cover_seed("stillness-press", "stillness-press--wandering-harvest", vol, "JP")
    for vol in range(1, 6)
}

# US market seeds
seeds_us = {
    vol: compute_cover_seed("stillness-press", "stillness-press--wandering-harvest", vol, "US")
    for vol in range(1, 6)
}
```

Computing manually:

| Volume | Market | Key String | SHA-256 Prefix | Seed (decimal) |
|--------|--------|-----------|----------------|----------------|
| 1 | JP | `stillness-press:stillness-press--wandering-harvest:0001:JP` | (SHA-256[:8]) | 2,847,634,291 |
| 2 | JP | `stillness-press:stillness-press--wandering-harvest:0002:JP` | (SHA-256[:8]) | 1,092,847,563 |
| 3 | JP | `stillness-press:stillness-press--wandering-harvest:0003:JP` | (SHA-256[:8]) | 3,461,029,847 |
| 4 | JP | `stillness-press:stillness-press--wandering-harvest:0004:JP` | (SHA-256[:8]) | 892,374,051 |
| 5 | JP | `stillness-press:stillness-press--wandering-harvest:0005:JP` | (SHA-256[:8]) | 2,134,987,223 |
| 1 | US | `stillness-press:stillness-press--wandering-harvest:0001:US` | (SHA-256[:8]) | 3,892,041,776 |

Note: Exact decimal values are illustrative. The real values are computed by the engine at runtime.

### 6.3 Layer 3 Selection Trace — JP Market, Vol. 1–5

**Banks used:**
- Character focal bank (4 items): `[protagonist, antagonist, supporting_primary, ensemble]`
- Pose bank (12 items): poses 0–11 as listed in Section 5.2
- Setting bank (10 items): settings 0–9 as listed in Section 5.3
- Color temperature bank (3 items): `[warm, neutral, cool]`
- Mood beat bank (5 items): `[hopeful, tense, reflective, triumphant, ominous]`
- Background treatment bank (4 items): `[environment, gradient, solid_color, pattern]` (blown_out forbidden)
- Focal element bank (3 items): `[character_dominant, setting_dominant, object_symbolic]`

**Volume 1 (seed: 2,847,634,291):**

Raw selections before anti-repetition:
- `character_focal`: (2,847,634,291 + 0) % 4 = 3 → `ensemble`
- `pose_variant_index`: (2,847,634,291 + 1000) % 12 = (2,847,635,291) % 12 = 11 → pose #11 (standing at threshold)
- `setting_variant_index`: (2,847,634,291 + 2000) % 10 = 1 → Rice paddy at dawn, summer
- `color_temperature`: (2,847,634,291 + 3000) % 3 = 1 → `neutral`
- `mood_beat`: (2,847,634,291 + 4000) % 5 = 1 → `tense`
- `background_treatment`: (2,847,634,291 + 5000) % 4 = 3 → `pattern`
- `focal_element`: (2,847,634,291 + 6000) % 3 = 1 → `setting_dominant`

Anti-repetition (Vol. 1 — no previous volumes, no adjustments needed):
- No character run to check
- No pose repeat to check
- No temperature run to check

Tone arc validation (Vol. 1 tone: `hopeful`):
- Selected mood_beat: `tense`
- `tense` is NOT compatible with `hopeful` arc
- Force selection from compatible: `[hopeful, reflective]`
- Re-select: (2,847,634,291 + 4000 + 100) % 2 = 1 → `reflective`

Final Vol. 1 selections:
- `character_focal`: ensemble
- `pose_variant`: 11 (standing at threshold — but for ensemble, this adapts to "two figures at threshold")
- `setting`: Rice paddy at dawn, summer
- `color_temperature`: neutral
- `mood_beat`: reflective (adjusted from tense by tone arc validation)
- `background_treatment`: pattern (natural wave pattern — complies with brand)
- `focal_element`: setting_dominant

**Volume 1 Cover Brief Summary:**  
Two figures stand at the edge of a rice paddy at dawn in summer. The setting dominates (setting_dominant). A natural wave pattern fills the background. Neutral color temperature — morning mist tones, neither warm nor cool. Reflective mood: even lighting, diffuse, contemplative. Recurring motif: barley stalk, right edge lower-third. Series accent: warm_clay touches on figures' clothing.

---

**Volume 2 (seed: 1,092,847,563):**

Raw selections:
- `character_focal`: (1,092,847,563 + 0) % 4 = 3 → `ensemble`
- `pose_variant_index`: (1,092,847,563 + 1000) % 12 = 4 → pose #4 (walking away, back to camera)
- `setting_variant_index`: (1,092,847,563 + 2000) % 10 = 5 → Forest clearing, dusk, misty
- `color_temperature`: (1,092,847,563 + 3000) % 3 = 2 → `cool`
- `mood_beat`: (1,092,847,563 + 4000) % 5 = 2 → `reflective`
- `background_treatment`: (1,092,847,563 + 5000) % 4 = 0 → `environment`
- `focal_element`: (1,092,847,563 + 6000) % 3 = 0 → `character_dominant`

Anti-repetition checks:
- Character focal: `ensemble` → Vol. 1 was also `ensemble`. Not protagonist, so no run limit applies. Ensemble ≠ protagonist; allow.
- Pose: index 4 ≠ Vol. 1's index 11. No adjustment.
- Temperature: `cool` ≠ Vol. 1's `neutral`. No run limit triggered.

Tone arc (Vol. 2 tone: `reflective`):
- Selected mood_beat: `reflective` ✓ Compatible with reflective arc.

Final Vol. 2 selections:
- `character_focal`: ensemble
- `pose_variant`: 4 (walking away, back to camera — group walking into forest)
- `setting`: Forest clearing, dusk, misty
- `color_temperature`: cool
- `mood_beat`: reflective
- `background_treatment`: environment
- `focal_element`: character_dominant (figures walking)

**Volume 2 Cover Brief Summary:**  
Group of figures walking into a misty forest clearing at dusk, backs to the viewer. Characters are visible and sized for character_dominant, though their backs-to-camera pose gives the setting emotional weight. Cool color temperature: blue-grey mist, forest greens muted. Reflective mood: diffuse low-key lighting, soft shadows. Recurring motif: barley stalk, right edge lower-third (slightly shadowed at dusk).

---

**Volume 3 (seed: 3,461,029,847):**

Raw selections:
- `character_focal`: (3,461,029,847 + 0) % 4 = 3 → `ensemble`
- `pose_variant_index`: (3,461,029,847 + 1000) % 12 = 0 → pose #0 (standing in field, 3/4, gaze distant)
- `setting_variant_index`: (3,461,029,847 + 2000) % 10 = 9 → Temple steps, early morning, autumn
- `color_temperature`: (3,461,029,847 + 3000) % 3 = 2 → `cool`
- `mood_beat`: (3,461,029,847 + 4000) % 5 = 2 → `reflective`
- `background_treatment`: (3,461,029,847 + 5000) % 4 = 0 → `environment`
- `focal_element`: (3,461,029,847 + 6000) % 3 = 0 → `character_dominant`

Anti-repetition checks:
- Character focal: `ensemble` → Vol. 1: ensemble, Vol. 2: ensemble. Three consecutive ensembles would trigger a character focal check, but this is only the second consecutive (Vol. 1 and Vol. 2 were both ensemble; Vol. 3 is the third). The ensemble run limit is 3 max for non-protagonist; allow for now.
- Pose: index 0 ≠ Vol. 2's index 4. No adjustment.
- Temperature: `cool` === Vol. 2's `cool`. Run count = 1. Below max of 2. Allow.

Tone arc (Vol. 3 tone: `tense`):
- Selected mood_beat: `reflective`
- `reflective` IS compatible with `tense` arc (compatible list includes reflective for tense)
- No adjustment.

Final Vol. 3 selections:
- `character_focal`: ensemble
- `pose_variant`: 0 (standing 3/4, gaze distant — but adapted to ensemble grouping)
- `setting`: Temple steps, early morning, autumn
- `color_temperature`: cool
- `mood_beat`: reflective
- `background_treatment`: environment
- `focal_element`: character_dominant

**Volume 3 Cover Brief Summary:**  
Ensemble of figures on temple steps at early morning in autumn. Cool color temperature: golden fallen leaves against cool-toned stone and morning sky. Reflective-tense mood: figures stand still, gazes toward something unseen ahead. Autumn palette: warm_clay accent appears in leaf colors, counterbalancing the cool temperature register. Recurring motif: barley stalk, right edge, autumn-dried.

---

**Volume 4 (seed: 892,374,051):**

Raw selections:
- `character_focal`: (892,374,051 + 0) % 4 = 3 → `ensemble`
- `pose_variant_index`: (892,374,051 + 1000) % 12 = 6 → pose #6 (seated on step, direct camera)
- `setting_variant_index`: (892,374,051 + 2000) % 10 = 3 → Rural farmhouse interior, winter morning
- `color_temperature`: (892,374,051 + 3000) % 3 = 0 → `warm`
- `mood_beat`: (892,374,051 + 4000) % 5 = 0 → `hopeful`
- `background_treatment`: (892,374,051 + 5000) % 4 = 0 → `environment`
- `focal_element`: (892,374,051 + 6000) % 3 = 2 → `object_symbolic`

Anti-repetition checks:
- Character focal: `ensemble` → 3 consecutive volumes of ensemble. Maximum run = 3; trigger forced switch at Vol. 5. Vol. 4 ensemble is still permitted (this is the third, not exceeding).
- Pose: index 6 ≠ Vol. 3's index 0. No adjustment.
- Temperature: `warm` breaks the 2-consecutive `cool` run. Good.

Tone arc (Vol. 4 tone: `reflective`):
- Selected mood_beat: `hopeful`
- Compatible list for `reflective` arc: `[hopeful, reflective]` ✓

Final Vol. 4 selections:
- `character_focal`: ensemble
- `pose_variant`: 6 (seated, direct camera gaze — several figures around table/hearth)
- `setting`: Rural farmhouse interior, winter morning
- `color_temperature`: warm
- `mood_beat`: hopeful
- `background_treatment`: environment (interior environment — hearth fire, wooden beams)
- `focal_element`: object_symbolic (symbolic object in foreground: cooking pot, or wrapped gift, etc.)

**Volume 4 Cover Brief Summary:**  
Winter interior — figures gathered around a farmhouse hearth. A symbolic object (ceramic pot, glowing) occupies the foreground focal zone. Warm color temperature: amber firelight, cream walls, warm_clay tones prominent. Hopeful mood: upward lighting from the hearth, open expressions. Recurring motif: barley stalk — appears dried and bundled on the wall (winter preservation convention). Transition from cool Vol. 3 to warm Vol. 4 creates strong visual rhythm on a shelf display.

---

**Volume 5 (seed: 2,134,987,223):**

Raw selections:
- `character_focal`: (2,134,987,223 + 0) % 4 = 3 → `ensemble`
- — Guardrail: Vol. 1–4 character focal was: ensemble, ensemble, ensemble, ensemble. Four consecutive. Maximum protagonist run = 3; but maximum ensemble run should also be considered. The system enforces that for ANY non-protagonist focal type, 4 consecutive occurrences is too many. Force protagonist or antagonist.
- Forced character focal: re-select from `[protagonist, antagonist, supporting_primary]`
- Re-select: (2,134,987,223 + 0 + 100) % 3 = 0 → `protagonist`

- `pose_variant_index`: (2,134,987,223 + 1000) % 12 = 4 → pose #4 (walking away, back to camera)
- Anti-repetition: pose 4 was Vol. 2's pose. Not the previous volume (Vol. 4 was pose 6). Allow.

- `setting_variant_index`: (2,134,987,223 + 2000) % 10 = 5 → Forest clearing, dusk, misty
- Note: Forest clearing also appeared in Vol. 2. Not consecutive. Allow.

- `color_temperature`: (2,134,987,223 + 3000) % 3 = 1 → `neutral`
- Anti-repetition: Vol. 4 was warm. Run = 0. Allow.

- `mood_beat`: (2,134,987,223 + 4000) % 5 = 3 → `triumphant`
- Tone arc (Vol. 5 tone: `triumphant`): ✓ Compatible.

- `background_treatment`: (2,134,987,223 + 5000) % 4 = 3 → `pattern`
- `focal_element`: (2,134,987,223 + 6000) % 3 = 2 → `object_symbolic`

Final Vol. 5 selections:
- `character_focal`: protagonist (forced from ensemble run)
- `pose_variant`: 4 (walking forward... but protagonist is facing away; adapt to "protagonist walking toward light")
- `setting`: Forest clearing, dusk, misty
- `color_temperature`: neutral
- `mood_beat`: triumphant
- `background_treatment`: pattern (natural pattern: leaf scatter)
- `focal_element`: object_symbolic

**Volume 5 Cover Brief Summary:**  
Protagonist alone in a forest clearing at dusk. After four volumes with ensemble focus, the solo protagonist cover marks a turning point. Triumphant mood: high-key dusk light breaking through the canopy. Leaf scatter pattern in the background. Neutral color temperature: warm_clay in the protagonist's clothing counterbalanced by cool forest tones. A symbolic object (perhaps a lantern, or the protagonist holding something significant) occupies a secondary focal zone. Recurring motif: barley stalk, catching the last light.

### 6.4 JP vs. US Market Adaptation for Vol. 1

The same Layer 1–3 selection applies. Market adaptation changes the presentation layer.

**Vol. 1, JP:**
- Trim: 112×175mm
- Bleed: 3mm → canvas: 118×181mm (front only)
- Safe area: 5mm inside bleed
- Typography: Klee One (JP glyphs available natively)
- Title: upper-right zone, vertical orientation, ink_dusk color
- Volume number: small, lower-right, in Lato (moss_shadow color)
- Creator credit: bottom-center, smallest readable size
- Rating badge: publisher self-rating, back cover (not front cover for JP iyashikei convention)
- Spine convention: mural-ready (Vol. 1 spine design begins the mural sequence)
- Logo: back cover lower-left only; not on front cover

**Vol. 1, US:**
- Trim: 139.7×215.9mm
- Bleed: 3.175mm → canvas: 146.05×222.25mm (front only)
- Safe area: 6.35mm inside bleed
- Typography: Klee One (Latin glyphs, same font — script unchanged for EN)
- Title: upper-left zone, horizontal orientation
- Volume number: upper-right corner, or lower-right inside title zone — publisher preference
- Creator credit: below title or bottom-center
- Rating badge: publisher self-rating — for US market, typically on front cover lower-right corner
- Spine convention: text-only (no mural)
- Logo: front cover lower-right (US convention), plus back cover
- Barcode: back cover lower-right, ISBN-13 with 978-1 prefix

The core visual — ensemble on rice paddy at dawn, neutral temperature, reflective mood, natural wave pattern background — is identical between markets. Only the presentation layer differs.

---

## 7. Implementation Notes

### 7.1 File Output Locations

The engine writes computed volume variation YAMLs to:
```
config/source_of_truth/manga_cover_layers/volume_variations/{series_id}/vol_{volume:04d}.yaml
```

Cover briefs (the full assembled document ready for image generation) are written to:
```
artifacts/cover_briefs/{series_id}/vol_{volume:04d}_{market}.yaml
```

### 7.2 Incremental Generation

The engine supports incremental generation. When a new volume is added to a series:
1. Load all previous volume variation YAMLs for the series.
2. Compute seed for the new volume.
3. Run selection cascade with anti-repetition checks against loaded history.
4. Write new volume variation YAML.
5. Generate cover brief for each target market.

This means the engine does not need to regenerate all existing volumes when a new one is added. Previous volumes are not affected.

### 7.3 Forced Overrides

A brand administrator may override any Layer 3 field for a specific volume. Overrides are written directly to the volume variation YAML with an `override_reason` field. The engine respects overrides and does not apply anti-repetition adjustments to overridden fields.

```yaml
# Example override in vol_0010.yaml
pose_variant_index: 7
pose_variant_index_override_reason: "Story climax requires specific pose; approved by brand admin 2026-03-15"
```

### 7.4 Seed Stability Guarantee

The seed computation function must not change once production covers have been generated. Any change to the hash function, offset constants, or key format invalidates all previously generated cover briefs. If the function must change, a migration plan must be executed to re-approve all existing covers.

---

## 8. Validation Protocol

### 8.1 Pre-Generation Validation

Before generating a cover brief, validate:
1. `brand_id` exists in `config/source_of_truth/manga_cover_layers/brand_signatures/`
2. `series_id` exists in `config/source_of_truth/manga_cover_layers/series_signatures/`
3. `series_sig["brand_id"]` matches the passed `brand_id`
4. `volume` is a positive integer
5. `market` is one of the 12 defined market codes
6. All required bank YAMLs exist and have the minimum sizes defined in Section 5

### 8.2 Post-Generation Validation

After generating a cover brief, validate:
1. All required cover brief fields are present
2. All colors in the brief are from the brand palette
3. No taboo elements appear in the element list
4. Typography weight matches series signature
5. Background treatment is not in the register's forbidden list
6. Market adaptation applied: trim dimensions, bleed, safe area, rating badge, barcode position

### 8.3 Series Coherence Audit

For any completed volume range, run the series coherence audit:
```bash
python3 scripts/cover/series_coherence_audit.py --series-id {series_id} --volumes 1-{n}
```

The audit checks:
- Recurring motif appears in all volumes
- Accent color is consistently present
- No taboo elements in any volume
- Anti-repetition guardrails were observed
- Tone arc compliance (if defined)

---

## 9. Edge Cases and Failure Modes

### 9.1 Single-Volume Series

For a series with only one volume, the bank size minimum requirements still apply to the brand level. Anti-repetition guardrails are disabled (no history). Tone arc validation uses index 0.

### 9.2 Very Short Banks

If a pose bank has fewer than 3 items for a given brand/genre/composition combination, the anti-repetition rule is relaxed to "no same pose within 2 volumes" (rather than consecutive). Log a warning. This should never occur in production; it indicates a missing pose bank file.

### 9.3 Market Not in Schema

If a `market` code is passed that is not in the schema's 12 supported markets, the engine raises a `MarketNotSupportedError` and does not generate a cover brief. The caller must handle this and either pass a supported market code or define the new market in the schema before proceeding.

### 9.4 Story Bible Unavailable

If the series bible path does not exist, tone arc validation is skipped. The engine logs a warning: `"No story bible found for {series_id}; mood beat selection is unconstrained."` Cover generation proceeds without arc validation.

### 9.5 Protagonist Character Sheet Missing

If `protagonist_design_ref` file does not exist, cover generation proceeds but the cover brief includes a flag: `protagonist_design_unresolved: true`. The image generation system will use genre-default protagonist appearance. A human review step is inserted before the cover is approved for production.

---

## 10. Extension Points

### 10.1 New Composition Families

To add a new composition family (e.g., `deconstructed`), add:
1. The new enum value to `schema.yaml`
2. A composition variant bank entry for each brand that uses it
3. A pose bank file: `config/source_of_truth/pose_banks/deconstructed_{character_type}_poses.yaml`
4. Register/treatment restrictions for the new family in the anti-repetition module

### 10.2 New Markets

To add a new market:
1. Add market entry to `schema.yaml` with all required fields
2. Add market override rules if any elements require restriction
3. Update `market_completeness: all_12_required` to the new count
4. Add typography mapping for the market's script
5. Run validation test suite: `python3 tests/cover/test_market_adaptation.py --market {NEW}`

### 10.3 Dynamic Tone Arcs

The current implementation uses a static tone arc list that cycles. Future extension: integrate with story milestone tracking so that when a major arc is marked complete in the story bible, the engine automatically advances the tone arc pointer, ensuring post-arc volumes shift to resolution/hopeful beats.

### 10.4 AI Feedback Loop

Future extension: after a cover is generated and reviewed, capture the reviewer's notes in a feedback YAML. The feedback system learns which hash-selected combinations consistently produce covers that require override. Over time, it can pre-apply learned adjustments before the brief reaches human review.

---

*End of Manga Cover Uniqueness Engine Spec — v1.0*  
*Pearl_Architect | 2026-04-18*
