# Music Mode — Anxiety & Overwhelm Family Pilot Packet

**Status:** authored candidate (manual pilot; generator engine not required)  
**Family SSOT:** `anxiety_and_overwhelm` in `config/music/song_kit_topic_families.yaml`  
**Date:** 2026-07-10  
**Audience:** musician / Brand Director (musician-neutral; not tied to a named external artist)  
**Acceptance layer:** authored candidate — not generator-built, not MusicGen-rendered, not YouTube-wired  
**Project:** `PRJ-MUSIC-ONBOARDING-SONG-KIT-V1`  
**Workstream:** `ws_pearl_editor_pearl_writer_anxiety_overwhelm_family_pilot_20260710`

---

## 0. How to use this packet

This is a **smallest-safe-batch** musician-facing kit for one song-kit family. It tells you what to write, sing, or play for anxiety / overwhelm work **before** the survey→generator engine ships.

| You are… | Use… |
|---|---|
| A lyric musician (folk / rock / singer-songwriter) | §4 English lyrics + §7 melody-fit notes |
| A Japanese-native lyric musician | §5 Japanese-native lyrics (not EN translations) |
| Crystal bowls / light-language / “la-la-la” / instrumental | §6 no-lyrics performance briefs (text direction only; no audio render in V1) |
| Posting Shorts / TikTok | The 90-second pieces in §4–§6 + CTA in §8 |

**Out of scope for this packet:** generator code, MusicGen WAV render, YouTube API upload, new topic_ids, new freebie types, persona-specific branching, all-eight-family cascade.

---

## 1. Why this family exists

`anxiety_and_overwhelm` is one of eight additive song-kit **family labels** over existing canonical topics. It is a routing/authoring aid — not a new topic taxonomy.

**Topic anchors (reuse only; do not mint):**

- `anxiety`
- `social_anxiety`
- `relationship_anxiety`

One family covers multiple subtopics **without persona branching** because the shared mechanism is the same:

> The body runs a protective alarm. The mind attaches a story. The song meets the alarm as signal — not as a character flaw — and offers a steadier rhythm the listener can borrow.

| Subtopic flavor | What the song can hold without rewriting the kit |
|---|---|
| General anxiety / overwhelm | Static in the ears; racing mind meeting a steadier pulse; “you are not your alarm” |
| Social anxiety | Scanning faces / exits; the send button; the room that got small |
| Relationship anxiety | Waiting for the reply; gripping the thread; love that does not need constant proof |

Musicians pick one concrete scene from their life (or a listener’s life) and keep the **register** from the family SSOT:

- **Lyric register hint:** honest about intensity but de-escalating; meet anxiety as signal, not character flaw.
- **Instrumental mood hint:** begins taut, resolves toward calm; gentle downward contour; tempo ~66–78 BPM settling lower; no jump-scares.

---

## 2. Pearl Prime vibe (distilled for musicians)

Grounded in Pearl Prime therapeutic assembly — not motivational slogans, not “just breathe and win.”

### 2.1 Somatic grounding

Start in the body, not the diagnosis. Chest coil. Jaw set. Thumb on the trackpad. Static in the ears. Name the sensation before the story.

### 2.2 Story / recognition

Give the listener a screenshot-worthy “this is me” moment: the message delivered, the reply not back, the hand already on the phone. Recognition first; teaching second.

### 2.3 Compassionate reframing

Anxiety is a protective alarm that once kept someone safe. The alarm can fire when danger is social or imagined. The body cannot always tell the difference. That is not a moral failure.

### 2.4 Second-person reader care

Address the listener as **you**. Do not impersonate a guru. Do not shame. Hold the seam between sensation and story: *Something rises. Then the story arrives. They are not the same thing.*

### 2.5 Non-shaming tone

No “fix your mindset.” No triumph arcs that erase the intensity. De-escalate. Offer one small lived proof — delivered, unanswered, and you are still here.

**Working chorus seed (register, not mandatory lyric):**  
*You are not your alarm / you are the one who hears it.*

---

## 3. DISCOVERY REPORT (lane record)

1. **Open-PR / sibling-lane deconfliction:** No open PR owns `artifacts/programs/music_mode_v2_20260611/*` or `config/music/*` for this family pilot. Open PRs #5515 / #5295 / #5237 / #5206 touch shared coordination TSVs only; this lane appends a narrow new ws + registry + OPD rows without claiming generator/YouTube surfaces.
2. **`PRJ-MUSIC-ONBOARDING-SONG-KIT-V1`:** still **proposed** on live main. Four child ws rows remain **proposed** (generator, lyric/mood engine, Ahjan reference kit, YouTube freebie wiring). None is a manual one-family content pilot → **new narrow ws** opened (not a narrowing of generator/Ahjan/YT rows).
3. **Execution substrate:** `EXECUTION_MODE=local_fallback`; `BACKGROUND_SAFE=no`; `RUNTIME_HOST=operator local Codex workspace`; `PERSISTENCE_SURFACES=feature branch + PR + committed repo artifacts`; `RESUME_SURFACE=pushed remote branch / PR URL`. **`docs/specs/AGENT_EXECUTION_FABRIC_V1_SPEC.md` and `docs/runbooks/CLOUD_FIRST_LOCAL_FALLBACK_AGENT_RUNBOOK.md` are absent on live `origin/main`** — conservative substrate rules used; those docs are not treated as landed.
4. **Reuse-first artifact decision:** Intro deck + long-form are overview assets. No existing per-family musician-facing content packet exists → **new canonical artifact justified** (`NEW-ARTIFACT-JUSTIFIED` below).
5. **Pearl Prime vibe sources read:** `artifacts/qa/snapshots/CANONICAL_FLAGSHIP_CH1.txt`; overlay craft sections in `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` (therapeutic register, Orient/Name, SCENE second-person); `SOURCE_OF_TRUTH/musician_banks/test_artist_alpha/approved_atoms/LYRIC_OPENING/lo_01.yaml`; sample `SOURCE_OF_TRUTH/teacher_banks/ahjan/` HOOK/COMPRESSION; music intro long-form; song-kit + freebie specs.
6. **8-family SSOT confirmed:** `recovery_and_repair`, `quiet_courage`, `presence_and_stillness`, `anxiety_and_overwhelm`, `grief_and_letting_go`, `self_worth_and_shame`, `connection_and_belonging`, `hope_and_renewal`.
7. **Scope lock:** this lane authors **only** `anxiety_and_overwhelm` — not all eight.

`NEW-ARTIFACT-JUSTIFIED:` Intro deck / long-form are overview onboarding assets. This file is the first reusable **per-family** musician-facing content packet (lyrics + no-lyrics briefs + CTA) and must remain a singleton amend-in-place surface under `artifacts/programs/music_mode_v2_20260611/`.

---

## 4. English lyrics

### 4.1 Five-minute English lyric — “Not Your Alarm”

**Form:** verse / chorus / verse / chorus / bridge / chorus (folk–rock friendly)  
**Feel:** starts taut; settles; ~70 BPM feel; singable on acoustic or clean electric  
**Original work:** yes — not dependent on any copyrighted tune

**[Verse 1]**  
You sent it — delivered, done —  
but your hand is back on the phone.  
Chest didn’t get the receipt.  
Four minutes feel like a year alone.

Thumb on the glass, jaw set tight,  
scanning a room that isn’t here.  
The body learned to watch the night  
because watching once kept you clear.

**[Chorus]**  
You are not your alarm.  
You are the one who hears it.  
Let the static be a weather report —  
not a verdict on your spirit.  
Breathe once where the story starts.  
Name the heat before the harm.  
Hold the seam with both your hands —  
you are not your alarm.

**[Verse 2]**  
Something rises — pulse, a wave —  
almost neutral, almost fact.  
Then the story rushes in:  
*this will ruin you, don’t look back.*

But the sensation came in first.  
The story learned to run on cue.  
You don’t have to marry every fear  
that knocks the door and talks like truth.

**[Chorus]**  
You are not your alarm.  
You are the one who hears it.  
Let the static be a weather report —  
not a verdict on your spirit.  
Breathe once where the story starts.  
Name the heat before the harm.  
Hold the seam with both your hands —  
you are not your alarm.

**[Bridge]**  
Social room, soft lights, exits counted —  
or a love-thread left on read —  
same old scanner in the ribs,  
same old story in the head.  
One small proof: the world moved on,  
and you are still here in your skin.  
Not fixed. Not finished. Just not alone  
inside the ringing.

**[Final chorus — softer, then steady]**  
You are not your alarm.  
You are the one who hears it.  
Meet the signal, skip the shame —  
give the night a steadier rhythm.  
Breathe once where the story starts.  
Name the heat before the harm.  
Hold the seam with both your hands —  
you are not your alarm.

---

### 4.2 Ninety-second English lyric (TikTok / Shorts) — “Scroll-Stop: Static”

**Hard rule:** first ~3 seconds must stop the scroll.  
**Target length:** ~90 seconds sung (~12–16 lines + short tag).  
**Original work:** yes.

**[0:00–0:03 — cold open / scroll-stop]**  
*(spoken or half-sung, close mic)*  
**Your chest is louder than the room.**

**[0:03–0:25]**  
You sent it. Delivered. Done.  
Hand’s already back on the phone.  
Four minutes. No reply.  
And the scanner calls it home.

**[0:25–0:55 — chorus]**  
You are not your alarm —  
you’re the one who hears the ring.  
Static in the ears ain’t a character flaw;  
it’s a body doing its thing.  
Hold the seam — sensation, then story —  
don’t marry the first loud thought.  
One breath where the heat begins.  
That’s the whole damn plot.

**[0:55–1:20]**  
Social room or love on read —  
same old coil behind the ribs.  
Name the heat. Skip the shame.  
Borrow this steadier rhythm.

**[1:20–1:30 — tag / CTA hook line]**  
Not your alarm. Just a signal.  
Save this if you need it tonight.

---

## 5. Japanese-native lyrics (not literal EN→JA translation)

These are **native rewrites** in Pearl Prime’s therapeutic register for ja-JP listeners: polite-but-intimate, body-first, non-shaming. They share the *mechanism* (alarm ≠ self; sensation before story) but use different images, cadence, and social texture than the English pieces.

### 5.1 五分・日本語詞 — 「警報の人ではない」

**形式:** 歌い出し → Aメロ → サビ → Aメロ → サビ → ブリッジ → サビ  
**テンポ感:** ゆっくりめ、落ち着きへ向かう（おおよそ 66–74 BPM）

**[歌い出し]**  
送信した。届いた、はずなのに。  
指がもう、画面に戻っている。

**[Aメロ1]**  
胸が部屋より先に鳴る。  
四分か、一年か、わからない。  
かつて守ってくれた見張りが、  
今夜も同じスイッチを押す。

あごに力。耳のざわめき。  
危険は外か、物語か。  
体はまだ、区別が苦手で、  
あなたを責めないでほしい。

**[サビ]**  
あなたは警報じゃない。  
警報を聞いている人だ。  
ざわめきは天気予報でいい。  
人格の判決じゃなくていい。  
熱の名前を、先に呼んで。  
物語は、半歩あとに。  
そのすきまに、息をひとつ。  
あなたは警報じゃない。

**[Aメロ2]**  
社交の部屋で出口を数えても、  
既読のままの糸を握っても、  
肋骨の奥のスキャナーは同じ。  
恥じゃなく、信号として迎えて。

感覚が先。物語はあと。  
二つは、ひとつに見えて別物。  
今夜は直さなくていい。  
ただ、縫い目に手を添えて。

**[サビ]**  
あなたは警報じゃない。  
警報を聞いている人だ。  
ざわめきは天気予報でいい。  
人格の判決じゃなくていい。  
熱の名前を、先に呼んで。  
物語は、半歩あとに。  
そのすきまに、息をひとつ。  
あなたは警報じゃない。

**[ブリッジ]**  
返信がなくても、世界は進んだ。  
あなたは、まだここにいる。  
完璧じゃなくていい。終わりじゃなくていい。  
小さな証拠を、体に渡すだけ。

**[サビ・最後は弱く、それから定常に]**  
あなたは警報じゃない。  
警報を聞いている人だ。  
信号に会って、恥は置いて。  
今夜は、少し遅い拍で。  
熱の名前を、先に呼んで。  
物語は、半歩あとに。  
そのすきまに、息をひとつ。  
あなたは警報じゃない。

---

### 5.2 九〇秒・日本語（Shorts / TikTok）— 「冒頭三秒」

**[0:00–0:03 — スクロール止め]**  
**胸の音が、部屋より大きい。**

**[0:03–0:30]**  
送った。届いた。なのに指が戻る。  
四分。既読なし。見張りが「帰れ」と言う。

**[0:30–1:00 — サビ]**  
あなたは警報じゃない。  
聞いている側の人だ。  
耳のざわめきは欠陥じゃない。  
体が、昔のやり方で守っている。  
熱を先に呼ぶ。物語はあと。  
そのすきまに、息をひとつ。

**[1:00–1:30]**  
人の目でも、恋の既読でも、  
肋骨の奥は同じスキャナー。  
今夜は直さない。拍を落とす。  
必要なら、保存してまた来て。

---

## 6. No-lyrics performance briefs (text direction only)

V1 = **text direction only**. No MusicGen WAV claim. No audio file ships with this packet.

### 6.1 Five-minute no-lyrics brief  
*(crystal bowls / light-language / “la-la-la” / ambient instrumental)*

**Intent:** begin taut; resolve toward calm; downward contour; no jump-scares; ~66–78 BPM settling lower.

**Arc (timed):**

| Time | Sonic job | Emotional job |
|---|---|---|
| 0:00–0:45 | Thin high shimmer or soft metallic edge; sparse strikes; slight dissonant interval | “Static in the ears” / scanner on |
| 0:45–2:00 | Introduce a slow pulse (bowl wash, heartbeat-low drone, or palm-muted pulse) under the shimmer | Body finds a floor without being told to relax |
| 2:00–3:30 | Widen the stereo gently; open vowels / light-language syllables on long tones (`la`, `ah`, `mm`) — no lexical lyric | Companion presence; second-person care without words |
| 3:30–4:30 | Resolve dissonance by small degrees; drop 2–4 BPM; remove the sharpest overtones | Alarm as weather, not verdict |
| 4:30–5:00 | Leave one warm fundamental + breath-length decay; end without a triumphant cadence | “Still here” — unfinished, unashamed |

**Do / Don’t:**

- Do: let silence be a bar; let decay finish.
- Don’t: sudden risers, horror stingers, “epic win” final major smash.
- Light-language: keep syllables soft, repetitive, non-semantic; treat them as nervous-system pacing, not message delivery.

### 6.2 Ninety-second no-lyrics brief (Shorts / TikTok)

**0:00–0:03 (scroll-stop, visual + sonic):** hard cut to face or hands on instrument + **one close, slightly sharp bowl edge or inhale** — then immediately soften. Caption option: `Your chest is louder than the room.` / `胸の音が、部屋より大きい。`

| Time | Direction |
|---|---|
| 0:03–0:25 | Taut shimmer + slow pulse enters |
| 0:25–0:55 | Open vowel / la-la bed; downward contour begins |
| 0:55–1:20 | Remove edge tones; BPM feels slower; warm fundamental |
| 1:20–1:30 | Single decay into quiet; on-screen CTA (see §8) |

---

## 7. Fit to existing melody (musician note)

- Lyrics are **original** and **flexible**: swap “phone / Slack / read receipt” for your scene (stage fright lobby, DM thread, family group chat) without breaking the chorus thesis.
- Keep lines **short and singable**; folk/rock stress pattern (mostly 3–4 stresses per line).
- **Do not** map these words onto a copyrighted melody you do not control. Write or use an original chord bed (Am–F–C–G / Em–C–G–D families work; any simple diatonic loop is fine).
- Chorus thesis that must survive melody changes: **alarm ≠ identity**; **sensation before story**; **de-escalate, don’t triumph**.
- Japanese pieces are native cadence — do not force EN syllable counts onto JA lines.

---

## 8. CTA / freebie recommendation (M1–M5 only)

Reuse existing music-mode freebie template IDs only (`funnel/music_mode/templates/m1..m5` via `config/music/youtube_freebie_bridge.yaml` contract). **No new freebie types.**

**Default pairing for this family pilot:**

| Role | `template_id` | Template file | Why |
|---|---|---|---|
| Primary | `companion_track_download_v1` | `m1_companion_song_download.yaml` | Listener who felt the alarm→seam thesis wants the full companion track after the hook |
| Secondary / Shorts | `preview_clip_30s_v1` | `m2_30s_preview_clip.yaml` | Matches 90s social cut; email-gate before longer listen |

**Allowed IDs (do not invent outside this set):**  
`companion_track_download_v1` · `preview_clip_30s_v1` · `sample_ep_bundle_v1` · `lyric_poster_pdf_v1` · `behind_the_song_interview_v1`

**Suggested pinned-comment / description pattern (copy only; no YT API in this lane):**  
“If your chest got loud while this played — grab the companion track + 30s preview (email gate). You’re not broken; you’re hearing an alarm.”

Optional later (not default): `lyric_poster_pdf_v1` for the chorus line *You are not your alarm.*

---

## 9. Self-audit checklist

| Requirement | Status |
|---|---|
| Why-family covers anxiety + social + relationship without persona branching | PASS (§1) |
| Pearl Prime vibe: somatic, recognition, reframe, second-person, non-shaming | PASS (§2) |
| Original EN 5-min lyric | PASS (§4.1) |
| Original EN 90s lyric with genuine first-3s scroll-stop | PASS (§4.2 cold open) |
| Original JA 5-min native (not literal translation) | PASS (§5.1 — different images/cadence) |
| Original JA 90s native | PASS (§5.2) |
| 5-min no-lyrics performance brief | PASS (§6.1) |
| 90s no-lyrics Shorts brief | PASS (§6.2) |
| CTA uses only M1–M5; default M1+M2 | PASS (§8) |
| Melody-fit note; no copyrighted-tune dependency | PASS (§7) |
| Provenance appendix | PASS (§10) |
| One family only; no generator/MusicGen/YouTube wiring | PASS |
| Execution-fabric docs absent on origin/main — stated | PASS (§3) |

---

## 10. Provenance appendix

| Source | What it informed |
|---|---|
| `config/music/song_kit_topic_families.yaml` → `anxiety_and_overwhelm` | Family anchors, themes (“static in the ears”, “you are not your alarm”), lyric/instrumental hints |
| `config/music/youtube_freebie_bridge.yaml` + `funnel/music_mode/templates/m1..m5` | CTA template_id reuse only |
| `docs/specs/MUSIC_ONBOARDING_SONG_KIT_V1_SPEC.md` | Manual kit posture; 8-family SSOT; no-lyrics = text only in V1 |
| `docs/specs/MUSIC_MODE_V2_PRODUCTION_READINESS_SPEC.md` | V2 priority cell cluster / production-readiness context |
| `docs/specs/MUSIC_MODE_FREEBIE_FUNNEL_V1_SPEC.md` | Freebie funnel boundaries |
| `artifacts/musician_survey/SURVEY_TEMPLATE.yaml` | with-lyrics / no-lyrics fork awareness |
| `artifacts/programs/music_mode_v2_20260611/MUSIC_MODE_INTRODUCTION_LONG_FORM.md` | Musician-facing framing; second-person; companion song |
| `artifacts/qa/snapshots/CANONICAL_FLAGSHIP_CH1.txt` | Alarm-as-protection; sensation vs story; Priya/send-button recognition; non-shaming close |
| `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` | Orient/Name craft; therapeutic (not slogan) register; SCENE second-person care |
| `SOURCE_OF_TRUTH/musician_banks/test_artist_alpha/approved_atoms/LYRIC_OPENING/lo_01.yaml` | Lyric atom brevity / soft naming pattern |
| `SOURCE_OF_TRUTH/teacher_banks/ahjan/approved_atoms/HOOK|COMPRESSION` (sample) | Doctrine-adjacent tone; ordinary-life path; wound-as-doorway compression (register only) |
| `config/source_of_truth/canonical_topics.yaml` | Confirmed anchors are existing topic_ids |
| `config/music/music_brand_registry.yaml` | Music-mode brand archetype awareness (no new brand minted here) |

**Research posture:** internal Pearl Prime corpus + live repo truth only. No external Japanese lyric research lane required for this pilot (native rewrite grounded in locale register notes + therapeutic doctrine already in-repo).

---

## 11. Next smallest wave

Author the **next one family only** (recommended candidate after operator review: `presence_and_stillness` or `recovery_and_repair`) as a sibling packet — still manual, still not the generator build.
