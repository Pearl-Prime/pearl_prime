"""Render/consumer guard: preview ≠ license (EULA §A).

Social b-roll (and any shipped consumer) must refuse Storyblocks-sourced
assets that lack a LicenseRecord with on-disk HD for the work unit.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts.storyblocks.license_store import LicenseStore, default_license_store


class UnlicensedStoryblocksAssetError(RuntimeError):
    """Preview-only / never-downloaded Storyblocks asset cannot enter render."""


def _provider_of(asset: Any) -> str:
    if asset is None:
        return ""
    if isinstance(asset, dict):
        return str(
            asset.get("source_provider")
            or asset.get("provider")
            or asset.get("source_kind")
            or ""
        ).lower()
    return str(getattr(asset, "source_provider", "") or getattr(asset, "provider", "") or "").lower()


def _stock_id_of(asset: Any) -> str:
    if isinstance(asset, dict):
        return str(
            asset.get("storyblocks_stock_id")
            or asset.get("stock_id")
            or asset.get("asset_id")
            or ""
        )
    return str(
        getattr(asset, "storyblocks_stock_id", None)
        or getattr(asset, "stock_id", None)
        or getattr(asset, "asset_id", "")
        or ""
    )


def is_storyblocks_asset(asset: Any) -> bool:
    provider = _provider_of(asset)
    if "storyblocks" in provider:
        return True
    # Path / URI heuristics for licensed bank
    if isinstance(asset, dict):
        for key in ("local_uri", "path", "source_stock_ref", "uri"):
            val = str(asset.get(key) or "")
            if "storyblocks_licensed" in val or "/storyblocks/" in val:
                return True
    elif isinstance(asset, (str, Path)):
        s = str(asset)
        if "storyblocks_licensed" in s or "source_provider=storyblocks" in s:
            return True
    return False


def assert_storyblocks_licensed_for_consumer(
    asset: Any,
    *,
    work_unit_id: str | None = None,
    license_store: LicenseStore | None = None,
) -> None:
    """
    Raise UnlicensedStoryblocksAssetError if asset is Storyblocks and unlicensed.

    Non-Storyblocks assets pass through (legacy Pexels/Pixabay/etc.).
    """
    if not is_storyblocks_asset(asset):
        return

    store = license_store or default_license_store
    stock_id = _stock_id_of(asset)
    wu = work_unit_id
    if isinstance(asset, dict):
        wu = wu or asset.get("work_unit_id")
        # Allow explicit licensed local_uri that exists + matching sidecar
        local_uri = asset.get("local_uri") or asset.get("path")
        if local_uri and Path(str(local_uri)).exists() and stock_id and wu:
            if store.has_license(str(wu), str(stock_id)):
                return
        if local_uri and Path(str(local_uri)).exists():
            # Sidecar next to HD
            side = Path(str(local_uri)).with_suffix(".license.json")
            # HD may be .mp4; sidecar is {stem}.license.json
            stem_side = Path(str(local_uri)).parent / f"{Path(str(local_uri)).stem}.license.json"
            if side.exists() or stem_side.exists():
                return

    if not wu or not stock_id:
        raise UnlicensedStoryblocksAssetError(
            "Storyblocks asset missing work_unit_id/stock_id; preview grants no license (EULA §A)."
        )
    if not store.has_license(str(wu), str(stock_id)):
        raise UnlicensedStoryblocksAssetError(
            f"Storyblocks asset {stock_id} has no license download for work_unit "
            f"{wu}; preview grants no license (EULA §A)."
        )


def resolve_licensed_path(
    asset: Any,
    *,
    work_unit_id: str | None = None,
    license_store: LicenseStore | None = None,
) -> Path | None:
    """Return on-disk HD path for a licensed Storyblocks asset, else None."""
    assert_storyblocks_licensed_for_consumer(
        asset, work_unit_id=work_unit_id, license_store=license_store
    )
    if not is_storyblocks_asset(asset):
        if isinstance(asset, dict) and asset.get("path"):
            return Path(str(asset["path"]))
        if isinstance(asset, (str, Path)):
            return Path(asset)
        return None
    store = license_store or default_license_store
    stock_id = _stock_id_of(asset)
    wu = work_unit_id or (asset.get("work_unit_id") if isinstance(asset, dict) else None)
    if not wu or not stock_id:
        return None
    rec = store.get(str(wu), str(stock_id))
    if rec and rec.local_uri:
        return Path(rec.local_uri)
    return None
