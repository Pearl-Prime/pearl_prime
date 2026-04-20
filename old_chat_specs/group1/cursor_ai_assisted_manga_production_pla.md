# AI-assisted manga production plan
_Exported on 4/16/2026 at 19:37:19 GMT+8 from Cursor (3.1.15)_

---

**User**

how to fix in whole system? and biz and marketing? 

Note: we will say AI assisted because our main art will be authored by a human artist , but the rest is AI assisted.

write plan

how to solve for: [Now let me read the rest of `build_demo_plan`:Now let me read the rest of the generate_images function and the main block:Good, I have the full picture. Now let me also check what teacher data we have to write good series titles and descriptions:Now I have everything I need. Let me rewrite `build_demo_plan()` for the new 13-page structure:

**New layout:**
- Page 1: Ahjan series intro (1 hero image, reuse ahjan character)
- Pages 2-7: 6 engines × 3 panels = 18 images  
- Page 8: 3 hero characters (1 Gen Z + 2 Gen Alpha) = 3 images
- Page 9: Ahjan vs Junko comparison = 2 images (reuse ahjan hero from p1 + new junko same-style)
- Pages 10-12: Teacher galleries, 4 per page = 12 images
- Page 13: Closing (no images)

**Total: 36 images** (but page 9 reuses ahjan from page 1, so 35 unique + 1 reuse)Now rewrite `build_demo_plan()`:Now update the `--section` choices and main:Now dry-run to verify:35 unique images (+ 1 reuse of ahjan_hero on the compare page). Now verify all prompts are under 500 chars:8 prompts slightly over. Let me tighten the `_prompt` truncation:The truncation applies before teacher boost is added. I need to apply it AFTER the boost. Let me fix `_apply_teacher_style` to enforce the 500 limit:All under 500. Now let me write the HTML:First, archive the current HTML:Now write the new HTML. This is a big file, so I'll write it directly:Now generate the full dry-run and save the prompt plan:Done. Both files refactored. Here's the new structure:

**Page 1** — Ahjan series intro: "The Weight You Carry", hero image, Gen Z tag, series desc, topics covered

**Pages 2-7** — One engine per page (shame, false_alarm, overwhelm, spiral, watcher, grief), each with 3 panels telling a complete scene: environment → character → resolution

**Page 8** — 3 new heroes: Joshin (Gen Z), Miki (Gen Alpha), Ra (Gen Alpha), each with series title, desc, and topic coverage

**Page 9** — Ahjan vs Junko comparison on dark_psychological: reuses ahjan_hero.png + new Junko render, with style breakdowns showing the teacher differentiation

**Pages 10-12** — Teacher galleries, 4 per page, each with 1 character portrait + series title + desc

**Page 13** — Closing

**35 unique images**, max prompt 495 chars, all under 500. 

Now — I see your new message about Rakuten AI deep research. Let me address that next.

---

I need to check whether the Rakuten AI deep research tool is available. Let me look for it:Rakuten AI is a Japanese-focused AI platform. Let me access it through Chrome:The Rakuten AI page is freezing the browser. Let me try a different approach — their search tool may require a Rakuten ID login which could be blocking. Let me check if you're already logged in or if there's a different URL:Rakuten AI isn't accessible from here — it requires a Japan-based Rakuten ID. Let me do the deep research directly using web search across all the assumptions in our pipeline. I'll identify every unresearched claim, validate it, and flag what needs fixing.First, let me catalog every assumption we're making that hasn't been research-validated:

**Assumptions in the pipeline:**

1. Gen Z wants dark psychological manga about anxiety/shame/grief
2. Gen Alpha (8-12) will engage with choose-your-path manga panels
3. Iyashikei, shonen, noir, webtoon, 4-koma are valid style categories that map to distinct audiences
4. Therapeutic/mental health manga is a viable product category
5. Art style (ink weight, B&W ratio, line type) meaningfully differentiates brands in manga
6. 65% B&W for Ahjan, 10% for Junko — these ratios matter to readers
7. Webtoon vertical scroll format is the right format for Gen Z romance
8. Meme/4-koma format works for TikTok-native audiences
9. 12 distinct teacher-brands can each sustain a manga series
10. "Engines" (shame, spiral, grief, etc.) map to distinct visual storytelling styles
11. Shonen training arcs work as metaphor for emotional regulation exercises for kids
12. AI-generated manga art is accepted by manga readers

Now let me research in parallel:Now let me compile everything into a research document:Full research audit complete. Here's the executive summary:

[View the full research audit](computer:///Users/ahjan/phoenix_omega/docs/MANGA_PIPELINE_RESEARCH_AUDIT.md)

**The big picture**: 7 of 12 assumptions validated, 4 partially validated, 1 unvalidated. The pipeline is fundamentally sound but has 3 critical fixes needed:

**CRITICAL FIXES:**

1. **12 teachers at once is too many** — No publisher launches 12 series simultaneously. Launch with Ahjan (flagship) + Junko (contrast) + 1 Gen Alpha. Rest becomes a roadmap. This is the biggest risk in the whole system.

2. **Don't call it therapy** — The research supports manga for emotional literacy, but making clinical claims without trials is ethically and legally risky. Reframe as "wellness manga" / "emotional literacy through storytelling" + add disclaimers.

3. **Custom archetype names look made up** — "collapse_cosmic" and "wound_literary" aren't real genres. Map to recognizable names for anything reader-facing (Cosmic Horror, Literary Josei, etc.). Keep the internal codes for production only.

**IMPORTANT FIXES:**

4. **4-koma isn't "TikTok-ready"** — TikTok is video. 4-koma is static panels. Target Instagram/X, or animate for TikTok.

5. **B&W teachers may struggle on webtoon platforms** — Webtoon audiences expect color. Plan color variants.

6. **AI transparency** — In Jan 2026, an AI manga hit #1 in Japan, proving it works commercially. BUT backlash is real when AI is hidden. Be upfront.

**WHAT'S SOLID** (backed by $10B+ markets): Gen Z mental health manga demand, webtoon vertical format, iyashikei as healing genre, interactive choose-your-path for Gen Alpha, art style as brand differentiator.

Sources:
- [Allied Market Research — Manga Market $21B by 2034](https://www.alliedmarketresearch.com/global-manga-comics-market-A325855)
- [CBR — Japan's Top Manga 2026 is AI-Generated](https://www.cbr.com/manga-top-ranking-2026-ai-generated/)
- [Mordor Intelligence — Webtoons $60B by 2031](https://www.mordorintelligence.com/industry-reports/webtoons-market)
- [Phys.org — Iyashikei healing manga](https://phys.org/news/2024-10-iyashikei-manga-comforts-readers-attention.html)
- [Kotaku — AI Manga Bestseller 2026](https://kotaku.com/one-of-the-best-selling-manga-in-japan-right-now-was-made-by-ai-2000657158)
- [ResearchGate — Manga and mental health relationship](https://www.researchgate.net/publication/384114702)]

---

**Cursor**

Exploring the codebase to locate where manga pipeline assumptions, teacher strategy, and messaging live so we can draft a grounded plan for system, business, and marketing fixes.



Synthesizing the research audit, your “AI-assisted / human-authored main art” framing, and where those concerns touch code and collateral.



