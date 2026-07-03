# Manga Mode-Wrapper Design — Teacher-mode XOR Music-mode, baked in by genre

**Authority status (M4, 2026-07-04):** This file is the cited authority for
`config/manga/manga_mode_vessels.yaml`. Runtime consumers (call-reachability):
`phoenix_v4/manga/mode/vessels.py` ← `story_architect.apply_mode_vessel` +
`chapter/writer._mode_vessel_prompt_block`. Research companion:
`docs/research/manga_craft/teacher_apparatus_per_genre.md`. Music×manga:
`docs/specs/MUSIC_MODE_MANGA_V1_SPEC.md`.

**Rule 0: one mode per series. Teacher-mode and music-mode are never combined.**
A manga series is the work of **one archetype** — a *teacher* (the soul is a doctrine)
or a *musician* (the soul is a sound). That choice is the series' spine, baked into
the genre through a **native vessel**, never bolted on as captions or sidebars.

This is the manga sibling of the book modes (`--teacher` / `--music-mode`), but a book
can frame in prose (a teacher pre-intro; a musician's "note from your reader"). Manga
can't narrate at the reader — the mode has to live *inside* the genre's world.

---

## The two contracts (why they can't share a story)

| | **Teacher-mode** | **Music-mode** |
|---|---|---|
| Soul | a teacher's **doctrine** | a musician's **sound** |
| Reader contract | is **taught** — earns an insight | is **made to feel** — gets an anchor, *not* an instruction |
| Voice on the page | wisdom, dramatized | feeling, scored — no explaining |
| Failure mode if mixed | the music turns the teaching into a soundtrack; the doctrine turns the music into a lecture. Each kills the other's contract. |

So: a teacher-mode story has **no musician/song vessel**; a music-mode story has **no
sage/doctrine vessel**. The genre supplies a *different* vessel for each.

---

## The vessel per genre (the wrapper)

The vessel is a thing that already belongs in the genre's world and can carry the mode
**diegetically** — a character, a force, an object, a recurring motif.

| Genre | Teacher-mode vessel (the doctrine, *taught*) | Music-mode vessel (the sound, *felt*) |
|---|---|---|
| **iyashikei** | an elder / a daily ritual whose small wisdom is the doctrine | a melody threaded through the daily world; a musician neighbor |
| **dark_fantasy** | a Keeper / oracle / the living land that *knows* | song-magic; a bard whose music holds back the dark |
| **mecha** | the mechanic who **co-regulates** the pilot (doctrine as care) | the **sync-song** — the pilot tunes the machine by finding the sound |
| **psychological_thriller** | a mentor who reads the body's tells before the mind lies | a motif that surfaces the truth one beat before the words |
| **supernatural_mystery** | a medium/elder who reads the unseen (= the body's signals) | a song only the haunted can hear |
| **romance / josei** | a wiser beloved who *models* the doctrine | a shared song; a musician beloved |
| **action_battle** | the sensei/master | the warrior's battle-rhythm; a war-drum heart |
| **sports_competition** | the coach | the team anthem; the runner's internal beat |
| **isekai** | a guide/mentor in the new world | a song that crosses worlds; bardic magic |
| **sci_fi_cyberpunk** | an AI/elder mentor | a synth-signal; the soul in the machine's hum |
| **historical_period** | a master/elder of the craft | a folk song carried down the eras |
| **school_coming_of_age** | a teacher / senpai | the music club; one song that follows the year |

---

## How it bakes in structurally (3 beats — same skeleton, opposite contract)

Mirrors the book modes' 3-position placement (open / mid / close), but as **story beats,
not inserts**:

**Teacher-mode** — the doctrine is *earned*:
1. **WOUND** — the genre dramatizes the doctrine's *absence* (the cost of not knowing it).
2. **TURN** — through a genre action (a battle lost, a clue read, a wall touched), the
   teaching *lands* — never spoken as advice; shown.
3. **RENEWAL** — "begin again." The world changes because the character now knows.

**Music-mode** — the sound *carries* the arc:
1. **OPENING motif** — the song/sound enters, establishing the feeling.
2. **MID recurrence (bestseller beat)** — the motif returns, transformed, at the pivot —
   the reader *feels* the shift before any line names it.
3. **CLOSING resolution** — the motif resolves the way a held breath does, on its own.

The mode chooses the EI author archetype too: a **teacher-author** (e.g. ahjan) for
teacher-mode; a **musician-author** for music-mode. The manga_author field already
exists per series — it just has to point at the right archetype, and the series carries
a `mode: teacher | music` flag the chapter writer reads.

---

## Demonstrations (this folder)

- `the_forest_beneath_the_skin__ep_001.chapter_script.yaml` — **teacher-mode** dark_fantasy
  (vessel = the Keeper; ahjan's body-first doctrine, *no music*).
- `the_cockpit_remembers_the_song__ep_001.chapter_script.yaml` — **music-mode** mecha
  (vessel = the sync-song; a musician-author's sound, *no teacher/doctrine*).

## To automate (manga chapter writer)

- Add `mode: teacher | music` to the series plan (XOR-validated — reject both).
- Teacher-mode: `story_architect` tags the TURN beat with a `doctrinal_anchor`; the
  chapter writer selects a matching teacher TEACHER_DOCTRINE atom and dramatizes it via
  the genre's teacher-vessel (table above).
- Music-mode: `music_overlay.plan_music_injection` targets the 3 story beats (not
  paragraphs); the lettering pass renders the musician atom as the genre's music-vessel
  (a song panel, a sound-motif caption) — never as narration.
