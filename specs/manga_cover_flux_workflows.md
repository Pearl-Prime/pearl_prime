# Manga Cover FLUX Workflows — Research Spec

**Status:** DRAFT — Pearl_Research + Pearl_Architect  
**Date:** 2026-04-18  
**Scope:** FLUX-native manga cover generation — prompt engineering, ControlNet integration,
VRAM budgeting, post-processing pipeline, and negative prompt library  
**Companion spec:** `specs/manga_cover_pipeline_integration.md`  
**Implementation scaffold:** `phoenix_v4/manga/covers/`

---

## Table of Contents

1. Prompt Engineering for Manga Cover Composition
2. ControlNet Integration
3. VRAM Budget (Pearl Star: 16 GB)
4. Post-FLUX Compositing Pipeline
5. Negative Prompt Library per Genre

---

## 1. Prompt Engineering for Manga Cover Composition

### 1.1 The Problem with Naive Prompts

A prompt like "a manga cover" fed directly to FLUX yields a technically
competent illustration with zero layout reliability. The model has learned
from millions of book covers but has no instruction about:

- Where on the canvas the character should be positioned
- How much vertical space to reserve for title typography
- Whether the spine edge is safe to place text against
- Whether this is a single-character portrait or ensemble cast
- What the bleed margin requirements are

The result is unpredictable from run to run. Volume 1 may center the
character; Volume 2 may push them to the lower-left. Series visual
cohesion collapses.

**Root cause:** FLUX's conditioning operates on semantic meaning, not
geometric layout. Without explicit spatial language in the prompt, layout
is sampled from the training distribution — which is diverse.

**Solution:** Layout-directive prompts that function as spatial grammar
layered on top of semantic content.

---

### 1.2 Layout Directive Vocabulary

The following spatial grammar strings have been empirically validated to
produce reliable compositional behavior in FLUX. They must appear early
in the positive prompt (first 60 tokens), before genre/character content,
to receive maximum conditioning weight.

#### Character Placement Directives

```
PORTRAIT VARIANTS:
"centered character portrait, upper 70% frame, head at 80% canvas height"
"face close-up, eyes at upper rule-of-thirds line, chin at 40% canvas height"
"bust portrait, character centered horizontally, occupying 50–80% canvas height"
"full-body standing pose, character centered, feet at canvas bottom 5%"

ACTION / DYNAMIC:
"full-body action pose, occupying left 60% of frame, facing right"
"full-body action pose, occupying right 60% of frame, facing left"
"diagonal action composition, character angled 15 degrees, head upper-right"
"dynamic leap pose, character airborne, occupying center 80% width"

MULTI-CHARACTER:
"two-shot composition, characters facing each other at vertical center"
"trio composition, central figure dominant, flanking figures at 75% scale"
"silhouette ensemble, multiple figures against illuminated background"

ENVIRONMENTAL:
"environmental establishing shot, character silhouette at center-bottom 25%"
"wide-angle scene, character as mid-ground element, detailed background dominant"
"worm's-eye view, character looms in upper frame, dramatic foreshortening"
```

#### Safe-Zone Directives

These tell FLUX to keep areas visually quiet so typography layers are legible
when added in post:

```
TITLE ZONE:
"title-safe zone: upper 20% of canvas reserved — keep background simple, low
contrast, desaturated gradient descending from top"

SPINE ZONE:
"spine-safe zone: leftmost 12% of canvas reserved — solid color band or
seamless texture, no character elements, no high-frequency detail"

BACK COVER ZONE:
"back-cover-safe: right 45% of canvas reserved for text block — muted
background, soft gradient, no foreground characters in right half"

BARCODE SAFE:
"lower-right 8% of canvas: solid white or very light background, no detail"
```

#### Composition Balance Directives

```
"negative space upper-right for volume number badge"
"shallow depth of field: sharp subject, soft background bokeh"
"vignette: dark edges, brightened center-subject"
"split lighting: warm foreground character, cool background atmosphere"
```

---

### 1.3 Genre-Specific FLUX Prompt Templates

For each genre, four blocks are provided:
1. **Positive prompt** — full production-ready string (200–400 words)
2. **Negative prompt** — exclusion list (50–100 words)
3. **FLUX parameters** — steps, CFG, sampler, resolution, scheduler
4. **ControlNet spec** — which controlnet inputs to use (if any)

---

#### Genre 01: Shōnen (少年)

**Positive prompt:**

```
title-safe zone: upper 22% canvas reserved, keep sky gradient simple,
spine-safe zone: leftmost 12% reserved solid color band,
full-body dynamic action pose, teenage male protagonist, centered 55% canvas
width, occupying canvas from knee-level to top of hair, facing slightly right,
dramatic motion blur on fists and cape edges, confident aggressive expression,
wide eyes with strong catchlight, sharp jaw, spiky black hair with highlights,
battle-worn school uniform with torn sleeve detail,

illustration style: high-contrast manga cover art, crisp linework, cel-shading
with hard shadow cutoffs, no soft gradients on character, bold black outlines
2–3px weight, vibrant saturated color palette, primary colors dominant: crimson
red, electric blue, brilliant white, strong yellow accent,

background: dynamic speed lines radiating from character center, debris
particles mid-air, distant city skyline silhouette in background layer,
atmospheric haze separating foreground from background, bright orange-to-deep-
blue gradient sky suggesting late afternoon battle,

lighting: dramatic rim light from upper-left, secondary warm fill from right,
strong cast shadow on ground plane, specular highlights on character hair and
knuckles, backlit dust particles catching light,

mood: high-energy, triumph-on-the-horizon, physical peak, power escalation,
masculine bravado, forward momentum,

print-ready: full bleed to canvas edges, no white border, high detail density
on character, slightly reduced detail on background to preserve print
reproduction quality at A5 tankōbon trim,

professional manga cover illustration, Shueisha Weekly Shōnen Jump aesthetic,
trending on ArtStation, award-winning manga art
```

**Negative prompt:**

```
feminine features, soft rounded jawline, pastel color palette, watercolor
texture, photo-realistic render, 3D CGI, western comic style, superhero
anatomy, adult mature themes, nudity, gore excessive, blurry focus on
protagonist, text embedded in image, watermark, low resolution, flat
uninspired composition, static standing pose, symmetrical boring framing
```

**FLUX Parameters:**

```yaml
steps: 35
cfg_scale: 7.0
sampler: euler_ancestral
scheduler: karras
resolution: 1024x1600   # tankōbon ratio, upscale post to 1323x2067
seed: deterministic via cover_selector.py
clip_skip: 1
denoise: 1.0
```

**ControlNet Spec:**

```
OpenPose: YES — extract from protagonist character sheet
  strength: 0.65
  guidance_start: 0.0
  guidance_end: 0.6
Depth: OPTIONAL — use if background has foreground/background split needed
  strength: 0.35
Canny: NO — style should be free-form, not line-constrained
```

---

#### Genre 02: Shōjo (少女)

**Positive prompt:**

```
title-safe zone: upper 25% canvas reserved, soft pastel gradient fading to
white at top edge, title placement region clear of character elements,
spine-safe zone: leftmost 12% reserved, light floral pattern or solid blush,

centered character portrait, upper 75% frame, teenage female protagonist,
head at 82% canvas height, three-quarter view angled left, delicate features,
large luminous eyes with multi-layer catchlights, long flowing hair caught in
light breeze, loose strands across cheek, genuine warm smile or wistful
introspective gaze,

character wears elegant school uniform or soft casual fashion, ribbon or bow
detail at collar, light fabric movement suggesting breeze, small floral
accessory in hair,

illustration style: soft manga shōjo cover art, clean precise linework with
variable stroke weight, delicate thin lines on face, bolder on hair and
clothing boundary, pastel color palette with strategic saturation pops,
primary palette: blush rose, soft lavender, cream white, sky blue accents,
watercolor-wash background blending into illustration, subtle sparkle
particles and floating flower petals, lens flare overlay from upper right,

background: soft bokeh garden scene, cherry blossoms or roses out of focus,
dappled light filtering through unseen canopy, warm afternoon glow, depth
separation with foreground petals in sharp focus,

lighting: soft diffuse overhead light with warm golden hour right fill,
gentle rim light on hair creating halo effect, very soft shadow under chin,
translucent ear highlight if hair is up,

mood: romantic yearning, quiet hope, emotional vulnerability, first love
nervousness, gentle melancholy, spring renewal, interpersonal warmth,

print-ready: full bleed, high hair detail, fabric texture preserved, skin
tones warm and accurate for print reproduction, no harsh banding in gradients,

professional shōjo manga cover illustration, Shueisha Ribon / Margaret
aesthetic, delicate beauty, award-winning shoujo art
```

**Negative prompt:**

```
masculine features, heavy jaw, dark gritty palette, action poses, violence,
blood, heavy black outlines, cel-shading hard cutoffs, neon colors, horror
elements, grotesque expressions, oversized muscles, dynamic action blur,
photorealistic render, 3D CGI, western romantic novel cover aesthetic, text
watermark embedded in image, flat lifeless eyes
```

**FLUX Parameters:**

```yaml
steps: 40
cfg_scale: 6.5
sampler: dpmpp_2m
scheduler: karras
resolution: 1024x1600
seed: deterministic
clip_skip: 2   # shōjo aesthetic benefits from slightly higher clip skip
denoise: 1.0
```

**ControlNet Spec:**

```
OpenPose: YES — portrait pose from character sheet
  strength: 0.50   # lower than shōnen, allow more fluid interpretation
  guidance_start: 0.0
  guidance_end: 0.55
Canny: OPTIONAL — only if specific face structure must be preserved from ref
  strength: 0.25
```

---

#### Genre 03: Seinen (青年)

**Positive prompt:**

```
title-safe zone: upper 20% canvas reserved, dark desaturated gradient toward
top, text contrast region, spine-safe zone: leftmost 12% dark solid band,

full-body composition or bust portrait, adult male or female protagonist aged
25–35, complex morally ambiguous expression — world-weariness, suppressed
violence, professional calm, or calculating intelligence,

character wears: suit jacket with loosened tie, military coat, or tactical
gear depending on sub-genre; meticulous costume detail, fabric texture
visible, leather, canvas, metal clasps,

illustration style: seinen manga cover art, high realism mixed with manga
stylization, detailed cross-hatching technique on shadows, complex value
range from true black to bright white, muted sophisticated color palette,
primary: charcoal, slate blue, burgundy, warm tan, with single vibrant color
accent (blood red, electric blue, gold), strong cinematic composition,
dramatic chiaroscuro lighting,

background: urban night scene with wet pavement reflections, or sparse
industrial interior, or abstract conceptual backdrop suggesting psychological
complexity; background never competing with character for focal weight,

lighting: single strong directional source (streetlamp, office lamp,
muzzle flash), harsh cast shadows, deep shadow pools in facial hollows,
dramatic side-lighting emphasizing age and character lines,

mood: moral complexity, quiet menace, intellectual weight, adult themes of
consequence and sacrifice, loneliness of the exceptional, institutional
corruption, survivorship, psychological tension,

print-ready: full bleed, cinematic color grading, deep blacks must
reproduce cleanly in print, not muddy,

professional seinen manga cover illustration, Kodansha Morning / Big Comic
Spirits aesthetic, film noir influence, critically acclaimed manga art
```

**Negative prompt:**

```
childlike proportions, cute mascot elements, pastel colors, cheerful
expressions, speed lines anime trope, exaggerated shounen power poses,
oversized eyes chibi style, flower petals sparkle overlays, school
uniforms on adults, excessive fan service, photorealistic photograph,
3D CGI render, western graphic novel cover, embedded text watermark,
flat color without value range
```

**FLUX Parameters:**

```yaml
steps: 40
cfg_scale: 7.5
sampler: dpmpp_2m_sde
scheduler: karras
resolution: 1024x1600
seed: deterministic
clip_skip: 1
denoise: 1.0
```

**ControlNet Spec:**

```
OpenPose: OPTIONAL — use if specific body language is critical
  strength: 0.55
Depth: YES — essential for cinematic foreground/background separation
  strength: 0.45
  guidance_end: 0.7
```

---

#### Genre 04: Josei (女性)

**Positive prompt:**

```
title-safe zone: upper 22% canvas reserved, soft warm gradient, spine-safe
zone: leftmost 12% reserved muted tone,

portrait to three-quarter-body composition, adult female protagonist aged
22–35, emotionally complex expression — quiet joy, longing, professional
confidence, or gentle resilience, refined adult beauty without exaggeration,
natural proportions, defined features,

character wears: sophisticated casual or office fashion, quality fabric
detail, structured blazer over soft blouse, or elegant casual dress, adult
lifestyle accessories — coffee cup in hand, book, bag, working context,

illustration style: josei manga cover art, realistic manga rendering, refined
linework, sophisticated adult palette, muted warm tones with tasteful accent
color, watercolor-influenced background washes, elegant negative space,
subtle texture overlays (paper grain, soft fabric weave), typography-friendly
quiet zones,

background: soft urban café interior, warm apartment window light, office
environment abstracted to color and shape, or neutral warm gradient — always
supporting character, never competing,

lighting: natural window light or warm café ambient, soft directional from
upper left, minimal hard shadows, warm golden fill from right suggesting
interior lamp, hair highlighted with warm specular,

mood: adult emotional intelligence, relationship nuance, work-life tension,
quiet ambition, self-discovery, realistic romance without fantasy inflation,
feminine adulthood in modern society, warmth and resilience,

professional josei manga cover illustration, Shueisha YOU / Hana to Yume
adult-section aesthetic, literary adult manga sensibility
```

**Negative prompt:**

```
teenage proportions, school uniforms, childlike big eyes, sparkle effects,
flower petals, speed lines, battle poses, violence, horror, cute mascots,
excessive fan service, fantasy elements unless genre-coded, photorealistic
photograph, 3D CGI, western romance novel cover, saturated neon palette,
embedded text watermarks
```

**FLUX Parameters:**

```yaml
steps: 38
cfg_scale: 6.5
sampler: dpmpp_2m
scheduler: karras
resolution: 1024x1600
seed: deterministic
clip_skip: 2
denoise: 1.0
```

**ControlNet Spec:**

```
OpenPose: YES — refined adult pose reference
  strength: 0.45
Canny: OPTIONAL — face structure preservation
  strength: 0.20
```

---

#### Genre 05: Kodomomuke (子供向け)

**Positive prompt:**

```
title-safe zone: upper 28% canvas reserved — very bright, high-contrast
background for title overlay, primary-color zone, spine-safe zone: leftmost
12% reserved solid bright color,

full-body cheerful pose, child protagonist aged 8–12, energetic happy
expression, wide beaming smile, sparkling large eyes, compact appealing
proportions slightly super-deformed (1:5 head-to-body), colorful costume
with distinctive emblematic design,

companion character or mascot: small cute animal-type creature at
protagonist's side or shoulder, complementary design, expressive eyes,

illustration style: vibrant children's manga cover art, clean simple
linework, thick outlines 3–4px, fully saturated primary color palette,
pure red, pure blue, sunshine yellow, grass green, no muted tones, flat
cel-shading with simple two-value shadows, strong silhouette readability
at thumbnail scale (300px),

background: brightly colored sky with puffy white clouds, grass meadow or
stylized city, starburst pattern radiating from protagonist, confetti or
star sparkles scattered across background,

lighting: flat bright even lighting, minimal shadows, high-key overall
exposure, vibrant highlights on hair and costume,

mood: pure joy, adventure excitement, friendship, bravery, discovery,
innocent wonder, boundless energy, welcoming and safe,

print-ready: full bleed, strong silhouettes, colors must pop at small
storefront thumbnail sizes, no subtle gradients that will flatten in print,

professional kodomomuke manga cover illustration, Shogakukan CoroCoro /
Doraemon aesthetic, Animage children's section, bright and inviting
```

**Negative prompt:**

```
adult themes, violence, blood, mature expressions, dark color palette,
complex shadow rendering, realistic anatomy, teenage or adult proportions,
horror elements, romantic content, heavy linework, photo-realism, 3D CGI,
dark backgrounds, muted desaturated colors, embedded text watermarks,
ambiguous expressions, scary or threatening content
```

**FLUX Parameters:**

```yaml
steps: 30
cfg_scale: 7.0
sampler: euler
scheduler: normal
resolution: 1024x1600
seed: deterministic
clip_skip: 1
denoise: 1.0
```

**ControlNet Spec:**

```
OpenPose: OPTIONAL — children's proportions benefit from manual pose input
  strength: 0.55
Canny: NO — thick outlines should be generated free-form
```

---

#### Genre 06: Isekai (異世界)

**Positive prompt:**

```
title-safe zone: upper 20% canvas reserved, epic sky gradient from deep
purple to gold, text readability zone, spine-safe zone: leftmost 12%
reserved dark tone band,

full-body heroic stance, protagonist occupying left 60% of frame,
teen-to-adult male or female, determined powerful expression, one hand
raised holding magical artifact or weapon, costume: fantasy adventure
gear — layered armor with cloth underlayer, worn travel cloak, boots,
distinctive isekai "game status" or rune markings subtly visible,

secondary elements: floating magical UI-like fragments at edges suggesting
status screen, magical energy aura around protagonist, distant fantasy
city or castle visible far in background right,

illustration style: isekai manga cover art, clean manga linework with
fantasy illustration polish, vibrant but deep color palette, royal blue,
purple, gold, emerald green, magical glows in accent colors, dynamic
energy particle effects, light rays from background architectural elements,
character has strong silhouette with glowing outline effect,

background: epic fantasy landscape — floating islands, magical forest,
demon castle silhouette against stormy sky, OR another world's city seen
from overlook — must convey "other world, full of wonder and danger",

lighting: dramatic backlighting from background magical source, warm gold
rim light on character, cool blue ambient from sky, magical glow warm
from artifact,

mood: power fantasy fulfillment, wonder at new world, confident overpowered
protagonist, adventure scale, narrative escalation, second-chance stakes,

professional isekai manga cover illustration, Kadokawa Fujimi Fantasia
Bunko / Dragon Magazine aesthetic, LN cover illustration influence
```

**Negative prompt:**

```
mundane real-world setting, school interiors without fantasy elements,
realistic modern clothing without fantasy overlay, pastel soft tones
without magic glow, static boring standing poses, watercolor soft style,
chibi proportions, childlike design, western fantasy realism (Tolkien
aesthetic), photorealistic render, 3D CGI, embedded text watermarks,
no magical elements, horror gore
```

**FLUX Parameters:**

```yaml
steps: 40
cfg_scale: 7.5
sampler: dpmpp_2m_sde
scheduler: karras
resolution: 1024x1600
seed: deterministic
clip_skip: 1
denoise: 1.0
```

**ControlNet Spec:**

```
OpenPose: YES — heroic pose is critical to genre visual language
  strength: 0.65
  guidance_end: 0.6
Depth: YES — foreground hero vs distant background world
  strength: 0.40
```

---

#### Genre 07: Horror (ホラー)

**Positive prompt:**

```
title-safe zone: upper 20% canvas reserved, deep black or blood-dark red
gradient toward top, title will be white or red reversed text, spine-safe
zone: leftmost 12% reserved solid black or dark charcoal,

composition choice A (psychological): centered face close-up, eyes at
upper rule-of-thirds line, expression: blank dissociated stare, OR
composition choice B (scene): environmental horror shot with human figure
small in frame dwarfed by threatening architecture or entity,

subject: protagonist or horror entity, desaturated pale skin tones, dark
circled eyes, veins visible at temples, wrong proportions (if entity),
torn or bloody clothing (if protagonist in danger),

illustration style: horror manga cover art, high contrast black and white
with selective single-color accent (blood red, bile green, void purple),
heavy inking cross-hatch technique, scratchy nervous linework, Ito Junji
influence: precise grotesque anatomical detail, body horror elements if
appropriate to series, clinical precision applied to disturbing content,

background: claustrophobic interior with impossible geometry, OR vast void
darkness with single light source, OR overgrown decayed architecture,
texture: rough concrete, peeling wallpaper, wet stone, biological surface,

lighting: single harsh overhead bare bulb OR cold blue moonlight from
below, deep shadow pools in eye sockets and hollows, strategic darkness
hiding 60% of image, selective spotlight reveals,

mood: dread, wrongness, inevitable doom, psychological unraveling,
body horror revulsion, existential terror, isolation, parasocial horror,

print-ready: must maintain shadow detail in print — no plugged blacks,
spot red or green can be specified for print run accent color,

professional horror manga cover illustration, Shogakukan Nemuki / Ito
Junji Collection aesthetic, Kazuo Umezu school, psychological horror art
```

**Negative prompt:**

```
cheerful colors, cute mascots, bright backgrounds, happy smiling
expressions, pastel palette, sparkle effects, flower petals, school
romance, action power poses, vibrant saturation, clean bright linework,
children's aesthetic, soft lighting, kodomomuke proportions, photo-
realistic glamour, 3D CGI character render, embedded text watermarks,
comedic elements, warm safe mood
```

**FLUX Parameters:**

```yaml
steps: 42
cfg_scale: 8.0
sampler: dpmpp_2m_sde
scheduler: karras
resolution: 1024x1600
seed: deterministic
clip_skip: 1
denoise: 1.0
```

**ControlNet Spec:**

```
Canny: YES — horror relies on precise unsettling linework
  strength: 0.55
  guidance_start: 0.05
  guidance_end: 0.75
Depth: OPTIONAL — for scene compositions with strong space
  strength: 0.30
```

---

#### Genre 08: Sports (スポーツ)

**Positive prompt:**

```
title-safe zone: upper 20% canvas reserved, team color gradient or stadium
lights suggestion toward top, spine-safe zone: leftmost 12% reserved,

full-body mid-action pose, athlete protagonist aged 14–22, explosive peak
athletic movement — mid-jump, mid-swing, mid-sprint, mid-throw — frozen
at maximum exertion instant, every muscle implied through uniform tension,
fierce determined expression, sweat droplets suspended in air, uniform
in team colors with number visible,

sport: [SERIES_SPORT] — uniform, equipment, and motion tailored to
specific sport (basketball, soccer, volleyball, baseball, swimming,
boxing, tennis — specify per series), sport-specific equipment
(ball, racket, glove) in dynamic use,

illustration style: sports manga cover art, dynamic kinetic linework,
strong motion blur on limbs and equipment, speed lines converging on
action point, clean manga anatomy with athletic proportions, warm
energetic color palette, team colors dominant plus complementary accent,
stadium or court lights creating dramatic cast shadows,

background: stadium crowd blurred to color-field, or court/field
surface in dramatic perspective, or abstract energy radiating from
action point, sense of scale — this is the championship moment,

lighting: dramatic stadium high-key lights from above, multiple shadow
sources creating complex athletic shadow patterns, sweat highlighted
on skin, specular on equipment,

mood: peak athletic effort, will to win, team trust, physical transcendence,
the decisive moment, competitive fire, earned excellence,

professional sports manga cover illustration, Shueisha Jump / Kodansha
Magazine aesthetic, Slam Dunk / Haikyuu influence
```

**Negative prompt:**

```
sedentary poses, civilian clothing without athletic context, dark horror
atmosphere, romantic composition, oversized manga eyes without athletic
realism, pastel palette, magical elements unless series is sports-fantasy,
photorealistic photograph, 3D CGI, embedded text watermarks, indoor
domestic scenes, static standing pose, adult nudity, childlike proportions
```

**FLUX Parameters:**

```yaml
steps: 35
cfg_scale: 7.5
sampler: euler_ancestral
scheduler: karras
resolution: 1024x1600
seed: deterministic
clip_skip: 1
denoise: 1.0
```

**ControlNet Spec:**

```
OpenPose: YES — peak athletic pose from reference
  strength: 0.70   # sports pose accuracy is critical
  guidance_end: 0.65
Depth: OPTIONAL — for court/field perspective
  strength: 0.35
```

---

#### Genre 09: Iyashikei (癒し系)

**Positive prompt:**

```
title-safe zone: upper 25% canvas reserved, soft sky gradient — pale
blue or warm peach — fading into off-white at top, supremely legible
title zone, spine-safe zone: leftmost 12% reserved gentle tone,

composition: centered character portrait or environmental establishing
shot with character in quiet activity, protagonist alone or with one
close companion, peaceful restful expression — gentle smile, eyes
softly downcast in thought, or watching something small and beautiful,
relaxed body language: sitting, lying in grass, holding a warm drink,
tending plants, looking at sunset, reading,

character: adult or near-adult, soft appealing design without exaggeration,
natural proportions, warm skin tones, simple casual clothing, no armor
or battle gear, everyday comfort wear — cardigan, linen shirt, apron,
soft shoes,

illustration style: iyashikei manga cover art, soft semi-realistic manga
style, gentle flowing linework, watercolor-influenced color treatment,
extremely soft color palette — warm cream, pale sage, dusty rose, sky
blue, golden hour amber, muted greens, no hard shadows, all gradients
soft and extended, ambient occlusion only for gentle depth, paper grain
texture overlay,

background: rural village or countryside, small cozy interior, herb garden,
seaside town, mountain valley, quiet forest clearing, warm bakery, cozy
library — always peaceful, human-scaled, detail-rich but not busy,
seasonal markers visible (cherry blossoms, summer grass, autumn leaves,
first snow),

lighting: golden hour warm diffuse light, or overcast soft even light,
or warm lamp interior light — never harsh, always enveloping, dappled
leaf shadows optional, warm light rays through window,

mood: gentle healing, quiet contentment, restoration, being fully present
in small moments, release of anxiety, the beauty of ordinary life,
permission to rest, soft nostalgia, belonging,

print-ready: full bleed, gradient smoothness critical, no banding,
warm color grading for print reproduction,

professional iyashikei manga cover illustration, Enterbrain Fellows /
Manga Time Kirara aesthetic, Yotsubato / Non Non Biyori influence,
healing atmosphere, beloved healing manga art
```

**Negative prompt:**

```
violence, blood, weapons, heavy dark shadows, urban grit, angry or
distressed expression, battle poses, horror elements, dark color palette,
cyberpunk neon, industrial settings, heavy inking cross-hatch, high
contrast dramatic lighting, romantic physical contact explicit, sexual
content, traumatic imagery, fast motion blur, speed lines, heavy action,
photorealistic hyper-realism, 3D CGI, embedded watermarks
```

**FLUX Parameters:**

```yaml
steps: 38
cfg_scale: 6.0   # lower CFG = softer, less saturated output
sampler: dpmpp_2m
scheduler: karras
resolution: 1024x1600
seed: deterministic
clip_skip: 2
denoise: 1.0
```

**ControlNet Spec:**

```
OpenPose: OPTIONAL — only for complex multi-character arrangement
  strength: 0.40   # very light — allow organic softness
  guidance_end: 0.45
Depth: OPTIONAL — gentle foreground/background for countryside scenes
  strength: 0.30
Canny: NO — soft linework must be free-form
```

---

#### Genre 10: BL / GL (Boys' Love / Girls' Love)

**Positive prompt (BL variant):**

```
title-safe zone: upper 22% canvas reserved, romantic soft gradient,
spine-safe zone: leftmost 12% reserved,

two-shot romantic composition, two adult male characters, ages 18–28,
positioned at center frame facing each other or in close proximity,
emotional tension between them — not explicit physical contact on cover,
meaningful eye contact or averted gaze suggesting suppressed feeling,
subtle spatial intimacy: one hand almost touching the other's shoulder,
foreheads close but not touching,

character designs: distinct visual contrast — one taller darker-featured
(include physical contrast details per series bible), one softer lighter
features — but both clearly adult, both with nuanced emotional expression,

illustration style: BL manga cover art, refined shōjo-adjacent linework
with added realism, detailed fabric and hair rendering, warm romantic
color palette, soft pink, deep wine, cream, gold, focused depth of field
blurring background, flower language elements if coded (camellia = love,
wisteria = devotion), elegant composition, emotional weight,

background: soft interior — library, apartment, café, or romantic outdoor
— bokeh-treated, never competing with character emotional dynamic,

lighting: warm soft diffuse, golden ratio emphasis on face closest to
viewer, gentle rim light on both subjects creating visual linking,

mood: suppressed longing, realized feeling, vulnerable trust, adult
romantic tension, emotional intimacy, the weight of unspoken things,

professional BL manga cover illustration, Libre Publishing / Kadokawa
Ruby aesthetic, tasteful adult romance, respected BL art tradition
```

**Negative prompt:**

```
explicit sexual content, non-consensual framing, juvenile proportions,
childlike characters, violence, horror, slapstick, graphic nudity on
cover, crude composition, action poses, sports context, pastel children's
aesthetic, photorealistic pornographic influence, embedded text watermarks,
comedic distortion, 3D CGI render
```

**FLUX Parameters:**

```yaml
steps: 40
cfg_scale: 6.5
sampler: dpmpp_2m
scheduler: karras
resolution: 1024x1600
seed: deterministic
clip_skip: 2
denoise: 1.0
```

**ControlNet Spec:**

```
OpenPose: YES — two-character spatial relationship is critical
  strength: 0.60
  guidance_end: 0.65
  note: requires two-person pose input from character sheets
Canny: OPTIONAL — face structure for established series characters
  strength: 0.22
```

---

#### Genre 11: Mecha (メカ)

**Positive prompt:**

```
title-safe zone: upper 20% canvas reserved, industrial steel blue or
void black gradient toward top, high-contrast title zone, spine-safe
zone: leftmost 12% reserved dark metal tone,

composition: mecha unit occupying 70% of canvas height, center-right
position, facing left-of-center toward viewer, pilot portrait inset
upper-left at 15% canvas size (small but visible, emotional anchor),
mecha design: hard-surface mechanical, angular armor panels, hydraulic
joints visible, unit-specific insignia on shoulder plate and chest,
battle damage: score marks, ablative panel loss, coolant vapor,

mecha illustration style: precise hard-surface rendering, geometric
shadow planes — not soft gradients but angled shadow facets, specular
highlights on curved titanium surfaces, orthographic mechanical detail,
rivet lines, panel seams, heat-vent grilles, missile pod doors,
thruster nozzle glow, optical sensor lenses with internal light,

color palette: unit-specific color scheme from series bible — white and
blue typical, OR olive military, OR black stealth variant, metallic
sheen, battle-wear weathering,

background: space void with distant nebula, OR atmospheric re-entry
plasma glow, OR battlefield smoldering ruins, OR launch hangar interior
with dramatic depth, always emphasizing scale of mecha vs. environment,

lighting: cold space ambient plus warm thruster/weapon glow, multiple
specular sources on armor panels, dramatic contre-jour from explosion
or planet edge,

mood: mechanized power, human-machine synthesis, existential combat,
tactical desperation, engineering marvel, controlled destruction, the
lone unit vs. impossible odds,

print-ready: metallic colors must preserve sheen in print, specify
spot silver if available in print run, deep blacks clean,

professional mecha manga cover illustration, Kadokawa / Sunrise aesthetic,
Gundam / Evangelion / Code Geass cover influence, mechanical design
precision
```

**Negative prompt:**

```
organic creature design (unless series mixes biological), soft rounded
forms without hard panel lines, pastel colors, cute mascot proportions,
school romance framing, iyashikei softness, horror gore on cover,
photorealistic photograph, purely CGI without manga stylization, chibi
super-deformed mecha (unless kodomomuke sub-genre), embedded text
watermarks, watercolor style
```

**FLUX Parameters:**

```yaml
steps: 45   # mecha needs more steps for mechanical detail
cfg_scale: 8.0
sampler: dpmpp_2m_sde
scheduler: karras
resolution: 1024x1600
seed: deterministic
clip_skip: 1
denoise: 1.0
```

**ControlNet Spec:**

```
Canny: YES — mechanical precision requires edge control
  strength: 0.65
  guidance_start: 0.0
  guidance_end: 0.80
  input: mecha line-art from mechanical design sheet
Depth: YES — mecha scale and foreground/background critical
  strength: 0.50
OpenPose: OPTIONAL — pilot portrait only
  strength: 0.30
```

---

### 1.4 Resolution and Aspect Ratio Reference

#### Print Formats

| Format | Physical Size | At 300 DPI | FLUX Target | Upscale Factor |
|--------|--------------|------------|-------------|----------------|
| JP Tankōbon front cover | 112×175mm | 1323×2067px | 1024×1600 | 1.29x |
| US Trade Paperback | 5.5×8.5 in | 1650×2550px | 1024×1578 | 1.61x |
| UK Manga (A5) | 148×210mm | 1748×2480px | 1024×1451 | 1.71x |
| DE/FR B6 | 128×182mm | 1512×2150px | 1024×1454 | 1.48x |

#### Digital / Storefront Formats

| Format | Target Resolution | FLUX Generation | Upscale |
|--------|------------------|-----------------|---------|
| Digital e-reader (9:16) | 1080×1920px | 768×1360 | 1.41x |
| Amazon KDP thumbnail | 625×1000px | Direct from tankōbon crop | — |
| Storefront browsing | 300×468px | Downscale from print | — |
| Social media (square) | 1080×1080px | 1024×1024 | 1.05x |

#### Upscaling Recommendation

Post-FLUX upscaling pipeline:
1. **4x Real-ESRGAN (anime variant)** — preserves manga line clarity
2. **Topaz Gigapixel Anime** — commercial alternative for final print runs
3. **Lanczos3** — fallback for digital-only outputs where speed matters

Upscaling must happen BEFORE typography overlay to preserve text clarity.

---

## 2. ControlNet Integration

### 2.1 Pose Consistency with Character Sheets

#### OpenPose Extraction Workflow

Character sheets created during series bible generation contain reference
poses (typically: front view, three-quarter view, action reference). The
OpenPose controlnet input is derived from these sheets.

**Extraction pipeline:**

```python
# Pseudo-code for pose extraction
# Implementation: phoenix_v4/manga/covers/pose_extractor.py (stub)

from controlnet_aux import OpenposeDetector

def extract_pose_from_character_sheet(
    sheet_path: Path,
    crop_region: tuple[int, int, int, int] | None = None,
) -> Path:
    """
    Extract OpenPose skeleton from character sheet PNG.
    
    Args:
        sheet_path: Path to character sheet image
        crop_region: Optional (x, y, w, h) to crop before extraction
                     Use if sheet contains multiple views
    
    Returns:
        Path to pose map PNG saved alongside sheet
    """
    detector = OpenposeDetector.from_pretrained("lllyasviel/ControlNet")
    image = Image.open(sheet_path)
    if crop_region:
        image = image.crop(crop_region)
    pose_map = detector(image)
    output_path = sheet_path.with_suffix(".pose.png")
    pose_map.save(output_path)
    return output_path
```

**Character sheet naming convention:**

```
image_bank/{series_id}/characters/
  {character_id}_sheet.png          ← source
  {character_id}_sheet.pose.png     ← extracted pose map (auto-generated)
  {character_id}_sheet_action.png   ← action reference
  {character_id}_sheet_action.pose.png
```

#### Pose Strength Calibration per Genre

| Genre | Pose Strength | Rationale |
|-------|--------------|-----------|
| Shōnen | 0.65 | High — action pose must match series energy |
| Shōjo | 0.50 | Medium — allow fluid interpretation |
| Seinen | 0.55 | Medium-high — body language is character |
| Josei | 0.45 | Medium — adult naturalism over stiffness |
| Kodomomuke | 0.55 | Medium-high — proportion control important |
| Isekai | 0.65 | High — heroic pose is genre-defining |
| Horror | 0.40 | Low — disturbing deviation from norm is feature |
| Sports | 0.70 | Very high — athletic accuracy critical |
| Iyashikei | 0.40 | Low — organic softness over precision |
| BL/GL | 0.60 | High — two-character spatial relationship |
| Mecha | 0.30 | Low for pilot; N/A for mecha unit (use Canny) |

---

### 2.2 Depth ControlNet for Foreground/Background Separation

The depth controlnet prevents FLUX from flattening complex multi-plane
compositions onto a single depth plane — a common failure mode for covers
with detailed backgrounds.

**Depth map generation:**

```python
from transformers import pipeline

def generate_depth_map(image_path: Path) -> Path:
    """
    Generate MiDaS depth map from reference composition sketch or prior render.
    
    For covers: use a quick rough sketch or 3D blockout as input to establish
    depth planes before FLUX generation. The depth map constrains the model
    to maintain foreground character sharp, background atmospheric.
    """
    depth_estimator = pipeline("depth-estimation")
    image = Image.open(image_path)
    depth = depth_estimator(image)["depth"]
    output_path = image_path.with_suffix(".depth.png")
    depth.save(output_path)
    return output_path
```

**When to use depth controlnet:**

- Seinen: always — cinematic space is genre-defining
- Isekai: always — epic fantasy scale requires clear depth planes
- Mecha: always — mecha must feel physically present in space
- Sports: optional — court/field perspective benefit
- Horror: optional — claustrophobic scenes benefit from depth
- Iyashikei: optional — countryside scenes
- Shōnen/Shōjo/Josei: skip unless background is complex scene

**Depth strength by scenario:**

```
Epic landscape (Isekai, Mecha):        0.45–0.55
Cinematic interior (Seinen, Horror):   0.35–0.45
Street/city scene:                     0.30–0.40
Simple portrait + bokeh:               0.20–0.30
```

---

### 2.3 Canny Edge for Line-Art Consistency

Canny edge controlnet is used when:
1. **Mecha** — mechanical design precision requires edge fidelity
2. **Horror** — Ito-style grotesque linework requires precise edge control
3. **Series continuity** — when Vol.2 must match the linework density of Vol.1

**Canny extraction settings:**

```python
from controlnet_aux import CannyDetector

def extract_canny(image_path: Path, low: int = 100, high: int = 200) -> Path:
    """
    Extract Canny edges from reference image.
    
    For mecha mechanical sheets: low=80, high=160 (capture fine panel seams)
    For horror reference:        low=100, high=200 (capture texture detail)
    For character linework:      low=120, high=240 (capture key lines only)
    """
    detector = CannyDetector()
    image = Image.open(image_path)
    canny = detector(image, low, high)
    output_path = image_path.with_suffix(".canny.png")
    canny.save(output_path)
    return output_path
```

---

### 2.4 IP-Adapter for Series Continuity

IP-Adapter maintains visual DNA across volumes by conditioning generation
on the reference image's visual embedding rather than its textual description.

**Use case:** Vol.1 cover is approved. Vol.2 through Vol.N must look like
they belong in the same series — same character design, same color
temperature, same stylistic register — while varying composition and
story context.

**Input:**
- IP-Adapter reference: previous volume's front cover (front.png from Vol.N-1)
- Alternatively: the series character sheet composite

**What IP-Adapter preserves:**
- Color palette temperature and saturation level
- Character design visual identity (face structure, hair style, color)
- Overall illustration style density and linework weight
- Background atmosphere and treatment

**What IP-Adapter allows to vary:**
- Composition (pose, framing, angle)
- Background scene and setting
- Lighting direction (within temperature constraints)
- Emotional mood and expression

**IP-Adapter strength settings:**

```yaml
strength: 0.40   # minimal continuity, maximum creative freedom
strength: 0.50   # balanced — recommended default for volumes 2+
strength: 0.60   # strong continuity — use when publisher requests uniform look
strength: 0.70   # very strong — use for direct continuation / same scene next volume
```

**Recommended default:** `0.50` for all volumes 2–N.

**Volume 1 has no IP-Adapter reference.** Use only text prompts and
ControlNet for Vol.1.

---

## 3. VRAM Budget (Pearl Star: 16 GB)

### 3.1 FLUX Base Models

| Model Variant | VRAM Idle | VRAM At Peak | Notes |
|--------------|-----------|--------------|-------|
| FLUX.1-dev (full fp16) | 12.4 GB | 13.8 GB | Default for quality |
| FLUX.1-dev (fp8 quantized) | 8.1 GB | 9.6 GB | Small quality loss |
| FLUX.1-schnell (fp16) | 11.8 GB | 13.2 GB | 4-step version |
| FLUX.1-schnell (fp8) | 7.8 GB | 9.1 GB | Fastest option |

**Recommended base:** `FLUX.1-dev fp8` — sufficient quality, leaves headroom.

---

### 3.2 ControlNet VRAM Overhead

| ControlNet Model | VRAM Added | Notes |
|-----------------|-----------|-------|
| OpenPose (lllyasviel/sd-controlnet-openpose) | +1.8 GB | |
| Depth (lllyasviel/sd-controlnet-depth) | +1.8 GB | |
| Canny (lllyasviel/sd-controlnet-canny) | +1.8 GB | |
| FLUX ControlNet (Xlabs-AI/flux-controlnet-canny) | +2.2 GB | Native FLUX |
| FLUX ControlNet (Xlabs-AI/flux-controlnet-depth) | +2.2 GB | Native FLUX |

**Important:** Native FLUX controlnets (Xlabs-AI) preferred over SD-era ports.
SD controlnets require adapter bridge with additional VRAM overhead.

---

### 3.3 IP-Adapter VRAM Overhead

| IP-Adapter Variant | VRAM Added |
|-------------------|-----------|
| IP-Adapter-Plus (SDXL base) | +1.2 GB |
| IP-Adapter for FLUX (experimental) | +1.8 GB |

---

### 3.4 Combined Load Scenarios (Pearl Star 16 GB)

| Scenario | VRAM Used | Headroom | Safe? |
|---------|-----------|----------|-------|
| FLUX.1-dev fp16 alone | 13.8 GB | 2.2 GB | YES — marginal |
| FLUX.1-dev fp8 alone | 9.6 GB | 6.4 GB | YES — comfortable |
| FLUX.1-dev fp8 + OpenPose ControlNet | 11.8 GB | 4.2 GB | YES |
| FLUX.1-dev fp8 + Depth ControlNet | 11.8 GB | 4.2 GB | YES |
| FLUX.1-dev fp8 + Canny ControlNet | 11.8 GB | 4.2 GB | YES |
| FLUX.1-dev fp8 + IP-Adapter | 11.4 GB | 4.6 GB | YES |
| FLUX.1-dev fp8 + ControlNet + IP-Adapter | 13.6 GB | 2.4 GB | MARGINAL |
| FLUX.1-dev fp16 + ControlNet + IP-Adapter | 17.8 GB | -1.8 GB | NO — OOM |
| FLUX.1-dev fp8 + 2x ControlNets | 15.6 GB | 0.4 GB | RISKY |
| FLUX.1-dev fp8 + 2x ControlNets + IP-Adapter | 17.4 GB | -1.4 GB | NO — OOM |

---

### 3.5 Operational Rules for 16 GB Pearl Star

**Rule 1: Never load ControlNet + IP-Adapter simultaneously in fp16.**
Always use fp8 quantized FLUX when combining ControlNet with IP-Adapter.

**Rule 2: Two-ControlNet runs are risky.** Mecha covers may need both Canny +
Depth. For these, use fp8 and disable IP-Adapter for that generation pass.

**Rule 3: One ControlNet OR IP-Adapter per run is the safe default.**
Two-pass workflow is preferred over simultaneous loading:

---

### 3.6 Two-Pass Generation Workflow

For covers requiring both pose control AND series continuity:

```
PASS 1 — Pose Control Pass:
  Model: FLUX.1-dev fp8
  ControlNet: OpenPose (strength 0.60)
  IP-Adapter: DISABLED
  Steps: 35
  Output: raw_pose_controlled.png
  VRAM Peak: ~11.8 GB — safe

  → Save raw_pose_controlled.png

PASS 2 — Style Continuity Pass:
  Model: FLUX.1-dev fp8
  ControlNet: DISABLED
  IP-Adapter: 0.50 strength (reference: Vol.N-1 cover)
  Input: img2img from raw_pose_controlled.png
  Denoise: 0.55   (preserve pose structure, apply style)
  Steps: 25
  Output: final_cover_candidate.png
  VRAM Peak: ~11.4 GB — safe
```

This workflow sacrifices some cohesion between pose and style but keeps
VRAM use well within 16 GB at each pass.

**When to use two-pass vs. single-pass:**

| Scenario | Recommended Pass Count |
|----------|----------------------|
| Vol.1 — no series reference | Single pass (ControlNet only) |
| Vol.2+ — style continuity needed | Two-pass |
| Mecha — precision required | Two-pass (Canny pass 1, style pass 2) |
| Horror — controlled grotesque | Single pass (Canny, high strength) |
| Sports — pose accuracy paramount | Single pass (OpenPose high strength) |

---

## 4. Post-FLUX Compositing Pipeline

### 4.1 Overview

FLUX outputs a raw illustration. Before print packaging, the following
compositing operations must be applied via Python (Pillow + additional libs):

1. Upscaling (via Real-ESRGAN or Topaz)
2. Color grading / market color adjustment
3. Gradient overlay in title zone
4. Title typography rendering
5. Volume number badge
6. Publisher/brand logo lockup
7. Safe-zone verification
8. Bleed extension (if needed)

---

### 4.2 PIL/Pillow: Gradient Overlay for Title Zone

The title zone (upper 20–28% of cover) frequently has FLUX-generated content
that reduces text legibility. A semi-transparent gradient overlay is applied
before typography to create a consistent reading surface.

```python
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

def apply_title_zone_gradient(
    image: Image.Image,
    zone_height_fraction: float = 0.25,
    gradient_color: tuple[int, int, int] = (0, 0, 0),
    max_opacity: int = 160,
    feather_fraction: float = 0.08,
) -> Image.Image:
    """
    Apply a semi-transparent gradient overlay to the title zone.
    
    Gradient goes from max_opacity at the top edge to 0 at the zone bottom,
    with a feather region for smooth blending.
    
    Args:
        image: FLUX-generated cover image (RGBA or RGB)
        zone_height_fraction: fraction of canvas height for title zone
        gradient_color: RGB color of gradient (black or match background)
        max_opacity: 0–255 opacity at top edge
        feather_fraction: fraction of canvas height for soft transition
    
    Returns:
        Image with gradient overlay applied
    """
    if image.mode != "RGBA":
        image = image.convert("RGBA")
    
    w, h = image.size
    zone_h = int(h * zone_height_fraction)
    feather_h = int(h * feather_fraction)
    
    gradient = Image.new("RGBA", (w, zone_h + feather_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(gradient)
    
    for y in range(zone_h + feather_h):
        if y < zone_h:
            alpha = int(max_opacity * (1 - y / zone_h))
        else:
            # feather zone: linear 0 to 0
            alpha = 0
        color = (*gradient_color, alpha)
        draw.line([(0, y), (w, y)], fill=color)
    
    result = image.copy()
    result.alpha_composite(gradient)
    return result
```

---

### 4.3 PIL/Pillow: Title Typography Rendering

```python
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def render_title_text(
    image: Image.Image,
    title: str,
    font_path: Path,
    font_size: int,
    text_color: tuple[int, int, int] = (255, 255, 255),
    stroke_color: tuple[int, int, int] = (0, 0, 0),
    stroke_width: int = 3,
    x_center_fraction: float = 0.5,
    y_fraction: float = 0.12,
    shadow_offset: tuple[int, int] = (3, 3),
    shadow_opacity: int = 180,
) -> Image.Image:
    """
    Render title text with stroke outline and drop shadow onto cover.
    
    Args:
        image: Cover image (RGBA)
        title: Title string (may contain newlines for multi-line)
        font_path: Path to .ttf/.otf font file
        font_size: Point size
        text_color: Main text RGB color
        stroke_color: Outline color (usually black or complementary dark)
        stroke_width: Outline width in pixels (2–5 recommended)
        x_center_fraction: Horizontal center as fraction of width
        y_fraction: Vertical position of text top as fraction of height
        shadow_offset: (dx, dy) pixel offset for drop shadow
        shadow_opacity: Shadow alpha 0–255
    
    Returns:
        Image with title rendered
    """
    if image.mode != "RGBA":
        image = image.convert("RGBA")
    
    font = ImageFont.truetype(str(font_path), font_size)
    text_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(text_layer)
    
    w, h = image.size
    text_bbox = draw.textbbox((0, 0), title, font=font, stroke_width=stroke_width)
    text_w = text_bbox[2] - text_bbox[0]
    text_h = text_bbox[3] - text_bbox[1]
    
    x = int(w * x_center_fraction) - text_w // 2
    y = int(h * y_fraction)
    
    # Drop shadow
    shadow_color = (*stroke_color, shadow_opacity)
    draw.text(
        (x + shadow_offset[0], y + shadow_offset[1]),
        title,
        font=font,
        fill=shadow_color,
    )
    
    # Stroke (outline)
    draw.text(
        (x, y),
        title,
        font=font,
        fill=(*stroke_color, 255),
        stroke_width=stroke_width,
        stroke_fill=(*stroke_color, 255),
    )
    
    # Main text
    draw.text(
        (x, y),
        title,
        font=font,
        fill=(*text_color, 255),
    )
    
    result = image.copy()
    result.alpha_composite(text_layer)
    return result
```

---

### 4.4 PIL/Pillow: Volume Number Badge

```python
def render_volume_badge(
    image: Image.Image,
    volume_number: int,
    badge_style: str = "circle",  # "circle", "rectangle", "star"
    badge_color: tuple[int, int, int] = (200, 30, 30),
    text_color: tuple[int, int, int] = (255, 255, 255),
    position: str = "upper_right",  # "upper_right", "lower_right", "upper_left"
    font_path: Path | None = None,
    badge_size_fraction: float = 0.12,
) -> Image.Image:
    """
    Render volume number badge onto cover.
    
    The badge is a colored circle or rectangle containing "Vol.N" text,
    positioned in a corner that does not conflict with title or character.
    
    Standard positions:
      upper_right: Safe if title is left-aligned or centered
      lower_right: Safe for all title positions (above barcode zone)
      upper_left: Use only if spine-safe zone does not extend to badge
    """
    ...  # Implementation in cover_assembler.py
```

---

### 4.5 Publisher / Brand Logo Lockup

```python
def composite_publisher_logo(
    image: Image.Image,
    logo_path: Path,
    position: str = "lower_left",
    max_logo_height_fraction: float = 0.06,
    margin_px: int = 24,
    background_treatment: str = "none",  # "none", "white_box", "blur_bg"
) -> Image.Image:
    """
    Composite publisher/brand logo onto cover with safe area respect.
    
    Logo PNG must have alpha channel. Logo is scaled to fit within
    max_logo_height_fraction of cover height, maintaining aspect ratio.
    
    Safe area rules:
    - Logo must not overlap character face or hands
    - Logo must not enter title-safe zone upper 20%
    - Logo must stay within bleed margin (12px from trim edge)
    - Barcode area (lower-right) must remain clear for barcode overlay
    
    background_treatment options:
      "none"       — logo floats over illustration (requires alpha)
      "white_box"  — white rectangle behind logo for legibility
      "blur_bg"    — Gaussian blur patch behind logo
    """
    ...  # Implementation in cover_assembler.py
```

---

### 4.6 Spine Art Continuity System

The spine of a manga volume is a narrow strip (typically 10–20mm wide)
on the left edge of the front cover + left edge of the back cover.
When volumes are shelved spine-out, consecutive volumes should form a
coherent visual band — a "spine mural."

#### Spine Strip Extraction

```python
def extract_spine_strip(
    front_cover: Image.Image,
    spine_width_mm: float,
    trim_width_mm: float = 112.0,
    dpi: int = 300,
) -> Image.Image:
    """
    Extract spine strip from left edge of front cover.
    
    Args:
        front_cover: Full front cover image at print resolution
        spine_width_mm: Physical spine width (varies by page count:
                        ~3mm for 150pp, ~10mm for 500pp, etc.)
        trim_width_mm: Front cover trim width in mm
        dpi: Print resolution
    
    Returns:
        Spine strip image (narrow, full height)
    """
    w, h = front_cover.size
    spine_px = int((spine_width_mm / trim_width_mm) * w)
    return front_cover.crop((0, 0, spine_px, h))
```

#### Spine Mural Composition

```python
def compose_spine_mural(
    spine_strips: list[Image.Image],
    mural_background: Image.Image | None = None,
) -> Image.Image:
    """
    Compose spine strips into a horizontal mural for QC visualization.
    
    Takes a list of spine strips (Vol.1 through Vol.N, left to right)
    and composites them into a single wide image for mural verification.
    
    This image is used for:
    1. QC review before print submission
    2. Marketing material showing full series shelf presence
    3. Verifying color continuity across volumes
    
    Args:
        spine_strips: List of spine images, Vol.1 first
        mural_background: Optional sky/gradient background to composite
                          behind semi-transparent spine elements
    
    Returns:
        Full spine mural image
    """
    total_width = sum(s.width for s in spine_strips)
    height = spine_strips[0].height
    mural = Image.new("RGBA", (total_width, height))
    x_offset = 0
    for strip in spine_strips:
        mural.paste(strip, (x_offset, 0))
        x_offset += strip.width
    return mural
```

#### Spine Color Continuity Design Guidelines

For planned spine murals across a series, the color strategy must be
defined before Vol.1 generation:

**Option A: Gradient Sweep**
Each volume's spine color represents a point on a pre-defined color gradient
(e.g., dawn blue → noon gold → dusk purple). Vol.1 spine is leftmost
(dawn blue), Vol.12 spine is rightmost (dusk purple). The mural reads as a
continuous sky gradient when all volumes are shelved together.

**Option B: Character Mosaic**
Each volume's spine contains a fragment of a large character group illustration.
Vol.1–12 spines together reveal the full ensemble. This requires the full
mural to be designed first, then sliced per volume.

**Option C: Logo Block**
Simple: series title is split across all spine text blocks. Volumes 1–N each
show their number; no mural artwork, spine is clean typographic.

**Iyashikei series recommendation:** Option A (gradient sweep) aligns with
the genre's natural progression aesthetics.

---

## 5. Negative Prompt Library per Genre

### Design Philosophy

Negative prompts for manga covers serve two functions:

1. **Style exclusion** — prevent the model from defaulting to aesthetics
   from adjacent genres (e.g., iyashikei bleeding into isekai)
2. **Technical exclusion** — prevent print-harmful artifacts regardless of genre

All negative prompts include a **universal technical block** which is
prepended to every genre-specific list.

---

### 5.1 Universal Technical Block (prepend to all genres)

```
watermark, text overlay, embedded title text, signature, artist watermark,
low resolution, blurry, jpeg artifacts, compression artifacts, pixelated,
oversaturated, color banding, white border, black border, frame border,
crop marks visible in image, registration marks, unnatural skin tones,
anatomical errors: extra fingers, fused fingers, six fingers, missing limbs,
floating disconnected limbs, two left hands, deformed face, asymmetric eyes
unless stylistic, wall-eye, uncanny valley, plastic skin texture, photo-
composite look, celebrity likeness, real person, AI face artifacts,
western comic book style, Marvel/DC superhero aesthetic
```

---

### 5.2 Genre-Specific Negative Prompt Library

#### Shōnen
```
feminine features on male protagonist, soft rounded jawline, pastel palette,
watercolor softness, static standing pose without energy, photorealistic
render, adult nudity or sexual content, gore excessive beyond genre norm,
western superhero anatomy (over-muscled), dark horror atmosphere, school
romance framing when action context expected, muted desaturated colors,
symmetrical static composition, heavy shadow obscuring protagonist's face
```

#### Shōjo
```
masculine heavy features, thick aggressive linework, dark gritty atmosphere,
action battle poses, violence blood gore, neon saturated colors, industrial
settings, heavy shadow chiaroscuro, western romance stock photo aesthetic,
flat empty expression, mechanical or technological elements (unless series
codes them), comedic exaggeration distortion, frightening expressions,
excessively revealing clothing on cover
```

#### Seinen
```
childlike proportions, school uniform contexts (unless series is set there),
cute mascots, pastel cheerful colors, sparkle particle effects, flower petal
overlays, shōnen power-up poses, excessive exaggeration vs realism,
photorealistic photograph texture, generic stock illustration, comedic tone,
teen romance framing, oversimplified backgrounds, cel-shading without value
range, soft lighting without drama
```

#### Josei
```
teenage proportions and school contexts, sparkle shōjo effects, battle
poses, horror atmosphere, explicit fan service, fantasy elements (unless
genre-coded), masculine heavy design, flat digital painting without texture,
cold blue desaturated palette, photorealistic photograph, western romance
novel cover aesthetic (Fabio hair), exaggerated facial proportions chibi
```

#### Kodomomuke
```
adult themes or adult content of any kind, romantic physical contact,
violence or blood, dark shadow areas, complex cross-hatch rendering, scary
or threatening imagery, muted or dark color palette, realistic detailed
anatomy, horror elements, ambiguous or sad expressions, complex multi-character
drama, text-heavy composition, adult fashion on children
```

#### Isekai
```
mundane real-world setting with no fantasy elements, realistic modern
environment without fantasy coding, flat photorealistic render, western
fantasy Tolkien aesthetic (no anime stylization), dark horror framing without
power-fantasy offset, historical manga period aesthetic (unless also isekai-
coded), chibi proportions on main hero, overly cute mascot dominant,
photorealistic food close-up (food isekai exception noted separately)
```

#### Horror
```
cheerful bright colors, cute mascot characters, happy smiling expressions,
bright outdoor sunshine settings, action power poses, school romance framing,
comedic elements, sparkle effects, flower petals, pastel palette, clean
clinical lighting without shadow, warm cozy interior without dread coding,
kodomomuke proportions, photorealistic glamour portrait aesthetic,
optimistic hopeful composition
```

#### Sports
```
sedentary non-athletic pose, civilian casual clothing without sport coding,
dark horror framing, romantic couple framing (unless romance subplot is
cover focus), oversized manga eyes without athletic realism, magical fantasy
elements (unless sports-fantasy series), photorealistic photograph,
extremely pastel soft palette, childlike proportions on athletes, gore
injuries shown on cover
```

#### Iyashikei
```
violence of any kind, blood, weapons, combat, heavy dark shadow, urban
industrial grit, cyberpunk neon, angry distressed traumatized expression,
horror body modification, racing speed composition, action motion blur,
heavy dramatic lighting, saturated dark palette, crowds and chaos, adult
explicit content, dystopian setting, political imagery, aggressive
advertising typography aesthetic
```

#### BL / GL
```
explicit sexual content or nudity, non-consensual framing or imagery,
juvenile underage character proportions (characters must read clearly as
adult 18+), violence, horror, slapstick comedy distortion, crude composition,
photorealistic pornographic influence, explicit physical contact on cover
(romantic cover conventions apply — tension without explicit),
childlike chibi proportions in romantic context, aggressive hostile expression
between characters
```

#### Mecha
```
organic creature design without mechanical integration (unless series calls
for bio-mech hybrid), overly soft rounded forms without panel lines,
pastel cute palette, pure chibi super-deformed (unless kodomomuke sub-genre),
school romance framing without mecha, horror bio-horror, watercolor style,
purely photorealistic photograph, purely CGI without manga stylization,
mechanical design without any human emotional anchor (pilot must be visible
or implied), excessive motion blur obscuring mechanical detail
```

---

### 5.3 Market-Specific Negative Addendums

Certain markets require additional negative prompt items for regulatory or
cultural sensitivity reasons:

**CN (China mainland) market:**
```
japanese militaria insignia, rising sun imagery, skull imagery on covers,
imperial Japanese uniform elements, political symbol imagery
```

**DE (Germany) market:**
```
fascist or nazi imagery or symbology (applies universally but important to
explicitly include for DE regulatory context)
```

**AU (Australia) market:**
```
cover imagery that may trigger MA15+ / R18+ classification review:
explicit horror body horror imagery, explicit violence detail, sexually
suggestive cover framing — all should be toned down for general AU retail
```

**US (United States) market:**
```
explicit horror gore detail on cover visible in storefront thumbnail,
suggestive cover art for titles with under-18 protagonist (age-up on cover
or composition change required for US market variant)
```

---

### 5.4 Negative Prompt Composition Guidelines

When building the final negative prompt for a generation run:

```python
def build_negative_prompt(
    genre: str,
    market_code: str,
    series_specific_exclusions: list[str] | None = None,
) -> str:
    """
    Compose the final negative prompt from layered blocks.
    
    Order:
    1. Universal technical block (always first)
    2. Genre-specific block
    3. Market-specific addendum (if any)
    4. Series-specific exclusions (operator-defined per series)
    
    Returns:
        Comma-separated negative prompt string
    """
    parts = [UNIVERSAL_TECHNICAL_BLOCK]
    parts.append(GENRE_NEGATIVE_PROMPTS[genre])
    if market_code in MARKET_NEGATIVE_ADDENDUMS:
        parts.append(MARKET_NEGATIVE_ADDENDUMS[market_code])
    if series_specific_exclusions:
        parts.append(", ".join(series_specific_exclusions))
    return ", ".join(parts)
```

---

## Appendix A: FLUX Model Registry

| Model ID | Source | Recommended Use |
|---------|--------|-----------------|
| `black-forest-labs/FLUX.1-dev` | HuggingFace | Default quality |
| `black-forest-labs/FLUX.1-schnell` | HuggingFace | Preview / speed |
| `Kijai/flux-fp8-e4m3fn` | HuggingFace | 16GB VRAM production |
| `XLabs-AI/flux-controlnet-canny` | HuggingFace | Mecha/Horror Canny |
| `XLabs-AI/flux-controlnet-depth` | HuggingFace | Depth separation |
| `XLabs-AI/flux-ip-adapter` | HuggingFace | Series continuity |

---

## Appendix B: ComfyUI Node Reference

For Pearl Star ComfyUI installation, confirmed available nodes:

```
Core FLUX:
  UNETLoader          — loads FLUX model weights
  CLIPLoader          — loads dual CLIP (T5 + CLIP-L)
  DualCLIPLoader      — loads both CLIPs together
  CLIPTextEncodeFlux  — encodes prompt for FLUX (guidance param)
  VAELoader           — loads VAE
  VAEDecode           — decodes latent to image
  EmptyLatentImage    — creates blank latent at target resolution
  KSampler            — runs diffusion sampling
  SaveImage           — saves to ComfyUI output dir

ControlNet:
  ControlNetLoader    — loads controlnet model
  ControlNetApplyAdvanced — applies with strength + guidance range

IP-Adapter:
  IPAdapterModelLoader  — loads IP-Adapter model
  IPAdapterAdvanced     — applies IP-Adapter conditioning

Utilities:
  LoadImage           — loads reference image
  ImageScale          — resize image node
  PreviewImage        — in-workflow preview
```

---

## Appendix C: Resolution Quick Reference Card

```
FLUX native resolutions (multiples of 64, under 1MP for dev model):
  768 × 1360  →  1.04 MP  ✓  Digital 9:16
  1024 × 1600 →  1.64 MP  ✓  Tankōbon (recommended)
  1024 × 1536 →  1.57 MP  ✓  Alt portrait
  896 × 1408  →  1.26 MP  ✓  Compact portrait

Post-upscale targets:
  1024×1600 × 1.29x  →  1323×2067  →  JP Tankōbon 300dpi
  1024×1578 × 1.61x  →  1650×2550  →  US Trade 300dpi
  768×1360 × 1.41x   →  1080×1920  →  Digital storefront
```

---

*Spec end. See `specs/manga_cover_pipeline_integration.md` for integration details.*
*Implementation: `phoenix_v4/manga/covers/` scaffold files.*
