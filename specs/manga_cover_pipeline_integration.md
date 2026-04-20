# Manga Cover Pipeline Integration Spec

**Status:** DRAFT — Pearl_Research + Pearl_Architect  
**Date:** 2026-04-18  
**Scope:** Integration of FLUX-based manga cover generation into the Phoenix Omega
production pipeline — pipeline stage definition, function API, CLI integration,
GitHub Actions workflow, and character sheet dependencies  
**Companion spec:** `specs/manga_cover_flux_workflows.md`  
**Implementation scaffold:** `phoenix_v4/manga/covers/`

---

## Table of Contents

1. Pipeline Stage: BOOK_COVER_ASSEMBLY
2. Function Signatures
3. CLI Integration
4. GitHub Actions Workflow
5. Character Sheet Dependencies

---

## 1. Pipeline Stage: BOOK_COVER_ASSEMBLY

### 1.1 Position in the Production DAG

The cover assembly stage sits after all panel work and lettering are complete,
and before the packaging stage that produces the final PDF / CBZ / EPUB files.
This placement ensures:

- Chapter content is finalized before the back cover synopsis is generated
- Character final appearances are confirmed (no cover character design drift)
- Volume page count is known (required to calculate spine width)
- The cover can be packaged into the same artifact as the interior

```
panel_render
    │
    ▼
panel_QC
    │
    ▼
lettering
    │
    ▼
chapter_assembly
    │
    ▼
[BOOK_COVER_ASSEMBLY]   ◄── THIS STAGE
    │
    ▼
pdf_cbz_epub_package
    │
    ▼
storefront_upload
```

**Stage ID:** `BOOK_COVER_ASSEMBLY`  
**Stage class:** `phoenix_v4.manga.covers.cover_generator.CoverGenerator`  
**Runner affinity:** `pearl-star-gpu` (FLUX requires GPU)  
**Typical wall time:** 3–8 minutes per volume (1 market variant)  
**Typical wall time (all 12 markets):** 36–96 minutes (parallelizable)

---

### 1.2 Inputs

All inputs are resolved by `LayeredCoverSelector` before FLUX invocation.

#### Primary Input: Series Identity YAML

**Location:** `config/source_of_truth/manga_cover_layers/series_signatures/{series_id}.yaml`

**Schema (required fields):**

```yaml
series_id: "stillness-press-morning-window"
brand_id: "stillness-press"
genre: "iyashikei"
art_style_token: "soft_watercolor_manga"
protagonist_character_id: "yuki_main"
ensemble_character_ids:
  - "yuki_main"
  - "hana_secondary"
color_palette:
  primary: "#C8D8A8"      # sage green
  secondary: "#F0E0C8"    # warm cream
  accent: "#8AB0C8"       # sky blue
  dark_anchor: "#384048"  # deep slate
spine_mural_strategy: "gradient_sweep"
spine_gradient_start: "#8AB0C8"   # dawn blue (Vol.1)
spine_gradient_end: "#F0C880"     # dusk amber (Vol.12)
```

**Schema (optional fields):**

```yaml
ip_adapter_reference_volume: 1      # which vol's cover to use as IP-Adapter ref
controlnet_pose_strength_override: 0.45
negative_prompt_addendum: "mechanical elements, urban grit"
title_font_override: "fonts/YuMincho-Regular.ttf"
title_zone_fraction: 0.25
spine_safe_fraction: 0.12
volume_badge_style: "circle"
volume_badge_color: "#C83020"
```

#### Primary Input: Volume Metadata

Passed programmatically from `chapter_assembly` stage output or constructed
by CLI invocation:

```python
@dataclass
class VolumeMetadata:
    volume_number: int               # 1-based
    chapter_list: list[str]         # chapter IDs included in this volume
    page_count: int                  # total interior pages (for spine width)
    story_beat_summary: str          # 1–3 sentences for back cover synopsis
    character_roster: list[str]      # character_ids appearing in this volume
    release_date: str                # ISO date "2026-06-01"
    isbn: str | None                 # if known at generation time
```

#### Primary Input: Character Sheets

**Location:** `image_bank/{series_id}/characters/{character_id}_sheet.png`

Expected content of each character sheet:
- Front view (neutral pose)
- Three-quarter view (preferred pose)
- Action reference pose (at minimum one)
- Color reference swatches
- Key costume elements visible

Missing character sheets cause `CharacterSheetMissingError` during cover
generation and must be resolved before automated cover generation can proceed.

#### Primary Input: Market Code

One of: `JP`, `US`, `FR`, `DE`, `IT`, `BR`, `MX`, `TW`, `CN`, `KR`, `ES`, `AU`

Market code drives:
- Trim size selection (see `market_adapters.py`)
- Typography config (font, text direction, title translation)
- Negative prompt addendum (regulatory)
- Color temperature adjustment (some markets prefer cooler/warmer)

#### Primary Input: Brand Signature YAML

**Location:** `config/source_of_truth/manga_cover_layers/brand_signatures/{brand_id}.yaml`

```yaml
brand_id: "stillness-press"
publisher_name: "Stillness Press"
logo_path: "image_bank/brand/stillness-press-logo.png"
logo_position: "lower_left"
primary_brand_color: "#384048"
secondary_brand_color: "#C8D8A8"
imprint_name: null
website_url: "stillnesspress.com"
copyright_template: "© {year} Stillness Press. All rights reserved."
colophon_font: "fonts/YuMincho-Regular.ttf"
```

---

### 1.3 Outputs

All outputs are written to `output_dir` (specified at invocation):

```
{output_dir}/
  {volume_padded}/
    {market_code}/
      front.png              ← front cover, print resolution, RGB
      back.png               ← back cover with synopsis text
      spine.png              ← spine strip, exact width per page count
      full_wrap.png          ← front + spine + back assembled horizontal
      digital_cover.png      ← digital storefront optimized (JPEG 95%)
      cover_metadata.json    ← generation params, seeds, timestamps
```

**cover_metadata.json schema:**

```json
{
  "series_id": "stillness-press-morning-window",
  "volume_number": 1,
  "market_code": "JP",
  "generation_timestamp": "2026-04-18T08:30:00Z",
  "flux_model": "black-forest-labs/FLUX.1-dev",
  "flux_quantization": "fp8",
  "seed": 3891204847,
  "steps": 38,
  "cfg_scale": 6.0,
  "sampler": "dpmpp_2m",
  "scheduler": "karras",
  "resolution_generated": "1024x1600",
  "resolution_final": "1323x2067",
  "controlnet_used": "openpose",
  "controlnet_strength": 0.40,
  "ip_adapter_used": false,
  "ip_adapter_strength": null,
  "positive_prompt_hash": "sha256:a1b2c3d4...",
  "negative_prompt_hash": "sha256:e5f6g7h8...",
  "upscaler": "real-esrgan-anime-4x",
  "elapsed_seconds": 187
}
```

---

## 2. Function Signatures

### 2.1 generate_front_cover

```python
def generate_front_cover(
    series_id: str,
    volume_number: int,
    market_code: str,
    output_dir: Path,
    *,
    seed: int | None = None,
    force_regen: bool = False,
) -> Path:
    """Generate the front cover image for a manga volume.

    Uses the layered selection engine (cover_selector.py) to deterministically
    choose composition, palette, pose, and typography variants based on
    (series_id, volume_number, market_code). Calls FLUX on Pearl Star via
    RunComfy API or local ComfyUI endpoint. Overlays typography via PIL.

    The generation is fully deterministic when seed is None: the seed is
    derived via SHA-256 hash of (series_id, volume_number, market_code) so
    the same inputs always produce the same cover image. This determinism
    is critical for reproducible build artifacts.

    If front.png already exists in output_dir and force_regen is False, the
    function returns the existing path immediately (cache hit). Set force_regen
    to True to bypass this cache and regenerate.

    The function follows the two-pass FLUX workflow when the volume has a
    prior volume cover available as IP-Adapter reference (volume_number > 1
    and the Vol.N-1 front.png exists). Single-pass generation is used for
    Vol.1 or when the prior cover is unavailable.

    Typography is applied via PIL after FLUX generation. The positive prompt
    does NOT embed the actual title text; title text is rendered by
    render_title_text() using the market-appropriate font and translation.

    Args:
        series_id: Unique series identifier matching the series_signatures
                   YAML key. Example: "stillness-press-morning-window"
        volume_number: 1-based volume index. Vol.1 through Vol.N.
        market_code: ISO-style market code. One of: JP, US, FR, DE, IT,
                     BR, MX, TW, CN, KR, ES, AU. Drives trim size, typography
                     config, and market-specific negative prompt addendum.
        output_dir: Base output directory. Front cover will be written to
                    output_dir/{volume_padded}/{market_code}/front.png
        seed: Override the deterministic seed. Use for operator exploration
              and preview mode only. Do not use in automated rollout.
        force_regen: If True, delete any cached front.png and regenerate
                     from scratch. Useful when prompt or model is updated.

    Returns:
        Path to the generated front.png (absolute path).

    Raises:
        SeriesIdentityNotFoundError: series_id is not present in
            config/source_of_truth/manga_cover_layers/series_signatures/
        MarketNotSupportedError: market_code is not in the supported market
            registry (SUPPORTED_MARKETS in market_adapters.py)
        CharacterSheetMissingError: The protagonist character sheet PNG does
            not exist at image_bank/{series_id}/characters/
            {protagonist_character_id}_sheet.png
        FLUXGenerationError: The FLUX endpoint (RunComfy or local ComfyUI)
            is unavailable, returns an error response, or times out after
            the configured MAX_GENERATION_TIMEOUT_SECONDS.
        UpscalingError: Post-generation upscaling failed. Front cover at
            FLUX native resolution is preserved as front_draft.png for
            operator inspection.
        TypographyError: Font file not found or font rendering failed.

    Example:
        >>> from pathlib import Path
        >>> from phoenix_v4.manga.covers.cover_generator import generate_front_cover
        >>> output = generate_front_cover(
        ...     series_id="stillness-press-morning-window",
        ...     volume_number=1,
        ...     market_code="JP",
        ...     output_dir=Path("artifacts/covers"),
        ... )
        >>> print(output)
        artifacts/covers/vol_001/JP/front.png
    """
```

---

### 2.2 generate_back_cover

```python
def generate_back_cover(
    series_id: str,
    volume_number: int,
    market_code: str,
    output_dir: Path,
    volume_metadata: "VolumeMetadata",
    *,
    seed: int | None = None,
    force_regen: bool = False,
) -> Path:
    """Generate the back cover image for a manga volume.

    The back cover consists of:
    1. A FLUX-generated background illustration (lower visual intensity than
       front cover — does not compete for attention with synopsis text)
    2. Synopsis text block (2–4 sentences from volume_metadata.story_beat_summary,
       translated to market language)
    3. Author/artist credit line
    4. Publisher logo (larger than front cover placement)
    5. Barcode placeholder zone (lower-right, 40x25mm, pure white)
    6. ISBN text if isbn is present in volume_metadata
    7. Price text placeholder (market-specific format)
    8. Website URL from brand_signature YAML

    The FLUX prompt for the back cover is a quieter version of the front cover
    prompt: same genre aesthetic, same color palette, but environmental scene
    rather than character portrait. The character does not appear prominently
    (back cover is text-primary).

    Back cover seed is derived as: SHA-256(series_id + volume_number + market_code
    + "back") to ensure front and back are different but both deterministic.

    Args:
        series_id: Unique series identifier.
        volume_number: 1-based volume index.
        market_code: Market code. Drives language for synopsis text.
        output_dir: Base output directory. Back cover written to
                    output_dir/{volume_padded}/{market_code}/back.png
        volume_metadata: VolumeMetadata instance containing story_beat_summary
                         for synopsis text generation.
        seed: Override deterministic seed.
        force_regen: Skip cache.

    Returns:
        Path to generated back.png

    Raises:
        SeriesIdentityNotFoundError, MarketNotSupportedError,
        FLUXGenerationError, TypographyError: Same as generate_front_cover.
        SynopsisTranslationError: Market language synopsis could not be
            generated (LLM translation step failed).
    """
```

---

### 2.3 generate_spine

```python
def generate_spine(
    series_id: str,
    volume_number: int,
    market_code: str,
    output_dir: Path,
    page_count: int,
    *,
    force_regen: bool = False,
) -> Path:
    """Generate the spine image for a manga volume.

    The spine is derived from the front cover's spine-safe zone (leftmost
    spine_safe_fraction of the cover canvas) rather than being independently
    FLUX-generated. This ensures seamless visual continuity between the spine
    and front cover when assembled into the full wrap.

    Spine content (overlaid on extracted background strip):
    1. Series title text (rotated 90° for vertical readability, JP style)
       OR horizontal short title (US/FR/DE style per market config)
    2. Volume number (rotated, below series title)
    3. Publisher logo mark (small, bottom of spine)
    4. Spine mural color application (if series uses gradient_sweep strategy)

    Spine width is calculated from page_count using standard manga bindery
    formula:
        spine_mm = page_count * 0.052   # for standard 60gsm manga paper
        spine_mm = page_count * 0.065   # for heavier 70gsm paper
    Bindery paper weight is specified in brand_signature YAML.

    Args:
        series_id: Unique series identifier.
        volume_number: 1-based volume index.
        market_code: Market code. Drives text direction and font.
        output_dir: Base output directory. Spine written to
                    output_dir/{volume_padded}/{market_code}/spine.png
        page_count: Total interior page count for spine width calculation.
        force_regen: Skip cache.

    Returns:
        Path to generated spine.png

    Raises:
        SeriesIdentityNotFoundError, MarketNotSupportedError,
        TypographyError: Same conditions as generate_front_cover.
        FrontCoverMissingError: generate_spine requires front.png to exist
            (spine is extracted from it). Call generate_front_cover first.
    """
```

---

### 2.4 assemble_full_wrap

```python
def assemble_full_wrap(
    series_id: str,
    volume_number: int,
    market_code: str,
    output_dir: Path,
    *,
    force_regen: bool = False,
) -> Path:
    """Assemble front, spine, and back into a single print-ready full wrap image.

    The full wrap is the print file submitted to the bindery. It is a single
    wide image with the following horizontal layout (left to right):

        [ back cover ] [ spine ] [ front cover ]

    This layout matches industry standard: when folded at the spine, back
    cover appears on the back and front cover on the front.

    Dimensions:
        width  = back_cover_width + spine_width + front_cover_width + 2 * bleed_mm
        height = cover_height + 2 * bleed_mm
    All dimensions calculated from market trim size + standard 3mm bleed.

    Bleed extension:
        The front, spine, and back images are composited with a 3mm bleed
        extension on all outer edges. Bleed pixels are generated by mirror-
        padding (reflecting the edge pixels outward) to avoid white borders
        or visible seams at trim.

    The full wrap is saved as both:
        full_wrap.png  — lossless PNG for archival
        full_wrap.tif  — TIFF for print submission (if PrintReadyMode enabled)

    Requires:
        front.png, back.png, spine.png must all exist in
        output_dir/{volume_padded}/{market_code}/ before calling this function.

    Args:
        series_id: Unique series identifier.
        volume_number: 1-based volume index.
        market_code: Market code.
        output_dir: Base output directory. Full wrap written to
                    output_dir/{volume_padded}/{market_code}/full_wrap.png
        force_regen: Skip cache.

    Returns:
        Path to generated full_wrap.png

    Raises:
        FrontCoverMissingError: front.png not found.
        BackCoverMissingError: back.png not found.
        SpineMissingError: spine.png not found.
        WrapAssemblyError: Dimension mismatch between component images.
    """
```

---

### 2.5 render_digital_cover

```python
def render_digital_cover(
    series_id: str,
    volume_number: int,
    market_code: str,
    output_dir: Path,
    *,
    target_format: str = "jpeg",    # "jpeg" or "webp"
    jpeg_quality: int = 95,
    webp_quality: int = 90,
    force_regen: bool = False,
) -> Path:
    """Render digital storefront cover optimized for e-reader and web display.

    Digital covers differ from print covers in several ways:
    1. Resolution target: 1080×1920px (9:16) or 625×1000px (storefront)
       rather than print DPI.
    2. Color space: sRGB confirmed (print covers use CMYK-safe RGB palette
       which may be slightly desaturated on screen).
    3. File format: JPEG or WebP rather than PNG/TIFF.
    4. Typography: Digital-optimized font sizes (print fonts may be too small
       at screen resolution).
    5. Barcode zone: Not required on digital cover; the barcode area on the
       print cover can be cropped and replaced with extended background.

    The digital cover is derived from the print front cover, not independently
    generated. Process:
    1. Load front.png (print resolution)
    2. Crop to digital aspect ratio (remove excess bottom if needed)
    3. Resize to 1080×1920px via Lanczos
    4. Boost screen-gamma color saturation +8% (compensates for print palette
       desaturation on screen)
    5. Re-render typography at screen-optimized sizes
    6. Save as JPEG 95% or WebP 90%

    Args:
        series_id: Unique series identifier.
        volume_number: 1-based volume index.
        market_code: Market code (drives typography language).
        output_dir: Base output directory. Digital cover written to
                    output_dir/{volume_padded}/{market_code}/digital_cover.{ext}
        target_format: Output format — "jpeg" or "webp".
        jpeg_quality: JPEG quality 1–100 (default 95 for storefront).
        webp_quality: WebP quality 1–100 (default 90).
        force_regen: Skip cache.

    Returns:
        Path to generated digital_cover file.

    Raises:
        FrontCoverMissingError: front.png required before digital render.
        UnsupportedFormatError: target_format not in ("jpeg", "webp").
    """
```

---

### 2.6 Supporting Functions

```python
def get_spine_width_mm(page_count: int, paper_gsm: int = 60) -> float:
    """Calculate spine width in mm from page count and paper weight.

    Standard bindery formula:
        60gsm: page_count * 0.052 mm
        70gsm: page_count * 0.065 mm
        80gsm: page_count * 0.075 mm

    Args:
        page_count: Total interior pages (not leaf count, page count).
        paper_gsm: Paper weight in grams per square meter.

    Returns:
        Spine width in millimeters, rounded to 2 decimal places.

    Example:
        >>> get_spine_width_mm(192, 60)
        9.98  # ~10mm spine for 192-page volume
    """


def validate_cover_set(
    output_dir: Path,
    volume_number: int,
    market_code: str,
) -> "CoverSetValidationResult":
    """Validate that all required cover files exist and meet quality thresholds.

    Checks:
    1. front.png exists and is non-zero size
    2. back.png exists and is non-zero size
    3. spine.png exists and is non-zero size
    4. full_wrap.png exists
    5. digital_cover.png or .jpg exists
    6. cover_metadata.json exists and parses correctly
    7. Image dimensions match expected values for market trim size
    8. No obviously corrupt images (PIL can open successfully)

    Returns:
        CoverSetValidationResult with .valid bool and .errors list
    """


def list_generated_covers(
    series_id: str,
    output_dir: Path,
) -> dict[int, dict[str, Path]]:
    """List all generated cover sets for a series.

    Returns:
        dict mapping volume_number → dict mapping market_code → front.png path
        Example: {1: {"JP": Path("..."), "US": Path("...")}, 2: {...}}
    """
```

---

### 2.7 Exception Classes

```python
class CoverGenerationError(Exception):
    """Base class for cover generation errors."""


class SeriesIdentityNotFoundError(CoverGenerationError):
    """series_id not found in series_signatures directory."""
    def __init__(self, series_id: str, search_path: Path):
        super().__init__(
            f"Series identity YAML not found for series_id={series_id!r}. "
            f"Expected: {search_path}/{series_id}.yaml"
        )


class MarketNotSupportedError(CoverGenerationError):
    """market_code not in supported market registry."""
    def __init__(self, market_code: str):
        from phoenix_v4.manga.covers.market_adapters import SUPPORTED_MARKETS
        super().__init__(
            f"Market code {market_code!r} not supported. "
            f"Supported: {sorted(SUPPORTED_MARKETS)}"
        )


class CharacterSheetMissingError(CoverGenerationError):
    """Character sheet PNG not found."""
    def __init__(self, character_id: str, expected_path: Path):
        super().__init__(
            f"Character sheet missing for {character_id!r}. "
            f"Expected: {expected_path}"
        )


class FLUXGenerationError(CoverGenerationError):
    """FLUX generation failed."""


class UpscalingError(CoverGenerationError):
    """Post-generation upscaling failed."""


class TypographyError(CoverGenerationError):
    """Typography rendering failed (font missing or render error)."""


class FrontCoverMissingError(CoverGenerationError):
    """front.png required but not found."""


class BackCoverMissingError(CoverGenerationError):
    """back.png required but not found."""


class SpineMissingError(CoverGenerationError):
    """spine.png required but not found."""


class WrapAssemblyError(CoverGenerationError):
    """Dimension mismatch or assembly failure during full wrap composition."""


class SynopsisTranslationError(CoverGenerationError):
    """Back cover synopsis translation to market language failed."""
```

---

## 3. CLI Integration

### 3.1 scripts/run_manga_pipeline.py Additions

```bash
# Generate covers for a single volume, single market
python3 scripts/run_manga_pipeline.py \
  --series stillness-press-morning-window \
  --volume 1 \
  --market JP \
  --generate-cover

# Generate covers only (skip all panel generation steps)
python3 scripts/run_manga_pipeline.py \
  --series stillness-press-morning-window \
  --volume 1 \
  --market JP \
  --cover-only

# Generate covers for all markets for a volume
python3 scripts/run_manga_pipeline.py \
  --series stillness-press-morning-window \
  --volume 1 \
  --all-markets \
  --cover-only

# Force regenerate even if covers already exist
python3 scripts/run_manga_pipeline.py \
  --series stillness-press-morning-window \
  --volume 1 \
  --market JP \
  --cover-only \
  --force-regen

# Override seed (operator preview mode)
python3 scripts/run_manga_pipeline.py \
  --series stillness-press-morning-window \
  --volume 1 \
  --market JP \
  --cover-only \
  --seed 42

# Validate existing covers without regenerating
python3 scripts/run_manga_pipeline.py \
  --series stillness-press-morning-window \
  --volume 1 \
  --market JP \
  --validate-covers-only
```

#### New CLI Arguments (to add to run_manga_pipeline.py):

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--generate-cover` | flag | off | Include BOOK_COVER_ASSEMBLY in pipeline run |
| `--cover-only` | flag | off | Run ONLY BOOK_COVER_ASSEMBLY (skip panels) |
| `--all-markets` | flag | off | Generate covers for all 12 market codes |
| `--market` | str | JP | Single market code for cover generation |
| `--force-regen` | flag | off | Skip cover cache, regenerate all |
| `--seed` | int | None | Override deterministic seed |
| `--validate-covers-only` | flag | off | Run validation only, no generation |
| `--cover-output-dir` | Path | artifacts/covers | Override output directory |

---

### 3.2 scripts/weekly_manga_rollout.py Additions

The weekly rollout script runs on Monday as a cron job via `scripts/ci/weekly_cron.sh`.
Cover generation is added as an optional automated step.

```bash
# Weekly rollout with auto-cover generation (default on)
python3 scripts/weekly_manga_rollout.py \
  --auto-cover

# Weekly rollout without cover generation
python3 scripts/weekly_manga_rollout.py \
  --no-auto-cover

# Cover generation runs per-book in the rollout plan
# For each book in the week's rollout manifest:
#   if book.has_cover_series_identity_yaml:
#     generate_front_cover(book.series_id, book.volume, book.primary_market)
#   else:
#     log WARNING: "Cover generation skipped — no series identity YAML"
```

**New flags in weekly_manga_rollout.py:**

| Flag | Default | Description |
|------|---------|-------------|
| `--auto-cover` | True | Generate covers for all rollout books that have series identity YAMLs |
| `--no-auto-cover` | — | Disable auto-cover for this rollout run |
| `--cover-markets` | JP,US | Comma-separated markets for auto-cover (default: primary markets only) |
| `--cover-all-markets` | False | Generate all 12 market variants in rollout (slower) |

---

### 3.3 scripts/cover_generate.py (New Standalone Script)

A dedicated standalone cover generation script for operator use outside
the main pipeline:

```bash
# Generate covers for a series range of volumes
python3 scripts/cover_generate.py \
  --series stillness-press-morning-window \
  --volumes 1-5 \
  --markets JP,US,FR \
  --output-dir artifacts/covers

# Generate covers and commit to image_bank
python3 scripts/cover_generate.py \
  --series stillness-press-morning-window \
  --volume 1 \
  --market JP \
  --commit-to-image-bank

# Batch generate for all series with valid series identity YAMLs
python3 scripts/cover_generate.py \
  --all-series \
  --volume 1 \
  --market JP \
  --dry-run   # show what would be generated without running FLUX
```

---

## 4. GitHub Actions Workflow

### 4.1 Workflow: manga-cover-generate.yml

**Location:** `.github/workflows/manga-cover-generate.yml`

```yaml
name: Manga Cover Generate

on:
  workflow_dispatch:
    inputs:
      series_id:
        description: 'Series ID (e.g. stillness-press-morning-window)'
        required: true
        type: string
      volume:
        description: 'Volume number (1-based integer)'
        required: true
        type: string
        default: '1'
      market:
        description: 'Market code (JP, US, FR, DE, IT, BR, MX, TW, CN, KR, ES, AU, or ALL)'
        required: true
        type: string
        default: 'JP'
      force_regen:
        description: 'Force regeneration even if covers exist'
        required: false
        type: boolean
        default: false
      commit_to_image_bank:
        description: 'Commit generated covers to image_bank/ in repo'
        required: false
        type: boolean
        default: false

jobs:
  generate-cover:
    runs-on: [self-hosted, pearl-star-gpu]
    timeout-minutes: 120

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 1

      - name: Verify GPU availability
        run: |
          nvidia-smi
          python3 -c "import torch; print('CUDA:', torch.cuda.is_available())"

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Load integration env from keychain
        run: |
          eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
          echo "COMFYUI_ENDPOINT=$COMFYUI_ENDPOINT" >> $GITHUB_ENV
          echo "RUNCOMFY_API_KEY=$RUNCOMFY_API_KEY" >> $GITHUB_ENV

      - name: Validate series identity YAML exists
        run: |
          python3 -c "
          from pathlib import Path
          series_id = '${{ inputs.series_id }}'
          yaml_path = Path('config/source_of_truth/manga_cover_layers/series_signatures') / f'{series_id}.yaml'
          if not yaml_path.exists():
              raise FileNotFoundError(f'Series identity YAML missing: {yaml_path}')
          print(f'Series identity YAML found: {yaml_path}')
          "

      - name: Generate manga cover
        run: |
          MARKET="${{ inputs.market }}"
          if [ "$MARKET" = "ALL" ]; then
            MARKET_ARG="--all-markets"
          else
            MARKET_ARG="--market $MARKET"
          fi

          FORCE_FLAG=""
          if [ "${{ inputs.force_regen }}" = "true" ]; then
            FORCE_FLAG="--force-regen"
          fi

          python3 scripts/cover_generate.py \
            --series "${{ inputs.series_id }}" \
            --volume "${{ inputs.volume }}" \
            $MARKET_ARG \
            $FORCE_FLAG \
            --output-dir artifacts/covers

      - name: Validate generated covers
        run: |
          python3 -c "
          from pathlib import Path
          from phoenix_v4.manga.covers.cover_generator import validate_cover_set
          result = validate_cover_set(
              output_dir=Path('artifacts/covers'),
              volume_number=int('${{ inputs.volume }}'),
              market_code='${{ inputs.market }}' if '${{ inputs.market }}' != 'ALL' else 'JP',
          )
          if not result.valid:
              for error in result.errors:
                  print(f'ERROR: {error}')
              raise SystemExit(1)
          print('Cover set validation PASSED')
          "

      - name: Upload cover artifacts
        uses: actions/upload-artifact@v4
        with:
          name: covers-${{ inputs.series_id }}-vol${{ inputs.volume }}-${{ inputs.market }}
          path: artifacts/covers/
          retention-days: 30

      - name: Commit covers to image_bank (optional)
        if: inputs.commit_to_image_bank == true
        run: |
          git config user.name "Pearl_GitHub"
          git config user.email "pearl-github@phoenix-omega.internal"
          
          DEST="image_bank/${{ inputs.series_id }}/covers/vol_$(printf '%03d' ${{ inputs.volume }})"
          mkdir -p "$DEST"
          cp -r artifacts/covers/vol_$(printf '%03d' ${{ inputs.volume }})/ "$DEST/"
          
          git add "image_bank/${{ inputs.series_id }}/covers/"
          git commit -m "feat(covers): add vol${{ inputs.volume }} cover for ${{ inputs.series_id }} [${{ inputs.market }}]"
          git push origin HEAD

      - name: Post generation summary
        run: |
          echo "## Cover Generation Complete" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "- **Series:** ${{ inputs.series_id }}" >> $GITHUB_STEP_SUMMARY
          echo "- **Volume:** ${{ inputs.volume }}" >> $GITHUB_STEP_SUMMARY
          echo "- **Market:** ${{ inputs.market }}" >> $GITHUB_STEP_SUMMARY
          echo "- **Force regen:** ${{ inputs.force_regen }}" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "Covers uploaded as workflow artifact." >> $GITHUB_STEP_SUMMARY
```

---

### 4.2 Workflow: manga-cover-validate.yml

A lighter validation-only workflow for checking existing covers without
FLUX generation:

```yaml
name: Manga Cover Validate

on:
  workflow_dispatch:
    inputs:
      series_id:
        description: 'Series ID'
        required: true
        type: string
      volume:
        description: 'Volume number'
        required: true
        type: string
  pull_request:
    paths:
      - 'image_bank/**/covers/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install Pillow PyYAML
      - name: Validate cover set
        run: |
          python3 scripts/validate_covers.py \
            --series "${{ inputs.series_id }}" \
            --volume "${{ inputs.volume }}"
```

---

## 5. Character Sheet Dependencies

### 5.1 What Must Exist Before Covers Auto-Generate

Automated cover generation has three hard dependencies. All three must be
satisfied for a given series before the `BOOK_COVER_ASSEMBLY` stage will run
without raising a blocking error.

#### Dependency 1: Character Sheet Files

**Required files:**

```
image_bank/{series_id}/characters/
  {protagonist_character_id}_sheet.png          ← REQUIRED
  {protagonist_character_id}_sheet.pose.png     ← auto-generated on first use
  {secondary_character_ids...}_sheet.png        ← REQUIRED for multi-character covers
```

**Character sheet quality requirements:**

- Minimum resolution: 512×768px (lower will produce degraded OpenPose extraction)
- Recommended resolution: 1024×1536px or higher
- Format: PNG with or without alpha channel
- Background: solid white or transparent preferred (aids OpenPose extraction)
- Content: full body visible in at least one view (head-to-toe for OpenPose)
- Color accuracy: final production colors (not rough concept colors)

**How to create character sheets:**
1. Use `phoenix_v4/manga/llm/character_designer.py` for AI-assisted generation
2. Or upload manually from artist deliverables
3. Or extract from series bible illustration

**What happens if character sheet is missing:**

```
CharacterSheetMissingError is raised.
Cover generation aborts with message:
  "Character sheet missing for {character_id}. Expected:
   image_bank/{series_id}/characters/{character_id}_sheet.png
   Create this file before running cover generation for series {series_id}."
```

#### Dependency 2: Series Identity YAML

**Required file:**

```
config/source_of_truth/manga_cover_layers/series_signatures/{series_id}.yaml
```

**Minimum viable YAML (required fields only):**

```yaml
series_id: "{series_id}"
brand_id: "{brand_id}"
genre: "{genre}"
art_style_token: "{style_token}"
protagonist_character_id: "{character_id}"
color_palette:
  primary: "#RRGGBB"
  secondary: "#RRGGBB"
  accent: "#RRGGBB"
  dark_anchor: "#RRGGBB"
```

**Who creates this:** The operator creates one YAML per series when that
series is prioritized for cover generation. This is not auto-generated.

**How to create:** Copy `config/source_of_truth/manga_cover_layers/series_signatures/_template.yaml`
and fill in the required fields.

**What happens if YAML is missing:**

```
SeriesIdentityNotFoundError is raised.
Cover generation aborts with message:
  "Series identity YAML not found for series_id={series_id}.
   Expected: config/source_of_truth/manga_cover_layers/series_signatures/{series_id}.yaml
   Create this file using the template at _template.yaml."
```

#### Dependency 3: Brand Signature YAML

**Required file:**

```
config/source_of_truth/manga_cover_layers/brand_signatures/{brand_id}.yaml
```

The `brand_id` is specified inside the series identity YAML. Brand signature
YAMLs are created once per brand (publisher imprint) and reused across all
series under that brand.

**For Stillness Press:** This YAML is a WS6 deliverable and is tracked as
a current-sprint item. Status: **IN PROGRESS**. See sprint board.

---

### 5.2 Blockers for First Real Cover (Stillness Press "Morning Window")

The following items must be resolved before the first automated cover run:

#### Blocker 1: Stillness Press Brand Signature YAML

**Status:** WS6 deliverable — IN PROGRESS (this sprint)

**File:** `config/source_of_truth/manga_cover_layers/brand_signatures/stillness-press.yaml`

**Owner:** Operator / brand admin  
**Estimated completion:** End of current sprint

**Minimum content required:**

```yaml
brand_id: "stillness-press"
publisher_name: "Stillness Press"
logo_path: "image_bank/brand/stillness-press-logo.png"
logo_position: "lower_left"
primary_brand_color: "#384048"
secondary_brand_color: "#C8D8A8"
colophon_font: "fonts/YuMincho-Regular.ttf"
copyright_template: "© {year} Stillness Press. All rights reserved."
paper_gsm: 60
```

**Unblocks:** All Stillness Press series cover generation.

#### Blocker 2: "Morning Window" Series Identity YAML

**Status:** NOT STARTED

**File:** `config/source_of_truth/manga_cover_layers/series_signatures/stillness-press-morning-window.yaml`

**Owner:** Operator  
**Priority:** HIGH — required before Vol.1 cover can generate

**Minimum content:** See template at `config/source_of_truth/manga_cover_layers/series_signatures/_template.yaml`

**Note:** This YAML cannot be created until the series bible is finalized
(genre confirmed as iyashikei, protagonist character ID confirmed).

#### Blocker 3: Protagonist Character Sheet

**Status:** NEEDS INVESTIGATION — check Workstream 5 forensic analysis output

**File:** `image_bank/stillness-press-morning-window/characters/{protagonist_id}_sheet.png`

**Owner:** Depends on Workstream 5 status

**Investigation steps:**

```bash
# Check if any character sheets exist for this series
ls image_bank/stillness-press-morning-window/characters/ 2>/dev/null || \
  echo "No character directory found"

# Check Workstream 5 deliverables
grep -r "morning-window" docs/ --include="*.md" -l

# Check series bible for protagonist character ID
cat config/source_of_truth/manga_cover_layers/series_signatures/*.yaml 2>/dev/null | \
  grep -A5 "morning-window"
```

**Fallback if character sheet is unavailable:**
- Generate a rough character sheet via FLUX using the series bible description
- Tag this as `[DRAFT - REPLACE WITH ARTIST DELIVERABLE]`
- Use for cover development only; replace before print submission

---

### 5.3 Series Identity YAML Template

```yaml
# Template: config/source_of_truth/manga_cover_layers/series_signatures/_template.yaml
# Copy to {series_id}.yaml and fill in all required fields.

# ── REQUIRED ─────────────────────────────────────────────────────────────────
series_id: ""                          # must match directory basename
brand_id: ""                           # must match a brand_signatures/ YAML
genre: ""                              # one of: shonen, shojo, seinen, josei,
                                       #   kodomomuke, isekai, horror, sports,
                                       #   iyashikei, bl, gl, mecha
art_style_token: ""                    # style descriptor for FLUX prompt
protagonist_character_id: ""           # must match character sheet filename
color_palette:
  primary: ""                          # hex e.g. "#C8D8A8"
  secondary: ""
  accent: ""
  dark_anchor: ""

# ── OPTIONAL — characters ────────────────────────────────────────────────────
ensemble_character_ids: []             # additional characters that may appear

# ── OPTIONAL — spine mural ───────────────────────────────────────────────────
spine_mural_strategy: "none"           # "none", "gradient_sweep", "character_mosaic", "typographic"
spine_gradient_start: null             # hex color for Vol.1 spine (gradient_sweep only)
spine_gradient_end: null               # hex color for Vol.N spine (gradient_sweep only)

# ── OPTIONAL — generation overrides ─────────────────────────────────────────
ip_adapter_reference_volume: 1
controlnet_pose_strength_override: null
negative_prompt_addendum: null
title_font_override: null
title_zone_fraction: null              # default: 0.22
spine_safe_fraction: null             # default: 0.12

# ── OPTIONAL — volume badge ──────────────────────────────────────────────────
volume_badge_style: "circle"           # "circle", "rectangle", "star"
volume_badge_color: null               # default: genre-standard color

# ── OPTIONAL — market overrides ─────────────────────────────────────────────
market_color_temperature_overrides:
  CN: null                             # cool|warm|null
  US: null
  DE: null
```

---

### 5.4 Dependency Resolution Checklist

Before running first cover generation for any new series, verify:

```bash
SERIES_ID="stillness-press-morning-window"
BRAND_ID="stillness-press"

echo "=== Cover Generation Dependency Check ==="
echo ""

# Check 1: Brand signature YAML
BRAND_YAML="config/source_of_truth/manga_cover_layers/brand_signatures/${BRAND_ID}.yaml"
if [ -f "$BRAND_YAML" ]; then
  echo "✓ Brand signature YAML: $BRAND_YAML"
else
  echo "✗ MISSING brand signature YAML: $BRAND_YAML"
fi

# Check 2: Series identity YAML
SERIES_YAML="config/source_of_truth/manga_cover_layers/series_signatures/${SERIES_ID}.yaml"
if [ -f "$SERIES_YAML" ]; then
  echo "✓ Series identity YAML: $SERIES_YAML"
else
  echo "✗ MISSING series identity YAML: $SERIES_YAML"
fi

# Check 3: Character sheet
# (Read protagonist ID from series YAML if it exists)
if [ -f "$SERIES_YAML" ]; then
  CHAR_ID=$(python3 -c "
import yaml
with open('$SERIES_YAML') as f:
    d = yaml.safe_load(f)
print(d.get('protagonist_character_id', 'UNKNOWN'))
  ")
  CHAR_SHEET="image_bank/${SERIES_ID}/characters/${CHAR_ID}_sheet.png"
  if [ -f "$CHAR_SHEET" ]; then
    echo "✓ Character sheet: $CHAR_SHEET"
  else
    echo "✗ MISSING character sheet: $CHAR_SHEET"
  fi
fi

# Check 4: ComfyUI endpoint reachable
if python3 -c "
import os, urllib.request
endpoint = os.environ.get('COMFYUI_ENDPOINT', '')
if not endpoint:
    raise SystemExit('COMFYUI_ENDPOINT not set')
urllib.request.urlopen(endpoint + '/system_stats', timeout=5)
" 2>/dev/null; then
  echo "✓ ComfyUI endpoint reachable"
else
  echo "✗ ComfyUI endpoint NOT reachable (check COMFYUI_ENDPOINT env var)"
fi

echo ""
echo "=== Check complete ==="
```

---

*Spec end. See `specs/manga_cover_flux_workflows.md` for FLUX prompt engineering details.*  
*Implementation: `phoenix_v4/manga/covers/` scaffold files.*
