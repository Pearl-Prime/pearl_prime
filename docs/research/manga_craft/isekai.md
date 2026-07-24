# Isekai — Craft Bible

> **Genre slug:** `isekai` (taxonomy family `fantasy_adventure` per
> `config/manga/canonical_genre_list.yaml` line 144 `aliases_inbound: [fantasy, isekai,
> magical_girl]`; pacing key `fantasy` per `manga_pacing_by_genre.yaml` alias line 500).
> Expanded 2026-07-24 from the M3 Wave-1 stub (manga process uplift Lane 05); the stub's reader
> promise, teacher-mode vessel, and anti-patterns are absorbed into §1, §5, and §6 below.
> Touchstones: *Re:Zero* (Nagatsuki Tappei), *Mushoku Tensei* (Rifujin na Magonote), *Overlord*
> (Maruyama Kugane), *The Rising of the Shield Hero* (early arcs — Aneko Yusagi), *Frieren*
> (adjacent — time and grief inside a fantasy shell), *Ascendance of a Bookworm* (craft-isekai
> pole).

## 1. Market Contract

Core readership is 16–34, male-skewing at the power-fantasy pole and increasingly mixed at the
slow-life/craft pole (*Bookworm*, farming and innkeeper isekai) — the pole this catalog builds
on. The surface promise is transportation: wake in a world with different rules. The real
promise, per the absorbed stub, is **permission to begin again** without the old body's habits
— not omnipotence. The best isekai carries the wound from the old world into the new one; the
new world does not erase it, it gives it room. Re:Zero's engine is death-loop as trauma;
Shield Hero's early arcs are a betrayal wound rebuilt slowly; Frieren is time and grief wearing
the genre's clothes.

Catalog allocation (`config/manga/locale_genre_allocations.yaml`): zh_CN 12% **primary** (the
996-work-culture burnout market; citation chain runs through `docs/CJK_CATALOG_PLAN.md` §1
"burnout→isekai recovery shell"), ja_JP 10% secondary (native home of the form), zh_TW 8%
niche, zh_SG 5% niche, en_US 3% niche (implication-only Western share). The wellness embed is
always the same shape: burnout → a world without the old job's rules; self-worth → no resume
follows you. Embedded, never marketed.

Readers will accept: heavy world-rule exposition *if* delivered through failure and discovery,
two-register dialogue comedy, tonal whiplash between comedy and drama (expected and desired),
long residence in daily-life beats. They will reject: a generic JRPG world with interchangeable
furniture, an instantly overpowered protagonist with no cost, stat screens deployed as the
emotional climax, and any panel where the topic is preached ("you must rest") instead of
enacted.

## 2. Visual Rules

- **Panels per page:** 4–6 (`manga_genre_writing_styles_2026_04_04.md` §10 metrics, line 608).
  Larger panels than school/shojo grids — the world itself is a character and needs room.
- **Words per page:** 70–120 (canonical contract, `manga_pacing_by_genre.yaml` `fantasy:` entry
  lines 264–283). The research baseline runs 50–120 "varies wildly" (line 606) — light on
  action pages, heavy during world-building; the contract holds the floor at 70 because isekai
  narrates constantly.
- **Words per balloon (max):** 25 (canonical — the genre's ceiling is the catalog's highest;
  exposition pressure is structural).
- **Silent panel %:** 15–30% (canonical `silent_panel_ratio_range: [0.15, 0.30]`). The research
  baseline is 10–15% ("isekai talks a LOT," line 609) — treat 0.15 as a hard floor and spend
  silence deliberately: arrival vistas, the homesick beat, the body registering wrong gravity.
- **Dialogue:caption ratio:** 55:45 (research line 610) — narration for world-building,
  dialogue for character comedy/drama. Interior narration is the translation layer: the
  protagonist interpreting the new world through the old one.
- **Reaction-shot frequency:** medium (canonical). The tsukkomi reaction panel (modern
  sensibility meeting fantasy absurdity) is genre-signature but declines across the series as
  the protagonist adapts — the declining tsukkomi tracks growth (research §10).
- **Spread frequency:** periodic (canonical). Spend spreads on arrivals — first sight of the
  city, the land answering, the vow. Never on a status screen.
- **Black-fill ratio:** 0.15–0.30. `background_density: ornate_detailed` (canonical) pushes
  ink into architecture, foliage, and market clutter rather than solid blacks; night/dungeon
  sequences may spike to 0.40 but the genre's default weather is daylight discovery.
- **Screentone convention:** texture-tone for worldbuilding surfaces (stone, timber, cloth);
  gradient skies on arrival panels; a distinct boxed/UI treatment for any status-screen or
  system text — *system text is typography, never hand-lettering*, and its visual register must
  be separable from the organic world (this is also the anti-drift lever that keeps the device
  in garnish position, per §6).
- **Line weight:** mid-weight organic line for the world; slightly cleaner, thinner line
  permitted on the protagonist to keep them legible as the outsider. SFX moderate (canonical)
  — wonder beats carry ambient SFX (ゴォォ waterfall, ざわ market murmur) more than impact type.

## 3. Pacing

**Structure:** settlement rhythm, not quest rhythm. Each volume banks one world-rule genuinely
learned (through failed attempts, not tutorial) and one wound beat (the old world surfacing in
the new). Episodic day-arcs thread onto a slow settlement through-line: arrival → shelter →
work → standing → belonging.

**Chapter hook:** the body in the new world before exposition — hands, breath, wrong gravity
(absorbed stub rule). Or: a small rule of the land asserting itself (bread that won't keep, a
door that expects a password, a moon too close). Never a lore caption.

**Page-turn triggers (canonical, `fantasy.page_turn_triggers`):** `revelation`, `arrival`,
`betrayal`, `impossible_task`, `vow`. One per turn, never stacked.

**Show, then explain:** the research doctrine (§10, "World-Building: Dialogue vs. Narration")
is the lane's pacing law — character encounters the strange thing → reacts → *then* gets the
explanation, if one is needed at all. The Solo-Leveling-style cutaway information panel is the
named anti-pattern ("PowerPoint slides"); embed world information in reactions and discoveries.

**Chapter ending:** a kept ritual, not a power-up (absorbed stub rule). The protagonist keeps
one small act on purpose — a door latched the local way, a phrase said correctly, tea taken
with the innkeeper. Endings on `vow` or `arrival` triggers close outward; endings on
`betrayal` reset the settlement one notch and are budgeted (≤1 per 3 volumes at this catalog's
recovery-shell pole).

**Tonal alternation:** comedy and drama alternate rapidly — tonal whiplash is expected (research
§10). The craft is placement: comedy lives in the two-register dialogue gap; drama lives in the
body and the homesick beat. They share pages but never the same panel.

*(Lane 03's `arc_cadence` blocks landed 2026-07-24 via `9446b3e74e` (#322): the pacing family's
`arc_cadence` block in `config/manga/manga_pacing_by_genre.yaml` is the quantitative authority
for beat cadence; the rhythm above is the qualitative contract.)*

## 4. Dialogue

**Two registers, never flattened (research §10 "Fish-Out-of-Water Dialogue"):**
- *Protagonist:* casual, modern, contraction-heavy; Earth references the locals cannot parse.
- *Locals:* fantasy register — formal address, trade idiom, era-appropriate rhythm. The comedic
  gap between the registers IS the genre; the dramatic gap (the protagonist realizing no one
  here can share a memory of home) is its shadow side.

**Key dialogue patterns (research §10, adapted to the recovery-shell pole):**
1. **The Earth Reference** — "This is just like—" cut off or met with blank stares; the
   protagonist's frame of reference is a private language, which is comedy early and
   loneliness later.
2. **The Audience-Surrogate Question** — "What's a guild?" The protagonist asks what the
   reader would ask; locals answer in-character, incompletely, so the world keeps its depth.
3. **The Local's Confusion** — "I don't understand half of what you're saying." The register
   gap played from the other side.
4. **The Adaptation Marker** — the protagonist stops being surprised; a local notices ("You
   ordered that like you were born here"). Growth is announced by others, never self-narrated.
5. **The Homesick Whisper** — the rare quiet beat where the old world is missed *specifically*
   (a convenience-store snack, a train sound, a person). One per volume at most; it carries the
   wound through-line.
6. **The Cost Line** — Re:Zero-register: what the new ability or new start actually costs,
   said plainly once and never milked ("I remember every loop. Nobody else does.").

**Balloon discipline:** ≤25 words (canonical). Exposition longer than a balloon becomes a
failed attempt on-panel instead — show the rule breaking the protagonist, don't say it.

## 5. Character

**Protagonist:** arrives carrying an old-world cost — exhaustion, shame, a name they no longer
want (absorbed stub). Competence grows by apprenticeship to the world, not by cheat: the
catalog's recovery-shell pole inverts the OP-protagonist default. Meta-knowledge, where present,
creates dramatic irony, not dominance. The wound is still there in volume 48; what changes is
the room it has.

**The guide (teacher-mode vessel, from `config/manga/manga_mode_vessels.yaml`):** doctrine
enters through a **genre-native guide who never lectures** — cartographer, innkeeper,
land-spirit — never named as the brand's teacher. The land's rules do the teaching; the guide
just refuses to hurry the protagonist past them. Wound → turn → renewal: the turn is a rule of
the land (or a small ritual) showing that the body knew the cost before the mind admitted it;
doctrine is *earned by doing*, never explained.

**Locals ensemble:** 4–6 recurring, each fluent in one domain of the world (the smith, the
gate-clerk, the herbalist). They are teachers-by-craft; their patience or impatience with the
outsider is characterization for both sides. At least one local should be a mirror: someone who
also arrived from elsewhere, further along the settlement curve.

**Antagonists:** systems and seasons more than villains — a guild examination, a winter, a
debt. Where a personal antagonist exists (Shield-Hero-register betrayal), the arc is trust
rebuilt slowly, and the betrayer must be legible as a person embedded in the world's incentives.

*(MC exemplars pending Lane 04 — when the main-character exemplar checklists merge, this
section feeds from them for named-cast scaffolding.)*

## 6. Failure Modes

1. **Generic JRPG world.** If the fantasy world is interchangeable with any other, there is no
   reason to explore it (research §10 failure #1). Give it specific, unique features — the
   catalog bar: three world-rules per series that exist nowhere else.
2. **Overpowered protagonist without tension.** If the MC can't lose, there are no stakes.
   The Re:Zero model: weak protagonist, one broken ability, terrible cost (research §10 #2).
3. **Status screens as storytelling crutch.** Numbers aren't narrative; use system UI as
   garnish for milestone moments only (research §10 #4), and always in the boxed typographic
   register (§2) so drift is visible at lint time.
4. **LitRPG stat screen as the emotional climax** (absorbed stub). The chapter's peak beat is
   never a number going up.
5. **Topic preached instead of enacted** (absorbed stub). "You must rest" in any mouth is a
   failed page; the land refusing to be hurried is the same content, enacted.
6. **Forgetting the isekai premise.** If the protagonist's modern perspective stops mattering
   after chapter 5, the genre premise is wasted (research §10 #5) — the translation layer must
   keep earning its place, even as the tsukkomi declines.
7. **Harem as substitute for character development** (research §10 #3). Relationship breadth
   without independent arcs is inventory, not cast.
8. **Wish fulfillment without consequence.** The Mushoku Tensei bar: the protagonist earns
   their place and pays for their advantages (research §10 #6).
9. **Teacher named in-story** (absorbed stub / vessel contract). The guide is never the brand's
   teacher by name; doctrine stays in the land.

## 7. 48-Volume Shape

48 volumes = **four 12-volume settlement eras** — the recovery arc mapped onto residence, not
power tiers. Unit of structure: the era (one relationship to the new world).

**Volumes 1–12 (Arrival — Learning the Rules):** wrong gravity, first shelter, first work.
Every rule learned through failed attempts; the guide found by volume 3 but trusted by volume
8. The old-world wound is named to the reader (not to the cast) by mid-band. Band closes on the
first kept ritual that survives a full volume.

**Volumes 13–24 (Roots — Building a Place):** work becomes standing; the ensemble thickens;
the protagonist teaches a newcomer one small rule (first inversion of the guide dynamic). The
wound resurfaces under pressure — an old-world habit (overwork, appeasement, flight) reasserts
in new-world clothes and costs something real. Band closes on `betrayal` or `impossible_task`
register: the settlement tested.

**Volumes 25–36 (The Crossing — The Old World Calls):** the past arrives — a memory artifact, a
second transplanted person, or a road back. The protagonist must go toward the old wound
(literally or ritually) rather than around it. The guide's own history surfaces: they were once
an arrival too. Band closes with the return crossing *chosen*, not forced.

**Volumes 37–48 (Homecoming in Place):** mastery redefined as tenancy — the protagonist now
holds the door for arrivals. A final season-scale threat (a winter, a levy, a land-rule
shifting) is resolved by the accumulated web of standing and craft, not by power. The final
volume closes on the same body-in-the-world framing as chapter 1 — hands, breath, gravity —
now familiar; the wound present, integrated, with room.

*(Lane 03's `arc_cadence` block (merged 2026-07-24, `9446b3e74e` #322) is the quantitative
authority on volume-band beat counts; the shape above is the narrative contract.)*

## 8. Panel Scaffolding

Per-panel fields for deterministic generation (9 fields):

1. `framing` — ELS / LS / MS / MCU / CU / arrival-vista / ui-insert / hands-insert
2. `beat_role` — one of {body_arrival, rule_encounter, failed_attempt, guide_beat,
   two_register_comedy, wound_echo, kept_ritual, vow, homesick_whisper}
3. `world_register` — one of {new_world_daily, new_world_wonder, old_world_memory,
   liminal_crossing}; drives tone/texture defaults (§2) and forbids Earth-reference dialogue
   outside protagonist scope
4. `rule_exposure` — one of {shown_by_failure, asked_and_answered, observed, explained};
   `explained` is budgeted ≤1 per chapter and must follow a `shown_by_failure` panel
5. `status_screen_flag` — boolean; true requires boxed-typography register, forbids
   `beat_role: kept_ritual|homesick_whisper|wound_echo` on the same panel, budget ≤2 per
   chapter
6. `tsukkomi_flag` — boolean; reaction-register comedy panel; frequency should decline across
   the series (adaptation marker, §4)
7. `dialogue` — ≤25 words per balloon (canonical); register must match speaker
   (modern/protagonist vs fantasy/local)
8. `caption` — protagonist interior translation layer, ≤20 words; comparative ("like X, but—")
   allowed; preaching forbidden
9. `silence_flag` — boolean; true on body_arrival, homesick_whisper, and post-vow beats;
   silence_flag=true on ≥15% of panels (floor of canonical range); consecutive non-silent
   panels ≤7

## 9. Locale Weighting

| Locale | Share / tier (`locale_genre_allocations.yaml`) | Notes |
|---|---|---|
| zh_CN | 12% primary | Burnout/996 resonance is the allocation driver (`CJK_CATALOG_PLAN.md` §1 burnout→isekai recovery shell; 2026-03-30 asian-persona research §3 zh-CN 996/sleep economy). Platforms: Kuaikan / Bilibili Comics; AI disclosure required; gray-zone per D-19 |
| ja_JP | 10% secondary | Native home of the form; light-novel adaptation pipeline sets reader expectations — differentiate on the recovery-shell pole, not power-fantasy volume |
| zh_TW | 8% niche | Full genre fluency via JP import culture; LINE Comics TW |
| zh_SG | 5% niche | Bilingual margin (`CJK_CATALOG_PLAN.md` §1 applied at SG margin) |
| en_US | 3% niche | Implication-only Western share; existing isekai anime audience is the beachhead; position as "second-chance fantasy," not LitRPG |

## 10. References

*Sources (pinned to origin/main `d55f6f397676a72913078efda87657b29c37babe`):*
`artifacts/research/manga_genre_writing_styles_2026_04_04.md` §10 Isekai lines 598–663 (metrics
table lines 602–610: words/page 50–120, panels 4–6, silent 10–15%, dialogue:narration 55:45;
fish-out-of-water dialogue lines 612–618; world-building dialogue-vs-narration lines 619–626;
status-screen doctrine; tsukkomi patterns; key dialogue patterns; failure modes lines 655–663)
and Cross-Genre Quick-Reference Table lines 669–680;
`config/manga/manga_pacing_by_genre.yaml` `fantasy:` entry lines 264–283 (words_per_page_range
[70, 120], words_per_balloon_max 25, silent_panel_ratio_range [0.15, 0.30], page_turn_triggers
revelation/arrival/betrayal/impossible_task/vow, background_density ornate_detailed, reference
corpus: Fullmetal Alchemist / Made in Abyss / Witch Hat Atelier) and alias `isekai: fantasy`
line 500;
`config/manga/canonical_genre_list.yaml` `fantasy_adventure` id line 137 with `aliases_inbound:
[fantasy, isekai, magical_girl]` line 144 and taxonomy fallback `isekai: fantasy_adventure`
line 287;
`config/manga/locale_genre_allocations.yaml` lines 100–104 (en_US 3% + implication-only note),
404–407 (zh_SG 5%), 442–445 (ja_JP 10%), 493–496 (zh_CN 12% primary + 996 citation), 584–586
(zh_TW 8%);
`docs/CJK_CATALOG_PLAN.md` §1 (burnout→isekai recovery shell);
`config/manga/manga_mode_vessels.yaml` (teacher-mode vessel contract);
predecessor stub: this file's 2026-era M3 Wave-1 version (reader promise, three-act skeleton,
vessel, anti-patterns — absorbed above);
structural template: `docs/research/manga_craft/supernatural_mystery.md`.
