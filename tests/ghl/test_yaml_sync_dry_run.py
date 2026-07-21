"""Tests for scripts.ghl.yaml_sync_dry_run (fail-closed desired-state diff).

LIVE_WRITES=none: these tests assert the engine has no GHL client and no network
call, and that every incomplete join blocks rather than proposing a write.
"""

from __future__ import annotations

import ast
import json
import re
import textwrap
from pathlib import Path

import pytest

from scripts.ghl import yaml_sync_dry_run as dr
from scripts.ghl import yaml_sync_inputs as si

# NOTE: constants are defined locally, not imported from conftest: a `tests` package in
# site-packages shadows this repo's `tests` namespace package, so `tests.ghl` is not importable.
# The `ghl` fixture itself still comes from tests/ghl/conftest.py via pytest's autoload.
REPO_ROOT = Path(__file__).resolve().parents[2]
FIELD_MAP_DOC = REPO_ROOT / "docs" / "ghl" / "GHL_YAML_SYNC_FIELD_MAP.md"

GHL_MODULES = ("__init__.py", "yaml_sync_inputs.py", "yaml_sync_dry_run.py", "build_setup_packet.py")

NETWORK_MODULES = {
    "requests",
    "httpx",
    "urllib",
    "urllib3",
    "http",
    "aiohttp",
    "socket",
    "ssl",
    "ftplib",
    "boto3",
    "botocore",
}


def _run(root: Path, **kw):
    kw.setdefault("generated_at", "2026-07-15T00:00:00Z")
    kw.setdefault("sync_sha", "a" * 40)
    return dr.build_dry_run(root, **kw)


def _rec(doc, brand_id=None):
    brand_id = brand_id or "way_stream_sanctuary"
    return next(r for r in doc["records"] if r["brand_id"] == brand_id)


def _field(rec, name):
    return next(f for f in rec["fields"] if f["field"] == name)


def _imported_roots(src: str) -> set[str]:
    roots: set[str] = set()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Import):
            roots.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            roots.add(node.module.split(".")[0])
    return roots


# ---------------------------------------------------------------------------
# LIVE_WRITES=none guarantees
# ---------------------------------------------------------------------------


def test_engine_imports_no_network_library():
    """LIVE_WRITES=none is structural: the sync tooling cannot reach the network."""
    for mod in GHL_MODULES:
        src = (REPO_ROOT / "scripts" / "ghl" / mod).read_text(encoding="utf-8")
        offenders = _imported_roots(src) & NETWORK_MODULES
        assert not offenders, f"{mod} imports network module(s): {sorted(offenders)}"


def test_engine_reads_no_credentials():
    """No env/keychain read: this tooling never touches a credential."""
    # Credential *reads*, not the deny-list names the secret guard carries as data.
    forbidden = re.compile(
        r"os\.environ|os\.getenv|environb|getpass|keyring|find-generic-password|load_dotenv",
        re.IGNORECASE,
    )
    for mod in GHL_MODULES:
        src = (REPO_ROOT / "scripts" / "ghl" / mod).read_text(encoding="utf-8")
        code = "\n".join(line for line in src.splitlines() if not line.strip().startswith("#"))
        assert not forbidden.search(code), f"{mod} must not read credentials"


def test_only_subprocess_use_is_local_git_rev_parse():
    """The one subprocess surface is `git rev-parse` for provenance -- no network shell-outs."""
    src = (REPO_ROOT / "scripts" / "ghl" / "yaml_sync_dry_run.py").read_text(encoding="utf-8")
    calls = re.findall(r"subprocess\.run\(\s*\[([^\]]*)\]", src, re.DOTALL)
    assert calls, "expected the git provenance subprocess call"
    for call in calls:
        assert '"git"' in call, f"non-git subprocess found: {call}"
        assert "rev-parse" in call, f"non-rev-parse git call found: {call}"
    for mod in GHL_MODULES:
        text = (REPO_ROOT / "scripts" / "ghl" / mod).read_text(encoding="utf-8")
        for banned in ("curl ", "wget ", "os.system", "subprocess.Popen", "subprocess.call"):
            assert banned not in text, f"{mod} contains {banned}"


def test_doc_declares_dry_run_only(ghl):
    doc = _run(ghl.repo())
    assert doc["mode"] == "dry_run_only"
    assert doc["live_writes"] is False
    assert doc["field_map_version"] == si.FIELD_MAP_VERSION


# ---------------------------------------------------------------------------
# origin/main reality: fail closed on the YAML/registry mismatch
# ---------------------------------------------------------------------------


def test_real_repo_state_fails_closed_on_missing_active_yaml():
    """The checked-in wizard YAML does not match the GHL pilot registry rows."""
    doc = dr.build_dry_run(REPO_ROOT, generated_at="2026-07-15T00:00:00Z")
    assert doc["summary"]["ghl_enabled_registry_rows"] == 3
    assert doc["summary"]["updates"] == 0
    assert doc["summary"]["creates_proposed"] == 0
    assert doc["summary"]["blocked"] == 3
    assert {r["brand_id"] for r in doc["records"]} == {
        "stillness_press",
        "devotion_path",
        "way_stream_sanctuary",
    }
    for r in doc["records"]:
        assert r["decision"] == "blocked"
        assert r["reason"] == dr.BLOCKED_MISSING_ACTIVE_YAML
        assert r["source_yaml_path"] is None
        assert r["target_location_id"] is None
        assert r["fields"] == []


def test_real_repo_state_has_no_classifier_active_yaml():
    """Spec eligibility == passes active_brand_classifier; on main that count is 0."""
    doc = dr.build_dry_run(REPO_ROOT, generated_at="2026-07-15T00:00:00Z")
    assert doc["summary"]["checked_in_brand_yamls"] == 1
    assert doc["summary"]["active_brand_yamls"] == 0
    assert doc["summary"]["eligible_brand_yamls"] == 0


def test_real_manifest_is_missing_location_id_column():
    """V1 is update-only; without location_id no row can ever be syncable."""
    manifest = si.load_manifest(REPO_ROOT / "docs" / "handoffs" / "ghl_location_manifest.example.tsv")
    assert "location_id" not in manifest.header
    assert "location_id" in manifest.missing_scale_columns


def test_cli_exits_two_when_blocked(capsys):
    rc = dr.main(["--repo-root", str(REPO_ROOT), "--generated-at", "2026-07-15T00:00:00Z", "--format", "table"])
    assert rc == 2
    assert "FAIL-CLOSED" in capsys.readouterr().err


def test_cli_exit_zero_on_blocked_flag_for_artifact_generation():
    rc = dr.main(
        ["--repo-root", str(REPO_ROOT), "--generated-at", "2026-07-15T00:00:00Z", "--exit-zero-on-blocked"]
    )
    assert rc == 0


# ---------------------------------------------------------------------------
# Join blocks
# ---------------------------------------------------------------------------


def test_missing_yaml_blocks(ghl):
    assert _rec(_run(ghl.repo(wizard="")))["reason"] == dr.BLOCKED_MISSING_ACTIVE_YAML


def test_inactive_yaml_blocks_and_reports_reason(ghl):
    """YAML present but failing the classifier (no wizard_core.tagline) blocks."""
    root = ghl.repo(
        wizard=textwrap.dedent(
            f"""
            schema_version: 1
            brand_id: {ghl.BRAND}
            display_name: Waystream Sanctuary
            wizard_core:
              positioning_line: Missing the tagline key.
            """
        ).lstrip()
    )
    rec = _rec(_run(root))
    assert rec["reason"] == dr.BLOCKED_INACTIVE_YAML
    assert "wizard_core.tagline" in rec["detail"]
    assert rec["source_yaml_path"] is not None
    assert rec["fields"] == []


def test_missing_manifest_row_blocks(ghl):
    assert _rec(_run(ghl.repo(manifest_rows=[])))["reason"] == dr.BLOCKED_MISSING_MANIFEST_ROW


def test_duplicate_manifest_row_blocks(ghl):
    root = ghl.repo(manifest_rows=[ghl.manifest_row(), ghl.manifest_row(location_id="LOC_FIXTURE_0002")])
    assert _rec(_run(root))["reason"] == dr.BLOCKED_DUPLICATE_MANIFEST_ROW


def test_missing_location_id_blocks(ghl):
    rec = _rec(_run(ghl.repo(manifest_rows=[ghl.manifest_row(location_id="")])))
    assert rec["reason"] == dr.BLOCKED_MISSING_LOCATION_MAPPING
    assert rec["target_location_id"] is None


def test_duplicate_location_id_blocks(ghl):
    root = ghl.repo(manifest_rows=[ghl.manifest_row(), ghl.manifest_row(brand_id="other_brand")])
    assert _rec(_run(root))["reason"] == dr.BLOCKED_DUPLICATE_LOCATION_ID


def test_missing_snapshot_blocks_even_on_a_perfect_join(ghl):
    """No proven current state -> no diff. Fail closed."""
    rec = _rec(_run(ghl.repo()))
    assert rec["reason"] == dr.BLOCKED_MISSING_SNAPSHOT
    assert rec["decision"] == "blocked"


def test_location_not_found_in_snapshot_blocks(ghl):
    root = ghl.repo(manifest_rows=[ghl.manifest_row(location_id="LOC_NOT_IN_SNAPSHOT")])
    rec = _rec(_run(root, snapshot_path=ghl.SNAPSHOT))
    assert rec["reason"] == dr.BLOCKED_LOCATION_NOT_FOUND
    assert "never creates sub-accounts" in rec["detail"]


def test_mismatched_location_name_blocks(ghl):
    root = ghl.repo(manifest_rows=[ghl.manifest_row(location_name="Wrong Name (en_US)")])
    assert _rec(_run(root, snapshot_path=ghl.SNAPSHOT))["reason"] == dr.BLOCKED_MISMATCHED_LOCATION_NAME


# ---------------------------------------------------------------------------
# Diff semantics on a complete join
# ---------------------------------------------------------------------------


def test_complete_join_yields_update_create_and_no_op(ghl):
    doc = _run(ghl.repo(), snapshot_path=ghl.SNAPSHOT)
    rec = _rec(doc)
    assert rec["decision"] == "update"

    # Snapshot value matches desired -> no_op.
    assert _field(rec, "phoenix_brand_id")["decision"] == "no_op"
    assert _field(rec, "phoenix_locale")["decision"] == "no_op"

    # Snapshot has a stale sha -> update, with a rollback note.
    sha = _field(rec, "phoenix_last_sync_sha")
    assert sha["decision"] == "update"
    assert sha["before"] == "0" * 40
    assert sha["after"] == "a" * 40
    assert "rollback" in (sha["rollback_note"] or "").lower()

    # Absent target -> create proposed only.
    feed = _field(rec, "phoenix_feed_url")
    assert feed["decision"] == "create"
    assert "create_proposed_only" in feed["reason"]

    assert doc["summary"]["updates"] >= 1
    assert doc["summary"]["creates_proposed"] >= 1
    assert doc["summary"]["no_ops"] >= 2


def test_missing_custom_value_id_blocks_the_field(ghl, tmp_path):
    """A target with no custom value id cannot be updated (spec: missing target id)."""
    snap = tmp_path / "snap.json"
    snap.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "locations": {
                    ghl.LOCATION_ID: {
                        "name": ghl.LOCATION_NAME,
                        "custom_values": {"phoenix_last_sync_sha": {"id": "", "value": "stale"}},
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    rec = _rec(_run(ghl.repo(), snapshot_path=snap))
    assert _field(rec, "phoenix_last_sync_sha")["decision"] == "blocked"
    assert _field(rec, "phoenix_last_sync_sha")["reason"] == dr.BLOCKED_MISSING_CUSTOM_VALUE_ID


def test_missing_source_value_blocks_the_field(ghl):
    """An empty manifest source cell blocks its field instead of writing a blank."""
    root = ghl.repo(manifest_rows=[ghl.manifest_row(funnel_base_url="")])
    rec = _rec(_run(root, snapshot_path=ghl.SNAPSHOT))
    fb = _field(rec, "phoenix_funnel_base_url")
    assert fb["decision"] == "blocked"
    assert fb["reason"] == dr.BLOCKED_MISSING_SOURCE_VALUE
    assert fb["after"] is None


def test_operator_approval_fields_are_flagged_and_not_live_writable(ghl):
    rec = _rec(_run(ghl.repo(), snapshot_path=ghl.SNAPSHOT))
    for name in ("phoenix_brand_tagline", "phoenix_positioning_line", "phoenix_brand_display_name"):
        f = _field(rec, name)
        assert f["requires_operator_approval"] is True
        assert f["live_write_allowed"] is False


def test_manual_ghl_admin_fields_are_never_live_writable(ghl):
    rec = _rec(_run(ghl.repo(), snapshot_path=ghl.SNAPSHOT))
    for name in ("phoenix_shop_cta_style", "phoenix_rollout_phase"):
        assert _field(rec, name)["live_write_allowed"] is False


def test_location_ids_are_redacted_by_default(ghl):
    doc = _run(ghl.repo(), snapshot_path=ghl.SNAPSHOT)
    rec = _rec(doc)
    assert rec["target_location_id"].startswith("loc_sha256:")
    assert ghl.LOCATION_ID not in json.dumps(doc)
    assert rec["target_location_id_redacted"] is True


def test_reveal_location_ids_is_opt_in(ghl):
    rec = _rec(_run(ghl.repo(), snapshot_path=ghl.SNAPSHOT, reveal_location_ids=True))
    assert rec["target_location_id"] == ghl.LOCATION_ID
    assert rec["target_location_id_redacted"] is False


def test_provenance_is_recorded(ghl):
    rec = _rec(_run(ghl.repo(), snapshot_path=ghl.SNAPSHOT))
    assert rec["source_yaml_path"].endswith(f"{ghl.BRAND}.yaml")
    assert len(rec["source_yaml_blob_sha"]) == 40
    assert rec["source_commit_sha"] == "a" * 40
    assert rec["manifest_row_id"] == 1


# ---------------------------------------------------------------------------
# Secret guard
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value",
    [
        "https://services.leadconnectorhq.com/hooks/abc123/webhook-trigger/xyz",
        "https://hooks.zapier.com/hooks/catch/123/abc/",
        "https://pub-x.r2.dev/feed.json?X-Amz-Signature=deadbeef",
        "https://example.com/feed.json?token=abc123def456",
        "pit-1234567890abcdef",
        "Bearer eyJhbGciOiJIUzI1NiJ9.abc",
    ],
)
def test_looks_secret_detects_webhook_and_token_shapes(value):
    assert si.looks_secret(value) is True
    assert si.redact(value) == si.REDACTED


@pytest.mark.parametrize(
    "value",
    [
        "https://brand-admin-onboarding.pages.dev/free/way_stream_sanctuary/",
        "PHOENIX_GHL_FUNNEL_WEBHOOK_WAYSTREAM",
        "way_stream_sanctuary",
        "en_US",
        None,
    ],
)
def test_looks_secret_allows_public_values_and_env_names(value):
    assert si.looks_secret(value) is False


def test_presigned_feed_url_is_blocked_and_redacted(ghl):
    signed = ghl.FEED_URL + "?X-Amz-Signature=deadbeefcafe"
    doc = _run(ghl.repo(manifest_rows=[ghl.manifest_row(feed_url=signed)]), snapshot_path=ghl.SNAPSHOT)
    feed = _field(_rec(doc), "phoenix_feed_url")
    assert feed["decision"] == "blocked"
    assert feed["reason"] == dr.BLOCKED_SECRET_LIKE_VALUE
    assert feed["after"] == si.REDACTED
    assert "deadbeefcafe" not in json.dumps(doc)


def test_secret_like_current_value_blocks_the_field(ghl, tmp_path):
    snap = tmp_path / "snap.json"
    snap.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "locations": {
                    ghl.LOCATION_ID: {
                        "name": ghl.LOCATION_NAME,
                        "custom_values": {
                            "phoenix_feed_url": {
                                "id": "cv_x",
                                "value": "https://services.leadconnectorhq.com/hooks/a/webhook-trigger/b",
                            }
                        },
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    doc = _run(ghl.repo(), snapshot_path=snap)
    feed = _field(_rec(doc), "phoenix_feed_url")
    assert feed["decision"] == "blocked"
    assert feed["reason"] == dr.BLOCKED_SECRET_LIKE_VALUE
    assert feed["before"] == si.REDACTED
    assert "leadconnectorhq" not in json.dumps(doc)


def test_webhook_url_never_reaches_the_diff(ghl):
    """webhook_env is phoenix_only: no GHL custom value targets it at all."""
    doc = _run(ghl.repo(), snapshot_path=ghl.SNAPSHOT)
    assert "leadconnectorhq" not in json.dumps(doc)
    fields = {f["field"] for r in doc["records"] for f in r["fields"]}
    assert not any("webhook" in f for f in fields)


# ---------------------------------------------------------------------------
# Field-map drift gate (memory is recall, not enforcement)
# ---------------------------------------------------------------------------


def _doc_field_map() -> dict[str, str]:
    """Parse phoenix_* rows out of the merged field-map markdown table."""
    out: dict[str, str] = {}
    for line in FIELD_MAP_DOC.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| `phoenix_"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4:
            continue
        out[cells[0].strip("`")] = cells[3].strip("`")
    return out


def test_code_field_map_matches_merged_doc():
    """scripts/ghl FIELD_MAP must not drift from docs/ghl/GHL_YAML_SYNC_FIELD_MAP.md."""
    doc_map = _doc_field_map()
    code_map = {f.name: f.safety_class for f in si.FIELD_MAP}
    assert doc_map, "field-map doc table parsed empty; the gate would be vacuous"
    assert code_map == doc_map


def test_every_field_map_safety_class_is_known():
    for f in si.FIELD_MAP:
        assert f.safety_class in si.SAFETY_CLASSES


def test_field_map_targets_are_phoenix_prefixed_and_unique():
    names = [f.name for f in si.FIELD_MAP]
    assert all(n.startswith("phoenix_") for n in names)
    assert len(names) == len(set(names))


def test_never_sync_keys_are_absent_from_the_field_map():
    names = {f.name for f in si.FIELD_MAP}
    sources = {f.source_key for f in si.FIELD_MAP}
    for key in si.NEVER_SYNC_KEYS:
        assert key not in names
        assert key not in sources


def test_pilot_fields_are_phoenix_managed():
    for name in si.PILOT_FIELD_ORDER:
        assert si.FIELD_MAP_BY_NAME[name].safety_class == si.PHOENIX_MANAGED
        assert si.FIELD_MAP_BY_NAME[name].live_write_allowed is True


# ---------------------------------------------------------------------------
# Scale shape: 37 manifest rows without 37 YAMLs
# ---------------------------------------------------------------------------


def test_thirty_seven_row_manifest_shape_is_supported_without_all_yamls(ghl):
    """Scale gate: a 37-row manifest must not require 37 wizard YAMLs to exist."""
    rows = [
        ghl.manifest_row(
            location_id=f"LOC_FIXTURE_{i:04d}",
            location_name=f"Brand {i} (en_US)",
            brand_id=f"brand_{i:02d}",
        )
        for i in range(1, 38)
    ]
    root = ghl.repo(manifest_rows=rows)
    manifest = si.load_manifest(root / "docs" / "handoffs" / "ghl_location_manifest.example.tsv")
    assert len(manifest.rows) == 37
    assert manifest.missing_scale_columns == ()

    # Only the registry-enabled brand is evaluated; the other 37 rows are inert.
    doc = _run(root)
    assert len(doc["records"]) == 1
    assert doc["records"][0]["brand_id"] == ghl.BRAND
    assert doc["records"][0]["reason"] == dr.BLOCKED_MISSING_MANIFEST_ROW


def test_brand_filter_limits_the_run():
    doc = dr.build_dry_run(REPO_ROOT, brand_filter="devotion_path", generated_at="2026-07-15T00:00:00Z")
    assert [r["brand_id"] for r in doc["records"]] == ["devotion_path"]
