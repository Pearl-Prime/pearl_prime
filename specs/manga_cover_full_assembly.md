# Manga Cover Full Assembly — Comprehensive Specification

**Spec ID:** MANGA-COVER-ASSEMBLY-v1.0  
**Status:** Canonical  
**Owner:** Pearl_Architect  
**Date:** 2026-04-18  
**Related specs:** `specs/manga_cover_uniqueness_engine.md`, `specs/LETTERING_AGENT_SPEC.md`

---

## Table of Contents

1. Component Overview
2. Dimension Reference Tables
3. Full Wrap Assembly (Print-Ready)
4. Back Cover Layout
5. Spine Design System
6. Jacket Flaps (JP Tankōbon)
7. Resolution and Color Space Requirements
8. Production Handoff Checklist
9. Digital vs. Print Assembly Variants
10. Market-Specific Assembly Notes

---

## 1. Component Overview

A complete manga book package consists of up to five physical components, depending on format and market. Not all components are required for all markets.

### 1.1 Component Inventory

**Front Cover (Front Board)**  
- The face of the book. The primary commercial asset.
- Contains: cover illustration, series title, volume number, creator credits, and optionally the publisher logo, rating badge, and price.
- This is the component produced by the cover uniqueness engine (Layers 1–3) and adapted by Layer 4 (market adaptation).
- Every market and format requires a front cover.

**Spine**  
- The narrow vertical strip connecting front and back boards.
- Contains: series title (vertical), volume number, publisher logo, and optionally a barcode.
- Width is calculated from page count and paper stock.
- Every bound format requires a spine. Digital editions do not.

**Back Cover (Back Board)**  
- The reverse face of the book.
- Contains: blurb/synopsis, creator bio (optional), publisher logo, barcode, ISBN, price, age rating badge, and any required regulatory marks.
- Every market and format requires a back cover.

**Jacket Flaps (JP Tankōbon Only)**  
- The folded extensions of the dust jacket that wrap inside the front and back boards.
- Front flap (right side): secondary character illustration, creator biography, next volume teaser.
- Back flap (left side): publisher series lineup, promotional text, social handles.
- Required for JP tankōbon with a dust jacket. Not used for digests, paperbacks, or most non-JP formats.

**Inside Cover (JP Convention)**  
- The interior face of the front and back boards, visible when the dust jacket is removed.
- Typically a single-color printed board (board color = brand accent or dark color).
- May contain a small spot illustration or brand text in some imprints.
- JP convention only. US and EU typically use unprinted boards.

### 1.2 Component Relationships

```
PHYSICAL BOOK (ASSEMBLED)
│
├── Dust Jacket (if present)
│   ├── Front Flap (folds inside front board)
│   ├── Front Cover Panel
│   ├── Spine Panel
│   ├── Back Cover Panel
│   └── Back Flap (folds inside back board)
│
└── Bound Book
    ├── Front Board (board face is inside cover)
    ├── Pages
    └── Back Board (board face is inside cover)
```

For paperback formats (no dust jacket), the cover is printed directly on the cover board. There are no flaps. The front cover, spine, and back cover are assembled as a single continuous "wrap" printed on one flat sheet.

For hardcover with dust jacket (JP tankōbon), the wrap includes the flaps. The boards themselves are separate and typically printed in a single color or left unprinted.

---

## 2. Dimension Reference Tables

### 2.1 Trim Sizes by Market and Format

All dimensions are trim size (final cut size after printing and trimming). Bleed and safe area are added during pre-press setup.

| Market | Format | Trim W (mm) | Trim H (mm) | Trim W (in) | Trim H (in) | Notes |
|--------|--------|------------|------------|------------|------------|-------|
| JP | Tankōbon | 112 | 175 | 4.41 | 6.89 | Standard JP manga format |
| JP | Bunkoban | 105 | 148 | 4.13 | 5.83 | A6 format, smaller digest |
| JP | A5 | 148 | 210 | 5.83 | 8.27 | Larger format, some seinen |
| US | Trade 5×7.5 | 127 | 190.5 | 5.00 | 7.50 | Smaller US manga format |
| US | Standard Trade | 139.7 | 215.9 | 5.50 | 8.50 | Most common US manga size |
| US | Digest | 127 | 190.5 | 5.00 | 7.50 | Same as Trade 5×7.5 |
| FR | Standard | 148 | 210 | 5.83 | 8.27 | A5 European standard |
| DE | Standard | 148 | 210 | 5.83 | 8.27 | A5 European standard |
| IT | Standard | 148 | 210 | 5.83 | 8.27 | A5 European standard |
| ES | Standard | 148 | 210 | 5.83 | 8.27 | A5 European standard |
| BR | Standard | 150 | 210 | 5.91 | 8.27 | Slight width variation from A5 |
| MX | Standard | 139.7 | 215.9 | 5.50 | 8.50 | US sizing applied |
| TW | Tankōbon | 112 | 175 | 4.41 | 6.89 | Follows JP sizing |
| CN | Tankōbon | 112 | 175 | 4.41 | 6.89 | Follows JP sizing |
| KR | Tankōbon | 112 | 175 | 4.41 | 6.89 | Follows JP sizing |
| AU | Standard Trade | 139.7 | 215.9 | 5.50 | 8.50 | US sizing applied |

### 2.2 Spine Width Calculation

Spine width is not fixed. It varies by page count and paper stock. Use the following formula:

```
spine_width_mm = (page_count / 2) × paper_thickness_mm + (cover_board_thickness_mm × 2)
```

**Paper thickness by stock type:**

| Stock Type | Thickness per Page (mm) | Common Use |
|-----------|------------------------|------------|
| Manga standard (woodfree, 52gsm) | 0.060 | JP standard interior |
| Manga standard (woodfree, 55gsm) | 0.063 | US standard interior |
| Manga premium (coated, 60gsm) | 0.068 | Color pages, US premium |
| Manga lightweight (newsprint equiv.) | 0.055 | JP compact/bunkoban |

**Cover board thickness by format:**

| Format | Board Thickness (mm) | Notes |
|--------|---------------------|-------|
| JP Tankōbon (paperback) | 0.30 | Soft cover board |
| JP Tankōbon (hardcover) | 2.50 | Hardcover board under dust jacket |
| US Trade Paperback | 0.35 | Standard US soft cover |
| US Hardcover | 2.50 | US hardcover |
| EU Paperback | 0.30 | A5 EU format soft cover |

**Spine calculation examples:**

| Example | Page Count | Paper mm/pg | Board mm | Spine Width |
|---------|-----------|-------------|----------|-------------|
| JP tankōbon, 192pp, standard | 192 | 0.060 | 0.30 | 96 × 0.060 + 0.60 = 6.36mm |
| JP tankōbon, 200pp, standard | 200 | 0.060 | 0.30 | 100 × 0.060 + 0.60 = 6.60mm |
| JP tankōbon, 180pp, standard | 180 | 0.060 | 0.30 | 90 × 0.060 + 0.60 = 6.00mm |
| US trade, 192pp, 55gsm | 192 | 0.063 | 0.35 | 96 × 0.063 + 0.70 = 6.75mm |
| US trade, 200pp, 55gsm | 200 | 0.063 | 0.35 | 100 × 0.063 + 0.70 = 6.99mm |
| EU A5, 200pp, 55gsm | 200 | 0.063 | 0.30 | 100 × 0.063 + 0.60 = 6.90mm |

**Production note:** Spine widths below 4mm cannot reliably carry text. Volumes with fewer than ~130 pages will have nearly blank spines. In this case, spine text may be omitted and only the publisher logo placed at the spine bottom.

**Rounded spine table for common JP tankōbon page counts (52gsm, 0.30mm boards):**

| Pages | Spine Width |
|-------|------------|
| 160pp | 5.40mm |
| 168pp | 5.64mm |
| 176pp | 5.88mm |
| 184pp | 6.12mm |
| 192pp | 6.36mm |
| 200pp | 6.60mm |
| 208pp | 6.84mm |
| 216pp | 7.08mm |
| 224pp | 7.32mm |
| 232pp | 7.56mm |
| 240pp | 7.80mm |

### 2.3 Flap Dimensions (JP Tankōbon)

Flap width is the portion that folds inside the cover boards.

| Format | Flap Width (mm) | Notes |
|--------|----------------|-------|
| JP Tankōbon standard | 80mm | Each flap: 80mm wide |
| JP Tankōbon wide | 90mm | Some premium imprints |
| JP Bunkoban | 60mm | Narrower flap for smaller format |

Flap height = Cover height (same as trim height + bleed).

### 2.4 Bleed and Safe Area by Market

| Market | Bleed (mm) | Front/Back Safe Area (mm) | Spine Safe Area (each side, mm) | Notes |
|--------|-----------|--------------------------|--------------------------------|-------|
| JP | 3.0 | 5.0 | 2.0 | Standard JP printing spec |
| US | 3.175 | 6.35 | 2.5 | 1/8 inch bleed, 1/4 inch safe |
| FR | 3.0 | 5.0 | 2.0 | Standard EU printing spec |
| DE | 3.0 | 5.0 | 2.0 | Standard EU printing spec |
| IT | 3.0 | 5.0 | 2.0 | Standard EU printing spec |
| ES | 3.0 | 5.0 | 2.0 | Standard EU printing spec |
| BR | 3.0 | 5.0 | 2.0 | |
| MX | 3.175 | 6.35 | 2.5 | US spec applied |
| TW | 3.0 | 5.0 | 2.0 | JP spec applied |
| CN | 3.0 | 5.0 | 2.0 | JP spec applied |
| KR | 3.0 | 5.0 | 2.0 | JP spec applied |
| AU | 3.175 | 6.35 | 2.5 | US spec applied |

---

## 3. Full Wrap Assembly (Print-Ready)

### 3.1 Wrap Canvas Geometry

The print-ready wrap is a single continuous flat file containing back cover, spine, and front cover. For dust jacket formats, the flaps are included.

**Paperback wrap (no flaps):**
```
wrap_width  = back_trim_width + spine_width + front_trim_width + (bleed × 2)
wrap_height = trim_height + (bleed × 2)
```

**Dust jacket wrap (with flaps):**
```
wrap_width  = back_flap_width + back_trim_width + spine_width + front_trim_width + front_flap_width + (bleed × 2)
wrap_height = trim_height + (bleed × 2)
```

Note: In most formats, `back_trim_width` = `front_trim_width` = `trim_width`. They are the same value.

**Worked example: JP Tankōbon, 192 pages (6.36mm spine), paperback:**
```
trim_width  = 112mm
trim_height = 175mm
bleed       = 3mm
spine_width = 6.36mm

wrap_width  = 112 + 6.36 + 112 + (3 × 2) = 236.36mm
wrap_height = 175 + (3 × 2) = 181mm
```

**Worked example: JP Tankōbon, 192 pages, dust jacket with 80mm flaps:**
```
wrap_width  = 80 + 112 + 6.36 + 112 + 80 + (3 × 2) = 396.36mm
wrap_height = 181mm
```

**Worked example: US Standard Trade, 200 pages (6.99mm spine), paperback:**
```
trim_width  = 139.7mm
trim_height = 215.9mm
bleed       = 3.175mm

spine_width = 6.99mm

wrap_width  = 139.7 + 6.99 + 139.7 + (3.175 × 2) = 293.74mm
wrap_height = 215.9 + (3.175 × 2) = 222.25mm
```

### 3.2 Canvas Zone Layout (Left to Right)

For right-to-left books (JP, TW, CN, KR — manga reads right-to-left), the binding is on the right. Therefore the wrap file is laid out from right to left:

```
[ BACK COVER ] [ SPINE ] [ FRONT COVER ]
←──────────────────────────────────────→
  (binding on right for RTL books)
```

Wait — this is counterintuitive. Clarification:

For RTL manga, the book is held spine-right. When laying flat for printing, the wrap is still printed as a flat left-to-right file from the printer's perspective. The convention is:

```
JP/RTL Wrap (printer-flat, looking at exterior of cover):
[ LEFT SIDE = BACK COVER ] [ SPINE ] [ RIGHT SIDE = FRONT COVER ]
```

When the reader holds the book, the spine is on the right, the front is the right face.

For LTR books (US, EU markets):
```
US/LTR Wrap (printer-flat, looking at exterior of cover):
[ LEFT SIDE = FRONT COVER ] [ SPINE ] [ RIGHT SIDE = BACK COVER ]
```

Wait — US books are also spine-right from the reader's perspective (left-to-right reading, front cover faces left on a shelf). Let's clarify definitively:

**Standard convention for wrap file layout** (regardless of market):
```
Looking at the FRONT of the book when assembled:
- Front cover = RIGHT face when wrap is unfolded flat
- Spine = CENTER of wrap
- Back cover = LEFT face when wrap is unfolded flat

Therefore, in the print file (printer looking at EXTERIOR surface):
[ BACK COVER | SPINE | FRONT COVER ]
  ←left                       right→
```

This is standard for both JP and US markets. The difference is reading direction inside the book, not the physical cover orientation.

**Coordinate system for wrap file:**

```
Origin (0,0) = top-left corner of the bleed-extended canvas

Back cover zone:
  x: 0 to (back_trim_width + bleed)
  y: 0 to wrap_height

Spine zone:
  x: (back_trim_width + bleed) to (back_trim_width + bleed + spine_width)
  y: 0 to wrap_height

Front cover zone:
  x: (back_trim_width + bleed + spine_width) to wrap_width
  y: 0 to wrap_height
```

### 3.3 Bleed Extension Rules

All artwork must extend into the bleed area. The bleed prevents white edges when the book is trimmed (trimming is not perfectly precise; ±1mm tolerance is standard).

Rules:
- **Background colors and gradients:** Must extend to the full bleed edge. No white fill in bleed.
- **Character art:** Should extend into bleed if character is near the edge. Character should not be cropped by trim line.
- **Text elements:** Must stay within safe area. No text enters bleed region or approaches within safe area margin.
- **Barcode:** Must stay within safe area. Barcode distortion near trim edge could make it unscannable.

### 3.4 Spine-to-Cover Color Continuity

At the join between spine and front cover, and between spine and back cover, the background colors must be continuous. There must be no visible seam.

If the front cover has a gradient background, the gradient must carry into the spine at the correct hue and value. If the back cover has a solid color, the spine edge of the back cover must match that solid color at the join.

For JP mural spines, the illustration continues seamlessly across the spine. The mural artwork is designed at wrap level, not component level.

### 3.5 Resolution and Output Format

| Use Case | Resolution | Format | Color Space |
|----------|-----------|--------|------------|
| Print-ready (professional printer) | 300 dpi minimum | PDF/X-1a or PDF/X-3, TIFF | CMYK |
| Print-on-demand (KDP, IngramSpark) | 300 dpi | PDF | CMYK or high-quality RGB |
| Print preview | 150 dpi acceptable | PDF, PNG | RGB |
| Digital cover (ebook, web store) | 72–150 dpi | JPEG, PNG, WEBP | sRGB |
| Thumbnail (catalog, admin) | 72 dpi | JPEG, WEBP | sRGB |

**CMYK conversion notes:**
- RGB-produced artwork must be converted to CMYK before print submission.
- Conversion profile: Japan Color 2011 Coated (JP market), US Web Coated SWOP v2 (US market), ISO Coated v2 (EU market).
- After CMYK conversion, check: blacks should be rich black (C:60 M:40 Y:40 K:100) for large black areas, not pure K:100 which prints flat.
- Vivid digital colors (neon, saturated screen colors) will shift on print. Review CMYK proof before approval.

---

## 4. Back Cover Layout

### 4.1 Standard Layout Zones

The back cover is divided into functional zones. Zone sizes are percentages of the trim height. Exact measurements are in millimeters at the trim size.

```
┌─────────────────────────────────────────┐  ← TOP (trim edge)
│                                          │
│  [PUBLISHER LOGO ZONE]                   │  ← Zone A: top 12–15mm
│   Publisher logo, imprint name           │
├──────────────────────────────────────────┤
│                                          │
│  [SERIES / TITLE IDENTIFICATION]         │  ← Zone B: 10–15mm
│   Series name in display font            │
│   "Volume X" designation                 │
├──────────────────────────────────────────┤
│                                          │
│                                          │
│  [SYNOPSIS / BLURB ZONE]                 │  ← Zone C: ~55–65% of height
│                                          │
│   Synopsis copy (body font)              │
│   Word count by market:                  │
│   - JP: 150–250 words                    │
│   - US: 100–150 words                    │
│   - FR: 100–180 words                    │
│   - DE: 100–150 words                    │
│   - CN/TW: 200–400 characters            │
│   - KR: 150–250 characters               │
│                                          │
│                                          │
├──────────────────────────────────────────┤
│  [CREATOR BIO ZONE]                      │  ← Zone D: optional, 15–20mm
│   Author name, bio, photo (optional)     │
├──────────────────────────────────────────┤
│  [BARCODE + ISBN + PRICE + RATING]       │  ← Zone E: 20–25mm
│   Barcode (40×25mm), ISBN-13 text,       │
│   price, age rating badge                │
└──────────────────────────────────────────┘  ← BOTTOM (trim edge)
```

**Zone C minimum content requirements:**

The synopsis is the primary commercial text on the back cover. It must:
- Describe the story setting and central conflict without spoilers past the first volume's events.
- Introduce the protagonist and their central motivation.
- End with a hook or question that motivates the reader to open the book.
- Be legible at the body font's minimum readable size for the market (typically 8pt minimum for Japanese, 9pt for Latin scripts).

### 4.2 Blurb Typography Specs

| Market | Script | Recommended Font | Min Size | Line Spacing | Max Width |
|--------|--------|-----------------|----------|--------------|-----------|
| JP | Japanese | M PLUS 1 / Noto Serif JP | 8pt | 1.6× | Trim width − 10mm (5mm each side) |
| US | Latin | Body font (brand) | 9pt | 1.4× | Trim width − 12.7mm |
| FR | Latin | Body font (brand) | 9pt | 1.4× | Trim width − 10mm |
| DE | Latin | Body font (brand) | 9pt | 1.4× | Trim width − 10mm |
| CN | Simplified Chinese | Noto Serif SC | 9pt | 1.6× | Trim width − 10mm |
| TW | Traditional Chinese | Noto Serif TC | 9pt | 1.6× | Trim width − 10mm |
| KR | Korean | Noto Serif KR | 9pt | 1.6× | Trim width − 10mm |
| BR | Portuguese | Body font (brand) | 9pt | 1.4× | Trim width − 10mm |
| MX | Spanish | Body font (brand) | 9pt | 1.4× | Trim width − 10mm |
| ES | Spanish | Body font (brand) | 9pt | 1.4× | Trim width − 10mm |
| IT | Italian | Body font (brand) | 9pt | 1.4× | Trim width − 10mm |
| AU | English | Body font (brand) | 9pt | 1.4× | Trim width − 12.7mm |

### 4.3 Barcode and ISBN Specifications

The ISBN-13 barcode is a mandatory commercial element in all print markets. It must be correctly formed and scannable.

**Barcode physical requirements:**
- Size: minimum 37.29mm × 26.26mm (100% magnification)
- Maximum 200% magnification; minimum 80% magnification for scanability
- Quiet zone: 7.5× module width on left, 5× module width on right (must be white or light background)
- Barcode must be printed in solid black or dark (K:100 or near). No reversed-out white barcodes.
- Background behind barcode: white or light color only. Avoid printing on dark or textured areas.

**Barcode placement by market:**

| Market | Position on Back Cover | ISBN Prefix | Format |
|--------|----------------------|------------|--------|
| JP | Zone E, lower-right quadrant | 978-4 | ISBN-13 with JAN prefix |
| US | Zone E, lower-right (Viz convention) or lower-left (Kodansha) | 978-1 | ISBN-13 |
| FR | Zone E, lower-right | 978-2 | ISBN-13 with EAN price extension |
| DE | Zone E, lower-right | 978-3 | ISBN-13; Altersfreigabe badge adjacent |
| IT | Zone E, lower-right | 978-88 | ISBN-13 |
| BR | Zone A (upper-right — exception) | 978-85 | ISBN-13; CLASSIND rating adjacent |
| MX | Zone E, lower-right | 978-607 | ISBN-13 |
| TW | Zone E, lower-right | 978-986 | ISBN-13 |
| CN | Zone E, lower-right | 978-7 | ISBN-13; 书号 (publishing license) required |
| KR | Zone E, lower-right | 978-89 | ISBN-13; KMRB number required |
| ES | Zone E, lower-right | 978-84 | ISBN-13 with EAN price extension |
| AU | Zone E, lower-right | 978-0 | ISBN-13 |

**Brazil exception:** Brazilian publishing convention places the barcode in the upper-right of the back cover (Zone A area). This is a firm convention across BR publishers. The CLASSIND rating badge appears adjacent to or below the barcode.

**ISBN structure:**
```
ISBN-13 format: 978-{group}-{publisher}-{title}-{check_digit}

Examples:
JP:  978-4-xxxxx-xxx-x
US:  978-1-xxxxx-xxx-x
FR:  978-2-xxxxx-xxx-x
DE:  978-3-xxxxx-xxx-x
```

ISBN-13 numbers are assigned by the ISBN agency of the country of publication. The engine does not generate ISBN numbers; they must be provided as input metadata.

**Price notation by market:**

| Market | Format | Example |
|--------|--------|---------|
| JP | ¥XXX + tax notation | ¥748(税込) |
| US | $X.XX | $12.99 |
| FR | €X,XX | €7,99 |
| DE | €X,XX | €8,99 |
| IT | €X,XX | €9,00 |
| BR | R$XX,XX | R$39,90 |
| MX | $XX MXN | $199 MXN |
| TW | NT$XXX | NT$120 |
| CN | ¥XX | ¥25 |
| KR | ₩X,XXX | ₩6,500 |
| ES | €X,XX | €8,95 |
| AU | A$XX.XX | A$14.99 |

### 4.4 Age Rating Badge Placement and Design

Rating badges must be clearly legible and positioned per market convention.

**Rating badge specifications:**

| Market | Rating System | Badge Size | Placement | Notes |
|--------|-------------|-----------|-----------|-------|
| JP | Publisher self-rating | Flexible | Back cover, Zone E area | Not mandatory by law; publishing convention |
| US | Publisher advisory | 20×20mm typical | Back cover lower-right, or front cover | "T for Teen", "M for Mature" etc. |
| FR | Loi 49-956 | 25×25mm minimum | Back cover, clearly visible | Age bands: all ages, 10+, 12+, 16+, 18+ |
| DE | BPjM/USK | 30×30mm | Back cover | Required: 0/6/12/16/18 |
| IT | AGCOM self-regulation | 20×20mm | Back cover | |
| BR | CLASSIND | 20×20mm | Front AND back cover | L/10/12/14/16/18 |
| MX | Publisher advisory | 20×20mm | Back cover | Optional |
| TW | TGPC | 20×20mm | Back cover | Mandatory for 12+ content |
| CN | NPPA categories | Not a badge system | Manifest, not cover badge | Age advisory in text on back cover |
| KR | KMRB | 20×20mm | Back cover | 전체/12/15/18세 이상 |
| ES | Publisher advisory | 20×20mm | Back cover | |
| AU | ACB | 25×25mm | Back cover | G/PG/M/MA15+/R18+ |

---

## 5. Spine Design System

### 5.1 Spine Text Elements

All spines must carry the following text elements (where physically possible given spine width):

**Mandatory elements (all markets):**
- Series title: primary identification
- Volume number: distinguishes this volume from others in series
- Publisher/imprint logo: brand identification

**Optional elements (include when space permits):**
- Author/creator credit
- ISBN barcode (some publishers; most do not place barcode on spine)
- Tagline or short series descriptor

**Minimum spine width for text:**
- Below 4mm: no text possible; publisher logo mark only (icon without wordmark)
- 4–7mm: single vertical text line (series title abbreviated if necessary) + volume number
- 7–10mm: full series title + volume number + publisher logo
- Above 10mm: can add author credit and other elements

### 5.2 Spine Typography

**JP convention:**
- Text direction: vertical, top-to-bottom (tategumi: 縦組み)
- Series title: top section, vertical, display font
- Volume number: bottom section, larger numerals, display or accent font
- Publisher logo: bottom-most, horizontal

**US/EU convention:**
- Text direction: rotated 90°, readable when book is spine-out on shelf face-right
- US: rotated so that reading direction is bottom-to-top (book tilts left to read)
- EU: same convention as US
- Series title: largest text element
- Volume number: after series title, same size or slightly smaller
- Publisher logo: at one end (usually top or bottom depending on publisher house style)

**Spine typographic specs for JP tankōbon (6.36mm spine, 192pp):**

```
Usable spine area after safe area:
  Height: 175 − (2 × 2) = 171mm usable height
  Width:  6.36 − (2 × 2) = 2.36mm usable width... 

Note: 2.36mm is below the minimum for text. For a 192pp volume with 6.36mm spine,
the spine width is adequate for text because the safe area is 2mm per side,
leaving 2.36mm for text... but this is extremely narrow.

Correction: safe area for spine is measured differently.
The spine is the full spine_width. Text must not fall within 2mm of either
spine-to-cover join. But the text itself can fill the remaining spine width.

For 6.36mm spine: 6.36 − (2 × 2) = 2.36mm for text horizontally.
Japanese vertical text in a 2.36mm column requires approximately 7pt font or smaller.
This is below readability threshold.

Resolution: For spines below 8mm, use vertical text at 6pt (minimum for Japanese)
with generous line spacing. Volume number may be rotated horizontal.
For spines below 5mm, only publisher mark (logo bug) at spine bottom.
```

**Practical spine text sizes for JP tankōbon:**

| Spine Width | Series Title | Volume Number | Publisher Logo |
|-------------|-------------|---------------|---------------|
| < 5mm | Omit | Omit | Logo mark only |
| 5–7mm | 6pt vertical, abbreviated | 6pt | Logo mark |
| 7–9mm | 7pt vertical | 7pt | Logo mark + wordmark abbreviated |
| 9–12mm | 8pt vertical | 8–9pt | Full logo |
| > 12mm | 9–10pt vertical | 9–10pt | Full logo |

### 5.3 JP Mural Spine System

The JP mural spine is a distinctive feature of many JP manga publishers. The spines of consecutive volumes form a continuous image — typically a landscape, a skyline, an abstract pattern, or a scene — that is only visible when all volumes are displayed together.

**Mural design requirements:**

1. **Planning scope:** The mural must be planned for the full anticipated series length. A 12-volume mural plan is the minimum. For open-ended series, plan for 12 volumes and design the mural to tile or extend gracefully.

2. **Slice assignment:** Each volume's spine contributes one vertical slice of the mural image. The slice width = spine_width for that volume. For consistent mural continuity, all volumes in a series should have the same or very similar page counts (within ±5% variation) so spine widths are approximately equal.

3. **Content of the mural:** The mural typically depicts:
   - A panoramic landscape from the series' world
   - The series' recurring motif at large scale
   - An abstract pattern that evokes the brand's mood register
   - A character lineup (all named characters, side by side)
   - A seasonal progression (each volume = one season or month)

4. **Color continuity:** The mural color must harmonize with the front cover of the same volume. The spine's left edge meets the back cover; the right edge meets the front cover. At each join, the spine background color must be close to the adjacent cover's background color.

5. **Volume number legibility:** The mural image must not reduce legibility of the spine text (series title, volume number). Mural images in the spine text area must be light or have a semi-transparent text background strip.

6. **Digital assembly for mural proof:** At time of mural design, a proof must be assembled showing all planned volumes' spines in sequence. This proof is reviewed before any individual volume spine is approved for print.

**Mural design workflow:**

```
1. Design mural image at full assembled width:
   mural_width = sum of all spine_widths across planned volumes
   mural_height = 175mm (JP tankōbon trim height)

2. Slice mural into per-volume spine images:
   vol_1_spine = mural[0 : spine_width_vol_1]
   vol_2_spine = mural[spine_width_vol_1 : spine_width_vol_1 + spine_width_vol_2]
   ... etc.

3. For each volume, add spine text overlay on top of mural slice.

4. Verify: join vol_N_spine right edge with vol_(N+1)_spine left edge visually.
```

**Stillness Press mural convention:**
- Wandering Harvest series mural: a panoramic rice paddy across all volumes, transitioning from spring green (Vol. 1) through summer lush (Vol. 2–4) to autumn gold (Vol. 5–8) to winter bare (Vol. 9–12).
- Mural designed at 12 volumes (84mm total width for 7mm average spine).
- At Vol. 12, the mural ends with a snow-covered field at the right edge — matching the back cover of Vol. 12.

### 5.4 US and EU Spine Design

US and EU spines do not follow the mural convention. Each volume's spine is designed independently.

**Standard US spine layout (top to bottom when book is face-left):**
```
[Publisher Logo — top]
[Series Title — vertical, large]
[VOLUME X — slightly smaller]
[Author Name — optional, smaller]
```

**Color:** Typically matches the front cover's dominant color or a series-specific spine color (consistent across all volumes in the series).

**EU spine:** Same structure as US. Some French publishers include the volume number in larger size at bottom for browsability.

---

## 6. Jacket Flaps (JP Tankōbon)

### 6.1 Front Flap (Right Flap When Jacket Open)

The front flap folds to the inside of the front cover board. It is typically the right flap when the jacket is opened flat.

**Standard front flap layout (top to bottom):**

```
┌────────────────────────────┐  ← top edge (trim)
│                            │
│  [Character Illustration]  │  ← top 40–50% of flap height
│  Secondary character bust  │
│  or protagonist in casual  │
│  pose (not the cover pose) │
│                            │
├────────────────────────────┤
│                            │
│  [Creator Biography]       │  ← middle 30–35% of flap
│  30–50 words in body font  │
│  Author name in display    │
│  font above bio text       │
│                            │
├────────────────────────────┤
│                            │
│  [Next Volume Teaser]      │  ← bottom 20–25% (optional)
│  "Next volume:" or         │
│  "Coming soon:"            │
│  1–3 sentence teaser       │
│                            │
└────────────────────────────┘  ← bottom edge (trim)
```

**Front flap design rules:**
- Character illustration is original to the flap — not reused from the cover image.
- Casual or character-study pose; not action pose.
- Bio uses the brand's body font, smallest comfortable reading size (8–9pt).
- Next volume teaser is optional. If the series is ongoing and the next volume is known, it is preferred.
- Flap background: typically matches one of the brand palette's lighter colors. For Stillness Press: cream_light (#FAF7EE).
- No bleed on interior flap folds. The flap safe area begins at the fold edge.

**Flap safe area:**
- Outer edge (book edge): 5mm safe area from trim
- Fold edge: 5mm safe area from fold (the fold is where the flap meets the cover panel)
- Top/bottom: 5mm safe area

### 6.2 Back Flap (Left Flap When Jacket Open)

The back flap folds to the inside of the back cover board.

**Standard back flap layout (top to bottom):**

```
┌────────────────────────────┐  ← top edge
│                            │
│  [Publisher Imprint        │  ← top 15–20% of flap
│   Series Lineup]           │
│  Other titles from same    │
│  imprint (list format)     │
│  "Also from [imprint]:"    │
│                            │
├────────────────────────────┤
│                            │
│  [Promotional Text]        │  ← middle 40–50%
│  Brand tagline, award      │
│  recognition, praise       │
│  quotes from reviewers     │
│  (if any)                  │
│                            │
├────────────────────────────┤
│                            │
│  [Social / Web Handles]    │  ← bottom 20–25%
│  Publisher website URL     │
│  Social handles (@brand)   │
│  QR code (optional)        │
│                            │
└────────────────────────────┘  ← bottom edge
```

**Back flap design rules:**
- Series lineup: list up to 6–8 other titles from the same imprint. Format: title + volume count or "ongoing."
- Promotional text: may include review excerpts if the series has received press coverage. Format: quote + source.
- Social handles: post-2020 convention; include Twitter/X, Instagram, and/or the publisher's primary platform handles.
- QR code: if present, links to the publisher's website or a series-specific landing page.
- Background: matches front flap background color for visual consistency.

### 6.3 Inside Cover (JP Convention)

The inside covers (interior face of front board and back board) are visible when the dust jacket is removed.

**JP convention:**
- Solid color, matching one of the brand palette dark or accent colors.
- May contain a small spot illustration (often a chibi or simplified character drawing) as a hidden delight for jacket-removers.
- Stillness Press convention: morning_mist (#E8EAD8) for inside front; ink_dusk (#2D3A2E) for inside back.
- No text except possibly a small publisher mark in the inside back board lower-right.

**Production note:** Inside cover printing adds cost. Some publishers use a single-color (one-pass) print for inside covers to control cost. Stillness Press inside covers are single-color: inside front is a matte warm white; inside back is a deep forest green.

---

## 7. Resolution and Color Space Requirements

### 7.1 Source Artwork Resolution

The cover illustration (output of image generation) must be produced at sufficient resolution for all target uses.

**Minimum generation resolution by use:**

| Use | Min Width (px at 300dpi) | Min Height (px at 300dpi) | Notes |
|-----|--------------------------|---------------------------|-------|
| JP Tankōbon front cover only | 1323px | 2067px | 112mm × 175mm at 300dpi |
| JP Tankōbon full wrap (192pp) | 2795px | 2067px | 236.36mm × 181mm at 300dpi, rounded |
| US Standard Trade front cover only | 1654px | 2551px | 139.7mm × 215.9mm at 300dpi |
| US Standard Trade full wrap (200pp) | 3476px | 2628px | 293.74mm × 222.25mm at 300dpi |
| EU A5 front cover only | 1748px | 2480px | 148mm × 210mm at 300dpi |
| Digital ebook cover | 1600px min | 2400px min | sRGB, JPEG/PNG |

**Recommendation:** Generate all cover illustrations at 2000px+ on the short edge. This accommodates all markets and future reprints without quality loss.

### 7.2 Color Space Requirements by Output Channel

| Output Channel | Color Space | ICC Profile | Notes |
|----------------|------------|-------------|-------|
| JP offset print | CMYK | Japan Color 2011 Coated | Standard for JP manga printing |
| US offset print | CMYK | US Web Coated (SWOP) v2 | Standard for US printing |
| EU offset print | CMYK | ISO Coated v2 | Standard for EU printing |
| POD (KDP, IngramSpark) | RGB or CMYK | sRGB IEC61966-2.1 for RGB | Some POD platforms require specific profiles |
| Digital / ebook | RGB | sRGB IEC61966-2.1 | Always sRGB for web distribution |
| Social media | RGB | sRGB | JPEG, max quality |
| Admin thumbnails | RGB | sRGB | WEBP preferred for web delivery |

**Conversion workflow:**
1. Generate cover in RGB (image generation models produce RGB).
2. Verify RGB version meets brand palette specifications.
3. Convert to CMYK using target market ICC profile for print.
4. Review CMYK proof: check that brand palette colors survived conversion.
5. Prepare separate sRGB export for digital distribution.

### 7.3 File Naming Convention

```
{series_id}__vol{volume:04d}__{market}__{component}.{ext}

Examples:
  stillness-press--wandering-harvest__vol0001__JP__front.tif
  stillness-press--wandering-harvest__vol0001__JP__wrap_full.tif
  stillness-press--wandering-harvest__vol0001__JP__back.tif
  stillness-press--wandering-harvest__vol0001__JP__spine.tif
  stillness-press--wandering-harvest__vol0001__JP__flap_front.tif
  stillness-press--wandering-harvest__vol0001__JP__flap_back.tif
  stillness-press--wandering-harvest__vol0001__JP__preview_thumb.jpg
```

All files for a volume are stored in:
```
artifacts/covers/{series_id}/vol_{volume:04d}/{market}/
```

---

## 8. Production Handoff Checklist

### 8.1 Pre-Handoff Verification

Before handing off print-ready files to the printer or distributor, verify:

**Dimensions:**
- [ ] Trim size matches market specification
- [ ] Bleed extends to all edges (no white bands)
- [ ] Safe area respected for all text elements
- [ ] Spine width calculated correctly for actual page count
- [ ] Wrap canvas width = back + spine + front + (bleed × 2)

**Color:**
- [ ] Color space: CMYK for print, sRGB for digital
- [ ] ICC profile embedded in file
- [ ] No out-of-gamut colors for CMYK output
- [ ] Rich black (not flat K:100) for large black areas
- [ ] Barcode in solid black on light background

**Typography:**
- [ ] All fonts embedded (no missing font substitutions)
- [ ] No text within bleed area
- [ ] Title legible at print size
- [ ] Barcode font and number correct
- [ ] ISBN-13 number valid (check digit correct)

**Content:**
- [ ] Age rating badge present and correct for market
- [ ] Publisher logo present and at correct position
- [ ] Barcode present and at correct position for market
- [ ] Synopsis/blurb text correct (no placeholder text)
- [ ] All regulatory marks present (market-specific)
- [ ] No taboo elements for brand

**File format:**
- [ ] PDF/X-1a or PDF/X-3 for professional offset print
- [ ] TIFF for POD platforms that require raster
- [ ] Resolution: 300dpi minimum at final output dimensions

### 8.2 Digital Edition Checklist

For ebook and digital distribution, verify:

- [ ] Front cover only (no spine or back cover for ebook)
- [ ] Minimum 1600×2400px (sRGB)
- [ ] JPEG or PNG, maximum quality
- [ ] File size under 2MB (most platforms limit cover file size)
- [ ] Cover matches print front cover (no different version)

---

## 9. Digital vs. Print Assembly Variants

### 9.1 Print Assembly

Full wrap (back + spine + front) as a single flat file. This is the master print file. All components are present and print-ready.

### 9.2 Digital (Ebook) Assembly

Front cover only. The spine and back cover have no role in digital distribution. The front cover is exported as a separate high-resolution sRGB image.

Digital covers must contain all the essential information that would otherwise appear on the back cover in print, either embedded in the cover metadata or in the ebook's product listing (not on the cover image itself).

### 9.3 Web Store Product Image Assembly

For online retail (Amazon, BookWalker, CDJapan, etc.), the product image sequence typically includes:

1. Front cover — primary product image
2. Back cover — secondary image (shows synopsis for browsing)
3. Inside spread sample — shows interior art quality (not a cover assembly component but part of the product listing)

The web store back cover image is identical to the print back cover, re-exported as sRGB JPEG.

### 9.4 Catalog and Admin Thumbnails

Thumbnail generation is automated. From the front cover file:

```python
def generate_thumbnail(
    front_cover_path: str,
    output_path: str,
    max_dim: int = 300
) -> None:
    """
    Generate a catalog-quality thumbnail from the front cover.
    Preserves aspect ratio. Output: WEBP, 72dpi, sRGB.
    """
    # Implementation: PIL/Pillow resize with LANCZOS resampling
```

Thumbnails are stored at:
```
artifacts/covers/{series_id}/vol_{volume:04d}/thumbs/{market}_thumb.webp
```

---

## 10. Market-Specific Assembly Notes

### 10.1 Japan (JP)

**Dust jacket vs. paperback:** Most JP tankōbon are printed with a dust jacket over a hard or soft board. The jacket has flaps. The boards themselves are usually printed in a single color.

**Price sticker:** JP books traditionally had price stickers rather than printed prices. Modern convention (post-2005) is to print the price on the cover. For Phoenix Omega publications: print price on back cover lower-right, adjacent to barcode.

**Barcode type:** JAN code (Japanese Article Number), which is the Japanese implementation of EAN-13. The JAN prefix for JP books is 978-4.

**Reading direction:** RTL. The front cover is the right face. The book opens left.

**Spine mural:** Planned for all JP series. Spine design is part of series launch package, not volume-level.

### 10.2 United States (US)

**Barcode position:** While US convention is lower-right, major publishers differ:
- Viz Media: lower-right back cover
- Kodansha USA: lower-left back cover
- Yen Press: lower-right back cover
- Seven Seas: lower-right back cover

Phoenix Omega default: lower-right back cover.

**UPC vs. ISBN barcode:** US books use an ISBN-13 barcode (EAN-13) without a UPC barcode. However, some mass-market channels require a UPC. For direct-to-book-trade sales, ISBN-13 only is sufficient.

**Reading direction:** LTR for most US manga editions. Some publishers (Viz, Kodansha) flip the reading direction to RTL to preserve the original Japanese reading experience. When RTL is preserved, the front cover is still the right-facing side, but the binding is on the right.

**Chapter page count:** US editions often include author notes, translator notes, or bonus pages not in the JP edition. This may affect spine width calculations. US production should use the US-specific page count, not the JP page count.

### 10.3 France (FR)

**Loi 49-956 compliance:** The French "Law of July 16, 1949" regulates publications aimed at young people. Any manga with mature themes (violence, sexual content, disturbing imagery) must carry a specific notation. For 16+ content, the notation "Interdit aux moins de 16 ans" must appear on the cover. For 18+ content, a diagonal stripe may be required.

**Price with TVA notation:** French prices include the VAT rate. Format: `€7,99 (TVA incluse)` or similar. The TVA rate for books is 5.5% in France.

**EAN price extension:** French barcodes often include an EAN-5 price extension suffix to the ISBN-13 barcode, encoding the price for automated retail systems.

### 10.4 Germany (DE)

**BPjM and Altersfreigabe:** The Federal Review Board for Publications Harmful to Minors (BPjM) can classify publications. The Altersfreigabe (age approval) badge is produced by the publisher based on content assessment. Size requirement: the badge must be clearly visible on the back cover and must be at least 25mm in diameter.

**§131 StGB:** Publications depicting glorified violence are subject to this statute. Manga with intense action violence may require legal review before German publication.

**Price with MwSt.:** German prices include VAT (Mehrwertsteuer = MwSt.). Book VAT in Germany is 7%. Price notation: `€8,99 (inkl. MwSt.)`.

### 10.5 Brazil (BR)

**CLASSIND mandatory front and back:** The CLASSIND (Classificação Indicativa) rating must appear on both the front cover and the back cover. Front cover placement: typically upper-right corner. Back cover: adjacent to barcode (which is also upper-right for BR).

**Portuguese language:** Brazilian Portuguese, not European Portuguese. Translation must be specific to BR market. The language difference is analogous to American vs. British English.

**ISBN prefix:** Brazil uses 978-85 prefix. Brazilian publishing is organized through the Câmara Brasileira do Livro (CBL).

### 10.6 China (CN)

**NPPA approval:** All books published in China must be approved by the National Press and Publication Administration. This includes a publishing license number (书号, shū hào) that must appear on the back cover or copyright page. The 书号 is not an ISBN but a separate Chinese system. Both ISBN and 书号 are required.

**Content regulation:** CN market has strict content guidelines. Manga with supernatural elements, political themes, or LGBTQ+ content may be restricted or require modification. The cover brief for CN market must be reviewed for content compliance before print.

**Simplified Chinese:** CN market requires Simplified Chinese (zh-Hans). Traditional Chinese (zh-Hant) is not acceptable for CN market distribution.

### 10.7 Taiwan (TW) and Korea (KR)

**Taiwan:** Traditional Chinese script. Follows JP sizing conventions (112×175mm). Manga culture is strong; JP cover conventions are generally followed.

**Korea:** Korea uses its own manhwa publishing tradition but licenses JP manga extensively. KR market uses 112×175mm sizing (matching JP). Rating system: KMRB (Korea Media Rating Board). Back cover must carry the KMRB rating mark and the KMRB approval number.

---

*End of Manga Cover Full Assembly Spec — v1.0*  
*Pearl_Architect | 2026-04-18*
