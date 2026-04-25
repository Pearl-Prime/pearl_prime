# WEBTOON Master Reference — Phoenix Omega Production Bible

**Date:** 2026-04-25
**Researcher:** Pearl_Research (4 parallel agents — technical, Japan-market via Rakuten AI, compositing/lettering, therapeutic-scroll craft)
**Status:** Decision-grade reference. Companion to PR #626 (manga-vs-webtoon production weight).
**Scope:** Everything Phoenix Omega needs to know to do WEBTOON right — technically, creatively, and therapeutically.

---

## How to use this document

This is the navigation + synthesis layer. **Detail lives in four companion docs**, all dated 2026-04-25:

| Companion | Topic | Words | Citations |
|-----------|-------|------:|----------:|
| [webtoon_technical_reference_2026-04-25.md](webtoon_technical_reference_2026-04-25.md) | WEBTOON Canvas + Originals technical specs (image dims, file caps, upload, AI policy, monetization, contracts) | 8,280 | 111 |
| [webtoon_japan_market_rakuten_ai_2026-04-25.md](webtoon_japan_market_rakuten_ai_2026-04-25.md) | Japan-market intel — LINE Manga / Piccoma / JUMP TOON / Comic C'moA specs, AI regulation, bestseller patterns | (Q&A) | Native Japanese sources |
| [webtoon_compositing_lettering_2026-04-25.md](webtoon_compositing_lettering_2026-04-25.md) | Layered compositing, word bubbles, lettering, multi-language text overlay engineering | 6,675 | 95 |
| [webtoon_therapeutic_scroll_craft_2026-04-25.md](webtoon_therapeutic_scroll_craft_2026-04-25.md) | Scroll-as-therapeutic-medium — iyashikei codified, Polyvagal/Somatic Experiencing/Positive Psych applied, 50-card Craft Formula Library | 10,571 | 100 |

This master synthesizes the highest-leverage cross-cutting findings — the things that span more than one companion. **Read this doc first; dive into companions for depth.**

---

## ⚡ Executive Summary — 5 Things You Need to Know

### 1. There is no single "WEBTOON" — there are three platforms

WEBTOON Entertainment's unified CANVAS supports **only 7 languages: English, Spanish, French, Indonesian, Thai, Traditional Chinese, German**. **Japanese is NOT included** (LINE Manga / Piccoma / JUMP TOON / Comic C'moA territory). **Korean is NOT in the unified CANVAS either** (Naver Webtoon Korea is a separate creator pipeline). zh_CN sits outside WEBTOON Entertainment's reach entirely — Bilibili Comics / Kuaikan / Tencent Comics, partner-only.

**Phoenix needs THREE separate connectors**, not one:
- **Connector A — WEBTOON unified CANVAS** → en_US + zh_TW (+ optional es, fr, id, th, de)
- **Connector B — LINE Manga Indies** → ja_JP (publishes hard specs)
- **Connector C — Naver Webtoon Korea** → ko_KR (separate Korean creator portal)

Plus future partner-required paths: Piccoma (post-pitch), Bilibili Comics (Chinese MCN required).

### 2. The technical specs are stable — and 800×1280 JPEG is the contract

| | WEBTOON unified CANVAS | LINE Manga Indies (ja_JP) | Piccoma (ja_JP) |
|---|---|---|---|
| **Width** | **800 px** (max & target) | **800 px standard** (min 400, max 10000) | **NOT PUBLIC** — assume LINE-compatible |
| **Per-image height** | **≤ 1280 px** (auto-sliced if taller) | **≤ 10000 px** | NOT PUBLIC |
| **Per-image file size** | **≤ 2 MB** | **≤ 2 MB** | NOT PUBLIC |
| **Episode total** | **≤ 20 MB or 100 images** | **≤ 1000 images per episode** | NOT PUBLIC |
| **Format** | **JPEG official, PNG accepted** | PNG / JPG | NOT PUBLIC |
| **Color** | sRGB assumed (no formal spec) | RGB recommended | NOT PUBLIC |
| **DPI** | 72 dpi upload | ≥ 72 dpi | NOT PUBLIC |
| **Upload** | **No public REST API — Chrome dashboard only** | Web dashboard | Pitch first, specs after |

**Phoenix render config (unified):** master at **1600×2560 per panel, downsample to 800×1280 sliced JPEG quality 92 sRGB**, pre-slice client-side between panels (never through panel content).

### 3. There is no public WEBTOON upload API — and that's a major engineering risk

WEBTOON Canvas accepts uploads only through the Chrome-based creator dashboard. **No documented REST endpoint exists.** The only feasible automation path is **headless Playwright/Chrome scripted against the dashboard UI** — TOS-grey, breakage-prone with any UI revision, and probably accelerated-rate-limited. Plan for:
- Manual fallback dashboards
- Per-account upload session management
- UI-change alerting (DOM diff detection)
- Conservative throttling (1 episode / N minutes / account)

LINE Manga Indies and Naver Webtoon Korea have similar constraints — none publish a public API. This is the #1 risk in the entire program.

### 4. Phoenix's compositing model is structurally a 10× advantage — for webtoon. Less so for B&W page manga.

The user's question — "is this different from manga plans?" — has a sharp answer: **layered compositing (background + character + object + word bubble) maps almost 1:1 onto vertical webtoon production and fights traditional B&W page manga in nearly every dimension.** The compositing doc enumerates this across BG, character, dialog, SFX, bubble, narration, gutter, panel border, color, resolution, locale-resize, RTL, vertical CJK, furigana — vertical webtoon wins on every row.

The headline implication: **make webtoon the master format. Treat B&W page manga as a downstream "flatten + screentone" export from the same layered source.** Per the prior PR #626 production weight (58% color vertical webtoon / 24% B&W page / 14% color page / 4% direct self-help illustrated), this also re-frames how the 24% B&W lane gets produced — *not* as a parallel pipeline but as a derivative export.

### 5. The scroll itself can be the therapeutic intervention

The strongest creative finding: **Phoenix should not make manga *about* wellness; it should make manga whose form (scroll cadence, panel weight, breath, silence) regulates the reader's nervous system in real time.** Teachings ride a regulating vehicle. Convergent evidence from polyvagal theory (Porges 2022), somatic experiencing (Levine 1997, 2010), broaden-and-build positive emotion (Fredrickson), awe-as-vagal-tone (Monroy & Keltner 2023), iyashikei craft (Frieren, Yokohama Kaidashi Kikō, Mushishi), and webtoon scroll-pacing research (S-Morishita, Lore Olympus) all point the same direction.

The companion doc supplies a 50-card Craft Formula Library, a per-teacher signature table (12 teachers × anchor + color + pacing + light cue), and a 5-item Scroll Therapeutic Test that should become a CI/QA gate before episodes ship.

---

## 6 Cross-Cutting Decisions Phoenix Should Make Now

The four companions each have their own action items; here are the six that span all of them and need owner sign-off before engineering starts.

### Decision 1 — Schema v3.0.0 with `text_by_locale` per dialogue line

**Why now:** Phoenix's current `lettering_spec.schema.json` v2 bakes text into render at production time. Re-rendering art for a second language costs roughly the same as the original render. With `text_by_locale: {en: "...", ja: "...", zh-TW: "...", zh-CN: "...", ko: "..."}` carried as a swappable manifest — and bubbles rendered at composite-time, not render-time — Phoenix gets **50–99× cost reduction across 5 markets** vs re-render.

**Specs (compositing doc §1, §8):**
- Per-locale text dict on every `dialogue_lines[]` entry
- Per-locale `sfx[]` (Japanese onomatopoeia stay in original or get translated per locale rule)
- Per-locale font override (Source Han Sans JP for ja_JP; Source Han Sans TC for zh_TW; Source Han Sans SC for zh_CN; Source Han Sans KR for ko_KR; primary Latin font for en_US)
- Validator rule: every series ships with at least the `default_locale` populated; missing-locale fallback rule explicit

### Decision 2 — Render at 2× supersample as the master, downsample for delivery

**Why:** Tablet/desktop readers see WEBTOON's 800-px image upscaled 1.5–2× to fill column. A native-800 render looks mushy on iPad. **Render master at 1600×2560 per panel** (compositing doc §12; technical doc §2.4), downsample with high-quality Lanczos to 800×1280 JPEG q92 sRGB for upload. This single decision unlocks tablet/desktop reading quality without changing the upload contract.

This also gives Phoenix a free print-ready master: at 1600 px wide, KDP collected volumes can output 6 in (15 cm) wide at ~270 dpi without further upscaling.

### Decision 3 — FONT_REGISTRY rebuild (CJK-first)

**Current state (compositing doc §1.5):** `fonts/manga/FONT_REGISTRY.yaml` lists 4 fonts, all status `pending`. Only `noto_sans_jp_body` covers any CJK. **Production-blocking gap.**

**Add (all OFL or compatibly licensed):**
- **Source Han Sans JP** (Adobe + Google) — Japanese body
- **Source Han Sans TC** — Traditional Chinese body
- **Source Han Sans SC** — Simplified Chinese body
- **Source Han Sans KR** — Korean body
- **Klee One** — Japanese display/cursive (handwritten feel)
- **LxgwWenKai** — Chinese Klee derivative
- **Anime Ace** — Latin dialogue font (free for personal/commercial)
- **Badaboom** — Latin SFX font (free)
- **Comic Mono / Comicraft alternatives** — backup Latin dialogue

CJK kerning quality requires HarfBuzz / Cairo (Pillow's drawing layer cannot do optical kerning per the compositing doc). Plan to migrate the bubble renderer's text-layout call to Skia or PangoCairo. This is the second-biggest engineering item after the upload connector.

### Decision 4 — SVG vector bubble masters in `/assets/manga/bubble_shapes/`

Phoenix's current bubble rendering uses **hard-coded Pillow polygons** which blur on any rescale. Replace with **SVG vector masters** composited via `cairosvg` + Pillow. Build 11 canonical shapes (compositing doc §2.1):

```
round_normal, spiky_emphasis, cloud_thought, square_narration,
whisper_dashed, scream_ultra, electronic_sharp, drip_horror,
shojo_soft, wavy_supernatural (NEW), off_panel (NEW), singing (NEW)
```

Per-character bubble register (Sandman/Klein pattern) — each teacher gets a signature bubble style. E.g., `joshin` (Zen) = `round_normal` + soft drop shadow + zero border at low intensity, hardens at high intensity. Document this in a new `series_lettering_register.yaml` per series.

### Decision 5 — Vertical-strip composer (NEW), retire horizontal `page_compose.py` for webtoon path

Current `phoenix_v4/manga/chapter/page_compose.py` produces **horizontal page strips left-to-right** — that's the page-manga path. Webtoon needs a **vertical concat composer** that:
1. Takes per-panel rendered PNG/JPEG inputs
2. Stacks them vertically with beat-type-aware gutter heights (technical doc §2.1):

| Beat type | Gutter px |
|-----------|----------:|
| `micro` (within scene) | 30–50 |
| `standard` (scene transition) | 600–1000 |
| `spatial` (same scene, different angle) | 200 |
| `long_drop` (Phoenix's named therapeutic technique) | 1500–3000 |
| `miyazaki_ma` (once-per-arc) | 2400–3200 |

3. Slices the resulting tall image into ≤1280 px tall JPEG segments at gutter midpoints — **never through panel content**
4. Outputs a numbered episode payload conforming to WEBTOON Canvas's 100-image / 20MB cap

The page-manga path keeps `page_compose.py` (horizontal strip + screentone export). Both consume the same source layers.

### Decision 6 — Adopt the Scroll Therapeutic Test as a ship gate

From therapeutic-craft doc §18. Every episode must pass **before publish**:

1. **Safety cue inside the first 800 px** (soft eye contact, open hands, ground-on-earth, warm palette — at least one)
2. **At least 3 oscillations between activation and ground** (Pendulation Pair structure, Somatic Experiencing principle)
3. **Activation:Ground vertical-pixel ratio ≤ 1:2.5** (titration — for every 1000 px of mobilizing content, 2500+ px of grounding)
4. **Closes with completion** (sigh, settle, integration — never tension-spike cliffhanger)
5. **HRV-style end-state delta** (testable proxy: average reader's last-30-second arousal lower than first-30-second; pilot with Welltory / EliteHRV apps before greenlight)

Items 1-4 can be enforced by static analysis on the lettering spec + composer manifest. Item 5 requires reader piloting and a measurement protocol; treat as Phase 2 gate.

---

## Per-Market Production Playbook (synthesis across all 4 companions)

### en_US — Phoenix's primary lane (60% of catalog production)

**Format:** Color vertical webtoon. Master at 1600×2560/panel; deliver at 800×1280 JPEG q92 sRGB to WEBTOON unified CANVAS.

**Platforms:**
1. **WEBTOON Canvas** (primary serialization) — 170M MAU; 7-language unified; AI-tolerant with Korea Basic Act 1-year grace through Jan 2027; AI Translation Beta available (≥10 episodes + >2,000 PV/365d to opt in)
2. **Amazon KDP Comics & GN** (collected volumes; AI disclosure required) — 70% royalty $2.99–9.99 + KU page reads
3. **GlobalComix** (secondary) — Kodansha distribution deal 2025

**Stay Canvas-tier, NOT Originals**, until catalog has revenue base. Originals contracts demand 3-year post-completion digital exclusivity, multimedia option, exclusive merchandising license — too costly for unproven IP. Comicsbeat's April 2024 Originals contract criticism analysis confirms creators reading these contracts as "predatory."

**Therapeutic spec:** Apply the 5-item Scroll Therapeutic Test on every episode. Use the 50-card Craft Formula Library, especially: **The Long Drop, Anchor Panel, Breath Bracket, Awe-Pullback, Pendulation Pair, Tea Beat, Dappled Light Hand**.

### ja_JP — dual-format per series (40% color vertical / 45% B&W page / 13% color page / 2% direct self-help)

**Why dual-format here only:** Japan is the ONLY market where both Oricon B&W bestsellers (ONE PIECE 1.55M, Frieren 4.99M in 2024 ranking year) AND Piccoma SMARTOON ($400M+ 2024) compete head-to-head. Every other market is single-format dominant.

**Color vertical path:**
- Render same 1600×2560 master as en_US
- Deliver to **LINE Manga Indies** at 800 px wide / 10000 px max tall PNG or JPG, ≤ 2MB per image, ≤ 1000 images per episode (Rakuten AI confirmed via manga.line.me)
- Submit Japanese-localized text via the v3 schema's `ja` locale field
- For Piccoma: **NOT publicly specced** — pitch via `持ち込み` submission, get specs after acceptance (Rakuten AI emphatic on this)

**B&W page path:**
- Same source layers, B&W-conversion pass + screentone overlay
- Right-to-left page flow (`page_compose.py` already produces horizontal strips — needs RTL-aware ordering)
- 128×182 mm tankōbon trim equivalent for KDP Japan + Comic C'moA upload
- Comic C'moA already accepted AI manga at #1 (Jan 2026 — *My Dear Wife…*) — most AI-tolerant Japanese platform

**JUMP TOON note:** Shueisha's vertical-color platform launched 29 May 2024 with *ONE PIECE* editor Takanori Asada at the helm. **Do not target — Shueisha disqualified AI manga from Jump Rookie Feb 2026.** Same hostility applies to JUMP TOON.

**Japan AI regulation:** Article 30-4 permits AI training; AI-generated content not separately regulated; **no disclosure obligation in Japan** (vs. Korea's AI Basic Act, 1-year grace through Jan 2027). Phoenix can ship AI-assisted ja_JP content cleanly.

### ko_KR — webtoon-native, Naver Korean platform (85% color vertical)

**Naver Webtoon Korea is NOT the same backend as WEBTOON unified CANVAS** (en/es/fr/id/th/zh-TW/de). It's a separate creator portal with separate submission. WEBTOON's AI Translation Beta does not include Korean (translates *out of* Korean for English readers, not into).

**Korea AI Basic Act (effective 22 Jan 2026):**
- 1-year grace through Jan 2027
- Obligations sit on **platforms, not individual creators**
- Webtoons satisfy disclosure with **machine-readable, non-visible watermarks** (no visible logo required)
- Less burdensome than initially scoped — ship-blocking only if Naver Webtoon's platform-side enforcement gets aggressive after grace ends

**Tapas:** AI BANNED since 23 Jan 2023. Zero path. Don't budget production cycles.

**Therapeutic angle:** 힐링 (healing) is an established Naver/Kakao genre tag. Apply the same Scroll Therapeutic Test + Craft Formula Library; tune palette per Korean cultural context (less wabi-sabi, more bright contemplative — 자기계발 / self-development category aesthetic).

### zh_TW — color vertical via WEBTOON unified CANVAS (zh-TW IS supported)

**This is the easy market.** WEBTOON unified CANVAS includes Traditional Chinese as one of its 7 languages — Phoenix gets zh_TW distribution for free if the v3 schema's locale dict has `zh-TW` populated.

Tong Li / BookWalker / LINE Manga TW are alternative paths; LINE Manga TW carries vertical webtoon. Cultural proximity to Japan means iyashikei recognition is immediate.

### zh_CN — partner-required, contingent

Bilibili Comics / Kuaikan Manhua / Tencent Comics are **all gated by Chinese MCN/entity partnership**. No self-pub path. Cultivation/xianxia genre dominant. Regulatory caution on health/wellness claims. Phoenix's posture: produce zh_CN catalog plans but DON'T render until partnership confirmed. Do not include zh_CN in Phase 0 connector buildout.

---

## Engineering Roadmap (consolidated across all four research passes)

### Phase 0 — Foundation (must ship before any Phase C rendering)

| ID | Item | Source | Effort |
|----|------|--------|-------:|
| F-1 | Schema v3.0.0 with `text_by_locale` + per-locale `sfx[]` + per-locale `font_override` | Compositing §12 | M |
| F-2 | FONT_REGISTRY.yaml rebuild — install Source Han Sans JP/TC/SC/KR + Klee One + LxgwWenKai + Anime Ace + Badaboom | Compositing §1.5, §3 | S |
| F-3 | SVG vector bubble masters in `/assets/manga/bubble_shapes/` (11 shapes) + cairosvg compositing in bubble_render | Compositing §12 | M |
| F-4 | Vertical-strip composer (new file: `phoenix_v4/manga/chapter/webtoon_compose.py`) with beat-type-aware gutter table + safe slicing at gutter midpoints | Tech §2.1, Compositing §11 | M |
| F-5 | Migrate bubble_render text layout to Skia or PangoCairo (CJK kerning) | Compositing §13 | L |
| F-6 | 2× supersample render config — 1600×2560 master, downsample-on-export | Tech §2.4, Compositing §12 | S |
| F-7 | Korea AI Basic Act watermark embed (machine-readable, non-visible) | Tech §6 | S |
| F-8 | KDP Comics connector (already has design path; AI disclosure flow) | Prior PR #626 | M |
| F-9 | WEBTOON unified CANVAS connector — headless Chrome/Playwright against creator dashboard, with retry, throttling, DOM-change detection | Tech §4 | L |
| F-10 | Scroll Therapeutic Test as static-analysis CI gate (items 1-4) | Therapeutic §18 | M |

### Phase 1 — Per-market expansion

| ID | Item | Source | Effort |
|----|------|--------|-------:|
| E-1 | LINE Manga Indies connector (ja_JP) — Chrome dashboard automation; PNG/JPG ≤ 2MB ≤ 10000px tall ≤ 1000 imgs | Rakuten AI Q1 | L |
| E-2 | Naver Webtoon Korea creator portal connector — separate from WEBTOON unified | Tech §8 | L |
| E-3 | RTL-aware page compose for ja_JP + zh_TW B&W path | Compositing §11 | M |
| E-4 | B&W conversion + screentone export pass from same layered source | Compositing §11 | M |
| E-5 | Comic C'moA upload (Japan; AI-tolerant per Jan 2026 #1 precedent) | PR #626 | M |
| E-6 | GlobalComix secondary distribution | Existing | S |
| E-7 | Furigana renderer + vertical CJK rendering | Compositing §1.7 | L |

### Phase 2 — Therapeutic instrumentation

| ID | Item | Source | Effort |
|----|------|--------|-------:|
| T-1 | Per-teacher signature config — Anchor Panel + color palette + pacing pixels + light cue per the 12 teacher table | Therapeutic §18 | M |
| T-2 | 50-card Craft Formula Library as a queryable reference + content-template hooks in the writer pipeline | Therapeutic §16 | M |
| T-3 | HRV-style reader-pilot protocol with Welltory/EliteHRV (item 5 of the Scroll Therapeutic Test) | Therapeutic §18 | M |
| T-4 | Awe-Pullback pixel-budget enforcement — 1× per arc, ≥ 2400 px vastness panel | Therapeutic §6 | S |

### Risk register (Phoenix-specific)

| ID | Risk | Severity | Mitigation |
|----|------|---------|-----------|
| R-1 | No public WEBTOON upload API; headless Chrome is TOS-grey + brittle | **HIGH** | DOM-diff alerts; per-account throttling; manual fallback dashboard; relationship-build for partner API access |
| R-2 | LoRA character lock blocked by 16 GB VRAM (PR #623) | MED | Workaround: FLUX 2 IP-Adapter chains using Phoenix's 289 portraits; cap 2 characters per panel; multi-character via inpainting |
| R-3 | Pillow can't do CJK optical kerning; Phoenix's bubble renderer uses Pillow | MED | Migrate to Skia or PangoCairo; budgeted L effort (F-5) |
| R-4 | Piccoma specs not public; can only get them by submitting | MED | Treat Piccoma as Phase 2 partner-only target; no Phase 0 budget |
| R-5 | WEBTOON Originals exclusivity (3-yr post-completion digital + multimedia + merch) | HIGH if signed | **Stay Canvas-tier**; do not sign Originals until catalog audience proven |
| R-6 | Tapas AI ban; Shueisha AI hostility | LOW | Don't target. KDP + Canvas + LINE Manga Indies cover the market. |
| R-7 | Korea AI Basic Act enforcement post-Jan 2027 | LOW now, MED future | Watermark every Korean upload now; monitor Naver enforcement quarterly |
| R-8 | "AI-look" rejection patterns — even where AI not banned, AI-looking submissions silently downranked | MED | Apply human-creative-direction emphasis; render variation; avoid uncanny faces; lean into Phoenix's contemplative-ink-wash distinctiveness |
| R-9 | Premium CJK fonts may need commercial licensing for high-volume use | MED | Default to OFL Source Han Sans family; budget commercial-font review at >$50K Year-1 revenue |
| R-10 | Multi-language text expansion (Japanese ↔ English ~30–50% character delta) blows bubble bounds | MED | Bubble auto-resize at composite-time; coverage-cap enforcement (already in v2 schema) |
| R-11 | WEBTOON dashboard UI revisions break the headless connector | HIGH | DOM-diff continuous integration; alert on element-selector miss; manual fallback workflow |

---

## What changed vs the prior research pass (PR #626)

PR #626 set production weight: **58% color vertical webtoon / 24% B&W page / 14% color page / 4% direct self-help illustrated** across 528 production units. This master reference does not change those weights but **refines the implementation**:

| Prior PR claim | Refinement |
|----------------|-----------|
| "Add WEBTOON Canvas + KDP connectors as Phase 0" | Confirmed. Add: WEBTOON connector is **headless Chrome only — no public API**. This is the single biggest engineering risk. |
| "ja_JP dual-format per series" | Confirmed. **LINE Manga Indies has hard published specs** (Rakuten AI confirmed); Piccoma does NOT publish specs (pitch first, specs after). Plan dual-format as: B&W to KDP JP + Comic C'moA; vertical color to LINE Manga Indies; Piccoma as Phase 2 partner. |
| "WEBTOON Canvas covers ja_JP + ko_KR" | **Wrong.** Unified CANVAS is 7 languages: en, es, fr, id, th, zh_TW, de. **Japanese and Korean are SEPARATE platforms.** Three connectors needed, not one. |
| "AI Basic Act requires disclosure" | **Refined.** 1-year grace through Jan 2027. Obligations on **platforms, not individual creators**. Machine-readable non-visible watermark suffices for webtoons. Less burdensome than initially scoped. |
| "B&W page manga gets dedicated production" | **Wrong direction.** Layered compositing structurally favors webtoon. **Make webtoon the master format; B&W page is a downstream flatten + screentone export from the same source layers.** Saves ~40% of the page-manga production cost. |
| Per-episode revenue benchmark | **Refined.** WEBTOON Originals self-cited $1,000/ep illustrative; range $700-$8,000; net ~$450/ep after assistant pay. KOCCA 2024 median Korean serialized webtoon artist income ₩38M (~$28K)/yr. Stay Canvas-tier until established. |

---

## What Phoenix already has (the good news)

- **Bubble engineering: 80% complete.** v2 schema with 9 bubble styles, 4 font overrides, 4 tail styles, 8 position zones, coverage cap; Pillow renderer with 14 passing tests; intensity → style mapping; lettering derivation from script.
- **Catalog plan: 132 series with genre + style + author tags** for 4 markets = 528 production units.
- **289 character portraits** rendered FLUX-schnell-fp8 at high quality, contemplative-ink-wash style — direct fit for iyashikei color vertical.
- **Translation pipeline operational** for ja_JP, zh_TW, zh_CN.
- **12-teacher persona matrix** with allowed engines and intensity caps.
- **Strong market research baseline** — 10 dated 2024-2026 internal docs covering market sizes, platforms, regulations, bestseller patterns.

The work in this master + four companions is **20% of remaining engineering**, concentrated in: schema v3, font rebuild, SVG bubbles, vertical composer, headless connectors, and therapeutic instrumentation.

---

## Citations

This master synthesizes ~300 distinct citations across the four companions. Top primary-source URLs:

**Technical specs:**
- WEBTOON Canvas Format: https://www.webtoons.com/en/canvas/webtoon-format/list?title_no=109936
- Global CANVAS Creator FAQ: https://www.webtoons.com/en/notice/detail?noticeNo=3621
- WEBTOON CANVAS Zendesk file-size FAQ: https://webtooncanvas.zendesk.com/hc/en-us/articles/32913712749588
- KCBeat 2026 monetization: https://kcomicsbeat.com/2026/01/13/webtoon-rolls-out-changes-to-its-monetization-features/
- WBTN S-1 (SEC EDGAR): https://www.sec.gov/Archives/edgar/data/1997859/000119312524151708/d396527ds1.htm
- LINE Manga Indies creator guidelines (via manga.line.me; Rakuten AI cited inline)

**Compositing/lettering:**
- Blambot Comic Book Grammar: https://blambot.com/pages/comic-book-grammar-tradition
- Comicraft Glossary: https://balloontales.com/the-comicraft-glossary-of-lettering-terms/
- Todd Klein Lettering Placements: https://kleinletters.com/Blog/lettering-placements/
- Source Han Sans (Adobe): https://en.wikipedia.org/wiki/Source_Han_Sans
- zyddnys/manga-image-translator: https://github.com/zyddnys/manga-image-translator
- S-Morishita Studio panel guide: https://www.s-morishitastudio.com/webtoon-panel-size-guide-for-beginners/

**Therapeutic craft:**
- Polyvagal Institute: https://www.polyvagalinstitute.org/whatispolyvagaltheory
- Polyvagal Theory: A Science of Safety (PMC 2022): https://pmc.ncbi.nlm.nih.gov/articles/PMC9131189/
- Monroy & Keltner 2023 (awe → vagal tone): cited in therapeutic doc §6
- Hayao Miyazaki on "ma": https://screencraft.org/blog/hayao-miyazaki-says-ma-is-an-essential-storytelling-tool/
- Frieren pacing analysis (Crunchyroll Features Oct 2024): https://www.crunchyroll.com/news/features/2024/10/29/frieren-beyond-journeys-end-processing-grief
- Lore Olympus pacing/symbolism: https://en.wikipedia.org/wiki/Lore_Olympus

**Japan-market (Rakuten AI Chat session 2026-04-25, ai.rakuten.co.jp):**
- LINE Manga Indies specs cited inline by Rakuten AI from manga.line.me
- Piccoma SMARTOON FAQ: https://piccoma.com/web/help/26
- Piccomics editorial on submission (Clip Studio interview): https://www.clipstudio.net/

Full citations in respective companion docs.

---

*Compiled 2026-04-25 by Pearl_Research. This master + four companions form Phoenix Omega's WEBTOON production bible. Owner review → engineering kick-off.*
