# Workstream 11: GTM Channel Audit — Manga Distribution
**Date:** 2026-04-18
**Auditor:** Pearl_Architect
**Primary source:** `artifacts/research/global_manga_distribution_strategy.md` (2026-04-05, Pearl_Research)
**Secondary source:** `docs/MANGA_GTM_PLAN.md` (March 2026, Pearl_Marketing)
**Brand source:** `config/brand_management/global_brand_registry.yaml` (312 total brands, 13 lanes, 13 teacher brands per lane)

---

## Executive Summary

Phoenix Omega has no live manga presence on any distribution channel as of 2026-04-18. The GTM plan is strategically sound but has not been executed. KDP, Naver WEBTOON Canvas, Apple Books, and Google Play are all accessible with no account — they are the fastest paths to market. Japan requires a distribution partner (MediaDo) and cannot be entered directly. Tapas and China are blocked for AI-generated content. WEBTOON Canvas AI policy is evolving and requires monitoring before commit.

The correct first wave is: Amazon KDP (US) + Google Play Books + Apple Books via aggregator — all accept AI content with disclosure, all are accessible without partnerships, and they provide the revenue baseline needed to fund the partnership-gated markets (Japan, Korea Originals, China MCN).

---

## Channel Assessment Table

| Channel | AI Allowed? | Royalty / Revenue | Phoenix Omega Status | Lead Time | Priority |
|---------|-------------|-------------------|----------------------|-----------|----------|
| Amazon KDP (global) | Yes — must disclose (Current policy) | 35–70% (70% requires KDP Select) | No account, no titles | 1–2 weeks to first title | P0 |
| WEBTOON Canvas (US + global) | Policy evolving — monitor | Variable ad-share; min payout $25 | No account | 1 week to register; 3 episodes to launch | P0 |
| Apple Books | Yes — must disclose (Current policy) | 70% to publisher | No account | 1–2 weeks via aggregator | P0 |
| Google Play Books | Yes — must disclose (Current policy) | ~52% to publisher (Google takes ~48%) | No account | 1–2 weeks via Partner Center | P0 |
| Bookwalker (Japan) | Not directly accessible — requires KADOKAWA relationship | Publisher negotiated | No account, no path | 6–12 months (partnership only) | P3 |
| Piccoma (Japan + Korea) | Not directly accessible — requires MediaDo or agency | Wait-or-pay model; splits not public | No account, no path | 6–12 months via MediaDo | P2 |
| Naver WEBTOON Canvas (Korea) | Policy evolving — same as WEBTOON global | Ad share + Super Likes; 50–70% for Originals | No account | 1 week to register | P1 |
| Direct storefront (Shopify + Cloudflare R2) | Self-governed | 100% margin minus payment processing (~2.9% + $0.30) | Not deployed for manga | 2–4 weeks build | P2 |
| Audible ACX | Audiobook format — not applicable to manga visual format directly | 25–40% royalty | Not applicable for manga panels | N/A | Out of scope |
| Tapas | NO — AI-generated art explicitly banned (Jan 2023 policy) | ~70% ad share | Blocked by policy | N/A until policy changes | BLOCKED |
| GlobalComix | Not explicitly banned — likely permitted | Up to 70% of subscription fees | No account | 1–2 weeks | P1 |
| Lezhin Comics | Not publicly stated — check before submission | Per-episode; negotiated | No account; submission required | 3–4 weeks (review) | P2 |
| LINE Manga (Japan) | Requires partnership — AI policy unknown | ~50–60% to publisher (industry standard) | No account, no path | 12+ months via MediaDo | P3 |
| PublishDrive (aggregator) | Passes through to store policies | Store royalties minus aggregator fee | No account | 1 week setup | P1 (enables scale) |

---

## Per-Channel Deep Assessment

### 1. Amazon KDP (Global Ebook / Print)

**AI content policy:** Accepted with disclosure. KDP requires AI-generated content to be flagged during upload. Authors must confirm whether AI tools were used for text or images. No ban on AI art for manga as of current policy. Source: `global_manga_distribution_strategy.md` Appendix C.

**Royalty structure:** 35% royalty available without restrictions (any price, any market). 70% royalty requires: price between $2.99–$9.99, KDP Select enrollment (90-day exclusivity on Kindle format), and availability in supported markets. For manga volumes, 35% royalty is typical unless KDP Select exclusivity is acceptable.

**Manga category support:** Full support. Comics & Graphic Novels > Manga categories available. Warning: ~27% of KDP category options are ghost categories with no browsing page; ~54% are duplicates. Each format (ebook/paperback/hardcover) gets 3 independent category slots. Kindle Comic Creator tool required for KPF format.

**Format requirements:** 1600x2560px pages, 300 DPI minimum; cover 2560x4096px ideal. File size: 650MB max.

**Phoenix Omega current presence:** No KDP account exists. No titles live.

**Submission process:** Create KDP account → use Kindle Comic Creator to build KPF from panel images → upload through KDP dashboard. No bulk upload for self-publishers. One book at a time. Approx. 24–72 hours for review before going live.

**Lead time to first title:** 1–2 weeks (account setup + first 3-panel chapter packaged as KPF).

**Priority: P0.** Lowest barrier, highest per-unit margin, global reach, AI-disclosed.

---

### 2. WEBTOON Canvas (US + Global)

**AI content policy:** Evolving. No explicit ban as of 2026-04. The 2026 unified Canvas platform across 7 languages launched spring 2026. Policy has not followed Tapas in banning AI art. Must monitor. Source: `global_manga_distribution_strategy.md` Appendix C.

**Revenue model:** Ad Revenue Sharing Program (variable based on views), Super Like tips, Reward Ads (expanded 2026), Patreon integration. Minimum payout reduced from $100 to $25 in 2026.

**Format requirements:** 800px wide, 1280px per strip segment, JPG or PNG, under 2MB per image, under 20MB per episode. VERTICAL SCROLL format required — Phoenix Omega's current page-format pipeline output needs horizontal-to-vertical conversion before upload.

**Phoenix Omega current presence:** No account. No series registered.

**Submission:** Free, open self-publishing. Create creator account, upload 3+ episodes to launch a series, then weekly cadence. Built-in episode scheduler available.

**Lead time:** 1 week to register + 3 episodes to launch. First episode visible immediately after upload.

**Priority: P0** — but conditional on format conversion (page-format → vertical scroll) and continued AI policy monitoring.

---

### 3. Apple Books

**AI content policy:** Accepted with disclosure. Apple Books requires metadata declaration of AI usage but does not ban AI-generated content. Source: `global_manga_distribution_strategy.md` Appendix C.

**Manga support:** Yes — Comics & Graphic Novels is a major Apple Books category. Top 20 manga chart sold 192,230 units averaging 9,612 units/title in 2025. Manga consistently outperforms superhero and author categories.

**Revenue split:** Publisher receives 70% of sale price (Apple takes 30%).

**Access:** EPUB or .ibooks format. Best accessed via aggregator (PublishDrive, Draft2Digital) for bulk distribution. Direct iTunes Connect access available but slower for initial setup.

**Phoenix Omega current presence:** No Apple Books account or aggregator relationship established.

**Lead time:** 1–2 weeks via PublishDrive aggregator.

**Priority: P0.**

---

### 4. Google Play Books

**AI content policy:** Accepted with disclosure. Google Play Books Partner Center requires metadata including AI disclosure. Source: `global_manga_distribution_strategy.md` Appendix C.

**Manga support:** Yes — Comics & Graphic Novels category with dedicated manga sub-genres for Japan and South Korea.

**Revenue split:** Publisher receives approximately 52% of sale price (Google takes approximately 48%).

**Access:** Free to publish. Sign up via Google Play Books Partner Center. Fixed-layout EPUB for manga. Bulk upload via spreadsheet + file upload available.

**Phoenix Omega current presence:** No Google Play Partner Center account.

**Lead time:** 1–2 weeks.

**Priority: P0.**

---

### 5. Bookwalker (Japan-specific)

**Entry requirements for foreign publishers:** Bookwalker is a KADOKAWA-operated ebook platform. Taiwan/HK version is accessible as a secondary channel, but the Japan Bookwalker requires a publisher relationship with KADOKAWA or a distribution partner. Not open for direct self-publishing.

**AI content policy:** Not publicly stated for Japan. Platform primarily licenses established publisher content.

**Revenue model:** Publisher negotiated. KADOKAWA standard industry splits (approximately 50-60% to publisher).

**Phoenix Omega current presence:** No account, no path. Would require MediaDo partnership to access Japan Bookwalker.

**Lead time:** 6–12 months (partnership negotiation required).

**Priority: P3** — defer until Japan MediaDo partnership is established.

---

### 6. Piccoma (Japan + Korea vertical scroll)

**Entry requirements:** Kakao's Japanese subsidiary operates Piccoma. #2 manga app in Japan (US$418M+ revenue 2024). Requires editorial relationship or distributor partnership. Not open self-publishing.

**Revenue model:** Wait-or-pay freemium. Readers wait for free access or pay coins immediately. Publisher revenue split not publicly disclosed.

**Publisher vs. creator track:** No creator track. Publisher/distributor track only.

**Phoenix Omega current presence:** No account, no path. Requires MediaDo or agency.

**Lead time:** 6–12 months.

**Priority: P2** — high revenue potential for Japan market at scale, but partnership-gated.

---

### 7. Naver WEBTOON Canvas (Korea)

**Creator program vs Originals:** Canvas is the open creator tier (anyone can publish, reviewed for guidelines). Originals are commissioned by WEBTOON editorial — requires Canvas track record + pitch.

**Revenue model for Canvas:** Ad revenue sharing, Super Likes, potential Original promotion. Canvas ad-share rate not publicly disclosed; reportedly 50–70% for Originals.

**Language requirements:** Korean-language content preferred for Korean audience, but English content is accepted and discoverable. The 2026 unified platform serves 7 languages; Korean is primary for the KR market.

**AI policy:** Same as WEBTOON Canvas global — evolving. No explicit ban as of 2026-04.

**Phoenix Omega current presence:** No account.

**Lead time:** 1 week to register Canvas account. Korean-language titles require localization (ko-KR translation pass through existing localization pipeline).

**Priority: P1** — low barrier, high growth market. Korean government Translation Support Center may co-fund localization in 2026.

---

### 8. Direct Storefront (Shopify + Cloudflare R2)

**Current status:** Not deployed for manga. Phoenix Omega's weekly rollout design has not included a direct manga storefront.

**Revenue model:** 100% margin minus payment processing. Shopify: 2.9% + $0.30 per transaction (Basic plan). Cloudflare R2: $0.015/GB storage + $0.36/GB egress. For a $4.99 manga chapter purchase, net to Phoenix Omega: approximately $4.69 minus hosting.

**Formats supported:** Unlimited flexibility — PDF, EPUB, CBZ, streaming reader, any format the builder implements.

**Lead time:** 2–4 weeks to build and deploy a manga reader storefront with Shopify checkout + Cloudflare R2 delivery.

**Priority: P2** — best margin, zero platform risk, but requires build investment and organic traffic (no marketplace discovery). Best as complement to platform presence, not lead channel.

---

### 9. Audible ACX (Audiobook Distribution)

**Scope:** ACX is for audiobooks (audio files + cover art). Manga visual content is out of scope for ACX.

**Relevance to Phoenix Omega manga:** If Phoenix Omega creates audio-enhanced manga (panel images + narration audio), this would be a novel format that Audible does not currently support as a standard format. Audiobook versions of therapeutic manga storylines (audio-only adaptation) would be ACX-eligible, but this is a separate content format from manga panels.

**AI-disclosed content policy:** ACX/Audible does not currently ban AI-generated audio or narration but may require disclosure depending on content. Policy evolving as of 2026.

**Phoenix Omega current presence:** Audible is referenced in `docs/AUDIOBOOK_PIPELINE_COMPLETE_GUIDE.md` and `docs/LOCALE_CATALOG_MARKETING_PLAN.md` for the audiobook pipeline. No manga-specific ACX presence planned.

**Priority: Out of scope for manga visual distribution.** Relevant for audiobook pipeline only.

---

## Brand × Market Priority Matrix

### Brands in scope (from global_brand_registry.yaml)

312 total brands across 13 locale lanes. 13 teacher brands per lane. The 13 core teacher brand archetypes with the clearest manga identity are:

| Brand Archetype | Teacher | Focus | Manga Genre Fit |
|----------------|---------|-------|----------------|
| Inner Light Press | ahjan | Meditation, mindfulness | Iyashikei (healing slice-of-life) |
| Zen Clarity | junko | Mental clarity, overthinking | Dark psychological / quiet drama |
| Still Forest | joshin | Nature-based grounding | Cozy contemplative |
| Iron Will | master_wu | Discipline, resilience | Power progression / martial arts |
| Truth Compass | maat | Boundaries, self-worth | Webtoon vertical slice-of-life |
| Gen Spark | miki | Gen Z grounding, identity | Webtoon vertical / contemporary |
| Body Wisdom | pamela_fellows | Somatic awareness | Therapeutic drama |
| Healing Ground Press | sai_ma | Grief integration | Iyashikei / emotional drama |
| Cosmic Edge | ra | Purpose, existential clarity | Dark psychological / sci-fi tones |
| Vitality Path | master_feung | Energy, life force | Action / wellness hybrid |
| Awakening Press | adi_da | Spiritual awakening | Philosophical drama |
| The Theater & The Gift | omote | Authenticity, Noh | Experimental / literary |
| Sacred Ground | master_sha | Healing practices | Spiritual drama |

### First-wave brand selection (3 brands for launch)

Criteria: (1) strongest manga genre fit, (2) highest commercial accessibility in English-first markets, (3) visual identity already developed (all 13 teachers have triptych art in teacher_showcase.html).

| Rank | Brand | Teacher | Rationale | Target Channels | Markets |
|------|-------|---------|-----------|-----------------|---------|
| 1 | Gen Spark (en_US) | miki | Gen Z audience = native webtoon readers. Identity/confidence themes = WEBTOON Canvas sweet spot. Vertical scroll format aligns with Gen Z consumption. English-first. | WEBTOON Canvas → Amazon KDP volume | US, then KR Canvas |
| 2 | Zen Clarity (en_US) | junko | Mental clarity / overthinking = top-performing therapeutic category. Clean minimalist visual style is easiest to produce consistently. Dark psychological archetype = strong WEBTOON audience. | Amazon KDP → Google Play → Apple Books | US, then FR (55% webtoon growth) |
| 3 | Iron Will (en_US) | master_wu | Discipline / resilience = highest-converting self-help category globally. Power progression manga = established audience on all platforms. Martial arts themes are globally legible without heavy localization. | Amazon KDP → WEBTOON Canvas → Naver Canvas KR | US, KR, then JP (via MediaDo) |

### Reasoning

- **Gen Spark first** because WEBTOON Canvas (the highest-discovery free channel) is most accessible to Phoenix Omega immediately, and Gen Z audiences are the platform's primary demographic. The brand's focus on identity formation maps directly to what WEBTOON Canvas readers seek.
- **Zen Clarity second** because KDP/Apple/Google are the revenue-generating channels, and junko's minimalist visual style is the most achievable with the current (pre-editorial-loop) pipeline quality. Low visual complexity = lower risk of the consistency failures identified in WS8.
- **Iron Will third** because master_wu has one of the strongest globally legible themes, and the brand's archetype matches Korean market preferences (discipline, martial progression). Once Naver Canvas is registered, Iron Will content can launch in Korean with translation support.

---

## Rollout Timeline (Revised from GTM Plan)

The existing GTM plan's Q2 2026 launch target for US/Canada (KDP, Apple Books — 10 titles) is achievable only if the pipeline quality issues in WS8 are fixed first. Shipping the current pipeline output to KDP would produce rejections or, worse, live titles at 3.7/10 quality establishing a negative brand reputation.

**Recommended revised timeline:**

```
April–May 2026:  Fix P0 pipeline quality issues (WS8 character consistency + seed locking)
                  Register Amazon KDP account, WEBTOON Canvas account, Google Play Partner Center

June 2026:        First 3 titles (Gen Spark, Zen Clarity, Iron Will) — KDP + Google Play + Apple Books
                  WEBTOON Canvas series registered for Gen Spark (3-episode launch)

Q3 2026:          Naver WEBTOON Canvas registration for Korean locale
                  PublishDrive aggregator account for multi-market ebook scaling
                  WEBTOON Canvas weekly cadence established for Gen Spark + Zen Clarity

Q4 2026:          GlobalComix + Lezhin Comics submission for Iron Will
                  MediaDo partnership outreach begins (Japan P0)

Q1 2027:          Japan MediaDo deal closes → Piccoma + LINE Manga entry
                  Korea Originals pitch (if Canvas performance justifies)
                  Direct storefront (Shopify + Cloudflare R2) build

Q2 2027:          France (Izneo + Amazon KDP FR) + Germany/UK/Spain
                  Second wave: 10 additional titles across 3–5 brands
```

---

## Critical Risks and Blockers

| Risk | Severity | Current Mitigation | Gap |
|------|----------|-------------------|-----|
| WEBTOON Canvas bans AI art | HIGH | Monitor only | No policy monitoring automation; manual review needed before each season |
| Pipeline quality insufficient for platform acceptance | CRITICAL | WS8 fixes must precede launch | No editorial loop yet (WS8 Gap C) |
| No KDP account set up | HIGH | GTM plan recommends Q2 2026 | Account creation not yet actioned |
| Japan requires MediaDo partnership — 6-12 month lead time | MEDIUM | Identified in GTM plan | No outreach initiated |
| Tapas policy blocks AI manga indefinitely | LOW | Plan already excludes Tapas | Confirmed blocked |
| Vertical scroll format not in current pipeline | HIGH | Research identifies requirement | Page-to-vertical scroll conversion script not built |

**The vertical scroll format gap is the most under-documented risk.** WEBTOON Canvas (global), Naver Canvas (Korea), and Piccoma (Japan/Korea) all require vertical scroll format. The current manga pipeline produces page-format output (traditional manga panels). A format conversion step (page-format panels → long-strip vertical scroll with panel re-ordering) is needed before any webtoon platform launch. This is not mentioned in the GTM plan's immediate next steps.

---

## Immediate Next Steps (Pre-Launch Blockers)

1. **Create Amazon KDP account** — 30 minutes. Unblocks the fastest revenue path.
2. **Create WEBTOON Canvas creator account** — 30 minutes. Unblocks US + Korea webtoon distribution.
3. **Create Google Play Books Partner Center account** — 1 hour.
4. **Build vertical scroll format export** — Convert page-format panel output to 800px-wide vertical strip. Required for all webtoon platform launches.
5. **Fix WS8 P0 character consistency issues** before any platform submission.
6. **Select 3 launch titles** from Gen Spark, Zen Clarity, Iron Will brands using EI v2 therapeutic value scores.
7. **Initiate MediaDo contact** for Japan entry (long lead time — start now even if Japan launch is Q1 2027).
