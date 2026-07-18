# Brand Admin active classifier consumer — handoff (2026-05-09)

**Project:** PRJ-WORLDWIDE-CATALOG-GO-LIVE-V1
**Workstream:** `ws_brand_admin_active_brand_consumer_20260509`
**Producer SSOT:** PR #972 (commit `10ed203bd6`) — `scripts/brand/active_brand_classifier.py`
**Spec:** `docs/specs/ACTIVE_BRAND_SSOT_V1_SPEC.md`
**Surface wired:** `brand_admin.html` (root, Pearl_Prime book pipeline)
**Author:** Pearl_Brand (Pearl_Conductor 2026-05-09 autonomous wave)

---

## 1. What this handoff documents

The minimal-change consumer pattern landed in `brand_admin.html` so that downstream consumers
(catalog generator, weekly packaging, exec dashboard, music-mode wizard) can mirror it
verbatim. The pattern is intentionally tiny — three additive blocks, one call site.

---

## 2. Pattern (4 additive blocks)

### 2.1 CSS pills + inactive dimming (block 1)

Add next to the existing `.brand-card` rules:

```css
.brand-card.inactive{opacity:.55}
.brand-card.inactive:hover{opacity:.85}
.brand-card .ab-pill{font-family:var(--mono);font-size:.4rem;letter-spacing:.05em;text-transform:uppercase;padding:1px 6px;border-radius:3px;margin-top:5px;margin-left:5px;display:inline-block}
.brand-card .ab-pill.active{color:var(--green);border:1px solid rgba(74,222,128,.4);background:rgba(74,222,128,.08)}
.brand-card .ab-pill.inactive{color:var(--red);border:1px solid rgba(248,113,113,.3);background:rgba(248,113,113,.05)}
.ab-counts-line{font-family:var(--mono);font-size:.5rem;color:var(--dim);letter-spacing:.05em;margin-bottom:14px}
.ab-counts-line strong.active{color:var(--green)}
.ab-counts-line strong.inactive{color:var(--red)}
```

### 2.2 `AB_SNAPSHOT` + classifier helpers (block 2)

Inserted at the top of the page `<script>` block:

- `AB_SNAPSHOT` — inline default, ships with `brands: []` until
  `brand-wizard-app/brands/<id>.yaml` bundles land (Phase 1 of
  `ACTIVE_BRAND_SSOT_V1_SPEC` §4).
- `abEndpointUrl()` — resolves a live JSON URL from
  `?ab_endpoint=` query, then `window.__ACTIVE_BRAND_DASHBOARD_URL`,
  else returns `null` (inline-only mode).
- `abApplySnapshot(snap)` — populates `AB_STATUS` from a snapshot of
  shape `{brands: [{brand_id, status, reason}]}` (matches
  `scripts/brand/dashboard_classifier_endpoint.py --json`).
- `abIsActive(brand_id)` / `abReason(brand_id)` — predicates consumers gate on.
- `abLoadAndRefresh()` — applies inline snapshot synchronously, then opportunistically
  fetches a live URL when configured. Failures keep the inline snapshot.

### 2.3 `renderPicker()` gating (block 3)

Replace the brand-card loop with an active-first partition:

```js
const entries=Object.entries(B);
const active=entries.filter(function(e){ return abIsActive(e[0]); });
const inactive=entries.filter(function(e){ return !abIsActive(e[0]); });
const ordered=active.concat(inactive);
// counts line + per-card class + ab-pill ...
```

Order rule: **active first, declared order within each bucket**. No re-sort by name —
operator declared-order is meaningful in `B`.

### 2.4 `init()` call site (block 4)

Single line at the top of `init()`:

```js
abLoadAndRefresh();
```

Sync inline-snapshot apply ensures the picker renders gated on first paint;
the optional fetch refresh repaints when it lands.

---

## 3. Runtime contract (matches PR #972 sibling endpoint)

`fetch(<ab_endpoint>)` must return JSON of shape:

```json
{
  "schema_version": 1,
  "generated_at": "2026-05-09T...Z",
  "brands": [
    { "brand_id": "...", "status": "active|inactive", "reason": "..." }
  ]
}
```

The same shape is emitted by
`PYTHONPATH=. python3 scripts/brand/dashboard_classifier_endpoint.py --json`
or the `--serve` HTTP helper at `http://127.0.0.1:8765/active-brand-dashboard.json`.

**Local dev:**

```bash
PYTHONPATH=. python3 scripts/brand/dashboard_classifier_endpoint.py --serve
# Then open: brand_admin.html?ab_endpoint=http://127.0.0.1:8765/active-brand-dashboard.json
```

**Static-site override (no helper):** publish a JSON snapshot artifact and wire
`window.__ACTIVE_BRAND_DASHBOARD_URL` from a deploy-time `<script>`.

---

## 4. Why empty `brands: []` is correct today

Per `artifacts/qa/active_brand_ssot_implementation_2026-05-09.md` §4:
no `brand-wizard-app/brands/<id>.yaml` bundles are committed on `main` as of
2026-05-09. The classifier therefore reports **0 active / 61 inactive**. The
inline `AB_SNAPSHOT.brands: []` reflects this exactly: the picker shows
all 24 brand cards as **Inactive** with the canonical reason
`no brand_wizard YAML found` in the hover title. Cards remain clickable so
admins can still proceed; the gate is **visibility weight + status pill +
ordering**, not hard removal.

When wizard bundles land in a follow-up PR, either:

1. Regenerate `AB_SNAPSHOT` inline from
   `PYTHONPATH=. python3 -c "from scripts.brand.dashboard_classifier_endpoint import build_payload; import json; print(json.dumps(build_payload(), indent=2))"`,
   **or**
2. Run the helper / publish the JSON artifact and wire the override.

---

## 5. Mirror this pattern for downstream consumers

| Workstream | Surface | Mirror notes |
|------------|---------|--------------|
| `ws_dashboard_active_brand_consumer_20260509` | `brand-wizard-app/public/brand_admin.html` | **Already shipped** in PR #972 sibling commit (`1ec019ad48`); uses the live HTTP helper rather than inline snapshot. |
| `ws_catalog_generator_active_brand_consumer_20260509` | `scripts/catalog/...` (Python) | Use `from scripts.brand.active_brand_classifier import is_active` directly — no JS layer needed. |
| `ws_weekly_packaging_active_brand_consumer_20260509` | `scripts/release/build_admin_packets.py` | Same Python import; gate per-brand packet inclusion on `is_active(brand_id)`. |
| Surface 8 exec dashboard | `brand-wizard-app/public/exec_catalog_dashboard.html` | Mirror the dashboard panel pattern (PR #972 sibling) for live executive view; uses HTTP helper. |
| Music-mode wizard (cap MUSIC-MODE-BRAND-INTEGRATION-V1-01) | `brand-wizard-app/public/...` | Inherits the same SSOT once `config/music/music_brand_registry.yaml` lands; classifier already tolerates absence. |

---

## 6. Out of scope for this PR

- `brand_admin_weekly_os.html` (Surface 2 broader binding — separate ws)
- `brand-wizard-app/public/brand_admin.html` (PR #972 sibling, already shipped)
- `config/brand_registry.yaml`, `config/manga/canonical_brand_list.yaml`, any wizard YAML (read-only boundary)
- Any backend/server code
- Refactor of `brand_admin.html` structure beyond the four additive blocks

---

## 7. Verification

Open `brand_admin.html` in a browser:

- Expected today: counts line shows **0 active / 24 inactive / 24 total**
  (the page only includes the 24 en_US Pearl_Prime book brands; the broader
  61-brand classifier universe spans other registries).
- All 24 cards render dimmed (`opacity:.55`) with red **Inactive** pills.
- Hover any card: tooltip shows `no brand_wizard YAML found`.
- Cards remain clickable (`selectBrand(bid)` unchanged).

When bundles land or the helper is running with `?ab_endpoint=...`, the
counts line, pill colors, and ordering update in place.
