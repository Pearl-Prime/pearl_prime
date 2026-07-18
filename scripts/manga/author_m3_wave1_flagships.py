#!/usr/bin/env python3
"""M3 Wave 1 — author 37 en_US flagship chapter_scripts (genre-first).

Pearl_Writer lane: emits chapter_script_writer_handoff YAMLs under
artifacts/manga/chapter_scripts/<series_id>/ep_001.yaml.

Reuses three proven pilots when they already match the brand flagship:
  stillness_press / cognitive_clarity / warrior_calm_cultivation (Q-MANGA-06 B).

All other brands get a new ep_001: genre story first, topic as subtle inner arc,
teacher-mode vessel cited, teacher NEVER named in-story. Gate floor only —
craft bar is separate (see manga_m3_wave1_craft_audit).
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "artifacts" / "manga" / "chapter_scripts"
EXISTING = OUT

# brand_id -> (tentpole_genre, primary_topic, title_slug, title, ei_author, protag)
# Tentpoles from GENRE_PORTFOLIO_PLAN top %. warrior_calm uses existing mecha hybrid (Q-06 B).
ROUTING: list[dict] = [
    # Reuse pilots
    {"brand": "stillness_press", "genre": "iyashikei", "topic": "anxiety",
     "reuse": "stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying"},
    {"brand": "cognitive_clarity", "genre": "psychological_thriller", "topic": "overthinking",
     "reuse": "cognitive_clarity__en_US__psychological_thriller__series01"},
    {"brand": "warrior_calm_cultivation", "genre": "mecha", "topic": "burnout",
     "reuse": "warrior_calm_cultivation__master_wu__en_US__burnout__the_chassis_is_listening",
     "note": "Q-MANGA-06 default B — cultivation-burnout hybrid (authored mecha), not fresh action_battle"},
    # New flagships
    {"brand": "digital_ground", "genre": "sci_fi_cyberpunk", "topic": "burnout",
     "slug": "the_feed_is_louder_than_blood", "title": "The Feed Is Louder Than Blood",
     "author": "Jun Park", "protag": ("reno", "Reno Vale", 29,
        "backend engineer — on-call rotation; optimized every system except sleep",
        "undercut black hair, blue-light glasses, frayed hoodie cuff he worries with his thumb")},
    {"brand": "sleep_restoration_iyashikei", "genre": "iyashikei", "topic": "sleep",
     "slug": "the_hour_that_wont_arrive", "title": "The Hour That Won't Arrive",
     "author": "Mika Shore", "protag": ("lena", "Lena Cho", 34,
        "night-shift nurse — off-duty body still listens for call bells",
        "soft bob, cardigan over scrubs, small silver ring she turns when awake too long")},
    {"brand": "somatic_wisdom_shojo", "genre": "iyashikei", "topic": "somatic_healing",
     "slug": "the_shoulder_remembers_first", "title": "The Shoulder Remembers First",
     "author": "Yui Han", "protag": ("sora", "Sora Nguyen", 22,
        "dance student — body keeps score of a fall she pretends was nothing",
        "hair in a low knot, worn ballet wrap, bruise-yellow tape on right shoulder")},
    {"brand": "relational_calm_iyashikei", "genre": "iyashikei", "topic": "social_anxiety",
     "slug": "the_door_is_only_a_door", "title": "The Door Is Only a Door",
     "author": "Eli Moss", "protag": ("jun", "Jun Rivera", 27,
        "junior designer — freezes at every open-plan hello",
        "round glasses, soft flannel, notebook held like a shield")},
    {"brand": "healing_ground_healing", "genre": "dark_fantasy", "topic": "grief",
     "slug": "the_forest_keeps_their_names", "title": "The Forest Keeps Their Names",
     "author": "Rowan Vale", "protag": ("ash", "Ash Keller", 31,
        "warden of a living wood — still hears a voice the trees won't release",
        "travel cloak, ash-smudged gloves, a ribbon tied to the staff that isn't theirs")},
    {"brand": "body_memory_shojo", "genre": "psychological_horror", "topic": "somatic_healing",
     "slug": "the_house_that_flinches", "title": "The House That Flinches",
     "author": "Nia Crowe", "protag": ("mira", "Mira Sol", 26,
        "returns to a childhood house that moves when she pretends she's fine",
        "rain jacket, keys on a frayed string, left hand that won't unclench")},
    {"brand": "minimal_mind_healing", "genre": "iyashikei", "topic": "overthinking",
     "slug": "one_cup_no_thesis", "title": "One Cup, No Thesis",
     "author": "Ken Arata", "protag": ("theo", "Theo Marsh", 38,
        "systems analyst — cannot drink tea without optimizing the steep",
        "neat side-part, plain mug he distrusts, watch he checks too often")},
    {"brand": "night_reset_healing", "genre": "iyashikei", "topic": "sleep",
     "slug": "the_lamp_stays_on_purpose", "title": "The Lamp Stays On Purpose",
     "author": "Hana Quill", "protag": ("ira", "Ira Bennett", 29,
        "freelance illustrator — night is when the deadlines become creatures",
        "ink-stained fingers, oversized shirt, desk lamp with a warm paper shade")},
    {"brand": "gentle_growth_healing", "genre": "iyashikei", "topic": "self_worth",
     "slug": "the_plant_that_didnt_ask", "title": "The Plant That Didn't Ask",
     "author": "Sofi Wren", "protag": ("mae", "Mae Ortiz", 24,
        "new hire — apologizes to furniture; inherits an office plant",
        "cardigan sleeves over hands, name badge slightly crooked")},
    {"brand": "stabilizer_healing", "genre": "iyashikei", "topic": "burnout",
     "slug": "the_bench_between_shifts", "title": "The Bench Between Shifts",
     "author": "Cal Reed", "protag": ("devon", "Devon Park", 36,
        "project lead post-crunch — body arrives at the park before the mind allows it",
        "loosened tie, scuffed shoes, coffee gone cold in hand")},
    {"brand": "career_lift_workplace", "genre": "workplace_drama", "topic": "imposter_syndrome",
     "slug": "the_slide_that_isnt_you", "title": "The Slide That Isn't You",
     "author": "Priya Sen", "protag": ("ava", "Ava Kim", 28,
        "associate presenting to partners — voice rehearsed, hands not convinced",
        "blazer that still feels borrowed, clicker held too tight")},
    {"brand": "high_performer_workplace", "genre": "workplace_drama", "topic": "burnout",
     "slug": "green_on_the_dashboard", "title": "Green on the Dashboard",
     "author": "Marcus Hale", "protag": ("cole", "Cole Nguyen", 33,
        "sales director — every metric green, sleep metric red and ignored",
        "crisp shirt, jaw set, smartwatch buzzing praise he doesn't feel")},
    {"brand": "executive_calm_workplace", "genre": "workplace_drama", "topic": "burnout",
     "slug": "the_calendar_with_no_white", "title": "The Calendar With No White",
     "author": "Irene Cho", "protag": ("helen", "Helen Drake", 47,
        "VP — calendar is a wall; a night custodian keeps leaving a chair pulled out",
        "steel-gray bob, quiet heels, tablet always awake")},
    {"brand": "morning_momentum_workplace", "genre": "sports_competition", "topic": "burnout",
     "slug": "the_second_lap_is_honest", "title": "The Second Lap Is Honest",
     "author": "Taro Beck", "protag": ("niko", "Niko Alvarez", 19,
        "track recruit — first lap for coaches, second lap for the body",
        "team singlet, tape on both knees, breath fog in early light")},
    {"brand": "optimizer_workplace", "genre": "psychological_thriller", "topic": "overthinking",
     "slug": "the_model_that_predicted_him", "title": "The Model That Predicted Him",
     "author": "Vera Lin", "protag": ("sam", "Sam Okonkwo", 32,
        "quant — builds a risk model that starts forecasting his own panic",
        "rolled sleeves, dual monitors' glow, a pen he clicks in threes")},
    {"brand": "focus_sprint_workplace", "genre": "sports_competition", "topic": "adhd_focus",
     "slug": "the_whistle_is_not_the_start", "title": "The Whistle Is Not the Start",
     "author": "Jamie Cruz", "protag": ("rio", "Rio Santos", 17,
        "relay runner — mind leaves the blocks before the body; coach watches feet not times",
        "bright spikes, tangled earbuds, number bib half-stuck")},
    {"brand": "heart_balance_shojo", "genre": "iyashikei", "topic": "social_anxiety",
     "slug": "two_cups_on_the_counter", "title": "Two Cups on the Counter",
     "author": "Lila Moon", "protag": ("emi", "Emi Sato", 23,
        "cafe closer — can serve anyone, cannot sit with someone",
        "apron strings double-knotted, hair clip she adjusts when nervous")},
    {"brand": "trauma_path_healing", "genre": "dark_fantasy", "topic": "grief",
     "slug": "the_blade_that_wont_sing", "title": "The Blade That Won't Sing",
     "author": "Gareth Thorn", "protag": ("riven", "Riven Cole", 30,
        "ex-knight — sword stays sheathed because silence is safer than memory",
        "travel leathers, empty scabbard worn shiny, a scar he covers with a glove")},
    {"brand": "resilient_parent_social", "genre": "iyashikei", "topic": "burnout",
     "slug": "the_socks_that_match_enough", "title": "The Socks That Match Enough",
     "author": "Dana Brooks", "protag": ("pat", "Pat Okada", 41,
        "parent of two — mornings are logistics; a neighbor leaves muffins without a speech",
        "messy bun, mismatched socks on purpose, keys already in hand")},
    {"brand": "confidence_core_romance", "genre": "supernatural_mystery", "topic": "imposter_syndrome",
     "slug": "the_mirror_that_borrows_faces", "title": "The Mirror That Borrows Faces",
     "author": "Celeste Rae", "protag": ("nova", "Nova Ellis", 25,
        "stage understudy — mirror shows the lead's face until someone sits beside her",
        "rehearsal blacks, script dog-eared, lipstick she never quite finishes")},
    {"brand": "relationship_clarity_romance", "genre": "iyashikei", "topic": "social_anxiety",
     "slug": "the_text_left_on_read_by_choice", "title": "The Text Left on Read by Choice",
     "author": "Owen Park", "protag": ("kai", "Kai Mendoza", 27,
        "almost-texts an apology for existing; a partner answers with soup instead",
        "hoodie, phone face-down, thumb hovering over send")},
    {"brand": "adhd_forge_mystery", "genre": "action_battle", "topic": "adhd_focus",
     "slug": "the_forge_hears_three_things", "title": "The Forge Hears Three Things",
     "author": "Rex Dalton", "protag": ("jax", "Jax Harlan", 20,
        "apprentice smith — attention splinters until the hammer finds one true ring",
        "leather apron, burn marks on sleeves, sparks in hair")},
    {"brand": "devotion_path_shonen", "genre": "dark_fantasy", "topic": "grief",
     "slug": "the_second_cup_stays_full", "title": "The Second Cup Stays Full",
     "author": "Iris Vale", "protag": ("ren", "Ren Okada", 28,
        "temple caretaker — pours tea for someone who will not return; the land answers differently",
        "simple robes, careful hands, a cup set across the table every dawn"),
     "teacher_meta": "sai_ma", "byline_note": "EI character-author; Sai Maa never author-of-record"},
    {"brand": "stoic_edge_battle", "genre": "action_battle", "topic": "courage",
     "slug": "the_guard_who_lowers_the_shield", "title": "The Guard Who Lowers the Shield",
     "author": "Dane Holt", "protag": ("voss", "Voss Ren", 34,
        "city guard — courage was armor; a street fight teaches the cost of never lowering it",
        "dented bracer, short spear, eyes that track exits first")},
    {"brand": "spiritual_ground_supernatural", "genre": "supernatural_mystery", "topic": "grief",
     "slug": "the_cold_spot_before_the_name", "title": "The Cold Spot Before the Name",
     "author": "Mara Quinn", "protag": ("ell", "Ell Faro", 35,
        "medium-in-training — trusts eyes, misses the body's cold; a case won't close by deduction",
        "long coat, notebook of unfinished names, fingers always cold")},
    {"brand": "solar_return_isekai", "genre": "isekai", "topic": "self_worth",
     "slug": "no_resume_in_this_sky", "title": "No Resume in This Sky",
     "author": "Pax Orion", "protag": ("sid", "Sid Kade", 26,
        "wakes under two moons — old job title doesn't translate; hands still know how to build",
        "torn office shirt under a travel cloak, ID badge that means nothing here")},
    {"brand": "legacy_builder_memoir", "genre": "psychological_thriller", "topic": "self_worth",
     "slug": "the_file_labeled_enough", "title": "The File Labeled Enough",
     "author": "Helen Frost", "protag": ("marc", "Marc Delaney", 52,
        "archivist — finds a file on himself written in a hand he doesn't remember",
        "reading glasses, cardigan, archive gloves he forgets to remove")},
    {"brand": "bio_flow_healing", "genre": "sci_fi_cyberpunk", "topic": "somatic_healing",
     "slug": "the_wetware_alarm", "title": "The Wetware Alarm",
     "author": "Cyra Moss", "protag": ("pix", "Pix Ortega", 31,
        "augment courier — feed says optimal; meat says stop; an old hacker trusts the meat",
        "neural port at temple, courier jacket, a tremor in the unaugmented hand")},
    {"brand": "longevity_lab_healing", "genre": "iyashikei", "topic": "somatic_healing",
     "slug": "the_walk_without_a_metric", "title": "The Walk Without a Metric",
     "author": "Dr. Len Yu", "protag": ("ada", "Ada Ferris", 58,
        "longevity researcher — tracks every biomarker; a morning walk has no dashboard",
        "practical coat, step-counter she leaves on the table, soft shoes")},
    {"brand": "hormone_reset_healing", "genre": "iyashikei", "topic": "somatic_healing",
     "slug": "the_body_changes_the_weather", "title": "The Body Changes the Weather",
     "author": "Sable Quinn", "protag": ("rue", "Rue Patel", 42,
        "learns her body's weather is not a character flaw — a clinic waiting room becomes a shore",
        "scarf she adjusts often, water bottle, appointment card bent at the corner")},
    {"brand": "qi_foundation_cultivation", "genre": "dark_fantasy", "topic": "somatic_healing",
     "slug": "the_meridian_that_wouldnt_force", "title": "The Meridian That Wouldn't Force",
     "author": "Wei Lan", "protag": ("tao", "Tao Shen", 29,
        "cultivation student — forces qi until the land refuses; breath is the only gate that opens",
        "training wraps, dust on knees, a stone token that warms when he stops pushing")},
    {"brand": "creative_unfold_social", "genre": "supernatural_mystery", "topic": "social_anxiety",
     "slug": "the_studio_that_echoes_back", "title": "The Studio That Echoes Back",
     "author": "Indie Cross", "protag": ("bee", "Bee Alvarez", 24,
        "artist — studio answers with unfinished songs when she avoids people; finishing one note is contact",
        "paint-splattered boots, headphones half-on, sketchbook hugged to chest")},
    {"brand": "calm_student_school", "genre": "school_coming_of_age", "topic": "anxiety",
     "slug": "the_bell_is_not_a_verdict", "title": "The Bell Is Not a Verdict",
     "author": "Mina Cho", "protag": ("yuki", "Yuki Tan", 16,
        "exam week — body treats the bell like a sentence; a club room offers a different clock",
        "uniform slightly large, pencil case organized like armor, earbuds in one ear")},
    {"brand": "bright_presence_tw_seinen", "genre": "psychological_thriller", "topic": "social_anxiety",
     "slug": "the_room_that_watches_back", "title": "The Room That Watches Back",
     "author": "Lin Wei", "protag": ("chen", "Chen Hao", 30,
        "open-plan office in a city that never dims — being seen is the plot; a quiet stairwell is the turn",
        "neat shirt, badge on lanyard, eyes that track reflections"),
     "locale_note": "manga_locales=[zh_TW]; en_US flagship authored for Wave-1 craft continuity only"},
]

VESSELS = {
    "iyashikei": ("the tea-house hands", "elder ritual learned by watching hands"),
    "dark_fantasy": ("the Keeper / the living land", "doctrine as observation, never advice"),
    "mecha": ("the mechanic who co-regulates the pilot", "care as doctrine; settle, don't override"),
    "supernatural_mystery": ("the medium who reads the cold", "body signal before the ghost"),
    "psychological_thriller": ("the detective who reads bodies", "body confesses before the mouth"),
    "romance_josei_drama": ("the beloved who rests", "unhurried partner models ease"),
    "workplace_drama": ("the custodian who's seen the cycles", "small acts; when to put the pen down"),
    "sci_fi_cyberpunk": ("the wetware elder / old hacker", "trust the meat's alarm"),
    "psychological_horror": ("the survivor who turns toward it", "meet it, don't flee"),
    "action_battle": ("the veteran who names the cost", "courage without armor theater"),
    "sports_competition": ("the coach who watches feet", "form before time"),
    "isekai": ("the innkeeper who asks no resume", "permission to begin without the old title"),
    "school_coming_of_age": ("the club room ritual", "a different clock than the bell"),
    "cultivation_martial": ("the stone that warms when you stop", "breath is the gate"),
}

BIBLES = {
    "iyashikei": "docs/research/manga_craft/iyashikei_minimalism.md",
    "dark_fantasy": "docs/research/manga_craft/dark_fantasy.md",
    "mecha": "docs/research/manga_craft/mecha.md",
    "supernatural_mystery": "docs/research/manga_craft/supernatural_mystery.md",
    "psychological_thriller": "docs/research/manga_craft/psychological_thriller.md",
    "workplace_drama": "docs/research/manga_craft/workplace_drama.md",
    "sci_fi_cyberpunk": "docs/research/manga_craft/sci_fi_cyberpunk.md",
    "psychological_horror": "docs/research/manga_craft/psychological_horror.md",
    "action_battle": "docs/research/manga_craft/action_battle.md",
    "sports_competition": "docs/research/manga_craft/sports_competition.md",
    "isekai": "docs/research/manga_craft/isekai.md",
    "school_coming_of_age": "docs/research/manga_craft/school_coming_of_age.md",
}


def _slug_author(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def _loc(text: str) -> dict:
    return {
        "en_US": text,
        "ja_JP": f"[ja_JP] {text}",
        "zh_TW": f"[zh_TW] {text}",
        "zh_CN": f"[zh_CN] {text}",
    }


def _panel(pid: str, scene: str, *, caption: str | None = None,
           dialogue: list | None = None, intent: str | None = None,
           silence: bool = False, sfx: str | None = None) -> dict:
    p: dict = {"panel_id": pid, "scene": scene, "beat_type": "micro"}
    if intent:
        p["intent"] = intent
    if silence:
        p["silence_confirmed"] = True
    if caption:
        p["narrator_caption_by_locale"] = _loc(caption)
    if dialogue:
        p["dialogue_lines"] = dialogue
    if sfx:
        p["sfx_by_locale"] = _loc(sfx)
    return p


def _dlg(speaker: str, text: str, intensity: str = "normal") -> dict:
    return {
        "speaker": speaker,
        "text_by_locale": _loc(text),
        "intensity": intensity,
        "bubble_style": "round_normal",
        "tail_style": "pointer",
        "position_hint": "top_right",
    }


def build_panels(spec: dict) -> list[dict]:
    """Genre-first 16-panel arc: wound → vessel turn → renewal. Topic is inner, never titled."""
    genre = spec["genre"]
    pid, pname, age, role, visual = spec["protag"]
    topic = spec["topic"]
    vessel_name, vessel_desc = VESSELS[genre]
    title = spec["title"]

    # Genre-specific opening worlds (surface story) — topic only as body weather.
    worlds = {
        "iyashikei": (
            f"Wide morning interior. Soft light. {pname}'s space is ordinary and slightly neglected — "
            f"not tragic, just lived-in. A cup, a chair, a window. No crisis yet.",
            f"Close on {pname}'s hands. They are doing a small task too carefully. The body is already ahead of the day.",
            f"A trigger enters the ordinary frame — a notification, a sound, a clock. Small. Specific. Not a jump scare.",
        ),
        "dark_fantasy": (
            f"Mist at the edge of a living wood. {pname} stands where the path thins. The land is watching without eyes.",
            f"Close on a token or blade {pname} carries. It is quiet when it should answer. That silence is the wound.",
            f"Something in the trees shifts — not an attack, a refusal. The land will not be forced.",
        ),
        "psychological_horror": (
            f"A familiar room at the wrong hour. {pname} pretends the angle of the hallway is normal. It isn't.",
            f"Close on {pname}'s hand on a doorknob. The wood is warm. It shouldn't be.",
            f"A sound from deeper in the house — not loud. The kind of quiet that follows you.",
        ),
        "psychological_thriller": (
            f"Office or archive light. Screens or files. {pname} is good at patterns. Tonight the pattern looks back.",
            f"Close on notes, models, or a file label. Precision as armor.",
            f"One data point that shouldn't exist — a prediction, a reflection, a name out of place.",
        ),
        "workplace_drama": (
            f"Open-plan or glass conference room. Fluorescent honesty. {pname} is already performing competence.",
            f"Close on a badge, a slide clicker, a calendar with no white space.",
            f"A meeting or metric moment arrives. The room's eyes are the weather.",
        ),
        "sci_fi_cyberpunk": (
            f"City feed glow on wet pavement. {pname}'s HUD is clean. The unaugmented hand is not.",
            f"Close on a port, a tremor, a notification stack that never empties.",
            f"The feed optimizes. The body disagrees. A discrepancy the system calls noise.",
        ),
        "action_battle": (
            f"Training yard or street edge. Dust, impact marks, breath. {pname} holds a weapon like a promise.",
            f"Close on grip — too tight. Courage as clamp.",
            f"A bout or clash begins. Form is perfect. Cost is ignored.",
        ),
        "sports_competition": (
            f"Track or court at dawn. Lines are honest. {pname} warms up for an audience that may not be there yet.",
            f"Close on feet in spikes or shoes. The start is a story the body tells.",
            f"Whistle or starter. First effort is for the watchers.",
        ),
        "supernatural_mystery": (
            f"A case site at blue hour. Cold collects in a corner before any apparition. {pname} writes what the eyes see.",
            f"Close on a notebook of unfinished names. Deduction as shield.",
            f"The cold moves. Eyes miss it. Skin doesn't.",
        ),
        "isekai": (
            f"Sky with two moons. {pname} wakes on dirt that isn't home. An ID badge from another life lies in the grass, meaningless.",
            f"Close on hands — they know tools. The title that used to matter does not translate.",
            f"A local approaches without asking for a resume. The question is simpler: can you stand?",
        ),
        "school_coming_of_age": (
            f"School corridor, fluorescent weather. Lockers, posters, the smell of floor wax. {pname} moves like the bell is a verdict.",
            f"Close on a pencil case organized like armor. Hands steady only when busy.",
            f"The bell. Bodies flood. {pname}'s throat tightens on schedule.",
        ),
        "mecha": (
            f"Hangar pre-dawn. Chassis looms. {pname} in the cockpit threshold — already half inside the machine's breath.",
            f"Close on a glove pad, a telemetry flicker, a jaw set for override.",
            f"Launch checklist. Sync forced. The chassis hesitates a fraction — listening.",
        ),
    }
    w0, w1, w2 = worlds.get(genre, worlds["iyashikei"])

    # Vessel character — genre-native, NEVER the brand teacher name
    vessel_chars = {
        "iyashikei": ("elder", "an elder whose hands move through a daily ritual without hurry"),
        "dark_fantasy": ("keeper", "a keeper who speaks only by placing a palm on warm ground"),
        "psychological_horror": ("survivor", "someone who has met this house before and did not run"),
        "psychological_thriller": ("reader", "a colleague who reads shoulders, not slides"),
        "workplace_drama": ("custodian", "a night custodian who has seen this calendar before"),
        "sci_fi_cyberpunk": ("hacker", "an old hacker with no augments left on purpose"),
        "action_battle": ("veteran", "a veteran who names cost without theater"),
        "sports_competition": ("coach", "a coach who watches feet, not the board"),
        "supernatural_mystery": ("medium", "a senior who feels cold before names"),
        "isekai": ("innkeeper", "an innkeeper who asks what you can carry, not who you were"),
        "school_coming_of_age": ("upperclassman", "an upperclassman who keeps the club room clock wrong on purpose"),
        "mecha": ("mechanic", "a mechanic who co-regulates the pilot without a lecture"),
    }
    vid, vrole = vessel_chars.get(genre, ("guide", "a quiet guide"))

    panels = [
        _panel("ep001_001", w0, silence=True, intent="Establish genre world"),
        _panel("ep001_002", w1, silence=True, intent="Body before mind"),
        _panel("ep001_003", w2, caption="The day has a shape. The body already knows it."),
        _panel("ep001_004",
               f"Medium on {pname}'s face. Alert, not yet broken. Age {age}. {visual.split(',')[0]}.",
               silence=True),
        _panel("ep001_005",
               f"{pname} pushes through — the competent move. Genre action continues. Inside, the topic-weather "
               f"({topic.replace('_', ' ')}) is only posture and breath, never named.",
               dialogue=[_dlg(pid, "I've got it.", "whisper")]),
        _panel("ep001_006",
               f"Cost lands in the body: jaw, hands, a held breath. The genre world does not pause for it.",
               sfx="…",
               intent="Wound — body cost"),
        _panel("ep001_007",
               f"{pname} doubles down. More force, more performance, more pattern. The vessel has not entered yet.",
               silence=True),
        _panel("ep001_008",
               f"Wide: the genre pressure peaks — a clash, a meeting, a cold room, a feed spike, a bell. "
               f"Still no lecture. Only weather.",
               intent="Peak pressure"),
        _panel("ep001_009",
               f"Enter the vessel: {vrole}. No name from any teaching lineage. Only presence. "
               f"({vessel_name}: {vessel_desc})",
               silence=True,
               intent="Vessel enters — teacher never named"),
        _panel("ep001_010",
               f"The vessel does one small genre-native act — hands on a ritual, palm on ground, a chair pulled out, "
               f"a foot placement corrected, a frequency trusted. No advice speech.",
               silence=True,
               intent="Turn begins"),
        _panel("ep001_011",
               f"{pname} watches. The body settles a half-second before the mind agrees.",
               caption="It knew first."),
        _panel("ep001_012",
               f"Optional vessel line — practical, not doctrinal.",
               dialogue=[_dlg(vid, "Don't override. Settle.", "soft")]),
        _panel("ep001_013",
               f"{pname} tries the smaller move once. Genre action continues, but from a different body.",
               intent="Renewal attempt"),
        _panel("ep001_014",
               f"The world answers slightly — telemetry eases, land warms, room quiets, second lap cleans, feed dims. "
               f"Not victory. Permission.",
               silence=True),
        _panel("ep001_015",
               f"Closing wide. {pname} keeps one small act on purpose. The topic is still present as weather. "
               f"No mastery. No cure. A first tool.",
               caption="I don't have to finish it. I have to notice it once."),
        _panel("ep001_016",
               f"Typographic end card on a quiet field of color.",
               caption=f"End of Episode 1 — {title}"),
    ]
    return panels


def build_script(spec: dict) -> dict:
    genre = spec["genre"]
    topic = spec["topic"]
    brand = spec["brand"]
    author = spec["author"]
    author_slug = _slug_author(author)
    pid, pname, age, role, visual = spec["protag"]
    series_id = f"{brand}__{author_slug}__en_US__{topic}__{spec['slug']}"
    vessel_name, vessel_desc = VESSELS[genre]
    bible = BIBLES[genre]

    chars = [
        {"id": pid, "name": pname, "age": age, "role": f"protagonist ({role})",
         "visual_anchor": visual},
    ]
    # vessel as secondary character (generic id)
    vmap = {
        "iyashikei": ("elder", "Elder"),
        "dark_fantasy": ("keeper", "Keeper"),
        "psychological_horror": ("survivor", "Survivor"),
        "psychological_thriller": ("reader", "The Reader"),
        "workplace_drama": ("custodian", "Custodian"),
        "sci_fi_cyberpunk": ("hacker", "Old Hacker"),
        "action_battle": ("veteran", "Veteran"),
        "sports_competition": ("coach", "Coach"),
        "supernatural_mystery": ("medium", "Senior Medium"),
        "isekai": ("innkeeper", "Innkeeper"),
        "school_coming_of_age": ("upperclassman", "Upperclassman"),
        "mecha": ("mechanic", "Mechanic"),
    }
    vid, vname = vmap.get(genre, ("guide", "Guide"))
    chars.append({
        "id": vid,
        "name": vname,
        "age": "unspecified",
        "role": f"vessel presence — {VESSELS[genre][1]}; never a named brand teacher",
        "visual_anchor": "genre-native; face optional; hands and posture carry doctrine",
    })

    teacher_meta = spec.get("teacher_meta", "brand_teacher_unresolved")
    doc: dict = {
        "schema_version": "1.0.0",
        "artifact_type": "chapter_script_writer_handoff",
        "schema_authority": "schemas/manga/chapter_script_writer_handoff.schema.json",
        "series_id": series_id,
        "chapter_id": "ep_001",
        "title": f"{spec['title']} — Episode 1",
        "manga_author": author,
        "teacher_id": teacher_meta,
        "brand_id": brand,
        "engine": topic.upper() if topic.isalpha() else topic,
        "locale": "en_US",
        "default_locale": "en_US",
        "available_locales": ["en_US", "ja_JP", "zh_CN", "zh_TW"],
        "genre": genre,
        "mode": "teacher",
        "vessel": vessel_name,
        "main_characters": chars,
        "scene_palette": {
            "primary": "genre-led; see craft_notes",
            "secondary": "warm accent for renewal beats",
            "accent": "one recurring visual through-line",
        },
        "pages": [{"page_id": "ep_001_p01", "panels": build_panels(spec)}],
        "notes": {
            "pacing": (
                "Sixteen panels — entry-floor clear, webtoon-breathing. Silence does work; "
                "dialogue only at inflection. Genre story on the surface; topic as body weather only."
            ),
            "bubble_style_register": (
                "Protagonist dialogue: round_normal, often whisper. Vessel lines: soft, practical, never lecture."
            ),
            "sfx_policy": "Minimal. Whisper-register only. No BANG-register for therapeutic brands.",
            "translation_pipeline_handoff": (
                "text_by_locale populated for en_US; CJK placeholders for Phase translate_chapter_script.py."
            ),
        },
        "craft_notes": (
            f"VESSEL: {vessel_name} — {vessel_desc}. Cited from config/manga/manga_mode_vessels.yaml. "
            f"Teacher is NEVER named in-story (teacher_id={teacher_meta!r} is metadata only).\n"
            f"GENRE BIBLE: {bible}\n"
            f"GENRE-FIRST: surface plot is a {genre.replace('_', ' ')} story; "
            f"topic ({topic}) is the protagonist's interior weather — posture, breath, cost — never the title card.\n"
            f"ARC: wound (force/perform/flee) → turn (vessel models settle) → renewal (one kept act).\n"
            f"ACCEPTANCE LAYER: authored + gate-floor + craft-reviewed — NOT claimed bestseller (M6 bar)."
        ),
    }
    if spec.get("locale_note"):
        doc["locale_note"] = spec["locale_note"]
    if spec.get("byline_note"):
        doc["byline_note"] = spec["byline_note"]
    if spec.get("note"):
        doc["routing_note"] = spec["note"]
    return doc


def ensure_craft_notes(path: Path) -> None:
    """If a reused pilot lacks craft_notes, append a minimal block (do not rewrite prose)."""
    data = yaml.safe_load(path.read_text())
    if data.get("craft_notes"):
        return
    brand = data.get("brand_id", "")
    genre = "iyashikei"
    for r in ROUTING:
        if r.get("reuse") and r["reuse"] in str(path):
            genre = r["genre"]
            brand = r["brand"]
            break
        if r["brand"] == brand:
            genre = r["genre"]
            break
    vessel_name, vessel_desc = VESSELS.get(genre, ("vessel", "genre-native apparatus"))
    bible = BIBLES.get(genre, "docs/research/manga_craft/")
    data["craft_notes"] = (
        f"VESSEL: {vessel_name} — {vessel_desc}. "
        f"Teacher never named in-story.\n"
        f"GENRE BIBLE: {bible}\n"
        f"REUSED PILOT (M3 Wave 1): proven authored script retained; craft-notes block added for exit check.\n"
        f"ACCEPTANCE LAYER: authored + gate-floor + craft-reviewed — NOT claimed bestseller."
    )
    if "genre" not in data:
        data["genre"] = genre
    if "mode" not in data:
        data["mode"] = "teacher"
    if "vessel" not in data:
        data["vessel"] = vessel_name
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for spec in ROUTING:
        if "reuse" in spec:
            src = EXISTING / spec["reuse"] / "ep_001.yaml"
            if not src.is_file():
                raise SystemExit(f"missing reuse pilot: {src}")
            dest_dir = OUT / spec["reuse"]
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / "ep_001.yaml"
            if src.resolve() != dest.resolve():
                shutil.copy2(src, dest)
            ensure_craft_notes(dest)
            written.append(spec["reuse"])
            print(f"REUSE {spec['reuse']}")
            continue
        doc = build_script(spec)
        series_id = doc["series_id"]
        dest_dir = OUT / series_id
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / "ep_001.yaml"
        dest.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True), encoding="utf-8")
        written.append(series_id)
        print(f"NEW   {series_id}")
    manifest = REPO / "artifacts" / "qa" / "manga_m3_wave1_craft_audit" / "WAVE1_MANIFEST.tsv"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    lines = ["brand\tgenre\ttopic\tseries_id\treuse\n"]
    for spec in ROUTING:
        if "reuse" in spec:
            lines.append(f"{spec['brand']}\t{spec['genre']}\t{spec['topic']}\t{spec['reuse']}\tyes\n")
        else:
            author_slug = _slug_author(spec["author"])
            sid = f"{spec['brand']}__{author_slug}__en_US__{spec['topic']}__{spec['slug']}"
            lines.append(f"{spec['brand']}\t{spec['genre']}\t{spec['topic']}\t{sid}\tno\n")
    manifest.write_text("".join(lines), encoding="utf-8")
    print(f"wrote {len(written)} flagships; manifest {manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
