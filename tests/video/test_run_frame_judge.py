"""Unit tests for scripts/video/run_frame_judge.py — STUBBED judge/rewrite/render.

Everything network-bound (Ollama judge + rewriter, ComfyUI render) is injected as
a stub, so these run deterministically in CI with no live Pearl Star box and no
paid API. Covers: keep-best loop, threshold pass/fail, retry budget, manga dual-use
(panel vs scene_description), per-character seed, checkpoint resume, judge-only mode,
missing-image handling, deterministic seed, and the CLI --help.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts" / "video"))

import run_frame_judge as rfj  # noqa: E402


# ───────────────────────── helpers / stubs ─────────────────────────

def _png(tmp_path: Path, name: str, content: bytes = b"\x89PNG\r\n\x1a\nstub") -> Path:
    p = tmp_path / name
    p.write_bytes(content)
    return p


def make_item(tmp_path: Path, item_id: str, text: str = "a monk on a mountain",
              prompt: str = "scene: a monk", character_id=None) -> rfj.JudgeItem:
    return rfj.JudgeItem(
        id=item_id,
        image=_png(tmp_path, f"frame_{item_id}.png"),
        target_text=text,
        prompt=prompt,
        character_id=character_id,
    )


class ScriptedJudge:
    """Returns scores from a per-id queue; records every call for assertions."""

    def __init__(self, scores_by_id: dict):
        self.scores_by_id = {k: list(v) for k, v in scores_by_id.items()}
        self.calls: list[str] = []

    def __call__(self, item: rfj.JudgeItem) -> dict:
        self.calls.append(item.id)
        q = self.scores_by_id.get(item.id, [50])
        score = q.pop(0) if q else 50
        return {"score": score, "missing": ["x"] if score < 80 else [],
                "wrong": [], "present": ["monk"], "suggested_fix": "add the mountain"}


class CountingRewriter:
    def __init__(self):
        self.calls = 0

    def __call__(self, item: rfj.JudgeItem, verdict: dict) -> str:
        self.calls += 1
        return f"{item.prompt} :: rewrite#{self.calls}"


class CountingRenderer:
    """Records the seed it was handed; returns deterministic stub bytes."""

    def __init__(self):
        self.seeds: list[int] = []
        self.calls = 0

    def __call__(self, item: rfj.JudgeItem, prompt: str, seed: int) -> bytes:
        self.calls += 1
        self.seeds.append(seed)
        return b"\x89PNG\r\n\x1a\nrerender" + str(seed).encode()


# ───────────────────────── seed ─────────────────────────

def test_seed_for_is_deterministic():
    assert rfj.seed_for("beat_03") == rfj.seed_for("beat_03")
    assert rfj.seed_for("beat_03") != rfj.seed_for("beat_04")
    assert isinstance(rfj.seed_for("x"), int)


def test_seed_keys_on_character_for_manga(tmp_path):
    # Same character across two different panels -> same seed (the manga win).
    panel_a = rfj.JudgeItem("panel_1", _png(tmp_path, "p1.png"), "scene a", "p", character_id="sai_ma")
    panel_b = rfj.JudgeItem("panel_2", _png(tmp_path, "p2.png"), "scene b", "p", character_id="sai_ma")
    assert rfj.seed_for(panel_a.character_id) == rfj.seed_for(panel_b.character_id)


# ───────────────────────── core loop ─────────────────────────

def test_passing_frame_kept_no_rerender(tmp_path):
    item = make_item(tmp_path, "a")
    judge = ScriptedJudge({"a": [95]})
    rewriter, renderer = CountingRewriter(), CountingRenderer()
    [v] = rfj.run_frame_judge([item], rfj.JudgeConfig(threshold=80),
                              judge_fn=judge, rewrite_fn=rewriter, render_fn=renderer)
    assert v.score == 95 and v.passed(80)
    assert v.attempts == 0
    assert renderer.calls == 0 and rewriter.calls == 0  # never re-rendered a passing frame
    assert v.kept_image == str(item.image)


def test_subthreshold_rerenders_and_keeps_best(tmp_path):
    item = make_item(tmp_path, "a")
    # first 60 (fail) -> attempt1 re-judge 90 (pass) -> stops.
    judge = ScriptedJudge({"a": [60, 90]})
    rewriter, renderer = CountingRewriter(), CountingRenderer()
    [v] = rfj.run_frame_judge([item], rfj.JudgeConfig(threshold=80, max_retries=2),
                              judge_fn=judge, rewrite_fn=rewriter, render_fn=renderer)
    assert v.score == 90 and v.passed(80)
    assert v.attempts == 1
    assert renderer.calls == 1 and rewriter.calls == 1
    assert v.kept_prompt.endswith("rewrite#1")  # kept the improved prompt


def test_keep_best_when_rerenders_worse(tmp_path):
    item = make_item(tmp_path, "a")
    # base 70, both retries worse (40, 50) -> keep the ORIGINAL 70 + original image/prompt.
    judge = ScriptedJudge({"a": [70, 40, 50]})
    renderer = CountingRenderer()
    [v] = rfj.run_frame_judge([item], rfj.JudgeConfig(threshold=80, max_retries=2),
                              judge_fn=judge, rewrite_fn=CountingRewriter(), render_fn=renderer)
    assert v.score == 70 and not v.passed(80)
    assert v.attempts == 2  # exhausted the budget
    assert renderer.calls == 2
    assert v.kept_image == str(item.image)  # original kept
    assert v.kept_prompt == item.prompt


def test_respects_max_retries_budget(tmp_path):
    item = make_item(tmp_path, "a")
    judge = ScriptedJudge({"a": [10, 20, 30, 40, 50]})  # never passes
    renderer = CountingRenderer()
    rfj.run_frame_judge([item], rfj.JudgeConfig(threshold=80, max_retries=3),
                        judge_fn=judge, rewrite_fn=CountingRewriter(), render_fn=renderer)
    assert renderer.calls == 3  # exactly max_retries, no more


def test_judge_only_mode_no_render(tmp_path):
    item = make_item(tmp_path, "a")
    judge = ScriptedJudge({"a": [55]})
    renderer = CountingRenderer()
    # render_fn omitted AND no comfyui_url -> never re-render.
    [v] = rfj.run_frame_judge([item], rfj.JudgeConfig(threshold=80),
                              judge_fn=judge, rewrite_fn=CountingRewriter())
    assert v.score == 55 and v.attempts == 0
    assert renderer.calls == 0


def test_missing_image_is_zero_scored(tmp_path):
    item = rfj.JudgeItem("ghost", tmp_path / "does_not_exist.png", "t", "p")
    judge = ScriptedJudge({"ghost": [99]})  # would pass IF judged — but image missing
    [v] = rfj.run_frame_judge([item], rfj.JudgeConfig(),
                              judge_fn=judge, rewrite_fn=CountingRewriter(), render_fn=CountingRenderer())
    assert v.score == 0 and v.error == "image-missing"
    assert judge.calls == []  # judge never invoked on a missing image


# ───────────────────────── per-character seed propagation ─────────────────────────

def test_rerender_seed_keys_on_character_id(tmp_path):
    item = make_item(tmp_path, "panel_1", character_id="sai_ma")
    judge = ScriptedJudge({"panel_1": [50, 50, 50]})
    renderer = CountingRenderer()
    rfj.run_frame_judge([item], rfj.JudgeConfig(threshold=80, max_retries=2),
                        judge_fn=judge, rewrite_fn=CountingRewriter(), render_fn=renderer)
    # Every re-render of the same character uses the character-derived seed (stable).
    assert renderer.seeds and all(s == rfj.seed_for("sai_ma") for s in renderer.seeds)


def test_rerender_seed_falls_back_to_item_id(tmp_path):
    item = make_item(tmp_path, "beat_07", character_id=None)
    judge = ScriptedJudge({"beat_07": [50, 50]})
    renderer = CountingRenderer()
    rfj.run_frame_judge([item], rfj.JudgeConfig(threshold=80, max_retries=1),
                        judge_fn=judge, rewrite_fn=CountingRewriter(), render_fn=renderer)
    assert renderer.seeds == [rfj.seed_for("beat_07")]


# ───────────────────────── manga dual-use ─────────────────────────

def test_manga_panel_vs_scene_description(tmp_path):
    """The manga caller: target_text = scene_description, keyed by character_id."""
    panels = [
        rfj.JudgeItem("panel_1", _png(tmp_path, "panel_1.png"),
                      target_text="Sai Ma stands at the temple gate at dawn",
                      prompt="scene: temple gate", character_id="sai_ma"),
        rfj.JudgeItem("panel_2", _png(tmp_path, "panel_2.png"),
                      target_text="Sai Ma raises a lantern",
                      prompt="scene: lantern", character_id="sai_ma"),
    ]
    judge = ScriptedJudge({"panel_1": [85], "panel_2": [40, 88]})
    renderer = CountingRenderer()
    verdicts = rfj.run_frame_judge(panels, rfj.JudgeConfig(threshold=80),
                                   judge_fn=judge, rewrite_fn=CountingRewriter(), render_fn=renderer)
    assert [v.id for v in verdicts] == ["panel_1", "panel_2"]
    assert verdicts[0].passed(80) and verdicts[0].attempts == 0
    assert verdicts[1].passed(80) and verdicts[1].attempts == 1
    # both panels of the same character re-rendered with the same seed.
    assert all(s == rfj.seed_for("sai_ma") for s in renderer.seeds)


# ───────────────────────── checkpoint resume ─────────────────────────

def test_checkpoint_is_written_per_item(tmp_path):
    items = [make_item(tmp_path, "a"), make_item(tmp_path, "b")]
    judge = ScriptedJudge({"a": [90], "b": [91]})
    ckpt = tmp_path / "ckpt.json"
    rfj.run_frame_judge(items, rfj.JudgeConfig(threshold=80),
                        judge_fn=judge, rewrite_fn=CountingRewriter(),
                        render_fn=CountingRenderer(), checkpoint_path=ckpt)
    data = json.loads(ckpt.read_text())
    assert {v["id"] for v in data["verdicts"]} == {"a", "b"}


def test_checkpoint_resume_skips_done_items(tmp_path):
    items = [make_item(tmp_path, "a"), make_item(tmp_path, "b")]
    ckpt = tmp_path / "ckpt.json"
    ckpt.write_text(json.dumps({"verdicts": [
        {"id": "a", "score": 88, "missing": [], "wrong": [], "present": [],
         "suggested_fix": "", "attempts": 0, "kept_image": "old.png", "kept_prompt": "p"}
    ]}))
    judge = ScriptedJudge({"b": [92]})  # 'a' must NOT be re-judged
    verdicts = rfj.run_frame_judge(items, rfj.JudgeConfig(threshold=80),
                                   judge_fn=judge, rewrite_fn=CountingRewriter(),
                                   render_fn=CountingRenderer(), checkpoint_path=ckpt)
    assert judge.calls == ["b"]  # 'a' resumed from checkpoint, only 'b' judged
    assert verdicts[0].id == "a" and verdicts[0].score == 88
    assert verdicts[1].id == "b" and verdicts[1].score == 92


# ───────────────────────── loaders + dataclasses ─────────────────────────

def test_items_from_beats_video(tmp_path):
    frames = tmp_path / "frames"
    frames.mkdir()
    manifest = tmp_path / "beats.json"
    manifest.write_text(json.dumps([
        {"id": "beat_00", "text": "opening", "prompt": "scene: open", "frame_index": 0},
        {"id": "beat_01", "text": "rising", "prompt": "scene: rise", "frame_index": 5},
    ]))
    items = rfj.items_from_beats(manifest, frames)
    assert [it.id for it in items] == ["beat_00", "beat_01"]
    assert items[1].image == frames / "frame_0005.png"
    assert items[0].target_text == "opening"


def test_items_from_beats_manga_scene_description(tmp_path):
    manifest = tmp_path / "panels.json"
    manifest.write_text(json.dumps({"beats": [
        {"id": "p0", "scene_description": "gate at dawn", "prompt": "scene: gate",
         "image": str(tmp_path / "p0.png"), "character_id": "sai_ma"},
    ]}))
    items = rfj.items_from_beats(manifest, tmp_path, text_key="scene_description")
    assert items[0].target_text == "gate at dawn"
    assert items[0].character_id == "sai_ma"
    assert items[0].image == tmp_path / "p0.png"


def test_verdict_to_dict_roundtrip():
    v = rfj.JudgeVerdict("a", 80, [], [], [], "fix", attempts=1,
                         kept_image=Path("x.png"), kept_prompt="p")
    d = v.to_dict()
    assert d["kept_image"] == "x.png"  # Path coerced to str for JSON
    again = rfj._verdict_from_dict(d)
    assert again.id == "a" and again.score == 80 and again.attempts == 1


def test_render_failure_keeps_best_so_far(tmp_path):
    item = make_item(tmp_path, "a")
    judge = ScriptedJudge({"a": [65]})

    def boom(_item, _prompt, _seed):
        raise RuntimeError("comfyui offline")

    [v] = rfj.run_frame_judge([item], rfj.JudgeConfig(threshold=80, max_retries=2),
                              judge_fn=judge, rewrite_fn=CountingRewriter(), render_fn=boom)
    assert v.score == 65  # falls back to the base judgment, no crash
    assert v.kept_image == str(item.image)


# ───────────────────────── CLI ─────────────────────────

def test_cli_help():
    r = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "video" / "run_frame_judge.py"), "--help"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    assert r.returncode == 0
    assert "--frames-dir" in r.stdout and "--beats" in r.stdout
    assert "--threshold" in r.stdout and "--judge-model" in r.stdout
    assert "--comfyui-url" in r.stdout and "--judge-only" in r.stdout


def test_cli_end_to_end_judge_only(tmp_path):
    """Full CLI path with a monkeypatched judge so no live box is touched."""
    frames = tmp_path / "frames"
    frames.mkdir()
    (frames / "frame_0000.png").write_bytes(b"\x89PNGstub")
    (frames / "frame_0001.png").write_bytes(b"\x89PNGstub")
    manifest = tmp_path / "beats.json"
    manifest.write_text(json.dumps([
        {"id": "b0", "text": "t0", "prompt": "p0", "frame_index": 0},
        {"id": "b1", "text": "t1", "prompt": "p1", "frame_index": 1},
    ]))
    report = tmp_path / "report.json"
    # Drive main() in-process with a stub judge (avoids spawning + network).
    import run_frame_judge as mod
    orig = mod.OllamaJudge

    class _StubJudge:
        def __init__(self, _cfg):
            pass

        def __call__(self, item):
            return {"score": 90, "missing": [], "wrong": [], "present": [], "suggested_fix": ""}

    mod.OllamaJudge = _StubJudge
    try:
        rc = mod.main([
            "--frames-dir", str(frames), "--beats", str(manifest),
            "--judge-only", "--report-out", str(report),
        ])
    finally:
        mod.OllamaJudge = orig
    assert rc == 0
    data = json.loads(report.read_text())
    assert data["total"] == 2 and data["passed"] == 2
    assert {v["id"] for v in data["verdicts"]} == {"b0", "b1"}


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
