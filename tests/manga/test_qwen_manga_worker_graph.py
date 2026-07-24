"""Wave-2 Item 2 — Qwen Pearl Star manga worker graph shape (no live GPU).

scripts/pearl_star/worker/qwen_manga_worker.py (via flux_schnell_worker.py)
does ``from app import app`` — the Procrastinate App, which is only
installed on the pearl_star host, not in the Core test environment
(``import procrastinate`` fails here on a missing libpq wrapper). Rather than
skip this test whenever Procrastinate is absent, stub a minimal fake ``app``
module in ``sys.modules`` before import so the graph-building logic — the
part this spec item actually changed (step count, cfg, negative-prompt CJK
exclusion, blob-gate) — gets real, always-on coverage. This matches the
spec's acceptance bar: "unit graph tests pass (build the ComfyUI graph and
assert node/param shape without needing a live GPU)". This test never claims
a live PNG smoke passed; that requires ComfyUI + the Qwen model trio on-box
on pearl_star (out of scope here — see the wave-2 closeout).
"""
from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest


class _FakeApp:
    """Stand-in for procrastinate.App: `.task(...)` returns an identity decorator."""

    def task(self, *_args, **_kwargs):
        def _decorator(fn):
            return fn

        return _decorator


def _install_fake_app_module() -> None:
    if "app" in sys.modules and getattr(sys.modules["app"], "_is_fake_pearl_star_app", False):
        return
    fake = types.ModuleType("app")
    fake.app = _FakeApp()
    fake._is_fake_pearl_star_app = True
    sys.modules["app"] = fake


_WORKER_DIR = Path(__file__).resolve().parents[2] / "scripts" / "pearl_star" / "worker"
if str(_WORKER_DIR) not in sys.path:
    sys.path.insert(0, str(_WORKER_DIR))

_install_fake_app_module()

import qwen_manga_worker as worker  # noqa: E402


def test_graph_matches_reference_step_count_and_cfg() -> None:
    # Reference workflow: scripts/image_generation/comfyui_workflows/
    # qwen_image_no_pulid_manga.json KSampler node "5" — steps=28, cfg=4.0.
    graph = worker.qwen_image_txt2img_graph("a prompt", "", 1080, 1920, 42)
    sampler = graph["5"]["inputs"]
    assert sampler["steps"] == 28
    assert sampler["cfg"] == 4.0
    assert sampler["sampler_name"] == "euler"
    assert sampler["scheduler"] == "simple"


def test_graph_has_split_loaders_matching_reference() -> None:
    graph = worker.qwen_image_txt2img_graph("a prompt", "", 1080, 1920, 42)
    assert graph["1"]["class_type"] == "UNETLoader"
    assert graph["1"]["inputs"]["unet_name"] == "qwen_image_fp8_e4m3fn.safetensors"
    assert graph["8"]["class_type"] == "CLIPLoader"
    assert graph["8"]["inputs"]["clip_name"] == "qwen_2.5_vl_7b_fp8_scaled.safetensors"
    assert graph["9"]["class_type"] == "VAELoader"


def test_graph_node_wiring_shape() -> None:
    graph = worker.qwen_image_txt2img_graph("a prompt", "neg", 1080, 1920, 7)
    # KSampler wires model/positive/negative/latent from the loader/encode nodes.
    sampler_inputs = graph["5"]["inputs"]
    assert sampler_inputs["model"] == ["1", 0]
    assert sampler_inputs["positive"] == ["2", 0]
    assert sampler_inputs["negative"] == ["3", 0]
    assert sampler_inputs["latent_image"] == ["4", 0]
    assert sampler_inputs["seed"] == 7
    # VAEDecode + SaveImage close the graph.
    assert graph["6"]["inputs"]["samples"] == ["5", 0]
    assert graph["6"]["inputs"]["vae"] == ["9", 0]
    assert graph["7"]["class_type"] == "SaveImage"


def test_negative_prompt_excludes_cjk_characters_matching_reference() -> None:
    # Reference JSON negative excludes CJK script leakage (chinese/japanese/
    # korean characters) — the worker's _NEG_SUFFIX previously lacked this.
    graph = worker.qwen_image_txt2img_graph("a prompt", "", 1080, 1920, 42)
    neg_text = graph["3"]["inputs"]["text"].lower()
    for token in ("chinese characters", "japanese characters", "kanji", "hiragana", "katakana", "hangul"):
        assert token in neg_text


def test_negative_prompt_merges_caller_negative_with_suffix() -> None:
    graph = worker.qwen_image_txt2img_graph("a prompt", "extra negative", 1080, 1920, 42)
    neg_text = graph["3"]["inputs"]["text"]
    assert neg_text.startswith("extra negative")
    assert "watermark" in neg_text


def test_empty_latent_uses_requested_dimensions() -> None:
    graph = worker.qwen_image_txt2img_graph("a prompt", "", 768, 1344, 1)
    assert graph["4"]["inputs"]["width"] == 768
    assert graph["4"]["inputs"]["height"] == 1344


def test_blob_gate_rejects_undersized_png(tmp_path) -> None:
    small = tmp_path / "stub.png"
    small.write_bytes(b"\x00" * 100)
    with pytest.raises(RuntimeError, match="blob-gate"):
        worker._assert_blob_gate(small)


def test_blob_gate_accepts_real_sized_png(tmp_path) -> None:
    real = tmp_path / "panel.png"
    real.write_bytes(b"\x00" * (worker.MIN_PNG_BYTES + 1))
    worker._assert_blob_gate(real)  # should not raise


def test_blob_gate_rejects_missing_file(tmp_path) -> None:
    missing = tmp_path / "does_not_exist.png"
    with pytest.raises(RuntimeError, match="blob-gate"):
        worker._assert_blob_gate(missing)
