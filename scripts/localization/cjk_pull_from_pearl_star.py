#!/usr/bin/env python3
"""Validate and batched-tar pull clean CJK locale atoms from Pearl Star.

Recipe mirrors #3032: validate each path on PS, tar-stream only CLEAN files,
re-validate locally, emit manifest for PR batching (≤180 files).

Usage:
  python3 scripts/localization/cjk_pull_from_pearl_star.py \\
    --locale ja_JP --paths-file /tmp/stranded_ja_clean.txt --batch-size 180
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SSH_HOST = "pearl_star"
PS_REPO = "~/phoenix_omega"

LOCALE_TO_PATH = {
    "ja_JP": "ja-JP",
    "zh_TW": "zh-TW",
    "zh_CN": "zh-CN",
    "ko_KR": "ko-KR",
}


def _ssh(cmd: str, *, timeout: int = 600) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["ssh", "-o", "BatchMode=yes", SSH_HOST, cmd],
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def validate_on_pearl_star(paths: list[str]) -> tuple[list[str], list[tuple[str, str]]]:
    if not paths:
        return [], []
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tf:
        tf.write("\n".join(paths) + "\n")
        local_list = tf.name

    remote_list = f"/tmp/cjk_validate_{Path(local_list).name}.txt"
    subprocess.run(
        ["scp", "-q", local_list, f"{SSH_HOST}:{remote_list}"],
        check=True,
        timeout=60,
    )
    cmd = (
        f"cd {PS_REPO} && export PYTHONPATH=. && "
        f"python3 scripts/localization/validate_cjk_atom.py --paths-file {remote_list}"
    )
    proc = _ssh(cmd, timeout=max(300, len(paths) * 2))
    clean: list[str] = []
    failed: list[tuple[str, str]] = []
    for line in (proc.stdout or "").splitlines():
        line = line.strip()
        if line.startswith("OK  "):
            p = line[4:].strip()
            if p.startswith("atoms/"):
                clean.append(p)
            elif "/atoms/" in p:
                clean.append("atoms/" + p.split("/atoms/", 1)[1])
            else:
                clean.append(p)
        elif line.startswith("FAIL "):
            rest = line[5:]
            path_part, _, reason = rest.partition(":")
            rel = path_part.strip()
            if "/atoms/" in rel and not rel.startswith("atoms/"):
                rel = "atoms/" + rel.split("/atoms/", 1)[1]
            failed.append((rel, reason.strip()))
    return clean, failed


def pull_tar_batch(paths: list[str], *, dry_run: bool = False) -> int:
    if not paths:
        return 0
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tf:
        tf.write("\n".join(paths) + "\n")
        list_path = tf.name

    remote_list = f"/tmp/cjk_pull_{Path(list_path).stem}.txt"
    subprocess.run(["scp", "-q", list_path, f"{SSH_HOST}:{remote_list}"], check=True, timeout=60)

    if dry_run:
        print(f"[dry-run] would pull {len(paths)} files")
        return len(paths)

    tar_cmd = (
        f"cd {PS_REPO} && tar czf - -T {remote_list} 2>/dev/null"
    )
    extract = subprocess.Popen(
        ["ssh", "-o", "BatchMode=yes", SSH_HOST, tar_cmd],
        stdout=subprocess.PIPE,
    )
    assert extract.stdout is not None
    untar = subprocess.run(
        ["tar", "xzf", "-", "-C", str(REPO_ROOT)],
        stdin=extract.stdout,
        capture_output=True,
    )
    extract.wait()
    if untar.returncode != 0:
        raise RuntimeError(f"untar failed: {untar.stderr.decode()}")
    return len(paths)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--locale", required=True, choices=sorted(LOCALE_TO_PATH))
    ap.add_argument("--paths-file", required=True, help="Stranded repo-relative paths on PS")
    ap.add_argument("--batch-size", type=int, default=180)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--manifest-out", help="Write pulled paths manifest")
    args = ap.parse_args(argv)

    raw = [
        ln.strip()
        for ln in Path(args.paths_file).read_text(encoding="utf-8").splitlines()
        if ln.strip() and not ln.startswith("#")
    ]
    print(f"Validating {len(raw)} candidate paths on Pearl Star...")
    clean, failed = validate_on_pearl_star(raw)
    print(f"  clean: {len(clean)}  failed: {len(failed)}")
    for path, reason in failed[:20]:
        print(f"  FAIL {path}: {reason}")
    if len(failed) > 20:
        print(f"  ... and {len(failed) - 20} more failures")

    batch = clean[: args.batch_size]
    if not batch:
        print("Nothing clean to pull.")
        return 1

    n = pull_tar_batch(batch, dry_run=args.dry_run)
    print(f"Pulled {n} files to {REPO_ROOT}")

    if not args.dry_run:
        local_failed = 0
        for rel in batch:
            proc = subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts/localization/validate_cjk_atom.py"), rel],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
            if proc.returncode != 0:
                local_failed += 1
                print(f"  local re-validate FAIL {rel}")
        if local_failed:
            print(f"WARNING: {local_failed} files failed local re-validation")

    if args.manifest_out:
        mp = Path(args.manifest_out)
        mp.parent.mkdir(parents=True, exist_ok=True)
        mp.write_text("\n".join(batch) + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
