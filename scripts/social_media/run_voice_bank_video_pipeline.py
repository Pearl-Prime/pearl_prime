#!/usr/bin/env python3
"""Robust social short pipeline: preflight → prefetch → assemble → render → verify.

Fail-closed on missing voice-bank MP3s. One job at a time with line-buffered logs,
flock, resume/skip-done, and append-only receipts.

Usage:
  # PRIMARY calendar (broll × 3 pilots), prefetch from R2 if needed
  PYTHONUNBUFFERED=1 python3 scripts/social_media/run_voice_bank_video_pipeline.py \\
    --styles broll --topics anxiety,burnout,overthinking --allow-r2 --resume

  # Dry preflight + coverage only
  python3 scripts/social_media/run_voice_bank_video_pipeline.py --preflight-only --allow-r2
"""
from __future__ import annotations

import argparse
import fcntl
import json
import os
import subprocess
import sys
import time
import traceback
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts/social"))

from evergreen_shortform_caption_pack import DEFAULT_VOICE_BANK, build_pack  # noqa: E402
from scripts.social_media.assemble_reel_from_voice_bank import (  # noqa: E402
    ReelAssembleError,
    assemble_reel_package,
)
from scripts.social_media.voice_bank_lookup import (  # noqa: E402
    VoiceBankError,
    VoiceBankIndex,
    load_index,
)
import render_pilot_variant_fixes as pilot  # noqa: E402

DEFAULT_OUT = (
    REPO
    / "artifacts/qa/social_finish_20260718/lane03_research_complete/variants"
    / "voice_bank_pipeline"
)
STYLES = ("broll", "kinetic", "metaphor")
# Full evergreen topic set (PRIMARY calendar still defaults to 3 pilots in CLI).
from scripts.social.evergreen_shortform_caption_pack import TOPICS as _EVERGREEN_TOPICS  # noqa: E402

TOPICS = tuple(_EVERGREEN_TOPICS)
MIN_MP4_BYTES = 500_000


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(msg: str, *, err: bool = False) -> None:
    stream = sys.stderr if err else sys.stdout
    print(f"[{utc_now()}] {msg}", file=stream, flush=True)


def which_bin(candidates: tuple[str, ...], fallback: str) -> str:
    for c in candidates:
        if Path(c).is_file():
            return c
    return fallback


FFMPEG = which_bin(("/opt/homebrew/bin/ffmpeg", "/usr/local/bin/ffmpeg"), "ffmpeg")
FFPROBE = which_bin(("/opt/homebrew/bin/ffprobe", "/usr/local/bin/ffprobe"), "ffprobe")


@contextmanager
def pipeline_lock(lock_path: Path) -> Iterator[None]:
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    fh = open(lock_path, "a+", encoding="utf-8")
    try:
        try:
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as e:
            raise SystemExit(
                f"BLOCKED: pipeline already running (lock={lock_path}). "
                "Wait or remove stale lock if the holder pid is dead."
            ) from e
        fh.seek(0)
        fh.truncate()
        fh.write(f"pid={os.getpid()}\nstarted={utc_now()}\n")
        fh.flush()
        yield
    finally:
        try:
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
        finally:
            fh.close()


def parse_csv(raw: str, allowed: tuple[str, ...]) -> list[str]:
    if raw.strip().lower() == "all":
        return list(allowed)
    items = [x.strip() for x in raw.split(",") if x.strip()]
    bad = [x for x in items if x not in allowed]
    if bad:
        raise SystemExit(f"unknown value(s) {bad}; allowed={list(allowed)}")
    return items or list(allowed)


def job_key(style: str, topic: str) -> str:
    return f"{style}:{topic}"


def example_id_for(topic: str) -> str:
    for eid, t in pilot.PILOTS.items():
        if t == topic:
            return eid
    raise KeyError(topic)


def final_mp4(style: str, topic: str) -> Path:
    eid = example_id_for(topic)
    return pilot.VAR / pilot.STYLE_DIR[style] / "final" / f"{eid}.mp4"


def probe_duration(path: Path) -> float:
    r = subprocess.run(
        [
            FFPROBE,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(r.stdout.strip())


def probe_audio_codec(path: Path) -> str | None:
    r = subprocess.run(
        [
            FFPROBE,
            "-v",
            "error",
            "-select_streams",
            "a:0",
            "-show_entries",
            "stream=codec_name",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        return None
    codec = (r.stdout or "").strip()
    return codec or None


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")


def load_ok_keys(*receipt_paths: Path) -> set[str]:
    ok: set[str] = set()
    for receipts_path in receipt_paths:
        if not receipts_path.is_file():
            continue
        for line in receipts_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            audio_ok = row.get("audio") == "social_voice_bank"
            status_ok = row.get("status") in (None, "ok")  # legacy rows omit status
            if audio_ok and status_ok and row.get("style") and row.get("topic"):
                ok.add(job_key(str(row["style"]), str(row["topic"])))
    return ok


def mp4_resume_eligible(mp4: Path, package: dict[str, Any] | None = None) -> bool:
    """True when on-disk MP4 already looks like a voice-bank render."""
    if not mp4.is_file() or mp4.stat().st_size < MIN_MP4_BYTES:
        return False
    if probe_audio_codec(mp4) not in ("aac", "mp3"):
        return False
    if package is not None:
        try:
            dur = probe_duration(mp4)
            expected = float(package.get("total_duration_s") or 0)
            if expected and abs(dur - expected) > 2.5:
                return False
        except Exception:
            return False
    return True


def preflight(
    *,
    styles: list[str],
    topics: list[str],
    manifest: Path,
    allow_r2: bool,
) -> list[str]:
    errors: list[str] = []
    for bin_name, path in (("ffmpeg", FFMPEG), ("ffprobe", FFPROBE)):
        r = subprocess.run([path, "-version"], capture_output=True, text=True)
        if r.returncode != 0:
            errors.append(f"{bin_name} not runnable: {path}")
    if not manifest.is_file():
        errors.append(f"manifest missing: {manifest}")
    from scripts.social_media.stock_plates_for_topic import plates_for_topic

    for topic in topics:
        # Prefer topic-keyed stock sampler; fall back to pilot.PLATES if present
        try:
            sampled = plates_for_topic(topic, n=5)
            if len(sampled) < 5:
                errors.append(f"need 5 plates for {topic}; got {len(sampled)}")
        except FileNotFoundError as e:
            plates = pilot.PLATES.get(topic) or {}
            master = plates.get("master")
            if not master or not Path(master).is_file():
                errors.append(f"missing plates for {topic}: {e}")
    if allow_r2:
        for env in ("R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY"):
            if not (os.environ.get(env) or "").strip():
                # endpoint can be derived; keys cannot
                errors.append(f"allow-r2 set but {env} missing in env")
    return errors


def prefetch_mp3s(
    bank: VoiceBankIndex,
    *,
    styles: list[str],
    topics: list[str],
    favor_gender: str | None,
) -> dict[str, Any]:
    """Download/resolve every beat MP3 before any ffmpeg work."""
    needed: list[dict[str, str]] = []
    missing: list[str] = []
    seen: set[str] = set()
    for topic in topics:
        for style in styles:
            pack = build_pack(topic, style=style, voice_bank=bank.manifest_path)
            for beat in pack.get("beats") or []:
                aid = beat.get("atom_id") or ""
                if not aid or aid in seen:
                    continue
                seen.add(aid)
                row = bank.get_row(aid)
                if not row:
                    missing.append(f"{aid}: not in manifest")
                    continue
                if (row.get("status") or "") != "ok":
                    missing.append(f"{aid}: status={row.get('status')!r}")
                    continue
                needed.append({"atom_id": aid, "topic": topic, "style": style})
                try:
                    path = bank.ensure_local_mp3(row)
                    try:
                        shown = path.relative_to(REPO)
                    except ValueError:
                        shown = path
                    log(f"  prefetch ok {aid} → {shown}")
                except VoiceBankError as e:
                    missing.append(f"{aid}: {e}")
                except Exception as e:  # noqa: BLE001 — surface R2/boto errors
                    missing.append(f"{aid}: {type(e).__name__}: {e}")
    # Also dry-assemble to catch gender mismatch early
    for topic in topics:
        for style in styles:
            pack = build_pack(topic, style=style, voice_bank=bank.manifest_path)
            try:
                assemble_reel_package(pack, bank=bank, favor_gender=favor_gender)
            except ReelAssembleError as e:
                missing.append(f"assemble {topic}/{style}: {e}")
    return {
        "atoms_needed": len(needed),
        "atoms_unique": len(seen),
        "missing": missing,
        "ok": not missing,
    }


def verify_mp4(mp4: Path, package: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    if not mp4.is_file():
        return [f"missing mp4: {mp4}"]
    if mp4.stat().st_size < MIN_MP4_BYTES:
        errs.append(f"mp4 too small: {mp4.stat().st_size} bytes")
    codec = probe_audio_codec(mp4)
    if codec is None:
        errs.append("no audio stream")
    elif codec not in ("aac", "mp3"):
        errs.append(f"unexpected audio codec={codec!r}")
    try:
        dur = probe_duration(mp4)
    except Exception as e:  # noqa: BLE001
        errs.append(f"ffprobe duration failed: {e}")
        return errs
    expected = float(package.get("total_duration_s") or 0)
    if expected and abs(dur - expected) > 2.5:
        errs.append(f"duration drift mp4={dur:.2f}s package={expected:.2f}s")
    return errs


def render_one(
    *,
    style: str,
    topic: str,
    bank: VoiceBankIndex,
    favor_gender: str | None,
    out_dir: Path,
) -> dict[str, Any]:
    eid = example_id_for(topic)
    pack = build_pack(topic, style=style, voice_bank=bank.manifest_path)
    package = assemble_reel_package(pack, bank=bank, favor_gender=favor_gender)
    package["_use_voice_bank"] = True

    pkg_path = out_dir / "reel_packages" / f"{topic}_{style}.json"
    pkg_path.parent.mkdir(parents=True, exist_ok=True)
    clean = {k: v for k, v in package.items() if not str(k).startswith("_")}
    pkg_path.write_text(json.dumps(clean, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Mirror into variants dir for operator inspection
    (pilot.VAR / f"_reel_package_{topic}_{style}.json").write_text(
        json.dumps(clean, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    t0 = time.time()
    mp4 = pilot.RENDERERS[style](topic, eid, package)
    verify_errs = verify_mp4(mp4, package)
    if verify_errs:
        raise RuntimeError("verify failed: " + "; ".join(verify_errs))

    row = {
        "status": "ok",
        "example_id": eid,
        "topic": topic,
        "style": style,
        "path": str(mp4.relative_to(REPO)),
        "duration_s": round(probe_duration(mp4), 2),
        "bytes": mp4.stat().st_size,
        "primary_calendar_style": style == "broll",
        "caption_source": "voice_bank_speakable",
        "audio": "social_voice_bank",
        "atom_ids": [b["atom_id"] for b in package["beats"]],
        "voice_ids": [b.get("voice_id") for b in package["beats"]],
        "reel_package": str(pkg_path.relative_to(REPO)),
        "elapsed_s": round(time.time() - t0, 1),
        "ts": utc_now(),
        "acceptance_layer": "system working — voice-bank video pipeline",
    }
    return row


def main() -> int:
    # Line-buffer even when piped
    try:
        sys.stdout.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
        sys.stderr.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
    except Exception:
        pass

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--styles", default="broll", help="comma: broll,kinetic,metaphor")
    ap.add_argument(
        "--topics",
        default="anxiety,burnout,overthinking",
        help="comma: anxiety,burnout,overthinking",
    )
    ap.add_argument("--manifest", type=Path, default=DEFAULT_VOICE_BANK)
    ap.add_argument("--allow-r2", action="store_true", help="prefetch missing MP3s from R2")
    ap.add_argument(
        "--favor-gender",
        default=None,
        choices=("male", "female"),
    )
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--resume", action="store_true", help="skip jobs with ok receipt + mp4")
    ap.add_argument(
        "--continue-on-error",
        action="store_true",
        help="finish remaining jobs after a failure (default: stop)",
    )
    ap.add_argument("--preflight-only", action="store_true")
    ap.add_argument("--prefetch-only", action="store_true")
    ap.add_argument("--force", action="store_true", help="re-render even if resume would skip")
    args = ap.parse_args()

    styles = parse_csv(args.styles, STYLES)
    topics = parse_csv(args.topics, TOPICS)
    out_dir: Path = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    lock_path = out_dir / "pipeline.lock"
    receipts_path = out_dir / "PIPELINE_RECEIPTS.jsonl"
    closeout_path = out_dir / "PIPELINE_CLOSEOUT.json"
    log_path = out_dir / "PIPELINE.log"

    class Tee:
        def __init__(self, *streams):
            self.streams = streams

        def write(self, data: str) -> int:
            for s in self.streams:
                s.write(data)
                s.flush()
            return len(data)

        def flush(self) -> None:
            for s in self.streams:
                s.flush()

    log_fh = log_path.open("a", encoding="utf-8")
    sys.stdout = Tee(sys.__stdout__, log_fh)  # type: ignore[assignment]
    sys.stderr = Tee(sys.__stderr__, log_fh)  # type: ignore[assignment]

    with pipeline_lock(lock_path):
        log(
            f"START styles={styles} topics={topics} allow_r2={args.allow_r2} "
            f"resume={args.resume} force={args.force}"
        )

        pf_errs = preflight(
            styles=styles,
            topics=topics,
            manifest=args.manifest,
            allow_r2=args.allow_r2,
        )
        if pf_errs:
            for e in pf_errs:
                log(f"PREFLIGHT FAIL: {e}", err=True)
            return 2
        log("PREFLIGHT ok")

        if args.preflight_only:
            return 0

        bank = load_index(args.manifest, allow_r2_download=args.allow_r2)
        log("STAGE prefetch")
        pref = prefetch_mp3s(
            bank,
            styles=styles,
            topics=topics,
            favor_gender=args.favor_gender,
        )
        (out_dir / "PREFETCH_REPORT.json").write_text(
            json.dumps(pref, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        if not pref["ok"]:
            log("PREFETCH BLOCKED — missing voice-bank audio:", err=True)
            for m in pref["missing"][:40]:
                log(f"  - {m}", err=True)
            if len(pref["missing"]) > 40:
                log(f"  … +{len(pref['missing']) - 40} more", err=True)
            return 2
        log(f"PREFETCH ok atoms_unique={pref['atoms_unique']}")

        if args.prefetch_only:
            return 0

        already_ok = (
            load_ok_keys(
                receipts_path,
                pilot.VAR / "PILOT_VARIANT_RENDER_RECEIPTS.jsonl",
            )
            if args.resume and not args.force
            else set()
        )
        jobs = [(s, t) for s in styles for t in topics]
        results: list[dict[str, Any]] = []
        failed = 0

        log(f"STAGE render jobs={len(jobs)}")
        for style, topic in jobs:
            key = job_key(style, topic)
            mp4 = final_mp4(style, topic)
            if args.resume and not args.force:
                # Prefer receipt hit; also accept verified on-disk AAC MP4
                pkg_for_resume = None
                try:
                    pkg_for_resume = assemble_reel_package(
                        build_pack(topic, style=style, voice_bank=bank.manifest_path),
                        bank=bank,
                        favor_gender=args.favor_gender,
                    )
                except ReelAssembleError:
                    pkg_for_resume = None
                if (key in already_ok or mp4_resume_eligible(mp4, pkg_for_resume)) and mp4_resume_eligible(
                    mp4, pkg_for_resume
                ):
                    codec = probe_audio_codec(mp4)
                    log(f"SKIP {key} (resume ok, audio={codec})")
                    results.append(
                        {
                            "status": "skipped",
                            "style": style,
                            "topic": topic,
                            "path": str(mp4.relative_to(REPO)),
                            "audio": "social_voice_bank",
                            "ts": utc_now(),
                        }
                    )
                    continue
                if key in already_ok:
                    log(f"RE-RENDER {key} (stale receipt; mp4 missing voice-bank audio)")

            log(f"RENDER {key}")
            try:
                row = render_one(
                    style=style,
                    topic=topic,
                    bank=bank,
                    favor_gender=args.favor_gender,
                    out_dir=out_dir,
                )
                append_jsonl(receipts_path, row)
                # Also append to legacy pilot receipts (do not overwrite)
                append_jsonl(pilot.VAR / "PILOT_VARIANT_RENDER_RECEIPTS.jsonl", row)
                results.append(row)
                log(
                    f"OK {key} {row['duration_s']}s bytes={row['bytes']} "
                    f"voices={sorted(set(row['voice_ids']))}"
                )
            except Exception as e:  # noqa: BLE001
                failed += 1
                err_row = {
                    "status": "fail",
                    "style": style,
                    "topic": topic,
                    "error": f"{type(e).__name__}: {e}",
                    "traceback": traceback.format_exc()[-2000:],
                    "ts": utc_now(),
                }
                append_jsonl(receipts_path, err_row)
                results.append(err_row)
                log(f"FAIL {key}: {err_row['error']}", err=True)
                if not args.continue_on_error:
                    break

        ok_n = sum(1 for r in results if r.get("status") == "ok")
        skip_n = sum(1 for r in results if r.get("status") == "skipped")
        closeout = {
            "schema": "social_voice_bank_video_pipeline_v1",
            "ts": utc_now(),
            "styles": styles,
            "topics": topics,
            "allow_r2": args.allow_r2,
            "jobs_planned": len(jobs),
            "ok": ok_n,
            "skipped": skip_n,
            "failed": failed,
            "receipts": str(receipts_path.relative_to(REPO)),
            "log": str(log_path.relative_to(REPO)),
            "acceptance_layer": "system working — voice-bank video pipeline",
            "status": "ok" if failed == 0 else "fail",
            "results": results,
        }
        closeout_path.write_text(
            json.dumps(closeout, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        log(
            f"DONE status={closeout['status']} ok={ok_n} skipped={skip_n} "
            f"failed={failed} → {closeout_path}"
        )
        return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
