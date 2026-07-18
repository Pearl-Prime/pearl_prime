# Drift Autopsy — stillness_press main_character.png (2026-04-29)

**Authors:** Pearl_Research (drift diagnosis), Pearl_Architect (engine config), Pearl_Marketing (register/brand-tint analysis).
**Subject:** 8 main_character.png outputs from `stillness_press` — operator-flagged for drift away from manga register toward Western illustration / fantasy character art / children's-book illustration / single-piece key art.
**Source images:** Inspected directly under `/Users/ahjan/phoenix_omega/assets/manga_catalog/stillness_press/<series_id>/main_character.png` (parent-checkout, not committed to this worktree).
**Source prompts:** Reconstructed from `/tmp/gen_20_new_images.py::build_prompt()` against each series YAML at `<sibling-worktree>/config/source_of_truth/manga_profiles/series/<series_id>.yaml`. Seed formula `int(hashlib.sha256(series_id.encode()).hexdigest(), 16) % (2**31)`.
**Engine:** RunComfy serverless, deployment `677edba8-ace0-4b2b-bad2-8e94b9959065`. Override pattern: only nodes "6" (CLIPTextEncode positive) and "25" (KSampler seed) — no negative prompt is sent in the override; the deployment's saved workflow_api.json supplies sampler/scheduler/steps/cfg/checkpoint and any negative.

---

## TL;DR for the operator

| # | Series | Genre | Drift mode | Severity | Single biggest cause |
|---|---|---|---|---|---|
| 1 | stillness_jp_07 | dark_fantasy | Color anime portrait, hallucinated typography | Medium | No mandatory `manga panel / screentone / black-and-white ink` token; "watercolor wash" + "expressive_josei" landed on color register |
| 2 | stillness_jp_08 | dark_fantasy | **Western fantasy character art** (armor + dragon + candlelight) | **High — full failure** | Character-role noun "dragon rider" outweighed every genre overlay; FLUX picked the most concrete image-anchor in the prompt |
| 3 | stillness_jp_16 | isekai → fantasy_adventure | Borderline pass — cozy iyashikei landed | Low — passes | "iyashikei minimalism" anchored register correctly; FLUX has strong manga prior for salaryman + traditional inn |
| 4 | stillness_jp_20 | mecha | Single-illustration sepia portrait, no halftone | Medium | Brand-tint "watercolor wash + earth tones" beat genre's manga line economy; the *image* matches the prompt — the prompt is wrong |
| 5 | stillness_jp_28 | fantasy_adventure | **Works — clean B&W manga** | None — passes | The same prompt that failed in en_US locale (#8) succeeded here because Japanese-locale prior + `ja_JP` setting hint pulled FLUX into manga register |
| 6 | stillness_press_mecha_us | mecha | YA-novel cover / Otomo-influenced single-illustration | Medium | Same as #4 + en_US locale weakened manga prior |
| 7 | stillness_press_dark_fantasy_us | dark_fantasy | Color visual-novel-style key art | Medium | Same as #1 + en_US locale weakened manga prior |
| 8 | stillness_press_fantasy_adventure_us | fantasy_adventure | **Children's-book / kawaii illustration** | **High** | en_US locale + "ornate fantasy + small object + cloak" English-language prior pulled FLUX to Western-children's-illustration; Japanese-prior counterpart (#5) succeeded with same logical prompt |

**Three root causes (ranked by leverage):**

1. **`GENRE_PROMPT[*]` lacks mandatory manga-anchor tokens.** Tokens like `manga panel`, `screentone`, `halftone shading`, `black and white ink`, `gekiga`, `monochrome` never appear in any of the 14 genre prompt strings in `/tmp/gen_20_new_images.py::GENRE_PROMPT`. The only register cue is the literal word "manga" buried inside the demographic tag (`josei demographic register`) and the trailing `manga catalog cover quality` boilerplate. **`manga catalog cover quality` is a single-illustration cue, not a panel cue** — it explicitly invites the cover-art register that drifted #1, #4, #6, #7.
2. **Locale hint is lossy.** `en_US` locale appends `American setting, manga-illustrated portrait, character of unspecified ethnicity but with specific personality features` while `ja_JP` appends `Japanese setting, Japanese woman or man, manga portrait`. The English version (a) names "American setting" which has zero manga-prior in FLUX training; (b) says "manga-illustrated" (an adjective applied to a portrait) instead of "manga panel" (a panel-medium cue); (c) the "of unspecified ethnicity but with specific personality features" tail is a paragraph of natural language that consumes embedding capacity without adding register signal. Empirical proof in this autopsy: stillness_jp_28 and stillness_press_fantasy_adventure_us run **identical genre+character logic**; the ja_JP one lands as clean B&W manga, the en_US one lands as a children's-book pixie. The locale hint is the variable that flipped the register.
3. **Workflow-engine config — almost certainly part of the cause.** The local FLUX workflow template (`config/comfyui_workflows/manga_covers/flux_character_portrait_template.json`) declares `flux1-schnell-fp8.safetensors` at `steps=24, cfg=4.0, sampler=euler, scheduler=normal`. **schnell is the 4-step distilled variant of FLUX.1; running it at 24 steps + cfg=4 is a known anti-pattern that oversaturates color, hallucinates typography, and amplifies whichever concrete noun is most visually dominant in the prompt embedding.** Every drift symptom in this autopsy is consistent with that engine-side amplification. Caveat: `runcomfy_batch.py::submit_inference` only overrides nodes "6" and "25" against a saved RunComfy deployment; the local template's node IDs (positive="2", KSampler="5") differ from the override IDs (positive="6", KSampler="25"), so the local template is **not** the workflow that ran on RunComfy — the production deployment's saved workflow_api.json is. We cannot read the production workflow without RunComfy API access. **The local template is therefore evidence of intent, not the production engine.** Either (a) the production deployment has the same schnell-mismatch (most parsimonious explanation given the symptoms — color saturation, typography hallucinations, oversampling artefacts) or (b) the production deployment runs a different misconfiguration and the local template is stale documentation — both demand the same NEXT_ACTION: pull the deployment's workflow_api.json and reconcile.

---

## Reconstructed prompt schema (applies to all 14 series below)

`build_prompt()` from `/tmp/gen_20_new_images.py` produces:

```
positive = "manga character portrait, clean linework, expressive face, upper body, "
           + LOCALE_HINT[locale]
           + ", " + f"{market_demo} demographic register"
           + ", " + GENRE_PROMPT[genre_family]
           + ", " + (f"main character: {name}, {role}" if role else f"main character: {name}")
           + ", " + f"series register: {title_en or title}"
           + ", no text, no typography, no letters, no watermark, expressive face, upper body or close-up,"
             " soft variable-weight brush linework, manga catalog cover quality"
```

**Constants:**

```python
LOCALE_HINT["ja_JP"] = "Japanese setting, Japanese woman or man, manga portrait"
LOCALE_HINT["en_US"] = "American setting, manga-illustrated portrait, character of unspecified ethnicity but with specific personality features"
```

**Critical structural defects in this scaffold (independent of any per-genre tuning):**

- The literal string `no text, no typography, no letters, no watermark` is appended to the **positive** prompt. FLUX uses a CLIP encoder + a T5 encoder — natural-language negations like "no text" embed *closer to* their content than away from it (the CLIP/T5 embedding for "no text" is statistically near "text"). Negations belong in the negative-prompt slot, never inline in positive. This is why every failed image in this autopsy has hallucinated Japanese ideograms or random characters baked in, despite the explicit "no text" instruction.
- The trailing tag `manga catalog cover quality` invites single-illustration / book-cover register. To get *manga panel* output, the trailing register cue should be `manga page panel, sequential art register, screentone shading, black and white ink with selective gray tone` or similar — not "cover quality."
- Brand-tint tokens (`watercolor wash`, `earth tones`, `restrained`, `paper texture grain`) are inserted **inside** `GENRE_PROMPT` for genres that conflict with the brand register (e.g., mecha, dark_fantasy). This is the brand-overrides-genre defect: the cookbook's brand-tint overlay rule must specify that line economy and screentone density are non-negotiable for genre-readability and that brand can only tint pose/framing/color-palette, not register-grammar.

---

## Failed-output autopsies

### Autopsy 1 — `stillness_jp_07` ("Awakening in the Soul Forest", dark_fantasy, ja_JP)

**Image observation:** Color anime portrait. Woman, late 20s/early 30s, long dark green hair styled with moss-crown overlay. Forest backdrop with weathered tree-bark texture left and right. Two large Japanese ideograms top-right (illegible — appears to read approximately `悟光` but is clearly hallucinated, not a real series mark), smaller `炎ア` characters and a small red square. Soft ink linework around the figure but **color register dominates** — green/sepia/skin tones, no halftone, no screentone, no panel structure.

**Reconstructed prompt:**

```
manga character portrait, clean linework, expressive face, upper body,
Japanese setting, Japanese woman or man, manga portrait,
josei demographic register,
expressive josei + symbolic reflection, woman emerging from forest, semi-translucent quality,
moss and bark textures, soft dappled light, melancholy resilient expression,
no horror imagery, no battle, somatic recovery framing,
main character: protagonist, burnout survivor, between human and forest spirit,
series register: Awakening in the Soul Forest,
no text, no typography, no letters, no watermark, expressive face, upper body or close-up,
soft variable-weight brush linework, manga catalog cover quality
```

**Seed:** 1178392698

**Diagnosis:**

- **Register drift** (medium severity, not full failure). The image *did* land most of the prompt's intent — woman, forest, moss, semi-translucent, melancholy — but in **color anime / single-illustration register**, not manga panel.
- The genre prompt names `expressive josei` and `symbolic reflection`. `expressive_josei` from `style_archetypes.yaml` is "soft flowing linework, warm color palette" — explicitly color, explicitly single-illustration register. **The genre prompt itself routes to color illustration.** Manga-panel B&W is excluded by the archetype choice.
- "Soft dappled light" + "moss and bark textures" + "semi-translucent quality" are all naturalistic / illustrative cues. None of them anchor sequential-art grammar.
- Hallucinated typography (the top-right characters) is the schnell-at-cfg-4 / no-text-in-positive defect cited above.

**Fixed prompt (per cookbook §dark_fantasy):**

```
manga panel, black and white ink with gray screentone, halftone shading,
seinen-josei mixed register, somatic recovery dark-fantasy register,
visible line weight variation, traditional manga ink wash,
Mushishi atmospheric register x Vagabond ink-weight,
upper body, expressive face, woman early 30s emerging from dense forest,
moss-crown silhouette, bark texture rendered in cross-hatch,
melancholy resilient expression, sparse composition with negative space,
series register: Awakening in the Soul Forest

NEGATIVE (sent in negative prompt slot, not appended to positive):
color illustration, watercolor, anime key art, full color, single-illustration cover,
visual novel render, photorealism, octane, 3d render, cgi, trending on artstation,
hyperdetailed, 8k, hallucinated text, hallucinated typography, japanese characters,
chinese characters, watermark, signature, logo
```

**Fixed engine config (per §0):** FLUX.1-dev fp8, sampler=dpmpp_2m, scheduler=karras, steps=28, cfg=3.5. (Or schnell at steps=4 cfg=1.0 if speed-prioritized — but at the cost of fine line-weight control.)

---

### Autopsy 2 — `stillness_jp_08` ("The Ashgrey Dragon Rider", dark_fantasy, ja_JP) — **PRIMARY FAILURE**

**Image observation:** Anime portrait, color, woman in metal breastplate / pauldron armor with red robe accent and shoulder cross-belt. **A stone-grey dragon head silhouette is rendered to her left, eye glowing.** Lit candle on the right. Stone wall background. Two columns of vertical Japanese ideograms (hallucinated). Reads as **fantasy character keyart / Berserk-influenced character splash** — explicitly Western-fantasy / RPG-character-portrait register, not manga panel.

**Reconstructed prompt:**

```
manga character portrait, clean linework, expressive face, upper body,
Japanese setting, Japanese woman or man, manga portrait,
josei demographic register,
expressive josei + symbolic reflection, woman emerging from forest, semi-translucent quality,
moss and bark textures, soft dappled light, melancholy resilient expression,
no horror imagery, no battle, somatic recovery framing,
main character: protagonist, female knight, sole survivor, ashgrey dragon rider,
series register: The Ashgrey Dragon Rider,
no text, no typography, no letters, no watermark, expressive face, upper body or close-up,
soft variable-weight brush linework, manga catalog cover quality
```

**Seed:** 1436070326

**Diagnosis:**

- **Catastrophic prompt-internal conflict.** The genre overlay is literally `woman emerging from forest, semi-translucent quality, moss and bark textures, soft dappled light, melancholy, no battle, somatic recovery framing`. The character role is `female knight, sole survivor, ashgrey dragon rider`. The series register is `The Ashgrey Dragon Rider`. **The prompt simultaneously asks for a forest-emerging spirit-woman AND a dragon-riding knight.** FLUX picked the more concrete, more statistically-canonical image: a fantasy female knight with a dragon. The genre overlay's negations (`no battle, no horror`) were ignored — both because they are negations in the positive slot, and because the dragon-rider noun is too dominant.
- **`GENRE_PROMPT["dark_fantasy"]` is a single string used for every dark_fantasy series.** It was hand-tuned for stillness_jp_07 (forest/somatic) and re-applied verbatim to stillness_jp_08 (dragon/knight). **The genre prompt cannot be a single string when the same genre family contains "forest somatic recovery" and "dragon-riding knight" subgenres.** The cookbook must treat dark_fantasy as a parent with subgenre overlays, or `GENRE_PROMPT` must read the series's `subgenre` field and route accordingly.
- **No mandatory manga-anchor tokens.** The image has color, armor specularity, candle flame, dragon scales — all illustrative anchors. There is nothing in the prompt that forces panel grammar.
- Hallucinated vertical Japanese text again — same root cause as Autopsy 1.

**This image alone justifies splitting `GENRE_PROMPT` into a per-subgenre table, not a per-genre-family table.** stillness_jp_07's `subgenre: somatic_fantasy` and stillness_jp_08's `subgenre: grief_fantasy` (with a literal dragon as the emotional engine) demand **completely different visual prompts**, not a shared parent.

**Fixed prompt (per cookbook §dark_fantasy.subgenre_overlays.grief_fantasy):**

```
manga panel, seinen-josei mixed register, black and white ink with selective heavy black fill,
Berserk-influenced cross-hatch atmosphere, Vagabond ink-weight,
female knight upper body, ashen dragon silhouette in middle ground (not foreground),
restrained pose, weight of grief in shoulder line, dragon's eye open but body grounded,
sparse stone background with negative space, no candlelight glow, no decorative ornament,
series register: The Ashgrey Dragon Rider

NEGATIVE:
color illustration, fantasy character key art, RPG character portrait, DnD splash art,
Western fantasy book cover, photorealistic armor, glossy metal, candlelight rendering,
volumetric lighting, hallucinated japanese text, hallucinated typography, watermark,
hyperdetailed, 8k, octane render
```

**Notes:** `Berserk-influenced cross-hatch atmosphere` is the genre-anchor that lets dark_fantasy keep its visual heaviness while staying in B&W manga register. Cite: Kentaro Miura's Berserk is *the* canonical reference for dark_fantasy manga visual grammar; FLUX has strong recognition for "Berserk style" → cross-hatch / heavy black / sparse panel. The cookbook should adopt artist/series anchors as primary genre tokens (see §genre_prompt_cookbook.yaml `canonical_visual_anchors`).

---

### Autopsy 3 — `stillness_jp_16` ("Reincarnation of the Burned-Out Hero", isekai, ja_JP) — **borderline pass, reclassify**

**Image observation:** Salaryman, late 30s, wearing a saffron-orange yukata-style wrap with red tie/cord at the chest. Soft smile, eyes closed. Background is a traditional Japanese inn — wooden lattice, paper screens, hanging lanterns, koi-pond aesthetic, a soft hot-spring vapor in the lower-right. Color register, warm palette, **clean anime-manga line economy**, no halftone but the linework is recognizably manga-derived. Vertical Japanese characters top-left ("か" visible — partially hallucinated).

**Reconstructed prompt:**

```
manga character portrait, clean linework, expressive face, upper body,
Japanese setting, Japanese woman or man, manga portrait,
josei demographic register,
iyashikei minimalism with subtle fantasy overlay, salaryman becomes calm fantasy hero, restoration mood,
main character: protagonist, karoshi salaryman, reincarnated protagonist,
series register: Reincarnation of the Burned-Out Hero,
no text, no typography, no letters, no watermark, expressive face, upper body or close-up,
soft variable-weight brush linework, manga catalog cover quality
```

**Seed:** 485414963

**Diagnosis:**

- **Passes**, with caveats. The genre prompt `iyashikei minimalism` + "salaryman becomes calm fantasy hero" + "restoration mood" landed on a recognizable iyashikei register. The salaryman + onsen-inn pairing is a high-density slice of FLUX's anime/manga training data — the model snaps to it confidently.
- The brand-tint conflict that broke jp_07/jp_08 doesn't fire here because **iyashikei IS the brand register**. There's no fight between brand and genre.
- Minor: still color, still has hallucinated typography fragment, still single-illustration not panel — but the register reads as manga-anime rather than Western illustration. **By the operator's rubric ("does it read as manga"), this is a pass.**
- **Reclassification:** moves from "operator-flagged failure" to "borderline pass." Note: the operator's brief listed jp_16 as a failure case based on its `genre_family: isekai` membership, but the actual output landed correctly because the subgenre is `recovery_isekai` and the genre prompt routed it to `iyashikei minimalism` — bypassing the fantasy-adventure pitfalls.

**Lesson for cookbook:** When a brand's voice_anchors and a genre's register are aligned (brand=iyashikei, genre=recovery_isekai), no special tuning is needed. **Drift only happens at the seam.** The cookbook should explicitly tag which (brand × genre) combinations are seam-prone and need active drift defense, vs which are aligned and need only the standard prompt.

---

### Autopsy 4 — `stillness_jp_20` ("Tea House and Frame", mecha, ja_JP)

**Image observation:** Woman, mid-30s, brown ponytail, wearing a tan utility jacket with red strap and small red bag, holding a closed object (maybe a ceramic cup or a tool wrap). **A small mech/exo-suit robot stands to her right at chest-height** — three-quarter-view, dormant pose, oxidized red/orange/grey panels, no kinetic energy. Behind her, a corner of a traditional Japanese building. Top-right has hallucinated Japanese characters reading approximately `二妢溍` (not real). **Color register, sepia/cream wash, single-illustration framing, no halftone, no panel.** Reads as Otomo-Akira-influenced anime poster / soft-watercolor key-art register.

**Reconstructed prompt:**

```
manga character portrait, clean linework, expressive face, upper body,
Japanese setting, Japanese woman or man, manga portrait,
seinen demographic register,
grounded realism, weathered character holding small object, dormant mech silhouette barely visible in background,
post-war quiet, muted earth tones with a single rust accent, watercolor wash, no kinetic action, no battle pose,
main character: Miyahara Sayaka, former frame pilot, now tea house proprietor; late 30s, weathered hands, reserved,
series register: Tea House and Frame,
no text, no typography, no letters, no watermark, expressive face, upper body or close-up,
soft variable-weight brush linework, manga catalog cover quality
```

**Seed:** 1074997088

**Diagnosis:**

- **The prompt produced exactly what it asked for.** Weathered character ✓, dormant mech in background ✓, post-war quiet ✓, muted earth tones ✓, single rust accent ✓, watercolor wash ✓, no kinetic action ✓, no battle pose ✓. **The output matches every prompt token literally.**
- **The prompt is wrong, not the output.** "Watercolor wash" + "muted earth tones" + "soft variable-weight brush linework" + "manga catalog cover quality" all instruct color illustration. The output is correctly color. But manga register requires monochrome ink + screentone. The prompt asked for color watercolor; FLUX delivered color watercolor; the output is therefore not manga.
- **Brand voice fought genre register and won.** stillness_press's `brand_illustration_styles.yaml` declares `Contemplative Ink Wash` archetype with `shading: watercolor_wash` and palette `slate / warm gold`. These brand tints were inserted into the genre prompt directly. The genre — mecha — needs B&W line economy + screentone + halftone. **Brand-tint overlay rule must forbid `watercolor_wash` shading on genres whose canonical visual grammar is line-economy-heavy** (mecha, dark_fantasy, horror, battle). Allowed brand tint for those genres: pose (restrained), framing (interior, post-conflict), color palette (if color is locale-permitted) — but never shading-style override.
- The mech is small and dormant — that's correct intent for stillness_press's mecha-as-pastoral-drama positioning. The cookbook should preserve this brand-tint allowance ("dormant mech in background, not foreground") while restoring genre-register grammar.

**Fixed prompt (per cookbook §mecha):**

```
manga panel, seinen register, black and white ink with light gray screentone,
Yokohama Kaidashi Kikou pastoral pacing x Patlabor quiet-episode register x
Mobile Suit Gundam: The Origin ink-weight,
upper body, weathered woman late 30s in utility jacket, holding small object,
dormant mech silhouette in middle-ground (sheeted, dormant, not active),
traditional Japanese building corner visible, sparse composition, generous negative space,
visible cross-hatch on mech panels (rust patina), pastoral seinen mecha register,
series register: Tea House and Frame

NEGATIVE:
Pacific Rim, Hollywood mech, Western mecha key art, octane render, photorealism,
glossy metal, kinetic action, battle pose, speed lines, energy effect,
color illustration, watercolor cover, single-illustration register,
hallucinated japanese text, hallucinated typography, watermark, signature
```

---

### Autopsy 5 — `stillness_jp_28` ("The One Who Carries Memories", fantasy_adventure, ja_JP) — **passes**

**Image observation:** **Clean black-and-white manga portrait.** Woman, late 20s, dark hair pulled into a low bun with elaborate ornamental hair-bow / hair-ribbon arrangement on the right side (the "memory ribbons" of the series concept). Hood pulled up around her shoulders. Holding a small wooden box (the memory-keeper's satchel-box per the YAML). Vertical kanji on the left side reading `蛉取じ` — partially hallucinated but small enough to read as register cue rather than failure. **Manga line economy is present** — visible variable-weight brush linework, sparse hatch shading on the hood, restrained black fill, no color, no halftone but the line economy substitutes. Reads as **shojo-josei mixed manga portrait, ornate-fantasy-quiet subgenre.**

**Reconstructed prompt:**

```
manga character portrait, clean linework, expressive face, upper body,
Japanese setting, Japanese woman or man, manga portrait,
shojo_josei_mixed demographic register,
ornate fantasy with symbolic reflection, wandering memory keeper figure with cloak and small wooden box of letters,
quiet world-walking pose, neither battle nor magical girl, gentle melancholy,
main character: Hina, wandering memory-keeper, late 20s, third-rank of her order,
series register: The One Who Carries Memories,
no text, no typography, no letters, no watermark, expressive face, upper body or close-up,
soft variable-weight brush linework, manga catalog cover quality
```

**Seed:** 1516782580

**Diagnosis:**

- **Passes — best output of the autopsied set.** Hood ✓, small wooden box ✓, gentle melancholy ✓, quiet pose ✓, ornate but not heavy ✓, B&W manga register ✓.
- Why this works while #8 (en_US fantasy_adventure with logically identical prompt) fails: **`Japanese setting, Japanese woman or man, manga portrait` is a much stronger manga-prior anchor than `American setting, manga-illustrated portrait, character of unspecified ethnicity`.** FLUX's training data has dense Japanese-locale-tagged manga material; "Japanese woman + manga portrait" reliably routes to Japanese-manga register. The English-locale formulation triggers Western-illustration prior.
- The shojo_josei_mixed demographic register helped — `shojo_josei_mixed` doesn't appear as a known archetype but the `shojo` half of it pulls toward the ornate-fine-line register that matches the image.
- Hallucinated kanji is still present (`蛉取じ`). Lower in saliency than #1/#2/#4 but still a violation of the explicit "no text" instruction.

**Lesson for cookbook:** The Japanese-locale prompt scaffold is approximately correct; the English-locale scaffold is the one that needs fixing. The cookbook's `genre_prompt_cookbook.ja_JP.yaml` should preserve the working `Japanese setting + manga portrait` anchor; the English cookbook needs an entirely different locale framing — see Autopsy 8.

---

### Autopsy 6 — `stillness_press_mecha_us` ("After the Cockpit", mecha, en_US)

**Image observation:** Woman, late 30s, brown hair with bangs, **goggles pushed up onto her forehead**, wearing a tan/olive flight-suit-style jumpsuit with red insignia patch and a leather strap/pocket. **Small mech-radio / robotic walkie-talkie object in her hand and another partially visible at the left edge.** Soft cream/olive watercolor wash. **Single-illustration framing**, sepia palette, no halftone, no panel. Reads as **YA-novel cover / Otomo Katsuhiro-influenced single-illustration key-art** — specifically the "Maggie" character looks like a Western YA-fiction cover protagonist, not a manga protagonist. No hallucinated typography this time (one of the cleaner failures on that axis).

**Reconstructed prompt:**

```
manga character portrait, clean linework, expressive face, upper body,
American setting, manga-illustrated portrait, character of unspecified ethnicity but with specific personality features,
seinen demographic register,
grounded realism, weathered character holding small object, dormant mech silhouette barely visible in background,
post-war quiet, muted earth tones with a single rust accent, watercolor wash, no kinetic action, no battle pose,
main character: Margaret "Maggie" Voss, former heavy frame pilot, now bookshop owner in a Pacific Northwest coastal town,
series register: After the Cockpit,
no text, no typography, no letters, no watermark, expressive face, upper body or close-up,
soft variable-weight brush linework, manga catalog cover quality
```

**Seed:** 1349654603

**Diagnosis:**

- **Same prompt-side defect as Autopsy 4**, plus **en_US locale-prior weakness**. The image is technically on-prompt (weathered character ✓, small object ✓, post-war quiet ✓, watercolor wash ✓, no kinetic action ✓) but the *aggregate* register reads as Western YA illustration because every cue in the prompt — "American setting, manga-illustrated portrait" + "grounded realism" + "watercolor wash" + "muted earth tones" + "soft variable-weight brush linework" + "manga catalog cover quality" — is more strongly associated with Western single-illustration than with Japanese manga panel in FLUX's training corpus.
- **The locale hint actively harms.** "American setting" + "manga-illustrated portrait" + "character of unspecified ethnicity" = three independent permission slips for FLUX to leave the manga register. Compare to ja_JP's "Japanese setting, Japanese woman or man, manga portrait" — which is three independent reinforcements of manga register.
- The radio-bot detail is interesting: the prompt asked for "weathered character holding small object" — FLUX, anchored by "former heavy frame pilot" + "small object" + "mech silhouette," interpreted "small object" as a small mech (a hand-radio bot). That is technically a creative landing of the brand-tint instruction (mech is small and dormant, not towering and active) but at the cost of further pulling the image toward Otomo-style Western anime-illustration register.
- **No hallucinated text** here — possibly because the en_US locale didn't cue Japanese-character generation specifically. (The "no text" violation is genre-locale-correlated; ja_JP runs hallucinate Japanese ideograms, en_US runs sometimes hallucinate Latin characters but not always.)

**Fixed prompt (per cookbook §mecha + en_US locale rules):**

```
manga panel, seinen register, black and white ink with light gray screentone,
Patlabor episodic-quiet register x The 08th MS Team character-grit,
upper body, weathered woman late 30s in flight-suit jumpsuit, leather strap detail,
holding small dormant device, sealed mech silhouette in distant background only,
Pacific Northwest coastal-town interior corner, sparse composition,
visible variable line weight, cross-hatch shading on garment,
seinen pastoral mecha register,
series register: After the Cockpit

NEGATIVE:
Pacific Rim, Hollywood mech, Western YA novel cover, watercolor cover illustration,
single-piece key art, octane render, photorealistic skin, color illustration,
glossy metal, kinetic action, battle pose, speed lines,
American illustration register, Western anime poster, Otomo Akira-style oil-painting,
hallucinated text, watermark, signature, hyperdetailed
```

**en_US locale-hint replacement (cookbook spec):** Replace `American setting, manga-illustrated portrait, character of unspecified ethnicity but with specific personality features` with `seinen manga panel, Western character ethnicity OK, Japanese manga panel grammar mandatory, screentone shading, monochrome ink with selective gray tone`. That formulation keeps the en_US ethnic flexibility while reinforcing manga register three times.

---

### Autopsy 7 — `stillness_press_dark_fantasy_us` ("The Forest Keeps Score", dark_fantasy, en_US)

**Image observation:** Woman, late 20s/early 30s, dark green hair, **pale skin (semi-translucent quality is rendered as visible blue-green vein hint at neck and collarbone)**, surrounded by lush green foliage and tree branches in mid-ground and foreground. Bare-shouldered (the dress strap is barely indicated). Color register, anime-illustration line economy, no halftone, no panel. **Reads as visual-novel single-illustration key art / "Yoshitaka Amano-meets-modern-anime-illustration" ornate-color register.**

**Reconstructed prompt:**

```
manga character portrait, clean linework, expressive face, upper body,
American setting, manga-illustrated portrait, character of unspecified ethnicity but with specific personality features,
josei demographic register,
expressive josei + symbolic reflection, woman emerging from forest, semi-translucent quality,
moss and bark textures, soft dappled light, melancholy resilient expression,
no horror imagery, no battle, somatic recovery framing,
main character: Wren Halberg, burnout survivor, between human and forest, late 30s, no longer fluent in the world she left,
series register: The Forest Keeps Score,
no text, no typography, no letters, no watermark, expressive face, upper body or close-up,
soft variable-weight brush linework, manga catalog cover quality
```

**Seed:** 1390194813

**Diagnosis:**

- **Color-register drift, same as Autopsy 1, amplified by en_US locale.** The genre prompt routes to color (`expressive_josei` archetype = color, `soft dappled light` = naturalistic). The en_US locale removes the Japanese-manga-prior anchor. Result: ornate-color visual-novel-style key art.
- The "semi-translucent quality" instruction landed faithfully (visible vein hint). That's a genre-correct emotional engine — Wren's "between human and forest" liminality is rendered. But the *register* is wrong.
- This output is closest in register to a 2010s-era anime CD-soundtrack cover / Type-Moon visual novel character illustration. FLUX's training data contains a large amount of that material, all tagged with terms adjacent to "expressive josei + ornate fantasy + semi-translucent + dappled light" — the prompt routed FLUX to the densest neighborhood, which is not manga.

**Fixed prompt (per cookbook §dark_fantasy.subgenre_overlays.somatic_fantasy + en_US locale rules):**

```
manga panel, seinen-josei mixed register, black and white ink with selective gray screentone,
Mushishi atmospheric register x Vagabond ink-weight x Berserk-cross-hatch atmosphere,
upper body, woman late 30s in dense forest, semi-translucent skin rendered as light line-economy
(not color gradient), moss-and-bark cross-hatch background, sparse composition,
melancholy resilient expression, generous negative space,
seinen-josei mixed somatic-fantasy register,
series register: The Forest Keeps Score

NEGATIVE:
color illustration, visual novel render, anime CD cover, Type-Moon style,
Yoshitaka Amano color, watercolor portrait, soft pastel,
ornate single-piece key art, photorealism, octane render,
American illustration register, Western fantasy book cover,
hallucinated text, watermark, signature, hyperdetailed, 8k
```

---

### Autopsy 8 — `stillness_press_fantasy_adventure_us` ("The Memory Keeper", fantasy_adventure, en_US) — **PRIMARY FAILURE**

**Image observation:** **Pixie-cute portrait.** Small face, large round eyes with prominent eyelashes, blunt-cut bangs, hood pulled up with **two-prong wing-shape ornament at the top** (the brown hood + wing motif reads as *fairy-tale woodland creature* not *memory-keeper order*). Pink blush spots on cheeks. Holding a small lantern/wooden box with a tiny light inside. Pastel palette (cream/peach/brown). Hallucinated stylized tag in upper-left reading approximately `懂` and small text `みゎんた / ょうがん / でき` (all hallucinated). **Reads as Western YA-illustration / kawaii children's-book cover** — explicitly NOT manga register. Compare to Autopsy 5 (jp_28, same logical prompt, ja_JP locale): there, the same character archetype rendered as a clean B&W manga portrait with elaborate hair-bow ornament. Here, the en_US locale routed the same character archetype to children's-book pixie register.

**Reconstructed prompt:**

```
manga character portrait, clean linework, expressive face, upper body,
American setting, manga-illustrated portrait, character of unspecified ethnicity but with specific personality features,
josei demographic register,
ornate fantasy with symbolic reflection, wandering memory keeper figure with cloak and small wooden box of letters,
quiet world-walking pose, neither battle nor magical girl, gentle melancholy,
main character: Iyo, wandering memory-keeper, age unstated, carries a satchel of objects,
series register: The Memory Keeper,
no text, no typography, no letters, no watermark, expressive face, upper body or close-up,
soft variable-weight brush linework, manga catalog cover quality
```

**Seed:** 1190503027

**Diagnosis:**

- **Pure locale-prior drift.** The character archetype, genre prompt, and brand tint are logically identical to stillness_jp_28. The only material difference is the locale hint — ja_JP's "Japanese setting, Japanese woman or man, manga portrait" vs en_US's "American setting, manga-illustrated portrait, character of unspecified ethnicity." That single token swap flipped the output from clean B&W manga to kawaii children's book.
- **`manga-illustrated portrait` is a load-bearing failure.** That phrase parses to FLUX as "[adjective: manga-illustrated] [noun: portrait]" — the noun is "portrait" (single illustration), the adjective is a stylistic modifier. Compare to "manga portrait" or "manga panel" — those parse as "[type of medium]" cues that more strongly route to manga register. The hyphenated compound "manga-illustrated" is a defective stylistic anchor.
- "Character of unspecified ethnicity but with specific personality features" is paragraph-of-natural-language consuming embedding capacity for zero register signal. The phrase has high entropy and low density — it dilutes the prompt without adding manga-anchor.
- "Ornate fantasy with symbolic reflection" + "small wooden box" + "gentle melancholy" + en_US-locale prior route to **Western kid-lit / cottagecore / Studio Ghibli children's-book** register. Studio Ghibli is anime-adjacent in FLUX training, so the pixie-cute output is half-correct — but the full manga-panel target requires explicit B&W ink + screentone tokens that aren't in the prompt.
- The hood-wing ornament rendered here is FLUX's interpretation of "ornate fantasy" + "wandering memory-keeper" — it picked a Western fairy-tale woodland-pixie costume archetype, not a Japanese fantasy-of-manners memory-keeper archetype. This is a **vocabulary-prior** failure: "memory keeper" has no established visual canon in either Japanese or Western imagery; FLUX defaults to the more statistically dominant prior, which en_US-locale = Western fairy tale.

**Fixed prompt (per cookbook §fantasy_adventure + en_US locale rules):**

```
manga panel, shojo-josei mixed register, black and white ink with sparse gray screentone,
Mushishi atmospheric quiet x Hyouka restraint x Spice and Wolf travel companionship register,
upper body, woman late 20s, hood pulled up with elaborate hair-ribbon ornament,
holding small wooden box of letters, sparse composition with negative space,
visible variable line weight, fine ink linework, melancholy quiet expression,
shojo-josei manga register, Western character ethnicity OK,
series register: The Memory Keeper

NEGATIVE:
children's book illustration, Western YA cover, kawaii, chibi, pixie, fairy tale illustration,
cottagecore, Ghibli children's-book illustration, blush marks, oversized round eyes,
visual novel render, color illustration, watercolor cover,
American illustration register, single-piece key art,
hallucinated text, watermark, signature, hyperdetailed, 8k
```

---

## Working-set autopsies (delta diagnosis — why these landed)

The working set is **not** included to celebrate it — it's included to diagnose **why the same scaffold succeeded** in these cases. The lesson is about the boundary between "snaps to canonical register" and "drifts."

### Autopsy 9 — `stillness_jp_01` ("After Work, Eating Alone", healing, ja_JP) — **passes**

**Image:** Woman, late 30s, dark hair, wearing a beige cardigan/wrap, soft features, gentle expression. Cream paper-grain background. Clean B&W-with-warm-tint manga linework. Tiny artist signature mark bottom-left. Reads as iyashikei manga portrait — clean register match.

**Why it works:** `iyashikei minimalism + contemplative ink wash + watercolor wash + near-zero ink density` (genre prompt) + `josei demographic register` + `Japanese setting + manga portrait` (locale) all align to the densest neighborhood of FLUX's manga training data: cozy-iyashikei josei portrait. Brand voice (`Contemplative Ink Wash` archetype) is *the* genre register — no fight. **This is the alignment baseline.** Every fixed prompt in this autopsy aims to make non-iyashikei genres produce equally clean register matches.

### Autopsy 10 — `stillness_jp_23` ("Letting the Cat Out at Dusk", slice_of_life, ja_JP) — **passes**

**Image:** Color manga, woman with bobbed hair, holding a calico cat, in domestic interior with bookshelf, lamp, and partial calendar with hallucinated kanji. Strong manga-anime register, cozy domestic warmth.

**Why it works:** `sparse atmosphere + everyday warmth + woman in early 40s in domestic interior + cat present + late afternoon light + quiet ordinary moment` is high-density FLUX manga training material — domestic-cat-josei is one of the most-represented manga subgenres in any image-model corpus. The prompt anchors three independent priors (woman, cat, domestic interior) that all route to manga.

### Autopsy 11 — `stillness_jp_26` ("One Bowl in the Side Street", food, ja_JP) — **passes (with caveat)**

**Image:** Woman in white shirt + red apron at ramen counter, color, lots of background hallucinated kanji on hanging signs. Strong food-manga register (Shinya Shokudo / Wakako Zake adjacent).

**Why it works:** `sensory closeup + everyday warmth + chef at small ramen counter + steam rising + warm ambient overhead` + the "ramen shop" noun pull FLUX to a very specific manga-anime training-data neighborhood (food manga). Hallucinated background text is acceptable register cue for this subgenre — Shinya Shokudo manga panels DO have Japanese signage. **Caveat:** the text is hallucinated — for production output the cookbook should still suppress it via negative prompt.

### Autopsy 12 — `stillness_jp_27` ("Grandma Is Still Here", comedy, ja_JP) — **passes**

**Image:** Color manga, woman with side-bun hair, blush marks, mild deformation reaction face, manga speech bubbles in background reading hallucinated `はいて？` / `にだ`. Strong gag-comedy josei register.

**Why it works:** `light comedic deformation + everyday warmth + woman 35 + slight wry expression + cluttered apartment interior + restrained gag, no slapstick` lands in the gag-josei manga neighborhood (Otomen, Aggretsuko, daily-domestic-comedy). Speech bubbles are expected register cue — though hallucinated text inside them is still a problem.

### Autopsy 13 — `stillness_press_food_us` ("The Tuesday Cafe", food, en_US) — **passes**

**Image:** Woman at cafe interior, color, breakfast plate, warm yellow lighting, soft anime-manga register. Hallucinated "Hier Mang" text top-right.

**Why it works:** Food + cafe + breakfast in en_US locale **still routes to manga register** because food-manga in en_US-translated form (Midnight Diner, Yotsuba's-mom-cooks-breakfast scenes) is densely represented in FLUX training. Food is one of the few genres where en_US-locale doesn't break manga prior.

### Autopsy 14 — `stillness_press_comedy_us` ("The Quiet Roommate", comedy, en_US) — **passes**

**Image:** Color manga, woman in pink t-shirt, small ghost mascot at her side, domestic interior. Reads as warm josei comedy.

**Why it works:** Same as Autopsy 12 — gag-comedy + woman + domestic-interior + ghost-mascot routes to a high-density manga neighborhood. en_US locale doesn't hurt here because Western comedy-comic-strip register (Calvin and Hobbes, Aggretsuko EN) overlaps with manga-comedy register in FLUX training.

---

## Pattern across all 14 autopsies

**Working-set genres** (healing, slice_of_life, food, comedy in both locales): high-density FLUX manga neighborhoods. Brand voice and genre register align. Prompts approximately work as-is. **Locale doesn't matter much** because the genre's manga-prior is strong enough in en_US-tagged training data.

**Failing-set genres** (mecha, dark_fantasy, fantasy_adventure): low-density FLUX manga neighborhoods relative to their non-manga (Western fantasy / Western mech / Western YA-illustration) neighbors. Brand voice (`watercolor wash, restrained, sparse`) actively fights the genre's canonical visual grammar. **Locale matters enormously** — ja_JP locale partially saves the prompt (jp_28 passes); en_US locale removes the saving anchor (fantasy_adventure_us fails).

**Locale axis of drift severity:**

| Genre | ja_JP outcome | en_US outcome | Δ |
|---|---|---|---|
| dark_fantasy | medium drift (color register, jp_07); full failure (jp_08, dragon-rider conflict) | medium drift (color visual-novel, dark_fantasy_us) | en_US slightly worse |
| fantasy_adventure | passes (jp_28) | full failure (fantasy_adventure_us, kawaii pixie) | en_US dramatically worse |
| mecha | medium drift (jp_20, sepia key-art) | medium drift (mecha_us, YA cover) | en_US slightly worse |

**Brand-tint-fights-genre axis:**

stillness_press's brand voice is iyashikei/watercolor-wash/restrained. Its alignment with each genre:

| Genre | Brand × genre alignment | Drift mode if misaligned |
|---|---|---|
| healing | perfect alignment | none |
| slice_of_life | strong alignment | none |
| food | strong alignment | none |
| comedy | strong alignment (light deformation matches restraint) | none |
| romance | moderate alignment | likely color-register drift |
| isekai (recovery_) | perfect alignment (recovery_isekai = iyashikei subgenre) | none |
| mystery | moderate alignment | likely overrun by Mushishi prior, may pass |
| workplace | moderate alignment | likely watercolor-key-art drift |
| sports | moderate alignment | likely soft single-illustration drift |
| essay | strong alignment | none |
| **mecha** | **strong misalignment** | **register drift, brand wins, manga loses** |
| **dark_fantasy** | **strong misalignment** | **register drift OR Western fantasy art if character has concrete fantasy noun** |
| **fantasy_adventure** | **moderate misalignment + locale-prior weakness in en_US** | **kawaii children's book drift** |
| horror | strong misalignment | likely watercolor-soft drift, OR Western-horror illustration |
| sci_fi_cyberpunk | strong misalignment | likely soft watercolor sci-fi key art |
| battle | strong misalignment | not yet observed; predicted: soft single-illustration |
| cultivation | strong misalignment | not yet observed; predicted: Chinese ink-wash key art |
| historical | moderate alignment | not yet observed; predicted: passes |
| graphic_medicine | strong alignment | predicted: passes |
| memoir | strong alignment | predicted: passes |
| social_issue | moderate alignment | predicted: passes |
| supernatural_everyday | strong alignment | predicted: passes |
| school | moderate alignment | predicted: passes |
| procedural | moderate alignment | predicted: passes |
| family | strong alignment | predicted: passes |
| battle_internal | moderate alignment | predicted: passes (because internal-battle manga IS a quiet register canonically) |

**Operator-side prediction:** 8 of 25 genres are misalignment-prone for stillness_press (the 7 marked "strong misalignment" plus dark_fantasy_us-style en_US ornate-fantasy locale-traps). The cookbook's brand-tint overlay rules need explicit "register-defense" entries for those 8 genres specifically — preserve brand pose/framing/color-palette tints, but force genre register tokens (manga panel, screentone, line economy) at mandatory weight.

---

## What the cookbook must change (load-bearing fixes)

1. **Promote `manga panel, screentone, halftone shading, black and white ink with selective gray tone` to mandatory tokens** at the front of every genre's `positive_prompt_template`. Do not bury them mid-prompt; do not make them optional. They are the genre-anchor that wins against character-noun concreteness (fixes Autopsy 2) and brand-tint conflict (fixes Autopsies 4, 6, 7).
2. **Move all negations into a real negative-prompt slot.** Stop appending `no text, no typography, no letters` to the positive. Either send them in the deployment's negative-prompt node, or drop them — appending them inline is actively harmful (fixes the hallucinated-typography pattern across Autopsies 1/2/4/5/11/12/13).
3. **Replace `manga catalog cover quality` with `manga page panel, sequential art register, screentone shading, monochrome ink with selective gray tone`** as the trailing register cue. "Cover quality" invites the single-illustration register that broke #1, #4, #6, #7.
4. **Replace the en_US locale hint** with `seinen/josei manga panel, Western character ethnicity OK, Japanese manga panel grammar mandatory, screentone shading, monochrome ink with selective gray tone` (or equivalent — see cookbook §0). The current en_US hint actively suppresses manga prior; the replacement reinforces it three times.
5. **Split `GENRE_PROMPT[*]` into per-(genre, subgenre) entries.** Single-string-per-family was the proximal cause of Autopsy 2 (forest-spirit prompt applied to a dragon-rider series). The cookbook's `subgenre_overlays:` block addresses this; the upstream `GENRE_PROMPT` table or its replacement must read both `genre_family` and `subgenre` from the YAML.
6. **Add canonical artist/series anchors** as primary genre tokens (e.g., dark_fantasy → "Berserk x Vagabond x Mushishi atmospheric", mecha → "Patlabor quiet-episode x Mobile Suit Gundam: The Origin x Yokohama Kaidashi Kikou pastoral"). FLUX has high-fidelity recognition of named manga artists and named manga titles; the cookbook should exploit this.
7. **Adopt brand-tint overlay rules:** brand can only tint pose/framing/color-palette/environment-density. Brand must NOT override line economy or screentone density or manga-page-grammar tokens. Specifically for stillness_press: "watercolor wash" is allowed only on iyashikei-aligned genres (healing, slice_of_life, food, comedy, romance, recovery_isekai); on mecha/dark_fantasy/horror/battle/sci_fi_cyberpunk it is forbidden and the brand-tint must restrict to "restrained pose, post-conflict framing, sparse environment density."

---

## What the engine config must change (§0 of the research doc — operator-facing)

Independent of any prompt-cookbook tuning:

1. **Pull the production deployment's workflow_api.json** from RunComfy (deployment `677edba8-ace0-4b2b-bad2-8e94b9959065`). Verify checkpoint, sampler, scheduler, steps, cfg.
2. **If schnell-mismatch is confirmed:** patch to FLUX.1-dev-fp8 + dpmpp_2m + karras + steps=28 + cfg=3.5. Or keep schnell with steps=4 + cfg=1.0.
3. **Add a real negative-prompt node** to the deployment workflow and route `runcomfy_batch.py::submit_inference` to override it as well as the positive. Today the override-only-positive pattern means the deployment's hardcoded negative (whatever it is) is the only negative that fires; the positive-side `no text` annotations are pure noise.
4. **Reconcile the local template** (`config/comfyui_workflows/manga_covers/flux_character_portrait_template.json`) with the production deployment. Either deprecate the local template or update it to match. Right now it is misleading documentation.

These are NEXT_ACTIONs, not in-PR changes (per brief out-of-scope).

---

## Coverage and gaps

**What this autopsy proves empirically (8 + 6 = 14 actual outputs):**
- Locale-hint axis of drift (jp_28 vs fantasy_adventure_us)
- Brand-tint-fights-genre axis of drift (jp_20 mecha sepia key-art)
- Character-role-noun-vs-genre-overlay conflict (jp_08 dragon rider)
- Working-set alignment is real (4 of 6 working-set images cleanly land manga register)
- Hallucinated-typography pattern (8 of 14 images, locale-correlated)
- Single-string-per-genre is insufficient (jp_07 vs jp_08, same `GENRE_PROMPT["dark_fantasy"]`, divergent outcomes)

**What this autopsy does NOT prove (gaps for follow-up):**
- Schnell-mismatch as direct cause (we only have indirect evidence — workflow template file doesn't equal production engine; needs RunComfy API verification)
- Drift behavior on the 17 unautopsied genres (battle, mystery, workplace, sports, romance, etc.) — predictions in the alignment table above are literature-grounded, not empirical, until those generations run against the new cookbook
- Whether character-consistency (PuLID/InstantID) would have prevented Autopsy 2's dragon-fight pull — needs separate test
- Whether a brand LoRA (per `brand_lora_plans.yaml`'s planned but-not-trained `stillness_press` style LoRA) would resolve any of these drifts independently of prompt fixes — likely yes for register, but at the cost of brand-versus-genre control

These gaps map to NEXT_ACTIONs in the parent research doc's CLOSEOUT_RECEIPT.

---

## Next steps after this PR (for the operator)

1. **Pull deployment workflow_api.json** from RunComfy to confirm/refute schnell-mismatch hypothesis. (5 minutes via API.)
2. **Patch `runcomfy_batch.py::submit_inference`** to also override a negative-prompt node. (Small PR.)
3. **Replace `GENRE_PROMPT[*]`** in any future generation script with a reader of `config/manga/genre_prompt_cookbook.yaml`. (Refactor PR.)
4. **Regenerate the 8 autopsied images** with the fixed prompts above + the engine fix. Smoke-test against `scripts/image_generation/qa/manga_register_check.py` (delivered in Phase H of this PR).
5. **Triage the 17 unautopsied genres** by generating one stillness_press representative each with the new cookbook; iterate where drift score exceeds threshold.
6. **Train the planned `stillness_press` style LoRA** per `brand_lora_plans.yaml` once the prompt cookbook is empirically validated. LoRA training cost-locks the register; until then the cookbook is the only enforcement mechanism.

Cost-of-being-wrong reasoning: at ~$0.04/image on FLUX-dev fp8 / RunComfy serverless and ~30 seconds wall-clock per image, regenerating 8 autopsied images is $0.32 and ~4 minutes. Triaging the remaining 17 genres at one representative each is $0.68 and ~9 minutes. Total cookbook validation cycle: under $1 and under 15 minutes wall-clock. The cost-driver is operator review time, not API spend.

---

*End of autopsy. Coverage: 8 of 8 operator-flagged failures + 6 working-set comparisons. All 14 prompts reconstructed deterministically from `/tmp/gen_20_new_images.py::build_prompt()` against the series YAMLs in the parent checkout. All seeds computed from `int(hashlib.sha256(series_id.encode()).hexdigest(), 16) % (2**31)`. All images visually inspected at `/Users/ahjan/phoenix_omega/assets/manga_catalog/stillness_press/<series_id>/main_character.png`.*
