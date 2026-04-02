# Brand Admin Onboarding — Image Pack v1 (Trust Layer)

**Purpose:** Tactical execution package (**A + B + C**) aligned to the spec stack:

- [BRAND_ADMIN_MEDIA_GENERATION_SPEC.md](./BRAND_ADMIN_MEDIA_GENERATION_SPEC.md) — contract-locked, deterministic generation + QA gates
- [ONBOARDING_REAL_EXAMPLE_GENERATION_SPEC.md](./ONBOARDING_REAL_EXAMPLE_GENERATION_SPEC.md) — what examples must exist, comparison logic, fidelity truth, registry behavior
- [BRAND_ADMIN_ONBOARDING_PAGES_SPEC.md](../docs/BRAND_ADMIN_ONBOARDING_PAGES_SPEC.md) — where proof shows up: hero/supporting spine, gallery, matrix, proof strip, inline media, proof-pending fallback

**Scope:** This pack is **Image Pack v1 — trust layer**. It is **not** full long-term lane proof coverage; see §11 and the real-example spec’s minimum matrix and `cmp_*` sets.

---

## A. Exact prompts for all 19 images

### Global rules for every prompt

These apply to every slot.

#### Hard rules

- Must feel like **real system output**
- Not mood board art
- Not vague conceptual AI wallpaper
- Clean composition
- Strong commercial readability
- Clear lane / tone / posture signal
- Professional finish
- No text baked into image unless the asset is specifically a UI/proof board style
- No random hands unless composition genuinely needs them
- No distorted faces
- No extra limbs
- No surreal artifacts unless explicitly part of the concept

#### Rendering direction

Use this suffix for most prompts:

> polished commercial product visual, premium publishing quality, clear focal hierarchy, visually believable, clean lighting, strong composition, modern editorial finish, realistic material treatment, production-ready, not abstract inspiration art

#### Contract metadata to bind during generation

Every asset should also carry:

- `template_id`
- `model_id`
- `seed`
- `style_variant`
- `lane`
- `persona`
- `topic`
- `brand_posture`
- `product_family`
- `proof_intent`
- `production_fidelity`

Per [BRAND_ADMIN_MEDIA_GENERATION_SPEC.md](./BRAND_ADMIN_MEDIA_GENERATION_SPEC.md), no asset should be marked `ready` without determinism metadata and QA pass data.

---

### Batch 1 — Mission (1)

#### 1) `mission_output_overview`

| Field | Value |
|-------|--------|
| **Use** | Flagship composite showing what the system makes |
| **Aspect** | 16:9 |
| **Product family** | `other` or split-composite registry logic |
| **Proof intent** | `ships_product` |
| **Production fidelity** | `pipeline_demo` until real composite export exists |

**Prompt**

> A premium composite presentation image showing a content generation system’s real outputs in one unified scene: several polished self-help book covers, one audiobook product tile, a set of social media reel or quote card assets, and one clean editorial news/article layout card, all arranged like a believable product showcase on a refined neutral background. The image should feel like a real SaaS or media platform output proof board, not a mood board. Distinct product categories must be instantly readable while still feeling cohesive. Elegant spacing, premium shadows, realistic surface treatment, subtle depth, clean editorial layout logic, believable publishing brand system, polished commercial product visual, premium publishing quality, clear focal hierarchy, visually believable, clean lighting, strong composition, modern editorial finish, realistic material treatment, production-ready, not abstract inspiration art.

---

### Batch 2 — Archetypes (5)

#### 2) `arch_nervous_system`

| Field | Value |
|-------|--------|
| **Aspect** | square or 4:3 |
| **Style intent** | calm vs overwhelm → relief |

**Prompt**

> A visually compelling cover-native scene representing nervous system regulation: a person moving from overwhelm into grounded calm, with the left side carrying subtle tension and overstimulation and the right side showing ease, breath, steadiness, and relief. The emotional arc must be readable instantly without feeling cheesy or clinical. Modern self-help publishing aesthetic, emotionally intelligent, soft but not weak, commercially viable, premium wellness product finish, polished commercial product visual, premium publishing quality, clear focal hierarchy, visually believable, clean lighting, strong composition, modern editorial finish, realistic material treatment, production-ready, not abstract inspiration art.

#### 3) `arch_identity_direction`

| Field | Value |
|-------|--------|
| **Style intent** | transition / path / forward motion |

**Prompt**

> A premium visual representing identity transformation and forward direction: one person in motion on a clear path, crossing from uncertainty into meaningful direction. The scene should suggest growth, purpose, and momentum without becoming motivational poster cliché. Strong sense of movement, horizon, trajectory, and self-definition. Commercially believable self-help cover aesthetic, polished commercial product visual, premium publishing quality, clear focal hierarchy, visually believable, clean lighting, strong composition, modern editorial finish, realistic material treatment, production-ready, not abstract inspiration art.

#### 4) `arch_emotional_healing`

| Field | Value |
|-------|--------|
| **Style intent** | warmth / softness / repair |

**Prompt**

> A deeply warm, emotionally restorative visual representing emotional healing and repair: softness, safety, gentleness, and inner restoration conveyed through environment, posture, and light. Must feel humane and elevated, not sentimental. Suitable for a premium self-help title about healing, grief, heartbreak, or self-compassion. Tender, grounded, soothing, commercially viable, polished commercial product visual, premium publishing quality, clear focal hierarchy, visually believable, clean lighting, strong composition, modern editorial finish, realistic material treatment, production-ready, not abstract inspiration art.

#### 5) `arch_performance_focus`

| Field | Value |
|-------|--------|
| **Style intent** | sharp / decisive / structured |

**Prompt**

> A high-clarity visual representing performance, focus, discipline, and structure: decisive atmosphere, controlled energy, cognitive sharpness, organized forward motion. The image should feel premium and strategic rather than corporate cliché. Suitable for productivity, leadership, discipline, or execution-oriented publishing. Clean lines, intelligent contrast, strong compositional control, polished commercial product visual, premium publishing quality, clear focal hierarchy, visually believable, clean lighting, strong composition, modern editorial finish, realistic material treatment, production-ready, not abstract inspiration art.

#### 6) `arch_spiritual_awakening`

| Field | Value |
|-------|--------|
| **Style intent** | luminous / contemplative |

**Prompt**

> A contemplative, luminous visual representing spiritual awakening and inner expansion: stillness, reverence, clarity, transcendence, and subtle radiance without fantasy excess. The scene should feel sacred, modern, and tasteful, appropriate for premium spiritual publishing. Quiet, elevated, emotionally resonant, commercially believable, polished commercial product visual, premium publishing quality, clear focal hierarchy, visually believable, clean lighting, strong composition, modern editorial finish, realistic material treatment, production-ready, not abstract inspiration art.

---

### Batch 3 — Systems (7)

These should look like **mini proof boards**, not abstract art.

#### 7) `sys_eois`

| Field | Value |
|-------|--------|
| **Meaning** | emotional state → content match |
| **Aspect** | 3:2 |

**Prompt**

> A mini proof board showing emotional-state-to-content matching inside a modern publishing/content system. Visually show a clean progression from audience emotional state to matched content outputs such as cover style, social card, and content lane. The board should feel like a product strategy board or SaaS proof visual, clean and real, with modular cards and believable design system structure. Premium UI-adjacent visual, clear logic, polished commercial product visual, premium publishing quality, clear focal hierarchy, visually believable, clean lighting, strong composition, modern editorial finish, realistic material treatment, production-ready, not abstract inspiration art.

#### 8) `sys_controlled_contrast`

| Field | Value |
|-------|--------|
| **Meaning** | tension → release flow |

**Prompt**

> A structured proof-board style visual illustrating controlled contrast in storytelling and product design: tension on one side, release on the other, showing how emotional contrast creates compelling content. Use clean modular card layout language, believable publishing examples, and a sophisticated strategic feel. This must look like a real system method being demonstrated, not conceptual art. Polished commercial product visual, premium publishing quality, clear focal hierarchy, visually believable, clean lighting, strong composition, modern editorial finish, realistic material treatment, production-ready, not abstract inspiration art.

#### 9) `sys_audiobook_dominance`

| Field | Value |
|-------|--------|
| **Meaning** | book → audio → platform |

**Prompt**

> A clean mini proof board showing a system that expands one core book concept into audiobook packaging and platform-ready promotional outputs. Visually communicate progression from book cover to audiobook tile to platform distribution or promo surface. Sophisticated, platform-native, modern digital publishing feel. Must look like real product proof from a media engine. Polished commercial product visual, premium publishing quality, clear focal hierarchy, visually believable, clean lighting, strong composition, modern editorial finish, realistic material treatment, production-ready, not abstract inspiration art.

#### 10) `sys_binge_loop`

| Field | Value |
|-------|--------|
| **Meaning** | chain of books / journey |

**Prompt**

> A premium proof board visualizing binge-loop publishing: one book leading naturally into another through thematic continuity, progression, and serial engagement. Show a chain or sequence of related covers and content states in a refined, strategic layout. Should feel like a real monetization/content architecture mechanism, not a vague metaphor. Polished commercial product visual, premium publishing quality, clear focal hierarchy, visually believable, clean lighting, strong composition, modern editorial finish, realistic material treatment, production-ready, not abstract inspiration art.

#### 11) `sys_social_wiring`

| Field | Value |
|-------|--------|
| **Meaning** | quote → share → viral |

**Prompt**

> A mini proof board showing how a core content idea becomes social-native assets: quote card, short-form visual, share behavior, attention loop. Show believable social media asset forms without copying any platform too literally. Should feel like a real growth system for publishing/media. Strategic, sharp, modern, commercially believable. Polished commercial product visual, premium publishing quality, clear focal hierarchy, visually believable, clean lighting, strong composition, modern editorial finish, realistic material treatment, production-ready, not abstract inspiration art.

#### 12) `sys_chaos_slot`

| Field | Value |
|-------|--------|
| **Meaning** | pattern break / surprise |

**Prompt**

> A proof-board style visual explaining the role of a pattern-break or chaos slot inside a content system: mostly structured outputs with one surprising, high-attention variation that disrupts sameness. The composition should clearly communicate disciplined system plus selective surprise. Must feel strategic and product-real, not playful randomness. Polished commercial product visual, premium publishing quality, clear focal hierarchy, visually believable, clean lighting, strong composition, modern editorial finish, realistic material treatment, production-ready, not abstract inspiration art.

#### 13) `sys_transformation_promise`

| Field | Value |
|-------|--------|
| **Meaning** | before vs after |

**Prompt**

> A premium mini proof board showing a transformation promise across publishing outputs: before state versus after state, mapped into believable book, social, or editorial product forms. The visual should communicate outcome clarity without cheesy before-and-after tropes. Clean, modern, emotionally legible, and product-truthful. Polished commercial product visual, premium publishing quality, clear focal hierarchy, visually believable, clean lighting, strong composition, modern editorial finish, realistic material treatment, production-ready, not abstract inspiration art.

---

### Batch 4 — Visual Identity (6)

These must look like **real covers**, per the real-example spec’s “real pipeline outputs” principle.

#### 14) `vi_calm`

| Field | Value |
|-------|--------|
| **Aspect** | 2:3 |
| **Style variant** | calm |

**Prompt**

> A premium self-help book cover visual with a calm identity: serene, spacious, regulated, elegant, emotionally safe, soft but not dull. Minimal but not empty. Designed to feel like a real bestselling modern wellness or overthinking-recovery book cover. High readability of form, refined restraint, polished commercial product visual, premium publishing quality, clear focal hierarchy, visually believable, clean lighting, strong composition, modern editorial finish, realistic material treatment, production-ready, not abstract inspiration art.

#### 15) `vi_dark`

**Prompt**

> A premium self-help or transformational nonfiction book cover visual with a dark identity: moody, intelligent, deep, dramatic, controlled, emotionally serious. Should feel premium and sophisticated, not horror, not fantasy. Suitable for shadow work, burnout, deep transformation, or intense personal growth. Real cover feel, polished commercial product visual, premium publishing quality, clear focal hierarchy, visually believable, clean lighting, strong composition, modern editorial finish, realistic material treatment, production-ready, not abstract inspiration art.

#### 16) `vi_earthy`

**Prompt**

> A premium book cover visual with an earthy identity: grounded, natural, human, textured, warm, quietly restorative. Suitable for healing, embodiment, nervous system regulation, or wholesome transformation. Must feel like a real marketable cover, not rustic décor art. Polished commercial product visual, premium publishing quality, clear focal hierarchy, visually believable, clean lighting, strong composition, modern editorial finish, realistic material treatment, production-ready, not abstract inspiration art.

#### 17) `vi_bold`

**Prompt**

> A premium nonfiction or self-help book cover visual with a bold identity: assertive, high contrast, confident, decisive, immediately noticeable in a storefront thumbnail. Strong impact without becoming cheap or loud. Feels like a real commercial winner for confidence, discipline, leadership, or action-oriented transformation. Polished commercial product visual, premium publishing quality, clear focal hierarchy, visually believable, clean lighting, strong composition, modern editorial finish, realistic material treatment, production-ready, not abstract inspiration art.

#### 18) `vi_premium`

**Prompt**

> A premium luxury-positioned self-help or transformational book cover visual: elevated, expensive-feeling, refined, highly intentional, tasteful, sophisticated. Should signal authority, quality, and aspirational emotional transformation. Must look like a real top-tier publishing output. Polished commercial product visual, premium publishing quality, clear focal hierarchy, visually believable, clean lighting, strong composition, modern editorial finish, realistic material treatment, production-ready, not abstract inspiration art.

#### 19) `vi_mysterious`

**Prompt**

> A premium self-help or spiritual-transformation book cover visual with a mysterious identity: intriguing, subtle, magnetic, atmospheric, emotionally open-ended, contemplative but still commercial. Should create curiosity without confusion. Real cover-native composition, polished commercial product visual, premium publishing quality, clear focal hierarchy, visually believable, clean lighting, strong composition, modern editorial finish, realistic material treatment, production-ready, not abstract inspiration art.

---

## B. Selection rubric

Use this after generating **3–5 candidates per slot**.

### Pass/fail gate first

Any candidate is immediately rejected if it has:

- distorted anatomy
- broken hands or face
- unreadable focal structure
- obvious AI artifacts
- mood-board vibe instead of product vibe
- wrong emotional archetype
- style drift from slot intent
- fake “concept art” feeling instead of deliverable output
- mismatch with lane/persona/topic/posture intent

This matches the media spec’s QA gate principle: contract fidelity, rendering quality, policy/format checks before `ready`.

### Weighted scorecard (100 pts)

| Category | Weight | What to ask |
|----------|--------|-------------|
| Contract fidelity | 25 | Does this actually match the slot’s intended lane/topic/posture/emotion? |
| Product realism | 20 | Does it feel like real system output, not inspiration? |
| Instant legibility | 15 | Can someone tell what it is in 2 seconds? |
| Commercial quality | 15 | Does it feel sellable / publishable / platform-ready? |
| Distinctiveness | 10 | Is it meaningfully different from sibling slots? |
| Emotional precision | 10 | Does it evoke the exact intended feeling? |
| Technical cleanliness | 5 | Is it artifact-free and polished? |

### Score interpretation

- **90–100** = approve
- **82–89** = approve if slot is weak elsewhere
- **75–81** = revision candidate
- **below 75** = reject

### Slot-specific emphasis

**Mission composite:** Prioritize (1) Product realism (2) Instant legibility (3) Commercial quality.

**Archetypes:** Prioritize (1) Emotional precision (2) Distinctiveness (3) Contract fidelity.

**Systems boards:** Prioritize (1) Instant legibility (2) Product realism (3) Contract fidelity.

**Visual identity covers:** Prioritize (1) Product realism (2) Commercial quality (3) Distinctiveness.

### Side-by-side winner selection method

For each slot:

**Round 1:** Generate 5.

**Round 2:** Delete obvious losers until 2 remain.

**Round 3:** Compare finalists on only these 4 questions:

1. Which one looks most like real product output?
2. Which one is most instantly understandable?
3. Which one best fits the intended emotion?
4. Which one still looks strong at thumbnail size?

Whichever wins 3/4 gets the slot.

### Portfolio-level normalization check

After choosing all winners, one final pass across the whole set:

1. **Tone consistency** — Do these feel like they came from the same system family?
2. **Range** — Do the 5 archetypes feel clearly different from each other?
3. **Commercial finish** — Do all 6 visual identity covers feel like real store-ready outputs?
4. **Proof truth** — Would a skeptical admin believe this came from your pipeline?

If not, regenerate the weak ones before shipping.

---

## C. Page roles and placement strategy

Aligned to [BRAND_ADMIN_ONBOARDING_PAGES_SPEC.md](../docs/BRAND_ADMIN_ONBOARDING_PAGES_SPEC.md): hero/supporting spine, gallery, matrix, proof strip, inline media, proof-pending fallback. Implementation should bind assets by registry id / `comparison_set_id` and render inline per pages spec.

### 1. `brand_admin_master_onboarding.html`

#### Hero section

| Slot | `mission_output_overview` |
|------|----------------------------|
| **Role** | Main “this system is real” hero visual |
| **Position** | Right side of hero on desktop; first media block below hero copy on mobile |

#### OutputProofStrip

Use these six as the first rotating or static strip:

- `vi_calm`, `vi_dark`, `vi_earthy`, `vi_bold`, `vi_premium`, `vi_mysterious`

| Field | Value |
|-------|--------|
| **Role** | Immediate proof that style variants create visibly different cover-native outputs |
| **Position** | Directly under “How the system works” or “What brand admins control” |

#### Compare lanes summary section

2×2 grid of system mini boards:

- `sys_eois`, `sys_controlled_contrast`, `sys_audiobook_dominance`, `sys_binge_loop`

#### Archetype explanation section

Five-card row or 2+3 grid:

- `arch_nervous_system`, `arch_identity_direction`, `arch_emotional_healing`, `arch_performance_focus`, `arch_spiritual_awakening`

**Note:** Supporting visuals; use `proof_intent: teaches_persona` or `teaches_topic` unless generated as direct cover outputs.

---

### 2. `lane_examples_gallery.html`

#### Featured section (top)

- `mission_output_overview` — anchor above lane sections.

#### Visual Identity comparison board

| Slots | All six `vi_*` |
|-------|----------------|
| **Grouping** | `comparison_set_id: cmp_visual_identity_v1` |
| **Registry tags** | `proof_intent: teaches_comparison`; `production_fidelity: pipeline_demo`; `product_family: book_engine` |

#### Archetypes board

| Slots | All five `arch_*` |
|-------|-------------------|
| **Grouping** | `comparison_set_id: cmp_archetypes_v1` |
| **Registry tags** | `proof_intent: teaches_comparison`; `production_fidelity: supporting_visual` unless tied to real output family; `product_family: other` or relevant family |

#### Systems board section

All seven `sys_*` boards. Recommended: section title **“Why outputs differ: the system logic underneath”** — either one section `cmp_systems_v1` or standalone explainer tiles.

**Registry tags:** `proof_intent: teaches_comparison`; `production_fidelity: supporting_visual` or `pipeline_demo` per literalism.

#### Lane section mapping (optional repeat)

| Lane | Suggested assets |
|------|------------------|
| Self-help | `vi_calm`, `vi_earthy`, `vi_premium`, `arch_emotional_healing`, `arch_identity_direction` |
| Audiobook | `sys_audiobook_dominance`, `vi_bold` or `vi_premium` |
| Manga | **None of these 19 as final manga proof.** Use a separate pack for manga sub-modes (cinematic, youth inspire, spiritual, healing, civic) per real-example spec. |
| Pearl News | `mission_output_overview`, `sys_social_wiring`, `sys_controlled_contrast` |
| Tools / funnel | `sys_eois`, `sys_transformation_promise`, `sys_chaos_slot` |

---

### 3. `market_lane_matrix.html`

Per pages spec, cells can include proof example links — enrich with **tiny thumbnail previews**, not text-only.

| Row / intent | Suggested thumbnail |
|--------------|----------------------|
| Self-help default | `vi_premium` |
| Audiobook | `sys_audiobook_dominance` |
| Pearl News | crop from `mission_output_overview` or future editorial hero |
| Tools | `sys_eois` |
| Emotional healing | `arch_emotional_healing` |
| Focus / performance | `arch_performance_focus` |

**UX:** Hover/click opens gallery anchor or lightbox/modal when available.

---

### 4. Wizard surfaces

Per [BRAND_ADMIN_ONBOARDING_WIZARD_SPEC.md](./BRAND_ADMIN_ONBOARDING_WIZARD_SPEC.md), visuals explain decisions; they do not compete with the contract.

| Surface | Slots |
|---------|--------|
| Style / posture step | All six `vi_*` |
| Persona / emotional fit | All five `arch_*` |
| System explainer / “what this changes” drawer | `sys_eois`, `sys_controlled_contrast`, `sys_binge_loop`, `sys_social_wiring`, `sys_transformation_promise` |
| Final confirmation / summary | `mission_output_overview` |

---

## Recommended registry starter shape

### Visual identity (example)

```json
{
  "id": "vi_calm_v1",
  "lane": "self_help",
  "market": "global",
  "locale": "en-US",
  "persona": "general_growth",
  "topic": "transformation",
  "format": "cover",
  "style_variant": "calm",
  "status": "planned",
  "proof_intent": "teaches_comparison",
  "production_fidelity": "pipeline_demo",
  "product_family": "book_engine",
  "source": "pipeline_demo",
  "comparison_set_id": "cmp_visual_identity_v1",
  "asset_path": "",
  "caption": "Calm style variant — cover-native output",
  "version": "v1",
  "created_at": "2026-04-01"
}
```

### Archetypes

- `format`: `persona_visual` or `topic_visual`
- `proof_intent`: `teaches_comparison`
- `production_fidelity`: `supporting_visual`

### Systems boards

- `format`: `audience_card` or a normalized label such as `system_board` (align with registry schema in [ONBOARDING_REAL_EXAMPLE_GENERATION_SPEC.md](./ONBOARDING_REAL_EXAMPLE_GENERATION_SPEC.md))
- `proof_intent`: `teaches_comparison`
- `production_fidelity`: `supporting_visual` or `pipeline_demo`

---

## Rollout order (recommended)

| PR | Content |
|----|---------|
| **A** | Registry rows for all 19 assets, all `planned` |
| **B** | Generate and approve: 6 visual identity + 5 archetypes + 1 mission composite |
| **C** | Wire those 12 into onboarding hero, output proof strip, gallery comparison boards, matrix thumbnails |
| **D** | Generate and wire the 7 systems boards |

---

## 11. What this pack is not

These 19 images are **Image Pack v1 — trust layer**. They do **not** satisfy the full long-term lane proof burden.

[ONBOARDING_REAL_EXAMPLE_GENERATION_SPEC.md](./ONBOARDING_REAL_EXAMPLE_GENERATION_SPEC.md) still requires differentiated examples across lanes (self-help, audiobook, manga, Pearl News, teacher, tools, youth civic), locked `cmp_*` sets (persona, locale, format, posture, manga mode), and honest `production_fidelity` / `source`. Treat this pack as accelerated trust and teaching coverage, not “onboarding proof complete.”
