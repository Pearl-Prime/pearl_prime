"""
Market adapter system for manga cover generation.

Each market has distinct physical specifications, typography requirements,
and regulatory constraints for book covers. This module provides:

- TrimSize objects per market (physical dimensions, DPI, FLUX resolution)
- TypographyConfig objects per market (font, direction, language, sizing)
- Market registry with all supported market codes
- MarketAdapter base class + per-market adapter stubs

Supported market codes:
    JP  — Japan (tankōbon standard)
    US  — United States (trade paperback)
    FR  — France (BD album adjacent)
    DE  — Germany
    IT  — Italy
    BR  — Brazil (Portuguese)
    MX  — Mexico (Spanish)
    TW  — Taiwan (Traditional Chinese)
    CN  — China mainland (Simplified Chinese)
    KR  — South Korea
    ES  — Spain (Spanish)
    AU  — Australia (same trim as US)

Usage:
    from phoenix_v4.manga.covers.market_adapters import (
        get_trim_size,
        get_typography_config,
        SUPPORTED_MARKETS,
    )

    trim = get_trim_size("JP")
    print(trim.width_mm, trim.height_mm)  # 112, 175

    typo = get_typography_config("JP", fonts_root=Path("fonts"))
    print(typo.title_language)  # "ja"
    print(typo.text_direction)  # "vertical_jp"
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path


# ── Registry ───────────────────────────────────────────────────────────────────

SUPPORTED_MARKETS: frozenset[str] = frozenset({
    "JP", "US", "FR", "DE", "IT", "BR", "MX", "TW", "CN", "KR", "ES", "AU"
})


# ── Data structures (re-exported here for convenience) ─────────────────────────

@dataclass
class TrimSize:
    """
    Physical trim size for a market book format.

    Attributes:
        width_mm: Cover width in millimeters (front cover only, not wrap).
        height_mm: Cover height in millimeters.
        bleed_mm: Bleed extension on each outer edge (default 3mm).
        dpi: Print DPI requirement (typically 300).
        spine_paper_gsm: Default paper weight for spine width calculation.
    """
    width_mm: float
    height_mm: float
    bleed_mm: float = 3.0
    dpi: int = 300
    spine_paper_gsm: int = 60

    @property
    def width_px(self) -> int:
        """Cover width at print DPI in pixels."""
        return int((self.width_mm / 25.4) * self.dpi)

    @property
    def height_px(self) -> int:
        """Cover height at print DPI in pixels."""
        return int((self.height_mm / 25.4) * self.dpi)

    @property
    def flux_width(self) -> int:
        """Nearest FLUX-compatible width (multiple of 64, max 1280)."""
        return _nearest_flux_dim(self.width_px, max_dim=1280)

    @property
    def flux_height(self) -> int:
        """Nearest FLUX-compatible height (multiple of 64, max 2048)."""
        return _nearest_flux_dim(self.height_px, max_dim=2048)

    @property
    def aspect_ratio(self) -> float:
        """Height / width ratio."""
        return self.height_mm / self.width_mm

    @property
    def bleed_width_px(self) -> int:
        """Bleed width in pixels."""
        return int((self.bleed_mm / 25.4) * self.dpi)


@dataclass
class TypographyConfig:
    """
    Typography configuration for a specific market.

    Attributes:
        market_code: Market code this config applies to.
        title_font_path: Path to primary title font file (.ttf / .otf).
        volume_font_path: Path to volume number font file.
        text_direction: "horizontal" or "vertical_jp" (top-to-bottom, right column).
        title_language: BCP-47 language tag for title text (e.g. "ja", "en", "fr").
        title_color: RGB tuple for main title text.
        stroke_color: RGB tuple for text outline.
        stroke_width: Outline width in pixels.
        title_size_fraction: Title font size as fraction of canvas height.
        volume_size_fraction: Volume number font size as fraction of canvas height.
        rtl: Whether text direction is right-to-left (Arabic/Hebrew — not current).
    """
    market_code: str
    title_font_path: Path
    volume_font_path: Path
    text_direction: str = "horizontal"
    title_language: str = "en"
    title_color: tuple[int, int, int] = field(default_factory=lambda: (255, 255, 255))
    stroke_color: tuple[int, int, int] = field(default_factory=lambda: (0, 0, 0))
    stroke_width: int = 3
    title_size_fraction: float = 0.075
    volume_size_fraction: float = 0.045
    rtl: bool = False


# ── Market trim size registry ──────────────────────────────────────────────────

_TRIM_SIZE_REGISTRY: dict[str, TrimSize] = {
    # Japan: B6 variant (standard tankōbon)
    "JP": TrimSize(width_mm=112.0, height_mm=175.0, bleed_mm=3.0, dpi=300, spine_paper_gsm=60),

    # United States: manga trade paperback (Viz / Kodansha USA standard)
    "US": TrimSize(width_mm=139.7, height_mm=215.9, bleed_mm=3.175, dpi=300, spine_paper_gsm=60),

    # France: BD poche / manga format (slightly taller than JP)
    "FR": TrimSize(width_mm=115.0, height_mm=178.0, bleed_mm=3.0, dpi=300, spine_paper_gsm=60),

    # Germany: same as France format for most manga publishers
    "DE": TrimSize(width_mm=115.0, height_mm=178.0, bleed_mm=3.0, dpi=300, spine_paper_gsm=60),

    # Italy: close to French format
    "IT": TrimSize(width_mm=115.0, height_mm=178.0, bleed_mm=3.0, dpi=300, spine_paper_gsm=60),

    # Brazil: same as US trade paperback
    "BR": TrimSize(width_mm=139.7, height_mm=215.9, bleed_mm=3.175, dpi=300, spine_paper_gsm=60),

    # Mexico: same as US trade paperback
    "MX": TrimSize(width_mm=139.7, height_mm=215.9, bleed_mm=3.175, dpi=300, spine_paper_gsm=60),

    # Taiwan: B6 (same as JP)
    "TW": TrimSize(width_mm=112.0, height_mm=175.0, bleed_mm=3.0, dpi=300, spine_paper_gsm=60),

    # China mainland: B6 (same as JP)
    "CN": TrimSize(width_mm=112.0, height_mm=175.0, bleed_mm=3.0, dpi=300, spine_paper_gsm=60),

    # South Korea: B6 (same as JP)
    "KR": TrimSize(width_mm=112.0, height_mm=175.0, bleed_mm=3.0, dpi=300, spine_paper_gsm=60),

    # Spain: same as France/DE
    "ES": TrimSize(width_mm=115.0, height_mm=178.0, bleed_mm=3.0, dpi=300, spine_paper_gsm=60),

    # Australia: same as US (Madman distribution)
    "AU": TrimSize(width_mm=139.7, height_mm=215.9, bleed_mm=3.175, dpi=300, spine_paper_gsm=60),
}


# ── Public accessors ───────────────────────────────────────────────────────────

def get_trim_size(market_code: str) -> TrimSize:
    """
    Return the TrimSize specification for a given market code.

    Args:
        market_code: One of the SUPPORTED_MARKETS codes.

    Returns:
        TrimSize dataclass with physical dimensions and DPI.

    Raises:
        KeyError: If market_code is not in the registry.
                  (Callers should validate market_code via SUPPORTED_MARKETS first.)

    Example:
        >>> trim = get_trim_size("JP")
        >>> trim.width_mm
        112.0
        >>> trim.flux_width
        1024   # nearest multiple of 64 to 1323px
    """
    if market_code not in _TRIM_SIZE_REGISTRY:
        raise KeyError(
            f"Market code {market_code!r} not in trim size registry. "
            f"Supported: {sorted(_TRIM_SIZE_REGISTRY.keys())}"
        )
    return _TRIM_SIZE_REGISTRY[market_code]


def get_typography_config(
    market_code: str,
    fonts_root: Path | None = None,
) -> TypographyConfig:
    """
    Return TypographyConfig for a given market code.

    Resolves font paths relative to fonts_root. If a specific font file
    does not exist, falls back to PIL's built-in default font (lower quality).

    Args:
        market_code: Market code.
        fonts_root: Root directory for font files. Defaults to repo fonts/.

    Returns:
        TypographyConfig with market-appropriate font, direction, and language.

    Raises:
        KeyError: If market_code is not in the registry.
    """
    if fonts_root is None:
        fonts_root = Path(__file__).resolve().parents[4] / "fonts"

    adapter = _get_adapter(market_code)
    return adapter.get_typography_config(fonts_root)


def get_market_adapter(market_code: str) -> "MarketAdapter":
    """
    Return the MarketAdapter instance for a given market code.

    Args:
        market_code: Market code.

    Returns:
        MarketAdapter subclass instance.
    """
    return _get_adapter(market_code)


# ── MarketAdapter base class ───────────────────────────────────────────────────

class MarketAdapter(ABC):
    """
    Base class for per-market cover adaptation.

    Each market has a concrete subclass that encapsulates:
    - Typography settings (font, direction, language)
    - Trim size (via get_trim_size())
    - Market-specific regulatory constraints
    - Color temperature preferences

    Subclasses override get_typography_config() and optionally
    apply_regulatory_constraints().
    """

    market_code: str = ""

    def get_trim_size(self) -> TrimSize:
        """Return the trim size for this market."""
        return get_trim_size(self.market_code)

    @abstractmethod
    def get_typography_config(self, fonts_root: Path) -> TypographyConfig:
        """Return TypographyConfig for this market."""
        ...

    def apply_regulatory_constraints(
        self,
        positive_prompt: str,
        negative_prompt: str,
    ) -> tuple[str, str]:
        """
        Apply any market-specific regulatory modifications to prompts.

        Base implementation returns prompts unchanged. Override in
        subclasses that have specific regulatory requirements.

        Args:
            positive_prompt: FLUX positive prompt.
            negative_prompt: FLUX negative prompt.

        Returns:
            (modified_positive_prompt, modified_negative_prompt) tuple.
        """
        return positive_prompt, negative_prompt

    def get_color_temperature_adjustment(self) -> float:
        """
        Return color temperature multiplier for this market.

        1.0 = no adjustment (JP reference)
        > 1.0 = warmer
        < 1.0 = cooler

        Base implementation returns 1.0 (no adjustment).
        """
        return 1.0

    def _resolve_font(self, fonts_root: Path, *candidates: str) -> Path:
        """
        Resolve font path from ordered candidates list.

        Returns the first candidate that exists, or a fallback PIL default.
        """
        for candidate in candidates:
            path = fonts_root / candidate
            if path.exists():
                return path
        # Return a path that will trigger PIL default font fallback
        return fonts_root / candidates[0] if candidates else fonts_root / "default.ttf"


# ── Per-market adapter implementations ────────────────────────────────────────

class JPMarketAdapter(MarketAdapter):
    """Japan market adapter. Reference market — no modifications."""

    market_code = "JP"

    def get_typography_config(self, fonts_root: Path) -> TypographyConfig:
        title_font = self._resolve_font(
            fonts_root,
            "YuMincho-Regular.ttf",
            "NotoSerifCJKjp-Regular.otf",
            "NotoSansCJKjp-Regular.otf",
        )
        return TypographyConfig(
            market_code="JP",
            title_font_path=title_font,
            volume_font_path=title_font,
            text_direction="vertical_jp",
            title_language="ja",
            title_color=(255, 255, 255),
            stroke_color=(0, 0, 0),
            stroke_width=3,
            title_size_fraction=0.075,
            volume_size_fraction=0.042,
        )


class USMarketAdapter(MarketAdapter):
    """United States market adapter."""

    market_code = "US"

    def get_typography_config(self, fonts_root: Path) -> TypographyConfig:
        title_font = self._resolve_font(
            fonts_root,
            "Roboto-Bold.ttf",
            "NotoSans-Bold.ttf",
            "Arial-Bold.ttf",
        )
        return TypographyConfig(
            market_code="US",
            title_font_path=title_font,
            volume_font_path=title_font,
            text_direction="horizontal",
            title_language="en",
            title_color=(255, 255, 255),
            stroke_color=(0, 0, 0),
            stroke_width=4,
            title_size_fraction=0.080,  # slightly larger for US market readability
            volume_size_fraction=0.045,
        )


class FRMarketAdapter(MarketAdapter):
    """France market adapter."""

    market_code = "FR"

    def get_typography_config(self, fonts_root: Path) -> TypographyConfig:
        title_font = self._resolve_font(
            fonts_root,
            "NotoSans-Regular.ttf",
            "Roboto-Regular.ttf",
        )
        return TypographyConfig(
            market_code="FR",
            title_font_path=title_font,
            volume_font_path=title_font,
            text_direction="horizontal",
            title_language="fr",
            title_color=(255, 255, 255),
            stroke_color=(0, 0, 0),
            stroke_width=3,
            title_size_fraction=0.073,
            volume_size_fraction=0.040,
        )


class DEMarketAdapter(MarketAdapter):
    """Germany market adapter."""

    market_code = "DE"

    def get_typography_config(self, fonts_root: Path) -> TypographyConfig:
        title_font = self._resolve_font(
            fonts_root,
            "NotoSans-Bold.ttf",
            "Roboto-Bold.ttf",
        )
        return TypographyConfig(
            market_code="DE",
            title_font_path=title_font,
            volume_font_path=title_font,
            text_direction="horizontal",
            title_language="de",
            title_color=(255, 255, 255),
            stroke_color=(0, 0, 0),
            stroke_width=3,
            title_size_fraction=0.073,
            volume_size_fraction=0.040,
        )

    def apply_regulatory_constraints(
        self,
        positive_prompt: str,
        negative_prompt: str,
    ) -> tuple[str, str]:
        """Add DE regulatory negative prompt addendum."""
        de_negative = "fascist or nazi imagery or symbology, hate symbols"
        return positive_prompt, f"{negative_prompt}, {de_negative}"


class ITMarketAdapter(MarketAdapter):
    """Italy market adapter."""

    market_code = "IT"

    def get_typography_config(self, fonts_root: Path) -> TypographyConfig:
        title_font = self._resolve_font(
            fonts_root,
            "NotoSans-Regular.ttf",
            "Roboto-Regular.ttf",
        )
        return TypographyConfig(
            market_code="IT",
            title_font_path=title_font,
            volume_font_path=title_font,
            text_direction="horizontal",
            title_language="it",
            title_color=(255, 255, 255),
            stroke_color=(0, 0, 0),
            stroke_width=3,
            title_size_fraction=0.073,
            volume_size_fraction=0.040,
        )


class BRMarketAdapter(MarketAdapter):
    """Brazil market adapter (Portuguese)."""

    market_code = "BR"

    def get_typography_config(self, fonts_root: Path) -> TypographyConfig:
        title_font = self._resolve_font(
            fonts_root,
            "NotoSans-Bold.ttf",
            "Roboto-Bold.ttf",
        )
        return TypographyConfig(
            market_code="BR",
            title_font_path=title_font,
            volume_font_path=title_font,
            text_direction="horizontal",
            title_language="pt-BR",
            title_color=(255, 255, 255),
            stroke_color=(0, 0, 0),
            stroke_width=4,
            title_size_fraction=0.078,
            volume_size_fraction=0.045,
        )


class MXMarketAdapter(MarketAdapter):
    """Mexico market adapter (Spanish)."""

    market_code = "MX"

    def get_typography_config(self, fonts_root: Path) -> TypographyConfig:
        title_font = self._resolve_font(
            fonts_root,
            "NotoSans-Bold.ttf",
            "Roboto-Bold.ttf",
        )
        return TypographyConfig(
            market_code="MX",
            title_font_path=title_font,
            volume_font_path=title_font,
            text_direction="horizontal",
            title_language="es-MX",
            title_color=(255, 255, 255),
            stroke_color=(0, 0, 0),
            stroke_width=4,
            title_size_fraction=0.078,
            volume_size_fraction=0.045,
        )


class TWMarketAdapter(MarketAdapter):
    """Taiwan market adapter (Traditional Chinese)."""

    market_code = "TW"

    def get_typography_config(self, fonts_root: Path) -> TypographyConfig:
        title_font = self._resolve_font(
            fonts_root,
            "NotoSerifCJKtc-Regular.otf",
            "NotoSansCJKtc-Regular.otf",
            "NotoSansCJKjp-Regular.otf",
        )
        return TypographyConfig(
            market_code="TW",
            title_font_path=title_font,
            volume_font_path=title_font,
            text_direction="vertical_jp",  # Traditional Chinese also uses vertical
            title_language="zh-Hant",
            title_color=(255, 255, 255),
            stroke_color=(0, 0, 0),
            stroke_width=3,
            title_size_fraction=0.075,
            volume_size_fraction=0.042,
        )


class CNMarketAdapter(MarketAdapter):
    """China mainland market adapter (Simplified Chinese)."""

    market_code = "CN"

    def get_typography_config(self, fonts_root: Path) -> TypographyConfig:
        title_font = self._resolve_font(
            fonts_root,
            "NotoSansCJKsc-Regular.otf",
            "NotoSansCJKjp-Regular.otf",
        )
        return TypographyConfig(
            market_code="CN",
            title_font_path=title_font,
            volume_font_path=title_font,
            text_direction="horizontal",  # CN manga typically horizontal
            title_language="zh-Hans",
            title_color=(255, 255, 255),
            stroke_color=(0, 0, 0),
            stroke_width=3,
            title_size_fraction=0.075,
            volume_size_fraction=0.042,
        )

    def apply_regulatory_constraints(
        self,
        positive_prompt: str,
        negative_prompt: str,
    ) -> tuple[str, str]:
        """Add CN regulatory negative prompt addendum."""
        cn_negative = (
            "japanese militaria insignia, rising sun imagery, skull imagery on cover, "
            "imperial japanese uniform elements, political symbol imagery"
        )
        return positive_prompt, f"{negative_prompt}, {cn_negative}"

    def get_color_temperature_adjustment(self) -> float:
        """CN market: slight desaturation applied post-generation."""
        return 0.92


class KRMarketAdapter(MarketAdapter):
    """South Korea market adapter (Korean)."""

    market_code = "KR"

    def get_typography_config(self, fonts_root: Path) -> TypographyConfig:
        title_font = self._resolve_font(
            fonts_root,
            "NotoSansCJKkr-Regular.otf",
            "NotoSansKR-Regular.otf",
        )
        return TypographyConfig(
            market_code="KR",
            title_font_path=title_font,
            volume_font_path=title_font,
            text_direction="horizontal",
            title_language="ko",
            title_color=(255, 255, 255),
            stroke_color=(0, 0, 0),
            stroke_width=3,
            title_size_fraction=0.075,
            volume_size_fraction=0.042,
        )


class ESMarketAdapter(MarketAdapter):
    """Spain market adapter (Spanish)."""

    market_code = "ES"

    def get_typography_config(self, fonts_root: Path) -> TypographyConfig:
        title_font = self._resolve_font(
            fonts_root,
            "NotoSans-Bold.ttf",
            "Roboto-Bold.ttf",
        )
        return TypographyConfig(
            market_code="ES",
            title_font_path=title_font,
            volume_font_path=title_font,
            text_direction="horizontal",
            title_language="es",
            title_color=(255, 255, 255),
            stroke_color=(0, 0, 0),
            stroke_width=3,
            title_size_fraction=0.073,
            volume_size_fraction=0.040,
        )


class AUMarketAdapter(MarketAdapter):
    """Australia market adapter (English)."""

    market_code = "AU"

    def get_typography_config(self, fonts_root: Path) -> TypographyConfig:
        title_font = self._resolve_font(
            fonts_root,
            "Roboto-Bold.ttf",
            "NotoSans-Bold.ttf",
        )
        return TypographyConfig(
            market_code="AU",
            title_font_path=title_font,
            volume_font_path=title_font,
            text_direction="horizontal",
            title_language="en-AU",
            title_color=(255, 255, 255),
            stroke_color=(0, 0, 0),
            stroke_width=4,
            title_size_fraction=0.080,
            volume_size_fraction=0.045,
        )

    def apply_regulatory_constraints(
        self,
        positive_prompt: str,
        negative_prompt: str,
    ) -> tuple[str, str]:
        """Add AU classification-aware negative prompt."""
        au_negative = (
            "explicit horror body horror imagery visible at storefront thumbnail, "
            "explicit violence detail, sexually suggestive cover framing"
        )
        return positive_prompt, f"{negative_prompt}, {au_negative}"


# ── Market adapter registry ────────────────────────────────────────────────────

_ADAPTER_REGISTRY: dict[str, type[MarketAdapter]] = {
    "JP": JPMarketAdapter,
    "US": USMarketAdapter,
    "FR": FRMarketAdapter,
    "DE": DEMarketAdapter,
    "IT": ITMarketAdapter,
    "BR": BRMarketAdapter,
    "MX": MXMarketAdapter,
    "TW": TWMarketAdapter,
    "CN": CNMarketAdapter,
    "KR": KRMarketAdapter,
    "ES": ESMarketAdapter,
    "AU": AUMarketAdapter,
}


def _get_adapter(market_code: str) -> MarketAdapter:
    """Return a MarketAdapter instance for the given market code."""
    if market_code not in _ADAPTER_REGISTRY:
        raise KeyError(
            f"Market code {market_code!r} not in adapter registry. "
            f"Supported: {sorted(_ADAPTER_REGISTRY.keys())}"
        )
    return _ADAPTER_REGISTRY[market_code]()


# ── Utility ────────────────────────────────────────────────────────────────────

def _nearest_flux_dim(pixels: int, max_dim: int = 2048, multiple: int = 64) -> int:
    """Round pixel count to nearest multiple of 64, capping at max_dim."""
    rounded = round(pixels / multiple) * multiple
    return min(rounded, max_dim)


def list_market_specs() -> dict[str, dict]:
    """
    Return a summary dict of all market specifications.

    Useful for debugging and documentation generation.

    Returns:
        dict mapping market_code → {trim_size, flux_resolution, language}
    """
    result = {}
    for code in sorted(SUPPORTED_MARKETS):
        trim = get_trim_size(code)
        result[code] = {
            "trim_width_mm": trim.width_mm,
            "trim_height_mm": trim.height_mm,
            "trim_width_px": trim.width_px,
            "trim_height_px": trim.height_px,
            "flux_width": trim.flux_width,
            "flux_height": trim.flux_height,
            "bleed_mm": trim.bleed_mm,
            "dpi": trim.dpi,
        }
    return result
