#!/usr/bin/env python3
"""Audit, generate (FLUX), and index Stillness Press manga image bank.

Expected layout per topic:
  {intent}_{style_slug}_{sNN}.png
  {intent}_{style_slug}_{sNN}_landscape.png

Where intent is lowercase snake (environment_atmosphere, ...).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

TOPICS_15 = [
    "anxiety",
    "boundaries",
    "burnout",
    "compassion_fatigue",
    "courage",
    "depression",
    "financial_anxiety",
    "financial_stress",
    "grief",
    "imposter_syndrome",
    "overthinking",
    "self_worth",
    "sleep_anxiety",
    "social_anxiety",
    "somatic_healing",
]

INTENTS_FILE = [
    "environment_atmosphere",
    "symbolic_metaphor",
    "hook_visual",
    "character_emotion",
]

INTENT_API = {
    "environment_atmosphere": "ENVIRONMENT_ATMOSPHERE",
    "symbolic_metaphor": "SYMBOLIC_METAPHOR",
    "hook_visual": "HOOK_VISUAL",
    "character_emotion": "CHARACTER_EMOTION",
}

STYLES = [
    "soft_ghibli_s00",
    "minimalist_line_art_s01",
    "watercolor_wash_s02",
    "lofi_chill_s03",
    "collage_s04",
    "sketchy_rough_s05",
    "geometric_abstract_s06",
]

STYLE_PROMPTS: dict[str, str] = {
    "soft_ghibli_s00": "Studio Ghibli inspired soft cel shading, warm pastoral anime film still",
    "minimalist_line_art_s01": "minimalist ink line art, sparse contours, generous negative space",
    "watercolor_wash_s02": "watercolor pigment wash on cold press paper, soft bleeding edges",
    "lofi_chill_s03": "lo-fi chill aesthetic, cozy muted palette, subtle analog grain",
    "collage_s04": "layered paper collage, cut edges and mixed paper texture",
    "sketchy_rough_s05": "rough graphite sketch, gestural lines, light construction marks",
    "geometric_abstract_s06": "geometric abstract composition, soft gradients, calm balance",
}


def _stem(intent: str, style: str, landscape: bool) -> str:
    base = f"{intent}_{style}"
    return f"{base}_landscape" if landscape else base


def _expected_path(bank: Path, topic: str, intent: str, style: str, landscape: bool) -> Path:
    return bank / topic / f"{_stem(intent, style, landscape)}.png"


def run_audit(bank: Path) -> dict[str, object]:
    per_topic: dict[str, dict[str, int]] = {}
    missing_by_topic: dict[str, list[str]] = {}
    total_needed = total_found = 0
    for topic in TOPICS_15:
        found = missing = 0
        miss: list[str] = []
        for intent in INTENTS_FILE:
            for style in STYLES:
                for landscape in (False, True):
                    total_needed += 1
                    p = _expected_path(bank, topic, intent, style, landscape)
                    if p.is_file() and p.stat().st_size > 0:
                        found += 1
                        total_found += 1
                    else:
                        missing += 1
                        miss.append(str(p.relative_to(REPO_ROOT)))
        per_topic[topic] = {"found": found, "missing": missing, "pct": (found * 100) // 56}
        if miss:
            missing_by_topic[topic] = miss
    topics_with_any = sum(1 for t in TOPICS_15 if per_topic[t]["found"] > 0)
    topics_complete = [t for t in TOPICS_15 if per_topic[t]["found"] == 56]
    return {
        "per_topic": per_topic,
        "missing_by_topic": missing_by_topic,
        "total_found": total_found,
        "total_needed": total_needed,
        "topics_with_any": topics_with_any,
        "topics_complete": topics_complete,
    }


def _write_audit_report(path: Path, data: dict[str, object]) -> None:
    lines = [
        f"Stillness Press image bank audit — {time.strftime('%Y-%m-%d %H:%M:%S %Z')}",
        "=" * 60,
        "",
    ]
    per_topic = data["per_topic"]  # type: ignore[assignment]
    for topic in TOPICS_15:
        row = per_topic[topic]  # type: ignore[index]
        lines.append(f"{topic}: {row['found']}/56 ({row['pct']}%)")
        miss = data["missing_by_topic"].get(topic, [])  # type: ignore[union-attr]
        if miss:
            lines.append("  Missing:")
            for m in miss[:400]:
                lines.append(f"    {m}")
            if len(miss) > 400:
                lines.append(f"    ... and {len(miss) - 400} more paths")
        lines.append("")
    lines.append("=" * 60)
    lines.append(
        f"TOTAL: {data['total_found']}/{data['total_needed']} found "  # type: ignore[index]
        f"({data['total_needed'] - data['total_found']} missing)"  # type: ignore[index]
    )
    lines.append(f"Topics with any assets: {data['topics_with_any']}/15")  # type: ignore[index]
    lines.append(f"Topics at 100%: {len(data['topics_complete'])}")  # type: ignore[index]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _build_positive(
    topic: str,
    intent_file: str,
    style: str,
    *,
    landscape: bool,
) -> tuple[str, str, float, int]:
    from scripts.video.flux_client import get_prompt_for_topic_scene, load_yaml

    api_intent = INTENT_API[intent_file]
    scenes_cfg = load_yaml("config/video/flux_bank_scenes.yaml")
    intent_map = scenes_cfg.get("visual_intent_scenes") or {}
    default_scene = scenes_cfg.get("default_scene") or "a contemplative moment, soft light, generous negative space, no faces"
    scene = (intent_map.get(api_intent) or {}).get("scene") or default_scene
    prompt, negative, guidance, seed = get_prompt_for_topic_scene(topic, scene)
    style_hint = STYLE_PROMPTS.get(style, "")
    ratio = (
        "16:9 widescreen composition, cinematic horizontal framing, subject readable at distance."
        if landscape
        else "9:16 vertical portrait composition, centered subject, generous headroom."
    )
    brand = (
        "Stillness Press iyashikei healing manga illustration, contemplative mood, no readable text, "
        "no logos, no photoreal faces."
    )
    positive = f"{prompt}\n\nStyle: {style_hint}\n{ratio}\n{brand}"
    return positive, negative, guidance, seed


def _generate_one_comfyui(
    topic: str,
    intent_file: str,
    style: str,
    landscape: bool,
    out_path: Path,
    comfyui_url: str,
) -> None:
    from scripts.video.flux_client import call_comfyui

    positive, negative, guidance, seed = _build_positive(
        topic, intent_file, style, landscape=landscape
    )
    h = hashlib.sha256(f"{topic}|{intent_file}|{style}|{landscape}|cu".encode()).hexdigest()
    seed_i = (int(h[:8], 16) ^ int(seed)) % (2**31 - 1)
    w, h_px = (1024, 576) if landscape else (576, 1024)
    image_bytes = call_comfyui(
        comfyui_url,
        prompt=positive[:6000],
        negative_prompt=negative,
        width=w,
        height=h_px,
        guidance=guidance,
        seed=seed_i,
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(image_bytes)


def _generate_one_cloudflare(
    topic: str,
    intent_file: str,
    style: str,
    landscape: bool,
    out_path: Path,
    account_id: str,
    api_token: str,
) -> None:
    from scripts.video.flux_client import call_flux

    positive, negative, guidance, seed = _build_positive(
        topic, intent_file, style, landscape=landscape
    )
    # Derive per-asset seed
    h = hashlib.sha256(f"{topic}|{intent_file}|{style}|{landscape}".encode()).hexdigest()
    seed_i = (int(h[:8], 16) ^ seed) % (2**31 - 1)
    w, h_px = (1024, 576) if landscape else (576, 1024)
    image_bytes = call_flux(
        account_id=account_id,
        api_token=api_token,
        prompt=positive,
        negative_prompt=negative,
        width=w,
        height=h_px,
        guidance=guidance,
        seed=seed_i,
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(image_bytes)


def _generate_one_runcomfy(
    topic: str,
    intent_file: str,
    style: str,
    landscape: bool,
    out_path: Path,
    api_key: str,
    deployment_id: str,
) -> None:
    from scripts.image_generation.runcomfy_batch import (
        submit_inference,
        poll_request,
        get_result,
        download_image,
    )

    positive, _neg, guidance, seed = _build_positive(
        topic, intent_file, style, landscape=landscape
    )
    h = hashlib.sha256(f"{topic}|{intent_file}|{style}|{landscape}|rc".encode()).hexdigest()
    seed_i = (int(h[:8], 16) ^ int(seed)) % (2**31 - 1)
    # RunComfy template ignores explicit dimensions in overrides; ratio hint stays in prompt.
    _ = guidance  # workflow owns steps; guidance in prompt only for this path
    resp = submit_inference(
        api_key=api_key,
        deployment_id=deployment_id,
        positive_prompt=positive[:4800],
        seed=seed_i,
    )
    request_id = resp.get("request_id", "unknown")
    status_url = resp.get("status_url", "")
    result_url = resp.get("result_url", "")
    if not status_url:
        base = f"https://api.runcomfy.net/prod/v1/deployments/{deployment_id}/requests/{request_id}"
        status_url = f"{base}/status"
        result_url = f"{base}/result"
    poll_resp = poll_request(api_key, status_url, max_wait=360, interval=5)
    status = poll_resp.get("status", "unknown")
    if status not in ("succeeded", "completed"):
        raise RuntimeError(f"RunComfy status={status} err={poll_resp.get('error')}")
    result_resp = get_result(api_key, result_url)
    from scripts.image_generation.runcomfy_batch import extract_image_url

    url = extract_image_url(result_resp)
    if not url:
        raise RuntimeError("RunComfy: no image URL in result")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    download_image(url, out_path)


def cmd_audit(args: argparse.Namespace) -> int:
    bank = Path(args.bank).resolve()
    data = run_audit(bank)
    _write_audit_report(Path(args.out), data)
    print(json.dumps({k: v for k, v in data.items() if k != "missing_by_topic"}, indent=2))
    print(f"Wrote {args.out}")
    return 0


def cmd_generate(args: argparse.Namespace) -> int:
    bank = Path(args.bank).resolve()
    data = run_audit(bank)
    planned: list[tuple[str, str, str, bool, Path]] = []
    for topic in TOPICS_15:
        for intent in INTENTS_FILE:
            for style in STYLES:
                for landscape in (False, True):
                    p = _expected_path(bank, topic, intent, style, landscape)
                    if p.is_file() and p.stat().st_size > 0:
                        continue
                    planned.append((topic, intent, style, landscape, p))

    if args.topics:
        allow = set(args.topics.split(","))
        planned = [x for x in planned if x[0] in allow]

    if args.max_new is not None:
        planned = planned[: int(args.max_new)]

    if args.dry_run:
        print(f"Would generate {len(planned)} images (backend={args.backend})")
        for row in planned[:50]:
            print(f"  {row[4].relative_to(REPO_ROOT)}")
        if len(planned) > 50:
            print(f"  ... {len(planned) - 50} more")
        return 0

    if args.backend == "comfyui":
        comfy = os.environ.get("COMFYUI_URL", "").strip().rstrip("/")
        if not comfy:
            print("COMFYUI_URL required for comfyui backend", file=sys.stderr)
            return 1
        for i, (topic, intent, style, landscape, out_path) in enumerate(planned):
            print(f"[{i+1}/{len(planned)}] {out_path.relative_to(REPO_ROOT)}")
            _generate_one_comfyui(topic, intent, style, landscape, out_path, comfy)
            time.sleep(float(args.sleep_s))
    elif args.backend == "cloudflare":
        from scripts.video.flux_client import load_credentials

        account_id, api_token = load_credentials(for_workers_ai_image=True)
        if not account_id or not api_token:
            print("Missing CLOUDFLARE_ACCOUNT_ID / CLOUDFLARE_API_TOKEN", file=sys.stderr)
            return 1
        for i, (topic, intent, style, landscape, out_path) in enumerate(planned):
            print(f"[{i+1}/{len(planned)}] {out_path.relative_to(REPO_ROOT)}")
            _generate_one_cloudflare(
                topic, intent, style, landscape, out_path, account_id, api_token
            )
            time.sleep(float(args.sleep_s))
    else:
        api_key = args.api_key or os.environ.get("RUNCOMFY_API_KEY", "").strip()
        if not api_key:
            print("Missing RunComfy API key", file=sys.stderr)
            return 1
        dep = args.deployment_id or os.environ.get(
            "RUNCOMFY_DEPLOYMENT_ID", "677edba8-ace0-4b2b-bad2-8e94b9959065"
        )
        for i, (topic, intent, style, landscape, out_path) in enumerate(planned):
            print(f"[{i+1}/{len(planned)}] {out_path.relative_to(REPO_ROOT)}")
            _generate_one_runcomfy(topic, intent, style, landscape, out_path, api_key, dep)
            time.sleep(float(args.sleep_s))

    return 0


def _layer_type(intent_file: str) -> str:
    if intent_file == "character_emotion":
        return "character"
    if intent_file == "environment_atmosphere":
        return "environment"
    if intent_file == "symbolic_metaphor":
        return "symbolic"
    return "environment"


def cmd_index(args: argparse.Namespace) -> int:
    bank = Path(args.bank).resolve()
    out_path = Path(args.out).resolve()
    assets: list[dict[str, object]] = []
    for topic_dir in sorted(bank.iterdir()):
        if not topic_dir.is_dir():
            continue
        topic = topic_dir.name
        for img in sorted(topic_dir.glob("*.png")):
            stem = img.stem
            is_landscape = stem.endswith("_landscape")
            core = stem[: -len("_landscape")] if is_landscape else stem
            intent_file = ""
            rest = core
            for cand in sorted(INTENTS_FILE, key=len, reverse=True):
                if core.startswith(cand + "_"):
                    intent_file = cand
                    rest = core[len(cand) + 1 :]
                    break
            api_intent = INTENT_API.get(intent_file, "HOOK_VISUAL")
            style_slug = rest if rest else "unknown"
            rel_file = str(img.relative_to(REPO_ROOT))
            compat = (
                {"16:9": 1.0, "9:16": 0.75}
                if is_landscape
                else {"9:16": 1.0, "16:9": 0.72}
            )
            assets.append(
                {
                    "asset_id": f"stillness_press_{topic}_{stem}",
                    "layer_type": _layer_type(intent_file),
                    "visual_intent": api_intent,
                    "tags": [topic, "stillness_press", style_slug, "iyashikei"],
                    "style_version": "v1",
                    "composition_compat": compat,
                    "file_path": rel_file,
                    "brand": "stillness_press",
                    "topic": topic,
                    "filename": rel_file,
                    "is_landscape": is_landscape,
                }
            )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(assets, indent=2) + "\n", encoding="utf-8")
    topics_n = len({str(a["topic"]) for a in assets})
    print(f"Indexed {len(assets)} assets across {topics_n} topics → {out_path}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Stillness Press manga image bank tools")
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("audit", help="Write gap report")
    a.add_argument("--bank", default=str(REPO_ROOT / "image_bank" / "stillness_press"))
    a.add_argument(
        "--out",
        default=str(REPO_ROOT / "artifacts" / "manga" / "stillness_press_image_bank_audit.txt"),
    )
    a.set_defaults(func=cmd_audit)

    g = sub.add_parser("generate", help="Fill missing PNGs")
    g.add_argument("--bank", default=str(REPO_ROOT / "image_bank" / "stillness_press"))
    g.add_argument(
        "--backend",
        choices=("comfyui", "cloudflare", "runcomfy"),
        default="comfyui",
    )
    g.add_argument("--api-key", default="", help="RunComfy API key (or env RUNCOMFY_API_KEY)")
    g.add_argument("--deployment-id", default="")
    g.add_argument("--topics", default=None, help="Comma-separated topic filter for missing slots")
    g.add_argument("--max-new", type=int, default=None, help="Cap number of new images")
    g.add_argument("--sleep-s", type=float, default=0.35, help="Pause between API calls")
    g.add_argument("--dry-run", action="store_true")
    g.set_defaults(func=cmd_generate)

    i = sub.add_parser("index", help="Rebuild image_bank/index.json from disk")
    i.add_argument("--bank", default=str(REPO_ROOT / "image_bank" / "stillness_press"))
    i.add_argument("--out", default=str(REPO_ROOT / "image_bank" / "index.json"))
    i.set_defaults(func=cmd_index)

    args = ap.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
