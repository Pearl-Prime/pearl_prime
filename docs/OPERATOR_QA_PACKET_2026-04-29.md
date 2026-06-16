# Operator QA Packet — Pearl Prime Catalog Launch Review

**Generated:** 2026-04-28 22:28 UTC
**Branch state:** `origin/main` post-#796 (final launch report) + #792 (cluster analyzer)
**Purpose:** show the operator what to approve. No catalog or generation changes.
**Reproduction:** `python3 scripts/catalog/build_operator_qa_packet.py`

---

## How to use this packet

1. Skim §1 (Top 50) and §2 (Top 10 per locale) — pick 10–20 to launch first.
2. Walk §3 (teacher showcase QA checklist) — mark each row approve / reject / fix.
3. Walk §4 (image/audio asset matrix) — flag missing or low-quality assets.
4. Fill §5 (CTA replacement list) — provide real storefront / freebie URLs to replace placeholders.

---

## §1 — Top 50 launch candidates

Source: [`artifacts/catalog/launch_baseline/top_50_combined.csv`](artifacts/catalog/launch_baseline/top_50_combined.csv)

Each row links to its source catalog CSV with a row index (`source_row` is 1-based; row 1 = CSV header, so row 2 = first data row).

| # | Lane | Locale | Brand | Topic/Genre | Persona | Teacher | Composite | Title | Subtitle | Source row |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | manga | ja_JP | sleep_restoration | healing |  |  | 1.00 | [needs_locale_native_synthesis] |  | manga (see manga catalog) |
| 2 | manga | ja_JP | sleep_restoration | healing |  |  | 1.00 | [needs_locale_native_synthesis] |  | manga (see manga catalog) |
| 3 | manga | ja_JP | sleep_restoration | healing |  |  | 1.00 | [needs_locale_native_synthesis] |  | manga (see manga catalog) |
| 4 | manga | ja_JP | sleep_restoration | healing |  |  | 1.00 | [needs_locale_native_synthesis] |  | manga (see manga catalog) |
| 5 | manga | ja_JP | sleep_restoration | healing |  |  | 1.00 | [needs_locale_native_synthesis] |  | manga (see manga catalog) |
| 6 | book_script | en_US | warrior_calm | courage | first_responders | master_wu | 0.95 | Steady Jump Scared |  | [en_US #939](artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv) |
| 7 | book_script | en_US | sleep_restoration | sleep_anxiety | healthcare_rns | master_sha | 0.95 | Restful The 3 AM Mind |  | [en_US #1086](artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv) |
| 8 | book_script | en_US | body_memory | grief | healthcare_rns | omote | 0.95 | Held Where the Love Goes |  | [en_US #1161](artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv) |
| 9 | book_script | en_US | body_memory | somatic_healing | healthcare_rns | omote | 0.95 | Held Unlock the Freeze |  | [en_US #1210](artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv) |
| 10 | book_script | ja_JP | warrior_calm | courage | first_responders | master_wu | 0.95 | ゆるがぬ勇気の手当て |  | [ja_JP #939](artifacts/catalog/pearl_prime_book_script_catalogs/ja_JP_catalog.csv) |
| 11 | book_script | ja_JP | sleep_restoration | sleep_anxiety | healthcare_rns | master_sha | 0.95 | やすらかな睡眠の不安の手当て |  | [ja_JP #1086](artifacts/catalog/pearl_prime_book_script_catalogs/ja_JP_catalog.csv) |
| 12 | book_script | ja_JP | body_memory | grief | healthcare_rns | omote | 0.95 | 抱きしめる喪失とかなしみとの対話 |  | [ja_JP #1161](artifacts/catalog/pearl_prime_book_script_catalogs/ja_JP_catalog.csv) |
| 13 | book_script | ja_JP | body_memory | somatic_healing | healthcare_rns | omote | 0.95 | 身体の癒しのあとに、抱きしめる日々 |  | [ja_JP #1210](artifacts/catalog/pearl_prime_book_script_catalogs/ja_JP_catalog.csv) |
| 14 | book_script | zh_TW | warrior_calm | courage | first_responders | master_wu | 0.95 | 勇氣之後，穩定的日子 |  | [zh_TW #2091](artifacts/catalog/pearl_prime_book_script_catalogs/zh_TW_catalog.csv) |
| 15 | book_script | zh_TW | sleep_restoration | sleep_anxiety | healthcare_rns | master_sha | 0.95 | 安睡的步調，走出睡眠焦慮 |  | [zh_TW #2238](artifacts/catalog/pearl_prime_book_script_catalogs/zh_TW_catalog.csv) |
| 16 | book_script | zh_TW | body_memory | grief | healthcare_rns | omote | 0.95 | 承接的步調，走出悲傷 |  | [zh_TW #2313](artifacts/catalog/pearl_prime_book_script_catalogs/zh_TW_catalog.csv) |
| 17 | book_script | zh_TW | body_memory | somatic_healing | healthcare_rns | omote | 0.95 | 承接的身體療癒指引 |  | [zh_TW #2362](artifacts/catalog/pearl_prime_book_script_catalogs/zh_TW_catalog.csv) |
| 18 | book_script | zh_CN | warrior_calm | courage | first_responders | master_wu | 0.95 | 穿越勇气，走向稳定的日子 |  | [zh_CN #2091](artifacts/catalog/pearl_prime_book_script_catalogs/zh_CN_catalog.csv) |
| 19 | book_script | zh_CN | sleep_restoration | sleep_anxiety | healthcare_rns | master_sha | 0.95 | 安睡的节奏，走出睡眠焦虑 |  | [zh_CN #2238](artifacts/catalog/pearl_prime_book_script_catalogs/zh_CN_catalog.csv) |
| 20 | book_script | zh_CN | body_memory | grief | healthcare_rns | omote | 0.95 | 承接的悲伤指南 |  | [zh_CN #2313](artifacts/catalog/pearl_prime_book_script_catalogs/zh_CN_catalog.csv) |
| 21 | book_script | zh_CN | body_memory | somatic_healing | healthcare_rns | omote | 0.95 | 承接的身体疗愈的同行 |  | [zh_CN #2362](artifacts/catalog/pearl_prime_book_script_catalogs/zh_CN_catalog.csv) |
| 22 | book_script | en_US | cognitive_clarity | overthinking | tech_finance_burnout | joshin | 0.93 | Clear Thought Traffic |  | [en_US #262](artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv) |
| 23 | book_script | en_US | somatic_wisdom | somatic_healing | millennial_women_professionals | pamela_fellows | 0.93 | Embodied The Body Remembers the Way Out |  | [en_US #396](artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv) |
| 24 | book_script | en_US | somatic_wisdom | somatic_healing | healthcare_rns | pamela_fellows | 0.93 | Embodied The Body Remembers the Way Out |  | [en_US #399](artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv) |
| 25 | book_script | en_US | digital_ground | financial_anxiety | gen_z_professionals | miki | 0.93 | Grounded The Quiet Ledger |  | [en_US #556](artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv) |
| 26 | book_script | en_US | digital_ground | financial_anxiety | gen_z_student | miki | 0.93 | Grounded Broke and Breathing |  | [en_US #562](artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv) |
| 27 | book_script | en_US | digital_ground | financial_stress | gen_z_professionals | miki | 0.93 | Grounded Broke and Breathing |  | [en_US #566](artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv) |
| 28 | book_script | en_US | digital_ground | financial_stress | gen_z_student | miki | 0.93 | Grounded Money Without Panic |  | [en_US #572](artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv) |
| 29 | book_script | en_US | digital_ground | imposter_syndrome | gen_z_professionals | miki | 0.93 | Grounded The Voice That Knows |  | [en_US #578](artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv) |
| 30 | book_script | en_US | digital_ground | imposter_syndrome | gen_z_student | miki | 0.93 | Grounded The Proof Was Always You |  | [en_US #585](artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv) |
| 31 | book_script | en_US | digital_ground | social_anxiety | gen_z_professionals | miki | 0.93 | Grounded The Smaller Yes |  | [en_US #620](artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv) |
| 32 | book_script | en_US | digital_ground | social_anxiety | gen_z_student | miki | 0.93 | Grounded The Room Isn't Watching |  | [en_US #627](artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv) |
| 33 | book_script | en_US | relational_calm | social_anxiety | millennial_women_professionals | junko | 0.93 | Together The Smaller Yes |  | [en_US #880](artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv) |
| 34 | book_script | en_US | relational_calm | social_anxiety | gen_z_professionals | junko | 0.93 | Together Visible at Your Own Pace |  | [en_US #882](artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv) |
| 35 | book_script | en_US | sleep_restoration | sleep_anxiety | first_responders | master_sha | 0.93 | Restful Reclaim the Night |  | [en_US #1087](artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv) |
| 36 | book_script | en_US | sleep_restoration | sleep_anxiety | working_parents | master_sha | 0.93 | Restful The 3 AM Mind |  | [en_US #1089](artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv) |
| 37 | book_script | en_US | body_memory | grief | gen_x_sandwich | omote | 0.93 | Held Carry It Lightly |  | [en_US #1166](artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv) |
| 38 | book_script | en_US | body_memory | somatic_healing | gen_x_sandwich | omote | 0.93 | Held The Body's Slow Yes |  | [en_US #1215](artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv) |
| 39 | book_script | en_US | devotion_path | courage | healthcare_rns | sai_ma | 0.93 | Devoted Jump Scared |  | [en_US #1402](artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv) |
| 40 | book_script | ja_JP | cognitive_clarity | overthinking | tech_finance_burnout | joshin | 0.93 | 澄んだ考えすぎの手当て |  | [ja_JP #262](artifacts/catalog/pearl_prime_book_script_catalogs/ja_JP_catalog.csv) |
| 41 | book_script | ja_JP | somatic_wisdom | somatic_healing | millennial_women_professionals | pamela_fellows | 0.93 | 身体の癒しのあとに、からだに宿る日々 |  | [ja_JP #396](artifacts/catalog/pearl_prime_book_script_catalogs/ja_JP_catalog.csv) |
| 42 | book_script | ja_JP | somatic_wisdom | somatic_healing | healthcare_rns | pamela_fellows | 0.93 | からだに宿る身体の癒し回復の歩み |  | [ja_JP #399](artifacts/catalog/pearl_prime_book_script_catalogs/ja_JP_catalog.csv) |
| 43 | book_script | ja_JP | digital_ground | financial_anxiety | gen_z_professionals | miki | 0.93 | お金への不安のあとに、落ち着いた日々 |  | [ja_JP #556](artifacts/catalog/pearl_prime_book_script_catalogs/ja_JP_catalog.csv) |
| 44 | book_script | ja_JP | digital_ground | financial_anxiety | gen_z_student | miki | 0.93 | 落ち着いたお金への不安との対話 |  | [ja_JP #562](artifacts/catalog/pearl_prime_book_script_catalogs/ja_JP_catalog.csv) |
| 45 | book_script | ja_JP | digital_ground | financial_stress | gen_z_professionals | miki | 0.93 | 落ち着いた経済的なストレス回復の歩み |  | [ja_JP #566](artifacts/catalog/pearl_prime_book_script_catalogs/ja_JP_catalog.csv) |
| 46 | book_script | ja_JP | digital_ground | financial_stress | gen_z_student | miki | 0.93 | 落ち着いた経済的なストレス回復の歩み |  | [ja_JP #572](artifacts/catalog/pearl_prime_book_script_catalogs/ja_JP_catalog.csv) |
| 47 | book_script | ja_JP | digital_ground | imposter_syndrome | gen_z_professionals | miki | 0.93 | インポスター症候群のあとに、落ち着いた日々 |  | [ja_JP #578](artifacts/catalog/pearl_prime_book_script_catalogs/ja_JP_catalog.csv) |
| 48 | book_script | ja_JP | digital_ground | imposter_syndrome | gen_z_student | miki | 0.93 | 落ち着いたインポスター症候群回復の歩み |  | [ja_JP #585](artifacts/catalog/pearl_prime_book_script_catalogs/ja_JP_catalog.csv) |
| 49 | book_script | ja_JP | digital_ground | social_anxiety | gen_z_professionals | miki | 0.93 | 対人不安のあとに、落ち着いた日々 |  | [ja_JP #620](artifacts/catalog/pearl_prime_book_script_catalogs/ja_JP_catalog.csv) |
| 50 | book_script | ja_JP | digital_ground | social_anxiety | gen_z_student | miki | 0.93 | 対人不安のあとに、落ち着いた日々 |  | [ja_JP #627](artifacts/catalog/pearl_prime_book_script_catalogs/ja_JP_catalog.csv) |

---

## §2 — Top 10 per locale

### §2.1 — en_US

Source: [`artifacts/catalog/launch_baseline/top_10_book_scripts_en_US.csv`](artifacts/catalog/launch_baseline/top_10_book_scripts_en_US.csv)

| # | Brand | Topic | Persona | Teacher | Composite | Title | Source row |
|---|---|---|---|---|---|---|---|
| 1 | warrior_calm | courage | first_responders | master_wu | 0.95 | Steady Jump Scared | [#939](artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv) |
| 2 | sleep_restoration | sleep_anxiety | healthcare_rns | master_sha | 0.95 | Restful The 3 AM Mind | [#1086](artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv) |
| 3 | body_memory | grief | healthcare_rns | omote | 0.95 | Held Where the Love Goes | [#1161](artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv) |
| 4 | body_memory | somatic_healing | healthcare_rns | omote | 0.95 | Held Unlock the Freeze | [#1210](artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv) |
| 5 | cognitive_clarity | overthinking | tech_finance_burnout | joshin | 0.93 | Clear Thought Traffic | [#262](artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv) |
| 6 | somatic_wisdom | somatic_healing | millennial_women_professionals | pamela_fellows | 0.93 | Embodied The Body Remembers the Way Out | [#396](artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv) |
| 7 | somatic_wisdom | somatic_healing | healthcare_rns | pamela_fellows | 0.93 | Embodied The Body Remembers the Way Out | [#399](artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv) |
| 8 | digital_ground | financial_anxiety | gen_z_professionals | miki | 0.93 | Grounded The Quiet Ledger | [#556](artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv) |
| 9 | digital_ground | financial_anxiety | gen_z_student | miki | 0.93 | Grounded Broke and Breathing | [#562](artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv) |
| 10 | digital_ground | financial_stress | gen_z_professionals | miki | 0.93 | Grounded Broke and Breathing | [#566](artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv) |

### §2.2 — ja_JP

Source: [`artifacts/catalog/launch_baseline/top_10_book_scripts_ja_JP.csv`](artifacts/catalog/launch_baseline/top_10_book_scripts_ja_JP.csv)

| # | Brand | Topic | Persona | Teacher | Composite | Title | Source row |
|---|---|---|---|---|---|---|---|
| 1 | warrior_calm | courage | first_responders | master_wu | 0.95 | ゆるがぬ勇気の手当て | [#939](artifacts/catalog/pearl_prime_book_script_catalogs/ja_JP_catalog.csv) |
| 2 | sleep_restoration | sleep_anxiety | healthcare_rns | master_sha | 0.95 | やすらかな睡眠の不安の手当て | [#1086](artifacts/catalog/pearl_prime_book_script_catalogs/ja_JP_catalog.csv) |
| 3 | body_memory | grief | healthcare_rns | omote | 0.95 | 抱きしめる喪失とかなしみとの対話 | [#1161](artifacts/catalog/pearl_prime_book_script_catalogs/ja_JP_catalog.csv) |
| 4 | body_memory | somatic_healing | healthcare_rns | omote | 0.95 | 身体の癒しのあとに、抱きしめる日々 | [#1210](artifacts/catalog/pearl_prime_book_script_catalogs/ja_JP_catalog.csv) |
| 5 | cognitive_clarity | overthinking | tech_finance_burnout | joshin | 0.93 | 澄んだ考えすぎの手当て | [#262](artifacts/catalog/pearl_prime_book_script_catalogs/ja_JP_catalog.csv) |
| 6 | somatic_wisdom | somatic_healing | millennial_women_professionals | pamela_fellows | 0.93 | 身体の癒しのあとに、からだに宿る日々 | [#396](artifacts/catalog/pearl_prime_book_script_catalogs/ja_JP_catalog.csv) |
| 7 | somatic_wisdom | somatic_healing | healthcare_rns | pamela_fellows | 0.93 | からだに宿る身体の癒し回復の歩み | [#399](artifacts/catalog/pearl_prime_book_script_catalogs/ja_JP_catalog.csv) |
| 8 | digital_ground | financial_anxiety | gen_z_professionals | miki | 0.93 | お金への不安のあとに、落ち着いた日々 | [#556](artifacts/catalog/pearl_prime_book_script_catalogs/ja_JP_catalog.csv) |
| 9 | digital_ground | financial_anxiety | gen_z_student | miki | 0.93 | 落ち着いたお金への不安との対話 | [#562](artifacts/catalog/pearl_prime_book_script_catalogs/ja_JP_catalog.csv) |
| 10 | digital_ground | financial_stress | gen_z_professionals | miki | 0.93 | 落ち着いた経済的なストレス回復の歩み | [#566](artifacts/catalog/pearl_prime_book_script_catalogs/ja_JP_catalog.csv) |

### §2.3 — zh_TW

Source: [`artifacts/catalog/launch_baseline/top_10_book_scripts_zh_TW.csv`](artifacts/catalog/launch_baseline/top_10_book_scripts_zh_TW.csv)

| # | Brand | Topic | Persona | Teacher | Composite | Title | Source row |
|---|---|---|---|---|---|---|---|
| 1 | warrior_calm | courage | first_responders | master_wu | 0.95 | 勇氣之後，穩定的日子 | [#2091](artifacts/catalog/pearl_prime_book_script_catalogs/zh_TW_catalog.csv) |
| 2 | sleep_restoration | sleep_anxiety | healthcare_rns | master_sha | 0.95 | 安睡的步調，走出睡眠焦慮 | [#2238](artifacts/catalog/pearl_prime_book_script_catalogs/zh_TW_catalog.csv) |
| 3 | body_memory | grief | healthcare_rns | omote | 0.95 | 承接的步調，走出悲傷 | [#2313](artifacts/catalog/pearl_prime_book_script_catalogs/zh_TW_catalog.csv) |
| 4 | body_memory | somatic_healing | healthcare_rns | omote | 0.95 | 承接的身體療癒指引 | [#2362](artifacts/catalog/pearl_prime_book_script_catalogs/zh_TW_catalog.csv) |
| 5 | cognitive_clarity | overthinking | tech_finance_burnout | joshin | 0.93 | 想太多之後，清明的日子 | [#1414](artifacts/catalog/pearl_prime_book_script_catalogs/zh_TW_catalog.csv) |
| 6 | somatic_wisdom | somatic_healing | millennial_women_professionals | pamela_fellows | 0.93 | 穿越身體療癒，走向身體的時光 | [#1548](artifacts/catalog/pearl_prime_book_script_catalogs/zh_TW_catalog.csv) |
| 7 | somatic_wisdom | somatic_healing | healthcare_rns | pamela_fellows | 0.93 | 身體療癒之後，身體的日子 | [#1551](artifacts/catalog/pearl_prime_book_script_catalogs/zh_TW_catalog.csv) |
| 8 | digital_ground | financial_anxiety | gen_z_professionals | miki | 0.93 | 踏實的金錢焦慮指引 | [#1708](artifacts/catalog/pearl_prime_book_script_catalogs/zh_TW_catalog.csv) |
| 9 | digital_ground | financial_anxiety | gen_z_student | miki | 0.93 | 踏實的步調，走出金錢焦慮 | [#1714](artifacts/catalog/pearl_prime_book_script_catalogs/zh_TW_catalog.csv) |
| 10 | digital_ground | financial_stress | gen_z_professionals | miki | 0.93 | 經濟壓力之後，踏實的日子 | [#1718](artifacts/catalog/pearl_prime_book_script_catalogs/zh_TW_catalog.csv) |

### §2.4 — zh_CN

Source: [`artifacts/catalog/launch_baseline/top_10_book_scripts_zh_CN.csv`](artifacts/catalog/launch_baseline/top_10_book_scripts_zh_CN.csv)

| # | Brand | Topic | Persona | Teacher | Composite | Title | Source row |
|---|---|---|---|---|---|---|---|
| 1 | warrior_calm | courage | first_responders | master_wu | 0.95 | 穿越勇气，走向稳定的日子 | [#2091](artifacts/catalog/pearl_prime_book_script_catalogs/zh_CN_catalog.csv) |
| 2 | sleep_restoration | sleep_anxiety | healthcare_rns | master_sha | 0.95 | 安睡的节奏，走出睡眠焦虑 | [#2238](artifacts/catalog/pearl_prime_book_script_catalogs/zh_CN_catalog.csv) |
| 3 | body_memory | grief | healthcare_rns | omote | 0.95 | 承接的悲伤指南 | [#2313](artifacts/catalog/pearl_prime_book_script_catalogs/zh_CN_catalog.csv) |
| 4 | body_memory | somatic_healing | healthcare_rns | omote | 0.95 | 承接的身体疗愈的同行 | [#2362](artifacts/catalog/pearl_prime_book_script_catalogs/zh_CN_catalog.csv) |
| 5 | cognitive_clarity | overthinking | tech_finance_burnout | joshin | 0.93 | 清明的过度思虑指南 | [#1414](artifacts/catalog/pearl_prime_book_script_catalogs/zh_CN_catalog.csv) |
| 6 | somatic_wisdom | somatic_healing | millennial_women_professionals | pamela_fellows | 0.93 | 身体的身体疗愈的同行 | [#1548](artifacts/catalog/pearl_prime_book_script_catalogs/zh_CN_catalog.csv) |
| 7 | somatic_wisdom | somatic_healing | healthcare_rns | pamela_fellows | 0.93 | 身体的身体疗愈指南 | [#1551](artifacts/catalog/pearl_prime_book_script_catalogs/zh_CN_catalog.csv) |
| 8 | digital_ground | financial_anxiety | gen_z_professionals | miki | 0.93 | 金钱焦虑之后，踏实的日子 | [#1708](artifacts/catalog/pearl_prime_book_script_catalogs/zh_CN_catalog.csv) |
| 9 | digital_ground | financial_anxiety | gen_z_student | miki | 0.93 | 踏实的金钱焦虑的同行 | [#1714](artifacts/catalog/pearl_prime_book_script_catalogs/zh_CN_catalog.csv) |
| 10 | digital_ground | financial_stress | gen_z_professionals | miki | 0.93 | 踏实的经济压力的同行 | [#1718](artifacts/catalog/pearl_prime_book_script_catalogs/zh_CN_catalog.csv) |

---

## §3 — Teacher showcase QA checklist

Source: [`brand-wizard-app/public/teacher_showcase.html`](brand-wizard-app/public/teacher_showcase.html)

13 teacher sections present. Walk each row, mark approve / reject / needs_fix.

| Teacher | Portrait | Audiobook Ch1 | Showcase Hook | Podcast 3min | Video Reel | YouTube | Manga Cover | Manga Panels | Reviewer mark |
|---|---|---|---|---|---|---|---|---|---|
| `ahjan` | ✅ `brand-wizard-app/public/teacher_pics/ahjan.png` | ✅ `brand-wizard-app/public/assets/audio/audiobook_chapters/ahjan_anxiety_ch1.mp3` | ✅ `brand-wizard-app/public/assets/audio/showcase/ahjan_depression_hook.mp3` | ✅ `brand-wizard-app/public/assets/audio/podcast/ahjan_podcast_3min.mp3` | ✅ `brand-wizard-app/public/assets/video/teacher_reels/ahjan_reel.mp4` | ❌ MISSING | ✅ `brand-wizard-app/public/assets/manga_covers/ahjan_cover_anxiety.png` | ✅ 4 pages | [ ] approve  [ ] reject  [ ] needs_fix |
| `adi_da` | ✅ `brand-wizard-app/public/teacher_pics/adi_da.png` | ✅ `brand-wizard-app/public/assets/audio/audiobook_chapters/adi_da_self_worth_ch1.mp3` | ✅ `brand-wizard-app/public/assets/audio/showcase/adi_da_depression_hook.mp3` | ✅ `brand-wizard-app/public/assets/audio/podcast/adi_da_podcast_3min.mp3` | ✅ `brand-wizard-app/public/assets/video/teacher_reels/adi_da_reel.mp4` | ❌ MISSING | ✅ `brand-wizard-app/public/assets/manga_covers/adi_da_cover_self_worth.png` | ✅ 4 pages | [ ] approve  [ ] reject  [ ] needs_fix |
| `master_feung` | ✅ `brand-wizard-app/public/teacher_pics/master_feung.png` | ✅ `brand-wizard-app/public/assets/audio/audiobook_chapters/master_feung_burnout_ch1.mp3` | ✅ `brand-wizard-app/public/assets/audio/showcase/master_feung_self_worth_hook.mp3` | ✅ `brand-wizard-app/public/assets/audio/podcast/master_feung_podcast_3min.mp3` | ❌ MISSING | ❌ MISSING | ✅ `brand-wizard-app/public/assets/manga_covers/master_feung_cover_burnout.png` | ✅ 4 pages | [ ] approve  [ ] reject  [ ] needs_fix |
| `sai_ma` | ✅ `brand-wizard-app/public/teacher_pics/sai_ma.png` | ✅ `brand-wizard-app/public/assets/audio/audiobook_chapters/sai_ma_grief_ch1.mp3` | ✅ `brand-wizard-app/public/assets/audio/showcase/sai_ma_boundaries_hook.mp3` | ✅ `brand-wizard-app/public/assets/audio/podcast/sai_ma_podcast_3min.mp3` | ✅ `brand-wizard-app/public/assets/video/teacher_reels/sai_ma_reel.mp4` | ❌ MISSING | ✅ `brand-wizard-app/public/assets/manga_covers/sai_ma_cover_grief.png` | ✅ 4 pages | [ ] approve  [ ] reject  [ ] needs_fix |
| `ra` | ✅ `brand-wizard-app/public/teacher_pics/ra.png` | ✅ `brand-wizard-app/public/assets/audio/audiobook_chapters/ra_self_worth_ch1.mp3` | ✅ `brand-wizard-app/public/assets/audio/showcase/ra_self_worth_hook.mp3` | ✅ `brand-wizard-app/public/assets/audio/podcast/ra_podcast_3min.mp3` | ✅ `brand-wizard-app/public/assets/video/teacher_reels/ra_reel.mp4` | ❌ MISSING | ✅ `brand-wizard-app/public/assets/manga_covers/ra_cover_self_worth.png` | ✅ 4 pages | [ ] approve  [ ] reject  [ ] needs_fix |
| `junko` | ✅ `brand-wizard-app/public/teacher_pics/junko.png` | ✅ `brand-wizard-app/public/assets/audio/audiobook_chapters/junko_overthinking_ch1.mp3` | ✅ `brand-wizard-app/public/assets/audio/showcase/junko_imposter_syndrome_hook.mp3` | ✅ `brand-wizard-app/public/assets/audio/podcast/junko_podcast_3min.mp3` | ❌ MISSING | ❌ MISSING | ✅ `brand-wizard-app/public/assets/manga_covers/junko_cover_mindfulness.png` | ✅ 4 pages | [ ] approve  [ ] reject  [ ] needs_fix |
| `miki` | ✅ `brand-wizard-app/public/teacher_pics/miki.png` | ✅ `brand-wizard-app/public/assets/audio/audiobook_chapters/miki_imposter_syndrome_ch1.mp3` | ✅ `brand-wizard-app/public/assets/audio/showcase/miki_compassion_fatigue_hook.mp3` | ✅ `brand-wizard-app/public/assets/audio/podcast/miki_podcast_3min.mp3` | ❌ MISSING | ❌ MISSING | ✅ `brand-wizard-app/public/assets/manga_covers/miki_cover_imposter_syndrome.png` | ✅ 4 pages | [ ] approve  [ ] reject  [ ] needs_fix |
| `master_wu` | ✅ `brand-wizard-app/public/teacher_pics/master_wu.png` | ✅ `brand-wizard-app/public/assets/audio/audiobook_chapters/master_wu_courage_ch1.mp3` | ✅ `brand-wizard-app/public/assets/audio/showcase/master_wu_self_worth_hook.mp3` | ✅ `brand-wizard-app/public/assets/audio/podcast/master_wu_podcast_3min.mp3` | ✅ `brand-wizard-app/public/assets/video/teacher_reels/wu_reel.mp4` | ❌ MISSING | ✅ `brand-wizard-app/public/assets/manga_covers/master_wu_cover_burnout.png` | ✅ 4 pages | [ ] approve  [ ] reject  [ ] needs_fix |
| `pamela_fellows` | ✅ `brand-wizard-app/public/teacher_pics/pamela_fellows.png` | ✅ `brand-wizard-app/public/assets/audio/audiobook_chapters/pamela_fellows_burnout_ch1.mp3` | ✅ `brand-wizard-app/public/assets/audio/showcase/pamela_fellows_burnout_hook.mp3` | ✅ `brand-wizard-app/public/assets/audio/podcast/pamela_fellows_podcast_3min.mp3` | ❌ MISSING | ❌ MISSING | ✅ `brand-wizard-app/public/assets/manga_covers/pamela_fellows_cover_burnout.png` | ✅ 4 pages | [ ] approve  [ ] reject  [ ] needs_fix |
| `joshin` | ✅ `brand-wizard-app/public/teacher_pics/joshin.png` | ✅ `brand-wizard-app/public/assets/audio/audiobook_chapters/joshin_anxiety_ch1.mp3` | ✅ `brand-wizard-app/public/assets/audio/showcase/joshin_sleep_anxiety_hook.mp3` | ✅ `brand-wizard-app/public/assets/audio/podcast/joshin_podcast_3min.mp3` | ❌ MISSING | ❌ MISSING | ✅ `brand-wizard-app/public/assets/manga_covers/joshin_cover_anxiety.png` | ✅ 4 pages | [ ] approve  [ ] reject  [ ] needs_fix |
| `maat` | ✅ `brand-wizard-app/public/teacher_pics/maat.png` | ✅ `brand-wizard-app/public/assets/audio/audiobook_chapters/maat_boundaries_ch1.mp3` | ✅ `brand-wizard-app/public/assets/audio/showcase/maat_courage_hook.mp3` | ✅ `brand-wizard-app/public/assets/audio/podcast/maat_podcast_3min.mp3` | ❌ MISSING | ❌ MISSING | ❌ MISSING | ✅ 4 pages | [ ] approve  [ ] reject  [ ] needs_fix |
| `omote` | ✅ `brand-wizard-app/public/teacher_pics/omote.png` | ✅ `brand-wizard-app/public/assets/audio/audiobook_chapters/omote_sleep_anxiety_ch1.mp3` | ✅ `brand-wizard-app/public/assets/audio/showcase/omote_imposter_syndrome_hook.mp3` | ✅ `brand-wizard-app/public/assets/audio/podcast/omote_podcast_3min.mp3` | ❌ MISSING | ❌ MISSING | ✅ `brand-wizard-app/public/assets/manga_covers/omote_cover_sleep_anxiety.png` | ✅ 4 pages | [ ] approve  [ ] reject  [ ] needs_fix |
| `master_sha` | ✅ `brand-wizard-app/public/teacher_pics/master_sha.png` | ✅ `brand-wizard-app/public/assets/audio/audiobook_chapters/master_sha_grief_ch1.mp3` | ✅ `brand-wizard-app/public/assets/audio/showcase/master_sha_anxiety_hook.mp3` | ✅ `brand-wizard-app/public/assets/audio/podcast/master_sha_podcast_3min.mp3` | ❌ MISSING | ❌ MISSING | ✅ `brand-wizard-app/public/assets/manga_covers/master_sha_cover_grief.png` | ✅ 4 pages | [ ] approve  [ ] reject  [ ] needs_fix |

### §3.1 — Aggregate gaps

- **YouTube videos:** 13 of 13 teachers missing — `assets/video/youtube/` dir absent on disk
- **Video reels:** 8 of 13 teachers missing reels in `assets/video/teacher_reels/`
- **Locale page variants:** only en_US fully wired today; ja_JP / zh_TW / zh_CN page versions are TBD downstream of this catalog

### §3.2 — Manual QA pass instructions

For each teacher row above:
1. Open the page locally: `cd brand-wizard-app && npm run dev` (or open the HTML file directly).
2. Scroll to `#{teacher_slug}` section.
3. Click each format card's play/pause control; verify audio plays.
4. Click each format card's cover; verify it opens / loads.
5. Mark approve / reject / needs_fix in the table column.

---

## §4 — Image / audio asset QA matrix

Same data as §3 with explicit reviewer slots per asset (not per teacher). Use this when doing a focused asset-by-asset pass.

### §4.1 — Portrait

| Teacher | Path | Reviewer mark |
|---|---|---|
| `ahjan` | `brand-wizard-app/public/teacher_pics/ahjan.png` | [ ] approve  [ ] reject  [ ] needs_fix |
| `adi_da` | `brand-wizard-app/public/teacher_pics/adi_da.png` | [ ] approve  [ ] reject  [ ] needs_fix |
| `master_feung` | `brand-wizard-app/public/teacher_pics/master_feung.png` | [ ] approve  [ ] reject  [ ] needs_fix |
| `sai_ma` | `brand-wizard-app/public/teacher_pics/sai_ma.png` | [ ] approve  [ ] reject  [ ] needs_fix |
| `ra` | `brand-wizard-app/public/teacher_pics/ra.png` | [ ] approve  [ ] reject  [ ] needs_fix |
| `junko` | `brand-wizard-app/public/teacher_pics/junko.png` | [ ] approve  [ ] reject  [ ] needs_fix |
| `miki` | `brand-wizard-app/public/teacher_pics/miki.png` | [ ] approve  [ ] reject  [ ] needs_fix |
| `master_wu` | `brand-wizard-app/public/teacher_pics/master_wu.png` | [ ] approve  [ ] reject  [ ] needs_fix |
| `pamela_fellows` | `brand-wizard-app/public/teacher_pics/pamela_fellows.png` | [ ] approve  [ ] reject  [ ] needs_fix |
| `joshin` | `brand-wizard-app/public/teacher_pics/joshin.png` | [ ] approve  [ ] reject  [ ] needs_fix |
| `maat` | `brand-wizard-app/public/teacher_pics/maat.png` | [ ] approve  [ ] reject  [ ] needs_fix |
| `omote` | `brand-wizard-app/public/teacher_pics/omote.png` | [ ] approve  [ ] reject  [ ] needs_fix |
| `master_sha` | `brand-wizard-app/public/teacher_pics/master_sha.png` | [ ] approve  [ ] reject  [ ] needs_fix |

### §4.2 — Audiobook Ch1

| Teacher | Path | Reviewer mark |
|---|---|---|
| `ahjan` | `brand-wizard-app/public/assets/audio/audiobook_chapters/ahjan_anxiety_ch1.mp3` | [ ] approve  [ ] reject  [ ] needs_fix |
| `adi_da` | `brand-wizard-app/public/assets/audio/audiobook_chapters/adi_da_self_worth_ch1.mp3` | [ ] approve  [ ] reject  [ ] needs_fix |
| `master_feung` | `brand-wizard-app/public/assets/audio/audiobook_chapters/master_feung_burnout_ch1.mp3` | [ ] approve  [ ] reject  [ ] needs_fix |
| `sai_ma` | `brand-wizard-app/public/assets/audio/audiobook_chapters/sai_ma_grief_ch1.mp3` | [ ] approve  [ ] reject  [ ] needs_fix |
| `ra` | `brand-wizard-app/public/assets/audio/audiobook_chapters/ra_self_worth_ch1.mp3` | [ ] approve  [ ] reject  [ ] needs_fix |
| `junko` | `brand-wizard-app/public/assets/audio/audiobook_chapters/junko_overthinking_ch1.mp3` | [ ] approve  [ ] reject  [ ] needs_fix |
| `miki` | `brand-wizard-app/public/assets/audio/audiobook_chapters/miki_imposter_syndrome_ch1.mp3` | [ ] approve  [ ] reject  [ ] needs_fix |
| `master_wu` | `brand-wizard-app/public/assets/audio/audiobook_chapters/master_wu_courage_ch1.mp3` | [ ] approve  [ ] reject  [ ] needs_fix |
| `pamela_fellows` | `brand-wizard-app/public/assets/audio/audiobook_chapters/pamela_fellows_burnout_ch1.mp3` | [ ] approve  [ ] reject  [ ] needs_fix |
| `joshin` | `brand-wizard-app/public/assets/audio/audiobook_chapters/joshin_anxiety_ch1.mp3` | [ ] approve  [ ] reject  [ ] needs_fix |
| `maat` | `brand-wizard-app/public/assets/audio/audiobook_chapters/maat_boundaries_ch1.mp3` | [ ] approve  [ ] reject  [ ] needs_fix |
| `omote` | `brand-wizard-app/public/assets/audio/audiobook_chapters/omote_sleep_anxiety_ch1.mp3` | [ ] approve  [ ] reject  [ ] needs_fix |
| `master_sha` | `brand-wizard-app/public/assets/audio/audiobook_chapters/master_sha_grief_ch1.mp3` | [ ] approve  [ ] reject  [ ] needs_fix |

### §4.3 — Showcase Hook

| Teacher | Path | Reviewer mark |
|---|---|---|
| `ahjan` | `brand-wizard-app/public/assets/audio/showcase/ahjan_depression_hook.mp3` | [ ] approve  [ ] reject  [ ] needs_fix |
| `adi_da` | `brand-wizard-app/public/assets/audio/showcase/adi_da_depression_hook.mp3` | [ ] approve  [ ] reject  [ ] needs_fix |
| `master_feung` | `brand-wizard-app/public/assets/audio/showcase/master_feung_self_worth_hook.mp3` | [ ] approve  [ ] reject  [ ] needs_fix |
| `sai_ma` | `brand-wizard-app/public/assets/audio/showcase/sai_ma_boundaries_hook.mp3` | [ ] approve  [ ] reject  [ ] needs_fix |
| `ra` | `brand-wizard-app/public/assets/audio/showcase/ra_self_worth_hook.mp3` | [ ] approve  [ ] reject  [ ] needs_fix |
| `junko` | `brand-wizard-app/public/assets/audio/showcase/junko_imposter_syndrome_hook.mp3` | [ ] approve  [ ] reject  [ ] needs_fix |
| `miki` | `brand-wizard-app/public/assets/audio/showcase/miki_compassion_fatigue_hook.mp3` | [ ] approve  [ ] reject  [ ] needs_fix |
| `master_wu` | `brand-wizard-app/public/assets/audio/showcase/master_wu_self_worth_hook.mp3` | [ ] approve  [ ] reject  [ ] needs_fix |
| `pamela_fellows` | `brand-wizard-app/public/assets/audio/showcase/pamela_fellows_burnout_hook.mp3` | [ ] approve  [ ] reject  [ ] needs_fix |
| `joshin` | `brand-wizard-app/public/assets/audio/showcase/joshin_sleep_anxiety_hook.mp3` | [ ] approve  [ ] reject  [ ] needs_fix |
| `maat` | `brand-wizard-app/public/assets/audio/showcase/maat_courage_hook.mp3` | [ ] approve  [ ] reject  [ ] needs_fix |
| `omote` | `brand-wizard-app/public/assets/audio/showcase/omote_imposter_syndrome_hook.mp3` | [ ] approve  [ ] reject  [ ] needs_fix |
| `master_sha` | `brand-wizard-app/public/assets/audio/showcase/master_sha_anxiety_hook.mp3` | [ ] approve  [ ] reject  [ ] needs_fix |

### §4.4 — Podcast 3min

| Teacher | Path | Reviewer mark |
|---|---|---|
| `ahjan` | `brand-wizard-app/public/assets/audio/podcast/ahjan_podcast_3min.mp3` | [ ] approve  [ ] reject  [ ] needs_fix |
| `adi_da` | `brand-wizard-app/public/assets/audio/podcast/adi_da_podcast_3min.mp3` | [ ] approve  [ ] reject  [ ] needs_fix |
| `master_feung` | `brand-wizard-app/public/assets/audio/podcast/master_feung_podcast_3min.mp3` | [ ] approve  [ ] reject  [ ] needs_fix |
| `sai_ma` | `brand-wizard-app/public/assets/audio/podcast/sai_ma_podcast_3min.mp3` | [ ] approve  [ ] reject  [ ] needs_fix |
| `ra` | `brand-wizard-app/public/assets/audio/podcast/ra_podcast_3min.mp3` | [ ] approve  [ ] reject  [ ] needs_fix |
| `junko` | `brand-wizard-app/public/assets/audio/podcast/junko_podcast_3min.mp3` | [ ] approve  [ ] reject  [ ] needs_fix |
| `miki` | `brand-wizard-app/public/assets/audio/podcast/miki_podcast_3min.mp3` | [ ] approve  [ ] reject  [ ] needs_fix |
| `master_wu` | `brand-wizard-app/public/assets/audio/podcast/master_wu_podcast_3min.mp3` | [ ] approve  [ ] reject  [ ] needs_fix |
| `pamela_fellows` | `brand-wizard-app/public/assets/audio/podcast/pamela_fellows_podcast_3min.mp3` | [ ] approve  [ ] reject  [ ] needs_fix |
| `joshin` | `brand-wizard-app/public/assets/audio/podcast/joshin_podcast_3min.mp3` | [ ] approve  [ ] reject  [ ] needs_fix |
| `maat` | `brand-wizard-app/public/assets/audio/podcast/maat_podcast_3min.mp3` | [ ] approve  [ ] reject  [ ] needs_fix |
| `omote` | `brand-wizard-app/public/assets/audio/podcast/omote_podcast_3min.mp3` | [ ] approve  [ ] reject  [ ] needs_fix |
| `master_sha` | `brand-wizard-app/public/assets/audio/podcast/master_sha_podcast_3min.mp3` | [ ] approve  [ ] reject  [ ] needs_fix |

### §4.5 — Video Reel

| Teacher | Path | Reviewer mark |
|---|---|---|
| `ahjan` | `brand-wizard-app/public/assets/video/teacher_reels/ahjan_reel.mp4` | [ ] approve  [ ] reject  [ ] needs_fix |
| `adi_da` | `brand-wizard-app/public/assets/video/teacher_reels/adi_da_reel.mp4` | [ ] approve  [ ] reject  [ ] needs_fix |
| `master_feung` | ❌ **MISSING** | [ ] approve  [ ] reject  [ ] needs_fix |
| `sai_ma` | `brand-wizard-app/public/assets/video/teacher_reels/sai_ma_reel.mp4` | [ ] approve  [ ] reject  [ ] needs_fix |
| `ra` | `brand-wizard-app/public/assets/video/teacher_reels/ra_reel.mp4` | [ ] approve  [ ] reject  [ ] needs_fix |
| `junko` | ❌ **MISSING** | [ ] approve  [ ] reject  [ ] needs_fix |
| `miki` | ❌ **MISSING** | [ ] approve  [ ] reject  [ ] needs_fix |
| `master_wu` | `brand-wizard-app/public/assets/video/teacher_reels/wu_reel.mp4` | [ ] approve  [ ] reject  [ ] needs_fix |
| `pamela_fellows` | ❌ **MISSING** | [ ] approve  [ ] reject  [ ] needs_fix |
| `joshin` | ❌ **MISSING** | [ ] approve  [ ] reject  [ ] needs_fix |
| `maat` | ❌ **MISSING** | [ ] approve  [ ] reject  [ ] needs_fix |
| `omote` | ❌ **MISSING** | [ ] approve  [ ] reject  [ ] needs_fix |
| `master_sha` | ❌ **MISSING** | [ ] approve  [ ] reject  [ ] needs_fix |

### §4.6 — YouTube

| Teacher | Path | Reviewer mark |
|---|---|---|
| `ahjan` | ❌ **MISSING** | [ ] approve  [ ] reject  [ ] needs_fix |
| `adi_da` | ❌ **MISSING** | [ ] approve  [ ] reject  [ ] needs_fix |
| `master_feung` | ❌ **MISSING** | [ ] approve  [ ] reject  [ ] needs_fix |
| `sai_ma` | ❌ **MISSING** | [ ] approve  [ ] reject  [ ] needs_fix |
| `ra` | ❌ **MISSING** | [ ] approve  [ ] reject  [ ] needs_fix |
| `junko` | ❌ **MISSING** | [ ] approve  [ ] reject  [ ] needs_fix |
| `miki` | ❌ **MISSING** | [ ] approve  [ ] reject  [ ] needs_fix |
| `master_wu` | ❌ **MISSING** | [ ] approve  [ ] reject  [ ] needs_fix |
| `pamela_fellows` | ❌ **MISSING** | [ ] approve  [ ] reject  [ ] needs_fix |
| `joshin` | ❌ **MISSING** | [ ] approve  [ ] reject  [ ] needs_fix |
| `maat` | ❌ **MISSING** | [ ] approve  [ ] reject  [ ] needs_fix |
| `omote` | ❌ **MISSING** | [ ] approve  [ ] reject  [ ] needs_fix |
| `master_sha` | ❌ **MISSING** | [ ] approve  [ ] reject  [ ] needs_fix |

### §4.7 — Manga Cover

| Teacher | Path | Reviewer mark |
|---|---|---|
| `ahjan` | `brand-wizard-app/public/assets/manga_covers/ahjan_cover_anxiety.png` | [ ] approve  [ ] reject  [ ] needs_fix |
| `adi_da` | `brand-wizard-app/public/assets/manga_covers/adi_da_cover_self_worth.png` | [ ] approve  [ ] reject  [ ] needs_fix |
| `master_feung` | `brand-wizard-app/public/assets/manga_covers/master_feung_cover_burnout.png` | [ ] approve  [ ] reject  [ ] needs_fix |
| `sai_ma` | `brand-wizard-app/public/assets/manga_covers/sai_ma_cover_grief.png` | [ ] approve  [ ] reject  [ ] needs_fix |
| `ra` | `brand-wizard-app/public/assets/manga_covers/ra_cover_self_worth.png` | [ ] approve  [ ] reject  [ ] needs_fix |
| `junko` | `brand-wizard-app/public/assets/manga_covers/junko_cover_mindfulness.png` | [ ] approve  [ ] reject  [ ] needs_fix |
| `miki` | `brand-wizard-app/public/assets/manga_covers/miki_cover_imposter_syndrome.png` | [ ] approve  [ ] reject  [ ] needs_fix |
| `master_wu` | `brand-wizard-app/public/assets/manga_covers/master_wu_cover_burnout.png` | [ ] approve  [ ] reject  [ ] needs_fix |
| `pamela_fellows` | `brand-wizard-app/public/assets/manga_covers/pamela_fellows_cover_burnout.png` | [ ] approve  [ ] reject  [ ] needs_fix |
| `joshin` | `brand-wizard-app/public/assets/manga_covers/joshin_cover_anxiety.png` | [ ] approve  [ ] reject  [ ] needs_fix |
| `maat` | ❌ **MISSING** | [ ] approve  [ ] reject  [ ] needs_fix |
| `omote` | `brand-wizard-app/public/assets/manga_covers/omote_cover_sleep_anxiety.png` | [ ] approve  [ ] reject  [ ] needs_fix |
| `master_sha` | `brand-wizard-app/public/assets/manga_covers/master_sha_cover_grief.png` | [ ] approve  [ ] reject  [ ] needs_fix |

---

## §5 — CTA placeholder replacement list

These anchors in [`teacher_showcase.html`](brand-wizard-app/public/teacher_showcase.html) are placeholders. Operator: provide real URLs to replace each.

| Anchor | Teacher | Real URL (operator fills) | Notes |
|---|---|---|---|
| `#audio-adi_da` | `adi_da` |  |  |
| `#audio-ahjan` | `ahjan` |  |  |
| `#audio-joshin` | `joshin` |  |  |
| `#audio-junko` | `junko` |  |  |
| `#audio-maat` | `maat` |  |  |
| `#audio-master_feung` | `master_feung` |  |  |
| `#audio-master_sha` | `master_sha` |  |  |
| `#audio-master_wu` | `master_wu` |  |  |
| `#audio-miki` | `miki` |  |  |
| `#audio-omote` | `omote` |  |  |
| `#audio-pamela_fellows` | `pamela_fellows` |  |  |
| `#audio-ra` | `ra` |  |  |
| `#audio-sai_ma` | `sai_ma` |  |  |
| `#book-adi_da` | `adi_da` |  |  |
| `#book-ahjan` | `ahjan` |  |  |
| `#book-joshin` | `joshin` |  |  |
| `#book-junko` | `junko` |  |  |
| `#book-maat` | `maat` |  |  |
| `#book-master_feung` | `master_feung` |  |  |
| `#book-master_sha` | `master_sha` |  |  |
| `#book-master_wu` | `master_wu` |  |  |
| `#book-miki` | `miki` |  |  |
| `#book-omote` | `omote` |  |  |
| `#book-pamela_fellows` | `pamela_fellows` |  |  |
| `#book-ra` | `ra` |  |  |
| `#book-sai_ma` | `sai_ma` |  |  |

**Total CTA placeholders:** 26

### §5.1 — Suggested URL targets per CTA kind

| CTA prefix | Suggested target | Notes |
|---|---|---|
| `#book-{teacher}` | Amazon KDP / Apple Books / storefront link to teacher's flagship book | If multiple titles per teacher, pick the highest-composite-score Pearl Prime entry from §1 |
| `#audio-{teacher}` | Audible / Spotify / podcast platform URL | Or in-page anchor to the audio player block if no external URL yet |
| `#guide-{teacher}` | (Not currently in HTML) — would point at `/free/{slug}` freebie | Operator to confirm whether this CTA kind is needed at all |

---

## §6 — Snapshot summary

**Catalog readiness (from `launch_baseline_data.json`):**

- Pearl Prime listing-ready: 8,244
- Pearl Prime blocked_score (zh_TW only): 160
- Manga ready: 727
- Manga awaiting manual image QA: 153

**Top 50 split:**

- by lane: {'manga': 5, 'book_script': 45}
- by locale: {'ja_JP': 20, 'en_US': 22, 'zh_TW': 4, 'zh_CN': 4}

---

## §7 — Stop / next

After reviewing this packet:
- Pick the 10–20 launch set from §1 / §2.
- Send back §3 / §4 with reviewer marks.
- Send back §5 with real URLs.

Catalog system is sealed. No further engineering required from this packet.