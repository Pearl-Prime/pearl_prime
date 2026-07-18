"""Pearl Star Job Queue V1 — flux-schnell t2i worker (Phase A dogfood).

The single workload class wired in Phase A (spec §8 step 7 — book covers are
the operator's stated $-maker, highest volume, concurrency=1). One job =
one atomic GPU dispatch = one image (spec §6.1, §6.2: flux-schnell 1 image /
1024x1536, concurrency 1).

Flow (matches scripts/image_generation/dispatchers/pearl_star_dispatcher.py):
    build flux-schnell ComfyUI graph (steps=4, cfg=1.0, euler/simple — schnell
    is incompatible with steps>=8/cfg>1) -> POST /prompt -> poll /history/{id}
    -> copy the SaveImage output into /var/lib/pearl-star/output/.

Stall contract (spec §5.1): emits a heartbeat JSONL line every 30 s with the
spec's exact field set, into /run/pearl-star/heartbeat/<worker_id>.jsonl
(tmpfs) and flushed to /var/log/pearl-star/heartbeat/ for forensics. The
watchdog (bin/watchdog.py) reads these and enforces 2x/3x thresholds.

Stall-injection for smoke A2: set env FORCE_STALL=1 to make the task sleep 600 s
(spec §5.4 / handoff §5.3 A2) instead of dispatching — exercises STALL_WARN ->
STALL_KILL -> requeue.

Tier policy: ComfyUI flux-schnell-fp8 is free + local + commercial-clean
(manga_render_path_decision.md §V2 license list). No paid LLM API (CLAUDE.md).
"""

from __future__ import annotations

import json
import os
import shutil
import socket
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

from app import app  # Procrastinate App (worker/app.py)
from gpu_heavy_lock import gpu_heavy_lock

# --- config (mirrors install/00_config.sh; env overridable) ----------------
COMFY_URL = os.environ.get("PS_COMFY_URL", "http://127.0.0.1:8188")
OUTPUT_DIR = Path(os.environ.get("PS_OUTPUT_DIR", "/var/lib/pearl-star/output"))
COMFY_OUTPUT = Path(
    os.environ.get("PS_COMFY_OUTPUT", str(Path.home() / "phoenix_server/ComfyUI/output"))
)
HEARTBEAT_DIR = Path(os.environ.get("PS_HEARTBEAT_DIR", "/run/pearl-star/heartbeat"))
HEARTBEAT_FORENSIC = Path(
    os.environ.get("PS_HEARTBEAT_FORENSIC", "/var/log/pearl-star/heartbeat")
)
HEARTBEAT_INTERVAL_S = int(os.environ.get("PS_HEARTBEAT_INTERVAL_S", "30"))
HEARTBEAT_FLUSH_S = int(os.environ.get("PS_HEARTBEAT_FLUSH_S", "60"))

# flux-schnell sizing + stall envelope (spec §3.1 / §6.2).
WORKLOAD = "t2i_flux_schnell"
NORMAL_S = 12.0          # spec §3.1 normal 6-12 s
EXPECTED_TOTAL_S = 18.0  # heartbeat field expected_total_s (a touch above normal)
STALL_WARN_S = 30.0      # spec §3.1 stall warn
STALL_KILL_S = 60.0      # spec §3.1 stall kill
DEFAULT_W, DEFAULT_H = 1024, 1536  # spec §6.2 flux-schnell 1024x1536


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _worker_id() -> str:
    return f"{socket.gethostname()}-t2i-{os.getpid()}"


def _flux_schnell_graph(prompt: str, negative: str, width: int, height: int, seed: int) -> dict:
    """ComfyUI API graph for flux1-schnell-fp8 (4 / 1.0 / euler / simple).

    Faithful to scripts/image_generation/comfyui_workflows/
    flux_txt2img_manga_brand2_schnell.json — schnell MUST use steps=4, cfg=1.0.
    """
    neg = (
        f"{negative}, text, words, letters, captions, watermark, signature, "
        "writing, typography, font, lettering, logos, subtitles"
    )
    return {
        "1": {"class_type": "CheckpointLoaderSimple",
              "inputs": {"ckpt_name": "flux1-schnell-fp8.safetensors"}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": neg, "clip": ["1", 1]}},
        "4": {"class_type": "EmptyLatentImage",
              "inputs": {"width": width, "height": height, "batch_size": 1}},
        "5": {"class_type": "KSampler",
              "inputs": {"seed": seed, "steps": 4, "cfg": 1.0,
                         "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0,
                         "model": ["1", 0], "positive": ["2", 0],
                         "negative": ["3", 0], "latent_image": ["4", 0]}},
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "SaveImage",
              "inputs": {"filename_prefix": "pearl_star_cover", "images": ["6", 0]}},
    }


class _Heartbeat:
    """Background heartbeat emitter (spec §5.1).

    Writes one JSONL line every HEARTBEAT_INTERVAL_S to the tmpfs path and
    re-flushes the whole journal to the forensic path every HEARTBEAT_FLUSH_S.
    The watchdog reads `elapsed_s` vs `stall_warn_at_s` / `stall_kill_at_s`.
    """

    def __init__(
        self,
        job_id: Any,
        prompt_id: str | None = None,
        *,
        expected_total_s: float = EXPECTED_TOTAL_S,
        stall_warn_at_s: float = STALL_WARN_S,
        stall_kill_at_s: float = STALL_KILL_S,
    ) -> None:
        self.worker_id = _worker_id()
        self.job_id = str(job_id)
        self.prompt_id = prompt_id
        self.phase = "starting"
        self._expected_total_s = expected_total_s
        self._stall_warn_at_s = stall_warn_at_s
        self._stall_kill_at_s = stall_kill_at_s
        self._start = time.monotonic()
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        HEARTBEAT_DIR.mkdir(parents=True, exist_ok=True)
        HEARTBEAT_FORENSIC.mkdir(parents=True, exist_ok=True)
        self._tmp = HEARTBEAT_DIR / f"{self.worker_id}.jsonl"
        self._forensic = HEARTBEAT_FORENSIC / f"{self.worker_id}.jsonl"

    def start(self) -> None:
        self._thread.start()

    def set_phase(self, phase: str, prompt_id: str | None = None) -> None:
        self.phase = phase
        if prompt_id:
            self.prompt_id = prompt_id

    def stop(self) -> None:
        self._stop.set()
        self._thread.join(timeout=2)
        # Final flush so the forensic copy is complete.
        self._flush()

    def _vram(self) -> dict[str, Any]:
        """nvidia-smi snapshot; never fatal if the binary is absent."""
        try:
            import subprocess
            out = subprocess.run(
                ["nvidia-smi",
                 "--query-gpu=memory.used,memory.free,utilization.gpu",
                 "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=5,
            ).stdout.strip().splitlines()
            used, free, util = (x.strip() for x in out[0].split(","))
            return {"vram_used_mb": int(used), "vram_free_mb": int(free),
                    "gpu_util_pct": int(util)}
        except Exception:
            return {"vram_used_mb": None, "vram_free_mb": None, "gpu_util_pct": None}

    def _line(self) -> dict[str, Any]:
        elapsed = round(time.monotonic() - self._start, 1)
        rec = {
            "ts": _utc(),
            "worker_id": self.worker_id,
            "job_id": self.job_id,
            "phase": self.phase,
            "elapsed_s": elapsed,
            "expected_total_s": self._expected_total_s,
            "stall_warn_at_s": self._stall_warn_at_s,
            "stall_kill_at_s": self._stall_kill_at_s,
            "comfyui_prompt_id": self.prompt_id,
        }
        rec.update(self._vram())
        return rec

    def _flush(self) -> None:
        try:
            shutil.copyfile(self._tmp, self._forensic)
        except Exception:
            pass

    def _loop(self) -> None:
        last_flush = time.monotonic()
        # Emit immediately, then on cadence, so the watchdog sees the job fast.
        while not self._stop.is_set():
            try:
                with self._tmp.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(self._line()) + "\n")
            except Exception:
                pass
            if time.monotonic() - last_flush >= HEARTBEAT_FLUSH_S:
                self._flush()
                last_flush = time.monotonic()
            self._stop.wait(HEARTBEAT_INTERVAL_S)


def _poll_history(prompt_id: str, max_wait_s: float = 120.0, interval: float = 2.0) -> dict:
    """Poll ComfyUI /history/{prompt_id} until outputs appear (spec A1: <60s)."""
    deadline = time.monotonic() + max_wait_s
    last = ""
    while time.monotonic() < deadline:
        try:
            r = requests.get(f"{COMFY_URL}/history/{prompt_id}", timeout=10)
            data = r.json()
            entry = data.get(prompt_id) if isinstance(data, dict) else None
            if isinstance(entry, dict) and entry.get("outputs"):
                return entry
        except Exception as exc:  # transient; keep polling
            last = str(exc)
        time.sleep(interval)
    raise TimeoutError(f"ComfyUI /history never produced outputs for {prompt_id}: {last}")


@app.task(name="t2i_flux_schnell", queue="t2i", retry=1)
def t2i_flux_schnell(
    prompt: str,
    negative: str = "",
    width: int = DEFAULT_W,
    height: int = DEFAULT_H,
    seed: int = 42,
    job_label: str = "book_cover",
) -> dict:
    """Render ONE flux-schnell image via ComfyUI and land it in OUTPUT_DIR.

    retry=1 per spec §5.3 t2i budget (1 retry). Returns the output path +
    prompt_id; raises on ComfyUI failure so Procrastinate's retry fires.
    """
    # Procrastinate passes job context; derive a stable id from PID+time if absent.
    job_id = os.environ.get("PROCRASTINATE_JOB_ID", f"{job_label}-{int(time.time())}")
    hb = _Heartbeat(job_id)
    hb.start()
    try:
        # --- A2 stall injection (spec §5.4 / handoff §5.3) ------------------
        if os.environ.get("FORCE_STALL") == "1":
            hb.set_phase("FORCE_STALL_sleeping")
            # 600 s sleep — the watchdog must STALL_WARN at 2x then STALL_KILL at 3x.
            time.sleep(600)
            return {"status": "should_have_been_killed"}

        # --- normal dispatch -----------------------------------------------
        with gpu_heavy_lock(
            f"t2i:{job_label}",
            worker_lane="manga",
            wait_s=float(os.environ.get("PS_GPU_HEAVY_WAIT_S", "300")),
        ):
            hb.set_phase("submitting")
            graph = _flux_schnell_graph(prompt, negative, width, height, seed)
            r = requests.post(f"{COMFY_URL}/prompt", json={"prompt": graph}, timeout=30)
            r.raise_for_status()
            pr = r.json()
            if pr.get("error"):
                raise RuntimeError(f"ComfyUI /prompt error: {pr['error']}")
            prompt_id = str(pr.get("prompt_id") or "")
            if not prompt_id:
                raise RuntimeError(f"no prompt_id in ComfyUI response: {pr}")
            hb.set_phase("rendering", prompt_id=prompt_id)

            entry = _poll_history(prompt_id)
            filename = None
            for node_out in entry.get("outputs", {}).values():
                for img in node_out.get("images", []) or []:
                    filename = img.get("filename")
                    if filename:
                        break
                if filename:
                    break
            if not filename:
                raise RuntimeError(f"no SaveImage output for prompt_id={prompt_id}: {entry}")

            hb.set_phase("copying_output", prompt_id=prompt_id)
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            src = COMFY_OUTPUT / filename
            dst = OUTPUT_DIR / filename
            copied = False
            try:
                if src.is_file():
                    shutil.copyfile(src, dst)
                    copied = True
            except PermissionError:
                copied = False
            if not copied:
                v = requests.get(
                    f"{COMFY_URL}/view",
                    params={"filename": filename, "type": "output"},
                    timeout=30,
                )
                v.raise_for_status()
                dst.write_bytes(v.content)

            hb.set_phase("done", prompt_id=prompt_id)
            return {
                "status": "COMPLETED",
                "prompt_id": prompt_id,
                "output": str(dst),
                "workload": WORKLOAD,
            }
    finally:
        hb.stop()
