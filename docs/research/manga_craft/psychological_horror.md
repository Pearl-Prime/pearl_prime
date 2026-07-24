# Psychological Horror — Craft Bible

> **Genre slug:** `psychological_horror` (pacing key `horror` per `manga_pacing_by_genre.yaml`
> alias line 491; drawing tradition: its OWN `top_8_deep` block in
> `config/manga/drawing_tradition_per_genre.yaml` — distinct from the deferred `horror` genre
> id, a separation that is CI-load-bearing and must be preserved).
> Expanded 2026-07-24 from the M3 Wave-1 stub (manga process uplift Lane 05); the stub's reader
> promise, teacher-mode vessel, and anti-patterns are absorbed into §1, §5, and §6 below.
> Touchstones: *Uzumaki* / *Tomie* (Junji Ito), *The Summer Hikaru Died* (Mokumokuren),
> *Higurashi: When They Cry* (Ryukishi07), *Goodnight Punpun* (adjacent — Asano Inio),
> *Mieruko-chan* (cute-horror boundary), *Something Is Killing the Children* (Western register).

## 1. Market Contract

Readers are 16–45 and — counterintuitively — **~55% female post-2018**, one of the more
female-balanced genres in the market (`horror_bestseller_research_2026-05-13.md` §5). The
cultural anchor is *controlled exposure to fear-as-rehearsal* and somatic catharsis: horror
readers are pre-selected for somatic literacy — they already know fear lives in the body —
which makes this the **highest-leverage genre for somatic-resourcing embeds** in the catalog
(dossier §5: therapeutic susceptibility "EXTREMELY HIGH").

The register is the dossier taxonomy's `psychological_horror` row: **the mind betrays**
(Higurashi, Punpun-adjacent) — distinct from cosmic (`Uzumaki`'s reality-is-wrong engine,
which this lane borrows techniques from), body horror, and survival horror. The promise, per
the absorbed stub: **something is wrong in the ordinary room.** The horror is not a jump-scare
catalog — it is the body's truth refusing to be ignored; the reader should feel the dread
*before* they can name it.

Catalog allocation (`config/manga/locale_genre_allocations.yaml`): ja_JP 14% **primary**,
zh_TW 14% **primary**, zh_HK 14% **primary**, zh_CN 8% secondary, en_US 4% niche. This is the
CJK lane's flagship genre shell; anxiety and sleep content ride inside it
(`docs/CJK_CATALOG_PLAN.md` §1 + §4). Wellness embeds as *the thing that will not stay silent*
— anxiety as an entity only the lead perceives; somatic trauma as a house that remembers —
never as self-help copy.

Readers will accept: slow-burn establishing scenes, unresolved endings, ambiguity held for
volumes, high silent-panel ratios, discomfort as the point. They will reject: gore-forward
body horror mislabeled as psychological, jump scares without build, comforting moral closure,
and any therapeutic vocabulary surfacing in captions.

## 2. Visual Rules

- **Panels per page:** 3–6 (`manga_genre_writing_styles_2026_04_04.md` §5 metrics, line 281)
  — large reveal panels against tight claustrophobic grids; the alternation is the technique.
- **Words per page:** 30–80 (canonical contract, `manga_pacing_by_genre.yaml` `horror:` entry
  lines 123–141). The research baseline runs 15–60 "deliberately sparse — silence is the
  weapon" (line 279); pages near the 80 ceiling are lull pages, pages near the floor are
  arrival pages.
- **Words per balloon (max):** 20 (canonical).
- **Silent panel %:** 35–55% (canonical `silent_panel_ratio_range: [0.35, 0.55]`) — the
  highest silence contract in the catalog; research baseline 30–50% (line 282), "highest of
  any genre."
- **Dialogue:caption ratio:** 60:40 (research line 283) — minimal narration; what IS said
  carries enormous weight.
- **Black-fill ratio:** 0.30–0.60 (`drawing_tradition_per_genre.yaml` `psychological_horror`
  B-block: "opposite of iyashikei's 5–15% floor"). White space is compressed and, when
  present, *threatening* — Uzumaki's spiral-cloud sky inverts empty-as-restful.
- **Two poles, one config cannot serve both (drawing-tradition A/B blocks):**
  - *Ito-sparse pole:* line starts neat in normalcy and escalates to frayed/panicked hatching
    as dread builds; ~70% hatching/screentone to 30% solid black.
  - *Maruo-dense pole:* uniform engraved pressure throughout; ~40% solid black, 60% precise
    crosshatch; gothic/ero-guro adjacency — used in this catalog only at the aesthetic level.
  Series must declare a pole in their manifest; mid-series pole drift is a lint error.
- **Faces:** realism plus one-degree-off proportions — the uncanny-valley face (dossier §4:
  "Junji Ito's eyes are 3% too large"). Expression grammar is *dread restraint*: pages of
  frozen, flat affect → a single peak panel (slack-jawed, hollow-eyed) per the drawing
  tradition's expression rule. Peak faces are budgeted, not free.
- **Reaction-shot frequency:** low (canonical) — the genre withholds reaction shots so the
  reader supplies the reaction themselves.
- **Spread frequency:** periodic (canonical); the spread is the page-turn reveal's payoff
  surface and is never spent on a lull.
- **Screentone convention:** heavy patterned dread-stippling (drawing-tradition B-block);
  `background_density: dense_oppressive` (canonical). Tone density tracks dread, not light.
- **SFX:** `sfx_usage: heavy_plus_dread_coded` (canonical) — dripping, creaking, scratching
  rendered as an inescapable audio landscape, placed at panel edges or bleeding across gutters
  (research §5 "SFX placement"). *Absence* of SFX where sound should exist is a deliberate
  wrongness device. **Therapeutic-brand ceiling (absorbed stub rule): heartbeat SFX at whisper
  register only — never BANG-register.** Biological SFX stays at the suggestion level; this
  lane is dread, not gore.

## 3. Pacing

**Two engines (dossier §3):**
1. *Anthology / case-of-the-week* (Ito, Mieruko register) — each chapter one horror event;
   dread is cumulative across cases.
2. *Mystery box* (Higurashi, Uzumaki register) — one wrong thing runs the whole arc; the
   protagonist circles it.
A 48-volume series interleaves both: anthology chapters breathe between mystery-box arcs.

**The slow-burn establishing scene is the signature move:** 4–6 pages of completely normal
life before the wrongness arrives (dossier §3). The reader must be lulled; a chapter that
opens on the horror has already failed. Then one wrong detail. Then escalation
(mundane-to-monstrous, research §5 "Junji Ito's Specific Techniques").

**Page-turn triggers (canonical, `horror.page_turn_triggers`):** `uncanny_reveal`,
`distorted_image`, `body_horror_cut`, `ominous_image`. The page-turn reveal is the genre's
core mechanic — build dread across a page of small reaction-less panels; the horror itself is
on the NEXT page; the reader must choose to turn (research §5). `body_horror_cut` is available
but rationed at this catalog's therapeutic pole — suggestion over anatomy.

**Chapter ending:** the ordinary room, slightly changed (absorbed stub). Never full comfort,
never total despair; the horror is not defeated, it is *met*, and its grip loosens one notch —
or tightens one. The aftermath beat is mandatory: the dossier's therapeutic landing moments
(§7) live there — the pre-confrontation breathing scene, the morning-after kitchen with hands
shaking on a coffee cup, the perimeter walk at dawn. These are where somatic resourcing enters
without ever being named.

**Fleeing feeds it (absorbed stub skeleton):** act one is refusal — the protagonist
rationalizes the signal, and rationalizing *strengthens* it. The turn is one breath toward the
dread instead of away. The only way out is through — enacted, never captioned.

*(Lane 03's `arc_cadence` blocks landed 2026-07-24 via `9446b3e74e` (#322): the pacing family's
`arc_cadence` block in `config/manga/manga_pacing_by_genre.yaml` is the quantitative authority
for beat cadence; the rhythm above is the qualitative contract.)*

## 4. Dialogue

**Register:** sparse, flat, mundane — the contrast between casual speech and abnormal visuals
creates the cognitive dissonance that IS the genre (research §5: "When dialogue AMPLIFIES
horror"). Discovery scenes take NO dialogue: the moment a character sees the horror, words
are removed and the image and the reader's body do the work.

**Key dialogue patterns (research §5):**
1. **The Denial** — "It's nothing... I'm sure it was just my imagination." The reader knows
   it wasn't; the gap between the line and the panel is the dread.
2. **The Calm Description of Horror** — a character describes something terrible in flat,
   clinical language; wrongness carried by register mismatch.
3. **The Repeated Phrase** — a line that becomes sinister through repetition and context
   shift; plant it in a lull page, harvest it at the reveal.
4. **The Warning Ignored** — "Don't go there." / "Don't look at it." The protagonist does it
   anyway; the reader is complicit because they turned the page to watch.
5. **The Disbelieved Telling** — the protagonist tries to tell someone (a friend, a
   professional) and is not believed (dossier §7: the genre's metabolic pattern is the
   *invalidation* of clinical help — which is exactly what makes the somatic vessel's
   welcome, §5, land so hard).
6. **The Survivor's Instruction** — the vessel's register: short, bodily, present-tense.
   "You held your breath when you came in. Notice you're breathing now." Never more than two
   sentences; never a term of art.

**Unreliable narration:** minimally characterized protagonists as projection surfaces;
narrators who insist everything is fine while the visuals scream otherwise; perspective
shifts that retroactively reveal the narrator was wrong (research §5). Interior monologue is
somatic and brief — the body registers what the mind refuses (shared grammar with
`seinen_psychological`, but here the body is *right* and the mind's refusal is the plot).

## 5. Character

**Protagonist:** vulnerable by design — horror requires vulnerability; competent, well-armed
characters undermine fear (research §5 failure #4). The protagonist's initial strategy is
always management-by-avoidance: rationalize, flee, stay busy. Fleeing feeds it. Their arc is
not toward power but toward *capacity* — the ability to stay present one breath longer than
last time.

**The survivor-vessel (teacher-mode, from `config/manga/manga_mode_vessels.yaml`):** `the
survivor who turns toward it` — wound: flee and feed it; turn: meet it; renewal: met, it
loses grip. Modeled on the dossier §8 operator-example (Baba's tea shop): an elder who has
survived their own haunting and teaches somatic technique without ever naming it as therapy —
orienting (find five blue things), grounding (feet flat, name the floor), pendulation (notice
ease, then tension, then return). The vessel never explains the horror and never names the
teacher or the doctrine. **Never the brand teacher by name.**

**Supporting cast:** small (2–4). One co-regulator (roommate, sibling) who does not perceive
the wrongness and whose ordinary presence is the protagonist's anchor — and strain. One
disbeliever whose invalidation closes the clinical door (§4 pattern 5). The entity itself is
cast: it has a grammar (where it appears, what feeds it, what it wants ignored), and that
grammar must stay consistent even while its nature stays unexplained.

**What the entity is:** at this catalog's pole, always legible — beneath the genre surface —
as an embodied pattern: anxiety as an entity only the lead perceives; trauma as a house that
remembers (absorbed stub). The mapping is never stated. The horror arc never resolves; the
somatic recovery does (dossier §8).

*(MC exemplars pending Lane 04 — when the main-character exemplar checklists merge, this
section feeds from them for named-cast scaffolding.)*

## 6. Failure Modes

1. **Over-explaining the monster.** Mystery is scarier than mythology; the less explained,
   the more frightening (research §5 failure #1). A codified entity taxonomy converts dread
   into a power system.
2. **Too much dialogue.** Every word added to a horror scene reduces its power (research §5
   failure #2). The 30–80 words/page contract is a ceiling to live under, not a target.
3. **Jump scares without build-up.** A shocking image without preceding tension is gross,
   not scary (research §5 failure #3). Every reveal must be paid for by a lull.
4. **Too-capable protagonist.** Competence undermines fear (research §5 failure #4);
   resourcefulness is allowed only in the somatic register.
5. **Horror as punishment for "not doing self-care"** (absorbed stub). The entity is never a
   morality enforcer; the wellness embed collapses into preaching the moment dread is framed
   as deserved.
6. **Defeating the monster = curing the topic** (absorbed stub). The horror is met, not
   defeated; grip loosens one notch. A slain entity is a genre exit.
7. **Explicit therapy jargon in captions** (absorbed stub). "Grounding," "trauma response,"
   "nervous system" — any term of art in caption or balloon fails the page.
8. **Register bleed into neighbors.** Spirits who are sad rather than wrong belong to
   `supernatural_mystery`; interior decay without an external wrongness belongs to
   `seinen_psychological`; gore-forward anatomy belongs to a body-horror register this
   catalog does not ship. The lane's own CI seam: `psychological_horror` must keep its own
   drawing-tradition block and never collapse into the deferred `horror` genre id.
9. **Comedic relief mistimed.** Comedy can coexist (Mieruko model) but timing is everything —
   wrongly placed, tension evaporates permanently (research §5 failure #5).
10. **BANG-register SFX on therapeutic brands** (absorbed stub / §2). Whisper-register
    heartbeat only; dread is quiet.

## 7. 48-Volume Shape

48 volumes = **four 12-volume dread cycles**, each one full revolution of
refusal → meeting → residue, at expanding scope. The horror never resolves across the series;
the protagonist's capacity does. Unit of structure: the cycle.

**Volumes 1–12 (Cycle I — The Signal):** anthology-weighted. The wrongness announces itself
in small, deniable events; the protagonist's flee-and-feed pattern is established and costed.
The survivor-vessel is encountered by volume 4 but their instruction only lands at the
band's end — the first breath *toward*. First somatic tool kept.

**Volumes 13–24 (Cycle II — The House That Remembers):** mystery-box arc. The entity's
grammar cohered; the ordinary room (apartment, family house, workplace) revealed as the
memory-holding structure. The co-regulator relationship strained by what cannot be told; the
disbelieved-telling beat closes the clinical door. Band ends with the protagonist returning
to the house on purpose.

**Volumes 25–36 (Cycle III — The Naming Without Names):** externalization. Mapping, drawing,
walking the perimeter — the dossier's planning-scene landing moments become the arc's spine.
The entity escalates as it is witnessed (witnessing is not free). A second afflicted person
appears; the protagonist becomes, imperfectly, a vessel for them — and discovers how much
they have and have not integrated. Band ends at peak dread: the reveal that the entity's
grammar points at something in the protagonist's own history.

**Volumes 37–48 (Cycle IV — Met, Not Defeated):** the turn toward the source. The final
confrontation is staged in the body: staying present in the room where it lives, one breath
at a time, with the co-regulator outside the door. The entity does not die; its grip loosens.
The final chapter is the ordinary room, slightly changed, in daylight — the same framing as
chapter 1's establishing page, with one detail at rest that was wrong before. Recovery
without cure; capacity without closure.

*(Lane 03's `arc_cadence` block (merged 2026-07-24, `9446b3e74e` #322) is the quantitative
authority on volume-band beat counts; the shape above is the narrative contract.)*

## 8. Panel Scaffolding

Per-panel fields for deterministic generation (9 fields):

1. `framing` — ELS / LS / MS / MCU / CU / extreme-CU-detail / doorway-threshold / reveal-spread
2. `beat_role` — one of {normal_lull, wrong_detail, denial, escalation, page_turn_setup,
   reveal, aftermath, somatic_beat, vessel_instruction}
3. `dread_register` — one of {baseline, unease, escalation, peak, residue}; drives tone
   density, black-fill, and line-fray level (Ito pole) per §2; `peak` budget ≤2 per chapter
4. `pole` — `ito_sparse` or `maruo_dense`; series-constant from the manifest; mid-series
   change is a lint error
5. `entity_visibility` — one of {absent, trace, peripheral, partial, full}; `full` only on
   `reveal` beats after a `page_turn_setup` page; the ratio of trace:full should exceed 4:1
6. `somatic_state` — null or one of {breath_held, breath_noticed, orienting, grounding,
   pendulation}; non-null forbids therapy vocabulary in `dialogue`/`caption` and marks the
   panel as a therapeutic landing moment
7. `sfx` — dread-coded vocabulary or null; whisper-register only for heartbeat; deliberate
   null on should-have-sound panels is a wrongness device and must be flagged in `beat_role`
8. `dialogue` — ≤20 words per balloon (canonical); null on reveal panels; flat/mundane
   register on escalation panels (calm-description pattern)
9. `silence_flag` — boolean; true on reveal, aftermath, and somatic_beat panels;
   silence_flag=true on ≥35% of panels (floor of canonical 0.35–0.55 range); consecutive
   non-silent panels ≤4

## 9. Locale Weighting

| Locale | Share / tier (`locale_genre_allocations.yaml`) | Notes |
|---|---|---|
| ja_JP | 14% primary | Native home register (Ito, Higurashi lineage); anxiety/sleep embeds per `CJK_CATALOG_PLAN.md` §1+§4; the catalog's flagship genre-shell in this locale |
| zh_TW | 14% primary | Strong horror appetite via JP import culture + local ghost-tradition literacy; LINE Comics TW |
| zh_HK | 14% primary | Cantonese horror-cinema lineage primes the register; Traditional-character production shared with zh_TW |
| zh_CN | 8% secondary | Supernatural framing constrained — prefer psychological/mind-betrays framing over ghost vocabulary in descriptions (precedent: `supernatural_mystery.md` §9 CN note); gray-zone per D-19; AI disclosure required |
| en_US | 4% niche | Cult shelf, not primary self-help carrier (US catalog citation: SIKTTC / Sweet Home comps); Ito's US bookstore presence is the beachhead |

## 10. References

*Sources (pinned to origin/main `d55f6f397676a72913078efda87657b29c37babe`):*
`artifacts/research/manga_genre_writing_styles_2026_04_04.md` §5 Horror Manga lines 271–338
(metrics table lines 275–283: words/page 15–60, panels 3–6, silent 30–50%, dialogue:narration
60:40; silence-as-dread lines 285–291; unreliable narrator lines 292–298; SFX writing lines
299–305; Ito techniques lines 306–312; dialogue patterns lines 313–320; failure modes lines
329–338) and §2 Seinen lines 79–137 (interior-monologue and environmental-storytelling
grammar shared at the boundary);
`artifacts/research/genre_bestseller_dossiers/horror_bestseller_research_2026-05-13.md`
(§2 register taxonomy — `psychological_horror` = "the mind betrays"; §3 two engines +
slow-burn establishing scene; §4 visual register; §5 demographics — 55% female, therapeutic
susceptibility EXTREMELY HIGH; §7 therapeutic-embed landing moments; §8 operator-example —
the Baba's-tea-shop somatic pattern; §9 Phoenix series concepts);
`config/manga/manga_pacing_by_genre.yaml` `horror:` entry lines 123–141 (words_per_page_range
[30, 80], words_per_balloon_max 20, silent_panel_ratio_range [0.35, 0.55], page_turn_triggers
uncanny_reveal/distorted_image/body_horror_cut/ominous_image, sfx_usage
heavy_plus_dread_coded, background_density dense_oppressive, reference corpus: Uzumaki /
Tomie / Junji Ito short form) and alias `psychological_horror: horror` line 491;
`config/manga/drawing_tradition_per_genre.yaml` `psychological_horror` block (status
top_8_deep; bipolar Ito-sparse/Maruo-dense line tradition; black-fill 30–60%; dread-restraint
expression rule; subgenre split recommendation) — NOTE: this genre id keeps its own deep
block and must never collapse into the deferred `horror` id (wave-2 spec item-1 constraint,
enforced on live main);
`config/manga/locale_genre_allocations.yaml` lines 95–99 (en_US 4% + SIKTTC/Sweet Home
citation), 422–425 (ja_JP 14% primary), 513–515 (zh_CN 8%), 549–551 (zh_TW 14% primary),
618–620 (zh_HK 14% primary);
`docs/CJK_CATALOG_PLAN.md` §1 + §4 (anxiety/sleep inside horror shell; genre-shell revenue
gap); `config/manga/manga_mode_vessels.yaml` (survivor-vessel contract);
predecessor stub: this file's 2026-era M3 Wave-1 version (reader promise, three-act skeleton,
vessel, anti-patterns — absorbed above);
structural template: `docs/research/manga_craft/supernatural_mystery.md`.
