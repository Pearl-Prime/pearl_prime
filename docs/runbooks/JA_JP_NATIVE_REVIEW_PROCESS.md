# ja-JP Native-Speaker Review (Manga / Chapter Scripts)

**Owner lane:** Pearl_Localization  
**Applies to:** `chapter_script_writer_handoff` YAML under `artifacts/manga/chapter_scripts/**/ep_*.yaml`  
**Locale keys in YAML:** `ja_JP` (underscore, matches writer handoff conventions). References to **ja-JP** in governance or storefront docs mean the same market locale.

---

## 1. When review is required

| Situation | Native review |
|-----------|----------------|
| **V1 — Tier-1 inline translation** (operator-present or scripted fill of `text_by_locale` / `narrator_caption_by_locale` / `sfx_by_locale` from English, including LLM-assisted) | **Required** before releasing on culturally sensitive surfaces (e.g. **WEBTOON Japan** pilot, domestic JP marketing screenshots, or JP-only lettering proofs). Tracks audit **P0-2**: ship V1 fast, gate publish on native pass. |
| **V2 — revised copy** ( tightened register, typography pass, lettering v3 tweaks, VO/TTS rehearsal ) | **Strongly desirable**; not always a legal blocker but should be scheduled if the episode is evergreen catalog in JP. |

Out of scope for *native manga register* (use other lanes): engine metadata only, filenames, `series_id` slugs.

---

## 2. What the reviewer checks

Deliver feedback as a dated artifact under `artifacts/qa/` (see §4) and optionally inline in the PR.

1. **Genre / audience register**  
   Align copy with intended band: **seinen** (grounded adult tone), **josei** (interior emotional precision), **iyashikei** warmth (solace without infantilizing), and colloquial naturalness versus **novelistic** narration. Mixed modes are OK if **consistent per speaker** (e.g. Tower radio = crisp professional JP; interior monologue = softer colloquial).

2. **敬語・タメ口バランス (polite vs casual)**  
   Dialogue must match speaker relationship and bubble type (`radio_box`, `cloud_thought`, `round_normal`, etc.). Internal monologue typically avoids stiff です・ます堆砌 unless the character voice is deliberately formal.

3. **バブル適合 (lettering / fit)**  
   - Line breaks that work in vertical or horizontal comps (coordinate with design if applicable).  
   - Onomatopoeia (`sfx_by_locale`) feel native; not English morphemes unless intentional style joke.  
   - No overflowing literal translations that break panel rhythm.

4. **Market stigma & wellness lexicon**  
   Follow **`config/localization/content_roots_by_locale.yaml`** ja-JP notes (e.g. avoid heavy “mental health” framing in titles; prefer nervous-system / wellbeing framings where policy requires).

5. **Kanji / kana / loanword choices**  
   Consistent term for recurring motifs (anchors, telemetry, metaphors); readable for target age band.

Unattended Tier-2 pipelines (**Gemma (English) / Qwen (CJK6) on Pearl Star via Ollama**, per CLAUDE.md) must **not** be treated as a substitute for this review when §1 mandates a native gate.

---

## 3. How edits flow back into `chapter_script` YAML

1. Reviewer edits `artifacts/qa/<series>_<episode>_jajp_review_<YYYY-MM-DD>.md` with **before → after** strings keyed by **`panel_id` + speaker field** (or narrator/SFX slot).  
2. Implementer applies changes directly to `text_by_locale` / `narrator_caption_by_locale` / `sfx_by_locale` under **`ja_JP`** in the repo YAML (never replace `en_US` unless correcting source).  
3. Run a quick YAML sanity pass (syntax + unicode). Optional: regenerate downstream artifacts only when the lettering or preview pipeline consumes the script (**coordinate with manga build lane**).  
4. Translator refresh: **`scripts/manga/translate_chapter_script.py`** is for *machine fill from source locale* — use **`--force`** only when intentionally overwriting machine text after review; preserve reviewed strings.  
5. Open PR → CI → merge. Update queue status to **`native_signed_off`** (§5).

---

## 4. SLA and cost guidance

| Mode | SLA (indicative) | Cost notes |
|------|------------------|------------|
| **Operator-led** (trusted native contacts / freelancers on retainer) | **≤ 5 business days** from queue open for WEBTOON-class P0 gates; escalate if blocker. | Usually **\$0–\$200** ep. for light dialogue counts if favors / in-house; track time. |
| **Commissioned linguistic QA** (manga-specialized JP → JP polish) | Agree turnaround in SOW (**rush 24–72h**, standard **~1 week**). | Order-of-magnitude **\$150–\$500** per short episode varies by bubble count and revision rounds; obtain quote. |

Record actual numbers in the tracker **notes** column for forecasting.

---

## 5. Tooling and trackers

| Artifact | Purpose |
|----------|---------|
| `artifacts/qa/native_review_queue_<YYYY-MM-DD>.tsv` | Tab-separated queue: which **series × chapter × locale** needs native review |
| `scripts/localization/queue_native_review.py` | List / add / update rows without hand-editing errors |

Examples:

```bash
python3 scripts/localization/queue_native_review.py list
python3 scripts/localization/queue_native_review.py set-status \\
  --series-id 'warrior_calm_cultivation__master_wu__en_US__burnout__the_chassis_is_listening' \\
  --chapter-id ep_001 --locale ja_JP --status native_signed_off
```

---

## 6. HARD STOP — no reviewer in session

If no ja-JP native reviewer is engaged, Pearl_Localization **ships** this runbook + queue tooling, leaves the episode row in **`pending_native_review`**, and files a dated review artifact stating **Reviewer: TBD** with no claimed linguistic sign-off. Publish to JP storefronts waits on **`native_signed_off`**.
