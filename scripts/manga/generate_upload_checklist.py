#!/usr/bin/env python3
"""Generate operator upload checklist from profile + distribution sidecars."""
from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:
    raise RuntimeError("PyYAML required: pip install pyyaml") from exc

from phoenix_v4.manga.models.validation import repo_root


def _load_platform_fields(root: Path) -> dict[str, Any]:
    path = root / "config" / "brand_management" / "platform_credential_fields.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data.get("platforms") or {}


def _credential_section(platform: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    notes = platform.get("notes")
    dashboard = platform.get("dashboard_url")
    if dashboard:
        lines.append(f"- **Dashboard:** {dashboard}")
    if notes:
        lines.append(f"- **Notes:** {notes}")
    lines.append("")
    lines.append("### Credential fields (vault)")
    for field in platform.get("fields") or []:
        req = "required" if field.get("required") else "optional"
        lines.append(
            f"- [ ] **{field.get('label')}** (`{field.get('name')}`) — {req}"
        )
    return lines


def generate_upload_checklist(
    *,
    profile: dict[str, Any],
    built_formats: dict[str, Path],
    out_path: Path,
    repo_root_path: Path | None = None,
) -> Path:
    root = repo_root_path or repo_root()
    platforms = _load_platform_fields(root)
    title_id = str(profile.get("title_id") or "")
    series_title = str(profile.get("series_title") or title_id)
    brand_id = str(profile.get("brand_id") or "")
    teacher = str(profile.get("teacher") or "")
    formats_built = ", ".join(sorted(built_formats))

    lines = [
        f"# Upload checklist — {series_title}",
        "",
        f"- **title_id:** `{title_id}`",
        f"- **brand_id:** `{brand_id}`",
        f"- **teacher / creator:** {teacher}",
        f"- **formats built:** {formats_built}",
        "",
        "## Series copy (paste into dashboards)",
        "",
        f"- **Title:** {series_title}",
    ]
    logline = profile.get("series_logline")
    if logline:
        lines.extend([f"- **Logline:** {logline}"])
    description = str(profile.get("series_description") or "").strip()
    if description:
        lines.extend(["- **Description:**", "", description, ""])
    hook_lines = profile.get("hook_lines") or []
    if hook_lines:
        lines.append("- **Hook lines:**")
        for hl in hook_lines:
            lines.append(f"  - {hl}")
        lines.append("")

    comp_titles = profile.get("comp_titles") or []

    if "epub3" in built_formats:
        lines.extend(["## Apple Books (fixed-layout EPUB3)", ""])
        epub = built_formats["epub3"]
        lines.append(f"- **EPUB file:** `{epub.resolve()}`")
        if comp_titles:
            lines.append("- **Comp titles (not in EPUB; upload notes):**")
            for ct in comp_titles:
                lines.append(f"  - {ct}")
            lines.append("")
        apple = platforms.get("apple_books") or {}
        lines.extend(_credential_section(apple))
        lines.append("")

    if "cbz" in built_formats:
        lines.extend(["## GlobalComix (CBZ)", ""])
        cbz = built_formats["cbz"]
        lines.append(f"- **CBZ file:** `{cbz.resolve()}`")
        if comp_titles:
            lines.append("- **Comp titles (sidecar, not in CBZ):**")
            for ct in comp_titles:
                lines.append(f"  - {ct}")
            lines.append("")
        gcx = platforms.get("globalcomix") or {}
        lines.extend(_credential_section(gcx))
        lines.append("")

    if "print_pdf" in built_formats:
        pdf = built_formats["print_pdf"]
        lines.extend(["## Print PDF", "", f"- **PDF file:** `{pdf.resolve()}`", ""])

    if "webtoon" in built_formats:
        wt = built_formats["webtoon"]
        lines.extend(["## Webtoon strips", "", f"- **Output dir:** `{wt.resolve()}`", ""])

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return out_path
