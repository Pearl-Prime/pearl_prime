#!/usr/bin/env python3
"""Parallel-chunk downloader for HuggingFace large files.

Empirical motivation (2026-05-20, Pearl Star RTX 5070 Ti):
  The standard `hf download` / `huggingface_hub` xet-protocol path stalls on
  Pearl Star's WAN at ~24-46 KB/s — single-stream HF cas-bridge throttling per
  connection. A Cloudflare WAN speedtest showed the connection itself sustains
  only ~90 KB/s peak single-stream.

  HF cas-bridge throttles PER CONNECTION, not per IP. Using N parallel curl
  byte-range requests achieved 12.9 MB/s AGGREGATE on a 20.5 GB Qwen-Image-Layered
  fp8mixed model (~24 min vs the single-stream estimate of 5 days).

  This script productionizes the workaround so the next large HF download
  (V5.x model swaps, additional ComfyUI models for ep_002+ archetypes,
  ToonOut variants, etc.) doesn't require re-inventing the approach.

Architecture:
  - HEAD request → content-length
  - Resume-from-incomplete if a `--resume-from <path>` file is supplied
  - N concurrent curl workers each downloading a byte range via `curl -r start-end`
  - Concatenate part files into the final destination
  - Verify final size matches Content-Length

Tier 1 (operator-present). No LLM calls. Per CLAUDE.md tier policy.

Usage:
    python3 scripts/utils/parallel_hf_download.py \\
        --url https://huggingface.co/<repo>/resolve/main/<path>/<file>.safetensors \\
        --dest /path/to/output.safetensors \\
        [--chunks 16] \\
        [--resume-from /path/to/incomplete-file]

Examples:

    # Qwen-Image-Layered fp8mixed (20.5 GB) — what V5 used:
    python3 scripts/utils/parallel_hf_download.py \\
        --url 'https://huggingface.co/Comfy-Org/Qwen-Image-Layered_ComfyUI/resolve/main/split_files/diffusion_models/qwen_image_layered_fp8mixed.safetensors' \\
        --dest /home/ahjan108/phoenix_server/ComfyUI/models/diffusion_models/qwen_image_layered_fp8mixed.safetensors \\
        --chunks 16

    # ToonOut weights (885 MB) — what Phase 1 used:
    python3 scripts/utils/parallel_hf_download.py \\
        --url 'https://huggingface.co/joelseytre/toonout/resolve/main/birefnet_finetuned_toonout.pth' \\
        --dest /home/ahjan108/phoenix_omega/models/cutout/toonout/birefnet_finetuned_toonout.pth \\
        --chunks 8

Empirical results (Pearl Star, 2026-05-20):
  - 20.5 GB / 16 chunks @ ~820 KB/s each = 12.9 MB/s aggregate, 24 min total
  - 885 MB / 8 chunks = 13 MB/s aggregate, 68 sec total
"""
from __future__ import annotations
import argparse
import os
import subprocess
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed


def head_content_length(url: str, timeout: int = 15) -> tuple[int, str]:
    """HEAD request → (content_length, signed_redirect_url)."""
    req = urllib.request.Request(url, method="HEAD")
    req.add_header("Accept", "*/*")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        total = int(r.headers["Content-Length"])
        signed_url = r.url
    return total, signed_url


def fetch_chunk(idx: int, start: int, end: int, url: str, dest_prefix: str) -> tuple[int, int, float, int]:
    """Curl one byte-range chunk to <dest_prefix>.part<idx>.

    Returns (idx, size_bytes, elapsed_sec, returncode).
    """
    out_path = f"{dest_prefix}.part{idx}"
    cmd = [
        "curl",
        "-sL",
        "--retry", "3",
        "--retry-delay", "2",
        "-r", f"{start}-{end}",
        "-o", out_path,
        url,
    ]
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - t0
    size = os.path.getsize(out_path) if os.path.exists(out_path) else 0
    return idx, size, elapsed, r.returncode


def parallel_download(
    url: str,
    dest: str,
    n_chunks: int = 16,
    resume_from: str | None = None,
) -> int:
    """Download `url` → `dest` via N parallel byte-range curl workers.

    If `resume_from` points to an existing partial file, its bytes become part0
    (concatenated at the head) and the remaining range is split across N chunks.

    Returns 0 on size-verified success, non-zero otherwise.
    """
    print(f"=== parallel_hf_download ===")
    print(f"  url:    {url}")
    print(f"  dest:   {dest}")
    print(f"  chunks: {n_chunks}")
    if resume_from:
        print(f"  resume: {resume_from}")

    os.makedirs(os.path.dirname(dest), exist_ok=True)

    try:
        total, signed_url = head_content_length(url)
    except Exception as e:
        print(f"ERROR: HEAD failed: {e}", file=sys.stderr)
        return 1
    print(f"\n  total: {total:,} bytes ({total / (1024**3):.2f} GB)")
    print(f"  signed_url: {signed_url[:96]}...")

    # Resume-from handling: part0 = the bytes we already have
    start_offset = 0
    if resume_from and os.path.exists(resume_from):
        start_offset = os.path.getsize(resume_from)
        pct = 100 * start_offset / total if total else 0
        print(f"  resume_from has {start_offset:,} bytes ({pct:.1f}%); copying to part0")
        subprocess.run(["cp", resume_from, f"{dest}.part0"], check=True)

    remaining = total - start_offset
    if remaining <= 0:
        print("  already complete; concatenating part0 → dest")
        if start_offset == total:
            os.rename(f"{dest}.part0", dest)
            return _verify(dest, total)
        return 1

    chunk_size = remaining // n_chunks
    ranges = []
    for i in range(n_chunks):
        s = start_offset + i * chunk_size
        e = (start_offset + (i + 1) * chunk_size - 1) if i < n_chunks - 1 else total - 1
        ranges.append((i + 1, s, e))  # part 1..N (part0 = resume bytes if any)

    print(f"\n  launching {n_chunks} workers, ~{chunk_size:,} bytes each")
    t_start = time.time()
    results = []
    with ThreadPoolExecutor(max_workers=n_chunks) as ex:
        futs = [ex.submit(fetch_chunk, idx, s, e, url, dest) for idx, s, e in ranges]
        for f in as_completed(futs):
            idx, size, dur, rc = f.result()
            results.append((idx, size, dur, rc))
            kbs = size / dur / 1024 if dur > 0 else 0
            print(f"    part{idx:02d}: {size:>13,} bytes in {dur:5.0f}s ({kbs:6.1f} KB/s) rc={rc}")

    t_dl = time.time() - t_start
    total_dl = sum(r[1] for r in results)
    fails = [r for r in results if r[3] != 0]
    print(f"\n  done: {total_dl:,} bytes in {t_dl:.0f}s ({total_dl / t_dl / 1024:.1f} KB/s aggregate)")
    if fails:
        print(f"  WARNING: {len(fails)} chunks returned non-zero rc — check parts before concatenating", file=sys.stderr)

    print("  concatenating part files → dest...")
    with open(dest, "wb") as out:
        for i in range(n_chunks + 1):
            p = f"{dest}.part{i}"
            if not os.path.exists(p):
                continue
            with open(p, "rb") as f:
                while True:
                    buf = f.read(64 * 1024 * 1024)  # 64 MB read chunks
                    if not buf:
                        break
                    out.write(buf)
            os.remove(p)

    return _verify(dest, total)


def _verify(dest: str, expected: int) -> int:
    final = os.path.getsize(dest)
    diff = final - expected
    ok = "OK" if diff == 0 else "MISMATCH"
    print(f"  final: {final:,} bytes (expected {expected:,}; diff {diff:+d}) [{ok}]")
    return 0 if diff == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", required=True, help="HuggingFace resolve URL")
    ap.add_argument("--dest", required=True, help="Output file path (absolute)")
    ap.add_argument("--chunks", type=int, default=16, help="Number of parallel curl workers (default 16)")
    ap.add_argument("--resume-from", default=None, help="Optional path to an existing partial file to resume from")
    args = ap.parse_args()
    return parallel_download(args.url, args.dest, args.chunks, args.resume_from)


if __name__ == "__main__":
    sys.exit(main())
