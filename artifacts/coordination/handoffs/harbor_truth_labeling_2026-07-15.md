# Harbor Line truth labeling — Lane 08 (Pearl_Brand) — 2026-07-15

Signal: `harbor-line-production-truth-labeling`

## Honest status

- `HARBOR_READY_100PCT=no`
- `PRODUCTION_DELIVERY_LIVE=no`

Harbor Line Books (`stabilizer`) / Brand Director Kamiko Parker is **ASSIGNED**, catalog is
**24 titles of catalog metadata only**. `production_files_ready: false`,
`delivery_status: catalog_ready_production_files_pending`. **No production files were generated
by this lane and none exist.** This lane changed *presentation and enforcement only* — it did not
move readiness data.

## The real defect found (not just a copy fix)

The packet bridge (`brand_admin_weekly_packets.json`) is regenerated **independently** of the
delivery feed (`brand_deliveries/stabilizer.json`). On `origin/main` a bridge `buildable` verdict
**silently outranked** `production_files_ready: false`:

```js
// origin/main — brand_handoff_dashboard.html boot()
PACKET_BLOCK = packetBridgeStatus(id);              // -> {state:"ready"} when bridge says buildable
if (!PACKET_BLOCK && REAL_DELIVERY && REAL_DELIVERY.production_files_ready === false) { ... }
//  ^^^^^^^^^^^^ truthy "ready" verdict => the production-pending guard never runs
```

`brand_admin_weekly_os.html` was worse: `packetStatus()` had **no delivery awareness at all** and
checked `buildable` first, so it would render **"Download Week 1 Package"** for books that had
never been rendered.

Harbor is labeled correctly *today* only because the bridge happens to list `stabilizer_en_us` as
blocked. That was incidental, not enforced — one bridge regeneration away from presenting catalog
metadata as shippable production books. Reproduced by execution before fixing (`node`, scenario
"bridge says buildable"): result `{"state":"ready"}` with `production_files_ready=false`.

## Fix — label, don't hide

`production_files_ready === false` is now **authoritative** on both surfaces. A bridge verdict can
only ever *add detail* to a pending reason; it can never clear one.

- `brand-wizard-app/public/brand_handoff_dashboard.html` — new `resolvePacketBlock(bridgeVerdict, delivery)`;
  `boot()` uses it. Lane-suffix regex widened to all 14 registry lanes (4 lanes — `de_de`, `fr_fr`,
  `it_it`, `hu_hu` — previously never loaded the delivery feed at all, silently skipping the guard).
- `brand_admin_weekly_os.html` (**repo-root canonical**) — added `DELIVERY` + `loadDelivery()` +
  `deliveryBase()`; `packetStatus()` now treats production-pending as authoritative and checks
  blocked before buildable. `initBrand()` is now `async` and awaits the delivery feed **before**
  `renderPhase2()`, so the packet card can never render ahead of the flag.
- Public copy regenerated via `scripts/onboarding/sync_onboarding_config_to_public.sh`
  (root canonical -> public; direction confirmed against `check_brand_admin_weekly_os_public_sync.py`).

Catalog metadata remains **fully visible** and metadata CSVs remain downloadable. Hide-until-ready
is operator-tier and has **not** been ratified — it was not implemented, and the gate actively
forbids over-blocking.

## Enforcement (memory is recall, not enforcement)

`scripts/ci/check_harbor_production_truth_labeling.py`, wired into **Drift detectors** (required
check) and covered by `tests/test_harbor_production_truth_labeling.py`.

The gate is **behavioural, not a marker grep**: it extracts the real guard functions from the
shipped HTML and executes them under `node` against a synthetic "bridge says buildable" bridge.
It asserts, per surface:

1. `production_files_ready=false` + bridge `buildable` => `state === "blocked"` (catalog-as-production).
2. `production_files_ready=true` => `state === "ready"` (**forbids blanket hiding** — label, don't hide).
3. Data invariant: a production-pending feed must carry a pending `delivery_status`, and no book
   inside it may claim `production_files_ready: true`.

Teeth verified by deliberately reintroducing each defect — all four fail as intended:

| Injected defect | Gate |
|---|---|
| origin/main precedence restored (handoff) | FAIL ✓ |
| weekly OS ignores delivery flag | FAIL ✓ |
| over-block / blanket hide | FAIL ✓ |
| book over-claims production ready | FAIL ✓ |
| (all restored) | PASS ✓ |

## Proof — observed, not asserted

Local static serve (`python3 -m http.server`) + browser, both surfaces, `?brand=stabilizer_en_us`:

- Weekly OS Phase 2: renders **"Catalog ready, production files pending."**, **no download button**
  (`hasDownloadButton: false`), catalog metadata still shown.
- Handoff dashboard: **"Production files pending"**, **"CATALOG READY, PRODUCTION FILES PENDING"**,
  "24 titles in catalog", all 24 titles listed, metadata CSV still enabled.
- **Regression scenario forced live** on both (`PACKET_BRIDGE` overridden to `buildable`): both stay
  `state: "blocked"`, no download offered, catalog metadata still visible.

Reproduce:

```bash
python3 scripts/ci/check_harbor_production_truth_labeling.py
PYTHONPATH=. python3 -m pytest tests/test_harbor_production_truth_labeling.py -q
python3 -m http.server 8791   # then open:
#   /brand_admin_weekly_os.html?brand=stabilizer_en_us
#   /brand-wizard-app/public/brand_handoff_dashboard.html?brand=stabilizer_en_us
```

## Scope discipline

Not touched: `brand_admin.html` renders books via the live
`/api/brand_admin/brand/<bid>/books_by_platform` API (server-side status), not the static delivery
feed — out of scope for a static UI/data PR. Waystream was **not** relabeled; `way_stream_sanctuary`
and `stabilizer` remain distinct feeds.

## Next action

Harbor production delivery stays **not live**. To move `production_files_ready` to `true`, render
real EPUB/cover/audio/manga assets and let `scripts/onboarding/gen_brand_deliveries.py` regenerate
the feed from bytes on disk — never by hand-editing the flag. The gate will then require every book
in the feed to back the claim.

Follow-up (not blocking): `brand_admin.html`'s live `books_by_platform` API surface has no
production_files_ready awareness; worth auditing when that API is next touched.
