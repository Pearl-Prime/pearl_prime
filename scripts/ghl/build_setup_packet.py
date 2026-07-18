#!/usr/bin/env python3
"""GHL admin setup packet generator (no live writes, no secrets).

Authority:
  docs/specs/GHL_YAML_SUBACCOUNT_SYNC_V1_SPEC.md   (PR #5687)
  docs/ghl/GHL_YAML_SYNC_FIELD_MAP.md              (PR #5690)

Emits, per (brand_id, locale), a human PACKET.md + machine packet.json carrying:
brand name, admin/person, expected tags, custom fields, channel list, sample
payload, funnel/freebie URLs, and the webhook ENV NAME.

HARD RULE: the webhook URL VALUE never appears in a packet. Only the env var
NAME (e.g. PHOENIX_GHL_FUNNEL_WEBHOOK_WAYSTREAM) is carried. Any value that
looks like a secret or signed URL is blocked and redacted before write.

Usage:
  PYTHONPATH=. python3 scripts/ghl/build_setup_packet.py --brand stabilizer_en_us
  PYTHONPATH=. python3 scripts/ghl/build_setup_packet.py --all-ghl-enabled --out-dir artifacts/ghl/setup_packets_20260715
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.ghl.yaml_sync_inputs import (  # noqa: E402
    FIELD_MAP,
    FIELD_MAP_VERSION,
    PILOT_FIELD_ORDER,
    SCHEMA_VERSION,
    Manifest,
    ManifestRow,
    Registry,
    RegistryRow,
    load_manifest,
    load_registry,
    looks_secret,
    redact,
    redact_location_id,
    resolve_wizard,
    utc_now_iso,
    wizard_yaml_paths,
)
from scripts.ghl.yaml_sync_dry_run import _rel, build_dry_run  # noqa: E402

MODE = "setup_packet_dry_run"
READY = "READY_FOR_ADMIN_REVIEW"
BLOCKED = "BLOCKED"

# Non-PII placeholder payload. example.invalid is reserved by RFC 2606.
SAMPLE_LEAD_EMAIL = "sample.lead@example.invalid"


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data if isinstance(data, dict) else {}


def _expected_tags(root: Path, topic: str | None = None) -> dict[str, Any]:
    seg = _load_yaml(root / "config" / "freebies" / "quiz_segment_map.yaml")
    topic_tags = seg.get("topic_default_tags") or {}
    bands = seg.get("score_bands") or {}
    out: dict[str, Any] = {
        "source": "config/freebies/quiz_segment_map.yaml",
        "score_band_tags": sorted({str(v.get("tag")) for v in bands.values() if isinstance(v, dict) and v.get("tag")}),
        "preferred_format_tags": sorted(str(v) for v in (seg.get("preferred_format_tags") or {}).values()),
        "readiness_tags": sorted(str(v) for v in (seg.get("readiness_tags") or {}).values()),
    }
    if topic:
        out["topic_default_tags"] = {topic: list(topic_tags.get(topic) or [])}
    else:
        out["topic_default_tags"] = {str(k): list(v or []) for k, v in topic_tags.items()}
    return out


def _funnel_pages(root: Path) -> list[dict[str, Any]]:
    cap = _load_yaml(root / "config" / "freebies" / "ghl_funnel_capture.yaml")
    pages = cap.get("funnel_pages") or []
    return [p for p in pages if isinstance(p, dict)]


def _funnel_urls(root: Path, funnel_base_url: str | None) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for p in _funnel_pages(root):
        slug = p.get("funnel_slug")
        url = f"{funnel_base_url.rstrip('/')}/{slug}/" if funnel_base_url and slug else None
        out.append(
            {
                "topic": p.get("topic"),
                "funnel_slug": slug,
                "quiz_id": p.get("quiz_id"),
                "capture_type": p.get("capture_type"),
                "tags": list(p.get("tags") or []),
                "url": redact(url),
                "url_status": "derived_from_manifest_funnel_base_url" if url else "unresolved_missing_funnel_base_url",
            }
        )
    return out


def _sample_payload(root: Path) -> dict[str, Any]:
    seg = _load_yaml(root / "config" / "freebies" / "quiz_segment_map.yaml")
    fields = list((seg.get("webhook") or {}).get("payload_fields") or [])
    example = {
        "email": SAMPLE_LEAD_EMAIL,
        "first_name": "Sample",
        "quiz_id": "capacity_assessment",
        "topic": "burnout",
        "score": 7,
        "score_band": "medium",
        "answers_json": '{"q1":"b","q2":"c"}',
        "funnel_slug": "burnout-energy-audit",
    }
    return {
        "transport": "GHL Automation -> Inbound Webhook (operator-owned URL)",
        "payload_fields": fields,
        "example": {k: example.get(k) for k in fields} if fields else example,
        "note": "Placeholder values only. No real contact data. Map JSON keys to GHL custom field UUIDs, not string ids.",
    }


def _channels(root: Path, row: RegistryRow | None, mrow: ManifestRow | None, registry: Registry) -> list[dict[str, Any]]:
    slots = _load_yaml(root / "config" / "marketing" / "ghl_email_slot_rules.yaml")
    defaults_by_type = slots.get("defaults_by_content_type") or {}
    feed_url = mrow.get("feed_url") if mrow else None
    funnel_base = mrow.get("funnel_base_url") if mrow else None
    shop_base = (row.shop_base if row else None) or registry.defaults.get("shop_base")
    return [
        {
            "channel": "weekly_marketing_feed",
            "kind": "r2_public_json",
            "target": redact(feed_url),
            "status": "resolved" if feed_url else "unresolved_missing_manifest_row",
            "note": "Existing proof-loop feed connector remains authority; no presigned URLs.",
        },
        {
            "channel": "freebie_funnel_pages",
            "kind": "cloudflare_pages",
            "target": redact(funnel_base),
            "status": "resolved" if funnel_base else "unresolved_missing_manifest_row",
            "note": f"{len(_funnel_pages(root))} interactive TOF landings (config/freebies/ghl_funnel_capture.yaml).",
        },
        {
            "channel": "inbound_webhook_capture",
            "kind": "ghl_inbound_webhook",
            "target": None,
            "status": "env_name_only",
            "note": "URL value is operator-owned and never stored in this repo. See webhook.env_name.",
        },
        {
            "channel": "email_automation",
            "kind": "ghl_workflow",
            "target": None,
            "status": "manual_ghl_admin",
            "note": f"Email slots: {sorted(set(str(v) for v in defaults_by_type.values()))} "
            "(config/marketing/ghl_email_slot_rules.yaml). GHL admin owns workflows.",
        },
        {
            "channel": "shop",
            "kind": "storefront",
            "target": redact(shop_base),
            "status": "resolved" if shop_base else "unresolved",
            "note": "Offer/CTA URLs flow through the existing feed, not YAML sync.",
        },
    ]


def build_packet(
    brand_id: str,
    *,
    repo_root: Path | None = None,
    registry_path: Path | None = None,
    manifest_path: Path | None = None,
    wizard_dir: Path | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Build one brand's setup packet. Always truth-labels readiness + blockers."""
    root = Path(repo_root or REPO_ROOT).resolve()
    registry = load_registry(registry_path or (root / "config" / "marketing" / "brand_marketing_registry.yaml"))
    manifest = load_manifest(manifest_path or (root / "docs" / "handoffs" / "ghl_location_manifest.example.tsv"))
    wdir = Path(wizard_dir or (root / "brand-wizard-app" / "brands"))
    now = generated_at or utc_now_iso()

    row = next((r for r in registry.rows if r.brand_id == brand_id), None)
    wizard = resolve_wizard(brand_id, repo_root=root, wizard_dir=wdir)
    locale = row.locale if row else str(((wizard.doc.get("wizard_core") or {}) or {}).get("lane") or registry.defaults.get("locale") or "en_US")

    mrows = manifest.rows_for(brand_id, locale)
    mrow = mrows[0] if len(mrows) == 1 else None

    blockers: list[str] = []
    if not wizard.exists:
        blockers.append(f"blocked_missing_active_yaml: no brand-wizard-app/brands/{brand_id}.yaml on this checkout")
    elif not wizard.active:
        blockers.append(f"blocked_inactive_yaml: {wizard.inactive_reason}")
    if row is None:
        blockers.append(f"blocked_missing_registry_row: {brand_id} absent from {_rel(registry.path, root)}")
    elif not row.ghl_enabled:
        blockers.append(f"blocked_ghl_disabled: registry row {brand_id} has ghl_enabled: false")
    if not mrows:
        blockers.append(f"blocked_missing_manifest_row: no row for {brand_id}/{locale} in {_rel(manifest.path, root)}")
    elif len(mrows) > 1:
        blockers.append(f"blocked_duplicate_manifest_row: {len(mrows)} rows for {brand_id}/{locale}")
    if mrow is not None and not mrow.location_id:
        blockers.append("blocked_missing_location_mapping: manifest row has no location_id")
    if manifest.missing_scale_columns:
        blockers.append(
            "blocked_manifest_missing_scale_columns: " + ", ".join(manifest.missing_scale_columns)
        )

    webhook_env = (row.webhook_env if row else None) or (mrow.get("webhook_env") if mrow else None)
    if webhook_env and looks_secret(webhook_env):
        blockers.append("blocked_secret_like_value: webhook_env carries a URL/token instead of an env var NAME")
        webhook_env = None
    if not webhook_env:
        blockers.append("blocked_missing_webhook_env_name: no webhook env var NAME resolved")

    director = wizard.doc.get("brand_director") or {}
    director = director if isinstance(director, dict) else {}

    display_name = (row.display_name if row else None) or wizard.doc.get("display_name") or wizard.doc.get("display_brand")

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "mode": MODE,
        "live_writes": False,
        "generated_at": now,
        "field_map_version": FIELD_MAP_VERSION,
        "readiness": BLOCKED if blockers else READY,
        "blockers": blockers,
        "brand": {
            "brand_id": brand_id,
            "locale": locale,
            "display_name": display_name,
            "registry_display_name": row.display_name if row else None,
            "wizard_display_name": wizard.doc.get("display_name") or wizard.doc.get("display_brand"),
            "wizard_yaml_path": _rel(wizard.path, root) if wizard.exists else None,
            "wizard_active": wizard.active,
            "wizard_inactive_reason": wizard.inactive_reason or None,
            "rollout_phase": row.rollout_phase if row else None,
            "ghl_enabled": bool(row.ghl_enabled) if row else False,
            "default_persona": row.default_persona if row else None,
        },
        "admin": {
            "brand_director_name": director.get("name"),
            "brand_director_id": director.get("id"),
            "brand_director_status": director.get("status"),
            "source": "brand-wizard YAML brand_director" if director else "unresolved",
            "ghl_admin_action": "Review this packet, then confirm/return the GHL location_id. Phoenix never creates sub-accounts.",
        },
        "ghl_target": {
            "location_id": redact_location_id(mrow.location_id) if (mrow and mrow.location_id) else None,
            "location_id_redacted": True,
            "location_name": mrow.get("location_name") if mrow else None,
            "manifest_row_id": mrow.row_id if mrow else None,
            "manifest_path": _rel(manifest.path, root),
            "registry_path": _rel(registry.path, root),
            "policy": "update-only; missing sub-account is blocked, never created (spec: Missing Sub-Account Policy)",
        },
        "custom_fields": {
            "phoenix_custom_values": [
                {
                    "name": fs.name,
                    "safety_class": fs.safety_class,
                    "source": f"{fs.source_kind}:{fs.source_key}",
                    "live_write_allowed": fs.live_write_allowed,
                    "requires_operator_approval": fs.requires_operator_approval,
                    "note": fs.note,
                }
                for fs in FIELD_MAP
            ],
            "pilot_field_order": list(PILOT_FIELD_ORDER),
            "quiz_inbound_custom_fields": sorted(
                str(v) for v in (_load_yaml(root / "config" / "freebies" / "quiz_segment_map.yaml").get("ghl_custom_fields") or {}).values()
            ),
            "note": "Custom fields are read-only in V1. Inbound quiz fields are existing webhook mapping, not YAML sync.",
        },
        "expected_tags": _expected_tags(root),
        "channels": _channels(root, row, mrow, registry),
        "funnel_urls": _funnel_urls(root, mrow.get("funnel_base_url") if mrow else None),
        "sample_payload": _sample_payload(root),
        "webhook": {
            "env_name": webhook_env,
            "url": None,
            "value_policy": "ENV NAME ONLY. The webhook URL value is a secret-class field: never committed, "
            "never printed, never synced to a GHL custom value. Operator sets it in the deploy env.",
        },
        "notes": [
            "LIVE_WRITES=none. This packet is a read-only handoff; it authorizes no GHL write.",
            "A BLOCKED packet must not be treated as a provisioning green light.",
        ],
    }
    _assert_packet_clean(packet)
    return packet


def _assert_packet_clean(packet: dict[str, Any]) -> None:
    """Fail closed if any secret-like value reached the packet."""
    offenders: list[str] = []

    def walk(node: Any, path: str) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                walk(v, f"{path}.{k}")
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{path}[{i}]")
        elif isinstance(node, str) and looks_secret(node):
            offenders.append(path)

    walk(packet, "packet")
    if offenders:
        raise ValueError(f"secret-like values reached the setup packet: {offenders}")


def render_markdown(packet: dict[str, Any]) -> str:
    b = packet["brand"]
    a = packet["admin"]
    t = packet["ghl_target"]
    lines: list[str] = []
    lines.append(f"# GHL Setup Packet — {b['display_name'] or b['brand_id']} ({b['locale']})")
    lines.append("")
    lines.append(f"- readiness: **{packet['readiness']}**")
    lines.append(f"- live_writes: **none** (this packet authorizes no GHL write)")
    lines.append(f"- generated_at: {packet['generated_at']}")
    lines.append(f"- field_map_version: {packet['field_map_version']}")
    lines.append("")
    if packet["blockers"]:
        lines.append("## Blockers (fail-closed)")
        lines.append("")
        for x in packet["blockers"]:
            lines.append(f"- {x}")
        lines.append("")
    lines.append("## Brand")
    lines.append("")
    lines.append(f"- brand_id: `{b['brand_id']}`")
    lines.append(f"- locale: `{b['locale']}`")
    lines.append(f"- display_name: {b['display_name'] or '_unresolved_'}")
    lines.append(f"- wizard YAML: `{b['wizard_yaml_path'] or 'ABSENT'}` (classifier-active: {b['wizard_active']})")
    if b["wizard_inactive_reason"]:
        lines.append(f"- wizard inactive reason: {b['wizard_inactive_reason']}")
    lines.append(f"- rollout_phase: {b['rollout_phase'] or '_unresolved_'} | ghl_enabled: {b['ghl_enabled']}")
    lines.append("")
    lines.append("## Admin / Person")
    lines.append("")
    lines.append(f"- brand director: {a['brand_director_name'] or '_unresolved_'} (`{a['brand_director_id'] or '-'}`)")
    lines.append(f"- status: {a['brand_director_status'] or '_unresolved_'}")
    lines.append(f"- action: {a['ghl_admin_action']}")
    lines.append("")
    lines.append("## GHL Target")
    lines.append("")
    lines.append(f"- location_id: `{t['location_id'] or 'UNMAPPED'}` (redacted)")
    lines.append(f"- location_name: {t['location_name'] or '_unresolved_'}")
    lines.append(f"- policy: {t['policy']}")
    lines.append("")
    lines.append("## Webhook")
    lines.append("")
    lines.append(f"- env NAME: `{packet['webhook']['env_name'] or 'UNRESOLVED'}`")
    lines.append(f"- URL value: **never stored here** — {packet['webhook']['value_policy']}")
    lines.append("")
    lines.append("## Custom Values (Phoenix-owned targets)")
    lines.append("")
    lines.append("| field | safety class | source | live write allowed |")
    lines.append("|---|---|---|---|")
    for f in packet["custom_fields"]["phoenix_custom_values"]:
        lines.append(f"| `{f['name']}` | {f['safety_class']} | `{f['source']}` | {f['live_write_allowed']} |")
    lines.append("")
    lines.append(f"Pilot field order: {', '.join(f'`{x}`' for x in packet['custom_fields']['pilot_field_order'])}")
    lines.append("")
    lines.append("## Channels")
    lines.append("")
    lines.append("| channel | kind | target | status |")
    lines.append("|---|---|---|---|")
    for c in packet["channels"]:
        lines.append(f"| {c['channel']} | {c['kind']} | {c['target'] or '—'} | {c['status']} |")
    lines.append("")
    lines.append("## Expected Tags")
    lines.append("")
    et = packet["expected_tags"]
    lines.append(f"- score bands: {', '.join(f'`{x}`' for x in et['score_band_tags'])}")
    lines.append(f"- preferred format: {', '.join(f'`{x}`' for x in et['preferred_format_tags'])}")
    lines.append(f"- readiness: {', '.join(f'`{x}`' for x in et['readiness_tags'])}")
    lines.append(f"- per-topic defaults: {len(et['topic_default_tags'])} topics (see packet.json)")
    lines.append("")
    lines.append("## Funnel / Freebie URLs")
    lines.append("")
    lines.append("| topic | slug | url | quiz_id |")
    lines.append("|---|---|---|---|")
    for u in packet["funnel_urls"]:
        lines.append(f"| {u['topic']} | `{u['funnel_slug']}` | {u['url'] or '_' + u['url_status'] + '_'} | `{u['quiz_id']}` |")
    lines.append("")
    lines.append("## Sample Inbound Payload")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps(packet["sample_payload"]["example"], indent=2))
    lines.append("```")
    lines.append("")
    lines.append(packet["sample_payload"]["note"])
    lines.append("")
    for n in packet["notes"]:
        lines.append(f"> {n}")
    return "\n".join(lines) + "\n"


def write_packet(packet: dict[str, Any], out_dir: Path) -> tuple[Path, Path]:
    b = packet["brand"]
    d = Path(out_dir) / f"{b['brand_id']}__{b['locale']}"
    d.mkdir(parents=True, exist_ok=True)
    jp = d / "packet.json"
    mp = d / "PACKET.md"
    jp.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    mp.write_text(render_markdown(packet), encoding="utf-8")
    return jp, mp


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="GHL admin setup packet generator (no live writes)")
    ap.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    ap.add_argument("--brand", action="append", default=None, help="brand_id (repeatable)")
    ap.add_argument("--all-ghl-enabled", action="store_true", help="every registry row with ghl_enabled: true")
    ap.add_argument("--all-wizard-yamls", action="store_true", help="every checked-in brand-wizard YAML")
    ap.add_argument("--registry", type=Path, default=None)
    ap.add_argument("--manifest", type=Path, default=None)
    ap.add_argument("--wizard-dir", type=Path, default=None)
    ap.add_argument("--generated-at", default=None)
    ap.add_argument("--out-dir", type=Path, default=None, help="write PACKET.md + packet.json per brand")
    ap.add_argument("--exit-zero-on-blocked", action="store_true")
    args = ap.parse_args(argv)

    root = Path(args.repo_root).resolve()
    brands: list[str] = list(args.brand or [])
    if args.all_ghl_enabled:
        registry = load_registry(args.registry or (root / "config" / "marketing" / "brand_marketing_registry.yaml"))
        brands.extend(r.brand_id for r in registry.ghl_enabled_rows())
    if args.all_wizard_yamls:
        brands.extend(wizard_yaml_paths(args.wizard_dir or (root / "brand-wizard-app" / "brands")))
    brands = sorted(dict.fromkeys(brands))
    if not brands:
        ap.error("no brands selected: pass --brand, --all-ghl-enabled, or --all-wizard-yamls")

    blocked = 0
    for bid in brands:
        packet = build_packet(
            bid,
            repo_root=root,
            registry_path=args.registry,
            manifest_path=args.manifest,
            wizard_dir=args.wizard_dir,
            generated_at=args.generated_at,
        )
        if packet["readiness"] == BLOCKED:
            blocked += 1
        if args.out_dir:
            jp, mp = write_packet(packet, args.out_dir)
            print(f"{packet['readiness']:<22} {bid:<24} -> {mp}", file=sys.stderr)
        else:
            print(render_markdown(packet))

    if args.out_dir:
        print(f"\n{len(brands)} packet(s), {blocked} BLOCKED, live_writes=none", file=sys.stderr)
    if blocked and not args.exit_zero_on_blocked:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
