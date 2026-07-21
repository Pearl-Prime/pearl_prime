#!/usr/bin/env python3
"""Dry-run desired-state diff: Phoenix brand YAML + marketing registry -> GHL.

Authority:
  docs/specs/GHL_YAML_SUBACCOUNT_SYNC_V1_SPEC.md   (PR #5687)
  docs/ghl/GHL_YAML_SYNC_FIELD_MAP.md              (PR #5690)

LIVE WRITES: none. This tool has no GHL client, makes no network calls, and
carries no credential reads. It joins read-only repo inputs with an optional
read-only current-state snapshot fixture and prints/writes a desired-state diff.

Fail-closed: the default decision is ``blocked``. A field only reaches
``update``/``create``/``no_op`` when the full join resolves 1:1:1 and a snapshot
proves the current value.

Usage:
  PYTHONPATH=. python3 scripts/ghl/yaml_sync_dry_run.py
  PYTHONPATH=. python3 scripts/ghl/yaml_sync_dry_run.py --out artifacts/ghl/.../diff.json
  PYTHONPATH=. python3 scripts/ghl/yaml_sync_dry_run.py --snapshot tests/fixtures/ghl/snapshot_example.json
  PYTHONPATH=. python3 scripts/ghl/yaml_sync_dry_run.py --brand way_stream_sanctuary --format table
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.ghl.yaml_sync_inputs import (  # noqa: E402
    DEFAULT_MANIFEST_PATH,
    DEFAULT_REGISTRY_PATH,
    FIELD_MAP,
    FIELD_MAP_VERSION,
    MANUAL_GHL_ADMIN,
    SCHEMA_VERSION,
    Manifest,
    ManifestRow,
    Registry,
    RegistryRow,
    Snapshot,
    WizardYaml,
    blob_sha_of,
    dotted_get,
    load_manifest,
    load_registry,
    load_snapshot,
    looks_secret,
    redact,
    redact_location_id,
    resolve_wizard,
    utc_now_iso,
    wizard_yaml_paths,
)

MODE = "dry_run_only"
LIVE_WRITES = False

# Blocked reason codes (spec "Diff Semantics" + "Missing Sub-Account Policy").
BLOCKED_MISSING_ACTIVE_YAML = "blocked_missing_active_yaml"
BLOCKED_INACTIVE_YAML = "blocked_inactive_yaml"
BLOCKED_MISSING_MANIFEST_ROW = "blocked_missing_manifest_row"
BLOCKED_DUPLICATE_MANIFEST_ROW = "blocked_duplicate_manifest_row"
BLOCKED_MISSING_LOCATION_MAPPING = "blocked_missing_location_mapping"
BLOCKED_DUPLICATE_LOCATION_ID = "blocked_duplicate_location_id"
BLOCKED_LOCATION_NOT_FOUND = "blocked_location_not_found"
BLOCKED_MISSING_SNAPSHOT = "blocked_missing_snapshot"
BLOCKED_MISSING_CUSTOM_VALUE_ID = "blocked_missing_custom_value_id"
BLOCKED_NON_PHOENIX_OWNED_TARGET = "blocked_non_phoenix_owned_target"
BLOCKED_SECRET_LIKE_VALUE = "blocked_secret_like_value"
BLOCKED_MISSING_SOURCE_VALUE = "blocked_missing_source_value"
BLOCKED_MISMATCHED_LOCATION_NAME = "blocked_mismatched_location_name"

PHOENIX_PREFIX = "phoenix_"


def _repo_head_sha(repo_root: Path) -> str | None:
    try:
        out = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        sha = out.stdout.strip()
        return sha or None
    except (OSError, subprocess.SubprocessError):
        return None


def _origin_main_sha(repo_root: Path) -> str | None:
    try:
        out = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "origin/main"],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        sha = out.stdout.strip()
        return sha or None
    except (OSError, subprocess.SubprocessError):
        return None


def _desired_value(
    spec_name: str,
    *,
    row: RegistryRow,
    manifest_row: ManifestRow | None,
    wizard: WizardYaml,
    sync_sha: str | None,
    sync_at: str,
) -> Any:
    fs = next(f for f in FIELD_MAP if f.name == spec_name)
    if fs.source_kind == "registry":
        if fs.source_key == "brand_id":
            return row.brand_id
        if fs.source_key == "locale":
            return row.locale
        if fs.source_key == "display_name":
            # Field map: prefer registry display name when a GHL pilot row exists.
            return row.display_name or dotted_get(wizard.doc, "display_name")
        if fs.source_key == "rollout_phase":
            return row.rollout_phase or (manifest_row.get("rollout_phase") if manifest_row else None)
        return None
    if fs.source_kind == "manifest":
        return manifest_row.get(fs.source_key) if manifest_row else None
    if fs.source_kind == "wizard":
        return dotted_get(wizard.doc, fs.source_key)
    if fs.source_kind == "engine":
        return sync_sha if fs.source_key == "sync_sha" else sync_at
    return None


def _field_record(
    spec_name: str,
    *,
    desired: Any,
    current_entry: dict[str, Any] | None,
) -> dict[str, Any]:
    fs = next(f for f in FIELD_MAP if f.name == spec_name)
    rec: dict[str, Any] = {
        "field": fs.name,
        "source": f"{fs.source_kind}:{fs.source_key}",
        "safety_class": fs.safety_class,
        "live_write_allowed": fs.live_write_allowed,
        "requires_operator_approval": fs.requires_operator_approval,
        "decision": "blocked",
        "reason": None,
        "before": None,
        "after": None,
        "rollback_note": None,
        "note": fs.note,
    }

    # Guard 1: a Phoenix-owned target must be phoenix_-prefixed.
    if not fs.name.startswith(PHOENIX_PREFIX):
        rec["reason"] = BLOCKED_NON_PHOENIX_OWNED_TARGET
        return rec

    # Guard 2: never move a secret-like value into GHL, never print it.
    if looks_secret(desired):
        rec["reason"] = BLOCKED_SECRET_LIKE_VALUE
        rec["after"] = redact(desired)
        return rec

    if desired is None or (isinstance(desired, str) and not desired.strip()):
        rec["reason"] = BLOCKED_MISSING_SOURCE_VALUE
        return rec

    rec["after"] = redact(desired)

    if current_entry is None:
        # Target custom value absent -> propose create only; live create needs approval.
        rec["decision"] = "create"
        rec["reason"] = "target_custom_value_absent_create_proposed_only"
        rec["rollback_note"] = "No-op rollback: proposed create was never executed (dry-run)."
        return rec

    current_value = current_entry.get("value")
    if looks_secret(current_value):
        rec["decision"] = "blocked"
        rec["reason"] = BLOCKED_SECRET_LIKE_VALUE
        rec["before"] = redact(current_value)
        return rec

    rec["before"] = redact(current_value)

    if not current_entry.get("id"):
        rec["decision"] = "blocked"
        rec["reason"] = BLOCKED_MISSING_CUSTOM_VALUE_ID
        return rec

    if str(current_value) == str(desired):
        rec["decision"] = "no_op"
        rec["reason"] = None
        rec["rollback_note"] = "No change proposed."
        return rec

    rec["decision"] = "update"
    rec["rollback_note"] = f"Restore custom value {current_entry.get('id')} to prior value on rollback."
    if fs.safety_class == MANUAL_GHL_ADMIN:
        rec["reason"] = "manual_ghl_admin_field_dry_run_only"
    return rec


def _blocked_record(
    row: RegistryRow,
    reason: str,
    *,
    registry_path: str,
    manifest_path: str,
    source_yaml_path: str | None = None,
    detail: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rec: dict[str, Any] = {
        "brand_id": row.brand_id,
        "locale": row.locale,
        "decision": "blocked",
        "reason": reason,
        "registry_path": registry_path,
        "manifest_path": manifest_path,
        "source_yaml_path": source_yaml_path,
        "target_location_id": None,
        "fields": [],
    }
    if detail:
        rec["detail"] = detail
    if extra:
        rec.update(extra)
    return rec


def build_dry_run(
    repo_root: Path | None = None,
    *,
    registry_path: Path | None = None,
    manifest_path: Path | None = None,
    snapshot_path: Path | None = None,
    wizard_dir: Path | None = None,
    brand_filter: str | None = None,
    sync_sha: str | None = None,
    generated_at: str | None = None,
    reveal_location_ids: bool = False,
) -> dict[str, Any]:
    """Produce the desired-state diff document. No API calls, no writes."""
    root = Path(repo_root or REPO_ROOT).resolve()
    reg_path = Path(registry_path or (root / "config" / "marketing" / "brand_marketing_registry.yaml"))
    man_path = Path(manifest_path or (root / "docs" / "handoffs" / "ghl_location_manifest.example.tsv"))
    wdir = Path(wizard_dir or (root / "brand-wizard-app" / "brands"))

    registry: Registry = load_registry(reg_path)
    manifest: Manifest = load_manifest(man_path)
    snapshot: Snapshot | None = load_snapshot(snapshot_path)

    reg_rel = _rel(reg_path, root)
    man_rel = _rel(man_path, root)

    now = generated_at or utc_now_iso()
    head_sha = sync_sha or _repo_head_sha(root)

    checked_in = wizard_yaml_paths(wdir)
    active_ids: list[str] = []
    for bid in checked_in:
        w = resolve_wizard(bid, repo_root=root, wizard_dir=wdir)
        if w.active:
            active_ids.append(bid)

    rows = [r for r in registry.ghl_enabled_rows() if brand_filter in (None, r.brand_id)]

    # Duplicate location ids across the manifest are a hard block (spec: mismatched/duplicate mapping).
    loc_counts: dict[str, int] = {}
    for mrow in manifest.rows:
        lid = mrow.location_id
        if lid:
            loc_counts[lid] = loc_counts.get(lid, 0) + 1

    records: list[dict[str, Any]] = []
    for row in rows:
        wizard = resolve_wizard(row.brand_id, repo_root=root, wizard_dir=wdir)

        # 1. Active wizard YAML (spec "Source Eligibility") -- checked first.
        if not wizard.exists:
            records.append(_blocked_record(row, BLOCKED_MISSING_ACTIVE_YAML, registry_path=reg_rel, manifest_path=man_rel))
            continue
        if not wizard.active:
            records.append(
                _blocked_record(
                    row,
                    BLOCKED_INACTIVE_YAML,
                    registry_path=reg_rel,
                    manifest_path=man_rel,
                    source_yaml_path=_rel(wizard.path, root),
                    detail=wizard.inactive_reason,
                    extra={"source_yaml_blob_sha": blob_sha_of(wizard.path)},
                )
            )
            continue

        yaml_rel = _rel(wizard.path, root)
        blob_sha = blob_sha_of(wizard.path)
        base_extra = {"source_yaml_blob_sha": blob_sha, "source_commit_sha": head_sha}

        # 2. Exactly one manifest row.
        mrows = manifest.rows_for(row.brand_id, row.locale)
        if not mrows:
            records.append(
                _blocked_record(
                    row, BLOCKED_MISSING_MANIFEST_ROW, registry_path=reg_rel, manifest_path=man_rel,
                    source_yaml_path=yaml_rel, extra=base_extra,
                )
            )
            continue
        if len(mrows) > 1:
            records.append(
                _blocked_record(
                    row, BLOCKED_DUPLICATE_MANIFEST_ROW, registry_path=reg_rel, manifest_path=man_rel,
                    source_yaml_path=yaml_rel,
                    detail=f"{len(mrows)} manifest rows for {row.brand_id}/{row.locale}",
                    extra=base_extra,
                )
            )
            continue
        mrow = mrows[0]
        base_extra["manifest_row_id"] = mrow.row_id

        # 3. Location id must be mapped (update-only policy; never create sub-accounts).
        location_id = mrow.location_id
        if not location_id:
            records.append(
                _blocked_record(
                    row, BLOCKED_MISSING_LOCATION_MAPPING, registry_path=reg_rel, manifest_path=man_rel,
                    source_yaml_path=yaml_rel,
                    detail=(
                        "manifest has no location_id column/value; V1 is update-only and never creates sub-accounts"
                        if "location_id" not in manifest.header
                        else "manifest location_id is empty"
                    ),
                    extra=base_extra,
                )
            )
            continue
        if loc_counts.get(location_id, 0) > 1:
            records.append(
                _blocked_record(
                    row, BLOCKED_DUPLICATE_LOCATION_ID, registry_path=reg_rel, manifest_path=man_rel,
                    source_yaml_path=yaml_rel, detail="location_id appears on multiple manifest rows",
                    extra=base_extra,
                )
            )
            continue

        loc_out = location_id if reveal_location_ids else redact_location_id(location_id)
        base_extra["target_location_id_redacted"] = not reveal_location_ids

        # 4. Current-state snapshot must prove the location.
        if snapshot is None:
            rec = _blocked_record(
                row, BLOCKED_MISSING_SNAPSHOT, registry_path=reg_rel, manifest_path=man_rel,
                source_yaml_path=yaml_rel,
                detail="no read-only current-state snapshot supplied; cannot diff without proving current values",
                extra=base_extra,
            )
            rec["target_location_id"] = loc_out
            records.append(rec)
            continue

        loc = snapshot.location(location_id)
        if loc is None:
            rec = _blocked_record(
                row, BLOCKED_LOCATION_NOT_FOUND, registry_path=reg_rel, manifest_path=man_rel,
                source_yaml_path=yaml_rel,
                detail="location_id not present in snapshot; V1 never creates sub-accounts",
                extra=base_extra,
            )
            rec["target_location_id"] = loc_out
            records.append(rec)
            continue

        # 5. Manifest location_name must match the snapshot's location name.
        manifest_name = mrow.get("location_name")
        snap_name = _str(loc.get("name"))
        if manifest_name and snap_name and manifest_name != snap_name:
            rec = _blocked_record(
                row, BLOCKED_MISMATCHED_LOCATION_NAME, registry_path=reg_rel, manifest_path=man_rel,
                source_yaml_path=yaml_rel,
                detail=f"manifest location_name {manifest_name!r} != GHL location name {snap_name!r}",
                extra=base_extra,
            )
            rec["target_location_id"] = loc_out
            records.append(rec)
            continue

        # 6. Per-field desired-state diff.
        current_values = loc.get("custom_values") or {}
        fields: list[dict[str, Any]] = []
        for fs in FIELD_MAP:
            desired = _desired_value(
                fs.name, row=row, manifest_row=mrow, wizard=wizard, sync_sha=head_sha, sync_at=now
            )
            entry = current_values.get(fs.name)
            entry = entry if isinstance(entry, dict) else None
            fields.append(_field_record(fs.name, desired=desired, current_entry=entry))

        decisions = {f["decision"] for f in fields}
        if "update" in decisions:
            row_decision = "update"
        elif "create" in decisions:
            row_decision = "create"
        elif decisions == {"no_op"}:
            row_decision = "no_op"
        else:
            row_decision = "blocked"

        rec = {
            "brand_id": row.brand_id,
            "locale": row.locale,
            "decision": row_decision,
            "reason": None if row_decision != "blocked" else "all_fields_blocked",
            "registry_path": reg_rel,
            "manifest_path": man_rel,
            "source_yaml_path": yaml_rel,
            "target_location_id": loc_out,
            "fields": fields,
        }
        rec.update(base_extra)
        records.append(rec)

    summary = _summarize(records, checked_in=len(checked_in), active=len(active_ids), rows=len(rows))
    notes = _notes(manifest, snapshot, active_ids, checked_in)

    doc: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "mode": MODE,
        "generated_at": now,
        "source_origin_main": _origin_main_sha(root),
        "source_commit_sha": head_sha,
        "field_map_version": FIELD_MAP_VERSION,
        "live_writes": LIVE_WRITES,
        "summary": summary,
        "records": records,
        "notes": notes,
    }
    return doc


def _summarize(records: list[dict[str, Any]], *, checked_in: int, active: int, rows: int) -> dict[str, Any]:
    field_decisions: list[str] = [f["decision"] for r in records for f in r.get("fields", [])]
    return {
        # Spec "Source Eligibility": eligible == passes active_brand_classifier.
        "eligible_brand_yamls": active,
        "checked_in_brand_yamls": checked_in,
        "active_brand_yamls": active,
        "ghl_enabled_registry_rows": rows,
        "updates": field_decisions.count("update"),
        "creates_proposed": field_decisions.count("create"),
        "no_ops": field_decisions.count("no_op"),
        "blocked": sum(1 for r in records if r["decision"] == "blocked"),
        "blocked_fields": field_decisions.count("blocked"),
    }


def _notes(manifest: Manifest, snapshot: Snapshot | None, active_ids: list[str], checked_in: dict[str, Path]) -> list[str]:
    notes = [
        "LIVE_WRITES=none. This tool has no GHL client and makes no network calls.",
        "Fail-closed: default decision is blocked; update/create/no_op requires a 1:1:1 "
        "wizard-YAML / registry-row / manifest-row join plus a read-only snapshot.",
    ]
    if not active_ids:
        notes.append(
            f"No classifier-active wizard YAML on this checkout: {len(checked_in)} file(s) present "
            f"({', '.join(sorted(checked_in)) or 'none'}), 0 pass scripts/brand/active_brand_classifier.py."
        )
    missing_cols = manifest.missing_scale_columns
    if missing_cols:
        notes.append(
            "Manifest is missing scale columns required by GHL_YAML_SYNC_FIELD_MAP "
            f"'Scale Manifest Columns': {', '.join(missing_cols)}."
        )
    if snapshot is None:
        notes.append("No current-state snapshot supplied; no field-level diff can be proven.")
    notes.append("Webhook URL values are never read, stored, or printed; only the env var NAME is carried.")
    return notes


def _rel(p: Path, root: Path) -> str:
    try:
        return str(Path(p).resolve().relative_to(Path(root).resolve()))
    except ValueError:
        return str(p)


def _str(v: Any) -> str | None:
    if v is None:
        return None
    s = str(v).strip()
    return s or None


def render_table(doc: dict[str, Any]) -> str:
    lines: list[str] = []
    s = doc["summary"]
    lines.append(f"GHL YAML sync dry-run  mode={doc['mode']}  live_writes={doc['live_writes']}")
    lines.append(f"field_map_version={doc['field_map_version']}  generated_at={doc['generated_at']}")
    lines.append(
        f"checked-in YAMLs={s['checked_in_brand_yamls']}  classifier-active={s['active_brand_yamls']}  "
        f"ghl_enabled rows={s['ghl_enabled_registry_rows']}"
    )
    lines.append(
        f"updates={s['updates']}  creates_proposed={s['creates_proposed']}  no_ops={s['no_ops']}  "
        f"blocked_rows={s['blocked']}  blocked_fields={s['blocked_fields']}"
    )
    lines.append("")
    lines.append(f"{'BRAND':<24} {'LOCALE':<7} {'DECISION':<9} REASON / DETAIL")
    lines.append("-" * 100)
    for r in doc["records"]:
        detail = r.get("detail") or ""
        reason = r.get("reason") or ""
        tail = f"{reason} {('- ' + detail) if detail else ''}".strip()
        lines.append(f"{r['brand_id']:<24} {r['locale']:<7} {r['decision']:<9} {tail}")
        for f in r.get("fields", []):
            flag = "!" if f["requires_operator_approval"] else " "
            lines.append(
                f"    {flag} {f['field']:<28} {f['decision']:<7} {f.get('reason') or ''}"
            )
    lines.append("")
    for n in doc["notes"]:
        lines.append(f"NOTE: {n}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="GHL YAML sub-account sync dry-run (no live writes)")
    ap.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    ap.add_argument("--registry", type=Path, default=None, help=f"default: {DEFAULT_REGISTRY_PATH}")
    ap.add_argument("--manifest", type=Path, default=None, help=f"default: {DEFAULT_MANIFEST_PATH}")
    ap.add_argument("--snapshot", type=Path, default=None, help="read-only current-state snapshot fixture JSON")
    ap.add_argument("--wizard-dir", type=Path, default=None)
    ap.add_argument("--brand", default=None, help="limit to one brand_id")
    ap.add_argument("--sync-sha", default=None, help="override the sync commit SHA")
    ap.add_argument("--generated-at", default=None, help="override the generated_at timestamp (determinism)")
    ap.add_argument("--out", type=Path, default=None, help="write the diff JSON here")
    ap.add_argument("--format", choices=("json", "table"), default="json")
    ap.add_argument(
        "--reveal-location-ids",
        action="store_true",
        help="print raw GHL location ids (local operator use only; never for committed artifacts)",
    )
    ap.add_argument(
        "--exit-zero-on-blocked",
        action="store_true",
        help="exit 0 even when rows are blocked (artifact generation); default fails closed with exit 2",
    )
    args = ap.parse_args(argv)

    doc = build_dry_run(
        args.repo_root,
        registry_path=args.registry,
        manifest_path=args.manifest,
        snapshot_path=args.snapshot,
        wizard_dir=args.wizard_dir,
        brand_filter=args.brand,
        sync_sha=args.sync_sha,
        generated_at=args.generated_at,
        reveal_location_ids=args.reveal_location_ids,
    )

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"wrote {args.out}", file=sys.stderr)

    print(render_table(doc) if args.format == "table" else json.dumps(doc, indent=2, ensure_ascii=False))

    blocked = doc["summary"]["blocked"]
    if blocked and not args.exit_zero_on_blocked:
        print(f"\nFAIL-CLOSED: {blocked} row(s) blocked. No live write is authorized.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
