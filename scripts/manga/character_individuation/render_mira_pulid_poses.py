#!/usr/bin/env python3
"""Render Mira Aoki reference sheet + PuLID-locked face poses (M5 character crux).

1. Reference sheet via flux_txt2img_manga.json (no PuLID — establishes identity).
2. Pose variants via flux_txt2img_manga_pulid.json (PulidFluxFaceNetLoader — commercial-clean).
3. Writes L2 character assets + runs qa_face_distance pairwise.

Queue note: PuLID is not a procrastinate task; ComfyUI API is used (install/smoke path
per PEARL_STAR_PULID_INSTALL runbook). Object/bg layers stay on the RAP queue.
"""
from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[3]
SERIES = "stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying"
CHAR_ID = "mira_aoki"
BRAND = "stillness_press"
COMFY = "http://127.0.0.1:8188"

POSES = [
    ("front_portrait_seated_calm",
     "Mira Aoki, adult woman 33, soft round face, medium almond eyes double lid, "
     "long brown hair, cream sweater, small jade pendant, seated upright at table, "
     "head and shoulders, gaze slightly downward, neutral mouth, relaxed brow, "
     "soft frontal lighting, plain warm cream background, josei iyashikei manga style"),
    ("front_portrait_seated_tense",
     "Mira Aoki, adult woman 33, soft round face, medium almond eyes double lid, "
     "long brown hair, cream sweater, small jade pendant, seated upright at table, "
     "head and shoulders, slight brow micro-furrow, jaw soft but set, gaze off-center, "
     "soft frontal lighting, plain warm cream background, josei iyashikei manga style"),
    ("front_portrait_seated_alert",
     "Mira Aoki, adult woman 33, soft round face, medium almond eyes double lid, "
     "long brown hair, cream sweater, small jade pendant, seated, head and shoulders, "
     "eyes slightly wider, lips closed, alerted not afraid, "
     "soft frontal lighting, plain warm cream background, josei iyashikei manga style"),
    ("front_portrait_seated_soft",
     "Mira Aoki, adult woman 33, soft round face, medium almond eyes double lid, "
     "long brown hair, cream sweater, small jade pendant, seated, head and shoulders, "
     "soft half-smile, eyes gentle, shoulders relaxed, "
     "soft frontal lighting, plain warm cream background, josei iyashikei manga style"),
]

NEG = (
    "text, words, letters, watermark, signature, deformed face, extra eyes, "
    "blurry, low quality, multiple people, male, child"
)


def _post_json(url: str, payload: dict) -> dict:
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise RuntimeError(f"HTTP {e.code}: {body[:2000]}") from e


def _get_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.loads(resp.read().decode())


def _get_bytes(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=120) as resp:
        return resp.read()


def _upload_image(path: Path) -> str:
    """Upload image to ComfyUI input folder; return filename."""
    import uuid
    boundary = uuid.uuid4().hex
    data = path.read_bytes()
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="image"; filename="{path.name}"\r\n'
        f"Content-Type: image/png\r\n\r\n"
    ).encode() + data + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(
        f"{COMFY}/upload/image",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        out = json.loads(resp.read().decode())
    return out.get("name") or path.name


def _inject(workflow: dict, *, positive: str, negative: str, seed: int,
            reference_image: str | None = None) -> dict:
    out = json.loads(json.dumps(workflow))
    for node in out.values():
        if not isinstance(node, dict):
            continue
        inputs = node.get("inputs") or {}
        text = inputs.get("text")
        if isinstance(text, str):
            if "{{positive_prompt}}" in text:
                inputs["text"] = positive
            elif "{{negative_prompt}}" in text:
                inputs["text"] = text.replace("{{negative_prompt}}", negative)
        if "seed" in inputs:
            inputs["seed"] = seed
        if "noise_seed" in inputs:
            inputs["noise_seed"] = seed
        if reference_image and inputs.get("image") == "{{reference_image}}":
            inputs["image"] = reference_image
    return {k: v for k, v in out.items() if k != "_meta"}


def _render(workflow: dict, out_path: Path, timeout: float = 600.0) -> int:
    submit = _post_json(f"{COMFY}/prompt", {"prompt": workflow})
    prompt_id = submit.get("prompt_id")
    if not prompt_id:
        raise RuntimeError(f"no prompt_id: {submit}")
    deadline = time.time() + timeout
    while time.time() < deadline:
        time.sleep(2)
        try:
            history = _get_json(f"{COMFY}/history/{prompt_id}")
        except urllib.error.URLError:
            continue
        if prompt_id not in history:
            continue
        for node_out in (history[prompt_id].get("outputs") or {}).values():
            for img in node_out.get("images") or []:
                data = _get_bytes(
                    f"{COMFY}/view?filename={img['filename']}"
                    f"&subfolder={img.get('subfolder', '')}&type={img.get('type', 'output')}"
                )
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_bytes(data)
                return len(data)
    raise TimeoutError(f"timeout waiting for {prompt_id}")


def main() -> int:
    ref_dir = REPO / "artifacts" / "manga" / "image_bank" / BRAND / "reference_sheets" / CHAR_ID
    l2_dir = REPO / "artifacts" / "manga" / SERIES / "image_bank" / "L2" / CHAR_ID
    ref_dir.mkdir(parents=True, exist_ok=True)
    l2_dir.mkdir(parents=True, exist_ok=True)

    # 1) Reference sheet (no PuLID) — skip if already present
    flux_wf = json.loads(
        (REPO / "scripts/image_generation/comfyui_workflows/flux_txt2img_manga.json").read_text()
    )
    ref_path = ref_dir / f"{CHAR_ID}_reference_sheet.png"
    if ref_path.is_file() and ref_path.stat().st_size > 50_000:
        print(f"  reference exists: {ref_path} ({ref_path.stat().st_size:,} bytes)")
    else:
        print("Rendering reference sheet (no PuLID)…")
        wf = _inject(
            flux_wf,
            positive=(
                "Character reference sheet, front-facing neutral portrait, head and shoulders, "
                "Mira Aoki, adult woman 33, soft round face, medium almond eyes double lid, "
                "long brown hair, cream sweater, small jade pendant, soft frontal lighting, "
                "plain warm cream background, josei iyashikei manga style, consistent identity"
            ),
            negative=NEG,
            seed=7777,
        )
        nbytes = _render(wf, ref_path)
        print(f"  reference: {ref_path} ({nbytes:,} bytes)")
        (ref_dir / "provenance.json").write_text(json.dumps({
            "character_id": CHAR_ID,
            "brand_id": BRAND,
            "workflow": "flux_txt2img_manga.json",
            "pulid": False,
            "seed": 7777,
            "bytes": nbytes,
            "note": "Identity-establishing reference; PuLID poses use this as reference_image",
        }, indent=2) + "\n")

    # 2) Upload reference for PuLID
    ref_name = _upload_image(ref_path)
    print(f"  uploaded reference as {ref_name}")

    # 3) PuLID pose variants
    pulid_wf = json.loads(
        (REPO / "scripts/image_generation/comfyui_workflows/flux_txt2img_manga_pulid.json").read_text()
    )
    pose_paths: list[Path] = []
    for i, (pose_id, prompt) in enumerate(POSES):
        out = l2_dir / f"{pose_id}.png"
        print(f"Rendering PuLID pose {pose_id}…")
        wf = _inject(
            pulid_wf, positive=prompt, negative=NEG,
            seed=7800 + i, reference_image=ref_name,
        )
        nbytes = _render(wf, out, timeout=300.0)
        print(f"  {pose_id}: {nbytes:,} bytes")
        pose_paths.append(out)
        (out.with_suffix(".provenance.json")).write_text(json.dumps({
            "provenance": "REAL",
            "character_id": CHAR_ID,
            "pose_id": pose_id,
            "workflow": "flux_txt2img_manga_pulid.json",
            "pulid_loader": "PulidFluxFaceNetLoader",
            "reference": str(ref_path),
            "bytes": nbytes,
        }, indent=2) + "\n")

    # 4) Face distance
    from scripts.manga.character_individuation.qa_face_distance import distance

    pairs = []
    for i, a in enumerate(pose_paths):
        for b in pose_paths[i + 1:]:
            d = distance(a, b)
            pairs.append((a.name, b.name, d))
            print(f"  face_distance {a.name} vs {b.name}: {d:.4f}")

    scores = [p[2] for p in pairs]
    mean_d = sum(scores) / len(scores) if scores else 999.0
    max_d = max(scores) if scores else 999.0
    # Same-identity gate: pairwise ≤ 0.4
    passed = all(d <= 0.4 for d in scores)
    report = {
        "character_id": CHAR_ID,
        "pairs": [{"a": a, "b": b, "distance": d} for a, b, d in pairs],
        "mean_distance": mean_d,
        "max_distance": max_d,
        "gate_threshold": 0.4,
        "gate_pass": passed,
        "interpretation": (
            "PASS — same identity across poses"
            if passed else
            "FAIL — drift exceeds 0.4; escalate to per-character LoRA (Q-MANGA-04)"
        ),
    }
    report_path = l2_dir / "qa_face_distance_report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
