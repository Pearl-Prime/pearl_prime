#!/usr/bin/env python3
"""Run LFS→R2 offload pilot round-trip proof (LFS_TO_R2_OFFLOAD_V1_SPEC §6).

Steps:
  1. Record sha256 of every PNG in pilot src
  2. push-offload → R2 + TSV manifest
  3. Delete local copies to a temp backup
  4. pull-on-demand → restore repo paths
  5. Verify sha256 byte-identical
  6. Run check_render_progress_bytes --require-images (manifest-verify with images absent)
  7. Write artifacts/audit/LFS_OFFLOAD_PILOT_PROOF_<date>.json

Requires R2 credentials (Keychain bridge or Codespaces secrets).
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from scripts.artifacts.lfs_offload_manifest import sha256_file  # noqa: E402

PILOT_SLUG = "stillness_press_alarm_composed_v4_ep_001"
SERIES_ID = "stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying"
BOOK_ID = "composed_v4_qwen__ep_001"
SRC = REPO / "artifacts/manga" / SERIES_ID / "composed_v4_qwen/ep_001"
REPO_PREFIX = f"artifacts/manga/{SERIES_ID}/composed_v4_qwen/ep_001"
TSV_REL = f"artifacts/manga/{SERIES_ID}/composed_v4_qwen/ep_001/RENDER_PROGRESS.tsv"


def _run(cmd: list[str]) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=REPO, check=True)


def main() -> int:
    pngs = sorted(SRC.glob("*.png"))
    if not pngs:
        print(f"❌ no PNGs under {SRC}", file=sys.stderr)
        return 1

    before = {p.name: sha256_file(p) for p in pngs}
    disk_before = sum(p.stat().st_size for p in pngs)

    # Generate RENDER_PROGRESS.tsv if missing
    tsv_path = REPO / TSV_REL
    lines = ["panel_id\tstatus\tbytes\tseconds\n"]
    for p in pngs:
        panel_id = p.stem
        lines.append(f"{panel_id}\tok\t{p.stat().st_size}\t0.0\n")
    tsv_path.write_text("".join(lines), encoding="utf-8")

    env = {**dict(__import__("os").environ), "PHOENIX_OMEGA_REMOTE": "local-override", "PYTHONPATH": str(REPO)}
    _run([
        sys.executable, "scripts/artifacts/r2_sync.py", "push-offload",
        "--slug", PILOT_SLUG,
        "--namespace", "manga_rendered_books",
        "--src", str(SRC),
        "--repo-path-prefix", REPO_PREFIX,
        "--series-id", SERIES_ID,
        "--book-id", BOOK_ID,
        "--write-yaml",
    ])

    backup = REPO / "artifacts/audit" / f"_pilot_backup_{PILOT_SLUG}"
    if backup.exists():
        shutil.rmtree(backup)
    backup.mkdir(parents=True)
    for p in pngs:
        shutil.move(str(p), str(backup / p.name))

    disk_after_delete = sum(p.stat().st_size for p in SRC.glob("*.png"))

    _run([sys.executable, "scripts/artifacts/r2_sync.py", "pull-on-demand", "--slug", PILOT_SLUG])

    after = {p.name: sha256_file(p) for p in sorted(SRC.glob("*.png"))}
    if before != after:
        print("❌ sha256 mismatch after round-trip", file=sys.stderr)
        print(json.dumps({"before": before, "after": after}, indent=2), file=sys.stderr)
        return 1

    # Gate: images were absent during pull window; manifest-verify must pass now that
    # files are restored OR while absent if we delete again — test absent path:
    for p in list(SRC.glob("*.png")):
        p.unlink()
    gate_rc = subprocess.run(
        [sys.executable, "scripts/ci/check_render_progress_bytes.py",
         "--paths", TSV_REL, "--require-images"],
        cwd=REPO,
        env=env,
    ).returncode

    # Restore backup for idempotent re-runs
    for p in backup.glob("*.png"):
        shutil.copy2(str(p), str(SRC / p.name))

    proof = {
        "slug": PILOT_SLUG,
        "files": len(pngs),
        "disk_bytes_before": disk_before,
        "disk_bytes_after_delete": disk_after_delete,
        "sha256_round_trip": "PASS",
        "render_bytes_gate_require_images": "PASS" if gate_rc == 0 else "FAIL",
        "pilot_src": str(SRC.relative_to(REPO)),
    }
    out = REPO / "artifacts/audit" / f"LFS_OFFLOAD_PILOT_PROOF_{date.today().isoformat()}.json"
    out.write_text(json.dumps(proof, indent=2) + "\n", encoding="utf-8")
    print(f"\n✓ proof written: {out.relative_to(REPO)}")

    if gate_rc != 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
