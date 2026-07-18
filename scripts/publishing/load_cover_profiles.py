#!/usr/bin/env python3
"""Loader + validator for config/publishing/platform_cover_profiles.yaml.

Pure CPU, no image libraries. Lets exporters (lanes 3-4, after PR #4269) read
per-platform sizes / formats / safe-areas from config instead of hardcoding.

Authority: docs/authoring/BOOK_COVER_UNIFIED_RESEARCH_2026-07-01.md §3/§4/§7 lane 1.

Public API:
    load_cover_profiles(path=None) -> dict          # full parsed registry
    get_profiles(path=None) -> dict[str, dict]      # profiles map only
    get_profile(key, path=None) -> dict             # single profile
    validate_profiles(registry) -> list[str]        # [] == valid; else errors
    aspect_matches(profile, w, h, tol=...) -> bool  # asset-vs-profile aspect check
    launch_order(path=None) -> list[str]            # keys sorted by launch_priority

CLI:
    python3 scripts/publishing/load_cover_profiles.py            # validate, print summary
    python3 scripts/publishing/load_cover_profiles.py --json     # emit parsed registry as JSON
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

# Repo-root relative default; resolved from this file's location.
_DEFAULT_PATH = (
    Path(__file__).resolve().parents[2]
    / "config"
    / "publishing"
    / "platform_cover_profiles.yaml"
)

ASPECT_TOL = 0.01  # decimal aspect tolerance for w/h == declared decimal

REQUIRED_KEYS = (
    "platform",
    "surface",
    "aspect_ratio",
    "size_recommended",
    "size_min",
    "formats",
    "color_mode",
    "dpi_min",
    "dpi_recommended",
    "max_file_mb",
    "borders_allowed",
    "letterbox_allowed",
    "marketing_copy_allowed",
    "safe_area",
    "launch_priority",
    "source_url",
    "source_verified",
)
VALID_SURFACES = {"ebook", "audiobook"}


def load_cover_profiles(path: str | Path | None = None) -> dict:
    """Parse the YAML registry and return the full mapping."""
    if yaml is None:  # pragma: no cover
        raise RuntimeError("PyYAML is required to load platform_cover_profiles.yaml")
    p = Path(path) if path else _DEFAULT_PATH
    with open(p, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"{p}: top-level YAML is not a mapping")
    return data


def get_profiles(path: str | Path | None = None) -> dict:
    return load_cover_profiles(path).get("profiles", {})


def get_profile(key: str, path: str | Path | None = None) -> dict:
    profiles = get_profiles(path)
    if key not in profiles:
        raise KeyError(f"no cover profile named {key!r}")
    return profiles[key]


def _dims(size: dict) -> tuple[int | None, int | None]:
    """Extract (w, h) from a size mapping. min-dimension-only sizes return (None, None)."""
    if size is None:
        return (None, None)
    if "width" in size and "height" in size:
        return (int(size["width"]), int(size["height"]))
    return (None, None)


def validate_profiles(registry: dict) -> list[str]:
    """Return a list of human-readable errors; empty list means the registry is valid."""
    errors: list[str] = []
    profiles = registry.get("profiles")
    if not isinstance(profiles, dict) or not profiles:
        return ["registry has no 'profiles' mapping"]

    for key, prof in profiles.items():
        if not isinstance(prof, dict):
            errors.append(f"{key}: profile is not a mapping")
            continue

        for req in REQUIRED_KEYS:
            if req not in prof:
                errors.append(f"{key}: missing required key '{req}'")

        surface = prof.get("surface")
        if surface not in VALID_SURFACES:
            errors.append(f"{key}: surface {surface!r} not in {sorted(VALID_SURFACES)}")

        # launch_priority present + int
        lp = prof.get("launch_priority")
        if not isinstance(lp, int):
            errors.append(f"{key}: launch_priority must be an int, got {lp!r}")

        # aspect decimal == w/h within tolerance (when both a decimal and w/h exist)
        ar = prof.get("aspect_ratio") or {}
        decimal = ar.get("decimal")
        w_rec, h_rec = _dims(prof.get("size_recommended"))
        if decimal is not None and w_rec and h_rec:
            got = w_rec / h_rec
            if abs(got - decimal) > ASPECT_TOL:
                errors.append(
                    f"{key}: aspect decimal {decimal} != size_recommended "
                    f"{w_rec}x{h_rec} ratio {got:.4f} (tol {ASPECT_TOL})"
                )

        # size_min <= size_recommended (per axis), when both are full W/H
        w_min, h_min = _dims(prof.get("size_min"))
        if w_min and h_min and w_rec and h_rec:
            if w_min > w_rec or h_min > h_rec:
                errors.append(
                    f"{key}: size_min {w_min}x{h_min} exceeds "
                    f"size_recommended {w_rec}x{h_rec}"
                )

        # formats must be a non-empty ordered list
        fmts = prof.get("formats")
        if not isinstance(fmts, list) or not fmts:
            errors.append(f"{key}: formats must be a non-empty list")

    return errors


def aspect_matches(profile: dict, width: int, height: int, tol: float = ASPECT_TOL) -> bool:
    """True if an asset of (width, height) matches this profile's declared aspect.

    Profiles without a fixed decimal aspect (e.g. generic 'portrait') accept any
    portrait asset (height >= width).
    """
    ar = profile.get("aspect_ratio") or {}
    decimal = ar.get("decimal")
    if decimal is None:
        return height >= width  # generic portrait/no-fixed-ratio surfaces
    return abs((width / height) - decimal) <= tol


def launch_order(path: str | Path | None = None) -> list[str]:
    """Profile keys sorted by (launch_priority, key)."""
    profiles = get_profiles(path)
    return sorted(profiles, key=lambda k: (profiles[k].get("launch_priority", 99), k))


def main(argv: list[str]) -> int:
    path = None
    as_json = "--json" in argv
    registry = load_cover_profiles(path)
    errors = validate_profiles(registry)
    if as_json:
        print(json.dumps(registry, indent=2, sort_keys=True))
        return 0 if not errors else 1
    profiles = registry.get("profiles", {})
    print(f"platform_cover_profiles.yaml: {len(profiles)} profiles")
    for key in launch_order():
        p = profiles[key]
        ar = p.get("aspect_ratio", {})
        rec = p.get("size_recommended", {})
        print(
            f"  [P{p.get('launch_priority')}] {key:28s} "
            f"{p.get('surface'):9s} {ar.get('ratio'):>8s} "
            f"rec {rec.get('width')}x{rec.get('height')}"
        )
    if errors:
        print(f"\nVALIDATION FAILED ({len(errors)} error(s)):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print("\nVALIDATION OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
