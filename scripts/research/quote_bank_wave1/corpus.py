"""Merge all corpus modules; rejected quotes; sensitivity exclusions."""
from __future__ import annotations

from scripts.research.quote_bank_wave1.corpus_en_us import EN_US
from scripts.research.quote_bank_wave1.corpus_european import EUROPEAN
from scripts.research.quote_bank_wave1.corpus_fill import FILL
from scripts.research.quote_bank_wave1.corpus_ja_jp import JA_JP
from scripts.research.quote_bank_wave1.corpus_stoic import STOIC_UNIVERSAL
from scripts.research.quote_bank_wave1.corpus_universal_extra import UNIVERSAL_EXTRA
from scripts.research.quote_bank_wave1.corpus_zh_cn import ZH_CN
from scripts.research.quote_bank_wave1.corpus_zh_tw import ZH_TW

_raw = STOIC_UNIVERSAL + UNIVERSAL_EXTRA + FILL + EN_US + ZH_CN + ZH_TW + JA_JP + EUROPEAN

# Drop entries marked not public domain or internal placeholders
QUOTES = [q for q in _raw if q.get("public_domain") == "y" and "PLACEHOLDER" not in q.get("sensitivity_notes", "")]

REJECTED = [
    {
        "rejected_id": "reject_frankl_stimulus_response_space",
        "claimed_text": "Between stimulus and response there is a space.",
        "claimed_author": "Viktor Frankl",
        "reason": "Misattribution — Stephen Covey paraphrase, not in Man's Search for Meaning",
        "verified_via": "Quote Investigator; Frankl estate; Covey acknowledged origin",
        "topic_keys": ["anxiety"],
    },
    {
        "rejected_id": "reject_einstein_fish_climbing",
        "claimed_text": "Everybody is a genius. But if you judge a fish by its ability to climb a tree...",
        "claimed_author": "Albert Einstein",
        "reason": "No primary source; earliest attribution decades after death",
        "verified_via": "Quote Investigator QI Einstein fish",
        "topic_keys": ["adhd_focus", "imposter_syndrome"],
    },
    {
        "rejected_id": "reject_james_greatest_weapon_stress",
        "claimed_text": "The greatest weapon against stress is our ability to choose one thought over another.",
        "claimed_author": "William James",
        "reason": "Misattribution — no match in James corpus",
        "verified_via": "Quote Investigator; James Principles searched",
        "topic_keys": ["anxiety", "overthinking"],
    },
    {
        "rejected_id": "reject_buddha_holding_anger_poison",
        "claimed_text": "Holding on to anger is like drinking poison and expecting the other person to die.",
        "claimed_author": "Buddha",
        "reason": "No Pali/Chinese canonical source; modern self-help origin",
        "verified_via": "Fake Buddha Quotes (Bodhipaksa); Pali Text Society search",
        "topic_keys": ["anxiety", "grief"],
    },
    {
        "rejected_id": "reject_lincoln_internet_quotes",
        "claimed_text": "Various internet Lincoln quotes on worry/anxiety",
        "claimed_author": "Abraham Lincoln",
        "reason": "Abe Lincoln rule — aggregator-only Lincoln anxiety quotes lack primary source",
        "verified_via": "Quote Investigator Lincoln corpus",
        "topic_keys": ["anxiety", "financial_anxiety"],
    },
    {
        "rejected_id": "reject_leonardo_simplicity_sophistication",
        "claimed_text": "Simplicity is the ultimate sophistication.",
        "claimed_author": "Leonardo da Vinci",
        "reason": "Earliest attribution Apple 1977; not in Leonardo notebooks",
        "verified_via": "Quote Investigator Leonardo simplicity",
        "topic_keys": ["adhd_focus"],
    },
    {
        "rejected_id": "reject_saramago_words_weight",
        "claimed_text": "As palavras têm peso.",
        "claimed_author": "José Saramago",
        "reason": "In copyright (d. 2010); no PD edition",
        "verified_via": "Copyright status Brazil/EU",
        "topic_keys": ["overthinking"],
    },
    {
        "rejected_id": "reject_nietzsche_frankl_why_how_swap",
        "claimed_text": "He who has a why to live can bear almost any how.",
        "claimed_author": "Viktor Frankl",
        "reason": "Nietzsche origin (Twilight of the Idols); Frankl quoted Nietzsche but did not author",
        "verified_via": "Quote Investigator; Nietzsche Götzen-Dämmerung §8",
        "topic_keys": ["burnout", "anxiety"],
    },
]

SENSITIVITY_EXCLUSIONS = [
    {
        "exclusion_id": "sens_zh_cn_dalai_lama",
        "figure": "Dalai Lama",
        "locale_cluster": "zh_CN",
        "reason": "Politically sensitive religious figure in PRC market",
        "action": "excluded from zh_CN corpus",
    },
    {
        "exclusion_id": "sens_zh_cn_western_political",
        "figure": "Western political icons (Lincoln, Churchill, etc.)",
        "locale_cluster": "zh_CN",
        "reason": "Hard exclusion per locale-fit design",
        "action": "excluded from zh_CN corpus",
    },
    {
        "exclusion_id": "sens_zh_cn_religious_figures",
        "figure": "Jesus/Buddha devotional one-liners",
        "locale_cluster": "zh_CN",
        "reason": "Religious figures sensitive in PRC secular composite brands",
        "action": "secular_safe:false excluded from zh_CN or teacher-mode only",
    },
    {
        "exclusion_id": "sens_ja_secular_dogen",
        "figure": "Dōgen Zen quotes",
        "locale_cluster": "ja_JP",
        "reason": "Tagged secular_safe:false — composite brands must skip",
        "action": "included with secular_safe:false for teacher-mode only",
    },
    {
        "exclusion_id": "sens_de_luther",
        "figure": "Martin Luther",
        "locale_cluster": "de_DE",
        "reason": "Religious reformer — secular composite brands skip",
        "action": "secular_safe:false",
    },
    {
        "exclusion_id": "sens_es_religious_proverb",
        "figure": "Dios le ayuda proverb",
        "locale_cluster": "es_ES",
        "reason": "Religious idiom — teacher-mode only",
        "action": "secular_safe:false",
    },
]
