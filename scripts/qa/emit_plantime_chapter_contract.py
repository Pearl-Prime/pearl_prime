#!/usr/bin/env python3
"""Emit plan-time chapter contracts from the current planner."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.planning.book_structure_plan import generate_book_plan  # noqa: E402
from phoenix_v4.planning.chapter_contract import (  # noqa: E402
    build_chapter_contracts,
    validate_chapter_contract_packet,
)


def emit_contract(
    *,
    topic: str,
    persona: str,
    engine: str,
    runtime_format: str,
    output_dir: Path,
    chapter_count: int | None = None,
) -> Path:
    plan = generate_book_plan(
        topic_id=topic,
        persona_id=persona,
        runtime_format=runtime_format,
        engine_type=engine,
        chapter_count=chapter_count,
        repo_root=REPO_ROOT,
    )
    packet = build_chapter_contracts(plan)
    errors = validate_chapter_contract_packet(packet)
    if errors:
        raise SystemExit("\n".join(errors))
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{persona}__{topic}__{engine}__{runtime_format}.chapter_contract.json"
    path.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit plan-time chapter contract packet")
    parser.add_argument("--topic", required=True)
    parser.add_argument("--persona", required=True)
    parser.add_argument("--engine", default="overwhelm")
    parser.add_argument("--runtime-format", default="standard_book")
    parser.add_argument("--chapter-count", type=int)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    path = emit_contract(
        topic=args.topic,
        persona=args.persona,
        engine=args.engine,
        runtime_format=args.runtime_format,
        chapter_count=args.chapter_count,
        output_dir=args.output_dir,
    )
    print(f"Contract written: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
