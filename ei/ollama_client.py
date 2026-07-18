"""
ei.ollama_client — free/local embeddings + LLM, no paid API (CLAUDE.md).

Two capabilities:
  1) embed(texts)      — vector embeddings for the spine/CEG and fitness.
  2) generate_json(...) — structured LLM output for the Reader Council.

Backends (all free/local):
  - embeddings:  sentence-transformers (local CPU) if importable & backend allows,
                 else Ollama on Pearl Star (GPU).
  - generation:  Ollama on Pearl Star (gemma3:27b / qwen2.5:14b), native
                 `format: json` for structured output (Outlines-equivalent).

Transport to Pearl Star Ollama:
  - On this box the Tailscale HTTP host is not always curl-resolvable, but the
    ssh alias `pearl_star` works. transport="auto" tries HTTP, falls back to ssh.
    The ssh path shells `curl http://localhost:11434/...` ON Pearl Star.

Determinism: embeddings are cached to disk by sha256(model|text). Generation uses
a fixed seed + temperature 0 where the backend supports it.
"""

from __future__ import annotations

import hashlib
import json
import shlex
import subprocess
from pathlib import Path
from typing import Iterable

import numpy as np

from . import config as C


# ---------------------------------------------------------------------------
# disk cache
# ---------------------------------------------------------------------------
def _cache_path(key: str) -> Path:
    C.ensure_dirs()
    h = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return C.CACHE_DIR / f"emb_{h}.npy"


# ---------------------------------------------------------------------------
# Ollama transport
# ---------------------------------------------------------------------------
def _ollama_http(path: str, payload: dict, timeout: int) -> dict | None:
    try:
        import urllib.request

        url = C.OLLAMA["http_url"].rstrip("/") + path
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def _ollama_ssh(path: str, payload: dict, timeout: int) -> dict | None:
    """Run curl against Ollama ON Pearl Star via ssh (the proven path here)."""
    host = C.OLLAMA["ssh_host"]
    body = json.dumps(payload)
    # localhost on Pearl Star
    remote = (
        f"curl -s --max-time {timeout} http://localhost:11434{path} "
        f"-H 'Content-Type: application/json' -d {shlex.quote(body)}"
    )
    try:
        proc = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=10", "-o", "BatchMode=yes", host, remote],
            capture_output=True, text=True, timeout=timeout + 25,
        )
        if proc.returncode != 0 or not proc.stdout.strip():
            return None
        return json.loads(proc.stdout)
    except Exception:
        return None


def ollama_call(path: str, payload: dict, timeout: int | None = None) -> dict | None:
    timeout = timeout or C.OLLAMA["timeout_s"]
    transport = C.OLLAMA["transport"]
    if transport in ("auto", "http"):
        r = _ollama_http(path, payload, timeout)
        if r is not None:
            return r
        if transport == "http":
            return None
    # auto-fallback or explicit ssh
    return _ollama_ssh(path, payload, timeout)


def ollama_available() -> bool:
    # GET /api/tags via the same transport (http then ssh).
    r = ollama_call("/api/tags", {}, timeout=20)
    if r and "models" in r:
        return True
    # ssh GET fallback (ollama_call posts a body; do a clean GET here)
    try:
        host = C.OLLAMA["ssh_host"]
        proc = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=10", "-o", "BatchMode=yes", host,
             "curl -s --max-time 20 http://localhost:11434/api/tags"],
            capture_output=True, text=True, timeout=45,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            d = json.loads(proc.stdout)
            return "models" in d
    except Exception:
        pass
    return False


# ---------------------------------------------------------------------------
# Embeddings
# ---------------------------------------------------------------------------
class _STModel:
    _model = None
    _name = None

    @classmethod
    def get(cls, name: str):
        if cls._model is not None and cls._name == name:
            return cls._model
        from sentence_transformers import SentenceTransformer  # may raise ImportError

        cls._model = SentenceTransformer(name)
        cls._name = name
        return cls._model


def _embed_sentence_transformers(texts: list[str], model_name: str) -> np.ndarray | None:
    try:
        model = _STModel.get(model_name)
    except Exception:
        return None
    vecs = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return np.asarray(vecs, dtype=np.float32)


def _embed_ollama_one(text: str, model: str) -> list[float] | None:
    r = ollama_call("/api/embeddings", {"model": model, "prompt": text})
    if r and isinstance(r.get("embedding"), list):
        return r["embedding"]
    return None


_REMOTE_EMBED_SCRIPT = r'''
import sys, json, urllib.request
model = sys.argv[1]
texts = json.load(sys.stdin)
out = []
for t in texts:
    data = json.dumps({"model": model, "prompt": t}).encode()
    req = urllib.request.Request("http://localhost:11434/api/embeddings", data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        out.append(json.loads(r.read().decode())["embedding"])
sys.stdout.write(json.dumps(out))
'''


def embed_batch_remote(texts: list[str], model: str) -> np.ndarray | None:
    """
    Embed ALL texts in ONE ssh call: a remote python process keeps the Ollama
    model warm in GPU and loops /api/embeddings locally on Pearl Star, then
    returns every vector at once. Turns N ssh round-trips into 1.
    """
    host = C.OLLAMA["ssh_host"]
    payload = json.dumps(texts)
    # generous timeout: ~0.15s/text once warm, plus model load.
    timeout = max(180, int(len(texts) * 0.5) + 120)
    try:
        proc = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=10", "-o", "BatchMode=yes", host,
             f"python3 -c {shlex.quote(_REMOTE_EMBED_SCRIPT)} {shlex.quote(model)}"],
            input=payload, capture_output=True, text=True, timeout=timeout,
        )
        if proc.returncode != 0 or not proc.stdout.strip():
            return None
        rows = json.loads(proc.stdout)
        mat = np.asarray(rows, dtype=np.float32)
        norms = np.linalg.norm(mat, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return mat / norms
    except Exception:
        return None


def embed(texts: Iterable[str], backend: str | None = None) -> np.ndarray:
    """
    Return an (N, D) float32 matrix of L2-normalized embeddings.

    backend: None -> use config. "sentence_transformers" | "ollama" | "auto".
    Cached to disk per (model, text). Pure-local; no paid API.
    """
    texts = [t if isinstance(t, str) else str(t) for t in texts]
    backend = backend or C.EMBED["backend"]

    # resolve effective backend
    use_st = False
    if backend in ("auto", "sentence_transformers"):
        try:
            import sentence_transformers  # noqa: F401

            use_st = True
        except Exception:
            use_st = False
            if backend == "sentence_transformers":
                raise RuntimeError("sentence-transformers requested but not installed")

    model_tag = C.EMBED["st_model"] if use_st else C.EMBED["ollama_embed_model"]

    # cache lookup
    vectors: list[np.ndarray | None] = [None] * len(texts)
    to_compute_idx: list[int] = []
    if C.EMBED["cache"]:
        for i, t in enumerate(texts):
            cp = _cache_path(f"{model_tag}|{t}")
            if cp.exists():
                try:
                    vectors[i] = np.load(cp)
                    continue
                except Exception:
                    pass
            to_compute_idx.append(i)
    else:
        to_compute_idx = list(range(len(texts)))

    if to_compute_idx:
        pending = [texts[i] for i in to_compute_idx]
        if use_st:
            mat = _embed_sentence_transformers(pending, model_tag)
            if mat is None:
                use_st = False  # fall through to ollama below
        if not use_st:
            model_tag = C.EMBED["ollama_embed_model"]
            # FAST PATH: one ssh call, model stays warm on Pearl Star GPU.
            mat = embed_batch_remote(pending, model_tag)
            if mat is None:
                # slow per-text fallback (still free/local)
                rows = []
                for t in pending:
                    v = _embed_ollama_one(t, model_tag)
                    if v is None:
                        raise RuntimeError(
                            "Ollama embedding failed (Pearl Star unreachable?). "
                            "No paid-API fallback by policy."
                        )
                    rows.append(v)
                mat = np.asarray(rows, dtype=np.float32)
                norms = np.linalg.norm(mat, axis=1, keepdims=True)
                norms[norms == 0] = 1.0
                mat = mat / norms

        for j, i in enumerate(to_compute_idx):
            vectors[i] = mat[j].astype(np.float32)
            if C.EMBED["cache"]:
                np.save(_cache_path(f"{model_tag}|{texts[i]}"), vectors[i])

    return np.vstack([v.reshape(1, -1) for v in vectors])


def embedding_backend_name() -> str:
    """What embed() will actually use, for honest provenance in artifacts."""
    b = C.EMBED["backend"]
    if b in ("auto", "sentence_transformers"):
        try:
            import sentence_transformers  # noqa: F401

            return f"sentence-transformers:{C.EMBED['st_model']} (local CPU)"
        except Exception:
            if b == "sentence_transformers":
                return "sentence-transformers (MISSING)"
    return f"ollama:{C.EMBED['ollama_embed_model']} (Pearl Star GPU)"


# ---------------------------------------------------------------------------
# Structured generation (Reader Council)
# ---------------------------------------------------------------------------
def generate_json(prompt: str, model: str | None = None, *, seed: int = 42,
                  timeout: int | None = None, system: str | None = None) -> dict | None:
    """
    Ask an Ollama model for a single JSON object (native format=json).
    Returns the parsed dict, or None on failure. Free/local only.
    """
    model = model or C.OLLAMA["council_model"]
    payload = {
        "model": model,
        "prompt": prompt,
        "format": "json",
        "stream": False,
        "options": {"temperature": 0.0, "seed": seed, "num_ctx": 8192},
    }
    if system:
        payload["system"] = system
    r = ollama_call("/api/generate", payload, timeout=timeout)
    if not r:
        return None
    resp = r.get("response", "")
    if not resp:
        return None
    try:
        return json.loads(resp)
    except Exception:
        # tolerate stray text around the JSON
        start = resp.find("{")
        end = resp.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(resp[start : end + 1])
            except Exception:
                return None
    return None
