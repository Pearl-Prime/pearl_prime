# Food Manga — Craft Bible

> Canonical genre lane per `config/manga/canonical_genre_list.yaml` (`id: food`, label "Food", `parent_family: null`, `must_include: yes`). Taxonomy-only row (`source_pacing: no`) — pacing is proxied to `healing` (`pacing_proxy: healing`, comment: "alias map: food → healing"); see §3 for the adaptation and the flagged gap.
> Quality-gate hint per `config/manga/main_character_interaction_grammar.yaml`: `food: {quality_gate_checks: [family_customer_or_craft_interaction]}` — every chapter must clear a bar of genuine family, customer, or craft-technique interaction; food cannot be plot wallpaper.
> Adjacent-but-distinct lane: `docs/research/manga_craft/iyashikei_minimalism.md` (healing) supplies this genre's quiet sensory-close-up register (§2, §3); this genre departs from it by adding a craft/technique-demonstration engine and a much higher reaction-shot frequency (see §1, §3).

Touchstones: *Food Wars! / Shokugeki no Sōma* (Yuto Tsukuda / Shun Saeki), *Oishinbo* (Tetsu Kariya / Akira Hanasaki), *What Did You Eat Yesterday?* (Fumi Yoshinaga), *Sweetness & Lightning / Amaama to Inazuma* (Gido Amagakure), *Restaurant to Another World / Isekai Shokudō* (Junpei Inuzuka / Katsumi Enami).

---

## 1. Market contract

**Target demographic:** Wide — shonen readers for competitive-cooking registers (Food Wars), josei/seinen adults for domestic and journalistic registers (Oishinbo, What Did You Eat Yesterday?), and family/all-ages readers for gentle-parenting-through-cooking registers (Sweetness & Lightning). Food is one of the few genre lanes in this catalog that spans multiple demographics natively because the vessel — cooking and eating — is universal in a way most genre premises aren't.

**Emotional promise:** *Watching someone care about a craft, and watching food genuinely change how a room of people feel.* The contract has two layers that every touchstone braids together: (1) craft respect — technique is shown accurately enough that a reader who cooks recognizes it, and technique mastery is earned through repetition and failure, not talent alone; (2) relational payoff — the dish is never the end point, the *table* is; a meal's real subject is always the people eating it (a grieving father and daughter in Sweetness & Lightning, two men building a life together over dinner in What Did You Eat Yesterday?, an isekai tavern's regulars in Restaurant to Another World). Readers will accept: competitive stakes (a cook-off, a critical review, a restaurant's survival), technical digression (an extended explanation of knife angle or stock reduction), sensory excess (the "tasting reaction" spectacle). They will reject: a dish resolving a relationship problem by itself with no character work behind it, and technique presented as trivia disconnected from a character's hands actually doing it.

**Distinction from iyashikei (its pacing proxy — do not treat as interchangeable):** iyashikei's sensory close-ups (a cup of tea, a bowl steaming) are used for atmosphere and restraint; food's sensory close-ups are used to *demonstrate craft* and to *trigger reaction* — the same close-up shot type serves an opposite narrative purpose. A food manga panel of steam rising off a bowl is rarely there to be contemplated quietly; it's the setup for a bite, a reaction, and often a flashback or explanation of why the dish works. Food keeps iyashikei's quietness only in its slower, most domestic registers (Oishinbo's investigative calm, What Did You Eat Yesterday?'s evening-kitchen wind-down); it abandons that quietness entirely in its competitive/tasting-spectacle registers (Food Wars).

---

## 2. Visual grammar

- **Panel count per chapter:** 45–70 panels over 18–22 pages; avg 2.5–4 panels/page — drops sharply during technique or tasting sequences, where a single panel (or a full-page dish reveal) can carry an entire beat.
- **Words per page:** 30–70 in domestic/investigative registers (Oishinbo, What Did You Eat Yesterday?); spikes to 90–130 during technique-explanation and judging sequences (Food Wars' judge monologues, Oishinbo's culinary-history digressions) — see §3 for the full range.
- **Silent-panel ratio:** 20–40% — close to iyashikei's floor but not its ceiling; a food chapter routinely has long wordless technique sequences (chopping, plating, the moment before the first bite) but rarely stays silent for long once a dish is served, because the tasting reaction demands dialogue or at minimum an SFX-and-expression beat.
- **Black-fill ratio:** 0.15–0.30 — kitchens are lit environments (steam, flame, steel) that create natural high-contrast opportunities; darker than iyashikei's airy 0.10–0.20.
- **Screentone density:** Medium, purpose-driven — heavy gradient/dot-screen on steam, smoke, and glaze sheen; naturalistic tone on skin and produce; near-zero tone on the "flavor burst" reaction panel, which is often line-only or backed with a solid abstract color/pattern field (Food Wars' signature move — the eater's clothes dissolving into a symbolic sensory backdrop).
- **Spread frequency:** Higher than iyashikei's — 1 per chapter or every other chapter, almost always the **dish reveal**: a full-page or two-page splash of the finished plate, shot from an appetite-forward angle. This is the genre's visual centerpiece and functions the way a fight-splash-page functions in shonen battle manga — a page-turn reward, not a landscape meditation.
- **Reaction-shot frequency:** High — this is the genre's defining visual rhythm. A tasting beat is built from 3–6 consecutive reaction panels: bite → pause → eyes widen/close → a flavor-description beat (verbal or visual-symbolic) → a settling reaction. Food Wars pushes this to spectacle (clothes-dissolving, imagined landscapes); Oishinbo and What Did You Eat Yesterday? keep it grounded (a held breath, a small satisfied exhale, a quiet "oh").
- **Line weight profile:** Medium-detailed, with disproportionately higher rendering density on food itself than on characters or backgrounds — glossy highlights on sauce, individual grain texture on rice, visible steam lines. The dish must out-render the room it's served in.
- **Craft/technique-demonstration panels:** A recurring, near-mandatory panel type absent from iyashikei entirely: a close, often diagrammatic insert showing hands mid-technique (knife angle, whisk motion, temperature check) sometimes with a callout label or measurement — Food Wars and Oishinbo both use this; it is the genre's equivalent of a training-montage panel in sports manga.

---

## 3. Pacing

**Flagged gap — no direct pacing-table entry.** `config/manga/manga_pacing_by_genre.yaml` has no `food:` key. `config/manga/canonical_genre_list.yaml` sets `pacing_proxy: healing` (annotated "alias map: food → healing"), i.e. the numbers below are adapted from the `healing:` entry (`manga_pacing_by_genre.yaml` ~line 81) rather than measured directly against a food-manga reference corpus. **Recommendation: a follow-up should add a direct `food:` entry to `manga_pacing_by_genre.yaml`**, built against an actual reference corpus (Food Wars!, Oishinbo, What Did You Eat Yesterday?, Sweetness & Lightning, Restaurant to Another World) rather than proxied — and note that the corpus itself spans a wide register (shonen-competitive to josei-domestic), so a single food entry may eventually need sub-registers the way `healing` does not.

**Adaptation rationale.** Per `config/manga/main_character_interaction_grammar.yaml`'s `food: {quality_gate_checks: [family_customer_or_craft_interaction]}` gate, this lane keeps healing's close, quiet, sensory attentiveness (steam, texture, the held moment before a bite mirrors iyashikei's held moment before a landscape) but is structurally required to demonstrate *craft* and *interaction* — a solo, wordless sensory register alone would not clear the gate. That requirement pushes the healing-proxy numbers in a specific, narrower direction than slice_of_life's broader adaptation (see `slice_of_life.md` §3 for contrast):

| Field | `healing` proxy value | `food` adapted value | Direction & reason |
|---|---|---|---|
| `words_per_page_range` | [20, 50] | **[30, 65]** | Up moderately — technique explanation and judging/tasting dialogue add words that pure atmosphere doesn't need, but domestic registers (Oishinbo, WDYEY) keep this closer to healing's range than slice_of_life's much higher one. |
| `words_per_balloon_max` | 20 | **26** | Up — technique explanation and flavor-description lines run longer than iyashikei's fragment-register dialogue; a judge's tasting monologue or a chef's technique note needs more room. |
| `silent_panel_ratio_range` | [0.35, 0.60] | **[0.25, 0.45]** | Down modestly — technique sequences preserve real silence (comparable to healing), but the tasting-reaction beat (see §2) is rarely wordless for long, pulling the average down from healing's floor. |
| `reaction_shot_frequency` | low | **high** | Up sharply — the tasting-reaction sequence (§2) is this genre's core rhythm device and has no equivalent in iyashikei's environmental-reaction register. |
| `spread_frequency` | periodic | **periodic-to-frequent** | Up — the dish-reveal spread (§2) recurs more often than iyashikei's landscape spread, functioning as a structural page-turn reward rather than an occasional meditative beat. |
| `narration_tolerance` | moderate | **moderate-to-generous** | Up in technique/investigative registers (Oishinbo's culinary-history captions) — held at moderate in domestic registers (WDYEY, Sweetness & Lightning). |
| `sfx_usage` | atmospheric | **food-specific (see vocabulary below)** | Redirected — sizzle, bubble, chop, and crunch sounds replace wind/water/insect atmosphere; see the dedicated SFX list below. |
| `background_density` | rich_plus_quiet | **rich_plus_craft-detailed** | Redirected — kitchen and market backgrounds carry the same loving specificity as iyashikei's landscapes, but rendered toward equipment, ingredients, and technique rather than nature. |

**Food-specific SFX vocabulary (required — no equivalent in the healing proxy):**
- **Heat/cooking:** ジュージュー (juu-juu, sizzle), パチパチ (pachi-pachi, crackle/pop of frying), ぐつぐつ (gutsu-gutsu, simmer/bubble), コトコト (koto-koto, gentle simmer/braise), ボコボコ (boko-boko, rolling boil).
- **Cutting/prep:** トントン (ton-ton, rhythmic knife-on-board chopping), シャキシャキ (shaki-shaki, crisp vegetable texture/bite), ザクザク (zaku-zaku, coarse chopping or crunchy bite), スパッ (supa, a single clean decisive cut).
- **Texture/eating:** サクサク (saku-saku, light crispness — tempura, pastry), もちもち (mochi-mochi, chewy-elastic texture), とろーり (toro-ri, a rich sauce or yolk slowly spreading/melting), ふわふわ (fuwa-fuwa, fluffy/airy — soufflé, fresh bread), パリパリ (pari-pari, crackly-crisp — skin, crust).
- **Steam/aroma (English convention for localized editions):** wisping steam-line SFX are typically rendered visually rather than lettered; when lettered, "fwoo" / soft sibilant sounds accompany an aroma-wafting panel.
- **English-market convention:** localized editions generally keep the most iconic Japanese SFX untranslated with a small gloss (as *Food Wars!* and *Oishinbo* English editions both do for texture words like *saku-saku*) rather than force an English onomatopoeia, since English lacks equivalents with the same specificity.

- **Chapter length:** 18–22 pages — shorter than iyashikei's 20–28, closer to a tight single-dish or single-technique unit per chapter.
- **Chapter hook family:** *Ingredient or challenge first.* Open on a specific ingredient (a rare fish, a family's aging recipe card, a customer's request), a technical problem to solve, or a competitive prompt (a themed cook-off) — not a mood cue as in iyashikei. The hook is a concrete culinary problem the chapter will solve.
- **Chapter ending convention:** *The verdict, softened.* A chapter typically closes on the eating — a diner's reaction, a judge's verdict, a family member's first bite — followed by one beat of quiet aftermath (dishes cleared, a thank-you, a character's private reflection) that keeps the ending from being purely transactional. Competitive registers (Food Wars) can end on a cliffhanger verdict; domestic registers (WDYEY, Sweetness & Lightning) almost never do.
- **Scene-to-scene transitions:** Ingredient or object bridges (a spice jar in scene A appears on the counter in scene B), plus hard cuts from market/shopping to kitchen to table — a three-beat structure (source → craft → table) recurs across nearly every chapter regardless of register.
- **Per-volume arc shape:** Volume = a sequence of dishes/techniques building toward either a competitive event (Food Wars' tournament blocks), a seasonal/relational throughline (Sweetness & Lightning's father-daughter year, WDYEY's household year), or an investigative throughline (Oishinbo's "Ultimate Menu" project). Unlike iyashikei, food tolerates real competitive stakes within a volume (a rival, a judged contest) — but per the gate in §1, the stakes must resolve through relational or craft growth, not through the food alone "winning."

---

## 4. Dialogue

- **Register:** Splits cleanly by register-family. Competitive/shonen (Food Wars): heightened, declarative, technique-as-battle-cry ("This is a dish that captures the essence of—"). Journalistic/investigative (Oishinbo): expository, historically curious, frequently argumentative between two food philosophies. Domestic/josei (WDYEY, Sweetness & Lightning): naturalistic, low-key, often quietly funny, with cooking narrated almost as internal monologue while hands work.
- **Narration tolerance:** Moderate-to-generous, higher than iyashikei — technique explanation and ingredient background are load-bearing narrative content in this genre, not indulgence, and readers expect some of it.
- **Dialogue-to-narration ratio:** ~60:40 in domestic/investigative registers (closer to josei workplace than iyashikei); ~75:25 in competitive registers where the tasting reaction itself often replaces narration with pure sensory dialogue ("It's—!").
- **Interior monologue:** In domestic registers, cooking is frequently paired with private reflection — the physical repetition of a technique (chopping, stirring) becomes a vehicle for a character to think through something unrelated to the dish, mirrored directly in What Did You Eat Yesterday?'s signature move of a legal case or relationship worry unspooling in the narrator's head while dinner cooks.
- **The technique-explanation beat:** A required, near-universal dialogue unit — a character (mentor, rival, or the protagonist themself) explains *why* a technique works, not just that it does. This must be technically accurate enough to read as researched, not hand-waved ("I seared it hot" is thin; "I got the pan to just past smoking point so the Maillard reaction happens before the fat renders out" is the genre's actual register, scaled to the target locale's assumed food literacy).
- **The tasting-reaction line:** A short, often single-word-to-single-sentence utterance at the peak of a tasting sequence ("...Oh." / "This is—") that the surrounding reaction panels (§2) do the heavy lifting for; the line should never over-explain what the art has already shown.
- **Tell-don't-show tolerance:** Low for flavor description specifically — a character stating "it was delicious" with no sensory or reaction detail is the genre's most immediate tell (see §6.1); low-to-moderate for character emotion generally, similar to workplace/josei registers.

---

## 5. Character

- **Protagonist archetype:** A craftsperson at some stage of technique mastery — ranges from prodigy-in-training (Food Wars' Soma) to established professional finding new purpose (Sweetness & Lightning's widowed father learning to cook for his daughter) to an omniscient culinary-philosopher pair (Oishinbo's Yamaoka and his rival-father) to a quietly domestic partner (WDYEY's Shiro). The unifying trait: competence is earned on-panel through visible repetition and failure, never asserted by reputation alone.
- **The mentor/rival figure:** Frequently doubles as antagonist-adjacent without being a villain — a stricter, more traditional, or more commercially successful cook whose approach the protagonist must reckon with (Food Wars' Erina, Oishinbo's father Kaibara). Per the genre's craft-respect contract (§1), even an antagonistic rival's technique must be shown as genuinely skilled, not strawmanned.
- **The eater/recipient figure:** As important as the cook — the person the dish is *for* (Sweetness & Lightning's daughter Tsumugi, WDYEY's partner Kenji, Restaurant to Another World's tavern regulars, Oishinbo's readers-as-diners via the newspaper framing device). This figure's reaction is the payoff the entire chapter has been building toward; a food manga without a well-drawn eater-figure has only half its cast.
- **Cast density:** Variable by register — a tight 2–4 in domestic registers (a household or couple), a wide rotating cast in competitive/restaurant registers (classmates, judges, customers) that can run 8+ across a volume, and an ensemble-of-regulars in tavern/restaurant-vessel stories (Restaurant to Another World's isekai patron rotation).
- **Emotional arc per volume:** Ingredient/challenge introduced → technique struggle and failure → mentorship or research → the dish succeeds → the eater's reaction resolves the volume's relational question (not just the culinary one). The craft plot and the relational plot must resolve together, never the craft plot alone (see §6.2).
- **Family/customer/craft interaction (the quality-gate requirement):** Every chapter must clear at least one of: a family interaction (cooking for or with kin), a customer interaction (serving, judging, or being served), or a craft interaction (learning or teaching a technique with another character present) — a chapter that is only a character cooking alone with no one to cook *for* or *with* fails this lane's core gate.

---

## 6. Failure modes

1. **Recipe-as-plot-device with no character stakes.** The cardinal sin of this lane. A dish is described or shown in technical detail, but nothing in a character's relationships, self-understanding, or circumstances is actually at stake in whether it succeeds — the food becomes a checklist item instead of the vehicle it's supposed to be. If the chapter would read the same with any interchangeable dish substituted in, the character stakes were never real.
2. **Craft resolving relationship problems by itself.** A dish "fixing" an estranged relationship or a customer's bad day with no character work behind it — the genre's contract (§1) requires the dish to be a catalyst that the characters still have to meet, not a magic solution.
3. **Technique hand-waved or inaccurate.** "It just tasted better because he tried harder" instead of a specific, researchable technical reason — breaks the craft-respect contract and reads as lazy to any reader who cooks.
4. **Flavor description with no sensory specificity.** "It was delicious" without texture, temperature, aroma, or a grounded comparison is the equivalent of iyashikei's emotional-labeling failure mode (§6 of `iyashikei_minimalism.md`) — the genre's entire sensory contract is broken by shortcutting the description.
5. **Reaction spectacle without an eater who matters.** Leaning on Food Wars-style visual reaction spectacle (clothes dissolving, symbolic backdrops) for a background or one-off character the reader has no investment in — the spectacle only works when it's *earned* by a relationship the reader cares about (see §5's eater-figure requirement).
6. **Competition escalating past the genre's tolerance.** Turning a cook-off into genuine cruelty, sabotage, or malice moves the story into a different, harsher register than food manga's competitive registers actually occupy — even Food Wars' fiercest rivals respect each other's craft.
7. **No family/customer/craft interaction (quality-gate failure).** A chapter of solo cooking with no one to cook for or learn from/teach fails the `family_customer_or_craft_interaction` gate outright (§5).
8. **Borrowing iyashikei's stillness without its payoff engine.** Importing iyashikei's slow sensory pacing into a food chapter but never landing a tasting-reaction beat leaves the chapter feeling like an unfinished iyashikei chapter rather than a food chapter with its own distinct payoff structure (see §1, §3).
9. **Food as scenery for an unrelated plot.** A restaurant or kitchen setting used only as backdrop for a story that isn't actually about the food or craft (a romance or workplace drama that happens to be set in a café) — food should be the narrative engine, not the wallpaper, per this genre's `must_include` status as its own lane.
10. **Ingredient/technique fetishism without a table.** Extended technical digression (Oishinbo-style) with no eventual scene of the food actually being eaten and reacted to by someone who matters — the craft demonstration must resolve at a table, not stop at the pan.

---

## 7. 48-volume shape

Food's 48-volume shape borrows healing's willingness to be episodic (§7 of `iyashikei_minimalism.md`) but organizes around **craft mastery stages and a widening table**, not a seasonal atmosphere:

- **12 × 4-volume "menus"** — each 4-volume block centers one culinary theme, technique family, or seasonal ingredient set (knife work and stocks; fermentation and preservation; a regional cuisine; a signature dish's many variations), building toward one dish-reveal centerpiece per block, OR
- **4 × 12-volume "career stages"** (apprentice → line cook → sous/second → head of the table), mirroring `shonen_encouragement.md`'s practice-as-narrative-engine model but keeping food's relational-payoff requirement primary at every stage — each stage's climax is a table reaction, not a title or rank, OR
- **48 standalone-ish volumes linked by one vessel** (a single restaurant, café, or tavern — Restaurant to Another World's model), where each volume is closer to an anthology of dishes-and-diners than a serialized arc, and continuity lives in the vessel and its regulars rather than in escalating plot.

Long-arc material should track **who the protagonist cooks for**, widening across the series the way slice of life's ensemble widens (see `slice_of_life.md` §7): early volumes often center a single relationship (a parent, a mentor, one struggling regular), middle volumes widen to a professional circle (coworkers, competitors, a full dining room), and late volumes can widen further to a community or legacy register (the protagonist now teaching, feeding a whole neighborhood, or preserving a family recipe for the next generation — Oishinbo's decades-spanning "Ultimate Menu" project is the reference model for this late-series register). Avoid: a series-wide villain who wants to destroy the restaurant/craft (a real risk in competitive registers — keep antagonism at the level of rival craftspeople, not saboteurs), and a 48-volume arc that never lets a volume simply be about one good meal with nothing else at stake.

---

## 8. Panel scaffolding

Per-panel fields (9):

1. `framing` — ELS / LS / MS / MCU / CU / macro-insert (ingredient/technique close-up) / dish-reveal-spread / reaction-row
2. `beat_role` — one of {ingredient_intro, technique_demonstration, craft_struggle, plating, dish_reveal, tasting_reaction, verdict, table_aftermath, family_or_customer_interaction}
3. `dialogue` — ≤26 words; technique-explanation lines may run to the max, tasting-reaction lines are typically ≤6 words or a fragment
4. `caption` — ≤20 words; ingredient/technique narration or investigative-register exposition; null on most tasting/reaction panels, where the art and dialogue carry the beat
5. `sfx` — food-specific vocabulary only (see §3's dedicated list — sizzle/simmer/chop/crisp/chew registers), or null
6. `dish_state` — `raw` / `in_progress` / `plated` / `being_eaten` / `finished` — tracks the source→craft→table structure (§3) across a chapter's panels
7. `reaction_intensity` — integer 0–3 (0=neutral, 1=noted, 2=visible pleasure/surprise, 3=full sensory-spectacle reaction); required non-null on every panel where `dish_state=being_eaten`
8. `technique_accuracy_flag` — boolean; true requires the accompanying dialogue/caption to name a real, verifiable technique or reason (enforcement flag against §6.3's hand-waving failure mode)
9. `silence_flag` — boolean; true forbids dialogue and caption but permits food-specific sfx; must appear on 25–45% of panels (see §3), concentrated in technique-demonstration beats rather than evenly distributed

Constraint hint for the generator: at least one panel per chapter must carry `beat_role=dish_reveal` with `framing=dish-reveal-spread`; `reaction_intensity=3` must never appear without a preceding `technique_demonstration` or `craft_struggle` beat earlier in the same chapter (enforces the craft-earns-payoff contract in §1/§6.1).

---

## 9. Locale weighting

| Locale | Primary register | Platform | Notes |
|---|---|---|---|
| **ja_JP** | Native home lane, spanning shonen-competitive (Weekly Shonen Jump), seinen-investigative (Big Comic Spirits), and josei-domestic (Kurage Bunch) magazines simultaneously — the widest single-locale register spread of any lane in this catalog. | LINE Manga, ComicWalker, Shonen Jump+ | Confirm which register (competitive / investigative / domestic) a given brand targets before drafting — the three pull from different reference touchstones (§1) and different pacing sub-ranges (§3). |
| **en_US** | Strong crossover appeal; Food Wars! and What Did You Eat Yesterday? both have significant English fanbases via anime/manga simultaneously. Food content performs well cross-platform (recipe/cooking-adjacent audiences beyond core manga readers). | Amazon manga digest, VIZ, WEBTOON English | Technique-explanation beats (§4) should calibrate to US home-cook literacy — avoid assuming professional kitchen vocabulary without a beat that teaches it in-panel. |
| **zh_TW** | Strong reception — food culture is a major shared cultural touchstone; domestic/family register (Oishinbo, WDYEY-adjacent) resonates particularly well. | LINE Comics TW | Regional/family-recipe throughlines (§7) can lean into locally resonant cuisine registers without losing the craft-bible's structural bones. |
| **zh_CN** | Low-risk lane — food and craft content is broadly welcomed with minimal sensitivity review overhead; family-interaction register (§5) aligns well with locally preferred wholesome-family content. | Bilibili Comics, Kuaikan | AI-disclosure and standard content-review requirements apply per catalog default; no genre-specific gray-zone flag. |
| **ko_KR** | Strong webtoon fit — food/cooking webtoons are an established Naver/Kakao category; vertical format adapts naturally to the dish-reveal spread (§2/§8) as a full-screen scroll moment. | Naver Webtoon, Kakao | Episode-cliffhanger convention (webtoon default) fits this genre more naturally than it does slice_of_life — a verdict/judging cliffhanger (§3) is a legitimate, genre-appropriate hook here. |

---

*Sources: `docs/research/manga_craft/iyashikei_minimalism.md` (pacing-proxy source genre; §2, §3, §6 direct comparison basis, per `canonical_genre_list.yaml`'s `pacing_proxy: healing` alias map); `docs/research/manga_craft/shonen_encouragement.md` (referenced for the career-stage 48-volume shape model in §7, craft-as-narrative-engine parallel); `docs/research/manga_craft/index.md` (schema confirmation); `config/manga/manga_pacing_by_genre.yaml` `healing:` entry (proxy pacing data, adapted in §3); `config/manga/canonical_genre_list.yaml` `food` row (`pacing_proxy: healing`, taxonomy-only, "alias map: food → healing"); `config/manga/main_character_interaction_grammar.yaml` `food: {quality_gate_checks: [family_customer_or_craft_interaction]}`; `docs/agent_prompt_packs/20260723_manga_48ep_3catalog_series/arc_plans_all_genres/procedural_medicine_family_food_social_historical.md` (worked food brand example, `heart_balance_shojo`, skimmed for context per assignment, and its explicit confirmation that no food craft bible existed prior to this file); WebSearch on *Food Wars! / Shokugeki no Sōma* (Yuto Tsukuda / Shun Saeki, Shueisha/VIZ) and general food-manga touchstones; established knowledge of *Oishinbo* (Tetsu Kariya / Akira Hanasaki, Shogakukan), *What Did You Eat Yesterday?* (Fumi Yoshinaga, Kodansha), *Sweetness & Lightning* (Gido Amagakure, Kodansha), and *Restaurant to Another World* (Junpei Inuzuka / Katsumi Enami, Hifumi Shobo/J-Novel Club) — series structure, technique-demonstration conventions, and Japanese food-manga SFX vocabulary.*
