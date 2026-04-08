"""Image generation backends: noop, fixture replay (CI), and RunComfy (live)."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from collections.abc import Mapping
from threading import Semaphore
from typing import Any, Protocol, runtime_checkable

logger = logging.getLogger(__name__)


@runtime_checkable
class ImageBackend(Protocol):
    """Generate or stub panel images from a panel_prompts artifact."""

    def generate(self, panel_prompts: Mapping[str, Any]) -> list[dict[str, Any]]:
        """Return one result dict per panel (panel_id, status, path?, dimensions, hash?)."""
        ...


class NoopImageBackend:
    """No files written — every panel stays ``pending`` (layout/QC wiring later)."""

    def generate(self, panel_prompts: Mapping[str, Any]) -> list[dict[str, Any]]:
        return [
            {
                "panel_id": p["panel_id"],
                "status": "pending",
                "path": None,
                "width": 0,
                "height": 0,
            }
            for p in panel_prompts.get("panels") or []
        ]


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


class FixtureReplayImageBackend:
    """Map panel_id → image path; emits ok + dimensions + sha256 when file exists."""

    def __init__(self, mapping: dict[str, Path]) -> None:
        self._mapping = {k: Path(v).resolve() for k, v in mapping.items()}

    @classmethod
    def from_json_file(cls, path: Path) -> FixtureReplayImageBackend:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("Replay mapping must be a JSON object of panel_id -> path")
        base = path.parent.resolve()
        out: dict[str, Path] = {}
        for pid, rel in data.items():
            p = Path(rel)
            out[str(pid)] = (base / p).resolve() if not p.is_absolute() else p
        return cls(out)

    def generate(self, panel_prompts: Mapping[str, Any]) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for p in panel_prompts.get("panels") or []:
            pid = str(p["panel_id"])
            file_path = self._mapping.get(pid)
            if file_path is None or not file_path.is_file():
                results.append(
                    {
                        "panel_id": pid,
                        "status": "pending",
                        "path": None,
                        "width": 0,
                        "height": 0,
                    }
                )
                continue
            # Minimal dimensions: skip PIL; use 1x1 for unknown or read PNG header if needed
            width, height = _png_dimensions_if_simple(file_path)
            results.append(
                {
                    "panel_id": pid,
                    "status": "ok",
                    "path": str(file_path),
                    "width": width,
                    "height": height,
                    "content_sha256": _sha256_file(file_path),
                }
            )
        return results


def _png_dimensions_if_simple(path: Path) -> tuple[int, int]:
    """Read width/height from PNG IHDR without Pillow."""
    data = path.read_bytes()
    if len(data) >= 24 and data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR":
        w = int.from_bytes(data[16:20], "big")
        h = int.from_bytes(data[20:24], "big")
        return w, h
    return 512, 512


class RunComfyImageBackend:
    """Submit panels to RunComfy serverless API and run QC on results.

    Parameters
    ----------
    deployment_id : str
        RunComfy deployment ID. Falls back to RUNCOMFY_DEPLOYMENT_ID env var,
        then to the hardcoded default.
    api_key : str | None
        RunComfy API key. If *None*, reads from RUNCOMFY_API_KEY env var.
    workflow_path : Path | str | None
        Path to ComfyUI workflow JSON template. Defaults to the bundled
        ``scripts/image_generation/comfyui_workflows/flux_video_bank.json``.
    output_dir : Path | str | None
        Directory for downloaded panel images. Defaults to cwd / ``panel_images``.
    dry_run : bool
        Compile prompts but skip API calls. Every panel returns status ``dry_run``.
    """

    _DEFAULT_DEPLOYMENT = "677edba8-ace0-4b2b-bad2-8e94b9959065"
    _SUBMIT_SPACING_S = 2.0   # seconds between API submissions
    _MAX_PANEL_RETRIES = 3
    _RETRY_BASE_S = 2.0       # base backoff for retries (doubles each attempt)
    _MAX_CONCURRENT = 4        # parallel API submissions

    def __init__(
        self,
        deployment_id: str | None = None,
        api_key: str | None = None,
        workflow_path: Path | str | None = None,
        output_dir: Path | str | None = None,
        dry_run: bool = False,
    ) -> None:
        self.deployment_id = (
            deployment_id
            or os.environ.get("RUNCOMFY_DEPLOYMENT_ID", "").strip()
            or self._DEFAULT_DEPLOYMENT
        )
        self.api_key = api_key or os.environ.get("RUNCOMFY_API_KEY", "").strip()
        if workflow_path is None:
            self.workflow_path = (
                Path(__file__).resolve().parent.parent.parent
                / "scripts"
                / "image_generation"
                / "comfyui_workflows"
                / "flux_video_bank.json"
            )
        else:
            self.workflow_path = Path(workflow_path)
        self.output_dir = Path(output_dir) if output_dir else Path.cwd() / "panel_images"
        self.dry_run = dry_run

    # ------------------------------------------------------------------
    # ImageBackend protocol
    # ------------------------------------------------------------------

    def generate(self, panel_prompts: Mapping[str, Any]) -> list[dict[str, Any]]:
        """Generate images for all panels via RunComfy API (or dry-run).

        Submits up to ``_MAX_CONCURRENT`` panels in parallel, with
        ``_SUBMIT_SPACING_S`` between each submission (via semaphore) and
        retries each panel up to ``_MAX_PANEL_RETRIES`` times.
        """
        from scripts.image_generation.prompt_compiler import compile_panel_prompt
        from scripts.image_generation.image_qc import run_panel_qc

        panels = list(panel_prompts.get("panels") or [])
        total = len(panels)

        # Fast path: dry-run (no API calls, no threading)
        if self.dry_run:
            return [
                {
                    "panel_id": str(p["panel_id"]),
                    "status": "dry_run",
                    "path": None,
                    "width": 0,
                    "height": 0,
                    "compiled_prompt": compile_panel_prompt(p),
                }
                for p in panels
            ]

        rate_sem = Semaphore(1)  # serializes the spacing delay

        def _process_one(idx: int, p: dict[str, Any]) -> dict[str, Any]:
            pid = str(p["panel_id"])
            try:
                compiled = compile_panel_prompt(p)

                # Rate-limit: only one thread enters the submit window at a time
                with rate_sem:
                    if idx > 0:
                        time.sleep(self._SUBMIT_SPACING_S)

                # Retry loop
                image_path: Path | None = None
                last_err = ""
                for attempt in range(self._MAX_PANEL_RETRIES):
                    try:
                        image_path = self._generate_single(pid, compiled)
                        break
                    except Exception as retry_exc:
                        last_err = str(retry_exc)[:500]
                        wait = self._RETRY_BASE_S * (2 ** attempt)
                        logger.warning(
                            "Panel %s attempt %d/%d failed: %s — retrying in %.0fs",
                            pid, attempt + 1, self._MAX_PANEL_RETRIES,
                            last_err[:100], wait,
                        )
                        time.sleep(wait)

                if image_path is None:
                    return {"panel_id": pid, "status": "failed", "path": None,
                            "width": 0, "height": 0, "error": last_err}

                qc = run_panel_qc(image_path)
                if not qc["passed"]:
                    logger.warning("QC failed for panel %s: %s", pid, qc["checks"])
                    return {"panel_id": pid, "status": "failed",
                            "path": str(image_path),
                            "width": qc.get("width", 0),
                            "height": qc.get("height", 0),
                            "qc_checks": qc["checks"]}

                logger.info("Panel %s done (%d/%d)", pid, idx + 1, total)
                return {"panel_id": pid, "status": "ok",
                        "path": str(image_path),
                        "width": qc["width"], "height": qc["height"],
                        "content_sha256": _sha256_file(image_path)}

            except Exception as exc:
                logger.error("Panel %s generation failed: %s", pid, exc)
                return {"panel_id": pid, "status": "failed", "path": None,
                        "width": 0, "height": 0, "error": str(exc)[:500]}

        workers = max(1, self._MAX_CONCURRENT)
        if workers <= 1:
            # Sequential mode (used in tests and single-panel runs)
            return [_process_one(idx, p) for idx, p in enumerate(panels)]

        # Parallel execution — submissions are rate-limited by the semaphore,
        # but polling/downloading runs concurrently across panels.
        result_map: dict[str, dict[str, Any]] = {}
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {
                pool.submit(_process_one, idx, p): str(p["panel_id"])
                for idx, p in enumerate(panels)
            }
            for future in as_completed(futures):
                pid = futures[future]
                result_map[pid] = future.result()

        # Return in original panel order
        return [result_map[str(p["panel_id"])] for p in panels]

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _generate_single(self, panel_id: str, compiled: dict[str, str]) -> Path:
        """Submit one panel to RunComfy via overrides, poll, download."""
        from scripts.image_generation.runcomfy_batch import (
            download_image,
            extract_image_url,
            get_result,
            poll_request,
            submit_inference,
        )

        if not self.api_key:
            raise RuntimeError("RUNCOMFY_API_KEY is not set")

        # Submit via overrides (node 6 = positive prompt, node 3 = seed)
        resp = submit_inference(
            api_key=self.api_key,
            deployment_id=self.deployment_id,
            positive_prompt=compiled["positive"],
            seed=hash(panel_id) % (2**31),
        )

        from scripts.image_generation.runcomfy_batch import _RUNCOMFY_API_BASE

        status_url = resp.get("status_url", "")
        result_url = resp.get("result_url", "")
        request_id = resp.get("request_id", resp.get("run_id", ""))
        # Construct URLs from request_id if the API didn't return them directly
        if not status_url and request_id:
            status_url = f"{_RUNCOMFY_API_BASE}/deployments/{self.deployment_id}/requests/{request_id}/status"
        if not result_url and request_id:
            result_url = f"{_RUNCOMFY_API_BASE}/deployments/{self.deployment_id}/requests/{request_id}/result"
        if not status_url:
            raise RuntimeError(f"No status_url or request_id in submit response: {resp}")

        # Poll until completed
        poll_result = poll_request(self.api_key, status_url, max_wait=300)

        # Get final result with image URLs
        if result_url:
            final = get_result(self.api_key, result_url)
        else:
            final = poll_result

        # Extract image URL
        image_url = extract_image_url(final)
        if not image_url:
            # Try outputs as list
            outputs = final.get("outputs", [])
            if isinstance(outputs, list) and outputs:
                first = outputs[0]
                image_url = first if isinstance(first, str) else first.get("url", "")
            if not image_url:
                raise RuntimeError(f"No image URL for panel {panel_id}: {final}")

        self.output_dir.mkdir(parents=True, exist_ok=True)
        dest = self.output_dir / f"{panel_id}.png"
        download_image(image_url, dest)
        return dest


def build_panel_images_manifest(
    panel_prompts: Mapping[str, Any],
    generation_results: list[dict[str, Any]],
    *,
    schema_version: str = "1.0.0",
) -> dict[str, Any]:
    """Merge panel_prompts with backend results into panel_images_manifest artifact."""
    by_id = {str(r["panel_id"]): r for r in generation_results}
    panels: list[dict[str, Any]] = []
    for p in panel_prompts.get("panels") or []:
        pid = str(p["panel_id"])
        r = by_id.get(pid, {})
        status = str(r.get("status", "pending"))
        entry: dict[str, Any] = {"panel_id": pid, "status": status}
        path = r.get("path")
        if path:
            entry["path"] = path
        w = int(r.get("width") or 0)
        h = int(r.get("height") or 0)
        if status == "ok" and w > 0 and h > 0:
            entry["width"] = w
            entry["height"] = h
        sha = r.get("content_sha256")
        if sha:
            entry["content_sha256"] = sha
        panels.append(entry)
    return {
        "schema_version": schema_version,
        "artifact_type": "panel_images_manifest",
        "panels": panels,
    }
