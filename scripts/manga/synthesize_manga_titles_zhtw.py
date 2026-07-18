#!/usr/bin/env python3
"""
Native zh_TW (Traditional Chinese) manga title / topic / EI-author synthesis.
=============================================================================

Fills the `title` / `localized_titles.zh_TW` / `topic` / `manga_author` fields
(currently ``TBD``) on the live zh_TW series plans at
``config/source_of_truth/manga_series_plans/zh_TW/*.yaml`` (274 series:
270 standard + 4 mecha whose topic+manga_author are already filled).

Per-field provenance (LLM tier policy compliant — NO paid API, NO Qwen/Ollama):
  - title          → AUTHORED by Claude (Tier-1, operator-reviewed). Native
                     Traditional Chinese, genre-faithful (incl. mecha), the
                     wellness `topic` kept as INTERIOR architecture (Genre Shell
                     thesis) — never an explicit self-help / clinical label.
                     Stored in the TITLES table below, keyed by series_id.
  - topic          → deterministic rotation of the brand's primary + secondary
                     topics across its series (covers all topics). Mecha series
                     already carry a topic → left untouched. No LLM.
  - manga_author   → generate_manga_author.generate_display_name (deterministic
                     CJK name pools). Mecha series already authored → left
                     untouched. No LLM.

In-place, idempotent: only `: TBD` lines are rewritten, so partial runs resume
and re-runs never clobber filled values. File comments / field order preserved
(targeted line replacement, not a YAML round-trip). Touches ONLY the zh_TW
locale; 0 deletions.

Usage:
  python3 scripts/manga/synthesize_manga_titles_zhtw.py            # all
  python3 scripts/manga/synthesize_manga_titles_zhtw.py --check    # QA only
  python3 scripts/manga/synthesize_manga_titles_zhtw.py --dry-run  # no writes
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
from generate_manga_author import generate_display_name  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
_MAIN_REPO = Path("/Users/ahjan/phoenix_omega")
ROOT = _MAIN_REPO if (not (REPO_ROOT / "config").exists()
                      and (_MAIN_REPO / "config").exists()) else REPO_ROOT

SERIES_DIR = ROOT / "config" / "source_of_truth" / "manga_series_plans" / "zh_TW"
CANONICAL_BRANDS = ROOT / "config" / "manga" / "canonical_brand_list.yaml"
REVIEW_OUT = ROOT / "artifacts" / "catalog" / "manga" / "ssot_rollup" / "zh_TW_title_synthesis_review.csv"

# ── Clinical / self-help stems that must NEVER appear in a title (leak guard) ──
# Traditional-Chinese wellness/clinical vocabulary that would break the Genre
# Shell. Deliberately EXCLUDES soft words (心, 夢, 光, 影) that are legitimate
# manga vocabulary. Mirrors the ja_JP guard intent.
CLINICAL_STEMS = (
    "焦慮", "倦怠", "療癒", "治療", "自我價值", "自我肯定", "冒名", "創傷",
    "憂鬱", "抑鬱", "心理健康", "症候群", "諮商", "輔導", "自尊", "拖延",
    "注意力", "過度思考", "羞恥", "界線", "邊界", "失眠", "正念", "復原",
)

# Topic → the bare TC wellness word that must not surface verbatim in a title.
TOPIC_ZH: dict[str, str] = {
    "anxiety": "焦慮", "sleep": "失眠", "burnout": "倦怠", "overthinking": "過度思考",
    "grief": "悲傷", "somatic_healing": "療癒", "social_anxiety": "社交焦慮",
    "self_worth": "自我價值", "imposter_syndrome": "冒名", "trauma_recovery": "創傷",
    "shame": "羞恥", "boundaries": "界線", "courage": "勇氣", "compassion": "慈悲",
    "financial_anxiety": "金錢焦慮", "adhd_focus": "注意力", "self_compassion": "自我慈悲",
}

# ── TITLES (Claude-authored, native Traditional Chinese) ─────────────────────
# Key = series_id. Genre-faithful; the wellness topic is INTERIOR architecture,
# never named. Short, striking, bestseller-shaped. Unique within brand AND
# globally. The 4 mecha tentpole/satellite titles carry the Evangelion/Adi-Da
# philosophical-mecha register (mecha as trauma container).
TITLES: dict[str, str] = {
    # ── adhd_forge_mystery (shonen · ADHD/focus·courage·self-worth) ──────────
    "adhd_forge_mystery__zh_TW__action_battle__series01": "百分之一秒的閃電",
    "adhd_forge_mystery__zh_TW__isekai__series01": "轉生成為最弱召喚師",
    "adhd_forge_mystery__zh_TW__psychological_thriller__series01": "不存在的第三名證人",
    "adhd_forge_mystery__zh_TW__sports_competition__series01": "全場唯一沒在看球的人",

    # ── bio_flow_healing (seinen · somatic·overthinking·sleep) ───────────────
    "bio_flow_healing__zh_TW__historical_period__series01": "本草館的最後一味",
    "bio_flow_healing__zh_TW__iyashikei__series01": "慢一拍的早餐店",
    "bio_flow_healing__zh_TW__psychological_thriller__series01": "凌晨三點的訪客",
    "bio_flow_healing__zh_TW__psychological_thriller__series02": "解剖室裡的呼吸聲",
    "bio_flow_healing__zh_TW__sci_fi_cyberpunk__series01": "腦內七十二小時直播",
    "bio_flow_healing__zh_TW__sci_fi_cyberpunk__series02": "睡眠商人",

    # ── body_memory_shojo (josei · somatic·trauma·shame·grief) ───────────────
    "body_memory_shojo__zh_TW__dark_fantasy__series01": "皮膚底下的潮汐",
    "body_memory_shojo__zh_TW__dark_fantasy__series02": "縫補傷痕的繡娘",
    "body_memory_shojo__zh_TW__iyashikei__series01": "無人知曉的小裁縫",
    "body_memory_shojo__zh_TW__iyashikei__series02": "替遺物寫信的女孩",
    "body_memory_shojo__zh_TW__psychological_horror__series01": "鏡子記得每一道疤",
    "body_memory_shojo__zh_TW__psychological_horror__series02": "舊宅不肯遺忘",
    "body_memory_shojo__zh_TW__supernatural_mystery__series01": "藏在喉嚨裡的名字",
    "body_memory_shojo__zh_TW__supernatural_mystery__series02": "失物招領的亡靈",

    # ── bright_presence_tw_seinen (seinen · social·imposter·self-worth) ──────
    "bright_presence_tw_seinen__zh_TW__historical_period__series01": "燈下不語的說書人",
    "bright_presence_tw_seinen__zh_TW__iyashikei__series01": "頂樓那間沒招牌的店",
    # ── MECHA TENTPOLE (Adi Da philosophical-mecha; mecha = trauma container) ─
    "bright_presence_tw_seinen__zh_TW__mecha__series01": "明王機．第七號容器",
    "bright_presence_tw_seinen__zh_TW__mecha__series02": "他人即是我的駕駛艙",
    "bright_presence_tw_seinen__zh_TW__psychological_thriller__series01": "冒充者的最後一場演出",
    "bright_presence_tw_seinen__zh_TW__romance_josei_drama__series01": "你眼中的我太耀眼",

    # ── calm_student_school (shojo · anxiety·social·self-worth) ──────────────
    "calm_student_school__zh_TW__iyashikei__series01": "放學後的空教室",
    "calm_student_school__zh_TW__romance_josei_drama__series01": "與你同桌的第三排",
    "calm_student_school__zh_TW__school_coming_of_age__series01": "我不是班上的誰",
    "calm_student_school__zh_TW__supernatural_mystery__series01": "午夜十二點的鐘樓社",

    # ── career_lift_workplace (josei · imposter·social·financial·burnout) ────
    "career_lift_workplace__zh_TW__iyashikei__series01": "影印機旁的深呼吸",
    "career_lift_workplace__zh_TW__romance_josei_drama__series01": "電梯停在二十三樓",
    "career_lift_workplace__zh_TW__romance_josei_drama__series02": "月底前的告白",
    "career_lift_workplace__zh_TW__supernatural_mystery__series01": "加班到天亮的辦公室",
    "career_lift_workplace__zh_TW__supernatural_mystery__series02": "名片上的另一個我",
    "career_lift_workplace__zh_TW__workplace_drama__series01": "會議室最角落的位子",
    "career_lift_workplace__zh_TW__workplace_drama__series02": "年終獎金的代價",
    "career_lift_workplace__zh_TW__workplace_drama__series03": "提案前一夜",

    # ── cognitive_clarity (seinen · overthinking·imposter·burnout·boundaries) ─
    "cognitive_clarity__zh_TW__dark_fantasy__series01": "千層迷宮的看守人",
    "cognitive_clarity__zh_TW__dark_fantasy__series02": "戴著別人面具的王",
    "cognitive_clarity__zh_TW__dark_fantasy__series03": "燃盡之塔",
    "cognitive_clarity__zh_TW__psychological_thriller__series01": "別越過那條白線",
    "cognitive_clarity__zh_TW__psychological_thriller__series02": "腦海裡的第二個聲音",
    "cognitive_clarity__zh_TW__psychological_thriller__series03": "假冒偵探事務所",
    "cognitive_clarity__zh_TW__psychological_thriller__series04": "燒到最後一根火柴",
    "cognitive_clarity__zh_TW__psychological_thriller__series05": "請勿擅闖此門",
    "cognitive_clarity__zh_TW__sci_fi_cyberpunk__series01": "思緒過載都市",
    "cognitive_clarity__zh_TW__sci_fi_cyberpunk__series02": "贗品意識體",
    "cognitive_clarity__zh_TW__sci_fi_cyberpunk__series03": "系統即將過熱",
    "cognitive_clarity__zh_TW__supernatural_mystery__series01": "畫地為牢的咒",
    "cognitive_clarity__zh_TW__supernatural_mystery__series02": "想太多的降靈會",
    "cognitive_clarity__zh_TW__workplace_drama__series01": "頂替部長的那一天",

    # ── confidence_core_romance (shojo · imposter·self-worth·social) ─────────
    "confidence_core_romance__zh_TW__isekai__series01": "轉生後我才是公爵替身",
    "confidence_core_romance__zh_TW__iyashikei__series01": "甜點櫥窗裡的倒影",
    "confidence_core_romance__zh_TW__romance_josei_drama__series01": "隔著人群看你",
    "confidence_core_romance__zh_TW__romance_josei_drama__series02": "我不是你以為的那個她",
    "confidence_core_romance__zh_TW__romance_josei_drama__series03": "值得被你喜歡嗎",
    "confidence_core_romance__zh_TW__supernatural_mystery__series01": "說不出口的占卜屋",

    # ── creative_unfold_social (shojo · social·self-worth·courage) ───────────
    "creative_unfold_social__zh_TW__action_battle__series01": "畫筆即是我的劍",
    "creative_unfold_social__zh_TW__romance_josei_drama__series01": "個展開幕前的素描",
    "creative_unfold_social__zh_TW__school_coming_of_age__series01": "美術社的逃兵",
    "creative_unfold_social__zh_TW__supernatural_mystery__series01": "畫中走出來的人",

    # ── devotion_path_shonen (josei healing · grief·compassion·courage) ──────
    "devotion_path_shonen__zh_TW__action_battle__series01": "為亡者點燈的劍士",
    "devotion_path_shonen__zh_TW__action_battle__series02": "渡眾生的最後一戰",
    "devotion_path_shonen__zh_TW__cultivation_martial__series01": "踏破萬仞的修行者",
    "devotion_path_shonen__zh_TW__dark_fantasy__series01": "替亡靈守墓的少女",
    "devotion_path_shonen__zh_TW__dark_fantasy__series02": "寬恕是這座城的禁咒",
    "devotion_path_shonen__zh_TW__supernatural_mystery__series01": "敢踏進那道光的人",

    # ── digital_ground (manhwa · burnout·imposter·financial·anxiety·somatic) ─
    "digital_ground__zh_TW__isekai__series01": "轉生成全公司最後一個員工",
    "digital_ground__zh_TW__isekai__series02": "異世界冒充勇者",
    "digital_ground__zh_TW__iyashikei__series01": "存款見底的咖啡館",
    "digital_ground__zh_TW__psychological_horror__series01": "已讀不回的深夜",
    "digital_ground__zh_TW__psychological_horror__series02": "身體傳來的雜訊",
    "digital_ground__zh_TW__psychological_horror__series03": "電量剩百分之一",
    "digital_ground__zh_TW__sci_fi_cyberpunk__series01": "頂替帳號的人",
    "digital_ground__zh_TW__sci_fi_cyberpunk__series02": "餘額不足的城市",
    "digital_ground__zh_TW__sci_fi_cyberpunk__series03": "深夜通知的城市",
    "digital_ground__zh_TW__sci_fi_cyberpunk__series04": "斷線的軀體",
    "digital_ground__zh_TW__sci_fi_cyberpunk__series05": "伺服器即將熔毀",
    "digital_ground__zh_TW__workplace_drama__series01": "頂著別人頭銜的我",
    "digital_ground__zh_TW__workplace_drama__series02": "薪水條上的紅字",
    "digital_ground__zh_TW__workplace_drama__series03": "永遠回不完的訊息",

    # ── executive_calm_workplace (seinen · burnout·overthinking·financial) ───
    "executive_calm_workplace__zh_TW__dark_fantasy__series01": "焚城之主的王座",
    "executive_calm_workplace__zh_TW__psychological_thriller__series01": "董事長的第二個腦袋",
    "executive_calm_workplace__zh_TW__psychological_thriller__series02": "帳本上消失的零",
    "executive_calm_workplace__zh_TW__sci_fi_cyberpunk__series01": "高層即將斷電",
    "executive_calm_workplace__zh_TW__sci_fi_cyberpunk__series02": "決策迴圈過載",
    "executive_calm_workplace__zh_TW__workplace_drama__series01": "下一季的數字",
    "executive_calm_workplace__zh_TW__workplace_drama__series02": "燒光最後一口氣的董座",
    "executive_calm_workplace__zh_TW__workplace_drama__series03": "想得太遠的會議",

    # ── focus_sprint_workplace (seinen · adhd·imposter·social) ───────────────
    "focus_sprint_workplace__zh_TW__action_battle__series01": "三秒內擊中靶心",
    "focus_sprint_workplace__zh_TW__action_battle__series02": "假冒高手的擂台",
    "focus_sprint_workplace__zh_TW__psychological_thriller__series01": "茶水間的耳語",
    "focus_sprint_workplace__zh_TW__sports_competition__series01": "起跑線上的雜念",
    "focus_sprint_workplace__zh_TW__sports_competition__series02": "頂替名單的第六人",
    "focus_sprint_workplace__zh_TW__sports_competition__series03": "更衣室沒人跟我說話",
    "focus_sprint_workplace__zh_TW__workplace_drama__series01": "永遠開著的十七個視窗",
    "focus_sprint_workplace__zh_TW__workplace_drama__series02": "佔著位子的冒牌組長",

    # ── gentle_growth_healing (josei · self-worth·imposter·social) ───────────
    "gentle_growth_healing__zh_TW__dark_fantasy__series01": "不被加冕的繼承人",
    "gentle_growth_healing__zh_TW__iyashikei__series01": "巷尾那家二手書店",
    "gentle_growth_healing__zh_TW__iyashikei__series02": "怕生的花藝師",
    "gentle_growth_healing__zh_TW__romance_josei_drama__series01": "配不上這束光的我",
    "gentle_growth_healing__zh_TW__romance_josei_drama__series02": "你誤會了那個我",
    "gentle_growth_healing__zh_TW__romance_josei_drama__series03": "不敢回你訊息的午後",
    "gentle_growth_healing__zh_TW__supernatural_mystery__series01": "鏡中映出的真名",
    "gentle_growth_healing__zh_TW__supernatural_mystery__series02": "假扮神諭的少女",

    # ── healing_ground_healing (josei · grief·boundaries·overthinking) ───────
    "healing_ground_healing__zh_TW__dark_fantasy__series01": "替亡魂引路的擺渡人",
    "healing_ground_healing__zh_TW__dark_fantasy__series02": "拒絕跨越的結界守",
    "healing_ground_healing__zh_TW__dark_fantasy__series03": "千思萬緒的織夢者",
    "healing_ground_healing__zh_TW__iyashikei__series01": "海邊那間遺忘咖啡館",
    "healing_ground_healing__zh_TW__iyashikei__series02": "學會說不的花店老闆",
    "healing_ground_healing__zh_TW__psychological_thriller__series01": "停不下來的午夜推理",
    "healing_ground_healing__zh_TW__supernatural_mystery__series01": "未寄出的告別信",
    "healing_ground_healing__zh_TW__supernatural_mystery__series02": "劃出結界的靈媒",

    # ── heart_balance_shojo (josei · social·boundaries·self-worth) ───────────
    "heart_balance_shojo__zh_TW__iyashikei__series01": "怕生女孩的甜點日記",
    "heart_balance_shojo__zh_TW__iyashikei__series02": "學會拒絕的下午茶",
    "heart_balance_shojo__zh_TW__romance_josei_drama__series01": "我也值得這份溫柔",
    "heart_balance_shojo__zh_TW__romance_josei_drama__series02": "人群中找不到你",
    "heart_balance_shojo__zh_TW__romance_josei_drama__series03": "別再為他讓步",
    "heart_balance_shojo__zh_TW__supernatural_mystery__series01": "倒影裡的我才真實",
    "heart_balance_shojo__zh_TW__workplace_drama__series01": "茶水間沒人記得我",
    "heart_balance_shojo__zh_TW__workplace_drama__series02": "這次我不再退讓",

    # ── high_performer_workplace (seinen · burnout·financial·imposter·overth) ─
    "high_performer_workplace__zh_TW__dark_fantasy__series01": "燃盡王冠的騎士",
    "high_performer_workplace__zh_TW__dark_fantasy__series02": "黃金鎖鏈的負債者",
    "high_performer_workplace__zh_TW__historical_period__series01": "頂替狀元的書生",
    "high_performer_workplace__zh_TW__historical_period__series02": "想破腦袋的軍師",
    "high_performer_workplace__zh_TW__psychological_thriller__series01": "燒到只剩灰的明星員工",
    "high_performer_workplace__zh_TW__psychological_thriller__series02": "保險箱裡的赤字",
    "high_performer_workplace__zh_TW__workplace_drama__series01": "假裝懂的那場簡報",
    "high_performer_workplace__zh_TW__workplace_drama__series02": "凌晨還在改的企劃",

    # ── hormone_reset_healing (josei · somatic·self-worth·anxiety) ───────────
    "hormone_reset_healing__zh_TW__iyashikei__series01": "身體比我更誠實",
    "hormone_reset_healing__zh_TW__iyashikei__series02": "鏡前重新認識自己",
    "hormone_reset_healing__zh_TW__psychological_horror__series01": "深夜不肯停的心跳",
    "hormone_reset_healing__zh_TW__romance_josei_drama__series01": "聽見身體的耳語",
    "hormone_reset_healing__zh_TW__supernatural_mystery__series01": "倒影教我愛自己",
    "hormone_reset_healing__zh_TW__supernatural_mystery__series02": "凌晨醒來的房客",

    # ── legacy_builder_memoir (seinen · self-worth·grief·financial·shame) ────
    "legacy_builder_memoir__zh_TW__dark_fantasy__series01": "無名工匠的最後傑作",
    "legacy_builder_memoir__zh_TW__historical_period__series01": "替父立碑的長子",
    "legacy_builder_memoir__zh_TW__iyashikei__series01": "頂讓中的老木工坊",
    "legacy_builder_memoir__zh_TW__psychological_thriller__series01": "不敢說出的那樁事",

    # ── longevity_lab_healing (seinen · somatic·self-worth·grief) ────────────
    "longevity_lab_healing__zh_TW__historical_period__series01": "百歲藥師的手札",
    "longevity_lab_healing__zh_TW__historical_period__series02": "無名郎中的價值",
    "longevity_lab_healing__zh_TW__iyashikei__series01": "替老人讀信的青年",
    "longevity_lab_healing__zh_TW__iyashikei__series02": "山腳下的養生堂",
    "longevity_lab_healing__zh_TW__sci_fi_cyberpunk__series01": "活到三百歲的我是誰",
    "longevity_lab_healing__zh_TW__supernatural_mystery__series01": "送行者的最後一程",

    # ── minimal_mind_healing (seinen · overthinking·anxiety·burnout) ─────────
    "minimal_mind_healing__zh_TW__iyashikei__series01": "清空房間的那一天",
    "minimal_mind_healing__zh_TW__iyashikei__series02": "只留一張椅子的家",
    "minimal_mind_healing__zh_TW__iyashikei__series03": "熄燈後的小書房",
    "minimal_mind_healing__zh_TW__psychological_thriller__series01": "停不下來的推理迴圈",
    "minimal_mind_healing__zh_TW__psychological_thriller__series02": "凌晨四點的不速之客",
    "minimal_mind_healing__zh_TW__sci_fi_cyberpunk__series01": "記憶體即將燒盡",
    "minimal_mind_healing__zh_TW__sci_fi_cyberpunk__series02": "思緒清除程式",
    "minimal_mind_healing__zh_TW__supernatural_mystery__series01": "半夜敲門的雜念",

    # ── morning_momentum_workplace (shonen · burnout·courage·self-worth) ─────
    "morning_momentum_workplace__zh_TW__action_battle__series01": "燃到最後一擊的拳手",
    "morning_momentum_workplace__zh_TW__action_battle__series02": "黎明前出鞘的少年",
    "morning_momentum_workplace__zh_TW__isekai__series01": "轉生第一天就被低估",
    "morning_momentum_workplace__zh_TW__sports_competition__series01": "燒光體力的最後一棒",
    "morning_momentum_workplace__zh_TW__sports_competition__series02": "敢起跑的人",
    "morning_momentum_workplace__zh_TW__sports_competition__series03": "板凳上的王牌",
    "morning_momentum_workplace__zh_TW__workplace_drama__series01": "燒乾鬥志的星期一",
    "morning_momentum_workplace__zh_TW__workplace_drama__series02": "敢舉手的新人",

    # ── night_reset_healing (josei · sleep·anxiety·grief) ────────────────────
    "night_reset_healing__zh_TW__dark_fantasy__series01": "守夢人的長夜",
    "night_reset_healing__zh_TW__iyashikei__series01": "凌晨還亮著的便利店",
    "night_reset_healing__zh_TW__iyashikei__series02": "替逝者收信的夜班員",
    "night_reset_healing__zh_TW__iyashikei__series03": "深夜熄燈的甜點鋪",
    "night_reset_healing__zh_TW__psychological_horror__series01": "枕邊不肯走的客",
    "night_reset_healing__zh_TW__psychological_horror__series02": "閣樓那只空搖椅",
    "night_reset_healing__zh_TW__supernatural_mystery__series01": "夜半三更的安眠堂",
    "night_reset_healing__zh_TW__supernatural_mystery__series02": "天亮前的訪客",

    # ── optimizer_workplace (seinen · overthinking·burnout·imposter) ─────────
    "optimizer_workplace__zh_TW__psychological_thriller__series01": "演算到天亮的偵探",
    "optimizer_workplace__zh_TW__psychological_thriller__series02": "燒盡引擎的工程師",
    "optimizer_workplace__zh_TW__psychological_thriller__series03": "頂著天才之名的人",
    "optimizer_workplace__zh_TW__sci_fi_cyberpunk__series01": "最佳化過頭的城市",
    "optimizer_workplace__zh_TW__sci_fi_cyberpunk__series02": "效能燃燒殆盡",
    "optimizer_workplace__zh_TW__sports_competition__series01": "頂著他人之名的選手",
    "optimizer_workplace__zh_TW__workplace_drama__series01": "想到第十步的會議",
    "optimizer_workplace__zh_TW__workplace_drama__series02": "燒完最後一格電的我",

    # ── qi_foundation_cultivation (seinen · somatic·courage·burnout) ─────────
    "qi_foundation_cultivation__zh_TW__action_battle__series01": "氣脈初開的少年",
    "qi_foundation_cultivation__zh_TW__dark_fantasy__series01": "敢踏進禁地的修士",
    "qi_foundation_cultivation__zh_TW__historical_period__series01": "燃盡丹田的武者",
    "qi_foundation_cultivation__zh_TW__iyashikei__series01": "後山那座吐納堂",

    # ── relational_calm_iyashikei (josei · social·boundaries·somatic) ────────
    "relational_calm_iyashikei__zh_TW__iyashikei__series01": "怕生店主的小食堂",
    "relational_calm_iyashikei__zh_TW__iyashikei__series02": "學會說不的茶屋",
    "relational_calm_iyashikei__zh_TW__psychological_thriller__series01": "身體先一步察覺",
    "relational_calm_iyashikei__zh_TW__romance_josei_drama__series01": "人潮裡的怯步",
    "relational_calm_iyashikei__zh_TW__romance_josei_drama__series02": "畫出距離的那條線",
    "relational_calm_iyashikei__zh_TW__romance_josei_drama__series03": "指尖傳來的悸動",
    "relational_calm_iyashikei__zh_TW__supernatural_mystery__series01": "說不出話的占卜亭",
    "relational_calm_iyashikei__zh_TW__supernatural_mystery__series02": "結界外的訪客",

    # ── relationship_clarity_romance (josei · social·boundaries·self-worth) ──
    "relationship_clarity_romance__zh_TW__iyashikei__series01": "怕生女孩的花店",
    "relationship_clarity_romance__zh_TW__iyashikei__series02": "懂得拒絕的咖啡師",
    "relationship_clarity_romance__zh_TW__psychological_thriller__series01": "我也配得上幸福",
    "relationship_clarity_romance__zh_TW__romance_josei_drama__series01": "聚會角落的那個她",
    "relationship_clarity_romance__zh_TW__romance_josei_drama__series02": "這一次我說了不",
    "relationship_clarity_romance__zh_TW__supernatural_mystery__series01": "鏡中那個更好的我",

    # ── resilient_parent_social (josei · burnout·self-worth·boundaries) ──────
    "resilient_parent_social__zh_TW__dark_fantasy__series01": "燃盡魔力的守護者",
    "resilient_parent_social__zh_TW__iyashikei__series01": "深夜廚房的一盞燈",
    "resilient_parent_social__zh_TW__iyashikei__series02": "學會說不的媽媽",
    "resilient_parent_social__zh_TW__romance_josei_drama__series01": "蠟燭燒到兩頭的她",
    "resilient_parent_social__zh_TW__romance_josei_drama__series02": "我也曾經是我自己",
    "resilient_parent_social__zh_TW__supernatural_mystery__series01": "替家人擋下的那道門",

    # ── sleep_restoration_iyashikei (josei · sleep·anxiety·grief·social) ─────
    "sleep_restoration_iyashikei__zh_TW__iyashikei__series01": "凌晨亮燈的安眠堂",
    "sleep_restoration_iyashikei__zh_TW__iyashikei__series02": "睡不著的深夜食堂",
    "sleep_restoration_iyashikei__zh_TW__iyashikei__series03": "替逝者守夜的人",
    "sleep_restoration_iyashikei__zh_TW__iyashikei__series04": "怕生房客的旅店",
    "sleep_restoration_iyashikei__zh_TW__psychological_horror__series01": "枕頭底下的低語",
    "sleep_restoration_iyashikei__zh_TW__psychological_horror__series02": "天花板上的腳步聲",
    "sleep_restoration_iyashikei__zh_TW__psychological_horror__series03": "舊房間的空床位",
    "sleep_restoration_iyashikei__zh_TW__romance_josei_drama__series01": "派對外的那盞燈",
    "sleep_restoration_iyashikei__zh_TW__supernatural_mystery__series01": "夜半開張的眠夢屋",
    "sleep_restoration_iyashikei__zh_TW__supernatural_mystery__series02": "深夜來訪的客人",

    # ── solar_return_isekai (shonen · self-worth·imposter·courage) ───────────
    "solar_return_isekai__zh_TW__action_battle__series01": "被低估的最後王牌",
    "solar_return_isekai__zh_TW__dark_fantasy__series01": "假冒勇者的旅程",
    "solar_return_isekai__zh_TW__isekai__series01": "敢踏進魔王城的人",
    "solar_return_isekai__zh_TW__isekai__series02": "轉生成不被看好的廢柴",
    # ── MECHA satellite (isekai-mecha; pilot as self-worth crucible) ─────────
    "solar_return_isekai__zh_TW__mecha__series01": "啟動吧，無人看好的機體",

    # ── somatic_wisdom_shojo (josei · somatic·self-worth·social·grief) ───────
    "somatic_wisdom_shojo__zh_TW__dark_fantasy__series01": "聽見血脈低語的少女",
    "somatic_wisdom_shojo__zh_TW__dark_fantasy__series02": "不被加冕的女祭司",
    "somatic_wisdom_shojo__zh_TW__iyashikei__series01": "怕生少女的茶點鋪",
    "somatic_wisdom_shojo__zh_TW__iyashikei__series02": "替遺物寫信的店",
    "somatic_wisdom_shojo__zh_TW__iyashikei__series03": "身體比心更早知道",
    "somatic_wisdom_shojo__zh_TW__romance_josei_drama__series01": "我也值得被珍惜",
    "somatic_wisdom_shojo__zh_TW__romance_josei_drama__series02": "人群裡縮起的肩",
    "somatic_wisdom_shojo__zh_TW__romance_josei_drama__series03": "未說再見的那封信",
    "somatic_wisdom_shojo__zh_TW__supernatural_mystery__series01": "皮膚記得的咒語",
    "somatic_wisdom_shojo__zh_TW__supernatural_mystery__series02": "倒影裡的本來面目",

    # ── spiritual_ground_supernatural (josei · grief·self-worth·courage) ─────
    "spiritual_ground_supernatural__zh_TW__dark_fantasy__series01": "替亡魂寫經的少女",
    "spiritual_ground_supernatural__zh_TW__dark_fantasy__series02": "不被神明選中的巫",
    "spiritual_ground_supernatural__zh_TW__historical_period__series01": "敢入幽冥的引路人",
    "spiritual_ground_supernatural__zh_TW__iyashikei__series01": "山寺旁的招魂鋪",
    "spiritual_ground_supernatural__zh_TW__supernatural_mystery__series01": "鏡中那個真正的我",
    "spiritual_ground_supernatural__zh_TW__supernatural_mystery__series02": "敢推開那扇門的人",

    # ── stabilizer_healing (seinen · burnout·overthinking·financial) ─────────
    "stabilizer_healing__zh_TW__dark_fantasy__series01": "燃盡守護之火的人",
    "stabilizer_healing__zh_TW__iyashikei__series01": "想太多的修錶師",
    "stabilizer_healing__zh_TW__iyashikei__series02": "存摺見底的小食堂",
    "stabilizer_healing__zh_TW__iyashikei__series03": "燒乾力氣的午後",
    "stabilizer_healing__zh_TW__sci_fi_cyberpunk__series01": "運算不停的城市",
    "stabilizer_healing__zh_TW__sci_fi_cyberpunk__series02": "餘額歸零的街區",
    "stabilizer_healing__zh_TW__workplace_drama__series01": "燒到極限的值班夜",
    "stabilizer_healing__zh_TW__workplace_drama__series02": "想得太多的接班人",

    # ── stillness_press (josei flagship · anxiety·somatic·sleep·grief·trauma) ─
    "stillness_press__zh_TW__dark_fantasy__series01": "心湖不肯平靜的國度",
    "stillness_press__zh_TW__dark_fantasy__series02": "聽見身體哭聲的女巫",
    "stillness_press__zh_TW__dark_fantasy__series03": "永夜不眠的王國",
    "stillness_press__zh_TW__dark_fantasy__series04": "替亡者守靈的少女",
    "stillness_press__zh_TW__isekai__series01": "轉生後傷痕仍在",
    "stillness_press__zh_TW__isekai__series02": "心慌轉生記",
    "stillness_press__zh_TW__iyashikei__series01": "身體先說了實話",
    "stillness_press__zh_TW__iyashikei__series02": "睡不著的茶寮",
    "stillness_press__zh_TW__iyashikei__series03": "替逝者煮一碗粥",
    "stillness_press__zh_TW__iyashikei__series04": "縫補裂痕的繡坊",
    "stillness_press__zh_TW__iyashikei__series05": "心跳太快的小書店",
    "stillness_press__zh_TW__psychological_horror__series01": "皮膚下的雜音",
    "stillness_press__zh_TW__psychological_horror__series02": "枕邊不肯離去的影",
    "stillness_press__zh_TW__psychological_horror__series03": "葬禮後的空房間",
    "stillness_press__zh_TW__supernatural_mystery__series01": "舊傷未癒的招魂屋",
    "stillness_press__zh_TW__supernatural_mystery__series02": "心慌夜半的占卜店",

    # ── stoic_edge_battle (seinen · courage·grief·self-worth·shame) ──────────
    "stoic_edge_battle__zh_TW__action_battle__series01": "敢獨自上場的劍客",
    "stoic_edge_battle__zh_TW__action_battle__series02": "替戰友續命的最後一刀",
    "stoic_edge_battle__zh_TW__dark_fantasy__series01": "不被認可的鐵衛",
    "stoic_edge_battle__zh_TW__historical_period__series01": "背負罪名的浪人",
    "stoic_edge_battle__zh_TW__historical_period__series02": "敢拔刀的最後武士",
    "stoic_edge_battle__zh_TW__sports_competition__series01": "替逝去隊長而戰",

    # ── trauma_path_healing (josei · grief·trauma·somatic·shame) ─────────────
    "trauma_path_healing__zh_TW__dark_fantasy__series01": "替亡魂縫合傷口的人",
    "trauma_path_healing__zh_TW__dark_fantasy__series02": "舊傷化成的詛咒",
    "trauma_path_healing__zh_TW__historical_period__series01": "身體記得的舊事",
    "trauma_path_healing__zh_TW__iyashikei__series01": "不敢說出口的小店",
    "trauma_path_healing__zh_TW__psychological_horror__series01": "葬禮上多出的座位",
    "trauma_path_healing__zh_TW__psychological_horror__series02": "舊傷甦醒的閣樓",

    # ── warrior_calm_cultivation (shonen · burnout·courage·somatic) ──────────
    "warrior_calm_cultivation__zh_TW__action_battle__series01": "燃盡內力的少年",
    "warrior_calm_cultivation__zh_TW__action_battle__series02": "敢闖龍門的拳手",
    "warrior_calm_cultivation__zh_TW__dark_fantasy__series01": "聽見筋骨低語的武者",
    "warrior_calm_cultivation__zh_TW__dark_fantasy__series02": "燒乾真氣的守山人",
    "warrior_calm_cultivation__zh_TW__historical_period__series01": "敢提刀的山中少年",
    "warrior_calm_cultivation__zh_TW__iyashikei__series01": "後山的吐納小院",
    # ── MECHA satellite (cultivation-mecha; the calm warrior's iron vessel) ──
    "warrior_calm_cultivation__zh_TW__mecha__series01": "鋼鐵肉身，靜如止水",
}


def _load_yaml(p: Path) -> Any:
    with open(p, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _leaks_topic(title: str, topic: str) -> bool:
    if any(s in title for s in CLINICAL_STEMS):
        return True
    t_zh = TOPIC_ZH.get(topic, "")
    return bool(t_zh) and t_zh in title


def assign_topics(brand_info: dict, series_list: list[dict]) -> None:
    """Round-robin the brand's [primary]+secondary topics across its series.

    Mecha series that already carry a topic keep it (do not re-rotate).
    """
    topics = [brand_info.get("primary_topic", "")] + list(brand_info.get("secondary_topics", []) or [])
    topics = [t for t in topics if t] or ["self_worth"]
    for i, sp in enumerate(sorted(series_list, key=lambda r: (r["genre"], r["series_index"]))):
        if sp["topic_is_tbd"]:
            sp["_topic"] = topics[i % len(topics)]
        else:
            sp["_topic"] = sp["topic_existing"]


def _yaml_quote(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def apply_edits(path: Path, *, title: str, topic: str, author: str,
                write_topic: bool, write_author: bool) -> bool:
    """Replace `: TBD` lines in place. Idempotent. Returns True if changed.

    Only TBD lines are touched. `write_topic`/`write_author` are False for the
    mecha series (already filled) so their existing values are never rewritten.
    """
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    changed = False
    in_localized = False
    for i, line in enumerate(lines):
        stripped = line.rstrip("\n")
        if re.match(r"^title:\s*TBD\s*$", stripped):
            lines[i] = f"title: {_yaml_quote(title)}\n"; changed = True
        elif re.match(r"^localized_titles:\s*$", stripped):
            in_localized = True
        elif in_localized and re.match(r"^\s+zh_TW:\s*TBD\s*$", stripped):
            indent = line[:len(line) - len(line.lstrip())]
            lines[i] = f"{indent}zh_TW: {_yaml_quote(title)}\n"; changed = True; in_localized = False
        elif write_topic and re.match(r"^topic:\s*TBD\s*$", stripped):
            lines[i] = f"topic: {topic}\n"; changed = True
        elif write_author and re.match(r"^manga_author:\s*TBD\s*$", stripped):
            lines[i] = f"manga_author: {_yaml_quote(author)}\n"; changed = True
        elif stripped and not line.startswith((" ", "\t")) and in_localized:
            in_localized = False
    if changed:
        path.write_text("".join(lines), encoding="utf-8")
    return changed


def build_plans() -> tuple[list[dict], dict[str, Any]]:
    brands = (_load_yaml(CANONICAL_BRANDS) or {}).get("brands", {})
    plans: list[dict] = []
    for p in sorted(SERIES_DIR.glob("*.yaml")):
        sp = _load_yaml(p) or {}
        sid = sp.get("series_id", p.stem)
        topic_existing = str(sp.get("topic", "")).strip()
        author_existing = str(sp.get("manga_author", "")).strip()
        plans.append({
            "path": p, "brand_id": sp.get("brand_id", ""), "genre": sp.get("genre", ""),
            "demographic": sp.get("demographic", "general"), "series_id": sid,
            "series_index": sid.split("__")[-1],
            "title_is_tbd": str(sp.get("title", "")).strip().upper() == "TBD",
            "topic_is_tbd": topic_existing.upper() == "TBD",
            "author_is_tbd": author_existing.upper() == "TBD",
            "topic_existing": topic_existing,
            "author_existing": author_existing,
        })
    by_brand: dict[str, list[dict]] = defaultdict(list)
    for r in plans:
        by_brand[r["brand_id"]].append(r)
    for b, lst in by_brand.items():
        assign_topics(brands.get(b, {}), lst)
    return plans, brands


def run_checks(plans: list[dict]) -> int:
    """QA: coverage, leak, within-brand + global title uniqueness. Returns err count."""
    errs = 0
    # 1. Every series has a title in the table.
    missing = [r["series_id"] for r in plans if r["series_id"] not in TITLES]
    if missing:
        errs += len(missing)
        print(f"  ERR: {len(missing)} series missing from TITLES table:")
        for m in missing[:20]:
            print(f"       {m}")
    # 2. Clinical / topic leak.
    for r in plans:
        t = TITLES.get(r["series_id"])
        if t and _leaks_topic(t, r["_topic"]):
            errs += 1
            print(f"  ERR: leak in {r['series_id']}: {t!r} (topic={r['_topic']})")
    # 3. Within-brand uniqueness.
    by_brand: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for r in plans:
        t = TITLES.get(r["series_id"])
        if t:
            by_brand[r["brand_id"]].append((r["series_id"], t))
    for b, lst in by_brand.items():
        seen: dict[str, list[str]] = defaultdict(list)
        for sid, t in lst:
            seen[t].append(sid)
        for t, sids in seen.items():
            if len(sids) > 1:
                errs += 1
                print(f"  ERR: within-brand dup in {b}: {t!r} -> {sids}")
    # 4. Global uniqueness.
    allt: dict[str, list[str]] = defaultdict(list)
    for r in plans:
        t = TITLES.get(r["series_id"])
        if t:
            allt[t].append(r["series_id"])
    for t, sids in allt.items():
        if len(sids) > 1:
            errs += 1
            print(f"  ERR: GLOBAL dup: {t!r} -> {sids}")
    # 5. Non-empty, contains CJK.
    for r in plans:
        t = TITLES.get(r["series_id"], "")
        if t and not any("一" <= c <= "鿿" for c in t):
            errs += 1
            print(f"  ERR: no CJK in {r['series_id']}: {t!r}")
    return errs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--brand", help="Restrict to one brand_id")
    ap.add_argument("--dry-run", action="store_true", help="No writes")
    ap.add_argument("--check", action="store_true", help="QA only, no writes")
    args = ap.parse_args()

    plans, _brands = build_plans()

    print(f"== zh_TW series: {len(plans)}  (TITLES table: {len(TITLES)}) ==")
    errs = run_checks(plans)
    if args.check:
        print(f"== CHECK: {errs} error(s) ==")
        return 0 if errs == 0 else 1
    if errs:
        print(f"== ABORT: {errs} QA error(s) before write ==")
        return 1

    todo = [r for r in plans if (not args.brand or r["brand_id"] == args.brand)]
    todo.sort(key=lambda r: (r["brand_id"], r["genre"], r["series_index"]))

    review_rows: list[dict] = []
    filled = skipped = 0
    for r in todo:
        if not r["title_is_tbd"]:
            skipped += 1
            continue
        title = TITLES[r["series_id"]]
        # Author: regenerate only if TBD (mecha already authored → keep).
        if r["author_is_tbd"]:
            author = generate_display_name(
                genre=r["genre"], locale="zh_TW", brand_id=r["brand_id"],
                topic=r["_topic"], demographic=r["demographic"])
        else:
            author = r["author_existing"]
        wrote = False
        if not args.dry_run:
            wrote = apply_edits(
                r["path"], title=title, topic=r["_topic"], author=author,
                write_topic=r["topic_is_tbd"], write_author=r["author_is_tbd"])
        filled += 1
        review_rows.append({
            "brand_id": r["brand_id"], "genre": r["genre"],
            "series_id": r["series_id"], "topic": r["_topic"],
            "title_zh_TW": title, "manga_author": author,
            "topic_prefilled": not r["topic_is_tbd"],
            "author_prefilled": not r["author_is_tbd"], "written": wrote})

    if review_rows and not args.dry_run:
        REVIEW_OUT.parent.mkdir(parents=True, exist_ok=True)
        with open(REVIEW_OUT, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(review_rows[0].keys()))
            w.writeheader(); w.writerows(review_rows)
        print(f"review sidecar → {REVIEW_OUT.relative_to(ROOT)}")
    print(f"DONE filled={filled} skipped={skipped}  (dry_run={args.dry_run})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
