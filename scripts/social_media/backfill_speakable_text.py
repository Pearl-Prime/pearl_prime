#!/usr/bin/env python3
"""Backfill MANIFEST.tsv speakable_text from SSOT + apply_text_prep (deterministic).

Does not re-synth audio. Recomputes speakable_text and optionally refreshes
params_hash / speakable_preview. SSOT atoms are never mutated.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "social_media"))

from tts_text_prep import apply_text_prep, load_prep  # noqa: E402

ATOMS_DEFAULT = REPO / "SOURCE_OF_TRUTH" / "social_media_atoms" / "evergreen_en_us_atoms.jsonl"
PREP_DEFAULT = REPO / "config" / "tts" / "social_media_tts_text_prep.yaml"
HEADER = (
    "atom_id\tpersona\ttopic\tlocale\tvoice_id\tparams_hash\tchar_count\t"
    "r2_key\tbytes\tsha256\tstatus\tspeakable_preview\tspeakable_text\n"
)


def _content_hash(voice_id: str, speakable: str, prep_ver: str) -> str:
    blob = json.dumps(
        {"voice_id": voice_id, "speakable": speakable, "prep": prep_ver},
        sort_keys=True,
    ).encode()
    return hashlib.sha256(blob).hexdigest()[:16]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--atoms", type=Path, default=ATOMS_DEFAULT)
    ap.add_argument("--text-prep", type=Path, default=PREP_DEFAULT)
    ap.add_argument("-o", "--out", type=Path, default=None, help="Default: overwrite --manifest")
    args = ap.parse_args()
    out = args.out or args.manifest

    prep = load_prep(args.text_prep)
    prep_ver = str(prep.get("schema_version") or "1")
    by_id = {}
    for line in args.atoms.read_text(encoding="utf-8").splitlines():
        if line.strip():
            o = json.loads(line)
            by_id[o["atom_id"]] = o

    lines = args.manifest.read_text(encoding="utf-8").splitlines()
    if not lines:
        print("empty manifest", file=sys.stderr)
        return 1
    cols = lines[0].split("\t")
    rows = []
    filled = missing = 0
    for line in lines[1:]:
        parts = line.split("\t")
        # tolerate shorter rows from older manifests
        while len(parts) < len(cols):
            parts.append("")
        row = dict(zip(cols, parts[: len(cols)]))
        # absorb extra trailing cols if old row had fewer named cols
        aid = row.get("atom_id", "")
        atom = by_id.get(aid)
        if not atom:
            missing += 1
            row["speakable_text"] = row.get("speakable_text") or ""
            rows.append(row)
            continue
        speakable = apply_text_prep(atom["text"], prep)
        speakable_clean = speakable.replace("\t", " ").replace("\n", " ")
        row["speakable_text"] = speakable_clean
        row["speakable_preview"] = speakable_clean[:80]
        row["char_count"] = str(len(speakable))
        voice_id = row.get("voice_id") or ""
        if voice_id and row.get("status") == "ok":
            row["params_hash"] = _content_hash(voice_id, speakable, prep_ver)
        filled += 1
        rows.append(row)

    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        f.write(HEADER)
        for r in sorted(rows, key=lambda x: x.get("atom_id") or ""):
            f.write(
                "\t".join(
                    [
                        r.get("atom_id", ""),
                        r.get("persona", ""),
                        r.get("topic", ""),
                        r.get("locale", ""),
                        r.get("voice_id", ""),
                        r.get("params_hash", ""),
                        r.get("char_count", ""),
                        r.get("r2_key", ""),
                        r.get("bytes", ""),
                        r.get("sha256", ""),
                        r.get("status", ""),
                        r.get("speakable_preview", ""),
                        r.get("speakable_text", ""),
                    ]
                )
                + "\n"
            )
    print(f"backfill wrote {out} filled={filled} missing_atoms={missing} rows={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
