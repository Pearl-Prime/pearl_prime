#!/usr/bin/env python3
"""Apply marketing_deep_research scaffold YAML into canonical config files."""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
ALIAS_MAP_PATH = REPO_ROOT / "config" / "marketing" / "brand_id_alias_map.yaml"


def _load_alias_map() -> dict[str, str]:
    """Load scaffold-name → canonical brand_id map. Returns empty dict if file is absent."""
    if not ALIAS_MAP_PATH.exists():
        return {}
    try:
        import yaml
    except ImportError as e:
        raise RuntimeError("PyYAML required") from e

    try:
        raw = yaml.safe_load(ALIAS_MAP_PATH.read_text(encoding="utf-8")) or {}
    except Exception as e:
        raise RuntimeError(f"failed to load alias map {ALIAS_MAP_PATH}") from e

    return {str(k): str(v) for k, v in (raw.get("alias_to_canonical") or {}).items()}


BRAND_LIST_KEYS = (
    "brands",
    "brand_kdp_patches",
    "brand_vocabulary_patches",
    "brand_duration_patches",
    "brand_pricing_patches",
)

# Per-file stem → keys allowed to deep-merge into each registry brand row
STEM_BRAND_KEYS: dict[str, tuple[str, ...]] = {
    "01_gtm_identity_patch": ("gtm_identity", "discovery_contract"),
    "02_emotional_vocabulary_patch": ("emotional_vocabulary",),
    "05_duration_bands_patch": ("duration_strategy",),
    "06_cover_design_patch": ("cover_art_identity",),
    "07_pricing_topology_patch": ("pricing_posture",),
    "08_kdp_ebook_strategy_patch": ("kdp_ebook_identity",),
}


def parse_target_line(text: str) -> str | None:
    for line in text.splitlines()[:40]:
        m = re.search(r"Target:\s*(.+)", line, re.I)
        if m:
            return m.group(1).strip()
    return None


def deep_merge(base: dict, patch: dict, keys: tuple[str, ...]) -> dict:
    out = dict(base)
    for k in keys:
        if k not in patch or patch[k] in (None, {}, []):
            continue
        if k not in out or not isinstance(out[k], dict):
            out[k] = {}
        if not isinstance(patch[k], dict):
            out[k] = patch[k]
            continue
        merged = dict(out[k])
        for pk, pv in patch[k].items():
            if isinstance(pv, dict) and isinstance(merged.get(pk), dict):
                sub = dict(merged[pk])
                sub.update(pv)
                merged[pk] = sub
            else:
                merged[pk] = pv
        out[k] = merged
    return out


def _iter_brand_rows(data: dict):
    for key in BRAND_LIST_KEYS:
        for row in data.get(key) or []:
            if isinstance(row, dict) and row.get("brand_id"):
                yield row


def _registry_index(reg: dict) -> dict[str, int]:
    idx: dict[str, int] = {}
    for i, row in enumerate(reg.get("brand_archetypes") or []):
        bid = row.get("brand_id")
        if bid:
            idx[str(bid)] = i
    return idx


def apply_registry_patch(scaffold_path: Path, data: dict, dry_run: bool) -> tuple[str, list[str]]:
    reg_path = REPO_ROOT / "config/catalog_planning/brand_archetype_registry.yaml"
    try:
        import yaml
    except ImportError as e:
        raise RuntimeError("PyYAML required") from e

    reg = yaml.safe_load(reg_path.read_text(encoding="utf-8")) or {}
    brands = reg.get("brand_archetypes")
    if not isinstance(brands, list):
        return str(reg_path), ["registry missing brand_archetypes list"]

    stem = scaffold_path.stem
    merge_keys = STEM_BRAND_KEYS.get(stem)
    if not merge_keys:
        candidates = (
            "gtm_identity",
            "discovery_contract",
            "emotional_vocabulary",
            "duration_strategy",
            "cover_art_identity",
            "pricing_posture",
            "kdp_ebook_identity",
        )
        found: set[str] = set()
        for row in list(_iter_brand_rows(data)):
            for k in candidates:
                if k in row and row[k] not in (None, {}, []):
                    found.add(k)
        merge_keys = tuple(found) if found else ("gtm_identity", "discovery_contract")

    messages: list[str] = []

    if stem == "02_emotional_vocabulary_patch" and isinstance(data.get("global_constraints"), dict):
        gc = reg.setdefault("global_constraints", {})
        for k, v in data["global_constraints"].items():
            if v in (None, "", [], {}):
                continue
            if isinstance(v, dict) and isinstance(gc.get(k), dict):
                sub = dict(gc[k])
                sub.update(v)
                gc[k] = sub
            else:
                gc[k] = v
        messages.append("merged top-level global_constraints")

    if stem == "05_duration_bands_patch" and isinstance(data.get("global_constraints_patch"), dict):
        gc = reg.setdefault("global_constraints", {})
        for k, v in data["global_constraints_patch"].items():
            if v not in (None, "", []):
                gc[k] = v
        messages.append("merged global_constraints_patch")

    idx = _registry_index(reg)
    alias_map = _load_alias_map()
    for row in _iter_brand_rows(data):
        bid = str(row["brand_id"])
        canonical = alias_map.get(bid, bid)  # resolve alias → canonical
        if canonical != bid:
            messages.append(f"alias {bid!r} → {canonical!r}")
        if canonical not in idx:
            messages.append(f"skip unknown brand_id {bid!r} (canonical: {canonical!r})")
            continue
        i = idx[canonical]
        brands[i] = deep_merge(brands[i], row, merge_keys)
        messages.append(f"patched brand {canonical}: {merge_keys}")

    reg["brand_archetypes"] = brands

    if dry_run:
        return str(reg_path), messages + ["dry-run: no write"]

    backup = reg_path.with_suffix(
        reg_path.suffix + f".bak.{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    )
    shutil.copy2(reg_path, backup)
    reg_path.write_text(yaml.dump(reg, default_flow_style=False, allow_unicode=True, sort_keys=False), encoding="utf-8")
    messages.append(f"wrote {reg_path.relative_to(REPO_ROOT)} backup {backup.name}")
    return str(reg_path), messages


def apply_consumer_language_patch(data: dict, dry_run: bool) -> tuple[str, list[str]]:
    import yaml

    dest = REPO_ROOT / "config/marketing/consumer_language_by_topic.yaml"
    cur = yaml.safe_load(dest.read_text(encoding="utf-8")) if dest.exists() else {}
    cur = cur or {}
    topics = cur.get("topics")
    if not isinstance(topics, list):
        topics = []
    by_id = {t.get("topic_id"): i for i, t in enumerate(topics) if isinstance(t, dict) and t.get("topic_id")}
    for t in data.get("topics") or []:
        if not isinstance(t, dict) or not t.get("topic_id"):
            continue
        tid = t["topic_id"]
        if tid in by_id:
            topics[by_id[tid]] = t
        else:
            topics.append(t)
            by_id[tid] = len(topics) - 1
    cur["topics"] = topics
    if dry_run:
        return str(dest), ["dry-run consumer_language"]
    dest.write_text(yaml.dump(cur, default_flow_style=False, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return str(dest), [f"wrote {dest.relative_to(REPO_ROOT)}"]


def _normalize_script_entry(entry: dict) -> dict | None:
    pid = entry.get("persona_id")
    tid = entry.get("topic_id")
    if not pid or not tid:
        return None
    if "scripts" in entry and isinstance(entry["scripts"], list):
        return {"persona_id": pid, "topic_id": tid, "scripts": [str(s) for s in entry["scripts"] if str(s).strip()]}
    single = entry.get("invisible_script")
    if single and str(single).strip():
        return {"persona_id": pid, "topic_id": tid, "scripts": [str(single).strip()]}
    return None


def apply_invisible_scripts_patch(data: dict, dry_run: bool) -> tuple[str, list[str]]:
    import yaml

    dest = REPO_ROOT / "config/marketing/invisible_scripts_by_persona_topic.yaml"
    cur = yaml.safe_load(dest.read_text(encoding="utf-8")) or {}
    scripts = cur.get("scripts")
    if not isinstance(scripts, list):
        scripts = []
    key_index: dict[tuple[str, str], int] = {}
    for i, s in enumerate(scripts):
        if isinstance(s, dict) and s.get("persona_id") and s.get("topic_id"):
            key_index[(str(s["persona_id"]), str(s["topic_id"]))] = i

    for entry in data.get("scripts") or []:
        if not isinstance(entry, dict):
            continue
        norm = _normalize_script_entry(entry)
        if not norm:
            continue
        k = (norm["persona_id"], norm["topic_id"])
        if k in key_index:
            scripts[key_index[k]] = norm
        else:
            scripts.append(norm)
            key_index[k] = len(scripts) - 1

    cur["scripts"] = scripts
    if dry_run:
        return str(dest), ["dry-run invisible_scripts"]
    dest.write_text(yaml.dump(cur, default_flow_style=False, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return str(dest), [f"wrote {dest.relative_to(REPO_ROOT)}"]


def main() -> int:
    ap = argparse.ArgumentParser(description="Apply marketing scaffold into canonical configs")
    ap.add_argument("scaffold", type=Path, help="Scaffold YAML path")
    ap.add_argument("--dry-run", action="store_true", help="Do not write files")
    args = ap.parse_args()
    path = args.scaffold if args.scaffold.is_absolute() else REPO_ROOT / args.scaffold
    if not path.exists():
        print(f"Not found: {path}", file=sys.stderr)
        return 2

    try:
        import yaml
    except ImportError:
        print("PyYAML required", file=sys.stderr)
        return 2

    raw = path.read_text(encoding="utf-8")
    target = parse_target_line(raw) or ""
    data = yaml.safe_load(raw) or {}

    tl = target.lower()
    try:
        if "brand_archetype_registry" in tl:
            dest, msgs = apply_registry_patch(path, data, args.dry_run)
        elif "consumer_language" in tl:
            dest, msgs = apply_consumer_language_patch(data, args.dry_run)
        elif "invisible_scripts" in tl:
            dest, msgs = apply_invisible_scripts_patch(data, args.dry_run)
        else:
            print(f"Could not infer target from header: {target!r}", file=sys.stderr)
            return 2
    except Exception as e:
        print(f"Patch failed: {e}", file=sys.stderr)
        return 1

    print(dest)
    for m in msgs:
        print(f"  {m}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
