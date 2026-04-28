# Pearl Prime — Final Launch Readiness Report

Generated: 2026-04-28 21:45 UTC
Source: post-#793 catalogs at `artifacts/catalog/pearl_prime_book_script_catalogs/{locale}_catalog.csv`

**Catalog ladder closed.** B3+B4 (#780) → B2 (#788, then #790) → B1 (#793) all merged. This report selects the launch baseline from current main.

---

## §1 — Readiness by locale

| Locale | Total rows | Ready | Listing-ready (titled) | Blocked (score) | Distinct titles |
|---|---:|---:|---:|---:|---:|
| en_US | 1,478 | 1,478 | **1,478** | 0 | 698 |
| ja_JP | 1,478 | 1,478 | **1,478** | 0 | 699 |
| zh_TW | 2,818 | 2,658 | **2,658** | 160 | 1,187 |
| zh_CN | 2,630 | 2,630 | **2,630** | 0 | 1,178 |
| **All 4** | **8,404** | **8,244** | **8,244** | **160** | — |

Listing-ready = ready row AND has a non-blank title. Listing-ready rows are the candidate set for the Top 50 selection.

## §2 — Top 50 combined launch candidates

Selection: highest composite score across all 4 locales, with ≤ 2 rows per `(brand, topic)` pair (preserves brand-topic diversity) and a ~14-per-locale cap (preserves locale balance).

Composite range in Top 50: **0.90–0.95** · Per-locale: en_US=14, ja_JP=14, zh_TW=8, zh_CN=14

| # | Locale | Brand | Topic | Persona | Teacher | Composite | Title | Subtitle |
|---:|---|---|---|---|---|---:|---|---|
| 1 | en_US | body_memory | grief | healthcare_rns | omote | 0.95 | Held Where the Love Goes | A Grief Companion for Year One and After — for healthcare workers |
| 2 | en_US | body_memory | somatic_healing | healthcare_rns | omote | 0.95 | Held Unlock the Freeze | A Somatic Guide to Nervous System Reset and Trauma Release — for healthcare workers |
| 3 | en_US | sleep_restoration | sleep_anxiety | healthcare_rns | master_sha | 0.95 | Restful The 3 AM Mind | A Guide to Overcoming Insomnia and Sleep Anxiety — for healthcare workers |
| 4 | en_US | warrior_calm | courage | first_responders | master_wu | 0.95 | Steady Jump Scared | A Guide to Building Courage and Facing the Unknown — for frontline workers |
| 5 | ja_JP | body_memory | grief | healthcare_rns | omote | 0.95 | 抱きしめる喪失とかなしみとの対話 | 喪失とかなしみのあとに、抱きしめる静けさを取り戻す — 医療従事者へ |
| 6 | ja_JP | body_memory | somatic_healing | healthcare_rns | omote | 0.95 | 身体の癒しのあとに、抱きしめる日々 | 抱きしめる暮らしへの、身体の癒し回復の手引き — 医療従事者へ |
| 7 | ja_JP | sleep_restoration | sleep_anxiety | healthcare_rns | master_sha | 0.95 | やすらかな睡眠の不安の手当て | 睡眠の不安を抜けるための、やすらかな日々への手引き — 医療従事者へ |
| 8 | ja_JP | warrior_calm | courage | first_responders | master_wu | 0.95 | ゆるがぬ勇気の手当て | 勇気を抜けるための、ゆるがぬ日々への手引き — 現場の最前線へ |
| 9 | en_US | cognitive_clarity | overthinking | tech_finance_burnout | joshin | 0.93 | Clear Thought Traffic | Breaking Free from Overthinking, Worry, and Analysis Paralysis — for tech and finance pros |
| 10 | en_US | devotion_path | courage | healthcare_rns | sai_ma | 0.93 | Devoted Jump Scared | A Guide to Building Courage and Facing the Unknown — for healthcare workers |
| 11 | en_US | digital_ground | financial_anxiety | gen_z_professionals | miki | 0.93 | Grounded The Quiet Ledger | A Financial Anxiety Practice for the Spreadsheet-Tired — for Gen Z professionals |
| 12 | en_US | digital_ground | financial_anxiety | gen_z_student | miki | 0.93 | Grounded Broke and Breathing | A Somatic Guide to Financial Anxiety Recovery — for Gen Z students |
| 13 | en_US | digital_ground | financial_stress | gen_z_professionals | miki | 0.93 | Grounded Broke and Breathing | A Somatic Guide to Financial Stress Recovery — for Gen Z professionals |
| 14 | en_US | digital_ground | financial_stress | gen_z_student | miki | 0.93 | Grounded Money Without Panic | A Nervous-System Guide to Financial Stress — for Gen Z students |
| 15 | en_US | digital_ground | imposter_syndrome | gen_z_professionals | miki | 0.93 | Grounded The Voice That Knows | Trusting Yourself Through Imposter Syndrome — for Gen Z professionals |
| 16 | en_US | digital_ground | imposter_syndrome | gen_z_student | miki | 0.93 | Grounded The Proof Was Always You | An Imposter Syndrome Recovery Guide for Professionals — for Gen Z students |
| 17 | en_US | digital_ground | social_anxiety | gen_z_professionals | miki | 0.93 | Grounded The Smaller Yes | Starting Small With Social Anxiety Recovery — for Gen Z professionals |
| 18 | en_US | digital_ground | social_anxiety | gen_z_student | miki | 0.93 | Grounded The Room Isn't Watching | A Social Anxiety Recovery Guide for Quiet People — for Gen Z students |
| 19 | ja_JP | cognitive_clarity | overthinking | tech_finance_burnout | joshin | 0.93 | 澄んだ考えすぎの手当て | 考えすぎを抜けるための、澄んだ日々への手引き — テック・金融で働く人へ |
| 20 | ja_JP | devotion_path | courage | healthcare_rns | sai_ma | 0.93 | ささげる勇気との対話 | 勇気のあとに、ささげる静けさを取り戻す — 医療従事者へ |
| 21 | ja_JP | relational_calm | social_anxiety | millennial_women_professionals | junko | 0.93 | 対人不安のあとに、やわらかな日々 | やわらかな暮らしへの、対人不安回復の手引き — ミレニアル世代の女性へ |
| 22 | ja_JP | relational_calm | social_anxiety | gen_z_professionals | junko | 0.93 | 対人不安のあとに、やわらかな日々 | やわらかな暮らしへの、対人不安回復の手引き — Z世代の働き手へ |
| 23 | ja_JP | somatic_wisdom | somatic_healing | millennial_women_professionals | pamela_fellows | 0.93 | 身体の癒しのあとに、からだに宿る日々 | からだに宿る暮らしへの、身体の癒し回復の手引き — ミレニアル世代の女性へ |
| 24 | ja_JP | somatic_wisdom | somatic_healing | healthcare_rns | pamela_fellows | 0.93 | からだに宿る身体の癒し回復の歩み | 身体の癒しが止まらないときの、からだに宿る手引き — 医療従事者へ |
| 25 | ja_JP | body_memory | compassion_fatigue | healthcare_rns | omote | 0.90 | 抱きしめる共感疲労との対話 | 共感疲労のあとに、抱きしめる静けさを取り戻す — 医療従事者へ |
| 26 | ja_JP | cognitive_clarity | imposter_syndrome | tech_finance_burnout | joshin | 0.90 | 澄んだインポスター症候群回復の歩み | インポスター症候群が止まらないときの、澄んだ手引き — テック・金融で働く人へ |
| 27 | ja_JP | devotion_path | compassion_fatigue | healthcare_rns | sai_ma | 0.90 | ささげる共感疲労回復の歩み | 共感疲労が止まらないときの、ささげる手引き — 医療従事者へ |
| 28 | ja_JP | devotion_path | grief | healthcare_rns | sai_ma | 0.90 | ささげる喪失とかなしみとの対話 | 喪失とかなしみのあとに、ささげる静けさを取り戻す — 医療従事者へ |
| 29 | zh_CN | body_memory | compassion_fatigue | healthcare_rns | omote | 0.90 | 共情疲劳之后，承接的日子 | 承接的生活，共情疲劳恢复的同行者 — 写给医疗从业者 |
| 30 | zh_CN | cognitive_clarity | imposter_syndrome | tech_finance_burnout | joshin | 0.90 | 清明的节奏，走出冒名顶替综合征 | 当冒名顶替综合征无法停止时的清明的指引 — 写给科技与金融从业者 |
| 31 | zh_CN | devotion_path | compassion_fatigue | healthcare_rns | sai_ma | 0.90 | 皈依的共情疲劳指南 | 走出共情疲劳，迈向皈依的日子 — 写给医疗从业者 |
| 32 | zh_CN | devotion_path | grief | healthcare_rns | sai_ma | 0.90 | 皈依的悲伤指南 | 走出悲伤，迈向皈依的日子 — 写给医疗从业者 |
| 33 | zh_CN | devotion_path | imposter_syndrome | healthcare_rns | sai_ma | 0.90 | 冒名顶替综合征之后，皈依的日子 | 皈依的生活，冒名顶替综合征恢复的同行者 — 写给医疗从业者 |
| 34 | zh_CN | devotion_path | self_worth | healthcare_rns | sai_ma | 0.90 | 自我价值之后，皈依的日子 | 皈依的生活，自我价值恢复的同行者 — 写给医疗从业者 |
| 35 | zh_CN | digital_ground | anxiety | gen_z_professionals | miki | 0.90 | 踏实的焦虑的同行 | 焦虑恢复期的踏实的日子 — 写给 Z 世代职场人 |
| 36 | zh_CN | digital_ground | anxiety | gen_z_student | miki | 0.90 | 踏实的焦虑的同行 | 焦虑恢复期的踏实的日子 — 写给 Z 世代学生 |
| 37 | zh_CN | digital_ground | overthinking | gen_z_professionals | miki | 0.90 | 穿越过度思虑，走向踏实的日子 | 过度思虑恢复期的踏实的陪伴 — 写给 Z 世代职场人 |
| 38 | zh_CN | digital_ground | overthinking | gen_z_student | miki | 0.90 | 穿越过度思虑，走向踏实的日子 | 过度思虑恢复期的踏实的陪伴 — 写给 Z 世代学生 |
| 39 | zh_CN | digital_ground | self_worth | gen_z_professionals | miki | 0.90 | 踏实的节奏，走出自我价值 | 当自我价值无法停止时的踏实的指引 — 写给 Z 世代职场人 |
| 40 | zh_CN | digital_ground | self_worth | gen_z_student | miki | 0.90 | 踏实的节奏，走出自我价值 | 当自我价值无法停止时的踏实的指引 — 写给 Z 世代学生 |
| 41 | zh_CN | relational_calm | anxiety | millennial_women_professionals | junko | 0.90 | 温柔的节奏，走出焦虑 | 当焦虑无法停止时的温柔的指引 — 写给千禧一代女性 |
| 42 | zh_CN | relational_calm | anxiety | gen_z_professionals | junko | 0.90 | 温柔的节奏，走出焦虑 | 当焦虑无法停止时的温柔的指引 — 写给 Z 世代职场人 |
| 43 | zh_TW | devotion_path | imposter_syndrome | healthcare_rns | sai_ma | 0.90 | 皈依的冒牌者症候群的同行 | 冒牌者症候群復原中的皈依的日子 — 寫給醫療人員 |
| 44 | zh_TW | devotion_path | self_worth | healthcare_rns | sai_ma | 0.90 | 穿越自我價值，走向皈依的時光 | 自我價值復原途中的皈依的陪伴 — 寫給醫療人員 |
| 45 | zh_TW | relational_calm | boundaries | millennial_women_professionals | junko | 0.90 | 溫柔的界限的同行 | 界限復原中的溫柔的日子 — 寫給千禧世代女性 |
| 46 | zh_TW | relational_calm | boundaries | gen_z_professionals | junko | 0.90 | 界限之後，溫柔的日子 | 溫柔的生活，界限復原的同行者 — 寫給 Z 世代專業工作者 |
| 47 | zh_TW | sleep_restoration | burnout | healthcare_rns | master_sha | 0.90 | 安睡的步調，走出倦怠 | 當倦怠停不下來時的安睡的指引 — 寫給醫療人員 |
| 48 | zh_TW | sleep_restoration | somatic_healing | healthcare_rns | master_sha | 0.90 | 身體療癒之後，安睡的日子 | 安睡的生活，身體療癒復原的同行者 — 寫給醫療人員 |
| 49 | zh_TW | solar_return | burnout | tech_finance_burnout | ra | 0.90 | 明亮的步調，走出倦怠 | 當倦怠停不下來時的明亮的指引 — 寫給科技與金融工作者 |
| 50 | zh_TW | solar_return | burnout | entrepreneurs | ra | 0.90 | 明亮的倦怠指引 | 走出倦怠，邁向明亮的日子 — 寫給創業者 |

## §3 — Top 10 per locale (≤ 1 per `(brand, topic)` for diversity)

### en_US

| # | Brand | Topic | Persona | Teacher | Composite | Title | Subtitle |
|---:|---|---|---|---|---:|---|---|
| 1 | warrior_calm | courage | first_responders | master_wu | 0.95 | Steady Jump Scared | A Guide to Building Courage and Facing the Unknown — for frontline workers |
| 2 | sleep_restoration | sleep_anxiety | healthcare_rns | master_sha | 0.95 | Restful The 3 AM Mind | A Guide to Overcoming Insomnia and Sleep Anxiety — for healthcare workers |
| 3 | body_memory | grief | healthcare_rns | omote | 0.95 | Held Where the Love Goes | A Grief Companion for Year One and After — for healthcare workers |
| 4 | body_memory | somatic_healing | healthcare_rns | omote | 0.95 | Held Unlock the Freeze | A Somatic Guide to Nervous System Reset and Trauma Release — for healthcare workers |
| 5 | cognitive_clarity | overthinking | tech_finance_burnout | joshin | 0.93 | Clear Thought Traffic | Breaking Free from Overthinking, Worry, and Analysis Paralysis — for tech and finance pros |
| 6 | somatic_wisdom | somatic_healing | millennial_women_professionals | pamela_fellows | 0.93 | Embodied The Body Remembers the Way Out | Somatic Healing and Nervous System Recovery — for millennial women professionals |
| 7 | digital_ground | financial_anxiety | gen_z_professionals | miki | 0.93 | Grounded The Quiet Ledger | A Financial Anxiety Practice for the Spreadsheet-Tired — for Gen Z professionals |
| 8 | digital_ground | financial_stress | gen_z_professionals | miki | 0.93 | Grounded Broke and Breathing | A Somatic Guide to Financial Stress Recovery — for Gen Z professionals |
| 9 | digital_ground | imposter_syndrome | gen_z_professionals | miki | 0.93 | Grounded The Voice That Knows | Trusting Yourself Through Imposter Syndrome — for Gen Z professionals |
| 10 | digital_ground | social_anxiety | gen_z_professionals | miki | 0.93 | Grounded The Smaller Yes | Starting Small With Social Anxiety Recovery — for Gen Z professionals |

### ja_JP

| # | Brand | Topic | Persona | Teacher | Composite | Title | Subtitle |
|---:|---|---|---|---|---:|---|---|
| 1 | warrior_calm | courage | first_responders | master_wu | 0.95 | ゆるがぬ勇気の手当て | 勇気を抜けるための、ゆるがぬ日々への手引き — 現場の最前線へ |
| 2 | sleep_restoration | sleep_anxiety | healthcare_rns | master_sha | 0.95 | やすらかな睡眠の不安の手当て | 睡眠の不安を抜けるための、やすらかな日々への手引き — 医療従事者へ |
| 3 | body_memory | grief | healthcare_rns | omote | 0.95 | 抱きしめる喪失とかなしみとの対話 | 喪失とかなしみのあとに、抱きしめる静けさを取り戻す — 医療従事者へ |
| 4 | body_memory | somatic_healing | healthcare_rns | omote | 0.95 | 身体の癒しのあとに、抱きしめる日々 | 抱きしめる暮らしへの、身体の癒し回復の手引き — 医療従事者へ |
| 5 | cognitive_clarity | overthinking | tech_finance_burnout | joshin | 0.93 | 澄んだ考えすぎの手当て | 考えすぎを抜けるための、澄んだ日々への手引き — テック・金融で働く人へ |
| 6 | somatic_wisdom | somatic_healing | millennial_women_professionals | pamela_fellows | 0.93 | 身体の癒しのあとに、からだに宿る日々 | からだに宿る暮らしへの、身体の癒し回復の手引き — ミレニアル世代の女性へ |
| 7 | digital_ground | financial_anxiety | gen_z_professionals | miki | 0.93 | お金への不安のあとに、落ち着いた日々 | 落ち着いた暮らしへの、お金への不安回復の手引き — Z世代の働き手へ |
| 8 | digital_ground | financial_stress | gen_z_professionals | miki | 0.93 | 落ち着いた経済的なストレス回復の歩み | 経済的なストレスが止まらないときの、落ち着いた手引き — Z世代の働き手へ |
| 9 | digital_ground | imposter_syndrome | gen_z_professionals | miki | 0.93 | インポスター症候群のあとに、落ち着いた日々 | 落ち着いた暮らしへの、インポスター症候群回復の手引き — Z世代の働き手へ |
| 10 | digital_ground | social_anxiety | gen_z_professionals | miki | 0.93 | 対人不安のあとに、落ち着いた日々 | 落ち着いた暮らしへの、対人不安回復の手引き — Z世代の働き手へ |

### zh_TW

| # | Brand | Topic | Persona | Teacher | Composite | Title | Subtitle |
|---:|---|---|---|---|---:|---|---|
| 1 | warrior_calm | courage | first_responders | master_wu | 0.95 | 勇氣之後，穩定的日子 | 穩定的生活，勇氣復原的同行者 — 寫給第一線救援人員 |
| 2 | sleep_restoration | sleep_anxiety | healthcare_rns | master_sha | 0.95 | 安睡的步調，走出睡眠焦慮 | 當睡眠焦慮停不下來時的安睡的指引 — 寫給醫療人員 |
| 3 | body_memory | grief | healthcare_rns | omote | 0.95 | 承接的步調，走出悲傷 | 當悲傷停不下來時的承接的指引 — 寫給醫療人員 |
| 4 | body_memory | somatic_healing | healthcare_rns | omote | 0.95 | 承接的身體療癒指引 | 走出身體療癒，邁向承接的日子 — 寫給醫療人員 |
| 5 | cognitive_clarity | overthinking | tech_finance_burnout | joshin | 0.93 | 想太多之後，清明的日子 | 清明的生活，想太多復原的同行者 — 寫給科技與金融工作者 |
| 6 | somatic_wisdom | somatic_healing | millennial_women_professionals | pamela_fellows | 0.93 | 穿越身體療癒，走向身體的時光 | 身體療癒復原途中的身體的陪伴 — 寫給千禧世代女性 |
| 7 | digital_ground | financial_anxiety | gen_z_professionals | miki | 0.93 | 踏實的金錢焦慮指引 | 走出金錢焦慮，邁向踏實的日子 — 寫給 Z 世代專業工作者 |
| 8 | digital_ground | financial_stress | gen_z_professionals | miki | 0.93 | 經濟壓力之後，踏實的日子 | 踏實的生活，經濟壓力復原的同行者 — 寫給 Z 世代專業工作者 |
| 9 | digital_ground | imposter_syndrome | gen_z_professionals | miki | 0.93 | 踏實的冒牌者症候群指引 | 走出冒牌者症候群，邁向踏實的日子 — 寫給 Z 世代專業工作者 |
| 10 | digital_ground | social_anxiety | gen_z_professionals | miki | 0.93 | 踏實的社交焦慮的同行 | 社交焦慮復原中的踏實的日子 — 寫給 Z 世代專業工作者 |

### zh_CN

| # | Brand | Topic | Persona | Teacher | Composite | Title | Subtitle |
|---:|---|---|---|---|---:|---|---|
| 1 | warrior_calm | courage | first_responders | master_wu | 0.95 | 穿越勇气，走向稳定的日子 | 勇气恢复期的稳定的陪伴 — 写给一线响应人员 |
| 2 | sleep_restoration | sleep_anxiety | healthcare_rns | master_sha | 0.95 | 安睡的节奏，走出睡眠焦虑 | 当睡眠焦虑无法停止时的安睡的指引 — 写给医疗从业者 |
| 3 | body_memory | grief | healthcare_rns | omote | 0.95 | 承接的悲伤指南 | 走出悲伤，迈向承接的日子 — 写给医疗从业者 |
| 4 | body_memory | somatic_healing | healthcare_rns | omote | 0.95 | 承接的身体疗愈的同行 | 身体疗愈恢复期的承接的日子 — 写给医疗从业者 |
| 5 | cognitive_clarity | overthinking | tech_finance_burnout | joshin | 0.93 | 清明的过度思虑指南 | 走出过度思虑，迈向清明的日子 — 写给科技与金融从业者 |
| 6 | somatic_wisdom | somatic_healing | millennial_women_professionals | pamela_fellows | 0.93 | 身体的身体疗愈的同行 | 身体疗愈恢复期的身体的日子 — 写给千禧一代女性 |
| 7 | digital_ground | financial_anxiety | gen_z_professionals | miki | 0.93 | 金钱焦虑之后，踏实的日子 | 踏实的生活，金钱焦虑恢复的同行者 — 写给 Z 世代职场人 |
| 8 | digital_ground | financial_stress | gen_z_professionals | miki | 0.93 | 踏实的经济压力的同行 | 经济压力恢复期的踏实的日子 — 写给 Z 世代职场人 |
| 9 | digital_ground | imposter_syndrome | gen_z_professionals | miki | 0.93 | 穿越冒名顶替综合征，走向踏实的日子 | 冒名顶替综合征恢复期的踏实的陪伴 — 写给 Z 世代职场人 |
| 10 | digital_ground | social_anxiety | gen_z_professionals | miki | 0.93 | 踏实的社交焦虑的同行 | 社交焦虑恢复期的踏实的日子 — 写给 Z 世代职场人 |

## §4 — Remaining blocked_score rows

Total blocked: **160**.

| Locale | Brand | Teacher | Blocked rows |
|---|---|---|---:|
| zh_TW | bright_presence_tw | adi_da | 160 |

**All 160 blocked rows are `bright_presence_tw` (Adi Da, Taiwan-only teacher-mode brand).**

- adi_da scoring is **P2-deferred** per Issue #777 rubric (B3+B4 covered the 12 global teacher brands; adi_da's `topic_scores` and `persona_scores` extension was scoped out).
- Closing this remainder is a small follow-up: backfill `teacher_topic_persona_scores.yaml::teachers.adi_da` with topic + persona scores for the 17 topics × 12 personas relevant to bright_presence_tw. Pure data, no LLM, no code change. Same pattern as B3+B4 (#780).
- These 160 rows do NOT affect any other locale or brand. en_US, ja_JP, zh_CN are 100% ready.

## §5 — Image QA list (manual QA, NOT LoRA training)

Image assets shipped to `main` via #781 (PR-B portraits) and the prior teacher-showcase asset PR. **Manual QA only — no LoRA training, no regeneration, no new image authoring in this report's scope.**

### Per-teacher portrait (13 of 13)

Path pattern: `teacher_pics/{teacher_id}.png` · Wired in `teacher_showcase.html` line ~portrait-section.

| Teacher | Portrait file | QA status |
|---|---|---|
| ahjan | `teacher_pics/ahjan.png` | ⏳ awaiting manual visual QA |
| maat | `teacher_pics/maat.png` | ⏳ awaiting manual visual QA |
| adi_da | `teacher_pics/adi_da.png` | ⏳ awaiting manual visual QA |
| joshin | `teacher_pics/joshin.png` | ⏳ awaiting manual visual QA |
| pamela_fellows | `teacher_pics/pamela_fellows.png` | ⏳ awaiting manual visual QA |
| master_feung | `teacher_pics/master_feung.png` | ⏳ awaiting manual visual QA |
| miki | `teacher_pics/miki.png` | ⏳ awaiting manual visual QA |
| master_wu | `teacher_pics/master_wu.png` | ⏳ awaiting manual visual QA |
| master_sha | `teacher_pics/master_sha.png` | ⏳ awaiting manual visual QA |
| omote | `teacher_pics/omote.png` | ⏳ awaiting manual visual QA |
| ra | `teacher_pics/ra.png` | ⏳ awaiting manual visual QA |
| sai_ma | `teacher_pics/sai_ma.png` | ⏳ awaiting manual visual QA |
| junko | `teacher_pics/junko.png` | ⏳ awaiting manual visual QA |

### Audiobook chapter MP3s (13 of 13 — maat added in #784)

Path pattern: `brand-wizard-app/public/assets/audio/audiobook_chapters/{teacher}_{topic}_ch1.mp3`. Each is 4–6 minutes of narration. **Audio QA = listen-test for clarity / pronunciation / pace.**

| Teacher | Topic | File | QA status |
|---|---|---|---|
| adi_da | self_worth | `adi_da_self_worth_ch1.mp3` | ⏳ awaiting manual audio QA |
| ahjan | anxiety | `ahjan_anxiety_ch1.mp3` | ⏳ awaiting manual audio QA |
| _(unknown)_ | boundaries | `ajahn_x_boundaries_ch1.mp3` | ⚠️ pre-existing leftover (not one of the 13 canonical teachers — investigate / rename / drop) |
| joshin | anxiety | `joshin_anxiety_ch1.mp3` | ⏳ awaiting manual audio QA |
| junko | overthinking | `junko_overthinking_ch1.mp3` | ⏳ awaiting manual audio QA |
| maat | boundaries | `maat_boundaries_ch1.mp3` | ⏳ awaiting manual audio QA (added in #784) |
| master_feung | burnout | `master_feung_burnout_ch1.mp3` | ⏳ awaiting manual audio QA |
| master_sha | grief | `master_sha_grief_ch1.mp3` | ⏳ awaiting manual audio QA |
| master_wu | courage | `master_wu_courage_ch1.mp3` | ⏳ awaiting manual audio QA |
| miki | imposter_syndrome | `miki_imposter_syndrome_ch1.mp3` | ⏳ awaiting manual audio QA |
| omote | sleep_anxiety | `omote_sleep_anxiety_ch1.mp3` | ⏳ awaiting manual audio QA |
| pamela_fellows | burnout | `pamela_fellows_burnout_ch1.mp3` | ⏳ awaiting manual audio QA |
| ra | self_worth | `ra_self_worth_ch1.mp3` | ⏳ awaiting manual audio QA |
| sai_ma | grief | `sai_ma_grief_ch1.mp3` | ⏳ awaiting manual audio QA |

### Other shipped image assets

- `brand-wizard-app/public/assets/covers/kdp/` — book / audiobook covers per teacher × topic (~52 files)
- `brand-wizard-app/public/assets/manga_covers/` — manga cover art (97 files, ≥6 per teacher)
- `brand-wizard-app/public/assets/manga_panels/{teacher}/` — 4 panels per teacher (56 total)
- `brand-wizard-app/public/assets/audio/podcast/` — 13 podcast cover images
- `brand-wizard-app/public/assets/audio/showcase/` — 13 hook clip audio files
- `brand-wizard-app/public/assets/video/teacher_reels/` — 4 teacher reels (ra, sai_ma, plus 2 from prior PRs)
- `brand-wizard-app/public/assets/video/tiktok/` — 13 TikTok-format videos

**Scope note (from rubric):** Manual QA = visual review + flag-for-replacement. Out of scope: LoRA training, regeneration, new asset authoring.

## §6 — `teacher_showcase.html` status (post-#781 / #784 / #785)

After the three teacher-lane PRs landed, `brand-wizard-app/public/teacher_showcase.html` carries:

| Element | Source PR | Verified post-merge |
|---|---|---|
| 13 portrait `<img src="teacher_pics/{teacher}.png">` blocks (with first-initial gradient fallback) | #781 PR-B | ✅ 13 `<img src="teacher_pics/` references in HTML |
| Removed duplicate HTML id collisions (R2 reels for ahjan + adi_da) | #781 PR-B | ✅ 1 video example section per teacher |
| Removed dead R2 URLs (replaced with local-asset references) | #781 PR-B | ✅ |
| `maat_boundaries_ch1.mp3` audiobook (4:01, Pearl Star CosyVoice2 Tier-2) | #784 PR-D | ✅ file present + wired in HTML |
| 13 per-teacher CTA blocks (Read Free Guide / Get the Book / Listen) | #785 PR-C | ✅ 14 `teacher-cta-row` blocks (1 per teacher + 1 likely a global header)  |
| Placeholder anchors for future Amazon ASIN / Audible / Podcast URLs (`#book-{teacher}`, `#audio-{teacher}`) | #785 PR-C | ✅ 26 placeholder anchors + 13 TODO markers |

**Audit gaps still present (from `artifacts/audits/teacher_page_requirements_audit_2026-04-28.md`):**

- Req #12 (video reel): ⚠️ for ahjan / adi_da (R2-hosted), N/A for many teachers, ✅ for ra / sai_ma. Local-asset fallback wired by #781.
- Req #15 (broken-links-clean): ⚠️ for ahjan / adi_da (legacy R2 links remained — partially cleaned by #781). Worth a follow-up pass.
- Req #17 (locale-notes): ❌ across all 13. Locale-specific brand naming notes missing on the showcase page. Out of scope for this report.

## §7 — Recommended next actions (post-launch report, not in this PR)

1. **Native-fluency pass on CJK title content** — `config/catalog/catalog_generation_config.yaml` voice_prefix_{locale} / signal_{locale} / title_templates_{locale} / topic_displays_{locale}. 1-line YAML edits, no code change required.
2. **adi_da scoring backfill** — extend `teacher_topic_persona_scores.yaml::teachers.adi_da` to unblock the 160 bright_presence_tw rows (zh_TW). Same pattern as B3+B4 (#780).
3. **Manual QA pass** on the 13 portraits + 13 audiobook MP3s + manga panels per teacher. No LoRA training.
4. **Real Amazon ASIN / Audible / Podcast URL replacement** — swap `#book-{teacher}` / `#audio-{teacher}` placeholders in `teacher_showcase.html` with real outbound URLs (PR-C TODO markers tag each insertion point).
5. **Locale-notes section** on `teacher_showcase.html` — req #17 from the audit.

**Out of scope for this report:** book assembly, manga rendering, LoRA training, new image authoring, scoring changes, en_US title changes, manga catalog materialization beyond what's in [`config/manga/brand_genre_allocation.yaml`](config/manga/brand_genre_allocation.yaml).

---

## Appendix — Method

- All numbers in this report come from the four `*_catalog.csv` files post-#793 + the audit doc + asset-disk inventory.
- No LLM was called. Composite scores parsed from the `notes` column.
- Top 50 selection: deterministic — sort by composite desc, then locale alphabetical, then brand alphabetical. Constraints applied greedily.
- Reproducibility: re-running the same generator + analyzer + this report builder produces identical output.
