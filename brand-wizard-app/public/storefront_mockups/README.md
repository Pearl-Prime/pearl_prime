# Pearl Prime Storefront V1 — UI Mockups

**Workstream:** `ws_pearl_prime_storefront_v1_ui_mockups_20260603`
**Authored:** 2026-06-06 (Pearl_Dev)
**Spec:** `docs/specs/PEARL_PRIME_STOREFRONT_V1_SPEC.md` §6 component inventory + §AMENDMENT-2026-06-04 deltas
**Parent merges:** [PR #1433](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1433) (V1 spec) · [PR #1446](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1446) (AMENDMENT-2026-06-04)

## What this directory contains

Twelve static HTML mockups + a shared stylesheet + demo SKU data + this README. Pure static content — no backend code, no Worker, no D1 wiring, no live Snipcart account. The mockups visualize what the storefront's component inventory looks like under the Pearl Prime visual identity so the operator can review the design language before the storefront frontend application code workstream begins.

```
storefront_mockups/
├── index.html                      # mockup-list landing page
├── locale_landing_en_US.html       # #1
├── locale_landing_ja_JP.html       # #2
├── header_preview.html             # #3 (both locale variants)
├── search_results_grid.html        # #4 (locale toggle)
├── product_detail_book.html        # #5 (locale toggle)
├── product_detail_audiobook.html   # #6
├── product_detail_manga.html       # #7
├── audiobook_sample_player.html    # #8
├── manga_preview_reader.html       # #9
├── cart_drawer_stub.html           # #10
├── account_library.html            # #11
├── review_form_guest.html          # #12
├── storefront.css                  # shared stylesheet — strict 7-token palette
├── storefront_demo_data.json       # 18 demo SKUs + Snipcart data-attribute schema
└── README.md                       # this file
```

## Operator review

Open `index.html` to see the mockup grid. Each card links to the corresponding mockup.

**Local preview (recommended):**

```bash
cd brand-wizard-app/public/storefront_mockups
python3 -m http.server 8000
open http://localhost:8000/index.html
```

**Deploy preview** (via existing `.github/workflows/brand-admin-onboarding-pages.yml`):

After merging this branch to `main`, the brand-admin-onboarding-pages CI deploys to Cloudflare Pages and the mockups become available at:

```
https://brand-admin-onboarding.pages.dev/storefront_mockups/index.html
https://brand-admin-onboarding.pages.dev/storefront_mockups/locale_landing_en_US.html
… etc
```

DO NOT run `wrangler` from a laptop — per `skills/pearl-int/references/cloudflare_pages_deploy.md` Traps 1-4, that bypasses the account-split routing and breaks future deploys.

## Pearl Prime token compliance

The shared stylesheet locks itself to the 7 design tokens from the spec §6.1 table verbatim. Every hex literal in `storefront.css` is one of these 7 values:

```
#0e0a06   --pp-bg          page background (deep warm near-black)
#faf6f0   --pp-text        primary text (off-white cream)
#d97706   --pp-accent      amber-600 — CTAs, ratings, focus, brand chips
#92400e   --pp-accent-soft amber-800 — hover
#a8a29e   --pp-muted       secondary text
#3f3530   --pp-border      card borders, dividers
#1a1410   --pp-card-bg     elevated card surface
```

Overlay/transparency uses `rgba()` derivations of those same 7 base values (e.g., `rgba(217, 119, 6, 0.12)` = `--pp-accent @ 12%`). No bespoke color introduced anywhere.

The inline SVG covers on the mockups also stay within the palette — gradients use only `#0e0a06`, `#1a1410`, `#3f3530`, `#92400e`, `#d97706`, `#faf6f0` stops.

**Audit command:**

```bash
cd brand-wizard-app/public/storefront_mockups
grep -oE '#[0-9a-fA-F]{6}' storefront.css *.html | \
  awk -F: '{print $2}' | sort -u
```

Expected output: only the 7 tokens above.

## Locale parity

The router prompt requires full ja-JP variants on at least mockups #1, #2, #3, #4, #5. This delivery has:

| # | en-US | ja-JP | Notes |
|---|---|---|---|
| 1 | YES — separate file | — | counterpart for #2 |
| 2 | — | YES — separate file | counterpart for #1 |
| 3 | YES | YES | both headers rendered in one file (component preview) |
| 4 | YES | YES | in-page locale toggle pill swaps the layout |
| 5 | YES | YES | in-page locale toggle pill swaps the PDP |
| 6 | YES | summary note + Noto JP CSS fallback | full ja-JP rendering at app-code ws |
| 7 | YES | summary note + Noto JP CSS fallback | full ja-JP rendering at app-code ws |
| 8 | YES | summary note + Noto JP CSS fallback | full ja-JP rendering at app-code ws |
| 9 | YES | summary note + Noto JP CSS fallback | full ja-JP rendering at app-code ws |
| 10 | YES | summary note + Noto JP CSS fallback | full ja-JP rendering at app-code ws |
| 11 | YES | summary note + Noto JP CSS fallback | full ja-JP rendering at app-code ws |
| 12 | YES | summary note + Noto JP CSS fallback | full ja-JP rendering at app-code ws |

ja-JP visual considerations applied across all mockups:
- Horizontal LTR only (no vertical writing mode at V1).
- Locale-aware font chain: `html[lang^="ja"]` switches body to `Noto Sans JP` and display to `Noto Serif JP`.
- JPY display: no decimal places, `¥` prefix (e.g., `¥520`).
- Brand chip labels use the `brand_locale_name` column from `artifacts/catalog/manga/ja_JP_manga_catalog.csv` (e.g., `静心社` for `stillness_press`).
- Phase-B/C locales (`zh-TW`, `zh-CN`, `ko-KR`) appear in the locale switcher dropdown as italic dashed "Coming soon" pills.

## Snipcart data-attribute schema

Every Buy-Now / Add-to-Cart button on the PDPs (mockups #5, #6, #7) carries Snipcart's HTML data attributes. The mockup uses `<snipcart-file-guid-placeholder>` for the file pointer — the real GUID is set up in the Pearl_Int Cloudflare wiring workstream.

| Attribute | Required | Purpose |
|---|---|---|
| `data-item-id` | YES | Unique SKU identifier — matches D1 `sku.sku_id` |
| `data-item-name` | YES | Title shown in the Snipcart cart drawer |
| `data-item-price` | YES | Decimal price in the SKU's currency. For JPY use whole-yen integer string (`"520"`). For USD use 2-decimal (`"4.99"`). |
| `data-item-url` | YES | Snipcart fetches metadata from this URL at cart-build time. Must be the canonical SKU detail page URL, i.e. `pearlprime.shop/{locale}/{product_type}/{brand_id}/{inner_key}`. |
| `data-item-file-guid` | YES (digital) | Snipcart-hosted file pointer; our Worker signs the R2 URL via webhook on `order.completed` per `§AMENDMENT-2026-06-04.3 §12/§13`. |
| `data-item-image` | RECOMMENDED | Cover image URL |
| `data-item-description` | OPTIONAL | Short blurb shown in cart drawer |

**Hybrid cart UX** (Q-PRP-CART-01 / `§AMENDMENT-2026-06-04.6`):

- `class="pp-btn-primary snipcart-checkout"` → Snipcart skips the drawer and goes straight to checkout (Buy-Now flow).
- `class="pp-btn-secondary snipcart-add-item"` → Snipcart opens the drawer (Add-to-cart flow, mockup #10).
- Cart icon always visible in header with item-count badge.

## Demo data

`storefront_demo_data.json` carries:

- **18 SKUs total** — 8 en-US books + 4 ja-JP books + 1 en-US + 1 ja-JP audiobook + 2 en-US + 2 ja-JP manga.
- All titles, subtitles, brand IDs, topics, personas, and series IDs are sourced from real catalog rows:
  - `artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv`
  - `artifacts/catalog/manga/en_US_manga_catalog.csv`
  - `artifacts/catalog/manga/ja_JP_manga_catalog.csv`
- Brand chip rails (en-US + ja-JP) reference real entries from `config/manga/canonical_brand_list.yaml` (Path X 37) plus one music brand from `config/music/music_brand_registry.yaml`.
- ja-JP `brand_locale_name` values come from the catalog CSV (e.g., `静心社` for `stillness_press`).
- Sample reviews in both locales are illustrative (per the spec they would be user-authored content).

## What lives in the next ws

This is mockup scope only. None of the following is implemented here — it lives in the next workstreams:

- **`storefront/frontend/`** — the production frontend app (React/Astro/etc, TBD)
- **Cloudflare Worker routes** — `/api/catalog`, `/api/search`, `/api/sku/:id`, `/api/review`, `/api/webhook/snipcart` (Pearl_Int CF wiring ws)
- **D1 schema migrations** — `sku`, `order`, `order_item`, `review`, `subscription` tables (Pearl_Int)
- **Real Snipcart account + file GUIDs** (Pearl_Int)
- **Catalog projector script** (`scripts/storefront/project_skus.py`) (Pearl_Int)
- **CTA redirect unification across `funnel/`, freebie surfaces, email YAMLs, social CTAs** (Pearl_Marketing CTA ws — already running in parallel)
- **Atom audit (§15)** (Pearl_Writer atom audit ws — already running in parallel)

## Parallel-ws operational notes

Per the router prompt, four sibling agent sessions are working concurrently on:

- **Pearl_Int** — CF Pages + Workers + D1 + Snipcart wiring scaffold
- **Pearl_Writer** — atom audit for `§15` external-book references
- **Pearl_Marketing** — paid-CTA cutover across funnel + freebie surfaces
- **Pearl_PM** — coordination tracker updates

Pearl_Dev (this ws) stays scoped to the mockup files in this directory. No changes to:
- `artifacts/coordination/*.tsv` (Pearl_PM owns post-merge updates)
- `config/manga/canonical_brand_list.yaml` (FROZEN — read-only)
- `funnel/` (Pearl_Marketing owns)
- `brand-wizard-app/public/free/` (Pearl_Marketing owns)
- `somatic_exercise_freebee_apps/` (Pearl_Marketing owns)

## Verification

Token-conformance audit (run from this directory):

```bash
grep -ohE '#[0-9a-fA-F]{6}' storefront.css *.html | sort -u
```

Should print exactly these 7 lowercase hex values, in alphanumeric order:

```
#0e0a06
#1a1410
#3f3530
#92400e
#a8a29e
#d97706
#faf6f0
```

Any other hex code is a token violation — fix before deploy.

## Open questions for operator review

1. Are the 7 design tokens applied correctly on every mockup? Any chrome we should iterate?
2. Is the ja-JP type chain (`Noto Serif JP` for display, `Noto Sans JP` for body) reading as we want it to on the locale_landing_ja_JP page in particular?
3. Are the inline SVG cover placeholders acceptable for mockup review, or do you want real cover art (would require a follow-up render pass from the cover-art pipeline before deploy)?
4. Snipcart drawer styling (mockup #10) — is the "Pearl-Prime-skinned-Snipcart" balance right, or do we want a more clearly delineated boundary between "our UI" and "Snipcart UI"?
5. Audiobook + manga preview UX (mockups #8, #9) — do these accurately reflect the experience you want at Phase A launch?

Reply on the PR with feedback and the next ws (Pearl_Dev storefront frontend application code) can start.
