# Onboarding Output Proof System

**Purpose:** Define how **real and honestly labeled** examples feed brand-admin onboarding and the decision wizard: registry as source of truth, **`status`-driven UX**, proof-pending when assets are absent or broken, and integration with Cloudflare-hosted delivery.

**Related docs:**

- [ONBOARDING_REAL_EXAMPLE_GENERATION_SPEC.md](./ONBOARDING_REAL_EXAMPLE_GENERATION_SPEC.md) — what to generate, comparison sets, `proof_intent` / `production_fidelity` / `product_family`.
- [BRAND_ADMIN_ONBOARDING_WIZARD_SPEC.md](./BRAND_ADMIN_ONBOARDING_WIZARD_SPEC.md) — wizard steps and components.
- [docs/BRAND_ADMIN_ONBOARDING_PAGES_SPEC.md](../docs/BRAND_ADMIN_ONBOARDING_PAGES_SPEC.md) — static page shells.
- [docs/ONBOARDING_EXAMPLE_PRODUCTION_CHECKLIST.md](../docs/ONBOARDING_EXAMPLE_PRODUCTION_CHECKLIST.md) — production phases.
- [docs/BRAND_ADMIN_ONBOARDING_CLOUDFLARE_DEPLOYMENT.md](../docs/BRAND_ADMIN_ONBOARDING_CLOUDFLARE_DEPLOYMENT.md) — deploy and JSON sync.
- [BRAND_ADMIN_CANONICAL_PACKAGE.md](../BRAND_ADMIN_CANONICAL_PACKAGE.md) — canonical entry governance.
- Config: [config/onboarding/example_registry.json](../config/onboarding/example_registry.json), [config/onboarding/wizard_decision_explainer_data.json](../config/onboarding/wizard_decision_explainer_data.json).

---

## 1. Core rules

1. **Prefer real pipeline outputs** over decorative stock. See Real Example Generation Spec for `production_fidelity` and three visual categories.
2. **JSON-first:** `config/onboarding/*.json` is canonical in repo; CI may sync copies into `brand-wizard-app/public/onboarding/` before Vite build.
3. **No silent failure:** UI must render for every registry row regardless of asset presence.

---

## 2. Registry `status` (primary UX driver)

Every row includes:

```text
status: "ready" | "planned" | "missing"
```

| Value | UI behavior |
|-------|-------------|
| `ready` | Attempt to show asset; on load error → treat as proof-pending (see §4). |
| `planned` | Show metadata + “Proof pending” (planned). |
| `missing` | Show metadata + “Proof pending” (not yet generated). |

**Optional `asset_exists` (boolean):** operational metadata only. **Do not** branch UX on `asset_exists` when `status` is set; `status` wins.

---

## 3. Required registry semantics (summary)

Full schema: [ONBOARDING_REAL_EXAMPLE_GENERATION_SPEC.md §8](./ONBOARDING_REAL_EXAMPLE_GENERATION_SPEC.md#8-registry-schema-normalized-fields).

Minimum mental model:

- **`proof_intent`:** `ships_product` | `teaches_persona` | `teaches_topic` | `teaches_comparison`
- **`production_fidelity`:** `production` | `pipeline_demo` | `supporting_visual`
- **`product_family`:** links row to generating system (`book_engine`, `manga`, `pearl_news`, …)
- **`comparison_set_id`:** groups tiles for comparison boards (`cmp_*` v1 sets in Real Example Spec §3.3)

---

## 4. Proof-pending and stale-`ready` behavior

**Rule:** No component may **require** an on-disk or HTTP-resolvable asset to render.

- If `status !== "ready"`: always show label, metadata badges (lane, market, persona, topic, format), and **Proof pending**.
- If `status === "ready"` but image (or asset) **fails to load**: show the **same** proof-pending placeholder; **React:** `img` `onError` handler; **optional** `console.warn` in **development** only.
- **HTML galleries:** use `onerror` on `img` or equivalent.

This allows shipping onboarding before the full example library exists.

---

## 5. Integration points

| Consumer | Behavior |
|----------|----------|
| `lane_examples_gallery.html` (scaffold) | Fetch or embed registry; render grid with §4 fallbacks. |
| `BrandWizard.jsx` / `OutputProofStrip` | Resolve `exampleIds`; apply §4. |
| WordPress (optional shell) | Link or iframe to Cloudflare-hosted app; do not duplicate registry JSON as source of truth. |
| Cloudflare Pages | Serve built app + static JSON under `/onboarding/*.json`. |

---

## 6. Quality rules (proof, not decoration)

1. Every image or asset must **teach** a decision (who, what lane, what tradeoff)—see Real Example Spec.
2. **Caption** must match asset type (no “cover” label on a persona mood shot).
3. Comparison-set members must share the documented fixed dimensions per [ONBOARDING_REAL_EXAMPLE_GENERATION_SPEC.md §3.3](./ONBOARDING_REAL_EXAMPLE_GENERATION_SPEC.md#33-locked-first-comparison-sets-v1-contract).

---

## 7. Out of scope

- Exact pipeline CLI commands per `product_family` (owned by Pearl_Dev / visual pipelines).
- Branch protection classification for Cloudflare Pages checks (Pearl_GitHub decision per deployment doc).
