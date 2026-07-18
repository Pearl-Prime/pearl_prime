#!/usr/bin/env python3
"""run_frame_judge — reusable AI-judge perception-loop gate (Tier-2, no paid API).

Generalizes the v3.7 keep-best judge loop out of the LOCAL-only
``scripts/video/intelligent_v3_7_pipeline.py`` into a reusable module shared by:

  • the canonical beat-driven VIDEO pipeline  (frame  vs beat narration)
  • manga panel QA (``qa_panel_judge.py``)    (panel  vs scene_description)

Both callers feed a list of :class:`JudgeItem` (image path + the verbatim text the
image should depict + the positive prompt that produced it) and get back a
:class:`JudgeVerdict` per item, scored 0-100 by a local vision judge. Items below
``threshold`` have their prompt rewritten by a local LLM, are re-rendered at the
SAME deterministic seed, re-judged, and the highest-scoring attempt is kept.

The whole loop is Tier-2: judge + rewriter are local Ollama, re-render is local
ComfyUI (CLAUDE.md LLM Tier policy — NO closed/paid API). Models, threshold,
retries, and the judge/rewriter/render callables are all injectable, so unit
tests stub them and CI is deterministic without a live Pearl Star box.

Reference implementation lifted from intelligent_v3_7_pipeline.py
(judge :154-163, model defaults :318-319, keep-best :422-444, seed :406);
schema per artifacts/video/video_best_method_20260616/PEARL_VIDEO_AI_JUDGE_GATE_V1_SPEC.md.

Public API (what lane E + the manga consumer bind to):
    JudgeItem(id, image, target_text, prompt, character_id=None, metadata=None)
    JudgeVerdict(id, score, missing, wrong, present, suggested_fix,
                 attempts, kept_image, kept_prompt, error=None)
    JudgeConfig(threshold=80, max_retries=2, judge_model="qwen2.5vl:7b",
                rewriter_model="gemma3:27b", ollama_url=None, comfyui_url=None,
                workflow=DEFAULT_WORKFLOW, checkpoint_path=None,
                resize_over_bytes=1_000_000)
    seed_for(item_id) -> int                       # blake2b(id), deterministic
    OllamaJudge(config)        -> callable(item) -> JudgeVerdict-fields dict
    OllamaRewriter(config)     -> callable(item, verdict) -> str
    ComfyUIRenderer(config)    -> callable(item, prompt, seed) -> bytes
    run_frame_judge(items, config, *, judge_fn=None, rewrite_fn=None,
                    render_fn=None, checkpoint_path=None, progress=None)
                               -> list[JudgeVerdict]
"""
from __future__ import annotations

import argparse
import base64
import dataclasses
import hashlib
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Callable, Optional, Sequence

# ───────────────────────── defaults (mirror v3.7 contract) ─────────────────────────

DEFAULT_JUDGE_MODEL = "qwen2.5vl:7b"
DEFAULT_REWRITER_MODEL = "gemma3:27b"
DEFAULT_THRESHOLD = 80
DEFAULT_MAX_RETRIES = 2
DEFAULT_WORKFLOW = (
    Path(__file__).resolve().parent.parent
    / "image_generation" / "comfyui_workflows" / "flux_dev_narrative.json"
)
# ComfyUI flux_dev_narrative.json node ids (see workflow): 2=positive prompt,
# 4=negative prompt, 5=latent w/h, 6=KSampler seed.
_NODE_POSITIVE = "2"
_NODE_NEGATIVE = "4"
_NODE_LATENT = "5"
_NODE_SAMPLER = "6"

# Style/negative banks carried verbatim from the v3.7 reference (sacred painterly
# register). Callers (e.g. manga) override via JudgeConfig.style_lock / .negative_bank.
DEFAULT_STYLE_LOCK = (
    " Render in oil-on-canvas painterly register with chiaroscuro lighting. "
    "Palette: indigo, violet, gold, rose-gold. Single subject focus, golden-ratio composition, "
    "solid surfaces with clean edges, dark anchor element for grounding. Cinematic still."
)
DEFAULT_NEGATIVE_BANK = (
    "text, signature, watermark, logo, caption, subtitle, version stamp, resolution stamp, "
    "4K, 8K, HD, low contrast, blurry, washed out, hazy, foggy, ethereal blur, "
    "recognizable face, photoreal anatomy, neon, cyan dominance, orange dominance"
)

JUDGE_SYSTEM = (
    "You are a strict visual director scoring whether a rendered image depicts what the "
    "source text describes.\n\n"
    "RULES:\n"
    "1. If the art is intentionally stylized (painterly, cel/manga, etc.), never penalize "
    "   stylization, soft brushwork, or low photographic detail.\n"
    "2. IGNORE any 'no X' phrases in the prompt (e.g. 'no Christ', 'no recognizable face') — "
    "   those are safety constraints, NOT required elements. Do NOT list them as 'missing'.\n"
    "3. Focus ONLY on the POSITIVE scene description: what subjects, objects, named entities, "
    "   actions, emotions, and composition are described. Score 0-100 on how well those appear.\n"
    "4. STRICT scale: 90-100 all named entities + structure; 75-89 missing 1-2 minor; "
    "   60-74 wrong on a primary entity or central composition; 40-59 substantially wrong; "
    "   0-39 nothing matches.\n"
    "5. Be specific in 'missing' — list actual visual elements, not safety tokens.\n\n"
    "Respond with VALID JSON: {\"score\": int 0-100, \"missing\": [string], "
    "\"wrong\": [string], \"present\": [string], \"suggested_fix\": \"string under 40 words\"}"
)

REWRITER_SYSTEM = (
    "You are a senior prompt engineer rewriting a failed image-generation prompt. The image "
    "dropped or substituted named entities described in the source text.\n\n"
    "RULES YOU MUST FOLLOW:\n"
    "1. Put the SUBJECT FIRST (first 15 words). Don't bury named entities behind style.\n"
    "2. ORDER: Subject -> Action -> Setting -> Lighting -> Style -> Camera.\n"
    "3. Natural prose, 40-70 words. NO tag soup.\n"
    "4. For named entities: describe-then-name ('An elderly monk with white beard and indigo "
    "   robe - Master Fun') to bind the name to visual specs.\n"
    "5. If the failure leaked the wrong tradition/identity, correct it descriptively, not as a "
    "   negative.\n"
    "6. Never include 'watermark' or '4K' in the positive prompt.\n\n"
    "Respond with VALID JSON: {\"prompt\": \"the rewritten prompt under 70 words\"}"
)


# ───────────────────────────── data types ─────────────────────────────

@dataclasses.dataclass
class JudgeItem:
    """One thing to judge: an image + the text it should depict + its source prompt.

    Generic over the two callers:
      • video: ``target_text`` = verbatim beat narration; ``prompt`` = the render prompt.
      • manga: ``target_text`` = ``scene_description`` / panel description; ``prompt`` = panel prompt.
    """
    id: str
    image: Path
    target_text: str
    prompt: str
    character_id: Optional[str] = None
    metadata: Optional[dict] = None

    def __post_init__(self) -> None:
        self.image = Path(self.image)


@dataclasses.dataclass
class JudgeVerdict:
    """Per-item result. ``score`` is the kept (best) score after the loop."""
    id: str
    score: int
    missing: list
    wrong: list
    present: list
    suggested_fix: str
    attempts: int = 0          # number of re-render attempts performed (0 = first frame kept)
    kept_image: Optional[str] = None
    kept_prompt: Optional[str] = None
    error: Optional[str] = None

    def passed(self, threshold: int) -> bool:
        return self.score >= threshold

    def to_dict(self) -> dict:
        d = dataclasses.asdict(self)
        if d.get("kept_image") is not None:
            d["kept_image"] = str(d["kept_image"])
        return d


@dataclasses.dataclass
class JudgeConfig:
    threshold: int = DEFAULT_THRESHOLD
    max_retries: int = DEFAULT_MAX_RETRIES
    judge_model: str = DEFAULT_JUDGE_MODEL
    rewriter_model: str = DEFAULT_REWRITER_MODEL
    ollama_url: Optional[str] = None
    comfyui_url: Optional[str] = None
    workflow: Path = DEFAULT_WORKFLOW
    width: int = 1920
    height: int = 1080
    style_lock: str = DEFAULT_STYLE_LOCK
    negative_bank: str = DEFAULT_NEGATIVE_BANK
    checkpoint_path: Optional[Path] = None
    resize_over_bytes: int = 1_000_000
    request_timeout: int = 300

    def resolved_ollama_url(self) -> str:
        if self.ollama_url:
            return self.ollama_url.rstrip("/")
        ip = os.environ.get("PEARL_STAR_IP", "").strip()
        if not ip:
            raise RuntimeError("ollama_url unset and PEARL_STAR_IP not in env")
        return f"http://{ip}:11434"


# Callable type aliases (the injection seam used by tests + lane E).
JudgeFn = Callable[[JudgeItem], dict]            # -> {score, missing, wrong, present, suggested_fix}
RewriteFn = Callable[[JudgeItem, dict], str]     # -> rewritten prompt
RenderFn = Callable[[JudgeItem, str, int], bytes]  # (item, prompt, seed) -> png bytes


# ───────────────────────────── seed ─────────────────────────────

def seed_for(item_id: str, *, digest_size: int = 4) -> int:
    """Deterministic seed from an id (blake2b) — matches v3.7 :406.

    Video keys on ``beat_id`` (new scene each time). Manga keys on ``character_id``
    (stable across panels) — pass that as the id to hold a character consistent.
    """
    return int.from_bytes(
        hashlib.blake2b(item_id.encode("utf-8"), digest_size=digest_size).digest(), "big"
    )


# ───────────────────────── Ollama transport ─────────────────────────

def _ollama_chat(url: str, model: str, messages: list, *,
                 images: Optional[Sequence[bytes]] = None, fmt_json: bool = False,
                 timeout: int = 300, resize_over_bytes: int = 1_000_000) -> str:
    payload = {
        "model": model,
        "messages": [dict(m) for m in messages],
        "stream": False,
        "keep_alive": -1,
        "options": {"num_predict": 1024, "temperature": 0.2},
    }
    if fmt_json:
        payload["format"] = "json"
    if images:
        encoded = [_encode_image(raw, resize_over_bytes) for raw in images]
        for m in reversed(payload["messages"]):
            if m.get("role") == "user":
                m["images"] = encoded
                break
    req = urllib.request.Request(
        url.rstrip("/") + "/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.loads(r.read())
    return data.get("message", {}).get("content", "")


def _encode_image(raw: bytes, resize_over_bytes: int) -> str:
    """base64-encode; downscale large images to keep the vision payload light."""
    if resize_over_bytes and len(raw) > resize_over_bytes:
        try:
            from io import BytesIO
            from PIL import Image  # type: ignore

            img = Image.open(BytesIO(raw)).convert("RGB")
            w, h = img.size
            new_w = 768
            new_h = max(1, int(h * new_w / w))
            img = img.resize((new_w, new_h), Image.LANCZOS)
            buf = BytesIO()
            img.save(buf, format="JPEG", quality=85)
            return base64.b64encode(buf.getvalue()).decode("ascii")
        except Exception:
            pass
    return base64.b64encode(raw).decode("ascii")


# ───────────────────────── default judge / rewrite / render ─────────────────────────

def _strip_safety_prefix(prompt: str) -> str:
    for marker in ("composition: ", "scene: "):
        idx = prompt.rfind(marker)
        if idx != -1:
            return prompt[idx + len(marker):].strip()
    return prompt


def _parse_judge_json(raw: str) -> dict:
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if not m:
        return {"score": 50, "missing": [], "wrong": [], "present": [],
                "suggested_fix": "(judge returned no JSON)"}
    d = json.loads(m.group(0))
    return {
        "score": int(d.get("score", 50)),
        "missing": list(d.get("missing", []))[:8],
        "wrong": list(d.get("wrong", []))[:8],
        "present": list(d.get("present", []))[:8],
        "suggested_fix": str(d.get("suggested_fix", "")).strip()[:300],
    }


class OllamaJudge:
    """Default vision judge (Qwen2.5-VL via local Ollama). Callable(item) -> fields dict."""

    def __init__(self, config: JudgeConfig):
        self.config = config

    def __call__(self, item: JudgeItem) -> dict:
        cfg = self.config
        scene_only = _strip_safety_prefix(item.prompt)
        user_content = (
            f"SOURCE TEXT (verbatim, what the image should depict): \"{item.target_text}\"\n\n"
            f"POSITIVE SCENE DESCRIPTION: \"{scene_only}\"\n\n"
            f"Now look at the attached image. Score 0-100 on how well it depicts the POSITIVE "
            f"scene elements above. Ignore any 'no X' safety tokens. List what's actually "
            f"missing (visual gaps, not safety phrases), what's wrong, what's present. "
            f"Suggest a concrete fix to the prompt."
        )
        try:
            raw = _ollama_chat(
                cfg.resolved_ollama_url(), cfg.judge_model,
                [{"role": "system", "content": JUDGE_SYSTEM},
                 {"role": "user", "content": user_content}],
                images=[item.image.read_bytes()],
                fmt_json=True, timeout=min(cfg.request_timeout, 120),
                resize_over_bytes=cfg.resize_over_bytes,
            )
            return _parse_judge_json(raw)
        except Exception as exc:  # noqa: BLE001 — judge failure is data, not a crash
            return {"score": -1, "missing": [], "wrong": [], "present": [],
                    "suggested_fix": f"(judge error: {exc!r})"}


class OllamaRewriter:
    """Default prompt rewriter (Gemma3 via local Ollama). Callable(item, verdict) -> prompt."""

    def __init__(self, config: JudgeConfig):
        self.config = config

    def __call__(self, item: JudgeItem, verdict: dict) -> str:
        cfg = self.config
        user_content = (
            f"SOURCE TEXT: \"{item.target_text}\"\n\n"
            f"FAILED PROMPT (image scored {verdict.get('score')}/100): \"{item.prompt}\"\n\n"
            f"JUDGE FEEDBACK:\n"
            f"  missing in image: {verdict.get('missing')}\n"
            f"  wrong in image: {verdict.get('wrong')}\n"
            f"  fix suggestion: {verdict.get('suggested_fix')}\n\n"
            f"Rewrite the prompt following the rules above."
        )
        try:
            raw = _ollama_chat(
                cfg.resolved_ollama_url(), cfg.rewriter_model,
                [{"role": "system", "content": REWRITER_SYSTEM},
                 {"role": "user", "content": user_content}],
                fmt_json=True, timeout=min(cfg.request_timeout, 90),
            )
            m = re.search(r"\{.*\}", raw, re.DOTALL)
            if m:
                p = str(json.loads(m.group(0)).get("prompt", "")).strip()
                if 20 <= len(p) <= 700:
                    return p
        except Exception:  # noqa: BLE001 — fall back to heuristic augment
            pass
        return _heuristic_augment(item.prompt, verdict, item.target_text)


def _heuristic_augment(old: str, verdict: dict, target_text: str) -> str:
    missing = ", ".join(verdict.get("missing", []))
    add = []
    if missing:
        add.append(f"Must clearly show: {missing}.")
    return f"{target_text.rstrip('.').strip()}. {old} {' '.join(add)}".strip()


class ComfyUIRenderer:
    """Default re-render (flux1-dev workflow via local ComfyUI). Callable(item, prompt, seed) -> bytes."""

    def __init__(self, config: JudgeConfig):
        self.config = config
        self._workflow_cache: Optional[dict] = None

    def _workflow(self) -> dict:
        if self._workflow_cache is None:
            wf = json.loads(Path(self.config.workflow).read_text(encoding="utf-8"))
            self._workflow_cache = {k: v for k, v in wf.items() if k != "_meta"}
        return json.loads(json.dumps(self._workflow_cache))  # deep copy per call

    def __call__(self, item: JudgeItem, prompt: str, seed: int) -> bytes:
        cfg = self.config
        if not cfg.comfyui_url:
            raise RuntimeError("comfyui_url unset; cannot re-render")
        wf = self._workflow()
        wf[_NODE_POSITIVE]["inputs"]["text"] = prompt + cfg.style_lock
        wf[_NODE_NEGATIVE]["inputs"]["text"] = cfg.negative_bank
        wf[_NODE_LATENT]["inputs"]["width"] = int(cfg.width)
        wf[_NODE_LATENT]["inputs"]["height"] = int(cfg.height)
        wf[_NODE_SAMPLER]["inputs"]["seed"] = int(seed)

        url = cfg.comfyui_url.rstrip("/")
        payload = json.dumps({"prompt": wf}).encode("utf-8")
        req = urllib.request.Request(f"{url}/prompt", data=payload,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            prompt_id = json.loads(resp.read())["prompt_id"]
        deadline = time.monotonic() + 600
        while time.monotonic() < deadline:
            time.sleep(3)
            hreq = urllib.request.Request(f"{url}/history/{prompt_id}")
            with urllib.request.urlopen(hreq, timeout=15) as hresp:
                history = json.loads(hresp.read())
            if prompt_id in history:
                for node_out in history[prompt_id].get("outputs", {}).values():
                    for img in node_out.get("images", []):
                        params = urllib.parse.urlencode({
                            "filename": img["filename"],
                            "subfolder": img.get("subfolder", ""),
                            "type": img.get("type", "output"),
                        })
                        with urllib.request.urlopen(f"{url}/view?{params}", timeout=60) as iresp:
                            return iresp.read()
        raise RuntimeError(f"flux-dev render timed out prompt_id={prompt_id}")


# ───────────────────────────── the loop ─────────────────────────────

def run_frame_judge(
    items: Sequence[JudgeItem],
    config: Optional[JudgeConfig] = None,
    *,
    judge_fn: Optional[JudgeFn] = None,
    rewrite_fn: Optional[RewriteFn] = None,
    render_fn: Optional[RenderFn] = None,
    checkpoint_path: Optional[Path] = None,
    progress: Optional[Callable[[str], None]] = None,
) -> list[JudgeVerdict]:
    """Judge each item; rewrite + re-render + re-judge sub-threshold items, keep best.

    The three callables (judge/rewrite/render) default to the local Ollama/ComfyUI
    implementations but are injectable — unit tests pass stubs so no live box is
    needed. ``render_fn`` may be ``None`` (judge-only / render-disabled): then
    sub-threshold items are reported as-is with attempts=0.

    Returns one :class:`JudgeVerdict` per input item, in input order. Resumable: if
    ``checkpoint_path`` (or ``config.checkpoint_path``) exists, verdicts already
    recorded there are reused and skipped.
    """
    config = config or JudgeConfig()
    judge_fn = judge_fn or OllamaJudge(config)
    rewrite_fn = rewrite_fn or OllamaRewriter(config)
    if render_fn is None and config.comfyui_url:
        render_fn = ComfyUIRenderer(config)
    ckpt = checkpoint_path or config.checkpoint_path
    log = progress or (lambda _msg: None)

    done: dict[str, dict] = {}
    if ckpt and Path(ckpt).exists():
        try:
            prior = json.loads(Path(ckpt).read_text(encoding="utf-8"))
            done = {v["id"]: v for v in prior.get("verdicts", [])}
            log(f"resumed checkpoint: {len(done)} verdict(s)")
        except Exception:  # noqa: BLE001 — corrupt checkpoint = start clean
            done = {}

    verdicts: list[JudgeVerdict] = []
    for i, item in enumerate(items):
        if item.id in done:
            verdicts.append(_verdict_from_dict(done[item.id]))
            log(f"[{i + 1}/{len(items)}] {item.id} [cached]")
            continue
        verdict = _judge_one(item, config, judge_fn, rewrite_fn, render_fn, log, i, len(items))
        verdicts.append(verdict)
        if ckpt:
            done[item.id] = verdict.to_dict()
            Path(ckpt).write_text(
                json.dumps({
                    "judge_model": config.judge_model,
                    "threshold": config.threshold,
                    "verdicts": [v.to_dict() for v in verdicts],
                }, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
    return verdicts


def _judge_one(item, config, judge_fn, rewrite_fn, render_fn, log, i, n) -> JudgeVerdict:
    if not item.image.exists():
        return JudgeVerdict(item.id, 0, ["source image missing"], [], [],
                            "must be rendered", attempts=0, kept_image=str(item.image),
                            kept_prompt=item.prompt, error="image-missing")

    base = judge_fn(item)
    best_score = int(base.get("score", -1))
    best = dict(base)
    best_image = item.image
    best_prompt = item.prompt
    attempts = 0
    sym = "ok" if best_score >= config.threshold else "x "
    log(f"[{i + 1}/{n}] {sym} {item.id} score={best_score}")

    if best_score < config.threshold and render_fn is not None:
        seed = seed_for(item.character_id or item.id)
        prompt = item.prompt
        cur_verdict = base
        for attempt in range(1, config.max_retries + 1):
            attempts = attempt
            new_prompt = rewrite_fn(item, cur_verdict)
            try:
                png = render_fn(item, new_prompt, seed)
            except Exception as exc:  # noqa: BLE001 — render failure: keep best so far
                log(f"    {item.id} render attempt {attempt} failed: {exc!r}")
                break
            out_path = item.image.with_name(f"{item.image.stem}__judge_a{attempt}.png")
            try:
                out_path.write_bytes(png)
            except Exception:  # noqa: BLE001
                out_path = item.image
            reitem = JudgeItem(item.id, out_path, item.target_text, new_prompt,
                               item.character_id, item.metadata)
            cur_verdict = judge_fn(reitem)
            new_score = int(cur_verdict.get("score", -1))
            log(f"    {item.id} attempt {attempt}: {best_score} -> {new_score}")
            if new_score > best_score:
                best_score, best, best_image, best_prompt = new_score, dict(cur_verdict), out_path, new_prompt
            prompt = new_prompt
            if best_score >= config.threshold:
                break

    return JudgeVerdict(
        id=item.id,
        score=best_score,
        missing=list(best.get("missing", [])),
        wrong=list(best.get("wrong", [])),
        present=list(best.get("present", [])),
        suggested_fix=str(best.get("suggested_fix", "")),
        attempts=attempts,
        kept_image=str(best_image),
        kept_prompt=best_prompt,
        error=("judge-error" if best_score < 0 else None),
    )


def _verdict_from_dict(d: dict) -> JudgeVerdict:
    fields = {f.name for f in dataclasses.fields(JudgeVerdict)}
    return JudgeVerdict(**{k: v for k, v in d.items() if k in fields})


# ───────────────────────── beat / panel loaders ─────────────────────────

def items_from_beats(beats_json: Path, frames_dir: Path, *,
                     text_key: str = "text", prompt_key: str = "prompt",
                     id_key: str = "id") -> list[JudgeItem]:
    """Load JudgeItems from a beats/panels JSON manifest.

    Each entry needs an id, the target text (``text`` for video beats /
    ``scene_description`` for manga panels — set ``text_key``), the source prompt,
    and either an explicit ``image``/``frame`` path or a ``frame_index`` resolved
    against ``frames_dir`` as ``frame_<idx:04d>.png``.
    """
    data = json.loads(Path(beats_json).read_text(encoding="utf-8"))
    entries = data["beats"] if isinstance(data, dict) and "beats" in data else data
    items: list[JudgeItem] = []
    for n, b in enumerate(entries):
        bid = str(b.get(id_key, n))
        if b.get("image") or b.get("frame"):
            image = Path(b.get("image") or b["frame"])
        else:
            idx = int(b.get("frame_index", n))
            image = Path(frames_dir) / f"frame_{idx:04d}.png"
        items.append(JudgeItem(
            id=bid,
            image=image,
            target_text=str(b.get(text_key, "")),
            prompt=str(b.get(prompt_key, "")),
            character_id=b.get("character_id"),
            metadata={k: v for k, v in b.items()
                      if k not in {id_key, text_key, prompt_key, "image", "frame"}},
        ))
    return items


# ───────────────────────────── CLI ─────────────────────────────

def build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="run_frame_judge",
        description="Reusable AI-judge perception-loop gate (Tier-2, local Ollama/ComfyUI).",
    )
    ap.add_argument("--frames-dir", type=Path, required=True,
                    help="dir holding frame_<idx>.png renders")
    ap.add_argument("--beats", type=Path, required=True,
                    help="beats/panels JSON manifest (id + text + prompt [+ frame_index])")
    ap.add_argument("--text-key", default="text",
                    help="manifest key for the target text (video: 'text'; manga: 'scene_description')")
    ap.add_argument("--threshold", type=int, default=DEFAULT_THRESHOLD)
    ap.add_argument("--max-retries", type=int, default=DEFAULT_MAX_RETRIES)
    ap.add_argument("--judge-model", default=DEFAULT_JUDGE_MODEL)
    ap.add_argument("--rewriter-model", default=DEFAULT_REWRITER_MODEL)
    ap.add_argument("--ollama-url", default=None,
                    help="override; else http://$PEARL_STAR_IP:11434")
    ap.add_argument("--comfyui-url", default=None,
                    help="ComfyUI base url; omit to run judge-only (no re-render)")
    ap.add_argument("--workflow", type=Path, default=DEFAULT_WORKFLOW)
    ap.add_argument("--checkpoint-out", type=Path, default=None,
                    help="resumable per-frame verdict checkpoint JSON")
    ap.add_argument("--report-out", type=Path, default=None,
                    help="final verdict report JSON (default: stdout)")
    ap.add_argument("--judge-only", action="store_true",
                    help="judge + report only; never re-render even if --comfyui-url is set")
    return ap


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    config = JudgeConfig(
        threshold=args.threshold,
        max_retries=args.max_retries,
        judge_model=args.judge_model,
        rewriter_model=args.rewriter_model,
        ollama_url=args.ollama_url,
        comfyui_url=None if args.judge_only else args.comfyui_url,
        workflow=args.workflow,
        checkpoint_path=args.checkpoint_out,
    )
    items = items_from_beats(args.beats, args.frames_dir, text_key=args.text_key)
    print(f"[run_frame_judge] {len(items)} item(s); threshold={config.threshold} "
          f"judge={config.judge_model} render={'off' if not config.comfyui_url else 'on'}",
          file=sys.stderr, flush=True)

    verdicts = run_frame_judge(
        items, config,
        checkpoint_path=args.checkpoint_out,
        progress=lambda m: print(f"  {m}", file=sys.stderr, flush=True),
    )
    passed = sum(1 for v in verdicts if v.passed(config.threshold))
    report = {
        "judge_model": config.judge_model,
        "rewriter_model": config.rewriter_model,
        "threshold": config.threshold,
        "total": len(verdicts),
        "passed": passed,
        "failed": len(verdicts) - passed,
        "verdicts": [v.to_dict() for v in verdicts],
    }
    out = json.dumps(report, indent=2, ensure_ascii=False)
    if args.report_out:
        Path(args.report_out).write_text(out, encoding="utf-8")
        print(f"[run_frame_judge] wrote {args.report_out} "
              f"({passed}/{len(verdicts)} passed)", file=sys.stderr)
    else:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
