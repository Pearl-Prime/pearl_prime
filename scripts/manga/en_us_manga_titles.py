#!/usr/bin/env python3
"""Authored en_US manga catalog titles — Claude / Pearl_Writer (Tier-1).

This module is the title SOURCE for ``synthesize_manga_titles_enus.py``. Unlike the
ja_JP pipeline (which calls Qwen on Pearl Star), the en_US titles are AUTHORED
directly by Claude (Tier-1, operator-reviewed) per the operator's request — no LLM
API call is made at synthesis time. Each title is:

  * genre-faithful to the series ``genre`` (iyashikei, dark_fantasy, … , mecha);
  * built on the "Genre Shell" thesis — the wellness ``topic`` is embedded as
    INTERIOR architecture (what the story is *really* about) and NEVER stated as an
    explicit self-help / clinical word (no "anxiety", "burnout", "healing",
    "self-worth", "therapy", …);
  * short, striking, bookstore-shelf-worthy;
  * unique within its brand AND globally unique across all en_US titles.

Keyed by series-plan filename (……__en_US__<genre>__<series_index>.yaml) so the
mapping is unambiguous. ``synthesize_manga_titles_enus.py`` validates leaks and
uniqueness against this table before writing anything.
"""

from __future__ import annotations

# series-plan filename  ->  authored en_US title
TITLES: dict[str, str] = {
    # ── adhd_forge_mystery (shonen; adhd_focus / courage / self_worth) ──────────
    "adhd_forge_mystery__en_US__action_battle__series01.yaml": "Hammerstorm Brigade",
    "adhd_forge_mystery__en_US__isekai__series01.yaml": "The Anvil Between Worlds",
    "adhd_forge_mystery__en_US__psychological_thriller__series01.yaml": "The Quiet Forge",
    "adhd_forge_mystery__en_US__sports_competition__series01.yaml": "Full-Throttle Circuit",

    # ── bio_flow_healing (seinen; somatic_healing / overthinking / sleep) ───────
    "bio_flow_healing__en_US__historical_period__series01.yaml": "The Tidewater Physician",
    "bio_flow_healing__en_US__iyashikei__series01.yaml": "The Slow River Inn",
    "bio_flow_healing__en_US__psychological_thriller__series01.yaml": "Pulse of the Drowned City",
    "bio_flow_healing__en_US__psychological_thriller__series02.yaml": "The Sleepwalker's Ward",
    "bio_flow_healing__en_US__sci_fi_cyberpunk__series01.yaml": "Signal Bleed",
    "bio_flow_healing__en_US__sci_fi_cyberpunk__series02.yaml": "Dreamfeed District",

    # ── body_memory_shojo (josei; somatic_healing / trauma_recovery / shame / grief) ─
    "body_memory_shojo__en_US__dark_fantasy__series01.yaml": "The Skin of the Forest",
    "body_memory_shojo__en_US__dark_fantasy__series02.yaml": "Where the Scars Remember",
    "body_memory_shojo__en_US__iyashikei__series01.yaml": "The Quiet After Bloom",
    "body_memory_shojo__en_US__iyashikei__series02.yaml": "Letters to the Empty Chair",
    "body_memory_shojo__en_US__psychological_horror__series01.yaml": "The House That Breathes",
    "body_memory_shojo__en_US__psychological_horror__series02.yaml": "Beneath the Old Skin",
    "body_memory_shojo__en_US__supernatural_mystery__series01.yaml": "The Hollow Reflection",
    "body_memory_shojo__en_US__supernatural_mystery__series02.yaml": "The Garden of Lost Names",

    # ── bright_presence_tw_seinen (seinen; social_anxiety / imposter_syndrome / self_worth) ─
    "bright_presence_tw_seinen__en_US__historical_period__series01.yaml": "The Lantern Diplomat",
    "bright_presence_tw_seinen__en_US__iyashikei__series01.yaml": "The Borrowed Stage",
    "bright_presence_tw_seinen__en_US__psychological_thriller__series01.yaml": "The Understudy",
    "bright_presence_tw_seinen__en_US__romance_josei_drama__series01.yaml": "Two Seats From the Window",

    # ── calm_student_school (shojo; anxiety / social_anxiety / self_worth) ───────
    "calm_student_school__en_US__iyashikei__series01.yaml": "Afternoon Light Club",
    "calm_student_school__en_US__romance_josei_drama__series01.yaml": "The Seat Beside You",
    "calm_student_school__en_US__school_coming_of_age__series01.yaml": "The Last Row",
    "calm_student_school__en_US__supernatural_mystery__series01.yaml": "The Clocktower Holds Its Breath",

    # ── career_lift_workplace (josei; imposter_syndrome / social_anxiety / financial_anxiety / burnout) ─
    "career_lift_workplace__en_US__iyashikei__series01.yaml": "The Rooftop Garden Office",
    "career_lift_workplace__en_US__romance_josei_drama__series01.yaml": "Between Floors",
    "career_lift_workplace__en_US__romance_josei_drama__series02.yaml": "The Salary We Don't Discuss",
    "career_lift_workplace__en_US__supernatural_mystery__series01.yaml": "The Midnight Mailroom",
    "career_lift_workplace__en_US__supernatural_mystery__series02.yaml": "The Promotion That Wasn't There",
    "career_lift_workplace__en_US__workplace_drama__series01.yaml": "Glass Partitions",
    "career_lift_workplace__en_US__workplace_drama__series02.yaml": "Red Ink",
    "career_lift_workplace__en_US__workplace_drama__series03.yaml": "The Corner Office Is Empty",

    # ── cognitive_clarity (seinen; overthinking / imposter_syndrome / burnout / boundaries) ─
    "cognitive_clarity__en_US__dark_fantasy__series01.yaml": "The Labyrinth of Endless Doors",
    "cognitive_clarity__en_US__dark_fantasy__series02.yaml": "The Crown of Borrowed Faces",
    "cognitive_clarity__en_US__dark_fantasy__series03.yaml": "Ashlight Cathedral",
    "cognitive_clarity__en_US__psychological_thriller__series01.yaml": "The Line You Don't Cross",
    "cognitive_clarity__en_US__psychological_thriller__series02.yaml": "Seventeen Versions of Tonight",
    "cognitive_clarity__en_US__psychological_thriller__series03.yaml": "The Stand-In",
    "cognitive_clarity__en_US__psychological_thriller__series04.yaml": "Running on Empty Floors",
    "cognitive_clarity__en_US__psychological_thriller__series05.yaml": "The Door Marked No",
    "cognitive_clarity__en_US__sci_fi_cyberpunk__series01.yaml": "Loop Static",
    "cognitive_clarity__en_US__sci_fi_cyberpunk__series02.yaml": "Ghost in the Resume",
    "cognitive_clarity__en_US__sci_fi_cyberpunk__series03.yaml": "Overclocked",
    "cognitive_clarity__en_US__supernatural_mystery__series01.yaml": "The Threshold Keeper",
    "cognitive_clarity__en_US__supernatural_mystery__series02.yaml": "The Thinking Room",
    "cognitive_clarity__en_US__workplace_drama__series01.yaml": "Acting Director",

    # ── confidence_core_romance (shojo; imposter_syndrome / self_worth / social_anxiety) ─
    "confidence_core_romance__en_US__isekai__series01.yaml": "Summoned as the Spare",
    "confidence_core_romance__en_US__iyashikei__series01.yaml": "The Flower Shop at the End of the Lane",
    "confidence_core_romance__en_US__romance_josei_drama__series01.yaml": "First Words, Last",
    "confidence_core_romance__en_US__romance_josei_drama__series02.yaml": "The Girl Who Almost Wasn't",
    "confidence_core_romance__en_US__romance_josei_drama__series03.yaml": "Worth the Wait",
    "confidence_core_romance__en_US__supernatural_mystery__series01.yaml": "The Wallflower's Mirror",

    # ── creative_unfold_social (shojo; social_anxiety / self_worth / courage) ────
    "creative_unfold_social__en_US__action_battle__series01.yaml": "Paint the Arena",
    "creative_unfold_social__en_US__romance_josei_drama__series01.yaml": "The Color You Are",
    "creative_unfold_social__en_US__school_coming_of_age__series01.yaml": "Sketchbook Courage",
    "creative_unfold_social__en_US__supernatural_mystery__series01.yaml": "The Gallery That Speaks",

    # ── devotion_path_shonen (josei; grief / compassion / courage) ──────────────
    "devotion_path_shonen__en_US__action_battle__series01.yaml": "The Last Pilgrim's Blade",
    "devotion_path_shonen__en_US__action_battle__series02.yaml": "Shield of the Merciful",
    "devotion_path_shonen__en_US__cultivation_martial__series01.yaml": "The Mountain Does Not Move",
    "devotion_path_shonen__en_US__dark_fantasy__series01.yaml": "The Shrine of Fallen Stars",
    "devotion_path_shonen__en_US__dark_fantasy__series02.yaml": "The Mercy Vow",
    "devotion_path_shonen__en_US__supernatural_mystery__series01.yaml": "The Bell That Calls the Brave",

    # ── digital_ground (manhwa; burnout / imposter_syndrome / financial_anxiety / anxiety / somatic_healing) ─
    "digital_ground__en_US__isekai__series01.yaml": "Logged Out of Eden",
    "digital_ground__en_US__isekai__series02.yaml": "NPC No More",
    "digital_ground__en_US__iyashikei__series01.yaml": "The Unpaid Bill Cafe",
    "digital_ground__en_US__psychological_horror__series01.yaml": "Notification at 3 A.M.",
    "digital_ground__en_US__psychological_horror__series02.yaml": "The Body Keeps the Feed",
    "digital_ground__en_US__psychological_horror__series03.yaml": "Read Receipts",
    "digital_ground__en_US__sci_fi_cyberpunk__series01.yaml": "Account Suspended",
    "digital_ground__en_US__sci_fi_cyberpunk__series02.yaml": "Credit Score Zero",
    "digital_ground__en_US__sci_fi_cyberpunk__series03.yaml": "Buffering Reality",
    "digital_ground__en_US__sci_fi_cyberpunk__series04.yaml": "Haptic Drift",
    "digital_ground__en_US__sci_fi_cyberpunk__series05.yaml": "Logout Protocol",
    "digital_ground__en_US__workplace_drama__series01.yaml": "Seen at 11:58",
    "digital_ground__en_US__workplace_drama__series02.yaml": "The Invoice War",
    "digital_ground__en_US__workplace_drama__series03.yaml": "Open Tabs",

    # ── executive_calm_workplace (seinen; burnout / overthinking / financial_anxiety) ─
    "executive_calm_workplace__en_US__dark_fantasy__series01.yaml": "The Iron Throne Room",
    "executive_calm_workplace__en_US__psychological_thriller__series01.yaml": "The Quarterly Reckoning",
    "executive_calm_workplace__en_US__psychological_thriller__series02.yaml": "The Ledger Bleeds",
    "executive_calm_workplace__en_US__sci_fi_cyberpunk__series01.yaml": "CEO of Nothing",
    "executive_calm_workplace__en_US__sci_fi_cyberpunk__series02.yaml": "Boardroom Static",
    "executive_calm_workplace__en_US__workplace_drama__series01.yaml": "The Bottom Line",
    "executive_calm_workplace__en_US__workplace_drama__series02.yaml": "After the Bell",
    "executive_calm_workplace__en_US__workplace_drama__series03.yaml": "The Spreadsheet at Midnight",

    # ── focus_sprint_workplace (seinen; adhd_focus / imposter_syndrome / social_anxiety) ─
    "focus_sprint_workplace__en_US__action_battle__series01.yaml": "Sprint Zero",
    "focus_sprint_workplace__en_US__action_battle__series02.yaml": "The Rookie Gambit",
    "focus_sprint_workplace__en_US__psychological_thriller__series01.yaml": "The Standup Nobody Speaks At",
    "focus_sprint_workplace__en_US__sports_competition__series01.yaml": "Tunnel Vision",
    "focus_sprint_workplace__en_US__sports_competition__series02.yaml": "Bench to Starter",
    "focus_sprint_workplace__en_US__sports_competition__series03.yaml": "The Quiet Striker",
    "focus_sprint_workplace__en_US__workplace_drama__series01.yaml": "Deadline Velocity",
    "focus_sprint_workplace__en_US__workplace_drama__series02.yaml": "Probation Period",

    # ── gentle_growth_healing (josei; self_worth / imposter_syndrome / social_anxiety) ─
    "gentle_growth_healing__en_US__dark_fantasy__series01.yaml": "The Seedling Crown",
    "gentle_growth_healing__en_US__iyashikei__series01.yaml": "The Greenhouse of Borrowed Time",
    "gentle_growth_healing__en_US__iyashikei__series02.yaml": "Tea for One More",
    "gentle_growth_healing__en_US__romance_josei_drama__series01.yaml": "Enough, As You Are",
    "gentle_growth_healing__en_US__romance_josei_drama__series02.yaml": "The Imposter at the Altar",
    "gentle_growth_healing__en_US__romance_josei_drama__series03.yaml": "Across a Crowded Room",
    "gentle_growth_healing__en_US__supernatural_mystery__series01.yaml": "The Worth of Small Things",
    "gentle_growth_healing__en_US__supernatural_mystery__series02.yaml": "The Mask Shop on Willow Street",

    # ── healing_ground_healing (josei; grief / boundaries / overthinking) ────────
    "healing_ground_healing__en_US__dark_fantasy__series01.yaml": "The Mourning Country",
    "healing_ground_healing__en_US__dark_fantasy__series02.yaml": "The Wall of Thorns",
    "healing_ground_healing__en_US__dark_fantasy__series03.yaml": "The Maze of Maybe",
    "healing_ground_healing__en_US__iyashikei__series01.yaml": "The Memory Garden",
    "healing_ground_healing__en_US__iyashikei__series02.yaml": "The Fence Between Us",
    "healing_ground_healing__en_US__psychological_thriller__series01.yaml": "What the Clock Keeps Asking",
    "healing_ground_healing__en_US__supernatural_mystery__series01.yaml": "The Lighthouse of Lost Things",
    "healing_ground_healing__en_US__supernatural_mystery__series02.yaml": "The Door You Learned to Close",

    # ── heart_balance_shojo (josei; social_anxiety / boundaries / self_worth) ────
    "heart_balance_shojo__en_US__iyashikei__series01.yaml": "The Quiet Corner Bakery",
    "heart_balance_shojo__en_US__iyashikei__series02.yaml": "Room for Two Hearts",
    "heart_balance_shojo__en_US__romance_josei_drama__series01.yaml": "Worthy of the Window Seat",
    "heart_balance_shojo__en_US__romance_josei_drama__series02.yaml": "The Confession Nobody Heard",
    "heart_balance_shojo__en_US__romance_josei_drama__series03.yaml": "The Word Is No",
    "heart_balance_shojo__en_US__supernatural_mystery__series01.yaml": "The Mirror Knows Your Name",
    "heart_balance_shojo__en_US__workplace_drama__series01.yaml": "The Break Room Wallflower",
    "heart_balance_shojo__en_US__workplace_drama__series02.yaml": "Off the Clock, Off the Hook",

    # ── high_performer_workplace (seinen; burnout / financial_anxiety / imposter_syndrome / overthinking) ─
    "high_performer_workplace__en_US__dark_fantasy__series01.yaml": "The Champion Who Could Not Rest",
    "high_performer_workplace__en_US__dark_fantasy__series02.yaml": "The Debt of Kings",
    "high_performer_workplace__en_US__historical_period__series01.yaml": "The General's Borrowed Glory",
    "high_performer_workplace__en_US__historical_period__series02.yaml": "Counsel of a Thousand Doubts",
    "high_performer_workplace__en_US__psychological_thriller__series01.yaml": "The Last One Working",
    "high_performer_workplace__en_US__psychological_thriller__series02.yaml": "Margin Call at Midnight",
    "high_performer_workplace__en_US__workplace_drama__series01.yaml": "The Fraud in the Mirror",
    "high_performer_workplace__en_US__workplace_drama__series02.yaml": "Second-Guessing the Win",

    # ── hormone_reset_healing (josei; somatic_healing / self_worth / anxiety) ────
    "hormone_reset_healing__en_US__iyashikei__series01.yaml": "The Slow Tide Spa",
    "hormone_reset_healing__en_US__iyashikei__series02.yaml": "Worth the Warm Light",
    "hormone_reset_healing__en_US__psychological_horror__series01.yaml": "The Pulse Beneath the Floor",
    "hormone_reset_healing__en_US__romance_josei_drama__series01.yaml": "The Body Remembers Spring",
    "hormone_reset_healing__en_US__supernatural_mystery__series01.yaml": "The Worth of a Whispered Name",
    "hormone_reset_healing__en_US__supernatural_mystery__series02.yaml": "The House on Trembling Hill",

    # ── legacy_builder_memoir (seinen; self_worth / grief / financial_anxiety / shame) ─
    "legacy_builder_memoir__en_US__dark_fantasy__series01.yaml": "The Heir of Hollow Halls",
    "legacy_builder_memoir__en_US__historical_period__series01.yaml": "The Last Letter Home",
    "legacy_builder_memoir__en_US__iyashikei__series01.yaml": "The Workshop We Inherited",
    "legacy_builder_memoir__en_US__psychological_thriller__series01.yaml": "The Name on the Plaque",

    # ── longevity_lab_healing (seinen; somatic_healing / self_worth / grief) ─────
    "longevity_lab_healing__en_US__historical_period__series01.yaml": "The Apothecary of Long Years",
    "longevity_lab_healing__en_US__historical_period__series02.yaml": "The Worth of an Old Soldier",
    "longevity_lab_healing__en_US__iyashikei__series01.yaml": "The Garden That Outlived Us",
    "longevity_lab_healing__en_US__iyashikei__series02.yaml": "The Long Walk Home",
    "longevity_lab_healing__en_US__sci_fi_cyberpunk__series01.yaml": "Telomere",
    "longevity_lab_healing__en_US__supernatural_mystery__series01.yaml": "The Clock That Mourns",

    # ── minimal_mind_healing (seinen; overthinking / anxiety / burnout) ──────────
    "minimal_mind_healing__en_US__iyashikei__series01.yaml": "The Empty Room Is Enough",
    "minimal_mind_healing__en_US__iyashikei__series02.yaml": "One Cup, One Window",
    "minimal_mind_healing__en_US__iyashikei__series03.yaml": "The Last Box Unpacked",
    "minimal_mind_healing__en_US__psychological_thriller__series01.yaml": "The Clutter Speaks Back",
    "minimal_mind_healing__en_US__psychological_thriller__series02.yaml": "Too Many Rooms",
    "minimal_mind_healing__en_US__sci_fi_cyberpunk__series01.yaml": "Cache Overflow",
    "minimal_mind_healing__en_US__sci_fi_cyberpunk__series02.yaml": "Signal to Noise",
    "minimal_mind_healing__en_US__supernatural_mystery__series01.yaml": "The House With Too Many Doors",

    # ── morning_momentum_workplace (shonen; burnout / courage / self_worth) ──────
    "morning_momentum_workplace__en_US__action_battle__series01.yaml": "Dawn Patrol Zero",
    "morning_momentum_workplace__en_US__action_battle__series02.yaml": "First Light Brigade",
    "morning_momentum_workplace__en_US__isekai__series01.yaml": "Reborn at Sunrise",
    "morning_momentum_workplace__en_US__sports_competition__series01.yaml": "The 5 A.M. Lane",
    "morning_momentum_workplace__en_US__sports_competition__series02.yaml": "Against the Whistle",
    "morning_momentum_workplace__en_US__sports_competition__series03.yaml": "Start Where You Stand",
    "morning_momentum_workplace__en_US__workplace_drama__series01.yaml": "The First Shift",
    "morning_momentum_workplace__en_US__workplace_drama__series02.yaml": "Clock In, Stand Tall",

    # ── night_reset_healing (josei; sleep / anxiety / grief) ─────────────────────
    "night_reset_healing__en_US__dark_fantasy__series01.yaml": "The Kingdom That Never Sleeps",
    "night_reset_healing__en_US__iyashikei__series01.yaml": "The Last Lamp on the Street",
    "night_reset_healing__en_US__iyashikei__series02.yaml": "The Chair That Stays Empty",
    "night_reset_healing__en_US__iyashikei__series03.yaml": "Lullaby for the Restless",
    "night_reset_healing__en_US__psychological_horror__series01.yaml": "Three O'Clock and Wide Awake",
    "night_reset_healing__en_US__psychological_horror__series02.yaml": "The Visitor at the Foot of the Bed",
    "night_reset_healing__en_US__supernatural_mystery__series01.yaml": "The Sandman Keeps a Ledger",
    "night_reset_healing__en_US__supernatural_mystery__series02.yaml": "The Hour the House Wakes",

    # ── optimizer_workplace (seinen; overthinking / burnout / imposter_syndrome) ─
    "optimizer_workplace__en_US__psychological_thriller__series01.yaml": "The Perfect Schedule Kills",
    "optimizer_workplace__en_US__psychological_thriller__series02.yaml": "Diminishing Returns",
    "optimizer_workplace__en_US__psychological_thriller__series03.yaml": "The Metric Nobody Asked For",
    "optimizer_workplace__en_US__sci_fi_cyberpunk__series01.yaml": "Process Loop",
    "optimizer_workplace__en_US__sci_fi_cyberpunk__series02.yaml": "Thermal Throttle",
    "optimizer_workplace__en_US__sports_competition__series01.yaml": "The Marginal Gain",
    "optimizer_workplace__en_US__workplace_drama__series01.yaml": "A/B Forever",
    "optimizer_workplace__en_US__workplace_drama__series02.yaml": "The Efficiency Trap",

    # ── qi_foundation_cultivation (seinen; somatic_healing / courage / burnout) ──
    "qi_foundation_cultivation__en_US__action_battle__series01.yaml": "Breath of the Iron Mountain",
    "qi_foundation_cultivation__en_US__dark_fantasy__series01.yaml": "The Trembling Disciple",
    "qi_foundation_cultivation__en_US__historical_period__series01.yaml": "The Monk Who Carried the Mountain Alone",
    "qi_foundation_cultivation__en_US__iyashikei__series01.yaml": "The Stillness Between Forms",

    # ── relational_calm_iyashikei (josei; social_anxiety / boundaries / somatic_healing) ─
    "relational_calm_iyashikei__en_US__iyashikei__series01.yaml": "The Teahouse of Quiet Words",
    "relational_calm_iyashikei__en_US__iyashikei__series02.yaml": "The Gate We Keep Open",
    "relational_calm_iyashikei__en_US__psychological_thriller__series01.yaml": "What the Body Won't Say",
    "relational_calm_iyashikei__en_US__romance_josei_drama__series01.yaml": "A Table for the Shy",
    "relational_calm_iyashikei__en_US__romance_josei_drama__series02.yaml": "The Space You Asked For",
    "relational_calm_iyashikei__en_US__romance_josei_drama__series03.yaml": "Skin and Stillness",
    "relational_calm_iyashikei__en_US__supernatural_mystery__series01.yaml": "The Quiet One in Room Nine",
    "relational_calm_iyashikei__en_US__supernatural_mystery__series02.yaml": "The Threshold We Don't Cross",

    # ── relationship_clarity_romance (josei; social_anxiety / boundaries / self_worth) ─
    "relationship_clarity_romance__en_US__iyashikei__series01.yaml": "The Cafe Where No One Rushes",
    "relationship_clarity_romance__en_US__iyashikei__series02.yaml": "The Line We Draw in Sand",
    "relationship_clarity_romance__en_US__psychological_thriller__series01.yaml": "The One Who Settled",
    "relationship_clarity_romance__en_US__romance_josei_drama__series01.yaml": "Almost Brave Enough to Stay",
    "relationship_clarity_romance__en_US__romance_josei_drama__series02.yaml": "The Word I Couldn't Say",
    "relationship_clarity_romance__en_US__supernatural_mystery__series01.yaml": "The Locket That Knows Your Worth",

    # ── resilient_parent_social (josei; burnout / self_worth / boundaries) ───────
    "resilient_parent_social__en_US__dark_fantasy__series01.yaml": "The Queen With No Throne to Rest On",
    "resilient_parent_social__en_US__iyashikei__series01.yaml": "The Kitchen Light Stays On",
    "resilient_parent_social__en_US__iyashikei__series02.yaml": "The Door I Finally Closed",
    "resilient_parent_social__en_US__romance_josei_drama__series01.yaml": "Running on Lullabies",
    "resilient_parent_social__en_US__romance_josei_drama__series02.yaml": "More Than Someone's Mother",
    "resilient_parent_social__en_US__supernatural_mystery__series01.yaml": "The House That Asks Too Much",

    # ── sleep_restoration_iyashikei (josei; sleep / anxiety / grief / social_anxiety) ─
    "sleep_restoration_iyashikei__en_US__iyashikei__series01.yaml": "The Quietest Hour",
    "sleep_restoration_iyashikei__en_US__iyashikei__series02.yaml": "The Night Light Cafe",
    "sleep_restoration_iyashikei__en_US__iyashikei__series03.yaml": "Where the Stars Keep Vigil",
    "sleep_restoration_iyashikei__en_US__iyashikei__series04.yaml": "The Bench by the Late Train",
    "sleep_restoration_iyashikei__en_US__psychological_horror__series01.yaml": "The Thing Beneath the Quilt",
    "sleep_restoration_iyashikei__en_US__psychological_horror__series02.yaml": "Eyes Open at Midnight",
    "sleep_restoration_iyashikei__en_US__psychological_horror__series03.yaml": "The Mourning Lamp",
    "sleep_restoration_iyashikei__en_US__romance_josei_drama__series01.yaml": "Goodnight, Stranger",
    "sleep_restoration_iyashikei__en_US__supernatural_mystery__series01.yaml": "The Keeper of Drowsy Things",
    "sleep_restoration_iyashikei__en_US__supernatural_mystery__series02.yaml": "The Lamplighter's Last Round",

    # ── solar_return_isekai (shonen; self_worth / imposter_syndrome / courage) ───
    "solar_return_isekai__en_US__action_battle__series01.yaml": "Sunforged",
    "solar_return_isekai__en_US__dark_fantasy__series01.yaml": "The Hero They Mistook Me For",
    "solar_return_isekai__en_US__isekai__series01.yaml": "Reborn Beneath Two Suns",
    "solar_return_isekai__en_US__isekai__series02.yaml": "The World That Chose Me",
    "solar_return_isekai__en_US__mecha__series01.yaml": "Solaris Vanguard",

    # ── somatic_wisdom_shojo (josei; somatic_healing / self_worth / social_anxiety / grief) ─
    "somatic_wisdom_shojo__en_US__dark_fantasy__series01.yaml": "The Forest That Remembers Touch",
    "somatic_wisdom_shojo__en_US__dark_fantasy__series02.yaml": "The Witch Who Forgot Her Worth",
    "somatic_wisdom_shojo__en_US__iyashikei__series01.yaml": "The Soft-Spoken Florist",
    "somatic_wisdom_shojo__en_US__iyashikei__series02.yaml": "The Bench We Always Shared",
    "somatic_wisdom_shojo__en_US__iyashikei__series03.yaml": "Where the Body Learns to Bloom",
    "somatic_wisdom_shojo__en_US__romance_josei_drama__series01.yaml": "Worthy of Warm Hands",
    "somatic_wisdom_shojo__en_US__romance_josei_drama__series02.yaml": "The Shyest Heart in the Room",
    "somatic_wisdom_shojo__en_US__romance_josei_drama__series03.yaml": "The Spring We Lost",
    "somatic_wisdom_shojo__en_US__supernatural_mystery__series01.yaml": "The Skin-Deep Spell",
    "somatic_wisdom_shojo__en_US__supernatural_mystery__series02.yaml": "The Girl the Mirror Forgot",

    # ── spiritual_ground_supernatural (josei; grief / self_worth / courage) ──────
    "spiritual_ground_supernatural__en_US__dark_fantasy__series01.yaml": "The Cathedral of Quiet Sorrow",
    "spiritual_ground_supernatural__en_US__dark_fantasy__series02.yaml": "The Saint Who Doubted Herself",
    "spiritual_ground_supernatural__en_US__historical_period__series01.yaml": "The Pilgrim Who Feared the Dark",
    "spiritual_ground_supernatural__en_US__iyashikei__series01.yaml": "The Shrine by the Still Pond",
    "spiritual_ground_supernatural__en_US__supernatural_mystery__series01.yaml": "The Ghost Who Knew Her Worth",
    "spiritual_ground_supernatural__en_US__supernatural_mystery__series02.yaml": "The Candle in the Haunted Wing",

    # ── stabilizer_healing (seinen; burnout / overthinking / financial_anxiety) ──
    "stabilizer_healing__en_US__dark_fantasy__series01.yaml": "The Knight Who Could Not Stop",
    "stabilizer_healing__en_US__iyashikei__series01.yaml": "The Anchor Shop",
    "stabilizer_healing__en_US__iyashikei__series02.yaml": "The Tab We Never Settle",
    "stabilizer_healing__en_US__iyashikei__series03.yaml": "The Stillness After the Storm",
    "stabilizer_healing__en_US__sci_fi_cyberpunk__series01.yaml": "Thread Overload",
    "stabilizer_healing__en_US__sci_fi_cyberpunk__series02.yaml": "Insufficient Funds",
    "stabilizer_healing__en_US__workplace_drama__series01.yaml": "The Last to Leave the Office",
    "stabilizer_healing__en_US__workplace_drama__series02.yaml": "The Mind That Won't Clock Out",

    # ── stillness_press (josei; anxiety / somatic_healing / sleep / grief / trauma_recovery) ─
    "stillness_press__en_US__dark_fantasy__series01.yaml": "The Kingdom Holding Its Breath",
    "stillness_press__en_US__dark_fantasy__series02.yaml": "The Forest Beneath the Skin",
    "stillness_press__en_US__dark_fantasy__series03.yaml": "The Tower That Never Slept",
    "stillness_press__en_US__dark_fantasy__series04.yaml": "The Realm of Empty Chairs",
    "stillness_press__en_US__isekai__series01.yaml": "Carried Across the Veil",
    "stillness_press__en_US__isekai__series02.yaml": "The World Beyond the Tremor",
    "stillness_press__en_US__iyashikei__series02.yaml": "The Warmth of Small Rooms",
    "stillness_press__en_US__iyashikei__series03.yaml": "The Last Train Stays Late",
    "stillness_press__en_US__iyashikei__series04.yaml": "The Tea Goes Cold Slowly",
    "stillness_press__en_US__iyashikei__series05.yaml": "The Long Way Back to Calm",
    "stillness_press__en_US__psychological_horror__series01.yaml": "Something Under the Ribs",
    "stillness_press__en_US__psychological_horror__series02.yaml": "The Hours That Won't Close Their Eyes",
    "stillness_press__en_US__psychological_horror__series03.yaml": "The Empty Side of the Bed",
    "stillness_press__en_US__supernatural_mystery__series01.yaml": "The House Remembers the Wound",
    "stillness_press__en_US__supernatural_mystery__series02.yaml": "The Trembling Hour",

    # ── stoic_edge_battle (seinen; courage / grief / self_worth / shame) ─────────
    "stoic_edge_battle__en_US__action_battle__series01.yaml": "The Unflinching Blade",
    "stoic_edge_battle__en_US__action_battle__series02.yaml": "The Warrior Who Carried the Dead",
    "stoic_edge_battle__en_US__dark_fantasy__series01.yaml": "The Knight of Hollow Worth",
    "stoic_edge_battle__en_US__historical_period__series01.yaml": "The General's Buried Shame",
    "stoic_edge_battle__en_US__historical_period__series02.yaml": "The Last Stand at Iron Pass",
    "stoic_edge_battle__en_US__sports_competition__series01.yaml": "The Fighter Who Lost His Brother",

    # ── trauma_path_healing (josei; grief / trauma_recovery / somatic_healing / shame) ─
    "trauma_path_healing__en_US__dark_fantasy__series01.yaml": "The Land Where Grief Takes Root",
    "trauma_path_healing__en_US__dark_fantasy__series02.yaml": "The Scar That Became a Door",
    "trauma_path_healing__en_US__historical_period__series01.yaml": "The Healer of the War Road",
    "trauma_path_healing__en_US__iyashikei__series01.yaml": "The Hush After the Storm",
    "trauma_path_healing__en_US__psychological_horror__series01.yaml": "The Grief That Walks the Halls",
    "trauma_path_healing__en_US__psychological_horror__series02.yaml": "What the Wound Remembers",

    # ── warrior_calm_cultivation (shonen; burnout / courage / somatic_healing) ───
    "warrior_calm_cultivation__en_US__action_battle__series01.yaml": "The Blade That Learned to Rest",
    "warrior_calm_cultivation__en_US__action_battle__series02.yaml": "Stand Until the Storm Breaks",
    "warrior_calm_cultivation__en_US__dark_fantasy__series01.yaml": "The Body of the Mountain Sage",
    "warrior_calm_cultivation__en_US__dark_fantasy__series02.yaml": "The Warlord Who Could Not Sleep",
    "warrior_calm_cultivation__en_US__historical_period__series01.yaml": "The Swordsman of the Quiet Valley",
    "warrior_calm_cultivation__en_US__iyashikei__series01.yaml": "The Dojo by the Slow Stream",
    "warrior_calm_cultivation__en_US__mecha__series01.yaml": "Stillpoint Zero",
}
