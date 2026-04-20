# Manga Cover Regulatory Compliance
## Legal and Technical Reference for Cover Generation Automation

**Research Date:** 2026-04-18
**Scope:** Age rating systems and regulatory requirements for manga covers across 12 markets
**Audience:** Engineers implementing programmatic cover generation; editorial compliance staff
**Cross-reference:** artifacts/research/manga_cover_design/03_global_markets.md

---

## Table of Contents

1. [Japan](#1-japan)
2. [USA](#2-usa)
3. [Germany](#3-germany)
4. [France](#4-france)
5. [Italy](#5-italy)
6. [Australia](#6-australia)
7. [Brazil](#7-brazil)
8. [China](#8-china)
9. [South Korea](#9-south-korea)
10. [Taiwan / Hong Kong](#10-taiwan--hong-kong)
11. [Spain](#11-spain)
12. [Latin America General (Mexico, Argentina)](#12-latin-america-general)
13. [Cover Compliance Matrix](#13-cover-compliance-matrix)
14. [Implementation Checklist for Cover Assembly](#14-implementation-checklist-for-cover-assembly)

---

## 1. Japan

### Rating System Overview

Japan does not have a mandatory government-run age rating system for manga comparable to those in Germany, France, or Australia. Manga is regulated through a layered system of publisher self-regulation, industry association guidelines, and prefectural ordinances (most notably Tokyo's Ordinance on the Healthy Development of Youth).

### CERO

**CERO (Computer Entertainment Rating Organization)** rates video games, not manga. It is not applicable to manga covers. However, it is sometimes referenced in the publishing context because manga-game crossover products (artbooks, tie-ins sold with game editions) may carry CERO ratings when the primary product is a game. In this context only, a CERO badge may appear on manga-adjacent packaging. CERO ratings: A (all ages), B (12+), C (15+), D (17+), Z (18+ only).

**Not applicable to standard manga covers.**

### Publisher Self-Regulation

**Imprint designations** are the primary rating mechanism in Japan:

- **少年 (Shōnen):** Boys 12–18. Shōnen Jump, Shōnen Sunday, Shōnen Magazine. No explicit content. Action, adventure, friendship. Publishers enforce internal guidelines; no cover badge required.
- **少女 (Shōjo):** Girls 12–18. Margaret, Nakayoshi. Romantic themes acceptable; no explicit sexual content.
- **青年 (Seinen):** Young men 18+. Young Jump, Big Comic, Evening. Can include nudity, violence, and mature themes. No mandatory cover badge but magazine context signals maturity. Tankobon (collected volumes) carry no mandatory badge.
- **女性 (Josei):** Young women 18+. Cocohana, Feel Young. Similar to seinen in terms of permitted content.
- **成人向け (Adult/18+, also "成人漫画"):** Explicit sexual content for adults 18+. Regulation here is most significant.

### Adult Manga (成人漫画) Self-Regulation

The **Comic Ethics Review Board (コミック倫理研究会, CBMR)** is an industry self-regulatory body. Members include major adult manga publishers. The CBMR:

- Reviews submissions from member publishers before publication
- Issues approval seals for compliant works
- The **倫理マーク (Ethics Mark)** appears on covers of approved adult manga

**The 成年コミック (Adult Comic) mark (成年マーク):** A standardized industry mark indicating content is for adults 18+ only. Adopted by industry associations in the early 1990s following public pressure. The mark appears in a fixed location on the cover (typically lower corner) and on the spine. It is a voluntary industry standard but near-universally observed by major publishers.

**Standard adult manga mark specifications:**
- White circle with "成年コミック" text and "18才未満の方には販売しないでください" (Do not sell to those under 18)
- Or simplified version with "18禁" (18 prohibited) in a circle or box
- Minimum size: approximately 20 × 20 mm
- Placement: front cover lower right or back cover

### Eirin vs. Manga Self-Regulation

**Eirin (映倫)** is the film classification board for movies, not manga. It has no direct applicability to manga covers. The comparison to manga is: film uses a formal board (Eirin) while manga uses voluntary publisher/industry self-regulation. This is an important distinction when publishers in Japan discuss "rating systems" — they are referring to self-regulatory imprint designations and the adult manga industry standards, not a government board equivalent to Eirin.

### Convenience Store Display Rules for Adult Manga

Tokyo Metropolitan Ordinance on the Healthy Development of Youth (東京都青少年の健全な育成に関する条例) and equivalent ordinances in other prefectures regulate the display and sale of "non-healthy publications" (不健全図書 / 有害図書 in some prefectures).

**Practical effect on cover design:**
- Adult manga sold in convenience stores must be displayed in a segregated "adult" section behind a curtain or at a height inaccessible to minors
- The cover cannot feature explicit depictions visible in open display
- Publishers may create "convenience store edition" covers (コンビニ版) with less explicit imagery for mass-market distribution, while the "original" (original shop) edition retains the full-art cover
- The **成年マーク** on covers signals the retailer to apply segregated display
- Seven-Eleven Japan has strict guidelines on what adult manga covers are permitted; Lawson and FamilyMart have similar policies

### Legal Liability Notes

- No criminal liability for publishers for cover content of self-regulated adult manga as long as CBMR or equivalent self-regulatory marks are applied and distribution restrictions are observed
- Prefectural "harmful publications" designation (有害図書指定) can restrict display and sale of specific works within that prefecture
- Child Welfare Act amendments (2014+) strengthened prohibitions on distribution of sexual content involving minors; this applies to cover imagery as well as interior content

---

## 2. USA

### Rating System Overview

The United States has no legal requirement for manga to carry age ratings. The rating systems used are entirely publisher self-regulatory. However, retailer requirements (physical and digital) create de facto standards that function similarly to mandatory ratings.

### Publisher Self-Rating Systems

#### Viz Media Rating System

Viz Media uses a five-tier rating system displayed on all manga back covers:

| Rating | Label | Age Target | Description |
|--------|-------|-----------|-------------|
| A | All Ages | All | No offensive content |
| T | Teen | 13+ | May contain violence, suggestive themes |
| T+ | Older Teen | 16+ | May contain intense violence, suggestive content, crude humor |
| OT | Older Teen | 16+ | Older Teen variant, equivalent to T+ |
| M | Mature | 18+ | May contain extreme violence, sexual themes, adult content |

**Badge design:** Viz's rating badge is a horizontal rectangle approximately 30 × 12 mm, placed in the lower right corner of the back cover. It displays the rating letter (A, T, T+, OT, or M) prominently, the label text, the age indication, and the Viz imprint logo. For M-rated titles, additional advisory text may be included.

**Parental advisory text:** Viz includes specific content descriptors below the rating for Teen and above: "This volume contains [violence / suggestive themes / adult content]." This is not legally required but is standard Viz practice.

#### Yen Press Rating System

Yen Press uses a similar but visually distinct system:

| Rating | Age |
|--------|-----|
| All Ages | All |
| Teen | 13+ |
| Older Teen | 16+ |
| Mature | 18+ |

**Badge design:** Yen Press badges are square or circular, typically 20 × 20 mm, placed in the lower left or lower right of the back cover. The badge includes the rating level and age number.

#### Seven Seas Entertainment Rating System

Seven Seas uses:

| Rating | Age |
|--------|-----|
| Everyone | All |
| Teen | 13+ |
| Older Teen | 16+ |
| Mature | 18+ |

**Badge design:** Seven Seas badges are their own distinct design — often a circle or shield shape. Mature-rated titles (often yaoi/yuri explicit content, horror) include specific content warnings.

#### Kodansha USA

Follows a similar convention to Viz, using text-based rating labels on back covers.

### No Legal Requirement

To be explicit: no federal or state law in the United States requires manga publishers to apply age ratings to their books. The First Amendment protections for speech make content-based regulations difficult. However:

- **Retailers have their own policies:** Walmart, Target, and other mass market retailers may decline to carry or may restrict placement of Mature-rated manga. Publishers consider this when setting ratings.
- **Barnes & Noble** shelves manga by publisher rating; Mature titles may be in a separate adult section.
- **Amazon/Comixology content policies:** Amazon has content policies for digital comics. Explicit sexual content (not just Mature, but explicitly sexual) requires enrollment in the Adult Titles program, which restricts visibility in standard search results.

### ComiXology Content Policies

ComiXology (now Kindle Comics) maintains content policies that affect cover design for digital distribution:

- **Standard content:** Available in main catalog, searchable
- **Mature content (non-explicit):** Available but may be filtered from default search results; user must enable Mature content in account settings
- **Explicit sexual content:** Must be submitted as Adult Title; not visible in standard search; requires age verification

**Cover implications:** For digital, a cover that shows explicit nudity may trigger reclassification to Adult Title even if the interior content would otherwise qualify only as Mature. Publishers designing for Amazon digital distribution must consider that cover imagery determines the initial content tier in some cases.

**Amazon cover review:** Amazon reviews submitted covers for compliance with its content guidelines. Covers that violate guidelines (explicit nudity, sexual acts, etc.) will be rejected. The cover, not just the interior, determines the product's content classification tier.

---

## 3. Germany

### Rating System Overview

Germany has the most complex regulatory environment for manga in Europe, combining a game-focused voluntary rating system (USK) with a legally powerful content indexing board (BPjM, now BzgA-adjacent) and specific provisions for youth protection.

### USK (Unterhaltungssoftware Selbstkontrolle)

**USK** is technically the age rating body for software and video games (Unterhaltungssoftware = Entertainment Software). USK ratings (USK 0, USK 6, USK 12, USK 16, USK 18) are legally required for video games sold in Germany under the Jugendschutzgesetz (Youth Protection Act).

**USK is NOT legally required for manga.** However:
- German manga publishers sometimes apply USK-equivalent age labels (0, 6, 12, 16, 18) voluntarily, in the same spirit as the USK system, because German consumers and retailers understand these numbers as a standard age rating framework
- Some publishers apply text-based recommendations: "Empfohlen ab 16 Jahren" (Recommended for 16 years and older)
- This is publisher convention, not law

**USK-style badge on manga:** When used, the badge is a square or circle with the age number (12, 16, or 18), typically 20 × 20 mm, placed on back cover lower corner. The styling mirrors the official USK game rating badge to leverage consumer recognition of that format.

### BPjM / BzgA — Bundesprüfstelle für jugendgefährdende Schriften

**BPjM (Bundesprüfstelle für jugendgefährdende Schriften** — Federal Review Board for Youth-Endangering Publications) was the body that could index and restrict distribution of manga (and other print media) deemed harmful to youth. As of 2021, the BPjM was folded into the **Bundeszentrale für Kinder- und Jugendmedienschutz (BzKJ)** under the updated Jugendschutzgesetz.

**What indexing means:** A work indexed by BPjM/BzKJ:
- Cannot be displayed in publicly visible areas of retail stores
- Cannot be advertised or promoted in public media
- Cannot be sold to persons under 18
- Can still be sold, but only through direct order, age-verified online stores, or behind-counter storage

**This directly affects cover design** because indexed works effectively cannot be displayed on shelves. Publishers wanting broad retail distribution must ensure covers do not trigger an indexing request.

### What Triggers BPjM Review

German authorities or individuals can submit works to the BzKJ for review. Common triggers:

- **Extreme violence:** Graphic depictions of torture, dismemberment presented approvingly
- **Glorification of violence:** Cover imagery that presents extreme violence as desirable
- **Sexualization of minors:** Any sexual depiction of characters identifiable as minors — this is the most frequent trigger for manga indexing in Germany. Germany has indexed multiple manga titles specifically for this.
- **Nazi symbolism:** Displaying prohibited symbols (Hakenkreuz, SS runes) — relevant for historical manga set in WWII
- **Incitement:** Hate speech imagery

**Case history:** Several hentai and sexually explicit manga have been indexed in Germany. The manga "Battle Angel Alita" (Gunnm) was controversially indexed in the 1990s for violence content, later removed from the index. More recently, certain adult manga with content depicting characters appearing to be minors in sexual situations have been indexed.

### Specific Visual Triggers on Covers for Higher Ratings

For publishers choosing to apply voluntary age ratings:

**12+ trigger elements (publisher convention):**
- Moderate fantasy violence (blood from wounds, combat injuries)
- Suggestive but non-explicit romantic situations
- Moderate horror imagery (zombie-like creatures, body horror without gore)

**16+ trigger elements:**
- Significant graphic violence (visible wounds, death depicted explicitly)
- Partial nudity (non-sexual context)
- Strong horror themes

**18+ trigger elements:**
- Explicit violence with gore
- Sexual themes (non-explicit)
- Extreme horror content

**Cover must not include (for any retail distribution):**
- Sexual depictions of characters appearing to be minors
- Nazi symbols or glorification of fascism
- Extremely graphic gore on cover visible to general public (may trigger BzKJ notice)

### Legal Liability Notes

- Criminal liability exists under German law (StGB §184 and related sections) for distribution of pornographic content depicting minors
- BzKJ indexing creates civil/administrative consequences (distribution restrictions) without criminal charge
- Publishers are liable for content they distribute; "we didn't know the Japanese source material contained this" is not an effective defense

---

## 4. France

### Rating System Overview

France has a legally mandated content classification system for publications addressed to youth, established by the **Loi du 16 juillet 1949 sur les publications destinées à la jeunesse** (Law of July 16, 1949 on publications for youth). This law is the oldest content regulation framework in this survey and has specific, direct effects on manga cover design.

### Loi du 16 juillet 1949

**Scope:** Any publication that is "addressed principally to young people" (addressed to children or adolescents) falls under this law. The law prohibits such publications from featuring content that:
- Presents favorably crime, deception, laziness, cowardice, violence, or racial discrimination
- Presents favorably theft, dishonesty, debauchery
- Inspires or maintains ethnic or national prejudice
- Contains advertising for products harmful to health

**Commission de surveillance et de contrôle des publications destinées à l'enfance et à l'adolescence:** A government commission supervises these publications. The commission can issue warnings and ultimately recommend to the Minister of the Interior that a publication be classified as prohibited for minors.

### Age Labels in Practice (Publisher Convention)

French manga publishers apply age labels as a combination of legal compliance and consumer communication. The French system uses the following age labels, placed on covers:

| Label | Placement | Trigger content |
|-------|-----------|-----------------|
| Tout public (All audiences) | No label, or explicit "Tout public" | No restrictions |
| 8+ | Cover badge or back cover | Mild fantasy violence, mild scary content |
| 12+ | Cover badge or back cover | Moderate violence, mild romantic content |
| 16+ | Cover badge (back cover) | Significant violence, suggestive content |
| 18+ | Back cover, sealed/stickered | Explicit violence, sexual themes |

**These labels are publisher conventions, not legally specified badge designs** — unlike Brazil's CLASSIND (which specifies exact badge design). French publishers may use text ("Déconseillé aux moins de 16 ans" — Not recommended for those under 16) or numeric labels.

**Practice:** Glénat, Ki-oon, and Pika use back cover age indications on titles with mature content. Explicitly adult (18+) manga is typically sold sealed (in a plastic bag) in France, particularly in FNAC's adult sections.

### Cover Restrictions per Category

**All audiences:**
- No restrictions on any cover content that would be permissible in standard advertising

**8+:**
- Mild fantasy violence acceptable (swords, action, non-graphic injury)
- No horror imagery beyond mild spookiness
- No romantic physical contact beyond hand-holding

**12+:**
- Moderate battle violence acceptable (blood not graphic)
- Light romantic themes (kissing, suggestion of relationship)
- No nudity
- Horror imagery acceptable if not realistic/extreme

**16+:**
- Significant battle violence (visible injury, death) in appropriate framing
- Suggestive romantic imagery (not explicit)
- Partial cover nudity (non-frontal) may be acceptable in some contexts
- Strong horror imagery

**18+ / Sealed:**
- Explicit violence, gore
- Sexual themes (suggestive)
- Note: French law prohibits explicitly pornographic content from being sold openly regardless of age rating; such content requires sealed packaging and restricted retail placement

### PEGI for Interactive

**PEGI (Pan European Game Information)** is used for video games in France (and EU generally). It is NOT used for manga. However, French consumers may be familiar with PEGI 12, PEGI 16, PEGI 18 designations from gaming. Some publishers may leverage this familiarity by using similar-looking age-number badges.

### Legal Liability Notes

- The 1949 law creates publisher liability for publications that violate its provisions
- The French commission can require modifications or banning of specific publications
- Violations can result in fines and prohibition of sale
- "Harm to youth" determinations have been made against manga titles in France; publishers must obtain legal advice for borderline content

---

## 5. Italy

### Rating System Overview

Italy has a relatively light regulatory framework for manga compared to Germany and France. The primary regulatory body for audiovisual content is AGCOM (Autorità per le Garanzie nelle Comunicazioni), but its jurisdiction is primarily television and audiovisual media, not print manga.

### AGCOM Regulations

AGCOM regulates:
- Television broadcasting
- Online content (increasingly, post-2021 digital media regulations)
- Telecommunications

**AGCOM has no direct mandatory rating requirement for print manga.** However, the broader AGCOM framework for protecting minors from harmful digital content (implemented under EU Audiovisual Media Services Directive) is being extended to digital comics platforms. Publishers distributing manga digitally in Italy need to be aware of AGCOM's evolving digital content regulations.

### Publisher Self-Regulation (Panini Rating Badges)

**Panini Comics Italy** applies its own rating badges as a publisher convention:

| Badge | Target | Criteria |
|-------|--------|----------|
| Tutti i lettori (All readers) | All ages | Family-appropriate content |
| 13+ | Adolescents 13 and up | Moderate violence, romantic themes |
| 16+ | Older teens | Significant violence, suggestive content |
| 18+ | Adults only | Mature violence, sexual content |

**Panini badge design:** The Panini rating badge is a small colored circle or shield in the lower corner of the back cover (sometimes front cover lower right). The age number appears prominently with "+" symbol. Colors typically: green (all ages), yellow (13+), orange (16+), red (18+).

**Star Comics** applies similar conventions. J-Pop typically relies on imprint identity (their catalog is adult-oriented by default) rather than explicit badges.

### Italian Criminal Code (Codice Penale)

The relevant provisions for cover content in Italy relate to:
- **Art. 528 C.P.** (Obscene publications): Prohibits publication, exhibition, or sale of obscene material. Definition of "obscene" has evolved through case law.
- **Art. 600-quater C.P.** (Possession of child pornography): Applies to any medium including manga that depicts sexual acts involving minors, even if fictional/drawn.

The latter provision is particularly relevant for manga: Italian law has been applied to drawn/illustrated content depicting minors in sexual situations, not only photographic material.

### Legal Liability Notes

- Publishers are criminally liable for art. 600-quater violations (distribution of sexual imagery of minors)
- Civil and administrative liability for content violating the 1948 Constitution's provisions on dignity
- Import restrictions: The Italian Customs Authority has occasionally seized shipments of manga deemed to violate obscenity laws

---

## 6. Australia

### Rating System Overview

Australia has one of the most clearly defined and legally binding content classification systems for publications (including manga) among all markets surveyed. The Australian Classification Board (ACB) classifies films, video games, and publications (books, comics, magazines).

### Australian Classification Board

The ACB is a government body established under the Classification (Publications, Films and Computer Games) Act 1995 (Cth). For **publications** (which includes manga):

**Classification categories for publications:**

| Category | Symbol | Description | Restrictions |
|----------|--------|-------------|--------------|
| Unrestricted (General) | G | Suitable for everyone | No restrictions on sale or display |
| Mature Accompanied | MA | Not suitable for under 15 without parent | No mandatory legal restrictions on sale, but retailers may restrict |
| Restricted (R 18+) | R18+ | Adults only | Sale and supply restricted to adults 18+ |
| Refused Classification | RC | Not permissible for sale | Cannot be imported, sold, or distributed in Australia |

**Note:** The ACB's film and game ratings include additional categories (PG, M, MA15+, R18+, X18+) that do not map directly to publications. For publications specifically, the main division is between "unrestricted" content and "restricted" (R18+) content, with RC as the most severe.

**Unclassified publications:** Unlike films and games, most publications in Australia do not need to be submitted for classification before sale. They are sold without ACB classification unless:
1. An enforcement authority requests classification of a specific work
2. A complaint triggers a classification review
3. A retailer or publisher voluntarily seeks classification for certainty

**This means most manga sold in Australia is never formally classified by the ACB.** Publisher self-rating conventions are the operative standard.

### Cover Restrictions per Rating

**Unrestricted / General:**
- No restrictions on cover content that is not sexually explicit or gratuitously violent
- Action, fantasy, mild horror themes permissible
- Manga sold openly in all retail environments under this default

**MA (Mature Accompanied, 15+) — publisher convention:**
- Significant violence themes
- Suggestive romantic imagery
- Strong language referenced in content description

**R18+ (Restricted):**
- Explicit violence
- Sexual references
- Adult themes
- Must not be sold to persons under 18
- Cover must carry R18+ classification marking if formally classified
- R18+ publications cannot be displayed openly in many retail environments

**RC (Refused Classification):**
- Cannot be legally imported, sold, or distributed in Australia
- Includes publications containing sexual depictions of minors (drawings included)
- Includes content that promotes, incites, or instructs in matters of crime or violence in a manner that is likely to cause serious harm
- **Relevant for manga:** Several adult manga titles have been RC'd in Australia for depicting sexual content involving characters appearing to be minors. Importation of such titles is a criminal offense.

### Cover Badge Design

When a publication is formally classified by the ACB, the classification marking must appear on the front cover or packaging:
- **R18+:** Red octagonal badge with white "R 18+" text, minimum 25 × 25 mm, placed in prominent position on front cover
- The classification number (set by the National Classification Code) and the ACB symbol are mandated elements

For informally sold (unclassified) manga, publishers typically apply no badge or use publisher conventions from their home market.

### Legal Liability Notes

- **Importation:** Customs Act 1901 prohibits importation of RC material. Individuals importing RC manga risk confiscation and potentially criminal charges.
- **Sale:** Sale of RC publications carries criminal penalties under state and territory legislation.
- **The RC risk for manga cover design:** A cover that features sexualized imagery of characters appearing under 18 could trigger RC classification. Publishers releasing manga in Australia must screen cover imagery for this specific risk.
- **Online supply:** Australia's Online Safety Act 2021 extends some classification enforcement to online distribution, creating risk for digital manga distributors.

---

## 7. Brazil

### Rating System Overview

Brazil has a mandatory government content rating system — the **CLASSIND (Classificação Indicativa)** — administered by the Ministry of Justice (Ministério da Justiça e Segurança Pública). Unlike most other markets in this survey, Brazil's CLASSIND is legally binding and the badge design is specified by the government.

### CLASSIND Rating System

**CLASSIND** applies to films, games, music, and publications including manga. The ratings are:

| Rating | Symbol | Color | Age | Description |
|--------|--------|-------|-----|-------------|
| Livre (Free) | L | Green | All ages | Suitable for all audiences |
| 10 Anos | 10 | Blue | 10+ | Mild violence, mild emotional content |
| 12 Anos | 12 | Yellow | 12+ | Moderate violence, mild sexual content |
| 14 Anos | 14 | Orange | 14+ | Significant violence, suggestive sexual content |
| 16 Anos | 16 | Red | 16+ | Intense violence, sexual content |
| 18 Anos | 18 | Black | 18+ | Extreme violence, sexual content, drug use |

### Badge Design and Placement

**CLASSIND badge design is government-specified:**
- Circle shape
- Specific color per rating tier (as listed above)
- Age number prominently displayed (or "L" for Livre)
- Minimum size: 25 mm diameter for print publications
- Must appear on **front or back cover** of all rated publications
- The badge design cannot be modified, scaled below minimum size, or recolored

**Mandatory placement (Brazil):** Publishers selling manga in Brazil must include the CLASSIND badge. This is not optional. Distribution through major retail channels (Amazon Brasil, Saraiva, FNAC) requires CLASSIND compliance. Panini Brasil and JBC both apply CLASSIND badges on all their publications.

**"Impresso no Brasil" compliance:** When printed in Brazil, the edition must also include the mandatory printer's declaration (see market document).

### Cover Requirements per Rating

**Livre (L) / Green:**
- Cover may contain family-appropriate imagery
- No violence beyond cartoon-level
- No romantic or sexual themes
- No horror imagery

**10 Anos / Blue:**
- Mild fantasy violence on cover acceptable
- Mild adventure themes
- No romantic physical contact beyond hand-holding

**12 Anos / Yellow:**
- Moderate fantasy violence (battle scenes, non-graphic injury)
- Mild romantic themes
- Scary but non-graphic horror imagery

**14 Anos / Orange:**
- Significant violence acceptable on cover (visible wounds, dramatic battle)
- Suggestive romantic imagery (no explicit contact)
- Horror imagery at moderate intensity

**16 Anos / Red:**
- Intense violence imagery acceptable
- Strong romantic/suggestive imagery
- Drug or alcohol reference imagery
- Cover must carry the red 16 badge

**18 Anos / Black:**
- Extreme violence (gore) possible
- Sexual themes (non-explicit nudity may be present)
- Extreme horror
- Cover must carry black 18 badge
- Retail display restrictions: 18+ publications cannot be displayed in open view accessible to minors at retail

### Marco Civil Implications

The **Marco Civil da Internet** (Brazil's Internet Civil Rights Framework, Law 12.965/2014) establishes user rights and provider obligations for internet services in Brazil. Its direct implications for manga cover design are limited, but:
- Digital manga platforms distributing in Brazil must comply with content classification requirements for digital publications
- Age verification requirements under Marco Civil and complementary regulations apply to platforms distributing 18+ content
- Publishers distributing digitally in Brazil should ensure their digital cover images match the CLASSIND rating displayed on physical editions

### Legal Liability Notes

- Publishers failing to display CLASSIND badge can face fines and removal from distribution channels
- Sale of 18+ rated material to minors is a violation of the Estatuto da Criança e do Adolescente (ECA — Child and Adolescent Statute), carrying criminal liability
- Import of publications without proper CLASSIND classification can be delayed or blocked at Brazilian customs

---

## 8. China

### Rating System Overview

China does not have a manga-specific content rating system comparable to CLASSIND or USK. Instead, manga is regulated through a combination of:
1. General publication content restrictions enforced through the National Press and Publication Administration (NPPA / 国家新闻出版总署)
2. Content review requirements for imported publications
3. Self-regulatory guidelines from licensed publishers
4. Platform-specific content policies for digital distribution

### Content Restrictions

**Published regulations affecting manga covers and content include:**

**General Publication Management Regulations (出版管理条例):** All publications in China must comply. Prohibited content includes:
- Content endangering national unity, sovereignty, or territorial integrity
- Content divulging state secrets
- Content propagating terrorism, extremism, ethnic hatred, discrimination
- Content propagating obscenity, pornography, gambling, violence, or superstition that harms social ethics
- Content harming minors' physical and mental health

**"Superstition" and supernatural content:** This is a notable and frequently misunderstood restriction. The prohibition is on content that "propagates superstition" (宣扬封建迷信), which in practice has been interpreted to restrict:
- Content glamorizing ghosts, demons, and supernatural beings in contexts that could be seen as promoting belief in the supernatural
- This does NOT mean all supernatural content is banned — manga with fantasy/supernatural elements is widely published in China
- The key distinction is between fantasy as clearly fictional entertainment vs. content that could "promote superstition"
- In practice, this creates uncertainty for publishers, leading to self-censorship on borderline titles

**Import restrictions:** Foreign manga requires approval from the NPPA for official publication. The review process can take months to years. Unapproved foreign manga cannot be legally published or distributed in China. This creates significant delays between Japanese publication and Chinese availability.

**Domestic production standards:** Domestically produced Chinese manhua is subject to NPPA registration and content review. The same content restrictions apply. LGBTQ content is a particularly sensitive area — there have been periods of more and less restriction; as of 2024, content that is explicitly LGBTQ in romantic/sexual terms faces review challenges.

### Cover-Specific Implications

**Cover imagery that has created challenges:**
- Imagery that could be interpreted as promoting Japanese militarism or nationalism (Rising Sun flags, certain WWII-era uniforms, imperial iconography)
- Horror imagery that could be construed as "promoting superstition" in a serious/glamorizing way
- Political content (references to Taiwan independence, Tibet, Xinjiang, Tiananmen in any sympathetic framing)
- Explicit violence

**What typically bypasses restriction:**
- Character-focused covers with minimal background (less likely to contain triggerable imagery)
- Action scenes without political/military symbolism
- Cover art that has been modified to remove triggerable elements
- Art-book and promotional imagery from works approved for digital distribution

### Platform Content Policies

**Tencent Comics / Bilibili Comics** apply their own content policies in addition to NPPA requirements:
- Both platforms self-regulate to maintain their operating licenses
- Content that might be challenged under NPPA guidelines is typically not featured even if technically legal
- Age verification is implemented for mature content (via phone number linking)
- Platform cover display policies are more conservative than interior content policies

### Legal Liability Notes

- Publishers operating without proper NPPA approval face fines and operational restrictions
- Criminal liability exists for distribution of prohibited content under the Criminal Law (刑法) provisions on obscenity (第364-367条)
- Foreign publishers distributing directly to Chinese consumers through digital channels without proper approvals also risk liability

---

## 9. South Korea

### Rating System Overview

South Korea has a government-administered content rating system for publications including manga, operated through the **Game Rating and Administration Committee (GRAC)** for games and the **Korea Media Rating Board (KMRB / 영상물등급위원회)** for audiovisual media. For publications (books and manga), the primary framework is the **Youth Protection Act (청소년보호법)**.

### Youth Protection Act

**The Youth Protection Act** designates certain publications as "harmful to youth" (청소년유해물) through the **Korea Communications Standards Commission (KOCSC / 방송통신심의위원회)** and the **Ministry of Gender Equality and Family (여성가족부)**.

**A publication designated as "harmful to youth" cannot be:**
- Sold to persons under 18
- Displayed openly in retail environments accessible to minors
- Advertised in media accessible to minors

**The designation is based on content, not a pre-submission rating system.** Most manga is sold without any government rating; complaints or enforcement actions trigger designation review.

### Publisher Rating Conventions

Korean manga publishers (Haksan, Daewon) apply voluntary age ratings:

| Rating | Description |
|--------|-------------|
| 전체이용가 (All ages) | Suitable for all |
| 12세 이용가 (12+) | 12 and older |
| 15세 이용가 (15+) | 15 and older |
| 18세 이용가 (18+) | Adults only |

**Badge design:** Small square badge with Korean text and age number, typically 20 × 20 mm, placed on back cover. Color conventions: blue (all ages), green (12+), yellow (15+), red/black (18+).

### KMRB for Webtoon Print Collections

The **Korea Media Rating Board (영상물등급위원회, KMRB)** has jurisdiction over webtoons published on platforms, and by extension, their print collections. KMRB ratings for webtoon content:

| Rating | Korean | Age |
|--------|--------|-----|
| All | 전체 | All ages |
| 12 | 12세+ | 12+ |
| 15 | 15세+ | 15+ |
| 18 (Adult) | 18세+ / 청소년이용불가 | Adults only |

**청소년이용불가 (Not available to youth):** The most severe platform-level restriction, equivalent to Adults Only. Content with this designation must be behind age verification on platforms.

**Print collection implications:** When a webtoon with a 18+ platform rating is published as a print collection, the print collection carries the equivalent 18+ designation with the badge displayed on the cover.

### Legal Liability Notes

- Sale of designated "harmful to youth" materials to minors under 18 is a criminal offense under the Youth Protection Act, with fines and imprisonment possible
- Importation of publications that would qualify as harmful to youth is also restricted
- Political sensitivity: Works involving Korea-Japan history or comfort women issues may face scrutiny beyond standard youth protection frameworks

---

## 10. Taiwan / Hong Kong

### Taiwan

#### TGPC (Taiwan Game and Publishing Classification)

Taiwan's primary classification body for games is the **Taiwan Game and Publishing Classification (台灣遊戲內容分級)** system. For publications (manga, books), the applicable framework is the **Children and Adolescents Protection Act (兒童及少年福利與權益保障法)**.

**Mandatory age labels for publications in Taiwan:**

| Label | Chinese | Age | Badge Color |
|-------|---------|-----|-------------|
| 普遍級 (General) | 普 | All | Green |
| 保護級 (Protected) | 護 | 6+ | Blue |
| 輔導級 (Guidance) | 輔 | 12+ | Yellow |
| 輔15級 | 輔15 | 15+ | Orange |
| 限制級 (Restricted) | 限 | 18+ | Red |

**Mandatory placement:** The 輔導級 (12+), 輔15級 (15+), and 限制級 (18+) labels are **legally required** to appear on publications. The 限制級 (18+) designation triggers:
- Mandatory shrink-wrapping of the publication
- Display restrictions — cannot be displayed openly
- Sale restrictions — cannot be sold to persons under 18

**Badge design:** Specified by law. Circle with Chinese character in center (普, 護, 輔, 限) and age range in text. Minimum size: 25 mm diameter. Placed on front cover or back cover (front cover preferred for 限制級).

**Enforcing body:** The Ministry of the Interior (內政部) oversees enforcement. Convenience stores (7-Eleven, FamilyMart) are major enforcement points — they conduct age verification at the counter for shrink-wrapped materials.

### Hong Kong

#### Obscene Articles Tribunal (OAT)

Hong Kong's **Obscene Articles Tribunal (淫褻物品審裁處, OAT)** classifies publications under the Obscene Articles Ordinance (Cap. 390).

**Classification categories:**

| Category | Description | Publication requirements |
|----------|-------------|--------------------------|
| Class I | Not obscene or indecent | No restrictions |
| Class II | Indecent | Must be sealed/wrapped; "For Adults Only" warning; cannot be displayed |
| Class III | Obscene | Prohibited from publication, sale, or importation |

**Publication requirements for Class II:**
- The publication must carry a warning label: "For Adults Only" (成人刊物)
- The label must appear prominently on the cover
- The publication must be sealed/wrapped so the cover is not directly visible
- Cannot be sold to persons under 18

**OAT classification process:**
- Can be triggered by complaint or by police action
- Can be proactive (publisher submits for classification certainty)
- Once classified, the classification applies to all copies of that specific work

**Label design (Class II):** Black border rectangle with white text: "此書類別屬於不雅 只准售予十八歲或以上人士" (This publication is classified as indecent. Only for sale to persons 18 years of age or over). Minimum dimensions not explicitly specified in the Ordinance but standard practice is approximately 50 × 25 mm, placed prominently on front cover or wrapper.

### Legal Liability Notes

**Taiwan:**
- Sale of 限制級 materials to minors — criminal liability under Children and Adolescents Protection Act
- Failure to display required age label — administrative fine
- Failure to shrink-wrap 限制級 publications — administrative fine and potential criminal liability

**Hong Kong:**
- Sale of Class II publications without proper labeling and sealing — criminal offense under Obscene Articles Ordinance, fines and imprisonment
- Sale of Class III (obscene) publications — criminal offense, more severe penalties
- Importation of obscene articles — customs seizure and criminal liability

---

## 11. Spain

### Rating System Overview

Spain has one of the lightest regulatory frameworks for manga publications among European markets. There is no mandatory government rating system specifically for manga or comics. The main framework that could apply is:

- **Ley Orgánica de Protección Jurídica del Menor (LOPJM)** — Organic Law on the Legal Protection of Minors: establishes broad protection frameworks but not a specific publication rating mandate
- **Código Penal (Criminal Code):** Provisions on obscenity and child protection

### Publisher Convention

Spanish manga publishers apply age ratings as a voluntary convention:

- "Recomendado para mayores de X años" (Recommended for those over X years old) — text-based indication on back cover
- Common ratings: 7+, 12+, 16+, 18+
- No standardized badge design — publishers use their own visual designs

**Planeta Cómic** applies "Recomendado para mayores de X años" text on back covers of titles with mature content. No standardized icon system across publishers.

**18+ / explicit content:** While not legally required, explicit adult manga is typically sold sealed in Spain and displayed in restricted sections of comic shops. General bookstores (El Corte Inglés, FNAC Spain) typically do not stock explicit adult manga regardless of legal requirements.

### Legal Liability Notes

- **Art. 189 of the Código Penal:** Prohibits pornographic material involving minors, including drawn/illustrated material. Applies to manga with sexual depictions of characters appearing to be minors.
- No specific fines for failure to apply age labels (since there is no mandatory system) — but civil and criminal liability can arise from content violations
- Spain is subject to EU law including the Directive on combating sexual abuse and exploitation of children (2011/93/EU), which requires criminalization of child sexual abuse material including virtual/drawn content

---

## 12. Latin America General

### Mexico — Calificación de Contenidos

**Mexico does not have a manga-specific mandatory rating system.** The existing media content classification systems are:

**Calificaciones de la Secretaría de Gobernación (SEGOB) for audiovisual content:**
| Rating | Audience |
|--------|----------|
| A | All audiences |
| B | General audiences (suitable for all, informational) |
| B15 | 15 years and older |
| C | Adults |
| D | Adults, extremes of sex and/or violence |

This system applies to film, video, and television. For publications (manga), there is no equivalent mandatory system.

**Practice:** Panini México applies text-based age advisories on back covers of mature manga titles: "Este libro está dirigido a adultos" (This book is directed at adults) or "No recomendado para menores de X años" (Not recommended for those under X years of age).

**Legal framework:** The Ley General de los Derechos de Niñas, Niños y Adolescentes and related laws establish protections for minors but do not create a specific publication rating mandate.

### Brazil CLASSIND (Repeated from Section 7)

Brazil's CLASSIND system is covered in Section 7 and represents the most formally structured mandatory rating system in Latin America.

### Argentina

**No formal manga rating system exists in Argentina.** Argentine law (Ley 23.052 on film content) addresses audiovisual media but not publications specifically. Publisher conventions apply:

- **OVNI Press** and **Ivrea** (both Argentine publishers) apply publisher-specific age recommendations on back covers, typically: "No recomendado para menores de X años"
- 18+ adult manga is typically sold sealed
- Argentine customs has occasionally seized shipments of explicitly adult manga containing apparent minors in sexual situations, applying criminal law provisions rather than publication-specific regulations

**Código Penal Argentino:** Art. 128 prohibits production, distribution, and financing of pornographic material depicting persons under 18, including drawn material. This applies to manga covers and content.

### Colombia, Chile, Peru, Venezuela, Central America

These markets generally lack manga-specific rating regulations. The distribution of Spanish-language LATAM editions from Panini México or Argentine publishers (OVNI, Ivrea) means these markets receive covers compliant with Mexican or Argentine publisher conventions. Local enforcement depends on:
- Local child protection laws (which exist in all these countries) applied case-by-case
- Customs enforcement at import
- Retailer self-regulation

---

## 13. Cover Compliance Matrix

The following matrix summarizes what cover content triggers what rating or restriction across markets. It is intended as a quick-reference tool for cover design decision-making.

### Matrix: Content Type → Rating Trigger by Market

**Legend:**
- **OK** = Permitted without rating elevation
- **T/12+** = Triggers Teen / 12+ equivalent rating
- **16+** = Triggers 16+ equivalent rating
- **18+** = Triggers 18+ equivalent rating, restricted distribution
- **BLOCK** = May be prohibited entirely / RC / indexed
- **N/A** = Not applicable (no mandatory system; publisher convention applies)

| Cover Content | JP | US | DE | FR | IT | AU | BR | CN | KR | TW | ES | MX |
|---------------|----|----|----|----|----|----|----|----|----|----|----|----|
| Fantasy violence (swords, punches, no blood) | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK |
| Battle violence with visible blood (non-graphic) | OK | T | 12+ | 12+ | 13+ | OK | 12 | Review | 12+ | 12+ | N/A | N/A |
| Graphic gore / dismemberment on cover | 成年 | M | 18+ | 16+ | 18+ | R18+ | 16-18 | Block | 18+ | 限 | 18+ | N/A |
| Mild romantic (clothed couple, holding hands) | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK |
| Suggestive / pinup imagery (non-nude) | 成年 | T+ | 16+ | 16+ | 16+ | MA | 14-16 | Review | 15+ | 輔15 | 16+ | N/A |
| Partial adult nudity (non-explicit) | 成年 | M | 18+ | 18+ | 18+ | R18+ | 16-18 | Block | 18+ | 限 | 18+ | N/A |
| Explicit adult sexual content on cover | 成年 | M | BLOCK | BLOCK | BLOCK | RC/R18+ | 18 | Block | BLOCK | 限/Block | BLOCK | N/A |
| Sexual content with apparent minor | BLOCK | BLOCK | BLOCK | BLOCK | BLOCK | RC | BLOCK | BLOCK | BLOCK | BLOCK | BLOCK | BLOCK |
| Horror imagery (monsters, not graphic) | OK | T | 12+ | 12+ | 13+ | OK | 12 | Review | 12+ | 12+ | N/A | N/A |
| Graphic horror (extreme body horror, realistic gore) | 成年 | M | 16-18+ | 16+ | 18+ | R18+ | 16-18 | Block | 18+ | 限 | 16+ | N/A |
| Drug / alcohol reference imagery | OK | T | 12+ | 12+ | 13+ | OK | 12 | Review | 15+ | 12+ | N/A | N/A |
| Nationalist / militarist symbolism (Japan, WWII-era) | — | OK | BLOCK | Review | OK | OK | OK | BLOCK | Review | OK | OK | OK |
| Supernatural / demonic imagery (serious framing) | OK | OK | Review | Review | OK | OK | OK | Review | OK | OK | OK | OK |
| LGBTQ romantic themes (non-explicit) | OK | OK | OK | OK | OK | OK | OK | Review | OK | OK | OK | OK |

**Notes on table:**
- JP "成年" = Adult manga mark required (industry self-regulation)
- CN "Review" = Subject to content review; outcome uncertain; "Block" = likely prohibited
- AU ratings apply when formally classified; unclassified manga is sold with publisher self-labels
- MX/ES "N/A" = No mandatory system; publisher convention applies

---

## 14. Implementation Checklist for Cover Assembly

This checklist is for use in programmatic cover generation workflows to ensure compliance across target markets before cover art is finalized and distributed.

### Pre-Generation Checklist (Before Creating Cover Art)

- [ ] Identify all target markets for this volume
- [ ] Determine the series' existing rating in each target market (from prior volumes or series rating)
- [ ] Review interior content rating triggers to ensure cover is consistent with interior rating
- [ ] Confirm publisher license terms — some licensors specify what cover elements can be included
- [ ] Note any specific market-prohibited content (e.g., CN political content restrictions, DE minor sexualization risk)

### Cover Art Review Checklist

**Violence content:**
- [ ] Categorize violence level: None / Fantasy / Blood present / Graphic gore
- [ ] For blood/graphic content: flag for 12+/16+/18+ in relevant markets per matrix
- [ ] For graphic gore: flag for 18+ restricted distribution in FR, DE, IT, AU, BR; review for CN

**Romantic/Sexual content:**
- [ ] Categorize romantic content: None / Hand-holding / Suggestive / Partial nudity / Explicit
- [ ] For suggestive/partial nudity: flag for 16+/18+ in relevant markets per matrix
- [ ] For explicit content: NOT PERMITTED on publicly distributed covers in any major market
- [ ] For any content involving apparent minor in romantic/sexual context: BLOCKED in all markets — do not generate

**Cultural/Political content:**
- [ ] Check for imagery potentially interpreted as Japanese militarism (for CN market)
- [ ] Check for supernatural/demonic framing (for CN content review)
- [ ] Check for political content that could trigger market-specific review (CN, KR)

**Horror content:**
- [ ] Categorize horror level: None / Mild spooky / Monster / Graphic body horror
- [ ] For graphic horror: flag for 16+/18+ in relevant markets

### Badge Assembly Checklist by Market

**Japan:**
- [ ] If adult content: Add 成年コミック (成年マーク) badge, minimum 20×20mm, front or back cover lower corner
- [ ] If adult content: Verify convenience store distribution restrictions

**USA:**
- [ ] Apply Viz/Yen/Seven Seas/Kodansha publisher rating badge per series publisher's system
- [ ] Verify badge is in lower right corner of back cover
- [ ] For M-rated: add content descriptor text
- [ ] For digital (Amazon): verify cover image does not include explicit nudity (separate from interior rating)

**Germany:**
- [ ] If applying USK-style label: specify age number (12/16/18) in square/circle badge, lower corner of back cover, 20×20mm
- [ ] Review cover for BzKJ risk indicators (minor sexualization, extreme gore, prohibited symbols)
- [ ] If Nazi/militarist symbols present: remove before German distribution

**France:**
- [ ] Apply age indication badge or text as appropriate to content level (8+/12+/16+/18+)
- [ ] Verify legal notices on copyright page (Loi 49-956, dépôt légal)
- [ ] For 18+ content: confirm retail partner's sealed-packaging requirement

**Italy:**
- [ ] Apply Panini/publisher rating badge if applicable (Panini: circle color-coded per age)
- [ ] Verify no content triggering Art. 528 C.P. or Art. 600-quater C.P.

**Australia:**
- [ ] If formally classified: include ACB R18+ badge (red octagon, 25×25mm min, front cover) if applicable
- [ ] For informally distributed: apply publisher rating convention from home market
- [ ] Review for RC risk indicators (minor sexualization) — do not distribute in AU if present

**Brazil:**
- [ ] Apply CLASSIND badge (government-specified circle badge, color-coded) — MANDATORY
- [ ] Minimum badge size: 25mm diameter
- [ ] Placement: front or back cover — back cover lower corner standard
- [ ] Include "Impresso no Brasil" if locally printed
- [ ] Verify CLASSIND badge color matches assigned rating (L=green, 10=blue, 12=yellow, 14=orange, 16=red, 18=black)
- [ ] For 18+ (black badge): confirm retailer compliance with display restrictions

**China:**
- [ ] Submit for publisher/platform review BEFORE finalizing
- [ ] Remove any flagged cultural/political elements from cover art
- [ ] Verify no supernatural imagery in "glamorizing superstition" frame
- [ ] Ensure CIP data block will be included in print files
- [ ] Do not distribute digitally without platform approval

**South Korea:**
- [ ] Apply publisher rating badge (전체이용가 / 12세+ / 15세+ / 18세이용가) — publisher convention
- [ ] Badge: square format, 20×20mm, back cover
- [ ] For 18+: verify retailer compliance with display restrictions

**Taiwan:**
- [ ] Apply mandatory age label (普/護/輔/限) as circle badge, 25mm min diameter, front or back cover
- [ ] For 限制級 (18+): mandatory shrink-wrapping of physical product — coordinate with printer
- [ ] For 限制級: badge on front cover preferred

**Hong Kong:**
- [ ] If Class II (indecent): mandatory "For Adults Only" label on cover, 50×25mm approx
- [ ] If Class II: mandatory sealed/wrapped packaging
- [ ] If Class III (obscene): do not distribute

**Spain:**
- [ ] Apply publisher age recommendation text ("Recomendado para mayores de X años") on back cover
- [ ] No standardized badge required — text format is standard
- [ ] For 18+: coordinate with retailer for sealed display

**Mexico / LATAM:**
- [ ] Apply publisher age advisory text ("No recomendado para menores de X años") on back cover
- [ ] For 18+: specify "Para adultos únicamente" on back cover
- [ ] "Hecho en México" if printed in Mexico — coordinate with printer

### Final Pre-Distribution Verification

- [ ] All target market badges have been applied or confirmed not required
- [ ] Badge sizes meet minimums for each market
- [ ] Badge colors match specification (especially CLASSIND Brazil — exact colors mandated)
- [ ] Cover art has been reviewed for all market-specific prohibited content
- [ ] Barcode placement does not overlap badge placement
- [ ] Back cover text has been reviewed in all target languages
- [ ] Price display conventions correct for each market (period vs. comma decimal, currency symbol position)
- [ ] Spine text direction confirmed for target market (US: top→bottom; Europe/LATAM: bottom→top)
- [ ] Digital cover image is RGB (not CMYK) for digital platform submission

---

*Document prepared by Pearl_Research — 2026-04-18*
*Version 1.0 — initial comprehensive draft*
*Cross-reference: artifacts/research/manga_cover_design/03_global_markets.md for full market context*
