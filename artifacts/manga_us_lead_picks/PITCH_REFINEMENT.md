# Pitch Refinement — Notes from a Re-Read After Drafting Chapter 1s

After writing all 13 chapter 1 scripts, I went back through `PITCHES.md` and noted what wants tightening. The pitches were written before the chapters; the chapters surfaced what was working and what was speculative.

## Strong as-is — no changes needed (8/13)

| # | Brand | Why it landed |
|---|---|---|
| 1 | body_memory | Yui's silence + the client-as-mirror is a clean unforced engine. The teacher (Omote Sensei) earned the lineage word *misogi* without exposition. |
| 4 | devotion_path | Riz's reach is a single physical action that carries the whole arc. The Sai Maa cameo without dialogue is exactly right for shonen. |
| 5 | digital_ground | The trained-out voice is a 2026-pitch-perfect Gen Z premise. Miki's "what did they take from you" hits in three words. |
| 7 | qi_foundation | The cracked foundation is a literal manifestation of the metaphysical premise. Master Feung never has to argue. |
| 8 | relational_calm | The "witnessed solitude" service category Mio invents at the end is a real product idea. The pitch is also a brand strategy memo. |
| 11 | somatic_wisdom | Pamela's *"I'm not going to give you a protocol. I'm going to give you permission"* — the cleanest single line across the 13 scripts. |
| 12 | stillness_press | Already the format reference. Ahjan's `where do you live in your body` is the core question of the entire imprint. |
| 13 | warrior_calm | Master Wu's `your calm is not real — it is a held breath` is shonen-ready and tradition-accurate at once. |

## Wants minor tightening (4/13)

### 2 · bright_presence_tw — re-anchor teacher
**Issue:** the brand profile lists `teacher: adi_da` which predates the current Pearl Prime roster (per CLAUDE.md memory: *adi_da teacher atoms lack depth-tagged variants — currently xfailed*). Chapter 1 leaned on a generic "old man at a tea stall" voice and the named teacher (Ra) doesn't appear yet.
**Fix:** in pitch and chapter 2, formally re-anchor to **Ra** (Advaita Vedanta — same nondual register Wei needs). The tea-stall old man is Ra in disguise; reveal in chapter 2. This also resolves the pre-existing roster gap noted in `tests/test_teacher_mode_e2e_smoke.py`.

### 3 · cognitive_clarity — series_id is wrong
**Issue:** the catalog index lists this brand's lead as `battle_shonen_template_001` — that's a template placeholder name, not a real series id. The brand profile is `cognitive_clarity_seinen.yaml` (note: seinen, not shonen) but the chapter and pitch reads as shonen.
**Fix:** decide the lane. Recommendation: keep my chapter 1 (shonen with esports) — Kenji at 16 is the right reader-age for the brand's mental-clarity message. Rename the series to `cognitive_clarity_shonen` in the catalog index. Update the brand profile to add a shonen lane alongside the existing seinen one, since cognitive clarity sells across both age bands.

### 6 · heart_balance — geographic recheck
**Issue:** Layla in Dubai works for the South Indian Sufi register (Ma'at's tradition is dargah-rooted in Tamil Nadu, with a Gulf-diaspora reading audience), but the qawwali concert beat may read more authentic in Hyderabad or Chennai. Dubai works for the demo (UAE has a large South Asian diaspora) but is one geographic step off the source.
**Fix:** keep Dubai for the demographic cross-pollination value but ensure the qawwali concert in chapter 1 is a touring South Indian troupe, not a Pakistani qawwal — this is a Ma'at-tradition show. One-line change in the page-8 shot list.

### 10 · sleep_restoration — patient is too convenient
**Issue:** Master Sha appearing in Marina's ER as a patient is a strong dramatic beat but reads slightly engineered. He is 78, in São Paulo, refusing sedation, with the exact teaching she needs. Edges close to magical-realist convenience.
**Fix:** ground the encounter. Make Master Sha a real visiting teacher who collapsed at a community event and was brought to the ER — not a coincidence drop-in. Marina is on shift. The community group following him to the hospital adds texture. One paragraph addition to the premise.

## Wants a full re-pitch (1/13)

### 9 · relational_calm — actually fine, scratch this
On re-read it's strong. Initial draft note was a false alarm. No change.

(Kept this section so the structure is honest — when 13 pitches all need work, that means the bar was wrong. Calling that out.)

## Cross-cutting: 2 things every pitch should add

1. **Chapter count target.** Each pitch should declare how many chapters per arc and total. Default proposal: 6–8 chapters per arc × 5 arcs = 30–40 chapter run. Webtoon-native release schedule: 1 chapter/week per series. Means a 30–40 week first season per brand.
2. **Practice integration cadence.** Each chapter must surface the brand's practice (from `assemble_v52.py` TEACHER_DB) at least once — not as a how-to scene but as a moment a character considers, refuses, or finally tries it. I implemented this in the chapter 1s. The pitch deck should make it explicit so the script-writer (whether me or Pearl Star) doesn't drop it.

## What this means for the rollout

- All 13 pitches are publish-ready with the small revisions above.
- All 13 chapter 1 scripts are written and don't need Pearl Star.
- Pearl Star is no longer a blocker for the script content — only for downstream chapters 2+ once we scale.
- The remaining real blocker is **ComfyUI + image bank** for panel rendering. That's a tooling/credentials problem, not a creative problem.
