# Manga / Webtoon / Graphic Novel Craft Style Bibles

Per-lane style bibles for 48-volume series planning and deterministic panel-level script generation. Each lane file follows a standard 10-section schema (market contract, visual grammar, pacing, dialogue, character, failure modes, 48-volume implications, panel scaffolding fields, three canonical opening examples, references).

## Lanes

1. **[iyashikei_minimalism](iyashikei_minimalism.md)** — Healing/slice-of-life josei register (Mushishi, Yokohama Kaidashi Kikō, Aria). Low-arousal atmospheric work; volumes are seasonal cycles, not arcs.
2. **[josei_adult_memoir](josei_adult_memoir.md)** — Diaristic autobiographical manga (Nagata Kabi, Asano's *Solanin*). Caption-dense confessional; resists transformation arcs.
3. **[seinen_psychological](seinen_psychological.md)** — Adult psychological drama (Punpun, *A Silent Voice*). Moral ambiguity, withheld resolution, symbolic-substitution grammar.
4. **[shojo_romance](shojo_romance.md)** — Relationship-ladder romance (Fruits Basket, Kimi ni Todoke). Delay engine; long proximity arcs with ornamental mood-tone fields.
5. **[shonen_encouragement](shonen_encouragement.md)** — Craft/vocation manga (Blue Period, Sweat and Soap, Hikaru no Go). Technical-vocabulary honesty; practice as narrative engine.
6. **[webtoon_vertical_romance](webtoon_vertical_romance.md)** — Korean vertical-scroll romance (Lore Olympus, True Beauty). Color-mood-field storytelling, episodic hook cadence, season cliffs.
7. **[webtoon_vertical_drama](webtoon_vertical_drama.md)** — Korean vertical-scroll action/mystery (Tower of God, Bastard pacing). System-fiction captions, POV rotation, arc-per-season escalation.
8. **[BL_slice_of_life](BL_slice_of_life.md)** — Adult queer slice-of-life (Given, My Brother's Husband). Domestic-particular grammar; mutual-intimacy register; homophobia handled with specificity.
9. **[graphic_novel_us_literary](graphic_novel_us_literary.md)** — Western literary memoir graphic novels (Fun Home, Persepolis, This One Summer). Essayistic captions, non-linear memory, single-book completeness.
10. **[kodomomuke_educational](kodomomuke_educational.md)** — Children's encouragement + somatic-literacy (Doraemon, Chi's Sweet Home). Warm resolution per chapter, named body-feelings, caregiver-friendly read-aloud register.

## How to use

- **For 48-volume pre-planning:** read Section 7 of the relevant lane first; each lane gives a concrete 48-volume arc shape.
- **For deterministic panel scripting:** Section 8 lists the 6–9 required panel fields per lane. Scripts should emit these fields per panel; downstream artist/image-gen handoff uses this as the contract.
- **For stylistic tuning:** Section 9's three canonical openings are voice reference. Section 6 lists failure modes to lint against.
- **For quantitative targets** (panels/page, silent-panel ratio, ink density, etc.): Section 2.

## Cross-lane notes

- **Iyashikei vs josei memoir:** both are quiet lanes but have opposite dialogue/narration ratios. Don't confuse them.
- **Shojo romance vs webtoon vertical romance:** core beats overlap but format grammar is entirely different (panel grid vs vertical scroll; B&W+tone vs full color; flower-tone vs color-register).
- **Seinen psychological vs literary graphic novel:** both permit heavy interior work; seinen uses visual symbolic substitution where literary GN uses essayistic caption.
- **Kodomomuke vs iyashikei:** both are low-threat, but kodomomuke resolves per-chapter warmly with named feelings; iyashikei leaves feelings un-named and returns to atmospheric baseline.

## Canonical 48-volume shapes summary

| Lane | 48-vol shape | Volume unit |
|---|---|---|
| iyashikei | 12 × 4-vol seasonal cycles | seasonal bouquet |
| josei memoir | diaristic serial, 12yr window, retrospectives at vols 8/16/24/32/40/48 | life-quarter |
| seinen psych | 4 × 12-vol psychological eras | one life-stage |
| shojo romance | 6–8 multi-vol relationship arcs | one ladder-rung |
| shonen encouragement | 4 × 12-vol career eras (apprentice → master-as-doubt) | one practice cycle |
| webtoon romance | 48 seasons × ~25 episodes (~1,200 eps) | season |
| webtoon drama | 48 arcs, each 20–30 eps, 4-stage cosmology | arc/floor |
| BL slice-of-life | 4 × 12-vol couple arcs + aging coda | relationship stage |
| literary GN | 48 thematic-artifact single volumes | one artifact/theme |
| kodomomuke | age-progressive 4 × 12-vol bands (5–7, 7–9, 9–11, 10–12) | age-register |
