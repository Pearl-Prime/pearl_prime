"""
Manga cover generation system.

Generates programmatic covers for manga volumes across 12 global markets.
Uses a layered selection engine (brand → series → volume → market) for
deterministic, uniqueness-guaranteed cover output.

Pipeline stage: BOOK_COVER_ASSEMBLY (after panel render, before packaging)

See specs/manga_cover_pipeline_integration.md for integration details.
See specs/manga_cover_flux_workflows.md for FLUX prompt engineering reference.
See specs/manga_cover_uniqueness_engine.md for selection engine design.

Public API
----------
The following are the primary entry points consumed by the pipeline runner
and CLI scripts:

    from phoenix_v4.manga.covers import (
        generate_front_cover,
        generate_back_cover,
        generate_spine,
        assemble_full_wrap,
        render_digital_cover,
        validate_cover_set,
        list_generated_covers,
    )

Exceptions
----------
All domain exceptions are importable from this package:

    from phoenix_v4.manga.covers import (
        CoverGenerationError,
        SeriesIdentityNotFoundError,
        MarketNotSupportedError,
        CharacterSheetMissingError,
        FLUXGenerationError,
        UpscalingError,
        TypographyError,
        FrontCoverMissingError,
        BackCoverMissingError,
        SpineMissingError,
        WrapAssemblyError,
        SynopsisTranslationError,
    )

Architecture
------------
The cover system is composed of four modules:

cover_selector.py
    LayeredCoverSelector — deterministically resolves all generation
    parameters (seed, prompt variants, ControlNet settings, typography
    config) from the four-level hierarchy:
        brand_signature YAML → series_signature YAML → volume metadata
        → market_code

cover_generator.py
    CoverGenerator — calls FLUX via ComfyUI (local) or RunComfy (remote
    API) and handles upscaling. Contains the primary generate_* functions
    exposed in this package's public API.

cover_assembler.py
    CoverAssembler — PIL/Pillow-based compositing operations: typography
    overlay, logo lockup, volume badge, full wrap assembly, spine
    extraction, digital cover rendering.

market_adapters.py
    MarketAdapter hierarchy — one adapter per market code. Encapsulates
    trim sizes, typography configs (font, text direction, language),
    bleed settings, and market-specific regulatory constraints.

Data flow
---------
    operator invokes generate_front_cover(series_id, volume, market, output_dir)
        │
        ▼
    LayeredCoverSelector.select_cover_params()
        loads brand_signature.yaml + series_signature.yaml
        resolves protagonist character_id → character sheet path
        calls _compute_seed() → deterministic int seed
        returns CoverParams dataclass
        │
        ▼
    CoverGenerator._load_comfyui_workflow(genre, market)
        loads base workflow JSON from config/comfyui_workflows/manga_covers/
        patches: prompt, seed, resolution, ControlNet inputs
        │
        ▼
    CoverGenerator._call_flux_api(workflow_json)
        POSTs workflow to ComfyUI /prompt endpoint
        polls /history until complete
        downloads result image
        │
        ▼
    CoverGenerator._upscale(image, factor)
        runs Real-ESRGAN anime model
        │
        ▼
    CoverAssembler._overlay_typography(image, cover_params)
        gradient overlay → title text → volume badge → publisher logo
        │
        ▼
    output_dir/{volume_padded}/{market_code}/front.png
    cover_metadata.json
"""

from phoenix_v4.manga.covers.cover_generator import (
    CoverGenerator,
    generate_front_cover,
    generate_back_cover,
    generate_spine,
    assemble_full_wrap,
    render_digital_cover,
    validate_cover_set,
    list_generated_covers,
    get_spine_width_mm,
)
from phoenix_v4.manga.covers.cover_selector import (
    LayeredCoverSelector,
    CoverParams,
)
from phoenix_v4.manga.covers.cover_assembler import CoverAssembler
from phoenix_v4.manga.covers.market_adapters import (
    MarketAdapter,
    get_trim_size,
    get_typography_config,
    SUPPORTED_MARKETS,
)

# Exception classes — all importable from package root
from phoenix_v4.manga.covers.cover_generator import (
    CoverGenerationError,
    SeriesIdentityNotFoundError,
    MarketNotSupportedError,
    CharacterSheetMissingError,
    FLUXGenerationError,
    UpscalingError,
    TypographyError,
    FrontCoverMissingError,
    BackCoverMissingError,
    SpineMissingError,
    WrapAssemblyError,
    SynopsisTranslationError,
)

__all__ = [
    # Primary API
    "generate_front_cover",
    "generate_back_cover",
    "generate_spine",
    "assemble_full_wrap",
    "render_digital_cover",
    "validate_cover_set",
    "list_generated_covers",
    "get_spine_width_mm",
    # Classes
    "CoverGenerator",
    "LayeredCoverSelector",
    "CoverParams",
    "CoverAssembler",
    "MarketAdapter",
    # Market utilities
    "get_trim_size",
    "get_typography_config",
    "SUPPORTED_MARKETS",
    # Exceptions
    "CoverGenerationError",
    "SeriesIdentityNotFoundError",
    "MarketNotSupportedError",
    "CharacterSheetMissingError",
    "FLUXGenerationError",
    "UpscalingError",
    "TypographyError",
    "FrontCoverMissingError",
    "BackCoverMissingError",
    "SpineMissingError",
    "WrapAssemblyError",
    "SynopsisTranslationError",
]
