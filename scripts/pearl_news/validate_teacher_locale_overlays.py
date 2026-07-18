#!/usr/bin/env python3
"""Validate teacher topic pack locale overlays (ja, zh-cn) against English bases."""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError as e:  # pragma: no cover
    raise SystemExit(f"PyYAML required: {e}") from e

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pearl_news.pipeline.deterministic_teacher_topic import load_teacher_topic_pack  # noqa: E402

_BAD_ROOT_KEYS = frozenset({"teacher_id", "topic", "sdg_number", "template_id", "schema_version", "active"})


def _has_japanese_prose(s: str) -> bool:
    return bool(re.search(r"[\u3040-\u30ff\u4e00-\u9fff]", s))


def _has_cjk_prose(s: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", s))


def _first_hook_line(pack: dict) -> str:
    hp = (pack.get("hook_personal") or {}).get("options") or []
    if hp and isinstance(hp[0], dict):
        return str(hp[0].get("line") or "")
    return ""


def main() -> int:
    teachers_root = REPO_ROOT / "pearl_news" / "teacher_topic_packs" / "teachers"
    bases = sorted(teachers_root.glob("*/*.yaml"))
    errors: list[str] = []

    for base_path in bases:
        rel = base_path.relative_to(teachers_root)
        teacher_id = rel.parts[0]
        topic = rel.stem
        for lang, checker, label in (
            ("ja", _has_japanese_prose, "Japanese"),
            ("zh-cn", _has_cjk_prose, "Chinese"),
        ):
            overlay_path = (
                REPO_ROOT
                / "pearl_news"
                / "teacher_topic_packs"
                / "locales"
                / lang
                / "teachers"
                / teacher_id
                / f"{topic}.yaml"
            )
            if not overlay_path.exists():
                errors.append(f"Missing overlay: {overlay_path.relative_to(REPO_ROOT)}")
                continue
            raw = yaml.safe_load(overlay_path.read_text(encoding="utf-8")) or {}
            if not isinstance(raw, dict):
                errors.append(f"Overlay not a dict: {overlay_path}")
                continue
            for bad in _BAD_ROOT_KEYS & raw.keys():
                errors.append(f"Metadata key {bad!r} should not be in overlay {overlay_path}")
            ts = raw.get("title_system") or {}
            hl1 = (ts.get("headline_layer_1") or {}).get("options") or []
            hl2_ts = (ts.get("headline_layer_2") or {}).get("options") or []
            hl2_root = (raw.get("headline_layer_2") or {}).get("options") or []
            if not hl1 and not hl2_ts and not hl2_root:
                errors.append(
                    f"Missing title headlines (layer_1 or layer_2 options) in {overlay_path}"
                )
            if "hook_personal" not in raw and "hook_big_picture" not in raw:
                errors.append(f"Missing hook_personal / hook_big_picture in {overlay_path}")
            if "teacher_intro" not in raw:
                errors.append(f"Missing teacher_intro in {overlay_path}")

            merged = load_teacher_topic_pack(
                REPO_ROOT, teacher_id, topic, template_id=None, language=lang
            )
            if not merged:
                errors.append(f"Merged pack is empty for {teacher_id}/{topic} lang={lang}")
                continue
            hook = _first_hook_line(merged)
            if hook and not checker(hook):
                errors.append(
                    f"Merged hook_personal for {teacher_id}/{topic} ({lang}) "
                    f"does not look like {label}: {hook[:80]!r}..."
                )

    if errors:
        print("Validation failed:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"OK: {len(bases)} base packs × 2 locales; overlays and merged hooks validated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
