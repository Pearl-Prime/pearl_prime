# Phoenix Omega — Brand Admin Distribution Index

**Date:** March 2026
**Authority:** Pearl_Marketing + Pearl_Research
**Governance:** GTM plan in `docs/MANGA_GTM_PLAN.md`

---

## Overview

This index links the five locale-specific distribution guides that govern how Phoenix Omega brands reach readers across ebook, audiobook, and manga platforms worldwide.

## Distribution Guides

| Locale | Brands | Ebook Platforms | Audiobook Platforms | Manga Platforms | Market Entry Complexity | Guide |
|--------|--------|-----------------|---------------------|-----------------|------------------------|-------|
| en_US | 24 | 6 | 6 | 6 | Low — self-serve portals | [en_US Guide](en_US_distribution_guide.md) |
| zh_TW | 6 | 5 | 3 | 4 | Low — direct upload, no censorship | [zh_TW Guide](zh_TW_distribution_guide.md) |
| zh_HK | 6 | 4 | 3 | 3 | Low — direct upload | [zh_HK Guide](zh_HK_distribution_guide.md) |
| zh_CN | 6 | 4 | 3 | 3 | **High** — MCN agent required, tax + legal | [zh_CN Guide](zh_CN_distribution_guide.md) |
| zh_SG | 6 | 4 | 3 | 3 | Low — English + Chinese dual-channel | [zh_SG Guide](zh_SG_distribution_guide.md) |
| ko / es-US / es-ES / fr / de / it / hu / pt-BR | — | see guide | see guide | see guide | Low–Medium — mostly self-serve + local retailers | [Global Markets Guide](global_markets_distribution_guide.md) |

**Total:** 48 brands across the 5 original locale guides. The 14-lane Weekly-OS
platform truth (all markets above) is encoded in
`config/brand_management/brand_admin_weekly_os_platforms.yaml` →
`brand-wizard-app/public/brand_admin_weekly_os_data.json`; the eight non-CJK
markets are documented in the [Global Markets Guide](global_markets_distribution_guide.md).

## Brand Count Summary

- **en_US (24):** stabilizer, somatic_reset, sleep_repair, panic_first_aid, emotional_resilience, grief_companion, gentle_recovery, inner_security, breathwork_lab, focus_forge, adhd_anchor, dopamine_balance, habit_builder, clarity_engine, high_efficiency, longevity_path, metabolic_reset, movement_intelligence, creative_reclaiming, identity_rebuild, quiet_confidence, relational_healing, gen_z_grounding, contemplative_wisdom
- **zh_TW (6):** sleep_repair_tw, stabilizer_tw, panic_first_aid_tw, gen_z_grounding_tw, grief_companion_tw, inner_security_tw
- **zh_HK (6):** sleep_repair_hk, stabilizer_hk, panic_first_aid_hk, gen_z_grounding_hk, grief_companion_hk, inner_security_hk
- **zh_CN (6):** sleep_repair_cn, stabilizer_cn, panic_first_aid_cn, gen_z_grounding_cn, grief_companion_cn, inner_security_cn
- **zh_SG (6):** sleep_repair_sg, stabilizer_sg, panic_first_aid_sg, gen_z_grounding_sg, grief_companion_sg, inner_security_sg

## Content Lane Timeline (GTM Plan)

| Lane | Q2 2026 | Q3 2026 | Q4 2026 |
|------|---------|---------|---------|
| Ebook | en_US launch on KDP + Apple Books | zh_TW, zh_HK, zh_SG launch | zh_CN via MCN agent |
| Audiobook | en_US launch on ACX + Apple | All locales expand | zh_CN via MCN agent |
| Manga | en_US pilot on Webtoon Canvas | zh_TW, zh_HK, zh_SG launch | zh_CN via MCN agent |

## Key Governance Notes

1. All distribution actions must pass push-guard and preflight before catalog updates are committed.
2. zh_CN market entry requires legal review before any upload — see the zh_CN guide for the full compliance checklist.
3. Revenue splits and platform terms are current as of March 2026 and must be re-verified quarterly.
4. Manga adaptation priority brands: gen_z_grounding, identity_rebuild, emotional_resilience, grief_companion.

## Next Steps

- Brand admins: read your locale-specific guide and confirm platform account readiness.
- Pearl_Marketing: finalize MCN agent selection for zh_CN by end of Q2 2026.
- Pearl_Research: update platform revenue data quarterly.
