# Funnel Status — 2026-04-10

**Project:** proj_state_convergence_20260328
**Session:** funnel-activation
**Status:** All 15 topics wired (en_US)

## What's LIVE After This PR

- 15 freebie landing pages (en_US, brand-wizard-app/public/free/)
- 15 email sequence templates (config/funnel/email_templates/ — need GHL activation)
- 15 freebie-to-book mappings (config/funnel/freebie_to_book_map.yaml)
- 15 registered freebie slugs (config/freebies/freebie_registry.yaml — Gate 16 compliant)
- 15 proof loop entries (config/freebies/funnel_proof_loop.yaml — email trigger wired)
- GA4 tracking on all 15 pages (G-PLACEHOLDER — owner must replace with real ID)
- Store URLs: landing redirects (pending real platform uploads)
- Store URL tracker: config/funnel/store_url_tracker.yaml (swap when books go live)

## Topic Map

| Topic | Freebie Slug | Catalog ID | Series ID |
|-------|-------------|-----------|-----------|
| anxiety | anxiety-nervous-system-reset | CAT-E32709F72B72 | SER-279D9C44 |
| burnout | burnout-energy-audit | CAT-14B5C0D58EC1 | SER-61A56EC7 |
| self_worth | self-worth-inventory | CAT-65AE85E345C6 | SER-EEC7097A |
| imposter_syndrome | imposter-evidence-log | CAT-3D46736D06F9 | SER-D336EE82 |
| boundaries | boundaries-script-kit | CAT-6F997E15EC81 | SER-21F36B63 |
| depression | depression-momentum-kit | CAT-0CCEB8778D2C | SER-384A183D |
| courage | courage-decision-map | CAT-7A399F390DBA | SER-92C54191 |
| overthinking | overthinking-thought-sorter | CAT-CD0893B57DA3 | SER-1C448D8E |
| compassion_fatigue | compassion-fatigue-audit | CAT-2D9D3BA44B36 | SER-C2F2EA5D |
| social_anxiety | social-anxiety-toolkit | CAT-9F43F71C337E | SER-E01644A4 |
| sleep_anxiety | sleep-anxiety-wind-down | CAT-F7F5688DBD50 | SER-54F19D2D |
| financial_anxiety | financial-anxiety-check-in | CAT-F5229F211EF6 | SER-011E1C44 |
| financial_stress | financial-stress-audit | CAT-409ADE12A9F3 | SER-E9B764B2 |
| somatic_healing | somatic-body-scan | CAT-A9154F426D59 | SER-4E641AD5 |
| grief | grief-letter-template | CAT-69C6B1006576 | SER-24CF9913 |

## Pending (Manual / Off-Repo)

| Item | Owner | Blocker |
|------|-------|---------|
| GHL sub-account setup + email template loading | Brand admin | No leads are nurtured until this is done |
| GA4 measurement ID (replace G-PLACEHOLDER) | Brand admin | No analytics data |
| Real platform store URLs (KDP, Google Play, Apple Books, Kobo) | Brand admin | E4 email sends to landing redirect, not store |
| Book 2-7 real titles | Pearl_Writer | E5 upsell emails have placeholders |

## Phase 2 (After en_US Proven)

- CJK6 freebie assets (LINE/WeChat/KakaoTalk)
- CJK6 email sequences (translated)
- Per-locale landing pages (ja_JP, ko_KR, zh_CN, zh_TW, zh_HK, zh_SG)
- Ximalaya direct upload integration (zh-CN)
