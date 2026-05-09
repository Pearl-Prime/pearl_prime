# config/marketing — Marketing-owned policy YAMLs

This directory holds **marketing-owned** numeric and language policy SSOTs.
**Do not** put platform caps, pipeline mix mechanics, or release-velocity ramps
here — those live under `config/release_velocity/` and `config/catalog/` respectively.

## Files

### Volume SSOT (V1)

| File | Role |
|------|------|
| `weekly_volumes_per_brand.yaml` | **SSOT** for marketing weekly volume targets. Per-brand × per-content-surface (`ebook`, `audiobook`, `manga`, `podcast`, `video`, `shorts`) weekly intent. Authored per `docs/specs/MARKETING_VOLUME_SSOT_V1_SPEC.md` (the binding template). |

### Other marketing policy

| File | Role |
|------|------|
| `marketing_assumptions.yaml` | Funnel / conversion / LTV assumptions for projections and dashboards. **Not** a volume SSOT. |
| `consumer_language_by_topic*.yaml` | Per-topic / per-locale consumer language banks. |
| `invisible_scripts_by_persona_topic.yaml` | Persona × topic invisible-script bank. |
| `brand_id_alias_map.yaml` | Brand-ID alias mapping. |
| `v32_*.yaml` | v3.2 marketing wiring (audiobook dominance, contrast config, EOIs, QA checklist, social wiring, transformation promise, chaos slot). |

## Authority and provenance

- **Spec (binding template):** [`docs/specs/MARKETING_VOLUME_SSOT_V1_SPEC.md`](../../docs/specs/MARKETING_VOLUME_SSOT_V1_SPEC.md)
- **Discovery report:** [`artifacts/qa/marketing_volume_ssot_discovery_2026-05-09.md`](../../artifacts/qa/marketing_volume_ssot_discovery_2026-05-09.md) (OUTCOME-B)
- **Project:** PRJ-WORLDWIDE-CATALOG-GO-LIVE-V1 / WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01
- **Owner agent:** Pearl_Marketing (authoring); Pearl_PM (governance / program alignment).

## Cross-references — what NOT to confuse with this SSOT

The following sibling files encode **adjacent** but distinct semantics; they are
**not** volume SSOTs and **must not** be edited from this directory:

| File | Authoritative for | Authority doc |
|------|-------------------|---------------|
| `config/release_velocity/safe_velocity.yaml` | **Platform caps** (Google Play Books, Findaway Voices, Ximalaya). Hard constraints; schedulers fail-hard if exceeded. **Read-only** from the volume-SSOT perspective. | `docs/RELEASE_VELOCITY_AND_SCHEDULE.md` |
| `config/release_velocity/velocity_ramp.yaml` | Aspirational ramp (70–84 books/week/brand at steady state, capped by `safe_velocity.yaml`). | `docs/RELEASE_VELOCITY_AND_SCHEDULE.md` |
| `config/release_velocity/lanes.yaml` | EN vs ZH24 lane definition for per-lane cap resolution. | `docs/RELEASE_VELOCITY_AND_SCHEDULE.md` |
| `config/catalog/weekly_queue_config.yaml` | Pipeline mix mechanics — how the weekly basket is composed (lane mix, locale mix). Not a volume SSOT. | (mechanical, in-line comments) |
| `config/video/upload_schedule.yaml` | Upload cadence; derives per-platform video load from book assumption. | (mechanical) |
| `config/podcast/platform_distribution.yaml` | Per-brand-type podcast distribution knobs. | (mechanical) |
| `config/manga/japan_dual_track_config.yaml` | JP regional pipeline cap (`weekly_cap`) + dual-track ebook/manga counts. | (regional pipeline) |
| `config/manga/korea_webtoon_config.yaml` | KR regional pipeline cap. | (regional pipeline) |
| `config/manga/canonical_brand_list.yaml` | **Path X canon** — 37 manga brands. Brand list source for `weekly_volumes_per_brand.yaml`. | `specs/MANGA_CATALOG_RECONCILIATION_SPEC.md` |

## Cap reconciliation — how this SSOT interacts with `safe_velocity.yaml`

Per spec §3 #2 (OUTCOME-B supersession rule):

> Platform caps in `config/release_velocity/safe_velocity.yaml` remain hard
> constraints — schedulers and release tooling clamp effective throughput; if
> a marketing target exceeds a platform cap, the consumer surfaces both numbers
> (target vs cap) or fails validation in CI.

This means:

1. `weekly_volumes_per_brand.yaml` expresses **marketing INTENT**, not effective
   throughput.
2. Platform caps in `safe_velocity.yaml` are **hard constraints** for schedulers
   and release tooling.
3. Consumers (exec catalog dashboard, brand admin weekly panels, weekly packaging
   summaries, schedulers) **must clamp** marketing targets against
   lane-applicable safe-velocity caps; per-lane resolution is governed by
   `config/release_velocity/lanes.yaml`.
4. Mismatches are surfaced at the consumer (target vs cap), or fail validation
   in CI per Pearl_Dev policy choice.

**This SSOT does not inline cap values.** The link is by reference only:
`weekly_volumes_per_brand.yaml::safe_velocity_link`.

## Authoring workflow (per spec §5)

1. **Owner:** Pearl_Marketing fills `weekly_volumes_per_brand.yaml` from the
   operator-ratified marketing sheet ("Table 6").
2. **Cadence:** Update on program cadence (weekly marketing review) or when
   operator revises Table 6; bump `last_updated` every edit.
3. **Recommended CI checks** (future, not implemented in V1):
   - Every `brand_id` ∈ `config/manga/canonical_brand_list.yaml` (or program-scoped
     brand registry).
   - No duplicate (`brand_id`, `surface`) pairs at the row level.
   - `weekly_target` non-negative integers; `unit` valid for `surface` if used.
   - Optional: cross-check sum of `ebook` + `audiobook` against `safe_velocity`
     min/max for the dominant platform lane — warn on exceed; error if program
     chooses a hard gate.
4. **Promotion:** `status: draft` → `status: active` only after Pearl_PM +
   operator acknowledgment in a program amendment or PR comment. Per spec §2.1,
   only `active` may drive production UIs without a warning banner.

## Consumer integration pattern (non-code contract; per spec §4)

| Consumer | Expected read |
|----------|---------------|
| `brand-wizard-app/public/exec_catalog_dashboard.html` (Surface 8) | Fetch or embed build artifact generated **from** SSOT + registry join; **no** hard-coded `MARKETS[]` weekly literals for targets. |
| `brand_admin.html` / weekly OS surfaces (Surface 2) | Locale grid + per-surface columns from SSOT join. |
| `scripts/release/build_admin_packets.py` and weekly packaging (Surface 3) | Include SSOT slice in operator bundle JSON/markdown. |
| Catalog planners / queue builders | Treat SSOT as **upper intent**; enforce `safe_velocity` and regional caps as **downstream** constraints. |

**Join keys:** `brand_id`, `surface`, plus `active` flag from Surface 4 SSOT
(`ws_worldwide_gl_s04_active_brand_ssot_20260508` lineage).

## Status

- `weekly_volumes_per_brand.yaml` V1 baseline: `status: draft` (37 brands,
  conservative starter values; all surfaces = 0 except `manga` = 1/week per
  brand). Promotion to `active` awaits operator Table 6 ratification.
