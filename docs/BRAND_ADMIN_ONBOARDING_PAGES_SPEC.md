# Brand Admin Onboarding — Pages Spec

**Purpose:** Page-level structure for the **static spine** around the wizard. Interactive wizard + JSON live on **Cloudflare Pages** per deployment doc; these pages may live in-repo (deployed with Pages) or as **WordPress** shells that link/embed—**pick one source per URL** to avoid drift.

**Related:** [specs/BRAND_ADMIN_ONBOARDING_WIZARD_SPEC.md](../specs/BRAND_ADMIN_ONBOARDING_WIZARD_SPEC.md), [specs/ONBOARDING_OUTPUT_PROOF_SYSTEM.md](../specs/ONBOARDING_OUTPUT_PROOF_SYSTEM.md), [specs/BRAND_ADMIN_MEDIA_GENERATION_SPEC.md](../specs/BRAND_ADMIN_MEDIA_GENERATION_SPEC.md), [specs/BRAND_ADMIN_ONBOARDING_IMAGE_PACK_V1_TRUST_LAYER_SPEC.md](../specs/BRAND_ADMIN_ONBOARDING_IMAGE_PACK_V1_TRUST_LAYER_SPEC.md) (Image Pack v1: hero/gallery/matrix/wizard placement map), [BRAND_ADMIN_CANONICAL_PACKAGE.md](../BRAND_ADMIN_CANONICAL_PACKAGE.md).

---

## 1. `brand_admin_master_onboarding.html` (supporting spine)

**Until product sign-off:** not the canonical “start here”; link from [brand_onboarding_hub.html](../brand_onboarding_hub.html).

Sections: Hero → Vision/Mission → Opportunity → How the system works → What brand admins do → Compare lanes (summary) → CTA to wizard + gallery + matrix + weekly OS.

Components: `HeroBanner`, `CTAGroup`, `OutputProofStrip` (registry-driven, proof-pending safe).

---

## 2. `brand_admin_weekly_os.html`

Role snapshot; Mon–Sun cards; judgment vs automation split; KPI stubs; common failure modes.

---

## 3. `market_lane_matrix.html`

Filter bar (stub); matrix columns: market, audience fit, platform mix, traction hint, admin load, revenue profile, proof example link, “recommended for.”

---

## 4. `lane_examples_gallery.html`

Sections per lane (self-help, audiobook, manga, Pearl News, tools). Load [example_registry.json](../config/onboarding/example_registry.json); group by `comparison_set_id` for boards; apply proof-pending rules.

Rendering behavior:

- Primary proof is inline media (not link-first UI).
- If row `status` is `ready`, render the media inline (`<img>` or `<video>` by asset type).
- If row is not ready, render proof-pending fallback state.
- Links are secondary actions only (metadata/download/open-in-new-tab), not the primary proof surface.

---

## 5. Navigation

All spine pages link to: hub, deployed wizard (`https://brand-admin-onboarding.pages.dev`), gallery, matrix, weekly OS.

Use one canonical public wizard URL in copy and WP shells to avoid split-routing drift.

---

## 6. Styling

Match typography and card patterns from [brand_onboarding_hub.html](../brand_onboarding_hub.html) where possible.
