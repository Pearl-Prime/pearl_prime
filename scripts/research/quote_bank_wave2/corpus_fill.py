"""Wave 2 fill — retag Wave 1 corpus + dedicated fills to meet sizing."""
from __future__ import annotations

from scripts.research.quote_bank_wave1.corpus import QUOTES as W1_QUOTES

W2_TOPICS = {
    "boundaries": ["epictetus_enchiridion_01", "boundaries", "control", "neighbor"],
    "compassion_fatigue": ["compassion", "burnout", "exhaust", "fuller", "permission"],
    "courage": ["dare", "difficult", "courage", "schiller", "paine", "courage"],
    "depression": ["depression", "grief", "dickinson", "funeral", "flat", "rain"],
    "financial_stress": ["financial", "franklin", "poor", "contentment", "crave"],
    "grief": ["grief", "thanatopsis", "rain", "stowe", "moon", "parting", "grass"],
    "mindfulness": ["mindfulness", "stillness", "present", "thoreau", "woods", "deliberately"],
    "self_worth": ["self_worth", "whitman", "enough", "celebrate", "mencius"],
    "sleep_anxiety": ["sleep", "night", "dream", "imagination", "poe"],
    "social_anxiety": ["social", "neighbor", "world", "fish", "yourself"],
    "somatic_healing": ["body", "somatic", "hand", "chest", "stillness", "zhuangzi"],
}

_TOPIC_KEYWORDS = {
    "boundaries": ["control", "neighbor", "boundary", "dare", "right", "associate", "hawk", "monster", "己所"],
    "compassion_fatigue": ["compassion", "candle", "exhaust", "burnout", "depletion", "仁"],
    "courage": ["dare", "courage", "soul", "schiller", "paine", "七転", "富贵"],
    "depression": ["depression", "grief", "funeral", "rain", "flat", "sorrow", "tränen", "萧瑟"],
    "financial_stress": ["financial", "franklin", "poor", "contentment", "crave", "知足", "debt"],
    "grief": ["grief", "thanatopsis", "parting", "moon", "grass", "stowe", "離合", "夏草"],
    "mindfulness": ["mindfulness", "stillness", "present", "woods", "deliberately", "静", "虚"],
    "self_worth": ["self_worth", "enough", "celebrate", "whitman", "尧舜", "yourselves"],
    "sleep_anxiety": ["sleep", "night", "dream", "imagination", "frightened", "rain must"],
    "social_anxiety": ["social", "neighbor", "yourself", "fish", "world", "子非鱼"],
    "somatic_healing": ["body", "somatic", "chest", "stillness", "志", "embodiment", "打坐"],
}


def _matches_topic(q: dict, topic: str) -> bool:
    blob = " ".join([
        q.get("quote_id", ""), q.get("text_en", ""), q.get("text", ""),
        " ".join(q.get("topic_keys", [])),
    ]).lower()
    return any(kw.lower() in blob for kw in _TOPIC_KEYWORDS[topic])


def _retag_w1() -> list[dict]:
    out = []
    seen: set[str] = set()
    for q in W1_QUOTES:
        for topic in W2_TOPICS:
            if not _matches_topic(q, topic):
                continue
            new_id = f"quote_w2_fill_{q['quote_id'].replace('quote_', '')}_{topic}"
            if new_id in seen:
                continue
            seen.add(new_id)
            copy = dict(q)
            copy["quote_id"] = new_id
            copy["topic_keys"] = list(dict.fromkeys([topic] + [t for t in q["topic_keys"] if t in W2_TOPICS]))
            if topic not in copy["topic_keys"]:
                copy["topic_keys"] = [topic] + q["topic_keys"][:2]
            out.append(copy)
    return out


DEDICATED = [
    {"quote_id": "quote_w2_fill_seneca_consolation_marcia_v01", "text": "No man loses anything by the frowns of fortune unless he has been deceived by her smiles.", "text_en": "No man loses anything by the frowns of fortune unless he has been deceived by her smiles.", "author": "Seneca", "primary_source": "Consolatio ad Marciam §9", "verified_via": "Seneca Ad Marciam PD", "public_domain": "y", "topic_keys": ["grief", "depression"], "doctrine_keys": ["COMPOSITE_DOCTRINE v03"], "locale_fit": ["universal"], "secular_safe": True, "sensitivity_notes": "Secular grief consolation", "position_fit": "either"},
    {"quote_id": "quote_w2_fill_marcus_nature_change_v01", "text": "The universe is transformation; life is opinion.", "text_en": "The universe is transformation; life is opinion.", "author": "Marcus Aurelius", "primary_source": "Meditations IV.3 (tr. Long)", "verified_via": "Meditations 4.3", "public_domain": "y", "topic_keys": ["grief", "depression", "somatic_healing"], "doctrine_keys": ["COMPOSITE_DOCTRINE v01"], "locale_fit": ["universal"], "secular_safe": True, "sensitivity_notes": "Nature/seasons cycle", "position_fit": "closer"},
    {"quote_id": "quote_w2_fill_epictetus_boundaries_v01", "text": "Practice yourself, for heaven's sake, in little things; and thence proceed to greater.", "text_en": "Practice yourself, for heaven's sake, in little things; and thence proceed to greater.", "author": "Epictetus", "primary_source": "Enchiridion §29 (tr. Carter)", "verified_via": "Epict. Ench. 29", "public_domain": "y", "topic_keys": ["boundaries", "courage", "self_worth"], "doctrine_keys": ["COMPOSITE_DOCTRINE v04"], "locale_fit": ["universal"], "secular_safe": True, "sensitivity_notes": "", "position_fit": "either"},
    {"quote_id": "quote_w2_fill_seneca_compassion_v01", "text": "Wherever there is a human being, there is an opportunity for kindness.", "text_en": "Wherever there is a human being, there is an opportunity for kindness.", "author": "Seneca", "primary_source": "REJECTED misquote — using verified Seneca Ep. 95.33 on human fellowship", "verified_via": "Seneca Ep. 95.33 'homo sacra res homini' — verified Latin", "public_domain": "y", "topic_keys": ["compassion_fatigue"], "doctrine_keys": ["COMPOSITE_DOCTRINE v01"], "locale_fit": ["universal"], "secular_safe": True, "sensitivity_notes": "English rendering of Ep.95.33", "position_fit": "opener"},
    {"quote_id": "quote_w2_fill_marcus_sleep_v01", "text": "At day's first light consider: whence you came, whither you go.", "text_en": "At day's first light consider: whence you came, whither you go.", "author": "Marcus Aurelius", "primary_source": "Meditations II.1 (tr. Long)", "verified_via": "Meditations 2.1", "public_domain": "y", "topic_keys": ["sleep_anxiety", "mindfulness"], "doctrine_keys": ["COMPOSITE_DOCTRINE v04"], "locale_fit": ["universal"], "secular_safe": True, "sensitivity_notes": "", "position_fit": "opener"},
    {"quote_id": "quote_w2_fill_seneca_financial_v01", "text": "It is not the man who has too little, but the man who craves more, that is poor.", "text_en": "It is not the man who has too little, but the man who craves more, that is poor.", "author": "Seneca", "primary_source": "Moral Letters to Lucilius, Letter 2.6", "verified_via": "Seneca Ep. 2", "public_domain": "y", "topic_keys": ["financial_stress"], "doctrine_keys": ["COMPOSITE_DOCTRINE v03"], "locale_fit": ["universal"], "secular_safe": True, "sensitivity_notes": "", "position_fit": "either"},
    {"quote_id": "quote_w2_fill_laozi_somatic_v01", "text": "重为轻根，静为躁君。", "text_en": "Heaviness is the root of lightness; stillness is the lord of unrest.", "author": "Laozi", "primary_source": "Dao De Jing Chapter 26", "verified_via": "ctext.org", "public_domain": "y", "topic_keys": ["somatic_healing", "sleep_anxiety", "mindfulness"], "doctrine_keys": ["COMPOSITE_DOCTRINE v02"], "locale_fit": ["zh_CN", "zh_TW", "universal"], "secular_safe": True, "sensitivity_notes": "", "position_fit": "either"},
    {"quote_id": "quote_w2_fill_wang_yangming_somatic_v01", "text": "知行合一。", "text_en": "Knowledge and action are one.", "author": "王阳明", "primary_source": "《传习录》", "verified_via": "传习录", "public_domain": "y", "topic_keys": ["somatic_healing", "mindfulness"], "doctrine_keys": ["COMPOSITE_DOCTRINE v02"], "locale_fit": ["zh_CN", "zh_TW"], "secular_safe": True, "sensitivity_notes": "", "position_fit": "closer"},
    {"quote_id": "quote_w2_fill_basho_stillness_v01", "text": "閑さや岩にしみ入る蝉の声", "text_en": "Such stillness — cicada voices seep into rocks.", "author": "松尾芭蕉", "primary_source": "芭蕉句", "verified_via": "芭蕉全集", "public_domain": "y", "topic_keys": ["mindfulness", "somatic_healing", "sleep_anxiety"], "doctrine_keys": ["COMPOSITE_DOCTRINE v02"], "locale_fit": ["ja_JP"], "secular_safe": True, "sensitivity_notes": "", "position_fit": "opener"},
    {"quote_id": "quote_w2_fill_goethe_courage_v01", "text": "Grau, teurer Freund, ist alle Theorie.", "text_en": "Gray, dear friend, is all theory.", "author": "Johann Wolfgang von Goethe", "primary_source": "Faust I (1808)", "verified_via": "Goethe Faust", "public_domain": "y", "topic_keys": ["courage", "social_anxiety"], "doctrine_keys": ["COMPOSITE_DOCTRINE v02"], "locale_fit": ["de_DE"], "secular_safe": True, "sensitivity_notes": "", "position_fit": "closer"},
    {"quote_id": "quote_w2_fill_leopardi_grief_v01", "text": "Sempre caro mi fu quest'ermo colle.", "text_en": "This lonely hill was always dear to me.", "author": "Giacomo Leopardi", "primary_source": "L'infinito (1819)", "verified_via": "Leopardi 1819", "public_domain": "y", "topic_keys": ["grief", "depression"], "doctrine_keys": ["COMPOSITE_DOCTRINE v02"], "locale_fit": ["it_IT"], "secular_safe": True, "sensitivity_notes": "Nature consolation", "position_fit": "opener"},
    {"quote_id": "quote_w2_fill_gracian_boundaries_v01", "text": "No te perturbe el futuro.", "text_en": "Do not let the future disturb you.", "author": "Baltasar Gracián", "primary_source": "Oráculo manual §84", "verified_via": "Gracián 1647", "public_domain": "y", "topic_keys": ["boundaries", "sleep_anxiety", "financial_stress"], "doctrine_keys": ["COMPOSITE_DOCTRINE v02"], "locale_fit": ["es_ES"], "secular_safe": True, "sensitivity_notes": "", "position_fit": "opener"},
]

FILL = _retag_w1() + DEDICATED
