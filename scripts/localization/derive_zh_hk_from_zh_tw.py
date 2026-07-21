#!/usr/bin/env python3
"""
zh-HK derivative pass — adapt from zh-TW truth, not from English.

Rationale (Prompt-D closeout, 2026-07-13): zh-TW is the most complete CJK6
locale (95.9%+ baseline). Rather than re-running the full English-source
translation loop for zh-HK (which would re-derive from scratch and ignore
the fact zh-TW's Traditional-script rendering is already validated), this
script takes each zh-TW CANONICAL.txt as the source-of-truth base and asks
the same Tier-2 Qwen model (Ollama, safe-by-default — mirrors
llm_client.py's provider resolution) to adapt it into Hong Kong
Cantonese-inflected written register:
  - Traditional script (already true of zh-TW; preserved)
  - HK-specific colloquial grammar where natural: 嘅/緊/咗/佢/唔 etc.
    (written Cantonese particles), not Taiwan-Mandarin phrasing
  - HK cultural/market register, not Taiwan register
  - Same ## TYPE vNN headers and --- delimiters preserved exactly

This is a derivative pass: it does NOT claim to be a substitute for a full
independent English->zh-HK translation wave. It is scoped, honest, and
resumable (--resume skips existing zh-HK files). Both source (zh-TW) and
target (zh-HK) file existence are required before an entry is queued.

Usage:
  python scripts/localization/derive_zh_hk_from_zh_tw.py --resume --max-files 200
  python scripts/localization/derive_zh_hk_from_zh_tw.py --resume --persona educators
"""
from __future__ import annotations

import argparse
import logging
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.localization.llm_client import call_llm  # noqa: E402
from scripts.localization.run_translation_loop import (  # noqa: E402
    ALL_ATOM_TYPES,
    _load_config,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("derive_zh_hk")

SYSTEM_PROMPT = (
    "You are a professional Hong Kong Cantonese localization editor adapting "
    "therapeutic/self-help content that has already been translated into "
    "Traditional Chinese for the Taiwan market (zh-TW). Your job is to adapt "
    "it — NOT re-translate from scratch — into Hong Kong written Cantonese "
    "register (zh-HK) for a Hong Kong audience.\n\n"
    "Rules:\n"
    "1. Keep Traditional Chinese script (already true of the source).\n"
    "2. Shift Taiwan-Mandarin grammar/phrasing to natural Hong Kong written "
    "Cantonese where a Hong Kong reader would notice the difference — use "
    "Cantonese particles/grammar such as 嘅/緊/咗/佢/唔/喺/俾 where they read "
    "more naturally than the Taiwan-Mandarin equivalents (的/正在/了/他/不/在/給).\n"
    "3. Preserve the second-person voice and the gentle, validating, "
    "zero-judgment emotional tone exactly.\n"
    "4. Preserve the ## TYPE vNN headers exactly as-is (English, unchanged).\n"
    "5. Preserve the --- delimiters exactly as-is.\n"
    "6. Do not add explanations, notes, or commentary.\n"
    "7. Return ONLY the adapted text in identical format to the source.\n"
    "8. Each variant must read as native Hong Kong writing, not as Taiwan "
    "Mandarin with a few words swapped."
)


def discover_pairs(atoms_root: Path, persona: str | None, topic: str | None) -> list[Path]:
    """Return zh-TW CANONICAL.txt source paths eligible for zh-HK derivation."""
    out: list[Path] = []
    for atom_type in ALL_ATOM_TYPES:
        for tw_path in atoms_root.rglob(f"{atom_type}/locales/zh-TW/CANONICAL.txt"):
            slot_dir = tw_path.parent.parent.parent  # .../{persona}/{topic}/{slot}
            rel = slot_dir.relative_to(atoms_root)
            if len(rel.parts) != 3:
                continue
            p, t = rel.parts[0], rel.parts[1]
            if persona and p != persona:
                continue
            if topic and t != topic:
                continue
            out.append(tw_path)
    return sorted(out)


def derive_one(tw_path: Path, resume: bool) -> tuple[str, str]:
    slot_dir = tw_path.parent.parent.parent
    hk_path = slot_dir / "locales" / "zh-HK" / "CANONICAL.txt"
    rel = str(slot_dir.relative_to(REPO_ROOT / "atoms"))

    if resume and hk_path.exists() and hk_path.stat().st_size > 100:
        return rel, "resume_skip"

    source_text = tw_path.read_text(encoding="utf-8")
    cfg = _load_config()
    try:
        adapted = call_llm(SYSTEM_PROMPT, source_text, cfg, role="draft")
    except Exception as e:  # noqa: BLE001
        logger.error("%s: FAILED (%s)", rel, e)
        return rel, f"error: {e}"

    if not adapted or len(adapted.strip()) < 50:
        return rel, "error: empty_response"

    hk_path.parent.mkdir(parents=True, exist_ok=True)
    hk_path.write_text(adapted, encoding="utf-8")
    return rel, "derived"


def main() -> int:
    ap = argparse.ArgumentParser(description="Derive zh-HK from zh-TW truth")
    ap.add_argument("--persona", help="Filter to one persona")
    ap.add_argument("--topic", help="Filter to one topic")
    ap.add_argument("--resume", action="store_true", help="Skip files with existing zh-HK output")
    ap.add_argument("--max-parallel", type=int, default=6)
    ap.add_argument("--max-files", type=int, default=0, help="Limit number of files (0=all)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    from scripts.localization.llm_client import _cloud_providers_allowed, _is_ollama_endpoint

    if not args.dry_run and not _is_ollama_endpoint() and not _cloud_providers_allowed():
        print(
            "Ollama endpoint required (OLLAMA_HOST or QWEN_BASE_URL with :11434), "
            "or set PHOENIX_TRANSLATION_ALLOW_CLOUD=1 (or use --dry-run)",
            file=sys.stderr,
        )
        return 2

    atoms_root = REPO_ROOT / "atoms"
    pairs = discover_pairs(atoms_root, args.persona, args.topic)
    if args.max_files and args.max_files > 0:
        pairs = pairs[: args.max_files]

    print(f"zh-TW source files eligible for zh-HK derivation: {len(pairs)}")
    if args.dry_run:
        for p in pairs[:20]:
            print(" ", p.parent.parent.parent.relative_to(atoms_root))
        if len(pairs) > 20:
            print(f"  ... and {len(pairs) - 20} more")
        return 0

    derived = errors = skipped = 0
    with ThreadPoolExecutor(max_workers=args.max_parallel) as ex:
        futs = {ex.submit(derive_one, p, args.resume): p for p in pairs}
        for i, fut in enumerate(as_completed(futs), 1):
            rel, status = fut.result()
            print(f"  [{i}/{len(pairs)}] {rel}: {status}")
            if status == "derived":
                derived += 1
            elif status == "resume_skip":
                skipped += 1
            else:
                errors += 1

    print(f"\nDone. derived={derived} skipped={skipped} errors={errors}")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
