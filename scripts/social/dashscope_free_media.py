#!/usr/bin/env python3
"""Operator-present Model Studio (Singapore) free-quota image/video client.

Lane B of the free-quota dual burn. Uses DashScope-intl native async APIs:

  - Image:  /api/v1/services/aigc/text2image/image-synthesis  (qwen-image-2.0)
  - Video:  /api/v1/services/aigc/video-generation/video-synthesis (wan2.7-t2v/i2v)

Hard-fails on Arrearage / AllocationQuota.FreeTierOnly. Never targets Beijing.
Do not wire into unattended CI (CLAUDE.md Tier-2 / llm-policy).

Usage:
  eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
  unset OLLAMA_HOST
  export DASHSCOPE_BASE_URL=https://dashscope-intl.aliyuncs.com/compatible-mode/v1

  PYTHONPATH=. python3 scripts/social/dashscope_free_media.py image \\
    --prompt "Faceless calm desk, soft light, 9:16, no text no logo" \\
    --out-dir artifacts/social_media_dashscope_free_2026-07-20/stills

  PYTHONPATH=. python3 scripts/social/dashscope_free_media.py video \\
    --prompt "Gentle camera push on empty chair by window, 9:16" \\
    --duration-s 5 --out-dir artifacts/social_media_dashscope_free_2026-07-20/video
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

NATIVE_BASE_DEFAULT = "https://dashscope-intl.aliyuncs.com/api/v1"
COMPAT_BASE_DEFAULT = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
IMAGE_PATH = "/services/aigc/text2image/image-synthesis"
VIDEO_PATH = "/services/aigc/video-generation/video-synthesis"
STUB_GUARD_BYTES = 50_000

HARD_FAIL_MARKERS = (
    "Arrearage",
    "AllocationQuota.FreeTierOnly",
    "FreeTierOnly",
    "overdue-payment",
)


class DashScopeFreeMediaError(RuntimeError):
    """Non-retryable Model Studio free-media failure."""


@dataclass
class TaskResult:
    task_id: str
    status: str
    output_url: str
    local_path: Path
    bytes: int
    model: str
    modality: str
    raw: dict[str, Any]


def api_key() -> str:
    # When PHOENIX_DASHSCOPE_FREE_MEDIA_ALLOW=1 (operator-present burn), REQUIRE
    # DASHSCOPE_FREE_QUOTA_API_KEY with NO fallback to the routine paid-risk keys
    # (CLAUDE.md contract / OPD-20260724-VBANK-00). Preflight without ALLOW may
    # still resolve FREE → DASHSCOPE_API_KEY → QWEN_API_KEY for dry tooling.
    allow = (os.environ.get("PHOENIX_DASHSCOPE_FREE_MEDIA_ALLOW") or "").strip() == "1"
    free = (os.environ.get("DASHSCOPE_FREE_QUOTA_API_KEY") or "").strip()
    if allow:
        if not free:
            raise DashScopeFreeMediaError(
                "BLOCKER: PHOENIX_DASHSCOPE_FREE_MEDIA_ALLOW=1 requires "
                "DASHSCOPE_FREE_QUOTA_API_KEY (no fallback to DASHSCOPE_API_KEY/"
                "QWEN_API_KEY). Load Keychain: eval \"$(python3 scripts/ci/"
                "load_integration_env_from_keychain.py)\""
            )
        return free
    key = (
        free
        or (os.environ.get("DASHSCOPE_API_KEY") or "").strip()
        or (os.environ.get("QWEN_API_KEY") or "").strip()
    )
    if not key:
        raise DashScopeFreeMediaError(
            "DASHSCOPE_FREE_QUOTA_API_KEY (or DASHSCOPE_API_KEY / QWEN_API_KEY) missing. "
            "Load Keychain: eval \"$(python3 scripts/ci/load_integration_env_from_keychain.py)\""
        )
    return key

MULTIMODAL_PATH = "/services/aigc/multimodal-generation/generation"


def native_base() -> str:
    # Prefer explicit native base; derive from compat if set to intl / workspace.
    raw = (os.environ.get("DASHSCOPE_NATIVE_BASE_URL") or "").strip()
    if raw:
        return raw.rstrip("/")
    compat = (os.environ.get("DASHSCOPE_BASE_URL") or COMPAT_BASE_DEFAULT).strip()
    if "dashscope.aliyuncs.com" in compat and "dashscope-intl" not in compat:
        raise DashScopeFreeMediaError(
            f"Beijing/mainland DashScope base refused: {compat}. Use Singapore intl only."
        )
    if "dashscope-intl" in compat or not compat:
        return NATIVE_BASE_DEFAULT
    # Model Studio workspace host (ws-*.ap-southeast-1.maas.aliyuncs.com):
    # derive /api/v1 from the compatible-mode URL. Do NOT fall back to
    # dashscope-intl — workspace keys fail there with InvalidParameter url error.
    if "maas.aliyuncs.com" in compat or "ap-southeast-1" in compat:
        root = compat.split("/compatible-mode")[0].rstrip("/")
        if root.startswith("http"):
            return root + "/api/v1"
    # Unknown base — still force intl native for media APIs.
    return NATIVE_BASE_DEFAULT


def _raise_if_hard_fail(payload: str | dict[str, Any], *, http_status: int | None = None) -> None:
    text = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)
    for marker in HARD_FAIL_MARKERS:
        if marker in text:
            raise DashScopeFreeMediaError(f"hard-fail {marker}: {text[:500]}")
    if isinstance(payload, dict):
        code = str(payload.get("code") or (payload.get("error") or {}).get("code") or "")
        err_type = str((payload.get("error") or {}).get("type") or "")
        for marker in HARD_FAIL_MARKERS:
            if marker in code or marker in err_type:
                raise DashScopeFreeMediaError(f"hard-fail {marker}: {text[:500]}")
    if http_status == 403 and "Quota" in text:
        raise DashScopeFreeMediaError(f"hard-fail quota HTTP 403: {text[:500]}")


def http_json(
    method: str,
    url: str,
    *,
    headers: dict[str, str],
    body: dict[str, Any] | None = None,
    timeout: float = 120.0,
    opener: Optional[Callable[..., Any]] = None,
) -> dict[str, Any]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    open_fn = opener or urllib.request.urlopen
    try:
        with open_fn(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", "replace")
            payload = json.loads(raw) if raw.strip() else {}
            _raise_if_hard_fail(payload, http_status=getattr(resp, "status", None))
            return payload
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        _raise_if_hard_fail(raw, http_status=exc.code)
        try:
            payload = json.loads(raw) if raw.strip() else {}
        except json.JSONDecodeError:
            payload = {"raw": raw}
        raise DashScopeFreeMediaError(f"HTTP {exc.code}: {raw[:800]}") from exc


def submit_image(
    *,
    prompt: str,
    model: str = "qwen-image-2.0",
    size: str = "720*1280",
    n: int = 1,
    key: str | None = None,
    opener: Optional[Callable[..., Any]] = None,
) -> str:
    """Submit async image job; return task_id."""
    url = native_base() + IMAGE_PATH
    headers = {
        "Authorization": f"Bearer {key or api_key()}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable",
    }
    body = {
        "model": model,
        "input": {"prompt": prompt},
        "parameters": {"size": size, "n": n},
    }
    payload = http_json("POST", url, headers=headers, body=body, opener=opener)
    task_id = (payload.get("output") or {}).get("task_id") or payload.get("task_id")
    if not task_id:
        raise DashScopeFreeMediaError(f"image submit missing task_id: {payload}")
    return str(task_id)


def submit_video(
    *,
    prompt: str,
    model: str = "wan2.7-t2v",
    duration_s: int = 5,
    resolution: str = "720P",
    image_url: str | None = None,
    key: str | None = None,
    opener: Optional[Callable[..., Any]] = None,
) -> str:
    """Submit async video job; return task_id. For i2v pass image_url."""
    url = native_base() + VIDEO_PATH
    headers = {
        "Authorization": f"Bearer {key or api_key()}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable",
    }
    inp: dict[str, Any] = {"prompt": prompt}
    if image_url:
        inp["img_url"] = image_url
    body = {
        "model": model,
        "input": inp,
        "parameters": {
            "resolution": resolution,
            "duration": int(duration_s),
            "watermark": False,
        },
    }
    payload = http_json("POST", url, headers=headers, body=body, opener=opener)
    task_id = (payload.get("output") or {}).get("task_id") or payload.get("task_id")
    if not task_id:
        raise DashScopeFreeMediaError(f"video submit missing task_id: {payload}")
    return str(task_id)


def poll_task(
    task_id: str,
    *,
    key: str | None = None,
    timeout_s: float = 600.0,
    interval_s: float = 3.0,
    opener: Optional[Callable[..., Any]] = None,
    sleeper: Callable[[float], None] = time.sleep,
) -> dict[str, Any]:
    url = f"{native_base()}/tasks/{task_id}"
    headers = {"Authorization": f"Bearer {key or api_key()}"}
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        payload = http_json("GET", url, headers=headers, body=None, opener=opener)
        output = payload.get("output") or payload
        status = str(output.get("task_status") or output.get("status") or "").upper()
        if status in {"SUCCEEDED", "SUCCESS", "FINISHED"}:
            return payload
        if status in {"FAILED", "CANCELED", "CANCELLED", "UNKNOWN"}:
            raise DashScopeFreeMediaError(f"task {task_id} failed: {payload}")
        _raise_if_hard_fail(payload)
        sleeper(interval_s)
    raise DashScopeFreeMediaError(f"task {task_id} timed out after {timeout_s}s")


def extract_output_url(payload: dict[str, Any], *, modality: str) -> str:
    output = payload.get("output") or {}
    # Common shapes
    for key in ("video_url", "image_url", "url", "file_url"):
        if output.get(key):
            return str(output[key])
    results = output.get("results") or output.get("task_result") or []
    if isinstance(results, dict):
        results = [results]
    if isinstance(results, list):
        for item in results:
            if not isinstance(item, dict):
                continue
            for key in ("url", "video_url", "image_url", "orig_url"):
                if item.get(key):
                    return str(item[key])
    # video nested
    video = output.get("video") or {}
    if isinstance(video, dict) and video.get("url"):
        return str(video["url"])
    raise DashScopeFreeMediaError(f"no output url for {modality}: {payload}")


def download_url(
    url: str,
    dest: Path,
    *,
    opener: Optional[Callable[..., Any]] = None,
    timeout: float = 300.0,
) -> int:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, method="GET")
    open_fn = opener or urllib.request.urlopen
    with open_fn(req, timeout=timeout) as resp:
        data = resp.read()
    dest.write_bytes(data)
    return len(data)


def run_image_sync_multimodal(
    *,
    prompt: str,
    out_dir: Path,
    model: str = "qwen-image-2.0",
    size: str = "720*1280",
    stem: str | None = None,
    key: str | None = None,
    opener: Optional[Callable[..., Any]] = None,
) -> TaskResult:
    """Sync multimodal image gen (workspace keys often deny async text2image).

    Uses ``/services/aigc/multimodal-generation/generation`` without
    ``X-DashScope-Async``. Hard-fails on Arrearage / FreeTierOnly.
    """
    url = native_base() + MULTIMODAL_PATH
    headers = {
        "Authorization": f"Bearer {key or api_key()}",
        "Content-Type": "application/json",
    }
    body = {
        "model": model,
        "input": {
            "messages": [
                {"role": "user", "content": [{"text": prompt}]},
            ]
        },
        "parameters": {"size": size, "n": 1},
    }
    payload = http_json("POST", url, headers=headers, body=body, opener=opener)
    out_url = ""
    choices = ((payload.get("output") or {}).get("choices") or [])
    for ch in choices:
        msg = (ch or {}).get("message") or {}
        for part in msg.get("content") or []:
            if isinstance(part, dict) and part.get("image"):
                out_url = str(part["image"])
                break
        if out_url:
            break
    if not out_url:
        try:
            out_url = extract_output_url(payload, modality="image")
        except DashScopeFreeMediaError as exc:
            raise DashScopeFreeMediaError(
                f"sync multimodal missing image url: {payload}"
            ) from exc
    name = stem or f"{model.replace('.', '_')}__sync"
    dest = out_dir / f"{name}.png"
    path = urlparse(out_url).path
    if path.endswith(".jpg") or path.endswith(".jpeg"):
        dest = dest.with_suffix(".jpg")
    elif path.endswith(".webp"):
        dest = dest.with_suffix(".webp")
    nbytes = download_url(out_url, dest, opener=opener)
    if nbytes < 8_000:
        raise DashScopeFreeMediaError(f"image stub-sized bytes={nbytes} path={dest}")
    return TaskResult(
        task_id=str(payload.get("request_id") or "sync"),
        status="SUCCEEDED",
        output_url=out_url,
        local_path=dest,
        bytes=nbytes,
        model=model,
        modality="image",
        raw=payload,
    )


def run_image(
    *,
    prompt: str,
    out_dir: Path,
    model: str = "qwen-image-2.0",
    size: str = "720*1280",
    stem: str | None = None,
    key: str | None = None,
    opener: Optional[Callable[..., Any]] = None,
    sleeper: Callable[[float], None] = time.sleep,
    prefer_sync: bool | None = None,
) -> TaskResult:
    """Generate one still. Prefers sync multimodal for workspace hosts.

    Set ``prefer_sync=True`` to force multimodal sync; ``False`` forces async
    text2image. Default: sync when native base is a Model Studio workspace host.
    """
    base = native_base()
    use_sync = prefer_sync
    if use_sync is None:
        use_sync = "maas.aliyuncs.com" in base or bool(
            (os.environ.get("DASHSCOPE_IMAGE_SYNC") or "").strip()
        )
    if use_sync:
        return run_image_sync_multimodal(
            prompt=prompt,
            out_dir=out_dir,
            model=model,
            size=size,
            stem=stem,
            key=key,
            opener=opener,
        )
    task_id = submit_image(prompt=prompt, model=model, size=size, key=key, opener=opener)
    payload = poll_task(task_id, key=key, opener=opener, sleeper=sleeper)
    out_url = extract_output_url(payload, modality="image")
    name = stem or f"{model.replace('.', '_')}__{task_id[:12]}"
    dest = out_dir / f"{name}.png"
    # Prefer png/jpeg from URL suffix
    path = urlparse(out_url).path
    if path.endswith(".jpg") or path.endswith(".jpeg"):
        dest = dest.with_suffix(".jpg")
    elif path.endswith(".webp"):
        dest = dest.with_suffix(".webp")
    nbytes = download_url(out_url, dest, opener=opener)
    if nbytes < 8_000:
        raise DashScopeFreeMediaError(f"image stub-sized bytes={nbytes} path={dest}")
    return TaskResult(
        task_id=task_id,
        status="SUCCEEDED",
        output_url=out_url,
        local_path=dest,
        bytes=nbytes,
        model=model,
        modality="image",
        raw=payload,
    )


def run_video(
    *,
    prompt: str,
    out_dir: Path,
    model: str = "wan2.7-t2v",
    duration_s: int = 5,
    image_url: str | None = None,
    stem: str | None = None,
    key: str | None = None,
    opener: Optional[Callable[..., Any]] = None,
    sleeper: Callable[[float], None] = time.sleep,
) -> TaskResult:
    task_id = submit_video(
        prompt=prompt,
        model=model,
        duration_s=duration_s,
        image_url=image_url,
        key=key,
        opener=opener,
    )
    payload = poll_task(task_id, key=key, opener=opener, sleeper=sleeper)
    out_url = extract_output_url(payload, modality="video")
    name = stem or f"{model.replace('.', '_')}__{task_id[:12]}"
    dest = out_dir / f"{name}.mp4"
    nbytes = download_url(out_url, dest, opener=opener)
    if nbytes < STUB_GUARD_BYTES:
        raise DashScopeFreeMediaError(f"video stub-sized bytes={nbytes} path={dest}")
    return TaskResult(
        task_id=task_id,
        status="SUCCEEDED",
        output_url=out_url,
        local_path=dest,
        bytes=nbytes,
        model=model,
        modality="video",
        raw=payload,
    )


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="modality", required=True)

    img = sub.add_parser("image", help="Generate still via qwen-image-2.0")
    img.add_argument("--prompt", required=True)
    img.add_argument("--model", default="qwen-image-2.0")
    img.add_argument("--size", default="720*1280", help="WxH for 9:16 social default 720*1280")
    img.add_argument("--out-dir", type=Path, required=True)
    img.add_argument("--stem", default="")
    img.add_argument("--dry-run-submit-body", action="store_true", help="Print would-be request and exit")

    vid = sub.add_parser("video", help="Generate short via wan2.7-t2v/i2v")
    vid.add_argument("--prompt", required=True)
    vid.add_argument("--model", default="wan2.7-t2v", choices=["wan2.7-t2v", "wan2.7-i2v"])
    vid.add_argument("--duration-s", type=int, default=5)
    vid.add_argument("--image-url", default="", help="Required for wan2.7-i2v")
    vid.add_argument("--out-dir", type=Path, required=True)
    vid.add_argument("--stem", default="")
    vid.add_argument("--dry-run-submit-body", action="store_true", help="Print would-be request and exit")
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.modality == "image":
        if args.dry_run_submit_body:
            print(json.dumps({"model": args.model, "prompt": args.prompt, "size": args.size}))
            return 0
        result = run_image(
            prompt=args.prompt,
            out_dir=args.out_dir,
            model=args.model,
            size=args.size,
            stem=args.stem or None,
        )
    else:
        if args.model == "wan2.7-i2v" and not args.image_url:
            print("ERROR: --image-url required for wan2.7-i2v", file=sys.stderr)
            return 2
        if args.dry_run_submit_body:
            print(
                json.dumps(
                    {
                        "model": args.model,
                        "prompt": args.prompt,
                        "duration_s": args.duration_s,
                        "image_url": args.image_url or None,
                    }
                )
            )
            return 0
        result = run_video(
            prompt=args.prompt,
            out_dir=args.out_dir,
            model=args.model,
            duration_s=args.duration_s,
            image_url=args.image_url or None,
            stem=args.stem or None,
        )
    print(
        json.dumps(
            {
                "task_id": result.task_id,
                "modality": result.modality,
                "model": result.model,
                "bytes": result.bytes,
                "local_path": str(result.local_path),
                "output_url": result.output_url,
                "content_provenance": "INTERIM",
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except DashScopeFreeMediaError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
