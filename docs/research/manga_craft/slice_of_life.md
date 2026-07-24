# Slice of Life Manga — Craft Bible

> Canonical genre lane per `config/manga/canonical_genre_list.yaml` (`id: slice_of_life`, label "Slice of Life", `parent_family: null`, `must_include: yes`). Taxonomy-only row (`source_pacing: no`) — pacing is proxied to `healing` (`pacing_proxy: healing`); see §3 for the adaptation and the flagged gap.
> Quality-gate hint per `config/manga/main_character_interaction_grammar.yaml`: `slice_of_life: {quality_gate_checks: [relationship_or_self_interaction]}` — every chapter must clear a bar of genuine relational or self-reflective content, not merely incident.
> Adjacent-but-distinct lane: `docs/research/manga_craft/iyashikei_minimalism.md` (healing). Slice of life is iyashikei's warmer, more populated sibling — see §1 for the distinction. Do not use this file interchangeably with iyashikei's; do not use `BL_slice_of_life.md` as a substitute either — that lane is queer-relationship-specific and this one is genre-general.

Touchstones: *Yotsuba&!* (Kiyohiko Azuma), *K-On!* (kakifly), *Nichijou* (Keiichi Arawi), *Barakamon* (Satsuki Yoshino), *Non Non Biyori* (Atto).

---

## 1. Market contract

**Target demographic:** Broad — teens through adults, skewing slightly young-adult and slightly female, but slice of life is the one genre lane with genuine crossover appeal across age and gender because its hook is not a premise but a *feeling*: the ordinary made warm and worth watching. Readers arrive tired of plot and stakes; they want to spend time inside a place and a group of people who like each other.

**Emotional promise:** *Nothing bad is going to happen to these people, and I still want to know what happens next.* The contract is low-stakes but not low-*attention* — readers are here for the specific texture of a life (a classroom's seating chart, a village's one vending machine, a share house's grocery rotation) rendered with enough loving detail that the mundane becomes interesting. Unlike iyashikei, the promise is not solitude and atmosphere but *company* — an ensemble the reader wants to be inside of. Readers will accept: comedic beats, a wide cast, small competitive stakes (a school festival, a band's first gig), gentle romantic subtext. They will reject: genuine danger, a named villain, tragedy played straight, and any sense that the ensemble might actually fracture.

**Distinction from iyashikei (do not confuse the two lanes):** iyashikei is a solo-or-near-solo lead moving through atmosphere with a small rotating cast (3–6); slice of life is an *ensemble* genre — a fixed cast of 4–8+ who are already a unit by chapter 1, and the pleasure is watching that unit's internal dynamics (Yotsuba's found-family household, K-On's five-piece club, Non Non Biyori's one-room schoolhouse). Iyashikei's silences are meditative; slice of life's silences are comedic beats or held affection, not atmosphere. Where iyashikei restores a nervous-system baseline, slice of life restores a *social* baseline — the reassurance that a group of people can simply be glad to see each other, chapter after chapter, with no plot required to justify it.

---

## 2. Visual grammar

- **Panel count per chapter:** 60–100 panels over 16–24 pages (magazine standard for 4-koma-adjacent and standard-grid slice of life alike); avg 3.5–5 panels/page — denser than iyashikei's 2.5, because more is *happening* per page (a full classroom, a group conversation, a physical gag).
- **Words per page:** 45–85 (see §3 for the full pacing-table adaptation). Ensemble scenes with 3+ speaking characters push toward the top of the range; solo domestic beats (Yotsuba alone with a cicada shell) sit at the bottom.
- **Silent-panel ratio:** 15–35% — lower than iyashikei's 35–60%. Silence in this lane is usually a comedic beat (the group's collective reaction-pause before a punchline) or a held-affection panel (a friend noticing another friend's small kindness), not extended atmosphere.
- **Black-fill ratio:** 0.10–0.20. Light and airy like iyashikei, but the blacks that do exist are more likely to be hair/uniform than shadow — this is a daylight genre.
- **Screentone density:** Low-to-medium, used for warmth (soft gradient skies, blush tones on faces) rather than mood. Comedic beats frequently drop tone entirely for a clean-line "gag panel."
- **Spread frequency:** 1 per 1–3 chapters, reserved for *ensemble group shots* — the whole cast gathered (a festival, a rooftop lunch, a group photo composition) — rather than iyashikei's solo landscape spread. This is the lane's visual signature: the spread exists to prove the group is whole.
- **Reaction-shot frequency:** High — 4–8 per chapter, the genre's core rhythm engine. A slice-of-life page routinely cuts between a speaker and 2–3 simultaneous listener reactions in a single sequence (the "reaction row"), which is how the ensemble register stays legible without dialogue overload.
- **Line weight profile:** Light-to-medium, rounded, often chibi-capable — the same character model must be able to snap into a simplified/SD reaction form for a comedic beat (Nichijou's signature move) without breaking tonal continuity.
- **Comedic-beat frequency:** 1–3 visual gags per chapter (a sight gag, a chibi deformation, an absurd non sequitur inserted into an otherwise naturalistic scene) — Nichijou runs this near-continuously; Yotsuba and Non Non Biyori use it more sparingly, as seasoning rather than structure.

---

## 3. Pacing

**Flagged gap — no direct pacing-table entry.** `config/manga/manga_pacing_by_genre.yaml` has no `slice_of_life:` key. `config/manga/canonical_genre_list.yaml` sets `pacing_proxy: healing`, i.e. the numbers below are adapted from the `healing:` entry (`manga_pacing_by_genre.yaml` ~line 81) rather than measured directly against a slice-of-life reference corpus. **Recommendation: a follow-up should add a direct `slice_of_life:` entry to `manga_pacing_by_genre.yaml`**, built against an actual reference corpus (Yotsuba&!, K-On!, Nichijou, Barakamon, Non Non Biyori) rather than proxied.

**Adaptation rationale.** Per `config/manga/main_character_interaction_grammar.yaml`'s `slice_of_life: {quality_gate_checks: [relationship_or_self_interaction]}` gate, this lane is structurally *relationship-forward* in a way iyashikei's atmospheric solo-lead register is not — it requires an ensemble in active social contact, not a lone observer moving through weather. That relational requirement pushes every healing-proxy number in a consistent direction:

| Field | `healing` proxy value | `slice_of_life` adapted value | Direction & reason |
|---|---|---|---|
| `words_per_page_range` | [20, 50] | **[45, 85]** | Up — a scene with 3–5 speaking cast members generates more dialogue volume than iyashikei's solo-observer register. |
| `words_per_balloon_max` | 20 | **20** | Held — individual lines stay short (naturalistic chatter, not monologue); the increase is in balloon *count* per page, not per-balloon length. |
| `silent_panel_ratio_range` | [0.35, 0.60] | **[0.15, 0.35]** | Down — ensemble comedy and conversation fill panels that iyashikei would leave wordless; silence here is a beat, not the baseline. |
| `reaction_shot_frequency` | low | **high** | Up — the reaction-row (see §2) is this lane's core rhythm device; iyashikei's environmental reactions (a leaf falling) are replaced by human reaction cuts. |
| `spread_frequency` | periodic | **periodic** | Held in frequency, redirected in *use* — ensemble group shots, not solo landscape (see §2). |
| `narration_tolerance` | moderate | **low-to-moderate** | Down slightly — dialogue carries more of the interior-state work than caption does, because the ensemble is present to react to a character rather than leaving them to narrate alone. |
| `sfx_usage` | atmospheric | **domestic/light-comedic** | Redirected — kettle whistles, door chimes, footsteps, a chalkboard eraser clap, laughter — everyday-life sound rather than wind/water/insect atmosphere. |
| `background_density` | rich_plus_quiet | **rich_plus_populated** | Redirected — backgrounds carry the same loving specificity as iyashikei but are full of *people* (a classroom, a shop floor, a festival crowd) rather than empty landscape. |

- **Chapter length:** 16–24 pages (shorter than iyashikei's 20–28; the ensemble format favors more, tighter chapters over fewer long ones).
- **Chapter hook family:** *Ensemble-in-motion.* Open mid-activity with 2+ cast members already interacting (not a solo weather cue) — a classroom before the bell, a club room mid-argument-about-nothing, a shop's morning rush. The hook is "you're rejoining people you already know," not "here is a mood to enter."
- **Chapter ending convention:** *Shared small moment* — the group settles (walking home together, a shared snack, a last punchline that lands on the whole cast's laughter) rather than iyashikei's solitary return-to-baseline. The final panel usually contains 2+ characters, not one.
- **Scene-to-scene transitions:** Activity-to-activity hard cuts are common and acceptable (unlike iyashikei's near-exclusive bleed transitions) — a slice-of-life chapter can jump from classroom to rooftop to walk-home in three scenes without an environmental bridge, because the cast's continuity carries the reader, not the setting's.
- **Per-volume arc shape:** Volume = a slice of the group's shared calendar (a school term, a festival season, a year in a village) told through mostly-standalone chapters with light continuity threads (a new member joining, a running gag's payoff, a season turning). Like iyashikei, no volume should introduce a threat requiring resolution — but unlike iyashikei, a volume *can* carry a mild competitive or logistical throughline (the band's first live, the festival prep) as long as the outcome is never in real doubt.

---

## 4. Dialogue

- **Register:** Naturalistic, age-appropriate chatter — overlapping, interrupting, tangential. Characters talk *past* each other as often as *to* each other (a defining slice-of-life texture: Yotsuba's non sequiturs, Nichijou's characters mid-conversation about something unrelated to the visual gag happening around them).
- **Narration tolerance:** Low-to-moderate. Caption is used for light scene-setting ("Third week of the term") and rarely for interiority — the ensemble is present to react, which does the interiority work that caption would otherwise carry.
- **Dialogue-to-narration ratio:** ~80:20 — the highest dialogue share of any genre in this lane family, driven by ensemble presence.
- **Interior monologue:** Sparse and comedic more often than confessional — a single aside caption undercutting the visible action (a character's calm face captioned with an anxious thought) is the lane's signature interior-monologue move, borrowed lightly from workplace-comedy grammar but played warm rather than caustic.
- **Ensemble-voice differentiation:** Because 4–8 characters carry dialogue in a single chapter, each must have an immediately legible verbal tic or register (formal/blunt/dreamy/deadpan) readable from the dialogue alone, without a name tag — this is the lane's hardest craft requirement and its most common failure point when it goes missing (see §6.1).
- **Tell-don't-show tolerance:** Low for emotional labeling, as in iyashikei, but for a different reason — in an ensemble, another character's visible reaction *is* the show; a line like "She felt embarrassed" is redundant when the panel already contains three friends' reaction shots doing that work.

---

## 5. Character

- **Archetype grammar:** A fixed ensemble anchored by one of: the observant newcomer/child lens (Yotsuba), the tight-knit club/group with defined roles (K-On's five members each carrying a distinct function: leader, talent, klutz, quiet one, mentor-senior), the eccentric-outsider-integrates-into-village register (Barakamon's exiled calligrapher, Non Non Biyori's transfer student), or the deadpan-surreal peer group (Nichijou). The through-line across all of them: the cast is a *unit* from the first chapter, not a group that forms over the course of the series.
- **Cast density:** 4–8 recurring principal cast, wider than both iyashikei (3–6) and BL slice-of-life (duo + 3–6 support) — this is the genre's defining structural fact. A slice-of-life cast that shrinks to 2–3 has drifted into a different lane (romance or iyashikei).
- **Emotional arc per volume:** Group baseline → a small perturbation (new member, small competition, minor mishap) → the group absorbs it together → baseline restored *and visibly closer*. Unlike iyashikei's solo return-to-baseline, the slice-of-life return is measured in the ensemble's cohesion, not an individual's atmosphere.
- **The newcomer/outsider function:** Recurring device (Yotsuba as literal newcomer to the neighborhood, Barakamon's protagonist as exile, Non Non Biyori's transfer student) — a fresh set of eyes that lets the ensemble's existing warmth be *narrated through discovery* rather than stated. Not required in every slice-of-life series, but present in most of the touchstones for a reason: it solves the "how do we show an already-warm group without exposition" problem.
- **Adult-anchor figures:** Slice of life frequently includes at least one benevolent adult (Yotsuba's father, Barakamon's village elders, Non Non Biyori's teacher-in-training) who is competent and warm rather than an obstacle — a marked departure from shonen/workplace grammar where adults are often pressure sources.

---

## 6. Failure modes

1. **Nothing actually observed, just vibes.** The cardinal sin of this lane. Slice of life reads as thin the instant its "everyday texture" is generic (unspecified snacks, unnamed streets, weather-as-wallpaper) rather than *specific* (Yotsuba's exact cicada shell, K-On's exact snack-table spread, Non Non Biyori's exact single vending machine). If a beat could be moved to any other slice-of-life series without rewriting, it hasn't been observed — it's been assumed.
2. **Ensemble collapse into one voice.** All 4–8 cast members sound interchangeable in dialogue; readers can't identify a speaker without a name tag. Fatal because voice differentiation is this lane's primary characterization tool (see §4).
3. **Introducing real stakes.** A villain, a genuine threat, a relationship-ending betrayal — any of these breaks the contract as surely as it would in iyashikei; slice of life tolerates *competitive* or *logistical* mini-stakes (a festival deadline) but never danger or malice.
4. **Comedy without warmth, or warmth without comedy.** The two touchstones diverge here (Nichijou is comedy-forward, Yotsuba is warmth-forward) but a slice-of-life series that has neither reads as inert; it needs at least one of the two engines running per chapter.
5. **Plot creeping in disguised as "arc."** A festival-prep or first-gig throughline is fine (§3) but must never accrue conflict, sabotage, or rivalry drama — the moment stakes feel real, the genre has quietly become sports or shonen.
6. **Static ensemble — no visible closeness accrual.** If volume 24's group dynamic reads identical to volume 1's, the "baseline restored, slightly deeper" arc (§5) has failed; readers should feel the cast knows each other better over time even with no plot forcing it.
7. **Over-explaining the gag or the warmth.** A caption that spells out the joke or the feeling after the panel has already delivered it (tell-don't-show, see §4) drains the lane's charm, which depends on trusting the reader to catch small things unassisted.
8. **Borrowing iyashikei's silence density wholesale.** A slice-of-life chapter that runs 40%+ silent panels reads as tonally adrift — it has imported the wrong sibling lane's rhythm (see §1, §3).
9. **Treating the newcomer/outsider device as mandatory.** Not every slice of life needs a fresh-eyes entry character (K-On and Nichijou don't lean on it); forcing one in creates artificial exposition scenes.
10. **Recipe-for-conflict subplot creep from adjacent brand topics.** Where this catalog embeds a subtext wellness topic (see project brief), it must never surface as named coaching or a named program in-panel — slice of life's low-stakes contract makes an on-the-nose "lesson" beat land especially badly, more so than in higher-stakes lanes where a mentor figure has narrative cover to speak plainly.

---

## 7. 48-volume shape

Slice of life's 48-volume shape is an **ensemble calendar**, not an escalating plot — the closest sibling model is iyashikei's seasonal-cycle structure (§7 of `iyashikei_minimalism.md`), widened to carry a full cast's shared life rather than one observer's atmosphere:

- **12 × 4-volume "terms" or "seasons"** (a school year's four terms repeated across grade levels, or four seasons repeated across years in a fixed place — Non Non Biyori's village, K-On's clubroom), each term introducing one small perturbation (a new member, an event, a minor departure) that the ensemble absorbs, OR
- **8 × 6-volume "chapters of the group's life"** organized by a recurring structural unit (a school year, a shop's fiscal year, a village's harvest cycle) rather than by theme, OR
- **48 standalone-ish volumes** linked by place and cast continuity only (a neighborhood, a clubroom, a village), each closer to a self-contained short-story collection than a serialized arc.

Long-arc material should be **demographic and compositional**, exactly as iyashikei recommends: characters age through the series in real time (Yotsuba growing up across decades of volumes, K-On's third-years graduating and a new cohort arriving), cast composition slowly turns over (a member graduates or moves away; a new member joins and is absorbed by volume's end), but the *ensemble itself* — not any one member — is the through-line the reader is loyal to across all 48 volumes. Avoid: a series-wide antagonist, a season-ending crisis cliffhanger, or a plot mechanism that would require volumes 1–48 to be read in strict sequence to make sense. A reader should be able to open volume 30 cold and understand the ensemble's dynamic within a chapter.

---

## 8. Panel scaffolding

Per-panel fields (9):

1. `framing` — ELS / LS / MS / MCU / CU / insert / reaction-row (2–3 simultaneous listener panels in sequence) / group-tableau
2. `beat_role` — one of {ensemble_hook, comedic_beat, held_affection, reaction_row, activity_transition, group_closure, newcomer_discovery, small_perturbation}
3. `speaker` — which cast member (or `group` for simultaneous/overlapping dialogue) — required non-null on all non-silent panels; enforces voice-differentiation discipline (see §4, §6.2)
4. `dialogue` — ≤15 words per balloon; overlapping/interrupted lines permitted and should be flagged with a linked `speaker` per fragment
5. `caption` — ≤12 words, scene-setting or light-comedic aside only; interiority almost always routed through a reaction panel instead (null on most panels)
6. `sfx` — domestic/environmental-comedic (kettle, chalk, door chime, footsteps, laughter), or null
7. `reaction_count` — integer 0–3; number of simultaneous listener-reaction panels attached to this dialogue beat (drives the reaction-row device)
8. `ensemble_present` — integer; how many named cast members are in frame (must average ≥3 across a chapter — a chapter that drifts toward 1–2 for most of its length has drifted out of the lane)
9. `silence_flag` — boolean; true forbids dialogue and caption but permits domestic sfx; must appear on 15–35% of panels (see §3), lower than iyashikei's 35%+ floor

Constraint hint for the generator: `reaction_count ≥ 2` on at least one panel per page; `ensemble_present` must not fall below 2 for more than 3 consecutive panels except during a designated solo comedic or reflective beat (max 1 such run per chapter).

---

## 9. Locale weighting

| Locale | Primary register | Platform | Notes |
|---|---|---|---|
| **ja_JP** | Native home lane — 4-koma-adjacent magazines (Manga Time Kirara, Comic Cune) and standard-grid seinen/shonen crossover (Barakamon in Weekly Shonen Magazine). Deepest reference corpus; highest craft-authenticity bar. | Manga Time Kirara, LINE Manga, ComicWalker | Iyashikei/slice-of-life demographic overlap is real here — confirm which register a given brand is targeting before drafting (see §1 distinction). |
| **en_US** | Strong crossover appeal (broadest-demographic lane in the catalog per §1); anime adaptations (K-On!, Nichijou, Non Non Biyori) are the primary English-market discovery path. | Amazon manga digest, WEBTOON English, Crunchyroll Manga | Comedic beats (§2, §6.4) translate well; ensemble voice-differentiation (§4) needs careful localization to preserve distinct registers in English dialogue. |
| **zh_TW** | Warm reception; iyashikei/slice-of-life overlap audience is well established via existing anime/manga import market. | LINE Comics TW | Ensemble-warmth register aligns naturally with TW literary/quiet-palette art direction. |
| **zh_CN** | Low-risk lane — no sensitive content by default (no romance-forward or politically adjacent material required). Straightforward to localize. | Bilibili Comics, Kuaikan | AI-disclosure and standard content-review requirements apply per catalog default; no genre-specific gray-zone flag. |
| **ko_KR** | Established Naver/Kakao "healing" and "everyday" webtoon categories; format adaptation to vertical scroll needed (reaction-row device, §2/§8, adapts naturally to vertical panel stacking). | Naver Webtoon, Kakao | Episode-cliffhanger convention (webtoon default) must be softened per §3/§6.3 — slice of life's contract forbids real stakes even in a cliffhanger-driven platform. |

---

*Sources: `docs/research/manga_craft/iyashikei_minimalism.md` (primary structural/formatting template; §1, §3, §5, §7 direct comparison basis); `docs/research/manga_craft/BL_slice_of_life.md` (checked for structural/tonal patterns per assignment; confirmed genre-general divergence, not used as a substitute); `docs/research/manga_craft/index.md` (schema confirmation); `config/manga/manga_pacing_by_genre.yaml` `healing:` entry (proxy pacing data, adapted in §3); `config/manga/canonical_genre_list.yaml` `slice_of_life` row (`pacing_proxy: healing`, taxonomy-only); `config/manga/main_character_interaction_grammar.yaml` `slice_of_life: {quality_gate_checks: [relationship_or_self_interaction]}`; `docs/agent_prompt_packs/20260723_manga_48ep_3catalog_series/arc_plans_all_genres/romance_and_slice_of_life.md` (worked slice_of_life brand examples, `relational_calm_iyashikei` / `night_reset_healing`, skimmed for context per assignment); WebSearch on *Yotsuba&!* (Kiyohiko Azuma, Yen Press), *K-On!* (kakifly, Houbunsha), *Nichijou* (Keiichi Arawi, Kadokawa), *Barakamon* (Satsuki Yoshino, Square Enix), *Non Non Biyori* (Atto, Media Factory) — series structure, ensemble cast conventions, and demographic reception.*
