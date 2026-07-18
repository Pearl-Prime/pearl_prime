# It se
_Exported on 4/16/2026 at 19:22:18 GMT+8 from Cursor (3.1.15)_

---

**User**

## PROMPT — CJK Teacher Topic Pack Overlays + Per-Language System Prompts

**AGENT:** Pearl_Dev + Pearl_Writer + Pearl_PM  
**TASK:** Translate deterministic slot content in teacher topic packs for Japanese and Chinese; create per-language system prompts (ja, zh-cn) for tighter editorial register  

### STARTUP_RECEIPT
```
AGENT: Pearl_Dev + Pearl_Writer + Pearl_PM
TASK: CJK teacher topic pack locale overlays + per-language system prompts
WRITE_SCOPE: pearl_news/teacher_topic_packs/locales/; pearl_news/prompts/
OUT_OF_SCOPE: phoenix_v4/; brand-wizard-app/; Korean (ko) — dropped from requirements
BLOCKERS: none
READY_STATUS: ready
```

### Context

Pearl News CJK articles currently have a split-language problem. The 2 LLM-prompted slots (news_peg, body_data) produce Japanese/Chinese text via Qwen + locale prompt files (PR #414, merged). But the **12 deterministic slots** still inject **English text** from the base teacher topic packs. A Japanese article has English teacher_intro, English hook_personal, English bridge — with only the data sections in Japanese. The article reads like a translation accident.

**Korean is dropped from this scope.** Focus only on Japanese (ja) and Chinese (zh-cn).

### Read First

```bash
# 1. Understand the pack structure
ls pearl_news/teacher_topic_packs/teachers/
cat pearl_news/teacher_topic_packs/teachers/ahjan/anxiety.yaml

# 2. Understand the overlay mechanism
grep -n "language\|locale\|deep_merge\|overlay" pearl_news/pipeline/deterministic_teacher_topic.py

# 3. List all teacher × topic combinations that have packs
find pearl_news/teacher_topic_packs/teachers -name "*.yaml" | sort

# 4. Read the current shared CJK system prompt
cat pearl_news/prompts/expansion_system_cjk.txt

# 5. Read the English system prompt for comparison
cat pearl_news/prompts/expansion_system_en.txt
```

### Phase 1 — Inventory All Teacher Topic Packs

Before translating, inventory what exists:

```bash
find pearl_news/teacher_topic_packs/teachers -name "*.yaml" -type f | \
  sed 's|.*/teachers/||' | sort
```

This gives you every `{teacher_id}/{topic}.yaml` pair. Each file contains deterministic slot values — the text that gets injected directly into articles without LLM involvement.

For each pack, identify which fields contain prose that readers see (these need translation):
- `hook_personal` — second-person opening lede
- `hook_big_picture` — systemic angle opener
- `teacher_intro` — teacher credential paragraph
- `teacher_perspective` — teacher's unique angle
- `teacher_witness` — teaching story/observation
- `bridge` — data-to-inner-capacity transition
- `turnaround` — crisis-as-opportunity reframe
- `practice_announce` — practice introduction sentence
- `forward_look` — next steps / concrete action
- `youth_somatic` — gen-Z nervous system angle
- `headline_layer_1` — main headline
- `headline_layer_2` — subtitle

Fields that are metadata or structural (NOT translated): `teacher_id`, `topic`, `template_id`, `sdg_number`, `sdg_name`, `un_agency_name`, etc.

### Phase 2 — Create Locale Overlay Files

#### File structure

```
pearl_news/teacher_topic_packs/
  teachers/{teacher_id}/{topic}.yaml               ← English base (existing, DO NOT modify)
  locales/ja/teachers/{teacher_id}/{topic}.yaml     ← Japanese overlay (new)
  locales/zh-cn/teachers/{teacher_id}/{topic}.yaml  ← Chinese overlay (new)
```

The overlay is a **partial YAML** — it only contains the fields that differ from English. The engine deep-merges overlay onto base at runtime (overlay values win at leaf level).

#### Overlay file format

For each English pack, the Japanese overlay contains ONLY the prose fields, translated:

```yaml
# pearl_news/teacher_topic_packs/locales/ja/teachers/ahjan/anxiety.yaml
# Japanese locale overlay — deep-merged onto English base at runtime.
# Only prose fields that readers see. Metadata/structural fields inherit from English.

hook_personal: |
  [Japanese translation of the hook_personal text — intimate, second-person,
   body-cost framing. Register: です・ます, like NHK feature writing.]

hook_big_picture: |
  [Japanese translation — systemic angle, why this matters at scale.]

teacher_intro: |
  [Japanese translation — one paragraph establishing teacher authority on this topic.
   Keep teacher name in romaji (e.g., Ahjan, not アジャン) for brand consistency.]

teacher_perspective: |
  [Japanese — teacher's unique spiritual/somatic angle on the topic.]

teacher_witness: |
  [Japanese — brief teaching story from this teacher's experience.]

bridge: |
  [Japanese — connect data to inner capacity, cite teacher tradition.]

turnaround: |
  [Japanese — reframe crisis as growth opportunity. No toxic positivity.]

practice_announce: |
  [Japanese — one sentence introducing a practice the reader can try.]

forward_look: |
  [Japanese — what comes next, one concrete action for today.]

youth_somatic: |
  [Japanese — gen-Z nervous system angle. Body-first language. No lecturing.]

headline_layer_1: "[Japanese main headline — short, punchy, news-forward]"

headline_layer_2: "[Japanese subtitle — teacher angle or emotional hook]"
```

Same structure for Chinese (zh-cn), using professional Mandarin editorial register (书面语).

#### Translation method

For each teacher topic pack:

1. Read the English base pack
2. Extract all 12 prose fields
3. Translate to Japanese and Chinese using Claude (Agent tool) with these instructions:

**Japanese translation instruction:**
```
Translate these Pearl News article slot texts into Japanese.
Register: professional editorial (です・ます), like NHK or Asahi feature writing.
- Keep teacher names in romaji (Ahjan, Joshin, Miki) — do NOT katakana-ize them
- Keep tradition names recognizable (Zen Buddhism = 禅仏教, not a creative rewrite)  
- Body-centered language should use standard somatic vocabulary (身体, 神経系, 呼吸)
- Youth/gen-Z language should feel natural for Japanese young adults, not textbook
- Headlines must be punchy in Japanese — different rhythm than English
- Do NOT translate metadata fields (teacher_id, topic, sdg_number, etc.)
- Output as YAML with the same field names as the English source
```

**Chinese translation instruction:**
```
Translate these Pearl News article slot texts into simplified Mandarin Chinese.
Register: professional editorial (书面语), like Xinhua or Caixin feature writing.
- Keep teacher names in pinyin/English (Ahjan, Master Feung) — do NOT hanzi-ize them
- Keep tradition names recognizable (Qi Foundation = 气功基础, Zen = 禅)
- Body-centered language should use standard somatic vocabulary (身体, 神经系统, 呼吸)
- Youth language should feel natural for Chinese young adults (Z世代, not 年轻一代)
- Headlines must be punchy in Chinese — different rhythm than English
- Use 你 not 您 for second-person address
- Do NOT translate metadata fields
- Output as YAML with the same field names as the English source
```

#### Execution order

Prioritize teachers who have CJK Pearl News articles:

**Japanese teachers (highest priority — their articles ARE in Japanese):**
1. joshin (all topics)
2. miki (all topics)
3. junko (all topics)
4. omote (all topics)

**Chinese teachers (their articles ARE in Chinese):**
5. master_feung (all topics)
6. master_wu (all topics)

**English teachers with CJK audience reach (lower priority):**
7. ahjan (all topics) — for when Japanese/Chinese editions run ahjan content
8. All remaining teachers — translate as time permits

For each teacher, translate ALL topic packs they have. A teacher with 5 topic packs gets 5 ja overlays + 5 zh-cn overlays.

### Phase 3 — Per-Language System Prompts

Currently all CJK languages share `expansion_system_cjk.txt`. Create language-specific versions for tighter editorial register.

#### 3A. Japanese system prompt

Create `pearl_news/prompts/expansion_system_ja.txt`:

```bash
cat pearl_news/prompts/expansion_system_cjk.txt
# Read the current shared CJK prompt, then specialize for Japanese
```

The Japanese system prompt should:
- Be written IN Japanese (not English instructions about Japanese)
- Open with: `あなたはPearl Newsの日本語編集AIです。`
- Specify register: です・ます form, NHK feature writing style
- Specify output format: plain text, no HTML/markdown
- Specify somatic vocabulary norms: 身体 (not ボディ), 神経系 (not ナーバスシステム), 呼吸法 (not ブレスワーク)
- Specify teacher name handling: Keep in romaji (Ahjan, Joshin) — brand names are NOT transliterated
- Specify headline style: Japanese news headline conventions (shorter than English, verb at end or nominalized)
- Preserve any slot-engine structural requirements from the current CJK prompt (CONTEXT:, SLOT: parsing tokens)
- Include: `出力は必ず日本語で書いてください。HTMLやMarkdownは使用しないでください。`

#### 3B. Chinese system prompt

Create `pearl_news/prompts/expansion_system_zh_cn.txt`:

- Written IN Chinese
- Open with: `你是Pearl News的简体中文编辑AI。`
- Specify register: 书面语, Caixin/Xinhua feature style
- Specify: 你 not 您, simplified characters only
- Specify somatic vocabulary: 身体 (not body), 神经系统 (not nervous system), 正念 (not mindfulness as loanword)
- Teacher names: Keep in English/pinyin
- Include: `请用简体中文撰写所有输出内容。不使用HTML或Markdown格式。`

#### 3C. Update routing to use per-language prompts

Check how the system prompt is selected in `expansion_routing.py` or `slot_expansion_engine.py`:

```bash
grep -n "system_prompt\|expansion_system" pearl_news/pipeline/slot_expansion_engine.py pearl_news/pipeline/expansion_routing.py pearl_news/config/llm_expansion.yaml
```

Update the routing so:
- `ja` → loads `expansion_system_ja.txt`
- `zh-cn` (and `zh-tw`, `zh-hk`, `zh-sg`) → loads `expansion_system_zh_cn.txt`
- `en` → keeps `expansion_system_en.txt`
- Any other language → falls back to `expansion_system_cjk.txt` (the generic one, kept as fallback)

This may be a config change in `llm_expansion.yaml`:
```yaml
providers:
  qwen_slots:
    system_prompts:
      ja: expansion_system_ja.txt
      zh-cn: expansion_system_zh_cn.txt
      default: expansion_system_cjk.txt
```

Or a code change in the engine to look up `expansion_system_{lang}.txt` with fallback to `expansion_system_cjk.txt`.

### Phase 4 — Validation

#### 4A. Pack overlay validation

```python
import os, yaml, glob

for lang in ['ja', 'zh-cn']:
    overlays = glob.glob(f'pearl_news/teacher_topic_packs/locales/{lang}/teachers/**/*.yaml', recursive=True)
    print(f"\n{lang}: {len(overlays)} overlay files")
    for path in sorted(overlays):
        with open(path) as f:
            data = yaml.safe_load(f)
        # Must have at least headline + hook + teacher_intro
        assert 'headline_layer_1' in data, f"Missing headline_layer_1 in {path}"
        assert 'hook_personal' in data or 'hook_big_picture' in data, f"Missing hook in {path}"
        assert 'teacher_intro' in data, f"Missing teacher_intro in {path}"
        # Must NOT have metadata fields (those inherit from English)
        for bad_key in ['teacher_id', 'topic', 'sdg_number', 'template_id']:
            assert bad_key not in data, f"Metadata key {bad_key} should not be in overlay {path}"
        print(f"  ✓ {path}")
```

#### 4B. System prompt validation

```bash
# Japanese prompt exists and contains Japanese text
grep "日本語" pearl_news/prompts/expansion_system_ja.txt
# Chinese prompt exists and contains Chinese text  
grep "中文" pearl_news/prompts/expansion_system_zh_cn.txt
```

#### 4C. Live pipeline test

Run one article per language and verify the output is fully in the target language:

```bash
eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"

# Japanese article with Joshin (Japanese teacher)
PYTHONPATH=. python3 -m pearl_news.pipeline.run_article_pipeline \
  --language ja --limit 1 --expand --validate 2>&1 | tail -15

# Check the output — ALL slots should be Japanese, not just news_peg/body_data
cat artifacts/pearl_news/drafts/ja/*.html | head -50
# Verify: teacher_intro is in Japanese, hook_personal is in Japanese, etc.

# Chinese article with Master Feung (Chinese teacher)
PYTHONPATH=. python3 -m pearl_news.pipeline.run_article_pipeline \
  --language zh-cn --limit 1 --expand --validate 2>&1 | tail -15

# English regression
PYTHONPATH=. python3 -m pearl_news.pipeline.run_article_pipeline \
  --language en --limit 1 --expand --validate 2>&1 | tail -15
```

**Success criteria:**
- Japanese article: ALL 14 slots in Japanese (not a mix of English + Japanese)
- Chinese article: ALL 14 slots in Chinese
- English article: unchanged behavior (regression check)

### Branch & Commit

```bash
git fetch origin
git checkout -b agent/cjk-pack-overlays-system-prompts origin/main

# Commit 1: System prompts
git add pearl_news/prompts/expansion_system_ja.txt pearl_news/prompts/expansion_system_zh_cn.txt
git commit -m "feat(pearl_news): per-language system prompts for ja and zh-cn"

# Commit 2: Pack overlays (per teacher for reviewability)
git add pearl_news/teacher_topic_packs/locales/
git commit -m "feat(pearl_news): CJK teacher topic pack overlays — deterministic slots in target language"

# Commit 3: Routing update (if code change needed)
git add pearl_news/pipeline/ pearl_news/config/
git commit -m "feat(pearl_news): route ja/zh-cn to per-language system prompts"
```

### Important Rules

1. **No Korean** — dropped from scope. Do not create `ko/` directories or Korean system prompts.
2. **Teacher names stay in romaji/English** — Ahjan is "Ahjan" in Japanese articles, not アジャン. Brand consistency.
3. **ahjan is NEVER "ajahn"** — if you see "ajahn" anywhere in pack content, fix it to "ahjan".
4. **Overlay = partial YAML** — only prose fields. Never duplicate metadata from the English base.
5. **Do NOT modify English base packs** — overlays only. English is the source of truth.

### CLOSEOUT_RECEIPT required fields
```
AGENT / TASK / COMMIT_SHA / FILES_WRITTEN / STATUS / NEXT_ACTION
Evidence:
  - N overlay files created (ja + zh-cn)
  - expansion_system_ja.txt and expansion_system_zh_cn.txt created
  - Routing updated for per-language system prompts
  - Japanese pipeline: all 14 slots in Japanese (no English text in deterministic slots)
  - Chinese pipeline: all 14 slots in Chinese
  - English regression: unchanged
NEXT_ACTION: Monitor CJK article quality in production; iterate on translations based on editorial feedback
```

---

**Cursor**

Implementing CJK teacher topic pack overlays and per-language system prompts. Exploring the codebase structure and inventorying packs.



Checking English pack YAML structure — overlays must mirror nested `options`/`title_system`, not flat prose fields.



Implementing merge-by-id for `options` arrays so partial overlays patch each option without replacing the full list. Then adding system prompts, routing, and generating overlays (starting with merge logic).



Implementing prompts and routing, then generating overlays. Reading full pack files for priority teachers in batches.



Creating system prompt files, then using a subagent to produce the first batch of overlay YAMLs.



Verifying ahjan overlays and launching parallel subagents for the remaining teachers.



Writing system prompts, validation script, tests, and updating `llm_expand.py`.



## Summary

Locale overlays are **nested YAML** matching the English packs (`hook_personal.options[].line`, `title_system`, `sdg`, etc.), not flat slot strings. `_deep_merge` now **merges `options` lists by `id`**, so each overlay can patch translated fields without replacing the whole option list (see ```64:95:pearl_news/pipeline/deterministic_teacher_topic.py```).

When the Qwen provider still points at `expansion_system_cjk.txt`, `resolve_expansion_system_prompt` loads **`expansion_system_ja.txt`** for `ja` and **`expansion_system_zh_cn.txt`** for any `zh-*`; **ko / vi / other CJK** keep the shared CJK file (```100:134:pearl_news/pipeline/slot_expansion_engine.py```). The same rule is applied in **`llm_expand._load_system_prompt`** for legacy full-document expansion.

**Delivered:** 102 overlay files (`ja` + `zh-cn` × **51** English base packs), Japanese and Simplified Chinese system prompts, validation script `scripts/pearl_news/validate_teacher_locale_overlays.py`, and tests for options-merge + prompt resolution.

**Repo facts:** `teachers/omote/` has **3** launch topics (not 4); `teachers/pamela_fellows/` has **3** YAMLs. Japanese “Junko” teacher id is **`channeler_junko`**. English identity for `master_feung` still uses **Master Fan** in the base pack (unchanged).

**Checks run:** `python3 scripts/pearl_news/validate_teacher_locale_overlays.py`, `pytest tests/test_slot_expansion_engine.py`, and a small `build_hard_news_deterministic_plan` smoke test for `ja` / `zh-cn` / `en`. Full `--expand` pipeline with Qwen was **not** run here (needs your Qwen endpoint and keychain env).

---

### CLOSEOUT_RECEIPT

```
AGENT: Pearl_Dev + Pearl_Writer + Pearl_PM
TASK: CJK teacher topic pack locale overlays + per-language system prompts
COMMIT_SHA: 15178196be (branch tip; stack: dc3211f39a → 87fee2b8a1 → 15178196be)
FILES_WRITTEN:
  - pearl_news/prompts/expansion_system_ja.txt
  - pearl_news/prompts/expansion_system_zh_cn.txt
  - pearl_news/teacher_topic_packs/locales/ja/**  (51 YAML)
  - pearl_news/teacher_topic_packs/locales/zh-cn/** (51 YAML)
  - scripts/pearl_news/validate_teacher_locale_overlays.py
  - tests/test_slot_expansion_engine.py (merge + prompt routing tests)
  - pearl_news/pipeline/deterministic_teacher_topic.py (options merge-by-id)
  - pearl_news/pipeline/slot_expansion_engine.py (per-lang system prompt routing)
  - pearl_news/pipeline/llm_expand.py (same routing for legacy Qwen expand)
STATUS: complete (local validation + unit tests; live Qwen expand not executed in this session)
NEXT_ACTION: Push branch agent/cjk-pack-overlays-system-prompts and open PR; run run_article_pipeline with Qwen for ja/zh-cn/en spot-checks when the API is available.

Evidence:
  - 102 overlay files (ja + zh-cn)
  - expansion_system_ja.txt and expansion_system_zh_cn.txt created
  - Routing: ja → expansion_system_ja.txt; zh-cn/zh-tw/zh-hk/zh-sg → expansion_system_zh_cn.txt; other CJK on expansion_system_cjk.txt
  - Deterministic merge: ja/zh-cn teacher_intro + hooks localized (smoke + validate script)
  - English regression: unchanged base YAMLs; en plans still English
```

---

**User**

do you have sai_maa_vid.mp4 or ra.mp4 ?
were you helping me move vids? 

---

**Cursor**

Searching the repo for those video files.



Here’s what shows up in **this workspace** right now:

### `sai_maa_vid.mp4`
- **Not present** under the names we checked. Your own inventory note says the repo uses the slug **`sai_ma`**, and the wired file is  
  `brand-wizard-app/public/assets/video/tiktok/sai_ma_depression_tiktok.mp4` (see `artifacts/video/TEACHER_R2_URL_INVENTORY.md`).  
- `teacher_vid_package/` at the repo root only has **`ahjan.mp4`** and **`maat.mp4`** — no `sai_*` mp4 there.

### `ra.mp4`
- **Not found** as a literal `ra.mp4` in a quick scan, and there is **no** `artifacts/video/tiktok_body_awareness/ra/` folder (that tree currently has things like `ahjan`, `joshin`, `junko`, `miki`, `omote`, etc., but not `ra` or `sai_ma`).

### Was I helping you move videos?
In **this chat thread**, no — the work we did was **Pearl News CJK teacher topic packs / prompts**, not video moves.  
Separately, your machine/session had **git stashes that included TikTok body-awareness artifacts** (lots of `artifacts/video/tiktok_body_awareness/...` paths), which can look like “moving vids,” but that wasn’t the task I was executing in the messages I have here.

If you want, we can next search **Downloads**, **`_wt_r2_sai_ma`**, or **R2** keys for `ra` / `sai_maa` — say which locations you care about.

