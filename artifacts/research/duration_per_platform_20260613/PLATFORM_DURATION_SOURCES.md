# Platform Duration Sources — what each surface rewards by length (cited)

**Date:** 2026-06-13 · **Agent:** Pearl_Research (platform-duration strategy) · **Mode:** deep web research (Tier-1, operator-present), 7 parallel per-platform research passes synthesized
**Companion docs:** `DURATION_PER_PLATFORM_PLAN.md` (the tier×platform×locale matrix) · `DURATION_GAP_VERIFICATION.md` (our durations vs these targets)
**Validates / refreshes:** `specs/CONTENT_DURATION_INTELLIGENCE_DEV_SPEC.md` §4 (CDIS, 2026-03-31, "43 source clusters") + `docs/PLATFORM_ALGORITHM_RESEARCH_2026.md` (2026-04) + `config/duration/platform_duration_profiles.yaml` + `config/catalog_planning/platform_knob_tuning.yaml`

> **Citation count: 50+ external sources below** (≥6 per platform cluster × 7 clusters), plus 3 internal cross-refs. Confidence is per-line. `[verify]` = number is inferred / weak-sourced / needs a native measurement. **No source or number here is fabricated;** where the web gave no hard figure, the line says so.

---

## How to read the "winning length"

Every platform monetizes differently, so "the length that wins" means a different thing per surface:

| Revenue model | Platforms | What length does |
|---|---|---|
| **Subscription read-through** (pay per page/hour consumed) | KDP **Kindle Unlimited**; Spotify Premium audiobooks (pro-rata hours); Audible **new** consumption pool (May 2026) | **Length × completion = revenue.** Longer *fully-consumed* book earns more. Thin book earns almost nothing. |
| **Credit / per-sale, length-tiered price** | Audible à-la-carte; ACX credit | **Length sets the price tier** → royalty. Sub-3hr lands in the bottom price tier and "isn't worth a credit." |
| **Flat per-sale** (% of one transaction) | Apple Books, Google Play, Kobo | Length = **price justification only**, not a payout lever. Pay-per-sale doesn't care about read-through. |
| **Ad + unlock micro-txn** | YouTube (ads/watch-time); WEBTOON/Piccoma/Kakao (ad-scroll + coin-unlock) | Watch-time / scroll-dwell → ads; **chapter count** → unlock conversions; **cadence** → ARPU. |

This is why the same 22k-word book is a credible podcast season, a KDP "short read," and a sub-floor Audible title all at once — the surface decides.

---

## §1 — Amazon KDP (Kindle ebook + Kindle Unlimited)

**Winning length:** **30,000–50,000 words ≈ 150–230 print pp ≈ 200–330 KENP pp.** Self-help consensus center **35–45k words (~170–210 pp).** **CDIS "150–230pp / $4.99–$9.99" VALIDATED**, with one correction: the 70% royalty band opens at **$2.99**, so encode the band $2.99–$9.99 with $4.99 as default, not floor.

**Thresholds:** delisting floor ~2,500 words · credible self-help-book floor ~25–30k words (~120–150pp; below = "short read") · sweet spot 30–50k / 150–230pp · practical max ~70–75k (completion decays past it).

**Why length wins on KU:** author KU royalty = **KENP pages actually read × the monthly per-page rate** (KDP Select Global Fund ÷ total KENP read). Rate is **rising**: ~$0.0041 (Jan 2025) → **~$0.00482 (Apr 2026)**; rule of thumb **~$0.0045/page**. A fully-read 250-KENP-page book earns **~$1.10–1.25/borrow** vs ~$0.30–0.45 for a 70–100pp short read — **length × completion is a direct, strengthening revenue lever.** Short reads forfeit the 70% band (drift to 99¢/35%) and read as funnel entries, not earners. Conversions: print page ≈ **250 words**; KENP page ≈ **~200 words** (community-measured, no official figure).

- [K1] *Up to Date List of KDP Global Fund Payouts* — Written Word Media — https://www.writtenwordmedia.com/kdp-global-fund-payouts/ — accessed 2026-06-13, latest Apr 2026 — **HIGH** (monthly KENP rate + Global Fund tracker; Apr 2026 ≈ $0.00482)
- [K2] *Royalties in Kindle Unlimited* — Amazon KDP (official) — https://kdp.amazon.com/en_US/help/topic/G201541130 — accessed 2026-06-13 — **HIGH** (KENP/Global Fund mechanism; 3,000-page/borrow cap; first-read-only)
- [K3] *How Many Words Per Page In a Book? (900-author survey)* — Kindlepreneur (Dave Chesson) — https://kindlepreneur.com/words-per-page/ — accessed 2026-06-13 — **HIGH** (nonfiction ≈ 233 words/Amazon-page; print ≈ 250)
- [K4] *eBook royalty / 70% band* — Amazon KDP (official) + Author Imprints 2025 pricing guide — https://kdp.amazon.com/en_US/help/topic/G200644210 · https://www.authorimprints.com/amazon-kdp-royalty-pricing/ — accessed 2026-06-13 — **HIGH** ($2.99–$9.99 = 70%; $0.15/MB delivery fee)
- [K5] *Amazon Short Reads: words per page / time buckets* — Life and Work — https://lifeandwork.blog/amazon-short-reads-how-many-words-equal-a-page/ — accessed 2026-06-13 — **MED** (Short Reads 15–120 min, 1–100pp / 250–25k words @250 w/pg)
- [K6] *Word counts vs KENPC for KU* — KBoards + John Dopp — https://www.kboards.com/threads/word-counts-vs-kenpc-for-kindle-unlimited.217364/ · https://johndopp.com/writers/kindle-unlimited-page-counts-adjusted/ — accessed 2026-06-13 — **MED** (KENP ≈ 180–200 words/page; varies with formatting)
- [K7] *Minimum/Maximum KDP word count, pages, file sizes* — Just Publishing Advice — https://justpublishingadvice.com/kdp-word-count-file-sizes-and-pages/ — accessed 2026-06-13 — **MED** (2,500-word delisting floor; 3,000 KENP/borrow cap)
- [K8] *How long should my book be? (nonfiction ≈ 30k floor; 50–75k = 153–230 ebook pp)* — Publishing.com — https://www.publishing.com/blog/self-publishing-faq-how-long-should-my-book-be — accessed 2026-06-13 — **MED**

**Strategic surprise:** KU per-page rate is *climbing*, not eroding — read-through is a strengthening channel; pushing books to the upper 150–230pp band (with high completion) compounds with the rising rate. Short reads are a **series/cadence funnel** play (Amazon rewards publishing frequency), not standalone earners.

---

## §2 — Audible / ACX (audiobook)

**Winning length:** **5–7 finished hours for self-help** (≈ **45,000–63,000 words** @150 WPM). Bestseller medians cluster here (Atomic Habits 5h35m; The Power of Now 7h37m). **CDIS "5–7hr" VALIDATED · "3hr monetization threshold" VALIDATED** (it's the real go/no-go) · **"Audible curates 'under 3hr' collections" CORRECTED** → no official short collection; shorts are *culturally disadvantaged* by the credit economics (third-party "don't-cost-a-credit" lists exist precisely because shorts are the exception).

**Thresholds:** no published hard minimum to distribute (only ≤120 min/chapter) — but **commercial floor ~3 hr (~27k words)**; sweet spot 5–7 hr (45–63k words); self-help practical max ~8 hr (~72k). 15-min `hard_min` in our config is a *technical* floor only, far below sellable.

**Why length wins:** ACX à-la-carte list price is **tiered by finished hours** — `<1h $6.95 | 1–3h $14.95 | 3–5h $19.95 | 5–10h $24.95 | 10–20h $29.95`. Length sets your price tier → your per-sale royalty **and** your weight in the **new consumption-based pool** (effective **May 26 2026**: exclusive **50%** / non-exclusive **30%**, "Member Value" split weighted by à-la-carte price × engagement/completion). **A 33-min render lands in the bottom $6.95 tier: lowest royalty, smallest pool weight, and a "not worth a credit" buyer reaction — a structural loser on both the old and new models.**

- [A1] *Audible's new royalty model* — ACX (official) — https://www.acx.com/mp/blog/audible-new-royalty-model — accessed 2026-06-13 — **HIGH** (50%/30%, consumption pool weighted by à-la-carte price, eff. 2026-05-26)
- [A2] *Choose a distribution option* — ACX Help (official) — https://help.acx.com/s/article/choose-a-distribution-option — accessed 2026-06-13 — **HIGH** (40/50% excl. vs 25/30% non-excl.; no minimum-runtime rule)
- [A3] *Audible's royalty changes explained* — Kindlepreneur — https://kindlepreneur.com/audible-royalty-changes/ — accessed 2026-06-13 — **HIGH** (engagement/consumption now drives payout; no transparent formula published)
- [A4] *Average length & pricing of audiobooks in 2025* — Rich Pav — https://blog.richpav.com/average-length-and-pricing-of-audiobooks-in-2025/ — 2025 — **MED** (most-completed ≈ 6–7h; how-to nonfiction 3–6h; catalog mean ~10–12h)
- [A5] *Audiobook pricing / finished-hour tiers* — Scribe Media + ACX pricing summaries — https://scribemedia.com/blog/audiobook-pricing — accessed 2026-06-13 — **MED-HIGH** (6-tier finished-hour ladder; ~9,300 finished words/hr ≈ 155 WPM)
- [A6] *How audiobook authors are paid by Audible-ACX* — Alliance of Independent Authors — https://selfpublishingadvice.org/how-audiobook-authors-are-paid-by-audible-acx/ — accessed 2026-06-13 — **MED-HIGH** (short-title penalty: ~$1.45/credit on a 3h title)
- [A7] *ACX audio submission requirements* — ACX Help (official) — https://help.acx.com/s/article/what-are-the-acx-audio-submission-requirements — accessed 2026-06-13 — **HIGH** (only hard length rule = chapter ≤120 min)
- [A8] *Findaway returns as INaudio; Spotify split* — Jane Friedman — https://janefriedman.com/what-authors-need-to-know-about-the-return-of-findaway-as-inaudio/ — accessed 2026-06-13 — **MED** (Aug 2025 Findaway→INaudio + Spotify for Authors; Spotify uses hours-of-access, less short-punishing)

**Strategic surprise:** the model **flipped to consumption-based** (live for new titles 2026-05-26; legacy per-credit retires end-2026). Earnings now ride on **completed hours**, weighted by the length-tiered price — rewarding a **tight, fully-finished 5–7 hr** book over both a bloated 12h (low completion) and a thin 33-min (negligible weight). Sweet-spot discipline is now a royalty lever, not just marketing. **Do not route sub-3hr content to Audible as a standalone paid title.**

---

## §3 — Apple Books + Google Play Books (ebook + audiobook)

**Winning length:** length is **not a payout lever** on either — both are flat per-sale (Apple 70% all prices; Google 70% ebook in 60+ countries / 52% auto-narrated audiobook). No subscription read-through. Length = **price justification + (Google) preview-tier** only. **CDIS treatment VALIDATED** as secondary platforms.

**The real gates are LANGUAGE + GENRE, not length:**
- **Apple Digital Narration** (free AI audiobook from your EPUB): **ENGLISH ONLY**, genre-gated (self-development **eligible**), 1–2 mo QC. No length min/max.
- **Google auto-narrated audiobooks**: 52% share, free beta, input languages **EN / ES / FR / DE / HI / pt-BR only**, <2 hr to produce, preview tier scales with runtime. Non-fiction/low-dialogue = stated best fit (favorable for self-help).
- **CJK wall:** Apple Books storefront in Asia ≈ **Japan only** (no KR/zh); Google reaches **JP/KR/HK/TW ebooks**. **Neither AI-narrates Japanese/Korean/Chinese** → CJK audiobooks remain human/other-pipeline (matches repo memory "CJK is voice/infra-gated").

- [P1] *Get started with digital narration* — Apple Books for Authors (official) — https://authors.apple.com/support/4973-get-started-digital-narration — accessed 2026-06-13 — **HIGH** (English-only; genre gates; 1–2 mo QC)
- [P2] *Auto-narrated audiobooks program policies* — Google Play Books Partner Center (official) — https://support.google.com/books/partner/answer/10013009 — accessed 2026-06-13 — **HIGH** (6 input languages; preview tiers; free beta)
- [P3] *Auto-narrated audiobooks (program page)* — Google Play Books — https://play.google.com/books/publish/autonarrated/ — accessed 2026-06-13 — **HIGH** (52% share; 50+ voices; <2h)
- [P4] *Revenue Split FAQs* — Google Play Books Partner Center (official) — https://support.google.com/books/partner/answer/9331459 — accessed 2026-06-13 — **HIGH** (70% in 60+ countries, flat, price-band removed)
- [P5] *How to self-publish on Apple Books* — Written Word Media — https://www.writtenwordmedia.com/how-to-self-publish-on-apple-books/ — **MED** (flat 70% all price points; editorial merchandising vs algorithm)
- [P6] *AI-narrated audiobooks on Big-5 retailers* — PublishDrive — https://publishdrive.com/ai-narrated-audiobooks-retailers.html — 2024-02-02 — **MED** (Apple English-only + genre gates + 1–2 mo review)
- [P7] *Supported countries for selling books on Google Play* — Google (official) — https://support.google.com/books/partner/table/6052428 — accessed 2026-06-13 — **MED-HIGH** (~75 countries incl. JP/KR/HK/TW)
- [P8] *Global book distributors (Apple ≈ Japan-only in Asia)* — ALLi Self-Publishing Advice — https://selfpublishingadvice.org/international-insights-global-book-distributors-apple-google-play-and-nook/ — accessed 2026-06-13 — **MED**

**Strategic surprise:** the **English** self-help catalog gets a **near-zero-cost audiobook expansion** via both Apple + Google free AI-narration — length-agnostic, genre-eligible. CJK is the hard wall on the audio side. Google's wholesale discounting can trip price-matching against KDP/Audible list prices (pricing-governance gotcha).

---

## §4 — Spotify (audiobook + podcast)

**Audiobook winning length:** **5–7 hr core; bias the LOWER end 4–6 hr (≈36–54k words)** for Spotify specifically (casual, 52% aged 18–34). **CDIS audiobook "5–7hr" VALIDATED · podcast "20–30min" CORRECTED → 20–40 min (target 25–35) · `monetization_threshold 1200s` MISLABELED** (Spotify publishes no audiobook consumption gate — keep 1200s as an internal *podcast*-completion floor only).

**The 15-hr/month dynamic (the sleeper rule):** Spotify Premium includes ~15 hr/mo audiobook listening **counted at normal-speed runtime** (speed-listening does NOT reclaim hours). A 6-hr book "spends" ~40% of the monthly allowance → suppresses trial; a 4–5 hr book lets a subscriber slot 3 books/month → **shorter = more tryable.** Premium payout is **pro-rata on hours streamed** → **completion drives realized revenue, not nominal length.**

**Podcast:** completion is high & roughly flat **~10 → ~45 min**, drops past ~50 min. Sweet spot **20–40 min (target 25–35).** **Cadence is a separate, quantified lever** (~15-day release cycle ≈ +5 chart positions). Wellness podcasts are **bimodal**: guided-practice 3–12 min vs talk/teaching 30–45 min — segment the format before setting length.

- [S1] *Audiobooks in Premium plans* — Spotify Support (official) — https://support.spotify.com/us/article/audiobooks-premium-plans/ — accessed 2026-06-13 — **HIGH** (15 hr/mo, normal-speed counting)
- [S2] *Audiobooks+ brings more flexibility* — Spotify Newsroom (official) — https://newsroom.spotify.com/2025-07-16/audiobooks-brings-more-choice-and-flexibility-to-spotify-premium-subscribers/ — 2025-07-16 — **HIGH** (+15 hr add-on; +10 hr top-up)
- [S3] *Two years of audiobooks in Premium* — Spotify Newsroom (official) — https://newsroom.spotify.com/2025-10-15/audiobooks-in-premium-two-year-anniversary/ — 2025-10-15 — **HIGH** (52% aged 18–34; Audiobooks+ +18% in 30 days)
- [S4] *Spotify for audiobooks: indie author guide* — ScribeCount — https://scribecount.com/author-resource/audiobook-creation-guide/spotify-audiobooks-guide — updated 2026-03-10 — **MED-HIGH** (à-la-carte ~45–50% net; Premium pro-rata engagement; Findaway→INaudio Aug 2025)
- [S5] *Royalty payments in Spotify for Authors* — Spotify Support (official) — https://support.spotify.com/us/authors/article/royalty-reports/ — accessed 2026-06-13 — **HIGH** (two-stream model; no per-hour rate / consumption-% threshold disclosed)
- [S6] *How long should an audiobook be? (genre guide)* — Coharmonify — https://coharmonify.com/resource-articles/how-long-should-an-audiobook-be-genre-by-genre-guide/ — accessed 2026-06-13 — **MED** (self-help 4–8h / 37–75k words; "90%-completion short beats 40%-completion long")
- [S7] *Podcast statistics — episode-length distribution* — Buzzsprout — https://www.buzzsprout.com/blog/podcast-statistics — 2025–26 — **HIGH** (avg ≈37 min; 20–40 min = 32% of episodes, largest bucket; 80% finish all/most)
- [S8] *Podcast statistics (length/completion)* — Sci-Tech Today / Backlinko-sourced — https://www.sci-tech-today.com/stats/podcast-statistics/ — 2025 — **MED** (20–40 min most popular; ~70% finished of a 30–40 min episode)
- [S9] *Spotify podcast charts: boost ranking 2026* — Ausha — https://www.ausha.co/blog/spotify-podcast-charts-ranking/ — 2026 — **MED** (~15-day cycle ≈ +5 positions; momentum > volume)
- [S10] *Audiobook consumption / completion data* — Public Books — https://www.publicbooks.org/audiobooks-consumption-data/ — accessed 2026-06-13 — **MED** (abandonment clusters at 20–40% progress; >10h drop-off)

**Strategic surprise:** **Findaway Voices ceased 2025-08-01** → non-Spotify distro is now "INaudio"; the direct path is "Spotify for Authors." Our `platform_knob_tuning.yaml` `findaway` profile note ("Serves Apple, Kobo, Spotify, libraries") is **STALE.**

---

## §5 — YouTube (long-form teaching + Shorts + trailers)

**Winning length:** long-form educational/wellness **8–15 min** (retention-gated ≥50% AVD); **CDIS "10–20 min" CORRECTED → 10–15 min** (tighten the top). **Monetization 8-min threshold VALIDATED** (unchanged 2026; target 10–15 min so 1–2 mid-rolls land). **Shorts `hard_max 60s` CORRECTED → 180s** (3-min Shorts since 2024-10-15); 15–30s completion-optimal, 30–60s views-optimal. **Trailer 60–90s.** Hook window = first ~15 s (steepest drop sec 10–20).

**Algo length bias 2026:** neither pure length nor pure retention "king" — winning function = *(length that sustains ≥50% retention) × (satisfaction/return signals)*. 2025 added a satisfaction layer (surveys, returning-viewer rate, shares); raw watch-time-as-a-number is "dead." Shorts & long-form ranked by **separate systems**, but the recommender rewards channels doing **both** — synergistic with an Ahjan-update + trailer/Shorts plan.

- [Y1] *Manage mid-roll ad breaks in long videos* — YouTube Help (official) — https://support.google.com/youtube/answer/6175006 — accessed 2026-06 — **HIGH** (8-min minimum; auto-placement at natural breakpoints)
- [Y2] *Mid-roll ads updates explained* — YouTube Blog (official) — https://blog.youtube/creator-and-artist-stories/mid-roll-ads-updates-explained/ — 2025-03-24 — **HIGH** (~5% revenue lift; 8-min threshold unchanged)
- [Y3] *Understand three-minute YouTube Shorts* — YouTube Help (official) — https://support.google.com/youtube/answer/15424877 — 2024-10 — **HIGH** (3-min/180s Shorts max from 2024-10-15)
- [Y4] *We analyzed 1.3M YouTube videos* — Backlinko — https://backlinko.com/youtube-ranking-factors — **MED** (canonical "first-page avg 14:50"; DATED 2017, directional only)
- [Y5] *YouTube Shorts statistics 2026* — DemandSage — https://www.demandsage.com/youtube-shorts-statistics/ — 2026 — **MED-HIGH** (22× views @50–60s vs <10s; ~76% completion @50–60s)
- [Y6] *How the YouTube algorithm works in 2026* — SocialBee — https://socialbee.com/blog/youtube-algorithm/ — 2026 — **MED** (satisfaction-weighted discovery; separate Shorts/long-form ranking; returning-viewer value)
- [Y7] *First 30 seconds of YouTube videos (2026)* — PrePublish — https://prepublish.ai/guides/first-30-seconds — 2026 — **MED** (hook inflection ~sec 15; >65% early-hold ↔ +58% AVD)
- [Y8] *How long should your book trailer be* — ebookpbook — https://www.ebookpbook.com/2026/05/19/book-trailer-ideal-length/ — 2026-05-19 — **MED** (60–90s YouTube trailer; ~55% abandon at 60s)
- [Y9] *YouTube mid-roll ads 2025* — TubeBuddy — https://www.tubebuddy.com/blog/2025-youtube-monetization-rules-mid-roll-ads-update/ — 2025 — **MED** (8-min rule persistence; RPM framing)
- [Y10] *YouTube Partner Program requirements 2026* — vidIQ — https://vidiq.com/blog/post/youtube-partner-program-guide/ — 2026 — **MED** (YPP: 1k subs + 4k watch-hrs OR 1k subs + 10M Shorts views/90d)

**Strategic surprise:** for a teacher-led therapeutic brand, **returning-viewer rate (reportedly 5–10× new-viewer value)** may be the highest-leverage metric, not raw length. Our config's Shorts `hard_max 60s` is stale (3-min lane unused).

---

## §6 — WEBTOON / LINE Manga / Piccoma / Kakao / Naver / Lezhin (vertical-scroll comics)

**Winning length:** **there is no official panel-count rule** — every "20–30 / 40–70" number traces to one creator (S-Morishita Studio). WEBTOON enforces only **technical** caps (≤100 images, ≤20 MB, 800×1280px). Real Canvas average ~30–45 panels; **retention sweet spot ≈ 3,500–4,500px scroll (~8–12 min read).** **CDIS corrections:** Canvas 20–30 = creator heuristic not platform rule (real ~30–45); **Lezhin "70+ panels" → ~60-panel guidance + 4 episodes to submit + ≥30-episode plan** (24→~30); **iyashikei "55–65 panels" → ~40–55** (pacing carried by 600–1,000px scene gutters + 1,500–3,000px long-drops, not panel count); genre splits → S-Morishita averages (Comedy **30** not 12, Romance 40, Drama 50, Fantasy 50, Action 60, Thriller 60, Sci-fi 70); Bilibili 30–80 = **unsourced estimate.**

**JP platforms (the structural difference):** Japan reads page-based (tankōbon heritage) → **short ~10–20-page chapters, daily cadence**, NOT long Korean scroll episodes. **Piccoma "wait-until-free"**: 1 free chapter per title every **23 hrs**, **parallel per-title** (20 series = 20 free/day) → monetizes impatience on a hooked series → **chapter count + deep backlog is the revenue lever.** Piccoma = #1 grossing app in Japan 2023 & 2024. **Piccoma is closed to self-pub (licensed only); Japan self-publishing goes via LINE Manga Indies.**

**Cadence:** WEBTOON/Korea **weekly** (consistency ≈ 3× subscriber velocity vs irregular); JP coin-apps **daily/near-daily.** Predictable > burst. **Series:** launch with **3 episodes** (subscribe prompt at ep 3); **monetizes/binges at ~25–30 episodes** (Fast Pass needs a locked backlog; Lezhin ≥30-ep plan; Kakao 25-ch contract tranche — **VALIDATED in origin**). Ep 1 does ~70% of subscriber conversion.

- [W1] *How many panels does a webtoon have?* — S-Morishita Studio — https://www.s-morishitastudio.com/how-many-panels-does-a-webtoon-have/ — accessed 2026-06-13 — **HIGH** (genre panel averages; the 20–30 personal aim)
- [W2] *Webtoon update schedule: quality vs quantity* — S-Morishita Studio — https://www.s-morishitastudio.com/webtoon-update-schedule-quality-vs-quantity/ — accessed 2026-06-13 — **HIGH** (weekly-cadence reward)
- [W3] *Lezhin World Comic Contest / submission FAQ* — Lezhin (official) — https://social.lezhin.com/2018/12/17/the-4th-lezhin-comics-world-comic-contest-faq/ — accessed 2026-06-13 — **MED-HIGH** (~60-panel rule of thumb; 4 episodes to submit; ≥30-episode plan)
- [W4] *How to launch a new webtoon* — Webtoonish — https://www.webtoonish.com/p/how-to-launch-a-new-webtoon — accessed 2026-06-13 — **MED** (weekly default; launch-as-marketing)
- [W5] *WEBTOON got rid of Daily Pass* — KComicsBeat — https://kcomicsbeat.com/2025/05/29/no-youre-not-losing-it-webtoon-got-rid-of-daily-pass/ — 2025-05-29 — **HIGH** (Daily Pass discontinued mid-2025; Fast/Ad Pass remain)
- [W6] *Webtoon service ends Daily Pass* — Anime News Network — https://www.animenewsnetwork.com/news/2025-06-05/webtoon-service-ends-daily-pass-feature/.225053 — 2025-06-05 — **HIGH**
- [W7] *What makes Piccoma the most profitable manga app in Japan* — Good e-Reader — https://goodereader.com/blog/manga-and-anime-news/what-makes-piccoma-the-most-profitable-manga-app-in-japan — accessed 2026-06-13 — **MED-HIGH** (23-hr wait-until-free; ~10–20 pages/chapter)
- [W8] *Piccoma named Japan's top consumer-spending app for 2024* — Anime News Network — https://www.animenewsnetwork.com/news/2025-01-17/webtoon-platform-piccoma-named-japan-top-consumer-spending-app-for-2024/.220135 — 2025-01-17 — **HIGH**
- [W9] *Kakao contract updates to protect creators* — CBR — https://www.cbr.com/webtoon-korea-announces-contract-updates-protect-creators/ — accessed 2026-06-13 — **MED** (Kakao/Daum 25-chapter contract origin)
- [W10] *WEBTOON revolutionizes discovery + market size* — WEBTOON IR + Mordor Intelligence — https://ir.webtoon.com/news-releases/news-release-details/webtoon-entertainment-revolutionizes-webcomic-discovery · https://www.mordorintelligence.com/industry-reports/webtoons-market — 2025 — **MED** (binge-unlock for completed titles; 32% pay-to-advance miniseries)
- [W-INT] internal: `artifacts/research/webtoon_technical_reference_2026-04-25.md` (111-source compiled), `manga_vs_webtoon_economics_2026-04-25.md`, `manga_quality_bar/01_iyashikei_craft_study.md` — **HIGH** (technical caps, pacing px, JP-platform split)

**Strategic surprise:** for a **healing** publisher the dominant revenue lever is **chapter count + cadence, NOT panels-per-episode.** Maximizing iyashikei panels (the 55–65 target) optimizes the wrong axis — it inflates production cost without monetization upside. Win with a **deep backlog of shorter chapters on a steady rhythm**, re-chaptered shorter for Piccoma/LINE.

---

## §7 — CJK platforms (zh / ja / ko) — character-based, NOT word-based

> **Provisional flag (gate before ship):** of the three EN→char expansion ratios, **only ja = 2.15 is repo-measured** (4 real renders). **zh ≈ 1.6 and ko ≈ 2.0 have NO external confirmation** and must be measured against real zh/ko renders before any CJK platform duration ships (Pearl Star CosyVoice2 currently off). External localization literature even reports Chinese *display text* runs ~40% **shorter** than English — a different measurement (display columns vs literary chars-for-narration) but enough to mandate a native measurement.

**ZH audio** (Ximalaya 喜马拉雅, ~268–303M MAU, ~125 min/day): episodes avg **~15–20 min** (CDIS "10–30 min" VALIDATED). Narration **180–220 字/分** market-typical; our therapeutic **160–190 字/分 is a deliberate slow floor** (~5–20% under slow-normal → inflates zh runtime). **ZH ebook** (WeChat Read 微信读书, Dedao, Readmoo): self-help **10万–15万字** (focused, not web-novel bulk).

**JA audio** (Audible JP, audiobook.jp): self-help/実用書 **~4–6 hr** (skews shorter than the ~10h novel tier). Narration **300 文字/分 (Audible-confirmed — the single HARD CJK number)**; 600 文字/page → 6 hr ≈ 180pp (**validates tankōbon 180–220pp**). **JA ebook** (Kobo/Kindle JP): self-help **80,000–120,000 文字** (10万 center) → ~4.6–6.7 hr unabridged.

**KO is a TWO-MARKET split, not "Koreans want short":** **Millie's Library (밀리의 서재)** = AI-voiced **15–30 min summary** (요약본) — CDIS "summary preference" **VALIDATED**; **Welaaa (윌라, ~220k items Nov 2025)** = **full-length** pro-narrator (성우). Ship **BOTH** a summary edition AND a full edition per ko title. **KO ebook**: trade-book standard **20万자/~300pp**; focused self-help lighter ~120k–180k자 [inference]. **자/分 narration rate: no source found [verify].**

- [C1] *Ximalaya scale + episode-length avg* — 中新社 — https://www.sh.chinanews.com.cn/wenhua/2024-01-05/120401.shtml — 2024-01-05 — **MED**
- [C2] *Chinese narration speed bands (audiobook 180–200 字/分)* — Sohu/中影人 — https://www.sohu.com/a/531294102_121156125 — **HIGH**
- [C3] *Chinese paper-book length norms (8万–35万字; 15万 common)* — 知乎 — https://www.zhihu.com/question/292776060 — **HIGH**
- [C4] *WeChat Read 心理 category charts* — 微信读书 — https://weread.qq.com/web/category/800000 — 2025 — **HIGH** (scale), none (length)
- [C5] *Audible JP self-help (5h vs 10h+ tiers)* — unlimilab — https://unlimilab.com/audible-selfhelp-audiobook/ — 2024–25 — **MED**
- [C6] *audiobook.jp service spec (0.5–4× speed)* — audiobook.jp (official) — https://audiobook.jp/booklist/2556 — 2025 — **HIGH**
- [C7] *Ximalaya knowledge-payment / 碎片化 listening* — 人人都是产品经理 — https://www.woshipm.com/operate/6124337.html — 2024 — **MED**
- [C8] *Audiobook playtime ↔ book volume (300 文字/分; 600字/page)* — オーディオブック GUIDE — https://guideandreviews-library.com/playtime-physicalvolume/ — **HIGH**
- [C9] *NHK-standard speech rate (300; narrators 300–350 文字/分)* — 亀の知恵 — https://kamenochie.com/kikanunotane-time-wordcount/ — **HIGH**
- [C10] *Japanese business/self-help book length (~10万字)* — 日本橋出版 — https://nihonbashi-pub.co.jp/8338 — **HIGH**
- [C11] *Millie summary audiobook 30분 내외 / 15분 docent* — App Store/나무위키 — https://namu.wiki/w/밀리의%20서재 — 2025 — **HIGH**
- [C12] *2025 Korea audiobook ecosystem (Millie summary / Welaaa 완독)* — 반디뉴스 — https://www.bandinews.com/news/articleView.html?idxno=684 — 2025 — **HIGH**
- [C13] *Korean trade-book length (원고지 1,000매 → 20만자 → ~300pp)* — brunch — https://brunch.co.kr/@iiwoorii/34 — **HIGH**
- [C14] *Millie vs Ridi (RIDI Select targets 자기계발 light readers)* — appstory — https://news.appstory.co.kr/battle11389 — **MED**
- [C15] *Text expansion in translation (zh ~40% shorter in display space)* — Eriksen / W3C — https://eriksen.com/language/text-expansion/ — **HIGH** (display), LOW relevance to chars/word narration
- [C16] *China audio/video session-length tolerance (45.63% watch 30min–1hr)* — 网易 — https://www.163.com/dy/article/KCV5MGPU05389VEO.html — 2025 — **MED**

**Strategic surprises:** (1) **ja 300 文字/分 is the anchor** — build ja duration on it, back-derives the tankōbon page map. (2) **Korea = ship BOTH summary (Millie) + full (Welaaa).** (3) The **expansion-ratio trap**: googling "Chinese text expansion" returns the *opposite* of our 1.6 (display vs narration) — document it to pre-empt a false alarm; still MEASURE zh/ko before shipping. (4) zh calm rate runs slow — the "6hr→7.5hr in Chinese" repo multiplier is partly the slow 160–190 rate, not just expansion.

---

## Cross-platform universal signals (from `docs/PLATFORM_ALGORITHM_RESEARCH_2026.md`, validated)

| Signal | Target | Confirmed by |
|---|---|---|
| **Completion rate** | ≥70% | universal positive signal — Audible, Spotify, YouTube, WEBTOON all rank on it |
| **Self-help audiobook** | 5–7 hr (≥10h kills completion) | [A4][A5][S6] + CDIS §4.2 |
| **Chapter / episode** | 15–30 min audio · 8–12 min webtoon · 8–15 min YouTube | [A4][W7][Y6] |
| **Opening** | best material first (highest drop-off) | [A3][Y7] |
| **Cadence** | weekly (audiobook/webtoon-West) · daily (JP comics / micro-podcast) | [S9][W2][W8] |
| **Release window** | Q1 (Jan self-help peak); avoid Nov 15–Dec 31 | PLATFORM_ALGORITHM_RESEARCH_2026 |

**The through-line:** every read-through/consumption platform (KU, Audible-new, Spotify, YouTube) pays on **completed length**, not nominal length — so the winning move is the **longest length our content can fill while sustaining ≥70% completion**, never padding. That is exactly the content-length routing in `DURATION_PER_PLATFORM_PLAN.md` §5.
