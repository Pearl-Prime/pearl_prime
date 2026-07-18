# Brand Wizard Translation Specification

## Lessons learned from the Japanese (ja) translation — replication guide for zh-CN and zh-TW

This document captures every mistake, correction, and technique from the 100+ iteration Japanese translation process. Follow this spec exactly to translate into Simplified Chinese (zh) and Traditional Chinese (tw) without repeating the same errors.

---

## 1. USE THE CORRECT SOURCE FILE

**Mistake made:** Started from the wrong BrandWizard.jsx (2842 lines, old version from `claude/dreamy-northcutt`). The correct version is 3605 lines, has 14 step functions, a "Congratulations" page, and a proper `useTranslation()` hook.

**Rule:** The correct source is:
```
/Users/ahjan/phoenix_omega/.claude/worktrees/crazy-clarke/brand-wizard-app/src/BrandWizard.jsx
```
- Branch: `agent/browser-translation-scripts-20260416`
- 3605 lines, 14 step functions
- Has `StepBrandReveal` with "Congratulations" 
- Has `useTranslation()` hook + `I18nProvider`
- Has `VOICE_AUDIO_SRC`, `VOICE_AUDIO_SRC_JA`, `VOICE_AUDIO_SRC_ZH`, `VOICE_AUDIO_SRC_TW` audio maps

**How to verify:** `grep -c "Congratulations" BrandWizard.jsx` should return 2.

---

## 2. ARCHITECTURE: SEPARATE PER-LOCALE JSX FILES

Do NOT rely on runtime `_t()` or `useTranslation()` for the locale versions. Create a **self-contained JSX file** with all text hardcoded in the target language.

**Files to create for each locale:**

| File | Purpose |
|------|---------|
| `BrandWizard-{locale}.jsx` | Full wizard with ALL English replaced by target language |
| `main-{locale}.jsx` | Entry point that imports `BrandWizard-{locale}.jsx` |
| `wizard-{locale}.html` | Points `<script>` to `main-{locale}.jsx` |

**Why:** Runtime i18n failed repeatedly because:
- Components had hardcoded English that bypassed `t()`
- Dynamic template literals couldn't be regex-matched
- Data arrays (ARCHETYPES, VOICE_SLIDERS, etc.) had English in nested objects
- The `t()` function required exact key matches that broke with periods in strings

---

## 3. TRANSLATION PIPELINE — EXACT ORDER OF OPERATIONS

### Step 3.1: Complete the strings-{locale}.json file

The strings JSON uses the English text as the KEY and the translation as the VALUE, nested by category.

**Source:** `strings-en.json` (774 leaf keys across 21 categories)

**Existing partial files:**
- `strings-zh.json` — ~130 keys (very incomplete)
- `strings-tw.json` — ~130 keys (very incomplete)

**Action:** Extract all missing keys, translate them, merge back.

```python
# Extract missing keys
en_flat = flatten(en)  # 774 keys
locale_flat = flatten(locale)
missing = {k: v for k, v in en_flat.items() if k not in locale_flat}
# Translate missing → merge back into strings-{locale}.json
```

**Critical: Fix nested key corruption.** When English strings contain periods (e.g., "Your archetype is...covers, video, and social. Pick the worldview..."), the unflatten step creates broken nested objects like `{"": "translation"}`. After merging, run the fix script:

```python
def fix_nested(d):
    for k, v in list(d.items()):
        if isinstance(v, dict) and len(v) == 1 and "" in v:
            full_key = k
            inner = v
            while isinstance(inner, dict) and len(inner) == 1:
                next_key = list(inner.keys())[0]
                full_key += next_key
                inner = inner[next_key]
            if isinstance(inner, str):
                d[full_key] = inner
                del d[k]
```

**Target:** 0 missing keys. Verify with:
```python
missing = [k for k in en_flat if k not in locale_flat]
assert len(missing) == 0
```

### Step 3.2: Generate BrandWizard-{locale}.jsx via bulk replacement

This is the core step. Read the ENGLISH BrandWizard.jsx and replace every English string with its translation.

**Phase 1 — Long strings (>20 chars):** Safe direct replacement, low collision risk.

```python
for en_str, locale_str in sorted(pairs, key=lambda x: -len(x[0])):
    if len(en_str) > 20 and en_str in content:
        content = content.replace(en_str, locale_str)
```

**Phase 2 — Short strings (3-20 chars):** Only replace inside quotes or JSX text content to avoid breaking variable names.

```python
# Replace "English" → "Translation" (quoted strings)
content = content.replace(f'"{en_str}"', f'"{locale_str}"')
# Replace >English< → >Translation< (JSX text content)
content = content.replace(f'>{en_str}<', f'>{locale_str}<')
```

**What this covers:** ~618 replacements including all UI labels, step titles, sidebar text, archetype names, taglines, emotion names, topic names, tradition names, visual style labels, channel names, format labels, and more.

### Step 3.3: Translate the 40 voice technique descriptions

These are NOT in the strings JSON. They're inside the `VOICE_SLIDERS` data object in BrandWizard.jsx, field name `technique`.

```bash
grep 'technique:' BrandWizard.jsx | sed 's/.*technique: "//' | sed 's/",*//'
```

Produces 40 lines like:
```
Opens with 'You might notice...' — never commands, only observes alongside the reader
Uses permission language: 'It's okay to...' and 'You're allowed to...'
...
```

Translate all 40 to target language. Apply via direct replacement.

### Step 3.4: Translate the 51 feedback strings (systemEffect + emotionalBenefit)

These are in the `SELECTION_FEEDBACK`, `ANGLE_FEEDBACK`, and archetype feedback data objects. They appear in the sidebar when a user selects an archetype/persona/moment.

```python
# Extract
se_matches = re.findall(r'systemEffect: "([^"]+)"', content)
eb_matches = re.findall(r'emotionalBenefit: "([^"]+)"', content)
# Filter English-only
english = [s for s in all_matches if sum(1 for c in s if ord(c) < 128)/len(s) > 0.8]
```

~51 unique strings. Translate and apply via direct replacement.

### Step 3.5: Translate the 17 benefit strings

Inside `VOICE_SLIDERS` position data, field name `benefits`. These are arrays of English strings like:
```
"Higher exercise completion rate — invitations feel safer than commands"
"Audiobook version works as a de-escalation tool during panic moments"
```

Extract with regex, translate, replace.

### Step 3.6: Fix the Brand Reveal dynamic template strings

The Brand Reveal page (StepBrandReveal) has template literals that mix English with JavaScript variables:

| English | Translation pattern |
|---------|-------------------|
| `Your voice is <span>...` | `あなたの声は <span>...` |
| `Rank #${vm.rank}` | `ランク #${vm.rank}` |
| `Combo Score: ${comboScore}` | `コンボスコア: ${comboScore}` |
| `` `Best on ${tm.platform}` `` | `` `${tm.platform} に最適` `` |
| `Open with "${moment.scene}" — your reader's exact moment` | Translate the template, keep `${moment.scene}` |
| `How {persona.emoji} {persona.label} experiences your brand:` | `{persona.emoji} {persona.label} があなたのブランドを体験する流れ：` |
| `Your ${voiceDesc[0]} voice makes them feel ${voiceDesc[2]}...` | Translate surrounding text, keep variables |
| `You are フェニックス・ライジング — a 命令的...` | `あなたは ... — ` (dynamic parts stay) |
| `Step 1` / `Step 2` / `Step 3` / `Step 4` | `ステップ 1` etc. |
| `"Search"` (radar label) | `"検索"` |
| `topics claimed` | locale equivalent |
| `In the System:` / `For Your Reader:` | locale equivalents |
| `F-slight` (demographic label) | locale equivalent |

These are ~20 individual fixes applied via `content.replace()`.

### Step 3.7: Fix the IntroJourney component

This component has hardcoded English that the `useTranslation()` hook was never wired into. The BASE BrandWizard.jsx was already fixed (committed in `fa38937f0e`) to use `t()` calls here. But the BULK REPLACEMENT in step 3.2 should have caught these strings anyway since they're in the `intro` category of the strings JSON.

**Verify after generation:**
```
grep "Foundation\|Voice\|Formats\|Reveal\|How this works\|Five beats\|Start building" BrandWizard-{locale}.jsx
```
Should return 0 results (all replaced).

---

## 4. EMOTION IMAGE MAP — KEY MATCHING

**Mistake made:** The bulk replacement translated emotion names in the `EMOTION_CATEGORIES` data but used a DIFFERENT translation for the same emotion in the image lookup map. Example: category said `"自信がある"` but image map had `"自信が持てる"`.

**Rule:** After generating BrandWizard-{locale}.jsx, run this verification:

```python
# Extract image map keys
img_keys = {match for match in re.findall(r'"([^"]+)":\s*"/onboarding/proof/wizard/emotion_', content)}
# Extract category item names
category_items = set()
for item_str in re.findall(r'items:\s*\[([^\]]+)\]', content):
    category_items.update(re.findall(r'"([^"]+)"', item_str))
# Check for mismatches
for item in category_items:
    if item not in img_keys:
        print(f"MISMATCH: '{item}' not in image map")
```

**Fix:** Make the image map key match the category item exactly.

---

## 5. AUDIO MP3 MAPPING

**Mistake made (3 times):**
1. First used `voice_cmp_comfort_voice_*.mp3` (old files, wrong content)
2. Then used `1p*.mp3` (identical to English `p*.mp3` — same MD5 hash)
3. Then used same `ja_p*.mp3` for ALL 4 sliders instead of per-slider files

**Correct mapping — mirrors the English structure exactly:**

| Slider | EN prefix | JA prefix | ZH prefix | TW prefix |
|--------|-----------|-----------|-----------|-----------|
| gentleDirect | `p` | `ja_p` | `zh_p` | `tw_p` |
| simpleDeep | `sd_p` | `ja_sd_p` | `zh_sd_p` | `tw_sd_p` |
| emotionalLogical | `el_p` | `ja_el_p` | `zh_el_p` | `tw_el_p` |
| spiritualPractical | `sp_p` | `ja_sp_p` | `zh_sp_p` | `tw_sp_p` |

Each slider has 5 positions: `{prefix}1.mp3`, `{prefix}3.mp3`, `{prefix}6.mp3`, `{prefix}8.mp3`, `{prefix}10.mp3`

**= 4 sliders × 5 positions = 20 MP3 files per locale**

**Audio source map in BrandWizard-{locale}.jsx:**
```javascript
const VOICE_AUDIO_SRC_{LOCALE} = {
  gentleDirect: { 1: "/onboarding/proof/wizard/{lc}_p1.mp3", 3: "...p3.mp3", 6: "...p6.mp3", 8: "...p8.mp3", 10: "...p10.mp3" },
  simpleDeep: { 1: "/onboarding/proof/wizard/{lc}_sd_p1.mp3", ... },
  emotionalLogical: { 1: "/onboarding/proof/wizard/{lc}_el_p1.mp3", ... },
  spiritualPractical: { 1: "/onboarding/proof/wizard/{lc}_sp_p1.mp3", ... },
};
```

**Also hardcode the selection:** `const audioSrc = VOICE_AUDIO_SRC_{LOCALE};` — don't use runtime locale detection.

**Verify files exist:**
```bash
for prefix in zh_p zh_sd_p zh_el_p zh_sp_p; do
  for n in 1 3 6 8 10; do
    [ -f "public/onboarding/proof/wizard/${prefix}${n}.mp3" ] || echo "MISSING: ${prefix}${n}.mp3"
  done
done
```

The MP3 files already exist at:
```
/Users/ahjan/phoenix_omega/brand-wizard-app/dist/onboarding/proof/wizard/
```
Copy them to the crazy-clarke worktree's `public/onboarding/proof/wizard/`.

---

## 6. ENTRY POINT WIRING

### main-{locale}.jsx
```jsx
import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import BrandWizard from "./BrandWizard-{locale}.jsx";
import { I18nProvider } from "./i18n.jsx";
import strings from "./strings-{locale}.json";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <I18nProvider locale="{locale}" strings={strings}>
      <BrandWizard />
    </I18nProvider>
  </React.StrictMode>
);
```

### wizard-{locale}.html
Change: `<script type="module" src="/src/main-{locale}.jsx"></script>`

### vite.config.js
Already has all 4 entry points. No changes needed.

---

## 7. BUILD AND VERIFICATION CHECKLIST

### Build
```bash
cd brand-wizard-app
npm run build
```

**Expected output:** Separate bundles per locale:
```
dist/assets/wizard-ja-XXXX.js   ~166 KB
dist/assets/wizard-zh-XXXX.js   ~166 KB  (NEW)
dist/assets/wizard-tw-XXXX.js   ~166 KB  (NEW)
dist/assets/main-XXXX.js        ~154 KB  (English)
```

### Smoke test each bundle
```bash
# ZH bundle has Simplified Chinese
grep "步骤" dist/assets/wizard-zh*.js && echo "✅ ZH"
# TW bundle has Traditional Chinese  
grep "步驟" dist/assets/wizard-tw*.js && echo "✅ TW"
# No cross-contamination
grep "ステップ" dist/assets/wizard-zh*.js && echo "❌ JA leaked into ZH"
```

### Screen-by-screen browser verification

For EACH screen, take a screenshot and verify zero English:

1. **Landing page** — hero, subtitle, icon labels, CTA button, footer link
2. **Journey overview** — eyebrow, title, subtitle, 5 phase labels + subtitles, CTA
3. **Step 1 (Archetype)** — progress bar ("步骤 1 / 9"), eyebrow, title, subtitle, helper, tip callout, sidebar (studio insight, brand defined), ALL archetype cards (name, tagline, visionVibe, tags)
4. **Step 2 (Primary Reader)** — persona cards (label, desc, needs), lane selector, market selector
5. **Step 3 (Trigger Moment)** — moment cards (label, scene, hookStyle)
6. **Step 4 (Voice Tone)** — slider labels (left/right), descriptions, position names (e.g., "バランス・直接的"), position number ("ポジション 6 / 10"), listen button, technique descriptions, radar chart labels, **PLAY AUDIO — verify it plays locale language, not English**
7. **Step 5 (Visual Style)** — style cards (label, desc, mood), emotion image picker
8. **Step 6 (Emotional Outcomes)** — category names + icons, ALL emotion items with images, impact descriptions. **CHECK: every emotion image loads (no broken images)**
9. **Step 7 (Topics)** — category headers, topic names, angle descriptions
10. **Step 8 (Brand Reveal / Congratulations)** — "おめでとうございます" banner, true category, voice signature, positioning map labels, visual identity, market scores, content engine steps (ステップ 1-4 with descriptions), advantage loop, reader experience staircase, voice×topic synergy, brand strength radar, brand synthesis
11. **Step 9 (Launch)** — form labels, section headers, field placeholders, messaging channels, activate button, secure process note

### Specific checks per screen:

**Sidebar (visible on every wizard step):**
- "スタジオの洞察" (not "Studio Insight")
- "ブランド確定" (not "Brand Defined")
- "これが変えること" (not "What this changes")
- Voice Profile slider labels all translated
- When archetype/persona/moment is selected: systemEffect and emotionalBenefit text must be in target language

**Audio (Step 4):**
- Click "Listen to position" on each slider
- Audio must play in the target language
- Each of the 4 sliders should play DIFFERENT audio (not all the same file)

**Emotion images (Step 6):**
- All 15 emotion items must show their image
- If any image is missing → the image map key doesn't match the category item name

---

## 8. DEPLOY

```bash
# Build
npm run build

# Deploy to production
eval "$(python3 ../../scripts/ci/load_integration_env_from_keychain.py)"
npx wrangler pages deploy dist --project-name brand-admin-onboarding --branch main

# Verify production URL
curl -sL "https://brand-admin-onboarding-bu2.pages.dev/wizard-zh.html" | grep "src=.*wizard-zh"
```

---

## 9. FILES CHECKLIST

For ZH (Simplified Chinese), create/modify:

| File | Action |
|------|--------|
| `src/strings-zh.json` | Complete to 900+ keys (currently ~130) |
| `src/BrandWizard-zh.jsx` | Generate via bulk EN→ZH replacement |
| `src/main-zh.jsx` | Create (same pattern as main-ja.jsx) |
| `wizard-zh.html` | Update script src to `/src/main-zh.jsx` |
| Copy `zh_p*.mp3`, `zh_sd_p*.mp3`, `zh_el_p*.mp3`, `zh_sp_p*.mp3` | Into `public/onboarding/proof/wizard/` |

Same for TW (Traditional Chinese) with `tw_` prefix.

---

## 10. COMMON MISTAKES TO AVOID

1. **Don't use runtime i18n for locale versions.** Hardcode everything. The `t()` function is a fallback, not the primary mechanism.
2. **Don't use the same MP3 for all 4 sliders.** Each slider (gentleDirect, simpleDeep, emotionalLogical, spiritualPractical) has its own set of 5 files.
3. **Don't assume `1p*.mp3` is Japanese.** Verify with `md5` hash comparison — `1p1.mp3` was identical to `p1.mp3` (English).
4. **Don't skip the emotion image key verification.** The bulk replacement can translate the same English word differently in different contexts, causing image lookup mismatches.
5. **Don't forget the Brand Reveal template strings.** They contain `${variable}` interpolation mixed with English text — both parts need translating, but the variables must stay intact.
6. **Don't forget the 40 voice technique descriptions.** They're not in the strings JSON — they're inline in the VOICE_SLIDERS data.
7. **Don't forget the 51 feedback strings.** systemEffect and emotionalBenefit in the sidebar activation panel.
8. **Don't deploy without checking the audio plays the right language.** Click the play button on each slider and listen.
9. **Don't trust the strings JSON structure after merging.** Periods in English keys create broken nested objects. Run the fix_nested() script after every merge.
10. **Don't work from a stale branch.** Always verify the source file has "Congratulations" and 3605 lines before starting.

---

## 11. POST-GENERATION HARDCODED ENGLISH PATTERNS (DISCOVERED APRIL 2026)

After generating BrandWizard-{locale}.jsx via bulk replacement, **these patterns survive unfixed** because they use JavaScript expressions, not string literals. The bulk replacer cannot catch them. **Every locale file must be patched manually after generation.**

Run these grep checks on the generated file and fix every hit:

```bash
grep -n "catching them at\|In the System\|For Your Reader\|Open with\|shift their self-story\|Use.*angles to\|Deliver.*tonight\|Deliver.*immediately\|Every piece ends\|They start to feel\|voice makes them feel\|You directly\|deliver one promise\|Best on \|gently\|directly\|clearly\|voice that catches\|at their.*moment" BrandWizard-{locale}.jsx
```

### 11.1 Pattern: TOPIC TAG BUTTONS — raw id displayed instead of label

**Location:** `StepTopicsV2` component, inside `cat.tags.map()` renderer

**English source:**
```jsx
<span>{tag.id.replace(/-/g, " ")}</span>
```

**Problem:** Topic tag IDs like `anxiety-at-night`, `burnout-recovery` are displayed raw. The bulk replacer doesn't touch `.id` property values in data arrays.

**Fix:** Add a `label` field to every tag in `TOPIC_CATEGORIES`, then use it:

```jsx
// In each tag object:
{ id: "anxiety-at-night", label: "夜の不安", angle: "framework", bullet: "..." }

// In renderer:
<span>{tag.label || tag.id.replace(/-/g, " ")}</span>
```

**Full label maps per locale** (26 topics × 3 locales):

| id | JA | ZH | TW |
|----|----|----|-----|
| anxiety-at-night | 夜の不安 | 夜间焦虑 | 夜間焦慮 |
| overthinking / 考えすぎ / 过度思虑 / 過度思考 | (already CJK id) | (already CJK id) | (already CJK id) |
| panic-grounding | パニックグラウンディング | 恐慌接地 | 恐慌接地 |
| sunday-dread | 日曜の憂鬱 | 周日恐惧 | 週日恐懼 |
| burnout-recovery | 燃え尽き回復 | 职业倦怠恢复 | 職業倦怠恢復 |
| nervous-system-reset | 神経系リセット | 神经系统重置 | 神經系統重置 |
| decision-fatigue | 決断疲れ | 决策疲劳 | 決策疲勞 |
| phone-addiction | スマホ依存 | 手机成瘾 | 手機成癮 |
| grief-timeline | 悲しみのタイムライン | 悲伤时间线 | 悲傷時間線 |
| toxic-relationship-healing | 有害な関係からの癒し | 有毒关系疗愈 | 有毒關係療癒 |
| intergenerational-trauma | 世代間トラウマ | 代际创伤 | 代際創傷 |
| heartbreak-recovery | 失恋からの回復 | 心碎恢复 | 心碎恢復 |
| emotional-numbness | 感情の麻痺 | 情感麻木 | 情感麻木 |
| feeling-behind | 遅れている感覚 | 感觉落后 | 感覺落後 |
| quarter-life-crisis | クォーターライフクライシス | 四分之一人生危机 | 四分之一人生危機 |
| identity-rebuild | アイデンティティの再構築 | 身份重建 | 身份重建 |
| purpose-after-30 | 30代以降の目的 | 30岁后的人生意义 | 30歲後的人生意義 |
| habit-building | 習慣形成 | 习惯养成 | 習慣養成 |
| ADHD-productivity | ADHD生産性 | ADHD效率 | ADHD效率 |
| dopamine-detox | ドーパミンデトックス | 多巴胺排毒 | 多巴胺排毒 |
| deep-work | ディープワーク | 深度工作 | 深度工作 |
| meditation-beginners | 瞑想入門 | 冥想入门 | 冥想入門 |
| meaning-after-loss | 喪失後の意味 | 失去后的意义 | 失去後的意義 |
| spiritual-no-religion | 宗教なきスピリチュアリティ | 无宗教灵性 | 無宗教靈性 |
| inner-peace-chaos | 混沌の中の内なる平和 | 混乱中的内心平静 | 混亂中的內心平靜 |
| mindfulness-skeptics | マインドフルネス懐疑派 | 对正念持怀疑态度者 | 對正念持懷疑態度者 |

**Note:** Some tags have CJK ids already (e.g., `考えすぎ`, `过度思虑`, `過度思考`). These still need `label` fields matching their ids, otherwise the fallback `id.replace(/-/g, " ")` still works for them.

---

### 11.2 Pattern: TOPIC TAG in SIDEBAR — raw selectedTagId

**Location:** Sidebar renderer, inside `step === 6` block (internal step, displays on Topics page)

**English source:**
```jsx
<span>{angleInfo?.label}: {selectedTagId.replace(/-/g, " ")}</span>
```

**Fix:**
```jsx
<span>{angleInfo?.label}: {(cat.tags.find(t => t.id === selectedTagId)?.label) || selectedTagId.replace(/-/g, " ")}</span>
```

---

### 11.3 Pattern: TOPIC TAG in BRAND REVEAL sidebar — p.tagId.replace

**Location:** `StepBrandReveal` component, in `topicAnglePairs.map()` — two occurrences

**English source:**
```jsx
const topicAnglePairs = topics.map(tagId => {
  const found = cat.tags.find(t => t.id === tagId);
  if (found) return { tagId, angle: found.angle, ... };
```
```jsx
<span>{p.tagId.replace(/-/g, " ")}</span>       // in topic×angle table
<strong>{p.tagId.replace(/-/g, " ")}</strong>    // in voice×topic synergy section
```

**Fix — two parts:**

1. Add `tagLabel` when building pairs:
```jsx
if (found) return { tagId, tagLabel: found.label || found.id.replace(/-/g, " "), angle: found.angle, ... };
```

2. Replace all `p.tagId.replace(/-/g, " ")` → `p.tagLabel`

---

### 11.4 Pattern: SIDEBAR LABELS "In the System" / "For Your Reader"

**Location:** Sidebar, steps 1–4 (`step === 0`, `step === 1`, `step === 2`, `step === 3` in internal numbering)

**English source:**
```jsx
<strong>In the System:</strong> {_SF.archetypes[arch.id].systemEffect}
<strong>For Your Reader:</strong> {_SF.archetypes[arch.id].emotionalBenefit}
```
(Appears 4 times — for archetypes, personas, moments, visualStyles)

**Fix per locale:**
| Locale | "In the System:" | "For Your Reader:" |
|--------|-----------------|-------------------|
| JA | 在システム： | 読者へ： |
| ZH | 系统效果： | 读者感受： |
| TW | 系統效果： | 讀者感受： |

```bash
# Quick fix script:
sed -i 's/<strong>In the System:<\/strong>/<strong>系统效果：<\/strong>/g' BrandWizard-zh.jsx
sed -i 's/<strong>For Your Reader:<\/strong>/<strong>读者感受：<\/strong>/g' BrandWizard-zh.jsx
```

**Note:** The `SelectionFeedback` component (used on Step 5/formats) has its own inline labels "在系统中" / "对你的读者" — these are already in the component body and get replaced by the bulk replacer. Only the 4 direct `<strong>` usages in the sidebar need manual fixing.

---

### 11.5 Pattern: BRAND REVEAL — "catching them at"

**Location:** `StepBrandReveal`, `trueCategory` derived string

**English source:**
```jsx
? `${arch.name} for ${persona.label}${moment ? ` — catching them at "${moment.label}"` : ""}`
```

**Fix per locale:**
| Locale | Translation |
|--------|------------|
| JA | `` ` — ${moment.label}の瞬間を捉える` `` |
| ZH | `` ` — 捕捉他们在「${moment.label}」的时刻` `` |
| TW | `` ` — 捕捉他們在「${moment.label}」的時刻` `` |

---

### 11.6 Pattern: CONTENT ENGINE STEPS — "Use debunk angles to shift their self-story" / "Deliver a framework"

**Location:** `engineSteps` array in `StepBrandReveal`

**English source:**
```jsx
{ step: "...", desc: `Use ${uniqueAngles.includes("debunk") ? "debunk" : ...} angles to shift their self-story` }
{ step: "...", desc: `Deliver ${uniqueAngles.includes("framework") ? "a framework they can use tonight" : "an actionable insight they can apply immediately"}` }
{ step: "...", desc: `Every piece ends at: "${emotions[0]}"` }
```

**Fix:** Translate the surrounding English, keep `${...}` variables. The angle name inside the ternary should reference `_AF[...].label` (already localized) or be inlined as translated strings.

Example for JA:
```jsx
{ step: "アイデンティティを再定義する", desc: `${uniqueAngles.includes("debunk") ? "誤解を正す" : uniqueAngles.includes("reveal") ? "お披露目" : "根源を辿る"}のアングルで自己ナラティブを書き換える` }
{ step: "マイクロツールを渡す", desc: `${uniqueAngles.includes("framework") ? "今夜から使えるフレームワークを提供する" : "すぐ実践できる行動的な洞察を渡す"}` }
{ step: "感情に着地する", desc: emotions.length > 0 ? `最後は必ずこの感情に着地する：「${emotions[0]}」` : "すべてのコンテンツが約束した感情で終わる" }
```

---

### 11.7 Pattern: VOICE×TOPIC SYNERGY — "gently/directly/clearly" + "You directly [angle] [topic]"

**Location:** Voice×topic synergy section in `StepBrandReveal`

**English source:**
```jsx
const toneWord = gentlePos <= 3 ? "gently" : gentlePos >= 8 ? "directly" : "clearly";
...
You <strong>{toneWord}</strong> {af?.label?.toLowerCase()} <strong>{p.tagLabel}</strong>
```

**Fix per locale:**

| Locale | gently | directly | clearly | Sentence structure |
|--------|--------|----------|---------|-------------------|
| JA | やさしく | 直接的に | 明確に | `あなたは{toneWord}{af?.label}する {p.tagLabel}` |
| ZH | 温柔地 | 直接地 | 清晰地 | `您以{toneWord}的语调进行{af?.label} {p.tagLabel}` |
| TW | 溫柔地 | 直接地 | 清晰地 | `您以{toneWord}的語調進行{af?.label} {p.tagLabel}` |

---

### 11.8 Pattern: BRAND SYNTHESIS — "a voice that catches...at their...moment"

**Location:** Final synthesis sentence in `StepBrandReveal` (last card, deep violet background)

**English source:**
```jsx
あなたは <strong>{arch.name}</strong> — a {voiceDesc[0]}, {voiceDesc[1]} voice that catches{" "}
<strong>{persona.label}</strong>
{moment && <> at their <em>{moment.label.toLowerCase()}</em> moment</>},{" "}
{uniqueAngles.length > 0 && <>uses {uniqueAngles.map(a => _AF[a]?.label?.toLowerCase()).join(" + ")} angles to</>}{" "}
{emotions.length > 0
  ? <>deliver one promise: <strong>"{emotions[0]}"</strong></>
  : <>deliver transformation</>
}.
```

**Fix per locale:**

JA:
```jsx
あなたは <strong>{arch.name}</strong> — {voiceDesc[0]}で{voiceDesc[1]}な声が、{" "}
<strong>{persona.label}</strong>
{moment && <>の<em>「{moment.label}」</em>の瞬間を捉え</>}、{" "}
{uniqueAngles.length > 0 && <>{uniqueAngles.map(a => _AF[a]?.label).join(" + ")}のアングルで</>}{" "}
{emotions.length > 0
  ? <>一つの約束を届ける：<strong>「{emotions[0]}」</strong></>
  : <>変容を届ける</>
}。
```

ZH:
```jsx
你是 <strong>{arch.name}</strong> — 以{voiceDesc[0]}、{voiceDesc[1]}的语调，捕捉{" "}
<strong>{persona.label}</strong>
{moment && <>在他们<em>「{moment.label}」</em>时刻</>}，{" "}
{uniqueAngles.length > 0 && <>运用 {uniqueAngles.map(a => _AF[a]?.label).join(" + ")} 的切角</>}{" "}
{emotions.length > 0
  ? <>传递一个承诺：<strong>「{emotions[0]}」</strong></>
  : <>带来蜕变</>
}。
```

TW:
```jsx
你是 <strong>{arch.name}</strong> — 以{voiceDesc[0]}、{voiceDesc[1]}的語調，捕捉{" "}
<strong>{persona.label}</strong>
{moment && <>在他們<em>「{moment.label}」</em>時刻</>}，{" "}
{uniqueAngles.length > 0 && <>運用 {uniqueAngles.map(a => _AF[a]?.label).join(" + ")} 的切角</>}{" "}
{emotions.length > 0
  ? <>傳遞一個承諾：<strong>「{emotions[0]}」</strong></>
  : <>帶來蛻變</>
}。
```

**Key change:** Use `_AF[a]?.label` (already translated) instead of `_AF[a]?.label?.toLowerCase()` — the `.toLowerCase()` method mangles CJK text.

---

### 11.9 Pattern: EMOTION IMAGE MAP — Missing entries for "Energy & Confidence" category

**Location:** `EMOTION_PROOF_URL` const (around line 231)

**Problem:** The bulk replacer translated EMOTION_CATEGORIES item names correctly, but the image map keys were generated from English and mapped to wrong PNG files. Example: TW had `"釋放"` pointing to `emotion_energized.png` (wrong), and `"充滿活力"` was missing entirely.

**Full correct mapping (15 emotions → 15 PNG files):**

| English concept | PNG filename | JA | ZH | TW |
|----------------|-------------|----|----|-----|
| Finally calm | emotion_finally_calm.png | 終わりにやっと落ち着く | 终于平静 | 終於平靜 |
| Safe in body | emotion_safe_in_body.png | 身体の中で安全 | 在身体里感到安全 | 在身體裡感到安全 |
| Permission to rest | emotion_permission_rest.png | 休んでいいという許可 | 允许自己休息 | 允許自己休息 |
| Clear headed | emotion_clear_headed.png | 頭が澄んでいる | 头脑清晰 | 頭腦清晰 |
| In control | emotion_in_control.png | 自分でコントロールできている | 掌控感 | 掌控感 |
| Connected to purpose | emotion_connected_purpose.png | 目的とつながっている | 与目标相连 | 與目標相連 |
| Energized | emotion_energized.png | エネルギーが湧いている | 充满活力 | 充滿活力 |
| Confident | emotion_confident.png | 自信がある / 自信 | 自信 | 自信 |
| Resilient | emotion_resilient.png | 回復力がある / 有韌性 | 有韧性 | 有韌性 |
| Released | emotion_released.png | 解放された | 释放 | 釋放 |
| Forgiven | emotion_forgiven.png | 許された気持ちになれる | 被宽恕 | 被寬恕 |
| Less alone | emotion_less_alone.png | 孤独じゃない | 不再孤单 | 不再孤單 |
| Grounded | emotion_grounded.png | 地に足がついている | 脚踏实地 | 腳踏實地 |
| Hopeful | emotion_hopeful.png | 希望に満ちている | 充满希望 | 充滿希望 |
| Present | emotion_present.png | 今ここにいられる | 活在当下 | 活在當下 |

**Verification script:**
```python
import re
with open("BrandWizard-{locale}.jsx") as f:
    content = f.read()

img_keys = set(re.findall(r'"([^"]+)":\s*"/onboarding/proof/wizard/emotion_', content))
items = set(re.findall(r'"([^"、。，]+)"(?=,|\s*\])', 
    '\n'.join(re.findall(r'items:\s*\[([^\]]+)\]', content))))

missing = [i for i in items if i not in img_keys and len(i) > 1]
print("MISSING from image map:", missing)
```

---

## 12. YAML DOWNLOAD FLOW (as of April 2026)

The YAML is generated on the **Launch page** (Step 9 of 9), **not** the Congratulations page.

**Flow:**
1. User fills in name, email, messaging channels
2. Clicks "Activate" button → `handleLaunch()` fires
3. `handleLaunch()` calls `generateYAML(state)`, triggers browser file download immediately
4. Page transitions to Congratulations

**File naming:** `{firstName}-brand-config.yaml` (lowercased, spaces→hyphens)

**YAML includes:**
- `brand_admin:` block with first_name, last_name, email, phone, messaging channels (LINE, WhatsApp, WeChat, FB Messenger, preferred_channel)
- Full brand state: archetype, persona, moment, visual_style, voice_settings, emotions, topic_tags, format_focus, channels
- Generated content: voice_signature, true_category, topic_angle_strategy, content_engine_steps

**No server needed.** Pure client-side Blob download. Works on any device anywhere.

---

## 13. INTRO PRESENTATION TRANSLATION CHECKLIST

The IntroJourney component (landing page shown before Step 1) needs the same treatment. Strings to translate:

### 13.1 Static text (covered by bulk replacer if in strings JSON)
- Hero eyebrow: "Pearl Prime Brand Studio"
- Hero title: "Launch and shape your publishing brand"
- Hero subtitle: "One guided session — voice, look, and proof aligned."
- 4 icon labels: "VOICE", "VISUAL", "READER", "FORMATS"
- CTA button: "Start building"
- Session note below CTA: "Takes 15–20 minutes · Save your YAML at the end"

### 13.2 5 Journey phases (in IntroJourney component)
Each phase has: `title`, `subtitle`, `icon`

| Phase | EN title | EN subtitle |
|-------|----------|------------|
| 1 | Foundation | Choose your archetype, reader, and trigger moment |
| 2 | Voice | Dial in tone — from gentle to direct, simple to layered |
| 3 | Visual | Pick mood, style, and the emotional outcomes you deliver |
| 4 | Formats | Choose channels, formats, and launch context |
| 5 | Reveal | See your full brand blueprint + YAML export |

### 13.3 How to verify IntroJourney is translated
```bash
grep "Foundation\|Voice\|Formats\|Reveal\|How this works\|Five beats\|Start building\|VOICE\|VISUAL\|READER\|FORMATS\|One guided session" BrandWizard-{locale}.jsx
```
Should return 0 English results. If any hit → check strings JSON has the key and the bulk replacer applied it.

### 13.4 Common issue: "VOICE" / "VISUAL" / "READER" / "FORMATS" not translated
These 4 labels are short (4–7 chars) and uppercase. The bulk replacer Phase 2 only replaces inside `"quotes"` or `>JSX text<`. Verify the strings JSON has them and they appear in the right pattern:
```jsx
// If in JSX text:
>VOICE<  →  >ボイス<
// If in quoted prop:
label="VOICE"  →  label="ボイス"
```

---

## 14. MASTER CHECKLIST FOR NEXT LOCALE

Run this checklist top-to-bottom for any new locale (KO, ES, PT, etc.):

- [ ] Source file is correct: `BrandWizard.jsx` in `crazy-clarke`, 3605+ lines, has "Congratulations"
- [ ] `strings-{locale}.json` has 0 missing keys vs `strings-en.json`
- [ ] fix_nested() run after JSON merge (no broken `{"": "value"}` objects)
- [ ] Bulk replacement Phase 1 (>20 chars) applied
- [ ] Bulk replacement Phase 2 (3-20 chars, quoted+JSX patterns) applied
- [ ] 40 voice technique descriptions translated
- [ ] 51 feedback strings (systemEffect + emotionalBenefit) translated  
- [ ] 17 benefit strings translated
- [ ] TOPIC_CATEGORIES: all 26 tag objects have `label` field (§11.1)
- [ ] Button renderer uses `tag.label ||` (§11.1)
- [ ] Sidebar topic renderer uses `cat.tags.find(...).label ||` (§11.2)
- [ ] `topicAnglePairs` builds `tagLabel` field (§11.3)
- [ ] All `p.tagId.replace` → `p.tagLabel` (§11.3)
- [ ] Sidebar "In the System:" / "For Your Reader:" replaced (§11.4)
- [ ] "catching them at" → locale (§11.5)
- [ ] Content engine steps 2+3+4 template literals → locale (§11.6)
- [ ] `toneWord` gently/directly/clearly → locale (§11.7)
- [ ] "You directly [angle] [topic]" sentence → locale (§11.7)
- [ ] Brand synthesis sentence fully localized (§11.8)
- [ ] EMOTION_PROOF_URL has all 15 entries, keys match category items (§11.9)
- [ ] Audio map hardcoded with correct locale prefix for all 4 sliders × 5 positions
- [ ] `main-{locale}.jsx` created, `wizard-{locale}.html` points to it
- [ ] `vite.config.js` has entry point (already wired for ja/zh/tw)
- [ ] `npm run build` succeeds, bundle size ~150-170 KB
- [ ] `grep "ステップ\|步骤\|步驟" dist/assets/wizard-{locale}*.js` returns locale strings
- [ ] Zero English in topic buttons (screen check Step 7)
- [ ] Zero English in sidebar at every step (sidebar check)
- [ ] Zero English on Brand Reveal page (screen check Step 8)
- [ ] Audio plays correct language on each slider (Step 4 audio check)
- [ ] All 15 emotion images load (Step 6 image check)
- [ ] YAML downloads on Activate click with contact info included
- [ ] IntroJourney/landing page fully translated (§13)
- [ ] `npx wrangler pages deploy dist/ --project-name phoenix-command`
