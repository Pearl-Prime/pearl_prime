#!/usr/bin/env python3
"""RSS 2.0 + iTunes podcast feed from rendered episode metadata JSONs."""
from __future__ import annotations

import argparse
import json
import email.utils
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


def _itunes_el(parent: ET.Element, tag: str, text: str | None = None, attrib: dict | None = None) -> ET.Element:
    el = ET.SubElement(parent, f"{{{ITUNES_NS}}}{tag}", attrib or {})
    if text is not None:
        el.text = text
    return el


ITUNES_NS = "http://www.itunes.com/dtds/podcast-1.0.dtd"


def rfc2822_now() -> str:
    return email.utils.format_datetime(datetime.now(timezone.utc), usegmt=True)


def load_episode_meta(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_feed(
    episodes: list[dict[str, Any]],
    brand_id: str,
    series_id: str,
    base_url: str,
    channel_meta: dict[str, Any],
) -> ET.ElementTree:
    base = base_url.rstrip("/")
    rss = ET.Element("rss", {"version": "2.0"})
    rss.set("xmlns:itunes", ITUNES_NS)
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = channel_meta.get("title") or series_id
    ET.SubElement(channel, "description").text = channel_meta.get("description") or ""
    ET.SubElement(channel, "language").text = channel_meta.get("language") or "es-US"
    ET.SubElement(channel, "link").text = base

    _itunes_el(channel, "author", channel_meta.get("author") or brand_id)
    _itunes_el(channel, "summary", channel_meta.get("description") or "")
    cat = _itunes_el(channel, "category", attrib={"text": "Health & Fitness"})
    ET.SubElement(cat, f"{{{ITUNES_NS}}}category", {"text": "Mental Health"})
    _itunes_el(channel, "explicit", channel_meta.get("explicit") or "no")
    _itunes_el(channel, "type", "serial")
    _itunes_el(channel, "image", attrib={"href": f"{base}/{brand_id}/{series_id}/artwork.jpg"})

    # Newest first: sort by pubDate descending
    def pub_tuple(ep: dict[str, Any]) -> float:
        pd = ep.get("pub_date_rfc2822") or ""
        try:
            return email.utils.parsedate_to_datetime(pd).timestamp()
        except (TypeError, ValueError):
            return 0.0

    for ep in sorted(episodes, key=pub_tuple, reverse=True):
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = ep.get("title") or "Episode"
        ET.SubElement(item, "description").text = ep.get("description") or ""
        ET.SubElement(item, "guid", {"isPermaLink": "false"}).text = ep.get("guid") or ep.get("episode_id", "")
        ET.SubElement(item, "pubDate").text = ep.get("pub_date_rfc2822") or rfc2822_now()
        enc_url = ep.get("enclosure_url") or ""
        enc_len = str(ep.get("enclosure_length_bytes") or 0)
        ET.SubElement(
            item,
            "enclosure",
            {"url": enc_url, "length": enc_len, "type": "audio/mpeg"},
        )
        dur = str(int(float(ep.get("duration_s") or 0)))
        _itunes_el(item, "duration", dur)
        _itunes_el(item, "episode", str(ep.get("episode_number") or 1))
        _itunes_el(item, "season", str(ep.get("season_number") or 1))
        _itunes_el(item, "episodeType", "full")
        _itunes_el(item, "explicit", ep.get("explicit") or "no")
    return ET.ElementTree(rss)


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate podcast RSS feed XML")
    ap.add_argument("--episodes-dir", type=Path, required=True)
    ap.add_argument("--brand-id", required=True)
    ap.add_argument("--series-id", required=True)
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    meta_files = sorted(args.episodes_dir.glob("*.meta.json"))
    if not meta_files:
        # Allow *render_report.json paired with mp3 naming convention
        meta_files = sorted(args.episodes_dir.glob("episode_*.json"))
    episodes: list[dict[str, Any]] = []
    for mf in meta_files:
        if "render_report" in mf.name:
            continue
        try:
            episodes.append(load_episode_meta(mf))
        except json.JSONDecodeError:
            continue

    if not episodes:
        # Discover from render reports + mp3
        for rep in sorted(args.episodes_dir.glob("*.render_report.json")):
            r = json.loads(rep.read_text(encoding="utf-8"))
            mp3 = rep.with_suffix("").with_suffix(".mp3")
            if not mp3.name.endswith(".mp3"):
                mp3 = rep.parent / (rep.name.replace(".render_report.json", ".mp3"))
            if not mp3.exists():
                stem = rep.name.replace(".render_report.json", "")
                mp3 = rep.parent / f"{stem}.mp3"
            if mp3.exists():
                aid = r.get("episode_id", stem)
                episodes.append(
                    {
                        "guid": aid,
                        "episode_id": aid,
                        "title": stem,
                        "description": "",
                        "pub_date_rfc2822": rfc2822_now(),
                        "enclosure_url": f"{args.base_url.rstrip('/')}/{args.brand_id}/{args.series_id}/{mp3.name}",
                        "enclosure_length_bytes": mp3.stat().st_size,
                        "duration_s": r.get("duration_s", 0),
                        "episode_number": 1,
                        "season_number": 1,
                        "explicit": "no",
                    }
                )

    asm_path = args.episodes_dir / "channel_assembly.json"
    channel_meta: dict[str, Any] = {}
    if asm_path.exists():
        a = json.loads(asm_path.read_text(encoding="utf-8"))
        channel_meta = a.get("channel") or {}

    tree = build_feed(episodes, args.brand_id, args.series_id, args.base_url, channel_meta)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    tree.write(args.output, encoding="utf-8", xml_declaration=True, default_namespace=None)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
