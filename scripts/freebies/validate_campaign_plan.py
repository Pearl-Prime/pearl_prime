#!/usr/bin/env python3
"""Validate and optionally sync evergreen freebie campaign plans."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parents[2]
DEFAULT_PLAN = REPO / "config/freebies/waystream_evergreen_campaign_plan.yaml"
PLAN_SCRIPT_ID = "phoenix-evergreen-campaign-plan"
FULL_GHL_WEBHOOK_RE = re.compile(
    r"https://(?:services|hooks)\.leadconnectorhq\.com/hooks/"
    r"[A-Za-z0-9]+/webhook-trigger/[A-Za-z0-9-]+"
)

BASE_REQUIRED = (
    "brand_id",
    "freebie_id",
    "quiz_id",
    "topic",
    "funnel_variant",
    "source_page_slug",
    "campaign_plan_id",
)
OPTIONAL_METADATA = (
    "locale",
    "archetype_id",
    "content_type",
    "fallback_allowed",
    "status",
)
EMAIL_REQUIRED = tuple(
    f"e{i}_{field}"
    for i in range(1, 10)
    for field in (
        "title",
        "url",
        "cta",
        "tool_name",
        "short_description",
        "benefit",
        "microcopy",
    )
)
SPECIAL_EMAIL_REQUIRED = (
    "e3_story_body",
    "e4_book_title",
    "e5_book1_title",
    "e5_book1_url",
    "e5_book1_note",
    "e5_book2_title",
    "e5_book2_url",
    "e5_book2_note",
    "e5_book3_title",
    "e5_book3_url",
    "e5_book3_note",
    "e6_book_title",
    "e7_bundle_title",
    "e8_last_chance_note",
)
BONUS_PRE_E3_REQUIRED = (
    "bonus_pre_e3_title",
    "bonus_pre_e3_url",
    "bonus_pre_e3_cta",
    "bonus_pre_e3_tool_name",
    "bonus_pre_e3_short_description",
    "bonus_pre_e3_benefit",
    "bonus_pre_e3_microcopy",
    "bonus_pre_e3_html_template",
    "bonus_pre_e3_send_if_welcome_depth_missing",
)
PAGE_PLAN_FIELDS = (
    BASE_REQUIRED
    + OPTIONAL_METADATA
    + EMAIL_REQUIRED
    + SPECIAL_EMAIL_REQUIRED
    + BONUS_PRE_E3_REQUIRED
)


class CampaignPageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.body_attrs: dict[str, str] = {}
        self.plan_json = ""
        self._capture_plan = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {k: v or "" for k, v in attrs}
        if tag.lower() == "body":
            self.body_attrs = attr_map
        if tag.lower() == "script" and attr_map.get("id") == PLAN_SCRIPT_ID:
            self._capture_plan = True

    def handle_data(self, data: str) -> None:
        if self._capture_plan:
            self.plan_json += data

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "script" and self._capture_plan:
            self._capture_plan = False


def _load_yaml(path: Path) -> dict[str, Any]:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _artifact_default(brand_id: str) -> Path:
    return REPO / "artifacts/freebies" / f"{brand_id}_campaign_plan_validation.json"


def _is_valid_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _campaign_payload(plan: dict[str, Any]) -> dict[str, Any]:
    return {field: plan.get(field) for field in PAGE_PLAN_FIELDS if field in plan}


def _parse_page(path: Path) -> tuple[dict[str, str], dict[str, Any] | None, str | None]:
    parser = CampaignPageParser()
    text = path.read_text(encoding="utf-8")
    parser.feed(text)
    if not parser.plan_json.strip():
        return parser.body_attrs, None, None
    try:
        return parser.body_attrs, json.loads(parser.plan_json), None
    except json.JSONDecodeError as exc:
        return parser.body_attrs, None, f"invalid embedded campaign JSON: {exc.msg}"


def _sync_page(path: Path, plan: dict[str, Any]) -> bool:
    text = path.read_text(encoding="utf-8")
    payload = json.dumps(_campaign_payload(plan), indent=2, sort_keys=True)
    block = (
        f'<script type="application/json" id="{PLAN_SCRIPT_ID}">\n'
        f"{payload}\n"
        "</script>"
    )
    pattern = re.compile(
        rf'<script\s+type="application/json"\s+id="{re.escape(PLAN_SCRIPT_ID)}">\s*'
        r".*?"
        r"\s*</script>",
        re.DOTALL,
    )
    if pattern.search(text):
        new_text = pattern.sub(lambda _match: block, text, count=1)
    else:
        marker = '<script src="/free/js/phoenix_lead.js"></script>'
        if marker in text:
            new_text = text.replace(marker, f"{block}\n{marker}", 1)
        else:
            new_text = text.replace("</body>", f"{block}\n</body>", 1)
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
        return True
    return False


def _scan_full_webhook_urls(paths: list[Path]) -> list[str]:
    files: list[str] = []
    for root in paths:
        if not root.exists():
            continue
        candidates = [root] if root.is_file() else [p for p in root.rglob("*") if p.is_file()]
        for path in candidates:
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            except OSError:
                continue
            if FULL_GHL_WEBHOOK_RE.search(text):
                files.append(str(path.relative_to(REPO)))
    return sorted(set(files))


def _validate(
    *,
    brand_id: str,
    plan_file: Path,
    artifact: Path,
    sync_pages: bool,
) -> tuple[bool, dict[str, Any]]:
    data = _load_yaml(plan_file)
    pages_root = REPO / "brand-wizard-app/public/free" / brand_id
    page_paths = sorted(pages_root.glob("*/index.html"))
    plans = data.get("plans") or []
    plans_by_slug = {str(plan.get("source_page_slug") or ""): plan for plan in plans}
    page_slugs = [path.parent.name for path in page_paths]

    report: dict[str, Any] = {
        "ok": False,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "brand_id": brand_id,
        "plan_file": str(plan_file.relative_to(REPO)),
        "campaign_model": data.get("campaign_model"),
        "expected_page_count": data.get("expected_page_count"),
        "pages_total": len(page_paths),
        "plans_total": len(plans),
        "pages_covered": sorted(set(page_slugs) & set(plans_by_slug)),
        "missing_campaign_plans": sorted(set(page_slugs) - set(plans_by_slug)),
        "missing_pages": sorted(set(plans_by_slug) - set(page_slugs)),
        "extra_pages": [],
        "invalid_plans": [],
        "invalid_urls": [],
        "page_context_mismatches": [],
        "pages_without_embedded_campaign_plan": [],
        "embedded_campaign_plan_mismatches": [],
        "secret_scan": {
            "roots": [
                "brand-wizard-app/public/free/way_stream_sanctuary",
                "docs/ghl",
                "docs/freebies",
                "docs/integrations",
                "docs/runbooks",
                "artifacts/coordination/handoffs",
                "artifacts/qa/freebie_post_experience_capture_20260714",
                "tests",
            ],
            "full_webhook_url_files": [],
        },
    }

    expected_page_count = data.get("expected_page_count")
    if expected_page_count is not None and len(page_paths) != int(expected_page_count):
        report["extra_pages"].append(
            f"expected {expected_page_count} pages, found {len(page_paths)}"
        )
    if data.get("brand_id") != brand_id:
        report["invalid_plans"].append(
            {"slug": None, "field": "brand_id", "reason": "top-level brand_id mismatch"}
        )
    if data.get("campaign_model") != "evergreen_form_submit":
        report["invalid_plans"].append(
            {"slug": None, "field": "campaign_model", "reason": "must be evergreen_form_submit"}
        )

    seen_ids: set[str] = set()
    for slug, plan in sorted(plans_by_slug.items()):
        if not slug:
            report["invalid_plans"].append(
                {"slug": slug, "field": "source_page_slug", "reason": "empty slug"}
            )
            continue
        campaign_plan_id = str(plan.get("campaign_plan_id") or "")
        if campaign_plan_id in seen_ids:
            report["invalid_plans"].append(
                {"slug": slug, "field": "campaign_plan_id", "reason": "duplicate"}
            )
        seen_ids.add(campaign_plan_id)
        for field in (
            BASE_REQUIRED
            + EMAIL_REQUIRED
            + SPECIAL_EMAIL_REQUIRED
            + BONUS_PRE_E3_REQUIRED
        ):
            value = plan.get(field)
            if value is None or str(value).strip() == "":
                report["invalid_plans"].append(
                    {"slug": slug, "field": field, "reason": "missing or empty"}
                )
        if plan.get("brand_id") != brand_id:
            report["invalid_plans"].append(
                {"slug": slug, "field": "brand_id", "reason": "plan brand_id mismatch"}
            )
        if plan.get("fallback_allowed") is not False:
            report["invalid_plans"].append(
                {"slug": slug, "field": "fallback_allowed", "reason": "must be false"}
            )
        for i in range(1, 10):
            field = f"e{i}_url"
            if not _is_valid_url(str(plan.get(field) or "")):
                report["invalid_urls"].append({"slug": slug, "field": field})
        for field in ("e5_book1_url", "e5_book2_url", "e5_book3_url"):
            if not _is_valid_url(str(plan.get(field) or "")):
                report["invalid_urls"].append({"slug": slug, "field": field})
        if not _is_valid_url(str(plan.get("bonus_pre_e3_url") or "")):
            report["invalid_urls"].append({"slug": slug, "field": "bonus_pre_e3_url"})
        if plan.get("bonus_pre_e3_send_if_welcome_depth_missing") is not True:
            report["invalid_plans"].append(
                {
                    "slug": slug,
                    "field": "bonus_pre_e3_send_if_welcome_depth_missing",
                    "reason": "must be true",
                }
            )
        template = REPO / str(plan.get("bonus_pre_e3_html_template") or "")
        if not template.is_file():
            report["invalid_plans"].append(
                {
                    "slug": slug,
                    "field": "bonus_pre_e3_html_template",
                    "reason": "template file missing",
                }
            )

    if sync_pages:
        for path in page_paths:
            slug = path.parent.name
            plan = plans_by_slug.get(slug)
            if not plan:
                continue
            if _sync_page(path, plan):
                print(f"synced {path.relative_to(REPO)}")

    for path in page_paths:
        slug = path.parent.name
        body_attrs, embedded, parse_error = _parse_page(path)
        plan = plans_by_slug.get(slug)
        rel = str(path.relative_to(REPO))
        if parse_error:
            report["embedded_campaign_plan_mismatches"].append(
                {"page": rel, "reason": parse_error}
            )
        if not embedded:
            report["pages_without_embedded_campaign_plan"].append(rel)
        elif plan and embedded != _campaign_payload(plan):
            report["embedded_campaign_plan_mismatches"].append(
                {"page": rel, "reason": "embedded plan does not match YAML source"}
            )
        if body_attrs.get("data-brand-id") != brand_id:
            report["page_context_mismatches"].append(
                {"page": rel, "field": "data-brand-id", "expected": brand_id}
            )
        if body_attrs.get("data-funnel-slug") != slug:
            report["page_context_mismatches"].append(
                {"page": rel, "field": "data-funnel-slug", "expected": slug}
            )
        if plan and body_attrs.get("data-topic") != plan.get("topic"):
            report["page_context_mismatches"].append(
                {"page": rel, "field": "data-topic", "expected": plan.get("topic")}
            )

    report["secret_scan"]["full_webhook_url_files"] = _scan_full_webhook_urls(
        [
            REPO / "brand-wizard-app/public/free/way_stream_sanctuary",
            REPO / "docs/ghl",
            REPO / "docs/freebies",
            REPO / "docs/integrations",
            REPO / "docs/runbooks",
            REPO / "artifacts/coordination/handoffs",
            REPO / "artifacts/qa/freebie_post_experience_capture_20260714",
            REPO / "tests",
        ]
    )

    failure_keys = (
        "missing_campaign_plans",
        "missing_pages",
        "extra_pages",
        "invalid_plans",
        "invalid_urls",
        "page_context_mismatches",
        "pages_without_embedded_campaign_plan",
        "embedded_campaign_plan_mismatches",
    )
    ok = all(not report[key] for key in failure_keys)
    ok = ok and not report["secret_scan"]["full_webhook_url_files"]
    report["ok"] = ok
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return ok, report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate evergreen GHL campaign plans for freebie landings."
    )
    parser.add_argument("--brand-id", default="way_stream_sanctuary")
    parser.add_argument("--plan-file", default=str(DEFAULT_PLAN))
    parser.add_argument("--artifact", help="Machine-readable validation report path")
    parser.add_argument(
        "--sync-pages",
        action="store_true",
        help="Inject or refresh per-page campaign JSON from the YAML plan source.",
    )
    args = parser.parse_args()

    plan_file = Path(args.plan_file)
    if not plan_file.is_absolute():
        plan_file = REPO / plan_file
    artifact = Path(args.artifact) if args.artifact else _artifact_default(args.brand_id)
    if not artifact.is_absolute():
        artifact = REPO / artifact

    ok, report = _validate(
        brand_id=args.brand_id,
        plan_file=plan_file,
        artifact=artifact,
        sync_pages=args.sync_pages,
    )
    rel_artifact = artifact.relative_to(REPO)
    if ok:
        print(
            "OK: "
            f"{args.brand_id} campaign plans valid "
            f"({report['pages_total']}/{report['expected_page_count']} pages, "
            f"{report['plans_total']} plans); artifact={rel_artifact}"
        )
        return 0

    print(f"FAIL: {args.brand_id} campaign plan validation failed; artifact={rel_artifact}")
    for key in (
        "missing_campaign_plans",
        "missing_pages",
        "invalid_plans",
        "invalid_urls",
        "page_context_mismatches",
        "pages_without_embedded_campaign_plan",
        "embedded_campaign_plan_mismatches",
    ):
        if report.get(key):
            print(f"{key}: {report[key]}")
    if report["secret_scan"]["full_webhook_url_files"]:
        print(f"full_webhook_url_files: {report['secret_scan']['full_webhook_url_files']}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
