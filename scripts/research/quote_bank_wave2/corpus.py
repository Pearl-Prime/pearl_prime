"""Merge Wave 2 corpus; rejected; sensitivity exclusions."""
from __future__ import annotations

from scripts.research.quote_bank_wave2.corpus_fill import FILL
from scripts.research.quote_bank_wave2.corpus_locale import LOCALE
from scripts.research.quote_bank_wave2.corpus_universal import UNIVERSAL_ALL

_raw = UNIVERSAL_ALL + LOCALE + FILL
QUOTES = [q for q in _raw if q.get("public_domain") == "y"]

REJECTED = [
    {
        "rejected_id": "reject_w2_kubler_ross_stages",
        "claimed_text": "The five stages of grief (denial, anger, bargaining, depression, acceptance)",
        "claimed_author": "Elisabeth Kübler-Ross",
        "reason": "Stages model misapplied to bereavement; not a verified linear quote for books",
        "verified_via": "Kübler-Ross On Death and Dying — clinical context not proverb",
        "topic_keys": ["grief"],
    },
    {
        "rejected_id": "reject_w2_religious_footprints",
        "claimed_text": "Footprints in the sand — one set of footprints",
        "claimed_author": "Mary Stevenson / anonymous",
        "reason": "Religious consolation — excluded from secular universal clusters",
        "verified_via": "Copyright 1964 Stevenson poem; religious framing",
        "topic_keys": ["grief", "depression"],
    },
    {
        "rejected_id": "reject_w2_psalm_23_aggregator",
        "claimed_text": "The Lord is my shepherd",
        "claimed_author": "Psalm 23",
        "reason": "Religious text — secular_safe false; not in zh_CN secular clusters",
        "verified_via": "Bible Psalm 23 — excluded per locale-fit design",
        "topic_keys": ["grief", "depression"],
    },
    {
        "rejected_id": "reject_w2_twain_misfortune",
        "claimed_text": "I've had a lot of worries in my life, most of which never happened",
        "claimed_author": "Mark Twain",
        "reason": "Misattribution — Montaigne primary per Quote Investigator",
        "verified_via": "QI Montaigne vs Twain",
        "topic_keys": ["sleep_anxiety", "financial_stress"],
    },
]

SENSITIVITY_EXCLUSIONS = [
    {
        "exclusion_id": "sens_w2_zh_cn_religious_grief",
        "figure": "Buddhist/Christian grief consolation",
        "locale_cluster": "zh_CN",
        "reason": "Religious consolation excluded from secular composite brands",
        "action": "Use Laozi/Su Shi nature-seasons canon instead",
    },
    {
        "exclusion_id": "sens_w2_grief_secular_rule",
        "figure": "Religious consolation quotes",
        "locale_cluster": "universal",
        "reason": "Grief/depression Wave 2: favor nature/seasons/endurance over religious",
        "action": "Seneca Consolatio themes OK; Psalm/Footprints rejected",
    },
]
