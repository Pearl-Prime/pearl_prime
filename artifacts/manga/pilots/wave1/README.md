# Manga Story Wave 1 — gold-reference chapter scripts (8 new genre × mode combos)

Tier-1 authored ep_001 chapter scripts (`chapter_script_writer_handoff` format) that extend the
two gold-reference pilots across the catalog's genres and prove the **teacher-mode XOR music-mode**
wrappers generalize. One mode per story, never both — see
[`../MANGA_MODE_WRAPPER_DESIGN.md`](../MANGA_MODE_WRAPPER_DESIGN.md) and
[`../GENRE_VESSEL_SKETCHES.md`](../GENRE_VESSEL_SKETCHES.md).

These are **stories** (Tier-1 prose authoring); rendering is still gated, exactly like the two
pilots. Each ~6 pages / 14–17 panels, with a `mode_beats:` block mapping pages to the 3-beat
skeleton (teacher: wound → turn → renewal; music: opening_motif → mid_recurrence →
closing_resolution).

## The wrapper contract (why a story is single-mode)
- **Teacher-mode** — the reader is **taught**. The doctrine is *earned* through a genre action,
  **shown before told** (the body acts the doctrine a beat before any line names it). The genre's
  **teacher-vessel** carries it. No musician/song vessel anywhere. `teacher_id` set; `musician_id` absent.
- **Music-mode** — the reader is **made to feel**. A sound/motif carries the arc at opening / mid /
  close. **No teacher, no doctrine line, nothing explained.** The genre's **music-vessel** carries it.
  `musician_id` set (an invented musician EI author); `teacher_id: null`.
- The wellness topic is **interior** — the genre is the facade; no clinical/self-help word ever
  appears in a title or caption.

## The 8 (4 teacher · 4 music)

### Teacher-mode (doctrine earned through the genre; reader is taught)
| # | Genre | Title | Vessel (teacher) | Interior (never on page) | Author / teacher_id |
|---|---|---|---|---|---|
| 1 | iyashikei | **The House That Warms the Cup** | the tea-house hands (the ritual; doctrine learned by *watching*, not hearing) | sleep / a body that can't go off-shift | Yuki Slowlight · ahjan |
| 2 | psychological_thriller | **The Room Reads You Back** | the detective who reads bodies (the body confesses before the mouth) | hypervigilance | Rei Calderwood · ahjan |
| 3 | romance_josei_drama | **The Weight She Set Down** | the beloved who rests (doctrine learned off another body's ease) | self-worth / love conditioned on output | Hana Tidecalm · ahjan |
| 4 | action_battle | **The Blade That Stopped Trying** | the sensei of the settled strike (lose by forcing, win by flowing) | courage / bracing mistaken for strength | Kaito Stillwater · ahjan |

### Music-mode (sound carries the arc; reader is made to feel)
| # | Genre | Title | Vessel (music) | Interior (never on page) | Author / musician_id |
|---|---|---|---|---|---|
| 5 | supernatural_mystery | **The Half a Lullaby** | the song only the haunted can hear (laying a spirit to rest = finishing its melody) | grief | Mizu Eveningtide · mizu_eveningtide |
| 6 | sports_competition | **The Beat Beneath the Lane** | the inner beat / team chant (the race turns when the beat re-finds itself) | imposter syndrome | Haru Kasten · haru_kasten |
| 7 | sci_fi_cyberpunk | **The Frequency They Filtered Out** | the pirate frequency, the soul in the hum (re-find the body the upgrades muted) | overthinking | Neon Aoki · neon_aoki |
| 8 | school_coming_of_age | **The Song the Year Was Set To** | the song the year is set to (growing up felt as the song maturing) | social anxiety | Sora Vesper · sora_vesper |

## Files
1. `the_house_that_warms_the_cup__ep_001.chapter_script.yaml` — TEACHER · iyashikei
2. `the_room_reads_you_back__ep_001.chapter_script.yaml` — TEACHER · psychological_thriller
3. `the_weight_she_set_down__ep_001.chapter_script.yaml` — TEACHER · romance_josei_drama
4. `the_blade_that_stopped_trying__ep_001.chapter_script.yaml` — TEACHER · action_battle
5. `the_half_a_lullaby__ep_001.chapter_script.yaml` — MUSIC · supernatural_mystery
6. `the_beat_beneath_the_lane__ep_001.chapter_script.yaml` — MUSIC · sports_competition
7. `the_frequency_they_filtered_out__ep_001.chapter_script.yaml` — MUSIC · sci_fi_cyberpunk
8. `the_song_the_year_was_set_to__ep_001.chapter_script.yaml` — MUSIC · school_coming_of_age

## QA (all 8 pass)
- valid YAML; `artifact_type: chapter_script_writer_handoff`; 6 pages each; 14–17 panels.
- single-mode: each `mode:` field set; teacher files carry no song/musician vessel on the page;
  music files carry no teacher/doctrine line on the page (XOR-verified on `teacher_id`/`musician_id` too).
- no clinical/self-help word in any title or caption; the interior topic lives only in metadata
  (`topic` / `felt_topic`) and the wrapper notes, never on the page.
- each follows the 3-beat skeleton via its `mode_beats:` block.

## Relationship to the two gold pilots (not duplicated)
The two existing pilots cover dark_fantasy=teacher
([`../the_forest_beneath_the_skin__ep_001.chapter_script.yaml`](../the_forest_beneath_the_skin__ep_001.chapter_script.yaml))
and mecha=music
([`../the_cockpit_remembers_the_song__ep_001.chapter_script.yaml`](../the_cockpit_remembers_the_song__ep_001.chapter_script.yaml)).
These 8 are all **new** genre × mode combinations; no pilot genre/mode is repeated.
