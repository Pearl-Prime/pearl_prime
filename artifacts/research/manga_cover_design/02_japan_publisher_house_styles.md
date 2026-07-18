# Japan Publisher House Styles
## Programmatic Cover Generation Reference — 8 Major Publishers

**Version:** 1.0 | **Audience:** Image generation engineers | **Purpose:** Publisher-accurate cover synthesis for FLUX/ComfyUI system

---

## Table of Contents

1. [Shūeisha](#1-shūeisha)
2. [Kodansha](#2-kodansha)
3. [Shōgakukan](#3-shōgakukan)
4. [Kadokawa](#4-kadokawa)
5. [Square Enix](#5-square-enix)
6. [Hakusensha](#6-hakusensha)
7. [Akita Shoten](#7-akita-shoten)
8. [Ichijinsha and Specialty Publishers](#8-ichijinsha-and-specialty-publishers)
9. [The Jump Comics Cover Stamp System](#9-the-jump-comics-cover-stamp-system)
10. [Tankōbon Book Production Specs](#10-tankōbon-book-production-specs)

---

## 1. Shūeisha

### a) Visual Identity Markers at Thumbnail Scale (50–100px)

Shūeisha's Jump Comics imprint is the single most visually recognizable publisher identity in the manga industry worldwide. At 50px, a Jump Comics volume is identified by: a saturated warm-colored cover (orange, red, yellow dominant — the "Jump palette"), and — most critically — a red-and-gold rectangular badge in the upper-left corner bearing the Jump logo and "COMICS" text. This badge is the publisher's most powerful thumbnail-scale identifier. No other major publisher uses this badge format in this corner position with this color combination. The badge itself is approximately 18–22% of the cover width and occupies the top 8–10% of cover height.

The Shūeisha logo (the Chinese character 集 in a square or the roman "SHUEISHA") typically appears on the spine in white on a red field. On the back cover it appears small, bottom-right, alongside the ISBN barcode block.

### b) Logo / Imprint Badge Design

**Jump Comics badge** (Jump Comics, Jump SQ, V-Jump, etc.):
- Shape: Horizontal rectangle with slight optical refinement at corners
- Color field: `#CC0000` (deep red) for the lower portion with "COMICS" text; `#D4AF37` (gold/yellow) for the upper "JUMP" wordmark background OR white letters on red field (variant by era)
- Typography of badge: Bold condensed sans, white text
- Placement: Upper-left corner, touching both top edge and left edge
- Size: approximately 70px wide × 30px tall at standard cover dimensions (112×175mm)

**Margaret Comics badge** (shōjo line):
- Similar rectangular badge format but in pink/magenta (`#CC3388`) with white "Margaret Comics" text
- Same upper-left placement convention

**Ultra Jump badge** (seinen line):
- Dark charcoal or black badge with white text, more understated than Jump Comics
- Signals: adult/serious audience rather than jump-energy excitement

### c) Title Typography Conventions

- Jump Comics: Ultra-bold, almost always all-caps for romaji; large kanji characters for Japanese titles. Heavy black stroke outline against cover illustration. Title color varies by cover — often white, yellow, or red depending on background.
- No house-mandated font (each title has its own treatment) but the visual convention is: maximum weight, maximum stroke, maximum legibility at distance.
- Volume number: White or yellow numeral inside or adjacent to a small colored badge or box, lower-right area of the front cover, sometimes immediately below the title.
- Author credit: Very small, typically at the bottom of the cover, often obscured or reduced.

### d) Spine Design

The Jump Comics spine is one of the most recognizable spine designs in publishing:
- **Spine color**: Varies by title (not standardized across imprint), but the Jump logo appears in a standardized position.
- **Jump logo on spine**: Red block at top of spine with "JUMP COMICS" or "JC" abbreviation in white.
- **Title on spine**: Large, same font treatment as front cover, vertical (top-to-bottom reading direction standard in Japan).
- **Volume number**: Bold numeral at bottom of spine, easy to read on bookshelf.
- **Barcode placement**: Barcode is on the back cover, not the spine.
- *Shelf-ID function*: A complete Naruto series (72 volumes) on a shelf creates a block of identical orange-spined books with the Jump red top-badge visible — an extremely powerful brand presence.

### e) Back Cover Layout Template

```
┌─────────────────────────┐
│  [SERIES LOGO small]    │  ← Same as front cover title, smaller
│                         │
│  [CHARACTER ART]        │  ← Secondary illustration, often a
│  (small, decorative)    │    different character than front cover
│                         │
│  [BLURB TEXT]           │  ← Story summary, 80–120 words max
│  (approx 10pt)          │    White or light paper shows through
│                         │
│  [AUTHOR NAME]          │
│  [PRICE] ¥XXX+tax       │
│                         │
│  [JUMP COMICS logo]  [ISBN/BARCODE block]
└─────────────────────────┘
```
- ISBN barcode block: lower-right, white box containing barcode + ISBN number + price code
- Background color: usually continues from front cover color field or uses a contrasting secondary color from the cover palette
- Author credit appears again, slightly larger than on front

### f) Inner Jacket Convention

Japanese tankōbon use dust jackets (obi + outer jacket) over a separate printed inner cover board. For Jump Comics:
- **Outer jacket (dust jacket)**: The full-color illustrated cover visible in bookstores
- **Inner cover** (visible when jacket removed): Usually a two-color or single-color print on the board itself — often a simplified or sketch version of the cover art, or a portrait of the author, or a simple color field with series logo
- **Inner jacket flaps**: Front flap contains author profile/photo and short bio. Back flap contains brief summary of the volume's contents or a message from the author.
- **Author note (atogaki)**: Often a 4-koma (four-panel comic) or handwritten-style note at the back of the inner jacket, or inside the book's back matter.

### g) Paper and Production Signature

- **Jump Comics standard**: Glossy full-color dust jacket over slightly cream-tinted inner board
- **Interior pages**: Cream-tinted newsprint for serialization reprints; slightly better quality paper for deluxe/kanzenban editions
- **Detection from cover photo**: Glossy jacket produces visible reflection in photographs; slight cream tint visible at spine/edge
- **Kanzenban editions** (Complete editions, e.g., Naruto Collector's Edition): Larger trim size, higher quality paper, foil spine accents — detectable by thicker spine and premium feel

### h) Characteristic Color Palettes

Shūeisha/Jump has a house bias toward high-saturation warm palettes across its shōnen line:
- Orange: `#FF6B1A` — Naruto, One Piece
- Red: `#CC0000` — Jump badge, Demon Slayer accents
- Yellow: `#FFE800` — Dragon Ball, electric accent
- Blue (contrast): `#0033CC` — My Hero Academia, contrast against warm titles

Margaret Comics (shōjo) skews pink/lavender:
- `#FF69B4`, `#CC44AA`, `#DDA0DD`

### i) Line-Specific Sub-Identities Within Shūeisha

**Jump Comics** (Weekly Shōnen Jump serializations):
- Most energetic, most colorful, highest saturation, most prominent badge
- Target: young male 12–18
- Badge: Red/gold prominent upper-left
- Examples: One Piece, Naruto, Dragon Ball, MHA, Demon Slayer, Jujutsu Kaisen

**Jump SQ** (Jump Square monthly serializations):
- Similar but slightly more mature visual tone
- Badge: "SQ" variant, same red color but with SQ designation
- Examples: Fullmetal Alchemist Brotherhood continuation, Blue Exorcist

**V-Jump** (video game–adjacent, monthly):
- "V" designation, gaming aesthetic more prominent
- Dragon Ball Super manga serialized here

**Young Jump** (Weekly Young Jump — older shōnen/young seinen):
- Dark/more mature badge treatment ("YOUNG JUMP COMICS")
- Examples: Tokyo Ghoul, Vinland Saga (early), Golden Kamuy

**Ultra Jump** (monthly seinen):
- Understated badge, sophisticated design language
- Examples: JoJo's Bizarre Adventure (Part 7+), Trigun Maximum

**Margaret Comics** (shōjo, biweekly):
- Pink badge, flower decorative elements
- Examples: Hana Yori Dango (Boys Over Flowers)

### j) Three Iconic Cover Examples

1. **One Piece v1** (Eiichiro Oda, 1997): Blue sky field with puffy clouds, Luffy in straw hat and red vest centered, Zoro and Nami visible smaller behind him, bright open energy. The Jump Comics badge in upper-left is gold/red. Title in bold white with black outline across top third. Establishes the entire aesthetic template for the series' 105-volume run.

2. **Demon Slayer: Kimetsu no Yaiba v1** (Koyoharu Gotouge, 2016): Tanjiro in three-quarter view, Nezuko visible in background, deep mountain/forest environment with wisteria color reference. More restrained palette than typical Jump — dark blue-green accents with warm character colors. Jump badge upper-left. Established a visual language different from the orange-dominant Jump tradition, signaling a slightly different aesthetic direction.

3. **Naruto v1** (Masashi Kishimoto, 1999): Naruto in orange jumpsuit, bright orange-red gradient field behind him, speed lines emanating from his direction. The cover is almost pure saturation — the orange field is extremely bold. Jump badge upper-left, title in large white-outlined letters. Volume 1 of one of the highest-selling manga series; this cover defined "shōnen orange" as a concept.

---

## 2. Kodansha

### a) Visual Identity Markers at Thumbnail Scale (50–100px)

Kodansha covers are slightly harder to identify at thumbnail scale than Jump Comics because Kodansha's imprint system is more fragmented — they operate at least 20 distinct imprints across different demographics. The common markers: Kodansha logo (K in a circle, or the wordmark) appears on the spine and back cover; imprint-specific badges tend to be less colorfully assertive than Shūeisha's Jump badge; Kodansha's shōnen imprint (Magazine Comics / Kodansha Comics) uses orange with a slightly different badge geometry than Jump. The KC (Kodansha Comics) shield-shape badge is recognizable at 100px.

### b) Logo / Imprint Badge Design

**KC (Kodansha Comics / Magazine Comics)**:
- Shield or rounded rectangle badge
- Color: Orange (`#FF6600`) with white "KC" or "Kodansha Comics" text
- Placement: Upper-left, similar position to Jump badge but slightly different shape
- Slightly softer orange than Jump's red-orange

**Afternoon Comics / Kodansha Manga Awards**:
- More understated badge, often dark colored with serif presentation
- Signals literary/seinen credibility

**Nakayoshi Comics** (shōjo):
- Pink badge (`#FF69B4`) with cursive/script "Nakayoshi"

### c) Title Typography Conventions

- Kodansha has slightly more variation in title typography than Shūeisha, allowing more experimental treatments
- KC Magazine Comics shōnen: Bold, similar weight to Jump but with slightly more spacing — titles feel slightly less aggressive
- Afternoon (seinen): Typography more likely to be experimental — condensed, reversed out, smaller scale with more breathing room
- Morning (seinen): Similar to Afternoon, sometimes more graphic-design-forward

### d) Spine Design

- **KC standard**: Orange spine top band with KC logo; title vertical; volume number at bottom
- **Afternoon/Morning**: More sophisticated spine design — color varies by title rather than being imprint-standardized; logo placement consistent but less aggressively branded than KC
- Full color spine on Kodansha titles is more common than some other publishers; they also produce more elaborate collector spine designs for long-running series

### e) Back Cover Layout Template

```
┌─────────────────────────┐
│  [SERIES TITLE small]   │
│  [VOLUME NUMBER]        │
│                         │
│  [CHARACTER ART]        │  ← Often a supporting character
│  (secondary)            │
│                         │
│  [VOLUME BLURB]         │  ← 80–100 word story summary
│                         │
│  [AUTHOR]               │
│  [KC SHIELD BADGE]      │
│                         │
│  ¥XXX+tax    [ISBN barcode + number]
└─────────────────────────┘
```

### f) Inner Jacket Convention

Kodansha tankōbon inner jacket: similar to Shūeisha — dust jacket over printed board.
- Inner board: often uses the same primary character illustration at reduced color range (often spot color or duotone)
- Jacket flaps: author bio and profile, volume contents description
- Author note: 4-koma or message, at book rear

### g) Paper and Production Signature

- Kodansha standard: glossy dust jacket, white to slightly cream interior paper
- Afternoon/Morning deluxe editions: higher quality matte jacket, better paper
- KC standard: similar to Jump quality — cream newsprint interior, gloss jacket

### h) Characteristic Color Palettes

- KC shōnen: Orange (`#FF6600`) as brand anchor, but less specifically committed to this than Jump to its orange-red
- Afternoon/Morning: More varied by title — earthy tones, muted palettes, professional
- Nakayoshi shōjo: Pinks, lavenders, shōjo-standard palette

### i) Line-Specific Sub-Identities

**Kodansha Comics (KC)**: Shōnen, action manga, most popular series
- Attack on Titan (Hajime Isayama): Dark, muted, military aesthetic — unusual for shōnen KC

**Afternoon**: Prestige seinen, literary manga
- Vinland Saga (Makoto Yukimura): Historical epic, Norwegian palette
- Mushishi (Yuki Urushibara): Supernatural naturalistic, very quiet palette

**Morning**: Workplace/adult manga, often literary
- Bartender, Drops of God (food/drink manga) — adult professional settings

**Nakayoshi**: Classic shōjo
- Cardcaptor Sakura (CLAMP): Magical girl, sparkle aesthetic

**Bessatsu Shōnen Magazine**: Dark/seinen-adjacent shōnen
- Attack on Titan serialized here: Dark military horror covers

### j) Three Iconic Cover Examples

1. **Attack on Titan v1** (Hajime Isayama, Kodansha, 2009): The Wall with Titans emerging over it, Eren in foreground in military survey corps uniform. Dark and muted unlike typical shōnen KC — olive drab military colors, ominous sky. This cover deliberately rejected the orange-bright shōnen convention and signaled a different kind of story. KC badge present but subdued.

2. **Vinland Saga v1** (Makoto Yukimura, Kodansha/Afternoon, 2005): Young Thorfinn in Norse fur-trimmed clothing, sword prominent, cold Nordic palette (steel blue, grey). Afternoon Comics badge. The cover uses the Afternoon color restraint language — more Scandinavian film poster than typical manga.

3. **Cardcaptor Sakura v1** (CLAMP, Kodansha/Nakayoshi, 1996): Sakura in her first magical costume, wand raised, Kero-chan flying nearby, stars and sparkles — full magical girl composition. Pink and star-gold palette. The Nakayoshi badge in pink upper corner. Classic shōjo composition establishing the magical girl cover template.

---

## 3. Shōgakukan

### a) Visual Identity Markers at Thumbnail Scale

Shōgakukan is distinguished by its Sunday Comics badge (yellow/orange for shōnen), Big Comics badge (mature seinen design), and Flower Comics badge (pink, shōjo). The Sunday Comics badge is one of the longest-running badges in manga — it uses a horizontal rectangle similar to Jump's badge but in a warmer yellow-orange (`#FFB300`) with "Sunday Comics" or "少年サンデーC" in red or dark text. At 50px, the yellow badge differentiates it from Jump's red badge.

### b) Logo / Imprint Badge Design

**Sunday Comics** (shōnen, Weekly Shōnen Sunday):
- Yellow-orange badge (`#FFB300`) with red "Sunday Comics" text
- Upper-left position, rectangular
- Slightly warmer/softer orange than KC, distinctly different from Jump red

**Big Comics** (seinen, Big Comic Spirits, Big Comic Original):
- Mature design — dark navy or charcoal badge with "BIG COMICS" white text
- Signals: adult content, serious subject matter

**Flower Comics** (shōjo):
- Pink badge (`#FF69B4` or `#FF1493`) with "Flower Comics" cursive/rounded text

### c) Title Typography Conventions

- Sunday Comics: Bold, high-energy similar to Jump — but often a fraction less extreme in weight
- Big Comics: More varied — literary titles use sophisticated typography, genre titles use bold standards
- Flower Comics: Script or rounded fonts, pastel colors

### d) Spine Design

- Sunday: Yellow-orange top strip with Sunday logo; rest of spine in title's color palette
- Big Comics: Dark sophisticated spine — often navy or charcoal background with white text
- Flower: Pink or floral-decorated spine

### e) Back Cover Layout

Similar template structure to Shūeisha and Kodansha. Notable: Shōgakukan back covers often feature more secondary character art than back covers from other publishers — a small secondary illustration alongside the text blurb is common across all their imprints.

### f) Inner Jacket Convention

Shōgakukan inner boards often feature monochrome or spot-color character art. For Big Comics prestige titles (Vagabond, Monster), inner boards may have higher-quality illustrations than standard imprints — recognizing that these titles attract collectors.

### g) Paper and Production

- Sunday Comics: Standard manga paper, cream tinted, gloss jacket
- Big Comics: Slightly better paper for prestigious runs; matte jacket options on special editions
- Monster/Vagabond kanzenban (Shōgakukan): Premium production — higher-grade paper, hardcover option

### h) Characteristic Color Palettes

- Sunday: Yellow-gold bias (`#FFB300`) as brand anchor
- Big Comics: Dark/sophisticated — no single dominant color, varies by title
- Flower: Pink/lavender/shōjo standard palette

### i) Line-Specific Sub-Identities

**Weekly Shōnen Sunday / Sunday Comics**: Inuyasha, Detective Conan, Magi, Zatch Bell
**Big Comic Original / Spirits**: Monster (Urasawa), Homunculus (Yamamoto), Golgo 13
**Big Comic Superior**: Vagabond (Inoue) — treated as flagship prestige title
**Flower Comics**: Historical shōjo series, contemporary romance

### j) Three Iconic Cover Examples

1. **Monster v1** (Naoki Urasawa, Shōgakukan/Big Comics, 1994): Johan Liebert in a corridor, clinical white environment, the composition is unsettling despite its cleanliness. Big Comics badge — dark, understated. Muted grey-blue palette. The cover is remarkable for what it doesn't do: no color, no energy, just a very wrong-feeling image of apparent normalcy.

2. **Detective Conan v1** (Gosho Aoyama, Shōgakukan/Sunday Comics, 1994): Young Conan in detective pose, magnifying glass prominent, red bow tie and large glasses against a blue mystery-toned background. Sunday Comics badge in yellow-orange. Long-running series identity established from volume one.

3. **Vagabond v1** (Takehiko Inoue, Shōgakukan/Big Comic Superior, 1998): Musashi rendered in watercolor brushwork, positioned against ink-wash sky/landscape. This cover is arguably the most artistically ambitious Vol.1 in major manga publishing — it looks like a gallery painting, not a comic cover. Big Comic Superior badge, subdued typography, horizontal brushstroke title treatment.

---

## 4. Kadokawa

### a) Visual Identity Markers at Thumbnail Scale

Kadokawa is Japan's largest multimedia company and its manga publishing spans an enormous range through multiple imprints. The key thumbnail identifiers: Dragon Comics Age badge (blue, associated with light novel adaptations), Media Factory / MF Comics badge (often blue-white, associated with isekai and LN manga), Comic Beam badge (square, understated — for avant-garde manga). Kadokawa covers tend to have the most visual diversity of any publisher because of the breadth of imprints and the influence of the light novel adaptation aesthetic on their isekai lines.

### b) Logo / Imprint Badge Design

**Dragon Comics Age** (fantasy/isekai adaptations):
- Blue badge (`#003399`) with "Dragon Comics AGE" in white
- Dragon graphic may be incorporated in badge

**MF Comics / Media Factory**:
- Clean modern badge, blue-white, "MF COMICS" or "メディアファクトリー"
- Square or rectangular, upper-left

**Comic Beam** (avant-garde/alternative manga):
- Small, understated logo — no loud badge
- Often positioned on spine rather than front cover
- Signals: artistic/literary credibility over commercial energy

**Young Ace / Ace Comics**:
- Orange-red badge for young male audience
- Isekai-adjacent, light novel adaptations

### c) Title Typography Conventions

- MF Comics / Dragon Comics Age: More likely to use display fonts with fantasy elements — gradient fills, decorative letterforms
- Long isekai titles rendered at smaller size to fit full LN-style title
- Comic Beam: Restrained, experimental — may use very thin or unusual typography choices

### d) Spine Design

- Kadokawa imprints are less spine-standardized than Shūeisha/Kodansha
- Dragon Comics Age: Often blue spine field with dragon logo
- MF Comics: Color varies by title; consistent logo placement
- Comic Beam: Black or dark spine, minimal text

### e) Back Cover Layout

Similar to other publishers, with more variation between imprints. Isekai titles from Dragon Comics Age/MF Comics often include:
- Full-color secondary character illustration
- Light novel series relationship note (e.g., "Original Light Novel published by Kadokawa Fantasia Bunko")
- QR code linking to publisher website in some modern editions

### f) Inner Jacket Convention

Kadokawa isekai manga adaptations frequently include:
- Inner jacket illustration featuring the artist's own take on the protagonist
- Artist's note (different from author's note — the manga artist comments on adapting the source material)
- LN original author's note on one flap, manga artist note on the other

### g) Paper and Production

- Standard manga production values similar to Shūeisha/Kodansha
- Some Kadokawa lines use slightly whiter paper than the cream-standard, giving the interior a brighter feel

### h) Characteristic Color Palettes

- MF Comics isekai: High saturation, fantasy blue-gold, magical effects
- Dragon Comics Age: Deep blue, gold, fantasy aesthetic
- Comic Beam: No characteristic palette — deliberately anti-commercial

### i) Line-Specific Sub-Identities

**MF Comics**: That Time I Got Reincarnated as a Slime, Konosuba, Re:Zero (manga adaptation)
**Dragon Comics Age**: Overlord, Is It Wrong to Try to Pick Up Girls in a Dungeon?
**Comic Beam**: Mushishi (original run), avant-garde/experimental work
**Young Ace**: SAO (Sword Art Online manga), Spice and Wolf

### j) Three Iconic Cover Examples

1. **Overlord v1** (art: Satoshi Oshio, Kadokawa/Dragon Comics Age, 2014): Ainz Ooal Gown on his throne in the Great Tomb of Nazarick, skull-face illuminated against dark purple-black background. Gold magic circle elements. Dragon Comics Age badge. Classic dark fantasy power aesthetic — intimidating but theatrical.

2. **That Time I Got Reincarnated as a Slime v1** (art: Taiki Kawakami, Kodansha → Kodansha Comics for manga, note: slime is Kodansha Comics not Kadokawa): Blue slime form of Rimuru, bright aqua palette. The contrast between the obviously cute slime form and the confident expression — this is the isekai cover genre defined.

3. **Mushishi v1** (Yuki Urushibara, Kodansha/Afternoon then Mel Tose → Comic Beam): Ginko the Mushishi against an organic atmospheric background, muted green-grey palette. Extraordinarily quiet cover for a manga — one figure, natural color tones, no urgency. Comic Beam's literary identity visible.

---

## 5. Square Enix

### a) Visual Identity Markers at Thumbnail Scale

Square Enix manga publishing is recognizable by its clean, game-adjacent aesthetic (Square Enix is primarily a game company — Final Fantasy, Dragon Quest — and this DNA infuses even its manga covers). The Gangan Comics badge is one of the most recognizable in seinen-adjacent shōnen: a circular or rounded-square logo in deep orange-red with "GANGAN COMICS" text. At 50px, the round badge geometry differentiates it from the rectangular badges of Shūeisha and Kodansha.

### b) Logo / Imprint Badge Design

**Gangan Comics** (shōnen, Monthly GFantasy):
- Circle or rounded-rectangle badge
- Color: Deep orange-red `#CC3300` with "GANGAN" in white
- Distinctive because of its circular/rounded geometry vs. competitors' rectangular badges

**Young Gangan** (young adult / older shōnen):
- Similar circular badge in a slightly different colorway
- "YOUNG GANGAN COMICS"

**Big Gangan** (seinen/adult):
- More sophisticated, lower-saturation badge
- Dark blue or charcoal presentation

### c) Title Typography Conventions

Square Enix titles often incorporate game-UI-influenced typography:
- Gradient-filled letterforms (gold gradient is very common)
- Decorative elements around title — stars, fantasy symbols
- Fullmetal Alchemist uses a distinctive alchemical-symbol-decorated title treatment recognizable across 27 volumes

### d) Spine Design

- Gangan Comics: Orange-red spine top, Gangan logo, title, volume number
- Some Square Enix titles have particularly notable spine art — the spines of a complete FMA collection show different character art on each volume, creating a "gallery wall" effect

### e) Back Cover Layout

Square Enix back covers sometimes include promotional material for related media (games, anime adaptations) — reflecting the company's multimedia orientation. Standard blurb + character art + badge + ISBN.

### f) Inner Jacket Convention

Square Enix tankōbon inner boards often feature:
- Sketch/rough art from the manga artist
- Bonus 4-koma (humorous four-panel strips) not in the serialized version
- Game collaboration bonus codes in special editions

### g) Paper and Production

- Standard quality for Gangan Comics line
- Some Square Enix special editions feature hardcover or premium paper — especially for Fullmetal Alchemist which received collector treatment

### h) Characteristic Color Palettes

- Gangan: Gold-orange bias (`#CC3300`, `#D4AF37`) reflecting game-aesthetic and alchemical/fantasy themes
- Big Gangan: Muted sophisticated, grey-blue for mature content

### i) Line-Specific Sub-Identities

**Monthly Gangan / Gangan Comics**: Fullmetal Alchemist, Soul Eater, Black Clover
**G Fantasy**: Dark/gothic themed manga, slightly more niche than core Gangan
**Young Gangan**: Black Butler (Yana Toboso) — Victorian gothic shōnen
**Big Gangan**: Dungeon Meshi (Ryoko Kui) — prestige seinen publication

### j) Three Iconic Cover Examples

1. **Fullmetal Alchemist v1** (Hiromu Arakawa, Square Enix/Gangan Comics, 2002): Edward Elric in red coat, automail arm raised, Alphonse's large armor suit behind him. Gold-alchemy aesthetic — the title treatment incorporates alchemical circle elements. Warm gold-rust palette. Gangan badge in circular form upper-left. Definitive Gangan Comics visual identity — warm, game-quality illustration, decorative title.

2. **Dungeon Meshi v1** (Ryoko Kui, Square Enix/Big Gangan, 2014): The party at a dungeon table eating a meal made from a monster — Laios, Marcille, Chilchuck around food that includes a Giant Frog and Scorpion dish. Warm illustration-book palette, yellow candlelight. Big Gangan badge subdued. The cover is anti-dramatic by genre convention — no battle, just a warm meal — but this subversion became the series' greatest asset.

3. **Black Butler v1** (Yana Toboso, Square Enix/G Fantasy, 2007): Ciel Phantomhive in Victorian mourning clothes, Sebastian in black butler uniform, roses — Gothic aesthetic. Deep rose and black palette. G Fantasy badge. The cover is one of the most successful Victorian Gothic manga cover designs — it reads clearly at thumbnail scale despite its elaborate detail.

---

## 6. Hakusensha

### a) Visual Identity Markers at Thumbnail Scale

Hakusensha is the publisher most associated with prestige shōjo and josei manga. Their flagship imprints — Hana to Yume (shōjo) and LaLa (shōjo) — have distinctive cover languages that differ from Shūeisha's Margaret and Kodansha's Nakayoshi. At 50px, Hakusensha covers often appear slightly more sophisticated/design-conscious than the shōjo mainstream: less maximally decorative, more white space, more editorial restraint. The Hana to Yume badge is white on green or white on deep teal, distinctly different from the pink badges of competitor shōjo lines.

### b) Logo / Imprint Badge Design

**Hana to Yume Comics** (flagship shōjo):
- White badge with green or teal accent: "Hana to Yume COMICS" — the name means "Flowers and Dreams"
- Distinctive: the green/teal badge is unique among shōjo publishers who use pink
- Size and placement: upper-left, rectangular, standard

**LaLa Comics**:
- Similar format, slight variation in color — often purple or lavender-rose accent
- LaLa is Hakusensha's second shōjo line, slightly younger audience than Hana to Yume

### c) Title Typography Conventions

- Hana to Yume: Elegant, often lighter weight than shōnen competitors. Script or semi-script with decorative elements.
- Fruits Basket: Uses a warm, handcrafted title treatment — the title letterforms feel drawn, not typeset
- Hakusensha shōjo typography in general: Never the heaviest option. Always at least one degree lighter and more refined than competing shōnen imprints.

### d) Spine Design

- Hana to Yume: Green or teal top band with HtY logo; rest varies by title
- Spine color often coordinates with the front cover's dominant palette — more holistic design thinking than some publishers
- Fruits Basket's spine design across its 23 volumes uses seasonal color progression — a deliberately designed collector experience

### e) Back Cover Layout

Hakusensha back covers tend to feature more elaborate illustration than competitors — the secondary character art is often as carefully composed as the front. Blurb text is set in softer, lighter typography. The overall back cover design reflects editorial sensibility rather than pure commercial urgency.

### f) Inner Jacket Convention

Hana to Yume inner boards are known for:
- High-quality second illustration — often in a different style or setting than the cover
- Author's handwritten notes reproduced in facsimile
- Bonus content pages — character profiles, artwork galleries

### g) Paper and Production

- Hakusensha: Generally slightly better quality than Jump/Sunday standard
- Berserk (Young Animal, Hakusensha's seinen imprint): Premium production — the pages are higher quality than average, reflecting the prestige/collector status of the title
- Young Animal is a separate editorial operation within Hakusensha, distinct from the shōjo lines

### h) Characteristic Color Palettes

- Hana to Yume: Green-teal accents as brand identity; cover palette varies by title
- Fruits Basket palette: Warm cream, soft rose, seasonal warmth
- Berserk (Young Animal/Hakusensha): Dark, painterly, rich — opposite of the Hana to Yume softness

### i) Line-Specific Sub-Identities

**Hana to Yume Comics**: Fruits Basket (Takaya), Ouran High School Host Club (Hatori Bisco)
**LaLa Comics**: The Earl and the Fairy, historical/fantasy shōjo
**Young Animal** (seinen, biweekly): Berserk (Miura) — the publisher's prestige flagship despite being in a totally different genre register than the shōjo lines

### j) Three Iconic Cover Examples

1. **Fruits Basket v1** (Natsuki Takaya, Hakusensha/Hana to Yume, 1998): Tohru Honda in school uniform, cherry blossom environment, three Sohma family members in animal forms visible. Warm peach-cream palette. Green Hana to Yume badge. Soft, botanical, emotionally warm — the definitive Hana to Yume aesthetic.

2. **Ouran High School Host Club v1** (Bisco Hatori, Hakusensha/Hana to Yume, 2002): Haruhi in male school uniform surrounded by the Host Club members in elaborate poses — high camp, bright gold and rose palette. The cover commits to the comedy-luxury aesthetic.

3. **Berserk v1** (Kentaro Miura, Hakusensha/Young Animal, 1989): Guts in his massive armor, against a dark field with Gothic compositional energy. Deep charcoal/crimson. Young Animal badge, understated. The visual language is completely unlike the shōjo lines on the same publisher's roster — Hakusensha's range as a publisher is extraordinary.

---

## 7. Akita Shoten

### a) Visual Identity Markers at Thumbnail Scale

Akita Shoten publishes through Champion Comics (shōnen, Weekly Shōnen Champion), Princess Comics (shōjo, Bessatsu Princess), and several adult manga lines. At thumbnail scale, Champion Comics has a distinctive badge: a royal/imperial visual language — the word "Champion" is often set in a way that evokes trophies and victory, in orange-gold. Princess Comics uses a tiara graphic element in its badge.

### b) Logo / Imprint Badge Design

**Champion Comics**:
- Orange-gold badge (`#CC7700`) with "少年チャンピオン" (Shōnen Champion) text
- Trophy or crown graphic element incorporated
- Upper-left placement, rectangular

**Princess Comics**:
- Pink badge with crown/tiara symbol
- "Princess Comics" text in decorative font

### c) Title Typography

- Champion Comics: Bold, energetic, similar to Sunday/Jump register but with gold-tinted palette influence
- Princess Comics: Elegant feminine typography

### d) Spine Design

- Champion: Gold-orange top band, champion logo, title vertical, volume at base
- Princess: Pink spine with princess tiara logo

### e) Characteristic Color Palettes

- Champion Comics: Gold-orange bias, warm, victory-coded
- Historical association: Osamu Tezuka's Black Jack was in Champion Comics — the line has deep historical roots

### f) Three Iconic Cover Examples

1. **Baki the Grappler v1** (Keisuke Itagaki, Akita Shoten/Champion Comics, 1991): Baki in fighting stance, muscular anatomy extreme, tournament arena bg. Champion Comics badge. Hyper-masculine sports/martial arts aesthetic.

2. **Black Jack v1** (Osamu Tezuka, Akita Shoten/Champion Comics, 1987 reprint): The master surgeon in his patchwork coat, cape in motion, patient implied behind him. Even decades after original serialization, this cover communicates Tezuka's unique graphic language. Champion badge.

3. **Shaman King v1** (Hiroyuki Takei, Shūeisha — note: actually Shūeisha not Akita — correction): *Corrected example:* **Majin Tantei Nougami Neuro v1** (Matsui Yusei, Shōgakukan/Sunday Comics Super) — this demonstrates the complexity of matching publishers to titles. For Akita Shoten's Princess Comics, a representative example: **Red River (Anatolia Story) v1** (Chie Shinohara) — historical fantasy shōjo, elaborate costume detail, warm earth tones.

---

## 8. Ichijinsha and Specialty Publishers

### a) Ichijinsha

Ichijinsha is a major publisher for dōjinshi-adjacent and otaku-focused manga, as well as BL and GL. Their imprints:
- **Comic Rex**: Moe/otaku-adjacent slice-of-life
- **Comic Yuri Hime**: GL flagship — the most prominent GL anthology in Japan
- **Dear+**: BL line

**Visual identity at thumbnail**: Ichijinsha covers often have a more illustrative/light-novel-adjacent quality than older publisher imprints — this reflects their audience's familiarity with game CG and LN covers. Colors tend toward softer moe palettes or specific BL aesthetic.

**Yuri Hime badge**: White on pink-purple, small, upper corner. GL content is signaled by the badge name recognition among fans rather than dramatic visual design.

### b) Mag Garden

Small publisher known for prestige seinen and josei:
- **Blade Comics**: Aria (Kozue Amano), Mushishi (original Blade run)
- Visual identity: clean, artistic, anti-commercial in feel
- At thumbnail: covers appear more like art books than commercial manga

### c) Futabasha

Action seinen publisher:
- **Weekly Manga Action**: Domestic crime, action, adult male
- Visual identity: darker, grittier, more realistic illustration style than mainstream shōnen

### d) Other Notable Specialty Publishers

- **Shinshokan**: BL publisher — Given (Rihito Takarai). Shinshokan BL covers use soft desaturated palettes and small imprint badges; recognition is through genre convention rather than visual brand assertiveness.
- **Libre / Bibury**: Major BL publishing house (Finder Series, etc.) — dramatic, often dark BL aesthetic
- **Enterbrain / Media Factory (Kadokawa)**: LN adaptations, isekai heavy
- **Akane Shinsha**: Seinen, mature adult — less visible internationally

---

## 9. The Jump Comics Cover Stamp System

### Historical Development

The Jump Comics red-and-gold badge is arguably the most valuable piece of manga publishing real estate in the world. Since Weekly Shōnen Jump's launch in 1968 and the establishment of the Jump Comics tankōbon line in 1972, the badge has functioned as a guarantee — a seal of mass-market quality and commercial success that readers associate with reliable entertainment.

### Anatomy of the Jump Badge

```
┌──────────────────────────────────┐
│  ██████████████████████████████  │ ← Gold/yellow upper section
│  ██  J U M P  ████████████████  │   "JUMP" in red or black
│  ██████████████████████████████  │ ← Red lower section
│  ██  C O M I C S  █████████████  │   "COMICS" in white
│  ██████████████████████████████  │
└──────────────────────────────────┘
```

**Dimensions**: approximately 22mm wide × 9mm tall (at standard B6 trim, 112×175mm)
**Position**: upper-left corner, touching both top edge and left edge — no margin
**Colors**: Upper: `#D4AF37` (gold) or `#FF0000` (red, variant by era). Lower: `#CC0000` (red) with `#FFFFFF` text. Some eras have used pure black on gold.
**Typography of badge**: Ultra-condensed bold sans, white or black text.

### Era Variations

- **1970s–1980s**: Simpler badge design, text-only, black outline
- **1990s**: Gold metallic effect introduced — the badge gets more premium visual treatment
- **2000s–present**: Current standardized form — red and gold, high contrast, recognizable worldwide

### The "Stamp" as Quality Signal

The Jump badge functions as a quality stamp in several ways:
1. **Sales guarantee**: Series that appear in Jump Comics have already survived Weekly Shōnen Jump's circulation test — only popular series continue long enough to become tankōbon volumes.
2. **Reader trust**: Readers who have been burned by niche publisher titles understand that Jump Comics = mass-market tested entertainment.
3. **Bookstore shelving**: Jump Comics volumes, even from many different series, are often shelved together as a publisher block — the consistent badge makes this block visually coherent and massive.
4. **Collectibility signal**: The gold-red badge on a long spine run (Naruto 72 volumes, One Piece 105+ volumes, Dragon Ball 42 volumes) creates a collector's pride visual — an entire shelf of identical red-badged spines.

### Sub-Badge Variants

Different Jump imprints modify the base badge:
- **JUMP SQ.**: "SQ" added to badge — same red/gold but with "SQ" designation
- **YOUNG JUMP**: "YOUNG JUMP COMICS" — typically larger badge with "Young" prefix
- **V JUMP**: "V JUMP COMICS" — game-market badge
- **ULTRA JUMP**: More sophisticated, darker treatment

### Practical Implementation Notes

For programmatic cover generation, the Jump badge must be:
1. Placed touching the top-left corner (0px margin)
2. At the correct scale relative to cover (approximately 19-22% of cover width)
3. Using the exact `#CC0000` red and `#D4AF37` gold (or `#FFFFFF` text on red, variant)
4. Added in the Pillow post-processing stage, NOT generated by FLUX
5. Font: a close approximation is **Bebas Neue** at full bold weight for the "COMICS" text; "JUMP" uses a slightly different treatment that may require custom path rendering

---

## 10. Tankōbon Book Production Specs

### Standard Format Dimensions

The Japanese tankōbon (単行本, "standalone book") is the primary collected edition format. Two predominant trim sizes:

**B6 Format (standard, most common)**:
- Trim: 112mm × 175mm
- Used by: Shūeisha (Jump Comics), Kodansha (KC/Afternoon/Morning), Shōgakukan (Sunday/Big), Square Enix (Gangan), Hakusensha (Hana to Yume)
- Safe area (text/design inset): 5mm bleed on all four edges for print; keep critical elements 8mm from any edge
- This is effectively the universal Japanese manga tankōbon format

**A5 Format (larger, used for deluxe/kanzenban editions)**:
- Trim: 148mm × 210mm
- Used for: Collector's editions, kanzenban (complete editions), premium reprints
- More breathing room for cover design — title and character can coexist without compression

**Wide-format / Aizōban variants**:
- Some publishers produce wide-format (B5 or A5-wide) editions of popular series with new covers
- Different design constraints — composition must adapt to wider canvas

### Spine Width Calculation

Spine width is a function of page count and paper thickness:
- Standard manga paper: approximately 0.06mm per page
- Average volume: 180–200 pages → spine approximately 10.8–12mm
- First volumes (often shorter): ~8mm spine
- Long volumes (250+ pages): ~15mm spine
- **Critical for programmatic generation**: spine width must be dynamically calculated from page count to generate accurate full-wrap templates

### Dust Jacket vs. Naked Cover

**Standard Japanese tankōbon = dust jacket + inner cover board**

The anatomy:
1. **Outer dust jacket (カバー, kabā)**: Full-color illustrated wrap. This is what readers see in stores. Wraps around the entire book including spine and extends to inner flaps.
2. **Inner cover board (表紙, hyōshi)**: The hardboard covers of the book itself, visible when jacket is removed. Usually a simplified or alternate design — often a single color field with author name and title.
3. **Obi/belly band** (帯, obi): A narrow paper band wrapped around the lower third of the jacket. Used for promotional messaging, awards notices, print-run milestones ("3 million copies sold!"), anime announcements. Changes frequently during the print run.

**Jacket flap design**:
- Front flap: Author bio + photo (or illustration of author's self-caricature) + short description of the volume's story arc
- Back flap: Brief author bibliography, previous volume summary, or additional bonus content listing

### Paper Specifications

| Paper Type | Color | Use | Notes |
|------------|-------|-----|-------|
| Manga newsprint | Cream/off-white (`#F5F0E0`) | Interior pages, standard volumes | Visible cream tint at edges |
| Matte text stock | White (`#F8F8F8`) | Deluxe/premium editions | Brighter, heavier than newsprint |
| Glossy art paper | White | Special inserts, color pages | Full-color pages at front of chapter |
| Jacket stock | White (glossy coated) | Dust jacket outer | Gloss or matte laminate options |
| Board | Cream-light grey | Inner cover board | Stiff, usually 2-color print |

**Detectability from cover photography**: The glossy jacket produces a visible reflection/sheen. Cream-tinted edge paper visible at spine. Premium matte editions have a soft-look jacket rather than reflective.

### Safe Area and Bleed Specifications

For programmatic full-cover generation (front + spine + back):

```
Total canvas width = front (112mm) + spine (variable) + back (112mm) = 224mm + spine
Total canvas height = 175mm (plus 5mm bleed each edge = 185mm actual canvas)

Bleed extension: 5mm on all edges beyond trim
Safe area: 8mm inset from trim edge (no critical text/logos within 8mm of trim edge)

Spine text (title, volume number): centered on spine width, min 3mm from spine edge
```

**For FLUX/ComfyUI + Pillow full-wrap generation**:
1. Generate front cover image: 832×1216px (representing 112×175mm at 188dpi)
2. Generate back cover image: 832×1216px (same scale)
3. Generate spine image: width proportional to page count, height 1216px
4. Composite in Pillow: [back][spine][front] horizontally
5. Add all text elements, badges, barcodes in Pillow layer
6. Add dust jacket flap extensions (fold-out panels) if generating full jacket

### ISBN and Barcode Placement

**Japanese ISBN system**:
- Japan uses the standard 978-prefix EAN-13 ISBN system
- ISBN block appears on the back cover, lower-right quadrant
- Standard block: white rectangle containing 13-digit barcode + ISBN number below + price code
- Dimensions: approximately 37mm × 26mm (the barcode block itself)
- Price code (Cコード / C-code): A Japanese classification code appearing alongside ISBN — e.g., "C9979" codes specify: 9=adult, 9=comics, 79=leisure. This code appears in small text adjacent to the barcode.

**ISBN placement template on back cover**:
```
┌──────────────────────────────┐
│  (illustration / blurb)      │
│                              │
│                              │
│  ¥550+tax                    │
│  978-4-XXXXXX-XXX-X  [BARCODE]│
│  C9979 ¥500E                 │
└──────────────────────────────┘
```

**Publisher prefix by major publishers**:
- Shūeisha: 978-4-08-XXXXXX
- Kodansha: 978-4-06-XXXXXX  
- Shōgakukan: 978-4-09-XXXXXX
- Kadokawa: 978-4-04-XXXXXX (Media Factory) or 978-4-04-XXXXXX
- Square Enix: 978-4-75-XXXXXX

**For programmatic generation**: Barcode can be generated using Python's `python-barcode` library. Place in Pillow composition at lower-right of back cover within defined safe area.

### Production Notes for Image Generation Engineers

**Full-cover Pillow composition workflow**:
```python
# Pseudocode for full wrap generation
front_cover = flux_generate(genre, publisher, prompt)  # 832×1216px
back_cover = generate_back_cover(series_info, genre)    # 832×1216px  
spine = generate_spine(title, author, vol_num, page_count)  # spine_width × 1216px

# Full wrap assembly
full_wrap_width = 832 + spine_width_px + 832 + (bleed × 2)
full_wrap = Image.new('RGB', (full_wrap_width, 1216 + bleed*2))
full_wrap.paste(back_cover, (bleed, bleed))
full_wrap.paste(spine, (bleed + 832, bleed))
full_wrap.paste(front_cover, (bleed + 832 + spine_width_px, bleed))

# Add publisher badge (front cover, upper-left)
badge = load_publisher_badge(publisher)
full_wrap.paste(badge, (bleed + 832 + spine_width_px, bleed), mask=badge)

# Add ISBN barcode (back cover, lower-right)
barcode = generate_isbn_barcode(isbn_number)
full_wrap.paste(barcode, (bleed + 790 - barcode.width, bleed + 1140))

# Add all text
add_title_text(full_wrap, title, genre_typography_spec, position='front_top')
add_spine_text(full_wrap, title, vol_num, position='spine_center')
add_back_blurb(full_wrap, blurb_text, position='back_mid')
```

**Critical dimension conversions**:
- 112mm at 350dpi = 1543px (print quality)
- 112mm at 188dpi = 832px (screen/generation quality, then upscale)
- 175mm at 350dpi = 2413px (print quality)
- 175mm at 188dpi = 1298px → standardize to 1216px for FLUX

**Typography size guidelines** (at 1216px canvas height = 175mm):
- Publisher badge: 180px wide × 78px tall
- Main title: 100–160px font size (varies by title length)
- Author byline: 22–28px font size
- Volume number: 40–60px font size
- Back cover blurb: 18–22px font size
- ISBN text: 14px font size

---

## Appendix: Publisher Quick-Reference Comparison Table

| Publisher | Key Imprint | Badge Color | Position | Target Demo | Signature Palette |
|-----------|-------------|-------------|----------|-------------|-------------------|
| Shūeisha | Jump Comics | Red/Gold | UL corner rect | M 12–18 | Orange/Red/Yellow |
| Shūeisha | Margaret | Pink/Magenta | UL corner rect | F 12–18 | Pink/Lavender |
| Shūeisha | Young Jump | Dark Red | UL corner rect | M 18–30 | Dark/Varied |
| Kodansha | KC | Orange | UL shield | M 12–18 | Orange/Varied |
| Kodansha | Afternoon | Dark Muted | UL small | M 18–35 | Varied/Muted |
| Kodansha | Nakayoshi | Pink | UL corner rect | F 10–16 | Pink/Star-Gold |
| Shōgakukan | Sunday Comics | Yellow-Orange | UL rect | M 12–18 | Yellow-Gold/Varied |
| Shōgakukan | Big Comics | Dark Navy | UL rect | M 25–40 | Dark/Sophisticated |
| Shōgakukan | Flower Comics | Pink | UL rect | F 12–20 | Pink/Lavender |
| Kadokawa | Dragon Comics Age | Blue | UL rect | M 18–30 | Blue/Gold/Fantasy |
| Kadokawa | MF Comics | Blue-White | UL rect | M 16–28 | Varied/Isekai |
| Kadokawa | Comic Beam | Small/Subtle | Varied | M 25–40 | Anti-commercial |
| Square Enix | Gangan Comics | Orange-Red round | UL circle | M 12–20 | Gold/Orange |
| Square Enix | Big Gangan | Dark rounded | UL | M 20–35 | Sophisticated |
| Hakusensha | Hana to Yume | White/Green | UL rect | F 13–20 | Green/Teal/Soft |
| Hakusensha | Young Animal | Mature dark | UL | M 20–35 | Dark/Varied |
| Akita Shoten | Champion Comics | Gold-Orange | UL rect | M 12–18 | Gold/Trophy |
| Ichijinsha | Comic Yuri Hime | Pink-Purple | UL small | F 16–30 | Soft/Moe |

UL = Upper-Left | F = Female target | M = Male target

---

*Document version 1.0 — Reference for programmatic manga cover generation system*
*All publisher logos, imprint names, and title citations are trademarks of their respective owners*
*Production specifications are approximate; verify with current publisher guidelines for commercial print use*
