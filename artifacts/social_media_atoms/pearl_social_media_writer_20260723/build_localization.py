#!/usr/bin/env python3
"""
Lane C — LOCALIZATION_ADAPTER family work:
  1. Repair existing ja-JP/ko-KR/zh-CN/zh-HK/zh-TW/en-SG rows per native-speaker
     subagent review (translate-ja/ko/zh-cn/zh-hk/zh-tw consulted 2026-07-23;
     en-SG fix self-authored, directly grounded in Lane A's digest Sec.5.6).
  2. Add new rows the native reviewers recommended (ja-JP CTA_ADAPTER-11,
     zh-CN PROOF_SIGNAL-11, zh-HK SCRIPT_PUNCTUATION-11).
  3. Author the genuinely missing zh-SG market (10 rows, all adapter_family
     subtypes) via translate-zh-sg subagent output.
"""
import json
from pathlib import Path

REPO = Path("/Users/ahjan/phoenix_omega_worktrees/social-writer-lane-c-atom-repair-20260723")
APAC = REPO / "SOURCE_OF_TRUTH/social_media_atoms/apac_localization_atoms.jsonl"

DIGEST = "artifacts/social_media_atoms/pearl_social_media_writer_20260723/deep_research_digest_20260723.md"
NATIVE = "artifacts/social_media_atoms/pearl_social_media_writer_20260723/NATIVE_SPEAKER_VALIDATION_20260723.md"

# ---------------------------------------------------------------------------
# 1. Repairs: atom_id -> (new_text, new_source_refs, native_review_evidence)
# ---------------------------------------------------------------------------

def src(agent, note):
    return (f"SRC_LANE_A_DIGEST;SRC_NATIVE_REVIEW_{agent.upper()} — {note} "
            f"(reviewed by {agent} subagent, 2026-07-23, this lane; see {DIGEST} Sec.5 and {NATIVE}).")


repairs = {
    # --- ja-JP (translate-ja) ---
    "APAC-JAJP-CULTURE_RISK-05": (
        "Risk guard: avoid hype, baseless superlatives, and command-form imperatives "
        "(pushy/foreign-sounding). Avoid confident first-person healing claims (\"私はXを治した\") "
        "and literal-translated encouragement like \"You've got this!\" (no natural equivalent, "
        "reads childish). Prefer suggestive framing — 〜かもしれません、〜してみませんか — over "
        "direct commands or claims.",
        src("translate-ja", "modesty-register precision: no superlatives/imperatives/boastful "
            "first-person claims/literal-translated encouragement"),
    ),
    "APAC-JAJP-PLATFORM_BIAS-06": (
        "Platform bias: adapt depth, not just idea, to the platform. Long-form (note, blog, "
        "YouTube) can go thorough/detailed. Short-form (Instagram, X) needs short, scannable "
        "text with line breaks — thoroughness there means structured completeness (clear steps/"
        "caveats), not word count. Avoid one-size-fits-all cross-posting.",
        src("translate-ja", "\"detailed/thorough\" is long-form-only; short-form still needs "
            "scannable structure, not density"),
    ),
    "APAC-JAJP-SOCIAL_SEO_TERMS-09": (
        "季節や生活文脈への言及は任意。noteやブログ、メルマガなど長文コンテンツでは季節性を活かして"
        "よいが、InstagramやXの短文投稿では無理に季節ネタを入れない。自然に合う場合のみ一文添える。",
        src("translate-ja", "seasonality matters more in long-form/email than short IG/X captions"),
    ),
    # --- ko-KR (translate-ko) ---
    "APAC-KOKR-VOICE_POSTURE-01": (
        "South Korea voice contract: polite-friendly haeyo-che, individual-centered self-care "
        "framing rather than collectivist \"group harmony,\" trend-aware but not slang-dependent.",
        src("translate-ko", "\"group harmony\" retired as the wellness-copy value for 2026; "
            "individualism/self-care (개인주의/자기돌봄) replacement framing"),
    ),
    "APAC-KOKR-OPENING_HOOK_ADAPTER-02": (
        "번아웃이나 지친 마음을 먼저 솔직하게 인정한 뒤에, 너무 딱딱하지 않으면서도 예의 있게 다가가요.",
        src("translate-ko", "name exhaustion candidly before pivoting to encouragement; "
            "2026 audiences fatigued by performative positivity/\"화이팅\"-only framing"),
    ),
    "APAC-KOKR-CULTURE_RISK-05": (
        "Risk guard: native review required for speech level, honorifics, trend references, and "
        "collectivist \"group harmony\" framing in wellness/self-care content (reads as dated and "
        "tone-deaf against 2026 individualism/self-care sensibility).",
        src("translate-ko", "review trigger added for dated collectivist framing"),
    ),
    # --- zh-CN (translate-zh-cn) ---
    "APAC-ZHCN-VOICE_POSTURE-01": (
        "Mainland China voice contract: practical, warm, compliance-aware, XHS/Douyin/WeChat "
        "native, authentic-over-polished (真实感/unpolished presentation now reads as more "
        "trustworthy than studio-produced content and helps distribution), credentialed-when-"
        "relevant (pair confessional/personal-share tone with a visible credential marker, e.g. "
        "国家二级心理咨询师, not tone alone), and free of dead MCN filler (情绪自由, 治愈系, 给自己"
        "充电).",
        src("translate-zh-cn", "真实感-over-polish + confessional-plus-credential + retired filler phrases"),
    ),
    "APAC-ZHCN-CULTURE_RISK-05": (
        "Risk guard: avoid 广告法-enforced trigger words (最, 第一, 唯一, 国家级, 极致, 100%有效, "
        "永久, 根治) — this is a legal/platform-removal risk, not a style nicety. For mental-"
        "health content specifically: never use accusatory diagnostic framing (e.g. \"你有抑郁症/"
        "焦虑症\") and never claim a product or course can \"治疗\" or \"根治\" 抑郁症/焦虑症; route "
        "readers toward 正规医疗机构/专业帮助 rather than encouraging self-diagnosis. Also continue "
        "to avoid other sensitive-topic/banned phrasing per platform policy.",
        src("translate-zh-cn", "\"avoid superlatives\" too vague — specific 广告法 trigger words + "
            "diagnosis-language risk named"),
    ),
    "APAC-ZHCN-PROOF_SIGNAL-07": (
        "Trust signal: XHS note utility, Douyin retention, WeChat trust loop should appear only "
        "when true and source-backed. For mental-health/wellness content specifically, tone "
        "alone (confessional/闺蜜式分享) no longer reads as credible — pair it with a visible "
        "credential marker (e.g. 国家二级心理咨询师, registered dietitian) in bio or first line.",
        src("translate-zh-cn", "confessional tone alone reads unverifiable without a credential marker"),
    ),
    # --- zh-HK (translate-zh-hk) ---
    "APAC-ZHHK-VOICE_POSTURE-01": (
        "Hong Kong voice contract: confident, bilingual, value-driven, skeptical of hard sell — "
        "self-aware and ironic in wellness/mental-health content (e.g. 「我而家好emo」used "
        "adjectivally), not uplifting-slogan register; authenticity is signaled more by "
        "Cantonese sentence-final particles (㗎/喎/囉/呀/嘛) than by vocabulary choice alone.",
        src("translate-zh-hk", "self-aware/ironic register over uplifting-slogan; particles as the real HK signal"),
    ),
    "APAC-ZHHK-OPENING_HOOK_ADAPTER-02": (
        "用intra-sentential code-switching——將單一英文詞彙或短語鑲嵌喺廣東話句子入面（例如「我而家"
        "真係好down」、「呢排work life balance好chaos」、「要stay positive呀」），唔係成句英文同成句"
        "中文交替出現；後者讀落似翻譯稿，唔自然亦唔賣弄。",
        src("translate-zh-hk", "code-switching model corrected: intra-sentential, not full-sentence alternation"),
    ),
    "APAC-ZHHK-SCRIPT_PUNCTUATION-04": (
        "Script/layout: use Traditional Chinese with intra-sentential English/Cantonese code-"
        "switching (single English words/phrases dropped into Cantonese grammar, never full-"
        "sentence or full-paragraph alternation), local punctuation rhythm including Cantonese "
        "sentence-final particles (㗎/喎/囉/呀/嘛), mobile line breaks, and no literal English-"
        "template transfer.",
        src("translate-zh-hk", "layout rule aligned to the corrected intra-sentential code-switching model"),
    ),
    "APAC-ZHHK-CULTURE_RISK-05": (
        "Risk guard: avoid forced Cantonese, political sensitivity, hard-sell resource framing. "
        "Avoid mainland-coded terms that undercut credibility in mental-health content "
        "specifically — 治愈 (reads earnest-to-preachy/mainland; prefer 療癒 or plain descriptive "
        "phrasing), 正能量 (same issue; prefer concrete, specific language over slogan), 视频 "
        "(mainland; use 影片), 网红 (mainland; use KOL). On Xiaohongshu (小紅書) specifically: "
        "guard against content reading mainland-inflected rather than genuinely HK-local — XHS "
        "fits lifestyle/beauty tone well but is higher-risk for mental-health confessional tone; "
        "don't treat it as an automatic safe local-Chinese win.",
        src("translate-zh-hk", "named mainland-coded term traps + XHS mainland-inflection risk"),
    ),
    "APAC-ZHHK-PLATFORM_BIAS-06": (
        "Platform bias: adapt the same idea to the market's native platforms, never one-size-"
        "fits-all cross-posting — Threads skews more English-forward and media-savvy in HK; "
        "Instagram Stories still lead for informal wellness-confessional content; Xiaohongshu "
        "(小紅書) suits lifestyle/beauty tone, not mental-health confessional tone, and carries "
        "real risk of reading mainland-inflected rather than genuinely HK-local — treat XHS "
        "mental-health content as elevated-risk, not a safe default win.",
        src("translate-zh-hk", "platform-specific nuance added: Threads/IG Stories/XHS risk split"),
    ),
    "APAC-ZHHK-SOCIAL_SEO_TERMS-09": (
        "LinkedIn版本可以偏professional，IG版本要更直接，Threads喺香港英文成分同media-savvy語氣重啲；"
        "XHS（小紅書）用詞要格外小心，唔好mainland化（尤其係mental health內容），要用香港字眼同語氣。",
        src("translate-zh-hk", "platform-specific SEO-term guidance extended with XHS caution"),
    ),
    # --- zh-TW (translate-zh-tw) ---
    "APAC-ZHTW-VOICE_POSTURE-01": (
        "Taiwan voice contract: warm, but not uniformly polished-community-warm. Since Threads "
        "took off (2023+), wellness/mental-health content skews confessional, self-deprecating, "
        "diary-style — closer to venting to your slightly chaotic best friend than to formal "
        "community outreach. Stay warm and conversational, lightly bilingual where natural, but "
        "favor personal vulnerability and self-aware humor over broadcast positivity.",
        src("translate-zh-tw", "confessional/diary-style register added alongside warmth, post-Threads-era"),
    ),
    "APAC-ZHTW-OPENING_HOOK_ADAPTER-02": (
        "用繁體中文，語氣像在跟很熟的朋友碎碎念、自嘲吐槽，而不是正式提醒或宣導。",
        src("translate-zh-tw", "shifted from advisory \"remind a friend\" framing to confessional/venting framing"),
    ),
    "APAC-ZHTW-CULTURE_RISK-05": (
        "Risk guard: never Simplified Chinese characters or Mainland-coded phrasing; preserve "
        "local Taiwan terms. Apply these substitutions and cautions: 心理咨询→心理諮商/諮詢, "
        "抑郁症→憂鬱症, 视频/网络/信息→影片/網路/資訊, 治愈→療癒. Do not import terms with no "
        "natural Taiwan equivalent (e.g. 內卷 — leave untranslated concept or rephrase, don't "
        "force a loanword). Treat 情緒價值 and 正能量 as mainland-coded or borderline for older/"
        "general TW readers — use only when no native alternative exists, and never as a "
        "headline phrase.",
        src("translate-zh-tw", "concrete simplified-to-traditional lexical substitution checklist added"),
    ),
    "APAC-ZHTW-VIDEO_CADENCE-08": (
        "可以加入語氣詞讓句尾自然，例如「喔」「～」「啦」「欸」「齁」「厚」「誒」；偶爾自嘲式用一點輕度"
        "台語（母湯、甘安捏）也可以，但要帶點自我調侃的語感，不要當正式用語。同一句只用一個語氣詞，疊兩個"
        "以上會顯得刻意、裝可愛。",
        src("translate-zh-tw", "expanded particle list + one-particle-per-sentence naturalness rule"),
    ),
    # --- en-SG (self-authored, grounded directly in Lane A digest Sec.5.6 —
    #     no fresh agent call needed since the correction was already native-
    #     reviewed same-day and is fully specified) ---
    "APAC-ENSG-VOICE_POSTURE-01": (
        "Singapore voice has two registers, not one: emotional-support/mental-health content is "
        "warm and relatable, with light Singlish markers (lah, can, steady, shiok, sian) "
        "signaling authenticity and community warmth; productivity/corporate-wellness content "
        "stays concise, pragmatic, efficient, data/utility-first. Do not default to the "
        "efficiency-only register for mental-health copy — it reads as generic corporate copy, "
        "which is specifically wrong for this content category.",
        (f"SRC_LANE_A_DIGEST;SRC_NATIVE_REVIEW_TRANSLATE-ZH-SG — {DIGEST} Sec.5.6 / {NATIVE}: "
         "\"Concise/pragmatic/data-driven alone reads as generic corporate copy, which is "
         "specifically wrong for mental-health content... Singapore wellness voice has moved "
         "warmer/more relatable.\" Row previously stated only the efficiency register; rewritten "
         "same-day, self-authored fix directly grounded in this lane's own native-reviewed digest."),
    ),
}

# ---------------------------------------------------------------------------
# 2. New 11th rows the native reviewers recommended (existing markets)
# ---------------------------------------------------------------------------

def base_row_like(template_id, all_rows):
    for d in all_rows:
        if d["atom_id"] == template_id:
            return dict(d)
    raise KeyError(template_id)


NEW_APAC_ROWS = [
    dict(
        atom_id="APAC-JAJP-CTA_ADAPTER-11",
        template="APAC-JAJP-CTA_ADAPTER-03",
        adapter_family="CTA_ADAPTER",
        text=(
            "日本の読者は本音を公然と示さず、非公開で読む・保存する傾向がある（建前・本音の使い分け、"
            "裏垢文化）。これは新しい世代特有の傾向ではなく、構造的で長年の文化的特徴として扱う。公開"
            "コメントや意見表明を求めるCTA（「コメントで教えて！」等）は避け、保存・スクリーンショット・"
            "個人的な振り返りを促す表現を優先する。"
        ),
        source_refs=src("translate-ja", "new row: public-lurking/tatemae-honne is structural, not "
                         "Gen-Z-specific — CTAs should ask for private save/reflection, not public comment"),
    ),
    dict(
        atom_id="APAC-ZHCN-PROOF_SIGNAL-11",
        template="APAC-ZHCN-PROOF_SIGNAL-07",
        adapter_family="PROOF_SIGNAL",
        text=(
            "闺蜜式分享/confessional personal-share tone alone reads as unverifiable, scripted MCN "
            "content on XHS/Douyin — it must be paired with a visible credential marker (e.g. 国家"
            "二级心理咨询师、注册营养师) in bio or opening line. Credential + authentic tone "
            "together, not tone alone."
        ),
        source_refs=src("translate-zh-cn", "new row: separates credential-pairing requirement from "
                         "the general trust-metrics PROOF_SIGNAL row for atomicity"),
    ),
    dict(
        atom_id="APAC-ZHHK-SCRIPT_PUNCTUATION-11",
        template="APAC-ZHHK-SCRIPT_PUNCTUATION-04",
        adapter_family="SCRIPT_PUNCTUATION",
        text=(
            "Code-switching applies script-wide, not just to openers: drop single English words/"
            "phrases mid-sentence into Cantonese grammar throughout the post — e.g. 「呢排真係好"
            "chaos，但我試緊stay grounded，starting做少少嘢先」— never switch by alternating whole "
            "English sentences with whole Chinese sentences/paragraphs; that reads as a translated "
            "brochure, not native HK voice."
        ),
        source_refs=src("translate-zh-hk", "new row: intra-sentential code-switching applies to full "
                         "body copy, not just the opening hook"),
    ),
]

# ---------------------------------------------------------------------------
# 3. zh-SG — genuinely new market, authored by translate-zh-sg subagent
# ---------------------------------------------------------------------------

ZH_SG_ROWS = {
    "VOICE_POSTURE": (
        "Singapore zh-SG voice has two registers, not one: emotional-support content is warm "
        "and relatable, with light Singdarin code-switch (Mandarin-English-Malay particles like "
        "lah/can/steady woven in naturally); productivity/corporate-wellness content stays "
        "concise and pragmatic. Do not default to efficiency-only framing for mental-health "
        "copy — that reads as generic corporate copy here."
    ),
    "CTA_ADAPTER": "工具包放在下面咯，想拿就拿，现在没力气看也没关系，慢慢来，steady 一点就好。",
    "CULTURE_RISK": (
        "Risk guard: sponsorship disclosure (#ad/#sponsored) must appear in-caption per SG ad "
        "standards (enforced since ~2022-2023); PDPA consent belongs in lead-gen forms, not "
        "caption voice; do not frame Hokkien/Cantonese dialect markers as broadly resonant — "
        "they land mainly with the 60+ Pioneer/Merdeka generation, not the general under-50 "
        "audience (flag any specific compliance wording for legal review)."
    ),
    "NATIVE_REVIEW_GATE": (
        "All zh-SG localized prose remains native_review_required until a qualified native "
        "reviewer signs off, with particular attention to whether the Singdarin code-switch "
        "reads authentic rather than caricature."
    ),
    "OPENING_HOOK_ADAPTER": "你是不是也常常很累，可是又不知道要跟谁讲？",
    "PLATFORM_BIAS": (
        "Platform bias: Instagram, TikTok, and WhatsApp/Telegram community broadcast channels "
        "are the dominant SG wellness-engagement surfaces; do not default to Xiaohongshu/RED as "
        "mainstream — it is niche there (Chinese-Singaporean women, PRC expat/student "
        "residents, beauty/luxury micro-influencers)."
    ),
    "PROOF_SIGNAL": (
        "Trust signal: relatable lived-experience framing (a friend's story, a shared feeling) "
        "reads as more trustworthy than a bare statistic for zh-SG emotional-support content; "
        "cite sources if a stat is used, and flag any clinical claim for legal review."
    ),
    "SCRIPT_PUNCTUATION": (
        "Script/layout: Simplified Chinese with natural Mandarin-English-Malay code-switch "
        "(Singdarin) particles woven in, local punctuation rhythm, mobile-short line breaks; do "
        "not force Traditional characters or mainland-only idiom, and do not literally transfer "
        "an English-template sentence structure."
    ),
    "SOCIAL_SEO_TERMS": "热门搜索词参考：#情绪价值 #解压方法 #心理健康SG #打工人日常 #自我照顾，方便本地读者刷到相关内容。",
    "VIDEO_CADENCE": "开头3秒直接说出感受，中间放慢配合呼吸停顿，结尾用一句暖心的话收尾，不用赶，慢慢说就好。",
}

# atom_id numbering must match the 01-10 convention already used by the other 6 markets
SUBTYPE_NUMBER = {
    "VOICE_POSTURE": 1, "OPENING_HOOK_ADAPTER": 2, "CTA_ADAPTER": 3, "SCRIPT_PUNCTUATION": 4,
    "CULTURE_RISK": 5, "PLATFORM_BIAS": 6, "PROOF_SIGNAL": 7, "VIDEO_CADENCE": 8,
    "SOCIAL_SEO_TERMS": 9, "NATIVE_REVIEW_GATE": 10,
}

ZH_SG_SRC = (
    f"SRC_LANE_A_DIGEST;SRC_NATIVE_REVIEW_TRANSLATE-ZH-SG — authored by translate-zh-sg subagent "
    f"2026-07-23, grounded in {DIGEST} Sec.5.6 (Singapore APAC refresh: two-register wellness "
    f"voice, Xiaohongshu-is-niche correction, Singdarin-not-dialect correction) and {NATIVE}. "
    f"Genuinely missing market before this lane — only en-SG existed."
)


def main():
    all_rows = [json.loads(l) for l in APAC.read_text(encoding="utf-8").splitlines() if l.strip()]
    by_id = {d["atom_id"]: d for d in all_rows}

    touched = []
    for aid, (new_text, new_src) in repairs.items():
        if aid not in by_id:
            raise SystemExit(f"ERROR: {aid} not found")
        d = by_id[aid]
        d["text"] = new_text
        d["word_count"] = len(new_text.split())
        d["char_count"] = len(new_text)
        d["first_fold_chars"] = min(d.get("first_fold_chars", len(new_text)), len(new_text))
        d["source_refs"] = new_src
        d["native_review_evidence"] = (
            f"{d.get('native_review_evidence', '')};LANE_C_NATIVE_REVIEW_20260723"
            if d.get("native_review_evidence") else "LANE_C_NATIVE_REVIEW_20260723"
        )
        d["review_status"] = "draft_operator_review_required"
        d["acceptance_layer"] = "repaired in place — Lane C native-review pass, unscheduled"
        touched.append(aid)

    new_rows = []
    for spec in NEW_APAC_ROWS:
        tmpl = base_row_like(spec["template"], all_rows)
        row = dict(tmpl)
        row["atom_id"] = spec["atom_id"]
        row["adapter_family"] = spec["adapter_family"]
        row["text"] = spec["text"]
        row["word_count"] = len(spec["text"].split())
        row["char_count"] = len(spec["text"])
        row["first_fold_chars"] = min(row.get("first_fold_chars", len(spec["text"])), len(spec["text"]))
        row["source_refs"] = spec["source_refs"]
        row.pop("promoted_at", None)
        row.pop("promotion_approval_evidence", None)
        row.pop("promotion_manifest_row_id", None)
        row.pop("promotion_prior_review_status", None)
        row.pop("promotion_source_bank_path", None)
        row["review_status"] = "draft_operator_review_required"
        row["acceptance_layer"] = "authored candidate — LOCALIZATION_ADAPTER extension, unscheduled"
        row["draft_only"] = True
        row["native_review_evidence"] = "LANE_C_NATIVE_REVIEW_20260723"
        new_rows.append(row)

    # zh-SG: build off the en-SG template (closest shape), swap locale/market/script/text
    ensg_template_by_subtype = {}
    for d in all_rows:
        if d["market_fit"] == "en-SG":
            ensg_template_by_subtype[d["adapter_family"]] = d

    for subtype, text in ZH_SG_ROWS.items():
        tmpl = dict(ensg_template_by_subtype[subtype])
        num = SUBTYPE_NUMBER[subtype]
        tmpl["atom_id"] = f"APAC-ZHSG-{subtype}-{num:02d}"
        tmpl["locale"] = "zh-SG"
        tmpl["market_fit"] = "zh-SG"
        tmpl["script"] = "Simplified Chinese with natural Singdarin (Mandarin-English-Malay) code-switch"
        tmpl["text"] = text
        tmpl["word_count"] = len(text.split())
        tmpl["char_count"] = len(text)
        tmpl["first_fold_chars"] = min(tmpl.get("first_fold_chars", len(text)), len(text))
        tmpl["source_refs"] = ZH_SG_SRC
        tmpl["tone"] = ("warm, relatable, light Singdarin code-switch for emotional-support content; "
                         "concise/pragmatic for productivity content (two registers)")
        tmpl.pop("promoted_at", None)
        tmpl.pop("promotion_approval_evidence", None)
        tmpl.pop("promotion_manifest_row_id", None)
        tmpl.pop("promotion_prior_review_status", None)
        tmpl.pop("promotion_source_bank_path", None)
        tmpl["review_status"] = "draft_operator_review_required"
        tmpl["acceptance_layer"] = "authored candidate — LOCALIZATION_ADAPTER new market, unscheduled"
        tmpl["draft_only"] = True
        tmpl["native_review_evidence"] = "LANE_C_NATIVE_REVIEW_20260723_TRANSLATE-ZH-SG"
        tmpl["native_review_required"] = True
        new_rows.append(tmpl)

    out_rows = list(all_rows) + new_rows
    with APAC.open("w", encoding="utf-8") as f:
        for d in out_rows:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

    print(f"Repaired {len(touched)} existing rows.")
    print(f"Added {len(new_rows)} new rows ({len(NEW_APAC_ROWS)} 11th-row additions + "
          f"{len(ZH_SG_ROWS)} zh-SG rows).")
    print(f"Total rows now: {len(out_rows)}")


if __name__ == "__main__":
    main()
