"""Pearl Star image dispatch (SSH + ComfyUI HTTP API on the remote host).

Dry-run returns a structured plan only. Live mode copies the workflow JSON to
the remote host, POSTs ``/prompt``, polls ``/history/{prompt_id}``, then
``scp``s the first SaveImage output PNG into the caller-provided output dir.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

_COMFY = "http://127.0.0.1:8188"
_REMOTE_OUTPUT = "~/phoenix_server/ComfyUI/output"


@dataclass(frozen=True)
class PearlStarDispatchPlan:
    """Structured preview of what a live dispatch would do."""

    mode: str  # "comfyui_api"
    batch_id: str
    notes: str


def build_plan(batch: Mapping[str, Any]) -> PearlStarDispatchPlan:
    """Return a non-executing plan for logging and dry-run output."""
    batch_id = str(batch.get("batch_id", ""))
    mode = str(batch.get("pearl_star_mode", "comfyui_api"))
    if mode not in ("ssh_hf_cli", "comfyui_api"):
        mode = "comfyui_api"
    return PearlStarDispatchPlan(
        mode=mode,
        batch_id=batch_id,
        notes="Pearl Star ComfyUI /prompt + /history + output scp",
    )


def _repo_root() -> Path:
    """Repository root (``phoenix_omega/``)."""
    return Path(__file__).resolve().parents[3]


def _workflow_path(batch: Mapping[str, Any]) -> Path:
    root = _repo_root() / "scripts" / "image_generation" / "comfyui_workflows"
    wf = batch.get("workflow_template") or batch.get("workflow_path") or "flux_txt2img_manga.json"
    name = str(wf).strip()
    if not name.endswith(".json"):
        name = f"{name}.json"
    p = Path(name)
    return p if p.is_absolute() else root / p.name


def _strip_meta(graph: dict[str, Any]) -> dict[str, Any]:
    """Keep only ComfyUI API node dicts (numeric string keys + ``class_type``)."""
    out: dict[str, Any] = {}
    for k, v in graph.items():
        if str(k).startswith("_"):
            continue
        if isinstance(v, dict) and "class_type" in v:
            out[str(k)] = v
    return out


def _substitute(obj: Any, mapping: Mapping[str, str]) -> Any:
    if isinstance(obj, str):
        s = obj
        for k, v in mapping.items():
            s = s.replace("{{" + k + "}}", v)
        return s
    if isinstance(obj, dict):
        return {k: _substitute(v, mapping) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_substitute(x, mapping) for x in obj]
    return obj


def _substitution_map(batch: Mapping[str, Any]) -> dict[str, str]:
    return {
        "positive_prompt": str(batch.get("positive_prompt", "manga panel, clean linework")),
        "negative_prompt": str(batch.get("negative_prompt", "watermark, blurry, lowres")),
        "reference_image": str(batch.get("reference_image", "example.png")),
    }


def _run_ssh(host: str, remote_cmd: str, *, timeout: int) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["ssh", "-o", "BatchMode=yes", host, remote_cmd],
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _scp(local: Path, host: str, remote_path: str, *, timeout: int = 120) -> None:
    subprocess.run(
        ["scp", "-q", str(local), f"{host}:{remote_path}"],
        check=True,
        timeout=timeout,
    )


def _scp_from_remote(host: str, remote_file: str, local: Path, *, timeout: int = 300) -> None:
    local.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["scp", "-q", f"{host}:{remote_file}", str(local)],
        check=True,
        timeout=timeout,
    )


def _curl_remote(host: str, url: str, *, timeout: int = 120) -> str:
    inner = f"curl -sS --max-time {timeout} {url!r}"
    r = _run_ssh(host, inner, timeout=timeout + 30)
    if r.returncode != 0:
        raise RuntimeError(f"ssh curl failed: {r.stderr.strip() or r.stdout}")
    return r.stdout


def _post_prompt_json(host: str, body: dict[str, Any], *, timeout: int = 120) -> dict[str, Any]:
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(body, f)
        local_path = f.name
    remote = "/tmp/phoenix_comfy_prompt.json"
    try:
        _scp(Path(local_path), host, remote, timeout=timeout)
        inner = (
            "curl -sS --max-time "
            + str(timeout)
            + " -X POST http://127.0.0.1:8188/prompt -H 'Content-Type: application/json' "
            + "-d @"
            + remote
        )
        r = _run_ssh(host, inner, timeout=timeout + 60)
        _run_ssh(host, f"rm -f {remote}", timeout=30)
        if r.returncode != 0:
            raise RuntimeError(f"ComfyUI /prompt failed: {r.stderr.strip() or r.stdout}")
        return json.loads(r.stdout)
    finally:
        try:
            os.unlink(local_path)
        except OSError:
            pass


def _parse_history_for_outputs(entry: dict[str, Any]) -> tuple[str, str] | None:
    """Return (filename, subfolder) for first SaveImage output, or None."""
    if not isinstance(entry, dict):
        return None
    outputs = entry.get("outputs")
    if not isinstance(outputs, dict):
        return None
    for _nid, node_out in outputs.items():
        if not isinstance(node_out, dict):
            continue
        images = node_out.get("images")
        if not images or not isinstance(images, list):
            continue
        first = images[0]
        if isinstance(first, dict):
            fn = first.get("filename")
            if fn:
                sub = str(first.get("subfolder") or "")
                return str(fn), sub
    return None


def _poll_history(host: str, prompt_id: str, *, max_wait_s: float = 600.0, interval: float = 3.0) -> dict[str, Any]:
    deadline = time.time() + max_wait_s
    last_err = ""
    while time.time() < deadline:
        try:
            raw = _curl_remote(host, f"{_COMFY}/history", timeout=90)
            data = json.loads(raw)
        except (json.JSONDecodeError, RuntimeError) as e:
            last_err = str(e)
            time.sleep(interval)
            continue
        if isinstance(data, dict) and prompt_id in data and isinstance(data[prompt_id], dict):
            entry = data[prompt_id]
            if entry.get("outputs"):
                return entry
        time.sleep(interval)
    raise TimeoutError(f"ComfyUI history never showed outputs for prompt_id={prompt_id}: {last_err}")


def _validate_png(path: Path) -> None:
    if not path.is_file():
        raise RuntimeError(f"missing output: {path}")
    n = path.stat().st_size
    if n < 10_000:
        raise RuntimeError(f"PNG too small ({n} bytes); likely corrupt or error body")
    with path.open("rb") as handle:
        sig = handle.read(8)
    if sig != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError("output is not a valid PNG (bad signature)")


def dispatch(
    batch: Mapping[str, Any],
    *,
    dry_run: bool,
    ssh_host: str = "pearl_star",
    activation_output_dir: Path | None = None,
) -> dict[str, Any]:
    """Dispatch to Pearl Star. ``activation_output_dir`` required when not dry_run."""
    plan = build_plan(batch)
    wf_path = _workflow_path(batch)
    result: dict[str, Any] = {
        "dispatch_path": "pearl_star",
        "dry_run": dry_run,
        "plan": {
            "mode": plan.mode,
            "batch_id": plan.batch_id,
            "notes": plan.notes,
            "workflow_path": str(wf_path),
        },
    }
    if dry_run:
        result["status"] = "dry_run"
        return result

    if activation_output_dir is None:
        raise ValueError("activation_output_dir is required for Pearl Star live dispatch")

    graph = json.loads(wf_path.read_text(encoding="utf-8"))
    graph = _strip_meta(graph)
    graph = _substitute(graph, _substitution_map(batch))
    client_id = str(uuid.uuid4())
    body = {"prompt": graph, "client_id": client_id}
    t0 = time.perf_counter()
    pr = _post_prompt_json(ssh_host, body, timeout=120)
    if "error" in pr:
        raise RuntimeError(f"ComfyUI prompt error: {pr['error']}")
    prompt_id = str(pr.get("prompt_id") or "")
    if not prompt_id:
        raise RuntimeError(f"no prompt_id in ComfyUI response: {pr}")
    hist_entry = _poll_history(ssh_host, prompt_id, max_wait_s=600.0)
    parsed = _parse_history_for_outputs(hist_entry)
    if not parsed:
        raise RuntimeError(f"no SaveImage outputs in history for {prompt_id}: {hist_entry!s}"[:2000])
    filename, subfolder = parsed
    remote_file_guess = f"{_REMOTE_OUTPUT.rstrip('/')}/{subfolder + '/' if subfolder else ''}{filename}"
    remote_file_guess = remote_file_guess.replace("//", "/")
    out_dir = activation_output_dir / str(batch.get("batch_id", "batch"))
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^a-zA-Z0-9_.-]+", "_", str(batch.get("batch_id", "render"))) + ".png"
    dest = out_dir / safe_name
    try:
        _scp_from_remote(ssh_host, remote_file_guess, dest, timeout=300)
    except (subprocess.CalledProcessError, RuntimeError):
        alt = f"~/phoenix_server/ComfyUI/output/{filename}"
        _scp_from_remote(ssh_host, alt, dest, timeout=300)
    _validate_png(dest)
    wall = round(time.perf_counter() - t0, 2)
    import hashlib

    sha = hashlib.sha256(dest.read_bytes()).hexdigest()
    result["status"] = "succeeded"
    root = _repo_root()
    try:
        result["output_path"] = str(dest.resolve().relative_to(root))
    except ValueError:
        result["output_path"] = str(dest)
    result["sha256"] = sha
    result["wall_time_s"] = wall
    result["prompt_id"] = prompt_id
    return result
