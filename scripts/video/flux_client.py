# DEMOTED: Cloudflare FLUX is fallback only. Primary image generation uses ComfyUI on Pearl Star.
"""
Image generation client: ComfyUI (primary) or Cloudflare Workers AI FLUX (fallback).
Load credentials, build prompts from config, call image gen API.
Used by: run_flux_generate.py, run_flux_bank_build.py, generate_author_cover_art_flux.py.
"""
from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def load_yaml(rel_path: str) -> dict:
    path = REPO_ROOT / rel_path
    if not path.exists():
        return {}
    try:
        import yaml
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except ImportError:
        raise RuntimeError("PyYAML required; pip install pyyaml")


def load_credentials(*, for_workers_ai_image: bool = False) -> tuple[str, str]:
    """Load CLOUDFLARE_ACCOUNT_ID and an API token from env, .env, or key file.

    ``for_workers_ai_image=True`` (Workers AI / FLUX REST): prefer
    ``CLOUDFLARE_AI_API_TOKEN`` when set, then ``CLOUDFLARE_API_TOKEN``.
    This avoids using a generic Cloudflare API token (Pages/DNS/etc.) that
    returns 401 on ``/accounts/.../ai/run/...``.

    Default ``False``: prefer ``CLOUDFLARE_API_TOKEN`` for backward compatibility.
    """
    try:
        from dotenv import load_dotenv
        load_dotenv(REPO_ROOT / ".env")
    except ImportError:
        pass
    for name in ("cloudflare_workers_ai.txt", "11.txt"):
        path = REPO_ROOT / name
        if not path.exists():
            continue
        raw = path.read_text(encoding="utf-8").strip()
        for line in raw.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            for key in ("CLOUDFLARE_ACCOUNT_ID", "CLOUDFLARE_API_TOKEN", "CLOUDFLARE_AI_API_TOKEN"):
                if os.environ.get(key, "").strip():
                    continue
                if line.startswith(key + "=") or line.startswith(key + ":"):
                    sep = "=" if "=" in line else ":"
                    val = line.split(sep, 1)[-1].strip().strip('"').strip("'")
                    if val and not val.startswith("$"):
                        os.environ[key] = val
                        break
    account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "").strip()
    ai = os.environ.get("CLOUDFLARE_AI_API_TOKEN", "").strip()
    general = os.environ.get("CLOUDFLARE_API_TOKEN", "").strip()
    if for_workers_ai_image:
        api_token = ai or general
    else:
        api_token = general or ai
    return account_id, api_token


def _workers_ai_bearer_candidates(primary_token: str) -> list[str]:
    """Ordered unique bearer tokens to try for Workers AI (401 fallback)."""
    ai = os.environ.get("CLOUDFLARE_AI_API_TOKEN", "").strip()
    general = os.environ.get("CLOUDFLARE_API_TOKEN", "").strip()
    out: list[str] = []
    for t in (primary_token.strip(), ai, general):
        if t and t not in out:
            out.append(t)
    return out


def _build_master_prompt_string(
    scene_description: str,
    palette_prompt_names: list[str],
    band_never_rules: list[str],
    no_adoration: list[str],
    shared_negatives: list[str],
    *,
    anchor_fragment: str | None = None,
) -> str:
    """Build positive prompt (foreground → Background: → Overall lighting:)."""
    palette_str = ", ".join(palette_prompt_names)
    foreground = (
        f"A soft hand-painted gouache illustration of {scene_description}, "
        f"in {palette_str}, soft brush texture, gentle paper-like grain, "
        "centered composition, generous negative space, no faces, contemplative mood."
    )
    if anchor_fragment:
        foreground = f"{foreground} Include {anchor_fragment}."
    background = (
        f"Background: an atmospheric abstract gradient of {palette_str}, "
        "with gentle depth, clean edges, soft tonal separation."
    )
    lighting = (
        "Overall lighting: soft ambient light, quiet and undramatic, "
        "no overexposure, grounded, 9:16, highly detailed but soft."
    )
    return f"{foreground}\n\n{background}\n\n{lighting}"


def build_master_prompt(
    *args: Any,
    topic: str | None = None,
    visual_intent: str | None = None,
    anchor_fragment: str | None = None,
) -> str | dict[str, str]:
    """
    Build the master positive prompt, or (when topic= is passed) return positive/negative dict.

    Positional form (5 args): scene_description, palette_prompt_names, band_never_rules,
    no_adoration, shared_negatives — returns a single positive string.

    Keyword form: topic=..., visual_intent=... — loads scene from flux_bank_scenes.yaml and
    returns {"positive", "negative", "guidance", "seed"}.
    """
    if topic is not None:
        if args:
            raise TypeError("build_master_prompt: use either positional (5 args) or topic=, not both")
        return _build_master_prompt_dict(topic, visual_intent)
    if len(args) != 5:
        raise TypeError(
            "build_master_prompt expects 5 positional arguments "
            "(scene_description, palette_prompt_names, band_never_rules, no_adoration, shared_negatives) "
            "or keyword arguments topic= and optional visual_intent="
        )
    scene_description, palette_prompt_names, band_never_rules, no_adoration, shared_negatives = args
    return _build_master_prompt_string(
        scene_description,
        palette_prompt_names,
        band_never_rules,
        no_adoration,
        shared_negatives,
        anchor_fragment=anchor_fragment,
    )


def _build_master_prompt_dict(topic: str, visual_intent: str | None) -> dict[str, str]:
    scenes_cfg = load_yaml("config/video/flux_bank_scenes.yaml")
    intent_map = scenes_cfg.get("visual_intent_scenes") or {}
    default_scene = scenes_cfg.get("default_scene") or (
        "a contemplative moment, soft light, generous negative space, no faces"
    )
    intent_key = visual_intent or "HOOK_VISUAL"
    scene = (intent_map.get(intent_key) or {}).get("scene") or default_scene
    prompt, negative, guidance, seed = get_prompt_for_topic_scene(topic, scene)
    return {
        "positive": prompt,
        "negative": negative,
        "guidance": str(guidance),
        "seed": str(seed),
    }


def build_negative_block(
    band_never_rules: list[str],
    no_adoration: list[str],
    shared_negatives: list[str],
    extra_never: list[str] | None = None,
) -> str:
    """Combine never_rules + no_adoration + shared_negatives + optional topic never list."""
    parts = list(band_never_rules)
    parts.extend(no_adoration)
    parts.extend(shared_negatives)
    if extra_never:
        parts.extend(extra_never)
    return ", ".join(parts)


def get_prompt_for_topic_scene(topic: str, scene_description: str) -> tuple[str, str, float, int]:
    """
    Load config for topic, build prompt and negative block. Returns (prompt, negative, guidance, seed).
    """
    tokens = load_yaml("config/video/brand_style_tokens.yaml")
    constraints = load_yaml("config/video/prompt_constraints.yaml")
    band_name = tokens.get("topic_to_band", {}).get(topic, "cool_calm")
    bands = tokens.get("bands", {})
    band = bands.get(band_name, {})
    topics_cfg = band.get("topics", {})
    topic_cfg = topics_cfg.get(topic, {})
    palette = topic_cfg.get("palette", [])
    palette_prompt_names = [p.get("prompt_name", "") for p in palette if p.get("prompt_name")]
    if not palette_prompt_names:
        palette_prompt_names = ["slate blue grey", "pale mist blue", "pale mist"]
    band_never = band.get("never_rules", [])
    gen_spec = band.get("generation_spec", {})
    seed = int(gen_spec.get("shnell_seed", 739204))
    guidance = float(gen_spec.get("guidance", 3.0))
    no_adoration = constraints.get("no_adoration", [])
    shared_negatives = constraints.get("shared_negatives", [])
    prompt_rules = topic_cfg.get("prompt_rules") or {}
    anchor_fragment = None
    if prompt_rules.get("require_dark_anchor"):
        anchor_fragment = prompt_rules.get("anchor_description", "").strip() or None
    extra_never = list(prompt_rules.get("never") or [])
    prompt = _build_master_prompt_string(
        scene_description,
        palette_prompt_names,
        band_never,
        no_adoration,
        shared_negatives,
        anchor_fragment=anchor_fragment,
    )
    negative = build_negative_block(band_never, no_adoration, shared_negatives, extra_never=extra_never)
    return prompt, negative, guidance, seed


def call_flux(
    account_id: str,
    api_token: str,
    prompt: str,
    negative_prompt: str,
    width: int = 576,
    height: int = 1024,
    steps: int = 25,
    guidance: float = 3.0,
    seed: int = 739204,
    model: str = "@cf/black-forest-labs/flux-2-dev",
) -> bytes:
    """POST to Cloudflare Workers AI FLUX; returns image bytes."""
    import requests

    if not account_id.strip() or not api_token.strip():
        account_id, api_token = load_credentials(for_workers_ai_image=True)
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model}"
    full_prompt = f"{prompt}\n\nAvoid: {negative_prompt}" if negative_prompt else prompt
    payload = {
        "prompt": (None, full_prompt),
        "width": (None, str(width)),
        "height": (None, str(height)),
        "steps": (None, str(steps)),
        "guidance": (None, str(guidance)),
        "seed": (None, str(seed)),
    }
    candidates = _workers_ai_bearer_candidates(api_token)
    if not candidates:
        raise RuntimeError(
            "Cloudflare FLUX: set CLOUDFLARE_AI_API_TOKEN (Workers AI) or CLOUDFLARE_API_TOKEN with Workers AI scope"
        )
    last_resp = None
    out: bytes = b""
    for bearer in candidates:
        last_resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {bearer}"},
            files=payload,
            timeout=120,
        )
        if last_resp.status_code == 401:
            continue
        last_resp.raise_for_status()
        out = last_resp.content
        break
    else:
        detail = ""
        if last_resp is not None:
            detail = f" last_http={last_resp.status_code} body={last_resp.text[:400]!r}"
        raise RuntimeError(f"Cloudflare FLUX: all bearer token attempts failed.{detail}")
    try:
        obj = json.loads(out.decode("utf-8"))
    except Exception:
        return out
    if not obj.get("success", True):
        raise RuntimeError(f"API errors: {obj.get('errors', [])}")
    result = obj.get("result", obj)
    if isinstance(result, dict) and "image" in result:
        return base64.b64decode(result["image"])
    if isinstance(result, str):
        return base64.b64decode(result)
    raise RuntimeError(f"Unexpected API response: {type(result)}")


# ── ComfyUI (PRIMARY — local Pearl Star server) ──


def get_image_provider() -> tuple[str, dict[str, str]]:
    """Return (provider_name, params) based on environment.

    Priority: COMFYUI_URL → comfyui, else → cloudflare.
    Does NOT change load_credentials() signature for backward compatibility.
    """
    comfyui_url = os.environ.get("COMFYUI_URL", "").strip()
    if comfyui_url:
        return "comfyui", {"url": comfyui_url}
    account_id, api_token = load_credentials(for_workers_ai_image=True)
    return "cloudflare", {"account_id": account_id, "api_token": api_token}


def call_comfyui(
    comfyui_url: str,
    prompt: str,
    negative_prompt: str,
    width: int = 576,
    height: int = 1024,
    steps: int = 25,
    guidance: float = 3.0,
    seed: int = 739204,
) -> bytes:
    """Submit prompt to ComfyUI and return image bytes."""
    import time
    import urllib.request

    workflow_path = REPO_ROOT / "scripts" / "image_generation" / "comfyui_workflows" / "flux_video_bank.json"
    workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
    workflow = {k: v for k, v in workflow.items() if k != "_meta"}
    if "5" in workflow:
        workflow["5"]["inputs"]["width"] = int(width)
        workflow["5"]["inputs"]["height"] = int(height)
    if "6" in workflow:
        workflow["6"]["inputs"]["text"] = prompt
    if "7" in workflow:
        workflow["7"]["inputs"]["text"] = negative_prompt if negative_prompt else " "
    if "25" in workflow:
        workflow["25"]["inputs"]["noise_seed"] = seed
    elif "3" in workflow:
        workflow["3"]["inputs"]["seed"] = seed

    url = comfyui_url.rstrip("/")
    payload = json.dumps({"prompt": workflow}).encode("utf-8")
    req = urllib.request.Request(f"{url}/prompt", data=payload,
                                headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        prompt_id = json.loads(resp.read())["prompt_id"]

    deadline = time.monotonic() + 300
    while time.monotonic() < deadline:
        time.sleep(3)
        hreq = urllib.request.Request(f"{url}/history/{prompt_id}")
        with urllib.request.urlopen(hreq, timeout=15) as hresp:
            history = json.loads(hresp.read())
        if prompt_id in history:
            outputs = history[prompt_id].get("outputs", {})
            for node_out in outputs.values():
                images = node_out.get("images", [])
                if images:
                    img = images[0]
                    import urllib.parse
                    params = urllib.parse.urlencode({
                        "filename": img["filename"],
                        "subfolder": img.get("subfolder", ""),
                        "type": img.get("type", "output"),
                    })
                    with urllib.request.urlopen(f"{url}/view?{params}", timeout=60) as iresp:
                        return iresp.read()
    raise RuntimeError(f"ComfyUI prompt {prompt_id} timed out")
