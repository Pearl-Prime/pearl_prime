# Phoenix Omega — Canonical Presentation Set

## What this is

Five files that together form the canonical brand-admin and investor-facing presentation package for Phoenix Omega. They are meant to be used as a set, not as isolated documents.

## The files

| File | Audience | Theme | Purpose |
|------|----------|-------|---------|
| `brand_onboarding_hub.html` | All brand admins | Dark | Starting point — brand explorer, V3.2 systems overview, QA checklist, changelog |
| `us_brand_admin_v32_briefing.html` | US brand admins | Dark | Deep briefing on the seven V3.2 marketing systems with action items |
| `jp_brand_admin_v32_briefing.html` | JP brand admins | Light (intentional for JP market readability) | V3.2 systems adapted for Japan, manga variants, cultural adaptations |
| `writer_v32_quick_reference.html` | Writers / content producers | Dark | Field-level reference for all 21 V3.2 parameters with type, constraints, and examples |
| `PHOENIX_OMEGA_INVESTOR_DD.xlsx` | Investors / due diligence | N/A | 10-sheet financial model with Data Provenance guide and assumption labeling |

## Design language

The four HTMLs share a unified design language: Inter font family (plus Noto Sans JP for the JP briefing), indigo accent (#6366F1), consistent component patterns (8px radius cards, 3-tier text hierarchy). The JP briefing intentionally uses a light theme for cultural readability; the other three use a dark theme.

All HTMLs are static, framework-free (no React, no Tailwind), and WordPress-safe.

## Investor workbook — numbers discipline

The workbook's first sheet ("Data Provenance") explains the labeling system:

- **REPO-BACKED** (green text): Verifiable from repo code, config, or docs
- **ESTIMATE** (orange text, yellow background): Derived from planning model, reasonable but unverified
- **ASSUMPTION** (red text, yellow background): Pre-revenue projection with no sales data
- **EXTERNAL** (blue text): Sourced from third-party research

Every sheet has a DATA SOURCE column. Revenue projections, conversion rates, and growth figures are all labeled ASSUMPTION. The workbook is pre-revenue; no revenue numbers are actuals.

## Where numbers come from

- Brand count (24), teacher count (13), brand personas, price ranges: `config/brand_registry.yaml`, `config/catalog_planning/brand_archetype_registry.yaml`, `config/authoring/`
- Pipeline architecture, EI V2: `phoenix_v4/quality/ei_v2/`, pipeline docs
- $0 COGS claim: auto-narration pipeline (repo-verified)
- Market sizing: Grand View Research 2025 (external)
- All revenue, conversion rates, impressions: modeled assumptions, not actuals

## How to use this set

1. Start with `brand_onboarding_hub.html` for orientation
2. Go to the relevant briefing (US or JP) for the V3.2 systems deep-dive
3. Use `writer_v32_quick_reference.html` as a field reference during content production
4. Use the investor workbook for financial due diligence — read the Data Provenance sheet first

## Authority

This set is governed by workstream `ws_brand_admin_investor_enhancement_20260328` in `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`. Design guidance was drawn from `old_chat_specs/chat_clause_marketing_close_prez.txt` (historical design notes, not current truth).

Last updated: 2026-03-28
