"""Image generation backends: noop, fixture replay (CI), and RunComfy (live)."""

from __future__ import annotations

import hashlib
import json
import logging
import os
from pathlib import Path
from collections.abc import Mapping
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
        """Generate images for all panels via RunComfy API (or dry-run)."""
        from scripts.image_generation.prompt_compiler import compile_panel_prompt
        from scripts.image_generation.image_qc import run_panel_qc

        panels = list(panel_prompts.get("panels") or [])
        results: list[dict[str, Any]] = []
        for p in panels:
            pid = str(p["panel_id"])
            try:
                compiled = compile_panel_prompt(p)
                if self.dry_run:
                    results.append({
                        "panel_id": pid,
                        "status": "dry_run",
                        "path": None,
                        "width": 0,
                        "height": 0,
                        "compiled_prompt": compiled,
                    })
                    continue

                # Submit to RunComfy API
                image_path = self._generate_single(pid, compiled)

                # Run QC gates
                qc = run_panel_qc(image_path)
                if not qc["passed"]:
                    logger.warning("QC failed for panel %s: %s", pid, qc["checks"])
                    results.append({
                        "panel_id": pid,
                        "status": "failed",
                        "path": str(image_path),
                        "width": qc.get("width", 0),
                        "height": qc.get("height", 0),
                        "qc_checks": qc["checks"],
                    })
                    continue

                results.append({
                    "panel_id": pid,
                    "status": "ok",
                    "path": str(image_path),
                    "width": qc["width"],
                    "height": qc["height"],
                    "content_sha256": _sha256_file(image_path),
                })
            except Exception as exc:
                logger.error("Panel %s generation failed: %s", pid, exc)
                results.append({
                    "panel_id": pid,
                    "status": "failed",
                    "path": None,
                    "width": 0,
                    "height": 0,
                    "error": str(exc)[:500],
                })
        return results

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _generate_single(self, panel_id: str, compiled: dict[str, str]) -> Path:
        """Submit one panel to RunComfy, poll, download, return local path."""
        from scripts.image_generation.runcomfy_batch import (
            download_image,
            extract_image_url,
            load_workflow,
            poll_run,
            submit_workflow,
        )

        if not self.api_key:
            raise RuntimeError("RUNCOMFY_API_KEY is not set")

        workflow = load_workflow(self.workflow_path)
        # Inject prompt placeholders into workflow
        workflow_str = json.dumps(workflow)
        workflow_str = workflow_str.replace("{{positive_prompt}}", compiled["positive"])
        workflow_str = workflow_str.replace("{{negative_prompt}}", compiled["negative"])
        workflow_str = workflow_str.replace("{{width}}", "512")
        workflow_str = workflow_str.replace("{{height}}", "512")
        workflow_str = workflow_str.replace("{{seed}}", "42")
        workflow_str = workflow_str.replace("{{guidance}}", "3.5")
        injected = json.loads(workflow_str)

        run_id = submit_workflow(self.api_key, self.deployment_id, injected)
        result = poll_run(self.api_key, self.deployment_id, run_id)
        image_url = extract_image_url(result)
        if not image_url:
            raise RuntimeError(f"No image URL in RunComfy result for panel {panel_id}")

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
