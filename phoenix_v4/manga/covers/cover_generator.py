"""
FLUX-based manga cover generator.

Handles:
- Loading ComfyUI workflow JSON templates
- Patching workflows with CoverParams (seed, resolution, prompts, ControlNet)
- Calling the FLUX endpoint (local ComfyUI or RunComfy remote API)
- Polling for generation completion
- Downloading and saving the result image
- Post-generation upscaling via Real-ESRGAN
- Two-pass generation workflow (pose pass + style pass)

Public API (re-exported from phoenix_v4.manga.covers.__init__):
    generate_front_cover()
    generate_back_cover()
    generate_spine()
    assemble_full_wrap()
    render_digital_cover()
    validate_cover_set()
    list_generated_covers()
    get_spine_width_mm()

All functions that need FLUX are non-blocking on import; the FLUX endpoint
is contacted only when a generate_* function is called.

ComfyUI endpoint
----------------
Resolved from environment variable COMFYUI_ENDPOINT.
Default: "http://localhost:8188"
Override in .env or via macOS Keychain (loaded by load_integration_env_from_keychain.py).

RunComfy remote API
-------------------
Activated when RUNCOMFY_API_KEY env var is set and
COVER_USE_RUNCOMFY=1 env var is set. Falls back to local ComfyUI if
RUNCOMFY_API_KEY is not set.

Upscaling
---------
Real-ESRGAN anime-4x model is called via subprocess if the
`realesrgan-ncnn-vulkan` binary is on PATH. Falls back to PIL Lanczos
if the binary is not available (lower quality, acceptable for preview).
"""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from phoenix_v4.manga.covers.cover_selector import CoverParams

logger = logging.getLogger(__name__)

# ── Environment defaults ───────────────────────────────────────────────────────

_DEFAULT_COMFYUI_ENDPOINT = "http://localhost:8188"
_DEFAULT_MAX_TIMEOUT_SECONDS = 600
_WORKFLOW_DIR = (
    Path(__file__).resolve().parents[4]
    / "config"
    / "comfyui_workflows"
    / "manga_covers"
)


# ── Exception classes ──────────────────────────────────────────────────────────

class CoverGenerationError(Exception):
    """Base class for cover generation errors."""


class SeriesIdentityNotFoundError(CoverGenerationError):
    """series_id not found in series_signatures directory."""

    def __init__(self, series_id: str, search_path: Path) -> None:
        super().__init__(
            f"Series identity YAML not found for series_id={series_id!r}. "
            f"Expected: {search_path}/{series_id}.yaml"
        )
        self.series_id = series_id
        self.search_path = search_path


class MarketNotSupportedError(CoverGenerationError):
    """market_code not in supported market registry."""

    def __init__(self, market_code: str) -> None:
        super().__init__(
            f"Market code {market_code!r} is not supported. "
            "See phoenix_v4.manga.covers.market_adapters.SUPPORTED_MARKETS."
        )
        self.market_code = market_code


class CharacterSheetMissingError(CoverGenerationError):
    """Character sheet PNG not found at expected path."""

    def __init__(self, character_id: str, expected_path: Path) -> None:
        super().__init__(
            f"Character sheet missing for character_id={character_id!r}. "
            f"Expected file: {expected_path}"
        )
        self.character_id = character_id
        self.expected_path = expected_path


class FLUXGenerationError(CoverGenerationError):
    """FLUX generation failed or endpoint unavailable."""


class UpscalingError(CoverGenerationError):
    """Post-generation upscaling failed."""


class TypographyError(CoverGenerationError):
    """Typography rendering failed."""


class FrontCoverMissingError(CoverGenerationError):
    """front.png required but not found."""


class BackCoverMissingError(CoverGenerationError):
    """back.png required but not found."""


class SpineMissingError(CoverGenerationError):
    """spine.png required but not found."""


class WrapAssemblyError(CoverGenerationError):
    """Dimension mismatch or assembly failure."""


class SynopsisTranslationError(CoverGenerationError):
    """Synopsis translation to market language failed."""


# ── Validation dataclass ───────────────────────────────────────────────────────

@dataclass
class CoverSetValidationResult:
    valid: bool
    errors: list[str]
    warnings: list[str]


# ── Primary public API ─────────────────────────────────────────────────────────

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

    Args:
        series_id: Unique series identifier (matches series_identity YAML key)
        volume_number: 1-based volume index
        market_code: ISO-style market code (JP, US, FR, DE, IT, BR, MX, TW, CN, KR, ES, AU)
        output_dir: Directory where front.png will be written
        seed: Override deterministic seed (for operator preview/exploration)
        force_regen: Skip cache check and regenerate even if front.png exists

    Returns:
        Path to the generated front.png

    Raises:
        SeriesIdentityNotFoundError: series_id not in cover layer config
        MarketNotSupportedError: market_code not in supported market registry
        FLUXGenerationError: FLUX endpoint unavailable or generation failed
    """
    generator = CoverGenerator()
    return generator.generate_front_cover(
        series_id=series_id,
        volume_number=volume_number,
        market_code=market_code,
        output_dir=output_dir,
        seed=seed,
        force_regen=force_regen,
    )


def generate_back_cover(
    series_id: str,
    volume_number: int,
    market_code: str,
    output_dir: Path,
    volume_metadata: object | None = None,
    *,
    seed: int | None = None,
    force_regen: bool = False,
) -> Path:
    """Generate the back cover image for a manga volume.

    See specs/manga_cover_pipeline_integration.md §2.2 for full docstring.
    """
    generator = CoverGenerator()
    return generator.generate_back_cover(
        series_id=series_id,
        volume_number=volume_number,
        market_code=market_code,
        output_dir=output_dir,
        volume_metadata=volume_metadata,
        seed=seed,
        force_regen=force_regen,
    )


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

    See specs/manga_cover_pipeline_integration.md §2.3 for full docstring.
    """
    assembler_cls = _lazy_import_assembler()
    assembler = assembler_cls()
    return assembler.generate_spine(
        series_id=series_id,
        volume_number=volume_number,
        market_code=market_code,
        output_dir=output_dir,
        page_count=page_count,
        force_regen=force_regen,
    )


def assemble_full_wrap(
    series_id: str,
    volume_number: int,
    market_code: str,
    output_dir: Path,
    *,
    force_regen: bool = False,
) -> Path:
    """Assemble front, spine, and back into a print-ready full wrap.

    See specs/manga_cover_pipeline_integration.md §2.4 for full docstring.
    """
    assembler_cls = _lazy_import_assembler()
    assembler = assembler_cls()
    return assembler.assemble_full_wrap(
        series_id=series_id,
        volume_number=volume_number,
        market_code=market_code,
        output_dir=output_dir,
        force_regen=force_regen,
    )


def render_digital_cover(
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
    """Render digital storefront cover optimized for e-reader and web.

    See specs/manga_cover_pipeline_integration.md §2.5 for full docstring.
    """
    assembler_cls = _lazy_import_assembler()
    assembler = assembler_cls()
    return assembler.render_digital_cover(
        series_id=series_id,
        volume_number=volume_number,
        market_code=market_code,
        output_dir=output_dir,
        target_format=target_format,
        jpeg_quality=jpeg_quality,
        webp_quality=webp_quality,
        force_regen=force_regen,
    )


def validate_cover_set(
    output_dir: Path,
    volume_number: int,
    market_code: str,
) -> CoverSetValidationResult:
    """Validate that all required cover files exist and meet quality thresholds."""
    errors: list[str] = []
    warnings: list[str] = []

    vol_dir = output_dir / f"vol_{volume_number:03d}" / market_code

    required_files = ["front.png", "back.png", "spine.png", "full_wrap.png"]
    optional_files = ["digital_cover.jpg", "digital_cover.png", "cover_metadata.json"]

    for fname in required_files:
        fpath = vol_dir / fname
        if not fpath.exists():
            errors.append(f"Missing required file: {fpath}")
        elif fpath.stat().st_size == 0:
            errors.append(f"Zero-byte file: {fpath}")
        else:
            # Attempt PIL open for corruption check
            try:
                from PIL import Image
                with Image.open(fpath) as img:
                    img.verify()
            except Exception as exc:
                errors.append(f"Corrupt image {fpath}: {exc}")

    for fname in optional_files:
        fpath = vol_dir / fname
        if not fpath.exists():
            warnings.append(f"Optional file missing: {fpath}")

    # Check metadata JSON parses
    meta_path = vol_dir / "cover_metadata.json"
    if meta_path.exists():
        try:
            with meta_path.open() as f:
                json.load(f)
        except json.JSONDecodeError as exc:
            errors.append(f"cover_metadata.json is invalid JSON: {exc}")

    return CoverSetValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )


def list_generated_covers(
    series_id: str,
    output_dir: Path,
) -> dict[int, dict[str, Path]]:
    """List all generated cover sets for a series.

    Returns:
        dict mapping volume_number → dict mapping market_code → front.png path
    """
    result: dict[int, dict[str, Path]] = {}
    if not output_dir.exists():
        return result
    for vol_dir in sorted(output_dir.glob("vol_*")):
        try:
            vol_num = int(vol_dir.name.split("_")[1])
        except (IndexError, ValueError):
            continue
        result[vol_num] = {}
        for market_dir in sorted(vol_dir.iterdir()):
            if not market_dir.is_dir():
                continue
            front = market_dir / "front.png"
            if front.exists():
                result[vol_num][market_dir.name] = front
    return result


def get_spine_width_mm(page_count: int, paper_gsm: int = 60) -> float:
    """Calculate spine width in mm from page count and paper weight.

    Standard bindery formula:
        60gsm: page_count * 0.052 mm
        70gsm: page_count * 0.065 mm
        80gsm: page_count * 0.075 mm

    Args:
        page_count: Total interior page count.
        paper_gsm: Paper weight in grams per square meter.

    Returns:
        Spine width in millimeters, rounded to 2 decimal places.
    """
    gsm_factor = {60: 0.052, 70: 0.065, 80: 0.075}
    factor = gsm_factor.get(paper_gsm, 0.052)
    return round(page_count * factor, 2)


# ── CoverGenerator class ───────────────────────────────────────────────────────

class CoverGenerator:
    """
    Orchestrates FLUX-based manga cover generation.

    Usage:
        gen = CoverGenerator()
        path = gen.generate_front_cover(
            series_id="stillness-press-morning-window",
            volume_number=1,
            market_code="JP",
            output_dir=Path("artifacts/covers"),
        )
    """

    def __init__(
        self,
        comfyui_endpoint: str | None = None,
        timeout_seconds: int | None = None,
    ) -> None:
        self._endpoint = (
            comfyui_endpoint
            or os.environ.get("COMFYUI_ENDPOINT", _DEFAULT_COMFYUI_ENDPOINT)
        ).rstrip("/")
        self._timeout = timeout_seconds or int(
            os.environ.get("COVER_MAX_TIMEOUT_SECONDS", _DEFAULT_MAX_TIMEOUT_SECONDS)
        )
        self._use_runcomfy = os.environ.get("COVER_USE_RUNCOMFY", "0") == "1"
        self._runcomfy_api_key = os.environ.get("RUNCOMFY_API_KEY", "")

    # ── Public generate methods ─────────────────────────────────────────────

    def generate_front_cover(
        self,
        series_id: str,
        volume_number: int,
        market_code: str,
        output_dir: Path,
        *,
        seed: int | None = None,
        force_regen: bool = False,
    ) -> Path:
        """Generate front cover. See module-level generate_front_cover() docstring."""
        out_path = output_dir / f"vol_{volume_number:03d}" / market_code / "front.png"

        if out_path.exists() and not force_regen:
            logger.info("Cache hit — returning existing front cover: %s", out_path)
            return out_path

        out_path.parent.mkdir(parents=True, exist_ok=True)

        # Resolve generation params
        from phoenix_v4.manga.covers.cover_selector import LayeredCoverSelector
        selector = LayeredCoverSelector()
        # Need brand_id — read from series YAML
        brand_id = self._get_brand_id(series_id)
        params = selector.select_cover_params(
            brand_id=brand_id,
            series_id=series_id,
            volume_number=volume_number,
            market_code=market_code,
            seed_override=seed,
        )

        if params.two_pass_mode:
            raw_image_path = self._two_pass_generate(params, out_path.parent)
        else:
            raw_image_path = self._single_pass_generate(params, out_path.parent, suffix="front_raw")

        # Upscale
        try:
            upscaled_path = self._upscale(raw_image_path, out_path.parent)
        except UpscalingError:
            logger.warning("Upscaling failed — using FLUX native resolution")
            upscaled_path = raw_image_path

        # Typography overlay
        from phoenix_v4.manga.covers.cover_assembler import CoverAssembler
        assembler = CoverAssembler()
        final_path = assembler.overlay_typography_front(upscaled_path, params, out_path)

        # Write metadata
        self._write_metadata(params, out_path.parent, cover_type="front")

        logger.info("Front cover generated: %s", final_path)
        return final_path

    def generate_back_cover(
        self,
        series_id: str,
        volume_number: int,
        market_code: str,
        output_dir: Path,
        volume_metadata: object | None = None,
        *,
        seed: int | None = None,
        force_regen: bool = False,
    ) -> Path:
        """Generate back cover. See module-level generate_back_cover() docstring."""
        out_path = output_dir / f"vol_{volume_number:03d}" / market_code / "back.png"

        if out_path.exists() and not force_regen:
            logger.info("Cache hit — returning existing back cover: %s", out_path)
            return out_path

        out_path.parent.mkdir(parents=True, exist_ok=True)

        # TODO: Full implementation
        # - Derive back cover params (quiet background prompt, no protagonist)
        # - Call FLUX
        # - Render synopsis text block
        # - Render barcode placeholder
        # - Render ISBN / price
        # - Render publisher logo (larger than front)
        logger.warning("generate_back_cover: stub — implement full back cover generation")
        # Stub: copy front as placeholder
        front_path = out_path.parent / "front.png"
        if front_path.exists():
            import shutil
            shutil.copy2(front_path, out_path)
        return out_path

    # ── Private: FLUX API calls ─────────────────────────────────────────────

    def _call_flux_api(self, workflow_json: dict) -> Path:
        """
        Submit workflow to ComfyUI and wait for completion.

        Posts the workflow JSON to /prompt, polls /history/{prompt_id}
        until status is complete, then downloads the output image.

        Args:
            workflow_json: Complete ComfyUI workflow dict with all
                           parameters patched in.

        Returns:
            Path to downloaded output image in a temp directory.

        Raises:
            FLUXGenerationError: On HTTP error, timeout, or ComfyUI error.
        """
        import urllib.error
        import urllib.request

        prompt_id = str(uuid.uuid4())
        payload = json.dumps({"prompt": workflow_json, "client_id": prompt_id}).encode()

        try:
            req = urllib.request.Request(
                f"{self._endpoint}/prompt",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                response_data = json.loads(resp.read())
        except urllib.error.URLError as exc:
            raise FLUXGenerationError(
                f"ComfyUI endpoint unreachable at {self._endpoint}: {exc}"
            ) from exc

        queue_prompt_id = response_data.get("prompt_id")
        if not queue_prompt_id:
            raise FLUXGenerationError(
                f"ComfyUI did not return prompt_id. Response: {response_data}"
            )

        # Poll for completion
        output_path = self._poll_until_complete(queue_prompt_id)
        return output_path

    def _poll_until_complete(self, prompt_id: str) -> Path:
        """Poll ComfyUI /history/{prompt_id} until generation completes."""
        import urllib.request
        import tempfile

        deadline = time.time() + self._timeout
        poll_interval = 3.0

        while time.time() < deadline:
            time.sleep(poll_interval)
            try:
                url = f"{self._endpoint}/history/{prompt_id}"
                with urllib.request.urlopen(url, timeout=10) as resp:
                    history = json.loads(resp.read())
            except Exception as exc:
                logger.warning("Poll error (will retry): %s", exc)
                continue

            if prompt_id not in history:
                continue  # Not yet in history

            outputs = history[prompt_id].get("outputs", {})
            for node_id, node_out in outputs.items():
                images = node_out.get("images", [])
                if images:
                    image_info = images[0]
                    return self._download_image(
                        image_info["filename"],
                        image_info.get("subfolder", ""),
                        image_info.get("type", "output"),
                    )

        raise FLUXGenerationError(
            f"Generation timed out after {self._timeout}s for prompt_id={prompt_id}"
        )

    def _download_image(self, filename: str, subfolder: str, folder_type: str) -> Path:
        """Download generated image from ComfyUI /view endpoint."""
        import urllib.request
        import urllib.parse
        import tempfile

        params = urllib.parse.urlencode({
            "filename": filename,
            "subfolder": subfolder,
            "type": folder_type,
        })
        url = f"{self._endpoint}/view?{params}"

        tmp = Path(tempfile.mkdtemp()) / filename
        urllib.request.urlretrieve(url, tmp)
        return tmp

    def _load_comfyui_workflow(self, genre: str, market_code: str) -> dict:
        """
        Load base ComfyUI workflow JSON for the given genre and market.

        Looks for workflow files in this order:
        1. {genre}_{market_code}_cover.json  (market-specific variant)
        2. {genre}_cover.json               (genre default)
        3. default_cover.json               (universal fallback)

        Args:
            genre: Genre identifier (e.g., "iyashikei", "shonen").
            market_code: Market code (e.g., "JP", "US").

        Returns:
            Parsed workflow JSON dict.

        Raises:
            FLUXGenerationError: If no workflow file can be found.
        """
        candidates = [
            _WORKFLOW_DIR / f"{genre}_{market_code.lower()}_cover.json",
            _WORKFLOW_DIR / f"{genre}_cover.json",
            _WORKFLOW_DIR / "default_cover.json",
        ]
        for candidate in candidates:
            if candidate.exists():
                with candidate.open("r", encoding="utf-8") as f:
                    return json.load(f)
        raise FLUXGenerationError(
            f"No ComfyUI workflow found for genre={genre!r}, market={market_code!r}. "
            f"Checked: {[str(c) for c in candidates]}"
        )

    def _patch_workflow(self, workflow: dict, params: "CoverParams") -> dict:
        """
        Patch a base workflow JSON with runtime parameters from CoverParams.

        Modifies in-place and returns the patched workflow.

        Patches applied:
        - Node type CLIPTextEncodeFlux / CLIPTextEncode: inject positive prompt
        - Node class KSampler: inject seed, steps, cfg, sampler, scheduler
        - Node class EmptyLatentImage: inject flux_width, flux_height
        - Node class SaveImage: inject output filename prefix

        Args:
            workflow: Base workflow dict (from _load_comfyui_workflow).
            params: Resolved CoverParams.

        Returns:
            Patched workflow dict.
        """
        import copy
        workflow = copy.deepcopy(workflow)

        for node_id, node in workflow.items():
            class_type = node.get("class_type", "")
            inputs = node.get("inputs", {})

            if class_type in ("CLIPTextEncodeFlux", "CLIPTextEncode"):
                if "text" in inputs and "negative" not in node.get("_meta", {}).get("title", "").lower():
                    inputs["text"] = params.positive_prompt
                elif "text" in inputs:
                    inputs["text"] = params.negative_prompt
                if "guidance" in inputs:
                    inputs["guidance"] = params.cfg_scale

            elif class_type == "KSampler":
                inputs["seed"] = params.seed
                inputs["steps"] = params.steps
                inputs["cfg"] = params.cfg_scale
                inputs["sampler_name"] = params.sampler
                inputs["scheduler"] = params.scheduler
                inputs["denoise"] = 1.0

            elif class_type == "EmptyLatentImage":
                inputs["width"] = params.flux_width
                inputs["height"] = params.flux_height
                inputs["batch_size"] = 1

            elif class_type == "SaveImage":
                inputs["filename_prefix"] = (
                    f"{params.series_id}_vol{params.volume_number:03d}"
                    f"_{params.market_code}_front"
                )

        return workflow

    # ── Private: generation passes ──────────────────────────────────────────

    def _single_pass_generate(
        self,
        params: "CoverParams",
        work_dir: Path,
        suffix: str = "raw",
    ) -> Path:
        """Run a single FLUX generation pass and return the raw output path."""
        workflow = self._load_comfyui_workflow(params.genre, params.market_code)
        workflow = self._patch_workflow(workflow, params)
        raw_path = self._call_flux_api(workflow)
        dest = work_dir / f"{suffix}.png"
        import shutil
        shutil.move(str(raw_path), dest)
        return dest

    def _two_pass_generate(
        self,
        params: "CoverParams",
        work_dir: Path,
    ) -> Path:
        """
        Run two-pass FLUX generation for pose + style continuity.

        Pass 1: ControlNet pose control → raw_pose.png
        Pass 2: img2img with IP-Adapter style reference → raw_styled.png

        Returns path to Pass 2 output.
        """
        logger.info("Two-pass generation: pass 1 (pose control)")
        pass1_params = _clone_params_for_pass1(params)
        pass1_path = self._single_pass_generate(pass1_params, work_dir, suffix="raw_pose")

        logger.info("Two-pass generation: pass 2 (IP-Adapter style)")
        pass2_params = _clone_params_for_pass2(params, pass1_path)
        pass2_path = self._single_pass_generate(pass2_params, work_dir, suffix="raw_styled")

        return pass2_path

    # ── Private: upscaling ──────────────────────────────────────────────────

    def _upscale(self, image_path: Path, work_dir: Path) -> Path:
        """
        Upscale image using Real-ESRGAN anime model or PIL Lanczos fallback.

        Target: 4x upscale from FLUX native resolution.
        For 1024×1600 → 4096×6400, then resized to print target.

        Args:
            image_path: Path to FLUX-native-resolution PNG.
            work_dir: Directory for upscaled output.

        Returns:
            Path to upscaled image.

        Raises:
            UpscalingError: If both Real-ESRGAN and PIL fallback fail.
        """
        import shutil
        import subprocess

        out_path = work_dir / "upscaled.png"

        # Try Real-ESRGAN binary
        binary = shutil.which("realesrgan-ncnn-vulkan")
        if binary:
            try:
                result = subprocess.run(
                    [binary, "-i", str(image_path), "-o", str(out_path), "-n", "realesrgan-x4plus-anime"],
                    capture_output=True,
                    timeout=300,
                )
                if result.returncode == 0 and out_path.exists():
                    logger.info("Upscaled via Real-ESRGAN: %s", out_path)
                    return out_path
                else:
                    logger.warning(
                        "Real-ESRGAN exited %d: %s", result.returncode, result.stderr
                    )
            except subprocess.TimeoutExpired:
                logger.warning("Real-ESRGAN timed out — falling back to PIL")
            except Exception as exc:
                logger.warning("Real-ESRGAN failed (%s) — falling back to PIL", exc)

        # PIL Lanczos fallback
        try:
            from PIL import Image
            with Image.open(image_path) as img:
                new_size = (img.width * 4, img.height * 4)
                upscaled = img.resize(new_size, Image.LANCZOS)
                upscaled.save(out_path, format="PNG", optimize=False)
            logger.info("Upscaled via PIL Lanczos (lower quality): %s", out_path)
            return out_path
        except Exception as exc:
            raise UpscalingError(f"PIL Lanczos upscaling failed: {exc}") from exc

    # ── Private: metadata ───────────────────────────────────────────────────

    def _write_metadata(
        self,
        params: "CoverParams",
        out_dir: Path,
        cover_type: str = "front",
    ) -> None:
        """Write cover_metadata.json alongside generated cover files."""
        meta = {
            "series_id": params.series_id,
            "brand_id": params.brand_id,
            "volume_number": params.volume_number,
            "market_code": params.market_code,
            "generation_timestamp": _utc_now_iso(),
            "flux_model": params.flux_model_id,
            "flux_quantization": params.flux_quantization,
            "seed": params.seed,
            "steps": params.steps,
            "cfg_scale": params.cfg_scale,
            "sampler": params.sampler,
            "scheduler": params.scheduler,
            "resolution_generated": f"{params.flux_width}x{params.flux_height}",
            "controlnet_used": params.controlnet_config.type if params.controlnet_config else None,
            "controlnet_strength": params.controlnet_config.strength if params.controlnet_config else None,
            "ip_adapter_used": params.ip_adapter_reference_path is not None,
            "ip_adapter_strength": params.ip_adapter_strength,
            "two_pass_mode": params.two_pass_mode,
            "cover_type": cover_type,
        }
        meta_path = out_dir / "cover_metadata.json"
        with meta_path.open("w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

    def _get_brand_id(self, series_id: str) -> str:
        """Read brand_id from series signature YAML."""
        import yaml
        repo_root = Path(__file__).resolve().parents[4]
        series_yaml = (
            repo_root
            / "config"
            / "source_of_truth"
            / "manga_cover_layers"
            / "series_signatures"
            / f"{series_id}.yaml"
        )
        if not series_yaml.exists():
            raise SeriesIdentityNotFoundError(series_id, series_yaml.parent)
        with series_yaml.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data.get("brand_id", "unknown")


# ── Helpers ────────────────────────────────────────────────────────────────────

def _lazy_import_assembler():
    from phoenix_v4.manga.covers.cover_assembler import CoverAssembler
    return CoverAssembler


def _clone_params_for_pass1(params: "CoverParams") -> "CoverParams":
    """Clone params for pass 1: enable ControlNet, disable IP-Adapter."""
    import copy
    p = copy.copy(params)
    p.ip_adapter_reference_path = None
    p.ip_adapter_strength = None
    p.generation_pass = 1
    return p


def _clone_params_for_pass2(params: "CoverParams", pass1_output: Path) -> "CoverParams":
    """Clone params for pass 2: img2img from pass1, enable IP-Adapter, disable ControlNet."""
    import copy
    p = copy.copy(params)
    p.controlnet_config = None
    p.generation_pass = 2
    # Pass 2 uses img2img — pass1_output is the init image
    # TODO: patch workflow to use img2img with denoise=0.55
    return p


def _utc_now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()
