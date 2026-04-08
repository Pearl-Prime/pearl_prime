#!/usr/bin/env python3
"""RunComfy batch image generator for Phoenix Omega video bank.

Reads topic×visual_intent matrix from config, compiles prompts via
prompt_compiler, and dispatches jobs to RunComfy API.

Usage:
    # Generate manifest only (dry run):
    python scripts/image_generation/runcomfy_batch.py --dry-run

    # Run full batch via RunComfy API:
    python scripts/image_generation/runcomfy_batch.py \
        --api-key $RUNCOMFY_API_KEY \
        --output artifacts/video_bank/

    # Single topic test:
    python scripts/image_generation/runcomfy_batch.py \
        --topic anxiety --intent HOOK_VISUAL --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

try:
    import requests  # type: ignore[import-untyped]
except ImportError:
    requests = None  # type: ignore[assignment]

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

from scripts.image_generation.prompt_compiler import (
    compile_image_prompt,
    QUALITY_TOKENS,
    SHARED_NEGATIVE_TOKENS,
)


# ── Config paths ──
_SCENES_PATH = REPO_ROOT / "config" / "video" / "flux_bank_scenes.yaml"
_STYLE_TOKENS_PATH = REPO_ROOT / "config" / "video" / "brand_style_tokens.yaml"
_CONSTRAINTS_PATH = REPO_ROOT / "config" / "video" / "prompt_constraints.yaml"
_WORKFLOW_PATH = REPO_ROOT / "scripts" / "image_generation" / "comfyui_workflows" / "flux_video_bank.json"

# ── RunComfy Serverless API ──
_RUNCOMFY_API_BASE = "https://api.runcomfy.net/prod/v1"
_DEFAULT_DEPLOYMENT_ID = "677edba8-ace0-4b2b-bad2-8e94b9959065"  # RunComfy/FLUX v1

# Node IDs in RunComfy/FLUX workflow_api.json
_NODE_POSITIVE_PROMPT = "6"   # CLIPTextEncode → inputs.text
_NODE_SEED = "25"             # KSampler → inputs.noise_seed


# ── Loaders ──

def _load_yaml(path: Path) -> dict[str, Any]:
    """Load YAML config. Returns empty dict if unavailable."""
    if yaml is None or not path.is_file():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _load_scenes() -> dict[str, str]:
    """Load visual_intent → scene mapping."""
    data = _load_yaml(_SCENES_PATH)
    scenes = data.get("visual_intent_scenes", {})
    default = data.get("default_scene", "a contemplative moment, soft light")
    return {k: v.get("scene", default) for k, v in scenes.items()}, default


def _load_topics() -> dict[str, dict[str, Any]]:
    """Load topic → band/palette mapping from brand_style_tokens."""
    data = _load_yaml(_STYLE_TOKENS_PATH)
    topic_to_band = data.get("topic_to_band", {})
    bands = data.get("bands", {})

    topics: dict[str, dict[str, Any]] = {}
    for topic, band_name in topic_to_band.items():
        if topic == "default":
            continue
        band = bands.get(band_name, {})
        topic_data = band.get("topics", {}).get(topic, {})
        palette = topic_data.get("palette", [])
        gen_spec = band.get("generation_spec", {})
        never_rules = band.get("never_rules", [])

        topics[topic] = {
            "band": band_name,
            "palette": palette,
            "palette_tokens": [p.get("prompt_name", "") for p in palette],
            "seed": gen_spec.get("shnell_seed", 739204),
            "guidance": gen_spec.get("guidance", 3.0),
            "never_rules": never_rules,
            "emotion_arc": topic_data.get("emotion_arc", ""),
        }
    return topics


def _load_constraints() -> dict[str, list[str]]:
    """Load shared negative constraints."""
    data = _load_yaml(_CONSTRAINTS_PATH)
    return {
        "no_adoration": data.get("no_adoration", []),
        "shared_negatives": data.get("shared_negatives", []),
    }


# ── Prompt building ──

def build_video_bank_manifest(
    *,
    topics_filter: list[str] | None = None,
    intents_filter: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Build the full topic × visual_intent prompt manifest.

    Returns list of dicts with: topic, intent, positive, negative, seed,
    guidance, filename_prefix, palette_tokens, band.
    """
    scenes, default_scene = _load_scenes()
    topics = _load_topics()
    constraints = _load_constraints()

    all_intents = ["HOOK_VISUAL", "CHARACTER_EMOTION", "SYMBOLIC_METAPHOR", "ENVIRONMENT_ATMOSPHERE"]

    if intents_filter:
        all_intents = [i for i in all_intents if i in intents_filter]

    manifest: list[dict[str, Any]] = []

    for topic, topic_data in topics.items():
        if topics_filter and topic not in topics_filter:
            continue

        palette_tokens = topic_data["palette_tokens"]
        band = topic_data["band"]
        seed = topic_data["seed"]
        guidance = topic_data["guidance"]
        never_rules = topic_data["never_rules"]

        for intent in all_intents:
            scene = scenes.get(intent, default_scene)

            # Build negative from shared + constraints + band never_rules
            neg_parts = [SHARED_NEGATIVE_TOKENS]
            for rule in constraints.get("no_adoration", []):
                neg_parts.append(rule.replace("no ", "", 1) if rule.startswith("no ") else rule)
            for rule in constraints.get("shared_negatives", []):
                neg_parts.append(rule.replace("no ", "", 1) if rule.startswith("no ") else rule)
            for rule in never_rules:
                neg_parts.append(rule)
            negative = ", ".join(neg_parts)

            # Compile via prompt_compiler
            compiled = compile_image_prompt(
                task="video_bank_image",
                subject=f"{topic.replace('_', ' ')} themed visual",
                style_hint=f"{topic_data['emotion_arc']} color arc",
                palette_tokens=palette_tokens,
                scene=scene,
                extra_positive="9:16 portrait orientation, cinematic still",
                extra_negative=negative,
                author_id="48social",
                bio_keywords=[topic, band],
            )

            # Override seed and guidance from band config
            compiled["seed"] = seed
            compiled["guidance"] = guidance

            filename_prefix = f"vb_{topic}_{intent.lower()}"

            manifest.append({
                "topic": topic,
                "intent": intent,
                "band": band,
                "positive": compiled["positive"],
                "negative": compiled["negative"],
                "seed": seed,
                "guidance": guidance,
                "filename_prefix": filename_prefix,
                "palette_tokens": palette_tokens,
                "positive_token_count": compiled["positive_token_count"],
                "negative_token_count": compiled["negative_token_count"],
                "provenance": compiled["provenance"],
            })

    return manifest


# ── RunComfy API ──

_MAX_RETRIES = 5
_BASE_BACKOFF_S: float = 2.0  # mutable for test patching


def _runcomfy_request(
    url: str,
    *,
    api_key: str,
    method: str = "GET",
    data: dict | None = None,
    timeout: int = 120,
) -> dict[str, Any]:
    """Make an authenticated request to RunComfy Serverless API.

    Retries with exponential backoff on transient errors (429 rate-limit,
    5xx server errors, connection resets).
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    last_err: Exception | None = None
    for attempt in range(_MAX_RETRIES):
        try:
            if requests is not None:
                if method == "POST":
                    resp = requests.post(url, json=data, headers=headers, timeout=timeout)
                else:
                    resp = requests.get(url, headers=headers, timeout=timeout)

                code = int(resp.status_code)
                if code == 429 or code >= 500:
                    # Retryable — back off and try again
                    wait = _BASE_BACKOFF_S * (2 ** attempt)
                    time.sleep(wait)
                    last_err = RuntimeError(f"RunComfy API {code}: {resp.text[:200]}")
                    continue
                if code >= 400:
                    raise RuntimeError(f"RunComfy API {resp.status_code}: {resp.text[:500]}")
                return resp.json()

            # Fallback: urllib
            body = json.dumps(data).encode("utf-8") if data else None
            req = urllib.request.Request(url, data=body, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8"))

        except (ConnectionError, OSError, urllib.error.URLError) as e:
            wait = _BASE_BACKOFF_S * (2 ** attempt)
            time.sleep(wait)
            last_err = e
        except urllib.error.HTTPError as e:
            code = e.code
            if code == 429 or code >= 500:
                wait = _BASE_BACKOFF_S * (2 ** attempt)
                time.sleep(wait)
                last_err = e
                continue
            error_body = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"RunComfy API {code}: {error_body}") from e

    raise RuntimeError(f"RunComfy API failed after {_MAX_RETRIES} retries: {last_err}")


def submit_inference(
    *,
    api_key: str,
    deployment_id: str,
    positive_prompt: str,
    seed: int = 739204,
) -> dict[str, Any]:
    """Submit an inference request to a RunComfy deployment.

    Uses the overrides pattern: only sends the nodes we want to change.
    The deployment's saved workflow_api.json handles everything else.
    """
    overrides: dict[str, Any] = {
        _NODE_POSITIVE_PROMPT: {
            "inputs": {
                "text": positive_prompt,
            }
        },
    }

    # Only override seed if non-default
    if seed != 0:
        overrides[_NODE_SEED] = {
            "inputs": {
                "noise_seed": seed,
            }
        }

    url = f"{_RUNCOMFY_API_BASE}/deployments/{deployment_id}/inference"
    return _runcomfy_request(
        url,
        api_key=api_key,
        method="POST",
        data={"overrides": overrides},
    )


def poll_request(
    api_key: str,
    status_url: str,
    *,
    max_wait: int = 300,
    interval: int = 5,
) -> dict[str, Any]:
    """Poll a RunComfy request until completion or timeout."""
    start = time.time()
    while time.time() - start < max_wait:
        result = _runcomfy_request(status_url, api_key=api_key)
        status = result.get("status", "unknown")
        if status in ("succeeded", "completed", "failed", "error"):
            return result
        time.sleep(interval)
    return {"status": "timeout"}


def get_result(api_key: str, result_url: str) -> dict[str, Any]:
    """Fetch the result of a completed request."""
    return _runcomfy_request(result_url, api_key=api_key)


def download_image(url: str, output_path: Path) -> Path:
    """Download a generated image from RunComfy output URL."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if requests is not None:
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        output_path.write_bytes(resp.content)
    else:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=60) as resp:
            output_path.write_bytes(resp.read())
    return output_path


# ── Manga-backend bridge functions ──────────────────────────────────
# Used by phoenix_v4.manga.image_backend.RunComfyImageBackend and tests.

MAX_POLL_S: float = 300.0


def load_workflow(workflow_path: Path) -> dict[str, Any]:
    """Load a ComfyUI workflow JSON template."""
    return json.loads(Path(workflow_path).read_text(encoding="utf-8"))


def submit_workflow(
    api_key: str,
    deployment_id: str,
    workflow: dict[str, Any],
) -> str:
    """Submit a workflow to RunComfy and return the run_id."""
    url = f"{_RUNCOMFY_API_BASE}/deployments/{deployment_id}/inference"
    if requests is not None:
        resp = requests.post(
            url,
            json={"workflow": workflow},
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
    else:
        data = _runcomfy_request(url, api_key=api_key, method="POST", data={"workflow": workflow})
    return str(data.get("run_id", ""))


def poll_run(
    api_key: str,
    deployment_id: str,
    run_id: str,
    *,
    max_wait: float | None = None,
    interval: float = 5.0,
) -> dict[str, Any]:
    """Poll a RunComfy run until completed, failed, or timeout."""
    if max_wait is None:
        max_wait = MAX_POLL_S
    url = f"{_RUNCOMFY_API_BASE}/deployments/{deployment_id}/runs/{run_id}"
    start = time.time()
    while time.time() - start < max_wait:
        if requests is not None:
            resp = requests.get(
                url,
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
        else:
            data = _runcomfy_request(url, api_key=api_key)
        status = data.get("status", "unknown")
        if status in ("completed", "succeeded"):
            return data
        if status in ("failed", "error"):
            raise RuntimeError(data.get("error", f"RunComfy run {run_id} failed: {status}"))
        time.sleep(interval)
    raise RuntimeError(f"RunComfy run {run_id} timed out after {max_wait}s")


def extract_image_url(result: dict[str, Any]) -> str | None:
    """Extract the first image URL from a RunComfy result payload.

    RunComfy outputs are keyed by node ID (e.g. ``"9"``), each containing
    an ``images`` list. This function searches all output nodes.
    """
    outputs = result.get("outputs", {})
    # Direct images list (simple format)
    images = outputs.get("images", [])
    if images:
        first = images[0]
        if isinstance(first, dict):
            return first.get("url")
        if isinstance(first, str):
            return first

    # Node-keyed format: outputs.{node_id}.images[0].url
    if isinstance(outputs, dict):
        for node_id, node_out in outputs.items():
            if isinstance(node_out, dict):
                node_images = node_out.get("images", [])
                if node_images and isinstance(node_images[0], dict):
                    url = node_images[0].get("url")
                    if url:
                        return url
    return None


# ── Batch execution ──

def run_batch(
    manifest: list[dict[str, Any]],
    *,
    api_key: str,
    deployment_id: str,
    output_dir: Path,
    dry_run: bool = False,
) -> list[dict[str, Any]]:
    """Execute the full batch via RunComfy Serverless API.

    Flow per image: submit inference → poll status → get result → download.
    Returns list of result dicts with status, path, etc.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, Any]] = []
    total = len(manifest)

    for i, entry in enumerate(manifest):
        print(f"[{i+1}/{total}] {entry['filename_prefix']} ({entry['topic']}/{entry['intent']})")

        if dry_run:
            results.append({
                "filename_prefix": entry["filename_prefix"],
                "topic": entry["topic"],
                "intent": entry["intent"],
                "status": "dry_run",
                "positive_tokens": entry["positive_token_count"],
                "negative_tokens": entry["negative_token_count"],
            })
            continue

        try:
            # Submit inference
            resp = submit_inference(
                api_key=api_key,
                deployment_id=deployment_id,
                positive_prompt=entry["positive"],
                seed=entry["seed"],
            )
            request_id = resp.get("request_id", "unknown")
            status_url = resp.get("status_url", "")
            result_url = resp.get("result_url", "")
            print(f"  → Request submitted: {request_id}")

            if not status_url:
                # Build URLs from deployment_id and request_id
                base = f"{_RUNCOMFY_API_BASE}/deployments/{deployment_id}/requests/{request_id}"
                status_url = f"{base}/status"
                result_url = f"{base}/result"

            # Poll until complete
            poll_resp = poll_request(api_key, status_url)
            status = poll_resp.get("status", "unknown")

            if status in ("succeeded", "completed"):
                # Get result
                result_resp = get_result(api_key, result_url)
                outputs = result_resp.get("outputs", {})

                # Extract image URL from outputs (node IDs as keys)
                output_url = None
                for node_id, node_output in outputs.items():
                    if isinstance(node_output, dict):
                        images = node_output.get("images", [])
                        if images:
                            output_url = images[0].get("url")
                            break

                if output_url:
                    out_path = output_dir / f"{entry['filename_prefix']}.png"
                    download_image(output_url, out_path)
                    print(f"  ✓ Saved: {out_path} ({out_path.stat().st_size} bytes)")
                    results.append({
                        "filename_prefix": entry["filename_prefix"],
                        "status": "completed",
                        "path": str(out_path),
                        "file_size": out_path.stat().st_size,
                    })
                else:
                    print(f"  ⚠ Succeeded but no image URL in outputs")
                    results.append({
                        "filename_prefix": entry["filename_prefix"],
                        "status": "completed_no_output",
                        "raw_outputs": outputs,
                    })
            else:
                print(f"  ✗ Request {status}: {poll_resp.get('error', 'unknown')}")
                results.append({
                    "filename_prefix": entry["filename_prefix"],
                    "status": status,
                    "error": poll_resp.get("error"),
                })

        except Exception as exc:
            print(f"  ✗ Error: {exc}")
            results.append({
                "filename_prefix": entry["filename_prefix"],
                "status": "error",
                "error": str(exc),
            })

        # Brief pause between submissions to avoid hammering
        if not dry_run and i < total - 1:
            time.sleep(2)

    return results


# ── CLI ──

def main() -> int:
    parser = argparse.ArgumentParser(description="RunComfy batch video bank generator.")
    parser.add_argument("--api-key", default=os.environ.get("RUNCOMFY_API_KEY", ""), help="RunComfy API key")
    parser.add_argument("--deployment-id", default=os.environ.get("RUNCOMFY_DEPLOYMENT_ID", _DEFAULT_DEPLOYMENT_ID), help="RunComfy deployment ID")
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "artifacts" / "video_bank", help="Output directory")
    parser.add_argument("--topic", nargs="*", default=None, help="Filter to specific topics")
    parser.add_argument("--intent", nargs="*", default=None, help="Filter to specific visual intents")
    parser.add_argument("--dry-run", action="store_true", help="Generate manifest without running")
    parser.add_argument("--manifest-only", action="store_true", help="Write manifest JSON and exit")

    args = parser.parse_args()

    # Build manifest
    manifest = build_video_bank_manifest(
        topics_filter=args.topic,
        intents_filter=args.intent,
    )

    print(f"Manifest: {len(manifest)} images")
    for entry in manifest:
        print(f"  {entry['filename_prefix']}: {entry['positive_token_count']}+/{entry['negative_token_count']}- tokens")

    if args.manifest_only:
        manifest_path = args.output / "manifest.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")
        print(f"\nManifest written: {manifest_path}")
        return 0

    if args.dry_run:
        results = run_batch(manifest, api_key="", deployment_id=args.deployment_id, output_dir=args.output, dry_run=True)
        print(f"\n[DRY-RUN] {len(results)} jobs planned")
        return 0

    if not args.api_key:
        print("Error: --api-key or RUNCOMFY_API_KEY required", file=sys.stderr)
        return 1

    results = run_batch(
        manifest,
        api_key=args.api_key,
        deployment_id=args.deployment_id,
        output_dir=args.output,
    )

    # Summary
    completed = sum(1 for r in results if r["status"] == "completed")
    failed = sum(1 for r in results if r["status"] not in ("completed", "dry_run"))
    print(f"\n{'='*60}")
    print(f"Batch complete: {completed}/{len(results)} succeeded, {failed} failed")

    # Write results
    results_path = args.output / "batch_results.json"
    results_path.write_text(json.dumps(results, indent=2, default=str), encoding="utf-8")
    print(f"Results: {results_path}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
