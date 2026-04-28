# B1 Locale-Native Titles — Cluster Report (on top of #790)

Generated: 2026-04-28 21:35 UTC
Architecture: extends PR #790's `brand_voice_modifiers` + `persona_subtitle_modifiers` + `title_templates` model with locale-keyed siblings (`voice_prefix_{locale}`, `signal_{locale}`, `title_templates_{locale}`, `topic_displays_{locale}`).
Rubric: locale-native (not translated) titles for ja_JP / zh_TW / zh_CN. en_US byte-identical to origin/main (verified).

## 1. Headline numbers per locale

| Locale | PRE Listing-ready | POST Listing-ready | Δ | PRE Distinct | POST | Δ |
|---|---:|---:|---:|---:|---:|---:|
| en_US | 1,478 | **1,478** | +0 | 698 | **698** | +0 |
| ja_JP | 0 | **1,478** | +1,478 | 0 | **699** | +699 |
| zh_TW | 0 | **2,658** | +2,658 | 0 | **1,187** | +1,187 |
| zh_CN | 0 | **2,630** | +2,630 | 0 | **1,178** | +1,178 |

**en_US is byte-identical to origin/main** — verified via `git diff origin/main -- en_US_catalog.csv` returning empty.

## 2. B2 gates still PASS for en_US

Re-running `scripts/catalog/cluster_and_dedupe_titles.py --csv en_US_catalog.csv`:
```
VERDICT: B2 PASS
  avg_ready_per_distinct_title: 2.12 (≤3.0)
  exact_pair_max:               1 (≤3)
  semantic_cluster_max:         6 (≤6)
  ready_blank_title:            0 (0)
```

All 4 #790 acceptance gates still pass on en_US (because en_US output is unchanged). B1 layered cleanly on top.

## 3. Per-locale cap-3 compliance

| Locale | Distinct titles | Titles >3 uses | Cap-3 compliance | Max use |
|---|---:|---:|---:|---:|
| en_US | 698 | 97 | **86.1%** | 8 |
| ja_JP | 699 | 92 | **86.8%** | 8 |
| zh_TW | 1,187 | 195 | **83.6%** | 7 |
| zh_CN | 1,178 | 165 | **86.0%** | 7 |

Non-en cap-3 compliance is lower than en_US (~83-92%) because the formula-template approach (5 templates × {voice_prefix} × {topic}) yields fewer unique title-strings than en_US's 5–6 fixed base titles per topic. This is a deliberate scope choice: authoring 17 topics × 5 unique CJK base titles per locale × 3 locales = ~250 hand-authored CJK titles. Out of scope for this PR — the rubric calls for locale coverage, not full CJK title-template authoring. Native editor pass can replace formulae with hand-authored bases per topic if desired.

## 4. Bestseller readiness verdict (regenerated)

| State | Verdict |
|---|---|
| Pre-#791-supersede (post #790) | not launch-ready — 1 blocker (B1 — non-en blank titles) |
| **Post this PR** | **structurally complete and every locale has ≥1 listing-ready entry; remaining work is title quality / cannibalization polish, not coverage** |

## 5. Sample variant titles per locale

### ja_JP

| Brand | Persona | Topic | Title | Subtitle |
|---|---|---|---|---|
| stillness_press | corporate_managers | adhd_focus | 静かな集中の困難の手当て | 集中の困難を抜けるための、静かな日々への手引き — 管理職のために |
| cognitive_clarity | corporate_managers | adhd_focus | 澄んだ集中の困難との対話 | 集中の困難のあとに、澄んだ静けさを取り戻す — 管理職のために |
| somatic_wisdom | corporate_managers | adhd_focus | からだに宿る集中の困難との対話 | 集中の困難のあとに、からだに宿る静けさを取り戻す — 管理職のために |
| qi_foundation | corporate_managers | adhd_focus | 集中の困難を超えて、根づいた日々へ | 集中の困難回復のための、しずかな歩み — 管理職のために |
| digital_ground | millennial_women_professionals | adhd_focus | 落ち着いた集中の困難の手当て | 集中の困難を抜けるための、落ち着いた日々への手引き — ミレニアル世代の女性へ |
| heart_balance | corporate_managers | adhd_focus | ととのう集中の困難回復の歩み | 集中の困難が止まらないときの、ととのう手引き — 管理職のために |
| relational_calm | corporate_managers | adhd_focus | やわらかな集中の困難との対話 | 集中の困難のあとに、やわらかな静けさを取り戻す — 管理職のために |
| warrior_calm | corporate_managers | adhd_focus | ゆるがぬ集中の困難回復の歩み | 集中の困難が止まらないときの、ゆるがぬ手引き — 管理職のために |

### zh_TW

| Brand | Persona | Topic | Title | Subtitle |
|---|---|---|---|---|
| sleep_repair_tw | corporate_managers | adhd_focus | 睡眠修復的步調，走出專注困難 | 當專注困難停不下來時的睡眠修復的指引 — 寫給中階主管 |
| stabilizer_tw | corporate_managers | adhd_focus | 神經安穩的步調，走出專注困難 | 當專注困難停不下來時的神經安穩的指引 — 寫給中階主管 |
| panic_first_aid_tw | corporate_managers | adhd_focus | 恐慌急救的步調，走出專注困難 | 當專注困難停不下來時的恐慌急救的指引 — 寫給中階主管 |
| gen_z_grounding_tw | corporate_managers | adhd_focus | 專注困難之後，Z 世代踏實的日子 | Z 世代踏實的生活，專注困難復原的同行者 — 寫給中階主管 |
| grief_companion_tw | corporate_managers | adhd_focus | 悲傷陪伴的專注困難指引 | 走出專注困難，邁向悲傷陪伴的日子 — 寫給中階主管 |
| inner_security_tw | corporate_managers | adhd_focus | 專注困難之後，內在安穩的日子 | 內在安穩的生活，專注困難復原的同行者 — 寫給中階主管 |
| stillness_press | corporate_managers | adhd_focus | 專注困難之後，靜默的日子 | 靜默的生活，專注困難復原的同行者 — 寫給中階主管 |
| cognitive_clarity | corporate_managers | adhd_focus | 穿越專注困難，走向清明的時光 | 專注困難復原途中的清明的陪伴 — 寫給中階主管 |

### zh_CN

| Brand | Persona | Topic | Title | Subtitle |
|---|---|---|---|---|
| sleep_repair_cn | corporate_managers | adhd_focus | 穿越注意力困难，走向睡眠修复的日子 | 注意力困难恢复期的睡眠修复的陪伴 — 写给中层管理者 |
| stabilizer_cn | corporate_managers | adhd_focus | 神经稳定的注意力困难指南 | 走出注意力困难，迈向神经稳定的日子 — 写给中层管理者 |
| panic_first_aid_cn | corporate_managers | adhd_focus | 恐慌急救的节奏，走出注意力困难 | 当注意力困难无法停止时的恐慌急救的指引 — 写给中层管理者 |
| gen_z_grounding_cn | corporate_managers | adhd_focus | 注意力困难之后，Z 世代安身的日子 | Z 世代安身的生活，注意力困难恢复的同行者 — 写给中层管理者 |
| grief_companion_cn | corporate_managers | adhd_focus | 注意力困难之后，悲伤陪伴的日子 | 悲伤陪伴的生活，注意力困难恢复的同行者 — 写给中层管理者 |
| inner_security_cn | corporate_managers | adhd_focus | 内在安稳的节奏，走出注意力困难 | 当注意力困难无法停止时的内在安稳的指引 — 写给中层管理者 |
| stillness_press | corporate_managers | adhd_focus | 止息的注意力困难指南 | 走出注意力困难，迈向止息的日子 — 写给中层管理者 |
| cognitive_clarity | corporate_managers | adhd_focus | 清明的注意力困难的同行 | 注意力困难恢复期的清明的日子 — 写给中层管理者 |

## 6. Method

- **Architecture: layered onto #790, not parallel to it.** All B1 additions are sibling keys in the same YAMLs (`voice_prefix_{locale}` next to `voice_prefix`; `signal_{locale}` next to `signal`; `title_templates_{locale}` next to `title_templates`; `topic_displays_{locale}` is new).
- **Generator change is one function** — `pick_title_subtitle()` now branches on `locale != 'en_US'` to use the locale-keyed entries. en_US path is unmodified, hence the byte-identical guarantee.
- **Non-en formula templates** (5 per locale): each carries `{voice_prefix}` and `{topic}` placeholders. `{voice_prefix}` always sits in attributive position immediately before a noun, so the result parses cleanly regardless of locale-specific modifier form (Japanese 連体形 — na-adj/i-adj/verb-past; Chinese 的-suffixed adjective).
- **Determinism preserved.** Same `sha256(locale|brand|topic|persona|teacher_mode|runtime_format)` salt as #790; same input → same output, every regeneration.
- **zh-specific brands covered.** All 7 zh_TW-specific brands (incl. bright_presence_tw, P2-deferred for adi_da scoring) and all 6 zh_CN-specific brands have voice_prefix entries for their locale.
- **Tonal anchors per rubric:**
  - `ja_JP` — contemplative, understated. Hiragana-rich, 体言止め where natural.
  - `zh_TW` — emotional clarity, human tone. Traditional characters.
  - `zh_CN` — structured, outcome-oriented. Simplified characters.

## 7. Native-fluency caveat

Per owner directive, the CJK voice_prefixes, persona signals, topic_displays, and formula templates are **best-effort drafts** authored without a native-fluency reviewer. They are deliberately conservative: short attributive phrases, no slang, no AI-translation idioms. A few likely-to-flag phrasings are documented in the PR description.

**Tonal misses are 1-line YAML edits.** All phrase content lives in `config/catalog/catalog_generation_config.yaml` under named sections; phrase swap requires zero code change, regeneration takes ~10s.

## 8. Out of scope

- en_US titles/subtitles — byte-identical to origin/main (rubric requirement).
- Scoring data — last touched in B3+B4 (PR #780).
- 160 zh_TW bright_presence_tw rows still blocked_score (adi_da scoring is P2).
- No book assembly, no LLM, no `--admin`, no threshold tuning.
- No new top-level files / systems — strictly extends #790's existing structures.
