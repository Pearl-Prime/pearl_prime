#!/usr/bin/env python3
"""Build a durable manga proof packet from existing proof roots."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any, Iterable

TEXT_SUFFIXES = {".json", ".yaml", ".yml", ".md", ".tsv", ".txt"}
INDEXABLE_SUFFIXES = TEXT_SUFFIXES | {".png", ".jpg", ".jpeg", ".webp", ".pdf"}


class ProofPacketError(RuntimeError):
    pass


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_packet(
    *,
    roots: list[Path],
    out_dir: Path,
    copy_files: bool = False,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []
    limitations: list[str] = []
    for proof_index, source_root in enumerate(roots, start=1):
        source_root = source_root.resolve()
        if not source_root.exists():
            limitations.append(f"missing proof root: {source_root}")
            continue
        for path in sorted(source_root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in INDEXABLE_SUFFIXES:
                continue
            if path.suffix.lower() in TEXT_SUFFIXES:
                text = path.read_text(encoding="utf-8", errors="replace")
                if "/Users/" in text:
                    raise ProofPacketError(f"local home path found in proof text: {path}")
            record = {
                "proof_index": proof_index,
                "source_root": str(source_root),
                "relative_path": str(path.relative_to(source_root)),
                "bytes": path.stat().st_size,
                "sha256": _sha(path),
            }
            if copy_files:
                dst = out_dir / "proofs" / f"{proof_index:02d}" / path.relative_to(source_root)
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, dst)
                record["packet_path"] = str(dst.relative_to(out_dir))
            records.append(record)
    payload = {
        "schema_version": "1.0.0",
        "manga-proof-packet": str(out_dir),
        "record_count": len(records),
        "proof_root_count_requested": len(roots),
        "proof_root_count_present": len({row["proof_index"] for row in records}),
        "limitations": limitations,
        "records": records,
        "real-pearlstar-proof": "committed-or-local-as-indexed",
        "overall-manga-green": "NOT_PROVEN",
    }
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    checksums = [
        f"{row['sha256']}  {row.get('packet_path') or row['relative_path']}"
        for row in records
    ]
    (out_dir / "SHA256SUMS.txt").write_text("\n".join(checksums) + ("\n" if checksums else ""), encoding="utf-8")
    (out_dir / "KNOWN_LIMITATIONS.md").write_text(
        "# Known limitations\n\n"
        + "\n".join(f"- {row}" for row in limitations)
        + ("\n" if limitations else "- None recorded by the packet builder.\n"),
        encoding="utf-8",
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proof-root", type=Path, action="append", default=[])
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--copy-files", action="store_true")
    args = parser.parse_args()
    result = build_packet(roots=args.proof_root, out_dir=args.out_dir, copy_files=args.copy_files)
    print(json.dumps(result, indent=2))
    return 0 if not result["limitations"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
