#!/usr/bin/env python3
"""Build fixed-layout EPUB3 from composed manga pages."""
from __future__ import annotations

import json
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from phoenix_v4.manga.distribution.config_io import (
    grammar_for_format,
    load_format_grammars,
    publisher_label,
)
from scripts.manga._output_pipeline_xml import xml_escape


def _page_progression(reading_direction: str) -> str:
    if reading_direction == "right_to_left":
        return "rtl"
    if reading_direction == "left_to_right":
        return "ltr"
    return "default"


def build_epub3(
    *,
    profile: dict[str, Any],
    pages: list[Path],
    out_path: Path,
    repo_root: Path,
) -> Path:
    formats = load_format_grammars(repo_root)
    print_grammar = grammar_for_format(formats, "print")
    reading_direction = str(print_grammar.get("reading_direction") or "right_to_left")
    progression = _page_progression(reading_direction)

    title_id = str(profile.get("title_id") or "manga")
    series_title = str(profile.get("series_title") or title_id)
    description = str(profile.get("series_description") or "").strip()
    creator = str(profile.get("teacher") or profile.get("brand_id") or "unknown")
    publisher = publisher_label(str(profile.get("brand_id") or ""))
    hook_lines = profile.get("hook_lines") or []
    subject = str(hook_lines[0]) if hook_lines else series_title
    uid = f"urn:uuid:{uuid.uuid4()}"

    manifest: list[str] = [
        '<item id="nav" properties="nav" href="Text/nav.xhtml" '
        'media-type="application/xhtml+xml"/>'
    ]
    spine: list[str] = ['<itemref idref="nav" linear="no"/>']

    for idx, page in enumerate(pages, start=1):
        img_id = f"img_{idx:04d}"
        page_id = f"page_{idx:04d}"
        img_href = f"Images/page_{idx:03d}.png"
        xhtml_href = f"Text/page_{idx:04d}.xhtml"
        manifest.append(
            f'<item id="{img_id}" href="{img_href}" media-type="image/png"/>'
        )
        manifest.append(
            f'<item id="{page_id}" href="{xhtml_href}" media-type="application/xhtml+xml"/>'
        )
        spine.append(f'<itemref idref="{page_id}"/>')

    modified = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    opf = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf"
         xmlns:dc="http://purl.org/dc/elements/1.1/"
         xmlns:dcterms="http://purl.org/dc/terms/"
         version="3.0" unique-identifier="pub-id" xml:lang="en"
         prefix="rendition: http://www.idpf.org/vocab/rendition/#">
  <metadata>
    <dc:identifier id="pub-id">{uid}</dc:identifier>
    <dc:title>{xml_escape(series_title)}</dc:title>
    <dc:description>{xml_escape(description)}</dc:description>
    <dc:language>en</dc:language>
    <dc:creator>{xml_escape(creator)}</dc:creator>
    <dc:publisher>{xml_escape(publisher)}</dc:publisher>
    <dc:subject>{xml_escape(subject)}</dc:subject>
    <meta property="dcterms:modified">{modified}</meta>
    <meta name="book-type" content="comics"/>
    <meta property="rendition:layout">pre-paginated</meta>
    <meta property="rendition:spread">none</meta>
  </metadata>
  <manifest>
    {chr(10).join(manifest)}
  </manifest>
  <spine page-progression-direction="{progression}">
    {chr(10).join(spine)}
  </spine>
</package>
"""

    nav = """<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en">
<head><meta charset="utf-8"/><title>Nav</title></head>
<body>
<nav epub:type="toc" id="toc"><h1>Contents</h1><ol></ol></nav>
</body></html>"""

    container = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_path, "w") as zf:
        zf.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        zf.writestr("META-INF/container.xml", container)
        zf.writestr("OEBPS/content.opf", opf)
        zf.writestr("OEBPS/Text/nav.xhtml", nav)
        for idx, page in enumerate(pages, start=1):
            zf.write(page, arcname=f"OEBPS/Images/page_{idx:03d}.png")
            xhtml = f"""<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head><meta charset="utf-8"/><title>Page {idx}</title></head>
<body><img src="../Images/page_{idx:03d}.png" alt="page {idx}"/></body>
</html>"""
            zf.writestr(f"OEBPS/Text/page_{idx:04d}.xhtml", xhtml)

    sidecar = out_path.parent / f"{title_id}_metadata.json"
    sidecar.write_text(
        json.dumps(
            {
                "title_id": title_id,
                "comp_titles": profile.get("comp_titles") or [],
                "series_logline": profile.get("series_logline"),
                "note": "comp_titles excluded from EPUB; use for upload checklist",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return out_path
