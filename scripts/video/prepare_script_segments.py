#!/usr/bin/env python3
"""
Script Preparer: render_manifest + optional plan/metadata -> script_segments.
Validates render manifest contract; outputs timed segments for Shot Planner.
Usage: python scripts/video/prepare_script_segments.py <render_manifest.json> -o <script_segments.json> [--content-type therapeutic] [--wpm 140] [--metadata <plan_or_metadata.json>]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
from scripts.video._config import write_atomically, should_skip_output


def _word_count(text: str) -> int:
    return len(text.split())


def _duration_from_wpm(words: int, wpm: float) -> float:
    return (words / wpm) * 60.0 if wpm else 0.0


# ── HTML Content Parser ─────────────────────────────────────────────
# Extracts narration segments from an HTML presentation file.
# Maps semantic HTML structure to arc roles for the video pipeline.

from html.parser import HTMLParser
import re as _re


class _HTMLSegmentExtractor(HTMLParser):
    """Extract text blocks from HTML, tagging each with its semantic role.

    Supports both semantic HTML (h1, p, blockquote) and CSS-class-based
    layouts (common in SPA presentations like Pearl Prime v6).

    Class-based mapping (Pearl Prime style):
    - ``.disp`` / ``.hl`` → hook (display headlines)
    - ``.bt`` → build (body text)
    - ``.qb`` → release (quotes)
    - ``.eye`` → hook (eyebrow/section labels)
    - ``.cnm`` → build (cell names in grids)
    - ``.cd`` → build (cell descriptions)
    - ``.snum`` → build (stat numbers)
    """

    _TAG_ARC = {
        "h1": "hook", "h2": "hook", "h3": "build",
        "p": "build", "blockquote": "release", "li": "build",
    }

    _CLASS_ARC = {
        "disp": "hook", "hl": "hook", "eye": "hook",
        "bt": "build", "cnm": "build", "cd": "build",
        "qb": "release", "snum": "build", "slbl": "build",
    }

    def __init__(self) -> None:
        super().__init__()
        self._segments: list[dict] = []
        self._current_tag: str = ""
        self._current_arc: str = "build"
        self._current_text: list[str] = []
        self._in_block = False
        self._block_depth = 0
        self._skip_tags = {"style", "script", "head"}
        self._skip_depth = 0

    def _class_arc(self, attrs: list) -> str | None:
        for name, val in attrs:
            if name == "class" and val:
                for cls in val.split():
                    if cls in self._CLASS_ARC:
                        return self._CLASS_ARC[cls]
        return None

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag in self._skip_tags:
            self._skip_depth += 1
            return
        if self._skip_depth > 0:
            return

        # Check class-based arc first (works on any tag), then tag-based
        class_arc = self._class_arc(attrs)
        tag_arc = self._TAG_ARC.get(tag)

        if class_arc or tag_arc:
            self._flush()
            self._current_tag = tag
            self._current_arc = class_arc or tag_arc or "build"
            self._in_block = True
            self._block_depth = 1
        elif self._in_block:
            self._block_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in self._skip_tags:
            self._skip_depth = max(0, self._skip_depth - 1)
            return
        if self._in_block:
            if tag == self._current_tag:
                self._block_depth -= 1
                if self._block_depth <= 0:
                    self._flush()
                    self._in_block = False

    def handle_data(self, data: str) -> None:
        if self._skip_depth > 0:
            return
        if self._in_block:
            self._current_text.append(data)

    def _flush(self) -> None:
        text = " ".join(self._current_text).strip()
        text = _re.sub(r"\s+", " ", text)
        text = _re.sub(r"\u00a0", " ", text)  # non-breaking space
        text = text.strip()
        # Skip very short fragments and duplicates
        if text and _word_count(text) >= 3:
            # Deduplicate (SPA presentations repeat content across views)
            if not self._segments or self._segments[-1]["text"] != text:
                self._segments.append({
                    "text": text,
                    "arc_role": self._current_arc,
                    "tag": self._current_tag,
                })
        self._current_text = []

    @property
    def segments(self) -> list[dict]:
        self._flush()
        return list(self._segments)


def extract_segments_from_html(html_path: Path, wpm: float = 140.0) -> dict:
    """Parse an HTML file into a render_manifest-compatible dict.

    Extracts text from ``h1``, ``h2``, ``h3``, ``p``, ``blockquote``, ``li``
    tags and assigns arc roles. The last 10% of segments are tagged as
    ``resolve``.

    Returns a dict with ``plan_id`` and ``segments`` ready for
    :func:`prepare_segments`.
    """
    html_content = html_path.read_text(encoding="utf-8")
    parser = _HTMLSegmentExtractor()
    parser.feed(html_content)
    raw = parser.segments

    if not raw:
        return {"plan_id": html_path.stem, "segments": []}

    # Tag last segments as resolve
    resolve_start = max(1, int(len(raw) * 0.9))
    for i in range(resolve_start, len(raw)):
        raw[i]["arc_role"] = "resolve"

    # Tag first segment as hook if not already
    if raw:
        raw[0]["arc_role"] = "hook"

    # Build render_manifest segments
    segments = []
    for i, block in enumerate(raw):
        segments.append({
            "segment_id": f"seg-{i + 1}",
            "text": block["text"],
            "slot_id": f"html-{block['tag']}-{i + 1}",
            "primary_atom_id": f"html-{i + 1}",
            "atom_refs": [{"atom_id": f"html-{i + 1}", "weight": 1.0, "role": "primary"}],
            "_arc_hint": block["arc_role"],
        })

    return {"plan_id": html_path.stem, "segments": segments}


def prepare_segments(manifest: dict, content_type: str, wpm: float, metadata_by_segment: dict | None) -> dict:
    plan_id = manifest["plan_id"]
    segments_in = manifest["segments"]
    out_segments = []
    t = 0.0
    for i, seg in enumerate(segments_in):
        text = seg.get("text", "")
        words = _word_count(text)
        duration_s = _duration_from_wpm(words, wpm)
        end_time_s = t + duration_s
        meta = metadata_by_segment.get(seg["segment_id"]) if metadata_by_segment else None
        if not meta:
            meta = {"arc_role": "hook" if i == 0 else "build", "emotional_band": "calm" if i == 0 else "subdued"}
        out_segments.append({
            "segment_id": seg["segment_id"],
            "text": text,
            "start_time_s": round(t, 2),
            "end_time_s": round(end_time_s, 2),
            "slot_id": seg.get("slot_id", ""),
            "primary_atom_id": seg.get("primary_atom_id", ""),
            "metadata": meta,
        })
        t = end_time_s
    return {
        "plan_id": plan_id,
        "content_type": content_type,
        "segments": out_segments,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Prepare script segments from render manifest")
    ap.add_argument("render_manifest", help="Path to render_manifest.json")
    ap.add_argument("-o", "--out", required=True, help="Output script_segments.json path")
    ap.add_argument("--content-type", default="therapeutic", help="content_type for pacing (default: therapeutic)")
    ap.add_argument("--wpm", type=float, default=140.0, help="Words per minute for timing (default: 140)")
    ap.add_argument("--metadata", help="Optional JSON with segment_id -> { arc_role, emotional_band } or plan with atom metadata")
    ap.add_argument("--force", action="store_true", help="Overwrite output even if it already exists")
    args = ap.parse_args()

    path = Path(args.render_manifest)
    if not path.exists():
        print(f"Error: not found: {path}", file=sys.stderr)
        return 1

    # Auto-detect HTML input and convert to render manifest format
    if path.suffix.lower() in (".html", ".htm"):
        print(f"HTML detected: parsing {path.name}...", flush=True)
        manifest = extract_segments_from_html(path, wpm=args.wpm)
        print(f"  Extracted {len(manifest.get('segments', []))} segments from HTML")
    else:
        manifest = json.loads(path.read_text(encoding="utf-8"))

    if "plan_id" not in manifest or "segments" not in manifest:
        print("Error: render manifest must have plan_id and segments", file=sys.stderr)
        return 1

    metadata_by_segment = None
    if args.metadata:
        meta_path = Path(args.metadata)
        if meta_path.exists():
            data = json.loads(meta_path.read_text(encoding="utf-8"))
            if isinstance(data, dict) and "segments" in data:
                metadata_by_segment = {s["segment_id"]: s.get("metadata", {}) for s in data["segments"] if "metadata" in s}
            elif isinstance(data, dict):
                metadata_by_segment = data

    out_path = Path(args.out)
    if should_skip_output(out_path, ["plan_id", "segments"], args.force):
        print(f"Skip (output exists, use --force to overwrite): {out_path}")
        return 0
    result = prepare_segments(manifest, args.content_type, args.wpm, metadata_by_segment)
    write_atomically(out_path, result)
    print(f"Wrote {len(result['segments'])} segments to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
