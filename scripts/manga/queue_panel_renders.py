#!/usr/bin/env python3
"""Queue panel renders to Pearl Star ComfyUI from a panel_prompts.json file.

This is the missing piece referenced in docs/sessions/SESSION_HANDOFF_2026-04-25.md
runbook §5 B ("scripts/manga/queue_panel_renders.py NOT YET COMMITTED — manual
ComfyUI driving from panel_prompts JSON or scripts/image_generation/runcomfy_batch.py
as interim").

Mirrors the pattern in scripts/image_generation/generate_teacher_showcase_triptych.py
(the proven Pearl Star ComfyUI direct driver):
  - reads ComfyUI workflow template from scripts/image_generation/comfyui_workflows/flux_txt2img_manga.json
  - injects per-panel prompt + negative_prompt + seed via _build_workflow helper
  - posts to ComfyUI's /prompt endpoint
  - polls /history for completion
  - downloads result PNG via /view
  - writes to artifacts/manga/<series>/panels/<chapter>/<panel_id>.png

Tier 1 (operator-present); Pearl Star ComfyUI (free, local GPU); no LLM calls.

Usage:
    # Dry run (validate prompts, no GPU work):
    python3 scripts/manga/queue_panel_renders.py \\
        --panel-prompts artifacts/manga/panel_prompts/<series>/<chapter>.panel_prompts.json \\
        --dry-run

    # Render one panel (smoke test):
    python3 scripts/manga/queue_panel_renders.py \\
        --panel-prompts <prompts.json> \\
        --output-dir artifacts/manga/<series>/panels/<chapter>/ \\
        --only-panel ep001_001

    # Render all 35 panels:
    python3 scripts/manga/queue_panel_renders.py \\
        --panel-prompts <prompts.json> \\
        --output-dir artifacts/manga/<series>/panels/<chapter>/

Environment:
    COMFYUI_URL  — defaults to http://192.168.1.112:8188 (Pearl Star)
    COMFYUI_OUTPUT_NAME_PREFIX — optional filename prefix override
"""
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

# Reuse the proven workflow builder from manga_teacher_batch
from scripts.image_generation.manga_teacher_batch import _build_workflow
from scripts.image_generation.runcomfy_batch import load_workflow

WORKFLOW_PATH = REPO_ROOT / "scripts" / "image_generation" / "comfyui_workflows" / "flux_txt2img_manga.json"


def _default_comfy_url() -> str:
    url = (os.environ.get("COMFYUI_URL") or "").strip()
    if not url and os.environ.get("PEARL_STAR_IP"):
        url = f"http://{os.environ['PEARL_STAR_IP'].strip()}:8188"
    return url
DEFAULT_STEPS = 22  # FLUX-schnell-fp8 sweet spot for manga panels
DEFAULT_GUIDANCE = 3.8
DEFAULT_SEED = 42
POLL_INTERVAL_SEC = 2.0
# Per-panel poll timeout. H1=A (flux1-dev / 28 steps / cfg 3.5) at 1080x1920
# on a shared GPU can hit 4-7 min on contested VRAM; bump to 15 min and let the
# orchestrator override via env if needed. 5 min was the schnell-era default.
POLL_TIMEOUT_SEC = float(os.environ.get("QUEUE_POLL_TIMEOUT_SEC", "900"))  # 15 min per panel


def _wait_for_panel_outputs(
    pending: list[tuple[str, Path, str, str]],
    *,
    timeout_per_panel: float,
    ssh_host: str,
) -> tuple[int, int]:
    """Poll until each enqueued panel PNG exists (local or Pearl Star via SSH)."""
    ok = 0
    fail = 0
    for panel_id, out_path, via, dest_path in pending:
        deadline = time.time() + timeout_per_panel
        while time.time() < deadline:
            if out_path.is_file() and out_path.stat().st_size > 1024:
                ok += 1
                print(f"  OK   {panel_id}: wrote {out_path.name} (queue)", file=sys.stderr)
                break
            if via.startswith("ssh:") and dest_path:
                probe = subprocess.run(
                    [
                        "ssh", "-o", "BatchMode=yes", ssh_host,
                        f"test -s {shlex.quote(dest_path)}",
                    ],
                    capture_output=True,
                    timeout=30,
                )
                if probe.returncode == 0:
                    if not out_path.is_file():
                        subprocess.run(
                            ["scp", "-o", "BatchMode=yes", f"{ssh_host}:{dest_path}", str(out_path)],
                            capture_output=True,
                            timeout=120,
                        )
                    if out_path.is_file() and out_path.stat().st_size > 1024:
                        ok += 1
                        print(f"  OK   {panel_id}: fetched {out_path.name} from Pearl Star", file=sys.stderr)
                        break
            time.sleep(POLL_INTERVAL_SEC)
        else:
            fail += 1
            print(
                f"  FAIL {panel_id}: queue wait timeout after {timeout_per_panel}s "
                f"(expected {out_path})",
                file=sys.stderr,
            )
    return ok, fail


def _post_json(url: str, payload: dict) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _get_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _get_bytes(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=120) as resp:
        return resp.read()


def queue_one_panel(
    comfy_url: str,
    workflow_template: dict,
    panel: dict,
    seed: int,
    out_path: Path,
) -> tuple[bool, str]:
    """Returns (ok, message). On ok, the rendered PNG is at out_path."""
    panel_id = panel.get("panel_id", "unknown")
    prompt = panel.get("prompt") or panel.get("flux_prompt") or ""
    neg = panel.get("negative_prompt", "")

    if not prompt.strip():
        return False, f"{panel_id}: empty prompt"

    # _build_workflow signature (manga_teacher_batch.py:120):
    # only accepts positive_prompt / negative_prompt / input_image_b64 / seed.
    # Steps + guidance are baked into the workflow template JSON.
    workflow = _build_workflow(
        workflow_template,
        positive_prompt=prompt,
        negative_prompt=neg,
        seed=seed,
    )
    # Strip the _meta sidecar key that the template carries — ComfyUI's /prompt
    # API rejects any node without class_type with HTTP 400. Same fix as
    # generate_teacher_showcase_triptych.py:198 _strip_meta.
    workflow = {k: v for k, v in workflow.items() if k != "_meta"}

    # Submit to ComfyUI
    try:
        submit_resp = _post_json(f"{comfy_url}/prompt", {"prompt": workflow})
        prompt_id = submit_resp.get("prompt_id")
        if not prompt_id:
            return False, f"{panel_id}: ComfyUI returned no prompt_id"
    except urllib.error.URLError as e:
        return False, f"{panel_id}: submit failed — {e}"

    # Poll for completion
    deadline = time.time() + POLL_TIMEOUT_SEC
    while time.time() < deadline:
        time.sleep(POLL_INTERVAL_SEC)
        try:
            history = _get_json(f"{comfy_url}/history/{prompt_id}")
        except urllib.error.URLError:
            continue
        if prompt_id not in history:
            continue
        outputs = history[prompt_id].get("outputs", {})
        for node_outputs in outputs.values():
            images = node_outputs.get("images", [])
            if not images:
                continue
            img = images[0]
            view_url = (
                f"{comfy_url}/view?filename={img['filename']}"
                f"&subfolder={img.get('subfolder', '')}&type={img.get('type', 'output')}"
            )
            try:
                png_bytes = _get_bytes(view_url)
            except urllib.error.URLError as e:
                return False, f"{panel_id}: download failed — {e}"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(png_bytes)
            return True, f"{panel_id}: wrote {out_path.name} ({len(png_bytes):,} bytes)"
    # Belt-and-suspenders: ComfyUI sometimes finishes the render *after* our
    # poll deadline. Before declaring FAIL, do one more wait + history check
    # and try to download. Catches panels that landed in the last few seconds
    # of our timeout window.
    for _ in range(30):  # ~60 sec grace window
        time.sleep(2.0)
        try:
            history = _get_json(f"{comfy_url}/history/{prompt_id}")
        except urllib.error.URLError:
            continue
        if prompt_id not in history:
            continue
        outputs = history[prompt_id].get("outputs", {})
        for node_outputs in outputs.values():
            images = node_outputs.get("images", [])
            if not images:
                continue
            img = images[0]
            view_url = (
                f"{comfy_url}/view?filename={img['filename']}"
                f"&subfolder={img.get('subfolder', '')}&type={img.get('type', 'output')}"
            )
            try:
                png_bytes = _get_bytes(view_url)
            except urllib.error.URLError:
                continue
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(png_bytes)
            return True, f"{panel_id}: wrote {out_path.name} ({len(png_bytes):,} bytes) [post-timeout grace]"
    return False, f"{panel_id}: poll timeout after {POLL_TIMEOUT_SEC}s (grace window exhausted)"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--panel-prompts", required=True, help="Path to panel_prompts.json")
    ap.add_argument("--output-dir", default=None, help="Output dir (default: artifacts/manga/<series>/panels/<chapter>/)")
    ap.add_argument("--comfy-url", default=None, help="ComfyUI URL (default: COMFYUI_URL from env)")
    ap.add_argument("--only-panel", default=None, help="Render only this panel_id (smoke test)")
    ap.add_argument("--seed-base", type=int, default=DEFAULT_SEED, help=f"Seed base (panel index added; default: {DEFAULT_SEED})")
    ap.add_argument(
        "--seed-by-character",
        action="store_true",
        help=(
            "Seed each panel from its character_id (seed_base + sum(ord(c) for c in "
            "character_id)) for cross-panel consistency, falling back to index jitter "
            "when a panel carries no character_id. NOTE: today's panel_prompts.json "
            "schema does NOT emit character_id, so on this legacy path the flag is a "
            "no-op until the upstream prompt emitter adds it — the canonical V5 path "
            "(render_v5_episode.py) is where per-character seeding is live."
        ),
    )
    ap.add_argument("--skip-existing", action="store_true", help="Skip panels whose output PNG already exists")
    ap.add_argument("--dry-run", action="store_true", help="Validate prompts; do not call ComfyUI")
    ap.add_argument(
        "--via-queue",
        action="store_true",
        help="Enqueue panels on Pearl Star Procrastinate (canonical per MANGA_PRODUCTION_OPERATIONAL_V1_SPEC)",
    )
    ap.add_argument("--ssh-host", default="pearl_star", help="SSH host for --via-queue when PS_QUEUE_DSN unset")
    # V2 Phase B.7 extensions: workflow override + reference-image conditioning.
    # Back-compat: when neither --workflow-path nor --reference-image is set,
    # the existing FLUX-schnell-no-PuLID path runs unchanged (brand-2 V1 ship).
    ap.add_argument("--workflow-path", default=None,
                    help="Override the default workflow template (e.g. comfyui_workflows/"
                         "flux_txt2img_manga_pulid.json for PuLID-FaceNet conditioning)")
    ap.add_argument("--reference-image", default=None,
                    help="Reference-image filename for PuLID workflows (must already be uploaded "
                         "to ComfyUI's input/ dir; replaces the {{reference_image}} placeholder "
                         "in the workflow JSON LoadImage node). Implies --workflow-path the "
                         "matching PuLID variant if not explicitly set.")
    args = ap.parse_args()
    comfy_url = (args.comfy_url or _default_comfy_url()).strip()
    if not args.dry_run and not args.via_queue and not comfy_url:
        print(
            "ERROR: COMFYUI_URL not set. Load Keychain env or pass --comfy-url / use --via-queue.",
            file=sys.stderr,
        )
        return 1

    pp_path = Path(args.panel_prompts).resolve()
    if not pp_path.is_file():
        print(f"ERROR: --panel-prompts not a file: {pp_path}", file=sys.stderr)
        return 1
    pp = json.loads(pp_path.read_text())
    # Schema tolerance: brand-1 used "panels"; brand-2 (PR #918) uses "prompts".
    # Same shape per item; fall through to whichever key exists.
    panels = pp.get("prompts") or pp.get("panels") or []
    # Same drift on identifiers — brand-2 uses "brand"/"episode".
    series_id = pp.get("series_id") or pp.get("brand") or "unknown_series"
    chapter_id = pp.get("chapter_id") or pp.get("episode") or "unknown_chapter"

    if args.output_dir:
        out_dir = Path(args.output_dir).resolve()
    else:
        out_dir = REPO_ROOT / "artifacts" / "manga" / series_id / "panels" / chapter_id
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.only_panel:
        panels = [p for p in panels if p.get("panel_id") == args.only_panel]
        if not panels:
            print(f"ERROR: panel_id '{args.only_panel}' not found in {pp_path}", file=sys.stderr)
            return 1

    print(f"queue: {len(panels)} panel(s) · series={series_id} · chapter={chapter_id}", file=sys.stderr)
    print(f"output dir: {out_dir}", file=sys.stderr)
    if args.via_queue:
        print("mode: via-queue (Pearl Star Procrastinate)", file=sys.stderr)
    else:
        print(f"comfy URL: {comfy_url}", file=sys.stderr)

    if args.dry_run:
        for i, p in enumerate(panels):
            pid = p.get("panel_id", f"p{i:03d}")
            prompt = p.get("prompt") or p.get("flux_prompt") or ""
            print(f"  [dry] {pid} → {out_dir}/{pid}.png  ({len(prompt)} char prompt)", file=sys.stderr)
        return 0

    # V2 Phase B.7: workflow override + reference-image-aware path
    workflow_path = Path(args.workflow_path).resolve() if args.workflow_path else WORKFLOW_PATH
    if args.reference_image and not args.workflow_path:
        # Imply PuLID variant if reference-image given without explicit workflow
        pulid_variant = WORKFLOW_PATH.with_name(WORKFLOW_PATH.stem + "_pulid.json")
        if pulid_variant.is_file():
            workflow_path = pulid_variant
            print(f"--reference-image set; auto-selected PuLID variant: {workflow_path.name}", file=sys.stderr)
    if not workflow_path.is_file():
        print(f"ERROR: workflow template missing: {workflow_path}", file=sys.stderr)
        return 1
    workflow_template = None
    if not args.via_queue:
        workflow_template = load_workflow(workflow_path)
        if args.reference_image:
            for node in workflow_template.values():
                if isinstance(node, dict):
                    inputs = node.get("inputs") or {}
                    img = inputs.get("image")
                    if isinstance(img, str) and "{{reference_image}}" in img:
                        inputs["image"] = args.reference_image
            print(
                f"reference image: {args.reference_image} (must be in ComfyUI input/ dir)",
                file=sys.stderr,
            )
    elif args.reference_image:
        print(
            "WARN: --reference-image ignored in --via-queue mode (PuLID queue path not wired)",
            file=sys.stderr,
        )

    if args.via_queue:
        from scripts.manga.pearl_star_t2i_enqueue import (
            enqueue_panel_job,
            pearl_star_dest_path,
            pick_task_for_workflow,
        )

    ok = 0
    fail = 0
    skipped = 0
    queue_pending: list[tuple[str, Path, str, str]] = []
    for i, panel in enumerate(panels):
        pid = panel.get("panel_id", f"p{i:03d}")
        out_path = out_dir / f"{pid}.png"
        if args.skip_existing and out_path.is_file() and out_path.stat().st_size > 1024:
            print(f"  SKIP {pid} (already exists)", file=sys.stderr)
            skipped += 1
            continue
        char_id = panel.get("character_id") if args.seed_by_character else None
        if char_id:
            seed = args.seed_base + sum(ord(c) for c in str(char_id))
        else:
            seed = args.seed_base + i

        if args.via_queue:
            task_name = pick_task_for_workflow(workflow_path.name)
            try:
                dest = pearl_star_dest_path(out_path)
                res = enqueue_panel_job(
                    task=task_name,
                    prompt=panel.get("prompt") or panel.get("flux_prompt") or "",
                    negative=panel.get("negative_prompt", ""),
                    seed=seed,
                    panel_id=pid,
                    output_basename=pid,
                    dest_path=dest,
                    ssh_host=args.ssh_host,
                )
                print(f"  QUEUE {pid} job_id={res.get('job_id')} via={res.get('via')}", file=sys.stderr)
                queue_pending.append((pid, out_path, str(res.get("via", "")), dest))
            except Exception as e:
                print(f"  FAIL {pid}: enqueue — {e}", file=sys.stderr)
                fail += 1
            continue

        success, msg = queue_one_panel(comfy_url, workflow_template, panel, seed, out_path)
        prefix = "OK  " if success else "FAIL"
        print(f"  {prefix} {msg}", file=sys.stderr)
        if success:
            ok += 1
        else:
            fail += 1

    if args.via_queue and queue_pending:
        print(f"waiting: {len(queue_pending)} queued panel(s)…", file=sys.stderr)
        wait_ok, wait_fail = _wait_for_panel_outputs(
            queue_pending,
            timeout_per_panel=POLL_TIMEOUT_SEC,
            ssh_host=args.ssh_host,
        )
        ok += wait_ok
        fail += wait_fail

    print(f"\nresult: {ok} ok · {fail} failed · {skipped} skipped (of {len(panels)} total)", file=sys.stderr)
    if fail == 0:
        print(f"\nNext: review thumbnails via:\n  python3 scripts/manga/build_thumbnail_review_grid.py \\\n      --input-dir {out_dir} \\\n      --output-html {out_dir.parent}/review/{chapter_id}_thumbnail_grid.html", file=sys.stderr)
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
