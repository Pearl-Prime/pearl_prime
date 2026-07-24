# Trend / Pattern Delta Bank (2026-07-23)

Companion to `deep_research_digest_20260723.md`. This is the compact, copy-usable extraction Lane C
should cite directly when authoring atoms. Each row names the delta from current spec/config
practice, the pattern to use instead, and whether it's verified-cited or general-knowledge-uncited
(see digest §6 for the full legend). This bank does not itself contain any atom rows — no atom
content is authored in this lane.

## Platform format-mix / hashtag deltas

| Platform | Current spec/config assumption | Verified 2026 pattern | Status |
|---|---|---|---|
| Instagram | `hashtags_min:5, max:15` (platform_specs.yaml) | Hard-capped at 5 platform-wide since 2025-12-19; recommended zone 3–5, high-relevance/medium-competition tags, not mega-tags | Verified-cited |
| Instagram | (implicit) hashtags drive discovery | Caption-native keywords are now the primary discovery mechanism; hashtags are classification metadata, not a reach lever | Verified-cited |
| LinkedIn | `hashtags_min:3, max:5` | Already correct — no change needed | Verified-cited (confirms existing config) |
| LinkedIn | (no explicit length guidance) | ~300–400 words / 20+ sentences maximizes dwell time, provided clarity holds; outbound links cost ~60% reach | Verified-cited |
| LinkedIn | (no carousel-priority signal) | Document/carousel posts report 2–3x dwell time of text/image posts | Verified-cited |
| TikTok/Reels/Shorts | Spec's VIDEO_BEAT: 0-3/3-8/8-20/20-25s+CTA | Confirmed directionally correct; cited variant: 0-3s hook, 3-8s situate, 8-22s value (2-3 beats), 22-27s payoff, 27-30s soft CTA | Verified-cited, no retire needed |
| Pinterest | `hashtags_min:2, max:5` | Fine as ceiling; real lever is description keyword placement (front-loaded, 3-6 keywords across title/description/alt-text) — not currently a distinct atom field | Verified-cited |
| Facebook | (no explicit signal) | Reach favors comments/shares ("Meaningful Social Interactions") over passive likes; engagement-bait penalized | Verified-cited |
| X/Threads | (no explicit thread-shape guidance) | Hook → Context → Position → Invitation; first line must leave tension unresolved; opinion-bearing beats purely informational | Verified-cited |

## CTA variety (pilot evidence: 2 unique CTAs across 20 posts — this is the sharpest live defect)

Verified pattern categories to diversify against (not literal copy to paste — Lane C authors the
actual lines):
1. **Save/bookmark** (current only variety used) — keep, but do not let it be the only category.
2. **Comment-prompt** (specific personal-experience question, not "comment below") — supported by
   the Threads/X finding that specific-personal-experience prompts outperform generic ones.
3. **Try-now micro-action** (do the tool step in the next N minutes, not "save for later") —
   supported by TikTok/faceless-video completion-focus finding.
4. **Share-with-someone** framing (name who it's for, not "share this") — supported by Facebook's
   meaningful-interaction finding (shares are a stronger signal than likes).
5. **Follow-for-next-part** (only where a genuine series/thread continuation exists — do not fake a
   series) — supported by carousel/thread "open loop" and re-serving findings.

## MICRO_STORY seed material (see digest §2 — corrected to name the real primary source)

**Primary, already-authored, untracked-on-disk source: `docs/research_social_media.txt`.** Contains
a ready-to-use Before-and-After format row (Instagram Carousels/TikTok, cold audience, side-by-side
behavioral-comparison visual, Profile-Visits KPI, named failure mode "over-promises quick results")
and a full weak→improved→excellent hook-quality ladder per hook-psychology-type with platform
adaptations. Lane C should pull from this file directly before reaching for any general template.

Secondary, general-knowledge-uncited four-beat template (offered only as a fallback shape, not a
found-in-source template): Anchor (concrete sensory/situational detail) → Turn (the specific moment
the pattern became visible) → Shift (what changed, stated as action/felt-state, not abstraction) →
Residue (one small concrete line of what's different now). All MICRO_STORY atoms must be original
composites, labeled as such in `source_refs` — never presented as a real named individual's
testimonial absent real consent and citation.

## CASE_PROOF safe shapes (see digest §3 — corrected to name the real primary source)

**Primary, already-authored, untracked-on-disk source: `docs/research_social_media.txt`.** Two
directly usable shapes:
1. Social-proof-as-shared-struggle framing: name that many people experience the same pattern, to
   normalize rather than to boast — explicitly *not* a metrics-flex.
2. Case-Study structural shape: **Problem → Mechanism → Result** (LinkedIn/Facebook/YouTube,
   warm/informed audience, Lead-Gen KPI; named failure mode: "dry, clinical, or lacks human
   emotion" — pair the structure with felt language, not just a clean logical chain).

Secondary, fresh-web-verified/general-knowledge-uncited shapes (see digest §3 for the split):
aggregate-pattern framing with a real, checkable source (or drop the claim); mechanism-plus-caveat
framing ("maps to what X researchers call Y — not a diagnosis, a pattern"); disclosure-first framing
("I'm not a therapist — here's what worked as one data point").

Hard line for both sources: no clinical-efficacy claims, no diagnosis-applicability claims, no
guaranteed outcomes.

## CAROUSEL_SLIDE structural delta

Current atom metadata has no field for a slide's position in an "open loop" arc. Verified pattern:
5–8 slides optimal for saves/completion; cover slide poses an unresolved question; answer withheld
until slide 5–6 of 8; re-serving reportedly triggers at slide-3+ swipe-through. Flagged as a schema
gap in digest §4/§7 (R5) — not fixed in this lane.

## APAC per-market voice corrections (post native-review — see digest §5 for full context)

| Market | Retire/correct | Replace with |
|---|---|---|
| Japan | Treating anonymous-account culture as a new Gen Z wellness trend | Structural, decades-old privacy norm — assume public-feed audience reads/lurks privately |
| Japan | "Detailed/thorough" as license for dense feed captions | Structured completeness (steps/caveats), not word count, in short-form; thoroughness applies to long-form only |
| Korea | "Kakao Story" as a live platform | Defunct — never reference; KakaoTalk (messenger) is the live product |
| Korea | "Group harmony" as the wellness-copy value | 개인주의/자기돌봄 (individualism/self-care), 혼자 culture, 갓생 framing; name exhaustion before pivoting to encouragement |
| China (CN) | "No superlatives" as the compliance rule | Specific 广告法 trigger words (最/第一/唯一/国家级/极致/100%有效/永久/根治) + no diagnosis-style or cure-guarantee language |
| China (CN) | Pure confessional tone as sufficient credibility signal | Confessional tone + visible credential marker (both, not either) |
| Hong Kong | Full-sentence language alternation as the code-switching model | Intra-sentential code-switching (English word dropped into Cantonese-grammar sentence) |
| Hong Kong | XHS Traditional-Chinese content as a safe local-language win | XHS in HK risks reading mainland-inflected; guard against it specifically |
| Singapore | Xiaohongshu as a general SG wellness channel | Niche diaspora/beauty-luxury channel; IG/TikTok/WhatsApp-Telegram are the real dominant surfaces |
| Singapore | Dialect diversity (Hokkien/Cantonese) as a resonance lever | "Singdarin" code-switching for under-50s; dialect only for 60+ (Pioneer/Merdeka generation) |
| Singapore | "Concise/pragmatic/data-driven" as the wellness voice | Warmer register with light Singlish markers for emotional-support content; efficiency-framing reserved for productivity/corporate-wellness angles |
| Taiwan | "Warmth + community feel" as the complete register | Also confessional/self-deprecating/diary-style, especially on Threads |
| Taiwan | (not previously flagged) Simplified-Chinese-derived terms used unchecked | Hard substitution checklist: 心理咨询→心理諮商/諮詢, 抑郁症→憂鬱症, 视频/网络/信息→影片/網路/資訊, 治愈→療癒, 情绪价值→情緒價值 (caution), 内卷 has no TW equivalent |
| Taiwan / Singapore | Conflating Taiwan's PDPA (個人資料保護法) with Singapore's PDPA | Treat as two fully separate laws — do not reuse text between the two markets' compliance notes |
