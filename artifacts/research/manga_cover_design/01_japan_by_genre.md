# Japan Manga Cover Design — By Genre
## Reference Document for Programmatic Cover Generation (FLUX/ComfyUI, 16GB VRAM)

**Version:** 1.0 | **Audience:** Image generation engineers | **Purpose:** Design bible for genre-accurate manga cover synthesis

---

## Table of Contents

1. [Shōnen](#1-shōnen)
2. [Shōjo](#2-shōjo)
3. [Seinen](#3-seinen)
4. [Josei](#4-josei)
5. [Kodomomuke](#5-kodomomuke)
6. [Isekai / Light Novel Crossover](#6-isekai--light-novel-crossover)
7. [Horror](#7-horror)
   - [7a. General Manga Horror](#7a-general-manga-horror)
   - [7b. Junji Ito Deep Section](#7b-junji-ito-deep-section-the-single-uncanny-image)
8. [Sports](#8-sports)
9. [Slice-of-Life / Iyashikei](#9-slice-of-life--iyashikei)
10. [BL / GL](#10-bl--gl)
11. [Mecha](#11-mecha)

---

## 1. Shōnen

### Overview

Shōnen covers communicate maximum energy in minimum pixel budget. At 100px thumbnail, the defining signals are: high-contrast warm palette (red, orange, yellow dominant), a character facing directly toward the viewer or in extreme action stance, bold black title lettering with white or colored outlines, and a publisher logo badge (usually Jump Comics red/gold) in the upper-left corner. Backgrounds are almost always subordinate — either fully blown out or abstracted into a radial energy burst (speed lines emanating from the character's center of mass). The character's expression is fierce, exuberant, or both simultaneously. Eyes are large and determined. The overall gestalt communicates: power, forward motion, male adolescent aspiration.

Shōnen covers evolved from Akira Toriyama's Dragon Ball (Shūeisha/Jump Comics, 1984–1995, 42 volumes) which established the template of single hero, bold action pose, energetic color field. Eiichiro Oda's One Piece (Shūeisha/Jump Comics, 1997–ongoing, 105+ volumes as of 2024) expanded the system by packing ensemble casts into dynamic group compositions — a technique later replicated in Koyoharu Gotouge's Demon Slayer: Kimetsu no Yaiba (Shūeisha/Jump Comics, 2016–2020, 23 volumes) and Kohei Horikoshi's My Hero Academia (Shūeisha/Jump Comics, 2014–2024, 38 volumes). Masashi Kishimoto's Naruto (Shūeisha/Jump Comics, 1999–2014, 72 volumes) introduced high-contrast orange backgrounds as a series-wide color identity signature.

**Thumbnail recognition signals:** Red/orange/yellow warmth. Bold black stroked title. Energetic male figure. Publisher badge upper-left.

---

### Layout Templates

**Template SHN-01: Single Hero Forward Facing**
```
┌─────────────────────────┐
│ [JUMP BADGE] [VOL #]    │  ← Top strip: 8% of height
│                         │
│    [TITLE BLOCK]        │  ← Title occupies top 25%, bold
│                         │
│                         │
│      CHARACTER          │  ← Full bleed, waist-up or full body
│   (center, facing fwd)  │    Character fills 70% of canvas width
│                         │
│  [speed line bg burst]  │  ← Background: radial from chest
│                         │
│ [Author name — small]   │  ← Bottom 5%, white or colored text
└─────────────────────────┘
```
*Reference: Naruto v1 (Kishimoto, 1999) — Naruto center, headband visible, orange radial bg. Demon Slayer v1 (Gotouge, 2016) — Tanjiro three-quarter, bamboo background abstracted.*

**Template SHN-02: Action Leap / Flying Pose**
```
┌─────────────────────────┐
│ [BADGE]    [TITLE BIG]  │  ← Title right-aligned or centered
│                         │
│        CHARACTER        │  ← Figure in mid-leap, diagonal
│      (diagonal axis)    │    Body occupies 80% of frame
│                         │
│ [TITLE continues down]  │  ← Title treatment may wrap vertically
│                         │
│  [flat color or env bg] │  ← Simplified environment at base
│ [AUTHOR]  [VOL#]        │
└─────────────────────────┘
```
*Reference: Dragon Ball v1 (Toriyama, 1984) — Goku on flying cloud, diagonal composition, single blue sky bg.*

**Template SHN-03: Ensemble Cast / Group Shot**
```
┌─────────────────────────┐
│ [BADGE] [TITLE LARGE]   │  ← Title across full top
│─────────────────────────│
│  [CHARACTER B]  [A]     │  ← Layered depth, overlapping figures
│  [CHARACTER C] [D] [E]  │    Main character center/front
│                         │    Secondary chars flanking/behind
│  [ENVIRONMENT BASE]     │  ← Ground plane or water, simplified
│ [AUTHOR]     [VOL#]     │
└─────────────────────────┘
```
*Reference: One Piece v50+ (Oda) — Straw Hat crew ensemble, Luffy always center-front. MHA v1 (Horikoshi) — Deku centered, All Might looming bg.*

**Template SHN-04: Face/Portrait Bust with Intense Expression**
```
┌─────────────────────────┐
│ [BADGE]                 │
│ [TITLE — vertical kanji]│  ← Title runs vertically left or right
│                         │
│   ┌─────────────────┐   │
│   │  FACE / BUST    │   │  ← Extreme close-up, fills 60% canvas
│   │  (eyes dominant)│   │
│   └─────────────────┘   │
│                         │
│ [gradient/abstract bg]  │
│ [AUTHOR]     [VOL#]     │
└─────────────────────────┘
```
*Reference: My Hero Academia v13 — Midoriya face close-up, green energy crackle bg. Naruto v25 — Itachi face, Sharingan eye dominant.*

**Template SHN-05: Two-Character Confrontation (Hero vs. Rival)**
```
┌─────────────────────────┐
│ [BADGE]   [TITLE]       │
│                         │
│  [HERO]      [RIVAL]    │  ← Mirror/diagonal composition
│  (left)      (right)    │    Characters lean toward each other
│                         │    Tension axis at center vertical
│  [bg: split color       │  ← Background split between two
│   or single env]        │    characters' color palettes
│ [AUTHOR]     [VOL#]     │
└─────────────────────────┘
```
*Reference: Naruto v43 — Naruto vs. Pain confrontation. Dragon Ball v28 — Goku vs Frieza.*

---

### Color Palette Recipes

**Palette SHN-A: "Jump Orange" (Classic Shōnen)**
- Background base: `#FF6B1A` (deep orange)
- Character skin highlight: `#FFD4A8`
- Title color: `#1A1A1A` (near-black)
- Title stroke: `#FFFFFF`
- Accent/energy: `#FFE800` (electric yellow)
- Publisher badge: `#CC0000` (Jump red)
- *Mood: Hot-blooded, urgent, archetypal Jump energy*
- *Reference: Naruto series, consistent across 72 volumes*

**Palette SHN-B: "Crimson Power" (Combat/Battle Arc)**
- Background: `#8B0000` (dark red)
- Mid-field: `#CC2200`
- Character silhouette shadow: `#330000`
- Title: `#FFFFFF` with `#FFD700` (gold) stroke
- Accent: `#FF4500` (orange-red flame)
- *Mood: Violence, high stakes, climax energy*
- *Reference: Demon Slayer v8 — Flame Hashira arc covers*

**Palette SHN-C: "Electric Blue Hero" (Power-Up Transformation)**
- Background: `#001A3A` (deep navy)
- Energy aura: `#00BFFF` (electric cyan-blue)
- Character: lit from behind, silhouette edge light
- Title: `#FFFFFF`
- Accent flash: `#7DF9FF`
- *Mood: Transcendence, new power, awe*
- *Reference: MHA v4 — Full Cowl reveal, blue lightning aesthetic*

**Palette SHN-D: "Forest Combat" (Natural Environment)**
- Background: `#1A4A2A` (deep forest green)
- Mid: `#2D6B3A`
- Character: warm skin against cool bg
- Title: `#FFE800` (yellow) or white
- Accent: `#FF6B1A`
- *Mood: Wilderness, survival, coming-of-age*
- *Reference: Demon Slayer v1 — mountain/forest environment*

**Palette SHN-E: "Gold Rush" (Tournament/Achievement)**
- Background: `#1A1200` → `#4A3500` gradient (dark gold)
- Highlights: `#FFD700`, `#FFA500`
- Title: metallic gold or white
- Shadow: `#0D0900`
- *Mood: Glory, tournament arcs, championship stakes*

---

### Typography Pairings

**SHN-TYPO-01: Classic Bold Impact**
- Title: Ultra-bold condensed sans, all caps, heavy black stroke (3–5% of canvas width). Think: Impact, but with more flare.
- Open-source equivalent: **Bebas Neue** (Google Fonts) or **Anton** — use at 200–300% scale, stroke in PILLOW with `strokewidth=8`
- Volume number: Small, bold, right-aligned, often in a colored box or badge
- Author byline: Thin weight, bottom of frame, 12–14pt equivalent
- Subtitle: Rare in shōnen; when present, thin italic below main title

**SHN-TYPO-02: Vertical Kanji Stack**
- Title runs vertically right-to-left (traditional Japanese reading direction)
- Characters large, high-contrast, each on its own line
- Open-source equivalent for romaji renders: **Noto Serif JP Bold** for Japanese-style weight/structure; for Latin: **Roboto Condensed Black**
- Volume number at bottom of vertical stack in smaller size

**SHN-TYPO-03: Graffiti/Brush Hybrid**
- Title treated as if hand-brushed in thick ink
- Strokes vary in width; letterforms energetic
- Open-source equivalent: **Permanent Marker** (Google Fonts) for Latin; **Zen Kurenaido** for Japanese-style brush feel
- Outline with white halo to pop off busy backgrounds

---

### Character Pose Library

| Pose ID | Name | Description |
|---------|------|-------------|
| SHN-P01 | Power Stance Forward | Both feet shoulder-width, fists at sides or one raised, direct eye contact with viewer |
| SHN-P02 | Battle Leap | Body airborne, one arm extended forward or weapon raised overhead, diagonal body axis |
| SHN-P03 | Victory Grin | Relaxed posture, hand behind head or thumb up, wide grin showing teeth |
| SHN-P04 | Tension Crouch | Low stance, weight forward, eyes narrowed, aura energy visible around body |
| SHN-P05 | Mid-Transformation | Arms wide, head back, energy burst emanating from body (power-up moment) |
| SHN-P06 | Determined Walk | Three-quarter view, walking toward viewer, confident expression, weapon or item in hand |
| SHN-P07 | Running at Viewer | Full frontal run, limbs pumping, speed lines behind, mouth open in battle cry |
| SHN-P08 | Injured Standing | One arm across chest wound, blood or damage visible, eyes still fierce — resilience pose |
| SHN-P09 | Friend Group Cluster | Multiple characters stacked/layered, leader front-center, all facing viewer |
| SHN-P10 | Back Turn w/ Head Glance | Character mostly back-facing, turns head to look over shoulder at viewer — mystery/cool |

---

### Background Treatment Rules

1. **Radial speed lines** (most common): White or colored lines emanating from character's torso center. Used in 60%+ of shōnen covers.
2. **Flat gradient field**: Single color or two-stop gradient. Simple. Used when character detail is maximum priority.
3. **Simplified environment**: Silhouette of mountains, ruins, city skyline — never photorealistic. Always subordinate to figure.
4. **Energy/aura field**: Swirling colored energy around character body (blues, yellows, reds depending on power type). Character appears to emanate light.
5. **Text-as-texture**: Background filled with small repeated Japanese characters or geometric pattern. Rare but iconic (certain Naruto volumes).
6. **NEVER**: Photorealistic rendered backgrounds, cluttered environmental detail, anything that competes with the character for visual dominance.

---

### Vol.1 vs. Later Volume Conventions

- **Vol.1**: Single hero, high-legibility introduction. Minimal complexity. Establish series visual identity. Often the most restrained cover in the run.
- **Vol.2–5**: Introduce secondary characters. Color palette solidifies as series identity.
- **Vol.10–20**: Ensemble poses common. Color becomes more adventurous as series has established equity. Major arc climax volumes often use dramatically different palette (darker, more intense).
- **Late volumes (50+, One Piece style)**: Near-abstract compositions possible. Fan recognition so high that experimental layouts work. Iconic variants: One Piece v61 (Oda) — silhouette-only cover. Color may invert from series norm to signal major story shift.
- **Final volume**: Often a callback composition to Vol.1 — same pose, evolved character design. Emotional bookend.

---

### Anti-Patterns (Negative Prompts for Generation)

- Soft pastel color palette (that's shōjo)
- Flowers, ribbons, lace, hearts as dominant decorative elements
- Sitting or recumbent character poses
- Melancholy or ambiguous expressions
- Muted/desaturated color treatment
- Thin or script typography for the main title
- White or cream background without energy treatment
- Realistic proportions (shōnen uses exaggerated anatomy)
- Character looking away from viewer in introspecive pose (that's seinen/slice-of-life)

---

## 2. Shōjo

### Overview

Shōjo covers operate in a completely different visual register from shōnen. Where shōnen is about outward energy, shōjo is about interior emotional states made visible. At 100px thumbnail, the recognition signals are: soft or jewel-toned palette (pinks, lavenders, warm creams, deep burgundies), a female protagonist in an elegant or emotionally expressive pose, extensive use of floral/botanical decorative elements, delicate line-weight title typography, and a sense of airiness or negative space. Eyes are enormous relative to the face — the single most recognizable anatomical marker of shōjo art — and are rendered with elaborate internal detail (highlights, starbursts, gradient irises).

Key reference works: Natsuki Takaya's Fruits Basket (Hakusensha/Hana to Yume, 1998–2006, 23 volumes; re-released in collector's edition) established the template of soft watercolor-influenced palette with elaborate decorative border elements. Ai Yazawa's Nana (Shūeisha/Cookie, 2000–2009, 21 volumes) broke from the soft template with high-contrast black-and-white fashion aesthetics — demonstrating that shōjo can span from kawaii-pink to punk-black depending on target age. Akiko Higashimura's Princess Jellyfish (Kodansha, 2008–2017, 17 volumes) used saturated jewel tones with illustration-style compositions. Chica Umino's Honey and Clover (Shūeisha/Young You → Chorus, 2000–2006, 10 volumes) employed loose watercolor washes and deliberately imprecise line work.

**Thumbnail recognition signals:** Soft or jewel palette. Enormous expressive eyes. Floral decorative elements. Delicate or script-style title. Female protagonist.

---

### Layout Templates

**Template SHJ-01: Floral Frame Portrait**
```
┌─────────────────────────┐
│ [IMPRINT BADGE — small] │  ← Flower Comics or equivalent, subtle
│                         │
│ [BOTANICAL BORDER]      │  ← Flowers/vines frame top and sides
│  ┌───────────────────┐  │
│  │  CHARACTER BUST   │  │  ← Soft-lit face, shoulders, elaborate
│  │  (dreamy gaze)    │  │    hair, 50% of canvas
│  └───────────────────┘  │
│ [BOTANICAL BORDER]      │  ← Flowers continue at base
│                         │
│  [TITLE — script/serif] │  ← Elegant typography, bottom third
│  [Author]  [Volume]     │
└─────────────────────────┘
```
*Reference: Fruits Basket v1 (Takaya, 1998) — Tohru bust portrait, cherry blossoms, soft peach palette.*

**Template SHJ-02: Full Figure Elegance**
```
┌─────────────────────────┐
│  [TITLE — top, elegant] │  ← Centered, serif or decorative font
│                         │
│      [CHARACTER]        │  ← Full body, standing gracefully
│   (3/4 turn or side)    │    Dress/costume detail visible
│                         │    Hair flowing, accessorized
│  [soft gradient bg]     │  ← Pastel gradient, no hard edges
│  [scattered petals]     │  ← Floating elements: petals, stars
│ [Author]    [Vol#]      │
└─────────────────────────┘
```
*Reference: Cardcaptor Sakura v1 (CLAMP, Kodansha, 1996) — Sakura full figure, magical costume, stars/sparkles.*

**Template SHJ-03: Two Characters / Romance Tension**
```
┌─────────────────────────┐
│ [TITLE — left or top]   │
│                         │
│  [CHAR A]    [CHAR B]   │  ← Hero and love interest close
│  (facing     (facing    │    Physical proximity implies romance
│   each other) each)    │    Eye contact or about to make it
│                         │
│  [floral/soft bg]       │  ← Garden, abstract flowers, warm light
│ [Author]    [Vol#]      │
└─────────────────────────┘
```
*Reference: Nana v1 (Yazawa, 2000) — Two Nanas together, high-contrast black/white fashion treatment.*

**Template SHJ-04: Emotional Close-Up (Face Only)**
```
┌─────────────────────────┐
│                   [VOL] │
│  [TITLE vertical right] │  ← Title runs along right edge
│                         │
│   ┌──────────────────┐  │
│   │   FACE CLOSE-UP  │  │  ← Eyes fill 40% of canvas
│   │  (tears optional)│  │    Emotional expression key
│   │  elaborate eyes  │  │
│   └──────────────────┘  │
│ [Author]                │
└─────────────────────────┘
```
*Reference: Honey and Clover v6 — Hagu face close-up, watercolor wash bg.*

**Template SHJ-05: Silhouette / Dreamy Distance**
```
┌─────────────────────────┐
│  [TITLE — large, center]│
│                         │
│    [CHARACTER]          │  ← Character seen from behind or in
│  (dreamy distance)      │    soft silhouette, smaller in frame
│                         │    Surrounded by environment/flowers
│  [ELABORATE BACKGROUND] │  ← Background more detailed than
│  (garden, cityscape,    │    usual — compensates for small figure
│   fantasy landscape)    │
│ [Author]    [Vol#]      │
└─────────────────────────┘
```
*Reference: Princess Jellyfish v1 (Higashimura) — Tsukimi dreaming, jellyfish environment fantasy treatment.*

---

### Color Palette Recipes

**Palette SHJ-A: "Cherry Blossom Dream"**
- Background: `#FFF0F5` (lavender blush)
- Floral accent: `#FFB7C5` (sakura pink)
- Deep accent: `#C2185B` (rose deep)
- Hair/shadow: `#8B3A5A` (mauve dark)
- Title: `#6D1E4A` (wine) or white
- *Mood: Romance, spring, classic shōjo — the default template*

**Palette SHJ-B: "Haute Punk" (Nana-style)**
- Background: `#FFFFFF` (white) or `#1A1A1A` (black)
- Character: High-contrast black/white fashion
- Accent: `#CC0022` (lipstick red)
- Title: Bold black on white or white on black, no softness
- *Mood: Fashion-forward, adult shōjo, urban cool*
- *Reference: Nana series — deliberately anti-saccharine*

**Palette SHJ-C: "Jewel Garden"**
- Background: `#1A0A2E` (deep violet)
- Flowers: `#9B59B6` (amethyst), `#E8D5F0` (pale lilac)
- Character lit: `#F8E8FF` (luminous lavender-white)
- Title: Gold `#D4AF37` or white
- *Mood: Fantasy-inflected romance, midnight garden, mystery*

**Palette SHJ-D: "Watercolor Wash"**
- Background: `#F5E6D3` (warm cream/ecru)
- Washes: `#E8A598` (coral-peach), `#A8C4D0` (soft teal)
- Character: Loose line, soft coloring — no hard outlines
- Title: `#5A3A28` (warm brown) or muted burgundy
- *Mood: Literary/artistic, slice-of-life shōjo, Honey and Clover aesthetic*

**Palette SHJ-E: "Starlight Rose"**
- Background: `#0D1A3A` gradient to `#2D0A4A` (deep night blue-purple)
- Stars/sparkles: `#FFD700`, `#FFFFFF`
- Character: backlit glow, `#FFE4E8` light skin
- Title: White or soft gold
- *Mood: Magical girl, fantasy, starry wonder — Cardcaptor Sakura palette territory*

---

### Typography Pairings

**SHJ-TYPO-01: Decorative Script**
- Title in flowing cursive or calligraphic font, light weight
- Open-source equivalent: **Dancing Script** (Google Fonts), **Great Vibes**, **Pinyon Script**
- Volume number: Small, surrounded by tiny floral ornament
- Author: Very small, italic, often in a complementary color rather than black

**SHJ-TYPO-02: High-Contrast Serif**
- Title bold serif, classical proportions — think fashion magazine masthead influence
- Open-source equivalent: **Playfair Display Bold**, **EB Garamond Bold**
- Effective for adult/josei-adjacent shōjo (Nana, NANA)

**SHJ-TYPO-03: Thin Weight Modern**
- Ultra-thin sans or display font — weightless, elegant
- Open-source equivalent: **Raleway Thin**, **Josefin Sans Light**
- Title may appear almost transparent against bg — legibility through contrast of color, not weight

---

### Character Pose Library

| Pose ID | Name | Description |
|---------|------|-------------|
| SHJ-P01 | Dreamy Gaze Up | Character looking upward or into the distance, eyes soft, half-lidded |
| SHJ-P02 | Hand to Heart | One or both hands pressed to chest, expressing longing or emotion |
| SHJ-P03 | Spin/Twirl | Full body spin, skirt or hair in motion, joyful expression |
| SHJ-P04 | Seated Elegance | Character seated on ground or chair, elaborate dress spread, contemplative |
| SHJ-P05 | Embrace/Lean | Character leaning into another or leaning against object — vulnerability |
| SHJ-P06 | Surprised/Blush | Eyes wide, mouth slightly open, flush visible on cheeks |
| SHJ-P07 | Profile Gaze | Strict profile view, eyes focused on something out of frame, wistful |
| SHJ-P08 | Hair Cascade | Character tossing or fanning long hair, decorative motion blur on hair |
| SHJ-P09 | Protective Crouch | Character crouched down protecting a smaller creature/person — maternal |
| SHJ-P10 | Tearful Resolve | Tears falling but expression firm — emotional climax pose |

---

### Background Treatment Rules

1. **Botanical overlay**: Flowers, vines, leaves rendered on top of or behind the character — not a scene, but a decorative surround.
2. **Soft gradient field**: Two-stop gradient in complementary pastels. Character floats in a color field.
3. **Scatter elements**: Individual petals, stars, bubbles, sparkles scattered across the field — never clustered, always dispersed.
4. **Romantic environment**: Loosely rendered garden, staircase, window with light — impressionistic, not architectural.
5. **Pattern background**: Repeating floral or lace pattern at low opacity — acts as texture rather than environment.
6. **NEVER**: Hard geometric backgrounds, industrial settings, sharp diagonal lines, high-contrast color blocks (unless doing deliberate Nana-style subversion).

---

### Vol.1 vs. Later Volume Conventions

- **Vol.1**: Introduce protagonist clearly, usually solo, clean palette. Establish whether series is soft-pink or more adult.
- **Mid-series**: Romance partner appears on covers. Emotional arc of relationship reflected in character proximity on covers.
- **Late series**: Emotional culmination — couples embrace, tearful expressions, dramatic composition changes. Color palette often darkens as story matures.
- **Final volume**: Frequently the most elaborate cover — full cast, maximum decorative treatment, callback to Vol.1 design elements.

---

### Anti-Patterns

- Speed lines or energy bursts as background treatment
- Hyper-muscled or exaggerated masculine anatomy
- Near-black or pure crimson dominant palette
- Bold blocky sans-serif title treatment
- Battle stance or aggressive action pose
- Absent or minimal decorative elements
- Publisher badge in red/gold shōnen format

---

## 3. Seinen

### Overview

Seinen covers operate in a register of deliberate aesthetic ambition. The target audience (adult men, 18–40) has sophisticated visual literacy and covers reward close inspection. At 100px thumbnail, seinen is often the hardest genre to pin down because it deliberately avoids genre clichés — but identifiable patterns include: desaturated or carefully controlled color palette (not warm-bright-orange or soft-pink, but earthy tones, deep blues, controlled contrast), compositions that give the character significant breathing room (more negative space than shōnen), title typography that is frequently more experimental or literary in treatment, and often a single image of stillness rather than action.

Reference works define a wide range: Takehiko Inoue's Vagabond (Kodansha/Morning, 1998–2015 hiatus, 37 volumes) uses watercolor painting as the cover medium — Musashi rendered in brushwork that looks nothing like typical manga art, positioned against ink-wash landscape. Kentaro Miura's Berserk (Hakusensha/Young Animal, 1989–2021, 41 volumes) uses rich oil-painting-influenced deep tones with Guts in maximalist Gothic armor compositions. Naoki Urasawa's Monster (Shōgakukan/Big Comic Original, 1994–2001, 18 volumes) uses thriller aesthetics — muted palette, disturbing negative space, characters cropped unsettlingly. Makoto Yukimura's Vinland Saga (Kodansha/Afternoon, 2005–ongoing, 28 volumes) evolved from action composition to increasingly sparse and contemplative covers mirroring the story's philosophical arc. Ryoko Kui's Dungeon Meshi (Kadokawa/Comic Beam, 2014–2023, 14 volumes) uses bright, illustration-book warmth — demonstrating seinen's breadth. Inio Asano's Goodnight Punpun (Shūeisha/Weekly Young Sunday→Big Comic Spirits, 2007–2013, 13 volumes) features intentionally mundane photography/illustration hybrid covers with the cartoon bird protagonist barely visible — radical subversion.

**Thumbnail recognition signals:** Controlled/desaturated or painterly palette. Negative space. Mature character design (realistic proportions). Literary title treatment. More restrained than shōnen.

---

### Layout Templates

**Template SEI-01: Single Figure with Negative Space**
```
┌─────────────────────────┐
│                [VOL #]  │
│                         │
│   [LARGE NEGATIVE       │  ← 40-60% of canvas is breathing room
│    SPACE / SKY /        │
│    GRADIENT]            │
│                         │
│      [CHARACTER]        │  ← Figure offset from center, smaller
│   (realistic style)     │    than shōnen, less "in your face"
│                         │
│  [TITLE — literary      │  ← Title sophisticated, lower placement
│   treatment]            │    May use period typefaces or bold lit
│  [IMPRINT] [AUTHOR]     │
└─────────────────────────┘
```
*Reference: Monster v1 (Urasawa) — Johan figure with disturbing stillness, muted grey-blue field.*

**Template SEI-02: Painterly Environment / Epic Landscape**
```
┌─────────────────────────┐
│  [TITLE — top edge]     │
│                         │
│  [ENVIRONMENT/          │  ← Background is almost primary subject
│   LANDSCAPE DOMINANT]   │    Painterly quality (watercolor, gouache)
│                         │
│    [SMALL CHARACTER]    │  ← Character embedded in landscape
│    (dwarfed by scene)   │    Scale emphasizes world > individual
│                         │
│  [IMPRINT]  [AUTHOR]    │
│  [VOL#]                 │
└─────────────────────────┘
```
*Reference: Vagabond v1 (Inoue, 1998) — Musashi in ink-wash landscape, figure and environment in dialogue.*

**Template SEI-03: Close-Up Psychological Portrait**
```
┌─────────────────────────┐
│ [IMPRINT badge subtle]  │
│ [TITLE — varied weight] │  ← Title may use mixed weights (bold/thin)
│                         │
│  ┌─────────────────┐    │
│  │  FACE / EYES    │    │  ← Realistic eye rendering, not manga-large
│  │  (unsettling    │    │    Gaze may be off-axis or disturbing
│  │   or compelling)│    │
│  └─────────────────┘    │
│                         │
│  [controlled bg]        │  ← Gradient, fog, abstract — never busy
│  [AUTHOR]    [VOL#]     │
└─────────────────────────┘
```
*Reference: Goodnight Punpun v1 — mundane photography bg with cartoon Punpun family absurdly integrated.*

**Template SEI-04: Action with Painterly Execution**
```
┌─────────────────────────┐
│ [TITLE left-aligned]    │
│                         │
│  [CHARACTER IN ACTION]  │  ← Action, but rendered with craft —
│  (dynamic but craft-    │    not speed-lines and energy bursts
│   focused, not cartoony)│    Emphasis on form and technique
│                         │
│  [RICH TEXTURED BG]     │  ← Environment has painterly texture
│  [IMPRINT] [AUTHOR/VOL] │
└─────────────────────────┘
```
*Reference: Berserk v1 (Miura) — Guts in Gothic armor, rich dark palette, semi-painterly execution.*

**Template SEI-05: Ensemble with Cinematic Frame**
```
┌─────────────────────────┐
│ ─────────────────────── │  ← Letterbox bars (widescreen cinematic)
│  [CHARACTERS — wide]    │  ← Characters arranged in wide format
│  (cinematic group shot) │    Like a film still, horizontal emphasis
│ ─────────────────────── │  ← Letterbox bars
│  [TITLE — below frame]  │
│  [AUTHOR / IMPRINT/VOL] │
└─────────────────────────┘
```
*Reference: Vinland Saga later volumes — cinematic wide compositions reflecting the epic historical scope.*

---

### Color Palette Recipes

**Palette SEI-A: "Ink and Rust" (Historical Action)**
- Background: `#2A1810` (dark umber)
- Mid: `#5C3320` (warm dark brown)
- Character armor/metal: `#7A7A7A` (steel grey)
- Blood/accent: `#8B1010` (dark crimson)
- Title: `#F0E0C0` (aged parchment) or white
- *Mood: Historical epic, violence, consequence — Berserk/Vagabond territory*

**Palette SEI-B: "Fog and Steel" (Psychological Thriller)**
- Background: `#B0B8C0` gradient to `#606870` (grey-blue fog)
- Character: slight warmth against cool bg
- Accent: `#2C4A6E` (deep slate blue)
- Title: `#1A1A1A` or `#FFFFFF`
- *Mood: Suspense, unease, urban thriller — Monster territory*

**Palette SEI-C: "Harvest Light" (Slice-of-life Seinen)**
- Background: `#F5DEB3` (wheat), `#D2691E` (warm ochre)
- Foliage: `#6B8E23` (olive), `#228B22` (forest)
- Character warm: `#F4C2A0` skin in natural light
- Title: `#3D1C02` (dark brown) or deep forest green
- *Mood: Rural warmth, contentment, Dungeon Meshi/food-manga aesthetic*

**Palette SEI-D: "Modernist Flat" (Contemporary Seinen)**
- Background: `#F8F8F8` (near-white) or `#1C1C1C` (near-black)
- Single accent: one saturated color — `#E8512A` or `#2A6AE8`
- Character: flat art style, limited palette
- Title: Bold, geometric, modern
- *Mood: Literary manga, Goodnight Punpun aesthetic — deliberately unglamorous*

**Palette SEI-E: "Arctic Saga" (Nordic/Historical)**
- Background: `#87CEEB` (sky blue), `#F0F8FF` (ice white), `#708090` (slate)
- Sea: `#1C4F7C` (cold navy)
- Character furs/metal: `#8B7355` (tan leather)
- Title: `#0D2137` (deep navy) or white
- *Mood: Vinland Saga — cold, vast, historically grounded*

---

### Typography Pairings

**SEI-TYPO-01: Literary Serif**
- Bold display serif, classical proportions, used at large scale
- Open-source: **Libre Baskerville Bold**, **Merriweather Bold**, **Lora Bold**
- Appropriate for historical, psychological, literary seinen

**SEI-TYPO-02: Geometric Modern Sans**
- Clean, architectural sans — confidence without aggression
- Open-source: **Montserrat Bold**, **Raleway Bold**, **Oswald**
- Used for contemporary/thriller seinen

**SEI-TYPO-03: Hand-Brushed Ink**
- Title appears hand-lettered in thick ink, similar to calligraphic brushwork
- Open-source: **Kaisei Decol**, **Zen Brush 2** (Google Fonts)
- Vagabond's covers use actual sumi-e brushwork — impossible to fake, but stylistically reference-worthy

---

### Character Pose Library

| Pose ID | Name | Description |
|---------|------|-------------|
| SEI-P01 | Still Observer | Standing or seated, simply looking — no action, maximum psychological weight |
| SEI-P02 | Walking Away | Seen from behind, figure walking into landscape or darkness |
| SEI-P03 | Weapon Rest | Sword/weapon resting on shoulder or at side — post-battle stillness |
| SEI-P04 | Contemplation Sit | Cross-legged or knee-up seated, thinking pose, hand to chin or forehead |
| SEI-P05 | Battle-Scarred Stand | Upright but visibly wounded, bandages, blood — earned suffering |
| SEI-P06 | Mid-Combat Frozen | Action caught mid-swing — cinematographic freeze frame feel |
| SEI-P07 | Intellectual Profile | Strict profile, reading or examining something, calm demeanor |
| SEI-P08 | Kneeling/Prostrate | Character kneeling in submission, grief, or prayer |
| SEI-P09 | Wide Environment | Character tiny within vast landscape — scale and insignificance |
| SEI-P10 | The Look Back | Turning to look behind at implied threat or memory |

---

### Background Treatment Rules

1. **Painterly environment**: Watercolor, gouache, or oil-painting-mimicking digital treatment. Background has intrinsic artistic value.
2. **Atmospheric gradient**: Fog, mist, smoke. Creates depth without narrative specificity.
3. **Empty field (strategic)**: Perfectly flat color field or gradient — background absence as statement.
4. **Architectural/environmental detail**: Rendered enough to establish historical or geographic setting.
5. **Texture overlay**: Paper grain, stone, aged surface applied to enhance painterly quality.
6. **NEVER**: Digital speed lines, energy aura bursts, pure anime-style coloring (cell-shading), kawaii decorative scatter elements.

---

### Vol.1 vs. Later Volume Conventions

- **Vol.1**: Often the most accessible entry point — character established clearly, palette introduced.
- **Mid-series**: Cover design may become more adventurous as series builds fan base. Urasawa's Monster grows progressively more disturbing.
- **Long-running (Berserk, Vagabond)**: Covers can become nearly abstract in artistic ambition. Vagabond's hiatus period covers are pure sumi-e paintings.
- **Late/final volumes**: Maximum artistic expression. The earned reward for long-running critical darlings is total cover freedom.

---

### Anti-Patterns

- High-saturation warm palette (shōnen territory)
- Speed lines / energy burst backgrounds
- Comic-relief expressions (big sweat drops, chibi moments)
- Overly sexualized female figures as primary cover element (may appear in ecchi-adjacent seinen but is anti-pattern for prestige seinen)
- Thin, weak title typography
- Publisher badge too prominent (seinen badges tend to be understated)
- Flat digital coloring with no texture or nuance

---

## 4. Josei

### Overview

Josei is adult women's manga, and its covers reflect a more mature, psychologically complex visual vocabulary than shōjo. At 100px thumbnail, josei occupies territory between shōjo and seinen: warmer and more emotionally expressive than seinen, but more restrained and adult-toned than shōjo. The palette tends toward wine reds, warm neutrals, dusty roses, forest greens, and deep indigos — sophisticated rather than saccharine. Typography is frequently more design-forward. Decorative elements remain (flowers, coffee cups, everyday objects) but are used with editorial restraint rather than maximum-decorative-density. Characters have more realistic proportions and adult body language.

Reference works: Chica Umino's Honey and Clover (Shūeisha, 2000–2006) sits at the shōjo/josei border, using loose watercolor illustration and deliberately imprecise line work that signals artistic intention rather than commercial perfection. Chica Umino's March Comes in Like a Lion (Hakusensha/Young Animal, 2007–ongoing, 20+ volumes) deepens the approach — covers feature Rei Kiriyama in isolated, psychologically loaded compositions, often using shogi pieces as symbolic props, backgrounds that feel like weathered wood and winter light. Yuki Yoshihara's Butterflies Flowers (Shōgakukan/Flower Comics, 2006–2009, 8 volumes) and Kintetsu Yamada's Sweat and Soap (Kodansha/Morning KC, 2018–2021, 11 volumes) use more illustrative, warm-toned approaches with adult characters in realistic workplace or romantic settings.

**Thumbnail recognition signals:** Wine/dusty rose/warm neutral palette. Realistic adult faces. Everyday objects as decorative props. Restrained editorial design. Emotional interiority.

---

### Layout Templates

**Template JOS-01: Editorial Portrait**
```
┌─────────────────────────┐
│  [TITLE — editorial,    │  ← Typeface choice is design statement
│   upper third]          │    Not scripty, not blocky — considered
│                         │
│  ┌─────────────────┐    │
│  │  ADULT FEMALE   │    │  ← Character with realistic proportions
│  │  CHARACTER      │    │    Adult expression, not wide-eyed
│  │  (3/4 portrait) │    │
│  └─────────────────┘    │
│                         │
│  [warm toned bg]        │  ← Cream, dusty rose, muted lavender
│  [prop elements]        │  ← Coffee cup, book, flower — editorial
│  [Author]    [Vol#]     │
└─────────────────────────┘
```

**Template JOS-02: Couple with Adult Tension**
```
┌─────────────────────────┐
│  [TITLE]                │
│                         │
│  [CHAR A]   [CHAR B]    │  ← Close but not touching, or touching
│  (adult male) (adult f) │    with realistic adult body language
│                         │    Not anime idealized — human warmth
│  [interior bg]          │  ← Apartment, office, cafe — realistic
│                         │    but simplified
│ [AUTHOR]     [VOL#]     │
└─────────────────────────┘
```

**Template JOS-03: Isolated Figure with Season**
```
┌─────────────────────────┐
│  [SEASONAL ELEMENT]     │  ← Snow, autumn leaves, summer heat haze
│  (top/background)       │    Season is emotional metaphor
│                         │
│    [CHARACTER]          │  ← Smaller within frame, season envelops
│  (contemplative)        │    Expression inward, not outward
│                         │
│  [TITLE — literary]     │  ← March Comes in Like a Lion style:
│                         │    title IS the emotional statement
│ [AUTHOR]    [VOL#]      │
└─────────────────────────┘
```
*Reference: March Comes in Like a Lion v1 (Umino, 2007) — Rei in winter light, shogi piece, isolated.*

---

### Color Palette Recipes

**Palette JOS-A: "Winter Interior"**
- Background: `#D4C4A8` (warm parchment), `#A89880` (warm grey-tan)
- Character: natural skin tones, no enhancement
- Accent: `#5C2A1A` (dark wine) or `#2A4A5C` (dark slate)
- Title: `#1A1A1A` or `#3A1A10`
- *Mood: Literary introspection, Umino's March Comes in Like a Lion*

**Palette JOS-B: "Dusty Rose Professional"**
- Background: `#E8C4C0` (dusty rose)
- Mid: `#C4948E` (mauve)
- Character: warm neutral clothing, workplace setting
- Title: `#5A1A2A` (dark mauve) or charcoal
- *Mood: Workplace romance, Sweat and Soap territory*

**Palette JOS-C: "Forest Hour"**
- Background: `#2A4A2A` (deep forest green)
- Mid: `#4A7A4A`
- Highlights: `#C8E8C0` (pale mint)
- Title: `#F5F0E8` (cream white)
- *Mood: Nature-grounded, quiet drama*

---

### Typography Pairings

**JOS-TYPO-01: Restrained Serif**
- Medium-weight serif, classical but not stuffy
- Open-source: **Cormorant Garamond**, **EB Garamond** — NOT bold italic, medium weight
- Subtitle present more often in josei than other genres

**JOS-TYPO-02: Minimal Sans**
- Thin to medium weight sans-serif, wide tracking
- Open-source: **Lato Light**, **Source Sans Pro**, **Inter Light**

---

### Character Pose Library

| Pose ID | Name | Description |
|---------|------|-------------|
| JOS-P01 | Looking Out Window | Character in profile or 3/4 view, gazing out, introspective |
| JOS-P02 | Coffee Cup Moment | Hands around mug, seated, quiet domestic energy |
| JOS-P03 | Walking City | Adult figure in urban setting, coat/scarf, casual movement |
| JOS-P04 | Unexpected Smile | Suppressed smile, as if caught in private happiness |
| JOS-P05 | Shoulder Lean | Leaning on partner's shoulder, trust and comfort expressed |

---

### Background Treatment Rules

1. **Interior spaces**: Apartment, office, cafe — rendered simply but recognizably real.
2. **Season-coded exterior**: Cherry blossoms, snow, autumn leaves used as emotional backdrop.
3. **Warm gradient**: Single warm color field with texture — not clinical.
4. **Everyday objects as still life**: Books, flowers in vase, food — editorial magazine influence.
5. **NEVER**: Speed lines, energy bursts, exaggerated fantastical environments.

---

### Anti-Patterns

- Enormous anime eyes (even though present in some josei, high-chibi proportions are anti-pattern)
- Maximal floral decoration (shōjo territory)
- Action poses or combat
- Saturated primary color palette
- Bubbly/kawaii typography

---

## 5. Kodomomuke

### Overview

Kodomomuke ("for children") manga covers are engineered for maximum approachability and joy. At 100px thumbnail, the key signals are: bright primary and secondary colors (not neon, but saturated and clean), rounded character designs with very large heads and small bodies (chibi proportions), friendly or excited facial expressions always, simple clear title typography often with rounded letterforms, and frequent inclusion of animals, companions, or cute accessories. The compositions are never threatening or ambiguous. Even the typography bounces.

Reference works: Fujiko F. Fujio's Doraemon (Shōgakukan, 1969–1996, 45 volumes) is the archetype — Doraemon's perfectly round blue head, white gloves, yellow pocket, against a clean white or pastel background with simple block-letter title. Hidenori Kusaka's Pokémon Adventures (Shōgakukan, 1997–ongoing) features the generation's starter Pokémon prominently with the human trainer, bright energy palettes. Kiyohiko Azuma's Yotsuba! (Dengeki Comics/Media Works, 2003–ongoing) uses remarkably uncluttered design — white or simple colored bg, Yotsuba's distinctive pigtails and green hair — a masterclass in children's book simplicity. Konami Kanata's Chi's Sweet Home (Kodansha/Morning, 2004–2011, 12 volumes) features Chi the kitten in bright pastel rounds, almost picture-book design.

**Thumbnail recognition signals:** Primary colors, round/chibi characters, friendly expression, bouncy title, no threatening elements.

---

### Layout Templates

**Template KOD-01: Character Center White Field**
```
┌─────────────────────────┐
│  [TITLE — large, round  │  ← Rounded letterforms, bright color
│   bouncy letterforms]   │
│                         │
│      [CHARACTER]        │  ← Full body, chibi proportions
│  (cute, round, bright)  │    Centered, lots of breathing room
│                         │
│  [white or light bg]    │  ← Almost no background — child focus
│  [companion/pet]        │    Companion character at feet or floating
│ [Author]    [Vol#]      │
└─────────────────────────┘
```
*Reference: Doraemon v1 — white background, Doraemon centered, clean.*

**Template KOD-02: Activity Scene**
```
┌─────────────────────────┐
│  [TITLE — top arc]      │  ← Title may curve or arch
│                         │
│  [CHARACTER IN ACTION]  │  ← Running, jumping, playing — joy
│  [+ COMPANION/FRIENDS]  │    Multiple characters in fun scene
│                         │
│  [SIMPLE ENVIRONMENT]   │  ← Grass, clouds, simple outdoors
│  [Author]    [Vol#]     │
└─────────────────────────┘
```
*Reference: Pokémon Adventures — trainer and Pokémon in action together.*

---

### Color Palette Recipes

**Palette KOD-A: "Primary Bright"**
- Background: `#FFFFFF` or `#F0F8FF` (near-white)
- Character 1: `#FF4444` (primary red)
- Character 2: `#4444FF` (primary blue)
- Character 3: `#FFDD00` (primary yellow)
- Title: Any primary, outlined in white
- *Mood: Doraemon — clean, friendly, trustworthy*

**Palette KOD-B: "Pastel Playhouse"**
- Background: `#E8F4FD` (baby blue)
- Accents: `#FFB3BA` (baby pink), `#BAFFC9` (mint)
- Character: Warm, soft tones
- Title: `#5B8DD9` (medium blue) outlined white
- *Mood: Chi's Sweet Home — soft, nurturing, safe*

**Palette KOD-C: "Nature Adventure"**
- Background: `#87E87A` (bright grass green) or `#87CEEB` (sky blue)
- Character: bright warm colors against nature bg
- Title: `#FFFFFF` outlined `#333300`
- *Mood: Yotsuba! — outdoor adventure, clean energy*

---

### Typography Pairings

**KOD-TYPO-01: Rounded Display**
- Rounded corners on all letterforms, medium-bold weight
- Open-source: **Nunito ExtraBold**, **Fredoka One**, **Baloo 2**
- NO sharp-cornered fonts, NO thin weights

**KOD-TYPO-02: Bubble Letter**
- Extra-bold with white outline, almost bubble effect
- Pillow implementation: stroke fill white at width 4–6px, then main color fill
- Open-source: **Titan One**, **Lilita One**

---

### Character Pose Library

| Pose ID | Name | Description |
|---------|------|-------------|
| KOD-P01 | Arms Wide Welcome | Character with both arms spread wide, biggest smile |
| KOD-P02 | Jumping Joy | Both feet off ground, arms up, pure excitement |
| KOD-P03 | Curious Lean | Head tilted, one finger on chin, quizzical but friendly |
| KOD-P04 | Holding Treasure | Character proudly holding a key object (gadget, Pokéball, etc.) |
| KOD-P05 | Running Together | Multiple characters running side by side, team energy |

---

### Background Treatment Rules

1. **White or very light field**: Most common — let character design breathe.
2. **Simple flat color**: Single pastel or primary color, perfectly flat.
3. **Basic outdoor scene**: Grass and sky, cloud elements — simplified, never realistic.
4. **Pattern ground**: Polka dots, stars, simple repeat — safe and cheerful.
5. **NEVER**: Dark or threatening backgrounds, fog, industrial settings, complex architectural detail, blood or injury indicators.

---

### Anti-Patterns

- Realistic proportions or adult anatomy
- Ambiguous or complex emotional expressions
- Dark/muted palette
- Violence or even mild combat energy
- Typography that is thin, serif-classical, or handwritten-cursive
- Cluttered or chaotic compositions

---

## 6. Isekai / Light Novel Crossover

### Overview

Isekai manga adaptation covers occupy a unique hybrid space: they are simultaneously manga and light novel advertisement. Many isekai manga are adaptations of web novels or light novels, and the cover design must satisfy both media's visual conventions. At 100px thumbnail, isekai covers are recognizable by: high-saturation illustrative style (more like game CG or light novel illustration than traditional manga), prominently featured (often overpowered-looking) protagonist with special glowing eyes or status effect visual, elaborate costume design (fantasy armor, school uniform hybrid, or elaborate casual wear that signals wealth/power), title text that is frequently very long and descriptive (LN-style title), and a tendency toward warm magical-fantasy palette (golds, magentas, teals).

Reference works: Reki Kawahara's Sword Art Online (Dengeki Comics/ASCII Media Works, manga adaptation, 2010–ongoing) — Kirito in black GGO coat, dramatic digital environment. Tappei Nagatsuki's Re:Zero (Square Enix, manga adaptation, 2014–ongoing) — Subaru and Emilia in elaborate fantasy compositions. Kugane Maruyama's Overlord (Kadokawa/Dragon Comics Age, manga adaptation, 2014–ongoing) — Ainz Ooal Gown skeleton figure in dramatic throne composition. Fuse's That Time I Got Reincarnated as a Slime (Kodansha/Sirius Comics, manga adaptation, 2015–ongoing) — Rimuru in both slime and humanoid form, bright blue/silver palette. Natsume Akatsuki's KonoSuba (Kadokawa/Dragon Comics Age, manga adaptation, 2015–ongoing) — ensemble "loser party" in comedy composition, bright palette.

**Thumbnail recognition signals:** Game-CG illustrative style. Long elaborate title. Fantasy armor/costume. Magical glowing effects. High saturation.

---

### Layout Templates

**Template ISK-01: Protagonist Power Reveal**
```
┌─────────────────────────┐
│ [TITLE — LONG, stacked] │  ← Title often 2-3 lines, descriptive
│ [small subtitle line]   │
│                         │
│    [PROTAGONIST]        │  ← Elaborate costume, glowing eyes/power
│  (semi-realistic CG     │    Background elements react to power
│   illustration style)   │
│                         │
│  [magical bg elements]  │  ← Floating runes, particles, energy
│  [AUTHOR] [ARTIST] [VOL]│  ← Often separate author + artist credits
└─────────────────────────┘
```
*Reference: Overlord v1 — Ainz on throne, elaborate dark magical environment.*

**Template ISK-02: Harem/Party Ensemble**
```
┌─────────────────────────┐
│  [TITLE — top]          │
│                         │
│  [CHAR B] [CHAR C]      │  ← Female characters flank protagonist
│       [PROTAGONIST]     │    Center figure male, flanked by party
│  [CHAR D]  [CHAR E]     │    Ecchi-adjacent: costumes elaborate
│                         │
│  [fantasy environment]  │  ← Castle, dungeon entrance, sky island
│ [AUTHOR] [ARTIST] [VOL] │
└─────────────────────────┘
```
*Reference: KonoSuba v1 — Kazuma flanked by Aqua, Megumin, Darkness.*

**Template ISK-03: Duo / Romance Focus**
```
┌─────────────────────────┐
│  [TITLE]                │
│                         │
│  [HERO]    [HEROINE]    │  ← Two-character cover, romantic framing
│  (close)   (close)      │    Heroine often more prominent than shōnen
│                         │    She faces viewer, he looks at her
│  [fantasy bg]           │
│ [AUTHOR] [ARTIST] [VOL] │
└─────────────────────────┘
```
*Reference: Re:Zero v1 — Subaru and Emilia, Emilia dominant.*

---

### Color Palette Recipes

**Palette ISK-A: "Dark Overlord" (Dark Fantasy)**
- Background: `#0D0A1A` (near-black violet)
- Mid: `#1A1530` (dark indigo)
- Glowing accents: `#9B30FF` (violet glow), `#3DFF9B` (teal energy)
- Character bone/armor: `#E8E8D0` (pale ivory)
- Title: `#D4AF37` (gold) outlined white
- *Mood: Overlord — dark power fantasy, theatrical evil*

**Palette ISK-B: "Virtual World Blue" (Game-world)**
- Background: `#001A4A` (deep navy) → `#002A7A` gradient
- UI elements: `#00D4FF` (HUD cyan)
- Character: `#1A1A1A` (black outfit), skin warm against cool bg
- Accent: `#FF4500` (health-bar orange-red)
- Title: `#FFFFFF` or `#00D4FF`
- *Mood: SAO — game aesthetic, digital environment, trapped-in-VR*

**Palette ISK-C: "Slime Aqua" (Isekai Comedy/Adventure)**
- Background: `#E0F8FF` (light aqua)
- Mid: `#80DFFF` (sky blue)
- Slime element: `#00BFFF` (pure bright blue)
- Silver/magic: `#C0C0C0`, `#E8E8FF`
- Title: `#005F8A` (dark teal) or white
- *Mood: Tensura/Slime — cheerful, non-threatening power fantasy*

**Palette ISK-D: "Comedy Fantasy"**
- Background: `#4A7FBB` (medium blue sky)
- Characters: high-saturation varied colors (red, blue, black, blonde)
- Title: `#FFD700` (gold) outlined white
- Tone: deliberately bright and approachable
- *Mood: KonoSuba — parody of isekai, bright and comedic*

---

### Typography Pairings

**ISK-TYPO-01: Dramatic Display with LN Title**
- Main series title: Bold display, often gradient-filled (gold to white)
- Full LN-style subtitle: Smaller, may be two to three lines
- Open-source for main: **Cinzel Bold** (fantasy Latin feel), **Marcellus SC**
- Volume number: Inside geometric badge or circle, gold/white

**ISK-TYPO-02: Modern Sans (Game UI)**
- Clean modern sans suggesting digital/game HUD
- Open-source: **Rajdhani Bold**, **Exo 2 Bold**

---

### Character Pose Library

| Pose ID | Name | Description |
|---------|------|-------------|
| ISK-P01 | OP Stance | Protagonist standing confidently, overpowered aura emanating |
| ISK-P02 | Throne/Seated Power | Character on throne or raised position, authority |
| ISK-P03 | Staff/Spellcast | Spellcaster mid-cast, magic circle or rune visible |
| ISK-P04 | Party Group | Ensemble arranged around hero, each character's personality visible |
| ISK-P05 | Slime Morph | Character transforming or mid-shape-shift (specifically Tensura) |
| ISK-P06 | Battle Ready | Sword drawn, shield raised, generic fantasy combat readiness |

---

### Background Treatment Rules

1. **Fantasy environment**: Castles, dungeons, forests, sky islands — rendered more realistically than shōnen bg.
2. **Magical particle effects**: Glowing motes, runes, energy fields floating around character.
3. **Game UI overlay**: HUD-style elements, level indicators, status windows (SAO-specific).
4. **Dramatic lighting**: Strong backlighting, volumetric light shafts through trees/ruins.
5. **NEVER**: Mundane real-world backgrounds without fantasy element, flat color fields without magic effects.

---

### Anti-Patterns

- Mundane contemporary setting without fantasy marker
- Muted/desaturated palette (isekai should read exciting)
- Realistic proportions without power-fantasy exaggeration
- Short, understated title text (LN titles are famously long)
- Missing magic/power visual effects on protagonist

---

## 7. Horror

### 7a. General Manga Horror

### Overview

Horror manga covers must communicate dread without alienating browsing readers — a balance between attracting the genre audience and being commercially displayable. At 100px thumbnail, horror covers signal genre through: desaturated or sickly palette (yellowed whites, dark greens, blood reds that look wrong against skin tones), character proportions or expressions that are subtly or overtly wrong (body horror, distorted faces), isolation of the figure in threatening negative space, and title typography that is either hand-scrawled/unstable-looking or hyper-legible against disturbing imagery.

Reference works: Suehiro Maruo's works use Ukiyo-e woodblock print aesthetics applied to grotesque imagery. Hideo Yamamoto's Homunculus (Shōgakukan/Big Comics Spirits, 2003–2011, 15 volumes) uses minimalist clean-line horror — the horror is in what the imagery implies, not explicit gore. Kakashi Oniyazu's Hideout (Shōgakukan, 2010) — claustrophobic cave imagery, muted terror. Dead Tube (Shōgakukan/Manga One, 2014–ongoing) — video-camera aesthetic horror, desaturated with high-contrast blood red.

**Thumbnail recognition signals:** Wrong/sickly palette. Distorted anatomy or expression. Threatening negative space. Unstable or hyper-legible title.

---

### Layout Templates

**Template HOR-01: Isolation Horror**
```
┌─────────────────────────┐
│                         │
│  [LARGE NEGATIVE SPACE] │  ← Darkness or void — threatening empty
│  (darkness / void)      │
│                         │
│    [CHARACTER/FIGURE]   │  ← Small, isolated, vulnerable
│    (small, alone)       │    OR: close-up showing wrong detail
│                         │
│  [TITLE — bottom]       │  ← Title appears after the image, not before
│  [Author]  [Publisher]  │
└─────────────────────────┘
```

**Template HOR-02: Body Horror Close-Up**
```
┌─────────────────────────┐
│  [TITLE — top]          │  ← Title anchors before the image hits
│                         │
│  ┌─────────────────┐    │
│  │  BODY PART OR   │    │  ← Extreme close-up of disturbing detail
│  │  FACE WITH      │    │    Spiral, eye wrong, mouth wrong
│  │  WRONG ELEMENT  │    │
│  └─────────────────┘    │
│                         │
│  [dark bg]              │
│  [Author]    [Vol#]     │
└─────────────────────────┘
```
*Reference: Uzumaki v1 — spiral eye close-up.*

**Template HOR-03: Before-The-Horror**
```
┌─────────────────────────┐
│  [TITLE]                │
│                         │
│  [NORMAL-SEEMING SCENE] │  ← Character appears normal, environment
│  with wrong element     │    appears normal EXCEPT for one detail
│                         │    that is deeply wrong
│  [wrong element visible]│  ← This is the focal point
│                         │
│  [Author]    [Vol#]     │
└─────────────────────────┘
```

---

### Color Palette Recipes

**Palette HOR-A: "Sickly Yellow"**
- Background: `#2A2800` (dark yellowed black)
- Mid: `#4A4600` (dark yellow-brown)
- Skin: `#D4C898` (jaundiced skin tone)
- Accent horror: `#8B0000` (deep blood red)
- Title: `#F0E080` (yellowed white) or pure red
- *Mood: Wrong, diseased, organic decay*

**Palette HOR-B: "Clinical White Fear"**
- Background: `#F8F8F8` (clinical white)
- Shadows: `#C0C0C0` (medium grey)
- Horror element: `#CC0000` (blood red), `#1A1A1A` (ink)
- Title: `#1A1A1A` bold
- *Mood: Mundane turned terrifying — the horror of normalcy*

**Palette HOR-C: "Deep Water Black"**
- Background: `#050A10` (near-black blue)
- Mid: `#0A1520`
- Illuminated element: `#E8E8E8` (cold white light)
- Horror accent: `#002244` (deep underwater blue)
- Title: `#FFFFFF` or `#CC0000`
- *Mood: Deep darkness, aquatic horror, Gyo-adjacent*

---

### 7b. Junji Ito Deep Section: The Single Uncanny Image

### Overview and Philosophy

Junji Ito's covers (Uzumaki: Shōgakukan/Big Comics Spirits, 1998–1999, 3 volumes; Gyo: Shōgakukan, 2001–2002, 2 volumes; Tomie: Asahi Shimbun Publications, collected 1987–2000, 3 volumes) represent a completely unique aesthetic philosophy that deserves separate documentation. Ito's covers are not about genre signaling — they are about delivering a single image of profound wrongness that cannot be unseen.

The core principle is: **one image, one violation of natural order, complete psychological disruption**. Everything else is subordinate to this. The title is almost always hand-lettered or in a treatment that mimics hand-lettering — imperfect, organic, as if drawn by the author themselves rather than set by a graphic designer. This is deliberate: digital perfection would create aesthetic distance from the horror. The hand-drawn title collapses that distance.

**The Mono no Aware of Wrongness**: Ito's visual language borrows from the Japanese aesthetic concept of mono no aware (物の哀れ) — the pathos of things — but inverts it. Instead of the bittersweet recognition of beauty in transience, Ito finds the horror in the wrongness that should not exist within ordinary life. A spiral that shouldn't be there. Legs that bend the wrong way. A face that keeps coming back when it should be gone.

**Restraint as Power**: Ito's covers rarely show maximum-horror content. The most disturbing element is often implied or shown in its early stage. Uzumaki v1 shows a woman's spiral-coiled hair — disturbing, but not the grotesque finale imagery. This restraint is essential: it tells the viewer something is wrong without telling them everything, which is more disturbing.

**Negative Space**: Ito uses white or near-white backgrounds extensively — because darkness is expected in horror and doesn't disturb. A body horror image floating in clean white space is more unsettling than the same image in a dark background. The cleanliness is wrong. The normalcy of the white space makes the wrong element MORE wrong.

**The Ito Palette**: Three-element palette.
- **Ink black** (`#0A0A0A`): pure sumi-e quality black for linework and shadows
- **Skin tones** (`#F5DEB3` to `#D4A484`): normal human skin rendered in its exact normalcy, which makes the wrongness more visible against it
- **One accent color**: Never more than one additional color. Usually blood red (`#8B0000` to `#CC0000`), occasionally a sickly off-white (`#F0ECD0`) or bile yellow (`#B8B040`)

**Hand-Drawn Title Treatment**:
- Title letterforms appear as if drawn with a brush or ink pen
- Weight varies within individual letterforms (thicker in middle, thinner at end strokes)
- Slight wobble or imperfection in letter placement — not cartoonishly wobbly, just human
- Open-source equivalent: **Yomogi** (Google Fonts, Japanese-style uneven brush) for Japanese titles; for Latin/romaji: **Rock Salt** or custom PILLOW path drawing with slight randomized offset per character
- Color: usually black on white, occasionally red on white or white on dark
- Background rule: title should have breathing room — not compressed, not crowded

**Negative Prompt Specifics for Ito-Style Generation**:
- NO energy bursts, speed lines, magical effects
- NO multiple horror elements competing (one is enough)
- NO dark brooding background (use white/light background)
- NO elaborate decorative elements (typography must be minimal)
- NO color palette beyond the three-element Ito palette
- NO stylized chibi or anime exaggeration — Ito's horror depends on realistic proportions

**Layout Template: Ito Single Uncanny**
```
┌─────────────────────────┐
│                         │
│  [TITLE — hand-lettered]│  ← Hand-drawn feel, black on white
│  [small subtitle]       │    Placed naturally, not formatted
│                         │
│  [WHITE / LIGHT SPACE]  │  ← 30-50% empty space
│                         │
│  [SINGLE WRONG IMAGE]   │  ← ONE element of wrongness
│  (realistic rendering,  │    Detailed, precise, not cartoony
│   one body part/detail) │    Human scale
│                         │
│  [Author] [Publisher]   │  ← Minimal, understated
└─────────────────────────┘
```

**Iconic Cover Analysis**:
- *Uzumaki v1* (1998): Kirie Goshima with spiral-coiled hair, face partially obscured, white background. The hair is the horror. Everything else is normal.
- *Gyo v1* (2001): A dead fish with mechanical spider legs — the wrongness is in the combination of organic and mechanical. Clean white background.
- *Tomie v1* (collected): Tomie's beautiful face — but something in the eyes is wrong. Beauty as horror. The horror is invisible unless you look carefully.

---

## 8. Sports

### Overview

Sports manga covers are among the most consistently legible at thumbnail size, because they leverage universal sports iconography: jerseys, equipment, athletic poses, and the specific color identity of the sport. At 100px, the recognition signals are: a character in athletic motion or readiness, sport-specific equipment visible (volleyball, basketball, soccer ball, etc.), team color palette (which often becomes the dominant background color), high energy composition similar to shōnen but constrained by real-world setting, and title typography that often incorporates the sport's motion energy.

Reference works: Takehiko Inoue's Slam Dunk (Shūeisha/Jump Comics, 1990–1996, 31 volumes) — basketball orange palette, Sakuragi's distinctive red hair, dynamic court compositions. Haruichi Furudate's Haikyuu!! (Shūeisha/Jump Comics, 2012–2020, 45 volumes) — orange and black volleyball team colors dominant, Hinata's explosive jumping energy. Muneyuki Kaneshiro's Blue Lock (Kodansha/Weekly Shōnen Magazine, 2018–ongoing, 29 volumes) — dark/elite aesthetic, soccer ball, royal blue and black. Tadatoshi Fujimaki's Kuroko's Basketball (Shūeisha/Jump Comics, 2008–2014, 30 volumes) — basketball game colors, Kagami and Kuroko duo compositions. Yoichi Takahashi's Captain Tsubasa (Shūeisha/Jump Comics, 1981–1988, 37 volumes; multiple continuations) — soccer ball and field greens, yellow and blue uniform colors.

**Thumbnail recognition signals:** Sport equipment visible. Athletic motion pose. Team color dominance. Dynamic energy similar to shōnen but real-world coded.

---

### Layout Templates

**Template SPT-01: Athletic Action Foreground**
```
┌─────────────────────────┐
│ [BADGE] [TITLE — large] │
│                         │
│   [CHARACTER in full    │  ← Athletic body in peak motion
│    athletic motion]     │    Jump, spike, dribble, shoot
│                         │
│  [SPORT EQUIPMENT]      │  ← Ball or equipment visible in frame
│  prominently featured   │    May be motion-blurred
│                         │
│  [simplified court/     │  ← Ground plane established, nothing more
│   field environment]    │
│ [Author]   [Vol#]       │
└─────────────────────────┘
```
*Reference: Slam Dunk v1 — Sakuragi dribbling, basketball court bg, orange dominant.*

**Template SPT-02: Determination Close-Up with Sport Element**
```
┌─────────────────────────┐
│  [TITLE]                │
│                         │
│  [FACE — fierce,        │  ← Determined expression, sweat visible
│   determined, athlete]  │    Characteristic feature (hair, eyes)
│                         │
│  [SPORT ELEMENT]        │  ← Ball partially visible, equipment edge
│  [in foreground]        │    or motion lines behind
│                         │
│  [team color bg]        │  ← Flat team color as background
│  [Author]    [Vol#]     │
└─────────────────────────┘
```
*Reference: Haikyuu!! v1 — Hinata face close-up, volleyball behind, orange field.*

**Template SPT-03: Team Formation**
```
┌─────────────────────────┐
│  [TITLE]                │
│                         │
│  [FULL TEAM]            │  ← All or most team members
│  (formation shot,       │    Arranged in strategic formation
│   jersey numbers visible│    Captain front-center
│   uniforms match)       │
│                         │
│  [stadium/court bg]     │  ← Implied environment, simplified
│ [Author]    [Vol#]      │
└─────────────────────────┘
```
*Reference: Kuroko's Basketball — Seirin team formation covers.*

---

### Color Palette Recipes

**Palette SPT-A: "Basketball Orange"**
- Background: `#FF6B00` (basketball orange)
- Character uniform: `#CC4400` (dark orange) and `#FFFFFF`
- Sweat/motion: `#FFD4A0`
- Title: `#1A1A1A` or `#FFFFFF`
- *Mood: Slam Dunk — hot, high-energy, game-day*

**Palette SPT-B: "Volleyball Arena"**
- Background: `#FF7A00` (Karasuno orange) with `#1A1A1A` (black)
- Net white: `#FFFFFF`
- Title: Bold black or white
- *Mood: Haikyuu!! — contrast-driven, team colors as identity*

**Palette SPT-C: "Elite Blue" (Blue Lock / prestige sports)**
- Background: `#0A1A3A` (deep navy)
- Accent: `#0040FF` (royal electric blue)
- Character: high-contrast against dark bg
- Title: `#FFFFFF` or `#00BFFF`
- *Mood: Blue Lock — elite, cold, competitive, dark sports psychological*

**Palette SPT-D: "Field Green"**
- Background: `#1A7A1A` (football/soccer field green)
- Lines: `#FFFFFF` (field markings)
- Character: Yellow/blue uniform or warmth against green
- Title: `#FFFFFF` outlined `#006600`
- *Mood: Captain Tsubasa — outdoor, sunlit, classic soccer*

---

### Character Pose Library

| Pose ID | Name | Description |
|---------|------|-------------|
| SPT-P01 | Jump Spike | Full airborne spike motion (volleyball), body at apex |
| SPT-P02 | Dribble Drive | Basketball dribble in motion, body low, eyes forward |
| SPT-P03 | Serve Stance | Volleyball serve or tennis serve ready position |
| SPT-P04 | Header Jump | Soccer header, body airborne, head making contact |
| SPT-P05 | Sprint Forward | Running at full speed, athletic body in perfect sprint form |
| SPT-P06 | Victory Celebration | Arms raised, team celebrating a point |
| SPT-P07 | Goalkeeper Dive | Horizontal dive, full body extension |
| SPT-P08 | The Stare-Down | Eyes locked on opponent, pre-match intensity |
| SPT-P09 | Equipment Feature | Character holding/presenting ball or equipment as central element |
| SPT-P10 | Team Stack | Team members in playful stack or huddle, bonding energy |

---

### Background Treatment Rules

1. **Sport venue implied**: Court lines, goal posts, net elements — functional, minimal.
2. **Team color field**: Single team color as background — powerful brand identity function.
3. **Dynamic motion lines**: Similar to shōnen but directed specifically from sport action.
4. **Stadium/crowd silhouette**: Crowd in background as texture, never individual faces.
5. **Outdoor field**: Green field at base, sky above — simple two-tone environment.
6. **NEVER**: Fantasy/magical backgrounds, nature scenes unrelated to sport, dark horror-influenced treatment.

---

### Vol.1 vs. Later Volume Conventions

- **Vol.1**: Establish sport and protagonist clearly. Team colors introduced.
- **Tournament arc volumes**: Opponent team's colors may appear on covers as foil — cover palette shifts to match the drama of that arc's rival.
- **Final volumes**: Championship composition. Team together. May feature the sport itself (the ball, the net, the court) without characters — letting the setting speak.

---

### Anti-Patterns

- Soft pastel palette (unless intentional comedy/gender-flip context)
- Non-sport environment backgrounds
- Character not in athletic context (school uniform without sport element)
- Floral or romantic decorative elements
- Overly fantastical power effects (some sports manga like Blue Lock allow this, but it's a late-series escalation, not Vol.1)

---

## 9. Slice-of-Life / Iyashikei

### Overview

Iyashikei (癒し系, "healing-type") covers are among the most deceptively challenging to generate programmatically, because their power comes from what they withhold: drama, conflict, visual noise, urgency. At 100px thumbnail, the recognition signals are: soft natural light palette (warm afternoon yellows, gentle greens, sky blues, cream), a character in a relaxed non-action pose in a quiet setting (reading, cooking, looking at nature, simply existing), substantial environmental detail that places equal or greater emphasis on place than person, and a title typography treatment that is gentle and unhurried.

Reference works: Kiyohiko Azuma's Yotsuba! (Dengeki Comics, 2003–ongoing, 15+ volumes) — Yotsuba's pure uncomplicated joy in ordinary moments, covers always feature a specific activity or discovery (bubbles, sunflowers, camping), palette warm and clean. Satsuki Yoshino's Barakamon (Square Enix/Gangan Comics, 2009–2019, 18 volumes) — calligrapher in rural island setting, natural materials, warm summer palette. Atto's Non Non Biyori (Media Factory/MF Comics, 2009–2021, 15 volumes) — four girls in four-seasons rural Japan, covers use seasonal palette shifts as primary design driver. Chihiro Ishizuka's Flying Witch (Kodansha/Bessatsu Shōnen Magazine, 2012–ongoing, 16 volumes) — witch in countryside setting, gentle magic, natural palette. Kozue Amano's Aria (Mag Garden/Blade Comics, 2001–2008, 12 volumes) — gondolier on Neo-Venezia canals, water light, European-Japan fantasy palette.

**Thumbnail recognition signals:** Natural light palette. Quiet environmental setting. Relaxed non-action character. Seasonal color coding. Unhurried typography.

---

### Layout Templates

**Template IYA-01: Character in Landscape**
```
┌─────────────────────────┐
│  [TITLE — gentle,       │  ← Soft typography, never aggressive
│   upper corner]         │    Often title placed like a caption
│                         │
│  [ENVIRONMENT/NATURE]   │  ← Background is almost as important
│  (sky, field, season)   │    as character — equal partnership
│                         │
│    [CHARACTER]          │  ← Character smaller than in action genres
│  (sitting, lying, doing │    Embedded in environment, not dominating
│   quiet activity)       │
│ [Author]    [Vol#]      │
└─────────────────────────┘
```
*Reference: Non Non Biyori — four girls in seasonal rural landscape, equal composition.*

**Template IYA-02: Activity Feature**
```
┌─────────────────────────┐
│  [TITLE]                │
│                         │
│  [CHARACTER doing       │  ← Activity is the cover's story
│   specific activity]    │    Fishing, painting, cooking, reading
│                         │
│  [ACTIVITY PROP         │  ← Props for the activity visible and
│   VISIBLE / DETAILED]   │    lovingly rendered
│                         │
│  [warm natural bg]      │
│  [Author]    [Vol#]     │
└─────────────────────────┘
```
*Reference: Barakamon v1 — Handa calligraphy brush, paper, rural house interior.*

**Template IYA-03: Seasonal Single Image**
```
┌─────────────────────────┐
│  [TITLE — left edge]    │
│                         │
│  [SEASONAL ELEMENT      │  ← Season dominates: snow, sakura,
│   FILLS FRAME]          │    sunflowers, autumn leaves
│                         │
│  [CHARACTER SMALL       │  ← Character small within season
│   WITHIN SEASON]        │    Season is the protagonist here
│                         │
│  [Author]    [Vol#]     │
└─────────────────────────┘
```
*Reference: Flying Witch — seasonal countryside, Makoto small within big sky.*

---

### Color Palette Recipes

**Palette IYA-A: "Summer Afternoon"**
- Background sky: `#87CEEB` → `#4A9FD4`
- Ground: `#90EE90` (light green) or `#D4B48C` (dry grass)
- Sunlight: `#FFE680` (warm yellow highlight)
- Character shadow: `#A0A0C0` (cool lavender shadow from overhead sun)
- Title: `#3A5A3A` (deep warm green) or dark blue
- *Mood: Yotsuba!/Non Non Biyori — pure summer, pure childhood contentment*

**Palette IYA-B: "Autumn Warmth"**
- Background: `#D4703A` (autumn leaf orange)
- Foliage: `#8B2500` (deep rust), `#D4A030` (golden yellow)
- Character coat/clothes: `#5A3A1A` (dark warm brown)
- Sky: `#B0C8E0` (cool autumn sky)
- Title: `#1A0A00` (near-black brown) or cream
- *Mood: Seasonal contentment, harvest, impermanence*

**Palette IYA-C: "Canal Water Light"**
- Background water: `#4090C0` (Mediterranean blue)
- Reflection: `#80C0E0` (lighter water reflection)
- Buildings: `#F0E0C0` (warm European plaster)
- Character: warm uniform against cool water
- Title: `#1A4A7A` (deep water blue)
- *Mood: Aria — Neo-Venezia, water and light, serenity*

**Palette IYA-D: "Winter Interior"**
- Background: `#E8E8F0` (pale winter light)
- Interior warmth: `#F4C882` (lamp/hearth glow)
- Outside cold: `#B0B8C8` (winter grey-blue through window)
- Title: `#2A1A0A` (dark warm brown)
- *Mood: Sheltered warmth against cold outside, cozy interior*

---

### Typography Pairings

**IYA-TYPO-01: Light Humanist**
- Title in light-to-medium weight humanist sans or serif
- Open-source: **Nunito Light**, **Quicksand**, **Raleway Light**
- Author name same weight as title — no hierarchy, gentle equality

**IYA-TYPO-02: Handwritten Natural**
- Title appears hand-lettered but in a gentle way (not horror-jagged)
- Open-source: **Caveat**, **Klee One** (Google Fonts)
- Natural imperfection without anxiety

---

### Character Pose Library

| Pose ID | Name | Description |
|---------|------|-------------|
| IYA-P01 | Looking at Sky | Lying on back or sitting, looking upward at sky or clouds |
| IYA-P02 | Quiet Work | Absorbed in a craft or task — writing, painting, knitting |
| IYA-P03 | Walk in Nature | Gentle walking pace through natural environment |
| IYA-P04 | Food Moment | Character with bowl/plate of food, warm expression of anticipation |
| IYA-P05 | Animal Companion | Interacting gently with a cat, dog, small creature |
| IYA-P06 | Window Light | Seated by window, light falling across face, reading or daydreaming |
| IYA-P07 | Seasonal Discovery | Noticing and responding to a seasonal element — first snow, first bloom |

---

### Background Treatment Rules

1. **Rich natural environment**: The environment in iyashikei is not background — it is part of the subject. Render it with care.
2. **Season-specific accuracy**: Spring elements in spring, autumn in autumn. Seasonal color palette DRIVES everything.
3. **Interior with good light**: Windows, lamps, warm light from within.
4. **Water**: Canals, rivers, rain puddles — water reflects and doubles the world.
5. **NEVER**: Speed lines, energy effects, dramatic lighting for action, dark brooding palette, conflict or tension visuals.

---

### Anti-Patterns

- Action poses or combat
- High-saturation primary palette
- Speed lines or energy burst backgrounds
- Publisher badge in prominent aggressive style
- Heavy or aggressive title typography
- Urban industrial backgrounds
- Multiple competing visual elements fighting for attention

---

## 10. BL / GL

### Overview

Boys' Love (BL) and Girls' Love (GL) covers share visual DNA with shōjo but encode genre-specific signals. At 100px thumbnail: BL covers feature two male characters in close physical proximity (shoulder touching, forehead-to-forehead, one looking at the other who is looking away), often in a composition that implies desire or tension; GL covers similarly feature two female characters with visible emotional intimacy, frequently in more delicate/impressionistic compositions. Both BL and GL covers are often more explicitly aestheticized than general shōjo — more attention to clothing detail, more deliberate about eye contact between characters, more use of negative space to frame the couple.

Reference works BL: Rihito Takarai's Given (Shinshokan, 2013–ongoing, 8 volumes) — musicians in washed-out indie aesthetic, music equipment visible, soft grey-blue palette; exceptional restraint for BL. Yamane Ayano's Finder Series (Biblos → Libre, 2002–ongoing) — dramatic dark-tone compositions with yakuza aesthetic, very different from Given's softness. Reference works GL: Nakatani Nio's Bloom Into You (Dengeki Comics, 2015–2019, 8 volumes) — school setting, two girls in intimate proximity, cherry blossom and school uniform palette. Takako Shimura's Aoi Hana / Whispered Words (Ohzora Publishing / Media Factory) — delicate illustration quality, pale palette, emotional restraint.

**Thumbnail recognition signals:** Two characters in intimate spatial relationship. Emotional tension or tenderness. Sophisticated palette (not primary-saturated). Characters of same gender.

---

### Layout Templates

**Template BL-01: The Almost-Touch**
```
┌─────────────────────────┐
│  [TITLE — upper area]   │
│                         │
│  [CHAR A]  [CHAR B]     │  ← Two figures very close
│  (one leaning into      │    One reaching toward the other
│   the other)            │    Spatial axis: tension between them
│                         │
│  [soft bg / environment]│  ← Nothing harsh — everything is
│                         │    serving the emotional focal point
│ [Author]    [Vol#]      │
└─────────────────────────┘
```
*Reference: Given v1 — Ritsuka and Mafuyu, guitar case between them, washed-out palette.*

**Template BL-02: Face Study Duo**
```
┌─────────────────────────┐
│  [TITLE]                │
│                         │
│  [FACE A]               │  ← Faces in close proximity
│         [FACE B]        │    One looking at viewer, one looking at A
│  (overlapping frame)    │    Emotional communication in eyes
│                         │
│  [minimal bg]           │
│ [Author]    [Vol#]      │
└─────────────────────────┘
```

**Template GL-01: Girls Together in Environment**
```
┌─────────────────────────┐
│  [TITLE — elegant]      │
│                         │
│  [ENVIRONMENT ELEMENT]  │  ← School hallway, garden, room detail
│  (school/domestic)      │
│                         │
│  [CHAR A] [CHAR B]      │  ← Two girls, physical closeness
│  (side by side, hands   │    intimacy implied through proximity
│   close or touching)    │    School uniforms or period dress
│                         │
│ [Author]    [Vol#]      │
└─────────────────────────┘
```
*Reference: Bloom Into You v1 — Yuu and Touko in school setting, spring palette.*

---

### Color Palette Recipes

**Palette BL-A: "Indie Music Washed" (Given-style)**
- Background: `#D8D8E8` (grey-lavender, film-washed)
- Mid: `#B8B8C8`
- Characters: warm skin against cool bg
- Accent: `#6080A0` (muted blue-slate)
- Title: `#2A2A3A` (near-black with slight warmth)
- *Mood: Modern, indie, music scene, emotional restraint*

**Palette BL-B: "Dark Desire" (Finder-style)**
- Background: `#0A0A14` (very dark navy-black)
- Mid: `#1A1A2A`
- Character 1 (dominant): dark suit against dark bg
- Character 2 (focus): pale skin, illuminated
- Accent: `#8B0000` (dark red) or `#4A4A8A` (deep indigo)
- Title: `#C0C0D8` (pale silver-blue) or `#D4AF37` (gold)
- *Mood: Power dynamic, dangerous attraction, adult BL*

**Palette GL-A: "Cherry Blossom School"**
- Background: `#FFF0F5` (sakura blush) → `#F8E8EE`
- Uniform: `#4A6A8A` (school navy) and `#FFFFFF`
- Floral accent: `#FFB7C5` (sakura pink)
- Title: `#6A2A4A` (deep rose) or navy
- *Mood: Bloom Into You — tender, school-age, spring*

**Palette GL-B: "Literary Pale"**
- Background: `#F5F0E8` (warm cream/parchment)
- Character: soft watercolor-adjacent rendering
- Accent: `#C0A080` (warm sepia)
- Title: `#5A3A2A` (dark warm brown)
- *Mood: Aoi Hana / Shimura style — literary, delicate, understated*

---

### Typography Pairings

**BL-TYPO-01: Restraint Serif**
- Light-to-medium weight serif, classical
- Open-source: **Cormorant Garamond Light/Regular**, **EB Garamond**
- Title does NOT need to be large — intimacy over announcement

**GL-TYPO-01: Delicate Modern**
- Thin to light sans, high tracking (letter-spacing)
- Open-source: **Lato Light**, **Raleway Thin/Light**

---

### Character Pose Library

| Pose ID | Name | Description |
|---------|------|-------------|
| BL-P01 | Forehead Rest | One character's forehead resting on the other's — maximum intimacy |
| BL-P02 | The Shoulder Glance | One looks at the other who isn't looking back — longing |
| BL-P03 | From Behind | One character's arms around the other from behind |
| BL-P04 | Music Together | Musicians side-by-side with instruments |
| GL-P01 | Hand Offering | One extends hand to other, palm up — invitation |
| GL-P02 | Shoulder Lean | One leans head on other's shoulder |
| GL-P03 | Facing Each Other | Full frontal two-shot, eye contact, equal positioning |

---

### Background Treatment Rules

1. **Environment as emotional metaphor**: Music venue, school, garden — always tied to the emotional story.
2. **Soft gradient field**: Single color or two-tone gradient, never busy.
3. **Scatter elements**: Cherry blossoms, musical notes, light particles — restrained.
4. **Interior with character**: Bedroom, music room — intimate space.
5. **NEVER**: Action elements, combat, large crowds, sports venues (unless sport is the setting).

---

### Anti-Patterns

- Characters facing away from each other with no emotional connection
- Aggressive action poses
- High-saturation primary palette
- Speed lines or energy bursts
- Chibi/comic relief expressions
- Absence of emotional intimacy between the two characters

---

## 11. Mecha

### Overview

Mecha covers face a unique design challenge: they must feature a giant robot prominently (the product, the brand, the spectacle) while maintaining visual interest beyond mechanical detail cataloguing. At 100px thumbnail: the recognition signals are a large, complex mechanical form (angular, industrial, often military in appearance), a dramatically lit environment (space, battlefield, city under attack), a high-contrast palette (metallic greys + one or two strong accent colors), and either no human character or a very small human figure dwarfed by the mecha (emphasizing scale). The title typography tends toward the geometric and mechanical — clean, angular, industrial.

Reference works: Yoshikazu Yasuhiko's Mobile Suit Gundam: The Origin (Kadokawa/Angle Comics, 2001–2011, 12 volumes) — RX-78-2 Gundam in space, white/blue/red military colors, detailed mechanical rendering. Hideaki Anno/Yoshiyuki Sadamoto's Neon Genesis Evangelion (Kadokawa/Dragon Comics, 1994–2013, 14 volumes) — Eva Unit-01 with purple and green, often in partially revealed or damaged state suggesting horror. Goro Taniguchi/Majiko's Code Geass (Kadokawa, 2006–2009) — Lancelot in dramatic battle poses, sleek white mecha against dark bg. Tsutomu Nihei's Knights of Sidonia (Kodansha/Afternoon, 2009–2015, 15 volumes) — Tsugumori in space, hard sf aesthetic, mechanical precision.

**Thumbnail recognition signals:** Large mechanical form. Industrial/military palette (grey/metal + accent). Space or battlefield environment. Scale relationship between mecha and world.

---

### Layout Templates

**Template MEC-01: Mecha Dominant**
```
┌─────────────────────────┐
│  [TITLE — top, angular] │  ← Geometric, mechanical typography
│                         │
│  [MECHA FIGURE          │  ← Mecha fills 60-80% of canvas
│   DOMINANT]             │    Viewed from below (more imposing)
│                         │    Detail visible — not silhouette
│  [small human pilot     │  ← Human tiny relative to machine
│   or absent]            │
│  [ENVIRONMENT]          │  ← Space, rubble, sky — simplified
│  [Author] [Vol#]        │
└─────────────────────────┘
```
*Reference: Gundam: The Origin v1 — RX-78-2 in battle stance, Earth limb visible in bg.*

**Template MEC-02: Pilot + Machine**
```
┌─────────────────────────┐
│  [TITLE]                │
│                         │
│  [PILOT PORTRAIT]       │  ← Human face/figure in foreground
│  (upper half)           │    Determined or troubled expression
│                         │
│  [MECHA LARGE]          │  ← Mecha looms behind/beneath pilot
│  (behind/below pilot)   │    Scale: pilot is large, mecha still huge
│                         │
│  [bg: space/battlefield]│
│  [Author] [Vol#]        │
└─────────────────────────┘
```
*Reference: Evangelion v1 — Shinji and Eva Unit-01 in composition.*

**Template MEC-03: Battle Action**
```
┌─────────────────────────┐
│  [TITLE]                │
│                         │
│  [MECHA IN ACTION]      │  ← Two mecha fighting OR one mecha in
│  (mid-battle)           │    dramatic action pose, weapons visible
│                         │
│  [ENEMY MECHA]          │  ← Second mecha as opponent
│  (smaller or similar    │
│   scale, different color│
│   palette)              │
│  [explosion/bg]         │
│  [Author] [Vol#]        │
└─────────────────────────┘
```

---

### Color Palette Recipes

**Palette MEC-A: "Federation White" (Gundam-style)**
- Background: `#000820` (space black)
- Stars: `#FFFFFF` (white points)
- Mecha primary: `#FFFFFF` (white armor)
- Mecha accent: `#003399` (Gundam blue), `#CC0000` (Gundam red)
- Title: `#FFFFFF` or `#D4AF37` (gold)
- *Mood: Classic heroic robot, military SF, bright clear sides*

**Palette MEC-B: "Evangelion Purple"**
- Background: `#0A0A1A` (deep cold night)
- Eva armor: `#4A1A6A` (Eva purple), `#1A6A4A` (Eva green accent)
- Blood/LCL: `#FF3300` (orange-red)
- Title: `#D4AF37` or `#FFFFFF`
- *Mood: Horror mecha, body horror, psychological darkness*

**Palette MEC-C: "Hard SF Monochrome"**
- Background: `#080808` (near-black)
- Mecha: `#707070` (medium grey), `#A0A0A0` (light grey highlights)
- Accent: `#C0FF00` (cyberpunk green) or `#00AAFF` (cold blue)
- Title: `#FFFFFF`
- *Mood: Knights of Sidonia — hard SF, biological/mechanical, cold and precise*

**Palette MEC-D: "Knightmare White" (Code Geass-style)**
- Background: `#1A1A2A` (dark indigo)
- Mecha: `#F8F8F8` (bright white, Lancelot)
- Glow: `#80E0FF` (Hadron Canon blue-white glow)
- Title: `#D4AF37` (gold) — Royal aesthetic
- *Mood: Noble mecha, political intrigue, sophisticated conflict*

---

### Typography Pairings

**MEC-TYPO-01: Industrial Angular**
- Geometric sans, slight military/technical feel
- Open-source: **Orbitron**, **Rajdhani Bold**, **Share Tech Mono**
- Title may include series acronym in same weight

**MEC-TYPO-02: Compressed Heroic**
- Ultra-condensed bold display — similar to shōnen but harder-edged
- Open-source: **Bebas Neue**, **Barlow Condensed Black**
- Often in white with no stroke (mecha bg handles the contrast)

---

### Character Pose Library (Mecha-Specific)

| Pose ID | Name | Description |
|---------|------|-------------|
| MEC-P01 | Standing Guardian | Mecha standing upright, arms slightly away from body, weapon at side |
| MEC-P02 | Shield Raise | One arm raised with shield or armored forearm blocking |
| MEC-P03 | Weapon Draw | Mecha pulling beam saber or large weapon into position |
| MEC-P04 | Aerial Assault | Mecha diving from above at angle, beam rifle aimed |
| MEC-P05 | Damaged Kneeling | One knee down, damage visible, still functional — earned resilience |
| MEC-P06 | Transformation Mid | Caught in transformation sequence, vehicle and mecha simultaneously |
| MEC-P07 | Close-Up Cockpit | Pilot visible in cockpit, reaction to battle |
| MEC-P08 | Scale Establishing | Mecha beside a city building — pure scale reference shot |

---

### Background Treatment Rules

1. **Space**: Stars, planet limbs, asteroid fields — the classic mecha environment.
2. **Ruined city**: City silhouette with destruction, fires — Earth-based conflict.
3. **Alien/hostile environment**: Atmospheric haze, unusual color sky, colony interior.
4. **Explosion/energy**: Beam weapon impact, missile trails, energy discharge.
5. **Abstract mechanical**: Gears, circuitry pattern, schematic lines — used on collector editions or special volumes.
6. **NEVER**: Natural pastoral environments (unless explicit plot contrast), kawaii/soft decorative elements, bright pastoral colors.

---

### Anti-Patterns

- Soft or pastel palette
- Character-only covers without mecha visible
- Romantic/intimate character poses as primary composition
- Botanical or floral decorative elements
- Thin, script, or handwritten typography
- Realistic human scale (mecha must read as enormous)

---

## Appendix: Cross-Genre Technical Notes for FLUX/ComfyUI Implementation

### Prompt Construction Hierarchy

For each genre cover, structure FLUX prompts in priority order:
1. **Lighting and color palette** — the first thing the model encodes
2. **Character pose and expression** — constrained by genre pose library
3. **Costume/clothing/equipment** — genre-specific markers
4. **Background treatment** — as specified per genre rules
5. **Typography treatment** — handled in post-processing (Pillow) not in FLUX
6. **Publisher badge** — always Pillow post-processing overlay

### Typography in Pillow (Post-Processing)

All title text should be rendered in Pillow after FLUX image generation:
- Load font from Google Fonts equivalents listed per genre
- Apply at target resolution (minimum 1200×1800px for B6 trim)
- Stroke implementation: `ImageDraw.text()` with `stroke_width` parameter
- Volume number: separate text element, positioned per genre template
- Author byline: 20% scale of title font size, minimum

### Negative Prompt Building

Combine the anti-patterns sections from the target genre with these universal negatives:
`lowres, bad anatomy, blurry, jpeg artifacts, watermark, text-on-image (use Pillow), ugly, poorly drawn, extra limbs, cloned face, gross proportions, deformed, mutation, disfigured, bad proportions, missing limbs, extra digit, fewer digits, cropped, worst quality`

Add genre-specific negatives from each section's anti-patterns list.

### Resolution and Aspect Ratio

- **Standard B6 Japanese tankōbon trim**: 112mm × 175mm → Use 0.64:1 aspect ratio
- **FLUX native**: 1024×1024 → for portrait covers use 832×1216 or 768×1152
- **Final cover including spine**: requires canvas extension (handled in Pillow composition stage)
- **Safe area**: maintain 5mm bleed on all edges for print; 8mm inset from edges for all text elements

---

*Document version 1.0 — Reference for programmatic manga cover generation system*
*All works cited are registered trademarks of their respective publishers and authors*
