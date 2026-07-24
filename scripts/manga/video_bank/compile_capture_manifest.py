#!/usr/bin/env python3
"""Compile demanded pose coverage into a character capture manifest.

Inputs (signal-gated, selected by what exists on disk):
  Primary:  series_demand_rollup.yaml  (when manga-bank-demand-rollup-merged)
  Fallback: character_pose_inventory.yaml under bank_contracts/

Output validates against schemas/manga/character_capture_manifest.schema.json.
Does NOT invent fixed pose atlases — only DEMANDED pose_ids drive capture_sets.

Usage:
  PYTHONPATH=. python3 scripts/manga/video_bank/compile_capture_manifest.py \\
    --series-id stillness_en_01 --character-id mira_aoki --outfit-id cream_sweater \\
    --identity-version pulid_sheet_v1 \\
    --anchor-path artifacts/manga/.../mira_aoki_pulid_reference.png \\
    --bank-contracts artifacts/manga/<series>/bank_contracts/character_pose_inventory.yaml \\
    --out artifacts/manga/<series>/video_bank/capture_manifests/mira_aoki__cream_sweater.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

from scripts.manga.video_bank import ALLOWED_CLOUD_ENGINES, SCHEMA_VERSION
from scripts.manga.video_bank._schema import validate_manifest

REPO = Path(__file__).resolve().parents[3]

# Heuristic family assignment from pose_id tokens (deterministic, no LLM).
_FAMILY_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("seated", ("seated", "sit", "sitting")),
    ("locomotion", ("walk", "stand", "turn", "run", "stride", "step")),
    ("dialogue", ("portrait", "bust", "face", "talk", "dialogue", "cu", "mcu")),
]


def _infer_family(pose_id: str) -> str:
    low = pose_id.lower()
    for family, tokens in _FAMILY_RULES:
        if any(tok in low for tok in tokens):
            return family
    return "genre_pack"


def _load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected mapping in {path}")
    return data


def _demanded_from_inventory(inv: dict[str, Any], character_id: str) -> list[str]:
    chars = inv.get("characters") or {}
    if character_id not in chars:
        raise KeyError(f"character_id {character_id!r} not in inventory characters")
    poses = chars[character_id].get("poses") or []
    out: list[str] = []
    for row in poses:
        if not isinstance(row, dict):
            continue
        pid = str(row.get("pose_id") or "").strip()
        if pid:
            out.append(pid)
    if not out:
        raise ValueError(f"no demanded pose_ids for {character_id} in inventory")
    return out


def _demanded_from_rollup(rollup: dict[str, Any], character_id: str, outfit_id: str) -> list[str]:
    """Accept a few common shapes for series_demand_rollup.yaml (Lane 09 TBD)."""
    # Shape A: characters.<id>.outfits.<outfit>.demanded_pose_ids
    chars = rollup.get("characters") or {}
    if character_id in chars:
        node = chars[character_id] or {}
        outfits = node.get("outfits") or {}
        if outfit_id in outfits:
            demanded = outfits[outfit_id].get("demanded_pose_ids") or []
            if demanded:
                return [str(x) for x in demanded]
        demanded = node.get("demanded_pose_ids") or []
        if demanded:
            return [str(x) for x in demanded]
    # Shape B: demanded[] rows with character_id / pose_id
    rows = rollup.get("demanded") or rollup.get("demanded_poses") or []
    out: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        if str(row.get("character_id") or "") != character_id:
            continue
        oid = row.get("outfit_id")
        if oid is not None and str(oid) != outfit_id:
            continue
        pid = str(row.get("pose_id") or "").strip()
        if pid:
            out.append(pid)
    if not out:
        raise ValueError(
            f"no demanded pose_ids for {character_id}/{outfit_id} in rollup"
        )
    # de-dupe preserve order
    seen: set[str] = set()
    uniq: list[str] = []
    for p in out:
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    return uniq


def _group_by_family(pose_ids: list[str]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    for pid in pose_ids:
        fam = _infer_family(pid)
        groups.setdefault(fam, []).append(pid)
    return groups


def _clip_prompt(family: str, outfit_id: str, demanded: list[str]) -> str:
    framing = {
        "dialogue": "MCU bust",
        "locomotion": "full body",
        "seated": "full body seated",
        "genre_pack": "full body comic-readable",
    }.get(family, "full body")
    return (
        f"Single character {framing}, {outfit_id.replace('_', ' ')}, "
        "locked camera, flat neutral high-contrast backdrop, no props, "
        "staged anticipation then impact then settle, comic-readable key poses, "
        f"anime still-frame clarity; demanded poses: {', '.join(demanded)}"
    )


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def resolve_demand_source(
    *,
    rollup_path: Path | None,
    bank_contracts_path: Path | None,
) -> tuple[str, list[str], dict[str, Any]]:
    """Return (mode, demanded_pose_ids, demand_source block)."""
    if rollup_path is not None and rollup_path.is_file():
        rollup = _load_yaml(rollup_path)
        # character/outfit filled by caller via demanded_from_rollup later
        return (
            "series_demand_rollup",
            [],  # filled below when character known — placeholder
            {
                "mode": "series_demand_rollup",
                "rollup_path": str(rollup_path),
                "signal_note": "manga-bank-demand-rollup present on disk — primary demand path.",
                "_rollup": rollup,
            },
        )
    if bank_contracts_path is not None and bank_contracts_path.is_file():
        inv = _load_yaml(bank_contracts_path)
        return (
            "bank_contracts_fallback",
            [],
            {
                "mode": "bank_contracts_fallback",
                "bank_contracts_glob": str(bank_contracts_path),
                "signal_note": (
                    "manga-bank-demand-rollup-merged absent — compile from demanded "
                    "pose_ids in character_pose_inventory only."
                ),
                "_inventory": inv,
            },
        )
    raise FileNotFoundError(
        "neither series_demand_rollup nor bank_contracts inventory found; "
        "pass --rollup and/or --bank-contracts"
    )


def compile_manifest(
    *,
    series_id: str,
    character_id: str,
    outfit_id: str,
    identity_version: str,
    anchor_path: str,
    anchor_source_class: str = "pulid_reference",
    rollup_path: Path | None = None,
    bank_contracts_path: Path | None = None,
    engine: str = "wan2.7-i2v",
    duration_s: int = 5,
    reserve_seconds: float = 10.0,
    provenance_default: str = "INTERIM",
    public_url: str | None = None,
    notes: str = "",
) -> dict[str, Any]:
    if engine not in ALLOWED_CLOUD_ENGINES:
        raise ValueError(
            f"engine {engine!r} not in allowed cloud engines {sorted(ALLOWED_CLOUD_ENGINES)}"
        )
    mode, _, meta = resolve_demand_source(
        rollup_path=rollup_path, bank_contracts_path=bank_contracts_path
    )
    if mode == "series_demand_rollup":
        demanded = _demanded_from_rollup(meta.pop("_rollup"), character_id, outfit_id)
    else:
        demanded = _demanded_from_inventory(meta.pop("_inventory"), character_id)

    groups = _group_by_family(demanded)
    capture_sets: list[dict[str, Any]] = []
    a_idx = 0
    for family, pose_ids in groups.items():
        clip_id = f"{_slug(character_id)}_{_slug(outfit_id)}_{family}_01"
        anchor_mode = "i2v" if engine.endswith("-i2v") else "t2v"
        capture_sets.append(
            {
                "family": family,
                "clip_id": clip_id,
                "a_namespace_id": f"A{a_idx % 10}",
                "prompt": _clip_prompt(family, outfit_id, pose_ids),
                "duration_s": duration_s,
                "engine": engine,
                "anchor_mode": anchor_mode,
                "demanded_pose_ids": pose_ids,
                "sampling_recipe": {
                    "candidate_keyed_samples": 10 if duration_s <= 5 else 14,
                    "bank_keep_target": 5 if duration_s <= 5 else 7,
                },
            }
        )
        a_idx += 1

    planned = float(sum(cs["duration_s"] for cs in capture_sets))
    engine_lane = "dashscope_free_i2v" if engine.endswith("-i2v") else "dashscope_free_t2v"
    demand_source = {k: v for k, v in meta.items() if not k.startswith("_")}
    anchor: dict[str, Any] = {
        "asset_path": anchor_path,
        "source_class": anchor_source_class,
        "outfit_id": outfit_id,
        "identity_version": identity_version,
    }
    if public_url:
        anchor["public_url"] = public_url

    manifest: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "manifest_id": f"{series_id}__{character_id}__{outfit_id}__capture_v1",
        "series_id": series_id,
        "character_id": character_id,
        "identity_version": identity_version,
        "outfit_id": outfit_id,
        "demand_source": demand_source,
        "anchor": anchor,
        "capture_sets": capture_sets,
        "quota_budget": {
            "engine_lane": engine_lane,
            "planned_seconds": planned,
            "reserve_seconds": float(reserve_seconds),
            "sunset_date": "2026-10-18",
            "notes": "Lane 02: skip r2v unless burn_summary proves seconds.",
        },
        "provenance_default": provenance_default,
    }
    if notes:
        manifest["notes"] = notes
    validate_manifest(manifest)
    return manifest


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--series-id", required=True)
    ap.add_argument("--character-id", required=True)
    ap.add_argument("--outfit-id", required=True)
    ap.add_argument("--identity-version", required=True)
    ap.add_argument("--anchor-path", required=True)
    ap.add_argument(
        "--anchor-source-class",
        default="pulid_reference",
        choices=["pulid_reference", "model_sheet", "pearl_star_render", "approved_panel_crop"],
    )
    ap.add_argument("--public-url", default="")
    ap.add_argument("--rollup", type=Path, default=None, help="series_demand_rollup.yaml")
    ap.add_argument(
        "--bank-contracts",
        type=Path,
        default=None,
        help="character_pose_inventory.yaml (fallback when rollup absent)",
    )
    ap.add_argument("--engine", default="wan2.7-i2v", choices=sorted(ALLOWED_CLOUD_ENGINES))
    ap.add_argument("--duration-s", type=int, default=5)
    ap.add_argument("--reserve-seconds", type=float, default=10.0)
    ap.add_argument("--provenance-default", default="INTERIM", choices=["INTERIM", "REAL"])
    ap.add_argument("--notes", default="")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--validate-only", action="store_true", help="Validate an existing --out and exit")
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.validate_only:
        data = json.loads(args.out.read_text(encoding="utf-8"))
        validate_manifest(data)
        print(json.dumps({"ok": True, "manifest_id": data.get("manifest_id")}, indent=2))
        return 0

    # Prefer rollup when present on disk (primary per supply spec §2.1).
    rollup = args.rollup
    bank = args.bank_contracts
    if rollup is None and bank is None:
        print("ERROR: pass --rollup and/or --bank-contracts", file=sys.stderr)
        return 2

    use_rollup = rollup is not None and Path(rollup).is_file()
    use_bank = (not use_rollup) and bank is not None and Path(bank).is_file()
    if not use_rollup and not use_bank:
        print("ERROR: demand source path not found on disk", file=sys.stderr)
        return 2

    manifest = compile_manifest(
        series_id=args.series_id,
        character_id=args.character_id,
        outfit_id=args.outfit_id,
        identity_version=args.identity_version,
        anchor_path=args.anchor_path,
        anchor_source_class=args.anchor_source_class,
        rollup_path=rollup if use_rollup else None,
        bank_contracts_path=bank if use_bank else None,
        engine=args.engine,
        duration_s=args.duration_s,
        reserve_seconds=args.reserve_seconds,
        provenance_default=args.provenance_default,
        public_url=args.public_url or None,
        notes=args.notes,
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "out": str(args.out), "manifest_id": manifest["manifest_id"],
                      "demand_source": manifest["demand_source"]["mode"],
                      "capture_sets": len(manifest["capture_sets"]),
                      "planned_seconds": manifest["quota_budget"]["planned_seconds"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
