#!/usr/bin/env python3
"""Apply HOOK v01 scene-first rewrites for P1 batch (ws_pearl_editor_hook_p1_rewrite_batch_20260527)."""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from p1_scene_first_rewrites_data import REWRITES  # noqa: E402
TSV = REPO / "artifacts/qa/HOOK_SCENE_FIRST_TAGGING_20260527.tsv"

V01_BLOCK_RE = re.compile(
    r"(## HOOK v01\n---\n\n---\n)([\s\S]*?)(\n---)",
    re.MULTILINE,
)
PLACEHOLDER_RE = re.compile(r"^\[Persona-specific hook for ")


def _split_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]


def replace_v01(atom_text: str, new_para1: str, *, move_old_to_para2: bool = True) -> str:
    m = V01_BLOCK_RE.search(atom_text)
    if not m:
        raise ValueError("No ## HOOK v01 block found")
    old_body = m.group(2).strip()
    old_paras = _split_paragraphs(old_body)
    parts = [new_para1.strip()]
    if move_old_to_para2 and old_paras:
        old_first = old_paras[0]
        if not PLACEHOLDER_RE.match(old_first) and old_first.strip() != new_para1.strip():
            parts.append(old_first)
        parts.extend(old_paras[1:])
    new_body = "\n\n".join(parts)
    return atom_text[: m.start(2)] + new_body + atom_text[m.end(2) :]


def update_tagging_tsv() -> None:
    rows: list[dict[str, str]] = []
    with TSV.open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        fieldnames = reader.fieldnames or []
        for row in reader:
            if row["rewrite_priority"] == "P1" and row["atom_path"] in REWRITES:
                row["classification"] = "SCENE_FIRST"
                row["first_paragraph_excerpt"] = REWRITES[row["atom_path"]][:200]
            rows.append(row)
    with TSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def apply_atoms() -> None:
    for rel, para1 in REWRITES.items():
        path = REPO / rel
        text = path.read_text(encoding="utf-8")
        path.write_text(replace_v01(text, para1), encoding="utf-8")
        print(f"updated {rel}")


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--tsv-only":
        update_tagging_tsv()
        return 0
    apply_atoms()
    update_tagging_tsv()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
