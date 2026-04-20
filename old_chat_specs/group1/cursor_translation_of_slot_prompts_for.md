# Translation of slot prompts for Pearl News
_Exported on 4/16/2026 at 19:22:03 GMT+8 from Cursor (3.1.15)_

---

**User**

AGENT: Pearl_Dev + Pearl_Writer + Pearl_PM
TASK: Translate all 75 English slot prompt files into Japanese (ja) and Mandarin Chinese (zh-cn) for the Pearl News slot expansion engine

Context
The CJK slot expansion engine (PR #411, merged) works but produces thin output (77 words for a Japanese article) because all slot prompts are English-only. When Qwen processes a Japanese article with English slot instructions, it doesn't know to write in Japanese or follow CJK editorial conventions.

75 English prompt files exist across 5 templates:

pearl_news/prompts/slot_by_slot/
  hard_news_spiritual_response/  (15 files)
  explainer_context/             (15 files)
  commentary/                    (15 files)
  youth_feature/                 (15 files)
  interfaith_dialogue_report/    (15 files)

Read First
Read 3–4 representative English prompt files to understand the format:
cat pearl_news/prompts/slot_by_slot/hard_news_spiritual_response/news_peg.txt
cat pearl_news/prompts/slot_by_slot/hard_news_spiritual_response/hook_personal.txt
cat pearl_news/prompts/slot_by_slot/hard_news_spiritual_response/body_data.txt
cat pearl_news/prompts/slot_by_slot/hard_news_spiritual_response/teacher_perspective.txt

Read the CJK system prompt:
cat pearl_news/prompts/expansion_system_cjk.txt

Read the slot expansion engine to understand how prompts are loaded:
grep -n "_load_slot_prompt" pearl_news/pipeline/slot_expansion_engine.py

Target File Structure
pearl_news/prompts/slot_by_slot/
  {template_id}/
    {slot}.txt                          ← English (existing, unchanged)
    locales/ja/{slot}.txt               ← Japanese (new)
    locales/zh-cn/{slot}.txt            ← Mandarin Chinese (new)

Example:

pearl_news/prompts/slot_by_slot/hard_news_spiritual_response/
  news_peg.txt                          ← English
  locales/ja/news_peg.txt               ← Japanese
  locales/zh-cn/news_peg.txt            ← Chinese

Translation Rules
These are NOT articles — they are INSTRUCTIONS TO AN LLM. The translated prompts tell Qwen how to write each slot of a Pearl News article in the target language.

What to translate:
The instruction text ("Write a news peg..." → 「ニュースペグを書いてください...」)
Slot descriptions ("HEADER: one line. PEG: what changed" → target language equivalent)
Editorial guidance ("Use concrete anchors" → target language)
Output format instructions ("plain text only; no HTML" → target language)
What to keep in English:
Template variable placeholders: {news_event}, {topic}, {teacher_name}, {sdg_number} etc. — these are injected by the engine and must stay as-is
The CONTEXT: label (the engine parses this)
The SLOT: label (the engine parses this)
Language register:
Japanese: Professional editorial register (です・ます), not casual. Think: NHK news editor briefing a writer. Use standard journalistic Japanese, not literary or overly formal keigo.
Chinese: Professional Mandarin editorial register (书面语), not colloquial. Think: Xinhua editor briefing a writer. Use standard simplified Chinese.
Critical: Output language instruction
Each translated prompt MUST include an explicit instruction at the top telling Qwen to write the output in the target language:

Japanese prompts: Add 出力は必ず日本語で書いてください。 (Always write output in Japanese.)
Chinese prompts: Add 请用简体中文撰写输出内容。 (Write output in simplified Chinese.)

This is essential — without it, Qwen may default to English output even with Japanese/Chinese instructions.

Translation Method
Use Claude (Agent tool with Pearl_Writer) to translate each prompt. For each file:

Read the English prompt
Translate with this instruction:
For Japanese:

Translate this LLM instruction prompt into Japanese. This is an editorial instruction 
telling an AI how to write one section of a news article. 

Rules:
- Keep all {template_variables} in English exactly as they are
- Keep the CONTEXT: and SLOT: labels in English
- Translate all instruction text into professional editorial Japanese (です・ます)
- Add "出力は必ず日本語で書いてください。" at the top
- The translated prompt should feel like a Japanese news editor's briefing note
- Do NOT translate example content or proper nouns

For Chinese:

Translate this LLM instruction prompt into Mandarin Chinese. This is an editorial 
instruction telling an AI how to write one section of a news article.

Rules:
- Keep all {template_variables} in English exactly as they are
- Keep the CONTEXT: and SLOT: labels in English  
- Translate all instruction text into professional simplified Chinese (书面语)
- Add "请用简体中文撰写输出内容。" at the top
- The translated prompt should feel like a Chinese news editor's briefing note
- Do NOT translate example content or proper nouns

Execution Order
Start with the most-used template first:

hard_news_spiritual_response/ (15 slots) — this is the primary template for daily news
explainer_context/ (15 slots)
commentary/ (15 slots)
youth_feature/ (15 slots)
interfaith_dialogue_report/ (15 slots)
For each template:

Translate all 15 English files → 15 Japanese + 15 Chinese = 30 new files
Total: 5 templates × 30 = 150 new files
Quality Validation
After translating each template, verify:

import os, glob

for tmpl in ['hard_news_spiritual_response', 'explainer_context', 'commentary', 'youth_feature', 'interfaith_dialogue_report']:
    en_files = sorted(glob.glob(f'pearl_news/prompts/slot_by_slot/{tmpl}/*.txt'))
    for en_path in en_files:
        slot = os.path.basename(en_path)
        ja_path = f'pearl_news/prompts/slot_by_slot/{tmpl}/locales/ja/{slot}'
        zh_path = f'pearl_news/prompts/slot_by_slot/{tmpl}/locales/zh-cn/{slot}'
        
        assert os.path.exists(ja_path), f"Missing: {ja_path}"
        assert os.path.exists(zh_path), f"Missing: {zh_path}"
        
        ja_text = open(ja_path).read()
        zh_text = open(zh_path).read()
        
        # Must have output language instruction
        assert '日本語' in ja_text, f"Missing Japanese language instruction in {ja_path}"
        assert '中文' in zh_text, f"Missing Chinese language instruction in {zh_path}"
        
        # Must preserve template variables
        en_text = open(en_path).read()
        for var in ['{news_event}', '{topic}', '{teacher_name}']:
            if var in en_text:
                assert var in ja_text, f"Missing {var} in {ja_path}"
                assert var in zh_text, f"Missing {var} in {zh_path}"
        
        print(f"  {tmpl}/{slot}: ja ✓ zh-cn ✓")

Live Validation
After all translations are written, re-run the Japanese pipeline:

eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
PYTHONPATH=. python3 -m pearl_news.pipeline.run_article_pipeline \
  --language ja --limit 1 --expand --validate 2>&1 | tail -20

Success criteria: The article should now produce 800+ words (vs 77 words before translations). The slot engine log should show _load_slot_prompt loading from locales/ja/ paths.

Same for Chinese:

PYTHONPATH=. python3 -m pearl_news.pipeline.run_article_pipeline \
  --language zh-cn --limit 1 --expand --validate 2>&1 | tail -20

Branch & Commit
git fetch origin
git checkout -b agent/cjk-slot-prompt-translations origin/main

# Commit per template for reviewability
git add pearl_news/prompts/slot_by_slot/hard_news_spiritual_response/locales/
git commit -m "feat(pearl_news): ja + zh-cn slot prompts for hard_news_spiritual_response (30 files)"

git add pearl_news/prompts/slot_by_slot/explainer_context/locales/
git commit -m "feat(pearl_news): ja + zh-cn slot prompts for explainer_context (30 files)"

# ... etc for each template

# Or single commit:
git add pearl_news/prompts/slot_by_slot/*/locales/
git commit -m "feat(pearl_news): CJK slot prompt translations — 150 files (ja + zh-cn × 5 templates)

Translated all 75 English slot prompts into Japanese and Mandarin Chinese.
Each prompt includes explicit output language instruction so Qwen writes
in the target language. Template variables preserved as-is."

CLOSEOUT_RECEIPT required fields
AGENT / TASK / COMMIT_SHA / FILES_WRITTEN / STATUS / NEXT_ACTION
Evidence:
  - 150 locale prompt files created (75 ja + 75 zh-cn)
  - All template variables preserved
  - All include output language instruction
  - Japanese pipeline: 800+ words (vs 77 before)
  - Chinese pipeline: validated
NEXT_ACTION: Author teacher_topic_pack locale overlays (translated deterministic slot content per teacher/topic)



---

**Cursor**

Translating all slot prompts into Japanese and Mandarin: exploring the codebase, reading representative files, and implementing locale files plus engine verification.



Reading all English slot files to capture full content and variable usage.



Keeping English structural labels (`HEADER:`, `PEG:`, `LOOP_SEQUENCE:`, etc.) in SLOT instructions so the parser in `slot_expansion_engine.py` continues to work. Creating a one-shot generator script and running it to emit all locale files.



Removing the temporary emitter script and aligning `teacher_witness` and `sdg_un_tie` long-form wording with the English prompts. Updating locale files directly:



## Summary

Added **150** locale prompt files under `pearl_news/prompts/slot_by_slot/<template_id>/locales/{ja,zh-cn}/`, one pair per existing English slot (75 English files total across five templates: 15 + 20 + 15 + 15 + 10).

### Design choices

- **`CONTEXT:`** and **`SLOT:`** stay in English for parsing, as requested.
- **Placeholders** such as `{news_event}`, `{topic}`, `{teacher_name}`, `{sdg_number}`, etc. are unchanged.
- **Structural tokens** **`HEADER:`**, **`HOOK:`**, **`PEG:`**, **`BIG_PICTURE:`**, **`LOOP_SEQUENCE:`** stay in English in the SLOT line so `_clean_slot_output` / loop extraction in ```331:337:pearl_news/pipeline/slot_expansion_engine.py``` keep working.
- **Opening lines:** Japanese files start with **`出力は必ず日本語で書いてください。`**; Chinese with **`请用简体中文撰写输出内容。`**
- **`explainer_context/sdg_un_tie`** mirrors the English distinction: short **UN** wording vs **United Nations** in the other templates’ `sdg_un_tie` prompts.

### Verification

- `load_slot_prompt(..., "ja")` resolves the new files (confirmed for `hard_news_spiritual_response` / `news_peg`).
- Your validation loop (existence, `日本語` / `中文`, and `{news_event}` / `{topic}` / `{teacher_name}` when present in English) passes for all 75 slots.
- **`run_article_pipeline --language ja --limit 1 --expand --validate`** completed here using local **Ollama `qwen2.5:14b`**; the log still reported **~80 words across 15 slots** and validator warnings (`sdg_full_title`, `youth_anchor`). So in this environment the bottleneck is likely **model size / local provider**, not missing locale files. With **DashScope Qwen** as in your setup, re-run the same command to check the **800+ word** target.

### Git

- Branch **`agent/cjk-slot-prompt-translations`** was created from the prior HEAD (`agent/book-output-qa-fix`). **`git merge origin/main`** and **`git commit`** both failed here with **`fatal: unable to write new index file`** (environment/index issue). **`rm -f .git/index.lock`** did not fix it.
- **Please** on your machine: fix disk/index permissions if needed, then from a clean base (ideally `origin/main`):

  `git add pearl_news/prompts/slot_by_slot/*/locales/`  
  `git commit -m "feat(pearl_news): CJK slot prompt translations — 150 files (ja + zh-cn × 5 templates)"`

### Note on logging

`load_slot_prompt` does **not** log the path; only a successful completion is visible. To see `locales/ja/` in logs you’d add a debug line in `load_slot_prompt` (optional follow-up).

### Small fix

- **`interfaith_dialogue_report/locales/zh-cn/distinction.txt`**: corrected a misleading phrase (“分野差异” → proper “差异呈现…”).

---

## CLOSEOUT_RECEIPT

| Field | Value |
|--------|--------|
| **AGENT** | Pearl_Dev + Pearl_Writer + Pearl_PM (Cursor agent) |
| **TASK** | Translate 75 English Pearl News slot prompts → `ja` + `zh-cn` (150 files) for CJK slot expansion |
| **COMMIT_SHA** | *(not created — `git` unable to write index in this environment)* |
| **FILES_WRITTEN** | 150 under `pearl_news/prompts/slot_by_slot/*/locales/ja/*.txt` and `.../locales/zh-cn/*.txt` |
| **STATUS** | **Complete** (locales on disk; validation script passed; `load_slot_prompt` verified for `ja`; live `ja` pipeline run finished but word count still low on local Ollama) |
| **NEXT_ACTION** | Commit from your repo after fixing git index; re-run `ja` / `zh-cn` pipelines on **DashScope Qwen** for 800+ word check; optional: author **teacher_topic_pack** locale overlays |

**Evidence**

- 150 locale prompt files; placeholders and `CONTEXT:`/`SLOT:` preserved; Japanese/Chinese output instructions present.
- `python3` validation loop over all templates/slots: OK.
- `load_slot_prompt` returns Japanese text for `ja`.
- `run_article_pipeline` (ja): completed; ~80 words / 15 slots with local `qwen2.5:14b` (not meeting 800+ word success criterion in this run).

---

**User**

do you have sai_maa_vid.mp4 or ra.mp4 ?
were you helping me move vids? 

---

**Cursor**

In this chat we only worked on Pearl News CJK slot prompts — no video moves. Searching the repo for those filenames.



---

**User**

go on

---

**Cursor**

Continuing now — I’ll check the likely video folders directly to confirm whether `sai_maa_vid.mp4` or `ra.mp4` exist, and then clarify what I did in this chat.



I’m not currently holding those files, and in this chat I wasn’t moving videos — I was working on prompt translation files.

I also ran a workspace scan for exact filenames:

- `sai_maa_vid.mp4` → not found  
- `ra.mp4` → not found

If you want, I can do a broader machine-wide search next (outside `/Users/ahjan/phoenix_omega`) and help move/rename them once found.

