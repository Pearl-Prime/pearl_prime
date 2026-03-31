#!/usr/bin/env python3
"""
Run locale translation + validation in parallel batches.

This is the "max agents" entrypoint for localization content generation.
You can set --max-agents to control parallel locale workers.

Architecture: teacher-level sharding — each shard = 1 LLM call = ~20s.
With --max-agents 6 and 120s timeout, that's a 6x safety margin.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
import urllib.request
import urllib.error
import os
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _load_dotenv() -> None:
    """Load .env from repo root if present (no dependency required)."""
    env_path = REPO_ROOT / ".env"
    if not env_path.is_file():
        return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key, value = key.strip(), value.strip()
            if key and key not in os.environ:
                os.environ[key] = value


_load_dotenv()

ALL_LOCALES = [
    # CJK (Route 1: Claude meta-prompt → Qwen)
    "ja-JP", "zh-CN", "zh-TW", "zh-HK", "zh-SG", "ko-KR",
    # European + Latin American (Route 2: Claude direct)
    "es-US", "es-ES", "fr-FR", "de-DE", "it-IT", "hu-HU",
    # Portuguese markets
    "pt-BR", "pt-PT",
    # Russian
    "ru-RU",
]
CORE_LOCALES = ["ja-JP", "zh-CN", "zh-TW", "zh-HK", "zh-SG", "ko-KR"]
ALL_TOPICS = [
    "climate",
    "economy_work",
    "education",
    "inequality",
    "mental_health",
    "partnerships",
    "peace_conflict",
]

# ─── EARLY ABORT THRESHOLD ─────────────────────────────────────────────────
# If this many consecutive shards fail, assume LM Studio is down and abort.
CONSECUTIVE_FAIL_ABORT = 5


def preflight_lm_studio(base_url: str = "http://127.0.0.1:1234") -> bool:
    """Quick connectivity check for local LM Studio. Returns True if reachable."""
    try:
        req = urllib.request.Request(f"{base_url}/v1/models", method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except Exception:
        return False


def preflight_check() -> tuple[bool, str]:
    """
    Check LLM backend availability.
    Cloud mode: DASHSCOPE_API_KEY set → always OK (key validity checked at first real call).
    Local mode: ping LM Studio at 127.0.0.1:1234.
    Returns (ok, message).
    """
    import os
    if os.environ.get("DASHSCOPE_API_KEY", "").strip():
        import os as _os
        model = _os.environ.get("DASHSCOPE_MODEL", "qwen-plus")
        return True, f"[cloud] DASHSCOPE_API_KEY set, model={model}"
    ok = preflight_lm_studio()
    if ok:
        return True, "[local] LM Studio reachable at 127.0.0.1:1234"
    return False, "[local] LM Studio UNREACHABLE at 127.0.0.1:1234"


def run_cmd(cmd: list[str], timeout_sec: int) -> tuple[int, str]:
    start = time.time()
    try:
        p = subprocess.run(
            cmd,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
        )
    except subprocess.TimeoutExpired as e:
        elapsed = time.time() - start
        out = (e.stdout or "") + ("\n" + e.stderr if e.stderr else "")
        out = (
            f"[TIMEOUT] cmd exceeded {timeout_sec}s (elapsed={elapsed:.1f}s)\n"
            f"{' '.join(cmd)}\n{out}"
        )
        return 124, out
    out = (p.stdout or "") + ("\n" + p.stderr if p.stderr else "")
    return p.returncode, out


def _discover_teachers(topic: str) -> list[str]:
    """Read the en-US topic file and return teacher IDs."""
    try:
        import yaml
        path = REPO_ROOT / "pearl_news" / "atoms" / "teacher_quotes_practices" / f"topic_{topic}.yaml"
        if not path.exists():
            return []
        with open(path) as f:
            data = yaml.safe_load(f) or {}
        return list((data.get("teachers") or {}).keys())
    except Exception:
        return []


def worker_teacher_shard(
    locale: str,
    topic: str,
    teacher_id: str,
    do_translate: bool,
    do_validate: bool,
    timeout_sec: int,
    dry_run: bool = False,
) -> tuple[str, int, str]:
    """Single teacher shard = exactly 1 LLM call. Deterministic, fast."""
    logs: list[str] = []
    rc = 0
    shard_id = f"{locale}/{topic}/{teacher_id}"

    if do_translate:
        cmd = [
            sys.executable,
            "scripts/localization/translate_atoms_all_locales.py",
            "--locale", locale,
            "--topic", topic,
            "--teacher", teacher_id,
        ]
        if dry_run:
            cmd.append("--dry-run")
        c, o = run_cmd(cmd, timeout_sec=timeout_sec)
        logs.append(f"[translate:{shard_id}] rc={c}\n{o}")
        rc = max(rc, c)

    # Validate only after all teachers for a topic are done (called separately)
    return shard_id, rc, "\n".join(logs)


def worker_validate(
    locale: str,
    topic: str,
    timeout_sec: int,
) -> tuple[str, int, str]:
    """Validate one locale/topic (no LLM, fast)."""
    shard_id = f"validate:{locale}/{topic}"
    c, o = run_cmd(
        [
            sys.executable,
            "scripts/localization/validate_translations.py",
            "--locale", locale,
            "--topic", topic,
            "--report",
        ],
        timeout_sec=timeout_sec,
    )
    return shard_id, c, f"[{shard_id}] rc={c}\n{o}"


def main() -> int:
    ap = argparse.ArgumentParser(description="Run locale translation/validation with max-agent parallelism")
    ap.add_argument("--max-agents", type=int, default=2, help="Max parallel workers (safe default: 2)")
    ap.add_argument("--locales", nargs="*", default=ALL_LOCALES, help="Locales to process")
    ap.add_argument("--core-locales", action="store_true", help="Run only core production locales (6)")
    ap.add_argument("--topics", nargs="*", default=ALL_TOPICS, help="Topics to process per locale")
    ap.add_argument("--translate-only", action="store_true")
    ap.add_argument("--validate-only", action="store_true")
    ap.add_argument("--log-dir", default="artifacts/localization/batch_runs")
    ap.add_argument("--timeout-sec", type=int, default=120,
                    help="Per-teacher subprocess timeout (seconds). "
                         "Each shard = 1 LLM call (~20s). Safe default: 120s.")
    ap.add_argument("--heartbeat-sec", type=int, default=15, help="Progress heartbeat interval (seconds)")
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Per shard: no LLM call / no writes (translate_atoms_all_locales --dry-run)",
    )
    args = ap.parse_args()

    do_translate = not args.validate_only
    do_validate = not args.translate_only
    locales = CORE_LOCALES if args.core_locales else args.locales
    topics = args.topics

    log_dir = REPO_ROOT / args.log_dir
    log_dir.mkdir(parents=True, exist_ok=True)

    # Build shard list: each shard = 1 locale + 1 topic + 1 teacher = 1 LLM call
    shards: list[tuple[str, str, str]] = []  # (locale, topic, teacher_id)
    for topic in topics:
        teachers = _discover_teachers(topic)
        for loc in locales:
            for tid in teachers:
                shards.append((loc, topic, tid))

    max_agents = max(1, args.max_agents)
    total_shards = len(shards)
    total_validate = len(locales) * len(topics) if do_validate else 0

    print(
        f"locale batches: {total_shards} translate shards + {total_validate} validate shards\n"
        f"  locales={len(locales)} topics={len(topics)} max_agents={max_agents} "
        f"timeout_sec={args.timeout_sec}\n"
        f"  Each shard = 1 teacher = 1 LLM call (~20s). "
        f"Total estimated: ~{total_shards * 20 // max_agents}s"
    )

    # ─── LOCK: local LM Studio only (cloud/Dashscope is parallel-safe) ───────
    sys.path.insert(0, str(REPO_ROOT))
    import os as _os

    use_cloud = bool(_os.environ.get("DASHSCOPE_API_KEY", "").strip())
    lock_ctx = None
    if do_translate and not use_cloud and not args.dry_run:
        from scripts.lm_studio_lock import lm_studio_lock

        lock_shards = total_shards
        lock_ctx = lm_studio_lock(
            "locale-batches",
            shards=lock_shards,
            timeout_sec=args.timeout_sec,
        )
        lock_ctx.__enter__()
    elif do_translate and use_cloud:
        print("[locale-batches] cloud mode (DASHSCOPE_API_KEY) — skipping LM Studio lock")

    # ─── PRE-FLIGHT: verify LLM backend is reachable ───────────────────────
    if do_translate and total_shards > 0 and not args.dry_run:
        print("\n[preflight] Checking LLM backend ...", end=" ", flush=True)
        ok, msg = preflight_check()
        print(msg)
        if not ok:
            print(
                "ERROR: LLM backend is not available.\n"
                "  Cloud mode: set DASHSCOPE_API_KEY environment variable.\n"
                "  Local mode: Open LM Studio, load a model, start the server.\n"
            )
            if lock_ctx:
                lock_ctx.__exit__(None, None, None)
            return 1

    failures = 0
    completed = 0
    consecutive_fails = 0
    started = time.time()
    all_logs: list[str] = []
    aborted = False

    with ThreadPoolExecutor(max_workers=max_agents) as ex:
        # Phase 1: Translation shards (1 LLM call each)
        if do_translate:
            # Submit all to the pool — ThreadPoolExecutor only runs max_agents at a time
            pending: dict = {}
            for loc, topic, tid in shards:
                fut = ex.submit(
                    worker_teacher_shard,
                    loc,
                    topic,
                    tid,
                    True,
                    False,
                    args.timeout_sec,
                    args.dry_run,
                )
                pending[fut] = (f"{loc}/{topic}/{tid}", time.time())

            while pending:
                done, _ = wait(
                    set(pending.keys()),
                    timeout=max(1, args.heartbeat_sec),
                    return_when=FIRST_COMPLETED,
                )
                if not done:
                    now = time.time()
                    # Count truly active (started) vs queued futures
                    active = [
                        (sid, int(now - st))
                        for _, (sid, st) in pending.items()
                        if now - st > 0.5  # started at least 0.5s ago
                    ]
                    # Only show up to max_agents in-flight (the rest are queued)
                    active.sort(key=lambda x: -x[1])  # longest first
                    shown = active[:max_agents]
                    in_prog = ", ".join(f"{sid}:{sec}s" for sid, sec in shown)
                    queued = max(0, len(pending) - max_agents)
                    print(
                        f"[heartbeat] {completed}/{total_shards} done, "
                        f"{min(len(pending), max_agents)} active, {queued} queued, "
                        f"elapsed={int(now - started)}s | {in_prog}"
                    )
                    continue

                for fut in done:
                    sid, _st = pending.pop(fut)
                    shard_id, rc, out = fut.result()
                    completed += 1
                    all_logs.append(out)
                    status = "OK" if rc == 0 else f"FAIL(rc={rc})"
                    print(f"  [{completed}/{total_shards}] {shard_id} {status}")
                    if rc != 0:
                        failures += 1
                        consecutive_fails += 1
                        # Surface first few lines of error output
                        err_lines = [l for l in out.strip().split("\n") if l.strip()][-3:]
                        if err_lines:
                            print(f"    └─ {' | '.join(err_lines)}")
                        # Early abort if LM Studio appears down
                        if consecutive_fails >= CONSECUTIVE_FAIL_ABORT:
                            print(
                                f"\n[ABORT] {consecutive_fails} consecutive failures — "
                                f"LM Studio may be down. Cancelling remaining shards."
                            )
                            # Cancel queued futures (already-running ones will finish/timeout)
                            for qfut in list(pending.keys()):
                                qfut.cancel()
                            pending.clear()
                            aborted = True
                            break
                    else:
                        consecutive_fails = 0  # reset on success

                if aborted:
                    break

        # Phase 2: Validation (no LLM, fast)
        if do_validate and not aborted:
            print(f"\n--- Validation phase: {total_validate} locale/topic pairs ---")
            pending_val: dict = {}
            for loc in locales:
                for topic in topics:
                    fut = ex.submit(worker_validate, loc, topic, args.timeout_sec)
                    pending_val[fut] = (f"validate:{loc}/{topic}", time.time())

            val_done = 0
            while pending_val:
                done, _ = wait(
                    set(pending_val.keys()),
                    timeout=max(1, args.heartbeat_sec),
                    return_when=FIRST_COMPLETED,
                )
                for fut in (done or []):
                    sid, _st = pending_val.pop(fut)
                    shard_id, rc, out = fut.result()
                    val_done += 1
                    all_logs.append(out)
                    status = "OK" if rc == 0 else f"FAIL(rc={rc})"
                    print(f"  [{val_done}/{total_validate}] {shard_id} {status}")
                    if rc != 0:
                        failures += 1

    if lock_ctx:
        lock_ctx.__exit__(None, None, None)

    # Write combined log
    elapsed = time.time() - started
    (log_dir / "combined.log").write_text("\n".join(all_logs), encoding="utf-8")
    status_msg = "ABORTED" if aborted else ("PASS" if failures == 0 else f"DONE ({failures} failures)")
    print(f"\n{status_msg}: shards={total_shards} validate={total_validate} "
          f"failures={failures} elapsed={int(elapsed)}s")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
