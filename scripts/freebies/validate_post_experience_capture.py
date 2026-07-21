#!/usr/bin/env python3
"""Validate Waystream post-experience freebie capture contracts."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[2]
PLAN = REPO / "config/freebies/waystream_evergreen_campaign_plan.yaml"
QA_ROOT = REPO / "artifacts/qa/freebie_post_experience_capture_20260714"
PAGES_ROOT = REPO / "brand-wizard-app/public/free/way_stream_sanctuary"
OWNED_SCAN_ROOTS = [
    REPO / "brand-wizard-app/public/free/way_stream_sanctuary",
    REPO / "brand-wizard-app/public/free/js/phoenix_lead.js",
    REPO / "brand-wizard-app/public/free/js/phoenix_funnel.js",
    REPO / "config/freebies/report_delivery_channels.yaml",
    REPO / "config/freebies/report_unlock_copy.yaml",
    REPO / "config/freebies/freebie_report_templates.yaml",
    REPO / "config/freebies/report_delivery_templates.yaml",
    REPO / "docs/freebies",
    REPO / "docs/integrations",
    REPO / "docs/runbooks",
]

BANNED_CLAIMS = [
    "cure",
    "guaranteed transformation",
    "diagnose",
    "diagnosis",
    "treats anxiety",
    "medical advice",
    "financial guarantee",
]


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _plans() -> list[dict[str, Any]]:
    return sorted((_load_yaml(PLAN).get("plans") or []), key=lambda item: item["source_page_slug"])


def _scan_text_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root]
    if not root.exists():
        return []
    return [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in {".html", ".js", ".css", ".yaml", ".yml", ".md", ".json", ".py"}]


def _full_webhook_hits() -> list[str]:
    hits: list[str] = []
    pattern = re.compile(r"https://[^\s\"']*(?:hooks/|webhook-trigger)[^\s\"']*", re.I)
    for root in OWNED_SCAN_ROOTS:
        for path in _scan_text_files(root):
            text = path.read_text(encoding="utf-8", errors="ignore")
            if pattern.search(text):
                hits.append(str(path.relative_to(REPO)))
    return sorted(set(hits))


def _validate_pages(plans: list[dict[str, Any]], errors: list[str]) -> list[dict[str, Any]]:
    rows = []
    for plan in plans:
        slug = plan["source_page_slug"]
        path = PAGES_ROOT / slug / "index.html"
        if not path.exists():
            errors.append(f"missing page {slug}")
            continue
        text = path.read_text(encoding="utf-8")
        required = [
            'data-brand-id="way_stream_sanctuary"',
            f'data-topic="{plan["topic"]}"',
            f'data-funnel-slug="{slug}"',
            'data-post-experience-capture="1"',
            '<script src="/free/js/phoenix_lead.js"></script>',
            'phoenix_funnel.js',
            'phoenix_tool.css',
            'id="phoenix-evergreen-campaign-plan"',
        ]
        for needle in required:
            if needle not in text:
                errors.append(f"{slug} missing {needle}")
        if not re.search(r'data-ghl-webhook=""', text):
            errors.append(f"{slug} data-ghl-webhook must be empty")
        if "services.leadconnectorhq.com" in text or "webhook-trigger" in text:
            errors.append(f"{slug} exposes webhook URL")
        rows.append({"slug": slug, "ok": slug not in " ".join(errors)})
    return rows


def _validate_configs(plans: list[dict[str, Any]], errors: list[str]) -> None:
    channels = _load_yaml(REPO / "config/freebies/report_delivery_channels.yaml")
    if channels.get("default_order") != ["whatsapp", "telegram", "email"]:
        errors.append("default channel order mismatch")
    if channels.get("region_orders", {}).get("JP") != ["line", "messenger", "whatsapp", "telegram", "email"]:
        errors.append("JP channel order mismatch")
    templates = _load_yaml(REPO / "config/freebies/freebie_report_templates.yaml").get("reports") or {}
    unlock = _load_yaml(REPO / "config/freebies/report_unlock_copy.yaml").get("per_tool_promises") or {}
    for plan in plans:
        slug = plan["source_page_slug"]
        if slug not in templates:
            errors.append(f"missing report template {slug}")
        if slug not in unlock:
            errors.append(f"missing unlock copy {slug}")
        if not (REPO / f"config/freebies/report_specs/way_stream_sanctuary/{slug}.yaml").exists():
            errors.append(f"missing report spec {slug}")


def _validate_js(errors: list[str]) -> None:
    lead = (REPO / "brand-wizard-app/public/free/js/phoenix_lead.js").read_text(encoding="utf-8")
    funnel = (REPO / "brand-wizard-app/public/free/js/phoenix_funnel.js").read_text(encoding="utf-8")
    for field in [
        "delivery_channel",
        "delivery_address",
        "channel_consent",
        "report_id",
        "report_variant",
        "report_summary",
        "completed_at",
        "completion_duration_seconds",
        "ab_variant",
    ]:
        if field not in lead:
            errors.append(f"phoenix_lead.js missing {field}")
    for needle in ["initPostExperienceCapture", "markToolComplete", "report_offer_view", "PhoenixLead.captureReportUnlock"]:
        if needle not in funnel:
            errors.append(f"phoenix_funnel.js missing {needle}")


def _copy_lint(errors: list[str]) -> None:
    files = [
        REPO / "config/freebies/report_unlock_copy.yaml",
        REPO / "config/freebies/freebie_report_templates.yaml",
        REPO / "config/freebies/report_delivery_templates.yaml",
    ] + list((REPO / "config/freebies/report_specs/way_stream_sanctuary").glob("*.yaml"))
    for path in files:
        text = path.read_text(encoding="utf-8").lower()
        for phrase in BANNED_CLAIMS:
            if phrase in text:
                errors.append(f"banned claim phrase {phrase!r} in {path.relative_to(REPO)}")
        if "{{" in text or "}}" in text:
            errors.append(f"unresolved placeholder braces in {path.relative_to(REPO)}")


def _sample_reports(plans: list[dict[str, Any]], errors: list[str]) -> list[str]:
    samples: list[str] = []
    for slug in [plans[0]["source_page_slug"], plans[len(plans) // 2]["source_page_slug"], plans[-1]["source_page_slug"]]:
        out = QA_ROOT / "sample_reports" / f"{slug}.json"
        cmd = [
            sys.executable,
            "scripts/freebies/generate_freebie_report.py",
            "--slug",
            slug,
            "--answers-json",
            json.dumps([{"field": "sample", "value": "completed"}]),
            "--out",
            str(out),
        ]
        result = subprocess.run(cmd, cwd=REPO, text=True, capture_output=True)
        if result.returncode != 0:
            errors.append(f"sample report failed for {slug}: {result.stderr.strip()}")
        elif "{{" in out.read_text(encoding="utf-8"):
            errors.append(f"sample report placeholder in {slug}")
        else:
            samples.append(str(out.relative_to(REPO)))
    return samples


def main() -> int:
    QA_ROOT.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []
    plans = _plans()
    if len(plans) != 15:
        errors.append(f"expected 15 Waystream plans, found {len(plans)}")
    page_rows = _validate_pages(plans, errors)
    _validate_configs(plans, errors)
    _validate_js(errors)
    _copy_lint(errors)
    sample_paths = _sample_reports(plans, errors)
    secret_hits = _full_webhook_hits()
    if secret_hits:
        errors.append(f"full webhook URL exposure: {secret_hits}")
    report = {
        "ok": not errors,
        "page_count": len(plans),
        "pages": page_rows,
        "sample_reports": sample_paths,
        "secret_hits": secret_hits,
        "errors": errors,
    }
    (QA_ROOT / "contract_test_report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if errors:
        print(f"FAIL: post-experience capture validation failed; artifact={QA_ROOT / 'contract_test_report.json'}")
        for err in errors:
            print(f"- {err}")
        return 1
    print(f"OK: post-experience capture validation passed ({len(plans)}/15 pages); artifact={QA_ROOT / 'contract_test_report.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
