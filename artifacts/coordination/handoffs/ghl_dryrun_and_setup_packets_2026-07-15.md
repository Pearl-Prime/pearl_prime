# Handoff — GHL Dry-Run Sync + Setup Packets (Lane 06)

- date: 2026-07-15
- agent: Pearl_Dev (Pearl_Int review hat)
- lane: `06_ghl_dryrun_and_setup_packets`
- branch: `agent/ghl-dryrun-packets-20260715` (based on `origin/main` `5472f4a517345ec9fbfc158f1562efd3667a9a26`)
- **LIVE_WRITES=none** — no GHL API call of any kind was made. No credential was read.
- signal: `ghl-yaml-sync-dryrun-and-packets`

## What Shipped

| Path | Purpose |
|---|---|
| `scripts/ghl/yaml_sync_inputs.py` | Read-only loaders + code field map + secret guard. |
| `scripts/ghl/yaml_sync_dry_run.py` | Fail-closed desired-state diff CLI (JSON + human table). |
| `scripts/ghl/build_setup_packet.py` | GHL admin setup packet CLI (PACKET.md + packet.json). |
| `tests/ghl/` (67 tests, ~3s) | Fail-closed join, secret guard, field-map drift gate, no-network gate. |
| `tests/fixtures/ghl/snapshot_sandbox_example.json` | Synthetic snapshot. Not a real location. |
| `docs/ghl/GHL_YAML_SYNC_DRY_RUN_RUNBOOK.md` | Commands, fail-closed order, findings, unblock order. |
| `artifacts/ghl/yaml_subaccount_sync_20260715/dry_run_diff_origin_main.{json,txt}` | Byte-verified run against main. |
| `artifacts/ghl/setup_packets_20260715/` | 4 packets, all truth-labeled `BLOCKED`. |

## Smoke -> Pilot -> Scale (what was actually run)

- **Smoke — DONE.** `stabilizer_en_us` (the one wizard YAML on main): packet generated,
  readiness `BLOCKED`, blockers enumerated. Brand director Kamiko Parker / `kamiko_parker`
  / `assigned` resolved from the YAML.
- **Pilot — NOT POSSIBLE, one-brand proof kept.** Zero additional active YAMLs exist on
  main, so there is no set of "up to 3 active YAMLs" to run. Packets were still generated
  for the 3 GHL-enabled registry rows (`stillness_press`, `devotion_path`,
  `way_stream_sanctuary`), all `BLOCKED` on missing YAML. No fake YAML was created.
- **Scale — SHAPE PROVEN IN TEST.** A 37-row manifest is parsed and evaluated without
  requiring 37 YAMLs (`test_thirty_seven_row_manifest_shape_is_supported_without_all_yamls`).

## Findings (the dry-run failing closed IS the result)

1. **YAML/registry mismatch — CONFIRMED.** One checked-in YAML (`stabilizer_en_us`) vs
   three GHL pilot rows (`stillness_press`, `devotion_path`, `way_stream_sanctuary`).
   All three -> `blocked_missing_active_yaml`. 0 updates, 0 creates. This reproduces the
   merged `dry_run_diff_example.json` records exactly.
2. **Zero classifier-active YAMLs — NEW.** `stabilizer_en_us` also fails
   `active_brand_classifier`: `brand_id` is not in the classifier universe
   (`config/brand_registry.yaml` carries `stabilizer_tw/hk/cn/sg`), and the file has
   `display_brand` (not `display_name`) and no `wizard_core.tagline`. Per the spec's own
   eligibility rule, main has **0 eligible YAMLs, not 1**.
3. **Manifest cannot map a location — NEW.** `docs/handoffs/ghl_location_manifest.example.tsv`
   has no `location_id` column. Even a perfect YAML+registry join blocks at
   `blocked_missing_location_mapping`. Missing scale columns: `location_id`,
   `phoenix_managed_custom_value_ids`, `last_readback_at`, `last_sync_sha`, `rollback_note`.
4. **Merged docs disagree on one safety class — NEW.** Spec Field Policy says
   `phoenix_brand_display_name` is "`phoenix_managed` with review"; the field map says
   `operator_approval_required`. Code follows the field map (stricter) and a drift test
   pins it. **Needs an owner ruling to reconcile the two merged docs.**
5. **Merged example summary overcounts — NEW.** `dry_run_diff_example.json` says
   `eligible_brand_yamls: 1` (counting checked-in files, not classifier-passing ones).
   Records are correct; only the summary is off. Not edited by this lane — reported for
   the owning lane. This lane's artifact emits `eligible_brand_yamls: 0` plus explicit
   `checked_in_brand_yamls` / `active_brand_yamls`.

## Safety Properties (test-pinned, not convention)

- No network library import anywhere in `scripts/ghl/` (AST-checked).
- No `os.environ` / `getenv` / keyring / dotenv read (regex-checked).
- Only subprocess is local `git rev-parse` (parse-checked); no curl/wget/Popen.
- Webhook URL values never enter a diff or packet; only the env NAME. `webhook_env` is
  `phoenix_only` — no GHL custom value targets it.
- Presigned/signed URLs and token shapes are blocked + redacted on both desired and
  current values.
- Location ids hashed by default; `--reveal-location-ids` is local-only.
- `_assert_packet_clean()` raises rather than writing a packet containing a secret.
- Secret scan over every generated artifact: clean.

## Next Actions (owner / lane 07)

1. **Do not** author placeholder brand YAMLs to turn the dry-run green. The block is the
   signal. Decide instead: do the GHL pilot brands get real wizard YAMLs, or does the
   registry's GHL row set change?
2. Add `location_id` + the missing scale columns to a real, human-reviewed manifest
   (the `.example.tsv` is not a manifest).
3. Rule on finding 4 (display-name safety class) and correct the losing doc.
4. Correct `eligible_brand_yamls` in the merged example (finding 5).
5. Lane 05 / Pearl_Int: land a redacted read-only snapshot so a field-level diff can exist.
6. Lane 07 live pilot stays blocked until 1-5 land AND the operator gives the exact phrase
   `OPERATOR_GHL_LIVE_PILOT_APPROVED`. Pilot field: `phoenix_last_sync_sha` only.
