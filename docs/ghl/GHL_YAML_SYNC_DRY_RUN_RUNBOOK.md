# GHL YAML Sync Dry-Run + Setup Packet Runbook

PROVENANCE
spec=docs/specs/GHL_YAML_SUBACCOUNT_SYNC_V1_SPEC.md (PR #5687)
field_map=docs/ghl/GHL_YAML_SYNC_FIELD_MAP.md (PR #5690)
research=artifacts/research/ghl_api_current_docs_20260715.md (PR #5686)
example=artifacts/ghl/yaml_subaccount_sync_20260715/dry_run_diff_example.json (PR #5689)
builds_on=brand-wizard YAML SSOT; brand_marketing_registry; ghl_location_manifest
inventory=EXTENDS the GHL YAML sync program with executable tooling; no reduction of feed/webhook behavior

## Status

`EXECUTED-REAL` for the dry-run and packet tooling: both CLIs run against `origin/main`
and produce byte-verified artifacts. **Not** `PROVEN-AT-BAR` for any GHL location —
zero live calls have ever been made from this code path.

**LIVE_WRITES=none.** This tooling has no GHL client. It imports no network library,
reads no credential, and its only subprocess is a local `git rev-parse` for provenance.
Those properties are pinned by tests (`tests/ghl/test_yaml_sync_dry_run.py`), not by
convention.

## What This Lane Ships

| Path | Purpose |
|---|---|
| `scripts/ghl/yaml_sync_inputs.py` | Read-only loaders (registry, manifest, snapshot, wizard YAML), the code field map, and the secret guard. |
| `scripts/ghl/yaml_sync_dry_run.py` | Desired-state diff CLI. Fails closed. |
| `scripts/ghl/build_setup_packet.py` | GHL admin setup packet CLI (Markdown + JSON). |
| `tests/ghl/` | 67 tests: fail-closed join, secret guard, field-map drift gate, no-network gate. |
| `tests/fixtures/ghl/snapshot_sandbox_example.json` | Synthetic current-state snapshot. Not a real location. |

## Commands

```bash
# Dry-run against the live checkout (exits 2 when anything is blocked)
PYTHONPATH=. python3 scripts/ghl/yaml_sync_dry_run.py --format table

# Machine artifact (exit 0 so artifact generation still writes the file)
PYTHONPATH=. python3 scripts/ghl/yaml_sync_dry_run.py \
  --out artifacts/ghl/yaml_subaccount_sync_20260715/dry_run_diff_origin_main.json \
  --exit-zero-on-blocked

# Field-level diff needs a read-only snapshot fixture
PYTHONPATH=. python3 scripts/ghl/yaml_sync_dry_run.py \
  --snapshot tests/fixtures/ghl/snapshot_sandbox_example.json --format table

# Setup packets
PYTHONPATH=. python3 scripts/ghl/build_setup_packet.py --brand stabilizer_en_us
PYTHONPATH=. python3 scripts/ghl/build_setup_packet.py --all-ghl-enabled --all-wizard-yamls \
  --out-dir artifacts/ghl/setup_packets_20260715 --exit-zero-on-blocked

# Tests (~3s)
PYTHONPATH=. python3 -m pytest tests/ghl/ -q
```

## Fail-Closed Order

The join is evaluated in this order; the first failure blocks the row and no field
diff is computed. Wizard-YAML eligibility is checked first, which is why the
`origin/main` run reproduces the merged example's three `blocked_missing_active_yaml`
records.

1. `blocked_missing_active_yaml` — no `brand-wizard-app/brands/<brand_id>.yaml`.
2. `blocked_inactive_yaml` — YAML present but fails `scripts/brand/active_brand_classifier.py`.
3. `blocked_missing_manifest_row` / `blocked_duplicate_manifest_row` — not exactly one row.
4. `blocked_missing_location_mapping` — manifest has no `location_id`. V1 is update-only; sub-accounts are never created.
5. `blocked_duplicate_location_id` — one location id on several rows.
6. `blocked_missing_snapshot` — no read-only current-state proof, so no diff is possible.
7. `blocked_location_not_found` — location id absent from the snapshot.
8. `blocked_mismatched_location_name` — manifest name != GHL location name.
9. Per field: `blocked_secret_like_value`, `blocked_missing_source_value`,
   `blocked_missing_custom_value_id`, `blocked_non_phoenix_owned_target`.

Only after all of the above does a field reach `no_op`, `update`, or `create`
(create is **proposed only** — live creation needs approval).

## Secret Discipline

- The webhook **env var NAME** (e.g. `PHOENIX_GHL_FUNNEL_WEBHOOK_WAYSTREAM`) is carried.
  The webhook **URL value** is never read, stored, printed, or synced. `webhook_env` is
  `phoenix_only`: no GHL custom value targets it.
- `looks_secret()` blocks and redacts webhook URLs, presigned URLs (`X-Amz-Signature`,
  `?sig=`, `?token=`), bearer tokens, JWTs, and `pit-`/`sk-` style keys — on both the
  desired value and the current snapshot value.
- GHL location ids are hashed (`loc_sha256:<12>`) by default. `--reveal-location-ids`
  is local-operator only and must never be used to produce a committed artifact.
- `build_setup_packet._assert_packet_clean()` raises rather than write a packet
  containing a secret-like value.

## Current `origin/main` Findings

Byte-verified at `5472f4a517345ec9fbfc158f1562efd3667a9a26`
(`artifacts/ghl/yaml_subaccount_sync_20260715/dry_run_diff_origin_main.json`):

1. **YAML/registry mismatch (confirmed).** The only checked-in wizard YAML is
   `stabilizer_en_us`; the GHL-enabled registry rows are `stillness_press`,
   `devotion_path`, `way_stream_sanctuary`. All three block on
   `blocked_missing_active_yaml`. Zero updates, zero creates.
2. **Zero classifier-active YAMLs.** `stabilizer_en_us` does not pass
   `active_brand_classifier` either: its `brand_id` is not in the classifier universe
   (`config/brand_registry.yaml` has `stabilizer_tw/hk/cn/sg`, not `stabilizer_en_us`),
   and it carries `display_brand` + `wizard_core.positioning_line` but no `display_name`
   and no `wizard_core.tagline`. Under the spec's own eligibility rule, the eligible
   count on main is **0, not 1**.
3. **The manifest cannot map a location.** `docs/handoffs/ghl_location_manifest.example.tsv`
   has no `location_id` column, so even a perfect YAML+registry join would block at
   `blocked_missing_location_mapping`. Missing scale columns: `location_id`,
   `phoenix_managed_custom_value_ids`, `last_readback_at`, `last_sync_sha`, `rollback_note`.
4. **Two merged docs disagree on one safety class.** The spec's Field Policy table calls
   `display_name` -> `phoenix_brand_display_name` "`phoenix_managed` with review"; the
   field map calls it `operator_approval_required`. The code follows the **field map**
   (the stricter, more specific authority) and a drift test pins code to that doc.
5. **The merged example's summary overcounts.** `dry_run_diff_example.json` reports
   `eligible_brand_yamls: 1`, which counts checked-in files rather than classifier-passing
   ones. Its three records are correct. This lane's generated artifact emits
   `eligible_brand_yamls: 0` plus explicit `checked_in_brand_yamls` / `active_brand_yamls`.

## Unblock Order (before any pilot)

1. Add `location_id` (+ the other missing scale columns) to a real, human-reviewed manifest.
2. Decide the brand-identity question: either the GHL pilot brands get active wizard YAMLs,
   or the registry's GHL rows change. **Do not** author placeholder YAMLs to make the
   dry-run go green — the block is the correct signal.
3. Land a redacted read-only snapshot (lane 05 / Pearl_Int) so a field diff can exist.
4. Only then: one operator-selected sandbox location, one `phoenix_last_sync_sha` write,
   readback, second dry-run no-op proof — gated on `OPERATOR_GHL_LIVE_PILOT_APPROVED`.

## Scale Shape

The 37-row manifest shape is supported without requiring 37 YAMLs: manifest rows with no
GHL-enabled registry row are inert, and rows without an active YAML block individually
rather than failing the run. Batch stop conditions stay as the spec defines them
(401/403, 422, 429, missing/duplicate mapping, failed readback, operator stop).
