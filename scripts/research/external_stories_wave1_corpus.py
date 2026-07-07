"""Wave 1 external stories — combined corpus for emit pipeline."""
from scripts.research.external_stories_wave1_anxiety import ANXIETY_STORIES
from scripts.research.external_stories_wave1_burnout import BURNOUT_STORIES
from scripts.research.external_stories_wave1_financial import FINANCIAL_ANXIETY_STORIES
from scripts.research.external_stories_wave1_imposter import IMPOSTER_SYNDROME_STORIES
from scripts.research.external_stories_wave1_overthinking import OVERTHINKING_STORIES

STORIES = (
    ANXIETY_STORIES
    + BURNOUT_STORIES
    + OVERTHINKING_STORIES
    + IMPOSTER_SYNDROME_STORIES
    + FINANCIAL_ANXIETY_STORIES
)

# Stories considered during Wave 1 research but rejected — Rule 0 / verification failure.
REJECTED = [
    {
        "candidate_id": "ext_anx_reject_einstein_anxiety_quote_v01",
        "topic_keys": ["anxiety"],
        "reason": "misattribution_risk",
        "detail": (
            "Widely circulated 'God does not play dice' / anxiety-adjacent Einstein quotes "
            "lack primary-source verification for therapeutic use. Rejected per quote-bank "
            "misattribution discipline."
        ),
        "rejected_on": "2026-07-07",
    },
    {
        "candidate_id": "ext_burn_reject_startup_founder_anecdote_v01",
        "topic_keys": ["burnout"],
        "reason": "unverifiable_anecdote",
        "detail": (
            "Aggregator-sourced 'founder slept under desk for 4 years' story with no primary "
            "interview or publication trace. Banned per EXTERNAL_STORIES_BANK_SPEC §2."
        ),
        "rejected_on": "2026-07-07",
    },
    {
        "candidate_id": "ext_over_reject_challenger_engineer_guilt_v01",
        "topic_keys": ["overthinking"],
        "reason": "sensitivity_and_speculation",
        "detail": (
            "Invented interior monologue for Challenger disaster engineers cannot meet "
            "verified_facts_only or paraphrase_attributed standard. Historical event allowed "
            "only with documented public statements."
        ),
        "rejected_on": "2026-07-07",
    },
    {
        "candidate_id": "ext_imp_reject_apocryphal_fermi_v01",
        "topic_keys": ["imposter_syndrome"],
        "reason": "fabricated_dialogue",
        "detail": (
            "Internet meme attributing imposter feelings to Enrico Fermi at Nobel ceremony "
            "has no citable primary source. Rejected Rule 0."
        ),
        "rejected_on": "2026-07-07",
    },
    {
        "candidate_id": "ext_fin_reject_lottery_winner_composite_v01",
        "topic_keys": ["financial_anxiety"],
        "reason": "composite_fiction",
        "detail": (
            "Generic 'lottery winner bought mansion then lost everything' narrative without "
            "named subject and citation. Replaced by Brickman et al. study-based entry."
        ),
        "rejected_on": "2026-07-07",
    },
]

# Locale / brand sensitivity exclusions — mirror quote-bank zh_CN policy.
SENSITIVITY_EXCLUSIONS = [
    {
        "exclusion_id": "sens_ext_western_political_icons_zh_cn",
        "locale_cluster": "zh_CN",
        "rule": "exclude_western_political_icon_stories",
        "detail": (
            "US/Western political figures (e.g. Lincoln melancholy, Churchill arcs) excluded "
            "from zh_CN cluster per EXTERNAL_STORIES_BANK_SPEC §3 — mirror quote bank Western "
            "political icon policy."
        ),
        "example_story_ids": [
            "ext_anx_historical_lincoln_melancholy_v01",
            "ext_over_historical_churchill_decisions_v01",
            "ext_imp_historical_churchill_parliament_v01",
        ],
    },
    {
        "exclusion_id": "sens_ext_devotional_religious_zh_cn",
        "locale_cluster": "zh_CN",
        "rule": "exclude_devotional_religious_one_liners",
        "detail": (
            "Saint-or-scripture anxiety relief anecdotes excluded from secular zh_CN brands "
            "even when historically attested."
        ),
        "example_story_ids": [],
    },
    {
        "exclusion_id": "sens_ext_mass_casualty_graphic_en_us",
        "locale_cluster": "en_US",
        "rule": "paraphrase_only_mass_casualty",
        "detail": (
            "9/11 and similar collective trauma stories permitted only as attributed paraphrase "
            "without graphic detail or invented survivor dialogue."
        ),
        "example_story_ids": ["ext_anx_storycorps_911_v01"],
    },
    {
        "exclusion_id": "sens_ext_karoshi_graphic_ja_jp",
        "locale_cluster": "ja_JP",
        "rule": "public_facts_only_labor_death",
        "detail": (
            "過労死 entries must cite public policy/labor statistics; no sensationalized "
            "individual death recreation."
        ),
        "example_story_ids": ["ext_anx_ja_jp_karoshi_v01"],
    },
    {
        "exclusion_id": "sens_ext_clinical_portrayal_film",
        "locale_cluster": "universal",
        "rule": "nominative_reference_not_clinical_advice",
        "detail": (
            "Films depicting mental illness (e.g. A Beautiful Mind) are nominative_reference only; "
            "must not be presented as diagnostic guidance in secular therapeutic register."
        ),
        "example_story_ids": ["ext_over_film_beautiful_mind_v01"],
    },
]
