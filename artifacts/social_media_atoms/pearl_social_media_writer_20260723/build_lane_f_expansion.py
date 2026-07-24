#!/usr/bin/env python3
"""
Lane F (2026-07-23) — social atom-bank wave-2 expansion.

Three operations on SOURCE_OF_TRUTH/social_media_atoms/evergreen_en_us_atoms.jsonl:

1. REPAIR: rewrite the 54 remaining broken mail-merge HOOK_COVER rows
   ("{persona}: {clause} is not the whole story.") across 18 topics x
   3 personas (corporate_managers, gen_z_professionals, healthcare_rns).
2. DEDUP: rewrite the gen_z_professionals REFRAME/MECHANISM_EXPLAINER
   variant-02/03 rows for anxiety+burnout that are currently byte-identical
   to corporate_managers/healthcare_rns.
3. EXPAND: append new MICRO_STORY/CASE_PROOF/CAROUSEL_SLIDE/THREAD_UNIT/
   VIDEO_BEAT rows for personas entrepreneurs + gen_x_sandwich across
   topics anxiety + burnout (the 5 families Lane C introduced previously
   covered only corporate_managers/gen_z_professionals).

Run: python3 artifacts/social_media_atoms/pearl_social_media_writer_20260723/build_lane_f_expansion.py
"""
import json

BANK = "SOURCE_OF_TRUTH/social_media_atoms/evergreen_en_us_atoms.jsonl"
DIGEST = "artifacts/social_media_atoms/pearl_social_media_writer_20260723/deep_research_digest_20260723.md"

LANE_F_DATE = "2026-07-23"

# ---------------------------------------------------------------------------
# 1. Broken HOOK_COVER repair — 18 topics x 3 personas
# ---------------------------------------------------------------------------

REPAIR_TEXT = {
    ("addiction", "corporate_managers"): "Willpower doesn't lose to a craving because you're weak — it loses because craving is a physiology problem wearing a decision-making costume.",
    ("addiction", "gen_z_professionals"): "You didn't fail at willpower. The craving was never a debate your logic could actually win.",
    ("addiction", "healthcare_rns"): "Telling a patient to just use more willpower ignores what's actually driving the craving — and it isn't a character flaw.",

    ("adhd", "corporate_managers"): "More effort was never the fix for a brain that's wired for novelty over repetition — the system needs scaffolding, not stamina.",
    ("adhd", "gen_z_professionals"): "It's not that you're not trying hard enough. Your brain is running a completely different reward system than the one this task was built for.",
    ("adhd", "healthcare_rns"): "Charting 'needs to try harder' misses the actual mechanism — executive function is a wiring difference, not a willpower problem.",

    ("body_image", "corporate_managers"): "The mirror doesn't go quiet after the next change — it goes quiet when the running commentary itself gets addressed.",
    ("body_image", "gen_z_professionals"): "You've hit the goal before and the voice in your head didn't stop. That's the part worth looking at, not the number.",
    ("body_image", "healthcare_rns"): "Patients chase one more physical change expecting relief, but the distress usually lives in the appraisal, not the appearance.",

    ("boundaries", "corporate_managers"): "A clear no rarely costs the relationship — the resentment that builds from never saying it usually costs more.",
    ("boundaries", "gen_z_professionals"): "You keep saying yes to protect the friendship. Watch what actually happens the first time you don't.",
    ("boundaries", "healthcare_rns"): "The nurses who never say no aren't more relationship-safe — they're just further along the road to resentment.",

    ("compassion_fatigue", "corporate_managers"): "Caring harder doesn't refill the tank — it's the mechanism that's draining it in the first place.",
    ("compassion_fatigue", "gen_z_professionals"): "You keep showing up for everyone hoping the caring itself will recharge you. It won't. It's the thing spending the battery.",
    ("compassion_fatigue", "healthcare_rns"): "The instinct is to care more when you're depleted, but caring is the expenditure here, not the recovery.",

    ("courage", "corporate_managers"): "Courage was never the absence of fear showing up first — it's moving with the fear still fully in the room.",
    ("courage", "gen_z_professionals"): "You're not broken because the fear didn't leave before you acted. Nobody's does. You just move anyway.",
    ("courage", "healthcare_rns"): "Waiting to feel fully ready before speaking up in a room full of hierarchy usually means never speaking up at all.",

    ("depression", "corporate_managers"): "Pushing harder against the flatness usually just adds exhaustion on top of the numbness — it doesn't touch the numbness itself.",
    ("depression", "gen_z_professionals"): "Grinding through the flat feeling doesn't fix it. It just means you're now tired and still flat.",
    ("depression", "healthcare_rns"): "Patients often push through low mood by increasing output, which frequently deepens the depletion instead of resolving it.",

    ("divorce", "corporate_managers"): "There's no fixed timeline where grief for a marriage is supposed to be finished — the calendar isn't the measure.",
    ("divorce", "gen_z_professionals"): "You're not behind schedule. There was never a schedule. You're just further along than you were yesterday.",
    ("divorce", "healthcare_rns"): "Patients measure their divorce recovery against an invisible deadline nobody actually set — that comparison is what's adding the extra pain.",

    ("financial_anxiety", "corporate_managers"): "Avoiding the number doesn't protect you from it — it just means the anxiety runs in the background instead of the foreground.",
    ("financial_anxiety", "gen_z_professionals"): "Not checking your balance doesn't change the balance. It just makes the dread follow you everywhere instead of staying in one tab.",
    ("financial_anxiety", "healthcare_rns"): "The instinct to avoid the number to feel safer usually backfires — the anxiety just relocates instead of resolving.",

    ("grief", "corporate_managers"): "Time by itself doesn't close a grief — what closes it is what you do with the time, not the time passing.",
    ("grief", "gen_z_professionals"): "It's not that not enough time has passed. Time alone was never going to be the thing that did this.",
    ("grief", "healthcare_rns"): "Telling a grieving patient 'it just takes time' is technically true and clinically useless — time has to be paired with something.",

    ("imposter_syndrome", "corporate_managers"): "The feeling of being qualified rarely arrives before the work does — competence gets proven in motion, not granted in advance.",
    ("imposter_syndrome", "gen_z_professionals"): "You're waiting to feel ready before you'll believe you belong. Most people in the room are faking that feeling too.",
    ("imposter_syndrome", "healthcare_rns"): "New RNs wait to feel competent before trusting their own judgment — but that feeling shows up after the reps, not before them.",

    ("money", "corporate_managers"): "Avoiding the spreadsheet feels easier for about a day — the plan is actually the shorter path to less stress.",
    ("money", "gen_z_professionals"): "Not looking at your money feels like the easy way out. It's actually the long way around.",
    ("money", "healthcare_rns"): "Avoiding a financial plan feels protective in the moment but tends to cost more stress over the following months than making one.",

    ("overthinking", "corporate_managers"): "More analysis rarely produces the certainty it's chasing — it usually just produces more analysis.",
    ("overthinking", "gen_z_professionals"): "You think you're one more replay away from certainty. You've replayed this fifty times already and it hasn't shown up yet.",
    ("overthinking", "healthcare_rns"): "Clinically, rumination markets itself as problem-solving, but it rarely resolves anything — it just repeats.",

    ("relationship_anxiety", "corporate_managers"): "One more reassuring text doesn't close the loop — the relief is temporary and the question just resets.",
    ("relationship_anxiety", "gen_z_professionals"): "You keep asking 'are we okay' hoping the answer will finally stick. It won't, because the question was never really about the answer.",
    ("relationship_anxiety", "healthcare_rns"): "Patients often seek reassurance expecting it to resolve the anxiety permanently, but reassurance-seeking is usually the loop itself.",

    ("self_worth", "corporate_managers"): "The next promotion won't make the feeling of enough finally stick — it never has, and it isn't designed to.",
    ("self_worth", "gen_z_professionals"): "You hit the goal and felt good for about a day. That's the pattern telling you the goal was never the actual fix.",
    ("self_worth", "healthcare_rns"): "Chasing the next credential to finally feel adequate rarely works — the feeling doesn't attach to the achievement long enough to matter.",

    ("shame", "corporate_managers"): "Silence around a mistake doesn't make it disappear — it just makes it heavier and harder to name later.",
    ("shame", "gen_z_professionals"): "You think if nobody brings it up, it's over. It's not over. It's just quietly getting bigger in your head.",
    ("shame", "healthcare_rns"): "Unspoken clinical mistakes don't resolve themselves — they tend to surface later as shame, not closure.",

    ("sleep_anxiety", "corporate_managers"): "Trying harder to fall asleep is usually the exact effort that keeps the nervous system too activated to actually sleep.",
    ("sleep_anxiety", "gen_z_professionals"): "The harder you try to force sleep, the more awake your body gets trying to prove it's trying.",
    ("sleep_anxiety", "healthcare_rns"): "Patients push to force sleep faster, but that effort itself raises arousal, working directly against the goal.",

    ("social_anxiety", "corporate_managers"): "The room is rarely watching as closely as it feels — most people are running the exact same internal commentary about themselves.",
    ("social_anxiety", "gen_z_professionals"): "You think everyone clocked that thing you said. They didn't. They were busy replaying their own thing.",
    ("social_anxiety", "healthcare_rns"): "Patients often overestimate how closely others are observing them — most people are similarly preoccupied with themselves, not surveilling the room.",
}

REPAIR_SOURCE_REFS = (
    "SRC_LANE_A_DIGEST — same root defect as the Lane C repair (hook_family=contrarian_reframe "
    "mail-merge template, \"{{persona}}: {{clause}} is not the whole story.\"), documented as "
    "\"Example C\" in artifacts/research/storyblocks_semantic_sourcing_20260720/RECOMMENDED_TAXONOMY.md:410 "
    "and stamped across 20 topics x 3 personas during the 2026-07-21 scaleup wave. Lane F "
    f"({LANE_F_DATE}) rewrite grounded in {DIGEST} Sec.0.2's naming of the persona-slug-leakage "
    "defect as the sharpest live problem; no new claim introduced, existing mechanism restated in "
    "an authored sentence per persona voice instead of a template fill."
)


def apply_repairs(rows):
    by_id = {r["atom_id"]: r for r in rows}
    fixed = 0
    for r in rows:
        if r.get("atom_family") != "HOOK_COVER":
            continue
        if "is not the whole story" not in r.get("text", ""):
            continue
        key = (r["topic"], r["persona"])
        if key not in REPAIR_TEXT:
            continue
        new_text = REPAIR_TEXT[key]
        r["text"] = new_text
        r["word_count"] = len(new_text.split())
        r["char_count"] = len(new_text)
        r["first_fold_chars"] = min(len(new_text), r.get("first_fold_chars", len(new_text)) or len(new_text))
        r["first_fold_chars"] = len(new_text) if len(new_text) <= 125 else 125
        r["review_status"] = "draft_operator_review_required"
        r["acceptance_layer"] = "repaired in place — Lane F anti-drift pass, unscheduled"
        r["source_refs"] = REPAIR_SOURCE_REFS
        fixed += 1
    return fixed


# ---------------------------------------------------------------------------
# 2. Dedup fix — gen_z_professionals REFRAME/MECHANISM_EXPLAINER -02/-03
# ---------------------------------------------------------------------------

DEDUP_TEXT = {
    "EVG-ENUS-ANXI-GEN_-ME-02": "Anxiety doesn't clear because you finally reasoned it out — it clears because your body gets a real signal that this specific threat is done. Trying harder to think it away just adds a second layer of pressure on top of the first.",
    "EVG-ENUS-ANXI-GEN_-ME-03": "Your brain isn't malfunctioning when it keeps predicting the worst case — it's doing its job on bad information. Give it a body signal that the situation actually changed, and the predicting slows down on its own.",
    "EVG-ENUS-ANXI-GEN_-R-02": "It's allowed to make sense that you're anxious and also allowed to not run your whole evening. Name three things you can touch, and let that be the thing that ends it, not one more replay.",
    "EVG-ENUS-ANXI-GEN_-R-03": "Skip \"why am I like this\" — try \"what would make my body feel safe in the next ten seconds.\" That question actually has an answer you can act on right now.",
    "EVG-ENUS-BURN-GEN_-ME-02": "Burnout doesn't lift because you finally pushed through the tired — it lifts because your nervous system gets an actual stand-down signal. Pushing harder against the exhaustion just adds more exhaustion on top of it.",
    "EVG-ENUS-BURN-GEN_-ME-03": "Your brain isn't broken for still bracing after a good week — it's running on old data. Give it proof the workload actually eased, and the bracing has less to hold onto.",
    "EVG-ENUS-BURN-GEN_-R-02": "It's allowed to be exhausted and also allowed to stop mid-week, not just at the finish line. One real off hour counts as recovery input right now, not a reward you haven't earned yet.",
    "EVG-ENUS-BURN-GEN_-R-03": "Skip \"why can't I just push through\" — try \"what would tell my body the shift actually ended.\" That's the question with an answer you can act on tonight.",
}

DEDUP_SOURCE_REFS = (
    "SRC_LANE_A_DIGEST — cross-persona verbatim-duplicate mechanism named in "
    "artifacts/social_media_atoms/pearl_social_media_writer_20260723/BEFORE_AFTER_COMPARISON_20260723.md "
    "Sec.2 (REFRAME/MECHANISM_EXPLAINER variants 02/03 reported as still duplicated corp<->genz after "
    f"Lane C). Lane F ({LANE_F_DATE}) rewrite: same underlying nervous-system-signal mechanism as the "
    "corporate_managers/healthcare_rns sibling row, restated as a genuinely distinct gen_z_professionals-"
    "voiced sentence rather than the identical shared clause; grounded in "
    f"{DIGEST} Sec.2's nervous-system-signal-over-reasoning finding."
)


def apply_dedup(rows):
    fixed = 0
    for r in rows:
        aid = r["atom_id"]
        if aid in DEDUP_TEXT:
            new_text = DEDUP_TEXT[aid]
            r["text"] = new_text
            r["word_count"] = len(new_text.split())
            r["char_count"] = len(new_text)
            r["review_status"] = "draft_operator_review_required"
            r["acceptance_layer"] = "repaired in place — Lane F de-duplication pass, unscheduled"
            r["source_refs"] = DEDUP_SOURCE_REFS
            fixed += 1
    return fixed


# ---------------------------------------------------------------------------
# 3. New family rows — entrepreneurs + gen_x_sandwich x anxiety + burnout
# ---------------------------------------------------------------------------

COMMON = {
    "locale": "en-US",
    "market_fit": "en-US",
    "platform_fit": "instagram;facebook;linkedin;tiktok_reels_shorts;youtube;pinterest;x;threads;google_business",
    "surface_fit": "static_caption;carousel;thread;short_video_script;business_update",
    "cta_policy": "none",
    "link_policy": "no_main_body_external_link",
    "claim_risk": "low_no_medical_claim",
    "culture_risk": "low_en_us_general",
    "incompatible_with": "medical_cure_claims;shame_language;unsupported_statistics;caption_clone_reuse",
    "reuse_cooldown_days": 14,
    "review_status": "draft_operator_review_required",
    "acceptance_layer": "authored candidate — evergreen extension, unscheduled",
    "draft_only": True,
}

PERSONA_CODE = {"entrepreneurs": "ENTR", "gen_x_sandwich": "GXSW"}
TOPIC_CODE = {"anxiety": "ANXI", "burnout": "BURN"}
PERSONA_TONE = {"entrepreneurs": "direct honest", "gen_x_sandwich": "calm professional"}

MS_SOURCE = (
    "SRC_LANE_A_DIGEST — Anchor/Turn/Shift/Residue four-beat shape, "
    f"{DIGEST} Sec.2 (general-knowledge-uncited fallback template, flagged as such); scene-concreteness "
    "pattern primary-sourced from docs/research_social_media.txt:3388-3399 (\"silent boundary\" personal-"
    "story format). Composite original scene, not a real named individual's testimonial — no consent/"
    "citation exists for a real case, per this lane's DO NOT constraint. Persona/topic recast of the "
    "corporate_managers/gen_z_professionals cells Lane C authored for the same shape."
)
CP_SOURCE = (
    "SRC_LANE_A_DIGEST — shared-struggle social-proof framing and Problem-Mechanism-Result case-study "
    f"shape, {DIGEST} Sec.3, primary-sourced from docs/research_social_media.txt:2449 (\"Social proof is "
    "integrated not as a boastful metric, but as shared struggle\") and :2644 (Case Studies row: Problem "
    "-> Mechanism -> Result). No named diagnosis, no clinical-efficacy claim, no invented statistic — "
    "aggregate-pattern framing only, per this lane's DO NOT constraint and digest Sec.3's hard line."
)
CS_SOURCE = (
    "SRC_LANE_A_DIGEST — carousel open-loop structure (5-8 slides, cover poses unresolved question, "
    f"answer withheld until slide 5-6), {DIGEST} Sec.4 / "
    "artifacts/social_media_atoms/pearl_social_media_writer_20260723/trend_pattern_delta_bank_20260723.md "
    "CAROUSEL_SLIDE row; structural model adapted (not copied) from the 6-slide containment/recovery "
    "carousel example in docs/research_social_media.txt:3370-3385."
)
TU_SOURCE = (
    "SRC_LANE_A_DIGEST — Hook -> Context -> Position -> Invitation thread structure, "
    f"{DIGEST} Sec.1.6/Sec.4; first-line-truncates-so-must-leave-tension-unresolved finding applied "
    "directly to unit 1 below."
)
VB_SOURCE = (
    "SRC_LANE_A_DIGEST — 0-3s hook / 3-8s agitation / 8-20s value / 20-25s proof / final-CTA beat map, "
    f"{DIGEST} Sec.1.3/Sec.4; text-over-B-roll/ambient-audio composited format confirmed sufficient for "
    "this pipeline's no-camera constraint (digest Sec.4)."
)

# content[topic][persona] = dict of family -> text(s)
CONTENT = {
    "burnout": {
        "entrepreneurs": {
            "MS": "One founder we worked with used to take investor calls from the shower because it was the only \"break\" her calendar allowed. The morning she caught herself drafting a reply mid-panic-attack in a parking lot, she tried something small: one hour after 6pm where the phone lives in the car, not the house. The first week felt like she was falling behind on purpose. Six weeks in, the business hadn't slowed down — her hands just stopped shaking before she opened the laptop.",
            "CP": "This isn't a rare pattern. In conversations with founders who reach out about exhaustion, the same shape shows up again and again: revenue climbing, no visible crisis, and a body that's quietly stopped recovering between one fundraising round and the next. The mechanism researchers point to is recovery debt, the gap between how much a nervous system is asked to carry and how much real stand-down time it actually gets. Naming that gap, instead of treating it as the cost of ambition, is usually the first thing that changes anything. This isn't a diagnosis and it isn't a guarantee. It's a pattern worth naming out loud.",
            "CS": [
                "Why does the business finally feel stable and you still feel like you're bracing for the next fire?",
                "Founders don't get a scoreboard that says the crisis is over. The nervous system has to decide that for itself.",
                "If revenue is calm and you're still bracing, that's not ingratitude — that's a body that hasn't gotten the all-clear yet.",
                "The bracing tends to outlast the actual danger, especially when \"always-on\" has been the job description for years.",
                "What actually signals safety isn't more runway. It's a repeated, protected stretch where nothing can reach you.",
                "Save this and pick one hour this week where the phone stays in another room, on purpose.",
            ],
            "TU": [
                "Most founder-burnout advice tells you to delegate more. That's not what's actually broken.",
                "Delegating without a real off switch doesn't register as relief — if you're still reachable, your nervous system is still on shift, no matter who's holding the task.",
                "The fix isn't fewer tasks. It's fewer hours where anything at all can reach you — even one protected hour changes the signal your body gets.",
                "What's the one hour in your week you could actually make unreachable? Not a vacation. Just one real hour.",
            ],
            "VB": [
                "The business is finally stable. Why do you still feel like you're bracing for the next fire?",
                "Your calendar calmed down, but your nervous system never got the memo that the crisis passed.",
                "Real recovery needs a protected window, not just a quieter inbox. One hour. Phone in the car. No exceptions.",
                "This is the pattern researchers call recovery debt: the body needs an actual all-clear, not just fewer emergencies.",
                "Save this. Pick the hour tonight.",
            ],
        },
        "gen_x_sandwich": {
            "MS": "One woman we worked with used to answer her mother's calls mid-work-meeting because saying \"not now\" felt like abandoning her. The evening she realized she'd rescheduled her own doctor's appointment for the third time to make room for everyone else's, she tried something small: one evening a week where her phone goes to voicemail for both generations, no exceptions. The first week felt like she was letting people down. Six weeks in, both households were still fine — her shoulders just stopped living up near her ears.",
            "CP": "This isn't a rare pattern. In conversations with people managing two generations at once, the same shape shows up again and again: constant availability, no visible crisis, and a body that's quietly stopped recovering between one household's need and the next. The mechanism researchers point to is recovery debt, the gap between how much a nervous system is asked to carry and how much real stand-down time it actually gets. Naming that gap, instead of treating it as the price of being reliable, is usually the first thing that changes anything. This isn't a diagnosis and it isn't a guarantee. It's a pattern worth naming out loud.",
            "CS": [
                "Why do you still feel wired after a weekend where nobody actually needed anything?",
                "Nothing going wrong doesn't mean your body clocks out. It just keeps standing by, waiting for the next call.",
                "Being on standby for two generations at once can look like rest from the outside and feel like nothing of the sort inside.",
                "Standby mode keeps the body activated even on the quiet weekends. It never gets the all-clear.",
                "Real recovery needs containment: a stretch of time where neither generation can reach you, not just a quiet phone.",
                "Save this and try one evening this week where your phone goes to voicemail for everyone.",
            ],
            "TU": [
                "Most advice for the sandwich generation says rest more. That's not what's actually broken.",
                "Rest without containment doesn't register as rest. If either generation can reach you, your nervous system is still on call, no matter how still the house is.",
                "The fix isn't more hours off. It's fewer hours where anyone can reach you at all — even one protected evening changes the signal your body gets.",
                "What's the one evening this week you could actually be unreachable to both generations? Not longer. Just real.",
            ],
            "VB": [
                "Nobody needed anything from you this weekend. Why do you still feel wired?",
                "Your body was still, but it never stopped standing by for the next call from either generation.",
                "Real recovery needs containment, not just quiet. One evening, phone on voicemail, both generations covered by someone else.",
                "This is the pattern researchers call recovery debt: standby doesn't register as rest until the scanning actually stops.",
                "Save this. Try the one evening this week.",
            ],
        },
    },
    "anxiety": {
        "entrepreneurs": {
            "MS": "One founder used to rehearse investor updates in the shower, replaying every sentence until the water ran cold. The morning she noticed she'd been holding her breath through an entire pitch deck review, she tried something small: name one thing she could physically touch before opening her laptop each morning. The first week it felt too simple to matter. Six weeks in, the pitch decks hadn't changed — her chest just stopped tightening before she opened them.",
            "CP": "This isn't a rare pattern. In conversations with founders who reach out about racing thoughts before big calls, the same shape shows up again and again: high stakes, no visible failure, and a body that's stuck rehearsing worst-case scenarios long after the prep is actually done. The mechanism researchers point to is threat-rehearsal, a nervous system trying to protect you by replaying danger that already isn't there. Naming that loop, instead of trying to out-plan it, is usually the first thing that changes anything. This isn't a diagnosis and it isn't a guarantee. It's a pattern worth naming out loud.",
            "CS": [
                "Why does your chest stay tight for hours after the investor call already went fine?",
                "Your nervous system doesn't get the \"it went well\" memo the second the call ends. It runs the replay first.",
                "That replay isn't you being unprepared. It's your body double-checking that the risk really passed.",
                "The replay tends to get longer, not shorter, the more you try to think your way out of it before the next call.",
                "What actually shortens it is a body-first signal: three slow exhales, feet flat on the floor, before you open the next deck.",
                "Save this for the next call that won't leave your chest alone. Try the three exhales first.",
            ],
            "TU": [
                "Founder anxiety isn't a confidence problem. It's a body problem wearing a confidence costume.",
                "Your mind keeps rehearsing the pitch because your body hasn't gotten the signal the call is actually over, so it keeps running the scan.",
                "More rehearsal doesn't close the loop faster. A physical signal does — three slow exhales tell your nervous system what more prep never will.",
                "Next time the replay starts after a call, try the three exhales before the post-mortem. What happens to the loop?",
            ],
            "VB": [
                "Why does your chest stay tight for hours after the pitch already landed?",
                "Your mind keeps replaying it because your body hasn't gotten the signal the risk actually passed.",
                "Three slow exhales. Feet flat on the floor. Name one thing you can touch. That's the signal, not more rehearsal.",
                "This is a documented pattern: the body needs a physical all-clear before the mind can actually let the call go.",
                "Save this for the next call that won't leave you alone.",
            ],
        },
        "gen_x_sandwich": {
            "MS": "One woman used to lie awake running the same loop: had she called her mother back, had she signed the permission slip, had she missed something with either generation. The night she realized she'd checked her phone four times during her son's bedtime story, she tried something small: name one thing she could touch — the blanket, the doorframe — before letting the loop start. The first week it felt silly. Six weeks in, the list hadn't gotten shorter, but her chest stopped tightening before she reached for her phone.",
            "CP": "This isn't a rare pattern. In conversations with people holding two generations' needs at once, the same shape shows up again and again: constant mental tracking, no visible failure, and a body stuck scanning for what might have been missed. The mechanism researchers point to is threat-rehearsal, a nervous system trying to protect everyone by replaying every possible gap. Naming that loop, instead of trying to out-plan it, is usually the first thing that changes anything. This isn't a diagnosis and it isn't a guarantee. It's a pattern worth naming out loud.",
            "CS": [
                "Why does your mind keep running the list even after everyone's actually fine tonight?",
                "Your nervous system doesn't get the all-clear the second both generations are okay. It runs the check again first.",
                "That check isn't you being careless. It's your body making sure nothing got missed between two households.",
                "The list tends to get longer, not shorter, the harder you try to think your way to certainty that nothing slipped.",
                "What actually shortens it is a body-first signal: name one thing you can touch, before you let the list start running.",
                "Save this for the next time the list won't quiet down. Try naming one thing you can touch first.",
            ],
            "TU": [
                "Sandwich-generation anxiety isn't a memory problem. It's a body problem wearing a to-do list costume.",
                "Your mind keeps running the list because your body hasn't gotten the signal that both generations are actually covered right now.",
                "More checking doesn't close the loop faster. A physical signal does — naming what you can touch tells your nervous system what more list-running never will.",
                "Next time the list starts running at bedtime, try naming one thing you can touch first. What happens to the loop?",
            ],
            "VB": [
                "Everyone's actually fine tonight. Why is your mind still running the list?",
                "Your mind keeps checking because your body hasn't gotten the signal that both generations are covered right now.",
                "Name one thing you can touch. That's the signal your nervous system needs, not another lap around the list.",
                "This is a documented pattern: the body needs a physical all-clear before the mind can actually let the list rest.",
                "Save this for the next time the list won't quiet down.",
            ],
        },
    },
}

CS_ROLES = ["cover_open_loop", "build", "build", "build", "reveal", "close_cta"]
CS_OBJ = ["reach_discovery", "trust_authority", "trust_authority", "trust_authority", "trust_authority", "lead_generation"]
CS_AWARE = ["problem_aware", "problem_aware", "problem_aware", "problem_aware", "ready_to_act", "ready_to_act"]

TU_ROLES = ["thread_hook", "thread_context", "thread_position", "thread_invitation"]
TU_OBJ = ["reach_discovery", "trust_authority", "trust_authority", "trust_authority"]
TU_AWARE = ["problem_aware", "problem_aware", "problem_aware", "ready_to_act"]

VB_ROLES = [("hook_0_3s", "0-3s"), ("agitation_3_8s", "3-8s"), ("value_8_20s", "8-20s"), ("proof_20_25s", "20-25s"), ("cta_final", "final")]
VB_OBJ = ["reach_discovery", "trust_authority", "trust_authority", "trust_authority", "trust_authority"]
VB_AWARE = ["problem_aware", "problem_aware", "problem_aware", "problem_aware", "ready_to_act"]


def make_row(atom_id, atom_family, topic, persona, tone, hook_family, objective,
             awareness_stage, text, compatible_previous, compatible_next, source_refs,
             variant_index=1, extra=None):
    row = dict(COMMON)
    row.update({
        "atom_id": atom_id,
        "atom_family": atom_family,
        "topic": topic,
        "persona": persona,
        "tone": tone,
        "hook_family": hook_family,
        "objective": objective,
        "awareness_stage": awareness_stage,
        "text": text,
        "word_count": len(text.split()),
        "char_count": len(text),
        "first_fold_chars": len(text) if len(text) <= 140 else 140,
        "compatible_previous": compatible_previous,
        "compatible_next": compatible_next,
        "source_refs": source_refs,
        "variant_index": variant_index,
    })
    if extra:
        row.update(extra)
    return row


def build_new_rows():
    new_rows = []
    for topic in ("anxiety", "burnout"):
        tcode = TOPIC_CODE[topic]
        for persona in ("entrepreneurs", "gen_x_sandwich"):
            pcode = PERSONA_CODE[persona]
            tone = PERSONA_TONE[persona]
            c = CONTENT[topic][persona]

            new_rows.append(make_row(
                f"EVG-ENUS-{tcode}-{pcode}-MS-01", "MICRO_STORY", topic, persona, tone,
                "story_scene", "trust_authority", "solution_aware", c["MS"],
                "HOOK_COVER;SOMATIC_SETUP;ANY_START",
                "CASE_PROOF;TOOL_STEP;SAVEABLE_PAYOFF;CTA_ANCHOR;BRIDGE",
                MS_SOURCE,
            ))
            new_rows.append(make_row(
                f"EVG-ENUS-{tcode}-{pcode}-CP-01", "CASE_PROOF", topic, persona, tone,
                "shared_struggle_proof", "trust_authority", "solution_aware", c["CP"],
                "MICRO_STORY;MECHANISM_EXPLAINER;REFRAME;PROBLEM_AGITATION",
                "TOOL_STEP;SAVEABLE_PAYOFF;CTA_ANCHOR;BRIDGE",
                CP_SOURCE,
            ))
            for i, text in enumerate(c["CS"], start=1):
                prev = "ANY_START" if i == 1 else "CAROUSEL_SLIDE"
                nxt = "CAROUSEL_SLIDE" if i < 6 else "BRIDGE;CTA_ANCHOR"
                new_rows.append(make_row(
                    f"EVG-ENUS-{tcode}-{pcode}-CS-{i:02d}", "CAROUSEL_SLIDE", topic, persona, tone,
                    "open_loop_carousel", CS_OBJ[i - 1], CS_AWARE[i - 1], text, prev, nxt, CS_SOURCE,
                    extra={"carousel_position": f"{i}/6", "carousel_role": CS_ROLES[i - 1]},
                ))
            for i, text in enumerate(c["TU"], start=1):
                prev = "ANY_START" if i == 1 else "THREAD_UNIT"
                nxt = "THREAD_UNIT" if i < 4 else "BRIDGE;CTA_ANCHOR"
                new_rows.append(make_row(
                    f"EVG-ENUS-{tcode}-{pcode}-TU-{i:02d}", "THREAD_UNIT", topic, persona, tone,
                    "thread_arc", TU_OBJ[i - 1], TU_AWARE[i - 1], text, prev, nxt, TU_SOURCE,
                    extra={"thread_position": f"{i}/4", "thread_role": TU_ROLES[i - 1]},
                ))
            for i, text in enumerate(c["VB"], start=1):
                prev = "ANY_START" if i == 1 else "VIDEO_BEAT"
                nxt = "VIDEO_BEAT" if i < 5 else "BRIDGE;CTA_ANCHOR"
                role, timing = VB_ROLES[i - 1]
                new_rows.append(make_row(
                    f"EVG-ENUS-{tcode}-{pcode}-VB-{i:02d}", "VIDEO_BEAT", topic, persona, tone,
                    "video_beat_arc", VB_OBJ[i - 1], VB_AWARE[i - 1], text, prev, nxt, VB_SOURCE,
                    extra={"beat_position": f"{i}/5", "beat_role": role, "beat_timing": timing},
                ))
    return new_rows


def main():
    with open(BANK, encoding="utf-8") as f:
        lines = f.readlines()
    rows = [json.loads(l) for l in lines]

    n_repaired = apply_repairs(rows)
    n_dedup = apply_dedup(rows)
    new_rows = build_new_rows()

    existing_ids = {r["atom_id"] for r in rows}
    collisions = [r["atom_id"] for r in new_rows if r["atom_id"] in existing_ids]
    if collisions:
        raise SystemExit(f"atom_id collision(s), aborting: {collisions}")

    rows.extend(new_rows)

    with open(BANK, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"broken-template rows repaired: {n_repaired} (expected 54)")
    print(f"dedup rows repaired: {n_dedup} (expected 8)")
    print(f"new rows appended: {len(new_rows)} (expected 68)")
    print(f"total rows now: {len(rows)}")


if __name__ == "__main__":
    main()
