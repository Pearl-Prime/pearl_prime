# Sci-Fi / Cyberpunk — Style Bible

Touchstones: *Akira* (Ōtomo Katsuhiro), *Ghost in the Shell* (Shirow Masamune), *BLAME!* (Nihei Tsutomu), *Battle Angel Alita* (Kishiro Yukito), *Dorohedoro* (Hayashida Q). Neon Genesis Evangelion for identity-collapse / mecha adjacency.

## 1. Market contract

Readers are adults 25–40, skewing male, skewing tech-industry adjacent: developers, system architects, digital-native workers who recognize themselves in a protagonist defined by what they have optimized and what the optimizing has cost them. They show up for *cognitive density, body-as-machine metaphors, and the question of whether the self survives the system* — not for action spectacle alone. They will accept slow chapters, heavy narration, and unresolved arcs; they will reject: hollow nihilism with no character anchor, world-building that never connects to inner experience, and tech-jargon deployed as decoration. The `digital_ground` persona ("the developer who optimized everything except themselves") and the `cognitive_clarity` ADHD/burnout/focus payload must be carried inside the genre shell, invisible as therapy, legible as story.

## 2. Visual rules

- **Panels per page:** 6–9 grid-dominant (Nihei uses 7–9 tight cells; Shirow uses 6 with technical overlay insets). Asymmetric grids for cognitive disruption beats; single bleed panel for environmental scale reveals.
- **Words per page:** 50–130. Technology-as-mirror sequences can drop to 10–20 for full-spread machine environments; dialogue-heavy existential beats can reach 150.
- **Dialogue-to-caption ratio:** 40:60. High narration density is the genre's signature.
- **Black-fill ratio:** 0.45–0.65. High contrast neon-noir convention: deep blacks anchor the page; neon accent (cyan, magenta, acid green) bleeds through seams, circuit-trace screentone, UI overlays. BLAME!'s megastructure ink-density is the ceiling reference.
- **Silent-panel ratio:** 15–25%. Silences are machine silences — a server room humming, a cursor blinking. Silence here signals *the system is still running while the human has stopped.*
- **Screentone use:** UI overlay layers (translucent hex grids, status bars, scan-line patterns), mechanical hatching for armor/chassis detail, gradient tone for neon bleed. Avoid natural-texture tones unless used for ironic contrast.
- **Mechanical detail density:** High for establishing shots and protagonist-body augmentation panels; compressed to silhouette for action sequences (Ghost in the Shell approach).
- **Line weight:** Heavy contour on mechanical and architectural elements; medium-fine on human faces (the gap reads as body-machine dissonance).
- **Typography:** Sharp angular display fonts — geometric precision and cut terminals signal technological cold. DotGothic16 or pixel-art-derived fonts for UI text overlays and system-prompt fragments.

## 3. Pacing

- **Info-dense world-building front-load:** Volumes 1–3 establish the system's logic through environmental immersion, not lecture. Choose one epistemological contract and hold it.
- **Technology-as-mirror moments:** Every third chapter minimum must redirect technological description back to protagonist inner experience. The surveillance grid is the protagonist's relationship to being observed. The exo-body upgrade is the question of where self ends and hardware begins.
- **Chapter length:** 20–35 pages. Dense-grid chapters read shorter experientially.
- **Chapter hook family:** System-anomaly first — open on a glitch, a scan result that doesn't resolve, an error in the feed. The reader's entry is always a rupture in the machine's logic.
- **Chapter ending convention:** Ambiguous escalation — close on a question in the protagonist's terminal, a half-decrypted message, a body-status readout that shows something wrong.
- **Per-volume arc shape:** Ascent into system → confrontation with system logic → integration or rejection. Vol. 1–4: protagonist learns the system's rules by surviving them. Vol. 5–8: the cost surfaces in body and narration. Vol. 9–12: choice between optimizing further or recovering what the optimization consumed.

## 4. Dialogue

- **Register:** Technical + existential in the same sentence. The work vocabulary (deployment, protocol, latency, threshold, rollback) and the underlying panic it is papering over. The genre's signature line sounds like documentation but is actually grief.
- **System-prompt fragments:** Caption boxes can carry text formatted as machine output: `> process suspended`, `> identity verification: FAILED`, `> override requested`. Narration from the system's perspective, which may not align with the protagonist's self-perception.
- **UI text overlays:** Diegetic HUD elements — body-temperature readout, network ping, cognitive-load percentage. Every UI element is a question about what is being measured and whether the measurement is honest.
- **High narration density:** First-person internal monologue in the seinen register: long, philosophical, self-interrupting. The protagonist's narration should contain more doubt than their dialogue.
- **AI character speech:** Slightly wrong affect — the AI is too cooperative, the system too certain, the human too efficient. That wrongness is where dread lives.

## 5. Character

- **Protagonist archetypes:** Hacker, developer, cyborg, test subject, augmented laborer. Unifying trait: their body or cognition has been modified to serve a system — and the story is whether they reclaim it. Motoko Kusanagi (Ghost in the Shell) is the model: supreme competence in the machine, profound uncertainty about the self beneath. The `digital_ground` persona translates this directly.
- **Supporting characters:** The AI or system that asks real questions (Puppet Master, HAL-adjacent but non-villainous); colleagues who have made the opposite choice (full integration vs. full rejection); a "civilian" character who has not been augmented and represents what was given up.
- **Antagonist:** The faceless system or its human proxy — a manager who speaks in metrics, a corporation that owns the protagonist's modification patents. The antagonist has no face in volumes 1–4; face-reveal is a mid-series event.

## 6. Failure modes

1. **World-building over character** — thirty pages of infrastructure detail with no protagonist inner experience. The megastructure is only interesting as a mirror.
2. **Tech-jargon as prose decoration** — vocabulary deployed to signal genre without earning meaning.
3. **Nihilist endings with no earned cost** — the system wins and the reader learns nothing.
4. **Action-sequence inflation** — cyberpunk is a thinking genre; extended fight choreography without cognitive-load narration is wrong-register.
5. **The AI/system as simple villain** — flattening the system into a monster removes the genre's central tension (the protagonist's complicity).
6. **Protagonist competence with no cost** — burnout and cognitive degradation must be visible in the body and in the narration.

## 7. 48-volume shape

Macro-structure runs on system → glitch → revelation → restructure cycles, 12 volumes each:

- **Vol. 1–12 (System):** Protagonist enters or is already inside the system; its logic seems operational. Glitch events small and deniable. Cycle ends with first un-deniable anomaly.
- **Vol. 13–24 (Revelation):** System's full architecture revealed — designers, costs, relationship to protagonist's specific modification. The revelation is not that the system is evil; it is that it was always indifferent. Cycle ends with structural rupture.
- **Vol. 25–36 (Restructure):** Protagonist tries to operate inside a modified version of the system, or builds an alternative. Every previous supporting character revealed to have been navigating their own version of the same choice.
- **Vol. 37–48 (Integration or rejection):** Either the protagonist redesigns their relationship to the system (Evangelion Third Impact model) or exits it entirely (Alita model). Neither is a simple victory. Final volume closes on a body-status readout that reads differently than vol. 1's equivalent panel.

## 8. Panel scaffolding

Per-panel fields (9):

1. `framing` — ELS / LS / MS / MCU / CU / insert / environmental-insert / ui_overlay_insert (HUD/status element as own panel)
2. `beat_role` — one of {system_anomaly, world_establish, tech_mirror, existential_beat, action_sequence, ui_data_reveal, silent_machine, protagonist_narration, system_dialogue}
3. `subject` — what is in frame (character + environment + machine element)
4. `dialogue` — ≤20 words; technical register permitted; null for machine-silent panels
5. `caption` — ≤35 words; philosophical-narration register; system-prompt format permitted (`> text`)
6. `ui_overlay_present` — boolean; if true, type (hud / scan / status_bar / error_prompt / hex_grid)
7. `system_prompt_text` — machine-voice narration distinct from protagonist narration; ≤20 words; null if not present
8. `technology_layer` — mechanical_detail / circuit_screentone / augmentation_visible / environment_only / human_dominant; affects line weight and fill directives
9. `silence_flag` — boolean; true = no dialogue, no protagonist caption (system prompts may remain); true required on ≥20% of panels

Constraint hints: `ui_overlay_present=true` on ≥1 panel per chapter; `tech_mirror` beat on ≥1 panel per 5 panels; consecutive `action_sequence` beats ≤4 without `protagonist_narration` or `existential_beat` interruption.

## 9. Locale weighting

| Locale | Weight | Rationale |
|---|---|---|
| `en_US` | Primary | Tech-worker burnout persona dominant; `digital_ground` brand core audience; "developer who optimized everything except themselves" recognizable archetype in US tech culture |
| `ja_JP` | High | Cyberpunk tradition ownership — Akira, Ghost in the Shell, BLAME! are JP-originated; seinen readership primed for philosophical density; Monthly Afternoon / ComicWalker platform fit |
| `zh_CN` | Resonant (gray-zone per D-19) | Rapid urbanization and tech-sector pressure create structural parallels; cyberpunk strong on Bilibili Comics; regulatory: frame as "cognitive clarity" and "human resilience," not "system critique"; AI disclosure required |
| `ko_KR` | Crossover (rendered + held per D-18) | Webtoon-cyberpunk established KR subgenre; vertical-scroll format requires panel-scaffold adaptation; thematic payload transfers directly |

## 10. Cover design notes

Black + electric blue or black + acid green is the primary cyberpunk palette cluster. Sharp angular display fonts. Face-to-cover ratio: 20–25%, three-quarter or frontal with visible augmentation detail (lens overlay, neural port, scar-grid). UI element inset in lower third — the cover's design includes one diegetic HUD element as brand mark. Protagonist faces viewer directly; the system element does not.

---

*Sources: `docs/CJK_CATALOG_PLAN.md` (Sci-Fi/Cyberpunk Tier §5; Genre Shell revenue table §1; locale format table §2); `artifacts/research/manga_genre_writing_styles_2026_04_04.md` (Seinen metrics §2 lines 80–136); `artifacts/research/manga_dialogue_system/02_dialogue_vocabulary_patterns.md` (Seinen register lines 82–101); `artifacts/research/manga_cover_design/04_typography_system.md` (DotGothic16 lines 184–186); `artifacts/research/manga_cover_design/09_bestseller_cover_analysis.md` (cyberpunk palette analog).*
