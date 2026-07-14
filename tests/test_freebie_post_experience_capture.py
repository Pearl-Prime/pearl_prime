from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_report_channel_order_and_validation_contracts() -> None:
    cfg = yaml.safe_load((REPO / "config/freebies/report_delivery_channels.yaml").read_text()) or {}
    assert cfg["default_order"] == ["whatsapp", "telegram", "email"]
    assert cfg["region_orders"]["JP"] == ["line", "messenger", "whatsapp", "telegram", "email"]
    assert "FREEBIE_TELEGRAM_BOT_TOKEN" in cfg["channels"]["telegram"]["env_vars"]
    text = (REPO / "config/freebies/report_delivery_channels.yaml").read_text().lower()
    assert "webhook-trigger" not in text
    assert "services.leadconnectorhq.com" not in text


def test_all_waystream_pages_are_tool_first_report_unlock() -> None:
    plans = yaml.safe_load((REPO / "config/freebies/waystream_evergreen_campaign_plan.yaml").read_text())["plans"]
    assert len(plans) == 15
    for plan in plans:
        page = REPO / "brand-wizard-app/public/free/way_stream_sanctuary" / plan["source_page_slug"] / "index.html"
        text = page.read_text()
        assert 'data-post-experience-capture="1"' in text
        assert 'data-ghl-webhook=""' in text
        assert "webhook-trigger" not in text
        assert "phoenix_funnel.js" in text


def test_sample_report_generation_has_no_placeholders() -> None:
    module = _load_module(REPO / "scripts/freebies/generate_freebie_report.py", "generate_freebie_report_test")
    report = module.build_report(
        "anxiety-nervous-system-reset",
        '[{"field":"q1","value":"completed"}]',
        "medium",
    )
    assert report["report_id"] == "waystream_anxiety-nervous-system-reset_report_v1"
    assert "clinical advice" in report["summary"].lower()
    assert "{{" not in report["text"]
    assert report["sections"]["recommended_practice"]
