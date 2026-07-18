"""Shared fixtures for the GHL YAML sync dry-run + setup packet tests.

Builds a self-contained fake repo root so the join can be exercised without any
network, credential, or live GHL location.
"""

from __future__ import annotations

import shutil
import textwrap
from dataclasses import dataclass
from pathlib import Path

import pytest

from scripts.brand.active_brand_classifier import reset_default_classifier

REPO_ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "ghl" / "snapshot_sandbox_example.json"
FIELD_MAP_DOC = REPO_ROOT / "docs" / "ghl" / "GHL_YAML_SYNC_FIELD_MAP.md"

BRAND = "way_stream_sanctuary"
LOCALE = "en_US"
LOCATION_ID = "LOC_FIXTURE_0001"
LOCATION_NAME = "Waystream Sanctuary (en_US)"
WEBHOOK_ENV = "PHOENIX_GHL_FUNNEL_WEBHOOK_WAYSTREAM"
FEED_URL = "https://pub-example.r2.dev/pearl-prime-content/way_stream_sanctuary/en_US/2026-W26/marketing_feed.json"
FUNNEL_BASE = "https://brand-admin-onboarding.pages.dev/free/way_stream_sanctuary/"

MANIFEST_HEADER = (
    "location_id\tlocation_name\tbrand_id\tlocale\tdisplay_name\tfeed_url\tfunnel_base_url\t"
    "webhook_env\tshop_cta_style\trollout_phase\tghl_enabled\tphoenix_managed_custom_value_ids\t"
    "last_readback_at\tlast_sync_sha\trollback_note"
)

ACTIVE_WIZARD = textwrap.dedent(
    f"""
    schema_version: 1
    brand_id: {BRAND}
    display_name: Waystream Sanctuary
    brand_director:
      name: Test Director
      id: test_director
      status: assigned
    wizard_core:
      tagline: Still water moves
      positioning_line: Composite EPUB brand for waystream operations.
    """
).lstrip()

# Copied into the fake repo so tags/channels/payloads resolve against real config.
_REAL_CONFIGS = (
    "config/freebies/quiz_segment_map.yaml",
    "config/freebies/ghl_funnel_capture.yaml",
    "config/marketing/ghl_email_slot_rules.yaml",
)


@dataclass
class GhlEnv:
    """Factory for a fake repo root with a classifier-active brand."""

    tmp_path: Path

    BRAND: str = BRAND
    LOCALE: str = LOCALE
    LOCATION_ID: str = LOCATION_ID
    LOCATION_NAME: str = LOCATION_NAME
    WEBHOOK_ENV: str = WEBHOOK_ENV
    FEED_URL: str = FEED_URL
    FUNNEL_BASE: str = FUNNEL_BASE
    REPO_ROOT: Path = REPO_ROOT
    SNAPSHOT: Path = SNAPSHOT_FIXTURE

    def manifest_row(
        self,
        *,
        location_id: str = LOCATION_ID,
        location_name: str = LOCATION_NAME,
        brand_id: str = BRAND,
        locale: str = LOCALE,
        feed_url: str = FEED_URL,
        funnel_base_url: str = FUNNEL_BASE,
    ) -> str:
        return "\t".join(
            [
                location_id,
                location_name,
                brand_id,
                locale,
                "Waystream Sanctuary",
                feed_url,
                funnel_base_url,
                WEBHOOK_ENV,
                "download_proxy",
                "pilot",
                "true",
                "cv_fixture_brand_id",
                "2026-07-15T00:00:00Z",
                "0" * 40,
                "restore prior value",
            ]
        )

    def repo(self, *, wizard: str | None = None, manifest_rows: list[str] | None = None) -> Path:
        root = self.tmp_path / "repo"
        if root.exists():
            shutil.rmtree(root)
        (root / "config" / "marketing").mkdir(parents=True)
        (root / "config" / "manga").mkdir(parents=True)
        (root / "config" / "freebies").mkdir(parents=True)
        (root / "docs" / "handoffs").mkdir(parents=True)
        (root / "brand-wizard-app" / "brands").mkdir(parents=True)

        # Classifier brand universe.
        (root / "config" / "brand_registry.yaml").write_text(
            f"brands:\n  {BRAND}:\n    display_name: Waystream Sanctuary\n", encoding="utf-8"
        )
        (root / "config" / "manga" / "canonical_brand_list.yaml").write_text("brands: {}\n", encoding="utf-8")

        text = ACTIVE_WIZARD if wizard is None else wizard
        if text:
            (root / "brand-wizard-app" / "brands" / f"{BRAND}.yaml").write_text(text, encoding="utf-8")

        (root / "config" / "marketing" / "brand_marketing_registry.yaml").write_text(
            textwrap.dedent(
                f"""
                schema_version: 1
                defaults:
                  locale: en_US
                  shop_base: https://pearlprime.shop
                brands:
                  {BRAND}:
                    rollout_phase: pilot
                    ghl_enabled: true
                    display_name: Waystream Sanctuary
                    webhook_env: {WEBHOOK_ENV}
                """
            ).lstrip(),
            encoding="utf-8",
        )

        rows = [self.manifest_row()] if manifest_rows is None else manifest_rows
        (root / "docs" / "handoffs" / "ghl_location_manifest.example.tsv").write_text(
            "\n".join([MANIFEST_HEADER, *rows]) + "\n", encoding="utf-8"
        )

        for rel in _REAL_CONFIGS:
            src = REPO_ROOT / rel
            if src.is_file():
                shutil.copy(src, root / rel)
        return root


@pytest.fixture
def ghl(tmp_path: Path) -> GhlEnv:
    return GhlEnv(tmp_path)


@pytest.fixture(autouse=True)
def _reset_classifier():
    """The classifier memoizes a default instance keyed to the real repo root."""
    reset_default_classifier()
    yield
    reset_default_classifier()
