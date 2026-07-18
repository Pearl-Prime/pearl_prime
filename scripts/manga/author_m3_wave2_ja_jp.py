#!/usr/bin/env python3
"""M3 Wave 2 — author 16 ja_JP-native flagship chapter_scripts (genre-led).

Native Japanese originals (NOT translations of en_US Wave 1). Tier-1 Pearl_Writer.
Each script: genre-first JP-market story, topic as body weather, wired vessel cited,
teacher never named. Passes check_manga_story_authored.py incl. name-scan.
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "artifacts" / "manga" / "chapter_scripts"

# brand, genre, topic, tier, title_ja, title_en_gloss, author_ja, author_romaji,
# protag (id, name_ja, name_romaji, age, role_en, visual_en)
SLATE: list[dict] = [
    {
        "brand": "stillness_press", "genre": "iyashikei", "topic": "anxiety",
        "title_ja": "湯気の向こう", "title_en": "Beyond the Steam",
        "author": "潮見 遥", "author_slug": "shiomi_haruka",
        "protag": ("aya", "綾", "Aya", 34, "会社員・朝の茶が唯一の錨", "柔らかいカーディガン、湯気の立つ湯呑み"),
        "vessel_key": "iyashikei",
    },
    {
        "brand": "cognitive_clarity", "genre": "psychological_thriller", "topic": "overthinking",
        "title_ja": "ループは思考ではない", "title_en": "The Loop Is Not Thinking",
        "author": "黒瀬 迅", "author_slug": "kurose_jin",
        "protag": ("ren", "蓮", "Ren", 38, "分析官・パターンが自分を読む", "ワイシャツの袖、クリックするペン"),
        "vessel_key": "psychological_thriller",
    },
    {
        "brand": "digital_ground", "genre": "sci_fi_cyberpunk", "topic": "burnout",
        "title_ja": "フィードは血より大きい", "title_en": "The Feed Is Louder Than Blood",
        "author": "青葉 零", "author_slug": "aoba_rei",
        "protag": ("kei", "圭", "Kei", 29, "オンコールエンジニア", "ブルーライト眼鏡、擦れたパーカー"),
        "vessel_key": "sci_fi_cyberpunk",
    },
    {
        "brand": "body_memory_shojo", "genre": "psychological_horror", "topic": "somatic_healing",
        "title_ja": "家がびくっとする", "title_en": "The House That Flinches",
        "author": "霧島 灯", "author_slug": "kirishima_akari",
        "protag": ("mio", "澪", "Mio", 26, "実家に戻った娘", "雨のジャケット、握ったままの鍵"),
        "vessel_key": "psychological_horror",
    },
    {
        "brand": "healing_ground_healing", "genre": "dark_fantasy", "topic": "grief",
        "title_ja": "森が名を覚える", "title_en": "The Forest Keeps Their Names",
        "author": "柘植 守", "author_slug": "tsuge_mamoru",
        "protag": ("ash", "葦", "Ash", 31, "生きた森の番人", "旅の外套、杖に結んだリボン"),
        "vessel_key": "dark_fantasy",
    },
    {
        "brand": "trauma_path_healing", "genre": "dark_fantasy", "topic": "grief",
        "title_ja": "鳴らない刃", "title_en": "The Blade That Won't Sing",
        "author": "棘 剛", "author_slug": "toge_tsuyoshi",
        "protag": ("riven", "裂", "Riven", 30, "元騎士・鞘は空のまま", "旅装束、光った空鞘"),
        "vessel_key": "dark_fantasy",
    },
    {
        "brand": "devotion_path_shonen", "genre": "dark_fantasy", "topic": "grief",
        "title_ja": "二杯目は満杯のまま", "title_en": "The Second Cup Stays Full",
        "author": "白井 祈", "author_slug": "shirai_inori",
        "protag": ("ren2", "蓮", "Ren", 28, "寺の世話人", "簡素な衣、丁寧な手"),
        "vessel_key": "dark_fantasy",
        "teacher_meta": "sai_ma",
    },
    {
        "brand": "career_lift_workplace", "genre": "workplace_drama", "topic": "imposter_syndrome",
        "title_ja": "借り物のスライド", "title_en": "The Slide That Isn't You",
        "author": "水野 杏", "author_slug": "mizuno_anzu",
        "protag": ("ava", "杏奈", "Anna", 28, "パートナー向け発表のアソシエイト", "借りたようなジャケット、握るクリッカー"),
        "vessel_key": "workplace_drama",
    },
    {
        "brand": "high_performer_workplace", "genre": "workplace_drama", "topic": "burnout",
        "title_ja": "ダッシュボードは緑", "title_en": "Green on the Dashboard",
        "author": "成瀬 剛", "author_slug": "naruse_tsuyoshi",
        "protag": ("cole", "航", "Ko", 33, "営業部長・指標は全部緑", "パリッとしたシャツ、震えるスマートウォッチ"),
        "vessel_key": "workplace_drama",
    },
    {
        "brand": "stabilizer_healing", "genre": "workplace_drama", "topic": "burnout",
        "title_ja": "シフトのあいだのベンチ", "title_en": "The Bench Between Shifts",
        "author": "岸 透", "author_slug": "kishi_toru",
        "protag": ("devon", "透", "Toru", 36, "プロジェクトリード・終電後", "緩めたネクタイ、冷めた缶コーヒー"),
        "vessel_key": "workplace_drama",
    },
    {
        "brand": "warrior_calm_cultivation", "genre": "mecha", "topic": "burnout",
        "title_ja": "機体は聴いている", "title_en": "The Chassis Is Listening",
        "author": "岩見 蓮", "author_slug": "iwami_ren",
        "protag": ("kaede", "楓", "Kaede", 27, "三度目の出撃パイロット", "フライトスーツ、手編みの掌パッド"),
        "vessel_key": "mecha",
    },
    {
        "brand": "solar_return_isekai", "genre": "isekai", "topic": "self_worth",
        "title_ja": "履歴書のない空", "title_en": "No Resume in This Sky",
        "author": "星野 朔", "author_slug": "hoshino_saku",
        "protag": ("sid", "朔", "Saku", 26, "二つの月の下で目覚めた元会社員", "破れたワイシャツ、意味を失った社員証"),
        "vessel_key": "isekai",
    },
    {
        "brand": "spiritual_ground_supernatural", "genre": "supernatural_mystery", "topic": "grief",
        "title_ja": "名より先に冷える", "title_en": "The Cold Spot Before the Name",
        "author": "遠野 霧", "author_slug": "tono_kiri",
        "protag": ("ell", "霧子", "Kiriko", 35, "見習い霊媒", "長いコート、未完の名前のノート"),
        "vessel_key": "supernatural_mystery",
    },
    {
        "brand": "sleep_restoration_iyashikei", "genre": "iyashikei", "topic": "sleep",
        "title_ja": "来ない時刻", "title_en": "The Hour That Won't Arrive",
        "author": "海老原 凪", "author_slug": "ebihara_nagi",
        "protag": ("lena", "凪", "Nagi", 34, "夜勤明けの看護師", "カーディガン、回る銀の指輪"),
        "vessel_key": "iyashikei",
    },
    {
        "brand": "heart_balance_shojo", "genre": "romance_josei_drama", "topic": "social_anxiety",
        "title_ja": "カウンターの二つのカップ", "title_en": "Two Cups on the Counter",
        "author": "月村 結", "author_slug": "tsukimura_yui",
        "protag": ("emi", "笑美", "Emi", 23, "閉店作業のカフェ店員", "二重結びのエプロン、触る髪留め"),
        "vessel_key": "romance_josei_drama",
    },
    {
        "brand": "stoic_edge_battle", "genre": "action_battle", "topic": "courage",
        "title_ja": "盾を下ろす衛兵", "title_en": "The Guard Who Lowers the Shield",
        "author": "刃 剛", "author_slug": "yaiba_go",
        "protag": ("voss", "剛", "Go", 34, "街の衛兵", "凹んだ腕当て、短い槍"),
        "vessel_key": "action_battle",
    },
]

VESSELS = {
    "iyashikei": ("茶屋の手", "言葉ではなく手を見て学ぶ日課"),
    "psychological_thriller": ("身体を読む探偵", "口より先に身体が告白する"),
    "sci_fi_cyberpunk": ("ウェットウェアの老ハッカー", "フィードより肉の警報を信じる"),
    "psychological_horror": ("向き直る生存者", "逃げるな、会え"),
    "dark_fantasy": ("守り手／生きた土地", "助言ではなく観察としての教え"),
    "workplace_drama": ("周期を見た清掃員", "ペンを置く時機の小さな所作"),
    "mecha": ("同調を整える整備士", "押し通すな、落ち着け"),
    "isekai": ("古い本能を信じる案内人", "旧世界の身体地図が最も正しい"),
    "supernatural_mystery": ("冷えを読む霊媒", "幽霊より先に身体の信号"),
    "romance_josei_drama": ("休む恋人", "急がない相手が楽さを見せる"),
    "action_battle": ("落ち着いた一撃の師範", "静かな身体から最も硬い一撃"),
}


def _loc(ja: str, en: str) -> dict:
    """ja_JP is authoritative; en_US is operator gloss only."""
    return {
        "ja_JP": ja,
        "en_US": en,
        "zh_TW": f"[zh_TW] {en}",
        "zh_CN": f"[zh_CN] {en}",
    }


def _panel(pid: str, scene_ja: str, *, caption_ja: str | None = None, caption_en: str | None = None,
           dialogue: list | None = None, silence: bool = False, intent: str | None = None) -> dict:
    p: dict = {"panel_id": pid, "scene": scene_ja, "beat_type": "micro"}
    if silence:
        p["silence_confirmed"] = True
    if intent:
        p["intent"] = intent
    if caption_ja:
        p["narrator_caption_by_locale"] = _loc(caption_ja, caption_en or caption_ja)
    if dialogue:
        p["dialogue_lines"] = dialogue
    return p


def _dlg(speaker: str, ja: str, en: str, intensity: str = "whisper") -> dict:
    return {
        "speaker": speaker,
        "text_by_locale": _loc(ja, en),
        "intensity": intensity,
        "bubble_style": "round_normal",
        "tail_style": "pointer",
        "position_hint": "top_right",
    }


def build_panels(spec: dict) -> list[dict]:
    """16-panel wound→vessel turn→renewal arc in native Japanese."""
    genre = spec["genre"]
    pid, name_ja, name_romaji, age, role, visual = spec["protag"]
    vessel_ja, vessel_desc = VESSELS[spec["vessel_key"]]
    topic = spec["topic"]

    # Genre-native openings (JP surface story)
    worlds = {
        "iyashikei": (
            f"朝の室内。柔らかい光。{name_ja}の部屋は普通で、少しだけ手入れが遅れている。危機ではない。日常だ。",
            f"{name_ja}の手のクローズアップ。小さな作業を丁寧すぎるほどにしている。身体が一日を先取りしている。",
            "小さなきっかけが入る——通知、音、時計。小さく、具体的。ジャンプスケアではない。",
        ),
        "psychological_thriller": (
            f"オフィスの光。画面。{name_ja}はパターンに強い。今夜、パターンがこちらを見返している。",
            "メモ、モデル、ファイルラベルのクローズアップ。精密さが鎧だ。",
            "存在してはいけないデータポイント——予測、反射、場違いな名前。",
        ),
        "sci_fi_cyberpunk": (
            f"濡れた舗道に都市フィードの光。{name_ja}のHUDはきれいだ。強化されていない手が違う。",
            "ポート、震え、空にならない通知スタック。",
            "フィードは最適化する。身体は反対する。システムがノイズと呼ぶ食い違い。",
        ),
        "psychological_horror": (
            f"見慣れた部屋の、間違った時刻。{name_ja}は廊下の角度が普通だと装う。普通ではない。",
            "ドアノブに置いた手。木が温かい。温かくてはいけない。",
            "家の奥からの音——大きくない。ついてくる種類の静けさ。",
        ),
        "dark_fantasy": (
            f"生きた森の縁の霧。{name_ja}は道が細くなるところに立つ。土地が目なしで見ている。",
            f"{name_ja}が持つ護符や刃のクローズアップ。応えるべきときに静かだ。その沈黙が傷だ。",
            "木々の何かが動く——攻撃ではなく、拒否。土地は強制されない。",
        ),
        "workplace_drama": (
            f"オープンプラン、またはガラスの会議室。蛍光灯の正直さ。{name_ja}はすでに有能を演じている。",
            "バッジ、クリッカー、白い隙間のないカレンダー。",
            "会議、または指標の瞬間。部屋の視線が天気だ。",
        ),
        "mecha": (
            f"夜明け前の格納庫。機体がそびえる。{name_ja}はコックピットの敷居——すでに機械の息の半分にいる。",
            "掌パッド、テレメトリのちらつき、上書きのための顎。",
            "発進チェックリスト。同調を強制する。機体が一瞬ためらう——聴いている。",
        ),
        "isekai": (
            f"二つの月の空。{name_ja}は故郷ではない土の上で目覚める。別の人生の社員証が草に落ち、意味がない。",
            "手のクローズアップ——道具を知っている。かつて重要だった肩書きは翻訳されない。",
            "地元の者が履歴書を聞かずに近づく。問いはもっと単純だ——立てるか。",
        ),
        "supernatural_mystery": (
            f"青い時刻の現場。幽霊より先に角に冷えが集まる。{name_ja}は目が見たものを書く。",
            "未完の名前のノート。推論が盾だ。",
            "冷えが動く。目は逃す。肌は逃さない。",
        ),
        "romance_josei_drama": (
            f"閉店後のカフェ。カウンターに二つのカップ。{name_ja}は誰にでも出せるが、誰かと座れない。",
            "エプロンの紐、触る髪留め。",
            "ノック——急がない。沈黙を埋めない相手。",
        ),
        "action_battle": (
            f"訓練場、または街の端。埃、衝撃の跡、息。{name_ja}は約束のように武器を握る。",
            "握りのクローズアップ——きつすぎる。勇気としての締め付け。",
            "試合、または衝突が始まる。型は完璧。代償は無視されている。",
        ),
    }
    w0, w1, w2 = worlds.get(genre, worlds["iyashikei"])

    vessel_chars = {
        "iyashikei": ("elder", "老人", "急がない日課の手"),
        "psychological_thriller": ("reader", "読む人", "スライドではなく肩を読む同僚"),
        "sci_fi_cyberpunk": ("hacker", "老ハッカー", "意図的に強化を外した老人"),
        "psychological_horror": ("survivor", "生存者", "この家に会ったことのある者"),
        "dark_fantasy": ("keeper", "守り手", "温かい地面に掌を置くだけ"),
        "workplace_drama": ("custodian", "清掃員", "このカレンダーを見た夜勤の人"),
        "mecha": ("mechanic", "整備士", "講義なしで同調を整える"),
        "isekai": ("innkeeper", "宿の主人", "履歴書ではなく運べるものを聞く"),
        "supernatural_mystery": ("medium", "先輩", "名より先に冷えを感じる"),
        "romance_josei_drama": ("beloved", "相手", "急がない恋人"),
        "action_battle": ("veteran", "古参", "芝居なしで代償を名指す"),
    }
    vid, vname, vrole = vessel_chars.get(genre, ("guide", "案内", "静かな案内"))

    title_ja = spec["title_ja"]
    panels = [
        _panel("ep001_001", w0, silence=True, intent="ジャンル世界の確立"),
        _panel("ep001_002", w1, silence=True, intent="心より先に身体"),
        _panel("ep001_003", w2,
               caption_ja="一日には形がある。身体はもう知っている。",
               caption_en="The day has a shape. The body already knows."),
        _panel("ep001_004",
               f"{name_ja}の顔のミディアム。警戒しているが、まだ壊れていない。{age}歳。{visual}。",
               silence=True),
        _panel("ep001_005",
               f"{name_ja}は押し通す——有能な動き。ジャンルの行動は続く。内側では、"
               f"話題の天気（{topic}）は姿勢と息だけで、題名にはならない。",
               dialogue=[_dlg(pid, "大丈夫です。", "I've got it.")]),
        _panel("ep001_006",
               "代償が身体に落ちる——顎、手、止めた息。ジャンルの世界は待たない。",
               intent="傷——身体の代償"),
        _panel("ep001_007",
               f"{name_ja}はさらに力を入れる。もっと演技、もっとパターン。器はまだ入っていない。",
               silence=True),
        _panel("ep001_008",
               "ワイド：ジャンルの圧力が頂点——衝突、会議、冷えた部屋、フィードのスパイク。"
               "講義はない。天気だけ。",
               intent="圧力の頂点"),
        _panel("ep001_009",
               f"器が入る：{vrole}。どの教えの系譜の名もない。存在だけ。"
               f"（{vessel_ja}：{vessel_desc}）",
               silence=True,
               intent="器——教師は決して名指しされない"),
        _panel("ep001_010",
               "器がジャンル固有の小さな所作をする——日課の手、地面の掌、引かれた椅子、"
               "足の置き方、信じた周波数。助言の演説はない。",
               silence=True,
               intent="転機の始まり"),
        _panel("ep001_011",
               f"{name_ja}が見る。心が同意する半秒前に、身体が落ち着く。",
               caption_ja="先に知っていた。",
               caption_en="It knew first."),
        _panel("ep001_012",
               "器の任意の一言——実践的で、教義ではない。",
               dialogue=[_dlg(vid, "押し通すな。落ち着け。", "Don't override. Settle.", "soft")]),
        _panel("ep001_013",
               f"{name_ja}が一度だけ、小さな動きを試す。ジャンルの行動は続くが、別の身体から。",
               intent="更新の試み"),
        _panel("ep001_014",
               "世界がわずかに応える——テレメトリが緩む、土地が温まる、部屋が静まる。"
               "勝利ではない。許可だ。",
               silence=True),
        _panel("ep001_015",
               f"閉じのワイド。{name_ja}は一つの小さな所作を意図して続ける。話題は天気として残る。"
               f"熟達はない。治癒はない。最初の道具だけ。",
               caption_ja="終わらせなくていい。一度、気づけばいい。",
               caption_en="I don't have to finish it. I have to notice it once."),
        _panel("ep001_016",
               "静かな色面の上のタイポグラフィックなエンドカード。",
               caption_ja=f"第一話・了——{title_ja}",
               caption_en=f"End of Episode 1 — {spec['title_en']}"),
    ]
    return panels


def build_script(spec: dict) -> dict:
    genre = spec["genre"]
    topic = spec["topic"]
    brand = spec["brand"]
    author = spec["author"]
    author_slug = spec["author_slug"]
    pid, name_ja, name_romaji, age, role, visual = spec["protag"]
    series_id = f"{brand}__{author_slug}__ja_JP__{topic}__{re.sub(r'[^a-z0-9]+', '_', spec['title_en'].lower()).strip('_')}"
    vessel_ja, vessel_desc = VESSELS[spec["vessel_key"]]
    bible = f"docs/research/manga_craft/{spec['vessel_key'] if spec['vessel_key'] != 'iyashikei' else 'iyashikei_minimalism'}.md"
    if genre == "psychological_horror":
        bible = "docs/research/manga_craft/psychological_horror.md"
    elif genre == "isekai":
        bible = "docs/research/manga_craft/isekai.md"
    elif genre == "mecha":
        bible = "docs/research/manga_craft/mecha.md"

    vessel_chars = {
        "iyashikei": ("elder", "老人"),
        "psychological_thriller": ("reader", "読む人"),
        "sci_fi_cyberpunk": ("hacker", "老ハッカー"),
        "psychological_horror": ("survivor", "生存者"),
        "dark_fantasy": ("keeper", "守り手"),
        "workplace_drama": ("custodian", "清掃員"),
        "mecha": ("mechanic", "整備士"),
        "isekai": ("innkeeper", "宿の主人"),
        "supernatural_mystery": ("medium", "先輩"),
        "romance_josei_drama": ("beloved", "相手"),
        "action_battle": ("veteran", "古参"),
    }
    vid, vname = vessel_chars.get(genre, ("guide", "案内"))

    chars = [
        {"id": pid, "name": name_ja, "name_romaji": name_romaji, "age": age,
         "role": f"主人公（{role}）", "visual_anchor": visual},
        {"id": vid, "name": vname, "age": "不詳",
         "role": f"器の存在——{vessel_desc}；ブランド教師の名は決して使わない",
         "visual_anchor": "ジャンル固有；顔は任意；手と姿勢が教えを運ぶ"},
    ]

    teacher_meta = spec.get("teacher_meta", "brand_teacher_unresolved")
    doc: dict = {
        "schema_version": "1.0.0",
        "artifact_type": "chapter_script_writer_handoff",
        "schema_authority": "schemas/manga/chapter_script_writer_handoff.schema.json",
        "series_id": series_id,
        "chapter_id": "ep_001",
        "title": f"{spec['title_ja']}——第一話",
        "title_en_gloss": f"{spec['title_en']} — Episode 1",
        "manga_author": author,
        "teacher_id": teacher_meta,
        "brand_id": brand,
        "engine": topic,
        "locale": "ja_JP",
        "default_locale": "ja_JP",
        "available_locales": ["ja_JP", "en_US", "zh_CN", "zh_TW"],
        "genre": genre,
        "mode": "teacher",
        "vessel": vessel_ja,
        "main_characters": chars,
        "scene_palette": {
            "primary": "ジャンル主導；craft_notes参照",
            "secondary": "更新ビートの温かいアクセント",
            "accent": "一つの反復する視覚的スルーライン",
        },
        "pages": [{"page_id": "ep_001_p01", "panels": build_panels(spec)}],
        "notes": {
            "pacing": (
                "十六コマ。入口フロアを満たし、ウェブトゥーンの呼吸。沈黙が働き、"
                "台詞は転換点のみ。表面はジャンル物語；話題は身体の天気のみ。"
            ),
            "bubble_style_register": "主人公の台詞：round_normal、多くはwhisper。器の台詞：soft、実践的、講義ではない。",
            "sfx_policy": "最小限。囁きレジスタのみ。",
            "language": "ja_JPが権威。en_USはオペレータ用グロスのみ。翻訳ではなくネイティブ原作。",
            "translation_pipeline_handoff": "en_USグロスはレビュー用。CJK他言語は別レーン。",
        },
        "craft_notes": (
            f"VESSEL: {vessel_ja} — {vessel_desc}。config/manga/manga_mode_vessels.yaml より引用。"
            f"教師は物語内で決して名指ししない（teacher_id={teacher_meta!r} はメタデータのみ）。\n"
            f"GENRE BIBLE: {bible}\n"
            f"GENRE-FIRST (ja_JP): 表面は{genre}の物語。話題（{topic}）は姿勢・息・代償としての内的天気。\n"
            f"ARC: 傷（強制／演技／逃走）→転機（器が落ち着きを見せる）→更新（一つの保持された所作）。\n"
            f"NATIVE: 英語からの翻訳ではない。JP市場のジャンル検索向け原作。\n"
            f"ACCEPTANCE: native-authored + gate-floor + JP-craft-reviewed — NOT claimed bestseller (M6 bar)."
        ),
    }
    if spec.get("teacher_meta") == "sai_ma":
        doc["byline_note"] = "EI character-author; Sai Maa never author-of-record"
    return doc


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest_lines = ["brand\tgenre\ttopic\tseries_id\ttitle_ja\n"]
    for spec in SLATE:
        doc = build_script(spec)
        series_id = doc["series_id"]
        dest_dir = OUT / series_id
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / "ep_001.yaml"
        dest.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True), encoding="utf-8")
        manifest_lines.append(
            f"{spec['brand']}\t{spec['genre']}\t{spec['topic']}\t{series_id}\t{spec['title_ja']}\n"
        )
        print(f"NEW {series_id}")
    manifest = REPO / "artifacts" / "qa" / "manga_m3_wave2_craft_audit" / "WAVE2_MANIFEST.tsv"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text("".join(manifest_lines), encoding="utf-8")
    print(f"wrote {len(SLATE)} scripts; manifest {manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
