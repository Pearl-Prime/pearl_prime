"""Tests for scripts.ghl.build_setup_packet (GHL admin setup packet generator).

LIVE_WRITES=none. The packet is a read-only handoff. These tests pin the two
rules that matter most: it never carries a webhook URL or any secret, and it
never labels an incomplete join as ready.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.ghl import build_setup_packet as bp
from scripts.ghl import yaml_sync_inputs as si

# Constants are local, not imported from conftest (a site-packages `tests` package shadows
# this repo's `tests` namespace package). The `ghl` fixture is autoloaded by pytest.
REPO_ROOT = Path(__file__).resolve().parents[2]


def _packet(root, brand_id="way_stream_sanctuary"):
    return bp.build_packet(brand_id, repo_root=root, generated_at="2026-07-15T00:00:00Z")


# ---------------------------------------------------------------------------
# Smoke: the one wizard YAML that actually exists on main
# ---------------------------------------------------------------------------


def test_stabilizer_packet_is_blocked_and_tells_the_truth():
    """stabilizer_en_us is the only checked-in YAML and it is not GHL-ready."""
    packet = bp.build_packet("stabilizer_en_us", repo_root=REPO_ROOT, generated_at="2026-07-15T00:00:00Z")
    assert packet["readiness"] == bp.BLOCKED
    assert packet["live_writes"] is False
    assert packet["brand"]["wizard_active"] is False
    assert packet["brand"]["wizard_yaml_path"] == "brand-wizard-app/brands/stabilizer_en_us.yaml"
    assert packet["ghl_target"]["location_id"] is None

    reasons = " ".join(packet["blockers"])
    assert "blocked_inactive_yaml" in reasons
    assert "blocked_missing_registry_row" in reasons
    assert "blocked_missing_manifest_row" in reasons


def test_stabilizer_packet_carries_the_brand_director():
    packet = bp.build_packet("stabilizer_en_us", repo_root=REPO_ROOT, generated_at="2026-07-15T00:00:00Z")
    assert packet["admin"]["brand_director_name"] == "Kamiko Parker"
    assert packet["admin"]["brand_director_id"] == "kamiko_parker"
    assert packet["admin"]["brand_director_status"] == "assigned"
    assert packet["brand"]["display_name"] == "Harbor Line Books"


def test_ghl_pilot_brands_are_blocked_on_missing_yaml():
    """The three GHL-enabled registry rows have no wizard YAML at all."""
    for brand_id in ("stillness_press", "devotion_path", "way_stream_sanctuary"):
        packet = bp.build_packet(brand_id, repo_root=REPO_ROOT, generated_at="2026-07-15T00:00:00Z")
        assert packet["readiness"] == bp.BLOCKED
        assert any("blocked_missing_active_yaml" in b for b in packet["blockers"])
        assert packet["brand"]["ghl_enabled"] is True


# ---------------------------------------------------------------------------
# Secret discipline
# ---------------------------------------------------------------------------


def test_packet_carries_webhook_env_name_only(ghl):
    packet = _packet(ghl.repo())
    assert packet["webhook"]["env_name"] == "PHOENIX_GHL_FUNNEL_WEBHOOK_WAYSTREAM"
    assert packet["webhook"]["url"] is None
    assert "ENV NAME ONLY" in packet["webhook"]["value_policy"]


def test_packet_contains_no_secret_like_value(ghl):
    blob = json.dumps(_packet(ghl.repo()))
    assert "leadconnectorhq" not in blob
    assert "X-Amz-Signature" not in blob
    for line in blob.split('"'):
        assert not si.looks_secret(line) or line == si.REDACTED


def test_packet_generation_fails_closed_when_webhook_env_holds_a_url(ghl):
    """A URL in the webhook_env slot is a secret-class value: blocked, not carried."""
    root = ghl.repo()
    reg = root / "config" / "marketing" / "brand_marketing_registry.yaml"
    reg.write_text(
        reg.read_text(encoding="utf-8").replace(
            "PHOENIX_GHL_FUNNEL_WEBHOOK_WAYSTREAM",
            "https://services.leadconnectorhq.com/hooks/abc/webhook-trigger/xyz",
        ),
        encoding="utf-8",
    )
    packet = _packet(root)
    assert packet["readiness"] == bp.BLOCKED
    assert any("blocked_secret_like_value" in b for b in packet["blockers"])
    assert packet["webhook"]["env_name"] is None
    assert "leadconnectorhq" not in json.dumps(packet)


def test_assert_packet_clean_raises_on_a_leaked_secret():
    with pytest.raises(ValueError, match="secret-like values"):
        bp._assert_packet_clean(
            {"webhook": {"url": "https://services.leadconnectorhq.com/hooks/abc/webhook-trigger/xyz"}}
        )


def test_location_id_is_redacted_in_the_packet(ghl):
    packet = _packet(ghl.repo())
    assert packet["ghl_target"]["location_id"].startswith("loc_sha256:")
    assert packet["ghl_target"]["location_id_redacted"] is True
    assert ghl.LOCATION_ID not in json.dumps(packet)


def test_sample_payload_uses_reserved_placeholder_domain(ghl):
    sp = _packet(ghl.repo())["sample_payload"]
    assert sp["example"]["email"].endswith("@example.invalid")
    assert set(sp["payload_fields"]) >= {"email", "quiz_id", "topic", "funnel_slug"}
    assert "No real contact data" in sp["note"]


# ---------------------------------------------------------------------------
# Packet content
# ---------------------------------------------------------------------------


def test_complete_join_yields_a_reviewable_packet(ghl):
    packet = _packet(ghl.repo())
    assert packet["readiness"] == bp.READY
    assert packet["blockers"] == []
    assert packet["brand"]["wizard_active"] is True
    assert packet["ghl_target"]["location_name"] == "Waystream Sanctuary (en_US)"
    assert packet["admin"]["brand_director_name"] == "Test Director"


def test_packet_lists_every_field_map_target(ghl):
    packet = _packet(ghl.repo())
    names = [f["name"] for f in packet["custom_fields"]["phoenix_custom_values"]]
    assert names == [f.name for f in si.FIELD_MAP]
    assert packet["custom_fields"]["pilot_field_order"] == list(si.PILOT_FIELD_ORDER)


def test_packet_lists_expected_tags(ghl):
    tags = _packet(ghl.repo())["expected_tags"]
    assert tags["score_band_tags"] == ["severity_high", "severity_low", "severity_medium"]
    assert "pref_somatic" in tags["preferred_format_tags"]
    assert "ready_buy" in tags["readiness_tags"]
    assert tags["topic_default_tags"]["burnout"] == ["source_freebie_quiz", "quiz_burnout", "freebie_captured"]


def test_packet_lists_channels_including_env_name_only_webhook(ghl):
    channels = {c["channel"]: c for c in _packet(ghl.repo())["channels"]}
    assert set(channels) == {
        "weekly_marketing_feed",
        "freebie_funnel_pages",
        "inbound_webhook_capture",
        "email_automation",
        "shop",
    }
    assert channels["inbound_webhook_capture"]["target"] is None
    assert channels["inbound_webhook_capture"]["status"] == "env_name_only"
    assert channels["weekly_marketing_feed"]["status"] == "resolved"


def test_packet_derives_funnel_urls_from_the_manifest(ghl):
    urls = _packet(ghl.repo())["funnel_urls"]
    assert len(urls) == 15
    burnout = next(u for u in urls if u["topic"] == "burnout")
    assert burnout["url"] == f"{ghl.FUNNEL_BASE.rstrip('/')}/burnout-energy-audit/"
    assert burnout["quiz_id"] == "capacity_assessment"
    assert "freebie_captured" in burnout["tags"]


def test_funnel_urls_are_unresolved_without_a_manifest_row(ghl):
    urls = _packet(ghl.repo(manifest_rows=[]))["funnel_urls"]
    assert all(u["url"] is None for u in urls)
    assert all(u["url_status"] == "unresolved_missing_funnel_base_url" for u in urls)


def test_markdown_render_is_truth_labeled(ghl):
    md = bp.render_markdown(_packet(ghl.repo(manifest_rows=[])))
    assert "readiness: **BLOCKED**" in md
    assert "live_writes: **none**" in md
    assert "## Blockers (fail-closed)" in md
    assert "leadconnectorhq" not in md


def test_markdown_render_of_a_ready_packet(ghl):
    md = bp.render_markdown(_packet(ghl.repo()))
    assert "readiness: **READY_FOR_ADMIN_REVIEW**" in md
    assert "PHOENIX_GHL_FUNNEL_WEBHOOK_WAYSTREAM" in md
    assert "never stored here" in md


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def test_cli_writes_packets_and_exits_two_when_blocked(tmp_path):
    out = tmp_path / "packets"
    rc = bp.main(
        [
            "--repo-root",
            str(REPO_ROOT),
            "--all-ghl-enabled",
            "--generated-at",
            "2026-07-15T00:00:00Z",
            "--out-dir",
            str(out),
        ]
    )
    assert rc == 2
    written = sorted(p.name for p in out.iterdir())
    assert written == ["devotion_path__en_US", "stillness_press__en_US", "way_stream_sanctuary__en_US"]
    for d in out.iterdir():
        assert (d / "PACKET.md").is_file()
        assert json.loads((d / "packet.json").read_text(encoding="utf-8"))["readiness"] == bp.BLOCKED


def test_cli_requires_a_brand_selection():
    with pytest.raises(SystemExit):
        bp.main(["--repo-root", str(REPO_ROOT)])


def test_cli_all_wizard_yamls_covers_the_one_checked_in_yaml(tmp_path):
    out = tmp_path / "packets"
    rc = bp.main(
        [
            "--repo-root",
            str(REPO_ROOT),
            "--all-wizard-yamls",
            "--generated-at",
            "2026-07-15T00:00:00Z",
            "--out-dir",
            str(out),
            "--exit-zero-on-blocked",
        ]
    )
    assert rc == 0
    assert [p.name for p in out.iterdir()] == ["stabilizer_en_us__en_US"]
