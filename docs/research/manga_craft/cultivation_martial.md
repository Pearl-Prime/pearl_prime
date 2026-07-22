# Cultivation / Martial Arts (Xianxia) — Craft Bible

> Phase 2X.3 backfill (M3 lane). Pattern follows existing bibles in this directory.
> Genre Shell — progression fantasy / power-tier martial arts. `genre_id: cultivation_martial`
> (taxonomy id `cultivation`; see `config/manga/canonical_genre_list.yaml` aliases).
> Allocation: primary tier in `zh_CN` (18%, largest single-genre share in that locale) and
> secondary tier in `zh_TW` (8%) per `config/manga/locale_genre_allocations.yaml`.
> Touchstones: *Soul Land / Douluo Dalu* (Tang Jia San Shao), *A Record of a Mortal's Journey
> to Immortality* (Wang Yu manhua adaptation), *Battle Through the Heavens*, *Tales of Demons
> and Gods*, *Solo Leveling* (progression-fantasy crossover, manhwa register).

---

## 1. Market contract

**Target demographic:** Seinen/shonen-adjacent readers 16–35, strongest in zh_CN and zh_TW
where cultivation fiction (修仙/武侠) is a native, load-bearing shelf category rather than an
imported curiosity — `config/manga/locale_genre_allocations.yaml` `locales.zh_CN` makes it the
single largest primary-tier genre (18%, ahead of isekai and workplace_drama). Readers arrive
for **legible power progression**: they want to know exactly where a character stands on a
named tier ladder and what it will cost to climb it. The contract is: *I will show you a
precise hierarchy of strength, and every step up that hierarchy will be earned through struggle
I can see, not granted off-page.* Face/status stakes (reputation, sect rank, humiliation and its
reversal) carry as much narrative weight as raw power — this is the genre's signature
divergence from Japanese shonen escalation, where the emotional stakes are more often
relational than hierarchical (`artifacts/research/manga_genre_writing_styles_2026_04_04.md`
§7 "Chinese Web Novel vs. Japanese Manga Dialogue").

---

## 2. Visual rules

| Metric | Cultivation value | Source |
|---|---|---|
| Panels per page | 4–7 (manhua favors larger panels carrying text overlays) | `manga_genre_writing_styles_2026_04_04.md` §7 Metrics |
| Words per page | 60–150 — exposition-heavy; this genre explains its power system constantly | `manga_genre_writing_styles_2026_04_04.md` §7 Metrics |
| Words per volume/season | ~25,000–40,000 | `manga_genre_writing_styles_2026_04_04.md` §7 Metrics |
| Silent panel ratio | 5–15% — lowest of any covered genre; something is almost always being explained | `manga_genre_writing_styles_2026_04_04.md` §7 Metrics; `manga_pacing_by_genre.yaml` `cultivation_martial.silent_panel_ratio_range: [0.15, 0.25]` (pacing contract runs slightly higher than the raw genre-writing baseline — treat 0.15 as the floor) |
| Words per balloon (max) | 18 | `manga_pacing_by_genre.yaml` `cultivation_martial.words_per_balloon_max` |
| Dialogue:narration ratio | 40:60 — heavy narration carrying system/world exposition | `manga_genre_writing_styles_2026_04_04.md` §7 Metrics |
| SFX usage | heavy_kinetic | `manga_pacing_by_genre.yaml` `cultivation_martial.sfx_usage` |
| Background density | medium | `manga_pacing_by_genre.yaml` `cultivation_martial.background_density` |
| Color / rendering | Full-color webtoon-vertical (manhua register) OR monochrome manga register depending on brand format — NOT a Western D&D cover look in either case | `config/manga/genre_prompt_cookbook.yaml` `genres.cultivation` (`color_policy: monochrome_or_manhwa_color`, `anti_blob_rules: forbid western fantasy armor default attractor`); `config/manga/drawing_tradition_per_genre.yaml` `cultivation` (`scope_note`: manhua-flavored full-color, flowing robes, qi-energy as glowing volumetrics) |

**Character design notes:**
- Flowing robes, not Western plate armor — the single most-cited anti-drift rule across both
  the cookbook (`forbid western fantasy armor default attractor`) and the drawing-tradition
  config (manhua jaw/proportions, longer/sharper than manga shonen default).
- Qi/energy effects rendered as stylized glowing volumetrics/particles, never CGI-photoreal —
  `genre_prompt_cookbook.yaml` negative_scaffold explicitly forbids `photorealistic, 3d render,
  cgi, concept art, key visual`.
- Power-tier visual legibility: a reader should be able to guess a character's relative
  cultivation tier from aura color/density and posture alone, before any status-screen text
  confirms it (see §3 exposition discipline below).

---

## 3. Pacing

**Chapter hook archetype:** *The tier assertion.* Open on a status challenge or a rival's
provocation that names the power gap directly ("A mere Foundation Establishment cultivator
dares challenge me?" — `manga_genre_writing_styles_2026_04_04.md` §7 Key Dialogue Patterns #1).
This orients the reader inside the hierarchy before anything else happens.

**Page-turn triggers:** `cultivation_breakthrough`, `rival_challenge`, `sect_revelation`,
`inner_realm_descent` (`manga_pacing_by_genre.yaml` `cultivation_martial.page_turn_triggers`).
A breakthrough is the genre's equivalent of a shonen power-up spread — reserve it, don't spend
it casually.

**Chapter ending archetype:** Either a breakthrough completed (new tier named, cost paid) or a
status reversal set up (a face-slap payoff deferred to next chapter). Cultivation rarely ends a
chapter on pure mystery — it ends on a hierarchy shift, stated or imminent.

**Exposition discipline (the genre's core craft risk):** the "exposition avalanche" — three
pages of tier taxonomy before anything happens — is the #1 named failure mode in the source
research (`manga_genre_writing_styles_2026_04_04.md` §7 Common Writing Failures #1). Weave
tier/technique explanation into failed attempts and character struggle rather than sect-elder
lecture; teach the reader the power system the way the protagonist learns it, through
consequence, not through a recited table.

**Per-volume emotional shape:** Status quo established (protagonist ranked low, humiliated or
underestimated) → training/struggle montage → breakthrough attempted and failed at least once
→ breakthrough achieved at real cost (health, relationship, reputation risked or spent) → status
reversed, at least partially, closing on the next rung of the ladder already visible above them.

---

## 4. Dialogue

**Register — Chinese web-novel mode (primary for zh_CN/zh_TW):** formal, verbose, philosophically
oriented; characters speak in proverbs and four-character idioms; power-level assertions are
explicit and frequent (`manga_genre_writing_styles_2026_04_04.md` §7 "Chinese Web Novel vs.
Japanese Manga Dialogue"). This is a deliberate register choice, not a translation artifact —
do not flatten it toward shorter, more emotionally-driven Japanese-manga cadence when the brand
targets zh_CN/zh_TW natively.

**Master-disciple conversation patterns** (source: `manga_genre_writing_styles_2026_04_04.md`
§7 Master-Disciple Conversation Patterns):
1. **The cryptic lesson** — the master says something that sounds like nonsense; understanding
   arrives through later experience, never through direct explanation in the same scene.
2. **The test disguised as conversation** — a seemingly philosophical question whose answer
   reveals whether the disciple is ready for the next teaching.
3. **Reluctant mentorship** — masters who resist teaching; earning guidance IS the arc, not a
   precondition to it.

**Key dialogue patterns to rotate** (source: same §7):
1. The Tier Assertion — direct naming of the power gap.
2. The Cryptic Master — Daoist-flavored riddle-teaching ("When the mountain stream meets the
   sea, does it lose itself or find its true nature?").
3. The Breakthrough Narration — internal monologue during cultivation itself: qi flow, barriers
   shattering, consciousness expanding.
4. The Face-Slap Exchange — arrogant rival insults protagonist → hidden strength revealed →
   observers gasp. Genre-essential; the failure mode is using it unvaried (see §6).
5. The Auction/Treasure Dialogue — bidding or identifying rare materials; world-building
   delivered through commerce rather than lecture.

**Status-screen exposition (Solo Leveling model):** game-like status overlays are an accepted
convention in manhwa-adjacent cultivation, but the same source research flags them as
"over-explanatory" when used as the sole exposition method — mix status-screen delivery with
in-scene struggle; never let a cutaway slide replace character reaction.

---

## 5. Character

**Protagonist archetype:** The Underestimated Climber — introduced at a disadvantaged tier,
often humiliated or dismissed by a rival or sect early on. Progress is legible and earned:
"moving from Rank D to Rank S IS the story" (`manga_genre_writing_styles_2026_04_04.md` §7
"What Makes Cultivation/Xianxia FEEL Different"). Face/reputation stakes matter as much as raw
power — a protagonist who wins a fight but is not seen to win it has not fully resolved the
beat.

**Supporting cast:** Master/mentor (reluctant, cryptic — see §4), rival(s) at adjacent or
higher tier whose status challenges structure page-turn beats, sect elders/authority figures who
carry hierarchy exposition without becoming lecture-delivery devices. Cast should make visible,
at a glance, who currently outranks whom.

**Antagonist grammar:** The Arrogant Young Master is genre-essential (the "face-slap" setup) —
vary the specific humiliation and the specific reveal each time it recurs so it does not read as
formulaic (named directly as a failure mode below). Higher-tier antagonists should embody the
"hierarchy is everything" rule: their authority is visible in bearing and aura, not only stated.

**Power taxonomy discipline:** every ability needs a name, a tier, a history, and a counter
(`manga_genre_writing_styles_2026_04_04.md` §7). Do not introduce a power without at least
implying where it sits on the ladder relative to what the reader already knows.

---

## 6. Failure modes

(Source: `manga_genre_writing_styles_2026_04_04.md` §7 Common Writing Failures, expanded with
visual-drift rules from `config/manga/genre_prompt_cookbook.yaml` and
`config/manga/drawing_tradition_per_genre.yaml`.)

1. **Exposition avalanche.** Three pages of tier taxonomy before anything happens. Weave it into
   struggle instead.
2. **"Courting death" cliché without variation.** The arrogant-young-master encounter is genre
   essential but becomes formulaic if the humiliation/reveal shape never changes.
3. **Power fantasy without cost.** If a breakthrough costs nothing (health, relationships,
   sanity, reputation), progress feels weightless.
4. **Generic JRPG worlds.** Chinese cultivation fiction carries rich, specific mythology
   (Daoist cosmology, named realms) — defaulting to generic Western fantasy setting wastes the
   genre's core strength.
5. **Status-screen crutch.** Delivering all world/power information through cutaway UI slides
   instead of character reaction and struggle.
6. **Ignoring character in favor of system.** Stat blocks and tier names do not substitute for
   personality; a named tier is not a personality trait.
7. **Western fantasy armor default.** Visual drift into Western plate-armor/D&D-cover imagery
   instead of flowing robes and manhua-register qi effects — explicitly forbidden in the
   cookbook's `anti_blob_rules`.
8. **Monochrome-only assumption for manhua-format brands.** The drawing-tradition config marks
   cultivation as full-color-throughout for manhua-flavored series — treating it as standard
   monochrome manga screentone is a registered forbidden-drift pattern for that format lane.

---

## 7. 48-volume shape

Cultivation's structure is inherently tier-based; the 48-volume arc should track a small number
of major realm transitions rather than many short arcs.

- **Vols 1–8 — Foundation Establishment:** Protagonist introduced at a disadvantaged or
  dismissed tier. First face-slap humiliation and reversal. Establish the sect/hierarchy, the
  master, and the taxonomy of realms the story will climb. Theme: what does it cost to be
  underestimated?
- **Vols 9–18 — Core Formation:** First real breakthrough failure and the struggle that follows
  it. Rival relationships solidify (some become allies, one becomes the recurring antagonist).
  Reader now fluent in the tier system through demonstrated consequence, not lecture. Theme:
  what is the price of the first real breakthrough?
- **Vols 19–30 — Nascent Soul:** Scale escalates from local (sect, village) to regional
  (kingdom, faction war). Face/reputation stakes shift from personal humiliation to
  responsibility for others. A named mentor figure is lost, tested, or revealed as more complex
  than the cryptic-lesson archetype implied. Theme: what do I owe the people who now rank below
  me?
- **Vols 31–42 — Immortal Ascension approach:** Scale becomes cosmic — village fights give way to
  battles with realm-level or god-tier forces (`manga_genre_writing_styles_2026_04_04.md` §7
  "Scale escalates astronomically"). The protagonist's Dao/philosophy (not just their power)
  becomes the story's engine. Theme: what kind of strength is worth having?
- **Vols 43–48 — Ascension / the Long Reckoning:** Final tier breakthrough attempted at maximum
  cost. Rivals and mentors resolve their arcs relative to the protagonist's climb. Closes on the
  protagonist at the top of a legible hierarchy, but the final beat should name what the climb
  cost, not just what it earned — echoing dark_fantasy's "carried weight" discipline so the
  ending is not a pure power-fantasy payoff.

Each realm transition should coincide with a visible aura/visual-register change so the
hierarchy shift reads at a glance, per the genre's core visual-legibility contract (§2).

---

## 8. Panel scaffolding

Per-panel fields (8):

1. `framing` — ELS / LS / MS / MCU / CU / insert; wide/establishing preferred for realm-scale
   reveals, MCU/CU for face-slap reaction beats
2. `beat_role` — one of {tier_assertion, breakthrough_attempt, breakthrough_failure,
   breakthrough_success, face_slap_setup, face_slap_payoff, cryptic_lesson, sect_revelation,
   auction_or_treasure, inner_realm_descent}
3. `dialogue` — ≤18 words per balloon (`manga_pacing_by_genre.yaml`
   `cultivation_martial.words_per_balloon_max`); proverb/idiom register permitted and encouraged
   for zh_CN/zh_TW native delivery
4. `power_tier_named` — string or null; the explicit tier name in play this panel, when the beat
   requires hierarchy legibility (breakthrough/assertion/reveal beats should rarely be null)
5. `aura_visual` — qi/energy rendering descriptor (color, density, volumetric shape) used to keep
   tier progression visually legible without relying solely on text
6. `sfx` — heavy_kinetic per pacing contract; scale intensity to the beat (whisper-level for
   cryptic_lesson, panel-breaking for breakthrough_success)
7. `reaction_shot` — boolean; high frequency expected (`manga_pacing_by_genre.yaml`
   `cultivation_martial.reaction_shot_frequency: high`) — face-slap and breakthrough beats
   require an onlooker reaction panel
8. `cost_marker` — string or null; names what a breakthrough/victory cost (health, standing,
   relationship) — should not stay null across an entire breakthrough sequence (anti power-fantasy-
   without-cost discipline, §6)

**Generator constraint:** silent panel ratio kept at 15–25% (`manga_pacing_by_genre.yaml`
range) — this genre talks more than almost any other covered lane; do not let assembly logic
push it toward a generic 30%+ silence floor tuned for iyashikei/dark_fantasy lanes.

---

## 9. Locale weighting

| Locale | Signal | Rationale |
|---|---|---|
| `zh_CN` | **Primary** | Largest single primary-tier genre share in the locale allocation (18%) — native, load-bearing shelf category, not an imported curiosity (`locale_genre_allocations.yaml` `locales.zh_CN`). |
| `zh_TW` | **Secondary** | 8% secondary-tier share; cultivation coexists with TW's stronger literary/horror primary tiers (`locale_genre_allocations.yaml` `locales.zh_TW`). |
| `ja_JP` | Not in the current en_US/CJK allocation's cultivation row for ja_JP — mecha/isekai/dark_fantasy carry the adjacent progression-fantasy space there instead; do not assume 1:1 crossover demand. |
| `en_US` / `ko_KR` | Progression-fantasy demand exists via the isekai/Solo-Leveling-adjacent crossover audience, but is carried under the `isekai` genre_id in the allocation file, not `cultivation_martial` — treat as a cross-genre reference point (§1), not a direct allocation signal. |
| `fr_FR` | Manhua/webtoon distribution channel exists per France's manga-market share, but cultivation is not a named allocation row for `fr_FR` — no direct signal yet. |

---

*Sources: `artifacts/research/manga_genre_writing_styles_2026_04_04.md` §7 "Cultivation / Xianxia"
(metrics, exposition/dialogue patterns, failure modes — lines 399–457);
`config/manga/manga_pacing_by_genre.yaml` `cultivation_martial` pacing contract;
`config/manga/genre_prompt_cookbook.yaml` `genres.cultivation` (visual/anti-drift rules);
`config/manga/drawing_tradition_per_genre.yaml` `cultivation` (manhua register, exemplars: Tang
Jia San Shao / Soul Land, Wang Yu / A Record of a Mortal's Journey to Immortality);
`config/manga/locale_genre_allocations.yaml` `locales.zh_CN` / `locales.zh_TW` (allocation
shares); `config/manga/manga_taxonomy.yaml` `cultivation` genre family.*
