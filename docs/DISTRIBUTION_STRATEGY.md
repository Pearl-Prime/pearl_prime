# Distribution Strategy — Illustrated Content Catalog
**Generated:** 2026-04-23  
**Authority:** Pearl_Research platform deep-dive (session `b70157a3`)  
**Scope:** All US/EN content — KDP, Google Play, Apple Books, WEBTOON, Tapas, Substack, GlobalComix  

---

## 1. The Short Answer

**Yes — KDP and Google Play both support comics/manga.** Every piece of content can go on 5–6 platforms simultaneously with zero exclusivity conflicts (as long as KDP Select is never enrolled). No platform has a public upload API — all require dashboard upload per title/episode. Automation can generate files and metadata; a human (or browser automation) does the final upload step.

---

## 2. Platform Matrix

| Platform | Accepts Comics? | Format | Upload Method | Bulk API? | Revenue Split | Exclusivity |
|---|---|---|---|---|---|---|
| **Amazon KDP** | ✅ Full support | Fixed-layout EPUB3 / KPF (via Kindle Create) | Dashboard per title | ❌ No | 35% (no delivery fee) or 70% − $0.15/MB | **Opt-in KDP Select only** — default NO |
| **KDP Print (POD)** | ✅ B&W + color | PDF, 300 DPI | Dashboard per title | ❌ No | List price − print cost | None |
| **Google Play Books** | ✅ EPUB + PDF | Fixed-layout EPUB3 or PDF | Partner Center dashboard; CSV for **metadata only** | ❌ Content = manual | **70%** (60+ countries) | None |
| **Apple Books** | ✅ Comics section | Fixed-layout EPUB3 | iTunes Connect direct (**aggregators can't handle fixed-layout**) | ❌ No | **70%** flat, no delivery fees | None |
| **WEBTOON Canvas** | ✅ Native format | PNG/JPG, 800px wide vertical scroll | Creator dashboard per episode | ❌ No | Ad share (after 40K views + 1K subs) | None |
| **Tapas** | ✅ | PNG/JPG, max 940px wide | Creator dashboard per episode | ❌ No | ~70% ad share (100 subs); 100% Support payments (250 subs) | None (free tier) |
| **Substack** | ✅ Images or CBZ | Inline images or CBZ file embed | Post editor per post | ❌ No | ~87% (after 10% Substack + ~3% Stripe) | None |
| **GlobalComix** | ✅ Comics-native | PDF, CBZ, EPUB | Creator dashboard | ❌ No | 65–75% subscription share; 92–95% donations | None |

---

## 3. How Many Channels Can 1 Piece of Content Reach?

**Answer: Up to 7 platforms simultaneously — zero exclusivity conflicts — if KDP Select is never used.**

### B&W Manga OGN (traditional page format)

| # | Platform | What to upload | Why |
|---|---|---|---|
| 1 | **KDP eBook** | Fixed-layout EPUB3 → KPF (via Kindle Create) | Largest EN Kindle audience; right-to-left + Guided View |
| 2 | **KDP Print** | B&W PDF 300 DPI | POD physical copies; $0.012/page — affordable |
| 3 | **Apple Books** | Same fixed-layout EPUB3 (direct iTunes Connect) | 70% flat royalty, no delivery fees, Comics section |
| 4 | **Google Play Books** | Same fixed-layout EPUB3 or PDF | 70% royalty, global Android reach |
| 5 | **GlobalComix** | PDF or CBZ | Comics-native discovery; print POD (Q4 2025 launch) |
| 6 | **Substack** | CBZ file embed + free chapter images | Audience building; ~87% on paid subscriptions |
| 7 | **KDP Japan marketplace** | Same KDP upload, set JPY pricing | Reach Japanese Kindle readers with EN content |

> **Skip WEBTOON Canvas** for traditional manga pages — format mismatch. Canvas is vertical scroll; manga is page-by-page. Reformatting required (see Section 6).

### Color Webcomic (vertical scroll / webtoon format)

| # | Platform | What to upload | Why |
|---|---|---|---|
| 1 | **WEBTOON Canvas** | PNG/JPG episodes, 800px wide | Native format; path to Originals contract |
| 2 | **Tapas** | Same PNG/JPG episodes | Second EN webcomic platform; 70% ad share |
| 3 | **Substack** | Episode images inline + CBZ downloadable | Paid subscription tier; Panels app integration |
| 4 | **KDP eBook** (collected volumes) | Fixed-layout EPUB3 of compiled volumes | Kindle visibility; 35% tier for color (large files) |
| 5 | **Apple Books** (collected volumes) | Same fixed-layout EPUB3 | 70% royalty |
| 6 | **Google Play Books** (collected volumes) | Same fixed-layout EPUB3 | 70% royalty |

### Doodle / Illustrated Prose

| # | Platform | What to upload | Why |
|---|---|---|---|
| 1 | **KDP eBook** | Fixed-layout EPUB3 | 70% tier likely works (text-heavy = smaller file = lower delivery fee) |
| 2 | **KDP Print** | Color PDF | Physical copies |
| 3 | **Apple Books** | Same EPUB3 | 70% flat |
| 4 | **Google Play Books** | Same EPUB3 | 70% |
| 5 | **Draft2Digital** | Reflowable EPUB (D2D can't do fixed layout) | Reaches Kobo, B&N, Scribd, libraries |
| 6 | **IngramSpark** | PDF | Global bookstore + library distribution |
| 7 | **Substack** | Chapter-by-chapter images | Audience building |

---

## 4. Revenue Optimization Rules

### KDP 35% vs 70% — The Math
The 70% tier has a **$0.15/MB delivery fee** that destroys royalties for large comics files.

```
70% tier: ($price × 0.70) − ($0.15 × file_size_MB)

Example: 50MB manga vol at $9.99
  = ($9.99 × 0.70) − ($0.15 × 50)
  = $6.99 − $7.50
  = −$0.51  ← NEGATIVE ROYALTY

Same book at 35% tier:
  = $9.99 × 0.35 = $3.50  ← Always positive
```

**Rule: Use 35% tier for any illustrated content over ~28MB at $9.99. Use 70% only for small illustrated prose files (<10MB).**

### Platform Revenue by Format (mid-tier title estimate)

| Platform + Format | Annual Revenue Range | Notes |
|---|---|---|
| KDP eBook (manga OGN, 35% tier, $9.99) | $3.50/sale | No floor; volume-dependent |
| KDP Print (B&W, $14.99 list, ~100pp) | ~$8/sale after print cost | Print cost ≈ $0.85 + $0.012×100 = $2.05 |
| Apple Books (70%, $9.99) | $6.99/sale | Best ebook royalty per sale |
| Google Play Books (70%, $9.99) | $6.99/sale | Same as Apple |
| WEBTOON Canvas (ad share) | $100–$2,000/mo | Requires 40K views + 1K subs to unlock |
| WEBTOON Canvas + Patreon | $2,000–$8,000/mo | At ~10K Patreon followers |
| Substack paid tier ($8/mo, 500 subs) | ~$4,200/mo | After Substack + Stripe cut |
| Tapas ad share | $500–$3,000/yr | Highly variable |
| GlobalComix | $500–$2,000/yr | Subscription share + donations |

---

## 5. US Catalog Format Allocation (Revenue-Optimized)

Based on market data + platform revenue models, revised % allocation per format:

| Format | % Allocation | Primary Revenue Channel | Distribution Stack |
|---|---|---|---|
| **YA/MG Print OGN** | **30%** | KDP Print + traditional publisher | KDP + Apple + Google Play + GlobalComix |
| **WEBTOON Canvas → Print** | **25%** | WEBTOON Originals contract + print deal | WEBTOON → Tapas → Substack → KDP (collected) |
| **Adult Graphic Memoir** | **15%** | Traditional publisher (Pantheon, First Second) + KDP | KDP + Apple + Google Play + IngramSpark |
| **Doodle/Humor Webcomic** | **15%** | Substack paid subs + Patreon + book collections | Substack → Patreon → KDP → D2D (library) |
| **Genre OGN (dark fantasy/horror)** | **10%** | Image/BOOM! + KDP + GlobalComix | Traditional pub → KDP → Apple → GlobalComix |
| **Illustrated Prose Hybrid** | **5%** | KDP + Apple + Substack (chapter serialization) | KDP → Apple → Google Play → D2D → IngramSpark |

---

## 6. Format Conversion Pipeline

Each piece of source content needs different format conversions per platform:

```
SOURCE MASTER (high-res layered files)
│
├── Fixed-Layout EPUB3 ──────────────────► Google Play Books (direct upload)
│         │                               ► Apple Books (iTunes Connect)
│         └── Kindle Create → .KPF ──────► KDP eBook
│
├── Print-Ready PDF (300 DPI, w/ bleed) ─► KDP Print
│                                         ► IngramSpark
│
├── Vertical-Scroll Strips (800px wide) ─► WEBTOON Canvas (per episode)
│         └── [requires reformat step]   ► Tapas (per episode, max 940px)
│
├── CBZ Bundle ──────────────────────────► Substack file embed
│                                         ► GlobalComix
│
└── Episode images (PNG) ────────────────► Substack inline post images
```

**The reformat step** (traditional manga page → WEBTOON vertical scroll) is not trivial — it requires re-compositing panels into a 800px-wide infinite-scroll strip. This is a separate production task, not just a file conversion.

---

## 7. Upload Workflow — No API Exists

**Critical operational fact: No platform has a public content upload API for indie creators.** All uploads are manual dashboard operations.

| What can be automated | What requires manual dashboard upload |
|---|---|
| File generation (EPUB3, KPF, CBZ, PDF) | KDP title upload and metadata entry |
| Metadata CSV for Google Play | Apple Books iTunes Connect upload |
| Episode image preparation (resize, compress) | WEBTOON Canvas episode upload |
| KDP royalty calculator (35% vs 70% decision) | Tapas episode upload |
| File naming and folder organization | Substack post creation |
| Checklist generation per platform | Google Play Books content upload (metadata CSV only) |

**Pipeline recommendation:** Build an automated step that:
1. Generates all required format variants from master source
2. Outputs a per-platform upload checklist with file paths and metadata
3. Routes to browser automation (Playwright/Puppeteer) for dashboard uploads, or flags for human upload

---

## 8. Aggregator Decision Tree

```
Is it a fixed-layout comic/manga?
│
├── YES → Do NOT use Draft2Digital or most aggregators (strips formatting)
│         Use direct upload: KDP (KPF) + Apple (iTunes Connect) + Google Play (Partner Center)
│         Consider: PublishDrive (best fixed-layout support among aggregators)
│         For print: IngramSpark or KDP Print
│
└── NO (illustrated prose, reflowable) 
          → Use Draft2Digital for reach (Kobo, B&N, Scribd, libraries)
          → Use IngramSpark for bookstore + library physical
          → Still upload KDP and Apple directly (aggregators take commission)
```

---

## 9. GlobalComix — Why It Matters

GlobalComix is the only comics-native non-exclusive platform that:
- Accepts page-format manga AND webtoon-format comics
- Has a subscription (Gold) model with consumption-based creator share
- Launched print-on-demand (Q4 2025 wide rollout)
- DC Comics partnership (September 2025) — signals platform legitimacy growth
- Non-exclusive — add all catalog titles here as a discovery layer

**Revenue model:** Creator share = proportion of Gold subscriber reading time on your titles × monthly subscription pool. Functions like Spotify but for comics. Suitable as supplemental channel, not primary.

---

## 10. KDP Select — Never Enroll

**KDP Select requires digital exclusivity for 90-day renewable periods.** Enrolling in KDP Select means no Apple Books, no Google Play, no GlobalComix, no Substack (for that content). The only benefit is Kindle Unlimited inclusion and promotional tools.

**For a multi-platform catalog: KDP Select is always wrong.** The combined revenue from Apple (70%) + Google Play (70%) + GlobalComix exceeds any Kindle Unlimited page-read income for illustrated content (KU pays ~$0.005 per page read — a 200-page manga earns ~$1 total per KU read vs $6.99 from an Apple Books sale).

**Pipeline rule: KDP Select enrollment = never. Hardcode OFF in any upload automation.**

---

## 11. Japan-Specific Distribution

For JP-locale content (LINE Manga, ComicWalker):
- **LINE Manga:** No open indie submission portal. Requires Japanese publisher relationship or direct partner agreement. Not accessible independently.
- **ComicWalker Global:** English support "coming soon" as of April 2026. No open indie portal yet.
- **Kindle Japan:** Same KDP upload — set JPY pricing in the KDP dashboard. EN-language manga reaches Japanese Kindle readers through the same upload workflow. This is the only accessible JP digital channel for independent creators currently.
- **Pixiv Global Comic Awards:** Contest-based annual path. Winners connect with 20 international publishers. Use as a visibility play, not distribution.

---

## 12. Platform Launch Sequence (New Series)

**For a WEBTOON-first series (webcomic-to-print pipeline):**
1. Launch on WEBTOON Canvas (episodes 1–10 free)
2. Add Tapas simultaneously (same episodes, non-exclusive)
3. Open Substack at episode 5 — free public episodes + paid "early access" tier
4. Hit 40K views + 1K subs → Canvas ad share unlocks
5. At 100K+ subscribers → pitch WEBTOON Originals or approach print publishers
6. Kickstarter for Vol 1 collected print edition (3,413 comics projects in 2024; 77.8% success rate)
7. KDP Print + eBook for Vol 1 (compiled fixed-layout EPUB)
8. Apple Books + Google Play Books with same EPUB

**For a print-first series (OGN/manga digest):**
1. KDP eBook (35% tier) + KDP Print simultaneously at launch
2. Apple Books (direct iTunes Connect) same day
3. Google Play Books (Partner Center — apply early, takes time)
4. GlobalComix PDF for comics-native discovery
5. Substack — free chapter + paid subscription for early/bonus content
6. IngramSpark for bookstore + library distribution (B&N shelf placement target)

---

## 13. Open Questions for Pipeline Design

- [ ] Apply for Google Play Books Partner Center access (not instant approval)
- [ ] Set up iTunes Connect for Apple Books (requires Apple developer account)
- [ ] Decision: Use PublishDrive as aggregator for fixed-layout reach to secondary markets, or direct-only?
- [ ] Build KDP royalty calculator (file size input → 35% vs 70% recommendation)
- [ ] Determine WEBTOON reformat workflow — which series get vertical-scroll versions?
- [ ] Confirm GlobalComix creator account setup
- [ ] Browser automation scope: which dashboard upload steps can be automated vs manual?
