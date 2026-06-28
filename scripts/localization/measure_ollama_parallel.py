#!/usr/bin/env python3
"""Measure Ollama num_parallel throughput for CJK atom translation on Pearl Star.

Runs a small fixed sample of en atoms through translate_atoms_to_locale.py at
workers=1,2,3,4 and reports atoms/min + OOM observations. SSH to pearl_star.

Usage:
  python3 scripts/localization/measure_ollama_parallel.py
  python3 scripts/localization/measure_ollama_parallel.py --workers 1 2 4
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SSH_HOST = "pearl_star"
PS_REPO = "~/phoenix_omega"

# Small fixed sample — midlife_women hooks (short, representative)
SAMPLE_EN_PATHS = [
    "atoms/midlife_women/anxiety/HOOK/CANONICAL.txt",
    "atoms/midlife_women/burnout/HOOK/CANONICAL.txt",
    "atoms/midlife_women/grief/HOOK/CANONICAL.txt",
    "atoms/midlife_women/courage/HOOK/CANONICAL.txt",
    "atoms/midlife_women/depression/HOOK/CANONICAL.txt",
]


def _ssh_run(script: str, *, timeout: int = 900) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", SSH_HOST, script],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return proc.returncode, proc.stdout or "", proc.stderr or ""


def measure_workers(workers: int, *, locale: str = "ja-JP", model: str = "qwen2.5:14b") -> dict:
    paths_body = "\n".join(SAMPLE_EN_PATHS)
    remote_paths = f"/tmp/ollama_bench_w{workers}.txt"
    subprocess.run(
        ["ssh", SSH_HOST, f"printf '%s\\n' {paths_body.replace(chr(10), ' ')} > {remote_paths}"],
        check=True,
        timeout=30,
    )
    # Write properly via heredoc
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tf:
        tf.write(paths_body + "\n")
        local = tf.name
    subprocess.run(["scp", "-q", local, f"{SSH_HOST}:{remote_paths}"], check=True, timeout=30)

    cmd = (
        f"cd {PS_REPO} && export PYTHONPATH=. && "
        f"pscli gpu-acquire cjk --note 'ollama_parallel_bench' 2>/dev/null; "
        f"python3 scripts/localization/translate_atoms_to_locale.py "
        f"--locale {locale} --paths-file {remote_paths} --force --workers {workers} "
        f"--model {model} --ollama-url http://127.0.0.1:11434 --persona-atoms-only"
    )
    t0 = time.monotonic()
    rc, out, err = _ssh_run(cmd, timeout=900)
    elapsed = time.monotonic() - t0

    ok_count = len(re.findall(r" OK ", out))
    fail_count = len(re.findall(r" FAILED", out))
    oom = "OOM" in out + err or "out of memory" in (out + err).lower()

    rate = ok_count / max(elapsed / 60.0, 0.01)
    return {
        "workers": workers,
        "elapsed_s": round(elapsed, 1),
        "ok": ok_count,
        "failed": fail_count,
        "atoms_per_min": round(rate, 2),
        "oom": oom,
        "returncode": rc,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workers", type=int, nargs="+", default=[1, 2, 3, 4])
    ap.add_argument("--locale", default="ja-JP")
    args = ap.parse_args(argv)

    print(f"Ollama parallel benchmark on {SSH_HOST} ({len(SAMPLE_EN_PATHS)} sample atoms)")
    print(f"{'workers':>8} {'ok':>5} {'fail':>5} {'sec':>8} {'atoms/min':>10} {'oom':>5}")
    best = None
    for w in args.workers:
        r = measure_workers(w, locale=args.locale)
        print(
            f"{r['workers']:>8} {r['ok']:>5} {r['failed']:>5} {r['elapsed_s']:>8.1f} "
            f"{r['atoms_per_min']:>10.2f} {str(r['oom']):>5}"
        )
        if not r["oom"] and r["ok"] > 0:
            if best is None or r["atoms_per_min"] > best["atoms_per_min"]:
                best = r

    if best:
        remaining = 7900  # ko + zh-CN + ja residual approx
        eta_h = remaining / max(best["atoms_per_min"], 0.1) / 60.0
        print(f"\nBest non-OOM: workers={best['workers']} @ {best['atoms_per_min']:.2f} atoms/min")
        print(f"Rough ETA for ~7,900 atoms (serial GPU): {eta_h:.1f} h ({eta_h/24:.1f} days)")
    else:
        print("\nNo successful benchmark run — check Ollama on Pearl Star.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
