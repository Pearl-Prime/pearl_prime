# Social Issue (Social Issue / Josei Realism) — Craft Bible

Touchstones: *A Silent Voice / Koe no Katachi* (Oima Yoshitoki — disability, bullying, and social exclusion carried through a school-community lens), *Princess Jellyfish* (Higashimura Akiko — economic precarity and gender-nonconformity carried through a shared-housing found-family), *Blue Period* (Yamaguchi Tsubasa — class access to art education, carried through a single household), *Usagi Drop* (Unita Yumi — single/unconventional parenthood carried through daily domestic realism), *Ashita no Joe* (Takamori/Chiba — working-class poverty carried through a boxing-gym community; the genre's foundational proof that a real social pressure reads stronger through a specific community than through direct statement).

## 1. Market + reader contract

Readers are 20–45, majority-female-skewing (josei core) with strong crossover into general adult literary-manga readers, who come for *recognition*, not escape. The contract: a real, nameable social pressure — eldercare, single parenthood, housing precarity, disability and exclusion, class access to opportunity, informal-caregiving burnout — will be carried by specific people in a specific household, workplace, or neighborhood, and the story will not flinch from the pressure's structural cause (an institution, a policy, an economic condition) while still keeping the frame at human scale. Readers will accept slow, unglamorous, procedurally-textured chapters (a benefits form, a school meeting, a rent notice) as long as those chapters cost the characters something specific. They will reject two things on sight: a story that resolves the social pressure through a single act of individual heroism (the genre's whole point is that individual heroism is not enough), and a story that becomes a lecture — characters explaining the social issue to each other or to the reader in essay-register dialogue.

## 2. Visual rules / visual grammar

Canonical pacing data (`config/manga/manga_pacing_by_genre.yaml` → `social_issue:`):
- **words_per_page_range:** 60–100
- **words_per_balloon_max:** 30
- **silent_panel_ratio_range:** 0.25–0.45
- **reaction_shot_frequency:** medium
- **spread_frequency:** rare
- **page_turn_triggers:** revelation, status_shift, grief_beat, ambiguous_line
- **narration_tolerance:** moderate
- **sfx_usage:** minimal
- **background_density:** realist
- **reference_corpus:** *A Silent Voice*, *Princess Jellyfish*, *Blue Period*

Additional visual-grammar rules built from those touchstones:

- **Panel count per chapter:** 18–30 pages, moderate grid density (5–7 panels/page average) — denser than `iyashikei` or `seinen_psychological`, because social_issue chapters carry real procedural content (forms, schedules, shift rotations) that needs legible sequential staging, not atmospheric compression.
- **The institutional-object insert:** every chapter dealing with `status_shift` (per the page-turn-trigger list) should include at least one tight insert panel on the actual bureaucratic or economic object doing the pressuring — a benefits letter, a rent notice, a school attendance form, a hospital discharge sheet, a shift-schedule board. This is the genre's core externalization technique: the institution is rendered legible as an object the reader can read over the character's shoulder, never summarized in dialogue.
- **Background density: realist** per pacing data — unlike `iyashikei`'s ornamental backgrounds or `dark_fantasy`'s atmospheric wash, social_issue backgrounds must be specific and inhabitable: a real apartment layout, a real workplace floor plan, a real waiting-room chair arrangement. Genericized "any city" backgrounds read as evasive in this lane.
- **Community-density panels:** wide shots establishing the surrounding community/household (a shared building courtyard, a boxing gym, a school corridor, a co-op kitchen) recur at fixed intervals (roughly once per 4–6 pages) to keep the collective stakes visible — the genre resists narrowing to a single household in isolation for more than a few pages at a stretch.
- **Reaction-shot frequency: medium** — used specifically on *secondary* characters absorbing news, not just the protagonist; a social_issue chapter should show the ripple of a status_shift across at least two people's faces, establishing that the pressure is systemic, not personal to the lead alone.
- **Line weight & tone:** clean, unshowy pen line; screentone used functionally (time of day, interior/exterior) rather than expressively — Higashimura's grounded character work and Yamaguchi's material-specific rendering (paint texture, art-school interiors) are both models of craft precision in service of legibility, not stylization for its own sake.
- **Silent-panel ratio 0.25–0.45:** silence here is used for the moment *after* a status_shift lands — the beat where a character absorbs news before responding — not for atmospheric drift (that's `iyashikei`'s use of silence).
- **Spreads:** rare, reserved for `grief_beat` — a genuine loss (a person, a home, a level of independence) — never for scale or scenery.

## 3. Pacing + beat conventions

- **Chapter hook family:** *Ordinary-day-under-pressure.* Open on a routine task (a school pickup, a shift handoff, a grocery run) already carrying a visible cost from an established pressure — the reader should feel the weight before any dialogue names it.
- **Chapter ending convention:** *Ambiguous line* or *status_shift landing.* Per the page-turn-trigger list, chapters end on a piece of news, a small institutional verdict (approved/denied, kept/cut, enrolled/waitlisted), or a line of dialogue that could be read two ways — never on a triumphant resolution and never on pure despair; the genre's honesty lives in the ambiguity.
- **Scene-to-scene transitions:** hard cuts between household/individual scenes and community/institutional scenes (a family dinner cut directly to a caseworker's office) — the juxtaposition itself argues that the personal and the systemic are the same story. Time-skip captions are permitted and typically procedural in register ("Three weeks after the inspection...") rather than lyrical.
- **Per-volume arc shape:** a volume tracks one full cycle of a social pressure meeting an institutional process — introduction of the pressure, an attempt to manage it informally, an institutional intervention (welcome or hostile) that forces formalization, and a new equilibrium that is *survivable, not solved*. This pattern should repeat with rising stakes across a series rather than resolving permanently in any single volume.
- **The community as the actual protagonist across volumes:** even when a single character carries POV, the volume-to-volume health of the surrounding community/household (does it grow, shrink, fracture, reorganize) should track as its own throughline — losing sight of the collective for more than a volume risks drifting into pure family-drama register.

## 4. Dialogue + narration

- **Register:** naturalistic, class- and context-specific — a caseworker's institutional register, a teenager's clipped register, an elder's generational register should all sound distinct. Avoid a flattened "issue novel" voice where every character speaks in the same articulate register regardless of age, education, or exhaustion.
- **Narration tolerance:** moderate per pacing data — used mainly for procedural/temporal orientation (what changed, how much time passed, what an institutional decision means in practice) rather than emotional interpretation. Narration should never tell the reader how to feel about the social issue.
- **Dialogue-to-narration ratio:** ~70:30 — more dialogue-forward than `seinen_psychological`'s 75:25 by a small margin toward narration, because procedural orientation captions carry real informational weight here.
- **The anti-lecture rule:** no character may explain the social issue in general terms to another character who would already know it (a caseworker should never explain "the housing crisis" to a family living it). Information about the systemic pressure must arrive either through the institutional-object insert (§2) or through a character explaining a *specific procedural fact* the other genuinely wouldn't know (a form deadline, an eligibility rule) — never through thematic summary.
- **Tell-don't-show tolerance:** low on the emotional register (never state "she felt overwhelmed by the system") but the *procedural* facts (deadlines, eligibility, hours, pay) may and should be stated plainly — this is the inverse of `seinen_psychological`'s rule and is what keeps social_issue legible rather than opaque.
- **Silence as refusal:** a character declining to answer a caseworker's or authority figure's question, rendered as a genuinely blank beat rather than a witty deflection, is a load-bearing move in this lane — per pacing table's `ambiguous_line` trigger.

## 5. Character + arc conventions

- **Protagonist archetype:** a connector, not a savior — someone positioned at the pressure point of a household or community (a working caregiver, a young person balancing school and family duty, an informal community organizer) whose competence is real but bounded; they cannot fix the structural cause, only navigate and sometimes reshape the local response to it. Per `main_character_interaction_grammar.yaml`'s `social_issue: {quality_gate_checks: [family_care_or_authority_pressure]}`, every beat must be gated through either family/care interaction or authority-pressure interaction — a protagonist isolated from both for an extended stretch has drifted out of genre.
- **The institutional-pressure figure:** an authority character (caseworker, school administrator, landlord, HR rep, inspector) who is drawn with the same care as the family — per this catalog's general anti-pattern doctrine, never a cartoon villain. The best social_issue authority figures are constrained by their own institution's rules and sometimes want to help but cannot fully (a caseworker sympathetic but bound by policy reads truer than a caseworker who is simply cruel).
- **Supporting cast size:** medium-to-large ensemble, 5–10 recurring — social_issue is a community genre; a too-small cast collapses it into family drama or memoir register.
- **Emotional arc per volume:** manageable strain → an institutional trigger event → informal coping strategy overextends and partially fails → a formal/structural adaptation is forced → new equilibrium at a redistributed (not eliminated) load. Distribution, not elimination, is the genre's characteristic "win" shape — see the worked example in `docs/agent_prompt_packs/20260723_manga_48ep_3catalog_series/arc_plans_all_genres/procedural_medicine_family_food_social_historical.md` (`resilient_parent_social`, Arc 4: "Burnout is not eliminated — it's distributed and made survivable").
- **The person who breaks:** at least one supporting character per volume-arc should visibly reach their own limit and step back or fail at their part of the informal support structure — this is what keeps the "community as safety net" premise honest rather than idealized.

## 6. Failure modes

1. **Issue-of-the-week flattening.** Treating the social pressure as a single-chapter problem that resolves and is never mentioned again — real structural pressures recur and compound across volumes.
2. **The savior protagonist.** A protagonist whose individual competence or kindness structurally fixes the institutional problem (gets the policy changed, personally rescues the family) betrays the genre's central honesty. Fixes must be local, partial, and often temporary.
3. **Cartoon-villain authority figures.** An institutional antagonist with no coherent constraints or interior logic reads as a strawman and lets the reader off the hook of recognizing the real, banal mechanics of institutional pressure.
4. **Essay-register dialogue.** Characters explaining the social issue to each other in terms a real person in that situation would never need explained (see §4's anti-lecture rule) — the single most common and most damaging failure in this lane.
5. **Poverty/precarity as aesthetic.** Rendering hardship in a stylized, art-directed way (picturesque poverty) rather than through the specific, unglamorous procedural detail that makes it legible and true (per §2's institutional-object insert and realist background_density).
6. **Community erasure.** Narrowing to a single household's internal drama for extended stretches, losing the collective/institutional throughline that distinguishes this lane from `family` or `memoir`.
7. **Premature or total resolution.** A volume or series ending that declares the social pressure solved (rather than "distributed and made survivable," per §5) undercuts the genre's realism contract.
8. **Purity-testing the caregiver.** Punishing a character in the narrative logic for reaching their limit and stepping back (per §5's "person who breaks") — that step-back should be treated as true and human, not as a moral failure requiring narrative punishment.
9. **Silence used as evasion rather than refusal.** Using the genre's silent-panel allowance (§2, §4) to avoid actually dramatizing a hard conversation, rather than as a deliberate charged beat.

## 7. Series planning implications (48-volume pre-plan)

48 volumes of social_issue sustains well because real structural pressures are inexhaustible and multi-generational — the genre's honesty (distribution, not elimination) means the story never needs to "solve" its subject, only keep finding new, specific pressure points to carry. Shape:

- **4 × 12-volume community eras**, each keyed to a different but related social pressure moving through the same core household/community as it ages (e.g., childcare precarity in the first era becomes eldercare precarity for the same characters twelve volumes later) — the *Usagi Drop* strategy of tracking a family across a real time horizon, extended to a full community.
- Each 12-volume era should contain exactly one major institutional-formalization event (vol 5–7 of the era, per §3's "attempt to manage informally → institutional intervention forces formalization") and one "person who breaks" volume (vol 9–10) where a key supporting character's informal role fails and the community must reorganize without them.
- Volume 48 should not resolve into a fixed, permanent, "solved" community structure — it should show the community's fourth reorganization holding under a new pressure, with the protagonist now in the position the §5 "connector" figure occupied at the start of era 1, having become what once supported them.

## 8. Panel scaffolding

Per-panel fields (9):

1. `framing` — standard set plus `institutional_object_insert` (tight CU on a form/notice/schedule) and `community_wide` (establishing the surrounding household/neighborhood/workplace)
2. `beat_role` — one of {ordinary_day_pressure, institutional_trigger, informal_coping, formalization_forced, person_breaks, redistribution, status_shift, grief_beat, new_equilibrium}
3. `dialogue` — ≤30 words per pacing data; procedural facts may be stated plainly (§4); thematic summary forbidden
4. `caption` — optional, ≤25 words; procedural/temporal orientation register, not emotional interpretation
5. `background_register` — realist per pacing data; must be specific and inhabitable, never genericized
6. `institution_pressure_level` — integer 0–3 (0 = none visible, 1 = background presence, 2 = active demand, 3 = formal intervention/deadline) — tracks the authority-pressure half of the `family_care_or_authority_pressure` gate
7. `care_load_level` — integer 0–3 (0 = distributed/light, 1 = manageable, 2 = strained, 3 = overextended) — tracks the family/care half of the gate; `care_load_level=3` should trigger a `person_breaks` beat within the same chapter or the next
8. `silence_flag` — boolean; true = charged refusal/absorption beat (per §4), never evasion of a scene that should be dramatized
9. `sfx` — minimal per pacing data; ambient/domestic/institutional sfx only (a stamped form, a phone ringing, a kettle) — no expressive or decorative sfx

**Generator constraint:** `institution_pressure_level=3` may not appear without a preceding `institutional_object_insert` framing panel in the same scene; `care_load_level=3` must resolve toward `redistribution` or `person_breaks` within 6 panels, never left unaddressed for a full chapter.

## 9. Locale weighting

| Locale | Signal | Rationale |
|---|---|---|
| `ja_JP` | **Primary** | Native register for josei realism (Feel Young / Big Comic imprint territory — *Princess Jellyfish*, *Usagi Drop* lineage); institutional specifics (koseki, kaigo/eldercare insurance, hoikuen waitlists) require native-accurate detail. |
| `en_US` | **Primary** | Strong crossover with Western literary-graphic-novel readers seeking recognition-driven realism (*A Silent Voice*'s Western breakout, *Blue Period*'s class-access theme travels well); institutional specifics must be localized (US housing/benefits systems differ structurally from Japan's — do not transliterate Japanese institutional mechanics). |
| `zh_TW` | **Secondary** | Josei realism has an established readership; eldercare and housing-precarity themes resonate given comparable demographic pressures. |
| `zh_CN` | **Secondary** | Social-realism content requires careful institutional-specificity localization and gray-zone distribution review per spec D-19; single-parenthood and housing themes carry sensitivity considerations to route through standard content review. |
| `ko_KR` | **Tertiary (rendered + held)** | Webtoon vertical adaptation viable — Korean social-realism webtoons are a proven adjacent format — but requires format-adaptation pass (institutional-object insert grammar translates awkwardly to infinite-scroll without redesign) before commit. |

---

*Sources: `config/manga/manga_pacing_by_genre.yaml` (`social_issue:` entry, ~line 204–220), `config/manga/canonical_genre_list.yaml` (`social_issue` row, ~line 257, label "Social Issue / Josei Realism"), `config/manga/main_character_interaction_grammar.yaml` (`social_issue: {quality_gate_checks: [family_care_or_authority_pressure]}`, line 31), `docs/research/manga_craft/seinen_psychological.md` (structural/formatting template), `docs/research/manga_craft/dark_fantasy.md` (9-section schema confirmation), `docs/agent_prompt_packs/20260723_manga_48ep_3catalog_series/arc_plans_all_genres/procedural_medicine_family_food_social_historical.md` (`resilient_parent_social` worked example — community caregiving co-op, institutional-pressure/redistribution arc shape). WebSearch: "josei social realism manga eldercare single parenthood housing precarity manga series" (tumblr.com/read-review-and-recc, cbr.com/josei-anime-manga-underrated, en.wikipedia.org/wiki/Josei_manga — *Usagi Drop* single-parenthood/eldercare framing); "Fumi Yoshinaga josei manga social realism eldercare family caregiving craft" (en.wikipedia.org/wiki/Fumi_Yoshinaga, tokion.jp/en/2022/09/14/interview-fumi-yoshinaga — domestic-routine-as-relational-register in *What Did You Eat Yesterday?*, mother-daughter caregiving negotiation in *All My Darling Daughters*); "Ashita no Joe poverty class realism boxing manga social issue craft" (yokogaomag.com/editorial/ashita-no-joe-boxing-manga, inkandimage.wordpress.com/2018/04/15/yabuki-joe-working-class-hero — gritty-realism-over-idealized-sports-tropes craft note, working-class-community-as-vessel); "Usagi Drop single parenthood josei manga panel technique realism" (weekendotaku.wordpress.com, animepapa.com/what-is-josei-anime — daily-domestic-realism, procedural-parenting-detail craft note).*
