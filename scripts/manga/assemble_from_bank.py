#!/usr/bin/env python3
"""Deterministic layered panel assembly from a series image bank.

The bank-assembly lane of the V5 layered architecture: given a manifest of
banked layer assets (L0 backdrop plates, L2 character cutouts, L3 object
sprites, optional L1/L4), composite panels OFFLINE with zero GPU work and
zero randomness. This is the "bank × assembly = many stories" half of the
layered-image system; GPU rendering of the bank assets themselves stays with
`render_v5_episode.py` (live dispatch) / `render_v4_episode.py` (legacy).

Spec authority (this tool implements, it does not re-specify):
  - docs/specs/MANGA_LAYER_RENDER_CONTRACT_SPEC.md §4  — layer taxonomy,
    z-order (incl. L3 above_L2/below_L2), L4 screen-blend contract
  - docs/specs/MANGA_LAYER_RENDER_CONTRACT_SPEC.md §10 — composite placement
    math (tight-crop → min-scale → LANCZOS → centered paste, 0px feather)
  - docs/specs/MANGA_V5_LAYERED_ARCHITECTURE.md §7      — layer semantics
  - schemas/manga/assembly_manifest.schema.json         — manifest contract

Reuses (does not reimplement):
  - phoenix_v4.manga.chapter.bubble_render.render_bubbles_onto_panel for the
    lettering pass (--bubbles)
  - scripts/manga/validate_layer.py checks remain the QA authority for the
    input cutouts; this tool validates manifest structure + provenance only.

Provenance doctrine: every layer in the manifest MUST declare REAL or
INTERIM provenance. The assembler stamps a provenance table
(`<out>/_provenance.json` + `.md`) into the output dir and refuses any
manifest with unlabeled layers. An INTERIM layer is a labeled stand-in —
never presentable as final art.

Tier 1 (operator-present). No LLM calls. No network. No paid APIs.
Pure local PIL compositing of already-rendered images.

Usage:
    PYTHONPATH=. python3 scripts/manga/assemble_from_bank.py \
        --manifest artifacts/manga/<series>/assembly_manifests/<name>.yaml \
        --out-dir  artifacts/manga/<series>/assembled/<name>/ \
        [--strip] [--bubbles] [--locale en_US] [--dry-run]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import yaml
from PIL import Image, ImageChops, ImageFilter

REPO = Path(__file__).resolve().parents[2]

# §10 z-order table (bottom → top). L3 flips to 15 when z_order=below_L2.
Z_DEFAULT = {"L0": 0, "L1": 10, "L2": 20, "L3": 30, "L4": 40}
Z_L3_BELOW_L2 = 15

CUTOUT_CLASSES = {"L1", "L2", "L3"}


def _resolve(path_str: str, manifest_dir: Path) -> Path:
    p = Path(path_str)
    if p.is_absolute():
        return p
    for base in (REPO, manifest_dir):
        cand = base / p
        if cand.is_file():
            return cand
    return REPO / p  # let the open() raise with the canonical candidate


def load_manifest(manifest_path: Path) -> dict[str, Any]:
    manifest = yaml.safe_load(manifest_path.read_text())
    errors = validate_manifest(manifest)
    if errors:
        raise ValueError(
            "manifest failed validation:\n  - " + "\n  - ".join(errors)
        )
    return manifest


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    """Structural + provenance validation. Returns a list of errors (empty = ok).

    Deliberately duplicates the load-bearing rules of
    schemas/manga/assembly_manifest.schema.json so the tool fails closed
    without a jsonschema dependency; CI can additionally validate against
    the schema file.
    """
    errors: list[str] = []
    for key in ("schema_version", "series_id", "canvas", "panels"):
        if key not in manifest:
            errors.append(f"missing top-level key: {key}")
    if errors:
        return errors
    canvas = manifest["canvas"]
    if not (isinstance(canvas.get("width"), int) and isinstance(canvas.get("height"), int)):
        errors.append("canvas.width/height must be integers")
    for i, panel in enumerate(manifest["panels"]):
        pid = panel.get("panel_id", f"<panels[{i}]>")
        layers = panel.get("layers") or []
        if not layers:
            errors.append(f"{pid}: no layers")
        for j, layer in enumerate(layers):
            lc = layer.get("layer_class")
            if lc not in Z_DEFAULT:
                errors.append(f"{pid}.layers[{j}]: bad layer_class {lc!r}")
                continue
            if not layer.get("asset"):
                errors.append(f"{pid}.layers[{j}]: missing asset")
            if layer.get("provenance") not in ("REAL", "INTERIM"):
                errors.append(
                    f"{pid}.layers[{j}] ({lc}): provenance must be REAL or INTERIM "
                    "— unlabeled layers are refused (stub-as-done guard)"
                )
            if lc in CUTOUT_CLASSES and not layer.get("bbox_pct"):
                errors.append(f"{pid}.layers[{j}] ({lc}): bbox_pct required for {lc}")
            bbox = layer.get("bbox_pct")
            if bbox is not None and (
                len(bbox) != 4 or not all(isinstance(v, (int, float)) for v in bbox)
            ):
                errors.append(f"{pid}.layers[{j}]: bbox_pct must be [x,y,w,h] numbers")
    return errors


def composite_layer(canvas: Image.Image, layer_cutout: Image.Image,
                    bbox_pct: list[float]) -> Image.Image:
    """MANGA_LAYER_RENDER_CONTRACT_SPEC §10 math, verbatim semantics.

    Tight-crop the cutout to its alpha bbox, min-scale it into the target
    bbox (canvas-percentage coords), LANCZOS resample, centered paste,
    hard alpha (0px feather).
    """
    W, H = canvas.size
    x_pct, y_pct, w_pct, h_pct = bbox_pct
    target_x = int(W * x_pct / 100)
    target_y = int(H * y_pct / 100)
    target_w = int(W * w_pct / 100)
    target_h = int(H * h_pct / 100)
    tight_box = layer_cutout.getbbox()
    if tight_box is None:  # fully transparent asset
        return canvas
    layer_tight = layer_cutout.crop(tight_box)
    scale = min(target_w / layer_tight.width, target_h / layer_tight.height)
    new_size = (max(1, int(layer_tight.width * scale)),
                max(1, int(layer_tight.height * scale)))
    layer_scaled = layer_tight.resize(new_size, Image.LANCZOS)
    paste_x = target_x + (target_w - new_size[0]) // 2
    paste_y = target_y + (target_h - new_size[1]) // 2
    canvas.alpha_composite(layer_scaled, dest=(paste_x, paste_y))
    return canvas


def screen_blend_overlay(canvas: Image.Image, overlay: Image.Image,
                         opacity: float = 1.0) -> Image.Image:
    """§4.5 L4 contract: screen blend for additive effects, 2-3px Gaussian
    on alpha before blend (spec §10 feathering policy for L4)."""
    overlay = overlay.convert("RGBA").resize(canvas.size, Image.LANCZOS)
    alpha = overlay.getchannel("A").filter(ImageFilter.GaussianBlur(2.5))
    if opacity < 1.0:
        alpha = alpha.point(lambda a: int(a * opacity))
    base_rgb = canvas.convert("RGB")
    screened = ImageChops.screen(base_rgb, overlay.convert("RGB"))
    out = Image.composite(screened, base_rgb, alpha)
    return out.convert("RGBA")


def _layer_z(layer: dict[str, Any]) -> int:
    if layer.get("z_override") is not None:
        return int(layer["z_override"])
    lc = layer["layer_class"]
    if lc == "L3" and layer.get("z_order") == "below_L2":
        return Z_L3_BELOW_L2
    return Z_DEFAULT[lc]


def assemble_panel(panel: dict[str, Any], canvas_spec: dict[str, Any],
                   manifest_dir: Path) -> tuple[Image.Image, list[dict]]:
    """Assemble one panel. Returns (image, per-layer provenance records)."""
    W, H = canvas_spec["width"], canvas_spec["height"]
    bg_hex = canvas_spec.get("background_hex", "#FFFFFF")
    canvas = Image.new("RGBA", (W, H), bg_hex)
    records: list[dict] = []

    layers = sorted(panel["layers"], key=_layer_z)
    for layer in layers:
        asset_path = _resolve(layer["asset"], manifest_dir)
        img = Image.open(asset_path).convert("RGBA")
        if layer.get("flip_h"):
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        opacity = float(layer.get("opacity", 1.0))
        lc = layer["layer_class"]

        if lc == "L0":
            img = img.resize((W, H), Image.LANCZOS)
            canvas.alpha_composite(img)
        elif lc == "L4" and layer.get("blend", "screen") == "screen":
            canvas = screen_blend_overlay(canvas, img, opacity)
        else:
            if opacity < 1.0:
                a = img.getchannel("A").point(lambda v: int(v * opacity))
                img.putalpha(a)
            canvas = composite_layer(canvas, img, layer["bbox_pct"])

        records.append({
            "panel_id": panel["panel_id"],
            "layer_class": lc,
            "z": _layer_z(layer),
            "asset": str(asset_path.relative_to(REPO)) if asset_path.is_relative_to(REPO) else str(asset_path),
            "bytes": asset_path.stat().st_size,
            "provenance": layer["provenance"],
            "provenance_note": layer.get("provenance_note", ""),
        })
    return canvas, records


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render_strip(panel_paths: list[Path], out_path: Path,
                 gutter_px: int = 80, bg_hex: str = "#FFFFFF") -> Path:
    """Stack panels into one vertical webtoon strip (fixed gutters).

    Beat-type-aware gutters live in phoenix_v4.manga.chapter.webtoon_compose
    .compose_episode_strips — that path needs the full episode payload
    contract; this is the minimal bank-demo stacker for assembly output.
    """
    imgs = [Image.open(p).convert("RGB") for p in panel_paths]
    w = max(i.width for i in imgs)
    h = sum(i.height for i in imgs) + gutter_px * (len(imgs) - 1)
    strip = Image.new("RGB", (w, h), bg_hex)
    y = 0
    for img in imgs:
        strip.paste(img, ((w - img.width) // 2, y))
        y += img.height + gutter_px
    strip.save(out_path, quality=92)
    return out_path


def run(manifest_path: Path, out_dir: Path, *, strip: bool = False,
        bubbles: bool = False, locale: str = "en_US",
        dry_run: bool = False) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    if dry_run:
        n_layers = sum(len(p["layers"]) for p in manifest["panels"])
        print(f"DRY-RUN ok: {len(manifest['panels'])} panels, {n_layers} layers, "
              f"provenance labels present on all layers")
        return {"dry_run": True, "panels": len(manifest["panels"])}

    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_dir = manifest_path.parent
    all_records: list[dict] = []
    panel_paths: list[Path] = []

    for panel in manifest["panels"]:
        img, records = assemble_panel(panel, manifest["canvas"], manifest_dir)
        out_path = out_dir / f"{panel['panel_id']}.png"
        img.save(out_path)
        all_records.extend(records)

        final_path = out_path
        if bubbles and (panel.get("dialogue") or panel.get("narrator_caption") or panel.get("sfx")):
            sys.path.insert(0, str(REPO))
            from phoenix_v4.manga.chapter.bubble_render import render_bubbles_onto_panel
            bubbled = out_dir / f"{panel['panel_id']}_bubbled.png"
            render_bubbles_onto_panel(
                out_path,
                panel.get("dialogue") or [],
                panel.get("sfx") or [],
                panel.get("narrator_caption"),
                out_path=bubbled,
                locale=locale,
            )
            final_path = bubbled
        panel_paths.append(final_path)
        print(f"  {panel['panel_id']}: {final_path.name} "
              f"({final_path.stat().st_size:,} bytes)")

    # provenance table — the honest-labeling artifact, always written
    interim = [r for r in all_records if r["provenance"] == "INTERIM"]
    prov = {
        "manifest": str(manifest_path),
        "manifest_sha256": _sha256(manifest_path),
        "series_id": manifest["series_id"],
        "panels": len(manifest["panels"]),
        "layers_total": len(all_records),
        "layers_real": len(all_records) - len(interim),
        "layers_interim": len(interim),
        "records": all_records,
    }
    (out_dir / "_provenance.json").write_text(json.dumps(prov, indent=2))
    lines = ["| panel | layer | z | provenance | bytes | asset |", "|---|---|---|---|---|---|"]
    for r in all_records:
        lines.append(f"| {r['panel_id']} | {r['layer_class']} | {r['z']} | "
                     f"**{r['provenance']}** | {r['bytes']:,} | {r['asset']} |")
    (out_dir / "_provenance.md").write_text("\n".join(lines) + "\n")

    result: dict[str, Any] = {"panels": [str(p) for p in panel_paths], "provenance": prov}
    if strip:
        strip_path = out_dir / f"{manifest.get('manifest_id', manifest_path.stem)}_strip.jpg"
        render_strip(panel_paths, strip_path)
        result["strip"] = str(strip_path)
        print(f"  strip: {strip_path} ({strip_path.stat().st_size:,} bytes)")
    return result


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--manifest", required=True, type=Path)
    ap.add_argument("--out-dir", required=True, type=Path)
    ap.add_argument("--strip", action="store_true", help="also emit a vertical strip")
    ap.add_argument("--bubbles", action="store_true",
                    help="lettering pass via phoenix_v4 bubble_render")
    ap.add_argument("--locale", default="en_US")
    ap.add_argument("--dry-run", action="store_true",
                    help="validate manifest only; no PIL work")
    args = ap.parse_args(argv)
    run(args.manifest, args.out_dir, strip=args.strip, bubbles=args.bubbles,
        locale=args.locale, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
