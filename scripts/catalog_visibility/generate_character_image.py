#!/usr/bin/env python3
"""Generate a main character image via RunComfy and write path into manga_series_index.json.

Uses the same Serverless API as scripts/image_generation/runcomfy_batch.py:
  POST https://api.runcomfy.net/prod/v1/deployments/{deployment_id}/inference

Auth: Bearer $RUNCOMFY_API_KEY (or $RUNCOMFY_TOKEN if API key unset).

Workflow template reference (local): config/comfyui_workflows/manga_covers/flux_character_portrait_template.json
Runtime submission uses deployment overrides (positive prompt), not raw workflow upload.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

DEFAULT_INDEX = REPO_ROOT / "artifacts" / "catalog_visibility" / "manga_series_index.json"
DEFAULT_OUT_ROOT = REPO_ROOT / "assets" / "manga_catalog"

_DEFAULT_DEPLOYMENT = "677edba8-ace0-4b2b-bad2-8e94b9959065"


def _api_key() -> str:
    return (os.environ.get("RUNCOMFY_API_KEY") or os.environ.get("RUNCOMFY_TOKEN") or "").strip()


def _deployment_id() -> str:
    return (os.environ.get("RUNCOMFY_DEPLOYMENT_ID") or "").strip() or _DEFAULT_DEPLOYMENT


def _load_index(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_index(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _find_series(data: dict[str, Any], series_id: str) -> dict[str, Any] | None:
    for row in data.get("series") or []:
        if str(row.get("series_id")) == series_id:
            return row
    return None


def run_generation(
    *,
    series_id: str,
    prompt: str,
    output_dir: Path,
    index_path: Path,
    dry_run: bool,
) -> Path:
    from scripts.image_generation.runcomfy_batch import (
        download_image,
        extract_image_url,
        get_result,
        poll_request,
        submit_inference,
        _RUNCOMFY_API_BASE,  # noqa: SLF001 — intentional reuse
    )

    data = _load_index(index_path)
    row = _find_series(data, series_id)
    if row is None:
        raise SystemExit(f"series_id not found in index: {series_id}")

    brand_id = str(row.get("brand_id") or "unknown_brand")
    dest = output_dir / brand_id / series_id / "main_character.png"
    # Derive the stored relative path from the resolved output_dir so that
    # --output-dir customisations are reflected in the index rather than being
    # silently discarded in favour of the hardcoded assets/manga_catalog prefix.
    try:
        rel_dir = dest.parent.resolve().relative_to(REPO_ROOT)
    except ValueError:
        rel_dir = dest.parent.resolve()
    dest.parent.mkdir(parents=True, exist_ok=True)

    if dry_run:
        return dest

    key = _api_key()
    if not key:
        raise SystemExit("RUNCOMFY_API_KEY or RUNCOMFY_TOKEN must be set in the environment")

    dep = _deployment_id()
    positive = (
        "manga character portrait, clean linework, expressive face, upper body, "
        f"{prompt}"
    )

    resp = submit_inference(
        api_key=key,
        deployment_id=dep,
        positive_prompt=positive,
        # Use a stable, process-independent hash so repeated runs produce the
        # same seed for a given series_id (Python's built-in hash() is
        # randomised per-process since Python 3.3).
        seed=int(hashlib.sha256(series_id.encode()).hexdigest(), 16) % (2**31),
    )

    status_url = resp.get("status_url", "")
    result_url = resp.get("result_url", "")
    request_id = resp.get("request_id", resp.get("run_id", ""))
    if not status_url and request_id:
        status_url = f"{_RUNCOMFY_API_BASE}/deployments/{dep}/requests/{request_id}/status"
    if not result_url and request_id:
        result_url = f"{_RUNCOMFY_API_BASE}/deployments/{dep}/requests/{request_id}/result"
    if not status_url:
        raise RuntimeError(f"No status_url or request_id in submit response: {resp}")

    poll_request(key, status_url, max_wait=300)
    final = get_result(key, result_url) if result_url else {}
    image_url = extract_image_url(final)
    if not image_url:
        raise RuntimeError(f"No image URL in RunComfy result: {json.dumps(final)[:2000]}")

    download_image(image_url, dest)

    row["main_character_image_path"] = str(rel_dir / "main_character.png")
    _write_index(index_path, data)

    return dest


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate character image via RunComfy and update index.")
    ap.add_argument("--series-id", required=True)
    ap.add_argument("--prompt", required=True, help="Positive prompt fragment (character + style hints).")
    ap.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUT_ROOT,
        help="Directory root for assets/manga_catalog/<brand>/<series>/ (default: repo assets/manga_catalog)",
    )
    ap.add_argument("--index", type=Path, default=DEFAULT_INDEX)
    ap.add_argument("--dry-run", action="store_true", help="Resolve paths only; no API calls.")
    args = ap.parse_args()

    try:
        out = run_generation(
            series_id=args.series_id,
            prompt=args.prompt,
            output_dir=args.output_dir,
            index_path=args.index,
            dry_run=args.dry_run,
        )
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    try:
        rel = out.resolve().relative_to(REPO_ROOT)
    except ValueError:
        rel = out.resolve()
    print(str(rel).replace("\\", "/"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
