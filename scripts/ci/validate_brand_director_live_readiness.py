#!/usr/bin/env python3
"""Validate that Brand Wizard/Director assignments are live on public ops surfaces."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except ModuleNotFoundError:  # GitHub Actions runs this before dependency install.
    yaml = None

ROOT = Path(__file__).resolve().parents[2]
ASSIGNMENTS = ROOT / "config" / "brand_management" / "brand_director_assignments.yaml"
PUBLIC = ROOT / "brand-wizard-app" / "public"
BRAND_BUNDLES = ROOT / "brand-wizard-app" / "brands"

LANE_SUFFIX = re.compile(r"_(en_us|es_us|es_es|pt_br|zh_tw|zh_hk|zh_cn|zh_sg|ja_jp|ko_kr)$")
EMAIL_RE = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
SENSITIVE_KEYS = {"email", "phone", "secret", "token", "credential", "password"}


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise AssertionError(f"missing JSON: {path.relative_to(ROOT)}")
    except json.JSONDecodeError as exc:
        raise AssertionError(f"invalid JSON {path.relative_to(ROOT)}: {exc}") from exc


def load_yaml(path: Path) -> Any:
    try:
        text = path.read_text(encoding="utf-8")
        if yaml is not None:
            return yaml.safe_load(text) or {}
        return simple_yaml_load(text)
    except FileNotFoundError:
        raise AssertionError(f"missing YAML: {path.relative_to(ROOT)}")
    except Exception as exc:
        raise AssertionError(f"invalid YAML {path.relative_to(ROOT)}: {exc}") from exc


def simple_yaml_load(text: str) -> dict[str, Any]:
    """Tiny YAML subset parser for nested key/value maps used by public assignment files."""
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.strip()
        if ":" not in line:
            raise ValueError(f"unsupported YAML line: {line!r}")
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        if not stack:
            raise ValueError(f"bad indentation near {key!r}")
        parent = stack[-1][1]
        if value == "":
            child: dict[str, Any] = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = parse_scalar(value)
    return root


def parse_scalar(value: str) -> Any:
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    lower = value.lower()
    if lower in {"null", "none", "~"}:
        return None
    if lower == "true":
        return True
    if lower == "false":
        return False
    return value


def base_from_brand_id(brand_id: str, rec: dict[str, Any]) -> str:
    return str(rec.get("base_brand") or LANE_SUFFIX.sub("", brand_id)).strip()


def assert_public_safe_record(label: str, rec: Any, errors: list[str]) -> None:
    def walk(node: Any, path: str) -> None:
        if isinstance(node, dict):
            for key, val in node.items():
                lower = str(key).lower()
                if lower in SENSITIVE_KEYS:
                    errors.append(f"{label}: public-safe record contains sensitive key {path}.{key}")
                walk(val, f"{path}.{key}" if path else str(key))
        elif isinstance(node, list):
            for idx, val in enumerate(node):
                walk(val, f"{path}[{idx}]")
        elif isinstance(node, str) and EMAIL_RE.search(node):
            errors.append(f"{label}: public-safe record contains an email-like value at {path}")

    walk(rec, "")


def main() -> int:
    errors: list[str] = []
    assignments_doc = load_yaml(ASSIGNMENTS)
    assignments = assignments_doc.get("assignments") or {}
    if not isinstance(assignments, dict) or not assignments:
        errors.append("brand_director_assignments.yaml must contain at least one assignment")
        assignments = {}

    admin = load_json(PUBLIC / "brand_admin_brands.json")
    weekly = load_json(PUBLIC / "brand_admin_weekly_packets.json")
    setup = load_json(PUBLIC / "platform_setup_helper_brands.json")

    for brand_id, rec in sorted(assignments.items()):
        if not isinstance(rec, dict):
            errors.append(f"{brand_id}: assignment must be an object")
            continue
        name = str(rec.get("brand_director_name") or "").strip()
        director_id = str(rec.get("brand_director_id") or "").strip()
        base = base_from_brand_id(brand_id, rec)
        if not name or not director_id:
            errors.append(f"{brand_id}: assignment missing brand_director_name/id")
            continue
        assert_public_safe_record(f"{brand_id} assignment", rec, errors)

        admin_rec = admin.get(brand_id) if isinstance(admin, dict) else None
        if not isinstance(admin_rec, dict):
            errors.append(f"{brand_id}: missing from public brand_admin_brands.json")
        else:
            if admin_rec.get("brand_director_name") != name:
                errors.append(f"{brand_id}: brand_admin_brands.json has wrong director name")
            if admin_rec.get("brand_director_id") != director_id:
                errors.append(f"{brand_id}: brand_admin_brands.json has wrong director id")

        setup_rec = setup.get(brand_id) if isinstance(setup, dict) else None
        if isinstance(setup_rec, dict):
            if setup_rec.get("brand_director_name") != name:
                errors.append(f"{brand_id}: platform_setup_helper_brands.json has wrong director name")
            if setup_rec.get("brand_director_id") != director_id:
                errors.append(f"{brand_id}: platform_setup_helper_brands.json has wrong director id")

        bundle_path = BRAND_BUNDLES / f"{brand_id}.yaml"
        try:
            bundle = load_yaml(bundle_path)
        except AssertionError as exc:
            errors.append(str(exc))
            bundle = {}
        assert_public_safe_record(f"{brand_id} brand bundle", bundle, errors)
        bundle_director = bundle.get("brand_director") if isinstance(bundle, dict) else {}
        if not isinstance(bundle_director, dict) or bundle_director.get("name") != name:
            errors.append(f"{brand_id}: brand bundle missing matching brand_director.name")
        if not isinstance(bundle_director, dict) or bundle_director.get("id") != director_id:
            errors.append(f"{brand_id}: brand bundle missing matching brand_director.id")

        catalog_path = PUBLIC / "brand_catalogs" / f"{base}.json"
        try:
            catalog = load_json(catalog_path)
        except AssertionError as exc:
            errors.append(str(exc))
            catalog = {}
        books = catalog.get("books") if isinstance(catalog, dict) else None
        if not isinstance(books, list) or not books:
            errors.append(f"{brand_id}: missing non-empty public brand catalog {catalog_path.relative_to(ROOT)}")
        if isinstance(catalog, dict):
            if catalog.get("brand_director_name") != name:
                errors.append(f"{brand_id}: brand catalog has wrong director name")
            if catalog.get("brand_director_id") != director_id:
                errors.append(f"{brand_id}: brand catalog has wrong director id")

        delivery_path = PUBLIC / "brand_deliveries" / f"{base}.json"
        try:
            delivery = load_json(delivery_path)
        except AssertionError as exc:
            errors.append(str(exc))
            delivery = {}
        weeks = delivery.get("weeks") if isinstance(delivery, dict) else None
        if not isinstance(weeks, dict) or not weeks:
            errors.append(f"{brand_id}: missing non-empty delivery/ops feed {delivery_path.relative_to(ROOT)}")
            continue
        if delivery.get("brand_director_name") != name:
            errors.append(f"{brand_id}: delivery feed has wrong director name")
        if delivery.get("brand_director_id") != director_id:
            errors.append(f"{brand_id}: delivery feed has wrong director id")

        production_ready = delivery.get("production_files_ready") is True
        if production_ready:
            if delivery.get("delivery_status") != "production_files_live":
                errors.append(f"{brand_id}: production feed must declare delivery_status=production_files_live")
        else:
            if delivery.get("delivery_status") != "catalog_ready_production_files_pending":
                errors.append(f"{brand_id}: catalog-only delivery feed must declare production files pending")
            has_catalog_queue = any(
                isinstance(plats, dict)
                and isinstance(plats.get("catalog_metadata"), list)
                and len(plats.get("catalog_metadata") or []) > 0
                for plats in weeks.values()
            )
            if not has_catalog_queue:
                errors.append(f"{brand_id}: catalog-only delivery feed must include catalog_metadata rows")
            blocked = (weekly.get("blocked") or {}).get(brand_id) if isinstance(weekly, dict) else None
            reason = str((blocked or {}).get("reason") or "").lower() if isinstance(blocked, dict) else ""
            if "production files pending" not in reason:
                errors.append(f"{brand_id}: weekly packet bridge must say production files pending when not production-ready")

    if errors:
        print("validate_brand_director_live_readiness.py: FAILED", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1
    print("validate_brand_director_live_readiness.py: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
