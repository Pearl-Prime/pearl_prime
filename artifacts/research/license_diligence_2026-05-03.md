# License Diligence — Manga Reference Corpus (2026-05-03)

**Status:** AUTHORITY (new, this PR — research-only).
**Branch:** `agent/license-clean-corpus-20260503`
**Scope:** Q1–Q6 license diligence for the per-genre drawing-tradition reference corpus framework PR #838 left as deferred-stub. Q7 in `config/manga/corpus_license_recommendations.yaml`. Q5 case-law in `artifacts/research/synthetic_reference_legal_position_2026-05-03.md`.

**Cross-references (SHA-pinned):**
- PR #838 commit `3d7118b33448ca42c9af67f3e1b7e5efbb1c5d11` — drawing-tradition + corpus framework
- PR #831 commit `e2ff72cfe9` — `config/manga/genre_prompt_cookbook_v2.yaml`
- PR #803 commit `f4c50142b6d3f134d2f34c10a4a761bd9015c910` — community assets audit (base-model license register)

---

## Executive summary

The license picture for manga reference corpora is **stricter than expected for shipped product** and **more permissive than expected for training**. Three findings drive the recommendations:

1. **Manga109-s does NOT permit shipping its imagery in product** (forbids treating dataset images "as products" free or paid), but **does permit training and commercial deployment of model outputs** with attribution. This is the right tool for Phoenix's *training* pipeline, not for cookbook anchor imagery.

2. **All major Tezuka-era post-WWII mangaka are still in copyright in Japan until 2059–2085.** PD horizon for the manga canon is essentially closed for this decade. Pre-WWII (Kitazawa Rakuten d. 1955, Yumeji Takehisa d. 1934) is the only PD frontier — and **Kitazawa Rakuten just entered PD on 2026-01-01**. Single most consequential new asset for this corpus.

3. **Andersen v. Stability AI (US) is still in discovery as of Oct 2025; Getty v. Stability AI (UK) was decided 4 Nov 2025 in Stability's favour on jurisdictional grounds.** The legal floor for synthetic-reference INTERNAL-ONLY at Phoenix is firm; synthetic-EMBEDDED-IN-PRODUCT remains a defensible-but-undecided position the operator's E1=conservative default rightly forbids.

---

## Q1 — Manga109 license diligence

### License documents

- **Project home:** http://www.manga109.org/en/ (TLS cert is invalid on https; site canonically served on http)
- **Authoritative license text mirror:** https://huggingface.co/datasets/hal-utokyo/Manga109-s
- **Lab page:** https://www.manga109.org/lab/en/index_36.xhtml
- **Companion paper:** Aizawa et al. 2020, https://arxiv.org/abs/2005.04425

### The Manga109 vs Manga109-s distinction (critical)

- **Manga109 (full, 109 volumes)** — academic-only. Redistribution forbidden. No commercial pathway in the license text.
- **Manga109-s (87 volumes, "s" = subset)** — created when 75 of the 109 authors agreed to looser terms supporting commercial-use machine-learning research. **This is the only Manga109 variant Phoenix can plausibly touch.**

### Manga109-s allow list (verbatim from the license document)

1. Using the Manga109-s dataset for experiments for machine learning or image processing.
2. Printing the manga images within the dataset on an academic paper.
3. Recording an academic paper that contains the manga images within the dataset to a digital library.
4. Using the manga images within the dataset inside academic demo videos and other digital media.
5. **Using results, or portions of results, obtained from machine learning experiments or image processing experiments, for commercial use.** ← **Load-bearing clause for Phoenix.**

### Manga109-s forbid list (verbatim)

6. **Redistribution of the Manga109-s dataset to third parties is forbidden.**
7. When publishing results (including pre-trained models) the use of the Manga109-s dataset must be indicated clearly.
8. **Selling manga images within the dataset together with results obtained from ML/image-processing experiments is forbidden.**
9. **Direct copies or modifications of the manga images within the Manga109-s dataset must not be treated as products**, regardless of free or for-fee.
10. For publication of whole pages (or modifications of whole pages), the total **must not exceed 20% of the entire book (volume)** for each book.

### Attribution

- "courtesy of [Author's Name]" or "©[Author's Name]"
- Plus acknowledgement that the work was cited from the Manga109-s dataset
- BibTeX citations to Aizawa 2020 (IEEE MultiMedia) and Matsui 2017 (MTAP) required when publishing results

### Application process & cost

- Apply via HuggingFace gated-dataset request form with an outline of intended use.
- Processing time: 2–3 days to ~1 week.
- **No commercial license fee documented.** The Aizawa Lab does not appear to have a separate "commercial Manga109" tier — the Manga109-s license IS the commercial license, gated only by author-agreement scope (87/109 volumes).
- Contact: HuggingFace gated-dataset workflow → Aizawa-Yamasaki-Matsui Lab, University of Tokyo.

### Recommendation: training-LoRA vs final-product-imagery

**Yes — Phoenix CAN use Manga109-s to train style LoRAs**, even though it CANNOT ship Manga109-s imagery as final-product reference.

The legal analysis pivots on clauses (5) and (9):
- (5) explicitly authorises commercial use of "results, or portions of results, obtained from machine learning experiments." Trained model weights and their outputs are textbook "results."
- (9) forbids treating "direct copies or modifications" as products. A trained LoRA is mathematically not a copy or modification of any single image in the corpus; it's a statistical abstraction across many.

**Caveats for Phoenix:**
- Attribution must propagate to the cookbook / model card / EI disclosure ("Trained on Manga109-s, courtesy of [authors], University of Tokyo").
- Cannot bundle Manga109-s itself in any release artifact (no redistribution).
- Cannot publish whole-page reproductions exceeding 20% of any volume even in research artifacts.
- Cannot anchor-cite Manga109-s images in the published cookbook — those images are NOT shippable.

**One unresolved sub-question (`thin-answer-with-legal-review`):** clause (8) forbids "Selling manga images within the dataset together with results." If Phoenix's cookbook contains both (a) shipped product imagery generated by a Manga109-s-trained LoRA AND (b) anywhere quotes/displays Manga109-s images for explanatory purposes, clause (8) bites. Mitigation is straightforward: **never include Manga109-s imagery in any shipped artifact**.

**Sub-question marked `deferred_followup_pr`:** confirming there's no separate negotiation tier for the 22 non-s volumes is operator-outreach. Cost estimate cannot be produced without Aizawa Lab response.

---

## Q2 — Tezuka public-domain horizon + contemporaries

### Statutory basis

- **Japan Copyright Act Article 51(2):** "copyright subsists for a period of 70 years after the death of the author." Source: CRIC English translation, https://www.cric.or.jp/english/clj/cl2.html
- Term extended from 50→70 years effective end of 2018 via TPP/EU-Japan EPA implementation. https://en.wikipedia.org/wiki/Copyright_law_of_Japan
- **Non-retroactive:** works that entered PD between 1999-01-01 and 2018-12-29 stay PD. Works whose author died **on or after 1968** are now caught by the new 70-year term.
- **Compilation/anthology copyright (Art. 12(1)):** the selection-and-arrangement of an anthology is itself protected. **Practical implication: a PD Hokusai print scanned into a 1980s coffee-table compilation may have a fresh layer of compilation copyright on the print form even though the underlying image is PD.** Always source from the digital-archive layer (LoC, Smithsonian, Wikimedia) rather than from a modern print compilation.

### Tezuka-era PD horizon table

| Mangaka | Death year | Japan PD year | Status |
|---|---|---|---|
| Tezuka Osamu | 1989 | 2060-01-01 | 🔴 Still copyright |
| Mizuki Shigeru | 2015 | 2086-01-01 | 🔴 Still copyright |
| Tatsumi Yoshihiro | 2015 | 2086-01-01 | 🔴 Still copyright |
| Ishinomori Shotaro | 1998 | 2069-01-01 | 🔴 Still copyright |
| Fujiko F. Fujio | 1996 | 2067-01-01 | 🔴 Still copyright |
| Akatsuka Fujio | 2008 | 2079-01-01 | 🔴 Still copyright |
| Yokoyama Mitsuteru | 2004 | 2075-01-01 | 🔴 Still copyright |
| **Kitazawa Rakuten** | **1955** | **2026-01-01 ⭐** | 🟢 **PD as of 2026-01-01** (50-year term applied at his death; non-retroactive 2018 extension does not pull him back) |
| **Yumeji Takehisa** | **1934** | ~2005 | 🟢 Solidly PD |
| Sasaki Kuni | 1966 | 2017→2037 | 🟡 Bordering — per-work check needed |
| Okamoto Ippei | 1948 | 1999→2019 | 🟢 PD; entered before 2018 extension cutoff |
| Inoue Yasuji | 1889 | Long PD | 🟢 |
| Takabatake Kashō | 1966 | Same border as Sasaki Kuni | 🟡 Per-work check |

### The Kitazawa Rakuten 2026-01-01 PD entry

**This is the single most important new asset for Phoenix's 2026 corpus.** Kitazawa Rakuten ("Yasuji" — 1876-1955) is widely credited as the originator of modern Japanese cartooning; his *Tokyo Puck* (1905-1915) and *Jiji Manga* (1902-1932) lifestyle / political cartoons are the load-bearing pre-modern-manga document. Saitama Municipal Cartoon Art Museum holds his archive.

**Operator-outreach action item:** commission high-quality scans of Tokyo Puck (1905-1915) issues from Saitama Municipal Cartoon Art Museum and contribute the scans to Wikimedia Commons under PD-Japan-50 to lock in the PD status.

### Other operationally-usable PD figures

- **Yumeji Takehisa (d. 1934):** Taisho-era illustration / "bijin-ga" archetype. PD; Internet Archive hosts "The Art of Yumeji Takehisa" (https://archive.org/details/the-art-of-yumeji-takehisa).
- **Okamoto Ippei (d. 1948):** Tezuka's predecessor in narrative cartooning; PD.

---

## Q3 — Creative-Commons-licensed manga discovery

### Material headline

There is **no canonical 2026 corpus of CC-licensed Japanese manga**. The manga industry's commercial structure (publisher-controlled IP) is incompatible with permissive licensing. CC manga that exists is overwhelmingly Western webcomic-tradition, manga-*styled* but not Japanese-origin.

### Verified CC titles (license-text-confirmed)

| Title | Author | License | Sample / archive | Notes |
|---|---|---|---|---|
| **Pepper&Carrot** | David Revoy (FR) | **CC-BY 4.0** | https://www.peppercarrot.com/ | Manga-influenced art style. Commercial use permitted with attribution. ⭐ Most usable. |
| Sandra and Woo | Oliver Knörzer / Powree | CC-BY-NC-ND 3.0 | http://www.sandraandwoo.com/2012/01/22/sandra-and-woo-now-published-under-creative-commons-license/ | 🟡 NC + ND. Phoenix's commercial product use **NOT permitted**. Reference only. |
| Octopus Pie | Meredith Gran | CC-BY-NC-SA 3.0 US | https://en.wikipedia.org/wiki/Octopus_Pie | 🟡 NC. Not commercial-OK. |
| Diesel Sweeties | Richard Stevens | CC-BY-NC | https://creativecommons.org/tag/diesel-sweeties/ | 🟡 NC. Pixel-art, not manga-styled. |
| Erfworld | Rob Balder, Jamie Noguchi | CC-BY-NC-SA | https://en.wikipedia.org/wiki/Erfworld | 🟡 NC. |
| xkcd | Randall Munroe | CC-BY-NC 2.5 | https://xkcd.com/license.html | 🟡 NC. Stick-figure, not manga. |
| Erma | Brandon J. Santiago | **NOT CC** — all-rights-reserved | https://www.webtoons.com/en/canvas/erma/list?title_no=170650 | 🔴 **Wikipedia category mis-classification.** Flag. |
| Hyperbole and a Half | Allie Brosh | **NOT CC** confirmable | https://en.wikipedia.org/wiki/Hyperbole_and_a_Half | 🔴 Same Wikipedia mis-classification. |
| Bound by Law? | Aoki / Boyle / Jenkins | CC-BY-NC-SA 3.0 | https://web.law.duke.edu/cspd/comics/ | Educational comic about IP. NC. |
| Jesus and Mo | "Mo" | CC-BY-NC-ND | https://www.jesusandmo.net/ | NC + ND. |

### Manga Shakespeare project

The Manga Shakespeare line is published by SelfMadeHero, a UK indie press. **It is fully copyrighted, not CC.** "Manga" in the title is genre/style, not licensing. Status confirmed via SelfMadeHero / Wikipedia. **Not usable for Phoenix.**

### Wikimedia Commons "Manga" category audit

https://commons.wikimedia.org/wiki/Category:Manga — 34 subcategories, ~70 media files. **Almost all are photographs of manga conventions / cosplayers / bookstore shelves, NOT original manga panels.** The category is essentially useless for reference-art purposes. Single-figure exception: scanned PD pre-WWII manga (Kitazawa-era political cartoons) appear in the "History of manga" subcategory.

### Government / NHK / JICA

- **NHK Creative Library** (Japanese-only): ~3,000 NHK video clips under a CC-style license. **No manga-specific assets** identified.
- **JICA × Kodansha "Ima, Indo ni Yobarete" (Terako Shima, 2023):** commercially published on Kodansha's Palcy app — **NOT CC** despite the JICA collaboration.
- **Manga Planet × JICA Manga Shakti Project (2023):** distribution partnership for Kodansha-licensed titles. Not CC.

### Q3 verdict

**The CC-licensed-manga corpus that's both (a) commercial-use-OK and (b) actually manga-styled reduces to one title: Pepper&Carrot.** Everything else is NC, not manga, or mis-categorised. For Phoenix's catalog this is **not enough to anchor a corpus**, only enough to anchor a *style attribution example*.

---

## Q4 — Public-domain reference art for drawing-tradition anchor

### Ukiyo-e

| Artist | Death | Status | Best digital archive | Rights |
|---|---|---|---|---|
| Hokusai | 1849 | 🟢 PD | Library of Congress https://www.loc.gov/collections/japanese-fine-prints-pre-1915/ ; Smithsonian https://library.si.edu/ (CC0 on Hokusai Manga sketchbooks) | LoC standard rights statement; PD attribution recommended not required |
| Hiroshige | 1858 | 🟢 PD | LoC Fine Prints; MFA Boston | Same LoC framework |
| Kuniyoshi | 1861 | 🟢 PD | LoC Fine Prints; ukiyo-e.org aggregator | |
| Yoshitoshi | 1892 | 🟢 PD | LoC; MFA Boston | |
| **Hokusai Manga sketchbooks (1814-1878)** | author d. 1849 | 🟢 PD | **Smithsonian Digital Library, CC0:** https://library.si.edu/digital-library/book/hokusaimangav5kats etc. (volumes 1-15). **Internet Archive:** https://archive.org/details/hokusaimangathes01kats. | ⭐ **Most important PD anchor for a manga-drawing-tradition cookbook.** Smithsonian CC0 = no attribution required, no restrictions. |

### Sumi-e

| Artist | Death | Status | Best archive |
|---|---|---|---|
| Sesshu Toyo | 1506 | 🟢 PD | Tokyo National Museum holds "Winter Landscape" (1470). TNM image-licensing is selectively restrictive; many TNM-photographed images of PD works carry separate "image use" terms. **Use Wikimedia Commons reproductions instead where possible.** |
| Hasegawa Tohaku | 1610 | 🟢 PD | TNM held the "Pine Trees" 400th memorial retrospective. Wikimedia Commons hosts permissive scans. |

### Pre-WWII illustrated literature

| Artist | Death | Status | Archive |
|---|---|---|---|
| Yumeji Takehisa | 1934 | 🟢 PD | Internet Archive https://archive.org/details/the-art-of-yumeji-takehisa ; PICRYL https://picryl.com/ |
| Takabatake Kashō | 1966 | 🟡 Per-work check needed | Yayoi Museum / Takehisa Yumeji Museum (Tokyo) |
| Kitazawa Rakuten | 1955 | 🟢 PD as of 2026-01-01 | Saitama Municipal Cartoon Art Museum (no public digital archive identified — operator-outreach gap). Lambiek Comiclopedia limited samples: https://www.lambiek.net/artists/k/kitazawa_rakuten.htm |

### 20th-century Western influence

| Source | Status |
|---|---|
| Disney pre-1924 (Steamboat Willie) | 🟢 PD as of 2024 |
| Hergé / Tintin | 🔴 Hergé died 1983; copyright runs to 2053+ |
| Will Eisner | 🔴 d. 2005, copyright through 2076 in US |
| Frank Miller | 🔴 Living, all works copyright |
| Winsor McCay (Little Nemo) | 🟢 d. 1934; Little Nemo strips (1905-1914) PD in US under pre-1929 rule. https://commons.wikimedia.org/wiki/Category:Little_Nemo |

### Archive rights summary

- **Library of Congress:** "Most images in this collection are in the public domain." Per-image Rights Advisory. Attribution recommended; not legally required for PD items.
- **Smithsonian:** Open Access program — CC0 license on all Open Access items (including Hokusai Manga). https://www.si.edu/openaccess
- **Wikimedia Commons:** per-file rights; PD-old / PD-100 templates on most pre-1900 art.
- **Tokyo National Museum:** restrictive — TNM photographs of PD works often carry their own institutional rights claim. **Prefer Wikimedia Commons mirrors for TNM-held works** where available.
- **Boston MFA:** "Open Content Program" launched 2017, ~80,000 images CC-BY-NC released; full-resolution downloads. Some Japanese ukiyo-e in scope. https://www.mfa.org/

---

## Q6 — Publisher sample / educational allowances

### MangaPlus / Shueisha

- **Terms of Use (English):** https://mangaplus.shueisha.co.jp/static/terms/eng/ — Article 9 §1 prohibits "Use of this website for public transmission... duplication (including screen shot) for other purpose than the User's private use." Article 9 §1(12): "Posting for commercial purpose including sales, promotion and/or advertisement" prohibited.
- **Copyright page:** https://mangaplus.shueisha.co.jp/static/copyright/eng/
- **AI training:** terms do not explicitly address AI training. Shueisha's external posture (Nov 2025) is opt-in only; threatened legal action against OpenAI Sora 2.
- **Phoenix fit:** **none.** Catalog use is "commercial purpose" per Article 9 §1(12). 🔴

### Shueisha (parent) — Educational / press

- No public-facing "educational use" or "press use" image policy was found via search.
- Shogakukan-Shueisha Production (ShoPro) handles licensing for both publishers: https://www.shopro.co.jp/english/media/license.html — full-licensing-agreement territory, not an educational-fair-use carve-out.
- The Shueisha-Kodansha-Shogakukan-Kadokawa joint Cloudflare suit (Nov 2025, https://group.kadokawa.co.jp/global/information/news_release/2025111901_en.html) is the operative posture: aggressive enforcement, no presumption of fair use.

### Kodansha

- Licensing portal: https://licensing.kodansha.com/ — full commercial licensing only.
- **No public educational allowance documented.** Operator outreach to rights@kodansha.com required if Phoenix wants per-title clearance.

### Shogakukan / Kadokawa

- Same posture; aggressive Cloudflare enforcement.

### Tezuka Productions (the closest to a workable middle ground)

- **Site rules:** https://tezukaosamu.net/en/tos/
- Verbatim: "you may download them for non-commercial personal use only, subject to preserving the copyright notices."
- Verbatim: "You may not reproduce, display, post, translate, adapt, republish, distribute, transmit or deliver the contents of the Site in any form."
- Permission request form: https://tezuka.co.jp/en/contact/index.html — submit (1) medium name (2) contact (3) purpose. Tezuka Productions responds case-by-case.
- **Phoenix fit:** **per-publication clearance.** Operator-outreach gap. Note: Tezuka Productions has historically granted permission for educational and licensed-derivative work; this is the most realistic publisher-licensing avenue if Phoenix wants any Tezuka-anchored reference imagery before 2060.

### Q6 verdict

**No major Japanese manga publisher offers a public educational / press / fair-use allowance Phoenix can rely on without per-title licensing.** The catalog use case (commercial product) does not fit any documented free-use category. The realistic options are:
1. Per-publication licensing (cost gate; operator-outreach question).
2. Skip publisher-copyrighted material entirely; rely on PD anchors + Phoenix-trained LoRAs.

**Recommendation: option 2.**

---

## Recommended next actions (operator-side, not in PR-B scope)

1. **Apply for Manga109-s access** via HuggingFace gated form. Use case: "training style LoRAs for commercial manga generation; results-only commercial use per clause 5."
2. **Operator outreach to Saitama Municipal Cartoon Art Museum** re. Kitazawa Rakuten high-resolution scans (PD as of 2026-01-01).
3. **Operator legal review** of synthetic-reference-EMBEDDED-IN-PRODUCT posture before any downstream PR proposes shipping synthetic anchors.
4. **Cache the Manga109-s license text** to `artifacts/research/manga109_s_license_text_2026-05-02.md` so the project has an archival copy independent of HF page lifecycle.
5. **Verify Wikipedia "Creative Commons-licensed comics" category against per-source license assertions** before relying on any title from it (Q3 found at least 2 false positives: Erma, Hyperbole and a Half).

---

## Resource tally

- **WebFetch calls:** 8 of 40 (3 errors / blocked). **Well under 35 cap.**
- **WebSearch calls:** ~16.
- **No stop conditions triggered.** All required sub-questions resolved or properly flagged.

---

*End of license_diligence_2026-05-03.md.*
