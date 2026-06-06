# Pearl Prime Storefront V1 — Specification

**Status:** draft — awaits operator ratification (Q-PRP-* in §17)
**Owner:** Pearl_Architect (spec) + Pearl_Int (operations) + Pearl_Dev (UI) + Pearl_Marketing (CTA unification) + Pearl_Writer (atom audit)
**Cap entry:** `PEARL-PRIME-STOREFRONT-V1-01` in `docs/PEARL_ARCHITECT_STATE.md`
**Project:** `PRJ-PEARL-PRIME-STOREFRONT-V1` in `artifacts/coordination/ACTIVE_PROJECTS.tsv`
**Subsystem:** `storefront` (new — see `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv`)
**Authored:** 2026-06-03
**Last updated:** 2026-06-03

---

## §1 — Purpose + Non-Goals

### 1.1 Purpose

Author the V1 contract for **Pearl Prime Storefront** — a Pearl-Prime-branded **book + audiobook + manga + music** marketplace that becomes the **single call-to-action destination** for every paid Pearl Prime content purchase across the entire ecosystem.

The storefront unifies what is today a fragmented funnel surface: paid CTAs that today point at Amazon KDP, Google Play Books, Apple Books, Kobo, Spotify, Audible, Google Play Audiobooks, and WEBTOON Canvas will, on Phase 1 launch, **all** resolve to per-SKU canonical URLs on the storefront. External-platform discovery remains valuable for **acquisition** (operator decision Q-PRP-CTA-UNIFY-01 governs the cutover cadence), but **monetization** consolidates here.

Pearl Prime's catalog is large enough — Path X 37 manga brands × 5 locales × {book, audiobook, manga, music} plus 38+ music-mode brands per `MUSIC-MODE-BRAND-INTEGRATION-V1-01` — that an Amazon-pattern surface (search + browse + filter + grid + reviews) is the only experience that scales the operator's "800 high-confidence configs per brand" tier (memory `project_800_high_confidence_configs`). Per-platform redirects to third-party stores cannot deliver that experience.

### 1.2 Non-Goals (V1)

The storefront V1 explicitly does **NOT**:

1. Carry **any** third-party content. Pearl Prime catalog SKUs only. No marketplace listings from outside authors. No drop-shipping.
2. Replace the brand-wizard onboarding flow. The wizard remains the way new brands enter the system (Path X 37 + music 38+). The storefront *consumes* wizard outputs.
3. Replace the brand-admin dashboard (`brand-wizard-app/public/brand_admin_v2.html`). That dashboard is an **operator** surface; the storefront is a **buyer** surface.
4. Re-architect `phoenix_recommender/` (already promoted via `ws_recommender_promotion_20260328`). The storefront *consumes* the recommender's ranked output.
5. Author new content. Books, audiobooks, manga, and music are produced upstream by `Pearl_Prime`, `Pearl_Audio`, `Pearl_Author` (Manga V2), and the music_mode pipeline. The storefront *sells* what those produce.
6. Replace **lead-magnet** freebie surfaces (free-PDF wind-down kits, free 30-sec audio samples, the `somatic_exercise_freebee_apps/` tools). Freebies still live where they live. Only **paid-book** CTAs unify here — see §14.
7. Substitute for the **Brand-Admin-V2 weekly-package writer** cron (`weekly_package_writer.yml`). That cron produces operator-facing per-platform ZIPs; the storefront produces customer-facing per-SKU pages.

### 1.3 What the storefront is, in one sentence

A Cloudflare-hosted, Amazon-pattern, Pearl-Prime-branded marketplace that sells **only** Pearl Prime catalog SKUs (book / audiobook / manga / music) across 5 locales with dark+amber Pearl Prime visual language, star-based reviews, locale auto-detect + manual switcher, brand-lane filter, search + browse, in-browser sample players + readers, and Stripe Checkout payment.

---

## §2 — In-Scope Catalog + SKU Shape

### 2.1 Brand axes (FROZEN — do NOT re-architect)

- **Manga / book / audiobook / podcast brands:** Path X **37** brands per `config/manga/canonical_brand_list.yaml` (cap `BR-CANON-02`). FROZEN. The storefront indexes these 37 across 5 locales × 4 product types.
- **Music brands:** 38+ first-class music-mode brands per `config/music/music_brand_registry.yaml` and cap `MUSIC-MODE-BRAND-INTEGRATION-V1-01`. FROZEN at archetype level; new musician onboardings extend (do not contradict) this list.

### 2.2 Locale axes

5 canonical locales per `config/localization/locale_registry.yaml`:

| Locale | Region | Script | Baseline | Phase |
|---|---|---|---|---|
| `en-US` | United States | Latin | yes (canonical reference) | Phase 1 (launch) |
| `ja-JP` | Japan | Japanese | no | Phase 2 |
| `zh-TW` | Taiwan | Traditional Chinese | no | Phase 3 |
| `zh-CN` | Mainland China | Simplified Chinese | no | Phase 3 |
| `ko-KR` | South Korea | Korean | no | Phase 4 (gated on distribution_status clearance per `docs/CJK_CATALOG_PLAN.md`) |

### 2.3 Product-type axes

Four product types per SKU:

1. **book** — text-format (EPUB primary; PDF fallback for full-PDF Phase 1 path) digital book
2. **audiobook** — M4B with chapter markers + MP3 fallback (delivery model in §12)
3. **manga** — multi-page sequential art, served as PDF (full download) + WEBTOON vertical-scroll PNG (in-browser reader) per §13
4. **music** — per-album default (Q-PRP-MUSIC-SKU-01); per-track + per-brand-subscription alternates

### 2.4 SKU model (derived from existing catalog rows)

The storefront's `sku` table joins three existing SSOTs:

- **Book SKUs:** `artifacts/catalog/pearl_prime_book_script_catalogs/<locale>_catalog.csv` — 28 columns; join key = `(locale, brand, topic, persona, teacher_id)`. Storefront stores: `sku_id`, `locale`, `brand_id`, `topic`, `persona`, `title`, `subtitle`, `teacher_id`, `product_type=book`, `output_target_path` (used to locate the EPUB), `bestseller_overlay_ref`, plus storefront-specific fields (price, currency, cover_url, status, created_at).
- **Manga SKUs:** `artifacts/catalog/manga/<locale>_manga_catalog.csv` — 23 columns; join key = `(locale, brand, series_id)`. Storefront stores: `sku_id`, `locale`, `brand_id`, `series_id`, `series_title`, `genre`, `is_tentpole`, `product_type=manga`, `chapters_per_volume`, `cadence_weeks`, `output_target_path`, plus storefront fields.
- **Music SKUs:** `config/music/music_brand_registry.yaml` `music_brands[].{brand_id, musician_handle, archetype, survey_yaml_pointer}` joined with album/track manifests under `SOURCE_OF_TRUTH/musician_banks/<musician_handle>/` (when populated by the music_mode pipeline).
- **Audiobook SKUs:** derived per book SKU when an audiobook deliverable exists at `artifacts/weekly_packages/<brand>/<week>/audible/` per `WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01` AMENDMENT-2026-05-27. Storefront stores: `sku_id_parent` (the book SKU), `product_type=audiobook`, `m4b_url`, `chapter_marker_url`, `duration_sec`, plus storefront fields.

### 2.5 SKU identity

```
sku_id = <product_type>_<locale>_<brand_id>_<inner_key>
inner_key (book)      = <topic>_<persona>_<teacher_id>
inner_key (audiobook) = same as parent book SKU's inner_key
inner_key (manga)     = <series_id>
inner_key (music)     = <album_slug> | <track_slug> | <musician_handle>_subscription
```

Example: `book_en_US_stillness_press_adhd_focus_corporate_managers_ahjan`.

### 2.6 Series bundles (Phase 3+)

A `bundle` table joins multiple `sku_id` rows into a single purchase unit (e.g., a 3-volume manga series). Bundle pricing default = flat tier per Q-PRP-SERIES-BUNDLE-01 (recommend `$9.99` for any 3-volume manga series; `$14.99` for any 6-volume).

### 2.7 What is NOT a storefront SKU

- Atom files under `atoms/` and `SOURCE_OF_TRUTH/teacher_banks/` are **content sources**, not SKUs.
- Brand-wizard YAMLs under `brand-wizard-app/brands/` are **brand identity manifests**, not SKUs.
- Weekly per-platform ZIPs under `artifacts/weekly_packages/<brand>/<week>/<platform>/` are **distribution deliverables for external platforms**, not storefront SKUs (though the storefront's audiobook/manga assets are sourced from the same upstream that builds those ZIPs).

---

## §3 — Storefront Architecture Selection

Per operator directive ("prefer easy-adapt over complex integration; if zero workable Cloudflare-compatible options surface, surface that as a STOP_REASON instead of inventing one") the architect ran a 10-search web sweep (2026-06-03) and built the comparison matrix below.

### 3.1 Candidate matrix

| Candidate | CF Pages/Workers fit | Self-host vs SaaS | Digital-only fit | Multi-locale | Star reviews | License | Integration effort | Cost |
|---|---|---|---|---|---|---|---|---|
| **Meridian (Medusa.js + Payload + Next.js on CF Workers)** [casualchic/medusa-payload-cloudflare](https://github.com/casualchic/medusa-payload-cloudflare) | **native** (the only Medusa template that runs end-to-end on CF Workers as of 2026) | self-host | recipe + plugin (no built-in digital product type) | planned v1.1+ (not present today) | not included | MIT | medium (adapt + add digital-products plugin + add reviews + add i18n + add catalog ingest) | ~$5/mo on CF |
| **Medusa.js core** [docs](https://docs.medusajs.com/resources/recipes/digital-products) | partial (CF support exists in community templates; not first-party) | self-host | recipe-driven; [srindom/medusa-downloadable-products](https://github.com/srindom/medusa-downloadable-products) plugin available | yes (regions + locales) | not built-in | MIT | high (full backend stack to provision + customize product model) | self-managed infra |
| **Saleor** [saleor.io](https://saleor.io/) | **no** (Django + Postgres; not CF-Workers-native) | self-host | yes (native digital products + downloads) | yes (GraphQL i18n) | not built-in | BSD-3 | high (Django stack does not run on CF; would need a separate VPS) | VPS hosting |
| **Vendure** [vendure.io](https://vendure.io/) | **no** (NestJS + Postgres) | self-host | yes (digital products) | yes | not built-in | **GPLv3** (changed from MIT 2024) | high (NestJS not CF-Workers-native) | VPS hosting; GPL license incompatible with potential closed extensions |
| **Snipcart** [snipcart.com/sell-digital-products](https://snipcart.com/sell-digital-products) | **native** (HTML/JS drop-in works on any static CF Pages site) | SaaS | **yes** (built-in digital download delivery, PDF/EPUB/MP3/video first-class) | yes (multi-currency + multi-language confirmed) | not built-in | SaaS (closed) | **low** (drop-in JS; catalog declared via HTML data attributes or JSON feed) | 2% + Stripe fees (or $20/mo flat under threshold) |
| **Custom CF Pages + Workers + D1 + R2 + KV + Stripe Checkout** [CF e-commerce D1 tutorial](https://developers.cloudflare.com/d1/tutorials/using-read-replication-for-e-com/) | **native** (Cloudflare's own reference architecture) | self-host | yes (we control the model end-to-end) | yes (we model from the start) | yes (we model from the start) | MIT (our code) | medium-high (~3-4 weeks Pearl_Dev + Pearl_Int) | ~$5-25/mo on CF |
| **WooCommerce** [open-source-ecommerce comparison](https://www.ecommerceceo.com/open-source-ecommerce/) | **no** (WordPress LAMP stack) | self-host | yes via extensions | yes via plugins | yes via plugins | GPLv2 | high (LAMP stack not CF-Workers; would need separate hosting) | hosting + plugin licenses |
| **BookFunnel + Stripe** [blog.bookfunnel.com](https://blog.bookfunnel.com/2026/sell-direct-with-stripe-and-automatic-bookfunnel-delivery/) | n/a (delivery layer only, not storefront) | SaaS | yes (purpose-built for ebook + audiobook delivery via Stripe Checkout) | n/a | n/a | SaaS | low (pair with whatever storefront we pick) | per-author tier |

### 3.2 Recommendation — PRIMARY

**Custom Cloudflare Pages + Workers + D1 + R2 + KV stack with Stripe Checkout** (full topology in §5).

**Rationale (operator's "easy-adapt over complex integration" lens):**

1. The "easy-adapt" path here is **not** adopting a heavy framework — it is **reading our existing YAML SSOTs directly**. Path X 37 brand list, locale registry, music brand registry, planned-volumes coverage matrix, and the two catalog CSVs (book + manga) are already canonical. Every commerce framework would force us to *re-import* them into the framework's product model and re-sync on each catalog regen. That is more integration work than building a thin storefront that *reads* the SSOTs at request time.
2. Meridian (Medusa on CF Workers) is the closest framework fit but ships without digital-products built in, without i18n, and without reviews. Those are exactly the three features the storefront is centered on (§7, §8, §11). Adapting Meridian means re-implementing those three features inside its product/order model — substantially harder than building them on a flat schema we own.
3. Snipcart is a serious fallback (§3.3) but is closed-source SaaS with no review widget, no brand-lane filter, and no path to Pearl-Prime-specific UX patterns like the somatic-exercise audiobook preview or the manga WEBTOON in-browser reader (§§12-13).
4. Cloudflare publishes a [first-party e-commerce reference architecture](https://developers.cloudflare.com/d1/tutorials/using-read-replication-for-e-com/) using D1 read replication, KV cart, R2 assets, Pages frontend, and Workers API. The storefront's stack lines up with that reference architecture verbatim.
5. The custom path is also the only one that lets §14 (CTA redirect unification) and §15 (atom rewrite) land cleanly — both require per-SKU canonical URLs we own and rewrite-time-stable, not vendor-prefixed.

**License posture:** all custom code = MIT (consistent with phoenix_omega repo). Stripe Checkout, BookFunnel, Cloudflare are SaaS dependencies, not bundled.

**Cost envelope:** ~$5/mo (CF Pages free tier + Workers Paid $5/mo + D1 first 5GB free + R2 first 10GB free + KV first 1GB free). Stripe = 2.9% + 30¢ per transaction. At MVP volume (Phase 1 en_US ebook only) we expect <$25/mo infra.

### 3.3 Recommendation — FALLBACK

**Snipcart drop-in on a custom Cloudflare Pages static site.** If Pearl_Dev's mockup workstream (`ws_pearl_prime_storefront_v1_ui_mockups_20260603`) discovers the custom payment + delivery layer takes longer than expected, swap Stripe Checkout direct integration for Snipcart's drop-in JS. We retain:

- Cloudflare Pages frontend (no change)
- D1 for our catalog SSOT + reviews (no change)
- R2 for assets (no change)
- KV for sessions (no change)
- Worker routes for catalog browse + search + review submission (no change)

We delegate to Snipcart:

- Cart UI
- Checkout
- Stripe handoff
- Digital download delivery (via [Snipcart's built-in digital products](https://snipcart.com/sell-digital-products))

This is an additive change (a Pearl_Int amendment ws) — not a rebuild — so it's a safe fallback. Cost rises to ~2% + Stripe fees.

### 3.4 Rejected paths

- **Saleor / Vendure / WooCommerce / CS-Cart / Bagisto / Magento:** all require non-Cloudflare hosting. Operator constraint = "hosted on Cloudflare" — these violate it.
- **Shopify, BigCommerce, Squarespace:** off-the-shelf SaaS storefronts; brand-skinning is shallow and per-SKU custom routing (atoms → storefront URLs in §15) is not feasible.
- **LemonSqueezy / Paddle / Gumroad as primary storefront:** these are **merchant-of-record payment processors with thin checkout UIs**, not catalog/browse storefronts. Suitable as payment processors (see §10) but cannot serve as the storefront itself.

### 3.5 STOP_REASON check

The architect did not invoke STOP_REASON. The custom path is a real, validated, Cloudflare-native option; it has a viable Snipcart fallback; and one workable framework alternative (Meridian) exists at proportionate adaptation cost. Per operator constraint ("if zero workable Cloudflare-compatible options surface, surface that as a STOP_REASON instead of inventing one") — multiple workable options surfaced.

---

## §4 — URL + Domain Strategy

Per operator instruction ("we prefer 'Pearl Prime' in the name"), three candidate primary domains, priority-ordered:

1. **`pearlprime.shop`** (RECOMMENDED) — clearest commerce signal; `.shop` TLD reads as marketplace to global audiences; short.
2. **`books.pearlprime.com`** — subdomain on existing `pearlprime.com` apex. Only viable if `pearlprime.com` is already operator-owned; otherwise requires apex acquisition. Subordinates the music + manga product types implicitly.
3. **`store.pearlprime.com`** — same caveat as #2; reads cleaner than `books.` for non-book SKUs.

**Operator action required:** DNS availability for `pearlprime.shop`, ownership/acquisition status for `pearlprime.com`. The architect cannot validate WHOIS from this session. Logged as **Q-PRP-DOMAIN-01** in §17.

**Naming anti-drift:** the storefront is NOT named "Phoenix Store", "Phoenix Prime Books", "Pearl Books", or "Phoenix Marketplace". The brand on the storefront UI is **Pearl Prime** verbatim, matching the brand-wizard's "Pearl Prime — Get Started" preamble (`brand-wizard-app/dist/onboarding.html` title tag).

**Locale paths:** `pearlprime.shop/{locale}/...` (e.g., `pearlprime.shop/en-US/`, `pearlprime.shop/ja-JP/`). The bare `pearlprime.shop/` URL resolves via locale auto-detect (§8) to the appropriate locale subpath.

**Per-SKU canonical URL shape:**

```
pearlprime.shop/{locale}/{product_type}/{brand_id}/{inner_key}
```

Examples:

```
pearlprime.shop/en-US/book/stillness_press/adhd_focus_corporate_managers_ahjan
pearlprime.shop/ja-JP/manga/stillness_press/stillness_press_healing_01
pearlprime.shop/en-US/audiobook/stillness_press/anxiety_gen_z_professionals_priya
pearlprime.shop/en-US/music/ahjansam_music/album_quiet_hour
```

These URLs are stable across the catalog regen process — `sku_id` is content-deterministic, not auto-incrementing — which is what makes §14 (external CTA replacement) and §15 (atom rewrite) safe.

---

## §5 — Hosting Topology (Cloudflare)

```
┌──────────────────────────────────────────────────────────────────────┐
│  CLOUDFLARE                                                           │
│                                                                       │
│   ┌─────────────────┐    ┌────────────────────┐    ┌──────────────┐ │
│   │  Pages          │    │  Workers           │    │  D1          │ │
│   │  (frontend)     ├───▶│  (API + edge)      ├───▶│  (orders +   │ │
│   │                 │    │                    │    │   reviews +  │ │
│   │  HTML+CSS+JS    │    │  - /catalog        │    │   accounts + │ │
│   │  Pearl Prime    │    │  - /search         │    │   sku index) │ │
│   │  dark+amber     │    │  - /sku/:id        │    │              │ │
│   │  per §6         │    │  - /review (POST)  │    │  read-replicas │
│   └────────┬────────┘    │  - /cart           │    │  per region  │ │
│            │             │  - /checkout       │    │  per CF e-com│ │
│            │             │  - /webhook/stripe │    │  ref-arch    │ │
│            │             └────────┬───────────┘    └──────────────┘ │
│            │                      │                                   │
│            │                      ├──▶ KV (cart/session, 60min TTL)  │
│            │                      │                                   │
│            │                      └──▶ R2 (m4b, mp3, pdf, png, jpg)  │
│            │                                                          │
│            └────────────────────────────────────────────────────────  │
│                                                                       │
│   ┌──────────────────┐    ┌──────────────────┐                       │
│   │ Cloudflare       │    │ Turnstile        │                       │
│   │ Access (optional │    │ (review-spam     │                       │
│   │ admin / auth)    │    │  prevention)     │                       │
│   └──────────────────┘    └──────────────────┘                       │
└──────────────────────────────────────────────────────────────────────┘
       │
       └──▶ Stripe Checkout (hosted) ──▶ webhook ──▶ /webhook/stripe Worker
```

### 5.1 Component responsibilities

- **Cloudflare Pages** — static frontend bundle: HTML + Pearl Prime CSS + small JS for search/filter/cart-add interactions. Built from `storefront/frontend/` (new dir; not yet created — Pearl_Dev mockups ws scaffolds it).
- **Cloudflare Workers** — Pages Functions (routes co-located with the Pages project; Cloudflare compiles them into Workers automatically per the [Pages-Workers integration model](https://developers.cloudflare.com/pages/)). Endpoints: `/api/catalog`, `/api/search`, `/api/sku/:id`, `/api/review` (POST + GET), `/api/cart/*`, `/api/checkout`, `/api/webhook/stripe`, `/api/account/*`.
- **Cloudflare D1** — SQLite-semantics serverless DB. Tables (sketches in §11 + §10 + §7). Read-replicated regionally per the [D1 e-commerce reference architecture](https://developers.cloudflare.com/d1/tutorials/using-read-replication-for-e-com/).
- **Cloudflare R2** — blob storage for: audiobook M4B + MP3, manga WEBTOON PNG + PDF, book EPUB, cover JPG/PNG. Signed URLs for paid-customer downloads (15-minute TTL; regenerated on demand from `/api/account/library`).
- **Cloudflare KV** — cart + session state with 60-minute TTL. Anonymous browsing carts auto-expire; signed-in carts persist to D1.
- **Cloudflare Turnstile** — bot/spam filter on review submissions and on account creation (when accounts are enabled — Q-PRP-AUTH-01).
- **Cloudflare Access** (optional) — gate the `/admin` surfaces; non-customer-facing.

### 5.2 Tier 2 (paid) limits at MVP scale

CF Workers Paid plan ($5/mo): 10M requests + 30 GB-sec CPU. At MVP scale (Phase 1 en_US ebook only, low single-digit-thousand DAU), this is comfortable.

D1 Paid: first 5 GB included; reads up to 25B/mo, writes up to 50M/mo. Our catalog at full scope (37 brands × 5 locales × 4 product types × ~800 configs per brand ≈ 600k SKU rows) plus reviews fits easily.

R2: first 10 GB + 1M Class-A ops/mo free; $0.015/GB beyond. Audiobook + manga ZIPs could push past 10 GB by Phase 2 — recommended to monitor at Phase 2 launch.

KV: first 1 GB + 100k reads/day free. Cart/session fits.

### 5.3 Account split awareness

Per `skills/pearl-int/references/cloudflare_pages_deploy.md` (Traps 1-4 from 2026-06-03), Phoenix Omega's Cloudflare projects live under **account `b80152c319f941e6e92f928e2617a3d5`**, not the operator's primary `ahjansamvara@gmail.com` account (`626d6eb8162a8121f74e59235d82a4f5`). The storefront's Pages project + Workers + D1 + R2 + KV resources must be provisioned under `b80152c3...` so that the existing GitHub-Actions deploy pattern (`CLOUDFLARE_API_TOKEN` repo secret) continues to work. **Operator action required:** confirm provisioning location. Logged as part of `ws_pearl_prime_storefront_v1_cloudflare_wiring_20260603`.

### 5.4 Deploy pattern

Identical to brand-wizard's pattern (per same reference doc): merge to `main` → `.github/workflows/pearl-prime-storefront-deploy.yml` (new file under the Pearl_Int ws) auto-fires → `wrangler-action@v3` deploys Pages + Workers + D1 migrations + KV/R2 bindings. **Do not** run `wrangler` from a laptop — same Trap 1-4 contraindications apply.

---

## §6 — UI Design Contract

### 6.1 Visual language

Inherits the Pearl Prime brand-wizard design tokens verbatim per `brand-wizard-app/src/BrandWizard.jsx` lines 1-100 + `brand-wizard-app/dist/onboarding.html` + `MUSIC-MODE-BRAND-INTEGRATION-V1-01` + recent PR #1430 (`musician_reflections_survey`):

| Token | Value | Use |
|---|---|---|
| `--pp-bg` | `#0e0a06` | Page background (deep almost-black warm-tinted) |
| `--pp-text` | `#faf6f0` | Primary text (off-white cream) |
| `--pp-accent` | `#d97706` | Amber-600 — CTAs, links, ratings, focus rings, brand-lane chips |
| `--pp-accent-soft` | `#92400e` | Amber-800 — hover states |
| `--pp-muted` | `#a8a29e` | Secondary text, metadata |
| `--pp-border` | `#3f3530` | Card borders, dividers |
| Body font | DM Sans (300/400/500) | UI text, body copy |
| Display font | Cormorant Garamond (300/400 + italic) | Headlines, titles, hero copy |
| Mono font | DM Mono (300/400) | SKU IDs, prices in spec sheets, code-like data |
| Font preamble | `<link rel="preload" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300;1,400&family=DM+Mono:wght@300;400&family=DM+Sans:wght@300;400;500&display=swap" as="style" onload="this.onload=null;this.rel='stylesheet'">` | copy verbatim from `brand-wizard-app/dist/onboarding.html` |

The storefront is **not** a "light theme" surface and **not** a brand-customizable per-brand surface. The Pearl Prime visual identity is consistent across all brand-lane pages — only the brand-lane chip + hero phrasing change.

### 6.2 Component inventory (Pearl_Dev mockup ws scope)

1. **Header** (`<storefront-header>`)
   - Pearl Prime wordmark (Cormorant Garamond, amber)
   - Search bar (DM Sans, expandable)
   - Locale switcher (5 locales; current locale highlighted)
   - Brand-lane chip rail (collapses to dropdown on narrow viewports)
   - Cart icon (amber dot when non-empty)
   - Account icon (initials or generic person glyph when signed in; "Sign in" link otherwise — auth model per Q-PRP-AUTH-01)

2. **Search results grid** (`<sku-grid>`)
   - 4-up at desktop, 2-up at tablet, 1-up at mobile
   - Each card: cover (1:1.5 ratio book / 1:1.4 manga / 1:1 music), title (Cormorant 1.25rem), subtitle (DM Sans 0.875rem muted), brand chip, star rating + count, price (DM Mono)
   - Hover lift + amber border glow

3. **Product detail page** (`<sku-detail>`)
   - Left column (40% desktop): large cover + brand chip + title + subtitle + price + Buy-Now button
   - Right column (60% desktop): description (from `bestseller_overlay_ref` or manga `genre/visual_grammar`), sample player (§12) or preview reader (§13), star summary, review list, "Customers also bought" rail (from `phoenix_recommender`)

4. **Audiobook sample player** (`<audiobook-sample>`)
   - 30-second preview clip (Q-PRP-SAMPLE-01); waveform; play/pause; chapter list teaser; full duration

5. **Manga preview reader** (`<manga-preview>`)
   - WEBTOON vertical-scroll, first N pages free (Q-PRP-SAMPLE-01 default = first chapter)
   - Touch + mousewheel scroll
   - "Buy to unlock full series" CTA at scroll-end

6. **Cart** (`<cart-page>`)
   - Multi-item list with per-row remove
   - Phase 1 default = single-item Buy-Now Stripe Checkout per Q-PRP-CART-01 (cart UI hidden Phase 1; visible Phase 2+)

7. **Stripe Checkout handoff** — server-side `/api/checkout` constructs a Stripe Checkout Session and 302's to the hosted Checkout URL. Customer returns to `/account/library?session=...` on success.

8. **My Library** (`<account-library>`)
   - Grid of owned SKUs with re-download buttons (R2 signed URLs)
   - Audiobook entries open the in-browser player; manga entries open the WEBTOON reader; book entries surface EPUB + (optional) PDF download
   - Music entries (Phase 3) surface tracks + streaming player

9. **Account page** (`<account-page>`)
   - Email, magic-link login (Q-PRP-AUTH-01 default)
   - Purchase history
   - Locale preference
   - Communication opt-ins (separate from freebie email lists — those live in the funnel)

10. **Review form** (`<review-form>`)
    - 5-star widget (amber filled stars on `#0e0a06`)
    - Free-text body (DM Sans; 250-char minimum, 4000-char maximum)
    - Verified-purchase badge auto-applied if `(sku_id, account_id)` matches a completed order
    - Cloudflare Turnstile widget (invisible challenge)

11. **Brand-lane page** (`<brand-page>`)
    - Hero with brand tagline (`config/manga/canonical_brand_list.yaml` `notes` field for Path X 37; `archetype` + `notes` for music 38+)
    - Filtered SKU grid (all product types for that brand)
    - "Start the series" / "Featured" rail per brand

12. **Locale landing** (`<locale-home>`)
    - Bestsellers in this locale (deterministic ranking — not personalized in Phase 1)
    - "Featured brands" rail (locale-appropriate subset of 37 + active music 38+)
    - "New this week" rail (sorted by `created_at` descending)

### 6.3 Accessibility

- WCAG 2.1 AA contrast minimums met by the `#0e0a06 / #faf6f0` pairing (contrast ratio ≈ 15.7:1).
- Amber `#d97706` on dark background contrast ratio ≈ 4.9:1 (passes large-text AA, large-icon AA).
- All interactive elements keyboard-reachable with visible focus ring (`outline: 2px solid var(--pp-accent)`).
- ARIA labels on cart, account, locale switcher, star ratings.

---

## §7 — Catalog Wiring

### 7.1 Ingest model

The storefront's `sku` table is built by a **read-only catalog projector** Worker (`scripts/storefront/project_skus.py` — not authored this session; Pearl_Dev ws scope) that:

1. Reads `artifacts/catalog/pearl_prime_book_script_catalogs/<locale>_catalog.csv` (per locale)
2. Reads `artifacts/catalog/manga/<locale>_manga_catalog.csv` (per locale)
3. Reads `config/music/music_brand_registry.yaml` joined with `SOURCE_OF_TRUTH/musician_banks/<musician_handle>/<album>/manifest.yaml` (when populated)
4. Reads `artifacts/weekly_packages/<brand>/<week>/<platform>/manifest.json` to detect audiobook deliverables
5. Projects to flat `sku` rows in D1

Projection cadence: **on every catalog regen merge to main** (CI workflow trigger), plus a weekly cron sweep (Sunday 22:00 UTC) to catch upstream content that landed without a catalog re-project (defensive).

### 7.2 D1 `sku` table schema (Phase 1 sketch)

```sql
CREATE TABLE sku (
  sku_id         TEXT PRIMARY KEY,    -- per §2.5
  locale         TEXT NOT NULL,        -- 'en-US' | 'ja-JP' | 'zh-TW' | 'zh-CN' | 'ko-KR'
  brand_id       TEXT NOT NULL,        -- 'stillness_press' | '<musician_handle>_music' | ...
  product_type   TEXT NOT NULL,        -- 'book' | 'audiobook' | 'manga' | 'music'
  topic          TEXT,                 -- book only
  persona        TEXT,                 -- book + audiobook only
  series_id      TEXT,                 -- manga only
  title          TEXT NOT NULL,
  subtitle       TEXT,
  description    TEXT,                 -- pulled from upstream metadata; may be NULL Phase 1
  cover_url      TEXT,                 -- R2 key
  preview_url    TEXT,                 -- R2 key for 30-sec audio / first-N-page manga / sample EPUB chapter
  asset_url      TEXT,                 -- R2 key for full paid asset (signed at download time)
  price_cents    INTEGER NOT NULL,     -- in locale currency's smallest unit
  currency       TEXT NOT NULL,        -- 'USD' | 'JPY' | 'TWD' | 'CNY' | 'KRW'
  status         TEXT NOT NULL,        -- 'active' | 'draft' | 'archived'
  bundle_id      TEXT,                 -- nullable; for series bundles (Phase 3)
  upstream_path  TEXT,                 -- the `output_target_path` from the source catalog row
  created_at     INTEGER NOT NULL,
  updated_at     INTEGER NOT NULL
);
CREATE INDEX idx_sku_locale_brand_type ON sku(locale, brand_id, product_type);
CREATE INDEX idx_sku_locale_status ON sku(locale, status);
CREATE INDEX idx_sku_brand_status ON sku(brand_id, status);
```

### 7.3 Brand-lane filter contract

The header's brand-lane chip rail renders the brands eligible for the current locale:

- `en-US`: all 37 Path X manga-canon brands + all active music 38+ brands
- `ja-JP`: subset per `docs/CJK_CATALOG_PLAN.md` (Japan-licensed brands only)
- `zh-TW`, `zh-CN`: subsets per CJK plan
- `ko-KR`: gated on `distribution_status` clearance (Phase 4)

The chip rail is **not** a hard filter — clicking "Stillness Press" routes to `/{locale}/brand/stillness_press`. A user can deep-link to a brand-lane page even if the brand isn't currently surfaced as a chip (e.g., a manga brand on `en-US` with no en-US-licensed series yet shows a "Coming soon" state instead of 404).

### 7.4 Locale routing matrix

| User locale | URL behavior |
|---|---|
| `en-US` | Default; bare `pearlprime.shop/` redirects here if no cookie + no Accept-Language match. |
| `ja-JP` | Auto-redirected from `pearlprime.shop/` if CF-IPCountry=JP **or** Accept-Language matches `ja*`. |
| `zh-TW` | Auto-redirected if CF-IPCountry=TW. |
| `zh-CN` | Auto-redirected if CF-IPCountry=CN. |
| `ko-KR` | Auto-redirected if CF-IPCountry=KR (Phase 4+). |

Persistent cookie `pp_locale` overrides auto-detect for 365 days. Manual locale switcher in header writes that cookie.

### 7.5 Anti-drift invariants for catalog wiring

1. **Do NOT** mutate `config/manga/canonical_brand_list.yaml`, `config/music/music_brand_registry.yaml`, or the locale registry from the storefront. Read-only.
2. **Do NOT** create a parallel SKU SSOT. The D1 `sku` table is a **projection cache**, not a source of truth. Catalog regen overwrites it.
3. **Do NOT** silently filter brands. If a brand is in the canonical lists but has zero active SKUs in a locale, render a "Coming soon" surface — do not 404 or hide.

---

## §8 — Locale Auto-Detection + Manual Switcher

### 8.1 Detection chain (request-time)

```
1. cookie pp_locale exists, value in {en-US, ja-JP, zh-TW, zh-CN, ko-KR}? → use it.
2. CF-IPCountry header matches a locale's region? → use that locale, set cookie.
3. Accept-Language header prefix matches a locale? → use that locale, set cookie.
4. Default → en-US, set cookie.
```

Detection runs in the Worker for `/` and untagged paths. Locale-tagged paths (`/{locale}/...`) are honored as-is and the cookie is updated to match if it differs (treat the URL as the user's explicit choice).

### 8.2 Manual switcher

Always-visible in the header. Five buttons (or a dropdown on narrow viewports), current locale highlighted. Clicking writes the cookie and reloads to the equivalent path in the new locale, falling back to that locale's home if the path doesn't exist there.

### 8.3 Currency follows locale (not separately switchable Phase 1)

- `en-US` → USD
- `ja-JP` → JPY (zero-decimal — Stripe needs `amount` in whole yen)
- `zh-TW` → TWD
- `zh-CN` → CNY (subject to Q-PRP-PAY-01 — Stripe coverage of CNY)
- `ko-KR` → KRW (zero-decimal)

User-selectable currency is a Phase 3+ consideration if travelers in a different locale want to pay in their home currency. Not in scope V1.

---

## §9 — Search + Browse UX (Amazon Pattern)

### 9.1 Top search bar

Always present in header. Searches across `(title, subtitle, brand_id, topic, persona, series_title, archetype, description)` in the current locale. Returns SKU grid.

Implementation: D1 full-text-search (FTS5) on the `sku_search` virtual table. SQL:

```sql
CREATE VIRTUAL TABLE sku_search USING fts5(
  sku_id UNINDEXED,
  title, subtitle, brand_id, topic, persona, series_title, archetype, description,
  content='sku', content_rowid='rowid'
);
```

### 9.2 Left-rail filters

- **Brand** — multi-select chip list (locale-appropriate subset)
- **Topic** — multi-select (book + audiobook only)
- **Genre** — multi-select (manga only)
- **Format** — checkboxes: book / audiobook / manga / music
- **Price range** — slider
- **Star rating** — 4+, 3+, 2+, 1+
- **Tentpole** — manga only (boolean from catalog `is_tentpole`)

### 9.3 Sort options

- Relevance (default for search; falls back to bestsellers for browse)
- Newest (`created_at` DESC)
- Best-selling (joins `order_item` aggregation, computed nightly into a materialized `sku_sales_rank` table)
- Price low → high
- Price high → low
- Star rating high → low

### 9.4 Infinite-scroll grid

24 SKUs per page; intersection observer triggers next page fetch. Skeleton-loading placeholders during load. Pagination via `?cursor=<last_sku_id>` query param.

### 9.5 "Customers also bought" rail

On every product detail page. Source = `phoenix_recommender/` output (already promoted per `ws_recommender_promotion_20260328`). The recommender writes `artifacts/recommendations/ranked.json` per SKU; storefront reads top-5 per current SKU. **Not personalized in Phase 1** — Q-PRP-RECO-01 defaults to "reuse phoenix_recommender as-is" through Phase 2; personalization is Phase 3+.

### 9.6 "Best in this brand" rail

On brand-lane pages and SKU detail pages. Top-5 SKUs by `sku_sales_rank` within the same `brand_id`.

### 9.7 Anti-drift invariants

- Search is **catalog-local**. We do NOT proxy to Amazon, Google, or any external search.
- Sort = "Best-selling" is computed from **storefront** order data, not external bestseller charts.
- No paid promotion / sponsored listings in V1.

---

## §10 — Payment Processing

### 10.1 Default = Stripe Checkout (Q-PRP-PAY-01 recommended default)

**Why Stripe:**

- 2.9% + 30¢ per transaction (cheaper than LemonSqueezy/Paddle 5% + 50¢ at our expected scale, per [comparison sources](https://designrevision.com/blog/stripe-vs-lemonsqueezy))
- All 5 locale currencies supported (USD, JPY, TWD, CNY, KRW — confirmed per [Stripe currencies docs](https://docs.stripe.com/currencies); CNY support has restrictions worth verifying for Q-PRP-PAY-01)
- Stripe Checkout = hosted payment page; PCI scope minimized (we never see card data); mobile-optimized; multi-currency built-in
- Webhook-driven order confirmation (we receive `checkout.session.completed` and write to D1 `order` table)
- Operator is the merchant; sales tax is operator-handled at filing time (Stripe Tax is an add-on we can enable later)

### 10.2 Alternates surfaced for Q-PRP-PAY-01

| Processor | Pro | Con | When to prefer |
|---|---|---|---|
| **LemonSqueezy** | Merchant of Record; global tax compliance handled | 5% + 50¢; less control over checkout UI | If operator wants zero tax-filing overhead and is comfortable with the 2% MoR premium |
| **Paddle** | Merchant of Record; enterprise tax coverage; B2B-friendly | 5% + 50¢; more enterprise-skewed onboarding | If volume passes ~$100k MRR and tax footprint expands |
| **BookFunnel + Stripe** | Purpose-built ebook/audiobook fulfillment via Stripe Checkout | Adds a per-author tier subscription | If we want delivery-side reliability + we keep Stripe pricing |
| **Apple Pay / Google Pay via Stripe Checkout** | Already included; one-tap on mobile | n/a — additive | Always enable; no extra integration cost |

### 10.3 D1 `order` and `order_item` table sketch

```sql
CREATE TABLE order_table (
  order_id          TEXT PRIMARY KEY,
  account_id        TEXT,                 -- nullable for guest checkout
  email             TEXT NOT NULL,
  locale            TEXT NOT NULL,
  currency          TEXT NOT NULL,
  total_cents       INTEGER NOT NULL,
  stripe_session_id TEXT UNIQUE,
  stripe_payment_intent_id TEXT,
  status            TEXT NOT NULL,        -- 'pending' | 'paid' | 'refunded' | 'failed'
  created_at        INTEGER NOT NULL,
  paid_at           INTEGER
);
CREATE TABLE order_item (
  order_item_id     TEXT PRIMARY KEY,
  order_id          TEXT NOT NULL REFERENCES order_table(order_id),
  sku_id            TEXT NOT NULL REFERENCES sku(sku_id),
  qty               INTEGER NOT NULL DEFAULT 1,
  unit_price_cents  INTEGER NOT NULL,
  currency          TEXT NOT NULL
);
CREATE INDEX idx_order_account ON order_table(account_id, paid_at DESC);
CREATE INDEX idx_order_item_sku ON order_item(sku_id);
```

### 10.4 Webhook flow

```
Customer click Buy Now
  → /api/checkout (Worker)
  → creates Stripe Checkout Session (line_items from cart in KV)
  → 302 to session.url
Customer completes Stripe-hosted checkout
  → Stripe POST → /api/webhook/stripe (Worker)
  → verify signature against STRIPE_WEBHOOK_SECRET
  → insert into order_table + order_item
  → mark sku as "owned" for the account (or store email+order_id for guest)
  → trigger entitlement email (Cloudflare Email Workers or third-party — Q-PRP-EMAIL deferred)
Customer redirected to /account/library?session=<id>
```

### 10.5 Per-locale currency routing

Stripe Checkout Sessions are constructed with `currency` derived from `pp_locale` cookie. Price catalog stores `price_cents` per locale; conversion is NOT live-FX — operator sets per-locale prices in a price book (Q-PRP-PRICE-01).

### 10.6 Refunds + chargebacks

V1 = manual via Stripe dashboard. Auto-revoke of digital entitlement on full refund: webhook `charge.refunded` flips `order.status='refunded'` and the library page hides the SKU. Hard cutoff: 24 hours post-refund, R2 signed URLs invalidate.

---

## §11 — Star Review System

### 11.1 Mechanics

- **5-star** scale, integer 1-5, no half-stars in V1.
- **Free-text body** required (250-char min, 4000-char max).
- **Verified-purchase badge** auto-applied if `(sku_id, account_id)` matches a paid order in `order_item`. Reviews from non-purchasers are allowed by default (Q-PRP-REVIEW-01) but display without the badge.
- **Spam prevention:** Cloudflare Turnstile invisible challenge on submission; D1 `review_rate_limit` tracks per-account submission rate (max 10/day).
- **Moderation:** post-publish default (Q-PRP-REVIEW-01). Pearl_PM or designated moderator can flip `status='hidden'` via admin route. Operator approval required to permanently delete.

### 11.2 D1 `review` table

```sql
CREATE TABLE review (
  review_id          TEXT PRIMARY KEY,
  sku_id             TEXT NOT NULL REFERENCES sku(sku_id),
  account_id         TEXT,                -- nullable if guest review enabled per Q-PRP-REVIEW-01
  reviewer_name      TEXT NOT NULL,       -- display name; defaults to "Reader"
  email_hash         TEXT,                -- SHA-256 of email; supports "you already reviewed this" check
  stars              INTEGER NOT NULL CHECK (stars BETWEEN 1 AND 5),
  body               TEXT NOT NULL,
  verified_purchase  INTEGER NOT NULL DEFAULT 0,    -- 0/1 boolean
  status             TEXT NOT NULL DEFAULT 'visible', -- 'visible' | 'hidden' | 'spam'
  helpful_count      INTEGER NOT NULL DEFAULT 0,
  reported_count     INTEGER NOT NULL DEFAULT 0,
  locale             TEXT NOT NULL,        -- review's own locale (review-in-Japanese surfaces on ja-JP SKU)
  created_at         INTEGER NOT NULL,
  updated_at         INTEGER NOT NULL
);
CREATE INDEX idx_review_sku_status ON review(sku_id, status, created_at DESC);
CREATE INDEX idx_review_account ON review(account_id, created_at DESC);
```

### 11.3 Aggregate caching

`sku_review_summary` materialized view (recomputed via Worker scheduled task every 15 min, or on review insert via `AFTER INSERT` trigger):

```sql
CREATE TABLE sku_review_summary (
  sku_id     TEXT PRIMARY KEY REFERENCES sku(sku_id),
  avg_stars  REAL NOT NULL,
  count      INTEGER NOT NULL,
  star_1     INTEGER NOT NULL,
  star_2     INTEGER NOT NULL,
  star_3     INTEGER NOT NULL,
  star_4     INTEGER NOT NULL,
  star_5     INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);
```

Surface: SKU card shows `avg_stars` + `count`; SKU detail page shows distribution + recent reviews + "Most helpful" sort.

### 11.4 Anti-drift invariants

- Reviews are NOT auto-imported from external platforms (Amazon, Goodreads, Audible). Each storefront review is native, with consent.
- Verified-purchase badge cannot be self-applied. Auto only.
- Reviewer display names are user-controlled but cannot impersonate "Pearl Prime", "Phoenix", or any teacher_id slug — enforced via a moderation-deny-list in the validator.

---

## §12 — Audiobook Sample + Full Delivery (Q-PRP-AUDIOBOOK-DELIVERY-01)

### 12.1 Sample (free)

- 30-second preview clip per Q-PRP-SAMPLE-01 default (operator may opt for "first chapter" instead).
- Source: trimmed from the M4B at projection time; stored as `preview_url` in R2 (public-read).
- Player: HTML `<audio controls>` with custom Pearl Prime styling + waveform via wavesurfer.js (free MIT lib).

### 12.2 Full delivery (paid)

Per Q-PRP-AUDIOBOOK-DELIVERY-01 default = **both**:

- **In-browser streaming player** — `<audio>` element seeded with a 60-minute signed R2 URL; player includes chapter scrubber (chapter markers loaded from a sidecar JSON).
- **MP3 download** — separate "Download MP3" button → fresh signed URL → browser direct download. Filename: `<title>_<locale>.mp3`.

### 12.3 R2 layout

```
r2://pearl-prime-storefront-assets/audiobook/<locale>/<brand_id>/<inner_key>/
  ├── full.m4b
  ├── full.mp3
  ├── preview.mp3
  ├── cover.jpg
  └── chapters.json
```

### 12.4 Signed URL parameters

- Preview = public-read (any browser can stream)
- Full = signed URL, 60-minute TTL, refreshed on demand from `/api/account/library/sku/:id/url`
- Re-download is unlimited for paid customers
- Refunded purchasers lose signed-URL refresh within 24 hours of refund (§10.6)

---

## §13 — Manga Preview + Full Delivery (Q-PRP-MANGA-DELIVERY-01)

### 13.1 Preview (free)

- First N pages free per Q-PRP-SAMPLE-01 (default = first chapter — typically 10 pages per `manga_catalog.csv` `chapters_per_volume`)
- Preview pages = PNG tiles stored as `preview_pages/p001.png` ... `preview_pages/pNNN.png`

### 13.2 Full delivery (paid)

Per Q-PRP-MANGA-DELIVERY-01 default = **both**:

- **In-browser WEBTOON vertical-scroll reader** — pages streamed lazily; intersection observer fetches next page when prior is 80% scrolled
- **Full PDF download** — single PDF compiled from all chapter PNGs + bookmarks per chapter; filename: `<series_id>_vol<N>_<locale>.pdf`

### 13.3 R2 layout

```
r2://pearl-prime-storefront-assets/manga/<locale>/<brand_id>/<series_id>/<volume_N>/
  ├── pages/
  │   ├── p001.png   (WEBTOON 1080-wide vertical-scroll tile)
  │   ├── p002.png
  │   └── ...
  ├── preview_pages/
  │   ├── p001.png   (subset of pages/, first-chapter only by default)
  │   └── ...
  ├── full.pdf        (compiled for download)
  ├── cover.jpg
  └── manifest.json   (page count, chapter breakpoints)
```

### 13.4 Reader UX

- Vertical scroll (mouse wheel + touch)
- "Jump to chapter" dropdown anchored to header during reading
- Reading-progress persisted to D1 `reader_progress` table (account-scoped; surfaces as "Continue reading" on Account home)
- Right-click protection NOT applied in V1 (PNG tiles are screenshot-able by definition; signed URLs deter bulk scrape)

---

## §14 — CTA Redirect Unification (HARD REQUIREMENT)

### 14.1 Operator directive (verbatim)

> "We won't direct them to Amazon or Google Play or any other platforms for any of our book content: eBooks, audiobooks, and manga."

This is **not optional** and **not deferred**. Phase 1 launch ships with the CTA unification in place — for **paid** CTAs.

### 14.2 What gets rewritten

Every **paid-book / paid-audiobook / paid-manga / paid-music** CTA across the following surfaces resolves to a `pearlprime.shop/{locale}/{product_type}/{brand_id}/{inner_key}` URL:

1. **`funnel/`** — Flask proof-loop hub + per-topic pages. Today: ad-hoc external links per `config/funnel/store_url_tracker.yaml`. Phase 1: every "BUY NOW" / "Get the book" / "Buy on Amazon" / "Listen on Audible" CTA points to the storefront SKU.
2. **`platform_marketing/`** — if present (see anti-drift note below). Same rewrite.
3. **`somatic_exercise_freebee_apps/`** — current freebie HTML tools. Their **freebie download** CTAs remain pointed at lead-magnet pages; their **"And the full book is here"** CTAs route to the storefront.
4. **`brand-wizard-app/public/free/`** — current freebie landing pages (15 in `anxiety-nervous-system-reset/`, etc.). Same as #3.
5. **Email sequences** — every "Buy the book" CTA in lead-nurture, post-purchase, win-back, etc.
6. **Social CTAs** (link-in-bio, Twitter/X, Instagram, TikTok descriptions) — managed by Pearl_Marketing; same rewrite contract.

### 14.3 What is hard-deprecated

`config/funnel/store_url_tracker.yaml` is **hard-deprecated** on Phase 1 launch. The file's per-topic `kdp / google_play / apple_books / kobo` columns become stale by definition. A successor file (`config/storefront/sku_url_map.yaml`, generated automatically by the catalog projector) keys `(topic, persona, locale)` → canonical storefront URL.

The legacy file is retained read-only for archaeology — but no code reads from it post-cutover.

### 14.4 What is NOT rewritten

- **Freebie CTAs** ("Download the free PDF", "Get the 5-minute wind-down audio") continue to flow through existing lead-magnet pages. Freebies remain a **lead-acquisition** surface, not a monetization surface.
- **External-platform discovery links** (e.g., "Find us on Spotify Podcasts") on brand bio pages — these are content-marketing surfaces, not buy-now CTAs, and remain.
- **Brand-admin internal links** (operator dashboard, weekly-work view) — not buyer-facing.

### 14.5 Cutover model (Q-PRP-CTA-UNIFY-01 default)

**Soft-deprecate-then-redirect-then-replace** (default):

1. **Phase 1 launch:** new storefront SKU URLs become the canonical destination. CTAs across `funnel/` and elsewhere updated.
2. **Phase 1 + 30 days:** any remaining external-platform CTAs in static content updated via Pearl_Marketing sweep ws.
3. **Phase 1 + 90 days:** `store_url_tracker.yaml` archived; `config/storefront/sku_url_map.yaml` becomes the sole truth.
4. **CI guard:** new `scripts/ci/check_external_buy_links.py` (Pearl_Marketing ws scope) scans `funnel/`, `platform_marketing/`, `brand-wizard-app/public/free/`, `somatic_exercise_freebee_apps/`, email YAMLs, and social CTA registries for the patterns `amazon.com/dp`, `play.google.com/store/books`, `audible.com/pd`, `books.apple.com`, `kobo.com/ebook`, `webtoons.com`, etc.; fails CI if a paid-book CTA matches outside an allow-list.

Hard-cutover (alternative) would orphan in-flight email sequences and ad campaigns that already point at external stores. The soft cutover is recommended.

### 14.6 Anti-drift invariants

- The storefront URL is **the** paid-content destination on Phase 1 launch day. Any new freebie / funnel / email content authored after Phase 1 must use storefront URLs for paid CTAs (CI guard enforces).
- Pearl_PM owns escalation if a downstream ws drifts.
- "Find on Amazon" affiliate links are **not** an exception. Per operator directive — none.

### 14.7 Anti-drift note on `platform_marketing/`

Per `MUSIC-MODE-FREEBIE-FUNNEL-V1-02` §2 discovery: `platform_marketing/` is **not present** at repo root; the marketing-adjacent surfaces are `config/marketing/`, `docs/marketing/`, `scripts/marketing/`, `marketing_deep_research/`. The §14.2 #2 entry is included for forward-compatibility in case the directory is created; the CI guard scans the actual present directories.

---

## §15 — Pearl_Writer "What to do next" Atom Audit & Rewrite

### 15.1 Problem

Every Pearl Prime 15-minute book ships with **"what to do next"** atoms across the COMPRESSION / REFLECTION / INTEGRATION / chapter-closer slots. A non-trivial subset of those atoms today references **off-catalog books, authors, classes, and organizations** — e.g., "go read Bessel van der Kolk's *The Body Keeps the Score*", "check out a Tara Brach RAIN workshop", "subscribe to the Insight Timer app". These work against §14's mandate: a reader who finishes one of our books and is told to read someone else's book is being routed out of Pearl Prime's ecosystem.

### 15.2 Scope

Every atom in:

- `atoms/<persona>/<topic>/COMPRESSION/CANONICAL.txt`
- `atoms/<persona>/<topic>/REFLECTION/CANONICAL.txt`
- `atoms/<persona>/<topic>/INTEGRATION/CANONICAL.txt`
- `atoms/<persona>/<topic>/HOOK/CANONICAL.txt` (chapter-closer slots when present)
- `SOURCE_OF_TRUTH/teacher_banks/<teacher_id>/<topic>/*.txt` (teacher-mode next-step atoms)

…across **all 5 locales** when the atoms are locale-specific (most are en-US-only today but locale parity per `CJK_CATALOG_PLAN.md` is in flight).

### 15.3 Detection contract

New CI script `scripts/ci/check_atoms_external_book_references.py` (Pearl_Writer ws scope to author — this spec defines its contract):

**Match patterns (high-confidence):**

- Literal mentions of well-known external author surnames + book-noun proximity (`van der Kolk`, `Brach`, `Tolle`, `Hanh`, `Goleman`, `Kabat-Zinn`, `Brown` (Brené), `Maté`, ...) within ±10 words of `book|memoir|guide|manual|workbook|read it|her work|his work`.
- External title patterns: italic-quoted or capitalized-multi-word titles followed by "by" + Capitalized.Name.
- External org/class patterns: `Insight Timer|Calm|Headspace|10% Happier|MBSR|Tara Brach|Plum Village|Spirit Rock|...` (regex registry).
- External URL patterns: any HTTP URL in an atom (atoms should be content-only; URLs are a smell).

**Lower-confidence patterns (review-by-human):**

- "There's a great book about this" / "I learned this from a wonderful teacher" (vague but suspicious).
- Direct "subscribe to" / "check out" / "I recommend" + brand-noun.

**Per-atom output:** TSV row with `(file_path, line_no, match_type, matched_text, suggested_action)`.

### 15.4 Rewrite contract

For each flagged atom, Pearl_Writer (under a follow-up ws gated on operator approval of the audit) rewrites the next-step direction to a **Pearl Prime catalog SKU at locale parity**:

- ja-JP atom → ja-JP catalog SKU; never an en-US SKU.
- The rewritten next-step must be **topic-matched** (anxiety atom → anxiety-topic SKU in same persona's brand-lane when available; nearest-neighbor topic when not).
- Voice is preserved: the atom continues to read in the teacher's voice — only the destination is replaced.
- Format flexibility: the rewrite can recommend a book, audiobook, manga, or music SKU per the atom's natural fit.

### 15.5 What is NOT in scope (V1 audit)

- Atom craft / quality / re-voicing — separate authoring concern owned by Pearl_Editor.
- Removing genuinely useful general references that don't constitute a "go buy this" CTA (e.g., "research on the polyvagal system" is content; "go read Dr. Stephen Porges's *Pocket Guide to the Polyvagal Theory*" is a CTA out of ecosystem).
- Teacher-bank pseudo-biographies that name external influences (those are character-development metadata).

### 15.6 This-session scope = COVERAGE REPORT, not REWRITE

The Pearl_Writer ws opened this session (`ws_pearl_writer_next_step_atom_audit_20260603`) produces only the audit coverage report:

- Run the detector across `atoms/` + `SOURCE_OF_TRUTH/teacher_banks/`
- Output `artifacts/qa/next_step_atom_audit_<date>.tsv`
- Output a summary report at `artifacts/qa/next_step_atom_audit_<date>_summary.md` covering: total atoms scanned, flagged count, distribution by persona × topic, top external-author/title/org references by frequency.

The **rewrite** workstream is a separate, follow-up ws (`ws_pearl_writer_next_step_atom_rewrite_<future-date>`) opened only after operator reviews the audit and ratifies a scope per Q-PRP-WRITER-AUDIT-01 (start narrow vs full sweep).

### 15.7 Anti-drift invariants

- Atoms remain content-only (no URLs, no `<a href>` markup).
- Storefront URLs are NOT embedded in atom text. The atom recommends a Pearl Prime SKU **by content** (title + topic); the storefront's "Customers also bought" / brand-page surface is where readers land for purchase.
- Pearl_Writer ws output is treated as a sensitive content change — operator approval required before any atom file is modified (per `feedback_validation_before_scaling` memory).

---

## §16 — Phased Rollout

| Phase | Scope | Gate to next | Owner |
|---|---|---|---|
| **Phase 1 (MVP)** | en-US locale only; 37 brands × book SKUs only; Stripe Checkout; basic 5-star reviews; manual catalog ingest (no automated cron); §14 CTA cutover for en-US paid-book CTAs; §15 audit-report only | en-US Phase 1 e2e smoke (≥1 real purchase + ≥1 real review + ≥1 download) | Pearl_Dev + Pearl_Int |
| **Phase 2** | + ja-JP locale; + audiobook product type; + manga product type; + automated catalog ingest (per-merge + weekly cron) | ja-JP e2e smoke + audiobook player verified + manga reader verified | Pearl_Dev + Pearl_Localization |
| **Phase 3** | + zh-TW + zh-CN locales; + music product type (Q-PRP-MUSIC-SKU-01); + series bundles (Q-PRP-SERIES-BUNDLE-01); + recommender personalization (Q-PRP-RECO-01) | CJK e2e smoke + music album e2e smoke | Pearl_Dev + Pearl_Localization + Pearl_Audio |
| **Phase 4** | + ko-KR locale (gated on `distribution_status` clearance per `docs/CJK_CATALOG_PLAN.md`) | KO market entry approval | Pearl_Localization + Pearl_PM |

Each phase ships **only** after operator review + sign-off. No silent phase rollover.

---

## §17 — Open Operator Questions (Q-PRP-*)

Sixteen decisions left to the operator. Each has a recommended default. **The Pearl_Architect cap entry remains `proposed` until these are answered.**

| ID | Question | Recommended default |
|---|---|---|
| **Q-PRP-DOMAIN-01** | Domain priority — `pearlprime.shop` / `books.pearlprime.com` / `store.pearlprime.com` / `prime.pearlprime.com` / other? | **`pearlprime.shop`** (clearest commerce signal; subdomains require apex ownership) |
| **Q-PRP-PAY-01** | Payment processor — Stripe Checkout / LemonSqueezy / Paddle / other? Also: CNY coverage acceptable? | **Stripe Checkout** (cheapest at MVP scale; all 5 currencies covered modulo CNY caveats) |
| **Q-PRP-AUTH-01** | Customer accounts — required for purchase / optional / magic-link only / Cloudflare Access? | **magic-link only** (lowest friction Phase 1; Stripe Checkout collects email for guest receipt) |
| **Q-PRP-CART-01** | Cart model — single-item Buy-Now Checkout Phase 1 / multi-item cart with persistence? | **single-item Buy-Now** Phase 1; multi-item Phase 2+ |
| **Q-PRP-REVIEW-01** | Reviews — verified-purchase-only / open to logged-in users / open to anyone with email? Pre- or post-publish moderation? | **open to logged-in users + post-publish + Turnstile**; verified-purchase = badge, not gate |
| **Q-PRP-RECO-01** | "Customers also bought" — reuse phoenix_recommender Phase 1 / hold for Phase 3? | **reuse Phase 1** (already promoted; deterministic) |
| **Q-PRP-PRICE-01** | Default price tiers $0.99 / $4.99 / series-bundle — confirm + per-locale currency mapping? | **$4.99 base ebook, $9.99 audiobook, $1.99 per manga chapter, $9.99 manga series bundle**; locale FX = operator-set per-locale price book, not live-FX |
| **Q-PRP-MANGA-DELIVERY-01** | Full-PDF download only / in-browser WEBTOON reader / both? | **both** (PDF for offline + reader for in-browser) |
| **Q-PRP-AUDIOBOOK-DELIVERY-01** | In-browser streaming / MP3 download / both? | **both** (streaming default + MP3 fallback) |
| **Q-PRP-SAMPLE-01** | Free preview length — first chapter / first 10% / fixed N pages? | **first chapter** (book + manga); **30 sec** (audiobook); first track (music) |
| **Q-PRP-WRITER-AUDIT-01** | Pearl_Writer audit scope — all personas × all topics / staged? | **staged: start with en-US `anxiety` + `overthinking` × all personas; expand by topic after operator review** |
| **Q-PRP-CTA-UNIFY-01** | Hard-cutover external CTA deprecation / soft-deprecate-redirect-replace? | **soft**: storefront URL becomes truth on Phase 1 launch; legacy file archived at Phase 1 + 90d (§14.5) |
| **Q-PRP-LICENSE-01** | Storefront framework license — accept Pearl_Architect's custom-MIT recommendation / pin to MIT/Apache-2.0 only? | **accept custom-MIT** (no framework adopted; our code = MIT) |
| **Q-PRP-ROLLOUT-01** | Phase 1 = en-US ebook only / include ja-JP at launch? | **en-US ebook only** (ja-JP joins at Phase 2 with audiobook + manga; reduces launch surface area) |
| **Q-PRP-MUSIC-SKU-01** | Music brand 38+ SKU shape — per-track / per-album / per-brand-subscription? | **per-album** (Phase 3); per-track + subscription deferred |
| **Q-PRP-SERIES-BUNDLE-01** | Series bundle pricing — fixed % discount off sum / flat tier? | **flat tier**: $9.99 for any 3-volume manga series, $14.99 for any 6-volume |

Per `feedback_operator_proxy_routing` memory: any subset of these that fall within Pearl_Operator_Proxy's envelope may be decided + logged to `artifacts/coordination/operator_decisions_log.tsv` ahead of formal operator review.

---

## §18 — Cross-References

| Cap entry / spec | Relationship |
|---|---|
| `BR-CANON-02` | Path X 37 brands frozen — storefront indexes these, does not mutate |
| `MUSIC-MODE-BRAND-INTEGRATION-V1-01` | Music brands 38+ as first-class — storefront treats music as first-class product type from §2.3 onward |
| `WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01` | 10-surface program → this storefront is **surface 11** (consumer-facing, vs the operator-facing 10) |
| `COVER-REGISTRY-01` | Cover-art sourcing — storefront reads `config/authoring/author_cover_art_registry.yaml` (book pipeline) + manga panel covers from the V5 render path |
| `FULL_FUNNEL_PLAN.md` + `config/funnel/freebie_to_book_map.yaml` | Freebie ↔ paid handoff: freebies remain at lead-magnet pages, "and the full book is here" CTAs route to the storefront |
| `IMG-RENDER-DUAL-PATH-V1-01` | Cover-art render path (Pearl Star + RunComfy) feeds R2 cover assets |
| `MANGA-LAYERED-PIPELINE-V2-01` + `MANGA-RENDER-LINEAGE-01` | Manga page assets sourced from V4/V5 contract + continuity_state render path |
| `PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` | Book pipeline upstream → storefront reads `output_target_path` per row to locate EPUB |
| `PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md` | 12×10×5 spine — storefront does not constrain this, but consumes its outputs |
| `BRAND_ADMIN_CANONICAL_PACKAGE.md` | Operator-facing dashboard — DISTINCT from this consumer storefront; both consume the same upstream catalogs |
| `MUSIC-MODE-FREEBIE-FUNNEL-V1-02` | Music freebies remain freebies; music PAID CTAs route here |
| `COHESIVE-FLOW-PATH-DEFAULT-SPINE-01` | Upstream pipeline contract — no storefront impact, but EPUBs the storefront sells are built on spine-mode |

---

## §19 — LLM Tier Policy Compliance

Per `CLAUDE.md` Tier Policy:

| Surface | Tier | Rationale |
|---|---|---|
| **Storefront frontend runtime** | **NONE** | No LLM calls at request time. All catalog data is pre-projected; reviews are user-authored. |
| **Recommender ("Customers also bought")** | **NONE** | `phoenix_recommender` is deterministic (already promoted). No LLM. |
| **Review submission** | **NONE** | User-authored text; Turnstile for spam; optional moderation deny-list is a regex registry. |
| **Catalog projector script** | **Tier 1** (Claude Code, operator-present) — when authoring | One-time authoring + occasional schema-evolution edits |
| **Review-summary AI feature (optional Phase 3+)** | **Tier 2** Gemma/Qwen on Pearl Star OR **Tier 1** Claude Code attended only | Not in V1 scope; if added, must obey Tier policy |
| **PR governance review** | Existing `pr_governance_review.py` (no LLM) | Continues as today |

**Banned for storefront code:** `ANTHROPIC_API_KEY`, `CLAUDE_API_KEY`, OpenAI cloud, DashScope cloud, Together, Replicate, Perplexity, Cohere, Mistral paid. Enforced by `.github/workflows/llm-policy-enforcement.yml`. Storefront code = no paid LLM dependencies.

---

## §20 — Anti-Drift Summary (the non-negotiables)

1. **Path X 37 brands FROZEN** — storefront reads, never mutates.
2. **Music 38+ FROZEN** — storefront treats music as first-class product type from V1 design, not bolted on at Phase 3.
3. **Pearl Prime visual identity NON-NEGOTIABLE** — dark+amber tokens per §6.1, fonts per §6.1 font preamble.
4. **Custom MIT code, no paid LLM APIs** — per Tier policy.
5. **Cloudflare account `b80152c3...` for provisioning** — per `cloudflare_pages_deploy.md` Traps 1-4.
6. **One PR per ws, no drive-by edits** — this spec PR scope = the 5 files listed in the cap entry.
7. **§14 CTA unification is HARD** — operator directive verbatim, no exceptions.
8. **§15 atom rewrite scope = audit only this session** — rewrite is a separate ws gated on operator approval.

---

## §21 — Glossary (mini)

- **SKU** — Storefront-Keeping Unit; one purchasable item per the §2.5 identity scheme.
- **Brand-lane** — A `(brand_id, locale)` slice of the catalog; e.g., `(stillness_press, ja-JP)`.
- **Inner key** — The brand-and-locale-specific portion of the SKU identity (topic+persona+teacher for book; series_id for manga; album_slug for music).
- **Path X** — The 37-manga-canon brand axis frozen per `BR-CANON-02`.
- **WEBTOON** — Vertical-scroll manga format (vs traditional page-turn); 1080-wide tile convention per `MANGA_LAYER_RENDER_CONTRACT_SPEC.md`.
- **Surface 11** — This storefront, in the 10-surface taxonomy from `WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01`.

---

## §22 — Web Research Citations (used in §3)

| Source | Used for |
|---|---|
| [casualchic/medusa-payload-cloudflare (Meridian)](https://github.com/casualchic/medusa-payload-cloudflare) | Medusa-on-CF reference architecture, MIT license, $5/mo cost envelope, gaps in i18n/digital/reviews |
| [Medusa Digital Products recipe](https://docs.medusajs.com/resources/recipes/digital-products) | Medusa core digital-products approach (recipe + plugin, not built-in) |
| [srindom/medusa-downloadable-products](https://github.com/srindom/medusa-downloadable-products) | Medusa downloadable-products plugin reference |
| [Saleor open-source](https://saleor.io/open-source) + [Saleor docs](https://docs.saleor.io/) | Django/Postgres stack — disqualified for CF Workers native |
| [Vendure GitHub](https://github.com/vendure-ecommerce/vendure) + [Vendure licensing](https://vendure.io/licensing) | GPLv3 license change confirmation; NestJS stack |
| [Snipcart digital products](https://snipcart.com/sell-digital-products) + [Snipcart FAQ](https://snipcart.com/faq) | Drop-in JS + native digital downloads + multi-currency confirmation |
| [Stripe digital downloads patterns](https://docs.stripe.com/mobile/digital-goods/checkout) + [BookFunnel + Stripe](https://blog.bookfunnel.com/2026/sell-direct-with-stripe-and-automatic-bookfunnel-delivery/) | Stripe Checkout delivery patterns; BookFunnel pairing |
| [Cloudflare D1 e-commerce read-replication tutorial](https://developers.cloudflare.com/d1/tutorials/using-read-replication-for-e-com/) | Reference architecture for the §5 topology |
| [Cloudflare Pages overview](https://developers.cloudflare.com/pages/) + [Cloudflare Workers overview](https://developers.cloudflare.com/workers/demos/) | Pages-Workers integration model |
| [LemonSqueezy vs Stripe vs Paddle comparison (2026)](https://designrevision.com/blog/stripe-vs-lemonsqueezy) | Payment-processor pricing + MoR comparison for Q-PRP-PAY-01 |
| [Stripe supported currencies](https://docs.stripe.com/currencies) | Locale currency coverage for §10.5 |
| [ecommerceceo open-source roundup (2026)](https://www.ecommerceceo.com/open-source-ecommerce/) | Disqualified-frameworks roundup (WooCommerce, CS-Cart, Bagisto) |

Total search count: 10 (per spec mandate) + 3 targeted WebFetch confirmations = 13 sources cited.

---

**End of spec.** Operator answers to §17 unblock the AMENDMENT cap entry and fan-out to the 5 child workstreams listed in the §3 of the cap entry and in `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`.
