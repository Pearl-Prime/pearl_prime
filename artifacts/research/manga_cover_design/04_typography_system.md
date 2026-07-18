# Typography System for Manga Covers
**Reference Document 04 — International Manga Publishing**
*Revised: 2026-04-18*

This document is the canonical typography reference for the programmatic manga cover generation system. It covers title font selection, script-specific conventions, volume number treatment, creator credits, furigana, typographic pairing recipes, and technical implementation notes for FLUX and Pillow/PIL-based rendering pipelines. It supersedes the previous shorter version of this document.

---

## Table of Contents

1. [Part 1: Japanese Typography for Manga Covers](#part-1-japanese-typography-for-manga-covers)
   - 1.1 Display and Title Font Categories
   - 1.2 Vertical vs Horizontal Title Stacking
   - 1.3 Furigana on Covers
   - 1.4 Volume Number Typography
   - 1.5 Creator Credits
   - 1.6 Open-Source Font Recommendations
2. [Part 2: English/Latin Script Typography](#part-2-englishlatin-script-typography)
   - 2.1 Manga-Style Fonts
   - 2.2 Dramatic Display Fonts
   - 2.3 Literary, Iyashikei, and Josei Fonts
   - 2.4 Volume Number Treatment
   - 2.5 Creator Credit in English Editions
3. [Part 3: CJK Beyond Japanese](#part-3-cjk-beyond-japanese)
   - 3.1 Traditional Chinese (Taiwan/HK)
   - 3.2 Simplified Chinese (Mainland)
   - 3.3 Korean (Hangul)
4. [Part 4: Other Scripts](#part-4-other-scripts)
   - 4.1 Arabic
   - 4.2 Thai
   - 4.3 French (Latin Extended)
5. [Part 5: Typographic Pairing Recipes](#part-5-typographic-pairing-recipes)
6. [Part 6: Cover Typography Implementation Notes](#part-6-cover-typography-implementation-notes)
7. [Appendix A: Genre-to-Font Quick Reference](#appendix-a-genre-to-font-quick-reference)
8. [Appendix B: OFL Font Summary Table](#appendix-b-ofl-font-summary-table)

---

## Part 1: Japanese Typography for Manga Covers

Japanese manga cover typography is one of the most sophisticated visual language systems in commercial publishing. It balances centuries of calligraphic tradition against modern display demands, and must accommodate the vertical-horizontal duality of Japanese writing, the complexity of kanji logographs, and the commercial pressures of shelf visibility at small sizes. Understanding this system deeply is essential for any AI-assisted manga cover generation pipeline.

### 1.1 Display and Title Font Categories

#### 1.1.1 Fude — Calligraphic Brush Fonts

Fude (筆) fonts simulate ink-brush calligraphy, the oldest and most prestigious typographic register in East Asian visual culture. On manga covers, fude fonts communicate specific genre signals with high precision.

**Genre associations:**

*Horror and supernatural thriller:* Fude strokes convey the brittleness and unpredictability of terror. Series such as *Uzumaki* (Junji Ito) use brush-influenced letterforms that feel hand-cut and psychologically unstable. The ink bleeds, strokes crack, and counters are asymmetric — all reinforcing dread.

*Martial arts and action:* Fude on martial arts covers (e.g., *Vagabond*, *Baki*) references the calligraphy tradition of warrior culture — brushwork that is simultaneously controlled and explosive. The best examples show "harai" (sweeping strokes) pulled at speed, with the trailing edge of the stroke visibly accelerating.

*Historical and period drama:* Covers set in the Edo period or earlier almost universally use fude to signal authenticity. The font reads "old Japan" in the same way that blackletter reads "medieval Europe."

*Literary seinen:* Fude appears in more refined, controlled form for literary-leaning seinen titles, where the calligraphic reference is to classical poetry manuscripts rather than warrior culture.

**Stroke anatomy relevant to cover design:**
- **Tome (止め):** The definitive stop at the end of a stroke. A clean, heavy tome signals precision and dignity.
- **Hane (はね):** The upward flick at the end of certain strokes. More dynamic; used in action-register fude.
- **Harai (払い):** The sweeping diagonal release. Most energetic; appears in action and horror.
- **Nyū (入り):** The entry of the stroke, where the brush first contacts the surface. Can be sharp (hard-set brush) or rounded (soft brush).

**Representative series with notable fude titling:**
- *Berserk* (Kentaro Miura): Heavy, almost woodblock-carved fude suggesting stone inscriptions and war memorials
- *Vagabond* (Takehiko Inoue): Fluid, masterful calligraphy by the author himself — one of the few cases where the mangaka provides actual calligraphic titling
- *Rurouni Kenshin* (Nobuhiro Watsuki): Bold, aggressive brush with strong ink variation
- *Blade of the Immortal* (Hiroaki Samura): Angular, staccato brush quality mirroring the manga's graphic fragmentation
- *Lone Wolf and Cub* (Koike/Kojima): Classic 1970s jidaigeki with monumental brushstroke lettering
- *GeGeGe no Kitaro*: Playful ghostly fude, slightly irregular, suggesting old supernatural manuscripts

**Technical considerations for AI pipelines:**
Fude fonts in OpenType form are approximations of brush behavior. The best OFL options (Kosugi, Klee One at calligraphic weights) feel mechanically regular compared to genuine calligraphy. For covers requiring authentic fude, the recommended pipeline is:
1. Set placeholder title text in a fude font for composition
2. Render actual title calligraphy via image overlay (commissioned or generative)
3. Composite at the cover assembly stage in Pillow

**Open-source brush-adjacent options:**
- **Zen Old Mincho** (Google Fonts, OFL): Captures some stroke variation of traditional calligraphy
- **Hina Mincho** (Google Fonts, OFL): Delicate brush-influenced mincho with genuine stroke character
- **Kosugi** (Google Fonts, OFL): Semi-calligraphic, bridges formal gothic and brush — strokes show slight weight variation

#### 1.1.2 Mincho — Serif Fonts

Mincho (明朝体) is the Japanese serif category, characterized by thin horizontal strokes, thick vertical strokes, triangular terminals (uroko/scales) at stroke endings, and high contrast between stroke weights. The name comes from the Mincho dynasty in China, where the style was developed for woodblock printing.

**Visual characteristics relevant to cover design:**
- High stroke contrast creates an elegant, refined texture
- Uroko terminals give each character a precise, considered appearance
- At display sizes, individual stroke details become visible and contribute to the typographic "hand"
- At small sizes, thin strokes can break down — relevant for spine text and thumbnail consideration

**Genre and tonal associations:**
- *Literary seinen:* Mincho signals literary seriousness. Covers for manga marketed as literary fiction (*Mushishi*, *The Flowers of Evil*) use mincho to signal that the work operates in a different register from action manga.
- *BL (Boys' Love) and josei:* The elegance and precision of mincho aligns with emotional interiority. Thin strokes suggest delicacy; high contrast suggests drama.
- *Historical drama:* Mincho has a pre-war aesthetic appropriate for Taisho-era or earlier settings.
- *Horror (psychological):* Unlike fude, which signals visceral horror, mincho signals quiet dread — the horror of beautiful things gone wrong.

**Emotional associations in Japanese visual culture:**
Mincho carries weight and authority that Gothic/sans cannot easily replicate. It reads "traditional," "serious," "literary," and "elegant." It does not read "fun," "fast," or "accessible."

**Publisher preferences:**
- Shogakukan uses mincho variants for its Big Comic series editorial text
- Kodansha's literary Morning Comics line uses mincho in promotional typography
- Square Enix's Monthly G Fantasy uses mincho for certain horror titles to distinguish from shōnen line

**Representative series:**
- *Mushishi* (Yuki Urushibara): Clean, slightly archaic mincho suggesting natural world + supernatural quiet
- *Monster* (Naoki Urasawa): Bold authoritative mincho reinforcing the manga's literary ambitions; looks like a hardcover novel
- *Vinland Saga* (Makoto Yukimura): Editorial mincho treatment combined with historically resonant design
- *March Comes in Like a Lion* (Chica Umino): Sophisticated literary treatment

**Open-source mincho options:**
- **Noto Serif JP** (Google Fonts, OFL): Excellent foundational mincho; seven weights including ExtraBold (900)
- **Shippori Mincho** (Google Fonts, OFL): Designed for display use; captures 1960s-70s Japanese book typography aesthetic
- **Source Han Serif JP** (Adobe, OFL): Most technically comprehensive open-source Japanese serif; seven weights
- **Kaisei Tokumin** (Google Fonts, OFL): Extra-bold display mincho with very strong presence
- **Kaisei Decol** (Google Fonts, OFL): Display-optimized mincho with romantic qualities; variable stroke contrast

#### 1.1.3 Gothic/Kaku-Gothic — Sans-Serif Fonts

Gothic (ゴシック体) in Japanese typographic tradition means sans-serif, not the Western blackletter meaning. Kaku-Gothic (角ゴシック) specifically denotes square gothic — uniform-weight strokes with squared terminals. This is the workhorse of contemporary manga cover typography.

**Visual characteristics:**
- Uniform stroke weight (mono-linear or near-mono-linear)
- Squared terminals (kaku = square/corner)
- High legibility at all sizes
- Strong shelf presence; punches through busy background illustration
- Modern, energetic, accessible

**Genre and tonal associations:**
- *Shōnen action:* Kaku-gothic is the de facto standard for shōnen. The energy is direct, forward, muscular. Weekly Shōnen Jump's proprietary lettering sensibility is built on heavy gothic variants.
- *Isekai:* The genre's emphasis on accessibility and forward momentum aligns with gothic's directness. Heavy condensed gothic says "this series moves fast."
- *Sports manga:* Action-register gothic variants signal athletic energy and competition.
- *Comedy:* Lighter-weight gothic with rounded corners (approaching maru-gothic) signals playfulness.

**Weight spectrum:**
Gothic fonts for manga covers typically operate in the heavy end of the weight spectrum. ExtraBold (800) and Black (900) weights are standard for titles; Regular and Medium for secondary text. Ultra-compressed variants (horizontal scale 70-80%) are common for titles needing shelf presence without excessive vertical space.

**Publisher-specific gothic conventions:**
- *Shueisha / Jump Comics:* Heavy kaku-gothic, often custom-modified, with aggressive letter-spacing tightened to near zero or slightly negative
- *Kodansha / KC Comics:* Slightly more varied — gothic for action, mincho for literary titles
- *Akita Shoten:* Heavy gothic with color treatment (outline, shadow, or gradient fill)

**Representative series:**
- *Dragon Ball* (Akira Toriyama): Iconic heavy gothic logotype, custom-modified, inseparable from brand identity
- *My Hero Academia*: Gothic with expressive tracking — letters feel pulled outward by explosive force
- *Demon Slayer (Kimetsu no Yaiba)*: Gothic with decorative breath-pattern elements integrated into letterforms
- *Fullmetal Alchemist*: Gothic with metallic treatment — font choice reinforces the series' industrial/alchemical world
- *Attack on Titan*: Bold gothic with slightly compressed feeling

**Open-source options:**
- **M PLUS 1p** (Google Fonts, OFL): Highly recommended; clean modern gothic with excellent CJK coverage; Black (900) ideal for cover titles
- **Noto Sans JP** (Google Fonts, OFL): Industry-standard CJK sans; nine weights; extremely reliable
- **Zen Kaku Gothic New** (Google Fonts, OFL): More geometric than M PLUS; rigorous contemporary feeling; Black (900) very strong for horror and seinen
- **BIZ UDGothic** (Google Fonts, OFL): Universal design principles; slightly wider proportions; good for mixed JP/Latin
- **Source Han Sans JP** (Adobe, OFL): Adobe's comprehensive Japanese sans; nine weights

#### 1.1.4 Modern Display Variants

**Maru-Gothic (丸ゴシック) — Rounded Sans-Serif:**
Maru-gothic is gothic with rounded terminals, producing a softer, warmer, more approachable appearance. The rounding is applied to the outer corners of strokes, not the strokes themselves.

Genre associations:
- *Kodomomuke (children's manga):* Maru-gothic is the default for manga aimed at young children.
- *Iyashikei (healing manga):* Covers that want to communicate comfort, warmth, and gentle reassurance use maru-gothic. *Yotsuba&!* and *Laid-Back Camp* employ rounded font strategies.
- *Slice-of-life and 4-koma:* Casual, everyday-feeling maru-gothic signals genre without aggression.

Open-source maru-gothic:
- **Kosugi Maru** (Google Fonts, OFL): Clean round gothic; reliable and well-hinted
- **Rounded M+** (OFL via GitHub): More character variation; excellent for retro-manga feeling
- **Zen Maru Gothic** (Google Fonts, OFL): Slightly more refined; full weight range (300-900)
- **Mochiy Pop One** (Google Fonts, OFL): Extreme roundness; very contemporary kawaii aesthetic

**Sharp Angular Display:**
Fonts with extreme angles, cut terminals, and aggressive geometry.

Genre associations:
- *Horror and psychological thriller:* Sharp angles suggest broken glass, surgical cuts, and danger.
- *Cyberpunk and sci-fi:* Geometric precision and sharp angles signal technological cold.
- *Dark fantasy:* Angular display integrates with bone and crystal visual motifs.

**DotGothic16 — Pixel/Retro:**
A pixel-art-derived font that simulates early computer/game display. Genre-specific for gaming manga, isekai with game mechanics, and nostalgic 1980s-90s aesthetic.

#### 1.1.5 Custom Logotypes

Major manga series frequently develop custom logotypes — letterforms designed specifically for the series, not drawn from any existing font. This is the highest tier of manga title typography.

**Creation methods:**
1. *Publisher in-house design:* Large publishers have dedicated typographic designers creating custom logotypes for flagship series
2. *Contracted type designers:* Freelance lettering artists hired for series-specific letterforms
3. *Author-created calligraphy:* In rare cases (most famously *Vagabond*), the author provides actual calligraphy
4. *Modified existing fonts:* An existing font is licensed and then modified — strokes cut, terminals redesigned, proportions adjusted

**Characteristics of successful manga logotypes:**
- **Legibility at all scales:** From full cover to 100px thumbnail to 5mm spine
- **Genre-genre resonance:** Letterforms feel like they emerged from the series' visual world
- **Temporal durability:** Logotypes from 2000 should still feel appropriate in 2026
- **International adaptation:** Must have a legible structural skeleton that can be reinterpreted in other scripts

**Examples of notable custom logotypes:**
- *One Piece*: Stretching, nautical letterforms suggesting rubber-band physics and ocean movement
- *Naruto*: Angular, aggressive strokes with scroll-like terminals referencing ninja scroll iconography
- *Attack on Titan*: Stone-carved, monumental letterforms suggesting giant architecture and doom
- *Bleach*: Fluid, organic forms that seem to drip or dissolve — referencing spiritual death themes

---

### 1.2 Vertical vs Horizontal Title Stacking

Japanese typography's bidirectionality is one of its most complex and distinctive features. Manga covers use this not just as a typographic convenience but as a deliberate expressive choice.

#### 1.2.1 Vertical Stack (縦組み / Tategumi)

Traditional Japanese writing runs top-to-bottom, right-to-left. Vertical title stacking on manga covers follows this tradition and carries specific associations.

**Compositional rules for vertical stacking:**
- *Reading direction:* Japanese vertical text reads from top to bottom within a column, and columns are ordered right-to-left. The "first" character appears at the top-right of the title block.
- *Column width:* Single-column vertical stacks are most common for manga titles. Multi-column stacks (two or three characters wide) are used for very long titles or decorative effect.
- *Character spacing:* Japanese vertical display typography typically uses tight spacing — characters nearly touching. Negative space is usually 0-5% of character size.
- *Mixed script handling:* Arabic numerals and Latin characters in vertical Japanese text are rotated 90 degrees clockwise (縦中横 / tate-chu-yoko for short inline sequences, or full rotation for display). Volume numbers expressed as "1" or "Vol.1" must be handled carefully.
- *Alignment:* Vertical title stacks typically align to the right edge of the cover (for right-to-left reading flow) or are centered.

**When vertical stacking is used:**
- Traditional and historical genres
- Literary seinen
- BL and josei (for elegance associations)
- Shueisha's Jump Comics: vertical for traditional titles, horizontal for modern action

**Spacing rules:**
- *Tsumegumi (詰め組み):* Tight setting, 0-5% tracking. Standard for display titles.
- *Akigumi (空き組み):* Loose setting, 10-20% tracking. Used in some literary or artistic covers.
- *Proportional adjustment:* Narrow characters (一, 十) benefit from manual kern adjustment to avoid large gaps.

**Pillow/PIL Technical Implementation for Tategumi:**

Pillow does not natively support vertical text rendering for CJK characters. Recommended approach:

```python
from PIL import Image, ImageDraw, ImageFont

def render_tategumi_title(text, font_path, font_size, fill_color, stroke_color=None, stroke_width=0):
    """
    Render Japanese text vertically (tategumi) by drawing each character
    individually, positioned top-to-bottom in a column.
    """
    font = ImageFont.truetype(font_path, font_size)
    char_height = font_size * 1.15  # 15% leading between characters
    column_height = len(text) * char_height

    strip = Image.new('RGBA', (font_size + 20, int(column_height)), (0, 0, 0, 0))
    draw = ImageDraw.Draw(strip)

    for i, char in enumerate(text):
        y_pos = i * char_height
        if stroke_width and stroke_color:
            draw.text((0, y_pos), char, font=font, fill=fill_color,
                      stroke_width=stroke_width, stroke_fill=stroke_color)
        else:
            draw.text((0, y_pos), char, font=font, fill=fill_color)

    return strip
```

For production-quality tategumi with proper punctuation rotation and kana rotation, the recommended approach is to pre-render titles as SVG using `fonttools` with vertical writing mode (`writing-mode: vertical-rl`), then rasterize with `cairosvg`. This handles the full complexity of vertical CJK typography automatically.

#### 1.2.2 Horizontal Single-Line (横組み / Yokogumi)

Modern horizontal title setting reads left-to-right. It is the dominant format for action manga and anything seeking a contemporary, global feeling.

**Rules for horizontal titles:**
- Heavy weight is standard — thin strokes look weak against busy cover illustrations
- Tracking: action titles use very tight tracking (negative letter-spacing of 2-5% of cap height); literary titles use standard or slightly open tracking
- Baseline: horizontal titles are almost always set on a single baseline, not arched or curved
- Alignment: centered alignment is most common; left-alignment signals modernity

**When horizontal stacking is used:**
- Shōnen action (the dominant modern format)
- Isekai and contemporary genres
- Series targeting international markets (horizontal reads more naturally across all scripts)
- Magazine covers (Weekly Shōnen Jump sets all current cover text horizontally)

**How title placement interacts with character composition:**
When generating cover illustrations via FLUX, the prompt must reserve space for title typography:

- Horizontal title at top → character faces and bodies in lower two-thirds; sky/background in upper third
- Vertical title at right → main character positioned left-center; the right 15% of canvas is text zone
- Double-title (both vertical JP and horizontal EN) → character positioned center-left; right strip for JP, top strip for EN
- Single-character close-up covers → face fills center; title overlaid with semi-transparent backing or drop shadow

#### 1.2.3 Mixed Orientation

Some covers use both vertical and horizontal text simultaneously, creating deliberate compositional tension.

**Common mixed patterns:**
- *Title horizontal, volume number vertical:* Title reads as horizontal brand identity; volume number "第N巻" stacks vertically to the side
- *Title vertical, subtitle horizontal:* Traditional main title with modern subtitle — "rooted in Japanese tradition but speaks to the contemporary moment"
- *Volume number horizontally, chapter identifier vertically:* Used in some omnibus formats

**Publisher-specific conventions:**
- *Shueisha:* Horizontal titles for current flagship titles; vertical reserved for legacy or literary titles
- *Kodansha:* Vertical for literary imprints (Afternoon, Morning); horizontal for action (KC Comics)
- *Square Enix:* Horizontal for Young Gangan and Monthly G Fantasy; mixed for older legacy series
- *Hakusensha:* Flower Comics uses vertical for BL and josei; horizontal for some shōnen

---

### 1.3 Furigana on Covers

Furigana (振り仮名) are small phonetic glosses printed alongside kanji to indicate pronunciation. On covers, furigana serve multiple functions: accessibility, disambiguation of unusual readings, and decorative layering.

#### 1.3.1 When Furigana Appears on Cover Titles

**Audience considerations:**
- *Kodomomuke and elementary-level manga:* Furigana on titles is almost mandatory for kanji that appear in the title.
- *Shōnen (junior high level):* Furigana appears selectively — for unusual kanji, non-standard name readings, or decorative layering
- *Seinen and josei:* Furigana on covers is rare. When it does appear, it is usually for an unusual or invented reading (gikun)
- *BL:* Variable; some titles use furigana as a design element even when not strictly necessary

**Title disambiguation:**
When a title uses kanji with multiple possible readings, furigana disambiguates. This matters for brand recognition — readers searching for a title need to know the correct reading.

**Gikun (義訓) — The Conceptual Reading:**
One of the most sophisticated uses of furigana in manga is the gikun — where kanji are chosen for their semantic meaning but given a non-standard phonetic reading. The reader sees both the literal kanji meaning and the overlaid phonetic meaning simultaneously.

Classic example: A character's name might be written with kanji meaning "fate" but given the furigana reading "desutinii" (destiny in katakana-ized English). The reader holds both meanings at once. This technique is extremely common in shōnen titles and creates a title that functions simultaneously in Japanese and Western conceptual space.

**Decorative furigana:**
Some covers use furigana that are actually the English translation of the title, creating a bilingual title block even for the Japanese domestic edition.

#### 1.3.2 Size Ratio

**Standard ratio:**
Furigana to main kanji ratio is conventionally 1:4 to 1:3. This means:
- If the main title is set at 120pt, furigana appears at 30pt (1:4) to 40pt (1:3)
- The 1:4 ratio is more traditional and formal; 1:3 is more generous and readable

**Display size adjustments:**
At large display sizes (covers), the standard ratio may be loosened slightly to improve furigana legibility. A ratio of 1:3.5 is common for cover titles where furigana must be visible at thumbnail scale.

**At production canvas size (1322×2067px at 300dpi equivalent):**
- Main title at 80–140px → furigana at 22–48px
- Furigana below 22px becomes unreliable at print; below 18px is invisible at thumbnail

#### 1.3.3 Style Variations

**Rounded vs sharp furigana:**
- *Rounded (maru):* Furigana in a rounded style (matching maru-gothic main text) appears warmer and more approachable. Common in children's manga and iyashikei.
- *Sharp (kaku):* Furigana matching the sharpness of kaku-gothic main text appears more precise and serious. Common in action manga and seinen.

**Weight:**
Furigana is almost always set lighter than the main text — Regular or Light weight against a Bold or ExtraBold main title.

**Decorative furigana fonts:**
Some covers use furigana in a different font family from the main title — for instance, gothic main title with handwritten-style furigana, creating a contrast that signals a specific genre register.

---

### 1.4 Volume Number Typography

Volume numbers on manga covers are a surprisingly complex typographic subsystem. They must be simultaneously legible and subordinate — visible enough to allow series tracking without competing with the cover art or title.

#### 1.4.1 Kanji Numerals (漢数字)

Japanese kanji numerals (一二三四五六七八九十百) appear on volume numbers in certain contexts.

**When kanji numerals are used:**
- *Traditional and historical series:* Period-appropriate and reinforces genre associations
- *Literary seinen:* 第一巻, 第二巻 etc. convey formality
- *BL and josei:* Kanji numerals appear where elegance reinforces the genre's aesthetic register
- *Publisher: Shogakukan's Big Comic series:* Historical preference for kanji numeral volume notation

**Format patterns:**
- *第N巻 (dai-N-kan):* "Volume N" in formal Japanese. Used when formality is desired.
- *第N集 (dai-N-shuu):* "Collection N." Less common; used for some anthology-format collections.
- *N巻 (N-kan):* Without the 第 (dai) prefix. More informal; common in casual or action-register manga.

**Rendering considerations:**
Kanji numerals above 10 require two-character combinations (十一 for 11, 二十 for 20). For series with many volumes, this creates increasing complexity. Publishers sometimes switch to Arabic at volume 11 or 20 for practical reasons.

#### 1.4.2 Arabic Numeral Conventions by Publisher

Arabic numerals are now the dominant volume number format across all Japanese manga publishers, particularly for action and contemporary genres.

**Format patterns:**
- *"N" (plain numeral):* Most common. Clean, unambiguous. Shueisha Jump Comics standard.
- *"Vol.N":* Used by publishers targeting international awareness.
- *"#N":* Rare; some magazine-format collections use this.
- *Roman numerals (I, II, III…):* Extremely rare; reserved for special edition or prestige format volumes.

**Publisher-specific practices:**
- *Shueisha/Jump Comics:* Plain Arabic numeral, usually in a box or circle design element on the upper spine area.
- *Kodansha/KC Comics:* Similar to Shueisha; occasionally uses "Vol." prefix for internationally-oriented titles
- *Akita Shoten:* Sometimes integrates the numeral into a design element — the number appears inside a star, diamond, or logo shape

**Numeral font choices:**
Volume numbers almost always use the same font family as the title at reduced weight, or a decorative numeric-specific font. Common approaches:
- Same font, smaller size, reduced weight: Creates family relationship with title
- Tabular lining numerals: Preferred for precise alignment in series contexts

**Volume number placement by publisher style:**

| Cover Layout | Typical Placement |
|---|---|
| Shōnen horizontal title (Shūeisha standard) | Upper right, inside colored badge/oval; or below title right-aligned |
| Seinen minimal (Kodansha Afternoon style) | Lower left corner, small, quiet |
| Historical tategumi | Right column below the title, same vertical axis |
| Publisher logo alongside volume | Volume number anchored to publisher logo block |

#### 1.4.3 Spine Number Conventions

The spine is a distinct typographic space from the cover front. Spine typography must work in a very narrow vertical band (typically 5-20mm wide, depending on page count and paper weight).

**Spine number placement:**
- *Upper spine:* Most common for Japanese manga. The series title occupies the middle-to-lower portion of the spine, and the volume number sits at the top, often inside a colored box or circle.
- *Lower spine:* Some publishers place the numeral at the bottom of the spine
- *Mid-spine box:* The numeral appears in a colored box in the middle of the spine

**Spine number typographic characteristics:**
- *Size:* Very small — typically 7-10pt equivalent at actual print size
- *Weight:* Medium to Bold — thin strokes disappear at this size
- *Color:* Usually white on color, or the series' accent color

**Shelf-scanning design principle:**
Japanese manga publishers understand that readers scan spines to find their place in a series. The volume number must be in a consistent position across all volumes of a series, and must be large enough to read while the book is shelved upright at a bookstore distance of approximately 50cm.

---

### 1.5 Creator Credits

**Author/artist name placement — Japanese conventions by publisher:**

- *Shūeisha (Jump Comics):* Author name appears at the bottom of the cover, typically right-aligned, in a font 25-35% the size of the title.
- *Kodansha (Morning/Afternoon):* Often bottom-left, or integrated into the lower band design. Literary titles may place the author name very discreetly.
- *Shogakukan:* Bottom right is common; Sunday Comics places it prominently in the lower zone.

**Typical font for creator credits:**
A lighter/smaller version of the title font, or a neutral clean sans-serif (Noto Sans JP Regular or M PLUS 1p Regular) at 20-30% of title size.

**Japanese convention for author line formatting:**
- `著：[name]` or simply the name alone is standard
- For split credits: `原作：[story author]` / `作画：[artist]` / `原案：[concept author]`

**Pen name handling:**
Most manga authors publish under a single pen name (筆名/ペンネーム). The pen name is used on all covers without qualification — Japanese publishing does not use the Western convention of "writing as [pen name]."

---

### 1.6 Open-Source Font Recommendations

All fonts listed below are available under OFL-1.1 (SIL Open Font License) or equivalent permissive open-source licensing, making them appropriate for commercial AI pipeline use without royalty concerns.

#### 1.6.1 Noto Sans JP

**Source:** Google Fonts / Adobe (as Source Han Sans JP)
**License:** OFL-1.1
**Weights:** 100, 200, 300, 400, 500, 600, 700, 800, 900
**Scripts:** Hiragana, Katakana, Kanji (6,000+ JLPT-relevant glyphs), Latin, Numeric

**Use cases:**
- *Title text (700-900):* Excellent kaku-gothic display at heavy weights. Clean, modern, highly legible.
- *Secondary text (400-600):* Body and caption text for cover secondary elements.
- *Volume numbers:* The numeric glyphs are well-designed; tabular lining figures available.

**Weight-specific use guidance:**
- 900 (Black): Shōnen title, action display, maximum shelf impact
- 800 (ExtraBold): Standard action-manga title weight
- 700 (Bold): Seinen cover text; secondary title elements
- 600 (SemiBold): Taglines, subtitles
- 400 (Regular): Creator credits, fine print
- 300 (Light): Decorative secondary text; atmospheric lettering at large sizes

**FLUX rendering notes:**
Noto Sans JP renders adequately in FLUX at large sizes (100pt+ equivalent) for simple kanji strings. However, FLUX regularly hallucinates strokes in complex kanji at smaller sizes. Recommended pipeline: use Noto Sans JP for typographic mockup, then render all final Japanese text as a Pillow overlay.

#### 1.6.2 M PLUS 1 / M PLUS 1p

**Source:** Google Fonts
**License:** OFL-1.1
**Weights:** 100, 200, 300, 400, 500, 600, 700, 800, 900
**Scripts:** Hiragana, Katakana, Kanji, Latin

**Use cases:**
- *Iyashikei and slice-of-life titles:* M PLUS 1's slightly softer gothic structure gives it warmth that Noto Sans JP lacks at heavier weights
- *Kodomomuke secondary text:* At lighter weights, appropriate for child-facing secondary cover text
- *Rounded-adjacent application:* M PLUS 1 occupies the space between kaku-gothic precision and maru-gothic softness

**Design character:**
M PLUS fonts were designed by Coji Morishita with a focus on readability and a slightly humanist touch in their gothic structure. The counters are slightly more open than Noto Sans JP, giving M PLUS 1 more "breathing room" at display sizes.

**Specific weights for cover applications:**
- 900 (Black): Title treatment for gentle-action or iyashikei titles
- 700 (Bold): Standard iyashikei title weight; approachable without being too soft
- 400 (Regular): Secondary text with character

#### 1.6.3 Kosugi / Kosugi Maru

**Source:** Google Fonts
**License:** OFL-1.1
**Weights:** 400 (Kosugi), 400 (Kosugi Maru)
**Scripts:** Hiragana, Katakana, basic Kanji set, Latin

**Use cases:**
- *Calligraphic-adjacent applications:* Kosugi has a slightly hand-drawn quality — not full fude, but not the mechanical precision of Noto Sans JP
- *Traditional atmosphere without full calligraphy:* When a cover needs to feel "traditional" without the full intensity of fude

**Design character:**
Kosugi was designed to bridge formal gothic and brush calligraphy. Its strokes show slight variation in weight absent from pure geometric gothic fonts. Kosugi Maru adds rounded terminals, creating a warm traditional feel.

**Limitations:**
- *Single weight only:* The lack of bold weights is a significant limitation for display applications.
- *Limited kanji coverage:* Covers fewer kanji than Noto; may require fallback for uncommon characters.

**Pipeline workaround for bold:**
For applications that need Kosugi's aesthetic at heavier weights, apply a stroke effect in Pillow (text with paint stroke fill) to artificially increase apparent weight.

#### 1.6.4 Klee One

**Source:** Google Fonts
**License:** OFL-1.1
**Weights:** 400, 600
**Scripts:** Hiragana, Katakana, Kanji, Latin

**Use cases:**
- *Educational manga and kodomomuke:* Klee One was designed for educational contexts — clear, unmistakable, and gentle
- *Gentle manga (iyashikei, slice-of-life):* The semi-calligraphic quality gives warmth and human presence
- *BL light romance:* At SemiBold, Klee One has a refined, slightly literary quality

**Design character:**
Klee One is a semi-cursive Japanese font referencing educational handwriting models. Its strokes are clean but show human hand qualities — stroke entry and exit are clearly defined, creating letterforms that feel both precise and warm.

**Emotional register:**
Klee One reads as "written with care" — the emotional association is of a person writing thoughtfully, not a machine outputting text.

#### 1.6.5 RocknRoll One

**Source:** Google Fonts
**License:** OFL-1.1
**Weights:** 400
**Scripts:** Hiragana, Katakana, Kanji, Latin

**Use cases:**
- *Energetic casual action:* RocknRoll One has the energy of kaku-gothic but with irregular stroke weights and slight playfulness
- *Youth-targeted action:* Strong shelf impact for shōnen that doesn't want to read as too serious
- *Music and performance manga:* The name reflects its design personality accurately

**Design character:**
RocknRoll One's strokes have deliberate irregularity — this is not a mechanical sans but a designed approximation of spontaneous marking. Characters appear slightly vibrant, as if they could be moving.

#### 1.6.6 Zen Kaku Gothic New

**Source:** Google Fonts
**License:** OFL-1.1
**Weights:** 100, 300, 400, 500, 700, 900
**Scripts:** Hiragana, Katakana, Kanji, Latin

**Use cases:**
- *Professional display:* Full weight range makes Zen Kaku Gothic New one of the most versatile options for manga cover typography
- *Seinen action and thriller:* At 900, the font has strong impact; at 400-500, it reads as professional and serious
- *Secondary text system:* The full weight range allows a complete typographic hierarchy within a single font family

**Design character:**
Zen Kaku Gothic New is more refined than Noto Sans JP while maintaining the kaku-gothic structure. Its proportions are slightly more square, which gives it a premium feel at display sizes.

#### 1.6.7 Dela Gothic One

**Source:** Google Fonts
**License:** OFL-1.1
**Weights:** 400 (display-optimized ultra-heavy)
**Scripts:** Hiragana, Katakana, Kanji, Latin, Korean (basic Hangul)

**Use cases:**
- *Maximum impact shōnen title:* Dela Gothic One is among the heaviest Japanese display fonts available in OFL
- *Action and impact headers:* Designed specifically for large-scale display
- *Cover title overlay on dark backgrounds:* The extreme stroke weight holds against complex illustration backgrounds

**Design character:**
Dela Gothic One pushes kaku-gothic to its extreme — strokes are so heavy that counters (enclosed spaces) become very small. This extreme weight creates a physical presence on the page.

**Use with caution:**
At small sizes (below about 48pt at final print resolution), Dela Gothic One's counters fill in and the font becomes a solid block. Only use for large-scale display applications.

#### 1.6.8 Rampart One

**Source:** Google Fonts
**License:** OFL-1.1
**Weights:** 400
**Scripts:** Hiragana, Katakana, Kanji, Latin

**Use cases:**
- *Energetic shōnen with fortress/defensive themes:* The font has a blocky, fortified quality
- *Fantasy and adventure:* Strong medieval-castle energy that works with fantasy genre covers
- *Special attack names and impact text:* Rampart One's blocky quality suits in-cover impact text

**Design character:**
Rampart One has a distinctive extruded/3D-adjacent quality — strokes have a layered appearance that gives the font depth.

#### 1.6.9 DotGothic16

**Source:** Google Fonts
**License:** OFL-1.1
**Weights:** 400
**Scripts:** Hiragana, Katakana, Kanji, Latin

**Use cases:**
- *Retro/pixel aesthetic:* DotGothic16 is a pixel-art-derived font that simulates early computer/game display
- *Gaming manga and isekai with game mechanics:* Perfect for manga set in game worlds
- *Nostalgic 1980s-90s aesthetic:* For covers evoking early Japanese gaming culture

**Design character:**
DotGothic16 is built on a pixel grid, with strokes that align to imaginary pixels. Its use is genre-specific and immediately communicates "game/retro/pixel."

---

## Part 2: English/Latin Script Typography

English and Latin-script typography for manga covers addresses two distinct market contexts: (1) English-language editions of Japanese manga, and (2) original English-language manga (OEL/OEM). Each has distinct typographic conventions, though they share many font resources.

### 2.1 Manga-Style Fonts

#### 2.1.1 Bangers (Google Fonts, OFL)

**Source:** Google Fonts
**License:** OFL-1.1
**Weights:** 400
**Designer:** Vernon Adams

**Technical characteristics:**
- Heavy condensed display typeface
- High x-height with moderate cap height
- Slight italic lean (roughly 3-5 degrees) suggesting forward movement
- Rounded terminals that prevent the font from reading as aggressive despite its weight
- Strong horizontal rhythm due to condensed proportions

**Genre associations:**
- *Shōnen action (primary use case):* Bangers is the go-to free OFL option for shōnen-register English manga covers.
- *Comedy manga:* The rounded terminals and forward lean give Bangers a playful quality
- *Youth-targeted titles:* Accessible energy without intimidating complexity

**Pillow usage:** `Bangers-Regular.ttf` (single weight only; achieve heavier appearance through stroke rendering rather than bold weight variant)

#### 2.1.2 Anton (Google Fonts, OFL)

**Source:** Google Fonts
**License:** OFL-1.1
**Weights:** 400 (display-optimized ultra-heavy)

**Technical characteristics:**
- Extremely heavy condensed sans-serif
- Near-vertical stress throughout
- Very tight default tracking
- Monumental proportions — letters feel carved from stone

**Genre associations:**
- *Heavy shōnen:* Anton has more gravitas than Bangers — it reads heavier, more serious. Where Bangers is "fun action," Anton is "serious action."
- *Sports manga:* The font's condensed monumentality suits covers about athletes at peak performance
- *Dark action/thriller hybrid:* At large display sizes, Anton can read as ominous rather than cheerful

**Comparison with Bangers:**
Both are condensed heavy display fonts, but Anton has less playfulness and more authority. Anton reads "champion" while Bangers reads "adventure."

#### 2.1.3 Bebas Neue (OFL via Google Fonts)

**Source:** Google Fonts
**License:** OFL-1.1
**Weights:** 400 (single heavy weight)
**Designer:** Ryoichi Tsunekawa

**Technical characteristics:**
- All-caps only (no lowercase glyphs)
- Extremely condensed proportions
- Flat-head letterforms with horizontal shearing
- Strong geometric skeleton with humanist curve relief
- Designed with maximum legibility in condensed headlines in mind

**Genre associations:**
- *Seinen action:* The font reads as sophisticated heavy — associated with prestige action content
- *Contemporary thriller:* The clinical precision of Bebas Neue works for psychological thriller and crime manga
- *Sports and competition:* The font's championship-trophy aesthetic suits competitive sports manga

**Important technical note:**
Bebas Neue is all-caps only. Lowercase letters will display as uppercase. All volume numbers, subtitles, and secondary text set in Bebas Neue will appear in all-caps regardless of input case.

#### 2.1.4 Big Shoulders Display (OFL)

**Source:** Google Fonts
**License:** OFL-1.1
**Weights:** 100, 200, 300, 400, 500, 600, 700, 800, 900
**Designer:** Patric King

**Technical characteristics:**
- Ultra-condensed display typeface — one of the narrowest available in OFL
- Strong angular geometry with flat-cut diagonals
- Industrial/architectural visual associations
- Full weight range makes it highly versatile

**Genre associations:**
- *Dark thriller and horror:* The industrial angularity and narrow proportions create a claustrophobic quality
- *Post-apocalyptic and dystopian:* The stripped, architectural character fits post-collapse world-building
- *Crime and noir:* Ultra-condensed letterforms reference early 20th-century crime fiction typography

**Weight-specific use:**
- 900 (Black): Maximum thriller impact
- 700 (Bold): Standard thriller display
- 400 (Regular): Secondary text in thriller-register covers; cold and spare
- 100-200 (Thin/ExtraLight): Atmospheric headline text where spareness = menace

### 2.2 Dramatic Display Fonts

#### 2.2.1 Oswald (Google Fonts, OFL)

**Source:** Google Fonts
**License:** OFL-1.1
**Weights:** 200, 300, 400, 500, 600, 700

**Technical characteristics:**
- Condensed sans-serif with strong vertical emphasis
- Redrawn from the traditional Gothic Alternate style
- Moderate x-height with strong cap height
- Clean geometric skeleton with humanist details
- Full weight range for complete typographic hierarchy

**Use cases for manga covers:**
- *Series numbering systems:* Oswald's condensed precision makes it excellent for volume number treatment
- *Subtitle and secondary headline:* DemiBold to Bold weights make effective subtitles
- *Publisher and imprint credits:* The medium weights read as professional without being corporate

**Pairing notes:**
Oswald pairs naturally with Bebas Neue (both have condensed, geometric structure) and creates effective contrast with the more expressive Bangers or Anton.

#### 2.2.2 Cinzel (Google Fonts, OFL)

**Source:** Google Fonts
**License:** OFL-1.1
**Weights:** 400, 500, 600, 700, 800, 900

**Technical characteristics:**
- Inspired by classical Roman inscriptions
- All-caps only
- High contrast between thick and thin strokes with pronounced serifs
- The grandeur of ancient stone carving

**Genre associations:**
- *Fantasy isekai:* Excellent for titles that benefit from a sense of classical weight and ceremony
- *Historical fantasy:* Works well for series with invented kingdoms, ancient prophecies, or legendary heroes
- *Mecha with epic scope:* Classical gravitas applied to science-fiction cover design

### 2.3 Literary, Iyashikei, and Josei Fonts

#### 2.3.1 Libre Baskerville (OFL)

**Source:** Google Fonts
**License:** OFL-1.1
**Weights:** 400, 400 Italic, 700
**Designer:** Pablo Impallari

**Technical characteristics:**
- Optimized Baskerville revival for screen and print at text sizes
- High stroke contrast (thick-thin)
- Generous x-height relative to classical Baskerville
- Strong vertical axis
- Elegant italic with calligraphic connections

**Use cases:**
- *Literary manga English covers:* For manga that crosses into literary fiction territory
- *Josei romance title treatment:* The elegant stroke contrast creates the romantic visual register typical of josei
- *BL (English editions):* Refined serif titling for BL titles signaling literary quality

#### 2.3.2 Nunito (Google Fonts, OFL)

**Source:** Google Fonts
**License:** OFL-1.1
**Weights:** 200, 300, 400, 500, 600, 700, 800, 900
**Designer:** Vernon Adams

**Technical characteristics:**
- Rounded terminal sans-serif
- Well-rounded, balanced letterforms
- High legibility through rounded apertures
- Warm, friendly personality

**Use cases:**
- *Iyashikei (healing manga) English covers:* Nunito is the Latin-script equivalent of Klee One or M PLUS 1 — warmth and gentleness built into its letterforms
- *Kodomomuke English titles:* Rounded terminals signal child-appropriate content
- *Slice-of-life covers:* The approachable character signals everyday warmth

**Weight guidance for covers:**
- 900 (Black): Iyashikei titles needing shelf impact while maintaining warmth
- 700 (Bold): Standard iyashikei English title weight
- 400 (Regular): Secondary text, taglines, creator credits in gentle-register covers

#### 2.3.3 DM Serif Display (Google Fonts, OFL)

**Source:** Google Fonts
**License:** OFL-1.1
**Weights:** 400, 400 Italic
**Designer:** Colophon Foundry

**Technical characteristics:**
- High-contrast serif designed specifically for display sizes (48pt+)
- Pronounced thick-thin contrast that reads elegantly at large scales
- Glyphic (wedge) serifs rather than bracketed
- Strong classical proportions

**Use cases:**
- *Literary manga display title (English):* Prestige-literary quality signals "this is serious fiction with excellent artwork"
- *Josei and BL prestige titles:* The font reads romantic and elevated simultaneously
- *Historical and period drama English editions:* Classical proportions align with historical setting

#### 2.3.4 Playfair Display (Google Fonts, OFL)

**Source:** Google Fonts
**License:** OFL-1.1
**Weights:** 400, 500, 600, 700, 800, 900

**Technical characteristics:**
- High-contrast display serif with elegant proportions
- Available in regular, italic, and multiple weights
- The italic is particularly excellent for romantic taglines

**Use cases:**
- *Shōjo and josei:* Bold weight recommended for title display
- *BL:* Italic variants add a romantic quality
- *Romance:* The elegant high-contrast design creates the romantic visual register

#### 2.3.5 Raleway (Google Fonts, OFL)

**Source:** Google Fonts
**License:** OFL-1.1
**Weights:** 100, 200, 300, 400, 500, 600, 700, 800, 900

**Technical characteristics:**
- Elegant geometric sans
- Thin and Light weights give a refined French editorial feeling

**Use cases:**
- *Shōjo/josei and romantic titles:* SemiBold recommended for title display
- *French market covers:* Strong French design associations
- *Iyashikei:* The lighter weights have excellent breathing room

### 2.4 Volume Number Treatment

#### 2.4.1 Placement Conventions

**US/English market:**
- *Upper right* is most common for English manga editions. This follows Western book design convention and aligns with the cover reading direction.
- *Lower right* is a secondary common position — consistent with where price stickers often appear in physical retail.
- *Cover band/strip:* Some English publishers use a horizontal strip at the bottom containing series name, volume number, and barcode information.

**Japanese market (domestic):**
- *Upper spine area:* Volume numbers appear on the spine, not the cover front, in many Japanese editions.
- *Within the title block:* Japanese covers often integrate the volume number typographically within the title block.

**"Vol.N" vs "Volume N" — Publisher conventions:**
- *Viz Media:* "Vol." abbreviation, Arabic numeral, small font. Positioned at upper right. Example: `Vol. 23`
- *Yen Press:* "Volume" spelled out in some series; "Vol." in others; depends on series page design template
- *Seven Seas Entertainment:* Varies by series; generally "Vol. N" format
- *Dark Horse Comics:* Often "Volume N" spelled out, positioned at lower-left
- *Kodansha Comics USA:* "Volume N" tendency; clean integration with cover design

#### 2.4.2 Font Size Relative to Cover

**General proportions at production canvas (1322×2067px):**

| Element | Typical px Range | Notes |
|---|---|---|
| Main title (JP) | 80–140px | Shorter titles can go larger; 5+ kanji titles should scale down |
| Main title (EN) | 70–120px | Condensed fonts (Bangers, Bebas) can run larger |
| Volume number | 40–70px | Badge size scales around this |
| Creator credit | 22–35px | Must be legible at print size |
| Tagline/subtitle | 30–50px | |
| Furigana | 22–48px | 35–45% of base character size |

#### 2.4.3 Color Contrast Rules

**Core principle:** The volume number must be legible against the cover background at thumbnail scale.

**Contrast strategies:**
- *White text on color:* White numerals on a colored background strip or box. Most reliable high-contrast approach.
- *Color on white:* A colored numeral on a white background strip.
- *Outlined numerals:* A colored or white numeral with a contrasting outline ensuring legibility against any background.
- *Drop shadow:* A numeral with a contrasting drop shadow — less reliable than outline at small sizes.

**Minimum contrast ratio:** 4.5:1 between numeral and background (WCAG AA standard — a practical minimum even for non-accessible commercial contexts).

### 2.5 Creator Credit in English Editions

**Standard formats:**
- *"Story & Art by [Name]"* — Viz Media formula; used when a single creator handles both
- *"Art by [Name] / Story by [Name]"* — split credits; Story typically listed first in North American editions
- *"Based on the novel by [Author]"* — when the manga is an adaptation

**Translator/letterer credit placement:**
Translator and letterer credits virtually never appear on the front cover. They appear on the copyright/credits page. Some publishers include translator credit on the back cover in very small type.

---

## Part 3: CJK Beyond Japanese

### 3.1 Traditional Chinese (Taiwan/HK)

Traditional Chinese (繁體中文) editions of manga are the primary market for Taiwan, Hong Kong, Macao, and some overseas Chinese communities. The publishing infrastructure in Taiwan is particularly robust — many major Japanese manga have simultaneous or near-simultaneous Traditional Chinese releases.

#### 3.1.1 Font Recommendations

**Noto Serif TC (Traditional Chinese):**
- Source: Google Fonts
- License: OFL-1.1
- Weights: 100, 200, 300, 400, 500, 600, 700, 800, 900
- Scripts: Traditional Chinese characters, compatible CJK, Latin
- Use cases: Literary manga, historical drama, josei, BL in Traditional Chinese editions. The serif variant carries the same literary/formal associations as Mincho in Japanese.
- Character coverage: Extensive Traditional Chinese character set including Taiwan-specific variants

**Noto Sans TC (Traditional Chinese):**
- Source: Google Fonts
- License: OFL-1.1
- Weights: 100, 200, 300, 400, 500, 600, 700, 900
- Use cases: Action and contemporary manga in Traditional Chinese. Heavy weights for title display; lighter for secondary cover text.

**Source Han Serif TC:**
- Source: Adobe (GitHub, open source)
- License: OFL-1.1
- Weights: ExtraLight, Light, Regular, Medium, SemiBold, Bold, Heavy
- Use cases: Premium literary and historical manga. Has slightly different design decisions from Google Fonts version; both are valid.

**Jf Open Huninn:**
- Source: GitHub (justfont/open-huninn-font)
- License: OFL-1.1
- Use cases: Community-created rounded display font (Traditional Chinese) specifically designed as a free alternative to DFPop. Excellent for casual, friendly covers. Rounded terminals give warmth without licensing issues. Version 2.0 includes expanded character set.

#### 3.1.2 Title Directionality Conventions in Taiwan

**Historical vertical tradition:**
Traditional Chinese books — including manga in Taiwan — have historically used vertical text (top-to-bottom, right-to-left columns), following the same directional tradition as Japanese.

**Contemporary horizontal shift:**
More recent Taiwan manga editions increasingly use horizontal title typography, following international (and specifically Japanese contemporary) conventions.

**Cover-specific conventions:**
- Vertical title stacking: Still common for historical, literary, and prestige titles
- Horizontal title stacking: Standard for contemporary action and isekai genres
- Mixed: The same mixed conventions seen in Japan appear in Taiwan editions

**Volume number typography:**
Taiwan editions typically mirror Japanese volume number conventions — 第N冊 (dai-N-ce) or 第N卷 (dai-N-juan) for formal usage; plain Arabic numerals for most contemporary titles.

#### 3.1.3 Typographic Localization of Japanese Covers

When Japanese manga covers are adapted for Traditional Chinese editions, the process involves more than translation:

**Character-level decisions:**
- Japanese-specific kanji variants must be evaluated for the TC audience
- Series title translations may require typographic redesign — a Japanese title that is short in kanji may translate to a longer Chinese phrase requiring different layout
- Custom Japanese logotypes cannot be directly reused; the TC edition may need a newly designed title treatment

**Layout preservation:**
The goal is typically to preserve the composition of the original Japanese cover while replacing Japanese text with Chinese text.

---

### 3.2 Simplified Chinese (Mainland)

Simplified Chinese (简体中文) editions serve mainland China, Singapore, and some overseas communities. The mainland China market has specific regulatory and typographic requirements.

#### 3.2.1 Font Recommendations

**Noto Sans SC (Simplified Chinese):**
- Source: Google Fonts
- License: OFL-1.1
- Weights: 100, 200, 300, 400, 500, 600, 700, 800, 900
- Use cases: All contemporary mainland manga covers. Heavy weights for title; regular for secondary text.

**Source Han Sans CN:**
- Source: Adobe (GitHub)
- License: OFL-1.1
- Use cases: Mainland China editions where Source Han Sans is preferred over Noto Sans SC. Slightly more refined in some areas.

**LXGW WenKai:**
- Source: GitHub (lxgw/LxgwWenKai)
- License: OFL-1.1
- Weights: 300, 400, 700
- Use cases: Beautiful hand-writing-influenced kaiti (regular script) font covering both Simplified and Traditional Chinese character sets. Excellent for slice-of-life, romance, and iyashikei covers needing warmth. NOT suitable for bold display use — use for subtitles, credits, and taglines.

#### 3.2.2 Regulatory Requirements

**Mandatory simplified forms:**
All text on covers published for the mainland China market must use the approved simplified character set. Traditional forms are not permitted on publications distributed in mainland China.

**Font standards:**
The GB/T 17978-1999 standard and subsequent updates specify requirements for Chinese character display in publication contexts.

**Publisher imprint requirements:**
All covers distributed in mainland China must include the publisher's officially registered Chinese name and ISBN. These must appear in a specific location.

**Content review:**
Cover typography including series titles must pass content review by the National Press and Publication Administration (国家新闻出版总署).

**Mandatory elements on mainland Chinese manga editions:**
- ISBN barcode and number (back cover, standard positioning)
- Publisher name and license number
- Price (RMB) in a specific area
- CIP data (if applicable)

These elements use standard body fonts at mandated minimum sizes (GB/T 17710).

---

### 3.3 Korean (Hangul)

Korean editions of Japanese manga constitute a significant market. Korea also produces its own original manhwa, which has distinct typographic conventions.

#### 3.3.1 Font Recommendations

**Noto Sans KR:**
- Source: Google Fonts
- License: OFL-1.1
- Weights: 100, 200, 300, 400, 500, 600, 700, 800, 900
- Use cases: Standard Korean-language manga covers across all genres

**Nanum Gothic:**
- Source: Google Fonts (designed by Sandoll for Naver)
- License: OFL-1.1
- Weights: 400, 700, 800
- Use cases: Contemporary action and shōnen covers in Korean. Slightly warmer than Noto Sans KR. ExtraBold (800) recommended for cover title display.

**Nanum Myeongjo:**
- Source: Google Fonts
- License: OFL-1.1
- Weights: 400, 700, 800
- Use cases: Literary, josei, and BL Korean covers. The Korean serif (myeongjo) carries the same formal/literary associations as Japanese mincho.

**Pretendard:**
- Source: GitHub (orioncactus/pretendard)
- License: OFL-1.1
- Weights: 100, 200, 300, 400, 500, 600, 700, 800, 900
- Notes: The most versatile and recommended modern Korean OFL font. Nine weights. Excellent Korean/Latin harmonization makes it ideal for bilingual covers. Widely adopted in Korean digital design. Recommended as the default Korean font for production cover generation.

**SUIT Variable:**
- Source: GitHub (sunn-us/SUIT)
- License: OFL-1.1
- Notes: Modern variable font optimized for contemporary UI/screen use. Nine weights. Excellent for covers targeting digital-first audiences (webtoon adaptations, digital manga platforms).

#### 3.3.2 Manhwa Cover Conventions

**Full-bleed illustration:** Manhwa covers — particularly webtoon-derived manhwa — tend to use full-bleed illustration with minimal typography. The title may appear as a small element at the top or bottom.

**Color-dominant design:** Manhwa covers frequently use bold, saturated color palette as a primary design element. Typography integrates with the color field rather than sitting above it.

**Minimal decorative typography:** Where Japanese manga covers may have complex typographic layering, manhwa covers tend toward minimalism — title + volume number, sometimes only the title.

#### 3.3.3 Title Stacking — Hangul is Horizontal

A critical difference from Japanese typography: **Korean/Hangul is inherently a horizontal script.** While Hangul can technically be set vertically, it is highly unusual and reads as archaic or decorative. Contemporary Korean publishing is entirely horizontal.

**Implications for cover design:**
- All Korean title text is set horizontally, left-to-right
- Vertical text on a Korean cover would read as a deliberate artistic choice, not standard convention
- Volume numbers appear horizontally
- The bidirectional duality of Japanese cover typography does not apply to Korean covers

**Title placement:**
Korean manga and manhwa covers typically place the title at the top of the cover, often centered or left-aligned, set horizontally.

---

## Part 4: Other Scripts

### 4.1 Arabic

Arabic-language manga is an emerging market, with Middle Eastern readership growing and some publishers beginning to produce Arabic editions. Arabic script presents unique challenges for manga typography.

#### 4.1.1 Right-to-Left Layout Implications

Arabic is a right-to-left script, which fundamentally affects cover design for manga:

**Manga's right-to-left advantage:**
Japanese manga reads right-to-left, like Arabic. When Arabic-language editions are produced, the book's reading direction is already correct — the book opens from what Western readers would call the "back." This means the cover's visual hierarchy doesn't need to be mirrored the way it would for an LTR language like English.

**Text placement adjustments:**
- Cover text that appears in the upper-right corner in Japanese (first-read position for RTL readers) remains in the upper-right for Arabic
- Publisher logos and series credits remain in the lower-right for Arabic
- Volume numbers in the upper-right corner work naturally for both Japanese and Arabic reading conventions

**Typographic complexity:**
Arabic script uses contextual forms — each letter has up to four different shapes depending on its position in a word (initial, medial, final, isolated). Type rendering must correctly handle Arabic ligatures and contextual substitutions.

#### 4.1.2 Font Families for Arabic Manga Covers

**Noto Sans Arabic:**
- Source: Google Fonts
- License: OFL-1.1
- Weights: 100, 200, 300, 400, 500, 600, 700, 800, 900
- Use cases: Standard Arabic manga cover typography. Heavy weights for display titles; lighter for secondary text. The full weight range makes Noto Sans Arabic the most versatile OFL option.

**Scheherazade New:**
- Source: Google Fonts
- License: OFL-1.1
- Weights: 400, 700
- Notes: Nastaliq-adjacent serif Arabic font with more traditional calligraphic associations. Appropriate for historical and literary manga covers. The name references the *One Thousand and One Nights* and carries appropriate cultural resonance for fantasy manga.

**Cairo:**
- Source: Google Fonts
- License: OFL-1.1
- Weights: 200, 300, 400, 500, 600, 700, 800, 900
- Notes: Genuinely excellent contemporary Arabic display font designed specifically for modern publishing. Includes harmonized Latin alongside Arabic. Recommended as primary choice for most manga cover contexts.

**Implementation considerations:**
Arabic text rendering in Pillow requires:
- `python-bidi` library for the bidi algorithm
- `arabic-reshaper` for shaping before passing text to Pillow

```python
from arabic_reshaper import reshape
from bidi.algorithm import get_display

def prepare_arabic_text(text):
    reshaped = reshape(text)
    return get_display(reshaped)
```

Both are pip-installable and should be included in any pipeline producing Arabic cover text.

---

### 4.2 Thai

Thailand is one of the strongest manga markets in Southeast Asia.

#### 4.2.1 Font Families for Thai Manga Covers

**Noto Sans Thai:**
- Source: Google Fonts
- License: OFL-1.1
- Weights: 100, 200, 300, 400, 500, 600, 700, 800, 900
- Use cases: Standard Thai manga cover typography across all genres

**Sarabun:**
- Source: Google Fonts
- License: OFL-1.1
- Weights: 100, 200, 300, 400, 500, 600, 700, 800
- Notes: Elegant proportioned Thai font designed for both display and body use. Preferred for shōjo, josei, and iyashikei covers.

**Kanit:**
- Source: Google Fonts
- License: OFL-1.1
- Weights: 100, 200, 300, 400, 500, 600, 700, 800, 900
- Notes: Geometric Thai sans with slightly condensed, contemporary feeling. Good for action/shōnen covers.

**Thai typographic notes:**
- Thai script uses a complex combining-character system for vowel marks and tone marks that appear above and below consonant clusters
- These marks require careful line-height management — Thai text needs more vertical space than Latin text at the same point size (set leading at ~1.6x for multi-line)
- Thai does not use word spacing in the same way as Latin script; word boundaries are contextual, affecting line-breaking logic

---

### 4.3 French (Latin Extended)

France is one of the largest non-Japanese markets for manga, with publishers including Glénat, Kana, Pika, Ki-oon, and Delcourt/Tonkawa.

#### 4.3.1 French Typographic Requirements

**Accent handling:**
Accented characters (é, è, ê, ë, à, â, î, ï, ô, ù, û, ü, ç, œ, æ) MUST be preserved in display text. Dropping accents for stylistic reasons is considered typographically illiterate in French design. All recommended OFL fonts include complete Latin Extended character sets including all French accents.

**Common display fonts used by French manga publishers:**
- Adapted DIN (condensed industrial sans) — particularly for action/seinen
- Futura (or open-source alternatives) — geometric modernism for titles with a clean, designed feeling

**License-clean French-suitable display fonts:**
- **Raleway** (Google Fonts, OFL): Elegant geometric sans; excellent for shōjo/josei and romantic titles; thin and regular weights give a refined French editorial feeling
- **Montserrat** (Google Fonts, OFL): Geometric sans with rounded stems; versatile across genres; strong French design associations
- **Barlow Condensed** (Google Fonts, OFL): Industrial/contemporary; the condensed variant for long French titles (French titles tend to be longer than their Japanese originals due to grammatical structure)
- **Work Sans** (Google Fonts, OFL): Optimized for screen but equally effective in print; clean and neutral

---

## Part 5: Typographic Pairing Recipes

The following ten recipes represent complete typographic systems for specific genre targets. Each recipe is designed to be implemented as a complete system — all type elements on the cover working together.

---

### Recipe 1: Classic Shōnen Action

**Genre target:** Weekly shōnen action manga (battle, adventure, power systems)
**Reference series:** Typical Jump-style shōnen

**Title font (primary):** Dela Gothic One (Japanese) / Anton (English)
**Subtitle font:** Zen Kaku Gothic New 700 (Japanese) / Oswald SemiBold (English)
**Volume number font:** Noto Sans JP 900 (Japanese) / Bebas Neue (English)
**Creator credit font:** Noto Sans JP 400 / Noto Sans 400
**Color treatment:** Title in white with 3pt black stroke; volume number in yellow with black stroke; creator credit in white
**Example cover description:** The title dominates the upper third of the cover. Dela Gothic characters set tightly with near-zero tracking, creating a dense wall of heavy strokes that reads as forceful and energetic. The volume number sits in a colored pill-shape in the upper corner, the numeral in Noto Sans Black for consistency with the gothic register. Creator credit is set small at the bottom, in regular weight — barely present, ensuring all attention stays on the art and title.

---

### Recipe 2: Iyashikei / Healing Manga

**Genre target:** Gentle slice-of-life, nature, food manga
**Reference series:** Laid-Back Camp, Yotsuba, flying witch-style titles

**Title font (primary):** Klee One SemiBold (Japanese) / Nunito Bold (English)
**Subtitle font:** M PLUS 1 400 (Japanese) / Nunito Regular (English)
**Volume number font:** M PLUS 1 400 (Japanese) / Nunito Regular (English)
**Creator credit font:** Klee One 400 / Nunito Light
**Color treatment:** Title in a warm earth tone (terracotta #C67B5C or forest green #5B7A52) with no stroke; subtle soft drop shadow (blur: 4px, opacity: 30%, offset: 2px/3px); everything else in the same tonal family, lighter
**Example cover description:** The title occupies the lower third of the cover rather than the top, leaving maximum space for the peaceful illustration above. Text floats rather than anchors — generous spacing between elements. The volume number is set in a small circle in a corner, using the same warm tone as the title, at minimal weight. The overall typographic impression should be "this text is resting."

---

### Recipe 3: Dark Psychological Horror

**Genre target:** Psychological thriller, body horror, existential dread manga
**Reference series:** Uzumaki-adjacent, Oyasumi Punpun-adjacent

**Title font (primary):** Kosugi (Japanese) / Big Shoulders Display 700 (English)
**Subtitle font:** Noto Sans JP 300 Light (Japanese) / Big Shoulders Display 300 (English)
**Volume number font:** Noto Sans JP 400 (Japanese) / Big Shoulders Display 400 (English)
**Creator credit font:** Noto Sans JP 300 / Big Shoulders Display 200
**Color treatment:** Title in blood red #8B0000 or bone white #F5F0E8 on near-black background; no stroke (the absence of stroke emphasizes isolation); very subtle inner glow if title is light on dark (2px, 10% opacity, white)
**Example cover description:** The title is set off-center — deliberate compositional asymmetry creates unease. Kosugi's slightly irregular strokes at large scale show texture that regular gothic would not, suggesting something handwritten under duress. The volume number is as small as legibility allows. Secondary text is ghostly light weight, barely there.

---

### Recipe 4: Seinen Literary Manga

**Genre target:** Literary-ambition seinen, auteur manga, literary adaptation
**Reference series:** Mushishi, The Flowers of Evil, I Am a Hero

**Title font (primary):** Zen Kaku Gothic New 500 (Japanese) / Libre Baskerville Regular (English)
**Subtitle font:** Noto Sans JP 300 (Japanese) / Libre Baskerville Italic (English)
**Volume number font:** Noto Sans JP 400 (Japanese) / Oswald Regular (English)
**Creator credit font:** Noto Sans JP 300 / Lato 300
**Color treatment:** Monochromatic — title in deep navy #1A2744 or black on off-white #FAF8F5 cover, or reversed; no stroke, no glow; letter-spacing on the title set slightly open (5-10% of cap height)
**Example cover description:** The title is set at a moderate size — it doesn't shout. Medium weight. Open tracking. The composition allows the title and illustration to coexist as equals rather than the title dominating. The volume number is set in a very small size in the corner. The overall typographic message: "this work is confident enough not to need to shout."

---

### Recipe 5: BL (Boys' Love) / Romance

**Genre target:** Boys' love, romantic drama, emotional character-study manga
**Reference series:** Given, Takane to Hana, Koi wa Ameagari no You ni

**Title font (primary):** Klee One SemiBold (Japanese) / DM Serif Display (English)
**Subtitle font:** Noto Sans JP 300 (Japanese) / Libre Baskerville Italic (English)
**Volume number font:** Noto Sans JP 400 (Japanese) / Lato Regular (English)
**Creator credit font:** Noto Sans JP 300 / Lato Light
**Color treatment:** Title in a rich jewel tone or blush — amethyst #7B5EA7, rose gold #B76E79, or deep teal #2D6A6B; title treatment has a subtle glow suggesting emotional warmth (outer glow: 6px, 20% opacity, same hue as text); all secondary text in softer versions of the same palette
**Example cover description:** The title is set large and centered, in the vertical center or upper-center of the cover. DM Serif Display's high-contrast strokes at display size create elegance. The italic subtitle adds movement and emotional flow. Volume number sits quietly in the lower corner. The typographic system should feel like the opening page of a well-designed literary novel.

---

### Recipe 6: Isekai Fantasy

**Genre target:** Isekai adventure (portal fantasy, reincarnation, game-world manga)
**Reference series:** Overlord, That Time I Got Reincarnated as a Slime, Shield Hero

**Title font (primary):** Dela Gothic One or Rampart One (Japanese) / Anton (English)
**Subtitle font:** Zen Kaku Gothic New 700 (Japanese) / Oswald Bold (English)
**Volume number font:** Noto Sans JP 900 (Japanese) / Bebas Neue (English)
**Creator credit font:** Noto Sans JP 400 / Oswald Regular
**Color treatment:** Title in electric blue #00BFFF or gold #FFD700 with white stroke 2pt; subtitle in white or complementary color; background glow on title in same hue (12px, 25% opacity)
**Example cover description:** The title is maximum impact, occupying the upper 25-35% of the cover. A magical glow or energy halo effect behind the title characters reinforces the fantasy setting. The condensed weight suggests the density of worldbuilding. Subtitle text identifies the arc or volume theme.

---

### Recipe 7: Sports Manga

**Genre target:** Competition sports, training-arc, athletic achievement manga
**Reference series:** Haikyuu!!, Kuroko's Basketball, Blue Lock

**Title font (primary):** Zen Kaku Gothic New 900 (Japanese) / Bebas Neue (English)
**Subtitle font:** Noto Sans JP 700 (Japanese) / Oswald SemiBold (English)
**Volume number font:** Noto Sans JP 900 (Japanese) / Anton (English)
**Creator credit font:** Noto Sans JP 400 / Oswald Regular
**Color treatment:** Title in the series' sport-specific primary color; white stroke on title; volume number in white on colored tab; motion-blur treatment on certain title characters (horizontal motion blur 2-3px on horizontal strokes only, suggesting speed)
**Example cover description:** The typography suggests athletic kinetics. Title characters may have subtle horizontal extension or slight italic lean (manually adjusted, not font-native) to suggest forward movement. The composition is typically portrait-format with the athlete figure taking the center and the title sweeping across the upper portion.

---

### Recipe 8: Historical Drama (Jidaigeki)

**Genre target:** Samurai, Edo period, feudal Japan historical manga
**Reference series:** Vagabond, Blade of the Immortal, Rurouni Kenshin

**Title font (primary):** Kosugi Maru (as base, with custom stroke treatment) (Japanese) / Libre Baskerville Bold (English)
**Subtitle font:** Noto Sans JP 300 (Japanese) / Libre Baskerville Regular (English)
**Volume number font:** Noto Sans JP 400 or kanji numerals in Klee One (Japanese) / Oswald Regular (English)
**Creator credit font:** Noto Sans JP 300 / Lato Light
**Color treatment:** Title in aged ink black with slight warm undertone (off-black #1A1209); on aged paper cream (#EDE8D5) or rich shadow background; volume number may use 第N巻 kanji notation for period-appropriate formality; no contemporary glow or stroke effects
**Example cover description:** The typography should feel like it was set in another era. The avoidance of contemporary typographic effects (glow, outline, gradient) is itself a design choice — these covers rely on the quality of the letterforms and the illustration to convey period authenticity. The title occupies a vertical position (if vertically stacked) on the right side of the cover, reading downward.

---

### Recipe 9: Horror and Supernatural

**Genre target:** Supernatural horror, ghost story, creature horror manga
**Reference series:** Junji Ito works, Kouishou Radio, Ghost Hunt

**Title font (primary):** Kosugi (Japanese) / Big Shoulders Display 900 (English)
**Subtitle font:** Noto Sans JP 200 ExtraLight (Japanese) / Big Shoulders Display 200 (English)
**Volume number font:** Noto Sans JP 300 (Japanese) / Big Shoulders Display 300 (English)
**Creator credit font:** Noto Sans JP 200 / Lato ExtraLight
**Color treatment:** Title in deep blood red #6B0000 or bone white on near-black; intentionally degraded or distressed treatment (slight texture overlay on title, not smooth clean font); volume number in dim grey; all secondary text barely visible — whisper weight
**Example cover description:** Contrast of weights — the title is present and heavy, while all other text is almost invisible. The cover feels like it has a single obsessive focus (the title, which is the series' world) and peripheral elements fade. Slight distress texture on title characters (applied as Pillow overlay) suggests age, decay, or psychological fracture.

---

### Recipe 10: Kodomomuke (Children's Manga)

**Genre target:** All-ages, early childhood, elementary school manga
**Reference series:** Doraemon, Chi's Sweet Home, Yotsuba&!

**Title font (primary):** M PLUS 1 900 (Japanese) / Nunito Black (English)
**Subtitle font:** M PLUS 1 700 (Japanese) / Nunito Bold (English)
**Volume number font:** M PLUS 1 700 (Japanese) / Nunito Bold (English)
**Creator credit font:** M PLUS 1 400 / Nunito Regular
**Color treatment:** Title in the series' primary color (bright primary red, blue, yellow, or green); white stroke 4pt (generous stroke for clear legibility); volume number in a bright complementary color inside a rounded rectangle shape; all text at generous sizes relative to page
**Example cover description:** Maximum contrast, maximum size, maximum friendliness. The rounded terminals of M PLUS 1 / Nunito prevent any aggressive visual energy. The title is set very large — children need larger text cues for title recognition. The volume number is clearly visible. Furigana appears on all title kanji, set in the same M PLUS 1 at approximately 1:3 ratio. Nothing is ambiguous.

---

## Part 6: Cover Typography Implementation Notes

### 6.1 Minimum Legible Sizes at 100px Thumbnail

When manga covers are displayed online — on Amazon, Bookwalker, Comixology, or publisher store pages — they are typically shown as 100-pixel-wide thumbnails. This is the most hostile reading environment for cover typography.

**Empirically determined minimum sizes at 100px thumbnail width:**

At 100px thumbnail width (assuming a 2:3 aspect ratio standard cover, approximately 100x150px):

| Text element | Minimum pixel height | Minimum font weight |
|---|---|---|
| Title (Japanese kanji) | 14px | Bold (700) |
| Title (Latin) | 12px | Bold (700) |
| Subtitle | 10px | SemiBold (600) |
| Volume number | 9px | Bold (700) |
| Creator credit | 7px | Medium (500) — may be illegible |

**Critical implication:** At 100px thumbnail, creator credits are often effectively invisible. This is accepted practice — credits exist for full-size cover display and spine; they are not expected to be legible at thumbnail.

**Testing methodology:**
For AI-generated cover pipelines, thumbnail legibility testing should be included as an automated quality step:
1. Generate cover at full resolution (e.g., 1400x2100px)
2. Downsample to 100x150px using high-quality Lanczos downsampling
3. Apply a sharpness detection threshold to the text regions
4. Flag covers where text energy drops below threshold

### 6.2 Stroke/Outline Technique for Title Legibility

When a title must appear over a busy illustration background, a stroke (outline) applied to the title text dramatically improves legibility.

**Stroke implementation in Pillow:**
```python
from PIL import Image, ImageDraw, ImageFont

def draw_text_with_stroke(draw, position, text, font, fill_color, stroke_color, stroke_width):
    """
    Draw text with a stroke/outline for legibility on busy backgrounds.
    stroke_width: pixels of stroke on each side
    """
    x, y = position
    # Draw stroke by rendering text multiple times offset in all directions
    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=font, fill=stroke_color)
    # Draw the fill text on top
    draw.text(position, text, font=font, fill=fill_color)
```

**Pillow 9.2+ native stroke support:**
```python
draw.text(
    position,
    text,
    font=font,
    fill=fill_color,
    stroke_width=3,
    stroke_fill=stroke_color
)
```

**Stroke width recommendations by cover element:**
- Large title (60pt+): 3-5px stroke
- Medium title (36-60pt): 2-3px stroke
- Volume number (24-36pt): 2px stroke
- Secondary text (18-24pt): 1-2px stroke
- Very small text (12-18pt): 1px stroke or none (stroke at this scale can fill letter counters)

**Stroke color selection:**
- Dark title on light/mixed background: Black or dark navy stroke (#000000 or #1A1A2E)
- Light title on dark/mixed background: White stroke
- Colored title: Use the complementary or analogous dark shadow of the title color, not pure black

**Anti-aliasing considerations:**
For production pipeline, render at 2x final resolution and downsample — this provides natural anti-aliasing through the downsampling process.

### 6.3 Shadow and Glow Treatment Conventions

Beyond stroke outlines, shadows and glows provide additional legibility tools with different visual registers.

#### 6.3.1 Drop Shadow

**Visual register:** Classic, grounded, authoritative
**Implementation:**

```python
from PIL import Image, ImageFilter

def apply_drop_shadow(text_layer, shadow_color, offset_x, offset_y, blur_radius, opacity=0.6):
    """
    Apply a drop shadow to a transparent text layer.
    text_layer: RGBA Image containing text on transparent background
    """
    shadow = Image.new('RGBA', text_layer.size, (0, 0, 0, 0))
    shadow_data = text_layer.split()[3]  # Alpha channel
    shadow.paste(shadow_color, mask=shadow_data)
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur_radius))
    # Apply opacity
    r, g, b, a = shadow.split()
    a = a.point(lambda p: int(p * opacity))
    shadow = Image.merge('RGBA', (r, g, b, a))
    # Offset the shadow
    shadow_offset = Image.new('RGBA', text_layer.size, (0, 0, 0, 0))
    shadow_offset.paste(shadow, (offset_x, offset_y))
    return shadow_offset
```

**Convention guidance:**
- Offset direction: Conventionally downward-right (positive x, positive y) — follows implied light source from upper-left
- Offset distance: 2-5px for tight, professional shadows; 8-15px for dramatic, pop-art shadows
- Blur radius: 2-4px for sharp, close shadows; 6-12px for soft atmospheric shadows
- Opacity: 40-60% for standard shadow; 80-100% for very dark/dramatic shadow

#### 6.3.2 Glow Treatment

**Visual register:** Magical, ethereal, emotional, energetic
**Implementation:**

```python
def apply_outer_glow(text_layer, glow_color, glow_radius, glow_opacity):
    """
    Apply an outer glow to a transparent text layer.
    """
    glow = Image.new('RGBA', text_layer.size, (0, 0, 0, 0))
    text_alpha = text_layer.split()[3]
    glow.paste(glow_color, mask=text_alpha)
    glow = glow.filter(ImageFilter.GaussianBlur(glow_radius))
    r, g, b, a = glow.split()
    a = a.point(lambda p: int(p * glow_opacity))
    glow = Image.merge('RGBA', (r, g, b, a))
    return glow
```

**Convention guidance by genre:**
- Fantasy/Isekai: Warm golden glow (radius 12-20px, opacity 30-50%)
- Romance/BL: Soft pastel glow matching the emotion palette (radius 8-15px, opacity 20-35%)
- Horror: Sickly pale glow or red inner glow (radius 4-8px, opacity 40-60%) — horror glows are tighter and more menacing
- Sci-fi/Cyberpunk: Electric blue or green glow (radius 15-25px, opacity 60-80%) — cyberpunk glows are intense and saturated

### 6.4 FLUX Text Rendering Limitations and Workarounds

FLUX (and diffusion model image generators generally) have fundamental limitations in rendering text, particularly CJK scripts.

#### 6.4.1 Known FLUX Text Rendering Limitations

**Hallucinated strokes in kanji:**
FLUX's text understanding is fundamentally probabilistic. Complex kanji (any character with more than 8-10 strokes) will frequently have:
- Missing strokes
- Extra strokes
- Incorrectly placed strokes
- Strokes that do not close (open counters where they should be closed)
- Merged strokes from adjacent characters

**Latin text limitations:**
Even for Latin characters, FLUX text rendering is unreliable for:
- Strings longer than 4-5 characters
- Specific fonts or weights (FLUX cannot replicate specific typefaces)
- Precise positioning or alignment

**Consistency across variations:**
FLUX cannot guarantee that a title appearing across multiple generated cover variants will appear consistently — making it impossible to use FLUX-generated text as a series-consistent brand element.

#### 6.4.2 Recommended Workaround: Overlay Pipeline

The established workaround is to use FLUX for illustration generation only, and handle all typography as a post-processing overlay step in Pillow/PIL.

**Pipeline architecture:**

```
1. FLUX GENERATION STAGE
   Input: cover art prompt (description of characters, setting, atmosphere)
   Input: text_exclude_instruction = "no text, no lettering, no logos"
   Output: cover_art_base.png (illustration only, no text)

2. TYPOGRAPHY LAYER GENERATION
   Input: title_string, font_path, size, color, position
   Input: subtitle_string, ...
   Input: volume_number, ...
   Input: creator_credit, ...
   Output: typography_layer.png (RGBA, transparent background)

3. COMPOSITING STAGE
   Input: cover_art_base.png
   Input: typography_layer.png
   Process: alpha-composite typography over illustration
   Apply: stroke, shadow, glow treatments as appropriate
   Output: final_cover.png
```

**Prompting FLUX to avoid text:**
Including explicit text-exclusion instructions in the FLUX prompt significantly reduces hallucinated text. Recommended prompt suffix:
`"no text, no captions, no labels, no letters, no writing, no typography, clean illustration"`

**Background preparation for text areas:**
Consider prompting FLUX to include a specific area of solid or simple-gradient color where the title will appear:
`"darker upper area for title text placement, simplified upper-third composition"`

**Title reservation in FLUX prompts:**

Every FLUX prompt for manga cover generation MUST include explicit text reservation. Recommended formulations:

*Top-title horizontal reservation (shōnen/contemporary):*
`"text-free zone at top 350 pixels, clean background gradient or open sky, no text or lettering in top area"`

*Right-column vertical reservation (historical/seinen):*
`"clear vertical band on right side of image approximately 120 pixels wide, simple background in that zone, text-free"`

*Dual reservation (bilingual covers):*
`"text-free zone at top 300 pixels AND clean right strip 100 pixels wide, no decorative elements in these margins"`

*Full creative freedom with character bleed (variant approach):*
`"character fills entire frame, face and upper body, extreme close-up. typography overlay will be handled in post-processing. no text in image."`

#### 6.4.3 FLUX for Text Mockups Only

One legitimate use of FLUX-generated text: rapid visual mockups where typographic accuracy is not needed — only the overall composition and color relationship. For client approval or layout iteration, a FLUX cover mockup with rough-but-positioned text elements can communicate the design direction before final Pillow compositing is done.

### 6.5 Pillow (PIL) Text Rendering for Cover Assembly

Pillow (Python Imaging Library, maintained fork) is the recommended toolkit for production cover typography in automated pipelines.

#### 6.5.1 Font Loading

```python
from PIL import ImageFont

# Load OTF/TTF font file
font = ImageFont.truetype(
    font="/path/to/fonts/NotoSansJP-Bold.otf",
    size=96,  # points at intended render resolution
    encoding="unic"
)
```

**Font file management — recommended project structure:**
```
fonts/
  manga_covers/
    FONT_REGISTRY.yaml
    jp/
      MPLUS1p-Black.ttf
      NotoSansJP-Black.ttf
      ShipporiMincho-ExtraBold.ttf
      KleeOne-SemiBold.ttf
      ZenMaruGothic-Bold.ttf
      DelaGothicOne-Regular.ttf
      KosugiMaru-Regular.ttf
      ZenKakuGothicNew-Black.ttf
    latin/
      Bangers-Regular.ttf
      Anton-Regular.ttf
      Oswald-SemiBold.ttf
      BebasNeue-Regular.ttf
      Cinzel-Regular.ttf
      Nunito-Bold.ttf
      DMSerifDisplay-Regular.ttf
      LibreBaskerville-Bold.ttf
    korean/
      Pretendard-Bold.ttf
      NotoSansKR-Bold.ttf
    chinese_tc/
      NotoSerifTC-Bold.ttf
      jf-openhuninn-2.0.ttf
      NotoSansTC-Black.ttf
    chinese_sc/
      NotoSansSC-Black.ttf
      LXGWWenKai-Regular.ttf
    arabic/
      Cairo-Bold.ttf
      NotoSansArabic-Bold.ttf
    thai/
      Sarabun-Bold.ttf
      Kanit-Bold.ttf
      NotoSansThai-Bold.ttf
```

#### 6.5.2 Text Sizing and Positioning

```python
from PIL import Image, ImageDraw, ImageFont

def get_text_dimensions(text, font):
    """Get accurate text bounding box dimensions."""
    bbox = font.getbbox(text)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    return width, height

def center_text_horizontal(cover_width, text, font):
    """Calculate x position for horizontally centered text."""
    text_width, _ = get_text_dimensions(text, font)
    return (cover_width - text_width) // 2

def build_cover_typography_layer(cover_size, text_config):
    """
    Build a full typography overlay layer for a cover.

    text_config: list of text element dicts:
    {
        'text': str,
        'font_path': str,
        'size': int,
        'position': (x, y),
        'fill': (R, G, B),
        'stroke_color': (R, G, B) or None,
        'stroke_width': int,
        'anchor': 'la' | 'ma' | 'ra' | etc (Pillow anchor)
    }
    """
    layer = Image.new('RGBA', cover_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    for element in text_config:
        font = ImageFont.truetype(element['font_path'], element['size'])
        stroke_width = element.get('stroke_width', 0)
        stroke_color = element.get('stroke_color')

        if stroke_width and stroke_color:
            draw.text(
                element['position'],
                element['text'],
                font=font,
                fill=element['fill'],
                stroke_width=stroke_width,
                stroke_fill=stroke_color,
                anchor=element.get('anchor', 'la')
            )
        else:
            draw.text(
                element['position'],
                element['text'],
                font=font,
                fill=element['fill'],
                anchor=element.get('anchor', 'la')
            )

    return layer
```

#### 6.5.3 Vertical Japanese Text in Pillow

Pillow does not natively support vertical text layout. For covers requiring vertical Japanese title text:

**Option 1: Character-by-character stacking (recommended for simple cases)**
```python
def render_vertical_japanese(draw, start_position, text, font, fill,
                              stroke_color=None, stroke_width=0, char_spacing=0):
    """
    Render Japanese text vertically by stacking characters top-to-bottom.
    start_position: (x, y) of the top character's top-left corner
    char_spacing: additional pixels between characters
    """
    x, y = start_position
    for char in text:
        bbox = font.getbbox(char)
        char_width = bbox[2] - bbox[0]
        char_height = bbox[3] - bbox[1]
        if stroke_width and stroke_color:
            draw.text((x, y), char, font=font, fill=fill,
                      stroke_width=stroke_width, stroke_fill=stroke_color)
        else:
            draw.text((x, y), char, font=font, fill=fill)
        y += char_height + char_spacing
```

**Option 2: External library (for full vertical text support)**
The `pycairo` + `pangocairo` stack supports full OpenType vertical text features including width-variant forms (縦専用字形 — vertical-specific glyph variants). This is the production-quality solution for vertical Japanese text.

#### 6.5.4 Recommended Full Rendering Pipeline

```
Step 1: FLUX generates the base illustration
        - Prompt includes explicit text-free zone specification
        - Output: base_illustration.png (1322×2067px at 300dpi equivalent)

Step 2: Text elements pre-rendered as SVG (optional, for maximum quality)
        - Use fonttools (Python) + svgwrite for SVG text generation
        - Handles: vertical text, ruby, proper OpenType features
        - Output: title.svg, subtitle.svg, volume_badge.svg, credits.svg

Step 3: SVG rasterization with cairosvg (optional step)
        - cairosvg.svg2png(url='title.svg', output_width=1322, output_height=400)
        - Each text element becomes a PNG with transparency

Step 4: Pillow compositing
        - Load base_illustration.png
        - Paste each text PNG element at calculated position
        - Apply drop shadows or color treatments using Pillow ImageFilter
        - Final output: cover_final.png

Step 5: Color profile and format conversion
        - Convert to CMYK for print (using Pillow + littlecms or ImageMagick subprocess)
        - RGB sRGB for digital/ebook output
```

#### 6.5.5 Image Resolution and DPI Settings

**Print resolution:** Japanese manga are typically printed at 600 DPI for black-and-white art and 300 DPI for covers. Cover art generation should target:
- *Print quality:* 1800px wide × 2700px tall at 300 DPI (6" × 9" cover)
- *Standard production canvas:* 1322px wide × 2067px tall (112×175mm at 300 DPI)

**Screen quality:** For digital distribution:
- 1400px wide × 2100px tall is a common standard for digital manga cover art

**Pipeline recommendation:** Generate at 1400×2100 for speed; upscale to 1800×2700 using a superresolution step (Real-ESRGAN or similar) if print quality is needed.

### 6.6 Handling the Genre Typography Signal System

Typography on manga covers functions as a rapid genre signal system. Readers at a bookstore scanning shelf spines and cover fronts decode genre from typography in milliseconds — before they read the actual title. This is why font choice is not merely aesthetic; it is functional communication.

**The decoding hierarchy:**
1. **Weight:** Heavy = action or children; Light = literary or romantic; Medium = general or seinen
2. **Terminals:** Rounded = gentle, approachable; Sharp/squared = serious or aggressive; Irregular = horror or handmade
3. **Script style:** Brush/calligraphic = historical, emotional, or horror; Geometric sans = contemporary, energetic; Serif = literary or prestigious
4. **Tracking:** Tight = energy, youth; Open = literary confidence, space
5. **Color treatment:** Outline/stroke = action; No stroke = literary; Glow = fantasy/romance

A reader who has been reading manga for several years has internalized this grammar so thoroughly that they can identify the genre of a manga they have never seen before from typography alone — even before decoding the title text. AI pipelines must respect this grammar to generate covers that read as authentic.

**Common typography grammar violations to avoid:**
- Using Kosugi Maru (rounded, traditional) for a shōnen action title
- Using Bebas Neue (cold, condensed) for an iyashikei cover
- Using a glow effect (fantasy register) on a seinen literary cover
- Using no stroke (literary confidence signal) on a busy action cover where contrast is needed
- Setting the volume number in a larger size than the title (hierarchy violation)

### 6.7 Bilingual Title Typography

Many manga covers, particularly in international markets, include both Japanese and English title text simultaneously. This creates a bilingual design challenge.

**Common bilingual configurations:**
1. *Japanese title primary, English title secondary:* Japanese title at full scale; English title at approximately 60-70% of Japanese title height, positioned below or beside the Japanese title
2. *English title primary, Japanese title as subtitle:* Used in English-market editions of manga; Japanese title may appear in small type as an "original title" reference
3. *Equal weight bilingual:* Both languages at the same visual weight; unusual but used for specifically bilingual-audience markets

**Script contrast as a design element:**
On bilingual covers, the contrast between Japanese and Latin letterforms can itself be a visual element. A heavy Dela Gothic One Japanese title paired with a clean Bebas Neue English title creates a cross-cultural visual statement — the different structural systems of the two scripts emphasize each other.

**Sizing relationships:**
Because Japanese kanji are individually more information-dense than Latin letters, a Japanese title that reads at a certain cognitive scale will typically require a larger point size in Latin to read at the same cognitive scale. A rough guideline:
- Japanese title at 100px → English title at approximately 55-70px to achieve similar visual weight
- This varies significantly with font choice — a heavy condensed Latin font (Bebas Neue) at 55px may match a lighter Japanese font at 100px

---

## Appendix A: Genre-to-Font Quick Reference

| Genre | JP Title Font | EN Title Font | Color Register | Stroke |
|---|---|---|---|---|
| Shōnen action | Dela Gothic One | Anton | White on dark + yellow accent | Yes, black 3-4px |
| Isekai | Rampart One / Dela Gothic One | Bebas Neue | Gold or electric blue | Yes, white 2px |
| Seinen literary | Zen Kaku Gothic New 500 | Libre Baskerville | Navy or black, open tracking | No |
| Horror | Kosugi | Big Shoulders Display 900 | Dark red or bone white | No |
| Iyashikei | Klee One / M PLUS 1 | Nunito | Earth tones, warm | No, soft shadow |
| Kodomomuke | M PLUS 1 | Nunito | Bright primary colors | Yes, white 4px |
| BL/Romance | Klee One SemiBold | DM Serif Display | Jewel tones, blush | No, soft glow |
| Josei | Zen Kaku Gothic New 400 | Libre Baskerville Italic | Neutral to warm | No |
| Historical | Kosugi Maru | Libre Baskerville Bold | Aged black, warm cream | No |
| Sports | Zen Kaku Gothic New 900 | Bebas Neue | Sport team colors | Yes, white |
| Sci-fi/Cyberpunk | Noto Sans JP 900 | Big Shoulders Display 900 | Neon blues, cold greys | Yes, neon glow |
| Fantasy | Rampart One | Cinzel | Gold, deep blue | Yes, warm glow |
| Comedy | RocknRoll One | Bangers | Bright saturated | Yes, black 2px |
| Psychological thriller | Noto Sans JP 200 | Big Shoulders Display 700 | Near black, minimal palette | No |
| Mecha | Zen Kaku Gothic New 900 | Cinzel or Barlow Condensed | Metallic silver, gunmetal | Yes, metallic stroke |

---

## Appendix B: OFL Font Summary Table

| Font | License | Weights | Script | Primary Use |
|---|---|---|---|---|
| Noto Sans JP | OFL-1.1 | 100-900 | JA, KN, Latin | Universal Japanese sans |
| M PLUS 1p | OFL-1.1 | 100-900 | JA, KN, Latin | Warm gothic, iyashikei |
| Kosugi | OFL-1.1 | 400 | JA, KN, Latin | Calligraphic-adjacent |
| Kosugi Maru | OFL-1.1 | 400 | JA, KN, Latin | Traditional warm round |
| Klee One | OFL-1.1 | 400, 600 | JA, KN, Latin | Educational, gentle |
| RocknRoll One | OFL-1.1 | 400 | JA, KN, Latin | Casual energetic |
| Zen Kaku Gothic New | OFL-1.1 | 100-900 | JA, KN, Latin | Professional display |
| Dela Gothic One | OFL-1.1 | 400 | JA, ZH, KR, Latin | Maximum impact shōnen |
| Rampart One | OFL-1.1 | 400 | JA, KN, Latin | Fantasy display |
| DotGothic16 | OFL-1.1 | 400 | JA, KN, Latin | Pixel/retro |
| Noto Serif JP | OFL-1.1 | 100-900 | JA, KN, Latin | Literary/mincho |
| Shippori Mincho | OFL-1.1 | 400-800 | JA, KN, Latin | Display mincho |
| Source Han Serif JP | OFL-1.1 | 250-900 | JA, ZH, KR, Latin | Premium mincho |
| Hina Mincho | OFL-1.1 | 400 | JA, KN, Latin | Delicate romantic |
| Kaisei Decol | OFL-1.1 | 400-700 | JA, KN, Latin | Display mincho romantic |
| Zen Maru Gothic | OFL-1.1 | 300-900 | JA, KN, Latin | Round gothic |
| Bangers | OFL-1.1 | 400 | Latin | Manga-style action |
| Anton | OFL-1.1 | 400 | Latin | Heavy action display |
| Bebas Neue | OFL-1.1 | 400 | Latin | Condensed all-caps |
| Big Shoulders Display | OFL-1.1 | 100-900 | Latin | Ultra-condensed thriller |
| Oswald | OFL-1.1 | 200-700 | Latin | Series numbering, seinen |
| Cinzel | OFL-1.1 | 400-900 | Latin | Fantasy/classical |
| Libre Baskerville | OFL-1.1 | 400, 400i, 700 | Latin | Literary serif |
| Nunito | OFL-1.1 | 200-900 | Latin | Rounded warm |
| DM Serif Display | OFL-1.1 | 400, 400i | Latin | Prestige display serif |
| Playfair Display | OFL-1.1 | 400-900 | Latin | Romantic display serif |
| Lato | OFL-1.1 | 100-900 | Latin | Clean humanist |
| Raleway | OFL-1.1 | 100-900 | Latin | Elegant geometric |
| Montserrat | OFL-1.1 | 100-900 | Latin | French market versatile |
| Barlow Condensed | OFL-1.1 | 100-900 | Latin | Industrial condensed |
| Noto Serif TC | OFL-1.1 | 100-900 | Traditional Chinese | TC literary |
| Noto Sans TC | OFL-1.1 | 100-900 | Traditional Chinese | TC action |
| Jf Open Huninn | OFL-1.1 | 400 | Traditional Chinese | TC round gothic |
| Source Han Serif TC | OFL-1.1 | 250-900 | Traditional Chinese | TC premium |
| Noto Sans SC | OFL-1.1 | 100-900 | Simplified Chinese | SC all genres |
| Source Han Sans CN | OFL-1.1 | 100-900 | Simplified Chinese | SC premium |
| LXGW WenKai | OFL-1.1 | 300-700 | SC + TC | Warm handwriting style |
| Noto Sans KR | OFL-1.1 | 100-900 | Korean | KR all genres |
| Nanum Gothic | OFL-1.1 | 400-800 | Korean | KR energetic |
| Nanum Myeongjo | OFL-1.1 | 400-800 | Korean | KR literary |
| Pretendard | OFL-1.1 | 100-900 | Korean | KR versatile modern |
| SUIT Variable | OFL-1.1 | 100-900 | Korean | KR digital-first |
| Noto Sans Arabic | OFL-1.1 | 100-900 | Arabic | AR all genres |
| Cairo | OFL-1.1 | 200-900 | Arabic + Latin | AR contemporary |
| Scheherazade New | OFL-1.1 | 400, 700 | Arabic | AR literary/historical |
| Noto Sans Thai | OFL-1.1 | 100-900 | Thai | TH all genres |
| Sarabun | OFL-1.1 | 100-800 | Thai | TH refined |
| Kanit | OFL-1.1 | 100-900 | Thai | TH action |

---

*Document version: 2.0.0 — 2026-04-18*
*Covers 8 scripts, 15+ genres, 50+ fonts, complete pipeline documentation*
*Cross-reference: fonts/manga_covers/FONT_REGISTRY.yaml for machine-readable font data*
*Supersedes previous 04_typography_system.md (747-line version)*
