"""Load per-brand GHL / funnel marketing profiles."""
from __future__ import annotations

from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REGISTRY_PATH = REPO_ROOT / "config" / "marketing" / "brand_marketing_registry.yaml"


def _load_yaml(path: Path) -> dict[str, Any]:
    import yaml

    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def load_registry(path: Path | None = None) -> dict[str, Any]:
    return _load_yaml(path or REGISTRY_PATH)


def list_brands(
    *,
    ghl_enabled_only: bool = False,
    rollout_phase: str | None = None,
    registry: dict[str, Any] | None = None,
) -> list[str]:
    reg = registry or load_registry()
    brands = reg.get("brands") or {}
    out: list[str] = []
    for brand_id, profile in sorted(brands.items()):
        if not isinstance(profile, dict):
            continue
        if ghl_enabled_only and not profile.get("ghl_enabled"):
            continue
        if rollout_phase and profile.get("rollout_phase") != rollout_phase:
            continue
        out.append(brand_id)
    return out


def get_brand_profile(brand_id: str, registry: dict[str, Any] | None = None) -> dict[str, Any]:
    reg = registry or load_registry()
    defaults = dict(reg.get("defaults") or {})
    brands = reg.get("brands") or {}
    row = brands.get(brand_id)
    if not isinstance(row, dict):
        raise KeyError(f"Unknown brand in brand_marketing_registry: {brand_id}")
    merged = {**defaults, **row, "brand_id": brand_id}
    return merged


def resolve_funnel_landing_path(profile: dict[str, Any], slug: str) -> str:
    prefix = profile.get("funnel_path_prefix")
    if prefix:
        return f"/free/{prefix}/{slug}/"
    return f"/free/{slug}/"


def resolve_landing_url(profile: dict[str, Any], slug: str) -> str:
    base = str(profile.get("landing_base") or "https://phoenix-brand-admin.pages.dev").rstrip("/")
    path = resolve_funnel_landing_path(profile, slug)
    return f"{base}{path}"
