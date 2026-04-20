"""
Layered cover selection engine.

Deterministically resolves all FLUX generation parameters for a manga cover
from the four-level hierarchy:

    brand_signature YAML
        → series_signature YAML
            → volume metadata
                → market_code

The selection engine is the "brain" of the cover system: it takes the
operator-defined configuration files and produces a fully-specified
CoverParams dataclass that the CoverGenerator can act on without making
any creative decisions.

Determinism guarantee
---------------------
Given the same (brand_id, series_id, volume_number, market_code) inputs,
select_cover_params() always returns the same CoverParams. This is achieved
by deriving the seed from a SHA-256 hash of the input tuple, and using that
seed for all probabilistic variant selections (pose reference, background
variant, typography color, etc.).

This determinism is intentional: cover images are build artifacts. The same
source inputs should always produce the same cover. Operator override via
the seed= CLI parameter breaks determinism intentionally, for preview and
exploration only.

Layer bank selection
--------------------
The _select_layer() method picks one item from a list of options using a
seeded pseudorandom generator. It is NOT truly random — the selection is
fully determined by (seed, seed_offset). Different seed_offsets are used
for different parameter dimensions (pose choice, background choice, palette
variant, etc.) so each dimension is independent but still deterministic.

Usage
-----
    selector = LayeredCoverSelector(config_root=Path("config/source_of_truth"))
    params = selector.select_cover_params(
        brand_id="stillness-press",
        series_id="stillness-press-morning-window",
        volume_number=1,
        market_code="JP",
    )
    print(params.seed)            # deterministic int
    print(params.genre)           # "iyashikei"
    print(params.positive_prompt) # full FLUX positive prompt string
    print(params.controlnet_config)  # ControlNetConfig or None
"""

from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


# ── Dataclasses ────────────────────────────────────────────────────────────────

@dataclass
class TrimSize:
    """Physical trim size for a market."""
    width_mm: float
    height_mm: float
    bleed_mm: float = 3.0
    dpi: int = 300

    @property
    def width_px(self) -> int:
        return int((self.width_mm / 25.4) * self.dpi)

    @property
    def height_px(self) -> int:
        return int((self.height_mm / 25.4) * self.dpi)

    @property
    def flux_width(self) -> int:
        """Nearest FLUX-compatible width (multiple of 64, max 1280)."""
        return _nearest_flux_dim(self.width_px, max_dim=1280)

    @property
    def flux_height(self) -> int:
        """Nearest FLUX-compatible height (multiple of 64, max 2048)."""
        return _nearest_flux_dim(self.height_px, max_dim=2048)


@dataclass
class ControlNetConfig:
    """Configuration for a single ControlNet pass."""
    type: str              # "openpose", "depth", "canny"
    model_id: str          # HuggingFace model ID or local path
    strength: float        # 0.0–1.0
    guidance_start: float = 0.0
    guidance_end: float = 1.0
    input_image_path: Path | None = None  # resolved at generation time


@dataclass
class TypographyConfig:
    """Typography settings for a specific market."""
    market_code: str
    title_font_path: Path
    volume_font_path: Path
    text_direction: str        # "horizontal", "vertical_jp"
    title_language: str        # BCP-47 code e.g. "ja", "en", "fr"
    title_color: tuple[int, int, int] = (255, 255, 255)
    stroke_color: tuple[int, int, int] = (0, 0, 0)
    stroke_width: int = 3
    title_size_fraction: float = 0.08  # as fraction of canvas height


@dataclass
class CoverParams:
    """
    Fully resolved parameters for a single FLUX cover generation run.

    Produced by LayeredCoverSelector.select_cover_params(). This dataclass
    is passed directly to CoverGenerator and CoverAssembler; they should not
    need to read any YAML files themselves.

    All paths are absolute.
    """
    # Identity
    series_id: str
    brand_id: str
    volume_number: int
    market_code: str

    # Generation
    seed: int
    genre: str
    art_style_token: str
    positive_prompt: str
    negative_prompt: str
    steps: int
    cfg_scale: float
    sampler: str
    scheduler: str
    flux_width: int
    flux_height: int
    flux_model_id: str = "black-forest-labs/FLUX.1-dev"
    flux_quantization: str = "fp8"

    # ControlNet (None = disabled)
    controlnet_config: ControlNetConfig | None = None

    # IP-Adapter (None = disabled)
    ip_adapter_reference_path: Path | None = None
    ip_adapter_strength: float | None = None

    # Character sheets
    protagonist_sheet_path: Path | None = None
    protagonist_pose_map_path: Path | None = None

    # Typography
    typography_config: TypographyConfig | None = None
    title_text: str = ""
    title_zone_fraction: float = 0.22
    spine_safe_fraction: float = 0.12

    # Brand / publisher
    logo_path: Path | None = None
    logo_position: str = "lower_left"
    copyright_text: str = ""
    volume_badge_style: str = "circle"
    volume_badge_color: tuple[int, int, int] = field(default_factory=lambda: (200, 30, 30))

    # Physical
    trim_size: TrimSize | None = None
    spine_width_mm: float | None = None
    page_count: int | None = None

    # Metadata
    generation_pass: int = 1   # 1 = single pass or pass 1 of 2
    two_pass_mode: bool = False


# ── Main selector class ────────────────────────────────────────────────────────

class LayeredCoverSelector:
    """
    Deterministic cover parameter resolver.

    Reads brand and series identity YAML files and combines them with
    volume/market context to produce a fully resolved CoverParams object.

    Args:
        config_root: Path to the config/source_of_truth directory.
                     Defaults to the canonical location relative to repo root.
        image_bank_root: Path to image_bank/. Defaults to canonical location.
        fonts_root: Path to fonts/. Defaults to canonical location.
        flux_model_id: FLUX model to use. Default is FLUX.1-dev.
        flux_quantization: Quantization level. "fp16" or "fp8".
    """

    SERIES_SIGNATURES_DIR = "manga_cover_layers/series_signatures"
    BRAND_SIGNATURES_DIR = "manga_cover_layers/brand_signatures"

    def __init__(
        self,
        config_root: Path | None = None,
        image_bank_root: Path | None = None,
        fonts_root: Path | None = None,
        flux_model_id: str = "black-forest-labs/FLUX.1-dev",
        flux_quantization: str = "fp8",
    ) -> None:
        repo_root = Path(__file__).resolve().parents[4]
        self._config_root = config_root or (repo_root / "config" / "source_of_truth")
        self._image_bank_root = image_bank_root or (repo_root / "image_bank")
        self._fonts_root = fonts_root or (repo_root / "fonts")
        self._flux_model_id = flux_model_id
        self._flux_quantization = flux_quantization

        # Lazy-loaded YAML caches
        self._brand_cache: dict[str, dict] = {}
        self._series_cache: dict[str, dict] = {}

    # ── Public API ──────────────────────────────────────────────────────────

    def select_cover_params(
        self,
        brand_id: str,
        series_id: str,
        volume_number: int,
        market_code: str,
        *,
        page_count: int | None = None,
        title_text: str = "",
        seed_override: int | None = None,
    ) -> CoverParams:
        """
        Resolve all cover generation parameters deterministically.

        Args:
            brand_id: Brand identifier. Must match a brand_signatures YAML.
            series_id: Series identifier. Must match a series_signatures YAML.
            volume_number: 1-based volume index.
            market_code: Market code (JP, US, FR, etc.).
            page_count: Interior page count for spine width calculation.
            title_text: Series title string (localized for market if needed).
            seed_override: If provided, overrides the deterministic seed.
                           Use only for operator preview.

        Returns:
            CoverParams — fully resolved, ready for CoverGenerator.

        Raises:
            SeriesIdentityNotFoundError, MarketNotSupportedError,
            CharacterSheetMissingError
        """
        from phoenix_v4.manga.covers.cover_generator import (
            SeriesIdentityNotFoundError,
            MarketNotSupportedError,
            CharacterSheetMissingError,
        )
        from phoenix_v4.manga.covers.market_adapters import (
            SUPPORTED_MARKETS,
            get_trim_size,
            get_typography_config,
        )

        # Validate market
        if market_code not in SUPPORTED_MARKETS:
            raise MarketNotSupportedError(market_code)

        # Load YAMLs
        brand_data = self._load_brand_signature(brand_id)
        series_data = self._load_series_signature(series_id)

        # Compute seed
        seed = seed_override if seed_override is not None else self._compute_seed(
            brand_id, series_id, volume_number, market_code
        )

        # Genre and style
        genre = series_data["genre"]
        art_style_token = series_data["art_style_token"]

        # Protagonist character sheet
        protagonist_id = series_data.get("protagonist_character_id", "")
        protagonist_sheet = None
        protagonist_pose_map = None
        if protagonist_id:
            sheet_path = (
                self._image_bank_root
                / series_id
                / "characters"
                / f"{protagonist_id}_sheet.png"
            )
            if not sheet_path.exists():
                raise CharacterSheetMissingError(protagonist_id, sheet_path)
            protagonist_sheet = sheet_path
            pose_map = sheet_path.with_suffix(".pose.png")
            protagonist_pose_map = pose_map if pose_map.exists() else None

        # Trim size + typography
        trim_size = get_trim_size(market_code)
        typography_config = get_typography_config(market_code, self._fonts_root)

        # Apply font override from series YAML if present
        font_override = series_data.get("title_font_override")
        if font_override:
            override_path = self._fonts_root / font_override
            if override_path.exists():
                typography_config.title_font_path = override_path

        # Build prompts
        positive_prompt = self._build_positive_prompt(
            genre, art_style_token, series_data, market_code, seed
        )
        negative_prompt = self._build_negative_prompt(
            genre, market_code, series_data.get("negative_prompt_addendum")
        )

        # FLUX generation params from genre defaults
        gen_params = self._get_genre_generation_params(genre)

        # ControlNet config
        controlnet = self._build_controlnet_config(
            genre, protagonist_pose_map, series_data
        )

        # IP-Adapter: available for Vol.2+
        ip_adapter_ref = None
        ip_adapter_strength = None
        two_pass_mode = False
        if volume_number > 1:
            prior_cover = self._find_prior_cover(series_id, volume_number - 1, market_code)
            if prior_cover and prior_cover.exists():
                ip_adapter_ref = prior_cover
                ip_adapter_strength = 0.50
                two_pass_mode = True

        # Logo and brand
        logo_path_str = brand_data.get("logo_path", "")
        logo_path = (self._image_bank_root.parent / logo_path_str) if logo_path_str else None
        if logo_path and not logo_path.exists():
            logo_path = None  # graceful degradation

        year = 2026  # TODO: pull from volume metadata
        copyright_text = brand_data.get(
            "copyright_template", "© {year} {publisher}"
        ).format(year=year, publisher=brand_data.get("publisher_name", ""))

        # Spine width
        spine_width_mm = None
        if page_count:
            paper_gsm = brand_data.get("paper_gsm", 60)
            from phoenix_v4.manga.covers.cover_generator import get_spine_width_mm
            spine_width_mm = get_spine_width_mm(page_count, paper_gsm)

        return CoverParams(
            series_id=series_id,
            brand_id=brand_id,
            volume_number=volume_number,
            market_code=market_code,
            seed=seed,
            genre=genre,
            art_style_token=art_style_token,
            positive_prompt=positive_prompt,
            negative_prompt=negative_prompt,
            steps=gen_params["steps"],
            cfg_scale=gen_params["cfg_scale"],
            sampler=gen_params["sampler"],
            scheduler=gen_params["scheduler"],
            flux_width=trim_size.flux_width,
            flux_height=trim_size.flux_height,
            flux_model_id=self._flux_model_id,
            flux_quantization=self._flux_quantization,
            controlnet_config=controlnet,
            ip_adapter_reference_path=ip_adapter_ref,
            ip_adapter_strength=ip_adapter_strength,
            protagonist_sheet_path=protagonist_sheet,
            protagonist_pose_map_path=protagonist_pose_map,
            typography_config=typography_config,
            title_text=title_text,
            title_zone_fraction=series_data.get("title_zone_fraction", 0.22),
            spine_safe_fraction=series_data.get("spine_safe_fraction", 0.12),
            logo_path=logo_path,
            logo_position=brand_data.get("logo_position", "lower_left"),
            copyright_text=copyright_text,
            volume_badge_style=series_data.get("volume_badge_style", "circle"),
            trim_size=trim_size,
            spine_width_mm=spine_width_mm,
            page_count=page_count,
            two_pass_mode=two_pass_mode,
        )

    # ── Private: seed computation ────────────────────────────────────────────

    def _compute_seed(
        self,
        brand_id: str,
        series_id: str,
        volume_number: int,
        market_code: str,
    ) -> int:
        """
        Compute deterministic generation seed via SHA-256 hash.

        The seed is derived from the concatenated string:
            "{brand_id}|{series_id}|{volume_number}|{market_code}"

        The first 8 bytes of the SHA-256 digest are interpreted as a
        big-endian unsigned integer, then masked to 32 bits to stay within
        ComfyUI seed range.

        This guarantees:
        - Same inputs → same seed (always)
        - Different volume numbers → different seeds
        - Different market codes → different seeds (different crop/comp)
        - Brand and series scoping prevents cross-series collision
        """
        key = f"{brand_id}|{series_id}|{volume_number}|{market_code}"
        digest = hashlib.sha256(key.encode("utf-8")).digest()
        seed_64 = int.from_bytes(digest[:8], "big")
        return seed_64 & 0xFFFFFFFF  # 32-bit mask for ComfyUI compatibility

    # ── Private: layer selection ─────────────────────────────────────────────

    def _select_layer(
        self,
        layer_bank: list[Any],
        seed_offset: int,
    ) -> Any:
        """
        Deterministically select one item from layer_bank using seed_offset.

        Uses Python's random.Random seeded with (self._current_seed + seed_offset)
        to select one element from layer_bank. Different seed_offsets ensure
        independent selections across different parameter dimensions.

        Args:
            layer_bank: List of options to choose from.
            seed_offset: Integer offset applied to seed for this dimension.
                         Convention: 0=pose, 1=background, 2=palette, 3=badge

        Returns:
            Selected item from layer_bank.

        Raises:
            ValueError: If layer_bank is empty.
        """
        if not layer_bank:
            raise ValueError("layer_bank must not be empty")
        rng = random.Random(self._current_seed + seed_offset)
        return rng.choice(layer_bank)

    # ── Private: YAML loading ────────────────────────────────────────────────

    def _load_brand_signature(self, brand_id: str) -> dict:
        if brand_id not in self._brand_cache:
            path = (
                self._config_root
                / self.BRAND_SIGNATURES_DIR
                / f"{brand_id}.yaml"
            )
            if not path.exists():
                raise FileNotFoundError(
                    f"Brand signature YAML not found: {path}"
                )
            with path.open("r", encoding="utf-8") as f:
                self._brand_cache[brand_id] = yaml.safe_load(f)
        return self._brand_cache[brand_id]

    def _load_series_signature(self, series_id: str) -> dict:
        if series_id not in self._series_cache:
            from phoenix_v4.manga.covers.cover_generator import SeriesIdentityNotFoundError
            path = (
                self._config_root
                / self.SERIES_SIGNATURES_DIR
                / f"{series_id}.yaml"
            )
            if not path.exists():
                raise SeriesIdentityNotFoundError(series_id, path.parent)
            with path.open("r", encoding="utf-8") as f:
                self._series_cache[series_id] = yaml.safe_load(f)
        return self._series_cache[series_id]

    # ── Private: prompt building ─────────────────────────────────────────────

    def _build_positive_prompt(
        self,
        genre: str,
        art_style_token: str,
        series_data: dict,
        market_code: str,
        seed: int,
    ) -> str:
        """
        Build positive FLUX prompt from genre template + series customization.

        Loads the genre base prompt from the internal genre template registry,
        then injects series-specific elements (color palette, art style token,
        protagonist description if available).

        TODO: Full prompt templates are in specs/manga_cover_flux_workflows.md.
        This implementation returns the genre base prompt with art_style_token
        injected. Future iteration: load from config YAML templates.
        """
        self._current_seed = seed  # store for _select_layer calls
        base = _GENRE_BASE_PROMPTS.get(genre, _GENRE_BASE_PROMPTS["iyashikei"])
        palette = series_data.get("color_palette", {})
        palette_desc = ""
        if palette:
            palette_desc = (
                f"color palette: primary {palette.get('primary', '')}, "
                f"secondary {palette.get('secondary', '')}, "
                f"accent {palette.get('accent', '')}"
            )
        prompt_parts = [base, art_style_token, palette_desc]
        return ", ".join(p for p in prompt_parts if p.strip())

    def _build_negative_prompt(
        self,
        genre: str,
        market_code: str,
        series_addendum: str | None,
    ) -> str:
        """Build negative prompt from universal + genre + market blocks."""
        parts = [_UNIVERSAL_NEGATIVE]
        genre_neg = _GENRE_NEGATIVE_PROMPTS.get(genre, "")
        if genre_neg:
            parts.append(genre_neg)
        market_neg = _MARKET_NEGATIVE_ADDENDUMS.get(market_code, "")
        if market_neg:
            parts.append(market_neg)
        if series_addendum:
            parts.append(series_addendum)
        return ", ".join(p for p in parts if p.strip())

    def _build_controlnet_config(
        self,
        genre: str,
        pose_map_path: Path | None,
        series_data: dict,
    ) -> ControlNetConfig | None:
        """Build ControlNet config for genre, if applicable."""
        strength_override = series_data.get("controlnet_pose_strength_override")
        defaults = _GENRE_CONTROLNET_DEFAULTS.get(genre, {})
        if not defaults:
            return None
        strength = strength_override if strength_override else defaults.get("strength", 0.5)
        return ControlNetConfig(
            type=defaults.get("type", "openpose"),
            model_id=defaults.get("model_id", "XLabs-AI/flux-controlnet-canny"),
            strength=strength,
            guidance_start=defaults.get("guidance_start", 0.0),
            guidance_end=defaults.get("guidance_end", 0.65),
            input_image_path=pose_map_path,
        )

    def _get_genre_generation_params(self, genre: str) -> dict:
        """Return FLUX sampler parameters for the given genre."""
        return _GENRE_GENERATION_PARAMS.get(genre, _GENRE_GENERATION_PARAMS["iyashikei"])

    def _find_prior_cover(
        self, series_id: str, prior_volume: int, market_code: str
    ) -> Path | None:
        """Locate prior volume's front.png for IP-Adapter reference."""
        vol_str = f"vol_{prior_volume:03d}"
        candidate = (
            self._image_bank_root
            / series_id
            / "covers"
            / vol_str
            / market_code
            / "front.png"
        )
        return candidate if candidate.exists() else None


# ── Genre defaults registry ────────────────────────────────────────────────────

_GENRE_GENERATION_PARAMS: dict[str, dict] = {
    "shonen": {"steps": 35, "cfg_scale": 7.0, "sampler": "euler_ancestral", "scheduler": "karras"},
    "shojo": {"steps": 40, "cfg_scale": 6.5, "sampler": "dpmpp_2m", "scheduler": "karras"},
    "seinen": {"steps": 40, "cfg_scale": 7.5, "sampler": "dpmpp_2m_sde", "scheduler": "karras"},
    "josei": {"steps": 38, "cfg_scale": 6.5, "sampler": "dpmpp_2m", "scheduler": "karras"},
    "kodomomuke": {"steps": 30, "cfg_scale": 7.0, "sampler": "euler", "scheduler": "normal"},
    "isekai": {"steps": 40, "cfg_scale": 7.5, "sampler": "dpmpp_2m_sde", "scheduler": "karras"},
    "horror": {"steps": 42, "cfg_scale": 8.0, "sampler": "dpmpp_2m_sde", "scheduler": "karras"},
    "sports": {"steps": 35, "cfg_scale": 7.5, "sampler": "euler_ancestral", "scheduler": "karras"},
    "iyashikei": {"steps": 38, "cfg_scale": 6.0, "sampler": "dpmpp_2m", "scheduler": "karras"},
    "bl": {"steps": 40, "cfg_scale": 6.5, "sampler": "dpmpp_2m", "scheduler": "karras"},
    "gl": {"steps": 40, "cfg_scale": 6.5, "sampler": "dpmpp_2m", "scheduler": "karras"},
    "mecha": {"steps": 45, "cfg_scale": 8.0, "sampler": "dpmpp_2m_sde", "scheduler": "karras"},
}

_GENRE_CONTROLNET_DEFAULTS: dict[str, dict] = {
    "shonen": {"type": "openpose", "model_id": "XLabs-AI/flux-controlnet-depth", "strength": 0.65, "guidance_end": 0.60},
    "shojo": {"type": "openpose", "model_id": "XLabs-AI/flux-controlnet-depth", "strength": 0.50, "guidance_end": 0.55},
    "seinen": {"type": "depth", "model_id": "XLabs-AI/flux-controlnet-depth", "strength": 0.45, "guidance_end": 0.70},
    "isekai": {"type": "openpose", "model_id": "XLabs-AI/flux-controlnet-depth", "strength": 0.65, "guidance_end": 0.60},
    "horror": {"type": "canny", "model_id": "XLabs-AI/flux-controlnet-canny", "strength": 0.55, "guidance_end": 0.75},
    "sports": {"type": "openpose", "model_id": "XLabs-AI/flux-controlnet-depth", "strength": 0.70, "guidance_end": 0.65},
    "mecha": {"type": "canny", "model_id": "XLabs-AI/flux-controlnet-canny", "strength": 0.65, "guidance_end": 0.80},
    # Genres with no default ControlNet (None returned)
    "josei": {},
    "kodomomuke": {},
    "iyashikei": {},
    "bl": {},
    "gl": {},
}

# Abbreviated prompt bases — full prompts in specs/manga_cover_flux_workflows.md
_GENRE_BASE_PROMPTS: dict[str, str] = {
    "shonen": (
        "title-safe zone: upper 22% canvas reserved, full-body dynamic action pose, "
        "teenage male protagonist, centered, illustration style: high-contrast manga cover art, "
        "crisp linework, cel-shading, vibrant saturated color palette, professional shonen manga cover"
    ),
    "shojo": (
        "title-safe zone: upper 25% canvas reserved, centered character portrait, teenage female "
        "protagonist, head at 82% canvas height, delicate features, large luminous eyes, "
        "soft manga shojo cover art, pastel color palette, watercolor-wash background, "
        "professional shojo manga cover"
    ),
    "seinen": (
        "title-safe zone: upper 20% canvas reserved, full-body or bust portrait, adult protagonist, "
        "complex morally ambiguous expression, seinen manga cover art, high realism mixed with manga "
        "stylization, muted sophisticated color palette, strong cinematic composition"
    ),
    "josei": (
        "title-safe zone: upper 22% canvas reserved, portrait composition, adult female protagonist "
        "aged 22-35, josei manga cover art, realistic manga rendering, warm tones, elegant negative space"
    ),
    "kodomomuke": (
        "title-safe zone: upper 28% canvas reserved, full-body cheerful pose, child protagonist, "
        "vibrant children's manga cover art, thick outlines, fully saturated primary color palette, "
        "pure joy adventure mood"
    ),
    "isekai": (
        "title-safe zone: upper 20% canvas reserved, full-body heroic stance, protagonist left 60% "
        "of frame, fantasy adventure gear, isekai manga cover art, epic fantasy landscape background, "
        "dramatic backlighting"
    ),
    "horror": (
        "title-safe zone: upper 20% canvas reserved, horror manga cover art, high contrast black and "
        "white with selective single-color accent, heavy inking cross-hatch, Ito Junji influence, "
        "dread inevitability mood"
    ),
    "sports": (
        "title-safe zone: upper 20% canvas reserved, full-body mid-action pose, athlete protagonist, "
        "explosive peak athletic movement, sports manga cover art, dynamic kinetic linework, "
        "warm energetic color palette, peak effort mood"
    ),
    "iyashikei": (
        "title-safe zone: upper 25% canvas reserved, centered character portrait or environmental "
        "establishing shot, protagonist in quiet peaceful activity, relaxed restful expression, "
        "iyashikei manga cover art, soft semi-realistic manga style, watercolor-influenced color "
        "treatment, soft color palette warm cream pale sage sky blue golden hour amber, "
        "golden hour warm diffuse light, gentle healing quiet contentment mood, "
        "professional iyashikei manga cover illustration, Enterbrain Fellows aesthetic"
    ),
    "bl": (
        "title-safe zone: upper 22% canvas reserved, two-shot romantic composition, two adult male "
        "characters, emotional tension, BL manga cover art, refined shojo-adjacent linework, "
        "warm romantic color palette, elegant composition"
    ),
    "gl": (
        "title-safe zone: upper 22% canvas reserved, two-shot romantic composition, two adult female "
        "characters, emotional tension, GL manga cover art, refined elegant linework, "
        "warm romantic color palette"
    ),
    "mecha": (
        "title-safe zone: upper 20% canvas reserved, mecha unit occupying 70% of canvas height, "
        "hard-surface rendering, angular armor panels, pilot portrait inset upper-left, "
        "mecha manga cover art, cold space ambient plus thruster glow lighting"
    ),
}

_UNIVERSAL_NEGATIVE = (
    "watermark, text overlay, embedded title text, signature, low resolution, blurry, "
    "jpeg artifacts, compression artifacts, pixelated, oversaturated, color banding, "
    "white border, black border, anatomical errors extra fingers fused fingers six fingers, "
    "deformed face, asymmetric eyes, uncanny valley, AI face artifacts, "
    "western comic book style, Marvel DC superhero aesthetic"
)

_GENRE_NEGATIVE_PROMPTS: dict[str, str] = {
    "shonen": "feminine features, pastel palette, static standing pose, photorealistic render, adult nudity",
    "shojo": "masculine features, thick aggressive linework, dark gritty atmosphere, violence blood gore",
    "seinen": "childlike proportions, cute mascots, pastel cheerful colors, sparkle effects",
    "josei": "teenage proportions, sparkle shojo effects, battle poses, horror atmosphere",
    "kodomomuke": "adult themes, violence, blood, dark color palette, scary imagery",
    "isekai": "mundane real-world setting, photorealistic render, western fantasy tolkien aesthetic",
    "horror": "cheerful bright colors, cute mascots, happy smiling expressions, sparkle effects",
    "sports": "sedentary pose, dark horror framing, magical fantasy elements, photorealistic photograph",
    "iyashikei": "violence, blood, weapons, heavy dark shadows, urban grit, angry expression, horror",
    "bl": "explicit sexual content, juvenile proportions, violence, photorealistic pornographic influence",
    "gl": "explicit sexual content, juvenile proportions, violence, photorealistic pornographic influence",
    "mecha": "purely organic design without mechanical integration, overly soft rounded forms, pastel palette",
}

_MARKET_NEGATIVE_ADDENDUMS: dict[str, str] = {
    "CN": "japanese militaria insignia, rising sun imagery, skull imagery, imperial japanese uniform",
    "DE": "fascist or nazi imagery or symbology",
    "AU": "explicit horror body horror imagery, explicit violence detail, sexually suggestive cover framing",
    "US": "explicit horror gore detail visible in storefront thumbnail",
}


# ── Utility ────────────────────────────────────────────────────────────────────

def _nearest_flux_dim(pixels: int, max_dim: int = 2048, multiple: int = 64) -> int:
    """Round pixel count to nearest multiple of 64, capping at max_dim."""
    rounded = round(pixels / multiple) * multiple
    return min(rounded, max_dim)
