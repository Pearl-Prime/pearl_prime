"""Lane 03: phantom-books gates — fail-closed catalog bearing + real-asset availability."""
from __future__ import annotations

import subprocess

from server.routes.brand_onboarding import (
    _is_catalog_bearing,
    available_downloadable_assets,
)


def test_is_catalog_bearing_fail_closed_unknown_brand():
    """Unknown brand_id must NOT invent available books (fail-closed)."""
    assert _is_catalog_bearing("totally_unknown_brand_xx", {"known_en_us": {"buildable": True}}) is False


def test_is_catalog_bearing_fail_closed_empty_index():
    assert _is_catalog_bearing("any_brand_en_us", {}) is False


def test_is_catalog_bearing_explicit_non_buildable_hidden():
    index = {"planned_only_en_us": {"buildable": False, "d": "Planned Only"}}
    assert _is_catalog_bearing("planned_only_en_us", index) is False


def test_is_catalog_bearing_real_buildable_shown():
    index = {"stabilizer_en_us": {"buildable": True, "d": "Harbor Line Books"}}
    assert _is_catalog_bearing("stabilizer_en_us", index) is True


def test_is_catalog_bearing_buildable_default_true_when_key_absent():
    """Index entry present without buildable key → treated as buildable (same as client)."""
    index = {"optimizer_en_us": {"d": "Daybreak Editions"}}
    assert _is_catalog_bearing("optimizer_en_us", index) is True


def test_available_downloadable_assets_empty_when_none():
    assert available_downloadable_assets(None) == []
    assert available_downloadable_assets({}) == []
    assert available_downloadable_assets({"weeks": {}}) == []


def test_available_downloadable_assets_hides_catalog_only_and_pending():
    """Catalog metadata / production-pending must never surface as downloadable."""
    pending = {
        "production_files_ready": False,
        "delivery_status": "catalog_ready_production_files_pending",
        "weeks": {
            "2026-W29": {
                "catalog_metadata": [
                    {"file": "title.epub", "url": "/download/fake", "kb": 1},
                ],
                "amazon_kdp": [
                    {"file": "phantom.epub", "url": "/download/phantom", "kb": 10},
                ],
            }
        },
    }
    assert available_downloadable_assets(pending) == []

    catalog_only = {
        "weeks": {
            "2026-W29": {
                "catalog_metadata": [
                    {"file": "meta.csv", "url": "/meta.csv", "kb": 2},
                ],
            }
        }
    }
    assert available_downloadable_assets(catalog_only) == []


def test_available_downloadable_assets_shows_real_asset():
    delivery = {
        "weeks": {
            "2026-W27": {
                "amazon_kdp": [
                    {
                        "file": "warrior_calm__burnout.epub",
                        "url": "/download/warrior_calm__burnout?week=2026-W27",
                        "kb": 413,
                    },
                    {"file": "notes.md", "url": "/download/notes.md", "kb": 1},
                ]
            }
        }
    }
    assets = available_downloadable_assets(delivery)
    assert len(assets) == 1
    assert assets[0]["file"] == "warrior_calm__burnout.epub"
    assert assets[0]["platform"] == "amazon_kdp"


def test_roster_ops_url_points_to_handoff_not_stale_admin():
    """React data source must deep-link Ops to real-asset-gated handoff page."""
    script = r"""
import { pathToFileURL } from "node:url";

const modUrl = pathToFileURL(`${process.cwd()}/brand-wizard-app/src/brandDirectorRoster.js`).href;
const { brandOpsUrl, staticRowsFromIndex } = await import(modUrl);

const ops = brandOpsUrl("optimizer_en_us");
if (!ops.includes("brand_handoff_dashboard.html")) {
  throw new Error(`ops url must target handoff dashboard, got ${ops}`);
}
if (ops.includes("brand_admin.html")) {
  throw new Error(`ops url must not target stale brand_admin.html, got ${ops}`);
}
if (!ops.includes("brand=optimizer_en_us")) {
  throw new Error(`ops url must scope brand_id, got ${ops}`);
}

const rows = staticRowsFromIndex({
  optimizer_en_us: { d: "Daybreak Editions", arch: "optimizer", lane: "en_US", lifecycle: "active", buildable: true },
  phantom_planned_en_us: { d: "Phantom", arch: "phantom", buildable: false },
});
const byId = Object.fromEntries(rows.map((r) => [r.brand_id, r]));
if (byId.optimizer_en_us.ops_url !== "/brand_handoff_dashboard.html?brand=optimizer_en_us") {
  throw new Error(`bad optimizer ops_url: ${byId.optimizer_en_us.ops_url}`);
}
if (byId.phantom_planned_en_us.ops_access !== "blocked") {
  throw new Error(`non-buildable must block ops access: ${JSON.stringify(byId.phantom_planned_en_us)}`);
}
"""
    proc = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout


def test_js_available_downloadable_assets_mirrors_python_gate():
    script = r"""
import { pathToFileURL } from "node:url";

const modUrl = pathToFileURL(`${process.cwd()}/brand-wizard-app/src/brandDirectorAvailability.js`).href;
const { availableDownloadableAssets, availableBooksSummary } = await import(modUrl);

const pending = {
  production_files_ready: false,
  weeks: {
    "2026-W29": {
      amazon_kdp: [{ file: "phantom.epub", url: "/download/phantom", kb: 10 }],
    },
  },
};
if (availableDownloadableAssets(pending).length !== 0) {
  throw new Error("pending production must be empty");
}
if (availableDownloadableAssets(null).length !== 0) {
  throw new Error("null delivery must be empty");
}

const real = {
  weeks: {
    "2026-W27": {
      amazon_kdp: [
        { file: "real.epub", url: "/download/real", kb: 100 },
        { file: "notes.md", url: "/download/notes.md", kb: 1 },
      ],
      catalog_metadata: [{ file: "meta.csv", url: "/meta.csv", kb: 2 }],
    },
  },
};
const assets = availableDownloadableAssets(real);
if (assets.length !== 1 || assets[0].file !== "real.epub") {
  throw new Error(`expected one real asset, got ${JSON.stringify(assets)}`);
}
const summary = availableBooksSummary(null);
if (!summary.empty || summary.empty_label !== "No titles available yet") {
  throw new Error(`bad empty summary: ${JSON.stringify(summary)}`);
}
"""
    proc = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
