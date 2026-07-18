# V1.2 Themes Summary — zh_CN × Cluster A (Anxiety/Somatic/Sleep)

**Locale:** zh_CN (Simplified Chinese, mainland-natural)
**Cluster:** A — Anxiety / Somatic / Sleep
**Total series:** 25 (5 brands × 5 series)
**Authoring date:** 2026-05-11
**Author:** Pearl_Writer (Claude Opus 4.7 / 1M, Tier-1 operator-present)
**Branch:** `agent/v1-2-cluster-a-zh-cn-retry-20260512`
**YAML data file:** `artifacts/marketing/v1_2_themes_zh_CN_cluster_a.yaml`
**Authority chain:**
- `artifacts/research/v1_2_genre_allocation_constraint_2026-05-12.md` (binding)
- `artifacts/research/manga_bestseller_magical_serial_framework_2026-05-12.md`
- `artifacts/research/manga_genz_genalpha_portal_framework_2026-05-13.md`
- `artifacts/marketing/v1_2_themes_en_US_cluster_a.yaml` (structural template — localized to zh_CN, not translated)
- `config/manga/canonical_brand_list.yaml`

## Genre family allocation — validation gate

| genre_family | count | target (per cluster) | within_range |
|---|---|---|---|
| healing | 6 | 6 | yes |
| slice_of_life | 5 | 5 | yes |
| supernatural_everyday | 4 | 4-5 | yes |
| mystery_cozy | 4 | 4 | yes |
| fantasy_adventure | 3 | 3 | yes |
| romance | 1 | 1-2 | yes |
| horror | 1 | 1 | yes |
| school | 1 | 0-1 | yes |
| other | 0 | 0-1 | yes |
| **TOTAL** | **25** | **25** | **yes** |

All rows within range. Cluster passes constraint gate.

## Reading-platform allocation

| platform | count | share | target guidance |
|---|---|---|---|
| webtoon_vertical | 15 | 60% | ~70% (Kuaikan / Bilibili Comics dominance) |
| manga_traditional | 10 | 40% | ~30% |

Note: at 60/40 the cluster sits one notch below the 70/30 mainland tilt guidance.
Three `manga_traditional` slots are intentionally retained for the longer-arc /
older-audience books (Brand 5 vol_1 `yu_huo_ke_zhan`, Brand 4 vol_1 `shou_fen_lv_dian`,
Brand 1 vol_5 `zhou_ri_xiao_qu_yao_pu`) because their reading register is closer
to traditional manga pacing (long establishing panels, no vertical-scroll cadence).
Cluster B and Cluster C can pull cluster-wide toward 70/30 by going webtoon-heavier.

## Persona archetype allocation

| persona | count | share | target guidance |
|---|---|---|---|
| GZ-firstjob | 9 | 36% | Gen Z bucket ~55% |
| GZ-uni | 5 | 20% | (Gen Z subtotal: 14 / 56%) |
| M-newparent | 8 | 32% | Millennial ~30% |
| GA-middle | 3 | 12% | Gen Alpha ~30% (lifted by Cluster E) |

Gen Z (GZ-*) totals **56% (14/25)** — on target for the ~55% mainland tilt.
Millennial **32%** — slightly above ~30% target, acceptable given Cluster A's
postpartum / mid-career anxiety subject matter pulls Millennial weight.
Gen Alpha **12%** — under the 30% locale target; Clusters D/E carry the
Gen Alpha quota. No Gen X in this cluster (target ~3% absorbed by other clusters).

## Magical-register allocation

| register | count | share | target guidance |
|---|---|---|---|
| supernatural_everyday | 9 | 36% | ~37% |
| magical_realism | 9 | 36% | ~28% |
| soft_fantasy | 3 | 12% | ~8% |
| occult_cosmic | 1 | 4% | ~2% |
| none | 3 | 12% | ~19% |

Slightly heavier on `magical_realism` (book/bowl/ledger as portal) because zh_CN's
Cluster A leans into object-mediated emotion (the writing-implement / craft-object
tradition); slightly lighter on `none` because mainland anxiety/somatic content benefits
from the magical-register softening for content-compliance and palatability. Within
advisory variance.

## Serial-engine allocation

| serial_engine | count | share |
|---|---|---|
| case_of_the_week | 15 | 60% |
| slice_of_life_arc | 8 | 32% |
| serialized_long_arc | 2 | 8% |

Healthy weekly-episode floor; two serialized long-arcs (Brand 4 `shen_ti_zhi_tu_shi`,
Brand 5 `wen_xin_zhong_xue_xin_sheng_ji`) for binge/spine readers.

## Volume runway

- **Median:** 180 volumes
- **Min:** 140 (Brand 1 vol_3, Brand 3 vol_4)
- **Max:** 220 (Brand 4 vol_3, Brand 5 vol_4)
- All series ≥ 140 volumes — clears the V1.2 minimum runway floor.

## Emotional engines used (top 5)

`competent_calm_specialist` (12) · `ritual_keeper` (9) · `chosen_family` (10) ·
`named_and_claimed` (6) · `ledger_atonement` (4) · `future_self_mentor` (3) ·
`mentor_apprentice` (3)

(Counts overlap because most series use compound engines, e.g.
`competent_calm_specialist + chosen_family`.)

## Mainland-locale (zh_CN) linguistic confirmation

- **Zero Taiwan phrasing in content body.** `grep` over the YAML for
  `視頻|軟體|智慧型|網路|捷運|計程車|麵店|裡|為何|資料|資訊|機車` returns only matches
  inside the file's own commented anti-Taiwan guidance block (lines 27-28).
  All free-text Chinese fields use mainland Simplified Chinese vocabulary:
  视频, 软件, 智能手机, 互联网, 地铁, 出租车, 早高峰, 高铁, 共享单车, 直播, 小红书,
  抖音, 微信, 外卖, 小区, 城中村, 老破小, 高考, 期中考, 网课, 等。
- **Cultural anchors used across the 25 series:** 上海郊区便利店, 城中村, 老破小,
  小区花园, 北京胡同, 朝阳合租房, 早高峰, 高铁返乡, 城中村, 春运/春节, 抖音/小红书直播,
  人民公园相亲角, 茶馆, 京剧, 三甲医院, 地铁夜班, 深圳南山普拉提工作室, 重庆山城老巷,
  长沙老社区小推拿店, 南京老档案馆, 杭州西郊徽派民宿, 成都老社区, 武汉某大学地理系,
  广州国际医院, 浙江某大学心理咨询中心, 西安出版社, 上海三甲急诊科, 重庆江北攀岩馆。
- **Comp_titles intentionally include mainland-released originals + JP/KR
  imports available on Bilibili Comics / Kuaikan:** 一人之下, 罗小黑战记, 镖人,
  我们这一天 (CN-licensed), 千与千寻 (CN-released), 你的名字 (CN-released),
  深夜食堂 (CN-popular), 解忧杂货店 (东野圭吾 CN ed.), 哆啦A梦 (CN-popular),
  哈利波特 (CN ed.), 凪的新生活 (CN-popular), 声音的形状 (CN-released),
  孤独的美食家 (CN-popular), 心灵奇旅 (CN-released), 排球少年 (CN-popular),
  总之就是非常可爱 (CN-licensed). No Western-only or HK-political comp titles.

## Content compliance check (politically sensitive content)

All 25 series pass the no-politics screen:

- **No Taiwan / Hong Kong political content.** Where the city of Hong Kong or
  Taiwan would appear as a setting, the cluster uses mainland-only settings
  (上海, 北京, 深圳, 重庆, 杭州, 南京, 成都, 武汉, 长沙, 广州, 西安, 浙江, 江苏, 山东,
  陕西, 新疆乌鲁木齐, 江西, 长春, 天津, 广东).
- **No Tibet / Xinjiang as politically-charged settings.** One Gen Alpha character
  (Brand 5 vol_4) is described as a 10-year-old missing his parents who work in
  Urumqi — frame is family-migrant-labor, not ethnic or political.
- **No national leadership, ideology, religion, or military topics.**
- **No depictions of state-medical-system criticism.** Hospital settings
  (三甲医院 in Brand 2, Brand 4, Brand 5) frame the doctor protagonists positively
  and individualistically. Burnout is shown as the *individual's* burden, not as a
  systemic critique.
- **No depictions of school-system criticism.** School settings (Brand 5 `wen_xin`,
  Brand 1 `xiao_zhang_ben`, Brand 3 `cheng_ji_huo_xi_shi`) frame the protagonist's
  experience individually, not as critique of 高考 or education policy.
- **Magical-register framing helps abstract sensitive emotional content** (惊恐发作,
  失眠, 创伤记忆) into culturally palatable supernatural-everyday / magical-realism
  / soft-fantasy modes — these registers carry better through the mainland
  content review framework than direct clinical-realist framings.
- **Wellness, therapy, anxiety, family, career, body, intergenerational care, and
  recovery topics are all retained** — these are mainland-publishable wellness
  content in line with the surge in 小红书/抖音 mental-health vertical content.

## Tone confirmation

- 『一人之下』 grounded-supernatural register: applied to brands 1, 2 (sleep tales),
  4 (scars / phantom limbs), 5 (translator / guild).
- 『罗小黑战记』 contemporary-yokai register: applied to brands 1 (3AM aisle), 3
  (pilates spirits), 5 (Gen Alpha guild).
- 『镖人』 emotional-restraint register: applied to brands 4 (memory archive,
  guesthouse, hair memory), 5 (24-hour innkeeper, stabilizer journal).
- No preachy / advice / lecture register anywhere. Wellness content is delivered
  through *action / object / ritual* rather than dialogue or moral lesson.

## Brand-by-brand series titles (audit-friendly)

**Brand 1 — stillness_press (5)**
- 凌晨三点的货架
- 口袋里的小账本
- 她看得见
- 易筱最后一次惊恐发作
- 周日小区药铺

**Brand 2 — sleep_restoration_iyashikei (5)**
- 助眠直播间
- 月球睡眠诊所
- 睡眠调度员
- 夜厨房
- 替别人做梦

**Brand 3 — somatic_wisdom_shojo (5)**
- 普拉提教练的小妖
- 身体信件档案
- 邻里推拿
- 给重度上网者的呼吸课
- 攀岩馆的身体记忆课

**Brand 4 — body_memory_shojo (5)**
- 守分律店
- 疤在唱
- 身体制图师
- 幻肢
- 手的记忆

**Brand 5 — stabilizer_healing (5)**
- 余火客栈
- 惊恐翻译官
- 稳定者日志
- 急救冒险者公会
- 稳心中学新生记

## Out-of-scope confirmation

- en_US / ja_JP / zh_TW Cluster A files NOT touched.
- Other-cluster (B, C, D, E) files NOT touched.
- `canonical_brand_list.yaml` NOT touched.
- Allocation constraint doc NOT touched.
- `audit_llm_callers.py` clean (no new LLM calls anywhere in this PR — only YAML + MD authoring).
- Zero file deletions in this PR.
- Tier-1 Claude authoring permitted (operator-present, prose generation).
- File count in PR: 2 (1 YAML + 1 MD).
