#!/usr/bin/env python3
"""CPU-only deterministic five-layer cover assembly.

Layers: brand identity, blueprint/template, series continuity, book-specific
identity, and locale typography. No image generation or GPU is used.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
import yaml

from scripts.publish.bank_image_picker import load_topic_map, pick_image
from scripts.publish.render_kdp_cover import render_kdp_cover

REPO_ROOT = Path(__file__).resolve().parents[2]
CATALOG_CONFIG = REPO_ROOT / "config/catalog/catalog_generation_config.yaml"


def assemble_cover(*, title: str, author: str, topic: str, output_path: Path,
                   subtitle: str = "", book_id: str | None = None,
                   series_id: str | None = None, locale: str = "en_US",
                   seed: str = "", index_path: Path | None = None,
                   topic_map_path: Path | None = None, allow_legacy_bank: bool = False,
                   legacy_candidates: tuple[dict[str, Any], ...] = ()) -> dict[str, Any]:
    locales = yaml.safe_load(CATALOG_CONFIG.read_text(encoding="utf-8"))["locales"]
    if locale not in locales:
        raise ValueError(f"Unknown catalog locale {locale!r}; expected one of {sorted(locales)}")
    kwargs: dict[str, Any] = {"seed": seed or book_id or title, "allow_legacy_bank": allow_legacy_bank,
                              "legacy_candidates": legacy_candidates}
    if index_path is not None: kwargs["index_path"] = index_path
    if topic_map_path is not None: kwargs["topic_map_path"] = topic_map_path
    image = pick_image(topic, **kwargs)
    topic_map = load_topic_map(topic_map_path) if topic_map_path else load_topic_map()
    template_topic = topic_map["topics"][topic].get("template_topic", topic)
    render = render_kdp_cover(image.path, title, author, subtitle=subtitle, genre=template_topic,
                              output_path=output_path, book_id=book_id)
    render.update({"image_source": image.to_dict(), "assembly_engine": "cpu_pillow",
                   "topic": topic, "template_topic": template_topic,
                   "layers": {"brand": True, "blueprint": template_topic, "series": series_id,
                              "book": book_id, "locale": locale}})
    return render


def main() -> int:
    parser = argparse.ArgumentParser(description="Assemble a licensed Storyblocks cover on CPU")
    parser.add_argument("--title", required=True)
    parser.add_argument("--author", required=True)
    parser.add_argument("--topic", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--subtitle", default="")
    parser.add_argument("--book-id")
    parser.add_argument("--series-id")
    parser.add_argument("--locale", default="en_US")
    parser.add_argument("--seed", default="")
    parser.add_argument("--license-index", type=Path)
    args = parser.parse_args()
    result = assemble_cover(title=args.title, author=args.author, topic=args.topic,
                            output_path=args.output, subtitle=args.subtitle,
                            book_id=args.book_id, series_id=args.series_id,
                            locale=args.locale, seed=args.seed, index_path=args.license_index)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
