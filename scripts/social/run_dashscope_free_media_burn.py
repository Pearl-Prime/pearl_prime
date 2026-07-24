#!/usr/bin/env python3
"""Operator-present free-quota image/video burn into media bank (Lane B).

Caps (DOC-ONLY until Vision console confirms):
  - ≤100 stills via qwen-image-2.0
  - ≤50 s wan2.7-t2v (5 s clips → ≤10)
  - ≤50 s wan2.7-i2v (5 s clips → ≤10)

Aborts immediately on Arrearage / FreeTierOnly. Labels INTERIM.

Usage:
  eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
  unset OLLAMA_HOST
  export DASHSCOPE_BASE_URL=https://dashscope-intl.aliyuncs.com/compatible-mode/v1
  export DASHSCOPE_NATIVE_BASE_URL=https://dashscope-intl.aliyuncs.com/api/v1

  PYTHONPATH=. python3 scripts/social/run_dashscope_free_media_burn.py --preflight-only
  PYTHONPATH=. python3 scripts/social/run_dashscope_free_media_burn.py --max-stills 2 --max-t2v-s 5
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from scripts.social import dashscope_free_media as dfm  # noqa: E402
from scripts.social import ingest_dashscope_free_media_bank as ingest  # noqa: E402

OUT_ROOT = REPO / "artifacts/social_media_dashscope_free_2026-07-20"
SUMMARY_PATH = OUT_ROOT / "burn_summary.json"

TOPICS = ("anxiety", "boundaries", "burnout")
DESIGN_FAMILIES = ("object_metaphor", "photo_full_bleed_emotional", "story_carousel")

PROMPT_STILL = (
    "Faceless wellness social still, soft natural light, calm {topic} metaphor, "
    "vertical 9:16, no text, no logo, no watermark, no identifiable face"
)
PROMPT_T2V = (
    "Gentle camera push on a faceless calm scene about {topic}, soft light, "
    "vertical 9:16, no text, no logo"
)


def force_singapore_env() -> None:
    os.environ.pop("OLLAMA_HOST", None)
    os.environ["DASHSCOPE_BASE_URL"] = (
        os.environ.get("DASHSCOPE_BASE_URL")
        or "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    )
    if "dashscope.aliyuncs.com" in os.environ["DASHSCOPE_BASE_URL"] and "intl" not in os.environ[
        "DASHSCOPE_BASE_URL"
    ]:
        raise dfm.DashScopeFreeMediaError("Beijing base refused for free burn")
    # Derive via dfm.native_base()'s own workspace-aware logic instead of
    # hardcoding the generic dashscope-intl host here. Hardcoding silently
    # broke image generation for workspace-scoped keys (sk-ws-...) on
    # 2026-07-24: it forced native calls through the generic host, which
    # workspace keys can't use for async image submission ("current user api
    # does not support asynchronous calls") nor route correctly at all
    # ("InvalidParameter: url error"); video happened to still work there by
    # coincidence, which is what made the bug hard to notice. At this point
    # DASHSCOPE_NATIVE_BASE_URL is guaranteed unset (that's the precondition
    # for setdefault to act), so native_base() correctly derives the
    # workspace-specific ws-*.maas.aliyuncs.com/api/v1 host from the
    # DASHSCOPE_BASE_URL just resolved above when applicable, or the generic
    # intl default otherwise — same derivation used everywhere else in
    # dashscope_free_media.py, now applied here too instead of bypassed.
    os.environ.setdefault("DASHSCOPE_NATIVE_BASE_URL", dfm.native_base())


def preflight_chat_smoke() -> dict[str, Any]:
    """Tiny chat smoke; Arrearage must abort both lanes."""
    key = dfm.api_key()
    url = os.environ["DASHSCOPE_BASE_URL"].rstrip("/") + "/chat/completions"
    body = {
        "model": "qwen3.7-plus",
        "messages": [{"role": "user", "content": "ok"}],
        "max_tokens": 5,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
            dfm._raise_if_hard_fail(payload)
            return {"ok": True, "payload_keys": list(payload.keys())}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        dfm._raise_if_hard_fail(raw, http_status=exc.code)
        raise dfm.DashScopeFreeMediaError(f"preflight HTTP {exc.code}: {raw[:400]}") from exc


def run_burn(
    *,
    max_stills: int,
    max_t2v_s: int,
    max_i2v_s: int,
    clip_s: int,
    skip_preflight: bool,
) -> dict[str, Any]:
    force_singapore_env()
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    still_dir = OUT_ROOT / "stills"
    video_dir = OUT_ROOT / "video"
    summary: dict[str, Any] = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "stills_ok": [],
        "video_ok": [],
        "video_seconds_used_t2v": 0,
        "video_seconds_used_i2v": 0,
        "errors": [],
        "blocker": None,
        "content_provenance": "INTERIM",
    }
    if not skip_preflight:
        try:
            summary["preflight"] = preflight_chat_smoke()
        except dfm.DashScopeFreeMediaError as exc:
            summary["blocker"] = str(exc)
            summary["finished_at"] = datetime.now(timezone.utc).isoformat()
            SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
            return summary

    # Stills
    n = 0
    for topic in TOPICS:
        for family in DESIGN_FAMILIES:
            if n >= max_stills:
                break
            stem = f"{topic}__{family}__{n:03d}"
            prompt = PROMPT_STILL.format(topic=topic)
            try:
                result = dfm.run_image(
                    prompt=prompt,
                    out_dir=still_dir,
                    model="qwen-image-2.0",
                    size="720*1280",
                    stem=stem,
                )
                row = ingest.ingest_image(
                    result.local_path,
                    topic=topic,
                    design_family=family,
                    model=result.model,
                )
                summary["stills_ok"].append(
                    {
                        "path": str(result.local_path),
                        "image_id": row["image_id"],
                        "bytes": result.bytes,
                        "output_url": result.output_url,
                    }
                )
                n += 1
            except dfm.DashScopeFreeMediaError as exc:
                summary["errors"].append(str(exc))
                if any(m in str(exc) for m in dfm.HARD_FAIL_MARKERS):
                    summary["blocker"] = str(exc)
                    break
            except Exception as exc:  # noqa: BLE001
                summary["errors"].append(f"still:{exc}")
        if summary.get("blocker") or n >= max_stills:
            break

    # T2V
    t2v_used = 0
    k = 0
    while t2v_used + clip_s <= max_t2v_s and not summary.get("blocker"):
        topic = TOPICS[k % len(TOPICS)]
        stem = f"wan27_t2v__{topic}__k{k:02d}"
        try:
            result = dfm.run_video(
                prompt=PROMPT_T2V.format(topic=topic),
                out_dir=video_dir,
                model="wan2.7-t2v",
                duration_s=clip_s,
                stem=stem,
            )
            row = ingest.ingest_video(
                result.local_path,
                topic=topic,
                model="wan2.7-t2v",
                duration_s=clip_s,
                k_index=k,
            )
            summary["video_ok"].append(
                {"path": str(result.local_path), "asset_id": row["asset_id"], "seconds": clip_s}
            )
            t2v_used += clip_s
            k += 1
        except dfm.DashScopeFreeMediaError as exc:
            summary["errors"].append(str(exc))
            if any(m in str(exc) for m in dfm.HARD_FAIL_MARKERS):
                summary["blocker"] = str(exc)
            break
        except Exception as exc:  # noqa: BLE001
            summary["errors"].append(f"t2v:{exc}")
            break
    summary["video_seconds_used_t2v"] = t2v_used

    # I2V from still output URLs (or DASHSCOPE_I2V_IMAGE_URL override).
    i2v_used = 0
    env_i2v = os.environ.get("DASHSCOPE_I2V_IMAGE_URL", "").strip()
    for i, still in enumerate(summary["stills_ok"]):
        if i2v_used + clip_s > max_i2v_s or summary.get("blocker"):
            break
        image_url = env_i2v or str(still.get("output_url") or "").strip()
        if not image_url:
            summary["errors"].append("i2v_skipped: no still output_url and no DASHSCOPE_I2V_IMAGE_URL")
            break
        topic = TOPICS[i % len(TOPICS)]
        try:
            result = dfm.run_video(
                prompt=PROMPT_T2V.format(topic=topic),
                out_dir=video_dir,
                model="wan2.7-i2v",
                duration_s=clip_s,
                image_url=image_url,
                stem=f"wan27_i2v__{topic}__k{i:02d}",
            )
            row = ingest.ingest_video(
                result.local_path,
                topic=topic,
                model="wan2.7-i2v",
                duration_s=clip_s,
                k_index=100 + i,
            )
            summary["video_ok"].append(
                {"path": str(result.local_path), "asset_id": row["asset_id"], "seconds": clip_s}
            )
            i2v_used += clip_s
        except dfm.DashScopeFreeMediaError as exc:
            summary["errors"].append(str(exc))
            if any(m in str(exc) for m in dfm.HARD_FAIL_MARKERS):
                summary["blocker"] = str(exc)
            break
    summary["video_seconds_used_i2v"] = i2v_used
    summary["finished_at"] = datetime.now(timezone.utc).isoformat()
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--max-stills", type=int, default=100)
    ap.add_argument("--max-t2v-s", type=int, default=50)
    ap.add_argument("--max-i2v-s", type=int, default=50)
    ap.add_argument("--clip-s", type=int, default=5)
    ap.add_argument("--preflight-only", action="store_true")
    ap.add_argument("--skip-preflight", action="store_true")
    args = ap.parse_args(argv)

    # Explicit operator opt-in (CLAUDE.md scoped exception, 2026-07-24). This
    # is a one-time free-quota content-bank build, not a standing pipeline —
    # no workflow/cron may set this; it must be set by hand in an
    # operator-present shell.
    if not args.preflight_only and os.environ.get("PHOENIX_DASHSCOPE_FREE_MEDIA_ALLOW") != "1":
        print(
            json.dumps(
                {
                    "blocker": (
                        "PHOENIX_DASHSCOPE_FREE_MEDIA_ALLOW=1 not set. This is an "
                        "operator-present-only one-time burn (CLAUDE.md scoped "
                        "exception, 2026-07-24) — set it explicitly in your shell, "
                        "never in a workflow/cron."
                    )
                },
                indent=2,
            )
        )
        return 1

    force_singapore_env()
    if args.preflight_only:
        try:
            result = preflight_chat_smoke()
            print(json.dumps({"preflight": result}, indent=2))
            return 0
        except dfm.DashScopeFreeMediaError as exc:
            print(json.dumps({"blocker": str(exc)}, indent=2))
            return 1

    summary = run_burn(
        max_stills=args.max_stills,
        max_t2v_s=args.max_t2v_s,
        max_i2v_s=args.max_i2v_s,
        clip_s=args.clip_s,
        skip_preflight=args.skip_preflight,
    )
    print(json.dumps(summary, indent=2))
    return 1 if summary.get("blocker") else 0


if __name__ == "__main__":
    raise SystemExit(main())
