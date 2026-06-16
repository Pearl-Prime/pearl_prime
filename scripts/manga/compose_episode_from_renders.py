#!/usr/bin/env python3
"""Compose Canvas-ready webtoon episode payloads from already-rendered panels.

This is the missing glue between panel rendering and publish. The
docs/sessions/SESSION_HANDOFF_2026-04-25.md runbook §5 D leaves this as
inline Python with a ``# … reconstruct panel_images_manifest from rendered
out/ dir …`` placeholder. This script fills that placeholder with a real,
tested CLI so an operator (or the weekly rollout) can go from a directory of
rendered PNGs straight to per-locale episode strips with one command.

Pipeline (all existing, canonical phoenix_v4.manga.chapter functions — no new
rendering or compositing logic is invented here, this only wires them):

    rendered out/ dir of <panel_id>.png
        │  (reconstruct backend-result rows by scanning the dir,
        │   then reuse phoenix_v4.manga.image_backend.build_panel_images_manifest)
        ▼
    panel_images_manifest  (schema: schemas/manga/panel_images_manifest.schema.json)
        │  render_bubbles_on_panels  (per locale; locale-aware text_by_locale)
        ▼
    bubbled panel_images_manifest  (writes <panel_id>_bubbled.png)
        │  compose_episode_strips    (vertical-strip composer, beat-type gutters)
        ▼
    <out>/episodes/<locale>/<episode_id>/<episode_id>_seg_NNN.jpg  + payload.json

Tier 1 (operator-present). NO LLM calls. NO paid API. NO network. Pure local
PIL compositing of already-rendered images. The upstream GPU render
(scripts/manga/queue_panel_renders.py → Pearl Star ComfyUI) and the downstream
R2 push + WEBTOON Canvas upload are SEPARATE, operator/infra-gated steps and
are intentionally NOT performed here.

Usage:
    # Dry run — validate inputs + build the panel_images_manifest, NO PIL work,
    # NO output written. Proves the wiring without GPU renders or Pillow:
    python3 scripts/manga/compose_episode_from_renders.py \\
        --chapter-script artifacts/manga/chapter_scripts/<series>/ep_001.yaml \\
        --panel-prompts  artifacts/manga/panel_prompts/<series>/ep_001.panel_prompts.json \\
        --renders-dir    out/rendered/<series>/ep_001/ \\
        --dry-run

    # Real compose for one locale (requires the rendered PNGs + Pillow):
    python3 scripts/manga/compose_episode_from_renders.py \\
        --chapter-script artifacts/manga/chapter_scripts/<series>/ep_001.yaml \\
        --panel-prompts  artifacts/manga/panel_prompts/<series>/ep_001.panel_prompts.json \\
        --renders-dir    out/rendered/<series>/ep_001/ \\
        --out-root       out \\
        --locales        en_US

    # All locales declared in the chapter script:
    python3 scripts/manga/compose_episode_from_renders.py \\
        --chapter-script ... --panel-prompts ... --renders-dir ... --out-root out

Exit codes:
    0  success (or clean dry-run)
    2  bad/missing inputs (no chapter script, no prompts, no renders)
    3  compose error (e.g. caps violation, Pillow missing in non-dry-run)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


# Candidate filename patterns for a panel's rendered image, in priority order.
# queue_panel_renders.py writes "<panel_id>.png"; other drivers historically
# used a "_bubbled"-less raw panel. We accept the common variants.
def _render_path_for_panel(renders_dir: Path, panel_id: str) -> Path | None:
    for name in (
        f"{panel_id}.png",
        f"{panel_id}.PNG",
        f"{panel_id}.jpg",
        f"{panel_id}.jpeg",
        f"{panel_id}.webp",
    ):
        cand = renders_dir / name
        if cand.is_file():
            return cand
    # Fallback: any file that starts with the panel_id (e.g. comfyui prefix).
    matches = sorted(renders_dir.glob(f"{panel_id}.*"))
    matches = [m for m in matches if m.is_file() and "_bubbled" not in m.name]
    return matches[0] if matches else None


def _image_dims(path: Path) -> tuple[int, int]:
    """Return (width, height) of an image, or (0, 0) if unreadable / no PIL."""
    try:
        from PIL import Image  # type: ignore
    except ImportError:
        return (0, 0)
    try:
        with Image.open(path) as im:
            return (int(im.width), int(im.height))
    except Exception:
        return (0, 0)


def build_generation_results_from_dir(
    panel_prompts: dict[str, Any],
    renders_dir: Path,
    *,
    probe_dims: bool = True,
) -> tuple[list[dict[str, Any]], list[str]]:
    """Scan ``renders_dir`` for a PNG per panel in ``panel_prompts``.

    Returns ``(generation_results, missing_panel_ids)`` where
    ``generation_results`` is the row shape consumed by
    ``phoenix_v4.manga.image_backend.build_panel_images_manifest``:
        {"panel_id": str, "status": "ok"|"failed", "path": str,
         "width": int, "height": int}
    """
    results: list[dict[str, Any]] = []
    missing: list[str] = []
    for p in panel_prompts.get("panels") or []:
        pid = str(p.get("panel_id") or "")
        if not pid:
            continue
        rp = _render_path_for_panel(renders_dir, pid)
        if rp is None:
            missing.append(pid)
            results.append({"panel_id": pid, "status": "failed"})
            continue
        w, h = _image_dims(rp) if probe_dims else (0, 0)
        row: dict[str, Any] = {
            "panel_id": pid,
            "status": "ok",
            "path": str(rp.resolve()),
        }
        if w > 0 and h > 0:
            row["width"] = w
            row["height"] = h
        results.append(row)
    return results, missing


def _load_chapter_script(path: Path) -> dict[str, Any]:
    import yaml  # type: ignore

    data = yaml.safe_load(path.read_text())
    if not isinstance(data, dict):
        raise ValueError(f"chapter script {path} did not parse to a mapping")
    return data


def _load_panel_prompts(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text())
    if not isinstance(data, dict) or "panels" not in data:
        raise ValueError(f"panel_prompts {path} missing 'panels'")
    return data


def compose_one_locale(
    *,
    chapter_script: dict[str, Any],
    lettering_spec: dict[str, Any],
    panel_images_manifest: dict[str, Any],
    locale: str,
    out_root: Path,
    episode_id: str,
) -> dict[str, Any]:
    """Bubble + compose a single locale. Reuses canonical chapter functions."""
    from phoenix_v4.manga.chapter.bubble_render import render_bubbles_on_panels
    from phoenix_v4.manga.chapter.webtoon_compose import compose_episode_strips

    bubbled_dir = out_root / "bubbled" / locale / episode_id
    episode_dir = out_root / "episodes" / locale / episode_id

    bubbled_manifest = render_bubbles_on_panels(
        chapter_script,
        lettering_spec,
        panel_images_manifest,
        None,  # bubble_style_config — v2-reserved; defaults
        bubbled_dir,
        locale=locale,
    )

    payload = compose_episode_strips(
        chapter_script,
        bubbled_manifest,
        episode_dir,
        episode_id=episode_id,
    )
    # Persist the Canvas-ready payload next to the segments.
    payload_path = episode_dir / "payload.json"
    payload_path.parent.mkdir(parents=True, exist_ok=True)
    payload_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    payload["_payload_path"] = str(payload_path)
    return payload


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Compose Canvas-ready webtoon episode strips from already-rendered "
            "panels (the runbook §5 D glue). No GPU, no LLM, no network."
        )
    )
    ap.add_argument(
        "--chapter-script",
        required=True,
        type=Path,
        help="Path to chapter_script ep_NNN.yaml",
    )
    ap.add_argument(
        "--panel-prompts",
        required=True,
        type=Path,
        help="Path to ep_NNN.panel_prompts.json (defines panel ordering/ids)",
    )
    ap.add_argument(
        "--renders-dir",
        required=True,
        type=Path,
        help="Directory of rendered <panel_id>.png produced by queue_panel_renders.py",
    )
    ap.add_argument(
        "--out-root",
        type=Path,
        default=Path("out"),
        help="Root for out/bubbled/<locale>/ and out/episodes/<locale>/ (default: out)",
    )
    ap.add_argument(
        "--locales",
        nargs="*",
        default=None,
        help="Locales to compose (default: chapter_script.available_locales)",
    )
    ap.add_argument(
        "--episode-id",
        default=None,
        help="Episode id for output naming (default: chapter_script.chapter_id)",
    )
    ap.add_argument(
        "--manifest-out",
        type=Path,
        default=None,
        help="Optional path to also write the reconstructed panel_images_manifest JSON",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate + build manifest only; no PIL work, no output written",
    )
    args = ap.parse_args(argv)

    # ---- Load inputs -------------------------------------------------------
    if not args.chapter_script.is_file():
        print(f"ERROR: chapter script not found: {args.chapter_script}", file=sys.stderr)
        return 2
    if not args.panel_prompts.is_file():
        print(f"ERROR: panel_prompts not found: {args.panel_prompts}", file=sys.stderr)
        return 2
    if not args.renders_dir.is_dir():
        print(f"ERROR: renders dir not found: {args.renders_dir}", file=sys.stderr)
        return 2

    chapter_script = _load_chapter_script(args.chapter_script)
    panel_prompts = _load_panel_prompts(args.panel_prompts)

    episode_id = str(
        args.episode_id or chapter_script.get("chapter_id") or "ep_001"
    )
    locales = list(
        args.locales
        or chapter_script.get("available_locales")
        or [str(chapter_script.get("default_locale") or "en_US")]
    )

    # ---- Reconstruct panel_images_manifest from the rendered dir (the glue) -
    from phoenix_v4.manga.image_backend import build_panel_images_manifest

    gen_results, missing = build_generation_results_from_dir(
        panel_prompts, args.renders_dir, probe_dims=not args.dry_run
    )
    panel_images_manifest = build_panel_images_manifest(panel_prompts, gen_results)
    n_total = len(panel_prompts.get("panels") or [])
    n_ok = sum(1 for r in gen_results if r.get("status") == "ok")

    if args.manifest_out is not None:
        args.manifest_out.parent.mkdir(parents=True, exist_ok=True)
        args.manifest_out.write_text(
            json.dumps(panel_images_manifest, indent=2, ensure_ascii=False)
        )

    print(
        f"[compose_episode] episode={episode_id} panels: {n_ok}/{n_total} rendered "
        f"(missing={len(missing)}) locales={locales}"
    )
    if missing:
        print(
            f"[compose_episode] WARNING missing renders for: {', '.join(missing[:10])}"
            + (" ..." if len(missing) > 10 else ""),
            file=sys.stderr,
        )

    # ---- Build lettering spec (reuse canonical builder) --------------------
    from phoenix_v4.manga.chapter.lettering_from_script import (
        build_lettering_spec_from_chapter_script,
    )

    lettering_spec = build_lettering_spec_from_chapter_script(chapter_script)

    if args.dry_run:
        print(
            "[compose_episode] DRY RUN — wiring validated: panel_images_manifest "
            f"built ({n_ok} ok panels), lettering_spec built "
            f"({len(lettering_spec.get('lettering_panels') or [])} lettering panels), "
            f"would compose {len(locales)} locale(s). No PIL work, no files written."
        )
        # In dry-run, fail-fast signal if literally nothing is renderable.
        if n_ok == 0:
            print(
                "[compose_episode] note: 0 panels rendered yet — run "
                "scripts/manga/queue_panel_renders.py on Pearl Star first.",
                file=sys.stderr,
            )
        return 0

    if n_ok == 0:
        print(
            "ERROR: no rendered panels found in --renders-dir; run "
            "queue_panel_renders.py first.",
            file=sys.stderr,
        )
        return 2

    # ---- Compose per locale ------------------------------------------------
    try:
        all_payloads: dict[str, Any] = {}
        for locale in locales:
            payload = compose_one_locale(
                chapter_script=chapter_script,
                lettering_spec=lettering_spec,
                panel_images_manifest=panel_images_manifest,
                locale=locale,
                out_root=args.out_root,
                episode_id=episode_id,
            )
            caps = payload.get("caps_check", {})
            seg_n = len(payload.get("segments") or [])
            print(
                f"[compose_episode] {locale}: {seg_n} segment(s), "
                f"total_height={payload.get('total_height')}px, "
                f"caps_ok={not caps.get('violations')} -> {payload.get('_payload_path')}"
            )
            all_payloads[locale] = payload
    except Exception as e:  # compose-time failure (caps, missing Pillow, etc.)
        print(f"ERROR: compose failed: {type(e).__name__}: {e}", file=sys.stderr)
        return 3

    print(
        f"[compose_episode] DONE — composed {len(all_payloads)} locale(s) for "
        f"{episode_id}. Next (operator/infra-gated): r2_sync.py push + "
        f"webtoon_canvas_upload.py."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
