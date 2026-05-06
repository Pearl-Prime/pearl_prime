"""
PIL/Pillow-based cover compositing and assembly.

Handles all post-FLUX image operations:
- Typography overlay (title text, volume badge, copyright)
- Publisher logo compositing
- Gradient overlay for title zone legibility
- Full wrap assembly (front + spine + back)
- Digital cover rendering (resize, color adjustment, re-typography)
- Spine extraction and mural composition

All methods accept and return PIL Image objects or Paths.
Image objects are in RGBA mode internally; outputs are converted
to RGB before PNG save (removes alpha for final print files).

Dependencies:
    Pillow >= 9.0
    Optional: numpy (for gradient operations — falls back to pure PIL)

Usage:
    from phoenix_v4.manga.covers.cover_assembler import CoverAssembler

    assembler = CoverAssembler()
    final = assembler.overlay_typography_front(raw_path, params, out_path)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PIL import Image as PILImageModule
    from phoenix_v4.manga.covers.cover_selector import CoverParams

logger = logging.getLogger(__name__)


class CoverAssembler:
    """
    PIL/Pillow compositing operations for manga covers.

    All heavy compositing operations are lazy-import: PIL is only
    imported when a method is called. This keeps module import fast
    and allows the module to be imported in non-GPU environments
    for testing.
    """

    def __init__(self) -> None:
        self._pil_available: bool | None = None

    # ── Typography overlay ──────────────────────────────────────────────────

    def overlay_typography_front(
        self,
        raw_image_path: Path,
        params: "CoverParams",
        output_path: Path,
    ) -> Path:
        """
        Apply all typography layers to raw FLUX output for the front cover.

        Operations applied in order:
        1. apply_title_zone_gradient() — darken upper zone for legibility
        2. render_title_text()         — title string
        3. render_volume_badge()       — "Vol.N" badge
        4. composite_publisher_logo()  — brand logo

        Args:
            raw_image_path: Path to raw FLUX output PNG (upscaled).
            params: Resolved CoverParams with all typography settings.
            output_path: Where to save the final composited front.png.

        Returns:
            output_path after writing.
        """
        from PIL import Image

        with Image.open(raw_image_path) as img:
            image = img.convert("RGBA")

        # 1. Gradient overlay on title zone
        image = self.apply_title_zone_gradient(
            image,
            zone_height_fraction=params.title_zone_fraction,
        )

        # 2. Title text — fail-closed: a cover without a title is a defect, not a stylistic choice.
        # Historical bug (2026-04..2026-05): manga covers shipped to artifacts/pipeline_examples/
        # with no title rendered because params.title_text was empty AND the swallowed-exception
        # path silently passed broken covers downstream. See
        # docs/PEARL_NEWS_LAYOUT_SYSTEM_2026-05-04.md "Anti-regression checklist" — every cover
        # must have its title rendered before publish.
        if not params.title_text or not params.title_text.strip():
            raise ValueError(
                "CoverParams.title_text is required (manga covers must render a title; "
                "shipping a title-less cover violates the cover_quality_gates contract)."
            )
        if not params.typography_config:
            raise ValueError(
                "CoverParams.typography_config is required to render the title."
            )
        # Re-raise instead of swallowing — a title render failure is not recoverable here.
        image = self._render_title_text(image, params)

        # 3. Volume badge
        image = self._render_volume_badge(image, params)

        # 4. Publisher logo
        if params.logo_path and params.logo_path.exists():
            try:
                image = self._composite_publisher_logo(image, params)
            except Exception as exc:
                logger.warning("Logo composite failed: %s", exc)

        # Save as RGB PNG
        final = image.convert("RGB")
        final.save(output_path, format="PNG", optimize=False)
        logger.info("Typography applied → %s", output_path)
        return output_path

    def apply_title_zone_gradient(
        self,
        image: "PILImageModule.Image",
        zone_height_fraction: float = 0.22,
        gradient_color: tuple[int, int, int] = (0, 0, 0),
        max_opacity: int = 140,
        feather_fraction: float = 0.06,
    ) -> "PILImageModule.Image":
        """
        Apply semi-transparent gradient overlay to title zone.

        Creates a gradient that transitions from max_opacity at the top
        of the canvas to 0 at the bottom of the title zone, with a soft
        feather for smooth blending into the illustration below.

        Args:
            image: RGBA cover image.
            zone_height_fraction: Title zone height as fraction of canvas height.
            gradient_color: RGB color for gradient (typically black).
            max_opacity: Alpha at top edge (0–255). 140 = ~55% opacity.
            feather_fraction: Soft transition zone below title zone.

        Returns:
            RGBA image with gradient applied.
        """
        from PIL import Image, ImageDraw

        if image.mode != "RGBA":
            image = image.convert("RGBA")

        w, h = image.size
        zone_h = int(h * zone_height_fraction)
        feather_h = int(h * feather_fraction)
        gradient_height = zone_h + feather_h

        gradient = Image.new("RGBA", (w, gradient_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(gradient)

        for y in range(gradient_height):
            if y < zone_h:
                # Linear fade from max_opacity at top to 0 at zone bottom
                progress = y / zone_h
                alpha = int(max_opacity * (1.0 - progress))
            else:
                # Feather zone: fully transparent
                alpha = 0
            r, g, b = gradient_color
            draw.line([(0, y), (w, y)], fill=(r, g, b, alpha))

        result = image.copy()
        result.alpha_composite(gradient, dest=(0, 0))
        return result

    def _render_title_text(
        self,
        image: "PILImageModule.Image",
        params: "CoverParams",
    ) -> "PILImageModule.Image":
        """
        Render title text with stroke outline and drop shadow.

        Typography settings are taken from params.typography_config.
        Position: horizontally centered, vertically at title_zone_fraction / 2.

        Args:
            image: RGBA cover image.
            params: CoverParams with title_text and typography_config set.

        Returns:
            RGBA image with title text composited.

        Raises:
            TypographyError: Font file not found.
        """
        from PIL import Image, ImageDraw, ImageFont
        from phoenix_v4.manga.covers.cover_generator import TypographyError

        tc = params.typography_config
        if tc is None:
            return image

        font_path = tc.title_font_path
        if not font_path.exists():
            raise TypographyError(f"Title font not found: {font_path}")

        font_size = int(image.height * tc.title_size_fraction)
        font = ImageFont.truetype(str(font_path), font_size)

        text_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(text_layer)

        w, h = image.size
        title = params.title_text
        stroke_width = tc.stroke_width

        bbox = draw.textbbox((0, 0), title, font=font, stroke_width=stroke_width)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        x = (w - text_w) // 2
        y = int(h * params.title_zone_fraction * 0.35)  # ~35% down title zone

        shadow_offset = (3, 3)
        shadow_color = (*tc.stroke_color, 180)
        draw.text(
            (x + shadow_offset[0], y + shadow_offset[1]),
            title,
            font=font,
            fill=shadow_color,
        )

        # Stroke
        draw.text(
            (x, y),
            title,
            font=font,
            fill=(*tc.stroke_color, 255),
            stroke_width=stroke_width,
            stroke_fill=(*tc.stroke_color, 255),
        )

        # Main text
        draw.text(
            (x, y),
            title,
            font=font,
            fill=(*tc.title_color, 255),
        )

        result = image.copy()
        result.alpha_composite(text_layer)
        return result

    def _render_volume_badge(
        self,
        image: "PILImageModule.Image",
        params: "CoverParams",
    ) -> "PILImageModule.Image":
        """
        Render volume number badge in corner of cover.

        Badge styles: "circle", "rectangle", "star"
        Default position: upper_right (avoids title zone and spine zone)

        Args:
            image: RGBA cover image.
            params: CoverParams with volume_number, volume_badge_style, etc.

        Returns:
            RGBA image with volume badge composited.
        """
        from PIL import Image, ImageDraw, ImageFont

        if image.mode != "RGBA":
            image = image.convert("RGBA")

        w, h = image.size
        badge_size = int(w * 0.10)
        margin = int(w * 0.03)

        badge_color = params.volume_badge_color
        text = f"Vol.{params.volume_number}"

        badge_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(badge_layer)

        # Position: upper right, below title zone
        title_zone_bottom = int(h * params.title_zone_fraction)
        cx = w - margin - badge_size // 2
        cy = title_zone_bottom + margin + badge_size // 2

        style = params.volume_badge_style

        if style == "circle":
            bbox = [cx - badge_size // 2, cy - badge_size // 2,
                    cx + badge_size // 2, cy + badge_size // 2]
            draw.ellipse(bbox, fill=(*badge_color, 230))
            draw.ellipse(bbox, outline=(255, 255, 255, 200), width=2)

        elif style == "rectangle":
            bbox = [cx - badge_size * 0.7, cy - badge_size * 0.4,
                    cx + badge_size * 0.7, cy + badge_size * 0.4]
            draw.rounded_rectangle(bbox, radius=8, fill=(*badge_color, 230))

        else:  # fallback to circle
            bbox = [cx - badge_size // 2, cy - badge_size // 2,
                    cx + badge_size // 2, cy + badge_size // 2]
            draw.ellipse(bbox, fill=(*badge_color, 230))

        # Volume text
        font_size = badge_size // 3
        try:
            # Try to use a system font
            font = ImageFont.load_default()
        except Exception:
            font = None

        draw.text(
            (cx, cy),
            text,
            fill=(255, 255, 255, 255),
            font=font,
            anchor="mm",
        )

        result = image.copy()
        result.alpha_composite(badge_layer)
        return result

    def _composite_publisher_logo(
        self,
        image: "PILImageModule.Image",
        params: "CoverParams",
        max_logo_height_fraction: float = 0.06,
        margin_px: int = 24,
    ) -> "PILImageModule.Image":
        """
        Composite publisher/brand logo onto cover.

        Logo is scaled to fit within max_logo_height_fraction of canvas height,
        maintaining aspect ratio. Alpha channel preserved.

        Args:
            image: RGBA cover image.
            params: CoverParams with logo_path and logo_position.
            max_logo_height_fraction: Max logo height as fraction of canvas.
            margin_px: Margin from canvas edge in pixels.

        Returns:
            RGBA image with logo composited.
        """
        from PIL import Image

        logo_path = params.logo_path
        if not logo_path or not logo_path.exists():
            return image

        with Image.open(logo_path) as logo_img:
            logo = logo_img.convert("RGBA")

        w, h = image.size
        max_logo_h = int(h * max_logo_height_fraction)
        if logo.height > max_logo_h:
            scale = max_logo_h / logo.height
            new_w = int(logo.width * scale)
            logo = logo.resize((new_w, max_logo_h), Image.LANCZOS)

        position = params.logo_position
        lw, lh = logo.size

        if position == "lower_left":
            x, y = margin_px, h - lh - margin_px
        elif position == "lower_right":
            x, y = w - lw - margin_px, h - lh - margin_px
        elif position == "upper_left":
            x, y = margin_px, margin_px
        elif position == "upper_right":
            x, y = w - lw - margin_px, margin_px
        else:
            x, y = margin_px, h - lh - margin_px

        result = image.copy()
        result.alpha_composite(logo, dest=(x, y))
        return result

    # ── Full wrap assembly ──────────────────────────────────────────────────

    def assemble_full_wrap(
        self,
        series_id: str,
        volume_number: int,
        market_code: str,
        output_dir: Path,
        *,
        force_regen: bool = False,
    ) -> Path:
        """
        Assemble front + spine + back into a print-ready full wrap image.

        Layout (left to right): [ back ] [ spine ] [ front ]

        See specs/manga_cover_pipeline_integration.md §2.4 for full docstring.
        """
        from PIL import Image
        from phoenix_v4.manga.covers.cover_generator import (
            FrontCoverMissingError,
            BackCoverMissingError,
            SpineMissingError,
            WrapAssemblyError,
        )

        vol_dir = output_dir / f"vol_{volume_number:03d}" / market_code
        out_path = vol_dir / "full_wrap.png"

        if out_path.exists() and not force_regen:
            return out_path

        front_path = vol_dir / "front.png"
        back_path = vol_dir / "back.png"
        spine_path = vol_dir / "spine.png"

        if not front_path.exists():
            raise FrontCoverMissingError(f"front.png missing: {front_path}")
        if not back_path.exists():
            raise BackCoverMissingError(f"back.png missing: {back_path}")
        if not spine_path.exists():
            raise SpineMissingError(f"spine.png missing: {spine_path}")

        with Image.open(front_path) as f:
            front = f.convert("RGBA")
        with Image.open(back_path) as b:
            back = b.convert("RGBA")
        with Image.open(spine_path) as s:
            spine = s.convert("RGBA")

        # Validate heights match
        heights = {front.height, back.height, spine.height}
        if len(heights) > 1:
            raise WrapAssemblyError(
                f"Height mismatch in cover components: "
                f"front={front.height}, back={back.height}, spine={spine.height}"
            )

        total_width = back.width + spine.width + front.width
        height = front.height
        wrap = Image.new("RGBA", (total_width, height), (255, 255, 255, 255))
        wrap.paste(back, (0, 0))
        wrap.paste(spine, (back.width, 0))
        wrap.paste(front, (back.width + spine.width, 0))

        wrap.convert("RGB").save(out_path, format="PNG", optimize=False)
        logger.info("Full wrap assembled: %s", out_path)
        return out_path

    # ── Spine operations ────────────────────────────────────────────────────

    def generate_spine(
        self,
        series_id: str,
        volume_number: int,
        market_code: str,
        output_dir: Path,
        page_count: int,
        *,
        force_regen: bool = False,
    ) -> Path:
        """
        Generate spine image from front cover's spine-safe zone.

        See specs/manga_cover_pipeline_integration.md §2.3 for full docstring.
        """
        from PIL import Image
        from phoenix_v4.manga.covers.cover_generator import (
            FrontCoverMissingError,
            get_spine_width_mm,
        )

        vol_dir = output_dir / f"vol_{volume_number:03d}" / market_code
        out_path = vol_dir / "spine.png"

        if out_path.exists() and not force_regen:
            return out_path

        front_path = vol_dir / "front.png"
        if not front_path.exists():
            raise FrontCoverMissingError(f"front.png must exist before spine: {front_path}")

        with Image.open(front_path) as img:
            front = img.convert("RGBA")

        # Calculate spine width in pixels
        # Assume JP tankōbon trim width 112mm as default
        # TODO: read from market_adapters.get_trim_size()
        trim_width_mm = 112.0
        spine_mm = get_spine_width_mm(page_count, paper_gsm=60)
        spine_px = int((spine_mm / trim_width_mm) * front.width)
        spine_px = max(spine_px, 20)  # minimum 20px for legibility

        spine_strip = front.crop((0, 0, spine_px, front.height))

        # TODO: overlay spine text (series title + volume number)
        # TODO: apply spine mural color if series uses gradient_sweep

        spine_strip.convert("RGB").save(out_path, format="PNG")
        logger.info("Spine generated: %s (width=%dpx, %.1fmm)", out_path, spine_px, spine_mm)
        return out_path

    def extract_spine_strip(
        self,
        front_cover: "PILImageModule.Image",
        spine_width_mm: float,
        trim_width_mm: float = 112.0,
    ) -> "PILImageModule.Image":
        """
        Extract spine strip from left edge of front cover image.

        Args:
            front_cover: Full front cover at print resolution.
            spine_width_mm: Physical spine width in mm.
            trim_width_mm: Physical front cover trim width in mm.

        Returns:
            Spine strip image (narrow, full height).
        """
        w, h = front_cover.size
        spine_px = int((spine_width_mm / trim_width_mm) * w)
        return front_cover.crop((0, 0, spine_px, h))

    def compose_spine_mural(
        self,
        spine_strips: list["PILImageModule.Image"],
    ) -> "PILImageModule.Image":
        """
        Compose spine strips into a horizontal mural for QC visualization.

        Takes Vol.1 through Vol.N spine strips (left to right) and composites
        them into a single wide image for shelf presence visualization.

        Args:
            spine_strips: List of spine images, Vol.1 first (leftmost on shelf).

        Returns:
            Full spine mural image.
        """
        from PIL import Image

        if not spine_strips:
            raise ValueError("spine_strips must not be empty")

        total_width = sum(s.width for s in spine_strips)
        height = spine_strips[0].height
        mural = Image.new("RGBA", (total_width, height), (255, 255, 255, 255))

        x_offset = 0
        for strip in spine_strips:
            mural.paste(strip.convert("RGBA"), (x_offset, 0))
            x_offset += strip.width

        return mural

    # ── Digital cover ───────────────────────────────────────────────────────

    def render_digital_cover(
        self,
        series_id: str,
        volume_number: int,
        market_code: str,
        output_dir: Path,
        *,
        target_format: str = "jpeg",
        jpeg_quality: int = 95,
        webp_quality: int = 90,
        force_regen: bool = False,
    ) -> Path:
        """
        Render digital storefront cover from print front cover.

        See specs/manga_cover_pipeline_integration.md §2.5 for full docstring.
        """
        from PIL import Image, ImageEnhance
        from phoenix_v4.manga.covers.cover_generator import FrontCoverMissingError

        if target_format not in ("jpeg", "webp"):
            raise ValueError(f"Unsupported target_format: {target_format!r}")

        vol_dir = output_dir / f"vol_{volume_number:03d}" / market_code
        ext = "jpg" if target_format == "jpeg" else "webp"
        out_path = vol_dir / f"digital_cover.{ext}"

        if out_path.exists() and not force_regen:
            return out_path

        front_path = vol_dir / "front.png"
        if not front_path.exists():
            raise FrontCoverMissingError(f"front.png required for digital render: {front_path}")

        with Image.open(front_path) as img:
            cover = img.convert("RGB")

        # Target: 1080x1920 (9:16)
        target_w, target_h = 1080, 1920
        cover_ratio = cover.width / cover.height
        digital_ratio = target_w / target_h

        if cover_ratio > digital_ratio:
            # Cover is wider than 9:16 — crop sides
            new_h = cover.height
            new_w = int(cover.height * digital_ratio)
            left = (cover.width - new_w) // 2
            cover = cover.crop((left, 0, left + new_w, new_h))
        elif cover_ratio < digital_ratio:
            # Cover is taller — crop bottom (preserve title at top)
            new_w = cover.width
            new_h = int(cover.width / digital_ratio)
            cover = cover.crop((0, 0, new_w, new_h))

        cover = cover.resize((target_w, target_h), Image.LANCZOS)

        # Boost saturation +8% for screen
        enhancer = ImageEnhance.Color(cover)
        cover = enhancer.enhance(1.08)

        if target_format == "jpeg":
            cover.save(out_path, format="JPEG", quality=jpeg_quality, optimize=True)
        else:
            cover.save(out_path, format="WEBP", quality=webp_quality, method=6)

        logger.info("Digital cover rendered: %s", out_path)
        return out_path

    # ── Market adaptations ──────────────────────────────────────────────────

    def _apply_market_adaptations(
        self,
        image: "PILImageModule.Image",
        market_code: str,
    ) -> "PILImageModule.Image":
        """
        Apply market-specific color and composition adjustments.

        Market adaptations:
        - CN: slight desaturation of red tones (regulatory sensitivity)
        - JP: no change (reference market)
        - US: no change for most genres
        - DE/FR/AU: no color changes, only typography adjustments (handled elsewhere)

        Args:
            image: RGBA cover image.
            market_code: Market code.

        Returns:
            Adjusted RGBA image.
        """
        from PIL import ImageEnhance

        if market_code == "CN":
            # Slight desaturation
            enhancer = ImageEnhance.Color(image.convert("RGB"))
            adjusted = enhancer.enhance(0.92)
            return adjusted.convert("RGBA")

        # All other markets: no color adjustment
        return image
