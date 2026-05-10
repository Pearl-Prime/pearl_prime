#!/usr/bin/env python3
"""Dual-path parallel image batch runner (Pearl Star + RunComfy).

Plan load, locale-first ordering, dry-run dispatch, RunComfy spend cooldown,
optional **activation** (``--activate`` / ``--live``) for real Pearl Star
(SSH + ComfyUI ``/prompt``) and RunComfy (``submit_inference`` overrides path).

Project: PRJ-DUAL-PATH-IMAGE-RENDER-V1 (IMG-RENDER-DUAL-PATH-V1-01).
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import io
import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]

# Default artifact paths (tests may monkeypatch these module attributes).
RUNCOMFY_SPEND_TSV = REPO_ROOT / "artifacts" / "qa" / "runcomfy_monthly_spend.tsv"
DISPATCH_LOG_TSV = REPO_ROOT / "artifacts" / "qa" / "image_batch_dispatch_log.tsv"

_COOLDOWN_USD = 10.0


@dataclass
class PearlStarModelState:
    """Pearl Star ComfyUI model presence snapshot (from a read-only SSH probe)."""

    flux_schnell_present: bool
    animagine_xl_present: bool
    qwen_unified_ckpt_present: bool
    qwen_transformer_shard_count: int
    probe_stdout: str


def probe_pearl_star_models(ssh_host: str = "pearl_star", *, timeout_s: int = 90) -> PearlStarModelState | None:
    """SSH to Pearl Star and list checkpoints / diffusion_models / transformer shards."""
    remote = (
        "echo __CK__; ls ~/phoenix_server/ComfyUI/models/checkpoints/*.safetensors 2>/dev/null || true; "
        "echo __DM__; ls ~/phoenix_server/ComfyUI/models/diffusion_models/*.safetensors 2>/dev/null || true; "
        "echo __TR__; ls ~/phoenix_server/ComfyUI/models/transformer/diffusion_pytorch_model-*.safetensors "
        "2>/dev/null | wc -l"
    )
    try:
        r = subprocess.run(
            ["ssh", "-o", "BatchMode=yes", ssh_host, remote],
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if r.returncode != 0:
        return None
    text = r.stdout
    low = text.lower()
    flux = "flux1-schnell-fp8" in low
    animagine = "animagine_xl_4_0.safetensors" in low or "animagine-xl-4.0" in low
    qwen_ckpt = "qwen_image_2.0" in low
    shards = 0
    if "__tr__" in low:
        tail = text.split("__TR__", 1)[-1]
        for line in tail.splitlines():
            line = line.strip()
            if line.isdigit():
                shards = int(line)
                break
    return PearlStarModelState(
        flux_schnell_present=flux,
        animagine_xl_present=animagine,
        qwen_unified_ckpt_present=qwen_ckpt,
        qwen_transformer_shard_count=shards,
        probe_stdout=text.strip()[:8000],
    )


def resolve_dispatch_path(
    batch: Mapping[str, Any],
    state: PearlStarModelState | None,
) -> str:
    """IMG-RENDER-DUAL-PATH routing: ``flux_*`` Pearl primary; ``animagine_*`` if ckpt; ``qwen_*`` if unified ckpt."""
    raw = str(batch.get("dispatch_path", "auto")).strip().lower()
    if raw not in ("", "auto"):
        return "runcomfy" if raw in ("run_comfy",) else raw

    if state is None:
        return "runcomfy"

    wf = str(
        batch.get("workflow_template") or batch.get("workflow_path") or "flux_txt2img_manga.json",
    ).strip().lower()
    if wf.startswith("flux_"):
        return "pearl_star" if state.flux_schnell_present else "runcomfy"
    if wf.startswith("animagine_"):
        return "pearl_star" if state.animagine_xl_present else "runcomfy"
    if wf.startswith("qwen_image_"):
        return "pearl_star" if state.qwen_unified_ckpt_present else "runcomfy"
    return "pearl_star"


def apply_dispatch_routing(batch: Mapping[str, Any], state: PearlStarModelState | None) -> dict[str, Any]:
    out = dict(batch)
    out["dispatch_path"] = resolve_dispatch_path(batch, state)
    return out


def ensure_pearl_comfyui(ssh_host: str = "pearl_star", *, wait_s: int = 30) -> None:
    """If ComfyUI is not answering on 8188, start ``main.py`` remotely (nohup) and wait."""
    ping = (
        "curl -s -o /dev/null -w '%{http_code}' "
        "http://127.0.0.1:8188/system_stats || true"
    )
    r = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", ssh_host, ping],
        capture_output=True,
        text=True,
        timeout=40,
    )
    if (r.stdout or "").strip() == "200":
        return
    start = (
        "cd ~/phoenix_server/ComfyUI && "
        "nohup python3 main.py --listen 0.0.0.0 --port 8188 > /tmp/comfyui.log 2>&1 &"
    )
    subprocess.run(
        ["ssh", "-o", "BatchMode=yes", ssh_host, start],
        check=False,
        timeout=30,
    )
    time.sleep(wait_s)
    r2 = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", ssh_host, ping],
        capture_output=True,
        text=True,
        timeout=40,
    )
    if (r2.stdout or "").strip() != "200":
        raise RuntimeError(
            "Pearl Star ComfyUI did not become ready on :8188 after remote start attempt "
            f"(http_code={(r2.stdout or '').strip()!r}).",
        )


# Q-IMG-1 locale-first: highest priority first within the tuple sort key.
_LOCALE_RANK: dict[str, int] = {
    "ja-jp": 0,
    "zh-cn": 1,
    "zh-tw": 2,
    "ko-kr": 3,
    "yue-hk": 4,
    "en-us": 100,
}


def _load_dispatcher_module(file_stem: str) -> Any:
    """Load ``dispatchers/<file_stem>.py`` without a package ``__init__``."""
    path = Path(__file__).resolve().parent / "dispatchers" / f"{file_stem}.py"
    qualname = f"scripts.image_generation.dispatchers.{file_stem}"
    spec = importlib.util.spec_from_file_location(qualname, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load dispatcher module from {path}")
    module = importlib.util.module_from_spec(spec)
    # Python 3.9 dataclasses inspect sys.modules during class creation.
    sys.modules[qualname] = module
    spec.loader.exec_module(module)
    return module


_pearl_mod: Any | None = None
_runcomfy_mod: Any | None = None


def _pearl() -> Any:
    global _pearl_mod
    if _pearl_mod is None:
        _pearl_mod = _load_dispatcher_module("pearl_star_dispatcher")
    return _pearl_mod


def _runcomfy() -> Any:
    global _runcomfy_mod
    if _runcomfy_mod is None:
        _runcomfy_mod = _load_dispatcher_module("runcomfy_dispatcher")
    return _runcomfy_mod


_BATCH_BLOCK = re.compile(
    r"```batch\s*\n(.*?)```",
    re.IGNORECASE | re.DOTALL,
)


def load_plan(path: str | Path) -> list[dict[str, Any]]:
    """Parse ``parallel_image_generation_plan`` markdown into batch dicts.

    Each fenced `` ```batch`` `` block contains ``key: value`` lines. Arrays
    may use comma-separated values on one line. Booleans: ``true`` / ``false``.
    """
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    batches: list[dict[str, Any]] = []
    for m in _BATCH_BLOCK.finditer(text):
        block = m.group(1)
        batch: dict[str, Any] = {}
        for raw_line in block.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            low = value.lower()
            if low in ("true", "false"):
                batch[key] = low == "true"
            else:
                # ints
                if key in ("sequence", "panel_count") and value.isdigit():
                    batch[key] = int(value)
                elif "," in value:
                    batch[key] = [v.strip() for v in value.split(",") if v.strip()]
                else:
                    try:
                        if "." in value:
                            batch[key] = float(value)
                        elif value.isdigit():
                            batch[key] = int(value)
                        else:
                            batch[key] = value
                    except ValueError:
                        batch[key] = value
        if batch:
            batches.append(batch)
    return batches


def _locale_sort_key(batch: Mapping[str, Any]) -> tuple[int, int, str, str]:
    loc = str(batch.get("locale", "en-US")).strip().lower() or "en-us"
    rank = _LOCALE_RANK.get(loc, 50 if loc != "en-us" else 100)
    seq = batch.get("sequence")
    try:
        seq_i = int(seq)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        seq_i = 10**9
    batch_id = str(batch.get("batch_id", ""))
    return (rank, seq_i, loc, batch_id)


def priority_sort(batches: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Locale-first ordering (Q-IMG-1): CJK6 family first, ``en-US`` last."""
    enriched = [dict(b) for b in batches]
    enriched.sort(key=_locale_sort_key)
    return enriched


def dispatch(batch: Mapping[str, Any], *, dry_run: bool = True, **kwargs: Any) -> dict[str, Any]:
    """Route ``batch`` to Pearl Star or RunComfy.

    Optional ``activation_output_dir`` / ``ssh_host`` are forwarded for live
    activation (see ``pearl_star_dispatcher`` / ``runcomfy_dispatcher``).
    """
    path = str(batch.get("dispatch_path", "")).strip().lower()
    if path == "pearl_star":
        return _pearl().dispatch(batch, dry_run=dry_run, **kwargs)
    if path in ("runcomfy", "run_comfy"):
        return _runcomfy().dispatch(batch, dry_run=dry_run, **kwargs)
    raise ValueError(f"Unknown dispatch_path: {batch.get('dispatch_path')!r}")


def runcomfy_cost_check(
    *,
    spend_path: Path | None = None,
    cooldown_usd: float = _COOLDOWN_USD,
) -> dict[str, Any]:
    """Sum month-to-date RunComfy spend from TSV; cooldown when over cap."""
    path = spend_path or RUNCOMFY_SPEND_TSV
    spend = 0.0
    if path.is_file():
        spend = _parse_spend_tsv(path.read_text(encoding="utf-8"))
    cooldown = spend >= cooldown_usd
    return {
        "spend_to_date_usd": round(spend, 4),
        "cooldown": cooldown,
        "cooldown_threshold_usd": cooldown_usd,
        "source_path": str(path) if path.is_file() else None,
    }


def _parse_spend_tsv(text: str) -> float:
    """Sum numeric spend column from a simple TSV."""
    total = 0.0
    buf = io.StringIO(text)
    reader = csv.reader(buf, delimiter="\t")
    rows = list(reader)
    if not rows:
        return 0.0
    start = 0
    header = [c.strip().lower() for c in rows[0]]
    if any("usd" in h or "spend" in h or "amount" in h for h in header):
        start = 1
        if "spend_usd" in header:
            idx = header.index("spend_usd")
        elif "amount_usd" in header:
            idx = header.index("amount_usd")
        else:
            idx = len(header) - 1
        # Spec §4: cumulative_month_spend_usd is vendor running total — do not sum rows.
        if "cumulative_month_spend_usd" in header:
            idx = header.index("cumulative_month_spend_usd")
            last_val = 0.0
            for row in rows[start:]:
                if not row or idx >= len(row):
                    continue
                cell = row[idx].strip().replace("$", "")
                if not cell:
                    continue
                try:
                    last_val = float(cell)
                except ValueError:
                    continue
            return last_val
        for row in rows[start:]:
            if not row or idx >= len(row):
                continue
            cell = row[idx].strip().replace("$", "")
            if not cell:
                continue
            try:
                total += float(cell)
            except ValueError:
                continue
        return total
    # No header: treat last column as USD if possible, else first column.
    for row in rows:
        if not row:
            continue
        cell = row[-1].strip().replace("$", "")
        try:
            total += float(cell)
        except ValueError:
            try:
                total += float(row[0].strip().replace("$", ""))
            except (ValueError, IndexError):
                continue
    return total


def log_dispatch(entry: Mapping[str, Any]) -> None:
    """Append a dispatch record to ``artifacts/qa/image_batch_dispatch_log.tsv``."""
    log_path = DISPATCH_LOG_TSV
    log_path.parent.mkdir(parents=True, exist_ok=True)
    is_new = not log_path.is_file()
    fieldnames = [
        "ts_utc",
        "batch_id",
        "dispatch_path",
        "dry_run",
        "status",
        "notes",
        "payload_json",
    ]
    row = {
        "ts_utc": datetime.now(timezone.utc).isoformat(),
        "batch_id": str(entry.get("batch_id", "")),
        "dispatch_path": str(entry.get("dispatch_path", "")),
        "dry_run": str(bool(entry.get("dry_run", False))).lower(),
        "status": str(entry.get("status", "")),
        "notes": str(entry.get("notes", "")),
        "payload_json": json.dumps(dict(entry.get("payload", {})), sort_keys=True),
    }
    with log_path.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        if is_new:
            writer.writeheader()
        writer.writerow(row)


def _should_skip_runcomfy(cost: Mapping[str, Any]) -> bool:
    return bool(cost.get("cooldown"))


def run_batches(
    batches: Sequence[Mapping[str, Any]],
    *,
    dry_run: bool = True,
    cost_check: Callable[[], dict[str, Any]] | None = None,
    skip_runcomfy_on_cooldown: bool = True,
) -> list[dict[str, Any]]:
    """Ordered execution with optional RunComfy cooldown skip."""
    cost_fn = cost_check or runcomfy_cost_check
    cost = cost_fn()
    ordered = priority_sort(batches)
    results: list[dict[str, Any]] = []
    for batch in ordered:
        path = str(batch.get("dispatch_path", "")).strip().lower()
        if (
            skip_runcomfy_on_cooldown
            and path in ("runcomfy", "run_comfy")
            and _should_skip_runcomfy(cost)
        ):
            results.append(
                {
                    "batch_id": batch.get("batch_id"),
                    "dispatch_path": "runcomfy",
                    "skipped": True,
                    "reason": "runcomfy_cost_cooldown",
                    "cost": dict(cost),
                }
            )
            continue
        results.append(dispatch(batch, dry_run=dry_run))
    return results


def run_live_activation(
    batches: Sequence[Mapping[str, Any]],
    *,
    output_root: Path,
    ssh_host: str = "pearl_star",
    skip_comfy_ping: bool = False,
    max_batches: int | None = None,
    write_dispatch_log: bool = False,
    cost_check: Callable[[], dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Locale-first live run with ``dispatch_path:auto`` resolved from Pearl Star probe."""
    if not skip_comfy_ping:
        ensure_pearl_comfyui(ssh_host)
    state = probe_pearl_star_models(ssh_host)
    routed = [apply_dispatch_routing(dict(b), state) for b in batches]
    ordered = priority_sort(routed)
    if max_batches is not None:
        ordered = ordered[: max(0, max_batches)]
    cost_fn = cost_check or runcomfy_cost_check
    results: list[dict[str, Any]] = []
    for batch in ordered:
        path = str(batch.get("dispatch_path", "")).strip().lower()
        cost = cost_fn()
        if path in ("runcomfy", "run_comfy") and _should_skip_runcomfy(cost):
            row = {
                "batch_id": batch.get("batch_id"),
                "dispatch_path": "runcomfy",
                "skipped": True,
                "reason": "runcomfy_cost_cooldown",
                "cost": dict(cost),
            }
            results.append(row)
            if write_dispatch_log:
                log_dispatch(
                    {
                        "batch_id": batch.get("batch_id"),
                        "dispatch_path": "runcomfy",
                        "dry_run": False,
                        "status": "SUPPRESSED_COOLDOWN",
                        "notes": "tsv_or_billing_cap",
                        "payload": row,
                    },
                )
            continue
        kwargs: dict[str, Any] = {"activation_output_dir": output_root}
        if path == "pearl_star":
            kwargs["ssh_host"] = ssh_host
        res = dispatch(batch, dry_run=False, **kwargs)
        res["batch_id"] = batch.get("batch_id")
        if state is not None:
            res["model_probe"] = {
                "flux_schnell_present": state.flux_schnell_present,
                "animagine_xl_present": state.animagine_xl_present,
                "qwen_unified_ckpt_present": state.qwen_unified_ckpt_present,
                "qwen_transformer_shard_count": state.qwen_transformer_shard_count,
            }
        if write_dispatch_log:
            log_dispatch(
                {
                    "batch_id": batch.get("batch_id"),
                    "dispatch_path": path,
                    "dry_run": False,
                    "status": str(res.get("status", "")),
                    "notes": str(res.get("notes", "")),
                    "payload": {k: v for k, v in res.items() if k != "model_probe"},
                },
            )
        results.append(res)
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--plan",
        required=True,
        type=Path,
        help="Path to markdown containing ```batch fenced blocks",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Explicit safe mode (default when --activate/--live are not set)",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Alias of --activate (live dispatch)",
    )
    parser.add_argument(
        "--activate",
        action="store_true",
        help="Live dispatch to Pearl Star and/or RunComfy (respects routing + cost cap)",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=None,
        help="Directory for activation PNG outputs (default: artifacts/manga/activation_smoke_2026-05-10)",
    )
    parser.add_argument(
        "--max-batches",
        type=int,
        default=None,
        help="Process only the first N batches after locale sort (smoke)",
    )
    parser.add_argument(
        "--ssh-host",
        default="pearl_star",
        help="SSH host alias for Pearl Star (default: pearl_star)",
    )
    parser.add_argument(
        "--skip-comfy-ping",
        action="store_true",
        help="Do not SSH-start ComfyUI if :8188 is down (for tests)",
    )
    parser.add_argument(
        "--write-dispatch-log",
        action="store_true",
        help="Append rows to artifacts/qa/image_batch_dispatch_log.tsv during activation",
    )
    args = parser.parse_args(argv)
    if args.dry_run and (args.live or args.activate):
        parser.error("--dry-run is mutually exclusive with --live / --activate")
    activate = bool(args.live or args.activate)
    dry_run = not activate
    plan_path = args.plan
    if not plan_path.is_file():
        print(f"error: plan file not found: {plan_path}", file=sys.stderr)
        return 2
    batches = load_plan(plan_path)
    cost = runcomfy_cost_check()
    print(json.dumps({"cost": cost, "batch_count": len(batches)}, indent=2))
    if activate:
        out = args.output_root or (
            REPO_ROOT / "artifacts" / "manga" / "activation_smoke_2026-05-10"
        )
        out.mkdir(parents=True, exist_ok=True)
        probe = probe_pearl_star_models(args.ssh_host)
        print(json.dumps({"model_probe": probe.__dict__ if probe else None}, indent=2, default=str))
        for res in run_live_activation(
            batches,
            output_root=out.resolve(),
            ssh_host=args.ssh_host,
            skip_comfy_ping=args.skip_comfy_ping,
            max_batches=args.max_batches,
            write_dispatch_log=args.write_dispatch_log,
        ):
            print(json.dumps(res, indent=2, default=str))
        return 0
    for res in run_batches(batches, dry_run=dry_run):
        print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
